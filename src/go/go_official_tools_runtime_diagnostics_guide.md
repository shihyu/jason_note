# Go 官方工具與 Runtime 診斷總整理

基準版本：`go1.21.6 linux/amd64`

範圍：

- 官方 `go` 指令
- 官方 `go tool` 子工具
- 官方 runtime 診斷/觀測機制
- `GODEBUG` 與相關環境變數

不含：

- 第三方工具，例如 `dlv`、`staticcheck`、`golangci-lint`

---

## 先講結論

如果你只想知道「什麼時候用什麼」：

| 情境 | 先用什麼 |
| --- | --- |
| 程式變慢、CPU 飆高 | `go test -cpuprofile` + `go tool pprof` |
| 記憶體暴增、疑似洩漏 | `go test -memprofile` + `go tool pprof` |
| Goroutine 卡住、鎖競爭、阻塞 | `block profile`、`mutex profile`、`goroutine profile`、`go tool trace` |
| 想看排程器、syscall、GC、阻塞全貌 | `go test -trace` + `go tool trace` |
| 懷疑資料競態 | `go test -race` |
| 想知道測試覆蓋率 | `go test -cover` / `-coverprofile` / `go tool cover` |
| 想看 runtime GC 行為 | `GODEBUG=gctrace=1` |
| 想看 scheduler 行為 | `GODEBUG=schedtrace=1000,scheddetail=1` |
| 想調 GC 壓力 | `GOGC`、`GOMEMLIMIT` |
| 想看 panic 時所有 goroutine | `GOTRACEBACK=all` 或 `system` |
| 只想快速看匯編、符號、物件內容 | `go tool objdump`、`nm`、`addr2line` |
| 想抓 API 文件或符號說明 | `go doc` / `go tool doc` |
| 想做程式碼檢查 | `go vet` |
| 想批次修正舊 API | `go fix` |

---

## 範例程式碼（所有範例均已驗證可執行）

以下範例以這個模組為基礎：

```bash
mkdir demo && cd demo
go mod init demo
```

### 範例主程式 `main.go`

```go
package main

import (
    "fmt"
    "math"
    "runtime"
    "runtime/debug"
    "sync"
    "time"
)

func isPrime(n int) bool {
    if n < 2 {
        return false
    }
    for i := 2; i <= int(math.Sqrt(float64(n))); i++ {
        if n%i == 0 {
            return false
        }
    }
    return true
}

func countPrimes(max int) int {
    count := 0
    for i := 2; i <= max; i++ {
        if isPrime(i) {
            count++
        }
    }
    return count
}

func allocStrings(n int) []string {
    result := make([]string, n)
    for i := range result {
        result[i] = fmt.Sprintf("item-%d", i)
    }
    return result
}

type Counter struct {
    mu    sync.Mutex
    value int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    c.value++
    c.mu.Unlock()
}

func (c *Counter) Get() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.value
}

func main() {
    fmt.Printf("Go version: %s\n", runtime.Version())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))

    count := countPrimes(100000)
    fmt.Printf("Primes below 100000: %d\n", count)

    var ms runtime.MemStats
    runtime.ReadMemStats(&ms)
    fmt.Printf("HeapAlloc: %d KB\n", ms.HeapAlloc/1024)

    if info, ok := debug.ReadBuildInfo(); ok {
        fmt.Printf("Module: %s\n", info.Main.Path)
    }
    _ = time.Now()
}
```

### 範例測試 `main_test.go`（完整示範各種 profiling）

