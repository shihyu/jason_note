// gc-pressure: 示範並行化後 GC 壓力增加的問題
// 對比不同 GOGC 和 GOMEMLIMIT 設定的效果
package main

import (
	"fmt"
	"runtime"
	"runtime/debug"
	"sync"
	"time"
)

// 模擬產生大量短暫物件的工作
func doAllocWork(n int) []byte {
	result := make([]byte, 0, 1024)
	for i := 0; i < n; i++ {
		// 每次迭代都分配一小塊記憶體（模擬真實應用）
		tmp := make([]byte, 256)
		tmp[0] = byte(i)
		result = append(result, tmp[0])
	}
	return result
}

// 單執行緒版本
func runSequential(totalWork int) time.Duration {
	start := time.Now()
	_ = doAllocWork(totalWork)
	return time.Since(start)
}

// 並行版本
func runParallel(totalWork, numWorkers int) time.Duration {
	start := time.Now()
	var wg sync.WaitGroup
	workPerWorker := totalWork / numWorkers

	for i := 0; i < numWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			_ = doAllocWork(workPerWorker)
		}()
	}
	wg.Wait()
	return time.Since(start)
}

// 使用 goroutine pool 的版本
func runWithPool(totalWork, poolSize int) time.Duration {
	start := time.Now()
	jobs := make(chan int, poolSize)
	var wg sync.WaitGroup

	// 啟動 worker pool
	for i := 0; i < poolSize; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for n := range jobs {
				_ = doAllocWork(n)
			}
		}()
	}

	// 發送工作：分成多個小批次
	batchSize := totalWork / 100
	for sent := 0; sent < totalWork; sent += batchSize {
		remaining := totalWork - sent
		if remaining < batchSize {
			batchSize = remaining
		}
		jobs <- batchSize
	}
	close(jobs)
	wg.Wait()
	return time.Since(start)
}

func printGCStats(label string) {
	var stats debug.GCStats
	debug.ReadGCStats(&stats)
	var memStats runtime.MemStats
	runtime.ReadMemStats(&memStats)

	fmt.Printf("  [%s] GC 次數: %d, 暫停總時間: %v, 堆記憶體: %.2f MiB\n",
		label,
		stats.NumGC,
		stats.PauseTotal,
		float64(memStats.HeapAlloc)/(1024*1024),
	)
}

func main() {
	fmt.Println("=== GC 壓力與並行化分析 ===")
	fmt.Printf("GOMAXPROCS: %d\n\n", runtime.GOMAXPROCS(0))

	const totalWork = 500_000
	numCPU := runtime.GOMAXPROCS(0)

	// 測試 1：單執行緒
	runtime.GC()
	printGCStats("開始前")
	d := runSequential(totalWork)
	printGCStats("單執行緒結束")
	fmt.Printf("  耗時: %v\n\n", d)

	// 測試 2：並行（每個 CPU 一個 goroutine）
	runtime.GC()
	printGCStats("開始前")
	d = runParallel(totalWork, numCPU)
	printGCStats("並行結束")
	fmt.Printf("  耗時: %v\n\n", d)

	// 測試 3：Goroutine Pool
	runtime.GC()
	printGCStats("開始前")
	d = runWithPool(totalWork, numCPU)
	printGCStats("Pool 結束")
	fmt.Printf("  耗時: %v\n\n", d)

	// 測試 4：調整 GOGC 後再跑並行
	fmt.Println("--- 調整 GOGC=200 後重測並行 ---")
	oldGOGC := debug.SetGCPercent(200)
	runtime.GC()
	printGCStats("開始前")
	d = runParallel(totalWork, numCPU)
	printGCStats("GOGC=200 並行結束")
	fmt.Printf("  耗時: %v\n\n", d)
	debug.SetGCPercent(oldGOGC)

	// 測試 5：設定 GOMEMLIMIT
	fmt.Println("--- 設定 GOMEMLIMIT=512MiB 後重測並行 ---")
	debug.SetMemoryLimit(512 * 1024 * 1024) // 512 MiB
	runtime.GC()
	printGCStats("開始前")
	d = runParallel(totalWork, numCPU)
	printGCStats("GOMEMLIMIT=512MiB 並行結束")
	fmt.Printf("  耗時: %v\n", d)
}
