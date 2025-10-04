goroutine 之間可以通過 channel 來交換數據

Go 語言中的通道（channel）是一種特殊的類型。通道像一個傳送帶或者隊列，總是遵循先入先出（First In First Out）的規則，保證收發數據的順序。每一個通道都是一個具體類型的導管，也就是聲明channel的時候需要為其指定元素類型。

## 無緩存的通道
```go
//創建無緩存的通道
c1 := make(chan int)

//嘗試讀取，沒有數據就會被阻塞
<-c1

//嘗試寫入，沒有人接收也會被阻塞
c1 <- 100
```

## 有緩存的通道
緩衝滿載（發送）或變空（接收）之前通信不會阻塞，當滿了以後會阻塞掉。

```go
func main() {
	//有緩存的 channel
	c1 := make(chan int, 10)
}
```

## forrange遍歷channel
使用 forrange 遍歷 channel 很方便，當 channel 被 close 的時候，forrange 會自動退出。

```go
for i := range c {
    fmt.Println(i)
}
```
