// Go 並行程式設計範例 02: Channel 通訊
// 展示無緩衝和緩衝 Channel 的使用方式

package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("=== Channel 通訊範例 ===")

	fmt.Println("\n📡 無緩衝通道範例:")
	unbufferedChannelDemo()

	fmt.Println("\n📦 緩衝通道範例:")
	bufferedChannelDemo()
}

// 無緩衝通道範例
func unbufferedChannelDemo() {
	messages := make(chan string)

	// 發送者 goroutine
	go func() {
		data := []string{"Hello", "World", "From", "Go", "Channels"}
		for i, msg := range data {
			fmt.Printf("📤 準備發送: %s\n", msg)
			messages <- msg
			fmt.Printf("✅ 已發送: %s (%d/%d)\n", msg, i+1, len(data))
			time.Sleep(300 * time.Millisecond)
		}
		close(messages)
	}()

	// 接收者
	fmt.Println("📥 開始接收訊息...")
	for msg := range messages {
		fmt.Printf("📨 接收到: %s\n", msg)
		time.Sleep(200 * time.Millisecond)
	}
	fmt.Println("📪 所有訊息接收完畢")
}

// 緩衝通道範例
func bufferedChannelDemo() {
	// 創建容量為 3 的緩衝通道
	buffer := make(chan int, 3)

	// 發送者
	go func() {
		for i := 1; i <= 6; i++ {
			fmt.Printf("📤 嘗試發送: %d\n", i)
			buffer <- i
			fmt.Printf("✅ 成功發送: %d (緩衝區: %d/%d)\n", i, len(buffer), cap(buffer))
			time.Sleep(200 * time.Millisecond)
		}
		close(buffer)
	}()

	// 接收者故意延遲
	fmt.Println("⏰ 接收者延遲 1 秒開始處理...")
	time.Sleep(1 * time.Second)

	for value := range buffer {
		fmt.Printf("📨 處理數據: %d\n", value)
		time.Sleep(400 * time.Millisecond)
	}
	fmt.Println("📪 所有數據處理完畢")
}
