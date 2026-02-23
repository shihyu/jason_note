package main

import (
	"context"
	"fmt"
	"log"
	"time"
)

func doWork(ctx context.Context, workDuration time.Duration) error {
	done := make(chan struct{})
	go func() {
		// 模擬實際工作
		time.Sleep(workDuration)
		close(done)
	}()

	select {
	case <-done:
		return nil
	case <-ctx.Done():
		return fmt.Errorf("goroutine timeout: %w", ctx.Err())
	}
}

func main() {
	// 測試1：工作在超時內完成
	ctx1, cancel1 := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel1()
	if err := doWork(ctx1, 100*time.Millisecond); err != nil {
		log.Println("測試1 失敗:", err)
	} else {
		fmt.Println("✅ 測試1：工作正常完成（100ms < 5s 超時）")
	}

	// 測試2：工作超時
	ctx2, cancel2 := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel2()
	if err := doWork(ctx2, 5*time.Second); err != nil {
		fmt.Println("✅ 測試2：偵測到超時或卡死:", err)
	} else {
		log.Println("測試2 失敗：應該超時但沒有")
	}
}
