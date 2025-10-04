
在 Go 語言中，每一個併發的執行單元叫作一個 goroutine，goroutine 的概念類似於線程，屬於用戶態的線程, 是由 Go 的運行時（runtime）調度和管理的。

每一個 OS 線程都有一個固定大小的內存塊(一般會是2MB)來做棧，這個棧會用來存儲當前正在被調用或掛起(指在調用其它函數時)的函數的內部變量。相反，一個 goroutine 會以一個很小的棧開始其生命週期，一般只需要 2KB。一個 goroutine 的棧，和操作系統線程一樣，會保存其活躍或掛起的函數調用的本地變量，但是和 OS 線程不太一樣的是一個 goroutine 的棧大小並不是固定的；棧的大小會根據需要動態地伸縮。而 goroutine 的棧的最大值有 1GB，比傳統的固定大小的線程棧要大得多，儘管一般情況下，大多 goroutine 都不需要這麼大的棧。

## 使用

Go 語言中使用 goroutine 非常簡單，只需要在調用函數或方法的時候在前面加上 go 關鍵字，就可以為一個函數創建一個 goroutine。當一個程序啟動時，其 main() 函數即在一個單獨的 goroutine 中運行，我們叫它 main goroutine，儘管它並沒有通過 go 來啟動。

不過由於主線程有可能先於 hello 協程退出，先用最簡單的辦法，sleep 一秒等待輸出。

```go
func hello(){
	fmt.Println("Hello")
}

func main(){
	go hello()
	time.Sleep(1)
}
```

## 調度
GPM 是 Go 語言運行時（runtime）層面的實現，是 go 語言自己實現的一套調度系統。區別於操作系統調度 OS 線程。

- G: Gourtines, 每個 Goroutine 對應一個 G 結構體，G 保存 Goroutine 的運行堆棧，即併發任務狀態。G 並非執行體，每個 G 需要綁定到P才能被調度執行。
- P: Processors, 對 G 來說，P 相當於 CPU 核，G 只有綁定到 P(在P的 local runq 中)才能被調度。對M來說，P 提供了相關的執行環境(Context)，如內存分配狀態(mcache)，任務隊列(G)等，P 會對自己管理的 goroutine 隊列做一些調度（比如把佔用 CPU 時間較長的 goroutine 暫停、運行後續的 goroutine 等等）當自己的隊列消費完了就去全局隊列裡取，如果全局隊列裡也消費完了會去其他P的隊列裡搶任務。
- M（machine）是 Go 運行時（runtime）對操作系統內核線程的抽象， M 與內核線程一般是一一映射的關係， 一個 groutine 最終是要放到M上執行的； P 與 M 一般也是一一對應的。他們關係是： P 管理著一組 G 掛載在 M 上運行。當一個 G 長久阻塞在一個 ，runtime 會新建一個 M，阻塞 G 所在的 P 會把其他的 G 掛載在新建的 M 上。當舊的 G 阻塞完成或者認為其已經死掉時 回收舊的 M。

P 的個數是通過 runtime.GOMAXPROCS 設定（最大256），Go 1.5版本之後默認為物理線程數。
M 的個數是不定的，由 Go Runtime 調整，默認最大限制為 10000 個。