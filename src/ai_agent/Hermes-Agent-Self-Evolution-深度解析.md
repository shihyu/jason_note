# AI Agent 如何自我進化？Hermes Agent Self-Evolution 深度解析 - iTech

## AI Agent 如何自我進化？Hermes Agent Self-Evolution 深度解析

如果 AI Agent 能夠自己改進自己，會是什麼樣子？

這不是科幻小說，而是 Nous Research 正在實作的技術。他們剛剛開放原始碼了 **Hermes Agent Self-Evolution** 專案 —— 一個讓 AI Agent 透過進化演算法自動最佳化自身技能、工具描述、系統提示和程式碼的系統。

**關鍵點**：不需要 GPU 訓練，成本僅 $2-10 每次最佳化，透過 API 呼叫實作，所有改進都需要人工審查。

今天深入拆解這個專案，看看 AI 自我進化的未來。

---

## 一、核心概念：什麼是 Hermes Agent Self-Evolution？

**定義**：一個獨立的最佳化管道，透過自動化最佳化迴圈系統性地改進 Hermes Agent 的效能。

**工作原理**：讀取 Agent 的技能檔案、工具描述、系統提示和程式碼 → 產生評估資料集 → 使用進化演算法產生變體 → 評估效能 → 選擇最佳版本 → 建立 PR 供人工審查。

**三大引擎**：

| 引擎 | 最佳化目標 | 許可證 | 整合方式 |
| --- | --- | --- | --- |
| **DSPy + GEPA** | 技能、提示、指令、工具描述 | MIT | 原生 Python，主引擎 |
| **Darwinian Evolver** | 程式碼檔案、演算法、工具實作 | AGPL v3 | 外部 CLI |
| **DSPy MIPROv2** | Few-shot 範例、指令文字 | MIT | 原生 Python，備用最佳化器 |

**核心亮點**：

⚡ **無需 GPU 訓練**：所有操作透過 API 呼叫完成，DSPy+GEPA 和 MIPROv2 最佳化的是提示、指令和範例的文字，不是模型權重。

**理解"為什麼"失敗**：GEPA 讀取執行追蹤來理解為什麼失敗（不僅僅是失敗的事實），然後提出有針對性的改進。

**低成本**：每次最佳化執行成本約 $2-10，不是昂貴的 GPU 訓練。

**安全可控**：所有變化透過 PR 人工審查，永不直接提交到主分支。

---

## 二、核心技術：DSPy + GEPA

### 2.1 什麼是 GEPA？

**GEPA (Genetic-Pareto Prompt Evolution)** 是整合到 DSPy 中的進化式提示最佳化演算法，具有以下特點：

-   ✅ **反射性分析**：讀取執行追蹤，理解失敗原因
-   ✅ **少樣本高效**：僅需 3 個範例即可工作
-   ✅ **超越 RL**：效能優於強化學習和之前的 DSPy 最佳化器
-   ✅ **ICLR 2026 Oral**：已發表於頂級會議

### 2.2 GEPA 如何工作？

```bash
讀取當前 skill/prompt/tool
         ↓
   產生評估資料集
         ↓
   GEPA 最佳化器 ←── 執行追蹤
     │    ▲
     ▼    │
  候選變體 ────→ 評估
     │
  約束門控（測試、大小限制、基準測試）
     ↓
  最佳變體 ────→ PR 到 hermes-agent
```

**關鍵創新**：GEPA 不只是看到"失敗了"，而是透過執行追蹤理解**為什麼**失敗，然後提出有針對性的改進。

例如，如果 Agent 在某個任務上總是錯誤地選擇了工具，GEPA 會分析執行追蹤，發現混淆點，然後修改工具描述來減少這種混淆。

### 2.3 DSPy 在其中的作用

DSPy 為 Hermes Agent Self-Evolution 提供了：

-   **模組化抽象**：將技能、工具描述、提示包裝為 DSPy 模組
-   **最佳化框架**：統一的最佳化介面
-   **評估管道**：批次執行評估任務
-   **追蹤收集**：擷取執行過程用於反射分析

