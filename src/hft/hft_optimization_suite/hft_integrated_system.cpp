#include <iostream>
#include <vector>
#include <queue>
#include <thread>
#include <atomic>
#include <chrono>
#include <memory>
#include <cstring>
#include <iomanip>
#include <algorithm>
#include <array>

#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <netinet/in.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>
// #include <numa.h>  // Optional: NUMA support
#include <signal.h>
#include <errno.h>

using namespace std;
using namespace chrono;

// 無鎖 SPSC (Single Producer Single Consumer) 隊列
template<typename T, size_t Size>
class SPSCQueue {
private:
    alignas(64) atomic<size_t> write_pos{0};
    alignas(64) atomic<size_t> read_pos{0};
    alignas(64) array<T, Size> buffer;
    
public:
    bool push(const T& item) {
        size_t current_write = write_pos.load(memory_order_relaxed);
        size_t next_write = (current_write + 1) % Size;
        
        if (next_write == read_pos.load(memory_order_acquire)) {
            return false;  // Queue full
        }
        
        buffer[current_write] = item;
        write_pos.store(next_write, memory_order_release);
        return true;
    }
    
    bool pop(T& item) {
        size_t current_read = read_pos.load(memory_order_relaxed);
        
        if (current_read == write_pos.load(memory_order_acquire)) {
            return false;  // Queue empty
        }
        
        item = buffer[current_read];
        read_pos.store((current_read + 1) % Size, memory_order_release);
        return true;
    }
    
    bool empty() const {
        return read_pos.load(memory_order_acquire) == 
               write_pos.load(memory_order_acquire);
    }
};

// 市場數據結構
struct MarketData {
    uint64_t timestamp;
    uint32_t symbol_id;
    double bid_price;
    double ask_price;
    uint32_t bid_size;
    uint32_t ask_size;
    char padding[24];  // 對齊到 64 bytes
};

// 訂單結構
struct Order {
    uint64_t order_id;
    uint32_t symbol_id;
    double price;
    uint32_t quantity;
    bool is_buy;
    char padding[27];  // 對齊到 64 bytes
};

// 整合的 HFT 系統
class UltraLowLatencyTradingSystem {
private:
    // 系統配置
    static constexpr size_t MARKET_DATA_BUFFER_SIZE = 1UL << 30;  // 1 GB
    static constexpr size_t ORDER_BUFFER_SIZE = 256 * 1024 * 1024;  // 256 MB
    static constexpr size_t QUEUE_SIZE = 65536;
    static constexpr int MAX_EVENTS = 1024;
    
    // 大頁面緩衝區
    void* market_data_buffer;
    void* order_buffer;
    size_t market_data_offset;
    size_t order_offset;
    
    // 網路相關
    int multicast_fd;
    int order_send_fd;
    int epoll_fd;
    
    // 無鎖隊列
    SPSCQueue<MarketData, QUEUE_SIZE> market_queue;
    SPSCQueue<Order, QUEUE_SIZE> order_queue;
    
    // 執行緒控制
    atomic<bool> running{true};
    vector<thread> worker_threads;
    
    // 統計
    atomic<uint64_t> total_market_data{0};
    atomic<uint64_t> total_orders{0};
    atomic<uint64_t> total_latency_ns{0};
    
public:
    UltraLowLatencyTradingSystem() {
        cout << "Initializing Ultra Low Latency Trading System..." << endl;
        initialize();
    }
    
    ~UltraLowLatencyTradingSystem() {
        shutdown();
    }
    
    void initialize() {
        // 1. 設置大頁面
        setup_huge_pages();
        
        // 2. 初始化網路
        setup_networking();
        
        // 3. 設置 CPU 親和性並啟動執行緒
        setup_threads();
        
        // 4. 預熱系統
        warmup_system();
        
        cout << "System initialized successfully!" << endl;
    }
    
