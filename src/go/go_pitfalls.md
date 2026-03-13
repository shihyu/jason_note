# Go 語言常見陷阱完整指南

> 涵蓋日常開發 + 面試高頻考點，每個陷阱附有錯誤示範、正確寫法與原理說明

---

## 目錄

1. [閉包陷阱（Closure Trap）](#1-閉包陷阱)
2. [goroutine 洩漏（Goroutine Leak）](#2-goroutine-洩漏)
3. [defer 執行順序與變數捕獲](#3-defer-執行順序與變數捕獲)
4. [slice 共享底層陣列](#4-slice-共享底層陣列)
5. [map 並發讀寫（Race Condition）](#5-map-並發讀寫)
6. [interface nil 陷阱](#6-interface-nil-陷阱)
7. [for range 變數複用](#7-for-range-變數複用)
8. [channel 死鎖（Deadlock）](#8-channel-死鎖)
9. [goroutine 與 WaitGroup 誤用](#9-goroutine-與-waitgroup-誤用)
10. [值接收者 vs 指標接收者](#10-值接收者-vs-指標接收者)
11. [string 與 []byte 轉換效能](#11-string-與-byte-轉換效能)
12. [init 函數陷阱](#12-init-函數陷阱)
13. [錯誤處理常見誤區](#13-錯誤處理常見誤區)
14. [記憶體逃逸（Escape Analysis）](#14-記憶體逃逸)
15. [nil map 寫入 panic](#15-nil-map-寫入-panic)
16. [select 多 case 隨機性](#16-select-多-case-隨機性)
17. [型別斷言陷阱](#17-型別斷言陷阱)
18. [time.After 洩漏](#18-timeafter-洩漏)
19. [Mutex 不可重入死鎖](#19-mutex-不可重入死鎖)
20. [rune vs byte（string Unicode 陷阱）](#20-rune-vs-byte)
21. [JSON 序列化陷阱](#21-json-序列化陷阱)
22. [context 誤用](#22-context-誤用)
23. [整數溢出與型別轉換](#23-整數溢出與型別轉換)
24. [面試高頻陷阱總覽](#24-面試高頻陷阱總覽)

---

## 1. 閉包陷阱

### ❌ 錯誤示範

```go
funcs := make([]func(), 5)
for i := 0; i < 5; i++ {
    funcs[i] = func() {
        fmt.Println(i) // 捕獲的是變數 i 的「參考」，不是值
    }
}
for _, f := range funcs {
    f() // 輸出: 5 5 5 5 5
}
```

### ✅ 正確寫法（兩種）

```go
// 方法一：傳參數進去
for i := 0; i < 5; i++ {
    i := i // 重新宣告新變數遮蔽外層
    funcs[i] = func() {
        fmt.Println(i) // 捕獲的是新的 i
    }
}

// 方法二：顯式傳入
for i := 0; i < 5; i++ {
    funcs[i] = func(n int) func() {
        return func() { fmt.Println(n) }
    }(i)
}
// 輸出: 0 1 2 3 4
```

### 原理圖

```
閉包捕獲機制

❌ 錯誤：共享同一個 i 變數
┌─────────────────────────────────────────┐
│  for loop 結束後 i = 5                  │
│  ┌──────────┐  ┌──────────┐             │
│  │ func[0]  │  │ func[1]  │ ...         │
│  │  ref→i   │  │  ref→i   │             │
│  └────┬─────┘  └────┬─────┘             │
│       └──────┬───────┘                  │
│          ┌───▼───┐                      │
│          │  i=5  │ ← 所有閉包共享此變數  │
│          └───────┘                      │
└─────────────────────────────────────────┘

✅ 正確：每個閉包有獨立的 i
┌─────────────────────────────────────────┐
│  ┌──────────┐  ┌──────────┐             │
│  │ func[0]  │  │ func[1]  │ ...         │
│  │  ref→i₀  │  │  ref→i₁  │             │
│  └────┬─────┘  └────┬─────┘             │
│   ┌───▼───┐     ┌───▼───┐               │
│   │  i=0  │     │  i=1  │               │
│   └───────┘     └───────┘               │
└─────────────────────────────────────────┘
```

---

## 2. goroutine 洩漏

### ❌ 錯誤示範

```go
func leak() {
    ch := make(chan int) // 無緩衝 channel
    go func() {
        val := <-ch // 永遠等不到資料，goroutine 卡死
        fmt.Println(val)
    }()
    // 函數結束，ch 沒人傳值，goroutine 永遠無法退出
}
```

### ✅ 正確寫法

```go
func noLeak() {
    ch := make(chan int, 1) // 緩衝 channel，或使用 context 控制
    ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
    defer cancel()

    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            fmt.Println("goroutine 正常退出")
            return
        }
    }()

    ch <- 42
}
```

### 原理圖

```
Goroutine 洩漏示意

正常流程：
Main ──────► goroutine ──► 收到資料 ──► 退出 ✓

洩漏流程：
Main ──► goroutine ──► 等待 channel ──► 等待... ──► 永遠不退出 ✗
 │                         │
結束                    堆積在記憶體
                     (每次呼叫 +1 goroutine)

使用 Context 修復：
Main ──► goroutine ──► select { ch | ctx.Done() }
                            │           │
                          收到資料     超時/取消
                          正常退出     正常退出 ✓
```

### 常見洩漏場景

```go
// 場景2：http handler 中忘記處理 channel
func handler(w http.ResponseWriter, r *http.Request) {
    result := make(chan string)
    go fetchData(result) // 若 fetchData panic，result 永遠沒人寫
    fmt.Fprint(w, <-result) // 卡死
}

// 修復：加 context
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()
    result := make(chan string, 1)
    go func() {
        select {
        case result <- fetchData():
        case <-ctx.Done():
        }
    }()
    select {
    case data := <-result:
        fmt.Fprint(w, data)
    case <-ctx.Done():
        http.Error(w, "timeout", 504)
    }
}
```

---

## 3. defer 執行順序與變數捕獲

### 陷阱 3-1：defer 是 LIFO（後進先出）

```go
func main() {
    defer fmt.Println("first")
    defer fmt.Println("second")
    defer fmt.Println("third")
    // 輸出: third → second → first
}
```

### 陷阱 3-2：defer 在函數返回時執行，但參數立即求值

```go
// ❌ 陷阱：以為能印出最終的 i
func trapDefer() {
    for i := 0; i < 3; i++ {
        defer fmt.Println(i) // 參數 i 立即求值（0,1,2）
    }
    // 輸出: 2 1 0（LIFO，但值是當時捕獲的）
}

// ❌ 陷阱：命名返回值被 defer 修改
func double(x int) (result int) {
    defer func() {
        result *= 2 // defer 可以修改命名返回值！
    }()
    result = x
    return result // 最終返回 x*2
}

func main() {
    fmt.Println(double(3)) // 輸出: 6，不是 3！
}
```

### defer 執行流程圖

```
defer 執行時機

func foo() int {
    defer A()     ← 第3個執行
    defer B()     ← 第2個執行
    defer C()     ← 第1個執行
    return val
}

執行順序：
return val  →  [defer stack 依 LIFO 執行]  →  實際返回
              C() → B() → A()

命名返回值陷阱：
┌──────────────────────────────┐
│  func f() (n int) {          │
│    defer func() { n++ }()    │
│    return 1  ← n=1           │
│  }           ↑               │
│   defer 修改 n → n=2         │
│   最終返回 2                 │
└──────────────────────────────┘
```

---

## 4. slice 共享底層陣列

### ❌ 陷阱：append 可能修改原始 slice

```go
original := []int{1, 2, 3, 4, 5}
sub := original[1:3] // [2, 3]，與 original 共享底層陣列

sub = append(sub, 100) // 修改的是原始陣列的第4個位置！
fmt.Println(original)  // [1 2 3 100 5] ← 被意外修改了！
```

### ✅ 正確寫法：使用 copy 或三索引切片

```go
// 方法一：完整 copy
sub := make([]int, 2)
copy(sub, original[1:3])
sub = append(sub, 100)
fmt.Println(original) // [1 2 3 4 5] ← 不受影響

// 方法二：三索引切片（限制 cap）
sub := original[1:3:3] // [low:high:max]，cap=max-low=2
// append 時因 cap 不足，會分配新底層陣列
sub = append(sub, 100)
fmt.Println(original) // [1 2 3 4 5] ← 不受影響
```

### 記憶體佈局圖

```
slice 底層結構

original := []int{1, 2, 3, 4, 5}
sub := original[1:3]

記憶體佈局：
底層陣列：  [1][2][3][4][5]
             ↑     ↑     ↑
original:  ptr  len=5  cap=5
sub:       ptr  len=2  cap=4  ← ptr 指向 [2] 的位置

sub = append(sub, 100)
因為 cap=4 > len=2，不會重新分配！
底層陣列：  [1][2][3][100][5]  ← [4] 被覆蓋！
                      ↑
              original[3] 被污染

三索引切片修復：
sub := original[1:3:3]  ← cap = 3-1 = 2
底層陣列：  [1][2][3][4][5]
sub: ptr=&[2], len=2, cap=2

sub = append(sub, 100)
cap 不足 → 分配新陣列 → 原始陣列安全 ✓
```

---

## 5. map 並發讀寫

### ❌ 危險：concurrent map read and write（會 panic）

```go
m := map[string]int{"a": 1}
var wg sync.WaitGroup

for i := 0; i < 100; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        m["key"] = n  // 並發寫 → fatal error: concurrent map writes
        _ = m["key"]  // 並發讀寫 → panic
    }(i)
}
wg.Wait()
```

### ✅ 正確寫法（三種方案）

```go
// 方案一：sync.Mutex
type SafeMap struct {
    mu sync.RWMutex
    m  map[string]int
}

func (s *SafeMap) Get(key string) int {
    s.mu.RLock()
    defer s.mu.RUnlock()
    return s.m[key]
}

func (s *SafeMap) Set(key string, val int) {
    s.mu.Lock()
    defer s.mu.Unlock()
    s.m[key] = val
}

// 方案二：sync.Map（適合讀多寫少）
var sm sync.Map
sm.Store("key", 42)
val, ok := sm.Load("key")
sm.LoadOrStore("key", 100)  // 原子操作

// 方案三：channel 序列化（適合複雜邏輯）
type MapOp struct {
    key string
    val int
    get chan int
}
```

---

## 6. interface nil 陷阱

### ❌ 最經典陷阱之一

```go
type MyError struct{ msg string }
func (e *MyError) Error() string { return e.msg }

func getError() error {
    var err *MyError = nil
    return err // ← 這裡有大陷阱！
}

func main() {
    err := getError()
    if err != nil {
        fmt.Println("有錯誤!") // 這行「會」執行！
    }
}
```

### 原理圖

```
interface 的內部結構

interface 由兩個欄位組成：
┌─────────┬─────────┐
│  type   │  value  │
└─────────┴─────────┘

nil interface：type=nil, value=nil → err == nil  ✓

var err *MyError = nil
return err  // 轉換為 interface 後：
┌────────────────┬──────────┐
│  type=*MyError │ value=nil│  ← type 不是 nil！
└────────────────┴──────────┘
err != nil  ✓  (因為 type 欄位有值)

正確判斷方式：
┌────────────────────────────────────────┐
│ interface == nil                       │
│ 要求：type == nil AND value == nil     │
│                                        │
│ 只要 type 不是 nil，就不等於 nil！     │
└────────────────────────────────────────┘
```

### ✅ 正確寫法

```go
func getError() error {
    var err *MyError = nil
    if err == nil {
        return nil  // 直接返回 nil interface，不是帶 type 的 nil
    }
    return err
}

// 或者使用 reflect 判斷
func isNil(i interface{}) bool {
    if i == nil {
        return true
    }
    v := reflect.ValueOf(i)
    return v.Kind() == reflect.Ptr && v.IsNil()
}
```

---

## 7. for range 變數複用

### ❌ 陷阱：Go 1.22 之前的行為

```go
// Go 1.21 及以前
people := []Person{{Name: "Alice"}, {Name: "Bob"}}
var ptrs []*Person
for _, p := range people {
    ptrs = append(ptrs, &p) // &p 每次都是同一個地址！
}
fmt.Println(ptrs[0].Name) // Bob（不是 Alice！）
fmt.Println(ptrs[1].Name) // Bob
```

### ✅ 正確寫法

```go
// 方法一：重新宣告變數（Go 1.21 及以前的修復）
for _, p := range people {
    p := p  // 建立新的局部變數
    ptrs = append(ptrs, &p)
}

// 方法二：使用索引
for i := range people {
    ptrs = append(ptrs, &people[i])
}

// Go 1.22+ 已修復此問題，每次迭代使用新變數
```

### 圖解

```
Go 1.21 for range 變數複用

for _, p := range people {
    ptrs = append(ptrs, &p)
}

迭代1: p = {Alice} → &p = 0xC000
迭代2: p = {Bob}   → &p = 0xC000  ← 同一個地址！p 被覆蓋

ptrs[0] = 0xC000 → {Bob}  ← 錯誤！
ptrs[1] = 0xC000 → {Bob}

修復後：
迭代1: p₁ = {Alice} → &p₁ = 0xC000
迭代2: p₂ = {Bob}   → &p₂ = 0xC010  ← 不同地址

ptrs[0] = 0xC000 → {Alice}  ✓
ptrs[1] = 0xC010 → {Bob}    ✓
```

---

## 8. channel 死鎖

### ❌ 常見死鎖情況

```go
// 情況1：無緩衝 channel，沒有 goroutine 接收
ch := make(chan int)
ch <- 1  // 永久阻塞 → deadlock

// 情況2：從空 channel 讀取
ch := make(chan int)
val := <-ch  // 永久阻塞 → deadlock

// 情況3：互相等待
ch1 := make(chan int)
ch2 := make(chan int)
go func() {
    <-ch1  // 等 ch1
    ch2 <- 1
}()
<-ch2  // 等 ch2，但 ch2 要等 ch1，ch1 沒人送 → deadlock
```

### ✅ 正確使用 channel

```go
// 使用 select + default 避免阻塞
select {
case ch <- val:
    // 成功送出
default:
    // channel 滿了，fallback 處理
}

// 使用 close 通知多個 goroutine
done := make(chan struct{})
for i := 0; i < 3; i++ {
    go func() {
        <-done  // 等待關閉
        fmt.Println("goroutine 退出")
    }()
}
close(done)  // 廣播給所有等待的 goroutine

// 正確的 pipeline 模式
func producer(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)  // 記得 close！
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}
```

### Channel 狀態表

```
Channel 操作狀態速查表

              nil channel    空 channel    非空 channel    已關閉 channel
─────────────────────────────────────────────────────────────────────────
發送 (<-)     永久阻塞        阻塞等接收     阻塞等接收      panic ❌
接收 (<-)     永久阻塞        阻塞等發送     返回值           返回零值+false
close()       panic ❌        正常關閉        正常關閉        panic ❌
```

---

## 9. goroutine 與 WaitGroup 誤用

### ❌ 常見錯誤

```go
// 錯誤1：Add 在 goroutine 內部呼叫
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    go func() {
        wg.Add(1)      // ❌ 可能在 Wait() 之後才執行
        defer wg.Done()
        doWork()
    }()
}
wg.Wait() // 可能提前返回！

// 錯誤2：Done 呼叫次數不對
wg.Add(1)
go func() {
    wg.Done()
    wg.Done() // ❌ panic: negative WaitGroup counter
}()

// 錯誤3：傳值而非傳指標
func worker(wg sync.WaitGroup) { // ❌ WaitGroup 被複製了！
    defer wg.Done()
}
```

### ✅ 正確用法

```go
var wg sync.WaitGroup
for i := 0; i < 5; i++ {
    wg.Add(1) // ✅ 在啟動 goroutine 前 Add
    go func(n int) {
        defer wg.Done() // ✅ 使用 defer 確保一定執行
        doWork(n)
    }(i)
}
wg.Wait()

// WaitGroup 只能傳指標
func worker(wg *sync.WaitGroup) { // ✅
    defer wg.Done()
}
```

---

## 10. 值接收者 vs 指標接收者

### 陷阱：interface 實作判定

```go
type Animal interface {
    Speak() string
}

type Dog struct{ Name string }

func (d Dog) Speak() string { return "Woof" }     // 值接收者
func (d *Dog) Fetch() string { return "Fetching" } // 指標接收者

var a Animal = Dog{"Rex"}   // ✅ 值接收者，Dog 和 *Dog 都實作 Animal
var a Animal = &Dog{"Rex"}  // ✅ 也可以

// 但是！指標接收者的方法集問題：
type Counter struct{ count int }
func (c *Counter) Inc() { c.count++ } // 指標接收者

var c Counter
c.Inc()  // ✅ Go 自動取址：(&c).Inc()

// ❌ 但在 interface 中行不通
type Incrementer interface{ Inc() }
var i Incrementer = Counter{}  // ❌ Counter does not implement Incrementer
var i Incrementer = &Counter{} // ✅
```

### 方法集規則圖

```
方法集（Method Set）規則

類型 T：
┌────────────────────────────────────┐
│ 可呼叫：值接收者的方法              │
└────────────────────────────────────┘

類型 *T：
┌────────────────────────────────────┐
│ 可呼叫：值接收者 + 指標接收者的方法  │
└────────────────────────────────────┘

interface 實作判定：
T  implements interface ← 只需 T 的值接收者方法
*T implements interface ← 值接收者 + 指標接收者方法

記憶口訣：
「指標可以呼叫一切，值只能呼叫值接收者」
```

---

## 11. string 與 []byte 轉換效能

### ❌ 頻繁轉換導致效能問題

```go
// 每次轉換都會分配新記憶體
for i := 0; i < 1000000; i++ {
    b := []byte("hello world")  // 分配新記憶體
    s := string(b)              // 再分配一次
    _ = s
}
```

### ✅ 優化技巧

```go
// 技巧1：strings.Builder（高效拼接）
var sb strings.Builder
for i := 0; i < 1000; i++ {
    sb.WriteString("hello")
}
result := sb.String()  // 只分配一次

// 技巧2：bytes.Buffer
var buf bytes.Buffer
buf.WriteString("hello")
buf.WriteByte(' ')
buf.WriteString("world")
result := buf.String()

// 技巧3：unsafe 零拷貝轉換（謹慎使用）
func bytesToString(b []byte) string {
    return *(*string)(unsafe.Pointer(&b))
}
// ⚠️ 注意：若 []byte 被修改，string 也會變動，違反 immutability

// 技巧4：預分配
ss := make([]string, 0, 1000)  // 預分配容量
```

---

## 12. init 函數陷阱

### 特性說明

```go
// 每個 package 可以有多個 init()
// 執行順序：依賴順序 → 同 package 內按檔案名 → 同檔案內由上到下

package main

var x = initX() // 包級變數先初始化

func initX() int {
    fmt.Println("1. 變數初始化")
    return 1
}

func init() {
    fmt.Println("2. init 執行")
}

func main() {
    fmt.Println("3. main 執行")
}
// 輸出順序：1 → 2 → 3
```

### ❌ init 中的常見陷阱

```go
// 陷阱1：init 中的錯誤無法返回，只能 panic
func init() {
    db, err := sql.Open("mysql", dsn)
    if err != nil {
        panic(err) // 只能 panic，無法優雅處理
    }
    _ = db
}

// 陷阱2：循環依賴 init
// packageA init → 用到 packageB → packageB init → 用到 packageA → 循環！

// 最佳實踐：避免在 init 中做複雜初始化，改用顯式 Initialize() 函數
func Initialize(cfg Config) error {
    // 可以返回錯誤
    return setup(cfg)
}
```

---

## 13. 錯誤處理常見誤區

### ❌ 常見錯誤

```go
// 錯誤1：忽略錯誤
result, _ := doSomething() // 危險！

// 錯誤2：錯誤遮蔽（shadowing）
err := step1()
if err != nil {
    return err
}
result, err := step2() // 重用 err，但上面的 err 已消失
if err != nil {
    return err  // 但如果 step2 panic，上面的 err 資訊丟失了
}

// 錯誤3：fmt.Errorf 丟失類型資訊
err := fmt.Errorf("database error: %v", originalErr) // 無法使用 errors.As
```

### ✅ 正確錯誤處理

```go
// 使用 %w 包裹錯誤（Go 1.13+）
err := fmt.Errorf("processing user %d: %w", userID, originalErr)

// errors.Is：判斷錯誤值
if errors.Is(err, sql.ErrNoRows) {
    return nil, ErrNotFound
}

// errors.As：轉換錯誤類型
var netErr *net.OpError
if errors.As(err, &netErr) {
    fmt.Println("網路錯誤:", netErr.Op)
}

// 自訂錯誤類型
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("validation error: %s - %s", e.Field, e.Message)
}
```

### 錯誤鏈示意圖

```
errors.Is / errors.As 的錯誤鏈查找

原始錯誤: ErrPermission
    ↓ fmt.Errorf("open file: %w", ErrPermission)
包裹錯誤: "open file: permission denied"
    ↓ fmt.Errorf("startup: %w", wrappedErr)
外層錯誤: "startup: open file: permission denied"

errors.Is(outerErr, ErrPermission) → true ✓
（自動解包整個錯誤鏈搜尋）

errors.As(outerErr, &targetType) → 搜尋鏈中符合類型的錯誤
```

---

## 14. 記憶體逃逸

### 何時發生逃逸

```go
// 逃逸到 heap（需要 GC 管理）

// 情況1：返回局部變數指標
func newUser() *User {
    u := User{Name: "Alice"} // u 逃逸到 heap
    return &u
}

// 情況2：interface 包裝
func printAny(v interface{}) { ... }
x := 42
printAny(x) // x 逃逸（interface 需要 heap 分配）

// 情況3：閉包捕獲
func makeCounter() func() int {
    count := 0  // count 逃逸到 heap（被閉包捕獲）
    return func() int {
        count++
        return count
    }
}

// 查看逃逸分析
// go build -gcflags="-m" ./...
```

### 記憶體分配圖

```
Stack vs Heap 分配

Stack（快，函數結束自動回收）：
┌─────────────────────┐
│     main()          │
│   ┌─────────────┐   │
│   │  局部變數    │   │
│   └─────────────┘   │
│     foo()           │
│   ┌─────────────┐   │
│   │  局部變數    │   │
│   └─────────────┘   │
└─────────────────────┘

Heap（慢，需要 GC 管理）：
┌──────────────────────────────┐
│  逃逸的物件                   │
│  ┌────────┐  ┌────────┐      │
│  │ User{} │  │ []byte │ ...  │
│  └────────┘  └────────┘      │
│         GC 負責清理           │
└──────────────────────────────┘

減少逃逸的技巧：
- 使用值類型而非指標（小物件）
- sync.Pool 重用物件
- 預分配 slice/map
- 避免 interface 包裝頻繁呼叫的函數
```

---

## 15. nil map 寫入 panic

### ❌ 錯誤示範

```go
// 宣告但未初始化的 map 是 nil
var m map[string]int

// 讀取 nil map：安全，返回零值
fmt.Println(m["key"]) // 0，不會 panic

// 寫入 nil map：panic！
m["key"] = 1 // panic: assignment to entry in nil map

// 常見陷阱：struct 中的 map 欄位
type Cache struct {
    data map[string]int
}

c := Cache{}           // data 是 nil
c.data["key"] = 1      // panic！
```

### ✅ 正確寫法

```go
// 方法一：make 初始化
m := make(map[string]int)
m["key"] = 1 // 安全

// 方法二：字面量初始化
m := map[string]int{}
m["key"] = 1 // 安全

// 方法三：struct 中使用建構函數確保初始化
type Cache struct {
    data map[string]int
}

func NewCache() *Cache {
    return &Cache{
        data: make(map[string]int),
    }
}

// 方法四：延遲初始化（lazy init）
func (c *Cache) Set(key string, val int) {
    if c.data == nil {
        c.data = make(map[string]int)
    }
    c.data[key] = val
}
```

### nil map vs 空 map 圖解

```
nil map：
┌──────────────────────────────────┐
│ var m map[string]int             │
│                                  │
│  m ──► nil（沒有底層資料結構）    │
│                                  │
│  讀：m["key"] → 0   ✓ 安全       │
│  寫：m["key"] = 1  ✗ panic       │
│  len：len(m) → 0   ✓ 安全       │
└──────────────────────────────────┘

空 map（已初始化）：
┌──────────────────────────────────┐
│ m := make(map[string]int)        │
│                                  │
│  m ──► hash table（空的）         │
│                                  │
│  讀：m["key"] → 0   ✓ 安全       │
│  寫：m["key"] = 1  ✓ 安全        │
│  len：len(m) → 0   ✓ 安全       │
└──────────────────────────────────┘
```

---

## 16. select 多 case 隨機性

### ❌ 常見誤解：以為 select 按順序執行

```go
ch1 := make(chan string, 1)
ch2 := make(chan string, 1)
ch1 <- "one"
ch2 <- "two"

// 以為一定先收到 ch1
for i := 0; i < 5; i++ {
    select {
    case msg := <-ch1:
        fmt.Println("ch1:", msg)
    case msg := <-ch2:
        fmt.Println("ch2:", msg)
    }
}
// 實際輸出不確定！Go runtime 隨機選擇就緒的 case
```

### ✅ 正確理解與運用

```go
// select 的規則：
// 1. 多個 case 都就緒 → 隨機選一個（Go spec 保證）
// 2. 沒有 case 就緒 → 阻塞等待
// 3. 有 default → 立即執行 default（非阻塞）

// 利用隨機性：公平競爭
select {
case job := <-highPriority:
    process(job)
case job := <-lowPriority:
    process(job)
}

// 需要優先順序時，用巢狀 select
select {
case job := <-highPriority:
    process(job)
default:
    select {
    case job := <-lowPriority:
        process(job)
    default:
        // 都沒有就緒
    }
}

// 超時控制
select {
case result := <-ch:
    fmt.Println(result)
case <-time.After(3 * time.Second):
    fmt.Println("timeout")
}

// 非阻塞嘗試讀取
select {
case val := <-ch:
    fmt.Println("got:", val)
default:
    fmt.Println("channel empty, skip")
}
```

### select 執行流程圖

```
select 決策邏輯

              ┌─────────────┐
              │  select {}  │
              └──────┬──────┘
                     │
              ┌──────▼──────────────────┐
              │ 掃描所有 case            │
              │ 哪些 channel 已就緒？    │
              └──────┬──────────────────┘
                     │
         ┌───────────┼───────────┐
         │           │           │
    沒有就緒     一個就緒     多個就緒
         │           │           │
         ▼           ▼           ▼
    有default?   執行它     偽隨機選一個
    ┌──┬──┐                  執行它
    有  沒有
    ▼    ▼
  執行  阻塞等待
default  直到有
         case就緒
```

---

## 17. 型別斷言陷阱

### ❌ 單返回值形式：失敗直接 panic

```go
var i interface{} = "hello"

// 斷言成功
s := i.(string)    // ✅ s = "hello"

// 斷言失敗 → panic!
n := i.(int)       // ❌ panic: interface conversion:
                   //    interface {} is string, not int

// 常見場景：收到 interface{} 參數直接斷言
func process(v interface{}) {
    s := v.(string) // 若 v 不是 string，直接 panic
    fmt.Println(s)
}
```

### ✅ 使用 comma-ok 慣用法

```go
var i interface{} = "hello"

// comma-ok 形式：安全
s, ok := i.(string)
if !ok {
    fmt.Println("不是 string")
    return
}
fmt.Println(s) // hello

// switch type 斷言：處理多種型別
func describe(i interface{}) {
    switch v := i.(type) {
    case int:
        fmt.Printf("int: %d\n", v)
    case string:
        fmt.Printf("string: %q\n", v)
    case []int:
        fmt.Printf("[]int 長度: %d\n", len(v))
    case nil:
        fmt.Println("nil")
    default:
        fmt.Printf("未知型別: %T\n", v)
    }
}

// ❌ 另一個陷阱：斷言 interface 到 interface
type Reader interface{ Read() }
type Writer interface{ Write() }

var r Reader = someReader
w, ok := r.(Writer) // 斷言是否同時實作 Writer
_ = w
```

### 型別斷言 vs 型別轉換

```
型別斷言（Type Assertion）：
┌─────────────────────────────────────────┐
│  interface → 具體型別 或 另一個 interface │
│                                         │
│  v := i.(T)       ← 失敗 panic          │
│  v, ok := i.(T)   ← 失敗 ok=false       │
│                                         │
│  適用：interface{} 或任何 interface 變數 │
└─────────────────────────────────────────┘

型別轉換（Type Conversion）：
┌─────────────────────────────────────────┐
│  具體型別 ←→ 具體型別（編譯期決定）      │
│                                         │
│  n := int(float64Val)  ← 數值轉換       │
│  s := string([]byte{}) ← []byte→string  │
│  b := []byte(str)      ← string→[]byte  │
│                                         │
│  不兼容型別 → 編譯錯誤（而非執行時錯誤） │
└─────────────────────────────────────────┘
```

---

## 18. time.After 洩漏

### ❌ 在迴圈中使用 time.After 造成記憶體洩漏

```go
// 每次呼叫 time.After 都會建立一個新的 Timer
// Timer 在觸發前不會被 GC 回收！

func processMessages(ch <-chan string) {
    for {
        select {
        case msg := <-ch:
            fmt.Println(msg)
        case <-time.After(5 * time.Second): // ❌ 每次迴圈都建立新 Timer
            fmt.Println("timeout")
            return
        }
    }
    // 若訊息持續來，time.After 不斷建立但永不觸發
    // 導致大量 Timer 堆積在記憶體
}

// 高頻場景：每秒 1000 個請求，每個請求都 select time.After(30s)
// → 同時存在 30,000 個未觸發的 Timer！
```

### ✅ 正確寫法：在迴圈外建立 Timer

```go
// 方法一：time.NewTimer，手動重置
func processMessages(ch <-chan string) {
    timer := time.NewTimer(5 * time.Second)
    defer timer.Stop() // 確保退出時清理

    for {
        select {
        case msg := <-ch:
            fmt.Println(msg)
            // 重置 timer
            if !timer.Stop() {
                select {
                case <-timer.C:
                default:
                }
            }
            timer.Reset(5 * time.Second)
        case <-timer.C:
            fmt.Println("timeout")
            return
        }
    }
}

// 方法二：使用 context 控制超時（推薦）
func processMessages(ctx context.Context, ch <-chan string) {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    for {
        select {
        case msg := <-ch:
            fmt.Println(msg)
        case <-ctx.Done():
            fmt.Println("timeout or cancelled")
            return
        }
    }
}

// time.After 安全使用場景：只呼叫一次
func waitOnce(ch <-chan int) {
    select {
    case v := <-ch:
        fmt.Println(v)
    case <-time.After(3 * time.Second): // ✅ 只呼叫一次，沒有洩漏問題
        fmt.Println("timeout")
    }
}
```

### 記憶體洩漏示意圖

```
time.After 在迴圈中的問題

for {
    select {
    case msg := <-ch:  ←── 每秒收到訊息
    case <-time.After(5s):
    }
}

時間軸（每秒收到一條訊息）：
t=0s: 建立 Timer₀（5s後觸發）→ ch 收到訊息，Timer₀ 不會被 Stop
t=1s: 建立 Timer₁（5s後觸發）→ ch 收到訊息，Timer₁ 不會被 Stop
t=2s: 建立 Timer₂（5s後觸發）→ ...
...

t=5s: Timer₀ 到期，觸發，channel 排空 → GC 才能回收
t=6s: Timer₁ 到期，觸發... → 記憶體「延遲釋放」

積壓量 = rate × delay = 1/s × 5s = 5 個 Timer 常駐記憶體
（高頻情況更嚴重）

使用 time.NewTimer 的方案：
┌──────────────────────────────┐
│  只有 1 個 Timer 存在         │
│  收到訊息後 Reset，不建新的   │
│  記憶體使用恆定               │
└──────────────────────────────┘
```

---

## 19. Mutex 不可重入死鎖

### ❌ Go 的 Mutex 不支援重入（不像 Java 的 ReentrantLock）

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *SafeCounter) IncTwice() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.Inc() // ❌ 死鎖！Inc() 試圖再次 Lock 已鎖定的 Mutex
}

// 另一個常見場景：遞迴函數
func (c *SafeCounter) recursiveAdd(n int) {
    c.mu.Lock()
    defer c.mu.Unlock()
    if n <= 0 {
        return
    }
    c.count++
    c.recursiveAdd(n - 1) // ❌ 死鎖！第二次呼叫試圖 Lock
}
```

### ✅ 正確寫法：拆分加鎖和業務邏輯

```go
type SafeCounter struct {
    mu    sync.Mutex
    count int
}

// 不加鎖的內部方法（需呼叫者保證已持有鎖）
func (c *SafeCounter) inc() {
    c.count++ // 假設呼叫者已持有鎖
}

// 加鎖的公開方法
func (c *SafeCounter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.inc() // ✅ 呼叫不加鎖版本
}

func (c *SafeCounter) IncTwice() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.inc() // ✅ 直接呼叫內部方法
    c.inc()
}

// 遞迴場景：在鎖外執行邏輯，只在需要修改時加鎖
func (c *SafeCounter) Add(n int) {
    c.mu.Lock()
    c.count += n // 一次性修改，不遞迴持鎖
    c.mu.Unlock()
}
```

### Mutex 死鎖示意圖

```
重入死鎖（Reentrant Deadlock）

goroutine G1:
  IncTwice()
    └── Lock()    ← 成功獲取鎖，state=locked
    └── Inc()
          └── Lock()  ← 等待... 但鎖被自己持有！
                         永遠等不到 → 死鎖

Go Mutex 狀態：
┌─────────────────────────────────────┐
│  Locked by G1                       │
│                                     │
│  G1 再次嘗試 Lock → 進入等待隊列    │
│  G1 在等待隊列中 → 無法解鎖         │
│  G1 無法解鎖 → 永遠等待 → 死鎖 ❌   │
└─────────────────────────────────────┘

解決原則：
┌─────────────────────────────────────┐
│  持有鎖期間，不要呼叫同一個鎖的 Lock │
│  拆分：加鎖方法 vs 不加鎖方法        │
│  命名慣例：公開方法加鎖，私有方法不加 │
└─────────────────────────────────────┘
```

---

## 20. rune vs byte

### ❌ 陷阱：把 string 當 byte 陣列操作中文

```go
s := "Hello, 世界"

// ❌ 用 len 取得的是 byte 數，不是字元數
fmt.Println(len(s)) // 13（"世界" 各佔 3 bytes，UTF-8）

// ❌ 用索引取得的是 byte，不是字元
fmt.Println(s[7]) // 228（'世' 的第一個 byte）

// ❌ 截斷中文字串可能破壞 UTF-8 編碼
broken := s[:8] // 切在 '世' 字的中間 → 亂碼

// ❌ 用 byte 迭代
for i := 0; i < len(s); i++ {
    fmt.Printf("%c", s[i]) // 亂碼！byte by byte
}
```

### ✅ 正確操作多位元組字元

```go
s := "Hello, 世界"

// ✅ 轉成 []rune 再操作
runes := []rune(s)
fmt.Println(len(runes)) // 9（9個字元）
fmt.Println(string(runes[7])) // "世" ✓

// ✅ 安全截斷
safe := string(runes[:7]) // "Hello, "

// ✅ for range 自動處理 rune
for i, r := range s {
    fmt.Printf("index=%d, rune=%c, bytes=%d\n",
        i, r, utf8.RuneLen(r))
}
// index=0, rune=H, bytes=1
// index=7, rune=世, bytes=3
// index=10, rune=界, bytes=3

// ✅ 計算字元數
fmt.Println(utf8.RuneCountInString(s)) // 9

// ✅ strings 套件的函數都是 rune 感知的
fmt.Println(strings.Count(s, "界")) // 1
```

### byte vs rune 圖解

```
"Hello, 世界" 的記憶體佈局

byte 視角（len=13）：
Index:  0   1   2   3   4   5   6   7   8   9  10  11  12
Value: 'H' 'e' 'l' 'l' 'o' ',' ' ' 228 184 150 231 149 140
                                    └────世(3B)────┘└────界(3B)────┘

rune 視角（[]rune，len=9）：
Index:  0    1    2    3    4    5    6      7      8
Value: 'H'  'e'  'l'  'l'  'o'  ','  ' '  '世'   '界'

型別說明：
┌──────────────────────────────────┐
│  byte  = uint8   （1 byte）       │
│  rune  = int32   （4 bytes）      │
│                                  │
│  string → byte 序列（UTF-8 編碼） │
│  []rune → Unicode code point 序列 │
└──────────────────────────────────┘

常用工具：
  utf8.RuneCountInString(s)  → 字元數
  utf8.RuneLen(r)            → rune 的 byte 數
  []rune(s)                  → 轉 rune slice
  string([]rune{...})        → 轉回 string
```

---

## 21. JSON 序列化陷阱

### ❌ 常見陷阱

```go
// 陷阱1：未匯出欄位（小寫開頭）不會被序列化
type User struct {
    name  string // ❌ 小寫，json 忽略
    Age   int
    Email string
}

u := User{name: "Alice", Age: 30, Email: "a@b.com"}
data, _ := json.Marshal(u)
fmt.Println(string(data)) // {"Age":30,"Email":"a@b.com"}，name 消失！

// 陷阱2：interface{} 數字預設反序列化為 float64
var result map[string]interface{}
json.Unmarshal([]byte(`{"id": 123456789}`), &result)
id := result["id"].(float64) // 必須斷言為 float64，不是 int！
fmt.Printf("%T: %v\n", result["id"], result["id"]) // float64: 1.23456789e+08

// 陷阱3：零值欄位也會輸出
type Config struct {
    Host    string
    Port    int
    Timeout int
}
c := Config{Host: "localhost"}
data, _ = json.Marshal(c)
fmt.Println(string(data)) // {"Host":"localhost","Port":0,"Timeout":0}

// 陷阱4：time.Time 序列化格式
type Event struct {
    CreatedAt time.Time
}
// 預設輸出 RFC 3339 格式，可能與前端期望格式不同
```

### ✅ 正確寫法

```go
// 使用 struct tag 控制序列化行為
type User struct {
    Name    string `json:"name"`                // 改小寫 key
    Age     int    `json:"age"`
    Email   string `json:"email,omitempty"`     // 零值時省略
    Password string `json:"-"`                  // 永遠不序列化
    Score   float64 `json:"score,string"`       // 數字以 string 輸出
}

// 解決 interface{} 數字問題：使用 json.Number
var result map[string]interface{}
dec := json.NewDecoder(strings.NewReader(`{"id": 123456789}`))
dec.UseNumber() // 數字保持為 json.Number 型別
dec.Decode(&result)
id, _ := result["id"].(json.Number).Int64() // ✅ 精確的整數

// 或者用明確的 struct 接收
type Response struct {
    ID int64 `json:"id"`
}
var resp Response
json.Unmarshal([]byte(`{"id": 123456789}`), &resp)
fmt.Println(resp.ID) // 123456789 ✓

// 自訂 time 格式
type Event struct {
    CreatedAt time.Time
}
func (e Event) MarshalJSON() ([]byte, error) {
    return json.Marshal(struct {
        CreatedAt string `json:"created_at"`
    }{
        CreatedAt: e.CreatedAt.Format("2006-01-02 15:04:05"),
    })
}
```

### JSON tag 速查

```
struct tag 語法：`json:"key,options"`

key 選項：
  json:"name"      → 指定 JSON key 名稱
  json:"-"         → 永遠不序列化此欄位
  json:""          → 使用欄位名稱（同沒有 tag）

options 選項：
  omitempty        → 零值時省略（"", 0, false, nil, 空slice/map）
  string           → 強制以 JSON string 格式輸出數字/bool
  omitempty,string → 組合使用

範例：
┌──────────────────────────────────────────────────────┐
│  Name     string  `json:"name"`         → "name":""  │
│  Name     string  `json:"name,omitempty"` → 省略      │
│  Score    int     `json:"score,string"` → "score":"0"│
│  Password string  `json:"-"`           → 不輸出       │
└──────────────────────────────────────────────────────┘
```

---

## 22. context 誤用

### ❌ 常見誤用

```go
// 誤用1：將 context 存入 struct（官方明確反對）
type Server struct {
    ctx context.Context // ❌ context 應該在函數間傳遞，不應存在 struct
}

// 誤用2：傳入 nil context
func doWork(ctx context.Context) {}
doWork(nil) // ❌ 若內部呼叫 ctx.Done() 等方法，會 panic

// 誤用3：忽略 cancel 函數造成洩漏
ctx, _ := context.WithCancel(context.Background()) // ❌ cancel 被丟棄
// ctx 永遠不會被取消，關聯的 goroutine 可能永遠運行

// 誤用4：把 context 放在第二個參數
func process(data string, ctx context.Context) {} // ❌ 違反慣例

// 誤用5：用 context.Value 傳遞業務參數
ctx = context.WithValue(ctx, "userID", 123)    // ❌ 不推薦傳業務數據
ctx = context.WithValue(ctx, "page", 1)        // 應該用函數參數
```

### ✅ 正確用法

```go
// ✅ context 永遠是第一個參數
func doWork(ctx context.Context, data string) error {
    select {
    case <-ctx.Done():
        return ctx.Err() // context.Canceled 或 DeadlineExceeded
    default:
    }
    // ... 執行工作
    return nil
}

// ✅ 永遠 defer cancel()
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
defer cancel() // ✅ 即使提前完成也要 cancel，釋放資源

ctx, cancel = context.WithCancel(context.Background())
defer cancel()

// ✅ 傳入 context.TODO() 代替 nil（表示「待補充」）
func legacyFunc() {
    doWork(context.TODO(), "data") // 明確表示還未確定用哪個 context
}

// ✅ context.Value 只用於請求範圍的元數據（如 trace ID、auth token）
type contextKey string
const traceIDKey contextKey = "traceID"

func withTraceID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, traceIDKey, id)
}

func getTraceID(ctx context.Context) string {
    v, _ := ctx.Value(traceIDKey).(string)
    return v
}
```

### context 傳播圖

```
context 層級與取消傳播

context.Background()
    │
    ├── WithCancel(...)  ← root ctx
    │       │  cancel() 被呼叫或父 ctx 取消
    │       ▼
    │   WithTimeout(5s)  ← 子 ctx
    │       │  5s 超時或父取消
    │       ▼
    │   WithValue(key, val)  ← 孫 ctx
    │
    ▼
取消傳播：父 ctx 取消 → 所有子孫 ctx 自動取消 ✓
取消不上傳：子 ctx 取消 → 父 ctx 不受影響 ✓

context.Done() 使用模式：
for {
    select {
    case work := <-workCh:
        doWork(work)
    case <-ctx.Done():
        return ctx.Err()  ← ctx.Canceled 或 DeadlineExceeded
    }
}
```

---

## 23. 整數溢出與型別轉換

### ❌ 整數溢出不會 panic，靜默截斷

```go
// 整數溢出：Go 不會 panic，直接截斷（環繞）
var x int8 = 127
x++
fmt.Println(x) // -128（溢出！）

var u uint8 = 0
u--
fmt.Println(u) // 255（下溢！）

// 危險場景：長度計算溢出
func makeBuffer(size int) []byte {
    return make([]byte, size*2) // 若 size > MaxInt/2，size*2 溢出變負數
    // make 收到負數長度 → panic
}

// 型別轉換截斷
big := int64(300)
small := int8(big)       // 300 超過 int8 範圍（-128~127）
fmt.Println(small)       // 44（300 % 256 = 44，低 8 bits）

// float → int 截斷（不是四捨五入）
f := 3.9
n := int(f)
fmt.Println(n) // 3（直接截斷小數，不是 4！）
```

### ✅ 安全處理

```go
// 方法1：用 math 套件的常數做邊界檢查
import "math"

func safeAdd(a, b int32) (int32, error) {
    if b > 0 && a > math.MaxInt32-b {
        return 0, errors.New("integer overflow")
    }
    if b < 0 && a < math.MinInt32-b {
        return 0, errors.New("integer underflow")
    }
    return a + b, nil
}

// 方法2：轉換前檢查範圍
func toInt8(n int64) (int8, error) {
    if n < math.MinInt8 || n > math.MaxInt8 {
        return 0, fmt.Errorf("value %d out of int8 range", n)
    }
    return int8(n), nil
}

// 方法3：Go 1.21+ math/bits 檢測溢出
import "math/bits"

func safeMultiply(a, b uint64) (uint64, bool) {
    hi, lo := bits.Mul64(a, b)
    return lo, hi == 0 // hi != 0 表示溢出
}

// float → int 的正確四捨五入
f := 3.9
n := int(math.Round(f)) // 4 ✓
```

### 型別大小與範圍速查

```
Go 整數型別範圍

型別      大小    最小值                最大值
─────────────────────────────────────────────────
int8      1B      -128                  127
int16     2B      -32,768               32,767
int32     4B      -2,147,483,648        2,147,483,647
int64     8B      -9.2×10¹⁸             9.2×10¹⁸
uint8     1B      0                     255
uint16    2B      0                     65,535
uint32    4B      0                     4,294,967,295
uint64    8B      0                     1.8×10¹⁹
int       4B/8B   platform dependent（64位系統=int64範圍）

常見溢出陷阱：
┌───────────────────────────────────────────────┐
│ int8(127) + 1  → -128  （環繞）               │
│ uint8(0) - 1   → 255   （下溢）               │
│ int(300) → int8 → 44   （截斷）               │
│ float64(3.9) → int → 3  （截小數，非四捨五入）│
└───────────────────────────────────────────────┘
```

---

## 24. 面試高頻陷阱總覽

### 24-1 面試必考：輸出什麼？

```go
// 題目1：defer + 命名返回值
func f1() (result int) {
    defer func() { result++ }()
    return 0
}
// 答案：1（defer 修改了命名返回值）

// 題目2：goroutine 閉包
func main() {
    for i := 0; i < 3; i++ {
        go func() {
            fmt.Print(i) // 答案：不確定，可能 333 或 223 等
        }()
    }
    time.Sleep(time.Second)
}

// 題目3：slice append
a := []int{1, 2, 3}
b := a[:2]
b = append(b, 100)
fmt.Println(a) // 答案：[1 2 100]（b 修改了 a 的底層陣列）

// 題目4：nil interface
var p *int = nil
var i interface{} = p
fmt.Println(i == nil) // 答案：false（interface 有 type 資訊）

// 題目5：map 的 zero value
m := map[string]int{}
fmt.Println(m["不存在的key"]) // 答案：0（int 的零值）
v, ok := m["不存在的key"]
fmt.Println(v, ok) // 答案：0 false
```

### 24-2 面試常問概念

```
GMP 調度模型

G = Goroutine（協程）
M = Machine（OS 執行緒）
P = Processor（處理器，邏輯 CPU）

┌─────────────────────────────────────────────┐
│                  Go Runtime                  │
│                                             │
│  P1          P2          P3                 │
│  ┌──────┐   ┌──────┐   ┌──────┐            │
│  │LRQ   │   │LRQ   │   │LRQ   │            │
│  │G G G │   │G G G │   │G G G │            │
│  └──┬───┘   └──┬───┘   └──┬───┘            │
│     │M1        │M2        │M3               │
│                                             │
│  全局隊列(GRQ): G G G G G G                 │
│                                             │
│  Work Stealing: P 沒工作時從其他 P 偷 G     │
└─────────────────────────────────────────────┘

關鍵點：
- GOMAXPROCS 控制 P 的數量
- M 可以比 P 多（syscall 阻塞時建新 M）
- G 遠比 OS 執行緒輕量（初始棧 2-8KB，可動態增長）
```

### 24-3 sync 包常見陷阱

```go
// Mutex 陷阱：複製 Mutex
type MyStruct struct {
    mu sync.Mutex
    data int
}
s1 := MyStruct{}
s2 := s1        // ❌ 複製了 Mutex（狀態也被複製）
// 應該用指標傳遞：func process(s *MyStruct)

// Once 陷阱：panic 後 Once 不會重試
var once sync.Once
once.Do(func() {
    panic("oops") // Once 標記為已完成，之後不會再執行
})
once.Do(func() {
    // 這個永遠不會執行
})

// RWMutex 注意：讀鎖可以同時多個，寫鎖排他
var rw sync.RWMutex
rw.RLock()   // 多個 goroutine 可同時 RLock
rw.RUnlock()
rw.Lock()    // 排他鎖，必須等所有 RLock 釋放
rw.Unlock()
```

### 24-4 常見面試問題快速回答

| 問題 | 關鍵答案 |
|------|---------|
| goroutine 和 thread 的區別 | G 更輕量（2KB初始棧 vs 1MB），由 runtime 調度，可有百萬個 |
| channel 是否執行緒安全 | 是，channel 本身是執行緒安全的 |
| map 是否執行緒安全 | 否，需要加鎖或用 sync.Map |
| Go 的 GC 是什麼算法 | 三色標記清除 + 寫屏障，並發 GC |
| interface 是否可以比較 | 可以，但若 dynamic type 不可比較（如 slice）會 panic |
| 空 struct{} 的用途 | 不占記憶體，用於 set 的 value、channel 信號 |
| make vs new | make 初始化 slice/map/channel；new 只分配歸零記憶體 |
| panic recover 的作用範圍 | 只在同一個 goroutine 有效 |

### 24-5 效能優化常見考點

```go
// 1. 字串拼接：❌ += 是 O(n²)，✅ strings.Builder 是 O(n)
var b strings.Builder
for _, s := range strs {
    b.WriteString(s)
}

// 2. 預分配
// ❌ 每次 append 可能重新分配
s := []int{}
// ✅ 預知長度就預分配
s := make([]int, 0, len(input))

// 3. sync.Pool 減少 GC 壓力
var pool = sync.Pool{
    New: func() interface{} {
        return &bytes.Buffer{}
    },
}
buf := pool.Get().(*bytes.Buffer)
buf.Reset()
defer pool.Put(buf)
// 處理 buf...

// 4. 避免 interface{} 的 box/unbox 開銷
// 使用泛型（Go 1.18+）代替 interface{}
func Min[T constraints.Ordered](a, b T) T {
    if a < b {
        return a
    }
    return b
}
```

---

## 快速參考：陷阱清單

| # | 陷阱 | 嚴重程度 | 關鍵字 |
|---|------|---------|--------|
| 1 | 閉包捕獲變數引用 | ⚠️ 高 | `i := i` 重宣告 |
| 2 | goroutine 洩漏 | 🔴 極高 | context, close channel |
| 3 | defer LIFO + 命名返回值 | ⚠️ 中 | 命名返回值可被修改 |
| 4 | slice 共享底層陣列 | 🔴 高 | 三索引或 copy |
| 5 | map 並發讀寫 | 🔴 極高 | sync.Mutex 或 sync.Map |
| 6 | interface nil 判斷 | 🔴 高 | type + value 都要是 nil |
| 7 | for range 變數複用 | ⚠️ 高 | Go 1.22 已修復 |
| 8 | channel 死鎖 | 🔴 極高 | select, buffered channel |
| 9 | WaitGroup.Add 位置 | ⚠️ 中 | 必須在 goroutine 外 Add |
| 10 | 方法集與 interface | ⚠️ 中 | 指標接收者需傳 *T |
| 11 | string/[]byte 頻繁轉換 | ℹ️ 低 | strings.Builder |
| 12 | init 無法返回錯誤 | ℹ️ 低 | 改用顯式 Initialize() |
| 13 | 錯誤遮蔽 | ⚠️ 中 | errors.Is / errors.As / %w |
| 14 | 意外記憶體逃逸 | ℹ️ 低 | `-gcflags="-m"` 分析 |
| 15 | nil map 寫入 panic | 🔴 極高 | make 初始化，不要只 var |
| 16 | select 多 case 隨機性 | ⚠️ 中 | 用巢狀 select 實作優先順序 |
| 17 | 型別斷言不用 ok 形式 | 🔴 高 | `v, ok := i.(T)` |
| 18 | time.After 迴圈洩漏 | 🔴 高 | time.NewTimer + Reset |
| 19 | Mutex 重入死鎖 | 🔴 極高 | 拆分加鎖/不加鎖方法 |
| 20 | string 索引是 byte 非 rune | ⚠️ 高 | []rune 轉換、for range |
| 21 | JSON 未匯出欄位/float64 | ⚠️ 中 | struct tag、json.Number |
| 22 | context 誤用 | ⚠️ 中 | 第一參數、defer cancel() |
| 23 | 整數溢出靜默截斷 | ⚠️ 中 | 邊界檢查、math.MaxInt |

---

*本文件涵蓋 Go 1.21+ 特性，部分行為（如 for range 變數複用）在 Go 1.22 已修改。新增陷阱 15-23 含 nil map、select 隨機性、型別斷言、time.After 洩漏、Mutex 重入、rune/byte、JSON、context、整數溢出*
