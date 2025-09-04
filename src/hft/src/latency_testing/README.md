# HFT Latency Testing Suite

高頻交易延遲測試套件，用於測量和驗證交易系統的各個組件延遲。

## 目錄結構

```
latency_testing/
├── benchmarks/          # 基準測試
│   ├── basic_latency.cpp      # 基礎語法和資料結構測試
│   └── orderbook_latency.cpp  # 訂單簿操作測試
├── network/            # 網路測試
│   ├── udp_server.cpp        # UDP 服務器（模擬交易所）
│   └── udp_client.cpp        # UDP 客戶端（模擬策略）
├── memory/             # 記憶體測試
│   └── memory_pool.cpp       # 記憶體池和分配策略測試
├── utils/              # 工具類
│   └── timer.hpp            # 計時器和統計工具
├── Makefile           # 構建配置
├── run_tests.sh       # 測試運行腳本
└── validate_results.py # 結果驗證腳本
```

## 快速開始

### 編譯所有測試

```bash
make all
```

### 運行所有測試

```bash
# 運行本地測試
make test

# 包含網路測試
make test-all

# 或使用測試腳本
./run_tests.sh
./run_tests.sh --with-network  # 包含網路測試
```

### 運行特定測試

```bash
# 基礎延遲測試
./bin/basic_latency map      # map vs unordered_map
./bin/basic_latency copy     # memcpy vs move
./bin/basic_latency alloc    # 動態分配比較
./bin/basic_latency timer    # 計時器開銷

# 訂單簿測試
./bin/orderbook_latency ops    # 訂單操作
./bin/orderbook_latency match  # 撮合模擬
./bin/orderbook_latency stress # 壓力測試

# 記憶體池測試
./bin/memory_pool strategies  # 分配策略比較
./bin/memory_pool patterns    # 分配模式測試
./bin/memory_pool cache       # 緩存效應測試

# 網路測試
./bin/udp_server [port]              # 啟動服務器
./bin/udp_client [server_ip] [port]  # 運行客戶端測試
```

## 測試項目說明

### 1. 基礎延遲測試 (basic_latency)

- **Map vs Unordered Map**: 比較有序和無序容器的插入延遲
- **Memcpy vs Move**: 比較記憶體拷貝和移動語義的效能
- **動態分配**: 比較 new/delete、unique_ptr、malloc/free
- **計時器開銷**: 比較 chrono、rdtsc、rdtscp 的開銷

### 2. 訂單簿測試 (orderbook_latency)

- **訂單操作**: 測試添加、取消、修改訂單的延遲
- **BBO 查詢**: 測試獲取最佳買賣價的延遲
- **撮合模擬**: 模擬激進訂單的處理延遲
- **壓力測試**: 測試深度訂單簿的效能

### 3. 記憶體池測試 (memory_pool)

- **分配策略**: 比較堆分配、記憶體池、環形緩衝區
- **分配模式**: 測試順序、隨機、突發分配模式
- **緩存效應**: 測試不同步長的記憶體訪問延遲

### 4. 網路測試 (network)

- **Quote 請求延遲**: 測試行情請求的往返時間
- **訂單提交延遲**: 測試訂單提交和確認的延遲
- **突發處理**: 測試批量消息的處理延遲
- **持續吞吐**: 測試在固定速率下的延遲分布

## 效能優化

### 系統配置

運行測試前的優化建議：

```bash
# 設置 CPU 為性能模式（需要 root）
sudo cpupower frequency-set -g performance

# 增加網路緩衝區
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# 啟用大頁面
sudo echo 128 > /proc/sys/vm/nr_hugepages

# 綁定到特定 CPU 核心
taskset -c 0 ./bin/basic_latency
```

### 編譯優化

```bash
# 優化編譯
make clean && make all

# Debug 模式
make debug

# 性能分析模式
make profile
```

## 結果分析

### 使用驗證腳本

```bash
python3 validate_results.py
```

驗證腳本會：
1. 檢查系統配置
2. 運行基準測試
3. 驗證結果是否符合預期閾值
4. 生成 JSON 格式的報告

### 使用 perf 分析

```bash
# 分析 CPU 事件
make perf-basic
make perf-orderbook
make perf-memory

# 詳細分析
perf record -g ./bin/basic_latency
perf report
```

## 延遲指標說明

### 關鍵指標

- **Mean (平均值)**: 所有樣本的平均延遲
- **Median (中位數)**: 50% 分位數，更能反映典型延遲
- **P95/P99**: 95% 和 99% 分位數，尾部延遲
- **P99.9**: 99.9% 分位數，極端情況延遲
- **Jitter (抖動)**: 延遲的變化程度
- **StdDev (標準差)**: 延遲分布的離散程度

### 預期延遲範圍

| 操作類型 | 平均延遲 | P99 延遲 |
|---------|---------|---------|
| Map 插入 | < 1 μs | < 5 μs |
| Unordered Map 插入 | < 500 ns | < 2 μs |
| 記憶體池分配 | < 50 ns | < 200 ns |
| 訂單簿添加 | < 500 ns | < 2 μs |
| 本地 UDP RTT | < 50 μs | < 100 μs |

## 注意事項

1. **測試環境**: 確保在低負載環境下運行測試
2. **預熱**: 測試包含預熱階段以穩定緩存
3. **統計意義**: 每個測試收集足夠樣本（通常 > 10,000）
4. **系統干擾**: 關閉不必要的服務和進程
5. **NUMA 親和性**: 在多 NUMA 系統上注意綁定

## 故障排除

### 編譯錯誤

```bash
# 確保安裝必要的開發工具
sudo apt-get install build-essential
```

### 權限問題

```bash
# 大頁面需要 root 權限
sudo ./run_tests.sh

# 或調整用戶權限
sudo sysctl -w vm.nr_hugepages=128
sudo chmod 755 /dev/hugepages
```

### 網路測試失敗

```bash
# 檢查端口是否被占用
netstat -tuln | grep 9000

# 檢查防火牆
sudo ufw status
```

## 擴展測試

可以通過修改代碼添加更多測試：

1. 在相應目錄創建新的測試文件
2. 更新 Makefile 添加新的構建目標
3. 在 run_tests.sh 中添加新的測試調用
4. 在 validate_results.py 中添加新的閾值