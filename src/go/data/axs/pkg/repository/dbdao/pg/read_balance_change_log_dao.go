package pg

import (
	"context"
	"fmt"

	"github.com/lib/pq"
	"github.com/vx416/axs/pkg/model"
)

func (dao PGDao) GetIdempotencyKeysStatus(ctx context.Context, idempotencyKeys []string, shardID int32) (map[string]model.ChangeLogStatus, error) {
	driver := dao.GetDB(ctx)
	sql := fmt.Sprintf(`SELECT idempotency_key, status
			FROM %s
			WHERE idempotency_key = ANY($1)`, BalanceChangeLogsTable)
	logs := []struct {
		IdempotencyKey string                `db:"idempotency_key"`
		Status         model.ChangeLogStatus `db:"status"`
	}{}
	err := driver.SelectContext(ctx, &logs, sql, pq.Array(idempotencyKeys))
	if err != nil {
		return nil, err
	}
	result := make(map[string]model.ChangeLogStatus)
	for _, log := range logs {
		result[log.IdempotencyKey] = log.Status
	}
	return result, nil
}
