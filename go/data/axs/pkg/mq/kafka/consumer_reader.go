package kafka

import (
	"context"
	"fmt"
	"sync"
	"time"

	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"

	"github.com/vx416/axs/pkg/mq"
)

type consumerReader struct {
	consumerGroupName   string
	consumer            *ckafka.Consumer
	maxPollIntervalTime time.Duration
	rebuild             func(consumer *ckafka.Consumer) (*ckafka.Consumer, error)
	isClosed            bool
	closedLock          sync.Mutex
}

// GetConsumerGroupName get consumer group name
func (s *consumerReader) GetConsumerGroupName() string {
	return s.consumerGroupName
}

// ReadMessage read message from kafka, if timeout <= 0, will use 3 sec
//
//	if timeout >= maxPollIntervalTime, will use maxPollIntervalTime/5
func (s *consumerReader) ReadMessage(ctx context.Context, readTimeout time.Duration) (mq.ConsumedMessage, error) {
	if readTimeout <= 0 {
		readTimeout = s.maxPollIntervalTime / 5
	}
	if readTimeout <= 0 {
		// readTimeout = 3 * time.Second
	}
	if s.maxPollIntervalTime > 0 && readTimeout > s.maxPollIntervalTime {
		readTimeout = s.maxPollIntervalTime / 5
	}
	//
Retry:
	//
	kafkaMsg, err := s.consumer.ReadMessage(readTimeout)
	if err != nil {
		if ckafkaErr, ok := err.(ckafka.Error); ok {
			switch ckafkaErr.Code() {

			case ckafka.ErrTimedOut:
				return nil, mq.ErrSubscriberTimeout
			case ckafka.ErrMaxPollExceeded:
				newConsumer, err := s.rebuild(s.consumer)
				if err != nil {
					return nil, err
				} else {
					s.consumer = newConsumer
				}
				goto Retry
			case ckafka.ErrTransport:
				time.Sleep(300 * time.Millisecond)
				goto Retry
			}
		}
		return nil, err
	}
	msg := NewKafkaConsumedMessage(ctx, kafkaMsg, s.consumer)
	return msg, nil
}

// CommitAndClose commit offsets and close consumer
func (s *consumerReader) CommitAndClose(timeout time.Duration) error {
	s.closedLock.Lock()
	defer s.closedLock.Unlock()
	if s.isClosed {
		return nil
	}
	s.isClosed = true
	_, committedErr := s.consumer.Commit()
	closeErr := s.consumer.Close()
	if committedErr != nil || closeErr != nil {
		return fmt.Errorf("commit error: %v, close error: %v", committedErr, closeErr)
	}
	return nil
}
