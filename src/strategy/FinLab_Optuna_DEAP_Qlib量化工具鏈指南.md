# FinLab、Optuna、DEAP 與 Qlib：量化交易工具鏈指南

量化交易與機器學習的開發流程會用到不同工具。本文整理 FinLab、Optuna、DEAP 與微軟的 Qlib 各自的用途，以及適合使用的階段。

## 一、工具核心定位總覽

```text
【 策略起點：FinLab 】 ── 提供台美股資料與快速回測框架
          │
          ▼
【 參數微調：Optuna 】 ── 搜尋已定義的參數空間（如：均線天數）
          OR
【 架構演化：DEAP 】   ── 演化自訂的策略公式或規則（如：因子公式）
```

這張圖表示一種選用方式，並非必須先用 FinLab 才能使用 Optuna 或 DEAP。Optuna 可搜尋整數、浮點及類別參數；「均線天數」是整數。多目標搜尋也不是 DEAP 獨有功能。選用工具時，應先確認要搜尋的是固定參數，還是自行定義的候選公式或規則結構。參考：[Optuna Trial API](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.trial.Trial.html)、[Optuna 多目標教學](https://optuna.readthedocs.io/en/stable/tutorial/20_recipes/002_multi_objective.html)、[DEAP GP 教學](https://deap.readthedocs.io/en/stable/tutorials/advanced/gp.html)。

| 工具 | 類型 | 主要用途 | 適用情境 |
| --- | --- | --- | --- |
| FinLab | 財經資料庫＋多因子回測引擎 | 策略起跑線：提供台美股資料與選股回測。 | 快速驗證基本面、籌碼面、簡單技術面想法時。 |
| Optuna | 超參數最佳化（預設 TPE sampler） | 智慧型參數微調：在指定的搜尋空間中反覆試驗參數組合。 | 參數範圍明確但組合過多，或需微調 AI 模型超參數時。 |
| DEAP | 演化計算框架（含遺傳演算法與遺傳程式設計） | 大範圍架構演化：透過選擇、交配與突變搜尋候選規則。 | 想讓電腦混搭已定義的指標與運算子，產生候選策略／因子時。 |
| Qlib | AI-oriented 一體化量化平台 | AI 研究管線：整合資料處理、模型、策略與回測。 | 欲引進機器學習模型或進行可重複的 AI 量化實驗時。 |

Optuna 有多種取樣器（sampler），預設使用 TPE。搜尋結果取決於目標函式、搜尋空間與試驗預算，無法保證找到最理想的參數。參考：[Optuna 官方文件](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html)。

FinLab 的台股與美股資料及回測功能可參考[資料 API](https://studio.finlab.finance/docs/reference/data)與[市場物件文件](https://studio.finlab.finance/docs/reference/market)；可用欄位、頻率與市場規則仍須依實際資料集確認。

### DEAP 補充：它會演化什麼？

DEAP 不限定只能做固定參數的遺傳演算法。若把候選因子表示成樹，遺傳程式設計（GP）可以對公式結構做交配與突變；但使用者須先定義允許的輸入欄位、運算子、個體表示法及適應度函式。候選公式仍須經過獨立回測，不能把演化後的高分當成有效交易策略。[DEAP 官方總覽](https://deap.readthedocs.io/en/stable/)、[DEAP GP 教學](https://deap.readthedocs.io/en/stable/tutorials/advanced/gp.html)

### Optuna 補充：它如何微調？

先寫出可回傳分數的 `objective`，再讓每個 trial 選取一組參數並執行評估。適合搜尋指標天數、`learning_rate`、`max_depth` 或持股數等已定義的變數。若訓練能提供中途分數，可另用 pruner 提前結束不理想的 trial；一般回測不一定能直接使用剪枝。[Optuna Study API](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.Study.html)、[Optuna 剪枝說明](https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html)

## 二、Qlib 的核心工作流架構（Workflow）

Qlib 將整個量化流程標準化（Pipeline 化）。實務上，研究員可以使用 YAML 設定檔與 `qrun` 執行資料處理、模型訓練、訊號分析及回測；執行前仍需準備資料、相依套件和適合市場的設定。[Qlib Workflow 官方文件](https://github.com/microsoft/qlib/blob/main/docs/component/workflow.rst)

```text
【 Data 】           ── 資料載入與轉換（Qlib .bin 格式與快取）
   │
   ▼
【 Feature 】        ── 特徵處理（Alpha158 與 Alpha360 資料處理器）
   │
   ▼
【 Forecast Model 】 ── 模型訓練與預測（滾動訓練須另外設定）
   │
   ▼
【 Strategy 】       ── 預測訊號轉化為交易決策（例如 Top-k 選股）
   │
   ▼
【 Backtest 】       ── 按設定的成交規則與成本模擬交易、評估績效
```

流程中的 Alpha158／Alpha360、模型與策略是可選範例，並非一份 YAML 會自動啟用的全部功能。Alpha158 偏向人工設計特徵，Alpha360 主要使用價量時序資料；Qlib 的一般 `qrun` 範例不等於自動執行滾動訓練。預測、交易與績效指標取決於資料切分、模型、策略、成本及報表設定；速度也取決於資料與運行環境。[Qlib 資料層文件](https://github.com/microsoft/qlib/blob/main/docs/component/data.rst)、[Qlib 範例資料集說明](https://github.com/microsoft/qlib/blob/main/examples/benchmarks/README.md)、[Qlib 策略與回測文件](https://qlib.readthedocs.io/en/latest/component/strategy.html)

## 三、進階整合：Qlib 需要先做 Optuna 嗎？

不需要先做，而是可以「包在 Qlib 的工作流中一起跑」，或者在 Qlib 基礎流程確認可重現後再引入。

### 1. 初期階段：Qlib 優先（建立 Baseline）

- **做法**：從 Qlib 範例 YAML 的設定起步，先確認資料源、訓練／驗證／測試區間、模型與策略可正常執行，再依研究問題調整參數。
- **目的**：先跑通 Data 到 Backtest 的流程，檢查資料和特徵有無洩漏、對齊或品質問題。Baseline 不必先「確定能賺錢」；搜尋前需要可信的評估流程。

### 2. 後期階段：Qlib + Optuna 外部整合（策略精進）

建立基準流程後，可用以下架構搜尋超參數（如：`learning_rate`、`max_depth`、Top-K）。應以**驗證區間**的指標作為搜尋分數，扣除適用的交易成本；獨立測試區間保留到搜尋完成後才使用。這種整合需要自行撰寫 `objective`，不是 Qlib YAML 範例內建的 Optuna 功能。[Optuna Study API](https://optuna.readthedocs.io/en/stable/reference/generated/optuna.study.Study.html)、[Qlib Workflow 官方文件](https://github.com/microsoft/qlib/blob/main/docs/component/workflow.rst)

```text
【 Optuna 引擎 】── 建議候選超參數（如：learning_rate, max_depth, Top-K）
       │
       ▼ (傳遞參數組合)
┌─────────────────────────────────────┐
│ Qlib 工作流 (Objective Function)    │
│ 1. 讀取 YAML 並更新參數             │
│ 2. 訓練 AI 模型 (如 LightGBM / GRU) │
│ 3. 跑交易模擬回測 (Backtest)        │
│ 4. 輸出評分指標 (如：回測夏普值)    │
└─────────────────────────────────────┘
       │
       ▼ (回傳夏普值)
【 Optuna 引擎 】── 根據回傳結果，建議下一輪的候選參數
```

### DEAP 與 Qlib 怎麼搭配？

若要搜尋的是公式或規則的**結構**，可讓 DEAP 產生候選因子，再自行撰寫串接程式，用 Qlib 的資料與回測流程評分；選出的候選因子仍須在未參與演化的測試區間驗證。若只有少量固定參數，Optuna 通常較容易建立可追蹤的試驗。兩者都要控制搜尋次數、資料洩漏與過度擬合。

## 四、實作起點

- **FinLab + Optuna**：先建立可重現的選股與回測流程，再以 Optuna 搜尋技術指標天數。
- **Qlib 標準 YAML 範例**：先熟悉資料、模型、策略與回測設定，再視需求加入參數搜尋。
