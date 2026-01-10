// market_data_publisher.cpp: 行情發布系統實作
//
// 職責：
// - 接收來自撮合引擎的市場更新（Market Updates）
// - 透過雙路徑發布機制廣播給訂閱者：
//   1. 增量更新路徑（Incremental Updates）：即時串流（UDP Multicast）
//   2. 快照路徑（Snapshot）：週期性完整狀態（TCP/UDP）
// - 管理序列號（Sequence Number），讓客戶端偵測封包遺失
//
// 架構設計：
// - 生產者：撮合引擎（MatchingEngine）寫入 Lock-Free Queue
// - 消費者：本元件從 Lock-Free Queue 讀取並廣播
// - 零拷貝設計：指標共享，避免記憶體複製
//
// ⚡ 低延遲關鍵：
// - Lock-Free Queue：無鎖佇列，避免執行緒同步開銷
// - UDP Multicast：單次發送，多個訂閱者同時接收
// - 批次處理：一次迴圈處理多個更新，減少 syscall 開銷

#include "market_data_publisher.h"

namespace Exchange
{
// MarketDataPublisher 建構子
//
// 初始化流程：
// 1. 關聯輸入佇列：從撮合引擎接收市場更新（指標共享，不複製）
// 2. 創建內部快照佇列：用於轉發給 SnapshotSynthesizer
// 3. 初始化 Incremental Socket：設定 UDP Multicast 通道
// 4. 創建 SnapshotSynthesizer：負責合成完整市場快照
//
// 雙佇列設計原理：
// - outgoing_md_updates_：外部佇列（來自撮合引擎）
// - snapshot_md_updates_：內部佇列（轉發給快照合成器）
// - 分離關注點：增量發布 vs. 快照合成
//
// ⚡ 效能考量：
// - 指標共享：outgoing_md_updates_ 不複製資料
// - 固定大小佇列：snapshot_md_updates_ 預配置 ME_MAX_MARKET_UPDATES 個元素
// - 非監聽模式：incremental_socket_ 只發送，不接收（is_listening=false）
//
// @param market_updates: 來自撮合引擎的市場更新佇列（外部佇列）
// @param iface: 網路介面名稱（例如 "eth0"）
// @param snapshot_ip: 快照服務 IP（TCP 或 UDP）
// @param snapshot_port: 快照服務 Port
// @param incremental_ip: 增量更新 Multicast 群組 IP
// @param incremental_port: 增量更新 Multicast Port
MarketDataPublisher::MarketDataPublisher(MEMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port,
        const std::string& incremental_ip, int incremental_port)
    : outgoing_md_updates_(market_updates),               // 外部佇列（指標共享）
      snapshot_md_updates_(ME_MAX_MARKET_UPDATES),        // 內部佇列（固定大小）
      run_(false),                                        // 執行標誌（初始為 false）
      logger_("exchange_market_data_publisher.log"),      // 日誌系統
      incremental_socket_(logger_)                        // UDP Multicast Socket
{
    // 初始化 Incremental Socket（UDP Multicast）
    // ⚡ 非監聽模式（is_listening=false）：只發送，不接收
    // ⚠️ 失敗時中止程式：ASSERT 確保網路通道正常
    ASSERT(incremental_socket_.init(incremental_ip, iface,
                                    incremental_port, /*is_listening*/ false) >= 0,
           "Unable to create incremental mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 創建 SnapshotSynthesizer（快照合成器）
    // - 輸入：snapshot_md_updates_ 佇列（本元件轉發）
    // - 輸出：完整市場快照（週期性發布）
    // ⚡ 動態配置：使用 new 創建（由解構子負責釋放）
    snapshot_synthesizer_ = new SnapshotSynthesizer(&snapshot_md_updates_, iface,
            snapshot_ip, snapshot_port);
}

// run: 主事件迴圈 - 行情發布核心邏輯
//
// 執行流程：
// 1. 從 Lock-Free Queue 讀取市場更新（批次處理）
// 2. 透過 UDP Multicast 廣播增量更新（序列號 + 資料）
// 3. 轉發到快照佇列，供 SnapshotSynthesizer 使用
// 4. 更新序列號（遞增）
// 5. 呼叫 sendAndRecv() 刷新 Socket 緩衝區
//
// 雙路徑發布機制：
// ┌────────────────┐
// │ MatchingEngine │
// └───────┬────────┘
//         │ (Lock-Free Queue)
//         ▼
// ┌──────────────────────┐
// │ MarketDataPublisher  │
// └──┬────────────────┬──┘
//    │                │
//    │ Incremental    │ Snapshot
//    │ (即時串流)     │ (週期快照)
//    ▼                ▼
// UDP Multicast   SnapshotSynthesizer
//
// ⚡ 效能優化：
// - Busy-Wait 迴圈：while(run_) 持續輪詢，無 sleep（極低延遲）
// - 批次處理：for 迴圈一次處理多個更新（減少 syscall）
// - 零拷貝：指標操作，不複製 MEMarketUpdate 結構
// - 序列號前置：先發送序列號，再發送資料（減少封包數）
//
// ⚠️ 注意事項：
// - noexcept：不拋出異常（低延遲程式碼避免異常處理）
// - 序列號管理：客戶端可透過序列號偵測封包遺失或亂序
// - sendAndRecv()：必須定期呼叫以刷新 Socket 緩衝區
auto MarketDataPublisher::run() noexcept -> void
{
    // 記錄啟動時間（除錯用）
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    // 主事件迴圈：Busy-Wait 模式（持續輪詢佇列）
    // ⚡ 無 sleep/yield：確保極低延遲（代價：100% CPU 使用率）
    while (run_) {
        // 批次處理迴圈：一次處理佇列中的所有更新
        // ⚡ 條件：
        // 1. getNextToRead() 取得下一個可讀元素
        // 2. size() > 0 確保佇列非空
        // 3. market_update != nullptr 確保有效指標
        for (auto market_update = outgoing_md_updates_->getNextToRead();
             outgoing_md_updates_->size() &&
             market_update; market_update = outgoing_md_updates_->getNextToRead()) {

            // 記錄發送的序列號和市場更新內容（除錯用）
            logger_.log("%:% %() % Sending seq:% %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), next_inc_seq_num_,
                        market_update->toString().c_str());

            // === 步驟 1：發送增量更新（UDP Multicast）===
            // 1.1 先發送序列號（4 或 8 bytes）
            // ⚡ 序列號前置：讓客戶端能立即驗證封包順序
            incremental_socket_.send(&next_inc_seq_num_, sizeof(next_inc_seq_num_));

            // 1.2 再發送市場更新資料（MEMarketUpdate 結構）
            // ⚡ 零拷貝：直接傳送指標，不複製資料
            incremental_socket_.send(market_update, sizeof(MEMarketUpdate));

            // 1.3 更新讀取索引（標記已處理）
            // ⚡ Lock-Free 操作：無需鎖定，只更新原子索引
            outgoing_md_updates_->updateReadIndex();

            // === 步驟 2：轉發到快照佇列 ===
            // 2.1 取得快照佇列的寫入位置
            auto next_write = snapshot_md_updates_.getNextToWriteTo();

            // 2.2 寫入序列號和市場更新（包裝成 MDPMarketUpdate）
            // ⚡ 結構複製：snapshot_md_updates_ 需要持久化資料
            next_write->seq_num_ = next_inc_seq_num_;
            next_write->me_market_update_ = *market_update;

            // 2.3 更新寫入索引（標記已寫入）
            snapshot_md_updates_.updateWriteIndex();

            // === 步驟 3：遞增序列號 ===
            // ⚡ 單調遞增：確保每個更新都有唯一序列號
            ++next_inc_seq_num_;
        }

        // 刷新 Socket 緩衝區（批次發送）
        // ⚡ 批次優化：累積多個 send() 後一次性刷新
        // ⚠️ 注意：sendAndRecv() 可能會執行實際的 syscall（sendmsg/recvmsg）
        incremental_socket_.sendAndRecv();
    }
}
}
