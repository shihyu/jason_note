#include <shared_mutex>
#include <mutex>
#include <thread>
#include <vector>
#include <iostream>
#include <chrono>

std::shared_mutex sh_mtx;
std::vector<int> data = {1, 2, 3, 4, 5};

void reader(int reader_id) {
    for (int i = 0; i < 3; ++i) {
        std::shared_lock<std::shared_mutex> lock(sh_mtx);
        std::cout << "Reader " << reader_id << ": ";
        for (int val : data) {
            std::cout << val << " ";
        }
        std::cout << std::endl;
        
        // 模擬讀取工作
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void writer(int writer_id) {
    for (int i = 0; i < 2; ++i) {
        std::unique_lock<std::shared_mutex> lock(sh_mtx);
        data.push_back(data.size() + 1);
        std::cout << "Writer " << writer_id << ": Added element, size now = " 
                  << data.size() << std::endl;
        
        // 模擬寫入工作
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

int main() {
    std::cout << "Starting shared_mutex example (C++17)..." << std::endl;
    
    std::vector<std::thread> threads;
    
    // 創建多個讀者
    for (int i = 1; i <= 4; ++i) {
        threads.emplace_back(reader, i);
    }
    
    // 創建少數寫者
    for (int i = 1; i <= 2; ++i) {
        threads.emplace_back(writer, i);
    }
    
    // 等待所有執行緒完成
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "Final data: ";
    for (int val : data) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
    
    return 0;
}