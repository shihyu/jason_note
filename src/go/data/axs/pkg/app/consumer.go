package app

import (
	"context"
	"net/http"
	"time"

	"github.com/rs/zerolog"
	"github.com/vx416/axs/pkg/handler/consumer"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq/kafka"
	"github.com/vx416/axs/pkg/service/processor"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

// NewConsumerAPP creates a new fx.App for the consumer application.
func NewConsumerAPP(cfgName string) *fx.App {
	appOpts := fx.Options(
		fx.Provide(func() (infra.Config, error) {
			config, err := infra.InitConfig(cfgName, "")
			if err != nil {
				return infra.Config{}, err
			}

			log := logger.InitLogger()
			zerolog.SetGlobalLevel(zerolog.InfoLevel)

			svcID, err := infra.GetSvcID()
			if err != nil {
				return infra.Config{}, nil
			}
			partitionNum, err := infra.GetConsumerOrdinal()
			if err != nil {
				return infra.Config{}, nil
			}
			newLog := log.With().Str("svc_id", svcID).Int("partition_num", int(partitionNum)).Logger()
			logger.SetGlobalLogger(&newLog)
			logger.GetLogger(context.Background()).Info().Msg("consumer config initialized")
			return config, nil
		}),
		EventProcessor,
		fx.Provide(utils.WorkerPoolProvider(30, 2000, 30*time.Second)),
		fx.Provide(infra.NewKafkaConsumerBuilder),
		fx.Invoke(RunConsumer),
		fx.Invoke(RunLivenessProbe),
	)
	return fx.New(
		appOpts,
	)
}

// RunConsumer sets up and runs the consumer within the fx lifecycle.
func RunConsumer(lc fx.Lifecycle, consumerBuilder *kafka.ConfluentConsumerBuilder, eventProcessor *processor.EventProcessor) error {
	var consumer *consumer.BatchEventConsumer
	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			logger.GetLogger(ctx).Info().Msg("consumer starting")
			go func() {
				partition, commitOffset, ok := eventProcessor.TryToBecomeLeader(ctx)
				if ok {
					logger.GetLogger(ctx).Info().Msg("acquired leader lock, starting consumer")
					var err error
					consumer, err = buildConsumer(consumerBuilder, eventProcessor, int(partition), int(commitOffset))
					if err != nil {
						logger.GetLogger(ctx).Fatal().Err(err).Msg("failed to build consumer")
					}
					consumer.StartConsuming()
				} else {
					logger.GetLogger(ctx).Info().Msg("did not acquire leader lock, event processor closing")
				}
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			var err error
			if consumer != nil {
				logger.GetLogger(ctx).Info().Msg("consumer shutting down")
				err := consumer.GracefulShutdown(5 * time.Second)
				if err != nil {
					logger.GetLogger(ctx).Error().Err(err).Msg("consumer shutdown failed")
				} else {
					logger.GetLogger(ctx).Info().Msg("consumer shutdown success")
				}
			}
			eventProcessor.Close(ctx)
			return err
		},
	})
	return nil
}

// buildConsumer constructs a BatchEventConsumer with the appropriate starting offset.
func buildConsumer(consumerBuilder *kafka.ConfluentConsumerBuilder, eventProcessor *processor.EventProcessor, partition, commitOffset int) (*consumer.BatchEventConsumer, error) {
	ctx := context.Background()
	consumerGroupName := "event_processor_group"
	var offset kafka.Offset
	if commitOffset <= 0 {
		offset = kafka.Beginning
	} else {
		offset = kafka.Offset(commitOffset + 1)
	}
	consumerReader, err := consumerBuilder.BuildPartitionConsumer(ctx, consumerGroupName, kafka.TopicPartition{
		Topic:     model.BalanceChangeEventTopic,
		Partition: int32(partition),
		Offset:    offset,
	})
	if err != nil {
		return nil, err
	}
	logger.GetLogger(ctx).Info().Str("topic", model.BalanceChangeEventTopic).Int32("partition", int32(partition)).Int64("start_offset", int64(offset)).Msg("consumer created")
	return consumer.NewBatchEventConsumer(consumerReader, eventProcessor, 200, time.Millisecond*30, 1*time.Second), nil
}

// RunLivenessProbe starts an HTTP server to handle liveness and readiness probes.
func RunLivenessProbe(lc fx.Lifecycle, eventProcessor *processor.EventProcessor) error {
	mux := http.NewServeMux()
	mux.HandleFunc("/ready", func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("OK"))
	})

	mux.HandleFunc("/live", func(w http.ResponseWriter, r *http.Request) {
		if !eventProcessor.IsClosed() {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte("OK"))
		} else {
			w.WriteHeader(http.StatusServiceUnavailable)
			w.Write([]byte("NOT OK"))
		}
	})
	httpSvc := &http.Server{Addr: ":8080", Handler: mux}

	// start liveness probe server
	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			go func() {
				logger.GetLogger(ctx).Info().Msg("liveness probe server starting")
				httpSvc.ListenAndServe()
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			logger.GetLogger(ctx).Info().Msg("liveness probe server shutting down")
			return httpSvc.Close()
		},
	})
	return nil
}
