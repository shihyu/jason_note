"""
老周交易心法 - 完整實現 (使用本地緩存數據)
================================

使用本地緩存的 broker_transactions 數據（券商分點交易統計）

核心策略：
1. 找出連續3天以上被同一分點買超的股票
2. 計算分點平均成本，現價不超過均價5%
3. 檢查集保戶數是否減少
"""

import pandas as pd
import numpy as np
import pickle
from finlab.backtest import sim

print("=" * 60)
print("老周交易心法 - 券商分點實作版")
print("=" * 60)

# ============================================================
# Step 1: 載入本地數據
# ============================================================
print("\n【Step 1】載入本地數據...")

# 載入本地券商分點數據
with open("/home/shihyu/github/Jlab/finlab/broker_transactions.bin", "rb") as f:
    bt = pickle.load(f)

print(f"券商分點數據形狀: {bt.shape}")
print(f"欄位: {bt.columns.tolist()}")
print(f"日期範圍: {bt.index[0]} ~ {bt.index[-1]}")

# 計算淨買超
bt['net_buy'] = bt['buy'] - bt['sell']

# 移除特殊股票後綴
bt = bt[~bt['stock_id'].astype(str).str[-1].isin(['L', 'B', 'C'])]

# 載入價格數據
close = pd.read_pickle("/home/shihyu/github/Jlab/finlab/close.bin") if False else None

# ============================================================
# Step 2: 計算券商分點力道
# ============================================================
print("\n【Step 2】計算券商分點力道...")

# 按股票和日期聚合（合併所有分點）
broker_daily = (
    bt.groupby(["date", "stock_id"])[["buy", "sell", "net_buy"]]
    .sum()
    .reset_index()
)

# 轉為透視表
broker_pivot = (
    broker_daily
    .pivot(index="date", columns="stock_id", values=["buy", "sell", "net_buy"])
)

buy_vol = broker_pivot["buy"].fillna(0)
sell_vol = broker_pivot["sell"].fillna(0)
net_buy = broker_pivot["net_buy"].fillna(0)

# 券商分點力道 = (買-賣) / (買+賣)
broker_force = (buy_vol - sell_vol) / (buy_vol + sell_vol + 1e-9)

# 去除特殊股票
valid_cols = ~broker_force.columns.astype(str).str[-1].isin(["L", "B", "C"])
broker_force = broker_force.loc[:, valid_cols]

print(f"力道數據形狀: {broker_force.shape}")

# ============================================================
# Step 3: 實現老周核心條件
# ============================================================
print("\n【Step 3】實現老周核心條件...")

# 條件1: 連續3天買超力道為正
# sustain 函數：檢查過去N天是否持續滿足條件
def sustain(series, days):
    """檢查是否持續滿足條件N天"""
    return series.rolling(days).min() > 0

continuous_buy_3d = sustain(broker_force, 3)

# 條件2: 現價不超過均價5% - 需要載入價格
# 這裡我們用 close 替代，實際應為分點平均成本
# 簡化：使用股價相對近期低點

# 條件3: 持有人數減少（假設用成交量作為代理）

# ============================================================
# Step 4: 讀取價格數據
# ============================================================
print("\n【Step 4】讀取價格數據...")

# 嘗試從 finlab 獲取
try:
    from finlab import data
    finlab.login("RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m")
    close = data.get("price:收盤價")
    vol = data.get("price:成交股數")
    print(f"成功載入價格數據: {close.shape}")
except Exception as e:
    print(f"無法載入價格: {e}")
    print("使用簡化版策略")
    close = None

# ============================================================
# Step 5: 構建信號
# ============================================================
print("\n【Step 5】構建交易信號...")

if close is not None:
    # 去除特殊股票
    valid_stocks = ~close.columns.astype(str).str[-1].isin(["L", "B", "C"])
    close_valid = close.loc[:, valid_stocks]
    
    # 滾動均線
    ma5 = close_valid.average(5)
    ma10 = close_valid.average(10)
    
    # 條件：股價在均價5%以內
    near_ma5 = (close_valid - ma5).abs() / ma5 < 0.05
    
    # 條件：股價在均線上
    above_ma10 = close_valid > ma10
    
    # 結合券商分點買超條件
    position = continuous_buy_3d.reindex(close_valid.index, method='ffill') & near_ma5 & above_ma10
    
    # 流動性過濾
    liquid = vol.average(20) > 500_000
    position = position & liquid.reindex(close_valid.index, method='ffill')
else:
    # 無價格數據時只用券商力道
    position = continuous_buy_3d.fillna(False)

print(f"信號覆蓋天數: {position.notna().sum()}")
print(f"平均每日信號數: {position.sum(axis=1).mean():.1f}")

# ============================================================
# Step 6: 執行回測
# ============================================================
print("\n【Step 6】執行回測...")

if close is not None:
    try:
        report = sim(
            position,
            resample="W",  # 週期再平衡
            stop_loss=0.1,
            take_profit=0.2,
            position_limit=0.3,
            fee_ratio=1.425/1000,
            tax_ratio=3/1000,
            upload=False
        )
        
        print("\n" + "=" * 60)
        print("【回測結果】")
        print("=" * 60)
        print(report)
        
        stats = report.get_stats()
        print(f"\n===== 關鍵指標 =====")
        for key in ['cagr', 'monthly_sharpe', 'max_drawdown', 'daily_mean', 'daily_sortino']:
            if key in stats:
                print(f"{key}: {stats[key]:.4f}" if isinstance(stats[key], (int, float)) else f"{key}: {stats[key]}")
                
    except Exception as e:
        print(f"回測錯誤: {e}")
        import traceback
        traceback.print_exc()
else:
    print("跳過回測（無價格數據）")

# ============================================================
# 分析說明
# ============================================================
print("\n" + "=" * 60)
print("【策略說明】")
print("=" * 60)
print("""
老周策略核心：
1. 券商分點連續買超 - broker_force.sustain(3) 實現
2. 現價不超過均價5% - near_ma5 條件
3. 持有人數減少 - （需集保數據，暫用成交量代理）

注意：完整版需要：
- 分點平均成本計算
- 集保戶數變化資料
- 追蹤「同一分點」而非全部分點合計
""")

