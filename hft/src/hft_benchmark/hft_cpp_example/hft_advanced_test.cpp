#include <iostream>
#include <vector>
#include <algorithm>
#include <chrono>
#include <thread>
#include <atomic>
#include <cmath>
#include <iomanip>
#include <numeric>
#include <map>
#include <fstream>
#include <cstring>
#include <sys/mman.h>
#include <sched.h>

using namespace std::chrono;

class HFTBenchmark {
private:
    std::vector<double> latencies;
    std::atomic<uint64_t> total_orders{0};
    std::atomic<bool> running{true};
    
    // 統計數據
    struct Stats {
        double min;
        double max;
        double mean;
        double median;
        double stddev;
        double p50;
        double p90;
        double p95;
        double p99;
        double p999;
        double p9999;
    };
    
public:
    // 取得高精度時間戳
    inline uint64_t get_timestamp() {
        return duration_cast<nanoseconds>(
            high_resolution_clock::now().time_since_epoch()
        ).count();
    }
    
    // 模擬訂單處理
    void process_order() {
        auto start = get_timestamp();
        
        // 模擬訂單處理邏輯
        volatile double dummy = 0;
        for (int i = 0; i < 10; ++i) {
            dummy += i * 3.14159;
        }
        
        auto end = get_timestamp();
        double latency = static_cast<double>(end - start);
        
        latencies.push_back(latency);
        total_orders++;
    }
    
    // 計算百分位數
    double calculate_percentile(double percentile) {
        if (latencies.empty()) return 0;
        
        std::sort(latencies.begin(), latencies.end());
        size_t index = static_cast<size_t>(percentile * latencies.size() / 100.0);
        
        if (index >= latencies.size()) {
            index = latencies.size() - 1;
        }
        
        return latencies[index];
    }
    
    // 計算統計數據
    Stats calculate_stats() {
        Stats stats{};
        
        if (latencies.empty()) return stats;
        
        std::sort(latencies.begin(), latencies.end());
        
        // 基本統計
        stats.min = latencies.front();
        stats.max = latencies.back();
        stats.mean = std::accumulate(latencies.begin(), latencies.end(), 0.0) / latencies.size();
        stats.median = latencies[latencies.size() / 2];
        
        // 標準差
        double variance = 0;
        for (double lat : latencies) {
            variance += std::pow(lat - stats.mean, 2);
        }
        stats.stddev = std::sqrt(variance / latencies.size());
        
        // 百分位數
        stats.p50 = calculate_percentile(50);
        stats.p90 = calculate_percentile(90);
        stats.p95 = calculate_percentile(95);
        stats.p99 = calculate_percentile(99);
        stats.p999 = calculate_percentile(99.9);
        stats.p9999 = calculate_percentile(99.99);
        
        return stats;
    }
    
    // 執行延遲測試
    void run_latency_test(int duration_seconds) {
        std::cout << "\n===== 延遲分布測試 =====" << std::endl;
        
        auto start_time = steady_clock::now();
        auto end_time = start_time + seconds(duration_seconds);
        
        while (steady_clock::now() < end_time) {
            process_order();
        }
        
        auto stats = calculate_stats();
        
        // 輸出結果
        std::cout << std::fixed << std::setprecision(2);
        std::cout << "\n測試結果:" << std::endl;
        std::cout << "總訂單數: " << total_orders << std::endl;
        std::cout << "樣本數: " << latencies.size() << std::endl;
        std::cout << "\n延遲統計 (奈秒):" << std::endl;
        std::cout << "  最小值:   " << stats.min << " ns" << std::endl;
        std::cout << "  最大值:   " << stats.max << " ns" << std::endl;
        std::cout << "  平均值:   " << stats.mean << " ns" << std::endl;
        std::cout << "  中位數:   " << stats.median << " ns" << std::endl;
        std::cout << "  標準差:   " << stats.stddev << " ns" << std::endl;
        std::cout << "\n百分位數:" << std::endl;
        std::cout << "  P50:      " << stats.p50 << " ns" << std::endl;
        std::cout << "  P90:      " << stats.p90 << " ns" << std::endl;
        std::cout << "  P95:      " << stats.p95 << " ns" << std::endl;
        std::cout << "  P99:      " << stats.p99 << " ns" << std::endl;
        std::cout << "  P99.9:    " << stats.p999 << " ns" << std::endl;
        std::cout << "  P99.99:   " << stats.p9999 << " ns" << std::endl;
        
        // 輸出延遲分布直方圖
        print_histogram();
    }
    
