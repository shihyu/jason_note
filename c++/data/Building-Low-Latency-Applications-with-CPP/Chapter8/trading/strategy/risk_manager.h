/**
 * @file risk_manager.h
 * @brief 風控管理器標頭檔 - 交易前風險檢查
 *
 * 功能：
 * - 下單前風險檢查（訂單大小、倉位限制、虧損限制）
 * - 即時倉位追蹤與風險評估
 * - 風險配置管理（每個商品獨立配置）
 * - 風險檢查結果分類與日誌記錄
 *
 * 風險檢查項目：
 * 1. ORDER_TOO_LARGE：單筆訂單數量超過上限
 * 2. POSITION_TOO_LARGE：下單後倉位會超過上限
 * 3. LOSS_TOO_LARGE：累計虧損超過上限
 * 4. ALLOWED：通過所有風險檢查
 *
 * 架構位置：
 * - RiskManager：風控管理器（本地風險檢查）
 * - PositionKeeper：倉位追蹤器（維護當前倉位和 PnL）
 * - OrderManager：訂單管理器（下單前調用風控檢查）
 *
 * 設計模式：
 * - 策略模式：不同風險檢查規則封裝在 checkPreTradeRisk()
 * - 組合模式：每個商品有獨立的 RiskInfo
 * - 不可變模式：風控配置在建構時設定，運行時不修改
 *
 * 使用場景：
 * 1. 做市商策略：檢查雙邊報價是否違反風控
 * 2. 流動性接盤：檢查主動吃單是否違反倉位限制
 * 3. 即時監控：記錄所有風控檢查結果
 *
 * 效能特性：
 * - 所有檢查方法標記 noexcept（無例外拋出）
 * - 使用預先分配的陣列（ME_MAX_TICKERS）
 * - O(1) 風險檢查（直接訪問陣列元素）
 * - 使用 UNLIKELY 宏優化分支預測
 *
 * 注意事項：
 * - 風控檢查不會修改任何狀態（只讀操作）
 * - 檢查結果僅作為建議，最終決策由 OrderManager 執行
 * - 虧損限制檢查基於 total_pnl_（已實現 + 未實現盈虧）
 */

#pragma once

#include "common/macros.h"
#include "common/logging.h"

#include "position_keeper.h"
#include "om_order.h"

using namespace Common;

namespace Trading
{
class OrderManager;

/**
 * @enum RiskCheckResult
 * @brief 風險檢查結果枚舉
 *
 * 結果優先級（由高到低）：
 * 1. ORDER_TOO_LARGE - 訂單過大（最高優先級）
 * 2. POSITION_TOO_LARGE - 倉位過大
 * 3. LOSS_TOO_LARGE - 虧損過大
 * 4. ALLOWED - 通過檢查
 *
 * 使用方式：
 * - 風控檢查按順序執行，遇到第一個失敗項立即返回
 * - ALLOWED 表示通過所有檢查，可以下單
 */
enum class RiskCheckResult : int8_t {
    INVALID = 0,              ///< 無效結果（未初始化）
    ORDER_TOO_LARGE = 1,      ///< 單筆訂單數量超過上限
    POSITION_TOO_LARGE = 2,   ///< 下單後倉位會超過上限
    LOSS_TOO_LARGE = 3,       ///< 累計虧損超過上限
    ALLOWED = 4               ///< 通過所有風險檢查
};

/**
 * riskCheckResultToString() - 將風險檢查結果轉換為字串
 *
 * @param result 風險檢查結果
 * @return 結果的字串表示
 *
 * 使用場景：
 * - 日誌記錄風控拒絕原因
 * - 監控介面顯示風控狀態
 * - 除錯和審計
 */
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

/**
 * @struct RiskInfo
 * @brief 風險資訊結構 - 每個商品的風控狀態
 *
 * 組成：
 * - position_info_：當前倉位資訊（來自 PositionKeeper）
 * - risk_cfg_：風控配置（訂單上限、倉位上限、虧損上限）
 *
 * 職責：
 * - 封裝單個商品的風控檢查邏輯
 * - 整合倉位資訊和風控配置
 * - 提供下單前風險檢查方法
 *
 * 設計理由：
 * - 每個商品獨立配置風控參數
 * - 倉位資訊只讀引用（避免複製）
 * - 風控邏輯集中在一處，便於維護
 *
 * 使用方式：
 * - RiskManager 維護 ME_MAX_TICKERS 個 RiskInfo
 * - 每次下單前調用 checkPreTradeRisk()
 */
struct RiskInfo {
    /// 倉位資訊指標（指向 PositionKeeper 維護的倉位）
    const PositionInfo* position_info_ = nullptr;

