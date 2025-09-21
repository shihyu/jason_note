#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <curl/curl.h>
#include <atomic>
#include <sched.h>
#include <sys/mman.h>
#include <numa.h>
#include <immintrin.h>
#include <x86intrin.h>
#include <unistd.h>

using namespace std::chrono;

// CPU Core configuration
constexpr int TRADING_CORE_START = 8;  // Start of isolated cores for trading
constexpr int TRADING_CORE_END = 15;   // End of isolated cores
constexpr int NUMA_NODE = 0;           // NUMA node to bind to

// Memory configuration
constexpr size_t CACHE_LINE_SIZE = 64;
constexpr size_t HUGEPAGE_SIZE = 2 * 1024 * 1024; // 2MB
constexpr size_t MEMORY_POOL_SIZE = 16 * 1024 * 1024; // 16MB

enum class BSAction {
    Buy,
    Sell
};

enum class MarketType {
    Common,
    Warrant,
    OddLot,
    Daytime,
    FixedPrice,
    PlaceFirst
};

enum class PriceType {
    Limit,
    Market,
    LimitUp,
    LimitDown,
    Range
};

enum class TimeInForce {
    ROD,
    IOC,
    FOK
};

enum class OrderType {
    Stock,
    Futures,
    Option
};

// Cache-line aligned order structure to prevent false sharing
struct alignas(CACHE_LINE_SIZE) Order {
    BSAction buy_sell;
    int symbol;
    double price;
    int quantity;
    MarketType market_type;
    PriceType price_type;
    TimeInForce time_in_force;
    OrderType order_type;
    char user_def[32];  // Fixed size for better memory layout
    char padding[8];    // Ensure cache line alignment
};

// Cache-line aligned statistics per thread
struct alignas(CACHE_LINE_SIZE) ThreadStats {
    std::atomic<uint64_t> processed{0};
    std::atomic<uint64_t> errors{0};
    double* latencies;           // Pre-allocated array
    size_t latency_count{0};
    size_t latency_capacity;
    char padding[CACHE_LINE_SIZE - 40]; // Padding to fill cache line
};

// Memory allocator for hugepage and locked memory
class HFTMemoryAllocator {
private:
    void* memory_pool;
    size_t pool_size;
    size_t allocated;
    std::mutex alloc_mutex;

public:
    HFTMemoryAllocator(size_t size = MEMORY_POOL_SIZE) : pool_size(size), allocated(0) {
        // Allocate hugepage memory
        int flags = MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB;
        int prot = PROT_READ | PROT_WRITE;
        memory_pool = mmap(nullptr, pool_size, prot, flags, -1, 0);

        if (memory_pool == MAP_FAILED) {
            // Fallback to regular pages
            memory_pool = mmap(nullptr, pool_size, prot, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
            if (memory_pool == MAP_FAILED) {
                throw std::runtime_error("Failed to allocate memory pool");
            }
        }

        // Lock memory to prevent swapping
        if (mlock(memory_pool, pool_size) != 0) {
            std::cerr << "Warning: Failed to lock memory (requires CAP_IPC_LOCK or root)\n";
        }

        // Prefault pages by touching them
        memset(memory_pool, 0, pool_size);
    }

    ~HFTMemoryAllocator() {
        if (memory_pool != MAP_FAILED) {
            munlock(memory_pool, pool_size);
            munmap(memory_pool, pool_size);
        }
    }

    void* allocate(size_t size, size_t alignment = CACHE_LINE_SIZE) {
        std::lock_guard<std::mutex> lock(alloc_mutex);

        // Align the allocation
        size_t aligned_size = (size + alignment - 1) & ~(alignment - 1);
        size_t aligned_offset = (allocated + alignment - 1) & ~(alignment - 1);

        if (aligned_offset + aligned_size > pool_size) {
            return nullptr;
        }

        void* ptr = static_cast<char*>(memory_pool) + aligned_offset;
        allocated = aligned_offset + aligned_size;
        return ptr;
    }
};

// Thread-local resources with CPU affinity
thread_local CURL* tls_curl = nullptr;
thread_local struct curl_slist* tls_headers = nullptr;
thread_local char* tls_response_buffer = nullptr;
thread_local char* tls_json_buffer = nullptr;
thread_local int tls_cpu_id = -1;

class HFTThreadPoolClient {
private:
    std::string base_url;
    std::vector<ThreadStats*> thread_stats;
    std::vector<std::thread> thread_pool;
    std::deque<std::pair<int, Order*>> work_queue;
    std::mutex queue_mutex;
    std::condition_variable cv;
    std::atomic<bool> stop_flag{false};
    std::atomic<int> active_workers{0};
    HFTMemoryAllocator allocator;
    int num_threads;

