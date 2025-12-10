package pg

import (
	"context"
	"fmt"
	"strconv"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/pkg/errors"
	"github.com/vx416/axs/pkg/model"
	"github.com/vx416/axs/pkg/service/svcerr"
)

func (dao *PGDao) ApplyAccountBalanceChanges(ctx context.Context, writeAccounts map[int64]*model.WriteAccount, logs []*model.EventApplyResult, latestOffset *model.PartitionLeaderLock) error {
	tx, err := dao.PGConn.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)

	tempBalanceWriteTable, tempLogWriteTable, err := dao.TruncateTempTables(ctx, tx, int(latestOffset.Partition))
	if err != nil {
		return errors.WithMessage(err, "failed to create temp tables")
	}

	balanceChangeRows := [][]any{}
	for _, wa := range writeAccounts {
		for _, balanceChangeRow := range wa.BalanceChangesMap {
			balanceChangeRows = append(balanceChangeRows, []any{
				wa.AccountID,
				wa.UserID,
				wa.ShardID,
				balanceChangeRow.CurrencyCode,
				balanceChangeRow.AvailableDelta,
				balanceChangeRow.FrozenDelta,
				time.Now().UnixMilli(),
			})
		}
	}
	cnt, err := tx.CopyFrom(ctx, pgx.Identifier([]string{tempBalanceWriteTable}), []string{
		"account_id",
		"user_id",
		"shard_id",
		"currency_code",
		"available_delta",
		"frozen_delta",
		"updated_msec",
	}, pgx.CopyFromRows(balanceChangeRows))
	if err != nil {
		return errors.WithMessage(err, "failed to copy balance change rows to temp table")
	}
	if int(cnt) != len(balanceChangeRows) {
		return fmt.Errorf("expected to copy %d rows, but copied %d", len(balanceChangeRows), cnt)
	}
	updatedRows, insertedRows := 0, 0
	err = tx.QueryRow(ctx, dao.getBatchUpdateAccountBalanceSQL(tempBalanceWriteTable)).Scan(&updatedRows, &insertedRows)
	if err != nil {
		return errors.WithMessage(err, "failed to batch update account balances")
	}
	if updatedRows+insertedRows != len(balanceChangeRows) {
		return svcerr.ErrBalanceInsufficient
	}

	balanceLogStatusRows := [][]any{}
	for _, log := range logs {
		balanceLogStatusRows = append(balanceLogStatusRows, []any{
			log.IdempotencyKey,
			log.ChangeID,
			log.Status,
			log.RejectReason,
			time.Now().UnixMilli(),
		})
	}
	cnt, err = tx.CopyFrom(ctx, pgx.Identifier([]string{tempLogWriteTable}), []string{
		"idempotency_key",
		"change_id",
		"status",
		"reject_reason",
		"updated_msec",
	}, pgx.CopyFromRows(balanceLogStatusRows))
	if err != nil {
		return err
	}
	if int(cnt) != len(balanceLogStatusRows) {
		return fmt.Errorf("expected to copy %d rows, but copied %d", len(balanceLogStatusRows), cnt)
	}

	logUpdateRes, err := tx.Exec(ctx, dao.getBatchUpdateLogsSQL(tempLogWriteTable))
	if err != nil {
		return errors.WithMessage(err, "failed to batch update balance change log status")
	}
	logUpdatedRows := logUpdateRes.RowsAffected()
	if int(logUpdatedRows) != len(balanceLogStatusRows) {
		return svcerr.ErrIdempotentViolation
	}
	sql := `UPDATE ` + PartitionLeaderLocksTable + `
			SET commit_offset = $1,
				updated_msec = $2,
				updater_svc_id = $3
			WHERE topic = $4 AND partition = $5 AND leader_svc_id = $3 AND fencing_token = $6
	`
	res, err := tx.Exec(ctx, sql, latestOffset.CommitOffset, time.Now().UnixMilli(), latestOffset.LeaderSvcID, latestOffset.Topic, latestOffset.Partition, latestOffset.FencingToken)
	if err != nil {
		return errors.WithMessage(err, "failed to update partition leader lock")
	}
	rowsAffected := res.RowsAffected()
	if rowsAffected != 1 {
		return svcerr.ErrLeaderChange
	}
	return tx.Commit(ctx)
}

