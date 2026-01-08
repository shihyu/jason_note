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
