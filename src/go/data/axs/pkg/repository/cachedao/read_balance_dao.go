package cachedao

import (
	"context"

	"github.com/allegro/bigcache/v3"
	"github.com/shopspring/decimal"
	"github.com/vmihailenco/msgpack/v5"
	"github.com/vx416/axs/pkg/model"
)

func (dao CacheDao) ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error) {
	result := make(map[int64]*model.ReadAccount)
	notFoundFilters := make([]model.AccountBalanceFilter, 0, len(opts.AccountBalanceFilters))
	for _, filter := range opts.AccountBalanceFilters {
		accountBalance, err := dao.getAccountBalance(filter.AccountID, filter.CurrencyCode)
		if err != nil {
			if err == bigcache.ErrEntryNotFound {
				notFoundFilters = append(notFoundFilters, filter)
				continue
			} else {
				return nil, err
			}
		}
		readAccount, exists := result[filter.AccountID]
		if !exists {
			readAccount = model.NewReadAccount(accountBalance.AccountID, accountBalance.UserID, accountBalance.ShardID)
			result[filter.AccountID] = readAccount
		}
		readAccount.AddCurrencyBalance(accountBalance.CurrencyCode, accountBalance.Available, accountBalance.Frozen, false)
		result[filter.AccountID] = readAccount
	}

	for _, filter := range notFoundFilters {
		readAccount, exists := result[filter.AccountID]
		if !exists {
			// We don't have userID and shardID info here, set them to zero
			readAccount = model.NewReadAccount(filter.AccountID, 0, filter.ShardID)
			result[filter.AccountID] = readAccount
		}
		readAccount.AddCurrencyBalance(model.CurrencyCode(filter.CurrencyCode), decimal.Zero, decimal.Zero, true)
		result[filter.AccountID] = readAccount
	}
	return result, nil
}

func (dao CacheDao) getAccountBalanceCacheKey(accID int64, currencyCode string) string {
	return "ab_" + string(rune(accID)) + "_" + currencyCode
}

func (dao CacheDao) getAccountBalance(accID int64, currencyCode string) (*model.AccountBalance, error) {
	data, err := dao.userBalanceCache.Get(dao.getAccountBalanceCacheKey(accID, currencyCode))
	if err != nil {
		return nil, err
	}
	accountBalance := &model.AccountBalance{}
	err = msgpack.Unmarshal(data, &accountBalance)
	if err != nil {
		return nil, err
	}
	return accountBalance, nil
}
