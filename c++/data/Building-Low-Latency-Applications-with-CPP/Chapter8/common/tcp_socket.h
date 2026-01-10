#pragma once

#include <functional>

#include "socket_utils.h"
#include "logging.h"

namespace Common
{
/**
 * TCPBufferSize - TCP 發送/接收緩衝區大小
 *
 * 設定為 64 MB (64 * 1024 * 1024 bytes)
 *
 * 設計理由：
 * - 大緩衝區減少系統呼叫次數（批次處理）
 * - 適合高頻交易場景（每秒數萬筆訊息）
 * - 避免緩衝區溢位導致阻塞或丟包
 *
 * 權衡考量：
 * - 優點：高吞吐量，減少延遲變異
 * - 缺點：佔用記憶體（每個 socket 128 MB）
 *
 * 效能影響：
 * - SO_SNDBUF/SO_RCVBUF 設定會影響核心緩衝區大小
 * - 應用層緩衝區避免頻繁系統呼叫
 */
constexpr size_t TCPBufferSize = 64 * 1024 * 1024;

/**
 * TCPSocket - 低延遲 TCP Socket 封裝
 *
 * 設計目標：
 * - 最小化延遲（< 10 μs per operation）
 * - 高吞吐量（支援每秒數萬筆訊息）
 * - 零拷貝設計（直接操作緩衝區）
 *
 * 核心特性：
 * 1. 大緩衝區（64 MB 發送 + 64 MB 接收）
 * 2. 非阻塞 I/O（不會卡住主執行緒）
 * 3. 回調機制（資料到達時觸發）
 * 4. 批次發送（減少系統呼叫）
 *
 * 典型使用場景：
 * - 訂單閘道（連接到交易所）
 * - TCP 伺服器（接受客戶端連接）
 * - 市場數據訂閱（雖然通常用 multicast）
 *
 * 優化細節：
 * - TCP_NODELAY：關閉 Nagle 演算法，立即發送小封包
 * - SO_RCVBUF/SO_SNDBUF：設定核心緩衝區大小
 * - 非阻塞模式：避免 recv()/send() 阻塞
 *
 * 使用範例：
 * ```cpp
 * TCPSocket socket(logger);
 * socket.connect("192.168.1.100", "eth0", 8080, false);  // 客戶端模式
 * socket.recv_callback_ = [](auto* s, auto rx_time) {
 *     // 處理接收到的資料
 * };
 * while (true) {
 *     socket.send(data, len);      // 寫入發送緩衝區
 *     socket.sendAndRecv();        // 實際收發
 * }
 * ```
 */
struct TCPSocket {
    /**
     * 構造函式
     * @param logger 日誌記錄器引用
     *
     * 初始化流程：
     * 1. 預配置發送緩衝區（64 MB）
     * 2. 預配置接收緩衝區（64 MB）
     * 3. 儲存日誌記錄器引用
     *
     * 注意：
     * - 緩衝區在構造時就分配（避免動態擴容）
     * - 每個 TCPSocket 實例佔用 128 MB 記憶體
     */
    explicit TCPSocket(Logger& logger)
        : logger_(logger)
    {
        outbound_data_.resize(TCPBufferSize);  // 預配置發送緩衝區
        inbound_data_.resize(TCPBufferSize);   // 預配置接收緩衝區
    }

    /**
     * connect() - 建立或監聽 TCP 連接
     *
     * @param ip 目標 IP 地址（客戶端模式）或綁定 IP（伺服器模式）
     * @param iface 本地網路介面名稱（例如 "eth0"）
     * @param port 目標埠號（客戶端模式）或監聽埠號（伺服器模式）
     * @param is_listening true=伺服器模式（監聽），false=客戶端模式（連接）
     * @return 成功返回 0，失敗返回 -1
     *
     * 功能：
     * - 客戶端模式（is_listening=false）：
     *   - 建立 socket，連接到指定 IP:Port
     *   - 設定 TCP_NODELAY、SO_RCVBUF、SO_SNDBUF
     *   - 設定非阻塞模式
     *
     * - 伺服器模式（is_listening=true）：
     *   - 建立 socket，綁定到指定 IP:Port
     *   - 設定 SO_REUSEADDR、SO_REUSEPORT
     *   - 開始監聽（listen）
     *
     * 低延遲優化：
     * - TCP_NODELAY：關閉 Nagle 演算法（立即發送小封包）
     * - 大緩衝區：減少系統呼叫次數
     * - 非阻塞模式：避免阻塞主執行緒
     * - 網路介面綁定：減少路由查找時間
     */
    auto connect(const std::string& ip, const std::string& iface, int port,
                 bool is_listening) -> int;

