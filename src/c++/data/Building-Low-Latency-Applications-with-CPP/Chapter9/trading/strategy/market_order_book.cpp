// ============================================================================
// MarketOrderBook 實作檔案
// ============================================================================
//
// 職責:
// - 維護 Trading Client 本地的 Order Book 快照（從市場更新重建）
// - 處理市場更新事件（ADD, MODIFY, CANCEL, TRADE, CLEAR）
// - 計算 BBO (Best Bid and Offer) 最佳買賣價
// - 序列化 Order Book 狀態（用於日誌與除錯）
//
// 說明:
// MarketOrderBook 是 Trading Client 本地維護的 Order Book 快照（影子副本）
// 資料來源: Exchange 的 MarketDataPublisher/SnapshotSynthesizer 發送的更新
//
// 與 Chapter6 的 MEOrderBook 對比:
// - MEOrderBook:    Exchange 側的官方 Order Book（權威狀態）
// - MarketOrderBook: Trading Client 側的本地快照（重建狀態）
//
// ============================================================================

#include "market_order_book.h"

#include "trade_engine.h"

namespace Trading
{
// ============================================================================
// 建構函式
// ============================================================================
//
// 參數說明:
// - ticker_id: 商品代碼（例如 0 = ETH/USD）
// - logger:    日誌記錄器指標
//
// 初始化:
// - orders_at_price_pool_: 價格層級 (MarketOrdersAtPrice) 物件池
//   - 容量: ME_MAX_PRICE_LEVELS（預配置記憶體, 避免動態分配）
// - order_pool_: MarketOrder 物件池
//   - 容量: ME_MAX_ORDER_IDS（預配置記憶體）
//
// ⚡ 效能關鍵:
// - 使用 Memory Pool 避免 new/delete 的頻繁分配（參考 Chapter4 mem_pool.h）
// - 所有物件在建構時預分配, 交易時間只做 O(1) 的物件池分配/回收
//
MarketOrderBook::MarketOrderBook(TickerId ticker_id, Logger* logger)
    : ticker_id_(ticker_id), orders_at_price_pool_(ME_MAX_PRICE_LEVELS),
      order_pool_(ME_MAX_ORDER_IDS), logger_(logger)
{
}

// ============================================================================
// 解構函式
// ============================================================================
//
// 清理邏輯:
// 1. 記錄最終 Order Book 狀態（包含完整性檢查）
// 2. 清空指標參照（trade_engine_, bids_by_price_, asks_by_price_）
// 3. 清空訂單雜湊表 (oid_to_order_)
//
// ⚠️ 注意:
// - Memory Pool 物件 (orders_at_price_pool_, order_pool_) 由其解構函式自動清理
// - 不需要手動 deallocate(), Memory Pool 會在解構時一次性釋放所有記憶體
// - toString(false, true): false = 簡化輸出, true = 啟用完整性檢查（驗證價格排序）
//
MarketOrderBook::~MarketOrderBook()
{
    // 記錄最終 Order Book 狀態（用於事後分析）
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), toString(false, true));

    // 清空指標（避免野指標）
    trade_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;
    oid_to_order_.fill(nullptr); // 清空雜湊表
}

