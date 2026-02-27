# Go Memory Model & Happens-Before 完整整理

## 目錄

1. [Memory Model 是什麼？](#1-memory-model-是什麼)
2. [只有 Go 才有 Memory Model 嗎？](#2-只有-go-才有-memory-model-嗎)
3. [Happens-Before 是什麼？](#3-happens-before-是什麼)
4. [沒有 Happens-Before 的世界](#4-沒有-happens-before-的世界)
5. [CPU 底層示意圖](#5-cpu-底層示意圖)
6. [Happens-Before 在做什麼？](#6-happens-before-在做什麼)
7. [Go 中如何建立 Happens-Before？](#7-go-中如何建立-happens-before)
   - [7.1 Channel](#71-channel)
   - [7.2 Mutex](#72-mutex)
   - [7.3 Atomic](#73-atomic)
   - [7.4 Goroutine Start](#74-goroutine-startgo-語句)
   - [7.5 Goroutine Exit](#75-goroutine-exit結束不建立-hb)
   - [7.6 sync.Once](#76-synconce)
   - [7.7 sync.Cond](#77-synccond)
   - [7.8 sync.Map](#78-syncmap)
   - [7.9 各機制 HB 速查表](#79-各機制-hb-速查表)
8. [Happens-Before 圖模型](#8-happens-before-圖模型)
9. [Data Race 本質](#9-data-race-本質)
10. [系統層理解總整理](#10-系統層理解總整理)
11. [完整結論](#11-完整結論)

---

## 1. Memory Model 是什麼？

**Memory Model（記憶體模型）** 是一套規則，定義在多執行緒 / 多 goroutine 情況下，讀寫記憶體時「什麼是保證可見的」，什麼是不保證的。

它解決的核心問題：

| 問題 | 說明 |
|------|------|
| CPU 指令重排（Reordering） | CPU 為了優化效能，可能改變指令執行順序 |
| Store Buffer 延遲寫回 | 寫入操作先進入 buffer，未必立即對其他 core 可見 |
| Cache 尚未同步 | 多核心各有自己的 cache，寫入不會立即同步 |
| 編譯器優化重排 | 編譯器可能因優化改變程式碼執行順序 |

> 如果沒有 memory model，多執行緒程式的行為將完全不可預測。

---

## 2. 只有 Go 才有 Memory Model 嗎？

不是。幾乎所有現代語言都有 Memory Model：

| 語言 | 特性 |
|------|------|
| C/C++ | 給予極大自由，但容易產生未定義行為（UB） |
| Java | 有嚴格定義的 Java Memory Model (JMM)，happens-before 規則完整 |
| Rust | 基於 C++ 的 memory order，型別系統靜態排除 data race |
| Go | 模型相對簡單直觀，規則明確 |

Go 的核心立場：

> **有 data race = 行為未定義（Undefined Behavior）**

這意味著即使程式看起來「跑得到」，也不代表行為正確。Go race detector (`-race`) 可以在執行時期偵測。

---

## 3. Happens-Before 是什麼？

**Happens-Before** 是 Memory Model 中最核心的因果保證機制。

定義：

> 若 **A happens-before B**，則 A 的所有記憶體寫入，在 B 執行時**一定可見**。

重點澄清：

| 概念 | 說明 |
|------|------|
| ✅ 可見性（Visibility） | B 能讀到 A 所有的寫入結果 |
| ✅ 有序性（Ordering） | A 的操作邏輯上在 B 之前完成 |
| ❌ 時間先後 | 不保證 A 在時鐘時間上先於 B |
| ❌ 誰先被 OS 排程 | 不是描述 goroutine 排程順序 |

> **Happens-Before 描述的是「因果關係」，而非「時間順序」。**

---

## 4. 沒有 Happens-Before 的世界

### 問題範例

```go
var x int
var ready bool

go func() {
    x = 42
    ready = true
}()

for !ready {}
fmt.Println(x)  // 你以為一定印出 42？
```

### 為什麼可能印出 0？

**問題一：編譯器重排**

編譯器看到 `x = 42` 和 `ready = true` 之間沒有依賴關係，
可能將執行順序調換以優化效能：

```
你寫的程式碼：          編譯器可能改成：
──────────────          ────────────────
x = 42                  ready = true    ← 先設旗標
ready = true            x = 42          ← 後寫資料
```

**問題二：CPU Store Buffer 造成可見性不一致**

```
Goroutine A (Core 1)          Goroutine B (Core 2)
─────────────────────         ─────────────────────
x = 42                        for !ready {}
  ↓ 進入 store buffer              ↓ 看到 ready = true (已同步)
ready = true                  fmt.Println(x)
  ↓ 先同步到 Core 2                ↓ 讀 x，但 store buffer 還沒 flush！
                                    → 讀到舊值 x = 0
```

**結果：主 goroutine 可能看到**

```
ready == true   ← 已設定（已同步）
x    == 0       ← 還沒同步（仍在 store buffer）
```

### 根本原因

`x = 42` 和 `fmt.Println(x)` 之間**沒有任何 happens-before 關係**，
因此 Go memory model **不保證** `x` 的可見性，這段程式碼有 data race。

---

## 5. CPU 底層示意圖

### 多核心記憶體架構

```
┌──────────────────────────────────────────────────────────┐
│                        CPU                               │
│                                                          │
│  ┌─────────────────┐         ┌─────────────────┐        │
│  │     Core 1      │         │     Core 2      │        │
│  │  ┌───────────┐  │         │  ┌───────────┐  │        │
│  │  │ Registers │  │         │  │ Registers │  │        │
│  │  ├───────────┤  │         │  ├───────────┤  │        │
│  │  │  L1 Cache │  │         │  │  L1 Cache │  │        │
│  │  ├───────────┤  │         │  ├───────────┤  │        │
│  │  │Store Buf. │  │         │  │Store Buf. │  │        │
│  │  └─────┬─────┘  │         │  └─────┬─────┘  │        │
│  └────────┼────────┘         └────────┼────────┘        │
│           │                           │                  │
│           └────────────┬──────────────┘                  │
│                   ┌────┴────┐                            │
│                   │L2 Cache │                            │
│                   └────┬────┘                            │
│                   ┌────┴────┐                            │
│                   │  Main   │                            │
│                   │ Memory  │                            │
│                   └─────────┘                            │
└──────────────────────────────────────────────────────────┘
```

### 問題：未同步時的寫入流程

```
時間軸 ─────────────────────────────────────────→

Core 1 (寫入)          Store Buffer         Core 2 (讀取)
─────────────          ────────────         ─────────────
x = 42  ──────→  [x=42] (pending)
                                            read x
                                            ↓
                                            從自己的 cache 讀
                                            得到舊值 x = 0  ← 問題！

(稍後某個時間點)
flush ──────────→ Main Memory
                                            (再讀才看到 42)
```

**關鍵問題：**
- Store Buffer 的 flush 時機不確定
- Core 2 讀取時，Core 1 的寫入可能還在 buffer 中
- 沒有任何機制通知 Core 2「你的 cache 已過期」

---

## 6. Happens-Before 在做什麼？

Happens-Before 透過插入 **Memory Barrier（記憶體屏障）** 來保證一致性。

### Memory Barrier 的三個效果

```
效果一：Flush Store Buffer
  ─────────────────────────
  強制將所有 pending 寫入提交到 shared memory
  確保其他 core 能看到最新值

效果二：禁止指令重排
  ─────────────────
  屏障「之前」的操作 ─→ 不會被移到屏障「之後」
  屏障「之後」的操作 ─→ 不會被移到屏障「之前」

效果三：Cache 同步（Invalidate）
  ───────────────────────────────
  讓其他 core 的對應 cache line 失效
  下次讀取時強制從 main memory 重新載入
```

### 有 Memory Barrier 的執行流程

```
時間軸 ─────────────────────────────────────────→

Core 1 (寫入)              Core 2 (讀取)
─────────────              ─────────────
x = 42
[WRITE BARRIER]  ─────→   [READ BARRIER]
  ↓ flush buffer              ↓ invalidate cache
  ↓ 寫入 main memory          ↓ 重新從 main memory 讀
                              read x → 一定得到 42 ✓
```

> 兩側都需要屏障：**寫端** 確保寫出；**讀端** 確保讀入最新值。

---

## 7. Go 中如何建立 Happens-Before？

Go 提供以下幾種機制建立 happens-before 關係。

---

### 7.1 Channel

Channel 是 Go 並發的核心原語，體現了 Go 的設計哲學：

> **"Do not communicate by sharing memory; instead, share memory by communicating."**

#### HB 規則

```
Unbuffered channel（容量 0）：
  ch <- v（Send 完成）  happens-before  <-ch（Receive 完成）

Buffered channel（容量 C）：
  第 n 個 Send 完成  happens-before  第 n+C 個 Receive 完成
  （意思是：buffer 滿時，第 n 個 send 要等第 n-C 個 receive 先完成）

close(ch)：
  close(ch)  happens-before  任何從 closed channel 的 receive 返回
```

#### Channel 內部結構

```
┌──────────────────────────────────────────────────────────┐
│                   hchan（channel 的底層結構）             │
│                                                          │
│  ┌──────────┐   ┌──────────────────────────────────┐    │
│  │  qcount  │   │  buf（ring buffer，buffered 才有）│    │
│  │  dataqsiz│   │                                  │    │
│  │  elemsize│   │  [0][1][2][3]...[C-1]            │    │
│  │  closed  │   │   ↑                ↑             │    │
│  └──────────┘   │  sendx            recvx          │    │
│                 └──────────────────────────────────┘    │
│                                                          │
│  ┌───────────────────────┐  ┌───────────────────────┐   │
│  │  sendq（等待送出的G） │  │  recvq（等待接收的G） │   │
│  │  G5 → G3 → G1 → nil  │  │  G6 → G4 → G2 → nil  │   │
│  └───────────────────────┘  └───────────────────────┘   │
│                                                          │
│  lock（保護以上所有欄位）                                 │
└──────────────────────────────────────────────────────────┘
```

#### Unbuffered Channel 詳細行為

```
建立：ch := make(chan int)   // 容量 = 0

情況 A：接收方先到
─────────────────────────────────────────────────────
時間軸 ──────────────────────────────────────────→

Goroutine A (sender)          Goroutine B (receiver)
────────────────────          ──────────────────────
                              v := <-ch
                              ↓ 沒有 sender，B 進入 recvq
                              [B 睡眠，讓出 CPU]
x = 42
ch <- x                       [A 找到 B 在 recvq]
  ↓ 直接把值複製給 B           [B 被喚醒]
  ↓ HB 建立                   v == 42 ✓
  [A 繼續執行]                 [B 繼續執行]


情況 B：送出方先到
─────────────────────────────────────────────────────
Goroutine A (sender)          Goroutine B (receiver)
────────────────────          ──────────────────────
x = 42
ch <- x
↓ 沒有 receiver，A 進入 sendq
[A 睡眠]
                              v := <-ch
                              ↓ 找到 A 在 sendq
                              ↓ HB 建立
                              [A 被喚醒，繼續執行]
                              v == 42 ✓
```

#### Buffered Channel 詳細行為

```
建立：ch := make(chan int, 3)  // 容量 = 3

Ring Buffer 狀態示意：
  空：[ ][ ][ ]   sendx=0, recvx=0, qcount=0
  送：[1][ ][ ]   sendx=1, recvx=0, qcount=1
  送：[1][2][ ]   sendx=2, recvx=0, qcount=2
  送：[1][2][3]   sendx=0, recvx=0, qcount=3  ← buffer 滿！
  收：[ ][2][3]   sendx=0, recvx=1, qcount=2
  收：[ ][ ][3]   sendx=0, recvx=2, qcount=1

時間軸 ──────────────────────────────────────────→

Goroutine A (sender)          Goroutine B (receiver)
────────────────────          ──────────────────────
ch <- 1  // 寫入 buf，不阻塞 ✓
ch <- 2  // 寫入 buf，不阻塞 ✓
ch <- 3  // 寫入 buf，不阻塞 ✓
ch <- 4  // buf 已滿！A 進入 sendq，睡眠
                              v1 := <-ch  // 讀出 1，喚醒 A
                              v2 := <-ch  // 讀出 2
                              v3 := <-ch  // 讀出 3（A 送的 4）
                              v4 := <-ch  // 讀出 4
```

**Buffered channel 的 HB 規則說明：**

```
ch := make(chan int, 2)  // 容量 C = 2

第 1 個 Send  ─── HB ──→  第 3 個 Receive  （n=1, n+C=3）
第 2 個 Send  ─── HB ──→  第 4 個 Receive  （n=2, n+C=4）

直觀理解：
  buffer 容量 2，代表最多讓 2 個 send 不用等 receive 完成。
  從第 3 個 send 開始，必須等第 1 個 receive 完成後才能送。
  這個「等」本身建立了 HB 關係。
```

#### Channel 狀態全覽

```
操作 \ 狀態    nil channel      open channel     closed channel
─────────────  ──────────────   ──────────────   ───────────────
Send (ch <- v) 永遠阻塞         正常／阻塞        panic ❌
Receive (<-ch) 永遠阻塞         正常／阻塞        立即返回零值+false
Close (close)  panic ❌         正常 ✓            panic ❌

nil channel 的特殊用途：
  在 select 中，nil channel 的 case 永遠不會被選中，
  可以用來「動態停用」某個 case。
```

#### select 語句

```go
// select 從所有「不阻塞」的 case 中隨機選一個執行
// 如果全部阻塞，執行 default；沒有 default 則等待

select {
case v := <-ch1:       // ch1 有資料
    process(v)
case ch2 <- data:      // ch2 有空間
    // 送出成功
case <-time.After(1 * time.Second):  // 逾時
    fmt.Println("timeout")
default:               // 上面都阻塞時立即執行（非阻塞 select）
    fmt.Println("no data ready")
}
```

**select 的 HB：**

```
時間軸 ──────────────────────────────────────────→

Goroutine A              Goroutine B (select)
───────────              ───────────────────────
x = 42
ch1 <- x   ─── HB ──→   case v := <-ch1:
                             use(x)   // 保證看到 42 ✓

y = 99
ch2 <- y   ─── HB ──→   case v := <-ch2:
                             use(y)   // 保證看到 99 ✓
```

**nil channel 停用 case 技巧：**

```go
ch1 := make(chan int, 1)
ch2 := make(chan int, 1)
ch1 <- 1

// 動態停用 ch1
var active1 chan int = ch1   // 啟用
// active1 = nil            // 停用（該 case 永遠不選）

select {
case v := <-active1:
    fmt.Println("ch1:", v)
case v := <-ch2:
    fmt.Println("ch2:", v)
}
```

#### close(ch) 的 HB 示意

```
時間軸 ──────────────────────────────────────────→

Producer                  Consumer 1             Consumer 2
────────                  ──────────             ──────────
data = []int{1,2,3}
close(ch)  ─── HB ──→    v, ok := <-ch         v, ok := <-ch
                          ok == false ✓          ok == false ✓
                          // 看到 data           // 看到 data

用途：廣播關閉信號給所有正在等待的 goroutine
      close 一次，所有 receiver 都能收到
```

#### 常用 Channel Patterns

**Pattern 1：Pipeline（流水線）**

```
資料流：generator → square → print

  [1,2,3,4,5]  →  [1,4,9,16,25]  →  印出
```

```go
func generator(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        for _, n := range nums {
            out <- n
        }
        close(out)
    }()
    return out
}

func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        for n := range in {
            out <- n * n
        }
        close(out)
    }()
    return out
}

func main() {
    // 組合 pipeline
    c := generator(1, 2, 3, 4, 5)
    sq := square(c)

    for v := range sq {
        fmt.Println(v)   // 1 4 9 16 25
    }
}
```

**Pattern 2：Fan-out / Fan-in（分散 / 匯聚）**

```
                  ┌─→ Worker 1 ─┐
input ──────────→ ├─→ Worker 2 ─┼──→ output（merged）
（Fan-out）        └─→ Worker 3 ─┘    （Fan-in）
```

```go
// Fan-out：將同一個 channel 的工作分給多個 worker
func fanOut(input <-chan int, n int) []<-chan int {
    outputs := make([]<-chan int, n)
    for i := range outputs {
        outputs[i] = square(input)
    }
    return outputs
}

// Fan-in：將多個 channel 合併成一個
func fanIn(inputs ...<-chan int) <-chan int {
    merged := make(chan int)
    var wg sync.WaitGroup

    forward := func(ch <-chan int) {
        defer wg.Done()
        for v := range ch {
            merged <- v
        }
    }

    wg.Add(len(inputs))
    for _, ch := range inputs {
        go forward(ch)
    }

    go func() {
        wg.Wait()
        close(merged)
    }()

    return merged
}
```

**Pattern 3：Done Channel（取消信號）**

```
時間軸 ──────────────────────────────────────────→

主 Goroutine              Worker
────────────              ──────
done := make(chan struct{})
go worker(done, ...)
                          for {
                              select {
                              case <-done:
                                  return   // 收到取消，結束
                              case v := <-work:
                                  process(v)
                              }
                          }
close(done)  ─ HB ──→    所有 <-done 立即返回 ✓
```

```go
func worker(done <-chan struct{}, jobs <-chan int) {
    for {
        select {
        case <-done:
            fmt.Println("worker stopped")
            return
        case j, ok := <-jobs:
            if !ok {
                return
            }
            fmt.Println("processing", j)
        }
    }
}

func main() {
    done := make(chan struct{})
    jobs := make(chan int, 10)

    go worker(done, jobs)

    for i := 0; i < 5; i++ {
        jobs <- i
    }

    close(done)   // 廣播取消信號（比 context 更輕量，適合簡單場景）
}
```

**Pattern 4：Semaphore（信號量，限制並發數）**

```
sem := make(chan struct{}, N)   // 最多允許 N 個 goroutine 同時執行

for each task:
    sem <- struct{}{}   // 佔用一個槽位（滿了就等）
    go func() {
        defer func() { <-sem }()   // 釋放槽位
        doWork()
    }()
```

```go
func main() {
    sem := make(chan struct{}, 3)   // 最多 3 個並發
    var wg sync.WaitGroup

    for i := 0; i < 10; i++ {
        wg.Add(1)
        sem <- struct{}{}   // 取得信號量
        go func(n int) {
            defer wg.Done()
            defer func() { <-sem }()   // 釋放信號量
            fmt.Printf("task %d running\n", n)
            time.Sleep(100 * time.Millisecond)
        }(i)
    }
    wg.Wait()
}
```

#### 常見錯誤與陷阱

**陷阱 1：Goroutine Leak（goroutine 洩漏）**

```go
// ❌ receiver 結束，但 sender 永遠阻塞，goroutine 洩漏
func leak() {
    ch := make(chan int)
    go func() {
        ch <- expensiveCompute()   // 若沒人接收，永遠阻塞
    }()
    // 函式返回後，goroutine 仍在記憶體中
}

// ✅ 用 buffered channel 或 done channel 解決
func noLeak() {
    ch := make(chan int, 1)   // buffer 1，sender 不會阻塞
    go func() {
        ch <- expensiveCompute()
    }()
    // 即使不讀，goroutine 也能正常結束
}
```

**陷阱 2：send on closed channel**

```go
// ❌ 對已關閉的 channel 送出會 panic
ch := make(chan int)
close(ch)
ch <- 1   // panic: send on closed channel

// ✅ 關閉的責任在 sender，用 sync.Once 確保只 close 一次
var once sync.Once
closeOnce := func() { once.Do(func() { close(ch) }) }
```

**陷阱 3：for range 沒有 close 會永遠等待**

```go
ch := make(chan int)

go func() {
    for i := 0; i < 5; i++ {
        ch <- i
    }
    // ❌ 忘記 close(ch)
}()

for v := range ch {   // 讀完 5 個後永遠等待，goroutine 洩漏
    fmt.Println(v)
}

// ✅ sender 負責 close
go func() {
    defer close(ch)   // 確保 close
    for i := 0; i < 5; i++ {
        ch <- i
    }
}()
```

---

### 7.2 Mutex

Mutex（互斥鎖）確保同一時間只有一個 goroutine 能進入**臨界區（Critical Section）**，
是保護共享資料最直觀的方式。

#### HB 規則

```
mu.Unlock()  happens-before  下一個 mu.Lock() 返回
```

#### 多 goroutine 競爭示意圖

```
時間軸 ──────────────────────────────────────────→

G1               G2               G3
──               ──               ──
mu.Lock()        mu.Lock()        mu.Lock()
  ↓ 取得鎖          ↓ 等待鎖           ↓ 等待鎖
x = 42           [阻塞在等待佇列]  [阻塞在等待佇列]
mu.Unlock()
  ↓ HB ──────────→ mu.Lock()
                   ↓ 取得鎖
                   read x          [繼續等待]
                   mu.Unlock()
                     ↓ HB ───────→ mu.Lock()
                                   ↓ 取得鎖
                                   read x
                                   mu.Unlock()

鎖的等待佇列（FIFO，保證公平性）：
  [G2] → [G3] → nil   等待 G1 釋放
```

#### 執行時序示意圖（HB 傳遞）

```
時間軸 ──────────────────────────────────────────→

Goroutine A                    Goroutine B
───────────                    ───────────
mu.Lock()
x = 42    ← 臨界區
y = 100
mu.Unlock()  ─── HB ──────→   mu.Lock() ← 獲得鎖
                               read x    // 一定是 42
                               read y    // 一定是 100
                               mu.Unlock()
```

#### 完整範例（互斥計數器）

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var mu sync.Mutex
    var counter int
    var wg sync.WaitGroup

    for i := 0; i < 1000; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            mu.Lock()
            counter++          // 臨界區：安全存取
            mu.Unlock()
        }()
    }

    wg.Wait()
    fmt.Println(counter)       // 保證印出 1000
}
```

#### defer unlock 最佳實踐

```go
// ✅ 推薦：defer 確保即使 panic 也能解鎖
func safeUpdate(mu *sync.Mutex, data *[]int, val int) {
    mu.Lock()
    defer mu.Unlock()   // 函式返回時自動解鎖，不會忘記
    *data = append(*data, val)
}

// ❌ 手動解鎖容易遺漏（特別是有多個 return 路徑時）
func unsafeUpdate(mu *sync.Mutex, data *[]int, val int) error {
    mu.Lock()
    if val < 0 {
        return errors.New("negative")   // ← 忘記 Unlock！
    }
    *data = append(*data, val)
    mu.Unlock()
    return nil
}
```

#### 死鎖（Deadlock）

死鎖發生在 goroutine 互相等待對方釋放鎖，導致永遠無法繼續。

```
G1 持有 muA，等待 muB
G2 持有 muB，等待 muA
→ 兩者永遠等待

圖示：
  G1: [Lock A] ──等待──→ [Lock B]
                              ↑
  G2: [Lock B] ──等待──→ [Lock A]
       ↑___________________________↓

  形成循環等待 → 死鎖
```

```go
// ❌ 死鎖範例
var muA, muB sync.Mutex

go func() {
    muA.Lock()
    time.Sleep(1 * time.Millisecond)
    muB.Lock()   // 等待 muB（G2 持有中）
    // ...
    muB.Unlock()
    muA.Unlock()
}()

go func() {
    muB.Lock()
    time.Sleep(1 * time.Millisecond)
    muA.Lock()   // 等待 muA（G1 持有中）→ 死鎖！
    // ...
    muA.Unlock()
    muB.Unlock()
}()
```

**避免死鎖的規則：**

```
規則 1：固定加鎖順序
  所有 goroutine 都按 muA → muB 的順序取鎖，不允許反向

規則 2：盡量縮小臨界區
  只在真正需要保護的地方持有鎖，儘早釋放

規則 3：不要在持有鎖時呼叫外部函式
  外部函式可能也在取鎖，容易造成不可預期的死鎖

規則 4：使用 go vet / race detector 輔助檢查
  go vet -deadlock（需額外套件）
  go test -race
```

#### sync.RWMutex（讀寫鎖）

```
RWMutex 允許：
  - 多個 goroutine 同時持有 RLock（讀鎖）
  - 只有一個 goroutine 可以持有 Lock（寫鎖）
  - 寫鎖獨佔：持有寫鎖時，沒有任何讀鎖或寫鎖可以被取得
```

**HB 規則：**

```
規則 1：RUnlock() happens-before Lock()
  → 所有讀鎖釋放後，寫鎖才能獲得

規則 2：Unlock() happens-before RLock()
  → 寫鎖釋放後，讀鎖才能獲得
```

**時序示意圖：**

```
時間軸 ──────────────────────────────────────────→

Reader1   Reader2   Reader3   Writer
───────   ───────   ───────   ──────
RLock()   RLock()             Lock()
read      read                [等待 Reader1 和 Reader2 釋放]
RUnlock() RUnlock()
                   RLock()   [等待 Reader3 釋放]
                   [等待 Writer]
                             ← 取得寫鎖
                             write
                             Unlock() ─── HB ──→
                   RLock()   取得讀鎖 ✓
```

```go
type SafeMap struct {
    mu   sync.RWMutex
    data map[string]int
}

// 讀取：可以多個 goroutine 同時進入
func (m *SafeMap) Get(key string) (int, bool) {
    m.mu.RLock()
    defer m.mu.RUnlock()
    v, ok := m.data[key]
    return v, ok
}

// 寫入：獨佔
func (m *SafeMap) Set(key string, val int) {
    m.mu.Lock()
    defer m.mu.Unlock()
    m.data[key] = val
}
```

**效能對比（讀多寫少時 RWMutex 優勢明顯）：**

```
情境：10 個 reader，1 個 writer

  Mutex：   reader 互相排隊，throughput 低
  RWMutex：10 個 reader 同時讀，throughput 提升 ~10x
```

---

### 7.3 Atomic

`sync/atomic` 提供**單一記憶體操作的原子性**，底層直接使用 CPU 的原子指令（如 `LOCK XCHG`、`CMPXCHG`），**不需要作業系統介入**，比 mutex 開銷小很多。

#### HB 規則

```
atomic.Store(&x, v)  happens-before  atomic.Load(&x)
（前提：Load 讀到了 Store 寫的那個值）
```

#### Atomic 操作與普通操作的底層差異

```
普通寫入（x = 42）：
  ┌────────────────────────────────────────────────┐
  │  MOV [x], 42   ← 可能分成多個 CPU 指令        │
  │  無記憶體屏障   ← 可被編譯器/CPU 重排          │
  │  store buffer 延遲寫回                         │
  └────────────────────────────────────────────────┘

Atomic 寫入（atomic.Store(&x, 42)）：
  ┌────────────────────────────────────────────────┐
  │  LOCK MOV [x], 42   ← 單一不可分割指令        │
  │  Memory Barrier      ← 禁止重排               │
  │  立即對其他 core 可見                          │
  └────────────────────────────────────────────────┘
```

#### CAS（Compare-And-Swap）圖解

CAS 是 atomic 最關鍵的操作：**原子地比較並交換**。

```
CompareAndSwap(&x, old, new) 的邏輯：

  if x == old {          // 比較
      x = new            // 交換（如果相等）
      return true
  }
  return false           // 不相等，什麼都不做

關鍵：「比較」和「交換」是原子的，不可被打斷。
```

**CAS 競爭示意圖：**

```
時間軸 ──────────────────────────────────────────→

x = 0（初始值）

G1                         G2
──                         ──
CAS(&x, 0, 1)              CAS(&x, 0, 2)
  ↓ 讀 x=0，比較相等          ↓ 讀 x=0，比較相等
  ↓ 寫 x=1（成功）            ↓ 此時 x 已是 1
  ↓ return true              ↓ 比較失敗（1 ≠ 0）
                             ↓ return false → 重試

最終 x = 1（G1 成功），G2 需要重試 CAS(&x, 1, 2)
```

**CAS 實作無鎖計數器：**

```go
// 無鎖計數器（Compare-And-Swap 自旋重試）
func atomicIncrement(x *int64) {
    for {
        old := atomic.LoadInt64(x)
        if atomic.CompareAndSwapInt64(x, old, old+1) {
            return   // CAS 成功，退出
        }
        // CAS 失敗（被其他 goroutine 搶先修改），重試
    }
}
// 注意：Go 1.19+ 建議用 atomic.Int64.Add，更簡潔
```

#### 執行時序示意圖

```
時間軸 ──────────────────────────────────────────→

Goroutine A (生產者)          Goroutine B (消費者)
────────────────────          ──────────────────────
data = prepareData()          for !flag.Load() {
  ↓                               // CPU 自旋，讀取 flag
flag.Store(true) ─ HB ──→    }
                              // flag.Load() 讀到 true
                              use(data)   // 保證看到 prepareData() 的結果
```

#### 完整範例

```go
package main

import (
    "fmt"
    "sync/atomic"
)

func main() {
    var flag atomic.Bool
    var data int

    go func() {
        data = 42              // 寫入資料
        flag.Store(true)       // Atomic store（建立 HB）
    }()

    for !flag.Load() {}        // Atomic load（自旋等待）
    fmt.Println(data)          // 保證看到 42
}
```

#### 非 atomic 的危險對比

```go
// ❌ data race！普通 bool 沒有任何 memory barrier
var flag bool
var data int

go func() {
    data = 42
    flag = true   // 普通寫入，可能被重排到 data=42 之前
}()

// 問題一：編譯器可能把 flag 讀取優化成常數（永遠 false）
// 問題二：即使跳出迴圈，data 也不保證是 42
for !flag {}
fmt.Println(data)   // 未定義行為
```

#### Atomic 全部型別與用途

```go
// ─── 數值型別 ───────────────────────────────────
var i32  atomic.Int32
var i64  atomic.Int64
var u32  atomic.Uint32
var u64  atomic.Uint64

i64.Store(100)
i64.Add(1)               // 原子加（返回新值）
i64.Swap(200)            // 原子替換（返回舊值）
i64.CompareAndSwap(200, 300)  // CAS

// ─── Bool ────────────────────────────────────────
var initialized atomic.Bool
if initialized.CompareAndSwap(false, true) {
    // 全局只有一個 goroutine 進入這裡
    doInit()
}

// ─── Pointer（替換整個資料結構，無鎖讀取）─────────
type Config struct {
    MaxConn int
    Timeout time.Duration
}
var cfg atomic.Pointer[Config]

// 寫入方（熱更新設定，無需停服務）
cfg.Store(&Config{MaxConn: 100, Timeout: 5 * time.Second})

// 讀取方（完全無鎖）
c := cfg.Load()
fmt.Println(c.MaxConn)

// ─── Value（任意型別，需自己保證型別一致）──────────
var v atomic.Value
v.Store([]int{1, 2, 3})     // 存任意型別
data := v.Load().([]int)    // 讀取時需型別斷言
```

**atomic.Pointer vs atomic.Value：**

```
atomic.Pointer[T]（Go 1.19+，推薦）：
  ✅ 型別安全，不需型別斷言
  ✅ 可以 Store(nil)
  ✅ 泛型支援

atomic.Value（Go 1.4+）：
  ⚠️ 需要型別斷言，容易出錯
  ⚠️ 第一次 Store 後，型別不能改變
  ❌ 不能 Store(nil)
  ✅ 相容舊版本
```

> **注意：** atomic 只保證**單一操作的原子性**。若需要「先讀再判斷再寫」的複合原子性，仍需 mutex 或 CAS 自旋。

---

### 7.4 Goroutine Start（go 語句）

#### HB 規則

```
go 語句的執行  happens-before  goroutine 函式開始執行
```

#### 執行時序示意圖

```
時間軸 ──────────────────────────────────────────→

主 Goroutine                  新 Goroutine（f）
────────────                  ─────────────────
x = 42         ← HB 邊界之前
config = "prod"← HB 邊界之前
go f() ─────── HB ──────────→ func f() {
                                  fmt.Println(x)       // 保證是 42
                                  fmt.Println(config)  // 保證是 "prod"
                              }
```

**HB 邊界精確說明：**

```
HB 只涵蓋 go 語句「之前」的所有操作。

主 Goroutine                  新 Goroutine
────────────                  ────────────
a = 1          ← ✅ HB 範圍內
b = 2          ← ✅ HB 範圍內
go f()         ← HB 邊界
c = 3          ← ❌ HB 邊界之後，不保證對 f 可見
                              func f() {
                                  _ = a   // ✅ 保證是 1
                                  _ = b   // ✅ 保證是 2
                                  _ = c   // ❌ 可能是 0 或 3，不確定
                              }
```

#### 完整範例

```go
package main

import (
    "fmt"
    "time"
)

func main() {
    x := 42
    name := "Alice"

    go func() {
        fmt.Println(x, name)   // 保證看到 42 和 "Alice"
    }()

    time.Sleep(time.Second)   // 注意：sleep 本身不建立 HB
}
```

#### 傳遞初始化參數給 goroutine

```go
// ✅ 透過參數傳遞（最清晰，值在 go 語句時複製）
for i := 0; i < 5; i++ {
    go func(n int) {   // n 是 i 的副本，HB 保證可見
        fmt.Println(n)
    }(i)
}

// ✅ 透過閉包捕獲（go 語句之前賦值）
for i := 0; i < 5; i++ {
    i := i   // Go 1.21 之前需要這樣，每次建立新變數
    go func() {
        fmt.Println(i)
    }()
}

// ❌ Go 1.21 之前的典型錯誤（所有 goroutine 共享同一個 i）
for i := 0; i < 5; i++ {
    go func() {
        fmt.Println(i)   // 可能全部印出 5
    }()
}
```

---

### 7.5 Goroutine Exit（結束不建立 HB）

#### 重要：Goroutine 結束本身不建立 HB！

```
常見誤解：「goroutine 跑完了，主 goroutine 一定看得到它的寫入」
實際情況：goroutine 結束 ≠ 建立 happens-before

必須透過明確的同步原語（channel、WaitGroup 等）才能建立 HB。
```

**時序示意圖（為什麼 sleep 不夠）：**

```
時間軸 ──────────────────────────────────────────→

Goroutine A              主 Goroutine
───────────              ────────────
x = 42                   time.Sleep(1s)
goroutine 結束           (sleep 結束)
                         fmt.Println(x)   ← 仍無 HB 保證！

原因：sleep 只是等待時間，不建立任何記憶體屏障。
      即使 goroutine 已結束 100ms，x 的寫入也不保證對主 goroutine 可見。
```

```go
// ❌ 錯誤：依賴 sleep 等待
var x int
go func() {
    x = 42
}()
time.Sleep(time.Second)   // sleep 不建立 HB！
fmt.Println(x)            // 不保證是 42
```

#### 正確做法：WaitGroup

```go
var x int
var wg sync.WaitGroup

wg.Add(1)
go func() {
    defer wg.Done()
    x = 42
}()

wg.Wait()         // wg.Done() HB wg.Wait() 返回
fmt.Println(x)    // 保證是 42 ✓
```

**WaitGroup 時序示意圖：**

```
時間軸 ──────────────────────────────────────────→

Goroutine (工作)              主 Goroutine
────────────────              ────────────
x = 42                        wg.Wait() ← 阻塞
y = 100
wg.Done()  ─── HB ──────────→ (Wait 返回)
                               fmt.Println(x, y)  // 保證是 42, 100
```

**多 goroutine 並行工作：**

```go
results := make([]int, 10)
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(idx int) {
        defer wg.Done()
        results[idx] = idx * idx   // 每個 goroutine 寫自己的 index，無 race
    }(i)
}

wg.Wait()
fmt.Println(results)   // 保證看到所有結果
```

#### 正確做法：channel 通知

```go
var x int
done := make(chan struct{})

go func() {
    x = 42
    close(done)   // close HB receive
}()

<-done            // 等待
fmt.Println(x)    // 保證是 42 ✓
```

---

### 7.6 sync.Once

`sync.Once` 確保某個函式在整個程式生命週期中**只被執行一次**，且執行完成後的結果對所有 goroutine 可見。最常見用途是**延遲初始化（Lazy Initialization）**。

#### HB 規則

```
once.Do(f) 中 f 的執行完成  happens-before  任何 once.Do() 返回
```

#### 為什麼不能用普通 bool 旗標？（Double-Checked Locking 的陷阱）

很多人直覺上想用 double-checked locking，但沒有 Once 的話這是錯的：

```go
// ❌ 看起來對，但有 data race！
var initialized bool
var instance *DB

func getInstance() *DB {
    if !initialized {          // 第一次檢查（無鎖）← data race！
        mu.Lock()
        defer mu.Unlock()
        if !initialized {      // 第二次檢查（有鎖）
            instance = &DB{...}
            initialized = true
        }
    }
    return instance
}

問題：
  G1 讀 initialized（false，在鎖外）
  G2 寫 initialized=true（在鎖內）
  → 這是 data race（一讀一寫，無 HB）
  → instance 可能被讀到半初始化的狀態
```

```go
// ✅ 正確：用 sync.Once
var once sync.Once
var instance *DB

func getInstance() *DB {
    once.Do(func() {
        instance = &DB{conn: "postgres://..."}
    })
    return instance   // Once 保證 instance 完整初始化後才返回
}
```

#### 執行時序示意圖

```
時間軸 ──────────────────────────────────────────→

G1                    G2                    G3
──                    ──                    ──
once.Do(init)         once.Do(init)         once.Do(init)
  ↓ 搶到執行權           ↓ 發現 done=0           ↓ 發現 done=0
  init() 開始            [等待 G1 完成]          [等待 G1 完成]
  instance = &DB{...}
  init() 完成 ─ HB ──→  ↓ 返回              ↓ 返回
  done = 1               instance ≠ nil ✓   instance ≠ nil ✓
```

**Once 內部實現原理：**

```
type Once struct {
    done atomic.Uint32   // 0 = 未執行，1 = 已完成
    m    Mutex
}

func (o *Once) Do(f func()) {
    if o.done.Load() == 0 {   // 快速路徑（已完成則直接返回）
        o.doSlow(f)
    }
}

func (o *Once) doSlow(f func()) {
    o.m.Lock()
    defer o.m.Unlock()
    if o.done.Load() == 0 {   // 再次確認（可能被其他 G 搶先完成）
        defer o.done.Store(1)
        f()
    }
}
```

#### 完整範例（Singleton DB 連線）

```go
package main

import (
    "fmt"
    "sync"
)

type DB struct {
    conn string
}

var (
    once     sync.Once
    instance *DB
)

func getDB() *DB {
    once.Do(func() {
        // 只執行一次，且完成後才對所有 goroutine 可見
        instance = &DB{conn: "postgres://localhost/mydb"}
        fmt.Println("DB 連線初始化完成")
    })
    return instance   // 不論哪個 goroutine 呼叫，都看到完整初始化的 instance
}

func main() {
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            db := getDB()
            fmt.Printf("G%d 使用 DB: %s\n", id, db.conn)
        }(i)
    }
    wg.Wait()
    // 輸出：「DB 連線初始化完成」只出現一次
}
```

#### 常見陷阱

```go
// ❌ 陷阱：Once 的 f 不能呼叫同一個 Once
var once sync.Once
once.Do(func() {
    once.Do(func() { ... })   // 死鎖！Once 的鎖還沒釋放
})

// ❌ 陷阱：f 發生 panic，Once 不會重試
var once sync.Once
once.Do(func() {
    panic("init failed")   // panic 後 once.done 仍被設為 1
})
once.Do(func() {
    // 永遠不會執行（Once 認為已完成）
})

// ✅ 處理初始化失敗：回傳 error
type singleton struct {
    once sync.Once
    db   *DB
    err  error
}

func (s *singleton) GetDB() (*DB, error) {
    s.once.Do(func() {
        s.db, s.err = connectDB()
    })
    return s.db, s.err
}
```

---

### 7.7 sync.Cond

**sync.Cond** 是 Go 提供的條件變數（Condition Variable），用於讓 goroutine 在某個「條件成立」前**高效等待**，避免 busy-waiting（忙碌等待）浪費 CPU。

#### 核心概念

```
條件變數解決的問題：

  ❌ Busy-waiting（浪費 CPU）：
     for !condition {
         // 一直空跑，佔用 CPU
     }

  ✅ sync.Cond（讓 goroutine 睡眠，條件成立才喚醒）：
     cond.L.Lock()
     for !condition {
         cond.Wait()   // 睡眠，釋放 lock，讓其他 goroutine 執行
     }
     // 條件成立，繼續執行
     cond.L.Unlock()
```

#### HB 規則

```
cond.Signal()    happens-before  被喚醒的 cond.Wait() 返回
cond.Broadcast() happens-before  所有被喚醒的 cond.Wait() 返回
```

#### 三個核心方法

| 方法 | 說明 |
|------|------|
| `cond.Wait()` | **釋放 lock** 並讓 goroutine 睡眠，被喚醒後**重新取得 lock** |
| `cond.Signal()` | 喚醒**一個**正在 Wait 的 goroutine |
| `cond.Broadcast()` | 喚醒**所有**正在 Wait 的 goroutine |

> **關鍵：`Wait()` 必須在 lock 持有時呼叫，且必須在 `for` 迴圈中使用（不能用 `if`）。**

#### 執行時序示意圖

**Signal（喚醒一個）：**

```
時間軸 ─────────────────────────────────────────→

生產者 (Producer)             消費者 A              消費者 B
──────────────────            ──────────            ──────────
                              cond.L.Lock()         cond.L.Lock()
                              for !ready {          for !ready {
                                cond.Wait()           cond.Wait()
                              } ← 釋放 lock，睡眠   } ← 釋放 lock，睡眠

cond.L.Lock()
data = produce()
ready = true
cond.Signal()  ─── HB ──→   (喚醒其中一個)
cond.L.Unlock()              cond.Wait() 返回      (仍在睡眠)
                             // 重新取得 lock
                             process(data)  ✓
                             cond.L.Unlock()
```

**Broadcast（喚醒全部）：**

```
時間軸 ─────────────────────────────────────────→

生產者                        消費者 A              消費者 B              消費者 C
──────                        ──────────            ──────────            ──────────
                              cond.Wait() 睡眠      cond.Wait() 睡眠      cond.Wait() 睡眠

cond.Broadcast() ── HB ──→   全部喚醒 ────────────→ 全部喚醒 ───────────→ 全部喚醒
                             重新競爭 lock          重新競爭 lock          重新競爭 lock
                             (依序執行)             (依序執行)             (依序執行)
```

**Wait() 內部行為（原子操作）：**

```
cond.Wait() 的內部執行步驟：

  步驟 1：原子地 釋放 lock + 將 goroutine 加入等待佇列
           ↓
  步驟 2：goroutine 睡眠（不佔用 CPU）
           ↓
  步驟 3：收到 Signal 或 Broadcast 被喚醒
           ↓
  步驟 4：重新取得 lock（可能要等其他 goroutine 先釋放）
           ↓
  步驟 5：Wait() 返回（回到 for 迴圈重新檢查條件）

  重要：步驟 1 是原子的，確保不會有 goroutine 在「即將 Wait」
         但還沒睡著的瞬間收到 Signal 而永久錯過喚醒。
```

#### 範例一：生產者 / 消費者

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

type Queue struct {
    mu    sync.Mutex
    cond  *sync.Cond
    items []int
}

func NewQueue() *Queue {
    q := &Queue{}
    q.cond = sync.NewCond(&q.mu)
    return q
}

// 生產者：加入資料並通知消費者
func (q *Queue) Push(item int) {
    q.mu.Lock()
    q.items = append(q.items, item)
    fmt.Printf("Push %d，佇列長度：%d\n", item, len(q.items))
    q.cond.Signal()    // 通知一個等待的消費者
    q.mu.Unlock()
}

// 消費者：等待資料可用
func (q *Queue) Pop() int {
    q.mu.Lock()
    defer q.mu.Unlock()

    // 必須用 for，不能用 if！
    // 原因：被喚醒後條件可能已被其他 goroutine 消費掉
    for len(q.items) == 0 {
        fmt.Println("佇列為空，等待...")
        q.cond.Wait()   // 睡眠，等待 Signal
    }

    item := q.items[0]
    q.items = q.items[1:]
    return item
}

func main() {
    q := NewQueue()

    // 啟動兩個消費者
    for i := 0; i < 2; i++ {
        go func(id int) {
            for {
                item := q.Pop()
                fmt.Printf("消費者 %d 取得：%d\n", id, item)
            }
        }(i)
    }

    time.Sleep(100 * time.Millisecond)

    // 生產者陸續生產
    for i := 1; i <= 5; i++ {
        q.Push(i)
        time.Sleep(200 * time.Millisecond)
    }
}
```

**輸出說明：**

```
佇列為空，等待...          ← 消費者 0 進入等待
佇列為空，等待...          ← 消費者 1 進入等待
Push 1，佇列長度：1
消費者 0 取得：1           ← Signal 喚醒其中一個
佇列為空，等待...          ← 消費者 0 再次等待
Push 2，佇列長度：1
消費者 1 取得：2
...
```

#### 範例二：多個 goroutine 等待同一事件（Broadcast）

```go
package main

import (
    "fmt"
    "sync"
    "time"
)

func main() {
    var mu sync.Mutex
    cond := sync.NewCond(&mu)
    ready := false

    // 啟動多個 worker，等待 ready 信號
    var wg sync.WaitGroup
    for i := 0; i < 5; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            mu.Lock()
            for !ready {               // 用 for，不用 if
                cond.Wait()            // 等待 Broadcast
            }
            fmt.Printf("Worker %d 開始工作\n", id)
            mu.Unlock()
        }(i)
    }

    // 模擬準備工作
    time.Sleep(500 * time.Millisecond)
    fmt.Println("準備完成，喚醒所有 worker...")

    mu.Lock()
    ready = true
    cond.Broadcast()   // 喚醒所有等待的 goroutine
    mu.Unlock()

    wg.Wait()
    fmt.Println("所有 worker 完成")
}
```

#### 為什麼必須用 `for` 而不是 `if`？

```
問題：Spurious Wakeup（虛假喚醒）

  即使沒有收到 Signal / Broadcast，
  Wait() 也可能因為 OS 底層原因而返回。

  ❌ 用 if 會錯誤地繼續執行：
     mu.Lock()
     if !ready {
         cond.Wait()      // 虛假喚醒後 ready 仍是 false
     }
     use(data)           // ready == false，錯誤！

  ✅ 用 for 會重新檢查條件：
     mu.Lock()
     for !ready {
         cond.Wait()      // 虛假喚醒後重新檢查 ready
     }
     use(data)           // ready 一定是 true
```

也存在另一個原因：**競爭喚醒**——Broadcast 喚醒所有 goroutine，但它們需要依序重新取得 lock，第一個取到的 goroutine 處理完後，後面的 goroutine 醒來時條件可能已不成立。

```
G1 和 G2 同時被 Broadcast 喚醒：

  G1 搶到 lock → 讀取資料 → 解鎖
  G2 搶到 lock → 用 for 重新檢查 → 條件不成立 → 繼續 Wait ✓
               → 若用 if，會直接執行，但資料已被 G1 消費 ✗
```

#### sync.Cond vs Channel：如何選擇？

```
使用 sync.Cond 的場景：
  ✅ 等待「某個條件成立」，而非等待「特定資料」
  ✅ 需要廣播給多個 goroutine（Broadcast）
  ✅ 已經有 Mutex 保護共享狀態，不想再建立 channel
  ✅ 條件複雜（如：佇列有空間 AND 優先權 > 5）

使用 channel 的場景：
  ✅ 傳遞具體的值
  ✅ 一對一或 pipeline 模式
  ✅ 使用 select 多路複用
  ✅ 更符合 Go 慣例（優先考慮 channel）

典型誤用（不應用 sync.Cond）：
  ❌ 只是傳遞資料 → 用 channel
  ❌ 只有一個等待者 → 用 channel 或 WaitGroup
```

---

### 7.8 sync.Map

**sync.Map** 是 Go 標準庫提供的並發安全 map，專門針對兩種高頻場景優化：**讀多寫少**以及**多 goroutine 各自只寫自己的 key**（不交叉修改）。

#### 為什麼不能直接用普通 map？

```
普通 map 的問題：

  Go 的 map 完全不是執行緒安全的。
  兩個 goroutine 同時讀寫同一個 map，
  不只是結果錯誤，甚至會造成 runtime 崩潰（fatal error）。

  ❌ 危險：
     m := make(map[string]int)
     go func() { m["key"] = 1 }()    // 寫
     go func() { _ = m["key"] }()    // 讀（並發 → fatal error）

  runtime 輸出：
  fatal error: concurrent map read and map write
```

#### HB 規則

```
sm.Store(key, val)   happens-before  sm.Load(key) 讀到該值
sm.Delete(key)       happens-before  sm.Load(key) 返回 (nil, false)
```

#### 內部結構（雙層 map 設計）

`sync.Map` 使用兩個 map 搭配一把 mutex，達到讀取幾乎無鎖的效果：

```
┌─────────────────────────────────────────────────────────────┐
│                        sync.Map                             │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  read map（atomic.Pointer，讀取完全無鎖）           │   │
│  │                                                     │   │
│  │  "a" ──→ entry{p: 0xABCD}   (expunged 標記)        │   │
│  │  "b" ──→ entry{p: 0x1234}   (正常值)               │   │
│  │  "c" ──→ entry{p: 0x5678}   (正常值)               │   │
│  └─────────────────────────────────────────────────────┘   │
│                    ↑ 大部分讀取走這條路（不需鎖）           │
│                                                             │
│  mu ─────── Mutex（只有寫入或 miss 時才鎖）                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  dirty map（完整資料，有鎖才能存取）                │   │
│  │                                                     │   │
│  │  "a" ──→ entry{...}                                 │   │
│  │  "b" ──→ entry{...}                                 │   │
│  │  "c" ──→ entry{...}                                 │   │
│  │  "d" ──→ entry{...}   ← 新寫入先在這裡             │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  misses：計數器，miss 累積到閾值後，dirty 升為 read map     │
└─────────────────────────────────────────────────────────────┘
```

**讀取路徑（快速路徑 vs 慢速路徑）：**

```
Load(key)
   │
   ├─ 在 read map 找到？ ──→ 直接返回（無鎖，atomic load）✓
   │
   └─ 找不到（miss）
         │
         ├─ 鎖定 mu
         ├─ 在 dirty map 找
         ├─ misses++
         ├─ 若 misses >= len(dirty)：dirty 升為 read map
         └─ 返回結果
```

**寫入路徑：**

```
Store(key, val)
   │
   ├─ key 在 read map 且未被 expunged？
   │     └─ atomic CAS 更新 entry.p（無鎖）✓
   │
   └─ 否則
         ├─ 鎖定 mu
         ├─ 更新 dirty map
         └─ 解鎖
```

#### 執行時序示意圖

**讀多寫少（sync.Map 的最佳場景）：**

```
時間軸 ─────────────────────────────────────────→

G1 (寫入)         G2 (讀取)         G3 (讀取)         G4 (讀取)
─────────         ─────────         ─────────         ─────────
sm.Store("k",1)
  ↓ 更新 read map
                  sm.Load("k")      sm.Load("k")      sm.Load("k")
                  → 走快速路徑      → 走快速路徑      → 走快速路徑
                  → 無鎖 ✓          → 無鎖 ✓          → 無鎖 ✓
                  → 返回 1          → 返回 1          → 返回 1

多個 reader 可以完全並行，互不干擾
```

**dirty map 升級過程：**

```
初始狀態：
  read map: {a:1, b:2}
  dirty map: nil
  misses: 0

Store("c", 3)：          // 新 key，dirty 從 read 複製並加入 c
  read map: {a:1, b:2}
  dirty map: {a:1, b:2, c:3}

Load("c") × 3次：        // 每次 miss 都在 dirty 找到
  misses: 1 → 2 → 3

misses >= len(dirty)：   // 觸發升級
  read map: {a:1, b:2, c:3}   ← dirty 升為 read
  dirty map: nil
  misses: 0
```

#### API 完整說明

```go
var sm sync.Map

// Store：存入 key-value（覆蓋舊值）
sm.Store("key", "value")

// Load：讀取，返回 (value, ok)
val, ok := sm.Load("key")
if ok {
    fmt.Println(val.(string))
}

// LoadOrStore：key 不存在才存入，返回 (實際值, 是否已存在)
actual, loaded := sm.LoadOrStore("key", "default")
// loaded=true 表示已有值，actual 是舊值
// loaded=false 表示成功存入，actual 是新值

// Delete：刪除 key
sm.Delete("key")

// LoadAndDelete：讀取並刪除（原子操作）
val, loaded = sm.LoadAndDelete("key")

// Range：遍歷所有 key-value（遍歷期間的修改不保證可見）
sm.Range(func(key, value any) bool {
    fmt.Println(key, value)
    return true  // 返回 false 停止遍歷
})

// Swap（Go 1.20+）：替換並返回舊值
old, loaded := sm.Swap("key", "new_value")

// CompareAndSwap（Go 1.20+）：CAS 操作
swapped := sm.CompareAndSwap("key", "expected", "new")

// CompareAndDelete（Go 1.20+）：值符合才刪除
deleted := sm.CompareAndDelete("key", "expected")
```

#### 範例一：並發快取（讀多寫少）

```go
package main

import (
    "fmt"
    "sync"
)

type Cache struct {
    sm sync.Map
}

func (c *Cache) Set(key string, val any) {
    c.sm.Store(key, val)
}

func (c *Cache) Get(key string) (any, bool) {
    return c.sm.Load(key)
}

// GetOrCompute：key 不存在才呼叫 compute，避免重複計算
func (c *Cache) GetOrCompute(key string, compute func() any) any {
    if val, ok := c.sm.Load(key); ok {
        return val   // 快速路徑：已有值，無鎖讀取
    }
    val := compute()
    actual, _ := c.sm.LoadOrStore(key, val)
    return actual    // 若並發寫入，返回第一個寫入的值
}

func main() {
    cache := &Cache{}
    var wg sync.WaitGroup

    // 100 個 goroutine 同時讀寫
    for i := 0; i < 100; i++ {
        wg.Add(1)
        go func(n int) {
            defer wg.Done()
            key := fmt.Sprintf("user:%d", n%10)

            // 寫入
            cache.Set(key, n)

            // 讀取
            if val, ok := cache.Get(key); ok {
                _ = val
            }
        }(i)
    }

    wg.Wait()

    // 遍歷所有快取
    cache.sm.Range(func(k, v any) bool {
        fmt.Printf("%s = %v\n", k, v)
        return true
    })
}
```

#### 範例二：多 goroutine 各自寫自己的 key（無交叉）

```go
package main

import (
    "fmt"
    "sync"
)

func main() {
    var results sync.Map
    var wg sync.WaitGroup

    // 每個 goroutine 寫入自己專屬的 key，互不干擾
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func(id int) {
            defer wg.Done()
            key := fmt.Sprintf("worker-%d", id)
            results.Store(key, id*id)   // 每個 goroutine 只寫自己的 key
        }(i)
    }

    wg.Wait()

    // 彙整結果
    results.Range(func(k, v any) bool {
        fmt.Printf("%s: %d\n", k, v)
        return true
    })
}
```

#### sync.Map vs Mutex+map：如何選擇？

```
效能比較示意（讀多寫少情境）：

  操作          Mutex+map        sync.Map
  ──────────    ─────────        ────────
  純讀取        需鎖（競爭）     無鎖（atomic）← 大幅領先
  更新已有key   需鎖             部分無鎖（CAS）
  寫入新key     需鎖             需鎖（dirty map）
  遍歷          需鎖             無鎖快照（但注意一致性）

適合 sync.Map 的場景：
  ✅ 讀遠多於寫（如：快取、路由表、設定）
  ✅ 寫入後幾乎不再修改（write-once, read-many）
  ✅ 多個 goroutine 各自操作不同的 key（不交叉）

適合 Mutex+map 的場景：
  ✅ 寫入頻率與讀取相當
  ✅ 需要批次操作（如：同時更新多個 key 保持一致性）
  ✅ 需要 len()、for range 等原生 map 操作
  ✅ key 集合變化頻繁（頻繁新增/刪除 key）
```

**注意事項：**

```go
// ❌ sync.Map 沒有 len() 方法，需要自己計數
var count int
sm.Range(func(k, v any) bool {
    count++
    return true
})

// ❌ Range 遍歷時存入的新 key 不保證被看到
sm.Range(func(k, v any) bool {
    sm.Store("new-key", 1)  // 不保證在本次 Range 中出現
    return true
})

// ❌ 不要在 sync.Map 上做 check-then-act（用 LoadOrStore / CompareAndSwap）
val, ok := sm.Load("key")   // ← 讀
if !ok {                     // ← 判斷
    sm.Store("key", 1)       // ← 寫（非原子！中間可能被其他 goroutine 搶先）
}
// ✅ 正確做法：
sm.LoadOrStore("key", 1)
```

---

### 7.9 各機制 HB 速查表

```
機制                      HB 邊界（左 happens-before 右）
──────────────────────────────────────────────────────────────
ch <- v (send)            Send 完成  ─────────→  <-ch (receive)
close(ch)                 close()    ─────────→  <-ch (receive)
mu.Unlock()               Unlock()   ─────────→  mu.Lock() 返回
atomic.Store(&x, v)       Store()    ─────────→  atomic.Load(&x) 讀到 v
go f()                    go 語句    ─────────→  f() 開始執行
wg.Done()                 Done()     ─────────→  wg.Wait() 返回
once.Do(f) — f 執行完     f 完成     ─────────→  所有 once.Do 返回
cond.Signal()             Signal()   ─────────→  被喚醒的 Wait() 返回
cond.Broadcast()          Broadcast() ────────→  所有被喚醒的 Wait() 返回
sm.Store(k, v)            Store()    ─────────→  sm.Load(k) 讀到該值
sm.Delete(k)              Delete()   ─────────→  sm.Load(k) 返回 (nil,false)
```

---

## 8. Happens-Before 圖模型

### 基本概念

Happens-Before 可以建模成一張**有向無環圖（DAG）**：

```
事件 A  ──HB──→  事件 B  ──HB──→  事件 C

意義：
  A → B：A 的所有寫入對 B 可見
  B → C：B 的所有寫入對 C 可見
  A → C：（傳遞性）A 的所有寫入對 C 也可見
```

**圖的性質：**

```
傳遞性：A → B 且 B → C  則  A → C
反身性：A → A（同一個 goroutine 內，程式順序自動建立 HB）
非對稱：A → B 不代表 B → A
```

### 傳遞性範例

```go
var x, y int
ch1 := make(chan struct{}, 1)
ch2 := make(chan struct{}, 1)

// G1 → G2 → 主 goroutine 的傳遞鏈
go func() {  // G1
    x = 1
    ch1 <- struct{}{}     // HB₁
}()

go func() {  // G2
    <-ch1                 // 接收 HB₁
    y = 2
    ch2 <- struct{}{}     // HB₂
}()

<-ch2                     // 接收 HB₂

// HB 鏈：x=1 → ch1 send → ch1 recv → y=2 → ch2 send → ch2 recv
fmt.Println(x, y)          // 保證看到 1 和 2
```

```
因果圖：

G1: [x=1] ──HB₁──→ [ch1 send]
                         │
G2:             [ch1 recv] ──→ [y=2] ──HB₂──→ [ch2 send]
                                                    │
主: [x=?, y=?]                          [ch2 recv] ──→ [print x,y]
                                                            ↑
                                        透過傳遞性看到 x=1 且 y=2
```

### 無 HB 關係的情況

```
G1:  [x = 1]
                   ← 沒有任何箭頭 →
G2:            [read x]

結論：G2 的 read x 可能得到 0 或 1，行為未定義
```

---

## 9. Data Race 本質

### 定義

符合以下**所有條件**即構成 **Data Race**：

```
條件 1：兩個（或以上）goroutine 存取同一記憶體位置
條件 2：至少一個操作是「寫入」
條件 3：兩個操作之間沒有 happens-before 關係
```

### 執行時序示意圖

```
時間軸 ─────────────────────────────────────────→

G1                    G2
──                    ──
read x  (得到 0)
  ↓                   read x  (得到 0)
x = x + 1              ↓
  ↓                   x = x + 1
write x = 1            ↓
                      write x = 1   ← 覆蓋 G1 的寫入！

預期結果：x = 2
實際結果：x = 1   ← 遺失了一次加法
```

**記憶體層面的示意：**

```
G1 (Core 1)                  G2 (Core 2)
───────────                  ───────────
load x=0 from cache          load x=0 from cache
x_local = 0 + 1 = 1         x_local = 0 + 1 = 1
store x=1 to cache           store x=1 to cache
  ↓                            ↓
Main Memory: x=1  ← 最後寫入者獲勝，一次加法消失
```

### 偵測方式

```bash
# 執行時期偵測（有額外開銷，建議開發/測試時使用）
go run -race main.go
go test -race ./...
go build -race -o myapp_race
```

**Race detector 輸出範例：**

```
==================
WARNING: DATA RACE
Write at 0x00c0000b4010 by goroutine 7:
  main.main.func1()
      /tmp/main.go:12 +0x2c

Previous write at 0x00c0000b4010 by goroutine 6:
  main.main.func1()
      /tmp/main.go:12 +0x2c

Goroutine 7 (running) created at:
  main.main()
      /tmp/main.go:10 +0x6e
==================
```

### 常見 Data Race 模式與修正

**模式一：共享計數器**

```go
// ❌ Data race
var counter int
var wg sync.WaitGroup
for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        counter++   // 讀-改-寫，非原子操作
    }()
}
wg.Wait()

// ✅ 修正方案 A：atomic
var counter atomic.Int64
for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        counter.Add(1)
    }()
}

// ✅ 修正方案 B：mutex
var mu sync.Mutex
var counter int
for i := 0; i < 1000; i++ {
    wg.Add(1)
    go func() {
        defer wg.Done()
        mu.Lock()
        counter++
        mu.Unlock()
    }()
}
```

**模式二：map 並發讀寫**

```go
// ❌ Data race：map 不是執行緒安全的
m := make(map[string]int)
go func() { m["key"] = 1 }()
go func() { _ = m["key"] }()

// ✅ 修正方案 A：mutex 保護
var mu sync.RWMutex
m := make(map[string]int)
go func() {
    mu.Lock()
    m["key"] = 1
    mu.Unlock()
}()
go func() {
    mu.RLock()
    _ = m["key"]
    mu.RUnlock()
}()

// ✅ 修正方案 B：sync.Map（適合讀多寫少）
var sm sync.Map
go func() { sm.Store("key", 1) }()
go func() { sm.Load("key") }()
```

**模式三：goroutine 中捕獲迴圈變數（Go 1.22 之前）**

```go
// ❌ Go 1.21 及之前：所有 goroutine 共享同一個 i
for i := 0; i < 5; i++ {
    go func() {
        fmt.Println(i)   // 可能全部印出 5
    }()
}

// ✅ 修正：明確傳遞變數
for i := 0; i < 5; i++ {
    i := i   // 建立新變數（或透過參數傳遞）
    go func() {
        fmt.Println(i)
    }()
}

// ✅ Go 1.22+ 之後，for 迴圈變數自動成為每次迭代的新變數
```

---

## 10. 系統層理解總整理

### 問題根源

```
┌──────────────────────────────────────────────────────────┐
│               為什麼需要 Happens-Before？                  │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  硬體層面：                                               │
│    • 每個 CPU core 有自己的 L1 cache                      │
│    • 有 store buffer（寫入不立即可見）                    │
│    • Out-of-order execution（亂序執行）                   │
│                                                          │
│  軟體層面：                                               │
│    • 編譯器優化會重排無依賴的指令                          │
│    • 語言規範允許這些優化                                  │
│                                                          │
│  結果：                                                   │
│    沒有同步機制 → 行為完全不可預測                         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 解決方案對照表

| 機制 | HB 建立時機 | 效能 | 適用場景 |
|------|------------|------|---------|
| `channel`（unbuffered） | Send/Receive 之間 | 中 | goroutine 間通訊、協調 |
| `channel`（buffered） | 第 n 個 Send / 第 n+C 個 Recv | 中高 | 限速、批次處理 |
| `sync.Mutex` | Unlock → Lock | 中 | 保護複雜臨界區 |
| `sync.RWMutex` | RUnlock→Lock / Unlock→RLock | 中高（讀多） | 讀多寫少的共享資料 |
| `sync.Cond` | Signal/Broadcast → Wait 返回 | 中 | 等待條件成立、廣播喚醒多個 goroutine |
| `sync.Map` | Store → Load（讀到該值） | 高（讀多） | 並發安全 map，讀多寫少或各寫自己的 key |
| `sync/atomic` | Store → Load（讀到該值） | 高 | 計數器、旗標、指標替換 |
| `go f()` | go 語句 → f 開始 | N/A | 傳遞初始狀態 |
| `sync.WaitGroup` | Done → Wait 返回 | 中 | 等待多個 goroutine |
| `sync.Once` | Do(f) 完成 → Do 返回 | 高（初始化後） | 一次性初始化 |

### 選擇原則

```
需求                              推薦方案
────────────────────────────────────────────────────
goroutine 間傳遞資料              channel
等待多個 goroutine 完成           sync.WaitGroup
一次性初始化                      sync.Once
保護複雜的多步驟操作               sync.Mutex
讀多寫少的共享資料                 sync.RWMutex
等待某個條件成立                   sync.Cond
廣播喚醒多個 goroutine            sync.Cond.Broadcast()
並發安全 map（讀多寫少）           sync.Map
並發安全 map（寫多或需批次操作）   sync.Mutex + map
單一整數計數器或旗標               sync/atomic
替換整個資料結構（無鎖讀取）       atomic.Pointer[T]
並發安全 map（讀多寫少）           sync.Map
並發安全 map（寫多或批次操作）     sync.Mutex + map
```

---

## 11. 完整結論

Go 並不是唯一有 Memory Model 的語言，但 Go 的設計哲學非常明確：

> **有 Data Race = 行為未定義（Undefined Behavior）**

### 三條黃金法則

```
法則 1：不要假設執行順序
  → 沒有 HB 保證的程式碼，行為不可預測
  → 即使「跑了一千次都正確」，也可能在特定 CPU/OS 下出錯

法則 2：不要裸存取共享變數
  → 一定要透過 channel、mutex 或 atomic
  → 包括 bool、int 這種基本型別也不例外

法則 3：開啟 race detector 驗證
  → 開發和測試時務必使用 -race
  → CI/CD 流程中應包含 go test -race
```

### 完整心智模型

```
問題根源                解決機制               保證效果
──────────             ──────────             ──────────
CPU 亂序執行    →      Memory Barrier    →    指令有序
Store Buffer   →      Flush Buffer      →    寫入可見
Cache 不一致   →      Cache Invalidate  →    讀到最新值
編譯器重排     →      編譯器語義        →    程式邏輯正確

Go 的 HB 機制（channel/mutex/atomic/...）
底層都是透過上述硬體機制實現的。
```

### 一句話總結

> **Happens-Before = 記憶體可見性的因果關係保證**
>
> 它不是描述時間，而是描述：
> **「如果你觀察到了某個事件（如 channel receive），你一定也能看到建立這個事件之前的所有記憶體寫入。」**
