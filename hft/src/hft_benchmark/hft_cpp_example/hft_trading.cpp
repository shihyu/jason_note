#include <iostream>
#include <chrono>
#include <vector>
#include <queue>
#include <atomic>
#include <thread>
#include <random>
#include <cstring>
#include <unistd.h>
#include <sched.h>
#include <sys/mman.h>

using namespace std::chrono;

// Market data structure
struct MarketData {
    uint64_t timestamp;
    double bid;
    double ask;
    uint64_t volume;
    char symbol[8];
} __attribute__((packed));

// Order structure
struct Order {
    uint64_t id;
    uint64_t timestamp;
    double price;
    uint64_t quantity;
    char side; // 'B' or 'S'
    char symbol[8];
} __attribute__((packed));

// Lock-free ring buffer for market data
template<typename T, size_t Size>
class RingBuffer {
private:
    alignas(64) std::atomic<size_t> write_idx{0};
    alignas(64) std::atomic<size_t> read_idx{0};
    alignas(64) T buffer[Size];
    
public:
    bool push(const T& item) {
        size_t current_write = write_idx.load(std::memory_order_relaxed);
        size_t next_write = (current_write + 1) % Size;
        
        if (next_write == read_idx.load(std::memory_order_acquire)) {
            return false; // Buffer full
        }
        
        buffer[current_write] = item;
        write_idx.store(next_write, std::memory_order_release);
        return true;
    }
    
    bool pop(T& item) {
        size_t current_read = read_idx.load(std::memory_order_relaxed);
        
        if (current_read == write_idx.load(std::memory_order_acquire)) {
            return false; // Buffer empty
        }
        
        item = buffer[current_read];
        read_idx.store((current_read + 1) % Size, std::memory_order_release);
        return true;
    }
};

// High-frequency trading engine
class HFTEngine {
private:
    RingBuffer<MarketData, 65536> market_buffer;
    RingBuffer<Order, 32768> order_buffer;
    std::atomic<uint64_t> processed_orders{0};
    std::atomic<uint64_t> total_latency_ns{0};
    std::atomic<bool> running{true};
    
    // Strategy parameters
    double spread_threshold = 0.001;
    uint64_t max_position = 10000;
    
public:
    // Get current timestamp in nanoseconds
    inline uint64_t get_timestamp() {
        return duration_cast<nanoseconds>(
            high_resolution_clock::now().time_since_epoch()
        ).count();
    }
    
    // Simple market making strategy
    void process_market_data(const MarketData& data) {
        auto start_time = get_timestamp();
        
        double spread = data.ask - data.bid;
        double mid_price = (data.ask + data.bid) / 2.0;
        
        // Generate orders based on spread
        if (spread > spread_threshold) {
            Order buy_order;
            buy_order.id = processed_orders.fetch_add(1);
            buy_order.timestamp = get_timestamp();
            buy_order.price = data.bid + 0.0001;
            buy_order.quantity = 100;
            buy_order.side = 'B';
            strcpy(buy_order.symbol, data.symbol);
            
            Order sell_order;
            sell_order.id = processed_orders.fetch_add(1);
            sell_order.timestamp = get_timestamp();
            sell_order.price = data.ask - 0.0001;
            sell_order.quantity = 100;
            sell_order.side = 'S';
            strcpy(sell_order.symbol, data.symbol);
            
            order_buffer.push(buy_order);
            order_buffer.push(sell_order);
            
            // Add latency for both orders (since we generated 2 orders)
            auto end_time = get_timestamp();
            total_latency_ns.fetch_add((end_time - start_time) * 2);
        }
    }
    
    // Market data feed simulator
    void market_data_generator() {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> price_dist(99.0, 101.0);
        std::uniform_int_distribution<> volume_dist(100, 10000);
        
        // Pin thread to CPU core
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(2, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        
        while (running.load()) {
            MarketData data;
            data.timestamp = get_timestamp();
            double mid = price_dist(gen);
            data.bid = mid - 0.001;
            data.ask = mid + 0.001;
            data.volume = volume_dist(gen);
            strcpy(data.symbol, "AAPL");
            
            market_buffer.push(data);
            
            // Simulate market data rate (10000 msgs/sec)
            std::this_thread::sleep_for(microseconds(100));
        }
    }
    
    // Trading engine main loop
    void trading_loop() {
        // Pin thread to CPU core
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(3, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        
        MarketData data;
        uint64_t messages_processed = 0;
        
        while (running.load()) {
            if (market_buffer.pop(data)) {
                process_market_data(data);
                messages_processed++;
                
                if (messages_processed % 10000 == 0) {
                    uint64_t avg_latency = total_latency_ns.load() / processed_orders.load();
                    std::cout << "Processed: " << messages_processed 
                             << " orders, Avg latency: " << avg_latency << " ns"
                             << " (" << avg_latency / 1000.0 << " μs)" << std::endl;
                }
            }
        }
    }
    
    // Order execution simulator
    void order_executor() {
        // Pin thread to CPU core
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(4, &cpuset);
        pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        
        Order order;
        uint64_t executed_orders = 0;
        
        while (running.load()) {
            if (order_buffer.pop(order)) {
                // Simulate order execution
                auto exec_time = get_timestamp() - order.timestamp;
                executed_orders++;
                
                if (executed_orders % 1000 == 0) {
                    std::cout << "Executed " << executed_orders << " orders" << std::endl;
                }
            }
        }
    }
    
    void run(int duration_seconds) {
        // Lock memory to prevent paging
        if (mlockall(MCL_CURRENT | MCL_FUTURE) != 0) {
            std::cerr << "Warning: Could not lock memory" << std::endl;
        }
        
        std::cout << "Starting HFT Engine for " << duration_seconds << " seconds..." << std::endl;
        
        std::thread market_thread(&HFTEngine::market_data_generator, this);
        std::thread trading_thread(&HFTEngine::trading_loop, this);
        std::thread executor_thread(&HFTEngine::order_executor, this);
        
        std::this_thread::sleep_for(seconds(duration_seconds));
        
        running.store(false);
        
        market_thread.join();
        trading_thread.join();
        executor_thread.join();
        
        // Print final statistics
        std::cout << "\n=== Final Statistics ===" << std::endl;
        std::cout << "Total orders processed: " << processed_orders.load() << std::endl;
        if (processed_orders.load() > 0) {
            uint64_t avg_latency = total_latency_ns.load() / processed_orders.load();
            std::cout << "Average latency: " << avg_latency << " ns (" 
                     << avg_latency / 1000.0 << " μs)" << std::endl;
        }
    }
};

int main(int argc, char* argv[]) {
    int duration = 30; // Default 30 seconds
    
    if (argc > 1) {
        duration = std::atoi(argv[1]);
    }
    
    std::cout << "C++ High-Frequency Trading Simulator" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    HFTEngine engine;
    engine.run(duration);
    
    return 0;
}