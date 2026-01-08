# Chapter 6:撮合引擎核心詳解

## 章節概述

本章實作了交易系統的**撮合引擎**(Matching Engine),負責處理訂單的撮合與管理。撮合引擎是交易所的核心,決定了系統的吞吐量和延遲表現。

### 核心元件

1. **MEOrder**(訂單):單一訂單的資料結構,使用雙向鏈結串列組織
2. **MEOrdersAtPrice**(價格層級):管理同一價格的所有訂單
3. **MEOrderBook**(訂單簿):完整的買賣盤,實現 Price-Time Priority
4. **MatchingEngine**(撮合引擎):主控制器,處理訂單請求並執行撮合

### 設計原則

- **Price-Time Priority**:價格優先、時間優先的撮合規則
- **FIFO 撮合**:同價格訂單按到達順序撮合
- **零動態分配**:使用 Memory Pool 預先配置所有訂單物件
- **Cache 友善**:雙向鏈結串列 + Hash Map 混合設計,平衡存取速度

---

## 一、基礎型別定義

### 📄 檔案位置
- `Chapter6/common/types.h`(第 10-112 行)

### 1.1 核心型別

```cpp
// 訂單 ID: 客戶端訂單 ID 與市場訂單 ID
typedef uint64_t OrderId;
constexpr auto OrderId_INVALID = std::numeric_limits<OrderId>::max();

// 股票代碼 ID
typedef uint32_t TickerId;
constexpr auto TickerId_INVALID = std::numeric_limits<TickerId>::max();

// 客戶 ID
typedef uint32_t ClientId;
constexpr auto ClientId_INVALID = std::numeric_limits<ClientId>::max();

// 價格(使用整數避免浮點數精度問題)
typedef int64_t Price;
constexpr auto Price_INVALID = std::numeric_limits<Price>::max();

// 數量
typedef uint32_t Qty;
constexpr auto Qty_INVALID = std::numeric_limits<Qty>::max();

// 優先級(用於 Time Priority)
typedef uint64_t Priority;
constexpr auto Priority_INVALID = std::numeric_limits<Priority>::max();
```

### 1.2 買賣方向

```cpp
enum class Side : int8_t {
    INVALID = 0,
    BUY = 1,      // 買單
    SELL = -1     // 賣單(使用 -1 便於某些計算)
};
```

**為什麼使用 `int8_t` 而非 `bool`?**

- `int8_t` 允許三種狀態:INVALID、BUY、SELL
- SELL = -1 在某些數學運算中有特殊用途(如計算 spread 時可直接相乘)

### 1.3 系統容量限制

```cpp
constexpr size_t ME_MAX_TICKERS = 8;              // 最多 8 個交易品種
constexpr size_t ME_MAX_NUM_CLIENTS = 256;        // 最多 256 個客戶
constexpr size_t ME_MAX_ORDER_IDS = 1024 * 1024;  // 每個客戶最多 1M 訂單
constexpr size_t ME_MAX_PRICE_LEVELS = 256;       // 最多 256 個價格層級
```

**容量設計考量**:
- `ME_MAX_PRICE_LEVELS = 256`:假設市場價格波動不超過 256 個檔位
- `ME_MAX_ORDER_IDS = 1M`:預先配置記憶體池,避免執行時分配
- 所有容量都是 2 的冪次方,便於 Hash Map 索引計算

---

## 二、MEOrder:訂單資料結構

### 📄 檔案位置
- `Chapter6/exchange/matcher/me_order.h`(第 11-37 行)

### 2.1 訂單結構設計

```cpp
struct MEOrder {
    // 訂單基本資訊
    TickerId ticker_id_ = TickerId_INVALID;        // 股票代碼
    ClientId client_id_ = ClientId_INVALID;        // 客戶 ID
    OrderId client_order_id_ = OrderId_INVALID;    // 客戶端訂單 ID
    OrderId market_order_id_ = OrderId_INVALID;    // 市場訂單 ID(交易所分配)

    // 訂單屬性
    Side side_ = Side::INVALID;                    // 買賣方向
    Price price_ = Price_INVALID;                  // 價格
    Qty qty_ = Qty_INVALID;                        // 數量(剩餘未成交數量)
    Priority priority_ = Priority_INVALID;         // 優先級(時間戳)

    // ⚡ 雙向鏈結串列指標
    MEOrder* prev_order_ = nullptr;                // 前一個訂單
    MEOrder* next_order_ = nullptr;                // 後一個訂單
};
```

