# Context Switch 完整比較：OS 底層 vs 語言層級

> 整理日期：2026-02-24  
> 涵蓋：作業系統原理、C/C++、Rust、Go

---

## 一、什麼是 Context Switch（上下文切換）？

Context Switch 是指 **CPU 停止執行當前任務，並切換去執行另一個任務** 的過程。

### 切換時需要儲存的狀態（CPU Context）

| 類別 | 內容 |
|------|------|
| 通用寄存器 | RAX, RBX, RCX, RDX … |
| 程序計數器 | RIP（下一條要執行的指令位置） |
| Stack Pointer | RSP（目前 stack 頂端） |
| CPU Flags | RFLAGS（條件旗標） |
| FPU / SIMD 狀態 | XMM / YMM 寄存器（浮點數與向量運算） |
| 記憶體映射 | CR3（Page Table 基址，process 切換時需要換） |

> **Process 切換** 比 **Thread 切換** 更貴，因為需要額外更換 Page Table（TLB flush）。

---

## 二、Context Switch 的層次分類

```
┌─────────────────────────────────────────────────┐
│               應用程式層（Developer）              │
│  Go context.Context / Rust Future / C++ coroutine │
├─────────────────────────────────────────────────┤
│               語言執行期層（Runtime）              │
│  Go Scheduler (M:N)  /  Tokio Executor           │
├─────────────────────────────────────────────────┤
│               作業系統層（Kernel）                 │
│  Process / Kernel Thread  context switch          │
├─────────────────────────────────────────────────┤
│               硬體層（CPU）                        │
│  暫存器儲存、TLB 刷新、Cache Miss                  │
└─────────────────────────────────────────────────┘
```

---

## 三、各語言 Context Switch 機制比較

### 3.1 總覽表

| 特性 | C（pthread） | C++20 Coroutine | Rust async/await | Go Goroutine |
|------|------------|----------------|-----------------|-------------|
| **並發單元** | Kernel Thread | Coroutine（stackless） | Future（stackless） | Goroutine（stackful） |
| **Stack** | OS 分配（預設 8MB） | 無獨立 Stack | 無獨立 Stack | 動態 Stack（初始 2KB） |
| **切換類型** | OS Context Switch | State Machine 轉移 | State Machine 轉移 | Go Runtime 切換 |
| **切換成本** | 高（需進 Kernel） | 極低 | 極低 | 低（User Space） |
| **調度者** | OS Kernel | 開發者/框架 | tokio / async-std | Go Runtime |
| **並發模型** | 1:1（Thread:OS Thread） | N:1 or M:N（視框架） | M:N（tokio） | M:N |
| **記憶體安全** | 手動（不安全） | 手動（不安全） | 編譯期保證 | GC + Race Detector |
| **學習曲線** | 中 | 高 | 高 | 低 |

---

### 3.2 C 語言：最接近底層

#### 使用 pthread（Kernel Thread）

```c
#include <pthread.h>

void* worker(void* arg) {
    // 每個 thread 由 OS 調度，切換時是完整的 context switch
    return NULL;
}

int main() {
    pthread_t t;
    pthread_create(&t, NULL, worker, NULL);
    pthread_join(t, NULL);
}
```

**特點：**
- 每個 thread 是 OS Kernel Thread，切換需要 syscall，成本高
- 預設 Stack 大小 8MB，大量 thread 會耗盡記憶體

#### 使用 ucontext（User Space 協程模擬）

```c
#include <ucontext.h>

ucontext_t ctx1, ctx2;
char stack[64 * 1024];  // 手動分配 Stack

void func2() {
    printf("in func2\n");
    swapcontext(&ctx2, &ctx1);  // 切回 ctx1
}

int main() {
    getcontext(&ctx2);
    ctx2.uc_stack.ss_sp = stack;
    ctx2.uc_stack.ss_size = sizeof(stack);
    ctx2.uc_link = &ctx1;
    makecontext(&ctx2, func2, 0);

    swapcontext(&ctx1, &ctx2);  // 切換到 ctx2
    printf("back in main\n");
}
```

**特點：**
- User Space 切換，不需要進入 Kernel
- 比 pthread 輕量，但需要**手動管理 Stack**
- 是許多協程框架（如 libco、libtask）的底層原語

---

### 3.3 C++20：Stackless Coroutine

C++20 引入 `co_await`、`co_yield`、`co_return`，編譯器自動產生 **State Machine**。

```cpp
#include <coroutine>
#include <iostream>

struct Generator {
    struct promise_type {
        int value;
        Generator get_return_object() {
            return Generator{std::coroutine_handle<promise_type>::from_promise(*this)};
        }
        std::suspend_always initial_suspend() { return {}; }
        std::suspend_always final_suspend() noexcept { return {}; }
        std::suspend_always yield_value(int v) {
            value = v;
            return {};
        }
        void return_void() {}
        void unhandled_exception() {}
    };

    std::coroutine_handle<promise_type> handle;

    int next() {
        handle.resume();  // ← 這裡發生 "context switch"（state machine 轉移）
        return handle.promise().value;
    }
};

Generator counter() {
    for (int i = 0; ; ++i)
        co_yield i;  // ← 暫停點，儲存目前狀態
}

int main() {
    auto gen = counter();
    for (int i = 0; i < 5; ++i)
        std::cout << gen.next() << "\n";
}
```