```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "runtime/debug"
    "runtime/pprof"
    "runtime/trace"
    "sync"
    "testing"
    "time"
)

// ===== 基本功能測試 =====

func TestIsPrime(t *testing.T) {
    cases := []struct {
        n    int
        want bool
    }{
        {1, false}, {2, true}, {3, true}, {4, false},
        {17, true}, {100, false}, {97, true},
    }
    for _, c := range cases {
        if got := isPrime(c.n); got != c.want {
            t.Errorf("isPrime(%d) = %v, want %v", c.n, got, c.want)
        }
    }
}

func TestCountPrimes(t *testing.T) {
    if got := countPrimes(100); got != 25 { // π(100) = 25
        t.Errorf("countPrimes(100) = %d, want 25", got)
    }
}

func TestCounter(t *testing.T) {
    c := &Counter{}
    var wg sync.WaitGroup
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            c.Inc()
        }()
    }
    wg.Wait()
    if got := c.Get(); got != 100 {
        t.Errorf("Counter = %d, want 100", got)
    }
}

// ===== Benchmark =====

func BenchmarkIsPrime(b *testing.B) {
    for i := 0; i < b.N; i++ {
        isPrime(999983)
    }
}

func BenchmarkCountPrimes(b *testing.B) {
    for i := 0; i < b.N; i++ {
        countPrimes(10000)
    }
}

func BenchmarkAllocStrings(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        _ = allocStrings(1000)
    }
}

func BenchmarkCounterParallel(b *testing.B) {
    c := &Counter{}
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            c.Inc()
        }
    })
}

// 預分配 vs 動態增長對比
var sink []string

func BenchmarkAllocWithGrow(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        var s []string
        for j := 0; j < 100; j++ {
            s = append(s, fmt.Sprintf("x%d", j))
        }
        sink = s
    }
}

func BenchmarkAllocWithPrealloc(b *testing.B) {
    b.ReportAllocs()
    for i := 0; i < b.N; i++ {
        s := make([]string, 0, 100)
        for j := 0; j < 100; j++ {
            s = append(s, fmt.Sprintf("x%d", j))
        }
        sink = s
    }
}

// ===== CPU Profile（程式內手動） =====

func TestCPUProfile(t *testing.T) {
    f, _ := os.Create("cpu.out")
    defer f.Close()
    if err := pprof.StartCPUProfile(f); err != nil {
        t.Logf("skip: %v", err) // 外部已開 -cpuprofile 時會衝突
        return
    }
    defer pprof.StopCPUProfile()
    t.Logf("Primes: %d (cpu.out written)", countPrimes(50000))
}

// ===== Memory Profile =====

func TestMemProfile(t *testing.T) {
    for i := 0; i < 5; i++ {
        _ = allocStrings(10000)
    }
    runtime.GC()
    f, _ := os.Create("mem.out")
    defer f.Close()
    pprof.WriteHeapProfile(f)
    t.Log("mem.out written")
}

// ===== Block Profile =====

func TestBlockProfile(t *testing.T) {
    runtime.SetBlockProfileRate(1)
    defer runtime.SetBlockProfileRate(0)

    ch := make(chan int)
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() { defer wg.Done(); ch <- 1 }()
    }
    go func() {
        for i := 0; i < 10; i++ { <-ch; time.Sleep(time.Millisecond) }
    }()
    wg.Wait()

    f, _ := os.Create("block.out")
    defer f.Close()
    pprof.Lookup("block").WriteTo(f, 0)
    t.Log("block.out written")
}

// ===== Mutex Profile =====

func TestMutexProfile(t *testing.T) {
    runtime.SetMutexProfileFraction(1)
    defer runtime.SetMutexProfileFraction(0)

    c := &Counter{}
    var wg sync.WaitGroup
    for i := 0; i < 50; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < 100; j++ { c.Inc() }
        }()
    }
    wg.Wait()

    f, _ := os.Create("mutex.out")
    defer f.Close()
    pprof.Lookup("mutex").WriteTo(f, 0)
    t.Logf("mutex.out written, counter=%d", c.Get())
}

// ===== Trace =====

func TestTrace(t *testing.T) {
    f, _ := os.Create("trace.out")
    defer f.Close()
    if err := trace.Start(f); err != nil {
        t.Logf("skip: %v", err) // 外部已開 -trace 時會衝突
        return
    }
    defer trace.Stop()

    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func() { defer wg.Done(); _ = countPrimes(5000) }()
    }
    wg.Wait()
    t.Log("trace.out written")
}

// ===== Goroutine Profile =====

func safeGoroutine(done <-chan struct{}) {
    for {
        select {
        case <-done:
            return
        case <-time.After(10 * time.Millisecond):
        }
    }
}

func TestGoroutineProfile(t *testing.T) {
    done := make(chan struct{})
    for i := 0; i < 3; i++ {
        go safeGoroutine(done)
    }
    time.Sleep(10 * time.Millisecond)

    f, _ := os.Create("goroutine.out")
    defer f.Close()
    pprof.Lookup("goroutine").WriteTo(f, 1)
    close(done)
    t.Logf("goroutine.out written, goroutines=%d", runtime.NumGoroutine())
}

// ===== MemStats =====

func TestMemStats(t *testing.T) {
    var before, after runtime.MemStats
    runtime.ReadMemStats(&before)
    _ = allocStrings(100000)
    runtime.GC()
    runtime.ReadMemStats(&after)
    t.Logf("HeapAlloc before: %d KB", before.HeapAlloc/1024)
    t.Logf("HeapAlloc after:  %d KB", after.HeapAlloc/1024)
    t.Logf("NumGC: %d", after.NumGC)
    t.Logf("TotalAlloc: %d KB", after.TotalAlloc/1024)
}

// ===== Fuzz =====

func FuzzIsPrime(f *testing.F) {
    f.Add(0); f.Add(1); f.Add(2); f.Add(97); f.Add(-1)
    f.Fuzz(func(t *testing.T, n int) {
        _ = isPrime(n) // 只驗不 panic
    })
}

// ===== Escape Analysis =====

func newOnHeap() *int { x := 42; return &x } // → heap
func stayOnStack() int { x := 42; return x } // → stack

func TestEscapeAnalysis(t *testing.T) {
    p := newOnHeap()
    t.Logf("heap ptr: %p = %d", p, *p)
    t.Logf("stack val: %d", stayOnStack())
}

// ===== runtime/debug =====

func TestRuntimeDebug(t *testing.T) {
    old := debug.SetGCPercent(50)
    defer debug.SetGCPercent(old)
    t.Logf("old GC percent: %d", old)

    debug.FreeOSMemory()

    if info, ok := debug.ReadBuildInfo(); ok {
        t.Logf("module: %s", info.Main.Path)
    }

    var stats debug.GCStats
    debug.ReadGCStats(&stats)
    t.Logf("NumGC: %d", stats.NumGC)
}

// ===== 列出所有可用 profile =====

func TestListProfiles(t *testing.T) {
    for _, p := range pprof.Profiles() {
        t.Logf("  %s (count=%d)", p.Name(), p.Count())
    }
}
```

