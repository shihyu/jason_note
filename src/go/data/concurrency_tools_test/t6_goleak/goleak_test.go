package main

import (
	"testing"
	"time"

	"go.uber.org/goleak"
)

// TestLeakyFunc：應該失敗 — goroutine 洩漏
func TestLeakyFunc(t *testing.T) {
	defer goleak.VerifyNone(t)

	go func() {
		// 這個 goroutine 永遠不結束 → 洩漏
		time.Sleep(time.Hour)
	}()
}

// TestCleanFunc：應該通過 — 無洩漏
func TestCleanFunc(t *testing.T) {
	defer goleak.VerifyNone(t)

	done := make(chan struct{})
	go func() {
		defer close(done)
		time.Sleep(10 * time.Millisecond)
	}()
	<-done
}
