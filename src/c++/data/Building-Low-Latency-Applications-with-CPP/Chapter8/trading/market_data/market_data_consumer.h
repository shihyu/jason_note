#pragma once

#include <functional>
#include <map>

#include "common/thread_utils.h"
#include "common/lf_queue.h"
#include "common/macros.h"
#include "common/mcast_socket.h"

#include "exchange/market_data/market_update.h"

namespace Trading
{
/**
 * MarketDataConsumer - 市場數據消費者
 *
 * 核心職責：
 * 1. 訂閱交易所多播市場數據（Multicast）
 * 2. 接收增量更新（Incremental Updates）和快照（Snapshots）
 * 3. 偵測遺失訊息並觸發恢復機制
 * 4. 重建完整市場狀態並通知交易引擎
 *
 * 雙通道設計：
 * - Incremental Channel（增量通道）：
 *   - 發佈市場事件（訂單新增/取消/成交）
 *   - 低延遲：< 50 μs（交易所到本地）
 *   - 可能遺失訊息（UDP 特性）
 *
 * - Snapshot Channel（快照通道）：
 *   - 定期發佈完整訂單簿狀態
 *   - 用於初始化和恢復
 *   - 頻率：每 1-5 秒一次
 *
 * 恢復機制（Recovery）：
 * 1. 正常模式：處理增量更新，驗證序列號
 * 2. 檢測到遺失 → 進入恢復模式（in_recovery_ = true）
 * 3. 訂閱快照通道，重建市場狀態
 * 4. 暫存增量訊息到 incremental_queued_msgs_
 * 5. 快照同步完成 → 重放暫存訊息 → 恢復正常模式
 *
 * 訊息排序：
 * - 使用 std::map<seq_num, update> 暫存亂序訊息
 * - 保證交易引擎接收到順序正確的市場數據
 *
 * 效能考量：
 * - Multicast 訂閱（減少交易所負載）
 * - Lock-Free Queue 輸出（零等待）
 * - 序列號檢查：O(1)
 * - 排隊邏輯：O(log N)（std::map 插入）
 *
 * 典型延遲：
 * - 增量更新：20-50 μs（交易所 → 本地）
 * - 恢復時間：100-500 ms（取決於訊息積壓量）
 */
class MarketDataConsumer
{
public:
    /**
     * 構造函式
     * @param client_id 客戶端識別碼
     * @param market_updates 指向市場更新佇列的指標（輸出到交易引擎）
     * @param iface 本地網路介面名稱（用於 multicast 訂閱）
     * @param snapshot_ip 快照多播群組 IP
     * @param snapshot_port 快照多播埠號
     * @param incremental_ip 增量更新多播群組 IP
     * @param incremental_port 增量更新多播埠號
     */
    MarketDataConsumer(Common::ClientId client_id,
                       Exchange::MEMarketUpdateLFQueue* market_updates, const std::string& iface,
                       const std::string& snapshot_ip, int snapshot_port,
                       const std::string& incremental_ip, int incremental_port);

    /**
     * 解構函式
     * 安全關閉流程：
     * 1. 呼叫 stop() 停止執行緒
     * 2. 等待 5 秒讓執行緒完成清理
     * 3. Multicast sockets 自動解除訂閱
     */
    ~MarketDataConsumer()
    {
        stop();

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(5s);  // 等待執行緒優雅退出
    }

    /**
     * 啟動市場數據消費者
     * 步驟：
     * 1. 設置運行旗標
     * 2. 建立獨立執行緒執行 run() 主迴圈
     * 3. 訂閱 multicast 群組（在 run() 中進行）
     */
    auto start()
    {
        run_ = true;
        ASSERT(Common::createAndStartThread(-1, "Trading/MarketDataConsumer", [this]() {
            // ⚡ 關鍵路徑：函式內避免鎖/分配，保持快取局部性。
            run();
        }) != nullptr, "Failed to start MarketData thread.");
    }

