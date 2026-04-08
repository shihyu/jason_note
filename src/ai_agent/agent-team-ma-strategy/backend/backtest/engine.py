import pandas as pd


class BacktestEngine:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.position = None
        self.trades = []
        self.capital = initial_capital
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0

    def _update_drawdown(self):
        if self.capital > self.peak_capital:
            self.peak_capital = self.capital
        drawdown = self.peak_capital - self.capital
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown

    def _calculate_profit(
        self, entry_price: float, exit_price: float, shares: int
    ) -> float:
        return (exit_price - entry_price) * shares

    def execute_signal(self, date: str, price: float, signal: str):
        if signal == "golden_cross" and self.position is None:
            shares = int(self.capital / price)
            if shares > 0:
                self.position = {
                    "entry_date": date,
                    "entry_price": price,
                    "shares": shares,
                }
                self.capital -= price * shares
        elif signal == "death_cross" and self.position is not None:
            entry = self.position
            exit_value = entry["shares"] * price
            profit = self._calculate_profit(
                entry["entry_price"], price, entry["shares"]
            )
            self.capital += exit_value
            self.trades.append(
                {
                    "entry_date": entry["entry_date"],
                    "entry_price": entry["entry_price"],
                    "exit_date": date,
                    "exit_price": price,
                    "profit": profit,
                    "type": "golden_cross",
                }
            )
            self.position = None
            self._update_drawdown()

    def run(self, df: pd.DataFrame, short_col: str = "ma_5", long_col: str = "ma_20"):
        for _, row in df.iterrows():
            if pd.isna(row[short_col]) or pd.isna(row[long_col]):
                continue
            signal = row.get("signal", "hold")
            if signal in ("golden_cross", "death_cross"):
                self.execute_signal(str(row["date"]), float(row["close"]), str(signal))
        if self.position is not None:
            last_row = df.iloc[-1]
            profit = self._calculate_profit(
                float(self.position["entry_price"]),
                float(last_row["close"]),
                int(self.position["shares"]),
            )
            self.trades.append(
                {
                    "entry_date": self.position["entry_date"],
                    "entry_price": self.position["entry_price"],
                    "exit_date": str(last_row["date"]),
                    "exit_price": float(last_row["close"]),
                    "profit": profit,
                    "type": "golden_cross",
                }
            )
            self.capital += self.position["shares"] * float(last_row["close"])
            self.position = None
            self._update_drawdown()
        total_trades = len(self.trades)
        win_trades = sum(1 for t in self.trades if t["profit"] > 0)
        total_profit = self.capital - self.initial_capital
        return {
            "total_trades": total_trades,
            "win_rate": win_trades / total_trades if total_trades > 0 else 0.0,
            "total_profit": total_profit,
            "max_drawdown": self.max_drawdown,
            "trades": self.trades,
        }


def run_backtest(
    df: pd.DataFrame,
    initial_capital: float = 100000.0,
    short_col: str = "ma_5",
    long_col: str = "ma_20",
):
    engine = BacktestEngine(initial_capital)
    return engine.run(df, short_col, long_col)
