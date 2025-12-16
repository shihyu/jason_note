package pg

import (
	"github.com/allegro/bigcache/v3"
	"github.com/vmihailenco/msgpack/v5"
	"github.com/vx416/axs/pkg/model"
)

func (dao *PGDao) getUserAccountsCache(accIDs ...int64) (hit []*model.Account, missingUIDs []int64, err error) {
	hit = make([]*model.Account, 0, len(accIDs))
	for _, accID := range accIDs {
		data, err := dao.userAccountsCache.Get(dao.encodeUserAccountCacheKey(accID))
		if err != nil {
			if err == bigcache.ErrEntryNotFound {
				missingUIDs = append(missingUIDs, accID)
				continue
			} else {
				return []*model.Account{}, accIDs, err
			}
		}
		account := &model.Account{}
		err = msgpack.Unmarshal(data, &account)
		if err != nil {
			return []*model.Account{}, accIDs, err
		}
		hit = append(hit, account)
	}
	return hit, missingUIDs, nil
}

func (dao *PGDao) setUserAccountsCache(accounts ...*model.Account) error {
	for _, account := range accounts {
		b, err := msgpack.Marshal(account)
		if err != nil {
			return err
		}
		err = dao.userAccountsCache.Set(dao.encodeUserAccountCacheKey(account.ID), b)
		if err != nil {
			return err
		}
	}
	return nil
}

func (dao *PGDao) encodeUserAccountCacheKey(accID int64) string {
	return "user_account_" + string(rune(accID))
}
