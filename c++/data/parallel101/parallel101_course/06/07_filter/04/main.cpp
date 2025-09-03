#include <iostream>
#include <tbb/parallel_for.h>
#include <tbb/concurrent_vector.h>
#include <cmath>
#include "ticktock.h"

int main() {
    size_t n = 1<<27;
    tbb::concurrent_vector<float> a;

    TICK(filter);
    tbb::parallel_for(tbb::blocked_range<size_t>(0, n),
    [&] (tbb::blocked_range<size_t> r) {
        std::vector<float> local_a;
        local_a.reserve(r.size());
        for (size_t i = r.begin(); i < r.end(); i++) {
            float val = std::sin(i);
            if (val > 0) {
                local_a.push_back(val);
            }
        }
        auto it = a.grow_by(local_a.size());
        std::copy(local_a.begin(), local_a.end(), it);
    });
    TOCK(filter);

    return 0;
}