// ============================================================================
// 處理市場更新事件（核心方法）
// ============================================================================
//
// 參數:
// - market_update: 市場更新訊息（來自 Exchange 的 MarketDataPublisher）
//
// 支援的更新類型:
// 1. ADD:    新增訂單到 Order Book
// 2. MODIFY: 修改現有訂單數量
// 3. CANCEL: 取消訂單
// 4. TRADE:  成交事件（觸發 PositionKeeper 更新）
// 5. CLEAR:  清空整個 Order Book（例如交易日結束）
//
// 流程:
// 1. 判斷是否會影響 BBO (Best Bid and Offer)
//    - bid_updated: 買單且價格 >= 當前最佳買價
//    - ask_updated: 賣單且價格 <= 當前最佳賣價
// 2. 根據更新類型執行對應操作
// 3. 更新 BBO
// 4. 記錄日誌
// 5. 通知 TradeEngine 進行策略決策
//
// ⚡ 效能關鍵:
// - noexcept: 承諾不拋出異常, 避免異常處理開銷
// - 提前計算 bid_updated/ask_updated, 避免重複判斷
// - switch 語句編譯器優化為跳轉表 (Jump Table)
//
auto MarketOrderBook::onMarketUpdate(const Exchange::MEMarketUpdate*
                                     market_update) noexcept -> void
{
    // ⚡ 預先判斷是否影響 BBO（最佳買賣價）
    // - 買單: 價格 >= 當前最佳買價 → 可能成為新的最佳買價
    // - 賣單: 價格 <= 當前最佳賣價 → 可能成為新的最佳賣價
    const auto bid_updated = (bids_by_price_ && market_update->side_ == Side::BUY &&
                              market_update->price_ >= bids_by_price_->price_);
    const auto ask_updated = (asks_by_price_ &&
                              market_update->side_ == Side::SELL &&
                              market_update->price_ <= asks_by_price_->price_);

    switch (market_update->type_) {
    // ========================================================================
    // ADD: 新增訂單
    // ========================================================================
    // 流程:
    // 1. 從 order_pool_ 分配一個 MarketOrder 物件 (O(1) 記憶體池分配)
    // 2. 呼叫 addOrder() 將訂單插入 Order Book（在 header 中實作）
    //
    case Exchange::MarketUpdateType::ADD: {
            auto order = order_pool_.allocate(market_update->order_id_,
                                              market_update->side_, market_update->price_,
                                              market_update->qty_, market_update->priority_, nullptr, nullptr);
            addOrder(order); // 插入 Order Book（更新雜湊表與鏈結串列）
        }
        break;

    // ========================================================================
    // MODIFY: 修改訂單數量
    // ========================================================================
    // 流程:
    // 1. 從雜湊表 (oid_to_order_) 查找訂單 (O(1))
    // 2. 直接修改數量（不改變價格與優先權, 保持在原鏈結串列位置）
    //
    // ⚠️ 注意:
    // - 只修改數量, 不修改價格（修改價格需要先 CANCEL 再 ADD）
    //
    case Exchange::MarketUpdateType::MODIFY: {
            auto order = oid_to_order_.at(market_update->order_id_);
            order->qty_ = market_update->qty_; // 直接修改數量
        }
        break;

    // ========================================================================
    // CANCEL: 取消訂單
    // ========================================================================
    // 流程:
    // 1. 從雜湊表查找訂單 (O(1))
    // 2. 呼叫 removeOrder() 從 Order Book 移除（在 header 中實作）
    //    - 從雜湊表移除
    //    - 從雙向鏈結串列移除
    //    - 回收到 Memory Pool
    //
    case Exchange::MarketUpdateType::CANCEL: {
            auto order = oid_to_order_.at(market_update->order_id_);
            removeOrder(order); // 從 Order Book 移除並回收記憶體
        }
        break;

    // ========================================================================
    // TRADE: 成交事件
    // ========================================================================
    // 流程:
    // 1. 通知 TradeEngine 進行成交處理（更新 PositionKeeper）
    // 2. 直接 return, 不執行後續的 BBO 更新與日誌記錄
    //
    // ⚠️ 注意:
    // - TRADE 事件不改變 Order Book 狀態（成交後訂單自動移除）
    // - 使用 return 而非 break, 避免重複記錄日誌
    //
    case Exchange::MarketUpdateType::TRADE: {
            trade_engine_->onTradeUpdate(market_update, this);
            return; // 直接返回, 不執行 updateBBO() 與日誌記錄
        }
        break;

    // ========================================================================
    // CLEAR: 清空 Order Book
    // ========================================================================
    // 使用場景: 交易日結束、快照重建、異常恢復
    //
    // 流程:
    // 1. 回收所有 MarketOrder 物件到 order_pool_
    // 2. 回收所有 MarketOrdersAtPrice 物件到 orders_at_price_pool_
    // 3. 清空雜湊表與鏈結串列指標
    //
    // ⚡ 效能關鍵:
    // - 使用環狀鏈結串列遍歷（next_entry_ 回到起點時停止）
    // - Memory Pool 回收是 O(1) 操作（只更新 Free List）
    //
    case Exchange::MarketUpdateType::CLEAR: {
            // 1. 回收所有訂單物件
            for (auto& order : oid_to_order_) {
                if (order) {
                    order_pool_.deallocate(order); // O(1) 回收到 Memory Pool
                }
            }

            oid_to_order_.fill(nullptr); // 清空雜湊表

            // 2. 回收所有買單價格層級（環狀鏈結串列遍歷）
            if (bids_by_price_) {
                for (auto bid = bids_by_price_->next_entry_; bid != bids_by_price_;
                     bid = bid->next_entry_) {
                    orders_at_price_pool_.deallocate(bid);
                }

                orders_at_price_pool_.deallocate(bids_by_price_); // 回收頭節點
            }

            // 3. 回收所有賣單價格層級（環狀鏈結串列遍歷）
            if (asks_by_price_) {
                for (auto ask = asks_by_price_->next_entry_; ask != asks_by_price_;
                     ask = ask->next_entry_) {
                    orders_at_price_pool_.deallocate(ask);
                }

                orders_at_price_pool_.deallocate(asks_by_price_); // 回收頭節點
            }

            bids_by_price_ = asks_by_price_ = nullptr; // 清空指標
        }
        break;

    // ========================================================================
    // INVALID/SNAPSHOT_START/SNAPSHOT_END: 忽略的事件類型
    // ========================================================================
    // - INVALID:        非法事件（錯誤處理）
    // - SNAPSHOT_START: 快照開始標記（不需處理）
    // - SNAPSHOT_END:   快照結束標記（不需處理）
    //
    case Exchange::MarketUpdateType::INVALID:
    case Exchange::MarketUpdateType::SNAPSHOT_START:
    case Exchange::MarketUpdateType::SNAPSHOT_END:
        break;
    }

    // ⚡ 更新 BBO (Best Bid and Offer) 最佳買賣價
    // 只有在影響最佳買賣價的事件才需要重新計算
    updateBBO(bid_updated, ask_updated);

    // 記錄市場更新與當前 BBO 狀態
    logger_->log("%:% %() % % %", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), market_update->toString(),
                 bbo_.toString());

    // 通知 TradeEngine: Order Book 已更新, 可以進行策略決策
    trade_engine_->onOrderBookUpdate(market_update->ticker_id_,
                                     market_update->price_, market_update->side_, this);
}