    void run() {
        cout << "Trading system running..." << endl;
        
        // 主執行緒作為監控執行緒
        while (running) {
            this_thread::sleep_for(seconds(1));
            print_statistics();
        }
        
        // 等待所有工作執行緒
        for (auto& t : worker_threads) {
            if (t.joinable()) {
                t.join();
            }
        }
    }
    
    void shutdown() {
        cout << "Shutting down trading system..." << endl;
        running = false;
        
        // 清理資源
        if (epoll_fd >= 0) close(epoll_fd);
        if (multicast_fd >= 0) close(multicast_fd);
        if (order_send_fd >= 0) close(order_send_fd);
        
        // 釋放大頁面
        if (market_data_buffer) {
            munmap(market_data_buffer, MARKET_DATA_BUFFER_SIZE);
        }
        if (order_buffer) {
            munmap(order_buffer, ORDER_BUFFER_SIZE);
        }
    }
    
private:
    void setup_huge_pages() {
        cout << "Setting up huge pages..." << endl;
        
        // 分配 1GB 大頁面給市場數據
        market_data_buffer = mmap(
            nullptr,
            MARKET_DATA_BUFFER_SIZE,
            PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | (30 << MAP_HUGE_SHIFT),
            -1, 0
        );
        
        if (market_data_buffer == MAP_FAILED) {
            // 降級到 2MB 大頁面
            cout << "1GB huge pages not available, trying 2MB..." << endl;
            market_data_buffer = mmap(
                nullptr,
                MARKET_DATA_BUFFER_SIZE,
                PROT_READ | PROT_WRITE,
                MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                -1, 0
            );
            
            if (market_data_buffer == MAP_FAILED) {
                throw runtime_error("Failed to allocate huge pages for market data");
            }
        }
        
        // 分配 2MB 大頁面給訂單緩衝
        order_buffer = mmap(
            nullptr,
            ORDER_BUFFER_SIZE,
            PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
            -1, 0
        );
        
        if (order_buffer == MAP_FAILED) {
            throw runtime_error("Failed to allocate huge pages for orders");
        }
        
        // 預觸摸記憶體
        memset(market_data_buffer, 0, MARKET_DATA_BUFFER_SIZE);
        memset(order_buffer, 0, ORDER_BUFFER_SIZE);
        
        // 鎖定記憶體
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            cerr << "Warning: Failed to lock memory" << endl;
        }
        
