# Linux 系統鎖與 C++ 鎖機制完整指南 📚

## 📊 鎖機制視覺化概覽

```
鎖的選擇流程圖：
┌──────────────────┐
│   需要同步嗎？   │
└─────┬────────────┘
      │ 是
      ▼
┌──────────────────┐    ┌──────────────────┐
│   簡單計數？     │───▶│   使用 atomic    │
└─────┬────────────┘ 是 │  🔢 原子操作     │
      │ 否              └──────────────────┘
      ▼
┌──────────────────┐    ┌──────────────────┐
│   多讀少寫？     │───▶│ 使用 shared_mutex│
└─────┬────────────┘ 是 │  📖 讀寫鎖       │
      │ 否              └──────────────────┘
      ▼
┌──────────────────┐    ┌──────────────────┐
│   等待時間短？   │───▶│  使用 spinlock   │
└─────┬────────────┘ 是 │  🌀 自旋鎖       │
      │ 否              └──────────────────┘
      ▼
┌──────────────────┐    ┌──────────────────┐
│   需要等條件？   │───▶│使用condition_var │
└─────┬────────────┘ 是 │   🚌 條件變數    │
      │ 否              └──────────────────┘
      ▼
┌──────────────────┐
│   使用 mutex     │
│   🔒 互斥鎖      │
└──────────────────┘
```

---

## Linux 系統鎖 🐧

### 1. Mutex (互斥鎖) 🔒

**白話解釋**: 就像廁所門鎖，一次只能一個人使用，其他人必須在外面等待  
**用途**: 保護共享資源，同一時間只允許一個執行緒存取  
**使用時機**: 當多個執行緒需要存取同一個變數或資料結構時

```
Mutex 工作示意圖：
執行緒A: 🏃‍♂️ ──▶ 🔒[資源] ◀── ⏸️ 執行緒B (等待)
                              ⏸️ 執行緒C (等待)

時間線：
T1: A獲得鎖 🔒✅    B等待❌    C等待❌
T2: A釋放鎖 🔓      B獲得鎖✅   C等待❌  
T3: B釋放鎖 🔓      C獲得鎖✅
```

**程式碼範例:**
```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
int shared_counter = 0;

void* worker_thread(void* arg) {
    pthread_mutex_lock(&mutex);
    shared_counter++;
    printf("Counter: %d\n", shared_counter);
    pthread_mutex_unlock(&mutex);
    return NULL;
}

int main() {
    pthread_t threads[5];
    
    // 創建5個執行緒
    for (int i = 0; i < 5; i++) {
        pthread_create(&threads[i], NULL, worker_thread, NULL);
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 5; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Final counter: %d\n", shared_counter);
    pthread_mutex_destroy(&mutex);
    return 0;
}
```

> 💡 **完整範例**: 查看 `locks_examples/01_pthread_mutex.c` 獲得完整可編譯的程式碼

---

### 2. Semaphore (信號量) 🚗

**白話解釋**: 像停車場管理員，有固定的停車位數量，滿了就要等有人開走  
**用途**: 控制同時存取資源的執行緒數量  
**使用時機**: 限制同時使用資源的執行緒數量，比如連線池

```
Semaphore 工作示意圖 (假設最多3個車位)：
停車場: [🚗][🚗][🚗] ← 滿了
等待區: 🚗💤 🚗💤 🚗💤

當有車離開：
停車場: [🚗][🚗][  ] ← 有空位
等待區: 🚗💤 🚗💤     ← 一臺車可以進入

數量控制：
sem_init(&sem, 0, 3);  // 最多3個同時進入
等待中: ████████░░     (8個等待，2個在執行)
```

**程式碼範例:**
```c
#include <semaphore.h>
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>
#include <stdlib.h>

sem_t semaphore;

void* worker(void* arg) {
    int id = *(int*)arg;
    sem_wait(&semaphore);  // 取得資源
    printf("Worker %d: Working...\n", id);
    sleep(2);  // 模擬工作
    printf("Worker %d: Done\n", id);
    sem_post(&semaphore);  // 釋放資源
    return NULL;
}

int main() {
    pthread_t threads[6];
    int ids[6];
    
    sem_init(&semaphore, 0, 3);  // 最多3個執行緒同時工作
    
    // 創建6個執行緒
    for (int i = 0; i < 6; i++) {
        ids[i] = i + 1;
        pthread_create(&threads[i], NULL, worker, &ids[i]);
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 6; i++) {
        pthread_join(threads[i], NULL);
    }
    
    sem_destroy(&semaphore);
    return 0;
}
```

