package processor_test

import (
	"context"
	"os"
	"testing"
	"time"

	"github.com/stretchr/testify/mock"
	"github.com/stretchr/testify/suite"
	"github.com/vx416/axs/pb/eventpb"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/repository/cachedao"
	"github.com/vx416/axs/pkg/repository/dbdao"
	"github.com/vx416/axs/pkg/repository/redisdao"
	"github.com/vx416/axs/pkg/service/processor"
	"github.com/vx416/axs/pkg/testutil"
	"github.com/vx416/axs/pkg/testutil/factory"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

func TestEventProcessorTestSuite(t *testing.T) {
	testInstance, err := testutil.NewTestInstance(t)
	if err != nil {
		t.Fatalf("failed to create test instance: %v", err)
	}
	suite.Run(t, &EventProcessorTestSuite{
		TestInstance: testInstance,
	})

}

type EventProcessorTestSuite struct {
	TestInstance *testutil.TestInstance
	suite.Suite
	*processor.EventProcessor
	DBRepo     domain.DBRepository
	RedisRepo  domain.RedisRepository
	CacheRepo  domain.CacheRepository
	WorkerPool utils.WorkerPool
}

func (suite *EventProcessorTestSuite) SetupSuite() {
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
}

func (suite *EventProcessorTestSuite) SetupTest() {
	err := suite.TestInstance.ClearRedisData()
	suite.Require().NoError(err, "failed to clear redis data")
	err = suite.TestInstance.ResetAndRunSeedData()
	suite.Require().NoError(err, "failed to reset and run seed data")
	err = suite.CacheRepo.ClearAllData(suite.TestInstance.Ctx)
	suite.Require().NoError(err, "failed to clear cache data")
	_, _, ok := suite.EventProcessor.TryToBecomeLeader(suite.TestInstance.Ctx)
	suite.Require().True(ok, "should become leader")
}

func (suite *EventProcessorTestSuite) Test_ProcessMultiCurrencyAndFrozenAvailableTransitions() {
	event := factory.BalanceChangeEvent.WithAccInfo(1000, 1000, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*eventpb.BalanceChange)
	event.Changes = append(event.Changes, change)
	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Once()
	suite.ProcessEvents(event)
	err := suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")
	suite.AssertEventStatus(model.ChangeLogStatusApplied, event)

	opts := model.ListAccountBalancesOptions{}
	opts.AddFilter(1000, "USDT", 1)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1000: {
				"USDT": "100",
			},
		},
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
			},
		},
	)

	event2 := factory.BalanceChangeEvent.WithAccInfo(1000, 1000, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change2 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-100", "100").MustBuild().(*eventpb.BalanceChange)
	event2.Changes = append(event2.Changes, change2)
	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Once()
	suite.ProcessEvents(event2)
	err = suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")
	suite.AssertEventStatus(model.ChangeLogStatusApplied, event2)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
			},
		},
		map[int64]map[string]string{
			1000: {
				"USDT": "100",
			},
		},
	)

	event3 := factory.BalanceChangeEvent.WithAccInfo(1000, 1000, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change3 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("0", "-100").MustBuild().(*eventpb.BalanceChange)
	change1 := factory.BalanceChange.WithCurrency("BTC", "BTC").WithDelta("1", "0").MustBuild().(*eventpb.BalanceChange)
	event3.Changes = append(event3.Changes, change3, change1)
	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Once()
	suite.ProcessEvents(event3)
	err = suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")
	suite.AssertEventStatus(model.ChangeLogStatusApplied, event3)

	opts = model.ListAccountBalancesOptions{}
	opts.AddFilter(1000, "USDT", 1)
	opts.AddFilter(1000, "BTC", 1)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
				"BTC":  "1",
			},
		},
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
				"BTC":  "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) Test_ShouldApplyIndependentEventsAcrossDifferentAccounts() {
	event := factory.BalanceChangeEvent.WithAccInfo(1000, 1000, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*eventpb.BalanceChange)
	event.Changes = append(event.Changes, change)

	event2 := factory.BalanceChangeEvent.WithAccInfo(1, 1, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change2 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-100", "0").MustBuild().(*eventpb.BalanceChange)
	event2.Changes = append(event2.Changes, change2)

	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Twice()
	suite.ProcessEvents(event, event2)
	err := suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")
	suite.AssertEventStatus(model.ChangeLogStatusApplied, event, event2)

	opts := model.ListAccountBalancesOptions{}
	opts.AddFilter(1000, "USDT", 1)
	opts.AddFilter(1, "USDT", 1)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1000: {
				"USDT": "100",
			},
			1: {
				"USDT": "900",
			},
		},
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
			},
			1: {
				"USDT": "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) Test_ShouldReadCacheDirectlyAndApplyEventsConsistently() {
	preLoad := model.ListAccountBalancesOptions{}
	preLoad.AddFilter(1, "USDT", 1)
	_, err := suite.EventProcessor.ChangeApplier.GetReadBalanceMap(context.Background(), preLoad)
	suite.Require().NoError(err, "failed to get read balance map before processing events")

	event := factory.BalanceChangeEvent.WithAccInfo(1000, 1000, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*eventpb.BalanceChange)
	event.Changes = append(event.Changes, change)

	event2 := factory.BalanceChangeEvent.WithAccInfo(1, 1, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change2 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-100", "0").MustBuild().(*eventpb.BalanceChange)
	event2.Changes = append(event2.Changes, change2)
	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Twice()

	suite.ProcessEvents(event, event2)
	err = suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")
	suite.AssertEventStatus(model.ChangeLogStatusApplied, event2)

	opts := model.ListAccountBalancesOptions{}
	opts.AddFilter(1000, "USDT", 1)
	opts.AddFilter(1, "USDT", 1)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1000: {
				"USDT": "100",
			},
			1: {
				"USDT": "900",
			},
		},
		map[int64]map[string]string{
			1000: {
				"USDT": "0",
			},
			1: {
				"USDT": "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) Test_ShouldApplyMultipleChangesInSingleEventAtomically() {
	preLoad := model.ListAccountBalancesOptions{}
	preLoad.AddFilter(1, "USDT", 1)
	preLoad.AddFilter(1, "BTC", 1)
	_, err := suite.EventProcessor.ChangeApplier.GetReadBalanceMap(context.Background(), preLoad)
	suite.Require().NoError(err, "failed to get read balance map before processing events")

	event2 := factory.BalanceChangeEvent.WithAccInfo(1, 1, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change2 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-100", "0").MustBuild().(*eventpb.BalanceChange)
	change21 := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("100", "0").MustBuild().(*eventpb.BalanceChange)
	change23 := factory.BalanceChange.WithCurrency("BTC", "BTC").WithDelta("100", "0").MustBuild().(*eventpb.BalanceChange)
	event2.Changes = append(event2.Changes, change2, change21, change23)
	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Once()
	suite.ProcessEvents(event2)
	err = suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")

	suite.AssertEventStatus(model.ChangeLogStatusApplied, event2)

	opts := model.ListAccountBalancesOptions{}
	opts.AddFilter(1, "USDT", 1)
	opts.AddFilter(1, "BTC", 1)
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			1: {
				"USDT": "1000",
				"BTC":  "1100",
			},
		},
		map[int64]map[string]string{
			1: {
				"USDT": "0",
				"BTC":  "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) Test_ShouldApplyEventsWithDifferentUsers() {
	events := factory.BalanceChangeEvent.MustBuildN(600).([]*eventpb.BalanceChangeEvent)
	for i := range events {
		change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-100", "100").MustBuild().(*eventpb.BalanceChange)
		change2 := factory.BalanceChange.WithCurrency("BTC", "BTC").WithDelta("-0.01", "0.01").MustBuild().(*eventpb.BalanceChange)
		change3 := factory.BalanceChange.WithCurrency("ETH", "ETH").WithDelta("-0.01", "0.01").MustBuild().(*eventpb.BalanceChange)
		events[i].Changes = append(events[i].Changes, change, change2, change3)
	}

	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Times(len(events))
	suite.ProcessEvents(events...)
	err := suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")

	suite.AssertEventStatus(model.ChangeLogStatusApplied, events...)
	for _, event := range events {
		opts := model.ListAccountBalancesOptions{}
		for _, change := range event.Changes {
			opts.AddFilter(event.AccountId, change.CurrencyCode, event.AccountShardId)
		}
		suite.AssertBalance(opts,
			map[int64]map[string]string{
				event.AccountId: {
					"USDT": "900",
					"BTC":  "999.99",
					"ETH":  "999.99",
				},
			},
			map[int64]map[string]string{
				event.AccountId: {
					"USDT": "100",
					"BTC":  "0.01",
					"ETH":  "0.01",
				},
			},
		)
	}
}

func (suite *EventProcessorTestSuite) Test_ShouldHandleBalanceInsufficient() {
	event := factory.BalanceChangeEvent.WithAccInfo(1, 1, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-10000000", "0").MustBuild().(*eventpb.BalanceChange)
	event.Changes = append(event.Changes, change)

	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Times(1)
	suite.ProcessEvents(event)
	err := suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")

	suite.AssertEventStatus(model.ChangeLogStatusCannotApplied, event)
	opts := model.ListAccountBalancesOptions{}
	for _, change := range event.Changes {
		opts.AddFilter(event.AccountId, change.CurrencyCode, event.AccountShardId)
	}
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			event.AccountId: {
				"USDT": "1000",
			},
		},
		map[int64]map[string]string{
			event.AccountId: {
				"USDT": "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) Test_ShouldHandleBalanceInsufficientAndFallbackCurrency() {
	event := factory.BalanceChangeEvent.WithAccInfo(1, 1, 1).MustBuild().(*eventpb.BalanceChangeEvent)
	change := factory.BalanceChange.WithCurrency("USDT", "USDT").WithDelta("-10000000", "0").WithFallbackInfo("BTC", "BTC", "-1", "0").MustBuild().(*eventpb.BalanceChange)
	event.Changes = append(event.Changes, change)

	suite.TestInstance.MockProducer.EXPECT().AsyncPublish(mock.Anything, mock.Anything).Return([]mq.ProducedMessageResult{}).Times(1)
	suite.ProcessEvents(event)
	err := suite.PersistentWorker.DoNowAndWait(context.Background())
	suite.WorkerPool.WaitAllDone(10 * time.Millisecond)
	suite.Require().NoError(err, "failed to do now and wait")

	suite.AssertEventStatus(model.ChangeLogStatusApplied, event)
	opts := model.ListAccountBalancesOptions{}
	for _, change := range event.Changes {
		opts.AddFilter(event.AccountId, change.CurrencyCode, event.AccountShardId)
		opts.AddFilter(event.AccountId, change.FallbackCurrencyCode, event.AccountShardId)
	}
	suite.AssertBalance(opts,
		map[int64]map[string]string{
			event.AccountId: {
				"USDT": "1000",
				"BTC":  "999",
			},
		},
		map[int64]map[string]string{
			event.AccountId: {
				"USDT": "0",
				"BTC":  "0",
			},
		},
	)
}

func (suite *EventProcessorTestSuite) AssertBalance(options model.ListAccountBalancesOptions, expectedAvailable, expectedFrozen map[int64]map[string]string) {
	balanceView, err := suite.DBRepo.ListAccountBalances(suite.TestInstance.Ctx, options)
	suite.Require().NoError(err, "failed to list account balances")
	suite.Require().Greater(len(balanceView), 0, "expected at least one account balance")
	for accid, currencyMap := range expectedAvailable {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "db: expected account balance accid %d to exist", accid)
			available, ok := balanceView[accid].GetAvailableAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "db: expected currency balance to exist")
			suite.Require().Equal(amount, available.String(), "db: expected available amount to match for account %d currency %s", accid, currency)
		}
	}
	for accid, currencyMap := range expectedFrozen {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "db: expected account balance accid %d to exist", accid)
			frozen, ok := balanceView[accid].GetFrozenAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "db: expected currency balance to exist")
			suite.Require().Equal(amount, frozen.String(), "db: expected frozen amount to match for account %d currency %s", accid, currency)
		}
	}

	balanceView, err = suite.CacheRepo.ListAccountBalances(suite.TestInstance.Ctx, options)
	suite.Require().NoError(err, "failed to list account balances")
	suite.Require().Greater(len(balanceView), 0, "expected at least one account balance")
	for accid, currencyMap := range expectedAvailable {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "cache: expected account balance accid %d to exist", accid)
			available, ok := balanceView[accid].GetAvailableAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "cache: expected currency balance to exist")
			suite.Require().Equal(amount, available.String(), "cache: expected available amount to match for account %d currency %s", accid, currency)
		}
	}
	for accid, currencyMap := range expectedFrozen {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "cache: expected account balance accid %d to exist", accid)
			frozen, ok := balanceView[accid].GetFrozenAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "cache: expected currency balance to exist")
			suite.Require().Equal(amount, frozen.String(), "cache: expected frozen amount to match for account %d currency %s", accid, currency)
		}
	}

	balanceView, err = suite.RedisRepo.ListAccountBalances(suite.TestInstance.Ctx, options)
	suite.Require().NoError(err, "failed to list account balances")
	suite.Require().Greater(len(balanceView), 0, "expected at least one account balance")
	for accid, currencyMap := range expectedAvailable {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "redis: expected account balance accid %d to exist", accid)
			available, ok := balanceView[accid].GetAvailableAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "redis: expected currency balance to exist")
			suite.Require().Equal(amount, available.String(), "redis: expected available amount to match for account %d currency %s", accid, currency)
		}
	}
	for accid, currencyMap := range expectedFrozen {
		for currency, amount := range currencyMap {
			_, ok := balanceView[accid]
			suite.Require().Truef(ok, "redis: expected account balance accid %d to exist", accid)
			frozen, ok := balanceView[accid].GetFrozenAmount(model.CurrencyCode(currency))
			suite.Require().True(ok, "redis: expected currency balance to exist")
			suite.Require().Equal(amount, frozen.String(), "redis: expected frozen amount to match for account %d currency %s", accid, currency)
		}
	}
}