        cout << "Huge pages allocated: " 
             << (MARKET_DATA_BUFFER_SIZE + ORDER_BUFFER_SIZE) / (1024*1024) 
             << " MB" << endl;
    }
    
    void setup_networking() {
        cout << "Setting up networking..." << endl;
        
        // 創建多播 socket 接收市場數據
        multicast_fd = socket(AF_INET, SOCK_DGRAM, 0);
        if (multicast_fd < 0) {
            throw runtime_error("Failed to create multicast socket");
        }
        
        // 設置 socket 選項
        int opt = 1;
        setsockopt(multicast_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
        
        // 設置接收緩衝區大小
        int rcvbuf = 8 * 1024 * 1024;  // 8MB
        setsockopt(multicast_fd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
        
        // 設置非阻塞
        set_nonblocking(multicast_fd);
        
        // 綁定到多播地址
        sockaddr_in addr{};
        addr.sin_family = AF_INET;
        addr.sin_addr.s_addr = INADDR_ANY;
        addr.sin_port = htons(5555);
        bind(multicast_fd, (sockaddr*)&addr, sizeof(addr));
        
        // 創建訂單發送 socket
        order_send_fd = socket(AF_INET, SOCK_STREAM, 0);
        if (order_send_fd < 0) {
            throw runtime_error("Failed to create order socket");
        }
        
        // TCP_NODELAY - 關閉 Nagle 算法
        setsockopt(order_send_fd, IPPROTO_TCP, TCP_NODELAY, &opt, sizeof(opt));
        
        // 創建 epoll
        epoll_fd = epoll_create1(EPOLL_CLOEXEC);
        if (epoll_fd < 0) {
            throw runtime_error("Failed to create epoll");
        }
        
        // 添加市場數據 socket 到 epoll
        epoll_event ev{};
        ev.events = EPOLLIN | EPOLLET;
        ev.data.fd = multicast_fd;
        epoll_ctl(epoll_fd, EPOLL_CTL_ADD, multicast_fd, &ev);
        
        cout << "Network setup completed" << endl;
    }
    
    void setup_threads() {
        cout << "Setting up threads with CPU affinity..." << endl;
        
        int num_cpus = sysconf(_SC_NPROCESSORS_ONLN);
        cout << "Available CPUs: " << num_cpus << endl;
        
        // IO 執行緒 - CPU 0
        worker_threads.emplace_back([this]() {
            io_thread_function(0);
        });
        
        // 策略執行緒 - CPU 1-2
        for (int cpu = 1; cpu <= min(2, num_cpus - 2); cpu++) {
            worker_threads.emplace_back([this, cpu]() {
                strategy_thread_function(cpu);
            });
        }
        
        // 訂單執行緒 - CPU 3
        if (num_cpus > 3) {
            worker_threads.emplace_back([this]() {
                order_thread_function(3);
            });
        }
    }
    
    void io_thread_function(int cpu_id) {
        // 綁定到指定 CPU
        pin_thread_to_cpu(cpu_id);
        set_thread_name("IO_Thread");
        set_realtime_priority(99);
        
        cout << "IO thread running on CPU " << cpu_id << endl;
        
        epoll_event events[MAX_EVENTS];
        char buffer[65536];
        
        while (running) {
            // 等待網路事件
            int nfds = epoll_wait(epoll_fd, events, MAX_EVENTS, 1);
            
            for (int i = 0; i < nfds; i++) {
                if (events[i].data.fd == multicast_fd) {
                    // 接收所有可用的市場數據
                    while (true) {
                        ssize_t n = recv(multicast_fd, buffer, sizeof(buffer), MSG_DONTWAIT);
                        
                        if (n <= 0) {
                            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                                break;
                            }
                            continue;
                        }
                        
                        // 解析並放入隊列
                        if (n >= sizeof(MarketData)) {
                            MarketData* data = reinterpret_cast<MarketData*>(buffer);
                            data->timestamp = rdtsc();  // 記錄接收時間
                            
                            if (!market_queue.push(*data)) {
                                // 隊列滿，記錄丟失
                                cerr << "Market data queue full!" << endl;
                            } else {
                                total_market_data++;
                            }
                        }
                    }
                }
            }
        }
    }
    
    void strategy_thread_function(int cpu_id) {
        // 綁定到指定 CPU
        pin_thread_to_cpu(cpu_id);
        set_thread_name("Strategy_Thread");
        set_realtime_priority(98);
        
        cout << "Strategy thread running on CPU " << cpu_id << endl;
        
        MarketData data;
        
        while (running) {
            // 從隊列獲取市場數據
            if (market_queue.pop(data)) {
                // 簡單的策略邏輯
                Order order = generate_order(data);
                
                if (order.order_id != 0) {
                    // 發送訂單到訂單隊列
                    if (!order_queue.push(order)) {
                        cerr << "Order queue full!" << endl;
                    } else {
                        total_orders++;
                        
                        // 計算延遲
                        uint64_t now = rdtsc();
                        uint64_t latency = now - data.timestamp;
                        total_latency_ns += latency;
                    }
                }
            } else {
                // 隊列空，短暫讓出 CPU
                __builtin_ia32_pause();  // CPU pause instruction
            }
        }
    }
    
    void order_thread_function(int cpu_id) {
        // 綁定到指定 CPU
        pin_thread_to_cpu(cpu_id);
        set_thread_name("Order_Thread");
        set_realtime_priority(97);
        
        cout << "Order thread running on CPU " << cpu_id << endl;
        
        Order order;
        
        while (running) {
            // 從隊列獲取訂單
            if (order_queue.pop(order)) {
                // 發送訂單 (模擬)
                send_order(order);
            } else {
                __builtin_ia32_pause();
            }
        }
    }
    
    Order generate_order(const MarketData& data) {
        Order order{};
        
        // 簡單的策略：價差套利
        double spread = data.ask_price - data.bid_price;
        double mid_price = (data.ask_price + data.bid_price) / 2.0;
        
        if (spread > 0.01 * mid_price) {  // 價差大於 1%
            order.order_id = generate_order_id();
            order.symbol_id = data.symbol_id;
            order.price = data.bid_price + 0.0001;
            order.quantity = min(data.bid_size, 100u);
            order.is_buy = true;
        }
        
        return order;
    }
    
    void send_order(const Order& order) {
        // 將訂單寫入訂單緩衝區
        if (order_offset + sizeof(Order) <= ORDER_BUFFER_SIZE) {
            memcpy(static_cast<char*>(order_buffer) + order_offset, &order, sizeof(Order));
            order_offset += sizeof(Order);
        }
        
        // 實際發送 (這裡僅模擬)
        // send(order_send_fd, &order, sizeof(order), MSG_DONTWAIT);
    }
    
    void warmup_system() {
        cout << "Warming up system..." << endl;
        
        // 預熱 CPU 快取
        volatile long sum = 0;
        for (size_t i = 0; i < MARKET_DATA_BUFFER_SIZE; i += 64) {
            sum += static_cast<char*>(market_data_buffer)[i];
        }
        
        // 預熱 TLB
        for (size_t i = 0; i < ORDER_BUFFER_SIZE; i += 4096) {
            static_cast<char*>(order_buffer)[i] = 0;
        }
        
        cout << "Warmup completed" << endl;
    }
    
    void print_statistics() {
        static auto last_print = steady_clock::now();
        auto now = steady_clock::now();
        auto duration = duration_cast<seconds>(now - last_print).count();
        
        if (duration >= 5) {
            cout << "\n=== System Statistics ===" << endl;
            cout << "Market data received: " << total_market_data << endl;
            cout << "Orders generated: " << total_orders << endl;
            
            if (total_orders > 0) {
                uint64_t avg_latency = total_latency_ns / total_orders;
                cout << "Average latency: " << avg_latency << " cycles" << endl;
            }
            
            cout << "Market data rate: " << total_market_data / duration << " msg/sec" << endl;
            cout << "Order rate: " << total_orders / duration << " orders/sec" << endl;
            
            last_print = now;
        }
    }
    
    // 輔助函數
    void set_nonblocking(int fd) {
        int flags = fcntl(fd, F_GETFL, 0);
        fcntl(fd, F_SETFL, flags | O_NONBLOCK);
    }
    
    void pin_thread_to_cpu(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    }
    
    void set_realtime_priority(int priority) {
        struct sched_param param;
        param.sched_priority = priority;
        
        if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
            cerr << "Warning: Failed to set realtime priority (need root)" << endl;
        }
    }
    
    void set_thread_name(const string& name) {
        pthread_setname_np(pthread_self(), name.c_str());
    }
    
    uint64_t rdtsc() {
        unsigned int lo, hi;
        __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64_t)hi << 32) | lo;
    }
    
    uint64_t generate_order_id() {
        static atomic<uint64_t> order_counter{1};
        return order_counter++;
    }
};

