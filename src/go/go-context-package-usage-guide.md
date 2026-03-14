# 用 10 分鐘了解 Go 語言 `context` package 的使用場景

![Golang Logo](images/go-context-package-logo.png)

[context](https://pkg.go.dev/context) 在 Go 1.7 才正式納入標準函式庫。初學 Go、開始撰寫 API 或處理併發程式時，常會在 `http handler` 或 service function 的第一個參數看到：

```go
ctx context.Context
```

這個 `context` 到底是做什麼用的？這篇文章會用幾個實際例子，快速說明 `context` 的用途、常見場景，以及它與 `WaitGroup`、`channel` 的差異。本文不會深入原始碼，而是聚焦在日常開發中的實際使用方式。

## 教學影片

如果你對課程內容有興趣，可以參考以下資源：

- [Go 語言基礎實戰（開發、測試及部署）](https://www.udemy.com/course/golang-fight/?couponCode=202004)
- [一天學會 DevOps 自動化測試及部署](https://www.udemy.com/course/devops-oneday/?couponCode=202004)
- [DOCKER 容器開發部署實戰](https://www.udemy.com/course/docker-practice/?couponCode=202004)

如果需要搭配購買，請直接透過 [FB 聯絡我](http://facebook.com/appleboy46)。

## 使用 `WaitGroup`

學 Go 時一定會碰到 goroutine，而 goroutine 的協調方式常見有兩種：一種是 [WaitGroup](https://pkg.go.dev/sync#WaitGroup)，另一種是 `context`。

那什麼時候該用 `WaitGroup`？很簡單，當你把同一件事拆成多個 job 並行執行，而且主程式必須等所有 job 都完成之後才能繼續，這時候就很適合使用 `WaitGroup`。

```go
package main

import (
	"fmt"
	"sync"
	"time"
)

func main() {
	var wg sync.WaitGroup

	wg.Add(2)

	go func() {
		time.Sleep(2 * time.Second)
		fmt.Println("job 1 done.")
		wg.Done()
	}()

	go func() {
		time.Sleep(1 * time.Second)
		fmt.Println("job 2 done.")
		wg.Done()
	}()

	wg.Wait()
	fmt.Println("all done.")
}
```

上面的例子中，主程式透過 `wg.Wait()` 等待所有 job 執行完成，最後才印出訊息。

不過會有另一種情境：工作雖然拆成多個 job 丟到背景執行，但如果使用者想透過 UI 上的「停止」按鈕，或透過其他外部事件主動終止正在執行的 goroutine，該怎麼做？這時可以先用 `channel + select` 來處理。

## 使用 `channel + select`

```go
package main

import (
	"fmt"
	"time"
)

func main() {
	stop := make(chan bool)

	go func() {
		for {
			select {
			case <-stop:
				fmt.Println("got the stop channel")
				return
			default:
				fmt.Println("still working")
				time.Sleep(1 * time.Second)
			}
		}
	}()

	time.Sleep(5 * time.Second)
	fmt.Println("stop the goroutine")
	stop <- true
	time.Sleep(5 * time.Second)
}
```

透過 `select + channel`，可以很直接地通知背景 goroutine 停止工作。只要在任何地方把值送進 `stop channel`，背景工作就會收到訊號並結束。

但如果背景不只一個 goroutine，而是很多個 goroutine，甚至 goroutine 裡面還會再啟動新的 goroutine，事情就會變得很複雜。像下圖這種層層展開的 worker 結構，就不太適合只靠單一 `channel` 來管理：

![Context Cancel Flow](images/go-context-package-cancel-flow.png)

這時候就輪到 `context` 登場了。

## 使用 `context`

從上圖可以看到，主程式先建立一個根 `context.Background()`，接著讓每個 worker 依照需要延伸出自己的子 context。這樣一來，只要取消某個 context，就能讓該 context 之下的工作一併收到停止通知。

先把前面的 `channel` 範例改寫成 `context`：

```go
package main

import (
	"context"
	"fmt"
	"time"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	go func() {
		for {
			select {
			case <-ctx.Done():
				fmt.Println("got the stop channel")
				return
			default:
				fmt.Println("still working")
				time.Sleep(1 * time.Second)
			}
		}
	}()

	time.Sleep(5 * time.Second)
	fmt.Println("stop the goroutine")
	cancel()
	time.Sleep(5 * time.Second)
}
```

可以看到，邏輯幾乎沒變，只是把原本的 `stop channel` 改成監聽 `ctx.Done()`。而這裡最關鍵的是：

```go
ctx, cancel := context.WithCancel(context.Background())
```

`context.WithCancel` 會回傳一個新的 `context`，以及對應的 `cancel func`。這代表每個 worker 都可以有自己的取消控制點，開發者能在合適的地方呼叫 `cancel()`，決定要停止哪一段工作。

## 一次停止多個 worker

下面這個範例示範如何用同一個 `context` 同步停止多個 worker：

```go
package main

import (
	"context"
	"fmt"
	"time"
)

func main() {
	ctx, cancel := context.WithCancel(context.Background())

	go worker(ctx, "node01")
	go worker(ctx, "node02")
	go worker(ctx, "node03")

	time.Sleep(5 * time.Second)
	fmt.Println("stop the goroutine")
	cancel()
	time.Sleep(5 * time.Second)
}

func worker(ctx context.Context, name string) {
	for {
		select {
		case <-ctx.Done():
			fmt.Println(name, "got the stop channel")
			return
		default:
			fmt.Println(name, "still working")
			time.Sleep(1 * time.Second)
		}
	}
}
```

透過同一個 `context`，可以一次停止多個 worker。實務上我通常會把這種模式搭配 graceful shutdown 一起使用，例如停止背景 job、關閉資料庫連線，或中止正在等待的外部請求。

## 心得

剛開始學 Go、還不常用 goroutine 時，通常很難立刻理解 `context` 的價值。等到你開始寫背景工作、需要控制生命週期，或要處理一整串可以被取消的流程時，就會慢慢體會到 `context` 的重要性。

當然，`context` 不只用在取消工作，也常拿來傳遞 deadline、timeout 與 request-scoped value。這些主題之後還可以再分開深入討論。

## 延伸閱讀

- [用 Google 團隊推出的 Wire 工具解決 Dependency Injection](https://blog.wu-boy.com/2022/09/dependency-injection-in-go/)
- [三種好用的 gRPC 測試工具](https://blog.wu-boy.com/2022/08/three-grpc-testing-tool/)
- [監控服務 Gatus 系統架構](https://blog.wu-boy.com/2022/07/gatus-system-architecture/)
- [在 Go 語言測試使用 Setup 及 Teardown](https://blog.wu-boy.com/2022/07/setup-and-teardown-with-unit-testing-in-golang/)
- [優化重構 Worker Pool 程式碼](https://blog.wu-boy.com/2022/06/refactor-worker-pool-source-code/)
- [在 Go 語言內使用 bytes.Buffer 注意事項](https://blog.wu-boy.com/2022/06/reuse-the-bytes-buffer-in-go/)
- [用 10 分鐘了解 Go 語言如何從 Channel 讀取資料](https://blog.wu-boy.com/2022/05/read-data-from-channel-in-go/)
- [用 Go 語言實作 Pub-Sub 模式](https://blog.wu-boy.com/2022/04/simple-publish-subscribe-pattern-in-golang/)
- [Go 語言實作 Graceful Shutdown 套件](https://blog.wu-boy.com/2022/04/new-package-graceful-shutdown-in-golang/)
- [使用 AWS IAM Policy 設定 S3 Bucket 底下特定目錄權限](https://blog.wu-boy.com/2022/04/grant-access-to-user-specific-folders-in-amazone-s3-bucket/)
