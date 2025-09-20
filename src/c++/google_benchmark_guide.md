# Google Benchmark 完整使用指南

## 目錄
- [簡介](#簡介)
- [安裝方式](#安裝方式)
- [基本使用](#基本使用)
- [進階功能](#進階功能)
- [測試 C 語言程式碼](#測試-c-語言程式碼)
- [編譯與執行](#編譯與執行)
- [最佳實踐](#最佳實踐)
- [輸出解讀](#輸出解讀)
- [完整測試範例程式碼](#完整測試範例程式碼)

## 簡介

Google Benchmark 是一個強大的 C++ 微基準測試（microbenchmarking）函式庫，由 Google 開發並開源。它能夠精確測量程式碼效能，自動處理統計分析，並提供詳細的性能指標。

### 主要特點
- 自動決定迭代次數以獲得統計上有意義的結果
- 支援多執行緒基準測試
- 提供多種輸出格式（控制台、JSON、CSV）
- 防止編譯器優化的機制
- 支援自訂計數器和吞吐量測量
- 可測試 C 和 C++ 程式碼

## 安裝方式

### 方法一：使用 CMake 從源碼安裝

```bash
# 1. 克隆專案
git clone https://github.com/google/benchmark.git
cd benchmark

# 2. 建立建構目錄
cmake -E make_directory "build"

# 3. 產生建構檔案
cmake -E chdir "build" cmake -DBENCHMARK_DOWNLOAD_DEPENDENCIES=on -DCMAKE_BUILD_TYPE=Release ../

# 4. 編譯
cmake --build "build" --config Release

# 5. 安裝到系統（選擇性）
sudo cmake --build "build" --config Release --target install
```

### 方法二：使用 Conan 套件管理器

**conanfile.txt:**
```txt
[requires]
benchmark/1.8.3

[generators]
CMakeDeps
CMakeToolchain
```

安裝指令：
```bash
conan install . --build=missing -s build_type=Release
```

### 方法三：整合到 CMake 專案

**使用 find_package（需先安裝）：**
```cmake
find_package(benchmark REQUIRED)
target_link_libraries(MyTarget benchmark::benchmark)
```

**使用 add_subdirectory（作為子專案）：**
```cmake
add_subdirectory(benchmark)
target_link_libraries(MyTarget benchmark::benchmark)
```

**使用 FetchContent（CMake 3.14+）：**
```cmake
include(FetchContent)
FetchContent_Declare(
  googlebenchmark
  GIT_REPOSITORY https://github.com/google/benchmark.git
  GIT_TAG main
)
FetchContent_MakeAvailable(googlebenchmark)
target_link_libraries(MyTarget benchmark::benchmark)
```

## 基本使用

### 最簡單的範例

```cpp
#include <benchmark/benchmark.h>

static void BM_StringCreation(benchmark::State& state) {
  for (auto _ : state)
    std::string empty_string;
}
// 註冊基準測試
BENCHMARK(BM_StringCreation);

// 定義主函式
BENCHMARK_MAIN();
```

### 測試含參數的函式

```cpp
#include <benchmark/benchmark.h>
#include <vector>
#include <algorithm>

static void BM_VectorSort(benchmark::State& state) {
  // 取得參數（向量大小）
  const int size = state.range(0);

  for (auto _ : state) {
    // 暫停計時器來準備資料
    state.PauseTiming();
    std::vector<int> v(size);
    for (int i = 0; i < size; i++) {
      v[i] = rand() % 1000;
    }
    state.ResumeTiming();

    // 實際要測試的程式碼
    std::sort(v.begin(), v.end());
  }
}

// 測試不同大小：8, 64, 512, 4096
BENCHMARK(BM_VectorSort)->Range(8, 8<<10);

// 或指定特定值
BENCHMARK(BM_VectorSort)->Args({10})->Args({100})->Args({1000});
```

### 防止編譯器優化

```cpp
static void BM_Calculation(benchmark::State& state) {
  for (auto _ : state) {
    int sum = 0;
    for (int i = 0; i < 1000; ++i) {
      sum += i;
    }
    // 防止編譯器優化掉未使用的結果
    benchmark::DoNotOptimize(sum);
  }
}
BENCHMARK(BM_Calculation);
```

## 進階功能

### 1. 使用 Fixture（測試夾具）

適用於需要複雜設定或共享資源的測試：

```cpp
class MyFixture : public benchmark::Fixture {
public:
  void SetUp(const ::benchmark::State& state) override {
    // 在每個基準測試開始前執行
    data.resize(state.range(0));
    std::generate(data.begin(), data.end(), std::rand);
  }

  void TearDown(const ::benchmark::State& state) override {
    // 在每個基準測試結束後執行
    data.clear();
  }

  std::vector<int> data;
};

BENCHMARK_DEFINE_F(MyFixture, SortTest)(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> local_data = data;  // 複製資料
    std::sort(local_data.begin(), local_data.end());
  }
}

BENCHMARK_REGISTER_F(MyFixture, SortTest)->Range(8, 8<<10);
```

### 2. 多執行緒基準測試

```cpp
static void BM_MultiThreaded(benchmark::State& state) {
  static std::mutex mu;
  static int counter = 0;

  if (state.thread_index() == 0) {
    // 只在第一個執行緒執行
    counter = 0;
  }

  for (auto _ : state) {
    std::lock_guard<std::mutex> lock(mu);
    ++counter;
  }
}

// 測試 1, 2, 4, 8 個執行緒
BENCHMARK(BM_MultiThreaded)->Threads(1);
BENCHMARK(BM_MultiThreaded)->Threads(2);
BENCHMARK(BM_MultiThreaded)->Threads(4);
BENCHMARK(BM_MultiThreaded)->Threads(8);

// 或使用 ThreadRange
BENCHMARK(BM_MultiThreaded)->ThreadRange(1, 8);
```

### 3. 自訂計數器和吞吐量

```cpp
void ProcessData(size_t bytes) {
  // 模擬資料處理
  volatile char* data = new char[bytes];
  for (size_t i = 0; i < bytes; ++i) {
    data[i] = static_cast<char>(i);
  }
  delete[] data;
}

static void BM_DataProcessing(benchmark::State& state) {
  const size_t bytes_per_iteration = 1024 * 1024;  // 1MB

  for (auto _ : state) {
    ProcessData(bytes_per_iteration);
  }

  // 設定處理的位元組數（會顯示 MB/s）
  state.SetBytesProcessed(state.iterations() * bytes_per_iteration);

  // 設定處理的項目數（會顯示 items/s）
  state.SetItemsProcessed(state.iterations() * 1000);

  // 自訂計數器
  state.counters["CustomMetric"] = benchmark::Counter(
    state.iterations() * 2.5,
    benchmark::Counter::kIsRate
  );
}
BENCHMARK(BM_DataProcessing);
```

### 4. 統計分析

```cpp
static void BM_SomeFunction(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> v(100);
    std::iota(v.begin(), v.end(), 0);
    std::shuffle(v.begin(), v.end(), std::mt19937{42});
    benchmark::DoNotOptimize(v);
  }
}

// 重複執行以獲得統計資料
BENCHMARK(BM_SomeFunction)
  ->Repetitions(10)           // 重複 10 次
  ->ReportAggregatesOnly()    // 只報告統計結果
  ->DisplayAggregatesOnly();  // 只顯示統計結果

// 或顯示所有資料加上統計
BENCHMARK(BM_SomeFunction)
  ->Repetitions(5)
  ->ComputeStatistics("max", [](const std::vector<double>& v) -> double {
    return *std::max_element(v.begin(), v.end());
  })
  ->ComputeStatistics("min", [](const std::vector<double>& v) -> double {
    return *std::min_element(v.begin(), v.end());
  });
```

### 5. 模板基準測試

```cpp
template <typename T>
static void BM_TemplateTest(benchmark::State& state) {
  T value{};
  for (auto _ : state) {
    value += T(1);
    benchmark::DoNotOptimize(value);
  }
}

BENCHMARK_TEMPLATE(BM_TemplateTest, int);
BENCHMARK_TEMPLATE(BM_TemplateTest, double);
// Note: std::string 不支援 += 與 int(1) 的操作
```

## 測試 C 語言程式碼

Google Benchmark 雖然是 C++ 函式庫，但可以完美地測試 C 語言程式碼。

### 專案結構範例

```
project/
├── src/                    # C 原始碼
│   ├── algorithms.c
│   ├── algorithms.h
│   ├── data_structures.c
│   └── data_structures.h
├── benchmark/              # 基準測試（C++）
│   ├── bench_algorithms.cpp
│   └── bench_data_structures.cpp
├── CMakeLists.txt
└── Makefile
```

### C 程式碼範例

**algorithms.h:**
```c
#ifndef ALGORITHMS_H
#define ALGORITHMS_H

#ifdef __cplusplus
extern "C" {
#endif

// 排序演算法
void bubble_sort(int* arr, int n);
void quick_sort(int* arr, int low, int high);
void merge_sort(int* arr, int n);

// 搜尋演算法
int linear_search(const int* arr, int n, int target);
int binary_search(const int* arr, int n, int target);

// 數學函式
int fibonacci(int n);
int factorial(int n);
int gcd(int a, int b);

#ifdef __cplusplus
}
#endif

#endif // ALGORITHMS_H
```

**algorithms.c:**
```c
#include "algorithms.h"
#include <stdlib.h>
#include <string.h>

void bubble_sort(int* arr, int n) {
    for (int i = 0; i < n - 1; i++) {
        for (int j = 0; j < n - i - 1; j++) {
            if (arr[j] > arr[j + 1]) {
                int temp = arr[j];
                arr[j] = arr[j + 1];
                arr[j + 1] = temp;
            }
        }
    }
}

void quick_sort_helper(int* arr, int low, int high) {
    if (low < high) {
        int pivot = arr[high];
        int i = (low - 1);

        for (int j = low; j < high; j++) {
            if (arr[j] < pivot) {
                i++;
                int temp = arr[i];
                arr[i] = arr[j];
                arr[j] = temp;
            }
        }

        int temp = arr[i + 1];
        arr[i + 1] = arr[high];
        arr[high] = temp;

        int pi = i + 1;

        quick_sort_helper(arr, low, pi - 1);
        quick_sort_helper(arr, pi + 1, high);
    }
}

void quick_sort(int* arr, int low, int high) {
    quick_sort_helper(arr, low, high);
}

void merge(int* arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;

    int* L = (int*)malloc(n1 * sizeof(int));
    int* R = (int*)malloc(n2 * sizeof(int));

    for (int i = 0; i < n1; i++)
        L[i] = arr[left + i];
    for (int j = 0; j < n2; j++)
        R[j] = arr[mid + 1 + j];

    int i = 0, j = 0, k = left;

    while (i < n1 && j < n2) {
        if (L[i] <= R[j]) {
            arr[k] = L[i];
            i++;
        } else {
            arr[k] = R[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        arr[k] = L[i];
        i++;
        k++;
    }

    while (j < n2) {
        arr[k] = R[j];
        j++;
        k++;
    }

    free(L);
    free(R);
}

void merge_sort_helper(int* arr, int left, int right) {
    if (left < right) {
        int mid = left + (right - left) / 2;

        merge_sort_helper(arr, left, mid);
        merge_sort_helper(arr, mid + 1, right);

        merge(arr, left, mid, right);
    }
}

void merge_sort(int* arr, int n) {
    merge_sort_helper(arr, 0, n - 1);
}

int linear_search(const int* arr, int n, int target) {
    for (int i = 0; i < n; i++) {
        if (arr[i] == target) return i;
    }
    return -1;
}

int binary_search(const int* arr, int n, int target) {
    int left = 0;
    int right = n - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;

        if (arr[mid] == target)
            return mid;

        if (arr[mid] < target)
            left = mid + 1;
        else
            right = mid - 1;
    }

    return -1;
}

int fibonacci(int n) {
    if (n <= 1) return n;

    int prev = 0, curr = 1;
    for (int i = 2; i <= n; i++) {
        int next = prev + curr;
        prev = curr;
        curr = next;
    }
    return curr;
}

int factorial(int n) {
    if (n <= 1) return 1;

    int result = 1;
    for (int i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

int gcd(int a, int b) {
    while (b != 0) {
        int temp = b;
        b = a % b;
        a = temp;
    }
    return a;
}
```

### 基準測試程式碼

**bench_algorithms.cpp:**
```cpp
#include <benchmark/benchmark.h>
#include <cstdlib>
#include <cstring>
#include <vector>
#include <algorithm>
#include <numeric>
#include <random>

extern "C" {
    #include "algorithms.h"
}

// 測試排序演算法
class SortingFixture : public benchmark::Fixture {
public:
    void SetUp(const ::benchmark::State& state) override {
        size = state.range(0);
        data = new int[size];
        for (int i = 0; i < size; i++) {
            data[i] = rand() % 10000;
        }
    }

    void TearDown(const ::benchmark::State& state) override {
        delete[] data;
    }

    int* data;
    int size;
};

BENCHMARK_DEFINE_F(SortingFixture, BubbleSort)(benchmark::State& state) {
    for (auto _ : state) {
        int* temp = new int[size];
        memcpy(temp, data, size * sizeof(int));

        bubble_sort(temp, size);

        benchmark::DoNotOptimize(temp);
        delete[] temp;
    }
    state.SetItemsProcessed(state.iterations() * size);
}

BENCHMARK_REGISTER_F(SortingFixture, BubbleSort)
    ->RangeMultiplier(2)
    ->Range(8, 512)  // 減少範圍因為 bubble sort 是 O(n²)
    ->Unit(benchmark::kMicrosecond);

BENCHMARK_DEFINE_F(SortingFixture, QuickSort)(benchmark::State& state) {
    for (auto _ : state) {
        int* temp = new int[size];
        memcpy(temp, data, size * sizeof(int));

        quick_sort(temp, 0, size - 1);

        benchmark::DoNotOptimize(temp);
        delete[] temp;
    }
    state.SetItemsProcessed(state.iterations() * size);
}

BENCHMARK_REGISTER_F(SortingFixture, QuickSort)
    ->RangeMultiplier(2)
    ->Range(8, 8<<10)
    ->Unit(benchmark::kMicrosecond);

BENCHMARK_DEFINE_F(SortingFixture, MergeSort)(benchmark::State& state) {
    for (auto _ : state) {
        int* temp = new int[size];
        memcpy(temp, data, size * sizeof(int));

        merge_sort(temp, size);

        benchmark::DoNotOptimize(temp);
        delete[] temp;
    }
    state.SetItemsProcessed(state.iterations() * size);
}

BENCHMARK_REGISTER_F(SortingFixture, MergeSort)
    ->RangeMultiplier(2)
    ->Range(8, 8<<10)
    ->Unit(benchmark::kMicrosecond);

// 比較 C 和 C++ STL 實作
static void BM_CSort_vs_STLSort(benchmark::State& state) {
    const int size = state.range(0);
    std::vector<int> original(size);
    std::generate(original.begin(), original.end(), std::rand);

    for (auto _ : state) {
        if (state.range(1) == 0) {
            // 測試 C 版本
            int* arr = new int[size];
            std::copy(original.begin(), original.end(), arr);
            bubble_sort(arr, size);
            benchmark::DoNotOptimize(arr);
            delete[] arr;
        } else {
            // 測試 STL 版本
            std::vector<int> v = original;
            std::sort(v.begin(), v.end());
            benchmark::DoNotOptimize(v.data());
        }
    }
}

BENCHMARK(BM_CSort_vs_STLSort)->Args({100, 0})->Args({100, 1});

// 測試 Fibonacci
static void BM_Fibonacci(benchmark::State& state) {
    const int n = state.range(0);

    for (auto _ : state) {
        int result = fibonacci(n);
        benchmark::DoNotOptimize(result);
    }
}

BENCHMARK(BM_Fibonacci)->DenseRange(10, 30, 5);

// 測試 Factorial
static void BM_Factorial(benchmark::State& state) {
    const int n = state.range(0);

    for (auto _ : state) {
        int result = factorial(n);
        benchmark::DoNotOptimize(result);
    }
}

BENCHMARK(BM_Factorial)->Range(5, 20);

// 測試 GCD
static void BM_GCD(benchmark::State& state) {
    const int a = state.range(0);
    const int b = state.range(1);

    for (auto _ : state) {
        int result = gcd(a, b);
        benchmark::DoNotOptimize(result);
    }
}

BENCHMARK(BM_GCD)->Args({48, 18})->Args({1234567, 987654})->Args({1000000, 500000});

// 測試搜尋演算法
static void BM_LinearSearch(benchmark::State& state) {
    const int size = state.range(0);
    int* arr = new int[size];
    for (int i = 0; i < size; i++) {
        arr[i] = i;
    }

    for (auto _ : state) {
        // 搜尋中間元素（平均情況）
        int result = linear_search(arr, size, size / 2);
        benchmark::DoNotOptimize(result);
    }

    delete[] arr;
    state.SetComplexityN(size);
}

BENCHMARK(BM_LinearSearch)->RangeMultiplier(10)->Range(10, 10000)->Complexity();

static void BM_BinarySearch(benchmark::State& state) {
    const int size = state.range(0);
    int* arr = new int[size];
    for (int i = 0; i < size; i++) {
        arr[i] = i;
    }

    for (auto _ : state) {
        // 搜尋中間元素（平均情況）
        int result = binary_search(arr, size, size / 2);
        benchmark::DoNotOptimize(result);
    }

    delete[] arr;
    state.SetComplexityN(size);
}

BENCHMARK(BM_BinarySearch)->RangeMultiplier(10)->Range(10, 10000)->Complexity();

// 組織相關測試
namespace {
    std::vector<int> GenerateTestData(size_t size) {
        std::vector<int> data(size);
        std::iota(data.begin(), data.end(), 0);
        std::shuffle(data.begin(), data.end(), std::mt19937{42});
        return data;
    }

    // 額外的測試：比較不同排序演算法在不同數據大小下的效能
    void RegisterComparisonBenchmarks() {
        // Small arrays (8 - 64)
        static auto small_sort = [](benchmark::State& state, int algo) {
            const int size = state.range(0);
            std::vector<int> original = GenerateTestData(size);

            for (auto _ : state) {
                int* arr = new int[size];
                std::copy(original.begin(), original.end(), arr);

                switch (algo) {
                    case 0: bubble_sort(arr, size); break;
                    case 1: quick_sort(arr, 0, size - 1); break;
                    case 2: merge_sort(arr, size); break;
                }

                benchmark::DoNotOptimize(arr);
                delete[] arr;
            }
            state.SetItemsProcessed(state.iterations() * size);
        };

        benchmark::RegisterBenchmark("SmallArray_BubbleSort", small_sort, 0)->Range(8, 64);
        benchmark::RegisterBenchmark("SmallArray_QuickSort", small_sort, 1)->Range(8, 64);
        benchmark::RegisterBenchmark("SmallArray_MergeSort", small_sort, 2)->Range(8, 64);
    }
}

int main(int argc, char** argv) {
    RegisterComparisonBenchmarks();
    ::benchmark::Initialize(&argc, argv);
    ::benchmark::RunSpecifiedBenchmarks();
    return 0;
}
```

### Makefile 範例

```makefile
# 編譯器設定
CC = gcc
CXX = g++
CFLAGS = -O3 -Wall -Wextra
CXXFLAGS = -O3 -Wall -Wextra -std=c++17
LDFLAGS = -lbenchmark -pthread

# 目錄
SRC_DIR = src
BENCH_DIR = benchmark
BUILD_DIR = build

# 原始檔
C_SOURCES = $(wildcard $(SRC_DIR)/*.c)
C_OBJECTS = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(C_SOURCES))

# 基準測試
BENCH_SOURCES = $(wildcard $(BENCH_DIR)/*.cpp)
BENCH_TARGETS = $(patsubst $(BENCH_DIR)/%.cpp,$(BUILD_DIR)/%_bench,$(BENCH_SOURCES))

# 預設目標
all: $(BUILD_DIR) $(BENCH_TARGETS)

# 建立建構目錄
$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

# 編譯 C 原始檔
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c
	$(CC) $(CFLAGS) -c $< -o $@

# 編譯並連結基準測試
$(BUILD_DIR)/%_bench: $(BENCH_DIR)/%.cpp $(C_OBJECTS)
	$(CXX) $(CXXFLAGS) $< $(C_OBJECTS) $(LDFLAGS) -o $@

# 執行所有基準測試
benchmark: $(BENCH_TARGETS)
	@for bench in $(BENCH_TARGETS); do \
		echo "Running $$bench..."; \
		$$bench; \
		echo ""; \
	done

# 執行並輸出 JSON
benchmark-json: $(BENCH_TARGETS)
	@for bench in $(BENCH_TARGETS); do \
		$$bench --benchmark_format=json > $$bench.json; \
	done

# 清理
clean:
	rm -rf $(BUILD_DIR)

.PHONY: all benchmark benchmark-json clean
```

### CMakeLists.txt 範例

```cmake
cmake_minimum_required(VERSION 3.14)
project(MyProject LANGUAGES C CXX)

# 設定 C 和 C++ 標準
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# 尋找 Google Benchmark
find_package(benchmark REQUIRED)

# C 函式庫
add_library(algorithms STATIC
    src/algorithms.c
    src/data_structures.c
)
target_include_directories(algorithms PUBLIC src)

# 基準測試執行檔
add_executable(bench_algorithms benchmark/bench_algorithms.cpp)
target_link_libraries(bench_algorithms
    algorithms
    benchmark::benchmark
)

# 新增測試目標
enable_testing()
add_test(NAME benchmark_test COMMAND bench_algorithms)
```

## 編譯與執行

### 基本編譯指令

```bash
# 簡單編譯
g++ -std=c++17 -O3 my_benchmark.cpp -lbenchmark -pthread -o my_benchmark

# 混合 C 和 C++
gcc -O3 -c my_c_code.c -o my_c_code.o
g++ -std=c++17 -O3 -c my_benchmark.cpp -o my_benchmark.o
g++ my_benchmark.o my_c_code.o -lbenchmark -pthread -o my_benchmark
```

### 執行選項

```bash
# 基本執行
./my_benchmark

# 只執行符合模式的測試
./my_benchmark --benchmark_filter=BM_StringCreation

# 設定最小執行時間（秒）
./my_benchmark --benchmark_min_time=2.0s

# 輸出格式
./my_benchmark --benchmark_format=console  # 預設
./my_benchmark --benchmark_format=json
./my_benchmark --benchmark_format=csv

# 輸出到檔案
./my_benchmark --benchmark_out=results.json --benchmark_out_format=json

# 顯示記憶體使用
./my_benchmark --benchmark_memory_usage

# 設定重複次數
./my_benchmark --benchmark_repetitions=10

# 報告統計資料
./my_benchmark --benchmark_report_aggregates_only=true

# 列出所有測試但不執行
./my_benchmark --benchmark_list_tests

# 設定時間單位
./my_benchmark --benchmark_time_unit=ns  # ns, us, ms, s
```

## 最佳實踐

### 1. 測試設計原則

- **隔離測試目標**：只測試你關心的程式碼部分
- **避免 I/O 操作**：除非你正在測試 I/O 效能
- **使用合理的資料大小**：測試實際使用場景
- **考慮快取效應**：第一次執行通常較慢

### 2. 防止優化技巧

```cpp
// 防止編譯器優化掉變數
benchmark::DoNotOptimize(data);

// 確保記憶體寫入
benchmark::ClobberMemory();

// 組合使用
static void BM_Example(benchmark::State& state) {
  for (auto _ : state) {
    auto result = ComputeSomething();
    benchmark::DoNotOptimize(result);
    benchmark::ClobberMemory();
  }
}
```

### 3. 環境優化

```bash
# 設定 CPU 為效能模式
sudo cpupower frequency-set -g performance

# 關閉 CPU 頻率調整
echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo

# 綁定到特定 CPU 核心
taskset -c 0 ./my_benchmark

# 設定程序優先級
nice -n -20 ./my_benchmark
```

### 4. 程式碼組織建議

```cpp
// 將相關測試分組
namespace {
  // 測試資料準備
  std::vector<int> GenerateTestData(size_t size) {
    std::vector<int> data(size);
    std::iota(data.begin(), data.end(), 0);
    std::shuffle(data.begin(), data.end(), std::mt19937{42});
    return data;
  }

  // 基準測試群組
  void RegisterSortingBenchmarks() {
    BENCHMARK(BM_BubbleSort)->Range(8, 8<<10);
    BENCHMARK(BM_QuickSort)->Range(8, 8<<10);
    BENCHMARK(BM_MergeSort)->Range(8, 8<<10);
  }
}

int main(int argc, char** argv) {
  RegisterSortingBenchmarks();
  ::benchmark::Initialize(&argc, argv);
  ::benchmark::RunSpecifiedBenchmarks();
  return 0;
}
```

## 輸出解讀

### 基本輸出格式

```
--------------------------------------------------------------------------
Benchmark                   Time             CPU   Iterations
--------------------------------------------------------------------------
BM_StringCreation        9.18 ns         9.17 ns     76143424
BM_StringCopy           30.5 ns         30.5 ns     22864488
BM_VectorSort/10        64.7 ns         64.7 ns     10744601
BM_VectorSort/100        815 ns          815 ns       854951
BM_VectorSort/1000     10183 ns        10183 ns        68647
```

### 欄位說明

- **Benchmark**: 測試名稱和參數
- **Time**: 實際經過時間（包含系統排程等）
- **CPU**: 純 CPU 執行時間
- **Iterations**: 執行次數

### 進階指標

```
BM_DataProcess/1024     2145 ns      2145 ns    326224 1.79688GB/s 465.2k items/s
```

- **Throughput**: 資料吞吐量（GB/s, MB/s, KB/s）
- **Items/s**: 每秒處理項目數

### 統計輸出

```
BM_Example_mean         100 ns       100 ns        10
BM_Example_median        99 ns        99 ns        10
BM_Example_stddev         5 ns         5 ns        10
BM_Example_cv          5.00 %       5.00 %        10
```

- **mean**: 平均值
- **median**: 中位數
- **stddev**: 標準差
- **cv**: 變異係數（stddev/mean）

### 複雜度分析

```
BM_LinearSearch/10      146 ns       146 ns    4799450
BM_LinearSearch/100    1447 ns      1447 ns     483932
BM_LinearSearch/1000  14491 ns     14491 ns      48276
BM_LinearSearch_BigO   14.49 N      14.49 N
BM_LinearSearch_RMS        0 %          0 %
```

- **BigO**: 演算法複雜度估計
- **RMS**: 均方根誤差

## 完整測試範例程式碼

### 基本功能測試程式 (test_basic_benchmark.cpp)

```cpp
#include <benchmark/benchmark.h>
#include <string>
#include <vector>
#include <algorithm>
#include <random>
#include <numeric>
#include <mutex>
#include <cassert>
#include <cstring>

// 1. 最簡單的範例
static void BM_StringCreation(benchmark::State& state) {
  for (auto _ : state)
    std::string empty_string;
}
BENCHMARK(BM_StringCreation);

// 2. 測試含參數的函式
static void BM_VectorSort(benchmark::State& state) {
  const int size = state.range(0);

  for (auto _ : state) {
    state.PauseTiming();
    std::vector<int> v(size);
    for (int i = 0; i < size; i++) {
      v[i] = rand() % 1000;
    }
    state.ResumeTiming();

    std::sort(v.begin(), v.end());
  }
}
BENCHMARK(BM_VectorSort)->Range(8, 8<<10);
BENCHMARK(BM_VectorSort)->Args({10})->Args({100})->Args({1000});

// 3. 防止編譯器優化
static void BM_Calculation(benchmark::State& state) {
  for (auto _ : state) {
    int sum = 0;
    for (int i = 0; i < 1000; ++i) {
      sum += i;
    }
    benchmark::DoNotOptimize(sum);
  }
}
BENCHMARK(BM_Calculation);

// 4. 使用 Fixture（測試夾具）
class MyFixture : public benchmark::Fixture {
public:
  void SetUp(const ::benchmark::State& state) override {
    data.resize(state.range(0));
    std::generate(data.begin(), data.end(), std::rand);
  }

  void TearDown(const ::benchmark::State& state) override {
    data.clear();
  }

  std::vector<int> data;
};

BENCHMARK_DEFINE_F(MyFixture, SortTest)(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> local_data = data;
    std::sort(local_data.begin(), local_data.end());
  }
}
BENCHMARK_REGISTER_F(MyFixture, SortTest)->Range(8, 8<<10);

// 5. 多執行緒基準測試
static void BM_MultiThreaded(benchmark::State& state) {
  static std::mutex mu;
  static int counter = 0;

  if (state.thread_index() == 0) {
    counter = 0;
  }

  for (auto _ : state) {
    std::lock_guard<std::mutex> lock(mu);
    ++counter;
  }
}
BENCHMARK(BM_MultiThreaded)->Threads(1);
BENCHMARK(BM_MultiThreaded)->Threads(2);
BENCHMARK(BM_MultiThreaded)->Threads(4);
BENCHMARK(BM_MultiThreaded)->Threads(8);
BENCHMARK(BM_MultiThreaded)->ThreadRange(1, 8);

// 6. 自訂計數器和吞吐量
void ProcessData(size_t bytes) {
  // 模擬資料處理
  volatile char* data = new char[bytes];
  for (size_t i = 0; i < bytes; ++i) {
    data[i] = static_cast<char>(i);
  }
  delete[] data;
}

static void BM_DataProcessing(benchmark::State& state) {
  const size_t bytes_per_iteration = 1024 * 1024;  // 1MB

  for (auto _ : state) {
    ProcessData(bytes_per_iteration);
  }

  state.SetBytesProcessed(state.iterations() * bytes_per_iteration);
  state.SetItemsProcessed(state.iterations() * 1000);
  state.counters["CustomMetric"] = benchmark::Counter(
    state.iterations() * 2.5,
    benchmark::Counter::kIsRate
  );
}
BENCHMARK(BM_DataProcessing);

// 7. 統計分析
static void BM_SomeFunction(benchmark::State& state) {
  for (auto _ : state) {
    std::vector<int> v(100);
    std::iota(v.begin(), v.end(), 0);
    std::shuffle(v.begin(), v.end(), std::mt19937{42});
    benchmark::DoNotOptimize(v);
  }
}

BENCHMARK(BM_SomeFunction)
  ->Repetitions(10)
  ->ReportAggregatesOnly()
  ->DisplayAggregatesOnly();

BENCHMARK(BM_SomeFunction)
  ->Repetitions(5)
  ->ComputeStatistics("max", [](const std::vector<double>& v) -> double {
    return *std::max_element(v.begin(), v.end());
  })
  ->ComputeStatistics("min", [](const std::vector<double>& v) -> double {
    return *std::min_element(v.begin(), v.end());
  });

// 8. 模板基準測試
template <typename T>
static void BM_TemplateTest(benchmark::State& state) {
  T value{};
  for (auto _ : state) {
    value += T(1);
    benchmark::DoNotOptimize(value);
  }
}

BENCHMARK_TEMPLATE(BM_TemplateTest, int);
BENCHMARK_TEMPLATE(BM_TemplateTest, double);

// 9. 防止優化技巧組合使用
int ComputeSomething() {
  int result = 0;
  for (int i = 0; i < 100; ++i) {
    result += i * 2;
  }
  return result;
}

static void BM_Example(benchmark::State& state) {
  for (auto _ : state) {
    auto result = ComputeSomething();
    benchmark::DoNotOptimize(result);
    benchmark::ClobberMemory();
  }
}
BENCHMARK(BM_Example);

// Main function
BENCHMARK_MAIN();
```

### 編譯和執行指令

```bash
# 編譯基本測試程式
g++ -std=c++17 -O3 test_basic_benchmark.cpp -lbenchmark -pthread -o test_basic_benchmark

# 編譯 C 語言測試程式
gcc -O3 -c algorithms.c -o algorithms.o
g++ -std=c++17 -O3 test_c_benchmark.cpp algorithms.o -lbenchmark -pthread -o test_c_benchmark

# 執行測試
./test_basic_benchmark
./test_c_benchmark

# 執行特定測試
./test_basic_benchmark --benchmark_filter=BM_StringCreation

# 設定最小執行時間
./test_basic_benchmark --benchmark_min_time=0.5s

# 輸出到 JSON
./test_basic_benchmark --benchmark_format=json --benchmark_out=results.json
```

## 疑難排解

### 常見問題

1. **結果不穩定**
   - 確保系統負載低
   - 使用 `--benchmark_repetitions` 增加重複次數
   - 考慮使用 CPU 隔離

2. **測試時間太短**
   - 使用 `--benchmark_min_time` 增加最小執行時間
   - 確保測試的工作量足夠

3. **記憶體洩漏**
   - 使用 Valgrind 或 AddressSanitizer 檢查
   - 確保 SetUp/TearDown 配對

4. **連結錯誤**
   - 確認 `-lbenchmark -pthread` 連結選項
   - 檢查函式庫安裝路徑

## 參考資源

- [Google Benchmark GitHub](https://github.com/google/benchmark)
- [官方使用者指南](https://github.com/google/benchmark/blob/main/docs/user_guide.md)
- [Google Benchmark 討論群組](https://groups.google.com/forum/#!forum/benchmark-discuss)
- [CppCon 演講：Tuning C++](https://www.youtube.com/watch?v=nXaxk27zwlk)

## 總結

Google Benchmark 是 C/C++ 效能測試的強大工具，提供了：
- 精確的時間測量
- 自動化的統計分析
- 豐富的測試配置選項
- 良好的編譯器優化防護
- 支援 C 和 C++ 程式碼測試

無論是簡單的函式測試還是複雜的多執行緒效能分析，Google Benchmark 都能提供可靠的測量結果，幫助開發者優化程式碼效能。
