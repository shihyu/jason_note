#pragma once

#include "common/macros.h"
#include "common/types.h"
#include "common/logging.h"

#include "exchange/order_server/client_response.h"

#include "market_order_book.h"

using namespace Common;

namespace Trading
{
// ============================================================================
// 倉位資訊結構（PositionInfo）
// ============================================================================
// 📌 核心職責：追蹤單一商品的倉位、盈虧、成交量
// ⚡ 關鍵計算：
//   - VWAP（成交量加權平均價）：計算平均成本
//   - Realized PnL：已實現盈虧（平倉確定的盈虧）
//   - Unrealized PnL：未實現盈虧（浮動盈虧，根據市價計算）
struct PositionInfo {
    // 當前持倉：正數=多倉（Long），負數=空倉（Short）
    // 範例：+500 表示持有 500 張多倉，-300 表示持有 300 張空倉
    int32_t position_ = 0;

    double real_pnl_ = 0;    // 已實現盈虧（平倉後確定的盈虧）
    double unreal_pnl_ = 0;  // 未實現盈虧（浮動盈虧）
    double total_pnl_ = 0;   // 總盈虧 = real_pnl_ + unreal_pnl_

    // 📊 VWAP 累計（Volume Weighted Average Price）
    // 📌 設計：分別記錄買方和賣方的累計成交金額
    // open_vwap_[1] = BUY 方向的累計金額（用於計算多倉成本）
    // open_vwap_[2] = SELL 方向的累計金額（用於計算空倉成本）
    // 範例：買入 100@50 + 200@52 → open_vwap_[BUY] = 5000 + 10400 = 15400
    std::array < double, sideToIndex(Side::MAX) + 1 > open_vwap_;

    Qty volume_ = 0;          // 累計成交量（不分買賣方向）
    const BBO* bbo_ = nullptr;  // 📌 指向當前最佳買賣價（用於計算未實現 PnL）

    auto toString() const
    {
        std::stringstream ss;
        ss << "Position{"
           << "pos:" << position_
           << " u-pnl:" << unreal_pnl_
           << " r-pnl:" << real_pnl_
           << " t-pnl:" << total_pnl_
           << " vol:" << qtyToString(volume_)
           << " vwaps:[" << (position_ ? open_vwap_.at(sideToIndex(Side::BUY)) / std::abs(
                                 position_) : 0)
           << "X" << (position_ ? open_vwap_.at(sideToIndex(Side::SELL)) / std::abs(
                          position_) : 0)
           << "] "
           << (bbo_ ? bbo_->toString() : "") << "}";

        return ss.str();
    }

