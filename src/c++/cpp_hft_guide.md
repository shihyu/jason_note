# C++高頻交易技術指南

## 目錄
- [延遲優化核心技術](#延遲優化核心技術)
- [CPU與系統級優化](#cpu與系統級優化)
- [內存管理與數據結構](#內存管理與數據結構)
- [網絡編程優化](#網絡編程優化)
- [編譯器與代碼優化](#編譯器與代碼優化)
- [實時系統配置](#實時系統配置)
- [監控與調試工具](#監控與調試工具)

---

## 延遲優化核心技術

### 微秒級優化策略

高頻交易的核心是將延遲壓縮到極致，每一微秒都可能決定盈利與否。

**關鍵原則：**
- 避免動態內存分配
- 減少系統調用
- 使用無鎖數據結構
- CPU親和性設置
- 預測分支行為

---

## CPU與系統級優化

### CPU核心綁定技術

#### 基本核心綁定

```cpp
#include <sched.h>
#include <pthread.h>
#include <unistd.h>

// 綁定當前進程到指定CPU核心
void bind_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    if (sched_setaffinity(0, sizeof(cpuset), &cpuset) == -1) {
        perror("sched_setaffinity failed");
        exit(1);
    }
    
    printf("Process bound to CPU %d\n", cpu_id);
}

// 綁定線程到指定CPU核心
void bind_thread_to_cpu(pthread_t thread, int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    int result = pthread_setaffinity_np(thread, sizeof(cpuset), &cpuset);
    if (result != 0) {
        fprintf(stderr, "pthread_setaffinity_np failed: %d\n", result);
        exit(1);
    }
}

// 創建綁定線程
void* trading_worker(void* arg) {
    int cpu_id = *((int*)arg);
    
    // 確認當前運行的CPU
    int current_cpu = sched_getcpu();
    printf("Trading thread running on CPU %d\n", current_cpu);
    
    // 主要交易邏輯
    while (true) {
        // 高頻交易處理邏輯
        process_market_data();
        execute_trading_strategy();
    }
    
    return nullptr;
}

void create_bound_trading_thread(int cpu_id) {
    pthread_t thread;
    pthread_attr_t attr;
    cpu_set_t cpuset;
    
    pthread_attr_init(&attr);
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    
    pthread_attr_setaffinity_np(&attr, sizeof(cpuset), &cpuset);
    pthread_create(&thread, &attr, trading_worker, &cpu_id);
    
    pthread_attr_destroy(&attr);
}
```

#### NUMA感知內存分配

```cpp
#include <numa.h>
#include <numaif.h>

class NUMAOptimizedAllocator {
private:
    int target_node;
    
public:
    NUMAOptimizedAllocator(int cpu_id) {
        if (numa_available() == -1) {
            fprintf(stderr, "NUMA not available\n");
            exit(1);
        }
        
        target_node = numa_node_of_cpu(cpu_id);
        printf("CPU %d belongs to NUMA node %d\n", cpu_id, target_node);
    }
    
    void* allocate_on_node(size_t size) {
        void* ptr = numa_alloc_onnode(size, target_node);
        if (!ptr) {
            fprintf(stderr, "NUMA allocation failed\n");
            exit(1);
        }
        return ptr;
    }
    
    void deallocate(void* ptr, size_t size) {
        numa_free(ptr, size);
    }
    
    // 綁定內存頁到特定NUMA節點
    void bind_memory_to_node(void* addr, size_t len) {
        unsigned long nodemask = 1UL << target_node;
        if (mbind(addr, len, MPOL_BIND, &nodemask, sizeof(nodemask) * 8, 0) == -1) {
            perror("mbind failed");
        }
    }
};
```

### 實時調度策略

```cpp
#include <sched.h>
#include <sys/mman.h>

class RealTimeScheduler {
public:
    // 設置實時優先級
    static void set_realtime_priority(int priority = 99) {
        struct sched_param param;
        param.sched_priority = priority;
        
        // 使用SCHED_FIFO獲得確定性調度
        if (sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
            perror("Failed to set real-time priority");
            exit(1);
        }
        
        // 鎖定內存，防止頁面交換
        if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
            perror("mlockall failed");
            exit(1);
        }
        
        printf("Real-time priority set to %d\n", priority);
    }
    
    // 檢查當前調度策略
    static void check_scheduling_policy() {
        int policy = sched_getscheduler(0);
        struct sched_param param;
        sched_getparam(0, &param);
        
        const char* policy_name;
        switch (policy) {
            case SCHED_FIFO: policy_name = "SCHED_FIFO"; break;
            case SCHED_RR: policy_name = "SCHED_RR"; break;
            case SCHED_OTHER: policy_name = "SCHED_OTHER"; break;
            default: policy_name = "UNKNOWN"; break;
        }
        
        printf("Current policy: %s, Priority: %d\n", policy_name, param.sched_priority);
    }
    
    // 設置CPU親和性和實時調度的完整配置
    static void setup_realtime_thread(int cpu_core, int priority = 99) {
        // 1. 綁定CPU核心
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_core, &cpuset);
        sched_setaffinity(0, sizeof(cpuset), &cpuset);
        
        // 2. 設置實時優先級
        struct sched_param param;
        param.sched_priority = priority;
        sched_setscheduler(0, SCHED_FIFO, &param);
        
        // 3. 鎖定內存
        mlockall(MCL_CURRENT | MCL_FUTURE);
        
        printf("Real-time thread setup: CPU %d, Priority %d\n", cpu_core, priority);
    }
};
```

---

## 內存管理與數據結構

### 緩存友好的數據結構

```cpp
#include <immintrin.h>
#include <atomic>

// 緩存行大小通常為64字節
static constexpr size_t CACHE_LINE_SIZE = 64;

// 避免false sharing的結構設計
struct alignas(CACHE_LINE_SIZE) CacheLineAligned {
    std::atomic<uint64_t> counter;
    char padding[CACHE_LINE_SIZE - sizeof(std::atomic<uint64_t>)];
};

// 高性能訂單簿數據結構
class OptimizedOrderBook {
private:
    static constexpr size_t MAX_LEVELS = 1000;
    
    struct PriceLevel {
        double price;
        uint64_t quantity;
        uint32_t order_count;
        uint32_t padding;  // 對齊到8字節邊界
    };
    
    // 使用固定大小數組避免動態分配
    alignas(CACHE_LINE_SIZE) PriceLevel bids[MAX_LEVELS];
    alignas(CACHE_LINE_SIZE) PriceLevel asks[MAX_LEVELS];
    
    // 分離到不同緩存行避免競爭
    alignas(CACHE_LINE_SIZE) volatile uint32_t bid_count;
    alignas(CACHE_LINE_SIZE) volatile uint32_t ask_count;
    
public:
    // 預取下一個緩存行
    void prefetch_next_level(size_t index) {
        if (index + 1 < MAX_LEVELS) {
            _mm_prefetch(reinterpret_cast<const char*>(&bids[index + 1]), _MM_HINT_T0);
        }
    }
    
    // 批量處理更新，提高緩存效率
    void batch_update_levels(const PriceLevel* updates, size_t count) {
        for (size_t i = 0; i < count; i += 8) {  // 按緩存行處理
            // 預取下一組數據
            if (i + 8 < count) {
                _mm_prefetch(reinterpret_cast<const char*>(&updates[i + 8]), _MM_HINT_T0);
            }
            
            // 處理當前緩存行的數據
            process_level_updates(&updates[i], std::min(size_t(8), count - i));
        }
    }
    
private:
    void process_level_updates(const PriceLevel* updates, size_t count) {
        // 實際的價格層級更新邏輯
        for (size_t i = 0; i < count; ++i) {
            // 更新邏輯
        }
    }
};
```

### 內存池管理

```cpp
#include <cstdlib>
#include <vector>

template<typename T>
class MemoryPool {
private:
    struct Block {
        alignas(T) char data[sizeof(T)];
        Block* next;
    };
    
    Block* free_list;
    std::vector<Block*> chunks;
    size_t chunk_size;
    
public:
    explicit MemoryPool(size_t initial_chunk_size = 1000) 
        : free_list(nullptr), chunk_size(initial_chunk_size) {
        allocate_chunk();
    }
    
    ~MemoryPool() {
        for (Block* chunk : chunks) {
            std::free(chunk);
        }
    }
    
    T* allocate() {
        if (!free_list) {
            allocate_chunk();
        }
        
        Block* block = free_list;
        free_list = free_list->next;
        return reinterpret_cast<T*>(block);
    }
    
    void deallocate(T* ptr) {
        Block* block = reinterpret_cast<Block*>(ptr);
        block->next = free_list;
        free_list = block;
    }
    
private:
    void allocate_chunk() {
        // 分配對齊的內存塊
        Block* chunk = static_cast<Block*>(
            std::aligned_alloc(CACHE_LINE_SIZE, sizeof(Block) * chunk_size)
        );
        
        if (!chunk) {
            throw std::bad_alloc();
        }
        
        chunks.push_back(chunk);
        
        // 構建自由鏈表
        for (size_t i = 0; i < chunk_size - 1; ++i) {
            chunk[i].next = &chunk[i + 1];
        }
        chunk[chunk_size - 1].next = free_list;
        free_list = chunk;
    }
};

// 使用示例
class Order {
public:
    uint64_t order_id;
    double price;
    uint64_t quantity;
    char symbol[16];
    
    static MemoryPool<Order> pool;
    
    void* operator new(size_t) {
        return pool.allocate();
    }
    
    void operator delete(void* ptr) {
        pool.deallocate(static_cast<Order*>(ptr));
    }
};

MemoryPool<Order> Order::pool;
```

---

## 網絡編程優化

### 零拷貝網絡編程

```cpp
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>

class HighPerformanceNetwork {
private:
    int epoll_fd;
    static constexpr int MAX_EVENTS = 1000;
    struct epoll_event events[MAX_EVENTS];
    
public:
    HighPerformanceNetwork() {
        epoll_fd = epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd == -1) {
            perror("epoll_create1");
            exit(1);
        }
    }
    
    // 創建高性能UDP套接字
    int create_optimized_udp_socket() {
        int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
        if (sockfd == -1) {
            perror("socket");
            return -1;
        }
        
        // 設置套接字選項以獲得最佳性能
        int opt = 1;
        
        // 允許地址重用
        setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &opt, sizeof(opt));
        
        // 設置接收緩衝區大小
        int buffer_size = 64 * 1024 * 1024;  // 64MB
        setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &buffer_size, sizeof(buffer_size));
        setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF, &buffer_size, sizeof(buffer_size));
        
        // 啟用時間戳
        opt = SOF_TIMESTAMPING_RX_HARDWARE | SOF_TIMESTAMPING_RAW_HARDWARE;
        setsockopt(sockfd, SOL_SOCKET, SO_TIMESTAMPING, &opt, sizeof(opt));
        
        return sockfd;
    }
    
    // 高性能數據接收
    void receive_market_data(int sockfd) {
        char buffer[65536];  // 64KB緩衝區
        struct sockaddr_in sender_addr;
        socklen_t addr_len = sizeof(sender_addr);
        
        // 使用MSG_DONTWAIT進行非阻塞接收
        ssize_t bytes_received = recvfrom(sockfd, buffer, sizeof(buffer), 
                                         MSG_DONTWAIT, 
                                         (struct sockaddr*)&sender_addr, 
                                         &addr_len);
        
        if (bytes_received > 0) {
            // 獲取硬件時間戳
            uint64_t timestamp = get_hardware_timestamp(sockfd);
            process_market_data(buffer, bytes_received, timestamp);
        }
    }
    
private:
    uint64_t get_hardware_timestamp(int sockfd) {
        // 從套接字獲取硬件時間戳的實現
        struct msghdr msg = {0};
        struct cmsghdr *cmsg;
        char control[1024];
        
        msg.msg_control = control;
        msg.msg_controllen = sizeof(control);
        
        if (recvmsg(sockfd, &msg, MSG_ERRQUEUE) > 0) {
            for (cmsg = CMSG_FIRSTHDR(&msg); cmsg; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
                if (cmsg->cmsg_level == SOL_SOCKET && 
                    cmsg->cmsg_type == SCM_TIMESTAMPING) {
                    struct timespec *ts = (struct timespec*)CMSG_DATA(cmsg);
                    return ts->tv_sec * 1000000000ULL + ts->tv_nsec;
                }
            }
        }
        
        return 0;
    }
    
    void process_market_data(const char* data, size_t length, uint64_t timestamp) {
        // 處理市場數據的邏輯
    }
};
```

### DPDK用戶態網絡驅動

```cpp
// DPDK基本設置示例
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>

class DPDKNetwork {
private:
    static constexpr uint16_t PORT_ID = 0;
    static constexpr uint16_t RX_RING_SIZE = 1024;
    static constexpr uint16_t TX_RING_SIZE = 1024;
    static constexpr uint16_t NUM_MBUFS = 8191;
    static constexpr uint16_t MBUF_CACHE_SIZE = 250;
    
    struct rte_mempool *mbuf_pool;
    
public:
    int initialize_dpdk(int argc, char *argv[]) {
        // 初始化EAL (Environment Abstraction Layer)
        int ret = rte_eal_init(argc, argv);
        if (ret < 0) {
            rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
        }
        
        // 創建內存池
        mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
                                           MBUF_CACHE_SIZE, 0, 
                                           RTE_MBUF_DEFAULT_BUF_SIZE,
                                           rte_socket_id());
        
        if (mbuf_pool == nullptr) {
            rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");
        }
        
        // 配置網卡
        return configure_port();
    }
    
    void packet_processing_loop() {
        struct rte_mbuf *bufs[32];
        
        while (true) {
            // 批量接收數據包
            const uint16_t nb_rx = rte_eth_rx_burst(PORT_ID, 0, bufs, 32);
            
            if (unlikely(nb_rx == 0)) {
                continue;
            }
            
            // 處理接收到的數據包
            for (uint16_t i = 0; i < nb_rx; i++) {
                process_packet(bufs[i]);
                rte_pktmbuf_free(bufs[i]);
            }
        }
    }
    
private:
    int configure_port() {
        struct rte_eth_conf port_conf = {};
        
        // 配置端口
        int retval = rte_eth_dev_configure(PORT_ID, 1, 1, &port_conf);
        if (retval != 0) {
            return retval;
        }
        
        // 設置RX隊列
        retval = rte_eth_rx_queue_setup(PORT_ID, 0, RX_RING_SIZE,
                                       rte_eth_dev_socket_id(PORT_ID),
                                       nullptr, mbuf_pool);
        if (retval < 0) {
            return retval;
        }
        
        // 設置TX隊列
        retval = rte_eth_tx_queue_setup(PORT_ID, 0, TX_RING_SIZE,
                                       rte_eth_dev_socket_id(PORT_ID),
                                       nullptr);
        if (retval < 0) {
            return retval;
        }
        
        // 啟動端口
        retval = rte_eth_dev_start(PORT_ID);
        if (retval < 0) {
            return retval;
        }
        
        return 0;
    }
    
    void process_packet(struct rte_mbuf *pkt) {
        // 解析和處理數據包
        char *data = rte_pktmbuf_mtod(pkt, char *);
        uint16_t data_len = rte_pktmbuf_data_len(pkt);
        
        // 處理市場數據
        parse_market_data(data, data_len);
    }
    
    void parse_market_data(const char *data, uint16_t length) {
        // 市場數據解析邏輯
    }
};
```

---

## 編譯器與代碼優化

### 高精度時間測量

```cpp
#include <x86intrin.h>
#include <chrono>

class HighPrecisionTimer {
private:
    static uint64_t tsc_frequency;
    static bool calibrated;
    
public:
    // 校準TSC頻率
    static void calibrate_tsc() {
        auto start = std::chrono::high_resolution_clock::now();
        uint64_t tsc_start = __rdtsc();
        
        // 等待1秒進行校準
        std::this_thread::sleep_for(std::chrono::seconds(1));
        
        uint64_t tsc_end = __rdtsc();
        auto end = std::chrono::high_resolution_clock::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
        tsc_frequency = (tsc_end - tsc_start) * 1000000000 / duration.count();
        calibrated = true;
        
        printf("TSC frequency: %lu Hz\n", tsc_frequency);
    }
    
    // 獲取TSC計數
    static inline uint64_t get_tsc() {
        unsigned int dummy;
        return __rdtscp(&dummy);  // 序列化版本的rdtsc
    }
    
    // 將TSC轉換為納秒
    static double tsc_to_nanoseconds(uint64_t tsc_cycles) {
        if (!calibrated) {
            calibrate_tsc();
        }
        return static_cast<double>(tsc_cycles) * 1000000000.0 / tsc_frequency;
    }
    
    // 高精度延時
    static void precise_delay_ns(uint64_t nanoseconds) {
        uint64_t tsc_target = nanoseconds * tsc_frequency / 1000000000;
        uint64_t start_tsc = get_tsc();
        
        while ((get_tsc() - start_tsc) < tsc_target) {
            _mm_pause();  // 暫停指令，降低功耗
        }
    }
};

uint64_t HighPrecisionTimer::tsc_frequency = 0;
bool HighPrecisionTimer::calibrated = false;
```

### 分支預測優化

```cpp
#include <cstdlib>

// 分支預測提示宏
#define likely(x)       __builtin_expect(!!(x), 1)
#define unlikely(x)     __builtin_expect(!!(x), 0)

class OptimizedTrading {
public:
    // 使用分支預測優化的訂單處理
    void process_order(const Order& order) {
        // 大多數情況下訂單是有效的
        if (likely(is_valid_order(order))) {
            execute_order(order);
        } else {
            // 處理無效訂單的情況較少
            handle_invalid_order(order);
        }
        
        // 價格變動通常很小
        if (unlikely(is_significant_price_change(order.price))) {
            trigger_risk_management();
        }
    }
    
    // 強制內聯的關鍵函數
    __attribute__((always_inline))
    inline bool is_valid_order(const Order& order) {
        return order.quantity > 0 && 
               order.price > 0 && 
               order.order_id != 0;
    }
    
    // 使用restrict關鍵字優化指針別名
    void process_price_array(double* __restrict__ prices, 
                           const size_t* __restrict__ volumes,
                           size_t count) {
        for (size_t i = 0; i < count; ++i) {
            prices[i] *= calculate_adjustment_factor(volumes[i]);
        }
    }
    
private:
    void execute_order(const Order& order) {
        // 訂單執行邏輯
    }
    
    void handle_invalid_order(const Order& order) {
        // 處理無效訂單
    }
    
    bool is_significant_price_change(double price) {
        static double last_price = 0.0;
        double change = std::abs((price - last_price) / last_price);
        last_price = price;
        return change > 0.05;  // 5%變動
    }
    
    void trigger_risk_management() {
        // 風險管理邏輯
    }
    
    double calculate_adjustment_factor(size_t volume) {
        return 1.0 + (volume / 1000000.0);
    }
};
```

### SIMD向量化優化

```cpp
#include <immintrin.h>

class SIMDOptimizations {
public:
    // 使用AVX2進行向量化計算
    void vectorized_price_calculation(const double* prices, 
                                    const double* volumes,
                                    double* results, 
                                    size_t count) {
        size_t simd_count = count - (count % 4);  // AVX2處理4個double
        
        for (size_t i = 0; i < simd_count; i += 4) {
            // 加載4個價格和數量
            __m256d price_vec = _mm256_load_pd(&prices[i]);
            __m256d volume_vec = _mm256_load_pd(&volumes[i]);
            
            // 向量化乘法運算
            __m256d result_vec = _mm256_mul_pd(price_vec, volume_vec);
            
            // 存儲結果
            _mm256_store_pd(&results[i], result_vec);
        }
        
        // 處理剩餘元素
        for (size_t i = simd_count; i < count; ++i) {
            results[i] = prices[i] * volumes[i];
        }
    }
    
    // 向量化的移動平均計算
    void moving_average_avx2(const float* data, float* output, 
                            size_t data_size, size_t window_size) {
        __m256 sum_vec = _mm256_setzero_ps();
        float window_inv = 1.0f / window_size;
        __m256 window_inv_vec = _mm256_set1_ps(window_inv);
        
        for (size_t i = 0; i < data_size - 8; i += 8) {
            __m256 data_vec = _mm256_load_ps(&data[i]);
            
            // 水平相加向量元素
            __m256 hadd1 = _mm256_hadd_ps(data_vec, data_vec);
            __m256 hadd2 = _mm256_hadd_ps(hadd1, hadd1);
            
            // 提取總和並計算平均值
            float sum = _mm256_cvtss_f32(hadd2);
            output[i / 8] = sum * window_inv;
        }
    }
};
```

---

## 實時系統配置

### 完整的HFT線程設置

```cpp
#include <signal.h>
#include <sys/resource.h>

class HFTSystemSetup {
public:
    struct HFTConfig {
        int cpu_core;
        int priority;
        size_t stack_size;
        bool isolate_interrupts;
        bool disable_swap;
    };
    
    static void setup_hft_environment(const HFTConfig& config) {
        printf("Setting up HFT environment...\n");
        
        // 1. 設置信號屏蔽
        mask_signals();
        
        // 2. 設置資源限制
        set_resource_limits();
        
        // 3. 綁定CPU並設置實時優先級
        setup_cpu_and_priority(config.cpu_core, config.priority);
        
        // 4. 內存鎖定
        if (config.disable_swap) {
            lock_memory();
        }
        
        // 5. 中斷隔離
        if (config.isolate_interrupts) {
            isolate_interrupts(config.cpu_core);
        }
        
        // 6. 系統調優
        tune_system_parameters();
        
        printf("HFT environment setup complete\n");
    }
    
private:
    static void mask_signals() {
        sigset_t set;
        sigemptyset(&set);
        sigaddset(&set, SIGINT);
        sigaddset(&set, SIGTERM);
        sigaddset(&set, SIGUSR1);
        sigaddset(&set, SIGUSR2);
        
        if (pthread_sigmask(SIG_BLOCK, &set, nullptr) != 0) {
            perror("pthread_sigmask");
            exit(1);
        }
    }
    
    static void set_resource_limits() {
        struct rlimit rlim;
        
        // 設置最大文件描述符數量
        rlim.rlim_cur = 65536;
        rlim.rlim_max = 65536;
        setrlimit(RLIMIT_NOFILE, &rlim);
        
        // 設置最大內存鎖定大小
        rlim.rlim_cur = RLIM_INFINITY;
        rlim.rlim_max = RLIM_INFINITY;
        setrlimit(RLIMIT_MEMLOCK, &rlim);
        
        // 設置堆棧大小
        rlim.rlim_cur = 8 * 1024 * 1024;  // 8MB
        rlim.rlim_max = 8 * 1024 * 1024;
        setrlimit(RLIMIT_STACK, &rlim);
    }
    
    static void setup_cpu_and_priority(int cpu_core, int priority) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_core, &cpuset);
        sched_setaffinity(0, sizeof(cpuset), &cpuset);
        
        struct sched_param param;
        param.sched_priority = priority;
        sched_setscheduler(0, SCHED_FIFO, &param);
    }
    
    static void lock_memory() {
        if (mlockall(MCL_CURRENT | MCL_FUTURE) == -1) {
            perror("mlockall");
            exit(1);
        }
    }
    
    static void isolate_interrupts(int cpu_core) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), 
                "echo %d > /proc/irq/default_smp_affinity", 
                ~(1 << cpu_core));
        system(cmd);
    }
    
    static void tune_system_parameters() {
        // 設置TCP參數
        system("echo 1 > /proc/sys/net/ipv4/tcp_low_latency");
        system("echo 0 > /proc/sys/net/ipv4/tcp_timestamps");
        system("echo 0 > /proc/sys/kernel/timer_migration");
    }
};

---

## 監控與調試工具

### Linux 效能檢測工具完整清單

#### 1. Context Switch 監控工具

```bash
# vmstat - 系統整體狀態監控
vmstat 1  # 每秒更新一次，cs列顯示context switch次數

# pidstat - 進程級別監控
pidstat -w -p [PID] 1  # 監控特定進程的context switch
pidstat -wt -p [PID] 1  # 包含線程級別的context switch

# perf stat - 詳細的效能統計
perf stat -e context-switches,cpu-migrations -p [PID]
perf stat -d -p [PID]  # 詳細模式

# 監控特定CPU核心的context switch
perf stat -e context-switches -C 0-3  # 監控CPU 0-3

# sar - 系統活動報告
sar -w 1  # 顯示context switch和進程創建率
```

#### 2. CPU 效能分析工具

```bash
# perf top - 實時CPU熱點分析
perf top -p [PID]  # 監控特定進程
perf top -C 0  # 監控特定CPU核心

# perf record/report - 詳細的效能分析
perf record -g -p [PID] -- sleep 10  # 記錄10秒
perf report  # 查看報告

# mpstat - 多處理器統計
mpstat -P ALL 1  # 顯示所有CPU核心使用情況

# turbostat - CPU頻率和功耗監控
turbostat --interval 1

# cpupower - CPU頻率控制
cpupower frequency-info  # 查看當前頻率設置
cpupower frequency-set -g performance  # 設置高性能模式
```

#### 3. 內存與緩存監控

```bash
# pcm - Intel Performance Counter Monitor
pcm 1  # 監控內存帶寬、緩存命中率

# perf stat - 緩存性能監控
perf stat -e cache-references,cache-misses,L1-dcache-loads,L1-dcache-load-misses -p [PID]

# numastat - NUMA統計
numastat -p [PID]  # 查看進程的NUMA分佈
numactl --hardware  # 顯示NUMA硬件配置

# smem - 內存使用報告
smem -P [process_name] -k  # 顯示進程內存使用

# pmap - 進程內存映射
pmap -x [PID]  # 詳細內存映射信息
```

#### 4. 網絡延遲監控

```bash
# ss - Socket統計
ss -i  # 顯示內部TCP信息（RTT、擁塞窗口等）
ss -tnp  # 顯示TCP連接和進程信息

# tc - 流量控制（查看隊列延遲）
tc -s qdisc show dev eth0

# ethtool - 網卡統計
ethtool -S eth0  # 顯示詳細的網卡統計
ethtool -g eth0  # 顯示ring buffer設置

# netstat - 網絡統計
netstat -s  # 顯示網絡統計摘要

# iftop - 實時流量監控
iftop -i eth0  # 監控特定網卡流量
```

#### 5. 磁盤 I/O 監控

```bash
# iotop - I/O 使用率排名
iotop -p [PID]  # 監控特定進程

# iostat - I/O 統計
iostat -x 1  # 詳細I/O統計
iostat -p sda 1  # 監控特定磁盤

# blktrace - 塊設備跟踪
blktrace -d /dev/sda -o trace
blkparse trace  # 解析跟踪數據

# biolatency - BPF工具，監控I/O延遲分佈
biolatency-bpfcc
```

#### 6. 系統調用追蹤

```bash
# strace - 系統調用追蹤
strace -c -p [PID]  # 統計系統調用
strace -T -p [PID]  # 顯示每個系統調用的時間
strace -e trace=network -p [PID]  # 只追蹤網絡相關調用

# ltrace - 庫調用追蹤
ltrace -c -p [PID]  # 統計庫函數調用

# ftrace - 內核函數追蹤
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on
cat /sys/kernel/debug/tracing/trace
```

#### 7. 延遲分析工具

```bash
# latencytop - 系統延遲分析
latencytop  # 需要內核支持

# cyclictest - 實時延遲測試
cyclictest -t1 -p 99 -i 1000 -n  # 測試實時延遲

# hwlatdetect - 硬件延遲檢測
hwlatdetect --duration=60  # 檢測60秒
```

#### 8. BPF/eBPF 工具集

```bash
# bpftrace - 高級追蹤語言
bpftrace -e 'tracepoint:sched:sched_switch { @[comm] = count(); }'

# bcc-tools 工具集
execsnoop  # 監控新進程執行
opensnoop  # 監控文件打開
tcpconnect  # 監控TCP連接
tcpretrans  # 監控TCP重傳
runqlat  # CPU運行隊列延遲
hardirqs  # 硬中斷統計
softirqs  # 軟中斷統計
```

### C++ 代碼中的效能監控實現

```cpp
#include <sys/time.h>
#include <sys/resource.h>
#include <fstream>
#include <sstream>

class PerformanceMonitor {
private:
    struct CPUStats {
        unsigned long long user;
        unsigned long long nice;
        unsigned long long system;
        unsigned long long idle;
        unsigned long long iowait;
        unsigned long long irq;
        unsigned long long softirq;
    };
    
    struct ProcessStats {
        long voluntary_ctxt_switches;
        long nonvoluntary_ctxt_switches;
        double cpu_usage;
        size_t memory_rss;
        size_t memory_vms;
    };
    
public:
    // 獲取進程的context switch統計
    static ProcessStats get_process_stats(pid_t pid = 0) {
        ProcessStats stats = {0};
        
        if (pid == 0) {
            pid = getpid();
        }
        
        // 讀取 /proc/[pid]/status
        std::string status_path = "/proc/" + std::to_string(pid) + "/status";
        std::ifstream status_file(status_path);
        std::string line;
        
        while (std::getline(status_file, line)) {
            if (line.find("voluntary_ctxt_switches:") != std::string::npos) {
                sscanf(line.c_str(), "voluntary_ctxt_switches: %ld", 
                       &stats.voluntary_ctxt_switches);
            } else if (line.find("nonvoluntary_ctxt_switches:") != std::string::npos) {
                sscanf(line.c_str(), "nonvoluntary_ctxt_switches: %ld", 
                       &stats.nonvoluntary_ctxt_switches);
            } else if (line.find("VmRSS:") != std::string::npos) {
                sscanf(line.c_str(), "VmRSS: %zu", &stats.memory_rss);
            } else if (line.find("VmSize:") != std::string::npos) {
                sscanf(line.c_str(), "VmSize: %zu", &stats.memory_vms);
            }
        }
        
        // 獲取CPU使用率
        stats.cpu_usage = get_cpu_usage(pid);
        
        return stats;
    }
    
    // 獲取系統級context switch
    static long get_system_context_switches() {
        std::ifstream stat_file("/proc/stat");
        std::string line;
        
        while (std::getline(stat_file, line)) {
            if (line.find("ctxt") == 0) {
                long ctxt;
                sscanf(line.c_str(), "ctxt %ld", &ctxt);
                return ctxt;
            }
        }
        
        return -1;
    }
    
    // 監控線程的CPU遷移
    static int get_cpu_migrations(pid_t tid) {
        std::string schedstat_path = "/proc/" + std::to_string(tid) + "/schedstat";
        std::ifstream schedstat_file(schedstat_path);
        
        if (!schedstat_file.is_open()) {
            return -1;
        }
        
        unsigned long long run_time, wait_time;
        int nr_migrations;
        schedstat_file >> run_time >> wait_time >> nr_migrations;
        
        return nr_migrations;
    }
    
    // 獲取緩存未命中統計（需要perf權限）
    static void get_cache_stats(pid_t pid, long& l1_misses, long& llc_misses) {
        char cmd[256];
        snprintf(cmd, sizeof(cmd), 
                "perf stat -e L1-dcache-load-misses,LLC-load-misses -p %d sleep 0.1 2>&1", 
                pid);
        
        FILE* pipe = popen(cmd, "r");
        if (!pipe) {
            l1_misses = llc_misses = -1;
            return;
        }
        
        char buffer[256];
        while (fgets(buffer, sizeof(buffer), pipe)) {
            if (strstr(buffer, "L1-dcache-load-misses")) {
                sscanf(buffer, "%ld", &l1_misses);
            } else if (strstr(buffer, "LLC-load-misses")) {
                sscanf(buffer, "%ld", &llc_misses);
            }
        }
        
        pclose(pipe);
    }
    
    // 實時監控並報告
    static void monitor_performance(int duration_seconds) {
        pid_t pid = getpid();
        
        printf("Monitoring PID %d for %d seconds...\n", pid, duration_seconds);
        printf("Time\tVol_CS\tNonvol_CS\tCPU%%\tRSS(MB)\tCPU_Migrations\n");
        
        for (int i = 0; i < duration_seconds; ++i) {
            ProcessStats stats = get_process_stats(pid);
            int migrations = get_cpu_migrations(pid);
            
            printf("%d\t%ld\t%ld\t%.2f\t%.2f\t%d\n",
                   i,
                   stats.voluntary_ctxt_switches,
                   stats.nonvoluntary_ctxt_switches,
                   stats.cpu_usage,
                   stats.memory_rss / 1024.0,
                   migrations);
            
            sleep(1);
        }
    }
    
private:
    static double get_cpu_usage(pid_t pid) {
        static std::map<pid_t, std::pair<unsigned long long, clock_t>> last_stats;
        
        // 讀取進程CPU時間
        std::string stat_path = "/proc/" + std::to_string(pid) + "/stat";
        std::ifstream stat_file(stat_path);
        std::string line;
        std::getline(stat_file, line);
        
        // 解析stat文件（簡化版）
        std::istringstream iss(line);
        std::string ignore;
        unsigned long utime, stime;
        
        // 跳過前13個字段
        for (int i = 0; i < 13; ++i) {
            iss >> ignore;
        }
        iss >> utime >> stime;
        
        unsigned long long total_time = utime + stime;
        clock_t current_time = clock();
        
        double cpu_percent = 0.0;
        
        if (last_stats.find(pid) != last_stats.end()) {
            auto& last = last_stats[pid];
            unsigned long long time_diff = total_time - last.first;
            clock_t clock_diff = current_time - last.second;
            
            if (clock_diff > 0) {
                cpu_percent = 100.0 * time_diff / clock_diff;
            }
        }
        
        last_stats[pid] = {total_time, current_time};
        
        return cpu_percent;
    }
};

// 使用示例
int main() {
    // 設置高性能環境
    RealTimeScheduler::setup_realtime_thread(2, 99);
    
    // 開始監控
    PerformanceMonitor::monitor_performance(10);
    
    return 0;
}