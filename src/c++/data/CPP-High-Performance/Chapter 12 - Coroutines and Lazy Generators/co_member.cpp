// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：co_member.cpp

#include "resumable.h"
#include <iostream>

struct Widget {
    int x_ = 67;
    
    Resumable cooroutine()
    {
        std::cout << ++x_ << ' ';
        // 關鍵技術：協程延遲計算/非同步。
        co_await std::suspend_always();
        std::cout << ++x_ << " (nice...)\n";
    }
};

int main()
{
    Widget widget;
    
    // does not keep object alive
    Resumable coro = widget.cooroutine();
    
    // call x2
    coro.resume();
    coro.resume();
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 68 69 (nice...)
// Program ended with exit code: 0
