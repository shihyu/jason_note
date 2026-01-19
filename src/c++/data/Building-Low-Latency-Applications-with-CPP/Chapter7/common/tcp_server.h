#pragma once

#include "tcp_socket.h"

namespace Common
{
// TCPServer: 基於 Epoll 的非阻塞 TCP 伺服器
//
// 設計原理:
// 1. IO 多路復用 (IO Multiplexing): 使用 Linux Epoll 機制監控多個 Socket
// 2. 非阻塞 IO (Non-blocking IO): 避免 read/write 阻塞執行緒
// 3. Reactor 模式: 事件驅動處理連接 (Connect) 與數據 (Read/Write)
//
// 使用場景: 交易所 Order Server, 處理大量客戶端並發連線
struct TCPServer {
    explicit TCPServer(Logger& logger)
        : listener_socket_(logger), logger_(logger)
    {
    }

    // 啟動監聽
    // @param iface: 監聽介面 (如 "eth0", "127.0.0.1")
    // @param port: 監聽埠號
    auto listen(const std::string& iface, int port) -> void;

    // 輪詢 IO 事件
    // 呼叫 epoll_wait 檢查是否有新連線或新數據
    // ⚡ 效能關鍵: 低延遲系統中使用 0 超時 (立即返回)
    auto poll() noexcept -> void;

    // 處理數據收發
    // 遍歷所有已連線 Socket, 執行非阻塞 send 和 recv
    auto sendAndRecv() noexcept -> void;

private:
    // 將 Socket 加入 Epoll 監控清單
    // 監控事件: EPOLLIN (可讀) | EPOLLET (Edge Triggered, 可選)
    auto addToEpollList(TCPSocket* socket);

public:
    // ⚡ Epoll I/O：事件驅動降低延遲。
    int epoll_fd_ = -1;
    TCPSocket listener_socket_; // 監聽 Socket (負責 accept 新連線)

    epoll_event events_[1024];  // Epoll 事件緩衝區

    // 連線管理容器
    // receive_sockets_: 所有已連線的 Socket (用於接收)
    // send_sockets_: 有數據待發送的 Socket (用於發送)
    std::vector<TCPSocket*> receive_sockets_, send_sockets_;

    // 回調函數
    // recv_callback_: 當 Socket 收到數據時觸發 (通知上層應用)
    std::function<void(TCPSocket* s, Nanos rx_time)> recv_callback_ = nullptr;
    
    // recv_finished_callback_: 本輪 poll 所有數據處理完畢後觸發
    std::function<void()> recv_finished_callback_ = nullptr;

    std::string time_str_;
    Logger& logger_;
};
}