// 基準測試
class SystemBenchmark {
public:
    static void run_benchmarks() {
        cout << "\n=== Running System Benchmarks ===" << endl;
        
        // 測試大頁面 vs 標準頁面
        benchmark_memory_access();
        
        // 測試 CPU 親和性影響
        benchmark_cpu_affinity();
        
        // 測試無鎖隊列性能
        benchmark_lock_free_queue();
    }
    
private:
    static void benchmark_memory_access() {
        cout << "\n--- Memory Access Benchmark ---" << endl;
        
        const size_t size = 100 * 1024 * 1024;  // 100 MB
        
        // 標準頁面
        void* normal_mem = malloc(size);
        memset(normal_mem, 0, size);
        
        auto start = high_resolution_clock::now();
        volatile long sum = 0;
        for (size_t i = 0; i < size; i += 4096) {
            sum += static_cast<char*>(normal_mem)[i];
        }
        auto normal_time = high_resolution_clock::now() - start;
        
        free(normal_mem);
        
        // 大頁面
        void* huge_mem = mmap(nullptr, size, PROT_READ | PROT_WRITE,
                            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB, -1, 0);
        
        if (huge_mem != MAP_FAILED) {
            memset(huge_mem, 0, size);
            
            start = high_resolution_clock::now();
            sum = 0;
            for (size_t i = 0; i < size; i += 4096) {
                sum += static_cast<char*>(huge_mem)[i];
            }
            auto huge_time = high_resolution_clock::now() - start;
            
            munmap(huge_mem, size);
            
            cout << "Standard pages: " << duration_cast<microseconds>(normal_time).count() << " us" << endl;
            cout << "Huge pages: " << duration_cast<microseconds>(huge_time).count() << " us" << endl;
            cout << "Speedup: " << (double)normal_time.count() / huge_time.count() << "x" << endl;
        }
    }
    
