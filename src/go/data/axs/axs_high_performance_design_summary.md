# axs 系統：為什麼能做到「百萬級吞吐」且「一塊錢都不會少」？（深度白話版）

簡單來說，axs 的設計哲學是：**「在記憶體裡飆車，但每一步都綁好安全帶」。**

---

## 整體系統架構

```
  ┌──────────────────────────────────────────────────────────────────────────────────┐
  │                              axs 系統整體資料流                                  │
  └──────────────────────────────────────────────────────────────────────────────────┘

   ┌────────────┐   HMAC-SHA256    ┌─────────────────┐
   │  下單服務   │ ──────────────> │                 │
   ├────────────┤                  │   Balance API   │
   │  清算服務   │ ──────────────> │   (gRPC/HTTP)   │
   ├────────────┤                  │                 │
   │  其他微服務 │ ──────────────> └────────┬────────┘
   └────────────┘                           │  ① Outbox Pattern
                                            │  寫入 DB + produce Kafka
                                            ▼
                          ┌────────────────────────────────────┐
                          │            Kafka MQ                │
                          │  ┌──────────────┬──────────────┐   │
                          │  │ Partition 0  │ Partition 1  │   │
                          │  │  [用戶A,C,E] │  [用戶B,D,F] │   │
                          │  └──────┬───────┴──────┬───────┘   │
                          └─────────│──────────────│───────────┘
                    ② assign API    │              │  assign API
                    (非 rebalance)  │              │
                          ┌─────────▼──────────────▼────────────┐
                          │        Consumer Server Cluster      │
                          │                                     │
                          │  ┌──────────────┐  ┌──────────────┐ │
                          │  │ Consumer A   │  │ Consumer B   │ │
                          │  │ (Leader)     │  │ (Leader)     │ │
                          │  │              │  │              │ │
                          │  │ ┌──────────┐ │  │ ┌──────────┐ │ │
                          │  │ │BigCache  │ │  │ │BigCache  │ │ │
                          │  │ │(in-mem)  │ │  │ │(in-mem)  │ │ │
                          │  │ └──────────┘ │  │ └──────────┘ │ │
                          │  │ Single Thread│  │ Single Thread│ │
                          │  └──────┬───────┘  └────────┬─────┘ │
                          └─────────│───────────────────│───────┘
                    ③ Flush Worker  │                   │  Flush Worker
                    COPY+TempTable  │                   │
                          ┌─────────▼───────────────────▼────────┐
                          │           PostgreSQL DB              │
                          │  ┌─────────────────────────────────┐ │
                          │  │        account_balances         │ │
                          │  │  shard_id │ user_id │ currency  │ │
                          │  │  balance  │ frozen  │ offset    │ │
                          │  └─────────────────────────────────┘ │
                          └────────────────┬─────────────────────┘
                    ④ Snapshot (LWW)       │
                    Thread Pool 並行       │
                          ┌────────────────▼─────────────────────┐
                          │           Redis Cluster              │
                          │   key: balance:{shard_id}:{user_id}  │
                          │   value: { amount, timestamp }       │
                          │   用於即時查詢，延遲極低             │
                          └──────────────────────────────────────┘
```

---

## 1. 極速的核心：單線程 + 記憶體（飆車模式）

傳統資料庫之所以慢，是因為大家都在搶路（鎖競爭）。axs 的做法是把路分好，讓大家各跑各的。

### 1-1 傳統鎖競爭 vs. Sharding 分道揚鑣

```
  ❌ 傳統做法：所有請求搶同一把鎖

  用戶A ──┐
  用戶B ──┤──> [ 資料庫 row lock ] ──> 大家排隊，互相等待
  用戶C ──┤             ↑
  用戶D ──┘       lock contention
                  P90 latency > 1sec

  ─────────────────────────────────────────────────────────

  ✅ axs 做法：Sharding 分組，各跑各的

  用戶A ──┐                       ┌──> Consumer 0 (單線程)
  用戶C ──┤ hash(user_id) % N=0   │    記憶體直接算，不需要鎖
  用戶E ──┘                       │    速度：微秒等級
          Kafka Partition 0 ──────┘

  用戶B ──┐                       ┌──> Consumer 1 (單線程)
  用戶D ──┤ hash(user_id) % N=1   │    記憶體直接算，不需要鎖
  用戶F ──┘                       │    速度：微秒等級
          Kafka Partition 1 ──────┘

  不同 Consumer 互不干擾，可無限橫向擴展！
```

