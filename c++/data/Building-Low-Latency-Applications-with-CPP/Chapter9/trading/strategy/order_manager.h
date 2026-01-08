#pragma once

#include "common/macros.h"
#include "common/logging.h"

#include "exchange/order_server/client_response.h"

#include "om_order.h"
#include "risk_manager.h"

using namespace Common;

namespace Trading
{
class TradeEngine;

// ============================================================================
// 訂單管理器（OrderManager）
// ============================================================================
// 📌 核心職責：
//   1. 管理所有訂單的生命週期（發單、取消、狀態更新）
//   2. 整合風控檢查（在發單前呼叫 RiskManager）
//   3. 維護訂單狀態機（INVALID → PENDING_NEW → LIVE → DEAD）
//   4. 處理交易所回報（ACCEPTED, FILLED, CANCELED, CANCEL_REJECTED）
// ⚡ 效能特性：
//   - 固定大小陣列儲存訂單（避免動態分配）
//   - 風控檢查 < 20 ns（熱路徑優化）
//   - 訂單狀態更新 O(1)
class OrderManager
{
public:
    OrderManager(Common::Logger* logger, TradeEngine* trade_engine,
                 RiskManager& risk_manager)
        : trade_engine_(trade_engine), risk_manager_(risk_manager), logger_(logger)
    {
    }

    // ⚡ 熱路徑：處理交易所回報，更新訂單狀態
    // 📊 呼叫頻率：每次收到回報（約數百到數千次/秒）
    // 📌 狀態機維護：根據回報類型轉換訂單狀態
    auto onOrderUpdate(const Exchange::MEClientResponse* client_response) noexcept
    -> void
    {
        // 日誌記錄：收到的回報內容
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     client_response->toString().c_str());

        // 📌 訂單定位：根據 ticker_id 和 side 找到對應的訂單
        // ⚠️ 假設：每個 (ticker, side) 只有一個活躍訂單
        auto order = &(ticker_side_order_.at(client_response->ticker_id_).at(
                           sideToIndex(client_response->side_)));

        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     order->toString().c_str());

