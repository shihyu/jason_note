# Chapter 4:低延遲核心元件庫詳解

## 章節概述

本章實作了一套完整的低延遲應用程式基礎元件庫(Common Library),包含了五大核心模組:

1. **Lock-Free Queue**(無鎖佇列):單生產者單消費者(SPSC)的無鎖資料結構
2. **Memory Pool**(記憶體池):預先配置、零碎片化的記憶體管理器
3. **Zero-Allocation Logger**(零配置記錄器):非同步、無阻塞的日誌系統
4. **Thread Utilities**(執行緒工具):CPU 親和性綁定與執行緒管理
5. **Network Stack**(網路堆疊):TCP/UDP Socket 的低延遲封裝

這些元件是後續交易系統(Exchange)和策略引擎(Trading Engine)的基石,設計原則圍繞著:
- **預先配置(Pre-allocation)**:避免執行時記憶體分配
- **Cache 友善性(Cache-Friendliness)**:最大化 CPU Cache 命中率
- **無鎖同步(Lock-Free Synchronization)**:利用原子操作取代傳統鎖
- **零拷貝(Zero-Copy)**:減少不必要的記憶體複製

---

## 一、Lock-Free Queue(無鎖佇列)

### 📄 檔案位置
- `Chapter4/lf_queue.h`(第 12-67 行)

### 1.1 為什麼需要 Lock-Free Queue?

**傳統佇列的問題**:
```cpp
// 傳統實作:使用 std::queue + std::mutex
std::mutex mtx;
std::queue<T> q;

// 寫入資料
{
    std::lock_guard<std::mutex> lock(mtx);  // ⚠️ 阻塞其他執行緒
    q.push(data);
}

// 讀取資料
{
    std::lock_guard<std::mutex> lock(mtx);  // ⚠️ 阻塞其他執行緒
    auto data = q.front();
    q.pop();
}
```

**問題分析**:
- **鎖競爭(Lock Contention)**:多執行緒爭搶鎖時,會進入 kernel space 等待,延遲可達 **數千納秒**
- **優先權反轉(Priority Inversion)**:低優先權執行緒持有鎖時,高優先權執行緒被迫等待
- **不可預測性**:鎖的獲取時間無法保證

**Lock-Free 的優勢**:
- **永遠不阻塞**:使用 `std::atomic` 原子操作,不依賴作業系統排程
- **延遲可預測**:沒有 context switch,延遲穩定在 **數十納秒**
- **死鎖免疫**:無鎖機制根本不存在死鎖問題

### 1.2 SPSC Queue 的設計原理

**單生產者單消費者(Single Producer Single Consumer)限制**:
- 只有**一個執行緒**寫入(Producer)
- 只有**一個執行緒**讀取(Consumer)
- 這種限制讓我們能避免複雜的 CAS(Compare-And-Swap)循環

**核心數據結構**:
```cpp
template<typename T>
class LFQueue final {
private:
    std::vector<T> store_;                     // ⚡ Ring Buffer 底層儲存
    std::atomic<size_t> next_write_index_ = {0};  // 寫入索引(Producer 修改)
    std::atomic<size_t> next_read_index_ = {0};   // 讀取索引(Consumer 修改)
    std::atomic<size_t> num_elements_ = {0};      // 當前元素數量
};
```

**關鍵設計決策**:

| 設計選擇 | 理由 |
|---------|------|
| 使用 `std::vector` 而非 `std::array` | 允許執行時指定佇列大小,靈活性更高 |
| 預先配置所有元素 `store_(num_elems, T())` | 避免執行時記憶體分配,延遲穩定 |
| 三個 `std::atomic` 變數 | 確保 Producer/Consumer 之間的可見性(Visibility) |
| Ring Buffer(環形緩衝區)| 利用 `%` 運算實現索引環繞,空間利用率 100% |

### 1.3 Memory Ordering 分析

**為什麼需要 Memory Ordering?**

現代 CPU 會對記憶體操作重排序(Reordering)以提升效能,但這在多執行緒環境下可能導致資料競爭。例如:

```cpp
// Producer 執行緒
store_[next_write_index_] = data;  // 步驟 1:寫入資料
next_write_index_++;               // 步驟 2:更新索引

// CPU 可能重排序為:
next_write_index_++;               // 🚨 索引先更新
store_[next_write_index_] = data;  // 🚨 資料後寫入(Consumer 可能讀到舊資料!)
```

**當前實作的問題**:
```cpp
auto updateWriteIndex() noexcept {
    next_write_index_ = (next_write_index_ + 1) % store_.size();  // ⚠️ 預設 memory_order_seq_cst
    num_elements_++;
}
```

- 使用預設的 `std::memory_order_seq_cst`(順序一致性)
- 這是**最強**的記憶體順序保證,但也是**最慢**的(可能導致完整的記憶體屏障)

**優化方向**(後續章節會改進):
```cpp
// 優化後的版本(Chapter 10+)
auto updateWriteIndex() noexcept {
    // 使用 Release 語義:保證之前的寫入對 Consumer 可見
    next_write_index_.store((next_write_index_.load(std::memory_order_relaxed) + 1) % store_.size(),
                            std::memory_order_release);
    num_elements_.fetch_add(1, std::memory_order_relaxed);
}

auto getNextToRead() const noexcept -> const T* {
    // 使用 Acquire 語義:讀取時獲得最新的寫入結果
    return (num_elements_.load(std::memory_order_acquire) ?
            &store_[next_read_index_.load(std::memory_order_acquire)] : nullptr);
}
```

**Memory Order 對照表**:

| Memory Order | 保證 | 效能 | 使用場景 |
|--------------|------|------|---------|
| `memory_order_relaxed` | 無順序保證 | 最快 | 單純的計數器遞增 |
| `memory_order_acquire` | 讀取時獲得之前的寫入 | 中等 | Consumer 讀取資料 |
| `memory_order_release` | 寫入時保證之前的操作完成 | 中等 | Producer 發布資料 |
| `memory_order_seq_cst` | 全域順序一致性 | 最慢 | 預設值(安全但慢) |

### 1.4 ABA Problem(ABA 問題)

**什麼是 ABA 問題?**

在多執行緒環境下,一個執行緒讀取變數 A,接著另一個執行緒將 A 改成 B 再改回 A,第一個執行緒無法察覺變數曾經變化過。

**範例**:
```cpp
// 執行緒 1 讀取 next_write_index_ = 10
size_t old_index = next_write_index_.load();

// 執行緒 2 快速執行:
//   10 -> 11 -> ... -> (環繞一圈) -> 10
// 佇列被填滿又清空,索引回到 10

// 執行緒 1 以為沒變化,繼續執行
if (next_write_index_ == old_index) {
    // 🚨 誤判!佇列狀態已完全不同
}
```

**本實作為何不受 ABA 影響?**

1. **SPSC 限制**:只有一個 Producer 修改 `next_write_index_`,不存在多執行緒競爭
2. **不使用 CAS**:沒有 Compare-And-Swap 操作,不依賴「值相等」判斷
3. **單調遞增**:`num_elements_` 計數器作為額外的狀態檢查

**如果是 MPMC(多生產者多消費者)怎麼辦?**

需要使用版本標記(Versioning)或 Hazard Pointer 來解決 ABA 問題。例如:
```cpp
struct VersionedIndex {
    size_t index : 48;   // 索引佔 48 位元
    size_t version : 16; // 版本號佔 16 位元
};
std::atomic<VersionedIndex> next_write_index_;  // 每次修改時版本號 +1
```

### 1.5 Cache Line False Sharing

**問題**:
```cpp
struct LFQueue {
    std::atomic<size_t> next_write_index_;  // Producer 頻繁修改
    std::atomic<size_t> next_read_index_;   // Consumer 頻繁修改
    // 如果這兩個變數在同一個 Cache Line(64 bytes),會導致 Cache 乒乓效應
};
```

**解決方案**(後續章節採用):
```cpp
struct LFQueue {
    alignas(64) std::atomic<size_t> next_write_index_;  // 強制對齊到 Cache Line 邊界
    alignas(64) std::atomic<size_t> next_read_index_;
    alignas(64) std::atomic<size_t> num_elements_;
};
```

---

## 二、Memory Pool(記憶體池)

### 📄 檔案位置
- `Chapter4/mem_pool.h`(第 12-96 行)

### 2.1 為什麼需要自訂記憶體池?

**標準 `new`/`delete` 的問題**:

```cpp
// 交易系統中頻繁執行
for (int i = 0; i < 1000000; i++) {
    Order* order = new Order();  // ⚠️ 呼叫 malloc/brk 系統呼叫
    process(order);
    delete order;                // ⚠️ 呼叫 free,觸發記憶體合併
}
```

