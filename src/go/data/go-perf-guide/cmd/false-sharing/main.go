// false-sharing: 示範 False Sharing 問題及解決方案
package main

import (
	"fmt"
	"sync"
	"testing"
	"time"
	"unsafe"
)

// ❌ 有 False Sharing 問題的結構
type ResultBad struct {
	sumA int64 // sumA 和 sumB 在同一條 cache line 上
	sumB int64
}

// ✅ 用 padding 解決 False Sharing
type ResultGood struct {
	sumA int64
	_    [56]byte // 填充到 64 bytes（一條 cache line）
	sumB int64
}

type Input struct {
	a int64
	b int64
}

func countBad(inputs []Input) ResultBad {
	var wg sync.WaitGroup
	wg.Add(2)
	result := ResultBad{}

	go func() {
		for i := 0; i < len(inputs); i++ {
			result.sumA += inputs[i].a
		}
		wg.Done()
	}()

	go func() {
		for i := 0; i < len(inputs); i++ {
			result.sumB += inputs[i].b
		}
		wg.Done()
	}()

	wg.Wait()
	return result
}

func countGood(inputs []Input) ResultGood {
	var wg sync.WaitGroup
	wg.Add(2)
	result := ResultGood{}

	go func() {
		for i := 0; i < len(inputs); i++ {
			result.sumA += inputs[i].a
		}
		wg.Done()
	}()

	go func() {
		for i := 0; i < len(inputs); i++ {
			result.sumB += inputs[i].b
		}
		wg.Done()
	}()

	wg.Wait()
	return result
}

func main() {
	fmt.Println("=== False Sharing 示範 ===")
	fmt.Println()

	// 顯示結構體大小
	fmt.Printf("ResultBad  大小: %d bytes (兩個欄位在同一 cache line)\n", unsafe.Sizeof(ResultBad{}))
	fmt.Printf("ResultGood 大小: %d bytes (兩個欄位在不同 cache line)\n", unsafe.Sizeof(ResultGood{}))
	fmt.Println()

	// 準備測試資料
	const n = 10_000_000
	inputs := make([]Input, n)
	for i := range inputs {
		inputs[i] = Input{a: int64(i), b: int64(i * 2)}
	}

	// 測試 Bad 版本 (有 false sharing)
	start := time.Now()
	iterations := 10
	for i := 0; i < iterations; i++ {
		countBad(inputs)
	}
	badDuration := time.Since(start)

	// 測試 Good 版本 (無 false sharing)
	start = time.Now()
	for i := 0; i < iterations; i++ {
		countGood(inputs)
	}
	goodDuration := time.Since(start)

	fmt.Printf("❌ 有 False Sharing:  %v (平均 %v/次)\n", badDuration, badDuration/time.Duration(iterations))
	fmt.Printf("✅ 無 False Sharing:  %v (平均 %v/次)\n", goodDuration, goodDuration/time.Duration(iterations))
	fmt.Printf("加速比: %.2fx\n", float64(badDuration)/float64(goodDuration))

	fmt.Println()
	fmt.Println("提示：使用 go test -bench=. 可以更精確地 benchmark")

	// 防止編譯器優化掉未使用的 testing 引入
	_ = testing.Benchmark
}
