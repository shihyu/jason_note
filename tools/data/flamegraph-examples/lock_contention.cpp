// lock_contention.cpp - 用來練習生成 Off-CPU 火焰圖
#include <iostream>
#include <thread>
#include <mutex>
#include <vector>
#include <atomic>
#include <chrono>

std::mutex global_mutex;
std::atomic<long> shared_counter(0);

// 問題：過度使用全域鎖
void bad_locking_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        // 鎖的粒度太大
        std::lock_guard<std::mutex> lock(global_mutex);
        
        // 在鎖裡面做太多事情
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        shared_counter += local_computation;
    }
}

// 優化：減少鎖的粒度
void better_locking_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        // 先在鎖外面計算
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        
        // 只在必要時加鎖
        std::lock_guard<std::mutex> lock(global_mutex);
        shared_counter += local_computation;
    }
}

// 最優：使用原子操作
void atomic_thread(int thread_id) {
    for (int i = 0; i < 100000; i++) {
        int local_computation = 0;
        for (int j = 0; j < 100; j++) {
            local_computation += j * thread_id;
        }
        
        // 使用原子操作代替鎖
        shared_counter.fetch_add(local_computation, std::memory_order_relaxed);
    }
}

int main(int argc, char* argv[]) {
    const int num_threads = 8;
    std::vector<std::thread> threads;
    
    std::string mode = (argc > 1) ? argv[1] : "bad";
    
    auto start = std::chrono::high_resolution_clock::now();
    
    if (mode == "bad") {
        std::cout << "Running with bad locking...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(bad_locking_thread, i);
        }
    } else if (mode == "better") {
        std::cout << "Running with better locking...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(better_locking_thread, i);
        }
    } else {
        std::cout << "Running with atomic operations...\n";
        for (int i = 0; i < num_threads; i++) {
            threads.emplace_back(atomic_thread, i);
        }
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    
    std::cout << "Result: " << shared_counter << std::endl;
    std::cout << "Time: " << duration.count() << " ms" << std::endl;
    
    return 0;
}