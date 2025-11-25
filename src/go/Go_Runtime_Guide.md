# Go Runtime 完整指南

## 什麼是 Go Runtime？

Go Runtime 是 Go 語言的執行時系統，負責在操作系統和用戶代碼之間進行交互。它是一個內嵌在每個 Go 程序中的系統層，提供語言運行所需的基礎設施。

## Runtime 的核心組件

### 1. 調度器（Scheduler）

**目的**：管理 goroutine 的執行，實現並發編程模型。

**三層模型（G-M-P）**：
- **G（Goroutine）**：輕量級線程，用戶創建的並發任務
- **M（Machine）**：映射到操作系統線程，執行實際代碼
- **P（Processor）**：邏輯處理器，每個 P 管理一個本地 goroutine 隊列

**調度策略**：
- Work-stealing 算法：空閒的 P 會從其他 P 的隊列中竊取任務
- 協作式調度：goroutine 在系統調用、IO 操作或明確讓出時觸發調度
- 搶佔式調度（1.14+）：定期檢查點強制調度

```
┌─────────────────────────────────────────────┐
│              Go 程序                         │
├─────────────────────────────────────────────┤
│  Go Code                                    │
│  ├─ go func1() ──┐                          │
│  ├─ go func2() ──┼─→ G (Goroutines)        │
│  └─ go func3() ──┘                          │
├─────────────────────────────────────────────┤
│  Scheduler                                  │
│  ├─ P0 [G1, G2, G3, ...]                   │
│  ├─ P1 [G4, G5, ...]                       │
│  └─ P2 [...]                               │
├─────────────────────────────────────────────┤
│  OS Threads (M)                             │
│  ├─ M0 ─→ 執行 P0 的 goroutine             │
│  ├─ M1 ─→ 執行 P1 的 goroutine             │
│  └─ M2 ─→ 執行 P2 的 goroutine             │
├─────────────────────────────────────────────┤
│  操作系統                                    │
└─────────────────────────────────────────────┘
```

### 2. 垃圾回收器（Garbage Collector）

**目的**：自動管理內存，回收不再使用的對象。

**特性**：
- 並發 GC：與用戶代碼並行運行，減少 STW（Stop The World）時間
- 三色標記法：黑、灰、白三種顏色追蹤對象狀態
- 寫屏障：記錄堆上對象的修改

**GC 階段**：
1. Mark Setup - 啟用寫屏障
2. Marking - 並發標記活對象
3. Mark Termination - 完成標記（需要 STW）
4. Sweep - 並發清掃死對象

### 3. 內存管理

**堆（Heap）**：
- 用於分配動態內存
- 由 GC 管理

**棧（Stack）**：
- 每個 goroutine 有自己的棧
- 棧空間自動增長（segmented stack）

**內存分配器**：
- 基於 TCMalloc 設計
- 多層級結構：小對象、中對象、大對象的不同分配策略

### 4. 系統調用和 IO 操作

**網絡 IO**：
- 使用非阻塞 socket 和 epoll/kqueue/IOCP
- Runtime 監控 IO 事件，自動喚醒相關 goroutine

**文件 IO**：
- 包裝操作系統的文件 API
- 支持異步操作

**特殊處理**：
- 當 M 執行阻塞系統調用時，會自動分配新 M 給 P
- 系統調用完成後，goroutine 回到隊列

### 5. Channel 和同步原語

**Channel**：
- 內置的消息傳遞機制
- 實現 goroutine 間的通信和同步

**同步原語**：
- Mutex
- RWMutex
- Cond
- WaitGroup
- Semaphore

### 6. Panic 和 Recover

**運行時異常處理**：
- nil 指針解引用檢查
- 數組邊界檢查
- 類型斷言檢查
- panic/recover 機制

## Runtime 的生命周期

### 程序啟動

```
1. 操作系統加載可執行檔案
2. 執行引導代碼（bootstrap code）
3. 初始化 runtime
   - 初始化全局變量
   - 啟動 GC 工作線程
   - 初始化調度器
4. 執行 init() 函數
5. 執行 main() 函數
```

### 程序運行

```
Runtime 在後台運行：
├─ Scheduler：調度 goroutine 執行
├─ GC：定期掃描堆內存
├─ Signal handler：處理操作系統信號
└─ Timer：管理 time.Timer 和 time.Ticker
```

