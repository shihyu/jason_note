package kafka

import (
	"errors"
	"strings"

	ckafka "github.com/confluentinc/confluent-kafka-go/v2/kafka"
)

// config errors
var (
	ErrRequireBrokers       error = errors.New("require brokers")
	ErrRequireConsumerGroup error = errors.New("require consumer group")
)

// InitOffsetMode consumer group
type InitOffsetMode int

// earliest, latest, none
const (
	// None 如果 consumer group 在 partition 有 commit offset，則從 commit offset 開始消費；如果沒有 commit offset，則拋出異常
	NoneOffsetMode InitOffsetMode = -3
	// Earliest 如果 consumer group 在 partition 有 commit offset，則從 commit offset 開始消費；如果沒有 commit offset，則從 partition 最早的 offset 開始消費
	EarliestOffsetMode InitOffsetMode = -2
	// Latest 如果 consumer group 在 partition 有 commit offset，則從 commit offset 開始消費；如果沒有 commit offset，則從 partition 最新的 offset 開始消費
	LatestOffsetMode InitOffsetMode = -1
)

func (mode InitOffsetMode) String() string {
	switch mode {
	case NoneOffsetMode:
		return "none"
	case EarliestOffsetMode:
		return "earliest"
	case LatestOffsetMode:
		return "latest"
	default:
		return "latest"
	}
}

func NewDefaultConsumerConfig(brokers []string, clientID string) ConsumerConfig {
	return ConsumerConfig{
		Brokers:  brokers,
		ClientID: clientID,
	}
}

// https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
type ConsumerConfig struct {
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
	//  NOTE: if you want to use new partition immediately after topic partition increase, you can set this value to smaller value, but it may cause more load on broker, and ensure your producer's refresh interval ms >= consumer's refresh interval ms
	TopicMetadataRefreshIntervalMs *int

	// InitOffsetMode is used to specify from where to start consuming messages.
	//  default: earliest
	InitOffsetMode *InitOffsetMode

	//  ConsumerGroupSessionTimeoutMs is the timeout used to detect consumer failures when using Kafka's group management facility.
	// default: 10000 which is min value,
	ConsumerGroupSessionTimeoutMs *int
	// ConsumerGroupHeartbeatMs is the expected time between heartbeats to the consumer coordinator when using Kafka's group management facilities. this value should < ConsumerGroupSessionTimeoutMs
	// default: 3000
	ConsumerGroupHeartbeatMs *int

	// Consumer Polling Config
	// MaxPollIntervalMs is the maximum allowed time between calls to consume messages (e.g., rd_kafka_consumer_poll()) for high-level consumers.
	//    NOTE: if consumer not call poll in this time, the consumer will be marked as failed and leave the group, then controller will rebalance in order to reassign the partitions to another consumer group member.
	// default: 300000
	MaxPollIntervalMs *int
	// FetchMaxBytes MaxPartitionFetchBytes is the maximum amount of data per-partition the server will return.
	// default: 1048576 1mb
	FetchMaxBytes *int
	// FetchMinBytes is the minimum amount of data the server should return for a fetch request, otherwise it will wait.
	// default: 5kb
	FetchMinBytes *int
	// FetchMaxWaitMs is the maximum amount of time the server will block before answering the fetch request if there isn't sufficient data to immediately satisfy the requirement given by fetch.min.bytes.
	// default: 500
	FetchWaitMaxMs *int

	// the following config is used to manage consumer offset
	//  ref: https://petertc.medium.com/consumer-offset-management-patterns-of-apache-kafka-f9130e1519f6
	// Offset Config
	// AutoCommitEnable enables the automatic offset commit functionality for this consumer. If set to true, consumer will commit the stored offset asynchronously based on AutoCommitIntervalMs.
	// default: true
	AutoCommitEnable *bool
	// AutoCommitIntervalMs is the frequency in milliseconds that the consumer offsets are committed (written) to offset storage.
	// default: 5000
	AutoCommitIntervalMs *int

	// AutoOffsetStoreEnable Automatically store offset of last message provided to application. The offset store is an in-memory store of the next offset to (auto-)commit for each partition.
	// Note: It is recommended to set enable.auto.offset.store=false for long-time processing applications and then explicitly store offsets (using offsets_store()) after message processing,
	// default: false
	AutoOffsetStoreEnable *bool
}

