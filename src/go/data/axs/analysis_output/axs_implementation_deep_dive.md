# 百萬級吞吐量的交易所餘額系統 — 實作深度分析

本報告深入剖析了 AXS 專案如何實現高吞吐量與高可靠性的核心技術。我們將對照 `百萬級吞吐量的交易所餘額系統系統實作.md` 一文中的設計理念與實際程式碼庫 (`axs`) 的實作細節。

## 1. 核心實作摘要

AXS 系統為了達成百萬級 TPS 與嚴格的資料一致性，採用了以下關鍵技術：

1.  **智慧批次消費 (Smart Batching)**: 採用動態 Timeout 機制 (Long Poll + Short Batch Latency)，在低延遲與高吞吐之間取得平衡，並減少 syscall。
2.  **極速資料庫寫入 (High-Performance Persistence)**: 捨棄標準的逐筆 Insert/Update，改用 `PostgreSQL COPY` + `UNLOGGED Temp Table` + `CTE (Common Table Expressions)` 進行批次 Upsert，大幅降低 DB I/O 與 Lock 競爭。
3.  **無鎖併發控制 (Lock-Free Concurrency)**: 透過 Sharding 與單一線程處理模型，避免了複雜的 Row Lock 與 Deadlock 問題。
4.  **強一致性與腦裂防護 (Strong Consistency & Fencing)**: 利用 DB 的 Transaction 原子性，將「餘額更新」、「Offset 提交」與「Leader 租約檢查 (Fencing Token)」綁定在同一個交易中，徹底解決 Kafka 重複消費與腦裂風險。

---

## 2. 技術細節與程式碼對照 (Code Mapping)

### 2.1 單線程 Consumer 批次處理 (Batch Consumer)

文章提到使用 **雙重 Timeout 機制** 來兼顧即時性與批次效率。

*   **設計理念**: 平時用長輪詢 (`longPoll`, e.g., 1s) 等待第一筆訊息，一旦收到訊息，轉為短輪詢 (`batchLatency`, e.g., 30ms) 快速收集後續訊息，直到湊滿 `batchSize` (e.g., 200) 或超時。
*   **程式碼位置**: `pkg/handler/consumer/batch_consumer.go`

```go
// StartConsuming 實作了動態 Timeout 邏輯
func (c *BatchEventConsumer) StartConsuming() {
    // ...
    readTimeout := c.maxReadTimeout // 初始為長輪詢 (1s)
    for {
        // ...
        msg, err := c.mqReader.ReadMessage(newCtx, readTimeout)
        if err != nil {
            // Timeout 處理：如果有累積訊息就處理，並重置為長輪詢
            if mq.IsTimeoutError(err) {
                 if len(batchMsg) > 0 {
                     c.handler.ProcessEvents(newCtx, batchMsg)
                     batchMsg = batchMsg[:0]
                 }
                 readTimeout = c.maxReadTimeout // 回復長輪詢
                 continue
            }
            // ...
        }

        // 收到訊息後，將 Timeout 縮短為 batchingDelay (30ms)，加速收集
        readTimeout = c.batchingDelay 
        batchMsg = append(batchMsg, msg)
        
        // 滿單處理
        if len(batchMsg) >= c.batchSize {
            c.handler.ProcessEvents(newCtx, batchMsg)
            batchMsg = batchMsg[:0]
            readTimeout = c.maxReadTimeout // 處理完後回復長輪詢
        }
    }
}
```

### 2.2 高效批次寫入 (High-Performance DB Write)

文章比較了 `SWITCH CASE`, `UPDATE JOIN` 與 `Temp Table` 的差異，最終選擇了 **COPY + Temp Table** 的極致優化方案。

*   **設計理念**: 
    1.  建立 `UNLOGGED` 臨時表 (不寫 WAL，速度快)。
    2.  用 `COPY` 指令將記憶體中的資料二進位直灌 DB (避開 SQL Parser overhead)。
    3.  用一個複雜的 `CTE` SQL 將臨時表的資料更新回主表 (一次 Round-trip 完成所有操作)。
*   **程式碼位置**: `pkg/repository/dbdao/pg/apply_balance_change_dao.go`

```go
// ApplyAccountBalanceChanges 實作了 COPY + CTE 流程
func (dao *PGDao) ApplyAccountBalanceChanges(...) error {
    // 1. 建立/清空臨時表 (UNLOGGED)
    tempBalanceWriteTable, ..., err := dao.TruncateTempTables(...)

    // 2. 使用 COPY 指令極速寫入臨時表
    // copy balance changes...
    cnt, err := tx.CopyFrom(ctx, pgx.Identifier([]string{tempBalanceWriteTable}), ...)
    
    // copy log status...
    cnt, err = tx.CopyFrom(ctx, pgx.Identifier([]string{tempLogWriteTable}), ...)

    // 3. 執行複雜的 CTE SQL 進行批量更新 (包含 Lazy Insert 邏輯)
    err = tx.QueryRow(ctx, dao.getBatchUpdateAccountBalanceSQL(tempBalanceWriteTable))...
    
    // 4. 更新 Offset 與 Leader Fencing Token (防止腦裂)
    // ...
}
```

