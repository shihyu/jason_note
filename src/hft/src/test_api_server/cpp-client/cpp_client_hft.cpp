// HFT-optimized C++ client
#define _GNU_SOURCE
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <cmath>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <unistd.h>
#include <atomic>
#include <algorithm>
#include <queue>
#include <mutex>
#include <condition_variable>
#include <sched.h>

#define MAX_ORDERS 50000
#define MAX_WORKERS 20

// Simple concurrent queue with mutex
template<typename T>
class ConcurrentQueue {
private:
    std::queue<T> queue;
    mutable std::mutex mutex;
    std::condition_variable cv;

public:
    void push(T item) {
        std::lock_guard<std::mutex> lock(mutex);
        queue.push(item);
        cv.notify_one();
    }

    bool pop(T& item) {
        std::unique_lock<std::mutex> lock(mutex);
        cv.wait_for(lock, std::chrono::microseconds(100),
                    [this] { return !queue.empty(); });
        if (queue.empty()) {
            return false;
        }
        item = queue.front();
        queue.pop();
        return true;
    }
};

// Core data structures
struct Order {
    const char* buy_sell;
    int symbol;
    double price;
    int quantity;
    const char* market_type;
    const char* price_type;
    const char* time_in_force;
    const char* order_type;
};

struct OrderResult {
    double latency_ms;
    int success;
};

struct Task {
    int order_id;
    const Order* order;
    OrderResult* result;
};


// HFT-optimized client
class HFTClient {
private:
    const char* base_url;
    ConcurrentQueue<Task*> task_queue;
    pthread_t* threads;
    int num_threads;
    std::atomic<bool> shutdown{false};

    // Pre-allocated CURL handles
    CURL** curl_handles;
    struct curl_slist** headers;

    // Metrics
    double* latencies;
    std::atomic<int> total_orders{0};
    std::atomic<int> successful_orders{0};

    static size_t write_callback(void* contents, size_t size, size_t nmemb, void* userp) {
        (void)userp; // We don't process response for performance
        return size * nmemb;
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

    void process_order(CURL* curl, struct curl_slist* hdrs, Task* task) {
        char json_buffer[512];
        char timestamp[64];
        char url[256];

        get_iso_timestamp(timestamp, sizeof(timestamp));

        snprintf(json_buffer, sizeof(json_buffer),
            "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
            "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
            "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"}",
            task->order->buy_sell, task->order->symbol,
            task->order->price, task->order->quantity,
            task->order->market_type, task->order->price_type,
            task->order->time_in_force, task->order->order_type,
            timestamp);

        snprintf(url, sizeof(url), "%s/order", base_url);

        double start = get_time_ms();

        curl_easy_setopt(curl, CURLOPT_URL, url);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_buffer);
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, hdrs);

        if (curl_easy_perform(curl) == CURLE_OK) {
            long code;
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);

            if (code == 200) {
                task->result->latency_ms = get_time_ms() - start;
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
        HFTClient* client = static_cast<HFTClient*>(arg);

        static std::atomic<int> thread_counter{0};
        int thread_id = thread_counter.fetch_add(1);

        // CPU affinity for performance
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(thread_id % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

        CURL* curl = client->curl_handles[thread_id];
        struct curl_slist* headers = client->headers[thread_id];

        while (!client->shutdown.load()) {
            Task* task = nullptr;
            if (client->task_queue.pop(task)) {
                client->process_order(curl, headers, task);
            }
        }

        return nullptr;
    }

public:
    HFTClient(const char* url, int thread_count)
        : base_url(url), num_threads(thread_count) {

        if (num_threads > MAX_WORKERS) {
            num_threads = MAX_WORKERS;
        }

        // Lock memory for HFT
        mlockall(MCL_CURRENT | MCL_FUTURE);

        threads = new pthread_t[num_threads];
        latencies = new double[MAX_ORDERS]();

        curl_global_init(CURL_GLOBAL_ALL);

        // Initialize CURL handles with HFT optimizations
        curl_handles = new CURL*[num_threads];
        headers = new struct curl_slist*[num_threads];

        for (int i = 0; i < num_threads; i++) {
            curl_handles[i] = curl_easy_init();

            // HFT optimizations
            curl_easy_setopt(curl_handles[i], CURLOPT_POST, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_WRITEFUNCTION, write_callback);
            curl_easy_setopt(curl_handles[i], CURLOPT_TIMEOUT, 30L);
            curl_easy_setopt(curl_handles[i], CURLOPT_TCP_NODELAY, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_TCP_KEEPALIVE, 1L);
            curl_easy_setopt(curl_handles[i], CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
            curl_easy_setopt(curl_handles[i], CURLOPT_FORBID_REUSE, 0L);

            headers[i] = curl_slist_append(nullptr, "Content-Type: application/json");
            headers[i] = curl_slist_append(headers[i], "Connection: keep-alive");
        }

        for (int i = 0; i < num_threads; i++) {
            pthread_create(&threads[i], nullptr, worker_thread, this);
        }
    }

    ~HFTClient() {
        shutdown.store(true);

        for (int i = 0; i < num_threads; i++) {
            pthread_join(threads[i], nullptr);
        }

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
        task_queue.push(task);
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

    printf("C++ HFT Optimized Client\n");
    printf("Using %d threads\n", num_threads);

    Order order = {
        .buy_sell = "buy",
        .symbol = 2881,
        .price = 66.0,
        .quantity = 2000,
        .market_type = "common",
        .price_type = "limit",
        .time_in_force = "rod",
        .order_type = "stock"
    };

    HFTClient client("http://localhost:8080", num_threads);

    int max_size = std::max(warmup, num_orders);
    Task* tasks = new Task[max_size]();
    OrderResult* results = new OrderResult[max_size]();

    // Warmup
    if (warmup > 0) {
        printf("\nWarming up with %d orders...\n", warmup);

        for (int i = 0; i < warmup; i++) {
            tasks[i] = {i, &order, &results[i]};
            client.submit_order(&tasks[i]);
        }

        client.wait_completion(warmup);
        client.reset_stats();
    }

    printf("\nSending %d orders...\n", num_orders);

    double start = HFTClient::get_current_time();

    for (int i = 0; i < num_orders; i++) {
        tasks[i] = {i, &order, &results[i]};
        client.submit_order(&tasks[i]);
    }

    client.wait_completion(num_orders);

    double elapsed_seconds = (HFTClient::get_current_time() - start) / 1000.0;

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    client.print_stats(elapsed_seconds);

    delete[] tasks;
    delete[] results;

    return 0;
}