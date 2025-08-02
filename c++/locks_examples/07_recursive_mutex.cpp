#include <mutex>
#include <thread>
#include <iostream>

std::recursive_mutex rmtx;
int call_count = 0;

void recursive_function(int n) {
    std::lock_guard<std::recursive_mutex> lock(rmtx);
    call_count++;
    std::cout << "Level: " << n << ", Call count: " << call_count << std::endl;
    
    if (n > 0) {
        recursive_function(n - 1);  // 同一執行緒再次獲得鎖
    }
}

void normal_function() {
    std::lock_guard<std::recursive_mutex> lock(rmtx);
    call_count++;
    std::cout << "Normal function called, Call count: " << call_count << std::endl;
    
    // 呼叫其他需要相同鎖的函數
    recursive_function(2);
}

void thread_worker(int thread_id) {
    std::cout << "Thread " << thread_id << " starting..." << std::endl;
    
    if (thread_id == 1) {
        recursive_function(3);
    } else {
        normal_function();
    }
    
    std::cout << "Thread " << thread_id << " finished" << std::endl;
}

int main() {
    std::cout << "Starting recursive_mutex example..." << std::endl;
    
    std::thread t1(thread_worker, 1);
    std::thread t2(thread_worker, 2);
    
    t1.join();
    t2.join();
    
    std::cout << "Total function calls: " << call_count << std::endl;
    
    return 0;
}