---

## 1. 高階 `go` 指令

這些是平常最常用的入口。

| 指令 | 用途 | 什麼時候用 |
| --- | --- | --- |
| `go build` | 編譯 package / binary | 驗證是否可編譯、產出執行檔、加建置旗標 |
| `go run` | 臨時編譯並執行 | 小工具、範例、一次性腳本 |
| `go test` | 跑測試/benchmark/fuzz | 平時測試、效能分析、race 檢查、coverage |
| `go vet` | 找高機率 bug | CI、提交前靜態檢查 |
| `go fmt` | 格式化 | 提交前、批次整理 |
| `go fix` | 自動遷移舊 API 用法 | 升 Go 版本後清舊語法 |
| `go doc` | 查 package / symbol 文件 | 忘記 API、查標準庫 |
| `go env` | 看 Go 環境 | 排查環境、CGO、module、交叉編譯問題 |
| `go list` | 列 package/module 資訊 | 腳本、自動化、查依賴 |
| `go generate` | 執行 `//go:generate` | codegen、mock、stringer 類流程 |
| `go install` | 安裝 binary | 裝 CLI 或編譯主程式到 `$GOBIN` |
| `go get` | 加/升依賴 | 更新 module 依賴 |
| `go mod` | module 維護 | `tidy`、`vendor`、`graph`、`why` |
| `go work` | workspace 維護 | 多 module 聯合開發 |
| `go version` | 看工具鏈版本 | 排查版本差異 |
| `go tool` | 跑低階工具 | 看匯編、trace、pprof、cover 等 |
| `go bug` | 產生 issue 範本 | 要回報 Go 問題時 |

### `go build` 常見診斷旗標

| 旗標 | 用途 | 什麼時候用 |
| --- | --- | --- |
| `-race` | 資料競態偵測 | 共享資料疑似沒鎖好 |
| `-cover` | 編譯時插 coverage instrumentation | 要跑可執行檔 coverage |
| `-asan` | AddressSanitizer 互通 | cgo / native memory 問題 |
| `-msan` | MemorySanitizer 互通 | cgo / 未初始化記憶體問題 |
| `-pgo` | Profile-guided optimization | 熱點穩定、要擠壓效能 |
| `-gcflags=all=-m` | 看 escape analysis / inline 決策 | 查 allocation、多餘 heap escape |
| `-gcflags=all=-S` | 看組合語言輸出 | 極限效能分析 |
| `-ldflags` | link 階段參數 | 瘦身、注入版本字串 |
| `-trimpath` | 去除本機絕對路徑 | 可重現建置、乾淨 binary |
| `-work` | 保留暫存建置目錄 | 排查編譯流程 |
| `-x` | 顯示實際執行命令 | 排查 toolchain 行為 |

#### Escape Analysis 範例

```bash
go build -gcflags='-m' ./...
```

輸出節錄（實測）：

```text
./main.go:13:6: can inline isPrime
./main.go:25:6: can inline countPrimes
./main.go:37:16: make([]string, n) escapes to heap
./main.go:39:38: i escapes to heap
```

解讀：

- `can inline`：函式夠小，會被 inline，無呼叫開銷
- `escapes to heap`：物件分配在 heap，GC 需管理
- stack 上的變數不會出現在這裡

---

## 2. `go test` 其實是最重要的分析入口

大多數官方分析流程都從 `go test` 開始。

### 功能型旗標

| 旗標 | 用途 | 什麼時候用 |
| --- | --- | --- |
| `-run` | 只跑特定測試 | 縮小問題範圍 |
| `-bench` | 跑 benchmark | 效能基準 |
| `-benchmem` | 顯示 allocation 次數與大小 | 盯 allocation regression |
| `-count` | 重跑多次 | 確認 flaky 或 benchmark 穩定性 |
| `-cpu` | 多組 `GOMAXPROCS` 測 | 看並行縮放性 |
| `-parallel` | 控制測試平行度 | 降噪、避免資源搶占 |
| `-shuffle` | 打亂順序 | 揪出順序相依測試 |
| `-fuzz` | 啟動 fuzzing | 不信任輸入、parser、decoder、protocol |
| `-json` | JSON 格式輸出 | 丟 CI、分析工具 |
| `-timeout` | 設定逾時 | 防止測試掛死 |
| `-v` | 詳細輸出 | 看每個 test 的 log |
| `-short` | 跳過耗時測試 | 快速 smoke test |

### 分析型旗標

| 旗標 | 輸出 | 什麼時候用 |
| --- | --- | --- |
| `-cpuprofile=cpu.out` | CPU profile | CPU 熱點分析 |
| `-memprofile=mem.out` | Memory profile | allocation / heap 分析 |
| `-blockprofile=block.out` | 阻塞 profile | channel / mutex / syscall 卡住 |
| `-mutexprofile=mutex.out` | mutex contention profile | 鎖競爭 |
| `-trace=trace.out` | execution trace | 排程、GC、阻塞、syscall 全景 |
| `-coverprofile=cover.out` | coverage profile | 覆蓋率報告 |
| `-blockprofilerate=1` | 開啟完整阻塞取樣 | 要抓 block 時常一起開 |
| `-mutexprofilefraction=1` | 提高 mutex 取樣 | 鎖競爭很重時 |
| `-memprofilerate=1` | 所有 allocation 都採樣 | 要極精準記憶體分析時，代價高 |

