# Chapter 7: 行情發布系統詳解

## 章節概述

本章實作交易所的**市場數據發布系統（Market Data Publisher）**，負責將撮合引擎產生的訂單簿變動與成交訊息發送給市場參與者。

### 技術目標

1. **低延遲廣播**：使用 UDP Multicast 實現微秒級延遲的市場數據發布
2. **增量更新與快照**：雙軌制設計確保數據完整性
3. **狀態重建**：快照合成器維護完整訂單簿狀態，定期發布快照

### 核心元件

| 元件 | 職責 | 通訊協定 |
|------|------|----------|
| **MarketDataPublisher** | 發布增量更新（Incremental Updates） | UDP Multicast |
| **SnapshotSynthesizer** | 生成與發布完整快照（Snapshots） | UDP Multicast |
| **MEMarketUpdate** | 市場數據更新消息格式 | 結構化數據 |

---

## 1. 市場數據更新消息格式

### 1.1 MarketUpdateType 枚舉

`market_update.h:11-20`

```cpp
enum class MarketUpdateType : uint8_t {
    INVALID = 0,
    CLEAR = 1,      // 清空訂單簿
    ADD = 2,        // 新增訂單
    MODIFY = 3,     // 修改訂單
    CANCEL = 4,     // 取消訂單
    TRADE = 5,      // 成交
    SNAPSHOT_START = 6,  // 快照開始標記
    SNAPSHOT_END = 7     // 快照結束標記
};
```

#### 更新類型說明

| 類型 | 用途 | 觸發時機 |
|------|------|----------|
| **CLEAR** | 清空特定標的的所有訂單 | 快照開始時 |
| **ADD** | 新增訂單到訂單簿 | 訂單被接受且未立即成交 |
| **MODIFY** | 更新訂單數量/價格 | 部分成交後剩餘數量變動 |
| **CANCEL** | 移除訂單 | 訂單被取消或完全成交 |
| **TRADE** | 成交事件 | 買賣雙方訂單撮合 |
| **SNAPSHOT_START** | 快照開始 | 快照發布序列的第一個消息 |
| **SNAPSHOT_END** | 快照結束 | 快照發布序列的最後一個消息 |

### 1.2 MEMarketUpdate 結構

`market_update.h:55-80`

```cpp
#pragma pack(push, 1)  // ⚡ 緊湊封裝：消除結構體填充，減少網路傳輸大小

struct MEMarketUpdate {
    MarketUpdateType type_ = MarketUpdateType::INVALID;
    OrderId order_id_ = OrderId_INVALID;
    TickerId ticker_id_ = TickerId_INVALID;
    Side side_ = Side::INVALID;
    Price price_ = Price_INVALID;
    Qty qty_ = Qty_INVALID;
    Priority priority_ = Priority_INVALID;
};

#pragma pack(pop)
```

#### 設計原理

**緊湊封裝（`#pragma pack(push, 1)`）**

- **目的**：消除編譯器自動添加的結構體填充（padding）
- **效果**：
  - 未封裝大小：可能 24 bytes（因編譯器對齊）
  - 封裝後大小：17 bytes（實際欄位總和）
  - 節省空間：~29%
- **適用場景**：網路傳輸、檔案儲存

**欄位設計**

- `type_`：指示更新類型（ADD/MODIFY/CANCEL 等）
- `order_id_`：訂單 ID（市場訂單 ID）
- `ticker_id_`：交易標的 ID
- `side_`、`price_`、`qty_`：訂單屬性
- `priority_`：時間優先權（用於排序）

### 1.3 MDPMarketUpdate 結構

`market_update.h:82-96`

```cpp
struct MDPMarketUpdate {
    size_t seq_num_ = 0;              // ⚡ 序列號：檢測丟包與排序
    MEMarketUpdate me_market_update_;  // 實際市場數據
};
```

#### 序列號（Sequence Number）的作用

**1. 丟包檢測（Packet Loss Detection）**

