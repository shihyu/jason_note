package pg

import (
	"context"
	"fmt"
	"time"

	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/service/svcerr"
)

func (dao *PGDao) BatchUpdateAccountBalances(ctx context.Context, accounts map[int64]*model.WriteAccount) (int, error) {
	_, err := dao.BatchInsertMissingAccountBalances(ctx, accounts)
	if err != nil {
		return 0, err
	}
	driver := dao.GetDB(ctx)
	batchSize := 200
	batchSQL := dao.getBatchUpdateAccountBalancesSQL(batchSize)

	updateTime := time.Now().UnixMilli()
	batchUpdate := func(ctx context.Context, sql string, values []any, batchCnt int) (int, error) {
		values = append([]any{updateTime}, values...)
		res, err := driver.ExecContext(ctx, sql, values...)
		if err != nil {
			return 0, err
		}
		affected, err := res.RowsAffected()
		if err != nil {
			return 0, err
		}
		if int(affected) != batchCnt {
			return 0, model.ErrInsufficientBalance
		}
		return int(affected), nil
	}

	values := []any{}
	batchCnt := 0
	totalUpdated := 0
	for _, account := range accounts {
		for _, change := range account.BalanceChangesMap {
			values = append(values,
				change.AccountID,
				change.ShardID,
				change.CurrencyCode,
				change.AvailableDelta,
				change.FrozenDelta,
			)
			batchCnt++

			if batchCnt >= batchSize {
				affected, err := batchUpdate(ctx, batchSQL, values, batchCnt)
				if err != nil {
					return 0, err
				}
				totalUpdated += int(affected)
				values = values[:0]
				batchCnt = 0
			}
		}
	}
	if batchCnt > 0 {
		sql := dao.getBatchUpdateAccountBalancesSQL(batchCnt)
		affected, err := batchUpdate(ctx, sql, values, batchCnt)
		if err != nil {
			return 0, err
		}
		totalUpdated += int(affected)
	}
	return totalUpdated, nil
}

func (dao *PGDao) getBatchUpdateAccountBalancesSQL(batchSize int) string {
	valuesPlaceholder := ""
	for i := range batchSize {
		if i > 0 {
			valuesPlaceholder += ","
		}
		base := i * 5
		valuesPlaceholder += fmt.Sprintf(`($%d::BIGINT, $%d::BIGINT, $%d::TEXT, $%d::NUMERIC, $%d::NUMERIC)`, 2+base, 3+base, 4+base, 5+base, 6+base)
	}

	return `UPDATE ` + AccountBalancesTable + ` AS ab SET
			available = ab.available + v.available_delta,
			frozen = ab.frozen + v.frozen_delta,
			updated_msec = $1
		FROM (VALUES ` + valuesPlaceholder + `) AS v(account_id, shard_id, currency_code, available_delta, frozen_delta)
		WHERE ab.account_id = v.account_id AND ab.shard_id = v.shard_id AND ab.currency_code = v.currency_code AND (ab.available + v.available_delta) >= 0 AND (ab.frozen + v.frozen_delta) >= 0`
}

func (dao *PGDao) BatchInsertMissingAccountBalances(ctx context.Context, accounts map[int64]*model.WriteAccount) (int64, error) {
	driver := dao.GetDB(ctx)
	neededInserts := make([]model.AccountBalanceChange, 0)
	for _, account := range accounts {
		for _, change := range account.BalanceChangesMap {
			if change.IsAddOperation() && change.NotExist {
				neededInserts = append(neededInserts, change)
			}
		}
	}
	if len(neededInserts) == 0 {
		return 0, nil
	}
	batchSize := 200
	batchSQL := dao.getBatchInsertAccountBalancesSQL(batchSize)

	batchInsert := func(ctx context.Context, sql string, values []any) (int64, error) {
		res, err := driver.ExecContext(ctx, sql, values...)
		if err != nil {
			return 0, err
		}
		affected, err := res.RowsAffected()
		if err != nil {
			return 0, err
		}
		return affected, nil
	}

	updateTime := time.Now().UnixMilli()
	batchCnt := 0
	values := make([]any, 0, batchSize*7)
	affected := int64(0)
	for _, insertRecord := range neededInserts {
		values = append(values,
			insertRecord.AccountID,
			insertRecord.UserID,
			insertRecord.ShardID,
			insertRecord.CurrencyCode,
			0,
			0,
			updateTime,
		)
		batchCnt++
		if batchCnt >= batchSize {
			rowsAffected, err := batchInsert(ctx, batchSQL, values)
			if err != nil {
				return 0, err
			}
			affected += rowsAffected
			values = values[:0]
			batchCnt = 0
		}
	}
	if batchCnt > 0 {
		sql := dao.getBatchInsertAccountBalancesSQL(batchCnt)
		rowsAffected, err := batchInsert(ctx, sql, values)
		if err != nil {
			return 0, err
		}
		affected += rowsAffected
	}
	return affected, nil
}

func (dao *PGDao) getBatchInsertAccountBalancesSQL(batchSize int) string {
	valuePlaceholder := ""
	for i := range batchSize {
		if i > 0 {
			valuePlaceholder += ","
		}
		valuePlaceholder += fmt.Sprintf(`($%d, $%d, $%d, $%d, $%d, $%d, $%d)`, 1+i*7, 2+i*7, 3+i*7, 4+i*7, 5+i*7, 6+i*7, 7+i*7)
	}
	return `INSERT INTO ` + AccountBalancesTable + ` (
			account_id, user_id, shard_id, currency_code, available, frozen, updated_msec
		) VALUES ` + valuePlaceholder
}

func (dao *PGDao) ApplyAccountBalanceChangesOLD(ctx context.Context, writeAccounts map[int64]*model.WriteAccount, logs []*model.EventApplyResult, latestOffset *model.PartitionLeaderLock) error {
	return dao.ExecuteInTransaction(ctx, func(txnCtx context.Context) error {
		_, err := dao.BatchUpdateAccountBalances(txnCtx, writeAccounts)
		if err != nil {
			return err
		}

		err = dao.BatchUpdateChangeLogStatus(txnCtx, logs)
		if err != nil {
			return err
		}

		ok, err := dao.UpdateCommitOffsets(txnCtx, latestOffset.Topic, latestOffset.Partition, latestOffset.CommitOffset, latestOffset.UpdaterSvcID, int(latestOffset.FencingToken))
		if err != nil {
			return err
		}
		if !ok {
			return svcerr.ErrLeaderChange
		}
		return nil
	})
}
