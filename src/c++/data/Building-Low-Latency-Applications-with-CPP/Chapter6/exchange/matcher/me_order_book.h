#pragma once

#include "common/types.h"
#include "common/mem_pool.h"
#include "common/logging.h"
#include "order_server/client_response.h"
#include "market_data/market_update.h"

#include "me_order.h"

using namespace Common;

namespace Exchange
{
class MatchingEngine;

// MEOrderBook: 限價訂單簿(Limit Order Book)
//
// 設計原理:
// 1. 價格-時間優先權(Price-Time Priority): 最優價格優先,同價位先到先撮合
// 2. 三層索引架構: 快速查詢訂單/價位/最佳報價
// 3. 記憶體池管理: 零動態記憶體分配
//
// 三層索引架構:
// [第一層] ClientOrderHashMap: 客戶訂單查詢 O(1)
//   cid_oid_to_order_[client_id][order_id] → MEOrder*
//
// [第二層] OrdersAtPriceHashMap: 價位節點查詢 O(1)
//   price_orders_at_price_[price % 256] → MEOrdersAtPrice*
//
// [第三層] 排序鏈結串列: 價格排序 O(1) 取得最佳報價
//   bids_by_price_ → Price 100.5 → Price 100.0 → Price 99.5  (買單降序)
//   asks_by_price_ → Price 100.0 → Price 100.5 → Price 101.0 (賣單升序)
//                         ↓              ↓              ↓
//                    [Order1→...]   [Order2→...]   [Order3→...] (同價位訂單佇列)
//
// ⚡ 時間複雜度:
// - 新增訂單: O(1) ~ O(P) (P = 價位數量,通常 < 256)
// - 取消訂單: O(1)
// - 撮合: O(1) 取得最佳報價
// - 查詢訂單: O(1)
//
// 使用場景: 交易所撮合引擎的核心數據結構
class MEOrderBook final
{
public:
    explicit MEOrderBook(TickerId ticker_id, Logger* logger,
                         MatchingEngine* matching_engine);

    ~MEOrderBook();

    // 新增訂單: 嘗試撮合,剩餘數量加入訂單簿
    // ⚡ 撮合演算法: FIFO (First In First Out)
    auto add(ClientId client_id, OrderId client_order_id, TickerId ticker_id,
             Side side, Price price, Qty qty) noexcept -> void;

    // 取消訂單: 從訂單簿移除
    auto cancel(ClientId client_id, OrderId order_id,
                TickerId ticker_id) noexcept -> void;

    auto toString(bool detailed, bool validity_check) const -> std::string;

    // Deleted default, copy & move constructors and assignment-operators.
    MEOrderBook() = delete;

    MEOrderBook(const MEOrderBook&) = delete;

    MEOrderBook(const MEOrderBook&&) = delete;

    MEOrderBook& operator=(const MEOrderBook&) = delete;

    MEOrderBook& operator=(const MEOrderBook&&) = delete;

private:
    TickerId ticker_id_ = TickerId_INVALID;

    MatchingEngine* matching_engine_ = nullptr;

    // [第一層索引] 客戶訂單雜湊表: 快速查詢訂單 O(1)
    // cid_oid_to_order_[client_id][order_id] → MEOrder*
    // ⚡ 用途: 取消訂單時快速定位
    ClientOrderHashMap cid_oid_to_order_;

    // 記憶體池: 價位節點預配置
    // ⚡ 容量: ME_MAX_PRICE_LEVELS (256 個價位節點)
    MemPool<MEOrdersAtPrice> orders_at_price_pool_;

    // [第三層索引] 排序鏈結串列頭指標
    // ⚡ 最佳買價: bids_by_price_->price_ (最高買價)
    // ⚡ 最佳賣價: asks_by_price_->price_ (最低賣價)
    MEOrdersAtPrice* bids_by_price_ = nullptr;  // 買單價位鏈結串列 (降序排列)
    MEOrdersAtPrice* asks_by_price_ = nullptr;  // 賣單價位鏈結串列 (升序排列)

