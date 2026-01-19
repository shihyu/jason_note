// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：join.cpp

#include <thread>
#include <iostream>

void print() {
    std::cout << "Sleeping for three seconds...\n";
    std::this_thread::sleep_for(std::chrono::seconds(3));
    std::cout << "ThreadID: " << std::this_thread::get_id() << '\n';
}

int main()
{
    // 關鍵技術：執行緒生命週期管理。
    std::thread t1(print);
    t1.join();
    
    // std::cout is thread safe
    std::cout << "ThreadID: " << std::this_thread::get_id() << '\n';
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// Sleeping for three seconds...
// ThreadID: 0x16fe87000
// ThreadID: 0x1f38b8100
// Program ended with exit code: 0
