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

#define MAX_ORDERS 10000
#define MAX_RESPONSE_SIZE 4096
#define MAX_WORKERS 20  // Maximum thread pool size
#define RING_BUFFER_SIZE 2048
#define OBJECT_POOL_SIZE 4096

// Order struct
typedef struct {
    char* buy_sell;
    int symbol;
    double price;
    int quantity;
    char* market_type;
    char* price_type;
    char* time_in_force;
    char* order_type;
    char* user_def;
} Order;

// Response struct with pre-allocated buffer
typedef struct {
    char data[MAX_RESPONSE_SIZE];
    size_t size;
} Response;

// Lock-free ring buffer implementation
typedef struct {
    void* buffer[RING_BUFFER_SIZE];
    atomic_size_t head;
    atomic_size_t tail;
} RingBuffer;

// Order result struct
typedef struct {
    double latency_ms;
    int success;
} OrderResult;

// Task for thread pool with pre-allocated buffers
typedef struct Task {
    int order_id;
    Order* order;
    OrderResult* result;
    char json_buffer[1024]; // Pre-allocated JSON buffer
    Response response;      // Pre-allocated response buffer
} Task;

// Object pool for tasks
typedef struct {
    Task pool[OBJECT_POOL_SIZE];
    atomic_int available[OBJECT_POOL_SIZE];
    atomic_size_t next_alloc;
} TaskPool;

// Thread pool structure with lock-free queue
typedef struct {
    pthread_t* threads;
    int num_threads;
    RingBuffer* queue;
    atomic_bool shutdown;
    const char* base_url;
    TaskPool* task_pool;
    CURL** curl_handles;     // Pre-initialized CURL handles
    struct curl_slist** headers; // Pre-created headers
} ThreadPool;

// Global metrics
double latencies[MAX_ORDERS];
atomic_int total_orders = 0;
atomic_int successful_orders = 0;

// Initialize ring buffer
RingBuffer* ring_buffer_create() {
    RingBuffer* rb = malloc(sizeof(RingBuffer));
    atomic_init(&rb->head, 0);
    atomic_init(&rb->tail, 0);
    memset(rb->buffer, 0, sizeof(rb->buffer));
    return rb;
}

// Lock-free enqueue
bool ring_buffer_enqueue(RingBuffer* rb, void* item) {
    size_t head = atomic_load(&rb->head);
    size_t next_head = (head + 1) % RING_BUFFER_SIZE;

    if (next_head == atomic_load(&rb->tail)) {
        return false; // Buffer full
    }

    rb->buffer[head] = item;
    atomic_store(&rb->head, next_head);
    return true;
}

// Lock-free dequeue
void* ring_buffer_dequeue(RingBuffer* rb) {
    size_t tail = atomic_load(&rb->tail);

    if (tail == atomic_load(&rb->head)) {
        return NULL; // Buffer empty
    }

    void* item = rb->buffer[tail];
    atomic_store(&rb->tail, (tail + 1) % RING_BUFFER_SIZE);
    return item;
}

// Initialize task pool
TaskPool* task_pool_create() {
    TaskPool* pool = malloc(sizeof(TaskPool));
    for (int i = 0; i < OBJECT_POOL_SIZE; i++) {
        atomic_init(&pool->available[i], 1);
    }
    atomic_init(&pool->next_alloc, 0);
    return pool;
}

// Allocate task from pool
Task* task_pool_alloc(TaskPool* pool) {
    for (int attempts = 0; attempts < OBJECT_POOL_SIZE; attempts++) {
        size_t idx = atomic_fetch_add(&pool->next_alloc, 1) % OBJECT_POOL_SIZE;
        int expected = 1;
        if (atomic_compare_exchange_strong(&pool->available[idx], &expected, 0)) {
            return &pool->pool[idx];
        }
    }
    return NULL; // Pool exhausted
}

// Release task back to pool
void task_pool_free(TaskPool* pool, Task* task) {
    size_t idx = ((char*)task - (char*)pool->pool) / sizeof(Task);
    atomic_store(&pool->available[idx], 1);
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
    size_t total_size = size * nmemb;
    Response* response = (Response*)userp;

    if (response->size + total_size < MAX_RESPONSE_SIZE) {
        memcpy(&(response->data[response->size]), contents, total_size);
        response->size += total_size;
        response->data[response->size] = 0;
    }

    return total_size;
}

