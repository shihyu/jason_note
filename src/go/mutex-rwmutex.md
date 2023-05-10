# Go 簡單例子來理解 sync.Mutex 和 sync.RWMutex

出處: https://clouding.city/go/mutex-rwmutex/



用簡單的例子來理解 `sync.Mutex` 和 `sync.RWMutex`。

## 蓋一間銀行

假設有一間銀行，可以存款和查詢餘額。

```go
package main

import (
    "fmt"
)

type Bank struct {
    balance int
}

func (b *Bank) Deposit(amount int) {
    b.balance += amount
}

func (b *Bank) Balance() int {
    return b.balance
}

func main() {
    b := &Bank{}

    b.Deposit(1000)
    b.Deposit(1000)
    b.Deposit(1000)

    fmt.Println(b.Balance())
}
$ go run main.go
3000
```

執行之後結果是 3000 沒問題，1000+1000+1000=3000。

## 同時存款

銀行不太可能讓人一個一個排隊存款，也需要支援同時存款，當今天存款的動作是並行的，會發生什麼事呢？

這邊用 sync.WaitGroup 去等待所有 goroutine 執行完畢，之後再印出餘額。

```go
func main() {
    var wg sync.WaitGroup
    b := &Bank{}

    wg.Add(3)
    go func() {
        b.Deposit(1000)
        wg.Done()
    }()
    go func() {
        b.Deposit(1000)
        wg.Done()
    }()
    go func() {
        b.Deposit(1000)
        wg.Done()
    }()

    wg.Wait()

    fmt.Println(b.Balance())
}
$ go run main.go
3000
```

還是 3000 沒問題，那我們同時存款 1000 次的時候會發生什麼事呢？

```go
func main() {
    var wg sync.WaitGroup
    b := &Bank{}

    n := 1000
    wg.Add(n)
    for i := 1; i <= n; i++ {
        go func() {
            b.Deposit(1000)
            wg.Done()
        }()
    }

    fmt.Println(b.Balance())
}
$ go run main.go
946000
```

誒奇怪，正常來說 1000 * 1000 = 1000000 嗎？怎麼數字不正確！

我們這次多帶一個參數 `-race` 跑看看

