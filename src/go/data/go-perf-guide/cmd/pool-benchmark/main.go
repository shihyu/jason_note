// pool-benchmark: 對比 goroutine-per-task vs worker pool 的效能差異
// 重點展示：pool 不一定更快，特別是在低延遲場景
package main

import (
	"fmt"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

// 模擬一個輕量計算任務
func lightWork(n int) int64 {
	var sum int64
	for i := 0; i < n; i++ {
		sum += int64(i)
	}
	return sum
}

// 方式 1: 每個任務啟動一個新的 goroutine
func goroutinePerTask(tasks int, workSize int) (time.Duration, int64) {
	start := time.Now()
	var total atomic.Int64
	var wg sync.WaitGroup

	for i := 0; i < tasks; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			result := lightWork(workSize)
			total.Add(result)
		}()
	}

	wg.Wait()
	return time.Since(start), total.Load()
}

// 方式 2: 使用固定大小的 worker pool
func workerPool(tasks int, workSize int, poolSize int) (time.Duration, int64) {
	start := time.Now()
	var total atomic.Int64
	var wg sync.WaitGroup
	jobs := make(chan struct{}, poolSize)

	for i := 0; i < tasks; i++ {
		wg.Add(1)
		jobs <- struct{}{} // 限制並行度
		go func() {
			defer wg.Done()
			result := lightWork(workSize)
			total.Add(result)
			<-jobs // 釋放 slot
		}()
	}

	wg.Wait()
	return time.Since(start), total.Load()
}

// 方式 3: 真正的 worker pool（預先建立 goroutine）
func fixedWorkerPool(tasks int, workSize int, poolSize int) (time.Duration, int64) {
	start := time.Now()
	var total atomic.Int64
	var wg sync.WaitGroup
	taskCh := make(chan struct{}, tasks)

	// 預先啟動固定數量的 worker
	for i := 0; i < poolSize; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for range taskCh {
				result := lightWork(workSize)
				total.Add(result)
			}
		}()
	}

	// 發送所有任務
	for i := 0; i < tasks; i++ {
		taskCh <- struct{}{}
	}
	close(taskCh)

	wg.Wait()
	return time.Since(start), total.Load()
}

func main() {
	fmt.Println("=== Goroutine Pool vs Per-Task Goroutine 效能比較 ===")
	fmt.Printf("GOMAXPROCS: %d\n\n", runtime.GOMAXPROCS(0))

	poolSize := runtime.GOMAXPROCS(0)

	scenarios := []struct {
		name     string
		tasks    int
		workSize int
	}{
		{"輕量任務 (100 次迴圈)", 10000, 100},
		{"中等任務 (10000 次迴圈)", 10000, 10000},
		{"重量任務 (100000 次迴圈)", 1000, 100000},
	}

	for _, s := range scenarios {
		fmt.Printf("--- %s (任務數: %d) ---\n", s.name, s.tasks)

		// Goroutine per task
		d1, r1 := goroutinePerTask(s.tasks, s.workSize)
		fmt.Printf("  每任務一個 goroutine:   %v\n", d1)

		// Semaphore-style pool
		d2, r2 := workerPool(s.tasks, s.workSize, poolSize)
		fmt.Printf("  Semaphore 限制池:       %v\n", d2)

		// Fixed worker pool
		d3, r3 := fixedWorkerPool(s.tasks, s.workSize, poolSize)
		fmt.Printf("  固定 Worker Pool:       %v\n", d3)

		// 驗證結果一致
		if r1 != r2 || r2 != r3 {
			fmt.Printf("  ⚠️ 結果不一致: %d vs %d vs %d\n", r1, r2, r3)
		}
		fmt.Println()
	}

	fmt.Println("結論:")
	fmt.Println("  - 輕量任務時，pool 的 channel 通訊開銷可能超過 goroutine 建立成本")
	fmt.Println("  - 重量任務時，pool 通常沒有明顯優勢（goroutine 建立成本佔比小）")
	fmt.Println("  - Pool 的真正價值在於「控制資源使用」而非單純加速")
}
