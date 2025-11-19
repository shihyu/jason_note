# HFT 延遲測試套件 - 完整使用手冊

## 📋 目錄

1. [快速開始](#快速開始)
2. [Makefile 完整命令](#makefile-完整命令)
3. [測試程式詳細說明](#測試程式詳細說明)
4. [實際使用案例](#實際使用案例)
5. [性能優化建議](#性能優化建議)
6. [常見問題解答](#常見問題解答)

---

## 快速開始

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install build-essential g++ make
sudo apt-get install linux-tools-generic  # for perf
sudo apt-get install python3 python3-pip  # for validation scripts

# CentOS/RHEL
sudo yum groupinstall "Development Tools"
sudo yum install gcc-c++ make
sudo yum install perf python3
```

### 基本使用流程

```bash
# 1. 查看幫助
make help

# 2. 編譯所有程式
make all

# 3. 運行快速測試
make quick-test

# 4. 運行完整測試
make test-all

# 5. 查看演示
make demo
```

---

## Makefile 完整命令

### 編譯命令

| 命令 | 說明 | 使用場景 |
|------|------|----------|
| `make all` | 編譯所有測試程式（優化模式） | 正常使用 |
| `make benchmarks` | 只編譯基準測試程式 | 只需要基礎測試 |
| `make network` | 只編譯網路測試程式 | 只需要網路測試 |
| `make memory` | 只編譯記憶體測試程式 | 只需要記憶體測試 |
| `make debug` | Debug 模式編譯（含符號表） | 調試用 |
| `make profile` | 性能分析模式編譯 | 使用 gprof 分析 |
| `make clean` | 清理所有編譯產物 | 重新編譯前 |

### 測試命令

| 命令 | 說明 | 執行時間 |
|------|------|----------|
| `make test` | 運行所有本地測試 | ~30秒 |
| `make test-all` | 運行所有測試（含網路） | ~60秒 |
| `make test-basic` | 只運行基礎延遲測試 | ~10秒 |
| `make test-orderbook` | 只運行訂單簿測試 | ~10秒 |
| `make test-memory` | 只運行記憶體池測試 | ~10秒 |
| `make test-network` | 只運行網路測試 | ~20秒 |
| `make quick-test` | 快速測試（精簡版） | ~5秒 |
| `make demo` | 功能演示 | ~5秒 |

### 分析命令

| 命令 | 說明 | 需求 |
|------|------|------|
| `make perf-basic` | 分析基礎延遲效能 | 需要 perf |
| `make perf-orderbook` | 分析訂單簿效能 | 需要 perf |
| `make perf-memory` | 分析記憶體池效能 | 需要 perf |
| `make run-benchmarks` | 運行完整基準測試 | 無 |

### 驗證命令

| 命令 | 說明 | 用途 |
|------|------|------|
| `make verify` | 驗證所有編譯選項 | 確認環境正常 |
| `make install-deps` | 檢查依賴項 | 初次使用 |
| `make help` | 顯示詳細幫助 | 查看用法 |

---

## 測試程式詳細說明

### 1. basic_latency - 基礎延遲測試

測試基本操作的延遲，用於建立基準線。

```bash
# 運行所有基礎測試
./bin/basic_latency

# 只測試特定項目
./bin/basic_latency map       # map vs unordered_map
./bin/basic_latency copy      # memcpy vs move
./bin/basic_latency alloc     # 記憶體分配策略
./bin/basic_latency timer     # 計時器開銷
```

**測試項目說明：**

- **map**: 比較 `std::map` 和 `std::unordered_map` 的插入性能
  - 預期結果：unordered_map 應該更快（平均 O(1) vs O(log n)）
  
- **copy**: 比較 `memcpy` 和 `std::move` 的性能
  - 預期結果：move 對大物件應該更快
  
- **alloc**: 比較不同記憶體分配策略
  - new/delete vs unique_ptr vs malloc/free
  
- **timer**: 測量不同計時方法的開銷
  - chrono vs rdtsc vs rdtscp

### 2. orderbook_latency - 訂單簿測試

模擬真實交易系統的訂單簿操作。

```bash
# 運行所有訂單簿測試
./bin/orderbook_latency

# 只測試特定場景
./bin/orderbook_latency ops     # 基本操作（增刪改查）
./bin/orderbook_latency match   # 撮合模擬
./bin/orderbook_latency stress  # 壓力測試（大量訂單）
```

**測試場景說明：**

- **ops**: 測試訂單的增加、取消、修改和 BBO 查詢
  - 模擬比例：40% 添加、30% 取消、15% 修改、15% BBO
  
- **match**: 模擬激進訂單穿過價差的撮合
  - 測試跨價差訂單的處理速度
  
- **stress**: 深度訂單簿壓力測試
  - 創建 20,000 個訂單（100 個價位 × 100 個訂單 × 2 邊）

### 3. memory_pool - 記憶體池測試

測試不同記憶體管理策略的效能。

```bash
# 運行所有記憶體測試
./bin/memory_pool

# 只測試特定策略
./bin/memory_pool strategies  # 分配策略比較
./bin/memory_pool patterns    # 分配模式測試
./bin/memory_pool cache       # 緩存效應測試
```

**測試內容說明：**

- **strategies**: 比較三種分配策略
  - 標準堆分配（new/delete）
  - 記憶體池（預分配）
  - 環形緩衝區（零拷貝）
  
- **patterns**: 測試不同分配模式
  - 順序分配/釋放
  - 隨機分配/釋放
  - 突發分配/釋放
  
- **cache**: 測試不同步長的緩存效應
  - 步長：1, 8, 64, 512, 4096 bytes

### 4. 網路延遲測試

測試網路通信的往返時間（RTT）。

```bash
# 啟動服務器（終端1）
./bin/udp_server [port]         # 預設 9000

# 運行客戶端測試（終端2）
./bin/udp_client [ip] [port]    # 預設 localhost 9000
```

**測試模式：**

- Quote 請求測試：模擬行情請求
- Order 提交測試：模擬訂單提交
- 突發測試：測試批量消息處理
- 持續吞吐測試：固定速率下的延遲

---

## 實際使用案例

### 案例1：完整性能基準測試

```bash
# 清理環境
make clean

# 編譯優化版本
make all

# 運行完整測試並保存結果
make run-benchmarks > benchmark_results.txt

# 生成性能報告
python3 validate_results.py
```

### 案例2：調試特定問題

```bash
# 編譯 Debug 版本
make debug

# 使用 GDB 調試
gdb ./bin/orderbook_latency
(gdb) break orderbook_latency.cpp:145
(gdb) run ops
(gdb) print orderbook.size()
```

### 案例3：性能分析

```bash
# 編譯 Profile 版本
make profile

# 運行程式生成分析數據
./bin/basic_latency

# 查看分析報告
gprof ./bin/basic_latency gmon.out > analysis.txt
```

### 案例4：網路延遲測試

```bash
# 終端1 - 啟動服務器
./bin/udp_server 9000

# 終端2 - 本地測試
./bin/udp_client localhost 9000

# 終端2 - 遠程測試
./bin/udp_client 192.168.1.100 9000
```

### 案例5：持續集成測試

```bash
#!/bin/bash
# CI 腳本範例

# 驗證編譯
if ! make verify; then
    echo "Compilation verification failed"
    exit 1
fi

# 運行快速測試
if ! make quick-test; then
    echo "Quick tests failed"
    exit 1
fi

# 驗證結果
python3 validate_results.py
if [ $? -ne 0 ]; then
    echo "Performance regression detected"
    exit 1
fi

echo "All tests passed"
```

---

## 性能優化建議

### 系統層級優化

```bash
# 1. 設置 CPU 為性能模式
sudo cpupower frequency-set -g performance

# 2. 關閉 CPU 節能
for i in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance | sudo tee $i
done

# 3. 增加網路緩衝區
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# 4. 啟用大頁面
sudo sysctl -w vm.nr_hugepages=128

# 5. 關閉 NUMA 自動平衡
echo 0 | sudo tee /proc/sys/kernel/numa_balancing

# 6. 設置 CPU 親和性
taskset -c 0,1 ./bin/orderbook_latency
```

### 編譯優化選項

```makefile
# 自定義編譯選項
CXXFLAGS = -O3 -march=native -mtune=native -flto
CXXFLAGS += -fno-exceptions -fno-rtti  # 如果不需要異常和RTTI
CXXFLAGS += -falign-functions=32       # 函數對齊
CXXFLAGS += -falign-loops=32          # 循環對齊
```

### 代碼優化建議

1. **使用適當的容器**
   - 頻繁查找：`std::unordered_map`
   - 有序遍歷：`std::map`
   - 固定大小：`std::array`

2. **避免動態分配**
   - 使用記憶體池
   - 預分配容器容量
   - 使用棧上物件

3. **優化熱路徑**
   - 使用 `likely/unlikely` 提示
   - 內聯關鍵函數
   - 避免虛函數調用

---

## 常見問題解答

### Q1: 編譯失敗怎麼辦？

```bash
# 檢查依賴
make install-deps

# 驗證編譯器版本
g++ --version  # 需要支援 C++17

# 清理重試
make clean
make all
```

### Q2: 測試結果不穩定？

```bash
# 1. 關閉其他程式減少幹擾
# 2. 使用 CPU 親和性
taskset -c 0 ./bin/basic_latency

# 3. 增加測試樣本數
# 修改源碼中的 NUM_OPERATIONS
```

### Q3: 如何解讀測試結果？

關鍵指標說明：
- **Mean**: 平均延遲，反映整體性能
- **P50 (Median)**: 中位數，比平均值更穩定
- **P99**: 99%分位數，反映尾部延遲
- **Jitter**: 抖動，反映延遲穩定性
- **StdDev**: 標準差，反映分散程度

### Q4: 如何比較不同系統的結果？

```bash
# 1. 在系統A運行
make run-benchmarks > system_a.txt

# 2. 在系統B運行  
make run-benchmarks > system_b.txt

# 3. 比較結果
diff system_a.txt system_b.txt
```

### Q5: 網路測試失敗？

```bash
# 檢查端口
netstat -tuln | grep 9000

# 檢查防火牆
sudo iptables -L | grep 9000

# 使用不同端口
./bin/udp_server 9999
./bin/udp_client localhost 9999
```

---

## 進階使用

### 自定義測試參數

編輯源碼中的常量：

```cpp
// benchmarks/basic_latency.cpp
const int NUM_OPERATIONS = 100000;  // 增加樣本數

// network/udp_client.cpp  
const int NUM_TESTS = 10000;        // 增加測試次數
const int BURST_SIZE = 100;         // 調整突發大小
```

### 添加新測試

1. 創建新的測試文件
2. 更新 Makefile 添加編譯目標
3. 更新 test_all.sh 添加測試調用

### 導出測試數據

```bash
# CSV 格式導出
./bin/basic_latency | grep -E "Mean|P99" | awk '{print $2}' > results.csv

# JSON 格式（使用 Python 腳本）
python3 validate_results.py  # 生成 latency_report.json
```

---

## 總結

本測試套件提供了完整的 HFT 系統延遲測試方案，涵蓋：

- ✅ 基礎語法和資料結構效能
- ✅ 訂單簿操作延遲
- ✅ 記憶體管理策略
- ✅ 網路通信延遲

使用本套件可以：
1. 建立性能基準線
2. 比較不同實現方案
3. 識別性能瓶頸
4. 驗證優化效果

記住：**在 HFT 中，每納秒都很重要！**