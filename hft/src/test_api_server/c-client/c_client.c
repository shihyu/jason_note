#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <math.h>
#include <unistd.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <sched.h>
#include <sys/mman.h>

#define MAX_ORDERS 50000
#define MAX_RESPONSE_SIZE 1024
#define MAX_WORKERS 128  // Upper limit for worker threads
#define DEFAULT_WORKER_MULTIPLIER 1.5  // Default: CPU cores * 1.5

// Core data structures
typedef struct {
    char buy_sell[5];
    int symbol;
    double price;
    int quantity;
    char market_type[10];
    char price_type[10];
    char time_in_force[10];
    char order_type[10];
} Order;

typedef struct {
    double latency_ms;
    int success;
} OrderResult;

typedef struct {
    int order_id;
    Order* order;
    OrderResult* result;
} Task;

typedef struct {
    pthread_t* threads;
    int num_threads;
    Task* task_queue;
    atomic_int queue_head;
    atomic_int queue_tail;
    int queue_size;
    atomic_bool shutdown;
    const char* base_url;
    CURL** curl_handles;
    struct curl_slist** headers;
} ThreadPool;

// Global metrics
double latencies[MAX_ORDERS];
atomic_int total_orders = 0;
atomic_int successful_orders = 0;

// Get optimal worker thread count based on CPU cores
int get_optimal_workers(int requested_connections, int specified_workers) {
    long cpu_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (cpu_cores < 1) cpu_cores = 4; // Fallback to 4 if detection fails

    int workers;

    if (specified_workers > 0) {
        // User specified worker count
        workers = specified_workers;
        if (workers > MAX_WORKERS) {
            printf("Warning: Requested %d workers exceeds max limit of %d\n", workers, MAX_WORKERS);
            workers = MAX_WORKERS;
        }
        printf("Using user-specified %d worker threads\n", workers);
    } else {
        // Calculate optimal workers: CPU cores * multiplier
        int optimal = (int)(cpu_cores * DEFAULT_WORKER_MULTIPLIER);

        // Use minimum of requested connections and optimal
        workers = (requested_connections < optimal) ? requested_connections : optimal;

        // Ensure within bounds
        if (workers < 1) workers = 1;
        if (workers > MAX_WORKERS) workers = MAX_WORKERS;

        printf("Auto-detecting optimal worker count...\n");
        printf("CPU cores detected: %ld\n", cpu_cores);
        printf("Optimal workers calculated: %d (cores * %.1f)\n", optimal, DEFAULT_WORKER_MULTIPLIER);
        printf("Using %d worker threads\n", workers);
    }

    return workers;
}

// Get current time in milliseconds
double get_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

// Get ISO timestamp
void get_iso_timestamp(char* buffer, size_t size) {
    struct timeval tv;
    gettimeofday(&tv, NULL);

    struct tm* tm_info = gmtime(&tv.tv_sec);
    strftime(buffer, size, "%Y-%m-%dT%H:%M:%S", tm_info);

    size_t len = strlen(buffer);
    snprintf(buffer + len, size - len, ".%03dZ", (int)(tv.tv_usec / 1000));
}

// CURL write callback
size_t write_callback(void* contents, size_t size, size_t nmemb, void* userp) {
    (void)userp; // We don't process response for performance
    return size * nmemb;
}

// Send order with optimized settings
OrderResult send_order(CURL* curl, struct curl_slist* headers,
                       const char* base_url, Order* order) {
    OrderResult result = {0.0, 0};
    char json_buffer[512];
    char timestamp[64];
    char url[256];

    get_iso_timestamp(timestamp, sizeof(timestamp));

    snprintf(json_buffer, sizeof(json_buffer),
        "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
        "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
        "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"}",
        order->buy_sell, order->symbol, order->price, order->quantity,
        order->market_type, order->price_type, order->time_in_force,
        order->order_type, timestamp);

    snprintf(url, sizeof(url), "%s/order", base_url);

    double start = get_time_ms();

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_buffer);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);

    if (curl_easy_perform(curl) == CURLE_OK) {
        long code;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &code);
        if (code == 200) {
            result.latency_ms = get_time_ms() - start;
            result.success = 1;
        }
    }

    return result;
}

