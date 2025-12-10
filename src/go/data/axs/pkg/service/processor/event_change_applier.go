package processor

import (
	"context"
	"maps"

	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/utils"
)

type ChangeApplier struct {
	DBRepo    domain.DBRepository
	RedisRepo domain.RedisRepository
	CacheRepo domain.CacheRepository
}

func (ca ChangeApplier) ApplyChanges(ctx context.Context, events []*DecodedEvent) (map[int64]*model.WriteAccount, map[int64]*model.ReadAccount, []*model.EventApplyResult, error) {
	var (
		writeBalanceMap   map[int64]*model.WriteAccount
		eventApplyResults []*model.EventApplyResult
		readAccountMap    map[int64]*model.ReadAccount
		err               error
	)

	listAccountBalancesOptions := model.ListAccountBalancesOptions{
		AccountBalanceFilters: []model.AccountBalanceFilter{},
	}
	for _, de := range events {
		for _, change := range de.ChangeDecimals {
			listAccountBalancesOptions.AccountBalanceFilters = append(listAccountBalancesOptions.AccountBalanceFilters, model.AccountBalanceFilter{
				AccountID:    de.Event.AccountId,
				CurrencyCode: change.CurrencyCode,
				ShardID:      de.Event.AccountShardId,
			})
			if change.FallbackCurrencyCode != "" {
				listAccountBalancesOptions.AccountBalanceFilters = append(listAccountBalancesOptions.AccountBalanceFilters, model.AccountBalanceFilter{
					AccountID:    de.Event.AccountId,
					CurrencyCode: change.FallbackCurrencyCode,
					ShardID:      de.Event.AccountShardId,
				})
			}
		}
	}

	logger.GetLogger(ctx).Debug().Int("event_count", len(events)).Msg("start applying changes for events")
	retryErr := utils.Retry(func() (bool, error) {
		readAccountMap, err = ca.GetReadBalanceMap(ctx, listAccountBalancesOptions)
		if err != nil {
			return true, err
		}

		writeBalanceMap, eventApplyResults, err = ca.checkBalanceGetWriteAccountsMap(ctx, events, readAccountMap)
		if err != nil {
			return true, err
		}
		err = ca.CacheRepo.ApplyAccountBalanceChanges(ctx, writeBalanceMap, eventApplyResults)
		if err != nil {
			logger.GetLogger(ctx).Warn().Err(err).Msg("apply account balance changes to cache failed, retrying...")
			if err.Error() == "balance insufficient" {
				// TODO: let consumer handle insufficient balance errors
				return false, err
			}
			if err.Error() == "idempotency key conflict" {
				// TODO: let consumer handle idempotency key conflict errors
				return false, err
			}
			return true, err
		}
		return false, nil
	})
	if retryErr != nil {
		return nil, nil, nil, retryErr
	}
	return writeBalanceMap, readAccountMap, eventApplyResults, nil
}

func (ca ChangeApplier) GetReadBalanceMap(ctx context.Context, listAccountBalancesOptions model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error) {
	readBalanceMap, err := ca.CacheRepo.ListAccountBalances(ctx, listAccountBalancesOptions)
	if err != nil {
		return nil, err
	}
	dbListAccountBalanceOptions := model.ListAccountBalancesOptions{
		AccountBalanceFilters: []model.AccountBalanceFilter{},
	}
	for _, readBalance := range readBalanceMap {
		for _, currencyBalance := range readBalance.AccountBalancesMap {
			if currencyBalance.NotExist {
				dbListAccountBalanceOptions.AddFilter(readBalance.AccountID, string(currencyBalance.CurrencyCode), readBalance.ShardID)
			}
		}
	}
	if len(dbListAccountBalanceOptions.AccountBalanceFilters) > 0 {
		dbReadBalanceMap, err := ca.DBRepo.ListAccountBalances(ctx, dbListAccountBalanceOptions)
		if err != nil {
			return nil, err
		}
		for accountID, dbReadBalance := range dbReadBalanceMap {
			readBalance, exists := readBalanceMap[accountID]
			if !exists {
				readBalanceMap[accountID] = dbReadBalance
				continue
			}
			readBalance.AccountID = dbReadBalance.AccountID
			readBalance.UserID = dbReadBalance.UserID
			readBalance.ShardID = dbReadBalance.ShardID
			maps.Copy(readBalance.AccountBalancesMap, dbReadBalance.AccountBalancesMap)
			readBalanceMap[accountID] = readBalance
		}
		err = ca.CacheRepo.BatchSetAccountBalances(ctx, dbReadBalanceMap)
		if err != nil {
			return nil, err
		}
	}

	return readBalanceMap, nil
}

