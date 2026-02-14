// trace-demo: 示範如何使用 go tool trace 產生追蹤檔案並分析
package main

import (
	"fmt"
	"os"
	"runtime/trace"
	"sync"
)

func main() {
	// 建立追蹤輸出檔案
	f, err := os.Create("trace.out")
	if err != nil {
		fmt.Fprintf(os.Stderr, "建立 trace 檔案失敗: %v\n", err)
		os.Exit(1)
	}
	defer f.Close()

	// 開始追蹤
	if err := trace.Start(f); err != nil {
		fmt.Fprintf(os.Stderr, "啟動 trace 失敗: %v\n", err)
		os.Exit(1)
	}
	defer trace.Stop()

	fmt.Println("開始追蹤，執行並行計算...")

	// 模擬一些並行工作
	const numGoroutines = 8
	const workPerGoroutine = 1_000_000

	var wg sync.WaitGroup
	results := make([]int64, numGoroutines)

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			var sum int64
			for j := 0; j < workPerGoroutine; j++ {
				sum += int64(j * id)
			}
			results[id] = sum
		}(i)
	}

	wg.Wait()

	var total int64
	for _, r := range results {
		total += r
	}

	fmt.Printf("計算完成，總和: %d\n", total)
	fmt.Println("追蹤檔案已寫入 trace.out")
	fmt.Println("使用以下指令開啟 Trace UI:")
	fmt.Println("  go tool trace trace.out")
}
