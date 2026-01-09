# 高頻/低延遲 Linux C/C++ 完整配置指南

> **目標**：硬體 + 系統 + 程式碼 = 極致低延遲  
> **適用**：HFT、DPDK、超低延遲交易系統

---

## 🎯 三層架構總覽

```
┌─────────────────────────────────────┐
│  1. 硬體層（Hardware）               │
│  - 高階網卡 + BIOS 設定              │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  2. 系統層（OS/Kernel）              │
│  - GRUB 參數 + Runtime 設定          │
└──────────────┬──────────────────────┘
               ↓
┌─────────────────────────────────────┐
│  3. 應用層（C/C++ Code）             │
│  - DPDK + Lock-free + 記憶體管理     │
└─────────────────────────────────────┘
```

---

## 1️⃣ 硬體層配置

### BIOS 設定（開機前）

```
┌─────────────────────────────┐
│ 必須關閉                     │
├─────────────────────────────┤
│ ✓ Hyper-Threading (SMT)     │
│ ✓ C-States (省電模式)        │
│ ✓ P-States (動態頻率)        │
│ ✓ Turbo Boost               │
│ ✓ NUMA Node Interleaving    │
└─────────────────────────────┘

┌─────────────────────────────┐
│ 必須開啟                     │
├─────────────────────────────┤
│ ✓ VT-d / IOMMU              │
│ ✓ Performance Mode          │
│ ✓ ACS (Access Control)      │
└─────────────────────────────┘
```

### 網卡要求

```
推薦型號：
- Intel X710 / XL710
- Mellanox ConnectX-5/6

必備功能：
✓ SR-IOV
✓ Flow Director / Flow Steering
✓ RSS (Receive Side Scaling)
✓ 32+ RX/TX queues
✓ DPDK PMD 支援
```

---

## 2️⃣ 系統層配置

### A. GRUB 啟動參數

編輯 `/etc/default/grub`：

```bash
GRUB_CMDLINE_LINUX="
  isolcpus=1-7
  nohz_full=1-7
  rcu_nocbs=1-7
  rcu_nocb_poll
  intel_pstate=disable
  intel_idle.max_cstate=0
  processor.max_cstate=0
  idle=poll
  nosoftlockup
  nmi_watchdog=0
  mce=off
  intel_iommu=on
  iommu=pt
  default_hugepagesz=1G
  hugepagesz=1G
  hugepages=8
  transparent_hugepage=never
"
```

更新並重啟：

```bash
sudo update-grub
sudo reboot
```

### B. 系統服務管理

```bash
# 關閉不必要服務
systemctl stop irqbalance
systemctl disable irqbalance
systemctl stop cpupower
systemctl mask systemd-journald.service

# 鎖定 CPU 頻率
cpupower frequency-set -g performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done
```

### C. IRQ 親和性設定

```bash
#!/bin/bash
# irq_binding.sh - 將所有 IRQ 綁定到 CPU 0

# 找出網卡的 IRQ
NIC_IRQS=$(grep "eth0" /proc/interrupts | awk '{print $1}' | tr -d ':')

# 綁定到 CPU 0 (0x01 = 二進位 0001)
for irq in $NIC_IRQS; do
    echo 1 > /proc/irq/$irq/smp_affinity
done

# 驗證
cat /proc/interrupts | grep eth0
```

### D. DPDK 環境準備

```bash
#!/bin/bash
# dpdk_setup.sh

# 1. 載入 VFIO 模組
modprobe vfio-pci
echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# 2. 查看網卡 PCI 位址
lspci | grep Ethernet
# 假設輸出：0000:03:00.0 Ethernet controller: Intel Corporation

# 3. 解綁原驅動
echo "0000:03:00.0" > /sys/bus/pci/drivers/i40e/unbind

# 4. 綁定到 vfio-pci（Intel X710 的 vendor:device ID）
echo "8086 1572" > /sys/bus/pci/drivers/vfio-pci/new_id
echo "0000:03:00.0" > /sys/bus/pci/drivers/vfio-pci/bind

# 5. 掛載 Hugepages
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 8 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# 6. 驗證
cat /proc/meminfo | grep Huge
```

---

## 3️⃣ 應用層 C/C++ 程式設計

### 專案架構

