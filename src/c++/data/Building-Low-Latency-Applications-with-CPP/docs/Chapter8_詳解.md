# Chapter 8: 連線閘道與訂單伺服器詳解

## 章節概述

本章實作交易所的**連線閘道（Order Gateway）**與**訂單伺服器（Order Server）**，負責處理客戶端與交易所之間的通訊。

### 技術目標

1. **TCP 可靠傳輸**：使用 TCP 保證訂單請求與回應的可靠送達
2. **序列號驗證**：檢測網路異常與重複訊息
3. **FIFO 公平性**：確保請求按接收時間順序處理

### 核心元件

| 元件 | 職責 | 位置 |
|------|------|------|
| **OrderGateway** | 客戶端連線管理（Trading側） | trading/order_gw/ |
| **OrderServer** | 伺服器端連線管理（Exchange側） | exchange/order_server/ |
| **FIFOSequencer** | 請求排序器（保證公平性） | exchange/order_server/ |
| **MEClientRequest** | 客戶端請求消息格式 | exchange/order_server/ |
| **MEClientResponse** | 伺服器回應消息格式 | exchange/order_server/ |

---

## 1. 客戶端請求與回應消息格式

### 1.1 ClientRequestType 枚舉

`client_request.h:12-16`

```cpp
enum class ClientRequestType : uint8_t {
    INVALID = 0,
    NEW = 1,       // 新增訂單
    CANCEL = 2     // 取消訂單
};
```

#### 請求類型說明

| 類型 | 用途 | 觸發時機 |
|------|------|----------|
| **NEW** | 新增訂單 | 客戶端發送新訂單請求 |
| **CANCEL** | 取消訂單 | 客戶端取消現有訂單 |

### 1.2 MEClientRequest 結構

`client_request.h:36-61`

```cpp
#pragma pack(push, 1)  // ⚡ 緊湊封裝

struct MEClientRequest {
    ClientRequestType type_ = ClientRequestType::INVALID;
    ClientId client_id_ = ClientId_INVALID;
    TickerId ticker_id_ = TickerId_INVALID;
    OrderId order_id_ = OrderId_INVALID;
    Side side_ = Side::INVALID;
    Price price_ = Price_INVALID;
    Qty qty_ = Qty_INVALID;
};

#pragma pack(pop)
```

#### 設計原理

**緊湊封裝**
- 未封裝：~28 bytes（因對齊）
- 封裝後：20 bytes（實際欄位總和）
- 節省空間：~28.5%

**欄位說明**
- `type_`：請求類型（NEW/CANCEL）
- `client_id_`：客戶 ID
- `ticker_id_`：交易標的 ID
- `order_id_`：客戶端訂單 ID
- `side_`、`price_`、`qty_`：訂單屬性（NEW 請求需要）

### 1.3 OMClientRequest 結構

`client_request.h:63-77`

```cpp
struct OMClientRequest {
    size_t seq_num_ = 0;                  // ⚡ 序列號
    MEClientRequest me_client_request_;   // 實際請求內容
};
```

#### 序列號的作用

**1. 檢測網路異常**

```
預期序列號：1, 2, 3, 4, 5
收到序列號：1, 2, 2, 4, 5  ← 發現重複（seq=2）
收到序列號：1, 2, 4, 5     ← 發現丟失（seq=3）
```

**2. 防止重複處理**

```
客戶端重傳：seq=5 (第二次)
伺服器檢查：next_exp_seq_num_ = 6
結果：拒絕處理（已處理過 seq=5）
```

### 1.4 ClientResponseType 枚舉

`client_response.h:12-18`

```cpp
enum class ClientResponseType : uint8_t {
    INVALID = 0,
    ACCEPTED = 1,         // 訂單已接受
    CANCELED = 2,         // 訂單已取消
    FILLED = 3,           // 訂單已成交
    CANCEL_REJECTED = 4   // 取消請求被拒絕
};
```

#### 回應類型說明

| 類型 | 用途 | 觸發時機 |
|------|------|----------|
| **ACCEPTED** | 訂單已接受 | NEW 請求成功 |
| **CANCELED** | 訂單已取消 | CANCEL 請求成功 |
| **FILLED** | 訂單已成交 | 撮合引擎成交訂單 |
| **CANCEL_REJECTED** | 取消被拒絕 | 訂單不存在或已成交 |

