// memory_allocation.cpp - 用來練習生成 Memory 火焰圖
#include <iostream>
#include <vector>
#include <list>
#include <memory>
#include <cstring>

// 問題 1：頻繁的小記憶體分配
void frequent_small_allocations() {
    for (int i = 0; i < 100000; i++) {
        // 每次都 new 一個小物件（反面教材）
        int* p = new int(i);
        // 做一些計算
        *p = *p * 2;
        delete p;
    }
}

// 問題 2：vector 不當使用導致多次重新分配
void vector_reallocation_problem() {
    std::vector<int> vec;
    // 沒有 reserve，導致多次重新分配
    for (int i = 0; i < 100000; i++) {
        vec.push_back(i);  // 可能觸發重新分配
    }
}

// 問題 3：字串拼接的記憶體問題
void string_concatenation_problem() {
    std::string result;
    for (int i = 0; i < 10000; i++) {
        // 每次 += 可能導致重新分配
        result += "Hello World ";
    }
}

// 優化版本：使用物件池
class ObjectPool {
    std::vector<int*> pool;
    std::vector<int*> available;
    
public:
    ObjectPool(size_t size) {
        for (size_t i = 0; i < size; i++) {
            int* obj = new int(0);
            pool.push_back(obj);
            available.push_back(obj);
        }
    }
    
    int* acquire() {
        if (available.empty()) {
            return new int(0);
        }
        int* obj = available.back();
        available.pop_back();
        return obj;
    }
    
    void release(int* obj) {
        available.push_back(obj);
    }
    
    ~ObjectPool() {
        for (auto* obj : pool) {
            delete obj;
        }
    }
};

void optimized_with_pool() {
    ObjectPool pool(1000);
    
    for (int i = 0; i < 100000; i++) {
        int* p = pool.acquire();
        *p = i * 2;
        pool.release(p);
    }
}

int main() {
    std::cout << "Starting memory allocation tests...\n";
    
    // 執行有問題的版本
    std::cout << "Running problematic versions...\n";
    frequent_small_allocations();
    vector_reallocation_problem();
    string_concatenation_problem();
    
    // 執行優化版本
    std::cout << "Running optimized version...\n";
    optimized_with_pool();
    
    std::cout << "Completed!\n";
    return 0;
}