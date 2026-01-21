---
description: 建立新的分析 Session，追蹤整個分析流程的數據和進度
---

# 建立分析 Session

在開始分析前，建立一個 Session 檔案來追蹤整個分析流程。

**使用方式**: `/new-session [名稱]`  
**範例**: `/new-session 2026-01-18-短線篩選`

---

## Step 1: 建立 Session 檔案

在當前目錄的 session 資料夾下建立新檔案：

**檔案名稱**: `[YYYY-MM-DD]-[名稱].md`

**初始內容**:

```markdown
# 分析 Session: [名稱]

**建立時間**: YYYY-MM-DD HH:MM  
**狀態**: 🟡 進行中

---

## 📋 分析標的

| Ticker | 優先級 | 數據 | 催化劑 | 風險 | 進出場 |
|--------|--------|------|--------|------|--------|
| | | ⬜ | ⬜ | ⬜ | ⬜ |

圖例: ⬜ 未完成 | 🟡 進行中 | ✅ 已完成

---

## 📊 篩選結果

> 執行 `/stock-scan` 後自動填入

---

## 📈 個股分析

### [TICKER 1]

#### 基礎數據
> 執行 `/stock-data [TICKER]` 後填入

#### 催化劑
> 執行 `/catalyst-check [TICKER]` 後填入

#### 風險評分
> 執行 `/risk-score [TICKER]` 後填入

#### 進出場
> 執行 `/entry-exit [TICKER]` 後填入

---

## 📝 手動筆記

[在此添加任何觀察或備註]

---

## 🔄 執行紀錄

| 時間 | Workflow | 標的 | 備註 |
|------|----------|------|------|
| | | | |
```

---

## Step 2: 通知後續操作

Session 建立完成後，提示用戶：

```
✅ Session 已建立: sessions/[檔案名].md

接下來你可以：
1. `/stock-scan` - 開始篩選標的
2. `/stock-data [TICKER]` - 分析特定標的
3. `/summary` - 輸出最終總結
```

---

## 重要規則

所有後續 workflow 執行時，都應該：
1. 讀取當前 session 檔案
2. 更新對應區塊的數據
3. 更新執行紀錄表

這樣可以確保數據跨 workflow 同步。