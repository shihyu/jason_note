# Chapter 11: 系統效能優化與量測詳解

## 章節概述

本章進入系統開發的關鍵階段：**效能儀表化（Instrumentation）與優化準備**。在低延遲系統中，「無法量測，就無法優化」。本章實作了一套極低開銷的量測工具，用於精確追蹤系統中每個組件的處理延遲。

### 技術目標

1.  **高精度計時**：利用 CPU 的 TSC（Time Stamp Counter）暫存器進行納秒級計時。
2.  **儀表化程式碼**：在交易引擎的核心路徑嵌入量測宏（Macros）。
3.  **效能瓶頸識別**：量測 `PositionKeeper`、`FeatureEngine` 及策略邏輯的執行時間。
4.  **系統級優化**：探討 CPU 親和性（Affinity）與快取對齊對延遲的影響。

---

## 1. 核心計時技術：RDTSC

### 1.1 為什麼不使用 std::chrono？

雖然 `std::chrono::system_clock` 提供納秒精度，但其底層通常涉及核心呼叫（vDSO 優化後的 `clock_gettime`），且經過多層封裝，開銷約為 **30-50 納秒**。

在低延遲交易中，某些邏輯（如雜湊表查找）僅需 **10 納秒**，使用 `std::chrono` 量測會產生嚴重的「觀察者效應」（量測工具本身拖慢了系統）。

### 1.2 RDTSC 指令原理

`RDTSC` (Read Time-Stamp Counter) 是一條彙編指令，直接讀取 CPU 自開機以來的時鐘週期數。

`perf_utils.h:7-12`

```cpp
inline auto rdtsc() noexcept {
    unsigned int lo, hi;
    // ⚡ 直接執行彙編指令，開銷僅約 10-15 週期
    __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
    return ((uint64_t) hi << 32) | lo;
}
```

*   **開銷**：極低（約 10 納秒）。
*   **精度**：週期級（在 3GHz CPU 上約 0.33 納秒）。
*   **注意**：RDTSC 量測的是「週期數」而非「時間」，且需考慮 CPU 調頻與跨核心同步問題（現代 CPU 通常支援 Invariant TSC，解決了這些問題）。

---

## 2. 效能量測宏（Performance Macros）

為了方便在程式碼中快速嵌入量測點，本章定義了三組宏：

### 2.1 START_MEASURE & END_MEASURE (週期量測)

用於量測一段程式碼區塊消耗的 **CPU 週期數**。

```cpp
#define START_MEASURE(TAG) const auto TAG = Common::rdtsc()

#define END_MEASURE(TAG, LOGGER)                                                              
      do {                                                                                    
        const auto end = Common::rdtsc();                                                     
        LOGGER.log("% RDTSC "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), (end - TAG)); 
      } while(false)
```

**使用範例：**
```cpp
START_MEASURE(RiskCheck);
risk_manager_.checkRisk(order);
END_MEASURE(RiskCheck, logger_); 
// 輸出：RiskCheck 120 (代表消耗 120 個週期)
```

### 2.2 TTT_MEASURE (時間點記錄)

TTT 代表 **Tick-to-Trade** 或時間戳追蹤。它記錄絕對納秒時間戳，用於跨組件（甚至跨機器）追蹤封包流轉。

```cpp
#define TTT_MEASURE(TAG, LOGGER)                                                              
      do {                                                                                    
        const auto TAG = Common::getCurrentNanos();                                           
        LOGGER.log("% TTT "#TAG" %\n", Common::getCurrentTimeStr(&time_str_), TAG);           
      } while(false)
```

---

## 3. 交易引擎儀表化（Instrumentation）

本章在 `TradeEngine` 的熱路徑（Hot Path）中嵌入了量測點，追蹤以下組件：

### 3.1 倉位管理器（PositionKeeper）
追蹤更新 BBO（最佳買賣價）與處理成交（Fill）的耗時。

```cpp
START_MEASURE(Trading_PositionKeeper_updateBBO);
position_keeper_.updateBBO(ticker_id, bbo);
END_MEASURE(Trading_PositionKeeper_updateBBO, logger_);
```

### 3.2 特徵引擎（FeatureEngine）
特徵計算通常涉及浮點運算，是系統中較重的組件。

```cpp
START_MEASURE(Trading_FeatureEngine_onOrderBookUpdate);
feature_engine_.onOrderBookUpdate(ticker_id, price, side, book);
END_MEASURE(Trading_FeatureEngine_onOrderBookUpdate, logger_);
```

### 3.3 策略回調（Strategy Callbacks）
量測 MarketMaker 或 LiquidityTaker 決定是否發單的邏輯耗時。

---

