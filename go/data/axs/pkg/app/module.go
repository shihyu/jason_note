package app

import (
	"github.com/vx416/axs/pkg/handler/grpcapi"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/repository/cachedao"
	"github.com/vx416/axs/pkg/repository/dbdao"
	"github.com/vx416/axs/pkg/repository/redisdao"
	"github.com/vx416/axs/pkg/service/processor"
	"go.uber.org/fx"
)

var (
	// ConfigProvider provides configuration related dependencies.
	ConfigProvider = fx.Options(
		fx.Provide(func(cfg infra.Config) infra.ServerConfig {
			return cfg.Server
		}),
		fx.Provide(func(cfg infra.Config) infra.DBConfig {
			return cfg.DB
		}),
		fx.Provide(func(cfg infra.Config) infra.RedisConfig {
			return cfg.Redis
		}),
		fx.Provide(func(cfg infra.Config) infra.KafkaConfig {
			return cfg.Kafka
		}),
	)

	// InfraProvider provides infrastructure related dependencies.
	InfraProvider = fx.Options(
		ConfigProvider,
		fx.Provide(infra.NewSqlx),
		fx.Provide(infra.NewRedisClient),
		fx.Provide(infra.NewKafkaProducer),
	)

	// RepoProvider provides repository related dependencies.
	RepoProvider = fx.Options(
		InfraProvider,
		fx.Provide(cachedao.NewCacheDao),
		fx.Provide(dbdao.NewDBDRepository),
		fx.Provide(redisdao.NewRedisRepository),
	)

	// GrpcAPI provides gRPC API related dependencies.
	GrpcAPI = fx.Options(
		RepoProvider,
		fx.Provide(grpcapi.NewGrpcApi),
	)

	// EventProcessor provides event processing related dependencies.
	EventProcessor = fx.Options(
		RepoProvider,
		fx.Provide(processor.NewEventProcessor),
	)
)
