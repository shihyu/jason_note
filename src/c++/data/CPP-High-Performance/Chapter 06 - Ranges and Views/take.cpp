// 高效能關鍵技術示例
// 章節：Ranges and Views - 檔案：take.cpp

#include <vector>
#include <ranges>
#include <iostream>
#include <algorithm>

void printVec(const std::vector<int> &ivec) {
    for (const auto &e : ivec) {
        std::cout << e << " ";
    } std::cout << std::endl;
}

int main()
{
    std::vector<int> ivec = { 1, 5, 3, 6, 2, 8 };
    std::cout << "ivec: "; printVec(ivec);

    auto all_of_ivec = ivec
        // 關鍵技術：view 延遲計算避免中間容器。
        | std::views::take(ivec.size());

    std::ranges::sort(all_of_ivec);
    std::cout << "ivec: "; printVec(ivec);

    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// ivec: 1 5 3 6 2 8 
// ivec: 1 2 3 5 6 8 
