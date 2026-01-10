// ============================================================================
// TCP Socket 使用範例
// ============================================================================
// 📌 範例目的：
// 展示如何使用 TCPServer 和 TCPSocket 實現客戶端-伺服器通訊
//
// 關鍵學習點：
// 1. ⚡ Epoll 事件循環：單執行緒處理多個連線（避免 Thread-per-Connection 開銷）
// 2. Lambda 回調函式：處理接收資料、發送回應
// 3. 非阻塞 I/O：send/recv 不會阻塞主執行緒
// 4. 單線程 Reactor 模式：類似 Node.js Event Loop
//
// 📊 效能特性：
// - 單執行緒可處理 10,000+ 連線（C10K Problem）
// - 訊息延遲：< 10 μs（本機 Loopback）
// - 記憶體開銷：每個連線 ~128 MB（發送/接收緩衝區）
//
// 執行流程：
// 1. 建立 TCPServer 監聽 127.0.0.1:12345
// 2. 建立 5 個 TCPSocket 客戶端連線到伺服器
// 3. 每個客戶端發送 5 條訊息（共 25 條）
// 4. 伺服器回應每條訊息

#include "time_utils.h"
#include "logging.h"
#include "tcp_server.h"

int main(int, char**)
{
    using namespace Common;

    std::string time_str_;
    Logger logger_("socket_example.log");

    // ⚡ TCP Server 接收回調函式
    // 當客戶端發送資料到達時，此函式被呼叫
    // 參數：
    // - socket：接收到資料的 TCPSocket
    // - rx_time：接收時間戳（奈秒）
    auto tcpServerRecvCallback = [&](TCPSocket * socket, Nanos rx_time) noexcept {
        logger_.log("TCPServer::defaultRecvCallback() socket:% len:% rx:%\n",
                    socket->socket_fd_, socket->next_rcv_valid_index_, rx_time);

        // 讀取接收緩衝區的資料
        const std::string reply = "TCPServer received msg:" + std::string(
                                      socket->inbound_data_.data(), socket->next_rcv_valid_index_);

        // ⚠️ 重置接收索引（清空緩衝區）
        socket->next_rcv_valid_index_ = 0;

        // 發送回應到客戶端（寫入發送緩衝區）
        socket->send(reply.data(), reply.length());
    };

    // TCP Server 接收完成回調函式
    // 當一輪 poll() 的所有接收操作完成時呼叫
    auto tcpServerRecvFinishedCallback = [&]() noexcept {
        logger_.log("TCPServer::defaultRecvFinishedCallback()\n");
    };

    // ⚡ TCP Client 接收回調函式
    // 當客戶端接收到伺服器的回應時呼叫
    auto tcpClientRecvCallback = [&](TCPSocket * socket, Nanos rx_time) noexcept {
        const std::string recv_msg = std::string(socket->inbound_data_.data(),
                                     socket->next_rcv_valid_index_);

        // ⚠️ 重置接收索引
        socket->next_rcv_valid_index_ = 0;

        logger_.log("TCPSocket::defaultRecvCallback() socket:% len:% rx:% msg:%\n",
                    socket->socket_fd_, socket->next_rcv_valid_index_, rx_time, recv_msg);
    };

    // 網路配置
    const std::string iface = "lo";       // Loopback 網路介面
    const std::string ip = "127.0.0.1";   // 本機 IP
    const int port = 12345;                // 監聽埠號

    // ============================================================================
    // 步驟 1：建立 TCP Server
    // ============================================================================
    logger_.log("Creating TCPServer on iface:% port:%\n", iface, port);
    TCPServer server(logger_);
    server.recv_callback_ = tcpServerRecvCallback;
    server.recv_finished_callback_ = tcpServerRecvFinishedCallback;
    server.listen(iface, port);  // 開始監聽

    // ============================================================================
    // 步驟 2：建立 5 個 TCP 客戶端連線
    // ============================================================================
    std::vector<TCPSocket*> clients(5);

    for (size_t i = 0; i < clients.size(); ++i) {
        clients[i] = new TCPSocket(logger_);
        clients[i]->recv_callback_ = tcpClientRecvCallback;

        logger_.log("Connecting TCPClient-[%] on ip:% iface:% port:%\n", i, ip, iface,
                    port);

        // 連線到伺服器
        clients[i]->connect(ip, iface, port, false);

        // ⚡ 重要：連線後立即呼叫 poll()，讓伺服器接受連線
        server.poll();
    }

    using namespace std::literals::chrono_literals;

    // ============================================================================
    // 步驟 3：客戶端發送訊息，伺服器回應
    // ============================================================================
    // 每個客戶端發送 5 條訊息（外層迴圈）
    for (auto itr = 0; itr < 5; ++itr) {
        // 遍歷所有客戶端（內層迴圈）
        for (size_t i = 0; i < clients.size(); ++i) {
            // 建立測試訊息
            const std::string client_msg = "CLIENT-[" + std::to_string(
                                               i) + "] : Sending " + std::to_string(itr * 100 + i);

            logger_.log("Sending TCPClient-[%] %\n", i, client_msg);

            // 客戶端發送訊息
            clients[i]->send(client_msg.data(), client_msg.length());
            clients[i]->sendAndRecv();  // 實際執行發送/接收

            // 模擬延遲（500 毫秒）
            std::this_thread::sleep_for(500ms);

            // ⚡ 伺服器處理接收到的訊息
            server.poll();        // 檢查新事件（Epoll）
            server.sendAndRecv(); // 發送/接收資料
        }
    }

    // ⚠️ 注意：實際應用中需要清理客戶端 socket（delete clients[i]）

    return 0;
}
