# MA 黃金交叉策略回測系統 - 後端實作計畫

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 實作 MA 黃金交叉策略回測系統的後端核心模組（數據抓取、MA 計算、回測引擎）

**Architecture:**
- `fetcher.py`: 使用 yfinance 下載股票歷史數據，回傳標準化 DataFrame
- `ma.py`: 純 Python 計算 5 日、20 日 MA，判斷黃金交叉/死亡交叉訊號
- `engine.py`: 根據 MA 交叉訊號執行回測，計算交易結果和統計數據

**Tech Stack:** Python 3, pandas, yfinance

---

## Task 1: 實作 `backend/data/fetcher.py`

**Files:**
- Create: `backend/data/fetcher.py`
- Test: `backend/tests/test_fetcher.py`

- [ ] **Step 1: 建立測試檔並寫入測試案例**

```python
# backend/tests/test_fetcher.py
import pytest
from datetime import datetime
import pandas as pd
from backend.data.fetcher import fetch_stock_data

def test_fetch_stock_data_columns():
    """驗證回傳 DataFrame 包含必要欄位"""
    # 使用真實 yfinance 測試
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-31")
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(df) > 0

def test_fetch_stock_data_types():
    """驗證欄位型別正確"""
    df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-31")
    assert pd.api.types.is_datetime64_any_dtype(df["date"])
    assert pd.api.types.is_float_dtype(df["close"])

def test_fetch_taiwan_stock():
    """驗證台股抓取（2330.TW）"""
    df = fetch_stock_data("2330.TW", "2024-01-01", "2024-01-31")
    assert len(df) > 0
    assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_fetcher.py -v`
Expected: FAIL with "No module named 'backend'"

- [ ] **Step 3: 建立 `backend/data/__init__.py`**

```python
# backend/data/__init__.py
```

- [ ] **Step 4: Write minimal fetcher implementation**

```python
# backend/data/fetcher.py
import yfinance as yf
import pandas as pd
from datetime import datetime

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
    df = yf.download(symbol, start=start, end=end, progress=False)

    # 重設索引，將 date 變成欄位
    df = df.reset_index()

    # yfinance 回傳的欄位可能是 MultiIndex，扁平化處理
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if col[1] == '' or col[1] == symbol else col[0] for col in df.columns]

    # 確保 date 欄位是 datetime 格式
    if "Date" in df.columns:
        df = df.rename(columns={"Date": "date"})
    df["date"] = pd.to_datetime(df["date"])

    # 選取必要欄位並確保順序
    df = df[["date", "Open", "High", "Low", "Close", "Volume"]]
    df.columns = ["date", "open", "high", "low", "close", "volume"]

    return df
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_fetcher.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /home/shihyu/github/jason_note/src/ai_agent
git add backend/data/__init__.py backend/data/fetcher.py backend/tests/test_fetcher.py
git commit -m "feat: add stock data fetcher using yfinance"
```

---

## Task 2: 實作 `backend/indicators/ma.py`

**Files:**
- Create: `backend/indicators/ma.py`
- Test: `backend/tests/test_ma.py`

- [ ] **Step 1: 建立測試檔並寫入測試案例**

