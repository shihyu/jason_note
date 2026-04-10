"""
Tests for stock data fetcher module.
"""

import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import pandas as pd

from backend.data.fetcher import (
    fetch_stock_data,
    validate_date_range,
    DataFetchError,
    StockData,
)


class TestDataFetchError:
    """Test DataFetchError exception."""

    def test_data_fetch_error_is_exception(self):
        """DataFetchError should be an Exception subclass."""
        error = DataFetchError("Test error")
        assert isinstance(error, Exception)

    def test_data_fetch_error_message(self):
        """DataFetchError should preserve message."""
        msg = "Connection failed"
        error = DataFetchError(msg)
        assert str(error) == msg


class TestStockData:
    """Test StockData dataclass."""

    def test_stock_data_creation(self):
        """StockData should store symbol, dates, and dataframe."""
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01", "2024-01-02"],
                "Open": [100.0, 101.0],
                "High": [105.0, 106.0],
                "Low": [99.0, 100.0],
                "Close": [102.0, 103.0],
                "Volume": [1000, 1100],
            }
        )
        data = StockData(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-02",
            df=df,
        )
        assert data.symbol == "AAPL"
        assert data.start_date == "2024-01-01"
        assert data.end_date == "2024-01-02"
        assert len(data.df) == 2

    def test_stock_data_to_dict(self):
        """StockData.to_dict() should serialize correctly."""
        df = pd.DataFrame(
            {
                "Date": ["2024-01-01"],
                "Open": [100.0],
                "High": [105.0],
                "Low": [99.0],
                "Close": [102.0],
                "Volume": [1000],
            }
        )
        data = StockData(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-02",
            df=df,
        )
        result = data.to_dict()
        assert result["symbol"] == "AAPL"
        assert result["start_date"] == "2024-01-01"
        assert result["end_date"] == "2024-01-02"
        assert "data" in result
        assert len(result["data"]) == 1


class TestValidateDateRange:
    """Test date range validation."""

    def test_validate_valid_range(self):
        """Valid date range should return datetime objects."""
        start, end = validate_date_range("2024-01-01", "2024-12-31")
        assert start == datetime(2024, 1, 1)
        assert end == datetime(2024, 12, 31)

    def test_validate_invalid_format(self):
        """Invalid date format should raise DataFetchError."""
        with pytest.raises(DataFetchError, match="YYYY-MM-DD"):
            validate_date_range("01-01-2024", "2024-12-31")

    def test_validate_start_after_end(self):
        """Start date after end date should raise DataFetchError."""
        with pytest.raises(DataFetchError, match="start_date must be before end_date"):
            validate_date_range("2024-12-31", "2024-01-01")

    def test_validate_start_equals_end(self):
        """Start date equal to end date should raise DataFetchError."""
        with pytest.raises(DataFetchError, match="start_date must be before end_date"):
            validate_date_range("2024-01-01", "2024-01-01")


class TestFetchStockData:
    """Test fetch_stock_data function."""

    @patch("backend.data.fetcher.yf.Ticker")
    def test_fetch_stock_data_success(self, mock_ticker):
        """Successful fetch should return StockData with OHLCV columns."""
        # Setup mock
        mock_df = pd.DataFrame(
            {
                "Open": [185.0, 186.0],
                "High": [187.0, 188.0],
                "Low": [184.0, 185.0],
                "Close": [185.5, 186.5],
                "Volume": [45678900, 46789000],
            },
            index=pd.to_datetime(["2024-01-02", "2024-01-03"]),
        )

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance

        # Execute
        result = fetch_stock_data("AAPL", "2024-01-01", "2024-01-05")

        # Verify
        assert result.symbol == "AAPL"
        assert result.start_date == "2024-01-01"
        assert result.end_date == "2024-01-05"
        assert "Close" in result.df.columns
        assert len(result.df) == 2

    @patch("backend.data.fetcher.yf.Ticker")
    def test_fetch_stock_data_empty_result(self, mock_ticker):
        """Empty data should raise DataFetchError."""
        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_instance

        with pytest.raises(DataFetchError, match="No data returned"):
            fetch_stock_data("INVALID", "2024-01-01", "2024-01-05")

    @patch("backend.data.fetcher.yf.Ticker")
    def test_fetch_stock_data_exception(self, mock_ticker):
        """yfinance exception should raise DataFetchError."""
        mock_ticker.side_effect = Exception("Network error")

        with pytest.raises(DataFetchError, match="Failed to fetch data"):
            fetch_stock_data("AAPL", "2024-01-01", "2024-01-05")

    @patch("backend.data.fetcher.yf.Ticker")
    def test_fetch_stock_data_custom_interval(self, mock_ticker):
        """Custom interval parameter should be passed to yfinance."""
        mock_df = pd.DataFrame(
            {
                "Open": [185.0],
                "High": [187.0],
                "Low": [184.0],
                "Close": [185.5],
                "Volume": [45678900],
            },
            index=pd.to_datetime(["2024-01-02"]),
        )

        mock_ticker_instance = MagicMock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance

        fetch_stock_data("AAPL", "2024-01-01", "2024-01-05", interval="1wk")

        mock_ticker_instance.history.assert_called_once()
        call_kwargs = mock_ticker_instance.history.call_args
        assert call_kwargs[1]["interval"] == "1wk"
