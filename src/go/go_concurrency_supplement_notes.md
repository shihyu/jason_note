# Go 併發補充知識筆記

## 一、核心概念

### 1. Goroutine（輕量級執行緒）

```go
go func() {
    fmt.Println("我在另一個 goroutine 跑")
}()
```

Goroutine 的啟動成本極低，初始堆疊約 2KB，而 C++ thread 通常需要 1MB 以上。你可以同時跑數十萬個 goroutine，因為它們由 Go runtime 排程，而不是直接對應 OS thread（M:N mapping）。

---

### 2. Channel（通道）

```go
ch := make(chan int, 1) // buffered channel
ch <- 42               // 發送
v := <-ch              // 接收
```

Go 的核心哲學：
> **"不要透過共享記憶體來通訊，要透過通訊來共享記憶體"**

Channel 方向宣告可以限制使用方式，讓 API 更安全：

```go
func producer(ch chan<- int) { ... } // 只能寫
func consumer(ch <-chan int) { ... } // 只能讀
```

---

### 3. Select

```go
select {
case msg := <-ch1:
    fmt.Println(msg)
case msg := <-ch2:
    fmt.Println(msg)
case <-time.After(1 * time.Second):
    fmt.Println("timeout")
}
```

`select` 會隨機選擇一個可執行的 case，常用來處理 timeout、多 channel 監聽、以及 `context` 取消。

---

### 4. sync 套件

| 工具 | 用途 |
|---|---|
| `sync.Mutex` / `sync.RWMutex` | 互斥鎖 / 讀寫鎖 |
| `sync.WaitGroup` | 等待多個 goroutine 完成 |
| `sync.Once` | 確保某段程式碼只執行一次 |
| `sync/atomic` | 低階原子操作，效能最高 |

---

## 二、sync.Once 深入解析

### 結構體

```go
type Once struct {
    done uint32  // 標記是否已執行過，0 = 未執行，1 = 已執行
    m    Mutex   // 互斥鎖，保護 f() 只被呼叫一次
}
```

### 原始碼

```go
func (o *Once) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 {
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    // 雙重檢查
    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}
```

拆解方法簽名：

```
func  (o *Once)  Do  (f func())  { ... }
 │        │       │       │
 │        │       │       └── 參數：f 是一個無參數無回傳的函數
 │        │       └────────── 方法名稱
 │        └────────────────── 接收者：屬於 *Once 型別
 └─────────────────────────── 關鍵字
```

`func (o *Once) Do(f func())` 是**方法**，不是函數。差別在於有沒有接收者：

```go
// 函數 — 直接呼叫
func Do(f func()) { ... }
Do(f)

// 方法 — 透過實例呼叫，(o *Once) 類似其他語言的 this / self
func (o *Once) Do(f func()) { ... }
var once Once
once.Do(f)
```

`f func()` 是參數，型別是「一個無參數、無回傳值的函數」：

```go
// 一般參數
func Add(n int)   { ... }  // n 是 int

// 函數作為參數
func Do(f func()) { ... }  // f 是一個 func()

// 呼叫時把函數傳進去
once.Do(func() {
    fmt.Println("hello")
})
```

---

### 執行流程

```
Do(f) 被呼叫
        │
        ▼
  done == 0？
   /        \
 No          Yes
  │           │
直接返回    doSlow(f)
（已執行過）    │
            加鎖 m.Lock()
                │
            再檢查 done == 0？  ← 雙重檢查
              /       \
            No         Yes
             │          │
            解鎖      執行 f()
                      done = 1
                      解鎖
```

---

### 為什麼要兩次檢查 done？

這是經典的 **Double-Checked Locking** 模式。情境如下：

```
Goroutine A                       Goroutine B
──────────────────────────────────────────────
atomic.Load(done) == 0 ✓
                                  atomic.Load(done) == 0 ✓
m.Lock() ← 搶到鎖
done == 0 ✓ → 執行 f()
done = 1
m.Unlock()
                                  m.Lock() ← 等待後拿到鎖
                                  done == 1 ✗ → 跳過 f()  ← 第二次檢查擋住！
                                  m.Unlock()
```

沒有第二次檢查的話，f() 就會被執行兩次。

---

### 為什麼第一次用 atomic.Load，第二次直接讀？

