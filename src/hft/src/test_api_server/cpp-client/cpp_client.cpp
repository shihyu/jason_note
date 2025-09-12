#include <iostream>
#include <string>
#include <vector>
#include <chrono>
#include <thread>
#include <future>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <iomanip>
#include <curl/curl.h>
#include <sstream>

using namespace std::chrono;

enum class BSAction {
    Buy,
    Sell
};

enum class MarketType {
    Common,
    Warrant,
    OddLot,
    Daytime,
    FixedPrice,
    PlaceFirst
};

enum class PriceType {
    Limit,
    Market,
    LimitUp,
    LimitDown,
    Range
};

enum class TimeInForce {
    ROD,
    IOC,
    FOK
};

enum class OrderType {
    Stock,
    Futures,
    Option
};

struct Order {
    BSAction buy_sell;
    int symbol;
    double price;
    int quantity;
    MarketType market_type;
    PriceType price_type;
    TimeInForce time_in_force;
    OrderType order_type;
    std::string user_def;
};

class AsyncOrderClient {
private:
    std::string base_url;
    int num_connections;
    std::vector<double> latencies;
    std::vector<CURL*> curl_handles;
    CURLM* multi_handle;
    
    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, std::string* userp) {
        userp->append((char*)contents, size * nmemb);
        return size * nmemb;
    }
    
    std::string get_iso_timestamp() {
        auto now = system_clock::now();
        auto time_t = system_clock::to_time_t(now);
        auto ms = duration_cast<milliseconds>(now.time_since_epoch()) % 1000;
        
        std::stringstream ss;
        ss << std::put_time(std::gmtime(&time_t), "%Y-%m-%dT%H:%M:%S");
        ss << '.' << std::setfill('0') << std::setw(3) << ms.count() << 'Z';
        return ss.str();
    }
    
    std::string enum_to_string(BSAction action) {
        return action == BSAction::Buy ? "buy" : "sell";
    }
    
    std::string enum_to_string(MarketType type) {
        switch (type) {
            case MarketType::Common: return "common";
            case MarketType::Warrant: return "warrant";
            case MarketType::OddLot: return "odd_lot";
            case MarketType::Daytime: return "daytime";
            case MarketType::FixedPrice: return "fixed_price";
            case MarketType::PlaceFirst: return "place_first";
            default: return "common";
        }
    }
    
    std::string enum_to_string(PriceType type) {
        switch (type) {
            case PriceType::Limit: return "limit";
            case PriceType::Market: return "market";
            case PriceType::LimitUp: return "limit_up";
            case PriceType::LimitDown: return "limit_down";
            case PriceType::Range: return "range";
            default: return "limit";
        }
    }
    
    std::string enum_to_string(TimeInForce tif) {
        switch (tif) {
            case TimeInForce::ROD: return "rod";
            case TimeInForce::IOC: return "ioc";
            case TimeInForce::FOK: return "fok";
            default: return "rod";
        }
    }
    
    std::string enum_to_string(OrderType type) {
        switch (type) {
            case OrderType::Stock: return "stock";
            case OrderType::Futures: return "futures";
            case OrderType::Option: return "option";
            default: return "stock";
        }
    }
    