**切換原理：**

```
co_yield / co_await 遇到時：
  → 編譯器將目前局部變數打包進 coroutine frame（heap 上）
  → 記錄下一個 resume 的位置（類似 goto label）
  → 返回給 caller

resume() 呼叫時：
  → 從 coroutine frame 恢復狀態
  → 跳到上次暫停的位置繼續執行
```

**成本對比：**
- 無 Stack 分配（只有一個 heap object）
- 切換只是 **函式呼叫 + struct 欄位存取**，極輕量
- 缺點：無法在任意深度的呼叫堆疊中 `co_await`（不像 Go 可以在任何地方被調度）

---

### 3.4 Rust：async/await + Future

Rust 的 async 也是 **stackless coroutine**，但加上了編譯期記憶體安全保證。

```rust
use tokio::time::{sleep, Duration};

async fn task_a() {
    println!("Task A: start");
    sleep(Duration::from_millis(100)).await;  // ← 暫停點，讓出執行權
    println!("Task A: done");
}

async fn task_b() {
    println!("Task B: start");
    sleep(Duration::from_millis(50)).await;
    println!("Task B: done");
}

#[tokio::main]
async fn main() {
    tokio::join!(task_a(), task_b());
}
```

**Future 的本質：**

```rust
// async fn task_a() 會被編譯器轉成類似這樣的 State Machine：
enum TaskAState {
    Start,
    WaitingSleep(SleepFuture),
    Done,
}

impl Future for TaskA {
    type Output = ();
    fn poll(&mut self, cx: &mut Context) -> Poll<()> {
        match self.state {
            Start => {
                println!("Task A: start");
                self.state = WaitingSleep(sleep(...));
                Poll::Pending  // ← 告訴 runtime 我還沒好
            }
            WaitingSleep(ref mut f) => {
                if f.poll(cx).is_ready() {
                    println!("Task A: done");
                    Poll::Ready(())
                } else {
                    Poll::Pending
                }
            }
        }
    }
}
```

**tokio 的 M:N 調度：**

```
┌──────────────────────────────────────┐
│  tokio Runtime                        │
│  ┌────────────┐  ┌────────────┐       │
│  │ Worker 1   │  │ Worker 2   │  ...  │  ← OS Threads（數量 = CPU 核心數）
│  │            │  │            │       │
│  │ Future A   │  │ Future C   │       │
│  │ Future B   │  │ Future D   │       │
│  └────────────┘  └────────────┘       │
│         ↑ poll() / wake() 驅動         │
└──────────────────────────────────────┘
```

**Rust vs Go 記憶體安全：**

| 場景 | Go | Rust |
|------|----|------|
| 跨 Goroutine 共享資料 | 執行期 Race Detector | 編譯期 Send/Sync trait 檢查 |
| 資料競爭 | `go run -race` 檢測 | 編譯器直接拒絕 |
| 記憶體洩漏 | GC 自動回收 | 所有權系統自動釋放 |

---

### 3.5 Go：Goroutine + G-M-P 調度模型

#### Goroutine 的特點

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func worker(ctx context.Context, id int) {
    for {
        select {
        case <-ctx.Done():
            fmt.Printf("Worker %d stopped: %v\n", id, ctx.Err())
            return
        default:
            fmt.Printf("Worker %d working...\n", id)
            time.Sleep(100 * time.Millisecond)
        }
    }
}

func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
    defer cancel()

    for i := 0; i < 3; i++ {
        go worker(ctx, i)  // ← 建立 Goroutine，僅 2KB stack
    }

    <-ctx.Done()
    fmt.Println("All workers stopped")
}
```

#### G-M-P 調度模型

```
G = Goroutine（使用者的並發任務）
M = Machine（OS Thread，真正執行 G 的載體）
P = Processor（調度上下文，持有 run queue）

┌────────────────────────────────────────────────┐
│  Go Runtime Scheduler                           │
│                                                 │
│  P1: [G1, G2, G3, ...]  →  M1 (OS Thread)      │
│  P2: [G4, G5, G6, ...]  →  M2 (OS Thread)      │
│  P3: [G7, ...]          →  M3 (OS Thread)       │
│                                                 │
│  Global Queue: [G8, G9, ...]                    │
└────────────────────────────────────────────────┘

當 G 遇到以下情況時，Go Scheduler 切換 Goroutine：
  - channel 阻塞
  - syscall（Go 會把 M 與 P 分離）
  - time.Sleep
  - runtime.Gosched()
  - 函式呼叫（搶佔式調度，Go 1.14+）