### 1.5 MEClientResponse 結構

`client_response.h:44-72`

```cpp
#pragma pack(push, 1)

struct MEClientResponse {
    ClientResponseType type_ = ClientResponseType::INVALID;
    ClientId client_id_ = ClientId_INVALID;
    TickerId ticker_id_ = TickerId_INVALID;
    OrderId client_order_id_ = OrderId_INVALID;
    OrderId market_order_id_ = OrderId_INVALID;
    Side side_ = Side::INVALID;
    Price price_ = Price_INVALID;
    Qty exec_qty_ = Qty_INVALID;      // 已成交數量
    Qty leaves_qty_ = Qty_INVALID;    // 剩餘數量
};

#pragma pack(pop)
```

#### 欄位設計

**關鍵欄位**
- `exec_qty_`：本次成交數量
- `leaves_qty_`：剩餘未成交數量
- `market_order_id_`：交易所分配的訂單 ID（全局唯一）

**計算公式**
```
原始數量 = exec_qty_ + leaves_qty_

範例：
訂單數量 = 1000
第一次成交：exec_qty = 300, leaves_qty = 700
第二次成交：exec_qty = 700, leaves_qty = 0 (完全成交)
```

---

## 2. FIFOSequencer（FIFO 序列器）

### 2.1 設計原理

`fifo_sequencer.h:12-91`

FIFOSequencer 確保來自多個客戶端的請求按**接收時間順序**處理，保證公平性。

#### 為何需要 FIFO Sequencer？

**問題：多個 TCP 連接的處理順序不確定**

```
時間軸：
10:00:00.001  Client A 發送 Order #1
10:00:00.002  Client B 發送 Order #2
10:00:00.003  Client C 發送 Order #3

TCP Server 輪詢順序：
Socket C → Socket A → Socket B  ← 處理順序錯亂！
```

**解決方案：收集所有請求後按時間排序**

```
1. 收集階段：addClientRequest() 記錄 (rx_time, request)
2. 排序階段：sequenceAndPublish() 按 rx_time 排序
3. 發布階段：依序寫入 Lock-Free Queue
```

### 2.2 核心數據結構

`fifo_sequencer.h:77-89`

```cpp
struct RecvTimeClientRequest {
    Nanos recv_time_ = 0;       // ⚡ 接收時間（奈秒）
    MEClientRequest request_;   // 客戶端請求

    auto operator<(const RecvTimeClientRequest& rhs) const {
        return (recv_time_ < rhs.recv_time_);  // 按接收時間排序
    }
};

std::array<RecvTimeClientRequest, ME_MAX_PENDING_REQUESTS> pending_client_requests_;
size_t pending_size_ = 0;
```

#### 設計決策

**固定大小陣列 vs 動態容器**

| 特性 | std::array | std::vector |
|------|-----------|-------------|
| 記憶體分配 | 編譯時（棧） | 執行時（堆） |
| 容量上限 | 固定（1024） | 動態增長 |
| 效能 | 更快（無 malloc） | 較慢（動態分配） |
| 適用場景 | 低延遲系統 | 一般應用 |

**容量限制**：ME_MAX_PENDING_REQUESTS = 1024

```cpp
if (pending_size_ >= pending_client_requests_.size()) {
    FATAL("Too many pending requests");  // ⚠️ 超過容量直接終止
}
```

### 2.3 核心流程

#### addClientRequest() - 收集請求

`fifo_sequencer.h:24-31`

```cpp
auto addClientRequest(Nanos rx_time, const MEClientRequest& request) {
    if (pending_size_ >= pending_client_requests_.size()) {
        FATAL("Too many pending requests");
    }

    pending_client_requests_.at(pending_size_++) =
        std::move(RecvTimeClientRequest{rx_time, request});
}
```

**執行流程**：
1. 檢查容量限制
2. 記錄 (接收時間, 請求) 到陣列
3. pending_size_ 遞增

#### sequenceAndPublish() - 排序與發布

`fifo_sequencer.h:33-58`

