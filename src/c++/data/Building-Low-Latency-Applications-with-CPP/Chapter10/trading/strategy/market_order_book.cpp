#include "market_order_book.h"

#include "trade_engine.h"

namespace Trading
{
// ============================================================================
// MarketOrderBook 建構子
// ============================================================================
//
// 📌 功能：初始化交易客戶端的本地訂單簿副本
//
// 初始化流程：
// 1. 儲存交易標的 ID（ticker_id_）
// 2. 創建價位記憶體池（orders_at_price_pool_）
// 3. 創建訂單記憶體池（order_pool_）
// 4. 關聯日誌記錄器
//
// ⚡ 效能設計：
// - Memory Pool：預先分配記憶體，避免 malloc/free
// - ME_MAX_PRICE_LEVELS：最大價位數量（編譯期常數）
// - ME_MAX_ORDER_IDS：最大訂單數量（編譯期常數）
//
// 📊 記憶體預算：
// - MarketOrdersAtPrice：~40 bytes × ME_MAX_PRICE_LEVELS
// - MarketOrder：~64 bytes × ME_MAX_ORDER_IDS
// - 總計：假設 ME_MAX_PRICE_LEVELS=1024, ME_MAX_ORDER_IDS=65536
//   則約 40KB + 4MB = 4.04MB per ticker
//
// ⚠️ 注意：
// - 訂單簿初始狀態為空（bids_by_price_/asks_by_price_ = nullptr）
// - 收到 MarketUpdate 後才開始填充資料
// - Memory Pool 不會自動擴容（固定大小）
//
// @param ticker_id: 交易標的 ID
// @param logger: 日誌記錄器指標
MarketOrderBook::MarketOrderBook(TickerId ticker_id, Logger* logger)
    : ticker_id_(ticker_id), orders_at_price_pool_(ME_MAX_PRICE_LEVELS),
      order_pool_(ME_MAX_ORDER_IDS), logger_(logger)
{
}

// ============================================================================
// MarketOrderBook 解構子
// ============================================================================
//
// 📌 功能：清理訂單簿資源並記錄最終狀態
//
// 清理流程：
// 1. 記錄完整訂單簿快照（用於除錯與審計）
// 2. 清空 TradeEngine 指標（不負責釋放）
// 3. 清空買賣價位鏈結串列頭指標
// 4. 清空訂單 ID 對照表
//
// ⚡ 記憶體管理：
// - Memory Pool 會自動釋放所有物件（在 Pool 解構子中）
// - 此處只需清空指標，無需手動 delete
//
// 📊 日誌輸出：
// - toString(false, true)：不顯示詳細訂單，但執行完整性檢查
// - 用於驗證訂單簿在關閉前是否一致
//
// ⚠️ 注意：
// - 生產環境應確保訂單簿已清空（所有訂單已取消或成交）
// - 如果殘留訂單，可能表示系統異常關閉
//
// @note 解構子不會拋出異常（noexcept 隱式保證）
MarketOrderBook::~MarketOrderBook()
{
    // 記錄最終訂單簿狀態（除錯與審計）
    logger_->log("%:% %() % OrderBook\n%\n", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), toString(false, true));

    // 清空指標（不負責釋放，由外部管理）
    trade_engine_ = nullptr;
    bids_by_price_ = asks_by_price_ = nullptr;

    // 清空訂單 ID 對照表
    oid_to_order_.fill(nullptr);
}

