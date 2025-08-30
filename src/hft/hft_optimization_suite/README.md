# HFT Optimization Suite

高頻交易系統性能優化工具套件，包含大頁面(HugePages)、事件驅動IO、CPU親和性等關鍵技術的實作與測試。

## 目錄結構

```
hft_optimization_suite/
├── hugepages_test.cpp        # 大頁面性能測試
├── event_driven_server.cpp   # 事件驅動IO伺服器
├── cpu_affinity_test.cpp     # CPU親和性測試
├── hft_integrated_system.cpp # 整合HFT系統
├── Makefile                   # 編譯腳本
└── README.md                  # 本文件
```

## 快速開始

### 1. 編譯所有程式

```bash
make all
```

### 2. 執行測試套件

```bash
make test
```

### 3. 執行性能基準測試

```bash
make benchmark
```

## 詳細使用說明

### 編譯選項

```bash
make all          # 編譯所有程式
make debug        # 編譯除錯版本
make profile      # 編譯性能分析版本
make clean        # 清理編譯檔案
```

### 個別測試

```bash
make test-hugepages  # 測試大頁面性能
make test-cpu        # 測試CPU親和性
make test-io         # 測試事件驅動IO
make test-hft        # 測試整合HFT系統
```

### 系統設置

```bash
make setup-hugepages  # 配置系統大頁面(需要sudo)
make setup-thp        # 配置透明大頁面(需要sudo)
make system-info      # 顯示系統資訊
```

### 執行程式

```bash
make run-server  # 執行事件驅動伺服器
make run-client  # 執行負載測試客戶端
make run-hft     # 執行HFT系統
```

## 程式說明

### 1. hugepages_test.cpp
- 測試標準頁面 vs 大頁面性能差異
- 支援2MB和1GB大頁面
- 包含隨機訪問和順序訪問測試
- 矩陣運算基準測試

### 2. event_driven_server.cpp
- 實作epoll事件驅動模型
- 支援10,000+並發連接
- 包含無鎖環形緩衝區
- 對比執行緒池模型

### 3. cpu_affinity_test.cpp
- CPU親和性綁定測試
- NUMA架構支援
- False sharing測試
- 執行緒優先級測試

### 4. hft_integrated_system.cpp
- 整合所有優化技術
- 無鎖SPSC隊列
- 多執行緒架構
- 模擬完整交易系統

## 性能優化要點

### 大頁面優化
- 減少TLB miss
- 提升記憶體訪問速度
- 降低頁表遍歷開銷

### 事件驅動IO
- 單執行緒處理大量連接
- 避免執行緒上下文切換
- 非阻塞IO操作

### CPU親和性
- 減少CPU快取失效
- 避免跨核心遷移
- 優化NUMA訪問

## 系統需求

- Linux kernel 3.10+
- g++ 7.0+ (C++17支援)
- 2GB+ RAM
- x86_64架構CPU

## 可選依賴

- perf (性能分析)
- libnuma-dev (NUMA支援)
- vmstat (系統監控)

## 測試結果範例

```
=== CPU Affinity Test ===
Available CPUs: 16
No CPU affinity: 88 ms
Each thread pinned to different CPU: 85 ms
All threads pinned to same CPU: 328 ms

=== HugePages Performance Test ===
Standard Pages (4KB):
  Random access: 13.91 ns/access
  Sequential access: 2.61 ns/access
  
HugePages (2MB):
  Random access: 8.45 ns/access
  Sequential access: 2.12 ns/access
  
Performance improvement: 1.65x
```

## 注意事項

1. 部分功能需要root權限(如設置大頁面)
2. 大頁面需要系統預先配置
3. 實時優先級需要適當的系統權限
4. 建議在生產環境前充分測試

## 授權

MIT License