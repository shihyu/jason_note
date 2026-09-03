# Go 現代風格與最佳實踐指南（Uber Guide 增補版）

> 本文件由 `README.md`（[uber-go/guide](https://github.com/uber-go/guide) 繁體中文翻譯）延伸整理而成，
> 目的是補上三塊 `README.md` 目前缺的內容，最終作為 Go 開發用 skill 的素材：
>
> 1. **上游同步差距**：`README.md` 目前同步至上游 commit `42f94b6`（2023-04-11），距今已約 2.5 年，上游有實質規則變更未同步。
> 2. **Effective Go 的設計哲學補充**：[Effective Go](https://go.dev/doc/effective_go) 中一些 Uber Guide 沒特別談的深層概念。
> 3. **Go 1.18 → 1.27 現代語言 / 標準庫特性**：Uber Guide 完全沒提到泛型與 2021 年之後的標準庫演進。
>
> **本文件不取代 `README.md`**：`README.md` 仍是逐條規範的權威內容，本文件是「更新清單 + 現代化擴充」。

---

## 目錄

- [Part 1｜README.md 待同步清單](#part-1readmemd-待同步清單)
- [Part 2｜Effective Go 補充：Uber Guide 未強調的設計哲學](#part-2effective-go-補充uber-guide-未強調的設計哲學)
- [Part 3｜現代 Go（1.18–1.27）語言與標準庫特性](#part-3現代-go118127語言與標準庫特性)
- [Part 4｜快速檢查清單](#part-4快速檢查清單)
- [參考來源](#參考來源)

---

## Part 1｜README.md 待同步清單

比對基準：`README.md` 記錄的上游 commit `42f94b6`（2023-04-11） vs. 上游 `master` 最新內容。以下依「是否影響規則本身的邏輯/內容」分三個優先序。

### 🔴 必改：規則內容或邏輯已變更

| 章節 | 上游變更 | 建議動作 |
|---|---|---|
| 主函式結束方式 → 只結束一次（Exit Once） | 新增約 40 行說明：明確聲明 `run()` 的名稱/簽名/位置**不是規範性的**；補充第二種寫法（`run()` 回傳 exit code `int` 而非 `error`，方便測試直接斷言 exit code）；澄清 `log.Fatal`／`os.Exit` 建議同樣適用於任何呼叫 `os.Exit` 的 library code。唯一硬性要求：`main()` 只能有一處真正離開程序。 | 補譯這段擴充內容，避免讀者誤以為 `run()` 這個模式是唯一寫法 |
| 縮小變數作用域 | 新增規則：**常數不需要放在全域**，除非被多個函式/檔案共用，或屬於套件對外的合約（external contract）。附 Bad（頂層 `const (...)`）/Good（宣告在使用它的函式內）範例。 | 補上此規則與範例 |
| 編程模式 → 表格驅動測試 | 新增兩個小節：①**Avoid Unnecessary Complexity in Table Tests**——主張表格測試不該塞入複雜/條件分支邏輯（用「test depth」概念類比 cyclomatic complexity），建議拆成多個獨立 `Test...` 函式；② **Parallel Tests** 獨立成小節標題。 | 補上這兩個小節（含 Bad/Good 範例） |
| 要對建立的 goroutine 負責 → 等待 goroutines 結束 | 因 Go 1.25 新增 `sync.WaitGroup.Go` 方法，範例從手動 `wg.Add(1)` + `go func(){ defer wg.Done(); ... }()` 改寫為 `wg.Go(...)` 單行寫法。 | 更新範例程式碼（見 [Part 3](#sync.waitgroup.go-go-1.25)） |
| 效能 → 指定容器容量 → 指定 Map 容量提示 | 範例型別從 `os.FileInfo` 改為 `os.DirEntry`（原範例型別有誤，`os.ReadDir` 回傳的本就是 `DirEntry`）；說明文字修正為「map 動態調整大小時，growth 過程會造成多次記憶體配置」。 | 修正範例型別與說明文字 |
| Linting | 移除 `golint`（已廢棄），改推薦 `revive`（golint 的現代化後繼者，速度更快）。 | 更新 Lint 工具建議清單 |

#### 對應範例

**縮小變數作用域 — 常數不需要放在全域**

```go
// Bad：套件內部才用得到的常數放在全域
const (
    defaultTimeout = 5 * time.Second
    maxRetries     = 3
)

func NewClient() *Client {
    return &Client{timeout: defaultTimeout, retries: maxRetries}
}
```

```go
// Good：宣告在唯一使用它的函式內
func NewClient() *Client {
    const (
        defaultTimeout = 5 * time.Second
        maxRetries     = 3
    )
    return &Client{timeout: defaultTimeout, retries: maxRetries}
}
```

**表格驅動測試 — Avoid Unnecessary Complexity in Table Tests**

```go
// Bad：單一 Test 函式裡塞條件分支，測試邏輯難以一眼看懂
func TestValidate(t *testing.T) {
    tests := []struct {
        name      string
        input     string
        wantErr   bool
        checkCode bool // 只有部分案例才需要的額外旗標，讓邏輯分岔
    }{
        {"empty", "", true, false},
        {"too long", strings.Repeat("a", 300), true, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            err := Validate(tt.input)
            if tt.checkCode {
                var verr *ValidationError
                if !errors.As(err, &verr) {
                    t.Fatalf("want ValidationError, got %v", err)
                }
            }
            if (err != nil) != tt.wantErr {
                t.Errorf("Validate(%q) error = %v, wantErr %v", tt.input, err, tt.wantErr)
            }
        })
    }
}
```

```go
// Good：拆成獨立測試，每個 Test 函式只驗證一件事
func TestValidate_EmptyInput(t *testing.T) {
    if err := Validate(""); err == nil {
        t.Error("want error for empty input")
    }
}

func TestValidate_TooLong(t *testing.T) {
    var verr *ValidationError
    err := Validate(strings.Repeat("a", 300))
    if !errors.As(err, &verr) {
        t.Fatalf("want ValidationError, got %v", err)
    }
}
```

**Map 容量提示 — 修正後型別（`os.DirEntry`）**

```go
entries, _ := os.ReadDir(root)

sizes := make(map[string]int64, len(entries)) // 預先提示容量，避免多次 rehash
for _, e := range entries {
    info, err := e.Info() // os.DirEntry → os.FileInfo，才能拿到 Size()
    if err != nil {
        continue
    }
    sizes[e.Name()] = info.Size()
}
```

**主函式結束方式 — `run()` 回傳 exit code 的第二種寫法**

```go
func main() {
    os.Exit(run())
}

// run() 的名稱、簽名、位置都不是規範性的；
// 這裡回傳 int（exit code）而非 error，方便測試直接斷言退出碼。
func run() int {
    if err := doWork(); err != nil {
        log.Println(err)
        return 1
    }
    return 0
}
```

**Linting — `revive` 設定範例**

```yaml
# .golangci.yml
linters:
  disable:
    - golint  # 已廢棄
  enable:
    - revive
```

### 🟡 應改：範例程式碼有 Bug

| 位置 | 問題 | 修正 |
|---|---|---|
| 要對建立的 goroutine 負責 → 不要在 `init()` 使用 goroutines | `NewWorker` 範例遺漏 `return w` | 補上 `return w` |
| 使用 `go.uber.org/atomic` | 範例語法錯誤 `func (f* foo) start()` | 修正為 `func (f *foo) start()` |
| 表格驅動測試（Parallel Tests） | `tt := tt // for t.Parallel` 這行技巧，因 Go 1.22 起迴圈變數語義變更已不再需要 | 移除該行，並可加註說明「Go 1.22+ 才可省略」（見 [Part 3](#迴圈變數語意變更-go-122強烈建議先讀)） |

#### 對應修正範例

**`NewWorker` 遺漏 `return w`**

```go
// Bad：忘記 return，呼叫端拿到 nil
func NewWorker(name string) *Worker {
    w := &Worker{name: name}
    go w.run()
}
```

```go
// Good
func NewWorker(name string) *Worker {
    w := &Worker{name: name}
    go w.run()
    return w
}
```

**`go.uber.org/atomic` 語法錯誤**

```go
// Bad：`*` 位置錯誤，無法通過編譯
func (f* foo) start() { ... }
```

```go
// Good
func (f *foo) start() { ... }
```

### 🟢 可選：文字潤飾與連結網域

- 大量 `golang.org/pkg|doc|ref` 連結可統一改為 `go.dev/...`（上游已於 2024-01 批量更新過，本翻譯目前新舊網域混用，例如「使用 time 處理時間」一節已用 `go.dev`，但多數其他章節仍是 `golang.org`）。
- `Avoid string-to-byte conversion` 標題已改為 `Avoid repeated string-to-byte conversions`（規則本文未變，只是標題更精確）。
- 幾處英文原文文字潤飾（如 "causing a lot of noise" → "makes a lot of noise"），影響不大，可視情況跟著調整譯文用字。

### 本地翻譯品質問題（與上游同步無關）

- **錯誤章節**：有一句英文原文殘留未翻譯（"Callers further up the stack will handle the error."），與下一句中譯重複，建議整合成一句。
- **錯誤章節表格**：其中一個表格標題「較佳做法：Match the error and degrade gracefully」漏翻，同表其他三個標題都已中文化，風格不一致。
- **使用 `go.uber.org/atomic`**：規則理由「隱藏基底類型以增加型別安全」自 Go 1.19 起部分過時——標準庫 `sync/atomic` 已內建 `atomic.Bool`/`atomic.Int32`/`Int64`/`Uint32`/`Uint64`/`Pointer[T]`，API 幾乎一致。建議補充說明：Go 1.19+ 專案可考慮直接用標準庫達成同樣效果，`go.uber.org/atomic` 剩下的主要優勢是內建 JSON 序列化支援（詳見 [Part 3](#syncatomic-泛型型別-go-119)）。

---

## Part 2｜Effective Go 補充：Uber Guide 未強調的設計哲學

Uber Guide 是「規則清單」，[Effective Go](https://go.dev/doc/effective_go) 是「設計哲學」。以下是 Effective Go 裡值得補進參考素材、但 Uber Guide 沒特別展開的部分。

### 格式化：gofmt 是唯一裁決者

不要爭論大括號位置、縮排寬度——`gofmt` 已經是全 Go 社群唯一標準，把格式爭議直接交給工具，不要在 code review 上討論風格。控制結構（`if`/`for`/`switch`）的左大括號必須與關鍵字同行，這不是美感選擇，而是 Go 的分號自動插入規則所要求的語法限制。

### Doc Comment 慣例

緊鄰在宣告之前、**中間沒有空行**的註解會被 `go doc`／`godoc` 視為該識別字的文件註解。套件層級的說明應寫在 `package foo` 前一行，以完整句子開頭（例如 `// Foo does the thing.`），這樣產出的文件才會通順。

```go
// Reader implements buffered reading from an io.Reader.
type Reader struct { ... }
```

### Control Structure 深化

- `if` 可搭配初始化陳述式：`if err := f(); err != nil { ... }`，把變數作用域限制到最小。
- `switch` 省略表達式時等同 `if-else-if` 鏈，比巢狀 `if` 更清楚。
- 需要跳出巢狀迴圈時，用 **labeled break/continue**，而不是額外開一個布林旗標變數。

```go
Loop:
    for i := range rows {
        for j := range cols {
            if shouldStop(i, j) {
                break Loop
            }
        }
    }
```

```go
// if 搭配初始化陳述式：err 的作用域只到這個 if/else 區塊結束
if err := f(); err != nil {
    return err
}

// switch 省略表達式，等同 if-else-if 鏈，但更清楚
switch {
case n < 0:
    fmt.Println("negative")
case n == 0:
    fmt.Println("zero")
default:
    fmt.Println("positive")
}
```

### 命名回傳值（Named Result）與裸 return

命名回傳值可以直接在函式簽名寫出語意（例如 `func Div(a, b int) (quotient, remainder int)`），搭配「裸 `return`」可以省去重複列出變數。但裸 `return` 在長函式裡會讓人看不出實際回傳什麼，**只建議在短函式**使用，這是 Effective Go 明確提示的可讀性取捨，Uber Guide 沒有討論到。

```go
// 短函式：命名回傳值 + 裸 return 讓語意一目了然
func Div(a, b int) (quotient, remainder int) {
    quotient = a / b
    remainder = a % b
    return // 裸 return：直接回傳 quotient, remainder
}
```

```go
// 長函式：裸 return 會讓人看不出實際回傳什麼，應明確列出
func ProcessOrder(o Order) (total float64, err error) {
    // ...（20 行驗證與計算邏輯）...
    return total, err // 明確寫出，而非裸 return
}
```

### 零值可用（Zero Value Usable）——比「零值 Mutex」更通用的原則

Uber Guide 只講了「零值 Mutex 是有效的」，但這其實是 Go 的一個更廣的設計哲學：**盡量把型別設計成宣告後（零值）就可以直接使用，不需要顯式建構函式**。標準庫 `bytes.Buffer`、`sync.WaitGroup` 都是這個原則的範例。設計自己的型別時，應該優先考慮「零值有沒有意義」，而不是預設都要寫 `NewXxx()`。

```go
// Bad：即使零值語意上已經可用，仍強迫呼叫者透過建構函式
type Counter struct {
    mu sync.Mutex
    n  int
}

func NewCounter() *Counter { return &Counter{} } // 沒有實際初始化邏輯，多此一舉

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.n++
}
```

```go
// Good：零值直接可用，呼叫端可以省略建構函式
type Counter struct {
    mu sync.Mutex
    n  int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.n++
}

var c Counter // 零值即可用，不需要 NewCounter()
c.Inc()
```

### Array 與 Slice 的值語意差異

這是理解 Uber Guide「在邊界處複製切片和 Maps」規則的前提知識，但 Uber Guide 沒有解釋原理：**Array 賦值/傳參是整個陣列的完整複製**；**Slice 是指向底層陣列的描述符（指標 + 長度 + 容量），賦值/傳參只複製描述符，底層資料仍共享**。這正是為什麼 slice 在邊界（函式參數、回傳值、struct 欄位）需要額外注意複製，而 array 不需要。

```go
var a1 [3]int = [3]int{1, 2, 3}
a2 := a1        // 完整複製，修改 a2 不影響 a1
a2[0] = 99      // a1 仍是 [1 2 3]

s1 := []int{1, 2, 3}
s2 := s1        // 只複製描述符，共享底層陣列
s2[0] = 99      // s1 也變成 [99 2 3]
```

### Stringer 與格式化慣例深化

實作 `String() string` 時，**絕對不要在 `String()` 內部用 `%v` 或 `%s` 格式化自己**，否則會觸發無限遞迴（`fmt` 會再呼叫一次 `String()`）。另外要清楚區分 `%v`（預設格式）、`%+v`（含欄位名稱）、`%#v`（Go 語法表示）、`%T`（型別名稱）的用途差異，這是除錯時最常用但也最常混淆的細節。

```go
type Level int

const (
    Debug Level = iota
    Info
)

func (l Level) String() string {
    switch l {
    case Debug:
        return "debug"
    case Info:
        return "info"
    default:
        return "unknown"
    }
}
```

```go
// Bad：在 String() 內部用 %v 格式化自己
func (l Level) String() string {
    return fmt.Sprintf("%v", l) // fmt 偵測到 Stringer，再次呼叫 String() → 無限遞迴、stack overflow
}
```

```go
type point struct{ X, Y int }

p := point{1, 2}
fmt.Printf("%v\n", p)  // {1 2}         預設格式
fmt.Printf("%+v\n", p) // {X:1 Y:2}     含欄位名稱
fmt.Printf("%#v\n", p) // main.point{X:1, Y:2}  Go 語法表示
fmt.Printf("%T\n", p)  // main.point    型別名稱
```

### Embedding 的設計意圖

Effective Go 說明了 embedding 真正該用在哪：讓外層型別「免費」取得內層型別的方法（method promotion），或用 interface embedding 組合出更大的介面（如 `io.ReadWriter = io.Reader + io.Writer`）。這跟 Uber Guide「避免在公用結構體中嵌入類型」是同一件事的兩面——Effective Go 說明「什麼時候該用」，Uber Guide 說明「公開 API 時為什麼要小心」，兩者搭配才完整。

```go
// Method promotion：Service 「免費」取得 Logger 的方法
type Logger struct{}

func (Logger) Log(msg string) { fmt.Println(msg) }

type Service struct {
    Logger // 嵌入
}

s := Service{}
s.Log("started") // 等同 s.Logger.Log("started")
```

```go
// Interface embedding：組合出更大的介面
type ReadWriter interface {
    io.Reader
    io.Writer
}
```

### 並發設計哲學：CSP，不只是「開 goroutine」

Effective Go 的核心並發主張是「用通信共享資料，而不是共享記憶體然後互相鎖」（源自 CSP）。幾個 Uber Guide 沒提到但很實用的慣用法：

- 用 `chan struct{}` 當**信號量**或「完成通知」，而非傳遞實際資料。
- `select` 搭配 `default` 可以做**非阻塞的 leaky buffer**：滿了就丟棄最舊/新資料而不阻塞。

```go
done := make(chan struct{})

go func() {
    defer close(done)
    doWork()
}()

<-done // 只關心「完成了沒」，不傳遞任何資料
```

```go
select {
case ch <- msg:
default:
    // channel 已滿，非阻塞放棄，避免拖慢上游
}
```

### panic / recover 的正確用途

Uber Guide 教「不要使用 panic」，Effective Go 補充**什麼時候 recover 才是慣用法**：只用於**隔離故障邊界**（例如伺服器每個請求各自 recover，避免一個請求的 panic 拖垮整個行程），絕對不能把 `panic`/`recover` 當成一般錯誤處理機制的替代品。

```go
func safeHandle(h http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        defer func() {
            if err := recover(); err != nil {
                log.Printf("panic recovered: %v", err)
                w.WriteHeader(http.StatusInternalServerError)
            }
        }()
        h.ServeHTTP(w, r)
    })
}
```

---

## Part 3｜現代 Go（1.18–1.27）語言與標準庫特性

Uber Guide 成文於泛型之前，完全沒提到 2022 年之後的語言演進。以下依版本整理，**全部已透過官方 release notes 二次驗證**。目前最新穩定版為 **Go 1.27**（2026-08-19 發布，最新修訂版 1.27.1）。

### Generics 泛型（Go 1.18 起）

型別參數讓容器/演算法可以脫離 `interface{}` 或程式碼生成。注意：Go 1.21 已把 `min`/`max` 做成內建函式，所以泛型最有價值的場景是**自訂容器**，不是重新發明 `Max()`。

```go
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(v T) { s.items = append(s.items, v) }

func (s *Stack[T]) Pop() (v T, ok bool) {
    if len(s.items) == 0 {
        return v, false // v 是 T 的零值
    }
    v, s.items = s.items[len(s.items)-1], s.items[:len(s.items)-1]
    return v, true
}
```

版本演進：Go 1.20 鬆綁 `comparable` 約束；Go 1.24 支援泛型型別別名；**Go 1.26 解除「泛型型別不可在自己的型別參數列表中自我參照」的限制**：

```go
// Go 1.26 起合法
type Adder[A Adder[A]] interface {
    Add(A) A
}
```

### `slices` / `maps` / `cmp` 標準庫套件（Go 1.21 起）

取代大量手寫的排序、比較、去重迴圈；Go 1.23 起兩個套件都補上了 iterator 版本函式（`maps.Keys`、`maps.Values` 等回傳 `iter.Seq`）。

```go
import "slices"

s := []int{3, 1, 2}
slices.Sort(s)                      // [1 2 3]
slices.Contains(s, 2)               // true
i, found := slices.BinarySearch(s, 2)

import "maps"
m := map[string]int{"a": 1, "b": 2}
keys := slices.Sorted(maps.Keys(m)) // Go 1.23+：排序後的 key 清單
```

### 內建 `min` / `max` / `clear`（Go 1.21）

```go
lo := min(3, 7, 1) // 1
hi := max(3, 7, 1) // 7

m := map[string]int{"a": 1}
clear(m)           // 清空 map，但保留底層記憶體（比重新 make 更省）
```

### range over int（Go 1.22）

```go
for i := range 5 {
    fmt.Println(i) // 0 1 2 3 4
}
```

### 迴圈變數語意變更（Go 1.22，**強烈建議先讀**）

這是對 Uber Guide 影響最直接的一個變更：**Go 1.22 起，`for` 迴圈的每次疊代都會建立獨立的迴圈變數**（過去整個迴圈只有一個變數，所有疊代共用）。這修正了 goroutine/closure 捕捉迴圈變數的經典 bug，也讓 Uber Guide 原本教的 `tt := tt` 技巧在新版 Go 變成多餘。

```go
// Go 1.21 及以前：所有 closure 共用同一個 i，結果印出 3 3 3
funcs := make([]func(), 0, 3)
for i := 0; i < 3; i++ {
    funcs = append(funcs, func() { fmt.Println(i) })
}

// Go 1.22 起：每次疊代都是新的 i，結果印出 0 1 2
```

```go
// Uber Guide 原本教的寫法（Go < 1.22 必須這樣）
for _, tt := range tests {
    tt := tt // 沒有這行，t.Parallel() 下所有 subtest 會共用最後一筆 tt
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // 使用 tt ...
    })
}

// Go 1.22+ 可以直接省略這行
for _, tt := range tests {
    t.Run(tt.name, func(t *testing.T) {
        t.Parallel()
        // 使用 tt ...
    })
}
```

> ⚠️ 前提是 `go.mod` 的 `go` 指令版本設為 `1.22` 以上，這個語意變更才會生效（Go 用模組宣告的語言版本做行為切換，不是編譯器版本）。

### range over func / Iterators（Go 1.23）

自訂容器可以實作 `func(yield func(V) bool)` 這種簽名，就能直接被 `range` 消費，不需要先轉成 slice。

```go
func Count(n int) func(yield func(int) bool) {
    return func(yield func(int) bool) {
        for i := 0; i < n; i++ {
            if !yield(i) {
                return // 消費端 break，提前停止
            }
        }
    }
}

for v := range Count(3) {
    fmt.Println(v) // 0 1 2
}
```

### `errors.Join`（Go 1.20）與 `errors.AsType`（Go 1.26）

`errors.Join` 可以把多個錯誤合併成一個錯誤樹，`errors.Is`/`errors.As` 仍能正常在樹中比對；Go 1.26 新增泛型版 `AsType`，省去手動宣告目標變數再取址的樣板寫法。

```go
err := errors.Join(errValidation, errTimeout)
if errors.Is(err, errTimeout) { ... }

// Go 1.26 起：func AsType[E error](err error) (E, bool)
if myErr, ok := errors.AsType[*MyError](err); ok {
    fmt.Println(myErr.Code)
}
```

### `log/slog` 結構化日誌（Go 1.21）

標準庫原生支援分級、結構化（key-value）日誌，不需要額外依賴第三方套件才能寫出可被日誌系統解析的輸出。

```go
logger := slog.New(slog.NewJSONHandler(os.Stdout, nil))
logger.Info("order created", "order_id", id, "amount", amount)
```

### `context` 強化（Go 1.21 / 1.24）

- Go 1.21：`context.WithoutCancel`（保留 value、拿掉取消關聯）、`context.WithDeadlineCause`/`WithTimeoutCause`（可附上取消原因）、`context.AfterFunc`（context 結束時執行回呼）。
- Go 1.24：`testing.T` 新增 `Context()`，測試中不再需要手動 `context.Background()`。

### `sync/atomic` 泛型型別（Go 1.19）

呼應 Part 1 的發現：標準庫已提供 `atomic.Bool`/`atomic.Int32`/`Int64`/`Uint32`/`Uint64`/`Pointer[T]`，API 風格與 `go.uber.org/atomic` 幾乎一致，多數場景可以直接用標準庫，減少一個外部依賴。

```go
var running atomic.Bool
running.Store(true)
if running.CompareAndSwap(true, false) { ... }
```

### `sync.WaitGroup.Go`（Go 1.25）

`func (wg *WaitGroup) Go(f func())`：自動處理 `Add(1)`/`Done()`，消除手動樣板；官方文件強調 **`f` 內部不得 panic**。

```go
var wg sync.WaitGroup
for _, job := range jobs {
    wg.Go(func() { process(job) })
}
wg.Wait()
```

### testing 套件現代化（Go 1.24 / 1.25）

- Go 1.24：`B.Loop()` 讓 benchmark 迴圈語意更精確（避免編譯器誤優化）、`T.Chdir()` 安全切換測試用工作目錄。
- Go 1.25：`testing/synctest` 從實驗性套件（`GOEXPERIMENT=synctest`）**正式畢業**，可用虛擬時鐘測試並發程式碼的 timing 邏輯；另新增 `T.Attr`/`B.Attr`/`F.Attr`（寫入測試日誌屬性）與 `T.Output`/`B.Output`/`F.Output`（取得測試輸出流的 `io.Writer`）。

### `new(expr)`：內建 `new` 支援運算式（Go 1.26）

過去 `new(T)` 只能接收**型別**，回傳該型別零值的指標；Go 1.26 起 `new` 也可以接收**運算式**，回傳該運算式結果副本的指標——對「可選欄位是指標」的場景（例如 JSON 欄位）特別方便，不需要先宣告臨時變數再取址。

```go
type Person struct {
    Name string `json:"name"`
    Age  *int   `json:"age,omitempty"`
}

// Go 1.26 之前：
age := 30
p := Person{Name: "Ada", Age: &age}

// Go 1.26 起：
p := Person{Name: "Ada", Age: new(30)}
```

### `net/http.ServeMux` 路由增強（Go 1.22）

標準庫路由器直接支援 HTTP 方法與路徑萬用字元，很多場景不再需要引入第三方 router。

```go
mux := http.NewServeMux()
mux.HandleFunc("GET /users/{id}", getUser)
mux.HandleFunc("POST /users", createUser)
```

---

## Part 4｜快速檢查清單

給未來寫程式/做 code review 時快速掃過用，混合 Uber Guide 既有規則與本文件新增內容：

- [ ] 公開套件的介面實作，是否用 `var _ Interface = (*T)(nil)` 做編譯期合理性驗證？
- [ ] 切片/map 在套件邊界（參數、回傳值、struct 欄位）是否需要複製，避免外部持有者意外修改內部狀態？
- [ ] 是否所有 error 都只在最外層處理一次（log 或回傳，不要兩者都做）？
- [ ] 新型別是否考慮過「零值就可用」，而不是預設要求呼叫 `NewXxx()`？
- [ ] `go.mod` 的 `go` 版本是否 ≥ 1.22？若是，迴圈裡的 `tt := tt` 類技巧是否已經多餘？
- [ ] 是否有能用 `slices`/`maps`/`cmp` 或內建 `min`/`max`/`clear` 取代的手寫迴圈？
- [ ] 泛型是否只用在真正需要型別參數化的容器/演算法，而不是為了用泛型而用？
- [ ] 並發程式碼是否用 channel／`context` 表達「通信」而非到處加鎖？`panic`/`recover` 是否只用於故障隔離邊界？
- [ ] 大量 `wg.Add`/`defer wg.Done()` 樣板是否可以用 `sync.WaitGroup.Go`（需 Go 1.25+）簡化？
- [ ] 日誌是否用 `log/slog` 輸出結構化欄位，而非拼接字串？
- [ ] Lint 工具鏈是否還在用已廢棄的 `golint`？應改用 `revive`。

---

## 參考來源

- [uber-go/guide](https://github.com/uber-go/guide)（英文原版）與本地 `README.md`（繁中翻譯，同步至 commit `42f94b6`）
- [Effective Go](https://go.dev/doc/effective_go)
- [Go 1.19](https://go.dev/doc/go1.19) / [1.20](https://go.dev/doc/go1.20) / [1.21](https://go.dev/doc/go1.21) / [1.22](https://go.dev/doc/go1.22) / [1.23](https://go.dev/doc/go1.23) / [1.24](https://go.dev/doc/go1.24) / [1.25](https://go.dev/doc/go1.25) / [1.26](https://go.dev/doc/go1.26) Release Notes
- [Go Release History](https://go.dev/doc/devel/release)
- [pkg.go.dev/errors](https://pkg.go.dev/errors)、[pkg.go.dev/sync](https://pkg.go.dev/sync)（確認 `AsType`、`WaitGroup.Go` 簽名）