### 程序退出

```
1. main() 函數返回
2. defer 語句執行（逆序）
3. goroutine 逐個終止
4. GC 最後一次運行
5. 釋放所有資源
6. 進程退出
```

## 關鍵數據結構

### G（Goroutine）結構體

```go
type g struct {
    stack       stack           // goroutine 的棧空間
    stackguard0 uintptr         // 棧溢出檢查
    m           *m              // 關聯的 M
    goid        uint64          // goroutine ID
    waiting     *sudog          // 阻塞在 channel 或 lock 上
    waitreason  waitReason      // 等待原因
    status      uint32          // goroutine 狀態
    // ... 更多字段
}
```

**Goroutine 狀態**：
- Gidle：未使用
- Grunnable：等待運行
- Grunning：正在運行
- Gsyscall：執行系統調用
- Gwaiting：阻塞（IO、channel、lock）
- Gdead：已終止

### M（Machine）結構體

```go
type m struct {
    p           puintptr        // 關聯的 P
    curg        *g              // 當前執行的 G
    id          int64
    procid      uint64          // 操作系統線程 ID
    // ... 更多字段
}
```

### P（Processor）結構體

```go
type p struct {
    id          int32
    runq        [256]guintptr   // 本地隊列
    runnext     guintptr        // 下一個要運行的 G
    // ... 更多字段
}
```

## 重要的 Runtime 函數

### 調度相關

```go
runtime.Gosched()           // 讓出 CPU，允許其他 goroutine 運行
runtime.NumGoroutine()      // 獲取當前 goroutine 數量
runtime.GOMAXPROCS(n)       // 設置最大 P 數量
runtime.LockOSThread()      // 將當前 goroutine 綁定到 OS 線程
runtime.UnlockOSThread()    // 解除綁定
```

### GC 相關

```go
runtime.GC()                // 手動觸發垃圾回收
runtime.ReadMemStats(m)     // 讀取內存統計信息
runtime.SetGCPercent(p)     // 設置 GC 觸發阈值
```

### Debug 和分析

```go
runtime.Stack(buf, all)     // 獲取棧信息
runtime.Caller(skip)        // 獲取調用者信息
runtime.SetMutexProfileFraction(r)  // 設置 mutex 分析
```

## 性能優化技巧

### 1. 調整 GOMAXPROCS

```go
import "runtime"

// 充分利用多核
runtime.GOMAXPROCS(runtime.NumCPU())
```

### 2. 減少 GC 壓力

```go
// 複用對象，減少分配
var buffer bytes.Buffer
buffer.WriteString("hello")
buffer.Reset()  // 復用 buffer

// 使用對象池
var pool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 0, 1024)
    },
}
```

### 3. 避免頻繁的系統調用

```go
// 不好：每次都調用系統調用
for i := 0; i < 1000; i++ {
    syscall.Write(fd, data)
}

// 好：批量操作
syscall.Write(fd, largeData)
```

### 4. 合理使用 goroutine

```go
// 不好：創建過多 goroutine
for i := 0; i < 1000000; i++ {
    go doSomething()
}

// 好：使用 worker pool
const numWorkers = 100
for i := 0; i < numWorkers; i++ {
    go worker(jobChan)
}
```

## Runtime 的來源和形式

在源碼層面，**Go Runtime 是用 Go 和 C 混寫的代碼**，存在 Go 標準庫的 `runtime` 包中。當你編譯 Go 程序時，Runtime 會被**靜態連結進去**，最終成為可執行檔案的一部分。

**Runtime 不是一個獨立的執行檔案**，而是代碼和數據結構的集合，包括：
- 調度器（Scheduler）
- 垃圾回收器（GC）
- 內存管理器
- goroutine 管理
- Channel 實現
- 同步原語實現
- 異常處理

## Runtime 和編譯器的關係

### 編譯器的職責

- 將 Go 源碼編譯成機器碼
- 識別 `go` 語句，生成對 `runtime.newproc` 的調用
- 插入棧溢出檢查代碼
- 插入邊界檢查代碼

### Runtime 的職責

- 執行調度算法
- 管理內存和垃圾回收
- 處理並發原語（channel、mutex）
- 處理異常和恢復

## 編譯和連結的完整流程

### 三個關鍵階段