### 2.2 雙向鏈結串列設計

**為什麼使用雙向鏈結串列?**

撮合引擎需要頻繁執行以下操作:
1. **在鏈結串列中間插入訂單**:O(1)
2. **刪除鏈結串列中間的訂單**:O(1)(需要雙向指標)
3. **遍歷同價格的所有訂單**:O(N)

**單向 vs 雙向鏈結串列**:

| 操作 | 單向鏈結串列 | 雙向鏈結串列 |
|------|------------|------------|
| 插入(已知位置) | O(1) | O(1) |
| 刪除(已知位置) | O(N)(需找前驅節點) | O(1) |
| 記憶體開銷 | 1 個指標 | 2 個指標 |

**權衡**:雙向鏈結串列多佔用 8 bytes(64-bit 系統),但刪除操作從 O(N) 降至 O(1),對撮合引擎至關重要。

### 2.3 環形鏈結串列

**特殊設計**:同價格的訂單形成**環形雙向鏈結串列**

```
假設價格 100 有 3 個訂單:Order1 -> Order2 -> Order3

環形結構:
Order1.prev_order_ = Order3  ──┐
Order1.next_order_ = Order2    │
                               │
Order2.prev_order_ = Order1    │
Order2.next_order_ = Order3    │
                               │
Order3.prev_order_ = Order2    │
Order3.next_order_ = Order1  ←─┘
```

**優勢**:
- **判斷單一元素**:`order->prev_order_ == order`
- **快速插入尾部**:不需要遍歷到尾部,直接從 `first_order->prev_order_` 取得
- **簡化邊界處理**:不需要特殊處理頭尾節點

---

## 三、MEOrdersAtPrice:價格層級

### 📄 檔案位置
- `Chapter6/exchange/matcher/me_order.h`(第 42-73 行)

### 3.1 價格層級結構

```cpp
struct MEOrdersAtPrice {
    Side side_ = Side::INVALID;              // 買單或賣單
    Price price_ = Price_INVALID;            // 價格

    MEOrder* first_me_order_ = nullptr;      // 該價格的第一個訂單(環形鏈結串列頭)

    // ⚡ 雙向鏈結串列指標(連接不同價格層級)
    MEOrdersAtPrice* prev_entry_ = nullptr;  // 前一個價格層級
    MEOrdersAtPrice* next_entry_ = nullptr;  // 後一個價格層級
};
```

### 3.2 價格層級的排序

**買單(Bids)**:價格**由高到低**排列
```
bids_by_price_ -> [Price=105] -> [Price=104] -> [Price=103] -> ...
                     (最佳買價)
```

**賣單(Asks)**:價格**由低到高**排列
```
asks_by_price_ -> [Price=106] -> [Price=107] -> [Price=108] -> ...
                     (最佳賣價)
```

**原因**:
- 買單頭部(bids_by_price_)是**最高買價**,最有可能成交
- 賣單頭部(asks_by_price_)是**最低賣價**,最有可能成交
- 撮合時直接從頭部開始,無需搜尋

### 3.3 Hash Map 索引

```cpp
// 價格 -> MEOrdersAtPrice* 的 Hash Map
typedef std::array<MEOrdersAtPrice*, ME_MAX_PRICE_LEVELS> OrdersAtPriceHashMap;

// 索引計算
auto priceToIndex(Price price) const noexcept {
    return (price % ME_MAX_PRICE_LEVELS);  // 簡單的模運算
}
```

**Hash 衝突處理**:
- 本實作**未處理衝突**,假設價格不會衝突(price % 256 唯一)
- 生產環境需要使用鏈結法(Chaining)或開放定址法(Open Addressing)

**為什麼用 Hash Map + 鏈結串列混合設計?**

