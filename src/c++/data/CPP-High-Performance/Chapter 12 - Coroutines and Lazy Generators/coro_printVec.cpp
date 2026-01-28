// 高效能關鍵技術示例
// 章節：Coroutines and Lazy Generators - 檔案：coro_printVec.cpp

#include "chapter_12.h"
#include <iostream>
#include <utility>

class Resumable {
    struct Promise;
public:
    using promise_type = Promise;
    
    Resumable(Resumable &&rhs) : h_(std::exchange(rhs.h_, h_)) { }
    
    ~Resumable()
    {
        if (h_) { h_.destroy(); }
    }
    
    bool resume()
    {
        if (!h_.done()) { h_.resume(); }
        return !h_.done();
    }
    
private:
    std::coroutine_handle<Promise> h_;
    
    explicit Resumable(std::coroutine_handle<Promise> h) : h_(h) { }
    
    struct Promise {
        Resumable get_return_object()
        {
            using Handle = std::coroutine_handle<Promise>;
            return Resumable(Handle::from_promise(*this));
        }
        
        // using auto to tidy up experimental namespace
        auto initial_suspend() { return std::suspend_always(); }
        auto final_suspend() noexcept { return std::suspend_always(); }
        
        void return_void() { }
        void unhandled_exception() { std::terminate(); }
    };
};

Resumable coroutine() {
    std::cout << "3 ";
    // 關鍵技術：協程延遲計算/非同步。
    co_await std::suspend_always();
    std::cout << "5 ";
}

int main()
{
    std::cout << "1 ";
    std::cout << "2 ";
    
    Resumable resumble = coroutine();
    
    resumble.resume();
    std::cout << "4 ";
    resumble.resume();
    std::cout << "6\n";
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// 1 2 3 4 5 6
// Program ended with exit code: 0
