// Go 並行程式設計範例 03: Select 多路復用
// 展示 Select 語句在多通道操作中的使用

package main

import (
	"fmt"
	"time"
)

func main() {
	fmt.Println("=== Select 多路復用範例 ===")

	ch1 := make(chan string)
	ch2 := make(chan string)
	quit := make(chan bool)

	// 啟動發送者
	go sender1(ch1)
	go sender2(ch2)
	go timeoutController(quit)

	// Select 多路復用接收
	selectMultiplexer(ch1, ch2, quit)
}

func sender1(ch chan string) {
	messages := []string{"訊息A-1", "訊息A-2", "訊息A-3", "訊息A-4", "訊息A-5"}
	for i, msg := range messages {
		time.Sleep(800 * time.Millisecond)
		select {
		case ch <- msg:
			fmt.Printf("📤 通道1發送: %s (%d/%d)\n", msg, i+1, len(messages))
		default:
			fmt.Printf("⚠️  通道1發送失敗: %s\n", msg)
		}
	}
}

func sender2(ch chan string) {
	messages := []string{"訊息B-1", "訊息B-2", "訊息B-3", "訊息B-4"}
	for i, msg := range messages {
		time.Sleep(1200 * time.Millisecond)
		select {
		case ch <- msg:
			fmt.Printf("📤 通道2發送: %s (%d/%d)\n", msg, i+1, len(messages))
		default:
			fmt.Printf("⚠️  通道2發送失敗: %s\n", msg)
		}
	}
}

func timeoutController(quit chan bool) {
	time.Sleep(8 * time.Second)
	quit <- true
}

func selectMultiplexer(ch1, ch2 chan string, quit chan bool) {
	fmt.Println("🎯 開始多路復用監聽...")

	for {
		select {
		case msg1 := <-ch1:
			fmt.Printf("📨 從通道1接收: %s\n", msg1)

		case msg2 := <-ch2:
			fmt.Printf("📨 從通道2接收: %s\n", msg2)

		case <-quit:
			fmt.Println("🛑 接收到退出信號")
			return

		case <-time.After(600 * time.Millisecond):
			fmt.Println("⏰ 等待中...（600ms 超時）")
		}
	}
}
