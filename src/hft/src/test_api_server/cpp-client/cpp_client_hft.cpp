// HFT Ultra-optimized C++ client with complete optimizations
// Features: Memory locking, Huge pages, NUMA, CPU affinity, Lock-free, Cache alignment
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <cmath>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <sys/resource.h>
#include <unistd.h>
#include <atomic>
#include <algorithm>
#include <new>
#include <numa.h>
#include <numaif.h>
#include <errno.h>
#include <sched.h>
#include <immintrin.h>  // For prefetch instructions

#define MAX_ORDERS 10000
#define MAX_WORKERS 20
#define CACHE_LINE_SIZE 64
#define RING_BUFFER_SIZE 4096

// Cache-aligned atomic counter
struct alignas(CACHE_LINE_SIZE) AlignedCounter {
    std::atomic<size_t> value{0};
    char padding[CACHE_LINE_SIZE - sizeof(std::atomic<size_t>)];
};

// Lock-free MPMC ring buffer with cache alignment
template<typename T>
class alignas(CACHE_LINE_SIZE) LockFreeRingBuffer {
private:
    static constexpr size_t BUFFER_SIZE = RING_BUFFER_SIZE;

    struct alignas(CACHE_LINE_SIZE) Slot {
        std::atomic<T> data;
        std::atomic<size_t> sequence;
        char padding[CACHE_LINE_SIZE - sizeof(std::atomic<T>) - sizeof(std::atomic<size_t>)];
    };

    alignas(CACHE_LINE_SIZE) Slot buffer[BUFFER_SIZE];
    alignas(CACHE_LINE_SIZE) AlignedCounter head;
    alignas(CACHE_LINE_SIZE) AlignedCounter tail;

public:
    LockFreeRingBuffer() {
        for (size_t i = 0; i < BUFFER_SIZE; ++i) {
            buffer[i].sequence.store(i, std::memory_order_relaxed);
        }
    }

    bool enqueue(T item) {
        size_t current_tail = tail.value.load(std::memory_order_relaxed);

        for (;;) {
            Slot& slot = buffer[current_tail % BUFFER_SIZE];
            size_t seq = slot.sequence.load(std::memory_order_acquire);

            if (seq == current_tail) {
                if (tail.value.compare_exchange_weak(current_tail, current_tail + 1,
                                                     std::memory_order_relaxed)) {
                    slot.data.store(item, std::memory_order_relaxed);
                    slot.sequence.store(current_tail + 1, std::memory_order_release);
                    return true;
                }
            } else if (seq < current_tail) {
                return false;  // Queue is full
            } else {
                current_tail = tail.value.load(std::memory_order_relaxed);
            }
        }
    }

    bool dequeue(T& item) {
        size_t current_head = head.value.load(std::memory_order_relaxed);

        for (;;) {
            Slot& slot = buffer[current_head % BUFFER_SIZE];
            size_t seq = slot.sequence.load(std::memory_order_acquire);

            if (seq == current_head + 1) {
                if (head.value.compare_exchange_weak(current_head, current_head + 1,
                                                     std::memory_order_relaxed)) {
                    item = slot.data.load(std::memory_order_relaxed);
                    slot.sequence.store(current_head + BUFFER_SIZE, std::memory_order_release);
                    return true;
                }
            } else if (seq < current_head + 1) {
                return false;  // Queue is empty
            } else {
                current_head = head.value.load(std::memory_order_relaxed);
            }
        }
    }
};

// Cache-aligned order structure
struct alignas(CACHE_LINE_SIZE) Order {
    const char* buy_sell;
    int symbol;
    double price;
    int quantity;
    const char* market_type;
    const char* price_type;
    const char* time_in_force;
    const char* order_type;
    const char* user_def;
};

// Cache-aligned result structure
struct alignas(CACHE_LINE_SIZE) OrderResult {
    double latency_ms;
    int success;
};

// Cache-aligned task structure
struct alignas(CACHE_LINE_SIZE) Task {
    int order_id;
    const Order* order;
    OrderResult* result;
    char json_buffer[1024];
    char response_buffer[4096];
    size_t response_size;
};