**效能瓶頸**:
1. **系統呼叫開銷**:每次 `new` 可能觸發 `brk()`/`mmap()`,進入 kernel space(~1000ns)
2. **記憶體碎片化**:頻繁分配/釋放導致堆積記憶體碎片化,降低 Cache 效率
3. **不可預測性**:記憶體分配時間不穩定(worst case 可能數微秒)
4. **競爭**:多執行緒同時 `malloc` 時需要全域鎖

**Memory Pool 的優勢**:
- **O(1) 時間複雜度**:分配/釋放操作都是常數時間
- **零碎片化**:所有物件大小相同,記憶體連續
- **Cache 友善**:物件在記憶體中緊密排列
- **延遲可預測**:沒有系統呼叫,延遲穩定在 **10-20ns**

### 2.2 ObjectBlock 設計

**核心資料結構**:
```cpp
struct ObjectBlock {
    T object_;              // ⚡ 實際物件(必須是第一個成員)
    bool is_free_ = true;   // 空閒標記
};
std::vector<ObjectBlock> store_;  // 預先配置的物件陣列
```

**為什麼 `object_` 必須是第一個成員?**

```cpp
// 建構函式中的斷言
ASSERT(reinterpret_cast<const ObjectBlock*>(&(store_[0].object_)) == &(store_[0]),
       "T object should be first member of ObjectBlock.");
```

**原因**:實現 **指標反向查詢**(Pointer Backtracking)

```cpp
// 用戶拿到 T* 指標後,要釋放記憶體
auto deallocate(const T* elem) noexcept {
    // 🔍 透過指標轉型找到所屬的 ObjectBlock
    const auto elem_index = (reinterpret_cast<const ObjectBlock*>(elem) - &store_[0]);
    store_[elem_index].is_free_ = true;
}
```

**記憶體佈局**:
```
假設 sizeof(T) = 16 bytes, sizeof(bool) = 1 byte(對齊後 = 8 bytes)

store_[0]: [T object (16B)][bool is_free (8B)] = 24 bytes
store_[1]: [T object (16B)][bool is_free (8B)] = 24 bytes
store_[2]: [T object (16B)][bool is_free (8B)] = 24 bytes

如果 bool 在前面,指標轉型會失效!
```

### 2.3 Placement New 技術

**什麼是 Placement New?**

```cpp
T* allocate(Args... args) noexcept {
    auto obj_block = &(store_[next_free_index_]);
    T* ret = &(obj_block->object_);
    ret = new (ret) T(args...);  // ⚡ Placement New:在指定記憶體位置呼叫建構子
    obj_block->is_free_ = false;
    return ret;
}
```

**與普通 `new` 的差異**:

| 操作 | 普通 `new` | Placement New |
|------|-----------|--------------|
| 記憶體分配 | 呼叫 `operator new`(可能觸發 malloc) | **不分配**記憶體,使用既有記憶體 |
| 建構子呼叫 | 自動呼叫 | 自動呼叫 |
| 語法 | `T* p = new T(args);` | `T* p = new (addr) T(args);` |

**為什麼需要 Placement New?**

```cpp
// 初始化時已配置所有記憶體
MemPool(std::size_t num_elems) : store_(num_elems, {T(), true}) {
    // store_ 中的 T 物件已經被**預設建構**
}

// 用戶請求新物件時,需要重新初始化
T* allocate(Args... args) {
    // 🚨 如果直接返回 &(store_[i].object_),物件狀態可能是髒的
    // ✅ 使用 Placement New 重新呼叫建構子,確保物件乾淨
    return new (&(store_[i].object_)) T(args...);
}
```

**生命週期管理**:
```cpp
// 分配時:Placement New 呼叫建構子
T* obj = pool.allocate(arg1, arg2);

// 釋放時:需要手動呼叫解構子(本實作未呼叫,假設 T 沒有資源需要釋放)
pool.deallocate(obj);  // ⚠️ 只標記 is_free = true,未呼叫 ~T()

// ⚠️ 如果 T 持有資源(如 std::string),必須手動呼叫解構子
obj->~T();  // 明確呼叫解構子
pool.deallocate(obj);
```

### 2.4 Next Free Index 更新策略

**線性探測法(Linear Probing)**:
```cpp
auto updateNextFreeIndex() noexcept {
    const auto initial_free_index = next_free_index_;

    while (!store_[next_free_index_].is_free_) {  // 找到第一個空閒槽
        ++next_free_index_;

        if (UNLIKELY(next_free_index_ == store_.size())) {
            next_free_index_ = 0;  // 環繞回起點
        }

        if (UNLIKELY(initial_free_index == next_free_index_)) {
            ASSERT(false, "Memory Pool out of space.");  // ⚠️ 記憶體池耗盡
        }
    }
}
```

**時間複雜度分析**:
- **最佳情況(Best Case)**:`O(1)` — 下一個位置恰好是空閒的
- **最壞情況(Worst Case)**:`O(N)` — 記憶體池幾乎滿了,需要掃描整個陣列

**為什麼不使用 Free List(空閒鏈結串列)?**

```cpp
// 替代方案:Free List
struct ObjectBlock {
    union {
        T object_;
        ObjectBlock* next_free_;  // 空閒時指向下一個空閒節點
    };
};
```

**Free List 的優勢**:
- 分配時間固定 `O(1)`,直接從 `free_list_head_` 取節點

**Free List 的劣勢**:
- **記憶體佈局散亂**:釋放順序不同會導致 Free List 節點跳躍,Cache 命中率低
- **複雜度高**:需要維護鏈結串列的完整性

**當前實作的權衡**:
- 假設記憶體池**不會長時間接近滿載**
- 大部分情況下 `next_free_index_` 直接命中
- 簡化程式碼,減少錯誤

### 2.5 Cache 友善性分析

**連續記憶體佈局**:
```cpp
std::vector<ObjectBlock> store_;  // 物件在記憶體中緊密排列
```

**Cache Line 利用率**:
```
假設 Cache Line = 64 bytes,sizeof(ObjectBlock) = 24 bytes

一個 Cache Line 可容納:64 / 24 = 2.67 個 ObjectBlock

當掃描 next_free_index_ 時:
- 第一次 Cache Miss 載入 store_[0]、store_[1]、store_[2]
- 後續存取 store_[1]、store_[2] 都是 Cache Hit(已在 L1 Cache 中)
```

**與 std::vector 比較**:

| 比較項目 | Memory Pool | `std::vector<T*>` |
|---------|------------|------------------|
| 記憶體佈局 | 連續 | 指標陣列,物件散落在堆積中 |
| Cache 命中率 | 高(物件緊鄰) | 低(每次解引用都可能 Cache Miss) |
| 分配速度 | O(1)~O(N) | O(1)(但可能觸發 malloc) |
| 碎片化 | 零碎片 | 可能嚴重碎片化 |

---

## 三、Zero-Allocation Logger(零配置記錄器)

### 📄 檔案位置
- `Chapter4/logging.h`(第 14-250 行)

### 3.1 低延遲記錄器的挑戰

**傳統 Logger 的問題**:
```cpp
// 典型的同步 Logger
void log(const std::string& msg) {
    std::lock_guard<std::mutex> lock(mtx);  // ⚠️ 鎖競爭
    std::ofstream file("log.txt", std::ios::app);  // ⚠️ 系統呼叫
    file << msg;  // ⚠️ I/O 阻塞
    file.close();
}
```

**效能問題**:
- **I/O 阻塞**:寫入磁碟可能耗時 **數毫秒**(HDD)或 **數百微秒**(SSD)
- **記憶體分配**:`std::string` 動態分配記憶體
- **鎖競爭**:多執行緒同時記錄時爭搶鎖

**對交易系統的影響**:
```cpp
// 關鍵路徑(Hot Path)中的 Log
void onMarketData(const MarketData& md) {
    auto t1 = now();
    process(md);
    log("Processed order in % ns", now() - t1);  // ⚠️ 如果 log() 耗時 10μs,系統延遲暴增
}
```

### 3.2 非同步設計架構

**核心思想**:將記錄操作分為兩階段

```
┌─────────────────┐         ┌──────────────────┐
│  業務執行緒      │ pushValue│ Lock-Free Queue  │
│  (Producer)     │────────→│  (8MB Buffer)    │
└─────────────────┘         └──────────────────┘
                                       │
                                       │ getNextToRead()
                                       ↓
                           ┌──────────────────┐
                           │  Logger 執行緒    │
                           │  (Consumer)      │
                           │  flushQueue()    │
                           └──────────────────┘
                                       │
                                       ↓
                                  寫入檔案
```

**流程說明**:
1. **業務執行緒(Hot Path)**:
   - 只負責將資料 `pushValue()` 到 Lock-Free Queue
   - 耗時 **10-20 納秒**(純記憶體操作)
   - **不阻塞**,立即返回

