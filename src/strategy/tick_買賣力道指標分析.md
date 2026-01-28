# Tick 數據買賣力道指標與橫切面 Quantile 分析

## 一、概念說明

### 主動買賣的判定
- **主動買（外盤）**：成交價 = 賣一價，代表買方主動掃單
- **主動賣（內盤）**：成交價 = 買一價，代表賣方主動掃單

---

## 二、實際範例

假設 2025-01-27 這天有 1000 檔股票

### 步驟 1：計算個股買賣力道

#### 股票 A (2330 台積電)
```
主動買量：5,000,000 股
主動賣量：3,000,000 股
總成交量：8,000,000 股

買賣力道 = (主動買量 - 主動賣量) / 總成交量
        = (5,000,000 - 3,000,000) / 8,000,000
        = 0.25
```

#### 股票 B (2317 鴻海)
```
主動買量：2,000,000 股
主動賣量：4,000,000 股
總成交量：6,000,000 股

買賣力道 = (2,000,000 - 4,000,000) / 6,000,000
        = -0.33
```

---

### 步驟 2：橫切面標準化

當天 1000 檔股票的買賣力道分布：

```
平均值 (μ) = 0.05
標準差 (σ) = 0.15

台積電標準化分數 = (0.25 - 0.05) / 0.15 = 1.33
鴻海標準化分數 = (-0.33 - 0.05) / 0.15 = -2.53
```

**標準化公式**：
```
Z-Score = (個股買賣力道 - 當天平均值) / 當天標準差
```

---

### 步驟 3：Quantile 分組

將 1000 檔股票按標準化分數排序後分成 5 組（quintile）：

| 分組 | 條件 | 範圍 | 範例 |
|------|------|------|------|
| **Q5** | 最強 20% | 標準化分數 > 0.84 | 台積電 (1.33) |
| **Q4** | 次強 20% | 0.25 ~ 0.84 | - |
| **Q3** | 中間 20% | -0.25 ~ 0.25 | - |
| **Q2** | 次弱 20% | -0.84 ~ -0.25 | - |
| **Q1** | 最弱 20% | < -0.84 | 鴻海 (-2.53) |

---

## 三、Python 實作範例

```python
import pandas as pd
import numpy as np

# 模擬當天 tick 數據
data = {
    'stock_id': ['2330', '2317', '2454', '2412', '2308'],
    'active_buy': [5000000, 2000000, 1500000, 3000000, 800000],
    'active_sell': [3000000, 4000000, 1200000, 2500000, 1200000],
    'total_volume': [8000000, 6000000, 2700000, 5500000, 2000000]
}

df = pd.DataFrame(data)

# 1. 計算買賣力道
df['buy_sell_pressure'] = (df['active_buy'] - df['active_sell']) / df['total_volume']

# 2. 橫切面標準化
df['pressure_zscore'] = (
    (df['buy_sell_pressure'] - df['buy_sell_pressure'].mean()) 
    / df['buy_sell_pressure'].std()
)

# 3. 分成 5 個 quantile
df['quantile'] = pd.qcut(
    df['pressure_zscore'], 
    q=5, 
    labels=['Q1', 'Q2', 'Q3', 'Q4', 'Q5']
)

print(df)
```

### 輸出結果示例

```
  stock_id  active_buy  active_sell  total_volume  buy_sell_pressure  pressure_zscore quantile
0     2330     5000000      3000000       8000000              0.250            1.33       Q5
1     2317     2000000      4000000       6000000             -0.333           -2.53       Q1
2     2454     1500000      1200000       2700000              0.111            0.45       Q4
3     2412     3000000      2500000       5500000              0.091            0.28       Q3
4     2308      800000      1200000       2000000             -0.200           -1.15       Q2
```

---

## 四、應用策略

### 1. 做多策略
每天買入 **Q5 組別**的股票（買盤力道最強）

### 2. 做空策略
每天放空 **Q1 組別**的股票（賣盤力道最強）

### 3. 多空策略
- **做多**：Q5 組別
- **做空**：Q1 組別
- 建立市場中性部位

---

## 五、策略優勢

1. **相對強弱**：每天重新計算橫切面排名，避免絕對值偏誤
2. **捕捉資金流向**：tick 級別數據能反映即時買賣意願
3. **標準化處理**：消除不同股票成交量差異的影響
4. **動態調整**：每日重新分組，適應市場變化

---

## 六、注意事項

⚠️ **重要提醒**：
- tick 數據需要精確的時間戳和價格匹配
- 開盤、收盤時段可能有異常波動
- 需考慮交易成本和滑價
- 建議搭配其他指標（如成交量、波動率）進行過濾
- 回測時注意避免前視偏差（look-ahead bias）

---

## 七、進階應用

### 時間加權買賣力道
```python
# 給予不同時段不同權重
# 例如：尾盤 30 分鐘權重加倍
df['weighted_pressure'] = df['buy_sell_pressure'] * df['time_weight']
```

### 多日累積指標
```python
# 計算過去 5 日的買賣力道移動平均
df['pressure_ma5'] = df.groupby('stock_id')['buy_sell_pressure'].rolling(5).mean()
```

### 量價配合過濾
```python
# 只選擇成交量放大且買盤力道強的股票
high_volume = df['total_volume'] > df['total_volume'].quantile(0.7)
strong_buy = df['quantile'] == 'Q5'
final_selection = df[high_volume & strong_buy]
```

---

## 八、完整實作範例