```
收到序列號：1, 2, 3, 5, 6  ← 發現丟失序列號 4
```

**2. 亂序處理（Out-of-Order Handling）**

```
收到順序：5, 3, 4, 2, 6, 1  ← 需要重新排序
正確順序：1, 2, 3, 4, 5, 6
```

**3. 快照定位（Snapshot Anchoring）**

```
快照：seq_num = 1000 (包含所有 ≤1000 的更新)
增量：seq_num = 1001, 1002, 1003, ...
```

---

## 2. MarketDataPublisher（市場數據發布器）

### 2.1 架構設計

`market_data_publisher.h:9-74`

#### 資料流向

```
Matching Engine
      ↓
MEMarketUpdateLFQueue (outgoing_md_updates_)
      ↓
MarketDataPublisher::run()
      ├─────────────────────┬────────────────────┐
      ↓                     ↓                    ↓
UDP Multicast        MDPMarketUpdateLFQueue  Sequence Number
(Incremental)        (snapshot_md_updates_)   (next_inc_seq_num_++)
      ↓                     ↓
市場參與者          SnapshotSynthesizer
(實時行情)          (快照生成器)
```

### 2.2 核心數據成員

`market_data_publisher.h:61-73`

```cpp
private:
    size_t next_inc_seq_num_ = 1;                  // 增量更新序列號生成器
    MEMarketUpdateLFQueue* outgoing_md_updates_;   // 來自撮合引擎的更新佇列
    MDPMarketUpdateLFQueue snapshot_md_updates_;   // 轉發給快照合成器

    volatile bool run_ = false;

    Common::McastSocket incremental_socket_;       // UDP Multicast 發送端
    SnapshotSynthesizer* snapshot_synthesizer_;    // 快照合成器
};
```

#### 雙佇列設計

| 佇列 | 類型 | 生產者 | 消費者 | 用途 |
|------|------|--------|--------|------|
| `outgoing_md_updates_` | MEMarketUpdateLFQueue | Matching Engine | MarketDataPublisher | 接收撮合結果 |
| `snapshot_md_updates_` | MDPMarketUpdateLFQueue | MarketDataPublisher | SnapshotSynthesizer | 轉發快照合成器 |

### 2.3 發布流程

`market_data_publisher.cpp:22-49`

```cpp
auto MarketDataPublisher::run() noexcept -> void {
    while (run_) {
        // 1. 從撮合引擎讀取市場數據更新
        for (auto market_update = outgoing_md_updates_->getNextToRead();
             outgoing_md_updates_->size() && market_update;
             market_update = outgoing_md_updates_->getNextToRead()) {

            // 2. 發送序列號（8 bytes）
            incremental_socket_.send(&next_inc_seq_num_, sizeof(next_inc_seq_num_));

            // 3. 發送市場數據更新（17 bytes）
            incremental_socket_.send(market_update, sizeof(MEMarketUpdate));
            outgoing_md_updates_->updateReadIndex();

            // 4. 轉發給快照合成器（帶序列號）
            auto next_write = snapshot_md_updates_.getNextToWriteTo();
            next_write->seq_num_ = next_inc_seq_num_;
            next_write->me_market_update_ = *market_update;
            snapshot_md_updates_.updateWriteIndex();

            // 5. 序列號遞增
            ++next_inc_seq_num_;
        }

        incremental_socket_.sendAndRecv();
    }
}
```

#### 發布流程圖

```
┌──────────────────────────────────────────────────────────┐
│ Step 1: 讀取更新                                          │
│   market_update = outgoing_md_updates_->getNextToRead()  │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ Step 2 & 3: UDP Multicast 發送                            │
│   send(seq_num)  ← 8 bytes                               │
│   send(MEMarketUpdate)  ← 17 bytes                       │
│   總計：25 bytes/更新                                     │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ Step 4: 轉發快照合成器                                    │
│   snapshot_md_updates_.write(MDPMarketUpdate)           │
└──────────────────────┬───────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────────────────┐
│ Step 5: 序列號遞增                                        │
│   ++next_inc_seq_num_                                    │
└──────────────────────────────────────────────────────────┘
```

