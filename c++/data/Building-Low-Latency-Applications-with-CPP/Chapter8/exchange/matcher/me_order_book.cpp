/**
 * @file me_order_book.cpp
 * @brief 撮合引擎訂單簿實作檔案
 *
 * 實作 MEOrderBook 類別的核心撮合邏輯，包括：
 * - 訂單新增與取消操作
 * - FIFO (Price-Time Priority) 撮合演算法
 * - 雙向鏈結串列管理（買單/賣單分離）
 * - Memory Pool 記憶體管理（零動態分配）
 *
 * 核心設計原則：
 * 1. 單執行緒執行（避免 Lock）
 * 2. Memory Pool 預分配（消除 malloc/free）
 * 3. 使用指標算術優化查找（O(1) 訂單定位）
 * 4. 分支預測優化（LIKELY/UNLIKELY）
 *
 * 撮合流程：
 * 新單進入 → 檢查對手盤是否可撮合 → 撮合成交 → 剩餘數量掛單
 */
#include "me_order_book.h"

#include "matcher/matching_engine.h"

namespace Exchange
{
/**
 * @brief MEOrderBook 建構子
 *
 * 初始化訂單簿，預分配兩個 Memory Pool：
 * 1. orders_at_price_pool_：管理價格層級（MEOrdersAtPrice 物件池）
 * 2. order_pool_：管理個別訂單（MEOrder 物件池）
 *
 * @param ticker_id 商品代碼（例如：0 代表 BTC/USD）
 * @param logger 日誌記錄器指標
 * @param matching_engine 撮合引擎指標（用於發送成交回報與市場更新）
 *
 * 記憶體配置：
 * - orders_at_price_pool_ 預分配 ME_MAX_PRICE_LEVELS 個價格層級物件
 * - order_pool_ 預分配 ME_MAX_ORDER_IDS 個訂單物件
 * - 初始化時不進行任何 heap allocation
 */
MEOrderBook::MEOrderBook(TickerId ticker_id, Logger* logger,
                         MatchingEngine* matching_engine)
    : ticker_id_(ticker_id), matching_engine_(matching_engine),
      orders_at_price_pool_(ME_MAX_PRICE_LEVELS), order_pool_(ME_MAX_ORDER_IDS),
      logger_(logger)
{
}

/**
 * @brief MEOrderBook 解構子
 *
 * 關閉訂單簿時的清理工作：
 * 1. 記錄最終訂單簿狀態（用於除錯與審計）
 * 2. 清空所有指標引用（避免懸空指標）
 * 3. 重置客戶訂單查找表
 *
 * ⚠️ 注意：
 * - Memory Pool 的實際記憶體釋放由 Pool 的解構子處理
 * - 這裡只需要清空指標，不需要手動 delete
 * - toString(false, true) 會執行完整性檢查（validity_check = true）
 */
MEOrderBook::~MEOrderBook()
{
    // 記錄最終訂單簿狀態（詳細模式關閉，完整性檢查開啟）
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 toString(false, true));

    // 清空撮合引擎指標
    matching_engine_ = nullptr;

    // 清空買賣盤鏈結串列頭指標
    bids_by_price_ = asks_by_price_ = nullptr;

    // 重置客戶訂單查找表（ClientId -> OrderId -> MEOrder*）
    for (auto& itr : cid_oid_to_order_) {
        itr.fill(nullptr);
    }
}

/**
 * @brief ⚡ 撮合訂單核心函式（效能關鍵路徑）
 *
 * 將新進訂單（Aggressive Order）與訂單簿中的被動訂單（Passive Order）進行撮合成交。
 *
 * 撮合邏輯：
 * 1. 計算成交數量（取兩者較小值）
 * 2. 扣減雙方剩餘數量
 * 3. 發送成交回報給雙方客戶
 * 4. 發送市場更新（TRADE 事件）
 * 5. 處理被動訂單後續狀態：
 *    - 完全成交 → 發送 CANCEL 並從訂單簿移除
 *    - 部分成交 → 發送 MODIFY 更新剩餘數量
 *
 * @param ticker_id 商品代碼
 * @param client_id 主動方客戶 ID
 * @param side 主動方買賣方向
 * @param client_order_id 主動方客戶訂單 ID
 * @param new_market_order_id 主動方市場訂單 ID
 * @param itr 被動方訂單指標（訂單簿中的掛單）
 * @param leaves_qty 主動方剩餘數量（傳入傳出參數，會被修改）
 *
 * ⚡ 效能考量：
 * - noexcept 聲明：避免例外處理開銷
 * - 直接修改 leaves_qty 指標：避免回傳值拷貝
 * - 使用成員變數暫存回報結構：避免重複分配記憶體
 * - 最小化函式呼叫：直接呼叫 sendClientResponse/sendMarketUpdate
 *
 * 📊 撮合範例：
 * 新買單 100 張 @ $50，訂單簿有賣單 60 張 @ $50
 * → 成交 60 張，新買單剩餘 40 張，賣單完全成交並移除
 */
