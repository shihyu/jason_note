package mq

import (
	"context"
	"time"

	"github.com/vx416/axs/pkg/logger"
)

// ConsumerReader message queue consumer reader
type ConsumerReader interface {
	// ReadMessage read a message from message queue, this method will block until a message is received or timeout
	ReadMessage(ctx context.Context, readTimeout time.Duration) (ConsumedMessage, error)
	// CommitAndClose commit all messages and close consumer reader
	CommitAndClose(timeout time.Duration) error
}

// ConsumedMessage message consumed from message queue
type ConsumedMessage interface {
	Context() context.Context
	SetContext(ctx context.Context)
	GetPayload() []byte
	GetKey() []byte
	Commit() error
	Store() error
	GetTopic() string
	GetPartition() int32
	GetOffset() int64
	GetHeader(key string) []byte
	GetMessageDelayCount() (int64, error)
}

// Publisher message queue publisher
type Producer interface {
	// FlushAndClose flush all messages in buffer and close publisher
	//  return the number of messages flushed, and error
	FlushAndClose(to time.Duration) (int, error)
	// Publish publish a batch of messages to kafka, this method will block until all messages are sent
	Publish(ctx context.Context, message ...*ProducedMessage) []ProducedMessageResult
	// AsyncPublish publish a batch of messages to kafka asynchronously
	AsyncPublish(ctx context.Context, message ...*ProducedMessage) []ProducedMessageResult
	// Flush flush all messages in buffer
	//  return the number of messages flushed, and error
	Flush(to time.Duration) (int, error)
}

// ProducedMessage message to be produced to message queue
type ProducedMessage struct {
	// Key partition key, if nil, will use round-robin partitioner
	Key     []byte
	Message []byte
	Topic   string
	Header  map[string][]byte
	// Partition specify partition to send message to, if nil, will use round-robin partitioner
	Partition *int32
}

// ProducedMessageResult result of produced message
type ProducedMessageResult struct {
	Topic     string
	Partition int32
	Offset    int64
	Error     error
}

// LogWithMessage return a logger context with message info
func LogWithMessage(ctx context.Context, msg ConsumedMessage) context.Context {
	return logger.GetLogger(ctx).With().
		Str("topic", msg.GetTopic()).
		Int32("partition", msg.GetPartition()).
		Int64("offset", msg.GetOffset()).Logger().WithContext(ctx)
}
