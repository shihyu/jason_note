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
mkdir -p /tmp/go-trace-demo && cd /tmp/go-trace-demo
cat > main.go <<'EOF'
// 貼上上面的程式碼
EOF
go run main.go
go tool trace trace.out   # 開啟瀏覽器視覺化介面
```

**可觀察：** Goroutine 生命週期、阻塞原因、Syscall、Channel 操作、GC 事件

---

## 2. `pprof` — 效能剖析

```go
// pprof_demo.go
package main

import (
    "log"
    "net/http"
    _ "net/http/pprof"  // 自動註冊 /debug/pprof 端點
    "runtime"
    "sync"
    "time"
)

func main() {
    // 啟用 mutex / block profile（預設關閉）
    runtime.SetMutexProfileFraction(1)
    runtime.SetBlockProfileRate(1)

    var mu sync.Mutex
    ch := make(chan struct{})

    // 製造一點鎖競爭與阻塞，讓 /mutex、/block 有資料
    for i := 0; i < 4; i++ {
        go func() {
            for {
                mu.Lock()
                time.Sleep(10 * time.Millisecond)
                mu.Unlock()

                select {
                case ch <- struct{}{}:
                case <-time.After(5 * time.Millisecond):
                }
            }
        }()
    }

    go func() {
        log.Println("pprof listening on :6060")
        log.Println(http.ListenAndServe(":6060", nil))
    }()

    select {} // demo 用：保持程序存活
}
```

```bash
# 建議在獨立目錄操作
mkdir -p /tmp/go-pprof-demo && cd /tmp/go-pprof-demo
cat > pprof_demo.go <<'EOF'
// 貼上上面的程式碼
EOF
go run pprof_demo.go

# 另開一個 terminal 驗證端點
curl http://localhost:6060/debug/pprof/

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

# CPU 採樣（常用）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=10
```

`/debug/pprof/mutex` 與 `/debug/pprof/block` 需要先在程式內啟用（上方 `pprof_demo.go` 已包含）：

- `runtime.SetMutexProfileFraction(1)`
- `runtime.SetBlockProfileRate(1)`

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
mkdir -p /tmp/go-race-demo && cd /tmp/go-race-demo
cat > race_example.go <<'EOF'
// 貼上上面的程式碼
EOF
go run -race race_example.go
# 輸出：WARNING: DATA RACE，包含完整 goroutine stack trace

# 若要示範 go test -race，補一個最小 test 檔
go mod init example.com/race-demo
cat > race_example_test.go <<'EOF'
package main
import "testing"
func TestSmoke(t *testing.T) { main() }
EOF
go test -race ./...   # 對整個專案跑競態測試
```

---

## 4. `GODEBUG` 環境變數

先準備一個會持續配置記憶體與建立 goroutine 的範例，這樣 `schedtrace` / `gctrace` 才看得到輸出：

```go
// godebug_demo.go
package main

import (
    "bytes"
    "runtime"
    "time"
)

func main() {
    jobs := make(chan []byte, 1024)

    for i := 0; i < 4; i++ {
        go func() {
            for b := range jobs {
                _ = bytes.Count(b, []byte{1})
                time.Sleep(2 * time.Millisecond)
            }
        }()
    }

    for i := 0; i < 200000; i++ {
        b := make([]byte, 32*1024) // 製造 GC 壓力
        jobs <- b
        if i%1000 == 0 {
            runtime.Gosched()
        }
    }
    close(jobs)
    time.Sleep(2 * time.Second)
}
```

```bash
# 建議在獨立目錄操作
mkdir -p /tmp/go-godebug-demo && cd /tmp/go-godebug-demo
cat > godebug_demo.go <<'EOF'
// 貼上上面的程式碼
EOF

# schedtrace：每 500ms 輸出 Scheduler 狀態
GODEBUG=schedtrace=500 go run godebug_demo.go
# 輸出格式（Go 1.21+）：
# SCHED 0ms: gomaxprocs=8 idleprocs=6 threads=5 spinningthreads=1 needspinning=0 idlethreads=0 runqueue=0 [0 0 0 0 0 0 0 0]
# 欄位說明：spinningthreads=自旋中執行緒, needspinning=需要自旋, idlethreads=閒置執行緒

# scheddetail：更詳細的 goroutine 狀態（加上 gcwaiting/stopwait 等 GC 欄位）
GODEBUG=schedtrace=1000,scheddetail=1 go run godebug_demo.go

# asyncpreemptoff=1：關閉異步搶占（調試特定問題用）
GODEBUG=asyncpreemptoff=1 go run godebug_demo.go

# gctrace=1：每次 GC 輸出一行摘要，觀察 STW 暫停對併發的影響
GODEBUG=gctrace=1 go run godebug_demo.go
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
go mod init example.com/godebug-demo
cat > godebug_demo_test.go <<'EOF'
package main
import "testing"
func TestSmoke(t *testing.T) {}
EOF
GODEBUG=gccheckmark=1 go test ./...
```

---

## 5. `runtime` 套件 — 程式內部監控

