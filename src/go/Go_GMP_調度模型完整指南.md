# Go 的 GMP 調度模型完整指南

## 一、基本概念（用餐廳類比）

想像 Go 程序是一家高效率的餐廳：

| 角色 | 是什麼 | 餐廳類比 | 特點 |
|------|--------|----------|------|
| **G** (Goroutine) | 你寫的任務 | 📋 客人的訂單 | 超級多、超級輕（2KB） |
| **M** (Machine) | OS 線程 | 👨‍🍳 廚師 | 真正幹活的人（8MB） |
| **P** (Processor) | 邏輯處理器 | 🍳 廚房工作檯 | 數量 = CPU 核心數 |

---

## 二、基本數量關係

### 在 16 核心 CPU 上：

```go
package main

import (
    "fmt"
    "runtime"
)

func main() {
    fmt.Println("CPU 核心數:", runtime.NumCPU())           // 16
    fmt.Println("P 的數量:", runtime.GOMAXPROCS(0))        // 16（預設）
    fmt.Println("當前 G 數量:", runtime.NumGoroutine())    // 1（main goroutine）
    
    // 創建 1000 個 goroutine
    for i := 0; i < 1000; i++ {
        go func(id int) {
            // 做一些工作
            sum := 0
            for j := 0; j < 1000000; j++ {
                sum += j
            }
        }(i)
    }
    
    fmt.Println("創建後 G 數量:", runtime.NumGoroutine())  // 約 1000
}
```

**白話解釋：**
- 有 16 個工作檯（P）
- 來了 1000 份訂單（G）
- 每個工作檯分配約 62 份訂單
- 廚師（M）會根據需要自動出現（通常 ≈ P 的數量）

---

## 三、完整工作流程

### 範例 1：基本調度

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func main() {
    // 設置使用 4 個核心（方便觀察）
    runtime.GOMAXPROCS(4)
    
    var wg sync.WaitGroup
    
    // 創建 12 個 goroutine
    for i := 0; i < 12; i++ {
        wg.Add(1)
        go worker(i, &wg)
    }
    
    wg.Wait()
    fmt.Println("所有任務完成")
}

func worker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    fmt.Printf("G%d 開始執行\n", id)
    
    // CPU 密集型工作
    sum := 0
    for i := 0; i < 100000000; i++ {
        sum += i
    }
    
    fmt.Printf("G%d 完成\n", id)
}
```

**執行過程（白話）：**

```
1. 啟動時：
   - 創建 4 個 P（P0, P1, P2, P3）
   - 創建 12 個 G（G0~G11）

2. 初始分配：
   P0 隊列: [G0, G4, G8]
   P1 隊列: [G1, G5, G9]
   P2 隊列: [G2, G6, G10]
   P3 隊列: [G3, G7, G11]

3. 開始執行：
   M0 + P0 → 執行 G0
   M1 + P1 → 執行 G1
   M2 + P2 → 執行 G2
   M3 + P3 → 執行 G3
   
   （4 個廚師同時在 4 個工作檯做菜）

4. G0 完成後：
   M0 + P0 → 立刻取出 G4 繼續執行
   
   （廚師做完一份訂單，立刻拿下一份）

5. 全部完成：
   12 個 G 都執行完畢
```

---

## 四、阻塞場景（重點！）

### 範例 2：遇到阻塞操作

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func main() {
    runtime.GOMAXPROCS(4)
    
    var wg sync.WaitGroup
    
    // 創建 20 個會阻塞的 goroutine
    for i := 0; i < 20; i++ {
        wg.Add(1)
        go blockingWorker(i, &wg)
    }
    
    wg.Wait()
}

func blockingWorker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    fmt.Printf("G%d 開始\n", id)
    
    // 模擬 I/O 阻塞（網絡請求、文件讀取等）
    time.Sleep(1 * time.Second)
    
    fmt.Printf("G%d 完成\n", id)
}
```

**阻塞時的處理（白話）：**