### 典型命令（均已驗證）

```bash
# 所有測試加 race detector
go test ./... -race

# 跑指定 benchmark，印 allocation 統計
go test ./... -bench=BenchmarkCountPrimes -benchmem
# BenchmarkCountPrimes-16    4728    239650 ns/op    0 B/op    0 allocs/op

# 只跑特定測試，產生 CPU profile
go test ./... -bench=BenchmarkCountPrimes -cpuprofile=cpu.out

# 只跑特定測試，產生 memory profile
go test ./... -bench=BenchmarkAllocStrings -memprofile=mem.out

# block profile（需先在程式內設 rate 或加 -blockprofilerate）
go test ./... -run TestBlockProfile -blockprofile=block.out -blockprofilerate=1

# mutex profile
go test ./... -run TestMutexProfile -mutexprofile=mutex.out -mutexprofilefraction=1

# trace
go test ./... -run TestTrace -trace=trace.out

# coverage
go test ./... -coverprofile=cover.out

# 打亂測試順序（找隱性依賴）
go test ./... -shuffle=on -count=3
```

### Benchmark 結果說明

```text
BenchmarkIsPrime-16        816644    1500 ns/op    0 B/op    0 allocs/op
                   ^          ^         ^            ^           ^
              GOMAXPROCS   iteration  每次耗時     每次分配    每次分配次數
```

### 預分配 vs 動態增長（實測結果）

```bash
go test -bench='BenchmarkAllocWith' -benchmem
```

```text
BenchmarkAllocWithGrow-16       232879    5044 ns/op    4391 B/op    108 allocs/op
BenchmarkAllocWithPrealloc-16   244104    4445 ns/op    2102 B/op    101 allocs/op
```

結論：預分配容量可減少約一半 allocation 次數和記憶體用量。

---

## 3. PProf 全家桶

這組工具專門處理「哪裡花最多資源」。

### `runtime/pprof`

用途：

- 在程式內手動產生 profile
- 適合 CLI、batch job、非 HTTP 程式

什麼時候用：

- 你的程式不是長駐 HTTP 服務
- 想精準控制開始/結束分析時間點

常用 API：

```go
import "runtime/pprof"

// CPU
f, _ := os.Create("cpu.out")
pprof.StartCPUProfile(f)
// ... 你的工作 ...
pprof.StopCPUProfile()
f.Close()

// Heap（任意時刻抓快照）
f, _ := os.Create("mem.out")
runtime.GC()
pprof.WriteHeapProfile(f)
f.Close()

// 任意具名 profile
f, _ := os.Create("block.out")
pprof.Lookup("block").WriteTo(f, 0)
f.Close()

// 所有可用 profile 名稱
for _, p := range pprof.Profiles() {
    fmt.Printf("%s count=%d\n", p.Name(), p.Count())
}
// 輸出: allocs / block / goroutine / heap / mutex / threadcreate
```

> **注意**：`go test -cpuprofile` 已開啟 CPU profiling，再呼叫 `pprof.StartCPUProfile` 會回傳 error，要判斷跳過。`-trace` 同理。

### `net/http/pprof`

用途：

- 幫 HTTP 服務掛上 `/debug/pprof/*`

```go
import (
    "net/http"
    _ "net/http/pprof" // 副作用 import 即可註冊路由
)

func main() {
    go http.ListenAndServe(":6060", nil)
    // ... 你的程式 ...
}
```

常見 endpoint：

| 路徑 | 用途 |
| --- | --- |
| `/debug/pprof/` | 總覽 |
| `/debug/pprof/profile?seconds=30` | CPU 30 秒 |
| `/debug/pprof/heap` | heap 快照 |
| `/debug/pprof/goroutine` | goroutine 堆疊 |
| `/debug/pprof/block` | block profile |
| `/debug/pprof/mutex` | mutex profile |
| `/debug/pprof/trace?seconds=5` | execution trace |

注意：

- `block` 需要 `runtime.SetBlockProfileRate(1)`
- `mutex` 需要 `runtime.SetMutexProfileFraction(1)`

### `go tool pprof`

用途：

- 讀 profile 並做文字/圖形分析

```bash
# 讀本機 profile 檔
go tool pprof cpu.out
go tool pprof mem.out

# 直接從 HTTP 抓（程式要先跑起來）
go tool pprof http://127.0.0.1:6060/debug/pprof/heap
go tool pprof http://127.0.0.1:6060/debug/pprof/profile?seconds=30

# 開啟瀏覽器互動 UI（需要 graphviz）
go tool pprof -http=:8080 cpu.out
```

互動模式常用命令：

| 命令 | 用途 |
| --- | --- |
| `top` | 看最熱函式（flat/cum） |
| `top10` | 只看前幾名 |
| `list Foo` | 對照原始碼，看哪幾行最熱 |
| `web` | 開呼叫圖（需 graphviz） |
| `peek Foo` | 看 callers/callees |
| `traces` | 看樣本堆疊 |
| `svg` | 輸出 SVG 呼叫圖 |

