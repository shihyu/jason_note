# AXS 系統深度分析報告總覽 (Analysis Report Overview)

## 專案背景與定位

本 AXS 專案是一個模擬**交易所（Exchange）內部「核心餘額系統」（Balance System / Ledger Service）**的實現。它並非一個完整的交易所系統（不包含搓合引擎、KYC 等），而是專注於處理其中最關鍵且複雜的部分：**高併發的資金管理與帳務結算**。

您可以將其視為交易所的「中央銀行」或「總會計師」，負責以下核心職責：

*   **資金管理**：精確記錄每個用戶在不同幣種下的可用餘額與凍結餘額。
*   **高頻記帳**：在微秒級延遲內處理來自交易引擎的海量餘額變更請求（例如，下單凍結、成交扣款/入帳、撤單解凍）。
*   **風控守門員**：實時檢查用戶餘額是否充足，防止超額提款或交易。
*   **資料強一致性**：確保在任何情況下（包括系統故障），帳務數據的絕對正確性，杜絕任何資產遺失或錯誤。

之所以需要實現「百萬級吞吐量」，是因為在加密貨幣等高流動性交易場景下，單秒內可能產生數十萬甚至百萬計的餘額變更事件。AXS 專案的目標便是展示如何透過極致的技術優化，使一個基於傳統關係型資料庫（PostgreSQL）的系統，也能穩定、高效地承載如此龐大的交易壓力。

---


歡迎來到 AXS 系統的深度分析報告集合！本目錄旨在提供一個從宏觀架構到微觀程式碼實現的全方位視角，幫助您透徹理解這個百萬級吞吐量的交易所餘額系統的設計理念與實作細節。

---

## 報告列表與內容簡介

## 效能數據概覽 (Performance Overview)

**系統能力指標**（基於測試環境數據，詳見 [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md)）：

| 指標 | 數值 | 說明 |
|------|------|------|
| **Peak TPS** | ~1,200,000 | 峰值每秒交易處理量 |
| **平均延遲 (P50)** | 45ms | 中位數延遲 |
| **P95 延遲** | 120ms | 95% 請求的延遲上限 |
| **P99 延遲** | 250ms | 99% 請求的延遲上限 |
| **最佳 Batch Size** | 200 | 延遲與吞吐量平衡點 |
| **DB CPU 使用率** | ~65% | 高負載下的穩定狀態 |

---

## 文件導航矩陣 (Navigation Matrix)

### 按閱讀目的選擇

| 我想... | 推薦文件 | 預估閱讀時間 |
|---------|---------|------------|
| **快速了解系統架構** | [axs_architecture_analysis.md](axs_architecture_analysis.md) | 15 分鐘 |
| **理解核心技術實現** | [axs_implementation_deep_dive.md](axs_implementation_deep_dive.md) | 30 分鐘 |
| **深入閱讀程式碼細節** | [axs_code_walkthrough.md](axs_code_walkthrough.md) | 45 分鐘 |
| **獲得全面系統知識** | [axs_complete_system_breakdown.md](axs_complete_system_breakdown.md) | 60 分鐘 |
| **查詢效能基準數據** | [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md) | 10 分鐘 |
| **排查系統問題** | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 按需查詢 |
| **設置監控告警** | [MONITORING_GUIDE.md](MONITORING_GUIDE.md) | 20 分鐘 |
| **理解設計取捨** | [DESIGN_TRADEOFFS.md](DESIGN_TRADEOFFS.md) | 25 分鐘 |

### 按角色選擇

| 角色 | 學習路徑 |
|------|---------|
| **新人工程師** | README (你正在看!) → Architecture → Implementation → Code Walkthrough |
| **資深工程師** | Implementation → Code Walkthrough → Complete Breakdown → Design Tradeoffs |
| **架構師/Tech Lead** | Architecture → Complete Breakdown → Design Tradeoffs → Performance Benchmark |
| **SRE/運維** | Architecture → Troubleshooting → Monitoring Guide |
| **QA/測試** | Architecture → Performance Benchmark → Troubleshooting |

---

## 核心分析報告詳解

### 1. [axs_architecture_analysis.md](axs_architecture_analysis.md) 🏗️
*   **主題**: 系統邏輯架構與模組組裝分析。
*   **內容**: 從 `main.go` 入手，揭示了系統如何使用 Cobra 和 Uber FX 進行命令分派與依賴注入。解釋了系統的入口點、主要應用模組（Consumer, gRPC）及其內部組件如何協同工作，並提供了核心數據流（gRPC → Kafka → Consumer → DB）的概覽，包含改進後的 Mermaid 架構圖。
*   **適合對象**: 想要快速了解系統整體架構、各部分職責及高階數據流的讀者。
*   **關鍵亮點**:
     - ✅ 流程順序標記（①-⑨）
     - ✅ Outbox Pattern 視覺化
     - ✅ Leader Election + Fencing Token 說明