```go
// 第一次：在鎖外，需要 atomic 保證跨 goroutine 可見性
if atomic.LoadUint32(&o.done) == 0 { ... }

// 第二次：已在鎖內，Mutex 本身保證記憶體可見性，直接讀即可
if o.done == 0 { ... }
```

---

### 為什麼 done 要用 defer 寫回？

```go
defer atomic.StoreUint32(&o.done, 1)
f()
```

順序看起來奇怪，但 `defer` 是在 `f()` 執行完之後才把 `done` 設為 1。這樣設計的目的是：確保其他 goroutine 在看到 `done == 1` 的瞬間，`f()` 的所有副作用已完全可見，不會拿到一個「初始化到一半」的狀態。

---

### 常見錯誤

```go
var once sync.Once
var config *Config

// ❌ 錯誤：外層加 nil 判斷是 race condition
// config 可能在另一個 goroutine 初始化到一半
if config == nil {
    once.Do(func() { config = loadConfig() })
}

// ✅ 正確：直接 Do，內部保證只執行一次
once.Do(func() {
    config = loadConfig()
})
// Do 返回後直接使用，不需要再判斷 nil
```

---

### 完整可執行範例

```go
package main

import (
    "fmt"
    "sync"
    "sync/atomic"
)

// ===== 模擬 sync.Once 原始碼 =====

type MyOnce struct {
    done uint32
    m    sync.Mutex
}

func (o *MyOnce) Do(f func()) {
    if atomic.LoadUint32(&o.done) == 0 {
        o.doSlow(f)
    }
}

func (o *MyOnce) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done == 0 {
        defer atomic.StoreUint32(&o.done, 1)
        f()
    }
}

// ===== Demo 1：基本使用 =====

func demo1() {
    fmt.Println("=== Demo1: 基本使用 ===")
    var once MyOnce
    var wg sync.WaitGroup

    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            once.Do(func() {
                fmt.Printf("Goroutine %d 執行了 f()\n", id)
            })
        }(i)
    }
    wg.Wait()
    fmt.Println("f() 只被執行一次，其餘 goroutine 跳過")
    fmt.Println()
}

// ===== Demo 2：雙重檢查必要性 =====

func demo2() {
    fmt.Println("=== Demo2: 雙重檢查 ===")
    var once MyOnce
    var wg sync.WaitGroup
    var count int

    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            once.Do(func() {
                count++
            })
        }()
    }
    wg.Wait()
    fmt.Printf("count = %d（期望值為 1）\n\n", count)
}

// ===== Demo 3：單例初始化 =====

type Config struct {
    DSN string
}

var (
    cfg     *Config
    cfgOnce MyOnce
)

func getConfig() *Config {
    cfgOnce.Do(func() {
        fmt.Println("初始化 Config...")
        cfg = &Config{DSN: "postgres://localhost:5432/db"}
    })
    return cfg
}

func demo3() {
    fmt.Println("=== Demo3: 單例初始化 ===")
    var wg sync.WaitGroup

    for i := 0; i < 3; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            c := getConfig()
            fmt.Printf("Goroutine %d 拿到 Config: %s\n", id, c.DSN)
        }(i)
    }
    wg.Wait()
    fmt.Println()
}

// ===== Demo 4：常見錯誤示範 =====

func demo4() {
    fmt.Println("=== Demo4: 常見錯誤 ===")
    var once sync.Once
    var resource *string

    initResource := func() {
        s := "initialized"
        resource = &s
    }

    // ❌ 錯誤寫法：外層判斷 nil 是 race condition
    // if resource == nil {
    //     once.Do(initResource)
    // }

    // ✅ 正確寫法：直接 Do
    once.Do(initResource)
    fmt.Printf("resource = %s\n\n", *resource)
}

// ===== Demo 5：defer atomic.Store 順序驗證 =====

func demo5() {
    fmt.Println("=== Demo5: defer atomic.Store 順序 ===")
    var once MyOnce
    var wg sync.WaitGroup
    ready := make(chan struct{})

    wg.Add(1)
    go func() {
        defer wg.Done()
        once.Do(func() {
            fmt.Println("f() 開始執行...")
            <-ready
            fmt.Println("f() 執行完畢，done 即將設為 1")
        })
    }()

    wg.Add(1)
    go func() {
        defer wg.Done()
        close(ready)
        once.Do(func() {
            fmt.Println("B 的 f() 不應該出現！")
        })
        fmt.Println("B 的 Do 已返回（等待 A 完成）")
    }()

    wg.Wait()
    fmt.Println()
}

func main() {
    demo1()
    demo2()
    demo3()
    demo4()
    demo5()
}
```

