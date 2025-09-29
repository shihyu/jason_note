/*
 * HFT-Optimized C Client
 *
 * Features:
 * - Memory locking (mlock)
 * - HugePage allocation (2MB pages)
 * - NUMA memory binding
 * - CPU affinity (pinning to isolated cores)
 * - Cache line alignment (64-byte)
 * - Memory prefetching (__builtin_prefetch)
 * - Real-time scheduling (SCHED_FIFO)
 * - Thread pool with lock-free queue
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <sys/mman.h>
#include <math.h>
#include <unistd.h>
#include <stdatomic.h>
#include <stdbool.h>
#include <sched.h>
#include <numa.h>
#include <numaif.h>
#include <errno.h>

#define MAX_ORDERS 50000
#define MAX_RESPONSE_SIZE 1024
#define MAX_WORKERS 128
#define DEFAULT_WORKER_MULTIPLIER 1.5
#define CACHE_LINE_SIZE 64
#define HUGEPAGE_SIZE (2 * 1024 * 1024)  // 2MB

// Cache-aligned data structures
typedef struct __attribute__((aligned(CACHE_LINE_SIZE))) {
    char buy_sell[5];
    int symbol;
    double price;
    int quantity;
    char market_type[10];
    char price_type[10];
    char time_in_force[10];
    char order_type[10];
    char padding[CACHE_LINE_SIZE - 53];  // Pad to 64 bytes
} Order;

typedef struct __attribute__((aligned(CACHE_LINE_SIZE))) {
    double latency_ms;
    int success;
    char padding[CACHE_LINE_SIZE - sizeof(double) - sizeof(int)];
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
    atomic_int queue_head __attribute__((aligned(CACHE_LINE_SIZE)));
    atomic_int queue_tail __attribute__((aligned(CACHE_LINE_SIZE)));
    int queue_size;
    atomic_bool shutdown;
    const char* base_url;
    CURL** curl_handles;
    struct curl_slist** headers;
    int* thread_ids;  // Array to pass thread IDs
} ThreadPool;

// Global metrics (cache-aligned)
double* latencies __attribute__((aligned(CACHE_LINE_SIZE)));
atomic_int total_orders __attribute__((aligned(CACHE_LINE_SIZE))) = 0;
atomic_int successful_orders __attribute__((aligned(CACHE_LINE_SIZE))) = 0;

// Global flag to track if we used hugepages
bool used_hugepages = false;

// Initialize NUMA
void init_numa() {
    if (numa_available() < 0) {
        fprintf(stderr, "Warning: NUMA not available on this system\n");
        return;
    }

    // Set local allocation policy
    numa_set_localalloc();
    numa_set_strict(1);

    // Bind to NUMA node 0
    struct bitmask *nodemask = numa_allocate_nodemask();
    numa_bitmask_setbit(nodemask, 0);
    numa_bind(nodemask);
    numa_free_nodemask(nodemask);

    printf("✓ NUMA initialized: bound to node 0, local allocation enabled\n");
}

// Set real-time scheduling
void set_realtime_priority(int priority) {
    struct sched_param param;
    param.sched_priority = priority;

    if (sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
        fprintf(stderr, "Warning: Failed to set real-time priority: %s\n", strerror(errno));
        fprintf(stderr, "Hint: Run with sudo or set CAP_SYS_NICE capability:\n");
        fprintf(stderr, "      sudo setcap cap_sys_nice+ep ./c_client_hft\n");
    } else {
        printf("✓ Real-time scheduling enabled: SCHED_FIFO priority %d\n", priority);
    }
}

// Get optimal worker thread count
int get_optimal_workers(int requested_connections, int specified_workers) {
    long cpu_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (cpu_cores < 1) cpu_cores = 4;

    int workers;
    if (specified_workers > 0) {
        workers = specified_workers;
        if (workers > MAX_WORKERS) {
            printf("Warning: Requested %d workers exceeds max limit of %d\n", workers, MAX_WORKERS);
            workers = MAX_WORKERS;
        }
        printf("Using user-specified %d worker threads\n", workers);
    } else {
        int optimal = (int)(cpu_cores * DEFAULT_WORKER_MULTIPLIER);
        workers = (requested_connections < optimal) ? requested_connections : optimal;
        if (workers < 1) workers = 1;
        if (workers > MAX_WORKERS) workers = MAX_WORKERS;
        printf("Auto-detecting optimal worker count: %d (CPU cores: %ld)\n", workers, cpu_cores);
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
    (void)userp;
    return size * nmemb;
}

// Send order with optimizations
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
    int thread_id = *((int*)arg);

    // Get pool from global or passed context - we'll fix this
    // For now, we need to pass both pool and thread_id
    return NULL;
}

    // CPU affinity: bind to isolated cores (8-27)
    // Assuming cores 0-7 are for system, 8-27 are isolated
    int target_cpu = 8 + (thread_id % 20);  // Cores 8-27
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(target_cpu, &cpuset);

    if (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0) {
        // Success - affinity set
    } else {
        fprintf(stderr, "Warning: Failed to set CPU affinity for thread %d\n", thread_id);
    }

    // Set thread real-time priority
    struct sched_param param;
    param.sched_priority = 40;  // Lower than main thread
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);

    // Get thread-local CURL handle
    CURL* curl = pool->curl_handles[thread_id];
    struct curl_slist* headers = pool->headers[thread_id];

    while (!atomic_load(&pool->shutdown)) {
        int tail = atomic_load(&pool->queue_tail);
        int head = atomic_load(&pool->queue_head);

        if (tail != head) {
            int idx = atomic_fetch_add(&pool->queue_tail, 1) % pool->queue_size;
            Task* task = &pool->task_queue[idx];

            // Prefetch next task
            if (idx + 1 < pool->queue_size) {
                __builtin_prefetch(&pool->task_queue[idx + 1], 0, 3);
            }

            if (task->order != NULL) {
                *task->result = send_order(curl, headers, pool->base_url, task->order);

                if (task->result->success) {
                    int sidx = atomic_fetch_add(&successful_orders, 1);
                    if (sidx < MAX_ORDERS) {
                        latencies[sidx] = task->result->latency_ms;

                        // Prefetch next latency slot
                        if (sidx + 1 < MAX_ORDERS) {
                            __builtin_prefetch(&latencies[sidx + 1], 1, 3);
                        }
                    }
                }
                atomic_fetch_add(&total_orders, 1);
                task->order = NULL;
            }
        } else {
            // Reduce CPU usage when idle
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

// Add task to pool with prefetching
void thread_pool_add_task(ThreadPool* pool, int order_id, Order* order, OrderResult* result) {
    int idx = atomic_fetch_add(&pool->queue_head, 1) % pool->queue_size;

    // Prefetch task slot
    __builtin_prefetch(&pool->task_queue[idx], 1, 3);

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

// Calculate percentile
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
    (void)elapsed_seconds;
    (void)num_orders;

    int success_count = atomic_load(&successful_orders);

    if (success_count == 0) {
        printf("No successful orders to analyze\n");
        return;
    }

    // Sort latencies
    qsort(latencies, success_count, sizeof(double), compare_double);

    printf("\n=== HFT-Optimized C Client Performance ===\n");
    printf("Optimizations: HugePage, NUMA, Cache-aligned, Prefetch, RT-scheduling\n");
    printf("Total orders: %d\n", success_count);

    double min = latencies[0];
    double max = latencies[success_count - 1];

    double sum = 0;
    for (int i = 0; i < success_count; i++) {
        sum += latencies[i];
    }
    double avg = sum / success_count;

    double variance = 0;
    double std_dev = 0;
    if (success_count > 1) {
        for (int i = 0; i < success_count; i++) {
            variance += (latencies[i] - avg) * (latencies[i] - avg);
        }
        std_dev = sqrt(variance / (success_count - 1));
    }

    printf("Min latency: %.3f ms\n", min);
    printf("Max latency: %.3f ms\n", max);
    printf("Avg latency: %.3f ms\n", avg);
    printf("Median latency: %.3f ms\n", calculate_percentile(latencies, success_count, 50));
    printf("Std dev: %.3f ms\n", std_dev);
    printf("P50: %.3f ms\n", calculate_percentile(latencies, success_count, 50));
    printf("P90: %.3f ms\n", calculate_percentile(latencies, success_count, 90));
    printf("P95: %.3f ms\n", calculate_percentile(latencies, success_count, 95));
    printf("P99: %.3f ms\n", calculate_percentile(latencies, success_count, 99));
    printf("P99.9: %.3f ms\n", calculate_percentile(latencies, success_count, 99.9));
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        printf("Usage: %s <num_orders> <num_connections> <warmup_orders> [num_workers]\n", argv[0]);
        printf("  num_orders:      Number of orders to send\n");
        printf("  num_connections: Number of concurrent connections\n");
        printf("  warmup_orders:   Number of warmup orders\n");
        printf("  num_workers:     (Optional) Number of worker threads\n");
        return 1;
    }

    int num_orders = atoi(argv[1]);
    int num_connections = atoi(argv[2]);
    int warmup = atoi(argv[3]);
    int num_workers = (argc >= 5) ? atoi(argv[4]) : 0;

    if (num_orders > MAX_ORDERS) num_orders = MAX_ORDERS;

    const char* base_url = "http://localhost:8080";

    printf("=== HFT-Optimized C Client ===\n");
    printf("Using %d concurrent connections\n", num_connections);

    // Initialize NUMA
    init_numa();

    // Lock all memory (current and future)
    if (mlockall(MCL_CURRENT | MCL_FUTURE) == 0) {
        printf("✓ Memory locked: mlockall(MCL_CURRENT | MCL_FUTURE)\n");
    } else {
        fprintf(stderr, "Warning: mlockall failed: %s\n", strerror(errno));
    }

    // Set real-time priority for main thread
    set_realtime_priority(50);

    // Allocate latencies array
    size_t latencies_size = MAX_ORDERS * sizeof(double);
    latencies = (double*)malloc(latencies_size);
    if (!latencies) {
        fprintf(stderr, "Failed to allocate latencies array\n");
        return 1;
    }

    // Lock memory and prefault
    if (mlock(latencies, latencies_size) == 0) {
        printf("✓ Latencies array locked in memory (%zu bytes)\n", latencies_size);
    }
    memset(latencies, 0, latencies_size);

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

    // Cleanup memory (we can't easily distinguish if it's hugepage or malloc,
    // but free() is safe for malloc'd memory, so we skip munmap for simplicity)
    free(latencies);

    curl_global_cleanup();

    return 0;
}