    /// 風控配置（訂單上限、倉位上限、虧損上限）
    RiskCfg risk_cfg_;

    /**
     * checkPreTradeRisk() - 下單前風險檢查
     *
     * @param side 買賣方向（BUY/SELL）
     * @param qty 訂單數量
     * @return 風險檢查結果（ALLOWED 或拒絕原因）
     *
     * 檢查項目（按順序）：
     *
     * 1. 訂單大小檢查：
     *    - 條件：qty > max_order_size_
     *    - 失敗：ORDER_TOO_LARGE
     *
     * 2. 倉位限制檢查：
     *    - 計算下單後倉位：current_position + side_value * qty
     *    - 條件：abs(new_position) > max_position_
     *    - 失敗：POSITION_TOO_LARGE
     *    - 範例：
     *      * 當前倉位 = +100（多頭）
     *      * 下單 BUY 200 → 新倉位 = +300
     *      * 若 max_position_ = 250 → POSITION_TOO_LARGE
     *
     * 3. 虧損限制檢查：
     *    - 條件：total_pnl_ < max_loss_（注意：max_loss_ 是負數）
     *    - 失敗：LOSS_TOO_LARGE
     *    - 範例：
     *      * total_pnl_ = -150（虧損 150）
     *      * max_loss_ = -100（允許最多虧損 100）
     *      * -150 < -100 → LOSS_TOO_LARGE
     *
     * 效能優化：
     * - 使用 UNLIKELY 宏標記失敗分支（大多數情況下檢查通過）
     * - 短路求值：第一個失敗項立即返回
     * - noexcept：不拋出例外
     *
     * 注意事項：
     * - 方向值轉換：BUY = +1, SELL = -1（sideToValue）
     * - 倉位計算包含方向性（多頭為正，空頭為負）
     * - max_loss_ 應設為負數（例如 -10000 表示允許虧損 10000）
     */
    auto checkPreTradeRisk(Side side, Qty qty) const noexcept
    {
        // 1. 檢查訂單大小（單筆訂單數量上限）
        if (UNLIKELY(qty > risk_cfg_.max_order_size_)) {
            return RiskCheckResult::ORDER_TOO_LARGE;
        }

        // 2. 檢查倉位限制（計算下單後倉位是否超限）
        // 計算公式：new_position = current_position + side_value * qty
        // BUY: side_value = +1, SELL: side_value = -1
        if (UNLIKELY(std::abs(position_info_->position_ + sideToValue(
                                  side) * static_cast<int32_t>(qty)) > static_cast<int32_t>
                     (risk_cfg_.max_position_))) {
            return RiskCheckResult::POSITION_TOO_LARGE;
        }

        // 3. 檢查虧損限制（累計 PnL 是否超過最大虧損）
        // max_loss_ 是負數（例如 -10000 表示最多虧損 10000）
        if (UNLIKELY(position_info_->total_pnl_ < risk_cfg_.max_loss_)) {
            return RiskCheckResult::LOSS_TOO_LARGE;
        }

        // 通過所有檢查
        return RiskCheckResult::ALLOWED;
    }

