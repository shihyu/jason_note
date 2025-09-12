#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>
#include <time.h>
#include <unistd.h>
#include <pthread.h>
#include <sched.h>
#include <sys/mman.h>
#include <stdatomic.h>

#define RING_BUFFER_SIZE 65536
#define ORDER_BUFFER_SIZE 32768
#define CACHE_LINE_SIZE 64

// Market data structure
typedef struct __attribute__((packed)) {
    uint64_t timestamp;
    double bid;
    double ask;
    uint64_t volume;
    char symbol[8];
} MarketData;

// Order structure
typedef struct __attribute__((packed)) {
    uint64_t id;
    uint64_t timestamp;
    double price;
    uint64_t quantity;
    char side; // 'B' or 'S'
    char symbol[8];
} Order;

// Ring buffer structure
typedef struct {
    _Alignas(CACHE_LINE_SIZE) atomic_size_t write_idx;
    _Alignas(CACHE_LINE_SIZE) atomic_size_t read_idx;
    _Alignas(CACHE_LINE_SIZE) void* buffer;
    size_t element_size;
    size_t capacity;
} RingBuffer;

// HFT Engine structure
typedef struct {
    RingBuffer* market_buffer;
    RingBuffer* order_buffer;
    atomic_uint_fast64_t processed_orders;
    atomic_uint_fast64_t total_latency_ns;
    atomic_bool running;
    double spread_threshold;
    uint64_t max_position;
} HFTEngine;

// Initialize ring buffer
RingBuffer* ring_buffer_init(size_t capacity, size_t element_size) {
    RingBuffer* rb = (RingBuffer*)aligned_alloc(CACHE_LINE_SIZE, sizeof(RingBuffer));
    if (!rb) return NULL;
    
    rb->buffer = aligned_alloc(CACHE_LINE_SIZE, capacity * element_size);
    if (!rb->buffer) {
        free(rb);
        return NULL;
    }
    
    atomic_init(&rb->write_idx, 0);
    atomic_init(&rb->read_idx, 0);
    rb->element_size = element_size;
    rb->capacity = capacity;
    
    return rb;
}

// Push to ring buffer
bool ring_buffer_push(RingBuffer* rb, const void* item) {
    size_t current_write = atomic_load_explicit(&rb->write_idx, memory_order_relaxed);
    size_t next_write = (current_write + 1) % rb->capacity;
    
    if (next_write == atomic_load_explicit(&rb->read_idx, memory_order_acquire)) {
        return false; // Buffer full
    }
    
    memcpy((char*)rb->buffer + (current_write * rb->element_size), item, rb->element_size);
    atomic_store_explicit(&rb->write_idx, next_write, memory_order_release);
    return true;
}

// Pop from ring buffer
bool ring_buffer_pop(RingBuffer* rb, void* item) {
    size_t current_read = atomic_load_explicit(&rb->read_idx, memory_order_relaxed);
    
    if (current_read == atomic_load_explicit(&rb->write_idx, memory_order_acquire)) {
        return false; // Buffer empty
    }
    
    memcpy(item, (char*)rb->buffer + (current_read * rb->element_size), rb->element_size);
    atomic_store_explicit(&rb->read_idx, (current_read + 1) % rb->capacity, memory_order_release);
    return true;
}

// Free ring buffer
void ring_buffer_free(RingBuffer* rb) {
    if (rb) {
        free(rb->buffer);
        free(rb);
    }
}

// Get current timestamp in nanoseconds
static inline uint64_t get_timestamp_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

// Initialize HFT Engine
HFTEngine* hft_engine_init() {
    HFTEngine* engine = (HFTEngine*)malloc(sizeof(HFTEngine));
    if (!engine) return NULL;
    
    engine->market_buffer = ring_buffer_init(RING_BUFFER_SIZE, sizeof(MarketData));
    engine->order_buffer = ring_buffer_init(ORDER_BUFFER_SIZE, sizeof(Order));
    
    if (!engine->market_buffer || !engine->order_buffer) {
        if (engine->market_buffer) ring_buffer_free(engine->market_buffer);
        if (engine->order_buffer) ring_buffer_free(engine->order_buffer);
        free(engine);
        return NULL;
    }
    
    atomic_init(&engine->processed_orders, 0);
    atomic_init(&engine->total_latency_ns, 0);
    atomic_init(&engine->running, true);
    engine->spread_threshold = 0.001;
    engine->max_position = 10000;
    
    return engine;
}

// Process market data (simple market making strategy)
void process_market_data(HFTEngine* engine, const MarketData* data) {
    uint64_t start_time = get_timestamp_ns();
    
    double spread = data->ask - data->bid;
    double mid_price = (data->ask + data->bid) / 2.0;
    
    // Generate orders based on spread
    if (spread > engine->spread_threshold) {
        Order buy_order;
        buy_order.id = atomic_fetch_add(&engine->processed_orders, 1);
        buy_order.timestamp = get_timestamp_ns();
        buy_order.price = data->bid + 0.0001;
        buy_order.quantity = 100;
        buy_order.side = 'B';
        strncpy(buy_order.symbol, data->symbol, 8);
        
        Order sell_order;
        sell_order.id = atomic_fetch_add(&engine->processed_orders, 1);
        sell_order.timestamp = get_timestamp_ns();
        sell_order.price = data->ask - 0.0001;
        sell_order.quantity = 100;
        sell_order.side = 'S';
        strncpy(sell_order.symbol, data->symbol, 8);
        
        ring_buffer_push(engine->order_buffer, &buy_order);
        ring_buffer_push(engine->order_buffer, &sell_order);
    }
    
    uint64_t latency = get_timestamp_ns() - start_time;
    atomic_fetch_add(&engine->total_latency_ns, latency);
}

