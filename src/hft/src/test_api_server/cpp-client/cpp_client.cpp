// Ultra-optimized C++ client - approaching C performance
// Uses Zero-copy, Lock-free queue, Pre-allocation, CPU affinity
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <cmath>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <unistd.h>
#include <atomic>
#include <algorithm>
#include <new>

#ifdef __linux__
#include <sched.h>
#endif

#define MAX_ORDERS 10000
#define MAX_WORKERS 20
#define RING_BUFFER_SIZE 2048

// Simple lock-free SPSC (Single Producer Single Consumer) ring buffer
template<typename T>
class LockFreeQueue {
private:
    static constexpr size_t QUEUE_SIZE = 4096;
    alignas(64) T buffer[QUEUE_SIZE];
    alignas(64) std::atomic<size_t> head{0};
    alignas(64) std::atomic<size_t> tail{0};

public:
    LockFreeQueue() = default;

    bool enqueue(T item) {
        size_t current_tail = tail.load(std::memory_order_relaxed);
        size_t next_tail = (current_tail + 1) % QUEUE_SIZE;

        if (next_tail == head.load(std::memory_order_acquire)) {
            return false;  // Queue is full
        }

        buffer[current_tail] = item;
        tail.store(next_tail, std::memory_order_release);
        return true;
    }

    bool dequeue(T& item) {
        size_t current_head = head.load(std::memory_order_relaxed);

        if (current_head == tail.load(std::memory_order_acquire)) {
            return false;  // Queue is empty
        }

        item = buffer[current_head];
        head.store((current_head + 1) % QUEUE_SIZE, std::memory_order_release);
        return true;
    }
};

// Raw C-style structures - no std::string
struct Order {
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

struct OrderResult {
    double latency_ms;
    int success;
};

// Pre-allocated task structure
struct Task {
    int order_id;
    const Order* order;
    OrderResult* result;
    char json_buffer[1024];     // Pre-allocated JSON buffer
    char response_buffer[4096]; // Pre-allocated response
    size_t response_size;
};

class UltraOptimizedClient {
private:
    const char* base_url;
    LockFreeQueue<Task*> task_queue;
    pthread_t* threads;
    int num_threads;
    std::atomic<bool> shutdown{false};

    // Pre-allocated CURL handles per thread
    CURL** curl_handles;
    struct curl_slist** headers;

    // Global metrics
    double* latencies;
    std::atomic<int> total_orders{0};
    std::atomic<int> successful_orders{0};

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

    // Zero-copy order processing
    void process_order_zerocopy(CURL* curl, struct curl_slist* hdrs, Task* task) {
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
        UltraOptimizedClient* client = static_cast<UltraOptimizedClient*>(arg);

        // Get thread ID for CPU affinity and CURL handle indexing
        static std::atomic<int> thread_counter{0};
        int thread_id = thread_counter.fetch_add(1);

#ifdef __linux__
        // Set CPU affinity
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(thread_id % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
#endif

        // Get pre-allocated CURL handle for this thread
        CURL* curl = client->curl_handles[thread_id];
        struct curl_slist* headers = client->headers[thread_id];

        while (!client->shutdown.load()) {
            Task* task = nullptr;

            if (client->task_queue.dequeue(task)) {
                // Process with zero-copy
                client->process_order_zerocopy(curl, headers, task);
            } else {
                usleep(100); // Brief sleep when queue is empty
            }
        }

        return nullptr;
    }

public:
    UltraOptimizedClient(const char* url, int threads)
        : base_url(url), num_threads(threads) {

        if (num_threads > MAX_WORKERS) {
            num_threads = MAX_WORKERS;
        }

        // Allocate thread array
        this->threads = new pthread_t[num_threads];

        // Pre-allocate latencies array
        latencies = new double[MAX_ORDERS];

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
            pthread_create(&this->threads[i], nullptr, worker_thread, this);
        }
    }

    ~UltraOptimizedClient() {
        shutdown.store(true);

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
        delete[] threads;
        delete[] latencies;

        curl_global_cleanup();
    }

    void submit_order(Task* task) {
        while (!task_queue.enqueue(task)) {
            usleep(100);  // Wait if queue is full
        }
    }

    void wait_completion(int expected) {
        while (total_orders.load() < expected) {
            usleep(1000);
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

        // Calculate percentiles
        auto percentile = [this, success_count](int p) {
            int idx = (success_count * p) / 100;
            if (idx >= success_count) idx = success_count - 1;
            return latencies[idx];
        };

        printf("\n=== C++ Ultra-Optimized Performance ===\n");
        printf("Zero-copy, Lock-free, CPU affinity, Pre-allocated\n");
        printf("Total orders: %d\n", success_count);
        printf("Min latency: %.2f ms\n", min);
        printf("Max latency: %.2f ms\n", max);
        printf("Avg latency: %.2f ms\n", avg);
        printf("P50: %.2f ms\n", percentile(50));
        printf("P90: %.2f ms\n", percentile(90));
        printf("P95: %.2f ms\n", percentile(95));
        printf("P99: %.2f ms\n", percentile(99));
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

    printf("C++ Ultra-Optimized - Approaching C Performance\n");
    printf("Using %d threads with CPU affinity\n", num_threads);

    // Static order - no allocations
    Order order = {
        "buy",          // buy_sell
        2881,           // symbol
        66.0,           // price
        2000,           // quantity
        "common",       // market_type
        "limit",        // price_type
        "rod",          // time_in_force
        "stock",        // order_type
        "CPP_ULTRA"     // user_def
    };

    UltraOptimizedClient client("http://localhost:8080", num_threads);

    // Pre-allocate all tasks and results
    Task* warmup_tasks = new Task[warmup];
    OrderResult* warmup_results = new OrderResult[warmup];

    Task* tasks = new Task[num_orders];
    OrderResult* results = new OrderResult[num_orders];

    // Initialize tasks
    for (int i = 0; i < warmup; i++) {
        warmup_tasks[i].order_id = i;
        warmup_tasks[i].order = &order;
        warmup_tasks[i].result = &warmup_results[i];
    }

    for (int i = 0; i < num_orders; i++) {
        tasks[i].order_id = i;
        tasks[i].order = &order;
        tasks[i].result = &results[i];
    }

    // Warmup
    if (warmup > 0) {
        printf("\nWarming up with %d orders...\n", warmup);

        for (int i = 0; i < warmup; i++) {
            client.submit_order(&warmup_tasks[i]);
        }

        client.wait_completion(warmup);
        client.reset_stats();
    }

    printf("\nSending %d orders...\n", num_orders);

    double start_time = UltraOptimizedClient::get_current_time();

    // Submit all orders
    for (int i = 0; i < num_orders; i++) {
        client.submit_order(&tasks[i]);
    }

    client.wait_completion(num_orders);

    double end_time = UltraOptimizedClient::get_current_time();
    double elapsed_seconds = (end_time - start_time) / 1000.0;

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    client.print_stats(elapsed_seconds);

    // Cleanup
    delete[] warmup_tasks;
    delete[] warmup_results;
    delete[] tasks;
    delete[] results;

    return 0;
}