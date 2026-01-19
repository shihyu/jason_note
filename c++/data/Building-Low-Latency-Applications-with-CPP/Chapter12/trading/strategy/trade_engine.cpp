/**
 * @file trade_engine.cpp
 * @brief 交易引擎核心實作
 *
 * 🎯 架構設計：
 * - 訂單簿管理：維護每個標的的本地訂單簿（MarketOrderBook）
 * - 策略執行：支援 MarketMaker、LiquidityTaker 兩種演算法
 * - 風險管理：透過 RiskManager 進行事前風控檢查
 * - 訂單管理：透過 OrderManager 追蹤訂單狀態
 * - 特徵計算：透過 FeatureEngine 計算市場特徵（用於策略決策）
 * - 倉位追蹤：透過 PositionKeeper 管理各標的持倉與 PnL
 *
 * ⚡ 事件驅動架構：
 * - 行情更新 → onTradeUpdate / onOrderBookUpdate → 策略回調
 * - 客戶回報 → onOrderUpdate → 策略回調
 * - 策略透過 sendClientRequest() 發送訂單
 *
 * 📊 執行緒模型：
 * - 單執行緒處理所有事件（避免鎖競爭）
 * - 透過 Lock-Free 佇列接收外部事件
 */
#include "trade_engine.h"

namespace Trading
{
/// 建構函式：初始化交易引擎的所有子系統
TradeEngine::TradeEngine(Common::ClientId client_id,
                         AlgoType algo_type,
                         const TradeEngineCfgHashMap& ticker_cfg,
                         Exchange::ClientRequestLFQueue* client_requests,
                         Exchange::ClientResponseLFQueue* client_responses,
                         Exchange::MEMarketUpdateLFQueue* market_updates)
    : client_id_(client_id),
      outgoing_ogw_requests_(client_requests),      // → OrderGateway
      incoming_ogw_responses_(client_responses),    // ← OrderGateway
      incoming_md_updates_(market_updates),         // ← MarketDataConsumer
      logger_("trading_engine_" + std::to_string(client_id) + ".log"),
      feature_engine_(&logger_),                    // 市場特徵計算器
      position_keeper_(&logger_),                   // 倉位管理器
      order_manager_(&logger_, this, risk_manager_), // 訂單狀態追蹤器
      risk_manager_(&logger_, &position_keeper_, ticker_cfg)  // 風險控管器
{
    // 步驟 1：為每個標的建立本地訂單簿
    // 📊 本地訂單簿用途：
    // - 追蹤市場狀態（最佳買賣價、深度）
    // - 計算市場特徵（價差、不平衡度）
    // - 策略需要即時市場資訊做決策
    for (size_t i = 0; i < ticker_order_book_.size(); ++i) {
        ticker_order_book_[i] = new MarketOrderBook(i, &logger_);
        ticker_order_book_[i]->setTradeEngine(this);  // 設定回調
    }

    // 步驟 2：初始化策略回調函式（預設實作）
    // ⚡ Lambda 捕獲 this，轉發到預設處理函式
    // 🎯 設計模式：策略建構時可覆蓋這些回調，實現客製化邏輯
    algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price, auto side,
    auto book) {
        defaultAlgoOnOrderBookUpdate(ticker_id, price, side, book);
    };
    algoOnTradeUpdate_ = [this](auto market_update, auto book) {
        defaultAlgoOnTradeUpdate(market_update, book);
    };
    algoOnOrderUpdate_ = [this](auto client_response) {
        defaultAlgoOnOrderUpdate(client_response);
    };

    // 步驟 3：根據 algo_type 建立對應的交易策略實例
    // ⚠️ 策略建構式會覆蓋上面的回調函式
    if (algo_type == AlgoType::MAKER) {
        // 做市商策略：提供流動性，賺取價差
        mm_algo_ = new MarketMaker(&logger_, this, &feature_engine_, &order_manager_,
                                   ticker_cfg);
    } else if (algo_type == AlgoType::TAKER) {
        // 趨勢跟隨策略：捕捉價格動能，主動成交
        taker_algo_ = new LiquidityTaker(&logger_, this, &feature_engine_,
                                         &order_manager_, ticker_cfg);
    }
    // ⚠️ RANDOM 演算法不需要策略實例（在 trading_main.cpp 直接實作）