2. **Logger 執行緒(Background)**:
   - 每 10ms 檢查一次佇列
   - 批次處理所有待寫入資料
   - 寫入檔案後執行 `flush()`

### 3.3 LogElement 設計:避免記憶體分配

**問題:如何記錄不同型別的資料?**

傳統做法:
```cpp
template<typename T>
void log(const T& value) {
    std::string str = std::to_string(value);  // ⚠️ 動態分配記憶體
    queue.push(str);  // ⚠️ 複製字串
}
```

**本實作:使用 Tagged Union**

```cpp
enum class LogType : int8_t {
    CHAR, INTEGER, LONG_INTEGER, FLOAT, DOUBLE, ...
};

struct LogElement {
    LogType type_;  // 型別標籤(1 byte)
    union {         // 共用體(只佔用最大成員的空間)
        char c;
        int i;
        long l;
        long long ll;
        float f;
        double d;
    } u_;
};
```

**記憶體佈局**:
```
sizeof(LogElement) = 1 (type_) + 8 (union) + 7 (padding) = 16 bytes

// 8MB Queue 可容納:
8 * 1024 * 1024 / 16 = 524,288 個 LogElement
```

**優勢**:
- **固定大小**:不使用 `std::string`,避免堆積分配
- **記憶體高效**:Union 讓所有型別共用 8 bytes
- **Cache 友善**:LogElement 緊密排列在 Lock-Free Queue 中

### 3.4 printf-Style 格式化

**可變參數模板(Variadic Template)遞迴展開**:

```cpp
template<typename T, typename... A>
auto log(const char* s, const T& value, A... args) noexcept {
    while (*s) {
        if (*s == '%') {
            if (UNLIKELY(*(s + 1) == '%')) {  // %% -> % 逃逸字元
                ++s;
            } else {
                pushValue(value);  // 替換第一個 %
                log(s + 1, args...);  // ⚡ 遞迴處理剩餘參數
                return;
            }
        }
        pushValue(*s++);  // 逐字元寫入
    }
    FATAL("extra arguments provided to log()");
}
```

**編譯期展開範例**:
```cpp
logger.log("Order % filled % shares at price %", order_id, quantity, price);

// 編譯器遞迴展開為:
log("Order % filled % shares at price %", 12345, 100, 50.25)
  → pushValue('O'), pushValue('r'), ..., pushValue(12345)
  → log(" filled % shares at price %", 100, 50.25)
    → pushValue(' '), ..., pushValue(100)
    → log(" shares at price %", 50.25)
      → pushValue(' '), ..., pushValue(50.25)
      → log("", ) → 返回
```

**為什麼不用 `std::format`(C++20)?**

```cpp
// C++20 std::format
std::string msg = std::format("Value: {}", value);  // ⚠️ 動態分配字串
```

- `std::format` 回傳 `std::string`,會觸發堆積分配
- 本實作的目標是**零配置**,所有資料直接寫入 Lock-Free Queue

### 3.5 刷新策略(Flush Strategy)

**背景執行緒的主迴圈**:
```cpp
auto flushQueue() noexcept {
    while (running_) {
        for (auto next = queue_.getNextToRead();
             queue_.size() && next;
             next = queue_.getNextToRead()) {

            // 根據 LogType 寫入對應資料
            switch (next->type_) {
                case LogType::INTEGER:
                    file_ << next->u_.i;  // ⚡ 寫入檔案緩衝區(不立即 flush)
                    break;
                // ... 其他型別
            }
            queue_.updateReadIndex();
        }

        file_.flush();  // ⚡ 每 10ms 批次寫入磁碟
        std::this_thread::sleep_for(10ms);
    }
}
```

**為什麼每 10ms 刷新一次?**

| 刷新頻率 | 優點 | 缺點 |
|---------|------|------|
| 每次寫入都 `flush()` | 資料不會遺失 | I/O 開銷巨大(~100μs/次) |
| 每 10ms 刷新 | 批次處理,減少 I/O 次數 | 程式崩潰時可能遺失 10ms 的 Log |
| 從不 `flush()` | 最快 | 程式崩潰時遺失所有未寫入的 Log |

**交易系統的考量**:
- **可接受資料遺失**:10ms 的 Log 資料遺失是可容忍的(相比系統崩潰本身)
- **優先保證延遲**:寧可遺失 Log,也不能讓 Logger 拖慢業務執行緒

### 3.6 解構時的優雅關閉

**問題:如何確保所有 Log 都寫入?**

```cpp
~Logger() {
    // 1. 等待佇列清空
    while (queue_.size()) {
        std::this_thread::sleep_for(1s);  // ⚠️ 最多等待數秒
    }

    // 2. 停止背景執行緒
    running_ = false;
    logger_thread_->join();  // 等待執行緒結束

    // 3. 關閉檔案
    file_.close();
}
```

**為什麼不使用條件變數(Condition Variable)?**

```cpp
// 更高效的做法(本實作未採用)
std::condition_variable cv;

void flushQueue() {
    while (running_) {
        std::unique_lock<std::mutex> lock(mtx);
        cv.wait(lock, [this]{ return queue_.size() > 0 || !running_; });
        // 處理佇列
    }
}

void pushValue(...) {
    queue_.push(...);
    cv.notify_one();  // 喚醒 Logger 執行緒
}
```

**本實作的權衡**:
- **簡單性優先**:避免引入 Mutex 和條件變數
- **延遲容忍**:10ms 的輪詢延遲是可接受的
- **避免競爭**:不引入鎖機制,保持 Lock-Free 特性

---

## 四、Thread Utilities(執行緒工具)

### 📄 檔案位置
- `Chapter4/thread_utils.h`(第 12-48 行)

### 4.1 CPU Affinity(CPU 親和性)

**什麼是 CPU Affinity?**

預設情況下,作業系統會動態分配執行緒到不同 CPU 核心:
```
時間 0ms: 執行緒運行在 CPU 0
時間 5ms: OS 排程器將執行緒移到 CPU 2
時間 10ms: 執行緒再次移到 CPU 1
```

**問題:Cache 冷啟動(Cold Cache)**
```
CPU 0 的 L1/L2 Cache: [執行緒的工作資料]
                        ↓ 執行緒遷移
CPU 2 的 L1/L2 Cache: [空的]
                        ↓ 重新載入資料(Cache Miss)
                        ↓ 延遲 +50-200ns
```

**CPU Affinity 解決方案**:
```cpp
inline auto setThreadCore(int core_id) noexcept {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);            // 清空 CPU 集合
    CPU_SET(core_id, &cpuset);    // 加入目標 CPU

    // ⚡ 綁定當前執行緒到指定 CPU
    return (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0);
}
```

**效果**:
- 執行緒**永遠**運行在 `core_id` 上
- L1/L2 Cache 保持熱態(Hot Cache)
- 延遲降低 **20-50ns**

### 4.2 NUMA 感知(NUMA-Awareness)

**NUMA 架構(Non-Uniform Memory Access)**:
```
┌─────────────┐    ┌─────────────┐
│   CPU 0-3   │    │   CPU 4-7   │
│   L1/L2/L3  │    │   L1/L2/L3  │
└──────┬──────┘    └──────┬──────┘
       │                  │
       ├────────┬─────────┤
       ↓        ↓         ↓
     RAM 0    RAM 1     RAM 2
     (Local) (Remote)  (Remote)
```

**記憶體存取延遲**:
| 存取型別 | 延遲 |
|---------|------|
| Local RAM(同 NUMA 節點) | ~80ns |
| Remote RAM(跨 NUMA 節點) | ~120ns |

**最佳化策略**:
```cpp
// 假設有 2 個 NUMA 節點,每節點 4 個 CPU

// ✅ 好的做法:將相關執行緒綁定到同一個 NUMA 節點
createAndStartThread(0, "MarketDataThread", func1);  // CPU 0(NUMA 0)
createAndStartThread(1, "OrderThread", func2);       // CPU 1(NUMA 0)
// 兩者共享 RAM 0,存取延遲低

// ❌ 壞的做法:
createAndStartThread(0, "MarketDataThread", func1);  // CPU 0(NUMA 0)
createAndStartThread(4, "OrderThread", func2);       // CPU 4(NUMA 1)
// OrderThread 可能需要存取 MarketDataThread 的資料,跨 NUMA 節點 +40ns
```

### 4.3 超執行緒(Hyper-Threading)考量

**實體核心 vs 邏輯核心**:
```
實體核心 0: 邏輯核心 0, 邏輯核心 8
實體核心 1: 邏輯核心 1, 邏輯核心 9
實體核心 2: 邏輯核心 2, 邏輯核心 10
```

