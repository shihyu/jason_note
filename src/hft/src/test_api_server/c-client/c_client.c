#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <curl/curl.h>
#include <pthread.h>
#include <unistd.h>
#include <math.h>
#include <sys/time.h>

#define MAX_RESPONSE_SIZE 4096
#define MAX_ORDERS 100000

// Order structure
typedef struct {
    const char* buy_sell;
    int symbol;
    double price;
    int quantity;
    const char* market_type;
    const char* price_type;
    const char* time_in_force;
    const char* order_type;
    const char* user_def;
} Order;

// Response structure
typedef struct {
    char data[MAX_RESPONSE_SIZE];
    size_t size;
} Response;

// Performance metrics
typedef struct {
    double latency_ms;
    int success;
} OrderResult;

// Thread data structure
typedef struct {
    int thread_id;
    int start_order;
    int end_order;
    Order* order;
    OrderResult* results;
    const char* base_url;
    double* thread_latencies;  // Thread-local latency storage
    int thread_success_count;  // Thread-local success counter
} ThreadData;

// Global metrics
double latencies[MAX_ORDERS];
int total_orders = 0;
int successful_orders = 0;
pthread_mutex_t metrics_mutex = PTHREAD_MUTEX_INITIALIZER;

// Get current time in milliseconds
double get_time_ms() {
    struct timeval tv;
    gettimeofday(&tv, NULL);
    return tv.tv_sec * 1000.0 + tv.tv_usec / 1000.0;
}

// Get ISO timestamp string
void get_iso_timestamp(char* buffer, size_t size) {
    time_t now;
    struct tm* tm_info;
    struct timeval tv;
    
    gettimeofday(&tv, NULL);
    now = tv.tv_sec;
    tm_info = gmtime(&now);
    
    strftime(buffer, size - 4, "%Y-%m-%dT%H:%M:%S", tm_info);
    sprintf(buffer + strlen(buffer), ".%03dZ", (int)(tv.tv_usec / 1000));
}

// Write callback for CURL
size_t write_callback(void* contents, size_t size, size_t nmemb, Response* response) {
    size_t total_size = size * nmemb;
    size_t new_size = response->size + total_size;
    
    if (new_size < MAX_RESPONSE_SIZE - 1) {
        memcpy(response->data + response->size, contents, total_size);
        response->size = new_size;
        response->data[response->size] = '\0';
    }
    
    return total_size;
}

// Parse latency from JSON response (simple parsing)
double parse_latency(const char* json) {
    const char* latency_str = strstr(json, "\"latency_ms\":");
    if (latency_str) {
        latency_str += 13; // Skip "latency_ms":
        return atof(latency_str);
    }
    return 0.0;
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
    curl_easy_setopt(curl, CURLOPT_TCP_NODELAY, 1L);  // Disable Nagle's algorithm
    curl_easy_setopt(curl, CURLOPT_TCP_KEEPALIVE, 1L);  // Enable TCP keepalive
    curl_easy_setopt(curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);  // Use HTTP/1.1
    
    res = curl_easy_perform(curl);
    
    double end_time = get_time_ms();
    
    if (res == CURLE_OK) {
        long http_code = 0;
        curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
        
        if (http_code == 200) {
            result.success = 1;
            result.latency_ms = end_time - start_time;
            
            // Try to parse server latency
            double server_latency = parse_latency(response.data);
            if (server_latency > 0) {
                // Use server-reported latency if available
                result.latency_ms = server_latency;
            }
        }
    }
    
    curl_slist_free_all(headers);
    curl_easy_cleanup(curl);
    
    return result;
}

// Worker thread function
void* worker_thread(void* arg) {
    ThreadData* data = (ThreadData*)arg;
    data->thread_success_count = 0;

    for (int i = data->start_order; i < data->end_order; i++) {
        OrderResult result = send_order(data->base_url, data->order);

        if (result.success) {
            data->thread_latencies[data->thread_success_count++] = result.latency_ms;
        }
    }

    return NULL;
}

// Comparison function for qsort
int compare_double(const void* a, const void* b) {
    double diff = *(double*)a - *(double*)b;
    return (diff > 0) - (diff < 0);
}

// Calculate percentile
double calculate_percentile(double* sorted_array, int size, double percentile) {
    if (size == 0) return 0;
    int index = (int)((percentile / 100.0) * (size - 1));
    return sorted_array[index];
}

// Calculate standard deviation
double calculate_stddev(double* array, int size, double mean) {
    if (size <= 1) return 0;
    
    double sum_sq = 0;
    for (int i = 0; i < size; i++) {
        double diff = array[i] - mean;
        sum_sq += diff * diff;
    }
    
    return sqrt(sum_sq / (size - 1));
}

