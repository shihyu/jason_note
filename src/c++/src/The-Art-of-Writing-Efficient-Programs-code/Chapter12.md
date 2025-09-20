# Chapter 12: 性能分析和基準測試

## 本章重點

掌握性能分析工具和基準測試方法，學習如何識別性能瓶頸並驗證優化效果。

## 性能分析工具

### 1. Linux perf
```bash
# 基本 CPU 分析
perf record ./program
perf report

# 詳細採樣
perf record -g -F 999 ./program  # 999Hz 採樣率，含呼叫圖

# 即時統計
perf stat ./program

# 快取分析
perf stat -e cache-references,cache-misses ./program

# 分支預測
perf stat -e branches,branch-misses ./program

# 火焰圖生成
perf record -g ./program
perf script | flamegraph.pl > flame.svg
```

### 2. Valgrind 套件
```bash
# Callgrind - CPU 分析
valgrind --tool=callgrind ./program
kcachegrind callgrind.out.*

# Cachegrind - 快取分析
valgrind --tool=cachegrind ./program

# Massif - 堆記憶體分析
valgrind --tool=massif ./program
ms_print massif.out.*

# Memcheck - 記憶體錯誤
valgrind --leak-check=full ./program
```

### 3. Google Performance Tools
```cpp
// 使用 gperftools
#include <gperftools/profiler.h>

int main() {
    ProfilerStart("profile.out");

    // 要分析的程式碼
    intensive_computation();

    ProfilerStop();
}
```

```bash
# 編譯連結
g++ -lprofiler program.cpp

# 分析結果
pprof --text ./program profile.out
pprof --web ./program profile.out
```

## 微基準測試框架

### 1. Google Benchmark
```cpp
#include <benchmark/benchmark.h>

static void BM_StringCreation(benchmark::State& state) {
    for (auto _ : state) {
        std::string empty_string;
    }
}
BENCHMARK(BM_StringCreation);

// 參數化測試
static void BM_VectorPushBack(benchmark::State& state) {
    for (auto _ : state) {
        state.PauseTiming();  // 暫停計時
        std::vector<int> v;
        v.reserve(state.range(0));
        state.ResumeTiming();  // 恢復計時

        for (int i = 0; i < state.range(0); ++i) {
            v.push_back(i);
        }
    }
}
BENCHMARK(BM_VectorPushBack)->Range(8, 8<<10);

BENCHMARK_MAIN();
```

### 2. 自訂基準測試
```cpp
template<typename Func>
class Benchmark {
    Func func;
    std::string name;

public:
    Benchmark(const std::string& n, Func f)
        : name(n), func(f) {}

    void run(size_t iterations = 1000000) {
        // 預熱
        for (size_t i = 0; i < 100; ++i) {
            func();
        }

        // 測量
        auto start = std::chrono::high_resolution_clock::now();
        for (size_t i = 0; i < iterations; ++i) {
            func();
        }
        auto end = std::chrono::high_resolution_clock::now();

        // 統計
        auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>
                       (end - start);
        double ns_per_op = duration.count() / static_cast<double>(iterations);

        std::cout << name << ": "
                  << ns_per_op << " ns/op, "
                  << 1e9/ns_per_op << " ops/sec\n";
    }
};
```

## 性能計數器

### 1. PAPI (Performance API)
```cpp
#include <papi.h>

void measure_cache() {
    int events[2] = {PAPI_L1_DCM, PAPI_L2_DCM};
    long long values[2];

    PAPI_start_counters(events, 2);

    // 執行要測量的程式碼
    process_data();

    PAPI_stop_counters(values, 2);

    std::cout << "L1 cache misses: " << values[0] << "\n";
    std::cout << "L2 cache misses: " << values[1] << "\n";
}
```

### 2. Intel PCM
```cpp
#include <cpucounters.h>

void monitor_performance() {
    PCM* m = PCM::getInstance();
    m->program();

    SystemCounterState before = getSystemCounterState();

    // 執行工作負載
    heavy_computation();

    SystemCounterState after = getSystemCounterState();

    std::cout << "Instructions per cycle: "
              << getIPC(before, after) << "\n";
    std::cout << "L3 cache hit ratio: "
              << getL3CacheHitRatio(before, after) << "\n";
}
```

## 視覺化工具