    // [第二層索引] 價位雜湊表: 快速查詢價位節點 O(1)
    // price_orders_at_price_[price % ME_MAX_PRICE_LEVELS] → MEOrdersAtPrice*
    OrdersAtPriceHashMap price_orders_at_price_;

    // 記憶體池: 訂單物件預配置
    // ⚡ 容量: ME_MAX_ORDER_IDS (1,048,576 個訂單)
    MemPool<MEOrder> order_pool_;

    // 回應物件: 重複使用同一物件,避免記憶體分配
    MEClientResponse client_response_;  // 客戶回應 (ACCEPTED/CANCELED/FILLED)
    MEMarketUpdate market_update_;      // 市場數據更新 (成交/訂單簿變動)

    // 市場訂單 ID 生成器
    // ⚠️ 注意: 單調遞增,不可重複
    OrderId next_market_order_id_ = 1;

    std::string time_str_;
    Logger* logger_ = nullptr;

private:
    // 生成新的市場訂單 ID
    // ⚠️ 注意: 單調遞增,確保唯一性
    auto generateNewMarketOrderId() noexcept -> OrderId
    {
        return next_market_order_id_++;
    }

    // 價格雜湊函數: 將價格映射到陣列索引
    // ⚡ Hash Function: price % ME_MAX_PRICE_LEVELS
    // 複雜度: O(1)
    auto priceToIndex(Price price) const noexcept
    {
        return (price % ME_MAX_PRICE_LEVELS);
    }

    // 查詢價位節點
    // @param price: 價格
    // @return: 該價位的訂單鏈結串列,若不存在則返回 nullptr
    // 複雜度: O(1)
    auto getOrdersAtPrice(Price price) const noexcept -> MEOrdersAtPrice*
    {
        return price_orders_at_price_.at(priceToIndex(price));
    }

    // 新增價位節點到訂單簿 (維護價格排序)
    // @param new_orders_at_price: 新價位節點
    //
    // ⚡ 演算法: 找到插入位置,維護環狀雙向鏈結串列
    // - 買單(BID): 降序排列 (100.5 → 100.0 → 99.5)
    // - 賣單(ASK): 升序排列 (100.0 → 100.5 → 101.0)
    //
    // 複雜度: O(1) ~ O(P) (P = 價位數量,通常 < 256)
    // ⚠️ 最壞情況: 遍歷所有價位節點 (當新價位是最差價時)
    auto addOrdersAtPrice(MEOrdersAtPrice* new_orders_at_price) noexcept
    {
        price_orders_at_price_.at(priceToIndex(new_orders_at_price->price_)) =
            new_orders_at_price;

        const auto best_orders_by_price = (new_orders_at_price->side_ == Side::BUY ?
                                           bids_by_price_ : asks_by_price_);

        if (UNLIKELY(!best_orders_by_price)) {
            (new_orders_at_price->side_ == Side::BUY ? bids_by_price_ : asks_by_price_) =
                new_orders_at_price;
            new_orders_at_price->prev_entry_ = new_orders_at_price->next_entry_ =
                                                   new_orders_at_price;
        } else {
            auto target = best_orders_by_price;
            bool add_after = ((new_orders_at_price->side_ == Side::SELL &&
                               new_orders_at_price->price_ > target->price_) ||
                              (new_orders_at_price->side_ == Side::BUY &&
                               new_orders_at_price->price_ < target->price_));

            if (add_after) {
                target = target->next_entry_;
                add_after = ((new_orders_at_price->side_ == Side::SELL &&
                              new_orders_at_price->price_ > target->price_) ||
                             (new_orders_at_price->side_ == Side::BUY &&
                              new_orders_at_price->price_ < target->price_));
            }

            while (add_after && target != best_orders_by_price) {
                add_after = ((new_orders_at_price->side_ == Side::SELL &&
                              new_orders_at_price->price_ > target->price_) ||
                             (new_orders_at_price->side_ == Side::BUY &&
                              new_orders_at_price->price_ < target->price_));

                if (add_after) {
                    target = target->next_entry_;
                }
            }

            if (add_after) { // add new_orders_at_price after target.
                if (target == best_orders_by_price) {
                    target = best_orders_by_price->prev_entry_;
                }

                new_orders_at_price->prev_entry_ = target;
                target->next_entry_->prev_entry_ = new_orders_at_price;
                new_orders_at_price->next_entry_ = target->next_entry_;
                target->next_entry_ = new_orders_at_price;
            } else { // add new_orders_at_price before target.
                new_orders_at_price->prev_entry_ = target->prev_entry_;
                new_orders_at_price->next_entry_ = target;
                target->prev_entry_->next_entry_ = new_orders_at_price;
                target->prev_entry_ = new_orders_at_price;

                if ((new_orders_at_price->side_ == Side::BUY &&
                     new_orders_at_price->price_ > best_orders_by_price->price_) ||
                    (new_orders_at_price->side_ == Side::SELL &&
                     new_orders_at_price->price_ < best_orders_by_price->price_)) {
                    target->next_entry_ = (target->next_entry_ == best_orders_by_price ?
                                           new_orders_at_price : target->next_entry_);
                    (new_orders_at_price->side_ == Side::BUY ? bids_by_price_ : asks_by_price_) =
                        new_orders_at_price;
                }
            }
        }
    }

