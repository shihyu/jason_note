// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：async.cpp

#include <iostream>
#include <future>

auto divide(int x, int y) {
    if (!y) { throw std::runtime_error("Oops! Trying to divide by zero..."); }
    return x / float(y);
}

int main()
{
    try {
        // 關鍵技術：非同步任務與結果傳遞。
        std::cout << "Result: " << std::async(divide, 45, 5).get() << '\n';
    } catch (const std::exception &e) {
        std::cout << "Exception caught: " << e.what() << '\n';
    }
    
    return 0;
}