    // 列印延遲分布直方圖
    void print_histogram() {
        if (latencies.empty()) return;
        
        std::cout << "\n延遲分布直方圖:" << std::endl;
        
        // 建立區間
        std::map<int, int> histogram;
        double min_lat = *std::min_element(latencies.begin(), latencies.end());
        double max_lat = *std::max_element(latencies.begin(), latencies.end());
        
        int num_bins = 10;
        double bin_width = (max_lat - min_lat) / num_bins;
        
        for (double lat : latencies) {
            int bin = static_cast<int>((lat - min_lat) / bin_width);
            if (bin >= num_bins) bin = num_bins - 1;
            histogram[bin]++;
        }
        
        // 找出最大計數用於縮放
        int max_count = 0;
        for (const auto& pair : histogram) {
            max_count = std::max(max_count, pair.second);
        }
        
        // 列印直方圖
        for (int i = 0; i < num_bins; ++i) {
            double range_start = min_lat + i * bin_width;
            double range_end = min_lat + (i + 1) * bin_width;
            
            std::cout << std::setw(8) << std::fixed << std::setprecision(0) 
                      << range_start << "-" << std::setw(6) << range_end << " ns | ";
            
            int count = histogram[i];
            int bar_length = (count * 50) / max_count;
            
            for (int j = 0; j < bar_length; ++j) {
                std::cout << "█";
            }
            
            std::cout << " " << count << " (" 
                      << std::fixed << std::setprecision(1)
                      << (100.0 * count / latencies.size()) << "%)" << std::endl;
        }
    }
    
    // 吞吐量測試
    void run_throughput_test(int duration_seconds) {
        std::cout << "\n===== 吞吐量測試 =====" << std::endl;
        
        total_orders = 0;
        auto start_time = steady_clock::now();
        auto end_time = start_time + seconds(duration_seconds);
        
        // 不收集延遲數據，專注於吞吐量
        while (steady_clock::now() < end_time) {
            // 簡化的訂單處理
            volatile double dummy = 0;
            for (int i = 0; i < 10; ++i) {
                dummy += i * 3.14159;
            }
            total_orders++;
        }
        
        auto actual_duration = duration_cast<milliseconds>(steady_clock::now() - start_time).count() / 1000.0;
        double throughput = total_orders / actual_duration;
        
        std::cout << "測試時間: " << actual_duration << " 秒" << std::endl;
        std::cout << "總訂單數: " << total_orders << std::endl;
        std::cout << "吞吐量: " << std::fixed << std::setprecision(0) 
                  << throughput << " orders/sec" << std::endl;
        std::cout << "平均延遲: " << std::fixed << std::setprecision(2)
                  << (1000000000.0 / throughput) << " ns/order" << std::endl;
    }
    
    // CPU 親和性測試
    void run_cpu_affinity_test(int cpu_id, int duration_seconds) {
        std::cout << "\n===== CPU 親和性測試 (CPU " << cpu_id << ") =====" << std::endl;
        
        // 設定 CPU 親和性
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        
        if (sched_setaffinity(0, sizeof(cpu_set_t), &cpuset) == -1) {
            std::cerr << "無法設定 CPU 親和性" << std::endl;
            return;
        }
        
        // 執行測試
        latencies.clear();
        total_orders = 0;
        
        auto start_time = steady_clock::now();
        auto end_time = start_time + seconds(duration_seconds);
        
        while (steady_clock::now() < end_time) {
            process_order();
        }
        
        auto stats = calculate_stats();
        
        std::cout << "CPU " << cpu_id << " 測試結果:" << std::endl;
        std::cout << "  平均延遲: " << stats.mean << " ns" << std::endl;
        std::cout << "  P50: " << stats.p50 << " ns" << std::endl;
        std::cout << "  P99: " << stats.p99 << " ns" << std::endl;
    }
    
    // 記憶體配置測試
    void run_memory_allocation_test() {
        std::cout << "\n===== 記憶體配置測試 =====" << std::endl;
        
        const int num_allocations = 1000000;
        std::vector<double> alloc_times;
        
        // 測試小型配置
        std::cout << "小型配置 (64 bytes):" << std::endl;
        for (int i = 0; i < num_allocations; ++i) {
            auto start = get_timestamp();
            void* ptr = malloc(64);
            auto end = get_timestamp();
            free(ptr);
            
            alloc_times.push_back(static_cast<double>(end - start));
        }
        
        double avg_small = std::accumulate(alloc_times.begin(), alloc_times.end(), 0.0) / alloc_times.size();
        std::cout << "  平均配置時間: " << avg_small << " ns" << std::endl;
        
        // 測試大型配置
        alloc_times.clear();
        std::cout << "大型配置 (1 MB):" << std::endl;
        for (int i = 0; i < 10000; ++i) {
            auto start = get_timestamp();
            void* ptr = malloc(1024 * 1024);
            auto end = get_timestamp();
            free(ptr);
            
            alloc_times.push_back(static_cast<double>(end - start));
        }
        
        double avg_large = std::accumulate(alloc_times.begin(), alloc_times.end(), 0.0) / alloc_times.size();
        std::cout << "  平均配置時間: " << avg_large << " ns" << std::endl;
        
        // 測試記憶體池
        std::cout << "記憶體池配置:" << std::endl;
        std::vector<char> memory_pool(10 * 1024 * 1024); // 10MB 池
        size_t pool_offset = 0;
        alloc_times.clear();
        
        for (int i = 0; i < num_allocations; ++i) {
            auto start = get_timestamp();
            void* ptr = &memory_pool[pool_offset];
            pool_offset = (pool_offset + 64) % memory_pool.size();
            auto end = get_timestamp();
            
            alloc_times.push_back(static_cast<double>(end - start));
        }
        
        double avg_pool = std::accumulate(alloc_times.begin(), alloc_times.end(), 0.0) / alloc_times.size();
        std::cout << "  平均配置時間: " << avg_pool << " ns" << std::endl;
        
        std::cout << "\n效能比較:" << std::endl;
        std::cout << "  記憶體池 vs malloc(64): " << std::fixed << std::setprecision(2) 
                  << (avg_small / avg_pool) << "x 更快" << std::endl;
        std::cout << "  記憶體池 vs malloc(1MB): " << (avg_large / avg_pool) << "x 更快" << std::endl;
    }
    
