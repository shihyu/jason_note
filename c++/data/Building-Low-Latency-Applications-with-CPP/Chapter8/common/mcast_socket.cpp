// UDP Multicast 收發：行情熱路徑 I/O 實作。
// ⚡ 效能關鍵：單次 recv/write 合併處理。
// ⚠️ 注意：回調不可阻塞。

#include "mcast_socket.h"

namespace Common
{
// 初始化 Multicast Socket
// 建立 socket 並設定參數 (但不執行 connect 或 bind)
auto McastSocket::init(const std::string& ip, const std::string& iface,
                       int port, bool is_listening) -> int
{
    const SocketCfg socket_cfg{ip, iface, port, true, is_listening, false};
    socket_fd_ = createSocket(logger_, socket_cfg);
    return socket_fd_;
}

// 加入多播群組 (Join Membership)
// 告訴核心我們想接收發送到此 IP 的多播封包
bool McastSocket::join(const std::string& ip)
{
    return Common::join(socket_fd_, ip);
}

// 離開多播群組
// 關閉 Socket
auto McastSocket::leave(const std::string&, int) -> void
{
    close(socket_fd_);
    socket_fd_ = -1;
}

// 處理數據收發
// 1. 嘗試非阻塞讀取數據
// 2. 若發送緩衝區有數據，則非阻塞發送
auto McastSocket::sendAndRecv() noexcept -> bool
{
    // 1. 讀取數據 (Non-blocking)
    // MSG_DONTWAIT: 若無數據可讀，立即返回 -1 (errno=EAGAIN)
    const ssize_t n_rcv = recv(socket_fd_,
                               inbound_data_.data() + next_rcv_valid_index_,
                               // ⚡ 非阻塞 I/O：避免 syscall 阻塞。
                               McastBufferSize - next_rcv_valid_index_, MSG_DONTWAIT);

    if (n_rcv > 0) {
        next_rcv_valid_index_ += n_rcv;
        logger_.log("%:% %() % read socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_,
                    next_rcv_valid_index_);
        // 觸發回調函式處理數據
        recv_callback_(this);
    }

    // 2. 發送數據 (若有)
    if (next_send_valid_index_ > 0) {
        // MSG_NOSIGNAL: 避免因對端關閉而收到 SIGPIPE 信號
        ssize_t n = ::send(socket_fd_, outbound_data_.data(), next_send_valid_index_,
                           MSG_DONTWAIT | MSG_NOSIGNAL);

        logger_.log("%:% %() % send socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, n);
    }

    // 重置發送索引 (假設數據已全部寫入 socket 緩衝區)
    // ⚠️ 注意：這裡簡化了邏輯，假設 send 總是成功寫入所有字節
    // 在極高負載下，send 可能只寫入部分數據，生產環境需處理剩餘部分
    next_send_valid_index_ = 0;

    return (n_rcv > 0);
}

// 拷貝數據到發送緩衝區
auto McastSocket::send(const void* data, size_t len) noexcept -> void
{
    memcpy(outbound_data_.data() + next_send_valid_index_, data, len);
    next_send_valid_index_ += len;
    ASSERT(next_send_valid_index_ < McastBufferSize,
           "Mcast socket buffer filled up and sendAndRecv() not called.");
}
}