```

**Goroutine 切換 vs OS Context Switch 成本比較：**

| 項目 | OS Thread Context Switch | Goroutine Switch |
|------|--------------------------|-----------------|
| 觸發方式 | Kernel 中斷 | Go Runtime 函式呼叫 |
| 儲存的狀態 | 所有 CPU 寄存器 + FPU | 僅 3 個寄存器（SP, PC, DX） |
| 典型耗時 | ~1–10 μs | ~100–200 ns |
| Stack 大小 | 固定（MB 級） | 動態 2KB–1GB |
| 最大並發數 | 千～萬 | 百萬 |

---

## 四、Go `context.Context`：應用層的任務控制

這與 OS Context Switch 完全不同，是用來 **控制 Goroutine 生命週期** 的工具。

### context 的樹狀結構

```
context.Background()
    └── WithCancel(ctx)          ← 可手動取消
        └── WithTimeout(ctx, 5s) ← 5 秒後自動取消
            └── WithValue(ctx, "traceID", "abc123")  ← 攜帶元數據
```

### 四種 context 函式

| 函式 | 用途 | 典型場景 |
|------|------|---------|
| `context.Background()` | 根 context，永不取消 | main / 頂層函式 |
| `WithCancel(parent)` | 手動呼叫 `cancel()` 時取消 | 提前結束子任務 |
| `WithTimeout(parent, d)` | 超時自動取消 | HTTP 請求逾時 |
| `WithDeadline(parent, t)` | 指定截止時間點取消 | 定時任務 |
| `WithValue(parent, k, v)` | 傳遞請求級別的值 | Trace ID、Auth Token |

### 實際應用：HTTP 請求鏈

```go
func handleRequest(w http.ResponseWriter, r *http.Request) {
    ctx, cancel := context.WithTimeout(r.Context(), 3*time.Second)
    defer cancel()

    // 傳遞 TraceID
    ctx = context.WithValue(ctx, "traceID", generateTraceID())

    result, err := queryDatabase(ctx)
    if err != nil {
        if errors.Is(err, context.DeadlineExceeded) {
            http.Error(w, "timeout", 504)
        }
        return
    }
    // ...
}

func queryDatabase(ctx context.Context) (string, error) {
    select {
    case <-ctx.Done():
        return "", ctx.Err()  // 上游取消了，立即返回
    case result := <-doQuery():
        return result, nil
    }
}
```

---

## 五、各語言協程機制深度對比

### Stackful vs Stackless

```
Stackful Coroutine（Go Goroutine / C ucontext）：
  ┌──────────────────────┐
  │ Goroutine A          │
  │  Stack Frame 3       │  ← 可以在任意呼叫深度暫停
  │  Stack Frame 2       │
  │  Stack Frame 1       │
  └──────────────────────┘

Stackless Coroutine（Rust Future / C++20 coroutine）：
  ┌──────────────────────┐
  │ Future/State Machine │
  │  { state: Waiting,   │  ← 只儲存暫停點的局部變數
  │    local_var: 42 }   │
  └──────────────────────┘
  注意：只能在 async fn 內使用 await，不能在普通函式中暫停
```

### 效能基準（參考值）

| 操作 | 耗時（參考） |
|------|------------|
| OS Thread Context Switch | 1,000 – 10,000 ns |
| Go Goroutine Switch | 100 – 300 ns |
| Rust Future Poll（無等待） | < 10 ns |
| C ucontext swapcontext | 50 – 200 ns |
| C++20 coroutine resume | < 10 ns |

### 記憶體佔用（每個並發單元）

| 並發單元 | 記憶體 | 最大建議數量 |
|---------|--------|------------|
| OS Thread（Linux） | ~8 MB stack | ~數千 |
| Go Goroutine | 2KB – 8KB（動態） | ~百萬 |
| Rust Future | 依狀態 struct 大小 | ~百萬以上 |
| C ucontext | 手動設定（通常 64KB+） | ~數萬 |

---

## 六、選擇指南

```
你需要什麼？
│
├─ 高效能 I/O 密集型服務（Web API、微服務）
│   ├─ 易用性優先 → Go（Goroutine + context）
│   └─ 效能/控制優先 → Rust（tokio + async）
│
├─ 系統程式 / 嵌入式（記憶體受限）
│   ├─ 傳統多執行緒 → C（pthread）
│   └─ 現代協程 → C++20 coroutine 或 Rust async（no_std）
│
├─ CPU 密集型運算
│   ├─ 所有語言的 OS Thread 都適用
│   └─ Go 的 Goroutine 在 CPU-bound 無明顯優勢
│
└─ 需要細粒度控制生命週期
    └─ 一定要用 Go context.Context 或 Rust 的 CancellationToken
```

---

## 七、總結一句話

| 語言/概念 | 核心問題 |
|----------|---------|
| **OS Context Switch** | CPU 現在要幫誰工作？ |
| **C pthread** | 我來直接開 OS Thread，切換交給 Kernel |
| **C ucontext** | 我手動切換，比 Kernel 便宜但你要自己管 |
| **C++20 coroutine** | 編譯器幫我產生 State Machine，切換超便宜 |
| **Rust async/await** | 同上，但加上編譯期記憶體安全 |
| **Go Goroutine** | Runtime 幫我調度，Stack 自動增長，用起來最簡單 |
| **Go context.Context** | 這個任務還需要繼續執行嗎？ |

---

*本文整理自 OS 原理、C POSIX 文件、C++20 標準、Rust async Book、Go 官方文件*
