#include <iostream>
#include <map>
#include <unordered_map>
#include <queue>
#include <random>
#include <cstring>
#include "../utils/timer.hpp"

struct Order {
    uint64_t order_id;
    uint64_t price;  // Price in cents to avoid floating point
    uint64_t quantity;
    char side;  // 'B' for buy, 'S' for sell
    uint64_t timestamp;
};

class SimpleOrderBook {
private:
    std::map<uint64_t, std::map<uint64_t, Order>> buy_orders_;   // price -> order_id -> order
    std::map<uint64_t, std::map<uint64_t, Order>> sell_orders_;  // price -> order_id -> order
    uint64_t next_order_id_ = 1;

public:
    uint64_t add_order(uint64_t price, uint64_t quantity, char side) {
        uint64_t order_id = next_order_id_++;
        Order order{order_id, price, quantity, side, Timer::rdtsc()};
        
        if (side == 'B') {
            buy_orders_[price][order_id] = order;
        } else {
            sell_orders_[price][order_id] = order;
        }
        
        return order_id;
    }

    bool cancel_order(uint64_t order_id, uint64_t price, char side) {
        if (side == 'B') {
            auto price_it = buy_orders_.find(price);
            if (price_it != buy_orders_.end()) {
                auto order_it = price_it->second.find(order_id);
                if (order_it != price_it->second.end()) {
                    price_it->second.erase(order_it);
                    if (price_it->second.empty()) {
                        buy_orders_.erase(price_it);
                    }
                    return true;
                }
            }
        } else {
            auto price_it = sell_orders_.find(price);
            if (price_it != sell_orders_.end()) {
                auto order_it = price_it->second.find(order_id);
                if (order_it != price_it->second.end()) {
                    price_it->second.erase(order_it);
                    if (price_it->second.empty()) {
                        sell_orders_.erase(price_it);
                    }
                    return true;
                }
            }
        }
        return false;
    }

    bool modify_order(uint64_t order_id, uint64_t old_price, uint64_t new_quantity, char side) {
        if (side == 'B') {
            auto price_it = buy_orders_.find(old_price);
            if (price_it != buy_orders_.end()) {
                auto order_it = price_it->second.find(order_id);
                if (order_it != price_it->second.end()) {
                    order_it->second.quantity = new_quantity;
                    return true;
                }
            }
        } else {
            auto price_it = sell_orders_.find(old_price);
            if (price_it != sell_orders_.end()) {
                auto order_it = price_it->second.find(order_id);
                if (order_it != price_it->second.end()) {
                    order_it->second.quantity = new_quantity;
                    return true;
                }
            }
        }
        return false;
    }

    std::pair<uint64_t, uint64_t> get_best_bid_ask() {
        uint64_t best_bid = 0;
        uint64_t best_ask = UINT64_MAX;
        
        if (!buy_orders_.empty()) {
            best_bid = buy_orders_.rbegin()->first;  // Highest buy price
        }
        
        if (!sell_orders_.empty()) {
            best_ask = sell_orders_.begin()->first;  // Lowest sell price
        }
        
        return {best_bid, best_ask};
    }

    void clear() {
        buy_orders_.clear();
        sell_orders_.clear();
    }

    size_t size() const {
        size_t total = 0;
        for (const auto& price_level : buy_orders_) {
            total += price_level.second.size();
        }
        for (const auto& price_level : sell_orders_) {
            total += price_level.second.size();
        }
        return total;
    }
};

void test_orderbook_operations() {
    const int NUM_OPERATIONS = 100000;
    const int NUM_WARMUP = 10000;
    
    SimpleOrderBook orderbook;
    std::vector<std::pair<uint64_t, uint64_t>> orders;  // order_id, price
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint64_t> price_dist(9000, 11000);  // Price range: $90 - $110
    std::uniform_int_distribution<uint64_t> quantity_dist(100, 1000);
    std::uniform_int_distribution<int> side_dist(0, 1);
    std::uniform_int_distribution<int> operation_dist(0, 99);
    
    LatencyStats add_stats, cancel_stats, modify_stats, bbo_stats;

    // Warmup - populate orderbook
    for (int i = 0; i < NUM_WARMUP; ++i) {
        uint64_t price = price_dist(gen);
        uint64_t quantity = quantity_dist(gen);
        char side = side_dist(gen) ? 'B' : 'S';
        uint64_t order_id = orderbook.add_order(price, quantity, side);
        orders.push_back({order_id, price});
    }

    std::cout << "Orderbook initialized with " << orderbook.size() << " orders" << std::endl;

    // Test operations
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        int op = operation_dist(gen);
        
        if (op < 40) {  // 40% adds
            uint64_t price = price_dist(gen);
            uint64_t quantity = quantity_dist(gen);
            char side = side_dist(gen) ? 'B' : 'S';
            
            auto t1 = Timer::now();
            uint64_t order_id = orderbook.add_order(price, quantity, side);
            auto t2 = Timer::now();
            
            orders.push_back({order_id, price});
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            add_stats.add_sample(static_cast<double>(duration));
            
        } else if (op < 70 && !orders.empty()) {  // 30% cancels
            std::uniform_int_distribution<size_t> order_dist(0, orders.size() - 1);
            size_t idx = order_dist(gen);
            uint64_t order_id = orders[idx].first;
            uint64_t price = orders[idx].second;
            char side = side_dist(gen) ? 'B' : 'S';
            
            auto t1 = Timer::now();
            orderbook.cancel_order(order_id, price, side);
            auto t2 = Timer::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            cancel_stats.add_sample(static_cast<double>(duration));
            
        } else if (op < 85 && !orders.empty()) {  // 15% modifies
            std::uniform_int_distribution<size_t> order_dist(0, orders.size() - 1);
            size_t idx = order_dist(gen);
            uint64_t order_id = orders[idx].first;
            uint64_t price = orders[idx].second;
            uint64_t new_quantity = quantity_dist(gen);
            char side = side_dist(gen) ? 'B' : 'S';
            
            auto t1 = Timer::now();
            orderbook.modify_order(order_id, price, new_quantity, side);
            auto t2 = Timer::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            modify_stats.add_sample(static_cast<double>(duration));
            
        } else {  // 15% BBO queries
            auto t1 = Timer::now();
            auto [bid, ask] = orderbook.get_best_bid_ask();
            auto t2 = Timer::now();
            
            auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
            bbo_stats.add_sample(static_cast<double>(duration));
        }
    }

    std::cout << "\n========== Order Book Operation Latencies ==========" << std::endl;
    add_stats.print_summary("Add Order");
    cancel_stats.print_summary("Cancel Order");
    modify_stats.print_summary("Modify Order");
    bbo_stats.print_summary("Get BBO");
}

