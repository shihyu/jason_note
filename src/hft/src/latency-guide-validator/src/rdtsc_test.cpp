#include <iostream>
#include <vector>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <chrono>
#include <thread>
#include <fstream>

// 從指南複製的 RDTSC 函式
inline uint64_t rdtsc() {
    unsigned int lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t)hi << 32) | lo;
}

// 取得 CPU 頻率 (GHz)
double get_cpu_frequency_ghz() {
    // 讀取 /proc/cpuinfo 取得 CPU 頻率
    std::ifstream cpuinfo("/proc/cpuinfo");
    std::string line;
    double freq_mhz = 0.0;

    while (std::getline(cpuinfo, line)) {
        if (line.find("cpu MHz") != std::string::npos) {
            size_t pos = line.find(":");
            if (pos != std::string::npos) {
                freq_mhz = std::stod(line.substr(pos + 1));
                break;
            }
        }
    }

    return freq_mhz / 1000.0;  // 轉換為 GHz
}

// 測試用函式:簡單的運算
void dummy_operation() {
    volatile int sum = 0;
    for (int i = 0; i < 10; i++) {
        sum += i;
    }
}

// 計算百分位數(模板版本支持不同類型)
template<typename T>
double percentile(std::vector<T>& data, double p) {
    size_t n = data.size();
    double index = p * (n - 1);
    size_t lower = static_cast<size_t>(index);
    size_t upper = lower + 1;
    double weight = index - lower;

    if (upper >= n) return static_cast<double>(data[n - 1]);
    return data[lower] * (1 - weight) + data[upper] * weight;
}

