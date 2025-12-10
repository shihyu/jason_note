package processor_test

import (
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/suite"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/repository/cachedao"
	"github.com/vx416/axs/pkg/repository/dbdao"
	"github.com/vx416/axs/pkg/repository/redisdao"
	"github.com/vx416/axs/pkg/service/processor"
	"github.com/vx416/axs/pkg/testutil"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

func TestLeaderElectionTestSuite(t *testing.T) {
	testInstance, err := testutil.NewTestInstance(t)
	if err != nil {
		t.Fatalf("failed to create test instance: %v", err)
	}

	suite.Run(t, &LeaderElectionTestSuite{
		TestInstance: testInstance,
	})
}

type LeaderElectionTestSuite struct {
	TestInstance *testutil.TestInstance
	suite.Suite
	*processor.EventProcessor
	DBRepo     domain.DBRepository
	RedisRepo  domain.RedisRepository
	CacheRepo  domain.CacheRepository
	WorkerPool utils.WorkerPool
}

func (suite *LeaderElectionTestSuite) SetupSuite() {
	infraProvider, err := suite.TestInstance.GetTestInfraProvider()
	suite.Require().NoError(err, "failed to get infra provider")

	suite.WorkerPool, err = utils.InitAndRunGlobalWorkerPool(5, 100)
	suite.Require().NoError(err, "failed to init worker pool")

	app := fx.New(fx.Options(
		infraProvider,
		fx.Provide(func() utils.WorkerPool {
			return suite.WorkerPool
		}),
		fx.Provide(processor.NewEventProcessor),
		fx.Provide(cachedao.NewCacheDao),
		fx.Provide(dbdao.NewDBDRepository),
		fx.Provide(redisdao.NewRedisRepository),
		fx.Populate(&suite.EventProcessor),
		fx.Populate(&suite.DBRepo),
		fx.Populate(&suite.RedisRepo),
		fx.Populate(&suite.CacheRepo),
	))
	suite.Require().NoError(app.Start(suite.TestInstance.Ctx), "failed to start fx app")
	os.Setenv("CONSUMER_ORDINAL", "1")
	suite.Require().NoError(err, "failed to clear redis data")
	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to reset and run seed data")
	err = suite.CacheRepo.ClearAllData(suite.TestInstance.Ctx)
	suite.Require().NoError(err, "failed to clear cache data")
}

func (suite *LeaderElectionTestSuite) Test_LeaderElection() {

	_, _, ok := suite.EventProcessor.TryToBecomeLeader(suite.TestInstance.Ctx)
	suite.Require().True(ok, "failed to become leader")
	suite.True(suite.EventProcessor.IsLeader(), "should be leader after becoming leader")
	suite.NotEmpty((suite.EventProcessor.IsLeader()), "leader lock key should not be empty")
	time.Sleep(time.Duration(model.LeaderTTLSecond) * time.Second)

	isLeader := suite.EventProcessor.IsLeader()
	suite.Require().True(isLeader, "leader should still be valid after TTL duration")

	ok, err := suite.EventProcessor.DBRepo.UpdateCommitOffsets(suite.TestInstance.Ctx, model.BalanceChangeEventTopic, suite.GetPartition(), 100, suite.GetLeaderSvcID(), int(suite.GetFencingToken()))
	suite.Require().NoError(err, "failed to acquire leaded lock")
	suite.Require().True(ok, "commit offset should be updated")

	_, ok, err = suite.EventProcessor.DBRepo.AcquirePartitionLeaderLock(suite.TestInstance.Ctx, model.BalanceChangeEventTopic, int32(suite.GetPartition()), "new_svc_id")
	suite.Require().NoError(err, "failed to acquire leaded lock")
	suite.Require().False(ok, "leader lock shouldn't be taken")

	suite.EventProcessor.CloseNow(suite.TestInstance.Ctx)
	isLeader = suite.EventProcessor.IsLeader()
	suite.Require().False(isLeader, "leader should be invalid after processor is closed")
	suite.True(suite.EventProcessor.IsClosed(), "processor should be closed")

	partitionLock, ok, err := suite.EventProcessor.DBRepo.AcquirePartitionLeaderLock(suite.TestInstance.Ctx, model.BalanceChangeEventTopic, int32(suite.GetPartition()), "new_svc_id")
	suite.Require().NoError(err, "failed to acquire leaded lock")
	suite.Require().True(ok, "leader lock should be taken")
	suite.Require().EqualValues(100, partitionLock.CommitOffset)
}
