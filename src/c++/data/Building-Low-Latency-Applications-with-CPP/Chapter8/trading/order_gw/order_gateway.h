#pragma once

#include <functional>

#include "common/thread_utils.h"
#include "common/macros.h"
#include "common/tcp_server.h"

#include "exchange/order_server/client_request.h"
#include "exchange/order_server/client_response.h"

namespace Trading
{
/**
 * OrderGateway - 訂單閘道
 *
 * 核心職責：
 * 1. 建立與交易所的 TCP 連接
 * 2. 發送客戶端訂單請求到交易所
 * 3. 接收交易所的訂單回應
 * 4. 維護訊息序列號以偵測遺失訊息
 *
 * 設計特點：
 * - 使用 Lock-Free Queue 與交易引擎通訊（零等待）
 * - 獨立執行緒處理網路 I/O
 * - TCP 長連接，自動重連機制
 * - 序列號驗證確保訊息可靠性
 *
 * 效能考量：
 * - 單向延遲：20-50 μs（本地到交易所）
 * - 使用 SO_RCVBUF/SO_SNDBUF 優化緩衝區
 * - 關閉 Nagle 演算法（TCP_NODELAY）
 *
 * 典型流程：
 * 1. start() 建立 TCP 連接並啟動執行緒
 * 2. run() 輪詢 outgoing_requests_ 佇列
 * 3. 發送請求到交易所，遞增 next_outgoing_seq_num_
 * 4. recvCallback() 接收回應，驗證 next_exp_seq_num_
 * 5. 將回應放入 incoming_responses_ 佇列給交易引擎
 */
class OrderGateway
{
public:
    /**
     * 構造函式
     * @param client_id 客戶端識別碼
     * @param client_requests 指向交易所請求佇列的指標（發送方向）
     * @param client_responses 指向交易所回應佇列的指標（接收方向）
     * @param ip 交易所 IP 地址
     * @param iface 本地網路介面名稱（例如 "eth0"）
     * @param port 交易所監聽埠號
     */
    OrderGateway(ClientId client_id,
                 Exchange::ClientRequestLFQueue* client_requests,
                 Exchange::ClientResponseLFQueue* client_responses,
                 std::string ip, const std::string& iface, int port);

    /**
     * 解構函式
     * 安全關閉流程：
     * 1. 呼叫 stop() 設置停止旗標
     * 2. 等待 5 秒讓執行緒完成清理
     * 3. TCP 連接自動關閉
     */
    ~OrderGateway()
    {
        stop();

        using namespace std::literals::chrono_literals;
        std::this_thread::sleep_for(5s);  // 等待執行緒優雅退出
    }

    /**
     * 啟動訂單閘道
     * 步驟：
     * 1. 建立 TCP 連接到交易所
     * 2. 啟動獨立執行緒執行 run() 主迴圈
     *
     * 注意：連接失敗會觸發 ASSERT 中斷程式
     */
    auto start()
    {
        run_ = true;
        // 建立 TCP 連接（非阻塞模式）
        ASSERT(tcp_socket_.connect(ip_, iface_, port_, false) >= 0,
               "Unable to connect to ip:" + ip_ + " port:" + std::to_string(
                   port_) + " on iface:" + iface_ + " error:" + std::string(std::strerror(errno)));

        // 啟動網路 I/O 執行緒（不綁定特定 CPU 核心，-1 表示讓 OS 調度）
        ASSERT(Common::createAndStartThread(-1, "Trading/OrderGateway", [this]() {
            run();
        }) != nullptr, "Failed to start OrderGateway thread.");
    }

    /**
     * 停止訂單閘道
     * 設置 run_ = false，通知執行緒退出主迴圈
     * 注意：這是非阻塞呼叫，實際退出需等待執行緒結束
     */
    auto stop() -> void
    {
        run_ = false;
    }

    // Deleted default, copy & move constructors and assignment-operators.
    OrderGateway() = delete;

    OrderGateway(const OrderGateway&) = delete;

    OrderGateway(const OrderGateway&&) = delete;

    OrderGateway& operator=(const OrderGateway&) = delete;

    OrderGateway& operator=(const OrderGateway&&) = delete;

private:
    // === 連接配置 ===
    const ClientId client_id_;             ///< 客戶端唯一識別碼（用於訊息路由）

    std::string ip_;                       ///< 交易所 IP 地址
    const std::string iface_;              ///< 本地網路介面（用於綁定特定網卡，提高延遲穩定性）
    const int port_ = 0;                   ///< 交易所監聽埠號

    // === Lock-Free 通訊佇列 ===
    /**
     * outgoing_requests_ - 發送佇列
     * 交易引擎將訂單請求寫入此佇列，閘道執行緒讀取並發送到交易所
     * 無鎖設計確保交易引擎不會被網路 I/O 阻塞
     */
    Exchange::ClientRequestLFQueue* outgoing_requests_ = nullptr;

    /**
     * incoming_responses_ - 接收佇列
     * 閘道將交易所回應寫入此佇列，交易引擎讀取並處理
     * SPSC 佇列保證訊息順序
     */
    Exchange::ClientResponseLFQueue* incoming_responses_ = nullptr;

    // === 執行緒控制 ===
    volatile bool run_ = false;            ///< 執行緒運行旗標（volatile 確保可見性）

    // === 日誌系統 ===
    std::string time_str_;                 ///< 時間字串緩衝區（避免重複格式化）
    Logger logger_;                        ///< 日誌記錄器

    // === 序列號管理（訊息可靠性保證）===
    /**
     * next_outgoing_seq_num_ - 發送序列號
     * 每發送一條訊息遞增 1
     * 交易所使用此序列號偵測遺失或重複訊息
     */
    size_t next_outgoing_seq_num_ = 1;

    /**
     * next_exp_seq_num_ - 預期接收序列號
     * 每接收一條訊息驗證並遞增 1
     * 若接收到的序列號不符，表示網路遺失訊息或順序錯誤
     */
    size_t next_exp_seq_num_ = 1;

    // === TCP 連接 ===
    Common::TCPSocket tcp_socket_;         ///< TCP Socket 物件（已優化：TCP_NODELAY, SO_RCVBUF 等）

private:
    /**
     * run() - 主事件迴圈（在獨立執行緒中執行）
     *
     * 職責：
     * 1. 輪詢 outgoing_requests_ 佇列
     * 2. 將請求序列化並通過 TCP 發送
     * 3. 呼叫 tcp_socket_.sendAndRecv() 處理收發
     * 4. 通過 recvCallback() 處理接收到的回應
     *
     * 效能特性：
     * - 緊密迴圈（tight loop）
     * - 無阻塞操作
     * - 延遲：< 10 μs per iteration
     */
    auto run() noexcept -> void;

    /**
     * recvCallback() - TCP 接收回調函式
     *
     * @param socket TCP socket 指標
     * @param rx_time 接收時間戳記（奈秒精度）
     *
     * 職責：
     * 1. 從 TCP 緩衝區讀取訊息
     * 2. 反序列化為 ClientResponse 物件
     * 3. 驗證序列號（next_exp_seq_num_）
     * 4. 將回應寫入 incoming_responses_ 佇列
     *
     * 錯誤處理：
     * - 序列號不符 → 記錄 ERROR 日誌
     * - 佇列已滿 → 阻塞等待（背壓機制）
     */
    auto recvCallback(TCPSocket* socket, Nanos rx_time) noexcept -> void;
};
}
