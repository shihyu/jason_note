
# FinLab 菲比斯配對交易實作指南

## 一、資料取得對照表

### 菲比斯原始指標 → FinLab對應資料

| 菲比斯指標 | FinLab資料源 | 程式碼 |
|------------|-------------|--------|
| 當月營收 | 月營收資料 | data.get('monthly_revenue:當月營收') |
| 毛利率 | 基本面特徵 | data.get('fundamental_features:營業毛利率') |
| 營業利益率 | 基本面特徵 | data.get('fundamental_features:營業利益率') |
| 本益比 | 價格指標 | data.get('price_earning_ratio:本益比') |
| 股價淨值比 | 價格指標 | data.get('price_earning_ratio:股價淨值比') |
| 外資買賣超 | 籌碼資料 | data.get('institutional_investors:外資買賣超') |

## 二、實作步驟詳解

### Step 1: 基本面選股實作
```python
# 1. 營收成長篩選
revenue = data.get('monthly_revenue:當月營收')
revenue_yoy = revenue / revenue.shift(12)  # 年增率
revenue_growth = revenue_yoy > 1.05  # 成長5%以上

# 2. 獲利能力改善
gross_margin = data.get('fundamental_features:營業毛利率')
margin_improve = gross_margin > gross_margin.shift(4)  # 季度改善

# 3. 估值合理性
pe = data.get('price_earning_ratio:本益比')
reasonable_pe = (pe > 0) & (pe < 15)  # 本益比在0-15倍之間
```

### Step 2: 質化分析替代方案
```python
# 由於FinLab無法直接取得新聞和法人報告，使用以下替代：

# 1. 股價動能替代新聞面
close = data.get('price:收盤價')
price_momentum = close > close.average(20)

# 2. 成交量異常替代市場關注度
volume = data.get('price:成交量')
volume_surge = volume > volume.average(20) * 1.5

# 3. 法人買賣超資料（如果可取得）
foreign_buy = data.get('institutional_investors:外資買賣超')
foreign_support = foreign_buy.rolling(3).sum() > 0
```

### Step 3: 配對交易部位建構
```python
# 多頭組合
long_condition = revenue_growth & margin_improve & reasonable_pe & price_momentum
long_position = long_condition.astype(float)
long_position = long_position.div(long_position.sum(axis=1), axis=0) * 0.7

# 空頭組合  
short_condition = (revenue_yoy < 0.95) | (pe > 25) | (close < close.average(60))
short_position = short_condition.astype(float)
short_position = short_position.div(short_position.sum(axis=1), axis=0) * 0.3

# 總部位
total_position = long_position - short_position
```

### Step 4: 回測執行
```python
from finlab.backtest import sim

report = sim(
    position=total_position,
    resample='M',  # 月度調整
    stop_loss=0.15,  # 15%停損
    position_limit=0.1,  # 單一標的上限10%
    name="菲比斯配對交易",
    upload=False
)
```

## 三、FinLab平台限制與解決方案

### 限制1: 無法取得即時新聞資訊
**解決方案：**
- 使用股價動能指標替代
- 利用成交量異常作為市場關注度指標
- 結合技術分析判斷市場情緒

### 限制2: 外資買賣超資料可能延遲
**解決方案：**
- 使用成交量放大作為資金動向指標
- 結合股價相對強勢指標
- 使用融資融券餘額變化

### 限制3: 產業報價資訊缺乏
**解決方案：**
- 使用同產業股票相對表現
- 利用ETF走勢作為產業趨勢指標
- 結合總經數據判斷產業景氣

### 限制4: 回測數據品質
**解決方案：**
- 加入流動性篩選避免不可交易股票
- 使用adjusted price避免股價異常
- 設定reasonable position limits

## 四、策略優化建議

### 1. 多因子評分系統
```python
def create_quality_score():
    # 營收評分
    rev_score = (revenue_yoy - 1) * 100

    # 獲利評分  
    margin_score = gross_margin.rank(pct=True)

    # 估值評分
    valuation_score = (1/pe).rank(pct=True)

    # 綜合評分
    total_score = (rev_score + margin_score + valuation_score) / 3
    return total_score
```

### 2. 動態權重調整
```python
def dynamic_weight_allocation():
    market_trend = close.average(5) / close.average(20)  # 市場趨勢

    # 多頭市場增加多頭權重
    long_weight = 0.7 + (market_trend - 1) * 0.5
    short_weight = 1 - long_weight

    return long_weight, short_weight
```

### 3. 風險控制強化
```python
def enhanced_risk_control():
    # 波動度調整
    volatility = close.pct_change().rolling(20).std()
    vol_adj_position = position / volatility

    # 相關性檢查
    correlation_limit = 0.7  # 避免持股過度相關

    return vol_adj_position
```

## 五、回測驗證要點

### 1. 流動性檢測
```python
# 確保可實際交易
liquidity_filter = (close * volume).average(60) > 1e7
final_position = position * liquidity_filter
```

### 2. 交易成本考量
```python
# 設定合理的交易成本
report = sim(
    position=final_position,
    fee_ratio=0.001425,  # 手續費
    tax_ratio=0.003,     # 證交稅
)
```

### 3. 回測期間選擇
```python
# 包含不同市場環境
backtest_period = slice('2008-01-01', None)  # 包含金融海嘯後
position_filtered = position.loc[backtest_period]
```

## 六、實戰部署注意事項

### 1. 資料更新頻率
- 月營收：每月10日後更新
- 財報資料：季度更新，有延遲
- 股價資料：每日更新

### 2. 執行時機
- 建議在盤後執行策略
- 月底進行部位調整
- 財報公佈期密切關注

### 3. 監控指標
- 策略勝率變化
- 最大回撤控制
- 個股權重分散度
- 多空比例平衡

## 七、進階功能開發

### 1. 機器學習整合
```python
from sklearn.ensemble import RandomForestRegressor

def ml_enhanced_selection():
    # 使用機器學習優化選股
    features = pd.concat([revenue_yoy, gross_margin, pe], axis=1)
    model = RandomForestRegressor()
    # ... 模型訓練與預測
```

### 2. 動態再平衡
```python
def dynamic_rebalancing():
    # 根據市場狀況調整再平衡頻率
    market_volatility = close.pct_change().rolling(20).std().mean()

    if market_volatility > 0.02:  # 高波動期
        rebalance_freq = 'W'  # 週度調整
    else:
        rebalance_freq = 'M'  # 月度調整

    return rebalance_freq
```

這份指南提供了完整的實作框架，投資人可以根據自己的需求進行調整和優化。