// Market data generator thread
void* market_data_generator(void* arg) {
    HFTEngine* engine = (HFTEngine*)arg;
    
    // Pin to CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(1, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    MarketData data;
    strncpy(data.symbol, "AAPL", 8);
    data.bid = 150.00;
    data.ask = 150.01;
    data.volume = 1000000;
    
    uint64_t count = 0;
    while (atomic_load(&engine->running)) {
        data.timestamp = get_timestamp_ns();
        
        // Simulate price movement
        double random_walk = ((double)rand() / RAND_MAX - 0.5) * 0.01;
        data.bid += random_walk;
        data.ask = data.bid + 0.01 + ((double)rand() / RAND_MAX) * 0.02;
        data.volume = 100000 + rand() % 900000;
        
        ring_buffer_push(engine->market_buffer, &data);
        count++;
        
        // Throttle to simulate realistic market data rate
        if (count % 1000 == 0) {
            usleep(1);
        }
    }
    
    return NULL;
}

// Order processor thread
void* order_processor(void* arg) {
    HFTEngine* engine = (HFTEngine*)arg;
    
    // Pin to CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    Order order;
    uint64_t executed_orders = 0;
    
    while (atomic_load(&engine->running)) {
        if (ring_buffer_pop(engine->order_buffer, &order)) {
            // Simulate order execution
            executed_orders++;
            
            // In real system, would send to exchange
            if (executed_orders % 10000 == 0) {
                printf("Executed %lu orders\n", executed_orders);
            }
        }
    }
    
    return NULL;
}

// Strategy thread
void* strategy_thread(void* arg) {
    HFTEngine* engine = (HFTEngine*)arg;
    
    // Pin to CPU core
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(3, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    MarketData data;
    
    while (atomic_load(&engine->running)) {
        if (ring_buffer_pop(engine->market_buffer, &data)) {
            process_market_data(engine, &data);
        }
    }
    
    return NULL;
}

// Free HFT Engine
void hft_engine_free(HFTEngine* engine) {
    if (engine) {
        ring_buffer_free(engine->market_buffer);
        ring_buffer_free(engine->order_buffer);
        free(engine);
    }
}

// Benchmark function with configurable time
void run_benchmark_with_time(int seconds) {
    printf("=== C HFT Trading System Benchmark ===\n");
    printf("Running for %d seconds...\n\n", seconds);
    
    HFTEngine* engine = hft_engine_init();
    if (!engine) {
        fprintf(stderr, "Failed to initialize HFT engine\n");
        return;
    }
    
    // Lock memory to prevent swapping
    if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
        fprintf(stderr, "Warning: Failed to lock memory\n");
    }
    
    // Start threads
    pthread_t market_gen_thread, order_proc_thread, strat_thread;
    
    pthread_create(&market_gen_thread, NULL, market_data_generator, engine);
    pthread_create(&order_proc_thread, NULL, order_processor, engine);
    pthread_create(&strat_thread, NULL, strategy_thread, engine);
    
    // Run for specified seconds
    sleep(seconds);
    
    // Stop engine
    atomic_store(&engine->running, false);
    
    // Wait for threads
    pthread_join(market_gen_thread, NULL);
    pthread_join(order_proc_thread, NULL);
    pthread_join(strat_thread, NULL);
    
    // Print statistics
    uint64_t total_orders = atomic_load(&engine->processed_orders);
    uint64_t total_latency = atomic_load(&engine->total_latency_ns);
    
    printf("\n=== Final Statistics ===\n");
    printf("Total orders processed: %lu\n", total_orders);
    printf("Orders per second: %.2f\n", (double)total_orders / seconds);
    
    if (total_orders > 0) {
        double avg_latency = (double)total_latency / total_orders;
        printf("Average latency: %.2f ns (%.3f µs)\n", avg_latency, avg_latency / 1000.0);
    }
    
    // Memory usage
    printf("\nMemory usage:\n");
    printf("  Market buffer size: %lu KB\n", 
           (RING_BUFFER_SIZE * sizeof(MarketData)) / 1024);
    printf("  Order buffer size: %lu KB\n", 
           (ORDER_BUFFER_SIZE * sizeof(Order)) / 1024);
    printf("  Total buffer memory: %lu KB\n",
           ((RING_BUFFER_SIZE * sizeof(MarketData)) + 
            (ORDER_BUFFER_SIZE * sizeof(Order))) / 1024);
    
    munlockall();
    hft_engine_free(engine);
}

// Keep old function for compatibility
void run_benchmark() {
    run_benchmark_with_time(10);
}

int main(int argc, char* argv[]) {
    srand(time(NULL));
    
    // Parse command line arguments
    int run_time = 10; // default 10 seconds
    if (argc > 1) {
        run_time = atoi(argv[1]);
        if (run_time <= 0) {
            run_time = 10;
        }
    }
    
    run_benchmark_with_time(run_time);
    return 0;
}