| 操作 | 只用鏈結串列 | 只用 Hash Map | 混合設計 |
|------|------------|-------------|----------|
| 查找價格層級 | O(N) | O(1) | **O(1)** |
| 遍歷所有價格(排序) | O(N) | O(N log N) | **O(N)** |
| 插入新價格層級 | O(N) | O(1) | **O(N)** |

混合設計在**查找**和**遍歷**時都保持最佳效能。

---

## 四、MEOrderBook:訂單簿

### 📄 檔案位置
- `Chapter6/exchange/matcher/me_order_book.h`(第 17-243 行)

### 4.1 訂單簿核心成員

```cpp
class MEOrderBook final {
private:
    TickerId ticker_id_;                           // 股票代碼
    MatchingEngine* matching_engine_;              // 撮合引擎引用

    // ⚡ 核心資料結構
    ClientOrderHashMap cid_oid_to_order_;          // Client/Order ID -> MEOrder*

    MemPool<MEOrdersAtPrice> orders_at_price_pool_; // 價格層級記憶體池
    MEOrdersAtPrice* bids_by_price_ = nullptr;      // 買單鏈結串列頭(最高價)
    MEOrdersAtPrice* asks_by_price_ = nullptr;      // 賣單鏈結串列頭(最低價)

    OrdersAtPriceHashMap price_orders_at_price_;    // Price -> MEOrdersAtPrice*

    MemPool<MEOrder> order_pool_;                   // 訂單記憶體池

    OrderId next_market_order_id_ = 1;              // 下一個市場訂單 ID
};
```

### 4.2 三層查找結構

**層級 1:Client + Order ID 查找**
```cpp
// 快速查找特定客戶的特定訂單
typedef std::array<MEOrder*, ME_MAX_ORDER_IDS> OrderHashMap;
typedef std::array<OrderHashMap, ME_MAX_NUM_CLIENTS> ClientOrderHashMap;

ClientOrderHashMap cid_oid_to_order_;

// 用法
auto order = cid_oid_to_order_[client_id][order_id];  // O(1)
```

**層級 2:Price 查找**
```cpp
// 快速查找特定價格的所有訂單
OrdersAtPriceHashMap price_orders_at_price_;

// 用法
auto orders_at_price = price_orders_at_price_[price % ME_MAX_PRICE_LEVELS];  // O(1)
```

**層級 3:Price 排序遍歷**
```cpp
// 按價格順序遍歷(撮合時使用)
MEOrdersAtPrice* bids_by_price_;  // 買單:從高到低
MEOrdersAtPrice* asks_by_price_;  // 賣單:從低到高
```

**記憶體佈局**:
```
cid_oid_to_order_[256][1M]:  256 * 1M * 8 bytes =   2GB(指標陣列)
price_orders_at_price_[256]:       256 * 8 bytes =   2KB
order_pool_:                       1M * 96 bytes =  96MB(預先配置)
orders_at_price_pool_:            256 * 64 bytes =  16KB

總計:約 2.1GB(主要是 cid_oid_to_order_ 的稀疏陣列)
```

**優化方向**:
- `cid_oid_to_order_` 可改用稀疏 Hash Map,減少記憶體浪費
- 但當前設計優先考慮**存取速度**而非記憶體使用

### 4.3 addOrdersAtPrice:插入價格層級

**目標**:將新價格層級插入到排序的鏈結串列中

**演算法**:
1. 如果是第一個價格層級,建立環形鏈結串列
2. 否則,尋找插入位置:
   - 買單:找到第一個價格**小於等於**新價格的位置
   - 賣單:找到第一個價格**大於等於**新價格的位置
3. 插入鏈結串列
4. 如果新價格成為最佳價格,更新 `bids_by_price_` 或 `asks_by_price_`

**核心程式碼**(`me_order_book.h:83-148`):

