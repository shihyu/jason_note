package cachedao

import (
	"context"
	"fmt"

	"github.com/allegro/bigcache/v3"
	"github.com/vmihailenco/msgpack/v5"
	"github.com/vx416/axs/pkg/model"
)

func (dao CacheDao) BatchSetAccountBalances(ctx context.Context, accountBalances map[int64]*model.ReadAccount) error {
	for _, readAccount := range accountBalances {
		for currency, balance := range readAccount.AccountBalancesMap {
			cacheKey := dao.getAccountBalanceCacheKey(readAccount.AccountID, string(currency))
			data, err := msgpack.Marshal(balance)
			if err != nil {
				return err
			}
			err = dao.userBalanceCache.Set(cacheKey, data)
			if err != nil {
				return err
			}
		}
	}
	return nil
}

func (dao CacheDao) applyAccountBalancesChange(ctx context.Context, accountBalance map[int64]*model.WriteAccount) error {
	readAccountMap := make(map[int64]*model.ReadAccount)
	for _, writeAccount := range accountBalance {
		for currency, writeBalance := range writeAccount.BalanceChangesMap {
			readAccountBalance, err := dao.getAccountBalance(writeAccount.AccountID, string(currency))
			if err != nil {
				if err == bigcache.ErrEntryNotFound {
					if writeBalance.AvailableDelta.IsNegative() || writeBalance.FrozenDelta.IsNegative() {
						return fmt.Errorf("balance insufficient (not found) for account %d currency %s", writeAccount.AccountID, currency)
					}
					readAccountBalance = &model.AccountBalance{
						AccountID:    writeAccount.AccountID,
						UserID:       writeAccount.UserID,
						ShardID:      writeAccount.ShardID,
						CurrencyCode: currency,
						Available:    writeBalance.AvailableDelta,
						Frozen:       writeBalance.FrozenDelta,
					}
				} else {
					return err
				}
			}
			if _, exists := readAccountMap[writeAccount.AccountID]; !exists {
				readAccountMap[writeAccount.AccountID] = model.NewReadAccount(writeAccount.AccountID, writeAccount.UserID, writeAccount.ShardID)
			}
			readAccountMap[writeAccount.AccountID].AddCurrencyBalance(currency, readAccountBalance.Available, readAccountBalance.Frozen, false)
			err = readAccountMap[writeAccount.AccountID].ApplyChange(currency, writeBalance.AvailableDelta, writeBalance.FrozenDelta)
			if err != nil {
				return err
			}

		}
	}

	return dao.BatchSetAccountBalances(ctx, readAccountMap)
}

func (dao CacheDao) ApplyAccountBalanceChanges(ctx context.Context, writeAccounts map[int64]*model.WriteAccount, logs []*model.EventApplyResult) error {
	for _, log := range logs {
		status, err := dao.getIdemKeyStatus(log.IdempotencyKey)
		if err != nil {
			return err
		}
		if status != model.ChangeLogStatusInit {
			return fmt.Errorf("idempotency key %s status is not applied: %d", log.IdempotencyKey, status)
		}
	}

	err := dao.applyAccountBalancesChange(ctx, writeAccounts)
	if err != nil {
		return err
	}
	idemKey := map[string]struct{}{}
	for _, log := range logs {
		if _, exists := idemKey[log.IdempotencyKey]; exists {
			continue
		}
		idemKey[log.IdempotencyKey] = struct{}{}
		err := dao.updateIdemKeyStatus(log.IdempotencyKey, log.Status)
		if err != nil {
			return err
		}
	}
	return nil
}