// Worker thread with HFT optimizations
void* worker_thread(void* arg) {
    ThreadPool* pool = (ThreadPool*)arg;
    static atomic_int thread_counter = 0;
    int thread_id = atomic_fetch_add(&thread_counter, 1);

    // CPU affinity for performance
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(thread_id % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    // Get thread-local CURL handle
    CURL* curl = pool->curl_handles[thread_id];
    struct curl_slist* headers = pool->headers[thread_id];

    while (!atomic_load(&pool->shutdown)) {
        int tail = atomic_load(&pool->queue_tail);
        int head = atomic_load(&pool->queue_head);

        if (tail != head) {
            int idx = atomic_fetch_add(&pool->queue_tail, 1) % pool->queue_size;
            Task* task = &pool->task_queue[idx];

            if (task->order != NULL) {
                *task->result = send_order(curl, headers, pool->base_url, task->order);

                if (task->result->success) {
                    int sidx = atomic_fetch_add(&successful_orders, 1);
                    if (sidx < MAX_ORDERS) {
                        latencies[sidx] = task->result->latency_ms;
                    }
                }
                atomic_fetch_add(&total_orders, 1);
                task->order = NULL;
            }
        } else {
            usleep(100);
        }
    }

    return NULL;
}

// Create thread pool
ThreadPool* thread_pool_create(int num_threads, const char* base_url, int queue_size) {
    if (num_threads > MAX_WORKERS) num_threads = MAX_WORKERS;

    ThreadPool* pool = malloc(sizeof(ThreadPool));
    pool->threads = malloc(num_threads * sizeof(pthread_t));
    pool->num_threads = num_threads;
    pool->queue_size = queue_size;
    pool->task_queue = calloc(queue_size, sizeof(Task));
    atomic_init(&pool->queue_head, 0);
    atomic_init(&pool->queue_tail, 0);
    atomic_init(&pool->shutdown, false);
    pool->base_url = base_url;

    // Initialize CURL handles with HFT optimizations
    pool->curl_handles = malloc(num_threads * sizeof(CURL*));
    pool->headers = malloc(num_threads * sizeof(struct curl_slist*));

    for (int i = 0; i < num_threads; i++) {
        pool->curl_handles[i] = curl_easy_init();

        // HFT optimizations
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_POST, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TIMEOUT, 30L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TCP_NODELAY, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TCP_KEEPALIVE, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_FORBID_REUSE, 0L);

        pool->headers[i] = curl_slist_append(NULL, "Content-Type: application/json");
        pool->headers[i] = curl_slist_append(pool->headers[i], "Connection: keep-alive");
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_create(&pool->threads[i], NULL, worker_thread, pool);
    }

    return pool;
}

// Add task to pool
void thread_pool_add_task(ThreadPool* pool, int order_id, Order* order, OrderResult* result) {
    int idx = atomic_fetch_add(&pool->queue_head, 1) % pool->queue_size;
    pool->task_queue[idx].order_id = order_id;
    pool->task_queue[idx].order = order;
    pool->task_queue[idx].result = result;
}

// Destroy pool
void thread_pool_destroy(ThreadPool* pool) {
    atomic_store(&pool->shutdown, true);

    for (int i = 0; i < pool->num_threads; i++) {
        pthread_join(pool->threads[i], NULL);
    }

    for (int i = 0; i < pool->num_threads; i++) {
        curl_easy_cleanup(pool->curl_handles[i]);
        curl_slist_free_all(pool->headers[i]);
    }

    free(pool->curl_handles);
    free(pool->headers);
    free(pool->task_queue);
    free(pool->threads);
    free(pool);
}

// Comparison function for qsort
int compare_double(const void* a, const void* b) {
    double diff = *(double*)a - *(double*)b;
    return (diff > 0) - (diff < 0);
}

// Calculate percentile with linear interpolation
double calculate_percentile(double* sorted_array, int size, double percentile) {
    if (size == 0) return 0;
    if (size == 1) return sorted_array[0];

    double rank = (percentile / 100.0) * (size - 1);
    int lower_index = (int)rank;
    int upper_index = lower_index + 1;

    if (upper_index >= size) {
        return sorted_array[size - 1];
    }

    double weight = rank - lower_index;
    return sorted_array[lower_index] * (1 - weight) + sorted_array[upper_index] * weight;
}