```
hft_project/
├── CMakeLists.txt
├── src/
│   ├── main.cpp
│   ├── dpdk_init.cpp
│   └── packet_handler.cpp
├── include/
│   ├── config.h
│   └── lockfree_queue.hpp
└── scripts/
    ├── setup.sh
    └── run.sh
```

### 主程式 (src/main.cpp)

```cpp
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_cycles.h>
#include <pthread.h>
#include <sched.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

// NUMA-aware memory pool
static struct rte_mempool *mbuf_pool = NULL;

// 核心配置
#define POLLING_CORE 2    // 隔離的 core
#define NUMA_NODE 0       // NIC 所在的 NUMA node

// 將執行緒綁定到特定 CPU
static inline void bind_to_cpu(int cpu) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    // 設定最高優先權
    struct sched_param param;
    param.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
}

// Port 初始化
static int port_init(uint16_t port) {
    struct rte_eth_conf port_conf = {};
    const uint16_t rx_rings = 1, tx_rings = 1;
    uint16_t nb_rxd = RX_RING_SIZE;
    uint16_t nb_txd = TX_RING_SIZE;
    int retval;
    
    // RSS 配置（多 queue 時使用）
    port_conf.rxmode.mq_mode = RTE_ETH_MQ_RX_RSS;
    port_conf.rx_adv_conf.rss_conf.rss_key = NULL;
    port_conf.rx_adv_conf.rss_conf.rss_hf = 
        RTE_ETH_RSS_TCP | RTE_ETH_RSS_UDP;
    
    // 配置 port
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0) return retval;
    
    // 調整 ring size
    retval = rte_eth_dev_adjust_nb_rx_tx_desc(port, &nb_rxd, &nb_txd);
    if (retval != 0) return retval;
    
    // 配置 RX queue（綁定到 NUMA node）
    retval = rte_eth_rx_queue_setup(port, 0, nb_rxd,
        rte_eth_dev_socket_id(port), NULL, mbuf_pool);
    if (retval < 0) return retval;
    
    // 配置 TX queue
    retval = rte_eth_tx_queue_setup(port, 0, nb_txd,
        rte_eth_dev_socket_id(port), NULL);
    if (retval < 0) return retval;
    
    // 啟動 port
    retval = rte_eth_dev_start(port);
    if (retval < 0) return retval;
    
    // 開啟 promiscuous mode（依需求）
    rte_eth_promiscuous_enable(port);
    
    return 0;
}

// 快速封包處理（inline 減少函數呼叫開銷）
static inline void process_packet(struct rte_mbuf *mbuf) {
    // 零拷貝：直接操作 mbuf 的資料指標
    uint8_t *pkt_data = rte_pktmbuf_mtod(mbuf, uint8_t*);
    
    // 假設處理 Ethernet header
    // struct rte_ether_hdr *eth_hdr = (struct rte_ether_hdr *)pkt_data;
    
    // *** 你的業務邏輯 ***
    // 例如：解析、計算、決策
    
    // 重點：避免記憶體複製、避免系統呼叫、避免鎖
}

// 主迴圈：Busy Polling
static int lcore_main(__rte_unused void *arg) {
    uint16_t port = 0;
    
    // 綁定到隔離的 CPU
    bind_to_cpu(POLLING_CORE);
    
    printf("Core %u doing packet processing.\n", rte_lcore_id());
    
    // 預熱 cache
    struct rte_mbuf *bufs[BURST_SIZE];
    for (int i = 0; i < 1000; i++) {
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        for (uint16_t i = 0; i < nb_rx; i++) {
            rte_pktmbuf_free(bufs[i]);
        }
    }
    
    // 主迴圈：永遠不睡眠
    while (1) {
        // Burst 接收（減少 overhead）
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        
        if (unlikely(nb_rx == 0)) {
            // 即使沒封包也不睡眠
            rte_pause(); // CPU pause 指令，減少功耗
            continue;
        }
        
        // 處理封包
        for (uint16_t i = 0; i < nb_rx; i++) {
            process_packet(bufs[i]);
            
            // 釋放 mbuf（或發送出去）
            rte_pktmbuf_free(bufs[i]);
        }
    }
    
    return 0;
}

int main(int argc, char *argv[]) {
    // 1. 初始化 DPDK EAL
    int ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
    }
    argc -= ret;
    argv += ret;
    
    // 2. 建立 Memory Pool（NUMA-aware）
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, NUMA_NODE);
    if (mbuf_pool == NULL) {
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");
    }
    
    // 3. 初始化 port 0
    if (port_init(0) != 0) {
        rte_exit(EXIT_FAILURE, "Cannot init port 0\n");
    }
    
    // 4. 啟動處理迴圈
    lcore_main(NULL);
    
    // 清理（通常不會執行到）
    rte_eal_cleanup();
    return 0;
}
```

