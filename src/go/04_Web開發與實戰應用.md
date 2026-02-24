# Web 開發與實戰應用

> Go Web 開發、WebSocket、實時通訊與跨語言整合。

## 🌐 Web 開發基礎

### Web 框架
- [Go 編程實戰派 Web 開發基礎](Go編程實戰派Web開發基礎.md)

## 📡 實時通訊

### WebSocket
- [Websocket](websocket.md) - WebSocket 開發指南

### 實時通訊平台
- [LiveKit](LiveKit.md) - LiveKit 實時音視頻

## 🔗 跨語言整合

### Python + Go
- [pytago](pytago.md) - Python 與 Go 整合

## 🎯 完整指南

### 語言特性對比
- [Go 語言完整特性與常見誤解指南 (Python/C++ 開發者版)](golang_guide.md)

## 💡 Web 開發實踐

### HTTP Server
```go
package main

import (
    "fmt"
    "net/http"
)

func main() {
    http.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
        fmt.Fprintf(w, "Hello, World!")
    })

    http.ListenAndServe(":8080", nil)
}
```go

### RESTful API
```go
func handleUsers(w http.ResponseWriter, r *http.Request) {
    switch r.Method {
    case "GET":
        // 獲取用戶列表
    case "POST":
        // 創建用戶
    case "PUT":
        // 更新用戶
    case "DELETE":
        // 刪除用戶
    }
}
```go

### Middleware
```go
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        log.Printf("%s %s", r.Method, r.URL.Path)
        next.ServeHTTP(w, r)
    })
}
```go

## 🔌 WebSocket 實踐

### 基本連接
```go
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool {
        return true
    },
}

func wsHandler(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }
    defer conn.Close()

    for {
        _, message, err := conn.ReadMessage()
        if err != nil {
            break
        }
        conn.WriteMessage(websocket.TextMessage, message)
    }
}
```go

## 🌉 Python + Go 整合

### CGo 調用
```go
// export Add
func Add(a, b int) int {
    return a + b
}
```

### gRPC
```go
// 定義服務
service Calculator {
    rpc Add(Numbers) returns (Result);
}
```

**最後更新**: 2025-12-01