```cpp
auto sequenceAndPublish() {
    if (UNLIKELY(!pending_size_)) {
        return;  // 沒有待處理請求
    }

    // 1. 按接收時間排序
    std::sort(pending_client_requests_.begin(),
              pending_client_requests_.begin() + pending_size_);

    // 2. 依序寫入 Lock-Free Queue
    for (size_t i = 0; i < pending_size_; ++i) {
        const auto& client_request = pending_client_requests_.at(i);

        auto next_write = incoming_requests_->getNextToWriteTo();
        *next_write = std::move(client_request.request_);
        incoming_requests_->updateWriteIndex();
    }

    // 3. 重置計數器
    pending_size_ = 0;
}
```

**時間複雜度**：
- 排序：O(N log N)，N ≤ 1024
- 寫入：O(N)
- **總計**：O(N log N)

### 2.4 公平性保證範例

**場景：3 個客戶端同時發送訂單**

```
時間軸（奈秒）：
1000  Client A: NEW Order (price=100.5, qty=100)
1002  Client C: NEW Order (price=100.5, qty=50)
1001  Client B: NEW Order (price=100.5, qty=200)

收集階段：
pending_client_requests_[0] = {1000, ClientA's Order}
pending_client_requests_[1] = {1002, ClientC's Order}
pending_client_requests_[2] = {1001, ClientB's Order}

排序後：
pending_client_requests_[0] = {1000, ClientA's Order}  ← 先到
pending_client_requests_[1] = {1001, ClientB's Order}
pending_client_requests_[2] = {1002, ClientC's Order}  ← 後到

撮合順序：
1. ClientA's Order (price=100.5, qty=100)  ← 時間優先權 = 1
2. ClientB's Order (price=100.5, qty=200)  ← 時間優先權 = 2
3. ClientC's Order (price=100.5, qty=50)   ← 時間優先權 = 3
```

---

## 3. OrderServer（訂單伺服器）

### 3.1 架構設計

`order_server.h:15-163`

OrderServer 是交易所端的 TCP 伺服器，負責：
1. 接受客戶端連接
2. 接收客戶端請求（NEW/CANCEL）
3. 發送伺服器回應（ACCEPTED/FILLED/CANCELED）
4. 序列號驗證

#### 資料流向

```
Multiple Clients (OrderGateway)
      ↓ TCP Connections
┌─────────────────────────────────┐
│    OrderServer::run()           │
│  ┌───────────────────────────┐  │
│  │ tcp_server_.poll()        │  │  ← 接收新連接
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ tcp_server_.sendAndRecv() │  │  ← 觸發 recvCallback()
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ fifo_sequencer_.          │  │
│  │   addClientRequest()      │  │  ← 收集請求
│  └───────────────────────────┘  │
│  ┌───────────────────────────┐  │
│  │ fifo_sequencer_.          │  │
│  │   sequenceAndPublish()    │  │  ← 排序並發送到撮合引擎
│  └───────────────────────────┘  │
└─────────────────────────────────┘
      ↓ Lock-Free Queue
Matching Engine
```

### 3.2 核心數據成員

`order_server.h:137-161`

```cpp
private:
    // Lock-Free Queue 通訊通道
    ClientResponseLFQueue* outgoing_responses_ = nullptr;  // 撮合引擎 → Order Server

    // 序列號管理（每個客戶端獨立）
    std::array<size_t, ME_MAX_NUM_CLIENTS> cid_next_outgoing_seq_num_;  // 發送序列號
    std::array<size_t, ME_MAX_NUM_CLIENTS> cid_next_exp_seq_num_;       // 預期接收序列號

    // 客戶端連接管理
    std::array<Common::TCPSocket*, ME_MAX_NUM_CLIENTS> cid_tcp_socket_;  // ClientId → TCPSocket*

    // TCP 伺服器
    Common::TCPServer tcp_server_;

    // FIFO 序列器
    FIFOSequencer fifo_sequencer_;
```

#### 設計決策

**為何使用陣列而非 std::unordered_map？**

| 特性 | std::array | std::unordered_map |
|------|-----------|-------------------|
| 查詢複雜度 | O(1) 直接索引 | O(1) 平均，O(N) 最壞 |
| 記憶體佔用 | 固定（預先配置） | 動態增長 |
| Cache 友善性 | 優秀（連續記憶體） | 差（分散在 heap） |
| 適用場景 | ClientId 範圍已知 | ClientId 範圍未知 |

### 3.3 主事件迴圈

`order_server.h:29-62`

