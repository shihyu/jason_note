// Go 並行程式設計範例 11: 高級 Worker Pool 模式
// 展示動態調整、優先級隊列和負載均衡的工作池實現

package main

import (
	"container/heap"
	"fmt"
	"math/rand"
	"runtime"
	"sync"
	"sync/atomic"
	"time"
)

// 優先級任務
type PriorityTask struct {
	ID          int
	Type        string
	Priority    int // 數字越小優先級越高
	Data        interface{}
	CreatedAt   time.Time
	StartedAt   time.Time
	CompletedAt time.Time
	WorkerID    int
}

// 任務結果
type TaskResult struct {
	Task     PriorityTask
	Success  bool
	Output   string
	Error    error
	Duration time.Duration
}

// 優先級隊列實現
type PriorityQueue []*PriorityTask

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].Priority < pq[j].Priority
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*PriorityTask))
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	task := old[n-1]
	*pq = old[0 : n-1]
	return task
}

// 高級工作池
type AdvancedWorkerPool struct {
	// 配置
	minWorkers     int
	maxWorkers     int
	currentWorkers int32

	// 任務隊列
	taskQueue     chan *PriorityTask
	priorityQueue *PriorityQueue
	queueMutex    sync.Mutex

	// 結果通道
	resultChan chan TaskResult

	// 控制
	wg       sync.WaitGroup
	shutdown chan bool

	// 統計
	stats PoolStats

	// 監控
	lastActivity  time.Time
	activityMutex sync.RWMutex
}

type PoolStats struct {
	TasksSubmitted   int64
	TasksCompleted   int64
	TasksFailed      int64
	TotalProcessTime int64
	WorkersCreated   int64
	WorkersDestroyed int64
}

func NewAdvancedWorkerPool(minWorkers, maxWorkers int) *AdvancedWorkerPool {
	pq := make(PriorityQueue, 0)
	heap.Init(&pq)

	pool := &AdvancedWorkerPool{
		minWorkers:    minWorkers,
		maxWorkers:    maxWorkers,
		taskQueue:     make(chan *PriorityTask, maxWorkers*2),
		priorityQueue: &pq,
		resultChan:    make(chan TaskResult, maxWorkers*2),
		shutdown:      make(chan bool),
		lastActivity:  time.Now(),
	}

	return pool
}

func (pool *AdvancedWorkerPool) Start() {
	fmt.Printf("🚀 啟動高級工作池 (最小: %d, 最大: %d 工作者)\n",
		pool.minWorkers, pool.maxWorkers)

	// 啟動最小數量的工作者
	for i := 0; i < pool.minWorkers; i++ {
		pool.startWorker()
	}

	// 啟動任務調度器
	pool.wg.Add(1)
	go pool.taskScheduler()

	// 啟動自動縮放監控器
	pool.wg.Add(1)
	go pool.autoScaler()

	// 啟動統計監控器
	pool.wg.Add(1)
	go pool.statsMonitor()

	// 啟動結果收集器
	pool.wg.Add(1)
	go pool.resultCollector()
}

func (pool *AdvancedWorkerPool) Stop() {
	fmt.Println("🛑 停止工作池...")
	close(pool.shutdown)
	pool.wg.Wait()
	close(pool.resultChan)
}

func (pool *AdvancedWorkerPool) SubmitTask(task *PriorityTask) {
	atomic.AddInt64(&pool.stats.TasksSubmitted, 1)

	pool.activityMutex.Lock()
	pool.lastActivity = time.Now()
	pool.activityMutex.Unlock()

	// 添加到優先級隊列
	pool.queueMutex.Lock()
	heap.Push(pool.priorityQueue, task)
	pool.queueMutex.Unlock()

	fmt.Printf("📤 提交任務: %s-%d (優先級: %d, 隊列長度: %d)\n",
		task.Type, task.ID, task.Priority, pool.priorityQueue.Len())
}

func (pool *AdvancedWorkerPool) startWorker() {
	workerID := int(atomic.AddInt32(&pool.currentWorkers, 1))
	atomic.AddInt64(&pool.stats.WorkersCreated, 1)

	pool.wg.Add(1)
	go pool.worker(workerID)

	fmt.Printf("👷 啟動工作者 %d (當前工作者數: %d)\n",
		workerID, atomic.LoadInt32(&pool.currentWorkers))
}

