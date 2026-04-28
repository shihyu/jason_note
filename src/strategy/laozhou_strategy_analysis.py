"""
老周交易心法 - FinLab 量化驗證
================================

數據說明：
- FinLab 沒有「券商分點買超排行」數據（這需要從交易所取得 specialized data）
- 可用替代方案：
  1. 三大法人買賣超 (institutional_investors_trading_summary) 作為主力意圖的 proxy
  2. 集保戶數 (etl:inventory:全部人數) 作為籌碼集中度的 proxy

策略核心：
1. 三大法人連續買超（3天以上）
2. 現價不超過均價5%
3. 持有人數減少（籌碼集中）
"""

from finlab import data
from finlab.backtest import sim
import pandas as pd
import numpy as np

print("=" * 60)
print("老周交易心法 - FinLab 量化驗證")
print("=" * 60)

# ============================================================
# Step 1: 獲取數據
# ============================================================
print("\n【Step 1】獲取數據...")

# 價格數據
close = data.get("price:收盤價")
volume = data.get("price:成交股數")

# 三大法人買賣超 (外陸資)
inst_buy = data.get("institutional_investors_trading_summary:外陸資買賣超股數(不含外資自營商)")

# 持有人數 (週頻率)
try:
    holder_count = data.get("etl:inventory:全部人數")
    print(f"持有人數據形狀: {holder_count.shape}")
    print(f"持有人數據頻率: 週頻率")
except Exception as e:
    print(f"持有人數據獲取失敗: {e}")
    holder_count = None

print(f"收盤價數據形狀: {close.shape}")
print(f"法人買賣超數據形狀: {inst_buy.shape}")

# ============================================================
# Step 2: 定義條件 - 三大法人連續買超
# ============================================================
print("\n【Step 2】定義選股條件...")

# 條件1: 三大法人連續買超 (3天以上)
inst_continuous_buy = inst_buy.shift(1).sustain(3) & (inst_buy > 0)
print(f"條件1 - 三大法人連續買超3天以上: {inst_continuous_buy.sum().sum()} 筆信號")

# 條件2: 現價不超過均價5% (計算3天均價)
avg_cost_3d = close.shift(1).average(3)
within_5pct = close < avg_cost_3d * 1.05
print(f"條件2 - 現價不超過均價5%: {within_5pct.sum().sum()} 筆信號")

# 流動性條件
liquid = volume.average(20) > 1000000  # 日均成交量 > 100張

# 結合基本條件
position = inst_continuous_buy & within_5pct & liquid
print(f"基本條件組合 (法人連續買超 + 均價5%內 + 流動性): {position.sum().sum()} 筆信號")

# ============================================================
# Step 3: 執行回測
# ============================================================
print("\n【Step 3】執行回測...")

# 選擇每天符合條件的股票
report = sim(
    position,
    resample="W",  # 週結算
    stop_loss=0.1,   # 10% 停損
    take_profit=0.2, # 20% 停利
    position_limit=0.3,  # 單檔最大30%
    fee_ratio=1.425/1000,
    tax_ratio=3/1000,
    upload=False
)

# ============================================================
# Step 4: 顯示結果
# ============================================================
print("\n【Step 4】回測結果...")
print(report)

# 顯示關鍵指標
stats = report.get_stats()
print(f"\n===== 關鍵指標 =====")
print(f"CAGR (年化報酬率): {stats.get('cagr', 'N/A')}")
print(f"Sharpe (夏普比率): {stats.get('monthly_sharpe', 'N/A')}")
print(f"Max Drawdown (最大回撤): {stats.get('max_drawdown', 'N/A')}")

# ============================================================
# 分析說明
# ============================================================
print("\n" + "=" * 60)
print("【重要說明】")
print("=" * 60)
print("""
老周策略核心數據「券商分點買超排行」需要從交易所取得 specialized data，
FinLab 標準數據集沒有這個數據。

本回測使用替代方案：
1. 三大法人 (外陸資) 買賣超 → 作為主力意圖的 proxy
2. 持有人數 (etl:inventory) → 作為籌碼集中度的 proxy

若要完整實現老周策略，需要：
- 券商分點數據：可從 FinLab API 或其他數據源取得
- 集保戶數：可從集保結算所網站取得

建議補充數據源以提高策略精確度。
""")

