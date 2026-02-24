# Go 併發觀察與調試工具全覽

---

## 1. `go tool trace` — 執行追蹤視覺化

**安裝方式：** 內建，無需額外安裝

```go
// main.go
package main

import (
    "os"
    "runtime/trace"
    "sync"
)

func main() {
    f, _ := os.Create("trace.out")
    defer f.Close()
    trace.Start(f)
    defer trace.Stop()

    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            // 模擬工作
        }(i)
    }
    wg.Wait()
}
```

```bash
go run main.go
go tool trace trace.out   # 開啟瀏覽器視覺化介面
```

**可觀察：** Goroutine 生命週期、阻塞原因、Syscall、Channel 操作、GC 事件

---

## 2. `pprof` — 效能剖析

```go
import (
    "net/http"
    _ "net/http/pprof"  // 自動註冊 /debug/pprof 端點
)

func main() {
    go func() {
        http.ListenAndServe(":6060", nil)
    }()
    // ... 你的程式
}
```

```bash
# 抓取 goroutine 快照
go tool pprof http://localhost:6060/debug/pprof/goroutine

# 抓取鎖競爭 (需先啟用)
go tool pprof http://localhost:6060/debug/pprof/mutex

# 抓取阻塞剖析
go tool pprof http://localhost:6060/debug/pprof/block

# 互動式分析
(pprof) top
(pprof) web        # 生成 SVG 圖形（需安裝 graphviz）
(pprof) list main  # 查看特定函數細節
```

**啟用 mutex/block 剖析需加這行：**

```go
runtime.SetMutexProfileFraction(1)   // mutex
runtime.SetBlockProfileRate(1)       // block
```

---

## 3. `-race` 競態偵測器

```go
// race_example.go
package main

import "fmt"

func main() {
    counter := 0
    done := make(chan bool)

    go func() {
        counter++   // ← Data Race！
        done <- true
    }()

    counter++       // ← Data Race！
    <-done
    fmt.Println(counter)
}
```

```bash
go run -race race_example.go
# 輸出：WARNING: DATA RACE，包含完整 goroutine stack trace
go test -race ./...   # 對整個專案跑競態測試
```

---

## 4. `GODEBUG` 環境變數

```bash
# schedtrace：每 500ms 輸出 Scheduler 狀態
GODEBUG=schedtrace=500 go run main.go
# 輸出格式（Go 1.21+）：
# SCHED 0ms: gomaxprocs=8 idleprocs=6 threads=5 spinningthreads=1 needspinning=0 idlethreads=0 runqueue=0 [0 0 0 0 0 0 0 0]
# 欄位說明：spinningthreads=自旋中執行緒, needspinning=需要自旋, idlethreads=閒置執行緒

# scheddetail：更詳細的 goroutine 狀態（加上 gcwaiting/stopwait 等 GC 欄位）
GODEBUG=schedtrace=1000,scheddetail=1 go run main.go

# asyncpreemptoff=1：關閉異步搶占（調試特定問題用）
GODEBUG=asyncpreemptoff=1 go run main.go

# gctrace=1：每次 GC 輸出一行摘要，觀察 STW 暫停對併發的影響
GODEBUG=gctrace=1 go run main.go
# 輸出範例：
# gc 1 @0.011s 2%: 0.011+0.39+0.012 ms clock, 0.022+0.020/0.22/0+0.025 ms cpu, 4->4->0 MB, 5 MB goal, 4 P
# 欄位解讀：
#   gc 1       = 第幾次 GC
#   @0.011s    = 程式啟動後的時間點
#   2%         = GC 佔 CPU 總時間的比例
#   0.011+0.39+0.012 ms = STW掃描終止 + 並發標記 + STW標記終止
#   4->4->0 MB = GC前heap → 標記後heap → 存活物件
#   5 MB goal  = 下次 GC 觸發門檻
#   4 P        = 當前 GOMAXPROCS

# gccheckmark=1：GC 正確性驗證（開發/測試用，會大幅降速）
GODEBUG=gccheckmark=1 go test ./...
```

