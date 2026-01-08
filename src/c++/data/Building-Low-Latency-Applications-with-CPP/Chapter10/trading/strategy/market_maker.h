#pragma once

#include "common/macros.h"
#include "common/logging.h"

#include "order_manager.h"
#include "feature_engine.h"

using namespace Common;

namespace Trading
{
// ============================================================================
// 做市商策略（MarketMaker）
// ============================================================================
// 📌 策略類型：被動策略（Passive Strategy）
// 📌 核心目標：
//   1. 在 BBO 附近掛買賣單
//   2. 賺取買賣價差（Spread）
//   3. 持續提供流動性
// ⚡ 風險：單邊成交風險（只成交買單或只成交賣單導致倉位偏離）
class MarketMaker
{
public:
    MarketMaker(Common::Logger* logger, TradeEngine* trade_engine,
                const FeatureEngine* feature_engine,
                OrderManager* order_manager,
                const TradeEngineCfgHashMap& ticker_cfg);

    // ⚡ 訂單簿更新：動態調整報價
    // 📌 邏輯流程：
    //   1. 從 FeatureEngine 取得公平價格
    //   2. 根據公平價與 BBO 的距離決定報價位置
    //   3. 透過 OrderManager 移動訂單
    // 📊 定價策略：
    //   - 如果公平價遠離 BBO → 掛在最佳價（保守）
    //   - 如果公平價接近 BBO → 掛在次佳價（激進）
    auto onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                           const MarketOrderBook* book) noexcept -> void
    {
        logger_->log("%:% %() % ticker:% price:% side:%\n", __FILE__, __LINE__,
                     __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_), ticker_id,
                     Common::priceToString(price).c_str(),
                     Common::sideToString(side).c_str());

        const auto bbo = book->getBBO();
        const auto fair_price = feature_engine_->getMktPrice();

        // ⚠️ 前置檢查：BBO 和公平價必須有效
        if (LIKELY(bbo->bid_price_ != Price_INVALID &&
                   bbo->ask_price_ != Price_INVALID && fair_price != Feature_INVALID)) {
            logger_->log("%:% %() % % fair-price:%\n", __FILE__, __LINE__, __FUNCTION__,
                         Common::getCurrentTimeStr(&time_str_),
                         bbo->toString().c_str(), fair_price);

            const auto clip = ticker_cfg_.at(ticker_id).clip_;
            const auto threshold = ticker_cfg_.at(ticker_id).threshold_;

            // 📊 動態買單定價
            // 如果 fair_price - bid >= threshold（公平價遠高於最佳買價）
            //   → bid_price = bid（掛在最佳買價，保守）
            // 否則
            //   → bid_price = bid - 1（掛在次佳買價，激進）
            const auto bid_price = bbo->bid_price_ - (fair_price - bbo->bid_price_ >=
                                   threshold ? 0 : 1);

            // 📊 動態賣單定價
            // 如果 ask - fair_price >= threshold（公平價遠低於最佳賣價）
            //   → ask_price = ask（掛在最佳賣價，保守）
            // 否則
            //   → ask_price = ask + 1（掛在次佳賣價，激進）
            const auto ask_price = bbo->ask_price_ + (bbo->ask_price_ - fair_price >=
                                   threshold ? 0 : 1);

            // ⚡ 移動訂單至新價格（經過風控檢查）
            order_manager_->moveOrders(ticker_id, bid_price, ask_price, clip);
        }
    }

    /// Process trade events, which for the market making algorithm is none.
    auto onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                       MarketOrderBook* /* book */) noexcept -> void
    {
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     market_update->toString().c_str());
    }

    /// Process client responses for the strategy's orders.
    auto onOrderUpdate(const Exchange::MEClientResponse* client_response) noexcept
    -> void
    {
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     client_response->toString().c_str());

        order_manager_->onOrderUpdate(client_response);
    }

    /// Deleted default, copy & move constructors and assignment-operators.
    MarketMaker() = delete;

    MarketMaker(const MarketMaker&) = delete;

    MarketMaker(const MarketMaker&&) = delete;

    MarketMaker& operator=(const MarketMaker&) = delete;

    MarketMaker& operator=(const MarketMaker&&) = delete;

private:
    // 📌 特徵引擎：提供公平價格訊號
    const FeatureEngine* feature_engine_ = nullptr;

    // 📌 訂單管理器：負責發單、撤單、移動訂單
    OrderManager* order_manager_ = nullptr;

    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 📌 策略配置：clip_（單次發單量）、threshold_（價格閾值）、risk_cfg_（風控配置）
    const TradeEngineCfgHashMap ticker_cfg_;
};
}
