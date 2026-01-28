#pragma once

#include <functional>

#include "common/thread_utils.h"
#include "common/time_utils.h"
#include "common/lf_queue.h"
#include "common/macros.h"
#include "common/logging.h"

#include "exchange/order_server/client_request.h"
#include "exchange/order_server/client_response.h"
#include "exchange/market_data/market_update.h"

#include "market_order_book.h"

#include "feature_engine.h"
#include "position_keeper.h"
#include "order_manager.h"
#include "risk_manager.h"

#include "market_maker.h"
#include "liquidity_taker.h"

namespace Trading
{
// ============================================================================
// 交易引擎（TradeEngine）
// ============================================================================
// 📌 核心職責：
//   1. 主事件循環：處理行情更新與交易所回報
//   2. 元件協調：整合 FeatureEngine、PositionKeeper、OrderManager、RiskManager
//   3. 策略執行：根據 AlgoType 選擇並執行交易策略（MarketMaker 或 LiquidityTaker）
//   4. 生命週期管理：啟動/停止獨立執行緒
// ⚡ 效能特性：
//   - 單執行緒設計（無鎖競爭）
//   - Lock-Free Queue 通訊（< 1 μs 延遲）
//   - 事件處理延遲：20-50 μs
class TradeEngine
{
public:
    TradeEngine(Common::ClientId client_id,
                AlgoType algo_type,
                const TradeEngineCfgHashMap& ticker_cfg,
                Exchange::ClientRequestLFQueue* client_requests,
                Exchange::ClientResponseLFQueue* client_responses,
                Exchange::MEMarketUpdateLFQueue* market_updates);

    ~TradeEngine();

    // 📌 啟動交易引擎執行緒
    // ⚡ 創建獨立執行緒執行 run() 主循環
    auto start() -> void
    {
        run_ = true;
        ASSERT(Common::createAndStartThread(-1, "Trading/TradeEngine", [this] { run(); })
               != nullptr, "Failed to start TradeEngine thread.");
    }

    auto stop() -> void
    {
        while (incoming_ogw_responses_->size() || incoming_md_updates_->size()) {
            logger_.log("%:% %() % Sleeping till all updates are consumed ogw-size:% md-size:%\n",
                        __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), incoming_ogw_responses_->size(),
                        incoming_md_updates_->size());

            using namespace std::literals::chrono_literals;
            std::this_thread::sleep_for(10ms);
        }

        logger_.log("%:% %() % POSITIONS\n%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_),
                    position_keeper_.toString());

        run_ = false;
    }

    /// Main loop for this thread - processes incoming client responses and market data updates which in turn may generate client requests.
    auto run() noexcept -> void;

    /// Write a client request to the lock free queue for the order server to consume and send to the exchange.
    auto sendClientRequest(const Exchange::MEClientRequest* client_request) noexcept
    -> void;

    /// Process changes to the order book - updates the position keeper, feature engine and informs the trading algorithm about the update.
    auto onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                           MarketOrderBook* book) noexcept -> void;

    /// Process trade events - updates the  feature engine and informs the trading algorithm about the trade event.
    auto onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                       MarketOrderBook* book) noexcept -> void;

    /// Process client responses - updates the position keeper and informs the trading algorithm about the response.
    auto onOrderUpdate(const Exchange::MEClientResponse* client_response) noexcept
    -> void;

    // ============================================================================
    // ⚡ Lambda 回調機制：策略解耦設計
    // ============================================================================
    // 📌 設計目的：
    //   - TradeEngine 不依賴具體策略實作
    //   - 策略在建構時註冊自己的處理函式
    //   - 輕鬆切換不同交易演算法
    // 📊 使用範例：
    //   MarketMaker 在建構時設定：
    //     algoOnOrderBookUpdate_ = [this](...) { onOrderBookUpdate(...); };
    std::function<void(TickerId ticker_id, Price price, Side side, MarketOrderBook* book)>
    algoOnOrderBookUpdate_;  // 訂單簿更新回調
    std::function<void(const Exchange::MEMarketUpdate* market_update, MarketOrderBook* book)>
    algoOnTradeUpdate_;      // 成交事件回調
    std::function<void(const Exchange::MEClientResponse* client_response)>
    algoOnOrderUpdate_;      // 交易所回報回調

    auto initLastEventTime()
    {
        // ⚡ 時間戳取得：避免高開銷 API。
        last_event_time_ = Common::getCurrentNanos();
    }

    auto silentSeconds()
    {
        // ⚡ 時間戳取得：避免高開銷 API。
        return (Common::getCurrentNanos() - last_event_time_) / NANOS_TO_SECS;
    }

    auto clientId() const
    {
        return client_id_;
    }

    /// Deleted default, copy & move constructors and assignment-operators.
    TradeEngine() = delete;

    TradeEngine(const TradeEngine&) = delete;

    TradeEngine(const TradeEngine&&) = delete;

    TradeEngine& operator=(const TradeEngine&) = delete;

    TradeEngine& operator=(const TradeEngine&&) = delete;