#### 效能分析

**時間複雜度**：O(1) 每個更新
- Lock-Free Queue 讀取：O(1)
- UDP 發送：O(1)（系統呼叫）
- Lock-Free Queue 寫入：O(1)

**延遲特性**：
- 無批次處理：即時發送
- UDP 無確認：單向發送，無等待
- Multicast：一次發送，多方接收

---

## 3. SnapshotSynthesizer（快照合成器）

### 3.1 設計原理

快照合成器維護一個**完整的訂單簿狀態副本**，定期發布快照供市場參與者重建訂單簿。

#### 為何需要快照？

**問題：UDP 不可靠性**

```
增量更新序列：1, 2, 3, [4丟失], 5, 6, 7, ...
                            ↑
                      訂單簿狀態錯誤！
```

**解決方案：定期快照**

```
時間軸：
00:00 ─ 快照#1 (seq=1000)
00:01 ─ 增量更新 1001-1060
00:02 ─ 增量更新 1061-1120
...
01:00 ─ 快照#2 (seq=4500)  ← 每60秒發布快照
01:01 ─ 增量更新 4501-4560
```

### 3.2 核心數據結構

`snapshot_synthesizer.h:59-64`

```cpp
private:
    // 訂單簿狀態：ticker_orders_[ticker_id][order_id] → MEMarketUpdate*
    std::array<std::array<MEMarketUpdate*, ME_MAX_ORDER_IDS>, ME_MAX_TICKERS>
        ticker_orders_;

    size_t last_inc_seq_num_ = 0;     // 最後處理的增量序列號
    Nanos last_snapshot_time_ = 0;    // 最後快照發布時間

    MemPool<MEMarketUpdate> order_pool_;  // 訂單物件記憶體池
```

#### 數據結構設計

**二維陣列索引**

```
ticker_orders_[ticker_id][order_id] → MEMarketUpdate*

範例：
ticker_orders_[0][100] → Order{price=100.5, qty=100, ...}
ticker_orders_[0][101] → Order{price=100.0, qty=50, ...}
ticker_orders_[1][200] → Order{price=50.25, qty=200, ...}
```

**空間複雜度**：
- O(ME_MAX_TICKERS × ME_MAX_ORDER_IDS) 指標
- 8 tickers × 1M orders × 8 bytes = 64 MB

### 3.3 狀態更新流程

`snapshot_synthesizer.cpp:42-96`

```cpp
auto SnapshotSynthesizer::addToSnapshot(const MDPMarketUpdate* market_update) {
    const auto& me_market_update = market_update->me_market_update_;
    auto* orders = &ticker_orders_.at(me_market_update.ticker_id_);

    switch (me_market_update.type_) {
    case MarketUpdateType::ADD: {
        // ⚡ 新增訂單：從記憶體池配置，加入陣列
        auto order = orders->at(me_market_update.order_id_);
        ASSERT(order == nullptr, "訂單已存在");
        orders->at(me_market_update.order_id_) = order_pool_.allocate(me_market_update);
    }
    break;

    case MarketUpdateType::MODIFY: {
        // ⚡ 修改訂單：更新數量與價格
        auto order = orders->at(me_market_update.order_id_);
        ASSERT(order != nullptr, "訂單不存在");
        order->qty_ = me_market_update.qty_;
        order->price_ = me_market_update.price_;
    }
    break;

    case MarketUpdateType::CANCEL: {
        // ⚡ 取消訂單：歸還記憶體池，清空指標
        auto order = orders->at(me_market_update.order_id_);
        ASSERT(order != nullptr, "訂單不存在");
        order_pool_.deallocate(order);
        orders->at(me_market_update.order_id_) = nullptr;
    }
    break;
    }

    // ⚠️ 驗證序列號連續性
    ASSERT(market_update->seq_num_ == last_inc_seq_num_ + 1,
           "序列號必須連續");
    last_inc_seq_num_ = market_update->seq_num_;
}
```