    static void benchmark_cpu_affinity() {
        cout << "\n--- CPU Affinity Benchmark ---" << endl;
        
        const int iterations = 100000000;
        
        // 無親和性
        auto start = high_resolution_clock::now();
        double result = 1.0;
        for (int i = 0; i < iterations; i++) {
            result = result * 1.000001 + 0.000001;
        }
        auto no_affinity_time = high_resolution_clock::now() - start;
        
        // 有親和性
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(0, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        
        start = high_resolution_clock::now();
        result = 1.0;
        for (int i = 0; i < iterations; i++) {
            result = result * 1.000001 + 0.000001;
        }
        auto with_affinity_time = high_resolution_clock::now() - start;
        
        cout << "No CPU affinity: " << duration_cast<milliseconds>(no_affinity_time).count() << " ms" << endl;
        cout << "With CPU affinity: " << duration_cast<milliseconds>(with_affinity_time).count() << " ms" << endl;
    }
    
    static void benchmark_lock_free_queue() {
        cout << "\n--- Lock-Free Queue Benchmark ---" << endl;
        
        SPSCQueue<int, 1024> queue;
        const int iterations = 10000000;
        
        auto start = high_resolution_clock::now();
        
        thread producer([&queue, iterations]() {
            for (int i = 0; i < iterations; i++) {
                while (!queue.push(i)) {
                    __builtin_ia32_pause();
                }
            }
        });
        
        thread consumer([&queue, iterations]() {
            int value;
            for (int i = 0; i < iterations; i++) {
                while (!queue.pop(value)) {
                    __builtin_ia32_pause();
                }
            }
        });
        
        producer.join();
        consumer.join();
        
        auto duration = high_resolution_clock::now() - start;
        
        cout << "Processed " << iterations << " items in " 
             << duration_cast<milliseconds>(duration).count() << " ms" << endl;
        cout << "Throughput: " << (iterations * 1000) / duration_cast<milliseconds>(duration).count() 
             << " items/sec" << endl;
    }
};

int main(int argc, char* argv[]) {
    cout << "=== HFT Integrated System Demo ===" << endl;
    
    // 忽略 SIGPIPE
    signal(SIGPIPE, SIG_IGN);
    
    if (argc > 1 && string(argv[1]) == "benchmark") {
        SystemBenchmark::run_benchmarks();
        return 0;
    }
    
    try {
        // 創建並運行交易系統
        UltraLowLatencyTradingSystem trading_system;
        
        // 處理 Ctrl+C
        signal(SIGINT, [](int) {
            cout << "\nReceived shutdown signal..." << endl;
            exit(0);
        });
        
        // 運行系統
        trading_system.run();
        
    } catch (const exception& e) {
        cerr << "Error: " << e.what() << endl;
        return 1;
    }
    
    cout << "System shutdown complete" << endl;
    return 0;
}