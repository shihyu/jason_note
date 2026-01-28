# 產業輪動檢測系統 - 使用指南

## 🎯 Phase 4 最佳化引數（已內建）

系統已自動應用以下最佳引數：

```
✓ taker_ratio > 1.0      (買盤優勢 - 最重要)
✓ rank_pct > 0.6         (排名前 40%)
✓ early_methods >= 2     (至少 2/3 早期方法觸發)
✓ combined_score > 0.65  (綜合分數門檻)
✓ top_n = 15             (每日最多 15 個訊號)
```

**這些引數經過 2 年曆史回測驗證，達到 100% 檢出率（6/6 已知事件）。**

---

## 📋 指令參數說明

### `make rotation-detect` 可用參數

| 參數 | 說明 | 預設值 | 範例 |
|------|------|--------|------|
| `START_DATE` | 檢測開始日期 | 7 天前 | `START_DATE=2026-01-20` |
| `END_DATE` | 檢測結束日期 | 今天 | `END_DATE=2026-01-27` |

**Phase 4 內建優化參數（不可調整）**：

| 參數 | 條件 | 說明 |
|------|------|------|
| `taker_ratio` | > 1.0 | 買盤優勢（買盤/賣盤比值）|
| `rank_pct` | > 0.6 | 排名前 40%（相對強度）|
| `early_methods` | >= 2 | 至少 2/3 早期方法觸發 |
| `combined_score` | > 0.65 | 綜合分數門檻 |
| `top_n` | = 15 | 每日最多 15 個信號 |

**使用範例**：
```bash
# 預設：檢測最近 7 天
make rotation-detect

# 指定日期範圍
make rotation-detect START_DATE=2026-01-20 END_DATE=2026-01-27

# 檢測單日
make rotation-detect START_DATE=2026-01-27 END_DATE=2026-01-27
```

---

## 🚀 快速開始

### 1️⃣ 檢測最近 7 天（預設）

```bash
make rotation-detect
```

### 2️⃣ 指定日期範圍

```bash
# 檢測特定期間
make rotation-detect START_DATE=2026-01-20 END_DATE=2026-01-27

# 檢測單日
make rotation-detect START_DATE=2026-01-27 END_DATE=2026-01-27

# 檢測最近一個月
make rotation-detect START_DATE=2025-12-27 END_DATE=2026-01-27
```

---

## 📂 輸出檔案

### 1. `data/rotation_signals_YYYY-MM-DD.csv`
**每日發動訊號清單**（最重要，直接使用）

#### 欄位詳解

| 欄位 | 類型 | 範圍 | 說明 | 重要性 |
|------|------|------|------|--------|
| `date` | 日期 | YYYY-MM-DD | 檢測日期 | ⭐ |
| `industry` | 字串 | - | 產業名稱（如：IC設計指標） | ⭐⭐⭐ |
| `signal_type` | 字串 | strong_outbreak | 信號類型（Phase 4 僅輸出強勢買盤信號） | ⭐ |
| `combined_score` | 浮點數 | 0.0-1.0 | 綜合分數（加權平均所有方法分數） | ⭐⭐ |
| `taker_ratio` | 浮點數 | >1.0 | 內外盤比（買盤/賣盤），數值越大買盤越強 | ⭐⭐⭐ |
| `z_score` | 浮點數 | - | 標準化分數（與歷史平均的偏離程度） | ⭐ |
| `rank_pct` | 浮點數 | 0.0-1.0 | 排名百分位（0.989 = 前 1.1%） | ⭐⭐ |
| `early_methods` | 整數 | 2-3 | 觸發的早期檢測方法數量（最多 3 種） | ⭐⭐ |
| `method1` | 整數 | 0/1/-1 | 方法 1 異常檢測（1=觸發，0=未觸發） | ⭐ |
| `method2` | 整數 | 0/1/-1 | 方法 2 排名變化（1=觸發，0=未觸發） | ⭐ |
| `method3` | 整數 | 0/1/-1 | 方法 3 變化率（1=觸發，0=未觸發） | ⭐ |

#### 三種早期檢測方法說明

