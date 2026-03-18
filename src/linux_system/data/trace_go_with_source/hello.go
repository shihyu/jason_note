package main

import (
	"fmt"
)

func swap(a, b int) (int, int) {
	return b, a
}

func main() {
	a, b := 1, 2
	fmt.Printf("Before swap: a = %d, b = %d\n", a, b)
	// fmt.Println("Hello, World!")
	a, b = swap(a, b)
	fmt.Printf("After swap: a = %d, b = %d\n", a, b)
}
