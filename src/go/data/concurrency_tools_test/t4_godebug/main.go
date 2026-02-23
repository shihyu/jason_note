package main

import (
	"fmt"
	"sync"
)

func main() {
	var wg sync.WaitGroup
	for i := 0; i < 4; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			sum := 0
			for j := 0; j < 100000; j++ {
				sum += j
			}
			fmt.Printf("goroutine %d done\n", id)
		}(i)
	}
	wg.Wait()
}
