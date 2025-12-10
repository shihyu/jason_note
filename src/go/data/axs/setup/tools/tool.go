package tools

import (
	"context"
	"database/sql"
	"encoding/json"
	"os"
	"path/filepath"
	"runtime"

	"github.com/confluentinc/confluent-kafka-go/v2/kafka"
	_ "github.com/jackc/pgx/v5/stdlib"
	_ "github.com/lib/pq"
	"github.com/pressly/goose"
)

func DBMigrationUp(ctx context.Context, driverName, dsn string) error {
	db, err := sql.Open(driverName, dsn)
	if err != nil {
		return err
	}
	defer db.Close()
	err = db.PingContext(ctx)
	if err != nil {
		return err
	}

	migrationPath := GetPath("./migration")
	return goose.Up(db, migrationPath)
}

func DBMigrationUpWithDriver(db *sql.DB, path string) error {
	return goose.Up(db, path)
}

// GetPath returns the absolute path by joining the provided relative paths with the migration project root.
func GetPath(paths ...string) string {
	_, file, _, _ := runtime.Caller(0)
	basePath := filepath.Dir(file)
	rootPath := filepath.Join(basePath, "..", "..")
	return filepath.Join(rootPath, filepath.Join(paths...))
}

func KafkaTopicCreate(ctx context.Context, brokerAddr string) ([]kafka.TopicResult, error) {
	kafkaCfg := &kafka.ConfigMap{}
	kafkaCfg.SetKey("bootstrap.servers", brokerAddr)
	adminClient, err := kafka.NewAdminClient(kafkaCfg)
	if err != nil {
		return nil, err
	}
	kafkaTopicPath := GetPath("./kafka/topic.json")

	topicData, err := os.ReadFile(kafkaTopicPath)
	if err != nil {
		return nil, err
	}
	topicSpecs := []CreateTopicSpec{}
	err = json.Unmarshal(topicData, &topicSpecs)
	if err != nil {
		return nil, err
	}

	var topics []kafka.TopicSpecification
	for _, spec := range topicSpecs {
		topic := kafka.TopicSpecification{
			Topic:             spec.Topic,
			NumPartitions:     spec.NumPartitions,
			ReplicationFactor: spec.ReplicationFactor,
			Config:            spec.Config,
		}
		topics = append(topics, topic)
	}

	results, err := adminClient.CreateTopics(ctx, topics)
	if err != nil {
		return nil, err
	}

	return results, nil
}

type CreateTopicSpec struct {
	Topic             string            `json:"topic"`
	NumPartitions     int               `json:"num_partitions"`
	ReplicationFactor int               `json:"replication_factor"`
	Config            map[string]string `json:"config"`
}
