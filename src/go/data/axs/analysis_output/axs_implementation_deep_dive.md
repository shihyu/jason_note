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

#### 1. DB 負載集中風險 ⚠️
**問題描述**：所有寫入壓力最終都落在 Primary DB 上。

**潛在影響**：
- PostgreSQL 的 CPU/IO 可能成為瓶頸
- 單點故障風險（Primary DB 宕機會導致全系統停擺）
- 垂直擴展有上限（單機資源有限）

**緩解策略**：
- 採用 Sharding 策略，將不同 `shard_id` 的數據分散到不同 DB 實例
- 使用 PostgreSQL Streaming Replication 提供高可用性
- 考慮使用 Patroni 或 Stolon 等自動容錯移轉方案

#### 2. SQL 複雜度高 🔧
**問題描述**：`ApplyAccountBalanceChanges` 中的 CTE SQL 邏輯複雜。

**潛在影響**：
- 新人上手困難，學習曲線陡峭
- 除錯時難以定位問題（SQL 執行計劃複雜）
- 修改時容易引入 Bug（如遺漏 JOIN 條件）

**緩解策略**：
- 在程式碼中添加詳細的 SQL 註解，說明每個 CTE 的用途
- 建立完整的單元測試，覆蓋各種邊界情況
- 使用 `EXPLAIN ANALYZE` 定期檢查 SQL 執行計劃
- 考慮將部分邏輯提取為 PostgreSQL 的 Stored Procedure（權衡維護成本）

#### 3. 依賴 PostgreSQL 特性 🔒
**問題描述**：大量使用 `COPY`, `UNLOGGED TABLE`, `RETURNING` 等 PG 特有功能。

**潛在影響**：
- 資料庫遷移成本極高（MySQL/Oracle 無對等功能）
- 廠商鎖定（Vendor Lock-in）
- 升級 PostgreSQL 版本時需要重新驗證相容性

**緩解策略**：
- 在架構設計時就明確「不考慮跨資料庫」，接受這個技術債
- 若未來確實需要遷移，考慮使用 Vitess (MySQL Sharding) 或 CockroachDB (PostgreSQL 相容)
- 建立完整的效能基準測試，確保升級後效能不退化

#### 4. 批次處理的延遲權衡 ⏱️
**問題描述**：批次處理用「延遲」換取「吞吐量」。

**潛在影響**：
- 正常情況下延遲為 `batchingDelay` (30ms) 到 `maxReadTimeout` (1s)
- 對於需要極低延遲 (<10ms) 的場景（如高頻交易 HFT），不適用
- 用戶可能抱怨「下單後要等一下才看到餘額變化」

**緩解策略**：
- 在 gRPC 回應中立即返回「預期的餘額變化」（樂觀更新 UI）
- 提供 WebSocket 推送，當實際處理完成後通知前端
- 根據業務場景調整 `batchSize` 和 `batchingDelay`（如 VIP 用戶使用更小的 batch）
- 考慮實作「快速通道」（Fast Path）：餘額充足的小額交易走非批次處理

#### 5. UNLOGGED TABLE 的災難恢復風險 💥 **[NEW]**
**問題描述**：`UNLOGGED` 臨時表不寫 WAL (Write-Ahead Log)，提升速度但犧牲了持久化保證。

**潛在影響**：
- 如果 PostgreSQL 在 `COPY` 執行過程中崩潰，UNLOGGED TABLE 會被**自動清空**
- 雖然主表數據不會丟失（因為尚未提交交易），但會浪費已完成的計算
- 極端情況：DB 頻繁重啟會導致系統吞吐量大幅下降（不斷重新處理）

**緩解策略**：
- 確保 PostgreSQL 運行環境穩定（使用高可用架構、UPS 電源、ECC 記憶體）
- 監控 DB 的重啟次數，設置告警閾值
- 考慮使用 `LOGGED` 臨時表作為降級方案（效能下降約 30%，但更安全）
- 在批次處理前後記錄 Checkpoint，便於從斷點恢復

