// 流動性獲取策略實作：追隨成交訊號下單。
// ⚡ 效能關鍵：成交比率判斷為 O(1)。
// ⚠️ 注意：避免在回調中做重計算。

#include "liquidity_taker.h"

#include "trade_engine.h"

namespace Trading
{
LiquidityTaker::LiquidityTaker(Common::Logger* logger,
                               TradeEngine* trade_engine, const FeatureEngine* feature_engine,
                               OrderManager* order_manager,
                               const TradeEngineCfgHashMap& ticker_cfg)
    : feature_engine_(feature_engine), order_manager_(order_manager),
      logger_(logger),
      ticker_cfg_(ticker_cfg)
{
    trade_engine->algoOnOrderBookUpdate_ = [this](auto ticker_id, auto price,
    auto side, auto book) {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        onOrderBookUpdate(ticker_id, price, side, book);
    };
    trade_engine->algoOnTradeUpdate_ = [this](auto market_update, auto book) {
        onTradeUpdate(market_update, book);
    };
    trade_engine->algoOnOrderUpdate_ = [this](auto client_response) {
        onOrderUpdate(client_response);
    };
}
}
