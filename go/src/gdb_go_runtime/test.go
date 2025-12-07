package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("Hello, GDB!")

	// 創建 channel
	ch := make(chan int, 2)

	// 啟動 goroutine
	go worker(ch, 1)
	go worker(ch, 2)

	// 發送數據到 channel
	ch <- 100
	ch <- 200

	// 等待一下讓 goroutine 執行
	time.Sleep(time.Second)

	fmt.Println("Main finished")
}

func worker(ch chan int, id int) {
	val := <-ch
	fmt.Printf("Worker %d received: %d\n", id, val)
}