---

### 3. Spinlock (自旋鎖) 🌀

**白話解釋**: 像在門外一直敲門等待，不會離開也不會休息，持續檢查門是否開了  
**用途**: 短時間等待的鎖，不會讓執行緒進入睡眠  
**使用時機**: 預期等待時間很短的情況

```
Spinlock vs Mutex 比較：

Spinlock 🌀:
執行緒B: 🏃‍♂️ ──▶ 🌀🌀🌀 (一直轉圈檢查)
        消耗CPU: ████████████

Mutex 🔒:
執行緒B: 🏃‍♂️ ──▶ 😴💤 (進入睡眠等待)
        消耗CPU: ░░░░░░░░░░░░

適用場景：
短等待 (< 10μs): Spinlock ✅
長等待 (> 10μs): Mutex ✅
```

**程式碼範例:**
```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>

pthread_spinlock_t spinlock;
int shared_data = 0;

void* fast_operation(void* arg) {
    for (int i = 0; i < 1000; i++) {
        pthread_spin_lock(&spinlock);
        // 很快完成的操作
        shared_data++;
        pthread_spin_unlock(&spinlock);
    }
    return NULL;
}

int main() {
    pthread_t threads[4];
    
    pthread_spin_init(&spinlock, PTHREAD_PROCESS_PRIVATE);
    
    // 創建4個執行緒
    for (int i = 0; i < 4; i++) {
        pthread_create(&threads[i], NULL, fast_operation, NULL);
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 4; i++) {
        pthread_join(threads[i], NULL);
    }
    
    printf("Final shared_data: %d\n", shared_data);
    pthread_spin_destroy(&spinlock);
    return 0;
}
```

---

### 4. Read-Write Lock (讀寫鎖) 📖

**白話解釋**: 像圖書館規則，很多人可以同時看書（讀），但只能一個人寫字（寫）  
**用途**: 允許多個讀者同時存取，但寫者獨佔  
**使用時機**: 讀取頻繁但寫入較少的場景

```
Read-Write Lock 狀態圖：

讀取模式 📖:
資料: [📚] ← 👀👀👀👀 (多個讀者同時看)
等待: 📝💤 (寫者等待)

寫入模式 📝:
資料: [📚] ← ✍️ (只有一個寫者)
等待: 👀💤 👀💤 📝💤 (所有其他人等待)

性能比較：
傳統Mutex: R-R-R-W-R-R (序列執行)
ReadWrite:  RRR──W─RR  (讀取並行)
```

**程式碼範例:**
```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_rwlock_t rwlock = PTHREAD_RWLOCK_INITIALIZER;
int shared_data = 0;

void* reader(void* arg) {
    int id = *(int*)arg;
    pthread_rwlock_rdlock(&rwlock);
    printf("Reader %d: Reading data: %d\n", id, shared_data);
    usleep(100000);  // 模擬讀取時間
    pthread_rwlock_unlock(&rwlock);
    return NULL;
}

void* writer(void* arg) {
    int id = *(int*)arg;
    pthread_rwlock_wrlock(&rwlock);
    shared_data++;
    printf("Writer %d: Updated data to: %d\n", id, shared_data);
    usleep(200000);  // 模擬寫入時間
    pthread_rwlock_unlock(&rwlock);
    return NULL;
}

int main() {
    pthread_t readers[5], writers[2];
    int reader_ids[5], writer_ids[2];
    
    // 創建多個讀者
    for (int i = 0; i < 5; i++) {
        reader_ids[i] = i + 1;
        pthread_create(&readers[i], NULL, reader, &reader_ids[i]);
    }
    
    // 創建少數寫者
    for (int i = 0; i < 2; i++) {
        writer_ids[i] = i + 1;
        pthread_create(&writers[i], NULL, writer, &writer_ids[i]);
    }
    
    // 等待所有執行緒完成
    for (int i = 0; i < 5; i++) {
        pthread_join(readers[i], NULL);
    }
    for (int i = 0; i < 2; i++) {
        pthread_join(writers[i], NULL);
    }
    
    pthread_rwlock_destroy(&rwlock);
    return 0;
}
```