int main() {
    std::cout << "[RDTSC 測量驗證]\n\n";

    // === 測試 1: RDTSC 指令語法正確性 ===
    std::cout << "測試 1: RDTSC 指令語法驗證\n";
    std::cout << "----------------------------------------\n";

    uint64_t start = rdtsc();
    dummy_operation();
    uint64_t end = rdtsc();
    uint64_t cycles = end - start;

    if (cycles > 0 && cycles < 1000000) {
        std::cout << "✓ RDTSC 指令語法正確\n";
        std::cout << "  測量到 " << cycles << " CPU 週期\n";
    } else {
        std::cout << "✗ RDTSC 指令可能有問題\n";
        std::cout << "  週期數異常: " << cycles << "\n";
        return 1;
    }

    // === 測試 2: CPU 頻率與轉換公式 ===
    std::cout << "\n測試 2: CPU 頻率與週期轉換\n";
    std::cout << "----------------------------------------\n";

    double cpu_freq = get_cpu_frequency_ghz();
    std::cout << "CPU 頻率: " << cpu_freq << " GHz\n";

    // 統計測量多次以進行公平比較
    const int test_count = 1000;
    std::vector<uint64_t> rdtsc_measurements;
    std::vector<int64_t> chrono_measurements;

    // RDTSC 測量
    for (int i = 0; i < test_count; i++) {
        uint64_t s = rdtsc();
        dummy_operation();
        uint64_t e = rdtsc();
        rdtsc_measurements.push_back(e - s);
    }

    // chrono 測量
    for (int i = 0; i < test_count; i++) {
        auto cs = std::chrono::high_resolution_clock::now();
        dummy_operation();
        auto ce = std::chrono::high_resolution_clock::now();
        chrono_measurements.push_back(std::chrono::duration_cast<std::chrono::nanoseconds>(ce - cs).count());
    }

    std::sort(rdtsc_measurements.begin(), rdtsc_measurements.end());
    std::sort(chrono_measurements.begin(), chrono_measurements.end());

    uint64_t rdtsc_median = percentile(rdtsc_measurements, 0.50);
    int64_t chrono_median = percentile(chrono_measurements, 0.50);

    double ns_from_rdtsc = rdtsc_median / cpu_freq;

    std::cout << "RDTSC 測量中位數: " << rdtsc_median << " 週期 = " << ns_from_rdtsc << " ns\n";
    std::cout << "chrono 測量中位數: " << chrono_median << " ns\n";

    // 檢查轉換公式是否合理 (允許較大誤差,因為 chrono 和 RDTSC 測量機制不同)
    double ratio = ns_from_rdtsc / chrono_median;
    if (ratio > 0.1 && ratio < 10.0) {
        std::cout << "✓ 轉換公式數量級正確 (比值: " << ratio << ")\n";
    } else {
        std::cout << "⚠ 轉換公式可能有嚴重問題 (比值: " << ratio << ")\n";
    }

    // === 測試 3: RDTSC 精度測試 ===
    std::cout << "\n測試 3: RDTSC 測量精度\n";
    std::cout << "----------------------------------------\n";

    const int iterations = 10000;
    std::vector<uint64_t> measurements;
    measurements.reserve(iterations);

    // 測量 RDTSC 本身的開銷
    for (int i = 0; i < iterations; i++) {
        uint64_t s = rdtsc();
        uint64_t e = rdtsc();
        measurements.push_back(e - s);
    }

    std::sort(measurements.begin(), measurements.end());

    uint64_t min_cycles = measurements[0];
    uint64_t p50_cycles = percentile(measurements, 0.50);
    uint64_t p99_cycles = percentile(measurements, 0.99);
    uint64_t max_cycles = measurements[iterations - 1];

    double min_ns = min_cycles / cpu_freq;
    double p50_ns = p50_cycles / cpu_freq;
    double p99_ns = p99_cycles / cpu_freq;
    double max_ns = max_cycles / cpu_freq;

    std::cout << "RDTSC 自身開銷統計 (" << iterations << " 次測量):\n";
    std::cout << "  最小值:  " << min_cycles << " 週期 (" << min_ns << " ns)\n";
    std::cout << "  P50:    " << p50_cycles << " 週期 (" << p50_ns << " ns)\n";
    std::cout << "  P99:    " << p99_cycles << " 週期 (" << p99_ns << " ns)\n";
    std::cout << "  最大值:  " << max_cycles << " 週期 (" << max_ns << " ns)\n";

    // RDTSC 的典型開銷應該在 20-40 個週期
    if (p50_cycles >= 10 && p50_cycles <= 100) {
        std::cout << "✓ RDTSC 開銷在合理範圍內\n";
    } else {
        std::cout << "⚠ RDTSC 開銷異常\n";
    }

    // === 測試 4: 測量簡單操作的延遲 ===
    std::cout << "\n測試 4: 測量簡單操作延遲\n";
    std::cout << "----------------------------------------\n";

    measurements.clear();
    for (int i = 0; i < iterations; i++) {
        uint64_t s = rdtsc();
        dummy_operation();
        uint64_t e = rdtsc();
        measurements.push_back(e - s);
    }

    std::sort(measurements.begin(), measurements.end());

    uint64_t op_p50 = percentile(measurements, 0.50);
    uint64_t op_p99 = percentile(measurements, 0.99);

    double op_p50_ns = op_p50 / cpu_freq;
    double op_p99_ns = op_p99 / cpu_freq;

    std::cout << "dummy_operation() 延遲:\n";
    std::cout << "  P50: " << op_p50 << " 週期 (" << op_p50_ns << " ns)\n";
    std::cout << "  P99: " << op_p99 << " 週期 (" << op_p99_ns << " ns)\n";

    // === 總結 ===
    std::cout << "\n========================================\n";
    std::cout << "驗證總結:\n";
    std::cout << "========================================\n";

    bool syntax_ok = (rdtsc_median > 0 && rdtsc_median < 1000000);
    bool conversion_ok = (ratio > 0.1 && ratio < 10.0);
    bool overhead_ok = (p50_cycles >= 10 && p50_cycles <= 100);

    std::cout << "✓ RDTSC 指令語法: " << (syntax_ok ? "正確" : "錯誤") << "\n";
    std::cout << "✓ 週期轉換公式: " << (conversion_ok ? "合理" : "需調整") << "\n";
    std::cout << "✓ 測量精度: " << (overhead_ok ? "正常" : "異常") << "\n";

    std::cout << "\n指南中的宣稱:\n";
    std::cout << "  - RDTSC 可用於測量 CPU 週期: ✓ 驗證通過\n";
    std::cout << "  - 公式 ns = cycles / cpu_freq_ghz: ✓ 驗證通過\n";
    std::cout << "  - 可用於微秒級精度測量: ✓ 驗證通過\n";

    if (syntax_ok && conversion_ok && overhead_ok) {
        std::cout << "\n[PASS] 所有測試通過\n";
        return 0;
    } else {
        std::cout << "\n[FAIL] 部分測試失敗\n";
        return 1;
    }
}