// Send single order with pre-allocated resources
OrderResult send_order_optimized(CURL* curl, struct curl_slist* headers,
                                const char* base_url, Order* order,
                                char* json_buffer, Response* response) {
    OrderResult result = {0.0, 0};

    // Reset response buffer
    response->size = 0;
    response->data[0] = 0;

    // Build JSON payload in pre-allocated buffer
    char timestamp[64];
    get_iso_timestamp(timestamp, sizeof(timestamp));

    snprintf(json_buffer, 1024,
        "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
        "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
        "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"%s%s%s}",
        order->buy_sell, order->symbol, order->price, order->quantity,
        order->market_type, order->price_type, order->time_in_force,
        order->order_type, timestamp,
        order->user_def ? ",\"user_def\":\"" : "",
        order->user_def ? order->user_def : "",
        order->user_def ? "\"" : ""
    );

    // Build URL
    char url[256];
    snprintf(url, sizeof(url), "%s/order", base_url);

    double start_time = get_time_ms();

    // Reuse CURL handle with updated fields
    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_buffer);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, response);

    CURLcode res = curl_easy_perform(curl);

    double end_time = get_time_ms();
    double round_trip_ms = end_time - start_time;

    if (res == CURLE_OK) {
        long response_code;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &response_code);

        if (response_code == 200) {
            result.latency_ms = round_trip_ms;
            result.success = 1;
        }
    }

    return result;
}

// Worker thread function with CPU affinity
void* worker_thread(void* arg) {
    ThreadPool* pool = (ThreadPool*)arg;

    // Get thread ID for indexing pre-allocated resources
    static atomic_int thread_counter = 0;
    int thread_id = atomic_fetch_add(&thread_counter, 1);

    // Set CPU affinity
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(thread_id % sysconf(_SC_NPROCESSORS_ONLN), &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);

    // Get pre-allocated CURL handle and headers for this thread
    CURL* curl = pool->curl_handles[thread_id];
    struct curl_slist* headers = pool->headers[thread_id];

    while (!atomic_load(&pool->shutdown)) {
        Task* task = (Task*)ring_buffer_dequeue(pool->queue);

        if (task != NULL) {
            // Process with pre-allocated resources
            *task->result = send_order_optimized(curl, headers, pool->base_url,
                                                task->order, task->json_buffer,
                                                &task->response);

            // Return task to pool
            task_pool_free(pool->task_pool, task);

            // Update metrics
            if (task->result->success) {
                int idx = atomic_fetch_add(&successful_orders, 1);
                if (idx < MAX_ORDERS) {
                    latencies[idx] = task->result->latency_ms;
                }
            }
            atomic_fetch_add(&total_orders, 1);
        } else {
            usleep(100); // Brief sleep when queue is empty
        }
    }

    return NULL;
}

// Create optimized thread pool
ThreadPool* thread_pool_create(int num_threads, const char* base_url) {
    if (num_threads > MAX_WORKERS) {
        num_threads = MAX_WORKERS;
    }

    ThreadPool* pool = malloc(sizeof(ThreadPool));
    pool->threads = malloc(num_threads * sizeof(pthread_t));
    pool->num_threads = num_threads;
    pool->queue = ring_buffer_create();
    atomic_init(&pool->shutdown, false);
    pool->base_url = base_url;
    pool->task_pool = task_pool_create();

    // Pre-initialize CURL handles and headers
    pool->curl_handles = malloc(num_threads * sizeof(CURL*));
    pool->headers = malloc(num_threads * sizeof(struct curl_slist*));

    for (int i = 0; i < num_threads; i++) {
        pool->curl_handles[i] = curl_easy_init();

        // Set persistent CURL options
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_POST, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_WRITEFUNCTION, write_callback);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TIMEOUT, 30L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TCP_NODELAY, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_TCP_KEEPALIVE, 1L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_FRESH_CONNECT, 0L);
        curl_easy_setopt(pool->curl_handles[i], CURLOPT_FORBID_REUSE, 0L);

        // Pre-create headers
        pool->headers[i] = curl_slist_append(NULL, "Content-Type: application/json");
        pool->headers[i] = curl_slist_append(pool->headers[i], "Connection: keep-alive");
    }

    // Create worker threads
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&pool->threads[i], NULL, worker_thread, pool);
    }

    return pool;
}

