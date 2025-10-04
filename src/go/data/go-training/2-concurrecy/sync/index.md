## waitgroup
藉助標準庫 sync 裡的 Waitgroup，可以實現優雅等待所有子 goroutine 完全結束之後主進程才結束退出，這是一種控制併發的方式，可以實現對多 goroutine 的等待。

```go
var wait sync.WaitGroup

func worker(){
	fmt.Println("Worker is working!")
	wait.Done()
}

func main(){
	wait.Add(1)
	go worker()
	wait.Wait()
}
```

## 互斥鎖
互斥鎖是完全互斥的，兩個協程不能進入同一塊加鎖的區域

```go
//定義鎖
lock sync.Mutex

//加鎖
lock.Lock()

//解鎖
lock.Unlock()
```

### 讀寫鎖
```go
//定義鎖
rwlock sync.RWMutex

//加寫鎖
rwlock.Lock()

//解寫鎖
rwlock.Unlock()

//加讀鎖
rwlock.RLock()

//加讀鎖
rwlock.RUnLock()
```