---

## 三、五階段進化路線圖

Hermes Agent Self-Evolution 的實施分為 5 個階段，每個階段都建立在前一階段的基礎上。

### Phase 1: 技能檔案最佳化（SKILL.md）✅ 已實作

**目標**：最佳化 Agent 技能檔案，這些是 Agent 遵循的程式化指令。

**方法**：  
1. 將技能文字包裝為 DSPy 模組  
2. 透過 batch_runner 在測試任務上評估  
3. 使用 GEPA 進化最佳化

**為什麼有效**：  
- 技能是純文字，易於變異  
- 效能可直接測量（Agent 是否正確完成了任務）  
- 改進效果明顯且易於驗證

**範例**：進化 `github-code-review` 技能，透過測試已知良好程式碼審查的資料集，產生更好的程式碼審查。

**進度**：✅ 已實作

---

### Phase 2: 工具描述最佳化 計劃中

**目標**：最佳化工具架構中的描述欄位（Agent 在決定使用哪個工具時看到的內容）。

**方法**：  
- GEPA 進化描述  
- 評估 Agent 是否為給定任務選擇了正確的工具

**為什麼有效**：  
- 工具選擇是一個分類問題，非常適合 DSPy 最佳化  
- 描述的微小改進可以顯著提高選擇準確性

**範例**：進化 `search_files` 的描述，使 Agent 更可靠地選擇它而不是 `terminal(grep)`。

**約束**：  
- 每個工具描述最多 500 字元（每次 API 呼叫都傳送）  
- 每個引數描述最多 200 字元  
- 必須保持事實準確（不能聲稱工具做了它做不到的事）  
- Schema 結構（引數名稱、型別、必填欄位）是**凍結**的 —— 只有文字進化

**進度**： 計劃中

---

### Phase 3: 系統提示最佳化 計劃中

**目標**：最佳化系統提示的部分（人格、策略、格式說明）。

**方法**：  
- 將 `prompt_builder.py` 部分引數化為 DSPy Signatures  
- 使用 GEPA 最佳化

**為什麼有效**：  
- 系統提示品質直接決定 Agent 行為品質  
- 小的提示改進可以產生大的行為變化

**風險**：  
- ⚠️ 必須小心不要破壞提示快取 —— 只能離線最佳化，部署為新版本

**範例**：進化"工具使用指南"部分，減少不必要的工具呼叫。

**進度**： 計劃中

---

### Phase 4: 工具程式碼最佳化 計劃中

**目標**：最佳化工具實作程式碼、輔助函式。

**方法**：  
- Darwinian Evolver（外部 CLI）  
- 透過 pytest + batch_runner 測試

**為什麼有效**：  
- 某些工具實作有微妙的 bug 或低效  
- 進化搜尋可以找到這些問題

**風險**：  
- ⚠️ 程式碼更改可能破壞東西 —— 需要強大的測試套件作為護欄

**範例**：進化 `file_tools.py` 補丁匹配以處理更多邊緣情況。

**進度**： 計劃中

---

### Phase 5: 持續改進迴圈 計劃中

**目標**：自動化管道，無人值守執行。

**進度**： 計劃中

---

## 四、完整工作流程

### 4.1 高層流程

```vbnet
┌─────────────────────────────────────────────┐
│ 1. SELECT TARGET                            │
│ - 選擇技能、提示部分或工具                   │
│ - 載入當前版本作為基線                       │
│                                              │
│ 2. BUILD EVALUATION DATASET                 │
│ - 從 session_db 挖掘真實使用範例             │
│ - 或使用手工製作的測試用例                   │
│ - 分割：訓練 / 驗證 / 測試                   │
│                                              │
│ 3. WRAP AS DSPy MODULE                      │
│ - 技能文字 → dspy.Signature                 │
│ - Agent 工作流 → dspy.ReAct                  │
│ - 工具選擇 → dspy.Predict                   │
│                                              │
│ 4. RUN OPTIMIZER                            │
│ - 主要：dspy.GEPA（反射性進化）             │
│ - 備用：dspy.MIPROv2（貝葉斯最佳化）         │
│ - 程式碼：Darwinian Evolver（外部 CLI）       │
│                                              │
│ 5. EVALUATE & COMPARE                       │
│ - 在保留測試上執行最佳化版本                   │
│ - 比較：準確性、成本、延遲                   │
│ - 統計顯著性檢驗                             │
│                                              │
│ 6. DEPLOY (with approval)                   │
│ - Git 提交改進版本                           │
│ - A/B 測試（可選）                           │
│ - 透過 git revert 復原機制                   │
└─────────────────────────────────────────────┘
```

