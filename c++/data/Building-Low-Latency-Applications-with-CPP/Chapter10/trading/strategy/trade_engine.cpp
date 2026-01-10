#include "trade_engine.h"

namespace Trading
{
// TradeEngine 建構子
//
// 初始化流程（依賴順序）：
// 1. 初始化成員列表：logger → feature_engine → position_keeper → order_manager → risk_manager
// 2. 創建訂單簿實例（每個交易標的一個）
// 3. 設置 Lambda 回調函式（預設實作）
// 4. 根據策略類型創建具體策略實例（MarketMaker 或 LiquidityTaker）
//
// ⚡ 效能設計：
// - 所有元件在建構子一次性初始化，避免執行時動態配置
// - 使用 Lambda 回調實現多態（避免虛函式 vtable 查找）
// - 策略實例會覆寫預設回調（策略主動權模式）
//
// @param client_id: 客戶端 ID（用於日誌檔名）
// @param algo_type: 策略類型（MAKER 或 TAKER）
// @param ticker_cfg: 交易標的配置表
// @param client_requests: 發送訂單請求的 Lock-Free Queue
// @param client_responses: 接收訂單回應的 Lock-Free Queue
// @param market_updates: 接收市場數據更新的 Lock-Free Queue
TradeEngine::TradeEngine(Common::ClientId client_id,
                         AlgoType algo_type,
                         const TradeEngineCfgHashMap& ticker_cfg,
                         Exchange::ClientRequestLFQueue* client_requests,
                         Exchange::ClientResponseLFQueue* client_responses,
                         Exchange::MEMarketUpdateLFQueue* market_updates)
    : client_id_(client_id), outgoing_ogw_requests_(client_requests),
      incoming_ogw_responses_(client_responses),
      incoming_md_updates_(market_updates),
      logger_("trading_engine_" + std::to_string(client_id) + ".log"),
      feature_engine_(&logger_),
      position_keeper_(&logger_),
      order_manager_(&logger_, this, risk_manager_),
      risk_manager_(&logger_, &position_keeper_, ticker_cfg)
{
    // 為每個交易標的創建訂單簿實例
    // ⚡ 固定數量（ME_MAX_TICKERS=8）：編譯期已知大小
    for (size_t i = 0; i < ticker_order_book_.size(); ++i) {
        ticker_order_book_[i] = new MarketOrderBook(i, &logger_);
        // 設置雙向關聯：訂單簿 → 交易引擎（事件通知）
        ticker_order_book_[i]->setTradeEngine(this);
    }

    // 初始化 Lambda 回調函式（預設實作）
    // ⚡ Lambda 優勢：內聯展開，避免虛函式間接呼叫
    // 訂單簿更新回調
    algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price, auto side,
    auto book) {
        defaultAlgoOnOrderBookUpdate(ticker_id, price, side, book);
    };
    // 成交事件回調
    algoOnTradeUpdate_ = [this](auto market_update, auto book) {
        defaultAlgoOnTradeUpdate(market_update, book);
    };
    // 訂單回應回調
    algoOnOrderUpdate_ = [this](auto client_response) {
        defaultAlgoOnOrderUpdate(client_response);
    };

    // 根據策略類型創建具體策略實例
    // ⚠️ 策略建構子會覆寫上述 Lambda 回調（策略主動權）
    if (algo_type == AlgoType::MAKER) {
        mm_algo_ = new MarketMaker(&logger_, this, &feature_engine_, &order_manager_,
                                   ticker_cfg);
    } else if (algo_type == AlgoType::TAKER) {
        taker_algo_ = new LiquidityTaker(&logger_, this, &feature_engine_,
                                         &order_manager_, ticker_cfg);
    }

    // 記錄初始化完成（所有交易標的配置）
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

// sendClientRequest: 發送訂單請求到撮合引擎
//
// 資料流向：
// TradeEngine → Lock-Free Queue → OrderGateway → Exchange
//
// ⚡ 效能關鍵：
// - 零複製：使用 std::move 移動資料
// - Lock-Free：SPSC Queue，無互斥鎖
// - 單向發送：不等待確認（異步模式）
//
// @param client_request: 訂單請求指標
auto TradeEngine::sendClientRequest(const Exchange::MEClientRequest*
                                    client_request) noexcept -> void
{
    logger_.log("%:% %() % Sending %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                client_request->toString().c_str());
    // 取得佇列的下一個寫入位置
    auto next_write = outgoing_ogw_requests_->getNextToWriteTo();
    // ⚡ 移動語義：避免複製，直接轉移所有權
    *next_write = std::move(*client_request);
    // 更新寫入索引（發布資料給消費者）
    outgoing_ogw_requests_->updateWriteIndex();
}

// run: 主事件迴圈（在專用執行緒中執行）
//
// 處理流程（優先順序）：
// 1. 訂單回應（FILLED, ACCEPTED, CANCELLED...）
// 2. 市場數據更新（ADD, MODIFY, CANCEL, TRADE）
//
// ⚡ 效能設計：
// - 忙碌輪詢：持續檢查 Lock-Free Queue，無 sleep
// - 批次處理：一次處理佇列中所有可用消息
// - 單執行緒：避免鎖競爭（所有狀態更新在此執行緒）
//
// ⚠️ 注意：
// - 無阻塞操作：即使佇列為空也會立即返回（高 CPU 使用率）
// - 延遲追蹤：last_event_time_ 記錄最後事件時間（用於監控）
auto TradeEngine::run() noexcept -> void
{
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    while (run_) {
        // 處理訂單回應（優先處理：了解自己訂單狀態）
        // ⚡ 批次處理：連續讀取直到佇列為空
        for (auto client_response = incoming_ogw_responses_->getNextToRead();
             client_response; client_response = incoming_ogw_responses_->getNextToRead()) {
            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_),
                        client_response->toString().c_str());
            // 處理訂單回應（更新倉位、通知策略）
            onOrderUpdate(client_response);
            // 釋放佇列槽位
            incoming_ogw_responses_->updateReadIndex();
            // 記錄事件時間（用於延遲監控）
            last_event_time_ = Common::getCurrentNanos();
        }

        // 處理市場數據更新（次優先：了解市場狀態）
        // ⚡ 批次處理：連續讀取直到佇列為空
        for (auto market_update = incoming_md_updates_->getNextToRead(); market_update;
             market_update = incoming_md_updates_->getNextToRead()) {
            logger_.log("%:% %() % Processing %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_),
                        market_update->toString().c_str());
            // ⚠️ 斷言檢查：防止非法 ticker_id
            ASSERT(market_update->ticker_id_ < ticker_order_book_.size(),
                   "Unknown ticker-id on update:" + market_update->toString());
            // 更新本地訂單簿副本（觸發訂單簿回調）
            ticker_order_book_[market_update->ticker_id_]->onMarketUpdate(market_update);
            // 釋放佇列槽位
            incoming_md_updates_->updateReadIndex();
            // 記錄事件時間
            last_event_time_ = Common::getCurrentNanos();
        }
    }
}