func (suite *EventProcessorTestSuite) AssertEventStatus(expectedStatus model.ChangeLogStatus, events ...*eventpb.BalanceChangeEvent) {
	idemKeys := make([]string, 0, len(events))
	for _, event := range events {
		idemKeys = append(idemKeys, event.IdempotencyKey)
	}
	eventStatus, err := suite.DBRepo.GetIdempotencyKeysStatus(suite.TestInstance.Ctx, idemKeys, 0)
	suite.Require().NoError(err, "failed to list balance change logs by event IDs")
	suite.Require().Equal(len(events), len(eventStatus), "expected event status count to match")
	for _, event := range events {
		status, ok := eventStatus[event.IdempotencyKey]
		suite.Require().Truef(ok, "expected event status to exist for event %s", event.IdempotencyKey)
		suite.Require().Equalf(expectedStatus, status, "expected event status to match for event %s", event.IdempotencyKey)
	}

	eventStatus, err = suite.CacheRepo.GetIdempotencyKeysStatus(suite.TestInstance.Ctx, idemKeys, 0)
	suite.Require().NoError(err, "failed to list balance change logs by event IDs from cache")
	suite.Require().Equal(len(events), len(eventStatus), "expected event status count to match in cache")
	for _, event := range events {
		status, ok := eventStatus[event.IdempotencyKey]
		suite.Require().Truef(ok, "cache: expected event status to exist for event %s", event.IdempotencyKey)
		suite.Require().Equalf(expectedStatus, status, "cache: expected event status to match for event %s", event.IdempotencyKey)
	}
}

