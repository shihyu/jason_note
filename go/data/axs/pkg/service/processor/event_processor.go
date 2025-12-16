package processor

import (
	"context"
	"sync/atomic"
	"time"

	"github.com/vx416/axs/pb/eventpb"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/service/svcerr"
	"github.com/vx416/axs/pkg/utils"
	"go.uber.org/fx"
)

type Params struct {
	fx.In
	DBRepo     domain.DBRepository
	RedisRepo  domain.RedisRepository
	CacheRepo  domain.CacheRepository
	Producer   mq.Producer
	WorkerPool utils.WorkerPool
}

func NewEventProcessor(params Params) (*EventProcessor, error) {
	le := &LeaderElector{}
	pw := NewPersistentWorker(params.DBRepo, params.RedisRepo, le)
	go pw.Start()
	closeCtx, closeFunc := context.WithCancel(context.Background())

	return &EventProcessor{
		LeaderElector:    le,
		CacheRepo:        params.CacheRepo,
		DBRepo:           params.DBRepo,
		RedisRepo:        params.RedisRepo,
		EventValidator:   EventValidator{cacheRepo: params.CacheRepo},
		ChangeApplier:    ChangeApplier{DBRepo: params.DBRepo, RedisRepo: params.RedisRepo, CacheRepo: params.CacheRepo},
		WorkerPool:       params.WorkerPool,
		PersistentWorker: pw,
		ResultPublisher: ResultPublisher{
			Producer: params.Producer,
		},
		closeCtx:  closeCtx,
		closeFunc: closeFunc,
	}, nil
}

type EventProcessor struct {
	isClose int32
	*LeaderElector
	closeCtx  context.Context
	closeFunc context.CancelFunc

	CacheRepo        domain.CacheRepository
	DBRepo           domain.DBRepository
	RedisRepo        domain.RedisRepository
	EventValidator   EventValidator
	ChangeApplier    ChangeApplier
	PersistentWorker *PersistentWorker
	ResultPublisher  ResultPublisher
	WorkerPool       utils.WorkerPool
}

func (ep *EventProcessor) ProcessEvents(ctx context.Context, msgs []mq.ConsumedMessage) error {
	if !ep.IsLeader() {
		ep.CloseNow(ctx)
		logger.GetLogger(ctx).Warn().Msgf("not the leader anymore, stop processing events, leaderTimestamp: %d", ep.leaderTimestamp)
		return svcerr.StopConsumingError
	}

	if ep.IsClosed() {
		logger.GetLogger(ctx).Warn().Msg("event processor is closed, stop processing events")
		return svcerr.StopConsumingError
	}

	firstStartTime := time.Now()
	start := time.Now()
	stats := model.StressTestStats{
		TotalMessages:    len(msgs),
		StartProcessMsec: start.UnixMilli(),
	}
	ctx = logger.GetLogger(ctx).With().Int("msg_count", len(msgs)).Logger().WithContext(ctx)
	logger.GetLogger(ctx).Info().Msg("start processing events")
	shardIDEvents, invalidEventKeys, err := ep.EventValidator.DecodeEventsAndGroupByShardID(ctx, msgs)
	if err != nil {
		return err
	}
	stats.DecodeCostMicroSec = int(time.Since(start).Microseconds())

	logger.GetLogger(ctx).Debug().Int("shards", len(shardIDEvents)).Int("invalidEventsCnt", len(invalidEventKeys)).Msg("decoded and grouped events by shard ID")
	ep.updateInvalidEvents(ctx, invalidEventKeys)
	if len(msgs) > 0 && infra.GetConfig().Server.StressTestMode {
		start := time.Now()
		delayCnt, err := msgs[len(msgs)-1].GetMessageDelayCount()
		if err == nil {
			stats.DelayCount = int(delayCnt)
		} else {
			logger.GetLogger(ctx).Error().Err(err).Msg("failed to get message delay count from last message")
		}
		if time.Since(start).Microseconds() > 500 {
			logger.GetLogger(ctx).Warn().Int64("process_cost_microsec", time.Since(start).Microseconds()).Msg("decoding events took too long")
		}
	}

	epoch := time.Now().UnixMicro()
	for shardID, groupEvents := range shardIDEvents {
		if len(groupEvents.NewEvents) > 0 {
			stats.EventCreatedMsec = groupEvents.NewEvents[0].Event.CreatedMsec
		}
		start = time.Now()
		stats.TotalEventsProcessed += len(groupEvents.ProcessedEvents)
		logger.GetLogger(ctx).Info().Int("shardID", int(shardID)).Int("new_events", len(groupEvents.NewEvents)).Int("processed_events", len(groupEvents.ProcessedEvents)).Msg("processing events for shard")
		writeAccount, changedReadBalance, eventApplyResults, err := ep.ChangeApplier.ApplyChanges(ctx, groupEvents.NewEvents)
		if err != nil {
			return err
		}
		stats.ApplyCostMicroSec += int(time.Since(start).Microseconds())
		start = time.Now()
		ep.SyncBalanceToRedisCache(ctx, changedReadBalance, epoch)
		applyResult := &ApplyResult{
			ShardID:         shardID,
			WriteAccounts:   writeAccount,
			NewEvents:       groupEvents.NewEvents,
			ProcessedEvents: groupEvents.ProcessedEvents,
			Logs:            eventApplyResults,
			Ctx:             ctx,
		}
		ep.PersistentWorker.EnqueueResult(ctx, applyResult)
		ep.PublishApplyResults(ctx, changedReadBalance, groupEvents, eventApplyResults)
		stats.AsyncCostMicroSec += int(time.Since(start).Microseconds())
	}

	stats.TotalProcessCostMicroSec = int(time.Since(firstStartTime).Microseconds())
	if infra.GetConfig().Server.StressTestMode {
		ep.ResultPublisher.PublishStressTestStats(ctx, &stats)
	}
	return nil
}

