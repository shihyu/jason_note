package main

import (
	"fmt"
	"os"
	"runtime/trace"
	"sync"
)

func main() {
	f, err := os.Create("trace.out")
	if err != nil {
		panic(err)
	}
	defer f.Close()
	trace.Start(f)
	defer trace.Stop()

	var wg sync.WaitGroup
	for i := 0; i < 5; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			// 模擬工作
			sum := 0
			for j := 0; j < 1000; j++ {
				sum += j
			}
			_ = sum
		}(i)
	}
	wg.Wait()
	fmt.Println("trace.out 已生成")
}