```python
# backend/tests/test_ma.py
import pytest
import pandas as pd
import numpy as np
from backend.indicators.ma import calculate_ma, detect_crossover

# 測試用資料
def create_test_data():
    """建立測試用 K 線數據"""
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    return pd.DataFrame({
        "date": dates,
        "open": range(100, 130),
        "high": range(102, 132),
        "low": range(98, 128),
        "close": range(101, 131),
        "volume": [1000000] * 30
    })

def test_calculate_ma_short():
    """驗證 5 日 MA 計算"""
    df = create_test_data()
    result = calculate_ma(df, short_window=5, long_window=20)

    # 前 4 列應該是 NaN（第 5 列才會有值）
    assert pd.isna(result["ma_short"].iloc[0])
    assert pd.isna(result["ma_short"].iloc[3])
    # 第 5 列開始有值
    assert not pd.isna(result["ma_short"].iloc[4])
    # 驗證計算：前 5 筆 close 的平均值 = (101+102+103+104+105)/5 = 103.0
    assert result["ma_short"].iloc[4] == pytest.approx(103.0)

def test_calculate_ma_long():
    """驗證 20 日 MA 計算"""
    df = create_test_data()
    result = calculate_ma(df, short_window=5, long_window=20)

    # 前 19 列應該是 NaN
    assert pd.isna(result["ma_long"].iloc[0])
    assert pd.isna(result["ma_long"].iloc[18])
    assert not pd.isna(result["ma_long"].iloc[19])

def test_detect_golden_cross():
    """驗證黃金交叉偵測（短期 MA 上穿長期 MA）"""
    # 建立一個股價先下跌後上漲的測試數據
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    # close: [100, 95, 90, 85, 80, 85, 90, 95, 100, 105]
    # MA5: 會在第 5 天後低於 MA20，然後在第 6-7 天交叉
    closes = [100, 95, 90, 85, 80, 85, 90, 95, 100, 105]
    df = pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1000000] * 10
    })

    result = calculate_ma(df, short_window=3, long_window=5)
    crossovers = detect_crossover(result)

    # 應該偵測到 1 次黃金交叉
    golden_crosses = [c for c in crossovers if c["type"] == "golden_cross"]
    assert len(golden_crosses) >= 1

def test_detect_death_cross():
    """驗證死亡交叉偵測（短期 MA 下穿長期 MA）"""
    # 建立一個股價先上漲後下跌的測試數據
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    # close: [80, 85, 90, 95, 100, 95, 90, 85, 80, 75]
    closes = [80, 85, 90, 95, 100, 95, 90, 85, 80, 75]
    df = pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "volume": [1000000] * 10
    })

    result = calculate_ma(df, short_window=3, long_window=5)
    crossovers = detect_crossover(result)

    # 應該偵測到 1 次死亡交叉
    death_crosses = [c for c in crossovers if c["type"] == "death_cross"]
    assert len(death_crosses) >= 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_ma.py -v`
Expected: FAIL with "No module named 'backend'"

- [ ] **Step 3: 建立 `backend/indicators/__init__.py`**

```python
# backend/indicators/__init__.py
```

- [ ] **Step 4: Write minimal MA implementation**

```python
# backend/indicators/ma.py
import pandas as pd
from typing import List, Dict

def calculate_ma(df: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> pd.DataFrame:
    """
    計算移動平均線

    Args:
        df: K 線數據 DataFrame，需包含 close 欄位
        short_window: 短期 MA 窗口（預設 5 日）
        long_window: 長期 MA 窗口（預設 20 日）

    Returns:
        帶有 ma_short 和 ma_long 欄位的 DataFrame
    """
    result = df.copy()
    result["ma_short"] = df["close"].rolling(window=short_window).mean()
    result["ma_long"] = df["close"].rolling(window=long_window).mean()
    return result


def detect_crossover(df: pd.DataFrame) -> List[Dict]:
    """
    偵測 MA 交叉點

    Args:
        df: 已計算 MA 的 DataFrame，需包含 ma_short, ma_long, close, date 欄位

    Returns:
        List of crossover events, each with:
        - date: 交叉日期
        - type: "golden_cross" or "death_cross"
        - price: 當時股價
    """
    crossovers = []
    df = df.dropna()  # 移除 NaN 列

    for i in range(1, len(df)):
        prev = df.iloc[i - 1]
        curr = df.iloc[i]

        # 黃金交叉：短期 MA 從下方穿越到上方
        if prev["ma_short"] <= prev["ma_long"] and curr["ma_short"] > curr["ma_long"]:
            crossovers.append({
                "date": curr["date"],
                "type": "golden_cross",
                "price": curr["close"]
            })

        # 死亡交叉：短期 MA 從上方穿越到下方
        elif prev["ma_short"] >= prev["ma_long"] and curr["ma_short"] < curr["ma_long"]:
            crossovers.append({
                "date": curr["date"],
                "type": "death_cross",
                "price": curr["close"]
            })

    return crossovers
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_ma.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /home/shihyu/github/jason_note/src/ai_agent
git add backend/indicators/__init__.py backend/indicators/ma.py backend/tests/test_ma.py
git commit -m "feat: add MA indicator calculation module"
```

---

## Task 3: 實作 `backend/backtest/engine.py`