func (pool *AdvancedWorkerPool) worker(workerID int) {
	defer pool.wg.Done()
	defer func() {
		atomic.AddInt32(&pool.currentWorkers, -1)
		atomic.AddInt64(&pool.stats.WorkersDestroyed, 1)
		fmt.Printf("👷 工作者 %d 停止 (剩餘工作者: %d)\n",
			workerID, atomic.LoadInt32(&pool.currentWorkers))
	}()

	fmt.Printf("👷 工作者 %d 啟動\n", workerID)

	idleTimer := time.NewTimer(30 * time.Second) // 30秒空閒超時
	defer idleTimer.Stop()

	for {
		select {
		case task := <-pool.taskQueue:
			if task == nil {
				continue
			}

			// 重置空閒計時器
			if !idleTimer.Stop() {
				<-idleTimer.C
			}
			idleTimer.Reset(30 * time.Second)

			// 處理任務
			pool.processTask(task, workerID)

		case <-idleTimer.C:
			// 空閒超時，檢查是否可以縮減工作者
			currentWorkers := atomic.LoadInt32(&pool.currentWorkers)
			if currentWorkers > int32(pool.minWorkers) {
				fmt.Printf("⏰ 工作者 %d 空閒超時，準備退出\n", workerID)
				return
			}
			idleTimer.Reset(30 * time.Second)

		case <-pool.shutdown:
			fmt.Printf("🛑 工作者 %d 收到停止信號\n", workerID)
			return
		}
	}
}

func (pool *AdvancedWorkerPool) processTask(task *PriorityTask, workerID int) {
	task.StartedAt = time.Now()
	task.WorkerID = workerID

	fmt.Printf("🔄 工作者 %d 開始處理: %s-%d (優先級: %d)\n",
		workerID, task.Type, task.ID, task.Priority)

	start := time.Now()
	var success bool
	var output string
	var err error

	// 模擬不同類型任務的處理
	switch task.Type {
	case "cpu_intensive":
		// CPU 密集型任務
		success = pool.processCPUTask(task)
		output = fmt.Sprintf("CPU任務完成: %v", task.Data)

	case "io_intensive":
		// I/O 密集型任務
		success = pool.processIOTask(task)
		output = fmt.Sprintf("I/O任務完成: %v", task.Data)

	case "network_request":
		// 網路請求任務
		success = pool.processNetworkTask(task)
		output = fmt.Sprintf("網路請求完成: %v", task.Data)

	case "data_processing":
		// 數據處理任務
		success = pool.processDataTask(task)
		output = fmt.Sprintf("數據處理完成: %v", task.Data)

	default:
		success = true
		output = "默認處理完成"
	}

	duration := time.Since(start)
	task.CompletedAt = time.Now()

	// 更新統計
	atomic.AddInt64(&pool.stats.TotalProcessTime, duration.Nanoseconds())
	if success {
		atomic.AddInt64(&pool.stats.TasksCompleted, 1)
	} else {
		atomic.AddInt64(&pool.stats.TasksFailed, 1)
		err = fmt.Errorf("任務處理失敗")
	}

	// 發送結果
	result := TaskResult{
		Task:     *task,
		Success:  success,
		Output:   output,
		Error:    err,
		Duration: duration,
	}

	select {
	case pool.resultChan <- result:
	default:
		fmt.Printf("⚠️  結果隊列已滿，丟棄結果: %s-%d\n", task.Type, task.ID)
	}

	status := "✅"
	if !success {
		status = "❌"
	}
	fmt.Printf("%s 工作者 %d 完成: %s-%d (耗時: %v)\n",
		status, workerID, task.Type, task.ID, duration)
}

func (pool *AdvancedWorkerPool) processCPUTask(task *PriorityTask) bool {
	// 模擬 CPU 密集型計算
	iterations := 1000000 + task.Priority*100000
	var result float64
	for i := 0; i < iterations; i++ {
		result += float64(i) * 0.001
	}
	return rand.Float32() > 0.05 // 95% 成功率
}

func (pool *AdvancedWorkerPool) processIOTask(task *PriorityTask) bool {
	// 模擬 I/O 操作
	sleepTime := time.Duration(100+task.Priority*50) * time.Millisecond
	time.Sleep(sleepTime)
	return rand.Float32() > 0.1 // 90% 成功率
}

func (pool *AdvancedWorkerPool) processNetworkTask(task *PriorityTask) bool {
	// 模擬網路請求
	sleepTime := time.Duration(200+rand.Intn(800)) * time.Millisecond
	time.Sleep(sleepTime)
	return rand.Float32() > 0.15 // 85% 成功率
}

func (pool *AdvancedWorkerPool) processDataTask(task *PriorityTask) bool {
	// 模擬數據處理
	sleepTime := time.Duration(50+task.Priority*20) * time.Millisecond
	time.Sleep(sleepTime)
	return rand.Float32() > 0.08 // 92% 成功率
}

func (pool *AdvancedWorkerPool) taskScheduler() {
	defer pool.wg.Done()

	fmt.Println("📋 任務調度器啟動")

	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			pool.queueMutex.Lock()
			if pool.priorityQueue.Len() > 0 {
				task := heap.Pop(pool.priorityQueue).(*PriorityTask)
				pool.queueMutex.Unlock()

				select {
				case pool.taskQueue <- task:
					fmt.Printf("📋 調度任務: %s-%d (優先級: %d)\n",
						task.Type, task.ID, task.Priority)
				default:
					// 如果任務隊列滿了，重新放回優先級隊列
					pool.queueMutex.Lock()
					heap.Push(pool.priorityQueue, task)
					pool.queueMutex.Unlock()
				}
			} else {
				pool.queueMutex.Unlock()
			}

		case <-pool.shutdown:
			fmt.Println("📋 任務調度器停止")
			return
		}
	}
}

