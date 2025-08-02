#include <mutex>
#include <thread>
#include <iostream>
#include <chrono>
#include <condition_variable>

std::mutex mtx;
std::condition_variable cv;
bool ready = false;

void use_lock_guard() {
    std::cout << "=== lock_guard Example ===" << std::endl;
    
    {
        std::lock_guard<std::mutex> lock(mtx);
        std::cout << "lock_guard: 自動在建構時鎖定" << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
        std::cout << "lock_guard: 工作完成，即將在作用域結束時自動解鎖" << std::endl;
        // 自動在作用域結束時解鎖，無法手動控制
    }
    
    std::cout << "lock_guard: 已離開作用域，鎖已自動釋放" << std::endl;
}

void use_unique_lock() {
    std::cout << "\n=== unique_lock Example ===" << std::endl;
    
    std::unique_lock<std::mutex> lock(mtx);
    std::cout << "unique_lock: 建構時自動鎖定" << std::endl;
    
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    std::cout << "unique_lock: 手動解鎖，進行不需要鎖的工作" << std::endl;
    lock.unlock();
    
    // 進行不需要鎖保護的工作
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "unique_lock: 完成無鎖工作，重新獲得鎖" << std::endl;
    
    lock.lock();
    std::cout << "unique_lock: 重新鎖定成功，繼續受保護的工作" << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // 可以手動解鎖或讓析構函數自動解鎖
}

void use_unique_lock_with_condition_variable() {
    std::cout << "\n=== unique_lock with condition_variable ===" << std::endl;
    
    std::unique_lock<std::mutex> lock(mtx);
    std::cout << "Waiter: 等待條件..." << std::endl;
    
    // condition_variable 只能與 unique_lock 一起使用
    cv.wait(lock, []{ return ready; });
    
    std::cout << "Waiter: 條件滿足，繼續執行" << std::endl;
}

void signal_condition() {
    std::this_thread::sleep_for(std::chrono::milliseconds(500));
    
    {
        std::lock_guard<std::mutex> lock(mtx);
        ready = true;
        std::cout << "Signaler: 設置條件並發送信號" << std::endl;
    }
    cv.notify_one();
}

void deferred_lock_example() {
    std::cout << "\n=== Deferred Lock Example ===" << std::endl;
    
    // 延遲鎖定：建構時不自動鎖定
    std::unique_lock<std::mutex> lock(mtx, std::defer_lock);
    std::cout << "unique_lock: 建構完成但未鎖定" << std::endl;
    
    // 手動決定何時鎖定
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    std::cout << "unique_lock: 現在手動鎖定" << std::endl;
    lock.lock();
    
    std::cout << "unique_lock: 執行需要保護的工作" << std::endl;
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    // 析構時自動解鎖
}

void try_lock_example() {
    std::cout << "\n=== Try Lock Example ===" << std::endl;
    
    std::unique_lock<std::mutex> lock(mtx, std::try_to_lock);
    
    if (lock.owns_lock()) {
        std::cout << "unique_lock: 成功獲得鎖" << std::endl;
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    } else {
        std::cout << "unique_lock: 無法獲得鎖，立即返回" << std::endl;
    }
}

int main() {
    std::cout << "Starting lock_guard vs unique_lock comparison..." << std::endl;
    
    // 1. 基本使用比較
    std::thread t1(use_lock_guard);
    t1.join();
    
    std::thread t2(use_unique_lock);
    t2.join();
    
    // 2. condition_variable 使用 (只能用 unique_lock)
    std::thread waiter(use_unique_lock_with_condition_variable);
    std::thread signaler(signal_condition);
    
    waiter.join();
    signaler.join();
    
    // 3. 延遲鎖定
    std::thread t3(deferred_lock_example);
    t3.join();
    
    // 4. 嘗試鎖定
    std::thread t4(try_lock_example);
    t4.join();
    
    std::cout << "\n=== Summary ===" << std::endl;
    std::cout << "lock_guard: 簡單、自動、適合基本保護" << std::endl;
    std::cout << "unique_lock: 靈活、可控、適合複雜場景" << std::endl;
    
    return 0;
}