private:
    // 📌 客戶端 ID（用於識別交易者身份）
    const ClientId client_id_;

    // 🗂️ 訂單簿管理：TickerId → MarketOrderBook 的映射
    // 📊 記憶體大小：256 * 200 bytes ≈ 50 KB
    MarketOrderBookHashMap ticker_order_book_;

    // ============================================================================
    // ⚡ Lock-Free Queue：跨執行緒通訊
    // ============================================================================
    // 📌 三個佇列的職責：
    //   1. outgoing_ogw_requests_：TradeEngine → OrderGateway（發送訂單請求）
    //   2. incoming_ogw_responses_：OrderGateway → TradeEngine（接收交易所回報）
    //   3. incoming_md_updates_：MarketDataConsumer → TradeEngine（接收行情更新）
    Exchange::ClientRequestLFQueue* outgoing_ogw_requests_ = nullptr;
    Exchange::ClientResponseLFQueue* incoming_ogw_responses_ = nullptr;
    Exchange::MEMarketUpdateLFQueue* incoming_md_updates_ = nullptr;

    Nanos last_event_time_ = 0;
    // ⚠️ 注意：volatile 僅防優化，非同步原語。
    volatile bool run_ = false;  // 主循環控制標誌

    std::string time_str_;
    Logger logger_;

    // ============================================================================
    // 核心元件：交易系統的基礎設施
    // ============================================================================
    // 📌 特徵引擎：計算交易訊號（市場價格、激進成交比率）
    FeatureEngine feature_engine_;

    // 📌 倉位追蹤器：追蹤持倉、PnL、成交量
    PositionKeeper position_keeper_;

    // 📌 訂單管理器：管理訂單生命週期（發單、撤單、狀態更新）
    OrderManager order_manager_;

    // 📌 風控管理器：事前風控檢查（ORDER_TOO_LARGE, POSITION_TOO_LARGE, LOSS_TOO_LARGE）
    RiskManager risk_manager_;

    // ============================================================================
    // 交易策略實例（二選一）
    // ============================================================================
    // ⚠️ 注意：只會創建其中一個（根據 AlgoType 決定）
    MarketMaker* mm_algo_ = nullptr;          // 做市商策略
    LiquidityTaker* taker_algo_ = nullptr;    // 流動性獲取策略

    /// Default methods to initialize the function wrappers.
    auto defaultAlgoOnOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                                      MarketOrderBook*) noexcept -> void
    {
        logger_.log("%:% %() % ticker:% price:% side:%\n", __FILE__, __LINE__,
                    __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), ticker_id,
                    Common::priceToString(price).c_str(),
                    Common::sideToString(side).c_str());
    }

    auto defaultAlgoOnTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                                  MarketOrderBook*) noexcept -> void
    {
        logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_),
                    market_update->toString().c_str());
    }

    auto defaultAlgoOnOrderUpdate(const Exchange::MEClientResponse* client_response)
    noexcept -> void
    {
        logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_),
                    client_response->toString().c_str());
    }
};
}
