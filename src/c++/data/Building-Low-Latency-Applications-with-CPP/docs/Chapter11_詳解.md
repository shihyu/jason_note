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

## 總結

Chapter 11 為系統建立了一雙「眼睛」。透過 `rdtsc()` 量測工法，我們將低延遲系統的開發從「憑感覺優化」提升到了「數據驅動優化」的層次。這為 Chapter 12 的基準測試（Benchmarks）與最終性能調優奠定了基礎。

