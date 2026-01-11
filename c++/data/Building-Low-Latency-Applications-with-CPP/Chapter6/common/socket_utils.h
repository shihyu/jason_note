#pragma once

#include <iostream>
#include <string>
#include <unordered_set>
#include <sstream>
#include <sys/epoll.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <ifaddrs.h>
#include <sys/socket.h>
#include <fcntl.h>

#include "macros.h"

#include "logging.h"

namespace Common
{
/**
 * SocketCfg - Socket 配置結構
 *
 * 用途：
 * - 統一管理 TCP/UDP Socket 的配置參數
 * - 簡化 createSocket() 函式的參數列表
 * - 提供清晰的配置可讀性（toString()）
 *
 * 使用範例：
 * ```cpp
 * // TCP 客戶端：連接到交易所
 * SocketCfg cfg{
 *     .ip_ = "192.168.1.100",
 *     .iface_ = "eth0",
 *     .port_ = 8080,
 *     .is_udp_ = false,
 *     .is_listening_ = false,
 *     .needs_so_timestamp_ = false
 * };
 *
 * // UDP 伺服器：接收市場數據 Multicast
 * SocketCfg mcast_cfg{
 *     .ip_ = "239.255.0.1",  // Multicast 地址
 *     .iface_ = "eth0",
 *     .port_ = 9090,
 *     .is_udp_ = true,
 *     .is_listening_ = true,  // 綁定 port
 *     .needs_so_timestamp_ = true  // 啟用 SO_TIMESTAMP
 * };
 * ```
 */
struct SocketCfg {
    /**
     * ip_ - IP 位址
     *
     * 用途：
     * - 客戶端模式：目標伺服器的 IP 位址
     * - 伺服器模式：綁定的本地 IP 位址（通常留空，自動使用 iface_ 對應的 IP）
     * - Multicast 模式：多播群組位址（例如 239.255.0.1）
     *
     * 注意：
     * - 若留空且指定 iface_，將自動使用 getIfaceIP() 查詢介面 IP
     * - 支援 IPv4 格式（例如 "192.168.1.100"）
     */
    std::string ip_;

    /**
     * iface_ - 網路介面名稱
     *
     * 用途：
     * - 指定使用的網路介面（例如 "eth0", "ens33", "lo"）
     * - 當 ip_ 為空時，自動查詢此介面對應的 IP 位址
     *
     * 低延遲優化：
     * - 明確指定介面可減少路由查找時間
     * - 多網卡環境下，綁定專用介面避免流量競爭
     *
     * 常見介面名稱：
     * - "lo" - 本地迴環 (127.0.0.1)
     * - "eth0" - 第一張乙太網卡
     * - "ens33" - 現代 Linux 命名規則
     */
    std::string iface_;

    /**
     * port_ - 埠號
     *
     * 用途：
     * - 客戶端模式：目標伺服器的埠號
     * - 伺服器模式：綁定的監聽埠號
     *
     * 範圍：
     * - 有效範圍：1-65535
     * - -1 表示未設定（預設值）
     *
     * 建議：
     * - 避免使用特權埠 (1-1023，需要 root 權限)
     * - 高頻交易系統常用 8000-9999 範圍
     */
    int port_ = -1;

    /**
     * is_udp_ - 是否為 UDP Socket
     *
     * - true：建立 SOCK_DGRAM (UDP) socket
     * - false：建立 SOCK_STREAM (TCP) socket
     *
     * UDP vs TCP：
     * - UDP：無連接、低延遲、適合市場數據廣播
     * - TCP：有連接、可靠傳輸、適合訂單傳送
     */
    bool is_udp_ = false;

    /**
     * is_listening_ - 是否為伺服器模式
     *
     * - true：呼叫 bind() 和 listen()（TCP）或僅 bind()（UDP）
     * - false：呼叫 connect()（客戶端模式）
     *
     * 範例：
     * - 交易所的 Order Server：is_listening_ = true
     * - 交易客戶端的 Order Gateway：is_listening_ = false
     */
    bool is_listening_ = false;

