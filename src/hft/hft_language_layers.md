# 高頻交易系統的語言分層與選擇

## 一、核心觀念

在高頻交易（High-Frequency Trading, HFT）中，**每微秒延遲都可能造成盈虧差異**。  
因此，語言的選擇取決於：
- 延遲的可預測性（Latency Determinism）
- 記憶體控制能力
- 系統整合與硬體貼近度

---

## 二、語言比較總覽

| 特性 | C/C++ | Rust | Go |
|------|--------|--------|----|
| GC | ❌ 無 | ❌ 無 | ✅ 有 |
| 延遲穩定性 | ✅ 極高 | ✅ 極高 | ⚠️ 不穩定 |
| 記憶體控制 | ✅ 完全手動 | ✅ 編譯期安全 | ❌ 自動分配 |
| Thread / CPU 控制 | ✅ 完全可控 | ✅ 完全可控 | ⚠️ runtime 管理 |
| 開發速度 | ⚠️ 慢 | ⚠️ 中等 | ✅ 快 |
| 適合 HFT 核心 | ✅ | ✅ | ❌ |
| 適合後臺服務 | ⚠️ | ✅ | ✅✅ |

---

## 三、Go 的劣勢（為何不適合 HFT 核心）

1. **Garbage Collector (GC)**
   - 會產生 stop-the-world 暫停。
   - 雖短暫，但在微秒級交易仍是致命延遲。

2. **調度器不穩定**
   - Goroutine 會被 runtime scheduler 移動到不同核心，  
     導致 cache locality 不穩定。

3. **記憶體與 CPU 控制弱**
   - 難以控制記憶體配置、NUMA、hugepage、pinning。
   - 難以達成零拷貝與 cache-aware 設計。

---

## 四、C/C++ / Rust 的優勢

1. **無 GC、延遲可預測**
   - Rust 提供零成本安全機制；C/C++ 完全手動控制。

2. **貼近硬體層**
   - 能使用 `mmap`、`RDMA`、`io_uring`、DPDK 等技術。
   - 可實現 kernel bypass、零拷貝傳輸。

3. **Cache / 記憶體佈局控制**
   - `struct` / `#[repr(C, packed)]` 精確控制記憶體 layout。
   - 避免 false sharing / cache line bouncing。

---

## 五、語言應用分層

| 系統層 | 語言建議 | 特性說明 |
|--------|------------|-----------|
| **Feed Handler / Strategy Engine** | C/C++, Rust | 極低延遲、零拷貝、核心運算區 |
| **Order Gateway** | C/C++, Rust | 下單通道、需可控延遲 |
| **Risk Check / Reporting** | Go | 非核心路徑、重視開發效率 |
| **Back Office / Monitoring** | Go, Rust | 穩定性與開發速度兼顧 |

---

## 六、實際業界案例

| 公司 | 使用語言 | 備註 |
|------|-----------|------|
| Jump Trading / Citadel / DRW | C++ / Rust | 最低延遲引擎 |
| Jane Street | OCaml / C++ / Rust | 策略層 OCaml，底層 C++ |
| Two Sigma | C++ / Rust / Python | 引擎層 C++/Rust，策略層 Python |
| Coinbase / Binance | Go / Rust / C++ | API 層 Go，撮合層 Rust/C++ |

---

## 七、視覺分層示意（簡化版）

```

┌────────────────────────┐
│ BACK OFFICE            │ → Go, Rust
├────────────────────────┤
│ RISK CHECK, REPORTING  │ → Go
├────────────────────────┤
│ ORDER GATEWAY          │ → C/C++, Rust
├────────────────────────┤
│ FEED HANDLER, STRATEGY │ → C/C++, Rust
└────────────────────────┘

```

---

## 八、結論
- HFT 最重視的是「延遲穩定性」與「可預測性」。
- Rust 結合 C++ 的效能與記憶體安全，是未來主流趨勢。
- Go 適合做週邊服務與非核心邏輯，不適合關鍵撮合 loop。

