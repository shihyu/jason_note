# Go 入門實務會遇到的問題整理（偏交易系統 / 高併發場景）

------------------------------------------------------------------------

## 一、Concurrency 實務問題

### 1. goroutine ≠ OS Thread

**白話說明：** goroutine 是 Go 的「輕量級執行緒」，一個 goroutine 只佔幾 KB 記憶體（OS thread 至少 1MB），Go runtime 會自動把成千上萬的 goroutine 分配到少數 OS thread 上跑。就像一個餐廳只有 4 個服務生（OS thread），但可以同時服務 1000 桌客人（goroutine）——靠的是服務生在桌與桌之間快速切換。

-   Go 採用 M:N Scheduler（G / M / P 模型）
    - **G** = Goroutine（工作單元）
    - **M** = Machine（OS Thread）
    - **P** = Processor（邏輯處理器，數量 = GOMAXPROCS）
-   可能遇到：
    -   goroutine 暴增導致 GC 壓力
    -   blocking syscall 卡住 P
    -   GOMAXPROCS 設定不當導致 CPU 使用率異常

**GOMAXPROCS 對效能的影響：**

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func cpuWork() {
    sum := 0
    for i := 0; i < 100_000_000; i++ {
        sum += i
    }
    _ = sum
}

func main() {
    fmt.Println("CPU 核心數:", runtime.NumCPU())
    fmt.Println("預設 GOMAXPROCS:", runtime.GOMAXPROCS(0))

    // 用不同 GOMAXPROCS 跑 CPU-bound 工作
    for _, procs := range []int{1, 2, 4, runtime.NumCPU()} {
        runtime.GOMAXPROCS(procs)
        start := time.Now()

        var wg sync.WaitGroup
        for i := 0; i < 4; i++ {
            wg.Add(1)
            go func() {
                defer wg.Done()
                cpuWork()
            }()
        }
        wg.Wait()

        fmt.Printf("GOMAXPROCS=%d → 耗時: %v\n", procs, time.Since(start))
    }
}
```

```text
# 實際輸出（Intel i7-14700K, 28 核）：
CPU 核心數: 28
預設 GOMAXPROCS: 28
GOMAXPROCS=1  → 耗時: 51.970377ms   ← 只有 1 個核心，4 個任務排隊跑
GOMAXPROCS=2  → 耗時: 22.214338ms   ← 2 核並行，快了一倍
GOMAXPROCS=4  → 耗時: 17.586621ms   ← 4 核剛好跑 4 個任務
GOMAXPROCS=28 → 耗時: 11.724444ms   ← 核心再多也只有 4 個任務
```

> **重點：** GOMAXPROCS 設太小，CPU-bound 的 goroutine 會排隊等。交易系統通常設成 `runtime.NumCPU()` 就好（Go 預設值）。容器環境下建議用 `go.uber.org/automaxprocs` 自動偵測 cgroup 限制。

### 2. Data Race

**白話說明：** 兩個 goroutine 同時讀寫同一塊記憶體，結果不確定誰先誰後，程式行為就會不可預期。最經典的就是 **map 併發寫入直接 panic**（Go 的 map 內建了 race 偵測，會直接 crash）。

常見問題：
- map 併發 crash
- slice append race
- unsafe pointer 使用錯誤

**map 併發寫入 crash 示範：**

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    m := make(map[string]int)
    var wg sync.WaitGroup

    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            key := fmt.Sprintf("key-%d", id%10)
            m[key] = id // ❌ 沒加鎖！多個 goroutine 同時寫 map
        }(i)
    }
    wg.Wait()
}
```

用 race detector 跑會看到：

```bash
$ go run -race race_unsafe.go
==================
WARNING: DATA RACE
Write at 0x00c0000c63f0 by goroutine 11:
  runtime.mapassign_faststr()
  ...
Previous write at 0x00c0000c63f0 by goroutine 17:
  runtime.mapassign_faststr()
  ...
```

