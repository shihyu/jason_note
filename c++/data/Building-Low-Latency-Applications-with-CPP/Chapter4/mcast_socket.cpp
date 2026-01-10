#include "mcast_socket.h"

namespace Common
{
// ========================================
// McastSocket 實作: UDP 多播通訊
// ========================================

// init: 初始化多播 Socket
// @param ip: 多播群組位址 (如 "239.255.0.1")
// @param iface: 網卡名稱 (如 "eth0")
// @param port: 埠號
// @param is_listening: true=接收端(bind), false=發送端
// @return: socket 檔案描述符
//
// Socket 配置:
// - is_udp_ = true: 使用 UDP 協議
// - is_listening_: 決定是否綁定埠號
// - needs_so_timestamp_ = false: 不需要接收時間戳
//
// 兩步驟初始化:
// 1. init(): 建立 Socket 並綁定埠號(若為接收端)
// 2. join(): 加入多播群組(僅接收端需要)
//
// ⚠️ 發送端 vs 接收端:
// - 發送端: init(ip, iface, port, false) → 不需要 join()
// - 接收端: init(ip, iface, port, true) → 必須呼叫 join(ip)
auto McastSocket::init(const std::string& ip, const std::string& iface,
                       int port, bool is_listening) -> int
{
    // 建立 UDP Socket 配置
    // is_udp=true: UDP 協議
    // needs_so_timestamp=false: 多播不需要時間戳(已有序列號)
    const SocketCfg socket_cfg{ip, iface, port, true, is_listening, false};
    socket_fd_ = createSocket(logger_, socket_cfg);
    return socket_fd_;
}

// join: 加入多播群組(僅接收端需要)
// @param ip: 多播群組位址
// @return: true=成功, false=失敗
//
// IGMP 協議流程:
// 1. 應用程式呼叫 join(ip)
// 2. 核心發送 IGMP JOIN 訊息到網路
// 3. 路由器/交換機記錄訂閱者
// 4. 網卡開始接收該群組的封包
//
// ⚡ 硬體多播過濾:
// - MAC 位址: 多播 IP 映射到特定 MAC 位址
// - 網卡過濾: 只接收匹配的 MAC 位址封包
// - 減少 CPU 負載: 不相關的多播流量被硬體丟棄
bool McastSocket::join(const std::string& ip)
{
    // 呼叫 socket_utils.h 中的 join() 函式
    // 底層使用 setsockopt(IP_ADD_MEMBERSHIP)
    return Common::join(socket_fd_, ip);
}

// leave: 離開多播群組
// @param ip: 多播群組位址 (未使用)
// @param port: 埠號 (未使用)
//
// 簡化實作:
// - 直接關閉 Socket 而非呼叫 IP_DROP_MEMBERSHIP
// - close() 會自動清理所有資源(包括多播訂閱)
// - socket_fd_ = -1: 標記為無效,防止重複使用
//
// ⚠️ 注意: 參數未使用
// 原因: close() 不需要知道 IP 和 port
auto McastSocket::leave(const std::string&, int) -> void
{
    close(socket_fd_);  // 關閉 Socket,自動離開多播群組
    socket_fd_ = -1;    // 標記為無效
}

// sendAndRecv: 接收並發送資料(主事件循環)
// @return: true=有接收到資料, false=無資料
//
// ⚡ 批次處理模式(Batching Pattern):
// 1. 應用程式多次呼叫 send() 累積資料
// 2. 主循環呼叫 sendAndRecv() 一次性發送
// 3. 減少系統呼叫次數(每次 send() 約 1-2μs 開銷)
// 4. 提高網路利用率(減少小封包)
//
// UDP 封包特性:
// - 訊息邊界: 每次 send() 發送一個完整的 UDP 封包
// - 不會粘包: 與 TCP 不同,UDP 保持封包獨立性
// - 順序不保證: 網路可能亂序,需要序列號排序
// - 可能丟失: 無重傳機制,需要應用層處理
//
// ⚠️ 緩衝區溢出風險:
// - 若 send() 累積超過 64MB,ASSERT 會中止程式
// - 解決方案: 定期呼叫 sendAndRecv() 清空緩衝區
auto McastSocket::sendAndRecv() noexcept -> bool
{
    // ========== 階段 1: 接收資料 ==========
    // 非阻塞接收(MSG_DONTWAIT): 無資料時立即返回 EAGAIN
    // 追加模式: 寫入 next_rcv_valid_index_ 之後的空間
    // 支援部分讀取: UDP 封包可能分多次讀完
    const ssize_t n_rcv = recv(socket_fd_,
                               inbound_data_.data() + next_rcv_valid_index_,  // ⚡ 追加寫入位置
                               McastBufferSize - next_rcv_valid_index_,        // 剩餘空間
                               MSG_DONTWAIT);                                  // 非阻塞模式

    if (n_rcv > 0) {
        next_rcv_valid_index_ += n_rcv;  // 更新有效資料長度
        logger_.log("%:% %() % read socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_,
                    next_rcv_valid_index_);

        // ⚡ 回調處理: 解析協議並觸發業務邏輯
        // 注意: 回調應盡快處理,避免阻塞接收循環
        recv_callback_(this);
    }

    // ========== 階段 2: 發送資料 ==========
    // 批次發送: 將 send() 累積的資料一次性發送
    if (next_send_valid_index_ > 0) {
        // MSG_DONTWAIT: 非阻塞發送(若緩衝區滿立即返回)
        // MSG_NOSIGNAL: 避免 SIGPIPE 信號(對端關閉時不中止程式)
        //
        // ⚡ UDP 一次性發送保證:
        // - 不會部分發送(與 TCP 不同)
        // - 要嘛全部成功,要嘛失敗(返回 -1)
        // - 封包大小不能超過 MTU(通常 1500 bytes)
        ssize_t n = ::send(socket_fd_, outbound_data_.data(), next_send_valid_index_,
                           MSG_DONTWAIT | MSG_NOSIGNAL);

        logger_.log("%:% %() % send socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, n);
    }

    // ⚡ 重置發送緩衝區: 清空已發送的資料
    // 下次 send() 從頭開始累積
    next_send_valid_index_ = 0;

    return (n_rcv > 0);  // 返回是否有接收到資料
}

// send: 累積資料到發送緩衝區(不立即發送)
// @param data: 資料指標
// @param len: 資料長度
//
// ⚡ 延遲發送策略(Deferred Send):
// - 目的: 減少系統呼叫次數
// - 實作: 僅複製到緩衝區,不呼叫 ::send()
// - 實際發送: 由 sendAndRecv() 統一處理
//
// 效能優勢:
// - 單次 send() 開銷: ~1-2μs (用戶態 → 核心態切換)
// - 批次發送: 累積 10 筆訊息只需 1 次系統呼叫
// - 範例: 100 筆訊息從 200μs 降至 20μs (10x 加速)
//
// 使用情境範例:
// ```cpp
// // 行情發布系統
// for (const auto& update : market_updates) {
//     mcast_socket.send(&update, sizeof(update));  // 僅複製
// }
// mcast_socket.sendAndRecv();  // 批次發送 100 筆更新
// ```
//
// ⚠️ 緩衝區管理:
// - 容量限制: 64MB (McastBufferSize)
// - 溢出檢查: ASSERT 保證不超過容量
// - 最佳實踐: 每累積數百筆訊息就呼叫 sendAndRecv()
auto McastSocket::send(const void* data, size_t len) noexcept -> void
{
    // ⚡ 零拷貝追加: 直接寫入發送緩衝區的尾部
    // 避免動態分配和多餘的記憶體複製
    memcpy(outbound_data_.data() + next_send_valid_index_, data, len);
    next_send_valid_index_ += len;  // 更新有效資料長度

    // ⚠️ 緩衝區溢出保護: 開發階段捕捉邏輯錯誤
    // 若觸發 ASSERT,表示 sendAndRecv() 呼叫頻率不足
    ASSERT(next_send_valid_index_ < McastBufferSize,
           "Mcast socket buffer filled up and sendAndRecv() not called.");
}
}