```
Go 源碼文件                    Runtime 源碼
    │                            │
    │  (runtime 包在標準庫中)     │
    │                            │
    └────────────┬───────────────┘
                 │
            ┌────▼──────────────────┐
            │   編譯器 (go build)    │
            │  - 編譯用戶代碼         │
            │  - 編譯 runtime 代碼    │
            │  - 生成目標文件         │
            └────┬──────────────────┘
                 │
            ┌────▼────────────────────────┐
            │   目標文件 (.o)             │
            │  - 用戶代碼的機器碼          │
            │  - Runtime 的機器碼          │
            │  - 標準庫的機器碼            │
            └────┬─────────────────────────┘
                 │
            ┌────▼──────────────────┐
            │   Linker（連結器）    │
            │  - 連結所有目標文件    │
            │  - 連結 runtime       │
            │  - 解析符號引用        │
            │  - 生成最終可執行檔案  │
            └────┬──────────────────┘
                 │
       ┌─────────▼──────────────────────────┐
       │   可執行檔案（自包含）              │
       │  ┌──────────────────────────────┐ │
       │  │ 用戶代碼的機器碼              │ │
       │  ├──────────────────────────────┤ │
       │  │ Go Runtime 的機器碼           │ │
       │  │ - Scheduler                   │ │
       │  │ - GC                          │ │
       │  │ - Memory Manager              │ │
       │  │ - goroutine 管理              │ │
       │  │ - Channel 實現                │ │
       │  ├──────────────────────────────┤ │
       │  │ 標準庫的機器碼                │ │
       │  │ (fmt, io, sync 等)            │ │
       │  ├──────────────────────────────┤ │
       │  │ 其他必要資源                  │ │
       │  └──────────────────────────────┘ │
       └────────────────────────────────────┘
```

### 階段 1：編譯（go build）

**輸入**：Go 源碼文件 + Runtime 源碼

**處理**：
- 編譯器分別編譯用戶代碼和 runtime 代碼
- 每個 Go 文件（`.go`）都被編譯成目標文件（`.o`）
- Runtime 中的 C 代碼也被編譯成機器碼

**輸出**：多個目標文件，包含編譯後的機器碼

```bash
$ go build myprogram.go

# 在編譯過程中，編譯器會：
# 1. 編譯 myprogram.go → myprogram.o
# 2. 編譯 runtime/*.go → runtime_*.o
# 3. 編譯 runtime/*.c → runtime_*.o
# 4. 編譯標準庫 → stdlib_*.o
```

### 階段 2：連結（Linker）

**輸入**：所有目標文件和庫文件

**處理**：
- 將所有 `.o` 文件中的代碼和數據合併
- 解析符號引用（Symbol Resolution）
- 重定位地址（Relocation）
- 創建可執行檔案頭部

**輸出**：單個可執行檔案

### 階段 3：結果 - 自包含的可執行檔案

最終生成的可執行檔案包含：

1. **用戶代碼** - 你寫的所有函數和邏輯
2. **Go Runtime** - 核心部分，包括：
   - Scheduler（調度器）
   - GC（垃圾回收器）
   - Memory Manager（內存管理）
   - goroutine 管理機制
   - Channel 實現
3. **標準庫** - fmt、io、sync 等所有依賴的包
4. **元數據和資源** - 符號表、重定位信息等

### 為什麼是靜態連結？

Go 選擇靜態連結而不是動態連結的原因：

1. **跨平台部署**：生成的二進制可以直接在目標系統運行，不需要安裝依賴
2. **性能**：避免動態連結的開銷，啟動更快
3. **簡化分發**：只需分發一個檔案，使用者無需配置環境
4. **版本穩定性**：不會因為系統庫版本不同而導致問題

### 驗證靜態連結

你可以用以下命令查看編譯結果：

```bash
# 檢查檔案類型和依賴
$ file ./myprogram
./myprogram: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux), 
statically linked, Go BuildID=...

# 查看動態依賴（如果有的話）
$ ldd ./myprogram
    not a dynamic executable

# 查看檔案大小（包含 runtime）
$ ls -lh ./myprogram
-rwxr-xr-x 1 user group 5.2M Nov 26 12:34 myprogram

# 檢查編譯時包含的 runtime 信息
$ strings ./myprogram | grep "runtime\." | head -20
```

### Runtime 在編譯過程中的集成

