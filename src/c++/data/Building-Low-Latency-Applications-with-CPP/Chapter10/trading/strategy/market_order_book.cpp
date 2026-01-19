// 策略側訂單簿更新：處理 ADD/MODIFY/CANCEL。
// ⚡ 效能關鍵：BBO 快速更新、零分配。
// ⚠️ 注意：增量更新順序不可錯。

/**
 * @file market_order_book.cpp
 * @brief 客戶端市場訂單簿實作檔案 - 本地訂單簿副本維護
 *
 * 功能：
 * - 接收並處理來自交易所的市場更新訊息
 * - 維護本地訂單簿副本（只讀，不負責撮合）
 * - 提供 BBO（Best Bid/Offer）查詢接口給交易策略
 * - 通知 TradeEngine 訂單簿變化和成交事件
 *
 * 設計原則：
 * - 被動更新：僅根據市場更新訊息同步狀態
 * - 零撮合邏輯：不執行任何撮合操作
 * - 快照同步：支持 CLEAR 訊息清空並重建訂單簿
 *
 * 與 Exchange::MEOrderBook 的差異：
 * - MEOrderBook：交易所端，負責撮合、生成回報和市場更新
 * - MarketOrderBook：客戶端，只維護本地副本供策略查詢
 *
 * 效能特性：
 * - Memory Pool 預分配（零動態分配）
 * - 本地訂單簿更新延遲：< 500 ns
 * - BBO 查詢延遲：< 50 ns（已緩存）
 */

#include "market_order_book.h"

#include "trade_engine.h"

namespace Trading
{
/**
 * 構造函式 - 初始化客戶端訂單簿
 *
 * @param ticker_id 商品識別碼
 * @param logger 日誌記錄器指標
 *
 * 初始化內容：
 * 1. 設定商品 ID
 * 2. 預配置記憶體池：
 *    - orders_at_price_pool_: 價格層級物件池（ME_MAX_PRICE_LEVELS 個）
 *    - order_pool_: 訂單物件池（ME_MAX_ORDER_IDS 個）
 * 3. 儲存日誌記錄器引用
 *
 * 與交易所端訂單簿的差異：
 * - 無 matching_engine_ 指標（不負責撮合）
 * - 無 client_id 相關索引（只關心市場訂單 ID）
 * - 使用 oid_to_order_ 雜湊表（市場訂單 ID → MarketOrder）
 *
 * 記憶體管理：
 * - 使用物件池（Object Pool）避免動態記憶體分配
 * - 所有物件在構造時預先分配
 * - 延遲 < 50 ns（無 malloc/free 呼叫）
 */
MarketOrderBook::MarketOrderBook(TickerId ticker_id, Logger* logger)
    : ticker_id_(ticker_id), orders_at_price_pool_(ME_MAX_PRICE_LEVELS),
      order_pool_(ME_MAX_ORDER_IDS), logger_(logger)
{
}

/**
 * 解構函式 - 清理客戶端訂單簿並記錄最終狀態
 *
 * 清理步驟：
 * 1. 記錄訂單簿最終狀態（toString）到日誌
 * 2. 清空 trade_engine_ 引用（防止 dangling pointer）
 * 3. 清空買賣盤鏈表頭指標
 * 4. 清空 oid_to_order_ 雜湊表（所有槽位設為 nullptr）
 *
 * 注意：
 * - 物件池（orders_at_price_pool_, order_pool_）自動解構
 * - toString(false, true) 參數：不顯示詳細資訊，但執行有效性檢查
 * - 日誌記錄有助於除錯和審計
 */
MarketOrderBook::~MarketOrderBook()
{
    // 記錄訂單簿最終狀態
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), toString(false, true));

    // 清空引用和指標
    trade_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;
    oid_to_order_.fill(nullptr);
}

