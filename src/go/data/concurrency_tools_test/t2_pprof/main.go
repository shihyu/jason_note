package main

import (
	"fmt"
	"net/http"
	_ "net/http/pprof"
	"runtime"
	"sync"
	"time"
)

var (
	counter int
	mu      sync.Mutex
)

func worker() {
	for {
		mu.Lock()
		counter++
		mu.Unlock()
		time.Sleep(time.Millisecond)
	}
}

func main() {
	runtime.SetMutexProfileFraction(1)
	runtime.SetBlockProfileRate(1)

	go func() {
		http.ListenAndServe(":16060", nil)
	}()

	// 啟動幾個 worker goroutine
	for i := 0; i < 3; i++ {
		go worker()
	}

	// 等待 server 啟動
	time.Sleep(100 * time.Millisecond)
	fmt.Println("pprof server running at :16060")
	fmt.Println("endpoints: /debug/pprof/goroutine, /debug/pprof/mutex, /debug/pprof/block")

	// 讓 server 跑一段時間後自動退出（給外部 curl 充足時間）
	time.Sleep(5 * time.Second)
	fmt.Println("✅ pprof server 正常啟動並運行")
}
