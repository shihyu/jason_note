// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：coro_iota.cpp

#include <limits>

#include "include_check.h"
#include "generator.h"

#include <iostream>

Generator<int> iota(int start) {
    for (int i = start; i != std::numeric_limits<int>::max(); ++i)
        // 關鍵技術：協程延遲計算/非同步。
        co_yield i;
}

Generator<int> take_until(Generator<int> gen, int value) {
    for (int x : gen) {
        if (x == value) { co_return; }
        co_yield x;
    }
}

int main()
{
    for (const int yield : take_until(iota(2), 5)) {
        std::cout << yield << ", ";
    } std::cout << '\n';
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 2, 3, 4,
// Program ended with exit code: 0
