/**
 * @file order_manager.cpp
 * @brief 訂單管理器實作檔案 - 訂單生命週期管理核心邏輯
 *
 * 功能：
 * - 實作 newOrder() 和 cancelOrder() 方法
 * - 處理訂單發送到交易所的完整流程
 * - 更新本地訂單狀態並記錄日誌
 *
 * 實作細節：
 * - newOrder()：建構 MEClientRequest（NEW 類型）並發送到 TradeEngine
 * - cancelOrder()：建構 MEClientRequest（CANCEL 類型）並發送到 TradeEngine
 * - 所有操作都同步更新本地訂單狀態
 * - 日誌記錄請求和訂單資訊（用於審計和除錯）
 *
 * 設計考量：
 * - 非同步設計：發送請求後立即返回，不等待交易所回報
 * - 狀態追蹤：本地維護 PENDING_NEW/PENDING_CANCEL 狀態
 * - 錯誤處理：假設 TradeEngine 會處理所有通訊錯誤
 *
 * 效能特性：
 * - 所有方法標記 noexcept（無例外拋出）
 * - 時間複雜度：O(1)（建構請求並發送）
 * - 日誌記錄使用預分配緩衝區（time_str_）
 */

#include "order_manager.h"
#include "trade_engine.h"

namespace Trading
{
/**
 * newOrder() - 發送新訂單到交易所
 *
 * 實作流程：
 * 1. 建構 MEClientRequest（NEW 類型）
 *    - 設定客戶端 ID（trade_engine_->clientId()）
 *    - 設定商品 ID、價格、方向、數量
 *    - 使用當前 next_order_id_ 作為訂單 ID
 *
 * 2. 發送請求到 TradeEngine
 *    - trade_engine_->sendClientRequest(&new_request)
 *    - TradeEngine 會將請求發送到 OrderGateway
 *
 * 3. 更新本地訂單狀態
 *    - 設定訂單物件所有欄位
 *    - 狀態設為 PENDING_NEW
 *    - 遞增 next_order_id_
 *
 * 4. 記錄日誌
 *    - 輸出請求內容和訂單資訊
 *
 * 注意事項：
 * - 呼叫前必須確保風控檢查通過
 * - 訂單 ID 單調遞增，保證唯一性
 * - 不等待交易所回報（非同步操作）
 *
 * @see OrderManager::onOrderUpdate() 處理 ACCEPTED 回報
 */
auto OrderManager::newOrder(OMOrder* order, TickerId ticker_id, Price price,
                            Side side, Qty qty) noexcept -> void
{
    // 1. 建構新訂單請求
    const Exchange::MEClientRequest new_request{Exchange::ClientRequestType::NEW, trade_engine_->clientId(), ticker_id,
            next_order_id_, side, price, qty};

    // 2. 發送請求到交易引擎
    trade_engine_->sendClientRequest(&new_request);

    // 3. 更新本地訂單狀態為 PENDING_NEW
    *order = {ticker_id, next_order_id_, side, price, qty, OMOrderState::PENDING_NEW};
    ++next_order_id_;  // 遞增訂單 ID 生成器

    // 4. 記錄日誌（請求和訂單資訊）
    logger_->log("%:% %() % Sent new order % for %\n", __FILE__, __LINE__,
                 __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 new_request.toString().c_str(), order->toString().c_str());
}

/**
 * cancelOrder() - 發送撤單請求到交易所
 *
 * 實作流程：
 * 1. 建構 MEClientRequest（CANCEL 類型）
 *    - 使用現有訂單的所有欄位
 *    - 包含 ticker_id、order_id、side、price、qty
 *
 * 2. 發送請求到 TradeEngine
 *    - trade_engine_->sendClientRequest(&cancel_request)
 *    - TradeEngine 會將請求發送到 OrderGateway
 *
 * 3. 更新本地訂單狀態
 *    - 狀態設為 PENDING_CANCEL
 *
 * 4. 記錄日誌
 *    - 輸出請求內容和訂單資訊
 *
 * 注意事項：
 * - 只能撤銷狀態為 LIVE 的訂單
 * - 撤單可能被交易所拒絕（CANCEL_REJECTED）
 * - 已成交的訂單無法撤銷
 * - 不等待交易所回報（非同步操作）
 *
 * @see OrderManager::onOrderUpdate() 處理 CANCELED 回報
 */
auto OrderManager::cancelOrder(OMOrder* order) noexcept -> void
{
    // 1. 建構撤單請求（使用訂單的所有欄位）
    const Exchange::MEClientRequest cancel_request{Exchange::ClientRequestType::CANCEL, trade_engine_->clientId(),
            order->ticker_id_, order->order_id_, order->side_, order->price_,
            order->qty_};

    // 2. 發送請求到交易引擎
    trade_engine_->sendClientRequest(&cancel_request);

    // 3. 更新本地訂單狀態為 PENDING_CANCEL
    order->order_state_ = OMOrderState::PENDING_CANCEL;

    // 4. 記錄日誌（請求和訂單資訊）
    logger_->log("%:% %() % Sent cancel % for %\n", __FILE__, __LINE__,
                 __FUNCTION__,
                 Common::getCurrentTimeStr(&time_str_),
                 cancel_request.toString().c_str(), order->toString().c_str());
}
}
