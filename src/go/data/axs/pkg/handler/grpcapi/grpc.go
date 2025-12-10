package grpcapi

import (
	"github.com/vx416/axs/pb/apipb"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

type GrpcApi struct {
	apipb.UnimplementedAccountBalanceServiceServer
	dbRepo     domain.DBRepository
	redisRepo  domain.RedisRepository
	producer   mq.Producer
	workerPool utils.WorkerPool
}

type Params struct {
	DBRepo     domain.DBRepository
	RedisRepo  domain.RedisRepository
	Producer   mq.Producer
	WorkerPool utils.WorkerPool
	fx.In
}

func NewGrpcApi(params Params) GrpcApi {
	return GrpcApi{
		dbRepo:     params.DBRepo,
		producer:   params.Producer,
		workerPool: params.WorkerPool,
		redisRepo:  params.RedisRepo,
	}
}