**Files:**
- Create: `backend/backtest/engine.py`
- Test: `backend/tests/test_backtest.py`

- [ ] **Step 1: 建立測試檔並寫入測試案例**

```python
# backend/tests/test_backtest.py
import pytest
import pandas as pd
from backend.backtest.engine import BacktestEngine, run_backtest

def create_test_data_with_signals():
    """建立帶有明確交叉訊號的測試數據"""
    dates = pd.date_range("2024-01-01", periods=25, freq="D")
    # 故意設計：
    # - 前 20 天：MA5 < MA20（無交叉）
    # - 第 21 天：黃金交叉（MA5 上穿 MA20）
    # - 第 22-25 天：持續上漲
    closes = [100] * 20 + [105, 110, 115, 120, 125]
    return pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1000000] * 25
    })

def test_backtest_engine_initialization():
    """驗證 BacktestEngine 初始化"""
    engine = BacktestEngine(initial_cash=1000000)
    assert engine.initial_cash == 1000000
    assert engine.position == 0
    assert len(engine.trades) == 0

def test_backtest_engine_buy_signal():
    """驗證買入訊號處理"""
    engine = BacktestEngine(initial_cash=100000)

    # 模擬買入
    engine.buy("2024-01-01", 100.0, 1000)  # 買入 1000 股，價格 100
    assert engine.position == 1000
    assert engine.cash == 0  # 100000 - 100*1000 = 0

def test_backtest_engine_sell_signal():
    """驗證賣出訊號處理"""
    engine = BacktestEngine(initial_cash=100000)

    # 先買入
    engine.buy("2024-01-01", 100.0, 1000)
    # 再賣出
    engine.sell("2024-01-10", 110.0, 1000)  # 價格上漲
    assert engine.position == 0
    # 獲利：1000 * (110 - 100) = 10000
    assert engine.cash == 100000 + 10000

def test_run_backtest_with_golden_cross():
    """驗證完整回測流程（黃金交叉進場、死亡交叉出場）"""
    # 建立明確的黃金交叉和死亡交叉數據
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    # 設計：
    # - 前期：MA5 < MA20，股價 100
    # - 第 15 天：黃金交叉，股價 100 -> 105
    # - 之後：持續上漲到 120
    # - 第 25 天：死亡交叉，股價 120 -> 115
    closes = [100] * 15 + [105, 110, 115, 120, 125, 120, 115, 110, 105, 100]

    df = pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1000000] * 30
    })

    result = run_backtest(df, short_window=5, long_window=10)

    assert "total_trades" in result
    assert "win_rate" in result
    assert "total_profit" in result
    assert "max_drawdown" in result
    assert "trades" in result
    # 應該有交易記錄
    assert result["total_trades"] >= 1

def test_backtest_result_format():
    """驗證回測結果格式"""
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    closes = [100] * 15 + [105, 110, 115, 120, 125, 120, 115, 110, 105, 100]
    df = pd.DataFrame({
        "date": dates,
        "open": closes,
        "high": closes,
        "low": closes,
        "close": closes,
        "volume": [1000000] * 30
    })

    result = run_backtest(df, short_window=5, long_window=10)

    # 驗證交易格式
    for trade in result["trades"]:
        assert "entry_date" in trade
        assert "entry_price" in trade
        assert "exit_date" in trade
        assert "exit_price" in trade
        assert "profit" in trade
        assert "type" in trade
        assert trade["type"] in ["golden_cross", "death_cross"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_backtest.py -v`
Expected: FAIL with "No module named 'backend'"

- [ ] **Step 3: 建立 `backend/backtest/__init__.py`**

```python
# backend/backtest/__init__.py
```

- [ ] **Step 4: Write minimal backtest engine implementation**

