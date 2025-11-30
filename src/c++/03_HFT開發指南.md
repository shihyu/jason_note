# HFT 高頻交易開發指南

> C++ 在高頻交易中的應用與優化。

## 🎯 為什麼選擇 C++

### C++ 優勢
- [為什麼選擇 C++ 開發 HFT](why_cpp_for_hft.md)

核心優勢：
- **極致性能**: 零成本抽象、直接硬體控制
- **可預測性**: 確定性延遲、無 GC
- **低延遲**: 納秒級優化空間
- **硬體親和**: CPU affinity、NUMA 優化

## 📖 HFT 開發完整指南

### 系統架構
- [C++ HFT 開發完整指南](cpp_hft_guide.md)
- [HFT](HFT.md) - HFT 核心技術

核心內容：
- 低延遲系統設計
- 市場數據處理
- 訂單執行優化
- 風險控制系統

## 🏢 實戰案例

### UC Capital
- [UC_CAPITAL](UC_CAPITAL.md) - 實際應用案例

## 💡 HFT 核心技術

### 低延遲優化
1. **網路層優化**
   - Kernel bypass (DPDK)
   - TCP/UDP 優化
   - 零拷貝技術

2. **CPU 優化**
   - CPU affinity 綁定
   - 關閉動態頻率調整
   - 禁用 SMT/Hyperthreading

3. **記憶體優化**
   - Huge pages
   - NUMA 感知分配
   - Lock-free 數據結構

### 系統調優
1. **Linux Kernel**
   - Real-time kernel
   - 中斷親和性
   - Tickless mode

2. **編譯器優化**
   - LTO (Link Time Optimization)
   - PGO (Profile Guided Optimization)
   - -O3 -march=native

3. **硬體選擇**
   - 低延遲網卡
   - 高頻 CPU
   - NVMe SSD

### 監控與測試
1. **延遲測試**
   - 99.9% 延遲
   - Jitter 測量
   - 端到端延遲

2. **性能監控**
   - perf 工具
   - 硬體計數器
   - 火焰圖分析

**最後更新**: 2025-12-01