**正確做法（三種方式）：**

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    // 方法 1：sync.Mutex
    var mu sync.Mutex
    m := make(map[string]int)
    var wg sync.WaitGroup

    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            key := fmt.Sprintf("key-%d", id%10)
            mu.Lock()
            m[key] = id
            mu.Unlock()
        }(i)
    }
    wg.Wait()
    fmt.Println("Mutex 版 map 長度:", len(m))

    // 方法 2：sync.Map（讀多寫少場景更適合）
    var sm sync.Map
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            sm.Store(fmt.Sprintf("key-%d", id%10), id)
        }(i)
    }
    wg.Wait()
    count := 0
    sm.Range(func(k, v any) bool { count++; return true })
    fmt.Println("sync.Map 長度:", count)

    // 方法 3：slice append 也要加鎖
    var mu2 sync.Mutex
    var results []int
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(val int) {
            defer wg.Done()
            mu2.Lock()
            results = append(results, val)
            mu2.Unlock()
        }(i)
    }
    wg.Wait()
    fmt.Println("安全 append, slice 長度:", len(results))
}
```

```text
# 實際輸出：
Mutex 版 map 長度: 10
sync.Map 長度: 10
安全 append, slice 長度: 100
```

工具：

```bash
# 開發期間一定要用 race detector 跑
go run -race main.go
go test -race ./...
```

> **交易系統重點：** 行情推送（寫）和策略讀取（讀）是典型的讀多寫少場景，用 `sync.RWMutex` 或 `sync.Map` 比普通 `Mutex` 效能更好。

------------------------------------------------------------------------

## 二、Memory & GC 問題

### 1. GC Pause / Latency Spike

**白話說明：** Go 的 GC（垃圾回收）會在背景自動清理不再使用的記憶體。問題是 GC 工作時會造成短暫的「暫停」（pause），雖然 Go 1.8+ 已經把 pause 壓到 1ms 以下，但對交易系統來說，一次 100μs 的 GC pause 就可能讓你的報價比別人慢一拍。

低延遲系統常見：
- tail latency 爆掉（P99 突然飆高）
- GC 導致 response 時間抖動

**觀察 GC 行為：**

```go
package main

import (
    "fmt"
    "runtime"
    "runtime/debug"
    "time"
)

func main() {
    // 製造一些垃圾
    for i := 0; i < 100_000; i++ {
        s := make([]byte, 1024) // 每次配 1KB，用完就丟
        _ = s
    }

    // 手動觸發 GC 並計時
    start := time.Now()
    runtime.GC()
    gcTime := time.Since(start)

    // 讀取 GC 統計
    var stats debug.GCStats
    debug.ReadGCStats(&stats)
    fmt.Println("GC 次數:", stats.NumGC)
    fmt.Printf("手動 GC 耗時: %v\n", gcTime)
    if len(stats.Pause) > 0 {
        fmt.Printf("最近 GC pause: %v\n", stats.Pause[0])
    }

    // 讀取記憶體統計
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    fmt.Printf("HeapAlloc: %.2f MB\n", float64(m.HeapAlloc)/1024/1024)
    fmt.Printf("HeapSys:   %.2f MB\n", float64(m.HeapSys)/1024/1024)
    fmt.Printf("NumGC:     %d\n", m.NumGC)

    // 低延遲場景：調整 GC 目標
    debug.SetGCPercent(20) // 更積極 GC（預設 100）
    fmt.Println("\n已設定 GOGC=20（更頻繁 GC，但每次 pause 更短）")
}
```

```text
# 實際輸出：
GC 次數: 1
手動 GC 耗時: 279.976µs
最近 GC pause: 33.48µs
HeapAlloc: 0.33 MB
HeapSys:   3.59 MB
NumGC:     1

已設定 GOGC=20（更頻繁 GC，但每次 pause 更短）
```

> **交易系統 GC 調參建議：**
> - `GOGC=20~50`：更頻繁 GC，每次 pause 更短，適合低延遲
> - `GOMEMLIMIT`（Go 1.19+）：設定記憶體上限，避免 OOM
> - 終極手段：用 `sync.Pool` 重用物件，從源頭減少 GC 壓力

### 2. Escape Analysis

**白話說明：** Go 編譯器會自動判斷變數該放 stack 還是 heap。放 stack 幾乎零成本（函式結束就回收），放 heap 則需要 GC 介入。如果你回傳了指標，編譯器就被迫把變數「逃逸」到 heap 上。交易系統要盡量減少逃逸，減少 GC 壓力。

```go
package main

import "fmt"

//go:noinline
func stackAlloc() int {
    x := 42   // ✅ x 留在 stack，函式結束就回收，零成本
    return x
}

//go:noinline
func heapAlloc() *int {
    x := 42    // ❌ x 逃逸到 heap，因為回傳了指標
    return &x  // 編譯器：「你回傳指標，我只好放 heap」
}

type Order struct {
    Price  float64
    Volume int
}

//go:noinline
func newOrderStack() Order {
    return Order{Price: 100.5, Volume: 10} // ✅ 值複製，不逃逸
}

//go:noinline
func newOrderHeap() *Order {
    return &Order{Price: 100.5, Volume: 10} // ❌ 逃逸到 heap
}

