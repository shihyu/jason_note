#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curl/curl.h>
#include <pthread.h>
#include <sys/time.h>
#include <math.h>
#include <unistd.h>

#define MAX_ORDERS 10000
#define MAX_RESPONSE_SIZE 4096
#define MAX_WORKERS 20  // Maximum thread pool size

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

// Response struct
typedef struct {
    char data[MAX_RESPONSE_SIZE];
    size_t size;
} Response;

// Order result struct
typedef struct {
    double latency_ms;
    int success;
} OrderResult;

// Task for thread pool
typedef struct Task {
    int order_id;
    Order* order;
    OrderResult* result;
    struct Task* next;
} Task;

// Thread pool structure
typedef struct {
    pthread_t* threads;
    int num_threads;
    Task* task_queue;
    Task* queue_tail;
    pthread_mutex_t queue_mutex;
    pthread_cond_t queue_cond;
    int shutdown;
    const char* base_url;
} ThreadPool;

// Global metrics
double latencies[MAX_ORDERS];
int total_orders = 0;
int successful_orders = 0;

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

// Send single order
OrderResult send_order(const char* base_url, Order* order) {
    CURL* curl;
    CURLcode res;
    OrderResult result = {0.0, 0};
    Response response = {{0}, 0};

    curl = curl_easy_init();
    if (!curl) {
        return result;
    }

    // Build JSON payload
    char json_payload[1024];
    char timestamp[64];
    get_iso_timestamp(timestamp, sizeof(timestamp));

    snprintf(json_payload, sizeof(json_payload),
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

    // Set up CURL options
    struct curl_slist* headers = NULL;
    headers = curl_slist_append(headers, "Content-Type: application/json");

    double start_time = get_time_ms();

    curl_easy_setopt(curl, CURLOPT_URL, url);
    curl_easy_setopt(curl, CURLOPT_POST, 1L);
    curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_payload);
    curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, write_callback);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);

    // Performance optimizations
    curl_easy_setopt(curl, CURLOPT_TCP_NODELAY, 1L);
    curl_easy_setopt(curl, CURLOPT_TCP_KEEPALIVE, 1L);
    curl_easy_setopt(curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);

    res = curl_easy_perform(curl);

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

    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);

    return result;
}

// Worker thread function for thread pool
void* worker_thread(void* arg) {
    ThreadPool* pool = (ThreadPool*)arg;

    while (1) {
        pthread_mutex_lock(&pool->queue_mutex);

        // Wait for task or shutdown signal
        while (pool->task_queue == NULL && !pool->shutdown) {
            pthread_cond_wait(&pool->queue_cond, &pool->queue_mutex);
        }

        if (pool->shutdown) {
            pthread_mutex_unlock(&pool->queue_mutex);
            break;
        }

        // Get task from queue
        Task* task = pool->task_queue;
        if (task != NULL) {
            pool->task_queue = task->next;
            if (pool->task_queue == NULL) {
                pool->queue_tail = NULL;
            }
        }

        pthread_mutex_unlock(&pool->queue_mutex);

        if (task != NULL) {
            // Process the task
            *task->result = send_order(pool->base_url, task->order);
            free(task);
        }
    }

    return NULL;
}

// Create thread pool
ThreadPool* thread_pool_create(int num_threads, const char* base_url) {
    if (num_threads > MAX_WORKERS) {
        num_threads = MAX_WORKERS;
    }

    ThreadPool* pool = malloc(sizeof(ThreadPool));
    pool->threads = malloc(num_threads * sizeof(pthread_t));
    pool->num_threads = num_threads;
    pool->task_queue = NULL;
    pool->queue_tail = NULL;
    pool->shutdown = 0;
    pool->base_url = base_url;

    pthread_mutex_init(&pool->queue_mutex, NULL);
    pthread_cond_init(&pool->queue_cond, NULL);

    // Create worker threads
    for (int i = 0; i < num_threads; i++) {
        pthread_create(&pool->threads[i], NULL, worker_thread, pool);
    }

    return pool;
}

