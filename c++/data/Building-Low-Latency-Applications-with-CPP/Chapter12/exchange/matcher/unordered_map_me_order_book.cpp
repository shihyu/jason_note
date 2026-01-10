/**
 * @file unordered_map_me_order_book.cpp
 * @brief 基於 unordered_map 的訂單簿實作（效能比較版本）
 *
 * 📊 設計對比：
 * - 本實作使用 unordered_map<Price, MEOrdersAtPrice*> 管理價格層級
 * - 相較於 me_order_book.cpp 的陣列索引法（Price 直接當陣列 index）
 * - 優勢：支援任意價格範圍，不受陣列大小限制
 * - 劣勢：hash 查找 O(1) 平均但非常數時間，cache locality 較差
 *
 * ⚡ 效能考量：
 * - unordered_map 每次 lookup 需要 hash 運算 + 可能的 collision 處理
 * - 陣列版本直接用 price 當 index，0 個額外運算
 * - 實測差異：每次操作約增加 10-20ns（視 CPU cache 狀態）
 *
 * 🎯 使用場景：
 * - 價格範圍未知或極大時（如加密貨幣）
 * - 記憶體受限環境（不想預分配大陣列）
 * - 可接受些微延遲換取靈活性
 */
#include "unordered_map_me_order_book.h"

#include "matcher/matching_engine.h"

namespace Exchange
{
/// 建構函式：初始化訂單簿與記憶體池
/// @param ticker_id 標的代碼
/// @param logger 日誌器指標
/// @param matching_engine 撮合引擎指標（用於發送回應與市場更新）
UnorderedMapMEOrderBook::UnorderedMapMEOrderBook(TickerId ticker_id,
        Logger* logger, MatchingEngine* matching_engine)
    : ticker_id_(ticker_id), matching_engine_(matching_engine),
      orders_at_price_pool_(ME_MAX_PRICE_LEVELS),  // ⚡ 預分配價格層級物件池
      order_pool_(ME_MAX_ORDER_IDS),               // ⚡ 預分配訂單物件池
      logger_(logger)
{
    // ⚠️ 注意：bids_by_price_ 和 asks_by_price_ 初始為 nullptr
    // 第一筆訂單加入時才會建立對應的價格層級鏈表
}

UnorderedMapMEOrderBook::~UnorderedMapMEOrderBook()
{
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 toString(false, true));

    matching_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;
}

