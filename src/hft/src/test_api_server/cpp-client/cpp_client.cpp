#include <iostream>
#include <string>
#include <vector>
#include <deque>
#include <chrono>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <curl/curl.h>
#include <sstream>
#include <memory>
#include <atomic>

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

// Thread-local CURL handle for connection reuse
thread_local CURL* tls_curl = nullptr;
thread_local struct curl_slist* tls_headers = nullptr;
thread_local std::string tls_response;
thread_local char tls_json_buffer[1024];

class ThreadPoolClient {
private:
    std::string base_url;
    std::vector<double> latencies;
    std::mutex latencies_mutex;
    std::vector<std::thread> thread_pool;
    std::deque<std::pair<int, Order>> work_queue;
    std::mutex queue_mutex;
    std::condition_variable cv;
    std::atomic<bool> stop_flag{false};
    std::atomic<int> active_workers{0};

    static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
        std::string* response = static_cast<std::string*>(userp);
        size_t total_size = size * nmemb;
        response->append(static_cast<char*>(contents), total_size);
        return total_size;
    }

    std::string get_iso_timestamp() {
        auto now = system_clock::now();
        auto time_t = system_clock::to_time_t(now);
        auto us = duration_cast<microseconds>(now.time_since_epoch()) % 1000000;

        char buffer[64];
        struct tm tm_info;
        gmtime_r(&time_t, &tm_info);
        strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%S", &tm_info);

        char final_buffer[128];
        snprintf(final_buffer, sizeof(final_buffer), "%s.%06ldZ", buffer, us.count());

        return std::string(final_buffer);
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

    void worker_thread() {
        // Initialize thread-local CURL handle once
        if (!tls_curl) {
            tls_curl = curl_easy_init();
            if (!tls_curl) return;

            // Set persistent options
            std::string url = base_url + "/order";
            curl_easy_setopt(tls_curl, CURLOPT_URL, url.c_str());
            curl_easy_setopt(tls_curl, CURLOPT_POST, 1L);
            curl_easy_setopt(tls_curl, CURLOPT_WRITEFUNCTION, WriteCallback);
            curl_easy_setopt(tls_curl, CURLOPT_WRITEDATA, &tls_response);

            // Performance optimizations
            curl_easy_setopt(tls_curl, CURLOPT_TCP_NODELAY, 1L);
            curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPALIVE, 1L);
            curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPIDLE, 120L);
            curl_easy_setopt(tls_curl, CURLOPT_TCP_KEEPINTVL, 60L);
            curl_easy_setopt(tls_curl, CURLOPT_HTTP_VERSION, CURL_HTTP_VERSION_1_1);
            curl_easy_setopt(tls_curl, CURLOPT_FRESH_CONNECT, 0L);
            curl_easy_setopt(tls_curl, CURLOPT_FORBID_REUSE, 0L);
            curl_easy_setopt(tls_curl, CURLOPT_TIMEOUT, 30L);
            curl_easy_setopt(tls_curl, CURLOPT_CONNECTTIMEOUT, 5L);

            // Disable unnecessary features
            curl_easy_setopt(tls_curl, CURLOPT_SSL_VERIFYPEER, 0L);
            curl_easy_setopt(tls_curl, CURLOPT_SSL_VERIFYHOST, 0L);
            curl_easy_setopt(tls_curl, CURLOPT_FOLLOWLOCATION, 0L);

            // Pre-create headers
            tls_headers = curl_slist_append(nullptr, "Content-Type: application/json");
            tls_headers = curl_slist_append(tls_headers, "Connection: keep-alive");
            curl_easy_setopt(tls_curl, CURLOPT_HTTPHEADER, tls_headers);

            // Reserve space for response
            tls_response.reserve(4096);
        }

        while (!stop_flag) {
            std::pair<int, Order> work;

            {
                std::unique_lock<std::mutex> lock(queue_mutex);
                cv.wait(lock, [this] { return !work_queue.empty() || stop_flag; });

                if (stop_flag) break;
                if (work_queue.empty()) continue;

                work = work_queue.front();
                work_queue.pop_front();
                active_workers++;
            }

            // Process the order
            process_order(work.first, work.second);
            active_workers--;
        }

        // Cleanup thread-local resources
        if (tls_headers) {
            curl_slist_free_all(tls_headers);
            tls_headers = nullptr;
        }
        if (tls_curl) {
            curl_easy_cleanup(tls_curl);
            tls_curl = nullptr;
        }
    }

    void process_order(int order_id, const Order& order) {
        // Reuse thread-local CURL handle
        if (!tls_curl) return;

        // Clear response buffer
        tls_response.clear();

        // Build JSON directly in thread-local buffer for better performance
        std::string timestamp = get_iso_timestamp();

        snprintf(tls_json_buffer, sizeof(tls_json_buffer),
            "{\"buy_sell\":\"%s\",\"symbol\":%d,\"price\":%.2f,\"quantity\":%d,"
            "\"market_type\":\"%s\",\"price_type\":\"%s\",\"time_in_force\":\"%s\","
            "\"order_type\":\"%s\",\"client_timestamp\":\"%s\"%s%s%s}",
            enum_to_string(order.buy_sell).c_str(),
            order.symbol,
            order.price,
            order.quantity,
            enum_to_string(order.market_type).c_str(),
            enum_to_string(order.price_type).c_str(),
            enum_to_string(order.time_in_force).c_str(),
            enum_to_string(order.order_type).c_str(),
            timestamp.c_str(),
            order.user_def.empty() ? "" : ",\"user_def\":\"",
            order.user_def.empty() ? "" : order.user_def.c_str(),
            order.user_def.empty() ? "" : "\""
        );

        curl_easy_setopt(tls_curl, CURLOPT_POSTFIELDS, tls_json_buffer);
        curl_easy_setopt(tls_curl, CURLOPT_POSTFIELDSIZE, strlen(tls_json_buffer));

        auto start_time = steady_clock::now();
        CURLcode res = curl_easy_perform(tls_curl);
        auto end_time = steady_clock::now();

        if (res == CURLE_OK) {
            long http_code = 0;
            curl_easy_getinfo(tls_curl, CURLINFO_RESPONSE_CODE, &http_code);

            if (http_code == 200) {
                double latency = duration<double, std::milli>(end_time - start_time).count();

                std::lock_guard<std::mutex> lock(latencies_mutex);
                latencies.push_back(latency);
            }
        }
    }

