# Go Context 完整整理

## 1. Context 是什麼

在 Go 中，`context` 用來控制 **goroutine** 與 **請求** 的生命週期。

核心用途如下：

- Cancellation（取消任務）
- Timeout / Deadline（逾時控制）
- Propagation（跨 API 傳遞請求狀態）
- Metadata（傳遞請求資料）

一句話總結：

> `context` 就是 goroutine 與請求的生命週期管理器。

---

## 2. Context 介面

```go
type Context interface {
    Done() <-chan struct{}
    Err() error
    Deadline() (time.Time, bool)
    Value(key any) any
}
```

| 方法 | 作用 |
| --- | --- |
| `Done()` | 回傳一個 channel；當 context 被取消時會關閉 |
| `Err()` | 回傳取消原因 |
| `Deadline()` | 回傳截止時間 |
| `Value()` | 取得 context 內的值 |

### 2.1 四個方法之間的關係

```text
┌──────────────────────────────────────────┐
│              context.Context             │
├──────────────────────────────────────────┤
│ Done()      -> 取消通知 channel          │
│ Err()       -> 取消原因                  │
│ Deadline()  -> 最晚何時必須停止          │
│ Value()     -> 傳遞請求範圍內的資料      │
└──────────────────────────────────────────┘
```

### 2.2 `Err()` 常見回傳值

當 `<-ctx.Done()` 被觸發後，通常會再檢查 `ctx.Err()`：

```go
if err := ctx.Err(); err != nil {
    return err
}
```

常見結果如下：

| 錯誤值 | 意義 |
| --- | --- |
| `context.Canceled` | 被主動取消 |
| `context.DeadlineExceeded` | 超過 deadline 或 timeout |

---

## 3. 建立 Context

### 3.1 `Background`

```go
ctx := context.Background()
```

特性：

- 是根 context
- 永遠不會被取消
- 永遠沒有截止時間

### 3.2 `WithCancel`

```go
ctx, cancel := context.WithCancel(parent)
defer cancel()
```

用途：手動取消。

```text
cancel()
   │
   ▼
ctx.Done() 關閉
```

### 3.3 `WithTimeout`

```go
ctx, cancel := context.WithTimeout(parent, 3*time.Second)
defer cancel()
```

效果：

```text
t0 -------- t0+3s
   valid     timeout
               │
               ▼
         ctx.Done()
```

逾時後 context 會自動取消。

### 3.4 `WithDeadline`

```go
ctx, cancel := context.WithDeadline(parent, time.Now().Add(3*time.Second))
defer cancel()
```

`WithTimeout` 本質上只是 `WithDeadline` 的語法糖。

### 3.5 建立方式總覽

```text
context.Background()
        │
        ├── context.WithCancel(parent)
        │       └── 手動呼叫 cancel()
        │
        ├── context.WithTimeout(parent, d)
        │       └── 時間到自動取消
        │
        └── context.WithDeadline(parent, t)
                └── 到達指定時間自動取消
```

---

## 4. `Done` Channel

```go
select {
case <-ctx.Done():
    return
}
```

當 context 被取消時，可能來源如下：

```text
cancel()
timeout
parent cancel
      │
      ▼
ctx.Done() 關閉
```

收到訊號後，goroutine 就能結束。

### 4.1 `Done` + `Err` 的典型配合

```go
select {
case <-ctx.Done():
    return ctx.Err()
case result := <-resultCh:
    return result
}
```

這種寫法的重點是：

- `Done()` 負責通知
- `Err()` 負責說明原因
- 兩者通常成對出現

---

## 5. Goroutine 取消模式

常見寫法：

```go
func worker(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            work()
        }
    }
}
```

流程：

```text
cancel()
   │
   ▼
ctx.Done()
   │
   ▼
goroutine 結束
```

區塊示意圖：

```text
┌────────────┐      ┌────────────────┐      ┌─────────────────┐
│ parent ctx │ ───> │ worker select  │ ───> │ work / return   │
└────────────┘      └────────────────┘      └─────────────────┘
        │                    │
        │ cancel             │ listen ctx.Done()
        ▼                    ▼
  ctx.Done() 關閉        停止 goroutine
```

---

## 6. `Timeout` 使用情境

### HTTP Request

```go
ctx, cancel := context.WithTimeout(ctx, 2*time.Second)
defer cancel()
```

如果後端太慢：

```text
2s timeout
      │
      ▼
取消請求
```

完整流程示意：

```text
┌──────────────┐
│ HTTP Client  │
└──────┬───────┘
       │ request
       ▼
┌──────────────┐
│ HTTP Handler │
└──────┬───────┘
       │ 建立 timeout context
       ▼
┌──────────────┐
│ Service      │
└──────┬───────┘
       │ 傳遞 ctx
       ▼
┌──────────────┐
│ Repository   │
└──────┬───────┘
       │ QueryContext(ctx, ...)
       ▼
┌──────────────┐
│ Database     │
└──────────────┘

超時後：
Client / Handler / Service / DB query 一路收到取消訊號
```

