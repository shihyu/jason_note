package redisdao

import (
	"context"
	"fmt"

	"github.com/vx416/axs/pkg/model"
)

func (dao *RedisDao) SyncAccountBalances(ctx context.Context, accountBalance map[int64]*model.ReadAccount, epoch int64) error {
	if len(accountBalance) == 0 {
		return nil
	}
	keys := make([]string, 0, len(accountBalance))
	args := make([]any, 0, len(accountBalance)*5) // 每個帳戶至少 5 個參數

	for _, readAccount := range accountBalance {
		keys = append(keys, dao.getSyncAccCacheKey(readAccount.ShardID, readAccount.AccountID))
		args = append(args, readAccount.UserID)
		args = append(args, readAccount.ShardID)
		args = append(args, len(readAccount.AccountBalancesMap)) // 每個貨幣 4 個參數
		for _, balance := range readAccount.AccountBalancesMap {
			args = append(args, string(balance.CurrencyCode))
			args = append(args, balance.Available.String())
			args = append(args, balance.Frozen.String())
			args = append(args, epoch)
		}
	}

	_, err := dao.BatchSyncBalanceLuaScript.Run(ctx, dao.Client, keys, args...).Result()
	if err != nil {
		return fmt.Errorf("failed to sync account balances: %w", err)
	}
	return nil
}

func (dao *RedisDao) getSyncAccCacheKey(shardID int32, accountID int64) string {
	return fmt.Sprintf("a:{%d}:%d", shardID, accountID)
}
