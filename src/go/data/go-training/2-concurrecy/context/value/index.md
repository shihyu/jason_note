
context 的很重要的一個作用是在各個子 routine 之間傳遞一些共享值，例如用戶的 id。

使用 context.WithValue 創建一個值節點，並把它們鏈接到樹形結構中。

```go
func main() {
	ctx := context.WithValue(context.Background(), "userid", "1234567")
}
```

只要能獲取到該 ctx 的協程都可以獲取到該值。

```go
func Handler(ctx context.Context) {
	fmt.Println(ctx.Value("userid"))
	wg.Done()
}
func main() {
	ctx := context.WithValue(context.Background(), "userid", "1234567")
	wg.Add(1)
	go Handler(ctx)
	wg.Wait()
}
```

值得注意，如果 ctx 最終穿起來是一個樹形結構。所以所有該 ctx 派生的 context 上執行 WithValue 都能獲取到該值。
詳細例子參見