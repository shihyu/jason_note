
select 可同時監聽多個channel的讀/寫，執行 select 時，若只有一個 case 通過，則執行該 case。

```go
select {
    case i := <-ch1:
        fmt.Println("Worker1 job done", i)
    case j := <-ch2:
    ...
}
```

通過通道返回的第二個參數可以感知到通道的關閉

```go
select {
    ...
    case _, ok := <-ch3:
        if ok {
            fmt.Println("Finish all job")
            return
        }
    }
```