#### 6. 批次回滾的代價 🔄 **[NEW]**
**問題描述**：一批 200 筆交易中，如果最後 1 筆失敗（如餘額不足），整批交易會回滾。

**潛在影響**：
- 浪費了前 199 筆的計算資源（CPU、記憶體、I/O）
- 在高失敗率場景下，實際吞吐量會遠低於理論值
- 可能導致「雪崩效應」：失敗重試導致積壓越來越多

**緩解策略**：
- 在批次處理前進行「預檢查」（Pre-validation）：
  - 從 Redis 快取中快速檢查餘額是否充足
  - 將明顯會失敗的交易提前剔除
- 使用「分段提交」（Mini-batches）：
  - 將 200 筆拆成 4 個 50 筆的子批次
  - 每個子批次獨立提交，減少單次回滾的範圍
- 使用 PostgreSQL 的 `SAVEPOINT`：
  - 在批次處理中設置多個保存點
  - 失敗時回滾到最近的 SAVEPOINT 而非整個交易

#### 7. Memory Bloat 問題 🐘 **[NEW]**
**問題描述**：長時間運行的批次處理可能導致記憶體碎片化與膨脹。

**潛在影響**：
- Go 的 GC (Garbage Collector) 壓力增大，導致 STW (Stop-The-World) 時間變長
- 記憶體佔用持續增長，最終觸發 OOM (Out Of Memory)
- 效能逐漸退化，需要定期重啟服務

**緩解策略**：
- 使用 `sync.Pool` 重用切片和結構體，減少記憶體分配
- 定期執行 `runtime.GC()` 強制垃圾回收（僅在低流量時段）
- 監控 Go Runtime 指標（`runtime.ReadMemStats`）：
  - `HeapAlloc`: 當前堆記憶體使用量
  - `NumGC`: GC 執行次數
  - `PauseNs`: GC 暫停時間
- 實作「優雅重啟」（Graceful Restart）機制：
  - 每處理 N 個批次後，主動讓出 Leader 地位
  - 讓新啟動的 Consumer 接手（記憶體重置）
- 使用 `pprof` 定期進行記憶體分析，找出洩漏點

---

### 風險矩陣總結

| 風險項目 | 嚴重性 | 發生機率 | 優先級 | 緩解難度 |
|---------|-------|---------|-------|---------|
| DB 負載集中 | 高 | 中 | **P0** | 中（需 Sharding） |
| SQL 複雜度高 | 中 | 高 | P2 | 低（加註解+測試） |
| 廠商鎖定 | 低 | 低 | P3 | 高（重寫成本大） |
| 批次延遲 | 中 | 中 | P2 | 低（調參數） |
| UNLOGGED TABLE 風險 | 高 | 極低 | P1 | 中（加監控+降級方案） |
| 批次回滾代價 | 中 | 中 | **P1** | 中（需預檢查） |
| Memory Bloat | 中 | 中 | P2 | 中（需優雅重啟） |

**優先處理建議**：
1. **P0 - DB 負載集中**：規劃 Sharding 策略，準備擴展方案
2. **P1 - 批次回滾代價**：實作 Redis 預檢查，降低失敗率
3. **P1 - UNLOGGED TABLE 風險**：加強 DB 監控，準備降級方案

---

## 4. 關鍵學習筆記

1.  **Batching is King**: 在高併發系統中，將 I/O 操作 (Network, Disk) 批次化是提升效能最有效的手段。
2.  **Transaction as a Lock**: 利用 ACID Transaction 的特性，可以實現比 Redis Lock 更可靠的「樂觀鎖」與「腦裂防護」，且不需引入外部依賴。
3.  **SQL 也是程式碼**: 不要只把 DB 當作儲存桶。善用 SQL 的進階功能 (CTE, Window Functions, Bulk Copy) 可以將複雜的資料處理邏輯下推到 DB 層，大幅減少應用層的負載與網路傳輸。
4.  **Fencing Token**: 在分散式系統中，單純的「租約 (Lease)」是不夠的。寫入時必須帶上 Token (版本號/Fencing Token) 進行 Double Check，才能 100% 防止 Zombie Process 寫壞資料。