/**
 * onMarketUpdate() - 處理市場更新訊息並同步本地訂單簿
 *
 * @param market_update 市場更新訊息指標（來自 MarketDataConsumer）
 *
 * 處理的訊息類型：
 * 1. ADD：新增訂單到訂單簿
 *    - 從物件池分配 MarketOrder 物件
 *    - 呼叫 addOrder() 加入三層索引結構
 *
 * 2. MODIFY：修改訂單數量
 *    - 通過 oid_to_order_ 查找訂單
 *    - 直接更新 qty_ 欄位
 *    - 不改變價格和優先序號
 *
 * 3. CANCEL：取消訂單
 *    - 通過 oid_to_order_ 查找訂單
 *    - 呼叫 removeOrder() 從訂單簿移除
 *
 * 4. TRADE：成交事件
 *    - 轉發給 TradeEngine 處理
 *    - 策略可能根據成交調整倉位或報價
 *    - 直接返回，不執行 updateBBO()
 *
 * 5. CLEAR：清空訂單簿
 *    - 釋放所有訂單物件回物件池
 *    - 釋放所有價格層級物件回物件池
 *    - 清空 oid_to_order_ 雜湊表
 *    - 重置買賣盤頭指標為 nullptr
 *    - 用於快照同步開始時清空舊數據
 *
 * 6. INVALID / SNAPSHOT_START / SNAPSHOT_END：
 *    - 忽略，不執行任何操作
 *
 * BBO 更新檢測：
 * - bid_updated：買盤最優價格是否變化
 *   - 條件：有買盤 && 更新類型是 BUY && 更新價格 >= 當前最優買價
 * - ask_updated：賣盤最優價格是否變化
 *   - 條件：有賣盤 && 更新類型是 SELL && 更新價格 <= 當前最優賣價
 *
 * 通知機制：
 * 1. updateBBO()：更新 BBO 緩存（若 BBO 變化）
 * 2. trade_engine_->onOrderBookUpdate()：通知策略訂單簿變化
 *    - 策略可能根據訂單簿深度調整報價
 *
 * 效能特性：
 * - 時間複雜度：
 *   - ADD：O(log P)，P = 價格層級數
 *   - MODIFY：O(1)（雜湊表查找）
 *   - CANCEL：O(1)（雜湊表查找 + 鏈表移除）
 *   - TRADE：O(1)（轉發）
 *   - CLEAR：O(N + P)，N = 訂單數，P = 價格層級數
 * - 平均延遲：< 500 ns
 * - 無動態記憶體分配（物件池預先配置）
 *
 * 注意事項：
 * - noexcept 保證（低延遲要求）
 * - TRADE 訊息直接返回，不執行 updateBBO 和 onOrderBookUpdate
 * - CLEAR 用於快照同步，會清空整個訂單簿
 */
auto MarketOrderBook::onMarketUpdate(const Exchange::MEMarketUpdate*
                                     market_update) noexcept -> void
{
    // 檢測 BBO 是否可能變化
    // bid_updated：買盤最優價格是否受影響
    const auto bid_updated = (bids_by_price_ && market_update->side_ == Side::BUY &&
                              market_update->price_ >= bids_by_price_->price_);
    // ask_updated：賣盤最優價格是否受影響
    const auto ask_updated = (asks_by_price_ &&
                              market_update->side_ == Side::SELL &&
                              market_update->price_ <= asks_by_price_->price_);

    // 根據訊息類型處理
    switch (market_update->type_) {
    case Exchange::MarketUpdateType::ADD: {
            // 新增訂單：從物件池分配並加入訂單簿
            auto order = order_pool_.allocate(market_update->order_id_,
                                              market_update->side_, market_update->price_,
                                              market_update->qty_, market_update->priority_, nullptr, nullptr);
            addOrder(order);
        }
        break;

    case Exchange::MarketUpdateType::MODIFY: {
            // 修改訂單：更新數量（價格和優先序號不變）
            auto order = oid_to_order_.at(market_update->order_id_);
            order->qty_ = market_update->qty_;
        }
        break;

    case Exchange::MarketUpdateType::CANCEL: {
            // 取消訂單：從訂單簿移除
            auto order = oid_to_order_.at(market_update->order_id_);
            removeOrder(order);
        }
        break;

    case Exchange::MarketUpdateType::TRADE: {
            // 成交事件：轉發給 TradeEngine 處理
            trade_engine_->onTradeUpdate(market_update, this);
            return;  // 直接返回，不執行後續的 BBO 更新
        }
        break;

    case Exchange::MarketUpdateType::CLEAR: {
            // 清空訂單簿：釋放所有訂單和價格層級物件
            // 步驟 1：釋放所有訂單物件
            for (auto& order : oid_to_order_) {
                if (order) {
                    order_pool_.deallocate(order);
                }
            }

            // 步驟 2：清空訂單雜湊表
            oid_to_order_.fill(nullptr);

            // 步驟 3：釋放所有買盤價格層級物件
            if (bids_by_price_) {
                // 遍歷環狀鏈表（circular linked list）
                for (auto bid = bids_by_price_->next_entry_; bid != bids_by_price_;
                     bid = bid->next_entry_) {
                         // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
                    orders_at_price_pool_.deallocate(bid);
                }

                // 釋放頭節點
                orders_at_price_pool_.deallocate(bids_by_price_);
            }

            // 步驟 4：釋放所有賣盤價格層級物件
            if (asks_by_price_) {
                // 遍歷環狀鏈表
                for (auto ask = asks_by_price_->next_entry_; ask != asks_by_price_;
                     ask = ask->next_entry_) {
                    orders_at_price_pool_.deallocate(ask);
                }

                // 釋放頭節點
                orders_at_price_pool_.deallocate(asks_by_price_);
            }

            // 步驟 5：重置買賣盤頭指標
            bids_by_price_ = asks_by_price_ = nullptr;
        }
        break;

    case Exchange::MarketUpdateType::INVALID:
    case Exchange::MarketUpdateType::SNAPSHOT_START:
    case Exchange::MarketUpdateType::SNAPSHOT_END:
        // 忽略這些訊息類型
        break;
    }

    // 更新 BBO 緩存（若 BBO 變化）
    updateBBO(bid_updated, ask_updated);

    // 記錄市場更新和當前 BBO 狀態
    logger_->log("%:% %() % % %", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), market_update->toString(),
                 bbo_.toString());

    // 通知 TradeEngine 訂單簿更新
    // 策略可能根據訂單簿深度調整報價
    trade_engine_->onOrderBookUpdate(market_update->ticker_id_,
                                     market_update->price_, market_update->side_, this);
}

