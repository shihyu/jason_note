// hft_simulation.cpp - 模擬高頻交易系統的關鍵路徑
#include <iostream>
#include <vector>
#include <deque>
#include <algorithm>
#include <random>
#include <chrono>
#include <cstring>
#include <cmath>

struct MarketData {
    double bid;
    double ask;
    long timestamp;
    int volume;
};

struct Order {
    enum Type { BUY, SELL };
    Type type;
    double price;
    int quantity;
    long timestamp;
};

class OrderBook {
private:
    std::deque<Order> bids;
    std::deque<Order> asks;
    
public:
    // 這個函數會在火焰圖中顯示為熱點
    void update(const MarketData& data) {
        // 模擬訂單簿更新（簡化版）
        Order bid_order = {Order::BUY, data.bid, data.volume, data.timestamp};
        Order ask_order = {Order::SELL, data.ask, data.volume, data.timestamp};
        
        // 插入排序（實際系統會用更高效的資料結構）
        bids.push_back(bid_order);
        std::sort(bids.begin(), bids.end(), 
                  [](const Order& a, const Order& b) { 
                      return a.price > b.price; 
                  });
        
        asks.push_back(ask_order);
        std::sort(asks.begin(), asks.end(),
                  [](const Order& a, const Order& b) { 
                      return a.price < b.price; 
                  });
        
        // 限制深度
        if (bids.size() > 100) bids.resize(100);
        if (asks.size() > 100) asks.resize(100);
    }
    
    double get_mid_price() const {
        if (bids.empty() || asks.empty()) return 0;
        return (bids.front().price + asks.front().price) / 2.0;
    }
};

class TradingStrategy {
private:
    std::vector<double> price_history;
    const size_t window_size = 20;
    
public:
    // 簡單的均值回歸策略（會佔用 CPU）
    Order* generate_signal(const OrderBook& book) {
        double mid_price = book.get_mid_price();
        price_history.push_back(mid_price);
        
        if (price_history.size() < window_size) {
            return nullptr;
        }
        
        // 計算移動平均（這裡會顯示在火焰圖中）
        double sum = 0;
        for (size_t i = price_history.size() - window_size; 
             i < price_history.size(); i++) {
            sum += price_history[i];
        }
        double ma = sum / window_size;
        
        // 計算標準差（另一個熱點）
        double variance = 0;
        for (size_t i = price_history.size() - window_size; 
             i < price_history.size(); i++) {
            double diff = price_history[i] - ma;
            variance += diff * diff;
        }
        double std_dev = std::sqrt(variance / window_size);
        
        // 簡單的交易信號
        if (mid_price < ma - 2 * std_dev) {
            return new Order{Order::BUY, mid_price, 100, 0};
        } else if (mid_price > ma + 2 * std_dev) {
            return new Order{Order::SELL, mid_price, 100, 0};
        }
        
        return nullptr;
    }
};

class RiskManager {
private:
    double max_position = 10000;
    double current_position = 0;
    double max_loss = -1000;
    double current_pnl = 0;
    
public:
    // 風控檢查（關鍵路徑，需要極快）
    bool check_order(const Order* order) {
        if (!order) return true;
        
        // 檢查持倉限制
        double position_change = (order->type == Order::BUY) ? 
                                order->quantity : -order->quantity;
        
        if (std::abs(current_position + position_change) > max_position) {
            return false;
        }
        
        // 檢查損失限制
        if (current_pnl < max_loss) {
            return false;
        }
        
        return true;
    }
    
    void update_position(const Order* order) {
        if (!order) return;
        
        double position_change = (order->type == Order::BUY) ? 
                                order->quantity : -order->quantity;
        current_position += position_change;
    }
};

// 主要的交易循環
void trading_loop(int num_ticks) {
    OrderBook book;
    TradingStrategy strategy;
    RiskManager risk;
    
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_real_distribution<> price_dist(99.0, 101.0);
    std::uniform_int_distribution<> volume_dist(100, 1000);
    
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < num_ticks; i++) {
        // 生成模擬市場數據
        MarketData data;
        data.bid = price_dist(gen);
        data.ask = data.bid + 0.01;
        data.volume = volume_dist(gen);
        data.timestamp = std::chrono::duration_cast<std::chrono::microseconds>(
            std::chrono::high_resolution_clock::now().time_since_epoch()).count();
        
        // 關鍵路徑開始 >>>
        
        // 1. 更新訂單簿（預期 30% CPU）
        book.update(data);
        
        // 2. 生成交易信號（預期 40% CPU）
        Order* signal = strategy.generate_signal(book);
        
        // 3. 風控檢查（預期 10% CPU）
        if (risk.check_order(signal)) {
            // 4. 發送訂單（預期 20% CPU）
            risk.update_position(signal);
            // 實際系統這裡會發送到交易所
        }
        
        delete signal;
        
        // <<< 關鍵路徑結束
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);
    
    double latency_per_tick = static_cast<double>(duration.count()) / num_ticks;
    std::cout << "Processed " << num_ticks << " ticks\n";
    std::cout << "Average latency: " << latency_per_tick << " microseconds/tick\n";
}

int main() {
    std::cout << "Starting HFT simulation...\n";
    
    // 預熱
    trading_loop(1000);
    
    // 主要測試
    std::cout << "Running main test...\n";
    trading_loop(1000000);
    
    return 0;
}