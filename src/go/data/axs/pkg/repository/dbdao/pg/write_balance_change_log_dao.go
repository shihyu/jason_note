package pg

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/lib/pq"
	"github.com/vx416/axs/pkg/model"
)

func (dao PGDao) BatchUpdateIdempotencyKeysStatusToReject(ctx context.Context, idempotencyKeys []string, shardID int32, status model.ChangeLogStatus, rejectReason string) error {
	driver := dao.GetDB(ctx)
	sql := `UPDATE ` + BalanceChangeLogsTable + ` SET
			status = $1,
			reject_reason = $2,
			updated_msec = $3
		WHERE idempotency_key = ANY($4) AND account_shard_id = $5 AND status = $6`
	updateTime := time.Now().UnixMilli()
	res, err := driver.ExecContext(ctx, sql, int8(status), rejectReason, updateTime, pq.Array(idempotencyKeys), shardID, int8(model.ChangeLogStatusInit))
	if err != nil {
		return err
	}
	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return err
	}
	if int(rowsAffected) != len(idempotencyKeys) {
		// TODO: log concurrent update detected
	}
	return nil
}

func (dao PGDao) InsertBalanceChangeLogs(ctx context.Context, logs []*model.BalanceChangeLog) (int64, error) {
	var (
		affectedRows int64
		err          error
	)
	err = dao.ExecuteInTransaction(ctx, func(txnCtx context.Context) error {
		affectedRows, err = dao.BatchInsertChangeLogs(txnCtx, logs)
		return err
	})
	return affectedRows, err
}

func (dao PGDao) BatchInsertChangeLogs(ctx context.Context, logs []*model.BalanceChangeLog) (int64, error) {
	driver := dao.GetDB(ctx)
	batchSize := 200
	batchSQL := dao.getBatchInsertChangeLogsNamedSQL()
	batchInsert := func(ctx context.Context, sql string, values []*model.BalanceChangeLog) (int64, error) {
		rows, err := driver.NamedQueryContext(ctx, sql, values)
		if err != nil {
			return 0, err
		}
		defer rows.Close()
		rowsAffected := int64(0)
		for rows.Next() {
			rowsAffected++
			id := int64(0)
			err := rows.Scan(&id)
			if err != nil {
				return 0, err
			}
			values[rowsAffected-1].ID = id
		}
		if rowsAffected != int64(len(values)) {
			return 0, fmt.Errorf("mismatch in inserted rows and returned IDs")
		}
		return rowsAffected, nil
	}

	updateTime := time.Now().UnixMilli()
	batchCnt := 0
	values := make([]*model.BalanceChangeLog, 0, batchSize*15)
	affected := int64(0)
	for _, log := range logs {
		log.InsertMsec = model.TimestampInMsec(updateTime)
		log.UpdatedMsec = model.TimestampInMsec(updateTime)
		values = append(values, log)
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
		rowsAffected, err := batchInsert(ctx, batchSQL, values)
		if err != nil {
			return 0, err
		}
		affected += rowsAffected
	}
	return affected, nil
}

func (dao PGDao) getBatchInsertChangeLogsNamedSQL() string {
	return `INSERT INTO ` + BalanceChangeLogsTable + ` (
			event_id,
			event_type_id,
			idempotency_key,
			change_id,
			status,
			account_id,
			user_id,
			account_shard_id,
			currency_code,
			currency_symbol,
			available_delta,
			frozen_delta,
			fallback_currency_code,
			fallback_currency_symbol,
			fallback_available_delta,
			fallback_frozen_delta,
			source_svc_id,
			related_order_id,
			submitted_msec,
			insert_msec,
			updated_msec
		) VALUES (:event_id, :event_type_id, :idempotency_key, :change_id, :status, :account_id, :user_id, :account_shard_id, :currency_code, :currency_symbol, 
		    :available_delta, :frozen_delta, :fallback_currency_code, :fallback_currency_symbol, :fallback_available_delta, :fallback_frozen_delta,
			:source_svc_id, :related_order_id, :submitted_msec, :insert_msec, :updated_msec) RETURNING id`
}

func (dao PGDao) UpdateChangeLog(ctx context.Context, idempotencyKey string, updateData map[string]any) error {
	driver := dao.GetDB(ctx)
	setClauses := ""
	for col := range updateData {
		if setClauses != "" {
			setClauses += ", "
		}
		setClauses += fmt.Sprintf("%s = :%s", col, col)
	}
	updateData["idempotency_key"] = idempotencyKey
	sql := `UPDATE ` + BalanceChangeLogsTable + ` SET ` + setClauses + ` WHERE idempotency_key = :idempotency_key`
	_, err := driver.NamedExecContext(ctx, sql, updateData)
	return err
}

func (dao PGDao) BatchUpdateChangeLogStatus(ctx context.Context, logs []*model.EventApplyResult) error {
	if len(logs) == 0 {
		return nil
	}

	driver := dao.GetDB(ctx)
	batchSize := 200
	sql := dao.getBatchUpdateChangeLogStatus(batchSize)
	updateTime := time.Now().UnixMilli()
	batchFunc := func(ctx context.Context, sql string, values []any, batchCnt int) error {
		values = append([]any{updateTime}, values...)
		res, err := driver.ExecContext(ctx, sql, values...)
		if err != nil {
			return err
		}
		rows, err := res.RowsAffected()
		if err != nil {
			return err
		}
		if int(rows) != batchCnt {
			return fmt.Errorf("concurrent update detected in change log status update")
		}
		return nil
	}

	values := []any{}
	batchCnt := 0
	for _, log := range logs {
		values = append(values, int8(log.Status), log.RejectReason, log.IdempotencyKey, log.ChangeID)
		batchCnt++
		if batchCnt >= batchSize {
			err := batchFunc(ctx, sql, values, batchCnt)
			if err != nil {
				return err
			}
			batchCnt = 0
			values = values[:0]
		}
	}
	if batchCnt > 0 {
		sql := dao.getBatchUpdateChangeLogStatus(batchCnt)
		err := batchFunc(ctx, sql, values, batchCnt)
		if err != nil {
			return err
		}
	}
	return nil
}

func (dao PGDao) getBatchUpdateChangeLogStatus(batchSize int) string {
	valuesPlaceholder := ""
	for i := range batchSize {
		if i > 0 {
			valuesPlaceholder += ","
		}
		valuesPlaceholder += fmt.Sprintf(`($%d::SMALLINT, $%d::TEXT, $%d::TEXT, $%d::BIGINT)`, 2+i*4, 3+i*4, 4+i*4, 5+i*4)
	}

	return `UPDATE ` + BalanceChangeLogsTable + ` AS log SET
			status = v.status,
			reject_reason = v.reject_reason,
			updated_msec = $1
		FROM (VALUES ` + valuesPlaceholder + `) AS v(status, reject_reason, idempotency_key, change_id)
		WHERE log.idempotency_key = v.idempotency_key AND log.change_id = v.change_id AND log.status = ` + strconv.Itoa(int(model.ChangeLogStatusInit))
}
