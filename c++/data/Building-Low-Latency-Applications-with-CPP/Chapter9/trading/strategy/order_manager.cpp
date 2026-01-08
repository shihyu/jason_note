#include "order_manager.h"
#include "trade_engine.h"

namespace Trading
{
/**
 * newOrder() - 發送新訂單到交易所
 *
 * @param order 訂單物件指標（將被更新為新訂單狀態）
 * @param ticker_id 商品識別碼
 * @param price 訂單價格
 * @param side 買賣方向（BUY/SELL）
 * @param qty 訂單數量
 *
 * 職責：
 * 1. 建立新訂單請求（MEClientRequest）
 * 2. 通過 TradeEngine 發送到訂單閘道
 * 3. 更新本地訂單狀態為 PENDING_NEW
 * 4. 遞增訂單 ID 生成器
 *
 * 訂單生命週期：
 * INVALID → **PENDING_NEW** → LIVE/DEAD
 *            ↑ 此函式設定
 *
 * 效能特性：
 * - 無動態記憶體分配（訂單物件預先分配）
 * - 直接結構初始化（MEClientRequest）
 * - Lock-Free Queue 發送（sendClientRequest 不阻塞）
 * - 延遲：< 100 ns（建構請求 + 寫入佇列）
 *
 * 注意事項：
 * - 呼叫前應已通過風控檢查（checkPreTradeRisk）
 * - 訂單 ID 自動遞增，保證唯一性
 * - PENDING_NEW 狀態表示等待交易所 ACCEPTED 回報
 *
 * 典型流程：
 * 1. 策略決定發單（例如 Market Maker 報價）
 * 2. 通過風控檢查（RiskManager::checkPreTradeRisk）
 * 3. 呼叫此函式發送訂單
 * 4. 等待 onOrderUpdate() 處理 ACCEPTED 回報
 * 5. 訂單狀態轉為 LIVE
 */
auto OrderManager::newOrder(OMOrder* order, TickerId ticker_id, Price price,
                            Side side, Qty qty) noexcept -> void
{
    // 1. 建立新訂單請求（結構初始化）
    const Exchange::MEClientRequest new_request{
        Exchange::ClientRequestType::NEW,    // 請求類型：NEW
        trade_engine_->clientId(),          // 客戶端識別碼
        ticker_id,                          // 商品 ID
        next_order_id_,                     // 訂單 ID（唯一）
        side,                               // 買賣方向
        price,                              // 價格
        qty                                 // 數量
    };

    // 2. 發送請求到交易所（通過 TradeEngine → OrderGateway → TCP）
    trade_engine_->sendClientRequest(&new_request);

    // 3. 更新本地訂單狀態（結構初始化，覆蓋舊值）
    *order = {
        ticker_id,                   // 商品 ID
        next_order_id_,              // 訂單 ID
        side,                        // 買賣方向
        price,                       // 價格
        qty,                         // 數量
        OMOrderState::PENDING_NEW    // 狀態：等待交易所接受
    };

    // 4. 遞增訂單 ID 生成器（下次發單使用新 ID）
    ++next_order_id_;

    // 5. 記錄日誌（用於除錯和審計）
    logger_->log("%:% %() % Sent new order % for %\n", __FILE__, __LINE__,
                 __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 new_request.toString().c_str(), order->toString().c_str());
}

/**
 * cancelOrder() - 取消訂單
 *
 * @param order 要取消的訂單物件指標
 *
 * 職責：
 * 1. 建立取消訂單請求（MEClientRequest::CANCEL）
 * 2. 通過 TradeEngine 發送到訂單閘道
 * 3. 更新本地訂單狀態為 PENDING_CANCEL
 *
 * 訂單生命週期：
 * LIVE → **PENDING_CANCEL** → DEAD
 *         ↑ 此函式設定
 *
 * 效能特性：
 * - 無動態記憶體分配
 * - Lock-Free Queue 發送（不阻塞）
 * - 延遲：< 100 ns
 *
 * 重要考量：
 * - 取消不保證成功（可能已成交、訂單不存在）
 * - PENDING_CANCEL 狀態防止重複取消
 * - 需等待 onOrderUpdate() 處理 CANCELED 或 CANCEL_REJECTED 回報
 *
 * 典型使用場景：
 * 1. Market Maker 策略調整報價（取消舊單 + 發新單）
 * 2. 風控觸發（超過倉位限制）
 * 3. 市場狀況改變（波動過大）
 * 4. 交易時段結束前清倉
 *
 * 錯誤處理：
 * - 若取消被拒絕（CANCEL_REJECTED）：
 *   - 訂單可能已全部成交
 *   - 訂單 ID 不存在
 *   - onOrderUpdate() 會記錄日誌，但不改變狀態
 *
 * 注意事項：
 * - 取消請求使用原訂單的所有欄位（ticker_id, order_id, side, price, qty）
 * - 交易所通過 order_id 識別要取消的訂單
 * - PENDING_CANCEL 狀態表示等待交易所 CANCELED 回報
 */
auto OrderManager::cancelOrder(OMOrder* order) noexcept -> void
{
    // 1. 建立取消請求（包含原訂單的所有資訊）
    const Exchange::MEClientRequest cancel_request{
        Exchange::ClientRequestType::CANCEL,  // 請求類型：CANCEL
        trade_engine_->clientId(),           // 客戶端識別碼
        order->ticker_id_,                   // 商品 ID
        order->order_id_,                    // 訂單 ID（交易所用此識別訂單）
        order->side_,                        // 買賣方向
        order->price_,                       // 原價格
        order->qty_                          // 原數量
    };

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
