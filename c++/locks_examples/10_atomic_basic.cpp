#include <atomic>
#include <thread>
#include <iostream>
#include <vector>

// 1. 基本計數器 - 最常用
std::atomic<int> counter(0);

void basic_increment() {
    for (int i = 0; i < 1000; ++i) {
        counter++;        // 原子遞增
        // counter.fetch_add(1);  // 等同於上面
    }
}

// 2. 比較並交換 (CAS) - 高級操作
std::atomic<int> value(10);

bool try_update(int expected, int new_val) {
    // 如果 value == expected，則設為 new_val，返回 true
    // 否則 expected 被更新為實際值，返回 false
    return value.compare_exchange_weak(expected, new_val);
}

// 3. 原子交換
std::atomic<int> shared_data(100);

int atomic_swap_example() {
    int old_value = shared_data.exchange(200);  // 設為200，返回舊值100
    return old_value;
}

// 4. 記憶體順序示例
std::atomic<bool> ready{false};
std::atomic<int> data{0};

void producer() {
    data.store(42, std::memory_order_relaxed);    // 資料寫入
    ready.store(true, std::memory_order_release); // 發布信號
}

void consumer() {
    if (ready.load(std::memory_order_acquire)) {  // 獲取信號
        int value = data.load(std::memory_order_relaxed); // 讀取資料
        std::cout << "Consumer read: " << value << std::endl;
    }
}

int main() {
    std::cout << "Starting atomic operations example..." << std::endl;
    
    // 基本測試
    std::vector<std::thread> threads;
    
    // 啟動10個執行緒同時遞增
    for (int i = 0; i < 10; ++i) {
        threads.emplace_back(basic_increment);
    }
    
    for (auto& t : threads) {
        t.join();
    }
    
    std::cout << "最終計數: " << counter << std::endl;  // 應該是10000
    
    // CAS 範例
    int expected = 10;
    if (try_update(expected, 42)) {
        std::cout << "成功更新為 42" << std::endl;
    } else {
        std::cout << "更新失敗，當前值: " << expected << std::endl;
    }
    
    // 原子交換範例
    int old_val = atomic_swap_example();
    std::cout << "交換前的值: " << old_val << ", 交換後的值: " << shared_data << std::endl;
    
    // 記憶體順序範例
    std::thread t1(producer);
    std::thread t2(consumer);
    
    t1.join();
    t2.join();
    
    return 0;
}