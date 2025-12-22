# 效能量測指南 (Performance Measurement Guide)

本文件旨在介紹效能量測的核心知識、方法論及常用工具，協助開發者準確分析系統與應用程式的效能表現。

## 1. 緒論 (Introduction)

在軟體工程中，效能不僅是「跑得快」，更包含了系統的穩定性、擴展性與資源效率。準確的量測是優化的前提。沒有數據支撐的優化往往是徒勞甚至有害的（即「過早優化」）。

## 2. 關鍵指標 (Key Metrics)

了解指標是分析的第一步。

### 延遲 (Latency)
描述完成單一操作所需的時間。
- **P50 (中位數)**: 50% 的請求快於此時間。反映一般使用者的體驗。
- **P95 / P99**: 95% 或 99% 的請求快於此時間。反映「長尾效應」或極端情況下的體驗，對於 SLA (服務層級協議) 至關重要。
- **平均值 (Mean)**: 容易受極端值影響，通常不如百分位數 (Percentile) 具參考價值。

### 吞吐量 (Throughput)
系統在單位時間內能處理的工作量。
- **RPS (Requests Per Second)**: 每秒請求數，常用於 Web Server。
- **TPS (Transactions Per Second)**: 每秒交易數，常用於資料庫。
- **Bandwidth**: 網路或磁碟的傳輸速率 (如 MB/s)。

### 資源利用率 (Resource Usage)
- **CPU**: 使用率 (User/System)、Load Average。
- **Memory**: 使用量、Swap 使用情況、Page Faults。
- **Disk I/O**: IOPS、讀寫延遲。
- **Network**: 封包遺失率、重傳率。

### 飽和度與錯誤 (Saturation & Errors)
- **飽和度**: 資源排隊的情況（如 CPU Run Queue 長度）。
- **錯誤**: HTTP 5xx 比例、連線失敗數。
- **USE 方法論 (Utilization, Saturation, Errors)**: 由 Brendan Gregg 提出，是分析系統效能問題的有效框架。

## 3. 量測方法論 (Measurement Methodologies)

### 基準測試 (Benchmarking)
- **微觀 (Micro-benchmarking)**: 針對單一函數或小段程式碼進行測試（如 Google Benchmark）。
- **宏觀 (Macro-benchmarking)**: 針對整體系統或應用程式進行壓力測試。

### 效能分析 (Profiling)
透過採樣或插樁 (Instrumentation) 來分析程式執行期間的行為。
- **CPU Profiling**: 找出最耗時的函數。
- **Memory Profiling**: 分析記憶體分配與洩漏 (Leak)。
- **Mutex Contention**: 分析鎖競爭導致的等待時間。

### 追蹤 (Tracing)
- **系統調用 (Syscalls)**: 使用 `strace` 查看程式與核心的互動。
- **分佈式追蹤 (Distributed Tracing)**: 在微服務架構中，追蹤請求跨服務的流向 (如 Jaeger, Zipkin)。

## 4. 常用工具 (Tools - Linux Focus)

### 系統級別
- **top / htop**: 即時查看系統整體資源與 Process 狀態。
- **vmstat**: 檢視虛擬記憶體、Process、CPU 活動。
- **iostat**: 檢視磁碟 I/O 狀況。
- **strace**: 追蹤 Process 的系統呼叫 (System Calls)。
- **perf**: Linux 強大的效能分析工具，可看 CPU Cache miss, Context switch 等硬體計數器。

### 應用層級
- **gprof**: GNU Profiler，傳統的 C/C++ 分析工具。
- **pprof**: Google 開發的分析工具，支援 C++, Go 等。
    - *範例*: 請參考本專案 `data/cpp-pprof-demo` 目錄下的範例。
    - *進階*: 支援 Flame Graph (火焰圖) 視覺化。
- **fgprof**: 針對 Go 的 Sampling Profiler，可同時分析 On-CPU 和 Off-CPU 時間。
    - *範例*: 請參考本專案 `data/cpp-fgprof-demo` 目錄下的範例。

### 壓力測試
- **wrk**: 現代化 HTTP 壓力測試工具，支援 Lua 腳本。
- **ab (Apache Bench)**: 簡單易用的 HTTP 測試工具。
- **locust**: 使用 Python 撰寫測試腳本，易於模擬複雜的使用者行為。

## 5. 常見陷阱 (Common Pitfalls)

- **觀測者效應 (Observer Effect)**: 量測工具本身佔用資源，導致量測結果失真（如開啟詳細 Log 或頻繁採樣）。
- **冷啟動 vs 預熱 (Cold Start vs. Warmup)**: 許多系統（如 JVM, Cache）需要時間預熱才能達到最佳效能。測試前應確保系統已進入穩定狀態。
- **協同省略 (Coordinated Omission)**: 壓力測試工具在發送請求時，若因系統回應慢而暫停發送，會導致測試結果中的延遲被低估。應使用能修正此問題的工具（如 wrk2）。