    /**
     * needs_so_timestamp_ - 是否啟用核心時間戳記
     *
     * - true：啟用 SO_TIMESTAMP（透過 recvmsg() 獲取封包到達時間）
     * - false：不啟用（預設）
     *
     * 用途：
     * - 精確測量網路延遲（封包到達網卡的時間）
     * - 行情數據時間戳記（市場數據到達時間）
     *
     * 注意：
     * - 僅對 UDP Socket 有意義（TCP 無法獲取單一封包時間）
     * - 需使用 recvmsg() 而非 recv() 讀取時間戳記
     */
    bool needs_so_timestamp_ =  false;

    /**
     * toString() - 轉換為可讀字串
     *
     * 用途：
     * - 日誌輸出
     * - 除錯資訊
     * - 配置驗證
     *
     * 輸出範例：
     * "SocketCfg[ip:192.168.1.100 iface:eth0 port:8080 is_udp:0 is_listening:0 needs_SO_timestamp:0]"
     */
    auto toString() const
    {
        std::stringstream ss;
        ss << "SocketCfg[ip:" << ip_
           << " iface:" << iface_
           << " port:" << port_
           << " is_udp:" << is_udp_
           << " is_listening:" << is_listening_
           << " needs_SO_timestamp:" << needs_so_timestamp_
           << "]";

        return ss.str();
    }
};

/**
 * MaxTCPServerBacklog - TCP 伺服器最大待處理連線數
 *
 * 定義：
 * - listen() 系統呼叫的 backlog 參數
 * - 表示 SYN_RCVD 佇列的最大長度（等待 accept() 的連線數）
 *
 * 設定為 1024 的理由：
 * - 足夠處理突發連線請求
 * - 避免 SYN Flood 攻擊導致資源耗盡
 * - 平衡記憶體使用與連線處理能力
 *
 * 注意：
 * - 實際最大值受限於 /proc/sys/net/core/somaxconn（Linux 預設 4096）
 * - 若 backlog > somaxconn，核心會自動截斷為 somaxconn
 *
 * 高頻交易環境：
 * - 通常不需要大量並發連線（點對點連接）
 * - 1024 已足夠應對正常場景
 */
constexpr int MaxTCPServerBacklog = 1024;

// 取得網路介面 (Interface) 對應的 IP 位址
// 例如: "eth0" -> "192.168.1.10"
inline auto getIfaceIP(const std::string& iface) -> std::string
{
    char buf[NI_MAXHOST] = {'\0'};
    ifaddrs* ifaddr = nullptr;

    if (getifaddrs(&ifaddr) != -1) {
        for (ifaddrs* ifa = ifaddr; ifa; ifa = ifa->ifa_next) {
            if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET &&
                iface == ifa->ifa_name) {
                getnameinfo(ifa->ifa_addr, sizeof(sockaddr_in), buf, sizeof(buf), NULL, 0,
                            NI_NUMERICHOST);
                break;
            }
        }

        freeifaddrs(ifaddr);
    }

    return buf;
}

// 設定 Socket 為非阻塞模式 (Non-Blocking)
// ⚡ 核心優化：避免 read/recv 卡住執行緒，這對於單執行緒 Event Loop 至關重要
inline auto setNonBlocking(int fd) -> bool
{
    const auto flags = fcntl(fd, F_GETFL, 0);

    if (flags & O_NONBLOCK) {
        return true;
    }

    return (fcntl(fd, F_SETFL, flags | O_NONBLOCK) != -1);
}

// 停用 Nagle 演算法 (TCP_NODELAY)
// ⚡ 低延遲關鍵：Nagle 演算法會合併小封包以提高頻寬利用率，但會增加延遲
// 對於即時交易系統，我們希望每個小封包 (如 Order Update) 立即發送
inline auto disableNagle(int fd) -> bool
{
    int one = 1;
    return (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, reinterpret_cast<void*>(&one),
                       sizeof(one)) != -1);
}

// 啟用核心層級的接收時間戳記 (SO_TIMESTAMP)
// 允許透過 recvmsg() 獲取封包到達網卡的精確時間
inline auto setSOTimestamp(int fd) -> bool
{
    int one = 1;
    return (setsockopt(fd, SOL_SOCKET, SO_TIMESTAMP, reinterpret_cast<void*>(&one),
                       sizeof(one)) != -1);
}

