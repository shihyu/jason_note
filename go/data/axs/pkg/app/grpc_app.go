package app

import (
	"context"
	"net"
	"time"

	"github.com/rs/zerolog"
	"github.com/vx416/axs/pb/apipb"
	"github.com/vx416/axs/pkg/handler/grpcapi"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
	"google.golang.org/grpc"
)

// NewGrpcApiAPP creates a new fx.App for the gRPC API application.
func NewGrpcApiAPP(cfgName string, opts ...fx.Option) *fx.App {
	logger.InitLogger()
	zerolog.SetGlobalLevel(zerolog.InfoLevel)
	logger.SetIsPg("postgres")
	appOpts := []fx.Option{
		fx.Provide(func() (infra.Config, error) {
			return infra.InitConfig(cfgName, "")
		}),
		GrpcAPI,
		fx.Provide(utils.WorkerPoolProvider(30, 2000, 30*time.Second)),
		fx.Invoke(RunGrpcServer),
	}

	appOpts = append(appOpts, opts...)
	return fx.New(appOpts...)
}

// RunGrpcServer run a new gRPC server
func RunGrpcServer(lc fx.Lifecycle, config infra.ServerConfig, grpcApi grpcapi.GrpcApi) error {
	gRPCServer := grpc.NewServer(
		grpc.MaxRecvMsgSize(100 * 1024 * 1024),
	)

	apipb.RegisterAccountBalanceServiceServer(gRPCServer, grpcApi)

	// Register Grpc Server
	lc.Append(fx.Hook{
		OnStart: func(ctx context.Context) error {
			grpcHost := config.GrpcHost
			listener, err := net.Listen("tcp", grpcHost)
			if err != nil {
				return err
			}
			go func() {
				logger.GetLogger(ctx).Info().Msgf("gRPC server is running on %s", grpcHost)
				if err := gRPCServer.Serve(listener); err != nil {
					logger.GetLogger(ctx).Fatal().Err(err).Msg("failed to start grpc server")
				}
			}()
			return nil
		},
		OnStop: func(ctx context.Context) error {
			gRPCServer.GracefulStop()
			return nil
		},
	})

	return nil
}
