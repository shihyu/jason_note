#include <condition_variable>
#include <mutex>
#include <queue>
#include <thread>
#include <iostream>
#include <chrono>

std::mutex mtx;
std::condition_variable cv;
std::queue<int> buffer;
const int MAX_BUFFER_SIZE = 5;
bool finished = false;

void producer(int producer_id) {
    for (int i = 0; i < 10; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        
        // 等待緩衝區有空間
        cv.wait(lock, []{ return buffer.size() < MAX_BUFFER_SIZE; });
        
        int item = producer_id * 100 + i;
        buffer.push(item);
        std::cout << "Producer " << producer_id << " produced: " << item 
                  << " (buffer size: " << buffer.size() << ")" << std::endl;
        
        cv.notify_all();  // 通知消費者
        
        // 模擬生產時間
        lock.unlock();
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
}

void consumer(int consumer_id) {
    while (true) {
        std::unique_lock<std::mutex> lock(mtx);
        
        // 等待緩衝區有資料或生產完成
        cv.wait(lock, []{ return !buffer.empty() || finished; });
        
        if (buffer.empty() && finished) {
            break;
        }
        
        if (!buffer.empty()) {
            int item = buffer.front();
            buffer.pop();
            std::cout << "Consumer " << consumer_id << " consumed: " << item 
                      << " (buffer size: " << buffer.size() << ")" << std::endl;
            
            cv.notify_all();  // 通知生產者
            
            // 模擬消費時間
            lock.unlock();
            std::this_thread::sleep_for(std::chrono::milliseconds(150));
        }
    }
}

int main() {
    std::cout << "Starting condition_variable producer-consumer example..." << std::endl;
    
    std::vector<std::thread> threads;
    
    // 創建2個生產者
    for (int i = 1; i <= 2; ++i) {
        threads.emplace_back(producer, i);
    }
    
    // 創建3個消費者
    for (int i = 1; i <= 3; ++i) {
        threads.emplace_back(consumer, i);
    }
    
    // 等待生產者完成
    for (int i = 0; i < 2; ++i) {
        threads[i].join();
    }
    
    // 設置完成標誌
    {
        std::lock_guard<std::mutex> lock(mtx);
        finished = true;
    }
    cv.notify_all();
    
    // 等待消費者完成
    for (int i = 2; i < 5; ++i) {
        threads[i].join();
    }
    
    std::cout << "All producers and consumers finished. Final buffer size: " 
              << buffer.size() << std::endl;
    
    return 0;
}