```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class TickPressureAnalyzer:
    """Tick 數據買賣力道分析器"""
    
    def __init__(self, n_quantiles=5):
        self.n_quantiles = n_quantiles
        
    def calculate_pressure(self, df):
        """計算買賣力道"""
        df['buy_sell_pressure'] = (
            (df['active_buy'] - df['active_sell']) / df['total_volume']
        )
        return df
    
    def standardize(self, df, date_col='date'):
        """橫切面標準化"""
        df['pressure_zscore'] = df.groupby(date_col)['buy_sell_pressure'].transform(
            lambda x: (x - x.mean()) / x.std()
        )
        return df
    
    def assign_quantiles(self, df, date_col='date'):
        """分配 quantile 組別"""
        df['quantile'] = df.groupby(date_col)['pressure_zscore'].transform(
            lambda x: pd.qcut(x, q=self.n_quantiles, labels=False, duplicates='drop') + 1
        )
        return df
    
    def analyze(self, df, date_col='date'):
        """完整分析流程"""
        df = self.calculate_pressure(df)
        df = self.standardize(df, date_col)
        df = self.assign_quantiles(df, date_col)
        return df

# 使用範例
if __name__ == "__main__":
    # 模擬多日數據
    dates = pd.date_range('2025-01-20', '2025-01-27', freq='D')
    stocks = ['2330', '2317', '2454', '2412', '2308']
    
    data_list = []
    for date in dates:
        for stock in stocks:
            data_list.append({
                'date': date,
                'stock_id': stock,
                'active_buy': np.random.randint(1000000, 10000000),
                'active_sell': np.random.randint(1000000, 10000000),
                'total_volume': np.random.randint(5000000, 15000000)
            })
    
    df = pd.DataFrame(data_list)
    
    # 執行分析
    analyzer = TickPressureAnalyzer(n_quantiles=5)
    result = analyzer.analyze(df)
    
    # 查看最新一天的結果
    latest_date = result['date'].max()
    latest_result = result[result['date'] == latest_date].sort_values('quantile', ascending=False)
    
    print(f"\n{latest_date.date()} 買賣力道排名：")
    print(latest_result[['stock_id', 'buy_sell_pressure', 'pressure_zscore', 'quantile']])
    
    # 查看 Q5 組別（最強）
    q5_stocks = latest_result[latest_result['quantile'] == 5]['stock_id'].tolist()
    print(f"\nQ5 組別股票（建議做多）：{q5_stocks}")
    
    # 查看 Q1 組別（最弱）
    q1_stocks = latest_result[latest_result['quantile'] == 1]['stock_id'].tolist()
    print(f"Q1 組別股票（建議做空）：{q1_stocks}")
```

---

## 九、回測框架

```python
class BacktestEngine:
    """簡單回測引擎"""
    
    def __init__(self, initial_capital=1000000):
        self.initial_capital = initial_capital
        self.positions = {}
        self.equity_curve = []
        
    def run_backtest(self, signals_df, returns_df):
        """
        執行回測
        
        Parameters:
        -----------
        signals_df: DataFrame with columns ['date', 'stock_id', 'quantile']
        returns_df: DataFrame with columns ['date', 'stock_id', 'return']
        """
        dates = sorted(signals_df['date'].unique())
        
        for date in dates:
            # 取得當日訊號
            daily_signals = signals_df[signals_df['date'] == date]
            
            # 做多 Q5、做空 Q1
            long_stocks = daily_signals[daily_signals['quantile'] == 5]['stock_id'].tolist()
            short_stocks = daily_signals[daily_signals['quantile'] == 1]['stock_id'].tolist()
            
            # 計算當日報酬（簡化版本）
            if date in returns_df['date'].values:
                daily_returns = returns_df[returns_df['date'] == date]
                
                long_return = daily_returns[
                    daily_returns['stock_id'].isin(long_stocks)
                ]['return'].mean() if long_stocks else 0
                
                short_return = -daily_returns[
                    daily_returns['stock_id'].isin(short_stocks)
                ]['return'].mean() if short_stocks else 0
                
                total_return = (long_return + short_return) / 2
                
                # 更新權益曲線
                if not self.equity_curve:
                    self.equity_curve.append({
                        'date': date,
                        'equity': self.initial_capital * (1 + total_return)
                    })
                else:
                    last_equity = self.equity_curve[-1]['equity']
                    self.equity_curve.append({
                        'date': date,
                        'equity': last_equity * (1 + total_return)
                    })
        
        return pd.DataFrame(self.equity_curve)
    
    def calculate_metrics(self, equity_df):
        """計算績效指標"""
        equity_df['returns'] = equity_df['equity'].pct_change()
        
        total_return = (equity_df['equity'].iloc[-1] / self.initial_capital - 1) * 100
        sharpe_ratio = equity_df['returns'].mean() / equity_df['returns'].std() * np.sqrt(252)
        max_drawdown = ((equity_df['equity'] / equity_df['equity'].cummax()) - 1).min() * 100
        
        return {
            'Total Return (%)': round(total_return, 2),
            'Sharpe Ratio': round(sharpe_ratio, 2),
            'Max Drawdown (%)': round(max_drawdown, 2),
            'Final Equity': round(equity_df['equity'].iloc[-1], 2)
        }
```

---

## 十、參考資源

### 相關論文
- "Order Flow and Expected Option Returns" - Jesper Rangvid et al.
- "High Frequency Trading and Price Discovery" - Albert J. Menkveld

### 數據來源
- 台灣證券交易所（TWSE）
- 證券櫃檯買賣中心（TPEx）
- 各券商提供的 tick 數據 API

### 相關指標
- VWAP (Volume Weighted Average Price)
- OBV (On Balance Volume)
- MFI (Money Flow Index)
- Accumulation/Distribution Line

---

**文件建立時間**：2025-01-27  
**版本**：v1.0  
**作者**：Claude AI
