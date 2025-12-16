package processor

import (
	"context"
	"fmt"
	"sync"
	"sync/atomic"
	"time"

	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/mq"
	"github.com/vx416/axs/pkg/service/svcerr"
	"github.com/vx416/axs/pkg/utils"
)

func NewPersistentWorker(dbRepo domain.DBRepository, redisRepo domain.RedisRepository, le *LeaderElector) *PersistentWorker {
	ctx, cancel := context.WithCancel(context.Background())
	return &PersistentWorker{
		dbRepo:            dbRepo,
		redisRepo:         redisRepo,
		ctx:               ctx,
		cancel:            cancel,
		doNow:             make(chan struct{}, 100),
		latestApplyResult: map[int32]*ApplyResult{},
		LeaderElector:     le,
	}
}

type PersistentWorker struct {
	*LeaderElector
	redisRepo         domain.RedisRepository
	dbRepo            domain.DBRepository
	ctx               context.Context
	cancel            context.CancelFunc
	doNow             chan struct{}
	latestApplyResult map[int32]*ApplyResult
	cnt               atomic.Int32
	lock              sync.Mutex
	wg                sync.WaitGroup
}

type ApplyResult struct {
	ShardID         int32
	WriteAccounts   map[int64]*model.WriteAccount
	Logs            []*model.EventApplyResult
	NewEvents       []*DecodedEvent
	ProcessedEvents []*DecodedEvent
	Ctx             context.Context
}

func (ap *ApplyResult) Merge(other *ApplyResult) {
	for accountID, writeAccount := range other.WriteAccounts {
		if existingAccount, exists := ap.WriteAccounts[accountID]; exists {
			for currency, change := range writeAccount.BalanceChangesMap {
				if _, exists := existingAccount.BalanceChangesMap[currency]; exists {
					existingAccount.ApplyChange(change.CurrencyCode, change.AvailableDelta, change.FrozenDelta, change.NotExist)
				} else {
					existingAccount.BalanceChangesMap[currency] = change
				}
			}
			ap.WriteAccounts[accountID] = existingAccount
		} else {
			ap.WriteAccounts[accountID] = writeAccount
		}
	}
	ap.Logs = append(ap.Logs, other.Logs...)
	ap.NewEvents = append(ap.NewEvents, other.NewEvents...)
	ap.ProcessedEvents = append(ap.ProcessedEvents, other.ProcessedEvents...)
}

func (pw *PersistentWorker) EnqueueResult(ctx context.Context, result *ApplyResult) {
	pw.lock.Lock()
	if val, ok := pw.latestApplyResult[result.ShardID]; !ok || val == nil {
		pw.latestApplyResult[result.ShardID] = result
	} else {
		pw.latestApplyResult[result.ShardID].Merge(result)
	}
	pw.lock.Unlock()
	cnt := pw.cnt.Add(1)
	if cnt >= 10 {
		pw.doNow <- struct{}{}
	}
}

func (pw *PersistentWorker) Start() {
	pw.wg.Add(1)
	defer pw.wg.Done()
	ticker := time.NewTicker(3 * time.Second)
	defer ticker.Stop()
	for {
		select {
		case <-pw.ctx.Done():
			return
		case <-pw.doNow:
			results := pw.DequeueResult()
			for _, result := range results {
				ctx, cancel := context.WithTimeout(context.WithoutCancel(result.Ctx), 5*time.Second)
				err := pw.PersistentApplyResult(ctx, result)
				if err != nil {
					pw.EnqueueResult(ctx, result)
					logger.GetLogger(ctx).Error().Err(err).Msg("failed to persist apply results")
				}
				cancel()
			}
		case <-ticker.C:
			results := pw.DequeueResult()
			for _, result := range results {
				ctx, cancel := context.WithTimeout(context.WithoutCancel(result.Ctx), 5*time.Second)
				err := pw.PersistentApplyResult(ctx, result)
				if err != nil {
					pw.EnqueueResult(ctx, result)
					logger.GetLogger(ctx).Error().Err(err).Msg("failed to persist apply results")
				}
				cancel()
			}
		}
	}
}

