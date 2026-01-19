// 高效能關鍵技術示例
// 章節：Memory Management - 檔案：main.cpp

// 關鍵技術：自訂配置器降低記憶體配置成本。
#include <iostream>
#include <functional>

#include "short_alloc.h"

#include <set>

int main()
{
    // 關鍵技術：自訂配置器降低記憶體配置成本。
    using SmallSet = std::set<int, std::less<int>, short_alloc<int, 512>>;
    
    SmallSet::allocator_type::arena_type stack_arena;
    
    SmallSet unique_numbers(stack_arena);
    
    int n;
    std::cout << "Please enter some numbers: ";
    
    // read from std::cin (use Ctrl + D to escape)
    while (std::cin >> n) { unique_numbers.insert(n); }
    
    // print results
    for (const int &number : unique_numbers) {
        std::cout << number << ' ';
    } std::cout << '\n';
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// Please enter some numbers: 2 5 4 3 6
// 2 3 4 5 6
// Program ended with exit code: 0
