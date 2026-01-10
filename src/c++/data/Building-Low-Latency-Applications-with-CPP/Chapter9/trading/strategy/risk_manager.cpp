#include "risk_manager.h"

#include "order_manager.h"

namespace Trading
{
// RiskManager 建構子
//
// 初始化流程：
// 1. 為每個交易標的（ticker）初始化風控配置
// 2. 關聯倉位資訊：從 PositionKeeper 取得當前倉位指標（指標共享，不複製）
// 3. 載入風控參數：從交易引擎配置中提取風控限制
//
// ⚡ 效能考量：
// - 初始化時一次性載入所有配置，避免執行時查找
// - 使用指標共享（position_info_）避免資料複製
// - 編譯期常數迴圈（ME_MAX_TICKERS=8）會被完全展開
//
// @param logger: 日誌記錄器
// @param position_keeper: 倉位追蹤器（唯讀參考，共享倉位資訊）
// @param ticker_cfg: 交易標的配置表（包含風控參數）
RiskManager::RiskManager(Common::Logger* logger,
                         const PositionKeeper* position_keeper, const TradeEngineCfgHashMap& ticker_cfg)
    : logger_(logger)
{
    // 為所有交易標的初始化風控配置
    // ⚡ 迴圈展開：編譯器會將此迴圈完全展開為 8 次直接賦值
    for (TickerId i = 0; i < ME_MAX_TICKERS; ++i) {
        // 關聯倉位資訊（指標共享，即時取得最新倉位狀態）
        ticker_risk_.at(i).position_info_ = position_keeper->getPositionInfo(i);

        // 載入風控限制（複製配置，避免外部修改影響）
        ticker_risk_.at(i).risk_cfg_ = ticker_cfg[i].risk_cfg_;
    }
}
}