```cpp
auto addOrdersAtPrice(MEOrdersAtPrice* new_orders_at_price) noexcept {
    // 加入 Hash Map
    price_orders_at_price_.at(priceToIndex(new_orders_at_price->price_)) = new_orders_at_price;

    const auto best_orders_by_price = (new_orders_at_price->side_ == Side::BUY ?
                                       bids_by_price_ : asks_by_price_);

    if (UNLIKELY(!best_orders_by_price)) {
        // ⚡ 情況 1:第一個價格層級,建立環形鏈結串列
        (new_orders_at_price->side_ == Side::BUY ? bids_by_price_ : asks_by_price_) =
            new_orders_at_price;
        new_orders_at_price->prev_entry_ = new_orders_at_price->next_entry_ = new_orders_at_price;
    } else {
        // ⚡ 情況 2:插入排序鏈結串列
        auto target = best_orders_by_price;

        // 判斷是插入 target 之前還是之後
        bool add_after = ((new_orders_at_price->side_ == Side::SELL &&
                           new_orders_at_price->price_ > target->price_) ||
                          (new_orders_at_price->side_ == Side::BUY &&
                           new_orders_at_price->price_ < target->price_));

        // 尋找正確的插入位置
        while (add_after && target != best_orders_by_price) {
            target = target->next_entry_;
            add_after = /* 繼續判斷 */;
        }

        if (add_after) {
            // 插入 target 之後
            new_orders_at_price->prev_entry_ = target;
            new_orders_at_price->next_entry_ = target->next_entry_;
            target->next_entry_->prev_entry_ = new_orders_at_price;
            target->next_entry_ = new_orders_at_price;
        } else {
            // 插入 target 之前
            new_orders_at_price->prev_entry_ = target->prev_entry_;
            new_orders_at_price->next_entry_ = target;
            target->prev_entry_->next_entry_ = new_orders_at_price;
            target->prev_entry_ = new_orders_at_price;

            // ⚡ 如果成為最佳價格,更新頭指標
            if ((new_orders_at_price->side_ == Side::BUY &&
                 new_orders_at_price->price_ > best_orders_by_price->price_) ||
                (new_orders_at_price->side_ == Side::SELL &&
                 new_orders_at_price->price_ < best_orders_by_price->price_)) {
                (new_orders_at_price->side_ == Side::BUY ? bids_by_price_ : asks_by_price_) =
                    new_orders_at_price;
            }
        }
    }
}
```

**時間複雜度**:
- **最佳情況**:O(1)(新價格是最佳價格或最差價格)
- **最壞情況**:O(N)(需要遍歷所有價格層級)
- **平均情況**:O(log N)(假設價格分佈均勻)

---

## 五、Price-Time Priority 撮合規則

### 5.1 撮合原則

**Price Priority(價格優先)**:
- 買單:價格高的優先成交
- 賣單:價格低的優先成交

**Time Priority(時間優先)**:
- 同價格:先到的訂單優先成交
- 使用 `priority_` 欄位記錄到達順序

### 5.2 Priority 計算

```cpp
auto getNextPriority(Price price) noexcept {
    const auto orders_at_price = getOrdersAtPrice(price);

    if (!orders_at_price) {
        return 1lu;  // 第一個訂單,priority = 1
    }

    // ⚡ 環形鏈結串列:最後一個訂單是 first_order->prev_order_
    return orders_at_price->first_me_order_->prev_order_->priority_ + 1;
}
```

**範例**:
```
價格 100 的訂單:
Order1: priority = 1 (10:00:00.000)
Order2: priority = 2 (10:00:00.100)
Order3: priority = 3 (10:00:00.200)

新訂單到達:
new_order.priority_ = getNextPriority(100) = 3 + 1 = 4
```

### 5.3 FIFO 撮合順序

**買單撮合範例**:
```
賣盤:
Price=106, Qty=100, Priority=1  ← asks_by_price_(最低賣價)
Price=107, Qty=200, Priority=2
Price=108, Qty=150, Priority=3

新買單到達:
Side=BUY, Price=107, Qty=250

撮合流程:
1. 檢查 asks_by_price_(106):107 >= 106 → 成交 100 (剩餘 150)
2. 檢查下一個(107):107 >= 107 → 成交 150 (剩餘 0)
3. 撮合完成,買單完全成交
```

---

## 六、撮合演算法實作

### 📄 檔案位置
- `Chapter6/exchange/matcher/me_order_book.cpp`(第 68-100 行)

### 6.1 checkForMatch:撮合檢查

