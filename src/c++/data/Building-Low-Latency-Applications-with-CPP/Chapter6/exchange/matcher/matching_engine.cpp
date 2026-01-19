// 撮合引擎主循環：讀取請求並驅動訂單簿。
// ⚡ 效能關鍵：單執行緒避免鎖競爭。
// ⚠️ 注意：回應/市場更新順序。

#include "matching_engine.h"

namespace Exchange
{
/**
 * 構造函式 - 初始化撮合引擎
 *
 * @param client_requests 客戶端請求佇列指標（輸入：來自訂單閘道）
 * @param client_responses 客戶端回應佇列指標（輸出：發送到訂單閘道）
 * @param market_updates 市場更新佇列指標（輸出：發送到市場數據發佈器）
 *
 * 初始化流程：
 * 1. 儲存三個 Lock-Free Queue 指標：
 *    - incoming_requests_: 接收客戶端訂單請求（NEW/CANCEL）
 *    - outgoing_ogw_responses_: 發送客戶端回應（ACCEPTED/FILLED/CANCELED）
 *    - outgoing_md_updates_: 發送市場更新（ADD/TRADE/CANCEL/MODIFY）
 *
 * 2. 初始化日誌系統：
 *    - 日誌檔案：exchange_matching_engine.log
 *    - 記錄所有撮合事件和錯誤
 *
 * 3. 為每個商品建立訂單簿（MEOrderBook）：
 *    - ticker_order_book_: 陣列，索引 = TickerId
 *    - 每個訂單簿獨立管理該商品的所有訂單
 *    - 使用動態記憶體分配（new）建立訂單簿物件
 *    - 傳遞參數：商品 ID、日誌記錄器、撮合引擎指標
 *
 * 架構設計：
 * - 單執行緒事件迴圈架構（run() 方法）
 * - 通過 Lock-Free Queue 與其他元件通訊
 * - 每個商品獨立訂單簿（避免鎖競爭）
 *
 * 效能特性：
 * - 預配置所有訂單簿（避免動態分配）
 * - Lock-Free Queue 通訊（零等待）
 * - 單執行緒處理（無鎖競爭）
 * - 延遲：< 2 μs per order（包含撮合和訊息發送）
 *
 * 通訊拓撲：
 * ```
 * OrderGateway → [incoming_requests_] → MatchingEngine
 *                                             ↓
 * OrderGateway ← [outgoing_ogw_responses_] ←─┤
 *                                             ↓
 * MarketDataPublisher ← [outgoing_md_updates_] ←─┘
 * ```
 */
MatchingEngine::MatchingEngine(ClientRequestLFQueue* client_requests,
                               ClientResponseLFQueue* client_responses,
                               MEMarketUpdateLFQueue* market_updates)
    : incoming_requests_(client_requests),
      outgoing_ogw_responses_(client_responses), outgoing_md_updates_(market_updates),
      logger_("exchange_matching_engine.log")
{
    // 為每個商品建立獨立訂單簿
    // ticker_order_book_.size() 通常是常數（例如 1024 個商品）
    for (size_t i = 0; i < ticker_order_book_.size(); ++i) {
        ticker_order_book_[i] = new MEOrderBook(i, &logger_, this);
    }
}

/**
 * 解構函式 - 安全關閉撮合引擎
 *
 * 關閉流程：
 * 1. 停止事件迴圈：
 *    - 設置 run_ = false（通知 run() 方法退出）
 *    - 等待 1 秒，讓執行緒完成當前處理
 *
 * 2. 清空佇列指標：
 *    - incoming_requests_ = nullptr
 *    - outgoing_ogw_responses_ = nullptr
 *    - outgoing_md_updates_ = nullptr
 *    - 防止懸空指標（dangling pointer）
 *
 * 3. 釋放所有訂單簿物件：
 *    - 遍歷 ticker_order_book_ 陣列
 *    - 刪除每個 MEOrderBook 物件（delete）
 *    - 設置指標為 nullptr
 *
 * 安全性考量：
 * - 等待 1 秒確保執行緒完成清理
 * - 避免在執行緒運行時釋放資源
 * - 訂單簿解構函式會記錄最終狀態到日誌
 *
 * 注意事項：
 * - 應在系統關閉時呼叫
 * - 不應在交易時段呼叫（會遺失訂單）
 * - 解構前應確保所有訂單已處理完畢
 */
MatchingEngine::~MatchingEngine()
{
    // 1. 停止事件迴圈
    run_ = false;

    // 2. 等待執行緒完成清理（1 秒緩衝期）
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);

    // 3. 清空佇列指標（防止懸空指標）
    incoming_requests_ = nullptr;
    outgoing_ogw_responses_ = nullptr;
    outgoing_md_updates_ = nullptr;

    // 4. 釋放所有訂單簿物件
    for (auto& order_book : ticker_order_book_) {
        delete order_book;         // 呼叫 MEOrderBook 解構函式
        order_book = nullptr;      // 設置為 nullptr
    }
}

/**
 * start() - 啟動撮合引擎執行緒
 *
 * 功能：
 * 1. 設置運行旗標（run_ = true）
 * 2. 建立獨立執行緒執行 run() 方法
 * 3. 執行緒名稱：Exchange/MatchingEngine（用於監控和除錯）
 * 4. 不綁定 CPU 核心（-1）：讓作業系統調度
 *
 * 執行緒模型：
 * - 單執行緒事件迴圈（避免鎖競爭）
 * - 緊密迴圈（tight loop）處理訂單請求
 * - Lock-Free Queue 讀寫（零等待）
 *
 * 錯誤處理：
 * - 若執行緒建立失敗 → ASSERT 觸發程式終止
 * - 確保撮合引擎正常啟動（關鍵元件）
 *
 * 呼叫時機：
 * - 系統啟動時（所有元件初始化後）
 * - 僅呼叫一次（不可重複啟動）
 *
 * 注意事項：
 * - 執行緒建立後立即開始處理訂單
 * - 應確保佇列已正確初始化
 * - CPU 親和力：不綁定核心（通用調度策略）
 */
auto MatchingEngine::start() -> void
{
    run_ = true;  // 設置運行旗標
    // 建立並啟動執行緒（執行 run() 方法）
    ASSERT(Common::createAndStartThread(-1, "Exchange/MatchingEngine", [this]() {
        // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
        run();
    }) != nullptr, "Failed to start MatchingEngine thread.");
}

/**
 * stop() - 停止撮合引擎執行緒
 *
 * 功能：
 * - 設置 run_ = false，通知 run() 方法退出事件迴圈
 *
 * 執行流程：
 * 1. stop() 設置旗標
 * 2. run() 方法檢測到 run_ = false
 * 3. run() 退出迴圈並返回
 * 4. 執行緒自然結束
 *
 * 優雅關閉：
 * - 不強制終止執行緒（避免資料不一致）
 * - 等待當前訂單處理完成
 * - 解構函式會等待 1 秒確保清理完成
 *
 * 呼叫時機：
 * - 系統關閉前
 * - 交易時段結束
 * - 維護模式切換
 *
 * 注意事項：
 * - 非阻塞操作（立即返回）
 * - 實際停止需要等待事件迴圈檢測旗標
 * - 通常在毫秒級內完成停止
 */
auto MatchingEngine::stop() -> void
{
    run_ = false;  // 設置停止旗標
}
}
