package main_test

import (
	"bufio"
	"context"
	"os/exec"
	"testing"
	"time"
)

func TestDemoPrintsAllMessages(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 8*time.Second)
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

	want := map[string]bool{
		"執行步驟 1: Hello":    false,
		"執行步驟 2，次數: 42":   false,
		"分配記憶體: 256 bytes": false,
		"Worker goroutine 執行中": false,
	}

	scanner := bufio.NewScanner(stdout)
	for scanner.Scan() {
		line := scanner.Text()
		if _, ok := want[line]; ok {
			want[line] = true
		}
		allSeen := true
		for _, v := range want {
			if !v {
				allSeen = false
				break
			}
		}
		if allSeen {
			break
		}
	}

	_ = cmd.Process.Kill()
	_ = cmd.Wait()

	if err := scanner.Err(); err != nil {
		t.Fatalf("讀取輸出失敗: %v", err)
	}
	for msg, seen := range want {
		if !seen {
			t.Errorf("未看到輸出: %q", msg)
		}
	}
}