### Lock-free Queue (include/lockfree_queue.hpp)

```cpp
#pragma once
#include <atomic>
#include <array>

// Single Producer Single Consumer Lock-free Queue
template<typename T, size_t SIZE>
class SPSCQueue {
private:
    struct alignas(64) Node {  // Cache line alignment
        T data;
        std::atomic<bool> ready{false};
    };
    
    std::array<Node, SIZE> buffer_;
    alignas(64) std::atomic<size_t> write_idx_{0};
    alignas(64) std::atomic<size_t> read_idx_{0};
    
public:
    // 生產者：寫入
    bool try_push(const T& item) {
        size_t current_write = write_idx_.load(std::memory_order_relaxed);
        size_t next_write = (current_write + 1) % SIZE;
        
        // 檢查是否已滿
        if (next_write == read_idx_.load(std::memory_order_acquire)) {
            return false;
        }
        
        buffer_[current_write].data = item;
        buffer_[current_write].ready.store(true, std::memory_order_release);
        write_idx_.store(next_write, std::memory_order_release);
        return true;
    }
    
    // 消費者：讀取
    bool try_pop(T& item) {
        size_t current_read = read_idx_.load(std::memory_order_relaxed);
        
        if (!buffer_[current_read].ready.load(std::memory_order_acquire)) {
            return false;
        }
        
        item = buffer_[current_read].data;
        buffer_[current_read].ready.store(false, std::memory_order_release);
        read_idx_.store((current_read + 1) % SIZE, std::memory_order_release);
        return true;
    }
};
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(hft_app)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -mtune=native")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# DPDK
find_package(PkgConfig REQUIRED)
pkg_check_modules(DPDK REQUIRED libdpdk)

include_directories(
    ${DPDK_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/include
)

add_executable(hft_app
    src/main.cpp
)

target_link_libraries(hft_app
    ${DPDK_LIBRARIES}
    pthread
    numa
)
```

### 啟動腳本 (scripts/run.sh)

```bash
#!/bin/bash

# 檢查 root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# 設定 CPU affinity mask（使用隔離的 core 2）
# -l 2: 使用 lcore 2
# -n 4: 4 個 memory channels
# --socket-mem: 每個 NUMA node 的記憶體 (MB)
./hft_app -l 2 -n 4 --socket-mem=1024 \
    --file-prefix=hft \
    -- \
    --portmask=0x1
```

---

## 4️⃣ 進階優化技巧

### A. 記憶體對齊與 Prefetch

```cpp
// 1. Cache line 對齊（避免 false sharing）
struct alignas(64) Order {
    uint64_t timestamp;
    uint32_t price;
    uint32_t quantity;
    // ... 其他欄位
};

// 2. Prefetch（提前載入到 cache）
static inline void process_batch(Order* orders, int count) {
    for (int i = 0; i < count; i++) {
        // 提前載入下一筆
        if (i + 1 < count) {
            __builtin_prefetch(&orders[i + 1], 0, 3);
        }
        
        // 處理當前這筆
        process_order(&orders[i]);
    }
}
```

### B. Branch Prediction 優化

```cpp
// 使用 likely/unlikely 提示編譯器
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

if (unlikely(error_occurred)) {
    handle_error();
}

if (likely(packet_valid)) {
    process_packet();
}
```

### C. 避免 False Sharing

```cpp
// 錯誤：兩個變數在同一 cache line，多核心寫入會互相影響
struct Bad {
    std::atomic<uint64_t> counter1;  // 8 bytes
    std::atomic<uint64_t> counter2;  // 8 bytes (same cache line!)
};

// 正確：padding 分離到不同 cache line
struct Good {
    alignas(64) std::atomic<uint64_t> counter1;
    alignas(64) std::atomic<uint64_t> counter2;
};
```

### D. 時間戳記取得