auto MEOrderBook::match(TickerId ticker_id, ClientId client_id, Side side,
                        OrderId client_order_id, OrderId new_market_order_id, MEOrder* itr,
                        Qty* leaves_qty) noexcept
{
    const auto order = itr;  // 被動方訂單（訂單簿中的掛單）
    const auto order_qty = order->qty_;  // 被動方原始數量（用於完全成交時的記錄）

    // ⚡ 計算成交數量（取主動方剩餘與被動方掛單的較小值）
    const auto fill_qty = std::min(*leaves_qty, order_qty);

    // 扣減雙方剩餘數量
    *leaves_qty -= fill_qty;  // 主動方剩餘數量（傳出參數）
    order->qty_ -= fill_qty;  // 被動方剩餘數量（直接修改訂單簿中的訂單）

    // 發送成交回報給主動方客戶（Aggressive Order FILLED）
    client_response_ = {ClientResponseType::FILLED, client_id, ticker_id, client_order_id,
                        new_market_order_id, side, itr->price_, fill_qty, *leaves_qty
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 發送成交回報給被動方客戶（Passive Order FILLED）
    client_response_ = {ClientResponseType::FILLED, order->client_id_, ticker_id, order->client_order_id_,
                        order->market_order_id_, order->side_, itr->price_, fill_qty, order->qty_
                       };
    matching_engine_->sendClientResponse(&client_response_);

    // 發送市場更新（TRADE 事件）給所有行情訂閱者
    // OrderId_INVALID 表示這是成交事件，不是單筆訂單異動
    market_update_ = {MarketUpdateType::TRADE, OrderId_INVALID, ticker_id, side, itr->price_, fill_qty, Priority_INVALID};
    matching_engine_->sendMarketUpdate(&market_update_);

    // 處理被動訂單後續狀態
    if (!order->qty_) {
        // 完全成交：從訂單簿移除並發送 CANCEL 事件
        // ⚠️ 注意：CANCEL 不是客戶主動取消，而是「因完全成交而移除」
        market_update_ = {MarketUpdateType::CANCEL, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order_qty, Priority_INVALID
                         };
        matching_engine_->sendMarketUpdate(&market_update_);

        removeOrder(order);  // 從鏈結串列移除並釋放回 Memory Pool
    } else {
        // 部分成交：更新訂單數量並發送 MODIFY 事件
        market_update_ = {MarketUpdateType::MODIFY, order->market_order_id_, ticker_id, order->side_,
                          order->price_, order->qty_, order->priority_
                         };
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}

/**
 * @brief ⚡ 檢查新訂單是否可撮合（效能關鍵路徑）
 *
 * 檢查新進訂單與對手盤是否有可撮合的價格，並執行撮合。
 *
 * 撮合規則：
 * - 買單：與最低賣價（asks_by_price_ 鏈表頭）比較
 *   → 如果買價 >= 賣價，則可撮合
 * - 賣單：與最高買價（bids_by_price_ 鏈表頭）比較
 *   → 如果賣價 <= 買價，則可撮合
 *
 * @param client_id 客戶 ID
 * @param client_order_id 客戶訂單 ID
 * @param ticker_id 商品代碼
 * @param side 買賣方向
 * @param price 限價（Limit Price）
 * @param qty 訂單數量
 * @param new_market_order_id 市場訂單 ID
 * @return 剩餘未成交數量（Leaves Quantity）
 *
 * ⚡ 效能優化：
 * - LIKELY 宏：提示編譯器「價格不匹配」是常見情況（大部分訂單不會立即成交）
 * - 雙向鏈結串列：asks_by_price_ 和 bids_by_price_ 已按價格排序
 *   → 只需檢查鏈表頭的 first_me_order_，O(1) 時間複雜度
 * - while 迴圈：持續撮合直到剩餘數量為 0 或無法再撮合
 *
 * 📊 撮合範例：
 * 新買單 100 張 @ $50
 * 訂單簿賣盤：60 張 @ $49, 40 張 @ $50, 100 張 @ $51
 * → 撮合 60 張 @ $49（完全成交），撮合 40 張 @ $50（完全成交）
 * → 剩餘 0 張（無需掛單）
 *
 * ⚠️ 注意：
 * - 撮合完成後，match() 會自動修改 leaves_qty
 * - 如果 leaves_qty > 0，呼叫方需要將剩餘數量掛單
 */
auto MEOrderBook::checkForMatch(ClientId client_id, OrderId client_order_id,
                                TickerId ticker_id, Side side, Price price, Qty qty,
                                Qty new_market_order_id) noexcept
{
    auto leaves_qty = qty;  // 剩餘未成交數量

    // 買單撮合邏輯：與賣盤比價
    if (side == Side::BUY) {
        while (leaves_qty && asks_by_price_) {
            // 取得最低賣價的第一筆訂單（FIFO，最早進入的訂單）
            const auto ask_itr = asks_by_price_->first_me_order_;

            // ⚡ LIKELY：大部分情況下價格不匹配（買價 < 賣價），無法撮合
            if (LIKELY(price < ask_itr->price_)) {
                break;  // 價格不匹配，結束撮合
            }

            // 價格匹配（買價 >= 賣價），執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, ask_itr,
                  &leaves_qty);
        }
    }

    // 賣單撮合邏輯：與買盤比價
    if (side == Side::SELL) {
        while (leaves_qty && bids_by_price_) {
            // 取得最高買價的第一筆訂單（FIFO，最早進入的訂單）
            const auto bid_itr = bids_by_price_->first_me_order_;

            // ⚡ LIKELY：大部分情況下價格不匹配（賣價 > 買價），無法撮合
            if (LIKELY(price > bid_itr->price_)) {
                break;  // 價格不匹配，結束撮合
            }

            // 價格匹配（賣價 <= 買價），執行撮合
            match(ticker_id, client_id, side, client_order_id, new_market_order_id, bid_itr,
                  &leaves_qty);
        }
    }

    return leaves_qty;  // 回傳剩餘未成交數量
}

/**
 * @brief ⚡ 新增訂單（效能關鍵路徑）
 *
 * 處理新訂單的完整流程：
 * 1. 生成市場訂單 ID（全域唯一）
 * 2. 發送 ACCEPTED 回報給客戶
 * 3. 嘗試撮合對手盤訂單
 * 4. 如有剩餘數量，將訂單加入訂單簿並發送 ADD 市場更新
 *
 * @param client_id 客戶 ID
 * @param client_order_id 客戶訂單 ID
 * @param ticker_id 商品代碼
 * @param side 買賣方向
 * @param price 限價
 * @param qty 訂單數量
 *
 * ⚡ 效能優化：
 * - LIKELY 宏：大部分訂單會有剩餘數量需要掛單（立即完全成交的情況較少）
 * - Memory Pool 分配：order_pool_.allocate() 從預分配的記憶體池取得訂單物件（O(1)）
 * - 避免動態記憶體分配：所有物件都從 Memory Pool 取得
 *
 * 📊 訂單處理流程：
 * 1. 新買單 100 張 @ $50 進入
 * 2. 生成 market_order_id = 12345
 * 3. 發送 ACCEPTED 回報給客戶
 * 4. checkForMatch() 嘗試撮合，假設撮合 60 張，剩餘 40 張
 * 5. 從 order_pool_ 分配訂單物件
 * 6. addOrder() 將剩餘 40 張加入買盤鏈結串列
 * 7. 發送 ADD 市場更新（通知所有行情訂閱者）
 *
 * ⚠️ 注意：
 * - generateNewMarketOrderId() 必須保證全域唯一性
 * - getNextPriority(price) 用於 FIFO 排序（相同價格按時間優先）
 * - addOrder() 負責維護雙向鏈結串列的正確性
 */
auto MEOrderBook::add(ClientId client_id, OrderId client_order_id,
                      TickerId ticker_id, Side side, Price price, Qty qty) noexcept -> void
{
    // 生成新的市場訂單 ID（全域唯一，單調遞增）
    const auto new_market_order_id = generateNewMarketOrderId();

    // 發送 ACCEPTED 回報給客戶（表示訂單已被接受）
    client_response_ = {ClientResponseType::ACCEPTED, client_id, ticker_id, client_order_id, new_market_order_id, side, price, 0, qty};
    matching_engine_->sendClientResponse(&client_response_);

    // 嘗試撮合對手盤訂單，回傳剩餘未成交數量
    const auto leaves_qty = checkForMatch(client_id, client_order_id, ticker_id,
                                          side, price, qty, new_market_order_id);

    // ⚡ LIKELY：大部分訂單會有剩餘數量需要掛單（立即完全成交的情況較少）
    if (LIKELY(leaves_qty)) {
        // 取得下一個優先權編號（用於 FIFO 排序）
        const auto priority = getNextPriority(price);

        // 從 Memory Pool 分配訂單物件（O(1)，無動態記憶體分配）
        auto order = order_pool_.allocate(ticker_id, client_id, client_order_id,
                                          new_market_order_id, side, price, leaves_qty, priority, nullptr,
                                          nullptr);

        // 將訂單加入訂單簿的雙向鏈結串列
        addOrder(order);

        // 發送 ADD 市場更新給所有行情訂閱者
        market_update_ = {MarketUpdateType::ADD, new_market_order_id, ticker_id, side, price, leaves_qty, priority};
        matching_engine_->sendMarketUpdate(&market_update_);
    }
}

/**
 * @brief 取消訂單
 *
 * 處理客戶取消訂單請求，驗證訂單是否存在並執行取消操作。
 *
 * 取消流程：
 * 1. 檢查 client_id 是否合法（範圍檢查）
 * 2. 從 cid_oid_to_order_ 查找表中查找訂單
 * 3. 驗證訂單是否存在
 * 4. 如果存在：
 *    - 發送 CANCELED 回報給客戶
 *    - 發送 CANCEL 市場更新
 *    - 從訂單簿移除訂單
 * 5. 如果不存在：發送 CANCEL_REJECTED 回報
 *
 * @param client_id 客戶 ID
 * @param order_id 客戶訂單 ID
 * @param ticker_id 商品代碼
 *
 * ⚡ 效能優化：
 * - O(1) 訂單查找：使用二維陣列 cid_oid_to_order_[client_id][order_id]
 * - LIKELY/UNLIKELY 宏：大部分取消請求都是合法的（提示編譯器優化分支）
 * - 兩階段驗證：
 *   1. 先檢查 client_id 範圍（避免越界存取）
 *   2. 再檢查訂單指標是否為 nullptr
 *
 * 📊 取消範例：
 * 客戶 ID 3 想取消訂單 ID 1001
 * → cid_oid_to_order_[3][1001] 找到訂單指標
 * → removeOrder() 從鏈結串列移除並釋放回 Memory Pool
 * → 發送 CANCELED 回報與 CANCEL 市場更新
 *
 * ⚠️ 注意：
 * - 取消不存在的訂單不會拋出例外，而是回傳 CANCEL_REJECTED
 * - removeOrder() 會自動維護雙向鏈結串列的完整性
 * - 訂單取消後，Memory Pool 會回收該訂單物件供後續使用
 */
auto MEOrderBook::cancel(ClientId client_id, OrderId order_id,
                         TickerId ticker_id) noexcept -> void
{
    // 第一階段驗證：檢查 client_id 是否在合法範圍內
    auto is_cancelable = (client_id < cid_oid_to_order_.size());
    MEOrder* exchange_order = nullptr;

    // ⚡ LIKELY：大部分取消請求都是合法的
    if (LIKELY(is_cancelable)) {
        // O(1) 查找訂單：cid_oid_to_order_[client_id][order_id]
        auto& co_itr = cid_oid_to_order_.at(client_id);
        exchange_order = co_itr.at(order_id);

        // 第二階段驗證：檢查訂單是否存在（指標非 nullptr）
        is_cancelable = (exchange_order != nullptr);
    }

    // ⚡ UNLIKELY：訂單不存在的情況較少見
    if (UNLIKELY(!is_cancelable)) {
        // 發送 CANCEL_REJECTED 回報給客戶
        client_response_ = {ClientResponseType::CANCEL_REJECTED, client_id, ticker_id, order_id, OrderId_INVALID,
                            Side::INVALID, Price_INVALID, Qty_INVALID, Qty_INVALID
                           };
    } else {
        // 發送 CANCELED 回報給客戶
        client_response_ = {ClientResponseType::CANCELED, client_id, ticker_id, order_id, exchange_order->market_order_id_,
                            exchange_order->side_, exchange_order->price_, Qty_INVALID, exchange_order->qty_
                           };

        // 發送 CANCEL 市場更新給所有行情訂閱者
        // ⚠️ 注意：qty 欄位設為 0（表示訂單已完全取消）
        market_update_ = {MarketUpdateType::CANCEL, exchange_order->market_order_id_, ticker_id, exchange_order->side_, exchange_order->price_, 0,
                          exchange_order->priority_
                         };

        // 從訂單簿移除訂單並釋放回 Memory Pool
        removeOrder(exchange_order);

        // 發送市場更新
        matching_engine_->sendMarketUpdate(&market_update_);
    }

    // 發送客戶回報（CANCELED 或 CANCEL_REJECTED）
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