```
1. G0 在 M0 上執行，遇到 time.Sleep
   
2. Go runtime 的處理：
   ① G0 進入休眠狀態
   ② P0 和 M0 解綁
   ③ P0 立刻找到或創建新的 M（比如 M4）
   ④ P0 + M4 繼續執行隊列中的下一個 G
   
   （這個廚師要等食材，工作檯不能閒著，換個廚師繼續做）

3. 1 秒後 G0 醒來：
   ① G0 重新進入某個 P 的隊列
   ② 等待 M 來執行
   
   （食材到了，訂單重新排隊）
```

---

## 五、Work Stealing（搶工作機制）

### 範例 3：負載不均衡

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func main() {
    runtime.GOMAXPROCS(4)
    
    var wg sync.WaitGroup
    
    // P0 分配到重任務
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("重任務 G%d 開始\n", id)
            time.Sleep(2 * time.Second) // 模擬重任務
            fmt.Printf("重任務 G%d 完成\n", id)
        }(i)
    }
    
    // P1-P3 分配到輕任務
    for i := 100; i < 103; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("輕任務 G%d 開始\n", id)
            time.Sleep(100 * time.Millisecond) // 快速完成
            fmt.Printf("輕任務 G%d 完成\n", id)
        }(i)
    }
    
    wg.Wait()
}
```

**Work Stealing 流程（白話）：**

```
1. 初始狀態：
   P0: [G0, G1, G2, G3, G4]  ← 5 個重任務
   P1: [G100]                ← 1 個輕任務
   P2: [G101]
   P3: [G102]

2. 執行過程：
   - P1 的 M1 很快完成 G100
   - P1 的隊列空了！

3. Work Stealing 觸發：
   - M1 發現 P1 沒工作了
   - M1 偷偷去看 P0 的隊列
   - M1 從 P0 隊列尾部偷走一半：[G3, G4]
   
   （空閒的廚師去幫忙別的工作檯）

4. 結果：
   P0: [G0, G1, G2]
   P1: [G3, G4]  ← 偷來的
   
   負載更均衡了！
```

---

## 六、系統調用場景

### 範例 4：系統調用阻塞

```go
package main

import (
    "fmt"
    "os"
    "runtime"
    "sync"
)

func main() {
    runtime.GOMAXPROCS(4)
    
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go syscallWorker(i, &wg)
    }
    
    wg.Wait()
}

func syscallWorker(id int, wg *sync.WaitGroup) {
    defer wg.Done()
    
    fmt.Printf("G%d 準備系統調用\n", id)
    
    // 系統調用（會阻塞 M）
    file, _ := os.Create(fmt.Sprintf("/tmp/test_%d.txt", id))
    file.WriteString("Hello")
    file.Close()
    
    fmt.Printf("G%d 系統調用完成\n", id)
}
```

**系統調用時的處理（白話）：**

```
1. G0 在 M0 上執行系統調用（寫文件）
   
2. 問題：系統調用會阻塞 M0（OS 層面的阻塞）
   
3. Go runtime 的處理：
   ① M0 和 G0 一起被阻塞（陷入內核態）
   ② P0 檢測到 M0 被阻塞
   ③ P0 解綁 M0，去找新的 M（比如 M5）
   ④ P0 + M5 繼續執行其他 G
   
   （廚師卡在某個步驟，工作檯換個廚師繼續）

4. 系統調用完成後：
   ① M0 和 G0 恢復
   ② M0 嘗試重新獲取 P
   ③ 如果沒有空閒 P，M0 和 G0 進入休眠
   ④ G0 會被放入全局隊列，等待調度
   
   （原來的廚師回來了，如果沒有空工作檯，就待命）