## 4. 系統優化技術

除了量測，本章在 `thread_utils.h` 中強化了底層優化工具：

### 4.1 CPU 親和性（Affinity）

將執行緒固定在特定核心，避免作業系統進行 Context Switch（上下文切換），並保持 L1/L2 快取的「熱度」。

```cpp
inline auto setThreadCore(int core_id) noexcept {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(core_id, &cpuset);
    // ⚡ 綁定執行緒，減少快取失效延遲 (Cache Miss Penalty)
    return (pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset) == 0);
}
```

### 4.2 執行緒啟動延遲優化

在 `createAndStartThread` 中加入 `sleep_for(1s)`，確保執行緒在開始處理業務邏輯前，已正確完成核心綁定與核心初始化。

---

## 5. 數據分析與瓶頸診斷

透過日誌輸出的 RDTSC 數據，我們可以進行以下分析：

1.  **平均延遲（Average Latency）**：組件的典型執行時間。
2.  **長尾延遲（Tail Latency / P99）**：最慢的 1% 情況。通常由快取失效（Cache Miss）或分支出錯（Branch Misprediction）引起。
3.  **抖動（Jitter）分析**：量測數據的波動程度。低延遲系統追求的是「穩定」而非僅僅是「快」。

### 典型延遲數據參考（CPU Cycles）

| 組件操作 | 預期週期數 | 說明 |
| :--- | :--- | :--- |
| 簡單風控檢查 | 50 - 150 | 基本比較與邏輯 |
| 倉位更新 | 100 - 300 | 涉及浮點運算與陣列讀寫 |
| 特徵計算 (WAP) | 200 - 500 | 涉及除法（較慢的 CPU 指令） |
| 策略邏輯 | 500 - 2000 | 視策略複雜度而定 |

---

## 6. 常見問題與陷阱

### 6.1 亂序執行（Out-of-Order Execution）
CPU 可能為了優化效能而重新排列指令順序。如果我們直接量測一段極短的程式碼，`RDTSC` 可能在目標指令執行完畢前就讀取。
*   **解決方案**：在極精密量測中使用 `RDTSCP` 或 `CPUID` 作為指令屏障（Barrier），但在一般的組件級量測中，本章的 `__asm__ __volatile__` 已足夠。

### 2.2 量測成本
雖然 `RDTSC` 很輕量，但 `logger_.log()` 本身是有開銷的。
*   **優化方式**：本專案的 `Logger` 是非同步的，它將數據寫入無鎖佇列。儘管如此，頻繁的量測日誌仍會佔用佇列帶寬。在生產環境中，通常會使用「統計量集（Stats Aggregator）」在記憶體中累加數據，每隔一段時間才輸出一次平均值，而非逐筆輸出。

---

## 技術名詞中英對照

| 中文 | 英文 | 說明 |
| :--- | :--- | :--- |
| 儀表化 | Instrumentation | 在程式中加入監控點的行為 |
| 時鐘週期 | Clock Cycle | CPU 執行的最小時間單位 |
| 親和性 | Affinity | 將執行緒綁定到特定硬體核心 |
| 抖動 | Jitter | 延遲的不穩定性 |
| 屏障 | Barrier | 防止指令重排序的機制 |

## 7. 實際應用範例：撮合引擎效能追蹤

### 7.1 撮合引擎中的量測點

在 `matching_engine.cpp` 中，我們在關鍵路徑上嵌入量測：

```cpp
// 量測訂單處理總延遲
TTT_MEASURE(T0_ClientRequest_In, logger_);
START_MEASURE(Exchange_Matching_processClientRequest);

// 處理新增訂單請求
auto client_response = order_book_->add(client_request);

END_MEASURE(Exchange_Matching_processClientRequest, logger_);
TTT_MEASURE(T1_ClientResponse_Out, logger_);
```

**日誌輸出範例**：
```
2026-01-10 12:34:56.123456789 TTT T0_ClientRequest_In 1736481296123456789
2026-01-10 12:34:56.123458012 RDTSC Exchange_Matching_processClientRequest 3690
2026-01-10 12:34:56.123458200 TTT T1_ClientResponse_Out 1736481296123458200
```

**延遲分析**：
- 總延遲：T1 - T0 = 1411 奈秒
- 撮合邏輯：3690 週期 ÷ 3GHz = 1230 奈秒
- 其他開銷：181 奈秒（日誌、序列化等）

### 7.2 交易策略效能追蹤

在 `MarketMaker::onOrderBookUpdate()` 中：