**共享資源競爭**:
```cpp
// ❌ 壞的做法:將兩個關鍵執行緒綁定到同一實體核心的超執行緒上
createAndStartThread(0, "Thread1", func1);  // 邏輯核心 0
createAndStartThread(8, "Thread2", func2);  // 邏輯核心 8(實體核心 0)
// 兩者共享 L1/L2 Cache、執行單元,效能降低 30-50%

// ✅ 好的做法:使用不同的實體核心
createAndStartThread(0, "Thread1", func1);  // 實體核心 0
createAndStartThread(1, "Thread2", func2);  // 實體核心 1
```

**查詢 CPU 拓撲**:
```bash
# 查看實體核心與邏輯核心的對應關係
lscpu -e
# 或
cat /proc/cpuinfo | grep -E "processor|physical id|core id"
```

### 4.4 createAndStartThread() 詳解

**完整流程**:
```cpp
template<typename T, typename... A>
inline auto createAndStartThread(int core_id, const std::string& name,
                                 T&& func, A&&... args) noexcept {
    auto t = new std::thread([&]() {
        // 1. 設定 CPU Affinity
        if (core_id >= 0 && !setThreadCore(core_id)) {
            std::cerr << "Failed to set core affinity for " << name << std::endl;
            exit(EXIT_FAILURE);  // ⚠️ 失敗時終止程式(低延遲系統不允許配置失敗)
        }

        std::cerr << "Set core affinity for " << name << " to " << core_id << std::endl;

        // 2. 呼叫用戶提供的函式
        std::forward<T>(func)((std::forward<A>(args))...);  // ⚡ 完美轉發(Perfect Forwarding)
    });

    // 3. 等待 1 秒讓執行緒啟動
    std::this_thread::sleep_for(1s);  // ⚠️ 確保 CPU Affinity 生效

    return t;
}
```

**為什麼要等待 1 秒?**

- **確保 Affinity 生效**:`pthread_setaffinity_np` 是非同步操作
- **避免競爭條件**:主執行緒可能在子執行緒配置完成前繼續執行
- **穩定性優先**:1 秒延遲在系統啟動階段是可接受的

**完美轉發(Perfect Forwarding)**:
```cpp
// 範例 1:傳遞右值參考
createAndStartThread(0, "Thread", processData, std::move(large_object));
// large_object 會被移動(不複製)到 processData

// 範例 2:傳遞引用
createAndStartThread(1, "Thread", processQueue, std::ref(queue));
// queue 會以引用方式傳遞(不複製)
```

---

## 五、Time Utilities(時間工具)

### 📄 檔案位置
- `Chapter4/time_utils.h`(第 9-35 行)

### 5.1 高解析度時間戳

**為什麼不使用 `gettimeofday()`?**

```cpp
// 傳統做法
struct timeval tv;
gettimeofday(&tv, NULL);  // ⚠️ 系統呼叫,~500ns
```

**問題**:
- 需要進入 kernel space(Context Switch)
- 可能觸發 VDSO(Virtual Dynamic Shared Object),但仍有開銷

**本實作:使用 `std::chrono`**

```cpp
inline auto getCurrentNanos() noexcept {
    return std::chrono::duration_cast<std::chrono::nanoseconds>
           (std::chrono::system_clock::now().time_since_epoch()).count();
}
```

**底層實作(取決於編譯器和系統)**:
- **Linux**:通常映射到 `clock_gettime(CLOCK_REALTIME)`,利用 VDSO 避免系統呼叫
- **x86-64**:可能直接讀取 TSC(Time Stamp Counter),透過 `RDTSC` 指令(**~10ns**)

### 5.2 RDTSC 指令(後續章節採用)

**什麼是 RDTSC?**

```cpp
// Chapter 11/12 會採用的優化版本
inline uint64_t rdtsc() {
    uint32_t lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));  // ⚡ CPU 指令,~10ns
    return ((uint64_t)hi << 32) | lo;
}
```

**優勢**:
- **純 CPU 指令**:不涉及系統呼叫
- **極低延遲**:~10ns
- **適合微基準測試**:測量納秒級操作

**劣勢**:
- **不保證單調性**:不同 CPU 核心的 TSC 可能不同步(需要 `RDTSCP` 和 CPU Invariant TSC 支援)
- **頻率變化**:CPU 動態調頻會影響 TSC 計數(需要設定 `cpufreq` 為 `performance` 模式)
- **不是牆上時鐘**:需要額外校準才能轉換為絕對時間

### 5.3 時間轉換常數

**納秒(Nanosecond)階層**:
```cpp
typedef int64_t Nanos;

constexpr Nanos NANOS_TO_MICROS = 1000;       // 1微秒 = 1000納秒
constexpr Nanos MICROS_TO_MILLIS = 1000;      // 1毫秒 = 1000微秒
constexpr Nanos MILLIS_TO_SECS = 1000;        // 1秒 = 1000毫秒
constexpr Nanos NANOS_TO_MILLIS = 1000 * 1000;         // 1毫秒 = 1,000,000納秒
constexpr Nanos NANOS_TO_SECS = 1000 * 1000 * 1000;   // 1秒 = 1,000,000,000納秒
```

**使用範例**:
```cpp
auto start = getCurrentNanos();
processOrder(order);
auto end = getCurrentNanos();

auto latency_ns = end - start;
auto latency_us = latency_ns / NANOS_TO_MICROS;

logger.log("Order processed in % us", latency_us);
```

---

## 六、Socket Utilities(網路工具)

### 📄 檔案位置
- `Chapter4/socket_utils.h`(第 25-180 行)
- `Chapter4/tcp_socket.h`(第 13-60 行)
- `Chapter4/mcast_socket.h`(第 14-53 行)

### 6.1 非阻塞 I/O(Non-Blocking I/O)

**阻塞 vs 非阻塞**:

```cpp
// ❌ 阻塞模式(預設)
int fd = socket(AF_INET, SOCK_STREAM, 0);
char buffer[1024];
ssize_t n = recv(fd, buffer, sizeof(buffer), 0);  // ⚠️ 阻塞執行緒直到有資料

// ✅ 非阻塞模式
setNonBlocking(fd);
ssize_t n = recv(fd, buffer, sizeof(buffer), 0);  // 立即返回
if (n == -1 && errno == EAGAIN) {
    // 沒有資料可讀,繼續執行其他邏輯
}
```

**實作**:
```cpp
inline auto setNonBlocking(int fd) -> bool {
    const auto flags = fcntl(fd, F_GETFL, 0);  // 取得當前 flags
    if (flags & O_NONBLOCK) {
        return true;  // 已經是非阻塞
    }
    return (fcntl(fd, F_SETFL, flags | O_NONBLOCK) != -1);  // 加入 O_NONBLOCK flag
}
```

**為什麼低延遲系統需要非阻塞 I/O?**

| 模式 | 延遲 | CPU 利用率 | 適用場景 |
|------|------|-----------|---------|
| 阻塞 | 不可預測(可能數毫秒) | 低(執行緒休眠) | 低頻 I/O |
| 非阻塞 | 可控(~100ns) | 高(忙等待) | 高頻交易 |

### 6.2 Nagle 演算法禁用

**什麼是 Nagle 演算法?**

TCP 預設會**延遲發送小封包**,等待累積更多資料或收到 ACK 後再發送:

```cpp
// 未禁用 Nagle
send(fd, "A", 1, 0);  // 不立即發送
send(fd, "B", 1, 0);  // 不立即發送
send(fd, "C", 1, 0);  // 累積 "ABC" 後發送,或等待 200ms(Nagle Timeout)
```

**延遲**:
- 等待 ACK:**1 RTT**(Round-Trip Time,可能數毫秒)
- Nagle Timeout:**200ms**(最壞情況)

**禁用 Nagle**:
```cpp
inline auto disableNagle(int fd) -> bool {
    int one = 1;
    return (setsockopt(fd, IPPROTO_TCP, TCP_NODELAY, &one, sizeof(one)) != -1);
}
```

**效果**:
```cpp
send(fd, "A", 1, 0);  // 立即發送(~10μs,取決於網路卡排程)
```

**權衡**:
- **優點**:延遲降低到微秒級
- **缺點**:小封包數量增加,網路頻寬利用率降低

**適用場景**:
- 交易系統:每個訊息都必須立即發送(訂單、行情更新)
- 不適合大量小封包的情境(如聊天系統),會浪費頻寬

### 6.3 TCP 緩衝區大小

**預設緩衝區問題**:
```cpp
// Linux 預設 TCP 緩衝區
sysctl net.ipv4.tcp_rmem  # 讀取緩衝區:min=4KB, default=128KB, max=6MB
sysctl net.ipv4.tcp_wmem  # 寫入緩衝區:min=4KB, default=16KB, max=4MB
```

**問題**:
- **接收緩衝區不足**:高頻行情資料湧入時,128KB 可能在幾毫秒內填滿
- **發送緩衝區不足**:大量訂單同時送出時,16KB 可能導致 `EAGAIN` 錯誤

**本實作:64MB 緩衝區**

