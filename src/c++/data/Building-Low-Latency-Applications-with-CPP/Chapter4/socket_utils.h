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
// ========================================
// Socket 工具函式庫 (Socket Utilities)
// ========================================
//
// 設計目標:
// 1. 低延遲 Socket 設定: 禁用 Nagle、啟用非阻塞模式
// 2. 統一介面: 支援 TCP/UDP、Client/Server 模式
// 3. 硬體時間戳: 支援 SO_TIMESTAMP 取得封包接收時間
//
// 使用場景:
// - 交易所閘道: 建立與交易所的 TCP 連線
// - 市場數據接收: 訂閱 UDP 多播群組
// - 內部通訊: TCP Server 監聽訂單和執行報告

// SocketCfg: Socket 配置結構
//
// 靈活性設計:
// - ip_ 和 iface_ 二選一: 可指定 IP 或網卡名稱
// - is_udp_: 選擇 TCP 或 UDP
// - is_listening_: 區分 Client (connect) 或 Server (bind+listen)
// - needs_so_timestamp_: 啟用硬體/軟體時間戳
struct SocketCfg {
    std::string ip_;         // IP 位址 (如 "192.168.1.100"),優先於 iface_
    std::string iface_;      // 網卡名稱 (如 "eth0"),用於查詢 IP
    int port_ = -1;          // 埠號 (1-65535)
    bool is_udp_ = false;    // true: UDP, false: TCP
    bool is_listening_ = false;  // true: Server (bind), false: Client (connect)
    bool needs_so_timestamp_ = false;  // true: 啟用 SO_TIMESTAMP

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

// TCP Server 最大待連線佇列長度
// ⚡ 效能影響:
// - 太小 (如 5): 高負載時連線請求被拒絕
// - 太大 (如 65535): 浪費核心記憶體
// - 1024: 適合大多數低延遲交易系統
constexpr int MaxTCPServerBacklog = 1024;

// getIfaceIP: 將網卡名稱轉換為 IP 位址
// @param iface: 網卡名稱 (如 "eth0", "lo", "ens33")
// @return: IPv4 位址字串 (如 "192.168.1.100"),找不到則返回空字串
//
// 實作原理:
// 1. getifaddrs(): 取得系統所有網卡資訊
// 2. 遍歷網卡列表,匹配名稱和 IPv4 協議
// 3. getnameinfo(): 將 sockaddr 轉換為 IP 字串
//
// 使用場景:
// - 自動偵測網卡 IP: createSocket({.iface_="eth0", .port_=8080})
// - 多網卡系統: 明確指定使用哪張網卡
//
// ⚠️ 錯誤處理: 若網卡不存在或無 IPv4 位址,返回空字串
inline auto getIfaceIP(const std::string& iface) -> std::string
{
    char buf[NI_MAXHOST] = {'\0'};
    ifaddrs* ifaddr = nullptr;

    if (getifaddrs(&ifaddr) != -1) {  // 取得系統所有網卡資訊
        for (ifaddrs* ifa = ifaddr; ifa; ifa = ifa->ifa_next) {
            // 匹配條件: 網卡名稱相同 && IPv4 協議
            if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET &&
                iface == ifa->ifa_name) {
                // 將 sockaddr_in 轉換為 IP 字串
                getnameinfo(ifa->ifa_addr, sizeof(sockaddr_in), buf, sizeof(buf), NULL, 0,
                            NI_NUMERICHOST);
                break;
            }
        }

        freeifaddrs(ifaddr);  // 釋放網卡資訊結構
    }

    return buf;
}

// setNonBlocking: 將 socket 設定為非阻塞模式
// @param fd: socket 檔案描述符
// @return: 成功返回 true,失敗返回 false
//
// 非阻塞模式行為:
// - read/recv: 無資料時立即返回 EAGAIN 而非阻塞
// - write/send: 傳送緩衝區滿時立即返回 EAGAIN
// - accept: 無新連線時立即返回 EAGAIN
//
// ⚡ 低延遲必備:
// - 避免執行緒阻塞在 I/O 操作
// - 配合 epoll 實現事件驅動架構
// - 確保延遲的可預測性 (無阻塞等待)
inline auto setNonBlocking(int fd) -> bool
{
    const auto flags = fcntl(fd, F_GETFL, 0);  // 取得當前檔案狀態旗標

    if (flags & O_NONBLOCK) {  // 已經是非阻塞模式
        return true;
    }

    return (fcntl(fd, F_SETFL, flags | O_NONBLOCK) != -1);  // 設定 O_NONBLOCK 旗標
}