```cpp
// 使用 RDTSC（最快的時間戳）
static inline uint64_t rdtsc() {
    uint32_t lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

// 或使用 DPDK 的封裝
uint64_t now = rte_rdtsc();

// 轉換 cycles 到 nanoseconds
uint64_t hz = rte_get_tsc_hz();
uint64_t ns = (cycles * 1000000000ULL) / hz;
```

---

## 5️⃣ 測試與驗證

### Latency 測試程式

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

void measure_latency() {
    const int SAMPLES = 100000;
    std::vector<uint64_t> latencies;
    latencies.reserve(SAMPLES);
    
    for (int i = 0; i < SAMPLES; i++) {
        uint64_t start = rte_rdtsc();
        
        // *** 你的處理邏輯 ***
        process_packet();
        
        uint64_t end = rte_rdtsc();
        latencies.push_back(end - start);
    }
    
    // 排序計算百分位
    std::sort(latencies.begin(), latencies.end());
    
    uint64_t hz = rte_get_tsc_hz();
    auto cycles_to_ns = [hz](uint64_t cycles) {
        return (cycles * 1000000000ULL) / hz;
    };
    
    std::cout << "P50:    " << cycles_to_ns(latencies[SAMPLES * 50 / 100]) << " ns\n";
    std::cout << "P99:    " << cycles_to_ns(latencies[SAMPLES * 99 / 100]) << " ns\n";
    std::cout << "P99.9:  " << cycles_to_ns(latencies[SAMPLES * 999 / 1000]) << " ns\n";
    std::cout << "Max:    " << cycles_to_ns(latencies.back()) << " ns\n";
}
```

### 系統配置檢查腳本 (scripts/check.sh)

```bash
#!/bin/bash

echo "=== CPU Isolation Check ==="
cat /sys/devices/system/cpu/isolated

echo -e "\n=== CPU Governor ==="
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u

echo -e "\n=== C-States ==="
cat /sys/module/intel_idle/parameters/max_cstate

echo -e "\n=== IRQ Affinity ==="
grep eth0 /proc/interrupts

echo -e "\n=== Hugepages ==="
cat /proc/meminfo | grep Huge

echo -e "\n=== NUMA Topology ==="
numactl --hardware

echo -e "\n=== NIC Driver ==="
ethtool -i eth0

echo -e "\n=== NIC Queues ==="
ethtool -l eth0

echo -e "\n=== DPDK Binding ==="
dpdk-devbind.py --status
```

---

## 6️⃣ 完整部署 Checklist

### 硬體層

```
[✓] BIOS：關閉 Hyper-Threading
[✓] BIOS：關閉 C-States (C1E, C3, C6)
[✓] BIOS：關閉 P-States / Turbo Boost
[✓] BIOS：開啟 VT-d / IOMMU
[✓] BIOS：Performance Mode
[✓] 網卡：Intel X710 或 Mellanox ConnectX
[✓] 確認 NUMA 拓撲（NIC 在哪個 node）
```

### 系統層

```
[✓] GRUB：isolcpus=1-7
[✓] GRUB：nohz_full=1-7
[✓] GRUB：rcu_nocbs=1-7
[✓] GRUB：intel_pstate=disable
[✓] GRUB：intel_idle.max_cstate=0
[✓] GRUB：Hugepages 1GB
[✓] 關閉 irqbalance
[✓] IRQ 綁定到 CPU 0
[✓] CPU governor = performance
[✓] DPDK 網卡綁定 (vfio-pci)
[✓] 掛載 Hugepages
```

### 應用層

```
[✓] 使用 DPDK PMD
[✓] Busy polling (while(1) loop)
[✓] 綁定到隔離的 core (pthread_setaffinity_np)
[✓] SCHED_FIFO priority 99
[✓] Lock-free 資料結構
[✓] Cache line 對齊 (alignas(64))
[✓] 避免動態記憶體分配 (malloc/free)
[✓] 零拷貝設計 (直接操作 mbuf)
[✓] Prefetch + Branch hints
[✓] NUMA-aware memory allocation
```

---

## 7️⃣ 編譯與執行

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y dpdk dpdk-dev libnuma-dev \
    build-essential cmake pkg-config

# 驗證 DPDK 版本
dpdk-devbind.py --version
```

### 編譯專案

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 配置系統（需 root）