```cpp
constexpr size_t TCPBufferSize = 64 * 1024 * 1024;  // 64MB

struct TCPSocket {
    std::vector<char> outbound_data_;  // 應用層發送緩衝區
    std::vector<char> inbound_data_;   // 應用層接收緩衝區
};
```

**為什麼需要應用層緩衝區?**

```cpp
// 非阻塞 send() 可能無法一次發送完所有資料
auto sendAndRecv() noexcept -> bool {
    while (next_send_valid_index_ > 0) {
        ssize_t n = send(socket_fd_, outbound_data_.data(), next_send_valid_index_, 0);

        if (n == -1) {
            if (errno == EAGAIN || errno == EWOULDBLOCK) {
                break;  // Kernel 緩衝區滿了,下次再試
            }
            return false;  // 錯誤
        }

        // 移除已發送的資料
        next_send_valid_index_ -= n;
        memmove(outbound_data_.data(), outbound_data_.data() + n, next_send_valid_index_);
    }
}
```

### 6.4 UDP Multicast 配置

**什麼是 Multicast(組播)?**

```
發送方(Exchange)發送一次資料到 Multicast 組 239.0.0.1:12345
                  ↓
         ┌────────┼────────┐
         ↓        ↓        ↓
    訂閱者 A   訂閱者 B   訂閱者 C
    (所有訂閱者同時收到資料,無需多次發送)
```

**相比 Unicast 的優勢**:
```cpp
// Unicast(單播):Exchange 需要發送 N 次
for (auto& subscriber : subscribers) {
    send(subscriber.fd, data, len, 0);  // ⚠️ N 次 send()
}

// Multicast(組播):Exchange 只需發送 1 次
send(multicast_fd, data, len, 0);  // ⚡ 1 次 send(),交換器負責複製
```

**加入 Multicast 組**:
```cpp
inline auto join(int fd, const std::string& ip) -> bool {
    const ip_mreq mreq{
        {inet_addr(ip.c_str())},  // 組播 IP(239.0.0.1)
        {htonl(INADDR_ANY)}       // 任意本地介面
    };
    return (setsockopt(fd, IPPROTO_IP, IP_ADD_MEMBERSHIP, &mreq, sizeof(mreq)) != -1);
}
```

**UDP 不可靠性處理(Chapter 7 詳解)**:
- Multicast 使用 UDP,不保證封包送達
- 需要應用層 Sequence Number 檢測遺失
- 配合 TCP Snapshot 恢復遺失資料

### 6.5 SO_TIMESTAMP:軟體時間戳

**問題:何時記錄封包接收時間?**

```cpp
// ❌ 方案 1:應用層記錄
auto rx_time = getCurrentNanos();
recv(fd, buffer, len, 0);  // ⚠️ recv() 可能阻塞數微秒,時間戳不準確

// ❌ 方案 2:Kernel 記錄(預設未啟用)
recv(fd, buffer, len, 0);  // Kernel 丟棄時間戳
```

**✅ 方案 3:SO_TIMESTAMP(軟體時間戳)**

```cpp
inline auto setSOTimestamp(int fd) -> bool {
    int one = 1;
    return (setsockopt(fd, SOL_SOCKET, SO_TIMESTAMP, &one, sizeof(one)) != -1);
}

// 接收資料時,使用 recvmsg() 取得時間戳
struct msghdr msg;
recvmsg(fd, &msg, 0);

// 從 Control Message 中取出時間戳
for (struct cmsghdr *cmsg = CMSG_FIRSTHDR(&msg); cmsg; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
    if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SO_TIMESTAMP) {
        struct timeval *tv = (struct timeval *)CMSG_DATA(cmsg);
        auto rx_time = tv->tv_sec * NANOS_TO_SECS + tv->tv_usec * NANOS_TO_MICROS;
    }
}
```

**時間戳精度比較**:

| 方案 | 時間戳位置 | 精度 | 延遲誤差 |
|------|-----------|------|---------|
| 應用層 | `recv()` 返回後 | ±10μs | 受 Kernel 排程影響 |
| SO_TIMESTAMP | Kernel 收到封包時 | ±1μs | 軟體中斷延遲 |
| 硬體時間戳 | 網路卡收到封包時 | ±100ns | 需要支援 PTP 的網路卡(如 Intel X710) |

**後續章節優化(Chapter 11)**:
- 使用硬體時間戳(SO_TIMESTAMPING + PTP)
- 直接讀取網路卡的 DMA 緩衝區(Kernel Bypass,如 DPDK)

---

## 七、效能分析與基準測試

### 7.1 各元件延遲對比

| 元件 | 操作 | 延遲(納秒) | 參考基準 |
|------|------|------------|---------|
| **Lock-Free Queue** | `push()` | 10-20ns | 純記憶體操作 |
| **Memory Pool** | `allocate()` | 15-30ns | 取決於 `next_free_index_` 是否命中 |
| **Logger** | `log()` | 10-15ns | 只寫入 Queue,不 flush |
| **std::mutex** | `lock()`/`unlock()` | 20-100ns(無競爭)<br>1000-5000ns(有競爭) | Futex 系統呼叫 |
| **new/delete** | 堆積分配 | 50-200ns(無碎片)<br>500-2000ns(碎片化) | 取決於 glibc malloc 實作 |

### 7.2 為什麼 Chapter 4 沒有硬體優化?

**當前實作的不足**:
1. **Memory Ordering 過於保守**:所有 `std::atomic` 使用預設的 `seq_cst`
2. **Cache Line 對齊缺失**:Lock-Free Queue 的 `next_write_index_` 和 `next_read_index_` 可能在同一 Cache Line
3. **未使用 RDTSC**:時間戳記錄依賴 `std::chrono`(可能觸發 VDSO)
4. **網路未優化**:未啟用 SO_REUSEPORT、SO_BUSY_POLL 等低延遲 Socket 選項

**後續章節的優化**:
- **Chapter 10**:改進 Lock-Free Queue 的 Memory Ordering
- **Chapter 11**:CPU Affinity、NUMA、Huge Pages 配置
- **Chapter 12**:基準測試與效能調校

---

## 八、實戰應用場景

### 8.1 Lock-Free Queue 的使用

**適用場景**:
```cpp
// ✅ 單生產者單消費者(SPSC)
LFQueue<MarketData> market_data_queue(1024);

// Producer 執行緒
void onMarketUpdate(const MarketData& md) {
    *market_data_queue.getNextToWriteTo() = md;
    market_data_queue.updateWriteIndex();
}

// Consumer 執行緒
void processMarketData() {
    if (auto* md = market_data_queue.getNextToRead()) {
        process(*md);
        market_data_queue.updateReadIndex();
    }
}
```

**不適用場景**:
```cpp
// ❌ 多生產者(需要使用 MPSC Queue,如 Boost.Lockfree)
std::thread t1([&]{ market_data_queue.push(md1); });  // ⚠️ 競爭條件
std::thread t2([&]{ market_data_queue.push(md2); });
```

### 8.2 Memory Pool 的使用

**適用場景**:
```cpp
// ✅ 頻繁分配/釋放相同大小的物件
MemPool<Order> order_pool(10000);

void onNewOrder(const OrderRequest& req) {
    Order* order = order_pool.allocate(req.order_id, req.price, req.quantity);
    process(order);
    order_pool.deallocate(order);  // 快速回收
}
```

**不適用場景**:
```cpp
// ❌ 物件大小不一(Memory Pool 無法處理)
MemPool<void> pool(1000);  // ⚠️ void 無法實例化
auto* small_obj = pool.allocate(10);   // 10 bytes
auto* large_obj = pool.allocate(1000); // 1000 bytes(無法支援)
```

### 8.3 Logger 的使用

**適用場景**:
```cpp
// ✅ 熱路徑(Hot Path)中的記錄
void onOrderFilled(const Order& order) {
    auto t1 = getCurrentNanos();

    // 關鍵業務邏輯
    updatePositions(order);

    // ⚡ 非阻塞記錄,~10ns
    logger.log("Order % filled in % ns", order.id, getCurrentNanos() - t1);
}
```

**不適用場景**:
```cpp
// ❌ 需要立即寫入磁碟的情境(如交易確認)
logger.log("Trade confirmed: %", trade_id);  // ⚠️ 最多 10ms 後才寫入檔案
// 程式崩潰時可能遺失這條 Log
```

---

## 八之二、範例程式碼詳解

本章節提供 5 個完整的範例程式，展示如何在實際場景中使用 Chapter 4 的低延遲元件。每個範例都包含執行流程、預期輸出、效能分析和常見錯誤。

### 8.4 Lock-Free Queue 完整範例 (lf_queue_example.cpp)

**📄 檔案位置**: `Chapter4/lf_queue_example.cpp`

**範例目的**: 展示生產者-消費者模式的正確實作

