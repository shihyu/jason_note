// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：atomic_shared_ptr.cpp

#include <cstdlib>

#include <atomic>
#include <memory>
#include <iostream>
#include <thread>

// global atomic shared_ptr
// 關鍵技術：原子操作避免鎖並維持一致性。
std::atomic<std::shared_ptr<int>> asp;

// thread1
void f1() {
    std::cout << "Creating new shared_ptr from global atomic...\n";
    auto new_sp = std::make_shared<int>(std::rand());
    
    std::cout << "Storing this new shared_ptr to our global variable...\n";
    asp.store(new_sp);
}

// thread2
void f2() {
    std::cout << "Loading current state of gloval shared_ptr...\n";
    auto sp = asp.load();
}

int main()
{
    // 關鍵技術：執行緒生命週期管理。
    std::thread t1(f1), t2(f2);
    
    t1.join(), t2.join();
    
    return 0;
}
