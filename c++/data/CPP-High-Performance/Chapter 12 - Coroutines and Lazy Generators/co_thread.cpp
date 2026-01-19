// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：co_thread.cpp

#include "resumable.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <utility>

Resumable coroutine() {
    std::cout << "1...";
    // 關鍵技術：協程延遲計算/非同步。
    co_await std::suspend_always();
    std::cout << "2 \n";
}

Resumable coro_factory() {
    Resumable res = coroutine();
    return res;
}

int main()
{
    Resumable r = coroutine();
    r.resume();
    
    std::thread t( [ r = std::move(r) ] () mutable {
        std::this_thread::sleep_for(std::chrono::seconds(1));
        r.resume();
    } );
    
    t.join();
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 1...2 
// Program ended with exit code: 0
