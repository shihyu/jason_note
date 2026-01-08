#pragma once

#include "common/macros.h"
#include "common/logging.h"

#include "order_manager.h"
#include "feature_engine.h"

using namespace Common;

namespace Trading
{
// ============================================================================
// 流動性獲取策略（LiquidityTaker）
// ============================================================================
// 📌 策略類型：主動策略（Aggressive Strategy）
// 📌 核心目標：
//   1. 檢測短期趨勢信號（大額成交）
//   2. 立即市價成交（消耗流動性）
//   3. 快速進出場，捕捉短期波動
// ⚡ 風險：追高殺跌、滑價成本、趨勢反轉
class LiquidityTaker
{
public:
    LiquidityTaker(Common::Logger* logger, TradeEngine* trade_engine,
                   const FeatureEngine* feature_engine,
                   OrderManager* order_manager,
                   const TradeEngineCfgHashMap& ticker_cfg);

    // 📌 訂單簿更新：此策略不處理（只記錄日誌）
    // 原因：Liquidity Taker 只關注成交事件，不關注被動報價變動
    auto onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                           MarketOrderBook*) noexcept -> void
    {
        logger_->log("%:% %() % ticker:% price:% side:%\n", __FILE__, __LINE__,
                     __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_), ticker_id,
                     Common::priceToString(price).c_str(),
                     Common::sideToString(side).c_str());
    }

    // ⚡ 成交事件：核心邏輯（趨勢檢測與跟隨）
    // 📌 邏輯流程：
    //   1. 從 FeatureEngine 取得激進成交比率
    //   2. 比較比率與閾值，判斷是否為強勢趨勢
    //   3. 如果符合條件，立即市價跟隨成交
    // 📊 策略理念：
    //   - 激進買盤（大額買入）→ 跟隨買入（預期推高價格）
    //   - 激進賣盤（大額賣出）→ 跟隨賣出（預期壓低價格）
    auto onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                       MarketOrderBook* book) noexcept -> void
    {
        logger_->log("%:% %() % %\n", __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     market_update->toString().c_str());

        const auto bbo = book->getBBO();
        const auto agg_qty_ratio = feature_engine_->getAggTradeQtyRatio();

        // ⚠️ 前置檢查：BBO 和特徵必須有效
        if (LIKELY(bbo->bid_price_ != Price_INVALID &&
                   bbo->ask_price_ != Price_INVALID && agg_qty_ratio != Feature_INVALID)) {
            logger_->log("%:% %() % % agg-qty-ratio:%\n", __FILE__, __LINE__, __FUNCTION__,
                         Common::getCurrentTimeStr(&time_str_),
                         bbo->toString().c_str(), agg_qty_ratio);

            const auto clip = ticker_cfg_.at(market_update->ticker_id_).clip_;
            const auto threshold = ticker_cfg_.at(market_update->ticker_id_).threshold_;

            // 📊 趨勢檢測：激進成交比率 >= 閾值
            // 範例：threshold = 0.6, agg_qty_ratio = 0.8 → 強勢信號
            if (agg_qty_ratio >= threshold) {
                if (market_update->side_ == Side::BUY) {
                    // 檢測到激進買盤 → 跟隨買入（市價成交）
                    // 📌 買入價格 = Ask Price（立即成交）
                    // 📌 不發賣單（Price_INVALID）
                    order_manager_->moveOrders(market_update->ticker_id_, bbo->ask_price_,
                                               Price_INVALID, clip);
                } else {
                    // 檢測到激進賣盤 → 跟隨賣出（市價成交）
                    // 📌 賣出價格 = Bid Price（立即成交）
                    // 📌 不發買單（Price_INVALID）
                    order_manager_->moveOrders(market_update->ticker_id_, Price_INVALID,
                                               bbo->bid_price_, clip);
                }
            }
        }
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
    LiquidityTaker() = delete;

    LiquidityTaker(const LiquidityTaker&) = delete;

    LiquidityTaker(const LiquidityTaker&&) = delete;

    LiquidityTaker& operator=(const LiquidityTaker&) = delete;

    LiquidityTaker& operator=(const LiquidityTaker&&) = delete;

private:
    // 📌 特徵引擎：提供激進成交比率訊號
    const FeatureEngine* feature_engine_ = nullptr;

    // 📌 訂單管理器：負責發送市價單（立即成交）
    OrderManager* order_manager_ = nullptr;

    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 📌 策略配置：clip_（單次發單量）、threshold_（激進比率閾值）、risk_cfg_（風控配置）
    const TradeEngineCfgHashMap ticker_cfg_;
};
}