### 4.2 詳細架構

```markdown
SessionDB（真實對話）
         │
         ▼
  評估資料集構建器
         │
         ├──► DSPy 模組包裝器（將技能/提示/工具包裝為可最佳化模組）
         │   │
         │   ▼
         │   GEPA 最佳化器 ←── 執行追蹤（來自 batch_runner）
         │     │ ▲
         │     │ │
         │     ▼ │
         │     候選變體 ────► batch_runner（平行評估）
         │     │
         │     ├──► 約束驗證（測試、字元限制、快取相容性）
         │     │
         │     ▼
         │     最佳有效變體
         │     │
         ▼     ▼
  Git 分支 + PR（包含 diff、指標、前後對比）
         │
         ▼
  人工審查與合併
```

---

## 五、評估資料來源

Hermes Agent Self-Evolution 支援四種評估資料來源：

### Source A: 合成產生（主要，引導）

使用強模型（如 Claude Opus）為技能產生測試用例：

1.  讀取技能檔案 → 理解它的作用
2.  產生 15-30 個真實的 `(task_input, expected_behavior)` 對
3.  `expected_behavior` 是一個評分標準，不是確切文字 —— 例如，"應該識別第 42 行的 SQL 注入"而不是"輸出這個確切的字串"
4.  分割：10 訓練 / 5 驗證 / 5-10 保留

GEPA 僅需 3 個範例即可工作，這足夠開始。

### Source B: SessionDB 挖掘（真實使用，LLM-as-judge 評分）

1.  查詢 SessionDB 找到載入技能的會話（在訊息中搜尋技能名稱）
2.  提取使用者給出的任務和 Agent 的完整回應
3.  使用 LLM-as-judge 根據評分標準對每個 `(task, response)` 對評分
4.  高分對成為"好"範例；低分對成為 GEPA 反射分析的失敗案例

隨著更多真實使用積累，這會逐漸改善。

### Source C: 手工製作的黃金集（可選，高價值技能）

手工編寫的測試用例和預期輸出，儲存為 JSONL：

```bash
~/.hermes/evolution/datasets/<skill-name>/golden.jsonl
```

最高品質的訊號，但需要人工努力 —— 保留給關鍵技能。

### Source D: 特定技能的自動評估（適用時）

-   **systematic-debugging**：植入 bug，執行技能，檢查測試是否透過
-   **arxiv**：搜尋已知論文，檢查是否找到
-   **github-code-review**：建立包含植入問題的 PR，檢查是否被擷取

不是所有技能都有自然的自動評估 —— 這是獎勵，不是要求。

---

## 六、評分：LLM-as-judge with Rubrics

對於大多數技能，沒有明確的對/錯 —— 品質是主觀的。適應度函式使用 LLM 評分器根據評分標準評分：

-   **Agent 是否遵循了技能的過程？**（0-1）
-   **輸出是否正確/有用？**（0-1）
-   **是否簡潔（在 token 預算內）？**（0-1）

評分標準是特定於技能的，並儲存在評估資料集旁邊。

---

## 七、約束與護欄

每個進化變體必須透過：

✅ **完整測試套件**：`pytest tests/ -q` 必須 100% 透過

✅ **大小限制**：  
- 技能 ≤ 15KB  
- 工具描述 ≤ 500 字元

✅ **快取相容性**：無對話中途更改

