# 高頻交易開發完整指南

## 目錄

1. [開發環境設置](#開發環境設置)
2. [編譯策略](#編譯策略)
3. [效能測量與優化](#效能測量與優化)
4. [系統層級優化](#系統層級優化)
5. [記憶體管理策略](#記憶體管理策略)
6. [網路程式設計](#網路程式設計)
7. [並行與無鎖程式設計](#並行與無鎖程式設計)
8. [除錯與問題排查](#除錯與問題排查)
9. [常見陷阱與最佳實踐](#常見陷阱與最佳實踐)
10. [生產環境部署](#生產環境部署)

---

## 開發環境設置

### 問題場景
- 交易主機只有內網，無法直接連網
- 需要通過 SCP 傳輸套件和編譯文件
- 需要測試不同版本編譯器和工具

### 推薦方案

#### 1. 本地 Docker 容器開發（最推薦）

在本地機器安裝與機房**完全相同版本**的 Linux：

```bash
# 拉取與機房相同的系統
docker pull ubuntu:24.04
# 或
docker pull centos:7

# 啟動開發容器
docker run -it --rm -v $(pwd):/workspace ubuntu:24.04 bash
```

**優點：**
- 環境一致性高，避免相容性問題
- 可以快速測試不同編譯器版本（GCC 9/10/11, Clang 等）
- 編譯好的 binary 可直接 scp 到機房使用
- 本地測試方便，減少往返機房次數

#### 2. Dockerfile 範例

```dockerfile
FROM ubuntu:24.04

RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    linux-tools-generic \
    valgrind \
    gdb \
    git \
    perf \
    strace \
    htop

# 設置與機房相同的編譯環境
ENV CC=gcc-11
ENV CXX=g++-11

WORKDIR /workspace
```

#### 3. 開發流程

```bash
# 階段 1: 本地 Docker 功能測試
docker run -it --rm -v $(pwd):/workspace ubuntu:24.04
./trader --test-mode

# 階段 2: 本地效能基準測試
perf stat ./trader --benchmark

# 階段 3: 機房環境測試（真實數據）
scp trader user@trading-host:/opt/trading/
ssh user@trading-host './trader --production'
```

---

## 編譯策略

### Static vs Dynamic Linking

#### 動態連結（推薦）

```bash
# 在本地 Docker 中使用與機房相同的環境
docker run -it ubuntu:24.04 bash

# 正常編譯（動態連結）
g++ -O3 -march=skylake your_code.cpp -o trader

# 檢查依賴
ldd trader
```

**前提條件：**
1. 相同的 Linux 發行版和版本
2. 相同的共享庫版本（glibc, libstdc++）

**檢查依賴輸出範例：**
```
linux-vdso.so.1
libstdc++.so.6 => /usr/lib/x86_64-linux-gnu/libstdc++.so.6
libm.so.6 => /lib/x86_64-linux-gnu/libm.so.6
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6
```

#### 靜態連結（備選）

```bash
# 完全靜態編譯
g++ -O3 -static -march=native your_code.cpp -o trader

# 部分靜態連結
g++ -O3 your_code.cpp -o trader \
    -Wl,-Bstatic -lboost_system \
    -Wl,-Bdynamic -lpthread
```

**靜態編譯的效能影響：**
- 效能差異通常 < 5%
- Binary 檔案較大
- 可移植性高

### 動態連結 vs 靜態連結比較

| 特性 | 動態連結 | 靜態連結 |
|------|---------|---------|
| **效能** | 略好（可使用系統優化的庫） | 略差但可接受 |
| **檔案大小** | 小（幾 MB） | 大（可能 10+ MB） |
| **可移植性** | 需環境一致 | 高 |
| **適合高頻交易** | ✅ 是 | 可接受 |

### 系統優化庫說明

系統安裝的共享庫（如 glibc）通常包含：
- **SIMD 指令優化**：SSE, AVX, AVX2, AVX-512
- **運行時 CPU 檢測**：自動選擇最佳實現

```c
// glibc 動態版本的 memcpy 示例
void *memcpy(void *dest, const void *src, size_t n) {
    // 運行時 CPU 檢測
    if (cpu_has_avx512()) return memcpy_avx512(dest, src, n);
    if (cpu_has_avx2())   return memcpy_avx2(dest, src, n);
    return memcpy_generic(dest, src, n);
}
```

### 針對封包處理的編譯選項

封包重組和位元計算適合 **Static linking**：

```bash
# 推薦的編譯選項
g++ -O3 \
    -march=native \        # 使用機房 CPU 的所有指令集
    -flto \                # Link Time Optimization
    -static \              # 靜態連結
    -ffast-math \          # 如果有浮點運算
    -funroll-loops \       # 展開循環
    -finline-functions \   # 激進內聯
    packet_parser.cpp -o parser
```

**為什麼 Static 適合封包處理：**
1. 位元運算不依賴系統庫優化
2. 減少函數調用開銷
3. 更好的 CPU Cache 利用

### 額外的編譯優化選項

```bash
# Profile-Guided Optimization (PGO)
# 步驟 1: 編譯帶 instrumentation 的版本
g++ -O3 -fprofile-generate your_code.cpp -o trader

# 步驟 2: 運行典型 workload 收集 profile
./trader --benchmark

# 步驟 3: 使用 profile 重新編譯
g++ -O3 -fprofile-use your_code.cpp -o trader

# Link Time Optimization
g++ -O3 -flto file1.cpp file2.cpp -o trader

# 激進優化（需謹慎測試）
g++ -O3 -Ofast -march=native -mtune=native \
    -ffast-math -funroll-loops -finline-functions \
    your_code.cpp -o trader
```

---

## 效能測量與優化

### 1. 延遲測量工具

#### RDTSC 指令測量 CPU cycles

```cpp
#include <x86intrin.h>

inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

// 測量封包處理延遲
uint64_t start = rdtsc();
process_packet(data);
uint64_t end = rdtsc();
uint64_t cycles = end - start;

// 轉換成納秒（假設 3GHz CPU）
double ns = cycles / 3.0;
```

#### clock_gettime（高精度）

```cpp
#include <time.h>

struct timespec start, end;
clock_gettime(CLOCK_MONOTONIC, &start);
process_packet(data);
clock_gettime(CLOCK_MONOTONIC, &end);

long ns = (end.tv_sec - start.tv_sec) * 1e9 + 
          (end.tv_nsec - start.tv_nsec);
```

#### 更準確的 RDTSCP

```cpp
// RDTSCP 包含 memory barrier，更準確
inline uint64_t rdtscp() {
    unsigned int lo, hi;
    __asm__ volatile("rdtscp" : "=a"(lo), "=d"(hi) :: "rcx");
    return ((uint64_t)hi << 32) | lo;
}

// 完整的測量範例
inline uint64_t measure_latency() {
    // Warm up
    __asm__ volatile("" ::: "memory");
    
    uint64_t start = rdtscp();
    process_critical_path();
    uint64_t end = rdtscp();
    
    return end - start;
}
```

### 2. Profiling 工具

#### perf（必學）

```bash
# CPU cycles 和 instructions
perf stat -e cycles,instructions,cache-references,cache-misses \
    ./trader

# 找出熱點函數
perf record -g ./trader
perf report

# 查看 CPU cache 行為
perf stat -e L1-dcache-loads,L1-dcache-load-misses \
    -e LLC-loads,LLC-load-misses ./trader

# 查看分支預測
perf stat -e branches,branch-misses ./trader

# 記錄特定 CPU 上的事件
perf record -C 2 -g ./trader

# 查看 context switches
perf stat -e context-switches,cpu-migrations ./trader
```

#### valgrind + cachegrind（Cache 分析）

```bash
valgrind --tool=cachegrind ./trader
cg_annotate cachegrind.out.xxx

# 查看特定函數的 cache 行為
cg_annotate cachegrind.out.xxx --auto=yes | grep function_name
```

#### Intel VTune（商業工具）

```bash
# Hotspot 分析
vtune -collect hotspots -result-dir vtune_results ./trader

# Microarchitecture 分析
vtune -collect uarch-exploration -result-dir vtune_results ./trader
```

### 3. 延遲分佈統計

```cpp
#include <vector>
#include <algorithm>
#include <cstdio>

class LatencyTracker {
    std::vector<uint64_t> latencies;
    uint64_t min_latency = UINT64_MAX;
    uint64_t max_latency = 0;
    uint64_t sum = 0;
    
public:
    void record(uint64_t ns) {
        latencies.push_back(ns);
        min_latency = std::min(min_latency, ns);
        max_latency = std::max(max_latency, ns);
        sum += ns;
    }
    
    void report() {
        std::sort(latencies.begin(), latencies.end());
        size_t n = latencies.size();
        
        printf("Count: %zu\n", n);
        printf("Min:   %lu ns\n", min_latency);
        printf("Mean:  %lu ns\n", sum / n);
        printf("P50:   %lu ns\n", latencies[n/2]);
        printf("P90:   %lu ns\n", latencies[n*90/100]);
        printf("P95:   %lu ns\n", latencies[n*95/100]);
        printf("P99:   %lu ns\n", latencies[n*99/100]);
        printf("P99.9: %lu ns\n", latencies[n*999/1000]);
        printf("Max:   %lu ns\n", max_latency);
    }
    
    // 找出異常值
    void report_outliers(uint64_t threshold) {
        printf("\nOutliers (> %lu ns):\n", threshold);
        for (size_t i = 0; i < latencies.size(); i++) {
            if (latencies[i] > threshold) {
                printf("  Sample %zu: %lu ns\n", i, latencies[i]);
            }
        }
    }
};
```

### 4. 建立效能基準

```cpp
// benchmark.cpp
#include <benchmark/benchmark.h>

static void BM_PacketParsing(benchmark::State& state) {
    uint8_t packet[1024] = {/* test data */};
    
    for (auto _ : state) {
        parse_packet(packet);
        benchmark::DoNotOptimize(packet);
        benchmark::ClobberMemory();
    }
    
    state.SetItemsProcessed(state.iterations());
}
BENCHMARK(BM_PacketParsing);

// 測試不同參數
static void BM_OrderBook_Insert(benchmark::State& state) {
    OrderBook book;
    int num_orders = state.range(0);
    
    for (auto _ : state) {
        for (int i = 0; i < num_orders; i++) {
            book.insert(Order{i, 100 + i, 1000});
        }
        benchmark::DoNotOptimize(book);
    }
}
BENCHMARK(BM_OrderBook_Insert)->Range(8, 8<<10);

BENCHMARK_MAIN();
```

編譯並運行：
```bash
g++ -O3 -lbenchmark -lpthread benchmark.cpp -o bench
./bench --benchmark_repetitions=10
./bench --benchmark_filter=PacketParsing
```

---

## 系統層級優化

### 1. CPU 隔離和親和性

#### 隔離 CPU core

```bash
# 編輯 /etc/default/grub
GRUB_CMDLINE_LINUX="isolcpus=2,3,4,5 nohz_full=2,3,4,5 rcu_nocbs=2,3,4,5"

# 更新 grub
sudo update-grub
sudo reboot

# 驗證隔離
cat /sys/devices/system/cpu/isolated
```

#### 程式碼綁定 CPU

```cpp
#include <sched.h>
#include <pthread.h>

void pin_to_core(int core_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
}

// 設置優先級
void set_realtime_priority() {
    struct sched_param param;
    param.sched_priority = 99;  // 最高優先級
    sched_setscheduler(0, SCHED_FIFO, &param);
}

int main() {
    pin_to_core(2);  // 綁定到隔離的 core 2
    set_realtime_priority();
    // ...
}
```

#### NUMA 感知

```bash
# 查看 NUMA 拓撲
numactl --hardware

# 在特定 NUMA node 運行
numactl --cpunodebind=0 --membind=0 ./trader

# 查看記憶體分配
numastat -p $(pidof trader)
```

```cpp
#include <numa.h>

void init_numa() {
    if (numa_available() < 0) {
        fprintf(stderr, "NUMA not available\n");
        return;
    }
    
    // 綁定到 NUMA node 0
    numa_run_on_node(0);
    numa_set_preferred(0);
    
    // 分配 NUMA-local 記憶體
    void* buffer = numa_alloc_onnode(SIZE, 0);
}
```

### 2. 記憶體優化

#### Huge Pages

```bash
# 啟用 Huge Pages
echo 1024 > /proc/sys/vm/nr_hugepages

# 檢查
cat /proc/meminfo | grep Huge

# 持久化設置
echo "vm.nr_hugepages = 1024" >> /etc/sysctl.conf
```

```cpp
#include <sys/mman.h>

// 使用 Huge Pages 分配記憶體
void* buffer = mmap(NULL, SIZE, PROT_READ | PROT_WRITE,
                    MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                    -1, 0);
if (buffer == MAP_FAILED) {
    perror("mmap hugepage failed");
}
```

#### 記憶體預分配和 lock

```cpp
#include <sys/mman.h>

int main() {
    // 鎖定記憶體，防止 swap
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        perror("mlockall failed");
    }
    
    // 預分配所有需要的記憶體
    std::vector<Packet> packet_pool;
    packet_pool.reserve(10000);
    
    // 預先觸碰所有頁面，避免運行時 page fault
    for (size_t i = 0; i < packet_pool.capacity(); i++) {
        packet_pool.emplace_back();
    }
    
    // 或者手動觸碰記憶體
    char* buffer = new char[BUFFER_SIZE];
    for (size_t i = 0; i < BUFFER_SIZE; i += 4096) {
        buffer[i] = 0;  // 觸發 page fault
    }
}
```

### 3. 網路優化

#### Kernel 網路調優

```bash
# 增加 ring buffer
ethtool -G eth0 rx 4096 tx 4096

# 關閉中斷合併（降低延遲）
ethtool -C eth0 rx-usecs 0 tx-usecs 0

# 啟用 RSS (Receive Side Scaling)
ethtool -L eth0 combined 4

# 綁定網卡中斷到特定 CPU
echo 2 > /proc/irq/YOUR_IRQ/smp_affinity_list

# 查看網卡統計
ethtool -S eth0

# TCP 調優
cat >> /etc/sysctl.conf <<EOF
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 67108864
net.ipv4.tcp_wmem = 4096 65536 67108864
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr
EOF

sysctl -p
```

#### Socket 優化

```cpp
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

// 設置 socket buffer size
int buffer_size = 8 * 1024 * 1024;
setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, 
           &buffer_size, sizeof(buffer_size));

// 設置 busy polling（減少延遲）
int busy_poll = 50;
setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL, 
           &busy_poll, sizeof(busy_poll));

// SO_TIMESTAMP 獲取精確時間戳
int enable = 1;
setsockopt(sockfd, SOL_SOCKET, SO_TIMESTAMPNS, 
           &enable, sizeof(enable));

// 設置 TCP_NODELAY（關閉 Nagle 算法）
setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, 
           &enable, sizeof(enable));

// 設置 SO_REUSEADDR
setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, 
           &enable, sizeof(enable));
```

### 4. 關閉不必要的服務

```bash
# 關閉 CPU 頻率調整
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor

# 關閉 Turbo Boost（保持穩定延遲）
echo 1 > /sys/devices/system/cpu/intel_pstate/no_turbo

# 關閉 NUMA balancing
echo 0 > /proc/sys/kernel/numa_balancing

# 關閉透明大頁面（可能造成抖動）
echo never > /sys/kernel/mm/transparent_hugepage/enabled

# 關閉 swap
swapoff -a

# 設置中斷親和性腳本
#!/bin/bash
for irq in $(grep eth0 /proc/interrupts | awk '{print $1}' | sed 's/://'); do
    echo 2 > /proc/irq/$irq/smp_affinity_list
done

# 關閉不必要的系統服務
systemctl disable bluetooth.service
systemctl disable cups.service
systemctl stop irqbalance
```

---

## 記憶體管理策略

### Stack vs Static vs Heap 比較

#### 效能排名

**速度：Stack > Static > Heap**

| 特性 | Stack | Static | Heap |
|------|-------|--------|------|
| **分配速度** | ⭐⭐⭐⭐⭐ (1-2ns) | ⭐⭐⭐⭐⭐ (0ns) | ⭐ (150ns) |
| **訪問速度** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **生命週期** | 函數內 | 程序全局 | 手動管理 |
| **大小限制** | ~8MB | 幾乎無限 | 幾乎無限 |
| **Cache 友好** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **靈活性** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **適合高頻** | ✅ 臨時變量 | ✅ 資源池 | ❌ 避免 |

#### 實測效能對比

```cpp
#include <x86intrin.h>
#include <stdio.h>

struct Order {
    uint64_t id;
    uint32_t price;
    uint32_t quantity;
};

// Static
static Order static_orders[10000];

// Heap
Order* heap_orders = new Order[10000];

void test_stack() {
    uint64_t total = 0;
    for (int i = 0; i < 10000; i++) {
        uint64_t start = __rdtsc();
        
        Order order;  // Stack
        order.price = i;
        
        uint64_t end = __rdtsc();
        total += (end - start);
    }
    printf("Stack:  %.2f cycles/op\n", total / 10000.0);
}

void test_static() {
    uint64_t total = 0;
    for (int i = 0; i < 10000; i++) {
        uint64_t start = __rdtsc();
        
        static_orders[i].price = i;
        
        uint64_t end = __rdtsc();
        total += (end - start);
    }
    printf("Static: %.2f cycles/op\n", total / 10000.0);
}

void test_heap() {
    uint64_t total = 0;
    for (int i = 0; i < 10000; i++) {
        uint64_t start = __rdtsc();
        
        Order* order = new Order();
        order->price = i;
        delete order;
        
        uint64_t end = __rdtsc();
        total += (end - start);
    }
    printf("Heap:   %.2f cycles/op\n", total / 10000.0);
}
```

**典型結果（3GHz CPU）：**
```
Stack:  3.2 cycles/op   (~1ns)    ← 最快
Static: 8.5 cycles/op   (~3ns)    ← 次快
Heap:   450 cycles/op   (~150ns)  ← 最慢

速度比：Stack : Static : Heap = 1 : 2.7 : 140
```

### Static 記憶體模式（推薦）

#### 1. Object Pool

```cpp
template<typename T, size_t N>
class StaticPool {
    alignas(64) T pool[N];
    uint32_t free_list[N];
    uint32_t free_count = N;
    
public:
    StaticPool() {
        for (uint32_t i = 0; i < N; i++) {
            free_list[i] = i;
        }
    }
    
    T* allocate() {
        if (free_count == 0) return nullptr;
        uint32_t idx = free_list[--free_count];
        return &pool[idx];
    }
    
    void deallocate(T* ptr) {
        uint32_t idx = ptr - pool;
        free_list[free_count++] = idx;
    }
    
    size_t available() const { return free_count; }
};

// 使用
static StaticPool<Order, 10000> order_pool;

Order* order = order_pool.allocate();  // ~5ns
if (order) {
    order->price = 12345;
    // ...
    order_pool.deallocate(order);  // ~3ns
}
```

#### 2. Ring Buffer（封包處理）

```cpp
template<typename T, size_t N>
class RingBuffer {
    static_assert((N & (N - 1)) == 0, "N must be power of 2");
    
    alignas(64) T buffer[N];
    alignas(64) uint32_t read_idx = 0;
    alignas(64) uint32_t write_idx = 0;
    
public:
    bool push(const T& item) {
        uint32_t next = (write_idx + 1) & (N - 1);  // 快速取模
        if (next == read_idx) return false;  // Full
        
        buffer[write_idx] = item;
        write_idx = next;
        return true;
    }
    
    bool pop(T& item) {
        if (read_idx == write_idx) return false;  // Empty
        
        item = buffer[read_idx];
        read_idx = (read_idx + 1) & (N - 1);
        return true;
    }
    
    size_t size() const {
        return (write_idx - read_idx) & (N - 1);
    }
};

// 使用
static RingBuffer<Packet, 4096> packet_buffer;
```

#### 3. Fixed-size Array（訂單簿）

```cpp
class OrderBook {
    static constexpr size_t MAX_LEVELS = 100;
    static constexpr size_t MAX_ORDERS = 10000;
    
    struct Level {
        uint32_t price;
        uint32_t quantity;
        uint16_t order_count;
    };
    
    alignas(64) Level bids[MAX_LEVELS];
    alignas(64) Level asks[MAX_LEVELS];
    alignas(64) Order orders[MAX_ORDERS];
    
    uint32_t bid_count = 0;
    uint32_t ask_count = 0;
    
public:
    void add_order(const Order& order) {
        uint32_t idx = order.id % MAX_ORDERS;
        orders[idx] = order;
        
        // 更新價格層級
        if (order.side == Side::BUY) {
            update_level(bids, bid_count, order);
        } else {
            update_level(asks, ask_count, order);
        }
    }
    
private:
    void update_level(Level* levels, uint32_t& count, const Order& order);
};

static OrderBook book;
```

### 記憶體布局優化

#### 1. Cache Line 對齊

```cpp
// ❌ 不好：可能跨 cache line
struct Order {
    uint32_t id;
    uint32_t price;
    // 總共 8 bytes
};

// ✅ 好：對齊到 64 bytes（一個 cache line）
struct alignas(64) Order {
    uint32_t id;
    uint32_t price;
    uint32_t quantity;
    uint32_t timestamp;
    char padding[48];
};

// 或者緊密排列多個小對象
struct Order {
    uint32_t id;
    uint32_t price;
} __attribute__((packed));

static_assert(sizeof(Order) == 8);
```

#### 2. 熱數據集中

```cpp
// ❌ 不好：冷熱數據混合
struct Order {
    uint64_t timestamp;     // 熱數據
    uint32_t price;         // 熱數據
    char symbol[16];        // 冷數據
    char client_id[32];     // 冷數據
};

// ✅ 好：分離熱數據
struct OrderHot {
    uint64_t timestamp;
    uint32_t price;
    uint32_t quantity;
    uint32_t order_id;
} __attribute__((packed));

struct OrderCold {
    char symbol[16];
    char client_id[32];
};

static OrderHot hot_data[10000];
static OrderCold cold_data[10000];
```

#### 3. 陣列的結構 (SoA) vs 結構的陣列 (AoS)

```cpp
// AoS (Array of Structures) - 預設方式
struct Order {
    uint32_t id;
    uint32_t price;
    uint32_t quantity;
};
Order orders[1000];

// SoA (Structure of Arrays) - SIMD 友好
struct Orders {
    uint32_t ids[1000];
    uint32_t prices[1000];
    uint32_t quantities[1000];
};

// SoA 適合批量處理
void process_orders(Orders& orders, size_t count) {
    for (size_t i = 0; i < count; i += 8) {
        // 使用 SIMD 一次處理 8 個價格
        __m256i prices = _mm256_loadu_si256((__m256i*)&orders.prices[i]);
        // ...
    }
}
```

### Thread-local Static（最佳組合）

```cpp
// 結合 Static 和 Stack 的優點
thread_local static Order order_buffer[1000];
thread_local static char message_buffer[65536];

void worker_thread() {
    // 每個線程有自己的 static buffer
    // - Static 的速度
    // - 無需鎖
    // - 生命週期貫穿線程
    
    for (int i = 0; i < 1000; i++) {
        order_buffer[i].price = get_price();
    }
}
```

### 混合策略（最佳實踐）

```cpp
class OrderProcessor {
    // Static: 長期存在的資源池
    static Order order_pool[10000];
    static uint32_t free_list[10000];
    static uint32_t free_count;
    
public:
    void process_packet(const uint8_t* data) {
        // Stack: 臨時解析結果
        OrderMessage msg;
        parse_message(data, &msg);
        
        // Static pool: 分配訂單對象
        Order* order = allocate_from_pool();
        order->price = msg.price;
        
        // Stack: 臨時計算
        uint32_t total_value = calculate_value(order);
        
        submit_order(order);
    }
    
private:
    Order* allocate_from_pool() {
        if (free_count == 0) return nullptr;
        return &order_pool[free_list[--free_count]];
    }
};
```

---

## 網路程式設計

### 1. 接收封包的方式

#### 標準 Socket (較慢)

```cpp
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

// 接收封包
char buffer[2048];
struct sockaddr_in src_addr;
socklen_t addrlen = sizeof(src_addr);

ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                     (struct sockaddr*)&src_addr, &addrlen);
```

#### 零拷貝 + mmap (較快)

```cpp
// 使用 packet socket + mmap
int sockfd = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));

// 設置 ring buffer
struct tpacket_req req = {
    .tp_block_size = 4096,
    .tp_block_nr = 64,
    .tp_frame_size = 2048,
    .tp_frame_nr = 128
};

setsockopt(sockfd, SOL_PACKET, PACKET_RX_RING, &req, sizeof(req));

// mmap ring buffer
void* ring = mmap(NULL, req.tp_block_size * req.tp_block_nr,
                  PROT_READ | PROT_WRITE, MAP_SHARED, sockfd, 0);

// 零拷貝讀取
struct tpacket_hdr* header = (struct tpacket_hdr*)ring;
while (header->tp_status & TP_STATUS_USER) {
    process_packet((uint8_t*)header + header->tp_mac);
    header->tp_status = TP_STATUS_KERNEL;  // 歸還給 kernel
    header = next_frame(header);
}
```

#### Kernel Bypass (最快)

```cpp
// 使用 DPDK 或 Solarflare OpenOnload
// 完全繞過 kernel，直接從網卡讀取

// DPDK 範例
struct rte_mbuf* pkts[BURST_SIZE];
uint16_t nb_rx = rte_eth_rx_burst(port_id, queue_id, pkts, BURST_SIZE);

for (uint16_t i = 0; i < nb_rx; i++) {
    process_packet(rte_pktmbuf_mtod(pkts[i], uint8_t*));
    rte_pktmbuf_free(pkts[i]);
}
```

### 2. 多播 (Multicast) 訂閱

```cpp
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);

// 加入多播組
struct ip_mreq mreq;
mreq.imr_multiaddr.s_addr = inet_addr("239.1.1.1");
mreq.imr_interface.s_addr = INADDR_ANY;

setsockopt(sockfd, IPPROTO_IP, IP_ADD_MEMBERSHIP, 
           &mreq, sizeof(mreq));

// 綁定到多播端口
struct sockaddr_in addr;
addr.sin_family = AF_INET;
addr.sin_port = htons(12345);
addr.sin_addr.s_addr = INADDR_ANY;
bind(sockfd, (struct sockaddr*)&addr, sizeof(addr));
```

### 3. 發送封包優化

```cpp
// 使用 sendmmsg 批量發送
struct mmsghdr msgs[BATCH_SIZE];
struct iovec iovecs[BATCH_SIZE];

for (int i = 0; i < BATCH_SIZE; i++) {
    iovecs[i].iov_base = packets[i];
    iovecs[i].iov_len = packet_sizes[i];
    
    msgs[i].msg_hdr.msg_iov = &iovecs[i];
    msgs[i].msg_hdr.msg_iovlen = 1;
}

int sent = sendmmsg(sockfd, msgs, BATCH_SIZE, 0);
```

### 4. 封包解析優化

```cpp
// 零拷貝封包解析
struct __attribute__((packed)) MarketDataHeader {
    uint16_t msg_type;
    uint16_t msg_len;
    uint32_t seq_num;
    uint64_t timestamp;
};

const MarketDataHeader* parse_header(const uint8_t* data) {
    // 直接轉型，不複製
    return reinterpret_cast<const MarketDataHeader*>(data);
}

// 使用 SIMD 加速校驗和計算
uint32_t checksum_simd(const uint8_t* data, size_t len) {
    __m256i sum = _mm256_setzero_si256();
    
    for (size_t i = 0; i < len; i += 32) {
        __m256i chunk = _mm256_loadu_si256((__m256i*)&data[i]);
        sum = _mm256_add_epi32(sum, chunk);
    }
    
    // 水平求和
    uint32_t result = 0;
    uint32_t* p = (uint32_t*)&sum;
    for (int i = 0; i < 8; i++) result += p[i];
    return result;
}
```

---

## 並行與無鎖程式設計

### 1. Atomic 操作

```cpp
#include <atomic>

// 無鎖計數器
std::atomic<uint64_t> seq_num{0};

uint64_t get_next_seq() {
    return seq_num.fetch_add(1, std::memory_order_relaxed);
}

// 無鎖 flag
std::atomic<bool> ready{false};

// Producer
data = prepare_data();
ready.store(true, std::memory_order_release);

// Consumer
while (!ready.load(std::memory_order_acquire)) {
    // spin
}
process(data);
```

### 2. Lock-free Queue (單生產者單消費者)

```cpp
template<typename T, size_t N>
class SPSCQueue {
    static_assert((N & (N - 1)) == 0, "N must be power of 2");
    
    alignas(64) std::atomic<uint32_t> write_idx{0};
    alignas(64) std::atomic<uint32_t> read_idx{0};
    alignas(64) T buffer[N];
    
public:
    bool push(const T& item) {
        uint32_t w = write_idx.load(std::memory_order_relaxed);
        uint32_t next_w = (w + 1) & (N - 1);
        
        if (next_w == read_idx.load(std::memory_order_acquire)) {
            return false;  // Full
        }
        
        buffer[w] = item;
        write_idx.store(next_w, std::memory_order_release);
        return true;
    }
    
    bool pop(T& item) {
        uint32_t r = read_idx.load(std::memory_order_relaxed);
        
        if (r == write_idx.load(std::memory_order_acquire)) {
            return false;  // Empty
        }
        
        item = buffer[r];
        read_idx.store((r + 1) & (N - 1), std::memory_order_release);
        return true;
    }
};
```

### 3. 無鎖的訂單簿更新

```cpp
struct PriceLevel {
    std::atomic<uint32_t> quantity{0};
    std::atomic<uint16_t> order_count{0};
};

class LockFreeOrderBook {
    static constexpr size_t MAX_LEVELS = 100;
    
    alignas(64) PriceLevel bids[MAX_LEVELS];
    alignas(64) PriceLevel asks[MAX_LEVELS];
    
public:
    void add_order(uint32_t price, uint32_t qty, bool is_bid) {
        PriceLevel& level = is_bid ? bids[price % MAX_LEVELS] 
                                   : asks[price % MAX_LEVELS];
        
        level.quantity.fetch_add(qty, std::memory_order_relaxed);
        level.order_count.fetch_add(1, std::memory_order_relaxed);
    }
    
    uint32_t get_best_bid() {
        for (int i = MAX_LEVELS - 1; i >= 0; i--) {
            uint32_t qty = bids[i].quantity.load(std::memory_order_relaxed);
            if (qty > 0) return i;
        }
        return 0;
    }
};
```

### 4. Memory Order 選擇指南

```cpp
// memory_order_relaxed: 最快，無同步保證
counter.fetch_add(1, std::memory_order_relaxed);

// memory_order_acquire/release: 用於生產者-消費者
// Producer
data = prepare();
ready.store(true, std::memory_order_release);

// Consumer  
while (!ready.load(std::memory_order_acquire));
process(data);

// memory_order_seq_cst: 最慢，全局順序一致性
flag.store(true, std::memory_order_seq_cst);
```

### 5. 避免 False Sharing

```cpp
// ❌ 不好：false sharing
struct Data {
    std::atomic<uint64_t> counter1;
    std::atomic<uint64_t> counter2;  // 可能在同一個 cache line
};

// ✅ 好：cache line 對齊
struct Data {
    alignas(64) std::atomic<uint64_t> counter1;
    alignas(64) std::atomic<uint64_t> counter2;
};
```

---

## 除錯與問題排查

### 1. 常見問題診斷

#### 高延遲問題

```bash
# 檢查 CPU 頻率是否被調降
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq

# 檢查是否有 context switch
perf stat -e context-switches ./trader

# 檢查 page fault
perf stat -e page-faults ./trader

# 檢查是否有 swap
vmstat 1

# 檢查網卡 drop
ethtool -S eth0 | grep drop
```

#### 記憶體問題

```bash
# 檢查記憶體洩漏
valgrind --leak-check=full ./trader

# 查看記憶體使用
pmap -x $(pidof trader)

# 檢查 huge pages
cat /proc/meminfo | grep Huge
```

#### CPU 使用問題

```bash
# 查看哪個函數最耗 CPU
perf top -g

# 查看 CPU cache miss
perf stat -e cache-misses,cache-references ./trader

# 查看分支預測失敗
perf stat -e branch-misses,branches ./trader
```

### 2. GDB 除錯技巧

```bash
# 啟動 GDB
gdb ./trader

# 設置斷點
break process_packet
break main.cpp:123

# 條件斷點
break process_packet if price > 10000

# 查看記憶體
x/16xb 0x12345678  # 以 16 進制查看 16 bytes

# 查看結構體
p order
p/x order.price  # 以 16 進制顯示

# 查看 backtrace
bt

# 附加到運行中的進程
gdb -p $(pidof trader)
```

### 3. 效能回歸檢測

```cpp
// regression_test.cpp
#include "trader.h"
#include <fstream>

int main() {
    // 載入基準數據
    std::ifstream baseline("baseline.json");
    Metrics baseline_metrics = load_metrics(baseline);
    
    // 運行測試
    Metrics current_metrics = run_benchmark();
    
    // 比較
    if (current_metrics.p99_latency > baseline_metrics.p99_latency * 1.05) {
        fprintf(stderr, "REGRESSION: P99 latency increased by %.2f%%\n",
                (current_metrics.p99_latency / baseline_metrics.p99_latency - 1) * 100);
        return 1;
    }
    
    printf("PASS: No performance regression detected\n");
    return 0;
}
```

### 4. 日誌策略

```cpp
// 延遲日誌到非關鍵路徑
class AsyncLogger {
    static constexpr size_t BUFFER_SIZE = 1024 * 1024;
    
    char buffer[BUFFER_SIZE];
    std::atomic<size_t> write_pos{0};
    
public:
    void log(const char* fmt, ...) {
        size_t pos = write_pos.fetch_add(256, std::memory_order_relaxed);
        if (pos + 256 > BUFFER_SIZE) return;  // Buffer full
        
        va_list args;
        va_start(args, fmt);
        vsnprintf(&buffer[pos], 256, fmt, args);
        va_end(args);
    }
    
    void flush() {
        size_t end = write_pos.load(std::memory_order_acquire);
        write(log_fd, buffer, end);
        write_pos.store(0, std::memory_order_release);
    }
};

// 使用
thread_local AsyncLogger logger;

void process_order(Order* order) {
    logger.log("Processing order %u at price %u\n", order->id, order->price);
    // ... critical path ...
}

// 定期 flush（在非關鍵路徑）
void housekeeping_thread() {
    while (running) {
        sleep(1);
        logger.flush();
    }
}
```

---

## 常見陷阱與最佳實踐

### 1. 避免的操作（在 hot path）

```cpp
// ❌ 避免
std::string msg = "Order: " + std::to_string(order_id);  // 動態分配
std::cout << msg << std::endl;  // I/O 操作
std::map<int, Order> orders;    // 查找慢
std::vector<Order> v;
v.push_back(order);  // 可能重新分配

// ✅ 推薦
char buf[256];
snprintf(buf, sizeof(buf), "Order: %d", order_id);  // 棧上分配
// 延遲到非關鍵路徑再做 logging
std::unordered_map<int, Order> orders;  // 或 flat_map
std::vector<Order> v;
v.reserve(10000);  // 預分配
v.push_back(order);  // 不會重新分配
```

### 2. 編譯時檢查

```cpp
// 確保結構體大小符合預期
static_assert(sizeof(OrderMessage) == 64, "Unexpected padding");
static_assert(alignof(OrderMessage) == 8, "Wrong alignment");

// 確保是 trivial type（可以 memcpy）
static_assert(std::is_trivially_copyable_v<OrderMessage>);
static_assert(std::is_standard_layout_v<OrderMessage>);

// 確保沒有虛函數
static_assert(!std::is_polymorphic_v<OrderMessage>);
```

### 3. 位元操作優化

```cpp
// 使用編譯器內建函數（intrinsics）
#include <x86intrin.h>

// 計算 leading zeros
int len = __builtin_clz(header);

// 計算 population count (bit 為 1 的數量)
int count = __builtin_popcount(flags);

// SIMD 處理多個封包
__m256i data = _mm256_loadu_si256((__m256i*)packet);
__m256i mask = _mm256_set1_epi32(0xFF);
__m256i result = _mm256_and_si256(data, mask);

// 快速取模（當除數是 2 的冪）
uint32_t index = hash & (SIZE - 1);  // 比 hash % SIZE 快

// 位元欄位
struct Flags {
    uint32_t is_buy : 1;
    uint32_t is_market : 1;
    uint32_t is_ioc : 1;
    uint32_t reserved : 29;
};
```

### 4. Zero-copy 封包處理

```cpp
// 避免複製，直接操作原始 buffer
const uint8_t* parse_packet(const uint8_t* buf) {
    // 直接讀取，不 memcpy
    uint32_t price = *(uint32_t*)(buf + PRICE_OFFSET);
    uint32_t qty = *(uint32_t*)(buf + QTY_OFFSET);
    
    // 或使用 unaligned load (更安全)
    uint32_t price;
    memcpy(&price, buf + PRICE_OFFSET, sizeof(price));
    
    return buf + packet_len;
}
```

### 5. 使用 likely/unlikely hints

```cpp
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

if (likely(is_trade_message(type))) {
    // 最常見的路徑
    process_trade(msg);
} else if (unlikely(is_error(type))) {
    // 很少發生
    handle_error(msg);
}
```

### 6. 監控抖動（Jitter）

```cpp
class JitterMonitor {
    uint64_t threshold_ns;
    std::vector<uint64_t> outliers;
    
public:
    JitterMonitor(uint64_t threshold) : threshold_ns(threshold) {}
    
    void record(uint64_t latency_ns, uint64_t timestamp) {
        if (latency_ns > threshold_ns) {
            outliers.push_back((timestamp << 32) | latency_ns);
            
            // 即時警告
            fprintf(stderr, "JITTER ALERT: %lu ns at %lu\n", 
                    latency_ns, timestamp);
        }
    }
    
    void report() {
        printf("Total outliers: %zu\n", outliers.size());
        for (auto entry : outliers) {
            uint64_t ts = entry >> 32;
            uint64_t lat = entry & 0xFFFFFFFF;
            printf("  %lu: %lu ns\n", ts, lat);
        }
    }
};
```

### 7. 預取 (Prefetching)

```cpp
// 手動預取資料到 cache
void process_orders(Order* orders, size_t count) {
    for (size_t i = 0; i < count; i++) {
        // 預取下一個 order
        if (i + 1 < count) {
            __builtin_prefetch(&orders[i + 1], 0, 3);
        }
        
        process_order(&orders[i]);
    }
}

// 預取等級
// 0 = 不提示, 1 = L1, 2 = L2, 3 = L3
__builtin_prefetch(ptr, 0, 3);  // read, L3
__builtin_prefetch(ptr, 1, 1);  // write, L1
```

---

## 生產環境部署

### 1. 部署前檢查清單

```bash
#!/bin/bash
# pre_deploy_check.sh

echo "=== Pre-deployment Checks ==="

# 檢查 binary 是否靜態編譯或依賴正確
echo "Checking binary dependencies..."
ldd ./trader

# 檢查檔案權限
echo "Checking permissions..."
ls -l ./trader

# 檢查系統設定
echo "Checking system settings..."
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
cat /sys/kernel/mm/transparent_hugepage/enabled

# 檢查網路設定
echo "Checking network settings..."
ethtool -i eth0
ethtool -g eth0

# 檢查記憶體
echo "Checking memory..."
cat /proc/meminfo | grep -E "Huge|Mem"

# 測試基本功能
echo "Running smoke test..."
./trader --test-mode

echo "=== All checks passed ==="
```

### 2. 啟動腳本

```bash
#!/bin/bash
# start_trader.sh

# 設置環境
export LD_LIBRARY_PATH=/opt/trading/lib
export TRADING_CONFIG=/opt/trading/config/prod.conf

# CPU 親和性
CORE_ID=2

# 啟動前檢查
if ! ./pre_deploy_check.sh; then
    echo "Pre-deployment checks failed"
    exit 1
fi

# 啟動交易系統
echo "Starting trader on core $CORE_ID..."
taskset -c $CORE_ID ./trader --production 2>&1 | \
    tee /var/log/trading/trader.log

# 或使用 systemd
# systemctl start trader.service
```

### 3. Systemd Service 配置

```ini
# /etc/systemd/system/trader.service
[Unit]
Description=High Frequency Trading System
After=network.target

[Service]
Type=simple
User=trading
Group=trading
WorkingDirectory=/opt/trading
Environment="LD_LIBRARY_PATH=/opt/trading/lib"
ExecStart=/opt/trading/bin/trader --production
Restart=on-failure
RestartSec=10

# 資源限制
LimitMEMLOCK=infinity
LimitNOFILE=1048576

# 實時優先級
CPUSchedulingPolicy=fifo
CPUSchedulingPriority=99

# CPU 親和性
CPUAffinity=2 3 4 5

[Install]
WantedBy=multi-user.target
```

### 4. 監控腳本

```bash
#!/bin/bash
# monitor.sh

while true; do
    PID=$(pidof trader)
    
    if [ -z "$PID" ]; then
        echo "[ERROR] Trader process not found!"
        # 發送告警
        continue
    fi
    
    # CPU 使用率
    CPU=$(ps -p $PID -o %cpu= | tr -d ' ')
    
    # 記憶體使用
    MEM=$(ps -p $PID -o rss= | awk '{print $1/1024}')
    
    # 網路統計
    RX_PACKETS=$(cat /sys/class/net/eth0/statistics/rx_packets)
    TX_PACKETS=$(cat /sys/class/net/eth0/statistics/tx_packets)
    
    echo "$(date): CPU=$CPU% MEM=${MEM}MB RX=$RX_PACKETS TX=$TX_PACKETS"
    
    sleep 5
done
```

### 5. 緊急停止腳本

```bash
#!/bin/bash
# emergency_stop.sh

echo "Initiating emergency stop..."

# 發送 graceful shutdown 信號
PID=$(pidof trader)
if [ ! -z "$PID" ]; then
    kill -TERM $PID
    
    # 等待 5 秒
    sleep 5
    
    # 如果還沒停止，強制終止
    if ps -p $PID > /dev/null; then
        echo "Forcefully killing process..."
        kill -9 $PID
    fi
fi

echo "Trader stopped"
```

### 6. 配置文件範例

```ini
# config/prod.conf
[network]
multicast_address = 239.1.1.1
multicast_port = 12345
interface = eth0

[trading]
max_order_size = 1000
max_orders_per_second = 10000
risk_limit = 1000000

[system]
cpu_core = 2
use_huge_pages = true
log_level = warning

[monitoring]
enable_metrics = true
metrics_interval_ms = 1000
alert_threshold_ns = 100000
```

### 7. 健康檢查

```cpp
// health_check.cpp
#include <stdio.h>
#include <stdlib.h>

int main() {
    // 檢查進程是否運行
    FILE* fp = popen("pidof trader", "r");
    char buf[32];
    if (fgets(buf, sizeof(buf), fp) == NULL) {
        printf("CRITICAL: Trader not running\n");
        return 2;
    }
    pclose(fp);
    
    // 檢查最近延遲
    fp = fopen("/var/log/trading/latency.log", "r");
    if (!fp) {
        printf("WARNING: Cannot read latency log\n");
        return 1;
    }
    
    // 解析最後一行
    char line[256];
    char* last_line = NULL;
    while (fgets(line, sizeof(line), fp)) {
        last_line = line;
    }
    
    if (last_line) {
        uint64_t latency_ns;
        sscanf(last_line, "%*s %lu", &latency_ns);
        
        if (latency_ns > 100000) {  // > 100us
            printf("WARNING: High latency detected: %lu ns\n", latency_ns);
            fclose(fp);
            return 1;
        }
    }
    
    fclose(fp);
    printf("OK: System healthy\n");
    return 0;
}
```

---

## 效能基準參考

### 典型延遲指標

```
操作類型                延遲
───────────────────────────────
L1 cache 訪問           ~1 ns
L2 cache 訪問           ~3 ns
L3 cache 訪問           ~10 ns
主記憶體訪問            ~100 ns
malloc/free            ~150 ns
Context switch         ~1-10 μs
System call            ~1-5 μs
網路往返 (同機房)       ~100 μs
網路往返 (跨機房)       ~1-10 ms
```

### 目標延遲等級

| 等級 | 延遲範圍 | 優化重點 |
|------|---------|---------|
| 亞微秒級 | < 1μs | 極致優化、kernel bypass、FPGA |
| 微秒級 | 1-10μs | 系統調優、static 記憶體、無鎖 |
| 毫秒級 | > 1ms | 基本優化即可 |

### 不同交易類型的延遲要求

| 交易類型 | P50 | P99 | P99.9 |
|---------|-----|-----|-------|
| 做市 | < 5μs | < 20μs | < 50μs |
| 套利 | < 10μs | < 50μs | < 100μs |
| 趨勢追蹤 | < 100μs | < 1ms | < 5ms |

---

## 回歸測試與持續整合

### 回歸測試腳本

```bash
#!/bin/bash
# regression_test.sh

set -e

# 編譯新版本
echo "Building new version..."
make clean && make

# 運行效能測試
echo "Running performance tests..."
./bench --benchmark_repetitions=10 > results_new.txt

# 比較結果
echo "Comparing with baseline..."
if [ -f results_baseline.txt ]; then
    python3 check_regression.py results_baseline.txt results_new.txt
else
    echo "No baseline found, creating new baseline..."
    cp results_new.txt results_baseline.txt
fi

# 運行單元測試
echo "Running unit tests..."
./unit_tests

# 運行整合測試
echo "Running integration tests..."
./integration_tests

echo "All tests passed!"
```

### 效能回歸檢查

```python
#!/usr/bin/env python3
# check_regression.py

import sys
import re

def parse_results(filename):
    metrics = {}
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'(\w+)\s+(\d+)\s+ns', line)
            if match:
                metrics[match.group(1)] = int(match.group(2))
    return metrics

def main():
    baseline = parse_results(sys.argv[1])
    current = parse_results(sys.argv[2])
    
    regression_found = False
    
    for key in baseline:
        if key not in current:
            print(f"WARNING: {key} missing from current results")
            continue
            
        baseline_val = baseline[key]
        current_val = current[key]
        change = (current_val - baseline_val) / baseline_val * 100
        
        if change > 5:  # 5% regression threshold
            print(f"REGRESSION: {key} increased by {change:.1f}%")
            print(f"  Baseline: {baseline_val} ns")
            print(f"  Current:  {current_val} ns")
            regression_found = True
        elif change < -5:
            print(f"IMPROVEMENT: {key} decreased by {-change:.1f}%")
            print(f"  Baseline: {baseline_val} ns")
            print(f"  Current:  {current_val} ns")
    
    if regression_found:
        sys.exit(1)
    else:
        print("No performance regressions detected")
        sys.exit(0)

if __name__ == '__main__':
    main()
```

---

## 文檔和版本控制

### Git Commit 最佳實踐

```bash
# 記錄每次優化的效果
git commit -m "Optimize packet parsing using SIMD

Baseline: P99 = 850ns, P99.9 = 1200ns
After:    P99 = 720ns, P99.9 = 980ns
Improvement: P99 -15.3%, P99.9 -18.3%

Changes:
- Use AVX2 for checksum validation
- Unroll parsing loop (4x)
- Align packet buffer to 64 bytes
- Remove unnecessary branches

Tested with:
- 1M packets benchmark
- perf showed 30% reduction in L1 cache misses
- No functional regressions
"
```

### 變更日誌範例

```markdown
# Changelog

## [2.1.0] - 2024-12-05

### Added
- SIMD-accelerated packet checksum validation
- Lock-free order book implementation
- Automatic jitter monitoring

### Changed
- Switched from heap to static memory pool (-40% latency)
- Optimized network buffer alignment (+15% throughput)

### Performance
- P99 latency: 850ns → 720ns (-15.3%)
- P99.9 latency: 1200ns → 980ns (-18.3%)
- Throughput: 1.2M msg/s → 1.5M msg/s (+25%)

### Fixed
- Race condition in order cancellation
- Memory leak in error handling path
```

---

## 關鍵建議總結

### 開發環境
1. ✅ 使用 Docker 確保本地環境 = 機房環境
2. ✅ 優先使用動態連結（環境一致時）
3. ✅ 封包處理考慮靜態連結
4. ✅ 使用 PGO (Profile-Guided Optimization)

### 效能測量
1. ✅ 測量一切：沒有測量就沒有優化依據
2. ✅ 關注 P99/P99.9：不只是平均值
3. ✅ 使用 perf、RDTSC、valgrind
4. ✅ 建立基準並監控回歸

### 系統調優
1. ✅ 隔離 CPU core
2. ✅ 啟用 Huge Pages
3. ✅ 鎖定記憶體（mlockall）
4. ✅ 調整網路參數
5. ✅ 設置 NUMA 親和性

### 記憶體策略
1. ✅ 臨時變量用 Stack
2. ✅ 資源池用 Static
3. ✅ 避免使用 Heap（malloc/new）
4. ✅ Cache line 對齊（64 bytes）
5. ✅ 分離熱數據和冷數據

### 代碼優化
1. ✅ Hot path 避免動態分配
2. ✅ 使用 SIMD 指令
3. ✅ Zero-copy 設計
4. ✅ 編譯時檢查（static_assert）
5. ✅ 無鎖數據結構
6. ✅ 預取 (Prefetching)
7. ✅ Likely/Unlikely hints

### 網路優化
1. ✅ 考慮 kernel bypass (DPDK)
2. ✅ 使用零拷貝技術
3. ✅ 批量處理 (sendmmsg/recvmmsg)
4. ✅ 設置 busy polling

### 部署與監控
1. ✅ 完整的部署檢查清單
2. ✅ 自動化健康檢查
3. ✅ 監控延遲分佈
4. ✅ 告警機制
5. ✅ 緊急停止程序

---

## 參考資源

### 文檔
- Linux perf 文檔: https://perf.wiki.kernel.org/
- Intel 優化手冊: https://software.intel.com/content/www/us/en/develop/articles/intel-sdm.html
- Brendan Gregg 的效能分析: https://www.brendangregg.com/
- DPDK 文檔: https://doc.dpdk.org/

### 書籍
- "Systems Performance" by Brendan Gregg
- "The Art of Multiprocessor Programming" by Maurice Herlihy
- "Computer Architecture: A Quantitative Approach" by Hennessy & Patterson

### 工具
- perf: Linux 效能分析工具
- valgrind: 記憶體除錯和 profiling
- Intel VTune: 商業 profiling 工具
- Google Benchmark: C++ 微基準測試框架

### 社群
- Mechanical Sympathy: https://groups.google.com/g/mechanical-sympathy
- r/algotrading: https://reddit.com/r/algotrading
- Stack Overflow [high-frequency-trading] tag

---

## 附錄：快速參考卡

### 常用命令

```bash
# 編譯優化
g++ -O3 -march=native -flto your_code.cpp -o trader

# 效能測試
perf stat -e cycles,instructions,cache-misses ./trader
perf record -g ./trader
perf report

# 系統設置
echo performance > /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
echo 1024 > /proc/sys/vm/nr_hugepages

# 網路調優
ethtool -G eth0 rx 4096 tx 4096
ethtool -C eth0 rx-usecs 0 tx-usecs 0

# 監控
watch -n1 'cat /proc/$(pidof trader)/status | grep -E "VmRSS|VmSwap"'
```

### 常用 C++ 模式

```cpp
// 測量延遲
uint64_t start = __rdtsc();
critical_path();
uint64_t cycles = __rdtsc() - start;

// 無鎖 flag
std::atomic<bool> ready{false};
ready.store(true, std::memory_order_release);
while (!ready.load(std::memory_order_acquire));

// Object pool
static StaticPool<Order, 10000> pool;
Order* o = pool.allocate();
pool.deallocate(o);

// 對齊
struct alignas(64) Data { /* ... */ };

// Likely hint
if (likely(common_case)) { /* ... */ }
```

---

最後更新：2024-12-05
版本：2.0
