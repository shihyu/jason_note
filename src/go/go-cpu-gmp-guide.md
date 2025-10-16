# Go 語言 CPU、GMP 模型與多程式執行完整指南

## 目錄
1. [Go 程式與 CPU 核心](#1-go-程式與-cpu-核心)
2. [GMP 調度模型詳解](#2-gmp-調度模型詳解)
3. [單一 Go 程式的執行模型](#3-單一-go-程式的執行模型)
4. [兩支 Go 程式的競爭問題](#4-兩支-go-程式的競爭問題)
5. [實際驗證範例](#5-實際驗證範例)
6. [最佳實踐建議](#6-最佳實踐建議)

---

## 1. Go 程式與 CPU 核心

### 1.1 預設 Processor 數量

**Go 1.5+ 版本：**
```
預設 P (Processor) 數量 = runtime.NumCPU()
```

在 16 核心 CPU 上：
```go
runtime.GOMAXPROCS(0)  // 返回 16
runtime.NumCPU()        // 返回 16
```

**歷史變化：**
- **Go 1.5 之前**：預設只有 1 個 P（需要手動設置)
- **Go 1.5 之後**：預設使用所有 CPU 核心

**驗證範例：**
```go
package main

import (
    "fmt"
    "runtime"
)

func main() {
    fmt.Printf("CPU 核心數: %d\n", runtime.NumCPU())
    fmt.Printf("GOMAXPROCS (預設使用): %d\n", runtime.GOMAXPROCS(0))
}
```

### 1.2 手動設置 GOMAXPROCS

```go
import "runtime"

// 設置使用 8 個核心
runtime.GOMAXPROCS(8)

// 查詢當前設置（傳入 0）
n := runtime.GOMAXPROCS(0)

// 獲取機器 CPU 核心數
numCPU := runtime.NumCPU()
```

**環境變數方式：**
```bash
GOMAXPROCS=8 go run main.go
```

---

## 2. GMP 調度模型詳解

### 2.1 核心概念

Go 使用 **M:N 調度模型**，將 M 個 Goroutine 調度到 N 個 OS Thread 上執行。

#### **三個核心組件：**

| 組件 | 全名 | 說明 | 數量 |
|------|------|------|------|
| **G** | Goroutine | 輕量級協程，用戶創建的並發任務 | 可以有幾萬個 |
| **M** | Machine (OS Thread) | 作業系統執行緒，真正執行代碼 | 動態調整（≥ P 的數量） |
| **P** | Processor | 邏輯處理器，執行上下文 | 固定 = GOMAXPROCS |

### 2.2 GMP 架構圖（16 核心）

```
CPU 核心層:  [核1] [核2] [核3] [核4] ... [核16]
               ↓     ↓     ↓     ↓         ↓
P 層:        [P0]  [P1]  [P2]  [P3]  ... [P15]  (16個，固定)
               ↓     ↓     ↓     ↓         ↓
M 層:        [M0]  [M1]  [M2]  [M3]  ... [M15+] (16+ 個，動態)
               ↓     ↓     ↓     ↓         ↓
G 層:      本地隊列 本地隊列 本地隊列     本地隊列
          [G1,G2] [G10,G11] [G20]      [G150]
                            ↓
                      全局隊列: [G1000, G1001, ...]
```

### 2.3 Goroutine 特點

**對比 OS Thread：**

| 特性 | Goroutine | OS Thread |
|------|-----------|-----------|
| 初始堆疊大小 | ~2 KB | 1-2 MB |
| 創建成本 | 極低 | 較高 |
| 切換成本 | 極低（用戶態） | 較高（內核態） |
| 數量限制 | 幾萬～幾十萬 | 幾千 |
| 調度器 | Go Runtime | OS Kernel |

**範例：**
```go
// 輕鬆創建 10000 個 goroutine
for i := 0; i < 10000; i++ {
    go func(id int) {
        // 執行任務
    }(i)
}
```

### 2.4 調度流程

#### **本地隊列 (Local Run Queue)**
- 每個 P 維護自己的 goroutine 隊列（最多 256 個）
- 優先從本地隊列取 goroutine 執行

```
P0 的本地隊列: [G1, G2, G3, G4, G5]
P1 的本地隊列: [G10, G11, G12]
P2 的本地隊列: [G20, G21]
```

#### **全局隊列 (Global Run Queue)**
- 當本地隊列滿了，新 goroutine 放入全局隊列
- 當本地隊列空了，從全局隊列獲取

#### **工作竊取 (Work Stealing)**
當某個 P 的本地隊列空了：
1. 先從全局隊列獲取 goroutine
2. 如果全局隊列也空了，從其他 P「偷」一半的 goroutine

**範例：**
```
執行前：
P0: []  (空閒)
P5: [G50, G51, G52, G53, G54, G55, G56, G57]  (繁忙)

執行 Work Stealing 後：
P0: [G54, G55, G56, G57]  (偷了一半)
P5: [G50, G51, G52, G53]
```

### 2.5 M (OS Thread) 的動態調整

#### **情況 1：純 CPU 密集型**
```
16 個 P → 約 16-17 個 M
```
因為沒有阻塞，不需要額外的 M。

#### **情況 2：有 I/O 阻塞**
```go
go func() {
    time.Sleep(time.Second)  // 阻塞！
}()
```

```
16 個 P → 可能 20-30+ 個 M
```

**原因：**
1. Goroutine 在 M1 上執行，遇到阻塞（如 I/O、Sleep）
2. M1 被阻塞，但 P0 還可以繼續工作
3. Go Runtime 創建新的 M2 來接管 P0
4. M1 等待阻塞結束後，可能重新綁定空閒的 P

**時間軸範例：**
```
時刻 1:
P0 -- M0 (執行 G1)

時刻 2: G1 遇到 I/O 阻塞
P0 -- M0 (阻塞中，等待 I/O)
P0 -- M16 (新創建，接管 P0，執行 G2)

時刻 3: M0 的 I/O 完成
M0 嘗試重新綁定空閒的 P，或進入休眠
```

### 2.6 調度時機

Go Scheduler 會在以下時機進行調度：

1. **主動讓出：**
   ```go
   runtime.Gosched()
   ```

2. **系統調用（阻塞）：**
   ```go
   os.ReadFile("file.txt")  // I/O
   time.Sleep(time.Second)  // 睡眠
   ```

3. **Channel 操作阻塞：**
   ```go
   data := <-ch  // 等待接收
   ch <- value   // 等待發送
   ```

4. **Goroutine 執行過久：**
   - Go 1.14+ 使用基於信號的搶占式調度
   - 每個 goroutine 執行約 10ms 後可能被搶占

---

## 3. 單一 Go 程式的執行模型

### 3.1 整體架構（16 核心）

```
【單一 Go 程式】
       ↓
  1 個 OS Process
       ↓
  16+ 個 OS Thread (M)
       ↓
  16 個 Processor (P)
       ↓
  幾萬個 Goroutine (G)
```

### 3.2 資源使用

在 16 核心機器上運行單一 Go 程式：

| 資源 | 數量 | 說明 |
|------|------|------|
| **Process** | 1 個 | 單一進程 |
| **OS Thread** | 16+ 個 | 動態調整 |
| **Processor (P)** | 16 個 | 固定，對應核心數 |
| **Goroutine** | 不限 | 可以幾萬個 |
| **CPU 使用** | 100% (16 核心) | 可以充分利用所有核心 |

### 3.3 範例程式

```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "sync"
    "time"
)

func main() {
    fmt.Printf("=== Go 程式資訊 ===\n")
    fmt.Printf("Process ID: %d\n", os.Getpid())
    fmt.Printf("CPU 核心數: %d\n", runtime.NumCPU())
    fmt.Printf("GOMAXPROCS (P): %d\n", runtime.GOMAXPROCS(0))
    fmt.Printf("初始 Goroutine: %d\n\n", runtime.NumGoroutine())
    
    var wg sync.WaitGroup
    
    // 創建 10000 個 goroutine
    for i := 0; i < 10000; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            
            // CPU 密集型任務
            sum := 0
            for j := 0; j < 1000000; j++ {
                sum += j
            }
            
            // 模擬一些工作
            time.Sleep(time.Millisecond * 10)
        }(i)
    }
    
    time.Sleep(time.Millisecond * 100)
    fmt.Printf("峰值 Goroutine: %d\n", runtime.NumGoroutine())
    
    wg.Wait()
    fmt.Printf("完成後 Goroutine: %d\n", runtime.NumGoroutine())
}
```

**執行結果：**
```
=== Go 程式資訊 ===
Process ID: 12345
CPU 核心數: 16
GOMAXPROCS (P): 16
初始 Goroutine: 1

峰值 Goroutine: 10001
完成後 Goroutine: 1
```

**CPU 使用情況：**
```bash
# 使用 top 或 htop 查看
PID    CPU%   Command
12345  1600%  myapp    (16 個核心 × 100% = 1600%)
```

---

## 4. 兩支 Go 程式的競爭問題

### 4.1 整體架構

當啟動兩支 Go 程式時：

```
【Go 程式 A】              【Go 程式 B】
       ↓                        ↓
  Process 1                 Process 2
       ↓                        ↓
  16+ Thread                16+ Thread
       ↓                        ↓
  16 個 P                   16 個 P
       ↓                        ↓
  幾萬個 G                  幾萬個 G
       ↓                        ↓
       └────────┬────────────────┘
                ↓
          競爭 16 個 CPU 核心
```

### 4.2 關鍵特點

| 項目 | 單一程式 | 兩支程式 |
|------|---------|---------|
| **Process 數** | 1 個 | 2 個（獨立） |
| **總 Thread 數** | 16+ 個 | 32+ 個 |
| **總 P 數** | 16 個 | 32 個（各 16 個） |
| **記憶體共享** | ✅ 所有 goroutine 共享 | ❌ 各自獨立 |
| **CPU 使用** | 獨占 16 核心 | 競爭 16 核心 |
| **通訊方式** | Channel（極快） | IPC/網路（較慢） |
| **隔離性** | 無隔離 | 完全隔離 |

### 4.3 CPU 競爭情況

#### **情況 1：兩個 CPU 密集型程式**

```
CPU: [核1] [核2] [核3] ... [核16]
       ↓     ↓     ↓         ↓
    Process A 和 Process B 的 Thread 競爭使用
```

**理想分配：**
```
Process A: 使用 8 個核心  (800% CPU)
Process B: 使用 8 個核心  (800% CPU)
總計: 1600% (16 核心全滿)
```

**實際情況：**
- OS Scheduler 動態調度
- 可能不是均等分配
- 取決於各程式的負載

#### **情況 2：一個忙碌，一個閒置**

```
Process A (閒置): ~1-2 個核心  (100-200% CPU)
Process B (忙碌): ~14-15 個核心 (1400-1500% CPU)
```

#### **情況 3：都是 I/O 密集型**

```
Process A: 創建 1000+ Thread，但大部分在等待 I/O
Process B: 創建 1000+ Thread，但大部分在等待 I/O

CPU 使用率: 可能只有 20-30%（大部分時間在等待）
```

### 4.4 程式間隔離

**完全隔離：**
- ❌ 不共享記憶體
- ❌ 無法直接通訊
- ❌ 一個崩潰不影響另一個
- ✅ 需要透過 IPC 通訊

**通訊方式：**

#### **1. HTTP/網路通訊（最常用）**
```go
// 程式 A - Server
http.HandleFunc("/", handler)
http.ListenAndServe(":8080", nil)

// 程式 B - Client
resp, _ := http.Get("http://localhost:8080")
```

#### **2. 共享檔案**
```go
// 程式 A 寫入
os.WriteFile("/tmp/data.txt", data, 0644)

// 程式 B 讀取
data, _ := os.ReadFile("/tmp/data.txt")
```

#### **3. Message Queue**
```go
// 使用 Redis, RabbitMQ 等
// 程式 A 發送
redis.Publish("channel", "message")

// 程式 B 接收
redis.Subscribe("channel")
```

#### **4. Unix Socket**
```go
// 程式 A
listener, _ := net.Listen("unix", "/tmp/app.sock")

// 程式 B
conn, _ := net.Dial("unix", "/tmp/app.sock")
```

### 4.5 手動控制核心分配

如果希望兩個程式各用一半核心：

```go
// 程式 A
runtime.GOMAXPROCS(8)  // 限制使用 8 個 P

// 程式 B
runtime.GOMAXPROCS(8)  // 限制使用 8 個 P
```

或使用環境變數：
```bash
GOMAXPROCS=8 ./app_a &
GOMAXPROCS=8 ./app_b &
```

**注意：**
- 這只是限制 P 的數量
- 實際 CPU 使用仍由 OS Scheduler 決定
- 無法「鎖定」特定 CPU 核心

---

## 5. 實際驗證範例

### 5.1 單一程式範例

**程式：single_app.go**
```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "time"
)

func main() {
    fmt.Printf("=== 單一 Go 程式 ===\n")
    fmt.Printf("PID: %d\n", os.Getpid())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    fmt.Printf("NumCPU: %d\n\n", runtime.NumCPU())
    
    // 創建 CPU 密集型 goroutine
    for i := 0; i < 100; i++ {
        go func(id int) {
            for {
                sum := 0
                for j := 0; j < 10000000; j++ {
                    sum += j
                }
            }
        }(i)
    }
    
    // 定期顯示狀態
    ticker := time.NewTicker(time.Second * 2)
    for range ticker.C {
        fmt.Printf("Goroutines: %d\n", runtime.NumGoroutine())
    }
}
```

**執行與監控：**
```bash
# Terminal 1: 運行程式
go run single_app.go

# Terminal 2: 監控 CPU
top -pid $(pgrep single_app)

# 應該看到 1600% CPU (16 核心全滿)
```

### 5.2 雙程式範例

**程式 A：app_a.go**
```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "time"
)

func main() {
    fmt.Printf("=== Go 程式 A ===\n")
    fmt.Printf("PID: %d\n", os.Getpid())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    
    // CPU 密集型工作
    for i := 0; i < 1000; i++ {
        go func(id int) {
            for {
                sum := 0
                for j := 0; j < 10000000; j++ {
                    sum += j
                }
            }
        }(i)
    }
    
    ticker := time.NewTicker(time.Second * 2)
    for range ticker.C {
        fmt.Printf("[程式 A] PID: %d, Goroutines: %d\n", 
            os.Getpid(), runtime.NumGoroutine())
    }
}
```

**程式 B：app_b.go**
```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "time"
)

func main() {
    fmt.Printf("=== Go 程式 B ===\n")
    fmt.Printf("PID: %d\n", os.Getpid())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    
    // CPU 密集型工作
    for i := 0; i < 1000; i++ {
        go func(id int) {
            for {
                sum := 0
                for j := 0; j < 10000000; j++ {
                    sum += j
                }
            }
        }(i)
    }
    
    ticker := time.NewTicker(time.Second * 2)
    for range ticker.C {
        fmt.Printf("[程式 B] PID: %d, Goroutines: %d\n", 
            os.Getpid(), runtime.NumGoroutine())
    }
}
```

**執行與監控：**
```bash
# Terminal 1: 運行程式 A
go run app_a.go

# Terminal 2: 運行程式 B
go run app_b.go

# Terminal 3: 監控兩個程式
top -pid $(pgrep -d',' app_)

# 或使用 htop 更直觀
htop
```

**預期結果：**
```
PID    CPU%   Command
1234   800%   app_a    (約 8 個核心)
5678   800%   app_b    (約 8 個核心)
總計:  1600%  (16 個核心全滿)
```

### 5.3 查看 Thread 數量

```bash
# Linux: 查看某個進程的 thread 數
ps -T -p <PID>

# 或
ps -eLf | grep <PID>

# 或使用 top 查看 thread
top -H -p <PID>

# macOS:
ps -M <PID>
```

---

## 6. 最佳實踐建議

### 6.1 單一程式場景

**何時使用預設配置（16 個 P）：**
✅ 混合型工作負載（CPU + I/O）
✅ 微服務應用
✅ Web Server
✅ API Gateway

**範例：**
```go
// 預設配置即可，無需設置
// runtime.GOMAXPROCS(runtime.NumCPU()) // 預設已經是這樣
```

### 6.2 雙程式場景

**何時需要手動限制：**
- 明確想要資源隔離
- 避免互相搶佔 CPU
- 確保關鍵程式有足夠資源

**範例：**
```go
// 關鍵服務 A - 使用 12 個核心
runtime.GOMAXPROCS(12)

// 次要服務 B - 使用 4 個核心
runtime.GOMAXPROCS(4)
```

### 6.3 性能監控

```go
package main

import (
    "fmt"
    "runtime"
    "time"
)

func monitorPerformance() {
    ticker := time.NewTicker(time.Second * 5)
    
    for range ticker.C {
        var m runtime.MemStats
        runtime.ReadMemStats(&m)
        
        fmt.Printf("=== 性能指標 ===\n")
        fmt.Printf("Goroutines: %d\n", runtime.NumGoroutine())
        fmt.Printf("OS Threads: %d\n", runtime.NumCPU())
        fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
        fmt.Printf("記憶體使用: %d MB\n", m.Alloc/1024/1024)
        fmt.Printf("GC 次數: %d\n\n", m.NumGC)
    }
}

func main() {
    go monitorPerformance()
    
    // 你的程式邏輯...
    select {}
}
```

### 6.4 常見問題與解決方案

#### **問題 1：創建太多 Goroutine 導致記憶體耗盡**

**解決方案：使用 Worker Pool**
```go
func workerPool(jobs <-chan int, results chan<- int) {
    // 限制並發數為 100
    for j := range jobs {
        results <- process(j)
    }
}

func main() {
    jobs := make(chan int, 1000)
    results := make(chan int, 1000)
    
    // 創建固定數量的 worker
    for w := 0; w < 100; w++ {
        go workerPool(jobs, results)
    }
    
    // 發送任務...
}
```

#### **問題 2：單個 CPU 密集型任務無法利用多核**

**解決方案：分割任務**
```go
func processInParallel(data []int) {
    numWorkers := runtime.GOMAXPROCS(0)
    chunkSize := len(data) / numWorkers
    
    var wg sync.WaitGroup
    for i := 0; i < numWorkers; i++ {
        wg.Add(1)
        go func(start int) {
            defer wg.Done()
            end := start + chunkSize
            // 處理 data[start:end]
        }(i * chunkSize)
    }
    wg.Wait()
}
```

#### **問題 3：兩個程式互相干擾**

**解決方案 1：使用容器隔離**
```bash
# Docker 限制 CPU
docker run --cpus="8" myapp_a
docker run --cpus="8" myapp_b
```

**解決方案 2：使用 cgroups（Linux）**
```bash
# 限制 CPU 使用
cgcreate -g cpu:/app_a
cgset -r cpu.cfs_quota_us=800000 app_a
cgexec -g cpu:app_a ./app_a
```

**解決方案 3：手動設置 GOMAXPROCS**
```go
// 在程式啟動時設置
runtime.GOMAXPROCS(8)
```

### 6.5 架構建議

#### **單體應用**
```
單一 Go 程式
    ↓
使用預設 GOMAXPROCS
    ↓
利用全部 16 核心
```

#### **微服務架構**
```
服務 A (8 核) ← HTTP → 服務 B (4 核)
                          ↓
                      服務 C (4 核)
```

#### **負載均衡**
```
Nginx / HAProxy
        ↓
    ┌───┴───┬───────┬───────┐
    ↓       ↓       ↓       ↓
 實例 1  實例 2  實例 3  實例 4
 (4核)   (4核)   (4核)   (4核)
```

---

## 總結

### 關鍵要點

1. **Go 程式結構：**
   - 1 個 Process
   - 動態數量的 M (Thread)
   - 固定數量的 P (= GOMAXPROCS)
   - 大量的 G (Goroutine)

2. **16 核心單一程式：**
   - 預設創建 16 個 P
   - 至少 16 個 M
   - 可以充分利用所有核心

3. **16 核心雙程式：**
   - 兩個獨立的 Process
   - 總共約 32+ 個 Thread
   - 競爭 16 個 CPU 核心
   - 需要 OS Scheduler 調度

4. **調度機制：**
   - 本地隊列 + 全局隊列
   - Work Stealing 負載均衡
   - 搶占式調度（Go 1.14+）

### 記憶口訣

```
一個程式一個 Process
GOMAXPROCS 個 Processor
動態調整的 Machine Thread
成千上萬的 Goroutine
```

### 參考資源

- [Go 官方文檔 - Runtime](https://pkg.go.dev/runtime)
- [Go Scheduler 設計文檔](https://github.com/golang/go/blob/master/src/runtime/proc.go)
- [Go 並發模型解析](https://go.dev/blog/waza-talk)

---

**最後更新：** 2025-10-17
**適用版本：** Go 1.18+