#### 狀態轉換表

| 當前狀態 | 更新類型 | 操作 | 新狀態 |
|----------|---------|------|--------|
| `nullptr` | ADD | 配置新訂單 | `MEMarketUpdate*` |
| `MEMarketUpdate*` | MODIFY | 更新 qty/price | `MEMarketUpdate*` (修改) |
| `MEMarketUpdate*` | CANCEL | 歸還記憶體池 | `nullptr` |
| `nullptr` | MODIFY/CANCEL | **錯誤**（斷言失敗） | - |
| `MEMarketUpdate*` | ADD | **錯誤**（斷言失敗） | - |

### 3.4 快照發布流程

`snapshot_synthesizer.cpp:98-138`

```cpp
auto SnapshotSynthesizer::publishSnapshot() {
    size_t snapshot_size = 0;

    // 1. 發送 SNAPSHOT_START 標記
    const MDPMarketUpdate start_market_update{
        snapshot_size++,
        {MarketUpdateType::SNAPSHOT_START, last_inc_seq_num_}
    };
    snapshot_socket_.send(&start_market_update, sizeof(MDPMarketUpdate));

    // 2. 為每個交易標的發送完整訂單簿
    for (size_t ticker_id = 0; ticker_id < ticker_orders_.size(); ++ticker_id) {
        const auto& orders = ticker_orders_.at(ticker_id);

        // 2a. 發送 CLEAR 指令（清空客戶端訂單簿）
        MEMarketUpdate me_market_update;
        me_market_update.type_ = MarketUpdateType::CLEAR;
        me_market_update.ticker_id_ = ticker_id;
        const MDPMarketUpdate clear_market_update{snapshot_size++, me_market_update};
        snapshot_socket_.send(&clear_market_update, sizeof(MDPMarketUpdate));

        // 2b. 發送所有有效訂單
        for (const auto order : orders) {
            if (order) {
                const MDPMarketUpdate market_update{snapshot_size++, *order};
                snapshot_socket_.send(&market_update, sizeof(MDPMarketUpdate));
            }
        }
    }

    // 3. 發送 SNAPSHOT_END 標記
    const MDPMarketUpdate end_market_update{
        snapshot_size++,
        {MarketUpdateType::SNAPSHOT_END, last_inc_seq_num_}
    };
    snapshot_socket_.send(&end_market_update, sizeof(MDPMarketUpdate));
}
```

#### 快照消息序列範例

```
序列號  類型              內容
──────────────────────────────────────────
0       SNAPSHOT_START    seq=4500
1       CLEAR             ticker_id=0
2       ADD               Order{id=100, price=100.5, qty=100}
3       ADD               Order{id=101, price=100.0, qty=50}
4       ADD               Order{id=102, price=99.5, qty=200}
5       CLEAR             ticker_id=1
6       ADD               Order{id=200, price=50.25, qty=150}
...
N       SNAPSHOT_END      seq=4500
```

### 3.5 定時發布機制

`snapshot_synthesizer.cpp:140-163`

```cpp
void SnapshotSynthesizer::run() {
    while (run_) {
        // 1. 處理增量更新（維護訂單簿狀態）
        for (auto market_update = snapshot_md_updates_->getNextToRead();
             snapshot_md_updates_->size() && market_update;
             market_update = snapshot_md_updates_->getNextToRead()) {

            addToSnapshot(market_update);
            snapshot_md_updates_->updateReadIndex();
        }

        // 2. 每60秒發布一次快照
        if (getCurrentNanos() - last_snapshot_time_ > 60 * NANOS_TO_SECS) {
            last_snapshot_time_ = getCurrentNanos();
            publishSnapshot();
        }
    }
}
```

#### 時間軸示意

