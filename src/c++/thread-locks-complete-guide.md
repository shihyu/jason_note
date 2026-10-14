# 🔐 多執行緒鎖機制完全指南

> 用白話和示意圖理解所有常見的鎖機制

---

## 📚 目錄

1. [無鎖機制 (Lock-Free)](#1-無鎖機制-lock-free)
2. [互斥鎖 (Mutex)](#2-互斥鎖-mutex)
3. [自旋鎖 (Spinlock)](#3-自旋鎖-spinlock)
4. [讀寫鎖 (Read-Write Lock)](#4-讀寫鎖-read-write-lock)
5. [遞迴鎖 (Recursive Lock)](#5-遞迴鎖-recursive-lock)
6. [條件變數 (Condition Variable)](#6-條件變數-condition-variable)
7. [信號量 (Semaphore)](#7-信號量-semaphore)
8. [柵欄 (Barrier)](#8-柵欄-barrier)
9. [順序鎖 (Seqlock)](#9-順序鎖-seqlock)
10. [效能比較總表](#10-效能比較總表)

---

## 1. 無鎖機制 (Lock-Free)

### 🎯 核心概念
想像一個「旋轉壽司台」：
- **生產者** = 廚師放壽司
- **消費者** = 客人拿壽司
- **不需要服務生協調**（不需要鎖）

### 📊 示意圖

```
環狀緩衝區（SPSC Queue）
┌───┬───┬───┬───┬───┬───┬───┬───┐
│ A │ B │ C │   │   │   │   │   │
└───┴───┴───┴───┴───┴───┴───┴───┘
  ↑       ↑
  讀      寫

生產者（廚師）         消費者（客人）
只改寫入位置   ←→     只改讀取位置
互不干擾！
```

### 💻 程式碼範例

```cpp
template<typename T>
class LockFreeQueue {
    std::vector<T> buffer_;
    std::atomic<size_t> next_write_index_{0};  // 原子變數
    std::atomic<size_t> next_read_index_{0};
    
public:
    void push(T data) {
        size_t write_pos = next_write_index_.load(std::memory_order_relaxed);
        buffer_[write_pos] = data;
        next_write_index_.store(write_pos + 1, std::memory_order_release);
    }
    
    bool pop(T& data) {
        size_t read_pos = next_read_index_.load(std::memory_order_relaxed);
        size_t write_pos = next_write_index_.load(std::memory_order_acquire);
        
        if (read_pos == write_pos) return false;  // 佇列空
        
        data = buffer_[read_pos];
        next_read_index_.store(read_pos + 1, std::memory_order_release);
        return true;
    }
};
```

### ✅ 優點
- **超快速**：沒有 Context Switch
- **無死鎖**：沒有鎖就不會卡住
- **低延遲**：適合即時系統

### ❌ 缺點
- **限制多**：通常只支援 SPSC（單生產者單消費者）
- **複雜度高**：需要理解記憶體順序（Memory Order）
- **除錯困難**：錯誤不易重現

### 🎯 使用場景
- 音訊處理管線
- 高頻交易系統
- 網路封包處理

---

## 2. 互斥鎖 (Mutex)

### 🎯 核心概念
想像一個「公共廁所」：
- **只有一把鑰匙**（鎖）
- **誰拿到鑰匙誰進去**
- **其他人在外面排隊等**

### 📊 示意圖

```
時間軸：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→

執行緒 A:  [取得鎖]───執行中───[釋放鎖]
執行緒 B:            [等待......]  [取得鎖]───執行中───
執行緒 C:                          [等待..................]

狀態：
┌─────────────┐
│ 共享資源    │
│ (counter)   │  ← 只有拿到鎖的執行緒能存取
└─────────────┘
      ↑
      🔒 Mutex
```

### 💻 程式碼範例

```cpp
#include <mutex>

class BankAccount {
    int balance_ = 0;
    std::mutex mutex_;  // 保護 balance_
    
public:
    void deposit(int amount) {
        std::lock_guard<std::mutex> lock(mutex_);  // 自動加鎖
        balance_ += amount;
        // 離開作用域自動解鎖
    }
    
    void withdraw(int amount) {
        std::lock_guard<std::mutex> lock(mutex_);
        if (balance_ >= amount) {
            balance_ -= amount;
        }
    }
    
    int get_balance() {
        std::lock_guard<std::mutex> lock(mutex_);
        return balance_;
    }
};
```

### 🔄 運作流程

```
執行緒 A 想要修改 balance_：

1. 執行到 lock_guard
   ↓
2. 嘗試取得 mutex_
   ├─ 成功 → 繼續執行
   └─ 失敗 → 進入睡眠，等作業系統喚醒
   
3. 執行 balance_ += amount
   
4. 離開 {} 作用域
   ↓
5. 自動釋放 mutex_
   ↓
6. 作業系統喚醒等待中的執行緒
```

### ✅ 優點
- **簡單易用**：最基本的同步機制
- **保證互斥**：絕對不會有兩個執行緒同時執行
- **自動管理**：搭配 RAII（lock_guard）不會忘記解鎖

### ❌ 缺點
- **Context Switch 開銷**：等待時會睡眠
- **可能死鎖**：互相等待對方的鎖
- **不公平**：無法保證先等待的先取得

### 🎯 使用場景
- 銀行轉帳系統
- 資料庫連線池
- 任何需要保護共享資源的情境

---

## 3. 自旋鎖 (Spinlock)

### 🎯 核心概念
想像「排隊買演唱會票」：
- **不離開隊伍**（不睡眠）
- **一直盯著售票口**（一直檢查）
- **票一開賣馬上衝**（立即取得）

### 📊 示意圖

```
Mutex（睡眠等待）：
執行緒 B: [嘗試鎖]→ 😴 睡覺... → 被喚醒 → [取得鎖]
                    （Context Switch）

Spinlock（忙碌等待）：
執行緒 B: [嘗試鎖]→ 🔄🔄🔄 一直檢查... → [取得鎖]
                    （消耗 CPU 但無 Context Switch）

CPU 使用率：
Mutex:     ▓░░░░░░░░░░░▓▓▓▓ (睡眠時不佔用)
Spinlock:  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ (一直佔用 CPU)
```

### 💻 程式碼範例

```cpp
#include <atomic>

class Spinlock {
    std::atomic_flag flag_ = ATOMIC_FLAG_INIT;
    
public:
    void lock() {
        // 一直嘗試直到成功
        while (flag_.test_and_set(std::memory_order_acquire)) {
            // 空轉等待（可加入 CPU pause 指令優化）
            #ifdef __x86_64__
                __builtin_ia32_pause();  // x86 的 PAUSE 指令
            #endif
        }
    }
    
    void unlock() {
        flag_.clear(std::memory_order_release);
    }
};

// 使用範例
class Counter {
    int value_ = 0;
    Spinlock lock_;
    
public:
    void increment() {
        lock_.lock();
        ++value_;
        lock_.unlock();
    }
};
```

### 🔄 運作對比

```
關鍵時刻圖：

Mutex（等待 100 微秒）：
[執行] → [睡眠 100μs] → [喚醒] → [執行]
         ↑              ↑
    Context Switch   Context Switch
    (~1-10 微秒)     (~1-10 微秒)

總成本：100 + 1 + 1 = 102 微秒

Spinlock（等待 5 微秒）：
[執行] → [空轉 5μs] → [執行]
         ↑
    沒有 Context Switch！

總成本：5 微秒（但 CPU 一直忙碌）
```

### ✅ 優點
- **低延遲**：無 Context Switch
- **適合短臨界區**：鎖定時間 < 1 微秒時很快
- **簡單實作**：只需要原子操作

### ❌ 缺點
- **浪費 CPU**：等待時一直消耗 CPU
- **可能活鎖**：優先權反轉問題
- **不適合長時間鎖定**：會讓其他執行緒餓死

### 🎯 使用場景
- 作業系統核心（Kernel）
- 中斷處理程序
- 非常短的臨界區（< 100 奈秒）

---

## 4. 讀寫鎖 (Read-Write Lock)

### 🎯 核心概念
想像一個「圖書館」：
- **讀者**：很多人可以同時看書（共享）
- **作者**：只能一個人寫書，寫的時候不能讀（獨佔）

### 📊 示意圖

```
時間軸：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━→

讀者 A:  [讀取────────]
讀者 B:    [讀取──────]     ← 可以同時讀
讀者 C:      [讀取────]

寫者 X:               [等待] [寫入] ← 等所有讀者結束
讀者 D:                      [等待] [讀取] ← 等寫者結束

狀態表：
┌─────────────┬─────────────┬─────────────┐
│   讀模式    │   讀模式    │   寫模式    │
├─────────────┼─────────────┼─────────────┤
│ 多人可讀    │ ← 切換 →    │ 只有一人    │
│ 無人可寫    │             │ 無人可讀寫  │
└─────────────┴─────────────┴─────────────┘
```

### 💻 程式碼範例

```cpp
#include <shared_mutex>

class ThreadSafeCache {
    std::map<std::string, std::string> cache_;
    mutable std::shared_mutex mutex_;  // C++17
    
public:
    // 讀取（共享鎖）
    std::string get(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);  // 共享鎖
        auto it = cache_.find(key);
        return it != cache_.end() ? it->second : "";
    }
    
    // 寫入（獨佔鎖）
    void set(const std::string& key, const std::string& value) {
        std::unique_lock<std::shared_mutex> lock(mutex_);  // 獨佔鎖
        cache_[key] = value;
    }
    
    // 檢查存在（共享鎖）
    bool contains(const std::string& key) const {
        std::shared_lock<std::shared_mutex> lock(mutex_);
        return cache_.find(key) != cache_.end();
    }
};
```

### 🔄 執行流程

```
場景：5 個讀者，1 個寫者

步驟 1: 讀者 A, B, C 同時讀取
┌─────────────┐
│ 共享資源    │
│ (Data)      │
└─────────────┘
  ↑   ↑   ↑
  A   B   C    ← 共享鎖，可以同時讀

步驟 2: 寫者 X 嘗試寫入
┌─────────────┐
│ 共享資源    │
│ (Data)      │
└─────────────┘
  ↑   ↑   ↑
  A   B   C    ← 還在讀
      ⏰ X     ← 等待中（無法取得獨佔鎖）

步驟 3: 所有讀者結束，寫者開始
┌─────────────┐
│ 共享資源    │
│ (Data)      │
└─────────────┘
      ↑
      X        ← 獨佔鎖，只有它能存取

步驟 4: 寫者結束，新讀者進入
┌─────────────┐
│ 共享資源    │
│ (Data)      │
└─────────────┘
  ↑   ↑
  D   E        ← 新的讀者可以同時讀
```

### ✅ 優點
- **讀取效能高**：多個讀者不互斥
- **適合讀多寫少**：如快取系統
- **公平性可調**：可優先讀者或寫者

### ❌ 缺點
- **寫者可能餓死**：讀者不斷進入
- **實作複雜**：需要兩種鎖狀態
- **額外開銷**：比普通 Mutex 慢

### 🎯 使用場景
- 快取系統（Redis, Memcached）
- 組態檔讀取
- 資料庫索引

---

## 5. 遞迴鎖 (Recursive Lock)

### 🎯 核心概念
想像「俄羅斯娃娃」：
- **同一個人可以多次開門**（同一執行緒可多次加鎖）
- **但要記得開幾次就要關幾次**

### 📊 示意圖

```
普通 Mutex（會死鎖）：
void funcA() {
    mutex.lock();         // ✅ 第一次加鎖成功
    // ...
    funcB();              // 呼叫 funcB
}

void funcB() {
    mutex.lock();         // ❌ 死鎖！同一執行緒嘗試再次加鎖
    // ...
    mutex.unlock();
}

遞迴鎖（可以重入）：
void funcA() {
    recursive_mutex.lock();  // ✅ 計數 = 1
    // ...
    funcB();
}

void funcB() {
    recursive_mutex.lock();  // ✅ 計數 = 2（同一執行緒）
    // ...
    recursive_mutex.unlock(); // 計數 = 1
}
// funcA 結束時 unlock()     // 計數 = 0（真正釋放）

鎖計數器：
執行位置         | lock() 次數 | unlock() 次數 | 計數器
----------------|------------|--------------|-------
進入 funcA       |     1      |      0       |   1
進入 funcB       |     2      |      0       |   2
離開 funcB       |     2      |      1       |   1
離開 funcA       |     2      |      2       |   0  ← 釋放
```

### 💻 程式碼範例

```cpp
#include <mutex>

class FileSystem {
    std::recursive_mutex mutex_;
    std::string root_path_;
    
public:
    void createDirectory(const std::string& path) {
        std::lock_guard<std::recursive_mutex> lock(mutex_);
        
        // 建立父目錄（遞迴呼叫）
        auto parent = getParentPath(path);
        if (!parent.empty()) {
            ensureDirectoryExists(parent);  // 會再次加鎖！
        }
        
        // 建立目錄
        mkdir(path.c_str(), 0755);
    }
    
    void ensureDirectoryExists(const std::string& path) {
        std::lock_guard<std::recursive_mutex> lock(mutex_);  // 重入鎖
        
        if (!exists(path)) {
            createDirectory(path);  // 又呼叫回去了！
        }
    }
};
```

### 🔄 呼叫堆疊範例

```
呼叫過程：
createDirectory("/a/b/c/d")
  ├─ lock()  [計數=1]
  ├─ ensureDirectoryExists("/a/b/c")
  │    ├─ lock()  [計數=2]  ← 同一執行緒，允許！
  │    ├─ createDirectory("/a/b/c")
  │    │    ├─ lock()  [計數=3]
  │    │    ├─ ensureDirectoryExists("/a/b")
  │    │    │    └─ lock()  [計數=4]
  │    │    │    └─ unlock() [計數=3]
  │    │    └─ unlock() [計數=2]
  │    └─ unlock() [計數=1]
  └─ unlock() [計數=0]  ← 真正釋放
```

### ✅ 優點
- **允許重入**：遞迴函式不會死鎖
- **簡化設計**：不需追蹤是否已加鎖
- **相容 OOP**：物件方法互相呼叫方便

### ❌ 缺點
- **效能較差**：需要記錄擁有者和計數
- **容易誤用**：隱藏設計問題
- **記憶體開銷**：需要額外儲存資訊

### 🎯 使用場景
- 樹狀結構遍歷
- 遞迴演算法
- 複雜物件方法呼叫

---

## 6. 條件變數 (Condition Variable)

### 🎯 核心概念
想像「餐廳叫號系統」：
- **客人拿號碼牌等待**（wait）
- **廚師做好餐點通知**（notify）
- **被叫到號碼的去取餐**（被喚醒）

### 📊 示意圖

```
生產者-消費者模型：

生產者執行緒：                消費者執行緒：
┌─────────────┐              ┌─────────────┐
│ 生產資料    │              │ 等待資料    │
│   ↓         │              │  ↓          │
│ lock()      │              │ lock()      │
│   ↓         │              │   ↓         │
│ queue.push()│              │ while(empty)│
│   ↓         │              │   cv.wait() │ ← 釋放鎖並睡眠
│ cv.notify() │ ────通知───→ │ (被喚醒)    │ ← 重新取得鎖
│   ↓         │              │   ↓         │
│ unlock()    │              │ queue.pop() │
└─────────────┘              │   ↓         │
                             │ unlock()    │
                             └─────────────┘

時間序列：
消費者: [lock]→[檢查空]→[wait 睡眠......]→[被喚醒]→[pop]→[unlock]
生產者:                  [lock]→[push]→[notify]→[unlock]
                                        ↑
                                    喚醒訊號
```

### 💻 程式碼範例

```cpp
#include <condition_variable>
#include <mutex>
#include <queue>

template<typename T>
class BlockingQueue {
    std::queue<T> queue_;
    std::mutex mutex_;
    std::condition_variable cv_;
    
public:
    // 生產者：放入資料
    void push(T value) {
        std::unique_lock<std::mutex> lock(mutex_);
        queue_.push(value);
        cv_.notify_one();  // 通知一個等待的消費者
    }
    
    // 消費者：取出資料（會阻塞）
    T pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        
        // 等待直到佇列不為空
        cv_.wait(lock, [this] { return !queue_.empty(); });
        
        T value = queue_.front();
        queue_.pop();
        return value;
    }
    
    // 嘗試取出（不阻塞）
    bool try_pop(T& value, std::chrono::milliseconds timeout) {
        std::unique_lock<std::mutex> lock(mutex_);
        
        if (cv_.wait_for(lock, timeout, [this] { return !queue_.empty(); })) {
            value = queue_.front();
            queue_.pop();
            return true;
        }
        return false;  // 逾時
    }
};
```

### 🔄 詳細執行流程

```
初始狀態：佇列空

步驟 1: 消費者 A 嘗試 pop()
┌──────────┐
│ mutex_   │ ← A 取得
├──────────┤
│ queue_   │
│ (空)     │
└──────────┘
消費者 A: "佇列是空的，我要等待"
         cv_.wait() → 釋放 mutex_ → 進入睡眠

步驟 2: 生產者 B 執行 push("資料")
┌──────────┐
│ mutex_   │ ← B 取得（因為 A 釋放了）
├──────────┤
│ queue_   │
│ [資料]   │ ← B 放入
└──────────┘
生產者 B: "通知等待的人"
         cv_.notify_one() → 喚醒 A
         釋放 mutex_

步驟 3: 消費者 A 被喚醒
┌──────────┐
│ mutex_   │ ← A 重新取得
├──────────┤
│ queue_   │
│ [資料]   │ ← A 取出
└──────────┘
消費者 A: "拿到資料了！"
         返回 "資料"
         釋放 mutex_
```

### ⚠️ 常見陷阱：虛假喚醒

```cpp
// ❌ 錯誤寫法（可能虛假喚醒）
cv_.wait(lock);
T value = queue_.front();  // 可能 queue_ 還是空的！

// ✅ 正確寫法（用 predicate）
cv_.wait(lock, [this] { return !queue_.empty(); });
T value = queue_.front();  // 保證有資料

// 等價於：
while (queue_.empty()) {
    cv_.wait(lock);  // 被喚醒後重新檢查
}
```

### ✅ 優點
- **高效等待**：不需要忙碌輪詢
- **自動管理**：配合 RAII 不會忘記解鎖
- **支援逾時**：wait_for, wait_until

### ❌ 缺點
- **需搭配 Mutex**：不能單獨使用
- **虛假喚醒**：需要用 while 迴圈
- **效能開銷**：系統呼叫

### 🎯 使用場景
- 生產者-消費者佇列
- 執行緒池
- 事件通知系統

---

## 7. 信號量 (Semaphore)

### 🎯 核心概念
想像「停車場」：
- **有 N 個停車位**（資源數量）
- **車進來 → 可用車位 -1**（acquire）
- **車出去 → 可用車位 +1**（release）
- **車位滿了就在外面等**

### 📊 示意圖

```
二元信號量（Binary Semaphore）= Mutex
┌─────┐
│  1  │ ← 初始值
└─────┘

執行緒 A:  acquire() → 0 → [執行] → release() → 1
執行緒 B:              ↑ 等待（值=0）              ↑ 被喚醒

計數信號量（Counting Semaphore）：資源池
┌─────┐
│  3  │ ← 有 3 個資源
└─────┘

執行緒 A: acquire() → 2
執行緒 B: acquire() → 1
執行緒 C: acquire() → 0
執行緒 D: acquire() → [阻塞，等待有人 release()]

視覺化：
停車場（容量 3）：
[🚗] [🚗] [🚗]  ← 滿了，執行緒 D 在外面等
 A    B    C

執行緒 A 離開：
[  ] [🚗] [🚗]  ← 有空位了！執行緒 D 進來
     B    C
[🚗]
 D
```

### 💻 程式碼範例

```cpp
#include <semaphore>  // C++20

// 資料庫連線池（最多 5 個連線）
class ConnectionPool {
    std::counting_semaphore<5> semaphore_{5};  // 初始值 5
    std::vector<Connection*> connections_;
    std::mutex mutex_;
    
public:
    ConnectionPool() {
        // 初始化 5 個連線
        for (int i = 0; i < 5; ++i) {
            connections_.push_back(new Connection());
        }
    }
    
    // 取得連線（會阻塞直到有可用連線）
    Connection* acquire() {
        semaphore_.acquire();  // 可用數 -1（可能阻塞）
        
        std::lock_guard<std::mutex> lock(mutex_);
        Connection* conn = connections_.back();
        connections_.pop_back();
        return conn;
    }
    
    // 歸還連線
    void release(Connection* conn) {
        std::lock_guard<std::mutex> lock(mutex_);
        connections_.push_back(conn);
        
        semaphore_.release();  // 可用數 +1（喚醒等待者）
    }
    
    // 嘗試取得（不阻塞）
    Connection* try_acquire() {
        if (semaphore_.try_acquire()) {  // 成功返回 true
            std::lock_guard<std::mutex> lock(mutex_);
            Connection* conn = connections_.back();
            connections_.pop_back();
            return conn;
        }
        return nullptr;  // 無可用連線
    }
};

// 使用範例
void worker_thread(ConnectionPool& pool) {
    Connection* conn = pool.acquire();  // 等待可用連線
    
    // 使用連線執行查詢
    conn->execute("SELECT * FROM users");
    
    pool.release(conn);  // 歸還連線
}
```

### 🔄 執行時序

```
場景：5 個連線的資料庫池

時刻 0: 信號量值 = 5
┌───┬───┬───┬───┬───┐
│ 1 │ 2 │ 3 │ 4 │ 5 │ 所有連線都可用
└───┴───┴───┴───┴───┘

時刻 1: 執行緒 A, B, C, D, E 都 acquire()
信號量值 = 0
┌───┬───┬───┬───┬───┐
│ A │ B │ C │ D │ E │ 連線全部被佔用
└───┴───┴───┴───┴───┘

時刻 2: 執行緒 F, G 嘗試 acquire()
┌─────────┐
│ 等待佇列│
│   F     │ ← 阻塞中
│   G     │ ← 阻塞中
└─────────┘

時刻 3: 執行緒 A release()
信號量值 = 1 → 喚醒 F
┌───┬───┬───┬───┬───┐
│ F │ B │ C │ D │ E │
└───┴───┴───┴───┴───┘
等待佇列：[G]

時刻 4: 執行緒 B release()
信號量值 = 1 → 喚醒 G
┌───┬───┬───┬───┬───┐
│ F │ G │ C │ D │ E │
└───┴───┴───┴───┴───┘
```

### 🆚 Semaphore vs Mutex 對比

```
┌─────────────┬──────────────┬─────────────┐
│   特性      │   Mutex      │  Semaphore  │
├─────────────┼──────────────┼─────────────┤
│ 初始值      │ 1 (unlocked) │ N (可設定)  │
│ 誰能釋放    │ 只有擁有者   │ 任何執行緒  │
│ 用途        │ 互斥存取     │ 資源計數    │
│ 可重入      │ 需 recursive │ 不支援      │
└─────────────┴──────────────┴─────────────┘
```

### ✅ 優點
- **限制並行數**：控制資源使用
- **簡單直觀**：概念容易理解
- **彈性高**：支援多種語義（二元、計數）

### ❌ 缺點
- **容易誤用**：release 不當會破壞計數
- **無擁有權概念**：任何人都能 release
- **除錯困難**：信號量洩漏難以追蹤

### 🎯 使用場景
- 連線池、執行緒池
- 限流器（Rate Limiter）
- 資源池管理

---

## 8. 柵欄 (Barrier)

### 🎯 核心概念
想像「團體旅遊集合點」：
- **所有人都到了才能繼續**
- **早到的人等晚到的**
- **最後一人到達 → 所有人一起出發**

### 📊 示意圖

```
5 個執行緒使用 Barrier(5)：

執行緒 1:  ───────────●──→ [等待....]
執行緒 2:  ──────●───────→ [等待....]
執行緒 3:  ────●─────────→ [等待....]
執行緒 4:  ──●───────────→ [等待....]
執行緒 5:  ─────────────●→ [最後到達，釋放所有人！]
                         ↓
執行緒 1:                ──────────→ [繼續執行]
執行緒 2:                ──────────→ [繼續執行]
執行緒 3:                ──────────→ [繼續執行]
執行緒 4:                ──────────→ [繼續執行]
執行緒 5:                ──────────→ [繼續執行]

集合點示意：
到達計數器：0/5 → 1/5 → 2/5 → 3/5 → 4/5 → 5/5 ✓
            ↑     ↑     ↑     ↑     ↑     ↑
           T4    T2    T3    T1    T5   (全員到齊！)
```

### 💻 程式碼範例

```cpp
#include <barrier>  // C++20

// 多階段平行計算
class ParallelProcessor {
    std::barrier<> sync_point_;  // 同步點
    std::vector<std::thread> workers_;
    
public:
    ParallelProcessor(int num_threads) 
        : sync_point_(num_threads) {  // 初始化柵欄
        
        for (int i = 0; i < num_threads; ++i) {
            workers_.emplace_back([this, i] {
                worker_task(i);
            });
        }
    }
    
    void worker_task(int id) {
        // 階段 1：讀取資料
        auto data = read_data(id);
        sync_point_.arrive_and_wait();  // 等所有人讀完
        
        // 階段 2：處理資料
        auto result = process_data(data);
        sync_point_.arrive_and_wait();  // 等所有人處理完
        
        // 階段 3：寫入結果
        write_result(id, result);
        sync_point_.arrive_and_wait();  // 等所有人寫完
    }
};

// 使用回調的版本（C++20）
void parallel_map_reduce() {
    const int N = 4;
    std::vector<int> results(N);
    
    // Barrier 完成時執行的回調
    auto on_completion = [&]() noexcept {
        int sum = 0;
        for (int r : results) sum += r;
        std::cout << "總和: " << sum << std::endl;
    };
    
    std::barrier sync_point(N, on_completion);
    
    std::vector<std::thread> threads;
    for (int i = 0; i < N; ++i) {
        threads.emplace_back([&, i] {
            results[i] = compute(i);
            sync_point.arrive_and_wait();  // 最後一人觸發回調
        });
    }
    
    for (auto& t : threads) t.join();
}
```

### 🔄 執行時序範例

```
場景：4 個執行緒計算矩陣

階段 1：每個執行緒計算自己的列
┌─────────────────────────────────┐
│ Thread 0: [計算列 0] → 完成 ●   │
│ Thread 1: [計算列 1] → 完成 ●   │
│ Thread 2: [計算列 2........] →  │ ← 還在算
│ Thread 3: [計算列 3] → 完成 ●   │
└─────────────────────────────────┘
到達計數：3/4（等待 Thread 2）

Thread 2 完成：
┌─────────────────────────────────┐
│ Thread 0: [等待]                │
│ Thread 1: [等待]                │
│ Thread 2: [計算列 2] → 完成 ● → │ 全員到齊！
│ Thread 3: [等待]                │
└─────────────────────────────────┘
到達計數：4/4 ✓ → 所有人繼續

階段 2：同步後開始下一階段
┌─────────────────────────────────┐
│ Thread 0: → [正規化列 0]        │
│ Thread 1: → [正規化列 1]        │
│ Thread 2: → [正規化列 2]        │
│ Thread 3: → [正規化列 3]        │
└─────────────────────────────────┘
```

### 🆚 Barrier vs Condition Variable

```
┌────────────┬─────────────────┬──────────────────┐
│   比較項   │    Barrier      │ Condition Var    │
├────────────┼─────────────────┼──────────────────┤
│ 喚醒方式   │ 最後一人到達    │ 明確 notify      │
│ 等待語義   │ 全員到齊        │ 條件滿足         │
│ 重複使用   │ 自動重置        │ 需手動管理       │
│ 適用場景   │ 多階段同步      │ 生產者-消費者    │
└────────────┴─────────────────┴──────────────────┘
```

### ✅ 優點
- **簡化多階段同步**：不需複雜的計數邏輯
- **自動重置**：可重複使用
- **支援回調**：完成時自動執行

### ❌ 缺點
- **固定參與者數量**：無法動態調整
- **全員阻塞**：一個慢拖累全部
- **需 C++20**：舊編譯器不支援

### 🎯 使用場景
- 平行演算法（MapReduce）
- GPU 計算同步
- 遊戲引擎幀同步

---

## 9. 順序鎖 (Seqlock)

### 🎯 核心概念
想像「博物館展品」：
- **參觀者**：隨時可以看（讀者）
- **管理員**：偶爾換展品（寫者）
- **參觀者規則**：如果看到管理員在換，重新看一次

### 📊 示意圖

```
資料結構：
┌─────────────────────┐
│ sequence: 0 (偶數)  │ ← 版本號
│ data: {x:10, y:20}  │ ← 實際資料
└─────────────────────┘

寫入過程：
步驟 1: 寫者開始
sequence = 1 (奇數)  ← "正在修改中"
寫者: 寫入 x = 15
寫者: 寫入 y = 25
sequence = 2 (偶數)  ← "修改完成"

讀取過程（樂觀讀取）：
┌──────────────────────────────────────┐
│ 讀者開始:                            │
│   seq1 = sequence.load()  // 記錄版本│
│   ↓                                  │
│   讀取 data                          │
│   ↓                                  │
│   seq2 = sequence.load()  // 再次檢查│
│   ↓                                  │
│   if (seq1 == seq2 && seq1 % 2 == 0) │
│     → 資料一致，使用它               │
│   else                               │
│     → 重試！                         │
└──────────────────────────────────────┘

時序圖：
讀者 A:  [seq=0] → 讀取 → [seq=0] ✓ 成功
寫者:                  [seq=1] 寫入中 [seq=2]
讀者 B:          [seq=0] → 讀取 → [seq=2] ✗ 重試
                         [seq=2] → 讀取 → [seq=2] ✓ 成功
```

### 💻 程式碼範例

```cpp
#include <atomic>

template<typename T>
class Seqlock {
    std::atomic<unsigned> sequence_{0};
    T data_;
    
public:
    // 寫入（獨佔）
    void write(const T& new_data) {
        // 步驟 1：增加版本號（變奇數）
        unsigned seq = sequence_.load(std::memory_order_relaxed);
        sequence_.store(seq + 1, std::memory_order_release);
        
        // 步驟 2：寫入資料
        data_ = new_data;
        
        // 步驟 3：再次增加版本號（變偶數）
        sequence_.store(seq + 2, std::memory_order_release);
    }
    
    // 讀取（樂觀）
    T read() const {
        T result;
        unsigned seq1, seq2;
        
        do {
            // 記錄版本號
            seq1 = sequence_.load(std::memory_order_acquire);
            
            // 如果是奇數，表示正在寫入，等一下
            while (seq1 & 1) {
                seq1 = sequence_.load(std::memory_order_acquire);
            }
            
            // 讀取資料
            result = data_;
            
            // 檢查版本號是否改變
            seq2 = sequence_.load(std::memory_order_acquire);
            
        } while (seq1 != seq2);  // 不一致就重試
        
        return result;
    }
};

// 實際應用：座標追蹤
struct Position {
    double x, y, z;
    uint64_t timestamp;
};

Seqlock<Position> player_position;

// 遊戲執行緒（寫者）
void update_position(double x, double y, double z) {
    Position pos{x, y, z, get_timestamp()};
    player_position.write(pos);
}

// 渲染執行緒（讀者）
void render_player() {
    Position pos = player_position.read();
    draw_at(pos.x, pos.y, pos.z);
}
```

### 🔄 競爭條件處理

```
場景：讀者在寫者修改期間讀取

初始狀態：
┌────────────────────┐
│ sequence = 100     │
│ x = 10, y = 20     │
└────────────────────┘

時刻 T1：讀者開始讀取
讀者: seq1 = 100 (偶數，OK)
讀者: 讀取 x = 10

時刻 T2：寫者開始寫入（在讀者讀完之前）
寫者: sequence = 101 (奇數)  ← 標記"正在寫"
寫者: x = 15
寫者: y = 25
寫者: sequence = 102 (偶數)

時刻 T3：讀者讀完檢查
讀者: 讀取 y = 25  ← 可能是新值！
讀者: seq2 = 102
讀者: seq1(100) != seq2(102) → 資料不一致！
讀者: 重試...

時刻 T4：讀者重試
讀者: seq1 = 102
讀者: 讀取 x = 15, y = 25
讀者: seq2 = 102
讀者: seq1 == seq2 → 成功！✓
```

### 🆚 Seqlock vs RWLock

```
┌─────────────┬──────────────┬─────────────┐
│   特性      │   Seqlock    │   RWLock    │
├─────────────┼──────────────┼─────────────┤
│ 讀取成本    │ 無鎖（快）   │ 需加鎖（慢）│
│ 寫入成本    │ 無鎖         │ 獨佔鎖      │
│ 讀失敗處理  │ 重試         │ 阻塞等待    │
│ 資料一致性  │ 最終一致     │ 強一致      │
│ 適用場景    │ 讀多寫少     │ 讀多寫中    │
└─────────────┴──────────────┴─────────────┘
```

### ✅ 優點
- **讀取超快**：完全無鎖
- **寫者不阻塞讀者**：讀者自己重試
- **無死鎖**：沒有鎖就不會卡

### ❌ 缺點
- **讀者可能餓死**：頻繁寫入時一直重試
- **資料大小限制**：複製成本高
- **寫者需互斥**：多寫者需額外機制

### 🎯 使用場景
- 即時系統（股票價格）
- 遊戲引擎（位置更新）
- 系統監控（統計資料）

---

## 10. 效能比較總表

### 📊 延遲對比

```
操作延遲（單位：奈秒，以現代 x86-64 為準）：

Lock-Free (CAS):      ~10-50 ns
Spinlock:             ~50-100 ns
Mutex (無競爭):       ~50-100 ns
Mutex (有競爭):       ~1,000-10,000 ns  ← Context Switch
RWLock (讀):          ~100-200 ns
RWLock (寫):          ~1,000-10,000 ns
Semaphore:            ~1,000-5,000 ns
Condition Variable:   ~1,000-10,000 ns

圖示：
Lock-Free  ▓░░░░░░░░░░░░░░░░░░░░  (極快)
Spinlock   ▓▓░░░░░░░░░░░░░░░░░░░  (快)
Mutex(無)  ▓▓░░░░░░░░░░░░░░░░░░░  (快)
Mutex(有)  ▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░  (慢)
Semaphore  ▓▓▓▓▓▓▓▓░░░░░░░░░░░░  (中慢)
```

### 🎯 使用場景選擇表

```
┌────────────────────┬──────────────────────────────────┐
│     場景           │          推薦鎖機制              │
├────────────────────┼──────────────────────────────────┤
│ SPSC 佇列          │ Lock-Free Queue                  │
│ 共享計數器         │ Atomic / Spinlock                │
│ 銀行轉帳           │ Mutex                            │
│ 快取系統           │ RWLock / Seqlock                 │
│ 遞迴函式保護       │ Recursive Mutex                  │
│ 生產者-消費者      │ Condition Variable               │
│ 連線池             │ Semaphore                        │
│ 平行演算法同步     │ Barrier                          │
│ 即時股價更新       │ Seqlock                          │
│ 核心 Interrupt     │ Spinlock                         │
└────────────────────┴──────────────────────────────────┘
```

### 🔍 決策樹

```
開始
  │
  ├─ 是否需要共享資料？
  │   ├─ 否 → 無需鎖（Thread-Local Storage）
  │   └─ 是 ↓
  │
  ├─ 是否為 SPSC 模式？
  │   ├─ 是 → Lock-Free Queue
  │   └─ 否 ↓
  │
  ├─ 臨界區是否極短（< 100ns）？
  │   ├─ 是 → Spinlock / Atomic
  │   └─ 否 ↓
  │
  ├─ 是否讀多寫少（讀寫比 > 10:1）？
  │   ├─ 是 → RWLock / Seqlock
  │   └─ 否 ↓
  │
  ├─ 是否需要限制資源數量？
  │   ├─ 是 → Semaphore
  │   └─ 否 ↓
  │
  ├─ 是否需要條件等待？
  │   ├─ 是 → Condition Variable
  │   └─ 否 ↓
  │
  ├─ 是否有遞迴呼叫？
  │   ├─ 是 → Recursive Mutex
  │   └─ 否 ↓
  │
  └─ 預設選擇 → Mutex
```

### ⚡ 優化建議

```
1. 減少鎖粒度
   ❌ 整個物件一個大鎖
   ✅ 不同欄位用不同鎖

2. 避免鎖順序死鎖
   ❌ 執行緒 A: lock(L1) → lock(L2)
      執行緒 B: lock(L2) → lock(L1)
   ✅ 統一鎖順序：都先 L1 再 L2

3. 使用 RAII 管理鎖
   ❌ mutex.lock();
      do_something();
      mutex.unlock();  // 可能忘記
   ✅ std::lock_guard<std::mutex> lock(mutex);

4. 考慮無鎖替代
   ❌ mutex + counter++
   ✅ std::atomic<int> counter;
      counter.fetch_add(1);

5. 批次操作減少鎖次數
   ❌ for (item : items) {
        lock();
        process(item);
        unlock();
      }
   ✅ lock();
      for (item : items) {
        process(item);
      }
      unlock();
```

---

## 📝 總結

### 快速記憶口訣

```
🚀 速度要求高？        → Lock-Free / Spinlock
🔐 簡單互斥就好？      → Mutex
📖 讀多寫少？          → RWLock / Seqlock
🔁 會遞迴呼叫？        → Recursive Mutex
⏰ 需要條件等待？      → Condition Variable
🎫 限制資源數量？      → Semaphore
🚧 多階段同步？        → Barrier
```

### 常見錯誤

```
❌ 忘記解鎖               → 使用 RAII (lock_guard)
❌ 死鎖                   → 統一鎖順序
❌ 虛假喚醒               → Condition Variable 用 while
❌ 過度使用 Spinlock      → 長臨界區用 Mutex
❌ 忽略記憶體順序         → Atomic 正確使用 memory_order
```

---

## 📚 延伸閱讀

- [C++ Concurrency in Action (2nd Edition)](https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition)
- [The Art of Multiprocessor Programming](https://www.elsevier.com/books/the-art-of-multiprocessor-programming/herlihy/978-0-12-415950-1)
- [Linux Kernel Locking](https://www.kernel.org/doc/html/latest/locking/index.html)

---

**文件版本**: 1.0  
**最後更新**: 2026-01-09  
**授權**: CC BY-NC-SA 4.0

---

## 附錄：實用程式碼片段

### A1. 簡易效能測試框架

```cpp
#include <chrono>
#include <iostream>

template<typename Func>
double benchmark(Func f, int iterations = 1000000) {
    auto start = std::chrono::high_resolution_clock::now();
    
    for (int i = 0; i < iterations; ++i) {
        f();
    }
    
    auto end = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::nanoseconds>(end - start);
    
    return duration.count() / (double)iterations;
}

// 使用範例
int main() {
    std::mutex mutex;
    int counter = 0;
    
    double avg_ns = benchmark([&] {
        std::lock_guard<std::mutex> lock(mutex);
        ++counter;
    });
    
    std::cout << "平均每次操作: " << avg_ns << " ns\n";
}
```

### A2. 死鎖檢測器

```cpp
#include <map>
#include <thread>
#include <mutex>

class DeadlockDetector {
    std::map<std::thread::id, std::vector<void*>> held_locks_;
    std::mutex detector_mutex_;
    
public:
    void acquire(void* lock) {
        std::lock_guard<std::mutex> guard(detector_mutex_);
        auto tid = std::this_thread::get_id();
        held_locks_[tid].push_back(lock);
        check_for_cycles(tid);
    }
    
    void release(void* lock) {
        std::lock_guard<std::mutex> guard(detector_mutex_);
        auto tid = std::this_thread::get_id();
        auto& locks = held_locks_[tid];
        locks.erase(std::remove(locks.begin(), locks.end(), lock), locks.end());
    }
    
private:
    void check_for_cycles(std::thread::id tid) {
        // 簡化版：檢查是否有執行緒持有多個鎖
        if (held_locks_[tid].size() > 1) {
            std::cerr << "警告：執行緒持有多個鎖，可能死鎖！\n";
        }
    }
};
```

---

希望這份指南能幫助你理解各種鎖機制！🎓