```python
# backend/backtest/engine.py
import pandas as pd
from typing import List, Dict
from backend.indicators.ma import calculate_ma, detect_crossover

class BacktestEngine:
    """回測引擎"""

    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0  # 持仓股數
        self.trades: List[Dict] = []
        self.current_entry = None

    def buy(self, date, price: float, shares: int):
        """買入股票"""
        cost = price * shares
        if cost > self.cash:
            # 資金不足，全額買入
            shares = int(self.cash / price)
            cost = price * shares

        if shares > 0:
            self.cash -= cost
            self.position += shares
            self.current_entry = {
                "entry_date": date,
                "entry_price": price,
                "shares": shares
            }

    def sell(self, date, price: float, shares: int = None):
        """賣出股票"""
        if shares is None:
            shares = self.position

        shares = min(shares, self.position)
        if shares > 0 and self.current_entry:
            revenue = price * shares
            self.cash += revenue
            self.position -= shares

            # 記錄交易
            profit = (price - self.current_entry["entry_price"]) * shares
            self.trades.append({
                "entry_date": str(self.current_entry["entry_date"].date()) if hasattr(self.current_entry["entry_date"], 'date') else str(self.current_entry["entry_date"]),
                "entry_price": self.current_entry["entry_price"],
                "exit_date": str(date.date()) if hasattr(date, 'date') else str(date),
                "exit_price": price,
                "profit": profit,
                "type": "golden_cross"  # 預設，實際由 run_backtest 設定
            })
            self.current_entry = None

    def get_stats(self) -> Dict:
        """計算統計數據"""
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "max_drawdown": 0.0,
                "trades": []
            }

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t["profit"] > 0]
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_profit = sum(t["profit"] for t in self.trades)

        # 計算最大回撤
        cumulative_profit = 0
        peak = 0
        max_drawdown = 0
        for trade in self.trades:
            cumulative_profit += trade["profit"]
            peak = max(peak, cumulative_profit)
            drawdown = peak - cumulative_profit
            max_drawdown = max(max_drawdown, drawdown)

        return {
            "total_trades": total_trades,
            "win_rate": round(win_rate, 2),
            "total_profit": round(total_profit, 2),
            "max_drawdown": round(max_drawdown, 2),
            "trades": self.trades
        }


def run_backtest(df: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> Dict:
    """
    執行回測

    Args:
        df: K 線數據 DataFrame
        short_window: 短期 MA 窗口（預設 5 日）
        long_window: 長期 MA 窗口（預設 20 日）

    Returns:
        回測結果 Dict
    """
    # 計算 MA
    df_with_ma = calculate_ma(df, short_window=short_window, long_window=long_window)

    # 偵測交叉點
    crossovers = detect_crossover(df_with_ma)

    # 初始化回測引擎
    engine = BacktestEngine()

    # 遍歷交叉點，執行交易
    for crossover in crossovers:
        if crossover["type"] == "golden_cross":
            # 黃金交叉：買入
            engine.buy(crossover["date"], crossover["price"], shares=1000)  # 固定買入 1000 股
        else:
            # 死亡交叉：賣出
            engine.sell(crossover["date"], crossover["price"])

    # 確保最後持仓賣出
    if engine.position > 0 and engine.current_entry:
        last_date = df_with_ma.iloc[-1]["date"]
        last_price = df_with_ma.iloc[-1]["close"]
        engine.sell(last_date, last_price)

    # 設定交易類型
    for crossover, trade in zip(crossovers, engine.trades):
        trade["type"] = crossover["type"]

    return engine.get_stats()
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/test_backtest.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
cd /home/shihyu/github/jason_note/src/ai_agent
git add backend/backtest/__init__.py backend/backtest/engine.py backend/tests/test_backtest.py
git commit -m "feat: add backtest engine with MA crossover strategy"
```

---

## 驗證：整合測試

- [ ] **Step 1: 執行所有測試**

Run: `cd /home/shihyu/github/jason_note/src/ai_agent && python -m pytest backend/tests/ -v`

- [ ] **Step 2: 端到端測試（使用真實數據）**

```python
# 建立 e2e_test.py
import sys
sys.path.insert(0, ".")
from backend.data.fetcher import fetch_stock_data
from backend.indicators.ma import calculate_ma, detect_crossover
from backend.backtest.engine import run_backtest
import json

# 抓取 AAPL 數據
df = fetch_stock_data("AAPL", "2024-01-01", "2024-06-30")
print(f"Fetched {len(df)} rows for AAPL")

# 計算 MA 並偵測交叉
df_ma = calculate_ma(df)
crossovers = detect_crossover(df_ma)
print(f"Found {len(crossovers)} crossovers")

# 執行回測
result = run_backtest(df)
print(json.dumps(result, indent=2))
```

---

## 預期輸出格式

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
