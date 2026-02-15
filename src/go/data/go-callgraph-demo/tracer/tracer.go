// Package tracer 提供函數呼叫追蹤功能
// 在每個函數入口呼叫 tracer.Enter()，自動記錄呼叫深度和路徑
package tracer

import (
	"fmt"
	"os"
	"runtime"
	"strings"
	"sync"
	"time"
)

type CallRecord struct {
	Depth    int
	Func     string
	Caller   string
	Time     time.Time
	Duration time.Duration
	IsReturn bool
}

var (
	mu      sync.Mutex
	records []CallRecord
	enabled = true
)

// Enter 在函數入口呼叫，回傳一個 func() 用於 defer
// 用法：defer tracer.Enter()()
func Enter() func() {
	if !enabled {
		return func() {}
	}

	pc := make([]uintptr, 10)
	n := runtime.Callers(2, pc) // skip Callers + Enter
	frames := runtime.CallersFrames(pc[:n])

	// 第一個 frame 是呼叫 Enter() 的函數
	frame, _ := frames.Next()
	funcName := shortName(frame.Function)

	// 第二個 frame 是 caller
	callerFrame, _ := frames.Next()
	callerName := shortName(callerFrame.Function)

	depth := getDepth()
	start := time.Now()

	mu.Lock()
	records = append(records, CallRecord{
		Depth:  depth,
		Func:   funcName,
		Caller: callerName,
		Time:   start,
	})
	mu.Unlock()

	return func() {
		mu.Lock()
		records = append(records, CallRecord{
			Depth:    depth,
			Func:     funcName,
			Duration: time.Since(start),
			IsReturn: true,
		})
		mu.Unlock()
	}
}

// getDepth 根據 goroutine call stack 深度計算縮排
func getDepth() int {
	pc := make([]uintptr, 50)
	n := runtime.Callers(3, pc) // skip Callers + getDepth + Enter
	return n
}

// shortName 從完整路徑擷取 package.Func 或 package.(*Type).Method
func shortName(full string) string {
	if full == "" {
		return "<unknown>"
	}
	// github.com/demo/go-callgraph-demo/service.(*OrderService).PlaceOrder
	// → service.(*OrderService).PlaceOrder
	parts := strings.Split(full, "/")
	return parts[len(parts)-1]
}

// PrintTrace 印出函數呼叫路徑
func PrintTrace() {
	mu.Lock()
	defer mu.Unlock()

	fmt.Println("\n" + strings.Repeat("=", 70))
	fmt.Println("  函數執行路徑（Runtime Function Call Trace）")
	fmt.Println(strings.Repeat("=", 70))

	baseDepth := 100
	for _, r := range records {
		if !r.IsReturn && r.Depth < baseDepth {
			baseDepth = r.Depth
		}
	}

	for _, r := range records {
		indent := strings.Repeat("│ ", r.Depth-baseDepth)
		if r.IsReturn {
			fmt.Printf("  %s└─ return %s [%v]\n", indent, r.Func, r.Duration)
		} else {
			fmt.Printf("  %s┌─ %s  ← called by %s\n", indent, r.Func, r.Caller)
		}
	}
	fmt.Println(strings.Repeat("=", 70))
}

// WriteTraceToFile 將追蹤結果寫入檔案
func WriteTraceToFile(filename string) error {
	mu.Lock()
	defer mu.Unlock()

	f, err := os.Create(filename)
	if err != nil {
		return err
	}
	defer f.Close()

	baseDepth := 100
	for _, r := range records {
		if !r.IsReturn && r.Depth < baseDepth {
			baseDepth = r.Depth
		}
	}

	fmt.Fprintln(f, "# 函數執行路徑（Runtime Function Call Trace）")
	fmt.Fprintln(f, "")
	fmt.Fprintln(f, "```")
	for _, r := range records {
		indent := strings.Repeat("│ ", r.Depth-baseDepth)
		if r.IsReturn {
			fmt.Fprintf(f, "%s└─ return %s [%v]\n", indent, r.Func, r.Duration)
		} else {
			fmt.Fprintf(f, "%s┌─ %s  ← %s\n", indent, r.Func, r.Caller)
		}
	}
	fmt.Fprintln(f, "```")

	return nil
}

// Reset 清除記錄
func Reset() {
	mu.Lock()
	records = records[:0]
	mu.Unlock()
}
