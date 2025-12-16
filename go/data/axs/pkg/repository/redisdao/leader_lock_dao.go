package redisdao

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

func NewAcquireLeaderLockLuaScript() *redis.Script {
	return redis.NewScript(acquireLeaderLockLuaScript)
}

var (
	acquireLeaderLockLuaScript = `
--[[
Redis Lua Script for acquiring a leader lock.

KEYS:
  1) lock key

ARGV:
  1) lock value
  2) lock TTL in seconds
]]--

local lockKey = KEYS[1]
local lockValue = ARGV[1]
local lockTTL = tonumber(ARGV[2])

-- Try to get the lock
local result = redis.call("GET", lockKey)
if not result then
    -- Lock is available, set it
    redis.call("SET", lockKey, lockValue, "EX", lockTTL)
    return 1

elseif result == lockValue then
    -- Lock is already held by this owner, refresh TTL
    redis.call("EXPIRE", lockKey, lockTTL)
    return 1
end

-- Lock is held by someone else
return 0
`
)

func NewSafeReleaseLeaderLockLuaScript() *redis.Script {
	return redis.NewScript(safeReleaseLeaderLockLuaScript)
}

var (
	safeReleaseLeaderLockLuaScript = `
--[[
Redis Lua Script for safely releasing a leader lock.

KEYS:
  1) lock key

ARGV:
  1) lock value
]]--

local lockKey = KEYS[1]
local lockValue = ARGV[1]

-- Check if the lock is held by this owner
local result = redis.call("GET", lockKey)
if result == lockValue then
	-- Lock is held by this owner, delete it
	redis.call("DEL", lockKey)
	return 1
end
-- Lock is held by someone else or does not exist
return 0
`
)

func (dao *RedisDao) AcquireAndExtendLeaderLock(ctx context.Context, lockKey, lockValue string, ttlSeconds int) (bool, error) {
	result, err := dao.AcquireLeaderLockLuaScript.Eval(ctx, dao.Client, []string{lockKey}, lockValue, ttlSeconds).Int()
	if err != nil {
		return false, err
	}
	return result == 1, nil
}

func (dao *RedisDao) SafeReleaseLeaderLock(ctx context.Context, lockKey, lockValue string) (bool, error) {
	result, err := dao.Client.Eval(ctx, safeReleaseLeaderLockLuaScript, []string{lockKey}, lockValue).Int()
	if err != nil {
		return false, err
	}
	return result == 1, nil
}

func (dao *RedisDao) AcquireLeaderLock(ctx context.Context, lockKey, lockValue string, ttlSeconds int) (bool, error) {
	return dao.Client.SetNX(ctx, lockKey, lockValue, time.Duration(ttlSeconds)*time.Second).Result()
}
