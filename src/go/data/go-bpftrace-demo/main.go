package main

import (
	"fmt"
	"time"
)

//go:noinline
func Step1(msg string) {
	fmt.Println("執行步驟 1:", msg)
}

//go:noinline
func Step2(count int) {
	fmt.Println("執行步驟 2，次數:", count)
}

// Allocate 明確觸發 runtime.mallocgc，供 bpftrace 觀察 heap 分配
//
//go:noinline
func Allocate(n int) []byte {
	buf := make([]byte, n)
	fmt.Printf("分配記憶體: %d bytes\n", n)
	return buf
}

// Worker 在獨立 goroutine 執行，觸發 runtime.newproc 可被觀察
//
//go:noinline
func Worker() {
	fmt.Println("Worker goroutine 執行中")
}

func main() {
	// 啟動背景 goroutine，觸發 runtime.newproc
	go func() {
		for {
			Worker()
			time.Sleep(3 * time.Second)
		}
	}()

	for {
		Step1("Hello")
		Step2(42)
		_ = Allocate(256) // 觸發 runtime.mallocgc
		time.Sleep(2 * time.Second)
	}
}
