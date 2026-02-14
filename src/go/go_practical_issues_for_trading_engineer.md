# Go 入門實務會遇到的問題整理（偏交易系統 / 高併發場景）

------------------------------------------------------------------------

## 一、Concurrency 實務問題

### 1. goroutine ≠ OS Thread

-   Go 採用 M:N Scheduler（G / M / P 模型）
-   可能遇到：
    -   goroutine 暴增導致 GC 壓力
    -   blocking syscall 卡住 P
    -   GOMAXPROCS 設定不當導致 CPU 使用率異常

### 2. Data Race

常見問題： - map 併發 crash - slice append race - unsafe pointer
使用錯誤

工具：

``` bash
go run -race
```

------------------------------------------------------------------------

## 二、Memory & GC 問題

### 1. GC Pause / Latency Spike

低延遲系統常見： - tail latency 爆掉 - GC 導致 response 抖動

工具：

``` bash
go tool pprof
```

### 2. Escape Analysis

``` bash
go build -gcflags="-m"
```

-   了解 stack vs heap allocation
-   減少不必要的 heap allocation

------------------------------------------------------------------------

## 三、Debug 實務問題

### 常用工具

-   dlv（Delve debugger）
-   pprof
-   runtime.Stack()

### 常見問題

-   goroutine dump 看不懂
-   deadlock 找不到卡點
-   channel 卡死

------------------------------------------------------------------------

## 四、Channel 死鎖問題

常見錯誤：

``` text
fatal error: all goroutines are asleep - deadlock!
```

原因： - 沒人接收 - 忘記 close - range channel 卡死 - select default
使用錯誤

------------------------------------------------------------------------

## 五、HTTP Server 問題

### 1. Connection Leak

-   沒關 resp.Body
-   http client 沒設 timeout

### 2. Context 沒傳

-   goroutine leak
-   memory leak

------------------------------------------------------------------------

## 六、壓測工具

### k6

-   API 壓測
-   RPS / latency 分析

### 其他工具

-   wrk
-   vegeta
-   hey

------------------------------------------------------------------------

## 七、Production 常見問題

### 1. Goroutine Leak

症狀： - 記憶體慢慢上升 - QPS 不變

### 2. FD 用光

``` text
too many open files
```

需調整： - ulimit - http transport 設定

### 3. TCP TIME_WAIT 爆炸

高頻 API 常見

------------------------------------------------------------------------

## 八、Module / Dependency 問題

-   replace directive
-   私有 repo
-   vendor 模式

------------------------------------------------------------------------

## 九、進階優化方向（偏高頻 / 交易系統）

-   sync.Pool
-   object reuse
-   zero copy
-   netpoll
-   runtime scheduler 行為分析
-   lock contention 優化

------------------------------------------------------------------------

## 十、核心難點總結

真正困難在：

1.  理解 scheduler
2.  控制 GC latency
3.  找 goroutine leak

------------------------------------------------------------------------

# 建議練習方式

1.  寫高併發 REST API
2.  模擬撮合引擎
3.  寫 websocket server
4.  使用 benchmark + pprof 分析
5.  用壓測工具壓到出現瓶頸為止

------------------------------------------------------------------------

（適合具備 Linux / 系統底層經驗的工程師進階 Go 使用）