// disableNagle: 禁用 Nagle 演算法
// @param fd: TCP socket 檔案描述符
// @return: 成功返回 true,失敗返回 false
//
// Nagle 演算法問題:
// - 原理: 累積小封包直到收到 ACK 或達到 MSS,才傳送
// - 延遲影響: 增加 40-200ms 的延遲 (取決於 RTT)
// - 適用場景: 批次資料傳輸,降低網路負載
//
// ⚡ 低延遲交易系統必須禁用:
// - 訂單訊息需要立即傳送 (不能等待累積)
// - 延遲敏感度 > 頻寬利用率
// - TCP_NODELAY 確保資料立即傳送
inline auto disableNagle(int fd) -> bool
{
    int one = 1;
    return (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, reinterpret_cast<void*>(&one),
                       sizeof(one)) != -1);
}

// setSOTimestamp: 啟用軟體接收時間戳
// @param fd: socket 檔案描述符
// @return: 成功返回 true,失敗返回 false
//
// 時間戳來源:
// - SO_TIMESTAMP: 核心接收封包時的系統時間
// - 精度: 微秒級 (取決於核心設定)
// - 取得方式: 透過 recvmsg() 的輔助資料 (ancillary data)
//
// 使用場景:
// - 測量網路延遲: 比對傳送時間與接收時間
// - 時間序列分析: 精確記錄市場數據到達時間
//
// ⚠️ 硬體時間戳 vs 軟體時間戳:
// - 硬體時間戳 (SO_TIMESTAMPING): 奈秒精度,需網卡支援
// - 軟體時間戳 (SO_TIMESTAMP): 微秒精度,所有網卡支援
inline auto setSOTimestamp(int fd) -> bool
{
    int one = 1;
    return (setsockopt(fd, SOL_SOCKET, SO_TIMESTAMP, reinterpret_cast<void*>(&one),
                       sizeof(one)) != -1);
}

// join: 加入 UDP 多播群組
// @param fd: UDP socket 檔案描述符
// @param ip: 多播群組位址 (如 "239.255.0.1")
// @return: 成功返回 true,失敗返回 false
//
// 多播原理:
// - 一對多傳輸: 一個傳送者,多個接收者
// - 群組位址範圍: 224.0.0.0 ~ 239.255.255.255 (IPv4)
// - 網路層過濾: 網卡硬體過濾非訂閱的多播封包
//
// 使用場景:
// - 市場數據: 交易所透過多播發送行情資訊
// - 內部廣播: 將訂單更新廣播給多個策略引擎
//
// ⚡ 效能優勢:
// - 減少網路頻寬: 一份資料,多個接收者
// - 降低延遲: 避免多次單播的序列化開銷
inline auto join(int fd, const std::string& ip) -> bool
{
    const ip_mreq mreq{{inet_addr(ip.c_str())}, {htonl(INADDR_ANY)}};
    return (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq,
                       sizeof(mreq)) != -1);
}