func main() {
    a := stackAlloc()
    b := heapAlloc()
    o1 := newOrderStack()
    o2 := newOrderHeap()
    fmt.Println(a, *b, o1, o2)
}
```

用 `-gcflags="-m"` 看逃逸分析結果：

```bash
$ go build -gcflags="-m" escape_demo.go
/tmp/go-examples/escape_demo.go:13:2: moved to heap: x        ← heapAlloc 的 x 逃逸了
/tmp/go-examples/escape_demo.go:29:9: &Order{...} escapes to heap  ← newOrderHeap 逃逸了
```

> **白話總結：**
> - 回傳值（非指標） → stack，便宜
> - 回傳指標 → heap，要 GC 清理
> - 交易系統的 hot path（撮合、行情處理）盡量用值傳遞，避免逃逸

------------------------------------------------------------------------

## 三、Debug 實務問題

### 常用工具

-   **dlv**（Delve debugger）：Go 專用 debugger，支援 goroutine 切換
-   **pprof**：CPU / Memory profiling
-   **runtime.Stack()**：印出所有 goroutine 狀態

### Goroutine Dump 實戰

**白話說明：** 當你的程式「卡住了」但不知道卡在哪，用 `runtime.Stack()` 把所有 goroutine 的狀態印出來，就像拍一張「全體員工在幹嘛」的快照。

```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "sync"
)

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    ch := make(chan int)
    select {
    case <-ch: // 故意卡住（模擬卡在等資料）
    }
}

func dumpGoroutines() {
    buf := make([]byte, 1024*64)
    n := runtime.Stack(buf, true) // true = dump 所有 goroutine
    fmt.Fprintf(os.Stderr, "=== Goroutine Dump ===\n%s\n", buf[:n])
}

func main() {
    var wg sync.WaitGroup

    for i := 0; i < 3; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }

    runtime.Gosched() // 讓其他 goroutine 跑起來
    dumpGoroutines()
    fmt.Println("目前 goroutine 數:", runtime.NumGoroutine())
}
```

```text
# 實際輸出（節錄）：
=== Goroutine Dump ===
goroutine 1 [running]:
main.dumpGoroutines()
    /tmp/go-examples/debug_demo.go:21 +0x3d
main.main()
    /tmp/go-examples/debug_demo.go:36 +0xaa

goroutine 6 [chan receive]:     ← 卡在 channel 接收！
main.worker(0x0?, 0x0?)
    /tmp/go-examples/debug_demo.go:15 +0x4f

goroutine 7 [chan receive]:     ← 也卡在 channel 接收
goroutine 8 [chan receive]:     ← 也卡在 channel 接收

目前 goroutine 數: 4
```

> **怎麼看 dump：** 重點看 `[chan receive]`、`[select]`、`[semacquire]` 這些狀態，代表 goroutine 在「等東西」。如果等的東西永遠不會來，那就是 leak 或 deadlock。

### 常見 Debug 場景

| 症狀 | 工具 | 看什麼 |
|------|------|--------|
| 程式卡住不動 | `runtime.Stack()` | 找 `[chan receive]` / `[select]` |
| CPU 飆高 | `go tool pprof` | 找 hot function |
| 記憶體一直漲 | `go tool pprof -alloc_space` | 找誰在大量配記憶體 |
| 懷疑 deadlock | `dlv` + breakpoint | 看鎖的持有狀態 |

------------------------------------------------------------------------

## 四、Channel 死鎖問題

**白話說明：** Channel 就像一個傳話筒——有人說話就要有人聽，沒人聽就卡住。unbuffered channel（沒有 buffer 的）更嚴格：送和收必須同時發生，像面對面交談。buffered channel 則像信箱，塞滿才會卡住。

常見錯誤訊息：

```text
fatal error: all goroutines are asleep - deadlock!
```

**各種死鎖情境和解法：**

```go
package main

import "fmt"

func main() {
    // ===== 情境 1：沒人接收 =====
    // ch := make(chan int)
    // ch <- 1  // ❌ 永遠卡住！main goroutine 在送，沒人收

    // ✅ 正確：用另一個 goroutine 接收
    ch := make(chan int)
    go func() {
        val := <-ch
        fmt.Println("收到:", val)
    }()
    ch <- 42 // 現在有人收了，不會卡

    // ===== 情境 2：range channel 忘記 close =====
    ch2 := make(chan int, 3)
    ch2 <- 1
    ch2 <- 2
    ch2 <- 3
    close(ch2) // ✅ 一定要 close！不然 range 會永遠等下去
    for v := range ch2 {
        fmt.Println("range 收到:", v)
    }

    // ===== 情境 3：buffered channel 不會馬上卡 =====
    buffered := make(chan int, 1) // buffer 大小 1
    buffered <- 99                // ✅ 不卡（buffer 還有空間）
    fmt.Println("buffered 收到:", <-buffered)

    fmt.Println("全部完成，沒有死鎖！")
}
```

```text
# 實際輸出：
收到: 42
range 收到: 1
range 收到: 2
range 收到: 3
buffered 收到: 99
全部完成，沒有死鎖！
```

**select 搭配 timeout / context（交易系統必備）：**

```go
package main

import (
    "context"
    "fmt"
    "time"
)

