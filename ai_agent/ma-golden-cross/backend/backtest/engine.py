"""
Golden Cross Backtesting Engine.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

import pandas as pd


class TradeType(Enum):
    """Trade direction."""

    BUY = "buy"
    SELL = "sell"


class CrossType(Enum):
    """MA cross type."""

    GOLDEN = "golden_cross"  # MA5 crosses above MA20 -> BUY signal
    DEATH = "death_cross"  # MA5 crosses below MA20 -> SELL signal


@dataclass
class Trade:
    """Individual trade record."""

    entry_date: str
    entry_price: float
    exit_date: str
    exit_price: float
    trade_type: TradeType
    cross_type: CrossType
    holding_days: int
    profit_pct: float
    profit_amount: float

    def to_dict(self) -> dict:
        return {
            "entry_date": self.entry_date,
            "entry_price": round(self.entry_price, 2),
            "exit_date": self.exit_date,
            "exit_price": round(self.exit_price, 2),
            "trade_type": self.trade_type.value,
            "cross_type": self.cross_type.value,
            "holding_days": self.holding_days,
            "profit_pct": round(self.profit_pct, 4),
            "profit_amount": round(self.profit_amount, 2),
        }


@dataclass
class BacktestSummary:
    """Backtest summary statistics."""

    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    net_profit: float
    max_drawdown: float
    avg_holding_days: float

    def to_dict(self) -> dict:
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate, 4),
            "total_profit": round(self.total_profit, 2),
            "total_loss": round(self.total_loss, 2),
            "net_profit": round(self.net_profit, 2),
            "max_drawdown": round(self.max_drawdown, 4),
            "avg_holding_days": round(self.avg_holding_days, 2),
        }


@dataclass
class BacktestResult:
    """Complete backtest result."""

    symbol: str
    start_date: str
    end_date: str
    short_ma: int
    long_ma: int
    initial_capital: float
    final_capital: float
    summary: BacktestSummary
    trades: list[Trade] = field(default_factory=list)
    equity_curve: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "short_ma": self.short_ma,
            "long_ma": self.long_ma,
            "initial_capital": self.initial_capital,
            "final_capital": round(self.final_capital, 2),
            "summary": self.summary.to_dict(),
            "trades": [t.to_dict() for t in self.trades],
            "equity_curve": self.equity_curve,
        }


class BacktestError(Exception):
    """Raised when backtesting fails."""

    pass


def detect_crossovers(
    ma_short: pd.Series,
    ma_long: pd.Series,
) -> list[dict]:
    """
    Detect golden cross and death cross events.

    Args:
        ma_short: Short-term MA series (e.g., MA5).
        ma_long: Long-term MA series (e.g., MA20).

    Returns:
        List of crossover events, each containing:
        - date: The crossover date/index
        - cross_type: "golden_cross" or "death_cross"
        - price: The closing price at crossover

    Input Format:
        - ma_short: pd.Series with short-term MA values
        - ma_long: pd.Series with long-term MA values
        - Both series must have same index

    Output Format:
        List of dicts:
        [
            {"date": "2024-01-15", "cross_type": "golden_cross", "price": 185.50},
            {"date": "2024-03-20", "cross_type": "death_cross", "price": 182.30},
            ...
        ]

    Example:
        >>> crossovers = detect_crossovers(df["MA5"], df["MA20"])
        >>> print(crossovers[0] if crossovers else "No crossovers")
        {"date": "2024-01-15", "cross_type": "golden_cross", "price": 185.50}
    """
    crossovers = []

    # Need at least 2 data points to detect crossover
    if len(ma_short) < 2 or len(ma_long) < 2:
        return crossovers

    # Create comparison series (ma_short - ma_long)
    # Positive = short above long (golden cross territory)
    # Negative = short below long (death cross territory)
    diff = ma_short - ma_long

    # Detect sign changes
    for i in range(1, len(diff)):
        prev_diff = diff.iloc[i - 1]
        curr_diff = diff.iloc[i]

        if pd.isna(prev_diff) or pd.isna(curr_diff):
            continue

        # Golden Cross: short crosses above long (diff goes from negative to positive)
        if prev_diff < 0 and curr_diff > 0:
            crossovers.append(
                {
                    "date": str(ma_short.index[i]),
                    "cross_type": CrossType.GOLDEN,
                    "price": float(ma_short.iloc[i])
                    if not pd.isna(ma_short.iloc[i])
                    else None,
                }
            )
        # Death Cross: short crosses below long (diff goes from positive to negative)
        elif prev_diff > 0 and curr_diff < 0:
            crossovers.append(
                {
                    "date": str(ma_short.index[i]),
                    "cross_type": CrossType.DEATH,
                    "price": float(ma_short.iloc[i])
                    if not pd.isna(ma_short.iloc[i])
                    else None,
                }
            )

    return crossovers


def run_backtest(
    df: pd.DataFrame,
    ma_short: pd.Series,
    ma_long: pd.Series,
    symbol: str,
    start_date: str,
    end_date: str,
    short_ma: int = 5,
    long_ma: int = 20,
    initial_capital: float = 100000.0,
) -> BacktestResult:
    """
    Run golden cross backtest on OHLCV data with MA indicators.

    Args:
        df: DataFrame with OHLCV data (must have 'Close' column).
        ma_short: Short-term MA series.
        ma_long: Long-term MA series.
        symbol: Stock symbol for reporting.
        start_date: Backtest start date string.
        end_date: Backtest end date string.
        short_ma: Short MA period (for reporting).
        long_ma: Long MA period (for reporting).
        initial_capital: Starting capital (default: 100,000).

    Returns:
        BacktestResult object containing all trades and summary statistics.

    Raises:
        BacktestError: If required data is missing or invalid.

    Input Format:
        df DataFrame columns:
        - Date: datetime index
        - Close: closing prices (required)

        ma_short: pd.Series with short-term MA (e.g., MA5)
        ma_long: pd.Series with long-term MA (e.g., MA20)

    Output Format:
        BacktestResult containing:
        - symbol, dates, MA periods
        - initial_capital, final_capital
        - summary: BacktestSummary with win rate, profits, drawdown
        - trades: List[Trade] with individual trade details
        - equity_curve: List[dict] with portfolio value over time
    """
    if "Close" not in df.columns:
        raise BacktestError("DataFrame must contain 'Close' column")

    if len(ma_short) != len(ma_long) or len(ma_short) != len(df):
        raise BacktestError("MA series length must match DataFrame length")

    # Detect crossovers
    crossovers = detect_crossovers(ma_short, ma_long)

    if not crossovers:
        # No trades if no crossovers detected
        summary = BacktestSummary(
            total_trades=0,
            winning_trades=0,
            losing_trades=0,
            win_rate=0.0,
            total_profit=0.0,
            total_loss=0.0,
            net_profit=0.0,
            max_drawdown=0.0,
            avg_holding_days=0.0,
        )
        return BacktestResult(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            short_ma=short_ma,
            long_ma=long_ma,
            initial_capital=initial_capital,
            final_capital=initial_capital,
            summary=summary,
            trades=[],
            equity_curve=[{"date": str(df.index[-1]), "value": initial_capital}],
        )

    # Execute trades between crossovers
    trades = []
    capital = initial_capital
    position = 0  # 0 = no position, 1 = long
    entry_price = 0.0
    entry_date = ""
    equity_curve = []
    shares = 0

    # Add MA values to df for reference
    df = df.copy()
    df["MA_Short"] = ma_short.values
    df["MA_Long"] = ma_long.values

    for i, cross in enumerate(crossovers):
        cross_date = cross["date"]
        cross_price = cross["price"]

        # Find the row index for this crossover date
        date_idx = df.index[df.index.astype(str) == cross_date].tolist()
        if not date_idx:
            continue
        idx = date_idx[0]

        if cross["cross_type"] == CrossType.GOLDEN and position == 0:
            # BUY signal - enter long position
            shares = int(capital // cross_price)
            if shares > 0:
                entry_price = cross_price
                entry_date = cross_date
                position = 1
                capital -= shares * entry_price  # Cost basis

        elif cross["cross_type"] == CrossType.DEATH and position == 1:
            # SELL signal - exit long position
            exit_price = cross_price
            exit_date = cross_date
            profit_pct = (exit_price - entry_price) / entry_price
            profit_amount = shares * (exit_price - entry_price)

            capital += shares * exit_price
            holding_days = (
                datetime.strptime(exit_date, "%Y-%m-%d")
                - datetime.strptime(entry_date, "%Y-%m-%d")
            ).days

            trades.append(
                Trade(
                    entry_date=entry_date,
                    entry_price=entry_price,
                    exit_date=exit_date,
                    exit_price=exit_price,
                    trade_type=TradeType.BUY,
                    cross_type=CrossType.GOLDEN,
                    holding_days=holding_days,
                    profit_pct=profit_pct,
                    profit_amount=profit_amount,
                )
            )

            position = 0
            entry_price = 0.0
            shares = 0

        # Record equity at each crossover
        equity = capital + (shares * cross_price if position == 1 else 0)
        equity_curve.append({"date": cross_date, "value": round(equity, 2)})

    # Close any open position at end
    if position == 1:
        last_date = str(df.index[-1])
        last_price = float(df["Close"].iloc[-1])
        shares = int(capital // last_price) if last_price > 0 else 0
        exit_price = last_price
        profit_pct = (exit_price - entry_price) / entry_price if entry_price > 0 else 0
        profit_amount = shares * (exit_price - entry_price)
        capital += shares * exit_price

        holding_days = (
            (
                datetime.strptime(last_date, "%Y-%m-%d")
                - datetime.strptime(entry_date, "%Y-%m-%d")
            ).days
            if entry_date
            else 0
        )

        trades.append(
            Trade(
                entry_date=entry_date,
                entry_price=entry_price,
                exit_date=last_date,
                exit_price=exit_price,
                trade_type=TradeType.SELL,
                cross_type=CrossType.DEATH,
                holding_days=holding_days,
                profit_pct=profit_pct,
                profit_amount=profit_amount,
            )
        )

    # Calculate summary statistics
    total_trades = len(trades)
    winning_trades = len([t for t in trades if t.profit_amount > 0])
    losing_trades = len([t for t in trades if t.profit_amount <= 0])
    total_profit = sum(t.profit_amount for t in trades if t.profit_amount > 0)
    total_loss = sum(t.profit_amount for t in trades if t.profit_amount <= 0)
    net_profit = total_profit + total_loss
    win_rate = winning_trades / total_trades if total_trades > 0 else 0.0
    avg_holding = (
        sum(t.holding_days for t in trades) / total_trades if total_trades > 0 else 0.0
    )

    # Calculate max drawdown
    max_drawdown = 0.0
    peak = initial_capital
    for eq in equity_curve:
        if eq["value"] > peak:
            peak = eq["value"]
        drawdown = (peak - eq["value"]) / peak if peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    summary = BacktestSummary(
        total_trades=total_trades,
        winning_trades=winning_trades,
        losing_trades=losing_trades,
        win_rate=win_rate,
        total_profit=total_profit,
        total_loss=total_loss,
        net_profit=net_profit,
        max_drawdown=max_drawdown,
        avg_holding_days=avg_holding,
    )

    return BacktestResult(
        symbol=symbol,
        start_date=start_date,
        end_date=end_date,
        short_ma=short_ma,
        long_ma=long_ma,
        initial_capital=initial_capital,
        final_capital=round(capital, 2),
        summary=summary,
        trades=trades,
        equity_curve=equity_curve,
    )
