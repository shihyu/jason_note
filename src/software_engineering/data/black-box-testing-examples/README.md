# 黑箱測試方法實戰範例

> 實作「黑箱測試方法與 AI 應用」課程筆記中的四大科學測試方法

## 📖 專案簡介

本專案為成功大學資訊工程系李信杰教授「黑箱測試方法與 AI 應用」課程筆記的實戰範例，提供四種科學化黑箱測試方法的可執行程式碼與測試案例。

### 核心理念

- **用最少的測試案例**
- **抓出最大部分的 Bug**
- **從依賴經驗轉化為依賴邏輯與演算法**

## 🎯 四大測試方法

### 1️⃣ 等價類劃分 + 邊界值分析

**適用對象：** 單一輸入參數

**實作範例：**
- `age_validator.py` - 年齡驗證器（範圍 0-120）
- `amount_validator.py` - 金額驗證器（範圍 0-1000）

**測試重點：**
- 左邊界：-1, 0, 1
- 右邊界：119, 120, 121（或 999, 1000, 1001）
- 中間值與異常值

### 2️⃣ 組合測試（Pairwise Testing）

**適用對象：** 多輸入參數交互作用

**實作範例：**
- `browser_compatibility.py` - 瀏覽器相容性測試
- `pict_generator.py` - Pairwise 組合生成器

**效果展示：**
- 原始組合：5×7×2×3×2 = 420 種
- Pairwise 組合：約 30-50 種
- **縮減比例：90% 以上**

### 3️⃣ 決策表測試

**適用對象：** 複雜的商業規則

**實作範例：**
- `membership_discount.py` - 會員折扣計算（2³ = 8 種組合）
- `insurance_claim.py` - 保險理賠處理（2⁴ = 16 種組合）

**測試覆蓋：**
- 確保所有條件組合都被測試
- 完整性檢查（2ⁿ 個邏輯情境）

### 4️⃣ 狀態轉移測試

**適用對象：** 具有先後順序或狀態切換的系統

**實作範例：**
- `vending_machine.py` - 販賣機系統
- `media_player.py` - 媒體播放器

**測試目標：**
- 狀態覆蓋（State Coverage）
- 轉移覆蓋（Transition Coverage）
- 成對轉移覆蓋（Pair Transition Coverage）

## 🚀 快速開始

### 安裝依賴

```bash
make setup
```

### 執行測試

```bash
# 執行所有測試
make test

# 執行特定測試
make test-boundary    # 邊界值測試
make test-pairwise    # 組合測試
make test-decision    # 決策表測試
make test-state       # 狀態測試

# 詳細輸出
make test-verbose

# 生成覆蓋率報告
make coverage
```

## 📁 專案結構

```
black-box-testing-examples/
├── src/                          # 原始碼
│   ├── boundary_value/           # 邊界值分析
│   │   ├── age_validator.py
│   │   └── amount_validator.py
│   ├── pairwise/                 # 組合測試
│   │   ├── browser_compatibility.py
│   │   └── pict_generator.py
│   ├── decision_table/           # 決策表測試
│   │   ├── membership_discount.py
│   │   └── insurance_claim.py
│   └── state_transition/         # 狀態測試
│       ├── vending_machine.py
│       └── media_player.py
├── tests/                        # 測試檔案
│   ├── test_boundary_value.py
│   ├── test_pairwise.py
│   ├── test_decision_table.py
│   └── test_state_transition.py
├── Makefile                      # 建置與測試指令
├── requirements.txt              # Python 依賴
└── README.md                     # 專案說明
```

## 📊 測試結果摘要

| 測試方法 | 測試數量 | 通過率 | 說明 |
|---------|---------|--------|------|
| 邊界值分析 | 25 | 100% | 覆蓋左右邊界、中間值、異常值 |
| 組合測試 | 10 | 100% | 展示 420→50 的組合縮減 |
| 決策表測試 | 18 | 100% | 覆蓋 8 種會員折扣 + 16 種理賠情境 |
| 狀態轉移測試 | 22 | 100% | 100% 狀態與轉移覆蓋 |
| **總計** | **75** | **100%** | **所有測試通過** |

## 🛠️ 技術棧

- **Python 3.9+**
- **pytest** - 測試框架
- **allpairspy** - Pairwise 組合測試
- **transitions** - 狀態機實作

## 📚 參考資料

- 課程講師：成功大學資訊工程系 李信杰教授
- 課程筆記：`黑箱測試方法與AI應用_課程筆記.md`
- 工具推薦：
  - PICT（微軟開發的 Pairwise 測試工具）
  - Mermaid（圖表生成語法）

## 💡 學習要點

### 測試方法選擇

| 情境 | 推薦方法 |
|------|---------|
| 單參數輸入 | 邊界值分析 |
| 多參數交互 | Pairwise 組合測試 |
| 複雜規則 | 決策表測試 |
| 有流程順序 | 狀態測試 |

### 黃金法則

✅ 用**邏輯**取代**直覺**
✅ 用**演算法**取代**經驗**
✅ 用**最少案例**抓**最多 Bug**
✅ **AI 產出** + **人工審核** = 最佳組合

## 🔍 詳細文件

更詳細的測試方法說明請參閱：
- `docs/testing_methods_guide.md` - 測試方法詳細指南
- `黑箱測試方法與AI應用_課程筆記.md` - 完整課程筆記

## 📝 授權

本專案為教學範例，僅供學習參考使用。

---

**整理日期：** 2026-01-01
**課程來源：** 成功大學資訊工程系 李信杰教授