---

## 三、Memory Model（記憶體模型）

### 為什麼需要它？

Memory Model 規定：「何時」一個 goroutine 寫入的值，對另一個 goroutine 是「可見的」。

現代硬體與編譯器有兩種優化行為會造成問題：

**① CPU 快取（Cache）**

```
CPU Core 1          CPU Core 2
  L1 Cache            L1 Cache
     ↕                   ↕
        共享 RAM
```

Core 1 寫入的值可能還在 L1 Cache，尚未刷回 RAM，Core 2 根本看不到最新值。

**② 編譯器 / CPU 指令重排**

```go
// 你寫的
x = 1
ready = true

// 編譯器可能優化成
ready = true  // 順序被調換！
x = 1
```

單執行緒下結果相同，但多執行緒下就會出問題。

---

### 經典錯誤範例

```go
var x int
var ready bool

// Goroutine A
x = 42
ready = true

// Goroutine B
if ready {
    fmt.Println(x) // 可能印出 0！
}
```

B 可能看到 `ready = true`，但因為指令重排或 cache 問題，`x` 對 B 來說還是 0。結果是**未定義行為**，不是每次都重現，最難 debug 的那種。

---

### Happens-Before

Memory Model 的核心是定義 **happens-before** 關係：

> 如果 A happens-before B，則 A 的記憶體寫入，B **保證**看得到

```
A ──happens-before──→ B
寫 x=42               讀 x（保證是 42）
```

Go 保證以下操作具有 happens-before 關係：

- `sync.Mutex` 的 `Lock` / `Unlock`
- Channel 的發送 / 接收
- `sync.WaitGroup` 的 `Wait`
- `go` 啟動 goroutine 那一行

---

### 正確修法

**方法一：Channel（最 Go 風格）**

```go
package main

import "fmt"

func main() {
    var x int
    ch := make(chan struct{})

    go func() {
        x = 42
        ch <- struct{}{} // 發送 happens-before 接收
    }()

    <-ch             // main 在這裡阻塞，等 goroutine 送值過來
    fmt.Println(x)   // 保證是 42
}
```

`<-ch` 是阻塞的，main 會在這裡等到 goroutine 把值送進來才繼續，這就是 happens-before 的保證點。`struct{}{}` 是慣用的「空信號」，純粹通知「我做完了」，不佔任何記憶體。

**方法二：Mutex**

```go
var mu sync.Mutex

go func() {
    mu.Lock()
    x = 42
    mu.Unlock()
}()

mu.Lock()
fmt.Println(x) // 保證是 42
mu.Unlock()
```

**方法三：atomic（效能最高，但只適合簡單場景）**

```go
var x int64
var ready int32

go func() {
    atomic.StoreInt64(&x, 42)
    atomic.StoreInt32(&ready, 1)
}()

if atomic.LoadInt32(&ready) == 1 {
    fmt.Println(atomic.LoadInt64(&x))
}
```

---

## 四、Context Switch：Go vs C/C++

### 兩種執行緒模型

**C/C++ — 1:1 模型**

```
Thread A    Thread B    Thread C
   │            │           │
   └────────────┴───────────┘
              OS Kernel
         （直接對應 OS thread）
```

**Go — M:N 模型**

```
Goroutine A  Goroutine B  Goroutine C  Goroutine D
     └──────────┘               └──────────┘
       OS Thread 1             OS Thread 2
          │                        │
          └────────────────────────┘
                   OS Kernel
```

Go 的 runtime 自己扮演「排程器」的角色，把 N 個 goroutine 映射到 M 個 OS thread 上。

---

### C/C++ Thread 為什麼需要進 Kernel Space？

C/C++ 的 thread 直接就是 OS thread，任何排程決策都必須請 OS 幫你做：