### 2.3 新幣種 Lazy Insert 處理

文章提到使用 `CTE (Common Table Expressions)` 來同時處理 UPDATE 和 INSERT (針對新幣種)。

*   **SQL 邏輯**: 
    1.  `try_update`: 嘗試更新現有餘額，並回傳更新成功的 ID。
    2.  `missing`: 比對臨時表與 `try_update` 的結果，找出沒更新到的 (即新幣種)。
    3.  `try_insert`: 將 `missing` 的資料插入主表。

```sql
WITH try_update AS (
    UPDATE account_balances ab ...
    RETURNING t.account_id
),
missing AS (
    SELECT t.* FROM temp_balance_write_records t
    LEFT JOIN try_update u ON ...
    WHERE u.account_id IS NULL -- 找出更新失敗的
),
try_insert AS (
    INSERT INTO account_balances ... -- 插入新幣種
    SELECT ... FROM missing
)
...
```

### 2.4 冪等性與腦裂防護 (Idempotency & Fencing)

文章強調 Kafka Consumer 的 `exactly once` 必須由 Application 端透過 DB Transaction 來保證。

*   **設計理念**: 將「業務數據更新」與「Offset 更新」綁在一起。更進一步，為了防止多個 Consumer 同時操作同一 Partition (腦裂)，引入了 **Fencing Token** 機制。
*   **程式碼位置**: 
    *   `pkg/service/processor/event_leader_election.go` (搶鎖邏輯)
    *   `pkg/repository/dbdao/pg/apply_balance_change_dao.go` (Fencing Check)

```go
// SQL check: 確保只有持有最新 FencingToken 的 Leader 才能提交 Transaction
sql := `UPDATE ` + PartitionLeaderLocksTable + `
        SET commit_offset = $1, ...
        WHERE topic = $4 AND partition = $5 
          AND leader_svc_id = $3 
          AND fencing_token = $6  -- 關鍵：檢查 Fencing Token 是否仍有效
`
res, err := tx.Exec(ctx, sql, ...)
if rowsAffected != 1 {
    return svcerr.ErrLeaderChange // 如果更新筆數為 0，代表鎖被搶走，Rollback 交易
}
```

---

## 3. 優缺點與風險評估

### 優點
1.  **極致吞吐量**: 透過 Batch + COPY + UNLOGGED Table，將 DB 寫入效能推到極限，遠超傳統 ORM 或 SQL 寫法。
2.  **資料強一致性**: 所有狀態 (餘額、Log、Offset) 都在單一 DB Transaction 中完成，不會有資料不一致或丟失的問題。
3.  **架構簡單**: 不需要依賴複雜的分散式交易 (2PC/Saga) 或外部鎖服務 (Zookeeper/Etcd)，僅靠 PostgreSQL 即可實現。

### 缺點與風險
1.  **DB 負載集中**: 所有壓力最終都落在 Primary DB 上。雖然寫入極快，但若併發量過大，PostgreSQL 的 CPU/IO 仍可能成為瓶頸 (需透過 Sharding 解決)。
2.  **SQL 複雜度高**: 維護 `ApplyAccountBalanceChanges` 中的複雜 CTE SQL 需要較高的資料庫造詣，除錯與修改不易。
3.  **依賴 PostgreSQL 特性**: 使用了 `COPY`, `UNLOGGED TABLE`, `RETURNING` 等 PG 特有功能，若要遷移到 MySQL 或 Oracle 需要大幅重寫 (MySQL 沒有直接對應的 COPY 機制能達到同等速度，且 CTE 語法略有不同)。
4.  **延遲 (Latency)**: 批次處理本質上是用「延遲」換取「吞吐量」。對於需要極低延遲 (<10ms) 的場景，這種架構可能需要調整參數。

---

## 4. 關鍵學習筆記

1.  **Batching is King**: 在高併發系統中，將 I/O 操作 (Network, Disk) 批次化是提升效能最有效的手段。
2.  **Transaction as a Lock**: 利用 ACID Transaction 的特性，可以實現比 Redis Lock 更可靠的「樂觀鎖」與「腦裂防護」，且不需引入外部依賴。
3.  **SQL 也是程式碼**: 不要只把 DB 當作儲存桶。善用 SQL 的進階功能 (CTE, Window Functions, Bulk Copy) 可以將複雜的資料處理邏輯下推到 DB 層，大幅減少應用層的負載與網路傳輸。
4.  **Fencing Token**: 在分散式系統中，單純的「租約 (Lease)」是不夠的。寫入時必須帶上 Token (版本號/Fencing Token) 進行 Double Check，才能 100% 防止 Zombie Process 寫壞資料。

