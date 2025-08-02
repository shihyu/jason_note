// Go 並行程式設計範例 10: Pipeline 管道模式
// 展示數據處理管道和扇出-扇入模式

package main

import (
	"fmt"
	"math"
	"strings"
	"sync"
	"time"
)

// 數據項目
type DataItem struct {
	ID        int
	Content   string
	Value     float64
	Timestamp time.Time
	Metadata  map[string]interface{}
}

func main() {
	fmt.Println("=== Pipeline 管道模式範例 ===")

	fmt.Println("\n🔄 基本管道處理:")
	basicPipelineDemo()

	fmt.Println("\n🌟 扇出-扇入模式:")
	fanOutFanInDemo()

	fmt.Println("\n⚡ 複雜數據處理管道:")
	complexPipelineDemo()
}

func basicPipelineDemo() {
	// 階段1: 數據生成
	numbers := generateNumbers(1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

	// 階段2: 平方計算
	squares := calculateSquares(numbers)

	// 階段3: 過濾大於25的數
	filtered := filterGreaterThan(squares, 25)

	// 階段4: 格式化輸出
	formatted := formatNumbers(filtered)

	// 收集結果
	fmt.Println("📊 基本管道結果:")
	for result := range formatted {
		fmt.Printf("   %s\n", result)
	}
}

func generateNumbers(nums ...int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for _, n := range nums {
			fmt.Printf("🔢 生成數字: %d\n", n)
			out <- n
			time.Sleep(50 * time.Millisecond)
		}
	}()
	return out
}

func calculateSquares(in <-chan int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			square := n * n
			fmt.Printf("📐 計算平方: %d² = %d\n", n, square)
			out <- square
			time.Sleep(30 * time.Millisecond)
		}
	}()
	return out
}

func filterGreaterThan(in <-chan int, threshold int) <-chan int {
	out := make(chan int)
	go func() {
		defer close(out)
		for n := range in {
			if n > threshold {
				fmt.Printf("✅ 通過過濾: %d > %d\n", n, threshold)
				out <- n
			} else {
				fmt.Printf("❌ 未通過過濾: %d <= %d\n", n, threshold)
			}
		}
	}()
	return out
}

func formatNumbers(in <-chan int) <-chan string {
	out := make(chan string)
	go func() {
		defer close(out)
		for n := range in {
			formatted := fmt.Sprintf("結果: %d", n)
			fmt.Printf("🎨 格式化: %s\n", formatted)
			out <- formatted
		}
	}()
	return out
}

func fanOutFanInDemo() {
	// 生成數據
	data := generateData(20)

	// 扇出到多個處理器
	processor1 := processData(data, "處理器-1")
	processor2 := processData(data, "處理器-2")
	processor3 := processData(data, "處理器-3")

	// 扇入合併結果
	merged := fanInResults(processor1, processor2, processor3)

	// 收集和顯示結果
	fmt.Println("📊 扇出-扇入結果:")
	results := collectResults(merged)

	fmt.Printf("   總共處理了 %d 個項目\n", len(results))
	for processor, count := range countByProcessor(results) {
		fmt.Printf("   %s: %d 個項目\n", processor, count)
	}
}

func generateData(count int) <-chan DataItem {
	out := make(chan DataItem)
	go func() {
		defer close(out)
		for i := 1; i <= count; i++ {
			item := DataItem{
				ID:        i,
				Content:   fmt.Sprintf("data-item-%d", i),
				Value:     float64(i * 10),
				Timestamp: time.Now(),
				Metadata:  map[string]interface{}{"source": "generator"},
			}

			fmt.Printf("📦 生成數據: %s\n", item.Content)
			out <- item
			time.Sleep(100 * time.Millisecond)
		}
	}()
	return out
}

func processData(in <-chan DataItem, processorName string) <-chan DataItem {
	out := make(chan DataItem)
	go func() {
		defer close(out)
		for item := range in {
			// 模擬處理時間
			time.Sleep(time.Duration(200+item.ID*10) * time.Millisecond)

			// 處理數據
			processedItem := item
			processedItem.Value = math.Sqrt(item.Value)
			processedItem.Content = strings.ToUpper(item.Content)
			processedItem.Metadata["processor"] = processorName
			processedItem.Metadata["processed_at"] = time.Now()

			fmt.Printf("⚙️  %s 處理: %s (新值: %.2f)\n",
				processorName, processedItem.Content, processedItem.Value)

			out <- processedItem
		}
		fmt.Printf("✅ %s 完成處理\n", processorName)
	}()
	return out
}

