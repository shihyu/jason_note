// 高效能關鍵技術示例
// 章節：Concurrency - 檔案：jthread.cpp

#include <chrono>
#include <thread>
#include <iostream>

void print(std::stop_token stoken) {
    while (!stoken.stop_requested()) {
        std::cout << std::this_thread::get_id() << '\n';
        std::this_thread::sleep_for(std::chrono::seconds{1});
    } std::cout << "Stop requested\n";
}

int main() {
    // 關鍵技術：執行緒生命週期管理。
    std::jthread joinable_thread(print);
    
    std::cout << "main: goes to sleep\n";
    std::this_thread::sleep_for(std::chrono::seconds{3});
    
    std::cout << "main: request jthread to stop\n";
    joinable_thread.request_stop();
    
    return 0;
}