```cpp
auto MEOrderBook::checkForMatch(ClientId client_id, OrderId client_order_id,
                                TickerId ticker_id, Side side, Price price, Qty qty,
                                Qty new_market_order_id) noexcept {
    auto leaves_qty = qty;  // 剩餘未成交數量

    if (side == Side::BUY) {
        // ⚡ 買單:逐一檢查賣盤
        while (leaves_qty && asks_by_price_) {
            const auto ask_itr = asks_by_price_->first_me_order_;

            if (LIKELY(price < ask_itr->price_)) {
                break;  // 買價低於最低賣價,無法成交
            }

            // 執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id,
                  ask_itr, &leaves_qty);
        }
    }

    if (side == Side::SELL) {
        // ⚡ 賣單:逐一檢查買盤
        while (leaves_qty && bids_by_price_) {
            const auto bid_itr = bids_by_price_->first_me_order_;

            if (LIKELY(price > bid_itr->price_)) {
                break;  // 賣價高於最高買價,無法成交
            }

            // 執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id,
                  bid_itr, &leaves_qty);
        }
    }

    return leaves_qty;  // 返回剩餘未成交數量
}
```

### 6.2 match:單筆撮合

```cpp
auto MEOrderBook::match(TickerId ticker_id, ClientId client_id, Side side,
                        OrderId client_order_id, OrderId new_market_order_id,
                        MEOrder* itr, Qty* leaves_qty) noexcept {
    const auto order = itr;
    const auto order_qty = order->qty_;

    // ⚡ 計算成交數量:取兩者較小值
    const auto fill_qty = std::min(*leaves_qty, order_qty);

    // 更新剩餘數量
    *leaves_qty -= fill_qty;
    order->qty_ -= fill_qty;

    // 🔔 發送成交回應給主動方(新訂單)
    client_response_ = {ClientResponseType::FILLED, client_id, ticker_id,
                        client_order_id, new_market_order_id, side,
                        itr->price_, fill_qty, *leaves_qty};
    matching_engine_->sendClientResponse(&client_response_);

    // 🔔 發送成交回應給被動方(掛單)
    client_response_ = {ClientResponseType::FILLED, order->client_id_, ticker_id,
                        order->client_order_id_, order->market_order_id_,
                        order->side_, itr->price_, fill_qty, order->qty_};
    matching_engine_->sendClientResponse(&client_response_);

    // 📊 發送市場更新(成交資訊)
    market_update_ = {MarketUpdateType::TRADE, OrderId_INVALID, ticker_id,
                      side, itr->price_, fill_qty, Priority_INVALID};
    matching_engine_->sendMarketUpdate(&market_update_);

    // ⚡ 如果掛單完全成交,移除訂單
    if (!order->qty_) {
        market_update_ = {MarketUpdateType::CANCEL, order->market_order_id_,
                          ticker_id, order->side_, order->price_, order_qty,
                          Priority_INVALID};
        matching_engine_->sendMarketUpdate(&market_update_);
        removeOrder(order);  // 從訂單簿移除並歸還記憶體池
    } else {
        // 部分成交,發送數量修改通知
        market_update_ = {MarketUpdateType::MODIFY, order->market_order_id_,
                          ticker_id, order->side_, order->price_, order->qty_,
                          order->priority_};
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}
```

**撮合流程圖**:
```
新訂單到達
    ↓
checkForMatch()
    ↓
找到對手盤訂單
    ↓
match() ← 計算成交數量
    ↓
發送成交回應(雙方)
    ↓
發送市場更新(TRADE)
    ↓
更新或移除掛單
    ↓
是否還有剩餘? → Yes → 繼續撮合
    ↓ No
返回剩餘數量
```

---

## 七、訂單生命週期

### 7.1 新增訂單流程

```
1. MatchingEngine::processClientRequest(NEW)
       ↓
2. MEOrderBook::add(client_id, order_id, ticker_id, side, price, qty)
       ↓
3. checkForMatch() ← 嘗試撮合
       ↓
4. 如果有剩餘數量:
   - generateNewMarketOrderId() ← 分配市場訂單 ID
   - order_pool_.allocate() ← 從記憶體池分配
   - addOrder() ← 加入訂單簿
   - cid_oid_to_order_[client_id][order_id] = order ← 建立索引
   - sendClientResponse(ACCEPTED) ← 通知客戶
   - sendMarketUpdate(ADD) ← 通知市場
       ↓
5. 完成
```