---

## 5. `runtime` 套件 — 程式內部監控

```go
import "runtime"

func printStats() {
    fmt.Println("Goroutine 數量:", runtime.NumGoroutine())
    fmt.Println("CPU 核心數:", runtime.NumCPU())
    fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))

    var ms runtime.MemStats
    runtime.ReadMemStats(&ms)
    fmt.Printf("Heap 使用: %v MB\n", ms.HeapAlloc/1024/1024)
}
```

---

## 6. `goleak` — Goroutine 洩漏偵測 ⭐

```bash
go get go.uber.org/goleak   # 需在 go module 專案內執行
```

```go
import (
    "testing"
    "time"
    "go.uber.org/goleak"
)

// 洩漏範例：測試會失敗並報告洩漏位置
func TestLeakyFunc(t *testing.T) {
    defer goleak.VerifyNone(t)

    go func() {
        time.Sleep(time.Hour)  // 這個 goroutine 永遠不結束 → 洩漏
    }()
}

// 正確範例：測試通過
func TestCleanFunc(t *testing.T) {
    defer goleak.VerifyNone(t)

    done := make(chan struct{})
    go func() {
        defer close(done)
        // 做完事情就結束
    }()
    <-done
}
```

```
# TestLeakyFunc 執行後輸出：
# --- FAIL: TestLeakyFunc
#     goleak.go:XX: found unexpected goroutines:
#     [Goroutine 7 in state sleep, with time.Sleep on top of the stack:...]
```

---

## 7. `dlv` (Delve) — Go 專用 Debugger ⭐

```bash
go install github.com/go-delve/delve/cmd/dlv@latest

dlv debug main.go         # 啟動調試
dlv attach <PID>          # 附加到執行中的程序
```

```
# Delve 常用指令
(dlv) goroutines          # 列出所有 goroutine
(dlv) goroutine 18        # 切換到指定 goroutine
(dlv) bt                  # 查看當前 goroutine stack trace
(dlv) goroutines -t       # 顯示所有 goroutine 的 stack trace
```

---

## 8. `context` 超時監控模式 ⭐

```go
// 用 context 偵測 goroutine 是否卡死
func doWork(ctx context.Context) error {
    done := make(chan struct{})
    go func() {
        // 實際工作...
        close(done)
    }()

    select {
    case <-done:
        return nil
    case <-ctx.Done():
        return fmt.Errorf("goroutine timeout: %w", ctx.Err())
    }
}

// 使用
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel()
if err := doWork(ctx); err != nil {
    log.Println("偵測到超時或卡死:", err)
}
```

---

## 9. `go test` 整合剖析 — 測試期間直接採樣

**安裝方式：** 內建，無需額外安裝

測試時直接生成剖析檔，是定位效能問題最直接的路徑。

```bash
# CPU 剖析 + Benchmark
go test -bench=. -benchmem -cpuprofile=cpu.prof ./...
go tool pprof cpu.prof

# Memory 剖析
go test -bench=. -memprofile=mem.prof ./...
go tool pprof -alloc_space mem.prof   # 查看所有分配（含已釋放）
go tool pprof -inuse_space mem.prof   # 查看當前佔用

# 執行追蹤（輸出給 go tool trace）
go test -trace=trace.out ./...
go tool trace trace.out

# Block 剖析（等待鎖/channel 的時間）
go test -blockprofile=block.prof ./...
go tool pprof block.prof

# Mutex 競爭剖析
go test -mutexprofile=mutex.prof ./...
go tool pprof mutex.prof

# 同時開多種剖析（一次跑完）
go test -bench=BenchmarkWorker -cpuprofile=cpu.prof -memprofile=mem.prof -trace=trace.out ./...
```