    // ⚡ 效能關鍵：處理成交回報，更新倉位與 PnL
    // 📊 複雜度：O(1) - 固定數量的算術運算
    // ⚠️ 正確性關鍵：必須處理三種情境（開倉/加倉、減倉、倉位翻轉）
    auto addFill(const Exchange::MEClientResponse* client_response,
                 Logger* logger) noexcept
    {
        const auto old_position = position_;
        const auto side_index = sideToIndex(client_response->side_);
        const auto opp_side_index = sideToIndex(client_response->side_ == Side::BUY ?
                                                Side::SELL : Side::BUY);
        const auto side_value = sideToValue(client_response->side_);

        // 更新倉位與成交量
        position_ += client_response->exec_qty_ * side_value;
        volume_ += client_response->exec_qty_;

        // ============================================================================
        // 情境判斷：根據倉位變化方向決定處理邏輯
        // ============================================================================
        // 📌 判斷邏輯：old_position * side_value 的正負號
        //   - >= 0：同向交易（開倉或加倉）
        //   - < 0：反向交易（減倉或翻倉）

        if (old_position * sideToValue(client_response->side_) >= 0) {
            // 情境 1：開倉或加倉（同向交易）
            // 範例：原本 +300 張多倉，又買入 200 張 → 變成 +500 張
            // 📊 VWAP 更新：累加新的成交金額
            // open_vwap_[BUY] += 200 * 52 = 原值 + 10400
            open_vwap_[side_index] += (client_response->price_ *
                                       client_response->exec_qty_);
        } else {
            // 情境 2 & 3：減倉或倉位翻轉（反向交易）
            // 📌 關鍵：需要計算已實現 PnL

            // 計算原倉位的平均成本（VWAP）
            const auto opp_side_vwap = open_vwap_[opp_side_index] / std::abs(old_position);

            // 更新剩餘倉位的 VWAP 累計值
            open_vwap_[opp_side_index] = opp_side_vwap * std::abs(position_);

            // ⚡ 計算已實現 PnL
            // 📌 平倉數量：取「成交數量」與「原持倉數量」的較小值
            // 範例 1（純減倉）：原持倉 +500，賣出 300 → 平倉 300 張
            // 範例 2（翻倉）：原持倉 +200，賣出 500 → 平倉 200 張（剩餘 300 張開新空倉）
            real_pnl_ += std::min(static_cast<int32_t>(client_response->exec_qty_),
                                  std::abs(old_position)) *
                         (opp_side_vwap - client_response->price_) * sideToValue(client_response->side_);

            // 情境 3：倉位翻轉檢測
            // 📌 判斷：新倉位與舊倉位符號相反（一個正一個負）
            // 範例：原本 +200 張多倉，賣出 500 張 → 變成 -300 張空倉
            if (position_ * old_position < 0) {
                // ⚠️ 倉位翻轉處理：
                // 1. 記錄新倉位的 VWAP（未平倉部分的成本）
                // 2. 清空對向的 VWAP（舊倉位已完全平倉）
                open_vwap_[side_index] = (client_response->price_ * std::abs(position_));
                open_vwap_[opp_side_index] = 0;
            }
        }

        // ============================================================================
        // 計算未實現 PnL（使用成交價作為市價估算）
        // ============================================================================
        if (!position_) {
            // 情況：已完全平倉（倉位為 0）
            // ⚠️ 重要：清空所有 VWAP 累計值，避免下次開倉時數據污染
            open_vwap_[sideToIndex(Side::BUY)] = open_vwap_[sideToIndex(Side::SELL)] = 0;
            unreal_pnl_ = 0;
        } else {
            // 情況：仍持有倉位
            // 📌 使用當前成交價作為市價，計算浮動盈虧
            if (position_ > 0) {
                // 多倉未實現 PnL = (當前價 - 成本價) * 持倉數量
                // 範例：持有 +500 張，成本 50.5，當前價 53
                //      unreal_pnl = (53 - 50.5) * 500 = +1250
                unreal_pnl_ =
                    (client_response->price_ - open_vwap_[sideToIndex(Side::BUY)] / std::abs(
                         position_)) *
                    std::abs(position_);
            } else {
                // 空倉未實現 PnL = (成本價 - 當前價) * 持倉數量
                // 範例：持有 -300 張，成本 54，當前價 52
                //      unreal_pnl = (54 - 52) * 300 = +600
                unreal_pnl_ =
                    (open_vwap_[sideToIndex(Side::SELL)] / std::abs(position_) -
                     client_response->price_) *
                    std::abs(position_);
            }
        }

        // 更新總盈虧
        total_pnl_ = unreal_pnl_ + real_pnl_;

        // 記錄日誌（非熱路徑，Lock-Free Queue 異步寫入）
        std::string time_str;
        logger->log("%:% %() % % %\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str),
                    toString(), client_response->toString().c_str());
    }