func (suite *EventProcessorTestSuite) ProcessEvents(events ...*eventpb.BalanceChangeEvent) {
	msgs := make([]mq.ConsumedMessage, 0, len(events))
	changeLogs := make([]*model.BalanceChangeLog, 0, len(events))
	for _, event := range events {
		shardID, err := suite.DBRepo.GetAccountShardID(suite.TestInstance.Ctx, []int64{event.AccountId})
		suite.Require().NoError(err)
		event.AccountShardId = shardID[event.AccountId]

		msg, err := factory.EventToMQMessage(event)
		suite.Require().NoError(err, "failed to convert event to mq message")
		msgs = append(msgs, msg)
		changeLog, err := factory.EventToChangeLog(event)
		suite.Require().NoError(err, "failed to convert event to change log")
		changeLogs = append(changeLogs, changeLog...)
		ok, err := suite.RedisRepo.SetIdemKeyIfNotExists(suite.TestInstance.Ctx, event.IdempotencyKey, 24*time.Hour)
		suite.Require().NoError(err, "failed to set idempotency key in redis")
		suite.Require().Truef(ok, "expected idempotency key to not exist before processing: %s", event.IdempotencyKey)
	}
	_, err := suite.DBRepo.InsertBalanceChangeLogs(suite.TestInstance.Ctx, changeLogs)
	suite.Require().NoError(err, "failed to insert balance change logs")

	err = suite.EventProcessor.ProcessEvents(suite.TestInstance.Ctx, msgs)
	suite.Require().NoError(err, "failed to process messages")
	err = suite.PersistentWorker.DoNowAndWait(suite.TestInstance.Ctx)
	suite.Require().NoError(err, "failed to do now and wait")
}