// Add task to thread pool
void thread_pool_add_task(ThreadPool* pool, int order_id, Order* order, OrderResult* result) {
    Task* task = malloc(sizeof(Task));
    task->order_id = order_id;
    task->order = order;
    task->result = result;
    task->next = NULL;

    pthread_mutex_lock(&pool->queue_mutex);

    if (pool->queue_tail == NULL) {
        pool->task_queue = task;
        pool->queue_tail = task;
    } else {
        pool->queue_tail->next = task;
        pool->queue_tail = task;
    }

    pthread_cond_signal(&pool->queue_cond);
    pthread_mutex_unlock(&pool->queue_mutex);
}

// Wait for all tasks to complete
void thread_pool_wait(ThreadPool* pool) {
    while (1) {
        pthread_mutex_lock(&pool->queue_mutex);
        int empty = (pool->task_queue == NULL);
        pthread_mutex_unlock(&pool->queue_mutex);

        if (empty) {
            break;
        }

        usleep(1000);  // Sleep 1ms
    }
}

// Destroy thread pool
void thread_pool_destroy(ThreadPool* pool) {
    pthread_mutex_lock(&pool->queue_mutex);
    pool->shutdown = 1;
    pthread_cond_broadcast(&pool->queue_cond);
    pthread_mutex_unlock(&pool->queue_mutex);

    for (int i = 0; i < pool->num_threads; i++) {
        pthread_join(pool->threads[i], NULL);
    }

    pthread_mutex_destroy(&pool->queue_mutex);
    pthread_cond_destroy(&pool->queue_cond);

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
    if (successful_orders == 0) {
        printf("No successful orders to analyze\n");
        return;
    }

    // Sort latencies for percentile calculation
    qsort(latencies, successful_orders, sizeof(double), compare_double);

    printf("\n=== C Client Performance Stats ===\n");
    printf("Total orders: %d\n", successful_orders);

    double min = latencies[0];
    double max = latencies[successful_orders - 1];

    double sum = 0;
    for (int i = 0; i < successful_orders; i++) {
        sum += latencies[i];
    }
    double avg = sum / successful_orders;

    // Calculate standard deviation (sample std dev for better accuracy)
    double variance = 0;
    double std_dev = 0;
    if (successful_orders > 1) {
        for (int i = 0; i < successful_orders; i++) {
            variance += (latencies[i] - avg) * (latencies[i] - avg);
        }
        std_dev = sqrt(variance / (successful_orders - 1));
    }

    printf("Min latency: %.2f ms\n", min);
    printf("Max latency: %.2f ms\n", max);
    printf("Avg latency: %.2f ms\n", avg);
    printf("Median latency: %.2f ms\n", calculate_percentile(latencies, successful_orders, 50));
    printf("Std dev: %.2f ms\n", std_dev);

    // Calculate percentiles
    printf("P50: %.2f ms\n", calculate_percentile(latencies, successful_orders, 50));
    printf("P90: %.2f ms\n", calculate_percentile(latencies, successful_orders, 90));
    printf("P95: %.2f ms\n", calculate_percentile(latencies, successful_orders, 95));
    printf("P99: %.2f ms\n", calculate_percentile(latencies, successful_orders, 99));
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

        for (int i = 0; i < warmup; i++) {
            thread_pool_add_task(pool, i, &order, &warmup_results[i]);
        }

        thread_pool_wait(pool);
        free(warmup_results);
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
    thread_pool_wait(pool);

    double end_time = get_time_ms();
    double elapsed_seconds = (end_time - start_time) / 1000.0;

    // Collect results
    for (int i = 0; i < num_orders; i++) {
        if (results[i].success) {
            latencies[successful_orders++] = results[i].latency_ms;
        }
        total_orders++;
    }

    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    printf("Successful: %d, Failed: %d\n", successful_orders, total_orders - successful_orders);

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