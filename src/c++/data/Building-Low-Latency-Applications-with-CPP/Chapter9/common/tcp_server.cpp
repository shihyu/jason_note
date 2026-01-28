#include "tcp_server.h"

namespace Common
{
// 將 Socket 加入 Epoll 監控清單
// 監控事件：
// - EPOLLET (Edge Triggered): 邊緣觸發模式，僅在狀態變化時通知一次 (高效但需一次讀完)
// - EPOLLIN: 可讀事件 (有新連線或新數據)
auto TCPServer::addToEpollList(TCPSocket* socket)
{
    // ⚡ Epoll I/O：事件驅動降低延遲。
    epoll_event ev{EPOLLET | EPOLLIN, {reinterpret_cast<void*>(socket)}};
    return !epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, socket->socket_fd_, &ev);
}

// 啟動監聽
// 1. 建立 Epoll 實例
// 2. 建立並綁定監聽 Socket
// 3. 將監聽 Socket 加入 Epoll 監控
auto TCPServer::listen(const std::string& iface, int port) -> void
{
    // ⚡ Epoll I/O：事件驅動降低延遲。
    epoll_fd_ = epoll_create(1);
    ASSERT(epoll_fd_ >= 0, "epoll_create() failed error:" + std::string(
               std::strerror(errno)));

    ASSERT(listener_socket_.connect("", iface, port, true) >= 0,
           "Listener socket failed to connect. iface:" + iface + " port:" + std::to_string(
               port) + " error:" +
           std::string(std::strerror(errno)));

    ASSERT(addToEpollList(&listener_socket_),
           // ⚡ Epoll I/O：事件驅動降低延遲。
           "epoll_ctl() failed. error:" + std::string(std::strerror(errno)));
}

// 處理數據收發
// 遍歷所有活躍的 Socket，呼叫其 sendAndRecv() 方法
auto TCPServer::sendAndRecv() noexcept -> void
{
    auto recv = false;

    // 1. 接收數據
    std::for_each(receive_sockets_.begin(),
    receive_sockets_.end(), [&recv](auto socket) {
        recv |= socket->sendAndRecv();
    });

    // 若有收到任何數據，觸發處理完成回調 (例如：通知訂單閘道進行排序)
    if (recv) { // There were some events and they have all been dispatched, inform listener.
        recv_finished_callback_();
    }

    // 2. 發送數據
    std::for_each(send_sockets_.begin(), send_sockets_.end(), [](auto socket) {
        socket->sendAndRecv();
    });
}

// 輪詢 Epoll 事件
// 檢查是否有新連線、斷線或數據到達
auto TCPServer::poll() noexcept -> void
{
    const int max_events = 1 + send_sockets_.size() + receive_sockets_.size();

    // ⚡ epoll_wait: timeout=0 表示非阻塞立即返回
    const int n = epoll_wait(epoll_fd_, events_, max_events, 0);
    bool have_new_connection = false;

    for (int i = 0; i < n; ++i) {
        const auto& event = events_[i];
        auto socket = reinterpret_cast<TCPSocket*>(event.data.ptr);

        // Check for new connections.
        // ⚡ Epoll I/O：事件驅動降低延遲。
        if (event.events & EPOLLIN) {
            if (socket == &listener_socket_) {
                // 監聽 Socket 有事件 -> 表示有新連線請求
                logger_.log("%:% %() % EPOLLIN listener_socket:%\n", __FILE__, __LINE__,
                            __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);
                have_new_connection = true;
                continue;
            }

            // 一般 Socket 有事件 -> 有數據可讀
            logger_.log("%:% %() % EPOLLIN socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                          socket) == receive_sockets_.end()) {
                receive_sockets_.push_back(socket);
            }
        }

        // ⚡ Epoll I/O：事件驅動降低延遲。
        if (event.events & EPOLLOUT) {
            logger_.log("%:% %() % EPOLLOUT socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            if (std::find(send_sockets_.begin(), send_sockets_.end(),
                          socket) == send_sockets_.end()) {
                send_sockets_.push_back(socket);
            }
        }

        // ⚡ Epoll I/O：事件驅動降低延遲。
        if (event.events & (EPOLLERR | EPOLLHUP)) {
            logger_.log("%:% %() % EPOLLERR socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                          socket) == receive_sockets_.end()) {
                receive_sockets_.push_back(socket);
            }
        }
    }

    // 接受新連線
    while (have_new_connection) {
        logger_.log("%:% %() % have_new_connection\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_));
        sockaddr_storage addr;
        socklen_t addr_len = sizeof(addr);
        int fd = accept(listener_socket_.socket_fd_, reinterpret_cast<sockaddr*>(&addr),
                        &addr_len);

        if (fd == -1) {
            break;
        }

        // 設定非阻塞與 NoDelay
        ASSERT(setNonBlocking(fd) && disableNagle(fd),
               "Failed to set non-blocking or no-delay on socket:" + std::to_string(fd));

        logger_.log("%:% %() % accepted socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), fd);

        auto socket = new TCPSocket(logger_);
        socket->socket_fd_ = fd;
        socket->recv_callback_ = recv_callback_;
        
        // 將新連線加入 Epoll
        ASSERT(addToEpollList(socket),
               "Unable to add socket. error:" + std::string(std::strerror(errno)));

        if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                      socket) == receive_sockets_.end()) {
            receive_sockets_.push_back(socket);
        }
    }
}
}