```
Thread A 要切換到 Thread B

1. 觸發 syscall → 進入 kernel space
2. OS 儲存 Thread A 的 CPU registers、stack pointer 等完整狀態
3. OS 決定下一個跑誰
4. OS 載入 Thread B 的狀態
5. 返回 user space
6. Thread B 開始跑
```

每次 context switch 都要跨越 **user space ↔ kernel space** 的邊界，代價很高：

- 儲存/恢復完整的 CPU 狀態（registers、floating point state 等）
- kernel 要驗證權限
- CPU cache 可能被污染（TLB flush）
- 一次約 **1~10 微秒**

---

### Go 為什麼可以留在 User Space？

Go runtime 內建了自己的排程器（**G-M-P 模型**），不需要問 OS：

```
Goroutine A 要切換到 Goroutine B

1. Go runtime（在 user space）決定切換
2. 只儲存 goroutine 需要的最小狀態（PC、SP、少數 registers）
3. 切換到 Goroutine B
4. 全程在 user space，沒有 syscall
```

代價極低，一次約 **100~200 奈秒**，比 OS thread 快 10~100 倍。

---

### G-M-P 模型

Go runtime 的排程器由三個元素組成：

```
G = Goroutine   （要執行的任務）
M = OS Thread   （實際執行的載體，對應 kernel）
P = Processor   （邏輯處理器，持有 run queue）

P1 [G1, G2, G3, ...]      P2 [G4, G5, G6, ...]
        │                          │
       M1                         M2
        │                          │
        └──────────Kernel──────────┘
```

每個 P 有自己的 local run queue，G 在 P 之間排程，完全不需要進 kernel。當某個 P 的 queue 空了，還可以從其他 P「偷」goroutine 來跑（**work stealing**）。

---

### 什麼時候 Go 還是會進 Kernel Space？

Go 並非完全不碰 kernel，以下情況還是會：

| 情況 | 原因 |
|---|---|
| 檔案 I/O、網路 syscall | 需要 OS 介入 |
| `cgo` 呼叫 C 程式碼 | 離開 Go runtime 的管控 |
| goroutine 數量需要新建 thread 時 | 向 OS 要新的 thread |
| GC 某些階段 | Stop-the-world 需要 OS 配合 |

但 Go runtime 對網路 I/O 做了特別處理，透過 **netpoller**（底層用 epoll/kqueue）讓 goroutine 等待 I/O 時不會卡住 OS thread，而是把 OS thread 讓給其他 goroutine 繼續跑。

---

## 五、Go vs C/C++ 完整對比

| 面向 | Go | C/C++ |
|---|---|---|
| 執行緒模型 | Goroutine（M:N mapping） | OS Thread（1:1） |
| Context switch 位置 | User space（Go runtime） | Kernel space（OS） |
| 切換成本 | ~100–200 ns | ~1,000–10,000 ns |
| 儲存的狀態大小 | 極小（PC、SP） | 完整 CPU 狀態 |
| 排程決策者 | Go runtime | OS kernel |
| 同時存在數量 | 數十萬 | 數千（受 OS 限制） |
| 初始 stack 大小 | 2KB（可動態增長） | 1–8MB（固定） |
| 同步原語 | Channel 為主，也有 Mutex | 主要靠 Mutex、condition variable |
| 記憶體模型 | 有明確的 Go Memory Model | C++11 才有 memory model |
| Race 偵測 | 內建 `-race` flag | 需要 ThreadSanitizer（外部工具） |
| 死鎖偵測 | Runtime 可偵測部分 deadlock | 幾乎沒有內建支援 |
| 複雜度 | 相對簡單 | 更底層、更複雜 |

**C++ vs Go atomic 對比：**

```cpp
// C++ — 需要手動指定 memory order，容易誤用
std::atomic<int> x;
x.store(42, std::memory_order_release);
x.load(std::memory_order_acquire);
```

```go
// Go — 隱藏底層複雜度，用 channel 或 mutex 就好
ch := make(chan int)
go func() { ch <- 42 }()
result := <-ch
```

**C++ 手動管理 thread 對比：**

```cpp
// C++ — 手動管理 thread + mutex
std::mutex mu;
std::thread t([&]() {
    std::lock_guard<std::mutex> lock(mu);
    shared_data++;
});
t.join();
```

```go
// Go — 用 channel 更安全、更簡潔
ch := make(chan int)
go func() { ch <- 1 }()
result := <-ch
```