```cpp
START_MEASURE(Strategy_MarketMaker_PriceUpdate);

// 動態定價邏輯
const auto fair_price = feature_engine_->getFairPrice(ticker_id);
const auto spread = ticker_cfg_[ticker_id].spread_;
const auto bid = fair_price - spread;
const auto ask = fair_price + spread;

// 風控檢查
if (risk_manager_->checkPreTradeRisk(...) == RiskCheckResult::ALLOWED) {
    // 發送報價
    order_manager_->sendNewOrder(ticker_id, Side::BUY, bid, qty);
    order_manager_->sendNewOrder(ticker_id, Side::SELL, ask, qty);
}

END_MEASURE(Strategy_MarketMaker_PriceUpdate, logger_);
```

**效能瓶頸識別**：
- 若量測值 > 5000 週期（~1.6μs），表示策略過於複雜
- 應檢查是否有除法運算、sqrt() 等昂貴操作
- 使用編譯器優化 `-ffast-math` 加速浮點運算

---

## 8. 數據分析最佳實踐

### 8.1 延遲分佈分析

收集到 RDTSC 數據後，應計算以下統計指標：

```python
import numpy as np

cycles = [120, 135, 118, 142, 128, ...]  # 從日誌提取的週期數

# 基本統計
mean = np.mean(cycles)
p50 = np.percentile(cycles, 50)
p90 = np.percentile(cycles, 90)
p99 = np.percentile(cycles, 99)
p999 = np.percentile(cycles, 99.9)

# 抖動分析
jitter = np.std(cycles)  # 標準差
cv = jitter / mean       # 變異係數（越小越穩定）

print(f"平均: {mean:.1f} cycles")
print(f"P50: {p50} | P90: {p90} | P99: {p99} | P99.9: {p999}")
print(f"抖動: {jitter:.1f} cycles (CV: {cv:.2%})")
```

**良好效能指標**：
- P99 < 2× P50（長尾不明顯）
- CV < 20%（抖動可控）
- P99.9 < 5× P50（無離群值）

### 8.2 熱圖分析（Heatmap）

將延遲數據可視化，識別異常模式：

```python
import matplotlib.pyplot as plt

# 時間序列熱圖
plt.scatter(timestamps, cycles, alpha=0.5, s=1)
plt.axhline(y=p99, color='r', linestyle='--', label='P99')
plt.xlabel('時間（秒）')
plt.ylabel('延遲（週期）')
plt.legend()
plt.show()
```

**異常模式識別**：
- 週期性尖峰：可能是 GC（Go/Java）或 Timer（C++）
- 突發長尾：可能是 NUMA 遠端記憶體存取
- 逐漸上升：可能是快取污染或記憶體碎片化

---

## 9. 優化策略與技巧

### 9.1 CPU 親和性優化實戰

```bash
# 使用 isolcpus 隔離核心（開機參數）
isolcpus=2,3,4,5

# 關閉超執行緒（Hyper-Threading）
echo off > /sys/devices/system/cpu/smt/control

# 固定 CPU 頻率（避免 Turbo Boost 波動）
cpupower frequency-set -g performance -d 3.5GHz -u 3.5GHz
```

**執行緒核心分配範例**：
```cpp
// Matching Engine: Core 2（隔離核心）
createAndStartThread(2, "MatchingEngine", [this]() { run(); });

// Market Data Publisher: Core 3（相鄰核心，共享 L3 Cache）
createAndStartThread(3, "MarketDataPublisher", [this]() { run(); });

// Trading Strategy: Core 4（獨立核心，避免快取競爭）
createAndStartThread(4, "TradingStrategy", [this]() { run(); });
```

### 9.2 觀察者效應最小化

**問題**：量測工具本身會拖慢系統（Heisenberg Uncertainty Principle in CS）

**解決方案**：

1. **條件編譯**：生產環境關閉量測
```cpp
#ifdef ENABLE_PROFILING
  START_MEASURE(MyFunction);
  // ... 業務邏輯 ...
  END_MEASURE(MyFunction, logger_);
#else
  // ... 業務邏輯 ...（無量測開銷）
#endif
```

2. **取樣量測**：不是每次都量測
```cpp
static uint64_t counter = 0;
if (++counter % 1000 == 0) {  // 每 1000 次量測一次
    START_MEASURE(SampledFunction);
    doWork();
    END_MEASURE(SampledFunction, logger_);
} else {
    doWork();
}
```

3. **統計聚合**：在記憶體中累加，定期輸出
```cpp
struct PerfStats {
    uint64_t count = 0;
    uint64_t sum = 0;
    uint64_t min = UINT64_MAX;
    uint64_t max = 0;

    void record(uint64_t cycles) {
        count++;
        sum += cycles;
        min = std::min(min, cycles);
        max = std::max(max, cycles);
    }

    void report(Logger& logger) {
        if (count > 0) {
            logger.log("Avg: % Min: % Max: % Count: %\n",
                       sum/count, min, max, count);
        }
    }
};

// 每秒輸出一次統計
if (getCurrentNanos() - last_report_time > 1'000'000'000) {
    stats.report(logger_);
    stats = PerfStats{};  // 重置
    last_report_time = getCurrentNanos();
}
```

