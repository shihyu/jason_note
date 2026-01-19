// 訂單管理器介面：狀態機與風控協作。
// ⚡ 效能關鍵：避免鎖與動態分配。
// ⚠️ 注意：單執行緒假設。

/**
 * @file order_manager.h
 * @brief 訂單管理器標頭檔 - 管理客戶端訂單生命週期
 *
 * 功能：
 * - 訂單生命週期管理（新增、取消、修改）
 * - 訂單狀態追蹤（PENDING_NEW、LIVE、PENDING_CANCEL、DEAD）
 * - 訂單回報處理（ACCEPTED、CANCELED、FILLED）
 * - 與交易所閘道通訊（發送 NEW/CANCEL 請求）
 * - 整合風控管理器（下單前風險檢查）
 *
 * 訂單狀態機：
 * ```
 * INVALID/DEAD → [newOrder] → PENDING_NEW → [ACCEPTED] → LIVE
 *                                                            ↓
 *                                                      [cancelOrder]
 *                                                            ↓
 *                                         PENDING_CANCEL → [CANCELED] → DEAD
 *                                                            ↓
 *                                         [FILLED fully] → DEAD
 * ```
 *
 * 架構位置：
 * - OrderManager：客戶端訂單管理（本地狀態追蹤）
 * - OrderGateway：網路通訊層（發送請求到交易所）
 * - MatchingEngine：交易所撮合引擎（處理訂單）
 *
 * 設計模式：
 * - 狀態模式：訂單狀態機管理（OMOrderState）
 * - 命令模式：封裝訂單操作（newOrder、cancelOrder、moveOrder）
 * - 觀察者模式：接收訂單回報（onOrderUpdate）
 *
 * 使用場景：
 * 1. 做市商策略：moveOrders() 批量更新買賣雙邊報價
 * 2. 流動性接盤：newOrder() 主動吃單
 * 3. 訂單維護：cancelOrder() 撤單
 *
 * 效能特性：
 * - 所有方法標記 noexcept（無例外拋出）
 * - 使用預先分配的 OMOrderTickerSideHashMap（避免動態分配）
 * - 快速狀態查詢（O(1) 哈希表訪問）
 * - 日誌記錄不影響主路徑延遲
 */

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

/**
 * @class OrderManager
 * @brief 訂單管理器 - 管理客戶端訂單的完整生命週期
 *
 * 核心職責：
 * 1. 訂單狀態追蹤：維護每個商品每個方向的訂單狀態
 * 2. 訂單操作封裝：newOrder、cancelOrder、moveOrder
 * 3. 回報處理：接收並處理交易所回報（ACCEPTED、FILLED、CANCELED）
 * 4. 風控整合：下單前調用 RiskManager 進行風險檢查
 * 5. 日誌記錄：所有訂單操作和狀態變化
 *
 * 訂單狀態：
 * - INVALID：未初始化
 * - PENDING_NEW：已發送新單請求，等待確認
 * - LIVE：已被交易所接受，在訂單簿中
 * - PENDING_CANCEL：已發送撤單請求，等待確認
 * - DEAD：已完全成交或已取消
 *
 * 數據結構：
 * - ticker_side_order_：每個商品每個方向（BUY/SELL）的訂單追蹤
 * - next_order_id_：遞增的訂單 ID 生成器
 *
 * 注意事項：
 * - 單例模式：每個 TradeEngine 只有一個 OrderManager
 * - 線程安全：假設單線程環境（TradeEngine 的事件迴圈）
 * - 訂單 ID 唯一性：next_order_id_ 單調遞增
 */
