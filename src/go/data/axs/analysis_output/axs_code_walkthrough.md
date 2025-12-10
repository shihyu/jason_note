# AXS 核心程式碼深度導讀 (Code Walkthrough)

本文件針對 AXS 專案的三大核心模組進行深度剖析。我們將先介紹每個檔案的職責功能，接著逐行拆解關鍵程式碼，揭示其設計巧思。

---

## 1. 流量入口：批次消費模組

### 檔案資訊
*   **路徑**: `pkg/handler/consumer/batch_consumer.go`
*   **角色**: **水壩調節閥**
*   **功能**: 
    Kafka 是一個串流系統，如果來一個訊息就處理一次 DB，資料庫會瞬間被壓垮。
    這個模組的作用就像水壩，平時閘門半開（Long Polling），一旦水來了（收到訊息），就先把閘門關小（Short Polling），快速蓄滿一池水（Batch），再一次性洩洪（Batch Process）。這樣可以將數百次 DB 操作合併為一次，大幅提升吞吐量。

### 關鍵代碼詳解：雙重 Timeout 機制

這段程式碼位於 `StartConsuming` 方法中，是實現「智慧批次」的核心。

```go
func (c *BatchEventConsumer) StartConsuming() {
    // ... 前置初始化 ...

    // 初始狀態：設定為「長輪詢」Timeout (例如 1秒)。
    // 意義：如果沒有訊息，我願意等久一點，避免空轉浪費 CPU。
    readTimeout := c.maxReadTimeout 

    batchMsg := make([]mq.ConsumedMessage, 0, c.batchSize)
    for {
        // ... Context 設定 ...

        // 1. 嘗試從 Kafka 讀取一則訊息
        msg, err := c.mqReader.ReadMessage(newCtx, readTimeout)
        
        if err != nil {
            // 情況 A: 讀取超時 (Timeout)
            if mq.IsTimeoutError(err) {
                // 如果手上已經有累積一些訊息 (但還沒滿 batchSize)，因為等太久了，所以直接處理掉。
                if len(batchMsg) > 0 {
                    c.handler.ProcessEvents(newCtx, batchMsg)
                    batchMsg = batchMsg[:0] // 清空暫存區
                }
                // 處理完後，回歸平靜，把 Timeout 改回「長輪詢」，準備進入下一輪長時間等待。
                readTimeout = c.maxReadTimeout 
                continue
            }
            // ... 錯誤處理 ...
        }

        // 情況 B: 成功讀到訊息
        
        // 關鍵點！一旦收到第一則訊息，預期後續馬上會有更多訊息進來。
        // 所以把 Timeout 改成極短的「批次延遲」 (例如 30ms)。
        // 意義：給我 30ms，看能不能湊滿一批；如果湊不滿，30ms 後我也會處理掉，不會讓使用者等太久。
        readTimeout = c.batchingDelay 
        
        batchMsg = append(batchMsg, msg)

        // 檢查是否湊滿一批 (例如 200 筆)
        if len(batchMsg) >= c.batchSize {
            // 滿單！立刻處理。
            c.handler.ProcessEvents(newCtx, batchMsg)
            batchMsg = batchMsg[:0] // 清空暫存區
            
            // 處理完一批後，壓力釋放，將 Timeout 改回「長輪詢」。
            readTimeout = c.maxReadTimeout 
        }
    }
}
```

---

## 2. 系統大腦：核心處理與腦裂防護

### 檔案資訊
*   **路徑**: `pkg/service/processor/event_leader_election.go` (搭配 `event_processor.go`)
*   **角色**: **最高指揮官**
*   **功能**:
    在分散式系統中，為了避免兩個 Consumer 同時處理同一個 Partition (導致餘額重複扣款)，必須選出一個 Leader。
    這個模組負責「搶麥克風」：誰搶到 DB 裡的鎖，誰就是 Leader。而且它還會產生一個 `Fencing Token` (令牌)，做任何寫入操作都要出示這個令牌，確保前任 Leader (Zombie) 無法搞破壞。

### 關鍵代碼詳解：搶鎖與令牌