```
時間    動作
────────────────────────────────────────────────
00:00   啟動，last_snapshot_time_ = 當前時間
00:01   處理增量更新 1001-1060
00:02   處理增量更新 1061-1120
...
01:00   60秒到期 → 發布快照#1
01:01   處理增量更新 4501-4560
...
02:00   60秒到期 → 發布快照#2
```

---

## 4. UDP Multicast vs TCP 的設計權衡

### 4.1 為何選擇 UDP Multicast？

| 特性 | UDP Multicast | TCP |
|------|--------------|-----|
| **延遲** | 極低（單向發送） | 較高（三次握手、確認） |
| **吞吐量** | 高（無流控） | 受流控限制 |
| **擴展性** | 優秀（一次發送，多方接收） | 差（N個連接 = N次發送） |
| **可靠性** | 不保證（可能丟包） | 保證送達 |
| **順序性** | 不保證 | 保證順序 |

### 4.2 混合架構設計

本系統採用**雙軌制**：

```
                    Matching Engine
                           |
            ┌──────────────┴──────────────┐
            ↓                             ↓
    Incremental Updates          Snapshot Updates
    (UDP Multicast)              (UDP Multicast)
    每筆即時發送                   每60秒發送一次
            ↓                             ↓
      市場參與者 ←─────────────────────→ 市場參與者
      (實時訂閱)                        (恢復狀態)
```

#### 客戶端恢復策略

**場景1：正常訂閱**

```
1. 訂閱 Incremental Updates
2. 接收：seq=1, 2, 3, 4, 5, ...
3. 維護本地訂單簿
```

**場景2：丟包恢復**

```
1. 接收：seq=1, 2, 3, [4丟失], 5
2. 檢測到序列號跳躍（3 → 5）
3. 請求最新快照（seq=1000）
4. 重建訂單簿
5. 繼續接收增量更新（seq > 1000）
```

**場景3：新訂閱者加入**

```
1. 訂閱 Snapshot Updates
2. 等待下一個快照（最多60秒）
3. 接收完整快照（SNAPSHOT_START → CLEAR → ADD... → SNAPSHOT_END）
4. 切換到 Incremental Updates
```

---

## 5. 時間複雜度與效能分析

### 5.1 MarketDataPublisher 時間複雜度

| 操作 | 時間複雜度 | 說明 |
|------|-----------|------|
| 讀取更新 | O(1) | Lock-Free Queue |
| 發送 UDP | O(1) | 系統呼叫 |
| 寫入快照佇列 | O(1) | Lock-Free Queue |
| **每個更新總計** | **O(1)** | - |

### 5.2 SnapshotSynthesizer 時間複雜度

| 操作 | 時間複雜度 | 說明 |
|------|-----------|------|
| `addToSnapshot(ADD)` | O(1) | 陣列索引 + 記憶體池配置 |
| `addToSnapshot(MODIFY)` | O(1) | 陣列索引 + 欄位更新 |
| `addToSnapshot(CANCEL)` | O(1) | 陣列索引 + 記憶體池歸還 |
| `publishSnapshot()` | O(T × O) | T=標的數, O=訂單數 |

### 5.3 延遲分析

**增量更新延遲（Incremental Update Latency）**

```
撮合引擎生成更新
      ↓ (Lock-Free Queue 寫入：~20ns)
MarketDataPublisher 讀取
      ↓ (UDP 發送：~500ns - 2μs)
網路傳輸
      ↓ (區域網路：<100μs)
市場參與者接收
──────────────────────────────
總延遲：~1-3 微秒（同機房）
```

**快照發布延遲**

```
假設：8個標的，每個標的1000個訂單
消息數量：1 (START) + 8 (CLEAR) + 8000 (ADD) + 1 (END) = 8010 個消息
每個消息：25 bytes
總大小：8010 × 25 = 200 KB

發送時間：200 KB ÷ 10 Gbps ≈ 160 微秒
```

---