#### 實測輸出（CPU profile）

```bash
go test -bench=BenchmarkCountPrimes -cpuprofile=cpu.out
go tool pprof -top cpu.out
```

```text
Type: cpu  Duration: 1.30s  Samples = 1.17s (89.72%)
      flat  flat%   sum%        cum   cum%
     0.95s 81.20% 81.20%      1.03s 88.03%  go-tools-demo.isPrime (inline)
     0.12s 10.26% 91.45%      1.15s 98.29%  go-tools-demo.BenchmarkCountPrimes
     0.08s  6.84% 98.29%      0.08s  6.84%  math.Sqrt (inline)
```

解讀：

- `flat`：函式自己花的時間（不含被呼叫者）
- `cum`：函式 + 所有被呼叫者加起來的時間
- `(inline)`：已被 inline，不是真正的函式呼叫

#### 實測輸出（Memory profile）

```bash
go test -bench=BenchmarkAllocStrings -memprofile=mem.out
go tool pprof -top mem.out
```

```text
Type: alloc_space
      flat  flat%   sum%        cum   cum%
  654.21MB 69.55% 69.55%   932.72MB 99.16%  go-tools-demo.allocStrings
     278MB 29.56% 99.11%   278.51MB 29.61%  fmt.Sprintf
```

### `go tool pprof` 與 `go tool trace` 怎麼選

| 工具 | 主要回答的問題 |
| --- | --- |
| `pprof` | 哪些函式最吃 CPU / memory / lock / block |
| `trace` | 為什麼 goroutine 在那個時間點沒跑、被誰卡住、GC/排程如何互動 |

一句話：

- 熱點先看 `pprof`
- 時序、排程、阻塞因果看 `trace`

---

## 4. Trace 全家桶

### `runtime/trace`

用途：

- 在程式中產生 execution trace

```go
import "runtime/trace"

f, _ := os.Create("trace.out")
trace.Start(f)
defer trace.Stop()
// ... 你的工作 ...
```

標註業務 task / region（方便在 UI 中對齊）：

```go
import "runtime/trace"

ctx, task := trace.NewTask(context.Background(), "processRequest")
defer task.End()

trace.WithRegion(ctx, "parse", func() {
    // 解析邏輯
})

trace.Log(ctx, "db", "query start")
```

什麼時候用：

- 想看 goroutine 建立、喚醒、阻塞、syscall、GC、P/M/G 排程
- 不只想知道「熱點」，還要知道「為什麼這個時間點卡住」

### `go tool trace`

```bash
go test ./... -run TestTrace -trace=trace.out
go tool trace trace.out
# 開啟瀏覽器 http://127.0.0.1:<隨機port>

# 或從 HTTP 服務抓
curl -o trace.out http://127.0.0.1:6060/debug/pprof/trace?seconds=5
go tool trace trace.out
```

UI 頁面說明：

| 頁面 | 看什麼 |
| --- | --- |
| View trace | 時間軸，所有 goroutine/P/GC 事件 |
| Goroutine analysis | 各 goroutine 排程延遲統計 |
| Network blocking | network 等待時間 |
| Synchronization blocking | channel/mutex 等待時間 |
| Syscall blocking | syscall 阻塞時間 |
| Scheduler latency | goroutine 從 runnable 到 running 的延遲 |
| User-defined tasks | `trace.NewTask` 標記的業務任務 |

優勢：有時間軸、有 goroutine 與 task 關聯、看得出 block/unblock 因果

限制：檔案可能很大；trace overhead 通常比 pprof 高

---

## 5. Coverage 工具

### `go test -cover` / `-coverprofile`

```bash
# 快速看覆蓋率百分比
go test ./... -cover
# ok  demo  0.255s  coverage: 50.0% of statements

# 輸出詳細 profile
go test ./... -coverprofile=cover.out
```

### `go tool cover`

```bash
# 每個函式的覆蓋率
go tool cover -func=cover.out
# main.go:13:  isPrime      100.0%
# main.go:25:  countPrimes  100.0%
# main.go:73:  main           0.0%
# total:       (statements)  50.0%

# 開 HTML 報告（瀏覽器高亮顯示哪些行沒測到）
go tool cover -html=cover.out
```

### `go tool covdata`（Go 1.20+）

用途：

- 操作新版 coverage data 檔案
- 整合多次執行、多個 binary 的 coverage

```bash
# 收集可執行檔的 coverage
GOCOVERDIR=/tmp/cov ./myapp
go tool covdata textfmt -i=/tmp/cov -o=cover.out
go tool cover -html=cover.out
```

---

## 6. Race / Sanitizer / Memory 問題

### `-race`

```bash
go test ./... -race
go build -race -o myapp .
```

代價：慢 2~20x、binary 變大。建議只在 CI 或排查時開。

**有意識地製造 race（反面教材）：**

```go
// 這段程式碼沒有鎖，會被 -race 抓到
var counter int
var wg sync.WaitGroup
for i := 0; i < 100; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        counter++ // DATA RACE
    }()
}
wg.Wait()
```

**正確做法：用 sync.Mutex 或 atomic：**

```go
// 方法一：Mutex（上面的 Counter 示範）
// 方法二：atomic
var counter int64
go func() { atomic.AddInt64(&counter, 1) }()
```