```
┌────────────────────────────────────────────┐
│      編譯器看到的 Go 代碼                    │
├────────────────────────────────────────────┤
│                                            │
│  package main                              │
│                                            │
│  func main() {                             │
│      go doWork()  ◄── 識別 go 語句         │
│      time.Sleep(1 * time.Second)           │
│  }                                         │
│                                            │
│  func doWork() { ... }                     │
│                                            │
└────────────────────────────────────────────┘
                    │
                    │ 編譯器處理
                    │
                    ▼
┌────────────────────────────────────────────┐
│         生成的機器碼（偽代碼）              │
├────────────────────────────────────────────┤
│                                            │
│  main:                                     │
│      ... 初始化代碼 ...                    │
│      call runtime.newproc  ◄── 創建 G    │
│      ... sleep 代碼 ...                    │
│                                            │
│  doWork:                                   │
│      ... 函數體 ...                        │
│                                            │
│  runtime.newproc:       ◄── Runtime 代碼  │
│      ... scheduler 代碼 ...                │
│      ... 管理 goroutine ...                │
│                                            │
└────────────────────────────────────────────┘
```

### 實際編譯例子

```go
// main.go
package main

import "fmt"

func main() {
    go func() {
        fmt.Println("Hello from goroutine")
    }()
    
    fmt.Println("Hello from main")
}
```

編譯時會發生：

```bash
$ go build main.go

1. 編譯階段（go build）：
   - 編譯 main.go：
     * 編譯 main() 函數
     * 識別 go func(){...}，生成 runtime.newproc 調用
   
   - 編譯 fmt 包：
     * 編譯所有 fmt 函數
   
   - 編譯 runtime：
     * 編譯 scheduler（newproc、schedule 等）
     * 編譯 GC
     * 編譯 memory allocator
     * 編譯所有 runtime 包的代碼
   
   輸出：多個 .o 目標文件

2. 連結階段（Linker）：
   - 合併所有 .o 目標文件
   - 解析符號引用：
     * fmt.Println → fmt 包中的實現
     * newproc → runtime.newproc 的實現
   - 重定位地址
   - 生成可執行檔案
   
   輸出：main（可執行檔案，約 3-6 MB）
```

## 查看 Runtime 信息

```go
package main

import (
    "fmt"
    "runtime"
)

func main() {
    // 獲取運行時信息
    var m runtime.MemStats
    runtime.ReadMemStats(&m)
    
    fmt.Printf("Goroutines: %d\n", runtime.NumGoroutine())
    fmt.Printf("Memory Alloc: %v MB\n", m.Alloc/1024/1024)
    fmt.Printf("GC Runs: %d\n", m.NumGC)
    fmt.Printf("GOMAXPROCS: %d\n", runtime.GOMAXPROCS(-1))
}
```

## 總結

| 組件 | 作用 |
|------|------|
| Scheduler | 管理 goroutine 的執行和切換 |
| GC | 自動回收不使用的內存 |
| Memory Manager | 分配和管理內存 |
| Networking | 支持高效的網絡 IO |
| Synchronization | 提供 channel、mutex 等同步原語 |

Go Runtime 的設計使得開發者可以輕鬆編寫高效的並發程序，而不需要手動管理線程和內存。

---

# Go Runtime 原始碼檔案結構

## 原始碼路徑
```
/home/shihyu/go/src/runtime/
```

本目錄包含約 507 個 Go 原始碼檔案，以及多個子目錄。以下是核心關鍵檔案的分類介紹。

---

## 一、核心結構與型別定義

### 1. runtime2.go (核心資料結構)
- **路徑**: `/home/shihyu/go/src/runtime/runtime2.go`
- **說明**: 定義 runtime 最核心的資料結構
- **包含內容**:
  - `g` (goroutine) 結構體定義
  - `m` (machine/OS thread) 結構體定義
  - `p` (processor) 結構體定義
  - goroutine 狀態常數 (_Gidle, _Grunnable, _Grunning, _Gsyscall 等)
  - 各種核心型別和常數定義

### 2. type.go
- **路徑**: `/home/shihyu/go/src/runtime/type.go`
- **說明**: 型別系統的 runtime 表示

---

## 二、排程器 (Scheduler)