    // 移除價位節點 (當該價位所有訂單都已撮合/取消)
    // @param side: 買/賣方向
    // @param price: 價格
    //
    // ⚡ 演算法: 從環狀雙向鏈結串列中移除節點
    // - 更新前後節點的指標
    // - 若移除的是最佳報價節點,更新 bids_by_price_/asks_by_price_
    // - 釋放記憶體池中的節點
    //
    // 複雜度: O(1)
    auto removeOrdersAtPrice(Side side, Price price) noexcept
    {
        const auto best_orders_by_price = (side == Side::BUY ? bids_by_price_ :
                                           asks_by_price_);
        auto orders_at_price = getOrdersAtPrice(price);

        if (UNLIKELY(orders_at_price->next_entry_ ==
                     orders_at_price)) { // empty side of book.
            // ⚠️ 特殊情況: 只剩一個價位節點 (環狀鏈結串列只有一個節點)
            (side == Side::BUY ? bids_by_price_ : asks_by_price_) = nullptr;
        } else {
            // 從環狀鏈結串列中移除節點
            orders_at_price->prev_entry_->next_entry_ = orders_at_price->next_entry_;
            orders_at_price->next_entry_->prev_entry_ = orders_at_price->prev_entry_;

            if (orders_at_price == best_orders_by_price) {
                // 若移除的是最佳報價,更新頭指標為下一個節點
                (side == Side::BUY ? bids_by_price_ : asks_by_price_) =
                    orders_at_price->next_entry_;
            }

            orders_at_price->prev_entry_ = orders_at_price->next_entry_ = nullptr;
        }

        // 清除雜湊表索引
        price_orders_at_price_.at(priceToIndex(price)) = nullptr;

        // 歸還記憶體池
        orders_at_price_pool_.deallocate(orders_at_price);
    }

    // 取得下一個時間優先權值
    // @param price: 價格
    // @return: 新訂單的 priority 值 (同價位最後一個訂單的 priority + 1)
    //
    // ⚡ 時間優先權原理:
    // - Priority 越小越優先 (先到先撮合)
    // - 同價位訂單形成環狀鏈結串列,最後一個訂單是 first_me_order_->prev_order_
    //
    // 複雜度: O(1)
    auto getNextPriority(Price price) noexcept
    {
        const auto orders_at_price = getOrdersAtPrice(price);

        if (!orders_at_price) {
            return 1lu;  // 第一個訂單的 priority
        }

        // 環狀鏈結串列: first_me_order_->prev_order_ 指向最後一個訂單
        return orders_at_price->first_me_order_->prev_order_->priority_ + 1;
    }

