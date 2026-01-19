// 高效能關鍵技術示例
// 章節：Ranges and Views - 檔案：flatten.cpp

#include <vector>
#include <ranges>
#include <iostream>

int main()
{
    std::vector<std::vector<int>> list_of_lists = {
        { 1, 2 },
        { 3, 4, 5 },
        { 5 },
        { 4, 3, 2, 1 }
    };
    
    // 關鍵技術：view 延遲計算避免中間容器。
    auto flattened_view = std::views::join(list_of_lists);
    
    for (auto element : flattened_view) {
        std::cout << element << " ";
    } std::cout << std::endl;
    
    return 0;
}

// output:
// 1 2 3 4 5 5 4 3 2 1