### 3. proc.go (核心排程邏輯)
- **路徑**: `/home/shihyu/go/src/runtime/proc.go`
- **說明**: goroutine 排程器的核心實作
- **關鍵功能**:
  - goroutine 的建立、執行、停止
  - M-P-G 排程模型實作
  - Work-stealing 演算法
  - 系統呼叫的處理
  - 執行緒停放與喚醒機制
- **設計文件**: https://golang.org/s/go11sched

### 4. runtime1.go
- **路徑**: `/home/shihyu/go/src/runtime/runtime1.go`
- **說明**: runtime 初始化相關功能

---

## 三、記憶體管理 (Memory Management)

### 5. malloc.go (記憶體分配器)
- **路徑**: `/home/shihyu/go/src/runtime/malloc.go`
- **說明**: 記憶體分配的主要邏輯
- **關鍵功能**:
  - 物件記憶體分配 (small/large objects)
  - span 管理
  - size class 定義

### 6. mheap.go (堆記憶體管理)
- **路徑**: `/home/shihyu/go/src/runtime/mheap.go`
- **說明**: 堆記憶體的管理
- **關鍵功能**:
  - mheap 結構體與操作
  - span 的分配與回收
  - 記憶體頁管理

### 7. mcache.go (執行緒快取)
- **路徑**: `/home/shihyu/go/src/runtime/mcache.go`
- **說明**: 每個 P 的本地記憶體快取
- **關鍵功能**:
  - 小物件快速分配
  - 減少鎖競爭

### 8. mcentral.go (中央快取)
- **路徑**: `/home/shihyu/go/src/runtime/mcentral.go`
- **說明**: 中央 span 快取，連接 mcache 和 mheap

### 9. mprof.go (記憶體 profiling)
- **路徑**: `/home/shihyu/go/src/runtime/mprof.go`
- **說明**: 記憶體分配追蹤與 profiling

### 10. msize.go
- **路徑**: `/home/shihyu/go/src/runtime/msize.go`
- **說明**: 記憶體 size class 計算

### 11. mstats.go
- **路徑**: `/home/shihyu/go/src/runtime/mstats.go`
- **說明**: 記憶體統計資訊

### 12. mmap*.go
- **路徑**: `/home/shihyu/go/src/runtime/mmap*.go`
- **說明**: 不同平台的記憶體映射實作

---

## 四、垃圾回收 (Garbage Collection)

### 13. mgc.go (垃圾回收主邏輯)
- **路徑**: `/home/shihyu/go/src/runtime/mgc.go`
- **說明**: GC 的核心實作
- **關鍵功能**:
  - 並行標記清除 (concurrent mark-sweep)
  - GC 觸發條件
  - STW (stop-the-world) 控制
  - Write barrier

### 14. mgcmark.go (標記階段)
- **路徑**: `/home/shihyu/go/src/runtime/mgcmark.go`
- **說明**: GC 標記階段實作
- **關鍵功能**:
  - 物件掃描與標記
  - Work buffer 管理
  - 協助標記 (assist marking)

### 15. mgcsweep.go (清除階段)
- **路徑**: `/home/shihyu/go/src/runtime/mgcsweep.go`
- **說明**: GC 清除階段實作

### 16. mgcscavenge.go (記憶體歸還)
- **路徑**: `/home/shihyu/go/src/runtime/mgcscavenge.go`
- **說明**: 將未使用記憶體歸還給作業系統

### 17. mgcstack.go (堆疊掃描)
- **路徑**: `/home/shihyu/go/src/runtime/mgcstack.go`
- **說明**: GC 掃描 goroutine 堆疊

### 18. mgcwork.go (GC 工作佇列)
- **路徑**: `/home/shihyu/go/src/runtime/mgcwork.go`
- **說明**: GC 工作佇列管理

### 19. mbarrier.go (Write Barrier)
- **路徑**: `/home/shihyu/go/src/runtime/mbarrier.go`
- **說明**: Write barrier 實作

### 20. mbitmap.go (記憶體 bitmap)
- **路徑**: `/home/shihyu/go/src/runtime/mbitmap.go`
- **說明**: 記憶體標記 bitmap，用於追蹤指標

---

## 五、並發原語 (Concurrency Primitives)

### 21. chan.go (Channel)
- **路徑**: `/home/shihyu/go/src/runtime/chan.go`
- **說明**: channel 的實作
- **關鍵功能**:
  - send/receive 操作
  - 緩衝管理
  - goroutine 阻塞與喚醒

