package kafka

import (
	"context"
	"strings"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/pkg/errors"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/mq"
)

// ProducerAck producer acknowledgement level
type ProducerAck int

const (
	// NonAck no waiting for ack
	NonAck ProducerAck = 0
	// Leader waiting for leader ack
	Leader ProducerAck = 1
	// All waiting for leader and replicas
	All ProducerAck = -1
)

// PartitionerStrategy kafka producer sharding partitioner strategy
type PartitionerStrategy string

const (
	// RandomPartitioner random partitioner
	RandomPartitioner PartitionerStrategy = "random"
	// ConsistentPartitioner crc32 hash (Empty and NULL keys are mapped to single partition)
	ConsistentPartitioner PartitionerStrategy = "consistent"
	// ConsistentRandomPartitioner crc32 hash (Empty and NULL keys are mapped to random partition)
	ConsistentRandomPartitioner PartitionerStrategy = "consistent_random"
	// Murmur2Partitioner murmur2 hash
	Murmur2Partitioner PartitionerStrategy = "murmur2"
	// Murmur2RandomPartitioner murmur2 hash (Empty and NULL keys are mapped to random partition)
	Murmur2RandomPartitioner PartitionerStrategy = "murmur2_random"
	// FNV1APartitioner fnv1a hash
	FNV1APartitioner PartitionerStrategy = "fnv1a"
	// FNV1ARandomPartitioner fnv1a hash (Empty and NULL keys are mapped to random partition)
	FNV1ARandomPartitioner PartitionerStrategy = "fnv1a_random"
)

// CompressionType kafka message compression type
type CompressionType string

const (
	NoCompression CompressionType = "none"
	Gzip          CompressionType = "gzip"
	Snappy        CompressionType = "snappy"
	Lz4           CompressionType = "lz4"
	Zstd          CompressionType = "zstd"
)

// ProducerConfig kafka producer config
//
// https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
// https://www.linkedin.com/pulse/kafka-action-part-3-producers-advanced-real-life-example-kulkarni/
type ProducerConfig struct {
	Brokers []string
	// A user-provided string sent with every request to the brokers for logging,
	// debugging, and auditing purposes. Defaults to "sarama", but you should
	// probably set it to something specific to your application.
	ClientID string
	// A rack identifier for this client. This can be any string value which
	// indicates where this client is physically located.
	// It corresponds with the broker config 'broker.rack'
	RackID *string

	// TopicMetadataRefreshIntervalMs is the interval in milliseconds to refresh the topic metadata.
	//  default: 300000
	//  this value will effect consumer or producer use new topic partition when topic partition increase. If topic increase partition, producer and consumer should refresh metadata to get new partition based on this interval,
	//  so make sure producer's refresh interval ms should be greater or equal than consumer's refresh interval ms
	//  topic.metadata.refresh.interval.ms
	TopicMetadataRefreshIntervalMs *int

	// EnableIDempotence if enabled, the producer will ensure that exactly one copy of each message is written in the stream.
	// see more details:
	// https://medium.com/@gaddamnaveen192/kafka-idempotent-producer-the-hidden-secret-to-stop-duplicate-messages-2c49f931976e
	EnableIDempotence *bool
	// Acks default use leader
	Acks *ProducerAck

	// The ack timeout of the producer request in milliseconds. This value is only enforced by the broker and relies on request.required.acks being > 0. (Leader or All)
	// default: 300000
	MessageTimeoutMs *int

	// Partitioner producer partitioner strategy, default consistent
	Partitioner *PartitionerStrategy

	// producer message compression type, default snappy
	// https://medium.com/@prasanta.mohanty/bench-marking-standards-for-kafka-compression-9d9a46d22ce0
	CompressionType *CompressionType

	// The maximum number of messages batched in one MessageSet. The total MessageSet size is also limited by message.max.bytes.
	//  default 1000000
	BatchSize *int

	// Delay in milliseconds to wait for messages in the producer queue to accumulate before constructing message batches (MessageSets) to transmit to brokers. A higher value allows larger and more effective (less overhead, improved compression) batches of messages to accumulate at the expense of increased message delivery latency.
	//  default 5
	LingerMs *int

	// How many times to retry sending a failing Message. Note: retrying may cause reordering unless enable.idempotence is set to true.
	// default 2147483647
	Retries *int
}

