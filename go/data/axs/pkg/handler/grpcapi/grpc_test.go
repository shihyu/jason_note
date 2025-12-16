package grpcapi_test

import (
	"testing"
	"time"

	"github.com/go-jose/go-jose/v4/testutils/require"
	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
	"github.com/vx416/axs/pb/apipb"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/handler/grpcapi"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/repository/dbdao"
	"github.com/vx416/axs/pkg/repository/redisdao"
	"github.com/vx416/axs/pkg/testutil"
	"github.com/vx416/axs/pkg/testutil/factory"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

func TestGrpcApiTestSuite(t *testing.T) {
	ti, err := testutil.NewTestInstance(t)
	require.NoError(t, err, "failed to create test instance")
	suite.Run(t, &GrpcApiTestSuite{
		TestInstance: ti,
	})

}

type GrpcApiTestSuite struct {
	suite.Suite
	TestInstance *testutil.TestInstance
	GrpcApi      grpcapi.GrpcApi
	DBRepo       domain.DBRepository
	WorkerPool   utils.WorkerPool
}

func (suite *GrpcApiTestSuite) SetupSuite() {
	infraProvider, err := suite.TestInstance.GetTestInfraProvider()
	suite.Require().NoError(err, "failed to get test infra provider")

	suite.WorkerPool, err = utils.InitAndRunGlobalWorkerPool(5, 100)
	suite.Require().NoError(err, "failed to init worker pool")

	app := fx.New(fx.Options(
		infraProvider,
		fx.Provide(redisdao.NewRedisRepository),
		fx.Provide(dbdao.NewDBDRepository),
		fx.Provide(grpcapi.NewGrpcApi),
		fx.Populate(&suite.DBRepo),
		fx.Populate(&suite.GrpcApi),
		fx.Provide(func() utils.WorkerPool {
			return suite.WorkerPool
		}),
	))

	suite.Require().NoError(app.Start(suite.TestInstance.Ctx), "failed to start app")

	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to clear redis data")
}

func (suite *GrpcApiTestSuite) TestXXX() {
	suite.TestInstance.MockProducer.EXPECT().Publish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{
		{
			Partition: 5,
			Offset:    1,
		},
	}).Times(2)

	req := factory.SubmitBalanceChangeRequest.WithAccInfo(1, 1).MustBuild().(*apipb.SubmitBalanceChangeRequest)
	change := factory.BalanceChangeRequest.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*apipb.BalanceChange)
	req.Changes = append(req.Changes, change)

	resp, err := suite.GrpcApi.BatchSubmitBalanceChanges(suite.TestInstance.Ctx, &apipb.BatchSubmitBalanceChangesRequest{
		Requests: []*apipb.SubmitBalanceChangeRequest{req},
	})
	suite.Require().NoError(err, "SubmitBalanceChange failed")
	suite.Require().NotNil(resp, "expected non-nil response")
	for _, r := range resp.Responses {
		suite.Equal(apipb.BalanceChangeEventStatus_Init, r.Status, "expected status to be Init")
		suite.Empty(r.ErrorMessage, "expected no error message")
	}

	req = factory.SubmitBalanceChangeRequest.WithAccInfo(1, 1).MustBuild().(*apipb.SubmitBalanceChangeRequest)
	change = factory.BalanceChangeRequest.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*apipb.BalanceChange)
	req.Changes = append(req.Changes, change)

	resp, err = suite.GrpcApi.BatchSubmitBalanceChanges(suite.TestInstance.Ctx, &apipb.BatchSubmitBalanceChangesRequest{
		Requests: []*apipb.SubmitBalanceChangeRequest{req},
	})
	suite.Require().NoError(err, "SubmitBalanceChange failed")
	suite.Require().NotNil(resp, "expected non-nil response")
	for _, r := range resp.Responses {
		suite.Equal(apipb.BalanceChangeEventStatus_Init, r.Status, "expected status to be Init")
		suite.Empty(r.ErrorMessage, "expected no error message")
	}
	suite.WorkerPool.WaitAllDone(100 * time.Millisecond)

	// suite.WorkerPool.WaitAllDone(100 * time.Millisecond)
}