```cpp
auto run() noexcept {
    while (run_) {
        // 1. 輪詢 TCP 連接（接受新連接、接收數據）
        tcp_server_.poll();

        // 2. 發送與接收（觸發 recvCallback）
        tcp_server_.sendAndRecv();

        // 3. 處理撮合引擎的回應，發送給客戶端
        for (auto client_response = outgoing_responses_->getNextToRead();
             outgoing_responses_->size() && client_response;
             client_response = outgoing_responses_->getNextToRead()) {

            // 3a. 取得該客戶端的發送序列號
            auto& next_outgoing_seq_num = cid_next_outgoing_seq_num_[client_response->client_id_];

            // 3b. 驗證 TCP Socket 存在
            ASSERT(cid_tcp_socket_[client_response->client_id_] != nullptr,
                   "Dont have a TCPSocket for ClientId:" + std::to_string(client_response->client_id_));

            // 3c. 發送序列號 + 回應
            cid_tcp_socket_[client_response->client_id_]->send(&next_outgoing_seq_num, sizeof(next_outgoing_seq_num));
            cid_tcp_socket_[client_response->client_id_]->send(client_response, sizeof(MEClientResponse));

            outgoing_responses_->updateReadIndex();

            // 3d. 序列號遞增
            ++next_outgoing_seq_num;
        }
    }
}
```

#### 執行順序

```
┌────────────────────────────────────────┐
│ 1. tcp_server_.poll()                  │  ← 接受新連接
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│ 2. tcp_server_.sendAndRecv()           │  ← 接收客戶端請求
│    → 觸發 recvCallback()               │
│    → 呼叫 fifo_sequencer_              │
│       .addClientRequest()              │
└────────────────┬───────────────────────┘
                 ↓
┌────────────────────────────────────────┐
│ 3. 處理撮合引擎回應                     │
│    → 從 outgoing_responses_ 讀取       │
│    → 透過 TCP 發送給客戶端             │
└────────────────────────────────────────┘
```

### 3.4 接收回調函數

`order_server.h:65-117`

```cpp
auto recvCallback(TCPSocket* socket, Nanos rx_time) noexcept {
    if (socket->next_rcv_valid_index_ >= sizeof(OMClientRequest)) {
        size_t i = 0;

        // 處理接收緩衝區中的所有完整訊息
        for (; i + sizeof(OMClientRequest) <= socket->next_rcv_valid_index_;
             i += sizeof(OMClientRequest)) {

            auto request = reinterpret_cast<const OMClientRequest*>(socket->inbound_data_.data() + i);

            // 1. 首次連接：記錄 ClientId → TCPSocket 映射
            if (UNLIKELY(cid_tcp_socket_[request->me_client_request_.client_id_] == nullptr)) {
                cid_tcp_socket_[request->me_client_request_.client_id_] = socket;
            }

            // 2. 驗證 TCP Socket 一致性
            if (cid_tcp_socket_[request->me_client_request_.client_id_] != socket) {
                // ⚠️ 同一 ClientId 從不同連接發送請求（異常情況）
                logger_.log("Received ClientRequest from ClientId:% on different socket\n", request->me_client_request_.client_id_);
                continue;  // 拒絕處理
            }

            // 3. 序列號驗證
            auto& next_exp_seq_num = cid_next_exp_seq_num_[request->me_client_request_.client_id_];

            if (request->seq_num_ != next_exp_seq_num) {
                // ⚠️ 序列號錯誤（丟包或重複）
                logger_.log("Incorrect sequence number. Expected:% Received:%\n", next_exp_seq_num, request->seq_num_);
                continue;  // 拒絕處理
            }

            ++next_exp_seq_num;

            // 4. 加入 FIFO Sequencer
            fifo_sequencer_.addClientRequest(rx_time, request->me_client_request_);
        }

        // 5. 移除已處理的數據，保留未完整的訊息
        memcpy(socket->inbound_data_.data(), socket->inbound_data_.data() + i,
               socket->next_rcv_valid_index_ - i);
        socket->next_rcv_valid_index_ -= i;
    }
}
```

#### 序列號驗證範例

**正常情況**

```
Client發送：seq=1, seq=2, seq=3
Server預期：seq=1, seq=2, seq=3
結果：全部接受
```

**丟包情況**

```
Client發送：seq=1, seq=2, seq=3, seq=4
Server收到：seq=1, seq=2,      , seq=4  ← seq=3 丟失
Server預期：seq=1, seq=2, seq=3, seq=3, seq=3, ...
結果：seq=1,2 接受，seq=4 拒絕
```