---

### 5. Condition Variable (條件變數) 🚌

**白話解釋**: 像等公車的站牌，只有當公車來了（條件滿足）才上車，否則就一直等  
**用途**: 讓執行緒等待特定條件成立  
**使用時機**: 生產者-消費者模式，或需要等待某個狀態改變

```
Condition Variable 工作流程：

生產者-消費者模式：
生產者: 🏭 ──▶ [緩衝區] ──▶ 📢 通知消費者
消費者: 👤💤 ──▶ 🔔收到通知 ──▶ 👤🏃‍♂️ 開始工作

等待流程：
1. 獲取鎖    🔒
2. 檢查條件  ❓ (while循環)
3. 如果不滿足 😴 wait() 
4. 收到信號  🔔 signal()
5. 重新檢查  ❓ 
6. 執行工作  ⚙️
7. 釋放鎖    🔓
```

**程式碼範例:**
```c
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t condition = PTHREAD_COND_INITIALIZER;
int ready = 0;

void* waiter(void* arg) {
    int id = *(int*)arg;
    pthread_mutex_lock(&mutex);
    printf("Waiter %d: Waiting for condition...\n", id);
    while (!ready) {
        pthread_cond_wait(&condition, &mutex);
    }
    printf("Waiter %d: Condition met!\n", id);
    pthread_mutex_unlock(&mutex);
    return NULL;
}

void* signaler(void* arg) {
    sleep(2);
    pthread_mutex_lock(&mutex);
    printf("Signaler: Setting ready flag\n");
    ready = 1;
    pthread_cond_broadcast(&condition);  // 喚醒所有等待者
    pthread_mutex_unlock(&mutex);
    return NULL;
}

int main() {
    pthread_t waiters[3], sig;
    int waiter_ids[3];
    
    // 創建等待者執行緒
    for (int i = 0; i < 3; i++) {
        waiter_ids[i] = i + 1;
        pthread_create(&waiters[i], NULL, waiter, &waiter_ids[i]);
    }
    
    // 創建信號執行緒
    pthread_create(&sig, NULL, signaler, NULL);
    
    // 等待所有執行緒完成
    for (int i = 0; i < 3; i++) {
        pthread_join(waiters[i], NULL);
    }
    pthread_join(sig, NULL);
    
    pthread_mutex_destroy(&mutex);
    pthread_cond_destroy(&condition);
    return 0;
}
```

---

## C++ 鎖機制 ⚡

### 1. std::mutex 🔐

**白話解釋**: 標準版的廁所門鎖，C++ 內建的互斥鎖  
**用途**: C++ 標準的互斥鎖  
**使用時機**: 基本的互斥存取控制

```
RAII 自動管理示意圖：

手動管理 ❌:
mtx.lock();     🔒
// 工作...      ⚙️
mtx.unlock();   🔓  ← 容易忘記！

RAII管理 ✅:
{
  lock_guard<mutex> lock(mtx);  🔒自動鎖定
  // 工作...                   ⚙️
}  ← 🔓自動解鎖 (離開作用域)
```

**程式碼範例:**
```cpp
#include <mutex>
#include <thread>
#include <iostream>

std::mutex mtx;
int counter = 0;

void increment() {
    std::lock_guard<std::mutex> lock(mtx);  // RAII 自動解鎖
    counter++;
    std::cout << "Counter: " << counter << std::endl;
}

int main() {
    std::thread t1(increment);
    std::thread t2(increment);
    t1.join();
    t2.join();
    return 0;
}
```

---

### 2. std::recursive_mutex 🔄

**白話解釋**: 像有記憶的門鎖，記得是誰鎖的，同一個人可以重複進入  
**用途**: 可重複鎖定的互斥鎖  
**使用時機**: 同一執行緒可能需要多次獲得鎖