### 7.2 取消訂單流程

```
1. MatchingEngine::processClientRequest(CANCEL)
       ↓
2. MEOrderBook::cancel(client_id, order_id, ticker_id)
       ↓
3. cid_oid_to_order_[client_id][order_id] ← 查找訂單
       ↓
4. 如果找到:
   - removeOrder(order) ← 從訂單簿移除
   - order_pool_.deallocate(order) ← 歸還記憶體池
   - sendClientResponse(CANCELED) ← 通知客戶
   - sendMarketUpdate(CANCEL) ← 通知市場
       ↓
5. 完成
```

### 7.3 訂單狀態機

```
        NEW
         │
         ↓
    [檢查撮合]
         │
    ┌────┴────┐
    │         │
 完全成交   部分成交
    │         │
    ↓         ↓
 FILLED    [加入訂單簿]
              │
              ↓
           ACCEPTED
              │
         ┌────┴────┐
         │         │
      再次成交   取消
         │         │
         ↓         ↓
    FILLED/    CANCELED
    MODIFIED
```

---

## 八、記憶體管理與效能

### 8.1 Memory Pool 使用

```cpp
// 訂單記憶體池:預先配置 1M 個訂單
MemPool<MEOrder> order_pool_{ME_MAX_ORDER_IDS};

// 價格層級記憶體池:預先配置 256 個價格層級
MemPool<MEOrdersAtPrice> orders_at_price_pool_{ME_MAX_PRICE_LEVELS};
```

**優勢**:
- **零執行時分配**:所有訂單從記憶體池取得,延遲穩定
- **Cache 友善**:MEOrder 物件在記憶體中連續排列
- **避免碎片化**:記憶體池容量固定,不會產生碎片

### 8.2 操作複雜度分析

| 操作 | 時間複雜度 | 說明 |
|------|-----------|------|
| 查找訂單(by Client+Order ID) | O(1) | `cid_oid_to_order_[cid][oid]` |
| 查找價格層級 | O(1) | `price_orders_at_price_[price % 256]` |
| 插入新訂單 | O(1) | 插入環形鏈結串列尾部 |
| 刪除訂單 | O(1) | 雙向鏈結串列刪除 |
| 插入新價格層級 | O(N) | N = 價格層級數量(通常 < 50) |
| 撮合單筆訂單 | O(M) | M = 對手盤訂單數量 |

### 8.3 記憶體佈局最佳化

**MEOrder 記憶體佈局**:
```cpp
struct MEOrder {
    // 8 bytes 對齊的成員
    TickerId ticker_id_;      // 4 bytes
    ClientId client_id_;      // 4 bytes
    OrderId client_order_id_; // 8 bytes
    OrderId market_order_id_; // 8 bytes
    Side side_;               // 1 byte
    // [padding: 7 bytes]
    Price price_;             // 8 bytes
    Qty qty_;                 // 4 bytes
    Priority priority_;       // 8 bytes (padding 會自動調整)
    MEOrder* prev_order_;     // 8 bytes
    MEOrder* next_order_;     // 8 bytes
};
// 總計:~96 bytes(取決於對齊)
```

**Cache Line 利用率**:
- Cache Line = 64 bytes
- MEOrder = 96 bytes → 跨越 2 個 Cache Line
- 存取單一 MEOrder 可能產生 2 次 Cache Miss

**優化方向**:
- 將常用欄位(price, qty, side)放在前 64 bytes
- 將較少用的欄位(priority, client_order_id)放在後 32 bytes

---

## 九、MatchingEngine:主控制器

### 📄 檔案位置
- `Chapter6/exchange/matcher/matching_engine.h`(第 15-113 行)

### 9.1 核心成員

```cpp
class MatchingEngine final {
private:
    // ⚡ 每個 Ticker 一個訂單簿
    OrderBookHashMap ticker_order_book_;  // std::array<MEOrderBook*, 8>

    // ⚡ Lock-Free Queue 通訊
    ClientRequestLFQueue* incoming_requests_;        // 接收訂單請求
    ClientResponseLFQueue* outgoing_ogw_responses_;  // 發送訂單回應
    MEMarketUpdateLFQueue* outgoing_md_updates_;     // 發送市場更新

    volatile bool run_ = false;  // 運行標誌
    Logger logger_;              // 日誌記錄器
};
```

