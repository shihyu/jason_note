package main_test

import (
	"bufio"
	"context"
	"os/exec"
	"testing"
	"time"
)

func TestDemoPrintsStepMessages(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	cmd := exec.CommandContext(ctx, "./myapp")
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		t.Fatalf("無法建立 stdout pipe: %v", err)
	}
	cmd.Stderr = nil

	if err := cmd.Start(); err != nil {
		t.Fatalf("無法啟動程式: %v", err)
	}

	var sawStep1 bool
	var sawStep2 bool
	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		line := scanner.Text()
		if line == "執行步驟 1: Hello" {
			sawStep1 = true
		}
		if line == "執行步驟 2，次數: 42" {
			sawStep2 = true
		}
		if sawStep1 && sawStep2 {
			break
		}
	}

	_ = cmd.Process.Kill()
	_ = cmd.Wait()

	if err := scanner.Err(); err != nil {
		t.Fatalf("讀取輸出失敗: %v", err)
	}
	if !sawStep1 || !sawStep2 {
		t.Fatalf("輸出不完整: step1=%t step2=%t", sawStep1, sawStep2)
	}
}
