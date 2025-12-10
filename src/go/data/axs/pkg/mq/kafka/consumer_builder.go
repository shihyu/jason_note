package kafka

import (
	"context"
	"time"

	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/pkg/errors"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/mq"
)

// ConfluentConsumerBuilder kafka consumer builder
type ConfluentConsumerBuilder struct {
	cfg *ckafka.ConfigMap
}

// TopicPartition topic and partition
type TopicPartition struct {
	Topic     string
	Partition int32
	Offset    Offset
}

type Offset int64

var (
	Beginning Offset = -2
	End       Offset = -1
	Invalid   Offset = -1001
	Stored    Offset = -1000
)

// BuildPartitionConsumer builds a partition consumer by assigning the given topic partitions.
func (s *ConfluentConsumerBuilder) BuildPartitionConsumer(ctx context.Context, consumerGroupName string, topicsPartitions ...TopicPartition) (mq.ConsumerReader, error) {
	consumer, err := s.getConsumerClient(consumerGroupName)
	if err != nil {
		return nil, errors.WithMessage(err, "init consumer failed")
	}
	var partitions = make([]ckafka.TopicPartition, 0, len(topicsPartitions))
	for i := range topicsPartitions {
		tp := topicsPartitions[i]

		low, high, err := consumer.QueryWatermarkOffsets(tp.Topic, tp.Partition, 5000)
		if err != nil {
			return nil, errors.WithMessage(err, "query watermark offsets failed")
		}

		switch tp.Offset {
		case Beginning, End, Invalid, Stored:
		default:
			if tp.Offset < Offset(low) {
				tp.Offset = Offset(low)
			} else if tp.Offset > Offset(high) {
				tp.Offset = Offset(high)
			}
		}

		partitions = append(partitions, ckafka.TopicPartition{
			Topic:     &tp.Topic,
			Partition: tp.Partition,
			Offset:    ckafka.Offset(tp.Offset),
		})
	}
	err = consumer.Assign(partitions)
	if err != nil {
		return nil, errors.WithMessage(err, "assign partitions failed")
	}

	cfg := s.cloneCfg()
	val, err := cfg.Get("max.poll.interval.ms", ckafka.ConfigValue(10000))
	if err != nil {
		return nil, errors.WithMessage(err, "get max.poll.interval.ms failed")
	}
	maxPollMax, ok := val.(int)
	if !ok || maxPollMax <= 0 {
		maxPollMax = 10000
	}

	logger.SafeGo(func() {
		for log := range consumer.Logs() {
			if log.Level >= 3 {
				logger.GetLogger(context.Background()).Warn().Msgf("kafka consumer log: %s", log.String())
			} else {
				logger.GetLogger(context.Background()).Info().Msgf("kafka consumer log: %s", log.String())
			}
		}
	})
	return &consumerReader{
		maxPollIntervalTime: time.Duration(maxPollMax) * time.Millisecond,
		consumerGroupName:   consumerGroupName,
		consumer:            consumer,
		rebuild: func(consumer *ckafka.Consumer) (*ckafka.Consumer, error) {
			err := consumer.Assign(partitions)
			if err != nil {
				return consumer, err
			}
			return consumer, nil
		},
	}, nil
}

func (s *ConfluentConsumerBuilder) cloneCfg() *ckafka.ConfigMap {
	m2 := make(ckafka.ConfigMap)
	for k, v := range *s.cfg {
		m2[k] = v
	}
	return &m2
}

func (s *ConfluentConsumerBuilder) getConsumerClient(consumerGroup string) (*ckafka.Consumer, error) {
	m2 := s.cloneCfg()
	m2.SetKey("group.id", consumerGroup)
	m2.SetKey("go.logs.channel.enable", true)
	consumer, err := ckafka.NewConsumer(m2)
	if err != nil {
		return nil, err
	}

	return consumer, nil
}