// Add task to thread pool using lock-free queue
void thread_pool_add_task(ThreadPool* pool, int order_id, Order* order, OrderResult* result) {
    Task* task = task_pool_alloc(pool->task_pool);
    if (task == NULL) {
        // Fallback: wait and retry
        while ((task = task_pool_alloc(pool->task_pool)) == NULL) {
            usleep(100);
        }
    }

    task->order_id = order_id;
    task->order = order;
    task->result = result;

    // Add to lock-free queue
    while (!ring_buffer_enqueue(pool->queue, task)) {
        usleep(100); // Queue full, wait briefly
    }
}

// Wait for all tasks to complete
void thread_pool_wait(ThreadPool* pool) {
    while (atomic_load(&total_orders) < pool->num_threads) {
        usleep(1000);
    }
}

// Destroy thread pool
void thread_pool_destroy(ThreadPool* pool) {
    atomic_store(&pool->shutdown, true);

    for (int i = 0; i < pool->num_threads; i++) {
        pthread_join(pool->threads[i], NULL);
    }

    // Cleanup CURL handles and headers
    for (int i = 0; i < pool->num_threads; i++) {
        curl_easy_cleanup(pool->curl_handles[i]);
        curl_slist_free_all(pool->headers[i]);
    }

    free(pool->curl_handles);
    free(pool->headers);
    free(pool->queue);
    free(pool->task_pool);
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
        printf("Usage: %s <num_orders> <num_connections> <warmup_orders>\n", argv[0]);
        return 1;
    }

    int num_orders = atoi(argv[1]);
    int num_connections = atoi(argv[2]);
    int warmup = atoi(argv[3]);

    if (num_orders > MAX_ORDERS) {
        num_orders = MAX_ORDERS;
    }

    const char* base_url = "http://localhost:8080";

    printf("C Client (Optimized) - Lock-free queue, memory pool, CPU affinity\n");
    printf("Using %d concurrent connections\n", num_connections);

    // Initialize CURL globally
    curl_global_init(CURL_GLOBAL_ALL);

    // Create sample order
    Order order = {
        .buy_sell = "buy",
        .symbol = 2881,
        .price = 66,
        .quantity = 2000,
        .market_type = "common",
        .price_type = "limit",
        .time_in_force = "rod",
        .order_type = "stock",
        .user_def = NULL
    };

    // Limit thread pool size based on concurrency
    int pool_size = num_connections;
    if (pool_size > MAX_WORKERS) {
        pool_size = MAX_WORKERS;
    }

    // Create thread pool
    ThreadPool* pool = thread_pool_create(pool_size, base_url);

    // Warmup
    if (warmup > 0) {
        printf("\nWarming up with %d orders...\n", warmup);
        OrderResult* warmup_results = malloc(warmup * sizeof(OrderResult));

        atomic_store(&total_orders, 0);
        atomic_store(&successful_orders, 0);

        for (int i = 0; i < warmup; i++) {
            thread_pool_add_task(pool, i, &order, &warmup_results[i]);
        }

        while (atomic_load(&total_orders) < warmup) {
            usleep(1000);
        }

        free(warmup_results);

        // Reset counters after warmup
        atomic_store(&total_orders, 0);
        atomic_store(&successful_orders, 0);
    }

    printf("\nSending %d orders...\n", num_orders);

    // Allocate results array
    OrderResult* results = malloc(num_orders * sizeof(OrderResult));

    double start_time = get_time_ms();

    // Submit all tasks to thread pool
    for (int i = 0; i < num_orders; i++) {
        thread_pool_add_task(pool, i, &order, &results[i]);
    }

    // Wait for all tasks to complete
    while (atomic_load(&total_orders) < num_orders) {
        usleep(1000);
    }

    double end_time = get_time_ms();
    double elapsed_seconds = (end_time - start_time) / 1000.0;

    int final_total = atomic_load(&total_orders);
    int final_successful = atomic_load(&successful_orders);

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    printf("Successful: %d, Failed: %d\n", final_successful, final_total - final_successful);

    if (elapsed_seconds > 0) {
        double throughput = num_orders / elapsed_seconds;
        printf("Throughput: %.2f orders/sec\n", throughput);
    }

    // Print statistics
    print_stats(elapsed_seconds, num_orders);

    // Cleanup
    thread_pool_destroy(pool);
    free(results);
    curl_global_cleanup();

    return 0;
}