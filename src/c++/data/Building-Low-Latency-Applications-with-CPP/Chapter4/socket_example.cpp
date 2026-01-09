// ========================================
// TCP Socket 使用範例
// ========================================
//
// 範例目的:
// 展示如何使用 TCPServer 和 TCPSocket 實現客戶端-伺服器通訊
//
// ⚡ 核心技術:
// 1. 非阻塞 I/O: 所有操作立即返回,無等待
// 2. Epoll 事件循環: TCPServer 使用 epoll 管理多個連線
// 3. Lambda 回調: 自訂處理接收到的資料
// 4. SO_TIMESTAMP: 捕捉核心時間戳(rx_time)
//
// 執行流程:
// 1. 建立 TCPServer,監聽 127.0.0.1:12345
// 2. 建立 5 個 TCPSocket 客戶端連接到伺服器
// 3. 每個客戶端發送 5 輪訊息(共 25 筆)
// 4. 伺服器回應每筆訊息
//
// 關鍵設計:
// - 單執行緒: 所有 I/O 在主執行緒完成,避免執行緒切換
// - 事件驅動: poll() 觸發 epoll_wait,檢查可讀/可寫事件
// - 批次處理: sendAndRecv() 一次性處理所有緩衝資料
//
#include "time_utils.h"
#include "logging.h"
#include "tcp_server.h"

