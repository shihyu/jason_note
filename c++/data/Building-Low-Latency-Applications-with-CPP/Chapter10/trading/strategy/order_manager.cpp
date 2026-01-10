#include "order_manager.h"
#include "trade_engine.h"

namespace Trading
{
// ============================================================================
// newOrder() - 發送新訂單到交易所
// ============================================================================
//
// 📌 功能：創建並發送新訂單請求，更新本地訂單狀態
//
// 處理流程：
// 1. 建立訂單請求（MEClientRequest::NEW）
// 2. 透過 TradeEngine 發送到 OrderGateway
// 3. 更新本地訂單狀態為 PENDING_NEW
// 4. 遞增訂單 ID 生成器
// 5. 記錄日誌
//
// ⚡ 效能特性：
// - 零動態記憶體分配（結構初始化）
// - Lock-Free Queue 發送（不阻塞）
// - 延遲：< 100 ns
//
// 📊 訂單生命週期：
// INVALID → **PENDING_NEW** → LIVE → DEAD
//            ↑ 此函式設定
//
// ⚠️ 注意事項：
// - 呼叫前應已通過風控檢查（RiskManager::checkPreTradeRisk）
// - 訂單 ID 自動遞增，保證唯一性
// - PENDING_NEW 表示等待交易所 ACCEPTED 回報
//
// @param order: 訂單物件指標（將被更新）
// @param ticker_id: 交易標的 ID
// @param price: 訂單價格
// @param side: 買賣方向
// @param qty: 訂單數量
auto OrderManager::newOrder(OMOrder* order, TickerId ticker_id, Price price,
                            Side side, Qty qty) noexcept -> void
{
    // 1. 建立新訂單請求（結構初始化）
    const Exchange::MEClientRequest new_request{Exchange::ClientRequestType::NEW, trade_engine_->clientId(), ticker_id,
            next_order_id_, side, price, qty};

    // 2. 發送請求到交易所（Lock-Free Queue）
    trade_engine_->sendClientRequest(&new_request);

    // 3. 更新本地訂單狀態
    *order = {ticker_id, next_order_id_, side, price, qty, OMOrderState::PENDING_NEW};

    // 4. 遞增訂單 ID 生成器
    ++next_order_id_;

    // 5. 記錄日誌（用於除錯和審計）
    logger_->log("%:% %() % Sent new order % for %\n", __FILE__, __LINE__,
                 __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 new_request.toString().c_str(), order->toString().c_str());
}

// ============================================================================
// cancelOrder() - 取消訂單
// ============================================================================
//
// 📌 功能：發送取消訂單請求，更新本地訂單狀態
//
// 處理流程：
// 1. 建立取消請求（MEClientRequest::CANCEL）
// 2. 透過 TradeEngine 發送到 OrderGateway
// 3. 更新本地訂單狀態為 PENDING_CANCEL
// 4. 記錄日誌
//
// ⚡ 效能特性：
// - 零動態記憶體分配
// - Lock-Free Queue 發送（不阻塞）
// - 延遲：< 100 ns
//
// 📊 訂單生命週期：
// LIVE → **PENDING_CANCEL** → DEAD
//         ↑ 此函式設定
//
// ⚠️ 重要考量：
// - 取消不保證成功（訂單可能已成交）
// - PENDING_CANCEL 狀態防止重複取消
// - 需等待 CANCELED 或 CANCEL_REJECTED 回報
//
// 📊 使用場景：
// 1. Market Maker 調整報價（取消舊單 + 發新單）
// 2. 風控觸發（倉位超限）
// 3. 市場狀況改變（波動過大）
// 4. 交易時段結束前清倉
//
// @param order: 要取消的訂單物件指標
auto OrderManager::cancelOrder(OMOrder* order) noexcept -> void
{
    // 1. 建立取消請求（包含原訂單的所有資訊）
    const Exchange::MEClientRequest cancel_request{Exchange::ClientRequestType::CANCEL, trade_engine_->clientId(),
            order->ticker_id_, order->order_id_, order->side_, order->price_,
            order->qty_};

    // 2. 發送取消請求到交易所
    trade_engine_->sendClientRequest(&cancel_request);

    // 3. 更新訂單狀態為 PENDING_CANCEL（等待交易所確認）
    order->order_state_ = OMOrderState::PENDING_CANCEL;

    // 4. 記錄日誌
    logger_->log("%:% %() % Sent cancel % for %\n", __FILE__, __LINE__,
                 __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 cancel_request.toString().c_str(), order->toString().c_str());
}
}
