package domain

import (
	"context"
	"time"

	"github.com/vx416/axs/pkg/model"
)

// DBRepository defines the interface for database operations.
type DBRepository interface {
	// ListAccountBalances retrieves account balances based on the provided options.
	ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error)
	ApplyAccountBalanceChanges(ctx context.Context, writeAccounts map[int64]*model.WriteAccount, logs []*model.EventApplyResult, latestOffset *model.PartitionLeaderLock) error
	GetAccountShardID(ctx context.Context, accountIDs []int64) (map[int64]int32, error)
	GetIdempotencyKeysStatus(ctx context.Context, keys []string, shardID int32) (map[string]model.ChangeLogStatus, error)
	InsertBalanceChangeLogs(ctx context.Context, logs []*model.BalanceChangeLog) (int64, error)
	BatchUpdateIdempotencyKeysStatusToReject(ctx context.Context, keyStatus []string, shardID int32, status model.ChangeLogStatus, rejectReason string) error
	UpdateChangeLog(ctx context.Context, idempotencyKey string, updateData map[string]any) error

	AcquirePartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string) (model.PartitionLeaderLock, bool, error)
	ExtendPartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string, fencingToken int) (bool, error)
	ReleasePartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string, fencingToken int) (bool, error)
	UpdateCommitOffsets(ctx context.Context, topic string, partition int32, commitOffset int64, lockerSvcID string, fencingToken int) (bool, error)
	CreateAndTruncateTempTables(ctx context.Context, partition int) (tempBalWriteTable, tempLogWriteTable string, err error)
}

type RedisRepository interface {
	ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error)
	SyncAccountBalances(ctx context.Context, accountBalance map[int64]*model.ReadAccount, epoch int64) error
	SyncEventStatus(ctx context.Context, logs []*model.EventApplyResult, partition int32) error
	ListLatestEventStatus(ctx context.Context, partition int32) (map[string]model.ChangeLogStatus, error)

	SetIdemKeyIfNotExists(ctx context.Context, idemKey string, ttl time.Duration) (bool, error)
}

type CacheRepository interface {
	ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error)
	BatchSetAccountBalances(ctx context.Context, accountBalance map[int64]*model.ReadAccount) error
	ApplyAccountBalanceChanges(ctx context.Context, writeAccounts map[int64]*model.WriteAccount, logs []*model.EventApplyResult) error
	GetIdempotencyKeysStatus(ctx context.Context, keys []string, shardID int32) (map[string]model.ChangeLogStatus, error)
	BatchUpdateIdempotencyKeysStatusToReject(ctx context.Context, keyStatus []string, shardID int32, status model.ChangeLogStatus, rejectReason string) error
	SyncEventStatus(ctx context.Context, eventSTatus map[string]model.ChangeLogStatus) error
	ClearAllData(ctx context.Context) error
}