func (dao *PGDao) CreateAndTruncateTempTables(ctx context.Context, partition int) (tempBalWriteTable, tempLogWriteTable string, err error) {
	tempBalanceWriteTable := `temp_balance_write_records_` + strconv.Itoa(partition)
	createBalanceWriteTableSQL := `CREATE UNLOGGED TABLE IF NOT EXISTS ` + tempBalanceWriteTable + ` (
				account_id BIGINT NOT NULL,
				user_id BIGINT NOT NULL DEFAULT 0,
				shard_id SMALLINT NOT NULL,
				currency_code TEXT NOT NULL,
				available_delta NUMERIC(36, 18) NOT NULL DEFAULT 0,
				frozen_delta    NUMERIC(36, 18) NOT NULL DEFAULT 0,
				updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT
		);`
	_, err = dao.PGConn.Exec(ctx, createBalanceWriteTableSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to create temp table for balance write records")
	}
	truncateSQL := `TRUNCATE TABLE ` + tempBalanceWriteTable
	_, err = dao.PGConn.Exec(ctx, truncateSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to truncate temp table for balance write records")
	}
	tempBalanceLogWriteTable := `temp_balance_change_log_status_` + strconv.Itoa(partition)
	createBalanceLogWriteTableSQL := `CREATE UNLOGGED TABLE IF NOT EXISTS ` + tempBalanceLogWriteTable + ` (
			idempotency_key TEXT NOT NULL,
			change_id BIGINT NOT NULL,
			status SMALLINT NOT NULL,
			reject_reason TEXT,
			updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT
		);`
	_, err = dao.PGConn.Exec(ctx, createBalanceLogWriteTableSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to create temp table for balance change log status")
	}
	truncateLogSQL := `TRUNCATE TABLE ` + tempBalanceLogWriteTable
	_, err = dao.PGConn.Exec(ctx, truncateLogSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to truncate temp table for balance change log status")
	}
	return tempBalanceWriteTable, tempBalanceLogWriteTable, nil
}

func (dao *PGDao) TruncateTempTables(ctx context.Context, tx pgx.Tx, partition int) (tempBalWriteTable, tempLogWriteTable string, err error) {
	tempBalanceWriteTable := `temp_balance_write_records_` + strconv.Itoa(partition)
	truncateSQL := `TRUNCATE TABLE ` + tempBalanceWriteTable
	_, err = tx.Exec(ctx, truncateSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to truncate temp table for balance write records")
	}
	tempBalanceLogWriteTable := `temp_balance_change_log_status_` + strconv.Itoa(partition)
	truncateLogSQL := `TRUNCATE TABLE ` + tempBalanceLogWriteTable
	_, err = tx.Exec(ctx, truncateLogSQL)
	if err != nil {
		return "", "", errors.WithMessage(err, "failed to truncate temp table for balance change log status")
	}
	return tempBalanceWriteTable, tempBalanceLogWriteTable, nil
}