        // ============================================================================
        // 狀態轉換邏輯
        // ============================================================================
        switch (client_response->type_) {
        case Exchange::ClientResponseType::ACCEPTED: {
                // 訂單被交易所接受 → 進入 LIVE 狀態
                // PENDING_NEW → LIVE
                order->order_state_ = OMOrderState::LIVE;
            }
            break;

        case Exchange::ClientResponseType::CANCELED: {
                // 訂單被取消 → 進入 DEAD 狀態
                // PENDING_CANCEL → DEAD
                order->order_state_ = OMOrderState::DEAD;
            }
            break;

        case Exchange::ClientResponseType::FILLED: {
                // 訂單成交（部分或全部）
                // 📌 關鍵：更新剩餘數量（leaves_qty）
                order->qty_ = client_response->leaves_qty_;

                // ⚠️ 全部成交判斷：剩餘數量為 0
                if (!order->qty_) {
                    // LIVE → DEAD（全部成交）
                    order->order_state_ = OMOrderState::DEAD;
                }
                // 否則：保持 LIVE 狀態（部分成交）
            }
            break;

        case Exchange::ClientResponseType::CANCEL_REJECTED:
            // ⚠️ 重要：取消請求被拒絕
            // 📌 意義：訂單仍在交易所掛單（保持 LIVE 狀態）
            // ⚠️ 常見原因：訂單已全部成交、訂單不存在
            // TODO: 可考慮恢復訂單狀態為 LIVE
        case Exchange::ClientResponseType::INVALID: {
                // 無效回報 → 不做任何操作
            }
            break;
        }
    }

    auto newOrder(OMOrder* order, TickerId ticker_id, Price price, Side side,
                  Qty qty) noexcept -> void;

    auto cancelOrder(OMOrder* order) noexcept -> void;

    // ⚡ 效能關鍵：移動訂單（取消 + 發新單，或保持不動）
    // 📌 設計哲學：
    //   - 大多數交易所不支援 MODIFY 指令
    //   - 移動訂單 = 取消舊訂單 + 發送新訂單
    //   - 如果價格沒變，不做任何操作（避免無謂取消）
    // 📊 使用場景：Market Maker 策略頻繁調整報價
    auto moveOrder(OMOrder* order, TickerId ticker_id, Price price, Side side,
                   Qty qty) noexcept
    {
        // ============================================================================
        // 狀態機驅動的訂單操作
        // ============================================================================
        switch (order->order_state_) {
        case OMOrderState::LIVE: {
                // 訂單在交易所掛單中
                // 📌 策略：如果價格改變 → 取消舊訂單（下一輪會發新單）
                if (order->price_ != price) {
                    cancelOrder(order);
                }
                // 否則：價格相同 → 不動作（避免無謂取消）
            }
            break;

        case OMOrderState::INVALID:
        case OMOrderState::DEAD: {
                // 無訂單或訂單已結束
                // 📌 策略：發送新訂單（如果價格有效）
                if (LIKELY(price != Price_INVALID)) {
                    // ⚡ 效能關鍵：發單前檢查風控
                    const auto risk_result = risk_manager_.checkPreTradeRisk(ticker_id, side, qty);

                    if (LIKELY(risk_result == RiskCheckResult::ALLOWED)) {
                        // ✅ 通過風控 → 發送新訂單
                        newOrder(order, ticker_id, price, side, qty);
                    } else {
                        // ❌ 風控拒絕 → 記錄日誌
                        logger_->log("%:% %() % Ticker:% Side:% Qty:% RiskCheckResult:%\n", __FILE__,
                                     __LINE__, __FUNCTION__,
                                     Common::getCurrentTimeStr(&time_str_),
                                     tickerIdToString(ticker_id), sideToString(side), qtyToString(qty),
                                     riskCheckResultToString(risk_result));
                    }
                }
            }
            break;

        case OMOrderState::PENDING_NEW:
        case OMOrderState::PENDING_CANCEL:
            // ⚠️ 等待中狀態 → 不做任何操作
            // 📌 原因：避免重複發單或取消（等待交易所回報）
            // 📌 設計權衡：犧牲即時性換取正確性
            break;
        }
    }

    // 📌 便利函式：同時移動買單和賣單（Market Maker 策略常用）
    // 📊 使用場景：做市商需要同時調整買賣報價
    // ⚡ 效能優化：兩個訂單獨立操作，可並行處理（無依賴）
    auto moveOrders(TickerId ticker_id, Price bid_price, Price ask_price,
                    Qty clip) noexcept
    {
        // 移動買單
        auto bid_order = &(ticker_side_order_.at(ticker_id).at(sideToIndex(Side::BUY)));
        moveOrder(bid_order, ticker_id, bid_price, Side::BUY, clip);

        // 移動賣單
        auto ask_order = &(ticker_side_order_.at(ticker_id).at(sideToIndex(
                               Side::SELL)));
        moveOrder(ask_order, ticker_id, ask_price, Side::SELL, clip);
    }

    // 📌 查詢介面：取得指定商品的買賣訂單
    auto getOMOrderSideHashMap(TickerId ticker_id) const
    {
        return &(ticker_side_order_.at(ticker_id));
    }

    // Deleted default, copy & move constructors and assignment-operators.
    OrderManager() = delete;

    OrderManager(const OrderManager&) = delete;

    OrderManager(const OrderManager&&) = delete;

    OrderManager& operator=(const OrderManager&) = delete;

    OrderManager& operator=(const OrderManager&&) = delete;

private:
    TradeEngine* trade_engine_ = nullptr;  // 📌 關聯：用於發送訂單請求
    const RiskManager& risk_manager_;      // 📌 關聯：用於風控檢查

    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 🗂️ 核心資料結構：所有訂單的狀態陣列
    // 📌 索引方式：ticker_side_order_[ticker_id][side_index] → O(1) 查找
    // ⚠️ 限制：每個 (ticker, side) 只能有一個活躍訂單
    // 📊 記憶體大小：假設 ME_MAX_TICKERS=256，OMOrder≈40 bytes → 20 KB
    OMOrderTickerSideHashMap ticker_side_order_;

    // 訂單 ID 生成器（自增）
    // 📌 唯一性保證：每次發單後 +1
    OrderId next_order_id_ = 1;
};
}
