# Go 語言完整實戰指南：從語言特性到效能優化

> 本文整合 Go 語言的核心設計哲學、函數追蹤工具、並行效能優化，以及高併發場景下的實務問題，適合有 C/C++ 或系統底層經驗的工程師進階學習。

---

## 目錄

- [第一部分：Go 語言核心設計與 C++ 差異](#第一部分go-語言核心設計與-c-差異)
- [第二部分：函數呼叫追蹤與除錯工具](#第二部分函數呼叫追蹤與除錯工具)
- [第三部分：並行效能優化](#第三部分並行效能優化)
- [第四部分：高併發場景實務問題](#第四部分高併發場景實務問題)
- [總結](#總結)

---

# 第一部分：Go 語言核心設計與 C++ 差異

對於有 C++ 背景的工程師而言，學 Go 最大的挑戰不在語法，而在**設計思維的轉換**。Go 刻意捨棄了許多 C++ 的強大機制，換來的是更簡單、更不容易出錯的程式碼。本節整理兩者的核心差異，幫助你快速建立正確的 Go 思維。

## 1. Go 沒有 class，只有 type

### C++

```cpp
class Dog {
public:
    void Speak() { std::cout << "woof"; }
};
```

### Go

```go
type Dog struct{}

func (d Dog) Speak() {
    fmt.Println("woof")
}
```

### 重點

- Go 沒有 `class`
- `type` 是在定義型別
- method 是「掛在型別上」的 function
- `(d Dog)` 不是參數宣告錯誤，而是 receiver（接收者）

白話：Go 是「先定義型別，再幫它加能力」，不是像 C++ 把所有東西包在 class 裡。

---

## 2. method 其實就是特殊語法的 function

```go
func (d Dog) Speak()
```

等價概念：

```go
func Speak(d Dog)
```

差別只是呼叫方式：

    d.Speak()   // method
    Speak(d)    // function

白話：method 本質還是 function，只是語法糖。

---

## 3. Interface 是「隱式實作」

### Go

```go
type Speaker interface {
    Speak()
}

type Dog struct{}

func (Dog) Speak() {}
```

Dog 沒有寫 `implements Speaker`，但它自動符合。

### C++

```cpp
class Dog : public Speaker
```

必須明確繼承。

白話：
C++：你要報名參加俱樂部。
Go：你會做這件事，就算會員。

---

## 4. 實作者不需要知道 interface 存在

Go 設計哲學：

> Interface 屬於「使用者」，不是「實作者」。

例如：

```go
func Process(s Speaker) {}
```

Dog 不需要依賴 Speaker。這降低耦合。C++ 則必須依賴抽象類別。

---

## 5. 沒有繼承，只有組合

C++ 有 inheritance tree。Go 沒有 extends / subclass。

只用：
- struct 組合
- interface 抽象

白話：Go 故意不讓你設計很複雜的 class hierarchy。

---

## 6. 沒有 constructor / destructor / RAII

C++ 有建構子、解構子、RAII。Go 沒有 constructor 語法、沒有 destructor，用 GC 管理記憶體。

通常寫：

```go
func NewDog() *Dog {
    return &Dog{}
}
```

---

## 7. Error Handling 不用 Exception

C++：

```cpp
try { } catch(...) {}
```

Go：

```go
if err != nil {
    return err
}
```

Go 強制顯式處理錯誤。

---

## 8. 沒有 function overloading / operator overloading

C++ 可以多載：

```cpp
int add(int, int);
double add(double, double);
```

Go 不行。必須改名或用 generics。

---

## 9. 指標限制較多

C++ 可以 pointer arithmetic、placement new，可能 UB。Go 禁止 pointer arithmetic、不允許未定義行為，更安全。

---

## 10. Concurrency 模型不同

C++ 使用 thread + mutex + condition variable。

Go 採 CSP 模型：

```go
go func() {}
ch := make(chan int)
```

白話：
C++：共享記憶體 + 鎖
Go：不要共享記憶體，用 channel 溝通

---

## 核心哲學差異總結

| C++ | Go |
|-----|-----|
| Powerful | Simple |
| Template metaprogramming | 保守 generics |
| Inheritance | Composition |
| RAII | GC |
| 顯式繼承 | 隱式 interface |
| 高度彈性 | 刻意限制複雜度 |

**最重要的轉換心法：** 從 C++ 轉 Go 要改的是「設計思維」，不是語法。

❌ 不要設計複雜 class hierarchy
✅ 小 interface + 組合
✅ 明確 error handling
✅ 保持簡單

---

# 第二部分：函數呼叫追蹤與除錯工具

掌握了 Go 的設計哲學之後，下一步就是學會**觀察程式在幹嘛**。Go 生態提供了豐富的追蹤工具，從靜態分析到動態執行路徑，讓你能深入理解程式行為、快速定位問題。本節介紹五種互補的函數呼叫追蹤方法。

## 工具概覽

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

大專案（500+ 檔案）full graph 的 `.gv` 檔可能達數十 MB，graphviz 渲染極慢。**必須用 `-focus` / `-limit` 縮小範圍**：

```bash
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

# 3. 寫 bpftrace 腳本
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

### 真實專案驗證：gogcli

使用 [steipete/gogcli](https://github.com/steipete/gogcli)（506 個 Go 檔、973 個函數）實際驗證五種方法，以下為完整可重現的指令與輸出。

#### 環境準備

```bash
git clone https://github.com/steipete/gogcli.git /tmp/gogcli
cd /tmp/gogcli
go build -o ./bin/gog ./cmd/gog/
./bin/gog version
# → 0.12.0-dev
```

#### 方法一驗證：go-callvis 靜態呼叫圖

```bash
cd /tmp/gogcli

# 聚焦 main package（產出 4.9KB SVG，秒級完成）
go-callvis -file gogcli-main -format svg -nostd \
  -focus "github.com/steipete/gogcli/cmd/gog" \
  -limit "github.com/steipete/gogcli" \
  ./cmd/gog/
# → writing dot output
# → converting dot to svg
# → 產出 gogcli-main.svg (4.9KB)

# 聚焦 internal/cmd package（更完整，但 SVG 較大）
go-callvis -file gogcli-cmd -format svg -nostd \
  -focus "github.com/steipete/gogcli/internal/cmd" \
  -limit "github.com/steipete/gogcli" \
  ./cmd/gog/
# → 產出 gogcli-cmd.svg (4.3MB)
```

> **踩坑**：不加 `-focus`/`-limit` 時，中間的 `.gv` 檔達數十 MB，graphviz 渲染卡死。大專案**必須**縮小範圍。

#### 方法二驗證：tracer.Enter() 動態追蹤

**步驟 1**：在專案中建立 tracer 套件（複製上面的 `tracer/tracer.go`）

```bash
mkdir -p internal/tracer
# 將 tracer.go 放入 internal/tracer/
```

**步驟 2**：在關鍵函數加入 `defer tracer.Enter()()`

```go
// cmd/gog/main.go
func main() {
    defer tracer.PrintTrace()  // 程式結束時印出追蹤結果
    defer tracer.Enter()()     // 追蹤 main
    if err := cmd.Execute(os.Args[1:]); err != nil {
        os.Exit(cmd.ExitCode(err))
    }
}

// internal/cmd/root.go
func Execute(args []string) (err error) {
    defer tracer.Enter()()  // ← 加這一行
    // ...
}

// internal/cmd/version.go
func (c *VersionCmd) Run(ctx context.Context) error {
    defer tracer.Enter()()  // ← 加這一行
    // ...
}
```

**步驟 3**：執行並觀察

```bash
go build -o ./bin/gog-traced ./cmd/gog/
./bin/gog-traced version
```

**實際輸出**：

```
0.12.0-dev
======================================================================
  函數執行路徑（Runtime Function Call Trace）
======================================================================
  ┌─ main.main  ← called by runtime.main
  │ ┌─ cmd.Execute  ← called by main.main
  │ │ ┌─ cmd.rewriteDesirePathArgs  ← called by cmd.Execute
  │ │ └─ return cmd.rewriteDesirePathArgs [2.213µs]
  │ │ ┌─ cmd.newParser  ← called by cmd.Execute
  │ │ │ ┌─ cmd.VersionString  ← called by cmd.newParser
  │ │ │ └─ return cmd.VersionString [848ns]
  │ │ └─ return cmd.newParser [44.659ms]
  │ │ │ │ │ │ │ │ ┌─ cmd.(*VersionCmd).Run  ← called by reflect.Value.call
  │ │ │ │ │ │ │ │ │ ┌─ cmd.VersionString  ← called by cmd.(*VersionCmd).Run
  │ │ │ │ │ │ │ │ │ └─ return cmd.VersionString [416ns]
  │ │ │ │ │ │ │ │ └─ return cmd.(*VersionCmd).Run [17.204µs]
  │ └─ return cmd.Execute [49.370ms]
  └─ return main.main [49.392ms]
======================================================================
```

> 可以清楚看到：`main.main` → `cmd.Execute` → `cmd.newParser`（耗時最多，44ms）→ Kong 框架透過 `reflect.Value.call` 呼叫 `VersionCmd.Run`。

#### 方法三驗證：eBPF uprobe 非侵入式追蹤

```bash
cd /tmp/gogcli

# 1. 關閉 inlining 編譯
go build -gcflags='-l' -o ./bin/gog-noinline ./cmd/gog/

# 2. 查看可追蹤的函數符號
go tool nm ./bin/gog-noinline | grep ' T ' | grep -E 'main\.|cmd\.(Execute|newParser|VersionString)'
# → d1fd60 T github.com/steipete/gogcli/internal/cmd.Execute
# → d42fa0 T github.com/steipete/gogcli/internal/cmd.VersionString
# → d21540 T github.com/steipete/gogcli/internal/cmd.newParser
# → d52b40 T main.main

# 3. 寫 bpftrace 腳本 trace-gogcli.bt
cat > trace-gogcli.bt << 'EOF'
#!/usr/bin/env bpftrace
BEGIN {
    printf("%-12s %-6s %s\n", "TIME(µs)", "TID", "FUNCTION");
    printf("─────────────────────────────────────\n");
}
uprobe:./bin/gog-noinline:main.main
{ printf("%-12lu %-6d → main.main\n", elapsed/1000, tid); }
uprobe:./bin/gog-noinline:"github.com/steipete/gogcli/internal/cmd.Execute"
{ printf("%-12lu %-6d   → cmd.Execute\n", elapsed/1000, tid); }
uprobe:./bin/gog-noinline:"github.com/steipete/gogcli/internal/cmd.rewriteDesirePathArgs"
{ printf("%-12lu %-6d     → cmd.rewriteDesirePathArgs\n", elapsed/1000, tid); }
uprobe:./bin/gog-noinline:"github.com/steipete/gogcli/internal/cmd.newParser"
{ printf("%-12lu %-6d     → cmd.newParser\n", elapsed/1000, tid); }
uprobe:./bin/gog-noinline:"github.com/steipete/gogcli/internal/cmd.VersionString"
{ printf("%-12lu %-6d       → cmd.VersionString\n", elapsed/1000, tid); }
EOF

# 4. 執行（需要 root）
sudo bpftrace trace-gogcli.bt -c './bin/gog-noinline version'
```

**實際輸出**：

```
Attaching 6 probes...
TIME(µs)    TID    FUNCTION
─────────────────────────────────────
59793        2380773 → main.main
59816        2380773   → cmd.Execute
59819        2380773     → cmd.rewriteDesirePathArgs
59844        2380773     → cmd.newParser
59856        2380773       → cmd.VersionString
0.12.0-dev
112488       2380787       → cmd.VersionString
```

> **注意**：VersionString 出現兩次——第一次在 `newParser` 中設定版本字串給 Kong，第二次在 `VersionCmd.Run` 中印出版本。第二次的 TID 不同（2380787），代表 Kong 框架在不同 goroutine 中執行了指令。

#### 方法四驗證：pprof CPU profiling

```bash
cd /tmp/gogcli

# 對 tracking 套件跑 5 次測試，產生 CPU profile
go test -cpuprofile=cpu.prof -count=5 ./internal/tracking/...
# → ok  github.com/steipete/gogcli/internal/tracking  0.618s

# 查看熱點函數
go tool pprof -top -nodecount=10 cpu.prof
```

**實際輸出**：

```
Type: cpu
Duration: 603.41ms, Total samples = 430ms (71.26%)
Showing top 10 nodes out of 116
      flat  flat%   sum%        cum   cum%
     140ms 32.56% 32.56%      140ms 32.56%  crypto/internal/fips140/sha256.blockSHANI
      70ms 16.28% 48.84%       70ms 16.28%  internal/runtime/syscall.Syscall6
      50ms 11.63% 60.47%      220ms 51.16%  crypto/internal/fips140/sha256.(*Digest).checkSum
      30ms  6.98% 67.44%      190ms 44.19%  crypto/internal/fips140/sha256.(*Digest).Write
      30ms  6.98% 74.42%       30ms  6.98%  runtime.memmove
      10ms  2.33% 76.74%      250ms 58.14%  crypto/internal/fips140/sha256.(*Digest).Sum
      10ms  2.33% 79.07%       20ms  4.65%  crypto/internal/fips140/sha256.(*Digest).UnmarshalBinary
      10ms  2.33% 81.40%       10ms  2.33%  internal/poll.runtime_pollOpen
      10ms  2.33% 83.72%       10ms  2.33%  runtime.duffcopy
      10ms  2.33% 86.05%       10ms  2.33%  runtime.forEachG
```

> CPU 熱點集中在 SHA256（tracking 套件用 hash 做檔案追蹤），這在實際專案中很常見。

```bash
# 產生 SVG 呼叫圖
go tool pprof -svg -output=gogcli-pprof.svg cpu.prof
# → 產出 gogcli-pprof.svg (127KB)

# 互動式 Web UI（含火焰圖）
go tool pprof -http=:8080 cpu.prof
```

#### 方法五驗證：runtime/trace 時間線

```bash
cd /tmp/gogcli

# 產生 trace 檔案
go test -trace=trace.out ./internal/tracking/...
# → ok  github.com/steipete/gogcli/internal/tracking  0.078s

ls -lh trace.out
# → 112K trace.out

# 查看 trace 事件統計
go tool trace -d=footprint trace.out
```

**實際輸出**（事件分布）：

```
Event                Bytes  %       Count  %
Stack                76897  67.56%  726    12.89%
String               14938  13.12%  405    7.19%
HeapAlloc            9298   8.17%   1365   24.23%
GoSyscallBegin       5852   5.14%   1074   19.06%
GoSyscallEnd         2308   2.03%   1074   19.06%
GoStart              834    0.73%   205    3.64%
GoBlock              649    0.57%   150    2.66%
GoUnblock            626    0.55%   119    2.11%
GoCreate             354    0.31%   66     1.17%
```

> 可以看到：66 個 goroutine 被建立、1074 次 syscall、1365 次 heap 分配。這些數據對應 tracking 套件讀檔計算 hash 的行為。

```bash
# 用瀏覽器檢視完整時間線
go tool trace trace.out
# → 打開 http://localhost:xxxx
# → View trace：看 goroutine 排程時間線
# → Goroutine analysis：看各 goroutine 的狀態分布
```

### 踩坑記錄

| 問題 | 原因 | 解法 |
|------|------|------|
| go-callvis `internal error: package without types` | go-callvis 版本太舊 | `go install github.com/ofabry/go-callvis@latest` |
| go-callvis 大專案渲染卡死 | `.gv` 檔達數十 MB，graphviz 吃不消 | 加 `-focus` / `-limit` 過濾，先產小範圍 SVG |
| eBPF `uretprobe` 導致 Go 程式 crash | goroutine stack 機制與 uretprobe 衝突 | 只用 `uprobe`，不用 `uretprobe` |
| bpftrace 看到同一函數不同 TID | Kong 框架在內部 goroutine 執行指令 | 正常行為，觀察 TID 可發現並行模式 |
| pprof 取樣數據少 | 測試執行時間太短 | 加 `-count=5` 或 `-benchtime=3s` 增加取樣 |
| Delve `dlv trace` crash | Go 版本和 Delve 版本不匹配 | 確保版本一致，或改用 eBPF |

---

# 第三部分：並行效能優化

有了追蹤工具的能力之後，接下來深入 Go 並行程式的效能議題。Go 的 goroutine 讓並行變得容易，但「容易寫出並行程式碼」不等於「容易寫出高效的並行程式碼」。本節涵蓋 Go Trace Tool 指標解讀、False Sharing、GC 調校、Goroutine Pool 陷阱等核心議題。

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
go run main.go
go tool trace trace.out
```

### Trace UI 關鍵指標

```
┌──────────────────────────────────────────────────────┐
│                  go tool trace UI                    │
├──────────────────────────────────────────────────────┤
│  1. Goroutine Timeline                               │
│  ┌──────────────────────────────────────┐            │
│  │ G1  ████░░░░████████░░░████          │            │
│  │ G2  ░░░░████████░░░░░░░░████████     │            │
│  │ G3  ░░████░░░░████████████░░░░░░     │            │
│  └──────────────────────────────────────┘            │
│  ████ = Running    ░░░░ = Runnable    空白 = Blocked  │
│                                                      │
│  2. Processor (P) 時間軸                             │
│  ┌──────────────────────────────────────┐            │
│  │ P0  [G1][G3][G1][GC][G2][G1]        │            │
│  │ P1  [G2][G1][GC][G3][G2]            │            │
│  └──────────────────────────────────────┘            │
│                                                      │
│  3. Heap / GC 區域                                   │
│  ┌──────────────────────────────────────┐            │
│  │ Heap ──╱╲──╱╲╲──╱╲──╱╲──           │            │
│  │ GC     ↑   ↑    ↑   ↑               │            │
│  └──────────────────────────────────────┘            │
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

if requestDuration > 300*time.Millisecond {
    var b bytes.Buffer
    fr.WriteTo(&b)
    os.WriteFile("slow-request.trace", b.Bytes(), 0o644)
}
```

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

實測結果（Intel i7-14700K, 28 threads, 1000 萬筆資料）：有 padding 的版本快約 **7-10%**。在更高競爭的場景下差距會更大。

---

## 3. 並行化後的 GC 壓力觀測

把單執行緒改成並行後，整體時間通常會下降，但**同時也可能增加 GC 壓力**：

- 多個 goroutine 同時分配記憶體 → 堆增長更快
- GC 需要更頻繁觸發
- GC Assist（goroutine 被迫幫忙做 GC）會降低有效計算時間

### 觀測 GC 行為

```go
// 方法 1：程式內觀測
var stats debug.GCStats
debug.ReadGCStats(&stats)
fmt.Printf("GC 次數: %d, 暫停總時間: %v\n", stats.NumGC, stats.PauseTotal)
```

```bash
# 方法 2：環境變數觀測
GODEBUG=gctrace=1 ./your-program
# gc 1 @0.012s 2%: 0.021+0.45+0.019 ms clock, ...
#                ^^  ← GC 佔 CPU 時間百分比
```

**關鍵洞察**：並行版本雖然更快，但 GC 次數增加了。在高記憶體壓力場景下，GC CPU 佔比可能從 2% 飆升到 20%+。

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

// 模式 2：Semaphore 限制
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

// 模式 3：固定 Worker Pool
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
--- 輕量任務 (100 次迴圈, 10000 任務) ---
  每任務一個 goroutine:   10.40ms
  Semaphore 限制池:       17.04ms   ← 更慢！channel 開銷
  固定 Worker Pool:        5.91ms   ← 最快

--- 重量任務 (100000 次迴圈, 1000 任務) ---
  每任務一個 goroutine:    5.53ms   ← 反而最快
  Semaphore 限制池:       10.04ms
  固定 Worker Pool:        7.49ms
```

### 結論

| 情境 | 建議 |
|------|------|
| 輕量任務 + 大量任務 | 固定 Worker Pool 勝出 |
| 重量任務 + 少量任務 | 每任務一個 goroutine 就好 |
| 需控制資源 | 使用 Pool（目的是限制而非加速） |
| 不確定 | 先用最簡單的方式，有問題再優化 |

---

## 5. GOMEMLIMIT 與 GOGC 調校

### GOGC — 控制 GC 頻率

**公式**：`觸發 GC 的堆大小 = 存活堆 + (存活堆 + GC roots) × GOGC / 100`

```bash
export GOGC=100   # 預設：堆增長 100% 後觸發 GC
export GOGC=200   # 減少 GC 頻率（更多記憶體，更少 CPU 開銷）
export GOGC=50    # 增加 GC 頻率（更少記憶體，更多 CPU 開銷）
export GOGC=off   # 完全關閉 GC（需搭配 GOMEMLIMIT）
```

### GOMEMLIMIT — 記憶體軟上限（Go 1.19+）

```bash
export GOMEMLIMIT=512MiB
# 在容器中：留 5-10% 給 runtime 開銷
# 容器 1GiB → GOMEMLIMIT=900MiB
```

### 組合使用決策樹

```
Q: 在容器 / 固定記憶體環境中？
├─ Yes → 設定 GOMEMLIMIT（留 10% buffer）
│   ├─ CPU 敏感 → GOGC=200 或更高
│   └─ 記憶體敏感 → GOGC=50
│
└─ No → 通常不需要設 GOMEMLIMIT
    ├─ CPU 敏感 → 提高 GOGC
    └─ 預設 GOGC=100 夠用
```

### 調校效果對照表

| 調校 | GC 頻率 | CPU 開銷 | 記憶體用量 | 延遲 |
|------|---------|---------|-----------|------|
| GOGC ↑ | ↓ 降低 | ↓ 降低 | ↑ 增加 | ↓ 降低 |
| GOGC ↓ | ↑ 增加 | ↑ 增加 | ↓ 減少 | ↑ 增加 |
| GOMEMLIMIT ↓ | ↑ 增加 | ↑ 增加 | ↓ 受限 | ↑ 增加 |

---

## 6. 不要過早手動控制並行度

Go runtime 的排程器（GMP 模型）已經非常成熟：

```
┌─────────────────────────────────────────────┐
│              Go Runtime Scheduler            │
├─────────────────────────────────────────────┤
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
└─────────────────────────────────────────────┘
```

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
// ✅ 確認是並行度問題後才引入 pool，並用 benchmark 驗證
```

| 該用 Pool | 不需要 Pool |
|-----------|------------|
| 限制外部資源（DB 連線、API rate limit） | 純 CPU 計算任務 |
| 任務數量極大（百萬級）且記憶體受限 | 任務數量適中（幾千到幾萬） |
| 需要背壓（backpressure）機制 | Go runtime 排程就能處理 |
| benchmark 證實 pool 確實更快 | 「感覺」pool 應該更快 |

---

# 第四部分：高併發場景實務問題

理論和工具都到位之後，真正的挑戰來自**生產環境的實務問題**。本節以交易系統為背景，整理 Go 開發中最常遇到的問題，從 Concurrency、Memory、Debug 到 Production 場景，每個問題都附上可執行的範例程式碼和實際輸出。

## 一、Concurrency 實務問題

### 1. goroutine ≠ OS Thread

goroutine 是 Go 的「輕量級執行緒」，一個 goroutine 只佔幾 KB 記憶體（OS thread 至少 1MB），Go runtime 會自動把成千上萬的 goroutine 分配到少數 OS thread 上跑。

- Go 採用 M:N Scheduler（G / M / P 模型）
  - **G** = Goroutine（工作單元）
  - **M** = Machine（OS Thread）
  - **P** = Processor（邏輯處理器，數量 = GOMAXPROCS）

**GOMAXPROCS 對效能的影響：**

```go
func main() {
    for _, procs := range []int{1, 2, 4, runtime.NumCPU()} {
        runtime.GOMAXPROCS(procs)
        start := time.Now()
        var wg sync.WaitGroup
        for i := 0; i < 4; i++ {
            wg.Add(1)
            go func() {
                defer wg.Done()
                cpuWork() // CPU-bound 計算
            }()
        }
        wg.Wait()
        fmt.Printf("GOMAXPROCS=%d → 耗時: %v\n", procs, time.Since(start))
    }
}
```

```text
GOMAXPROCS=1  → 耗時: 51.970377ms   ← 只有 1 個核心，4 個任務排隊跑
GOMAXPROCS=2  → 耗時: 22.214338ms   ← 2 核並行，快了一倍
GOMAXPROCS=4  → 耗時: 17.586621ms   ← 4 核剛好跑 4 個任務
GOMAXPROCS=28 → 耗時: 11.724444ms   ← 核心再多也只有 4 個任務
```

> 交易系統通常設成 `runtime.NumCPU()` 就好（Go 預設值）。容器環境下建議用 `go.uber.org/automaxprocs` 自動偵測 cgroup 限制。

### 2. Data Race

兩個 goroutine 同時讀寫同一塊記憶體，結果不確定。最經典的就是 **map 併發寫入直接 panic**。

**正確做法（三種方式）：**

```go
// 方法 1：sync.Mutex
mu.Lock()
m[key] = id
mu.Unlock()

// 方法 2：sync.Map（讀多寫少場景更適合）
sm.Store(key, value)

// 方法 3：slice append 也要加鎖
mu.Lock()
results = append(results, val)
mu.Unlock()
```

```bash
# 開發期間一定要用 race detector 跑
go run -race main.go
go test -race ./...
```

> **交易系統重點：** 行情推送（寫）和策略讀取（讀）是典型的讀多寫少場景，用 `sync.RWMutex` 或 `sync.Map` 比普通 `Mutex` 效能更好。

---

## 二、Memory & GC 問題

### 1. GC Pause / Latency Spike

Go 的 GC 會在背景自動清理不再使用的記憶體。Go 1.8+ 已經把 pause 壓到 1ms 以下，但對交易系統來說，一次 100μs 的 GC pause 就可能讓你的報價比別人慢一拍。

**觀察 GC 行為：**

```go
start := time.Now()
runtime.GC()
gcTime := time.Since(start)

var stats debug.GCStats
debug.ReadGCStats(&stats)
fmt.Println("GC 次數:", stats.NumGC)
fmt.Printf("手動 GC 耗時: %v\n", gcTime)
```

> **交易系統 GC 調參建議：**
> - `GOGC=20~50`：更頻繁 GC，每次 pause 更短，適合低延遲
> - `GOMEMLIMIT`（Go 1.19+）：設定記憶體上限，避免 OOM
> - 終極手段：用 `sync.Pool` 重用物件，從源頭減少 GC 壓力

### 2. Escape Analysis

Go 編譯器會自動判斷變數該放 stack 還是 heap。放 stack 幾乎零成本，放 heap 則需要 GC 介入。

```go
//go:noinline
func stackAlloc() int {
    x := 42   // ✅ x 留在 stack
    return x
}

//go:noinline
func heapAlloc() *int {
    x := 42    // ❌ x 逃逸到 heap，因為回傳了指標
    return &x
}
```

用 `-gcflags="-m"` 看逃逸分析結果：

```bash
go build -gcflags="-m" escape_demo.go
```

> 交易系統的 hot path（撮合、行情處理）盡量用值傳遞，避免逃逸。

---

## 三、Debug 實務問題

### Goroutine Dump 實戰

當程式「卡住了」但不知道卡在哪，用 `runtime.Stack()` 把所有 goroutine 的狀態印出來：

```go
func dumpGoroutines() {
    buf := make([]byte, 1024*64)
    n := runtime.Stack(buf, true) // true = dump 所有 goroutine
    fmt.Fprintf(os.Stderr, "=== Goroutine Dump ===\n%s\n", buf[:n])
}
```

重點看 `[chan receive]`、`[select]`、`[semacquire]` 這些狀態，代表 goroutine 在「等東西」。

### 常見 Debug 場景

| 症狀 | 工具 | 看什麼 |
|------|------|--------|
| 程式卡住不動 | `runtime.Stack()` | 找 `[chan receive]` / `[select]` |
| CPU 飆高 | `go tool pprof` | 找 hot function |
| 記憶體一直漲 | `go tool pprof -alloc_space` | 找誰在大量配記憶體 |
| 懷疑 deadlock | `dlv` + breakpoint | 看鎖的持有狀態 |

---

## 四、Channel 死鎖問題

Channel 就像一個傳話筒——有人說話就要有人聽。unbuffered channel 送收必須同時發生，buffered channel 則像信箱，塞滿才會卡住。

**select 搭配 timeout / context（交易系統必備）：**

```go
select {
case msg := <-ch:
    fmt.Println("收到:", msg)
case <-time.After(1 * time.Second):
    fmt.Println("超時！")
}

// 推薦用 context
ctx, cancel := context.WithTimeout(context.Background(), 500*time.Millisecond)
defer cancel()
select {
case msg := <-ch:
    fmt.Println("收到:", msg)
case <-ctx.Done():
    fmt.Println("context 超時:", ctx.Err())
}
```

> **死鎖防治口訣：**
> 1. unbuffered channel 送收必須配對
> 2. range channel 一定要 close
> 3. 交易系統永遠加 timeout
> 4. 不確定就用 buffered channel

---

## 五、HTTP Server 問題

### Connection Leak

每次 HTTP 請求都會開一條 TCP 連線。忘記關 `resp.Body`，連線就不會被回收。

```go
// ✅ 正確做法
client := &http.Client{Timeout: 5 * time.Second}
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := client.Do(req)
if err != nil { return }
defer resp.Body.Close()
body, _ := io.ReadAll(resp.Body)
```

### Context 沒傳

如果啟動 goroutine 呼叫 API 但沒傳 context，當使用者斷線或 timeout 時，goroutine 還是會繼續跑，導致 goroutine leak。

---

## 六、Production 常見問題

### 1. Goroutine Leak

啟動了 goroutine 但它永遠不會結束。一個 goroutine 佔幾 KB 記憶體，漏個幾萬個就是幾百 MB。

```go
// ❌ 會 leak：沒人 send 也沒人 close
func leakyWorker() {
    ch := make(chan int)
    go func() { <-ch }()
}

// ✅ 安全版本
func safeWorker(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            return
        }
    }()
}
```

> **防 leak 三原則：**
> 1. 每個 goroutine 都要有退出機制（context / done channel / timeout）
> 2. 用 `runtime.NumGoroutine()` 監控 goroutine 數量
> 3. Production 用 pprof 的 `/debug/pprof/goroutine` 端點觀察

### 2. FD 用光 & TCP TIME_WAIT

```bash
# 調大系統限制
ulimit -n 65535
```

```go
// 正確設定 HTTP Transport
transport := &http.Transport{
    MaxIdleConns:        100,
    MaxIdleConnsPerHost: 100,
    IdleConnTimeout:     90 * time.Second,
    DisableKeepAlives:   false,
}
var globalClient = &http.Client{Transport: transport}
```

---

## 七、進階優化方向

### sync.Pool：物件重用

頻繁 `new` 物件再丟掉，GC 會很累。`sync.Pool` 就像「物件回收站」。

```go
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
    ob.Bids = ob.Bids[:0]
    ob.Asks = ob.Asks[:0]
    return ob
}

func putOrderBook(ob *OrderBook) {
    orderBookPool.Put(ob)
}
```

### 其他優化方向

| 技術 | 說明 | 交易系統場景 |
|------|------|-------------|
| **object reuse** | 預先配好物件反覆使用 | Tick、Order 結構重用 |
| **zero copy** | 避免不必要的記憶體複製 | 行情解析，直接操作 byte slice |
| **netpoll** | Go 底層的非同步 I/O | 大量 WebSocket 連線 |
| **lock contention** | 減少鎖競爭 | 用 `atomic` 取代 `Mutex` 做計數器 |
| **runtime scheduler** | 理解 G/M/P 排程行為 | 避免 goroutine 在 hot path 被搶佔 |

---

## 八、壓測工具

| 工具 | 語言 | 特色 | 適用場景 |
|------|------|------|----------|
| **k6** | JS (Go 引擎) | 腳本化場景 | 複雜 API 流程測試 |
| **wrk** | C | 極輕量 | 單一端點最大 RPS |
| **vegeta** | Go | 固定 RPS 模式 | latency 分析 |
| **hey** | Go | 簡單好用 | 快速壓一下看結果 |

```bash
hey -z 10s -c 200 http://localhost:8080/api/ticker
echo "GET http://localhost:8080/api/ticker" | vegeta attack -rate=1000 -duration=30s | vegeta report
```

---

## 九、Module / Dependency 問題

### replace directive

```go
// go.mod — 暫時用本地修改版
replace github.com/some/exchange-sdk => ../my-exchange-sdk
```

### 私有 repo

```bash
export GOPRIVATE=github.com/mycompany/*
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

### vendor 模式

```bash
go mod vendor
go build -mod=vendor ./...
```

---

# 附錄：Go 開發常用工具整理

## 工具總覽

| 工具 | 功能 | 一句話說明 |
|------|------|-----------|
| [Delve](https://github.com/go-delve/delve) | Debugger / Trace | Go 專用 debugger，支援 goroutine 切換、條件斷點 |
| [pprof](https://github.com/google/pprof) | Profiling 火焰圖 | CPU / Memory / Goroutine 的瑞士刀 |
| [statsviz](https://github.com/arl/statsviz) | 即時 Web 儀表板 | 一行程式碼開啟 runtime metrics 儀表板 |
| [go-callvis](https://github.com/ondrajz/go-callvis) | 呼叫運行圖 | 靜態分析產生互動式呼叫圖 SVG |
| [fgprof](https://github.com/felixge/fgprof) | CPU + Off-CPU Trace | 同時追蹤 CPU 和 I/O 等待時間 |

## 安裝方式

```bash
go install github.com/go-delve/delve/cmd/dlv@latest
go install github.com/google/pprof@latest
go install github.com/ofabry/go-callvis@latest
# statsviz / fgprof 是 library，go get 即可
```

## Delve 常用指令

```bash
dlv debug main.go

(dlv) break main.main          # 設斷點
(dlv) continue                 # 繼續執行
(dlv) next                     # 下一行（不進入函式）
(dlv) step                     # 下一行（進入函式）
(dlv) print myVar              # 印變數值
(dlv) goroutines               # 列出所有 goroutine
(dlv) goroutine 5              # 切換到 goroutine 5
(dlv) stack                    # 看當前 call stack

# 條件斷點
(dlv) break main.go:30
(dlv) condition 1 price > 50000

# attach 到正在跑的 process
dlv attach <PID>
```

## pprof 常用指令

```bash
# CPU profiling
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# Memory profiling
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine profiling（找 leak 必用）
go tool pprof http://localhost:6060/debug/pprof/goroutine

# 直接在瀏覽器看火焰圖
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/heap
```

## fgprof — CPU + Off-CPU 混合 Profiling

標準 pprof 只看 CPU 在跑的時間，fgprof 同時追蹤 CPU 時間和等待時間：

```go
http.DefaultServeMux.Handle("/debug/fgprof", fgprof.Handler())
```

> pprof：「CPU 花最多時間在哪個函式？」
> fgprof：「程式花最多時間在哪個函式？」（包含等待 I/O、sleep、鎖）

## 完整工具鏈使用流程

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

## 環境變數速查

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

## 效能優化流程

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

## 建議練習方式

| 練習 | 會碰到什麼問題 | 學到什麼 |
|------|---------------|---------|
| 1. 寫高併發 REST API | data race, connection leak | Mutex, context, http client 設定 |
| 2. 模擬撮合引擎 | lock contention, GC pause | sync.Pool, atomic, 逃逸分析 |
| 3. 寫 WebSocket server | goroutine leak, FD 用光 | context 控制, transport 設定 |
| 4. benchmark + pprof 分析 | 找不到瓶頸 | pprof 火焰圖、trace 分析 |
| 5. 壓測壓到出現瓶頸 | 各種 production 問題 | 調參、診斷、修復的完整流程 |

**推薦練習順序：** 1 → 4 → 3 → 2 → 5（由易到難）

---

# 總結

本文從四個維度完整涵蓋了 Go 語言的進階實戰知識：

1. **語言設計哲學**：Go 刻意捨棄了 C++ 的複雜機制（繼承、例外處理、運算子重載），換來更簡單、更不容易出錯的程式碼。核心轉換心法是「小 interface + 組合 + 明確錯誤處理」。

2. **觀察與追蹤能力**：五種互補的函數呼叫追蹤方法——go-callvis 看架構、tracer.Enter() 看執行路徑、eBPF 做生產環境追蹤、pprof 做效能分析、runtime/trace 看並發行為。工具選擇的關鍵在於「你想回答什麼問題」。

3. **並行效能優化**：False Sharing、GC 壓力、Goroutine Pool 陷阱等議題提醒我們，「容易寫出並行程式碼」不等於「高效的並行程式碼」。正確的優化流程是先 benchmark、再 profile、最後針對性修改，而非憑直覺加 pool 或調參數。

4. **生產環境實務**：Data Race、Goroutine Leak、Connection Leak、FD 耗盡、Channel 死鎖——這些都是高併發場景下的常客。防治的核心原則是：永遠加 timeout、永遠有退出機制、永遠用工具驗證而非靠肉眼判斷。

**一句話總結：** Go 的簡單不是限制，而是設計。用好它的工具鏈，遵循「先正確、再觀察、後優化」的流程，就能寫出既簡潔又高效的程式碼。

---

## 參考資源

- [Go 官方 GC 調校指南](https://go.dev/doc/gc-guide)
- [Go 1.22 Execution Traces 改進](https://go.dev/blog/execution-traces-2024)
- [100 Go Mistakes #92: False Sharing](https://100go.co/92-false-sharing/)
- [GOMEMLIMIT is a Game Changer (Weaviate)](https://weaviate.io/blog/gomemlimit-a-game-changer-for-high-memory-applications)
- [Go Performance Optimization Guide](https://goperf.dev/01-common-patterns/gc/)
- [runtime/trace 套件文件](https://pkg.go.dev/runtime/trace)
