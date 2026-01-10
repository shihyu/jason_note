// ============================================================================
// OrderServer 實作檔案
// ============================================================================
//
// 職責:
// - 建構與初始化 OrderServer (TCP 伺服器、FIFOSequencer、序列號管理)
// - 啟動與停止執行緒
//
// 說明:
// 主要業務邏輯 (run, recvCallback, recvFinishedCallback) 都在 header 中以 inline 方式實作,
// 此檔案僅包含建構/解構與生命週期管理。
//
// ============================================================================

#include "order_server.h"

namespace Exchange
{
// ============================================================================
// 建構函式
// ============================================================================
//
// 參數說明:
// - client_requests:  傳給 Matching Engine 的訂單請求佇列 (透過 FIFOSequencer)
// - client_responses: 從 Matching Engine 接收回應的佇列 (回傳給 Client)
// - iface:           監聽的網路介面 (例如 "0.0.0.0")
// - port:            監聽的 TCP Port
//
// 初始化流程:
// 1. 初始化成員變數 (介面、Port、Logger、TCP Server、FIFO Sequencer)
// 2. 初始化序列號陣列:
//    - cid_next_outgoing_seq_num_: 每個 Client 的下一個發送序列號 (初始值 1)
//    - cid_next_exp_seq_num_:      每個 Client 的預期接收序列號 (初始值 1)
//    - cid_tcp_socket_:            每個 Client 的 TCP Socket 映射 (初始值 nullptr)
// 3. 設定 TCP Server 回調函式:
//    - recv_callback_:          接收到資料時觸發 → recvCallback()
//    - recv_finished_callback_: 完成所有接收後觸發 → recvFinishedCallback()
//
// ⚡ 效能關鍵:
// - 使用 std::array 而非 std::vector (編譯時已知大小, 無動態分配)
// - Lambda 捕獲 [this] 避免 std::function 的虛擬呼叫開銷
//
// ⚠️ 注意:
// - 序列號從 1 開始 (0 保留為無效值)
// - Socket 映射在首次收到訊息時才建立 (recvCallback 中)
//
OrderServer::OrderServer(ClientRequestLFQueue* client_requests,
                         ClientResponseLFQueue* client_responses, const std::string& iface, int port)
    : iface_(iface), port_(port), outgoing_responses_(client_responses),
      logger_("exchange_order_server.log"),
      tcp_server_(logger_), fifo_sequencer_(client_requests, &logger_)
{
    // 初始化序列號陣列 (所有 Client 從 1 開始)
    cid_next_outgoing_seq_num_.fill(1);
    cid_next_exp_seq_num_.fill(1);
    cid_tcp_socket_.fill(nullptr);

    // 設定 TCP 接收回調: 收到資料時處理請求並驗證序列號
    tcp_server_.recv_callback_ = [this](auto socket, auto rx_time) {
        recvCallback(socket, rx_time);
    };

    // 設定接收完成回調: 觸發 FIFOSequencer 排序與發布
    tcp_server_.recv_finished_callback_ = [this]() {
        recvFinishedCallback();
    };
}

// ============================================================================
// 解構函式
// ============================================================================
//
// 清理邏輯:
// 1. 呼叫 stop() 設定 run_ = false, 停止主執行緒迴圈
// 2. 等待 1 秒讓執行緒安全結束
//
// ⚠️ 注意:
// - 1 秒等待是給 run() 迴圈一個 graceful shutdown 的緩衝時間
// - 如果執行緒卡住超過 1 秒, 程式結束時可能會強制終止 (undefined behavior)
// - 生產環境建議使用 std::thread::join() 確保執行緒結束
//
OrderServer::~OrderServer()
{
    stop(); // 設定 run_ = false

    // 等待 1 秒讓執行緒自然結束 (簡化版本, 生產環境應使用 thread::join)
    using namespace std::literals::chrono_literals;
    std::this_thread::sleep_for(1s);
}

// ============================================================================
// 啟動伺服器
// ============================================================================
//
// 啟動流程:
// 1. 設定 run_ = true (執行緒迴圈繼續條件)
// 2. 呼叫 tcp_server_.listen() 開始監聽 TCP 連線
// 3. 創建執行緒並執行 run() 主迴圈
//
// 執行緒配置:
// - CPU Affinity: -1 (不綁定特定核心, 由 OS 排程)
// - Thread Name: "Exchange/OrderServer" (方便 perf/htop 除錯)
// - 執行函式: run() (處理網路 I/O 與回應轉發)
//
// ⚡ 效能考量:
// - 如需極致低延遲, 可指定 CPU Core (避免 Context Switch)
// - listen() 內部使用 epoll (Linux) 或 kqueue (macOS) 高效輪詢
//
// ⚠️ 注意:
// - 必須在建構完成後呼叫 start()
// - ASSERT 失敗會終止程式 (Production 環境應改為錯誤處理)
//
auto OrderServer::start() -> void
{
    run_ = true; // 啟動執行緒迴圈

    // 開始監聽 TCP 連線 (Epoll 模式)
    tcp_server_.listen(iface_, port_);

    // 創建執行緒執行 run() 主迴圈 (不綁定 CPU, 由 OS 排程)
    ASSERT(Common::createAndStartThread(-1, "Exchange/OrderServer", [this]() {
        run();
    }) != nullptr, "Failed to start OrderServer thread.");
}

// ============================================================================
// 停止伺服器
// ============================================================================
//
// 停止邏輯:
// - 設定 run_ = false, 讓 run() 迴圈自然退出
//
// ⚡ 效能關鍵:
// - run_ 宣告為 volatile, 確保編譯器不會快取此變數
// - 主執行緒迴圈 (run()) 會在下一次檢查 while (run_) 時退出
//
// ⚠️ 注意:
// - 此方法不會阻塞等待執行緒結束
// - 解構函式會等待 1 秒讓執行緒安全結束
// - 如需即時停止, 應在呼叫 stop() 後手動 join 執行緒
//
auto OrderServer::stop() -> void
{
    run_ = false; // 設定停止旗標, 讓 run() 迴圈退出
}
} // namespace Exchange