void test_orderbook_matching() {
    const int NUM_OPERATIONS = 10000;
    SimpleOrderBook orderbook;
    LatencyStats matching_stats;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<uint64_t> price_dist(9900, 10100);
    std::uniform_int_distribution<uint64_t> quantity_dist(100, 1000);

    // Populate orderbook with initial orders
    for (int i = 0; i < 1000; ++i) {
        uint64_t price = price_dist(gen);
        uint64_t quantity = quantity_dist(gen);
        orderbook.add_order(price, quantity, i % 2 ? 'B' : 'S');
    }

    // Test matching scenarios
    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        auto [best_bid, best_ask] = orderbook.get_best_bid_ask();
        
        // Simulate aggressive order that crosses the spread
        uint64_t aggressive_price = (i % 2) ? best_ask - 10 : best_bid + 10;
        uint64_t quantity = quantity_dist(gen);
        char side = (i % 2) ? 'B' : 'S';
        
        auto t1 = Timer::now();
        
        // In a real matching engine, this would trigger matching logic
        // For now, we just add the order and get BBO
        orderbook.add_order(aggressive_price, quantity, side);
        auto [new_bid, new_ask] = orderbook.get_best_bid_ask();
        
        auto t2 = Timer::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        matching_stats.add_sample(static_cast<double>(duration));
    }

    matching_stats.print_summary("Order Matching Simulation");
}

void test_orderbook_stress() {
    const int NUM_PRICE_LEVELS = 100;
    const int ORDERS_PER_LEVEL = 100;
    
    SimpleOrderBook orderbook;
    LatencyStats stress_stats;
    
    std::cout << "\n========== Order Book Stress Test ==========" << std::endl;
    std::cout << "Creating " << (NUM_PRICE_LEVELS * ORDERS_PER_LEVEL * 2) 
              << " orders..." << std::endl;

    // Create a deep orderbook
    auto t1 = Timer::now();
    
    // Add buy orders
    for (int level = 0; level < NUM_PRICE_LEVELS; ++level) {
        uint64_t price = 10000 - level * 10;  // Buy prices from 10000 down
        for (int i = 0; i < ORDERS_PER_LEVEL; ++i) {
            orderbook.add_order(price, 100 * (i + 1), 'B');
        }
    }
    
    // Add sell orders
    for (int level = 0; level < NUM_PRICE_LEVELS; ++level) {
        uint64_t price = 10001 + level * 10;  // Sell prices from 10001 up
        for (int i = 0; i < ORDERS_PER_LEVEL; ++i) {
            orderbook.add_order(price, 100 * (i + 1), 'S');
        }
    }
    
    auto t2 = Timer::now();
    auto creation_time = std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count();
    
    std::cout << "Orderbook created in " << creation_time << " ms" << std::endl;
    std::cout << "Total orders: " << orderbook.size() << std::endl;

    // Test BBO retrieval on deep book
    for (int i = 0; i < 10000; ++i) {
        auto t1 = Timer::now();
        auto [bid, ask] = orderbook.get_best_bid_ask();
        auto t2 = Timer::now();
        
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(t2 - t1).count();
        stress_stats.add_sample(static_cast<double>(duration));
    }

    stress_stats.print_summary("BBO on Deep Book");
}

int main(int argc, char* argv[]) {
    std::cout << "==================================================" << std::endl;
    std::cout << "         Order Book Latency Benchmarks           " << std::endl;
    std::cout << "==================================================" << std::endl;

    if (argc > 1) {
        std::string test = argv[1];
        if (test == "ops") {
            test_orderbook_operations();
        } else if (test == "match") {
            test_orderbook_matching();
        } else if (test == "stress") {
            test_orderbook_stress();
        } else {
            std::cerr << "Unknown test: " << test << std::endl;
            std::cerr << "Available tests: ops, match, stress" << std::endl;
            return 1;
        }
    } else {
        // Run all tests
        test_orderbook_operations();
        test_orderbook_matching();
        test_orderbook_stress();
    }

    return 0;
}