/// ⚡ 核心撮合邏輯：將主動訂單與被動訂單進行撮合
///
/// 📊 撮合流程：
/// 1. 計算成交量 = min(主動訂單剩餘量, 被動訂單量)
/// 2. 更新雙方訂單的剩餘量
/// 3. 發送成交回報給雙方客戶
/// 4. 發送市場交易更新（TRADE）
/// 5. 若被動訂單完全成交，發送 CANCEL 並從訂單簿移除
/// 6. 若被動訂單部分成交，發送 MODIFY 更新剩餘量
///
/// ⚠️ 關鍵設計：
/// - 使用指標傳遞 leaves_qty 以回傳主動訂單的剩餘量
/// - 被動訂單（itr）會被修改，可能被移除
/// - 發送 3-4 個訊息：2 個 FILLED + 1 個 TRADE + 1 個 CANCEL/MODIFY
///
/// @param ticker_id 標的代碼
/// @param client_id 主動訂單的客戶 ID
/// @param side 主動訂單的方向
/// @param client_order_id 主動訂單的客戶訂單 ID
/// @param new_market_order_id 主動訂單的市場訂單 ID
/// @param itr 被動訂單指標（會被修改）
/// @param leaves_qty 主動訂單剩餘量指標（輸入輸出參數）
auto UnorderedMapMEOrderBook::match(TickerId ticker_id, ClientId client_id,
                                    Side side, OrderId client_order_id, OrderId new_market_order_id, MEOrder* itr,
                                    Qty* leaves_qty) noexcept
{
    const auto order = itr;                    // 被動訂單
    const auto order_qty = order->qty_;        // 保存原始量（用於 CANCEL 訊息）
    const auto fill_qty = std::min(*leaves_qty, order_qty);  // ⚡ 成交量 = 兩邊剩餘量的最小值

    // 步驟 1：更新雙方訂單的剩餘量
    *leaves_qty -= fill_qty;    // 主動訂單剩餘量減少
    order->qty_ -= fill_qty;    // 被動訂單剩餘量減少

    // 步驟 2：發送成交回報給主動訂單的客戶
    // leaves_qty: 主動訂單還剩多少量未成交
    client_response_ = {ClientResponseType::FILLED, client_id, ticker_id, client_order_id,
                        new_market_order_id, side, itr->price_, fill_qty, *leaves_qty
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 步驟 3：發送成交回報給被動訂單的客戶
    // order->qty_: 被動訂單還剩多少量未成交
    client_response_ = {ClientResponseType::FILLED, order->client_id_, ticker_id, order->client_order_id_,
                        order->market_order_id_, order->side_, itr->price_, fill_qty, order->qty_
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 步驟 4：發送市場交易更新（供行情訂閱者）
    // ⚠️ order_id 為 INVALID，因為這是撮合事件，不針對特定訂單
    market_update_ = {MarketUpdateType::TRADE, OrderId_INVALID, ticker_id, side, itr->price_, fill_qty, Priority_INVALID};
    matching_engine_->sendMarketUpdate(&market_update_);

    // 步驟 5：處理被動訂單的後續狀態
    if (!order->qty_) {
        // 情況 A：被動訂單完全成交 → 發送 CANCEL 並從訂單簿移除
        // 📊 為什麼用 CANCEL？因為這筆訂單不再存在於訂單簿中
        market_update_ = {MarketUpdateType::CANCEL, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order_qty, Priority_INVALID  // ⚠️ 使用原始量，非剩餘量
                         };
        matching_engine_->sendMarketUpdate(&market_update_);

        START_MEASURE(Exchange_UnorderedMapMEOrderBook_removeOrder);
        removeOrder(order);  // ⚡ 從訂單簿移除並釋放記憶體
        END_MEASURE(Exchange_UnorderedMapMEOrderBook_removeOrder, (*logger_));
    } else {
        // 情況 B：被動訂單部分成交 → 發送 MODIFY 更新剩餘量
        market_update_ = {MarketUpdateType::MODIFY, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order->qty_, order->priority_  // ⚡ 保持原優先權
                         };
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}

/// ⚡ 檢查新訂單是否能與對手盤撮合
///
/// 📊 撮合規則（Price-Time Priority）：
/// - 買單：當買價 >= 最佳賣價，就能成交
/// - 賣單：當賣價 <= 最佳買價，就能成交
/// - 按照價格優先、時間優先的順序逐筆撮合
///
/// ⚠️ 迴圈設計：
/// - 持續撮合直到：(1) 新訂單完全成交 (leaves_qty == 0) 或 (2) 價格不再匹配
/// - 每次撮合會修改 leaves_qty，並可能移除對手盤訂單
///
/// @return 新訂單的剩餘量（0 表示完全成交）
auto UnorderedMapMEOrderBook::checkForMatch(ClientId client_id,
        OrderId client_order_id, TickerId ticker_id, Side side, Price price, Qty qty,
        Qty new_market_order_id) noexcept
{
    auto leaves_qty = qty;  // 剩餘未成交量

    // 情況 A：新訂單是買單 → 檢查是否能與賣單撮合
    if (side == Side::BUY) {
        while (leaves_qty && asks_by_price_) {  // ⚡ 有剩餘量 且 有賣單存在
            const auto ask_itr = asks_by_price_->first_me_order_;  // 最佳賣價的第一筆訂單

            // 📊 撮合條件：買價 >= 賣價
            // LIKELY 提示：大部分情況下價格不會交叉（主動訂單會成為被動訂單）
            if (LIKELY(price < ask_itr->price_)) {
                break;  // 買價 < 賣價，無法成交
            }

            // ⚡ 執行撮合（會修改 leaves_qty 和可能移除 ask_itr）
            START_MEASURE(Exchange_UnorderedMapMEOrderBook_match);
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, ask_itr,
                  &leaves_qty);
            END_MEASURE(Exchange_UnorderedMapMEOrderBook_match, (*logger_));
        }
    }

    // 情況 B：新訂單是賣單 → 檢查是否能與買單撮合
    if (side == Side::SELL) {
        while (leaves_qty && bids_by_price_) {  // ⚡ 有剩餘量 且 有買單存在
            const auto bid_itr = bids_by_price_->first_me_order_;  // 最佳買價的第一筆訂單

            // 📊 撮合條件：賣價 <= 買價
            // LIKELY 提示：大部分情況下價格不會交叉
            if (LIKELY(price > bid_itr->price_)) {
                break;  // 賣價 > 買價，無法成交
            }

            // ⚡ 執行撮合（會修改 leaves_qty 和可能移除 bid_itr）
            START_MEASURE(Exchange_UnorderedMapMEOrderBook_match);
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, bid_itr,
                  &leaves_qty);
            END_MEASURE(Exchange_UnorderedMapMEOrderBook_match, (*logger_));
        }
    }

    return leaves_qty;  // 回傳剩餘未成交量
}

/// ⚡ 新增訂單到訂單簿（核心入口方法）
///
/// 📊 處理流程：
/// 1. 產生新的市場訂單 ID
/// 2. 發送 ACCEPTED 回報給客戶
/// 3. 嘗試撮合（checkForMatch）
/// 4. 若有剩餘量，加入訂單簿並發送 ADD 市場更新
///
/// ⚠️ 設計要點：
/// - LIKELY(leaves_qty) 表示大部分訂單會有剩餘量（成為被動訂單）
/// - 只有剩餘量不為 0 時才加入訂單簿
/// - 優先權（priority）用於實現時間優先原則
///
/// @param client_id 客戶 ID
/// @param client_order_id 客戶訂單 ID
/// @param ticker_id 標的代碼
/// @param side 買賣方向
/// @param price 價格
/// @param qty 數量
auto UnorderedMapMEOrderBook::add(ClientId client_id, OrderId client_order_id,
                                  TickerId ticker_id, Side side, Price price, Qty qty) noexcept -> void
{
    // 步驟 1：產生新的市場訂單 ID（交易所內部使用的唯一 ID）
    const auto new_market_order_id = generateNewMarketOrderId();

    // 步驟 2：發送 ACCEPTED 回報（訂單已接受，等待撮合或掛單）
    // ⚠️ fill_qty = 0 表示尚未成交
    client_response_ = {ClientResponseType::ACCEPTED, client_id, ticker_id, client_order_id, new_market_order_id, side, price, 0, qty};
    matching_engine_->sendClientResponse(&client_response_);

    // 步驟 3：嘗試撮合（會在內部發送 FILLED 回報）
    START_MEASURE(Exchange_UnorderedMapMEOrderBook_checkForMatch);
    const auto leaves_qty = checkForMatch(client_id, client_order_id, ticker_id,
                                          side, price, qty, new_market_order_id);
    END_MEASURE(Exchange_UnorderedMapMEOrderBook_checkForMatch, (*logger_));

    // 步驟 4：若有剩餘量，加入訂單簿成為被動訂單
    if (LIKELY(leaves_qty)) {  // 📊 LIKELY：大部分訂單不會完全成交
        // 取得優先權編號（同價位內，越早到的優先權越小）
        const auto priority = getNextPriority(price);

        // 從記憶體池分配訂單物件（⚡ O(1) 分配，無記憶體碎片）
        auto order = order_pool_.allocate(ticker_id, client_id, client_order_id,
                                          new_market_order_id, side, price, leaves_qty, priority, nullptr,
                                          nullptr);

        // 將訂單加入訂單簿（雙向鏈表操作）
        START_MEASURE(Exchange_UnorderedMapMEOrderBook_addOrder);
        addOrder(order);
        END_MEASURE(Exchange_UnorderedMapMEOrderBook_addOrder, (*logger_));

        // 發送 ADD 市場更新（通知行情訂閱者有新訂單加入）
        market_update_ = {MarketUpdateType::ADD, new_market_order_id, ticker_id, side, price, leaves_qty, priority};
        matching_engine_->sendMarketUpdate(&market_update_);
    }
    // ⚠️ 若 leaves_qty == 0，表示訂單完全成交，不需要加入訂單簿
}

/// ⚡ 取消訂單
///
/// 📊 取消流程：
/// 1. 檢查訂單是否存在（使用 cid_oid_to_order_ 雙層查找）
/// 2. 若存在，從訂單簿移除並發送 CANCELED 回報 + CANCEL 市場更新
/// 3. 若不存在，發送 CANCEL_REJECTED 回報
///
/// ⚠️ 查找邏輯：
/// - 使用兩層陣列：cid_oid_to_order_[client_id][order_id]
/// - 第一層檢查：client_id 是否在範圍內
/// - 第二層檢查：order_id 對應的訂單指標是否為 nullptr
/// - LIKELY/UNLIKELY 提示：取消失敗是罕見情況
///
/// @param client_id 客戶 ID
/// @param order_id 客戶訂單 ID
/// @param ticker_id 標的代碼
auto UnorderedMapMEOrderBook::cancel(ClientId client_id, OrderId order_id,
                                     TickerId ticker_id) noexcept -> void
{
    // 步驟 1：檢查 client_id 是否在有效範圍內
    auto is_cancelable = (client_id < cid_oid_to_order_.size());
    MEOrder* exchange_order = nullptr;

    if (LIKELY(is_cancelable)) {  // 📊 LIKELY：大部分情況 client_id 有效
        // 步驟 2：查找訂單（cid_oid_to_order_[client_id][order_id]）
        auto& co_itr = cid_oid_to_order_[client_id];
        exchange_order = co_itr[order_id];
        is_cancelable = (exchange_order != nullptr);  // 檢查訂單是否存在
    }

    // 步驟 3：根據訂單是否存在，發送不同的回報
    if (UNLIKELY(!is_cancelable)) {  // 📊 UNLIKELY：取消失敗是罕見情況
        // 情況 A：訂單不存在 → 發送 CANCEL_REJECTED
        // ⚠️ 所有欄位（除了 client_id, ticker_id, order_id）都設為 INVALID
        client_response_ = {ClientResponseType::CANCEL_REJECTED, client_id, ticker_id, order_id, OrderId_INVALID,
                            Side::INVALID, Price_INVALID, Qty_INVALID, Qty_INVALID
                           };
    } else {
        // 情況 B：訂單存在 → 發送 CANCELED 並從訂單簿移除
        // 📊 回報包含原訂單的完整資訊（市場訂單 ID、方向、價格、剩餘量）
        client_response_ = {ClientResponseType::CANCELED, client_id, ticker_id, order_id, exchange_order->market_order_id_,
                            exchange_order->side_, exchange_order->price_, Qty_INVALID, exchange_order->qty_
                           };

        // 發送市場更新（通知行情訂閱者訂單已取消）
        // ⚠️ qty = 0 表示這是取消操作，非成交
        market_update_ = {MarketUpdateType::CANCEL, exchange_order->market_order_id_, ticker_id, exchange_order->side_, exchange_order->price_, 0,
                          exchange_order->priority_
                         };

        // 從訂單簿移除訂單（修改雙向鏈表 + 釋放記憶體）
        START_MEASURE(Exchange_UnorderedMapMEOrderBook_removeOrder);
        removeOrder(exchange_order);
        END_MEASURE(Exchange_UnorderedMapMEOrderBook_removeOrder, (*logger_));

        // 發送市場更新
        matching_engine_->sendMarketUpdate(&market_update_);
    }

    // 步驟 4：發送客戶回報（無論成功或失敗）
    matching_engine_->sendClientResponse(&client_response_);
}

auto UnorderedMapMEOrderBook::toString(bool detailed,
                                       bool validity_check) const -> std::string
{
    std::stringstream ss;
    std::string time_str;

    auto printer = [&](std::stringstream & ss, MEOrdersAtPrice * itr, Side side,
    Price & last_price, bool sanity_check) {
        char buf[4096];
        Qty qty = 0;
        size_t num_orders = 0;

        for (auto o_itr = itr->first_me_order_;; o_itr = o_itr->next_order_) {
            qty += o_itr->qty_;
            ++num_orders;

            if (o_itr->next_order_ == itr->first_me_order_) {
                break;
            }
        }

        sprintf(buf, " <px:%3s p:%3s n:%3s> %-3s @ %-5s(%-4s)",
                priceToString(itr->price_).c_str(),
                priceToString(itr->prev_entry_->price_).c_str(),
                priceToString(itr->next_entry_->price_).c_str(),
                priceToString(itr->price_).c_str(), qtyToString(qty).c_str(),
                std::to_string(num_orders).c_str());
        ss << buf;

        for (auto o_itr = itr->first_me_order_;; o_itr = o_itr->next_order_) {
            if (detailed) {
                sprintf(buf, "[oid:%s q:%s p:%s n:%s] ",
                        orderIdToString(o_itr->market_order_id_).c_str(),
                        qtyToString(o_itr->qty_).c_str(),
                        orderIdToString(o_itr->prev_order_ ? o_itr->prev_order_->market_order_id_ :
                                        OrderId_INVALID).c_str(),
                        orderIdToString(o_itr->next_order_ ? o_itr->next_order_->market_order_id_ :
                                        OrderId_INVALID).c_str());
                ss << buf;
            }

            if (o_itr->next_order_ == itr->first_me_order_) {
                break;
            }
        }

        ss << std::endl;

        if (sanity_check) {
            if ((side == Side::SELL && last_price >= itr->price_) || (side == Side::BUY &&
                    last_price <= itr->price_)) {
                FATAL("Bids/Asks not sorted by ascending/descending prices last:" +
                      priceToString(last_price) + " itr:" + itr->toString());
            }

            last_price = itr->price_;
        }
    };

    ss << "Ticker:" << tickerIdToString(ticker_id_) << std::endl;
    {
        auto ask_itr = asks_by_price_;
        auto last_ask_price = std::numeric_limits<Price>::min();

        for (size_t count = 0; ask_itr; ++count) {
            ss << "ASKS L:" << count << " => ";
            auto next_ask_itr = (ask_itr->next_entry_ == asks_by_price_ ? nullptr :
                                 ask_itr->next_entry_);
            printer(ss, ask_itr, Side::SELL, last_ask_price, validity_check);
            ask_itr = next_ask_itr;
        }
    }

    ss << std::endl << "                          X" << std::endl << std::endl;

    {
        auto bid_itr = bids_by_price_;
        auto last_bid_price = std::numeric_limits<Price>::max();

        for (size_t count = 0; bid_itr; ++count) {
            ss << "BIDS L:" << count << " => ";
            auto next_bid_itr = (bid_itr->next_entry_ == bids_by_price_ ? nullptr :
                                 bid_itr->next_entry_);
            printer(ss, bid_itr, Side::BUY, last_bid_price, validity_check);
            bid_itr = next_bid_itr;
        }
    }

    return ss.str();
}
}