---

## 六、C++20 Coroutine vs Go Goroutine

### 先看本質差異

**Go Goroutine** — 有 runtime 全權管理

```
你只需要寫：
go func() { ... }()

剩下全部 Go runtime 幫你搞定：
- 排程
- stack 管理
- context switch
- work stealing
```

**C++20 Coroutine** — 只是語言機制，不是完整執行系統

```
co_await、co_yield、co_return

C++ 只給你「暫停/恢復」的能力
排程器？你自己寫，或用第三方庫
```

這是最根本的差異：**Go 是完整的併發系統，C++20 Coroutine 只是一個底層原語**。

---

### C++20 Coroutine 有排程器嗎？

**標準本身沒有**，你有三個選擇：

```
選項 1：自己實作排程器（極複雜）
選項 2：用第三方框架
         - cppcoro
         - libunifex
         - folly::coro（Meta 出品）
         - asio（Boost/standalone）
選項 3：只用 coroutine 做非同步，不做多執行緒排程
```

C++20 coroutine 標準只定義了關鍵字的行為，排程邏輯完全由 `Promise` 和 `Awaitable` 物件決定，你要自己實作或依賴框架。

---

### Context Switch 在哪裡發生？

**Go Goroutine**

```
完全在 User Space
Go runtime（G-M-P 模型）自己排程
不需要進 kernel
切換成本 ~100–200 ns
```

**C++20 Coroutine**

```
取決於你怎麼用：

情況 1：單執行緒 coroutine（純 user space）
  coroutine A ──co_await──→ coroutine B
  全程在同一個 thread，完全不碰 kernel
  切換成本極低 ~幾個 ns（只是函數跳躍）

情況 2：搭配 thread pool 排程器
  coroutine 恢復時可能被丟到不同 thread
  thread 切換還是會碰 kernel
  但 coroutine 本身的暫停/恢復仍在 user space
```

---

### 誰效能好？

**純切換成本**

```
C++20 Coroutine（單執行緒）  ~1–10 ns    ← 最快，只是 jmp 指令
Go Goroutine                ~100–200 ns  ← 需要 runtime 介入
C/C++ Thread                ~1,000–10,000 ns
```

C++ coroutine 在純切換上贏，因為它本質上就是**編譯器幫你做的函數暫停/恢復**，沒有任何 runtime overhead。

**實際應用效能（10 萬個併發任務）**

```
Go Goroutine
  ✅ 開箱即用
  ✅ runtime 自動分配到多個 CPU core
  ✅ work stealing 讓 CPU 使用率高
  ✅ 自動處理 blocking syscall

C++20 Coroutine（自己搭排程器）
  ✅ 理論上切換更快
  ❌ 要自己實作或整合排程器
  ❌ 要自己處理 blocking syscall
  ❌ 要自己做 work stealing
  ❌ 複雜度極高，踩坑成本大
```

---

### 底層機制對比

**Go Goroutine — runtime 動態管理 stack**

```
goroutine 初始 stack：2KB
需要更多空間時：runtime 自動擴展（最大 1GB）
切換時儲存：PC、SP、少數 registers
```

**C++20 Coroutine — 編譯器靜態配置 frame**

```
編譯時決定 coroutine frame 大小
存在 heap 上（一次 malloc）
切換時儲存：整個 coroutine frame 的狀態
沒有動態 stack，用的是原本 thread 的 stack
```

這導致一個重要差異：

```cpp
// C++ coroutine 不能無限遞迴
// frame 大小編譯時決定，stack 是借用 thread 的

// Go goroutine 可以遞迴很深
// runtime 會自動擴展 stack
```

---

### 程式碼對比

**Go — 簡單直接**

```go
func fetchData(url string) string {
    // 直接寫，runtime 幫你處理非同步
    resp, _ := http.Get(url)
    defer resp.Body.Close()
    body, _ := io.ReadAll(resp.Body)
    return string(body)
}

func main() {
    for i := 0; i < 10000; i++ {
        go func() {
            data := fetchData("https://example.com")
            fmt.Println(data)
        }()
    }
}
```

**C++20 — 需要大量樣板**

