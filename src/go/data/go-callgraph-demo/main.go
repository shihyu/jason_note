package main

import (
	"fmt"
	"math/rand"
	"os"
	"runtime/trace"
	"time"

	"github.com/demo/go-callgraph-demo/server"
	"github.com/demo/go-callgraph-demo/service"
)

func main() {
	// 動態 trace：若帶 --trace 參數則啟用
	if len(os.Args) > 1 && os.Args[1] == "--trace" {
		f, err := os.Create("trace.out")
		if err != nil {
			fmt.Fprintf(os.Stderr, "create trace: %v\n", err)
			os.Exit(1)
		}
		defer f.Close()
		if err := trace.Start(f); err != nil {
			fmt.Fprintf(os.Stderr, "start trace: %v\n", err)
			os.Exit(1)
		}
		defer trace.Stop()
		fmt.Println("[trace] 已啟用 runtime/trace，結果將寫入 trace.out")
	}

	app := server.NewApp("DemoApp")
	app.Init()

	// 模擬處理多個請求
	userSvc := service.NewUserService()
	orderSvc := service.NewOrderService()

	users := []string{"Alice", "Bob", "Charlie"}
	for _, name := range users {
		user := userSvc.CreateUser(name)
		fmt.Printf("建立使用者: %s (ID: %s)\n", user.Name, user.ID)

		// 隨機建立訂單
		count := rand.Intn(3) + 1
		for i := 0; i < count; i++ {
			order := orderSvc.PlaceOrder(user.ID, randomProduct(), rand.Float64()*1000)
			fmt.Printf("  訂單: %s - %s $%.2f\n", order.ID, order.Product, order.Amount)
		}
	}

	// 執行報表
	report := orderSvc.GenerateReport()
	fmt.Printf("\n=== 報表 ===\n%s\n", report)

	app.Shutdown()
}

func randomProduct() string {
	products := []string{"手機", "筆電", "耳機", "鍵盤", "螢幕"}
	rand.New(rand.NewSource(time.Now().UnixNano()))
	return products[rand.Intn(len(products))]
}