## 6. 常見問題與陷阱

### 6.1 序列號溢位

**問題**：
```cpp
size_t next_inc_seq_num_ = 1;  // 64位元
```

**分析**：
- 假設每秒10萬筆更新
- 溢位時間：2^64 ÷ 100,000 ÷ 86,400 ÷ 365 ≈ 58億年
- **結論**：實務上無需擔心

### 6.2 快照與增量的同步問題

**錯誤範例**：

```
快照：seq=1000 (包含訂單 A, B, C)
增量：seq=999 (取消訂單 C) ← 晚於快照送達
結果：訂單簿包含已取消的訂單 C（錯誤！）
```

**正確處理**：

```cpp
// 客戶端邏輯
if (incremental_update.seq_num_ <= last_snapshot_seq_num_) {
    // 捨棄過期更新
    return;
}
```

### 6.3 記憶體碎片化

**問題**：
```cpp
MemPool<MEMarketUpdate> order_pool_(ME_MAX_ORDER_IDS);  // 1M 個訂單
```

**優勢**：
- 預先配置：啟動時一次性配置所有記憶體
- 零碎片化：所有物件大小相同
- O(1) 配置：線性探測法

---

## 7. 實戰應用場景

### 7.1 行情訂閱客戶端

**最佳實踐**：

```cpp
class MarketDataClient {
    void onIncrementalUpdate(const MDPMarketUpdate& update) {
        // 檢查序列號
        if (update.seq_num_ != expected_seq_num_) {
            requestSnapshot();  // 發現丟包，請求快照
            return;
        }

        // 更新本地訂單簿
        applyUpdate(update.me_market_update_);
        ++expected_seq_num_;
    }

    void onSnapshot(const vector<MDPMarketUpdate>& snapshot) {
        // 清空訂單簿
        order_book_.clear();

        // 重建訂單簿
        for (const auto& update : snapshot) {
            applyUpdate(update.me_market_update_);
        }

        // 更新預期序列號
        expected_seq_num_ = snapshot.back().seq_num_ + 1;
    }
};
```

### 7.2 效能監控

**關鍵指標**：

```cpp
// 發布延遲
auto publish_latency = getCurrentNanos() - order_generation_time;

// 佇列深度（背壓指標）
auto queue_depth = outgoing_md_updates_->size();
if (queue_depth > THRESHOLD) {
    LOG_WARNING("Market data queue backlog: {}", queue_depth);
}

// 丟包率（客戶端）
auto packet_loss_rate = (missed_seq_nums / total_updates) * 100;
```

---

## 技術名詞中英對照

| 中文 | 英文 | 說明 |
|------|------|------|
| 增量更新 | Incremental Update | 訂單簿的變動消息 |
| 快照 | Snapshot | 完整訂單簿狀態 |
| 序列號 | Sequence Number | 消息順序編號 |
| 多播 | Multicast | 一對多傳輸 |
| 丟包 | Packet Loss | UDP 數據包遺失 |
| 緊湊封裝 | Packed Structure | 無填充的結構體 |
| 快照合成器 | Snapshot Synthesizer | 生成快照的元件 |
| 背壓 | Backpressure | 佇列堆積壓力 |

---

## 總結

### 關鍵設計決策

1. **UDP Multicast**：犧牲可靠性換取極低延遲與高擴展性
2. **雙軌制**：增量更新提供實時性，快照提供容錯性
3. **序列號**：檢測丟包與亂序
4. **定時快照**：60秒週期平衡數據新鮮度與頻寬成本

### 效能特性

- **增量更新延遲**：1-3 微秒（同機房）
- **快照發布大小**：~200 KB（8標的 × 1000訂單）
- **記憶體佔用**：64 MB（指標陣列）

### 擴展方向

- **壓縮**：使用 Snappy/LZ4 壓縮快照
- **多通道**：按標的分離到不同 Multicast 群組
- **增量壓縮**：只發送變動欄位（Delta Encoding）