### 22. select.go (Select)
- **路徑**: `/home/shihyu/go/src/runtime/select.go`
- **說明**: select 語句的實作

### 23. sema.go (Semaphore)
- **路徑**: `/home/shihyu/go/src/runtime/sema.go`
- **說明**: semaphore 與 sync 原語的底層實作

### 24. lock*.go (鎖機制)
- **路徑**: `/home/shihyu/go/src/runtime/lock_*.go`
- **說明**: mutex 等鎖機制的實作

### 25. rwmutex.go
- **路徑**: `/home/shihyu/go/src/runtime/rwmutex.go`
- **說明**: 讀寫鎖

---

## 六、堆疊管理 (Stack Management)

### 26. stack.go (堆疊管理)
- **路徑**: `/home/shihyu/go/src/runtime/stack.go`
- **說明**: goroutine 堆疊管理
- **關鍵功能**:
  - 堆疊分配與釋放
  - 堆疊增長 (stack growth)
  - 堆疊收縮 (stack shrinking)
  - 堆疊複製

---

## 七、錯誤處理 (Error Handling)

### 27. panic.go (Panic/Recover)
- **路徑**: `/home/shihyu/go/src/runtime/panic.go`
- **說明**: panic 與 recover 機制
- **關鍵功能**:
  - panic 處理流程
  - defer 執行
  - recover 機制

### 28. error.go
- **路徑**: `/home/shihyu/go/src/runtime/error.go`
- **說明**: runtime error 型別

---

## 八、訊號處理 (Signal Handling)

### 29. signal_unix.go
- **路徑**: `/home/shihyu/go/src/runtime/signal_unix.go`
- **說明**: Unix/Linux 訊號處理

### 30. os_*.go
- **路徑**: `/home/shihyu/go/src/runtime/os_*.go`
- **說明**: 不同作業系統的底層介面

### 31. sys_*.go
- **路徑**: `/home/shihyu/go/src/runtime/sys_*.go`
- **說明**: 系統呼叫相關

---

## 九、組合語言實作 (Assembly)

### 32. asm_*.s
- **路徑**: `/home/shihyu/go/src/runtime/asm_*.s`
- **平台**:
  - `asm_amd64.s` - x86-64 架構
  - `asm_arm64.s` - ARM64 架構
  - `asm_386.s` - x86 架構
  - 等各平台組語實作
- **說明**: runtime 核心功能的組語實作
- **包含**:
  - context switch
  - 系統呼叫
  - goroutine 啟動
  - 堆疊操作

---

## 十、介面與反射 (Interface & Reflection)

### 33. iface.go (介面)
- **路徑**: `/home/shihyu/go/src/runtime/iface.go`
- **說明**: interface 的 runtime 實作
- **關鍵功能**:
  - interface value 表示
  - 型別斷言 (type assertion)
  - 型別轉換

### 34. alg.go (演算法)
- **路徑**: `/home/shihyu/go/src/runtime/alg.go`
- **說明**: 雜湊、比較等演算法

---

## 十一、除錯與追蹤 (Debugging & Tracing)

### 35. debug.go
- **路徑**: `/home/shihyu/go/src/runtime/debug.go`
- **說明**: runtime 除錯支援

### 36. debuglog.go
- **路徑**: `/home/shihyu/go/src/runtime/debuglog.go`
- **說明**: runtime 內部日誌

### 37. trace.go
- **路徑**: `/home/shihyu/go/src/runtime/trace.go`
- **說明**: 執行追蹤 (execution tracing)

### 38. traceback.go
- **路徑**: `/home/shihyu/go/src/runtime/traceback.go`
- **說明**: 堆疊回溯 (stack traceback)

---

## 十二、效能分析 (Profiling)

### 39. cpuprof.go
- **路徑**: `/home/shihyu/go/src/runtime/cpuprof.go`
- **說明**: CPU profiling

### 40. profbuf.go
- **路徑**: `/home/shihyu/go/src/runtime/profbuf.go`
- **說明**: Profiling buffer 管理

---

## 十三、CGO 支援

### 41. cgocall.go
- **路徑**: `/home/shihyu/go/src/runtime/cgocall.go`
- **說明**: Go 呼叫 C 程式碼的支援

### 42. cgo*.go
- **路徑**: `/home/shihyu/go/src/runtime/cgo*.go`
- **說明**: CGO 相關支援檔案

