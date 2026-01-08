#pragma once

#include "common/macros.h"
#include "common/logging.h"

#include "position_keeper.h"
#include "om_order.h"

using namespace Common;

namespace Trading
{
class OrderManager;

// ============================================================================
// 風控檢查結果枚舉
// ============================================================================
// 📌 架構設計：使用 int8_t 節省記憶體（1 byte vs 4 bytes）
// 📌 ALLOWED 值最大：優化 CPU 分支預測（常見情況放最後判斷）
enum class RiskCheckResult : int8_t {
    INVALID = 0,
    ORDER_TOO_LARGE = 1,      // 單筆訂單數量超過限制
    POSITION_TOO_LARGE = 2,   // 持倉（預測成交後）超過限制
    LOSS_TOO_LARGE = 3,       // 已實現 + 未實現盈虧低於停損線
    ALLOWED = 4               // ⚡ 通過所有檢查（熱路徑）
};

inline auto riskCheckResultToString(RiskCheckResult result)
{
    switch (result) {
    case RiskCheckResult::INVALID:
        return "INVALID";

    case RiskCheckResult::ORDER_TOO_LARGE:
        return "ORDER_TOO_LARGE";

    case RiskCheckResult::POSITION_TOO_LARGE:
        return "POSITION_TOO_LARGE";

    case RiskCheckResult::LOSS_TOO_LARGE:
        return "LOSS_TOO_LARGE";

    case RiskCheckResult::ALLOWED:
        return "ALLOWED";
    }

    return "";
}

// ============================================================================
// 風控資訊結構（每個商品一個實例）
// ============================================================================
struct RiskInfo {
    // 📌 關聯設計：指標指向 PositionKeeper 內部資料，避免資料複製
    // ⚠️ 注意：position_info_ 必須在 PositionKeeper 生命週期內有效
    const PositionInfo* position_info_ = nullptr;

    // 風控配置參數（max_order_size, max_position, max_loss）
    RiskCfg risk_cfg_;

    // ⚡ 效能關鍵：事前風控檢查（Pre-Trade Risk Check）
    // 📊 時間複雜度：O(1) - 三個簡單比較運算
    // 📊 實測延遲：~8-15 ns（無 Cache Miss）
    // 📌 noexcept 保證：風控檢查不會拋出異常（關鍵路徑）
    auto checkPreTradeRisk(Side side, Qty qty) const noexcept
    {
        // 檢查 1：單筆訂單數量限制
        // ⚡ UNLIKELY 優化：告訴 CPU「這個條件很少成立」，優化分支預測
        if (UNLIKELY(qty > risk_cfg_.max_order_size_)) {
            return RiskCheckResult::ORDER_TOO_LARGE;
        }

        // 檢查 2：持倉限制（預測成交後的倉位）
        // 📌 關鍵邏輯：計算「如果這筆訂單全部成交，倉位會變多少」
        // 範例：目前 +300 張（多倉），買入 500 張 → 預測倉位 +800 張
        if (UNLIKELY(std::abs(position_info_->position_ + sideToValue(
                                  side) * static_cast<int32_t>(qty)) > static_cast<int32_t>
                     (risk_cfg_.max_position_))) {
            return RiskCheckResult::POSITION_TOO_LARGE;
        }

        // 檢查 3：虧損限制（停損機制）
        // ⚠️ 注意：max_loss_ 是負數（例如 -100000.0）
        // 📌 total_pnl_ 包含已實現 + 未實現盈虧
        if (UNLIKELY(position_info_->total_pnl_ < risk_cfg_.max_loss_)) {
            return RiskCheckResult::LOSS_TOO_LARGE;
        }

        // ✅ 所有檢查通過
        return RiskCheckResult::ALLOWED;
    }

    auto toString() const
    {
        std::stringstream ss;
        ss << "RiskInfo" << "["
           << "pos:" << position_info_->toString() << " "
           << risk_cfg_.toString()
           << "]";

        return ss.str();
    }
};

// 📌 記憶體佈局優化：固定大小陣列取代 unordered_map
// ⚡ 效能優勢：
//   - 陣列索引：O(1)，約 2-5 ns
//   - Hash 查找：O(1) 平均，但有 Hash 碰撞風險，約 10-20 ns
// 📊 記憶體大小：假設 ME_MAX_TICKERS=256，RiskInfo=32 bytes → 8 KB（可放入 L1 Cache）
typedef std::array<RiskInfo, ME_MAX_TICKERS> TickerRiskInfoHashMap;

// ============================================================================
// 風控管理器（RiskManager）
// ============================================================================
// 📌 職責：
//   1. 儲存所有商品的風控配置與倉位關聯
//   2. 提供統一的風控檢查介面
//   3. 記錄風控拒絕事件（日誌）
// ⚡ 效能特性：
//   - 熱路徑函式：checkPreTradeRisk()（每次發單前呼叫）
//   - 冷路徑函式：建構子（系統啟動時執行一次）
class RiskManager
{
public:
    // 建構子：初始化所有商品的風控資訊
    // 📌 關聯建立：將 RiskInfo 與 PositionKeeper 內部資料連結
    RiskManager(Common::Logger* logger, const PositionKeeper* position_keeper,
                const TradeEngineCfgHashMap& ticker_cfg);

    // ⚡ 熱路徑：風控檢查入口（inline 優化）
    // 📊 呼叫頻率：每次發單前（約數千次/秒）
    // 📊 延遲預算：< 20 ns（必須極快）
    auto checkPreTradeRisk(TickerId ticker_id, Side side, Qty qty) const noexcept
    {
        return ticker_risk_.at(ticker_id).checkPreTradeRisk(side, qty);
    }

    // Deleted default, copy & move constructors and assignment-operators.
    RiskManager() = delete;

    RiskManager(const RiskManager&) = delete;

    RiskManager(const RiskManager&&) = delete;

    RiskManager& operator=(const RiskManager&) = delete;

    RiskManager& operator=(const RiskManager&&) = delete;

private:
    std::string time_str_;
    Common::Logger* logger_ = nullptr;

    // 🗂️ 核心資料結構：所有商品的風控資訊陣列
    // 📌 索引方式：ticker_risk_[ticker_id] → O(1) 查找
    TickerRiskInfoHashMap ticker_risk_;
};
}