    auto match(TickerId ticker_id, ClientId client_id, Side side,
               OrderId client_order_id, OrderId new_market_order_id, MEOrder* bid_itr,
               Qty* leaves_qty) noexcept;

    auto
    checkForMatch(ClientId client_id, OrderId client_order_id, TickerId ticker_id,
                  Side side, Price price, Qty qty, Qty new_market_order_id) noexcept;

    // 移除訂單 (取消訂單或完全成交時呼叫)
    // @param order: 要移除的訂單
    //
    // ⚡ 演算法:
    // 1. 從環狀雙向鏈結串列中移除訂單
    // 2. 更新前後訂單的指標
    // 3. 若該價位沒有其他訂單,移除價位節點
    // 4. 清除客戶訂單雜湊表索引
    // 5. 歸還訂單物件到記憶體池
    //
    // 複雜度: O(1)
    auto removeOrder(MEOrder* order) noexcept
    {
        auto orders_at_price = getOrdersAtPrice(order->price_);

        if (order->prev_order_ == order) { // only one element.
            // ⚠️ 特殊情況: 該價位只有一個訂單 (環狀鏈結串列只有一個節點)
            removeOrdersAtPrice(order->side_, order->price_);
        } else { // remove the link.
            // 從環狀鏈結串列中移除訂單
            const auto order_before = order->prev_order_;
            const auto order_after = order->next_order_;
            order_before->next_order_ = order_after;
            order_after->prev_order_ = order_before;

            if (orders_at_price->first_me_order_ == order) {
                // 若移除的是第一個訂單,更新頭指標
                orders_at_price->first_me_order_ = order_after;
            }

            order->prev_order_ = order->next_order_ = nullptr;
        }

        // 清除客戶訂單雜湊表索引
        cid_oid_to_order_.at(order->client_id_).at(order->client_order_id_) = nullptr;

        // 歸還記憶體池
        order_pool_.deallocate(order);
    }

    // 新增訂單到訂單簿
    // @param order: 要新增的訂單
    //
    // ⚡ 演算法:
    // 1. 查詢該價位是否已存在
    // 2. 若不存在,創建新價位節點並插入價位鏈結串列
    // 3. 將訂單插入該價位的環狀雙向鏈結串列末尾 (Time Priority)
    // 4. 更新客戶訂單雜湊表索引
    //
    // ⚠️ 注意: 新訂單總是插入到環狀鏈結串列的末尾 (first_order->prev_order_ 之後)
    // 原因: 確保時間優先權 (Time Priority) - 先到先撮合
    //
    // 複雜度: O(1) ~ O(P) (P = 價位數量,addOrdersAtPrice 的複雜度)
    auto addOrder(MEOrder* order) noexcept
    {
        const auto orders_at_price = getOrdersAtPrice(order->price_);

        if (!orders_at_price) {
            // 該價位尚未存在,創建新價位節點
            // ⚡ 環狀鏈結串列初始化: 單一節點指向自己
            order->next_order_ = order->prev_order_ = order;

            auto new_orders_at_price = orders_at_price_pool_.allocate(order->side_,
                                       order->price_, order, nullptr, nullptr);
            addOrdersAtPrice(new_orders_at_price);
        } else {
            // 該價位已存在,將訂單插入環狀鏈結串列末尾
            auto first_order = (orders_at_price ? orders_at_price->first_me_order_ :
                                nullptr);

            // 插入到環狀鏈結串列末尾 (first_order->prev_order_ 之後)
            // ⚡ 時間優先權: 新訂單的 priority 最大,放在最後
            first_order->prev_order_->next_order_ = order;
            order->prev_order_ = first_order->prev_order_;
            order->next_order_ = first_order;
            first_order->prev_order_ = order;
        }

        // 更新客戶訂單雜湊表索引 (用於快速查詢)
        cid_oid_to_order_.at(order->client_id_).at(order->client_order_id_) = order;
    }
};

typedef std::array<MEOrderBook*, ME_MAX_TICKERS> OrderBookHashMap;
}
