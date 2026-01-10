#include "liquidity_taker.h"

#include "trade_engine.h"

namespace Trading
{
// LiquidityTaker 建構子
//
// 策略初始化流程：
// 1. 儲存核心元件參考（FeatureEngine, OrderManager, 配置）
// 2. 覆寫 TradeEngine 的 Lambda 回調（策略主動權模式）
//
// 設計模式：
// - 策略模式（Strategy Pattern）：與 MarketMaker 共享相同架構
// - 依賴注入（Dependency Injection）：TradeEngine 提供基礎設施
// - Lambda 回調（Callback）：避免虛函式，內聯展開
//
// ⚡ 效能考量：
// - Lambda 捕獲 this：編譯器內聯展開，零虛函式開銷
// - 策略主動權：由策略決定如何回應事件，TradeEngine 僅分發
//
// 流動性獲取者策略特性：
// - 市價成交：使用市價單（Market Order）立即成交
// - 趨勢跟隨：偵測激進買賣訊號，順勢交易
// - 單邊操作：只在判斷趨勢方向時下單（不雙邊報價）
// - 高週轉：快速進出，捕捉短期價格變動
//
// @param logger: 日誌記錄器
// @param trade_engine: 交易引擎（提供事件分發）
// @param feature_engine: 特徵引擎（激進成交比率、趨勢判斷）
// @param order_manager: 訂單管理器（訂單狀態機）
// @param ticker_cfg: 交易標的配置表（策略參數）
LiquidityTaker::LiquidityTaker(Common::Logger* logger,
                               TradeEngine* trade_engine, const FeatureEngine* feature_engine,
                               OrderManager* order_manager,
                               const TradeEngineCfgHashMap& ticker_cfg)
    : feature_engine_(feature_engine), order_manager_(order_manager),
      logger_(logger),
      ticker_cfg_(ticker_cfg)
{
    // 覆寫 TradeEngine 的訂單簿更新回調
    // ⚡ Lambda 捕獲 this：成員函式指標包裝
    // LiquidityTaker 通常不太關注訂單簿變動（更關注成交事件）
    trade_engine->algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price,
    auto side, auto book) {
        onOrderBookUpdate(ticker_id, price, side, book);
    };

    // 覆寫 TradeEngine 的成交事件回調
    // ⚡ 關鍵回調：LiquidityTaker 主要依據成交事件判斷趨勢
    // 當偵測到激進買入（Aggressive Buy）時，跟隨買入
    // 當偵測到激進賣出（Aggressive Sell）時，跟隨賣出
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
