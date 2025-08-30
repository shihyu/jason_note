#include <iostream>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <algorithm>
#include <numeric>
#include <cstring>
#include <fstream>
#include <random>

#include <pthread.h>
#include <sched.h>
#include <unistd.h>
#include <sys/syscall.h>
#include <sys/resource.h>
// #include <numa.h>  // Optional: NUMA support

using namespace std;
using namespace chrono;

class CPUAffinityManager {
public:
    // 獲取系統 CPU 數量
    static int get_cpu_count() {
        return sysconf(_SC_NPROCESSORS_ONLN);
    }
    
    // 獲取當前執行緒運行的 CPU
    static int get_current_cpu() {
        return sched_getcpu();
    }
    
    // 將執行緒綁定到特定 CPU
    static bool pin_thread_to_cpu(int cpu_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(cpu_id, &cpuset);
        
        pthread_t thread = pthread_self();
        int result = pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset);
        
        if (result != 0) {
            cerr << "設定 CPU 親和性失敗: " << strerror(result) << endl;
            return false;
        }
        
        return true;
    }
    
    // 將執行緒綁定到多個 CPU
    static bool pin_thread_to_cpus(const vector<int>& cpu_ids) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        
        for (int cpu : cpu_ids) {
            CPU_SET(cpu, &cpuset);
        }
        
        pthread_t thread = pthread_self();
        return pthread_setaffinity_np(thread, sizeof(cpu_set_t), &cpuset) == 0;
    }
    
    // 設置執行緒優先級
    static bool set_thread_priority(int priority) {
        struct sched_param param;
        param.sched_priority = priority;
        
        pthread_t thread = pthread_self();
        return pthread_setschedparam(thread, SCHED_FIFO, &param) == 0;
    }
    
    // 設置即時優先級
    static bool set_realtime_priority(int priority = 99) {
        struct sched_param param;
        param.sched_priority = priority;
        
        if (sched_setscheduler(0, SCHED_FIFO, &param) != 0) {
            cerr << "設定即時優先級失敗 (需要 root 權限?)" << endl;
            return false;
        }
        
        return true;
    }
    
    // 獲取 NUMA 節點資訊
    static void print_numa_info() {
        cout << "NUMA 資訊: (libnuma 不可用 - 安裝 libnuma-dev 以獲得完整支援)" << endl;
        // Basic NUMA detection via /sys
        ifstream numa_nodes("/sys/devices/system/node/online");
        if (numa_nodes) {
            string nodes;
            getline(numa_nodes, nodes);
            cout << "線上 NUMA 節點: " << nodes << endl;
        }
    }
    
    // 將記憶體綁定到 NUMA 節點
    static void* allocate_on_numa_node(size_t size, int node) {
        // Fallback to standard allocation without libnuma
        (void)node;  // Unused parameter
        return malloc(size);
    }
};

// CPU 親和性測試
class AffinityBenchmark {
private:
    static constexpr int ITERATIONS = 100000000;
    
    // 簡單的 CPU 密集型工作
    static double cpu_intensive_work(int iterations) {
        double result = 1.0;
        for (int i = 0; i < iterations; i++) {
            result = result * 1.000001 + 0.000001;
            if (i % 1000 == 0) {
                result = sqrt(result);
            }
        }
        return result;
    }
    
