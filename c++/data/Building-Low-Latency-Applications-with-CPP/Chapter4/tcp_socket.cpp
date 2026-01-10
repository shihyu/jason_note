#include "tcp_socket.h"

namespace Common
{
// ========================================
// TCPSocket 實作: 低延遲 TCP 通訊
// ========================================

// connect: 建立 TCP Socket 連線
// @param ip: IP 位址 (如 "192.168.1.100")
// @param iface: 網卡名稱 (如 "eth0"),與 ip 二擇一
// @param port: 埠號
// @param is_listening: true=Server模式(bind+listen), false=Client模式(connect)
// @return: socket 檔案描述符
//
// 配置特點:
// - is_udp_ = false: 使用 TCP 協議
// - needs_so_timestamp_ = true: 啟用接收時間戳
//   ⚠️ FIFOSequencer 依賴此時間戳進行訊息排序
//
// socket_attrib_ 用途:
// - 儲存對端位址資訊(recvmsg 會填充)
// - sin_addr.s_addr = INADDR_ANY: 接受來自任意 IP 的連線
// - sin_port = htons(port): 網路位元組序的埠號
// - sin_family = AF_INET: IPv4 協議
auto TCPSocket::connect(const std::string& ip, const std::string& iface,
                        int port, bool is_listening) -> int
{
    // 建立 Socket 配置: TCP + SO_TIMESTAMP
    const SocketCfg socket_cfg{ip, iface, port, false, is_listening, true};
    socket_fd_ = createSocket(logger_, socket_cfg);

    // 初始化 socket 屬性結構(用於 recvmsg/sendmsg)
    socket_attrib_.sin_addr.s_addr = INADDR_ANY;  // 接受任意來源 IP
    socket_attrib_.sin_port = htons(port);        // 埠號(網路位元組序)
    socket_attrib_.sin_family = AF_INET;          // IPv4

    return socket_fd_;
}

// sendAndRecv: 非阻塞式收發資料的核心函式
// @return: true=收到資料, false=無資料接收
//
// 功能:
// 1. 接收資料: 使用 recvmsg 從 socket 讀取資料到 inbound_data_
// 2. 取得時間戳: 從 ancillary data 提取核心接收時間戳
// 3. 觸發回呼: 呼叫 recv_callback_ 通知上層處理資料
// 4. 傳送資料: 將 outbound_data_ 緩衝區的資料傳送出去
//
// ⚡ 效能關鍵:
// - MSG_DONTWAIT: 非阻塞 I/O,無資料時立即返回
// - recvmsg: 相比 recv 可取得輔助資訊(時間戳)
// - 延遲測量: user_time - kernel_time = 核心態到用戶態的延遲
//
// 時間戳用途:
// - kernel_time: 封包到達網卡的時間(核心記錄)
// - user_time: 應用程式讀取資料的時間
// - diff: 核心處理延遲 + 排程延遲
auto TCPSocket::sendAndRecv() noexcept -> bool
{
    // 準備接收輔助資料(ancillary data)的緩衝區
    // CMSG_SPACE: 計算控制訊息所需的對齊後空間
    char ctrl[CMSG_SPACE(sizeof(struct timeval))];
    auto cmsg = reinterpret_cast<struct cmsghdr*>(&ctrl);

    // 準備 iovec: 指向接收緩衝區的剩餘空間
    iovec iov{inbound_data_.data() + next_rcv_valid_index_, TCPBufferSize - next_rcv_valid_index_};

    // 準備 msghdr: recvmsg 的參數結構
    // - msg_name: 對端位址(會被填充)
    // - msg_iov: 資料緩衝區
    // - msg_control: 輔助資料(時間戳)緩衝區
    msghdr msg{&socket_attrib_, sizeof(socket_attrib_), &iov, 1, ctrl, sizeof(ctrl), 0};

    // ⚡ 非阻塞接收: MSG_DONTWAIT 確保立即返回
    // 返回值:
    // - > 0: 接收到的位元組數
    // - 0: 連線已關閉
    // - -1: 錯誤(errno=EAGAIN 表示無資料)
    const auto read_size = recvmsg(socket_fd_, &msg, MSG_DONTWAIT);

    if (read_size > 0) {
        next_rcv_valid_index_ += read_size;  // 更新緩衝區索引

        // 提取核心時間戳
        Nanos kernel_time = 0;
        timeval time_kernel;

        // 驗證輔助資料中是否包含 SO_TIMESTAMP
        if (cmsg->cmsg_level == SOL_SOCKET &&
            cmsg->cmsg_type == SCM_TIMESTAMP &&
            cmsg->cmsg_len == CMSG_LEN(sizeof(time_kernel))) {
            // 從 ancillary data 複製時間戳
            memcpy(&time_kernel, CMSG_DATA(cmsg), sizeof(time_kernel));

            // 轉換為奈秒: tv_sec(秒) + tv_usec(微秒)
            kernel_time = time_kernel.tv_sec * NANOS_TO_SECS + time_kernel.tv_usec *
                          NANOS_TO_MICROS;
        }

        // 取得用戶態時間戳
        const auto user_time = getCurrentNanos();

        // 記錄延遲資訊
        // diff = user_time - kernel_time: 從核心接收到應用處理的總延遲
        // 包含: 核心處理時間 + 系統呼叫開銷 + 執行緒排程延遲
        logger_.log("%:% %() % read socket:% len:% utime:% ktime:% diff:%\n", __FILE__,
                    __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, next_rcv_valid_index_,
                    user_time, kernel_time, (user_time - kernel_time));

        // 觸發接收回呼,通知上層處理新資料
        recv_callback_(this, kernel_time);
    }

    // 傳送緩衝區資料
    if (next_send_valid_index_ > 0) {
        // ⚡ 非阻塞傳送: MSG_DONTWAIT 立即返回
        // MSG_NOSIGNAL: 對端關閉時不產生 SIGPIPE 信號
        //
        // 返回值:
        // - > 0: 實際傳送的位元組數(可能少於請求的數量)
        // - -1: 錯誤(errno=EAGAIN 表示傳送緩衝區已滿)
        //
        // ⚠️ 部分傳送問題:
        // - TCP 可能只傳送部分資料(傳送緩衝區不足)
        // - 本實作假設資料量小,一次傳送完成
        // - 若需處理部分傳送,需要追蹤 next_send_valid_index_
        const auto n = ::send(socket_fd_, outbound_data_.data(), next_send_valid_index_,
                              MSG_DONTWAIT | MSG_NOSIGNAL);
        logger_.log("%:% %() % send socket:% len:%\n", __FILE__, __LINE__, __FUNCTION__,
                    Common::getCurrentTimeStr(&time_str_), socket_fd_, n);
    }

    // 重置傳送緩衝區索引(假設資料已完全傳送)
    // ⚠️ 若 send() 部分失敗,未傳送的資料會遺失
    next_send_valid_index_ = 0;

    return (read_size > 0);  // 返回是否有接收到資料
}

// send: 將資料寫入傳送緩衝區
// @param data: 要傳送的資料指標
// @param len: 資料長度(位元組)
//
// 緩衝機制:
// 1. 資料先複製到 outbound_data_ 緩衝區
// 2. next_send_valid_index_ 追蹤緩衝區已使用空間
// 3. 下次呼叫 sendAndRecv() 時才實際傳送
//
// ⚡ 效能優勢:
// - 批次傳送: 累積多筆資料後一次 send(),減少系統呼叫
// - 零拷貝: 使用 memcpy 將資料集中,配合 MSG_DONTWAIT 避免阻塞
//
// ⚠️ 緩衝區溢位風險:
// - TCPBufferSize 是固定大小(通常 64KB)
// - 呼叫前應確保 next_send_valid_index_ + len <= TCPBufferSize
// - 本實作未檢查溢位(假設上層控制資料量)
auto TCPSocket::send(const void* data, size_t len) noexcept -> void
{
    // 將資料複製到傳送緩衝區
    memcpy(outbound_data_.data() + next_send_valid_index_, data, len);
    next_send_valid_index_ += len;  // 更新緩衝區索引
}
}
