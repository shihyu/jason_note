package mq

import (
	"context"
	"time"
)

type InMemoryConsumer struct {
	messagesCh chan ConsumedMessage
}

func NewInMemoryConsumer(bufferSize int) *InMemoryConsumer {
	return &InMemoryConsumer{
		messagesCh: make(chan ConsumedMessage, bufferSize),
	}
}

func (m InMemoryConsumer) ReadMessage(ctx context.Context, readTimeout time.Duration) (ConsumedMessage, error) {
	select {
	case msg := <-m.messagesCh:
		return msg, nil
	case <-time.After(readTimeout):
		return nil, ErrSubscriberCloseTimeout
	}
}
func (m InMemoryConsumer) CommitAndClose(timeout time.Duration) error {
	return nil
}

func (m *InMemoryConsumer) Publish(ctx context.Context, message ...*ProducedMessage) []ProducedMessageResult {
	results := make([]ProducedMessageResult, len(message))
	for i, msg := range message {
		inMemMsg := InMemoryConsumedMessage{msg: *msg}
		m.messagesCh <- inMemMsg
		results[i] = ProducedMessageResult{
			Topic: msg.Topic,
		}
	}
	return results
}

func NewInMemoryConsumedMessage(key, message []byte) *InMemoryConsumedMessage {
	return &InMemoryConsumedMessage{
		msg: ProducedMessage{
			Key:     key,
			Message: message,
		},
	}
}

type InMemoryConsumedMessage struct {
	msg ProducedMessage
}

func (m InMemoryConsumedMessage) Context() context.Context {
	return context.Background()
}
func (m InMemoryConsumedMessage) SetContext(ctx context.Context) {
	// No-op for in-memory message
}
func (m InMemoryConsumedMessage) GetPayload() []byte {
	return m.msg.Message
}
func (m InMemoryConsumedMessage) GetKey() []byte {
	return m.msg.Key
}
func (m InMemoryConsumedMessage) Commit() error {
	return nil
}

func (m InMemoryConsumedMessage) Store() error {
	return nil
}
func (m InMemoryConsumedMessage) GetTopic() string {
	return m.msg.Topic
}
func (m InMemoryConsumedMessage) GetPartition() int32 {
	if m.msg.Partition != nil {
		return *m.msg.Partition
	}
	return 0
}
func (m InMemoryConsumedMessage) GetOffset() int64 {
	return 1
}

func (m InMemoryConsumedMessage) GetHeader(key string) []byte {
	if m.msg.Header == nil {
		return nil
	}
	return m.msg.Header[key]
}

func (m InMemoryConsumedMessage) GetMessageDelayCount() (int64, error) {
	return 0, nil
}
