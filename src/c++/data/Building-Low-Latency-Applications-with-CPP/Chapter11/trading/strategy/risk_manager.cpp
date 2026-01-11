/**
 * @file risk_manager.cpp
 * @brief 風控管理器實作檔案 - 風控初始化與配置
 *
 * 功能：
 * - 實作 RiskManager 建構函式
 * - 初始化所有商品的風險資訊（RiskInfo）
 * - 連結倉位追蹤器（PositionKeeper）
 * - 載入風控配置（RiskCfg）
 *
 * 實作細節：
 * - 遍歷所有商品（0 到 ME_MAX_TICKERS-1）
 * - 為每個商品設定倉位資訊指標
 * - 為每個商品載入風控配置
 *
 * 設計考量：
 * - 初始化時一次性設定，執行時不修改
 * - 使用指標引用 PositionKeeper 的倉位資訊（避免複製）
 * - 風控配置從 TradeEngineCfgHashMap 複製（獨立配置）
 *
 * 效能特性：
 * - 初始化時間：O(ME_MAX_TICKERS)
 * - 無動態記憶體分配（使用預分配陣列）
 */

#include "risk_manager.h"

#include "order_manager.h"

namespace Trading
{
/**
 * RiskManager 建構函式 - 初始化風控管理器
 *
 * @param logger 日誌記錄器
 * @param position_keeper 倉位追蹤器（提供倉位資訊）
 * @param ticker_cfg 商品配置（包含風控參數）
 *
 * 實作邏輯：
 * 1. 設定日誌記錄器
 * 2. 遍歷所有商品（0 到 ME_MAX_TICKERS-1）
 * 3. 為每個商品初始化 RiskInfo：
 *    - position_info_：指向 PositionKeeper 的倉位資訊
 *      * 使用 getPositionInfo(i) 獲取倉位資訊指標
 *      * 倉位資訊由 PositionKeeper 維護，RiskManager 只讀取
 *
 *    - risk_cfg_：從 ticker_cfg 載入風控配置
 *      * max_order_size_：單筆訂單數量上限
 *      * max_position_：倉位上限（多頭或空頭）
 *      * max_loss_：最大虧損（負數，例如 -10000）
 *
 * 初始化後狀態：
 * - ticker_risk_ 陣列完全初始化
 * - 每個商品有獨立的風控配置
 * - 倉位資訊指標連結到 PositionKeeper
 *
 * 注意事項：
 * - position_info_ 是指標，指向 PositionKeeper 維護的倉位
 * - PositionKeeper 更新倉位時，RiskManager 自動看到最新值
 * - risk_cfg_ 是值複製，修改不影響 ticker_cfg
 */
RiskManager::RiskManager(Common::Logger* logger,
                         const PositionKeeper* position_keeper, const TradeEngineCfgHashMap& ticker_cfg)
    : logger_(logger)
{
    // 遍歷所有商品，初始化風險資訊
    for (TickerId i = 0; i < ME_MAX_TICKERS; ++i) {
        // 連結倉位追蹤器的倉位資訊（使用指標，避免複製）
        ticker_risk_.at(i).position_info_ = position_keeper->getPositionInfo(i);

        // 載入風控配置（從商品配置中複製）
        ticker_risk_.at(i).risk_cfg_ = ticker_cfg[i].risk_cfg_;
    }
}
}
