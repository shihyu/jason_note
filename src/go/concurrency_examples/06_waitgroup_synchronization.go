// Go 並行程式設計範例 06: WaitGroup 與 Once 同步控制
// 展示任務協調和單次執行的並行模式

package main

import (
	"fmt"
	"sync"
	"time"
)

// 全域單例相關變數
var (
	databaseConnection *DatabaseConnection
	once               sync.Once
)

// 模擬資料庫連接
type DatabaseConnection struct {
	Host         string
	Port         int
	ConnectionID string
	CreatedAt    time.Time
}

func GetDatabaseConnection() *DatabaseConnection {
	once.Do(func() {
		fmt.Println("🔌 初始化資料庫連接...")
		time.Sleep(500 * time.Millisecond) // 模擬連接時間

		databaseConnection = &DatabaseConnection{
			Host:         "localhost",
			Port:         5432,
			ConnectionID: "conn_12345",
			CreatedAt:    time.Now(),
		}

		fmt.Printf("✅ 資料庫連接建立: %s:%d (ID: %s)\n",
			databaseConnection.Host, databaseConnection.Port, databaseConnection.ConnectionID)
	})

	return databaseConnection
}

// 任務結果
type TaskResult struct {
	TaskID    int
	WorkerID  int
	Result    string
	Duration  time.Duration
	Timestamp time.Time
}

func main() {
	fmt.Println("=== WaitGroup 與 Once 同步控制範例 ===")

	// WaitGroup 範例
	fmt.Println("\n🎯 WaitGroup 任務協調範例:")
	waitGroupDemo()

	// Once 範例
	fmt.Println("\n🔐 sync.Once 單次執行範例:")
	onceDemo()
}

func waitGroupDemo() {
	var wg sync.WaitGroup
	results := make(chan TaskResult, 10)

	// 任務列表
	tasks := []string{
		"資料處理", "檔案上傳", "郵件發送", "日誌記錄",
		"快取更新", "資料備份", "報告生成",
	}

	fmt.Printf("📋 準備執行 %d 個任務...\n", len(tasks))

	// 啟動任務處理者
	for i, task := range tasks {
		wg.Add(1)
		go taskWorker(i+1, task, &wg, results)
	}

	// 啟動結果收集者
	go resultCollector(results, len(tasks))

	// 等待所有任務完成
	fmt.Println("⏳ 等待所有任務完成...")
	wg.Wait()
	close(results)

	time.Sleep(100 * time.Millisecond) // 讓結果收集者完成輸出
	fmt.Println("✅ 所有任務已完成")
}

func taskWorker(workerID int, taskName string, wg *sync.WaitGroup, results chan<- TaskResult) {
	defer wg.Done()

	fmt.Printf("🔄 Worker %d 開始執行: %s\n", workerID, taskName)
	startTime := time.Now()

	// 模擬不同的處理時間
	processingTime := time.Duration(200+workerID*100) * time.Millisecond
	time.Sleep(processingTime)

	duration := time.Since(startTime)
	result := TaskResult{
		TaskID:    workerID,
		WorkerID:  workerID,
		Result:    fmt.Sprintf("%s 成功完成", taskName),
		Duration:  duration,
		Timestamp: time.Now(),
	}

	results <- result
	fmt.Printf("✅ Worker %d 完成: %s (耗時: %v)\n", workerID, taskName, duration)
}

func resultCollector(results <-chan TaskResult, expectedCount int) {
	fmt.Println("📊 結果收集器啟動...")

	var totalDuration time.Duration
	count := 0

	for result := range results {
		count++
		totalDuration += result.Duration

		fmt.Printf("📈 收集結果 %d/%d: %s (耗時: %v)\n",
			count, expectedCount, result.Result, result.Duration)
	}

	if count > 0 {
		avgDuration := totalDuration / time.Duration(count)
		fmt.Printf("📊 平均處理時間: %v\n", avgDuration)
	}

	fmt.Println("📋 結果收集完成")
}

func onceDemo() {
	var wg sync.WaitGroup

	// 模擬多個 goroutine 同時嘗試獲取資料庫連接
	fmt.Println("🚀 啟動 5 個 Goroutine 獲取資料庫連接...")

	for i := 1; i <= 5; i++ {
		wg.Add(1)
		go databaseUser(i, &wg)
	}

	wg.Wait()

	// 驗證只有一個連接被創建
	conn := GetDatabaseConnection()
	fmt.Printf("\n🔍 驗證結果:\n")
	fmt.Printf("   連接主機: %s:%d\n", conn.Host, conn.Port)
	fmt.Printf("   連接ID: %s\n", conn.ConnectionID)
	fmt.Printf("   創建時間: %s\n", conn.CreatedAt.Format("2006-01-02 15:04:05"))
	fmt.Println("✅ sync.Once 確保只初始化一次")
}

func databaseUser(userID int, wg *sync.WaitGroup) {
	defer wg.Done()

	// 模擬不同的啟動時間
	time.Sleep(time.Duration(userID*50) * time.Millisecond)

	fmt.Printf("👤 用戶 %d 嘗試獲取資料庫連接...\n", userID)
	conn := GetDatabaseConnection()

	fmt.Printf("👤 用戶 %d 獲得連接: %s (ID: %s)\n",
		userID, conn.Host, conn.ConnectionID)

	// 模擬使用連接
	time.Sleep(100 * time.Millisecond)
	fmt.Printf("👤 用戶 %d 使用連接完成\n", userID)
}
