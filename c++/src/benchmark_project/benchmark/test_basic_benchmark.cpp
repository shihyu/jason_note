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

  // Note: This assertion might not work as expected in benchmark
  // due to the way iterations are distributed
}
BENCHMARK(BM_MultiThreaded)->Threads(1);
BENCHMARK(BM_MultiThreaded)->Threads(2);
BENCHMARK(BM_MultiThreaded)->Threads(4);
BENCHMARK(BM_MultiThreaded)->Threads(8);
BENCHMARK(BM_MultiThreaded)->ThreadRange(1, 8);

// 6. 自訂計數器和吞吐量
void ProcessData(size_t bytes) {
  // Simulate data processing
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
// Note: std::string doesn't support += with int(1), so we'll skip it

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