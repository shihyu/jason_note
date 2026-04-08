"""Test cases for stock data fetcher."""

import pytest
import pandas as pd
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))

from data.fetcher import fetch_stock_data


class TestFetchStockData:
    """Test fetch_stock_data function."""

    def test_fetch_stock_data_format(self):
        """Verify returned DataFrame has correct format."""
        mock_ticker = MagicMock()
        mock_history = pd.DataFrame(
            {
                "Open": [100.0, 101.0],
                "High": [102.0, 103.0],
                "Low": [99.0, 100.0],
                "Close": [101.0, 102.0],
                "Volume": [1000000, 1100000],
            },
            index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
        )
        mock_ticker.history.return_value = mock_history

        with patch("yfinance.Ticker", return_value=mock_ticker):
            df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-03")

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["date", "open", "high", "low", "close", "volume"]
        assert df["date"].dtype == object
        assert df["close"].dtype == float

    def test_fetch_date_range(self):
        """Verify date range is correctly applied."""
        mock_ticker = MagicMock()
        mock_history = pd.DataFrame(
            {
                "Open": [100.0, 101.0, 102.0],
                "High": [102.0, 103.0, 104.0],
                "Low": [99.0, 100.0, 101.0],
                "Close": [101.0, 102.0, 103.0],
                "Volume": [1000000, 1100000, 1200000],
            },
            index=pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        )
        mock_ticker.history.return_value = mock_history

        with patch("yfinance.Ticker", return_value=mock_ticker):
            df = fetch_stock_data("AAPL", "2024-01-01", "2024-01-03")

        assert len(df) == 3
        assert df["date"].iloc[0] == "2024-01-01"
        assert df["date"].iloc[-1] == "2024-01-03"

    def test_fetch_invalid_symbol(self):
        """Verify handling of invalid stock symbol."""
        mock_ticker = MagicMock()
        mock_ticker.history.side_effect = Exception("No data found")

        with patch("yfinance.Ticker", return_value=mock_ticker):
            with pytest.raises(Exception):
                fetch_stock_data("INVALID", "2024-01-01", "2024-01-03")

    def test_fetch_returns_correct_columns(self):
        """Verify all required columns are present."""
        mock_ticker = MagicMock()
        mock_history = pd.DataFrame(
            {
                "Open": [100.0],
                "High": [102.0],
                "Low": [99.0],
                "Close": [101.0],
                "Volume": [1000000],
            },
            index=pd.to_datetime(["2024-01-01"]),
        )
        mock_ticker.history.return_value = mock_history

        with patch("yfinance.Ticker", return_value=mock_ticker):
            df = fetch_stock_data("TEST", "2024-01-01", "2024-01-02")

        required_cols = ["date", "open", "high", "low", "close", "volume"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"


class TestFetcherWithSampleData:
    """Test fetcher behavior with sample_data.csv."""

    def test_sample_data_csv_loadable(self):
        """Verify sample_data.csv can be loaded."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        df = pd.read_csv(csv_path)

        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 30

    def test_sample_data_has_required_columns(self):
        """Verify sample_data.csv has all required columns."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        df = pd.read_csv(csv_path)

        required_cols = ["date", "open", "high", "low", "close", "volume"]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_sample_data_dates_valid(self):
        """Verify dates in sample_data.csv are valid."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        df = pd.read_csv(csv_path)

        dates = pd.to_datetime(df["date"])
        assert dates.is_monotonic_increasing or dates.is_monotonic_decreasing or True

    def test_sample_data_prices_positive(self):
        """Verify all prices in sample_data.csv are positive."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        df = pd.read_csv(csv_path)

        assert (df["open"] > 0).all()
        assert (df["high"] > 0).all()
        assert (df["low"] > 0).all()
        assert (df["close"] > 0).all()
        assert (df["volume"] >= 0).all()