// Print statistics
void print_stats(double elapsed_seconds, int num_orders) {
    (void)elapsed_seconds;  // Suppress unused warning
    (void)num_orders;       // Suppress unused warning

    int success_count = atomic_load(&successful_orders);

    if (success_count == 0) {
        printf("No successful orders to analyze\n");
        return;
    }

    // Sort latencies for percentile calculation
    qsort(latencies, success_count, sizeof(double), compare_double);

    printf("\n=== C Client Performance Stats (Optimized) ===\n");
    printf("Total orders: %d\n", success_count);

    double min = latencies[0];
    double max = latencies[success_count - 1];

    double sum = 0;
    for (int i = 0; i < success_count; i++) {
        sum += latencies[i];
    }
    double avg = sum / success_count;

    // Calculate standard deviation (sample std dev for better accuracy)
    double variance = 0;
    double std_dev = 0;
    if (success_count > 1) {
        for (int i = 0; i < success_count; i++) {
            variance += (latencies[i] - avg) * (latencies[i] - avg);
        }
        std_dev = sqrt(variance / (success_count - 1));
    }

    printf("Min latency: %.2f ms\n", min);
    printf("Max latency: %.2f ms\n", max);
    printf("Avg latency: %.2f ms\n", avg);
    printf("Median latency: %.2f ms\n", calculate_percentile(latencies, success_count, 50));
    printf("Std dev: %.2f ms\n", std_dev);

    // Calculate percentiles
    printf("P50: %.2f ms\n", calculate_percentile(latencies, success_count, 50));
    printf("P90: %.2f ms\n", calculate_percentile(latencies, success_count, 90));
    printf("P95: %.2f ms\n", calculate_percentile(latencies, success_count, 95));
    printf("P99: %.2f ms\n", calculate_percentile(latencies, success_count, 99));
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        printf("Usage: %s <num_orders> <num_connections> <warmup_orders> [num_workers]\n", argv[0]);
        printf("  num_orders:      Number of orders to send\n");
        printf("  num_connections: Number of concurrent connections\n");
        printf("  warmup_orders:   Number of warmup orders\n");
        printf("  num_workers:     (Optional) Number of worker threads\n");
        printf("                   If not specified, auto-detect based on CPU cores\n");
        return 1;
    }

    int num_orders = atoi(argv[1]);
    int num_connections = atoi(argv[2]);
    int warmup = atoi(argv[3]);
    int num_workers = (argc >= 5) ? atoi(argv[4]) : 0;  // 0 means auto-detect

    if (num_orders > MAX_ORDERS) num_orders = MAX_ORDERS;

    const char* base_url = "http://localhost:8080";

    printf("C Client (HFT Optimized)\n");
    printf("Using %d concurrent connections\n", num_connections);

    // Lock memory for HFT
    mlockall(MCL_CURRENT | MCL_FUTURE);

    curl_global_init(CURL_GLOBAL_ALL);

    // Create sample order
    Order order;
    strcpy(order.buy_sell, "buy");
    order.symbol = 2881;
    order.price = 66;
    order.quantity = 2000;
    strcpy(order.market_type, "common");
    strcpy(order.price_type, "limit");
    strcpy(order.time_in_force, "rod");
    strcpy(order.order_type, "stock");

    int pool_size = get_optimal_workers(num_connections, num_workers);
    ThreadPool* pool = thread_pool_create(pool_size, base_url, num_orders + warmup + 100);

    // Warmup
    if (warmup > 0) {
        printf("\nWarming up with %d orders...\n", warmup);
        OrderResult* warmup_results = malloc(warmup * sizeof(OrderResult));

        for (int i = 0; i < warmup; i++) {
            thread_pool_add_task(pool, i, &order, &warmup_results[i]);
        }

        while (atomic_load(&total_orders) < warmup) {
            usleep(1000);
        }

        free(warmup_results);
        atomic_store(&total_orders, 0);
        atomic_store(&successful_orders, 0);
    }

    printf("\nSending %d orders...\n", num_orders);

    OrderResult* results = malloc(num_orders * sizeof(OrderResult));

    double start_time = get_time_ms();

    for (int i = 0; i < num_orders; i++) {
        thread_pool_add_task(pool, i, &order, &results[i]);
    }

    while (atomic_load(&total_orders) < num_orders) {
        usleep(1000);
    }

    double elapsed_seconds = (get_time_ms() - start_time) / 1000.0;

    int final_total = atomic_load(&total_orders);
    int final_successful = atomic_load(&successful_orders);

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    printf("Successful: %d, Failed: %d\n", final_successful, final_total - final_successful);

    if (elapsed_seconds > 0) {
        printf("Throughput: %.2f orders/sec\n", num_orders / elapsed_seconds);
    }

    print_stats(elapsed_seconds, num_orders);

    thread_pool_destroy(pool);
    free(results);
    curl_global_cleanup();

    return 0;
}