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

## 工具選用速查表

| 問題場景 | 推薦工具 |
|---|---|
| Goroutine 執行順序異常 | `go tool trace` |
| 懷疑有 Data Race | `-race` |
| 鎖競爭嚴重，CPU 高 | `pprof mutex/block` |
| Goroutine 數量一直增長 | `goleak` + `runtime.NumGoroutine()` |
| 想暫停程序看 goroutine 狀態 | `dlv` |
| 生產環境即時監控 | `pprof HTTP endpoint` + `GODEBUG` |
| Goroutine 疑似卡死 | `context.WithTimeout` + `pprof goroutine` |

---

> 最常用的黃金組合：**`-race` + `pprof` + `go tool trace`**，三者涵蓋了從正確性到效能的完整調試需求。
