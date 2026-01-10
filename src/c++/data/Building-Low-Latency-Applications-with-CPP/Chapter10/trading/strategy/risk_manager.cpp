#include "risk_manager.h"

#include "order_manager.h"

namespace Trading
{
// ============================================================================
// RiskManager 建構子
// ============================================================================
//
// 📌 功能：初始化風控管理器，建立倉位追蹤與風控配置的關聯
//
// 初始化流程：
// 1. 儲存日誌記錄器指標
// 2. 遍歷所有交易標的（ME_MAX_TICKERS）
// 3. 為每個標的建立指標關聯（position_info_）
// 4. 載入風控限制配置（risk_cfg_）
//
// ⚡ 效能設計：
// - 編譯期迴圈展開：ME_MAX_TICKERS 為編譯期常數
// - 指標共享：position_info_ 指向 PositionKeeper 內部資料
// - 配置複製：risk_cfg_ 複製一份，避免外部修改影響
//
// 🔗 關聯設計：
// - 不複製 PositionInfo：使用指標共享（即時取得最新倉位）
// - PositionKeeper 必須在 RiskManager 生命週期內有效
// - 風控檢查時直接存取 position_info_（零延遲）
//
// 📊 風控參數：
// - max_order_size_：單筆訂單最大數量
// - max_position_：最大持倉數量（絕對值）
// - max_loss_：最大虧損限制（負數）
//
// ⚠️ 注意事項：
// - PositionKeeper 必須先於 RiskManager 初始化
// - position_info_ 指標有效性由外部保證
// - 風控配置在初始化後不可動態修改
//
// @param logger: 日誌記錄器指標
// @param position_keeper: 倉位追蹤器（唯讀參考）
// @param ticker_cfg: 交易標的配置表（包含風控參數）
RiskManager::RiskManager(Common::Logger* logger,
                         const PositionKeeper* position_keeper, const TradeEngineCfgHashMap& ticker_cfg)
    : logger_(logger)
{
    // 為所有交易標的初始化風控配置
    // ⚡ 迴圈展開：編譯器會將此迴圈完全展開為直接賦值
    for (TickerId i = 0; i < ME_MAX_TICKERS; ++i) {
        // 關聯倉位資訊（指標共享，即時取得最新倉位狀態）
        ticker_risk_.at(i).position_info_ = position_keeper->getPositionInfo(i);

        // 載入風控限制（複製配置，避免外部修改影響）
        ticker_risk_.at(i).risk_cfg_ = ticker_cfg[i].risk_cfg_;
    }
}
}
