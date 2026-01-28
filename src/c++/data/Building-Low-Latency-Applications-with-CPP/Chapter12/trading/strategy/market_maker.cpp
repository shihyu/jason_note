// 做市商策略實作：根據市場狀態調整報價。
// ⚡ 效能關鍵：計算路徑短、最小化分支。
// ⚠️ 注意：避免頻繁撤單導致抖動。

#include "market_maker.h"

#include "trade_engine.h"

namespace Trading
{
MarketMaker::MarketMaker(Common::Logger* logger, TradeEngine* trade_engine,
                         const FeatureEngine* feature_engine,
                         OrderManager* order_manager, const TradeEngineCfgHashMap& ticker_cfg)
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
