#include <iostream>
#include <tbb/parallel_for.h>
#include <vector>
#include <cmath>
#include <mutex>

int main() {
    size_t n = 1<<13;
    std::vector<float> a(n * n);
    std::recursive_mutex mtx;

    tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t i) {
        std::lock_guard lck(mtx);
        tbb::parallel_for((size_t)0, (size_t)n, [&] (size_t j) {
            a[i * n + j] = std::sin(i) * std::sin(j);
        });
    });

    return 0;
}