func main() {
    // 場景：等行情資料，但不能等太久
    ch := make(chan string)
    go func() {
        time.Sleep(2 * time.Second) // 模擬行情延遲
        ch <- "行情資料到了"
    }()

    select {
    case msg := <-ch:
        fmt.Println("收到:", msg)
    case <-time.After(1 * time.Second):
        fmt.Println("⏰ 超時！沒等到行情") // 1 秒就放棄
    }

    // 推薦用 context（可以在上層統一管理取消）
    ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
    defer cancel()

    ch2 := make(chan string)
    go func() {
        time.Sleep(1 * time.Second) // 模擬成交回報延遲
        ch2 <- "成交回報"
    }()

    select {
    case msg := <-ch2:
        fmt.Println("收到:", msg)
    case <-ctx.Done():
        fmt.Println("⏰ context 超時:", ctx.Err())
    }

    // 非阻塞嘗試：有就拿，沒有就算了
    ch3 := make(chan int, 1)
    select {
    case val := <-ch3:
        fmt.Println("收到:", val)
    default:
        fmt.Println("channel 是空的，不等了")
    }
}
```

```text
# 實際輸出：
⏰ 超時！沒等到行情
⏰ context 超時: context deadline exceeded
channel 是空的，不等了
```

> **死鎖防治口訣：**
> 1. unbuffered channel 送收必須配對
> 2. range channel 一定要 close
> 3. 交易系統永遠加 timeout（用 context 或 select + time.After）
> 4. 不確定就用 buffered channel

------------------------------------------------------------------------

## 五、HTTP Server 問題

### 1. Connection Leak

**白話說明：** 每次 HTTP 請求都會開一條 TCP 連線。如果你忘記關 `resp.Body`，這條連線就不會被回收，久了連線池就滿了，新的請求就發不出去。就像借了書不還，圖書館的書就會越來越少。

```go
package main

import (
    "context"
    "fmt"
    "io"
    "net/http"
    "net/http/httptest"
    "time"
)

func main() {
    // 模擬交易所 API
    ts := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte(`{"price": 42000.5}`))
    }))
    defer ts.Close()

    // ❌ 錯誤：沒關 resp.Body → connection leak
    resp, _ := http.Get(ts.URL)
    _ = resp // 忘記 resp.Body.Close()！
    fmt.Println("❌ 沒關 Body, status:", resp.StatusCode)

    // ✅ 正確：關 Body + 設 timeout + 用 context
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

    client := &http.Client{Timeout: 5 * time.Second}
    req, _ := http.NewRequestWithContext(ctx, "GET", ts.URL, nil)

    resp2, err := client.Do(req)
    if err != nil {
        fmt.Println("錯誤:", err)
        return
    }
    defer resp2.Body.Close()                // ✅ 一定要 close
    body, _ := io.ReadAll(resp2.Body)       // ✅ 讀完 body
    fmt.Println("✅ 正確讀取:", string(body))
}
```

```text
# 實際輸出：
❌ 沒關 Body, status: 200
✅ 正確讀取: {"price": 42000.5}
```

### 2. Context 沒傳

**白話說明：** Context 是 Go 的「取消令牌」。如果你啟動了一個 goroutine 去呼叫 API，但沒有傳 context 進去，當使用者斷線或 timeout 時，那個 goroutine 還是會繼續跑（浪費資源），最終導致 goroutine leak。

```go
// ❌ 錯誤：goroutine 不知道什麼時候該停
go func() {
    resp, _ := http.Get("https://api.exchange.com/ticker")
    // 就算 caller 已經不要結果了，這裡還是會等到回應
}()

// ✅ 正確：用 context 控制生命週期
go func(ctx context.Context) {
    req, _ := http.NewRequestWithContext(ctx, "GET", "https://api.exchange.com/ticker", nil)
    client := &http.Client{}
    resp, err := client.Do(req)
    if err != nil {
        return // context 被取消，直接退出
    }
    defer resp.Body.Close()
    // 處理結果...
}(ctx)
```

------------------------------------------------------------------------

## 六、壓測工具

### 工具比較

| 工具 | 語言 | 特色 | 適用場景 |
|------|------|------|----------|
| **k6** | JS (Go 引擎) | 腳本化場景 | 複雜 API 流程測試 |
| **wrk** | C | 極輕量 | 單一端點最大 RPS |
| **vegeta** | Go | 固定 RPS 模式 | latency 分析 |
| **hey** | Go | 簡單好用 | 快速壓一下看結果 |

```bash
# hey：最簡單的壓測（10 秒，200 併發）
hey -z 10s -c 200 http://localhost:8080/api/ticker

# vegeta：固定 RPS（每秒 1000 次，持續 30 秒）
echo "GET http://localhost:8080/api/ticker" | vegeta attack -rate=1000 -duration=30s | vegeta report

# k6：腳本化場景
# k6 run load_test.js
```

------------------------------------------------------------------------

## 七、Production 常見問題

### 1. Goroutine Leak

**白話說明：** Goroutine leak 就是啟動了 goroutine 但它永遠不會結束，像打開水龍頭忘了關。一個 goroutine 佔幾 KB 記憶體，漏個幾萬個就是幾百 MB。最可怕的是 QPS 沒變但記憶體慢慢漲，重啟前根本不知道怎麼回事。

```go
package main