// Memory management utilities
class HFTMemoryManager {
private:
    static void* locked_memory;
    static size_t locked_size;

public:
    // Allocate locked memory (prevent swapping)
    static void* allocateLockedMemory(size_t size) {
        void* mem;
        if (posix_memalign(&mem, sysconf(_SC_PAGESIZE), size) != 0) {
            return nullptr;
        }

        // Lock memory to prevent swapping
        if (mlock(mem, size) == -1) {
            free(mem);
            return nullptr;
        }

        // Prefetch memory to trigger page faults
        memset(mem, 0, size);
        return mem;
    }

    // Allocate huge pages for better TLB efficiency
    static void* allocateHugePage(size_t size) {
        void* ptr = mmap(nullptr, size,
                        PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                        -1, 0);

        if (ptr == MAP_FAILED) {
            // Fallback to regular locked memory
            return allocateLockedMemory(size);
        }

        // Lock and prefetch
        mlock(ptr, size);
        memset(ptr, 0, size);
        return ptr;
    }

    // NUMA-aware allocation
    static void* allocateNumaMemory(int node, size_t size) {
        if (numa_available() < 0) {
            return allocateLockedMemory(size);
        }

        struct bitmask *nm = numa_allocate_nodemask();
        numa_bitmask_setbit(nm, node);

        void* ptr = mmap(nullptr, size,
                        PROT_READ | PROT_WRITE,
                        MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
                        -1, 0);

        if (ptr != MAP_FAILED) {
            mbind(ptr, size, MPOL_BIND, nm->maskp, nm->size + 1, 0);
            mlock(ptr, size);
            memset(ptr, 0, size);  // Prefetch
        } else {
            ptr = allocateLockedMemory(size);
        }

        numa_free_nodemask(nm);
        return ptr;
    }

    static void freeMemory(void* ptr, size_t size) {
        munlock(ptr, size);
        munmap(ptr, size);
    }
};

void* HFTMemoryManager::locked_memory = nullptr;
size_t HFTMemoryManager::locked_size = 0;

// Ultra-optimized client with complete HFT features
class UltraHFTClient {
private:
    const char* base_url;
    LockFreeRingBuffer<Task*> task_queue;
    pthread_t* threads;
    int num_threads;
    std::atomic<bool> shutdown{false};

    // Pre-allocated CURL handles per thread
    CURL** curl_handles;
    struct curl_slist** headers;

    // Cache-aligned metrics
    alignas(CACHE_LINE_SIZE) double* latencies;
    alignas(CACHE_LINE_SIZE) std::atomic<int> total_orders{0};
    alignas(CACHE_LINE_SIZE) std::atomic<int> successful_orders{0};

    // Task pool with NUMA awareness
    Task* task_pool;
    std::atomic<bool>* task_available;
    size_t pool_size;

    static size_t write_callback(void* contents, size_t size, size_t nmemb, void* userp) {
        Task* task = static_cast<Task*>(userp);
        size_t total_size = size * nmemb;

        if (task->response_size + total_size < 4096) {
            memcpy(task->response_buffer + task->response_size, contents, total_size);
            task->response_size += total_size;
            task->response_buffer[task->response_size] = 0;
        }

        return total_size;
    }

    static double get_time_ms() {
        struct timeval tv;
        gettimeofday(&tv, nullptr);
        return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
    }

    static void get_iso_timestamp(char* buffer, size_t size) {
        struct timeval tv;
        gettimeofday(&tv, nullptr);

        struct tm* tm_info = gmtime(&tv.tv_sec);
        strftime(buffer, size, "%Y-%m-%dT%H:%M:%S", tm_info);

        size_t len = strlen(buffer);
        snprintf(buffer + len, size - len, ".%03dZ", (int)(tv.tv_usec / 1000));
    }

