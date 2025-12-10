package redisdao

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
	"github.com/vx416/axs/pkg/domain"
)

func NewRedisRepository(client redis.UniversalClient) (domain.RedisRepository, error) {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	batchSyncBalanceLuaScript := NewBatchSyncBalanceLuaScript()
	err := batchSyncBalanceLuaScript.Load(ctx, client).Err()
	if err != nil {
		return &RedisDao{}, err
	}
	acquireLeaderLockLuaScript := NewAcquireLeaderLockLuaScript()
	err = acquireLeaderLockLuaScript.Load(ctx, client).Err()
	if err != nil {
		return &RedisDao{}, err
	}
	safeReleaseLeaderLockLuaScript := NewSafeReleaseLeaderLockLuaScript()
	err = safeReleaseLeaderLockLuaScript.Load(ctx, client).Err()
	if err != nil {
		return &RedisDao{}, err
	}

	return &RedisDao{
		Client:                         client,
		BatchSyncBalanceLuaScript:      batchSyncBalanceLuaScript,
		AcquireLeaderLockLuaScript:     acquireLeaderLockLuaScript,
		SafeReleaseLeaderLockLuaScript: safeReleaseLeaderLockLuaScript,
	}, nil
}

type RedisDao struct {
	Client                         redis.UniversalClient
	BatchSyncBalanceLuaScript      *redis.Script
	AcquireLeaderLockLuaScript     *redis.Script
	SafeReleaseLeaderLockLuaScript *redis.Script
}
