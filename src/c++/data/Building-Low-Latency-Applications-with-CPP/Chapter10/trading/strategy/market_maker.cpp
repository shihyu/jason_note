#include "market_maker.h"

#include "trade_engine.h"

namespace Trading
{
// MarketMaker 建構子
//
// 策略初始化流程：
// 1. 儲存核心元件參考（FeatureEngine, OrderManager, 配置）
// 2. 覆寫 TradeEngine 的 Lambda 回調（策略主動權模式）
//
// 設計模式：
// - 策略模式（Strategy Pattern）：將演算法封裝成獨立類別
// - 依賴注入（Dependency Injection）：TradeEngine 提供基礎設施
// - Lambda 回調（Callback）：避免虛函式，內聯展開
//
// ⚡ 效能考量：
// - Lambda 捕獲 this：編譯器內聯展開，零虛函式開銷
// - 策略主動權：由策略決定如何回應事件，TradeEngine 僅分發
//
// 做市商策略特性：
// - 雙邊報價：在買賣兩側同時掛單
// - 賺取價差：買入價 < 賣出價（Bid-Ask Spread）
// - 風險中性：快速平倉，避免持倉風險
//
// @param logger: 日誌記錄器
// @param trade_engine: 交易引擎（提供事件分發）
// @param feature_engine: 特徵引擎（市場價格、激進成交比率）
// @param order_manager: 訂單管理器（訂單狀態機）
// @param ticker_cfg: 交易標的配置表（策略參數）
MarketMaker::MarketMaker(Common::Logger* logger, TradeEngine* trade_engine,
                         const FeatureEngine* feature_engine,
                         OrderManager* order_manager, const TradeEngineCfgHashMap& ticker_cfg)
    : feature_engine_(feature_engine), order_manager_(order_manager),
      logger_(logger),
      ticker_cfg_(ticker_cfg)
{
    // 覆寫 TradeEngine 的訂單簿更新回調
    // ⚡ Lambda 捕獲 this：成員函式指標包裝
    // 當訂單簿變動時（ADD/MODIFY/CANCEL），觸發做市商邏輯
    trade_engine->algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price,
    auto side, auto book) {
        onOrderBookUpdate(ticker_id, price, side, book);
    };

    // 覆寫 TradeEngine 的成交事件回調
    // 做市商通常不關注成交事件（只關注訂單簿價位）
    // 但保留回調以便未來擴展（例如：檢測市場衝擊）
    trade_engine->algoOnTradeUpdate_ = [this](auto market_update, auto book) {
        onTradeUpdate(market_update, book);
    };

    // 覆寫 TradeEngine 的訂單回應回調
    // 當自己的訂單狀態變化時（ACCEPTED/FILLED/CANCELLED），更新策略狀態
    trade_engine->algoOnOrderUpdate_ = [this](auto client_response) {
        onOrderUpdate(client_response);
    };
}
}