### 1-2 BigCache：讓垃圾回收車「視而不見」

```
  ❌ 普通 HashMap 的 GC 問題：

  cache = map[string]*Balance{
      "user_A": &Balance{ Available: 1000, Frozen: 0 }  ← 指標
      "user_B": &Balance{ Available: 500,  Frozen: 200 } ← 指標
      ...  數萬個物件，每個都有指標
  }
  GC 要掃描：每個物件的每個 field（含 slice/map 指標）
  結果：GC STW (Stop The World) 卡頓，吞吐量下降


  ✅ BigCache 的解法：一個大 bytes array 對 GC 只是一個物件

  ┌─────────────────────────────────────────────────────────────┐
  │                   大 bytes array                            │
  │ [idx=0]user_A資料bytes | [idx=48]user_B資料bytes | ...      │
  │  ↑marshaled struct      ↑marshaled struct                   │
  └─────────────────────────────────────────────────────────────┘
         ↑                        ↑
  ┌──────────────────────────────────┐
  │   index hashmap（結構單純）      │
  │   "user_A" → 0  (起始 index)     │
  │   "user_B" → 48 (起始 index)     │  ← 只有 int，無巢狀指標
  └──────────────────────────────────┘

  GC 視角：只看到 1 個 bytes array + 1 個 hashmap (simple)
  效果：GC 掃描時間從 O(N個物件) 降至 O(1)
```

---

## 2. 聰明的批次處理：公車與臨時表（物流模式）

### 2-1 智慧等公車（Adaptive Polling）

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                  Consumer 批次消費邏輯                          │
  └─────────────────────────────────────────────────────────────────┘

  開始
    │
    ▼
  consumer.Poll(timeout=longPoll=1s) ◄───────────────────────┐
    │                                                        │
    ├── [timeout 發生，buffer 有資料] ──> process(buffer)    │
    │                                   buffer 清空          │
    │                                   timeout = longPoll ──┘
    │
    ├── [timeout 發生，buffer 空] ──> 繼續等 ─────────────────┘
    │
    └── [收到訊息] ──> buffer.append(msg)
                        timeout = batchLatency (100ms)  ──────────┐
                        len(buffer) >= batchSize (200)?           │
                        ├── YES ──> process(buffer), 清空 ────────┤
                        └── NO  ──> 繼續 Poll(100ms) ────────────►┘

  效果：
  ┌─────────────────────────────────────────────────────┐
  │ 高流量：累積到 200 筆就立刻處理，最大化吞吐量       │
  │ 低流量：最多等 100ms 就處理，保證 latency 可控      │
  │ 空閒期：用 1s longPoll，不浪費 CPU                  │
  └─────────────────────────────────────────────────────┘
