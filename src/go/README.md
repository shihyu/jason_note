# Go 程式設計完整指南

> Golang 從基礎到高性能開發的完整學習資源。

## 📊 文檔統計

- **核心文檔**: 28 個
- **主題分類**: 5 個領域
- **適用對象**: Go 開發者、後端工程師

---

## 🗂️ 主題分類

### 📗 基礎入門

#### [01. Go 基礎與模組管理](01_Go基礎與模組管理.md)
**語法基礎、Go Modules** | 難度: ⭐⭐

核心內容：
- Go 編程實戰派基礎入門
- Golang Note 學習筆記
- Go Modules 完整指南
- 從一知半解到略懂 Go modules
- 基礎語法與範例

**適合**: Go 新手、需要系統學習基礎

---

### 📘 並發與性能

#### [02. 並發編程與 GMP 模型](02_並發編程與GMP模型.md)
**Goroutine、Channel、GMP** | 難度: ⭐⭐⭐⭐

核心內容：
- Goroutine 與 GMP 原理全面分析
- Go 語言 CPU、GMP 模型與多程式執行
- Goroutine vs C++/Rust 協程對比
- Go 併發機制完整指南
- 行程、執行緒、協程詳解
- sync.Mutex 和 sync.RWMutex

**適合**: 中高級開發者、性能優化工程師

---

### 📙 Runtime 與記憶體管理

#### [03. Runtime 與記憶體管理](03_Runtime與記憶體管理.md)
**GC、Runtime、Memory** | 難度: ⭐⭐⭐⭐

核心內容：
- Go Runtime 完整指南
- GC 全面解析
- Golang 記憶體管理
- Returning Pointer from Function

**適合**: 需要深入理解 Go 內部機制

---

### 📙 Web 開發與實戰

#### [04. Web 開發與實戰應用](04_Web開發與實戰應用.md)
**Web 框架、WebSocket、實戰** | 難度: ⭐⭐⭐

核心內容：
- Go 編程實戰派 Web 開發基礎
- WebSocket 開發
- LiveKit 實時通訊
- pytago Python+Go 整合
- Interface 應用

**適合**: Web 後端開發者

---

### 📙 性能分析與除錯

#### [05. 性能分析與除錯](05_性能分析與除錯.md)
**Profiling、Trace、Debug** | 難度: ⭐⭐⭐⭐

核心內容：
- Go 效能分析與最佳化指南
- Golang 大殺器之跟蹤剖析 trace
- Golang Debugger
- Go + MySQL 死鎖問題調查
- Golang 高效能開發完整指南

**適合**: 性能優化、問題排查

---

## 🎯 學習路徑建議

### 新手路徑（2-4週）

**第一階段：基礎語法**
1. [Go 基礎與模組管理](01_Go基礎與模組管理.md)
   - 學習基礎語法
   - 理解 Go Modules
   - 實作簡單程式

**第二階段：並發入門**
1. 學習 Goroutine 基礎
2. 理解 Channel 通訊
3. 實作並發程式

---

### 進階路徑（1-3個月）

**深入並發**
1. [並發編程與 GMP 模型](02_並發編程與GMP模型.md)
   - GMP 調度模型
   - 鎖機制深入
   - 並發模式

**Runtime 理解**
1. [Runtime 與記憶體管理](03_Runtime與記憶體管理.md)
   - GC 原理
   - 記憶體分配
   - Runtime 機制

**Web 開發**
1. [Web 開發與實戰應用](04_Web開發與實戰應用.md)
   - Web 框架
   - WebSocket
   - 實戰項目

---

### 專家路徑（持續學習）

**性能優化**
1. [性能分析與除錯](05_性能分析與除錯.md)
   - pprof 分析
   - trace 追蹤
   - 性能調優

**系統級開發**
1. 微服務架構
2. 分散式系統
3. 雲原生應用

---

## 💡 使用說明

### 學習 Go 基礎
→ [Go 基礎與模組管理](01_Go基礎與模組管理.md)

### 理解並發機制
→ [並發編程與 GMP 模型](02_並發編程與GMP模型.md)

### 深入 Runtime
→ [Runtime 與記憶體管理](03_Runtime與記憶體管理.md)

### Web 開發
→ [Web 開發與實戰應用](04_Web開發與實戰應用.md)

### 性能優化
→ [性能分析與除錯](05_性能分析與除錯.md)

---

## 🔗 相關資源

### 其他章節
- [Python 程式設計](../python/) - Python vs Go 對比
- [C++ 程式設計](../c++/) - C++ vs Go 性能對比
- [Rust 程式設計](../rust/) - Rust vs Go 協程對比

### 外部資源
- [Go 官方文檔](https://go.dev/doc/)
- [Effective Go](https://go.dev/doc/effective_go)
- [Go by Example](https://gobyexample.com/)
- [The Go Blog](https://go.dev/blog/)

---

## 🚀 快速開始

### Hello World

```go
package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}
```

### Goroutine 基礎

```go
package main

import (
    "fmt"
    "time"
)

func say(s string) {
    for i := 0; i < 3; i++ {
        time.Sleep(100 * time.Millisecond)
        fmt.Println(s)
    }
}

func main() {
    go say("world")
    say("hello")
}
```

### Channel 通訊

```go
package main

import "fmt"

func sum(s []int, c chan int) {
    sum := 0
    for _, v := range s {
        sum += v
    }
    c <- sum // 發送到 channel
}

func main() {
    s := []int{7, 2, 8, -9, 4, 0}
    c := make(chan int)

    go sum(s[:len(s)/2], c)
    go sum(s[len(s)/2:], c)

    x, y := <-c, <-c // 從 channel 接收
    fmt.Println(x, y, x+y)
}
```

### Web Server

```go
package main

import (
    "fmt"
    "net/http"
)

func handler(w http.ResponseWriter, r *http.Request) {
    fmt.Fprintf(w, "Hello, %s!", r.URL.Path[1:])
}

func main() {
    http.HandleFunc("/", handler)
    http.ListenAndServe(":8080", nil)
}
```

---

**最後更新**: 2025-12-01
**維護狀態**: ✅ 活躍更新
**貢獻**: 歡迎補充與修正