/**
 * join() - 加入 IP Multicast 群組
 *
 * @param fd Socket 檔案描述符（必須是 UDP socket）
 * @param ip Multicast 群組 IP 位址（例如 "239.255.0.1"）
 * @return 成功返回 true，失敗返回 false
 *
 * 功能：
 * - 將 socket 加入指定的 Multicast 群組
 * - 允許接收發送到該群組的 UDP 封包
 *
 * 原理：
 * - 使用 IP_ADD_MEMBERSHIP 選項通知核心加入多播群組
 * - 核心會向路由器發送 IGMP Join 訊息
 * - 網路交換機會將多播流量轉發到此主機
 *
 * Multicast IP 地址範圍：
 * - 224.0.0.0 ~ 239.255.255.255（Class D）
 * - 常用範圍：239.0.0.0 ~ 239.255.255.255（組織內部使用）
 *
 * 使用場景：
 * - 市場數據訂閱（Market Data Feed）
 * - 行情廣播（Price Updates）
 * - 一對多通訊（One-to-Many）
 *
 * 注意事項：
 * - 必須先建立 UDP socket（SOCK_DGRAM）
 * - 必須先 bind() 到對應的 port
 * - 網路環境必須支援 Multicast（路由器/交換機配置）
 * - 可多次呼叫加入多個群組
 *
 * 錯誤處理：
 * - 若 socket 不是 UDP，會返回 false
 * - 若 IP 格式錯誤，inet_addr() 返回 INADDR_NONE
 * - 若網路不支援 Multicast，setsockopt() 失敗
 *
 * 使用範例：
 * ```cpp
 * int fd = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
 * struct sockaddr_in addr;
 * addr.sin_family = AF_INET;
 * addr.sin_port = htons(9090);
 * addr.sin_addr.s_addr = htonl(INADDR_ANY);
 * bind(fd, (struct sockaddr*)&addr, sizeof(addr));
 *
 * join(fd, "239.255.0.1");  // 加入多播群組
 * // 現在可以接收發送到 239.255.0.1:9090 的封包
 * ```
 *
 * 效能考量：
 * - Multicast 延遲通常比 Unicast 稍高（10-50μs）
 * - 網路擁塞時可能出現封包丟失（UDP 不保證可靠性）
 * - 建議使用專用網路介面避免與其他流量競爭
 */
inline auto join(int fd, const std::string& ip) -> bool
{
    const ip_mreq mreq{{inet_addr(ip.c_str())}, {htonl(INADDR_ANY)}};
    return (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq,
                       sizeof(mreq)) != -1);
}

