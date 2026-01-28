// 高效能關鍵技術示例
// 章節：Algorithms - 檔案：sar.cpp

#include <algorithm>

#include <vector>
#include <iostream>

template <typename T>
void sar(T &t, std::size_t n) {
    // 關鍵技術：std::rotate 就地旋轉，避免額外配置。
    std::rotate(t.begin(), t.begin() += n, t.end());
}

template <typename T>
void printT(const T &t) {
    for (const auto &e : t) {
        std::cout << e << " ";
    } std::cout << std::endl;
}

int main()
{
    std::vector<int> ivec = { 1, 2, 3, 4, 5, 6 ,7 };
    printT(ivec);
    
    sar(ivec, 3);
    
    printT(ivec);
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 1 2 3 4 5 6 7 
// 4 5 6 7 1 2 3 
// Program ended with exit code: 0
