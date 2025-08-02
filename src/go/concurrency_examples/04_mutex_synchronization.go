// Go 並行程式設計範例 04: Mutex 同步
// 展示互斥鎖如何保護共享資源

package main

import (
	"fmt"
	"sync"
	"time"
)

// 安全計數器結構
type SafeCounter struct {
	mu       sync.Mutex
	value    int
	accesses int
}

func (c *SafeCounter) Increment() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.value++
	c.accesses++
	fmt.Printf("🔢 計數器增加到: %d (總存取次數: %d)\n", c.value, c.accesses)
}

func (c *SafeCounter) GetValue() (int, int) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.accesses++
	return c.value, c.accesses
}

func (c *SafeCounter) Reset() {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.value = 0
	c.accesses++
	fmt.Printf("🔄 計數器重置 (總存取次數: %d)\n", c.accesses)
}

func main() {
	fmt.Println("=== Mutex 同步範例 ===")

	counter := &SafeCounter{}
	var wg sync.WaitGroup

	// 啟動多個增加計數的 goroutine
	fmt.Println("🚀 啟動 5 個增加計數的 Goroutine...")
	for i := 1; i <= 5; i++ {
		wg.Add(1)
		go incrementWorker(i, counter, &wg)
	}

	// 啟動一個讀取計數的 goroutine
	fmt.Println("👁️  啟動讀取計數的 Goroutine...")
	wg.Add(1)
	go readWorker(counter, &wg)

	// 啟動一個重置計數的 goroutine
	fmt.Println("🔄 啟動重置計數的 Goroutine...")
	wg.Add(1)
	go resetWorker(counter, &wg)

	wg.Wait()

	// 最終結果
	finalValue, totalAccesses := counter.GetValue()
	fmt.Printf("\n📊 最終結果:\n")
	fmt.Printf("   計數器值: %d\n", finalValue)
	fmt.Printf("   總存取次數: %d\n", totalAccesses)
	fmt.Println("✅ 所有操作完成")
}

func incrementWorker(id int, counter *SafeCounter, wg *sync.WaitGroup) {
	defer wg.Done()

	for j := 1; j <= 3; j++ {
		counter.Increment()
		time.Sleep(time.Duration(100+id*20) * time.Millisecond)
	}
	fmt.Printf("✅ Worker %d 完成增加操作\n", id)
}

func readWorker(counter *SafeCounter, wg *sync.WaitGroup) {
	defer wg.Done()

	for i := 0; i < 8; i++ {
		time.Sleep(200 * time.Millisecond)
		value, accesses := counter.GetValue()
		fmt.Printf("👁️  讀取計數器: %d (總存取: %d)\n", value, accesses)
	}
	fmt.Println("✅ 讀取 Worker 完成")
}

func resetWorker(counter *SafeCounter, wg *sync.WaitGroup) {
	defer wg.Done()

	time.Sleep(800 * time.Millisecond)
	counter.Reset()
	fmt.Println("✅ 重置 Worker 完成")
}