| 方法 | 欄位 | 權重 | 檢測內容 | 觸發條件 |
|------|------|------|----------|----------|
| **Method 1** | `method1` | 40% | 異常強度檢測 | 內外盤比突然暴增（偏離移動平均 >2 倍標準差） |
| **Method 2** | `method2` | 30% | 排名變化檢測 | 排名快速躍升（3 天內排名提升 >20%） |
| **Method 3** | `method3` | 20% | 變化率檢測 | 內外盤比加速上升（2 天內變化率 >15%） |

**註**：
- `method1/2/3` 值為 `1` 表示該方法觸發買盤信號
- `early_methods` = 觸發方法總數（例如：method1=1, method2=1, method3=0 → early_methods=2）
- Phase 4 要求至少 2 種方法同時觸發才會產生信號

#### CSV 範例

```csv
date,industry,signal_type,combined_score,taker_ratio,z_score,rank_pct,early_methods,method1,method2,method3
2026-01-27,清潔用品指標,strong_outbreak,0.777,6.88,6.048,0.989,2,0,1,1
2026-01-27,精準醫療指標,strong_outbreak,0.681,7.054,6.226,0.995,2,0,1,1
2026-01-27,IC設計指標,strong_outbreak,0.693,1.753,0.794,0.951,2,0,1,1
```

**解讀範例**：

以「清潔用品指標」為例：
- `taker_ratio = 6.88`：買盤是賣盤的 6.88 倍 → 強勢買盤進場 ⭐⭐⭐
- `rank_pct = 0.989`：排名前 1.1%（100% - 98.9%）→ 相對強勢 ⭐⭐
- `early_methods = 2`：2 種早期方法觸發（method2=1, method3=1）→ 中高信心度 ⭐⭐
- `combined_score = 0.777`：綜合分數 77.7% → 優質信號 ⭐⭐
- `z_score = 6.048`：偏離歷史平均 6 倍標準差 → 異常強勢 ⭐

### 2. `data/industry_taker_stats.csv`
**完整統計資料**（用於深度分析）

包含所有產業的每日統計，適合：
- 歷史回測
- 引數調優
- 學術研究

---

## 📊 實際使用流程

### Step 1：執行檢測
```bash
make rotation-detect START_DATE=2026-01-20 END_DATE=2026-01-27
```

### Step 2：檢視終端輸出
```
🚀 【發動產業族群】2026-01-27
================================================================================

1. 清潔用品指標
   綜合分數: 0.80 | 內外盤比: 6.88 | Z-score: 6.05 | 排名: 98.9%
   早期訊號: 3/3 個方法觸發
   觸發方法: 異常檢測(強) + 排名變化(升) + 變化率(加速)

2. 精準醫療指標
   綜合分數: 0.70 | 內外盤比: 7.05 | Z-score: 6.23 | 排名: 99.5%
   早期訊號: 2/3 個方法觸發
   觸發方法: 排名變化(升) + 變化率(加速)

...
```

### Step 3：讀取 CSV 檔案（可選）
```bash
# 檢視訊號
cat data/rotation_signals_2026-01-27.csv

# 或用 Excel/LibreOffice 開啟
```

---

## 🎓 訊號解讀指南

### ⭐⭐⭐ 最強訊號（優先關注）

**特徵**：
- `taker_ratio > 3.0`（買盤 > 3 倍賣盤）
- `combined_score > 0.75`
- `early_methods = 3`（全方法觸發）
- `rank_pct > 0.95`（排名前 5%）

**範例**：2026-01-27 清潔用品指標
```
taker_ratio: 6.88 ⭐
combined_score: 0.802 ⭐
early_methods: 3/3 ⭐
rank_pct: 0.989 ⭐
```

### ⭐⭐ 中等訊號（可追蹤）

**特徵**：
- `taker_ratio > 1.5`
- `combined_score > 0.70`
- `early_methods >= 2`
- `rank_pct > 0.90`

**範例**：2026-01-27 IC設計指標
```
taker_ratio: 1.75
combined_score: 0.717
early_methods: 2/3
rank_pct: 0.951
```

### ⭐ 弱訊號（觀察為主）

**特徵**：
- `taker_ratio > 1.0` 但 < 1.5
- `combined_score > 0.65`
- `early_methods = 2`
- `rank_pct > 0.85`

---

## 🔍 常見問題

