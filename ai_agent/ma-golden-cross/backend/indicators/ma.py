"""
Moving Average indicator calculations.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import pandas as pd


class MAError(Exception):
    """Raised when MA calculation fails."""

    pass


@dataclass
class MAResult:
    """Container for MA calculation results."""

    ma_short: pd.Series  # Short-term MA (e.g., MA5)
    ma_long: pd.Series  # Long-term MA (e.g., MA20)


def calculate_sma(series: pd.Series, window: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).

    Args:
        series: Price series (typically Close prices).
        window: Number of periods for SMA window.

    Returns:
        pandas.Series with SMA values, same index as input.

    Raises:
        ValueError: If window <= 0 or series is empty.
        MAError: If required column 'Close' is missing.

    Input Format:
        - series: pandas.Series with numeric values
        - window: positive integer

    Output Format:
        pandas.Series with same index as input
        - First (window-1) values will be NaN
        - Subsequent values are rolling means

    Example:
        >>> prices = pd.Series([100, 102, 101, 103, 105, 104, 106])
        >>> ma5 = calculate_sma(prices, 5)
        >>> print(ma5)
        0      NaN
        1      NaN
        2      NaN
        3      NaN
        4    102.2
        5    103.0
        6    103.8
        dtype: float64
    """
    if window <= 0:
        raise ValueError(f"Window must be positive, got {window}")

    if len(series) == 0:
        raise ValueError("Series cannot be empty")

    return series.rolling(window=window, min_periods=window).mean()


def calculate_ma(
    df: pd.DataFrame, short_window: int = 5, long_window: int = 20
) -> MAResult:
    """
    Calculate short-term and long-term Moving Averages.

    Args:
        df: DataFrame with 'Close' column (OHLCV data).
        short_window: Short MA period (default: 5).
        long_window: Long MA period (default: 20).

    Returns:
        MAResult with ma_short and ma_long Series.

    Raises:
        MAError: If 'Close' column not found in DataFrame.
        ValueError: If windows are not positive integers.

    Input Format:
        df DataFrame with columns:
        - Close: closing prices (required)
        - Index: datetime or sequential

    Output Format:
        MAResult containing:
        - ma_short: pd.Series with short-term MA (e.g., MA5)
        - ma_long: pd.Series with long-term MA (e.g., MA20)

    Example:
        >>> df = fetch_stock_data("AAPL", "2024-01-01", "2024-12-31").df
        >>> result = calculate_ma(df, short_window=5, long_window=20)
        >>> print(result.ma_short.head(10))
        0          NaN
        ...
        4    185.920
        dtype: float64
    """
    if "Close" not in df.columns:
        raise MAError("DataFrame must contain 'Close' column")

    if short_window <= 0 or long_window <= 0:
        raise ValueError("MA windows must be positive integers")

    if short_window >= long_window:
        raise ValueError("short_window must be less than long_window")

    ma_short = calculate_sma(df["Close"], short_window)
    ma_long = calculate_sma(df["Close"], long_window)

    return MAResult(ma_short=ma_short, ma_long=ma_long)