```
Recursive Mutex 遞迴示意圖：

執行緒A 獲得鎖計數：
func1() { 
  lock(rmtx); 🔒 計數=1
  func2();    
}
func2() { 
  lock(rmtx); 🔒 計數=2 ← 同一執行緒可以再鎖
  // 工作
  unlock();   🔓 計數=1
}
unlock();     🔓 計數=0 ← 完全釋放

一般mutex會死鎖 ❌:
Thread A: 🔒 → 🔒 → 💀 (死鎖)
```

**程式碼範例:**
```cpp
#include <mutex>
#include <thread>

std::recursive_mutex rmtx;

void recursive_function(int n) {
    std::lock_guard<std::recursive_mutex> lock(rmtx);
    std::cout << "Level: " << n << std::endl;
    if (n > 0) {
        recursive_function(n - 1);  // 同一執行緒再次獲得鎖
    }
}
```

---

### 3. std::shared_mutex (C++17) 📚

**白話解釋**: 進階版圖書館規則，多人可以同時看書，但寫字時要清場  
**用途**: 讀寫鎖的 C++ 實現  
**使用時機**: 多讀少寫的場景

```
Shared Mutex 模式對比：

shared_lock (讀取模式) 📖:
Reader1: 👀 ──▶ [Data] ◀── 👀 Reader2
Reader3: 👀 ──▶ [Data] ◀── 👀 Reader4
Writer:  ✍️💤 (等待所有讀者完成)

unique_lock (寫入模式) ✍️:
Writer:  ✍️ ──▶ [Data] 
Reader1: 👀💤 (等待)
Reader2: 👀💤 (等待)

性能提升圖：
讀寫比例:  90% 讀 / 10% 寫
Mutex:     ████████████████ (100% 序列)
SharedMtx: ████░░░░████░░░░ (40% 序列) ← 效能提升!
```

**程式碼範例:**
```cpp
#include <shared_mutex>
#include <thread>
#include <vector>

std::shared_mutex sh_mtx;
std::vector<int> data = {1, 2, 3, 4, 5};

void reader() {
    std::shared_lock<std::shared_mutex> lock(sh_mtx);
    for (int val : data) {
        std::cout << val << " ";
    }
    std::cout << std::endl;
}

void writer() {
    std::unique_lock<std::shared_mutex> lock(sh_mtx);
    data.push_back(data.size() + 1);
    std::cout << "Added element\n";
}
```

---

### 4. std::condition_variable 📡

**白話解釋**: C++ 版的公車站牌，可以設定複雜的等車條件  
**用途**: C++ 的條件變數  
**使用時機**: 執行緒間的同步通訊

```
Producer-Consumer 圖解：

Buffer: [   |   |   ] (空的)
Producer: 🏭 ──▶ 📦 ──▶ [📦 |   |   ] ──▶ 📢 notify()
Consumer: 👤😴 ──▶ 🔔收到 ──▶ [   |   |   ] ──▶ 📦處理

等待條件邏輯：
wait(lock, []{ return !buffer.empty(); });
     ↓
while (!buffer.empty()) {  ← 自動轉換為while循環
    // 避免虛假喚醒
}

狀態轉換：
Consumer: 😴 (wait) → 🔔 (notify) → 👀 (check) → ⚙️ (work)
```

**程式碼範例:**
```cpp
#include <condition_variable>
#include <mutex>
#include <queue>
#include <thread>

std::mutex mtx;
std::condition_variable cv;
std::queue<int> buffer;

void producer() {
    for (int i = 0; i < 5; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        buffer.push(i);
        std::cout << "Produced: " << i << std::endl;
        cv.notify_one();
    }
}

void consumer() {
    for (int i = 0; i < 5; ++i) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, []{ return !buffer.empty(); });
        int item = buffer.front();
        buffer.pop();
        std::cout << "Consumed: " << item << std::endl;
    }
}
```

---

### 5. std::atomic ⚛️

**白話解釋**: 像原子彈一樣，動作不可分割，要嘛全做完，要嘛不做  
**用途**: 原子操作，無鎖編程  
**使用時機**: 簡單的數值操作，避免鎖的開銷