**執行流程**:
```cpp
// 1. 建立容量為 20 的 Lock-Free Queue
LFQueue<MyStruct> lfq(20);

// 2. 啟動消費者執行緒(延遲 5 秒後開始消費)
auto ct = createAndStartThread(-1, "", consumeFunction, &lfq);

// 3. 主執行緒(生產者)每秒產生 1 筆資料
for (auto i = 0; i < 50; ++i) {
    const MyStruct d{i, i * 10, i * 100};

    // ⚡ 兩步驟寫入
    auto* write_ptr = lfq.getNextToWriteTo();  // 取得寫入位置
    *write_ptr = d;                             // 寫入資料
    lfq.updateWriteIndex();                     // 更新索引(Memory Barrier)

    std::this_thread::sleep_for(1s);
}
```

**消費者行為**:
```cpp
auto consumeFunction(LFQueue<MyStruct>* lfq) {
    std::this_thread::sleep_for(5s);  // 模擬啟動延遲

    while (lfq->size()) {
        // ⚡ 兩步驟讀取
        const auto d = lfq->getNextToRead();  // 取得讀取位置
        lfq->updateReadIndex();                // 更新索引(標記已讀)

        // 處理資料
        std::cout << "Read: " << d->d_[0] << std::endl;
        std::this_thread::sleep_for(1s);
    }
}
```

**時間軸分析**:
```
時間 0-5 秒:
  生產者產生: [0][1][2][3][4]
  消費者狀態: 休眠中
  佇列大小: 增加到 5

時間 5 秒後:
  生產者: 每秒產生 1 筆 → [5][6][7]...
  消費者: 每秒消費 1 筆 → 處理 [0][1][2]...
  佇列大小: 穩定在 5 左右

時間 50 秒後:
  生產者: 停止(已產生 50 筆)
  消費者: 繼續處理剩餘 5 筆
  佇列大小: 逐漸降至 0
```

**常見錯誤範例**:

❌ **錯誤 1: 忘記更新索引**
```cpp
auto* ptr = lfq.getNextToWriteTo();
*ptr = data;
// 忘記呼叫 updateWriteIndex()!
// 結果: 消費者永遠讀不到這筆資料
```

❌ **錯誤 2: 索引更新順序錯誤**
```cpp
lfq.updateWriteIndex();  // ❌ 先更新索引
*lfq.getNextToWriteTo() = data;  // ❌ 後寫入資料
// 結果: 消費者可能讀到未初始化的資料(Race Condition)
```

✅ **正確做法**:
```cpp
auto* ptr = lfq.getNextToWriteTo();
*ptr = data;  // 1. 先完成資料寫入
lfq.updateWriteIndex();  // 2. 再更新索引(Memory Barrier 保證順序)
```

**效能關鍵點**:
- 單次寫入延遲: **~10-20ns** (指標操作 + Memory Barrier)
- 單次讀取延遲: **~10-20ns**
- 零系統呼叫: 完全在用戶態完成
- Cache 友善: Ring Buffer 連續記憶體佈局

---

### 8.5 Logger 使用範例 (logging_example.cpp)

**📄 檔案位置**: `Chapter4/logging_example.cpp`

**範例目的**: 展示如何記錄不同型別的資料

**完整程式碼**:
```cpp
int main() {
    using namespace Common;

    // 準備測試資料
    char c = 'd';
    int i = 3;
    unsigned long ul = 65;
    float f = 3.4;
    double d = 34.56;
    const char* s = "test C-string";
    std::string ss = "test string";

    // 建立 Logger(啟動背景執行緒)
    Logger logger("logging_example.log");

    // 記錄不同型別(自動推導)
    logger.log("Logging a char:% an int:% and an unsigned:%\n", c, i, ul);
    logger.log("Logging a float:% and a double:%\n", f, d);
    logger.log("Logging a C-string:'%'\n", s);
    logger.log("Logging a string:'%'\n", ss);

    // 程式結束時自動 Flush
    return 0;
}
```

**預期輸出** (logging_example.log):
```
Logging a char:d an int:3 and an unsigned:65
Logging a float:3.4 and a double:34.56
Logging a C-string:'test C-string'
Logging a string:'test string'
```

**效能分析**:

| 操作型別 | 延遲 | 說明 |
|---------|------|------|
| 基本型別(int, char) | ~50ns | 僅記憶體複製 |
| 浮點數(float, double) | ~200ns | 需要格式化 |
| C-string | ~100-300ns | 視字串長度 |
| std::string | ~100-300ns | .data() + .size() |

**與 printf 比較**:

| 特性 | printf | Logger | 改善 |
|------|--------|--------|------|
| 記錄延遲 | ~1-2μs | ~50ns | **20-40x** |
| 多執行緒安全 | 需 mutex | Lock-Free | 無競爭 |
| 記憶體分配 | 動態 | 零分配 | 可預測 |
| I/O 阻塞 | 是 | 否 | 背景寫入 |

**背景執行緒行為**:
```
主執行緒:
  logger.log() → 寫入 Lock-Free Queue → 立即返回(~50ns)

背景執行緒:
  每 10ms 檢查佇列
  若有資料 → 批次寫入檔案(1 次 write() 寫入所有累積日誌)
  I/O 開銷 ~1-2ms,主執行緒不受影響
```

**常見陷阱**:

⚠️ **陷阱 1: 指標懸空**
```cpp
int local_var = 42;
logger.log("Value: %\n", &local_var);  // ❌ 背景執行緒讀取時 local_var 可能已銷毀
logger.log("Value: %\n", local_var);   // ✅ 複製值
```

⚠️ **陷阱 2: 字串過長**
```cpp
std::string huge_str(10000, 'x');  // 10KB 字串
logger.log("%\n", huge_str);  // ⚠️ 可能超過緩衝區大小被截斷
// 建議: 單筆日誌 < 1KB
```

⚠️ **陷阱 3: 佇列滿溢**
```cpp
// 高頻日誌(每秒 100 萬次)
for (int i = 0; i < 1000000; ++i) {
    logger.log("Tick %\n", i);  // ⚠️ 若背景寫入速度 < 生產速度,佇列會滿
}
// 解決: 增大 Queue 容量或降低日誌頻率
```

---

### 8.6 Memory Pool 使用範例 (mem_pool_example.cpp)

**📄 檔案位置**: `Chapter4/mem_pool_example.cpp`

**範例目的**: 展示記憶體重用機制

**完整程式碼**:
```cpp
int main() {
    using namespace Common;

    // 建立兩個 Memory Pool(各 50 個物件)
    MemPool<double> prim_pool(50);
    MemPool<MyStruct> struct_pool(50);

    for (auto i = 0; i < 50; ++i) {
        // O(1) 分配
        auto p_ret = prim_pool.allocate(i);
        auto s_ret = struct_pool.allocate(MyStruct{i, i+1, i+2});

        std::cout << "allocated at: " << p_ret << std::endl;

        // 每 5 個釋放一次(測試重用)
        if (i % 5 == 0) {
            prim_pool.deallocate(p_ret);
            struct_pool.deallocate(s_ret);
        }
    }

    return 0;
}
```

**記憶體佈局**:
```
初始化時:
  [obj0][obj1][obj2]...[obj49]  ← 連續記憶體
  Free List: 0→1→2→...→49→null

第 0 次分配:
  分配: obj0 (位址 0x1000)
  Free List: 1→2→...→49→null

第 0 次釋放:
  釋放: obj0
  Free List: 0→1→2→...→49→null  ← obj0 插入頭部

第 5 次分配:
  分配: obj0 (位址 0x1000)  ← 重用!
  Free List: 1→2→...→49→null
```

**預期輸出分析**:
```
allocated at: 0x1000  ← 第 0 次
allocated at: 0x1008  ← 第 1 次
allocated at: 0x1010  ← 第 2 次
...
allocated at: 0x1000  ← 第 5 次(重用第 0 次的位址)
allocated at: 0x1030  ← 第 6 次(新位址)
...
allocated at: 0x1008  ← 第 10 次(重用第 1 次的位址)
```

**觀察重點**:
- ✅ 記憶體位址循環出現(證明重用機制)
- ✅ 位址始終在初始分配範圍內(0x1000~0x1190)
- ✅ 無需向系統請求新記憶體

**效能對比**:

| 操作 | new/delete | MemPool | 加速比 |
|------|-----------|---------|--------|
| 分配 | ~100-500ns | ~10-20ns | **5-50x** |
| 釋放 | ~50-200ns | ~5-10ns | **5-40x** |
| 碎片化 | 嚴重 | 零碎片 | - |
| 缺頁中斷 | 可能 | 不會 | - |

**容量規劃公式**:
```cpp
Pool 大小 = (峰值併發數) × 1.2  // 20% 緩衝

// 範例: 峰值有 1000 個活躍 Order
MemPool<Order> order_pool(1200);
```

