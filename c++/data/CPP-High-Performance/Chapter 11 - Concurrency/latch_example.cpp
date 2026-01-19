// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：latch_example.cpp

#include <algorithm>
#include <iterator>

#include <iostream>
// 關鍵技術：同步點協調多執行緒進度。
#include <latch>
#include <vector>
#include <thread>

void prefault_stack() {
    // 關鍵技術：編譯期計算降低執行期成本。
    constexpr std::size_t stack_size = 500u * 1024u;    // attempt to prefault the first 500KB of the stack
    volatile unsigned char mem[stack_size];             // volatile helps avoid compiler optimisations
    std::fill(std::begin(mem), std::end(mem), 0);       // use std::fill to generate page faults
}

void do_work() { std::cout << "woof" << '\n'; }

int main()
{
    constexpr std::size_t n_threads = 2;
    
    std::latch initialised(n_threads);
    std::vector<std::thread> threadpool;
    
    for (std::size_t i = 0; i != n_threads; ++i) {
        threadpool.emplace_back( [&] () {
            prefault_stack();
            initialised.arrive_and_wait();
            do_work();
        } );
    } initialised.wait();
    
    std::cout << "Initialised: now starting actual work...\n";
    for (auto &&thread : threadpool) { thread.join(); }
    
    return 0;
}