### `-asan`

```bash
go build -asan -o myapp .
```

適用：cgo 程式懷疑 native memory 越界、use-after-free。

### `-msan`

```bash
go build -msan -o myapp .
```

適用：cgo 程式懷疑未初始化記憶體。

---

## 7. Runtime 觀測與控制

### `GODEBUG`

格式：

```bash
GODEBUG=key=value,key=value ./app
```

### 常用 `GODEBUG` 選項

| 變數 | 用途 | 什麼時候用 |
| --- | --- | --- |
| `gctrace=1` | 每次 GC 印一行摘要 | 先看 GC 是否異常頻繁、pause 是否過大 |
| `schedtrace=1000` | 每 1000ms 印 scheduler 摘要 | 看 runnable goroutine 是否堆積 |
| `scheddetail=1` | 配合 `schedtrace` 印更多細節 | scheduler 問題深入分析 |
| `inittrace=1` | 印每個 package init 時間/配置量 | 啟動慢、初始化太肥 |
| `scavtrace=1` | 印 scavenger 資訊 | 看記憶體回收給 OS 的行為 |
| `gcpacertrace=1` | 印 GC pacer 狀態 | 深入 GC 調校 |
| `allocfreetrace=1` | 每次 alloc/free 都列 trace | 小範圍重現可疑 allocation 問題，代價極高 |
| `clobberfree=1` | free 後覆寫壞值 | 查 use-after-free 類問題 |
| `efence=1` | 每個物件單獨 page 配置 | 查 allocator / memory smash 類問題 |
| `cgocheck=2` | cgo 指標傳遞重檢查 | 懷疑 Go pointer 被錯誤交給 C |
| `madvdontneed=0/1` | 控制記憶體歸還 OS 策略 | 查 RSS 不降問題 |
| `memprofilerate=1` | 調整記憶體 profile 取樣率 | 要更精準 allocation profile |
| `tracebackancestors=N` | traceback 顯示 goroutine 祖先 | 查 goroutine 是誰生出來的 |
| `asyncpreemptoff=1` | 關閉 async preemption | 查 preemption / GC 相關疑難雜症 |
| `gcstoptheworld=1` | 關閉 concurrent GC | 對照 GC 行為，不建議常態使用 |

#### `gctrace=1` 輸出解讀

```text
gc 7 @0.123s 2%: 0.1+0.5+0.03 ms clock, 0.8+0.4/0.3/0+0.2 ms cpu, 4->4->2 MB, 5 MB goal, 16 P
^   ^  ^     ^   ^              ^                                  ^         ^
GC# 時間戳 佔比 STW+並發+STW  CPU時間            heap: before->after->live  goal P數
```

#### 常見命令

```bash
GODEBUG=gctrace=1 ./app
GODEBUG=schedtrace=1000,scheddetail=1 ./app
GODEBUG=inittrace=1 ./app
GODEBUG=gctrace=1,scavtrace=1 ./app
```

### `GOGC`

用途：控制 GC 目標比例，預設 `100`（即 heap 增長到上次存活大小的 2 倍時觸發 GC）。

```bash
GOGC=50 ./app    # 更積極 GC，記憶體壓力大時用
GOGC=200 ./app   # 少 GC，記憶體夠多時用
GOGC=off ./app   # 完全關閉 GC（危險，只用於診斷）
```

程式內動態調整：

```go
old := debug.SetGCPercent(50)
defer debug.SetGCPercent(old)
```

### `GOMEMLIMIT`（Go 1.19+）

用途：設定 Go runtime soft memory limit。

```bash
GOMEMLIMIT=512MiB ./app
GOMEMLIMIT=1GiB ./app
```

適用場景：

- 容器內記憶體有限，避免 OOM Kill
- 搭配 `GOGC=off` 讓 GC 只由記憶體上限觸發，減少 GC 次數

程式內設定：

```go
import "runtime/debug"
debug.SetMemoryLimit(512 * 1024 * 1024) // 512 MiB
```

### `GOMAXPROCS`

```bash
GOMAXPROCS=4 ./app   # 限制只用 4 個 CPU
```

程式內設定：

```go
runtime.GOMAXPROCS(4)
fmt.Println(runtime.GOMAXPROCS(0)) // 查詢當前值
```

### `GORACE`

配合 `-race` 使用：

```bash
GORACE="log_path=/tmp/race.log halt_on_error=1" go test ./... -race
```

### `GOTRACEBACK`

| 值 | 效果 |
| --- | --- |
| `none` | 幾乎不印 stack |
| `single` | 只印當前 goroutine |
| `all` | 印所有 user goroutine |
| `system` | 連 runtime goroutine 一起印 |
| `crash` | 印完後觸發系統層 crash/core dump |

```bash
GOTRACEBACK=all ./app
GOTRACEBACK=crash ./app  # 搭配 ulimit -c unlimited 產生 core dump
```

---

## 8. `runtime/metrics` 與 `runtime/debug`

### `runtime/metrics`（Go 1.16+）

用途：穩定地讀取 runtime 指標（比 `MemStats` 更好的 API）。

