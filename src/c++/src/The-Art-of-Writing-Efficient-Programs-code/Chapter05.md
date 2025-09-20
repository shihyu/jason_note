# Chapter 05: 執行緒和並發基礎

## 本章重點

介紹多執行緒程式設計的基礎概念，包括執行緒建立、同步機制、競爭條件和死鎖等問題。

## 核心概念

### 1. 執行緒建立與管理
- **std::thread**: C++11 標準執行緒
- **執行緒生命週期**: 建立、執行、結合(join)或分離(detach)
- **執行緒池**: 避免頻繁建立/銷毀執行緒的開銷

### 2. 同步原語
- **std::mutex**: 互斥鎖
- **std::lock_guard**: RAII 風格鎖管理
- **std::unique_lock**: 更靈活的鎖管理
- **std::condition_variable**: 條件變數

## 關鍵技術要點

### 基本執行緒使用
```cpp
#include <thread>
#include <vector>

void worker(int id) {
    // 執行緒工作函數
    process_data(id);
}

// 建立多個執行緒
std::vector<std::thread> threads;
for (int i = 0; i < num_threads; ++i) {
    threads.emplace_back(worker, i);
}

// 等待所有執行緒完成
for (auto& t : threads) {
    t.join();
}
```

### 互斥鎖使用
```cpp
std::mutex mtx;
int shared_counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);
    ++shared_counter;  // 受保護的臨界區
}
```

### 避免死鎖
```cpp
// 使用 std::lock 同時鎖定多個互斥鎖
std::mutex mtx1, mtx2;

void safe_transfer() {
    std::unique_lock<std::mutex> lock1(mtx1, std::defer_lock);
    std::unique_lock<std::mutex> lock2(mtx2, std::defer_lock);
    std::lock(lock1, lock2);  // 原子地鎖定兩個
    // 執行操作
}
```

## 並發性能考慮

### 1. 偽共享 (False Sharing)
```cpp
// 問題：不同執行緒的資料在同一快取行
struct BadCounters {
    int counter1;  // 執行緒1使用
    int counter2;  // 執行緒2使用
};

// 解決：快取行對齊
struct GoodCounters {
    alignas(64) int counter1;
    alignas(64) int counter2;
};
```

### 2. 鎖粒度
- **粗粒度鎖**: 簡單但併發性低
- **細粒度鎖**: 複雜但併發性高
- **無鎖資料結構**: 最高併發性但實作困難

### 3. 工作分配策略
```cpp
// 靜態分配
int chunk_size = N / num_threads;
for (int i = 0; i < num_threads; ++i) {
    int start = i * chunk_size;
    int end = (i == num_threads - 1) ? N : start + chunk_size;
    threads.emplace_back(process_range, start, end);
}

// 動態分配（工作竊取）
std::atomic<int> next_task{0};
void worker() {
    int task;
    while ((task = next_task.fetch_add(1)) < total_tasks) {
        process_task(task);
    }
}
```

## 常見並發問題

### 1. 競爭條件 (Race Condition)
- 多個執行緒同時存取共享資料
- 結果依賴執行順序
- 使用同步機制避免

### 2. 死鎖 (Deadlock)
- 執行緒相互等待對方釋放資源
- 避免策略：
  - 固定鎖定順序
  - 使用 std::lock
  - 超時機制

### 3. 活鎖 (Livelock)
- 執行緒不斷重試但無法進展
- 加入隨機延遲或優先級

### 4. 飢餓 (Starvation)
- 某些執行緒長期無法取得資源
- 使用公平鎖或優先級調度

## 性能優化建議

1. **減少同步開銷**
   - 最小化臨界區
   - 使用讀寫鎖
   - 考慮無鎖演算法

2. **負載平衡**
   - 動態工作分配
   - 工作竊取佇列
   - 適應性分區

3. **快取優化**
   - 避免偽共享
   - 資料局部性
   - NUMA 感知

## 測量工具
```bash
# 檢測資料競爭
g++ -fsanitize=thread -g program.cpp
./a.out

# 性能分析
perf record -g ./program
perf report
```

## 最佳實踐

1. 優先使用高階並發工具（std::async, std::future）
2. 避免共享可變狀態
3. 使用不可變資料結構
4. 考慮使用訊息傳遞而非共享記憶體
5. 徹底測試並發程式碼