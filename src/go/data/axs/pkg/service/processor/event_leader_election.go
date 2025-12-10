package processor

import (
	"context"
	"sync/atomic"
	"time"

	"github.com/vx416/axs/pkg/infra"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
)

type LeaderElector struct {
	leaderTimestamp int64
	leaderPartition int32
	leaderSvcID     string
	fencingToken    int64
	topic           string
}

func (le *LeaderElector) GetFencingToken() int64 {
	return le.fencingToken
}

func (le *LeaderElector) GetLeaderSvcID() string {
	return le.leaderSvcID
}

func (le *LeaderElector) GetPartition() int32 {
	return le.leaderPartition
}

func (le *LeaderElector) IsLeader() bool {
	return time.Now().UnixMilli()-atomic.LoadInt64(&le.leaderTimestamp) <= int64(model.LeaderTTLSecond)*1000
}

func (le *LeaderElector) SetLeader() {
	atomic.StoreInt64(&le.leaderTimestamp, time.Now().UnixMilli())
}

func (le *LeaderElector) ClearLeader() {
	atomic.StoreInt64(&le.leaderTimestamp, 0)
}

func (ep *EventProcessor) TryToBecomeLeader(ctx context.Context) (partition int64, offset int64, ok bool) {
	svcName, err := infra.GetSvcID()
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to get svc id")
		return 0, 0, false
	}
	partition, err = infra.GetConsumerOrdinal()
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("can't get partition")
		return 0, 0, false
	}
	if ep.LeaderElector == nil {
		logger.GetLogger(ctx).Error().Msg("leader elector is not init")
		return 0, 0, false
	}
	ep.LeaderElector.topic = model.BalanceChangeEventTopic
	ep.LeaderElector.leaderPartition = int32(partition)
	ep.LeaderElector.leaderSvcID = svcName

	leaderLockData, ok, err := ep.DBRepo.AcquirePartitionLeaderLock(ctx, ep.LeaderElector.topic, ep.LeaderElector.leaderPartition, ep.LeaderElector.leaderSvcID)
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to acquire leader lock")
	}
	if ok {
		err := ep.becomeLeader(&leaderLockData)
		if err != nil {
			logger.GetLogger(ctx).Error().Err(err).Msg("failed to start leader duties")
			return 0, 0, false
		}
		return partition, leaderLockData.CommitOffset, true
	}

	logger.GetLogger(ctx).Info().Msg("leader lock is held by another instance, will retry to acquire")
	timer := time.NewTicker(500 * time.Millisecond)
	defer timer.Stop()
	for {
		select {
		case <-ep.closeCtx.Done():
			return 0, 0, false
		case <-timer.C:
			newCtx, cancel := context.WithTimeout(context.Background(), 200*time.Millisecond)
			leaderLockData, ok, err := ep.DBRepo.AcquirePartitionLeaderLock(newCtx, ep.LeaderElector.topic, ep.LeaderElector.leaderPartition, ep.LeaderElector.leaderSvcID)
			cancel()
			if err != nil {
				logger.GetLogger(ctx).Error().Err(err).Msg("failed to acquire leader lock")
				continue
			}
			if ok {
				logger.GetLogger(ctx).Info().Msg("successfully acquired leader lock")
				ep.becomeLeader(&leaderLockData)
				return partition, leaderLockData.CommitOffset, true
			} else {
				logger.GetLogger(ctx).Debug().Msg("leader lock is held by another instance")
			}
		}
	}
}

func (ep *EventProcessor) becomeLeader(leaderLockData *model.PartitionLeaderLock) error {
	ctx := context.Background()
	timeoutCtx, cancel := context.WithTimeout(ctx, 2*time.Second)
	defer cancel()

	eventStatus, err := ep.RedisRepo.ListLatestEventStatus(timeoutCtx, int32(ep.LeaderElector.leaderPartition))
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to list latest event status for leader initialization")
		return err
	}
	err = ep.CacheRepo.SyncEventStatus(timeoutCtx, eventStatus)
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to sync latest event status to cache for leader initialization")
		return err
	}
	_, _, err = ep.DBRepo.CreateAndTruncateTempTables(timeoutCtx, int(ep.LeaderElector.leaderPartition))
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to create and truncate temp tables for leader initialization")
		return err
	}

	ep.LeaderElector.fencingToken = leaderLockData.FencingToken
	logger.GetLogger(ctx).Info().Msg("successfully acquired leader lock")
	ep.SetLeader()
	logger.SafeGo(func() {
		timerVal := time.Duration(time.Second*time.Duration(model.LeaderTTLSecond)) / 3
		timer := time.NewTicker(timerVal)
		defer timer.Stop()
		for {
			select {
			case <-ep.closeCtx.Done():
				logger.GetLogger(ctx).Info().Msg("stopping leader lock extension due to processor closure")
				return
			case <-timer.C:
				timeoutCtx, cancel := context.WithTimeout(ctx, timerVal/2)
				ok, err := ep.DBRepo.ExtendPartitionLeaderLock(timeoutCtx, ep.LeaderElector.topic, ep.LeaderElector.leaderPartition, ep.LeaderElector.leaderSvcID, int(ep.LeaderElector.fencingToken))
				cancel()
				if err != nil {
					logger.GetLogger(ctx).Error().Err(err).Msg("failed to extend leader lock")
					continue
				}
				if ok {
					logger.GetLogger(ctx).Debug().Msg("  extended leader lock")
					ep.SetLeader()
				} else {
					logger.GetLogger(ctx).Warn().Msg("lost leader lock to another instance")
					ep.CloseNow(ctx)
					return
				}
			}
		}
	})
	return nil
}

func (ep *EventProcessor) IsLeader() bool {
	return time.Now().UnixMilli()-atomic.LoadInt64(&ep.leaderTimestamp) <= (int64(model.LeaderTTLSecond)*1000 - 300)
}

func (ep *EventProcessor) SetLeader() {
	atomic.StoreInt64(&ep.leaderTimestamp, time.Now().UnixMilli())
}

func (ep *EventProcessor) ReleaseLeader(ctx context.Context) {
	if !ep.IsLeader() {
		logger.GetLogger(ctx).Info().Msg("not the leader, no need to release leader lock")
		return
	}

	ok, err := ep.DBRepo.ReleasePartitionLeaderLock(ctx, ep.LeaderElector.topic, ep.LeaderElector.leaderPartition, ep.LeaderElector.leaderSvcID, int(ep.LeaderElector.fencingToken))
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to release leader lock")
	} else if ok {
		logger.GetLogger(ctx).Info().Msg("leader lock released")
	} else {
		logger.GetLogger(ctx).Warn().Msg("leader lock not released, it may have been acquired by another instance")
	}
	ep.leaderTimestamp = 0
}