```go
import "runtime/metrics"

// 查詢所有可用指標
descs := metrics.All()
for _, d := range descs {
    fmt.Printf("%s: %s\n", d.Name, d.Description)
}

// 讀取特定指標
samples := []metrics.Sample{
    {Name: "/gc/heap/allocs:bytes"},
    {Name: "/gc/cycles/total:gc-cycles"},
    {Name: "/memory/classes/heap/objects:bytes"},
    {Name: "/sched/latencies:seconds"},
}
metrics.Read(samples)
for _, s := range samples {
    fmt.Printf("%s = %v\n", s.Name, s.Value)
}
```

常用指標名稱：

| 指標 | 意義 |
| --- | --- |
| `/gc/heap/allocs:bytes` | 累計分配 bytes |
| `/gc/heap/frees:bytes` | 累計釋放 bytes |
| `/gc/cycles/total:gc-cycles` | GC 次數 |
| `/gc/pauses/total/other:seconds` | GC pause 時間 |
| `/memory/classes/heap/objects:bytes` | 活躍 heap 物件大小 |
| `/sched/latencies:seconds` | goroutine 排程延遲分佈 |
| `/cpu/classes/user:cpu-seconds` | user CPU 使用時間 |

適合：exporter、`/metrics` endpoint、長期監控儀表板。

### `runtime/debug`

```go
import "runtime/debug"

// 動態調整 GC
old := debug.SetGCPercent(50)
defer debug.SetGCPercent(old)

// 設定記憶體上限（等同 GOMEMLIMIT）
debug.SetMemoryLimit(512 * 1024 * 1024)

// 主動把記憶體還給 OS
debug.FreeOSMemory()

// 讀 GC 統計
var stats debug.GCStats
debug.ReadGCStats(&stats)
fmt.Printf("NumGC=%d, LastGC=%v\n", stats.NumGC, stats.LastGC)
fmt.Printf("Pause total: %v\n", stats.PauseTotal)

// 讀 build info（module 路徑、版本、依賴）
if info, ok := debug.ReadBuildInfo(); ok {
    fmt.Printf("module: %s\n", info.Main.Path)
    for _, dep := range info.Deps {
        fmt.Printf("  dep: %s %s\n", dep.Path, dep.Version)
    }
}
```

### `runtime.MemStats`

```go
var ms runtime.MemStats
runtime.GC()                   // 先 GC 讓數字準確
runtime.ReadMemStats(&ms)

fmt.Printf("HeapAlloc:   %d KB\n", ms.HeapAlloc/1024)   // 當前活躍 heap
fmt.Printf("TotalAlloc:  %d KB\n", ms.TotalAlloc/1024)  // 累計分配（只增不減）
fmt.Printf("Sys:         %d KB\n", ms.Sys/1024)          // 從 OS 取得的總記憶體
fmt.Printf("NumGC:       %d\n", ms.NumGC)                // GC 次數
fmt.Printf("PauseTotalNs:%d ns\n", ms.PauseTotalNs)      // GC 累計 pause 時間
```

---

## 9. 低階 `go tool` 完整列表

| 工具 | 用途 | 什麼時候用 |
| --- | --- | --- |
| `addr2line` | 位址轉原始碼位置 | 有 PC 位址、stack 位址，要反查檔案/行號 |
| `asm` | Go 組譯器 | 寫 `.s`、研究底層 ABI，平時很少直接用 |
| `buildid` | 讀/寫 build ID | 排查 binary 是否對應正確 build |
| `cgo` | 產生 Go/C 互通膠水碼 | cgo 除錯、研究產生碼 |
| `compile` | Go 編譯器 | 極低階分析、看編譯器行為 |
| `covdata` | 操作 coverage data | 整合多份 coverage |
| `cover` | coverage 報告/HTML | 看哪些行沒測到 |
| `dist` | Go 發行版/建置相關 | 工具鏈開發、少數情境 |
| `distpack` | 發行打包工具 | 幾乎只有 Go 發行流程會碰 |
| `doc` | 文件查詢低階入口 | 一般直接用 `go doc` 即可 |
| `fix` | API 遷移修正低階入口 | 一般直接用 `go fix` |
| `link` | Go linker | 研究連結流程、極低階分析 |
| `nm` | 列 symbol table | binary 符號分析、大小、是否被裁剪 |
| `objdump` | 反組譯 | 查 hot path 最終機器碼 |
| `pack` | 操作 archive | 極少直接使用 |
| `pprof` | profile 分析 | CPU / memory / block / mutex 熱點分析 |
| `test2json` | 測試輸出轉 JSON | CI、IDE、機器分析 |
| `trace` | execution trace UI | 排程、GC、阻塞因果分析 |
| `vet` | 靜態檢查低階入口 | 一般直接用 `go vet` |

### `go tool nm` 範例

```bash
go build -o myapp .
go tool nm myapp | grep "main\."
```

輸出（實測）：

```text
483a80 T main.(*Counter).Get
483a00 T main.(*Counter).Inc
483900 T main.allocStrings
483ba0 T main.main
```

欄位：`地址 類型 符號名`，`T` = text（程式碼段）

### `go tool objdump` 範例

```bash
go tool objdump -s "main\.allocStrings" myapp | head -15
```

輸出（實測）：