    // 記憶體密集型工作
    static long memory_intensive_work(void* buffer, size_t size) {
        char* mem = static_cast<char*>(buffer);
        long sum = 0;
        
        for (size_t i = 0; i < size; i += 64) {  // Cache line stride
            sum += mem[i];
            mem[i] = (char)(sum & 0xFF);
        }
        
        return sum;
    }
    
public:
    // 測試不同 CPU 綁定策略
    static void test_cpu_affinity() {
        int num_cpus = CPUAffinityManager::get_cpu_count();
        cout << "\n=== CPU 親和性測試 ===" << endl;
        cout << "可用 CPU 數量: " << num_cpus << endl;
        
        const int num_threads = min(4, num_cpus);
        
        // 測試 1: 不綁定 (系統調度)
        cout << "\n測試 1: 無 CPU 親和性 (系統調度)" << endl;
        {
            vector<thread> threads;
            auto start = high_resolution_clock::now();
            
            for (int i = 0; i < num_threads; i++) {
                threads.emplace_back([i]() {
                    cpu_intensive_work(ITERATIONS);
                    cout << "執行緒 " << i << " 在 CPU " 
                         << CPUAffinityManager::get_current_cpu() << " 上完成" << endl;
                });
            }
            
            for (auto& t : threads) {
                t.join();
            }
            
            auto duration = high_resolution_clock::now() - start;
            cout << "時間: " << duration_cast<milliseconds>(duration).count() << " 毫秒" << endl;
        }
        
        // 測試 2: 綁定到不同 CPU
        cout << "\n測試 2: 每個執行緒綁定到不同 CPU" << endl;
        {
            vector<thread> threads;
            auto start = high_resolution_clock::now();
            
            for (int i = 0; i < num_threads; i++) {
                threads.emplace_back([i]() {
                    CPUAffinityManager::pin_thread_to_cpu(i);
                    cpu_intensive_work(ITERATIONS);
                    cout << "執行緒 " << i << " 在 CPU " 
                         << CPUAffinityManager::get_current_cpu() << " 上完成" << endl;
                });
            }
            
            for (auto& t : threads) {
                t.join();
            }
            
            auto duration = high_resolution_clock::now() - start;
            cout << "時間: " << duration_cast<milliseconds>(duration).count() << " 毫秒" << endl;
        }
        
        // 測試 3: 所有綁定到同一 CPU (錯誤示範)
        cout << "\n測試 3: 所有執行緒綁定到同一 CPU (錯誤示範)" << endl;
        {
            vector<thread> threads;
            auto start = high_resolution_clock::now();
            
            for (int i = 0; i < num_threads; i++) {
                threads.emplace_back([i]() {
                    CPUAffinityManager::pin_thread_to_cpu(0);  // 都綁定到 CPU 0
                    cpu_intensive_work(ITERATIONS);
                    cout << "執行緒 " << i << " 在 CPU " 
                         << CPUAffinityManager::get_current_cpu() << " 上完成" << endl;
                });
            }
            
            for (auto& t : threads) {
                t.join();
            }
            
            auto duration = high_resolution_clock::now() - start;
            cout << "時間: " << duration_cast<milliseconds>(duration).count() << " 毫秒" << endl;
        }
    }
    
    // 測試 NUMA 親和性
    static void test_numa_affinity() {
        cout << "\n=== NUMA 親和性測試 ===" << endl;
        
        CPUAffinityManager::print_numa_info();
        
        // Simple memory access test without libnuma
        const size_t buffer_size = 100 * 1024 * 1024;  // 100 MB
        
        cout << "\n記憶體存取測試:" << endl;
        void* buffer = malloc(buffer_size);
        
        if (buffer) {
            memset(buffer, 0, buffer_size);
            
            auto start = high_resolution_clock::now();
            long result = memory_intensive_work(buffer, buffer_size);
            auto duration = high_resolution_clock::now() - start;
            
            cout << "記憶體存取時間: " 
                 << duration_cast<microseconds>(duration).count() << " 微秒" << endl;
            cout << "(完整 NUMA 測試需要 libnuma-dev)" << endl;
            
            free(buffer);
        }
    }
    
    // 測試執行緒優先級
    static void test_thread_priority() {
        cout << "\n=== 執行緒優先級測試 ===" << endl;
        
        atomic<int> counter{0};
        atomic<bool> running{true};
        
        // 低優先級執行緒
        thread low_prio([&]() {
            nice(19);  // 最低優先級
            
            while (running) {
                counter++;
                this_thread::yield();
            }
        });
        
        // 高優先級執行緒
        thread high_prio([&]() {
            nice(-20);  // 最高優先級 (需要 root)
            // 或使用即時優先級
            // CPUAffinityManager::set_realtime_priority(50);
            
            int local_counter = 0;
            auto start = high_resolution_clock::now();
            
            while (duration_cast<seconds>(high_resolution_clock::now() - start).count() < 1) {
                local_counter++;
            }
            
            running = false;
            cout << "高優先級執行緒迭代次數: " << local_counter << endl;
        });
        
        low_prio.join();
        high_prio.join();
        
        cout << "低優先級執行緒迭代次數: " << counter << endl;
    }
};