func fanInResults(channels ...<-chan DataItem) <-chan DataItem {
	var wg sync.WaitGroup
	out := make(chan DataItem)

	// 為每個輸入通道啟動一個 goroutine
	multiplex := func(c <-chan DataItem) {
		defer wg.Done()
		for item := range c {
			out <- item
		}
	}

	wg.Add(len(channels))
	for _, c := range channels {
		go multiplex(c)
	}

	// 等待所有輸入完成後關閉輸出通道
	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

func collectResults(in <-chan DataItem) []DataItem {
	var results []DataItem
	for item := range in {
		results = append(results, item)
		fmt.Printf("📥 收集結果: %s from %v\n",
			item.Content, item.Metadata["processor"])
	}
	return results
}

func countByProcessor(results []DataItem) map[string]int {
	counts := make(map[string]int)
	for _, item := range results {
		if processor, ok := item.Metadata["processor"]; ok {
			counts[processor.(string)]++
		}
	}
	return counts
}

func complexPipelineDemo() {
	// 創建複雜的數據處理管道

	// 階段1: 原始數據生成
	rawData := generateComplexData()

	// 階段2: 數據清洗
	cleanedData := cleanData(rawData)

	// 階段3: 數據分析 (扇出到多個分析器)
	analyzer1 := analyzeData(cleanedData, "統計分析")
	analyzer2 := analyzeData(cleanedData, "趨勢分析")
	analyzer3 := analyzeData(cleanedData, "異常檢測")

	// 階段4: 結果聚合 (扇入)
	aggregated := aggregateAnalysis(analyzer1, analyzer2, analyzer3)

	// 階段5: 報告生成
	reports := generateReports(aggregated)

	// 收集最終結果
	fmt.Println("📋 複雜管道處理結果:")
	for report := range reports {
		fmt.Printf("   📄 %s\n", report)
	}
}

func generateComplexData() <-chan DataItem {
	out := make(chan DataItem)
	go func() {
		defer close(out)

		datasets := []string{
			"用戶行為數據", "交易記錄", "系統日誌", "性能指標",
			"錯誤報告", "用戶反饋", "市場數據", "庫存信息",
		}

		for i, dataset := range datasets {
			item := DataItem{
				ID:        i + 1,
				Content:   dataset,
				Value:     float64(100 + i*50),
				Timestamp: time.Now().Add(-time.Duration(i) * time.Hour),
				Metadata: map[string]interface{}{
					"quality": 0.7 + float64(i%3)*0.1,
					"size_mb": 10 + i*5,
					"source":  "data_warehouse",
				},
			}

			fmt.Printf("📊 生成複雜數據: %s (品質: %.1f)\n",
				item.Content, item.Metadata["quality"])
			out <- item
			time.Sleep(200 * time.Millisecond)
		}
	}()
	return out
}

func cleanData(in <-chan DataItem) <-chan DataItem {
	out := make(chan DataItem)
	go func() {
		defer close(out)
		for item := range in {
			// 模擬數據清洗過程
			time.Sleep(150 * time.Millisecond)

			quality := item.Metadata["quality"].(float64)
			if quality < 0.8 {
				// 提升數據品質
				item.Metadata["quality"] = quality + 0.2
				item.Metadata["cleaned"] = true
				fmt.Printf("🧹 清洗數據: %s (提升品質: %.1f -> %.1f)\n",
					item.Content, quality, item.Metadata["quality"])
			} else {
				item.Metadata["cleaned"] = false
				fmt.Printf("✨ 數據已清潔: %s (品質: %.1f)\n",
					item.Content, quality)
			}

			out <- item
		}
	}()
	return out
}

func analyzeData(in <-chan DataItem, analysisType string) <-chan string {
	out := make(chan string)
	go func() {
		defer close(out)
		for item := range in {
			// 模擬不同類型的分析
			time.Sleep(300 * time.Millisecond)

			var analysis string
			switch analysisType {
			case "統計分析":
				analysis = fmt.Sprintf("%s: 平均值 %.2f, 品質 %.1f",
					item.Content, item.Value, item.Metadata["quality"])
			case "趨勢分析":
				trend := "上升"
				if item.ID%2 == 0 {
					trend = "下降"
				}
				analysis = fmt.Sprintf("%s: 趨勢 %s, 變化率 %.1f%%",
					item.Content, trend, item.Value*0.1)
			case "異常檢測":
				anomaly := "正常"
				if item.Value > 300 {
					anomaly = "異常"
				}
				analysis = fmt.Sprintf("%s: 狀態 %s, 風險評分 %.0f",
					item.Content, anomaly, item.Value*0.3)
			}

			fmt.Printf("🔍 %s: %s\n", analysisType, analysis)
			out <- analysis
		}
		fmt.Printf("✅ %s 完成\n", analysisType)
	}()
	return out
}

func aggregateAnalysis(channels ...<-chan string) <-chan string {
	out := make(chan string)
	var wg sync.WaitGroup

	// 收集所有分析結果
	wg.Add(len(channels))
	for i, ch := range channels {
		go func(id int, c <-chan string) {
			defer wg.Done()
			for analysis := range c {
				aggregated := fmt.Sprintf("聚合結果 %d: %s", id+1, analysis)
				out <- aggregated
			}
		}(i, ch)
	}

	go func() {
		wg.Wait()
		close(out)
	}()

	return out
}

func generateReports(in <-chan string) <-chan string {
	out := make(chan string)
	go func() {
		defer close(out)
		reportID := 1
		for analysis := range in {
			// 模擬報告生成
			time.Sleep(100 * time.Millisecond)

			report := fmt.Sprintf("📄 報告 #%d: %s [生成時間: %s]",
				reportID, analysis, time.Now().Format("15:04:05"))

			fmt.Printf("📝 生成報告: 報告 #%d\n", reportID)
			out <- report
			reportID++
		}
	}()
	return out
}