```
Atomic vs Mutex 性能對比：

非原子操作問題 ❌:
Thread1: 讀取(5) → +1 → 寫入(6)
Thread2:   讀取(5) → +1 → 寫入(6) ← 丟失更新!
結果: 6 (錯誤，應該是7)

原子操作 ✅:
Thread1: atomic++ → 6
Thread2: atomic++ → 7 ← 正確!

性能圖表：
操作類型:     Atomic    Mutex     
延遲:        ████      ████████  
CPU使用:     ████      ██████    
程式碼複雜度: ███       ██████    
```

**🔥 基本原子操作範例:**
```cpp
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

int main() {
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
    
    return 0;
}
```

**🚀 實際應用範例 - 無鎖佇列:**
```cpp
#include <atomic>
#include <memory>

template<typename T>
class LockFreeQueue {
private:
    struct Node {
        std::atomic<T*> data{nullptr};
        std::atomic<Node*> next{nullptr};
    };
    
    std::atomic<Node*> head{new Node};
    std::atomic<Node*> tail{head.load()};

public:
    ~LockFreeQueue() {
        // 清理所有節點
        while (Node* head_node = head.load()) {
            head.store(head_node->next.load());
            T* data = head_node->data.load();
            if (data) delete data;
            delete head_node;
        }
    }
    
    void enqueue(T item) {
        Node* new_node = new Node;
        T* data = new T(std::move(item));
        
        Node* prev_tail = tail.exchange(new_node);
        prev_tail->data.store(data);
        prev_tail->next.store(new_node);
    }
    
    bool dequeue(T& result) {
        Node* head_node = head.load();
        Node* next = head_node->next.load();
        
        if (next == nullptr) {
            return false;  // 佇列為空
        }
        
        T* data = next->data.exchange(nullptr);
        if (data == nullptr) {
            return false;  // 其他執行緒已取走
        }
        
        result = *data;
        delete data;
        
        // 更安全的 head 更新
        if (head.compare_exchange_weak(head_node, next)) {
            delete head_node;
        }
        return true;
    }
};

// 使用範例
LockFreeQueue<int> queue;

void producer() {
    for (int i = 0; i < 100; ++i) {
        queue.enqueue(i);
    }
}

void consumer() {
    int value;
    for (int i = 0; i < 50; ++i) {
        while (!queue.dequeue(value)) {
            std::this_thread::yield();  // 等待數據
        }
        std::cout << "取得: " << value << std::endl;
    }
}
```

**⚡ 原子操作的記憶體順序:**
```cpp
#include <atomic>

std::atomic<bool> ready{false};
std::atomic<int> data{0};

// 1. 順序一致性 (預設，最安全但較慢)
void sequential_consistency() {
    data.store(42);                    // 預設 memory_order_seq_cst
    ready.store(true);                 // 預設 memory_order_seq_cst
}

// 2. 釋放-獲取語義 (較快，常用)
void release_acquire() {
    data.store(42, std::memory_order_relaxed);    // 資料寫入
    ready.store(true, std::memory_order_release); // 發布信號
    
    // 另一個執行緒
    if (ready.load(std::memory_order_acquire)) {  // 獲取信號
        int value = data.load(std::memory_order_relaxed); // 讀取資料
        std::cout << "讀到: " << value << std::endl;
    }
}

// 3. 鬆散記憶體順序 (最快，僅保證原子性)
std::atomic<int> relaxed_counter{0};

void relaxed_operations() {
    // 只保證這個操作是原子的，不保證與其他記憶體操作的順序
    relaxed_counter.fetch_add(1, std::memory_order_relaxed);
}
```

**🚫 為什麼 Atomic 不能處理複雜同步？**

#### 1. **原子性限制 - 只能保證單一操作**

```cpp
// ❌ 這不是原子的！多個步驟無法合併
std::atomic<int> balance{1000};

void withdraw(int amount) {
    // 這是兩個獨立的原子操作，中間可能被打斷！
    if (balance.load() >= amount) {    // 步驟1: 檢查餘額
        balance -= amount;             // 步驟2: 扣除金額
    }
    // 問題：在步驟1和2之間，其他執行緒可能修改balance！
}

// 正確做法：需要用 mutex 保護整個操作
std::mutex mtx;
int balance = 1000;

void withdraw_safe(int amount) {
    std::lock_guard<std::mutex> lock(mtx);
    if (balance >= amount) {           // 整個if-block是原子的
        balance -= amount;
    }
}
```