---

## 10. 常見效能陷阱與偵錯

### 10.1 False Sharing（偽共享）

**問題**：不同執行緒訪問同一 Cache Line 的不同變數，導致 Cache 頻繁失效。

**範例**：
```cpp
// ❌ 錯誤：兩個變數在同一 Cache Line（64 bytes）
struct BadStruct {
    uint64_t thread1_counter;  // Cache Line 0
    uint64_t thread2_counter;  // Cache Line 0（偽共享！）
};

// ✅ 正確：使用 Cache Line 對齊
struct alignas(64) GoodStruct {
    uint64_t thread1_counter;  // Cache Line 0
    char padding[56];          // 填充到 64 bytes
    uint64_t thread2_counter;  // Cache Line 1（無偽共享）
};
```

**偵錯工具**：
```bash
# 使用 perf 檢測 Cache Miss
perf stat -e LLC-load-misses,LLC-store-misses ./trading_engine

# 使用 Valgrind Cachegrind 分析
valgrind --tool=cachegrind --cache-sim=yes ./matching_engine
```

### 10.2 NUMA 遠端記憶體存取

**問題**：在多 Socket 系統中，訪問其他 NUMA 節點的記憶體延遲是本地的 2-3 倍。

**偵錯**：
```bash
# 檢查 NUMA 拓撲
numactl --hardware

# 綁定記憶體到特定 NUMA 節點
numactl --cpunodebind=0 --membind=0 ./trading_engine
```

**程式碼修正**：
```cpp
// 確保記憶體池在執行緒的 NUMA 節點上配置
void* allocateOnLocalNode(size_t size) {
    void* ptr = numa_alloc_local(size);
    return ptr;
}
```

---

## 11. 效能基準參考數據

### 11.1 典型組件延遲（3GHz CPU）

| 操作類型 | CPU 週期 | 時間（奈秒） | 說明 |
|---------|---------|------------|------|
| L1 Cache 讀取 | 4-5 | 1.3-1.6 | 最快記憶體存取 |
| L2 Cache 讀取 | 12-15 | 4-5 | 次快記憶體存取 |
| L3 Cache 讀取 | 40-75 | 13-25 | 跨核心共享快取 |
| 主記憶體讀取 | 200-300 | 67-100 | Cache Miss 懲罰 |
| RDTSC 指令 | 20-40 | 7-13 | 計時開銷 |
| 原子操作（std::atomic） | 50-100 | 17-33 | 記憶體屏障開銷 |
| Mutex Lock/Unlock | 50-200 | 17-67 | 無競爭情況 |
| Context Switch | 3000-10000 | 1-3.3μs | 作業系統排程 |
| 系統呼叫 | 500-2000 | 167-667 | 核心態切換 |

### 11.2 低延遲系統預算

一個端到端（End-to-End）交易延遲預算範例：

| 階段 | 預算（微秒） | 累計 |
|------|-------------|------|
| 訂單接收（OrderGateway） | 1-2 | 2 |
| FIFO 排序（FIFOSequencer） | 0.5-1 | 3 |
| 撮合引擎（MatchingEngine） | 1-3 | 6 |
| 行情發布（MarketDataPublisher） | 0.5-1 | 7 |
| 網路傳輸（Multicast） | 10-50 | 57 |
| **總計（同機房）** | **~7-57μs** | |

**優化目標**：
- P50 < 10μs（中位延遲）
- P99 < 50μs（長尾延遲）
- P99.9 < 100μs（極端情況）

---

## 總結

Chapter 11 為系統建立了一雙「眼睛」。透過 `rdtsc()` 量測工法，我們將低延遲系統的開發從「憑感覺優化」提升到了「數據驅動優化」的層次。

**關鍵要點**：
1. ⚡ **RDTSC 量測**：極低開銷（~10ns），適合熱路徑
2. 📊 **分佈分析**：P50/P90/P99 指標，識別長尾延遲
3. 🔧 **CPU 親和性**：核心隔離 + 頻率鎖定，減少抖動
4. ⚠️ **觀察者效應**：條件編譯 + 取樣量測，最小化干擾
5. 🎯 **瓶頸識別**：數據驅動決策，優先優化熱點

這為 Chapter 12 的基準測試（Benchmarks）與最終性能調優奠定了基礎。