    // Pre-allocated order pool
    Order* order_pool;
    std::atomic<size_t> order_index{0};

    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
        // Direct copy to pre-allocated buffer
        char* buffer = static_cast<char*>(userp);
        size_t total_size = size * nmemb;
        if (total_size > 4096) total_size = 4096; // Prevent overflow
        memcpy(buffer, contents, total_size);
        buffer[total_size] = '\0';
        return size * nmemb;
    }

    // High-precision timestamp using RDTSC
    inline uint64_t rdtsc() {
        return __rdtsc();
    }

    std::string get_iso_timestamp() {
        auto now = system_clock::now();
        auto time_t = system_clock::to_time_t(now);
        auto us = duration_cast<microseconds>(now.time_since_epoch()) % 1000000;

        char buffer[64];
        struct tm tm_info;
        gmtime_r(&time_t, &tm_info);
        strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &tm_info);

        char final_buffer[128];
        snprintf(final_buffer, sizeof(final_buffer), "%s.%06ldZ", buffer, us.count());

        return std::string(final_buffer);
    }

    constexpr const char* enum_to_string(BSAction action) {
        return action == BSAction::Buy ? "buy" : "sell";
    }

    constexpr const char* enum_to_string(MarketType type) {
        switch (type) {
            case MarketType::Common: return "common";
            case MarketType::Warrant: return "warrant";
            case MarketType::OddLot: return "odd_lot";
            case MarketType::Daytime: return "daytime";
            case MarketType::FixedPrice: return "fixed_price";
            case MarketType::PlaceFirst: return "place_first";
            default: return "common";
        }
    }

    constexpr const char* enum_to_string(PriceType type) {
        switch (type) {
            case PriceType::Limit: return "limit";
            case PriceType::Market: return "market";
            case PriceType::LimitUp: return "limit_up";
            case PriceType::LimitDown: return "limit_down";
            case PriceType::Range: return "range";
            default: return "limit";
        }
    }

    constexpr const char* enum_to_string(TimeInForce tif) {
        switch (tif) {
            case TimeInForce::ROD: return "rod";
            case TimeInForce::IOC: return "ioc";
            case TimeInForce::FOK: return "fok";
            default: return "rod";
        }
    }

    constexpr const char* enum_to_string(OrderType type) {
        switch (type) {
            case OrderType::Stock: return "stock";
            case OrderType::Futures: return "futures";
            case OrderType::Option: return "option";
            default: return "stock";
        }
    }

    void pin_thread_to_cpu(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);

        if (pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset) != 0) {
            std::cerr << "Warning: Failed to set CPU affinity for CPU " << cpu_id << "\n";
        }

        // Set real-time scheduling priority (requires CAP_SYS_NICE or root)
        struct sched_param param;
        param.sched_priority = sched_get_priority_max(SCHED_FIFO);
        if (pthread_setschedparam(pthread_self(), SCHED_FIFO, &param) != 0) {
            // Try with lower priority
            param.sched_priority = 1;
            pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
        }
    }

    void worker_thread(int thread_id) {
        // Pin to specific CPU core
        int cpu_id = TRADING_CORE_START + (thread_id % (TRADING_CORE_END - TRADING_CORE_START + 1));
        pin_thread_to_cpu(cpu_id);
        tls_cpu_id = cpu_id;

        // Set NUMA memory policy
        if (numa_available() >= 0) {
            numa_set_localalloc();
            numa_run_on_node(NUMA_NODE);
        }

        // Allocate thread-local buffers from locked memory pool
        tls_response_buffer = static_cast<char*>(allocator.allocate(4096));
        tls_json_buffer = static_cast<char*>(allocator.allocate(2048));

        if (!tls_response_buffer || !tls_json_buffer) {
            std::cerr << "Failed to allocate thread-local buffers\n";
            return;
        }

        // Initialize thread-local CURL handle
        tls_curl = curl_easy_init();
        if (!tls_curl) return;

        // Set persistent options
        std::string url = base_url + "/order";
        curl_easy_setopt(tls_curl, CURLOPT_URL, url.c_str());
        curl_easy_setopt(tls_curl, CURLOPT_POST, 1L);
        curl_easy_setopt(tls_curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(tls_curl, CURLOPT_WRITEDATA, tls_response_buffer);

        // Aggressive performance optimizations
        curl_easy_setopt(tls_curl, CURLOPT_TCP_NODELAY, 1L);
        curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPALIVE, 1L);
        curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPIDLE, 60L);
        curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPINTVL, 30L);
        curl_easy_setopt(tls_curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
        curl_easy_setopt(tls_curl, CURLOPT_FRESH_CONNECT, 0L);
        curl_easy_setopt(tls_curl, CURLOPT_FORBID_REUSE, 0L);
        curl_easy_setopt(tls_curl, CURLOPT_TIMEOUT_MS, 5000L);
        curl_easy_setopt(tls_curl, CURLOPT_CONNECTTIMEOUT_MS, 1000L);

        // Disable unnecessary features
        curl_easy_setopt(tls_curl, CURLOPT_SSL_VERIFYPEER, 0L);
        curl_easy_setopt(tls_curl, CURLOPT_SSL_VERIFYHOST, 0L);
        curl_easy_setopt(tls_curl, CURLOPT_FOLLOWLOCATION, 0L);
        curl_easy_setopt(tls_curl, CURLOPT_NOSIGNAL, 1L);

        // Pre-create headers
        tls_headers = curl_slist_append(nullptr, "Content-Type: application/json");
        tls_headers = curl_slist_append(tls_headers, "Connection: keep-alive");
        tls_headers = curl_slist_append(tls_headers, "Expect:");  // Disable 100-continue
        curl_easy_setopt(tls_curl, CURLOPT_HTTPHEADER, tls_headers);

        ThreadStats* stats = thread_stats[thread_id];

        while (!stop_flag.load(std::memory_order_acquire)) {
            std::pair<int, Order*> work;

            {
                std::unique_lock<std::mutex> lock(queue_mutex);
                cv.wait_for(lock, std::chrono::microseconds(100),
                           [this] { return !work_queue.empty() || stop_flag.load(std::memory_order_acquire); });

                if (stop_flag.load(std::memory_order_acquire)) break;
                if (work_queue.empty()) continue;

                work = work_queue.front();
                work_queue.pop_front();
                active_workers.fetch_add(1, std::memory_order_acq_rel);
            }

            // Process with minimal latency
            process_order(work.first, work.second, stats);
            active_workers.fetch_sub(1, std::memory_order_acq_rel);
        }

        // Cleanup
        if (tls_headers) {
            curl_slist_free_all(tls_headers);
            tls_headers = nullptr;
        }
        if (tls_curl) {
            curl_easy_cleanup(tls_curl);
            tls_curl = nullptr;
        }
    }

    void process_order(int order_id, const Order* order, ThreadStats* stats) {
        if (!tls_curl || !order) return;

        // Clear response buffer
        memset(tls_response_buffer, 0, 128); // Only clear what we need

        // Build JSON with minimal allocations
        std::string timestamp = get_iso_timestamp();

        int json_len = snprintf(tls_json_buffer, 2048,
            "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
            "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
            "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"%s%s%s}",
            enum_to_string(order->buy_sell),
            order->symbol,
            order->price,
            order->quantity,
            enum_to_string(order->market_type),
            enum_to_string(order->price_type),
            enum_to_string(order->time_in_force),
            enum_to_string(order->order_type),
            timestamp.c_str(),
            strlen(order->user_def) > 0 ? ",\"user_def\":\"" : "",
            strlen(order->user_def) > 0 ? order->user_def : "",
            strlen(order->user_def) > 0 ? "\"" : ""
        );

        curl_easy_setopt(tls_curl, CURLOPT_POSTFIELDS, tls_json_buffer);
        curl_easy_setopt(tls_curl, CURLOPT_POSTFIELDSIZE, json_len);

        // Use RDTSC for ultra-low overhead timing
        uint64_t start_tsc = rdtsc();
        auto start_time = high_resolution_clock::now();

        CURLcode res = curl_easy_perform(tls_curl);

        auto end_time = high_resolution_clock::now();
        uint64_t end_tsc = rdtsc();

        if (res == CURLE_OK) {
            long http_code = 0;
            curl_easy_getinfo(tls_curl, CURLINFO_RESPONSE_CODE, &http_code);

            if (http_code == 200) {
                double latency = duration<double, std::milli>(end_time - start_time).count();

                // Store latency without lock
                if (stats->latency_count < stats->latency_capacity) {
                    stats->latencies[stats->latency_count++] = latency;
                }
                stats->processed.fetch_add(1, std::memory_order_relaxed);
            } else {
                stats->errors.fetch_add(1, std::memory_order_relaxed);
            }
        } else {
            stats->errors.fetch_add(1, std::memory_order_relaxed);
        }
    }

