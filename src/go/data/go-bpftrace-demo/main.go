package main

import (
	"fmt"
	"time"
)

//go:noinline
func Step1(msg string) {
	fmt.Println("執行步驟 1:", msg)
}

//go:noinline
func Step2(count int) {
	fmt.Println("執行步驟 2，次數:", count)
}

func main() {
	for {
		Step1("Hello")
		Step2(42)
		time.Sleep(2 * time.Second)
	}
}