func (dao *PGDao) getBatchUpdateAccountBalanceSQL(tempTableName string) string {
	return fmt.Sprintf(`WITH try_update AS (
				UPDATE account_balances ab
				SET available = ab.available + t.available_delta,
					frozen    = ab.frozen + t.frozen_delta,
					updated_msec = t.updated_msec
				FROM %s t
				WHERE ab.account_id = t.account_id
				AND ab.shard_id = t.shard_id
				AND ab.currency_code = t.currency_code
				AND ab.available + t.available_delta >= 0
				AND ab.frozen + t.frozen_delta >= 0
				RETURNING t.account_id, t.shard_id, t.currency_code
			),
			missing AS (
				SELECT t.*
				FROM %s t
				LEFT JOIN try_update u
				ON u.account_id = t.account_id
				AND u.shard_id   = t.shard_id
				AND u.currency_code = t.currency_code
				WHERE u.account_id IS NULL
			),
			try_insert AS (
				INSERT INTO account_balances (
					account_id, shard_id, currency_code,
					user_id, available, frozen, updated_msec
				)
				SELECT
					m.account_id, m.shard_id, m.currency_code,
					m.user_id, m.available_delta, m.frozen_delta, m.updated_msec
				FROM missing m WHERE m.available_delta >= 0 AND m.frozen_delta >= 0
				RETURNING account_id
			),
			validate AS (
				SELECT
					(SELECT count(*) FROM try_update) AS updated_rows,
					(SELECT count(*) FROM try_insert) AS inserted_rows
			)
			SELECT *
			FROM validate;`, tempTableName, tempTableName)
}

func (dao *PGDao) getBatchUpdateLogsSQL(tempTableName string) string {
	return fmt.Sprintf(`
		UPDATE balance_change_logs bcl
		SET status = t.status,
			reject_reason = t.reject_reason,
			updated_msec = t.updated_msec
		FROM %s t
		WHERE bcl.idempotency_key = t.idempotency_key
		AND bcl.change_id = t.change_id AND bcl.status = 0;`, tempTableName)
}

var (
	batchUpdateAccountBalanceSQL = `
			WITH try_update AS (
				UPDATE account_balances ab
				SET available = ab.available + t.available_delta,
					frozen    = ab.frozen + t.frozen_delta,
					updated_msec = t.updated_msec
				FROM temp_balance_write_records t
				WHERE ab.account_id = t.account_id
				AND ab.shard_id = t.shard_id
				AND ab.currency_code = t.currency_code
				AND ab.available + t.available_delta >= 0
				AND ab.frozen + t.frozen_delta >= 0
				RETURNING t.account_id, t.shard_id, t.currency_code
			),
			missing AS (
				SELECT t.*
				FROM temp_balance_write_records t
				LEFT JOIN try_update u
				ON u.account_id = t.account_id
				AND u.shard_id   = t.shard_id
				AND u.currency_code = t.currency_code
				WHERE u.account_id IS NULL
			),
			try_insert AS (
				INSERT INTO account_balances (
					account_id, shard_id, currency_code,
					user_id, available, frozen, updated_msec
				)
				SELECT
					m.account_id, m.shard_id, m.currency_code,
					m.user_id, m.available_delta, m.frozen_delta, m.updated_msec
				FROM missing m WHERE m.available_delta >= 0 AND m.frozen_delta >= 0
				RETURNING account_id
			),
			validate AS (
				SELECT
					(SELECT count(*) FROM try_update) AS updated_rows,
					(SELECT count(*) FROM try_insert) AS inserted_rows
			)
			SELECT *
			FROM validate;
	`

	// createBalanceLogStatusTempTableSQL = `
	// 	CREATE UNLOGGED TABLE IF NOT EXISTS temp_balance_change_log_status (
	// 		idempotency_key TEXT NOT NULL,
	// 		change_id BIGINT NOT NULL,
	// 		status SMALLINT NOT NULL,
	// 		reject_reason TEXT,
	// 		updated_msec BIGINT NOT NULL DEFAULT (extract(epoch from now()) * 1000)::BIGINT
	// 	) ON COMMIT DROP;
	// `

	batchUpdateBalanceChangeLogStatusSQL = `
		UPDATE balance_change_logs bcl
		SET status = t.status,
			reject_reason = t.reject_reason,
			updated_msec = t.updated_msec
		FROM temp_balance_change_log_status t
		WHERE bcl.idempotency_key = t.idempotency_key
		AND bcl.change_id = t.change_id AND bcl.status = 0;
	`
)