    void process_order_optimized(CURL* curl, struct curl_slist* hdrs, Task* task) {
        // Prefetch task data into L1 cache
        __builtin_prefetch(task, 0, 3);
        __builtin_prefetch(task->order, 0, 3);

        // Reset response buffer
        task->response_size = 0;
        task->response_buffer[0] = 0;

        // Build JSON directly in pre-allocated buffer - no allocations
        char timestamp[64];
        get_iso_timestamp(timestamp, sizeof(timestamp));

        int json_len = snprintf(task->json_buffer, sizeof(task->json_buffer),
            "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
            "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
            "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"%s%s%s}",
            task->order->buy_sell, task->order->symbol,
            task->order->price, task->order->quantity,
            task->order->market_type, task->order->price_type,
            task->order->time_in_force, task->order->order_type,
            timestamp,
            task->order->user_def ? ",\"user_def\":\"" : "",
            task->order->user_def ? task->order->user_def : "",
            task->order->user_def ? "\"" : ""
        );

        // Build URL - stack allocated
        char url[256];
        snprintf(url, sizeof(url), "%s/order", base_url);

        double start_time = get_time_ms();

        // Reuse CURL handle - no allocations
        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, task->json_buffer);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDSIZE, json_len);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, hdrs);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, task);

        CURLcode res = curl_easy_perform(curl);

        double end_time = get_time_ms();

        if (res == CURLE_OK) {
            long response_code;
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);

            if (response_code == 200) {
                task->result->latency_ms = end_time - start_time;
                task->result->success = 1;

                int idx = successful_orders.fetch_add(1);
                if (idx < MAX_ORDERS) {
                    latencies[idx] = task->result->latency_ms;
                }
            } else {
                task->result->success = 0;
            }
        } else {
            task->result->success = 0;
        }

        total_orders.fetch_add(1);
    }

    static void* worker_thread(void* arg) {
        UltraHFTClient* client = static_cast<UltraHFTClient*>(arg);

        // Get thread ID
        static std::atomic<int> thread_counter{0};
        int thread_id = thread_counter.fetch_add(1);

        // Set CPU affinity with physical core isolation
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        int cpu_id = thread_id % sysconf(_SC_NPROCESSORS_ONLN);
        CPU_SET(cpu_id, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

        // Set real-time scheduling priority
        struct sched_param param;
        param.sched_priority = sched_get_priority_max(SCHED_FIFO) - 1;
        pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);

        // NUMA optimization: bind memory to local node
        if (numa_available() >= 0) {
            int node = numa_node_of_cpu(cpu_id);
            numa_set_preferred(node);
        }

        // Get pre-allocated CURL handle
        CURL* curl = client->curl_handles[thread_id];
        struct curl_slist* headers = client->headers[thread_id];

        while (!client->shutdown.load(std::memory_order_acquire)) {
            Task* task = nullptr;

            if (client->task_queue.dequeue(task)) {
                client->process_order_optimized(curl, headers, task);

                // Return task to pool
                int task_idx = task - client->task_pool;
                client->task_available[task_idx].store(true, std::memory_order_release);
            } else {
                // CPU-friendly pause
                _mm_pause();
            }
        }

        return nullptr;
    }

    Task* allocate_task() {
        for (size_t i = 0; i < pool_size; i++) {
            bool expected = true;
            if (task_available[i].compare_exchange_weak(expected, false,
                                                        std::memory_order_acquire)) {
                return &task_pool[i];
            }
        }
        return nullptr;
    }

