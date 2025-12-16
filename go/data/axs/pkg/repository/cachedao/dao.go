package cachedao

import (
	"context"
	"time"

	genericcache "github.com/Code-Hex/go-generics-cache"
	"github.com/Code-Hex/go-generics-cache/policy/fifo"

	"github.com/allegro/bigcache/v3"
	"github.com/vx416/axs/pkg/domain"
	"github.com/vx416/axs/pkg/model"
)

func NewCacheDao() (domain.CacheRepository, error) {
	cacheCfg := bigcache.DefaultConfig(10 * time.Minute)
	cacheCfg.HardMaxCacheSize = 64

	userBalanceCache, err := bigcache.New(context.Background(), cacheCfg)
	if err != nil {
		return nil, err
	}
	idemCache := genericcache.New(genericcache.AsFIFO[string, model.ChangeLogStatus](fifo.WithCapacity(10000)))
	return &CacheDao{
		userBalanceCache: userBalanceCache,
		idempotencyCache: idemCache,
	}, nil
}

type CacheDao struct {
	userBalanceCache *bigcache.BigCache
	idempotencyCache *genericcache.Cache[string, model.ChangeLogStatus]
}

func (dao *CacheDao) Close() error {
	err := dao.userBalanceCache.Close()
	if err != nil {
		return err
	}

	return nil
}

func (dao *CacheDao) ClearAllData(ctx context.Context) error {
	var findErr error
	err := dao.userBalanceCache.Reset()
	if err != nil {
		findErr = err
	}
	for _, key := range dao.idempotencyCache.Keys() {
		dao.idempotencyCache.Delete(key)
	}

	return findErr
}