```bash
# pprof 互動式常用指令
go tool pprof cpu.prof
(pprof) top 10          # 前 10 個耗時函數
(pprof) top -cum        # 按累計時間排序（含子呼叫）
(pprof) list MyFunc     # 逐行顯示某函數的耗時
(pprof) web             # 生成 SVG 火焰圖（需 graphviz）
(pprof) png > out.png   # 輸出圖片
```

**可觀察：** 測試中的 CPU 熱點、記憶體分配來源、鎖競爭位置

---

## 10. `runtime/debug` + `runtime.Stack()` — 程式內 Stack Dump

**安裝方式：** 內建標準函式庫

```go
import (
    "fmt"
    "runtime"
    "runtime/debug"
)

// 印出當前 goroutine 的 stack（crash handler 常用）
func crashHandler() {
    debug.PrintStack()
}

// 抓取所有 goroutine 的 stack 到 buffer（true = 所有 goroutine）
func dumpAllGoroutines() {
    buf := make([]byte, 1<<20)  // 1 MB 緩衝區
    n := runtime.Stack(buf, true)
    fmt.Printf("=== goroutine dump ===\n%s\n", buf[:n])
}

// 設定最大 OS 執行緒數（預設 10000）
// 當 CGO 或 runtime.LockOSThread() 使用過多時會觸發 panic
debug.SetMaxThreads(1000)

// 調整 GC 觸發比例（預設 100，代表 heap 翻倍時觸發）
// 設為負值可完全關閉 GC（測試用途）
debug.SetGCPercent(50)   // 更頻繁 GC，降低記憶體峰值
debug.SetGCPercent(-1)   // 關閉 GC（危險！僅測試用）

// 強制執行一次 GC
runtime.GC()

// 取得 build 資訊（module 路徑、版本、依賴）
if info, ok := debug.ReadBuildInfo(); ok {
    fmt.Println("Module:", info.Main.Path)
}
```

```go
// 實用模式：程式收到 SIGQUIT 時 dump 所有 goroutine
import (
    "os"
    "os/signal"
    "syscall"
)

func init() {
    go func() {
        c := make(chan os.Signal, 1)
        signal.Notify(c, syscall.SIGQUIT)
        for range c {
            buf := make([]byte, 1<<20)
            n := runtime.Stack(buf, true)
            fmt.Fprintf(os.Stderr, "%s", buf[:n])
        }
    }()
}
// 觸發：kill -QUIT <PID>  或  Ctrl+\
```

**可觀察：** 所有 goroutine 當前 stack、GC 行為調整、執行緒上限控制

---

## 11. `expvar` — 輕量級即時監控

**安裝方式：** 內建標準函式庫

比 pprof 更輕量，適合生產環境持續暴露程式狀態，無需採樣開銷。

```go
import (
    "expvar"
    "net/http"
    "runtime"
    "time"
    _ "net/http/pprof"  // 同時掛載 pprof
)

// 宣告監控變數（全域）
var (
    goroutineCount = expvar.NewInt("goroutine_count")
    tasksDone      = expvar.NewInt("tasks_done")
    tasksFailed    = expvar.NewInt("tasks_failed")
    queueDepth     = expvar.NewInt("queue_depth")
    workerStatus   = expvar.NewMap("worker_status")  // key-value map
)

func worker(id int, jobs <-chan int) {
    workerStatus.Set(fmt.Sprintf("worker_%d", id), expvar.Func(func() any {
        return "running"
    }))
    for j := range jobs {
        _ = j
        tasksDone.Add(1)
    }
    workerStatus.Set(fmt.Sprintf("worker_%d", id), expvar.Func(func() any {
        return "idle"
    }))
}

func main() {
    // 定期更新 goroutine 計數
    go func() {
        for {
            goroutineCount.Set(int64(runtime.NumGoroutine()))
            time.Sleep(time.Second)
        }
    }()

    go http.ListenAndServe(":6060", nil)
    // 其餘程式...
}
```

