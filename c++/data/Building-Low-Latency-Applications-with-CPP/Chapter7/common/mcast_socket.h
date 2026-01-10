#pragma once

#include <functional>

#include "socket_utils.h"

#include "logging.h"

namespace Common
{
// UDP Multicast 緩衝區大小 (64 MB)
// ⚡ 效能關鍵：大緩衝區避免在高流量市場數據下丟包 (Packet Loss)
constexpr size_t McastBufferSize = 64 * 1024 * 1024;

// ============================================================================
// UDP Multicast Socket (群播套接字)
// ============================================================================
// 📌 設計用途：
// 1. 市場數據發布 (Market Data Publishing)：交易所 -> 多個客戶端
// 2. 市場數據訂閱 (Market Data Subscription)：客戶端收聽到多播群組
//
// ⚡ 核心特性：
// - UDP 協議：無連線、低延遲、不保證順序 (需應用層處理)
// - 非阻塞 I/O (Non-blocking I/O)：recv() 不會阻塞主執行緒
// - 內建緩衝區：64 MB 發送/接收緩衝區
//
// ⚠️ UDP 協議特性與挑戰：
// 1. 不可靠傳輸 (Unreliable)：
//    - 封包可能丟失 (Packet Loss)
//    - 封包可能亂序 (Out-of-Order)
//    - 封包可能重複 (Duplication)
//    - 無自動重傳機制 (需應用層處理)
//
// 2. 無連接狀態 (Connectionless)：
//    - 發送端不知道接收端是否收到
//    - 無流量控制 (Flow Control)
//    - 無擁塞控制 (Congestion Control)
//
// 3. 高效能特性：
//    - 無三向交握 (No Handshake)
//    - 無序列號確認 (No ACK/NACK)
//    - 延遲極低 (< 10 μs in LAN)
//
// 🔧 應用層必須實作的機制：
// 1. **序列號檢測 (Sequence Number Detection)**：
//    ```cpp
//    struct MarketDataMessage {
//        uint64_t sequence_number;  // 遞增的序列號
//        uint64_t timestamp;        // 發送時間戳記
//        // ... 其他欄位 ...
//    };
//
//    // 接收端檢測
//    static uint64_t expected_seq = 0;
//    auto* msg = reinterpret_cast<MarketDataMessage*>(inbound_data_.data());
//
//    if (msg->sequence_number != expected_seq) {
//        if (msg->sequence_number > expected_seq) {
//            // 丟包：缺少 [expected_seq, msg->sequence_number) 的封包
//            size_t gap = msg->sequence_number - expected_seq;
//            logger.log("Packet loss detected: missing % packets (seq % to %)\n",
//                       gap, expected_seq, msg->sequence_number - 1);
//            // 觸發重傳請求或使用快照恢復
//        } else {
//            // 重複或亂序封包
//            logger.log("Duplicate/out-of-order packet: seq % (expected %)\n",
//                       msg->sequence_number, expected_seq);
//            return;  // 丟棄
//        }
//    }
//    expected_seq = msg->sequence_number + 1;
//    ```
//
// 2. **丟包恢復策略**：
//    - 方案 A：快照 + 增量 (Snapshot + Incremental)
//      - 定期請求完整快照 (例如每秒)
//      - 增量更新使用 Multicast
//      - 丟包時用快照重建狀態
//
//    - 方案 B：重傳機制 (Retransmission)
//      - 透過 TCP 連接請求重傳遺失的封包
//      - 範例：
//        ```cpp
//        if (gap > 0) {
//            tcp_socket.send_retransmit_request(expected_seq, msg->sequence_number);
//        }
//        ```
//
//    - 方案 C：FEC (Forward Error Correction)
//      - 發送端加入冗余資料 (例如 Reed-Solomon 編碼)
//      - 接收端可從部分封包恢復完整資料
//      - 代價：增加頻寬與計算開銷
//
// 3. **亂序處理 (Out-of-Order Handling)**：
//    ```cpp
//    std::map<uint64_t, MarketDataMessage> reorder_buffer_;
//    static uint64_t next_expected_seq = 0;
//
//    // 收到封包時
//    if (msg->sequence_number == next_expected_seq) {
//        // 順序正確，直接處理
//        process_message(msg);
//        next_expected_seq++;
//
//        // 檢查緩衝區中是否有後續封包
//        while (reorder_buffer_.count(next_expected_seq)) {
//            process_message(&reorder_buffer_[next_expected_seq]);
//            reorder_buffer_.erase(next_expected_seq);
//            next_expected_seq++;
//        }
//    } else if (msg->sequence_number > next_expected_seq) {
//        // 亂序，暫存到緩衝區
//        reorder_buffer_[msg->sequence_number] = *msg;
//
//        // 防止緩衝區無限增長
//        if (reorder_buffer_.size() > MAX_REORDER_BUFFER_SIZE) {
//            logger.log("Reorder buffer overflow, discarding old packets\n");
//            // 處理緩衝區中最舊的封包或清空
//        }
//    } else {
//        // 重複封包，丟棄
//    }
//    ```
//
// 4. **時間戳記驗證 (Timestamp Validation)**：
//    ```cpp
//    auto now = getCurrentNanos();
//    auto latency = now - msg->timestamp;
//
//    if (latency > 1 * NANOS_TO_SECS) {  // 超過 1 秒
//        logger.log("WARNING: Stale packet detected (latency: % ms)\n",
//                   latency / NANOS_TO_MILLIS);
//        // 可能是網路延遲或時鐘不同步
//    }
//
//    if (latency < 0) {  // 時間倒退
//        logger.log("ERROR: Timestamp in future (clock skew: % ms)\n",
//                   -latency / NANOS_TO_MILLIS);
//        // 可能是 NTP 調整或發送端/接收端時鐘不同步
//    }
//    ```
//
// 📊 丟包率監控與調優：
// 1. 監控丟包率：
//    ```cpp
//    static size_t total_packets = 0;
//    static size_t lost_packets = 0;
//
//    total_packets++;
//    lost_packets += gap;
//
//    if (total_packets % 10000 == 0) {
//        double loss_rate = (double)lost_packets / total_packets * 100;
//        logger.log("Packet loss rate: %.2f%% (%/%)\n",
//                   loss_rate, lost_packets, total_packets);
//    }
//    ```
//
// 2. 常見丟包原因與解決方案：
//    - 接收緩衝區溢位 (SO_RCVBUF 太小)：
//      - 增加 SO_RCVBUF：`setsockopt(fd, SOL_SOCKET, SO_RCVBUF, 64MB)`
//      - 當前實作已設定 64 MB
//
//    - 應用層處理太慢 (recv() 呼叫不夠頻繁)：
//      - 增加 recv() 呼叫頻率 (緊密迴圈)
//      - 使用專用執行緒處理接收
//      - 使用 recvmmsg() 批次接收
//
//    - 網路擁塞：
//      - 升級網路設備 (千兆 -> 萬兆)
//      - 使用專用 VLAN 隔離市場數據流量
//      - 啟用 QoS (Quality of Service) 優先級
//
//    - 作業系統丟包 (netstat -su 查看)：
//      ```bash
//      netstat -su | grep "packet receive errors"
//      # 若數值持續增長，表示系統層丟包
//      ```
//      - 調整內核參數：
//        ```bash
//        sudo sysctl -w net.core.rmem_max=134217728   # 128 MB
//        sudo sysctl -w net.core.rmem_default=67108864  # 64 MB
//        ```
//
// 3. 效能基準：
//    - 區域網路 (LAN)：丟包率應 < 0.01%
//    - 廣域網路 (WAN)：丟包率可能 0.1-1%
//    - 若丟包率 > 1%，需檢查網路與系統配置
//
// 🔧 生產環境最佳實踐：
// 1. 強制實作序列號檢測 (否則無法發現丟包)
// 2. 記錄所有丟包事件 (用於故障分析)
// 3. 監控丟包率指標 (接入監控系統如 Prometheus)
// 4. 定期測試丟包恢復機制 (注入人工丟包)
// 5. 使用專用網路介面 (避免與其他流量競爭)
//
// 📚 進階優化：
// 1. 使用 DPDK (Data Plane Development Kit)：
//    - 繞過內核網路堆疊
//    - 用戶態輪詢 (Polling) 取代中斷
//    - 延遲可降至 < 1 μs
//
// 2. 使用硬體時間戳記 (PTP Hardware Timestamping)：
//    - 網卡層直接打上時間戳記
//    - 精度 < 1 μs
//
// 3. 使用 Kernel Bypass (例如 Solarflare Onload)：
//    - 繞過內核，直接與網卡通訊
//    - 延遲降低 50-80%
struct McastSocket {
    McastSocket(Logger& logger)
        : logger_(logger)
    {
        outbound_data_.resize(McastBufferSize);
        inbound_data_.resize(McastBufferSize);
    }

