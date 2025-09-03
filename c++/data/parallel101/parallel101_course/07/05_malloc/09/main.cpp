#include <iostream>
#include <vector>
#include "ticktock.h"

constexpr size_t n = 1<<29;

int main() {
    {
        TICK(first_alloc);
        std::vector<int> arr(n);
        TOCK(first_alloc);
    }

    {
        TICK(second_alloc);
        std::vector<int> arr(n);
        TOCK(second_alloc);
    }
    return 0;
}