func (ca ChangeApplier) checkBalanceGetWriteAccountsMap(ctx context.Context, events []*DecodedEvent, readBalanceMap map[int64]*model.ReadAccount) (map[int64]*model.WriteAccount, []*model.EventApplyResult, error) {
	eventApplyResult := make([]*model.EventApplyResult, 0, len(events))
	writeBalanceMap := make(map[int64]*model.WriteAccount)
	for _, de := range events {
		readAccount, exists := readBalanceMap[de.Event.AccountId]
		if !exists {
			// TODO: log account not found
			for _, change := range de.ChangeDecimals {
				eventApplyResult = append(eventApplyResult, model.NewEventApplyResult(
					de.Event.EventId,
					"account not found",
					change.ChangeId,
					de.Event.IdempotencyKey,
					model.ChangeLogStatusCannotApplied,
					de.Event.AccountId,
					de.Event.AccountShardId,
					false,
				))
			}
			continue
		}
		if _, exists := writeBalanceMap[de.Event.AccountId]; !exists {
			writeBalanceMap[de.Event.AccountId] = model.NewWriteAccount(readAccount.AccountID, readAccount.UserID, readAccount.ShardID)
		}

		rejectReason := ""
		for i, change := range de.ChangeDecimals {
			err := readAccount.ApplyChange(model.CurrencyCode(change.CurrencyCode), change.AvailableDelta, change.FrozenDelta)
			if err != nil {
				if change.FallbackCurrencyCode != "" && (!change.FallbackAvailableDelta.IsZero() || !change.FallbackFrozenDelta.IsZero()) {
					fallbackErr := readAccount.ApplyChange(model.CurrencyCode(change.FallbackCurrencyCode), change.FallbackAvailableDelta, change.FallbackFrozenDelta)
					if fallbackErr == nil {
						change.ApplyFallback = true
						err = nil
						continue
					} else {
						err = utils.JoinErrors(err, fallbackErr)
					}
				}
				logger.GetLogger(ctx).Warn().Err(err).Msg("apply change to read account failed")
				rejectReason = err.Error()
				for j := range i {
					prevChange := de.ChangeDecimals[j]
					if prevChange.ApplyFallback {
						_ = readAccount.RollbackChange(model.CurrencyCode(prevChange.FallbackCurrencyCode), prevChange.FallbackAvailableDelta, prevChange.FallbackFrozenDelta)
					} else {
						_ = readAccount.RollbackChange(model.CurrencyCode(prevChange.CurrencyCode), prevChange.AvailableDelta, prevChange.FrozenDelta)
					}
				}
				break
			}
		}

		for _, change := range de.ChangeDecimals {
			if rejectReason != "" {
				eventApplyResult = append(eventApplyResult, model.NewEventApplyResult(
					de.Event.EventId,
					rejectReason,
					change.ChangeId,
					de.Event.IdempotencyKey,
					model.ChangeLogStatusCannotApplied,
					de.Event.AccountId,
					de.Event.AccountShardId,
					change.ApplyFallback,
				))
				continue
			}

			eventApplyResult = append(eventApplyResult, model.NewEventApplyResult(
				de.Event.EventId,
				"",
				change.ChangeId,
				de.Event.IdempotencyKey,
				model.ChangeLogStatusApplied,
				de.Event.AccountId,
				de.Event.AccountShardId,
				change.ApplyFallback,
			))
			if change.ApplyFallback {
				writeBalanceMap[de.Event.AccountId].ApplyChange(model.CurrencyCode(change.FallbackCurrencyCode), change.FallbackAvailableDelta, change.FallbackFrozenDelta, readAccount.CurrencyBalanceIsNotExist(model.CurrencyCode(change.FallbackCurrencyCode)))
			} else {
				writeBalanceMap[de.Event.AccountId].ApplyChange(model.CurrencyCode(change.CurrencyCode), change.AvailableDelta, change.FrozenDelta, readAccount.CurrencyBalanceIsNotExist(model.CurrencyCode(change.CurrencyCode)))
			}
		}
	}

	return writeBalanceMap, eventApplyResult, nil
}