### Q1：為何今天沒有檢測到訊號？
**A**：可能原因：
1. 市場整體平靜（沒有明顯輪動）
2. Phase 4 最佳化門檻較嚴格（信噪比優先）
3. 建議擴大檢測範圍（例如最近 7 天）

### Q2：如何調整引數？
**A**：不建議手動調整引數。Phase 4 引數已經過 2 年回測最佳化，達到最佳平衡：
- ✅ 100% 檢出率（6/6 已知事件）
- ✅ 平均提前 2 天檢出
- ✅ 信噪比提升 2.5 倍

如果需要更多訊號，請聯絡技術支援。

### Q3：如何解讀 `early_methods`？
**A**：
- `3/3`：3 種早期方法全觸發 → **高信心度** ⭐⭐⭐
- `2/3`：2 種早期方法觸發 → **中信心度** ⭐⭐
- `1/3`：已被系統過濾（不會出現在結果中）

**3 種早期方法**：
1. 異常檢測（Method 1）：內外盤比突然暴增
2. 排名變化（Method 2）：排名快速躍升
3. 變化率（Method 3）：內外盤比加速上升

### Q4：為何某些強勢產業沒有出現？
**A**：Phase 4 最佳化會過濾掉：
- ❌ 賣盤優勢產業（`taker_ratio < 1.0`）→ 下跌訊號
- ❌ 排名較低產業（`rank_pct < 0.6`）→ 相對弱勢
- ❌ 單一方法觸發（`early_methods < 2`）→ 誤判風險高

**系統哲學**：寧缺毋濫，只給高質量訊號。

---

## 📈 實戰建議

### 1️⃣ 每日檢測流程

**早盤前（08:30 前）**：
```bash
# 檢測昨日收盤
make rotation-detect START_DATE=$(date -d "1 day ago" +%Y-%m-%d) END_DATE=$(date -d "1 day ago" +%Y-%m-%d)
```

**盤中追蹤**：
- 觀察訊號中的產業是否持續強勢
- 結合技術面（K線、量價）確認

**收盤後（13:40 後）**：
```bash
# 檢測今日
make rotation-detect START_DATE=$(date +%Y-%m-%d) END_DATE=$(date +%Y-%m-%d)
```

### 2️⃣ 週末覆盤

```bash
# 檢測整週輪動
make rotation-detect START_DATE=$(date -d "7 days ago" +%Y-%m-%d) END_DATE=$(date +%Y-%m-%d)
```

### 3️⃣ 歷史驗證

```bash
# 驗證歷史事件
make rotation-detect START_DATE=2025-01-01 END_DATE=2025-01-10
```

---

## 🛠️ 進階用法

### 批次檢測指令碼

建立 `batch_detect.sh`：

```bash
#!/bin/bash
# 批次檢測最近 30 天，每 7 天一段

END_DATE=$(date +%Y-%m-%d)

for i in {0..3}; do
    START=$(date -d "$((i*7+7)) days ago" +%Y-%m-%d)
    END=$(date -d "$((i*7)) days ago" +%Y-%m-%d)

    echo "=========================================="
    echo "檢測期間: $START ~ $END"
    echo "=========================================="

    make rotation-detect START_DATE=$START END_DATE=$END

    echo ""
    sleep 1
done
```

執行：
```bash
chmod +x batch_detect.sh
./batch_detect.sh
```

---

## 📚 相關文件

- **Phase 4 最佳化報告**：`data/phase4_optimization_report.md`
- **完整回測報告**：`data/backtest_final_report.md`
- **專案計劃**：`../plan.md`

---

## 💡 核心原則

### Phase 4 系統優勢

✅ **早期檢測**：平均提前 2 天發現輪動
✅ **高精度**：100% 檢出率（6/6 已知事件）
✅ **低噪音**：信噪比提升 2.5 倍（12 個/天 vs 30 個/天）
✅ **買盤優勢**：只選「主力進場」訊號，過濾「崩盤反轉」

### 使用建議

1. **每日執行**：養成早盤檢測習慣
2. **結合基本面**：系統提供「技術訊號」，需結合產業訊息
3. **追蹤驗證**：記錄訊號並追蹤後續表現
4. **風險控管**：任何訊號都不保證 100% 獲利，需設定停損

---

**最後更新**：2026-01-27
**系統版本**：Phase 4 Smart Dual-Filter
**維護者**：Tick Strategy Team