```cpp
// 光是讓 coroutine 能用，就要先實作這些：
struct Task {
    struct promise_type {
        Task get_return_object() { ... }
        std::suspend_never initial_suspend() { ... }
        std::suspend_never final_suspend() noexcept { ... }
        void return_void() { ... }
        void unhandled_exception() { ... }
    };
};

// 然後才能寫業務邏輯
Task fetchData(std::string url) {
    auto result = co_await asyncHttpGet(url); // asyncHttpGet 也要自己實作
    co_return result;
}
```

C++20 coroutine 的樣板程式碼量非常大，光是讓它跑起來就需要實作 `promise_type`、`Awaitable` 等一堆概念。

---

### 完整對比表

| | Go Goroutine | C++20 Coroutine |
|---|---|---|
| 排程器 | 內建（G-M-P） | 無，需自備或用框架 |
| Context switch 位置 | User space | User space（單線程時） |
| 切換成本 | ~100–200 ns | ~1–10 ns |
| 初始記憶體 | 2KB（動態擴展） | heap 上的 frame（靜態大小） |
| 多核利用 | 自動 | 需自己實作 |
| Blocking syscall 處理 | runtime 自動處理 | 需自己處理或靠框架 |
| 上手難度 | 簡單 | 極複雜 |
| 最大併發數 | 數十萬（開箱即用） | 理論無限（但要自己搭） |
| Work stealing | 內建 | 需自己實作 |
| Stack overflow 保護 | 有 | 無（借用 thread stack） |

**一句話總結：**

> C++20 Coroutine 是工具，Go Goroutine 是完整的解決方案。C++ coroutine 的切換成本理論上更低，但你要自己搭排程器、處理 syscall、實作 work stealing——踩坑成本極高。如果追求極致效能且有足夠工程資源，C++ 可以做到更快；如果要在合理時間內做出高併發系統，Go 是更務實的選擇。

---

## 七、常見陷阱

### 1. Goroutine 洩漏

```go
// 危險：ch 沒人讀，goroutine 永遠卡住
go func() {
    ch <- data // 永遠阻塞！
}()
```

啟動 goroutine 前，要確認誰負責讀取或關閉 channel，否則這個 goroutine 會永遠存在、佔用記憶體。

---

### 2. 閉包捕獲問題

```go
// 錯誤示範：全部可能印出 3
for i := 0; i < 3; i++ {
    go func() { fmt.Println(i) }()
}

// 正確：傳入當下的值
for i := 0; i < 3; i++ {
    go func(i int) { fmt.Println(i) }(i)
}
```

閉包捕獲的是變數的「參考」，不是「當下的值」。迴圈結束時 `i` 已經是 3，所有 goroutine 都讀到同一個 3。

---

### 3. 共享資料未同步（Race Condition）

```go
// 危險：多個 goroutine 同時寫入
counter := 0
for i := 0; i < 1000; i++ {
    go func() { counter++ }() // race condition！
}

// 正確：用 atomic 或 mutex
var counter int64
for i := 0; i < 1000; i++ {
    go func() { atomic.AddInt64(&counter, 1) }()
}
```

---

## 八、重要一句話

> 只要兩個 goroutine 共享資料，就**必須**用同步機制（channel / mutex / atomic），否則結果是未定義的，即使「看起來能跑」。

用 `go run -race main.go` 可以幫你抓大部分這類問題。

---

## 九、學習工具與資源

### 開發時必用

- `go run -race main.go` — 內建 race detector，強烈建議開發時常開

### 互動學習

- **Go Tour** — 官方互動教學，必做
- **Go Playground** — 線上執行、快速測試

### 深入理解

- **Goroutine visualizer** — 視覺化 goroutine 行為
- **Go Memory Model（官方文件）** — 理解 happens-before 的權威來源

### 書籍

- **《Concurrency in Go》** by Katherine Cox-Buday — 目前最完整的 Go 併發參考書

### 實作練習（最重要的三個 Pattern）

| Pattern | 概念 |
|---|---|
| Pipeline | 多個 goroutine 串成流水線，前一個的輸出是下一個的輸入 |
| Fan-out / Fan-in | 一個輸入分散給多個 worker 處理，再匯聚回來 |
| Worker Pool | 固定數量的 goroutine 處理任務佇列，控制併發上限 |

這三個 pattern 涵蓋了大多數實務場景，自己實作一遍理解會非常深。