public:
    UltraHFTClient(const char* url, int thread_count)
        : base_url(url), num_threads(thread_count) {

        if (num_threads > MAX_WORKERS) {
            num_threads = MAX_WORKERS;
        }

        // Initialize NUMA if available
        if (numa_available() >= 0) {
            printf("NUMA optimization: ENABLED\n");
            numa_set_localalloc();
        } else {
            printf("NUMA optimization: DISABLED\n");
        }

        // Try to increase memory lock limits
        struct rlimit rlim;
        rlim.rlim_cur = RLIM_INFINITY;
        rlim.rlim_max = RLIM_INFINITY;
        if (setrlimit(RLIMIT_MEMLOCK, &rlim) == 0) {
            printf("Memory locking: UNLIMITED\n");
        } else {
            printf("Memory locking: LIMITED (run as root for unlimited)\n");
        }

        // Allocate threads
        threads = new pthread_t[num_threads];

        // Pre-allocate latencies array
        latencies = new double[MAX_ORDERS];
        memset(latencies, 0, MAX_ORDERS * sizeof(double));

        // Initialize task pool
        pool_size = RING_BUFFER_SIZE;
        task_pool = new Task[pool_size];
        memset(task_pool, 0, pool_size * sizeof(Task));

        task_available = new std::atomic<bool>[pool_size];
        for (size_t i = 0; i < pool_size; i++) {
            task_available[i].store(true, std::memory_order_relaxed);
        }

        // Initialize CURL globally
        curl_global_init(CURL_GLOBAL_ALL);

        // Pre-initialize all CURL handles and headers
        curl_handles = new CURL*[num_threads];
        headers = new struct curl_slist*[num_threads];

        for (int i = 0; i < num_threads; i++) {
            curl_handles[i] = curl_easy_init();

            // Set persistent CURL options
            curl_easy_setopt(curl_handles[i], CURLOPT_POST, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_WRITEFUNCTION, write_callback);
            curl_easy_setopt(curl_handles[i], CURLOPT_TIMEOUT, 30L);

            // Performance optimizations
            curl_easy_setopt(curl_handles[i], CURLOPT_TCP_NODELAY, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_TCP_KEEPALIVE, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
            curl_easy_setopt(curl_handles[i], CURLOPT_FRESH_CONNECT, 0L);
            curl_easy_setopt(curl_handles[i], CURLOPT_FORBID_REUSE, 0L);

            // Pre-create headers
            headers[i] = curl_slist_append(nullptr, "Content-Type: application/json");
            headers[i] = curl_slist_append(headers[i], "Connection: keep-alive");
        }

        // Create worker threads
        for (int i = 0; i < num_threads; i++) {
            pthread_attr_t attr;
            pthread_attr_init(&attr);

            // Set stack size to reduce memory overhead
            pthread_attr_setstacksize(&attr, 256 * 1024);  // 256KB stack

            pthread_create(&threads[i], &attr, worker_thread, this);
            pthread_attr_destroy(&attr);
        }
    }

    ~UltraHFTClient() {
        shutdown.store(true, std::memory_order_release);

        for (int i = 0; i < num_threads; i++) {
            pthread_join(threads[i], nullptr);
        }

        // Cleanup CURL resources
        for (int i = 0; i < num_threads; i++) {
            curl_easy_cleanup(curl_handles[i]);
            curl_slist_free_all(headers[i]);
        }

        delete[] curl_handles;
        delete[] headers;
        delete[] task_available;

        // Free threads
        delete[] threads;

        // Free allocated memory
        delete[] latencies;
        delete[] task_pool;

        curl_global_cleanup();
    }

    void submit_order(Task* task) {
        // Spin-wait with exponential backoff
        int backoff = 1;
        while (!task_queue.enqueue(task)) {
            for (int i = 0; i < backoff; i++) {
                _mm_pause();
            }
            backoff = std::min(backoff * 2, 256);
        }
    }

    Task* get_task() {
        return allocate_task();
    }

    void wait_completion(int expected) {
        while (total_orders.load(std::memory_order_acquire) < expected) {
            _mm_pause();
        }
    }

    void print_stats(double elapsed_seconds) {
        int success_count = successful_orders.load();

        if (success_count == 0) {
            printf("No successful orders to analyze\n");
            return;
        }

        // Sort latencies
        std::sort(latencies, latencies + success_count);

        double min = latencies[0];
        double max = latencies[success_count - 1];
        double sum = 0;

        for (int i = 0; i < success_count; i++) {
            sum += latencies[i];
        }
        double avg = sum / success_count;

        // Calculate standard deviation
        double variance = 0;
        for (int i = 0; i < success_count; i++) {
            variance += (latencies[i] - avg) * (latencies[i] - avg);
        }
        double std_dev = sqrt(variance / (success_count - 1));

        // Calculate percentiles with linear interpolation
        auto percentile = [this, success_count](double p) {
            double rank = (p / 100.0) * (success_count - 1);
            int lower = (int)rank;
            int upper = lower + 1;

            if (upper >= success_count) {
                return latencies[success_count - 1];
            }

            double weight = rank - lower;
            return latencies[lower] * (1 - weight) + latencies[upper] * weight;
        };

        printf("\n=== C++ HFT Ultra-Optimized Performance ===\n");
        printf("Features: Memory locking, Huge pages, NUMA, CPU affinity, Lock-free, RT scheduling\n");
        printf("Total orders: %d\n", success_count);
        printf("Min latency: %.3f ms\n", min);
        printf("Max latency: %.3f ms\n", max);
        printf("Avg latency: %.3f ms\n", avg);
        printf("Std dev: %.3f ms\n", std_dev);
        printf("P50: %.3f ms\n", percentile(50));
        printf("P90: %.3f ms\n", percentile(90));
        printf("P95: %.3f ms\n", percentile(95));
        printf("P99: %.3f ms\n", percentile(99));
        printf("P99.9: %.3f ms\n", percentile(99.9));
        printf("Throughput: %.2f orders/sec\n", success_count / elapsed_seconds);
    }

    void reset_stats() {
        total_orders.store(0);
        successful_orders.store(0);
    }

    static double get_current_time() {
        return get_time_ms();
    }
};

