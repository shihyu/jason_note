/**
 * @file market_data_publisher.cpp
 * @brief 行情發布器實作檔案
 *
 * 實作 MarketDataPublisher 類別的核心功能，負責將撮合引擎產生的市場更新
 * 透過 UDP Multicast 發送給所有行情訂閱者。
 *
 * 核心設計：
 * 1. 雙通道發布：
 *    - 增量更新（Incremental Updates）：即時發送每筆訂單變動
 *    - 快照（Snapshot）：由 SnapshotSynthesizer 定期發送完整訂單簿狀態
 * 2. Lock-Free 通訊：
 *    - 從撮合引擎透過 Lock-Free Queue 接收市場更新
 *    - 避免鎖競爭，保證低延遲
 * 3. 序列號管理：
 *    - 每筆增量更新都有唯一的序列號（next_inc_seq_num_）
 *    - 客戶端可用序列號檢測丟包與排序
 *
 * 資料流：
 * MatchingEngine → LFQueue → MarketDataPublisher → UDP Multicast → Clients
 *                           ↓
 *                  SnapshotSynthesizer → UDP Multicast → Clients
 */
#include "market_data_publisher.h"

namespace Exchange
{
/**
 * @brief MarketDataPublisher 建構子
 *
 * 初始化行情發布器的兩個發布通道：
 * 1. 增量更新通道（Incremental Channel）：即時發送訂單變動
 * 2. 快照通道（Snapshot Channel）：定期發送完整訂單簿狀態
 *
 * @param market_updates Lock-Free Queue 指標（從撮合引擎接收市場更新）
 * @param iface 網路介面名稱（例如 "eth0"）
 * @param snapshot_ip 快照通道的 Multicast IP 位址
 * @param snapshot_port 快照通道的 UDP Port
 * @param incremental_ip 增量更新通道的 Multicast IP 位址
 * @param incremental_port 增量更新通道的 UDP Port
 *
 * 初始化流程：
 * 1. 綁定 Lock-Free Queue（outgoing_md_updates_）
 * 2. 建立增量更新的 UDP Multicast Socket
 * 3. 建立快照合成器（SnapshotSynthesizer）
 * 4. 初始化日誌記錄器
 *
 * ⚡ 效能考量：
 * - UDP Multicast：無連線協議，低延遲（無 TCP 三次握手）
 * - Lock-Free Queue：撮合引擎與發布器之間無鎖通訊
 * - 雙通道設計：增量更新低延遲，快照保證最終一致性
 *
 * ⚠️ 注意：
 * - incremental_socket_ 的 is_listening 參數為 false（發送端模式）
 * - snapshot_synthesizer_ 使用 new 動態分配（需在解構子中 delete）
 */
MarketDataPublisher::MarketDataPublisher(MEMarketUpdateLFQueue* market_updates,
        const std::string& iface,
        const std::string& snapshot_ip, int snapshot_port,
        const std::string& incremental_ip, int incremental_port)
    : outgoing_md_updates_(market_updates),  // 綁定 Lock-Free Queue
      snapshot_md_updates_(ME_MAX_MARKET_UPDATES),  // 快照更新佇列（給 SnapshotSynthesizer）
      run_(false),  // 執行標誌（初始為 false，start() 時設為 true）
      logger_("exchange_market_data_publisher.log"),  // 日誌記錄器
      incremental_socket_(logger_)  // 增量更新的 UDP Multicast Socket
{
    // 初始化增量更新的 UDP Multicast Socket
    // ⚠️ is_listening = false：發送端模式（不接收任何資料）
    ASSERT(incremental_socket_.init(incremental_ip, iface,
                                    incremental_port, /*is_listening*/ false) >= 0,
           "Unable to create incremental mcast socket. error:" + std::string(std::strerror(
                       errno)));

    // 建立快照合成器（負責定期發送完整訂單簿狀態）
    // ⚠️ 使用 new 動態分配，需在解構子中 delete
    snapshot_synthesizer_ = new SnapshotSynthesizer(&snapshot_md_updates_, iface,
            snapshot_ip, snapshot_port);
}

/**
 * @brief ⚡ 行情發布主事件迴圈（效能關鍵路徑）
 *
 * 持續從 Lock-Free Queue 讀取市場更新並發送給所有訂閱者。
 *
 * 處理流程（每筆市場更新）：
 * 1. 從 outgoing_md_updates_ Lock-Free Queue 讀取市場更新
 * 2. 透過 UDP Multicast 發送序列號與市場更新
 * 3. 將市場更新轉發給 snapshot_md_updates_（供 SnapshotSynthesizer 使用）
 * 4. 遞增序列號（next_inc_seq_num_）
 * 5. 呼叫 sendAndRecv() 實際發送 UDP 封包
 *
 * ⚡ 效能優化：
 * - Lock-Free Queue：避免鎖競爭，確保低延遲
 * - 批次處理：for 迴圈處理完所有佇列中的更新後才呼叫 sendAndRecv()
 * - UDP Multicast：一次發送，所有訂閱者都能收到（比 TCP 單播快）
 * - noexcept 聲明：避免例外處理開銷
 *
 * 📊 訊息格式（UDP Payload）：
 * [4 bytes: 序列號][sizeof(MEMarketUpdate) bytes: 市場更新結構]
 *
 * 序列號用途：
 * - 丟包檢測：如果收到序列號 100 後直接收到 102，表示 101 丟失
 * - 順序保證：客戶端可用序列號重排亂序的封包
 * - 快照同步：客戶端可用序列號判斷何時需要請求快照
 *
 * ⚠️ 注意：
 * - run_ 標誌由 start() 設為 true，stop() 設為 false
 * - getNextToRead() 回傳 nullptr 表示佇列為空
 * - updateReadIndex() 通知 Lock-Free Queue 該元素已讀取完畢
 * - snapshot_md_updates_ 是給 SnapshotSynthesizer 的佇列（定期發送快照）
 */
auto MarketDataPublisher::run() noexcept -> void
{
    // 記錄啟動時間
    logger_.log("%:% %() %\n", __FILE__, __LINE__, __FUNCTION__,
                Common::getCurrentTimeStr(&time_str_));

    // ⚡ 主事件迴圈：持續發送市場更新直到 stop() 被呼叫
    while (run_) {
        // ⚡ 批次處理：從 Lock-Free Queue 讀取所有可用的市場更新
        // 迴圈條件：佇列非空 且 getNextToRead() 回傳非 nullptr
        for (auto market_update = outgoing_md_updates_->getNextToRead();
             outgoing_md_updates_->size() &&
             market_update; market_update = outgoing_md_updates_->getNextToRead()) {

            // 記錄發送日誌（包含序列號與市場更新內容）
            logger_.log("%:% %() % Sending seq:% %\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), next_inc_seq_num_,
                        market_update->toString().c_str());

            // 步驟 1：發送序列號（4 bytes）
            // ⚡ 客戶端先收到序列號，再收到市場更新（兩個 UDP 封包）
            incremental_socket_.send(&next_inc_seq_num_, sizeof(next_inc_seq_num_));

            // 步驟 2：發送市場更新結構（MEMarketUpdate）
            incremental_socket_.send(market_update, sizeof(MEMarketUpdate));

            // 步驟 3：更新讀取索引（通知 Lock-Free Queue 該元素已處理完畢）
            outgoing_md_updates_->updateReadIndex();

            // 步驟 4：將市場更新轉發給 snapshot_md_updates_（供 SnapshotSynthesizer 使用）
            auto next_write = snapshot_md_updates_.getNextToWriteTo();
            next_write->seq_num_ = next_inc_seq_num_;  // 記錄序列號
            next_write->me_market_update_ = *market_update;  // 拷貝市場更新
            snapshot_md_updates_.updateWriteIndex();  // 更新寫入索引

            // 步驟 5：遞增序列號（每筆市場更新都有唯一序列號）
            ++next_inc_seq_num_;
        }

        // ⚡ 批次發送：實際發送 UDP 封包（可能包含多筆市場更新）
        // sendAndRecv() 會呼叫系統呼叫 sendmsg()，一次發送所有緩衝的資料
        incremental_socket_.sendAndRecv();
    }
}
}
