package kafka

import (
	"context"
	"fmt"
	"time"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"
	"github.com/vx416/axs/pkg/mq"
)

type ConfluentPublisher struct {
	pub *ckafka.Producer
}

// Publish publish a batch of messages to kafka, this method will block until all messages are sent
//
//	please notice that if confluent lib's environment variable `delivery.report.only.error` is true, the producer will only deliver message when error occurs so that synchronous publish will be blocked.
func (p *ConfluentPublisher) Publish(ctx context.Context, message ...*mq.ProducedMessage) []mq.ProducedMessageResult {
	results := make([]mq.ProducedMessageResult, len(message))
	waitCh := make([]chan ckafka.Event, len(message))
	for i, msg := range message {
		waitCh[i] = make(chan ckafka.Event, 1)
		ckMsg := p.makeConfluentMsg(msg.Topic, msg)
		err := p.pub.Produce(ckMsg, waitCh[i])
		if err != nil {
			results[i] = mq.ProducedMessageResult{
				Topic:     msg.Topic,
				Partition: -1,
				Offset:    -1,
				Error:     err,
			}
		}
	}
	for i, ch := range waitCh {
		if results[i].Error == nil {
			select {
			case event := <-ch:
				if event != nil {
					switch ev := event.(type) {
					case *kafka.Message:
						m := ev
						if m.TopicPartition.Error != nil {
							topic := ""
							if m.TopicPartition.Topic != nil {
								topic = *m.TopicPartition.Topic
							}
							results[i].Error = fmt.Errorf("publish topic %s failed, err:%+v", topic, m.TopicPartition.Error)
						} else {
							if ev.TopicPartition.Topic != nil {
								results[i].Topic = *ev.TopicPartition.Topic
							}
							results[i].Partition = ev.TopicPartition.Partition
							results[i].Offset = int64(ev.TopicPartition.Offset)
						}
					case kafka.Error:
						results[i].Error = fmt.Errorf("publish failed, err:%+v", ev)
					}
				}
			case <-ctx.Done():
				results[i].Error = fmt.Errorf("publish messages failed, context timeout, err:%+v", ctx.Err())
			}
		}
	}
	return results
}

// AsyncPublishWithPayloads asynchronous publish a batch of messages to kafka, this method will not block
func (p *ConfluentPublisher) AsyncPublish(ctx context.Context, message ...*mq.ProducedMessage) []mq.ProducedMessageResult {
	results := make([]mq.ProducedMessageResult, len(message))
	for i, msg := range message {
		ckMsg := p.makeConfluentMsg(msg.Topic, msg)
		err := p.pub.Produce(ckMsg, nil)
		if err != nil {
			results[i] = mq.ProducedMessageResult{
				Topic:     msg.Topic,
				Partition: -1,
				Offset:    -1,
				Error:     err,
			}
		} else {
			results[i] = mq.ProducedMessageResult{
				Topic:     msg.Topic,
				Partition: ckMsg.TopicPartition.Partition,
				Offset:    -1,
				Error:     nil,
			}
		}
	}
	return results
}

// Flush flush all messages in buffer
//
//	return the number of messages remaining, and error
func (p *ConfluentPublisher) Flush(to time.Duration) (int, error) {
	remaining := p.pub.Flush(int(to / time.Millisecond))
	return remaining, nil
}

// FlushAndClose flush all messages in buffer and close publisher
//
//	return the number of messages flushed, and error
func (p *ConfluentPublisher) FlushAndClose(to time.Duration) (int, error) {
	remaining := p.pub.Flush(int(to / time.Millisecond))
	p.pub.Close()
	return remaining, nil
}

func (p *ConfluentPublisher) makeConfluentMsg(topic string, msg *mq.ProducedMessage) *ckafka.Message {
	partition := ckafka.PartitionAny
	if msg.Partition != nil {
		partition = *msg.Partition
	}
	headers := []ckafka.Header{}
	for k, v := range msg.Header {
		headers = append(headers, ckafka.Header{Key: k, Value: v})
	}
	return &ckafka.Message{
		TopicPartition: ckafka.TopicPartition{
			Topic:     &topic,
			Partition: partition,
		},
		Value:   msg.Message,
		Key:     msg.Key,
		Headers: headers,
	}
}