class OrderManager
{
public:
    /**
     * @brief 建構函式 - 初始化訂單管理器
     *
     * @param logger 日誌記錄器
     * @param trade_engine 交易引擎（用於發送訂單請求）
     * @param risk_manager 風控管理器（下單前風險檢查）
     *
     * 初始化：
     * - 設定 TradeEngine 引用（發送訂單到交易所）
     * - 設定 RiskManager 引用（風險檢查）
     * - 初始化 next_order_id_ = 1
     */
    OrderManager(Common::Logger* logger, TradeEngine* trade_engine,
                 RiskManager& risk_manager)
        : trade_engine_(trade_engine), risk_manager_(risk_manager), logger_(logger)
    {
    }

    /**
     * onOrderUpdate() - 處理來自交易所的訂單回報
     *
     * @param client_response 交易所回報（ACCEPTED、FILLED、CANCELED 等）
     *
     * 回報類型處理：
     * 1. ACCEPTED：訂單被接受 → 狀態變更為 LIVE
     * 2. CANCELED：訂單被取消 → 狀態變更為 DEAD
     * 3. FILLED：訂單成交 → 更新剩餘數量，若完全成交則變更為 DEAD
     * 4. CANCEL_REJECTED：撤單被拒絕 → 不改變狀態
     * 5. INVALID：無效回報 → 不處理
     *
     * 實作邏輯：
     * - 根據 ticker_id 和 side 查找對應的訂單物件
     * - 根據回報類型更新訂單狀態
     * - 記錄所有狀態變更到日誌
     *
     * 效能特性：
     * - noexcept：不拋出例外
     * - O(1) 查找：使用哈希表查找訂單
     * - 時間複雜度：O(1)
     *
     * 注意事項：
     * - 假設回報對應的訂單一定存在（由 TradeEngine 保證）
     * - FILLED 回報可能是部分成交或完全成交
     * - 只有 leaves_qty_ == 0 時才標記為 DEAD
     */
    auto onOrderUpdate(const Exchange::MEClientResponse* client_response) noexcept
    -> void
    {
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     client_response->toString().c_str());
        auto order = &(ticker_side_order_.at(client_response->ticker_id_).at(
                           sideToIndex(client_response->side_)));
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     order->toString().c_str());

        switch (client_response->type_) {
        case Exchange::ClientResponseType::ACCEPTED: {
                order->order_state_ = OMOrderState::LIVE;
            }
            break;

        case Exchange::ClientResponseType::CANCELED: {
                order->order_state_ = OMOrderState::DEAD;
            }
            break;

        case Exchange::ClientResponseType::FILLED: {
                order->qty_ = client_response->leaves_qty_;

                if (!order->qty_) {
                    order->order_state_ = OMOrderState::DEAD;
                }
            }
            break;

        case Exchange::ClientResponseType::CANCEL_REJECTED:
        case Exchange::ClientResponseType::INVALID: {
            }
            break;
        }
    }

    /**
     * newOrder() - 發送新訂單請求到交易所
     *
     * @param order 要更新的訂單物件（輸出參數）
     * @param ticker_id 商品識別碼
     * @param price 訂單價格
     * @param side 買賣方向（BUY/SELL）
     * @param qty 訂單數量
     *
     * 實作邏輯：
     * 1. 生成新的訂單 ID（next_order_id_++）
     * 2. 建構 MEClientRequest（NEW 類型）
     * 3. 發送請求到 TradeEngine
     * 4. 更新本地訂單狀態為 PENDING_NEW
     * 5. 記錄日誌
     *
     * 訂單狀態變化：
     * - 呼叫前：INVALID 或 DEAD
     * - 呼叫後：PENDING_NEW
     * - 收到 ACCEPTED 回報後：LIVE
     *
     * 注意事項：
     * - 必須在風控檢查通過後才能呼叫
     * - 訂單 ID 單調遞增，保證全局唯一性
     * - 不等待交易所回報，立即返回
     *
     * @see onOrderUpdate() 處理 ACCEPTED 回報
     */
    auto newOrder(OMOrder* order, TickerId ticker_id, Price price, Side side,
                  Qty qty) noexcept -> void;

    /**
     * cancelOrder() - 發送撤單請求到交易所
     *
     * @param order 要撤銷的訂單物件
     *
     * 實作邏輯：
     * 1. 建構 MEClientRequest（CANCEL 類型）
     * 2. 發送請求到 TradeEngine
     * 3. 更新本地訂單狀態為 PENDING_CANCEL
     * 4. 記錄日誌
     *
     * 訂單狀態變化：
     * - 呼叫前：LIVE
     * - 呼叫後：PENDING_CANCEL
     * - 收到 CANCELED 回報後：DEAD
     *
     * 注意事項：
     * - 只能撤銷狀態為 LIVE 的訂單
     * - 撤單可能被拒絕（CANCEL_REJECTED）
     * - 已成交的訂單無法撤銷
     *
     * @see onOrderUpdate() 處理 CANCELED 回報
     */
    auto cancelOrder(OMOrder* order) noexcept -> void;

    /**
     * moveOrder() - 智能訂單修改（撤單後重新下單）
     *
     * @param order 要修改的訂單物件
     * @param ticker_id 商品識別碼
     * @param price 新價格
     * @param side 買賣方向
     * @param qty 新數量
     *
     * 實作邏輯（根據訂單狀態）：
     *
     * 1. LIVE 狀態：
     *    - 若價格改變 → 撤銷舊訂單（不立即下新單，等待回報）
     *    - 若價格未變 → 不操作
     *
     * 2. INVALID/DEAD 狀態：
     *    - 若新價格有效 → 執行風控檢查
     *    - 風控通過 → 發送新訂單
     *    - 風控拒絕 → 記錄日誌，不下單
     *
     * 3. PENDING_NEW/PENDING_CANCEL 狀態：
     *    - 不操作（等待回報處理）
     *
     * 設計理由：
     * - 避免重複下單：只在 DEAD 狀態時下新單
     * - 價格變化檢測：只在價格改變時撤單
     * - 風控整合：每次新單都經過風控檢查
     *
     * 使用場景：
     * - 做市商策略更新報價
     * - 訂單價格跟隨市場變化
     *
     * 注意事項：
     * - 撤單後不立即下新單（等待策略主動決策）
     * - 使用 LIKELY 宏優化分支預測
     *
     * @see newOrder() 發送新訂單
     * @see cancelOrder() 撤銷訂單
     */
    auto moveOrder(OMOrder* order, TickerId ticker_id, Price price, Side side,
                   Qty qty) noexcept
    {
        switch (order->order_state_) {
        case OMOrderState::LIVE: {
                if (order->price_ != price) {
                    cancelOrder(order);
                }
            }
            break;

        case OMOrderState::INVALID:
        case OMOrderState::DEAD: {
                if (LIKELY(price != Price_INVALID)) {
                    const auto risk_result = risk_manager_.checkPreTradeRisk(ticker_id, side, qty);

                    if (LIKELY(risk_result == RiskCheckResult::ALLOWED)) {
                        newOrder(order, ticker_id, price, side, qty);
                    } else
                        logger_->log("%:% %() % Ticker:% Side:% Qty:% RiskCheckResult:%\n", __FILE__,
                                     __LINE__, __FUNCTION__,
                                     Common::getCurrentTimeStr(&time_str_),
                                     tickerIdToString(ticker_id), sideToString(side), qtyToString(qty),
                                     riskCheckResultToString(risk_result));
                }
            }
            break;

        case OMOrderState::PENDING_NEW:
        case OMOrderState::PENDING_CANCEL:
            break;
        }
    }

    /**
     * moveOrders() - 批量更新買賣雙邊訂單
     *
     * @param ticker_id 商品識別碼
     * @param bid_price 新買單價格
     * @param ask_price 新賣單價格
     * @param clip 訂單數量（買賣相同）
     *
     * 功能：
     * - 同時更新買單和賣單
     * - 呼叫 moveOrder() 處理每個方向的訂單
     *
     * 使用場景：
     * - 做市商策略：同時更新雙邊報價
     * - 維持市場流動性：買賣掛單同步調整
     *
     * 實作邏輯：
     * 1. 查找該商品的買單（BUY 方向）
     * 2. 呼叫 moveOrder() 更新買單
     * 3. 查找該商品的賣單（SELL 方向）
     * 4. 呼叫 moveOrder() 更新賣單
     *
     * 注意事項：
     * - 買賣單獨立處理，一個失敗不影響另一個
     * - clip 參數對買賣單使用相同值
     *
     * @see moveOrder() 單個訂單修改邏輯
     */
    auto moveOrders(TickerId ticker_id, Price bid_price, Price ask_price,
                    Qty clip) noexcept
    {
        auto bid_order = &(ticker_side_order_.at(ticker_id).at(sideToIndex(Side::BUY)));
        moveOrder(bid_order, ticker_id, bid_price, Side::BUY, clip);

        auto ask_order = &(ticker_side_order_.at(ticker_id).at(sideToIndex(
                               Side::SELL)));
        moveOrder(ask_order, ticker_id, ask_price, Side::SELL, clip);
    }

    /**
     * getOMOrderSideHashMap() - 獲取指定商品的買賣訂單映射
     *
     * @param ticker_id 商品識別碼
     * @return 該商品的買賣雙向訂單哈希表指標
     *
     * 返回結構：
     * - 陣列大小：2（索引 0 = BUY, 索引 1 = SELL）
     * - 每個元素：OMOrder 物件
     *
     * 使用場景：
     * - 外部模組查詢訂單狀態
     * - 策略引擎讀取當前訂單資訊
     *
     * 注意事項：
     * - 返回 const 指標（唯讀訪問）
     * - 調用者不應修改訂單狀態
     */
    auto getOMOrderSideHashMap(TickerId ticker_id) const
    {
        return &(ticker_side_order_.at(ticker_id));
    }

    // Deleted default, copy & move constructors and assignment-operators.
    // 刪除預設建構、複製與移動建構函式及賦值運算子
    // 理由：OrderManager 應單例存在於 TradeEngine 中，避免意外複製
    OrderManager() = delete;

    OrderManager(const OrderManager&) = delete;

    OrderManager(const OrderManager&&) = delete;

    OrderManager& operator=(const OrderManager&) = delete;

    OrderManager& operator=(const OrderManager&&) = delete;