    // 步驟 4：記錄初始化完成
    for (TickerId i = 0; i < ticker_cfg.size(); ++i) {
        logger_.log("%:% %() % Initialized % Ticker:% %.\n", __FILE__, __LINE__,
                    __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_),
                    algoTypeToString(algo_type), i,
                    ticker_cfg.at(i).toString());
    }
}

TradeEngine::~TradeEngine()
{
    run_ = false;

    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);

    delete mm_algo_;
    mm_algo_ = nullptr;
    delete taker_algo_;
    taker_algo_ = nullptr;

    for (auto& order_book : ticker_order_book_) {
        delete order_book;
        order_book = nullptr;
    }

    outgoing_ogw_requests_ = nullptr;
    incoming_ogw_responses_ = nullptr;
    incoming_md_updates_ = nullptr;
}

/// ⚡ 發送客戶訂單請求到 OrderGateway
///
/// 📊 資料流向：
/// TradeEngine → outgoing_ogw_requests_ (LFQueue) → OrderGateway → Exchange
///
/// ⚠️ Lock-Free 寫入流程：
/// 1. getNextToWriteTo()：取得下一個可寫位置的指標
/// 2. 寫入資料（使用 move 語意避免複製）
/// 3. updateWriteIndex()：更新寫入索引（通知讀取端）
///
/// 🎯 效能測量：
/// TTT_MEASURE 追蹤延遲（T10 = 策略決策到寫入佇列的時間）
auto TradeEngine::sendClientRequest(const Exchange::MEClientRequest*
                                    client_request) noexcept -> void
{
    logger_.log("%:% %() % Sending %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                client_request->toString().c_str());

    // ⚡ 兩階段寫入（Lock-Free Queue 標準模式）
    auto next_write = outgoing_ogw_requests_->getNextToWriteTo();  // 取得寫入位置
    *next_write = std::move(*client_request);                       // 寫入資料
    outgoing_ogw_requests_->updateWriteIndex();                     // 更新索引

    TTT_MEASURE(T10_TradeEngine_LFQueue_write, logger_);  // 測量寫入延遲
}

/// ⚡ 主事件迴圈：處理所有進入的訂單回報與市場更新
///
/// 📊 事件處理順序：
/// 1. 優先處理客戶回報（incoming_ogw_responses_）
///    - FILLED, CANCELED, ACCEPTED 等訂單狀態變化
///    - 更新倉位、觸發策略回調
/// 2. 處理市場數據更新（incoming_md_updates_）
///    - ADD, MODIFY, CANCEL, TRADE 等訂單簿變化
///    - 更新本地訂單簿、計算特徵、觸發策略回調
///
/// ⚡ 效能設計：
/// - Busy-loop（無 sleep）：微秒級延遲響應
/// - 單執行緒處理：避免鎖競爭與 context switch
/// - Lock-Free Queue 讀取：O(1) 無阻塞
/// - 批次處理：內層 for 迴圈處理佇列中所有訊息
///
/// ⚠️ 活動追蹤：
/// - last_event_time_ 記錄最後事件時間
/// - 用於判斷系統是否進入閒置狀態（無交易活動）
auto TradeEngine::run() noexcept -> void
{
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    // 主迴圈：持續運行直到 run_ = false
    while (run_) {
        // 步驟 1：處理所有待處理的客戶回報
        // ⚡ 批次處理：一次讀取佇列中所有訊息
        for (auto client_response = incoming_ogw_responses_->getNextToRead();
             client_response; client_response = incoming_ogw_responses_->getNextToRead()) {
            TTT_MEASURE(T9t_TradeEngine_LFQueue_read, logger_);  // 測量讀取延遲

            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_),
                        client_response->toString().c_str());

            onOrderUpdate(client_response);  // 處理訂單更新
            incoming_ogw_responses_->updateReadIndex();  // 更新讀取索引
            last_event_time_ = Common::getCurrentNanos();  // 更新活動時間
        }

        // 步驟 2：處理所有待處理的市場數據更新
        // ⚡ 批次處理：一次讀取佇列中所有訊息
        for (auto market_update = incoming_md_updates_->getNextToRead(); market_update;
             market_update = incoming_md_updates_->getNextToRead()) {
            TTT_MEASURE(T9_TradeEngine_LFQueue_read, logger_);  // 測量讀取延遲

            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_),
                        market_update->toString().c_str());

            // 檢查 ticker_id 有效性
            ASSERT(market_update->ticker_id_ < ticker_order_book_.size(),
                   "Unknown ticker-id on update:" + market_update->toString());

            // 更新對應標的的本地訂單簿（會觸發 onOrderBookUpdate/onTradeUpdate 回調）
            ticker_order_book_[market_update->ticker_id_]->onMarketUpdate(market_update);

            incoming_md_updates_->updateReadIndex();  // 更新讀取索引
            last_event_time_ = Common::getCurrentNanos();  // 更新活動時間
        }
    }
}