```

### 2-2 高速卸貨（COPY + Temp Table）

```
  ❌ 傳統逐筆 UPDATE（慢）：

  UPDATE accounts SET balance=1000 WHERE id=1;  ← 一次 round-trip
  UPDATE accounts SET balance=1500 WHERE id=2;  ← 一次 round-trip
  UPDATE accounts SET balance=2000 WHERE id=3;  ← 一次 round-trip
  ... 1000 筆就是 1000 次 round-trip


  ✅ axs 做法：COPY + Temp Table（快 2~3 倍）

  步驟 1: TRUNCATE temp_balance_write_records_p0
          (清空舊資料，避免 lock 衝突)
            │
            ▼
  步驟 2: COPY temp_balance_write_records_p0
          (id, delta, currency, ...) FROM STDIN
          ┌──────────────────────────────┐
          │ 1 | +500 | USDT | ...        │  ← bytes 形式傳輸
          │ 2 | -100 | BTC  | ...        │  ← 跳過 parser & optimizer
          │ 3 | +200 | ETH  | ...        │  ← 直接 execute，速度最快
          └──────────────────────────────┘
            │
            ▼
  步驟 3: CTE UPDATE（一條 SQL 搞定 update + lazy insert）

  WITH try_update AS (
    UPDATE account_balances ab
    SET available = ab.available + t.available_delta
    FROM temp_balance_write_records_p0 t
    WHERE ab.account_id = t.account_id
    AND   ab.currency_code = t.currency_code
    AND   ab.available + t.available_delta >= 0  ← 防止餘額變負
    RETURNING t.account_id, t.currency_code
  ),
  missing AS (
    SELECT t.* FROM temp_... t
    LEFT JOIN try_update u ON u.account_id = t.account_id
    WHERE u.account_id IS NULL   ← 找出沒更新到的（新幣種用戶）
  ),
  try_insert AS (
    INSERT INTO account_balances (...)
    SELECT ... FROM missing WHERE available_delta >= 0
  )
  SELECT updated_rows, inserted_rows FROM validate;

  ┌────────────────────────────────────────────────────┐
  │  效能比較（實測）                                  │
  │  資料量    │ UPDATE JOIN │ COPY+TempTable          │
  │  300 筆   │    基準      │  快 2x                  │
  │  2000 筆  │    基準      │  快 2~3x                │
  │  10000 筆 │    基準      │  快 3x                  │
  └────────────────────────────────────────────────────┘
```

---

## 3. 鐵壁般的安全機制：綁定 Offset（安全帶模式）

### 3-1 Transaction 綁定 Offset：一起成功，一起失敗

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │          Flush Worker 的原子性 Transaction（缺一不可）              │
  └─────────────────────────────────────────────────────────────────────┘

  BEGIN TRANSACTION;
  ┌──────────────────────────────────────────────────────────┐
  │  ① COPY 資料到 temp table                                │
  │     用戶A: +500 USDT                                     │
  │     用戶B: -100 BTC                                      │
  │                                                          │
  │  ② CTE UPDATE 餘額                                       │
  │     UPDATE account_balances ...                          │
  │                                                          │
  │  ③ 更新 change log 狀態（WHERE status=INIT → DONE）      │
  │     同時用 WHERE status=INIT 保證冪等性                  │
  │                                                          │
  │  ④ 更新 Kafka Offset 到 DB                               │
  │     UPDATE consumer_offsets                              │
  │     SET offset = 12345                                   │
  │     WHERE partition = 0                                  │
  │                                                          │
  │  ⑤ 檢查 Leader Lock（防腦裂）                            │
  │     SELECT * FROM leader_locks                           │
  │     WHERE partition=0 AND holder='consumer_A'            │
  │     FOR UPDATE                                           │
  └──────────────────────────────────────────────────────────┘
  COMMIT; ← 全部成功才提交

  ─────────────────────────────────────────────────────────────────────
  情境模擬：突然拔插頭

  正常情況                    拔插頭
  ①②③④⑤ 全部 COMMIT ✅      ①②③④⑤ 到一半 ROLLBACK ❌
  offset 推進到 12345         offset 還在 12344
                              ↓
                              重開機後，從 12344 的下一筆開始重播
                              ③ WHERE status=INIT 擋住重複處理 ✅
                              錢一分不少，資料完整！
```