    /**
     * toString() - 將風險資訊轉換為字串
     *
     * @return 風險資訊的字串表示
     *
     * 輸出格式：
     * ```
     * RiskInfo[pos:PositionInfo[...] RiskCfg[...]]
     * ```
     *
     * 使用場景：
     * - 日誌記錄風控狀態
     * - 監控介面顯示風險資訊
     * - 除錯和審計
     */
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

/// 商品風險資訊哈希表（每個商品一個 RiskInfo）
typedef std::array<RiskInfo, ME_MAX_TICKERS> TickerRiskInfoHashMap;

/**
 * @class RiskManager
 * @brief 風控管理器 - 管理所有商品的風險檢查
 *
 * 核心職責：
 * 1. 維護每個商品的風險資訊（RiskInfo）
 * 2. 提供下單前風險檢查接口
 * 3. 整合倉位追蹤器（PositionKeeper）和風控配置
 * 4. 記錄所有風控檢查結果（日誌）
 *
 * 數據結構：
 * - ticker_risk_：陣列，索引為 ticker_id，值為 RiskInfo
 * - 每個 RiskInfo 包含：
 *   * position_info_：指向 PositionKeeper 的倉位資訊
 *   * risk_cfg_：該商品的風控配置
 *
 * 工作流程：
 * 1. 建構時：初始化所有商品的 RiskInfo
 *    - 連結 PositionKeeper 的倉位資訊
 *    - 載入風控配置
 *
 * 2. 執行時：OrderManager 下單前調用 checkPreTradeRisk()
 *    - 查找對應商品的 RiskInfo
 *    - 執行風險檢查
 *    - 返回檢查結果
 *
 * 設計模式：
 * - 單例模式：每個 TradeEngine 只有一個 RiskManager
 * - 委託模式：將風控邏輯委託給 RiskInfo
 * - 不可變模式：建構後風控配置不變
 *
 * 效能特性：
 * - O(1) 風險檢查（陣列索引訪問）
 * - 無動態記憶體分配（預先分配陣列）
 * - noexcept 方法（無例外拋出）
 *
 * 注意事項：
 * - 風控檢查只讀，不修改任何狀態
 * - 倉位資訊由 PositionKeeper 更新，RiskManager 只讀取
 * - 風控配置在建構時載入，執行時不可修改
 */
class RiskManager
{
public:
    /**
     * @brief 建構函式 - 初始化風控管理器
     *
     * @param logger 日誌記錄器
     * @param position_keeper 倉位追蹤器（提供倉位資訊）
     * @param ticker_cfg 商品配置（包含風控參數）
     *
     * 初始化流程：
     * 1. 遍歷所有商品（0 到 ME_MAX_TICKERS-1）
     * 2. 為每個商品設定 RiskInfo：
     *    - position_info_：指向 PositionKeeper 的倉位資訊
     *    - risk_cfg_：從 ticker_cfg 載入風控配置
     *
     * @see risk_manager.cpp 實作細節
     */
    RiskManager(Common::Logger* logger, const PositionKeeper* position_keeper,
                const TradeEngineCfgHashMap& ticker_cfg);

    /**
     * checkPreTradeRisk() - 下單前風險檢查（主要接口）
     *
     * @param ticker_id 商品識別碼
     * @param side 買賣方向（BUY/SELL）
     * @param qty 訂單數量
     * @return 風險檢查結果（ALLOWED 或拒絕原因）
     *
     * 實作邏輯：
     * - 查找對應商品的 RiskInfo
     * - 委託給 RiskInfo::checkPreTradeRisk()
     *
     * 使用場景：
     * - OrderManager::moveOrder() 下單前調用
     * - 返回 ALLOWED 才允許發送訂單
     * - 返回其他結果則記錄日誌並拒絕下單
     *
     * 效能特性：
     * - noexcept：不拋出例外
     * - O(1) 查找：直接訪問陣列元素
     * - inline：編譯器可能內聯此方法
     */
    auto checkPreTradeRisk(TickerId ticker_id, Side side, Qty qty) const noexcept
    {
        return ticker_risk_.at(ticker_id).checkPreTradeRisk(side, qty);
    }

    // Deleted default, copy & move constructors and assignment-operators.
    // 刪除預設建構、複製與移動建構函式及賦值運算子
    // 理由：RiskManager 應單例存在於 TradeEngine 中，避免意外複製
    RiskManager() = delete;

    RiskManager(const RiskManager&) = delete;

    RiskManager(const RiskManager&&) = delete;

    RiskManager& operator=(const RiskManager&) = delete;

    RiskManager& operator=(const RiskManager&&) = delete;

private:
    /// 時間字串緩衝區（避免每次格式化時分配記憶體）
    std::string time_str_;

    /// 日誌記錄器（記錄所有風控檢查結果）
    Common::Logger* logger_ = nullptr;

    /**
     * ticker_risk_ - 商品風險資訊陣列
     *
     * 結構：
     * - 陣列大小：ME_MAX_TICKERS
     * - 索引：ticker_id
     * - 值：RiskInfo（倉位資訊 + 風控配置）
     *
     * 初始化：
     * - 建構函式中為每個商品設定 RiskInfo
     * - 連結 PositionKeeper 的倉位資訊
     * - 載入風控配置
     *
     * 訪問方式：
     * - ticker_risk_.at(ticker_id) 獲取指定商品的 RiskInfo
     */
    TickerRiskInfoHashMap ticker_risk_;
};
}