private:
    /// 交易引擎引用（用於發送訂單請求到交易所）
    TradeEngine* trade_engine_ = nullptr;

    /// 風控管理器引用（下單前風險檢查）
    const RiskManager& risk_manager_;

    /// 時間字串緩衝區（避免每次格式化時分配記憶體）
    std::string time_str_;

    /// 日誌記錄器（記錄所有訂單操作）
    Common::Logger* logger_ = nullptr;

    /**
     * ticker_side_order_ - 訂單追蹤哈希表
     *
     * 結構：ticker_id → [BUY/SELL] → OMOrder
     * - 第一層：商品 ID (TickerId)
     * - 第二層：買賣方向 (Side: BUY=0, SELL=1)
     * - 值：訂單物件 (OMOrder)
     *
     * 設計理由：
     * - 每個商品每個方向只維護一個訂單
     * - O(1) 訂單查找效率
     * - 固定大小，預先分配（無動態記憶體分配）
     *
     * 使用方式：
     * - ticker_side_order_.at(ticker_id).at(sideToIndex(side))
     */
    OMOrderTickerSideHashMap ticker_side_order_;

    /**
     * next_order_id_ - 訂單 ID 生成器
     *
     * 特性：
     * - 單調遞增，從 1 開始
     * - 保證訂單 ID 全局唯一性
     * - 每次 newOrder() 後自動遞增
     *
     * 注意事項：
     * - 不會重複使用已刪除訂單的 ID
     * - 可能溢位（需要處理 OrderId 類型上限）
     */
    OrderId next_order_id_ = 1;
};
}
