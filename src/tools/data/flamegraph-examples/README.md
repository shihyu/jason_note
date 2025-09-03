# Flamegraph Examples 火焰圖範例集

這個目錄包含了多個用於學習和實踐火焰圖分析的範例程式。所有範例都已經過測試驗證。

## 檔案結構

```
flamegraph-examples/
├── cpu_intensive.cpp        # CPU 密集型運算範例
├── memory_allocation.cpp    # 記憶體分配問題範例
├── lock_contention.cpp      # 多執行緒鎖競爭範例
├── hft_simulation.cpp       # 高頻交易系統模擬
├── compare_performance.sh   # 性能比較腳本
├── analyze_flamegraph.py    # 火焰圖數據分析工具
├── Makefile                 # 自動化編譯和測試
└── README.md               # 本文件
```

## 快速開始

### 1. 編譯所有範例

```bash
make all
```

### 2. 執行測試

```bash
make test
```

### 3. 執行性能基準測試

```bash
make benchmark
```

## 各範例說明

### 1. CPU 密集型範例 (cpu_intensive.cpp)

模擬 CPU 密集型運算，包含：
- 質數計算（低效版本）
- 費波那契數列（遞迴）
- 矩陣乘法

**編譯與執行：**
```bash
make cpu_intensive
./cpu_intensive
```

### 2. 記憶體分配範例 (memory_allocation.cpp)

展示常見的記憶體分配問題：
- 頻繁的小記憶體分配
- vector 重新分配問題
- 字串拼接的記憶體問題
- 物件池優化方案

**編譯與執行：**
```bash
make memory_allocation
./memory_allocation
```

### 3. 鎖競爭範例 (lock_contention.cpp)

比較不同的同步策略：
- 粗粒度鎖（bad）
- 細粒度鎖（better）
- 原子操作（atomic）

**編譯與執行：**
```bash
make lock_contention
./lock_contention bad    # 測試差的鎖策略
./lock_contention better # 測試較好的鎖策略
./lock_contention atomic # 測試原子操作
```

### 4. 高頻交易模擬 (hft_simulation.cpp)

模擬高頻交易系統的關鍵路徑：
- 訂單簿更新
- 交易信號生成
- 風險管理
- 延遲測量

**編譯與執行：**
```bash
make hft_simulation
./hft_simulation
```

## 生成火焰圖

### 安裝 FlameGraph 工具

```bash
make install-flamegraph
```

### 生成 CPU 火焰圖

```bash
make flamegraph-cpu
# 火焰圖將保存在 flamegraphs/cpu.svg
```

### 分析火焰圖數據

```bash
# 分析 folded 格式的數據
python3 analyze_flamegraph.py flamegraphs/cpu.folded

# 顯示前 10 個熱點
python3 analyze_flamegraph.py flamegraphs/cpu.folded -n 10

# 搜尋特定函數
python3 analyze_flamegraph.py flamegraphs/cpu.folded -s "is_prime"
```

## 性能比較

### 執行自動化比較

```bash
make compare
# 或直接執行腳本
./compare_performance.sh
```

這將會：
1. 編譯基準版本（-O2）和優化版本（-O3）
2. 收集性能數據
3. 生成對比火焰圖
4. 輸出性能統計

## 性能測試結果

在測試環境中的典型結果：

| 程式 | 模式 | 執行時間 |
|------|------|----------|
| lock_contention | bad (粗粒度鎖) | ~22 ms |
| lock_contention | better (細粒度鎖) | ~24 ms |
| lock_contention | atomic (原子操作) | ~5 ms |
| hft_simulation | -O2 優化 | ~1.24 μs/tick |
| hft_simulation | -O3 優化 | ~0.89 μs/tick |

## 依賴要求

- **編譯器**: g++ (支援 C++11)
- **性能工具**: perf (用於生成火焰圖)
- **Python**: python3 (用於分析腳本)
- **Git**: 用於下載 FlameGraph 工具

### 安裝依賴

Ubuntu/Debian:
```bash
sudo apt-get install g++ linux-tools-common linux-tools-generic python3 git
```

RHEL/CentOS:
```bash
sudo yum install gcc-c++ perf python3 git
```

## Makefile 目標

| 命令 | 說明 |
|------|------|
| `make all` | 編譯所有範例 |
| `make test` | 測試所有範例 |
| `make benchmark` | 執行性能基準測試 |
| `make flamegraph-cpu` | 生成 CPU 火焰圖 |
| `make analyze` | 分析火焰圖數據 |
| `make compare` | 比較優化前後性能 |
| `make clean` | 清理編譯產物 |
| `make distclean` | 完整清理（包括工具） |
| `make help` | 顯示幫助訊息 |

## 注意事項

1. 生成火焰圖可能需要 sudo 權限（用於 perf record）
2. 確保系統已安裝 perf 工具
3. 某些範例故意包含低效代碼用於教學目的
4. 實際性能結果會因硬體而異

## 進階使用

### 自定義編譯選項

修改 Makefile 中的 CXXFLAGS：
```makefile
CXXFLAGS = -g -O2 -fno-omit-frame-pointer -Wall -Wextra
```

### 調整採樣頻率

修改 compare_performance.sh 中的採樣頻率：
```bash
perf record -F 999 ...  # 提高到 999 Hz
```

## 故障排除

### perf 權限問題

如果遇到權限錯誤：
```bash
echo 0 | sudo tee /proc/sys/kernel/perf_event_paranoid
```

### 找不到符號

確保編譯時包含調試符號：
```bash
g++ -g -fno-omit-frame-pointer ...
```

### 火焰圖太平

可能是內聯優化導致，使用：
```bash
g++ -fno-inline ...
```