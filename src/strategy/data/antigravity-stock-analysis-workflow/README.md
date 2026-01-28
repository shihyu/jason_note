# 股票分析工作流 (Stock Analysis Workflow)

這是一套自動化的股票分析系統，協助你從數據收集、風險評估到生成交易報告。

## 🚀 快速開始

### 1. 完整分析單一標的
想要對一支股票進行深度研究時使用：
```
/full-analysis [TICKER]
```
**範例**: `/full-analysis RCAT`
- 自動收集即時報價、財報、機構持股
- 檢查催化劑（PDUFA, 財報日, 合約）
- 計算風險評分
- 給出進出場建議
- 自動生成獨立報告並更新匯總

### 2. 短線掃描
想要尋找當下有潛力的交易機會時使用：
```
/stock-scan
```
- 掃描當日熱門股、漲幅排行、期權異動
- 自動過濾低品質標的
- 生成「短線篩選」報告

### 3. 生成總結報告
當你分析完多支股票，想要看彙整結果時：
```
/summary
```
- 讀取所有 Session 數據
- 比較所有標的之優先級與風險報酬比
- 建立催化劑時間軸
- 輸出最終交易決策建議

---

## 📂 檔案結構

所有的分析結果都會自動保存在 `sessions/` 資料夾中：

- `sessions/YYYY-MM-DD-[TICKER]-完整分析.md`: 單一個股的詳細報告
- `sessions/YYYY-MM-DD-完整分析-彙整.md`: 當次 Session 的所有個股匯總
- `sessions/YYYY-MM-DD-總結.md`: 最終的決策指南（由 `/summary` 生成）

---

## 🛠️ 進階指令

如果你只想執行分析的某個部分，可以使用以下指令：

| 指令 | 用途 | 範例 |
|------|------|------|
| `/stock-data` | 僅收集基礎數據 (股價/市值/透過) | `/stock-data PLTR` |
| `/catalyst-check` | 僅檢查催化劑 (財報/FDA/合約) | `/catalyst-check RGNX` |
| `/risk-score` | 僅計算風險評分 | `/risk-score TSLA` |
| `/entry-exit` | 僅做技術面進出場分析 | `/entry-exit NVDA` |

---

## 💡 使用建議 (Best Practices)

1. **每日流程**:
    - 先跑 `/stock-scan` 找靈感
    - 選出 3-5 支有興趣的標的
    - 對每支標的跑 `/full-analysis`
    - 最後跑 `/summary` 做成當日日報

2. **重點關注**:
    - **PDUFA/財報**: 善用 `/catalyst-check` 確保日期準確，生技股二元事件風險大。
    - **風險評分**: 80分以上為「高優先」，60-80 為「中優先」，低於 60 建議觀望。

3. **數據驗證**:
    - 系統會盡量抓取即時數據，但建議在開盤期間重新確認當下波動。

---

## 🔧 IDE 工作流設定

本系統的工作流可以在支援 AI Agent 的 IDE 中使用。以下是各 IDE 的設定方式：

### Antigravity (Google)

**目錄結構**:
```
your-project/
└── .agent/
    └── workflows/
        ├── stock-data.md
        ├── catalyst-check.md
        ├── risk-score.md
        └── ...
```

**檔案格式**:
```yaml
---
description: 工作流的簡短描述
---

# 工作流標題

詳細執行步驟...
```

**特殊標記**:
- `// turbo` - 放在步驟上方，允許該步驟自動執行（無需用戶確認）
- `// turbo-all` - 放在檔案任意位置，允許所有步驟自動執行

**使用方式**: 在聊天視窗輸入 `/workflow-name [參數]`

---

### Cursor

**目錄結構**:
```
your-project/
└── .cursor/
    └── rules/
        ├── stock-data.mdc
        ├── catalyst-check.mdc
        └── ...
```

**檔案格式** (`.mdc`):
```yaml
---
description: 工作流描述
globs: 
alwaysApply: false
---

# 工作流標題

詳細執行步驟...
```

**注意事項**:
- 檔案副檔名必須是 `.mdc`（Markdown Cursor）
- `globs` 可指定適用的檔案類型
- `alwaysApply: true` 會讓規則自動套用

**使用方式**: 在聊天視窗輸入 `/workflow-name [參數]` 或透過 `@rules` 引用

---

### Windsurf

**目錄結構**:
```
your-project/
└── .windsurf/
    └── workflows/
        ├── stock-data.md
        ├── catalyst-check.md
        └── ...
```

**檔案格式**:
```yaml
---
trigger: manual
description: 工作流描述
---

# 工作流標題

詳細執行步驟...
```

**觸發模式** (`trigger`):
- `manual` - 手動觸發
- `always` - 總是套用
- `glob` - 檔案符合條件時觸發（需搭配 `globs` 欄位）

**使用方式**: 在聊天視窗輸入 `/workflow-name [參數]`

---

### 工作流轉換指南

若要將本專案的 workflow 轉換到其他 IDE：

| 來源 (Antigravity) | 目標 IDE | 需修改項目 |
|-------------------|----------|-----------|
| `.agent/workflows/*.md` | Cursor | 複製到 `.cursor/rules/`，改副檔名為 `.mdc` |
| `.agent/workflows/*.md` | Windsurf | 複製到 `.windsurf/workflows/`，加入 `trigger: manual` |
| `// turbo` 標記 | Cursor/Windsurf | 移除（這些 IDE 不支援此標記） |

---

## 📖 English Documentation

For English documentation, please refer to: **[README_EN.md](./README_EN.md)**
