// Go 並行程式設計範例 08: Context 上下文控制
// 展示 Context 在超時控制、取消操作和值傳遞中的應用

package main

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"time"
)

// 請求上下文鍵類型
type contextKey string

const (
	RequestIDKey contextKey = "request_id"
	UserIDKey    contextKey = "user_id"
	TraceIDKey   contextKey = "trace_id"
)

// 任務結果
type TaskResult struct {
	TaskID   string
	Success  bool
	Duration time.Duration
	Error    error
	Data     interface{}
}

func main() {
	fmt.Println("=== Context 上下文控制範例 ===")

	fmt.Println("\n⏰ 超時控制範例:")
	timeoutDemo()

	fmt.Println("\n🛑 取消控制範例:")
	cancellationDemo()

	fmt.Println("\n📦 值傳遞範例:")
	valuePassingDemo()

	fmt.Println("\n🔗 複合上下文範例:")
	compositeContextDemo()
}

func timeoutDemo() {
	// 創建 3 秒超時的上下文
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	var wg sync.WaitGroup
	results := make(chan TaskResult, 5)

	// 啟動多個任務，有些會超時
	tasks := []struct {
		id       string
		duration time.Duration
	}{
		{"task-1", 1 * time.Second},
		{"task-2", 2 * time.Second},
		{"task-3", 4 * time.Second}, // 會超時
		{"task-4", 5 * time.Second}, // 會超時
		{"task-5", 1500 * time.Millisecond},
	}

	for _, task := range tasks {
		wg.Add(1)
		go timeoutTask(ctx, task.id, task.duration, &wg, results)
	}

	go func() {
		wg.Wait()
		close(results)
	}()

	// 收集結果
	for result := range results {
		status := "✅"
		if !result.Success {
			status = "❌"
		}
		fmt.Printf("%s 任務 %s: 耗時 %v\n", status, result.TaskID, result.Duration)
		if result.Error != nil {
			fmt.Printf("   錯誤: %v\n", result.Error)
		}
	}
}

func timeoutTask(ctx context.Context, taskID string, duration time.Duration, wg *sync.WaitGroup, results chan<- TaskResult) {
	defer wg.Done()

	start := time.Now()

	select {
	case <-time.After(duration):
		// 任務正常完成
		results <- TaskResult{
			TaskID:   taskID,
			Success:  true,
			Duration: time.Since(start),
			Data:     fmt.Sprintf("任務 %s 數據", taskID),
		}

	case <-ctx.Done():
		// 任務被取消或超時
		results <- TaskResult{
			TaskID:   taskID,
			Success:  false,
			Duration: time.Since(start),
			Error:    ctx.Err(),
		}
	}
}

func cancellationDemo() {
	ctx, cancel := context.WithCancel(context.Background())
	var wg sync.WaitGroup

	// 啟動工作者
	for i := 1; i <= 4; i++ {
		wg.Add(1)
		go cancellableWorker(ctx, i, &wg)
	}

	// 2 秒後取消所有工作
	time.Sleep(2 * time.Second)
	fmt.Println("🛑 發送取消信號...")
	cancel()

	wg.Wait()
	fmt.Println("✅ 所有工作者已停止")
}

func cancellableWorker(ctx context.Context, id int, wg *sync.WaitGroup) {
	defer wg.Done()

	fmt.Printf("🔄 工作者 %d 開始工作\n", id)

	for {
		select {
		case <-ctx.Done():
			fmt.Printf("🛑 工作者 %d 收到取消信號: %v\n", id, ctx.Err())
			return

		default:
			// 模擬工作
			fmt.Printf("💼 工作者 %d 正在工作...\n", id)
			time.Sleep(500 * time.Millisecond)
		}
	}
}

func valuePassingDemo() {
	// 創建帶值的上下文
	ctx := context.WithValue(context.Background(), RequestIDKey, "req-12345")
	ctx = context.WithValue(ctx, UserIDKey, "user-67890")
	ctx = context.WithValue(ctx, TraceIDKey, "trace-abcdef")

	var wg sync.WaitGroup

	// 啟動處理鏈
	for i := 1; i <= 3; i++ {
		wg.Add(1)
		go processWithContext(ctx, fmt.Sprintf("handler-%d", i), &wg)
	}

	wg.Wait()
}

func processWithContext(ctx context.Context, handlerName string, wg *sync.WaitGroup) {
	defer wg.Done()

	// 從上下文提取值
	requestID := ctx.Value(RequestIDKey)
	userID := ctx.Value(UserIDKey)
	traceID := ctx.Value(TraceIDKey)

	fmt.Printf("🔍 %s 處理請求:\n", handlerName)
	fmt.Printf("   請求ID: %v\n", requestID)
	fmt.Printf("   用戶ID: %v\n", userID)
	fmt.Printf("   追蹤ID: %v\n", traceID)

	// 模擬處理時間
	time.Sleep(300 * time.Millisecond)

	// 調用下層服務
	callDownstreamService(ctx, handlerName)
}