**重複情況**

```
Client重傳：seq=1, seq=2, seq=2, seq=3
Server預期：seq=1, seq=2, seq=3, seq=3
結果：seq=1,2 接受，第二個 seq=2 拒絕
```

### 3.5 完成回調函數

`order_server.h:120-123`

```cpp
auto recvFinishedCallback() noexcept {
    fifo_sequencer_.sequenceAndPublish();
}
```

**觸發時機**：tcp_server_.sendAndRecv() 處理完所有連接後

**作用**：將本輪收集的所有請求排序並發送到撮合引擎

---

## 4. OrderGateway（訂單閘道）

### 4.1 架構設計

`order_gateway.h:14-81`

OrderGateway 是客戶端（Trading 側）的 TCP 客戶端，負責：
1. 連接到 OrderServer
2. 發送客戶端請求（NEW/CANCEL）
3. 接收伺服器回應（ACCEPTED/FILLED/CANCELED）

#### 資料流向

```
Trading Strategy
      ↓ Lock-Free Queue (outgoing_requests_)
┌─────────────────────────────────┐
│ OrderGateway::run()             │
│  ┌───────────────────────────┐  │
│  │ 從 outgoing_requests_     │  │
│  │ 讀取客戶端請求            │  │
│  └───────────────┬───────────┘  │
│                  ↓                │
│  ┌───────────────────────────┐  │
│  │ 透過 TCP 發送             │  │
│  │ (seq_num + request)       │  │
│  └───────────────┬───────────┘  │
│                  ↓                │
│  ┌───────────────────────────┐  │
│  │ tcp_socket_.sendAndRecv() │  │
│  │ → 觸發 recvCallback()     │  │
│  └───────────────┬───────────┘  │
│                  ↓                │
│  ┌───────────────────────────┐  │
│  │ 接收伺服器回應            │  │
│  │ 寫入 incoming_responses_  │  │
│  └───────────────────────────┘  │
└─────────────────────────────────┘
      ↓ Lock-Free Queue (incoming_responses_)
Trading Strategy
```

### 4.2 核心數據成員

`order_gateway.h:58-74`

```cpp
private:
    const ClientId client_id_;  // 此閘道的客戶端 ID

    // TCP 連接參數
    std::string ip_;
    const std::string iface_;
    const int port_ = 0;

    // Lock-Free Queue 通訊通道
    Exchange::ClientRequestLFQueue* outgoing_requests_ = nullptr;    // Strategy → Gateway
    Exchange::ClientResponseLFQueue* incoming_responses_ = nullptr;  // Gateway → Strategy

    // 序列號管理
    size_t next_outgoing_seq_num_ = 1;  // 發送序列號
    size_t next_exp_seq_num_ = 1;       // 預期接收序列號

    // TCP Socket
    Common::TCPSocket tcp_socket_;
```

### 4.3 啟動流程

`order_gateway.h:30-39`

```cpp
auto start() {
    run_ = true;

    // 1. 連接到 OrderServer
    ASSERT(tcp_socket_.connect(ip_, iface_, port_, false) >= 0,
           "Unable to connect to ip:" + ip_ + " port:" + std::to_string(port_));

    // 2. 創建專用執行緒
    ASSERT(Common::createAndStartThread(-1, "Trading/OrderGateway", [this]() {
        run();
    }) != nullptr, "Failed to start OrderGateway thread.");
}
```

---

## 5. TCP 協定設計

### 5.1 訊息格式

**客戶端請求格式（OrderGateway → OrderServer）**

```
┌──────────────┬────────────────────────┐
│ Sequence # │ MEClientRequest       │
│ (8 bytes)  │ (20 bytes)            │
└──────────────┴────────────────────────┘
總計：28 bytes/請求
```

**伺服器回應格式（OrderServer → OrderGateway）**

```
┌──────────────┬────────────────────────┐
│ Sequence # │ MEClientResponse      │
│ (8 bytes)  │ (32 bytes)            │
└──────────────┴────────────────────────┘
總計：40 bytes/回應
```

### 5.2 TCP vs UDP 的設計權衡

| 特性 | TCP | UDP |
|------|-----|-----|
| **可靠性** | 保證送達 | 可能丟包 |
| **順序性** | 保證順序 | 可能亂序 |
| **延遲** | 較高（三次握手、確認） | 極低（單向發送） |
| **適用場景** | 訂單請求/回應 | 市場數據廣播 |

