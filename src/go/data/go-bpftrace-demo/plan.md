# go-bpftrace-demo 計畫

## 任務目標

為目前的 Go 範例程式建立標準化專案入口，並擴充 `Makefile` 讓 `bpftrace` 測試可直接透過標準目標執行。`Makefile` 除了一致的 build、run、test、clean 流程外，還需支援 probe 列表、單點 trace、全量 trace、背景啟動與 smoke test。

## 專案結構組織

- 專案資料夾名稱：`go-bpftrace-demo`
- 組織原則：將程式碼、測試、文件集中在同一專案目錄下，避免根目錄散落建置產物與驗證檔
- 預計結構：

```text
go-bpftrace-demo/
├── Makefile
├── go.mod
├── cmd/
│   └── demo/
│       └── main.go
├── tests/
│   ├── main_behavior_test.go
│   └── tmp/
└── docs/
    ├── README.md
    └── ARCHITECTURE.md
```

## 預期產出

- `Makefile`
  - `make`：顯示 help
  - `make build`：編譯 `myapp`
  - `make run`：執行範例程式
  - `make test`：執行正式測試
  - `make clean`：移除建置產物與測試暫存
  - `make trace-list`：列出 `main.*` probes
  - `make trace-all`：追蹤 `main.*`
  - `make trace-main`：追蹤 `main.main`
  - `make trace-step1`：追蹤 `main.Step1`
  - `make trace-step2`：追蹤 `main.Step2`
  - `make run-bg`：背景啟動 `myapp` 並記錄 PID
  - `make stop-bg`：停止背景 `myapp`
  - `make trace-smoke`：自動背景啟動、短時間 trace、停止程式
- `tests/main_behavior_test.go`
  - 驗證核心輸出流程可被呼叫
- `docs/README.md`
  - 快速開始、執行範例、`bpftrace` 目標說明
- `docs/ARCHITECTURE.md`
  - ASCII 架構圖、資料流、trace 流程

## 架構設計

### 系統架構

```text
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  cmd/demo    │─────>│ main.Step1   │─────>│ stdout       │
│  main.main   │      │ main.Step2   │      │ trace target │
└──────────────┘      └──────────────┘      └──────────────┘
        │                     │                     │
        v                     v                     v
   迴圈驅動流程          輸出固定訊息          提供 uprobe 符號
```

### 資料流範例

1. `main.main` 進入無限迴圈。
2. 呼叫 `Step1("Hello")`，輸出步驟 1 訊息。
3. 呼叫 `Step2(42)`，輸出步驟 2 訊息。
4. `time.Sleep(2 * time.Second)` 等待後重複。
5. 外部可使用 `bpftrace` 對 `main.main`、`main.Step1`、`main.Step2` 下 `uprobe`。
6. `Makefile` 提供背景啟動與 smoke test，讓 trace 驗證流程可重複執行。

## Makefile 規範

### 必備目標

- `make`：顯示可用目標與範例
- `make build`：編譯專案，輸出 `./myapp`
- `make run`：執行 `./myapp`
- `make test`：執行 `go test ./...`
- `make clean`：刪除 `./myapp` 與 `tests/tmp/*`
- `make trace-list`：列出 `uprobe:./myapp:main.*`
- `make trace-all`：執行 `uprobe:./myapp:main.*`
- `make trace-main`：執行 `uprobe:./myapp:main.main`
- `make trace-step1`：執行 `uprobe:./myapp:main.Step1`
- `make trace-step2`：執行 `uprobe:./myapp:main.Step2`
- `make run-bg`：背景啟動 `./myapp`，將 PID 寫入 `tests/tmp/myapp.pid`
- `make stop-bg`：讀取 `tests/tmp/myapp.pid` 並停止程式
- `make trace-smoke`：自動完成 `build -> run-bg -> trace -> stop-bg`

### 設計要求

- `.DEFAULT_GOAL := help`
- 使用 Go 原生工具鏈，不引入額外建置工具
- `clean` 必須同時清掉建置產物與測試暫存
- help 內容需明確列出五個標準目標
- `trace-*` 目標可直接包 `sudo bpftrace`
- `run-bg` 與 `stop-bg` 必須具備冪等性，避免殘留背景程序
- `trace-smoke` 須限制追蹤時間，避免無限阻塞
- 背景執行的 PID、trace 暫存輸出集中放在 `tests/tmp/`

## build/debug/test 指令

- Build：`make build`
- Run：`make run`
- Test：`make test`
- 列 probe：`make trace-list`
- 全量 trace：`make trace-all`
- 單點 trace：`make trace-main` / `make trace-step1` / `make trace-step2`
- Smoke test：`make trace-smoke`
- 直接除錯建置：`go build -o myapp ./cmd/demo`
- 直接追蹤符號：`sudo bpftrace -e 'uprobe:./myapp:main.* { printf("時間: %llu ms | 函數: %s\n", elapsed / 1000000, probe); }'`

## 驗收標準

- `make` 無參數時顯示 help
- `make build` 成功產生 `myapp`
- `make run` 可執行現有範例程式
- `make test` 可執行正式測試並回報結果
- `make clean` 可移除 `myapp` 與 `tests/tmp/` 內容
- `make trace-list` 可列出 `main.main`、`main.Step1`、`main.Step2`
- `make trace-main`、`make trace-step1`、`make trace-step2` 可成功啟動對應 trace
- `make trace-smoke` 可在有限時間內完成 trace 並自動停止背景程式
- 所有 `bpftrace` 相關目標都需至少實測一次並回報結果
- 文件數量不超過 `docs/` 內 2 個 Markdown 檔案

## 子任務拆解

1. 建立 `plan.md`，確認目標、結構、Makefile 規格。
2. 建立或整理 Go 專案結構，使建置入口穩定。
3. 先寫測試，定義可驗證的行為。
4. 擴充 `Makefile`，加入 `bpftrace` 相關目標與背景流程。
5. 執行 `make build`、`make test`、所有 `bpftrace` 相關目標、必要的 `make clean` 驗證。
6. 補上 `docs/README.md` 與 `docs/ARCHITECTURE.md` 的 trace 使用說明。

## 子任務進度

- [x] 1. 已建立 `plan.md`
- [x] 2. 已整理 Go 專案結構為 `cmd/demo` + `tests` + `docs`
- [x] 3. 已新增 `tests/main_behavior_test.go`
- [x] 4. 已擴充 `Makefile` 的 `bpftrace` 目標與背景流程
- [ ] 5. 待完成所有 `bpftrace` 目標的逐項實測
- [x] 6. 已補上文件中的 `bpftrace` 目標說明
