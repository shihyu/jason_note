# MA 黃金交叉策略回測系統 - Agent Team 開發計畫

## 專案目標
建立一個 Agent Team 來開發 MA 黃金交叉策略回測系統

---

## 團隊成員與分工

### 成員1：後端工程師（核心，最先開始）
- **任務**：實做數據抓取、MA 指標計算和回測引擎
- **輸出檔案**：
  - `backend/data/fetcher.py` — 使用 yfinance 抓取股票歷史數據
  - `backend/indicators/ma.py` — MA 指標計算模組
  - `backend/backtest/engine.py` — 回測引擎核心
- **技術要求**：
  - 使用 `yfinance` 抓取真實股票數據（支援台股如 `2330.TW`、美股如 `AAPL`）
  - 純 Python 實作 MA 計算，不使用 TA-Lib
- **依賴**：無

---

### 成員2：API 工程師
- **任務**：實做 RESTful API 供前端使用
- **輸出檔案**：
  - `backend/api/routes.py` — API 路由定義
  - `backend/api/schemas.py` — Request/Response 格式
- **技術要求**：使用 Flask 框架實作 RESTful API，API 需支援傳入股票代碼、日期區間
- **依賴**：成員1 完成後開始（需 import 後端模組）

---

### 成員3：前端工程師
- **任務**：實做前端介面顯示回測結果
- **輸出檔案**：
  - `frontend/index.html` — 前端頁面（HTML + CSS + JS）
- **技術要求**：使用 Chart.js 畫 K 線和 MA 線，標記黃金交叉點
- **依賴**：UI 開發可與成員1 並行（使用 mock data），API 串接需等成員2 完成

---

### 成員4：測試工程師
- **任務**：實做單元測試和整合測試
- **輸出檔案**：
  - `backend/tests/test_ma.py` — MA 指標計算測試
  - `backend/tests/test_backtest.py` — 回測引擎測試
  - `backend/tests/test_api.py` — API 路由測試
  - `backend/tests/test_fetcher.py` — 數據抓取測試
  - `backend/tests/sample_data.csv` — 測試用範例 K 線數據（離線備用）
- **技術要求**：
  - 使用 pytest 框架
  - 用已驗證的數據確保正確性
- **依賴**：成員1 完成後開始單元測試，成員2 完成後開始 API 測試

---

## 策略參數定義

| 參數 | 設定值 | 說明 |
|------|--------|------|
| 短期 MA | 5 日 | 快速均線 |
| 長期 MA | 20 日 | 慢速均線 |
| 黃金交叉 | 短期 MA 上穿長期 MA | 買入訊號 |
| 死亡交叉 | 短期 MA 下穿長期 MA | 賣出訊號 |

---

## 數據來源

使用 `yfinance` 套件抓取真實股票歷史數據：

```python
import yfinance as yf

# 台股範例
df = yf.download("2330.TW", start="2024-01-01", end="2024-12-31")

# 美股範例
df = yf.download("AAPL", start="2024-01-01", end="2024-12-31")
```

### `backend/data/fetcher.py` 介面規格

```python
def fetch_stock_data(symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    抓取股票歷史 K 線數據

    Args:
        symbol: 股票代碼（如 "2330.TW", "AAPL"）
        start: 開始日期（如 "2024-01-01"）
        end: 結束日期（如 "2024-12-31"）

    Returns:
        DataFrame with columns: date, open, high, low, close, volume
    """
```

---

## 數據格式

### K 線數據（DataFrame）
```
date,open,high,low,close,volume
2024-01-02,595.0,600.0,590.0,598.0,25000000
...
```

### 輸出：回測結果
```json
{
  "total_trades": 10,
  "win_rate": 0.6,
  "total_profit": 1500.0,
  "max_drawdown": 200.0,
  "trades": [
    {
      "entry_date": "2024-01-05",
      "entry_price": 101.0,
      "exit_date": "2024-01-10",
      "exit_price": 105.0,
      "profit": 400.0,
      "type": "golden_cross"
    }
  ]
}
```

---

## 任務依賴關係圖

```
成員1 (後端) ──┬──> 成員2 (API) ──┬──> 成員3 (前端串接)
               │                  │
               ├──> 成員3 (前端UI) │    [並行開發 mock]
               │                  │
               └──> 成員4 (單元測試) ──> 成員4 (API 測試)
```

| 成員 | 依賴 | 說明 |
|------|-------|------|
| 成員1 | 無 | 最先開始，核心模組 |
| 成員2 | 成員1 | 等後端模組完成 |
| 成員3 | 成員2（API 串接） | UI 可並行開發，串接需等 API 完成 |
| 成員4 | 成員1 + 成員2 | 單元測試等成員1，API 測試等成員2 |

---

## 執行模式

- **Lead**：負責任務分配、協調、進度追蹤
- **Teamate**：負責實際程式碼實作，完成後回報進度並協助解決問題
- 每個成員完成任務後通知 Lead
- **Bug 修復原則**：測試工程師（成員4）發現問題後回報 Lead，由 Lead 指派回原模組負責人修復，修復後由成員4 重新驗證
- **Skill 使用原則**：開發過程中若有可用的 skill 適用於當前任務（如 TDD、code review、debugging、brainstorming 等），必須優先使用對應的 skill 來執行，以確保開發品質與流程一致性

---

## 驗收標準

1. 可透過 yfinance 抓取真實股票數據（台股 `2330.TW`、美股 `AAPL` 皆可運行）
2. MA 計算正確（5日、20日均線與預期一致）
3. 黃金交叉/死亡交叉判斷正確
4. 回測引擎輸出格式符合規格
5. API 可正常呼叫並返回正確資料（支援傳入股票代碼與日期區間）
6. 前端可顯示 K 線、MA 線及交叉點標記
7. 所有測試通過
8. 端對端可運行：輸入股票代碼 → 抓取數據 → 計算 MA → 回測 → 前端顯示結果