**常見陷阱**:

❌ **陷阱 1: Pool 容量不足**
```cpp
MemPool<Order> pool(10);  // 只能容納 10 個
for (int i = 0; i < 20; ++i) {
    auto* obj = pool.allocate();  // 第 11 個會失敗,返回 nullptr
    // ⚠️ 未檢查返回值會導致 Segfault
}

// ✅ 正確做法:
if (auto* obj = pool.allocate(); obj != nullptr) {
    // 使用 obj
} else {
    // 處理容量不足
}
```

❌ **陷阱 2: 重複釋放(Double Free)**
```cpp
auto* obj = pool.allocate();
pool.deallocate(obj);
pool.deallocate(obj);  // ❌ 破壞 Free List 結構,未定義行為
```

❌ **陷阱 3: 釋放錯誤的指標**
```cpp
auto* obj = new Order();
pool.deallocate(obj);  // ❌ obj 不是從 pool 分配的
```

---

### 8.7 TCP Socket 完整範例 (socket_example.cpp)

**📄 檔案位置**: `Chapter4/socket_example.cpp`

**範例目的**: 展示客戶端-伺服器通訊與 Epoll 事件循環

**系統架構**:
```
┌─────────────┐                    ┌─────────────┐
│ TCPServer   │                    │ TCPSocket   │
│ (127.0.0.1: │◄───────────────────┤ Client 0    │
│  12345)     │  connect()         └─────────────┘
│             │                    ┌─────────────┐
│ Epoll       │◄───────────────────┤ Client 1    │
│ 事件循環    │                    └─────────────┘
│             │                           ...
│             │                    ┌─────────────┐
│             │◄───────────────────┤ Client 4    │
└─────────────┘                    └─────────────┘
```

**執行流程**:

**階段 1: 初始化**
```cpp
// 1. 建立伺服器
TCPServer server(logger_);
server.recv_callback_ = tcpServerRecvCallback;  // 設定回調
server.listen("lo", 12345);  // 監聽 127.0.0.1:12345

// 2. 建立 5 個客戶端連線
for (size_t i = 0; i < 5; ++i) {
    clients[i] = new TCPSocket(logger_);
    clients[i]->connect("127.0.0.1", "lo", 12345, false);
    server.poll();  // ⚡ 關鍵: 觸發 accept()
}
```

**階段 2: 訊息交換**
```cpp
for (auto itr = 0; itr < 5; ++itr) {           // 5 輪
    for (size_t i = 0; i < 5; ++i) {           // 5 個客戶端
        // 客戶端發送訊息
        std::string msg = "CLIENT-[" + std::to_string(i) + "]";
        clients[i]->send(msg.data(), msg.length());  // 累積到緩衝區
        clients[i]->sendAndRecv();  // 批次發送 + 接收

        std::this_thread::sleep_for(500ms);

        // 伺服器處理事件
        server.poll();        // epoll_wait() → EPOLLIN 事件 → recv_callback_
        server.sendAndRecv(); // 批次發送回應
    }
}
// 總共: 5 輪 × 5 客戶端 = 25 筆訊息
```

**Epoll 事件流程**:
```
1. clients[0]->sendAndRecv()
   └─→ send() 發送資料到核心緩衝區

2. server.poll()
   └─→ epoll_wait() 檢測到 clients[0] 的 EPOLLIN 事件
       └─→ recv() 讀取資料
           └─→ 觸發 tcpServerRecvCallback
               └─→ socket->send(reply)  // 累積回應到緩衝區

3. server.sendAndRecv()
   └─→ send() 批次發送所有回應
```

**回調函數範例**:
```cpp
// 伺服器接收回調
auto tcpServerRecvCallback = [&](TCPSocket* socket, Nanos rx_time) {
    // 1. 讀取客戶端訊息
    std::string msg(socket->inbound_data_.data(), socket->next_rcv_valid_index_);
    socket->next_rcv_valid_index_ = 0;  // 重置緩衝區

    // 2. 建立回應(Echo Server)
    std::string reply = "Server received: " + msg;

    // 3. 累積回應到發送緩衝區(不立即發送)
    socket->send(reply.data(), reply.length());
};

// 客戶端接收回調
auto tcpClientRecvCallback = [&](TCPSocket* socket, Nanos rx_time) {
    std::string msg(socket->inbound_data_.data(), socket->next_rcv_valid_index_);
    socket->next_rcv_valid_index_ = 0;

    std::cout << "Client received: " << msg << " (rx_time: " << rx_time << "ns)" << std::endl;
};
```

**預期輸出**:
```
Creating TCPServer on iface:lo port:12345
Connecting TCPClient-[0] ...
Connecting TCPClient-[1] ...
...
Sending TCPClient-[0] CLIENT-[0] : Sending 0
TCPServer::defaultRecvCallback() socket:5 len:28 rx:1234567890
TCPSocket::defaultRecvCallback() ... msg:Server received: CLIENT-[0] : Sending 0
...
(重複 25 次)
```

**效能分析**:

| 操作 | 延遲 | 說明 |
|------|------|------|
| sendAndRecv() | ~1-2μs | 無資料時(系統呼叫開銷) |
| sendAndRecv() | ~5-10μs | 有資料時(含複製) |
| poll() | ~1-2μs | 無事件時(立即返回) |
| poll() | ~5-20μs | 有事件時(視連線數) |
| Loopback RTT | ~10-50μs | 本地迴環 |

**常見陷阱**:

⚠️ **陷阱 1: 忘記呼叫 poll()**
```cpp
clients[i]->sendAndRecv();  // 客戶端發送
// ❌ 忘記 server.poll(),伺服器不會處理!
server.sendAndRecv();  // 無法發送回應(因為沒接收到資料)

// ✅ 正確順序:
clients[i]->sendAndRecv();
server.poll();         // 處理接收事件
server.sendAndRecv();  // 發送回應
```

⚠️ **陷阱 2: 回調中執行耗時操作**
```cpp
auto callback = [](TCPSocket* socket, Nanos rx_time) {
    // ❌ 阻塞事件循環
    query_database();  // 可能耗時數毫秒
    process_complex_logic();
};

// ✅ 正確做法: 放入工作佇列
auto callback = [](TCPSocket* socket, Nanos rx_time) {
    work_queue.push(socket->inbound_data_);  // 快速返回
};
```

**進階優化**:
1. **SO_REUSEPORT**: 多執行緒監聽同一埠
2. **TCP_QUICKACK**: 禁用延遲 ACK(降低 ~40ms 延遲)
3. **CPU Affinity**: 綁定執行緒到特定核心

---

### 8.8 Thread CPU Affinity 範例 (thread_example.cpp)

**📄 檔案位置**: `Chapter4/thread_example.cpp`

**範例目的**: 展示 CPU 核心綁定技術

**完整程式碼**:
```cpp
int main() {
    using namespace Common;

    // 執行緒 1: 不綁定核心(作業系統自由排程)
    auto t1 = createAndStartThread(-1, "dummyFunction1",
                                   dummyFunction, 12, 21, false);

    // 執行緒 2: 綁定到 CPU 核心 1
    auto t2 = createAndStartThread(1, "dummyFunction2",
                                   dummyFunction, 15, 51, true);

    // 等待執行緒完成
    t1->join();
    t2->join();

    return 0;
}
```

**CPU Affinity 原理**:
```cpp
// 底層實作(pthread_setaffinity_np)
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(1, &cpuset);  // 允許在核心 1 執行
pthread_setaffinity_np(thread.native_handle(), sizeof(cpuset), &cpuset);
```

**預期行為**:

| 執行緒 | CPU 綁定 | PSR (Last Used CPU) | 行為 |
|-------|---------|---------------------|------|
| t1 | 無(-1) | 0, 1, 2, 3, ... | 可能在核心間移動 |
| t2 | 核心 1 | 1, 1, 1, 1, ... | 固定在核心 1 |

**驗證方法**:
```bash
# 執行程式
./thread_example &
PID=$!

# 查看執行緒在哪個核心執行
ps -o pid,tid,psr,comm -p $PID
# PSR 欄位: 當前 CPU 核心編號

# 或使用 top
top -H -p $PID  # 按 'f' 選擇 P (Last Used CPU)
```

**Context Switch 開銷分析**:

| 成本類型 | 延遲 | 說明 |
|---------|------|------|
| 直接成本 | ~1-5μs | 保存/恢復暫存器、切換頁表 |
| 間接成本 | ~10-100μs | L1/L2 Cache Miss |

**CPU Affinity 效能提升**:

| 場景 | 無綁定 | 綁定核心 | 改善 |
|------|--------|----------|------|
| 高頻熱路徑(每秒 100 萬次) | ~50ns | ~20ns | **2.5x** |
| Cache Miss 率 | ~10% | ~1% | **10x** |
| 延遲 Jitter (P99) | ~500ns | ~50ns | **10x** |

