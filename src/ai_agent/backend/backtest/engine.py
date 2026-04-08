# backend/backtest/engine.py
import pandas as pd
from typing import List, Dict
from backend.indicators.ma import calculate_ma, detect_crossover


class BacktestEngine:
    def __init__(self, initial_cash: float = 1000000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.position = 0
        self.trades: List[Dict] = []
        self.current_entry = None

    def buy(self, date, price: float, shares: int):
        cost = price * shares
        if cost > self.cash:
            shares = int(self.cash / price)
            cost = price * shares

        if shares > 0:
            self.cash -= cost
            self.position += shares
            self.current_entry = {
                "entry_date": date,
                "entry_price": price,
                "shares": shares,
            }

    def sell(self, date, price: float, shares: int = None):
        if shares is None:
            shares = self.position

        shares = min(shares, self.position)
        if shares > 0 and self.current_entry:
            revenue = price * shares
            self.cash += revenue
            self.position -= shares

            profit = (price - self.current_entry["entry_price"]) * shares
            self.trades.append(
                {
                    "entry_date": str(self.current_entry["entry_date"].date())
                    if hasattr(self.current_entry["entry_date"], "date")
                    else str(self.current_entry["entry_date"]),
                    "entry_price": self.current_entry["entry_price"],
                    "exit_date": str(date.date())
                    if hasattr(date, "date")
                    else str(date),
                    "exit_price": price,
                    "profit": profit,
                    "type": "golden_cross",
                }
            )
            self.current_entry = None

    def get_stats(self) -> Dict:
        if not self.trades:
            return {
                "total_trades": 0,
                "win_rate": 0.0,
                "total_profit": 0.0,
                "max_drawdown": 0.0,
                "trades": [],
            }

        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t["profit"] > 0]
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        total_profit = sum(t["profit"] for t in self.trades)

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
            "trades": self.trades,
        }


def run_backtest(
    df: pd.DataFrame, short_window: int = 5, long_window: int = 20
) -> Dict:
    df_with_ma = calculate_ma(df, short_window=short_window, long_window=long_window)
    crossovers = detect_crossover(df_with_ma)

    engine = BacktestEngine()

    for crossover in crossovers:
        if crossover["type"] == "golden_cross":
            engine.buy(crossover["date"], crossover["price"], shares=1000)
        else:
            engine.sell(crossover["date"], crossover["price"])

    if engine.position > 0 and engine.current_entry:
        last_date = df_with_ma.iloc[-1]["date"]
        last_price = df_with_ma.iloc[-1]["close"]
        engine.sell(last_date, last_price)

    for crossover, trade in zip(crossovers, engine.trades):
        trade["type"] = crossover["type"]

    return engine.get_stats()
