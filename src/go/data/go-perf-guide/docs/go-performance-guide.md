# Go 並行效能優化指南

> 涵蓋 Go Trace Tool、False Sharing、GC 調校、Goroutine Pool 陷阱等核心議題

---

## 目錄

1. [Go Trace Tool — 追蹤工具 UI 指標解讀](#1-go-trace-tool--追蹤工具-ui-指標解讀)
2. [False Sharing — 記憶體抖動問題](#2-false-sharing--記憶體抖動問題)
3. [並行化後的 GC 壓力觀測](#3-並行化後的-gc-壓力觀測)
4. [Goroutine Pool 不一定更快](#4-goroutine-pool-不一定更快)
5. [GOMEMLIMIT 與 GOGC 調校](#5-gomemlimit-與-gogc-調校)
6. [不要過早手動控制並行度](#6-不要過早手動控制並行度)

---

## 1. Go Trace Tool — 追蹤工具 UI 指標解讀

### 什麼是 Execution Trace

Go 內建的 `runtime/trace` 套件可以記錄程式執行期間的事件，包含：

- Goroutine 的建立、阻塞、喚醒
- GC 事件（開始、結束、GC Assist）
- 系統呼叫的進出
- 處理器（P）的排程狀態
- 堆記憶體大小變化

### 如何產生 Trace 檔案

```go
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

    // 你的程式邏輯
    var wg sync.WaitGroup
    for i := 0; i < 8; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            // 做一些工作...
        }(i)
    }
    wg.Wait()
}
```

```bash
# 編譯並執行
go run main.go

# 開啟 Trace UI（瀏覽器會自動開啟）
go tool trace trace.out
```

### Trace UI 要看的關鍵指標

```
┌──────────────────────────────────────────────────────┐
│                  go tool trace UI                    │
├──────────────────────────────────────────────────────┤
│                                                      │
│  1. Goroutine Timeline                               │
│  ┌──────────────────────────────────────┐            │
│  │ G1  ████░░░░████████░░░████          │            │
│  │ G2  ░░░░████████░░░░░░░░████████     │            │
│  │ G3  ░░████░░░░████████████░░░░░░     │            │
│  └──────────────────────────────────────┘            │
│  顏色意義：                                          │
│  ████ = Running（正在執行）                           │
│  ░░░░ = Runnable（可執行但等待 P）                    │
│  空白 = Blocked（阻塞中）                             │
│  特殊 = GC Assist（協助 GC）                          │
│                                                      │
│  2. Processor (P) 時間軸                             │
│  ┌──────────────────────────────────────┐            │
│  │ P0  [G1][G3][G1][GC][G2][G1]        │            │
│  │ P1  [G2][G1][GC][G3][G2]            │            │
│  └──────────────────────────────────────┘            │
│  觀察：哪個 P 在跑哪個 G，GC 佔用了多少時間          │
│                                                      │
│  3. Heap / GC 區域                                   │
│  ┌──────────────────────────────────────┐            │
│  │ Heap ──╱╲──╱╲╲──╱╲──╱╲──           │            │
│  │ GC     ↑   ↑    ↑   ↑               │            │
│  └──────────────────────────────────────┘            │
│  觀察：堆記憶體增長模式、GC 頻率和時間點              │
│                                                      │
└──────────────────────────────────────────────────────┘
```

**關鍵觀察點：**

| 指標 | 說明 | 警訊 |
|------|------|------|
| Goroutine 狀態 | Running / Runnable / Blocked | 大量 Runnable = 排程瓶頸 |
| GC Assist | Goroutine 被迫協助 GC | 頻繁出現 = GC 壓力過大 |
| Processor 利用率 | P 是否有閒置 | P 常空閒 = 並行度不足 |
| GC 暫停時間 | STW (Stop-the-World) 持續時間 | 超過 1ms 需關注 |
| Heap 增長曲線 | 記憶體分配速率 | 鋸齒過密 = 分配/回收太頻繁 |

### Go 1.21+ 改進

- **追蹤開銷降低**：從 10-20% CPU 降到 1-2% CPU
- **可擴展追蹤**：Go 1.22 引入 trace 分割，不再吃爆記憶體
- **Flight Recorder**：持續保留最近的 trace 資料，事件觸發時才寫入

```go
// Flight Recorder 範例（Go 1.22+, golang.org/x/exp/trace）
fr := trace.NewFlightRecorder()
fr.Start()

// 當偵測到異常時才匯出 trace
if requestDuration > 300*time.Millisecond {
    var b bytes.Buffer
    fr.WriteTo(&b)
    os.WriteFile("slow-request.trace", b.Bytes(), 0o644)
}
```

### 替代工具

- **[gotraceui](https://gotraceui.dev/)**：開源替代 trace viewer，體驗更好
- **`GODEBUG=gctrace=1`**：快速在 stderr 輸出 GC 資訊，不需要產生 trace 檔

---

## 2. False Sharing — 記憶體抖動問題

### 什麼是 False Sharing

當多個 goroutine 同時寫入位於**同一條 CPU cache line**（通常 64 bytes）的不同變數時，即使邏輯上互不相干，CPU 仍會不斷作廢整條 cache line，造成效能嚴重下降。

```
CPU Core 0                     CPU Core 1
┌─────────────┐               ┌─────────────┐
│  L1 Cache   │               │  L1 Cache   │
│ ┌─────────┐ │               │ ┌─────────┐ │
│ │ sumA    │ │  ← 作廢！ →   │ │ sumB    │ │
│ │ sumB    │ │  同一 cache   │ │ sumA    │ │
│ └─────────┘ │  line!        │ └─────────┘ │
└─────────────┘               └─────────────┘
     寫入 sumA                     寫入 sumB
     → 導致 Core 1               → 導致 Core 0
       的 cache line 失效           的 cache line 失效
```

### 問題程式碼

```go
// ❌ sumA 和 sumB 在同一條 cache line 上
type Result struct {
    sumA int64  // offset 0
    sumB int64  // offset 8 — 仍在同一個 64-byte cache line 內
}

func count(inputs []Input) Result {
    var wg sync.WaitGroup
    wg.Add(2)
    result := Result{}

    go func() {
        for i := range inputs {
            result.sumA += inputs[i].a  // Core 0 寫 sumA
        }
        wg.Done()
    }()

    go func() {
        for i := range inputs {
            result.sumB += inputs[i].b  // Core 1 寫 sumB → 導致 Core 0 cache 失效
        }
        wg.Done()
    }()

    wg.Wait()
    return result
}
```

### 解決方案：Cache Line Padding

```go
// ✅ 用 padding 讓兩個欄位分在不同 cache line
type Result struct {
    sumA int64
    _    [56]byte  // 填充：8 + 56 = 64 bytes，剛好一條 cache line
    sumB int64
}
```

結構體大小：
- `ResultBad`：16 bytes（同一條 cache line）
- `ResultGood`：72 bytes（兩條不同的 cache line）

### 實測結果

在 Intel i7-14700K (28 threads) 上，使用 1000 萬筆資料：

```
BenchmarkCountBad-28      100    10,411,331 ns/op
BenchmarkCountGood-28     126     9,681,298 ns/op
```

有 padding 的版本快約 **7-10%**。在更高競爭的場景下差距會更大。

### 驗證指令

```bash
cd go-perf-guide
make run-false   # 快速觀察
make bench       # 精確 benchmark
```

---

## 3. 並行化後的 GC 壓力觀測

### 問題

把單執行緒改成並行後，整體時間通常會下降，但**同時也可能增加 GC 壓力**：

- 多個 goroutine 同時分配記憶體 → 堆增長更快
- GC 需要更頻繁觸發
- GC Assist（goroutine 被迫幫忙做 GC）會降低有效計算時間

### 觀測 GC 行為

```go
import (
    "runtime"
    "runtime/debug"
)

// 方法 1：程式內觀測
var stats debug.GCStats
debug.ReadGCStats(&stats)
fmt.Printf("GC 次數: %d, 暫停總時間: %v\n", stats.NumGC, stats.PauseTotal)

var memStats runtime.MemStats
runtime.ReadMemStats(&memStats)
fmt.Printf("堆記憶體: %.2f MiB\n", float64(memStats.HeapAlloc)/(1024*1024))
```

```bash
# 方法 2：環境變數觀測
GODEBUG=gctrace=1 ./your-program

# 輸出格式範例：
# gc 1 @0.012s 2%: 0.021+0.45+0.019 ms clock, 0.17+0/0.39+0.15 ms cpu, 4->4->0 MB, 4 MB goal, 0 MB stacks, 0 MB globals, 8 P
#                  ^^
#                  GC 佔 CPU 時間百分比 ← 這是重點！
```

```bash
# 方法 3：trace 觀測
go tool trace trace.out
# 在 UI 中查看 Heap 區域的 GC 頻率和 GC Assist 事件
```

### 實測結果

```
=== GC 壓力與並行化分析 ===
GOMAXPROCS: 28

  [單執行緒結束] GC 次數: 1, 堆記憶體: 2.76 MiB
  耗時: 4.32ms

  [並行結束]     GC 次數: 2, 堆記憶體: 2.59 MiB
  耗時: 1.01ms     ← 時間下降

  [Pool 結束]    GC 次數: 3, 堆記憶體: 1.96 MiB
  耗時: 0.68ms     ← Pool 版本 GC 更多次
```

**關鍵洞察**：並行版本雖然更快，但 GC 次數增加了。在高記憶體壓力場景下，GC CPU 佔比可能從 2% 飆升到 20%+。

### 驗證指令

```bash
make run-gc

# 搭配 gctrace 觀測更詳細
GODEBUG=gctrace=1 ./bin/gc-pressure
```

---

## 4. Goroutine Pool 不一定更快

### 常見迷思

> 「用 goroutine pool 限制並行度一定比每個任務開一個 goroutine 更好」

**事實**：Pool 的主要價值是**控制資源使用**（記憶體、fd、連線數），不是單純加速。

### 三種並行模式比較

```go
// 模式 1：每任務一個 goroutine（最簡單）
for i := 0; i < tasks; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        doWork()
    }()
}

// 模式 2：Semaphore 限制（建立 goroutine 但限制同時執行數）
sem := make(chan struct{}, poolSize)
for i := 0; i < tasks; i++ {
    wg.Add(1)
    sem <- struct{}{}
    go func() {
        defer wg.Done()
        doWork()
        <-sem
    }()
}

// 模式 3：固定 Worker Pool（預先建立 goroutine）
taskCh := make(chan Task, bufSize)
for i := 0; i < poolSize; i++ {
    go func() {
        for task := range taskCh {
            process(task)
        }
    }()
}
```

### 實測結果

```
=== Goroutine Pool vs Per-Task Goroutine 效能比較 ===
GOMAXPROCS: 28

--- 輕量任務 (100 次迴圈, 10000 任務) ---
  每任務一個 goroutine:   10.40ms
  Semaphore 限制池:       17.04ms   ← 更慢！channel 開銷
  固定 Worker Pool:        5.91ms   ← 最快（預先建立，無建立成本）

--- 中等任務 (10000 次迴圈, 10000 任務) ---
  每任務一個 goroutine:   15.40ms
  Semaphore 限制池:       21.64ms   ← 仍然更慢
  固定 Worker Pool:       14.08ms   ← 差距縮小

--- 重量任務 (100000 次迴圈, 1000 任務) ---
  每任務一個 goroutine:    5.53ms   ← 反而最快
  Semaphore 限制池:       10.04ms
  固定 Worker Pool:        7.49ms
```

### 分析

| 情境 | 建議 |
|------|------|
| 輕量任務 + 大量任務 | 固定 Worker Pool 勝出（避免大量 goroutine 建立） |
| 重量任務 + 少量任務 | 每任務一個 goroutine 就好（建立成本佔比極小） |
| 需控制資源 | 使用 Pool（目的是限制而非加速） |
| 不確定 | 先用最簡單的方式，有問題再優化 |

### Pool 可能帶來的額外 GC 壓力

Pool 模式會讓所有任務的記憶體分配集中在少數 worker goroutine 中，可能導致：

1. 每個 worker 累積的垃圾物件更多
2. GC 掃描這些 goroutine 的 stack 時間更長
3. 觸發更積極的 GC（因為堆增長模式改變）

### 驗證指令

```bash
make run-pool

# 搭配 gctrace 觀察 GC 行為差異
GODEBUG=gctrace=1 ./bin/pool-benchmark
```

---

## 5. GOMEMLIMIT 與 GOGC 調校

### GOGC — 控制 GC 頻率

**公式**：`觸發 GC 的堆大小 = 存活堆 + (存活堆 + GC roots) × GOGC / 100`

```bash
# 預設值 100：堆增長 100% 後觸發 GC
export GOGC=100

# 減少 GC 頻率（更多記憶體，更少 CPU 開銷）
export GOGC=200

# 增加 GC 頻率（更少記憶體，更多 CPU 開銷）
export GOGC=50

# 完全關閉 GC（需搭配 GOMEMLIMIT）
export GOGC=off
```

```go
import "runtime/debug"

// 程式中動態調整
debug.SetGCPercent(200)    // 設為 200%
debug.SetGCPercent(-1)     // 關閉 GC
```

### GOMEMLIMIT — 記憶體軟上限（Go 1.19+）

```bash
# 設定堆記憶體軟上限
export GOMEMLIMIT=512MiB
export GOMEMLIMIT=2GiB

# 在容器中：留 5-10% 給 runtime 開銷
# 容器 1GiB → GOMEMLIMIT=900MiB
```

```go
import "runtime/debug"

debug.SetMemoryLimit(512 * 1024 * 1024)  // 512 MiB
```

### 組合使用策略

```
┌─────────────────────────────────────────────────┐
│               GOGC + GOMEMLIMIT 決策樹           │
├─────────────────────────────────────────────────┤
│                                                 │
│  Q: 在容器 / 固定記憶體環境中？                   │
│  ├─ Yes → 設定 GOMEMLIMIT（留 10% buffer）       │
│  │   ├─ CPU 敏感 → GOGC=200 或更高               │
│  │   └─ 記憶體敏感 → GOGC=50                     │
│  │                                               │
│  └─ No → 通常不需要設 GOMEMLIMIT                 │
│      ├─ CPU 敏感 → 提高 GOGC                     │
│      └─ 預設 GOGC=100 夠用                       │
│                                                 │
│  ⚠️ GOGC=off + GOMEMLIMIT 的組合：                │
│  記憶體自由增長到上限後才觸發 GC                   │
│  適合固定記憶體、穩定分配的場景                     │
│  不適合短暫大量分配（會導致突發 GC 壓力）           │
│                                                 │
└─────────────────────────────────────────────────┘
```

### 調校效果對照表

| 調校 | GC 頻率 | CPU 開銷 | 記憶體用量 | 延遲 |
|------|---------|---------|-----------|------|
| GOGC ↑ | ↓ 降低 | ↓ 降低 | ↑ 增加 | ↓ 降低 |
| GOGC ↓ | ↑ 增加 | ↑ 增加 | ↓ 減少 | ↑ 增加 |
| GOMEMLIMIT ↓ | ↑ 增加 | ↑ 增加 | ↓ 受限 | ↑ 增加 |

### 監控指令

```bash
# GC trace 輸出
GODEBUG=gctrace=1 ./your-program
# 輸出中的百分比就是 GC 佔 CPU 時間
# gc 1 @0.012s 2%: ...
#                ^^  ← GC CPU 佔比

# 配合 go tool trace
go test -trace=trace.out -bench=. ./...
go tool trace trace.out

# 程式內部讀取
runtime.ReadMemStats(&memStats)
fmt.Printf("GC 次數: %d\n", memStats.NumGC)
fmt.Printf("堆使用: %d bytes\n", memStats.HeapAlloc)
```

### 實際案例

```bash
# Cloudflare 的密碼學服務：GOGC 提高到 11300，效能提升 22 倍
# Uber 的動態 GC 調校：跨服務節省了數萬個 CPU 核心

# 你可以用以下指令快速測試不同設定
GOGC=50  ./bin/gc-pressure
GOGC=200 ./bin/gc-pressure
GOGC=off GOMEMLIMIT=100MiB ./bin/gc-pressure
```

---

## 6. 不要過早手動控制並行度

### 核心觀點

Go runtime 的排程器（GMP 模型）已經非常成熟：

```
┌─────────────────────────────────────────────┐
│              Go Runtime Scheduler            │
├─────────────────────────────────────────────┤
│                                             │
│  G (Goroutine)                              │
│  ├── 輕量級（初始 stack 2KB）                │
│  ├── 建立成本極低（~幾百 ns）               │
│  └── runtime 自動管理排程                    │
│                                             │
│  M (Machine = OS Thread)                    │
│  ├── 由 runtime 管理                        │
│  └── 按需建立，不需手動控制                  │
│                                             │
│  P (Processor = 邏輯處理器)                  │
│  ├── 數量 = GOMAXPROCS                      │
│  ├── 本地 run queue                         │
│  └── work stealing 自動負載平衡             │
│                                             │
│  ⚡ runtime 已經替你做了：                    │
│  - 自動 work stealing                       │
│  - goroutine 搶佔式排程                     │
│  - 網路 I/O 的非阻塞處理                    │
│  - GC 與 goroutine 的協調                   │
│                                             │
└─────────────────────────────────────────────┘
```

### 為什麼不該過早使用 Pool

1. **增加程式碼複雜度**：channel、worker 管理、任務分發
2. **可能更慢**：channel 通訊開銷 > goroutine 建立成本
3. **GC 副作用**：worker 累積垃圾可能導致更積極的 GC
4. **遮蔽真正瓶頸**：問題可能在 I/O、鎖競爭，不在 goroutine 數量

### 正確做法

```go
// ✅ 先用最簡單的方式
var wg sync.WaitGroup
for _, item := range items {
    wg.Add(1)
    go func(item Item) {
        defer wg.Done()
        process(item)
    }(item)
}
wg.Wait()

// ✅ 有問題了再用 trace 觀察
// go tool trace trace.out

// ✅ 確認是並行度問題後才引入 pool
// 而且要 benchmark 驗證 pool 確實更快
```

### 什麼時候該用 Pool

| 該用 Pool | 不需要 Pool |
|-----------|------------|
| 限制外部資源（DB 連線、API rate limit） | 純 CPU 計算任務 |
| 任務數量極大（百萬級）且記憶體受限 | 任務數量適中（幾千到幾萬） |
| 需要背壓（backpressure）機制 | Go runtime 排程就能處理 |
| benchmark 證實 pool 確實更快 | 「感覺」pool 應該更快 |

---

## 快速參考

### 工具清單

| 工具 | 用途 | 指令 |
|------|------|------|
| `go tool trace` | 視覺化 goroutine 排程、GC | `go tool trace trace.out` |
| `go tool pprof` | CPU / 記憶體 profiling | `go tool pprof cpu.prof` |
| `GODEBUG=gctrace=1` | GC 事件日誌 | 設環境變數即可 |
| `gotraceui` | 更好的 trace viewer | [gotraceui.dev](https://gotraceui.dev/) |
| `runtime.ReadMemStats` | 程式內讀取記憶體統計 | 寫在程式碼中 |
| `debug.SetGCPercent` | 動態調整 GOGC | 寫在程式碼中 |
| `debug.SetMemoryLimit` | 動態設定記憶體上限 | 寫在程式碼中 |

### 環境變數速查

```bash
# GC 調校
export GOGC=100         # 預設，堆增長 100% 觸發 GC
export GOGC=200         # 減少 GC 頻率
export GOGC=off         # 關閉 GOGC（需搭配 GOMEMLIMIT）
export GOMEMLIMIT=1GiB  # 堆記憶體軟上限

# 除錯
export GODEBUG=gctrace=1           # GC 追蹤
export GODEBUG=schedtrace=1000     # 排程追蹤（每 1000ms）
export GOMAXPROCS=4                # 限制邏輯處理器數量
```

### 效能優化流程

```
1. 先寫正確的程式碼
   ↓
2. 用 benchmark 確認有效能問題
   ↓
3. 用 pprof 找到瓶頸在哪
   ↓
4. 用 go tool trace 觀察並行行為
   ↓
5. 針對性優化（不是盲目加 pool）
   ↓
6. 用 benchmark 驗證優化有效
   ↓
7. 回到第 2 步
```

---

## 參考資源

- [Go 官方 GC 調校指南](https://go.dev/doc/gc-guide)
- [Go 1.22 Execution Traces 改進](https://go.dev/blog/execution-traces-2024)
- [100 Go Mistakes #92: False Sharing](https://100go.co/92-false-sharing/)
- [GOMEMLIMIT is a Game Changer (Weaviate)](https://weaviate.io/blog/gomemlimit-a-game-changer-for-high-memory-applications)
- [Go Performance Optimization Guide](https://goperf.dev/01-common-patterns/gc/)
- [runtime/trace 套件文件](https://pkg.go.dev/runtime/trace)
