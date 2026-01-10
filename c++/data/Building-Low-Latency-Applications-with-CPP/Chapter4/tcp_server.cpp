#include "tcp_server.h"

namespace Common
{
// ========================================
// TCPServer 實作: 高效能 Epoll 伺服器
// ========================================

// addToEpollList: 將 Socket 加入 Epoll 監控清單
// @param socket: 要監控的 TCPSocket 指標
// @return: true=成功, false=失敗
//
// Epoll 事件設定:
// - EPOLLIN: 監控可讀事件 (有新資料/新連線)
// - EPOLLET: Edge-Triggered 模式
//
// ⚡ EPOLLET vs EPOLLLT (Level-Triggered):
// - Edge-Triggered (邊緣觸發):
//   * 只在狀態變化時觸發一次
//   * 必須一次讀取所有資料,否則遺漏
//   * 效能更高 (減少喚醒次數)
// - Level-Triggered (水平觸發):
//   * 只要資料可讀就持續觸發
//   * 較安全但效能較低
//
// 為何使用 EPOLLET:
// - 低延遲系統使用非阻塞 IO + 循環讀取
// - 減少 epoll_wait 喚醒次數,降低開銷
// - 配合 MSG_DONTWAIT 確保不會阻塞
auto TCPServer::addToEpollList(TCPSocket* socket)
{
    // 設定事件: Edge-Triggered + 可讀監控
    // data.ptr: 儲存 TCPSocket 指標,觸發時可直接取得對應 Socket
    epoll_event ev{EPOLLET | EPOLLIN, {reinterpret_cast<void*>(socket)}};

    // EPOLL_CTL_ADD: 將 socket_fd_ 加入 epoll 監控
    // 返回 0=成功, -1=失敗
    return !epoll_ctl(epoll_fd_, EPOLL_CTL_ADD, socket->socket_fd_, &ev);
}

// listen: 啟動伺服器監聽
// @param iface: 網卡名稱或 IP 位址
// @param port: 監聽埠號
//
// 初始化流程:
// 1. 建立 Epoll 實例 (epoll_create)
// 2. 建立監聽 Socket (bind + listen)
// 3. 將監聽 Socket 加入 Epoll 監控
//
// ⚡ Epoll 效能優勢 vs select/poll:
// - O(1) 複雜度: 不需遍歷所有 FD
// - 事件驅動: 只返回活躍的 FD
// - 可擴展性: 支援數萬個並發連線
//
// epoll_create(1) 參數說明:
// - 傳統上指定最大監控 FD 數量
// - Linux 2.6.8+ 後此參數被忽略,但必須 > 0
auto TCPServer::listen(const std::string& iface, int port) -> void
{
    // 1. 建立 Epoll 實例
    epoll_fd_ = epoll_create(1);
    ASSERT(epoll_fd_ >= 0, "epoll_create() failed error:" + std::string(
               std::strerror(errno)));

    // 2. 建立並綁定監聽 Socket
    // connect() 的第一個參數為空字串表示使用 iface 查詢 IP
    // is_listening=true: Server 模式 (bind + listen)
    ASSERT(listener_socket_.connect("", iface, port, true) >= 0,
           "Listener socket failed to connect. iface:" + iface + " port:" + std::to_string(
               port) + " error:" +
           std::string(std::strerror(errno)));

    // 3. 將監聽 Socket 加入 Epoll 監控
    // 觸發 EPOLLIN 時表示有新連線到達
    ASSERT(addToEpollList(&listener_socket_),
           "epoll_ctl() failed. error:" + std::string(std::strerror(errno)));
}

// sendAndRecv: 批次處理所有連線的收發
//
// 處理流程:
// 1. 遍歷 receive_sockets_: 處理所有有資料可讀的 Socket
// 2. 若有資料接收: 呼叫 recv_finished_callback_()
// 3. 遍歷 send_sockets_: 處理所有有資料待發的 Socket
//
// 設計考量:
// - 分離接收和傳送: receive_sockets_ vs send_sockets_
// - 優先處理接收: 接收完成後才處理傳送
// - 批次通知: recv_finished_callback_ 在所有接收完成後才呼叫
//
// ⚡ 效能關鍵:
// - 批次處理: 減少回呼次數
// - 非阻塞 IO: 每個 socket->sendAndRecv() 都是非阻塞的
// - 避免飢餓: 先處理接收,確保訊息即時處理
auto TCPServer::sendAndRecv() noexcept -> void
{
    auto recv = false;  // 追蹤是否有接收到資料

    // 處理所有待接收 Socket
    // recv |= : 邏輯或累積,任一 Socket 有資料則為 true
    std::for_each(receive_sockets_.begin(),
    receive_sockets_.end(), [&recv](auto socket) {
        recv |= socket->sendAndRecv();
    });

    // 本輪所有資料接收完畢,通知上層
    // 使用場景: 批次處理完整的訊息集合
    if (recv) {
        recv_finished_callback_();
    }

    // 處理所有待傳送 Socket
    // 傳送不需要通知 (單向操作)
    std::for_each(send_sockets_.begin(), send_sockets_.end(), [](auto socket) {
        socket->sendAndRecv();
    });
}

// poll: 檢查並處理 Epoll 事件
//
// 處理事件類型:
// 1. EPOLLIN (可讀):
//    - listener_socket_: 有新連線
//    - 一般 socket: 有資料可讀
// 2. EPOLLOUT (可寫): 傳送緩衝區有空間
// 3. EPOLLERR/EPOLLHUP: 連線錯誤/斷線
//
// ⚡ epoll_wait(timeout=0) 的意義:
// - 非阻塞輪詢: 立即返回,不等待事件
// - 低延遲優先: 在主迴圈中頻繁呼叫,確保即時處理
// - CPU 使用權衡: 0 超時會持續佔用 CPU (忙等待)
//
// 設計模式:
// - Reactor 模式: 事件驅動,集中分發
// - 延遲連線接受: 標記 have_new_connection,迴圈後統一處理
auto TCPServer::poll() noexcept -> void
{
    // 計算最大可能事件數
    // +1: listener_socket_
    const int max_events = 1 + send_sockets_.size() + receive_sockets_.size();

    // ⚡ epoll_wait: 檢查就緒事件
    // timeout=0: 非阻塞,立即返回
    // 返回值: 就緒事件數量
    const int n = epoll_wait(epoll_fd_, events_, max_events, 0);
    bool have_new_connection = false;

    // 遍歷所有就緒事件
    for (int i = 0; i < n; ++i) {
        const auto& event = events_[i];
        auto socket = reinterpret_cast<TCPSocket*>(event.data.ptr);

        // === 處理 EPOLLIN (可讀事件) ===
        if (event.events & EPOLLIN) {
            // 特殊處理: 監聽 Socket 的 EPOLLIN 表示有新連線
            if (socket == &listener_socket_) {
                logger_.log("%:% %() % EPOLLIN listener_socket:%\n", __FILE__, __LINE__,
                            __FUNCTION__,
                            Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);
                have_new_connection = true;  // 標記有新連線,稍後處理
                continue;  // 跳過後續處理
            }

            // 一般 Socket: 有資料可讀
            logger_.log("%:% %() % EPOLLIN socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            // 加入接收清單 (避免重複)
            if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                          socket) == receive_sockets_.end()) {
                receive_sockets_.push_back(socket);
            }
        }

        // === 處理 EPOLLOUT (可寫事件) ===
        // 傳送緩衝區有空間,可以傳送資料
        if (event.events & EPOLLOUT) {
            logger_.log("%:% %() % EPOLLOUT socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            // 加入傳送清單 (避免重複)
            if (std::find(send_sockets_.begin(), send_sockets_.end(),
                          socket) == send_sockets_.end()) {
                send_sockets_.push_back(socket);
            }
        }

        // === 處理錯誤/斷線事件 ===
        // EPOLLERR: Socket 錯誤
        // EPOLLHUP: 對端關閉連線
        if (event.events & (EPOLLERR | EPOLLHUP)) {
            logger_.log("%:% %() % EPOLLERR socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                        Common::getCurrentTimeStr(&time_str_), socket->socket_fd_);

            // 將斷線的 Socket 加入接收清單
            // 原因: sendAndRecv() 會讀取 0 位元組,觸發斷線處理
            if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                          socket) == receive_sockets_.end()) {
                receive_sockets_.push_back(socket);
            }
        }
    }

