---
title: Go
tags: [go, backend, concurrency]
sources: []
created: 2026-04-07
updated: 2026-04-07
---

# Go

## 語言定位

> Go 是一種簡潔、併發友好、適合雲端後端服務的語言。

## 核心特性

- **Goroutine**：輕量級執行緒，開啟成本極低
- **Channel**：訊息傳遞，分享記憶體靠通訊
- **defer**：資源清理的簡潔語法
- **Interface**：隱式實作，組合優先於繼承
- **GC**：自動記憶體回收

## 語法速查

```go
// 變數宣告
var x int = 10
y := 20  // 簡寫

// 函式
func add(a, b int) int {
    return a + b
}

// 結構體
type Point struct {
    X, Y float64
}

// 介面
type Reader interface {
    Read(p []byte) (n int, err error)
}

// Goroutine
go func() {
    // 並發執行
}()

// Channel
ch := make(chan int)
go func() {
    ch <- 42  // 發送
}()
v := <-ch  // 接收

// Error 處理
result, err := doSomething()
if err != nil {
    return err
}
```

## 併發模型

- **Goroutine + Channel**：CSP 模型的實現
- **sync.Mutex**：傳統互斥鎖
- **sync.WaitGroup**：等待一群 goroutine 完成
- **context.Context**：取消信號與超時

## Go 生態

| 領域 | 常用套件 |
|------|----------|
| Web 框架 | Gin, Echo, Fiber |
| gRPC | google.golang.org/grpc |
| 資料庫 | sqlx, GORM |
| CLI | cobra, urfave/cli |

## 相關概念

- [[concepts/併發模型]]
- [[concepts/記憶體管理]]
- [[concepts/錯誤處理]]

## 外部資源

- [Go Tour](https://tour.golang.org/)
- [Go by Example](https://gobyexample.com/)