### 2. [axs_implementation_deep_dive.md](axs_implementation_deep_dive.md) 🔬
*   **主題**: 實作技術深度分析與設計理念對照。
*   **內容**: 對照原始設計文件，詳細闡述了 AXS 如何實作關鍵技術，包括智慧批次消費、高效批次寫入 DB (COPY + CTE)、新幣種 Lazy Insert、以及冪等性與腦裂防護。**新增了全面的風險評估章節**，包含 UNLOGGED TABLE 風險、批次回滾代價、Memory Bloat 問題及其緩解策略。
*   **適合對象**: 想要深入理解 AXS 系統如何將設計理念轉化為具體技術實現的讀者。
*   **關鍵亮點**:
     - ✅ 7 大風險項目詳細分析
     - ✅ 風險矩陣與優先級排序
     - ✅ 具體的緩解策略

### 3. [axs_code_walkthrough.md](axs_code_walkthrough.md) 💻
*   **主題**: 核心程式碼逐行導讀。
*   **內容**: 針對批次消費模組 (`batch_consumer.go`)、核心處理與腦裂防護模組 (`event_leader_election.go`)、以及極速寫入模組 (`apply_balance_change_dao.go`) 中的關鍵程式碼進行逐行剖析。**補充了完整的 CTE SQL 範例**，包含錯誤檢查（error_records）與統計驗證邏輯。
*   **適合對象**: 對具體程式碼實現細節感興趣，希望從程式碼層面理解系統運作原理的讀者。
*   **關鍵亮點**:
     - ✅ 完整的 SQL CTE 邏輯拆解（含錯誤處理）
     - ✅ 雙重 Timeout 機制詳解
     - ✅ Fencing Token 程式碼範例

### 4. [axs_complete_system_breakdown.md](axs_complete_system_breakdown.md) 📚
*   **主題**: AXS 系統全方位解構與設計總結。
*   **內容**: 這份報告是對前面所有分析的最終整合。它將設計文件中的每一個設計點與專案中對應的程式碼位置精確對照。此外，它還深入探討了資料庫 Schema 設計與分片策略、壓測與監控體系、**完整的錯誤處理策略（含錯誤分類表與 DLQ 流程圖）**，以及基礎設施與部署等完整面向。
*   **適合對象**: 想要獲得 AXS 系統最全面、最綜合理解的讀者，建議在閱讀完前三份報告後再閱讀此份報告。
*   **關鍵亮點**:
     - ✅ 設計點到程式碼的完整對照表
     - ✅ 錯誤分類與處理策略（9 種錯誤類型）
     - ✅ DLQ 處理流程圖與監控指標

### 5. [PERFORMANCE_BENCHMARK.md](PERFORMANCE_BENCHMARK.md) ⚡ **[NEW]**
*   **主題**: 效能測試報告與基準數據。
*   **內容**: 詳細的效能測試結果，包含不同 Batch Size 的對比、資源使用分析、壓測工具說明，以及生產環境配置建議。
*   **適合對象**: 需要了解系統實際效能表現、進行容量規劃或效能優化的讀者。

### 6. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) 🔧 **[NEW]**
*   **主題**: 常見問題排查指南。
*   **內容**: 涵蓋 Kafka、PostgreSQL、Consumer、gRPC 等各模組的常見問題，每個問題包含症狀、原因、診斷步驟和解決方案。
*   **適合對象**: 運維人員、On-call 工程師，以及需要快速定位並解決問題的開發者。

### 7. [MONITORING_GUIDE.md](MONITORING_GUIDE.md) 📊 **[NEW]**
*   **主題**: 監控指標與告警設置指南。
*   **內容**: 核心監控指標列表、正常範圍與異常閾值、Prometheus 查詢範例、Grafana Dashboard 設計建議、告警規則配置。
*   **適合對象**: SRE、DevOps 工程師，以及負責系統可觀測性的團隊。

### 8. [DESIGN_TRADEOFFS.md](DESIGN_TRADEOFFS.md) ⚖️ **[NEW]**
*   **主題**: 設計決策與權衡分析。
*   **內容**: 深入討論為什麼選擇批次處理、為什麼使用 UNLOGGED TABLE、為什麼選擇 PostgreSQL 而非其他資料庫等關鍵設計決策背後的思考。
*   **適合對象**: 架構師、Tech Lead，以及想要理解「為什麼這樣設計」的工程師。

---

## 建議閱讀順序

為了獲得最連貫且深入的學習體驗，建議您按照以下順序閱讀這些報告：

1.  **[axs_architecture_analysis.md](axs_architecture_analysis.md)**：建立對系統的整體概念。
2.  **[axs_implementation_deep_dive.md](axs_implementation_deep_dive.md)**：理解關鍵技術的實現思路。
3.  **[axs_code_walkthrough.md](axs_code_walkthrough.md)**：深入程式碼層面，看懂具體實現細節。
4.  **[axs_complete_system_breakdown.md](axs_complete_system_breakdown.md)**：總結並補齊所有剩餘的設計與實作環節，形成全面視角。

祝您學習愉快！
