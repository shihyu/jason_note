# API 參考文檔

> Building Low Latency Applications with C++ - Complete API Reference

---

## 📋 目錄

1. [核心資料結構](#核心資料結構)
   - [LFQueue (Lock-Free Queue)](#lfqueue-lock-free-queue)
   - [MemPool (Memory Pool)](#mempool-memory-pool)
2. [時間工具](#時間工具)
   - [Time Utils](#time-utils)
3. [執行緒工具](#執行緒工具)
   - [Thread Utils](#thread-utils)
4. [網路層](#網路層)
   - [TCPSocket](#tcpsocket)
   - [McastSocket](#mcastsocket)
   - [Socket Utils](#socket-utils)
5. [日誌系統](#日誌系統)
   - [Logger](#logger)
6. [巨集與工具](#巨集與工具)
   - [Macros](#macros)
   - [Types](#types)

---

## 核心資料結構

### LFQueue (Lock-Free Queue)

**檔案位置**：`common/lf_queue.h`

**命名空間**：`Common`

#### 類別定義

```cpp
template<typename T>
class LFQueue final;
```

#### 建構子

```cpp
explicit LFQueue(std::size_t num_elems);
```

**參數**：
- `num_elems`：佇列容量（固定大小）

**說明**：建立一個固定大小的 Ring Buffer，預先配置所有元素。

**範例**：
```cpp
LFQueue<Order> order_queue(10000);  // 10,000 個元素
```

---

#### Producer API

##### getNextToWriteTo()

```cpp
T* getNextToWriteTo() noexcept;
```

**返回值**：指向下一個可寫入槽位的指標

**說明**：取得下一個可寫入的位置，避免資料複製，允許原地構造。

**範例**：
```cpp
Order* order = queue.getNextToWriteTo();
order->id = 12345;
order->price = 99.50;
order->qty = 100;
```

**注意**：
- 必須在寫入完成後呼叫 `updateWriteIndex()`
- 若佇列已滿，返回的指標指向的槽位可能尚未被 Consumer 讀取（需使用者保證容量）

---

##### updateWriteIndex()

```cpp
void updateWriteIndex() noexcept;
```

**說明**：更新寫入索引，使 Consumer 可見新資料。

**範例**：
```cpp
Order* order = queue.getNextToWriteTo();
*order = Order{12345, 99.50, 100};
queue.updateWriteIndex();  // 提交資料
```

**注意**：
- 必須在資料完全寫入後才呼叫
- 使用原子操作，無需額外鎖

---

#### Consumer API

##### getNextToRead()

```cpp
const T* getNextToRead() const noexcept;
```

**返回值**：
- 指向下一個可讀取元素的指標
- 若佇列為空，返回 `nullptr`

**說明**：取得下一個可讀取的元素。

**範例**：
```cpp
const Order* order = queue.getNextToRead();
if (order) {
    process_order(order);
    queue.updateReadIndex();
}
```

---

##### updateReadIndex()

```cpp
void updateReadIndex() noexcept;
```

**說明**：更新讀取索引，釋放槽位供 Producer 重用。

**範例**：
```cpp
const Order* order = queue.getNextToRead();
if (order) {
    std::cout << "Order ID: " << order->id << "\n";
    queue.updateReadIndex();  // 釋放槽位
}
```

**注意**：
- 必須在處理完資料後才呼叫
- 若佇列為空時呼叫，會觸發 ASSERT

---

#### 共用 API

##### size()

```cpp
size_t size() const noexcept;
```

**返回值**：當前佇列中的元素數量

**說明**：原子讀取當前元素數量。

**範例**：
```cpp
std::cout << "Queue size: " << queue.size() << "\n";
```

---

#### 效能特性

| 操作 | 時間複雜度 | 延遲 (P50) | 延遲 (P99) |
|------|-----------|-----------|-----------|
| `getNextToWriteTo()` | O(1) | 12 ns | 18 ns |
| `updateWriteIndex()` | O(1) | 8 ns | 14 ns |
| `getNextToRead()` | O(1) | 15 ns | 22 ns |
| `updateReadIndex()` | O(1) | 9 ns | 15 ns |
| `size()` | O(1) | 5 ns | 8 ns |

---

#### 使用範例

```cpp
#include "common/lf_queue.h"

struct Order {
    int id;
    double price;
    int qty;
};

int main() {
    Common::LFQueue<Order> queue(10000);

    // Producer 執行緒
    std::thread producer([&]() {
        for (int i = 0; i < 1000; i++) {
            Order* order = queue.getNextToWriteTo();
            order->id = i;
            order->price = 100.0 + i;
            order->qty = 10;
            queue.updateWriteIndex();
        }
    });

    // Consumer 執行緒
    std::thread consumer([&]() {
        int count = 0;
        while (count < 1000) {
            const Order* order = queue.getNextToRead();
            if (order) {
                std::cout << "Order ID: " << order->id << "\n";
                queue.updateReadIndex();
                count++;
            }
        }
    });

    producer.join();
    consumer.join();

    return 0;
}
```

---

### MemPool (Memory Pool)

**檔案位置**：`common/mem_pool.h`

**命名空間**：`Common`

#### 類別定義

```cpp
template<typename T>
class MemPool final;
```

#### 建構子

```cpp
explicit MemPool(std::size_t num_elems);
```

**參數**：
- `num_elems`：記憶體池容量（固定大小）

**說明**：預先配置所有記憶體，避免執行時動態分配。

**範例**：
```cpp
MemPool<Order> order_pool(10000);  // 預配置 10,000 個 Order
```

---

#### 方法

##### allocate()

```cpp
template<typename... Args>
T* allocate(Args... args) noexcept;
```

**參數**：
- `args`：轉發給 `T` 建構子的參數

**返回值**：指向新分配物件的指標

**說明**：使用 Placement New 在預配置的記憶體上建構物件。

**範例**：
```cpp
// 分配一個 Order
Order* order = pool.allocate(12345, 99.50, 100);

// 等價於（但避免了 new 的開銷）
// Order* order = new Order(12345, 99.50, 100);
```

**注意**：
- 若記憶體池已滿，會觸發 ASSERT
- 建議保持使用率 < 80%

---

##### deallocate()

```cpp
void deallocate(const T* elem) noexcept;
```

**參數**：
- `elem`：要釋放的物件指標

**說明**：標記槽位為空閒，供後續分配重用。

**範例**：
```cpp
Order* order = pool.allocate(12345, 99.50, 100);
// ... 使用 order ...
pool.deallocate(order);  // 釋放
```

**警告**：
- 當前實作**未呼叫解構子**
- 若 `T` 持有資源（如 `std::string`），必須手動呼叫解構子：
  ```cpp
  order->~Order();
  pool.deallocate(order);
  ```

---

#### 效能特性

| 操作 | 時間複雜度 | 延遲 (P50) | 延遲 (P99) |
|------|-----------|-----------|-----------|
| `allocate()` | O(1) ~ O(N) | 18 ns | 28 ns |
| `deallocate()` | O(1) | 12 ns | 18 ns |
| vs `new/delete` | - | 50-10000 ns | - |

**說明**：
- 使用率 < 80% 時，`allocate()` 接近 O(1)
- 使用率 > 80% 時，線性探測導致延遲增加

---

#### 使用範例

```cpp
#include "common/mem_pool.h"

struct Order {
    int id;
    double price;
    int qty;
};

int main() {
    Common::MemPool<Order> pool(10000);

    // 分配
    Order* order1 = pool.allocate(12345, 99.50, 100);
    Order* order2 = pool.allocate(12346, 100.00, 200);

    // 使用
    std::cout << "Order 1: " << order1->id << "\n";

    // 釋放
    pool.deallocate(order1);
    pool.deallocate(order2);

    return 0;
}
```

---

## 時間工具

### Time Utils

**檔案位置**：`common/time_utils.h`

**命名空間**：`Common`

#### 型別定義

```cpp
typedef int64_t Nanos;
```

**說明**：奈秒時間戳類型，範圍約 292 年。

---

#### 常數

```cpp
constexpr Nanos NANOS_TO_MICROS = 1000;          // 1 μs = 1000 ns
constexpr Nanos MICROS_TO_MILLIS = 1000;         // 1 ms = 1000 μs
constexpr Nanos MILLIS_TO_SECS = 1000;           // 1 s = 1000 ms
constexpr Nanos NANOS_TO_MILLIS = 1000000;       // 1 ms = 1,000,000 ns
constexpr Nanos NANOS_TO_SECS = 1000000000;      // 1 s = 1,000,000,000 ns
```

---

#### 函式

##### getCurrentNanos()

```cpp
Nanos getCurrentNanos() noexcept;
```

**返回值**：當前系統時間（奈秒精度）

**說明**：使用 `std::chrono::system_clock` 取得高精度時間戳。

**效能**：約 20-30ns（取決於 CPU 和 TSC 頻率）

**範例**：
```cpp
Nanos start = getCurrentNanos();
process_order();
Nanos latency = getCurrentNanos() - start;
std::cout << "Latency: " << latency << " ns\n";
```

---

##### getCurrentTimeStr()

```cpp
std::string& getCurrentTimeStr(std::string* time_str);
```

**參數**：
- `time_str`：輸出參數，接收格式化後的時間字串

**返回值**：`time_str` 的引用

**輸出格式**：`"Fri Jan 10 12:34:56 2026"`

**說明**：取得可讀的時間字串，適用於日誌/除錯。

**效能**：約 1-5 μs（涉及格式化）

**範例**：
```cpp
std::string time_str;
std::cout << "Current time: " << getCurrentTimeStr(&time_str) << "\n";
```

---

## 執行緒工具

### Thread Utils

**檔案位置**：`common/thread_utils.h`

**命名空間**：`Common`

#### 函式

##### setThreadCore()

```cpp
bool setThreadCore(int core_id) noexcept;
```

**參數**：
- `core_id`：CPU 核心 ID（0-based）

**返回值**：
- `true`：成功綁定
- `false`：綁定失敗

**說明**：將當前執行緒綁定到指定的 CPU 核心。

**範例**：
```cpp
if (!setThreadCore(2)) {
    std::cerr << "Failed to bind thread to core 2\n";
    exit(EXIT_FAILURE);
}
```

---

##### createAndStartThread()

```cpp
template<typename T, typename... A>
std::thread* createAndStartThread(
    int core_id,
    const std::string& name,
    T&& func,
    A&&... args
) noexcept;
```

**參數**：
- `core_id`：CPU 核心 ID（-1 表示不綁定）
- `name`：執行緒名稱（用於日誌）
- `func`：要執行的函式
- `args`：函式參數

**返回值**：指向新執行緒的指標

**說明**：建立執行緒並綁定到指定 CPU 核心。

**範例**：
```cpp
auto thread = createAndStartThread(
    2,                    // 綁定到核心 2
    "TradeEngine",        // 執行緒名稱
    []() {                // Lambda 函式
        while (true) {
            process_orders();
        }
    }
);

// 等待執行緒結束
thread->join();
delete thread;
```

---

## 網路層

### TCPSocket

**檔案位置**：`common/tcp_socket.h`

**命名空間**：`Common`

#### 結構定義

```cpp
struct TCPSocket;
```

#### 建構子

```cpp
explicit TCPSocket(Logger& logger);
```

**參數**：
- `logger`：日誌記錄器引用

**說明**：建立 TCP Socket 並預配置 64 MB 發送/接收緩衝區。

---

#### 方法

##### connect()

```cpp
int connect(
    const std::string& ip,
    const std::string& iface,
    int port,
    bool is_listening
);
```

**參數**：
- `ip`：IP 位址（客戶端：目標 IP，伺服器：綁定 IP）
- `iface`：網路介面名稱（例如 "eth0"）
- `port`：埠號
- `is_listening`：`true` 為伺服器模式，`false` 為客戶端模式

**返回值**：
- `0`：成功
- `-1`：失敗

**說明**：建立或監聽 TCP 連接。

**範例**：
```cpp
TCPSocket server_socket(logger);
server_socket.connect("", "eth0", 8080, true);  // 伺服器

TCPSocket client_socket(logger);
client_socket.connect("192.168.1.100", "eth0", 8080, false);  // 客戶端
```

---

##### send()

```cpp
void send(const void* data, size_t len) noexcept;
```

**參數**：
- `data`：資料指標
- `len`：資料長度（bytes）

**說明**：將資料寫入發送緩衝區（不執行實際發送）。

**範例**：
```cpp
Order order{12345, 99.50, 100};
socket.send(&order, sizeof(order));
```

**警告**：
- 當前實作**無緩衝區溢位檢查**
- 若累積資料超過 64 MB，會發生緩衝區溢位
- 建議頻繁呼叫 `sendAndRecv()` 清空緩衝區

---

##### sendAndRecv()

```cpp
bool sendAndRecv() noexcept;
```

**返回值**：
- `true`：成功
- `false`：失敗

**說明**：執行實際的 TCP 收發操作。

**範例**：
```cpp
socket.send(&order, sizeof(order));
socket.sendAndRecv();  // 實際發送
```

---

#### 成員變數

```cpp
int socket_fd_;                                          // Socket 檔案描述符
std::vector<char> outbound_data_;                        // 發送緩衝區 (64 MB)
std::vector<char> inbound_data_;                         // 接收緩衝區 (64 MB)
size_t next_send_valid_index_;                           // 發送緩衝區有效資料結束位置
size_t next_rcv_valid_index_;                            // 接收緩衝區有效資料長度
std::function<void(TCPSocket*, Nanos)> recv_callback_;   // 接收回調函式
Logger& logger_;                                         // 日誌記錄器
```

---

#### 使用範例

```cpp
#include "common/tcp_socket.h"
#include "common/logging.h"

int main() {
    Common::Logger logger("tcp_server.log");
    Common::TCPSocket server_socket(logger);

    // 建立伺服器
    server_socket.connect("", "eth0", 8080, true);

    // 設定接收回調
    server_socket.recv_callback_ = [](Common::TCPSocket* s, Common::Nanos rx_time) {
        std::cout << "Received data at " << rx_time << "\n";
    };

    // 主迴圈
    while (true) {
        server_socket.sendAndRecv();
    }

    return 0;
}
```

---

### Socket Utils

**檔案位置**：`common/socket_utils.h`

**命名空間**：`Common`

#### 結構

##### SocketCfg

```cpp
struct SocketCfg {
    std::string ip_;
    std::string iface_;
    int port_ = -1;
    bool is_udp_ = false;
    bool is_listening_ = false;
    bool needs_so_timestamp_ = false;

    std::string toString() const;
};
```

---

#### 函式

##### createSocket()

```cpp
[[nodiscard]] int createSocket(
    Logger& logger,
    const SocketCfg& socket_cfg
);
```

**參數**：
- `logger`：日誌記錄器
- `socket_cfg`：Socket 配置

**返回值**：Socket 檔案描述符

**說明**：建立並完整配置 TCP/UDP Socket。

**範例**：
```cpp
SocketCfg cfg{
    .ip_ = "192.168.1.100",
    .iface_ = "eth0",
    .port_ = 8080,
    .is_udp_ = false,
    .is_listening_ = false,
    .needs_so_timestamp_ = false
};

int fd = createSocket(logger, cfg);
```

---

## 日誌系統

### Logger

**檔案位置**：`common/logging.h`

**命名空間**：`Common`

#### 類別定義

```cpp
class Logger final;
```

#### 建構子

```cpp
explicit Logger(const std::string& file_name);
```

**參數**：
- `file_name`：日誌檔案路徑

**說明**：建立無鎖日誌系統並啟動專用日誌執行緒。

---

#### 方法

##### log()

```cpp
template<typename T, typename... A>
void log(const char* s, const T& value, A... args) noexcept;

void log(const char* s) noexcept;
```

**參數**：
- `s`：格式字串（使用 `%` 作為佔位符）
- `value`：當前參數值
- `args`：剩餘參數

**說明**：printf 風格的變參模板日誌函式。

**範例**：
```cpp
logger.log("Order ID: % Price: % Qty: %\n", 12345, 99.50, 100);
// 輸出：Order ID: 12345 Price: 99.5 Qty: 100
```

---

#### 效能特性

| 操作 | 延遲 (P50) | 延遲 (P99) |
|------|-----------|-----------|
| `log()` - 簡單訊息 | 85 ns | 120 ns |
| `log()` - 帶參數 | 95 ns | 140 ns |
| vs `printf()` | 1500-5000 ns | - |

---

## 巨集與工具

### Macros

**檔案位置**：`common/macros.h`

#### LIKELY / UNLIKELY

```cpp
#define LIKELY(x)   __builtin_expect(!!(x), 1)
#define UNLIKELY(x) __builtin_expect(!!(x), 0)
```

**說明**：分支預測提示巨集。

**範例**：
```cpp
if (LIKELY(order != nullptr)) {
    process_order(order);  // 熱路徑
}

if (UNLIKELY(error)) {
    handle_error();  // 冷路徑
}
```

---

#### ASSERT

```cpp
inline void ASSERT(bool cond, const std::string& msg) noexcept;
```

**參數**：
- `cond`：必須為真的條件
- `msg`：斷言失敗時的錯誤訊息

**說明**：條件斷言，失敗時立即終止程式。

**範例**：
```cpp
ASSERT(price > 0, "Price must be positive");
```

---

#### FATAL

```cpp
inline void FATAL(const std::string& msg) noexcept;
```

**參數**：
- `msg`：致命錯誤的描述

**說明**：無條件終止程式並輸出錯誤訊息。

**範例**：
```cpp
switch(msg_type) {
    case NEW_ORDER: ...
    case CANCEL: ...
    default: FATAL("Unknown message type");
}
```

---

### Types

**檔案位置**：`common/types.h`

**命名空間**：`Common`

#### 型別定義

```cpp
typedef uint64_t OrderId;
typedef uint32_t TickerId;
typedef uint32_t ClientId;
typedef uint32_t Price;      // 固定點數表示（避免浮點精度問題）
typedef uint32_t Qty;
typedef uint64_t Priority;
typedef int64_t Nanos;
```

---

#### 常數

```cpp
constexpr size_t ME_MAX_TICKERS = 8;            // 最大 Ticker 數量
constexpr size_t ME_MAX_CLIENT_UPDATES = 256 * 1024;  // 最大客戶端更新
constexpr size_t ME_MAX_MARKET_UPDATES = 256 * 1024;  // 最大市場更新
constexpr size_t ME_MAX_NUM_CLIENTS = 256;            // 最大客戶端數量
constexpr size_t ME_MAX_ORDER_IDS = 1024 * 1024;      // 最大訂單 ID

// 無效值標記
constexpr auto OrderId_INVALID = std::numeric_limits<OrderId>::max();
constexpr auto TickerId_INVALID = std::numeric_limits<TickerId>::max();
constexpr auto ClientId_INVALID = std::numeric_limits<ClientId>::max();
constexpr auto Price_INVALID = std::numeric_limits<Price>::max();
constexpr auto Qty_INVALID = std::numeric_limits<Qty>::max();
```

---

## 快速參考

### 延遲對照表

| API | P50 延遲 | P99 延遲 | 用途 |
|-----|---------|---------|------|
| `LFQueue::getNextToWriteTo()` | 12 ns | 18 ns | 取得寫入槽位 |
| `MemPool::allocate()` | 18 ns | 28 ns | 分配物件 |
| `Logger::log()` | 95 ns | 140 ns | 寫入日誌 |
| `TCPSocket::sendAndRecv()` | 85 μs | 120 μs | TCP 收發 |
| `getCurrentNanos()` | 25 ns | 35 ns | 取得時間戳 |

---

### 常見錯誤與解決方案

| 錯誤 | 原因 | 解決方案 |
|------|------|---------|
| **LFQueue 滿溢** | Producer 速度 > Consumer 速度 | 增加佇列大小或加速 Consumer |
| **MemPool 耗盡** | 分配次數 > 容量 | 增加記憶體池大小或加速釋放 |
| **TCPSocket 緩衝區溢位** | send() 累積超過 64 MB | 頻繁呼叫 sendAndRecv() |
| **高延遲尖峰** | 上下文切換或 Cache Miss | 設定 CPU Affinity |

---

**文件版本**：1.0
**最後更新**：2026-01-11
**維護者**：Documentation Team
