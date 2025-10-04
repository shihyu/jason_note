// Go 並行程式設計範例 07: 原子操作
// 展示無鎖的原子操作在高並行場景下的應用

package main

import (
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

// 統計資料結構
type Statistics struct {
	requests    int64
	errors      int64
	totalTime   int64
	maxTime     int64
	running     int32
	connections int64
}

func (s *Statistics) IncrementRequest() {
	atomic.AddInt64(&s.requests, 1)
}

func (s *Statistics) IncrementError() {
	atomic.AddInt64(&s.errors, 1)
}

func (s *Statistics) AddProcessingTime(duration time.Duration) {
	nanos := duration.Nanoseconds()
	atomic.AddInt64(&s.totalTime, nanos)

	// 更新最大處理時間
	for {
		current := atomic.LoadInt64(&s.maxTime)
		if nanos <= current {
			break
		}
		if atomic.CompareAndSwapInt64(&s.maxTime, current, nanos) {
			break
		}
	}
}

func (s *Statistics) SetRunning(running bool) {
	if running {
		atomic.StoreInt32(&s.running, 1)
	} else {
		atomic.StoreInt32(&s.running, 0)
	}
}

func (s *Statistics) IsRunning() bool {
	return atomic.LoadInt32(&s.running) == 1
}

func (s *Statistics) IncrementConnection() {
	atomic.AddInt64(&s.connections, 1)
}

func (s *Statistics) DecrementConnection() {
	atomic.AddInt64(&s.connections, -1)
}

func (s *Statistics) GetSnapshot() (int64, int64, time.Duration, time.Duration, int64) {
	requests := atomic.LoadInt64(&s.requests)
	errors := atomic.LoadInt64(&s.errors)
	totalTime := atomic.LoadInt64(&s.totalTime)
	maxTime := atomic.LoadInt64(&s.maxTime)
	connections := atomic.LoadInt64(&s.connections)

	var avgTime time.Duration
	if requests > 0 {
		avgTime = time.Duration(totalTime / requests)
	}

	return requests, errors, avgTime, time.Duration(maxTime), connections
}

func main() {
	fmt.Println("=== 原子操作範例 ===")

	stats := &Statistics{}
	var wg sync.WaitGroup

	fmt.Println("🚀 啟動服務統計系統...")
	stats.SetRunning(true)

	// 啟動請求處理器
	fmt.Println("📡 啟動 10 個請求處理器...")
	for i := 1; i <= 10; i++ {
		wg.Add(1)
		go requestProcessor(i, stats, &wg)
	}

	// 啟動連接管理器
	fmt.Println("🔗 啟動 3 個連接管理器...")
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go connectionManager(i, stats, &wg)
	}

	// 啟動監控器
	fmt.Println("📊 啟動統計監控器...")
	wg.Add(1)
	go statisticsMonitor(stats, &wg)

	// 運行 5 秒後停止
	time.Sleep(5 * time.Second)
	fmt.Println("🛑 停止服務...")
	stats.SetRunning(false)

	wg.Wait()

	// 顯示最終統計
	displayFinalStats(stats)
}

func requestProcessor(id int, stats *Statistics, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Printf("🔄 請求處理器 %d 啟動\n", id)

	for stats.IsRunning() {
		start := time.Now()

		// 模擬請求處理
		processingTime := time.Duration(50+id*20) * time.Millisecond
		time.Sleep(processingTime)

		duration := time.Since(start)
		stats.IncrementRequest()
		stats.AddProcessingTime(duration)

		// 10% 的請求會出錯
		if id%10 == 1 && time.Now().UnixNano()%10 == 0 {
			stats.IncrementError()
			fmt.Printf("❌ 處理器 %d 處理請求出錯\n", id)
		}

		// 隨機休息
		time.Sleep(time.Duration(100+id*50) * time.Millisecond)
	}

	fmt.Printf("✅ 請求處理器 %d 停止\n", id)
}

func connectionManager(id int, stats *Statistics, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Printf("🔗 連接管理器 %d 啟動\n", id)

	for stats.IsRunning() {
		// 模擬連接建立
		stats.IncrementConnection()
		fmt.Printf("🔌 管理器 %d 建立連接\n", id)

		// 保持連接一段時間
		time.Sleep(time.Duration(800+id*200) * time.Millisecond)

		// 關閉連接
		stats.DecrementConnection()
		fmt.Printf("🔌 管理器 %d 關閉連接\n", id)

		time.Sleep(time.Duration(300+id*100) * time.Millisecond)
	}

	fmt.Printf("✅ 連接管理器 %d 停止\n", id)
}

func statisticsMonitor(stats *Statistics, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Println("📊 統計監控器啟動")

	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for stats.IsRunning() {
		select {
		case <-ticker.C:
			requests, errors, avgTime, maxTime, connections := stats.GetSnapshot()

			var errorRate float64
			if requests > 0 {
				errorRate = float64(errors) / float64(requests) * 100
			}

			fmt.Printf("📈 統計快照 - 請求:%d, 錯誤:%d(%.1f%%), 平均時間:%v, 最大時間:%v, 活躍連接:%d\n",
				requests, errors, errorRate, avgTime, maxTime, connections)

		default:
			time.Sleep(100 * time.Millisecond)
		}
	}

	fmt.Println("✅ 統計監控器停止")
}

func displayFinalStats(stats *Statistics) {
	requests, errors, avgTime, maxTime, connections := stats.GetSnapshot()

	fmt.Println("\n📊 最終統計報告:")
	fmt.Printf("   總請求數: %d\n", requests)
	fmt.Printf("   錯誤數: %d\n", errors)

	if requests > 0 {
		errorRate := float64(errors) / float64(requests) * 100
		fmt.Printf("   錯誤率: %.2f%%\n", errorRate)
	}

	fmt.Printf("   平均處理時間: %v\n", avgTime)
	fmt.Printf("   最大處理時間: %v\n", maxTime)
	fmt.Printf("   剩餘連接數: %d\n", connections)

	if requests > 0 {
		throughput := float64(requests) / 5.0 // 5 秒運行時間
		fmt.Printf("   吞吐量: %.1f 請求/秒\n", throughput)
	}

	fmt.Println("✅ 原子操作範例完成")
}