/// Process changes to the order book - updates the position keeper, feature engine and informs the trading algorithm about the update.
auto TradeEngine::onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                                    MarketOrderBook* book) noexcept -> void
{
    logger_.log("%:% %() % ticker:% price:% side:%\n", __FILE__, __LINE__,
                __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_), ticker_id,
                Common::priceToString(price).c_str(),
                Common::sideToString(side).c_str());

    auto bbo = book->getBBO();

    START_MEASURE(Trading_PositionKeeper_updateBBO);
    position_keeper_.updateBBO(ticker_id, bbo);
    END_MEASURE(Trading_PositionKeeper_updateBBO, logger_);

    START_MEASURE(Trading_FeatureEngine_onOrderBookUpdate);
    feature_engine_.onOrderBookUpdate(ticker_id, price, side, book);
    END_MEASURE(Trading_FeatureEngine_onOrderBookUpdate, logger_);

    START_MEASURE(Trading_TradeEngine_algoOnOrderBookUpdate_);
    algoOnOrderBookUpdate_(ticker_id, price, side, book);
    END_MEASURE(Trading_TradeEngine_algoOnOrderBookUpdate_, logger_);
}

/// Process trade events - updates the  feature engine and informs the trading algorithm about the trade event.
auto TradeEngine::onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                                MarketOrderBook* book) noexcept -> void
{
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                market_update->toString().c_str());

    START_MEASURE(Trading_FeatureEngine_onTradeUpdate);
    feature_engine_.onTradeUpdate(market_update, book);
    END_MEASURE(Trading_FeatureEngine_onTradeUpdate, logger_);

    START_MEASURE(Trading_TradeEngine_algoOnTradeUpdate_);
    algoOnTradeUpdate_(market_update, book);
    END_MEASURE(Trading_TradeEngine_algoOnTradeUpdate_, logger_);
}

/// Process client responses - updates the position keeper and informs the trading algorithm about the response.
auto TradeEngine::onOrderUpdate(const Exchange::MEClientResponse*
                                client_response) noexcept -> void
{
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                client_response->toString().c_str());

    // ⚡ 分支預測提示：降低誤判成本。
    if (UNLIKELY(client_response->type_ == Exchange::ClientResponseType::FILLED)) {
        START_MEASURE(Trading_PositionKeeper_addFill);
        position_keeper_.addFill(client_response);
        END_MEASURE(Trading_PositionKeeper_addFill, logger_);
    }

    START_MEASURE(Trading_TradeEngine_algoOnOrderUpdate_);
    algoOnOrderUpdate_(client_response);
    END_MEASURE(Trading_TradeEngine_algoOnOrderUpdate_, logger_);
}
}