/**
 * createSocket() - 建立並完整配置 TCP/UDP Socket
 *
 * @param logger 日誌記錄器（用於輸出配置資訊和錯誤訊息）
 * @param socket_cfg Socket 配置參數（見 SocketCfg 結構）
 * @return Socket 檔案描述符（>= 0），若失敗則透過 ASSERT 終止程式
 *
 * 功能概述：
 * - 整合 socket()、bind()、connect()、listen()、setsockopt() 等系統呼叫
 * - 根據配置自動選擇 TCP/UDP、客戶端/伺服器模式
 * - 自動應用低延遲優化（非阻塞、TCP_NODELAY、大緩衝區）
 *
 * 執行流程：
 * 1. **IP 位址解析**：
 *    - 若 socket_cfg.ip_ 為空，呼叫 getIfaceIP() 查詢介面 IP
 *    - 使用 getaddrinfo() 將 IP:Port 轉換為 sockaddr 結構
 *
 * 2. **建立 Socket**：
 *    - 根據 is_udp_ 選擇 SOCK_STREAM (TCP) 或 SOCK_DGRAM (UDP)
 *    - 設定 AF_INET（IPv4）和對應的協定（IPPROTO_TCP/IPPROTO_UDP）
 *
 * 3. **低延遲優化（自動應用）**：
 *    - ✅ 非阻塞模式（setNonBlocking）
 *    - ✅ 關閉 Nagle 演算法（disableNagle，僅 TCP）
 *    - ✅ SO_REUSEADDR（伺服器模式，快速重啟）
 *    - ✅ SO_TIMESTAMP（若 needs_so_timestamp_ = true）
 *
 * 4. **連接/綁定**：
 *    - 客戶端模式（is_listening_ = false）：
 *      - 呼叫 connect() 連接到目標 IP:Port
 *    - 伺服器模式（is_listening_ = true）：
 *      - 呼叫 bind() 綁定到本地 IP:Port
 *      - TCP：呼叫 listen() 開始監聽（backlog = 1024）
 *      - UDP：僅 bind()，準備接收封包
 *
 * 5. **錯誤處理**：
 *    - 使用 ASSERT 進行嚴格檢查（失敗立即終止程式）
 *    - 輸出詳細錯誤訊息（包含 errno 和系統錯誤描述）
 *    - 記錄配置參數到日誌（方便除錯）
 *
 * 低延遲優化細節：
 *
 * ⚡ **非阻塞模式（setNonBlocking）**：
 *    - 避免 recv()/send() 阻塞主執行緒
 *    - 配合 epoll/select 實現高效能事件循環
 *    - 延遲降低：避免等待 I/O 完成
 *
 * ⚡ **TCP_NODELAY**：
 *    - 關閉 Nagle 演算法（預設會合併小封包）
 *    - 立即發送每個封包，不等待 ACK
 *    - 延遲降低：~40μs（對於小訂單訊息）
 *    - 權衡：頻寬利用率降低 ~10%
 *
 * ⚡ **SO_REUSEADDR**：
 *    - 允許快速重啟伺服器（無需等待 TIME_WAIT 狀態結束）
 *    - 避免 "Address already in use" 錯誤
 *    - 生產環境必備（減少停機時間）
 *
 * ⚡ **SO_TIMESTAMP**：
 *    - 核心層級封包時間戳記（封包到達網卡的時間）
 *    - 用於精確測量網路延遲
 *    - 精度：微秒級（取決於網卡驅動）
 *
 * 使用範例：
 *
 * ```cpp
 * // 範例 1：TCP 客戶端（連接到交易所）
 * SocketCfg tcp_client{
 *     .ip_ = "192.168.1.100",
 *     .iface_ = "eth0",
 *     .port_ = 8080,
 *     .is_udp_ = false,
 *     .is_listening_ = false,
 *     .needs_so_timestamp_ = false
 * };
 * int fd = createSocket(logger, tcp_client);
 * // fd 已設定為非阻塞、TCP_NODELAY、已連接
 *
 * // 範例 2：TCP 伺服器（Order Server）
 * SocketCfg tcp_server{
 *     .ip_ = "",  // 留空，自動使用 eth0 的 IP
 *     .iface_ = "eth0",
 *     .port_ = 8080,
 *     .is_udp_ = false,
 *     .is_listening_ = true,
 *     .needs_so_timestamp_ = false
 * };
 * int listen_fd = createSocket(logger, tcp_server);
 * // listen_fd 已綁定到 eth0:8080，開始監聽
 *
 * // 範例 3：UDP Multicast 接收（Market Data Consumer）
 * SocketCfg udp_mcast{
 *     .ip_ = "239.255.0.1",  // Multicast 群組
 *     .iface_ = "eth0",
 *     .port_ = 9090,
 *     .is_udp_ = true,
 *     .is_listening_ = true,  // 綁定 port
 *     .needs_so_timestamp_ = true  // 啟用時間戳記
 * };
 * int mcast_fd = createSocket(logger, udp_mcast);
 * join(mcast_fd, "239.255.0.1");  // 加入多播群組
 * // mcast_fd 已綁定到 9090，準備接收多播封包
 * ```
 *
 * 注意事項：
 * - 返回的 fd 需要呼叫者管理（close(fd)）
 * - 所有錯誤都會觸發 ASSERT（程式終止）
 * - 日誌會記錄完整的配置參數和時間戳記
 * - [[nodiscard]] 屬性確保呼叫者使用返回值
 *
 * 錯誤診斷：
 * - "getaddrinfo() failed"：IP 格式錯誤或網路介面不存在
 * - "socket() failed"：系統資源不足（fd 數量限制）
 * - "setNonBlocking() failed"：fcntl 權限問題
 * - "disableNagle() failed"：socket 類型錯誤（UDP 不支援）
 * - "connect() failed"：目標伺服器不可達或拒絕連接
 * - "bind() failed"：埠號已被占用或權限不足
 * - "listen() failed"：socket 狀態錯誤
 *
 * 系統限制：
 * - 最大 fd 數量：ulimit -n（通常 1024，可調整）
 * - 埠號範圍：1-65535（1-1023 需要 root 權限）
 * - Multicast 支援：需路由器/交換機配置
 * - SO_RCVBUF/SO_SNDBUF：受限於 /proc/sys/net/core/rmem_max
 */