### Database Query

```go
db.QueryContext(ctx, "SELECT * FROM users")
```

如果資料庫卡住：

```text
timeout
   │
   ▼
查詢取消
```

實務上應優先使用支援 context 的 API，例如：

- `http.NewRequestWithContext`
- `db.QueryContext`
- `db.ExecContext`
- `exec.CommandContext`

---

## 7. Context 傳遞

`context` 會沿著呼叫鏈一路往下傳：

```text
HTTP handler
      │
      ▼
服務層
      │
      ▼
儲存層
      │
      ▼
database
```

區塊示意圖：

```text
┌──────────────┐
│ Handler      │
└──────┬───────┘
       │ ctx
       ▼
┌──────────────┐
│ Service      │
└──────┬───────┘
       │ ctx
       ▼
┌──────────────┐
│ Repository   │
└──────┬───────┘
       │ ctx
       ▼
┌──────────────┐
│ Driver / DB  │
└──────────────┘
```

範例：

```go
func handler(ctx context.Context) {
    service(ctx)
}

func service(ctx context.Context) {
    repo(ctx)
}
```

如果請求被取消：

```text
ctx.Done()
   │
   ▼
整條 call chain 停止
```

---

## 8. Context Tree

`context` 本質上是一棵 **取消樹**。

```text
Background
     │
     ▼
Request Context
     │
     ├── DB query goroutine
     ├── cache goroutine
     └── worker goroutine
```

如果請求被取消：

```text
cancel()
   │
   ▼
所有子 context 一起取消
```

父子關係示意圖：

```text
Background
   │
   └── Request A
       │
       ├── cache lookup
       ├── DB query
       └── async worker
            │
            └── sub task

Request A 被取消時：
上面整個分支全部停止，但不影響其他 request。
```

---

## 9. 傳遞 Metadata

```go
ctx = context.WithValue(ctx, "userID", 123)
```

取得方式：

```go
userID := ctx.Value("userID")
```

常見用途：

- 請求 ID
- user ID
- trace ID

注意：

> 不建議在 context 中放大量資料。

建議：

- 放與單次請求強相關的資料，例如 request ID、trace ID、auth 資訊
- 不要放可選參數、巨大物件、全域設定
- key 最好使用自定型別，避免碰撞

範例：

```go
type contextKey string

const userIDKey contextKey = "userID"

ctx = context.WithValue(ctx, userIDKey, 123)
```

---

## 10. 官方最佳實務

### 10.1 `context` 放在第一個參數

```go
func Query(ctx context.Context, sql string)
```

### 10.2 不要把 `context` 存進 struct

錯誤示範：

```go
type Service struct {
    ctx context.Context
}
```

正確做法：

```text
每個函式都顯式傳入 context
```

原因：避免 goroutine 的生命週期管理混亂。

### 10.3 一定要呼叫 `cancel`

```go
ctx, cancel := context.WithTimeout(...)
defer cancel()
```

原因如下：

- 停止計時器
- 釋放資源

### 10.4 不要把 `context` 當成可選參數容器

不建議這樣做：

```go
ctx = context.WithValue(ctx, "limit", 100)
ctx = context.WithValue(ctx, "sort", "desc")
ctx = context.WithValue(ctx, "page", 2)
```

原因：

- 參數語意不清楚
- 呼叫端難追蹤
- 型別不安全

這類資料應直接用函式參數或結構體傳遞。

---

## 11. Goroutine Leak 範例

錯誤示範：

```go
go func() {
    val := <-ch
    fmt.Println(val)
}()
```

如果一直沒有資料：

```text
goroutine 永遠阻塞
```

正確寫法：

```go
go func() {
    select {
    case val := <-ch:
        fmt.Println(val)
    case <-ctx.Done():
        return
    }
}()
```

### 11.1 常見錯誤模式

| 錯誤模式 | 問題 |
| --- | --- |
| 建了 `WithTimeout` 卻沒 `cancel()` | timer 與資源可能延後釋放 |
| 開 goroutine 但不監聽 `ctx.Done()` | 容易出現 goroutine leak |
| 在深層重新建立 `Background()` | 取消鏈被截斷 |
| 把大量業務資料塞進 `Value()` | context 被濫用 |

---

## 12. 進階 API

### 12.1 `signal.NotifyContext`

這個 API 常用在 CLI、daemon、HTTP server 優雅停止。

```go
ctx, stop := signal.NotifyContext(context.Background(), os.Interrupt, syscall.SIGTERM)
defer stop()

<-ctx.Done()
log.Println("收到停止訊號:", ctx.Err())
```

區塊示意圖：

```text
SIGINT / SIGTERM
       │
       ▼
signal.NotifyContext(...)
       │
       ▼
ctx.Done() 關閉
       │
       ▼
main / server / worker 開始收尾
```