public:
    AsyncOrderClient(const std::string& url = "http://localhost:8080", int connections = 100) 
        : base_url(url), num_connections(connections), multi_handle(nullptr) {
        curl_global_init(CURL_GLOBAL_ALL);
        multi_handle = curl_multi_init();
        curl_multi_setopt(multi_handle, CURLMOPT_MAX_TOTAL_CONNECTIONS, connections);
    }
    
    ~AsyncOrderClient() {
        for (auto handle : curl_handles) {
            curl_easy_cleanup(handle);
        }
        if (multi_handle) {
            curl_multi_cleanup(multi_handle);
        }
        curl_global_cleanup();
    }
    
    struct OrderResult {
        bool success;
        double round_trip_ms;
        double server_latency_ms;
        std::string response;
        std::string error;
    };
    
    OrderResult place_order_sync(int order_id, const Order& order) {
        CURL* curl = curl_easy_init();
        OrderResult result{false, 0, 0, "", ""};
        
        if (!curl) {
            result.error = "Failed to initialize CURL";
            return result;
        }
        
        // Build JSON string manually
        std::stringstream json_stream;
        json_stream << "{";
        json_stream << "\"buy_sell\":\"" << enum_to_string(order.buy_sell) << "\",";
        json_stream << "\"symbol\":" << order.symbol << ",";  // symbol is integer, not string
        json_stream << "\"price\":" << order.price << ",";
        json_stream << "\"quantity\":" << order.quantity << ",";
        json_stream << "\"market_type\":\"" << enum_to_string(order.market_type) << "\",";
        json_stream << "\"price_type\":\"" << enum_to_string(order.price_type) << "\",";
        json_stream << "\"time_in_force\":\"" << enum_to_string(order.time_in_force) << "\",";
        json_stream << "\"order_type\":\"" << enum_to_string(order.order_type) << "\",";
        json_stream << "\"client_timestamp\":\"" << get_iso_timestamp() << "\"";
        
        if (!order.user_def.empty()) {
            json_stream << ",\"user_def\":\"" << order.user_def << "\"";
        }
        
        json_stream << "}";
        std::string json_str = json_stream.str();
        std::string response_str;
        
        auto start_time = steady_clock::now();
        
        curl_easy_setopt(curl, CURLOPT_URL, (base_url + "/order").c_str());
        curl_easy_setopt(curl, CURLOPT_POST, 1L);
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json_str.c_str());
        curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
        curl_easy_setopt(curl, CURLOPT_WRITEDATA, &response_str);
        
        struct curl_slist* headers = nullptr;
        headers = curl_slist_append(headers, "Content-Type: application/json");
        curl_easy_setopt(curl, CURLOPT_HTTPHEADER, headers);
        
        CURLcode res = curl_easy_perform(curl);
        
        auto end_time = steady_clock::now();
        auto duration = duration_cast<microseconds>(end_time - start_time);
        result.round_trip_ms = duration.count() / 1000.0;
        
        if (res == CURLE_OK) {
            long http_code = 0;
            curl_easy_getinfo(curl, CURLINFO_RESPONSE_CODE, &http_code);
            
            if (http_code == 200) {
                result.success = true;
                result.response = response_str;
                
                // Simple JSON parsing for latency_ms
                size_t pos = response_str.find("\"latency_ms\":");
                if (pos != std::string::npos) {
                    pos += 13; // Skip "latency_ms":
                    size_t end = response_str.find_first_of(",}", pos);
                    if (end != std::string::npos) {
                        std::string latency_str = response_str.substr(pos, end - pos);
                        try {
                            result.server_latency_ms = std::stod(latency_str);
                        } catch (...) {
                            // Parse error, keep default value
                        }
                    }
                }
            }
        } else {
            result.error = curl_easy_strerror(res);
        }
        
        curl_slist_free_all(headers);
        curl_easy_cleanup(curl);
        
        return result;
    }
    
    std::vector<OrderResult> batch_orders(int num_orders, const Order& demo_order) {
        std::vector<std::future<OrderResult>> futures;
        std::vector<OrderResult> results;
        
        // Launch async tasks
        for (int i = 0; i < num_orders; ++i) {
            futures.push_back(
                std::async(std::launch::async, 
                          [this, i, demo_order]() { return place_order_sync(i, demo_order); })
            );
            
            // Limit concurrent connections
            if (futures.size() >= num_connections) {
                for (auto& fut : futures) {
                    auto result = fut.get();
                    if (result.success) {
                        latencies.push_back(result.round_trip_ms);
                    }
                    results.push_back(result);
                }
                futures.clear();
            }
        }
        
        // Get remaining results
        for (auto& fut : futures) {
            auto result = fut.get();
            if (result.success) {
                latencies.push_back(result.round_trip_ms);
            }
            results.push_back(result);
        }
        
        return results;
    }
    
    void print_stats() {
        if (latencies.empty()) {
            std::cout << "No successful orders to analyze\n";
            return;
        }
        
        std::sort(latencies.begin(), latencies.end());
        
        double min_lat = *std::min_element(latencies.begin(), latencies.end());
        double max_lat = *std::max_element(latencies.begin(), latencies.end());
        double avg_lat = std::accumulate(latencies.begin(), latencies.end(), 0.0) / latencies.size();
        
        double median_lat = 0;
        size_t n = latencies.size();
        if (n % 2 == 0) {
            median_lat = (latencies[n/2 - 1] + latencies[n/2]) / 2.0;
        } else {
            median_lat = latencies[n/2];
        }
        
        double variance = 0;
        for (double lat : latencies) {
            variance += std::pow(lat - avg_lat, 2);
        }
        double std_dev = std::sqrt(variance / latencies.size());
        
        std::cout << "\n=== C++ Client Performance Stats ===\n";
        std::cout << "Total orders: " << latencies.size() << "\n";
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "Min latency: " << min_lat << " ms\n";
        std::cout << "Max latency: " << max_lat << " ms\n";
        std::cout << "Avg latency: " << avg_lat << " ms\n";
        std::cout << "Median latency: " << median_lat << " ms\n";
        std::cout << "Std dev: " << std_dev << " ms\n";
        
        // Percentiles
        std::vector<int> percentiles = {50, 90, 95, 99};
        for (int p : percentiles) {
            if (latencies.size() >= 100 || (p <= 95 && latencies.size() >= 20)) {
                size_t index = (latencies.size() * p) / 100;
                if (index >= latencies.size()) index = latencies.size() - 1;
                std::cout << "P" << p << ": " << latencies[index] << " ms\n";
            }
        }
    }
};