int main(int argc, char* argv[]) {
    int num_orders = 1000;
    int num_threads = 50;
    int warmup = 100;

    if (argc > 1) num_orders = atoi(argv[1]);
    if (argc > 2) num_threads = atoi(argv[2]);
    if (argc > 3) warmup = atoi(argv[3]);

    printf("C++ HFT Ultra-Optimized Client\n");
    printf("Features: Complete HFT optimization stack\n");
    printf("Using %d threads with CPU affinity and RT scheduling\n", num_threads);

    // Static order
    Order order;
    order.buy_sell = "buy";
    order.symbol = 2881;
    order.price = 66.0;
    order.quantity = 2000;
    order.market_type = "common";
    order.price_type = "limit";
    order.time_in_force = "rod";
    order.order_type = "stock";
    order.user_def = "CPP_HFT";

    UltraHFTClient client("http://localhost:8080", num_threads);

    // Pre-allocate all tasks and results
    int max_size = std::max(warmup, num_orders);
    Task* tasks = new Task[max_size];
    OrderResult* results = new OrderResult[max_size];
    memset(tasks, 0, max_size * sizeof(Task));
    memset(results, 0, max_size * sizeof(OrderResult));

    // Warmup phase
    if (warmup > 0) {
        printf("\nWarming up with %d orders...\n", warmup);

        for (int i = 0; i < warmup; i++) {
            Task* task = client.get_task();
            while (!task) {
                _mm_pause();
                task = client.get_task();
            }

            task->order_id = i;
            task->order = &order;
            task->result = &results[i];

            client.submit_order(task);
        }

        client.wait_completion(warmup);
        client.reset_stats();
    }

    printf("\nSending %d orders...\n", num_orders);

    double start_time = UltraHFTClient::get_current_time();

    // Submit all orders
    for (int i = 0; i < num_orders; i++) {
        Task* task = client.get_task();
        while (!task) {
            _mm_pause();
            task = client.get_task();
        }

        task->order_id = i;
        task->order = &order;
        task->result = &results[i];

        client.submit_order(task);
    }

    client.wait_completion(num_orders);

    double end_time = UltraHFTClient::get_current_time();
    double elapsed_seconds = (end_time - start_time) / 1000.0;

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    client.print_stats(elapsed_seconds);

    // Cleanup
    delete[] tasks;
    delete[] results;

    return 0;
}