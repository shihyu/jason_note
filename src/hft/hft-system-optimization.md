# 高頻交易系統：作業系統效能調優完整指南

## 目錄
- [1. 背景介紹](#1-背景介紹)
- [2. NUMA架構詳解](#2-numa架構詳解)
- [3. 核心隔離技術](#3-核心隔離技術)
- [4. 記憶體優化策略](#4-記憶體優化策略)
- [5. 快取優化技術](#5-快取優化技術)
- [6. 網路優化](#6-網路優化)
- [7. 監控與診斷](#7-監控與診斷)
- [8. 實戰案例](#8-實戰案例)

---

## 1. 背景介紹

### 1.1 高頻交易的挑戰

高頻量化交易（HFT）是一場發生在奈秒（Nanosecond, ns）尺度上的戰爭。效能指標對比：

| 系統類型 | 延遲要求 | 抖動容忍度 | 吞吐量 |
|---------|---------|-----------|--------|
| 傳統交易系統 | 100-1000ms | ±50ms | 1K-10K/秒 |
| 低延遲交易 | 1-10ms | ±5ms | 10K-100K/秒 |
| 高頻交易 | 1-100μs | ±1μs | 100K-1M/秒 |
| 超高頻交易 | <1μs | ±100ns | >1M/秒 |

### 1.2 延遲來源分析

```
總延遲 = 網路延遲 + 系統延遲 + 應用延遲

其中系統延遲包括：
├── CPU調度延遲 (1-100μs)
├── 記憶體存取延遲 (60-200ns)
├── 快取未命中 (1-100ns)
├── 中斷處理 (1-10μs)
├── 系統呼叫 (100-1000ns)
└── 上下文切換 (1-10μs)
```

### 1.3 核心技術棧

- **硬體層**：CPU親和性、NUMA、快取、網路卡
- **作業系統層**：核心調度、中斷處理、記憶體管理
- **應用層**：無鎖資料結構、記憶體池、零拷貝

---

## 2. NUMA架構詳解

### 2.1 NUMA基本概念

NUMA（Non-Uniform Memory Access）是現代多處理器伺服器的主流架構：

```
傳統SMP架構：
┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐
│CPU0 │ │CPU1 │ │CPU2 │ │CPU3 │
└──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘
   └───────┴───────┴───────┘
           │
    ┌──────▼──────┐
    │  記憶體控制器  │
    └──────┬──────┘
    ┌──────▼──────┐
    │    記憶體     │
    └─────────────┘

NUMA架構：
┌─────────Node 0─────────┐  ┌─────────Node 1─────────┐
│ ┌─────┐ ┌─────┐       │  │       ┌─────┐ ┌─────┐ │
│ │CPU0 │ │CPU1 │       │  │       │CPU2 │ │CPU3 │ │
│ └──┬──┘ └──┬──┘       │  │       └──┬──┘ └──┬──┘ │
│    └──┬────┘          │  │          └────┬──┘    │
│  ┌────▼────┐          │  │          ┌────▼────┐  │
│  │記憶體控制器│        │◄─┼─────────►│記憶體控制器│  │
│  └────┬────┘          │  │          └────┬────┘  │
│  ┌────▼────┐          │  │          ┌────▼────┐  │
│  │本地記憶體 │          │  │          │本地記憶體 │  │
│  └─────────┘          │  │          └─────────┘  │
└───────────────────────┘  └───────────────────────┘
        QPI/UPI互連
```

### 2.2 NUMA效能特性

#### 記憶體存取延遲對比

| 存取類型 | 延遲 | 相對成本 |
|---------|------|---------|
| L1 Cache | 0.5ns | 1x |
| L2 Cache | 7ns | 14x |
| L3 Cache | 20ns | 40x |
| 本地記憶體 | 60-80ns | 120-160x |
| 遠端記憶體 | 120-200ns | 240-400x |
| SSD | 150μs | 300,000x |
| HDD | 10ms | 20,000,000x |

#### NUMA距離矩陣範例

```bash
$ numactl --hardware
node distances:
node   0   1   2   3
  0:  10  21  31  21
  1:  21  10  21  31
  2:  31  21  10  21
  3:  21  31  21  10
```

### 2.3 NUMA優化策略

#### 策略1：記憶體本地化

```cpp
// 不良實踐：跨NUMA存取
void cross_numa_access() {
    // CPU在Node0，記憶體可能在Node1
    int* data = new int[SIZE];
    process_data(data);  // 每次存取都可能跨節點
}

// 最佳實踐：本地化存取
void local_numa_access() {
    // 綁定CPU和記憶體到同一節點
    numa_run_on_node(0);
    numa_set_preferred(0);
    
    // 分配本地記憶體
    int* data = (int*)numa_alloc_onnode(
        sizeof(int) * SIZE, 0
    );
    process_data(data);  // 全部本地存取
}
```

#### 策略2：資料分片

```cpp
class NUMAOptimizedQueue {
private:
    struct NodeData {
        alignas(64) std::atomic<size_t> head;
        alignas(64) std::atomic<size_t> tail;
        void* buffer;
    };
    
    NodeData* nodes[MAX_NUMA_NODES];
    
public:
    void init() {
        int num_nodes = numa_num_configured_nodes();
        for(int i = 0; i < num_nodes; i++) {
            // 每個NUMA節點一個隊列分片
            nodes[i] = (NodeData*)numa_alloc_onnode(
                sizeof(NodeData), i
            );
            nodes[i]->buffer = numa_alloc_onnode(
                BUFFER_SIZE, i
            );
        }
    }
};
```

---

## 3. 核心隔離技術

### 3.1 CPU親和性設定

#### 物理核心拓撲識別

```bash
# 查看CPU拓撲
$ lscpu --extended
CPU NODE SOCKET CORE L1d:L1i:L2:L3 ONLINE
0   0    0      0    0:0:0:0       yes
1   0    0      1    1:1:1:0       yes
2   0    0      2    2:2:2:0       yes
3   0    0      3    3:3:3:0       yes
4   0    0      0    0:0:0:0       yes  # 超執行緒
5   0    0      1    1:1:1:0       yes  # 超執行緒
```

#### CPU綁定實作

```cpp
#include <sched.h>
#include <pthread.h>

class ThreadManager {
public:
    // 綁定執行緒到指定CPU核心
    static bool bind_to_cpu(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        
        pthread_t thread = pthread_self();
        return pthread_setaffinity_np(
            thread, sizeof(cpuset), &cpuset
        ) == 0;
    }
    
    // 綁定到物理核心（跳過超執行緒）
    static bool bind_to_physical_core(int core_id) {
        return bind_to_cpu(core_id * 2);  // 假設偶數是物理核
    }
    
    // 設定執行緒優先級
    static bool set_realtime_priority(int priority) {
        struct sched_param param;
        param.sched_priority = priority;
        
        return pthread_setschedparam(
            pthread_self(),
            SCHED_FIFO,  // 實時調度策略
            &param
        ) == 0;
    }
};
```

### 3.2 中斷處理優化

#### 中斷親和性設定

```bash
#!/bin/bash
# 將網路中斷綁定到專用CPU

# 找出網路卡中斷號
IFACE="eth0"
IRQ_LIST=$(grep $IFACE /proc/interrupts | awk -F: '{print $1}')

# 設定中斷親和性（綁定到CPU 16-23）
for IRQ in $IRQ_LIST; do
    echo "ff0000" > /proc/irq/$IRQ/smp_affinity
done

# 停用 irqbalance 服務
systemctl stop irqbalance
systemctl disable irqbalance
```

### 3.3 核心參數調優

#### 完整的GRUB配置

```bash
# /etc/default/grub
GRUB_CMDLINE_LINUX="
    # CPU隔離
    isolcpus=8-15
    nohz_full=8-15
    rcu_nocbs=8-15
    
    # 中斷處理
    irqaffinity=0-7
    
    # 記憶體管理
    transparent_hugepage=never
    numa_balancing=disable
    
    # 電源管理
    intel_pstate=disable
    processor.max_cstate=1
    intel_idle.max_cstate=0
    
    # 其他優化
    nowatchdog
    nosoftlockup
    nmi_watchdog=0
"
```

---

## 4. 記憶體優化策略

### 4.1 記憶體鎖定

```cpp
class MemoryManager {
private:
    struct MemoryBlock {
        void* addr;
        size_t size;
        int numa_node;
        bool locked;
        bool huge_page;
    };
    
    std::vector<MemoryBlock> blocks;
    
public:
    void* allocate_locked_memory(
        size_t size, 
        int numa_node = -1,
        bool use_huge_page = true
    ) {
        void* ptr = nullptr;
        
        if (use_huge_page) {
            // 分配大頁記憶體
            ptr = mmap(nullptr, size,
                PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                -1, 0);
        } else {
            // 分配普通記憶體
            if (numa_node >= 0) {
                ptr = numa_alloc_onnode(size, numa_node);
            } else {
                ptr = numa_alloc_local(size);
            }
        }
        
        if (ptr && ptr != MAP_FAILED) {
            // 鎖定記憶體
            if (mlock(ptr, size) == 0) {
                // 預取記憶體
                memset(ptr, 0, size);
                
                // 記錄記憶體塊
                blocks.push_back({
                    ptr, size, numa_node, true, use_huge_page
                });
                
                return ptr;
            }
        }
        
        return nullptr;
    }
};
```

### 4.2 大頁記憶體配置

```bash
# 系統配置
echo 'vm.nr_hugepages=1024' >> /etc/sysctl.conf
echo 'vm.hugetlb_shm_group=1001' >> /etc/sysctl.conf

# 掛載hugetlbfs
mkdir -p /mnt/hugepages
mount -t hugetlbfs nodev /mnt/hugepages

# 檢查配置
grep Huge /proc/meminfo
```

### 4.3 記憶體池實作

```cpp
template<typename T>
class LockFreeMemoryPool {
private:
    struct Node {
        T data;
        std::atomic<Node*> next;
    };
    
    std::atomic<Node*> head;
    std::atomic<size_t> size;
    Node* memory_block;
    
public:
    LockFreeMemoryPool(size_t capacity, int numa_node = -1) {
        // 分配連續記憶體塊
        size_t total_size = sizeof(Node) * capacity;
        
        if (numa_node >= 0) {
            memory_block = (Node*)numa_alloc_onnode(
                total_size, numa_node
            );
        } else {
            memory_block = (Node*)aligned_alloc(
                64, total_size  // 64位元組對齊
            );
        }
        
        // 初始化自由列表
        for (size_t i = 0; i < capacity - 1; ++i) {
            memory_block[i].next = &memory_block[i + 1];
        }
        memory_block[capacity - 1].next = nullptr;
        
        head.store(memory_block);
        size.store(capacity);
    }
    
    T* allocate() {
        Node* old_head = head.load();
        while (old_head && 
               !head.compare_exchange_weak(
                   old_head, old_head->next.load())) {
            // CAS重試
        }
        
        if (old_head) {
            size.fetch_sub(1);
            return &old_head->data;
        }
        return nullptr;
    }
    
    void deallocate(T* ptr) {
        Node* node = reinterpret_cast<Node*>(
            reinterpret_cast<char*>(ptr) - offsetof(Node, data)
        );
        
        Node* old_head = head.load();
        do {
            node->next = old_head;
        } while (!head.compare_exchange_weak(old_head, node));
        
        size.fetch_add(1);
    }
};
```

---

## 5. 快取優化技術

### 5.1 快取行對齊

```cpp
// 避免偽共享
struct alignas(64) CacheLine {
    std::atomic<uint64_t> value;
    char padding[64 - sizeof(std::atomic<uint64_t>)];
};

// 優化的計數器陣列
class OptimizedCounters {
private:
    struct alignas(64) Counter {
        std::atomic<uint64_t> count{0};
    };
    
    Counter* counters;
    size_t num_counters;
    
public:
    OptimizedCounters(size_t n) : num_counters(n) {
        // 確保每個計數器獨占快取行
        counters = new (std::align_val_t(64)) Counter[n];
    }
    
    void increment(size_t idx) {
        counters[idx].count.fetch_add(1, std::memory_order_relaxed);
    }
};
```

### 5.2 預取優化

```cpp
class DataProcessor {
public:
    void process_array(int* data, size_t size) {
        const size_t prefetch_distance = 8;
        
        for (size_t i = 0; i < size; ++i) {
            // 預取未來的資料
            if (i + prefetch_distance < size) {
                __builtin_prefetch(
                    &data[i + prefetch_distance], 
                    0,  // 讀取
                    3   // 高時間局部性
                );
            }
            
            // 處理當前資料
            process_element(data[i]);
        }
    }
    
private:
    void process_element(int& elem) {
        // 實際處理邏輯
        elem = complex_calculation(elem);
    }
};
```

### 5.3 Intel CAT配置

```cpp
// 使用Intel RDT進行快取分配
class CacheAllocator {
public:
    bool setup_cache_allocation() {
        // 檢查CAT支援
        if (!check_cat_support()) {
            return false;
        }
        
        // 為關鍵任務分配專用快取
        // COS 1: 75% 快取給交易引擎
        set_cos_mask(1, 0xFFF0);
        
        // COS 2: 25% 快取給其他任務
        set_cos_mask(2, 0x000F);
        
        // 綁定程序到COS
        bind_task_to_cos(getpid(), 1);
        
        return true;
    }
    
private:
    bool check_cat_support() {
        // 檢查CPUID是否支援CAT
        unsigned int eax, ebx, ecx, edx;
        __cpuid_count(0x10, 0, eax, ebx, ecx, edx);
        return (ebx & 0x2) != 0;  // L3 CAT
    }
    
    void set_cos_mask(int cos, uint64_t mask) {
        // 設定COS遮罩（需要MSR權限）
        uint32_t msr = 0xC90 + cos;
        wrmsr(msr, mask);
    }
};
```

---

## 6. 網路優化

### 6.1 核心旁路技術

```cpp
// DPDK 初始化範例
class DPDKNetworkHandler {
private:
    struct rte_mempool* mbuf_pool;
    uint16_t port_id;
    
public:
    bool init(int argc, char** argv) {
        // 初始化EAL
        int ret = rte_eal_init(argc, argv);
        if (ret < 0) {
            return false;
        }
        
        // 建立記憶體池
        mbuf_pool = rte_pktmbuf_pool_create(
            "MBUF_POOL",
            8192,  // 緩衝區數量
            250,   // 快取大小
            0,
            RTE_MBUF_DEFAULT_BUF_SIZE,
            rte_socket_id()
        );
        
        // 配置網路埠
        struct rte_eth_conf port_conf = {};
        port_conf.rxmode.mq_mode = ETH_MQ_RX_RSS;
        
        ret = rte_eth_dev_configure(
            port_id, 1, 1, &port_conf
        );
        
        return ret == 0;
    }
    
    void receive_packets() {
        struct rte_mbuf* bufs[BURST_SIZE];
        
        while (true) {
            // 輪詢接收封包
            uint16_t nb_rx = rte_eth_rx_burst(
                port_id, 0, bufs, BURST_SIZE
            );
            
            for (uint16_t i = 0; i < nb_rx; i++) {
                process_packet(bufs[i]);
                rte_pktmbuf_free(bufs[i]);
            }
        }
    }
};
```

### 6.2 網路卡優化參數

```bash
#!/bin/bash
# 網路卡調優腳本

IFACE="eth0"

# 增加環形緩衝區
ethtool -G $IFACE rx 4096 tx 4096

# 啟用巨型幀
ip link set $IFACE mtu 9000

# 關閉中斷調節
ethtool -C $IFACE rx-usecs 0 tx-usecs 0

# 啟用RSS
ethtool -K $IFACE ntuple on
ethtool -K $IFACE rxhash on

# 設定RSS隊列數
ethtool -L $IFACE combined 8

# 關閉省電功能
ethtool -s $IFACE speed 10000 duplex full autoneg off
```

---

## 7. 監控與診斷

### 7.1 效能監控工具

#### 系統層面監控

```bash
# CPU監控
mpstat -P ALL 1

# 記憶體監控
numastat -c

# 中斷監控
watch -n 1 'cat /proc/interrupts | grep eth'

# 快取監控
perf stat -e cache-misses,cache-references ./app

# 延遲監控
cyclictest -m -p 99 -i 1000 -n
```

#### 應用層面監控

```cpp
class PerformanceMonitor {
private:
    struct Metrics {
        std::atomic<uint64_t> total_latency{0};
        std::atomic<uint64_t> max_latency{0};
        std::atomic<uint64_t> min_latency{UINT64_MAX};
        std::atomic<uint64_t> count{0};
        
        // 延遲直方圖
        std::atomic<uint64_t> histogram[100]{};
    };
    
    alignas(64) Metrics metrics;
    
public:
    void record_latency(uint64_t latency_ns) {
        metrics.total_latency.fetch_add(latency_ns);
        metrics.count.fetch_add(1);
        
        // 更新最大/最小值
        uint64_t prev_max = metrics.max_latency.load();
        while (latency_ns > prev_max && 
               !metrics.max_latency.compare_exchange_weak(
                   prev_max, latency_ns)) {}
        
        uint64_t prev_min = metrics.min_latency.load();
        while (latency_ns < prev_min && 
               !metrics.min_latency.compare_exchange_weak(
                   prev_min, latency_ns)) {}
        
        // 更新直方圖
        size_t bucket = std::min(
            latency_ns / 100, size_t(99)
        );
        metrics.histogram[bucket].fetch_add(1);
    }
    
    void print_statistics() {
        uint64_t count = metrics.count.load();
        if (count == 0) return;
        
        double avg = metrics.total_latency.load() / 
                    static_cast<double>(count);
        
        std::cout << "Latency Statistics:\n"
                  << "  Average: " << avg << " ns\n"
                  << "  Min: " << metrics.min_latency.load() << " ns\n"
                  << "  Max: " << metrics.max_latency.load() << " ns\n"
                  << "  Count: " << count << "\n";
        
        // 計算百分位數
        print_percentiles();
    }
};
```

### 7.2 問題診斷清單

| 問題 | 可能原因 | 診斷方法 | 解決方案 |
|-----|---------|---------|---------|
| 延遲尖峰 | CPU調度 | `trace-cmd` | CPU隔離 |
| 延遲不穩定 | 中斷干擾 | `/proc/interrupts` | 中斷親和性 |
| 記憶體慢 | NUMA跨節點 | `numastat` | NUMA綁定 |
| 快取未命中高 | 偽共享 | `perf c2c` | 資料對齊 |
| 網路延遲 | 核心協定棧 | `tcpdump` | DPDK/XDP |

---

## 8. 實戰案例

### 8.1 完整的HFT系統配置

```cpp
class HFTSystem {
private:
    // 配置參數
    struct Config {
        int trading_cpu = 8;      // 交易引擎CPU
        int market_data_cpu = 9;   // 市場資料CPU
        int network_cpu = 10;      // 網路處理CPU
        int numa_node = 0;         // NUMA節點
        size_t memory_size = 1024 * 1024 * 1024;  // 1GB
    } config;
    
    // 核心元件
    std::unique_ptr<MemoryManager> memory_manager;
    std::unique_ptr<NetworkHandler> network_handler;
    std::unique_ptr<TradingEngine> trading_engine;
    
public:
    bool initialize() {
        // 1. 系統層級設定
        if (!setup_system()) {
            return false;
        }
        
        // 2. 記憶體初始化
        memory_manager = std::make_unique<MemoryManager>();
        void* trading_memory = memory_manager->allocate_locked_memory(
            config.memory_size,
            config.numa_node,
            true  // 使用大頁
        );
        
        // 3. CPU綁定
        ThreadManager::bind_to_cpu(config.trading_cpu);
        ThreadManager::set_realtime_priority(99);
        
        // 4. 網路初始化
        network_handler = std::make_unique<NetworkHandler>();
        network_handler->init_dpdk();
        
        // 5. 交易引擎初始化
        trading_engine = std::make_unique<TradingEngine>(
            trading_memory,
            config.memory_size
        );
        
        return true;
    }
    
private:
    bool setup_system() {
        // 檢查權限
        if (geteuid() != 0) {
            std::cerr << "需要root權限\n";
            return false;
        }
        
        // 設定CPU調速器
        system("cpupower frequency-set -g performance");
        
        // 關閉透明大頁
        system("echo never > /sys/kernel/mm/transparent_hugepage/enabled");
        
        // 設定記憶體鎖定限制
        struct rlimit rlim;
        rlim.rlim_cur = RLIM_INFINITY;
        rlim.rlim_max = RLIM_INFINITY;
        setrlimit(RLIMIT_MEMLOCK, &rlim);
        
        return true;
    }
};
```

### 8.2 延遲測試結果

```
測試環境：
- CPU: Intel Xeon Gold 6248R (24C/48T)
- 記憶體: 256GB DDR4-2933 (8通道)
- 網路: Mellanox ConnectX-5 100GbE
- OS: CentOS 8.4 RT Kernel

優化前：
- 平均延遲: 85μs
- P99延遲: 250μs
- 最大延遲: 2ms
- 抖動: ±50μs

優化後：
- 平均延遲: 18μs
- P99延遲: 22μs
- 最大延遲: 35μs
- 抖動: ±1μs

改善幅度：
- 平均延遲降低: 78.8%
- P99延遲降低: 91.2%
- 最大延遲降低: 98.3%
- 抖動降低: 98%
```

---

## 9. 最佳實踐總結

### 9.1 硬體選擇建議

| 元件 | 建議配置 | 原因 |
|-----|---------|------|
| CPU | Intel Xeon Gold/AMD EPYC | 高主頻、大快取 |
| 記憶體 | DDR4-3200以上 | 低延遲、高頻寬 |
| 網路卡 | Mellanox/Intel XL710 | 支援DPDK/核心旁路 |
| 儲存 | Intel Optane SSD | 超低延遲 |

### 9.2 軟體配置清單

- [ ] 作業系統核心參數調優
- [ ] CPU隔離與綁定
- [ ] NUMA優化配置
- [ ] 大頁記憶體設定
- [ ] 中斷親和性調整
- [ ] 網路協定棧優化
- [ ] 即時核心安裝（可選）
- [ ] 監控系統部署

### 9.3 開發建議

1. **設計原則**
   - 無鎖資料結構優先
   - 避免動態記憶體分配
   - 最小化系統呼叫
   - 資料局部性優化

2. **測試方法**
   - 使用生產環境硬體
   - 模擬真實負載
   - 長時間穩定性測試
   - 極端情況壓力測試

3. **持續優化**
   - 建立基準測試
   - 定期效能分析
   - 追蹤新技術發展
   - 保持程式碼簡潔

---

## 10. 進階資源

### 10.1 參考文獻

- Intel® 64 and IA-32 Architectures Optimization Reference Manual
- DPDK Programmer's Guide
- Linux Performance and Tuning Guidelines
- High-Performance Trading System Design

### 10.2 開源專案

- [DPDK](https://www.dpdk.org/) - 資料平面開發套件
- [Seastar](http://seastar.io/) - 高效能C++框架
- [Aeron](https://github.com/real-logic/aeron) - 高效能訊息傳輸
- [Disruptor](https://lmax-exchange.github.io/disruptor/) - 高效能佇列

### 10.3 監控工具

- [Intel VTune](https://software.intel.com/vtune) - 效能分析
- [perf](https://perf.wiki.kernel.org/) - Linux效能工具
- [BPF/eBPF](https://ebpf.io/) - 核心追蹤
- [PMU Tools](https://github.com/andikleen/pmu-tools) - CPU效能監控

---

## 附錄A：常用命令速查

```bash
# CPU相關
taskset -c 0-3 ./app          # CPU親和性
chrt -f 99 ./app              # 實時優先級
cpupower frequency-info       # CPU頻率資訊

# 記憶體相關
numactl --hardware            # NUMA拓撲
numastat -c                   # NUMA統計
echo 1024 > /proc/sys/vm/nr_hugepages  # 大頁設定

# 網路相關
ethtool -g eth0              # 查看環形緩衝區
ethtool -C eth0              # 中斷調節設定
tc qdisc show                # 流量控制

# 監控相關
mpstat -P ALL 1              # CPU使用率
sar -n DEV 1                 # 網路流量
pidstat -d -p PID 1          # 程序I/O
```

## 附錄B：故障排除指南

| 症狀 | 診斷步驟 | 可能的解決方案 |
|-----|---------|--------------|
| 延遲突然增加 | 1. 檢查CPU頻率<br>2. 查看中斷統計<br>3. 檢查記憶體分配 | - 固定CPU頻率<br>- 調整中斷親和性<br>- 使用記憶體池 |
| 效能不穩定 | 1. 監控系統負載<br>2. 檢查NUMA配置<br>3. 分析快取命中率 | - CPU隔離<br>- NUMA綁定<br>- 資料結構優化 |
| 網路延遲高 | 1. 檢查網路卡配置<br>2. 分析協定棧<br>3. 查看丟包率 | - 使用DPDK<br>- 調整緩衝區<br>- 優化批次處理 |

---

**文件版本**: 1.0  
**最後更新**: 2024年  
**作者**: HFT系統優化團隊  
**授權**: MIT License