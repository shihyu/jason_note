package kafka

import (
	"context"

	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

func NewKafkaConsumedMessage(ctx context.Context, msg *ckafka.Message, consumer *ckafka.Consumer) *KafkaConsumedMsg {
	header := make(map[string][]byte)
	for _, h := range msg.Headers {
		header[h.Key] = h.Value
	}
	return &KafkaConsumedMsg{
		ctx:      ctx,
		kafkaMsg: msg,
		consumer: consumer,
		header:   header,
	}
}

type KafkaConsumedMsg struct {
	ctx      context.Context
	kafkaMsg *ckafka.Message
	consumer *ckafka.Consumer
	header   map[string][]byte
}

func (k *KafkaConsumedMsg) Context() context.Context {
	return k.ctx
}

func (k *KafkaConsumedMsg) SetContext(ctx context.Context) {
	k.ctx = ctx
}

func (k *KafkaConsumedMsg) GetPayload() []byte {
	return k.kafkaMsg.Value
}

func (k *KafkaConsumedMsg) Commit() error {
	_, err := k.consumer.CommitMessage(k.kafkaMsg)
	return err
}

func (k *KafkaConsumedMsg) Store() error {
	_, err := k.consumer.StoreMessage(k.kafkaMsg)
	return err
}

func (k *KafkaConsumedMsg) GetTopic() string {
	if k.kafkaMsg.TopicPartition.Topic != nil {
		return *k.kafkaMsg.TopicPartition.Topic
	}
	return ""
}
func (k *KafkaConsumedMsg) GetPartition() int32 {
	return k.kafkaMsg.TopicPartition.Partition
}
func (k *KafkaConsumedMsg) GetOffset() int64 {
	return int64(k.kafkaMsg.TopicPartition.Offset)
}
func (k *KafkaConsumedMsg) GetHeader(key string) []byte {
	return k.header[key]
}

func (k *KafkaConsumedMsg) GetKey() []byte {
	return k.kafkaMsg.Key
}

func (k *KafkaConsumedMsg) GetMessageDelayCount() (int64, error) {
	_, high, err := k.consumer.GetWatermarkOffsets(k.GetTopic(), k.GetPartition())
	if err != nil {
		return 0, err
	}

	return high - k.GetOffset(), nil
}