#### 2. **競爭條件 (Race Condition) 圖解**

```
時間軸問題：
T1: 執行緒A 檢查 balance(1000) >= 800  ✅
T2: 執行緒B 檢查 balance(1000) >= 500  ✅  
T3: 執行緒A 扣除 balance = 200         😱
T4: 執行緒B 扣除 balance = -300        💀 負數！

Atomic 只能保證：
- balance.load() 是原子的       ✅
- balance -= amount 是原子的    ✅
- 但兩個操作之間沒有連續性！     ❌

可視化：
Thread A: [檢查] ────gap────▶ [扣除]
Thread B:    [檢查] ──gap──▶ [扣除]  ← 在gap中插入！
```

#### 3. **ABA 問題 - Atomic 的經典陷阱**

```cpp
// ABA問題示例
std::atomic<Node*> head;

bool problematic_pop() {
    Node* old_head = head.load();           // A: 讀到節點A
    if (!old_head) return false;
    
    Node* new_head = old_head->next;
    
    // 😱 危險間隙：其他執行緒可能：
    // 1. pop了A節點  
    // 2. pop了B節點
    // 3. push了新的A節點（記憶體位址相同！）
    
    // 這個CAS會成功，但new_head可能指向已刪除的記憶體！
    return head.compare_exchange_weak(old_head, new_head);  // A又回來了！
}

// 解決方案：使用版本計數或hazard pointer
struct VersionedPointer {
    Node* ptr;
    uint64_t version;
};
std::atomic<VersionedPointer> versioned_head;
```

#### 4. **複雜資料結構的問題**

```cpp
// ❌ Vector 的 push_back 為什麼不能用 atomic？
class BadAtomicVector {
    std::atomic<size_t> size_{0};
    std::atomic<int*> data_{nullptr};
    std::atomic<size_t> capacity_{0};
    
public:
    void push_back(int value) {
        // 這需要多個步驟，無法原子化：
        // 1. 檢查容量
        // 2. 可能需要重新分配記憶體  
        // 3. 複製舊資料到新位置
        // 4. 新增元素
        // 5. 更新大小
        // 每一步都可能被其他執行緒打斷！
    }
};

// ✅ 正確做法：整個操作用 mutex 保護
class SafeVector {
    std::vector<int> data_;
    std::mutex mtx_;
    
public:
    void push_back(int value) {
        std::lock_guard<std::mutex> lock(mtx_);
        data_.push_back(value);  // 整個操作是原子的
    }
};
```

#### 5. **等待條件的問題**

```cpp
#include <atomic>
#include <iostream>

// ❌ 用 atomic 實現等待是低效的
std::atomic<bool> ready{false};
std::atomic<int> data{0};

void busy_wait_consumer() {
    // 這會100%佔用CPU！
    while (!ready.load()) {
        // 空轉等待 - 浪費CPU
    }
    std::cout << "Processed data: " << data.load() << std::endl;
}

// ✅ 正確做法：用 condition_variable
std::mutex mtx;
std::condition_variable cv;
bool ready = false;
int data = 0;

void efficient_consumer() {
    std::unique_lock<std::mutex> lock(mtx);
    cv.wait(lock, []{ return ready; });  // CPU休眠等待
    std::cout << "Efficiently processed data: " << data << std::endl;
}
```

#### 6. **記憶體順序的複雜性**

```cpp
// 在複雜場景中，記憶體順序很難控制正確
std::atomic<int> x{0}, y{0};
std::atomic<bool> flag1{false}, flag2{false};

// Thread 1
void complex_publish() {
    x.store(1, std::memory_order_relaxed);
    y.store(1, std::memory_order_relaxed);  
    flag1.store(true, std::memory_order_release);
    
    if (flag2.load(std::memory_order_acquire)) {
        // 複雜的依賴關係...
    }
}

// Thread 2  
void complex_subscribe() {
    flag2.store(true, std::memory_order_release);
    
    if (flag1.load(std::memory_order_acquire)) {
        // x和y的值可能不是預期的！
        // 記憶體順序在複雜場景中很難推理
    }
}

// 用mutex更簡單且安全：
std::mutex mtx;
int x = 0, y = 0;
bool flag1 = false, flag2 = false;

void simple_and_safe() {
    std::lock_guard<std::mutex> lock(mtx);
    // 所有操作都有明確的順序保證
    x = 1;
    y = 1;  
    flag1 = true;
}
```