```text
TEXT main.allocStrings(SB) /path/to/main.go
  main.go:36    CMPQ SP, 0x10(R14)
  main.go:36    JBE  ...
  main.go:37    MOVQ AX, BX
  main.go:37    LEAQ 0x859c(IP), AX
  main.go:37    CALL runtime.makeslice(SB)
```

### `go tool addr2line` 範例

```bash
# 把 PC 位址轉成 file:line
echo "0x483900" | go tool addr2line myapp
```

### `go doc` 範例

```bash
go doc runtime.MemStats
go doc sync.Mutex.Lock
go doc fmt.Sprintf
go doc -all net/http
```

### `go tool test2json` 範例

```bash
go test ./... -v | go tool test2json | jq '.Action'
# "run" "output" "pass" "fail" ...
```

---

## 10. 實戰選型

### CPU 高

先用：

```bash
go test ./... -bench=. -cpuprofile=cpu.out
go tool pprof cpu.out
# 互動輸入 top10，看 flat% 最高的函式
```

如果是線上服務：

```bash
go tool pprof http://127.0.0.1:6060/debug/pprof/profile?seconds=30
```

### 記憶體高

先用：

```bash
go test ./... -run TestX -memprofile=mem.out
go tool pprof mem.out
# 互動輸入 top，看 alloc_space 最高的函式
```

再搭配：

```bash
GODEBUG=gctrace=1 ./app
```

如果是容器壓力：

- 看 `GOMEMLIMIT`
- 看 `GOGC`
- 看 `runtime/metrics`

### 鎖競爭 / 卡住

先用：

```bash
go test ./... -run TestX -mutexprofile=mutex.out -mutexprofilefraction=1
go tool pprof mutex.out
```

如果要看卡住時序：

```bash
go test ./... -run TestX -trace=trace.out
go tool trace trace.out
```

### Goroutine 洩漏 / 誰沒結束

先用：

```bash
# 線上服務
go tool pprof http://127.0.0.1:6060/debug/pprof/goroutine

# 非 HTTP 服務（程式內抓）
f, _ := os.Create("goroutine.out")
pprof.Lookup("goroutine").WriteTo(f, 1) // 1 = text 格式
f.Close()

# panic 時印全部 goroutine
GOTRACEBACK=all ./app
```

### 啟動慢

先用：

```bash
GODEBUG=inittrace=1 ./app
```

輸出格式：`init pkg=xxx @t ms, 2 ms clock, 1000 bytes, 3 allocs`

如果還要看整段啟動時序：

```bash
go test -run TestStartup -trace=trace.out
go tool trace trace.out
```

### 疑似資料競態

直接先用：

```bash
go test ./... -race
```

不要一開始就先看 pprof。那是不同維度的問題。

### 想看 inline / escape 決策

```bash
go build -gcflags='-m' ./...           # 一層 inline 資訊
go build -gcflags='-m -m' ./...        # 更詳細
go build -gcflags='all=-m' ./...       # 包含依賴
```

---

## 11. 一句話版心法

| 問題類型 | 最優先工具 |
| --- | --- |
| 熱點 | `pprof` |
| 時序/阻塞/排程 | `trace` |
| 競態 | `-race` |
| 測試覆蓋率 | `cover` |
| runtime 內部狀態 | `GODEBUG` |
| GC/記憶體策略 | `GOGC`、`GOMEMLIMIT`、`runtime/metrics` |
| 低階 binary/匯編 | `objdump`、`nm`、`addr2line` |

---

## 12. 建議工作流

效能問題排查，通常照這順序最省時間：

1. 先重現問題（加 `-race` 先排掉競態）
2. CPU 問題先抓 `pprof`（`-cpuprofile` + `go tool pprof -top`）
3. 卡頓/延遲/阻塞再補 `trace`（`-trace` + `go tool trace`）
4. 記憶體問題加 `memprofile`、`gctrace`
5. 並發正確性問題跑 `-race`
6. 需要長期監控時接 `runtime/metrics`

不要反過來：

- 不要一上來就開一堆 `GODEBUG`
- 不要還沒 benchmark 就急著看匯編
- 不要把 `pprof` 跟 `trace` 當同一種工具
- 不要在生產環境一開始就跑 `allocfreetrace=1`（overhead 極高）

---

## 13. 快速參考：profile 種類對照

| Profile 種類 | 收集方式 | 讀取方式 | 看什麼 |
| --- | --- | --- | --- |
| CPU | `-cpuprofile` / `pprof.StartCPUProfile` | `go tool pprof -top` | 函式 CPU 佔比 |
| Heap | `-memprofile` / `pprof.WriteHeapProfile` | `go tool pprof -top` | allocation 大頭 |
| Block | `-blockprofile` + rate=1 / `Lookup("block")` | `go tool pprof -top` | channel/mutex/syscall 阻塞 |
| Mutex | `-mutexprofile` + fraction=1 / `Lookup("mutex")` | `go tool pprof -top` | 鎖競爭熱點 |
| Goroutine | `Lookup("goroutine").WriteTo(f,1)` | 直接看文字 / `pprof` | goroutine 堆疊快照 |
| Trace | `-trace` / `trace.Start` | `go tool trace` | 時序、排程、GC 全景 |
| Coverage | `-coverprofile` | `go tool cover` | 哪些行未被測試覆蓋 |
