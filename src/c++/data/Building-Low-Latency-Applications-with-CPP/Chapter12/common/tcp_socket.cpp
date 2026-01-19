#include "tcp_socket.h"

namespace Common
{
// 建立 TCP 連線或綁定連接埠
// 根據 is_listening 參數決定是 Client (connect) 還是 Server (bind & listen)
auto TCPSocket::connect(const std::string& ip, const std::string& iface,
                        int port, bool is_listening) -> int
{
    // needs_so_timestamp=true: 啟用核心時間戳記 (對 FIFO Sequencer 很重要)
    const SocketCfg socket_cfg{ip, iface, port, false, is_listening, true};
    socket_fd_ = createSocket(logger_, socket_cfg);

    socket_attrib_.sin_addr.s_addr = INADDR_ANY;
    socket_attrib_.sin_port = htons(port);
    socket_attrib_.sin_family = AF_INET;

    return socket_fd_;
}

// 處理 TCP 數據收發
// 1. 使用 recvmsg() 讀取數據與輔助資訊 (Ancillary Data)
// 2. 提取核心時間戳記 (Kernel Timestamp)
// 3. 非阻塞發送緩衝區數據
auto TCPSocket::sendAndRecv() noexcept -> bool
{
    char ctrl[CMSG_SPACE(sizeof(struct timeval))];
    auto cmsg = reinterpret_cast<struct cmsghdr*>(&ctrl);

    // 設定分散/聚集 I/O 向量 (Scatter/Gather I/O)
    iovec iov{inbound_data_.data() + next_rcv_valid_index_, TCPBufferSize - next_rcv_valid_index_};
    msghdr msg{&socket_attrib_, sizeof(socket_attrib_), &iov, 1, ctrl, sizeof(ctrl), 0};

    // 1. 接收數據 (Non-blocking)
    const auto read_size = recvmsg(socket_fd_, &msg, MSG_DONTWAIT);

    if (read_size > 0) {
        next_rcv_valid_index_ += read_size;

        Nanos kernel_time = 0;
        timeval time_kernel;

        // 2. 提取核心接收時間戳記 (SO_TIMESTAMP)
        // ⚡ 核心時間比用戶空間時間更精確，排除了系統呼叫與排程延遲
        if (cmsg->cmsg_level == SOL_SOCKET &&
            cmsg->cmsg_type == SCM_TIMESTAMP &&
            cmsg->cmsg_len == CMSG_LEN(sizeof(time_kernel))) {
            memcpy(&time_kernel, CMSG_DATA(cmsg), sizeof(time_kernel));
            kernel_time = time_kernel.tv_sec * NANOS_TO_SECS + time_kernel.tv_usec *
                          NANOS_TO_MICROS; // 轉換為奈秒
        }

        // ⚡ 時間戳取得：避免高開銷 API。
        const auto user_time = getCurrentNanos();

        logger_.log("%:% %() % read socket:% len:% utime:% ktime:% diff:%\n", __FILE__,
                    __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, next_rcv_valid_index_,
                    user_time, kernel_time, (user_time - kernel_time));
        
        // 觸發回調，傳遞核心時間戳記
        recv_callback_(this, kernel_time);
    }

    // 3. 發送數據 (若有)
    if (next_send_valid_index_ > 0) {
        const auto n = ::send(socket_fd_, outbound_data_.data(), next_send_valid_index_,
                              // ⚡ 非阻塞 I/O：避免 syscall 阻塞。
                              MSG_DONTWAIT | MSG_NOSIGNAL);
        logger_.log("%:% %() % send socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, n);
    }

    // 重置發送索引 (假設發送成功)
    next_send_valid_index_ = 0;

    return (read_size > 0);
}

// 拷貝數據到發送緩衝區
auto TCPSocket::send(const void* data, size_t len) noexcept -> void
{
    memcpy(outbound_data_.data() + next_send_valid_index_, data, len);
    next_send_valid_index_ += len;
}
}