// HFT 優化架構示例
class HFTOptimizedArchitecture {
private:
    struct alignas(64) CacheLinePadded {  // 避免 false sharing
        atomic<long> value{0};
        char padding[64 - sizeof(atomic<long>)];
    };
    
public:
    static void demonstrate_hft_setup() {
        cout << "\n=== HFT 優化設定 ===" << endl;
        
        int num_cpus = CPUAffinityManager::get_cpu_count();
        
        // 1. 網路 IO 執行緒 (CPU 0)
        thread io_thread([]() {
            CPUAffinityManager::pin_thread_to_cpu(0);
            CPUAffinityManager::set_realtime_priority(99);
            
            cout << "IO 執行緒在 CPU " << CPUAffinityManager::get_current_cpu() 
                 << " 上使用即時優先級" << endl;
            
            // 模擬 IO 處理
            for (int i = 0; i < 1000000; i++) {
                // 接收市場數據
                // 放入無鎖隊列
                this_thread::yield();
            }
        });
        
        // 2. 策略計算執行緒 (CPU 1-2)
        vector<thread> calc_threads;
        for (int cpu = 1; cpu <= min(2, num_cpus - 1); cpu++) {
            calc_threads.emplace_back([cpu]() {
                CPUAffinityManager::pin_thread_to_cpu(cpu);
                
                cout << "計算執行緒在 CPU " << CPUAffinityManager::get_current_cpu() << " 上" << endl;
                
                // 模擬策略計算
                for (int i = 0; i < 1000000; i++) {
                    // 從隊列獲取數據
                    // 計算信號
                    // 生成訂單
                    this_thread::yield();
                }
            });
        }
        
        // 3. 日誌執行緒 (最後一個 CPU)
        thread log_thread([num_cpus]() {
            CPUAffinityManager::pin_thread_to_cpu(num_cpus - 1);
            nice(10);  // 低優先級
            
            cout << "日誌執行緒在 CPU " << CPUAffinityManager::get_current_cpu() 
                 << " 上使用低優先級" << endl;
            
            // 模擬日誌處理
            for (int i = 0; i < 100000; i++) {
                // 異步日誌寫入
                this_thread::sleep_for(microseconds(10));
            }
        });
        
        // 等待所有執行緒
        io_thread.join();
        for (auto& t : calc_threads) {
            t.join();
        }
        log_thread.join();
        
        cout << "HFT 設定示範完成" << endl;
    }
    
    // 測試 false sharing
    static void test_false_sharing() {
        cout << "\n=== False Sharing 測試 ===" << endl;
        
        const int num_threads = 4;
        const int iterations = 100000000;
        
        // 測試 1: 有 false sharing
        {
            struct BadLayout {
                atomic<long> counters[4];  // 在同一 cache line
            } bad_data;
            
            auto start = high_resolution_clock::now();
            
            vector<thread> threads;
            for (int i = 0; i < num_threads; i++) {
                threads.emplace_back([&bad_data, i, iterations]() {
                    for (int j = 0; j < iterations; j++) {
                        bad_data.counters[i]++;
                    }
                });
            }
            
            for (auto& t : threads) {
                t.join();
            }
            
            auto duration = high_resolution_clock::now() - start;
            cout << "有 false sharing: " 
                 << duration_cast<milliseconds>(duration).count() << " 毫秒" << endl;
        }
        
        // 測試 2: 無 false sharing
        {
            CacheLinePadded good_data[4];  // 每個在不同 cache line
            
            auto start = high_resolution_clock::now();
            
            vector<thread> threads;
            for (int i = 0; i < num_threads; i++) {
                threads.emplace_back([&good_data, i, iterations]() {
                    for (int j = 0; j < iterations; j++) {
                        good_data[i].value++;
                    }
                });
            }
            
            for (auto& t : threads) {
                t.join();
            }
            
            auto duration = high_resolution_clock::now() - start;
            cout << "無 false sharing: " 
                 << duration_cast<milliseconds>(duration).count() << " 毫秒" << endl;
        }
    }
};

int main() {
    cout << "=== CPU 親和性與執行緒優化測試 ===" << endl;
    
    // 基本系統資訊
    cout << "\n系統資訊:" << endl;
    cout << "CPU 數量: " << CPUAffinityManager::get_cpu_count() << endl;
    cout << "目前 CPU: " << CPUAffinityManager::get_current_cpu() << endl;
    
    // 執行測試
    AffinityBenchmark::test_cpu_affinity();
    AffinityBenchmark::test_numa_affinity();
    AffinityBenchmark::test_thread_priority();
    
    // HFT 優化示範
    HFTOptimizedArchitecture::demonstrate_hft_setup();
    HFTOptimizedArchitecture::test_false_sharing();
    
    cout << "\n所有測試完成!" << endl;
    return 0;
}