**NUMA 系統考量**:
```bash
# 檢查 NUMA 拓撲
numactl --hardware
# 輸出:
# node 0 cpus: 0 2 4 6 8 10
# node 1 cpus: 1 3 5 7 9 11
```

```cpp
// ✅ 正確: 記憶體在 Node 0,執行緒綁定到 Node 0 的核心
void* data = numa_alloc_onnode(size, 0);  // 分配在 Node 0
createAndStartThread(0, "worker", process, data);  // 綁定核心 0(Node 0)

// ❌ 錯誤: 跨 NUMA Node 存取(延遲 2-3x)
void* data = numa_alloc_onnode(size, 0);  // 分配在 Node 0
createAndStartThread(1, "worker", process, data);  // 綁定核心 1(Node 1)
```

**適合綁定核心的執行緒**:
- ✅ 撮合引擎執行緒(交易系統)
- ✅ 網路接收執行緒(高頻交易)
- ✅ 渲染執行緒(遊戲引擎)
- ✅ 控制迴路執行緒(即時系統)

**不應該綁定核心的執行緒**:
- ❌ 日誌執行緒(不頻繁執行)
- ❌ 監控執行緒(低優先級)
- ❌ 背景清理執行緒
- ❌ 短暫存在的工作執行緒

**進階優化: 核心隔離**
```bash
# 開機參數: 保留核心 1-3 給應用程式
# 編輯 /etc/default/grub
GRUB_CMDLINE_LINUX="isolcpus=1,2,3 nohz_full=1,2,3"

# 效果: 作業系統不會在這些核心上排程其他行程
```

**進階優化: 中斷親和性**
```bash
# 將網卡中斷路由到核心 0,避免干擾核心 1
IRQ=$(cat /proc/interrupts | grep eth0 | cut -d: -f1)
echo 1 > /proc/irq/$IRQ/smp_affinity  # Bitmask: 0x1 = 核心 0
```

---

## 九、與標準庫的比較

### 9.1 Lock-Free Queue vs std::queue

| 比較項目 | LFQueue | std::queue + std::mutex |
|---------|---------|------------------------|
| 延遲 | 10-20ns | 20-5000ns(取決於競爭) |
| 執行緒安全 | ✅(SPSC) | ✅(需手動加鎖) |
| 記憶體配置 | 預先配置 | 動態增長(可能觸發 realloc) |
| Cache 友善性 | 高(Ring Buffer) | 低(std::deque 實作) |
| 複雜度 | 中等 | 低 |

### 9.2 Memory Pool vs std::allocator

| 比較項目 | MemPool | std::allocator |
|---------|---------|---------------|
| 分配速度 | O(1)~O(N) | O(1)(可能觸發 brk) |
| 碎片化 | 零碎片 | 可能碎片化 |
| 執行緒安全 | ❌(需外部同步) | ✅(glibc malloc 有全域鎖) |
| 記憶體利用率 | 固定大小,可能浪費 | 彈性分配 |

### 9.3 Logger vs spdlog

[spdlog](https://github.com/gabime/spdlog) 是業界知名的高效能 C++ Logger。

| 比較項目 | 本實作 | spdlog |
|---------|-------|--------|
| 非同步 | ✅ | ✅ |
| 記憶體配置 | 零配置(Union) | 使用 `fmt::format`(動態分配) |
| 格式化 | printf-style | fmt-style(C++20 std::format) |
| 功能完整性 | 基本功能 | 支援多 Sink、Log Rotation |
| 延遲 | ~10ns(只寫入 Queue) | ~50-100ns |

**何時使用本實作?**
- 絕對延遲要求(< 20ns)
- 不需要複雜功能(如 Log Rotation、多檔案輸出)

**何時使用 spdlog?**
- 功能完整性優先
- 可容忍 50-100ns 的延遲

---

## 十、常見陷阱與最佳實踐

### 10.1 Lock-Free Queue 陷阱

**❌ 錯誤 1:未檢查佇列滿**
```cpp
// 危險:如果佇列滿了,會覆蓋未讀取的資料
*queue.getNextToWriteTo() = data;
queue.updateWriteIndex();
```

**✅ 正確做法**:
```cpp
if (queue.size() < queue.capacity()) {
    *queue.getNextToWriteTo() = data;
    queue.updateWriteIndex();
} else {
    // 處理佇列滿的情況(丟棄、阻塞、擴容)
}
```

**❌ 錯誤 2:在多生產者環境下使用**
```cpp
// ⚠️ 競爭條件!兩個執行緒可能取得相同的 next_write_index_
std::thread t1([&]{ *queue.getNextToWriteTo() = data1; });
std::thread t2([&]{ *queue.getNextToWriteTo() = data2; });
```

### 10.2 Memory Pool 陷阱

**❌ 錯誤 1:未呼叫解構子**
```cpp
struct MyObject {
    std::string name_;  // 動態分配記憶體
    ~MyObject() { /* 釋放 name_ */ }
};

MemPool<MyObject> pool(100);
MyObject* obj = pool.allocate("test");
pool.deallocate(obj);  // ⚠️ 只標記 is_free = true,未呼叫 ~MyObject()
// name_ 的記憶體洩漏!
```

**✅ 正確做法**:
```cpp
obj->~MyObject();  // 手動呼叫解構子
pool.deallocate(obj);
```

**❌ 錯誤 2:釋放外部指標**
```cpp
MyObject* external_obj = new MyObject();
pool.deallocate(external_obj);  // ⚠️ ASSERT 失敗(指標不屬於 pool)
```

### 10.3 Logger 陷阱

**❌ 錯誤 1:在佇列滿時繼續寫入**
```cpp
// 如果背景執行緒無法及時消費,佇列會滿
while (true) {
    logger.log("High frequency log");  // ⚠️ 可能覆蓋未寫入的 Log
}
```

**✅ 正確做法**:
```cpp
// 限制 Log 頻率或增大佇列大小
constexpr size_t LOG_QUEUE_SIZE = 64 * 1024 * 1024;  // 從 8MB 增加到 64MB
```

---

## 十一、技術名詞對照表

| 英文 | 繁體中文 | 說明 |
|------|---------|------|
| Lock-Free | 無鎖 | 不使用互斥鎖的並行技術 |
| Memory Ordering | 記憶體順序 | CPU 記憶體操作的可見性保證 |
| ABA Problem | ABA 問題 | 並行演算法中的值重複問題 |
| Placement New | 定位 new | 在指定記憶體位置呼叫建構子 |
| Cache Line | 快取行 | CPU 快取的最小單位(通常 64 bytes) |
| False Sharing | 偽共享 | 不同執行緒修改同一 Cache Line 導致的效能下降 |
| CPU Affinity | CPU 親和性 | 將執行緒綁定到特定 CPU 核心 |
| NUMA | 非均勻記憶體存取 | 多 CPU 系統中記憶體存取延遲不均勻的架構 |
| Nagle's Algorithm | Nagle 演算法 | TCP 延遲發送小封包的優化策略 |
| Multicast | 組播 | 一次發送多個接收者的網路傳輸方式 |
| Zero-Copy | 零拷貝 | 避免不必要的記憶體複製 |
| Hot Path | 熱路徑 | 程式中執行頻率最高的程式碼路徑 |

---

## 十二、總結

Chapter 4 建立了低延遲交易系統的基礎元件庫,展現了以下核心設計理念:

1. **預先配置(Pre-allocation)**:避免執行時記憶體分配,確保延遲穩定
2. **無鎖同步(Lock-Free)**:使用原子操作取代傳統鎖,消除阻塞
3. **Cache 友善(Cache-Friendly)**:連續記憶體佈局,最大化 CPU Cache 效率
4. **非同步化(Asynchronous)**:將耗時操作移出關鍵路徑

這些元件為後續章節的交易撮合引擎、行情發布系統、策略引擎奠定了堅實基礎。雖然當前實作尚未達到極致優化(如未使用 Relaxed Memory Order、未對齊 Cache Line),但已經展現了低延遲系統的核心思想。

**下一步**:
- **Chapter 6**:利用 Memory Pool 實作訂單簿(Order Book)
- **Chapter 7**:利用 Multicast Socket 發布行情資料
- **Chapter 8-10**:利用 Lock-Free Queue 串接各個元件
- **Chapter 11-12**:進一步優化(NUMA、Huge Pages、硬體時間戳)

---

**參考資料**:
- [C++ Concurrency in Action](https://www.manning.com/books/c-plus-plus-concurrency-in-action-second-edition) by Anthony Williams
- [Linux System Programming](https://www.oreilly.com/library/view/linux-system-programming/9781449341527/) by Robert Love
- [Intel® 64 and IA-32 Architectures Optimization Reference Manual](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