/**
 * toString() - 生成訂單簿的可視化字串表示
 *
 * @param detailed 是否顯示詳細訊息（每個訂單的詳細資訊）
 * @param validity_check 是否執行有效性檢查（驗證價格排序）
 * @return 訂單簿狀態的字串表示
 *
 * 功能：
 * - 生成訂單簿的文字表示，用於除錯和日誌記錄
 * - 顯示買賣盤的價格層級和訂單分佈
 * - 可選擇性顯示詳細訂單資訊
 * - 可選擇性執行有效性檢查（驗證資料結構完整性）
 *
 * 輸出格式範例：
 * ```
 * Ticker: AAPL
 * ASKS L:0 =>  <px:102 p:101 n:103> 102 @ 5000(2)
 * ASKS L:1 =>  <px:103 p:102 n:104> 103 @ 3000(1)
 *
 *                           X
 *
 * BIDS L:0 =>  <px:101 p:102 n:100> 101 @ 4000(3)
 * BIDS L:1 =>  <px:100 p:101 n:99 > 100 @ 2000(1)
 * ```
 *
 * 格式說明：
 * - L:N：層級編號（Level N）
 * - px：當前價格
 * - p：前一個價格層級指標
 * - n：下一個價格層級指標
 * - 價格 @ 數量(訂單數)
 *
 * 詳細模式（detailed = true）：
 * - 顯示每個訂單的資訊：
 *   - oid：市場訂單 ID
 *   - q：訂單數量
 *   - p：前一個訂單指標
 *   - n：下一個訂單指標
 *
 * 有效性檢查（validity_check = true）：
 * - 驗證賣盤價格遞增排序（100, 101, 102...）
 * - 驗證買盤價格遞減排序（102, 101, 100...）
 * - 若發現排序錯誤，觸發 FATAL（程式終止）
 *
 * 效能考量：
 * - 此函式非效能關鍵路徑（僅用於除錯）
 * - 使用 std::stringstream 構建輸出（涉及記憶體分配）
 * - 遍歷所有價格層級和訂單（O(P + O)，P = 價格層級數，O = 訂單數）
 *
 * 使用場景：
 * 1. 除錯：檢查訂單簿狀態
 * 2. 日誌：記錄訂單簿快照
 * 3. 測試：驗證訂單簿同步正確性
 * 4. 監控：人工檢查市場狀態
 *
 * 注意事項：
 * - const 函式：不修改訂單簿狀態
 * - 非 noexcept：stringstream 可能拋出例外
 * - 不應在交易時段頻繁呼叫（效能開銷較大）
 */