// onOrderBookUpdate: 處理訂單簿變動事件
//
// 觸發時機：
// - ADD: 新訂單加入訂單簿
// - MODIFY: 訂單數量變動（部分成交）
// - CANCEL: 訂單被取消或完全成交
//
// 處理流程：
// 1. 更新倉位追蹤器的最佳買賣價（BBO）
// 2. 通知特徵引擎更新市場價格指標
// 3. 通知交易策略（觸發策略邏輯）
//
// ⚡ 效能關鍵：
// - BBO 查詢：O(1) 訂單簿頂層價位
// - Lambda 回調：內聯展開，避免虛函式呼叫
//
// @param ticker_id: 交易標的 ID
// @param price: 變動發生的價位
// @param side: 買/賣方向
// @param book: 訂單簿指標
auto TradeEngine::onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                                    MarketOrderBook* book) noexcept -> void
{
    logger_.log("%:% %() % ticker:% price:% side:%\n", __FILE__, __LINE__,
                __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_), ticker_id,
                Common::priceToString(price).c_str(),
                Common::sideToString(side).c_str());

    // 取得最佳買賣價（Best Bid and Offer）
    auto bbo = book->getBBO();

    // 更新倉位追蹤器的 BBO（用於 PnL 計算）
    position_keeper_.updateBBO(ticker_id, bbo);

    // 通知特徵引擎（更新市場價格、價差等指標）
    feature_engine_.onOrderBookUpdate(ticker_id, price, side, book);

    // 通知交易策略（可能觸發下單/撤單）
    // ⚡ Lambda 回調：由具體策略覆寫（MarketMaker 或 LiquidityTaker）
    algoOnOrderBookUpdate_(ticker_id, price, side, book);
}

// onTradeUpdate: 處理成交事件
//
// 觸發時機：
// - 訂單簿中發生撮合（買賣雙方訂單匹配）
//
// 處理流程：
// 1. 通知特徵引擎更新激進成交比率
// 2. 通知交易策略（LiquidityTaker 可能跟隨趨勢）
//
// ⚡ 效能關鍵：
// - 成交事件較少：相比訂單簿更新，成交頻率低
// - Lambda 回調：內聯展開
//
// @param market_update: 成交事件資訊
// @param book: 訂單簿指標
auto TradeEngine::onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                                MarketOrderBook* book) noexcept -> void
{
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                market_update->toString().c_str());

    // 通知特徵引擎（更新激進成交比率）
    feature_engine_.onTradeUpdate(market_update, book);

    // 通知交易策略（可能觸發跟隨交易）
    // ⚡ Lambda 回調：由具體策略覆寫
    algoOnTradeUpdate_(market_update, book);
}

// onOrderUpdate: 處理訂單回應
//
// 觸發時機：
// - ACCEPTED: 訂單被接受
// - CANCELLED: 訂單被取消
// - FILLED: 訂單完全成交
//
// 處理流程：
// 1. 如果是成交回應（FILLED）：更新倉位追蹤器
// 2. 通知交易策略（OrderManager 更新訂單狀態）
//
// ⚡ 效能關鍵：
// - UNLIKELY 提示：FILLED 是少數情況，優化分支預測
// - 倉位更新：只在 FILLED 時執行（減少不必要計算）
//
// @param client_response: 訂單回應
auto TradeEngine::onOrderUpdate(const Exchange::MEClientResponse*
                                client_response) noexcept -> void
{
    logger_.log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_),
                client_response->toString().c_str());

    // ⚡ UNLIKELY: 大多數回應是 ACCEPTED/CANCELLED，FILLED 較少
    // 分支預測優化：假設條件為假，減少流水線停頓
    if (UNLIKELY(client_response->type_ == Exchange::ClientResponseType::FILLED)) {
        // 更新倉位（計算 VWAP、已實現/未實現 PnL）
        position_keeper_.addFill(client_response);
    }

    // 通知交易策略（OrderManager 更新訂單狀態機）
    // ⚡ Lambda 回調：由具體策略覆寫
    algoOnOrderUpdate_(client_response);
}
}
