# Linux 網路程式設計 API 完整參考手冊

## 目錄
1. [Socket 基礎 API](#socket-基礎-api)
2. [TCP 專用函數](#tcp-專用函數)
3. [UDP 專用函數](#udp-專用函數)
4. [I/O 多工機制](#io-多工機制)
5. [Socket 選項設定](#socket-選項設定)
6. [資料收發函數](#資料收發函數)
7. [位址轉換函數](#位址轉換函數)
8. [完整範例程式](#完整範例程式)

---

## Socket 基礎 API

### 核心函數總覽

| 函數 | 功能 | TCP | UDP | 說明 |
|------|------|-----|-----|------|
| `socket()` | 建立 socket | ✅ | ✅ | 創建通訊端點 |
| `bind()` | 綁定位址 | ✅ | ✅ | 綁定本地 IP 和埠號 |
| `listen()` | 監聽連線 | ✅ | ❌ | TCP 伺服器必須 |
| `accept()` | 接受連線 | ✅ | ❌ | TCP 伺服器必須 |
| `connect()` | 建立連線 | ✅ | 可選 | TCP 必須，UDP 可選 |
| `close()` | 關閉 socket | ✅ | ✅ | 釋放資源 |
| `shutdown()` | 關閉部分連線 | ✅ | ✅ | 半關閉連線 |

---

## 1. socket() - 建立 Socket

### 函數原型
```c
#include <sys/socket.h>

int socket(int domain, int type, int protocol);
```

### 參數詳解

#### domain（協定家族）
| 值 | 說明 | 用途 |
|---|------|------|
| `AF_INET` | IPv4 網路協定 | 最常用 |
| `AF_INET6` | IPv6 網路協定 | IPv6 網路 |
| `AF_UNIX` / `AF_LOCAL` | Unix domain socket | 本機行程間通訊 |
| `AF_PACKET` | 原始封包介面 | 網路監聽、封包分析 |

#### type（socket 類型）
| 值 | 說明 | 特性 | 協定 |
|---|------|------|------|
| `SOCK_STREAM` | 串流 socket | 可靠、有序、雙向位元組流 | TCP |
| `SOCK_DGRAM` | 資料報 socket | 不可靠、無連線、訊息邊界 | UDP |
| `SOCK_RAW` | 原始 socket | 直接存取網路層 | ICMP、自訂協定 |
| `SOCK_SEQPACKET` | 有序封包 socket | 可靠、有序、保留訊息邊界 | SCTP |

**type 可加入的標誌：**
| 標誌 | 說明 |
|------|------|
| `SOCK_NONBLOCK` | 非阻塞模式（Linux 2.6.27+） |
| `SOCK_CLOEXEC` | 執行 exec 時關閉 |

#### protocol（協定）
| 值 | 說明 |
|---|------|
| `0` | 自動選擇（最常用） |
| `IPPROTO_TCP` | 明確指定 TCP |
| `IPPROTO_UDP` | 明確指定 UDP |
| `IPPROTO_ICMP` | ICMP 協定 |
| `IPPROTO_RAW` | 原始 IP 封包 |

### 返回值
- **成功**：socket 檔案描述符（非負整數）
- **失敗**：-1，並設定 errno

### 常見錯誤碼
| errno | 說明 |
|-------|------|
| `EACCES` | 權限不足（如建立 raw socket 需要 root） |
| `EMFILE` | 行程打開檔案數達到上限 |
| `ENFILE` | 系統打開檔案數達到上限 |
| `EPROTONOSUPPORT` | 不支援的協定 |

### 使用範例

```c
// TCP socket
int tcp_sock = socket(AF_INET, SOCK_STREAM, 0);
if (tcp_sock < 0) {
    perror("socket");
    exit(1);
}

// UDP socket
int udp_sock = socket(AF_INET, SOCK_DGRAM, 0);

// 非阻塞 TCP socket（Linux 2.6.27+）
int nonblock_sock = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);

// 原始 socket（需要 root 權限）
int raw_sock = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP);
```

---

## 2. bind() - 綁定位址

### 函數原型
```c
#include <sys/socket.h>

int bind(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
```

### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | socket 檔案描述符 |
| `addr` | 要綁定的位址結構 |
| `addrlen` | 位址結構的長度 |

### sockaddr 結構家族

#### IPv4 位址結構
```c
struct sockaddr_in {
    sa_family_t    sin_family;  // AF_INET
    in_port_t      sin_port;    // 埠號（網路位元組序）
    struct in_addr sin_addr;    // IP 位址
    char           sin_zero[8]; // 填充（必須為 0）
};

struct in_addr {
    uint32_t s_addr;  // IP 位址（網路位元組序）
};
```

#### IPv6 位址結構
```c
struct sockaddr_in6 {
    sa_family_t     sin6_family;   // AF_INET6
    in_port_t       sin6_port;     // 埠號
    uint32_t        sin6_flowinfo; // IPv6 流量資訊
    struct in6_addr sin6_addr;     // IPv6 位址
    uint32_t        sin6_scope_id; // 範圍 ID
};
```

#### 通用位址結構
```c
struct sockaddr {
    sa_family_t sa_family;  // 位址家族
    char        sa_data[14]; // 位址資料
};
```

### 特殊 IP 位址

| IP 位址 | 巨集 | 說明 | 用途 |
|---------|------|------|------|
| `0.0.0.0` | `INADDR_ANY` | 任意位址 | 伺服器監聽所有網卡 |
| `127.0.0.1` | `INADDR_LOOPBACK` | 回環位址 | 本機測試 |
| `255.255.255.255` | `INADDR_BROADCAST` | 廣播位址 | UDP 廣播 |

### 埠號說明

| 埠號範圍 | 類型 | 說明 |
|----------|------|------|
| 0-1023 | 知名埠 | 需要特權（root） |
| 1024-49151 | 註冊埠 | 常用服務埠 |
| 49152-65535 | 動態埠 | 客戶端臨時埠 |
| 0 | 自動分配 | 系統自動選擇可用埠 |

### 返回值
- **成功**：0
- **失敗**：-1，並設定 errno

### 常見錯誤碼
| errno | 說明 | 解決方法 |
|-------|------|----------|
| `EADDRINUSE` | 位址已被使用 | 設定 SO_REUSEADDR 或等待 TIME_WAIT |
| `EACCES` | 權限不足 | 使用 >1024 的埠或提升權限 |
| `EINVAL` | socket 已綁定 | 每個 socket 只能 bind 一次 |
| `EADDRNOTAVAIL` | 位址不可用 | 檢查 IP 位址是否正確 |

### 使用範例

```c
// TCP 伺服器綁定
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

// 設定 SO_REUSEADDR（重要！）
int reuse = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

struct sockaddr_in addr;
memset(&addr, 0, sizeof(addr));
addr.sin_family = AF_INET;
addr.sin_port = htons(8080);           // 埠號 8080
addr.sin_addr.s_addr = INADDR_ANY;     // 監聽所有網卡

if (bind(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
    perror("bind");
    exit(1);
}

// 綁定特定 IP
addr.sin_addr.s_addr = inet_addr("192.168.1.100");
bind(sockfd, (struct sockaddr*)&addr, sizeof(addr));

// UDP 伺服器綁定（與 TCP 相同）
int udp_sock = socket(AF_INET, SOCK_DGRAM, 0);
bind(udp_sock, (struct sockaddr*)&addr, sizeof(addr));

// 客戶端不綁定（自動分配）
// TCP/UDP 客戶端通常不需要 bind，connect() 或第一次 sendto() 會自動綁定
```

---

## 3. listen() - 監聽連線（TCP 專用）

### 函數原型
```c
#include <sys/socket.h>

int listen(int sockfd, int backlog);
```

### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | 已綁定的 socket |
| `backlog` | 連線佇列長度 |

### backlog 詳解

| 值 | 說明 | 建議 |
|---|------|------|
| 小值（1-10） | 低並發場景 | 簡單服務 |
| 中值（128-512） | 一般 Web 服務 | 推薦 128 |
| 大值（1024+） | 高並發場景 | 大型服務 |
| `SOMAXCONN` | 系統最大值 | 通常 128（可調整） |

**注意**：`backlog` 是**已完成三次握手但未被 accept() 的連線數**，不是總連線數。

### 系統限制
```bash
# 查看系統最大值
cat /proc/sys/net/core/somaxconn

# 修改系統最大值
sudo sysctl -w net.core.somaxconn=1024
```

### 返回值
- **成功**：0
- **失敗**：-1

### 使用範例

```c
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_port = htons(8080);
addr.sin_addr.s_addr = INADDR_ANY;

bind(sockfd, (struct sockaddr*)&addr, sizeof(addr));

// 開始監聽
if (listen(sockfd, 128) < 0) {
    perror("listen");
    exit(1);
}

printf("伺服器正在監聽埠 8080...\n");

// 使用系統最大值
listen(sockfd, SOMAXCONN);
```

### TCP 連線佇列

TCP 有兩個佇列：

| 佇列 | 說明 | 狀態 |
|------|------|------|
| **SYN 佇列**（半連線） | 收到 SYN，未完成三次握手 | SYN_RCVD |
| **ACCEPT 佇列**（全連線） | 完成三次握手，等待 accept() | ESTABLISHED |

`backlog` 參數控制 **ACCEPT 佇列**的長度。

---

## 4. accept() - 接受連線（TCP 專用）

### 函數原型
```c
#include <sys/socket.h>

int accept(int sockfd, struct sockaddr *addr, socklen_t *addrlen);
```

### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | 監聽 socket |
| `addr` | 客戶端位址（輸出參數，可為 NULL） |
| `addrlen` | 位址結構長度（輸入輸出參數） |

### 返回值
- **成功**：新的連線 socket 檔案描述符
- **失敗**：-1

### 重要概念

**兩個 socket 的區別：**
| Socket | 功能 | 生命週期 |
|--------|------|----------|
| **監聽 socket** | 接受新連線 | 伺服器整個生命週期 |
| **連線 socket** | 與客戶端通訊 | 單次連線 |

### 常見錯誤碼
| errno | 說明 |
|-------|------|
| `EAGAIN/EWOULDBLOCK` | 非阻塞模式下無連線 |
| `EINTR` | 被信號中斷 |
| `EMFILE` | 行程檔案描述符用盡 |
| `ENFILE` | 系統檔案描述符用盡 |

### accept4() - Linux 擴展
```c
int accept4(int sockfd, struct sockaddr *addr, 
            socklen_t *addrlen, int flags);
```

**flags 可用值：**
| 標誌 | 說明 |
|------|------|
| `SOCK_NONBLOCK` | 返回的 socket 為非阻塞 |
| `SOCK_CLOEXEC` | 執行 exec 時關閉 |

### 使用範例

```c
// 1. 基本用法
struct sockaddr_in client_addr;
socklen_t addr_len = sizeof(client_addr);

int connfd = accept(listenfd, (struct sockaddr*)&client_addr, &addr_len);
if (connfd < 0) {
    perror("accept");
    exit(1);
}

// 取得客戶端資訊
char *client_ip = inet_ntoa(client_addr.sin_addr);
int client_port = ntohs(client_addr.sin_port);
printf("客戶端連線: %s:%d\n", client_ip, client_port);

// 2. 不關心客戶端位址
int connfd = accept(listenfd, NULL, NULL);

// 3. 非阻塞模式處理
while (1) {
    int connfd = accept(listenfd, NULL, NULL);
    if (connfd < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            break;  // 沒有新連線
        }
        perror("accept");
        break;
    }
    // 處理新連線
}

// 4. 使用 accept4（Linux）
int connfd = accept4(listenfd, NULL, NULL, SOCK_NONBLOCK | SOCK_CLOEXEC);
```

---

## 5. connect() - 建立連線

### 函數原型
```c
#include <sys/socket.h>

int connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);
```

### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | socket 檔案描述符 |
| `addr` | 伺服器位址 |
| `addrlen` | 位址結構長度 |

### TCP vs UDP

| 協定 | 是否必須 | 行為 |
|------|----------|------|
| **TCP** | ✅ 必須 | 發起三次握手，阻塞直到連線建立 |
| **UDP** | ❌ 可選 | 不發送封包，只記錄對端位址 |

### 返回值
- **成功**：0
- **失敗**：-1

### 常見錯誤碼
| errno | 說明 | 原因 |
|-------|------|------|
| `ECONNREFUSED` | 連線被拒絕 | 伺服器未監聽該埠 |
| `ETIMEDOUT` | 連線超時 | 網路不通或防火牆阻擋 |
| `ENETUNREACH` | 網路不可達 | 路由問題 |
| `EINPROGRESS` | 連線進行中 | 非阻塞模式正常情況 |
| `EISCONN` | 已經連線 | socket 已連線，不能重複 |

### 非阻塞 connect 處理

```c
// 1. 設定非阻塞
int flags = fcntl(sockfd, F_GETFL, 0);
fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

// 2. 發起連線
if (connect(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
    if (errno == EINPROGRESS) {
        // 正常：連線正在進行中
        
        // 使用 select/poll/epoll 等待連線完成
        fd_set wset;
        FD_ZERO(&wset);
        FD_SET(sockfd, &wset);
        
        struct timeval timeout = {5, 0};  // 5 秒超時
        int ret = select(sockfd + 1, NULL, &wset, NULL, &timeout);
        
        if (ret > 0) {
            // 檢查連線是否成功
            int error;
            socklen_t len = sizeof(error);
            getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &error, &len);
            
            if (error == 0) {
                printf("連線成功\n");
            } else {
                printf("連線失敗: %s\n", strerror(error));
            }
        } else if (ret == 0) {
            printf("連線超時\n");
        }
    } else {
        perror("connect");
    }
}
```

### 使用範例

```c
// TCP 客戶端連線
int sockfd = socket(AF_INET, SOCK_STREAM, 0);

struct sockaddr_in server_addr;
memset(&server_addr, 0, sizeof(server_addr));
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(8080);
server_addr.sin_addr.s_addr = inet_addr("192.168.1.100");

if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
    perror("connect");
    exit(1);
}

printf("已連線到伺服器\n");

// UDP「連線」（可選）
int udp_sock = socket(AF_INET, SOCK_DGRAM, 0);
connect(udp_sock, (struct sockaddr*)&server_addr, sizeof(server_addr));
// UDP connect 後可以使用 send/recv 而不是 sendto/recvfrom
```

---

## 6. close() 和 shutdown() - 關閉連線

### close() - 完全關閉

#### 函數原型
```c
#include <unistd.h>

int close(int fd);
```

#### 行為說明
| 特性 | 說明 |
|------|------|
| **引用計數** | fd 引用計數減 1，為 0 時才真正關閉 |
| **雙向關閉** | 同時關閉讀和寫 |
| **資料處理** | 根據 SO_LINGER 決定 |

#### 返回值
- **成功**：0
- **失敗**：-1

### shutdown() - 半關閉

#### 函數原型
```c
#include <sys/socket.h>

int shutdown(int sockfd, int how);
```

#### how 參數

| 值 | 說明 | 效果 |
|---|------|------|
| `SHUT_RD` (0) | 關閉讀端 | 不能再 recv，但對端仍可 send |
| `SHUT_WR` (1) | 關閉寫端 | 不能再 send，發送 FIN 給對端 |
| `SHUT_RDWR` (2) | 關閉讀寫 | 等同 close，但不減少引用計數 |

### close() vs shutdown() 對比

| 特性 | close() | shutdown() |
|------|---------|------------|
| **影響範圍** | 只影響本行程的 fd | 影響所有引用該 socket 的行程 |
| **引用計數** | 減少引用計數 | 不影響引用計數 |
| **半關閉** | 不支援 | 支援（SHUT_RD/SHUT_WR） |
| **發送 FIN** | 引用計數為 0 時發送 | SHUT_WR 立即發送 |

### 使用範例

```c
// 1. 正常關閉
close(sockfd);

// 2. 優雅關閉（半關閉）
shutdown(sockfd, SHUT_WR);  // 告訴對方：我不再發送資料
// 此時還可以繼續接收對方資料
while (recv(sockfd, buffer, sizeof(buffer), 0) > 0) {
    // 接收剩餘資料
}
close(sockfd);

// 3. 立即關閉（丟棄未發送資料）
struct linger lng = {1, 0};
setsockopt(sockfd, SOL_SOCKET, SO_LINGER, &lng, sizeof(lng));
close(sockfd);  // 發送 RST 而非 FIN

// 4. 父子行程共享 socket
int sockfd = accept(listenfd, NULL, NULL);
pid_t pid = fork();
if (pid == 0) {
    // 子行程
    close(listenfd);  // 關閉監聽 socket
    // 處理 sockfd
    close(sockfd);
    exit(0);
} else {
    // 父行程
    close(sockfd);  // 父行程不處理此連線
}
```

---

## TCP 專用函數

### TCP 狀態機

```
客戶端狀態                    伺服器狀態
                            LISTEN
CLOSED     ─── SYN ──>     SYN_RCVD
SYN_SENT   <── SYN+ACK ─   
ESTABLISHED ─── ACK ──>    ESTABLISHED
    ↓                           ↓
    ↓       [資料傳輸]          ↓
    ↓                           ↓
FIN_WAIT_1  ─── FIN ──>    CLOSE_WAIT
FIN_WAIT_2  <── ACK ───    CLOSE_WAIT
TIME_WAIT   <── FIN ───    LAST_ACK
TIME_WAIT   ─── ACK ──>    CLOSED
CLOSED (2MSL 後)
```

### TCP 函數呼叫流程

#### 伺服器端
```
socket() → bind() → listen() → accept() → recv()/send() → close()
```

#### 客戶端
```
socket() → connect() → send()/recv() → close()
```

---

## UDP 專用函數

### sendto() - UDP 發送

#### 函數原型
```c
#include <sys/socket.h>

ssize_t sendto(int sockfd, const void *buf, size_t len, int flags,
               const struct sockaddr *dest_addr, socklen_t addrlen);
```

#### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | UDP socket |
| `buf` | 要發送的資料 |
| `len` | 資料長度 |
| `flags` | 發送標誌（通常為 0） |
| `dest_addr` | 目標位址 |
| `addrlen` | 位址長度 |

#### 返回值
- **成功**：實際發送的位元組數
- **失敗**：-1

### recvfrom() - UDP 接收

#### 函數原型
```c
ssize_t recvfrom(int sockfd, void *buf, size_t len, int flags,
                 struct sockaddr *src_addr, socklen_t *addrlen);
```

#### 參數說明
| 參數 | 說明 |
|------|------|
| `sockfd` | UDP socket |
| `buf` | 接收緩衝區 |
| `len` | 緩衝區大小 |
| `flags` | 接收標誌（通常為 0） |
| `src_addr` | 來源位址（輸出參數） |
| `addrlen` | 位址長度（輸入輸出參數） |

#### 返回值
- **成功**：實際接收的位元組數
- **失敗**：-1

### UDP 完整範例

```c
// ============ UDP 伺服器 ============
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in server_addr;
memset(&server_addr, 0, sizeof(server_addr));
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(8080);
server_addr.sin_addr.s_addr = INADDR_ANY;

bind(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));

char buffer[1024];
struct sockaddr_in client_addr;
socklen_t addr_len = sizeof(client_addr);

while (1) {
    // 接收資料
    int n = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                     (struct sockaddr*)&client_addr, &addr_len);
    if (n > 0) {
        buffer[n] = '\0';
        printf("收到來自 %s:%d 的資料: %s\n",
               inet_ntoa(client_addr.sin_addr),
               ntohs(client_addr.sin_port),
               buffer);
        
        // 回傳資料
        sendto(sockfd, buffer, n, 0,
               (struct sockaddr*)&client_addr, addr_len);
    }
}

// ============ UDP 客戶端 ============
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in server_addr;
memset(&server_addr, 0, sizeof(server_addr));
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(8080);
server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

char *msg = "Hello, UDP!";
sendto(sockfd, msg, strlen(msg), 0,
       (struct sockaddr*)&server_addr, sizeof(server_addr));

// 接收回應
char buffer[1024];
struct sockaddr_in recv_addr;
socklen_t addr_len = sizeof(recv_addr);
int n = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                 (struct sockaddr*)&recv_addr, &addr_len);
buffer[n] = '\0';
printf("伺服器回應: %s\n", buffer);

close(sockfd);
```

### UDP 使用「連線」模式

```c
// UDP 也可以使用 connect()，好處：
// 1. 可以使用 send()/recv() 而非 sendto()/recvfrom()
// 2. 可以接收 ICMP 錯誤（如 ECONNREFUSED）

int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

struct sockaddr_in server_addr;
server_addr.sin_family = AF_INET;
server_addr.sin_port = htons(8080);
server_addr.sin_addr.s_addr = inet_addr("127.0.0.1");

// 「連線」到伺服器
connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr));

// 現在可以使用 send/recv
send(sockfd, "Hello", 5, 0);
char buffer[1024];
recv(sockfd, buffer, sizeof(buffer), 0);

close(sockfd);
```

---

## I/O 多工機制

### Socket 阻塞與非阻塞模式

在討論 I/O 多工之前，需要先理解 **socket 本身就有阻塞和非阻塞兩種模式**。

#### 1. 阻塞模式 (Blocking I/O) - 預設模式

```c
int sockfd = socket(AF_INET, SOCK_STREAM, 0);
// 預設就是阻塞模式

// accept() 會阻塞等待，直到有連線進來
int connfd = accept(sockfd, NULL, NULL);

// recv() 會阻塞等待，直到收到資料
recv(connfd, buffer, sizeof(buffer), 0);
```

#### 2. 非阻塞模式 (Non-blocking I/O)

```c
// 設定非阻塞
int flags = fcntl(sockfd, F_GETFL, 0);
fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

// 或建立時直接設定 (Linux 2.6.27+)
int sockfd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);

// accept() 立即返回，沒連線就返回 -1 (errno=EAGAIN)
int connfd = accept(sockfd, NULL, NULL);

// recv() 立即返回，沒資料就返回 -1 (errno=EAGAIN)
recv(connfd, buffer, sizeof(buffer), 0);
```

---

### 為什麼需要 select/poll/epoll？

**問題場景：**
- 你有 100 個 socket 需要監控
- 不知道哪個 socket 有資料可讀

#### ❌ 沒有 I/O 多工的解決方案

##### 方案 1：阻塞模式 - 無法同時監控多個 socket
```c
// 只能一個一個檢查，會卡在第一個 recv
recv(sock1, buf, size, 0);  // 卡在這裡
recv(sock2, buf, size, 0);  // 永遠執行不到
```

##### 方案 2：非阻塞模式 - CPU 空轉浪費資源
```c
// 輪詢 (polling) - 不斷檢查每個 socket
while (1) {
    for (int i = 0; i < 100; i++) {
        int n = recv(socks[i], buf, size, 0);
        if (n > 0) {
            // 處理資料
        }
    }
    // CPU 空轉，100% 使用率！
}
```

##### 方案 3：多執行緒 - 資源浪費
```c
// 為每個 socket 開一個執行緒
for (int i = 0; i < 100; i++) {
    pthread_create(&thread, NULL, handle_client, &socks[i]);
}
// 100 個連線 = 100 個執行緒！記憶體、context switch 開銷大
```

#### ✅ 有 select/poll/epoll 的解決方案

```c
int epfd = epoll_create1(0);

// 註冊 100 個 socket
for (int i = 0; i < 100; i++) {
    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = socks[i];
    epoll_ctl(epfd, EPOLL_CTL_ADD, socks[i], &ev);
}

// 一次監控所有 socket，只有就緒的會被通知
struct epoll_event events[100];
while (1) {
    // 這裡會阻塞等待，但只要有任何一個 socket 就緒就會返回
    int nfds = epoll_wait(epfd, events, 100, -1);

    for (int i = 0; i < nfds; i++) {
        int fd = events[i].data.fd;
        recv(fd, buffer, size, 0);  // 這裡保證有資料，不會阻塞
    }
}
```

**核心優勢：**
1. **不需要輪詢** - 系統會通知你哪些 socket 就緒
2. **不浪費 CPU** - 沒有事件時進程休眠
3. **可擴展性好** - 輕鬆處理成千上萬的連線

---

### I/O 模型總結對比

| 模式 | 優點 | 缺點 | 使用場景 |
|------|------|------|----------|
| **阻塞 I/O** | 簡單 | 一次只能處理一個連線 | 單一連線、簡單應用 |
| **非阻塞 I/O (輪詢)** | 可處理多個連線 | CPU 空轉浪費 | **不建議單獨使用** |
| **多執行緒/行程** | 可處理多個連線 | 資源開銷大 | 連線數少 (<100) |
| **select/poll/epoll** | 高效監控多個連線 | 程式碼複雜度高 | **高並發 (>100 連線)** |

**實際使用建議：**

| 連線數 | 推薦方案 | 範例 |
|--------|----------|------|
| **< 10** | 阻塞 I/O + 多執行緒 | `pthread_create(&tid, NULL, handle_client, &connfd);` |
| **100-1000** | poll + 非阻塞 | `poll(fds, nfds, -1);` |
| **> 1000** | epoll + 非阻塞 + 邊緣觸發 | `epoll_wait(epfd, events, MAX_EVENTS, -1);` |

**核心結論：**
1. ✅ **Socket 本身可以阻塞/非阻塞** - 這是 socket 的屬性
2. ✅ **select/poll/epoll 用於監控多個 socket** - 解決「不知道哪個 socket 就緒」的問題
3. ✅ **搭配使用才高效** - epoll + 非阻塞是高並發伺服器的標準做法

---

### select、poll、epoll 比較表

| 特性 | select | poll | epoll |
|------|--------|------|-------|
| **監控數量限制** | 1024（FD_SETSIZE） | 無限制 | 無限制 |
| **時間複雜度** | O(n) | O(n) | O(1) |
| **記憶體複製** | 每次都要複製 | 每次都要複製 | 只需註冊一次 |
| **跨平台** | ✅ 所有 Unix/Linux/Windows | ✅ 所有 Unix/Linux | ❌ 僅 Linux |
| **事件通知** | 水平觸發 | 水平觸發 | 水平/邊緣觸發 |
| **適用場景** | <100 連線 | 100-1000 連線 | >1000 連線 |

### select() - POSIX 標準

#### 函數原型
```c
#include <sys/select.h>

int select(int nfds, fd_set *readfds, fd_set *writefds,
           fd_set *exceptfds, struct timeval *timeout);
```

#### 參數說明
| 參數 | 說明 |
|------|------|
| `nfds` | 最大 fd + 1 |
| `readfds` | 監控可讀的 fd 集合 |
| `writefds` | 監控可寫的 fd 集合 |
| `exceptfds` | 監控異常的 fd 集合 |
| `timeout` | 超時時間 |

#### fd_set 操作巨集
| 巨集 | 功能 |
|------|------|
| `FD_ZERO(fd_set *set)` | 清空集合 |
| `FD_SET(int fd, fd_set *set)` | 加入 fd |
| `FD_CLR(int fd, fd_set *set)` | 移除 fd |
| `FD_ISSET(int fd, fd_set *set)` | 檢查 fd 是否就緒 |

#### 使用範例
```c
fd_set readfds;
struct timeval timeout;

while (1) {
    FD_ZERO(&readfds);
    FD_SET(sockfd, &readfds);
    
    timeout.tv_sec = 5;
    timeout.tv_usec = 0;
    
    int ret = select(sockfd + 1, &readfds, NULL, NULL, &timeout);
    
    if (ret > 0 && FD_ISSET(sockfd, &readfds)) {
        // sockfd 可讀
        recv(sockfd, buffer, sizeof(buffer), 0);
    }
}
```

### poll() - System V 標準

#### 函數原型
```c
#include <poll.h>

int poll(struct pollfd *fds, nfds_t nfds, int timeout);

struct pollfd {
    int   fd;       // 檔案描述符
    short events;   // 要監控的事件
    short revents;  // 實際發生的事件
};
```

#### events 標誌
| 標誌 | 說明 |
|------|------|
| `POLLIN` | 有資料可讀 |
| `POLLOUT` | 可以寫入資料 |
| `POLLERR` | 發生錯誤 |
| `POLLHUP` | 連線掛斷 |
| `POLLNVAL` | 無效的 fd |

#### 使用範例
```c
struct pollfd fds[2];
fds[0].fd = sockfd;
fds[0].events = POLLIN | POLLOUT;

while (1) {
    int ret = poll(fds, 1, 5000);  // 5 秒超時
    
    if (ret > 0) {
        if (fds[0].revents & POLLIN) {
            recv(sockfd, buffer, sizeof(buffer), 0);
        }
        if (fds[0].revents & POLLOUT) {
            send(sockfd, data, len, 0);
        }
    }
}
```

### epoll() - Linux 專用高效能方案

#### 三個核心函數

##### 1. epoll_create1() - 建立 epoll 實例
```c
int epoll_create1(int flags);
```

| 參數 | 說明 |
|------|------|
| `flags` | 0 或 `EPOLL_CLOEXEC` |
| **返回值** | epoll 檔案描述符 |

##### 2. epoll_ctl() - 控制 epoll
```c
int epoll_ctl(int epfd, int op, int fd, struct epoll_event *event);
```

| 參數 | 說明 |
|------|------|
| `epfd` | epoll 實例 |
| `op` | 操作（ADD/MOD/DEL） |
| `fd` | 要操作的檔案描述符 |
| `event` | 事件結構 |

**op 操作類型：**
| 值 | 說明 |
|---|------|
| `EPOLL_CTL_ADD` | 加入新的監控 |
| `EPOLL_CTL_MOD` | 修改已有的監控 |
| `EPOLL_CTL_DEL` | 刪除監控 |

##### 3. epoll_wait() - 等待事件
```c
int epoll_wait(int epfd, struct epoll_event *events, 
               int maxevents, int timeout);
```

#### epoll_event 結構
```c
struct epoll_event {
    uint32_t     events;   // 事件類型
    epoll_data_t data;     // 使用者資料
};

typedef union epoll_data {
    void    *ptr;
    int      fd;
    uint32_t u32;
    uint64_t u64;
} epoll_data_t;
```

#### events 標誌
| 標誌 | 說明 |
|------|------|
| `EPOLLIN` | 可讀 |
| `EPOLLOUT` | 可寫 |
| `EPOLLET` | **邊緣觸發模式** |
| `EPOLLONESHOT` | 只觸發一次 |
| `EPOLLRDHUP` | 對端關閉連線 |

#### 觸發模式對比

| 模式 | 說明 | 優缺點 |
|------|------|--------|
| **水平觸發（LT）** | 只要有資料就通知 | 簡單，但可能重複通知 |
| **邊緣觸發（ET）** | 狀態變化時才通知一次 | 高效能，但必須一次讀完 |

#### 完整範例
```c
// 1. 建立 epoll
int epfd = epoll_create1(0);

// 2. 註冊監聽 socket
struct epoll_event ev;
ev.events = EPOLLIN | EPOLLET;
ev.data.fd = listenfd;
epoll_ctl(epfd, EPOLL_CTL_ADD, listenfd, &ev);

// 3. 事件迴圈
struct epoll_event events[MAX_EVENTS];
while (1) {
    int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
    
    for (int i = 0; i < nfds; i++) {
        int fd = events[i].data.fd;
        
        if (fd == listenfd) {
            // 處理新連線
            int connfd = accept(listenfd, NULL, NULL);
            setnonblocking(connfd);
            
            ev.events = EPOLLIN | EPOLLET;
            ev.data.fd = connfd;
            epoll_ctl(epfd, EPOLL_CTL_ADD, connfd, &ev);
        } else {
            // 處理資料
            if (events[i].events & EPOLLIN) {
                // 邊緣觸發必須迴圈讀取
                while (1) {
                    int n = recv(fd, buffer, sizeof(buffer), 0);
                    if (n > 0) {
                        // 處理資料
                    } else if (n == 0 || errno != EAGAIN) {
                        epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL);
                        close(fd);
                        break;
                    } else {
                        break;  // 資料讀完
                    }
                }
            }
        }
    }
}
```

---

## Socket 選項設定

### getsockopt() / setsockopt()

#### 函數原型
```c
#include <sys/socket.h>

int getsockopt(int sockfd, int level, int optname,
               void *optval, socklen_t *optlen);

int setsockopt(int sockfd, int level, int optname,
               const void *optval, socklen_t optlen);
```

### SOL_SOCKET 層級選項

| 選項 | 資料型別 | 說明 | 預設值 |
|------|----------|------|--------|
| `SO_REUSEADDR` | int | 允許重用本地位址 | 0（關閉） |
| `SO_REUSEPORT` | int | 允許多個 socket 綁定同一埠 | 0（關閉） |
| `SO_KEEPALIVE` | int | 啟用 TCP keepalive | 0（關閉） |
| `SO_RCVBUF` | int | 接收緩衝區大小（位元組） | 系統預設 |
| `SO_SNDBUF` | int | 傳送緩衝區大小（位元組） | 系統預設 |
| `SO_RCVTIMEO` | struct timeval | 接收超時 | 無限等待 |
| `SO_SNDTIMEO` | struct timeval | 傳送超時 | 無限等待 |
| `SO_LINGER` | struct linger | 關閉時行為 | 優雅關閉 |
| `SO_BROADCAST` | int | 允許廣播（UDP） | 0（關閉） |
| `SO_ERROR` | int | 取得錯誤狀態（唯讀） | - |
| `SO_TYPE` | int | 取得 socket 類型（唯讀） | - |

### IPPROTO_TCP 層級選項

| 選項 | 資料型別 | 說明 | 預設值 |
|------|----------|------|--------|
| `TCP_NODELAY` | int | 禁用 Nagle 演算法 | 0（啟用 Nagle） |
| `TCP_KEEPIDLE` | int | Keepalive 開始時間（秒） | 7200 |
| `TCP_KEEPINTVL` | int | Keepalive 間隔（秒） | 75 |
| `TCP_KEEPCNT` | int | Keepalive 重試次數 | 9 |
| `TCP_CORK` | int | 暫停資料傳送（攢夠再發） | 0（關閉） |
| `TCP_DEFER_ACCEPT` | int | 延遲 accept（有資料才喚醒） | 0（關閉） |
| `TCP_QUICKACK` | int | 快速確認（禁用延遲 ACK） | 0（啟用延遲） |

### IPPROTO_IP 層級選項

| 選項 | 資料型別 | 說明 |
|------|----------|------|
| `IP_TOS` | int | 設定 Type of Service |
| `IP_TTL` | int | 設定 Time to Live |
| `IP_MULTICAST_LOOP` | int | 多播封包是否回環 |
| `IP_MULTICAST_TTL` | int | 多播封包 TTL |
| `IP_ADD_MEMBERSHIP` | struct ip_mreq | 加入多播群組 |
| `IP_DROP_MEMBERSHIP` | struct ip_mreq | 離開多播群組 |

### 常用範例

```c
// 1. SO_REUSEADDR（伺服器必備）
int reuse = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));

// 2. SO_REUSEPORT（負載均衡）
int reuse_port = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &reuse_port, sizeof(reuse_port));

// 3. TCP_NODELAY（低延遲）
int nodelay = 1;
setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, &nodelay, sizeof(nodelay));

// 4. SO_KEEPALIVE + 參數設定
int keepalive = 1;
int idle = 60;        // 60 秒後開始
int interval = 5;     // 每 5 秒一次
int count = 3;        // 失敗 3 次斷線

setsockopt(sockfd, SOL_SOCKET, SO_KEEPALIVE, &keepalive, sizeof(keepalive));
setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPIDLE, &idle, sizeof(idle));
setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPINTVL, &interval, sizeof(interval));
setsockopt(sockfd, IPPROTO_TCP, TCP_KEEPCNT, &count, sizeof(count));

// 5. SO_LINGER（控制 close 行為）
struct linger lng;
lng.l_onoff = 1;
lng.l_linger = 0;  // 立即關閉，發送 RST
setsockopt(sockfd, SOL_SOCKET, SO_LINGER, &lng, sizeof(lng));

// 6. SO_RCVTIMEO（接收超時）
struct timeval timeout;
timeout.tv_sec = 5;
timeout.tv_usec = 0;
setsockopt(sockfd, SOL_SOCKET, SO_RCVTIMEO, &timeout, sizeof(timeout));

// 7. SO_RCVBUF / SO_SNDBUF（緩衝區大小）
int buf_size = 64 * 1024;  // 64KB
setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buf_size, sizeof(buf_size));
setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &buf_size, sizeof(buf_size));

// 8. 取得 socket 類型
int type;
socklen_t len = sizeof(type);
getsockopt(sockfd, SOL_SOCKET, SO_TYPE, &type, &len);
if (type == SOCK_STREAM) {
    printf("TCP socket\n");
} else if (type == SOCK_DGRAM) {
    printf("UDP socket\n");
}

// 9. 取得錯誤狀態（非阻塞 connect 後使用）
int error;
socklen_t len = sizeof(error);
getsockopt(sockfd, SOL_SOCKET, SO_ERROR, &error, &len);
if (error == 0) {
    printf("連線成功\n");
}
```

---

## 資料收發函數

### 函數總覽

| 函數 | TCP | UDP | 說明 |
|------|-----|-----|------|
| `recv()` | ✅ | ✅ | 接收資料 |
| `send()` | ✅ | ✅ | 傳送資料 |
| `recvfrom()` | ✅ | ✅ | 接收資料（含來源位址） |
| `sendto()` | ✅ | ✅ | 傳送資料（指定目標位址） |
| `read()` | ✅ | ✅ | POSIX 讀取（無標誌） |
| `write()` | ✅ | ✅ | POSIX 寫入（無標誌） |
| `recvmsg()` | ✅ | ✅ | 高階接收（支援控制訊息） |
| `sendmsg()` | ✅ | ✅ | 高階傳送（支援控制訊息） |

### recv() - 接收資料

#### 函數原型
```c
#include <sys/socket.h>

ssize_t recv(int sockfd, void *buf, size_t len, int flags);
```

#### flags 標誌

| 標誌 | 說明 |
|------|------|
| `0` | 預設行為（最常用） |
| `MSG_PEEK` | 偷看資料但不移除 |
| `MSG_WAITALL` | 等到收滿 len 位元組 |
| `MSG_DONTWAIT` | 非阻塞接收（單次） |
| `MSG_OOB` | 接收帶外資料 |
| `MSG_TRUNC` | 返回真實長度（即使被截斷） |

#### 返回值說明

| 返回值 | 說明 |
|--------|------|
| `> 0` | 實際接收的位元組數 |
| `0` | 對方關閉連線（TCP） |
| `-1` | 錯誤（檢查 errno） |

#### 常見 errno

| errno | 說明 | 處理方式 |
|-------|------|----------|
| `EAGAIN` / `EWOULDBLOCK` | 非阻塞模式無資料 | 稍後重試 |
| `EINTR` | 被信號中斷 | 重新呼叫 |
| `ECONNRESET` | 連線被重置 | 關閉 socket |
| `ETIMEDOUT` | 接收超時 | 關閉 socket |

#### 使用範例

```c
// 1. 基本用法
char buffer[1024];
int n = recv(sockfd, buffer, sizeof(buffer), 0);
if (n > 0) {
    printf("收到 %d 位元組\n", n);
} else if (n == 0) {
    printf("對方關閉連線\n");
} else {
    perror("recv");
}

// 2. 偷看資料（不移除）
int n = recv(sockfd, buffer, sizeof(buffer), MSG_PEEK);
// 資料還在緩衝區，下次 recv 還會讀到

// 3. 非阻塞處理
int n = recv(sockfd, buffer, sizeof(buffer), 0);
if (n == -1) {
    if (errno == EAGAIN || errno == EWOULDBLOCK) {
        // 無資料，稍後再試
    } else {
        perror("recv");
    }
}

// 4. 邊緣觸發必須迴圈讀取
while (1) {
    int n = recv(sockfd, buffer, sizeof(buffer), 0);
    if (n > 0) {
        // 處理資料
    } else if (n == 0) {
        break;  // 對方關閉
    } else {
        if (errno == EAGAIN) {
            break;  // 讀完了
        }
        perror("recv");
        break;
    }
}

// 5. 確保接收指定長度
int total = 0;
int len = 1024;
while (total < len) {
    int n = recv(sockfd, buffer + total, len - total, 0);
    if (n > 0) {
        total += n;
    } else if (n == 0) {
        printf("連線關閉，只收到 %d 位元組\n", total);
        break;
    } else {
        perror("recv");
        break;
    }
}
```

### send() - 傳送資料

#### 函數原型
```c
ssize_t send(int sockfd, const void *buf, size_t len, int flags);
```

#### flags 標誌

| 標誌 | 說明 |
|------|------|
| `0` | 預設行為 |
| `MSG_NOSIGNAL` | 不產生 SIGPIPE 信號 |
| `MSG_DONTWAIT` | 非阻塞發送 |
| `MSG_MORE` | 還有更多資料（減少封包數） |
| `MSG_OOB` | 發送帶外資料 |

#### 返回值

| 返回值 | 說明 |
|--------|------|
| `> 0` | 實際傳送的位元組數（可能小於 len） |
| `-1` | 錯誤 |

#### 常見 errno

| errno | 說明 |
|-------|------|
| `EAGAIN` / `EWOULDBLOCK` | 傳送緩衝區滿 |
| `EPIPE` | 連線已斷（會觸發 SIGPIPE） |
| `ECONNRESET` | 連線被重置 |

#### 使用範例

```c
// 1. 基本用法
char *data = "Hello, World!";
int n = send(sockfd, data, strlen(data), 0);

// 2. 避免 SIGPIPE
send(sockfd, data, len, MSG_NOSIGNAL);

// 3. 確保全部發送
int total = 0;
int len = strlen(data);
while (total < len) {
    int n = send(sockfd, data + total, len - total, MSG_NOSIGNAL);
    if (n > 0) {
        total += n;
    } else if (n == -1) {
        if (errno == EAGAIN) {
            continue;  // 緩衝區滿，稍後再試
        }
        perror("send");
        break;
    }
}

// 4. MSG_MORE 優化（減少封包數）
send(sockfd, header, header_len, MSG_MORE | MSG_NOSIGNAL);
send(sockfd, body, body_len, MSG_NOSIGNAL);  // 最後一次不加 MSG_MORE
```

### recvfrom() / sendto() - UDP 專用

見前面 UDP 專用函數章節。

### read() / write() - POSIX 標準

```c
#include <unistd.h>

ssize_t read(int fd, void *buf, size_t count);
ssize_t write(int fd, const void *buf, size_t count);
```

**與 recv/send 的區別：**
- `read/write` 不支援 flags 參數
- `read/write` 是通用 I/O 函數，不限於 socket
- `recv/send` 是專門為 socket 設計的

---

## 位址轉換函數

### 字串 ↔ 二進位

#### inet_pton() / inet_ntop() - 推薦使用

```c
#include <arpa/inet.h>

// 字串 → 二進位
int inet_pton(int af, const char *src, void *dst);

// 二進位 → 字串
const char *inet_ntop(int af, const void *src, char *dst, socklen_t size);
```

| 參數 | 說明 |
|------|------|
| `af` | `AF_INET` 或 `AF_INET6` |
| `src` | 來源位址 |
| `dst` | 目標緩衝區 |
| `size` | 緩衝區大小 |

**使用範例：**
```c
// IPv4 字串 → 二進位
struct sockaddr_in addr;
inet_pton(AF_INET, "192.168.1.100", &addr.sin_addr);

// IPv4 二進位 → 字串
char ip_str[INET_ADDRSTRLEN];
inet_ntop(AF_INET, &addr.sin_addr, ip_str, sizeof(ip_str));
printf("IP: %s\n", ip_str);

// IPv6
struct sockaddr_in6 addr6;
inet_pton(AF_INET6, "::1", &addr6.sin6_addr);

char ip6_str[INET6_ADDRSTRLEN];
inet_ntop(AF_INET6, &addr6.sin6_addr, ip6_str, sizeof(ip6_str));
```

#### inet_addr() / inet_ntoa() - 舊版 API

```c
// 字串 → 二進位（僅 IPv4）
in_addr_t inet_addr(const char *cp);

// 二進位 → 字串（僅 IPv4，不可重入）
char *inet_ntoa(struct in_addr in);
```

**注意**：`inet_ntoa()` 不是執行緒安全的！

### 主機名稱解析

#### getaddrinfo() / getnameinfo() - 現代方法

```c
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

int getaddrinfo(const char *node, const char *service,
                const struct addrinfo *hints,
                struct addrinfo **res);

void freeaddrinfo(struct addrinfo *res);

int getnameinfo(const struct sockaddr *addr, socklen_t addrlen,
                char *host, socklen_t hostlen,
                char *serv, socklen_t servlen, int flags);
```

**使用範例：**
```c
// 解析主機名稱
struct addrinfo hints, *res;
memset(&hints, 0, sizeof(hints));
hints.ai_family = AF_UNSPEC;     // IPv4 或 IPv6
hints.ai_socktype = SOCK_STREAM; // TCP

int ret = getaddrinfo("www.google.com", "80", &hints, &res);
if (ret == 0) {
    // 使用 res
    int sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
    connect(sockfd, res->ai_addr, res->ai_addrlen);
    
    freeaddrinfo(res);  // 釋放記憶體
}

// 反向解析（位址 → 主機名稱）
struct sockaddr_in addr;
char host[NI_MAXHOST];
char serv[NI_MAXSERV];

getnameinfo((struct sockaddr*)&addr, sizeof(addr),
            host, sizeof(host),
            serv, sizeof(serv),
            NI_NUMERICSERV);
printf("主機: %s, 埠: %s\n", host, serv);
```

### 位元組序轉換

| 函數 | 說明 |
|------|------|
| `htons()` | Host to Network Short（16 位元） |
| `htonl()` | Host to Network Long（32 位元） |
| `ntohs()` | Network to Host Short（16 位元） |
| `ntohl()` | Network to Host Long（32 位元） |

```c
// 埠號必須轉換為網路位元組序
uint16_t port = 8080;
addr.sin_port = htons(port);

// IP 位址也要轉換
uint32_t ip = 0xC0A80164;  // 192.168.1.100
addr.sin_addr.s_addr = htonl(ip);

// 讀取時轉回主機位元組序
uint16_t local_port = ntohs(addr.sin_port);
```

---

## 完整範例程式

### TCP Echo 伺服器（epoll + 非阻塞 + ET）

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define MAX_EVENTS 1024
#define BUFFER_SIZE 4096

// 設定非阻塞
void setnonblocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}

int main() {
    // 1. 建立 socket
    int listenfd = socket(AF_INET, SOCK_STREAM, 0);
    if (listenfd < 0) {
        perror("socket");
        exit(1);
    }
    
    // 2. 設定 SO_REUSEADDR
    int reuse = 1;
    setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, &reuse, sizeof(reuse));
    
    // 3. 綁定位址
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    if (bind(listenfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(1);
    }
    
    // 4. 開始監聽
    if (listen(listenfd, 128) < 0) {
        perror("listen");
        exit(1);
    }
    
    printf("伺服器正在監聽埠 %d...\n", PORT);
    
    // 5. 設定非阻塞
    setnonblocking(listenfd);
    
    // 6. 建立 epoll
    int epfd = epoll_create1(0);
    if (epfd < 0) {
        perror("epoll_create1");
        exit(1);
    }
    
    // 7. 註冊監聽 socket（邊緣觸發）
    struct epoll_event ev;
    ev.events = EPOLLIN | EPOLLET;
    ev.data.fd = listenfd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, listenfd, &ev);
    
    // 8. 事件迴圈
    struct epoll_event events[MAX_EVENTS];
    char buffer[BUFFER_SIZE];
    
    while (1) {
        int nfds = epoll_wait(epfd, events, MAX_EVENTS, -1);
        if (nfds < 0) {
            perror("epoll_wait");
            continue;
        }
        
        for (int i = 0; i < nfds; i++) {
            int fd = events[i].data.fd;
            
            // 新連線
            if (fd == listenfd) {
                while (1) {
                    struct sockaddr_in client_addr;
                    socklen_t len = sizeof(client_addr);
                    int connfd = accept(listenfd, (struct sockaddr*)&client_addr, &len);
                    
                    if (connfd < 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) {
                            break;  // 沒有新連線了
                        }
                        perror("accept");
                        break;
                    }
                    
                    printf("新連線: %s:%d (fd=%d)\n",
                           inet_ntoa(client_addr.sin_addr),
                           ntohs(client_addr.sin_port),
                           connfd);
                    
                    // 設定非阻塞
                    setnonblocking(connfd);
                    
                    // 加入 epoll
                    ev.events = EPOLLIN | EPOLLET;
                    ev.data.fd = connfd;
                    epoll_ctl(epfd, EPOLL_CTL_ADD, connfd, &ev);
                }
            }
            // 客戶端資料
            else {
                if (events[i].events & EPOLLIN) {
                    // 邊緣觸發必須迴圈讀取
                    while (1) {
                        int n = recv(fd, buffer, sizeof(buffer), 0);
                        
                        if (n > 0) {
                            printf("收到 %d 位元組 (fd=%d)\n", n, fd);
                            
                            // Echo 回去
                            int sent = 0;
                            while (sent < n) {
                                int s = send(fd, buffer + sent, n - sent, MSG_NOSIGNAL);
                                if (s > 0) {
                                    sent += s;
                                } else if (s == -1) {
                                    if (errno != EAGAIN) {
                                        perror("send");
                                        goto close_conn;
                                    }
                                    break;
                                }
                            }
                        } else if (n == 0) {
                            printf("客戶端關閉連線 (fd=%d)\n", fd);
                            goto close_conn;
                        } else {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                                break;  // 資料讀完了
                            }
                            perror("recv");
                            goto close_conn;
                        }
                    }
                }
                
                if (events[i].events & (EPOLLERR | EPOLLHUP)) {
                    printf("連線錯誤或掛斷 (fd=%d)\n", fd);
                    goto close_conn;
                }
                
                continue;
                
close_conn:
                epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL);
                close(fd);
            }
        }
    }
    
    close(epfd);
    close(listenfd);
    return 0;
}
```

### TCP 客戶端

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8080

int main() {
    // 1. 建立 socket
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(1);
    }
    
    // 2. 連線到伺服器
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);
    
    if (connect(sockfd, (struct sockaddr*)&server_addr, sizeof(server_addr)) < 0) {
        perror("connect");
        exit(1);
    }
    
    printf("已連線到伺服器 %s:%d\n", SERVER_IP, SERVER_PORT);
    
    // 3. 發送和接收資料
    char buffer[1024];
    while (1) {
        printf("輸入訊息: ");
        fgets(buffer, sizeof(buffer), stdin);
        
        // 移除換行符
        buffer[strcspn(buffer, "\n")] = 0;
        
        if (strlen(buffer) == 0) {
            continue;
        }
        
        if (strcmp(buffer, "quit") == 0) {
            break;
        }
        
        // 發送資料
        int len = strlen(buffer);
        int sent = 0;
        while (sent < len) {
            int n = send(sockfd, buffer + sent, len - sent, 0);
            if (n > 0) {
                sent += n;
            } else {
                perror("send");
                goto cleanup;
            }
        }
        
        // 接收回應
        int n = recv(sockfd, buffer, sizeof(buffer) - 1, 0);
        if (n > 0) {
            buffer[n] = '\0';
            printf("伺服器回應: %s\n", buffer);
        } else if (n == 0) {
            printf("伺服器關閉連線\n");
            break;
        } else {
            perror("recv");
            break;
        }
    }
    
cleanup:
    close(sockfd);
    return 0;
}
```

### UDP Echo 伺服器

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main() {
    // 1. 建立 UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(1);
    }
    
    // 2. 綁定位址
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(PORT);
    addr.sin_addr.s_addr = INADDR_ANY;
    
    if (bind(sockfd, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        perror("bind");
        exit(1);
    }
    
    printf("UDP 伺服器正在監聽埠 %d...\n", PORT);
    
    // 3. 接收和發送資料
    char buffer[BUFFER_SIZE];
    struct sockaddr_in client_addr;
    socklen_t addr_len;
    
    while (1) {
        addr_len = sizeof(client_addr);
        
        // 接收資料
        int n = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0,
                        (struct sockaddr*)&client_addr, &addr_len);
        
        if (n > 0) {
            buffer[n] = '\0';
            printf("收到來自 %s:%d 的資料: %s\n",
                   inet_ntoa(client_addr.sin_addr),
                   ntohs(client_addr.sin_port),
                   buffer);
            
            // Echo 回去
            sendto(sockfd, buffer, n, 0,
                   (struct sockaddr*)&client_addr, addr_len);
        } else if (n < 0) {
            perror("recvfrom");
        }
    }
    
    close(sockfd);
    return 0;
}
```

### UDP 客戶端

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_IP "127.0.0.1"
#define SERVER_PORT 8080

int main() {
    // 1. 建立 UDP socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    if (sockfd < 0) {
        perror("socket");
        exit(1);
    }
    
    // 2. 設定伺服器位址
    struct sockaddr_in server_addr;
    memset(&server_addr, 0, sizeof(server_addr));
    server_addr.sin_family = AF_INET;
    server_addr.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, SERVER_IP, &server_addr.sin_addr);
    
    // 3. 發送和接收資料
    char buffer[1024];
    while (1) {
        printf("輸入訊息: ");
        fgets(buffer, sizeof(buffer), stdin);
        buffer[strcspn(buffer, "\n")] = 0;
        
        if (strlen(buffer) == 0) {
            continue;
        }
        
        if (strcmp(buffer, "quit") == 0) {
            break;
        }
        
        // 發送資料
        sendto(sockfd, buffer, strlen(buffer), 0,
               (struct sockaddr*)&server_addr, sizeof(server_addr));
        
        // 接收回應
        struct sockaddr_in recv_addr;
        socklen_t addr_len = sizeof(recv_addr);
        int n = recvfrom(sockfd, buffer, sizeof(buffer) - 1, 0,
                        (struct sockaddr*)&recv_addr, &addr_len);
        
        if (n > 0) {
            buffer[n] = '\0';
            printf("伺服器回應: %s\n", buffer);
        }
    }
    
    close(sockfd);
    return 0;
}
```

---

## 編譯和執行

### 編譯命令

```bash
# TCP 伺服器
gcc -o tcp_server tcp_server.c -Wall -O2

# TCP 客戶端
gcc -o tcp_client tcp_client.c -Wall -O2

# UDP 伺服器
gcc -o udp_server udp_server.c -Wall -O2

# UDP 客戶端
gcc -o udp_client udp_client.c -Wall -O2
```

### 執行

```bash
# 終端機 1：啟動伺服器
./tcp_server

# 終端機 2：啟動客戶端
./tcp_client
```

---

## 最佳實踐建議

### 1. Socket 選項設定

| 場景 | 必要設定 |
|------|----------|
| **TCP 伺服器** | SO_REUSEADDR |
| **低延遲應用** | TCP_NODELAY |
| **長連線** | SO_KEEPALIVE + 參數 |
| **高並發** | epoll + 非阻塞 + 邊緣觸發 |

### 2. 錯誤處理

```c
// EAGAIN/EWOULDBLOCK - 重試
if (errno == EAGAIN || errno == EWOULDBLOCK) {
    // 正常，稍後重試
}

// EINTR - 重新呼叫
if (errno == EINTR) {
    // 被信號中斷，重新呼叫
}

// EPIPE/ECONNRESET - 關閉連線
if (errno == EPIPE || errno == ECONNRESET) {
    close(sockfd);
}
```

### 3. I/O 模型選擇

| 連線數 | 推薦方案 |
|--------|----------|
| < 100 | select 或阻塞 I/O |
| 100-1000 | poll |
| > 1000 | epoll（Linux） |

### 4. 記憶體管理

```c
// 使用完後釋放
freeaddrinfo(res);

// 關閉 fd
close(sockfd);

// epoll 刪除監控
epoll_ctl(epfd, EPOLL_CTL_DEL, fd, NULL);
```

---

## 參考資源

### 線上手冊
```bash
man 2 socket
man 2 bind
man 7 tcp
man 7 udp
man 7 ip
man 7 epoll
```

### 重要標頭檔
```c
#include <sys/socket.h>    // socket, bind, listen, accept, connect
#include <netinet/in.h>    // sockaddr_in, INADDR_ANY
#include <arpa/inet.h>     // inet_pton, inet_ntop
#include <sys/epoll.h>     // epoll_create1, epoll_ctl, epoll_wait
#include <fcntl.h>         // fcntl, O_NONBLOCK
#include <unistd.h>        // close, read, write
```

---

## 結語

這份文件涵蓋了 Linux 網路程式設計的核心 API，包括：
- ✅ Socket 基礎函數（socket, bind, listen, accept, connect）
- ✅ TCP/UDP 專用函數
- ✅ I/O 多工機制（select, poll, epoll）
- ✅ Socket 選項設定（setsockopt）
- ✅ 資料收發函數（send, recv, sendto, recvfrom）
- ✅ 位址轉換函數
- ✅ 完整的範例程式

希望這份參考手冊對你的網路程式設計有所幫助！