### 9.2 主迴圈

```cpp
auto run() noexcept {
    while (run_) {
        // ⚡ 從 Lock-Free Queue 讀取客戶請求
        const auto me_client_request = incoming_requests_->getNextToRead();

        if (LIKELY(me_client_request)) {
            // 處理請求
            processClientRequest(me_client_request);

            // 更新讀取索引
            incoming_requests_->updateReadIndex();
        }
    }
}
```

**特性**:
- **Busy-Wait**:持續輪詢 Lock-Free Queue,不休眠
- **單執行緒**:撮合引擎在單一執行緒中運行,避免鎖競爭
- **CPU 親和性**:綁定到專用 CPU 核心(Chapter 4 的 Thread Utils)

### 9.3 通訊架構

```
┌──────────────┐         ┌─────────────────┐         ┌──────────────┐
│ Order Server │─ NEW  ─→│ Matching Engine │─ FILLED→│ Order Gateway│
│              │←ACCEPT──│                 │         │              │
└──────────────┘         └─────────────────┘         └──────────────┘
                                  │
                                  │ TRADE/ADD/CANCEL
                                  ↓
                         ┌──────────────────┐
                         │ Market Data Pub  │
                         └──────────────────┘
```

**Lock-Free Queue 的角色**:
- `incoming_requests_`:接收 Order Server 的訂單請求
- `outgoing_ogw_responses_`:發送回應給 Order Gateway
- `outgoing_md_updates_`:發送市場更新給 Market Data Publisher

---

## 十、實戰應用與最佳實踐

### 10.1 訂單簿快照

**問題:如何高效生成訂單簿快照?**

```cpp
// ❌ 低效做法:逐一遍歷所有訂單
for (auto price_level : all_price_levels) {
    for (auto order : price_level->orders) {
        snapshot.add(order);  // O(N*M)
    }
}

// ✅ 高效做法:只遍歷價格層級
auto bids = bids_by_price_;
for (int i = 0; i < 10 && bids; ++i) {  // 只取前 10 檔
    snapshot.add_bid(bids->price_, get_total_qty(bids));
    bids = bids->next_entry_;
}
```

**快照格式**:
```
Ticker: AAPL
Bids (Top 5):
  Price=150.10, Qty=1000
  Price=150.05, Qty=500
  Price=150.00, Qty=2000
  Price=149.95, Qty=1500
  Price=149.90, Qty=800
Asks (Top 5):
  Price=150.15, Qty=600
  Price=150.20, Qty=1200
  Price=150.25, Qty=900
  Price=150.30, Qty=1100
  Price=150.35, Qty=700
```

### 10.2 防禦性程式設計

**檢查訂單合法性**:
```cpp
// 在 add() 開頭加入檢查
ASSERT(price > 0 && price < Price_INVALID, "Invalid price");
ASSERT(qty > 0 && qty < Qty_INVALID, "Invalid quantity");
ASSERT(side == Side::BUY || side == Side::SELL, "Invalid side");
```

**防止重複訂單 ID**:
```cpp
auto existing_order = cid_oid_to_order_[client_id][order_id];
if (existing_order) {
    logger_->log("Duplicate order ID: client=%s order=%s\n",
                 clientIdToString(client_id),
                 orderIdToString(order_id));
    sendClientResponse({ClientResponseType::REJECTED, ...});
    return;
}
```

### 10.3 效能調校

**1. 使用 LIKELY/UNLIKELY 提示**:
```cpp
if (LIKELY(price < ask_itr->price_)) {
    break;  // 大多數情況:買價低於賣價
}

if (UNLIKELY(!best_orders_by_price)) {
    // 罕見情況:第一個價格層級
}
```

**2. 避免不必要的記憶體複製**:
```cpp
// ❌ 複製整個 MEOrder
*next_write = order;

// ✅ 使用 std::move
*next_write = std::move(order);
```

