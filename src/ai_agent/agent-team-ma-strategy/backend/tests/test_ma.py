"""Test cases for MA (Moving Average) indicator calculations."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from indicators.ma import calculate_ma, detect_crossover


class TestMACalculation:
    """Test MA calculation functions."""

    def test_ma_calculation_short_window(self):
        """Verify 5-day MA calculation is correct."""
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
                "2024-01-08",
            ],
            "close": [100.0, 105.0, 110.0, 115.0, 120.0, 125.0],
        }
        df = pd.DataFrame(data)
        result = calculate_ma(df, short_window=5, long_window=20)

        assert "ma_5" in result.columns
        assert "ma_20" in result.columns

        expected_ma5_row4 = (100.0 + 105.0 + 110.0 + 115.0 + 120.0) / 5
        assert abs(result.loc[4, "ma_5"] - expected_ma5_row4) < 0.01

    def test_ma_calculation_long_window(self):
        """Verify 20-day MA calculation is correct."""
        data = {
            "date": pd.date_range("2024-01-01", periods=25, freq="D"),
            "close": [100.0 + i * 2 for i in range(25)],
        }
        df = pd.DataFrame(data)
        df["date"] = df["date"].dt.strftime("%Y-%m-%d")
        result = calculate_ma(df, short_window=5, long_window=20)

        assert "ma_20" in result.columns

        expected_ma20 = sum(100.0 + i * 2 for i in range(20)) / 20
        assert abs(result.loc[19, "ma_20"] - expected_ma20) < 0.01


class TestCrossDetection:
    """Test golden cross and death cross detection."""

    def test_golden_cross_detection(self):
        """Verify golden cross is correctly detected."""
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "close": [100.0, 98.0, 96.0, 95.0, 97.0],
        }
        df = pd.DataFrame(data)
        df = calculate_ma(df, short_window=3, long_window=5)
        result = detect_crossover(df, short_col="ma_3", long_col="ma_5")

        golden_crosses = result[result["signal"] == "golden_cross"]
        assert len(golden_crosses) > 0, "Golden cross should be detected"

    def test_death_cross_detection(self):
        """Verify death cross is correctly detected."""
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "close": [100.0, 102.0, 104.0, 103.0, 101.0],
        }
        df = pd.DataFrame(data)
        df = calculate_ma(df, short_window=3, long_window=5)
        result = detect_crossover(df, short_col="ma_3", long_col="ma_5")

        death_crosses = result[result["signal"] == "death_cross"]
        assert len(death_crosses) > 0, "Death cross should be detected"

    def test_no_cross_when_parallel(self):
        """Verify no cross signal when MAs are parallel."""
        prices = [100.0] * 10
        data = {"date": [f"2024-01-{i + 1:02d}" for i in range(10)], "close": prices}
        df = pd.DataFrame(data)
        df = calculate_ma(df, short_window=3, long_window=5)
        result = detect_crossover(df, short_col="ma_3", long_col="ma_5")

        crosses = result[result["signal"].isin(["golden_cross", "death_cross"])]
        assert len(crosses) == 0, "No cross should be detected when MAs are parallel"


class TestMAWithSampleData:
    """Test MA calculations with sample_data.csv."""

    @pytest.fixture
    def sample_df(self):
        """Load sample_data.csv for testing."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        return pd.read_csv(csv_path)

    def test_ma_calculations_match_expected(self, sample_df):
        """Verify MA calculations using sample data."""
        result = calculate_ma(sample_df, short_window=5, long_window=20)

        assert "ma_5" in result.columns
        assert "ma_20" in result.columns
        assert not result["ma_5"].iloc[:4].notna().any()
        assert result["ma_5"].iloc[4:].notna().all()
        assert not result["ma_20"].iloc[:19].notna().any()
        assert result["ma_20"].iloc[19:].notna().all()

    def test_golden_cross_with_sample_data(self, sample_df):
        """Verify golden cross detection in sample data."""
        df = calculate_ma(sample_df, short_window=5, long_window=20)
        result = detect_crossover(df, short_col="ma_5", long_col="ma_20")

        golden_crosses = result[result["signal"] == "golden_cross"]
        assert len(golden_crosses) > 0, "Sample data should contain golden cross"

    def test_death_cross_with_sample_data(self, sample_df):
        """Verify death cross detection in sample data."""
        df = calculate_ma(sample_df, short_window=5, long_window=20)
        result = detect_crossover(df, short_col="ma_5", long_col="ma_20")

        death_crosses = result[result["signal"] == "death_cross"]
        assert len(death_crosses) > 0, "Sample data should contain death cross"