### 3-2 Leader Election：防止腦裂（兩個人同時改帳）

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                    Leader Election 機制                             │
  └─────────────────────────────────────────────────────────────────────┘

  Consumer A 啟動        Consumer B 啟動（備援，另一 AZ）
       │                       │
       ▼                       ▼
  ┌─────────────────────────────────────────┐
  │          Redis Leader Lock              │
  │  key: "leader:partition:0"              │
  │  value: "consumer_A"   TTL: 10s         │
  └─────────────────────────────────────────┘
       │                       │
  搶到 Lock                搶不到 Lock
  成為 Leader              成為 Follower（等待）
       │
       ▼
  每 3s 延長 TTL
  (ticker thread heartbeat)
       │
  [突發狀況：GC STW 卡住超過 10s]
       │
       ▼
  TTL 到期，Key 消失
       │
       ▼                 Consumer B 偵測到 key 消失
                               │
                               ▼
                         搶到 Lock，成為新 Leader
                         從 DB 讀取最後 committed offset
                         用 assign API 直接指定 offset 開始消費
                         （不用等 Kafka rebalance 的 1~5s）

  ─────────────────────────────────────────────────────────────────────
  ⚠️ 腦裂風險：Consumer A 的 GC 結束後，以為自己還是 Leader！

  Consumer A (舊 Leader)              Consumer B (新 Leader)
       │                                   │
       │  [GC 結束，開始 flush]            │  [也在消費同一批資料]
       │                                   │
       ▼                                   │
  Transaction:                             │
  ① 更新餘額 ...                           │
  ② 檢查 Leader Lock                       │
     SELECT WHERE holder='consumer_A'      │
     → 查無資料（已被 B 搶走）             │
     → ROLLBACK！❌ 不寫入！               │
                                           │
                         Consumer B 的 Transaction 正常 COMMIT ✅

  關鍵：把 Leader Lock 檢查放進 DB Transaction，
        用 DB 的 ACID 保證，而非 Redis（Redis 不夠可靠）
```

---

## 4. 懶人新增法（Lazy Insert）

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                   新幣種處理：Lazy Insert 策略                      │
  └─────────────────────────────────────────────────────────────────────┘

  ❌ 傳統做法（上新幣種時 pre-insert）：

  新上 BTC 幣種
  → INSERT INTO account_balances (user_id='A', currency='BTC', balance=0)
  → INSERT INTO account_balances (user_id='B', currency='BTC', balance=0)
  → ... 重複 1000 萬次
  → 資料庫直接 hang 死 💀


  ✅ axs 做法：CTE 一條 SQL，update 跟 insert 同時處理

  第一次存 BTC 時 ──> CTE 發現沒有對應 row ──> 順便 INSERT

  ┌───────────────────────────────────────────────────────────┐
  │  CTE 執行邏輯示意圖                                       │
  │                                                           │
  │  temp table 中的資料：                                    │
  │  [用戶A, USDT, +500]  ← 有 USDT row，走 UPDATE            │
  │  [用戶A, BTC,  +0.1]  ← 沒有 BTC row，走 INSERT           │
  │  [用戶B, USDT, -100]  ← 有 USDT row，走 UPDATE            │
  │                                                           │
  │  try_update (UPDATE 有對應 row 的)                        │
  │      → 用戶A USDT: 1000 + 500 = 1500 ✅                   │
  │      → 用戶B USDT: 2000 - 100 = 1900 ✅                   │
  │      → 用戶A BTC:  找不到 row，UPDATE 0 筆                │
  │                                                           │
  │  missing (找出 UPDATE 沒命中的)                           │
  │      → [用戶A, BTC, +0.1] ← 在這裡                        │
  │                                                           │
  │  try_insert (INSERT 沒有的 row)                           │
  │      → INSERT (用戶A, BTC, balance=0.1) ✅                │
  │                                                           │
  │  validate (統計結果)                                      │
  │      → updated=2, inserted=1                              │
  └───────────────────────────────────────────────────────────┘

  優點：
  ✅ 一條 SQL，一次 round-trip
  ✅ 不用預先建立空帳戶
  ✅ 避免 INSERT ON DUPLICATE KEY 的 gap lock 問題
  ✅ 單用戶單線程，SELECT 和 INSERT 無 race condition
```

---