func callDownstreamService(ctx context.Context, caller string) {
	requestID := ctx.Value(RequestIDKey)
	fmt.Printf("📡 %s 調用下游服務 (請求ID: %v)\n", caller, requestID)
}

func compositeContextDemo() {
	// 創建根上下文，10 秒超時
	rootCtx, rootCancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer rootCancel()

	// 添加值
	ctx := context.WithValue(rootCtx, RequestIDKey, "composite-req-001")

	// 創建子上下文，5 秒超時
	childCtx, childCancel := context.WithTimeout(ctx, 5*time.Second)
	defer childCancel()

	// 創建可取消的孫上下文
	grandChildCtx, grandChildCancel := context.WithCancel(childCtx)

	var wg sync.WaitGroup

	// 啟動使用不同層級上下文的任務
	wg.Add(1)
	go compositeTask(grandChildCtx, "孫任務", 8*time.Second, &wg)

	wg.Add(1)
	go compositeTask(childCtx, "子任務", 6*time.Second, &wg)

	wg.Add(1)
	go compositeTask(rootCtx, "根任務", 12*time.Second, &wg)

	// 3 秒後手動取消孫上下文
	time.Sleep(3 * time.Second)
	fmt.Println("🔪 手動取消孫上下文")
	grandChildCancel()

	wg.Wait()
}

func compositeTask(ctx context.Context, taskName string, workDuration time.Duration, wg *sync.WaitGroup) {
	defer wg.Done()

	requestID := ctx.Value(RequestIDKey)
	fmt.Printf("🚀 %s 開始 (請求ID: %v, 預計耗時: %v)\n", taskName, requestID, workDuration)

	start := time.Now()

	// 分段執行，每段檢查上下文
	segments := int(workDuration / (500 * time.Millisecond))
	for i := 0; i < segments; i++ {
		select {
		case <-ctx.Done():
			elapsed := time.Since(start)
			fmt.Printf("🛑 %s 被取消 (已執行: %v, 原因: %v)\n", taskName, elapsed, ctx.Err())
			return

		case <-time.After(500 * time.Millisecond):
			progress := float64(i+1) / float64(segments) * 100
			fmt.Printf("📈 %s 進度: %.0f%%\n", taskName, progress)
		}
	}

	elapsed := time.Since(start)
	fmt.Printf("✅ %s 完成 (總耗時: %v)\n", taskName, elapsed)
}

// 模擬 HTTP 請求處理
func simulateHTTPRequest() {
	fmt.Println("\n🌐 模擬 HTTP 請求處理:")

	// 創建請求上下文
	ctx := context.WithValue(context.Background(), RequestIDKey, "http-req-"+generateID())
	ctx = context.WithValue(ctx, UserIDKey, "user-123")

	// 5 秒超時
	ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
	defer cancel()

	// 模擬請求處理流程
	if err := handleHTTPRequest(ctx); err != nil {
		fmt.Printf("❌ HTTP 請求處理失敗: %v\n", err)
	} else {
		fmt.Println("✅ HTTP 請求處理成功")
	}
}

func handleHTTPRequest(ctx context.Context) error {
	requestID := ctx.Value(RequestIDKey)
	fmt.Printf("🔍 處理 HTTP 請求 (ID: %v)\n", requestID)

	// 驗證用戶
	if err := validateUser(ctx); err != nil {
		return fmt.Errorf("用戶驗證失敗: %w", err)
	}

	// 處理業務邏輯
	if err := processBusinessLogic(ctx); err != nil {
		return fmt.Errorf("業務處理失敗: %w", err)
	}

	// 記錄日誌
	logRequest(ctx)

	return nil
}

func validateUser(ctx context.Context) error {
	select {
	case <-time.After(200 * time.Millisecond):
		userID := ctx.Value(UserIDKey)
		fmt.Printf("✅ 用戶驗證成功 (用戶ID: %v)\n", userID)
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func processBusinessLogic(ctx context.Context) error {
	// 模擬隨機處理時間
	processingTime := time.Duration(rand.Intn(3000)+1000) * time.Millisecond

	select {
	case <-time.After(processingTime):
		fmt.Printf("✅ 業務邏輯處理完成 (耗時: %v)\n", processingTime)
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

func logRequest(ctx context.Context) {
	requestID := ctx.Value(RequestIDKey)
	userID := ctx.Value(UserIDKey)
	fmt.Printf("📝 記錄請求日誌 - 請求ID: %v, 用戶ID: %v\n", requestID, userID)
}

func generateID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano()%10000)
}