    // 初始化 Multicast Socket
    // @param ip: 多播群組 IP (如 224.0.0.1)
    // @param iface: 本地介面 (如 eth0)
    // @param port: 連接埠
    // @param is_listening: true 為接收端 (訂閱)，false 為發送端 (發布)
    auto init(const std::string& ip, const std::string& iface, int port,
              bool is_listening) -> int;

    // 加入多播群組 (Join Membership)
    // ⚡ 訂閱市場數據時必須呼叫
    auto join(const std::string& ip) -> bool;

    // 離開多播群組
    auto leave(const std::string& ip, int port) -> void;

    // 處理數據收發 (Send and Receive)
    // 1. 若發送緩衝區有資料 -> 呼叫 sendto()
    // 2. 呼叫 recv() 嘗試讀取資料 -> 存入接收緩衝區
    // 3. 若收到資料 -> 觸發 recv_callback_
    auto sendAndRecv() noexcept -> bool;

    // 將資料寫入發送緩衝區 (不立即發送)
    // ⚡ 批次處理：多次呼叫 send() 後，由 sendAndRecv() 一次性發送
    auto send(const void* data, size_t len) noexcept -> void;

    int socket_fd_ = -1;

    // 發送/接收緩衝區
    // 通常只會用到其中一個 (取決於角色是發送端還是接收端)
    std::vector<char> outbound_data_;
    size_t next_send_valid_index_ = 0;
    std::vector<char> inbound_data_;
    size_t next_rcv_valid_index_ = 0;

    // 資料接收回調函式
    // 當收到 UDP 封包時觸發
    std::function<void(McastSocket* s)> recv_callback_ = nullptr;

    std::string time_str_;
    Logger& logger_;
};
}