    // ⚡ 市場行情更新：根據最新 BBO 重新計算未實現 PnL
    // 📊 呼叫頻率：每次行情變動（約數千次/秒）
    // 📌 設計：使用中間價（Mid Price）計算浮動盈虧
    auto updateBBO(const BBO* bbo, Logger* logger) noexcept
    {
        std::string time_str;
        bbo_ = bbo;  // 更新 BBO 指標

        // ⚠️ 前置條件檢查：
        // 1. 必須持有倉位（position_ != 0）
        // 2. BBO 價格必須有效（非 Price_INVALID）
        if (position_ && bbo->bid_price_ != Price_INVALID &&
            bbo->ask_price_ != Price_INVALID) {

            // 📊 計算中間價（業界標準做法）
            // 📌 為什麼用中間價？
            //   - Bid 價低估多倉盈利
            //   - Ask 價低估空倉盈利
            //   - Mid 價公平且符合會計準則
            const auto mid_price = (bbo->bid_price_ + bbo->ask_price_) * 0.5;

            if (position_ > 0) {
                // 多倉未實現 PnL = (中間價 - 成本價) * 持倉數量
                unreal_pnl_ =
                    (mid_price - open_vwap_[sideToIndex(Side::BUY)] / std::abs(position_)) *
                    std::abs(position_);
            } else {
                // 空倉未實現 PnL = (成本價 - 中間價) * 持倉數量
                unreal_pnl_ =
                    (open_vwap_[sideToIndex(Side::SELL)] / std::abs(position_) - mid_price) *
                    std::abs(position_);
            }

            const auto old_total_pnl = total_pnl_;
            total_pnl_ = unreal_pnl_ + real_pnl_;

            // ⚡ 優化：只有總盈虧改變時才記錄日誌（減少日誌量）
            if (total_pnl_ != old_total_pnl)
                logger->log("%:% %() % % %\n", __FILE__, __LINE__, __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str),
                            toString(), bbo_->toString());
        }
    }
};

// ============================================================================
// 倉位追蹤器（PositionKeeper）
// ============================================================================
// 📌 核心職責：
//   1. 管理所有商品的倉位資訊（PositionInfo 陣列）
//   2. 處理成交回報（addFill）
//   3. 更新市場行情（updateBBO）
//   4. 提供倉位資訊給 RiskManager 使用
// ⚡ 效能特性：
//   - 固定大小陣列（無動態分配）
//   - Cache-Friendly 記憶體佈局
//   - 單執行緒操作（無鎖設計）
class PositionKeeper
{
public:
    PositionKeeper(Common::Logger* logger)
        : logger_(logger)
    {
    }

    // Deleted default, copy & move constructors and assignment-operators.
    PositionKeeper() = delete;

    PositionKeeper(const PositionKeeper&) = delete;

    PositionKeeper(const PositionKeeper&&) = delete;

    PositionKeeper& operator=(const PositionKeeper&) = delete;

    PositionKeeper& operator=(const PositionKeeper&&) = delete;

private:
    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 🗂️ 核心資料結構：所有商品的倉位資訊陣列
    // 📌 索引方式：ticker_position_[ticker_id] → O(1) 查找
    // 📊 記憶體大小：假設 ME_MAX_TICKERS=256，PositionInfo≈100 bytes → 25 KB
    std::array<PositionInfo, ME_MAX_TICKERS> ticker_position_;

public:
    // ⚡ 熱路徑：處理成交回報
    // 📊 呼叫頻率：每次成交（約數百到數千次/秒）
    auto addFill(const Exchange::MEClientResponse* client_response) noexcept
    {
        ticker_position_.at(client_response->ticker_id_).addFill(client_response,
                logger_);
    }

    // ⚡ 熱路徑：更新市場行情
    // 📊 呼叫頻率：每次行情變動（約數千次/秒）
    auto updateBBO(TickerId ticker_id, const BBO* bbo) noexcept
    {
        ticker_position_.at(ticker_id).updateBBO(bbo, logger_);
    }

    // 📌 關鍵介面：提供倉位資訊指標給 RiskManager
    // ⚠️ 注意：返回指標而非複製，保證資料一致性
    auto getPositionInfo(TickerId ticker_id) const noexcept
    {
        return &(ticker_position_.at(ticker_id));
    }

    auto toString() const
    {
        double total_pnl = 0;
        Qty total_vol = 0;

        std::stringstream ss;

        for (TickerId i = 0; i < ticker_position_.size(); ++i) {
            ss << "TickerId:" << tickerIdToString(i) << " " << ticker_position_.at(
                   i).toString() << "\n";

            total_pnl += ticker_position_.at(i).total_pnl_;
            total_vol += ticker_position_.at(i).volume_;
        }

        ss << "Total PnL:" << total_pnl << " Vol:" << total_vol << "\n";

        return ss.str();
    }
};
}