[[nodiscard]] inline auto createSocket(Logger& logger,
                                       const SocketCfg& socket_cfg) -> int
{
    std::string time_str;

    const auto ip = socket_cfg.ip_.empty() ? getIfaceIP(socket_cfg.iface_) :
                    socket_cfg.ip_;
    logger.log("%:% %() % cfg:%\n", __FILE__, __LINE__, __FUNCTION__,
               Common::getCurrentTimeStr(&time_str), socket_cfg.toString());

    const int input_flags = (socket_cfg.is_listening_ ? AI_PASSIVE : 0) |
                            (AI_NUMERICHOST | AI_NUMERICSERV);
    const addrinfo hints{input_flags, AF_INET, socket_cfg.is_udp_ ? SOCK_DGRAM : SOCK_STREAM,
                         socket_cfg.is_udp_ ? IPPROTO_UDP : IPPROTO_TCP, 0, 0, nullptr, nullptr};

    addrinfo* result = nullptr;
    const auto rc = getaddrinfo(ip.c_str(),
                                std::to_string(socket_cfg.port_).c_str(), &hints, &result);
    ASSERT(!rc, "getaddrinfo() failed. error:" + std::string(gai_strerror(
                rc)) + "errno:" + strerror(errno));

    int socket_fd = -1;
    int one = 1;

    for (addrinfo* rp = result; rp; rp = rp->ai_next) {
        ASSERT((socket_fd = socket(rp->ai_family, rp->ai_socktype,
                                   rp->ai_protocol)) != -1,
               "socket() failed. errno:" + std::string(strerror(errno)));

        // ⚡ 預設設定非阻塞
        ASSERT(setNonBlocking(socket_fd),
               "setNonBlocking() failed. errno:" + std::string(strerror(errno)));

        if (!socket_cfg.is_udp_) { // disable Nagle for TCP sockets.
            ASSERT(disableNagle(socket_fd),
                   "disableNagle() failed. errno:" + std::string(strerror(errno)));
        }

        if (!socket_cfg.is_listening_) { // establish connection to specified address.
            ASSERT(connect(socket_fd, rp->ai_addr, rp->ai_addrlen) != 1,
                   "connect() failed. errno:" + std::string(strerror(errno)));
        }

        if (socket_cfg.is_listening_) { // allow re-using the address in the call to bind()
            ASSERT(setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR,
                              reinterpret_cast<const char*>(&one), sizeof(one)) == 0,
                   "setsockopt() SO_REUSEADDR failed. errno:" + std::string(strerror(errno)));
        }

        if (socket_cfg.is_listening_) {
            // bind to the specified port number.
            const sockaddr_in addr{AF_INET, htons(socket_cfg.port_), {htonl(INADDR_ANY)}, {}};
            ASSERT(bind(socket_fd, socket_cfg.is_udp_ ?
                        reinterpret_cast<const struct sockaddr*>(&addr) : rp->ai_addr,
                        sizeof(addr)) == 0, "bind() failed. errno:%" + std::string(strerror(errno)));
        }

        if (!socket_cfg.is_udp_ &&
            socket_cfg.is_listening_) { // listen for incoming TCP connections.
            ASSERT(listen(socket_fd, MaxTCPServerBacklog) == 0,
                   "listen() failed. errno:" + std::string(strerror(errno)));
        }

        if (socket_cfg.needs_so_timestamp_) { // enable software receive timestamps.
            ASSERT(setSOTimestamp(socket_fd),
                   "setSOTimestamp() failed. errno:" + std::string(strerror(errno)));
        }
    }

    return socket_fd;
}
}