### 1. 火焰圖 (Flame Graphs)
```bash
# 生成 perf 火焰圖
git clone https://github.com/brendangregg/FlameGraph
perf record -g ./program
perf script | ./FlameGraph/stackcollapse-perf.pl | \
    ./FlameGraph/flamegraph.pl > perf-flame.svg

# 差異火焰圖
perf record -g ./program_before -o perf.before
perf record -g ./program_after -o perf.after
# 生成差異圖...
```

### 2. Intel VTune
```bash
# 基本熱點分析
vtune -collect hotspots ./program

# 微架構分析
vtune -collect uarch-exploration ./program

# 記憶體存取分析
vtune -collect memory-access ./program

# GUI 檢視結果
vtune-gui result_dir
```

## 程式碼層級分析

### 1. 手動計時
```cpp
class Timer {
    using Clock = std::chrono::high_resolution_clock;
    Clock::time_point start;
    std::string name;

public:
    Timer(const std::string& n) : name(n), start(Clock::now()) {}

    ~Timer() {
        auto end = Clock::now();
        auto duration = std::chrono::duration_cast<std::chrono::microseconds>
                       (end - start).count();
        std::cout << name << ": " << duration << " μs\n";
    }
};

// 使用 RAII 計時
{
    Timer t("Critical section");
    critical_function();
}  // 自動輸出時間
```

### 2. 統計分析
```cpp
class Statistics {
    std::vector<double> samples;

public:
    void add(double value) {
        samples.push_back(value);
    }

    double mean() const {
        return std::accumulate(samples.begin(), samples.end(), 0.0)
               / samples.size();
    }

    double stddev() const {
        double m = mean();
        double sq_sum = std::accumulate(samples.begin(), samples.end(), 0.0,
            [m](double acc, double val) {
                return acc + (val - m) * (val - m);
            });
        return std::sqrt(sq_sum / samples.size());
    }

    double percentile(double p) const {
        std::vector<double> sorted = samples;
        std::sort(sorted.begin(), sorted.end());
        size_t index = static_cast<size_t>(sorted.size() * p / 100);
        return sorted[index];
    }
};
```

## 持續性能測試

### 1. CI/CD 整合
```yaml
# .github/workflows/benchmark.yml
name: Benchmark
on: [push, pull_request]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run benchmarks
      run: |
        mkdir build && cd build
        cmake -DCMAKE_BUILD_TYPE=Release ..
        make
        ./benchmark --benchmark_format=json > result.json

    - name: Store benchmark result
      uses: benchmark-action/github-action-benchmark@v1
      with:
        tool: 'googlecpp'
        output-file-path: build/result.json
```

### 2. 性能回歸檢測
```cpp
class PerformanceTest {
    static constexpr double REGRESSION_THRESHOLD = 1.1;  // 10% 回歸

    bool check_regression(double current, double baseline) {
        return current > baseline * REGRESSION_THRESHOLD;
    }

public:
    void run_tests() {
        auto current = benchmark_function();
        auto baseline = load_baseline();

        if (check_regression(current, baseline)) {
            throw std::runtime_error("Performance regression detected!");
        }
    }
};
```

## 最佳實踐

### 1. 測量原則
- **測量而非猜測**: 使用工具找出真正的瓶頸
- **代表性工作負載**: 使用實際資料測試
- **多次測量**: 排除異常值和噪音
- **控制環境**: 關閉不必要的程序

### 2. 分析策略
- **自上而下**: 從系統層級到函數層級
- **熱點優先**: 專注於最耗時的部分
- **迭代優化**: 小步前進，持續驗證

### 3. 報告格式
```cpp
struct BenchmarkResult {
    std::string name;
    double mean_time;
    double stddev;
    double min_time;
    double max_time;
    double p50, p90, p99;

    void print() const {
        std::cout << std::format(
            "{}: mean={:.2f}ns, stddev={:.2f}ns, "
            "p50={:.2f}ns, p90={:.2f}ns, p99={:.2f}ns\n",
            name, mean_time, stddev, p50, p90, p99);
    }
};
```

## 常用性能指標

1. **延遲 (Latency)**: 單次操作時間
2. **吞吐量 (Throughput)**: 單位時間操作數
3. **CPU 使用率**: 處理器利用率
4. **記憶體頻寬**: 資料傳輸速率
5. **快取命中率**: L1/L2/L3 快取效率
6. **IPC**: 每週期指令數
7. **分支預測準確率**: 分支預測成功率