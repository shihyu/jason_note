# Google Benchmark 測試專案

這是一個完整的 Google Benchmark 測試專案，包含基本 C++ 測試和 C 語言函式測試。

## 專案結構

```
benchmark_project/
├── src/                    # C 原始碼
│   ├── algorithms.c        # 演算法實作
│   └── algorithms.h        # 演算法標頭檔
├── benchmark/              # 基準測試程式
│   ├── test_basic_benchmark.cpp   # 基本 C++ 測試
│   └── test_c_benchmark.cpp       # C 語言測試
├── build/                  # 建構輸出目錄
│   └── reports/           # 測試報告
├── Makefile               # 專案建構檔案
└── README.md              # 本檔案
```

## 前置需求

1. **編譯器**
   - GCC 或 Clang（支援 C11 和 C++17）

2. **Google Benchmark**
   - 需要先安裝 Google Benchmark 函式庫

## 安裝 Google Benchmark

```bash
# 克隆專案
git clone https://github.com/google/benchmark.git
cd benchmark

# 建立並編譯
cmake -E make_directory build
cmake -E chdir build cmake -DBENCHMARK_DOWNLOAD_DEPENDENCIES=on -DCMAKE_BUILD_TYPE=Release ../
cmake --build build --config Release

# 安裝到系統
sudo cmake --build build --config Release --target install
```

## 快速開始

```bash
# 檢查相依套件
make check-deps

# 編譯所有程式
make

# 執行所有基準測試
make benchmark

# 執行快速測試
make quick-test
```

## Makefile 目標

### 基本操作
- `make` - 編譯所有程式
- `make clean` - 清理建構檔案
- `make help` - 顯示說明

### 測試執行
- `make benchmark` - 執行所有基準測試
- `make test-basic` - 只執行基本 C++ 測試
- `make test-c` - 只執行 C 語言測試
- `make quick-test` - 執行快速測試（部分測試）
- `make list-tests` - 列出所有可用的測試

### 進階功能
- `make profile` - 執行詳細效能分析（10次重複）
- `make benchmark-json` - 產生 JSON 格式報告
- `make benchmark-csv` - 產生 CSV 格式報告
- `make memcheck` - 檢查記憶體洩漏（需要 valgrind）

### 開發相關
- `make debug` - 編譯偵錯版本
- `make check-deps` - 檢查相依套件

## 測試內容

### 基本 C++ 測試 (test_basic_benchmark)
- 字串建立效能
- 向量排序（不同大小）
- 編譯器優化防護測試
- Fixture 測試夾具
- 多執行緒測試
- 自訂計數器和吞吐量
- 統計分析
- 模板測試

### C 語言測試 (test_c_benchmark)
- **排序演算法**
  - Bubble Sort
  - Quick Sort
  - Merge Sort
- **搜尋演算法**
  - Linear Search
  - Binary Search
- **數學函式**
  - Fibonacci
  - Factorial
  - GCD (最大公因數)
- **比較測試**
  - C vs C++ STL 排序比較

## 使用範例

### 1. 執行特定測試
```bash
# 只執行字串相關測試
./build/test_basic_benchmark --benchmark_filter="BM_String.*"

# 只執行排序測試
./build/test_c_benchmark --benchmark_filter=".*Sort.*"
```

### 2. 產生報告
```bash
# 產生 JSON 報告
make benchmark-json

# 產生 CSV 報告
make benchmark-csv

# 報告會儲存在 build/reports/ 目錄
```

### 3. 效能分析
```bash
# 執行詳細分析（10次重複）
make profile

# 設定最小執行時間
./build/test_basic_benchmark --benchmark_min_time=2.0s
```

### 4. 記憶體檢查
```bash
# 需要先安裝 valgrind
sudo apt-get install valgrind  # Ubuntu/Debian
# 或
sudo yum install valgrind      # CentOS/RHEL

# 執行記憶體檢查
make memcheck
```

## 輸出範例

```
----------------------------------------------------------------
Benchmark                      Time             CPU   Iterations
----------------------------------------------------------------
BM_StringCreation           9.18 ns         9.17 ns     76143424
BM_VectorSort/100            815 ns          815 ns       854951
BM_Fibonacci/20             4.88 ns         4.88 ns     28542356
BM_LinearSearch_BigO       14.49 N         14.49 N
```

## 疑難排解

### 1. 找不到 benchmark 函式庫
```bash
# 確認安裝路徑
ldconfig -p | grep benchmark

# 設定 LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
```

### 2. 編譯錯誤
```bash
# 檢查編譯器版本
g++ --version

# 確認支援 C++17
g++ -std=c++17 -E -x c++ - < /dev/null
```

### 3. 執行時錯誤
```bash
# 使用偵錯版本
make debug

# 使用 gdb 偵錯
gdb ./build/test_basic_benchmark
```

## 效能優化建議

1. **系統設定**
   ```bash
   # 設定 CPU 效能模式
   sudo cpupower frequency-set -g performance

   # 關閉 Turbo Boost
   echo 1 | sudo tee /sys/devices/system/cpu/intel_pstate/no_turbo
   ```

2. **執行建議**
   - 關閉其他應用程式
   - 使用 `taskset` 綁定 CPU 核心
   - 增加 `--benchmark_repetitions` 取得穩定結果

## 授權

本專案使用 MIT 授權。

## 參考資源

- [Google Benchmark GitHub](https://github.com/google/benchmark)
- [Google Benchmark 使用者指南](https://github.com/google/benchmark/blob/main/docs/user_guide.md)
- [完整文檔](../google_benchmark_guide.md)