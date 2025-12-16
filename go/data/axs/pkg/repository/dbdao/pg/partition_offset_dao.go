package pg

import (
	"context"
	"database/sql"
	"errors"
	"time"

	"github.com/vx416/axs/pkg/model"
)

func (dao PGDao) UpdateCommitOffsets(ctx context.Context, topic string, partition int32, commitOffset int64, lockerSvcID string, fencingToken int) (bool, error) {
	updatedMsec := time.Now().UnixMilli()
	sql := `UPDATE ` + PartitionLeaderLocksTable + `
			SET commit_offset = $1,
				updated_msec = $2,
				updater_svc_id = $3
			WHERE topic = $4 AND partition = $5 AND leader_svc_id = $3 AND fencing_token = $6
	`
	res, err := dao.GetDB(ctx).ExecContext(ctx, sql, commitOffset, updatedMsec, lockerSvcID, topic, partition, fencingToken)
	if err != nil {
		return false, err
	}
	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return false, err
	}
	if rowsAffected == 0 {
		return false, nil
	}
	return true, nil
}

func (dao PGDao) AcquirePartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string) (model.PartitionLeaderLock, bool, error) {
	query := `WITH try_lock AS (
			INSERT INTO ` + PartitionLeaderLocksTable + ` (
				topic,
				partition,
				commit_offset,
				updated_msec,
				updater_svc_id,
				leader_svc_id,
				lease_expired_msec,
				fencing_token
			)
			VALUES (
				$1,                      
				$2,                      
				-1,                      
				$3,                      
				$4,                      
				$4,
				$5,                 
				1                       
			)
			ON CONFLICT (topic, partition)
			DO UPDATE
			SET
				leader_svc_id      = EXCLUDED.leader_svc_id,
				lease_expired_msec = EXCLUDED.lease_expired_msec,
				fencing_token      = partition_leader_locks.fencing_token + 1
			WHERE
				(partition_leader_locks.lease_expired_msec < $3 AND partition_leader_locks.leader_svc_id <> $4)
				OR partition_leader_locks.leader_svc_id IS NULL
			RETURNING
				topic,
				partition,
				commit_offset,
				updated_msec,
				updater_svc_id,
				leader_svc_id,
				lease_expired_msec,
				fencing_token
		)
		SELECT * FROM try_lock;
`
	leaderKey := model.PartitionLeaderLock{}
	updateTime := time.Now().UnixMilli()
	expiredTime := updateTime + int64(model.LeaderTTLSecond*1000)
	err := dao.GetDB(ctx).GetContext(ctx, &leaderKey, query, topic, partition, updateTime, lockerSvcID, expiredTime)
	if err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return leaderKey, false, nil
		}
		return model.PartitionLeaderLock{}, false, nil
	}
	return leaderKey, true, nil

}

func (dao PGDao) ExtendPartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string, fencingToken int) (bool, error) {
	query := `UPDATE ` + PartitionLeaderLocksTable + `
			SET lease_expired_msec = $1
			WHERE topic = $2 AND partition = $3 AND leader_svc_id = $4 AND fencing_token = $5`

	newLeaseExpiredMsec := time.Now().UnixMilli() + int64(model.LeaderTTLSecond*1000)
	res, err := dao.GetDB(ctx).ExecContext(ctx, query, newLeaseExpiredMsec, topic, partition, lockerSvcID, fencingToken)
	if err != nil {
		return false, err
	}
	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return false, err
	}
	if rowsAffected == 0 {
		return false, nil
	}
	return true, nil
}

func (dao PGDao) ReleasePartitionLeaderLock(ctx context.Context, topic string, partition int32, lockerSvcID string, fencingToken int) (bool, error) {
	query := `UPDATE ` + PartitionLeaderLocksTable + `
			SET leader_svc_id = NULL, lease_expired_msec = 0
			WHERE topic = $1 AND partition = $2 AND leader_svc_id = $3 AND fencing_token = $4`

	res, err := dao.GetDB(ctx).ExecContext(ctx, query, topic, partition, lockerSvcID, fencingToken)
	if err != nil {
		return false, err
	}
	rowsAffected, err := res.RowsAffected()
	if err != nil {
		return false, err
	}
	if rowsAffected == 0 {
		return false, nil
	}
	return true, nil
}
