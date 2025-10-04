當一個計算任務被goroutine承接了之後，由於超時等原因退出的時候，我們希望中止這個goroutine的計算任務。 這個時候可能就需要用到context了。

> 如果不需要為goroutine設置超時，也不需要手工取消執行。只是等待goroutine自己結束的話，只需要WaitGroup即可，不需要context。

# 超時退出
設置context的超時時間
```go
ctx, cancel := context.WithTimeout(context.Background(), 1*time.Second)
```

定義一個協程函數
```go
func handle(ctx context.Context) {
	ch := make(chan struct{}, 0)
	go func() {
		// 模擬4秒耗時任務
		time.Sleep(time.Second * 2)
		ch <- struct{}{}
	}()
	select {
	case <-ch:
		fmt.Println("done")
	case <-ctx.Done():
		fmt.Println("timeout")
	}
}
```

在創建goroutine的時候把上面返回的context傳入到協程中，並讓主協程多等待一會兒。
```go
go handle(ctx)
time.Sleep(time.Second * 5)
```

運行後輸出
```go
sub routine timeout
main routine end
```

# context.Background 與 context.TODO
我們查看一下源碼
```go
var (
	background = new(emptyCtx)
	todo       = new(emptyCtx)
)
func Background() Context {
	return background
}
func TODO() Context {
	return todo
}
```

從源代碼來看，context.Background 和 context.TODO 沒有太大的差別。它們只是在使用和語義上稍有不同：

- context.Background 是上下文的默認值，所有其他的上下文都應該從它衍生（Derived）出來；
- context.TODO 應該只在不確定應該使用哪種上下文時使用；

在多數情況下，如果當前函數沒有上下文作為入參，我們都會使用 context.Background 作為起始的上下文向下傳遞。

# 取消
除了超時以外，當最上層的 Goroutine 因為某些原因執行失敗時，一般也需要將其下面的協程都退出掉。
這時也可以使用context，可以使用context.WithCancel函數，這裡就不多舉例子了。