int main(int, char**)
{
    using namespace Common;

    std::string time_str_;
    Logger logger_("socket_example.log");

    // ========================================
    // TCPServer 回調函數配置
    // ========================================

    // tcpServerRecvCallback: 伺服器接收資料時的處理邏輯
    // @param socket: 接收到資料的客戶端連線
    // @param rx_time: 核心時間戳(SO_TIMESTAMP 捕捉的接收時間)
    //
    // ⚡ 典型流程:
    // 1. 記錄接收日誌(socket fd, 資料長度, 時間戳)
    // 2. 處理接收到的資料(解析協議、業務邏輯)
    // 3. 準備回應並發送
    // 4. 重置接收緩衝區索引
    //
    // ⚠️ 重要: 此回調在 poll() 中被觸發
    // 原因: poll() → epoll_wait() → EPOLLIN 事件 → 呼叫此回調
    auto tcpServerRecvCallback = [&](TCPSocket * socket, Nanos rx_time) noexcept {
        logger_.log("TCPServer::defaultRecvCallback() socket:% len:% rx:%\n",
                    socket->socket_fd_, socket->next_rcv_valid_index_, rx_time);

        // 建立回應訊息(Echo Server 模式)
        // ⚡ 字串拼接: "TCPServer received msg:" + 客戶端訊息
        const std::string reply = "TCPServer received msg:" + std::string(
                                      socket->inbound_data_.data(), socket->next_rcv_valid_index_);

        // ⚠️ 關鍵: 重置接收緩衝區索引
        // 原因: 下次接收從頭開始寫入,避免舊資料殘留
        socket->next_rcv_valid_index_ = 0;

        // ⚡ 累積回應到發送緩衝區(不立即發送)
        // 實際發送由 sendAndRecv() 批次處理
        socket->send(reply.data(), reply.length());
    };

    // tcpServerRecvFinishedCallback: 單輪 poll 結束後的回調
    // 用途: 記錄日誌、統計、清理等
    //
    // ⚡ 觸發時機:
    // poll() 處理完所有就緒的事件後呼叫此函數
    auto tcpServerRecvFinishedCallback = [&]() noexcept {
        logger_.log("TCPServer::defaultRecvFinishedCallback()\n");
    };

    // tcpClientRecvCallback: 客戶端接收伺服器回應的處理邏輯
    // @param socket: 客戶端 Socket
    // @param rx_time: 核心時間戳
    //
    // ⚡ 客戶端行為:
    // 1. 讀取伺服器回應
    // 2. 記錄日誌(驗證伺服器是否正確回應)
    // 3. 重置接收緩衝區
    auto tcpClientRecvCallback = [&](TCPSocket * socket, Nanos rx_time) noexcept {
        const std::string recv_msg = std::string(socket->inbound_data_.data(),
                                     socket->next_rcv_valid_index_);
        socket->next_rcv_valid_index_ = 0;

        logger_.log("TCPSocket::defaultRecvCallback() socket:% len:% rx:% msg:%\n",
                    socket->socket_fd_, socket->next_rcv_valid_index_, rx_time, recv_msg);
    };

    // ========================================
    // 伺服器配置與啟動
    // ========================================

    const std::string iface = "lo";        // Loopback 網卡(本地測試)
    const std::string ip = "127.0.0.1";    // Localhost
    const int port = 12345;                // 監聽埠號

    logger_.log("Creating TCPServer on iface:% port:%\n", iface, port);

    // 建立 TCPServer 實例
    // ⚡ 內部行為:
    // 1. 建立 epoll 實例(epoll_create1)
    // 2. 初始化連線管理結構(receive_sockets_、send_sockets_)
    TCPServer server(logger_);

    // 設定回調函數
    // ⚠️ 必須在 listen() 之前設定
    server.recv_callback_ = tcpServerRecvCallback;
    server.recv_finished_callback_ = tcpServerRecvFinishedCallback;

    // 開始監聽
    // ⚡ 內部行為:
    // 1. 建立監聽 Socket(socket + bind + listen)
    // 2. 設定非阻塞模式(O_NONBLOCK)
    // 3. 加入 epoll 監聽(EPOLLIN | EPOLLET - Edge Triggered)
    server.listen(iface, port);

    // ========================================
    // 客戶端建立與連線
    // ========================================

    std::vector<TCPSocket*> clients(5);  // 建立 5 個客戶端連線

    for (size_t i = 0; i < clients.size(); ++i) {
        // 建立 TCPSocket 客戶端
        clients[i] = new TCPSocket(logger_);
        clients[i]->recv_callback_ = tcpClientRecvCallback;

        logger_.log("Connecting TCPClient-[%] on ip:% iface:% port:%\n", i, ip, iface,
                    port);

        // 連接到伺服器
        // @param needs_so_timestamp: false = 不需要核心時間戳(客戶端通常不需要)
        //
        // ⚡ 內部行為:
        // 1. 建立 Socket(socket)
        // 2. 設定非阻塞模式
        // 3. 發起連線(connect,可能返回 EINPROGRESS)
        // 4. 設定 TCP_NODELAY(禁用 Nagle 演算法)
        clients[i]->connect(ip, iface, port, false);

        // ⚡ 關鍵: 呼叫 poll() 處理新連線
        // 原因:
        // 1. epoll_wait 檢測到監聽 Socket 的 EPOLLIN 事件
        // 2. 伺服器執行 accept() 接受連線
        // 3. 新連線加入 epoll 監聽(EPOLLIN | EPOLLET)
        server.poll();
    }

    // ========================================
    // 客戶端-伺服器互動循環
    // ========================================

    using namespace std::literals::chrono_literals;

    // 外層迴圈: 5 輪訊息
    // 內層迴圈: 5 個客戶端
    // 總共發送: 5 * 5 = 25 筆訊息
    for (auto itr = 0; itr < 5; ++itr) {
        for (size_t i = 0; i < clients.size(); ++i) {
            // 建立客戶端訊息
            // 格式: "CLIENT-[i] : Sending [編號]"
            const std::string client_msg = "CLIENT-[" + std::to_string(
                                               i) + "] : Sending " + std::to_string(itr * 100 + i);

            logger_.log("Sending TCPClient-[%] %\n", i, client_msg);

            // ⚡ 步驟 1: 累積資料到發送緩衝區
            // 不立即發送,由 sendAndRecv() 批次處理
            clients[i]->send(client_msg.data(), client_msg.length());

            // ⚡ 步驟 2: 批次發送並接收
            // 內部行為:
            // 1. send() 發送緩衝區資料(若非空)
            // 2. recv() 接收伺服器回應(非阻塞)
            // 3. 若有資料,觸發 recv_callback_
            clients[i]->sendAndRecv();

            // 延遲 500ms(模擬真實應用的處理時間)
            std::this_thread::sleep_for(500ms);

            // ⚡ 步驟 3: 伺服器處理事件
            // 內部行為:
            // 1. epoll_wait() 檢查所有 Socket 的事件
            // 2. EPOLLIN: 呼叫 recv() 並觸發 recv_callback_
            // 3. EPOLLOUT: 標記 Socket 可寫入
            server.poll();

            // ⚡ 步驟 4: 伺服器批次發送回應
            // 內部行為:
            // 遍歷 send_sockets_,將所有緩衝的回應發送出去
            server.sendAndRecv();
        }
    }

    // ⚠️ 注意: 程式結束時未呼叫 delete
    // 原因: 簡化範例,實際應用需要釋放資源
    // 正確做法:
    // for (auto* client : clients) delete client;

    return 0;
}

