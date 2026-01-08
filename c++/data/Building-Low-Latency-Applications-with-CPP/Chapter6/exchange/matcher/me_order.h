#pragma once

#include <array>
#include <sstream>
#include "common/types.h"

using namespace Common;

namespace Exchange
{
// MEOrder: 撮合引擎訂單結構
//
// 設計原理:
// 1. 環狀雙向鏈結串列(Circular Doubly Linked List): 支援 O(1) 插入/刪除
// 2. 記憶體池友善: 預設建構子允許使用 Placement New
// 3. Priority 排序: 同價位訂單依據時間優先權(Time Priority)排序
//
// 資料結構關係:
// MEOrderBook
//   ├── ClientOrderHashMap[client_id][order_id] → MEOrder*  (O(1) 查詢訂單)
//   └── MEOrdersAtPrice (價位節點)
//         └── first_me_order_ → MEOrder (環狀雙向鏈結串列)
//                                  ↓
//                              MEOrder → MEOrder → ... (同價位訂單佇列)
//
// 使用場景: 限價單(Limit Order)的價格-時間優先權(Price-Time Priority)撮合
struct MEOrder {
    TickerId ticker_id_ = TickerId_INVALID;        // 交易標的 ID
    ClientId client_id_ = ClientId_INVALID;        // 客戶 ID
    OrderId client_order_id_ = OrderId_INVALID;    // 客戶端訂單 ID
    OrderId market_order_id_ = OrderId_INVALID;    // 市場訂單 ID (交易所分配)
    Side side_ = Side::INVALID;                    // 買/賣方向
    Price price_ = Price_INVALID;                  // 限價
    Qty qty_ = Qty_INVALID;                        // 數量
    Priority priority_ = Priority_INVALID;         // 時間優先權(越小越優先)

    // ⚡ 環狀雙向鏈結串列指標: 支援 O(1) 插入/刪除
    // 設計決策: 為何不用 std::list?
    // 1. 零動態記憶體分配: 配合 Memory Pool 預先配置
    // 2. Cache 友善: 減少 heap 碎片化,提升 Cache 命中率
    // 3. 低延遲: 避免 malloc/free 的 50-10000ns 開銷
    MEOrder* prev_order_ = nullptr;  // 前一個訂單(同價位佇列)
    MEOrder* next_order_ = nullptr;  // 下一個訂單(同價位佇列)

    // ⚠️ 注意: 預設建構子必須存在才能與 MemPool 配合
    // MemPool 預先配置記憶體時會呼叫 T() 建構所有元素
    MEOrder() = default;

    MEOrder(TickerId ticker_id, ClientId client_id, OrderId client_order_id,
            OrderId market_order_id, Side side, Price price,
            Qty qty, Priority priority, MEOrder* prev_order, MEOrder* next_order) noexcept
        : ticker_id_(ticker_id), client_id_(client_id),
          client_order_id_(client_order_id), market_order_id_(market_order_id),
          side_(side),
          price_(price), qty_(qty), priority_(priority), prev_order_(prev_order),
          next_order_(next_order) {}

