// Go 並行程式設計範例 01: Goroutine 基礎
// 展示基本的 Goroutine 創建和使用方式

package main

import (
	"fmt"
	"runtime"
	"sync"
	"time"
)

func main() {
	fmt.Println("=== Goroutine 基礎範例 ===")
	fmt.Printf("CPU 核心數: %d\n", runtime.NumCPU())
	fmt.Printf("當前 Goroutine 數: %d\n", runtime.NumGoroutine())

	var wg sync.WaitGroup

	// 啟動多個 goroutine
	for i := 1; i <= 5; i++ {
		wg.Add(1)
		go worker(i, &wg)
	}

	fmt.Println("等待所有 Goroutine 完成...")
	wg.Wait()
	fmt.Printf("完成後 Goroutine 數: %d\n", runtime.NumGoroutine())
	fmt.Println("✅ 所有任務完成")
}

func worker(id int, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Printf("🔄 Worker %d 開始執行\n", id)

	// 模擬不同的工作負載
	for j := 1; j <= 3; j++ {
		fmt.Printf("   Worker %d 執行第 %d 次任務\n", id, j)
		time.Sleep(time.Duration(100+id*50) * time.Millisecond)
	}

	fmt.Printf("✅ Worker %d 完成所有任務\n", id)
}