// ConfluentConsumerGroupCallback confluent consumer group callback
type ConfluentConsumerGroupCallback func(*ckafka.Consumer, ckafka.Event) error

// GetConfluentBuilder get confluent consumer builder
func (cfg ConsumerConfig) GetConfluentBuilder() (*ConfluentConsumerBuilder, error) {
	err := cfg.IsValid()
	if err != nil {
		return nil, err
	}
	cKafkaCfg := &ckafka.ConfigMap{}
	cKafkaCfg.SetKey("bootstrap.servers", strings.Join(cfg.Brokers, ","))
	cKafkaCfg.SetKey("client.id", cfg.ClientID)

	if cfg.InitOffsetMode != nil {
		cKafkaCfg.SetKey("auto.offset.reset", cfg.InitOffsetMode.String())
	} else {
		cKafkaCfg.SetKey("auto.offset.reset", "earliest")
	}

	if cfg.RackID != nil {
		cKafkaCfg.SetKey("client.rack", *cfg.RackID)
	}
	if cfg.ConsumerGroupSessionTimeoutMs != nil {
		cKafkaCfg.SetKey("session.timeout.ms", *cfg.ConsumerGroupSessionTimeoutMs)
	}
	if cfg.ConsumerGroupHeartbeatMs != nil {
		cKafkaCfg.SetKey("heartbeat.interval.ms", *cfg.ConsumerGroupHeartbeatMs)
	}
	if cfg.MaxPollIntervalMs != nil {
		cKafkaCfg.SetKey("max.poll.interval.ms", *cfg.MaxPollIntervalMs)
	}
	if cfg.FetchMaxBytes != nil {
		cKafkaCfg.SetKey("max.partition.fetch.bytes", *cfg.FetchMaxBytes)
	}
	if cfg.FetchMinBytes == nil {
		cKafkaCfg.SetKey("fetch.min.bytes", 5120) // 5kb
	}
	if cfg.FetchMinBytes != nil {
		cKafkaCfg.SetKey("fetch.min.bytes", *cfg.FetchMinBytes)
	}
	if cfg.FetchWaitMaxMs == nil {
		cKafkaCfg.SetKey("fetch.wait.max.ms", 100)
	}
	if cfg.FetchWaitMaxMs != nil {
		cKafkaCfg.SetKey("fetch.wait.max.ms", *cfg.FetchWaitMaxMs)
	}
	if cfg.AutoCommitEnable == nil {
		cKafkaCfg.SetKey("enable.auto.commit", false)
	}
	if cfg.AutoCommitEnable != nil {
		cKafkaCfg.SetKey("enable.auto.commit", *cfg.AutoCommitEnable)
	}
	if cfg.AutoCommitIntervalMs != nil {
		cKafkaCfg.SetKey("auto.commit.interval.ms", *cfg.AutoCommitIntervalMs)
	}
	if cfg.AutoOffsetStoreEnable != nil {
		cKafkaCfg.SetKey("enable.auto.offset.store", *cfg.AutoOffsetStoreEnable)
	} else {
		cKafkaCfg.SetKey("enable.auto.offset.store", false)
	}

	if cfg.TopicMetadataRefreshIntervalMs != nil {
		cKafkaCfg.SetKey("topic.metadata.refresh.interval.ms", *cfg.TopicMetadataRefreshIntervalMs)
	}
	return &ConfluentConsumerBuilder{
		cfg: cKafkaCfg,
	}, nil
}

// IsValid check config is valid
func (cfg ConsumerConfig) IsValid() error {
	if len(cfg.Brokers) == 0 {
		return ErrRequireBrokers
	}
	return nil
}