**為何訂單使用 TCP？**

```
場景：客戶端發送 NEW Order
UDP：可能丟包 → 訂單遺失 → 客戶損失
TCP：保證送達 → 訂單必達 → 資金安全
```

---

## 6. 序列號驗證機制

### 6.1 雙向序列號

**發送序列號（next_outgoing_seq_num_）**

```cpp
// 發送請求/回應時
tcp_socket_.send(&next_outgoing_seq_num_, sizeof(next_outgoing_seq_num_));
tcp_socket_.send(&request, sizeof(MEClientRequest));
++next_outgoing_seq_num_;
```

**接收序列號（next_exp_seq_num_）**

```cpp
// 接收請求/回應時
if (received_seq_num != next_exp_seq_num_) {
    // 序列號錯誤，拒絕處理
    return;
}
++next_exp_seq_num_;
```

### 6.2 異常處理

**丟包檢測**

```
發送：seq=1, seq=2, seq=3, seq=4
接收：seq=1, seq=2,      , seq=4
檢測：next_exp_seq_num_ = 3, received = 4
動作：拒絕 seq=4，等待 seq=3 重傳
```

**重複檢測**

```
發送：seq=1, seq=2, seq=2 (重傳)
接收：seq=1, seq=2, seq=2
檢測：next_exp_seq_num_ = 3, received = 2
動作：拒絕第二個 seq=2
```

---

## 7. 時間複雜度與效能分析

### 7.1 FIFOSequencer 時間複雜度

| 操作 | 時間複雜度 | 說明 |
|------|-----------|------|
| `addClientRequest()` | O(1) | 陣列索引存取 |
| `sequenceAndPublish()` | O(N log N) | std::sort 排序 |

### 7.2 OrderServer 時間複雜度

| 操作 | 時間複雜度 | 說明 |
|------|-----------|------|
| 序列號驗證 | O(1) | 陣列索引存取 |
| 發送回應 | O(M) | M = 回應數量 |
| TCP 接收 | O(K) | K = 連接數量 |

### 7.3 延遲分析

**訂單請求延遲（OrderGateway → OrderServer → Matching Engine）**

```
┌─────────────────────────────────────────────────────┐
│ OrderGateway                                        │
│   Lock-Free Queue 寫入：~20ns                       │
│   TCP 發送：~2-10μs                                 │
└──────────────────┬──────────────────────────────────┘
                   ↓ 網路傳輸（區域網路：<100μs）
┌─────────────────────────────────────────────────────┐
│ OrderServer                                         │
│   TCP 接收：~2-10μs                                 │
│   序列號驗證：~10ns                                  │
│   FIFO Sequencer 收集：~20ns                         │
│   排序（1024請求）：~50μs                            │
│   Lock-Free Queue 寫入：~20ns                        │
└──────────────────┬──────────────────────────────────┘
                   ↓
          Matching Engine 處理
──────────────────────────────────────────────────────
總延遲：~150-200μs (同機房)
```

---

## 8. 常見問題與陷阱

### 8.1 FIFO Sequencer 容量溢位

**問題**：
```cpp
constexpr size_t ME_MAX_PENDING_REQUESTS = 1024;

if (pending_size_ >= 1024) {
    FATAL("Too many pending requests");  // ⚠️ 直接終止程序
}
```

**分析**：
- 假設處理週期 1ms
- 每秒最多處理：1024 × 1000 = 102萬筆請求
- 若超過此吞吐量，系統崩潰

**改進方向**：
- 動態調整容量
- 背壓機制（拒絕新請求而非崩潰）

### 8.2 TCP 粘包問題

**問題**：

```
發送：
Message 1: [seq=1][MEClientRequest]  28 bytes
Message 2: [seq=2][MEClientRequest]  28 bytes

TCP接收緩衝區：
[seq=1][MEClientRequest][seq=2][MEClientRequest]  56 bytes
         ↑                       ↑
    可能在任意位置分割！
```

**解決方案**：

