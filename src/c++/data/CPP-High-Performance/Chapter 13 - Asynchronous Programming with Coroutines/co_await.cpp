// 高效能關鍵技術示例
// 關鍵技術：協程延遲計算/非同步。
// 章節：Asynchronous Programming with Coroutines - 檔案：co_await.cpp

#include <chrono>
#include <coroutine>

template <class Rep, class Period>
auto operator co_await(std::chrono::duration<Rep, Period> d) {
    // 關鍵技術：協程非同步 I/O。
    
    struct Awaitable {
        std::chrono::system_clock::duration d_;
        Awaitable(std::chrono::system_clock::duration d) : d_(d) { }
        
        bool await_ready() const { return d_.count() <= 0; }
        void await_suspend(std::coroutine_handle<>) { }
        void await_resume() { }
    };
    
    return Awaitable(d);
}

// great and all, but requires a lot of boilerplate to get it to actually do something meaningful like in the author's example

// can't stick this directly into main()
// std::cout << "just about to go to sleep...\n";
// co_await 10ms;       // Calls operator co_await()
// std::cout << "resumed\n";