```

---

## 七、完整狀態圖

```
┌─────────────────────────────────────────────────────────┐
│                     Go Scheduler                         │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  全局隊列 (Global Queue)                                  │
│  [G50, G51, G52, ...]  ← 沒有 P 的 G 在這裡等待           │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  P0 [本地隊列]          M0 ─────→ 正在執行 G0              │
│  [G1, G2, G3]                                             │
│                                                           │
│  P1 [本地隊列]          M1 ─────→ 正在執行 G10             │
│  [G11, G12, G13]                                          │
│                                                           │
│  P2 [本地隊列]          M2 ─────→ 正在執行 G20             │
│  [G21, G22]                                               │
│                                                           │
│  P3 [本地隊列]          M3 ─────→ 正在執行 G30             │
│  [空]  ← 會去偷其他 P 的工作                               │
│                                                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  閒置 M 池: [M4, M5, M6, ...]                             │
│  (待命的線程，需要時可以快速喚醒)                           │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## 八、關鍵數據對比

| 項目 | G | M | P |
|------|---|---|---|
| **數量** | 成千上萬個 | 通常 ≈ P 的數量<br>最多 10000 | = CPU 核心數 |
| **記憶體** | 2KB 起始 | 8MB | 很小 |
| **創建成本** | 極低（納秒） | 較高（毫秒） | 啟動時創建 |
| **誰創建** | 程序員 (`go`) | Go runtime | Go runtime |
| **誰調度** | Go scheduler | OS scheduler | - |

---

## 九、G、M、P 詳細解釋

### G（Goroutine）- 訂單

**定義：**
- 你用 `go` 關鍵字創建的每個任務
- Go 程序的最小執行單位

**特性：**
- 非常輕量：初始堆疊只有 **2KB**（可動態增長到 1GB）
- 可以有數十萬個同時存在
- 包含：函數代碼、堆疊、程序計數器、狀態等

**生命週期：**
```
創建 → 等待運行 → 正在運行 → 阻塞 → 等待運行 → 完成
```

**程式碼範例：**
```go
// 每個 go 關鍵字都創建一個 G
go func() {
    fmt.Println("這是 G1")
}()

go func() {
    fmt.Println("這是 G2")
}()

// 現在有 3 個 G：main goroutine + G1 + G2
```

---

### M（Machine/OS Thread）- 廚師

**定義：**
- 真正的作業系統線程（pthread、Windows thread）
- 是實際執行代碼的載體

**特性：**
- 比較重量：每個線程約 **8MB** 堆疊
- 數量有限：Go 預設最多 **10000** 個 M
- 由 Go runtime 動態創建和銷毀

**工作流程：**
```
1. M 綁定一個 P
2. 從 P 的本地隊列取出 G
3. 執行 G 的代碼
4. G 完成後，繼續取下一個 G
```

**特殊情況：**
- 當 G 發起系統調用時，M 會和 G 一起阻塞
- P 會解綁這個 M，去找新的 M 繼續工作
- 阻塞結束後，M 嘗試重新獲取 P

---

### P（Processor）- 工作檯

**定義：**
- 邏輯處理器，是 G 和 M 之間的橋樑
- 持有 G 的本地運行隊列

**特性：**
- 數量 = `GOMAXPROCS` = CPU 核心數（預設）
- 每個 P 有自己的本地隊列（最多 256 個 G）
- P 必須綁定 M 才能執行 G

**核心作用：**
1. 維護本地 G 隊列
2. 管理記憶體分配（mcache）
3. 調度 G 的執行

**調整 P 的數量：**
```go
runtime.GOMAXPROCS(8)  // 設置為 8 個 P
```

---

## 十、實用調試技巧

```go
package main

import (
    "fmt"
    "runtime"
    "time"
)

func main() {
    // 查看調度信息
    fmt.Println("=== 初始狀態 ===")
    printStats()
    
    // 創建大量 goroutine
    for i := 0; i < 100; i++ {
        go func() {
            time.Sleep(10 * time.Second)
        }()
    }
    
    time.Sleep(1 * time.Second)
    
    fmt.Println("\n=== 創建 100 個 G 後 ===")
    printStats()
}

func printStats() {
    fmt.Printf("CPU 核心數: %d\n", runtime.NumCPU())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    fmt.Printf("當前 Goroutine 數: %d\n", runtime.NumGoroutine())
    
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    fmt.Printf("Goroutine 堆疊記憶體: %d KB\n", m.StackInuse/1024)
}
```

