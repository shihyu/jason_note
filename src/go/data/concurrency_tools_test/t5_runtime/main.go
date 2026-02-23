package main

import (
	"fmt"
	"runtime"
)

func printStats() {
	fmt.Println("Goroutine 數量:", runtime.NumGoroutine())
	fmt.Println("CPU 核心數:", runtime.NumCPU())
	fmt.Println("GOMAXPROCS:", runtime.GOMAXPROCS(0))

	var ms runtime.MemStats
	runtime.ReadMemStats(&ms)
	fmt.Printf("Heap 使用: %v MB\n", ms.HeapAlloc/1024/1024)
}

func main() {
	printStats()
}
