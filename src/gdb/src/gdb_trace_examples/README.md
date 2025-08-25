# GDB 程式追蹤範例

這個專案展示了多種使用 GDB 追蹤程式執行流程的方法。

## 檔案結構

```
gdb_trace_examples/
├── demo.c                      # 主要測試程式
├── Makefile                     # 建置和測試腳本
├── basic_trace/                # 方法一：基本追蹤
│   └── basic_trace.gdb
├── python_trace/                # 方法二：Python 腳本
│   └── trace.py
├── batch_trace/                 # 方法三：批次命令
│   └── trace_commands.gdb
├── record_replay/               # 方法四：記錄重播
│   └── record_replay.gdb
└── analysis_tools/              # 分析工具
    └── analyze_trace.py
```

## 快速開始

```bash
# 編譯程式
make build

# 執行所有追蹤方法
make test-all

# 分析追蹤結果
make analyze
```

## 各種追蹤方法

### 方法一：基本 GDB 追蹤
```bash
make test-basic
```
輸出檔案：`basic_trace.txt`

### 方法二：Python 腳本追蹤
```bash
make test-python
```
輸出檔案：`trace_log.txt`

### 方法三：批次命令追蹤
```bash
make test-batch
```
輸出檔案：`auto_trace.txt`

### 方法四：記錄/重播功能
```bash
make test-record
```
注意：此功能可能不支援所有系統

## 其他命令

- `make run` - 正常執行程式（不含 GDB）
- `make profile` - 使用 gprof 產生呼叫圖
- `make clean` - 清理所有產生的檔案
- `make help` - 顯示幫助訊息

## 追蹤結果分析

執行 `make analyze` 會分析追蹤檔案並顯示：
- 函式呼叫統計
- 斷點觸發次數
- 執行時間分析
- 呼叫堆疊深度

## 注意事項

1. 編譯時需要加入 `-g` 參數以包含除錯資訊
2. 追蹤會顯著降低程式執行速度
3. 長時間執行的程式可能產生很大的追蹤檔案
4. 記錄/重播功能可能不支援所有系統架構