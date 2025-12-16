package pg

import (
	"context"
	"time"

	"github.com/allegro/bigcache/v3"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/lib/pq"
	"github.com/vx416/axs/pkg/repository/dbdao/sqlx_adapter"
)

const (
	AccountBalancesTable      = "account_balances"
	BalanceChangeLogsTable    = "balance_change_logs"
	AccountsTable             = "accounts"
	PartitionLeaderLocksTable = "partition_leader_locks"
)

type PGDao struct {
	*sqlx_adapter.SqlxAdapter
	PGConn            *pgx.Conn
	userAccountsCache *bigcache.BigCache
}

func NewPGDao(dbAdapter *sqlx_adapter.SqlxAdapter, pgConn *pgx.Conn) (*PGDao, error) {
	cacheCfg := bigcache.DefaultConfig(10 * time.Minute)
	cacheCfg.HardMaxCacheSize = 64
	cache, err := bigcache.New(context.Background(), cacheCfg)
	if err != nil {
		return nil, err
	}

	pgDao := &PGDao{
		SqlxAdapter:       dbAdapter,
		userAccountsCache: cache,
		PGConn:            pgConn,
	}
	return pgDao, nil
}

func IsDuplicateKeyError(err error) bool {
	if err == nil {
		return false
	}

	pgErr, ok := err.(*pq.Error)
	if ok {
		if pgErr.Code == "23505" {
			return true
		}
	}
	pgConnErr, ok := err.(*pgconn.PgError)
	if ok {
		if pgConnErr.Code == "23505" {
			return true
		}
	}

	return false
}
