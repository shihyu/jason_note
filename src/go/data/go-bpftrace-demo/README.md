# go-bpftrace-demo

最小 Go 範例程式，示範如何用 `bpftrace` 對 Go 函數做 `uprobe` 追蹤。

## 快速開始

```bash
make build
make run
make test
```

## 系統架構

```text
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│  main.main  │─────>│ Step1/Step2  │─────>│   stdout    │
│  無限迴圈    │      │  格式化訊息   │      │  trace 點   │
└─────────────┘      └──────────────┘      └─────────────┘
```

資料流：
1. `main.main` 進入無限迴圈
2. 呼叫 `Step1("Hello")` → 輸出步驟 1 訊息
3. 呼叫 `Step2(42)` → 輸出步驟 2 訊息
4. `time.Sleep(2s)` 後重複
5. 外部可用 `bpftrace` 對三個符號掛 `uprobe`

## bpftrace 目標

```bash
sudo make trace-list     # 列出 main.* probes
sudo make trace-main     # 追蹤 main.main
sudo make trace-step1    # 追蹤 main.Step1
sudo make trace-step2    # 追蹤 main.Step2
sudo make trace-flow     # 追蹤所有 main.* 函數
sudo make trace-latency  # 統計 Step1/Step2 耗時
sudo make trace-count    # 統計函數命中次數
sudo make trace-stack    # 顯示 Step1 呼叫堆疊
sudo make trace-smoke    # 自動背景啟動 + 短時間 trace + 停止
```

## Trace 流程（trace-smoke）

```text
make run-bg ──> myapp 背景執行 ──> sudo bpftrace (3s) ──> make stop-bg
                  寫入 tmp/myapp.pid    命中 uprobe         停止程序
```

## 手動 trace 範例

終端機 1：
```bash
make run
```

終端機 2：
```bash
sudo bpftrace -e 'uprobe:./myapp:main.* { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'
```

## 輸出範例

```text
執行步驟 1: Hello
執行步驟 2，次數: 42
```