func (pool *AdvancedWorkerPool) autoScaler() {
	defer pool.wg.Done()

	fmt.Println("⚖️  自動縮放器啟動")

	ticker := time.NewTicker(5 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			pool.queueMutex.Lock()
			queueLen := pool.priorityQueue.Len()
			pool.queueMutex.Unlock()

			currentWorkers := atomic.LoadInt32(&pool.currentWorkers)

			// 擴展條件：隊列長度 > 工作者數 * 2
			if queueLen > int(currentWorkers)*2 && currentWorkers < int32(pool.maxWorkers) {
				fmt.Printf("📈 隊列壓力大 (隊列: %d, 工作者: %d)，擴展工作者\n",
					queueLen, currentWorkers)
				pool.startWorker()
			}

			// 縮減條件在工作者的空閒超時中處理

		case <-pool.shutdown:
			fmt.Println("⚖️  自動縮放器停止")
			return
		}
	}
}

func (pool *AdvancedWorkerPool) statsMonitor() {
	defer pool.wg.Done()

	fmt.Println("📊 統計監控器啟動")

	ticker := time.NewTicker(3 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			pool.printStats()

		case <-pool.shutdown:
			fmt.Println("📊 統計監控器停止")
			return
		}
	}
}

func (pool *AdvancedWorkerPool) printStats() {
	submitted := atomic.LoadInt64(&pool.stats.TasksSubmitted)
	completed := atomic.LoadInt64(&pool.stats.TasksCompleted)
	failed := atomic.LoadInt64(&pool.stats.TasksFailed)
	totalTime := atomic.LoadInt64(&pool.stats.TotalProcessTime)
	workers := atomic.LoadInt32(&pool.currentWorkers)

	pool.queueMutex.Lock()
	queueLen := pool.priorityQueue.Len()
	pool.queueMutex.Unlock()

	fmt.Printf("📈 統計快照 - 工作者:%d, 隊列:%d, 提交:%d, 完成:%d, 失敗:%d",
		workers, queueLen, submitted, completed, failed)

	if completed > 0 {
		avgTime := time.Duration(totalTime / completed)
		successRate := float64(completed) / float64(submitted) * 100
		fmt.Printf(", 成功率:%.1f%%, 平均時間:%v", successRate, avgTime)
	}

	fmt.Printf(", CPU:%.1f%%, Goroutines:%d\n",
		getCPUUsage(), runtime.NumGoroutine())
}

func (pool *AdvancedWorkerPool) resultCollector() {
	defer pool.wg.Done()

	fmt.Println("📥 結果收集器啟動")

	for {
		select {
		case result := <-pool.resultChan:
			if result.Success {
				fmt.Printf("📥 收集成功結果: %s-%d by 工作者%d (%v)\n",
					result.Task.Type, result.Task.ID, result.Task.WorkerID, result.Duration)
			} else {
				fmt.Printf("📥 收集失敗結果: %s-%d by 工作者%d (錯誤: %v)\n",
					result.Task.Type, result.Task.ID, result.Task.WorkerID, result.Error)
			}

		case <-pool.shutdown:
			fmt.Println("📥 結果收集器停止")
			return
		}
	}
}

func getCPUUsage() float64 {
	// 簡化的 CPU 使用率估算
	return float64(runtime.NumGoroutine()) / float64(runtime.NumCPU()) * 10
}

func main() {
	fmt.Println("=== 高級 Worker Pool 模式範例 ===")

	// 創建工作池：最小2個工作者，最大8個工作者
	pool := NewAdvancedWorkerPool(2, 8)
	pool.Start()

	// 啟動任務生產者
	go taskProducer(pool)

	// 運行 15 秒
	time.Sleep(15 * time.Second)

	// 停止工作池
	pool.Stop()

	// 顯示最終統計
	fmt.Println("\n📊 最終統計:")
	pool.printStats()

	fmt.Println("✅ 高級 Worker Pool 範例完成")
}

func taskProducer(pool *AdvancedWorkerPool) {
	fmt.Println("🏭 任務生產者啟動")

	taskTypes := []string{"cpu_intensive", "io_intensive", "network_request", "data_processing"}
	taskID := 1

	for i := 0; i < 50; i++ {
		taskType := taskTypes[rand.Intn(len(taskTypes))]
		priority := rand.Intn(5) + 1 // 1-5 優先級

		task := &PriorityTask{
			ID:        taskID,
			Type:      taskType,
			Priority:  priority,
			Data:      fmt.Sprintf("data_%d", taskID),
			CreatedAt: time.Now(),
		}

		pool.SubmitTask(task)
		taskID++

		// 隨機間隔提交任務
		sleepTime := time.Duration(rand.Intn(500)+100) * time.Millisecond
		time.Sleep(sleepTime)
	}

	fmt.Println("🏭 任務生產者完成")
}