## 5. 高可用架構：Zero Downtime 部署

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │              Zero Downtime 滾動更新流程                             │
  └─────────────────────────────────────────────────────────────────────┘

  部署前                         部署中                       部署後

  ┌─────────────┐               ┌─────────────┐             ┌─────────────┐
  │ Consumer A  │               │ Consumer A  │             │ Consumer A  │
  │ v1.0 Leader │               │ v1.0 Leader │             │ v1.0        │
  │ consuming   │               │ consuming   │             │ (shutdown)  │
  └─────────────┘               └─────────────┘             └─────────────┘
                                ┌─────────────┐             ┌─────────────┐
                                │ Consumer A' │             │ Consumer A' │
                                │ v2.0 啟動   │             │ v2.0 Leader │
                                │ 等待 lock   │             │ consuming   │
                                └─────────────┘             └─────────────┘

  關鍵步驟：
  1. 啟動 v2.0 Consumer，嘗試搶 Leader Lock → 搶不到，等待
  2. 優雅關閉 v1.0：
     a. 停止 poll 新訊息
     b. 等最後一批 flush 完成
     c. 釋放 Leader Lock（刪除 Redis key）
  3. v2.0 立刻搶到 Lock
     a. 從 DB 讀取最後 committed offset（例如 12345）
     b. consumer.Assign(partition=0, offset=12346) ← 直接指定！
     c. 立刻開始消費，不等 rebalance

  ┌─────────────────────────────────────────────────────┐
  │  傳統 rebalance：停頓 1~5 秒                        │
  │  axs assign 方案：停頓 < 100ms (graceful shutdown)  │
  └─────────────────────────────────────────────────────┘


  ┌─────────────────────────────────────────────────────────────────────┐
  │              多 AZ 高可用部署（防止單點故障）                       │
  └─────────────────────────────────────────────────────────────────────┘

  ┌──────────── AZ-A ──────────────┐    ┌──────────── AZ-B ──────────────┐
  │                                │    │                                │
  │  ┌──────────────────────────┐  │    │  ┌──────────────────────────┐  │
  │  │  Consumer A (Leader)     │  │    │  │  Consumer B (Standby)    │  │
  │  │  Partition 0,2,4         │  │    │  │  Partition 0,2,4         │  │
  │  │  heartbeat ──────────────┼──┼──> │  │  等待 TTL 過期           │  │
  │  └──────────────────────────┘  │    │  └──────────────────────────┘  │
  │                                │    │                                │
  │  ┌──────────────────────────┐  │    │  ┌──────────────────────────┐  │
  │  │  Consumer C (Leader)     │  │    │  │  Consumer D (Standby)    │  │
  │  │  Partition 1,3,5         │  │    │  │  Partition 1,3,5         │  │
  │  └──────────────────────────┘  │    │  └──────────────────────────┘  │
  │                                │    │                                │
  └────────────────────────────────┘    └────────────────────────────────┘
                  │
        AZ-A 整個掛掉
                  │
                  ▼
        AZ-B 的 Consumer B/D TTL 過期
        搶到 Leader Lock
        從 DB offset 恢復消費
        RTO（Recovery Time Objective）< Leader Lock TTL（10s）
```

---

## 總結

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                    axs 各層設計目標對應表                           │
  └─────────────────────────────────────────────────────────────────────┘

  挑戰                  解法                          效果
  ─────────────────────────────────────────────────────────────────────
  鎖競爭               Sharding + 單線程              消除 lock，微秒操作
  GC 卡頓              BigCache bytes array           GC 掃描 O(1)
  DB 寫入慢            COPY + Temp Table + CTE        快 2~3 倍
  當機資料遺失          Kafka WAL + Offset 綁 TX       零資料遺失
  重複消費             change log status=INIT + TX    幂等性保證
  腦裂問題             Leader Lock 放進 DB TX          絕對安全
  新幣種開帳            Lazy Insert CTE                無需預建帳戶
  零停機部署            assign API + Leader Election   停頓 < 100ms
  百萬用戶             shard_id range partition        無限橫向擴展

  最終結果：
  ┌────────────────────────────────────────────────────┐
  │  吞吐量：avg 10萬/s，尖峰 100萬/s                  │
  │  延遲：  P95 < 50ms                                │
  │  一致性：錢一分不少，不多不少                      │
  │  可用性：Zero Downtime，多 AZ 容災                 │
  └────────────────────────────────────────────────────┘
```

axs 之所以強，是因為它：
1.  **完全不排隊**：用 Sharding 和單線程消滅了「鎖」。
2.  **記憶體運算**：避開了硬碟的龜速。
3.  **批次黑科技**：用 COPY 和 Temp Table 把資料庫寫入速度催到極限。
4.  **絕對安全**：用「資料庫交易綁定進度條」這招，保證了就算拔插頭，錢也一分不會少。

這就是一個**把物理極限（記憶體、IO）和邏輯安全（一致性）都算計到極致**的系統。
