package redisdao

import "github.com/redis/go-redis/v9"

func NewBatchSyncBalanceLuaScript() *redis.Script {
	return redis.NewScript(batchSyncBalanceLuaScript)
}

var batchSyncBalanceLuaScript = `
--[[
Redis Lua Script for applying concurrent balance updates
using Last-Write-Win (LWW) for each currency per user.

KEYS:
  1) user balance hash key ("aid:{shard_id}")

ARGV (repeating blocks):
  Each update block structure:
    1) uid                  -- user ID (string or integer)
    2) shard_id             -- shard ID this user belongs to
    3) currency_update_cnt  -- number of currency updates in this block

    For each currency update:
      4) currency           -- currency code
      5) new_available      -- new available amount
      6) new_frozen         -- new frozen amount
      7) epoch              -- µs timestamp

This script writes:
  - uid                      => stored as field "uid"
  - shard_id                 => stored as field "shard_id"
  - currency fields:
       currency:a
       currency:f
       currency:epoch
Only currency fields obey LWW logic.
uid + shard_id are always written (metadata).
]]--


local argv_i = 1
local argv_len = #ARGV
local key_i = 1

while argv_i <= argv_len do
    -- Extract block metadata
    local key = KEYS[key_i]
    key_i = key_i + 1
    local uid       = ARGV[argv_i];     
    argv_i = argv_i + 1;
    local shard_id  = ARGV[argv_i];     
    argv_i = argv_i + 1;
    local cnt       = tonumber(ARGV[argv_i]); 
    argv_i = argv_i + 1;

    -- Write uid and shard_id metadata (always overwrite)
    redis.call("HSET", key, "uid", uid)
    redis.call("HSET", key, "shard_id", shard_id)

    -- Process each currency update in this block
    for _ = 1, cnt do
        local currency     = ARGV[argv_i];     
        argv_i = argv_i + 1
        local new_available = ARGV[argv_i];    
        argv_i = argv_i + 1
        local new_frozen   = ARGV[argv_i];     
        argv_i = argv_i + 1
        local new_epoch    = tonumber(ARGV[argv_i]); 
        argv_i = argv_i + 1

        local avail_key = currency .. ":a"
        local frozen_key = currency .. ":f"
        local epoch_key  = currency .. ":epoch"

        -- read old epoch
        local old_epoch_str = redis.call("HGET", key, epoch_key)
        local old_epoch = old_epoch_str and tonumber(old_epoch_str) or nil

        -- LWW: apply update only if epoch is newer
        if old_epoch == nil or new_epoch > old_epoch then
            redis.call("HSET", key, avail_key, new_available)
            redis.call("HSET", key, frozen_key, new_frozen)
            redis.call("HSET", key, epoch_key, new_epoch)
        end
    end
end

return "OK"

`