    auto toString() const -> std::string;
};

// 訂單雜湊表: 二維陣列索引結構
// ClientOrderHashMap[client_id][order_id] → MEOrder*
//
// 設計原理:
// 1. 使用 std::array 而非 std::unordered_map: 避免動態記憶體分配
// 2. 時間複雜度: O(1) 查詢/插入/刪除
// 3. 空間複雜度: O(MAX_CLIENTS × MAX_ORDER_IDS) 指標陣列
//
// ⚡ 效能關鍵:
// - 直接索引存取,無需 hash function 計算
// - Cache 友善: 連續記憶體排列
// - 缺點: 記憶體佔用較大 (8 bytes × 256 clients × 1M orders ≈ 2GB)
typedef std::array<MEOrder*, ME_MAX_ORDER_IDS> OrderHashMap;         // 單一客戶的訂單映射
typedef std::array<OrderHashMap, ME_MAX_NUM_CLIENTS> ClientOrderHashMap;  // 所有客戶的訂單映射

// MEOrdersAtPrice: 價位節點(Price Level)
//
// 設計原理:
// 1. 維護同一價位的所有訂單: first_me_order_ 指向環狀雙向鏈結串列的頭部
// 2. 價位鏈結串列: prev_entry_/next_entry_ 連接相鄰價位
// 3. 排序規則: 買單(Bid)降序排列,賣單(Ask)升序排列
//
// 資料結構關係:
// MEOrderBook::bids_by_price_ (買單)
//   Price 100.5 ← prev_entry_ ─ Price 100.0 ─ next_entry_ → Price 99.5
//       ↓                           ↓                           ↓
//   [Order1→Order2]           [Order3→Order4→Order5]      [Order6]
//
// ⚡ 撮合演算法優勢:
// - 最佳買價永遠是 bids_by_price_ (第一個節點)
// - 最佳賣價永遠是 asks_by_price_ (第一個節點)
// - O(1) 取得最佳報價 (Best Bid/Best Ask)
struct MEOrdersAtPrice {
    Side side_ = Side::INVALID;                // 買/賣方向
    Price price_ = Price_INVALID;              // 價位

    // ⚡ 同價位訂單佇列的頭指標
    // 指向第一個訂單 (時間優先權最高)
    MEOrder* first_me_order_ = nullptr;

    // 價位鏈結串列指標
    // ⚠️ 注意: prev_entry_ 指向價格更優的節點
    // 買單: prev_entry_->price_ > this->price_
    // 賣單: prev_entry_->price_ < this->price_
    MEOrdersAtPrice* prev_entry_ = nullptr;    // 前一個價位節點
    MEOrdersAtPrice* next_entry_ = nullptr;    // 下一個價位節點

    MEOrdersAtPrice() = default;

    MEOrdersAtPrice(Side side, Price price, MEOrder* first_me_order,
                    MEOrdersAtPrice* prev_entry, MEOrdersAtPrice* next_entry)
        : side_(side), price_(price), first_me_order_(first_me_order),
          prev_entry_(prev_entry), next_entry_(next_entry) {}

    auto toString() const
    {
        std::stringstream ss;
        ss << "MEOrdersAtPrice["
           << "side:" << sideToString(side_) << " "
           << "price:" << priceToString(price_) << " "
           << "first_me_order:" << (first_me_order_ ? first_me_order_->toString() : "null")
           << " "
           << "prev:" << priceToString(prev_entry_ ? prev_entry_->price_ : Price_INVALID)
           << " "
           << "next:" << priceToString(next_entry_ ? next_entry_->price_ : Price_INVALID)
           << "]";

        return ss.str();
    }
};

// 價位雜湊表: 陣列索引結構
// OrdersAtPriceHashMap[price % ME_MAX_PRICE_LEVELS] → MEOrdersAtPrice*
//
// 設計原理:
// 1. Modulo Hash: 使用價格對 256 取模作為索引
// 2. 時間複雜度: O(1) 查詢 (無碰撞時)
// 3. 碰撞處理: 依賴價位鏈結串列 (MEOrdersAtPrice::prev_entry_/next_entry_)
//
// ⚡ 效能特性:
// - 快速定位價位節點: 無需遍歷整個訂單簿
// - 空間效率: 僅儲存 256 個指標 (8 bytes × 256 = 2KB)
// - 適用場景: 價格變動範圍可預測的市場
//
// ⚠️ 注意:
// - 如果價格範圍 > 256,會發生雜湊碰撞
// - 碰撞時仍需遍歷價位鏈結串列 (性能退化為 O(N))
typedef std::array<MEOrdersAtPrice*, ME_MAX_PRICE_LEVELS> OrdersAtPriceHashMap;
}