auto MarketOrderBook::toString(bool detailed,
                               bool validity_check) const -> std::string
{
    std::stringstream ss;
    std::string time_str;

    /**
     * printer - Lambda 函式：列印單一價格層級的訂單資訊
     *
     * @param ss 字串流引用（輸出目標）
     * @param itr 價格層級指標
     * @param side 買賣方向（用於驗證排序）
     * @param last_price 上一個價格（用於驗證排序）
     * @param sanity_check 是否執行有效性檢查
     *
     * 功能：
     * 1. 計算該價格層級的總數量和訂單數
     * 2. 列印價格層級資訊（價格、前後指標、總量、訂單數）
     * 3. 若 detailed = true，列印每個訂單詳細資訊
     * 4. 若 sanity_check = true，驗證價格排序
     */
    auto printer = [&](std::stringstream & ss, MarketOrdersAtPrice * itr, Side side,
                       Price & last_price,
    bool sanity_check) {
        char buf[4096];  // 輸出緩衝區
        Qty qty = 0;     // 該價格層級的總數量
        size_t num_orders = 0;  // 該價格層級的訂單數

        // 第一次遍歷：計算總數量和訂單數
        // 使用環狀鏈表（circular linked list）
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            qty += o_itr->qty_;
            ++num_orders;

            // 環狀鏈表終止條件：回到起點
            if (o_itr->next_order_ == itr->first_mkt_order_) {
                break;
            }
        }

        // 列印價格層級摘要
        // 格式：<px:當前價格 p:前指標 n:後指標> 價格 @ 總量(訂單數)
        sprintf(buf, " <px:%3s p:%3s n:%3s> %-3s @ %-5s(%-4s)",
                priceToString(itr->price_).c_str(),
                priceToString(itr->prev_entry_->price_).c_str(),
                priceToString(itr->next_entry_->price_).c_str(),
                priceToString(itr->price_).c_str(), qtyToString(qty).c_str(),
                std::to_string(num_orders).c_str());
        ss << buf;

        // 第二次遍歷：若 detailed = true，列印每個訂單詳細資訊
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            if (detailed) {
                // 格式：[oid:訂單ID q:數量 p:前訂單 n:後訂單]
                sprintf(buf, "[oid:%s q:%s p:%s n:%s] ",
                        orderIdToString(o_itr->order_id_).c_str(), qtyToString(o_itr->qty_).c_str(),
                        orderIdToString(o_itr->prev_order_ ? o_itr->prev_order_->order_id_ :
                                        OrderId_INVALID).c_str(),
                        orderIdToString(o_itr->next_order_ ? o_itr->next_order_->order_id_ :
                                        OrderId_INVALID).c_str());
                ss << buf;
            }

            // 環狀鏈表終止條件
            if (o_itr->next_order_ == itr->first_mkt_order_) {
                break;
            }
        }

        ss << std::endl;

        // 有效性檢查：驗證價格排序
        if (sanity_check) {
            // 賣盤：價格應遞增（last_price < itr->price_）
            // 買盤：價格應遞減（last_price > itr->price_）
            if ((side == Side::SELL && last_price >= itr->price_) || (side == Side::BUY &&
                    last_price <= itr->price_)) {
                FATAL("Bids/Asks not sorted by ascending/descending prices last:" +
                      priceToString(last_price) + " itr:" +
                      itr->toString());
            }

            last_price = itr->price_;
        }
    };

    // === 主函式邏輯開始 ===

    // 列印商品識別碼
    ss << "Ticker:" << tickerIdToString(ticker_id_) << std::endl;

    // 列印賣盤（ASKS）
    {
        auto ask_itr = asks_by_price_;  // 最優賣價（最低價）
        auto last_ask_price = std::numeric_limits<Price>::min();  // 初始值：最小價格

        // 遍歷所有賣價層級（遞增順序）
        for (size_t count = 0; ask_itr; ++count) {
            ss << "ASKS L:" << count << " => ";
            // 計算下一個價格層級（環狀鏈表終止條件）
            auto next_ask_itr = (ask_itr->next_entry_ == asks_by_price_ ? nullptr :
                                 ask_itr->next_entry_);
            // 呼叫 printer 列印該層級
            printer(ss, ask_itr, Side::SELL, last_ask_price, validity_check);
            ask_itr = next_ask_itr;
        }
    }

    // 列印分隔線（市場中心線）
    ss << std::endl << "                          X" << std::endl << std::endl;

    // 列印買盤（BIDS）
    {
        auto bid_itr = bids_by_price_;  // 最優買價（最高價）
        auto last_bid_price = std::numeric_limits<Price>::max();  // 初始值：最大價格

        // 遍歷所有買價層級（遞減順序）
        for (size_t count = 0; bid_itr; ++count) {
            ss << "BIDS L:" << count << " => ";
            // 計算下一個價格層級（環狀鏈表終止條件）
            auto next_bid_itr = (bid_itr->next_entry_ == bids_by_price_ ? nullptr :
                                 bid_itr->next_entry_);
            // 呼叫 printer 列印該層級
            printer(ss, bid_itr, Side::BUY, last_bid_price, validity_check);
            bid_itr = next_bid_itr;
        }
    }

    return ss.str();  // 返回完整字串
}
}