```cpp
// 循環處理完整訊息
for (; i + sizeof(OMClientRequest) <= socket->next_rcv_valid_index_;
     i += sizeof(OMClientRequest)) {
    auto request = reinterpret_cast<const OMClientRequest*>(socket->inbound_data_.data() + i);
    // 處理請求...
}

// 保留未完整的訊息
memcpy(socket->inbound_data_.data(), socket->inbound_data_.data() + i,
       socket->next_rcv_valid_index_ - i);
socket->next_rcv_valid_index_ -= i;
```

### 8.3 序列號同步問題

**問題**：

```
客戶端重啟：
next_outgoing_seq_num_ = 1  ← 重置為 1

伺服器狀態：
cid_next_exp_seq_num_[client_id] = 100  ← 仍然是 100

結果：
客戶端發送 seq=1 → 伺服器拒絕（預期 seq=100）
```

**解決方案**：

1. **重置連接**：客戶端重啟時發送 RESET 訊息
2. **會話管理**：使用 Session ID 區分不同連接
3. **超時清理**：伺服器定期清理長時間無活動的連接

---

## 9. 實戰應用場景

### 9.1 客戶端最佳實踐

**OrderGateway 使用範例**

```cpp
class TradingClient {
    OrderGateway gateway_;
    ClientRequestLFQueue outgoing_requests_;
    ClientResponseLFQueue incoming_responses_;

    void sendNewOrder(TickerId ticker, Side side, Price price, Qty qty) {
        auto next_write = outgoing_requests_.getNextToWriteTo();
        next_write->type_ = ClientRequestType::NEW;
        next_write->client_id_ = client_id_;
        next_write->ticker_id_ = ticker;
        next_write->order_id_ = next_order_id_++;
        next_write->side_ = side;
        next_write->price_ = price;
        next_write->qty_ = qty;
        outgoing_requests_.updateWriteIndex();
    }

    void handleResponses() {
        for (auto response = incoming_responses_.getNextToRead();
             incoming_responses_.size() && response;
             response = incoming_responses_.getNextToRead()) {

            switch (response->type_) {
            case ClientResponseType::ACCEPTED:
                LOG_INFO("Order {} accepted", response->market_order_id_);
                break;
            case ClientResponseType::FILLED:
                LOG_INFO("Order {} filled: exec={} leaves={}",
                         response->market_order_id_, response->exec_qty_, response->leaves_qty_);
                break;
            case ClientResponseType::CANCELED:
                LOG_INFO("Order {} canceled", response->market_order_id_);
                break;
            }

            incoming_responses_.updateReadIndex();
        }
    }
};
```

### 9.2 效能監控

**關鍵指標**

```cpp
// OrderServer 監控
auto request_latency = getCurrentNanos() - rx_time;  // 請求處理延遲
auto pending_requests = fifo_sequencer_.pending_size_;  // 待處理請求數
auto rejected_requests = sequence_error_count_;  // 序列號錯誤次數

// OrderGateway 監控
auto response_latency = getCurrentNanos() - send_time;  // 回應延遲
auto tcp_buffer_usage = tcp_socket_.next_rcv_valid_index_;  // TCP 緩衝區使用量
```

---

## 技術名詞中英對照

| 中文 | 英文 | 說明 |
|------|------|------|
| 訂單伺服器 | Order Server | 交易所端的 TCP 伺服器 |
| 訂單閘道 | Order Gateway | 客戶端的 TCP 客戶端 |
| FIFO 序列器 | FIFO Sequencer | 確保請求按時間順序處理 |
| 序列號 | Sequence Number | 檢測丟包與重複的編號 |
| 公平性 | Fairness | 按接收時間順序處理 |
| 粘包 | Packet Concatenation | TCP 訊息邊界問題 |
| 背壓 | Backpressure | 處理不及時的壓力 |

---

## 總結

### 關鍵設計決策

1. **TCP 可靠傳輸**：訂單請求使用 TCP 保證可靠性
2. **雙向序列號**：檢測網路異常與重複訊息
3. **FIFO Sequencer**：確保多客戶端公平性
4. **固定大小陣列**：預先配置避免動態記憶體分配

### 效能特性

- **訂單請求延遲**：150-200 微秒（同機房）
- **FIFO 排序成本**：~50 微秒（1024 請求）
- **序列號驗證**：~10 奈秒（O(1) 陣列查詢）

### 擴展方向

- **會話管理**：支援客戶端重連與狀態恢復
- **流控機制**：背壓控制避免緩衝區溢位
- **多級優先權**：VIP 客戶優先處理
