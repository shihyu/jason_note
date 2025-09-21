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
    ->Range(8, 512)  // Reduced range for bubble sort as it's O(n²)
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
            // 測試 C 版本 (bubble sort)
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