func (ep *EventProcessor) updateInvalidEvents(ctx context.Context, invalidFormatEvents []*eventpb.BalanceChangeEvent) {
	if len(invalidFormatEvents) == 0 {
		return
	}
	logger.GetLogger(ctx).Warn().Int("invalid_event_count", len(invalidFormatEvents)).Msg("updating invalid format events status to reject")
	shardIDIdemKeys := make(map[int32][]string)
	for _, event := range invalidFormatEvents {
		if _, ok := shardIDIdemKeys[event.AccountShardId]; !ok {
			shardIDIdemKeys[event.AccountShardId] = make([]string, 0)
		}
		shardIDIdemKeys[event.AccountShardId] = append(shardIDIdemKeys[event.AccountShardId], event.IdempotencyKey)
	}
	for shardID, idemKeys := range shardIDIdemKeys {
		err := ep.DBRepo.BatchUpdateIdempotencyKeysStatusToReject(ctx, idemKeys, shardID, model.ChangeLogStatusCannotApplied, "invalid event format")
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Int("shardID", int(shardID)).Int("invalid_event_count", len(idemKeys)).Msg("failed to update invalid events status")
		}
		err = ep.CacheRepo.BatchUpdateIdempotencyKeysStatusToReject(ctx, idemKeys, shardID, model.ChangeLogStatusCannotApplied, "invalid event format")
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Int("shardID", int(shardID)).Int("invalid_event_count", len(idemKeys)).Msg("failed to update invalid events status in redis")
		}
	}
}

func (ep *EventProcessor) ProcessEventsErr(ctx context.Context, msgs []mq.ConsumedMessage, err error) {
	for _, msg := range msgs {
		logger.GetLogger(ctx).Error().Err(err).Msgf("failed message topic: %s partition: %d offset: %d", msg.GetTopic(), msg.GetPartition(), msg.GetOffset())
	}
}

func (ep *EventProcessor) SyncBalanceToRedisCache(ctx context.Context, changedAccountBalance map[int64]*model.ReadAccount, epoch int64) {
	ep.WorkerPool.PushJob(ctx, utils.FuncJob(func(ctx context.Context) error {
		err := ep.RedisRepo.SyncAccountBalances(ctx, changedAccountBalance, epoch)
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Msg("failed to sync account balances to redis cache")
			return err
		}
		return nil
	}))
}

func (ep *EventProcessor) PublishApplyResults(ctx context.Context, changedReadBalance map[int64]*model.ReadAccount, batchEvent *BatchEvents, eventResults []*model.EventApplyResult) {
	ep.WorkerPool.PushJob(ctx, utils.FuncJob(func(ctx context.Context) error {
		ep.ResultPublisher.PublishResults(ctx, changedReadBalance, batchEvent, eventResults)
		return nil
	}))
}

func (ep *EventProcessor) Close(ctx context.Context) {
	if !atomic.CompareAndSwapInt32(&ep.isClose, 0, 1) {
		return
	}
	ep.PersistentWorker.GracefulStop()
	ep.WorkerPool.GracefulShutdown(3 * time.Second)
	ep.closeFunc()
	ep.ReleaseLeader(ctx)
}

func (ep *EventProcessor) IsClosed() bool {
	return atomic.LoadInt32(&ep.isClose) == 1
}

func (ep *EventProcessor) CloseNow(ctx context.Context) {
	if !atomic.CompareAndSwapInt32(&ep.isClose, 0, 1) {
		return
	}
	ep.PersistentWorker.Stop()
	ep.closeFunc()
	ep.ReleaseLeader(ctx)
}