// ============================================================================
// onMarketUpdate() - 處理市場數據更新，維護本地訂單簿副本
// ============================================================================
//
// 📌 功能：根據交易所推送的市場數據更新本地訂單簿
//
// 支援的更新類型：
// 1. ADD：新訂單加入訂單簿
// 2. MODIFY：訂單數量變動（部分成交）
// 3. CANCEL：訂單被取消或完全成交
// 4. TRADE：成交事件（不更新訂單簿，轉發給 TradeEngine）
// 5. CLEAR：清空訂單簿（收盤、系統重啟）
// 6. SNAPSHOT_START/END：快照界定（忽略）
//
// ⚡ 效能關鍵：
// - 熱路徑：ADD/MODIFY/CANCEL（高頻率）
// - 冷路徑：CLEAR/SNAPSHOT（低頻率）
// - 延遲目標：< 100 ns per update
//
// 📊 BBO 更新邏輯：
// - bid_updated：買單價格 >= 當前最佳買價 → BBO 可能改變
// - ask_updated：賣單價格 <= 當前最佳賣價 → BBO 可能改變
// - 只在影響 BBO 時通知 TradeEngine（減少不必要的回調）
//
// ⚠️ 注意：
// - 假設市場數據按序到達（無亂序問題）
// - 假設 order_id 唯一且不重複
// - Memory Pool 必須有足夠容量（否則 allocate 會失敗）
//
// @param market_update: 市場數據更新事件指標
auto MarketOrderBook::onMarketUpdate(const Exchange::MEMarketUpdate*
                                     market_update) noexcept -> void
{
    // 前置檢查：判斷此次更新是否可能影響 BBO（Best Bid/Offer）
    // ⚡ 優化：提前計算，避免在 switch 後重複判斷
    const auto bid_updated = (bids_by_price_ && market_update->side_ == Side::BUY &&
                              market_update->price_ >= bids_by_price_->price_);
    const auto ask_updated = (asks_by_price_ &&
                              market_update->side_ == Side::SELL &&
                              market_update->price_ <= asks_by_price_->price_);

    switch (market_update->type_) {
    // ========== ADD：新訂單加入訂單簿 ==========
    case Exchange::MarketUpdateType::ADD: {
            // 1. 從 Memory Pool 分配訂單物件（O(1) 分配）
            // ⚡ 零動態記憶體分配：使用預分配的 Pool
            auto order = order_pool_.allocate(market_update->order_id_,
                                              market_update->side_, market_update->price_,
                                              market_update->qty_, market_update->priority_, nullptr, nullptr);
            // 2. 將訂單加入訂單簿（維護價位鏈結串列）
            addOrder(order);
        }
        break;

    // ========== MODIFY：訂單數量變動（部分成交） ==========
    case Exchange::MarketUpdateType::MODIFY: {
            // 📌 快速查找：透過 order_id 直接定位訂單（O(1)）
            auto order = oid_to_order_.at(market_update->order_id_);
            // 更新剩餘數量（leaves quantity）
            order->qty_ = market_update->qty_;
            // ⚠️ 注意：價格與優先權不變，訂單位置不移動
        }
        break;

    // ========== CANCEL：訂單被取消或完全成交 ==========
    case Exchange::MarketUpdateType::CANCEL: {
            // 1. 快速查找訂單
            auto order = oid_to_order_.at(market_update->order_id_);
            // 2. 從訂單簿移除（維護鏈結串列完整性）
            removeOrder(order);
            // ⚡ Memory Pool 會回收訂單物件（在 removeOrder 中）
        }
        break;

    // ========== TRADE：成交事件 ==========
    case Exchange::MarketUpdateType::TRADE: {
            // 📌 設計決策：成交事件不更新訂單簿
            // 原因：
            // 1. 成交後會收到 MODIFY/CANCEL 更新訂單狀態
            // 2. TRADE 事件用於策略層判斷趨勢
            // 3. 避免重複處理（訂單簿已透過 MODIFY/CANCEL 更新）
            //
            // 轉發給 TradeEngine（通知策略層）
            trade_engine_->onTradeUpdate(market_update, this);
            return;  // ⚠️ 提前返回：不執行 updateBBO()
        }
        break;

    // ========== CLEAR：清空訂單簿 ==========
    case Exchange::MarketUpdateType::CLEAR:
        {
            // 📌 使用場景：
            // 1. 交易日結束（收盤清倉）
            // 2. 系統重啟（重建訂單簿）
            // 3. 異常恢復（丟包過多，需要重新訂閱快照）
            //
            // 清空流程（三階段）：
            //
            // 階段 1：釋放所有訂單物件
            // ⚡ 遍歷訂單 ID 對照表，回收所有訂單到 Pool
            for (auto& order : oid_to_order_) {
                if (order) {
                    order_pool_.deallocate(order);
                }
            }
            oid_to_order_.fill(nullptr);

            // 階段 2：釋放買單價位鏈結串列
            // 🔗 環狀鏈結串列遍歷：從頭節點走到尾節點
            if (bids_by_price_) {
                for (auto bid = bids_by_price_->next_entry_; bid != bids_by_price_;
                     bid = bid->next_entry_) {
                    orders_at_price_pool_.deallocate(bid);
                }
                // 釋放頭節點
                orders_at_price_pool_.deallocate(bids_by_price_);
            }

            // 階段 3：釋放賣單價位鏈結串列
            if (asks_by_price_) {
                for (auto ask = asks_by_price_->next_entry_; ask != asks_by_price_;
                     ask = ask->next_entry_) {
                    orders_at_price_pool_.deallocate(ask);
                }
                // 釋放頭節點
                orders_at_price_pool_.deallocate(asks_by_price_);
            }

            // 重置鏈結串列頭指標
            bids_by_price_ = asks_by_price_ = nullptr;
        }
        break;

    // ========== 忽略的事件類型 ==========
    case Exchange::MarketUpdateType::INVALID:
        // 無效事件：協議錯誤或未初始化
        break;
    case Exchange::MarketUpdateType::SNAPSHOT_START:
    case Exchange::MarketUpdateType::SNAPSHOT_END:
        // 快照界定事件：標記快照開始/結束，不含實際數據
        // 用途：客戶端可根據這些事件重建訂單簿狀態
        break;
    }

    // 更新 BBO（Best Bid/Offer）
    // ⚡ 只在 BBO 可能改變時通知策略層（減少回調頻率）
    updateBBO(bid_updated, ask_updated);

    // 記錄市場數據更新日誌
    logger_->log("%:% %() % % %", __FILE__, __LINE__, __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_), market_update->toString(),
                 bbo_.toString());

    // 通知 TradeEngine（觸發訂單簿更新回調）
    // 📌 策略層會收到此通知並決定是否調整報價
    trade_engine_->onOrderBookUpdate(market_update->ticker_id_,
                                     market_update->price_, market_update->side_, this);
}

