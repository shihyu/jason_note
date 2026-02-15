# Go 函數呼叫圖完整指南：靜態分析 + 動態執行路徑

## 目錄

- [概覽](#概覽)
- [方法一：go-callvis 靜態呼叫圖](#方法一go-callvis-靜態呼叫圖)
- [方法二：defer tracer.Enter() 動態函數執行路徑](#方法二defer-tracerenter-動態函數執行路徑)
- [方法三：eBPF uprobe 非侵入式追蹤](#方法三ebpf-uprobe-非侵入式追蹤)
- [方法四：pprof 動態呼叫圖（含效能數據）](#方法四pprof-動態呼叫圖含效能數據)
- [方法五：runtime/trace 動態時間線](#方法五runtimetrace-動態時間線)
- [五種方法對比](#五種方法對比)
- [真實專案驗證：gogcli](#真實專案驗證gogcli)
- [實戰示範專案](#實戰示範專案)
- [進階技巧](#進階技巧)

---

## 概覽

```
┌──────────────────────────────────────────────────────────────────────────┐
│                        Go 函數呼叫追蹤工具                                │
├───────────────┬─────────────────┬──────────────┬──────────┬─────────────┤
│   靜態分析     │  動態執行路徑     │ eBPF 追蹤     │  pprof   │ runtime/trace│
│  go-callvis   │  tracer.Enter() │ bpftrace     │          │             │
├───────────────┼─────────────────┼──────────────┼──────────┼─────────────┤
│ 讀源碼        │ 程式跑時記錄      │ kernel 層追蹤 │ CPU 取樣  │ goroutine   │
│ 不需執行程式   │ 精確呼叫順序     │ 不改程式碼    │ 呼叫圖    │ 時間線       │
│ 看全部可能路徑 │ 含呼叫深度+耗時  │ 含時間戳      │ 含 CPU%  │ 含排程資訊   │
└───────────────┴─────────────────┴──────────────┴──────────┴─────────────┘
```

---

## 方法一：go-callvis 靜態呼叫圖

> 不需要執行程式，直接分析源碼產生呼叫圖

### 安裝

```bash
go install github.com/ofabry/go-callvis@latest
sudo apt install graphviz
```

### 基本用法

```bash
cd your-go-project/

# 產生 SVG（排除標準庫）
go-callvis -file output -format svg -nostd .

# 互動式 Web UI
go-callvis -nostd .
# → 打開 http://localhost:7878
```

### 常用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `-file` | 輸出檔名（省略則啟動 web server） | `-file callgraph` |
| `-format` | 輸出格式 svg/png/jpg | `-format svg` |
| `-nostd` | 排除標準庫呼叫 | `-nostd` |
| `-group` | 按 package/type 分組 | `-group pkg,type` |
| `-focus` | 聚焦特定 package | `-focus service` |
| `-limit` | 限制顯示的 package | `-limit github.com/demo` |
| `-ignore` | 忽略特定 package | `-ignore vendor` |
| `-algo` | 分析演算法 static/cha/rta | `-algo rta` |
| `-nointer` | 隱藏未匯出函數 | `-nointer` |

### 三種演算法

| 演算法 | 精確度 | 速度 | 適用場景 |
|--------|--------|------|----------|
| `static` | 低（過度估計） | 最快 | 快速概覽 |
| `cha` | 中 | 中 | 有 interface 的專案 |
| `rta` | 高（最接近實際） | 最慢 | 需要精確分析 |

### 大專案注意

大專案（500+ 檔案）full graph 的 `.gv` 檔可能達數十 MB，graphviz 渲染極慢。
**必須用 `-focus` / `-limit` 縮小範圍**：

```bash
# 只看某個 package
go-callvis -file focused -format svg -nostd \
  -focus "github.com/you/proj/internal/cmd" \
  -limit "github.com/you/proj" \
  ./cmd/app/
```

---

## 方法二：defer tracer.Enter() 動態函數執行路徑

> **重點方法**：程式實際跑的時候，記錄每個函數的進入/離開，產出精確的呼叫樹

### 原理

在每個函數開頭加一行 `defer tracer.Enter()()`，利用 `runtime.Callers()` 取得真實 call stack，記錄：
- 函數名稱、誰呼叫了它
- 呼叫深度（自動縮排）
- 執行耗時

### tracer 套件（直接複製使用）

```go
// tracer/tracer.go
package tracer

import (
    "fmt"
    "os"
    "runtime"
    "strings"
    "sync"
    "time"
)

type CallRecord struct {
    Depth    int
    Func     string
    Caller   string
    Time     time.Time
    Duration time.Duration
    IsReturn bool
}

var (
    mu      sync.Mutex
    records []CallRecord
)

// Enter 用法：defer tracer.Enter()()
func Enter() func() {
    pc := make([]uintptr, 10)
    n := runtime.Callers(2, pc)
    frames := runtime.CallersFrames(pc[:n])
    frame, _ := frames.Next()
    funcName := shortName(frame.Function)
    callerFrame, _ := frames.Next()
    callerName := shortName(callerFrame.Function)
    depth := func() int { pc := make([]uintptr, 50); return runtime.Callers(3, pc) }()
    start := time.Now()
    mu.Lock()
    records = append(records, CallRecord{Depth: depth, Func: funcName, Caller: callerName, Time: start})
    mu.Unlock()
    return func() {
        mu.Lock()
        records = append(records, CallRecord{Depth: depth, Func: funcName, Duration: time.Since(start), IsReturn: true})
        mu.Unlock()
    }
}

func shortName(full string) string {
    if full == "" { return "<unknown>" }
    parts := strings.Split(full, "/")
    return parts[len(parts)-1]
}

func PrintTrace() {
    mu.Lock()
    defer mu.Unlock()
    fmt.Println(strings.Repeat("=", 70))
    fmt.Println("  函數執行路徑（Runtime Function Call Trace）")
    fmt.Println(strings.Repeat("=", 70))
    baseDepth := 100
    for _, r := range records { if !r.IsReturn && r.Depth < baseDepth { baseDepth = r.Depth } }
    for _, r := range records {
        indent := strings.Repeat("│ ", r.Depth-baseDepth)
        if r.IsReturn {
            fmt.Printf("  %s└─ return %s [%v]\n", indent, r.Func, r.Duration)
        } else {
            fmt.Printf("  %s┌─ %s  ← called by %s\n", indent, r.Func, r.Caller)
        }
    }
    fmt.Println(strings.Repeat("=", 70))
}

func WriteTraceToFile(filename string) error {
    mu.Lock(); defer mu.Unlock()
    f, err := os.Create(filename); if err != nil { return err }; defer f.Close()
    baseDepth := 100
    for _, r := range records { if !r.IsReturn && r.Depth < baseDepth { baseDepth = r.Depth } }
    fmt.Fprintln(f, "# Runtime Function Call Trace\n\n```")
    for _, r := range records {
        indent := strings.Repeat("│ ", r.Depth-baseDepth)
        if r.IsReturn { fmt.Fprintf(f, "%s└─ return %s [%v]\n", indent, r.Func, r.Duration)
        } else { fmt.Fprintf(f, "%s┌─ %s  ← %s\n", indent, r.Func, r.Caller) }
    }
    fmt.Fprintln(f, "```"); return nil
}
```

### 使用方式

```go
func (s *OrderService) PlaceOrder(userID, product string, amount float64) *Order {
    defer tracer.Enter()()   // ← 就這一行
    order := &Order{...}
    s.processPayment(order)
    return order
}
```

程式結束前呼叫 `tracer.PrintTrace()`。

### 實際輸出

```
======================================================================
  函數執行路徑（Runtime Function Call Trace）
======================================================================
  ┌─ main.NewApp  ← called by main.main
  │ ┌─ main.NewMiddlewareChain  ← called by main.NewApp
  │ └─ return main.NewMiddlewareChain [3.71µs]
  └─ return main.NewApp [9.477µs]
  ┌─ main.(*App).Init  ← called by main.main
  │ ┌─ main.(*MiddlewareChain).Use  ← called by main.(*App).Init
  │ └─ return main.(*MiddlewareChain).Use [211ns]
  │ ┌─ main.(*App).setupRoutes  ← called by main.(*App).Init
  │ └─ return main.(*App).setupRoutes [73ns]
  └─ return main.(*App).Init [11.852µs]
  ┌─ main.(*App).HandleRequest  ← called by main.main
  │ ┌─ main.(*MiddlewareChain).Execute  ← called by main.(*App).HandleRequest
  │ │ ┌─ main.LoggerMiddleware  ← called by main.(*MiddlewareChain).Execute
  │ │ └─ return main.LoggerMiddleware [68ns]
  │ │ ┌─ main.AuthMiddleware  ← ...
  │ │ ┌─ main.RateLimitMiddleware  ← ...
  │ └─ return main.(*MiddlewareChain).Execute [7.97µs]
  └─ return main.(*App).HandleRequest [10.058µs]
  ┌─ main.(*OrderService).PlaceOrder  ← called by main.main
  │ ┌─ main.generateID  ← called by main.(*OrderService).PlaceOrder
  │ ┌─ main.(*OrderService).processPayment  ← called by main.(*OrderService).PlaceOrder
  │ │ ┌─ main.(*OrderService).notifyUser  ← called by main.(*OrderService).processPayment
  │ └─ return main.(*OrderService).PlaceOrder [12.018µs]
  ┌─ main.(*App).Shutdown  ← called by main.main
  │ ┌─ main.(*App).cleanup  ← called by main.(*App).Shutdown
  └─ return main.(*App).Shutdown [1.928µs]
======================================================================
```

---

## 方法三：eBPF uprobe 非侵入式追蹤

> **完全不改程式碼**，用 kernel 層 uprobe 追蹤函數進入

### 步驟

```bash
# 1. 編譯時關閉 inlining
go build -gcflags='-l' -o myapp .

# 2. 查看可追蹤的函數符號
go tool nm myapp | grep ' T ' | grep -v runtime | grep your/package

# 3. 寫 bpftrace 腳本（或用自動生成，見進階技巧）
# 4. 執行
sudo bpftrace trace.bt -c ./myapp
```

### 腳本範例

```bpftrace
#!/usr/bin/env bpftrace
BEGIN { printf("%-12s %-6s %s\n", "TIME(µs)", "TID", "FUNCTION"); }

uprobe:./myapp:main.main
{ printf("%-12lu %-6d → main\n", elapsed/1000, tid); }

uprobe:./myapp:"github.com/you/pkg.(*Type).Method"
{ printf("%-12lu %-6d   → Type.Method\n", elapsed/1000, tid); }
```

> **注意**：Go 的 goroutine stack 和 `uretprobe` 不相容（crash），只能用 `uprobe` 追蹤進入點。

### 實際輸出

```
TIME(µs)    TID    FUNCTION
---------------------------------------------------
37707        2270720 → main
37739        2270720   → server.NewApp
37744        2270720   → server.App.Init
37810        2270720       → middleware.Chain.Use ×3
37838        2270720   → service.NewUserService
37846        2270720   → service.UserService.CreateUser
37850        2270720     → util.GenerateID
37935        2270720   → service.OrderService.PlaceOrder
37941        2270720     → util.GenerateID
37947        2270720       → service.OrderService.notifyUser
38243        2270720   → service.OrderService.GenerateReport
38272        2270720   → server.App.Shutdown
```

---

## 方法四：pprof 動態呼叫圖（含效能數據）

> 程式實際跑時的 CPU 取樣，產出帶效能數據的呼叫圖

```bash
# 產生 profile（三種方式任選）
go test -bench=. -cpuprofile=cpu.prof -benchtime=3s .     # benchmark
go test -cpuprofile=cpu.prof -count=50 ./internal/...     # 多跑幾次 test
# 或程式碼嵌入 runtime/pprof / net/http/pprof

# 產生呼叫圖
go tool pprof -svg -output=callgraph.svg cpu.prof

# 互動式 Web UI（含火焰圖）
go tool pprof -http=:8080 cpu.prof
```

### 解讀

```
┌──────────────────────────────────┐
│ service.(*OrderService).PlaceOrder│
│    0.05s (0.88%)                 │  ← flat：自己的 CPU 時間
│    of 3.23s (56.87%)             │  ← cum：含子呼叫的總時間
└──────────┬───────────────────────┘
           │ 1.83s                     ← 邊 = 呼叫耗時
           ▼
┌──────────────────────────────────┐
│ service.(*OrderService).notifyUser│
└──────────────────────────────────┘
```

框越大 = CPU 越多、顏色越紅 = 熱點

---

## 方法五：runtime/trace 動態時間線

> 看 goroutine 排程、並發行為

```bash
# 不改程式碼，透過 test 產生
go test -trace=trace.out ./...

# 或程式碼嵌入
# trace.Start(f); defer trace.Stop()

# 分析
go tool trace trace.out
# → 瀏覽器打開：View trace / Goroutine analysis / Blocking profiles
```

---

## 五種方法對比

| 特性 | go-callvis | tracer.Enter() | eBPF uprobe | pprof | runtime/trace |
|------|-----------|----------------|-------------|-------|---------------|
| **分析方式** | 靜態 | 動態（精確） | 動態（kernel） | 動態（取樣） | 動態（事件） |
| **需要執行程式** | 否 | 是 | 是 | 是 | 是 |
| **需要改程式碼** | 否 | 是 | 否 | 否/少量 | 少量 |
| **需要 root** | 否 | 否 | **是** | 否 | 否 |
| **顯示呼叫順序** | 否 | **精確** | **精確** | 否（取樣） | 部分 |
| **顯示耗時** | 無 | **每函數** | **微秒時間戳** | CPU 佔比 | goroutine 延遲 |
| **產出格式** | SVG/Web | 終端樹狀圖 | 終端文字 | SVG/火焰圖 | Web 時間線 |
| **適用場景** | 看架構 | **看執行路徑** | **生產環境** | 效能優化 | 並發問題 |

### 選擇流程

```
想看什麼？
├─ 專案架構，誰可能呼叫誰 → go-callvis
├─ 真實執行的函數呼叫順序
│   ├─ 可以改程式碼 → tracer.Enter()
│   └─ 不能改程式碼 → eBPF uprobe (需 root)
├─ 哪個函數最耗 CPU → pprof
└─ goroutine 排程、鎖競爭 → runtime/trace
```

---

## 真實專案驗證：gogcli

使用 [steipete/gogcli](https://github.com/steipete/gogcli)（506 個 Go 檔、973 個函數）驗證五種方法：

### 驗證結果

| # | 方法 | 結果 | 產出 | 備註 |
|---|------|------|------|------|
| 1 | go-callvis 靜態 | **PASS** | `gogcli-static.svg` (4.9K) / `gogcli-cmd.svg` (4.5M) | 大專案必須用 `-focus` 限制範圍 |
| 2 | tracer.Enter() | **PASS** | 終端呼叫樹 | 追蹤 `Execute→version/help/error` 路徑 |
| 3 | eBPF uprobe | **PASS** | 帶時間戳的函數進入記錄 | 零侵入，清楚看到完整呼叫鏈 |
| 4 | pprof 呼叫圖 | **PASS** | `gogcli-pprof.svg` (141K) | tracking 模組 CPU profile |
| 5 | runtime/trace | **PASS** | `trace.out` (332K) | syscall 延遲分析正常 |

### 方法三 eBPF 追蹤 `gog version` 的真實輸出

```
TIME(µs)    TID    FUNCTION
---------------------------------------------------
61850        2291256 → main.main
61871        2291256   → cmd.Execute
61877        2291256       → config.Dir
61882        2291256       → config.Dir
68891        2291256     → cmd.newParser
103138       2291274     → ui.New
103201       2291274     → VersionCmd.Run
```

非侵入式看到了完整的啟動流程：`main → Execute → config.Dir → newParser → ui.New → VersionCmd.Run`

### 方法四 pprof 的 CPU 熱點（tracking 模組）

```
  0.67s  28.15%  sha256.blockSHANI          ← 加密是 CPU 熱點
  0.33s  13.87%  sha256.(*Digest).checkSum
  0.16s   6.72%  syscall.Syscall6
  0.10s   4.20%  jose2go/arrays.Xor
```

### 方法五 runtime/trace 的 syscall 延遲

```
  248.30ms  93.09%  syscall.Mkdirat           ← 建目錄是延遲瓶頸
   16.12ms   6.04%  syscall.fstatat
```

### 踩坑記錄

| 問題 | 原因 | 解法 |
|------|------|------|
| go-callvis `internal error: package without types` | go-callvis 版本太舊 | `go install github.com/ofabry/go-callvis@latest` |
| go-callvis 大專案渲染卡死 | `.gv` 檔 33MB，graphviz 吃不消 | 加 `-focus` / `-limit` 過濾 |
| eBPF `uretprobe` 導致 Go 程式 crash | goroutine stack 機制衝突 | 只用 `uprobe`，不用 `uretprobe` |
| Delve `dlv trace` crash | Go 版本和 Delve 版本不匹配 | 確保版本一致，或改用 eBPF |

---

## 實戰示範專案

```
go-callgraph-demo/
├── Makefile                       # make help 看所有指令
├── main.go                        # 入口，支援 --trace 參數
├── main_test.go                   # Benchmark（用於 pprof）
├── cmd/traced/main.go             # 帶 tracer 的版本
├── tracer/tracer.go               # tracer 套件（可複製）
├── model/model.go                 # User, Order
├── server/
│   ├── app.go                     # App 初始化/關閉
│   └── middleware/middleware.go    # Logger, Auth, RateLimit
├── service/
│   ├── user.go                    # UserService
│   └── order.go                   # OrderService
├── util/id.go                     # ID 生成
└── trace-uprobe-entry.bt          # bpftrace 腳本
```

---

## 進階技巧

### 1. go-callvis 過濾雜訊

```bash
go-callvis -file clean -format svg \
  -nostd -nointer -focus service \
  -limit github.com/your/project -algo rta .
```

### 2. pprof 過濾

```bash
go tool pprof cpu.prof
(pprof) focus=github.com/demo
(pprof) nodefraction=0.05
(pprof) web
```

### 3. 同時產生多種 profile

```bash
go test -bench=. -cpuprofile=cpu.prof -memprofile=mem.prof -trace=trace.out -benchtime=5s .
```

### 4. 自動產生 bpftrace 腳本

```bash
go tool nm myapp | grep ' T ' | grep -v 'runtime\|type:\|go:' | \
  awk '{printf "uprobe:./myapp:\"%s\" { printf(\"→ %s\\n\"); }\n", $3, $3}'
```

### 5. eBPF 限制

- Go `uretprobe` 會 crash → 只用 `uprobe`
- 必須 `-gcflags='-l'` 禁止 inlining
- 需要 root 權限

---

## 工具安裝

```bash
go install github.com/ofabry/go-callvis@latest   # 靜態呼叫圖
sudo apt install graphviz bpftrace                # 渲染 + eBPF
# go tool pprof / go tool trace / go tool nm 已內建
```