```go
func (ep *EventProcessor) TryToBecomeLeader(ctx context.Context) (partition int64, offset int64, ok bool) {
    // ... 取得自身 Service ID 與 Partition ID ...

    // 設定要搶哪個 Partition 的鎖
    ep.LeaderElector.topic = model.BalanceChangeEventTopic
    ep.LeaderElector.leaderPartition = int32(partition)
    ep.LeaderElector.leaderSvcID = svcName

    // 1. 嘗試去 DB 搶鎖
    // 對應 SQL: SELECT * FROM partition_leader_locks WHERE ... FOR UPDATE
    // 如果鎖過期或沒人持有，就將自己寫入 leader_svc_id
    leaderLockData, ok, err := ep.DBRepo.AcquirePartitionLeaderLock(ctx, ...)
    
    if ok {
        // 搶鎖成功！
        // 呼叫 becomeLeader 做就職演說 (初始化)。
        err := ep.becomeLeader(&leaderLockData)
        // ...
        // 回傳目前的 Offset，準備開始工作。
        return partition, leaderLockData.CommitOffset, true
    }

    // 2. 搶鎖失敗 (鎖被別人持有中)
    logger.GetLogger(ctx).Info().Msg("leader lock is held by another instance, will retry to acquire")
    
    // 進入無窮迴圈，每 500ms 重試一次，直到搶到鎖為止。
    // 這確保了 High Availability：一旦現任 Leader 掛掉，這裡的某個等待者就會立刻補位。
    timer := time.NewTicker(500 * time.Millisecond)
    // ... retry loop ...
}

func (ep *EventProcessor) becomeLeader(leaderLockData *model.PartitionLeaderLock) error {
    // ... 略 ...
    
    // 關鍵點！保存 Fencing Token。
    // 這個 Token 是從 DB 取出的 (通常是遞增序列或版本號)。
    // 之後做任何 DB 更新時，WHERE 條件都要帶上這個 Token。
    // SQL: UPDATE ... WHERE fencing_token = $my_token
    // 如果 DB 裡的 Token 變了 (被新 Leader 搶走)，我的更新就會失敗 (RowsAffected = 0)。
    ep.LeaderElector.fencingToken = leaderLockData.FencingToken
    
    // 啟動一個背景 Goroutine，定期去 DB "續約" (Heartbeat)。
    // 如果續約失敗，代表我失去 Leader 資格，必須立刻自殺 (CloseNow)。
    logger.SafeGo(func() {
        // ... 心跳續約邏輯 ...
    })
    return nil
}
```

---

## 3. 系統肌肉：極速寫入模組

### 檔案資訊
*   **路徑**: `pkg/repository/dbdao/pg/apply_balance_change_dao.go`
*   **角色**: **數據搬運工**
*   **功能**:
    這是全系統效能最關鍵的地方。標準的 SQL `INSERT` 會有大量的解析 (Parsing) 和交易日誌 (WAL) 開銷。
    這裡使用了 PostgreSQL 的黑科技：
    1.  **UNLOGGED Table**: 建立不寫 Log 的臨時表，速度接近記憶體。
    2.  **COPY Protocol**: 用二進位串流直接灌資料，跳過 SQL Parser。
    3.  **CTE (Common Table Expressions)**: 用一段複雜的 SQL 完成 Update、Insert (針對新幣種) 和 Log 更新，一次 Round-trip 搞定。

### 關鍵代碼詳解：CTE 批次更新術

這段 SQL (包在 `getBatchUpdateAccountBalanceSQL` 函數中) 是效能的秘密武器。