---

## 十四、計時器與時間 (Timer & Time)

### 43. time.go
- **路徑**: `/home/shihyu/go/src/runtime/time.go`
- **說明**: 計時器管理
- **關鍵功能**:
  - timer 實作
  - ticker 實作
  - time.Sleep 支援

---

## 十五、競態檢測與記憶體檢測

### 44. race.go / race/
- **路徑**:
  - `/home/shihyu/go/src/runtime/race.go`
  - `/home/shihyu/go/src/runtime/race/`
- **說明**: 資料競態檢測器 (race detector)

### 45. msan.go / msan/
- **路徑**:
  - `/home/shihyu/go/src/runtime/msan.go`
  - `/home/shihyu/go/src/runtime/msan/`
- **說明**: Memory Sanitizer 支援

### 46. asan.go / asan/
- **路徑**:
  - `/home/shihyu/go/src/runtime/asan.go`
  - `/home/shihyu/go/src/runtime/asan/`
- **說明**: Address Sanitizer 支援

---

## 十六、重要子目錄

### 47. internal/
- **路徑**: `/home/shihyu/go/src/runtime/internal/`
- **說明**: runtime 內部套件
- **子套件**:
  - `atomic/` - 原子操作
  - `sys/` - 系統參數與常數
  - `math/` - 數學函數

### 48. pprof/
- **路徑**: `/home/shihyu/go/src/runtime/pprof/`
- **說明**: pprof profiling 工具介面

### 49. debug/
- **路徑**: `/home/shihyu/go/src/runtime/debug/`
- **說明**: runtime/debug 套件

### 50. trace/
- **路徑**: `/home/shihyu/go/src/runtime/trace/`
- **說明**: runtime/trace 套件

### 51. metrics/
- **路徑**: `/home/shihyu/go/src/runtime/metrics/`
- **說明**: runtime/metrics 套件

### 52. coverage/
- **路徑**: `/home/shihyu/go/src/runtime/coverage/`
- **說明**: 程式碼覆蓋率支援

---

## 核心檔案學習順序建議

如果要深入學習 Go runtime，建議按以下順序閱讀:

### 階段一：基礎結構
1. `runtime2.go` - 理解核心資料結構 (g, m, p)
2. `type.go` - 理解型別系統

### 階段二：排程器
3. `proc.go` - 理解 goroutine 排程
4. `runtime1.go` - runtime 初始化

### 階段三：記憶體管理
5. `malloc.go` - 記憶體分配
6. `mheap.go` - 堆記憶體
7. `mcache.go` - 執行緒快取
8. `mcentral.go` - 中央快取

### 階段四：垃圾回收
9. `mgc.go` - GC 主邏輯
10. `mgcmark.go` - 標記階段
11. `mgcsweep.go` - 清除階段
12. `mbarrier.go` - Write barrier

### 階段五：並發原語
13. `chan.go` - channel 實作
14. `select.go` - select 實作
15. `sema.go` - semaphore

### 階段六：其他重要主題
16. `stack.go` - 堆疊管理
17. `panic.go` - panic/recover
18. `iface.go` - interface
19. `signal_unix.go` - 訊號處理

### 階段七：組語深入
20. `asm_amd64.s` - 組語實作 (依你的平台選擇)

---

## 重要設計文件與資源

1. **Go Scheduler Design Doc**
   https://golang.org/s/go11sched

2. **Go Memory Allocator**
   https://golang.org/s/go-memory-allocator

3. **Go GC Design Doc**
   https://golang.org/s/go15gcpacing

4. **Go Runtime 原始碼**
   https://github.com/golang/go/tree/master/src/runtime

---

## 統計資訊

- **總 Go 檔案數**: 約 507 個
- **核心行數**: 超過 23,000 行 (僅計算關鍵檔案)
- **支援平台**: linux, darwin, windows, freebsd, openbsd, netbsd, dragonfly, solaris, aix
- **支援架構**: amd64, 386, arm, arm64, ppc64, ppc64le, mips, mips64, riscv64, s390x, wasm

---

## 備註

- 所有 `*_test.go` 檔案為測試檔案
- 平台特定檔案使用 `_<os>_<arch>.go` 命名規則
- 組語檔案使用 `.s` 副檔名
- runtime 程式碼屬於 Go 編譯器的內部實作，API 可能會改變
