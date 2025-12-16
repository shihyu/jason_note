package cachedao

import (
	"context"
	"fmt"

	"github.com/vx416/axs/pkg/model"
)

func (dao CacheDao) GetIdempotencyKeysStatus(ctx context.Context, keys []string, shardID int32) (map[string]model.ChangeLogStatus, error) {
	result := make(map[string]model.ChangeLogStatus)
	for _, key := range keys {
		status, err := dao.getIdemKeyStatus(key)
		if err != nil {
			return nil, err
		}
		result[key] = status
	}
	return result, nil
}

func (dao CacheDao) getIdemKeyStatus(key string) (model.ChangeLogStatus, error) {
	status, ok := dao.idempotencyCache.Get(dao.getIdemKeyCacheKey(key))
	if !ok {
		return model.ChangeLogStatusInit, nil
	}
	return status, nil
}

func (dao CacheDao) getIdemKeyCacheKey(key string) string {
	return key
}

func (dao CacheDao) BatchUpdateIdempotencyKeysStatusToReject(ctx context.Context, keyStatus []string, shardID int32, status model.ChangeLogStatus, rejectReason string) error {
	for _, key := range keyStatus {
		err := dao.updateIdemKeyStatus(key, status)
		if err != nil {
			return err
		}
	}
	return nil
}

func (dao CacheDao) updateIdemKeyStatus(key string, status model.ChangeLogStatus) error {
	readStatus, err := dao.getIdemKeyStatus(key)
	if err != nil {
		return err
	}
	if readStatus != model.ChangeLogStatusInit {
		return fmt.Errorf("cannot update idempotency key %s status from %d to %d", key, readStatus, status)
	}
	dao.idempotencyCache.Set(dao.getIdemKeyCacheKey(key), status)
	return nil
}

func (dao CacheDao) SyncEventStatus(ctx context.Context, eventSTatus map[string]model.ChangeLogStatus) error {
	for key, status := range eventSTatus {
		dao.idempotencyCache.Set(dao.getIdemKeyCacheKey(key), status)
	}
	return nil
}
