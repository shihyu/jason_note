package main

import (
	"context"
	"flag"
	"log"
	"time"

	"github.com/vx416/axs/setup/tools"
)

var (
	sqlDriver   = flag.String("sql-driver", "", "SQL database driver (e.g., postgres, mysql)")
	sqlDSN      = flag.String("sql-dsn", "", "SQL database connection string")
	kafkaBroker = flag.String("kafka-broker", "", "Kafka broker address")
	runSeed     = flag.Bool("run-seed", false, "Whether to run seed data after migrations")
)

func main() {
	flag.Parse()

	log.Printf(`
		Starting setup with parameters:
		SQL Driver: %s
		SQL DSN: %s
		Kafka Broker: %s
		Run Seed: %v
	`, *sqlDriver, *sqlDSN, *kafkaBroker, *runSeed)

	dbCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	err := tools.DBMigrationUp(dbCtx, *sqlDriver, *sqlDSN)
	if err != nil {
		log.Fatalf("Database migration failed: %v", err)
	}
	log.Println("Database migration completed successfully")

	kafkaCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	results, err := tools.KafkaTopicCreate(kafkaCtx, *kafkaBroker)
	if err != nil {
		log.Fatalf("Kafka topic creation failed: %v", err)
	}
	for _, result := range results {
		if result.Error.Code() != 0 {
			log.Printf("Topic %s creation failed: %v", result.Topic, result.Error)
		} else {
			log.Printf("Topic %s created successfully", result.Topic)
		}
	}
	log.Println("Kafka topic creation process completed")

	if *runSeed {
		log.Println("Start run seed program")
		seedCtx := context.Background()
		err := tools.RunAccountSeedData(seedCtx, *sqlDriver, *sqlDSN)
		if err != nil {
			log.Fatalf("Run seed data failed: %v", err)
		}
		log.Println("Seed data completed successfully")
	}
}
