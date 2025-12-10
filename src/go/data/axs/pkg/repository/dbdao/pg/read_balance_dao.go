package pg

import (
	"context"
	"fmt"

	"github.com/vx416/axs/pkg/logger"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/utils"
)

func (dao *PGDao) ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error) {
	accountBalances, err := dao.QueryAccountBalances(ctx, opts)
	if err != nil {
		return nil, err
	}

	result := make(map[int64]*model.ReadAccount)
	for _, ab := range accountBalances {
		ra, exists := result[ab.AccountID]
		if !exists {
			ra = model.NewReadAccount(ab.AccountID, ab.UserID, ab.ShardID)
		}
		ra.AddCurrencyBalance(ab.CurrencyCode, ab.Available, ab.Frozen, ab.NotExist)
		result[ab.AccountID] = ra
	}
	return result, nil
}

func (dao *PGDao) QueryAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) ([]*model.AccountBalance, error) {
	driver := dao.GetDB(ctx)

	accIDsSet := utils.NewSet[int64]()
	for _, filter := range opts.AccountBalanceFilters {
		accIDsSet.Add(filter.AccountID)
	}
	accIDs := accIDsSet.ToSlice()
	if len(accIDs) == 0 {
		return make([]*model.AccountBalance, 0), nil
	}
	userAccounts, err := dao.ListUserAccounts(ctx, accIDs)
	if err != nil {
		return nil, err
	}
	if len(userAccounts) != len(accIDs) {
		return nil, fmt.Errorf("some accounts not found")
	}
	accIDAccountMap := make(map[int64]*model.Account)
	for _, ua := range userAccounts {
		accIDAccountMap[ua.ID] = ua
	}

	queryTuples := ``
	for _, filter := range opts.AccountBalanceFilters {
		if queryTuples != "" {
			queryTuples += ","
		}
		queryTuples += fmt.Sprintf("(%d, %d, '%s')", filter.AccountID, filter.ShardID, filter.CurrencyCode)
	}
	sql := fmt.Sprintf(`SELECT account_id, user_id, currency_code, available, frozen, updated_msec, shard_id
			FROM %s
			WHERE (account_id, shard_id, currency_code) IN (%s)`, AccountBalancesTable, queryTuples)
	balances := []*model.AccountBalance{}
	err = driver.SelectContext(ctx, &balances, sql)
	if err != nil {
		return nil, err
	}
	balancesMap := make(map[string]*model.AccountBalance)
	for _, bal := range balances {
		key := fmt.Sprintf("%d_%s", bal.AccountID, bal.CurrencyCode)
		balancesMap[key] = bal
	}
	// Mark not exist balances
	for _, filter := range opts.AccountBalanceFilters {
		key := fmt.Sprintf("%d_%s", filter.AccountID, filter.CurrencyCode)
		if _, exists := balancesMap[key]; !exists {
			balances = append(balances, &model.AccountBalance{
				AccountID:    filter.AccountID,
				UserID:       accIDAccountMap[filter.AccountID].UserID,
				ShardID:      accIDAccountMap[filter.AccountID].ShardID,
				CurrencyCode: model.CurrencyCode(filter.CurrencyCode),
				NotExist:     true,
			})
		}
	}
	return balances, nil
}

func (dao *PGDao) GetAccountShardID(ctx context.Context, accountIDs []int64) (map[int64]int32, error) {
	accs, err := dao.ListUserAccounts(ctx, accountIDs)
	if err != nil {
		return nil, err
	}
	result := make(map[int64]int32)
	for _, acc := range accs {
		result[acc.ID] = acc.ShardID
	}
	return result, nil
}

func (dao *PGDao) ListUserAccounts(ctx context.Context, accounts []int64) ([]*model.Account, error) {
	hitAccounts, missingAccIDs, err := dao.getUserAccountsCache(accounts...)
	if err != nil {
		logger.GetLogger(ctx).Error().Err(err).Msg("failed to get user accounts from cache")
	}
	if len(missingAccIDs) == 0 {
		return hitAccounts, nil
	}
	driver := dao.GetDB(ctx)
	sql := `SELECT id, user_id, shard_id, created_msec FROM ` + AccountsTable + ` WHERE id = ANY($1)`
	result := make([]*model.Account, 0)
	err = driver.SelectContext(ctx, &result, sql, missingAccIDs)
	if err != nil {
		return nil, err
	}
	result = append(result, hitAccounts...)
	dao.setUserAccountsCache(result...)
	return result, nil
}
