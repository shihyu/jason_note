"""
Tests for Moving Average indicator module.
"""

import pytest
import pandas as pd
import numpy as np

from backend.indicators.ma import (
    calculate_sma,
    calculate_ma,
    MAError,
    MAResult,
)


class TestMAError:
    """Test MAError exception."""

    def test_ma_error_is_exception(self):
        """MAError should be an Exception subclass."""
        error = MAError("Test error")
        assert isinstance(error, Exception)

    def test_ma_error_message(self):
        """MAError should preserve message."""
        msg = "Calculation failed"
        error = MAError(msg)
        assert str(error) == msg


class TestCalculateSMA:
    """Test calculate_sma function."""

    def test_calculate_sma_basic(self):
        """calculate_sma should compute rolling mean correctly."""
        prices = pd.Series([100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0])
        result = calculate_sma(prices, 3)

        # First 2 values should be NaN
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])
        # Subsequent values should be rolling means
        assert result.iloc[2] == pytest.approx(101.0)  # (100+102+101)/3
        assert result.iloc[3] == pytest.approx(102.0)  # (102+101+103)/3

    def test_calculate_sma_window_1(self):
        """Window=1 should return same values."""
        prices = pd.Series([100.0, 102.0, 101.0])
        result = calculate_sma(prices, 1)
        assert result.iloc[0] == pytest.approx(100.0)
        assert result.iloc[1] == pytest.approx(102.0)
        assert result.iloc[2] == pytest.approx(101.0)

    def test_calculate_sma_window_larger_than_series(self):
        """Window larger than series should return all NaN."""
        prices = pd.Series([100.0, 102.0])
        result = calculate_sma(prices, 5)
        assert pd.isna(result.iloc[0])
        assert pd.isna(result.iloc[1])

    def test_calculate_sma_invalid_window_zero(self):
        """Window=0 should raise ValueError."""
        prices = pd.Series([100.0, 102.0])
        with pytest.raises(ValueError, match="Window must be positive"):
            calculate_sma(prices, 0)

    def test_calculate_sma_invalid_window_negative(self):
        """Negative window should raise ValueError."""
        prices = pd.Series([100.0, 102.0])
        with pytest.raises(ValueError, match="Window must be positive"):
            calculate_sma(prices, -1)

    def test_calculate_sma_empty_series(self):
        """Empty series should raise ValueError."""
        prices = pd.Series([], dtype=float)
        with pytest.raises(ValueError, match="Series cannot be empty"):
            calculate_sma(prices, 3)

    def test_calculate_sma_preserves_index(self):
        """calculate_sma should preserve original index."""
        prices = pd.Series(
            [100.0, 102.0, 101.0, 103.0],
            index=["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"],
        )
        result = calculate_sma(prices, 2)
        assert list(result.index) == [
            "2024-01-01",
            "2024-01-02",
            "2024-01-03",
            "2024-01-04",
        ]


class TestCalculateMA:
    """Test calculate_ma function."""

    def test_calculate_ma_basic(self):
        """calculate_ma should return MAResult with both MAs."""
        df = pd.DataFrame(
            {
                "Close": [
                    100.0,
                    102.0,
                    101.0,
                    103.0,
                    105.0,
                    104.0,
                    106.0,
                    108.0,
                    107.0,
                    109.0,
                    111.0,
                    110.0,
                    112.0,
                    114.0,
                    113.0,
                    115.0,
                    117.0,
                    116.0,
                    118.0,
                    120.0,
                ],
            }
        )
        result = calculate_ma(df, short_window=5, long_window=20)

        assert isinstance(result, MAResult)
        assert isinstance(result.ma_short, pd.Series)
        assert isinstance(result.ma_long, pd.Series)
        assert len(result.ma_short) == 20
        assert len(result.ma_long) == 20

    def test_calculate_ma_missing_close_column(self):
        """Missing Close column should raise MAError."""
        df = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Volume": [1000],
            }
        )
        with pytest.raises(MAError, match="DataFrame must contain 'Close' column"):
            calculate_ma(df)

    def test_calculate_ma_invalid_short_window_zero(self):
        """short_window=0 should raise ValueError."""
        df = pd.DataFrame({"Close": [100.0, 102.0]})
        with pytest.raises(ValueError, match="MA windows must be positive"):
            calculate_ma(df, short_window=0, long_window=20)

    def test_calculate_ma_invalid_long_window_zero(self):
        """long_window=0 should raise ValueError."""
        df = pd.DataFrame({"Close": [100.0, 102.0]})
        with pytest.raises(ValueError, match="MA windows must be positive"):
            calculate_ma(df, short_window=5, long_window=0)

    def test_calculate_ma_short_not_less_than_long(self):
        """short_window >= long_window should raise ValueError."""
        df = pd.DataFrame({"Close": [100.0, 102.0, 103.0, 104.0, 105.0]})
        with pytest.raises(
            ValueError, match="short_window must be less than long_window"
        ):
            calculate_ma(df, short_window=20, long_window=5)

    def test_calculate_ma_equal_windows(self):
        """short_window == long_window should raise ValueError."""
        df = pd.DataFrame({"Close": [100.0, 102.0, 103.0, 104.0, 105.0]})
        with pytest.raises(
            ValueError, match="short_window must be less than long_window"
        ):
            calculate_ma(df, short_window=10, long_window=10)

    def test_calculate_ma_default_windows(self):
        """Default windows should be 5 and 20."""
        df = pd.DataFrame({"Close": [100.0] * 25})
        result = calculate_ma(df)

        assert isinstance(result, MAResult)
        # First 4 values of MA5 should be NaN
        assert pd.isna(result.ma_short.iloc[0])
        assert pd.isna(result.ma_short.iloc[3])
        # First 19 values of MA20 should be NaN
        assert pd.isna(result.ma_long.iloc[0])
        assert pd.isna(result.ma_long.iloc[18])

    def test_calculate_ma_ma_values_correct(self):
        """MA values should be calculated correctly."""
        df = pd.DataFrame(
            {
                "Close": [100.0, 102.0, 101.0, 103.0, 105.0, 104.0, 106.0],
            }
        )
        result = calculate_ma(df, short_window=3, long_window=5)

        # MA3: [NaN, NaN, 101.0, (102+101+103)/3, ...]
        assert pd.isna(result.ma_short.iloc[0])
        assert pd.isna(result.ma_short.iloc[1])
        assert result.ma_short.iloc[2] == pytest.approx(101.0)

    def test_calculate_ma_maresult_contains_both_ma_series(self):
        """MAResult should contain both short and long MA series."""
        df = pd.DataFrame({"Close": [100.0] * 25})
        result = calculate_ma(df, short_window=5, long_window=10)

        assert hasattr(result, "ma_short")
        assert hasattr(result, "ma_long")
        assert len(result.ma_short) == 25
        assert len(result.ma_long) == 25
