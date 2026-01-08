#pragma once

#include "common/macros.h"
#include "common/logging.h"

using namespace Common;

namespace Trading
{
/// 📌 特徵無效值：使用 NaN 表示未初始化或無效的特徵
/// ⚠️ 使用時必須用 std::isnan() 檢查，避免錯誤的數值比較
constexpr auto Feature_INVALID = std::numeric_limits<double>::quiet_NaN();

// ============================================================================
// 特徵引擎（FeatureEngine）
// ============================================================================
// 📌 核心職責：
//   1. 從原始市場數據提取交易訊號（Alpha Signals）
//   2. 計算公平價格（Market Price）
//   3. 計算激進成交比率（Aggressive Trade Quantity Ratio）
// ⚡ 效能特性：
//   - 簡單算術運算（< 2 μs）
//   - 無記憶體分配
//   - 實時更新特徵
class FeatureEngine
{
public:
    FeatureEngine(Common::Logger* logger)
        : logger_(logger)
    {
    }

    // ⚡ 訂單簿更新：計算公平市場價格（Market Price）
    // 📌 公式：(Bid * AskQty + Ask * BidQty) / (BidQty + AskQty)
    // 📊 原理：根據掛單量加權，反映供需關係 (Volume Weighted Mid Price)
    // 範例：Bid=100(500張) Ask=100.05(300張)
    //      → (100*300 + 100.05*500) / 800 = 100.03125
    // 意義: 如果買單量大，價格會偏向 Ask (買方推升價格的壓力大)
    auto onOrderBookUpdate(TickerId ticker_id, Price price, Side side,
                           MarketOrderBook* book) noexcept -> void
    {
        const auto bbo = book->getBBO();

        if (LIKELY(bbo->bid_price_ != Price_INVALID &&
                   bbo->ask_price_ != Price_INVALID)) {
            // 📊 數量加權價格：考慮買賣掛單量的平衡
            // ⚠️ 注意：分母不會為 0（BBO 存在則必有數量）
            mkt_price_ = (bbo->bid_price_ * bbo->ask_qty_ + bbo->ask_price_ *
                          bbo->bid_qty_) / static_cast<double>(bbo->bid_qty_ + bbo->ask_qty_);
        }

        logger_->log("%:% %() % ticker:% price:% side:% mkt-price:% agg-trade-ratio:%\n",
                     __FILE__, __LINE__, __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_), ticker_id,
                     Common::priceToString(price).c_str(),
                     Common::sideToString(side).c_str(), mkt_price_, agg_trade_qty_ratio_);
    }

    // ⚡ 成交事件：計算激進成交比率（Aggressive Trade Quantity Ratio）
    // 📌 公式：成交量 / 被動方掛單量
    // 📊 含義：衡量成交的激進程度
    // 範例：買入 80 張 @ Ask(100張) → 比率 = 0.8（非常激進，吃掉大部分流動性）
    //      買入 10 張 @ Ask(500張) → 比率 = 0.02（溫和）
    // 用途: Liquidity Taker 策略可用此判斷是否跟隨趨勢
    auto onTradeUpdate(const Exchange::MEMarketUpdate* market_update,
                       MarketOrderBook* book) noexcept -> void
    {
        const auto bbo = book->getBBO();

        if (LIKELY(bbo->bid_price_ != Price_INVALID &&
                   bbo->ask_price_ != Price_INVALID)) {
            // 📊 計算成交量相對於對手盤掛單量的比率
            // 買單：成交量 / Ask掛單量
            // 賣單：成交量 / Bid掛單量
            agg_trade_qty_ratio_ = static_cast<double>(market_update->qty_) /
                                   (market_update->side_ == Side::BUY ? bbo->ask_qty_ : bbo->bid_qty_);
        }

        logger_->log("%:% %() % % mkt-price:% agg-trade-ratio:%\n", __FILE__, __LINE__,
                     __FUNCTION__,
                     Common::getCurrentTimeStr(&time_str_),
                     market_update->toString().c_str(), mkt_price_, agg_trade_qty_ratio_);
    }

    // 📌 查詢介面：取得當前市場價格
    auto getMktPrice() const noexcept
    {
        return mkt_price_;
    }

    // 📌 查詢介面：取得當前激進成交比率
    auto getAggTradeQtyRatio() const noexcept
    {
        return agg_trade_qty_ratio_;
    }

    /// Deleted default, copy & move constructors and assignment-operators.
    FeatureEngine() = delete;

    FeatureEngine(const FeatureEngine&) = delete;

    FeatureEngine(const FeatureEngine&&) = delete;

    FeatureEngine& operator=(const FeatureEngine&) = delete;

    FeatureEngine& operator=(const FeatureEngine&&) = delete;

private:
    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 📊 特徵儲存：目前實作兩個特徵
    // 1. mkt_price_：公平市場價格（基於掛單量加權）
    // 2. agg_trade_qty_ratio_：激進成交比率（衡量成交強度）
    // ⚠️ 初始值：Feature_INVALID (NaN)，使用前需檢查
    double mkt_price_ = Feature_INVALID, agg_trade_qty_ratio_ = Feature_INVALID;
};
}
