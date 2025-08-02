# Linux 系統鎖與 C++ 鎖機制範例程式 🔒

本目錄包含 `locks_guide.md` 中所有鎖機制的完整可編譯範例程式。

## 📁 檔案結構

```
locks_examples/
├── README.md                    # 本說明檔
├── Makefile                     # 編譯腳本
├── 01_pthread_mutex.c           # pthread mutex 範例
├── 02_semaphore.c               # 信號量範例
├── 03_spinlock.c                # 自旋鎖範例
├── 04_rwlock.c                  # 讀寫鎖範例
├── 05_condition_variable.c      # 條件變數範例
├── 06_std_mutex.cpp             # C++ std::mutex 範例
├── 07_recursive_mutex.cpp       # C++ 遞迴鎖範例
├── 08_shared_mutex.cpp          # C++ 共享鎖範例 (C++17)
├── 09_condition_variable.cpp    # C++ 條件變數範例
├── 10_atomic_basic.cpp          # C++ 原子操作基礎範例
├── 11_lockfree_queue.cpp        # 無鎖佇列範例
└── 12_lock_comparison.cpp       # lock_guard vs unique_lock 比較
```

## 🚀 快速開始

### 編譯所有範例
```bash
make
```

### 編譯並測試所有範例
```bash
make test
```

### 只編譯 Linux C 範例
```bash
make linux
```

### 只編譯 C++ 範例
```bash
make cpp
```

### 清理編譯檔案
```bash
make clean
```

## 🛠️ 手動編譯

### Linux C 範例 (需要 pthread)
```bash
gcc -pthread -o 01_pthread_mutex 01_pthread_mutex.c
gcc -pthread -o 02_semaphore 02_semaphore.c
gcc -pthread -o 03_spinlock 03_spinlock.c
gcc -pthread -o 04_rwlock 04_rwlock.c
gcc -pthread -o 05_condition_variable 05_condition_variable.c
```

### C++ 範例 (需要 C++17 支援)
```bash
g++ -std=c++17 -pthread -o 06_std_mutex 06_std_mutex.cpp
g++ -std=c++17 -pthread -o 07_recursive_mutex 07_recursive_mutex.cpp
g++ -std=c++17 -pthread -o 08_shared_mutex 08_shared_mutex.cpp
g++ -std=c++17 -pthread -o 09_condition_variable 09_condition_variable.cpp
g++ -std=c++17 -pthread -o 10_atomic_basic 10_atomic_basic.cpp
g++ -std=c++17 -pthread -o 11_lockfree_queue 11_lockfree_queue.cpp
g++ -std=c++17 -pthread -o 12_lock_comparison 12_lock_comparison.cpp
```

## 🎯 範例說明

### Linux 系統鎖 (C)

1. **01_pthread_mutex.c** - pthread 互斥鎖
   - 展示基本的互斥鎖使用
   - 多執行緒安全的計數器範例

2. **02_semaphore.c** - 信號量
   - 控制同時存取資源的執行緒數量
   - 模擬資源池管理

3. **03_spinlock.c** - 自旋鎖
   - 適合短時間鎖定的場景
   - 高頻率操作的同步

4. **04_rwlock.c** - 讀寫鎖
   - 允許多讀者或單寫者
   - 多讀少寫場景最佳化

5. **05_condition_variable.c** - 條件變數
   - 執行緒間條件等待與通知
   - 生產者-消費者模式

### C++ 標準庫鎖 (C++)

6. **06_std_mutex.cpp** - C++ 標準互斥鎖
   - RAII 自動鎖管理
   - lock_guard 使用範例

7. **07_recursive_mutex.cpp** - 遞迴鎖
   - 允許同一執行緒多次獲得鎖
   - 遞迴函數鎖定場景

8. **08_shared_mutex.cpp** - 共享鎖 (C++17)
   - C++ 版本的讀寫鎖
   - shared_lock 與 unique_lock

9. **09_condition_variable.cpp** - C++ 條件變數
   - 完整的生產者-消費者實現
   - 緩衝區管理範例

10. **10_atomic_basic.cpp** - 原子操作基礎
    - 原子計數器、CAS 操作
    - 記憶體順序範例

11. **11_lockfree_queue.cpp** - 無鎖佇列
    - 高性能無鎖資料結構
    - 原子指標操作

12. **12_lock_comparison.cpp** - 鎖類型比較
    - lock_guard vs unique_lock
    - 不同使用場景對比

## 🔧 系統需求

- **Linux/Unix 系統**
- **GCC 7.0+** (支援 C++17)
- **pthread 函式庫**

## 📋 執行範例

```bash
# 編譯所有範例
make

# 執行特定範例
./01_pthread_mutex
./10_atomic_basic

# 快速測試所有範例
make quick-test
```

## ⚠️ 注意事項

1. **C++17 需求**: shared_mutex 需要 C++17 編譯器支援
2. **執行時間**: 某些範例可能需要幾秒鐘執行時間
3. **輸出差異**: 多執行緒程式輸出順序可能不同
4. **記憶體檢查**: 可用 valgrind 檢查記憶體洩漏

## 🐛 故障排除

### 編譯錯誤
```bash
# 檢查編譯器版本
gcc --version
g++ --version

# 確保支援 C++17
g++ -std=c++17 --version
```

### 執行時錯誤
```bash
# 檢查是否有 pthread 支援
ldd ./01_pthread_mutex

# 檢查權限
chmod +x ./01_pthread_mutex
```

## 📚 相關文件

- 主要指南: `../locks_guide.md`
- Linux pthread 手冊: `man pthread_mutex_init`
- C++ 並發參考: https://en.cppreference.com/w/cpp/thread

## 🤝 貢獻

如果發現任何問題或改進建議，歡迎提交 issue 或 pull request。