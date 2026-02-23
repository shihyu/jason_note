package main

import "fmt"

func main() {
	counter := 0
	done := make(chan bool)

	go func() {
		counter++ // ← Data Race！
		done <- true
	}()

	counter++  // ← Data Race！
	<-done
	fmt.Println(counter)
}