**進階調試：**
```bash
# 使用 GODEBUG 查看調度器信息
GODEBUG=schedtrace=1000 go run main.go

# 輸出解釋：
# SCHED 1000ms: gomaxprocs=8 idleprocs=0 threads=10 ...
# gomaxprocs: P 的數量
# idleprocs: 空閒的 P 數量
# threads: M 的數量
```

---

## 十一、常見問題 FAQ

### Q1: 為什麼需要 P？直接 G 和 M 不行嗎？

**答：** P 的存在是為了更好的調度效率：
- P 維護本地隊列，減少全局隊列的鎖競爭
- P 實現 work stealing，自動負載均衡
- P 管理記憶體分配，減少記憶體競爭

### Q2: M 的數量會無限增長嗎？

**答：** 不會
- Go 限制最多 10000 個 M（可調整）
- 閒置的 M 會被放入池中複用
- 長時間不用的 M 會被銷毀

### Q3: 什麼時候會創建新的 M？

**答：** 
1. 所有 M 都在執行 G，且有 G 在等待
2. M 被系統調用阻塞，P 需要新的 M
3. 手動調用 `runtime.LockOSThread()`

### Q4: Goroutine 的堆疊如何增長？

**答：**
- 初始 2KB
- 動態增長：2KB → 4KB → 8KB → ...
- 最大可達 1GB
- 使用分段堆疊（segmented stacks）或連續堆疊（contiguous stacks）

### Q5: 如何避免 Goroutine 洩漏？

**答：**
```go
// ❌ 錯誤：goroutine 永遠阻塞
func bad() {
    ch := make(chan int)
    go func() {
        ch <- 1  // 沒有接收者，永遠阻塞
    }()
}

// ✅ 正確：使用 context 或 buffered channel
func good(ctx context.Context) {
    ch := make(chan int, 1)  // buffered
    go func() {
        select {
        case ch <- 1:
        case <-ctx.Done():
            return
        }
    }()
}
```

---

## 十二、性能優化建議

### 1. 合理設置 GOMAXPROCS

```go
// 對於 CPU 密集型任務
runtime.GOMAXPROCS(runtime.NumCPU())  // 使用所有核心

// 對於 I/O 密集型任務
runtime.GOMAXPROCS(runtime.NumCPU() * 2)  // 可以超配

// 容器環境注意
// Docker 限制了 CPU，但 runtime.NumCPU() 可能返回宿主機核心數
// 建議手動設置
```

### 2. 避免大量短生命週期 Goroutine

```go
// ❌ 不好：創建過多 goroutine
for i := 0; i < 1000000; i++ {
    go process(i)
}

// ✅ 更好：使用 worker pool
func workerPool(jobs <-chan int, workers int) {
    var wg sync.WaitGroup
    for w := 0; w < workers; w++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for job := range jobs {
                process(job)
            }
        }()
    }
    wg.Wait()
}
```

### 3. 注意 Goroutine 的通信成本

```go
// 如果 goroutine 之間頻繁通信
// 可能不如單線程處理快

// 經驗法則：
// - CPU 密集型：goroutine 數量 ≈ CPU 核心數
// - I/O 密集型：可以創建大量 goroutine
```

---

## 十三、與其他語言對比

| 特性 | Go Goroutine | Python async/await | Java Thread |
|------|--------------|-------------------|-------------|
| 並發模型 | CSP (Communicating Sequential Processes) | 協程 (Coroutine) | 線程 (Thread) |
| 調度 | Go runtime (M:N) | 事件循環 (Event Loop) | OS 調度 |
| 堆疊大小 | 2KB 起始 | ~1KB | 1MB+ |
| 創建成本 | 極低 | 低 | 高 |
| 並行 | ✅ 真並行 | ❌ 單線程並發 | ✅ 真並行 |
| 語法 | `go func()` | `async/await` | `new Thread()` |
| 通信方式 | Channel | Queue/asyncio | 共享記憶體 |

