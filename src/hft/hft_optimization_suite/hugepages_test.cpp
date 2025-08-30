#include <iostream>
#include <cstring>
#include <cstdlib>
#include <chrono>
#include <random>
#include <vector>
#include <iomanip>
#include <sstream>
#include <fstream>
#include <algorithm>

#include <sys/mman.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
// #include <numa.h>  // Optional: NUMA support

using namespace std;
using namespace chrono;

class HugePagesManager {
private:
    static constexpr size_t PAGE_SIZE_4KB = 4 * 1024;
    static constexpr size_t PAGE_SIZE_2MB = 2 * 1024 * 1024;
    static constexpr size_t PAGE_SIZE_1GB = 1024 * 1024 * 1024;
    
public:
    // 標準記憶體分配
    static void* allocate_standard(size_t size) {
        void* ptr = nullptr;
        if (posix_memalign(&ptr, PAGE_SIZE_4KB, size) != 0) {
            cerr << "Standard allocation failed" << endl;
            return nullptr;
        }
        
        // 預觸摸記憶體
        memset(ptr, 0, size);
        
        // 嘗試鎖定記憶體
        if (mlock(ptr, size) != 0) {
            cerr << "Warning: mlock failed for standard pages" << endl;
        }
        
        return ptr;
    }
    
    // 2MB 大頁面分配
    static void* allocate_hugepages_2mb(size_t size) {
        // 對齊到 2MB 邊界
        size = (size + PAGE_SIZE_2MB - 1) & ~(PAGE_SIZE_2MB - 1);
        
        void* ptr = mmap(
            nullptr,
            size,
            PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB,
            -1,
            0
        );
        
        if (ptr == MAP_FAILED) {
            cerr << "2MB hugepage allocation failed: " << strerror(errno) << endl;
            return nullptr;
        }
        
        // 預觸摸確保分配
        memset(ptr, 0, size);
        
        // 鎖定記憶體
        if (mlock(ptr, size) != 0) {
            cerr << "Warning: mlock failed for 2MB hugepages" << endl;
        }
        
        cout << "Successfully allocated " << size / (1024*1024) << " MB using 2MB hugepages" << endl;
        return ptr;
    }
    
    // 1GB 大頁面分配
    static void* allocate_hugepages_1gb(size_t size) {
        // 對齊到 1GB 邊界
        size = (size + PAGE_SIZE_1GB - 1) & ~(PAGE_SIZE_1GB - 1);
        
        void* ptr = mmap(
            nullptr,
            size,
            PROT_READ | PROT_WRITE,
            MAP_PRIVATE | MAP_ANONYMOUS | MAP_HUGETLB | (30 << MAP_HUGE_SHIFT),
            -1,
            0
        );
        
        if (ptr == MAP_FAILED) {
            cerr << "1GB hugepage allocation failed: " << strerror(errno) << endl;
            return nullptr;
        }
        
        // 預觸摸確保分配
        memset(ptr, 0, size);
        
        // 鎖定記憶體
        if (mlock(ptr, size) != 0) {
            cerr << "Warning: mlock failed for 1GB hugepages" << endl;
        }
        
        cout << "Successfully allocated " << size / (1024*1024*1024) << " GB using 1GB hugepages" << endl;
        return ptr;
    }
    
    // 透明大頁面分配 (THP)
    static void* allocate_thp(size_t size) {
        void* ptr = nullptr;
        
        // 對齊到 2MB 邊界
        if (posix_memalign(&ptr, PAGE_SIZE_2MB, size) != 0) {
            cerr << "THP allocation failed" << endl;
            return nullptr;
        }
        
        // 建議內核使用大頁面
        if (madvise(ptr, size, MADV_HUGEPAGE) != 0) {
            cerr << "madvise MADV_HUGEPAGE failed" << endl;
        }
        
        // 預觸摸記憶體確保分配
        memset(ptr, 0, size);
        
        return ptr;
    }
    
    // 釋放記憶體
    static void deallocate(void* ptr, size_t size, bool is_mmap = false) {
        if (!ptr) return;
        
        munlock(ptr, size);
        
        if (is_mmap) {
            munmap(ptr, size);
        } else {
            free(ptr);
        }
    }
    