### 12.2 `context.WithoutCancel`

當你需要保留 value，但不想被上游取消影響時可以使用。

```go
detached := context.WithoutCancel(parent)
```

適合情境：

- 請求已結束，但還要寫審計日誌
- 背景補償任務要延續執行

注意：這會切斷取消鏈，不能亂用。

### 12.3 `context.AfterFunc`

可以在 context 被取消後觸發回呼。

```go
stop := context.AfterFunc(ctx, func() {
    log.Println("context 已取消，執行清理")
})
defer stop()
```

常見用途：

- 取消時釋放額外資源
- 發送取消事件
- 喚醒等待中的流程

---

## 13. HTTP Middleware 實戰

### 13.1 加上 Timeout Middleware

```go
func timeoutMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
        defer cancel()

        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

流程圖：

```text
Client
  │
  ▼
Middleware 建立 timeout ctx
  │
  ▼
Handler 使用 r.Context()
  │
  ▼
Service / DB 沿路傳遞 ctx
  │
  ▼
超時後整條鏈一起停止
```

### 13.2 帶入 Request ID

```go
type contextKey string

const requestIDKey contextKey = "requestID"

func requestIDMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        requestID := uuid.NewString()
        ctx := context.WithValue(r.Context(), requestIDKey, requestID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}
```

讀取方式：

```go
func handler(w http.ResponseWriter, r *http.Request) {
    requestID, _ := r.Context().Value(requestIDKey).(string)
    fmt.Fprintln(w, requestID)
}
```

---

## 14. Worker Pool 與 Background Job

### 14.1 Worker Pool 正確接收取消訊號

```go
func worker(ctx context.Context, jobs <-chan int, results chan<- int) {
    for {
        select {
        case <-ctx.Done():
            return
        case job, ok := <-jobs:
            if !ok {
                return
            }
            results <- job * 2
        }
    }
}
```

示意圖：

```text
jobs channel ────────┐
                     ▼
               ┌──────────┐
ctx.Done() ───>│ worker   │───> results channel
               └──────────┘
                     │
                     └── 收到取消就退出
```

### 14.2 背景任務不要誤用請求 Context

錯誤做法：

```go
func handler(w http.ResponseWriter, r *http.Request) {
    go sendEmail(r.Context())
    w.WriteHeader(http.StatusAccepted)
}
```

問題：HTTP 回應結束後，`r.Context()` 很快就可能被取消。

較合理做法：

```go
func handler(w http.ResponseWriter, r *http.Request) {
    detached := context.WithoutCancel(r.Context())
    go sendEmail(detached)
    w.WriteHeader(http.StatusAccepted)
}
```

如果這個背景工作本身需要壽命限制，應再包一層 timeout：

```go
detached := context.WithoutCancel(r.Context())
jobCtx, cancel := context.WithTimeout(detached, 10*time.Second)
defer cancel()
go sendEmail(jobCtx)
```

---

## 15. 測試 `cancel` 與 `timeout`

### 15.1 測試取消是否生效

```go
func TestWorkerStopsOnCancel(t *testing.T) {
    ctx, cancel := context.WithCancel(context.Background())
    done := make(chan struct{})

    go func() {
        defer close(done)
        <-ctx.Done()
    }()

    cancel()

    select {
    case <-done:
    case <-time.After(time.Second):
        t.Fatal("worker 沒有在取消後結束")
    }
}
```

### 15.2 測試 Timeout

```go
func TestContextTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Millisecond)
    defer cancel()

    <-ctx.Done()

    if !errors.Is(ctx.Err(), context.DeadlineExceeded) {
        t.Fatalf("預期 DeadlineExceeded，實際得到 %v", ctx.Err())
    }
}
```

### 15.3 測試原則

- 測試不要睡太久，避免整體測試變慢
- timeout 數值要短，但不要短到不穩定
- 優先檢查 `ctx.Err()`，不要只檢查 channel 是否關閉

---

## 16. 總結

| 功能 | 作用 |
| --- | --- |
| Cancellation | 停止 goroutine |
| Timeout | 任務時間限制 |
| Propagation | 傳遞請求狀態 |
| Metadata | 傳遞請求資料 |

一句話總結：

```text
context = goroutine lifecycle control
```

再補一個整體區塊圖：

```text
┌────────────────────────────────────────────────────┐
│                    一次請求流程                    │
├────────────────────────────────────────────────────┤
│ Client                                             │
│   │                                                │
│   ▼                                                │
│ Handler 建立 ctx / timeout                         │
│   │                                                │
│   ▼                                                │
│ Service 傳遞 ctx                                   │
│   │                                                │
│   ▼                                                │
│ Repository / DB / RPC 使用支援 context 的 API      │
│   │                                                │
│   ▼                                                │
│ timeout / cancel -> Done() 關閉 -> 全鏈停止        │
└────────────────────────────────────────────────────┘
```