```go
// runtime_stats.go
package main

import (
    "fmt"
    "runtime"
)

func printStats() {
    fmt.Println("Goroutine 數量:", runtime.NumGoroutine())
    fmt.Println("CPU 核心數:", runtime.NumCPU())
    fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))

    var ms runtime.MemStats
    runtime.ReadMemStats(&ms)
    fmt.Printf("Heap 使用: %v MB\n", ms.HeapAlloc/1024/1024)
}

func main() {
    printStats()
}
```

```bash
mkdir -p /tmp/go-runtime-demo && cd /tmp/go-runtime-demo
cat > runtime_stats.go <<'EOF'
// 貼上上面的程式碼
EOF
go run runtime_stats.go
```

---

## 6. `goleak` — Goroutine 洩漏偵測 ⭐

```bash
mkdir -p /tmp/go-goleak-demo && cd /tmp/go-goleak-demo
go mod init example.com/goleak-demo
go get go.uber.org/goleak   # 需在 go module 專案內執行
cat > leak_test.go <<'EOF'
// 貼上下面的 leak_test.go
EOF
```

```go
// leak_test.go
package leakdemo

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

```bash
# 先看失敗案例（會看到 goleak 報告）
go test -run TestLeakyFunc -v

# 再看正常案例（會通過）
go test -run TestCleanFunc -v
```

```
# TestLeakyFunc 執行後輸出：
# --- FAIL: TestLeakyFunc
#     goleak.go:XX: found unexpected goroutines:
#     [Goroutine 7 in state sleep, with time.Sleep on top of the stack:...]
```

---

## 7. `dlv` (Delve) — Go 專用 Debugger ⭐

```go
// dlv_demo.go
package main

import (
    "fmt"
    "time"
)

func worker(id int) {
    for i := 0; i < 3; i++ {
        fmt.Printf("worker=%d i=%d\n", id, i)
        time.Sleep(500 * time.Millisecond)
    }
}

func main() {
    go worker(1)
    worker(0)
}
```

```bash
mkdir -p /tmp/go-dlv-demo && cd /tmp/go-dlv-demo
go mod init example.com/dlv-demo
cat > dlv_demo.go <<'EOF'
// 貼上上面的程式碼
EOF

go install github.com/go-delve/delve/cmd/dlv@latest

dlv debug .               # 啟動調試
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
// context_timeout.go
package main

import (
    "context"
    "fmt"
    "log"
    "time"
)