    /**
     * 停止市場數據消費者
     * 設置 run_ = false，通知執行緒退出主迴圈
     */
    auto stop() -> void
    {
        run_ = false;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    MarketDataConsumer() = delete;

    MarketDataConsumer(const MarketDataConsumer&) = delete;

    MarketDataConsumer(const MarketDataConsumer&&) = delete;

    MarketDataConsumer& operator=(const MarketDataConsumer&) = delete;

    MarketDataConsumer& operator=(const MarketDataConsumer&&) = delete;

private:
    // === 序列號管理 ===
    /**
     * next_exp_inc_seq_num_ - 預期增量更新序列號
     * 用於偵測遺失訊息
     * 若收到的序列號 > 預期值 → 進入恢復模式
     */
    size_t next_exp_inc_seq_num_ = 1;

    // === Lock-Free 通訊佇列 ===
    /**
     * incoming_md_updates_ - 市場更新輸出佇列
     * 將處理後的市場更新寫入此佇列，交易引擎讀取
     */
    Exchange::MEMarketUpdateLFQueue* incoming_md_updates_ = nullptr;

    // === 執行緒控制 ===
    volatile bool run_ = false;  ///< 執行緒運行旗標

    // === 日誌系統 ===
    std::string time_str_;       ///< 時間字串緩衝區
    Logger logger_;              ///< 日誌記錄器

    // === Multicast Sockets ===
    /**
     * incremental_mcast_socket_ - 增量更新訂閱 socket
     * 接收實時市場事件（訂單新增/取消/成交）
     */
    Common::McastSocket incremental_mcast_socket_;

    /**
     * snapshot_mcast_socket_ - 快照訂閱 socket
     * 接收完整訂單簿狀態（用於初始化和恢復）
     */
    Common::McastSocket snapshot_mcast_socket_;

    // === 恢復機制 ===
    /**
     * in_recovery_ - 恢復模式旗標
     * true:  正在同步快照，暫存增量訊息
     * false: 正常模式，直接處理增量訊息
     */
    bool in_recovery_ = false;

    const std::string iface_;     ///< 本地網路介面名稱
    const std::string snapshot_ip_; ///< 快照多播群組 IP
    const int snapshot_port_;     ///< 快照多播埠號

    // === 訊息排隊 ===
    /**
     * QueuedMarketUpdates - 暫存亂序訊息的容器
     * std::map<seq_num, MEMarketUpdate>
     * 用於處理以下情境：
     * 1. 恢復模式：暫存增量訊息等待快照同步完成
     * 2. 亂序接收：按序列號排序後依序處理
     */
    typedef std::map<size_t, Exchange::MEMarketUpdate> QueuedMarketUpdates;

    /**
     * snapshot_queued_msgs_ - 快照訊息暫存
     * 儲存接收到但尚未處理的快照訊息
     */
    QueuedMarketUpdates snapshot_queued_msgs_;

    /**
     * incremental_queued_msgs_ - 增量訊息暫存
     * 恢復模式下儲存增量訊息，等待快照同步完成後重放
     */
    QueuedMarketUpdates incremental_queued_msgs_;

private:
    /**
     * run() - 主事件迴圈（在獨立執行緒中執行）
     *
     * 職責：
     * 1. 輪詢兩個 multicast sockets
     * 2. 接收市場數據更新
     * 3. 觸發 recvCallback() 處理訊息
     * 4. 執行恢復邏輯（若需要）
     */
    auto run() noexcept -> void;

    /**
     * recvCallback() - Multicast 接收回調函式
     *
     * @param socket 收到資料的 multicast socket 指標
     *
     * 職責：
     * 1. 從 socket 緩衝區讀取訊息
     * 2. 反序列化為 MDPMarketUpdate
     * 3. 判斷是快照還是增量更新
     * 4. 呼叫 queueMessage() 處理訊息
     */
    auto recvCallback(McastSocket* socket) noexcept -> void;

    /**
     * queueMessage() - 訊息排隊與處理
     *
     * @param is_snapshot 是否為快照訊息
     * @param request 市場更新訊息指標
     *
     * 職責：
     * 1. 檢查序列號是否符合預期
     * 2. 若序列號不符：
     *    - 增量訊息遺失 → 觸發 startSnapshotSync()
     *    - 快照訊息亂序 → 加入 snapshot_queued_msgs_
     * 3. 若序列號正確 → 寫入 incoming_md_updates_ 佇列
     * 4. 處理暫存的後續訊息（依序號順序）
     */
    auto queueMessage(bool is_snapshot, const Exchange::MDPMarketUpdate* request);

    /**
     * startSnapshotSync() - 啟動快照同步
     *
     * 觸發時機：偵測到增量訊息遺失
     *
     * 步驟：
     * 1. 設置 in_recovery_ = true
     * 2. 訂閱快照多播群組
     * 3. 清空 snapshot_queued_msgs_
     * 4. 開始接收快照訊息
     */
    auto startSnapshotSync() -> void;

    /**
     * checkSnapshotSync() - 檢查快照同步進度
     *
     * 呼叫時機：每次收到快照訊息後
     *
     * 職責：
     * 1. 檢查是否收到完整快照（最後一個訊息標記 END_OF_SNAPSHOT）
     * 2. 若完整：
     *    - 重建市場狀態
     *    - 重放 incremental_queued_msgs_ 中暫存的增量訊息
     *    - 設置 in_recovery_ = false
     *    - 恢復正常模式
     */
    auto checkSnapshotSync() -> void;
};
}