#### 🎯 **總結：Atomic 的邊界**

```
Atomic 適合的場景 ✅:
┌───────────────────────────┐
│ • 簡單計數器              │
│ • 狀態標誌 (bool)         │
│ • 單一指標更新            │
│ • 統計資料累積            │
│ • 無鎖資料結構的基礎操作  │
└───────────────────────────┘

Atomic 不適合的場景 ❌:
┌──────────────────────────┐
│ • 複合條件判斷           │
│ • 多步驟業務邏輯         │
│ • 複雜資料結構操作       │
│ • 需要等待特定條件       │
│ • 多個變數的一致性更新   │
│ • 錯誤處理和回滾         │
└──────────────────────────┘

記住：Atomic = 原子性，但不等於事務性！
複雜同步需要更高層次的同步原語。
```

---

### 6. std::unique_lock vs std::lock_guard 🔧

**白話解釋**: 
- **lock_guard**: 像自動門，進去就自動鎖，出來就自動開
- **unique_lock**: 像手動門，可以自己控制什麼時候鎖、什麼時候開

```
功能對比圖：

lock_guard 🚪 (自動門):
{
  lock_guard<mutex> lg(mtx);  🔒自動鎖
  // 工作                    ⚙️
  // 無法手動控制             ❌
} 🔓自動解鎖

unique_lock 🎛️ (手動門):
{
  unique_lock<mutex> ul(mtx);   🔒自動鎖
  // 工作                      ⚙️
  ul.unlock();                 🔓手動解鎖
  // 其他工作 (不需要鎖)        ⚙️
  ul.lock();                   🔒再次鎖定
} 🔓自動解鎖

使用場景：
簡單保護     → lock_guard  ✅
需要手動控制  → unique_lock ✅
與條件變數配合 → unique_lock ✅ (必須)
```

**lock_guard**: 簡單的 RAII 鎖包裝器  
**unique_lock**: 更靈活，支援延遲鎖定、手動解鎖等

```cpp
#include <mutex>
#include <thread>
#include <iostream>
#include <chrono>

std::mutex mtx;
int shared_data = 0;

void use_lock_guard() {
    std::lock_guard<std::mutex> lock(mtx);
    shared_data++;
    std::cout << "lock_guard: " << shared_data << std::endl;
    // 自動在作用域結束時解鎖
}

void use_unique_lock() {
    std::unique_lock<std::mutex> lock(mtx);
    shared_data++;
    std::cout << "unique_lock (locked): " << shared_data << std::endl;
    
    // 可以手動解鎖
    lock.unlock();
    
    // 做其他事情 (不需要鎖)
    std::this_thread::sleep_for(std::chrono::milliseconds(10));
    
    lock.lock();  // 再次鎖定
    shared_data++;
    std::cout << "unique_lock (re-locked): " << shared_data << std::endl;
}

int main() {
    std::thread t1(use_lock_guard);
    std::thread t2(use_unique_lock);
    
    t1.join();
    t2.join();
    
    return 0;
}
```

---

## 🎯 鎖的選擇指南

### 白話選擇邏輯
1. **計數器簡單操作** → 用 `atomic`（像計算機按鍵）
2. **保護共享資料** → 用 `mutex`（像門鎖）
3. **很多人讀，少數人寫** → 用 `shared_mutex`（像圖書館）
4. **等待時間很短** → 用 `spinlock`（像敲門等待）
5. **需要等待條件** → 用 `condition_variable`（像等公車）
6. **控制人數** → 用 `semaphore`（像停車場管理）

### 📊 效能比較圖 (從快到慢)
```
性能排行榜：
🥇 atomic       ████████████████ (無鎖最快)
🥈 spinlock     ████████████░░░░ (短等待)
🥉 mutex        ████████░░░░░░░░ (標準選擇)
4️⃣ shared_mutex ██████░░░░░░░░░░ (讀寫場景)
5️⃣ semaphore    ████░░░░░░░░░░░░ (資源控制)

等待時間對選擇的影響：
⏱️ < 1μs   → atomic     🔥
⏱️ < 10μs  → spinlock   🌀  
⏱️ < 100μs → mutex      🔒
⏱️ > 100μs → condition  🚌
```