// 用 context 偵測 goroutine 是否卡死
func doWork(ctx context.Context) error {
    done := make(chan struct{})
    go func() {
        // 實際工作...
        time.Sleep(10 * time.Second) // 故意超過 timeout
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
func main() {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := doWork(ctx); err != nil {
        log.Println("偵測到超時或卡死:", err)
    }
}
```

```bash
mkdir -p /tmp/go-context-demo && cd /tmp/go-context-demo
cat > context_timeout.go <<'EOF'
// 貼上上面的程式碼
EOF
go run context_timeout.go
# 預期輸出：偵測到超時或卡死: goroutine timeout: context deadline exceeded
```

---

## 9. `go test` 整合剖析 — 測試期間直接採樣

**安裝方式：** 內建，無需額外安裝

測試時直接生成剖析檔，是定位效能問題最直接的路徑。

```go
// profile_bench_test.go
package profiledemo

import (
    "crypto/sha256"
    "fmt"
    "testing"
)

func worker(n int) [32]byte {
    return sha256.Sum256([]byte(fmt.Sprintf("job-%d", n)))
}

func BenchmarkWorker(b *testing.B) {
    for i := 0; i < b.N; i++ {
        _ = worker(i)
    }
}

func TestWorker(t *testing.T) {
    got := worker(1)
    if got == ([32]byte{}) {
        t.Fatal("unexpected zero hash")
    }
}
```

```bash
mkdir -p /tmp/go-test-profile-demo && cd /tmp/go-test-profile-demo
go mod init example.com/profile-demo
cat > profile_bench_test.go <<'EOF'
// 貼上上面的程式碼
EOF

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
// stack_dump_demo.go
package main

import (
    "fmt"
    "os"
    "os/signal"
    "runtime"
    "runtime/debug"
    "syscall"
    "time"
)

// 印出當前 goroutine 的 stack（crash handler 常用）
func crashHandler() {
    debug.PrintStack()
}

// 抓取所有 goroutine 的 stack 到 buffer（true = 所有 goroutine）
func dumpAllGoroutines() {
    buf := make([]byte, 1<<20) // 1 MB 緩衝區
    n := runtime.Stack(buf, true)
    fmt.Printf("=== goroutine dump ===\n%s\n", buf[:n])
}

// 實用模式：程式收到 SIGQUIT 時 dump 所有 goroutine
func installSIGQUITDump() {
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

func main() {
    installSIGQUITDump()

    // 設定最大 OS 執行緒數（預設 10000）
    // 當 CGO 或 runtime.LockOSThread() 使用過多時會觸發 panic
    debug.SetMaxThreads(1000)

    // 調整 GC 觸發比例（預設 100，代表 heap 翻倍時觸發）
    debug.SetGCPercent(50)

    // 製造一些 goroutine，方便 dump
    for i := 0; i < 3; i++ {
        go func(id int) {
            for {
                time.Sleep(2 * time.Second)
                fmt.Println("worker", id, "alive")
            }
        }(i)
    }

    time.Sleep(200 * time.Millisecond)
    crashHandler()
    dumpAllGoroutines()
    runtime.GC()

    if info, ok := debug.ReadBuildInfo(); ok {
        fmt.Println("Module:", info.Main.Path)
    }

    fmt.Println("PID:", os.Getpid(), "（可用 kill -QUIT <PID> 再次 dump）")
    select {}
}
```

```bash
mkdir -p /tmp/go-stackdump-demo && cd /tmp/go-stackdump-demo
cat > stack_dump_demo.go <<'EOF'
// 貼上上面的程式碼
EOF
go run stack_dump_demo.go

# 另開 terminal（Linux/macOS）
kill -QUIT <PID>
# 或在前景程式按 Ctrl+\
```

**可觀察：** 所有 goroutine 當前 stack、GC 行為調整、執行緒上限控制

---

## 11. `expvar` — 輕量級即時監控

**安裝方式：** 內建標準函式庫

比 pprof 更輕量，適合生產環境持續暴露程式狀態，無需採樣開銷。

```go
// expvar_demo.go
package main

import (
    "fmt"
    "expvar"
    "log"
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
    jobs := make(chan int, 16)

    for i := 0; i < 2; i++ {
        go worker(i, jobs)
    }

    go func() {
        for i := 0; ; i++ {
            jobs <- i
            queueDepth.Set(int64(len(jobs)))
            if i%10 == 0 {
                tasksFailed.Add(1) // demo 用：模擬少量失敗
            }
            time.Sleep(100 * time.Millisecond)
        }
    }()

    // 定期更新 goroutine 計數
    go func() {
        for {
            goroutineCount.Set(int64(runtime.NumGoroutine()))
            queueDepth.Set(int64(len(jobs)))
            time.Sleep(time.Second)
        }
    }()

    log.Println("expvar + pprof listening on :6060")
    log.Fatal(http.ListenAndServe(":6060", nil))
}
```

```bash
mkdir -p /tmp/go-expvar-demo && cd /tmp/go-expvar-demo
cat > expvar_demo.go <<'EOF'
// 貼上上面的程式碼
EOF
go run expvar_demo.go

# 另開 terminal
# 查看所有指標（JSON 格式）
curl http://localhost:6060/debug/vars
curl -s http://localhost:6060/debug/vars | jq
curl -s http://localhost:6060/debug/vars | jq '.goroutine_count, .tasks_done, .worker_status'

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
mkdir -p /tmp/go-vet-demo && cd /tmp/go-vet-demo
go mod init example.com/vet-demo

go vet ./...                    # 分析整個專案
go vet -v ./...                 # 顯示執行的分析器清單
go vet -composites=false ./...  # 關閉特定分析器
```

**常見偵測項目（與併發相關）：**

```go
// copylocks_demo.go
package vetdemo

import "sync"

// ❌ sync.Mutex 被複製（傳值）會觸發 go vet 的 copylocks
type Worker struct {
    mu sync.Mutex
}

func process(w Worker) { // go vet: passes lock by value
    w.mu.Lock()
    defer w.mu.Unlock()
}

// ✅ 修正：傳指標
func processPtr(w *Worker) {
    w.mu.Lock()
    defer w.mu.Unlock()
}
```

```go
// lostcancel_demo.go
package vetdemo

import "context"

// ❌ 未呼叫 cancel，會觸發 go vet 的 lostcancel
func leakedContext(parent context.Context) context.Context {
    ctx, _ := context.WithCancel(parent)
    return ctx
}
```

```go
// compile_error_channel_direction.go（示意：這是編譯期錯誤，不是 go vet）
package main

func send(ch <-chan int) {
    ch <- 1 // compile error: send to receive-only channel
}
```

```bash
# 先建立可被 go vet 偵測的檔案
cat > copylocks_demo.go <<'EOF'
// 貼上 copylocks_demo.go
EOF
cat > lostcancel_demo.go <<'EOF'
// 貼上 lostcancel_demo.go
EOF
go vet ./...
# 預期可看到 copylocks / lostcancel 類型警告

# 再測試編譯期錯誤例子（分開放，避免干擾 go vet 示範）
mkdir -p compileerr && cd compileerr
cat > main.go <<'EOF'
// 貼上 compile_error_channel_direction.go
EOF
go mod init example.com/compileerr
go build ./...
# 預期：send to receive-only channel
cd ..

# 搭配 staticcheck 做更深入的靜態分析（第三方但業界標準）
go install honnef.co/go/tools/cmd/staticcheck@latest
staticcheck ./...
# 額外偵測：更多 code smell、部分併發誤用模式、context 洩漏
```

**可觀察：** Mutex 複製、lost cancel、部分併發誤用模式（另有編譯期錯誤示例）

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