```bash
# 查看所有指標（JSON 格式）
curl http://localhost:6060/debug/vars

# 輸出範例：
# {
#   "goroutine_count": 12,
#   "tasks_done": 1543,
#   "tasks_failed": 2,
#   "queue_depth": 8,
#   "worker_status": {"worker_0": "running", "worker_1": "idle"},
#   "memstats": {...}   ← expvar 自動包含記憶體統計
# }
```

**可觀察：** 自訂業務指標、即時 goroutine 數量、任務佇列深度，無額外 CPU 開銷

---

## 12. `go vet` — 靜態分析偵測併發陷阱

**安裝方式：** 內建，無需額外安裝

```bash
go vet ./...                    # 分析整個專案
go vet -v ./...                 # 顯示執行的分析器清單
go vet -composites=false ./...  # 關閉特定分析器
```

**常見偵測項目（與併發相關）：**

```go
// ❌ 1. sync.Mutex/sync.WaitGroup 被複製（傳值而非傳指標）
type Worker struct {
    mu sync.Mutex  // ← 若 Worker 被複製，go vet 會警告
}
func process(w Worker) { w.mu.Lock() }  // 警告：w contains sync.Mutex by value

// ✅ 修正：傳指標
func process(w *Worker) { w.mu.Lock() }

// ❌ 2. sync/atomic 操作對象未對齊（32-bit 系統）
type Counter struct {
    _ [0]func()
    n int64  // 必須 64-bit 對齊
}

// ❌ 3. goroutine 中使用 loop variable（Go 1.22 以前的常見 bug）
for i := 0; i < 5; i++ {
    go func() {
        fmt.Println(i)  // go vet 警告：loop variable i captured by func literal
    }()
}
// ✅ 修正（Go 1.22 以前）：
for i := 0; i < 5; i++ {
    i := i  // shadow 變數
    go func() { fmt.Println(i) }()
}

// ❌ 4. channel 方向性使用錯誤
func send(ch <-chan int) {
    ch <- 1  // go vet 警告：send on receive-only channel
}

// ❌ 5. context.WithCancel 洩漏（需搭配 staticcheck）
ctx, _ := context.WithCancel(parent)  // cancel 未儲存 → 資源洩漏
```

```bash
# 搭配 staticcheck 做更深入的靜態分析（第三方但業界標準）
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...
# 額外偵測：不必要的鎖、channel 死鎖模式、context 洩漏
```

**可觀察：** Mutex 複製、loop variable 捕獲、atomic 對齊問題、channel 方向性錯誤

---

## 工具選用速查表

| 問題場景 | 推薦工具 |
|---|---|
| Goroutine 執行順序異常 | `go tool trace` |
| 懷疑有 Data Race | `-race` |
| 鎖競爭嚴重，CPU 高 | `pprof mutex/block`、`go test -mutexprofile` |
| Goroutine 數量一直增長 | `goleak` + `runtime.NumGoroutine()` |
| 想暫停程序看 goroutine 狀態 | `dlv` |
| 生產環境即時監控 | `pprof HTTP endpoint` + `expvar` + `GODEBUG` |
| Goroutine 疑似卡死 | `context.WithTimeout` + `runtime.Stack()` |
| GC 暫停影響延遲 | `GODEBUG=gctrace=1` |
| Benchmark 效能問題 | `go test -cpuprofile` + `go test -trace` |
| 程式崩潰時抓 stack | `runtime.Stack()` + SIGQUIT handler |
| 程式碼靜態問題 | `go vet` + `staticcheck` |
| 低開銷業務指標監控 | `expvar` |

---

> 最常用的黃金組合：**`-race` + `pprof` + `go tool trace`**，三者涵蓋了從正確性到效能的完整調試需求。
>
> 生產環境推薦組合：**`expvar` + `pprof HTTP endpoint` + SIGQUIT `runtime.Stack()` handler**，零侵入持續可觀測。