    // 顯示系統大頁面資訊
    static void show_hugepage_info() {
        cout << "\n=== System Hugepage Information ===" << endl;
        
        ifstream meminfo("/proc/meminfo");
        string line;
        while (getline(meminfo, line)) {
            if (line.find("Huge") != string::npos) {
                cout << line << endl;
            }
        }
        
        cout << "\nTransparent Hugepage status: ";
        ifstream thp_enabled("/sys/kernel/mm/transparent_hugepage/enabled");
        if (thp_enabled) {
            getline(thp_enabled, line);
            cout << line << endl;
        }
    }
};

class PerformanceTester {
private:
    static constexpr int ITERATIONS = 1000000;
    
    // 隨機訪問測試
    static double measure_random_access(void* ptr, size_t size, size_t stride) {
        if (!ptr) return -1;
        
        char* mem = static_cast<char*>(ptr);
        size_t num_accesses = size / stride;
        
        // 生成隨機訪問索引
        vector<size_t> indices(num_accesses);
        for (size_t i = 0; i < num_accesses; i++) {
            indices[i] = (i * stride) % size;
        }
        
        // 打亂索引順序
        random_device rd;
        mt19937 gen(rd());
        std::shuffle(indices.begin(), indices.end(), gen);
        
        // 預熱
        volatile char dummy = 0;
        for (size_t i = 0; i < min(size_t(1000), num_accesses); i++) {
            dummy += mem[indices[i]];
        }
        
        // 實際測試
        auto start = high_resolution_clock::now();
        
        for (int iter = 0; iter < ITERATIONS; iter++) {
            size_t idx = indices[iter % num_accesses];
            dummy += mem[idx];
        }
        
        auto end = high_resolution_clock::now();
        
        auto duration = duration_cast<nanoseconds>(end - start).count();
        return static_cast<double>(duration) / ITERATIONS;
    }
    
    // 順序訪問測試
    static double measure_sequential_access(void* ptr, size_t size) {
        if (!ptr) return -1;
        
        char* mem = static_cast<char*>(ptr);
        
        // 預熱
        volatile long sum = 0;
        for (size_t i = 0; i < min(size_t(4096), size); i++) {
            sum += mem[i];
        }
        
        // 實際測試
        auto start = high_resolution_clock::now();
        
        for (int iter = 0; iter < 100; iter++) {
            for (size_t i = 0; i < size; i += 64) {  // 64 bytes = cache line
                sum += mem[i];
            }
        }
        
        auto end = high_resolution_clock::now();
        
        auto duration = duration_cast<nanoseconds>(end - start).count();
        return static_cast<double>(duration) / (100 * (size / 64));
    }
    
    // 矩陣乘法測試
    static double measure_matrix_multiply(void* ptr, size_t matrix_size) {
        if (!ptr) return -1;
        
        size_t elem_count = matrix_size * matrix_size;
        double* matrix = static_cast<double*>(ptr);
        
        // 初始化矩陣
        for (size_t i = 0; i < elem_count; i++) {
            matrix[i] = static_cast<double>(i % 100) / 100.0;
        }
        
        double* result = matrix + elem_count;
        double* temp = result + elem_count;
        
        auto start = high_resolution_clock::now();
        
        // 簡單矩陣乘法
        for (size_t i = 0; i < matrix_size; i++) {
            for (size_t j = 0; j < matrix_size; j++) {
                double sum = 0;
                for (size_t k = 0; k < matrix_size; k++) {
                    sum += matrix[i * matrix_size + k] * temp[k * matrix_size + j];
                }
                result[i * matrix_size + j] = sum;
            }
        }
        
        auto end = high_resolution_clock::now();
        
        return duration_cast<milliseconds>(end - start).count();
    }
    
public:
    static void run_benchmark(const string& name, void* ptr, size_t size) {
        cout << "\n=== " << name << " Performance Test ===" << endl;
        
        if (!ptr) {
            cout << "Allocation failed, skipping test" << endl;
            return;
        }
        
        // 隨機訪問測試 (跨頁)
        double random_4k = measure_random_access(ptr, size, 4096);
        double random_2m = measure_random_access(ptr, size, 2 * 1024 * 1024);
        
        // 順序訪問測試
        double sequential = measure_sequential_access(ptr, size);
        
        // 矩陣運算測試 (如果記憶體足夠)
        double matrix = -1;
        size_t matrix_size = 512;  // 512x512 matrix
        if (size >= matrix_size * matrix_size * sizeof(double) * 3) {
            matrix = measure_matrix_multiply(ptr, matrix_size);
        }
        
        // 輸出結果
        cout << fixed << setprecision(2);
        cout << "Random access (4KB stride): " << random_4k << " ns/access" << endl;
        cout << "Random access (2MB stride): " << random_2m << " ns/access" << endl;
        cout << "Sequential access: " << sequential << " ns/access" << endl;
        if (matrix > 0) {
            cout << "Matrix multiply (512x512): " << matrix << " ms" << endl;
        }
    }
    