---

## 十四、總結口訣

```
G 是任務輕如羽，成千上萬不是夢
M 是線程真幹活，數量有限要珍惜
P 是檯子分核心，工作隊列藏其中

G 排隊等 M 做，M 綁定 P 才能活
遇到阻塞不要慌，換個 M 繼續幹
隊列空了去偷工，負載均衡自動成

記住三點不會錯：
1. P 數量等於核心數
2. M 會根據需要增減
3. G 想執行必須通過 P
```

---

## 十五、學習資源

### 官方文檔
- [Go 並發模型](https://go.dev/blog/concurrency-is-not-parallelism)
- [Effective Go - Concurrency](https://go.dev/doc/effective_go#concurrency)

### 深入閱讀
- [Go scheduler 源碼](https://github.com/golang/go/blob/master/src/runtime/proc.go)
- [Scalable Go Scheduler Design](https://docs.google.com/document/d/1TTj4T2JO42uD5ID9e89oa0sLKhJYD0Y_kqxDv3I3XMw)

### 實用工具
```bash
# 查看 goroutine 堆疊
curl http://localhost:6060/debug/pprof/goroutine?debug=1

# 性能分析
go tool pprof http://localhost:6060/debug/pprof/profile
```

---

## 附錄：完整示例程序

```go
package main

import (
    "fmt"
    "runtime"
    "sync"
    "time"
)

func main() {
    fmt.Println("=== Go GMP 調度模型示例 ===\n")
    
    // 設置使用 4 個核心
    runtime.GOMAXPROCS(4)
    fmt.Printf("使用 %d 個 CPU 核心\n\n", runtime.GOMAXPROCS(0))
    
    // 示例 1: 基本並發
    fmt.Println("--- 示例 1: 基本並發 ---")
    basicConcurrency()
    
    // 示例 2: I/O 阻塞
    fmt.Println("\n--- 示例 2: I/O 阻塞處理 ---")
    ioBlocking()
    
    // 示例 3: Work Stealing
    fmt.Println("\n--- 示例 3: Work Stealing ---")
    workStealing()
    
    // 顯示最終統計
    fmt.Println("\n--- 最終統計 ---")
    printStats()
}

func basicConcurrency() {
    var wg sync.WaitGroup
    
    for i := 0; i < 8; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("G%d 開始\n", id)
            compute()
            fmt.Printf("G%d 完成\n", id)
        }(i)
    }
    
    wg.Wait()
}

func ioBlocking() {
    var wg sync.WaitGroup
    
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            fmt.Printf("G%d 開始 I/O\n", id)
            time.Sleep(100 * time.Millisecond)
            fmt.Printf("G%d I/O 完成\n", id)
        }(i)
    }
    
    wg.Wait()
}

func workStealing() {
    var wg sync.WaitGroup
    
    // 創建不均衡的任務
    for i := 0; i < 4; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            if id == 0 {
                // P0 分配到重任務
                time.Sleep(500 * time.Millisecond)
            } else {
                // 其他 P 快速完成
                time.Sleep(50 * time.Millisecond)
            }
            fmt.Printf("G%d 完成\n", id)
        }(i)
    }
    
    wg.Wait()
}

func compute() {
    sum := 0
    for i := 0; i < 10000000; i++ {
        sum += i
    }
}

func printStats() {
    fmt.Printf("CPU 核心數: %d\n", runtime.NumCPU())
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(0))
    fmt.Printf("當前 Goroutine 數: %d\n", runtime.NumGoroutine())
    
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    fmt.Printf("堆疊記憶體: %d KB\n", m.StackInuse/1024)
    fmt.Printf("堆記憶體: %d MB\n", m.Alloc/1024/1024)
}
```

---

**文件創建日期：** 2024-12-08  
**作者：** Claude  
**版本：** 1.0

如有問題或建議，歡迎交流！
