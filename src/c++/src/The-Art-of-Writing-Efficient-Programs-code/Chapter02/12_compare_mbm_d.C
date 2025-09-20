// Microbenchmarks for string comparison using Google benchmark (unsigned int with max length)
#include <cstdlib>
#include <cstring>
#include <memory>

#include "benchmark/benchmark.h"

using std::unique_ptr;

bool compare_uint_len(const char* s1, const char* s2, unsigned int l) {
    char c1, c2;
    for (unsigned int i1 = 0, i2 = 0; i1 < l; ++i1, ++i2) {
        c1 = s1[i1]; c2 = s2[i2];
        if (c1 != c2) return c1 > c2;
    }
    return false;
}

void BM_loop_uint_len(benchmark::State& state) {
    const unsigned int N = state.range(0);
    unique_ptr<char[]> s(new char[2*N]);
    ::memset(s.get(), 'a', 2*N*sizeof(char));
    s[2*N-1] = 0;
    const char* s1 = s.get(), *s2 = s1 + N;
    for (auto _ : state) {
        benchmark::DoNotOptimize(compare_uint_len(s1, s2, N));
    }
    state.SetItemsProcessed(N*state.iterations());
}

#define ARGS \
    ->Arg(1<<20)

BENCHMARK(BM_loop_uint_len) ARGS;
BENCHMARK_MAIN();
