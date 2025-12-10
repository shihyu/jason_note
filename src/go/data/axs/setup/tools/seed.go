package tools

import (
	"context"
	"database/sql"
	"log"
	"math/rand"
	"strings"
	"sync"

	pg "github.com/lib/pq"
)

const (
	AccountSeedCount = 1000000
	ShardCount       = 10
	CurrencyCodes    = "USDT,BTC,ETH,SOL,BNB,USDC"
)

func RunAccountSeedData(ctx context.Context, driver, dsn string) error {
	db, err := sql.Open(driver, dsn)
	if err != nil {
		return err
	}
	defer db.Close()

	batchSize := 100
	workerCnt := 20
	wg := sync.WaitGroup{}
	currencyCodes := strings.Split(CurrencyCodes, ",")
	defaultBalance := 1000000000
	workerJobSize := AccountSeedCount / workerCnt
	for w := range workerCnt {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for i := workerID * workerJobSize; i < (workerID+1)*workerJobSize; i += batchSize {
				shardID := rand.Intn(ShardCount) + 1
				_, err := db.Exec("SELECT batch_insert_account_balances($1::BIGINT, $2::BIGINT, $3::BIGINT, $4::TEXT[], $5::NUMERIC)", i+1, batchSize, shardID, pg.Array(&currencyCodes), defaultBalance)
				if err != nil {
					log.Println("Failed to execute batch_insert_account_balances:", err)
				}
			}
		}(w)
	}
	wg.Wait()

	return nil
}
