package redisdao

import (
	"context"
	"fmt"
	"strconv"
	"strings"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
)

const (
	maxEventSize = 10000
)

func (dao *RedisDao) ListLatestEventStatus(ctx context.Context, shardID int32) (map[string]model.ChangeLogStatus, error) {
	result, err := dao.Client.LRange(ctx, dao.getEventStatusCacheKey(shardID), 0, -1).Result()
	if err != nil {
		return nil, fmt.Errorf("failed to LRange event status from redis: %w", err)
	}

	eventStatus := make(map[string]model.ChangeLogStatus, len(result))
	for _, item := range result {
		parts := strings.Split(item, ":")
		if len(parts) != 2 {
			logger.GetLogger(ctx).Warn().Msgf("invalid event status format in redis: %s", item)
			continue
		}
		key := parts[0]
		statusInt, err := strconv.Atoi(parts[1])
		if err != nil {
			logger.GetLogger(ctx).Warn().Err(err).Msgf("invalid event status value in redis: %s", item)
			continue
		}
		eventStatus[key] = model.ChangeLogStatus(statusInt)
	}

	return eventStatus, nil
}

func (dao *RedisDao) SyncEventStatus(ctx context.Context, logs []*model.EventApplyResult, partition int32) error {
	if len(logs) == 0 {
		return nil
	}

	logsData := make([]any, 0, len(logs)*3)
	for _, log := range logs {
		logsData = append(logsData, log.IdempotencyKey+":"+strconv.Itoa(int(log.Status)))
	}

	_, err := dao.Client.TxPipelined(ctx, func(p redis.Pipeliner) error {
		err := p.LPush(ctx, dao.getEventStatusCacheKey(partition), logsData...).Err()
		if err != nil {
			return fmt.Errorf("failed to LPush event status to redis: %w", err)
		}

		err = p.LTrim(ctx, dao.getEventStatusCacheKey(partition), 0, maxEventSize-1).Err()
		if err != nil {
			return fmt.Errorf("failed to LTrim event status in redis: %w", err)
		}
		return nil
	})

	return err
}

func (dao *RedisDao) getEventStatusCacheKey(shardID int32) string {
	return fmt.Sprintf("e:status:{%d}", shardID)
}

const (
	idemKeyPrefix = "e:idem:"
)

func (dao *RedisDao) SetIdemKeyIfNotExists(ctx context.Context, idemKey string, ttl time.Duration) (bool, error) {
	set, err := dao.Client.SetNX(ctx, dao.getIdemKeyCacheKey(idemKey), "1", ttl).Result()
	if err != nil {
		return false, fmt.Errorf("failed to set idem key in redis: %w", err)
	}
	return set, nil
}

func (dao *RedisDao) getIdemKeyCacheKey(idemKey string) string {
	return idemKeyPrefix + idemKey
}