void run_test(int num_orders = 1000, int num_connections = 100, int warmup = 100) {
    AsyncOrderClient client("http://localhost:8080", num_connections);
    
    std::cout << "C++ Async Client - Starting test with " << num_orders << " orders\n";
    std::cout << "Using " << num_connections << " concurrent connections\n";
    
    // Create demo Taiwan stock order
    Order demo_order = {
        BSAction::Buy,
        2881,           // symbol
        66.0,           // price
        2000,           // quantity
        MarketType::Common,
        PriceType::Limit,
        TimeInForce::ROD,
        OrderType::Stock,
        "From_CPP"      // user_def
    };
    
    std::cout << "Testing with Taiwan Stock Order: Symbol=" << demo_order.symbol 
              << " Price=NT$" << demo_order.price 
              << " Qty=" << demo_order.quantity << "\n";
    
    if (warmup > 0) {
        std::cout << "\nWarming up with " << warmup << " orders...\n";
        client.batch_orders(warmup, demo_order);
    }
    
    std::cout << "\nSending " << num_orders << " orders...\n";
    
    auto start_time = steady_clock::now();
    auto results = client.batch_orders(num_orders, demo_order);
    auto end_time = steady_clock::now();
    
    auto duration = duration_cast<milliseconds>(end_time - start_time);
    double total_time = duration.count() / 1000.0;
    
    int successful = std::count_if(results.begin(), results.end(), 
                                   [](const auto& r) { return r.success; });
    int failed = num_orders - successful;
    
    std::cout << "\nCompleted in " << std::fixed << std::setprecision(2) 
              << total_time << " seconds\n";
    std::cout << "Successful: " << successful << ", Failed: " << failed << "\n";
    std::cout << "Throughput: " << (num_orders / total_time) << " orders/sec\n";
    
    client.print_stats();
}

int main(int argc, char* argv[]) {
    int num_orders = 1000;
    int num_connections = 100;
    int warmup = 100;
    
    if (argc > 1) num_orders = std::stoi(argv[1]);
    if (argc > 2) num_connections = std::stoi(argv[2]);
    if (argc > 3) warmup = std::stoi(argv[3]);
    
    run_test(num_orders, num_connections, warmup);
    
    return 0;
}