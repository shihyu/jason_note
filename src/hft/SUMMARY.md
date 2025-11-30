# 高頻交易 (HFT) 技術文檔

## 概述
- [HFT 系統總覽](06-resources/hft-index.md)
- [高性能運算與低延遲交易技術概覽](06-resources/hft-introduction.md)

---

## 01. 語言與技術選型

### 語言比較與選擇
- [語言分層架構](01-language/language-layers.md) - C/C++/Rust/Go 在 HFT 系統中的分層應用
- [並發編程模型比較](01-language/concurrency-comparison.md) - Python/C++/Rust 並發模型深度對比
- [API 交易性能指南](01-language/api-performance-guide.md) - 各語言在 API 交易中的性能排名

### 特定語言指南
- [C++ 開發指南](01-language/cpp-guide.md) - C++ HFT 核心編程技術
- [Rust 開發指南](01-language/rust-guide.md) - Rust 在 HFT 中的應用與優勢
- [為什麼 HFT 避開 Go](01-language/why-avoid-go.md) - Go 語言的 GC 問題與適用場景
- [Rust/C++ 互操作](01-language/rust-cpp-integration.md) - 整合臺灣券商 C++ API

---

## 02. 系統優化

### 作業系統選擇與調優
- [OS 選擇指南](02-system/os-selection.md) - 為何選擇 Linux、核心繞過、FPGA 協同
- [OS 調優完整指南](02-system/os-tuning-guide.md) - 核心隔離、NUMA、開源項目、臺灣市場實踐
- [OS 調優實踐手冊](02-system/os-tuning-practice.md) - 詳細的調優步驟與白話解釋
- [系統效能優化](02-system/system-optimization.md) - NUMA、CPU 隔離、中斷優化、快取優化

### 專項優化技術
- [C 語言終極優化](02-system/c-optimization-complete.md) - 位元運算、查表法、SIMD、Lock-free、FPGA
- [大頁面與執行緒模型](02-system/hugepages-threading.md) - HugePages、TLB 優化、執行緒設計

---

## 03. 網路與 I/O 優化

### 核心技術
- [網路優化完整指南](03-network/network-optimization.md) - 零拷貝、TCP/UDP 調優、多播、Co-location
- [Kernel Bypass 技術](03-network/kernel-bypass.md) - DPDK、XDP、Solarflare OpenOnload
- [網路 I/O 與 FPGA 整合](03-network/network-fpga-guide.md) - 零拷貝、RDMA、硬體時間戳、FPGA 加速

### DPDK 專題
- [DPDK 完整介紹](03-network/dpdk-introduction.md) - 什麼是 DPDK、核心概念、為何需要
- [DPDK 雙埠測試](03-network/dpdk-port-testing.md) - DPDK 20 環境配置、安裝、測試步驟
- [DPDK + QEMU + GDB 調試](03-network/dpdk-qemu-gdb.md) - 虛擬化環境下的 DPDK 調試

---

## 04. 測試與性能監控

- [延遲測試指南](04-testing/latency-testing.md) - Micro-benchmark、P99/P99.9 測量、測試工具
- [異步編程 vs HFT](04-testing/async-vs-hft.md) - 異步模式在 HFT 的適用性分析

---

## 05. 實踐案例

- [執行緒池優化案例](05-practice/thread-pool-optimization.md) - 50+ 連線下降低 P99 延遲 97%

---

## 06. 資源與參考

- [GitHub 開源項目分析](06-resources/github-projects.md) - exchange-core、SubZero、FPGA 項目
- [HFT 系統索引](06-resources/hft-index.md) - 架構、關鍵技術、策略、開發建議

---

## 附錄：程式碼實例與工具

### 優化工具套件
- [HFT 優化工具集](hft_optimization_suite/) - 實用優化工具與腳本
- [Kernel Bypass 套件](kernel_bypass_suite/) - 核心旁路技術實現

### 實踐項目
- [低延遲應用開發](src/Building-Low-Latency-Applications-with-CPP/) - C++ 低延遲應用實例
- [延遲測試工具](src/latency_testing/) - 專業延遲測試框架
- [Imperial HFT 設計模式](src/imperial_hft/) - 分支減少等設計模式
- [API 測試服務器](src/test_api_server/) - HFT 優化的 API 測試環境

---

## 快速導航

### 新手入門
1. [高性能運算概覽](06-resources/hft-introduction.md) ← **從這裡開始**
2. [語言分層架構](01-language/language-layers.md)
3. [OS 選擇指南](02-system/os-selection.md)

### 系統優化路徑
1. [OS 調優完整指南](02-system/os-tuning-guide.md)
2. [網路優化指南](03-network/network-optimization.md)
3. [延遲測試](04-testing/latency-testing.md)

### 深入學習
1. [C 語言終極優化](02-system/c-optimization-complete.md)
2. [Kernel Bypass](03-network/kernel-bypass.md)
3. [DPDK 深度學習](03-network/dpdk-introduction.md)

---

## 文檔說明

### 檔案組織原則
- **01-language/**: 語言選型與比較（7 個檔案）
- **02-system/**: 系統層優化（6 個檔案）
- **03-network/**: 網路與 I/O 優化（6 個檔案）
- **04-testing/**: 測試與監控（2 個檔案）
- **05-practice/**: 實踐案例（1 個檔案）
- **06-resources/**: 資源與參考（3 個檔案）

### 重點推薦檔案
- 🔥 [OS 調優完整指南](02-system/os-tuning-guide.md) - 最全面的調優文檔
- 🔥 [C 語言終極優化](02-system/c-optimization-complete.md) - 涵蓋所有優化層面
- 🔥 [網路 I/O 與 FPGA 整合](03-network/network-fpga-guide.md) - 硬體加速深度指南

### 相似主題說明
部分檔案內容有重疊但角度不同，已保留以提供多元視角：
- `os-tuning-guide.md` vs `os-tuning-practice.md` - 前者含臺灣市場實踐，後者有詳細白話解釋
- `system-optimization.md` vs `os-tuning-practice.md` - 前者技術導向，後者實踐導向

---

**最後更新**: 2025-11-30
**總檔案數**: 25 個核心文檔 + 多個實踐項目