// ============================================================================
// toString() - 訂單簿序列化為字串（除錯與日誌）
// ============================================================================
//
// 📌 功能：將完整訂單簿狀態轉換為人類可讀格式
//
// @param detailed: 是否顯示詳細訂單資訊（order_id, qty, prev, next）
// @param validity_check: 是否執行完整性檢查（價格排序）
//
// ⚠️ 效能警告：
// - 執行時間：O(N)，N = 訂單總數（可能數千筆）
// - 記憶體分配：stringstream 動態分配（數 KB 到數 MB）
// - **絕對不可在熱路徑中呼叫！**
// - 僅限除錯、日誌記錄、測試場景使用
//
// 📊 輸出格式：
// ```
// Ticker:AAPL
// ASKS L:0 => <px:100.05 p:100.10 n:100.00> 100.05 @ 500 (2)
// ASKS L:1 => <px:100.10 p:100.15 n:100.05> 100.10 @ 300 (1)
//                          X
// BIDS L:0 => <px:100.00 p:99.95 n:100.05> 100.00 @ 600 (3)
// BIDS L:1 => <px:99.95 p:99.90 n:100.00> 99.95 @ 400 (2)
// ```
//
// 欄位說明：
// - px: 當前價位
// - p: 前一個價位（prev_entry_）
// - n: 下一個價位（next_entry_）
// - 數量 @ 價位（訂單數量）
// - X: 價差分隔線（Bid-Ask Spread）
//
// @return 完整訂單簿的字串表示
auto MarketOrderBook::toString(bool detailed,
                               bool validity_check) const -> std::string
{
    std::stringstream ss;
    std::string time_str;

    // 📌 Lambda 函式：列印單一價位的所有訂單
    // 📊 功能：
    // 1. 統計該價位的總數量與訂單數
    // 2. （可選）列印每筆訂單的詳細資訊
    // 3. （可選）檢查價格排序完整性
    auto printer = [&](std::stringstream & ss, MarketOrdersAtPrice * itr, Side side,
                       Price & last_price,
    bool sanity_check) {
        char buf[4096];
        Qty qty = 0;
        size_t num_orders = 0;

        // 第一次遍歷：統計總數量與訂單數
        // 🔗 環狀鏈結串列：從頭節點遍歷，直到回到頭節點
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            qty += o_itr->qty_;
            ++num_orders;

            // 環狀鏈結串列終止條件：next_order_ 指回頭節點
            if (o_itr->next_order_ == itr->first_mkt_order_) {
                break;
            }
        }

        // 輸出價位彙總資訊
        // 格式：<px:當前價 p:前一價 n:下一價> 價位 @ 總量(訂單數)
        sprintf(buf, " <px:%3s p:%3s n:%3s> %-3s @ %-5s(%-4s)",
                priceToString(itr->price_).c_str(),
                priceToString(itr->prev_entry_->price_).c_str(),
                priceToString(itr->next_entry_->price_).c_str(),
                priceToString(itr->price_).c_str(), qtyToString(qty).c_str(),
                std::to_string(num_orders).c_str());
        ss << buf;

        // 第二次遍歷：（可選）輸出詳細訂單資訊
        for (auto o_itr = itr->first_mkt_order_;; o_itr = o_itr->next_order_) {
            if (detailed) {
                // 格式：[oid:訂單ID q:數量 p:前一訂單 n:下一訂單]
                sprintf(buf, "[oid:%s q:%s p:%s n:%s] ",
                        orderIdToString(o_itr->order_id_).c_str(), qtyToString(o_itr->qty_).c_str(),
                        orderIdToString(o_itr->prev_order_ ? o_itr->prev_order_->order_id_ :
                                        OrderId_INVALID).c_str(),
                        orderIdToString(o_itr->next_order_ ? o_itr->next_order_->order_id_ :
                                        OrderId_INVALID).c_str());
                ss << buf;
            }

            // 環狀鏈結串列終止條件
            if (o_itr->next_order_ == itr->first_mkt_order_) {
                break;
            }
        }

        ss << std::endl;

        // （可選）完整性檢查：驗證價格排序
        if (sanity_check) {
            // 賣單：價格應遞增（低 → 高）
            // 買單：價格應遞減（高 → 低）
            if ((side == Side::SELL && last_price >= itr->price_) || (side == Side::BUY &&
                    last_price <= itr->price_)) {
                FATAL("Bids/Asks not sorted by ascending/descending prices last:" +
                      priceToString(last_price) + " itr:" +
                      itr->toString());
            }

            last_price = itr->price_;
        }
    };

    // 輸出交易標的名稱
    ss << "Ticker:" << tickerIdToString(ticker_id_) << std::endl;

    // ========== 輸出賣單（ASKS）==========
    // 📌 價格排序：低到高（遞增）
    {
        auto ask_itr = asks_by_price_;
        auto last_ask_price = std::numeric_limits<Price>::min();

        for (size_t count = 0; ask_itr; ++count) {
            ss << "ASKS L:" << count << " => ";
            // 檢查是否為環狀鏈結串列的尾節點
            auto next_ask_itr = (ask_itr->next_entry_ == asks_by_price_ ? nullptr :
                                 ask_itr->next_entry_);
            // 列印該價位的所有訂單
            printer(ss, ask_itr, Side::SELL, last_ask_price, validity_check);
            ask_itr = next_ask_itr;
        }
    }

    // 輸出價差分隔線（Bid-Ask Spread）
    ss << std::endl << "                          X" << std::endl << std::endl;

    // ========== 輸出買單（BIDS）==========
    // 📌 價格排序：高到低（遞減）
    {
        auto bid_itr = bids_by_price_;
        auto last_bid_price = std::numeric_limits<Price>::max();

        for (size_t count = 0; bid_itr; ++count) {
            ss << "BIDS L:" << count << " => ";
            // 檢查是否為環狀鏈結串列的尾節點
            auto next_bid_itr = (bid_itr->next_entry_ == bids_by_price_ ? nullptr :
                                 bid_itr->next_entry_);
            // 列印該價位的所有訂單
            printer(ss, bid_itr, Side::BUY, last_bid_price, validity_check);
            bid_itr = next_bid_itr;
        }
    }

    return ss.str();
}
}
