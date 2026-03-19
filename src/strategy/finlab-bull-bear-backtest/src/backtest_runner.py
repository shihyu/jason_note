import math

import numpy as np
import pandas as pd

from cost_model import TaiwanStockCostModel


class BacktestRunner:
    def __init__(self, cost_model=None, initial_capital=100000.0):
        self.cost_model = cost_model or TaiwanStockCostModel()
        self.initial_capital = initial_capital

    def run(self, positions: pd.DataFrame, prices: pd.DataFrame) -> dict:
        shifted_positions = positions.shift(1).fillna(0.0)
        price_returns = prices.pct_change(fill_method=None).fillna(0.0)

        gross_returns = (price_returns * shifted_positions).sum(axis=1)
        daily_cost = self._calculate_daily_cost(shifted_positions)
        strategy_returns = gross_returns - daily_cost
        equity_curve = (1 + strategy_returns).cumprod()

        return {
            "positions": shifted_positions,
            "strategy_returns": strategy_returns,
            "equity_curve": equity_curve,
            "metrics": self._build_metrics(strategy_returns, equity_curve, shifted_positions, daily_cost),
        }

    def _calculate_daily_cost(self, shifted_positions: pd.DataFrame) -> pd.Series:
        position_changes = shifted_positions.diff().fillna(shifted_positions.iloc[0])
        buy_changes = position_changes.clip(lower=0.0)
        sell_changes = position_changes.clip(upper=0.0)

        buy_cost = buy_changes.sum(axis=1) * self.cost_model.buy_rate
        sell_cost = sell_changes.abs().sum(axis=1) * self.cost_model.sell_rate
        return buy_cost + sell_cost

    def _build_metrics(
        self,
        strategy_returns: pd.Series,
        equity_curve: pd.Series,
        positions: pd.DataFrame,
        daily_cost: pd.Series,
    ) -> dict:
        total_return = equity_curve.iloc[-1] - 1
        years = len(strategy_returns) / 52 if len(strategy_returns) else 0
        cagr = (equity_curve.iloc[-1] ** (1 / years) - 1) if years > 0 and equity_curve.iloc[-1] > 0 else 0.0
        volatility = strategy_returns.std()
        sharpe = strategy_returns.mean() / volatility * math.sqrt(52) if volatility and not np.isnan(volatility) else 0.0
        rolling_max = equity_curve.cummax()
        drawdown = equity_curve / rolling_max - 1
        total_trades = int((positions.diff().abs().fillna(positions.iloc[0]).sum(axis=1) > 0).sum())

        return {
            "total_return": total_return,
            "cagr": cagr,
            "sharpe": sharpe,
            "max_drawdown": drawdown.min(),
            "total_trades": total_trades,
            "total_cost_ratio": daily_cost.sum(),
        }