✅ **語義保持**：不得偏離原始目的

✅ **PR 審查**：所有更改都經過人工審查，從不直接提交

---

## 八、專案結構

```php
hermes-agent-self-evolution/  # 獨立倉庫
├── PLAN.md                   # 本檔案
├── README.md                 # 設定、使用、範例
├── pyproject.toml            # 包設定 + 依賴（dspy, gepa）
│
├── evolution/                # 主包
│   ├── core/                 # 共享基礎設施
│   │   ├── __init__.py
│   │   ├── dataset_builder.py      # 評估資料集產生
│   │   ├── fitness.py              # 適應度函式
│   │   ├── constraints.py          # 約束驗證器
│   │   ├── benchmark_gate.py       # 基準門控
│   │   └── pr_builder.py           # 自動產生 PR
│   │
│   ├── skills/               # Phase 1: 技能進化
│   │   ├── evolve_skill.py         # 主入口
│   │   └── skill_module.py         # 將 SKILL.md 包裝為 DSPy 模組
│   │
│   ├── tools/                # Phase 2: 工具描述進化
│   ├── prompts/              # Phase 3: 系統提示進化
│   ├── code/                 # Phase 4: 程式碼進化（Darwinian Evolver）
│   └── monitor/              # Phase 5: 持續迴圈
│
├── datasets/                 # 產生的評估資料集（gitignored，本機）
│   ├── skills/
│   └── tools/
│
└── tests/                    # 測試套件
```

---

## 九、使用範例

### 安裝

```bash
# 克隆並安裝
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution
pip install -e ".[dev]"

# 指向 hermes-agent 倉庫（從 ~/.hermes/hermes-agent 或環境變數自動檢測）
export HERMES_AGENT_REPO=~/.hermes/hermes-agent
```

### Phase 1: 進化一個技能

```bash
# 使用會話歷史的自動產生評估資料
python -m evolution.skills.evolve_skill \
  --skill github-code-review \
  --iterations 10 \
  --eval-source sessiondb

# 或使用合成評估資料
python -m evolution.skills.evolve_skill \
  --skill github-code-review \
  --iterations 10 \
  --eval-source synthetic
```

### Phase 2: 進化工具描述

```bash
python -m evolution.tools.evolve_tool_descriptions \
  --iterations 5 \
  --benchmark-gate tblite-fast
```

### Phase 3: 進化系統提示部分

```bash
python -m evolution.prompts.evolve_prompt_section \
  --section MEMORY_GUIDANCE \
  --iterations 5
```

### Phase 4: 進化工具程式碼

```bash
python -m evolution.code.evolve_tool_code \
  --tool file_tools \
  --bug-issue 742 \
  --iterations 10
```

**所有命令都輸出針對 hermes-agent 的 PR 分支 + 摘要。人工合併。**

---

## 十、關鍵設計決策

### 10.1 為什麼獨立倉庫？

Hermes Agent Self-Evolution 存在於自己的倉庫中，**獨立於 hermes-agent**。它：

-   pip 安裝或克隆 hermes-agent 來存取其基礎設施
-   將進化版本輸出到 git 分支
-   建立 PR 供人工審查

**hermes-agent 程式碼庫無需任何更改**。

### 10.2 為什麼需要人工審查？

所有變化都透過 PR 人工審查：

-   安全性：防止惡意或錯誤的自我修改
-   語義保持：確保進化不偏離原始目的
-   品質控制：人工驗證改進是真實的
-   可追溯性：完整的 Git 歷史記錄所有進化譜系

### 10.3 為什麼階段式實施？

階段是順序的 —— 每個階段都建立在前一個階段的基礎設施上，並且必須在進入下一個階段之前證明自己。

**流程**：

```erlang
Phase 1 ──► 驗證門控 ──► Phase 2 ──► 驗證門控 ──► Phase 3 ──► ...
  構建      是否真的       構建      是否有效       構建
  & 測試     有改進？      & 測試     且沒有破壞     & 測試
```

