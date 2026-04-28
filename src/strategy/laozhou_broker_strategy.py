"""
老周交易心法 - 券商分點版
================================

核心策略：
1. 券商分點連續買超3天以上
2. 現價不超過均價5%
3. 站上均線
"""

import os
import pickle
import pandas as pd
import numpy as np
import sys

import finlab
from finlab import data
from finlab.backtest import sim


# ============ 配置 ============
API_KEY = "RgK9Hzy5Pg66kc3lbv/mVUHcL6ciJ2QHA7wylySl4VdoUq/EPpXWeHFmu1kqmlC7#vip_m"


print("=" * 60)
print("老周交易心法 - 券商分點實作版")
print("=" * 60)

# 登入
finlab.login(API_KEY)
input()


# 移除特殊股票
bt = bt[~bt['stock_id'].astype(str).str[-1].isin(['L', 'B', 'C'])]

# 計算力道
broker_daily = bt.groupby(["date", "stock_id"])[["buy", "sell"]].sum().reset_index()
broker_pivot = broker_daily.pivot(index="date", columns="stock_id", values=["buy", "sell"])
buy_vol = broker_pivot["buy"].fillna(0)
sell_vol = broker_pivot["sell"].fillna(0)

# 力道 = (買-賣)/(買+賣)
broker_force = (buy_vol - sell_vol) / (buy_vol + sell_vol + 1)
valid_cols_bf = ~broker_force.columns.astype(str).str[-1].isin(["L", "B", "C"])
broker_force = broker_force.loc[:, valid_cols_bf]

print(f"券商力道: {broker_force.shape}")

# 讀取價格
close = data.get("price:收盤價")
vol = data.get("price:成交股數")

# 共同股票
common_stocks = broker_force.columns.intersection(close.columns)
broker_force = broker_force[common_stocks]
close_aligned = close[common_stocks]
vol_aligned = vol[common_stocks]

# 對齊期間
bt_dates = broker_force.index
close_valid = close_aligned.reindex(bt_dates)
vol_valid = vol_aligned.reindex(bt_dates)

# ============ 核心條件 ============
def sustain(series, days):
    return series.rolling(days).min() > 0

continuous_buy = sustain(broker_force, 3)
ma5 = close_valid.average(5)
near_ma5 = ((close_valid - ma5).abs() / ma5 < 0.05)
ma10 = close_valid.average(10)
above_ma10 = close_valid > ma10
liquid = vol_valid.average(5) > 500_000

position = continuous_buy & near_ma5 & above_ma10 & liquid

print(f"信號統計: 日均 {position.sum(axis=1).mean():.1f} 檔")

# ============ 回測 ============
print("\n【回測結果】")
position = position.fillna(False).astype(bool)

report = sim(
    position,
    resample="W",
    stop_loss=0.1,
    take_profit=0.2,
    position_limit=0.3,
    fee_ratio=1.425/1000,
    tax_ratio=3/1000,
    upload=False
)

print(report)

stats = report.get_stats()
for key in ['cagr', 'monthly_sharpe', 'max_drawdown', 'daily_mean', 'daily_sortino']:
    if key in stats:
        val = stats[key]
        if isinstance(val, (int, float)) and not pd.isna(val):
            print(f"  {key}: {val:.4f}")

report.get_trades().to_csv("laozhou_broker_trades.csv")
print("\n交易記錄已保存: laozhou_broker_trades.csv")