**3. 預先計算常用值**:
```cpp
// 在 MEOrdersAtPrice 中快取總數量
struct MEOrdersAtPrice {
    Qty total_qty_;  // 該價格的總數量
    // 每次 add/remove 訂單時更新
};
```

---

## 十一、常見陷阱與調試

### 11.1 環形鏈結串列陷阱

**❌ 錯誤 1:忘記環形結構**
```cpp
// 插入第一個訂單時
order->prev_order_ = nullptr;  // ⚠️ 錯誤!應該指向自己
order->next_order_ = nullptr;
```

**✅ 正確做法**:
```cpp
order->prev_order_ = order;
order->next_order_ = order;
```

**❌ 錯誤 2:判斷單一元素**
```cpp
if (order->next_order_ == nullptr) {  // ⚠️ 錯誤!
```

**✅ 正確做法**:
```cpp
if (order->prev_order_ == order) {  // 只有一個元素
```

### 11.2 Hash 衝突

**問題**:
```cpp
Price p1 = 100;
Price p2 = 356;  // 356 % 256 = 100
// 兩個價格映射到同一索引!
```

**解決方案**:
- 擴大 `ME_MAX_PRICE_LEVELS`(如改為 1024)
- 使用更好的 Hash 函數
- 實作衝突處理(鏈結法)

### 11.3 調試工具

**toString() 方法**:
```cpp
auto MEOrderBook::toString(bool detailed, bool validity_check) const -> std::string {
    std::stringstream ss;

    // 列印買單
    ss << "Bids:\n";
    auto bids = bids_by_price_;
    while (bids) {
        ss << bids->toString();
        if (detailed) {
            auto order = bids->first_me_order_;
            do {
                ss << "  " << order->toString() << "\n";
                order = order->next_order_;
            } while (order != bids->first_me_order_);
        }
        bids = bids->next_entry_;
    }

    // 列印賣單
    ss << "Asks:\n";
    // ... 類似邏輯

    return ss.str();
}
```

---

## 十二、技術名詞對照表

| 英文 | 繁體中文 | 說明 |
|------|---------|------|
| Matching Engine | 撮合引擎 | 處理訂單撮合的核心元件 |
| Order Book | 訂單簿 | 記錄所有未成交訂單的資料結構 |
| Price-Time Priority | 價格時間優先 | 價格優先、相同價格時間優先的撮合規則 |
| FIFO | 先進先出 | First In First Out,同價格先到先撮合 |
| Bid | 買單 | 買方掛單 |
| Ask | 賣單 | 賣方掛單 |
| Fill | 成交 | 訂單被撮合 |
| Leaves Qty | 剩餘數量 | 訂單未成交的數量 |
| Doubly Linked List | 雙向鏈結串列 | 每個節點有前後兩個指標 |
| Circular Linked List | 環形鏈結串列 | 尾節點指向頭節點 |
| Hash Map | 雜湊表 | 鍵值對映資料結構 |
| Price Level | 價格層級 | 同一價格的所有訂單 |

---

## 十三、總結

Chapter 6 實作了交易系統的核心:撮合引擎。關鍵設計包括:

1. **三層索引結構**:Client+Order ID、Price、排序鏈結串列
2. **Price-Time Priority**:嚴格的撮合規則保證公平性
3. **混合資料結構**:Hash Map(快速查找)+ 雙向鏈結串列(排序遍歷)
4. **零動態分配**:使用 Memory Pool 預先配置所有物件
5. **單執行緒設計**:避免鎖競爭,延遲可預測

雖然當前實作尚未達到極致優化(如 Hash 衝突處理、Cache Line 對齊),但已展現了低延遲撮合引擎的核心思想。

**下一步**:
- **Chapter 7**:Market Data Publisher,發布撮合結果
- **Chapter 8**:Order Gateway,接收客戶訂單
- **Chapter 11-12**:效能優化與基準測試

---

**參考資料**:
- [C++ High Performance Programming](https://www.packtpub.com/product/c-high-performance-second-edition/9781839216541)
- [Building Low Latency Applications with C++](https://www.packtpub.com/product/building-low-latency-applications-with-c/9781837639359)
- [Electronic Trading Systems Architecture](https://www.wiley.com/en-us/Electronic+Trading+Systems+Architecture-p-9781119608028)
