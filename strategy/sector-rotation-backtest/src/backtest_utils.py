"""
回測工具模組

提供修正後的回測邏輯：
1. 避免 Look-ahead Bias（訊號延後一天生效）
2. 扣除台股交易成本（手續費 + 證交稅）
"""
import pandas as pd
import numpy as np


class BacktestEngine:
    """回測引擎（修正版）"""

    # 台股交易成本設定
    COMMISSION_RATE = 0.001425  # 手續費 0.1425%（券商折扣後約 0.05-0.1%，這裡使用官方費率）
    TAX_RATE = 0.003  # 證交稅 0.3%（賣出時收取）
    COMMISSION_DISCOUNT = 0.3  # 券商折扣（70% off = 0.3 倍）

    def __init__(self, commission_rate=None, tax_rate=None, discount=None):
        """
        初始化回測引擎

        Args:
            commission_rate: 手續費率（None = 使用預設值）
            tax_rate: 證交稅率（None = 使用預設值）
            discount: 券商折扣（None = 使用預設值）
        """
        self.commission_rate = commission_rate or self.COMMISSION_RATE
        self.tax_rate = tax_rate or self.TAX_RATE
        self.discount = discount or self.COMMISSION_DISCOUNT

    def calculate_transaction_cost(self, signals, close):
        """
        計算交易成本

        Args:
            signals: 交易訊號 DataFrame（1=持有, 0=不持有）
            close: 收盤價 DataFrame

        Returns:
            Series: 每日交易成本（佔當日資產比例）
        """
        # 計算持倉變化
        position_changes = signals.diff().fillna(signals.iloc[0])

        # 買入訊號：從 0 變成 1（或初始為 1）
        buy_signals = (position_changes > 0).astype(int)

        # 賣出訊號：從 1 變成 0
        sell_signals = (position_changes < 0).astype(int)

        # 計算買入成本（手續費）
        # 成本 = 買入股數 × 手續費率 × 折扣
        buy_cost = buy_signals.sum(axis=1) * self.commission_rate * self.discount

        # 計算賣出成本（手續費 + 證交稅）
        # 成本 = 賣出股數 × (手續費率 × 折扣 + 證交稅率)
        sell_cost = sell_signals.sum(axis=1) * (self.commission_rate * self.discount + self.tax_rate)

        # 總成本 = 買入成本 + 賣出成本
        # 這裡假設等權重，所以每支股票的權重 = 1 / 持股數
        position_count = signals.sum(axis=1).replace(0, 1)  # 避免除以 0
        total_cost = (buy_cost + sell_cost) / position_count

        return total_cost

    def backtest_with_cost(self, signals, close, verbose=False):
        """
        執行修正後的回測（避免 Look-ahead Bias + 扣除交易成本）

        Args:
            signals: 交易訊號 DataFrame（index=日期, columns=股票代碼, value=1持有/0不持有）
            close: 收盤價 DataFrame（index=日期, columns=股票代碼）
            verbose: 是否顯示詳細資訊

        Returns:
            dict: {
                'cagr': 年化報酬率,
                'sharpe': Sharpe Ratio,
                'max_drawdown': 最大回撤,
                'win_rate': 勝率,
                'total_trades': 總交易次數,
                'cum_returns': 累積報酬曲線,
                'strategy_returns': 每日策略報酬,
                'total_cost': 總交易成本（佔初始資產比例）
            }
        """
        if signals.empty:
            return self._empty_result()

        # 【修正 1】：訊號延後一天生效（避免 Look-ahead Bias）
        # 在 t 日計算的訊號，在 t+1 日才買入
        signals_shifted = signals.shift(1).fillna(0)

        # 對齊日期和股票
        close_aligned = close.reindex(signals_shifted.index)[signals_shifted.columns]

        # 計算每日報酬
        returns = close_aligned.pct_change(fill_method=None)

        # 【修正 2】：計算交易成本
        transaction_cost = self.calculate_transaction_cost(signals_shifted, close_aligned)

        # 計算策略報酬（等權重）
        position_count = signals_shifted.sum(axis=1).replace(0, np.nan)

        # 原始報酬（未扣成本）
        raw_returns = (returns * signals_shifted).sum(axis=1) / position_count

        # 扣除交易成本後的報酬
        strategy_returns = raw_returns - transaction_cost

        # 填充 NaN 為 0（沒有持倉時報酬為 0）
        strategy_returns = strategy_returns.fillna(0)

        # 計算累積報酬
        cum_returns = (1 + strategy_returns).cumprod()

        # 計算績效指標
        total_return = cum_returns.iloc[-1] - 1
        years = len(strategy_returns) / 252
        cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

        sharpe = strategy_returns.mean() / strategy_returns.std() * np.sqrt(252) if strategy_returns.std() > 0 else 0

        # 計算最大回撤
        rolling_max = cum_returns.expanding().max()
        drawdown = (cum_returns - rolling_max) / rolling_max
        max_drawdown = drawdown.min()

        # 計算勝率
        valid_returns = strategy_returns[strategy_returns != 0]
        win_rate = (valid_returns > 0).sum() / len(valid_returns) if len(valid_returns) > 0 else 0

        # 計算交易次數
        total_trades = signals_shifted.diff().abs().sum().sum() / 2

        # 計算總交易成本
        total_cost = transaction_cost.sum()

        if verbose:
            print(f"總交易成本：{total_cost * 100:.2f}%")
            print(f"平均單次成本：{(self.commission_rate * self.discount * 2 + self.tax_rate) * 100:.4f}%")

        return {
            'cagr': cagr,
            'sharpe': sharpe,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'total_trades': int(total_trades),
            'cum_returns': cum_returns,
            'strategy_returns': strategy_returns,
            'total_cost': total_cost
        }

    def _empty_result(self):
        """返回空結果"""
        return {
            'cagr': None,
            'sharpe': None,
            'max_drawdown': None,
            'win_rate': None,
            'total_trades': 0,
            'total_cost': 0
        }
