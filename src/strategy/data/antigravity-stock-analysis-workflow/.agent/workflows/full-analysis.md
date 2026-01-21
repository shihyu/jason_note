---
description: 對指定標的執行完整分析流程（數據+催化劑+風險+進出場）
---

# 完整分析流程

對單一標的依序執行所有分析 workflow，一次完成全部數據收集。

**使用方式**: `/full-analysis [TICKER]`  
**範例**: `/full-analysis VKTX`

---

## 執行順序

```
Step 1: /stock-data [TICKER]     → 基礎數據
Step 2: /catalyst-check [TICKER] → 催化劑時間表
Step 3: /risk-score [TICKER]     → 風險評分
Step 4: /entry-exit [TICKER]     → 進出場建議
Step 5: 更新 Session 檔案        → 彙整所有結果
```

---

## Step 1: 收集即時基礎數據

**重要**: 必須獲取最新的即時數據，不能使用過時資訊。

### 1.1 即時報價數據

// turbo
1. 搜尋「[TICKER] stock price today real time」
2. 搜尋「[TICKER] market cap volume today」
3. 優先使用：Yahoo Finance, Google Finance, MarketWatch, TradingView

### 1.2 財務與機構數據

// turbo
1. 搜尋「[TICKER] latest earnings report Q[X] 2026」
2. 搜尋「[TICKER] institutional ownership changes」
3. 搜尋「[TICKER] analyst ratings upgrades downgrades」

### 1.3 期權市場數據

// turbo
1. 搜尋「[TICKER] options flow unusual activity」
2. 搜尋「[TICKER] implied volatility IV rank」
3. 優先使用：Barchart, Unusual Whales, Market Chameleon

### 1.4 數據驗證

確認所有數據都是當天或最近 1 個交易日的：
- ✅ 股價：必須是當天或最近收盤價
- ✅ 市值：根據最新股價計算
- ✅ 成交量：當天或昨日數據
- ⚠️ 財務數據：最新季報（標註季度）
- ⚠️ 機構持股：最近 13F 申報（標註日期）

**輸出格式**：
```markdown
**股價**: $XX.XX (更新: YYYY-MM-DD HH:MM)
**市值**: $X.XB (更新: YYYY-MM-DD HH:MM)
**日均量**: X.XM 股 (更新: YYYY-MM-DD)
```

---

## Step 2: 催化劑檢查

執行 `/catalyst-check [TICKER]` 的完整流程：

### 2.1 近期催化劑搜尋

// turbo
1. 搜尋「[TICKER] earnings date Q[X] 2026」
2. 搜尋「[TICKER] FDA PDUFA date 2026」（生技股）
3. 搜尋「[TICKER] government contract award 2026」（軍工/能源股）
4. 搜尋「[TICKER] news today catalyst」

### 2.2 催化劑驗證

確認每個催化劑的：
- ✅ 確切日期（如果有）
- ✅ 事件類型（財報/PDUFA/合約/產品發布）
- ✅ 來源連結（可驗證）
- ⚠️ 時效性（是否已過期）

**輸出格式**：
```markdown
- **YYYY-MM-DD**: [事件名稱] 🔥 (來源: [連結])
```

---

## Step 3: 風險評分

執行 `/risk-score [TICKER]` 的完整流程：
- 催化劑明確度評分 (30%)
- 基本面健康度評分 (25%)
- 期權活躍度評分 (20%)
- 機構參與度評分 (15%)
- 流動性評分 (10%)
- 計算總分並分類優先級

---

## Step 4: 進出場分析

執行 `/entry-exit [TICKER]` 的完整流程：

### 4.1 技術面即時數據

// turbo
1. 搜尋「[TICKER] technical analysis RSI MACD today」
2. 搜尋「[TICKER] support resistance levels」
3. 優先使用：TradingView, StockCharts, Finviz

### 4.2 分析師目標價

// turbo
1. 搜尋「[TICKER] analyst price target 2026」
2. 搜尋「[TICKER] analyst ratings consensus」

### 4.3 計算進出場點

基於即時數據計算：
- **當前價**: $XX.XX
- **進場價**: 根據支撐位/催化劑時間
- **停損**: 當前價 -10% 至 -15%
- **目標價**: 分析師平均目標價或技術面壓力位
- **風險報酬比**: (目標價 - 進場價) / (進場價 - 停損)

---

## Step 5: 更新 Session

在當前 Session 檔案中：

1. **新增個股區塊**（如不存在）：

```markdown
### [TICKER]

#### 基礎數據
[Step 1 結果]

#### 催化劑
[Step 2 結果]

#### 風險評分
[Step 3 結果]

#### 進出場
[Step 4 結果]
```

2. **更新分析標的表格**：

```markdown
| [TICKER] | [優先級] | ✅ | ✅ | ✅ | ✅ |
```

3. **新增執行紀錄**：

```markdown
| [時間] | /full-analysis | [TICKER] | 完整分析完成 |
```

---

## 輸出格式

完成後輸出彙整摘要：

```markdown
# [TICKER] 完整分析報告

**分析時間**: YYYY-MM-DD HH:MM
**數據更新時間**: YYYY-MM-DD HH:MM (即時)

---

## 📊 摘要

| 項目 | 數值 |
|------|------|
| 股價 | $XX.XX (即時) |
| 市值 | $X.XB (即時) |
| 數據時間 | YYYY-MM-DD HH:MM |
| 優先級 | 🟢/🟡/🔴 |
| 評分 | XX/100 |
| 最近催化劑 | [日期] [事件] |
| 建議進場價 | $XX.XX |
| 停損 | $XX.XX (-XX%) |
| 目標價 | $XX.XX (+XX%) |
| 風險報酬比 | X.X:1 |

---

## ⚡ 快速決策

- **動作建議**: [買入/觀望/避開]
- **理由**: [一句話說明]
- **注意事項**: [關鍵風險提醒]

---

---

## 🔗 關鍵來源紀錄
- **催化劑來源**: [連結/標題]
- **財務數據來源**: [連結/標題]

詳細數據已同步至 Session 檔案。
```

---

## 後續動作

- `/summary` - 若已分析多個標的，輸出總結報告（會自動更新所有即時數據）
- `/full-analysis [其他TICKER]` - 繼續分析下一個標的

---

## ⚠️ 重要提醒

1. **必須使用即時數據**：所有股價、市值、成交量都必須是當天或最近交易日的數據
2. **標註數據時間**：每個數據點都要標註更新時間，方便後續驗證
3. **驗證催化劑時效**：確認所有催化劑日期都在未來，已過期的要標註
4. **來源可驗證**：所有關鍵數據都要附上來源連結，便於查證