```sql
-- 1. 嘗試更新 (Try Update)
WITH try_update AS (
    UPDATE account_balances ab
    -- 直接將餘額加上 Delta (可能是負數)
    SET available = ab.available + t.available_delta,
        frozen    = ab.frozen + t.frozen_delta,
        updated_msec = t.updated_msec
    FROM temp_balance_write_records_1 t  -- 來源是剛剛用 COPY 灌進去的臨時表
    WHERE ab.account_id = t.account_id
    AND ab.shard_id = t.shard_id
    AND ab.currency_code = t.currency_code
    -- 餘額檢查：確保扣款後不會變負數 (DB 層級的防護)
    AND ab.available + t.available_delta >= 0
    AND ab.frozen + t.frozen_delta >= 0
    -- 回傳更新成功的那些帳號 ID
    RETURNING t.account_id, t.shard_id, t.currency_code
),

-- 2. 找出漏網之魚 (Find Missing)
-- 用臨時表 (全部資料) LEFT JOIN 剛剛更新成功的資料 (try_update)
missing AS (
    SELECT t.*
    FROM temp_balance_write_records_1 t
    LEFT JOIN try_update u
    ON u.account_id = t.account_id
    -- ... join conditions ...
    WHERE u.account_id IS NULL -- JOIN 不上的，就是「新幣種」或「餘額不足」
),

-- 3. 嘗試插入 (Try Insert)
-- 針對那些 missing 的資料，執行 INSERT
try_insert AS (
    INSERT INTO account_balances (
        account_id, shard_id, currency_code, ...
    )
    SELECT
        m.account_id, m.shard_id, m.currency_code, ...
    FROM missing m 
    WHERE m.available_delta >= 0 -- 確保初始餘額是正的 (不可以一開戶就透支)
    RETURNING account_id
),

-- 4. 錯誤檢查 (Error Validation)
-- 找出那些既沒有更新成功、也沒有插入成功的記錄（通常是餘額不足）
error_records AS (
    SELECT
        t.account_id,
        t.shard_id,
        t.currency_code,
        t.available_delta,
        t.frozen_delta,
        'INSUFFICIENT_BALANCE' AS reject_reason
    FROM temp_balance_write_records_1 t
    LEFT JOIN try_update u
        ON u.account_id = t.account_id
        AND u.shard_id = t.shard_id
        AND u.currency_code = t.currency_code
    LEFT JOIN try_insert i
        ON i.account_id = t.account_id
        AND i.shard_id = t.shard_id
        AND i.currency_code = t.currency_code
    WHERE u.account_id IS NULL  -- 沒有更新成功
      AND i.account_id IS NULL  -- 也沒有插入成功
),

-- 5. 統計結果 (Validate)
validate AS (
    SELECT
        (SELECT count(*) FROM try_update) AS updated_rows,
        (SELECT count(*) FROM try_insert) AS inserted_rows,
        (SELECT count(*) FROM error_records) AS error_rows
)
SELECT * FROM validate;
```

**這段 SQL 的完整邏輯拆解：**

1. **try_update**: 嘗試更新現有餘額記錄
   - 只有當餘額充足時才會更新成功
   - `RETURNING` 子句回傳成功更新的記錄 ID

2. **missing**: 找出所有未被 update 的記錄
   - 可能是新幣種（帳戶還沒有這個幣種的餘額記錄）
   - 也可能是餘額不足（更新失敗）

3. **try_insert**: 嘗試插入新幣種
   - 只處理 `available_delta >= 0` 的情況（不能一開戶就透支）
   - 這實現了 "Lazy Insert" 策略

4. **error_records**: 錯誤檢查（NEW!）
   - 找出那些既沒更新、也沒插入的記錄
   - 這些通常是因為餘額不足而被拒絕的交易
   - 應用層可以根據這個結果將失敗的交易寫入 `balance_change_logs` 並標記為 `REJECTED`

5. **validate**: 統計結果
   - `updated_rows`: 成功更新的筆數（舊帳號扣款/入帳）
   - `inserted_rows`: 成功插入的筆數（新幣種開戶）
   - `error_rows`: 失敗的筆數（需要進一步處理）

**總結這段 SQL 的威力：**
它在一個 Atomic 的操作中，同時完成了：
- 舊帳號的餘額更新
- 新幣種的自動開戶（Lazy Insert）
- 餘額不足的錯誤檢測
- 完整的統計與驗證

而且**不需要應用層介入判斷**，極大地減少了程式碼複雜度與網路來回次數。應用層只需要檢查 `validate` 的結果，就能知道這一批次處理的成功率與失敗原因。
