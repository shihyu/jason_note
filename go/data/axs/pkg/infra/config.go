package infra

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	_ "github.com/jackc/pgx/v5/stdlib"
	"github.com/pkg/errors"
	"github.com/redis/go-redis/v9"
	"github.com/spf13/viper"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/mq/kafka"

	"github.com/jmoiron/sqlx"
)

var (
	globalConfig *Config
)

// GetConfig returns the global configuration
func GetConfig() *Config {
	return globalConfig
}

// InitConfig initializes the configuration from the specified file and path
func InitConfig(configName string, configPath string) (Config, error) {
	var cfg Config
	if configPath == "" {
		viper.AddConfigPath(configPath)
	}
	if configName == "" {
		configName = "config"
	}
	viper.AddConfigPath(GetAbsPath("config"))
	viper.SetConfigName(configName)
	viper.SetConfigType("toml")
	viper.SetEnvPrefix("AXS")
	viper.AutomaticEnv()
	viper.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))
	err := viper.ReadInConfig()
	if err != nil {
		return cfg, err
	}

	err = viper.Unmarshal(&cfg)
	if err != nil {
		return cfg, err
	}
	globalConfig = &cfg
	return cfg, nil
}

// GetAbsPath returns the absolute path by joining the provided paths with the project root directory.
func GetAbsPath(paths ...string) string {
	_, filePath, _, _ := runtime.Caller(1)
	basePath := filepath.Dir(filePath)
	rootPath := filepath.Join(basePath, "..", "..")
	return filepath.Join(rootPath, filepath.Join(paths...))
}

// ServerConfig server configuration
type ServerConfig struct {
	GrpcHost         string `mapstructure:"grpc_host"`
	HttpHost         string `mapstructure:"http_host"`
	StressTestMode   bool   `mapstructure:"stress_test_mode"`
	StressStatsTopic string `mapstructure:"stress_stats_topic"`
	SvcType          string `mapstructure:"svc_type"`
}

// Config application configuration
type Config struct {
	Server ServerConfig `mapstructure:"server"`
	DB     DBConfig     `mapstructure:"database"`
	Redis  RedisConfig  `mapstructure:"redis"`
	Kafka  KafkaConfig  `mapstructure:"kafka"`
}

// DBConfig database configuration
type DBConfig struct {
	DBType       string        `mapstructure:"db_type"`
	DBHost       string        `mapstructure:"db_host"`
	DBPort       int           `mapstructure:"db_port"`
	DBUser       string        `mapstructure:"db_user"`
	DBPassword   string        `mapstructure:"db_password"`
	DBName       string        `mapstructure:"db_name"`
	DSNOptions   string        `mapstructure:"dsn_options"`
	MaxOpenConns int           `mapstructure:"max_open_conns"`
	MaxIdleConns int           `mapstructure:"max_idle_conns"`
	MaxIdleTime  time.Duration `mapstructure:"max_idle_time"`
	MaxLifeTime  time.Duration `mapstructure:"max_life_time"`
}

// NewSqlx creates a new sqlx.DB instance based on the provided DBConfig.
func NewSqlx(cfg DBConfig) (*sqlx.DB, *pgx.Conn, error) {
	var pgxConn *pgx.Conn
	dsn := ""
	switch cfg.DBType {
	case "postgres":
		dsn = "postgres://" + cfg.DBUser + ":" + cfg.DBPassword + "@" + cfg.DBHost + ":" + strconv.Itoa(cfg.DBPort) + "/" + cfg.DBName + "?sslmode=disable"

		timeoutCtx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
		defer cancel()
		pgxConnTemp, err := pgx.Connect(timeoutCtx, dsn)
		if err != nil {
			return nil, nil, errors.WithMessage(err, dsn)
		}
		pgxConn = pgxConnTemp
	default:
		return nil, nil, fmt.Errorf("unsupported db type: %s", cfg.DBType)
	}
	dbType := cfg.DBType
	if dbType == "postgres" {
		dbType = "pgx"
	}
	db, err := sqlx.Connect(dbType, dsn)
	if err != nil {
		return nil, nil, errors.WithMessage(err, dsn)
	}
	logger.SetIsPg(dbType)
	db.SetMaxOpenConns(cfg.MaxOpenConns)
	db.SetMaxIdleConns(cfg.MaxIdleConns)
	db.SetConnMaxIdleTime(cfg.MaxIdleTime)
	db.SetConnMaxLifetime(cfg.MaxLifeTime)
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	err = db.PingContext(ctx)
	if err != nil {
		return nil, nil, errors.WithMessage(err, dsn)
	}
	return db, pgxConn, nil
}

// RedisConfig redis configuration
type RedisConfig struct {
	Addr     string `mapstructure:"addr"`
	Port     int    `mapstructure:"port"`
	Password string `mapstructure:"password"`
	DB       int    `mapstructure:"db"`
}

// NewRedisClient creates a new Redis client based on the provided RedisConfig.
func NewRedisClient(cfg RedisConfig) (redis.UniversalClient, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()
	host := fmt.Sprintf("%s:%d", cfg.Addr, cfg.Port)
	client := redis.NewClient(&redis.Options{
		Addr:     host,
		Password: cfg.Password,
		DB:       cfg.DB,
	})
	err := client.Ping(ctx).Err()
	if err != nil {
		return nil, err
	}
	return client, nil
}

// KafkaConfig kafka configuration
type KafkaConfig struct {
	Brokers                      []string `mapstructure:"brokers"`
	BalanceChangeTopicPartitions int      `mapstructure:"balance_change_topic_partitions"`
}

// NewKafkaProducer creates a new Kafka Producer.
func NewKafkaProducer(cfg KafkaConfig) (mq.Producer, error) {
	producerConfig := kafka.ProducerConfig{
		Brokers: cfg.Brokers,
	}
	return producerConfig.GetConfluentProducer(nil)
}

// NewKafkaConsumerBuilder creates a new Kafka Consumer Builder.
func NewKafkaConsumerBuilder(cfg KafkaConfig) (*kafka.ConfluentConsumerBuilder, error) {
	consumerConfig := kafka.ConsumerConfig{
		Brokers: cfg.Brokers,
	}
	return consumerConfig.GetConfluentBuilder()
}

var (
	GitCommit = "unknown"
)

// GetSvcID generates a unique service identifier based on the hostname, process ID, and Git commit hash.
func GetSvcID() (string, error) {
	hostName, err := os.Hostname()
	if err != nil {
		return "unknown_svc_id", err
	}
	pid := os.Getpid()
	return fmt.Sprintf("%s_%d_%s", hostName, pid, GitCommit), nil
}

// GetConsumerOrdinal retrieves the consumer ordinal from the CONSUMER_ORDINAL environment variable.
func GetConsumerOrdinal() (int64, error) {
	podName := os.Getenv("CONSUMER_ORDINAL")
	if podName == "" {
		return -1, fmt.Errorf("CONSUMER_ORDINAL env var not set")
	}
	ss := strings.Split(podName, "-")
	ordinalStr := ss[len(ss)-1]
	ordinal, err := strconv.Atoi(ordinalStr)
	if err != nil {
		return -1, err
	}
	return int64(ordinal), nil
}