// Print performance statistics
void print_stats(double elapsed_seconds, int num_orders) {
    if (successful_orders == 0) {
        printf("No successful orders to analyze\n");
        return;
    }
    
    // Sort latencies
    qsort(latencies, successful_orders, sizeof(double), compare_double);
    
    // Calculate statistics
    double min_latency = latencies[0];
    double max_latency = latencies[successful_orders - 1];
    double sum = 0;
    for (int i = 0; i < successful_orders; i++) {
        sum += latencies[i];
    }
    double avg_latency = sum / successful_orders;
    double median = calculate_percentile(latencies, successful_orders, 50);
    double p90 = calculate_percentile(latencies, successful_orders, 90);
    double p95 = calculate_percentile(latencies, successful_orders, 95);
    double p99 = calculate_percentile(latencies, successful_orders, 99);
    double stddev = calculate_stddev(latencies, successful_orders, avg_latency);
    
    printf("\n=== C Client Performance Stats ===\n");
    printf("Total orders: %d\n", total_orders);
    printf("Min latency: %.2f ms\n", min_latency);
    printf("Max latency: %.2f ms\n", max_latency);
    printf("Avg latency: %.2f ms\n", avg_latency);
    printf("Median latency: %.2f ms\n", median);
    printf("Std dev: %.2f ms\n", stddev);
    
    if (successful_orders >= 100) {
        printf("P50: %.2f ms\n", median);
        printf("P90: %.2f ms\n", p90);
        printf("P95: %.2f ms\n", p95);
        printf("P99: %.2f ms\n", p99);
    }
}

int main(int argc, char* argv[]) {
    if (argc < 4) {
        printf("Usage: %s <num_orders> <num_connections> <warmup_orders>\n", argv[0]);
        return 1;
    }
    
    int num_orders = atoi(argv[1]);
    int num_connections = atoi(argv[2]);
    int warmup_orders = atoi(argv[3]);
    
    if (num_orders > MAX_ORDERS) {
        printf("Error: Maximum orders is %d\n", MAX_ORDERS);
        return 1;
    }
    
    printf("C Client - Starting test with %d orders\n", num_orders);
    printf("Using %d concurrent connections\n", num_connections);
    printf("Testing with Taiwan Stock Order: Symbol=2881 Price=NT$66 Qty=2000\n");
    
    // Initialize CURL
    curl_global_init(CURL_GLOBAL_ALL);
    
    // Default order
    Order order = {
        .buy_sell = "buy",
        .symbol = 2881,
        .price = 66.0,
        .quantity = 2000,
        .market_type = "common",
        .price_type = "limit",
        .time_in_force = "rod",
        .order_type = "stock",
        .user_def = NULL
    };
    
    const char* base_url = "http://localhost:8080";
    
    // Warmup phase
    if (warmup_orders > 0) {
        printf("\nWarming up with %d orders...\n", warmup_orders);
        
        for (int i = 0; i < warmup_orders; i++) {
            send_order(base_url, &order);
        }
        
        // Reset metrics after warmup
        successful_orders = 0;
        total_orders = 0;
    }
    
    // Main test phase
    printf("\nSending %d orders...\n", num_orders);
    
    double start_time = get_time_ms();
    
    // Create threads
    pthread_t* threads = malloc(num_connections * sizeof(pthread_t));
    ThreadData* thread_data = malloc(num_connections * sizeof(ThreadData));
    
    int orders_per_thread = num_orders / num_connections;
    int remaining_orders = num_orders % num_connections;
    
    int current_order = 0;
    for (int i = 0; i < num_connections; i++) {
        thread_data[i].thread_id = i;
        thread_data[i].start_order = current_order;
        thread_data[i].end_order = current_order + orders_per_thread;
        if (i < remaining_orders) {
            thread_data[i].end_order++;
        }
        thread_data[i].order = &order;
        thread_data[i].base_url = base_url;

        // Allocate thread-local latency storage
        int thread_orders = thread_data[i].end_order - thread_data[i].start_order;
        thread_data[i].thread_latencies = malloc(thread_orders * sizeof(double));
        thread_data[i].thread_success_count = 0;

        current_order = thread_data[i].end_order;

        pthread_create(&threads[i], NULL, worker_thread, &thread_data[i]);
    }

    // Wait for all threads to complete and merge results
    for (int i = 0; i < num_connections; i++) {
        pthread_join(threads[i], NULL);

        // Merge thread-local latencies into global array without lock
        for (int j = 0; j < thread_data[i].thread_success_count; j++) {
            latencies[successful_orders++] = thread_data[i].thread_latencies[j];
        }
        total_orders += (thread_data[i].end_order - thread_data[i].start_order);

        // Free thread-local storage
        free(thread_data[i].thread_latencies);
    }
    
    double end_time = get_time_ms();
    double elapsed_seconds = (end_time - start_time) / 1000.0;
    
    printf("\nCompleted in %.2f seconds\n", elapsed_seconds);
    printf("Successful: %d, Failed: %d\n", successful_orders, total_orders - successful_orders);
    
    if (elapsed_seconds > 0) {
        double throughput = num_orders / elapsed_seconds;
        printf("Throughput: %.2f orders/sec\n", throughput);
    }
    
    // Print statistics
    print_stats(elapsed_seconds, num_orders);
    
    // Cleanup
    free(threads);
    free(thread_data);
    curl_global_cleanup();
    
    return 0;
}