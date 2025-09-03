#include <mutex>
#include <thread>
#include <iostream>
#include <vector>

std::mutex mtx;
int counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);  // RAII 自動解鎖
    counter++;
    std::cout << "Counter: " << counter << std::endl;
}

void increment_manual() {
    mtx.lock();
    counter++;
    std::cout << "Manual Counter: " << counter << std::endl;
    mtx.unlock();
}

int main() {
    std::cout << "Starting std::mutex example..." << std::endl;
    
    std::vector<std::thread> threads;
    
    // 使用 RAII lock_guard
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back(increment);
    }
    
    // 使用手動鎖定 (不推薦)
    for (int i = 0; i < 5; ++i) {
        threads.emplace_back(increment_manual);
    }
    
    // 等待所有執行緒完成
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "Final counter value: " << counter << std::endl;
    
    return 0;
}