### 📋 使用時機總結

| 鎖類型 | 圖示 | 白話比喻 | 使用時機 | 優點 | 缺點 |
|--------|------|----------|----------|------|------|
| Mutex | 🔒 | 廁所門鎖 | 基本互斥存取 | 簡單易用 | 可能造成執行緒阻塞 |
| Spinlock | 🌀 | 敲門等待 | 短時間等待 | 低延遲 | CPU 佔用高 |
| Read-Write Lock | 📖 | 圖書館規則 | 多讀少寫 | 提高讀取併發 | 寫入時阻塞所有讀取 |
| Semaphore | 🚗 | 停車場管理 | 資源計數控制 | 靈活控制併發數 | 較複雜 |
| Condition Variable | 🚌 | 等公車 | 條件等待 | 高效的執行緒通訊 | 需要配合 mutex 使用 |
| Atomic | ⚛️ | 原子彈操作 | 簡單數值操作 | 無鎖高效能 | 僅適用於簡單操作 |

### 🛠️ 死鎖預防圖解

```
死鎖場景 💀:
Thread A: 🔒Lock1 ──▶ 等待Lock2 ──▶ 💀
Thread B: 🔒Lock2 ──▶ 等待Lock1 ──▶ 💀

預防方法 ✅:
1. 統一順序: 都先Lock1再Lock2
   Thread A: 🔒Lock1 → 🔒Lock2 ✅
   Thread B: 🔒Lock1 → 🔒Lock2 ✅

2. 超時機制: 
   Thread A: 🔒Lock1 → ⏰等待Lock2 → 🔓放棄 ✅

3. 避免嵌套:
   Single Lock: 🔒 → Work → 🔓 ✅
```

### 💡 最佳實踐
1. **優先考慮無鎖設計** (std::atomic) - 像用計算機而不是算盤 🧮→💻
2. **鎖的粒度要適中** - 不要鎖整棟樓🏢❌，也不要每個抽屜都上鎖🗄️❌
3. **避免死鎖** - 就像開車要遵守交通規則🚦，不要互相堵住
4. **使用 RAII** - 像自動門🚪一樣，進出自動管理
5. **考慮讀寫分離** - 像圖書館分開讀書區📖和寫字區✍️
6. **短時間臨界區用 spinlock** - 像快速過馬路🚶‍♂️不用等紅綠燈
7. **長時間等待用 condition_variable** - 像坐下來等公車🪑🚌而不是一直站著

### 🎓 學習路徑建議
```
初學者路線 🌱:
atomic → mutex → lock_guard → condition_variable

進階路線 🚀:
shared_mutex → spinlock → 無鎖程式設計

專家路線 🎯:
記憶體順序 → 自訂同步原語 → 高效能最佳化
```

---

## 🔚 總結

這份指南涵蓋了從 Linux 系統鎖到 C++ 標準庫的完整鎖機制，每種鎖都有其適用場景。記住這個核心原則：

> **選擇合適的工具解決對應的問題，簡單場景用簡單工具，複雜場景用複雜工具** 🎯

無論您是初學者還是經驗豐富的開發者，掌握這些同步機制都將幫助您寫出更安全、更高效的多執行緒程式！

---

## 📁 完整範例程式

本指南的所有程式碼範例都可以在 `locks_examples/` 目錄中找到完整的可編譯版本：

### 🔧 快速開始
```bash
cd locks_examples/
make          # 編譯所有範例
make test     # 編譯並測試所有範例
make help     # 查看詳細說明
```

### 📋 範例列表
- **Linux C 範例**: `01_pthread_mutex.c` 到 `05_condition_variable.c`
- **C++ 範例**: `06_std_mutex.cpp` 到 `12_lock_comparison.cpp`

每個範例都包含：
- ✅ 完整的可編譯程式碼
- ✅ 詳細的註解說明
- ✅ 實際運行結果展示
- ✅ 錯誤處理機制

更多詳細資訊請參考 `locks_examples/README.md`。