    // 快取行測試
    void run_cache_line_test() {
        std::cout << "\n===== 快取行測試 =====" << std::endl;
        
        const int array_size = 1024 * 1024 * 10; // 10MB
        std::vector<char> data(array_size);
        
        // 順序存取
        std::cout << "順序存取:" << std::endl;
        auto start = get_timestamp();
        for (int i = 0; i < array_size; ++i) {
            data[i] = i;
        }
        auto end = get_timestamp();
        double sequential_time = static_cast<double>(end - start);
        std::cout << "  時間: " << sequential_time / 1000000 << " ms" << std::endl;
        
        // 隨機存取
        std::cout << "隨機存取:" << std::endl;
        std::vector<int> indices(array_size);
        std::iota(indices.begin(), indices.end(), 0);
        std::random_shuffle(indices.begin(), indices.end());
        
        start = get_timestamp();
        for (int idx : indices) {
            data[idx] = idx;
        }
        end = get_timestamp();
        double random_time = static_cast<double>(end - start);
        std::cout << "  時間: " << random_time / 1000000 << " ms" << std::endl;
        
        // 跨步存取 (模擬快取行衝突)
        std::cout << "跨步存取 (64 bytes):" << std::endl;
        start = get_timestamp();
        for (int i = 0; i < array_size; i += 64) {
            data[i] = i;
        }
        end = get_timestamp();
        double stride_time = static_cast<double>(end - start);
        std::cout << "  時間: " << stride_time / 1000000 << " ms" << std::endl;
        
        std::cout << "\n效能比較:" << std::endl;
        std::cout << "  隨機 vs 順序: " << std::fixed << std::setprecision(2) 
                  << (random_time / sequential_time) << "x 更慢" << std::endl;
        std::cout << "  跨步 vs 順序: " << (stride_time / sequential_time) << "x" << std::endl;
    }
};

int main(int argc, char* argv[]) {
    int test_duration = (argc > 1) ? std::atoi(argv[1]) : 5;
    int test_type = (argc > 2) ? std::atoi(argv[2]) : 0;
    
    std::cout << "=====================================" << std::endl;
    std::cout << "    高頻交易進階效能測試" << std::endl;
    std::cout << "=====================================" << std::endl;
    
    HFTBenchmark benchmark;
    
    switch (test_type) {
        case 0:  // 執行所有測試
            benchmark.run_latency_test(test_duration);
            benchmark.run_throughput_test(test_duration);
            benchmark.run_memory_allocation_test();
            benchmark.run_cache_line_test();
            for (int cpu = 0; cpu < 4; ++cpu) {
                benchmark.run_cpu_affinity_test(cpu, 2);
            }
            break;
        case 1:
            benchmark.run_latency_test(test_duration);
            break;
        case 2:
            benchmark.run_throughput_test(test_duration);
            break;
        case 3:
            benchmark.run_memory_allocation_test();
            break;
        case 4:
            benchmark.run_cache_line_test();
            break;
        case 5:
            for (int cpu = 0; cpu < 4; ++cpu) {
                benchmark.run_cpu_affinity_test(cpu, test_duration);
            }
            break;
        default:
            std::cout << "使用方法: " << argv[0] << " [測試時間(秒)] [測試類型]" << std::endl;
            std::cout << "測試類型:" << std::endl;
            std::cout << "  0 - 所有測試 (預設)" << std::endl;
            std::cout << "  1 - 延遲測試" << std::endl;
            std::cout << "  2 - 吞吐量測試" << std::endl;
            std::cout << "  3 - 記憶體配置測試" << std::endl;
            std::cout << "  4 - 快取行測試" << std::endl;
            std::cout << "  5 - CPU 親和性測試" << std::endl;
    }
    
    return 0;
}