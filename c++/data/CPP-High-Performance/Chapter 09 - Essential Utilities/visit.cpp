// 高效能關鍵技術示例
// 章節：Essential Utilities - 檔案：visit.cpp

#include <variant>
#include <iostream>

int main()
{
    // 關鍵技術：variant/visit 分派降低虛擬呼叫成本。
    std::variant<int, bool, const char*> v = "hello";
    std::visit( [] (auto&& e) { std::cout << e << '\n'; } , v);
    
    v = false;
    std::visit( [] (auto&& e) { std::cout << e << '\n'; } , v);
    
    v = "woof";
    std::visit( [] (auto&& e) { std::cout << e << '\n'; } , v);
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// hello
// 0
// woof
// Program ended with exit code: 0