import (
    "context"
    "fmt"
    "runtime"
    "time"
)

// ❌ 會 leak 的 worker
func leakyWorker() {
    ch := make(chan int)
    go func() {
        val := <-ch     // 永遠在等，沒人 send 也沒人 close
        fmt.Println(val) // 永遠不會執行
    }()
    // 函式結束了，但 goroutine 還活著！
}

// ✅ 安全的 worker（用 context 控制生命週期）
func safeWorker(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            return // context 取消時，goroutine 正常退出
        }
    }()
}

func main() {
    fmt.Println("起始 goroutine 數:", runtime.NumGoroutine())

    // 製造 leak
    for i := 0; i < 10; i++ {
        leakyWorker()
    }
    time.Sleep(100 * time.Millisecond)
    fmt.Println("leakyWorker 後:", runtime.NumGoroutine(), "個 goroutine")

    // 安全版本
    ctx, cancel := context.WithCancel(context.Background())
    for i := 0; i < 10; i++ {
        safeWorker(ctx)
    }
    time.Sleep(100 * time.Millisecond)
    fmt.Println("safeWorker 後（cancel 前）:", runtime.NumGoroutine(), "個")
    cancel() // 一聲令下，所有 safe goroutine 退出
    time.Sleep(100 * time.Millisecond)
    fmt.Println("cancel 後:", runtime.NumGoroutine(), "個（leak 的 10 個還在）")
}
```

```text
# 實際輸出：
起始 goroutine 數: 1
leakyWorker 後: 11 個 goroutine        ← 多了 10 個永遠不會結束的
safeWorker 後（cancel 前）: 21 個       ← 再多 10 個
cancel 後: 11 個（leak 的 10 個還在）    ← safe 的全退了，leaky 的還卡著
```

> **防 leak 三原則：**
> 1. 每個 goroutine 都要有退出機制（context / done channel / timeout）
> 2. 用 `runtime.NumGoroutine()` 監控 goroutine 數量
> 3. Production 用 pprof 的 `/debug/pprof/goroutine` 端點觀察

### 2. FD 用光

**白話說明：** Linux 的每個 TCP 連線、每個開啟的檔案都要一個 File Descriptor（FD）。系統預設限制 1024 個。高頻交易系統如果對交易所有大量 API 呼叫，很容易把 FD 用光。

```text
too many open files
```

解法：

```bash
# 1. 調大系統限制
ulimit -n 65535

# 2. 永久設定（/etc/security/limits.conf）
# * soft nofile 65535
# * hard nofile 65535
```

```go
// 3. 在程式碼裡正確設定 HTTP Transport
transport := &http.Transport{
    MaxIdleConns:        100,              // 全域最大閒置連線
    MaxIdleConnsPerHost: 10,               // 每個 host 最大閒置連線
    IdleConnTimeout:     30 * time.Second, // 閒置連線超時回收
}

client := &http.Client{
    Transport: transport,
    Timeout:   10 * time.Second,
}
```

```text
# 實際輸出：
HTTP Client 設定完成:
  MaxIdleConns: 100
  MaxIdleConnsPerHost: 10
  IdleConnTimeout: 30s
  Client Timeout: 10s
```

### 3. TCP TIME_WAIT 爆炸

**白話說明：** TCP 連線關閉後會進入 TIME_WAIT 狀態，等 2 分鐘才真正釋放。高頻 API 呼叫如果每次都開新連線，很快就會有上萬個 TIME_WAIT，新連線就建不了。

```bash
# 查看 TIME_WAIT 數量
ss -s | grep TIME-WAIT
# 或
netstat -an | grep TIME_WAIT | wc -l
```

解法：

```go
// 重用連線（Keep-Alive），不要每次都開新的
transport := &http.Transport{
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 100,              // 對同一個 host 保持足夠的閒置連線
    IdleConnTimeout:     90 * time.Second,
    DisableKeepAlives:   false,            // 確保 Keep-Alive 開啟（預設就是 false）
}

// 全域共用一個 client，不要每次 new
var globalClient = &http.Client{Transport: transport}
```

------------------------------------------------------------------------

## 八、Module / Dependency 問題

### replace directive

**白話說明：** 當你需要用本地修改過的套件（例如改了交易所 SDK 的 bug），可以用 `replace` 把遠端套件指向本地路徑。

```go
// go.mod
module mytrading

go 1.22

require github.com/some/exchange-sdk v1.2.3