// createSocket: 建立並配置 TCP/UDP socket
// @param logger: 日誌記錄器
// @param socket_cfg: socket 配置參數
// @return: socket 檔案描述符,失敗時透過 ASSERT 終止程式
//
// 支援模式:
// 1. TCP Client: connect 到遠端伺服器
// 2. TCP Server: bind + listen,等待連線
// 3. UDP Client: 可傳送資料到任意目的地
// 4. UDP Server: bind 到本地埠,接收資料
//
// 低延遲優化:
// - 非阻塞模式: 避免執行緒阻塞
// - 禁用 Nagle: TCP 立即傳送 (TCP_NODELAY)
// - SO_REUSEADDR: Server 重啟時立即綁定埠
// - SO_TIMESTAMP: 記錄封包接收時間
//
// ⚠️ 錯誤處理策略:
// - 所有錯誤都透過 ASSERT 終止程式 (快速失敗)
// - 適合交易系統:網路配置錯誤應立即暴露,而非靜默失敗
[[nodiscard]] inline auto createSocket(Logger& logger,
                                       const SocketCfg& socket_cfg) -> int
{
    std::string time_str;

    // 優先使用 ip_,若為空則從 iface_ 查詢
    const auto ip = socket_cfg.ip_.empty() ? getIfaceIP(socket_cfg.iface_) :
                    socket_cfg.ip_;
    logger.log("%:% %() % cfg:%\n", __FILE__, __LINE__, __FUNCTION__,
               Common::getCurrentTimeStr(&time_str), socket_cfg.toString());

    // 準備 getaddrinfo() 的提示結構
    // AI_PASSIVE: Server 模式 (bind 到 INADDR_ANY)
    // AI_NUMERICHOST: ip 是數字格式,不需 DNS 查詢
    // AI_NUMERICSERV: port 是數字格式
    const int input_flags = (socket_cfg.is_listening_ ? AI_PASSIVE : 0) |
                            (AI_NUMERICHOST | AI_NUMERICSERV);
    const addrinfo hints{input_flags, AF_INET, socket_cfg.is_udp_ ? SOCK_DGRAM : SOCK_STREAM,
                         socket_cfg.is_udp_ ? IPPROTO_UDP : IPPROTO_TCP, 0, 0, nullptr, nullptr};

    // 解析 IP:Port 為 sockaddr 結構
    addrinfo* result = nullptr;
    const auto rc = getaddrinfo(ip.c_str(),
                                std::to_string(socket_cfg.port_).c_str(), &hints, &result);
    ASSERT(!rc, "getaddrinfo() failed. error:" + std::string(gai_strerror(
                rc)) + "errno:" + strerror(errno));

    int socket_fd = -1;
    int one = 1;

    // 遍歷 getaddrinfo 返回的位址列表 (通常只有一個)
    for (addrinfo* rp = result; rp; rp = rp->ai_next) {
        // 1. 建立 socket
        ASSERT((socket_fd = socket(rp->ai_family, rp->ai_socktype,
                                   rp->ai_protocol)) != -1,
               "socket() failed. errno:" + std::string(strerror(errno)));

        // 2. 設定非阻塞模式 (低延遲必備)
        ASSERT(setNonBlocking(socket_fd),
               "setNonBlocking() failed. errno:" + std::string(strerror(errno)));

        // 3. TCP 專屬: 禁用 Nagle 演算法
        if (!socket_cfg.is_udp_) {
            ASSERT(disableNagle(socket_fd),
                   "disableNagle() failed. errno:" + std::string(strerror(errno)));
        }

        // 4. Client 模式: 連線到遠端伺服器
        // ⚠️ 非阻塞 connect: 立即返回 EINPROGRESS,需透過 epoll 監控連線完成
        if (!socket_cfg.is_listening_) {
            ASSERT(connect(socket_fd, rp->ai_addr, rp->ai_addrlen) != 1,
                   "connect() failed. errno:" + std::string(strerror(errno)));
        }

        // 5. Server 模式: 允許位址重用 (避免 TIME_WAIT 狀態阻擋重啟)
        if (socket_cfg.is_listening_) {
            ASSERT(setsockopt(socket_fd, SOL_SOCKET, SO_REUSEADDR,
                              reinterpret_cast<const char*>(&one), sizeof(one)) == 0,
                   "setsockopt() SO_REUSEADDR failed. errno:" + std::string(strerror(errno)));
        }

        // 6. Server 模式: 綁定到指定埠
        // ⚠️ UDP vs TCP 的 bind 行為差異:
        //     - UDP: bind 指定接收埠,可立即接收資料
        //     - TCP: bind 只是預留埠,需配合 listen() 才能接受連線
        if (socket_cfg.is_listening_) {
            const sockaddr_in addr{AF_INET, htons(socket_cfg.port_), {htonl(INADDR_ANY)}, {}};
            ASSERT(bind(socket_fd, socket_cfg.is_udp_ ?
                        reinterpret_cast<const struct sockaddr*>(&addr) : rp->ai_addr,
                        sizeof(addr)) == 0, "bind() failed. errno:%" + std::string(strerror(errno)));
        }

        // 7. TCP Server: 監聽連線請求
        // MaxTCPServerBacklog: 最大待處理連線佇列長度
        if (!socket_cfg.is_udp_ &&
            socket_cfg.is_listening_) {
            ASSERT(listen(socket_fd, MaxTCPServerBacklog) == 0,
                   "listen() failed. errno:" + std::string(strerror(errno)));
        }

        // 8. 選用: 啟用接收時間戳 (市場數據延遲測量)
        if (socket_cfg.needs_so_timestamp_) {
            ASSERT(setSOTimestamp(socket_fd),
                   "setSOTimestamp() failed. errno:" + std::string(strerror(errno)));
        }
    }

    return socket_fd;  // 返回完全配置好的 socket
}
}
