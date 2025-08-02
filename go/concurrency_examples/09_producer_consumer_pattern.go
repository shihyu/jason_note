// Go 並行程式設計範例 09: 生產者-消費者模式
// 展示經典的生產者-消費者並行設計模式

package main

import (
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// 工作項目
type WorkItem struct {
	ID       int
	Type     string
	Data     interface{}
	Priority int
	Created  time.Time
}

// 處理結果
type ProcessResult struct {
	WorkItem WorkItem
	Success  bool
	Output   string
	Duration time.Duration
	WorkerID int
	Error    error
}

// 生產者-消費者系統
type ProducerConsumerSystem struct {
	jobQueue    chan WorkItem
	resultQueue chan ProcessResult
	workerCount int
	wg          sync.WaitGroup
	shutdown    chan bool
}

func NewProducerConsumerSystem(workerCount, bufferSize int) *ProducerConsumerSystem {
	return &ProducerConsumerSystem{
		jobQueue:    make(chan WorkItem, bufferSize),
		resultQueue: make(chan ProcessResult, bufferSize),
		workerCount: workerCount,
		shutdown:    make(chan bool),
	}
}

func (pcs *ProducerConsumerSystem) Start() {
	fmt.Printf("🚀 啟動生產者-消費者系統 (%d 個工作者)\n", pcs.workerCount)

	// 啟動工作者 (消費者)
	for i := 1; i <= pcs.workerCount; i++ {
		pcs.wg.Add(1)
		go pcs.worker(i)
	}

	// 啟動結果收集器
	go pcs.resultCollector()
}

func (pcs *ProducerConsumerSystem) Stop() {
	fmt.Println("🛑 停止生產者-消費者系統...")
	close(pcs.jobQueue)
	pcs.wg.Wait()
	close(pcs.resultQueue)

	// 等待一小段時間讓結果收集器完成
	time.Sleep(100 * time.Millisecond)
	close(pcs.shutdown)
}

func (pcs *ProducerConsumerSystem) SubmitJob(job WorkItem) {
	select {
	case pcs.jobQueue <- job:
		fmt.Printf("📤 提交任務: %s-%d (優先級: %d)\n", job.Type, job.ID, job.Priority)
	default:
		fmt.Printf("⚠️  任務隊列已滿，丟棄任務: %s-%d\n", job.Type, job.ID)
	}
}

func (pcs *ProducerConsumerSystem) worker(workerID int) {
	defer pcs.wg.Done()

	fmt.Printf("👷 工作者 %d 啟動\n", workerID)

	for job := range pcs.jobQueue {
		start := time.Now()

		fmt.Printf("🔄 工作者 %d 開始處理: %s-%d\n", workerID, job.Type, job.ID)

		// 模擬不同類型的處理時間
		var processingTime time.Duration
		var success bool
		var output string
		var err error

		switch job.Type {
		case "data_processing":
			processingTime = time.Duration(200+rand.Intn(300)) * time.Millisecond
			success = rand.Float32() > 0.1 // 90% 成功率
			output = fmt.Sprintf("處理了 %v 的數據", job.Data)

		case "file_upload":
			processingTime = time.Duration(500+rand.Intn(1000)) * time.Millisecond
			success = rand.Float32() > 0.05 // 95% 成功率
			output = fmt.Sprintf("上傳文件: %v", job.Data)

		case "email_sending":
			processingTime = time.Duration(100+rand.Intn(200)) * time.Millisecond
			success = rand.Float32() > 0.15 // 85% 成功率
			output = fmt.Sprintf("發送郵件給: %v", job.Data)

		case "report_generation":
			processingTime = time.Duration(800+rand.Intn(1200)) * time.Millisecond
			success = rand.Float32() > 0.2 // 80% 成功率
			output = fmt.Sprintf("生成報告: %v", job.Data)

		default:
			processingTime = 100 * time.Millisecond
			success = true
			output = "默認處理"
		}

		// 模擬處理時間
		time.Sleep(processingTime)

		if !success {
			err = fmt.Errorf("處理失敗: %s-%d", job.Type, job.ID)
		}

		duration := time.Since(start)

		result := ProcessResult{
			WorkItem: job,
			Success:  success,
			Output:   output,
			Duration: duration,
			WorkerID: workerID,
			Error:    err,
		}

		// 發送結果
		select {
		case pcs.resultQueue <- result:
		default:
			fmt.Printf("⚠️  結果隊列已滿，丟棄結果: %s-%d\n", job.Type, job.ID)
		}

		status := "✅"
		if !success {
			status = "❌"
		}
		fmt.Printf("%s 工作者 %d 完成: %s-%d (耗時: %v)\n",
			status, workerID, job.Type, job.ID, duration)
	}

	fmt.Printf("👷 工作者 %d 停止\n", workerID)
}

func (pcs *ProducerConsumerSystem) resultCollector() {

	fmt.Println("📊 結果收集器啟動")

	var totalJobs, successJobs int
	var totalDuration time.Duration
	workerStats := make(map[int]int)

	for {
		select {
		case result, ok := <-pcs.resultQueue:
			if !ok {
				// 通道已關閉，結束收集
				goto done
			}

			totalJobs++
			totalDuration += result.Duration
			workerStats[result.WorkerID]++

			if result.Success {
				successJobs++
				fmt.Printf("📈 收集成功結果: %s-%d by 工作者%d (%s)\n",
					result.WorkItem.Type, result.WorkItem.ID, result.WorkerID, result.Output)
			} else {
				fmt.Printf("📉 收集失敗結果: %s-%d by 工作者%d (錯誤: %v)\n",
					result.WorkItem.Type, result.WorkItem.ID, result.WorkerID, result.Error)
			}
		}
	}

done:

	// 顯示統計信息
	if totalJobs > 0 {
		successRate := float64(successJobs) / float64(totalJobs) * 100
		avgDuration := totalDuration / time.Duration(totalJobs)

		fmt.Printf("\n📊 處理統計:\n")
		fmt.Printf("   總任務數: %d\n", totalJobs)
		fmt.Printf("   成功任務: %d\n", successJobs)
		fmt.Printf("   失敗任務: %d\n", totalJobs-successJobs)
		fmt.Printf("   成功率: %.1f%%\n", successRate)
		fmt.Printf("   平均處理時間: %v\n", avgDuration)

		fmt.Println("   工作者負載分布:")
		for workerID, count := range workerStats {
			percentage := float64(count) / float64(totalJobs) * 100
			fmt.Printf("     工作者 %d: %d 任務 (%.1f%%)\n", workerID, count, percentage)
		}
	}

	fmt.Println("📊 結果收集器停止")
}

func main() {
	fmt.Println("=== 生產者-消費者模式範例 ===")

	// 創建系統：4個工作者，緩衝區大小10
	system := NewProducerConsumerSystem(4, 10)
	system.Start()

	// 啟動生產者
	fmt.Println("\n🏭 啟動生產者...")
	go producer1(system) // 數據處理生產者
	go producer2(system) // 文件上傳生產者
	go producer3(system) // 郵件發送生產者

	// 運行系統 8 秒
	time.Sleep(8 * time.Second)

	// 停止系統
	system.Stop()

	fmt.Println("✅ 生產者-消費者範例完成")
}

// 數據處理任務生產者
func producer1(system *ProducerConsumerSystem) {
	fmt.Println("🏭 數據處理生產者啟動")

	for i := 1; i <= 15; i++ {
		job := WorkItem{
			ID:       i,
			Type:     "data_processing",
			Data:     fmt.Sprintf("dataset_%d.csv", i),
			Priority: rand.Intn(5) + 1,
			Created:  time.Now(),
		}

		system.SubmitJob(job)
		time.Sleep(time.Duration(300+rand.Intn(200)) * time.Millisecond)
	}

	fmt.Println("🏭 數據處理生產者完成")
}

// 文件上傳任務生產者
func producer2(system *ProducerConsumerSystem) {
	fmt.Println("🏭 文件上傳生產者啟動")

	for i := 1; i <= 10; i++ {
		job := WorkItem{
			ID:       i,
			Type:     "file_upload",
			Data:     fmt.Sprintf("document_%d.pdf", i),
			Priority: rand.Intn(3) + 3, // 較高優先級
			Created:  time.Now(),
		}

		system.SubmitJob(job)
		time.Sleep(time.Duration(500+rand.Intn(500)) * time.Millisecond)
	}

	fmt.Println("🏭 文件上傳生產者完成")
}

// 郵件發送任務生產者
func producer3(system *ProducerConsumerSystem) {
	fmt.Println("🏭 郵件生產者啟動")

	recipients := []string{
		"user1@example.com", "user2@example.com", "user3@example.com",
		"admin@example.com", "support@example.com", "sales@example.com",
		"manager@example.com", "team@example.com",
	}

	for i, recipient := range recipients {
		job := WorkItem{
			ID:       i + 1,
			Type:     "email_sending",
			Data:     recipient,
			Priority: 2,
			Created:  time.Now(),
		}

		system.SubmitJob(job)
		time.Sleep(time.Duration(200+rand.Intn(300)) * time.Millisecond)

		// 一半時間後發送報告生成任務
		if i == len(recipients)/2 {
			reportJob := WorkItem{
				ID:       99,
				Type:     "report_generation",
				Data:     "monthly_report.xlsx",
				Priority: 5, // 最高優先級
				Created:  time.Now(),
			}
			system.SubmitJob(reportJob)
		}
	}

	fmt.Println("🏭 郵件生產者完成")
}