    // === 處理新連線接受 ===
    // 使用 while 迴圈: 一次處理所有待接受的連線
    // ⚠️ Edge-Triggered 模式要求: 必須一次接受所有連線
    while (have_new_connection) {
        logger_.log("%:% %() % have_new_connection\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_));

        // 準備接收對端位址資訊
        sockaddr_storage addr;
        socklen_t addr_len = sizeof(addr);

        // accept: 接受新連線
        // 返回值:
        // - >= 0: 新連線的檔案描述符
        // - -1: 無待接受連線 (EAGAIN) 或錯誤
        int fd = accept(listener_socket_.socket_fd_, reinterpret_cast<sockaddr*>(&addr),
                        &addr_len);

        // 無更多待接受連線
        if (fd == -1) {
            break;
        }

        // 配置新 Socket: 非阻塞 + 禁用 Nagle
        // ⚡ 關鍵優化: 確保新連線也具備低延遲特性
        ASSERT(setNonBlocking(fd) && disableNagle(fd),
               "Failed to set non-blocking or no-delay on socket:" + std::to_string(fd));

        logger_.log("%:% %() % accepted socket:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), fd);

        // 建立新 TCPSocket 物件
        auto socket = new TCPSocket(logger_);
        socket->socket_fd_ = fd;
        socket->recv_callback_ = recv_callback_;  // 繼承伺服器的接收回呼

        // 將新 Socket 加入 Epoll 監控
        ASSERT(addToEpollList(socket),
               "Unable to add socket. error:" + std::string(std::strerror(errno)));

        // 加入接收清單 (避免重複)
        if (std::find(receive_sockets_.begin(), receive_sockets_.end(),
                      socket) == receive_sockets_.end()) {
            receive_sockets_.push_back(socket);
        }
    }
}
}
