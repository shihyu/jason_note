#include "me_order_book.h"

#include "matcher/matching_engine.h"

namespace Exchange
{
// ============================================================================
// MEOrderBook 建構子 - 交易所撮合引擎訂單簿初始化
// ============================================================================
//
// 📌 功能：初始化撮合引擎的訂單簿（交易所伺服器端）
//
// 初始化流程：
// 1. 儲存交易標的 ID
// 2. 關聯撮合引擎指標（用於發送回報與行情更新）
// 3. 創建價位記憶體池（orders_at_price_pool_）
// 4. 創建訂單記憶體池（order_pool_）
// 5. 關聯日誌記錄器
//
// 🔗 與 Trading::MarketOrderBook 的差異：
// - MEOrderBook：交易所端的訂單簿（伺服器端，權威版本）
// - MarketOrderBook：客戶端的訂單簿副本（客戶端，本地快照）
// - MEOrderBook 負責撮合邏輯、產生成交與回報
// - MarketOrderBook 只負責維護本地副本、提供策略查詢
//
// ⚡ 效能設計：
// - Memory Pool：預先分配記憶體（ME_MAX_PRICE_LEVELS, ME_MAX_ORDER_IDS）
// - 零動態分配：所有物件從 Pool 取得
// - Cache 友善：連續記憶體佈局
//
// 📊 記憶體預算（每個交易標的）：
// - MEOrdersAtPrice：~40 bytes × ME_MAX_PRICE_LEVELS
// - MEOrder：~80 bytes × ME_MAX_ORDER_IDS（比客戶端多 client_id_ 等欄位）
//
// @param ticker_id: 交易標的 ID
// @param logger: 日誌記錄器指標
// @param matching_engine: 撮合引擎指標（用於發送回報）
MEOrderBook::MEOrderBook(TickerId ticker_id, Logger* logger,
                         MatchingEngine* matching_engine)
    : ticker_id_(ticker_id), matching_engine_(matching_engine),
      orders_at_price_pool_(ME_MAX_PRICE_LEVELS), order_pool_(ME_MAX_ORDER_IDS),
      logger_(logger)
{
}

MEOrderBook::~MEOrderBook()
{
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 toString(false, true));

    matching_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;

    for (auto& itr : cid_oid_to_order_) {
        itr.fill(nullptr);
    }
}