// GetConfluentProducer creates a new Kafka Producer.
func (cfg ProducerConfig) GetConfluentProducer(eventMonitorFunc func(event ckafka.Event)) (mq.Producer, error) {
	cKafkaCfg := &ckafka.ConfigMap{}
	cKafkaCfg.SetKey("bootstrap.servers", strings.Join(cfg.Brokers, ","))
	cKafkaCfg.SetKey("client.id", cfg.ClientID)

	if cfg.EnableIDempotence != nil {
		cKafkaCfg.SetKey("enable.idempotence", *cfg.EnableIDempotence)
	}
	if cfg.Acks != nil {
		cKafkaCfg.SetKey("acks", int(*cfg.Acks))
	}
	if cfg.MessageTimeoutMs != nil {
		cKafkaCfg.SetKey("message.timeout.ms", *cfg.MessageTimeoutMs)
	}
	if cfg.Partitioner != nil {
		cKafkaCfg.SetKey("partitioner", string(*cfg.Partitioner))
	}
	if cfg.CompressionType == nil {
		cKafkaCfg.SetKey("compression.type", "snappy")
	}
	if cfg.CompressionType != nil {
		cKafkaCfg.SetKey("compression.type", string(*cfg.CompressionType))
	}
	if cfg.BatchSize == nil {
		cKafkaCfg.SetKey("batch.size", 100)
	}
	if cfg.BatchSize != nil {
		cKafkaCfg.SetKey("batch.size", *cfg.BatchSize)
	}
	if cfg.LingerMs != nil {
		cKafkaCfg.SetKey("linger.ms", *cfg.LingerMs)
	}
	if cfg.Retries != nil {
		cKafkaCfg.SetKey("retries", *cfg.Retries)
	}
	if cfg.TopicMetadataRefreshIntervalMs != nil {
		cKafkaCfg.SetKey("topic.metadata.refresh.interval.ms", *cfg.TopicMetadataRefreshIntervalMs)
	}
	cKafkaCfg.SetKey("delivery.report.only.error", false)
	cKafkaCfg.SetKey("go.logs.channel.enable", true)
	producer, err := ckafka.NewProducer(cKafkaCfg)
	if err != nil {
		return nil, errors.WithMessage(err, "create producer error")
	}
	logger.SafeGo(func() {
		for log := range producer.Logs() {
			if log.Level >= 3 {
				logger.GetLogger(context.Background()).Warn().Msgf("kafka producer log: %s", log.String())
			} else {
				logger.GetLogger(context.Background()).Info().Msgf("kafka producer log: %s", log.String())
			}
		}
	})
	return NewConfluentPublisherWithClient(producer, eventMonitorFunc)
}

// NewConfluentPublisherWithClient creates a new Kafka Publisher.
//
//	please notice that if `delivery.report.only.error` is true, the producer will only deliver message when error occurs so that synchronous publish (Publish method) will be blocked.
func NewConfluentPublisherWithClient(pub *ckafka.Producer, eventMonitorFunc func(event ckafka.Event)) (*ConfluentPublisher, error) {
	var eventMonitorJob func(kProducer *ckafka.Producer)
	eventMonitorJob = func(kProducer *ckafka.Producer) {
		defer func() {
			// for handle panic recover background
			// FYI: https://go.dev/play/p/lMnMchsiXmm
			if panicError := recover(); panicError != nil {
				// log.Errorf("confluent_publisher event monitor has panicked, recovered it! error: %v", panicError)
				go eventMonitorJob(kProducer)
			}
			// log.Info("confluent_publisher event monitor closed")
		}()
		for e := range pub.Events() {
			if kProducer.IsClosed() {
				return
			}
			switch ev := e.(type) {
			case *kafka.Message:
				if eventMonitorFunc != nil {
					eventMonitorFunc(ev)
				}
			}
		}
	}
	go eventMonitorJob(pub)
	return &ConfluentPublisher{
		pub: pub,
	}, nil
}