// ========================================
// 預期輸出分析:
// ========================================
//
// 日誌順序:
// 1. Creating TCPServer on iface:lo port:12345
// 2. Connecting TCPClient-[0~4] ...
// 3. (重複 25 次)
//    - Sending TCPClient-[i] CLIENT-[i] : Sending [編號]
//    - TCPServer::defaultRecvCallback() ... (伺服器接收)
//    - TCPSocket::defaultRecvCallback() ... (客戶端接收回應)
//    - TCPServer::defaultRecvFinishedCallback()
//
// 時間戳觀察:
// - rx_time: 核心捕捉的接收時間(奈秒級精度)
// - 可用於計算延遲: send_time → rx_time
//
// ========================================
// 效能分析:
// ========================================
//
// 單次 sendAndRecv() 延遲:
// - 無資料時: ~1-2μs (系統呼叫開銷)
// - 有資料時: ~5-10μs (含資料複製)
//
// poll() 延遲:
// - 無事件時: ~1-2μs (epoll_wait 立即返回)
// - 有事件時: ~5-20μs (視連線數量)
//
// Loopback 延遲:
// - RTT: ~10-50μs (本地迴環,無網卡開銷)
//
// 與阻塞 I/O 比較:
// | 操作          | 阻塞 I/O  | 非阻塞 I/O | 優勢      |
// |---------------|-----------|------------|-----------|
// | recv() 等待   | 阻塞      | 立即返回   | 無等待    |
// | 多連線管理    | 多執行緒  | 單執行緒   | 無切換    |
// | CPU 利用率    | 低(等待)  | 高(輪詢)   | 更高效    |
//
// ========================================
// 使用建議:
// ========================================
//
// ✅ 適合場景:
// - 高併發連線(數千~數萬連線)
// - 低延遲需求(微秒級 RTT)
// - 單執行緒事件循環架構
//
// ⚠️ 常見陷阱:
// 1. 忘記呼叫 poll()
//    ❌ clients[i]->sendAndRecv();  // 伺服器不會處理
//    ✅ clients[i]->sendAndRecv(); server.poll();
//
// 2. recv_callback_ 中執行耗時操作
//    ❌ 在回調中進行資料庫查詢、檔案 I/O
//    原因: 會阻塞事件循環,影響其他連線
//    ✅ 將耗時操作放入工作佇列,交由背景執行緒處理
//
// 3. 未檢查連線狀態
//    ❌ socket->send(...);  // Socket 可能已斷線
//    ✅ if (socket->socket_fd_ != -1) socket->send(...);
//
// ========================================
// 進階優化:
// ========================================
//
// 1. SO_REUSEPORT:
//    多個執行緒/行程監聽同一埠,核心自動負載均衡
//    適合高併發場景(每秒數萬連線)
//
// 2. TCP_QUICKACK:
//    禁用延遲 ACK,降低延遲(~40ms → 即時)
//    trade-off: 增加 ACK 封包數量
//
// 3. CPU Affinity:
//    綁定執行緒到特定核心,避免 L1/L2 Cache Miss
//    範例: server 執行緒綁定 Core 0,客戶端執行緒綁定 Core 1
//