    static void compare_results(
        const string& baseline_name, double baseline_time,
        const string& test_name, double test_time
    ) {
        if (baseline_time > 0 && test_time > 0) {
            double speedup = baseline_time / test_time;
            cout << test_name << " vs " << baseline_name 
                 << ": " << fixed << setprecision(2) << speedup << "x speedup" << endl;
        }
    }
};

class TLBMonitor {
public:
    static void monitor_tlb_stats() {
        cout << "\n=== TLB Statistics ===" << endl;
        
        // 使用 perf 命令獲取 TLB 統計
        system("perf stat -e dTLB-loads,dTLB-load-misses,iTLB-loads,iTLB-load-misses sleep 0.1 2>&1 | grep TLB");
    }
    
    static void check_cpu_support() {
        cout << "\n=== CPU Hugepage Support ===" << endl;
        
        // 檢查 PSE (Page Size Extension) - 2MB pages
        system("grep -q pse /proc/cpuinfo && echo '2MB pages: Supported' || echo '2MB pages: Not supported'");
        
        // 檢查 PDPE1GB - 1GB pages
        system("grep -q pdpe1gb /proc/cpuinfo && echo '1GB pages: Supported' || echo '1GB pages: Not supported'");
    }
};

int main() {
    cout << "=== HugePages Performance Testing ===" << endl;
    
    // 顯示系統資訊
    TLBMonitor::check_cpu_support();
    HugePagesManager::show_hugepage_info();
    
    // 測試參數
    const size_t TEST_SIZE = 256 * 1024 * 1024;  // 256 MB
    cout << "\nTest memory size: " << TEST_SIZE / (1024*1024) << " MB" << endl;
    
    // 分配不同類型的記憶體
    cout << "\n=== Memory Allocation ===" << endl;
    
    void* standard_mem = HugePagesManager::allocate_standard(TEST_SIZE);
    void* huge_2mb_mem = HugePagesManager::allocate_hugepages_2mb(TEST_SIZE);
    void* thp_mem = HugePagesManager::allocate_thp(TEST_SIZE);
    
    // 嘗試 1GB 大頁面 (需要更大的記憶體)
    void* huge_1gb_mem = nullptr;
    if (TEST_SIZE >= 1024 * 1024 * 1024) {
        huge_1gb_mem = HugePagesManager::allocate_hugepages_1gb(TEST_SIZE);
    }
    
    // 執行性能測試
    cout << "\n=== Running Performance Tests ===" << endl;
    
    // 標準頁面測試
    PerformanceTester::run_benchmark("Standard Pages (4KB)", standard_mem, TEST_SIZE);
    // double std_random_time = 120;  // 假設基準時間
    
    // 2MB 大頁面測試
    if (huge_2mb_mem) {
        PerformanceTester::run_benchmark("HugePages (2MB)", huge_2mb_mem, TEST_SIZE);
    }
    
    // 透明大頁面測試
    if (thp_mem) {
        PerformanceTester::run_benchmark("Transparent HugePages", thp_mem, TEST_SIZE);
    }
    
    // 1GB 大頁面測試
    if (huge_1gb_mem) {
        PerformanceTester::run_benchmark("HugePages (1GB)", huge_1gb_mem, TEST_SIZE);
    }
    
    // 監控 TLB 統計
    TLBMonitor::monitor_tlb_stats();
    
    // 清理
    cout << "\n=== Cleanup ===" << endl;
    HugePagesManager::deallocate(standard_mem, TEST_SIZE, false);
    HugePagesManager::deallocate(huge_2mb_mem, TEST_SIZE, true);
    HugePagesManager::deallocate(thp_mem, TEST_SIZE, false);
    if (huge_1gb_mem) {
        HugePagesManager::deallocate(huge_1gb_mem, TEST_SIZE, true);
    }
    
    cout << "\nTest completed successfully!" << endl;
    return 0;
}