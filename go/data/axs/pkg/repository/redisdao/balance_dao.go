package redisdao

import (
	"context"
	"fmt"
	"strconv"

	"github.com/redis/go-redis/v9"
	"github.com/shopspring/decimal"
	"github.com/vx416/axs/pkg/model"
)

func (dao *RedisDao) ListAccountBalances(ctx context.Context, opts model.ListAccountBalancesOptions) (map[int64]*model.ReadAccount, error) {
	if len(opts.AccountBalanceFilters) == 0 {
		return map[int64]*model.ReadAccount{}, nil
	}

	// 1. 整理請求：將相同的 AccountID 聚合，避免重複建立 Redis Key
	// Map: AccountID -> List of Currencies
	type accRequest struct {
		ShardID    int32
		Currencies []string
	}
	reqMap := make(map[int64]*accRequest)

	for _, f := range opts.AccountBalanceFilters {
		if _, ok := reqMap[f.AccountID]; !ok {
			reqMap[f.AccountID] = &accRequest{
				Currencies: make([]string, 0),
				ShardID:    f.ShardID,
			}
		}
		// 去重邏輯可選，這裡假設 Filter 傳進來的同一個 Account 不會有重複 Currency
		reqMap[f.AccountID].Currencies = append(reqMap[f.AccountID].Currencies, f.CurrencyCode)
	}

	// 2. 建立 Pipeline
	pipe := dao.Client.Pipeline()

	// 用來保存每個 Account 對應的 Redis Command，方便後續讀取結果
	cmds := make(map[int64]*redis.SliceCmd)

	for accID, req := range reqMap {
		// 組裝 Redis Key: acc:{shard_id}:{account_id}
		shardID := req.ShardID
		key := dao.getSyncAccCacheKey(shardID, accID)

		// 準備 HMGET 欄位
		// 我們總是多讀一個 "shard_id" 用來驗證 Key 是否存在或做 Double Check
		fields := []string{"shard_id", "uid"}

		for _, currency := range req.Currencies {
			fields = append(fields, currency+":a") // Available
			fields = append(fields, currency+":f") // Frozen
		}

		cmds[accID] = pipe.HMGet(ctx, key, fields...)
	}

	// 3. 執行 Pipeline
	_, err := pipe.Exec(ctx)
	if err != nil && err != redis.Nil {
		return nil, fmt.Errorf("redis pipeline exec failed: %w", err)
	}

	// 4. 解析結果
	resultMap := make(map[int64]*model.ReadAccount)

	for accID, cmd := range cmds {
		// HMGET 回傳的是 []interface{}
		// 順序對應我們傳入的 fields: [shard_id, curr1:a, curr1:f, curr2:a, curr2:f, ...]
		vals, err := cmd.Result()
		if err != nil {
			// 如果單個指令失敗，視需求決定是忽略還是報錯，這裡選擇 log 並跳過
			return nil, fmt.Errorf("redis HMGET failed for account %d: %w", accID, err)
		}

		// 取得請求資訊
		req := reqMap[accID]

		// 初始化回傳結構

		// 檢查 shard_id (vals[0])
		// 如果 vals[0] 為 nil，代表這個 Hash Key 根本不存在 (新帳戶)
		keyExists := vals[0] != nil
		uid := 0
		if keyExists {
			// 解析 uid (vals[1])
			if vals[1] != nil {
				if uidInt, ok := vals[1].(string); ok {
					var err error
					uid, err = strconv.Atoi(uidInt)
					if err != nil {
						return nil, fmt.Errorf("invalid uid format for account %d: %w", accID, err)
					}
				}
			}
		}
		readAcc := model.ReadAccount{
			AccountID:          accID,
			ShardID:            req.ShardID,
			AccountBalancesMap: make(map[model.CurrencyCode]model.AccountBalanceView),
			UserID:             int64(uid),
		}

		// 遍歷貨幣解析餘額
		// fields 索引從 1 開始是貨幣資料 (0 是 shard_id, 1 是 uid)
		for i, currency := range req.Currencies {
			// Available Index = 1 + i*2
			// Frozen Index    = 1 + i*2 + 1
			availIdx := 2 + i*2
			frozenIdx := availIdx + 1

			view := model.AccountBalanceView{
				CurrencyCode: model.CurrencyCode(currency),
				Available:    decimal.Zero,
				Frozen:       decimal.Zero,
				NotExist:     true,
			}

			if keyExists {
				// 解析 Available
				if vals[availIdx] != nil {
					// Redis 回傳的是字串 (Big Decimal Format)
					if valStr, ok := vals[availIdx].(string); ok {
						dec, err := decimal.NewFromString(valStr)
						if err != nil {
							return nil, fmt.Errorf("invalid decimal format for account %d currency %s available: %w", accID, currency, err)
						}
						view.Available = dec
						view.NotExist = false
					}
				}

				// 解析 Frozen
				if vals[frozenIdx] != nil {
					if valStr, ok := vals[frozenIdx].(string); ok {
						dec, err := decimal.NewFromString(valStr)
						if err != nil {
							return nil, fmt.Errorf("invalid decimal format for account %d currency %s frozen: %w", accID, currency, err)
						}
						view.Frozen = dec
						view.NotExist = false
					}
				}
			}

			// 如果 Key 存在但該幣種欄位都是 nil，view.NotExist 保持 true，餘額為 0
			readAcc.AccountBalancesMap[model.CurrencyCode(currency)] = view
		}

		resultMap[accID] = &readAcc
	}

	return resultMap, nil
}