public:
    HFTThreadPoolClient(const std::string& url = "http://localhost:8080", int threads = 8)
        : base_url(url), num_threads(threads), allocator(MEMORY_POOL_SIZE) {

        curl_global_init(CURL_GLOBAL_ALL);

        // Pre-allocate order pool
        order_pool = static_cast<Order*>(allocator.allocate(sizeof(Order) * 100000));
        if (!order_pool) {
            throw std::runtime_error("Failed to allocate order pool");
        }

        // Initialize thread statistics
        thread_stats.reserve(num_threads);
        for (int i = 0; i < num_threads; i++) {
            ThreadStats* stats = static_cast<ThreadStats*>(allocator.allocate(sizeof(ThreadStats)));
            if (!stats) {
                throw std::runtime_error("Failed to allocate thread stats");
            }
            new (stats) ThreadStats();  // Placement new
            stats->latency_capacity = 10000;
            stats->latencies = static_cast<double*>(allocator.allocate(sizeof(double) * stats->latency_capacity));
            thread_stats.push_back(stats);
        }

        // Create worker threads
        for (int i = 0; i < num_threads; i++) {
            thread_pool.emplace_back(&HFTThreadPoolClient::worker_thread, this, i);
        }

        // Wait for threads to initialize
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }

    ~HFTThreadPoolClient() {
        stop_flag.store(true, std::memory_order_release);
        cv.notify_all();

        for (auto& t : thread_pool) {
            if (t.joinable()) {
                t.join();
            }
        }

        curl_global_cleanup();
    }

    void submit_order(int order_id, const Order& order) {
        // Copy to pre-allocated pool
        size_t idx = order_index.fetch_add(1, std::memory_order_relaxed) % 100000;
        Order* pool_order = &order_pool[idx];
        *pool_order = order;

        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            work_queue.emplace_back(order_id, pool_order);
        }
        cv.notify_one();
    }

    void wait_completion() {
        while (true) {
            {
                std::lock_guard<std::mutex> lock(queue_mutex);
                if (work_queue.empty() && active_workers.load(std::memory_order_acquire) == 0) {
                    break;
                }
            }
            std::this_thread::yield();  // Better than sleep for low latency
        }
    }

    void print_stats() {
        // Aggregate all thread statistics
        std::vector<double> all_latencies;
        uint64_t total_processed = 0;
        uint64_t total_errors = 0;

        for (auto* stats : thread_stats) {
            total_processed += stats->processed.load(std::memory_order_relaxed);
            total_errors += stats->errors.load(std::memory_order_relaxed);

            for (size_t i = 0; i < stats->latency_count; i++) {
                all_latencies.push_back(stats->latencies[i]);
            }
        }

        if (all_latencies.empty()) {
            std::cout << "No successful orders to analyze\n";
            std::cout << "Total errors: " << total_errors << "\n";
            return;
        }

        // Use SIMD for fast sorting if available
        std::sort(all_latencies.begin(), all_latencies.end());

        double min_lat = all_latencies.front();
        double max_lat = all_latencies.back();

        // SIMD-accelerated sum calculation
        double sum = 0;
        size_t i = 0;

        // Process 4 doubles at a time using AVX
        for (; i + 3 < all_latencies.size(); i += 4) {
            __m256d vec = _mm256_loadu_pd(&all_latencies[i]);
            __m256d sum_vec = _mm256_hadd_pd(vec, vec);
            sum += sum_vec[0] + sum_vec[2];
        }

        // Process remaining elements
        for (; i < all_latencies.size(); i++) {
            sum += all_latencies[i];
        }

        double avg_lat = sum / all_latencies.size();

        std::cout << "\n=== HFT C++ Client Performance ===\n";
        std::cout << "CPU Cores: " << TRADING_CORE_START << "-" << TRADING_CORE_END << " (isolated)\n";
        std::cout << "NUMA Node: " << NUMA_NODE << "\n";
        std::cout << "Memory: Locked hugepages with prefaulting\n";
        std::cout << "Total orders: " << total_processed << "\n";
        std::cout << "Total errors: " << total_errors << "\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Min latency: " << min_lat << " ms\n";
        std::cout << "Max latency: " << max_lat << " ms\n";
        std::cout << "Avg latency: " << avg_lat << " ms\n";

        // Calculate percentiles
        auto percentile = [&all_latencies](int p) {
            size_t index = (all_latencies.size() * p) / 100;
            if (index >= all_latencies.size()) index = all_latencies.size() - 1;
            return all_latencies[index];
        };

        std::cout << "P50: " << percentile(50) << " ms\n";
        std::cout << "P90: " << percentile(90) << " ms\n";
        std::cout << "P95: " << percentile(95) << " ms\n";
        std::cout << "P99: " << percentile(99) << " ms\n";

        // Calculate jitter (standard deviation)
        double variance = 0;
        for (const auto& lat : all_latencies) {
            variance += (lat - avg_lat) * (lat - avg_lat);
        }
        double stddev = std::sqrt(variance / all_latencies.size());
        std::cout << "Jitter (StdDev): " << stddev << " ms\n";
    }
};

