## 1. 為什麼要測試效能？

高頻交易 (High Frequency Trading, HFT) 關心的是 **延遲 (latency)** 與 **抖動 (jitter)**，而不是單純的吞吐量。
效能測試主要分成兩層：

* **微基準 (micro-benchmark)**：測試單一語法或資料結構的延遲。
* **端對端 (E2E) 測試**：模擬「收到報價 → 下單 → 收到回報」的完整路徑。

---

## 2. 可以測到的 vs 測不到的

### ✅ 可以模擬的

* 程式語法、資料結構效能 (map vs unordered\_map, memcpy vs move)。
* 系統延遲：syscall 開銷、context switch。
* socket 傳輸延遲。
* tick-in → order-out 的端對端延遲分布。

### ❌ 無法完全模擬的

* 真實網路距離 (WAN latency)。
* 交易所 gateway 撮合/風控/流控行為。
* NIC/FPGA 硬體時間戳。
* 真實行情的 burst 特性 (1ms 內數百筆 tick)。

---

## 3. 測試方法

### (a) Micro-benchmark

在單機測不同語法開銷。

工具：

```bash
perf stat ./your_program
perf record ./your_program
perf report
```

C++ 測時間：

```cpp
#include <chrono>
#include <iostream>
int main() {
    auto t1 = std::chrono::high_resolution_clock::now();
    // 測試的程式碼
    auto t2 = std::chrono::high_resolution_clock::now();
    std::cout << "Elapsed: "
              << std::chrono::duration_cast<std::chrono::nanoseconds>(t2-t1).count()
              << " ns" << std::endl;
}
```

使用 CPU TSC：

```cpp
#include <x86intrin.h>
#include <iostream>
int main() {
    unsigned long long t1 = __rdtsc();
    // 測試的程式碼
    unsigned long long t2 = __rdtsc();
    std::cout << "Cycles: " << (t2 - t1) << std::endl;
}
```

---

### (b) 端對端 E2E 測試

Server 模擬交易所 → 發行情、收訂單。
Client 模擬策略 → 收行情、下單。

#### Server 範例 (C++)

```cpp
#include <arpa/inet.h>
#include <unistd.h>
#include <cstring>
#include <iostream>

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(9000);
    bind(sock, (sockaddr*)&addr, sizeof(addr));

    char buf[1024];
    sockaddr_in client{};
    socklen_t len = sizeof(client);

    while (true) {
        int n = recvfrom(sock, buf, sizeof(buf), 0, (sockaddr*)&client, &len);
        if (n > 0) {
            // 收到訂單後回覆 ACK
            sendto(sock, "ACK", 3, 0, (sockaddr*)&client, len);
        }
    }
}
```

#### Client 範例 (C++)

```cpp
#include <arpa/inet.h>
#include <unistd.h>
#include <chrono>
#include <iostream>

int main() {
    int sock = socket(AF_INET, SOCK_DGRAM, 0);
    sockaddr_in server{};
    server.sin_family = AF_INET;
    server.sin_port = htons(9000);
    inet_pton(AF_INET, "127.0.0.1", &server.sin_addr);

    char buf[1024];

    for (int i = 0; i < 10; i++) {
        auto t1 = std::chrono::high_resolution_clock::now();
        sendto(sock, "ORDER", 5, 0, (sockaddr*)&server, sizeof(server));
        recv(sock, buf, sizeof(buf), 0);
        auto t2 = std::chrono::high_resolution_clock::now();

        std::cout << "RTT ns: "
                  << std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count()
                  << std::endl;
    }
}
```

---

## 4. 測試重點指標

* **平均延遲 (mean latency)**
* **尾部延遲 (p99 / p99.9 latency)**
* **抖動 (jitter)**

---

## 5. 進階優化

* 使用 kernel bypass (DPDK, VMA, Onload)。
* NUMA 綁定：確保 NIC 與 CPU 在同一個 NUMA node。
* HugePages 減少 TLB miss。
* Busy polling 減少 context switch。
* Zero copy ring buffer 減少 memory copy。

---

## 6. Makefile 範例

```makefile
CXX = g++
CXXFLAGS = -O2 -Wall -std=c++17

all: server client

server: server.cpp
	$(CXX) $(CXXFLAGS) -o server server.cpp

client: client.cpp
	$(CXX) $(CXXFLAGS) -o client client.cpp

clean:
	rm -f server client
```