// ============================================================================
// match() - 撮合函式（核心熱路徑）
// ============================================================================
//
// 📌 功能：執行訂單撮合，產生成交，發送回報與行情更新
//
// 撮合邏輯：
// 1. 計算成交數量 = min(新訂單剩餘量, 對手單數量)
// 2. 更新雙方訂單的剩餘數量
// 3. 發送成交回報給雙方客戶端（FILLED）
// 4. 發送成交行情更新（TRADE）
// 5. 處理對手單狀態：
//    - 全部成交 → 發送 CANCEL 行情更新，從訂單簿移除
//    - 部分成交 → 發送 MODIFY 行情更新，保留在訂單簿
//
// ⚡ 效能關鍵：
// - **撮合引擎的最熱路徑**：每次撮合約 50-100 ns
// - 零動態記憶體分配
// - 零虛函式呼叫
// - 結構初始化（POD 類型）
//
// 📊 撮合範例：
// - 新買單：BUY 100 張 @ 100.00，剩餘 100 張
// - 對手賣單：SELL 70 張 @ 100.00
// - 成交：70 張 @ 100.00
// - 結果：新買單剩餘 30 張，對手賣單全部成交並移除
//
// ⚠️ 注意事項：
// - noexcept 保證：撮合不會拋出異常
// - leaves_qty 會被修改：傳入時為新訂單剩餘量
// - 對手單可能被移除：match 後 itr 可能失效
//
// @param ticker_id: 交易標的 ID
// @param client_id: 新訂單的客戶端 ID
// @param side: 新訂單的買賣方向
// @param client_order_id: 新訂單的客戶端訂單 ID
// @param new_market_order_id: 新訂單的市場訂單 ID
// @param itr: 對手單指標
// @param leaves_qty: 新訂單剩餘數量（輸入/輸出參數）
auto MEOrderBook::match(TickerId ticker_id, ClientId client_id, Side side,
                        OrderId client_order_id, OrderId new_market_order_id, MEOrder* itr,
                        Qty* leaves_qty) noexcept
{
    const auto order = itr;  // 對手單
    const auto order_qty = order->qty_;  // 對手單原始數量（用於行情更新）
    const auto fill_qty = std::min(*leaves_qty, order_qty);  // 成交數量

    // 更新雙方剩餘數量
    *leaves_qty -= fill_qty;  // 新訂單剩餘量
    order->qty_ -= fill_qty;  // 對手單剩餘量

    // 發送成交回報給新訂單的客戶端（第一方）
    client_response_ = {ClientResponseType::FILLED, client_id, ticker_id, client_order_id,
                        new_market_order_id, side, itr->price_, fill_qty, *leaves_qty
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 發送成交回報給對手單的客戶端（第二方）
    client_response_ = {ClientResponseType::FILLED, order->client_id_, ticker_id, order->client_order_id_,
                        order->market_order_id_, order->side_, itr->price_, fill_qty, order->qty_
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 發送成交行情更新（市場數據）
    // 📌 TRADE 事件：所有訂閱者都會收到（用於價格發現、趨勢判斷）
    market_update_ = {MarketUpdateType::TRADE, OrderId_INVALID, ticker_id, side, itr->price_, fill_qty, Priority_INVALID};
    matching_engine_->sendMarketUpdate(&market_update_);

    // 處理對手單狀態
    if (!order->qty_) {
        // 對手單全部成交 → 發送 CANCEL 行情更新並移除
        market_update_ = {MarketUpdateType::CANCEL, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order_qty, Priority_INVALID
                         };
        matching_engine_->sendMarketUpdate(&market_update_);

        // 從訂單簿移除（回收到 Memory Pool）
        removeOrder(order);
    } else {
        // 對手單部分成交 → 發送 MODIFY 行情更新（數量減少）
        market_update_ = {MarketUpdateType::MODIFY, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order->qty_, order->priority_
                         };
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}

// ============================================================================
// checkForMatch() - 檢查並執行撮合（Price-Time Priority）
// ============================================================================
//
// 📌 功能：檢查新訂單是否能與訂單簿中的對手單撮合
//
// 撮合規則（Price-Time Priority）：
// 1. 價格優先：買單價格 >= 賣單價格 → 可撮合
// 2. 時間優先：同價位按 FIFO 順序撮合
// 3. 循環撮合：持續撮合直到新訂單完全成交或無對手單
//
// ⚡ 效能特性：
// - LIKELY 優化：大多數訂單不會立即撮合（限價單掛單）
// - 連續撮合：一次處理多個對手單（市價單場景）
// - O(M) 時間複雜度：M = 撮合的對手單數量
//
// 📊 範例（買單撮合）：
// - 新買單：BUY 100 張 @ 100.50
// - 訂單簿賣單：
//   - 100.40: 30 張 → 撮合 30 張（剩餘 70 張）
//   - 100.45: 50 張 → 撮合 50 張（剩餘 20 張）
//   - 100.50: 40 張 → 撮合 20 張（新訂單完全成交）
// - 返回：0（leaves_qty = 0，完全成交）
//
// @return 剩餘未成交數量（0 = 完全成交）
auto MEOrderBook::checkForMatch(ClientId client_id, OrderId client_order_id,
                                TickerId ticker_id, Side side, Price price, Qty qty,
                                Qty new_market_order_id) noexcept
{
    auto leaves_qty = qty;

    // 買單撮合邏輯：與賣單對撮
    if (side == Side::BUY) {
        while (leaves_qty && asks_by_price_) {
            const auto ask_itr = asks_by_price_->first_me_order_;

            // LIKELY：大多數限價單不會立即撮合
            if (LIKELY(price < ask_itr->price_)) {
                break;  // 買價 < 賣價 → 無法撮合
            }

            // 買價 >= 賣價 → 執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, ask_itr,
                  &leaves_qty);
        }
    }

    // 賣單撮合邏輯：與買單對撮
    if (side == Side::SELL) {
        while (leaves_qty && bids_by_price_) {
            const auto bid_itr = bids_by_price_->first_me_order_;

            // LIKELY：大多數限價單不會立即撮合
            if (LIKELY(price > bid_itr->price_)) {
                break;  // 賣價 > 買價 → 無法撮合
            }

            // 賣價 <= 買價 → 執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, bid_itr,
                  &leaves_qty);
        }
    }

    return leaves_qty;  // 返回剩餘未成交數量
}

// ============================================================================
// add() - 新增訂單（撮合引擎入口）
// ============================================================================
//
// 📌 功能：接收新訂單，執行撮合檢查，將未成交部分加入訂單簿
//
// 處理流程：
// 1. 產生市場訂單 ID（market_order_id_）
// 2. 發送 ACCEPTED 回報（訂單已接受）
// 3. 執行撮合檢查（checkForMatch）
// 4. 如果有剩餘未成交數量：
//    a. 分配訂單物件（從 Memory Pool）
//    b. 加入訂單簿（addOrder）
//    c. 發送 ADD 行情更新
//
// ⚡ 效能特性：
// - LIKELY：大多數訂單有剩餘量（限價單掛單）
// - Memory Pool 分配：O(1)
// - Priority 分配：奈秒級時間戳
//
// 📊 範例（部分成交）：
// - 新訂單：BUY 100 張 @ 100.50
// - 撮合後剩餘：30 張
// - 結果：
//   1. ACCEPTED 回報
//   2. 2 筆 FILLED 回報（撮合的 70 張）
//   3. 將 30 張加入訂單簿
//   4. ADD 行情更新（30 張 @ 100.50）
//
// @param client_id: 客戶端 ID
// @param client_order_id: 客戶端訂單 ID
// @param ticker_id: 交易標的 ID
// @param side: 買賣方向
// @param price: 訂單價格
// @param qty: 訂單數量
auto MEOrderBook::add(ClientId client_id, OrderId client_order_id,
                      TickerId ticker_id, Side side, Price price, Qty qty) noexcept -> void
{
    // 1. 產生市場訂單 ID（撮合引擎內部 ID）
    const auto new_market_order_id = generateNewMarketOrderId();

    // 2. 發送 ACCEPTED 回報（訂單已接受，進入處理流程）
    client_response_ = {ClientResponseType::ACCEPTED, client_id, ticker_id, client_order_id, new_market_order_id, side, price, 0, qty};
    matching_engine_->sendClientResponse(&client_response_);

    // 3. 執行撮合檢查（可能產生多筆 FILLED 回報）
    const auto leaves_qty = checkForMatch(client_id, client_order_id, ticker_id,
                                          side, price, qty, new_market_order_id);

    // 4. 處理剩餘未成交數量
    if (LIKELY(leaves_qty)) {
        // 分配優先權（時間戳，用於 FIFO 排序）
        const auto priority = getNextPriority(price);

        // 從 Memory Pool 分配訂單物件
        auto order = order_pool_.allocate(ticker_id, client_id, client_order_id,
                                          new_market_order_id, side, price, leaves_qty, priority, nullptr,
                                          nullptr);
        // 加入訂單簿（維護價位鏈結串列）
        addOrder(order);

        // 發送 ADD 行情更新（通知訂閱者新訂單加入）
        market_update_ = {MarketUpdateType::ADD, new_market_order_id, ticker_id, side, price, leaves_qty, priority};
        matching_engine_->sendMarketUpdate(&market_update_);
    }
    // 註：如果 leaves_qty == 0（完全成交），則不加入訂單簿
}

// ============================================================================
// cancel() - 取消訂單
// ============================================================================
//
// 📌 功能：取消訂單簿中的訂單，發送回報與行情更新
//
// 處理流程：
// 1. 驗證訂單是否可取消（檢查 client_id 和 order_id）
// 2. 如果不可取消：
//    - 發送 CANCEL_REJECTED 回報
// 3. 如果可取消：
//    - 從訂單簿移除訂單（removeOrder）
//    - 發送 CANCELED 回報
//    - 發送 CANCEL 行情更新
//
// ⚠️ 取消失敗原因：
// - 訂單不存在（已成交或已取消）
// - client_id 無效
// - order_id 無效
//
// ⚡ 效能特性：
// - UNLIKELY：取消失敗是罕見情況
// - O(1) 查找：透過 cid_oid_to_order_ 雜湊表
//
// @param client_id: 客戶端 ID
// @param order_id: 客戶端訂單 ID
// @param ticker_id: 交易標的 ID
auto MEOrderBook::cancel(ClientId client_id, OrderId order_id,
                         TickerId ticker_id) noexcept -> void
{
    // 1. 驗證 client_id 範圍
    auto is_cancelable = (client_id < cid_oid_to_order_.size());
    MEOrder* exchange_order = nullptr;

    if (LIKELY(is_cancelable)) {
        // 2. 查找訂單
        auto& co_itr = cid_oid_to_order_.at(client_id);
        exchange_order = co_itr.at(order_id);
        is_cancelable = (exchange_order != nullptr);
    }

    // 3. 處理取消失敗
    if (UNLIKELY(!is_cancelable)) {
        client_response_ = {ClientResponseType::CANCEL_REJECTED, client_id, ticker_id, order_id, OrderId_INVALID,
                            Side::INVALID, Price_INVALID, Qty_INVALID, Qty_INVALID
                           };
    } else {
        // 4. 處理取消成功
        client_response_ = {ClientResponseType::CANCELED, client_id, ticker_id, order_id, exchange_order->market_order_id_,
                            exchange_order->side_, exchange_order->price_, Qty_INVALID, exchange_order->qty_
                           };
        market_update_ = {MarketUpdateType::CANCEL, exchange_order->market_order_id_, ticker_id, exchange_order->side_, exchange_order->price_, 0,
                          exchange_order->priority_
                         };

        // 從訂單簿移除（回收到 Memory Pool）
        removeOrder(exchange_order);

        // 發送 CANCEL 行情更新
        matching_engine_->sendMarketUpdate(&market_update_);
    }

    // 發送回報（CANCELED 或 CANCEL_REJECTED）
    matching_engine_->sendClientResponse(&client_response_);
}

auto MEOrderBook::toString(bool detailed,
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
