# defer 語句
defer 是G o語言提供的一種用於註冊延遲調用的機制：讓函數或語句可以在當前函數執行完畢後（包括通過 return 正常結束或者 panic 導致的異常結束）執行，它會經常被用於關閉文件描述符、關閉數據庫連接以及解鎖資源等。

```go  
func main() {
	fmt.Println("start")
	for i := 0; i < 5; i++ {
		defer fmt.Println(i)
	}
	fmt.Println("end")
	
	/*
	輸出結果:
	start
    end
    4
    3
    2
    1
    0
}
```

defer 後面跟的內容除了可以是一行語句以外，也可以是一個函數/匿名函數。

```go  
func closeAll() {
	fmt.Println("close all 1 !")
}
func main() {
	fmt.Println("start")
	defer closeAll()
	defer func() { fmt.Println("close all 2") }()
	fmt.Println("end")
}
```
輸出結果
```go

```

# panic 
當一個函數在執行過程中出現了異常或遇到
panic()，正常語句就會立即終止，然後執行 defer 語句，再報告異
常信息，最後退出 goroutine。如果在 defer 中使用了 recover()
函數,則會捕獲錯誤信息，使該錯誤信息終止報告。

```go  
func main() {
	fmt.Println("start")
	defer func() { fmt.Println("close all") }()
	panic("ERROR")
	fmt.Println("end")
}
```
輸出結果為
```go  
start
close all
panic: ERROR

goroutine 1 [running]:
main.main()
        /Users/zhangyanfei/work_go/go-training/2-code-organize/defer/main.go:12 +0xb7

Process finished with exit code 2

```
注意：panic 只會觸發當前 Goroutine 的延遲函數調用；

# recover
recover 只有在 defer 函數中調用才會生效

```go  
fmt.Println("start")
defer func() {
    if r := recover(); r != nil {
        fmt.Println("Recovered in f", r)
    }
}()
panic("ERROR")
fmt.Println("end")
```

panic之後雖然end同樣沒有輸出，但是和沒有recover的demo相比，程序並沒有異常退出。

```go  
start
Recovered in f ERROR

Process finished with exit code 0
```
