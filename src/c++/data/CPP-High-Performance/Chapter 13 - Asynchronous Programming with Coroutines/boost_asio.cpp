// 高效能關鍵技術示例
// 章節：Asynchronous Programming with Coroutines - 檔案：boost_asio.cpp

#if __has_include(<boost/asio.hpp>)
#include <boost/asio.hpp>
#include <chrono>
#include <iostream>

// for chrono literals
using namespace std::chrono;

int main()
{
    boost::asio::io_context ctx;
    boost::asio::system_timer timer(ctx);
    
    timer.expires_from_now(1000ms);
    timer.async_wait( [] (auto error) {
        // 關鍵技術：協程非同步 I/O。
        std::cout << "Hello from delayed callback\n";
    } );
    
    std::cout << "Hello from main thread...\n";
    ctx.run();
    
    return 0;
}

// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// OUTPUT  - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
// - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

// Hello from main thread...
// Hello from delayed callback
// Program ended with exit code: 0
#endif