    /**
     * sendAndRecv() - 執行實際的 TCP 收發操作
     *
     * @return 成功返回 true，失敗返回 false
     *
     * 職責：
     * 1. 發送緩衝區資料：
     *    - 呼叫 ::send() 將 outbound_data_ 中的資料發送出去
     *    - 更新 next_send_valid_index_（標記已發送的資料）
     *    - 部分發送時記錄未發送的資料量
     *
     * 2. 接收資料：
     *    - 呼叫 ::recv() 從 socket 讀取資料到 inbound_data_
     *    - 更新 next_rcv_valid_index_（標記有效資料長度）
     *    - 若有新資料到達，觸發 recv_callback_
     *
     * 效能特性：
     * - 非阻塞操作（EAGAIN/EWOULDBLOCK 視為正常）
     * - 批次處理（一次發送/接收多個訊息）
     * - 回調延遲：< 5 μs
     *
     * 注意：
     * - 需要在主迴圈中頻繁呼叫（緊密迴圈）
     * - 發送失敗會累積在緩衝區中，下次繼續發送
     */
    auto sendAndRecv() noexcept -> bool;

    /**
     * send() - 將資料寫入發送緩衝區
     *
     * @param data 資料指標
     * @param len 資料長度（bytes）
     *
     * 職責：
     * - 將資料拷貝到 outbound_data_ 緩衝區
     * - 更新 next_send_valid_index_
     * - 不執行實際發送（由 sendAndRecv() 執行）
     *
     * 設計理由：
     * - 分離緩衝和發送邏輯（減少系統呼叫）
     * - 支援批次發送（多次 send() 後一次 sendAndRecv()）
     *
     * ⚠️ 緩衝區溢位風險：
     * - 當前實作無邊界檢查（為了效能）
     * - 若累積的資料超過 64 MB，會發生緩衝區溢位
     * - 溢位行為：
     *   1. 記憶體越界（Undefined Behavior）
     *   2. 可能覆蓋相鄰記憶體（導致程式崩潰或安全問題）
     *   3. 難以除錯（症狀可能在遠離溢位點的地方出現）
     *
     * 🔧 使用者責任：
     * 1. 單次發送不超過緩衝區大小：
     *    ```cpp
     *    if (len > TCPBufferSize) {
     *        logger.log("ERROR: Message too large: % bytes\n", len);
     *        return;
     *    }
     *    ```
     *
     * 2. 頻繁呼叫 sendAndRecv() 清空緩衝區：
     *    ```cpp
     *    socket.send(msg1, len1);
     *    socket.send(msg2, len2);
     *    socket.sendAndRecv();  // 清空緩衝區
     *    ```
     *
     * 3. 監控緩衝區使用率：
     *    ```cpp
     *    if (next_send_valid_index_ > TCPBufferSize * 0.8) {
     *        logger.log("WARNING: Send buffer 80%% full\n");
     *    }
     *    ```
     *
     * 🔧 生產環境建議（新增邊界檢查）：
     * ```cpp
     * auto send(const void* data, size_t len) noexcept -> void {
     *     // 方案 1：斷言檢查（Debug 模式）
     *     ASSERT(next_send_valid_index_ + len <= outbound_data_.size(),
     *            "Send buffer overflow");
     *
     *     // 方案 2：靜默丟棄（Release 模式）
     *     if (next_send_valid_index_ + len > outbound_data_.size()) {
     *         logger.log("ERROR: Send buffer full, dropping % bytes\n", len);
     *         return;
     *     }
     *
     *     // 方案 3：強制發送舊資料
     *     if (next_send_valid_index_ + len > outbound_data_.size()) {
     *         sendAndRecv();  // 清空緩衝區
     *     }
     *
     *     // 正常拷貝資料...
     * }
     * ```
     *
     * 📊 緩衝區容量估算：
     * - 假設平均訊息大小：100 bytes
     * - 發送頻率：10,000 msg/s
     * - sendAndRecv() 呼叫頻率：1,000 次/s
     * - 需要緩衝區：100 bytes × (10,000 ÷ 1,000) = 1,000 bytes
     * - 64 MB 緩衝區足夠應付極端情況（例如網路暫時阻塞）
     *
     * ⚠️ 特殊情況：網路擁塞
     * - 若 sendAndRecv() 無法清空緩衝區（例如 TCP 接收窗口滿）
     * - 持續呼叫 send() 最終會溢位
     * - 建議監控 sendAndRecv() 的返回值與實際發送量
     *
     * 📚 替代設計：動態緩衝區
     * ```cpp
     * std::deque<std::vector<char>> outbound_queue_;  // 多個小緩衝區
     * ```
     * - 優點：避免溢位（可動態擴展）
     * - 缺點：記憶體分配開銷、Cache Locality 較差
     */
    auto send(const void* data, size_t len) noexcept -> void;