public:
    ThreadPoolClient(const std::string& url = "http://localhost:8080", int num_threads = 10)
        : base_url(url) {

        curl_global_init(CURL_GLOBAL_ALL);

        // Reserve space for latencies to avoid reallocation
        latencies.reserve(10000);

        // Create worker threads
        for (int i = 0; i < num_threads; i++) {
            thread_pool.emplace_back(&ThreadPoolClient::worker_thread, this);
        }
    }

    ~ThreadPoolClient() {
        stop_flag = true;
        cv.notify_all();

        for (auto& t : thread_pool) {
            if (t.joinable()) {
                t.join();
            }
        }

        curl_global_cleanup();
    }

    void submit_order(int order_id, const Order& order) {
        {
            std::lock_guard<std::mutex> lock(queue_mutex);
            work_queue.emplace_back(order_id, order);
        }
        cv.notify_one();
    }

    void wait_completion() {
        while (true) {
            {
                std::lock_guard<std::mutex> lock(queue_mutex);
                if (work_queue.empty() && active_workers == 0) {
                    break;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(1));
        }
    }

    void print_stats() {
        if (latencies.empty()) {
            std::cout << "No successful orders to analyze\n";
            return;
        }

        std::sort(latencies.begin(), latencies.end());

        double min_lat = latencies.front();
        double max_lat = latencies.back();
        double avg_lat = std::accumulate(latencies.begin(), latencies.end(), 0.0) / latencies.size();

        std::cout << "\n=== C++ Client Performance (Optimized) ===\n";
        std::cout << "Total orders: " << latencies.size() << "\n";
        std::cout << std::fixed << std::setprecision(3);
        std::cout << "Min latency: " << min_lat << " ms\n";
        std::cout << "Max latency: " << max_lat << " ms\n";
        std::cout << "Avg latency: " << avg_lat << " ms\n";

        // Percentiles
        auto percentile = [this](int p) {
            size_t index = (latencies.size() * p) / 100;
            if (index >= latencies.size()) index = latencies.size() - 1;
            return latencies[index];
        };

        std::cout << "P50: " << percentile(50) << " ms\n";
        std::cout << "P90: " << percentile(90) << " ms\n";
        std::cout << "P95: " << percentile(95) << " ms\n";
        std::cout << "P99: " << percentile(99) << " ms\n";
    }

    std::vector<double>& get_latencies() { return latencies; }
};

void run_test(int num_orders = 1000, int num_threads = 10, int warmup = 100) {
    Order demo_order = {
        BSAction::Buy,
        2881,
        66.0,
        2000,
        MarketType::Common,
        PriceType::Limit,
        TimeInForce::ROD,
        OrderType::Stock,
        "From_CPP_STABLE"
    };

    ThreadPoolClient client("http://localhost:8080", num_threads);

    // Warmup phase
    if (warmup > 0) {
        std::cout << "Warming up with " << warmup << " orders...\n";
        for (int i = 0; i < warmup; i++) {
            client.submit_order(i, demo_order);
        }
        client.wait_completion();
        client.get_latencies().clear(); // Clear warmup results
    }

    std::cout << "\nC++ Client (Optimized) - Thread-local CURL, pre-allocated buffers\n";
    std::cout << "Sending " << num_orders << " orders with " << num_threads << " threads...\n";

    auto start_time = steady_clock::now();

    for (int i = 0; i < num_orders; i++) {
        client.submit_order(i, demo_order);
    }

    client.wait_completion();

    auto end_time = steady_clock::now();
    double total_time = duration<double>(end_time - start_time).count();

    std::cout << "\nCompleted in " << std::fixed << std::setprecision(2)
              << total_time << " seconds\n";
    std::cout << "Successful: " << client.get_latencies().size() << "\n";
    std::cout << "Throughput: " << (num_orders / total_time) << " orders/sec\n";

    client.print_stats();
}

int main(int argc, char* argv[]) {
    int num_orders = 1000;
    int num_threads = 50;
    int warmup = 100;

    if (argc > 1) num_orders = std::stoi(argv[1]);
    if (argc > 2) num_threads = std::stoi(argv[2]);
    if (argc > 3) warmup = std::stoi(argv[3]);

    run_test(num_orders, num_threads, warmup);

    return 0;
}