> `-race` 參數是 go 的 [Race Detector](https://blog.golang.org/race-detector)，內建整合工具，可以輕鬆檢查出是否有 race condition

```shell
$ go run -race main.go
==================
WARNING: DATA RACE
Read at 0x00c00009e010 by goroutine 8:
  main.main.func1()
      .../main.go:15 +0x6f

Previous write at 0x00c00009e010 by goroutine 7:
  main.main.func1()
      .../main.go:15 +0x85

Goroutine 8 (running) created at:
  main.main()
      .../main.go:31 +0xf4

Goroutine 7 (finished) created at:
  main.main()
      .../main.go:31 +0xf4
==================
996000
Found 1 data race(s)
exit status 66
```

喔喔喔發現原來有 [race condition](https://zh.wikipedia.org/wiki/競爭危害)， 因為同時去對 Bank.balance 去做存取的動作，數量少的時候可能沒問題，當量大的時候就可能出錯。

## sync.Mutex

為了防止這種狀況發生，就可以用[互斥鎖](https://zh.wikipedia.org/wiki/互斥鎖) `sync.Mutex` 來處理這個問題，同時間只有一個 goroutine 能存取該變數。

這次我們在 `Deposit()` 存款前先 `Lock()`，存款後再 `Unlock()`。

```go
type Bank struct {
    balance int
    mux     sync.Mutex
}

func (b *Bank) Deposit(amount int) {
    b.mux.Lock()
    b.balance += amount
    b.mux.Unlock()
}

func (b *Bank) Balance() int {
    return b.balance
}
$ go run -race main.go
1000000
```

這次結果正確了，而且也沒跳出 race condition 的警訊。

## 同時存款和查詢

想當然會有多人一起存款，就會有多人一起查詢餘額。~~也會有多人一起運動~~

多加一組查詢 1000 次的 goroutine 再執行看看。

```go
func main() {
    var wg sync.WaitGroup

    b := &Bank{}

    n := 1000
    wg.Add(n)
    for i := 1; i <= n; i++ {
        go func() {
            b.Deposit(1000)
            wg.Done()
        }()
    }
    wg.Add(n)
    for i := 1; i <= n; i++ {
        go func() {
            _ = b.Balance()
            wg.Done()
        }()
    }

    wg.Wait()

    fmt.Println(b.Balance())
}
$ go run -race main.go
==================
WARNING: DATA RACE
Read at 0x00c0000180e0 by goroutine 59:
  main.main.func2()
      .../main.go:22 +0x6f

Previous write at 0x00c0000180e0 by goroutine 58:
  main.(*Bank).Deposit()
      .../main.go:15 +0x70
  main.main.func1()
      .../main.go:35 +0x75

Goroutine 59 (running) created at:
  main.main()
      .../main.go:40 +0x153

Goroutine 58 (finished) created at:
  main.main()
      .../main.go:33 +0xf4
==================
==================
WARNING: DATA RACE
Read at 0x00c0000180e0 by goroutine 60:
  main.main.func2()
      .../main.go:22 +0x6f

Previous write at 0x00c0000180e0 by goroutine 58:
  main.(*Bank).Deposit()
      .../main.go:15 +0x70
  main.main.func1()
      .../main.go:35 +0x75

Goroutine 60 (running) created at:
  main.main()
      .../main.go:40 +0x153

Goroutine 58 (finished) created at:
  main.main()
      .../main.go:33 +0xf4
==================
1000000
Found 2 data race(s)
exit status 66
```

不意外，因為同時對 balance 去做讀寫，當然跳出 race condition 的警告。

我們一樣在 Balance() 加上 `Lock()` 和 `Unlock()` 後執行。

```go
type Bank struct {
    balance int
    mux     sync.Mutex
}

func (b *Bank) Deposit(amount int) {
    b.mux.Lock()
    b.balance += amount
    b.mux.Unlock()
}

func (b *Bank) Balance() (balnce int) {
    b.mux.Lock()
    balance = b.balance
    b.mux.Unlock()
    return 
}
$ go run -race main.go
1000000
```

結果成功了，也沒有 race 的警告了。

## 讀寫互相阻塞

目前這邊看起來都還不錯，但以現在的情況來說，只要有人讀，或只要有人寫，就會被 block。

假如銀行存款和查詢各要上花一秒：

```go
package main

import (
    "log"
    "sync"
    "time"
)

type Bank struct {
    balance int
    mux     sync.Mutex
}

func (b *Bank) Deposit(amount int) {
    b.mux.Lock()
    time.Sleep(time.Second) // spend 1 second
    b.balance += amount
    b.mux.Unlock()
}

func (b *Bank) Balance() (balance int) {
    b.mux.Lock()
    time.Sleep(time.Second) // spend 1 second
    balance = b.balance
    b.mux.Unlock()
    return 
}

func main() {
    var wg sync.WaitGroup
    b := &Bank{}

    n := 5
    wg.Add(n)
    for i := 1; i <= n; i++ {
        go func() {
            b.Deposit(1000)
            log.Printf("Write: deposit amonut: %v", 1000)
            wg.Done()
        }()
    }
    wg.Add(n)
    for i := 1; i <= n; i++ {
        go func() {
            log.Printf("Read: balance: %v", b.Balance())
            wg.Done()
        }()
    }

    wg.Wait()
}
$ go run -race main.go
2020/05/02 02:11:24 Write: deposit amonut: 1000
2020/05/02 02:11:25 Write: deposit amonut: 1000
2020/05/02 02:11:26 Write: deposit amonut: 1000
2020/05/02 02:11:27 Write: deposit amonut: 1000
2020/05/02 02:11:28 Write: deposit amonut: 1000
2020/05/02 02:11:29 Read: balance: 5000
2020/05/02 02:11:30 Read: balance: 5000
2020/05/02 02:11:31 Read: balance: 5000
2020/05/02 02:11:32 Read: balance: 5000
2020/05/02 02:11:33 Read: balance: 5000
```

就會發現，每隔一秒才能處理一個 action，以各五次讀寫來說，總共就要花上 10 秒，但對讀來說，應該可以瘋狂讀，每次讀都會是安全的， 值也都會是一樣，除非當下有寫的動作，它不應該被其他讀的動作 block。

## sync.RWMutex

`sync.RWMutex` 是一個[讀寫鎖](https://zh.wikipedia.org/wiki/讀寫鎖)(multiple readers, single writer lock)，多讀單寫，可以允許多個讀並發，單個寫。

把 `sync.Mutex` 換成 `sync.RWMutex`：

```go
type Bank struct {
    balance int
    mux     sync.RWMutex    // read write lock
}

func (b *Bank) Deposit(amount int) {
    b.mux.Lock()            // write lock
    time.Sleep(time.Second)
    b.balance += amount
    b.mux.Unlock()          // wirte unlock
}

func (b *Bank) Balance() (balance int) {
    b.mux.RWLock()          // read lock
    time.Sleep(time.Second)
    balance = b.balance
    b.mux.RWUnlock()        // read unlock
    return 
}
$ go run -race main.go
2020/05/02 02:13:59 Write: deposit amonut: 1000
2020/05/02 02:14:00 Read: balance: 1000
2020/05/02 02:14:00 Read: balance: 1000
2020/05/02 02:14:00 Read: balance: 1000
2020/05/02 02:14:00 Read: balance: 1000
2020/05/02 02:14:00 Read: balance: 1000
2020/05/02 02:14:01 Write: deposit amonut: 1000
2020/05/02 02:14:02 Write: deposit amonut: 1000
2020/05/02 02:14:03 Write: deposit amonut: 1000
2020/05/02 02:14:04 Write: deposit amonut: 1000
```

執行之後會發現，本來要花 10 秒，已經縮短成 5 秒了，只要當下是讀的時候，都會同時進行，並不會互相影響，寫的時候就會 block 讀和寫，只有一個寫會發生。

## 總結

1. 在寫 goroutine 的時候，需要考慮 race condition，在執行或測試上可以加上 `-race` 去檢查，以免結果與預期不符
2. 遇到 race condition 的時候可以考慮用 `sync.Mutex` 來解決，有讀寫阻塞的時候可以用 `sync.RWMutex`
3. `syncRWMutex` 可以有同時允許多個 `RLock` 和 `RUnlock` 但只能有一個 `Lock` 和 `Unlock`