    // 禁止預設建構、拷貝和移動
    TCPSocket() = delete;
    TCPSocket(const TCPSocket&) = delete;
    TCPSocket(const TCPSocket&&) = delete;
    TCPSocket& operator=(const TCPSocket&) = delete;
    TCPSocket& operator=(const TCPSocket&&) = delete;

    // === Socket 檔案描述符 ===
    /**
     * socket_fd_ - Socket 檔案描述符
     * -1 表示未初始化或已關閉
     * > 0 表示有效的 socket
     */
    int socket_fd_ = -1;

    // === 發送緩衝區 ===
    /**
     * outbound_data_ - 發送緩衝區（64 MB）
     * 儲存待發送的資料
     */
    std::vector<char> outbound_data_;

    /**
     * next_send_valid_index_ - 發送緩衝區有效資料結束位置
     * 表示 [0, next_send_valid_index_) 範圍內的資料需要發送
     * sendAndRecv() 成功發送後會遞增此索引
     */
    size_t next_send_valid_index_ = 0;

    // === 接收緩衝區 ===
    /**
     * inbound_data_ - 接收緩衝區（64 MB）
     * 儲存接收到的資料
     */
    std::vector<char> inbound_data_;

    /**
     * next_rcv_valid_index_ - 接收緩衝區有效資料長度
     * 表示 [0, next_rcv_valid_index_) 範圍內的資料有效
     * recv_callback_ 處理完資料後應減少此索引
     */
    size_t next_rcv_valid_index_ = 0;

    // === Socket 屬性 ===
    /**
     * socket_attrib_ - Socket 地址結構
     * 儲存 IP 地址、埠號等資訊
     * 用於 bind() 或 connect() 呼叫
     */
    struct sockaddr_in socket_attrib_ {};

    // === 接收回調函式 ===
    /**
     * recv_callback_ - 資料接收回調函式
     *
     * @param s TCPSocket 指標（this）
     * @param rx_time 接收時間戳記（奈秒精度）
     *
     * 觸發時機：
     * - sendAndRecv() 偵測到新資料到達時自動呼叫
     *
     * 典型用途：
     * - 反序列化訊息
     * - 驗證訊息完整性（序列號、校驗和）
     * - 將訊息轉發到業務邏輯層
     *
     * 注意：
     * - 回調函式應盡快返回（避免阻塞主迴圈）
     * - 複雜處理應放到其他執行緒或佇列
     */
    std::function<void(TCPSocket* s, Nanos rx_time)> recv_callback_ = nullptr;

    // === 輔助成員 ===
    std::string time_str_;  ///< 時間字串緩衝區（避免重複格式化）
    Logger& logger_;        ///< 日誌記錄器引用
};
}