void run_test(int num_orders = 1000, int num_threads = 8, int warmup = 100) {
    Order demo_order = {};
    demo_order.buy_sell = BSAction::Buy;
    demo_order.symbol = 2881;
    demo_order.price = 66.0;
    demo_order.quantity = 2000;
    demo_order.market_type = MarketType::Common;
    demo_order.price_type = PriceType::Limit;
    demo_order.time_in_force = TimeInForce::ROD;
    demo_order.order_type = OrderType::Stock;
    strncpy(demo_order.user_def, "HFT_CPP", sizeof(demo_order.user_def) - 1);

    // Use fewer threads for HFT (one per isolated core)
    int hft_threads = std::min(num_threads, TRADING_CORE_END - TRADING_CORE_START + 1);

    HFTThreadPoolClient client("http://localhost:8080", hft_threads);

    // Warmup phase - critical for HFT
    if (warmup > 0) {
        std::cout << "Warming up with " << warmup << " orders...\n";
        for (int i = 0; i < warmup; i++) {
            client.submit_order(i, demo_order);
        }
        client.wait_completion();
        // Note: We don't clear warmup results in HFT version to get full picture
    }

    std::cout << "\nHFT C++ Client - Core isolation, NUMA optimization, locked memory\n";
    std::cout << "Sending " << num_orders << " orders with " << hft_threads << " threads...\n";

    auto start_time = high_resolution_clock::now();

    // Submit orders in batches to reduce lock contention
    const int batch_size = 100;
    for (int i = 0; i < num_orders; i += batch_size) {
        int batch_end = std::min(i + batch_size, num_orders);
        for (int j = i; j < batch_end; j++) {
            client.submit_order(j, demo_order);
        }
        // Small yield to prevent queue overflow
        if ((i / batch_size) % 10 == 0) {
            std::this_thread::yield();
        }
    }

    client.wait_completion();

    auto end_time = high_resolution_clock::now();
    double total_time = duration<double>(end_time - start_time).count();

    std::cout << "\nCompleted in " << std::fixed << std::setprecision(2)
              << total_time << " seconds\n";
    std::cout << "Throughput: " << (num_orders / total_time) << " orders/sec\n";

    client.print_stats();
}

int main(int argc, char* argv[]) {
    int num_orders = 1000;
    int num_threads = 8;  // Default to fewer threads for HFT
    int warmup = 100;

    if (argc > 1) num_orders = std::stoi(argv[1]);
    if (argc > 2) num_threads = std::stoi(argv[2]);
    if (argc > 3) warmup = std::stoi(argv[3]);

    // Check if running with appropriate privileges
    if (geteuid() != 0) {
        std::cout << "Note: Running without root privileges. Some optimizations may be limited.\n";
        std::cout << "For best performance, run with: sudo ./cpp_client_hft\n\n";
    }

    run_test(num_orders, num_threads, warmup);

    return 0;
}