// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：eager.cpp

#include <vector>
#include <iostream>
#include <cstddef>

template <typename T>
std::vector<T> lin_space(T start, T stop, std::size_t n) {
    std::vector<T> result;
    // 關鍵技術：reserve 預先配置容量，降低重新配置成本。
    result.reserve(n);
    
    T diff = static_cast<T>(stop - start) / (n - 1);
    
    for (int step = 0; step != n; ++step)
        result.emplace_back(start + (diff * step) );
    
    return result;
}

template <typename T>
void printSpace(const std::vector<T> &ls_results) {
    for (const auto &v : ls_results) {
        std::cout << v << ' ';
    } std::cout << '\n';
}

int main()
{
    printSpace(lin_space(2.0f, 3.0f, 5));
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 2 2.25 2.5 2.75 3
// Program ended with exit code: 0