// ============================================================================
// 序列化 Order Book 為字串（用於日誌與除錯）
// ============================================================================
//
// 參數:
// - detailed:       是否輸出詳細資訊（每個訂單的 ID、數量、鏈結串列指標）
// - validity_check: 是否執行完整性檢查（驗證價格排序是否正確）
//
// 輸出格式:
// Ticker: ETH/USD
// ASKS L:0 => <px:101.50 p:101.00 n:102.00> 101.50 @ 500(3) [oid:123 q:200 p:122 n:124] ...
// ASKS L:1 => <px:102.00 p:101.50 n:102.50> 102.00 @ 300(2) ...
//                           X
// BIDS L:0 => <px:100.50 p:101.00 n:100.00> 100.50 @ 600(4) ...
// BIDS L:1 => <px:100.00 p:100.50 n:99.50> 100.00 @ 400(2) ...
//
// 欄位說明:
// - L:N     → Level N (距離最佳價的層級)
// - px      → 當前價格
// - p       → prev 前一個價格層級
// - n       → next 下一個價格層級
// - qty(N)  → 總數量（N 個訂單）
//
// ⚠️ 效能考量:
// - 此函式使用 std::stringstream (動態記憶體分配)
// - 僅用於日誌與除錯, 不應在交易主迴圈（Hot Path）中呼叫
//
auto MarketOrderBook::toString(bool detailed,
                               bool validity_check) const -> std::string
{
    std::stringstream ss;
    std::string time_str;

    // Lambda 函式: 列印單一價格層級的所有訂單
    // 參數:
    // - itr:          當前價格層級 (MarketOrdersAtPrice*)
    // - side:         買/賣方向（用於排序驗證）
    // - last_price:   上一個價格（用於驗證價格排序）
    // - sanity_check: 是否檢查價格排序正確性
    auto printer = [&](std::stringstream & ss, MarketOrdersAtPrice * itr, Side side,
                       Price & last_price,
    bool sanity_check) {
        char buf[4096];
        Qty qty = 0;
        size_t num_orders = 0;

        // 第一輪遍歷: 統計總數量與訂單數（環狀鏈結串列）
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            qty += o_itr->qty_;
            ++num_orders;

            if (o_itr->next_order_ == itr->first_mkt_order_) { // 回到起點
                break;
            }
        }

        // 列印價格層級摘要: <價格 前一個 下一個> 價格 @ 數量(訂單數)
        sprintf(buf, " <px:%3s p:%3s n:%3s> %-3s @ %-5s(%-4s)",
                priceToString(itr->price_).c_str(),
                priceToString(itr->prev_entry_->price_).c_str(),
                priceToString(itr->next_entry_->price_).c_str(),
                priceToString(itr->price_).c_str(), qtyToString(qty).c_str(),
                std::to_string(num_orders).c_str());
        ss << buf;

        // 第二輪遍歷: 輸出詳細訂單資訊（如果啟用 detailed 模式）
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            if (detailed) {
                sprintf(buf, "[oid:%s q:%s p:%s n:%s] ",
                        orderIdToString(o_itr->order_id_).c_str(), qtyToString(o_itr->qty_).c_str(),
                        orderIdToString(o_itr->prev_order_ ? o_itr->prev_order_->order_id_ :
                                        OrderId_INVALID).c_str(),
                        orderIdToString(o_itr->next_order_ ? o_itr->next_order_->order_id_ :
                                        OrderId_INVALID).c_str());
                ss << buf;
            }

            if (o_itr->next_order_ == itr->first_mkt_order_) {
                break;
            }
        }

        ss << std::endl;

        // 完整性檢查: 驗證價格排序是否正確
        if (sanity_check) {
            // 賣單應遞增排序（101.00 < 101.50 < 102.00）
            // 買單應遞減排序（100.50 > 100.00 > 99.50）
            if ((side == Side::SELL && last_price >= itr->price_) || (side == Side::BUY &&
                    last_price <= itr->price_)) {
                FATAL("Bids/Asks not sorted by ascending/descending prices last:" +
                      priceToString(last_price) + " itr:" +
                      itr->toString());
            }

            last_price = itr->price_;
        }
    };

    // 輸出 Ticker 識別碼
    ss << "Ticker:" << tickerIdToString(ticker_id_) << std::endl;

    // 列印所有賣單層級（由低到高: 101.00, 101.50, 102.00, ...）
    {
        auto ask_itr = asks_by_price_;
        auto last_ask_price = std::numeric_limits<Price>::min();

        for (size_t count = 0; ask_itr; ++count) {
            ss << "ASKS L:" << count << " => ";
            auto next_ask_itr = (ask_itr->next_entry_ == asks_by_price_ ? nullptr :
                                 ask_itr->next_entry_); // 環狀串列結束檢查
            printer(ss, ask_itr, Side::SELL, last_ask_price, validity_check);
            ask_itr = next_ask_itr;
        }
    }

    ss << std::endl << "                          X" << std::endl << std::endl; // 買賣分隔線

    // 列印所有買單層級（由高到低: 100.50, 100.00, 99.50, ...）
    {
        auto bid_itr = bids_by_price_;
        auto last_bid_price = std::numeric_limits<Price>::max();

        for (size_t count = 0; bid_itr; ++count) {
            ss << "BIDS L:" << count << " => ";
            auto next_bid_itr = (bid_itr->next_entry_ == bids_by_price_ ? nullptr :
                                 bid_itr->next_entry_); // 環狀串列結束檢查
            printer(ss, bid_itr, Side::BUY, last_bid_price, validity_check);
            bid_itr = next_bid_itr;
        }
    }

    return ss.str();
}
} // namespace Trading