```bash
# 執行 DPDK 設定腳本
sudo ../scripts/setup.sh

# 檢查配置
sudo ../scripts/check.sh
```

### 執行應用程式

```bash
# 方式 1：直接執行
sudo ./hft_app -l 2 -n 4 --socket-mem=1024

# 方式 2：使用腳本
sudo ../scripts/run.sh
```

---

## 8️⃣ 預期效果

### 效能指標

```
正確配置後的預期效果：

P50 Latency:  < 500 ns
P99 Latency:  < 1 μs (微秒)
P99.9:        < 5 μs
Jitter:       < 10 μs

吞吐量:       數百萬 pps (packets per second)
CPU 使用率:    100% (busy polling)
```

### 驗證方法

```bash
# 1. 檢查 CPU 是否真的隔離
taskset -cp $(pgrep hft_app)
# 應該顯示：pid XXX's current affinity list: 2

# 2. 檢查是否真的在 busy polling
top -H -p $(pgrep hft_app)
# CPU 應該接近 100%

# 3. 檢查 IRQ 是否正確分配
watch -n 1 'cat /proc/interrupts | grep eth0'
# IRQ 應該只在 CPU 0 上增長

# 4. 檢查記憶體是否在正確的 NUMA node
numastat -p $(pgrep hft_app)
```

---

## 9️⃣ 常見問題排除

### Q1: DPDK 初始化失敗

```bash
# 檢查 hugepages
cat /proc/meminfo | grep Huge

# 重新配置
echo 8 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages
```

### Q2: 網卡綁定失敗

```bash
# 確認網卡支援 DPDK
dpdk-devbind.py --status

# 確認 VFIO 模組已載入
lsmod | grep vfio

# 手動載入
modprobe vfio-pci
```

### Q3: Latency 仍然很高

```bash
# 檢查 CPU isolation
cat /sys/devices/system/cpu/isolated

# 檢查 C-States
cat /sys/module/intel_idle/parameters/max_cstate
# 應該是 0

# 檢查 CPU governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
# 應該全部是 performance
```

### Q4: IRQ 仍打到 polling core

```bash
# 檢查 irqbalance 是否真的關閉
systemctl status irqbalance
# 應該是 inactive (dead)

# 手動設定 IRQ affinity
echo 1 > /proc/irq/XXX/smp_affinity
```

---

## 🔟 核心原則總結

### 五大支柱

```
1. CPU 隔離
   isolcpus + nohz_full + rcu_nocbs
   → 讓 CPU 變成專屬裸機

2. Busy Polling
   while(1) + 永遠不睡眠
   → 換 CPU 資源取得穩定 latency

3. 零拷貝
   直接操作 DPDK mbuf
   → 避免記憶體複製

4. Lock-free
   atomic + memory_order
   → 避免鎖競爭

5. NUMA 對齊
   NIC/core/memory 同 node
   → 避免跨 NUMA 存取
```

### 優化優先級

```
高優先級（必做）
├── CPU isolation 配置
├── IRQ 綁定
├── Hugepages
├── DPDK kernel bypass
└── NUMA 對齊

中優先級（重要）
├── Lock-free 資料結構
├── Cache line 對齊
├── 避免動態記憶體分配
└── Prefetch

低優先級（加分）
├── Branch hints
├── 編譯器優化 flags
└── 微調 DPDK 參數
```

---

## 📚 參考資源

### 官方文件

- [DPDK Documentation](https://doc.dpdk.org/)
- [Intel X710 Datasheet](https://www.intel.com/content/www/us/en/products/docs/network-io/ethernet/700-series-controllers.html)
- [Linux Kernel Real-Time](https://wiki.linuxfoundation.org/realtime/start)

### 進階閱讀

- [DPDK Performance Tuning](https://doc.dpdk.org/guides/linux_gsg/nic_perf_intel_platform.html)
- [Linux Low Latency Tuning](https://rigtorp.se/low-latency-guide/)
- [Lock-free Programming](https://preshing.com/20120612/an-introduction-to-lock-free-programming/)

---

## 📄 授權與貢獻

本文件提供參考使用，實際部署請根據具體硬體與需求調整。

**最後更新**: 2026-01-09

---

**記住**：高頻系統優化不是追求「快」，而是追求「穩定的快」。

> **"It's not about being fast, it's about being consistently fast."**