如果某個階段沒有產生有意義的改進（進化變體不比基線好），我們停止並重新評估再進入下一個階段。

---

## 十一、實際影響與意義

### 11.1 對 AI Agent 開發的意義

**1. 持續改進**：Agent 可以在人工監督下不斷自我改進

**2. 低門檻最佳化**：無需大規模 GPU 訓練，任何團隊都可以使用

**3. 資料驅動**：基於真實使用資料和評估指標最佳化，而非猜測

**4\. 可追溯性**：完整的 Git 歷史記錄所有改進，可以復原

### 11.2 對 AI 安全的意義

**1. 人工審查**：所有改進都需要人工批准，防止不受控制的自我修改

**2. 測試護欄**：完整的測試套件確保改進不會破壞現有功能

**3. 語義保持**：約束確保進化不會偏離原始目的

**4\. 透明性**：PR 中的 diff 清晰顯示所有更改

### 11.3 對 AI 研究的意義

**1. 理論到實踐**：將 ICLR 2026 Oral 論文 GEPA 應用於真實系統

**2. 新正規化**：探索 AI Agent 自我進化的新正規化

**3. 可復現**：開放原始碼實作，社群可以復現和擴充套件

---

## 十二、侷限性

**1. 依賴評估資料品質**：進化效果取決於評估資料集的品質和代表性

**2. 計算成本**：雖然比 GPU 訓練便宜，但多次迭代仍需 API 呼叫成本

**3. 需要人工審查**：每個改進都需要人工審查，可能成為瓶頸

**4\. 適用範圍**：主要適用於基於文字的最佳化，不適用於所有型別的改進

**5\. 局部最優**：進化演算法可能陷入局部最優，需要多次執行或隨機重啟

---

## 十三、未來展望

### 短期（1-3 個月）

-   ✅ 完成 Phase 1-3 的實施和驗證
-   ✅ 在多個技能上證明改進效果
-   ✅ 建立完整的評估和基準測試基礎設施

### 中期（3-6 個月）

-   完成 Phase 4-5 的實施
-   建立自動化持續改進管道
-   擴充套件到更多 AI Agent 系統

### 長期（6-12 個月）

-   探索跨 Agent 的知識共享
-   開發更進階的進化策略
-   建立社群貢獻的評估資料集

---

## 十四、如何貢獻？

如果你想為 Hermes Agent Self-Evolution 做出貢獻：

1.  **報告問題**：在 GitHub Issues 中報告 bug
2.  **提交 PR**：改處理程式式碼、檔案或測試
3.  **貢獻評估資料**：為特定技能貢獻高品質的測試用例
4.  **分享經驗**：在你的專案中使用並分享經驗

---

## 十五、相關資源

-   **GitHub 倉庫**：https://github.com/NousResearch/hermes-agent-self-evolution
-   **PLAN.md**：完整的架構、評估資料策略、約束、基準測試整合和階段性時間表
-   **DSPy**：https://github.com/stanfordnlp/dspy
-   **GEPA 論文**：ICLR 2026 Oral（待釋出）
-   **Nous Research**：https://nousresearch.com/

---

## 十六、總結

Hermes Agent Self-Evolution 代表了 AI Agent 自我進化的一個重要里程碑。透過結合 DSPy 和 GEPA，它實作了一個既安全又有效的自我改進系統。

**核心優勢**：  
- **資料驅動**：基於真實使用資料和評估指標  
- **安全可控**：所有改進需要人工審查  
- **低成本**：無需 GPU，僅 $2-10 每次最佳化  
- **持續改進**：自動化迴圈，無人值守執行  
- **可追溯**：完整的 Git 歷史記錄所有改進

**未來展望**：隨著更多階段的完成和社群的參與，我們有理由相信 AI Agent 的自我進化將成為一個標準能力，推動整個行業的發展。

---

**作者**: TheAIEra  
**來源**: 公眾號：AI 人工智慧時代

_本文首發於 AI 人工智慧時代，轉載請註明出處。_

_關注公眾號，獲取更多 AI 技術乾貨！_