func (pw *PersistentWorker) GracefulStop() {
	pw.Stop()
	results := pw.DequeueResult()
	for _, result := range results {
		ctx, cancel := context.WithTimeout(context.WithoutCancel(result.Ctx), 5*time.Second)
		err := pw.PersistentApplyResult(ctx, result)
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Msg("failed to persist apply results")
		}
		cancel()
	}
}

func (pw *PersistentWorker) Stop() {
	pw.cancel()
	pw.wg.Wait()
}

func (pw *PersistentWorker) DoNowAndWait(ctx context.Context) error {
	result := pw.DequeueResult()
	for _, result := range result {
		ctx := context.WithoutCancel(ctx)
		err := pw.PersistentApplyResult(ctx, result)
		if err != nil {
			return err
		}
	}
	return nil
}

func (pw *PersistentWorker) DequeueResult() []*ApplyResult {
	results := make([]*ApplyResult, 0)
	pw.lock.Lock()
	for key, result := range pw.latestApplyResult {
		if result != nil {
			results = append(results, result)
		}
		delete(pw.latestApplyResult, key)
	}
	pw.lock.Unlock()
	pw.cnt.Store(0)
	return results
}

func (pw *PersistentWorker) PersistentApplyResult(ctx context.Context, result *ApplyResult) error {
	if result == nil {
		return nil
	}
	if !pw.IsLeader() {
		return fmt.Errorf("not leader, cannot persist apply result")
	}
	logger.GetLogger(ctx).Info().Int("new_events", len(result.NewEvents)).Int("processed_events", len(result.ProcessedEvents)).Int("writeAccounts", len(result.WriteAccounts)).Msg("persisting apply results")
	var (
		err error
	)

	maxOffset := int64(-1)
	var maxOffsetMsg mq.ConsumedMessage
	for _, de := range result.NewEvents {
		if de.Msg.GetOffset() > maxOffset {
			maxOffset = de.Msg.GetOffset()
			maxOffsetMsg = de.Msg
		}
	}
	for _, de := range result.ProcessedEvents {
		if de.Msg.GetOffset() > maxOffset {
			maxOffset = de.Msg.GetOffset()
			maxOffsetMsg = de.Msg
		}
	}
	if maxOffsetMsg == nil {
		return fmt.Errorf("no events to persist offset")
	}
	err = maxOffsetMsg.Commit()
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to commit offset after persisting apply results")
	}
	logger.GetLogger(ctx).Info().Int64("committed_offset", maxOffset).Msg("committed offset after persisting apply results")
	partitionOffset := &model.PartitionLeaderLock{
		Topic:        model.BalanceChangeEventTopic,
		Partition:    pw.LeaderElector.leaderPartition,
		CommitOffset: maxOffset,
		UpdaterSvcID: pw.LeaderElector.leaderSvcID,
		LeaderSvcID:  pw.LeaderElector.leaderSvcID,
		FencingToken: pw.LeaderElector.fencingToken,
	}

	retryErr := utils.Retry(func() (bool, error) {
		if len(result.WriteAccounts) == 0 {
			return false, nil
		}
		err = pw.dbRepo.ApplyAccountBalanceChanges(ctx, result.WriteAccounts, result.Logs, partitionOffset)
		if err != nil {
			if err.Error() == "balance insufficient" {
				// TODO: stop consumer from committing offsets
				return false, err
			}
			if err.Error() == "idempotency key conflict" {
				// TODO: stop consumer from committing offsets
				return false, err
			}
			return true, err
		}
		return false, nil
	})
	if retryErr != nil {
		if svcerr.IsLeaderChangeError(retryErr) {
			logger.GetLogger(ctx).Warn().Err(retryErr).Msg("leader changed during persisting apply results, stopping persistent worker")
			pw.Stop()
			pw.LeaderElector.ClearLeader()
			return nil
		}
		return retryErr
	}

	setRedisErr := utils.Retry(func() (keepRetry bool, err error) {
		partition, err := infra.GetConsumerOrdinal()
		if err != nil {
			return false, err
		}
		err = pw.redisRepo.SyncEventStatus(ctx, result.Logs, int32(partition))
		if err != nil {
			return true, err
		}
		return false, nil
	})
	if setRedisErr != nil {
		logger.GetLogger(ctx).Error().Err(setRedisErr).Msg("failed to sync event apply results to redis cache after retries")
	}

	return nil
}