// 暫時用本地修改版
replace github.com/some/exchange-sdk => ../my-exchange-sdk
```

### 私有 repo

```bash
# 設定 GOPRIVATE 讓 go 不要走 proxy
export GOPRIVATE=github.com/mycompany/*

# 用 SSH 存取私有 repo
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

### vendor 模式

```bash
# 把依賴下載到 vendor/ 目錄（部署時不用再下載）
go mod vendor

# 用 vendor 建構
go build -mod=vendor ./...
```

------------------------------------------------------------------------

## 九、進階優化方向（偏高頻 / 交易系統）

### sync.Pool：物件重用

**白話說明：** 頻繁 `new` 物件再丟掉，GC 會很累。`sync.Pool` 就像一個「物件回收站」——用完的物件丟進去，下次要用再拿出來，省去配記憶體和 GC 的成本。交易系統的 OrderBook、Tick 這類頻繁建立的結構特別適合。

```go
package main

import (
    "fmt"
    "sync"
)

type OrderBook struct {
    Bids []float64
    Asks []float64
}

var orderBookPool = sync.Pool{
    New: func() any {
        return &OrderBook{
            Bids: make([]float64, 0, 100),
            Asks: make([]float64, 0, 100),
        }
    },
}

func getOrderBook() *OrderBook {
    ob := orderBookPool.Get().(*OrderBook)
    ob.Bids = ob.Bids[:0] // 清空但保留底層 array（不重新配記憶體）
    ob.Asks = ob.Asks[:0]
    return ob
}

func putOrderBook(ob *OrderBook) {
    orderBookPool.Put(ob)
}

func main() {
    ob1 := getOrderBook()
    ob1.Bids = append(ob1.Bids, 42000.5, 41999.0)
    fmt.Println("OrderBook bids:", ob1.Bids)
    putOrderBook(ob1) // 用完還回去

    ob2 := getOrderBook() // 拿到剛才那個（已清空，但 capacity 保留）
    fmt.Println("重用後 bids 長度:", len(ob2.Bids), "容量:", cap(ob2.Bids))
    putOrderBook(ob2)
}
```

```text
# 實際輸出：
OrderBook bids: [42000.5 41999]
重用後 bids 長度: 0 容量: 100   ← 底層 array 被重用了，不用重新配
```

**Benchmark 對比：**

```text
# 實際 benchmark 結果（Intel i7-14700K）：
BenchmarkWithoutPool-28    125156714    9.534 ns/op    0 B/op    0 allocs/op
BenchmarkWithPool-28       184272228    6.419 ns/op    0 B/op    0 allocs/op
                                        ~~~~~~~~
                                        Pool 快了 ~33%
```

> 注意：上面 benchmark 因為編譯器優化，alloc 都是 0。實際在複雜程式中，Pool 的優勢更明顯（減少 heap allocation → 減少 GC 壓力）。

### 其他優化方向

| 技術 | 說明 | 交易系統場景 |
|------|------|-------------|
| **object reuse** | 預先配好物件反覆使用 | Tick、Order 結構重用 |
| **zero copy** | 避免不必要的記憶體複製 | 行情解析，直接操作 byte slice |
| **netpoll** | Go 底層的非同步 I/O | 大量 WebSocket 連線 |
| **lock contention** | 減少鎖競爭 | 用 `atomic` 取代 `Mutex` 做計數器 |
| **runtime scheduler** | 理解 G/M/P 排程行為 | 避免 goroutine 在 hot path 被搶佔 |

------------------------------------------------------------------------

## 十、核心難點總結

真正困難在：

| 難點 | 為什麼難 | 怎麼面對 |
|------|---------|---------|
| **1. 理解 scheduler** | G/M/P 模型抽象，行為不確定 | 讀 runtime 源碼，用 `GODEBUG=schedtrace=1000` 觀察 |
| **2. 控制 GC latency** | GC pause 不可控，受 heap 大小影響 | 調 GOGC、用 sync.Pool、減少逃逸 |
| **3. 找 goroutine leak** | 表面看不出來，記憶體慢慢漲 | pprof goroutine profile + runtime.NumGoroutine 監控 |

```bash
# 觀察 scheduler 行為
GODEBUG=schedtrace=1000 ./your_program

# 輸出範例：
# SCHED 0ms: gomaxprocs=8 idleprocs=7 threads=5 spinningthreads=0 idlethreads=0 ...
# SCHED 1000ms: gomaxprocs=8 idleprocs=4 threads=9 ...
#                              ^^^^^^^^^ 有 4 個 P 閒置

# pprof 看 goroutine 數量
go tool pprof http://localhost:6060/debug/pprof/goroutine
```

------------------------------------------------------------------------

## 建議練習方式

| 練習 | 會碰到什麼問題 | 學到什麼 |
|------|---------------|---------|
| 1. 寫高併發 REST API | data race, connection leak | Mutex, context, http client 設定 |
| 2. 模擬撮合引擎 | lock contention, GC pause | sync.Pool, atomic, 逃逸分析 |
| 3. 寫 WebSocket server | goroutine leak, FD 用光 | context 控制, transport 設定 |
| 4. benchmark + pprof 分析 | 找不到瓶頸 | pprof 火焰圖、trace 分析 |
| 5. 壓測壓到出現瓶頸 | 各種 production 問題 | 調參、診斷、修復的完整流程 |

**推薦練習順序：** 1 → 4 → 3 → 2 → 5（由易到難）

------------------------------------------------------------------------

------------------------------------------------------------------------

## 附錄：Go 開發常用工具整理

**白話說明：** 寫 Go 不只是寫程式碼，更多時間花在「觀察程式在幹嘛」。以下工具鏈覆蓋從即時監控到深度分析的完整流程，全部 `go install` 即可使用。

### 工具總覽

| 工具 | Stars | 功能 | 一句話說明 |
|------|-------|------|-----------|
| [Delve](https://github.com/go-delve/delve) | ~24k | Debugger / Trace | Go 專用 debugger，支援 goroutine 切換、條件斷點 |
| [pprof](https://github.com/google/pprof) | 高 | Profiling 火焰圖 | CPU / Memory / Goroutine 的瑞士刀 |
| [statsviz](https://github.com/arl/statsviz) | 中 | 即時 Web 儀表板 | 一行程式碼開啟 runtime metrics 儀表板 |
| [go-callvis](https://github.com/ondrajz/go-callvis) | 中高 | 呼叫運行圖 | 靜態分析產生互動式呼叫圖 SVG |
| [fgprof](https://github.com/felixge/fgprof) | 高 | CPU + Off-CPU Trace | 同時追蹤 CPU 和 I/O 等待時間 |

### 安裝方式

```bash
# Delve debugger
go install github.com/go-delve/delve/cmd/dlv@latest

# pprof（獨立版，比內建的更新）
go install github.com/google/pprof@latest

# go-callvis（呼叫圖視覺化）
go install github.com/ofabry/go-callvis@latest

# 驗證安裝
dlv version    # Delve Debugger Version: 1.26.0
which pprof    # /home/user/go/bin/pprof
which go-callvis
```

> **注意：** `statsviz` 和 `fgprof` 是 library，不是 CLI 工具，需在程式碼中 import。

### 1. Delve（dlv）— Go 專用 Debugger

**白話說明：** GDB 對 Go 的支援很差（看不到 goroutine、interface 顯示亂碼），Delve 是專門為 Go 設計的 debugger，能正確顯示 goroutine 狀態、channel 內容、defer stack 等。

```bash
# 啟動 debug（會自動 build 並進入互動模式）
dlv debug main.go

# 常用指令
(dlv) break main.main          # 設斷點
(dlv) break main.go:42         # 在第 42 行設斷點
(dlv) continue                 # 繼續執行到斷點
(dlv) next                     # 下一行（不進入函式）
(dlv) step                     # 下一行（進入函式）
(dlv) print myVar              # 印變數值
(dlv) locals                   # 印所有本地變數
(dlv) goroutines               # 列出所有 goroutine ← 重點！
(dlv) goroutine 5              # 切換到 goroutine 5
(dlv) stack                    # 看當前 goroutine 的 call stack

# 條件斷點（只在 price > 50000 時停下）
(dlv) break main.go:30
(dlv) condition 1 price > 50000

# attach 到正在跑的 process
dlv attach <PID>

# 用 headless 模式搭配 IDE（VS Code / GoLand）
dlv debug --headless --listen=:2345 --api-version=2
```

**交易系統 debug 場景：**
```bash
# 程式跑到一半卡住了？attach 上去看所有 goroutine 在幹嘛
dlv attach $(pgrep my-trading-bot)
(dlv) goroutines          # 找到卡住的 goroutine
(dlv) goroutine 15        # 切過去
(dlv) stack               # 看 call stack，找出卡在哪
```

### 2. pprof — 效能分析火焰圖

**白話說明：** pprof 就像程式的 X 光片——不用改程式碼（只要 import 一行），就能看到 CPU 花在哪、記憶體被誰吃掉、有多少 goroutine 在跑。

**在程式中啟用 pprof：**

```go
package main

import (
    "fmt"
    "net/http"
    _ "net/http/pprof" // 只要 import 這行！
    "runtime"
    "time"
)

func leakyWork() {
    for i := 0; i < 10; i++ {
        ch := make(chan int)
        go func() { <-ch }() // 故意 leak
    }
}

func main() {
    // pprof HTTP server
    go func() {
        fmt.Println("pprof: http://localhost:6060/debug/pprof/")
        http.ListenAndServe(":6060", nil)
    }()

    leakyWork()
    time.Sleep(200 * time.Millisecond)
    fmt.Println("goroutine 數:", runtime.NumGoroutine())

    select {} // 保持程式運行
}
```

**常用 pprof 指令：**

```bash
# CPU profiling（錄 30 秒）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Memory profiling
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profiling（找 leak 必用）
go tool pprof http://localhost:6060/debug/pprof/goroutine

# 進入互動模式後
(pprof) top 10         # 前 10 耗 CPU 的函式
(pprof) web            # 開瀏覽器看火焰圖（需要 graphviz）
(pprof) list main.     # 看 main 套件每行的耗時

# 直接在瀏覽器看（推薦！）
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/heap
# 然後打開 http://localhost:8080 → 選 Flame Graph
```

> **交易系統常用：** `goroutine` profile 找 leak，`heap` profile 看記憶體，`profile` 看 CPU。三個看完基本就知道瓶頸在哪。

### 3. statsviz — 即時 Runtime 儀表板

**白話說明：** pprof 是「拍 X 光」，statsviz 是「裝心電圖」——即時顯示 goroutine 數量、GC pause、heap 大小等 runtime metrics 的變化趨勢。一行程式碼就能開啟 Web 儀表板。

```go
package main

import (
    "fmt"
    "net/http"

    "github.com/arl/statsviz"
)

func main() {
    // 一行搞定！
    statsviz.RegisterDefault()

    fmt.Println("statsviz 儀表板: http://localhost:6060/debug/statsviz/")
    http.ListenAndServe(":6060", nil)
}
```

```bash
# 安裝依賴
go get github.com/arl/statsviz@latest

# 打開瀏覽器 http://localhost:6060/debug/statsviz/
# 會看到即時更新的圖表：
# - Heap size（記憶體使用趨勢）
# - GC pause（每次 GC 暫停多久）
# - Goroutines（goroutine 數量變化）
# - CPU（GC 佔 CPU 比例）
```

> **什麼時候用：** 壓測時開著 statsviz，即時觀察 GC pause 和 goroutine 數量，比看 log 直覺 100 倍。

### 4. go-callvis — 呼叫運行圖

**白話說明：** 接手一個陌生的 Go 專案，不知道從哪看起？go-callvis 會自動分析程式碼，產生函式呼叫關係圖（SVG），讓你一眼看懂整個專案的結構。

```bash
# 產生呼叫圖（會開啟瀏覽器）
go-callvis ./cmd/server

# 產生 SVG 檔案
go-callvis -file output ./cmd/server
# 會產生 output.svg

# 只看特定 package
go-callvis -focus main ./cmd/server

# 忽略 stdlib
go-callvis -nostd ./cmd/server

# 用不同演算法（rta 更精確但更慢）
go-callvis -algo rta ./cmd/server
```

### 5. fgprof — CPU + Off-CPU 混合 Profiling

**白話說明：** 標準 pprof 只看 CPU 在跑的時間，但交易系統很多時間花在「等」（等 API 回應、等 channel、等鎖）。fgprof 同時追蹤 CPU 時間和等待時間，讓你看到完整的時間花費。

```go
package main

import (
    "fmt"
    "net/http"
    _ "net/http/pprof"

    "github.com/felixge/fgprof"
)

func main() {
    // 註冊 fgprof 端點
    http.DefaultServeMux.Handle("/debug/fgprof", fgprof.Handler())

    fmt.Println("fgprof: http://localhost:6060/debug/fgprof")
    fmt.Println("pprof:  http://localhost:6060/debug/pprof/")
    http.ListenAndServe(":6060", nil)
}
```

```bash
# 安裝依賴
go get github.com/felixge/fgprof@latest

# 抓 fgprof 資料（錄 10 秒）
go tool pprof http://localhost:6060/debug/fgprof?seconds=10

# 和標準 pprof 一樣操作
(pprof) top
(pprof) web
```

> **pprof vs fgprof：**
> - pprof：「CPU 花最多時間在哪個函式？」（只看 on-CPU）
> - fgprof：「程式花最多時間在哪個函式？」（包含等待 I/O、sleep、鎖）
> - 交易系統推薦兩個都裝，互相對比

### 完整工具鏈使用流程

```text
開發階段                    壓測/上線前                    Production
   │                          │                            │
   ├─ go-callvis              ├─ statsviz                  ├─ pprof HTTP endpoint
   │  靜態分析專案結構          │  即時觀察 runtime metrics    │  遠端抓 profile
   │                          │                            │
   ├─ dlv                     ├─ pprof + fgprof            ├─ runtime.NumGoroutine()
   │  斷點 debug               │  找 CPU/Memory 瓶頸         │  goroutine leak 監控
   │  goroutine 切換           │  火焰圖分析                 │
   │                          │                            ├─ GODEBUG=schedtrace
   └─ go run -race            └─ hey/vegeta 壓測            │  scheduler 行為觀察
      Data race 檢測               搭配 pprof 一起看          │
                                                           └─ statsviz
                                                              即時儀表板
```

```bash
# 一鍵安裝所有工具
go install github.com/go-delve/delve/cmd/dlv@latest && \
go install github.com/google/pprof@latest && \
go install github.com/ofabry/go-callvis@latest && \
echo "✅ CLI 工具安裝完成（statsviz/fgprof 是 library，go get 即可）"
```

------------------------------------------------------------------------

（適合具備 Linux / 系統底層經驗的工程師進階 Go 使用）
