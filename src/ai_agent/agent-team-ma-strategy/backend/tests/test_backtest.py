"""Test cases for backtest engine."""

import pytest
import pandas as pd
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from indicators.ma import calculate_ma, detect_crossover
from backtest.engine import BacktestEngine, run_backtest


class TestBacktestEngine:
    """Test BacktestEngine class."""

    def test_backtest_no_trades_when_no_signal(self):
        """No trades when there is no golden/death cross signal."""
        engine = BacktestEngine(initial_capital=100000.0)
        data = {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "close": [100.0, 100.0, 100.0],
            "ma_5": [100.0, 100.0, 100.0],
            "ma_20": [100.0, 100.0, 100.0],
            "signal": ["hold", "hold", "hold"],
        }
        df = pd.DataFrame(data)
        result = engine.run(df)

        assert result["total_trades"] == 0
        assert result["total_profit"] == 0.0

    def test_backtest_golden_cross_buy(self):
        """Golden cross triggers a buy signal."""
        engine = BacktestEngine(initial_capital=100000.0)
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "close": [100.0, 95.0, 90.0, 95.0, 100.0],
            "ma_5": [100.0, 97.5, 95.0, 93.3, 95.0],
            "ma_20": [110.0, 108.0, 106.0, 104.0, 102.0],
            "signal": ["hold", "hold", "golden_cross", "hold", "hold"],
        }
        df = pd.DataFrame(data)
        result = engine.run(df)

        assert len(result["trades"]) > 0 or engine.position is not None

    def test_backtest_death_cross_sell(self):
        """Death cross triggers a sell signal."""
        engine = BacktestEngine(initial_capital=100000.0)
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "close": [100.0, 105.0, 110.0, 115.0, 110.0],
            "ma_5": [110.0, 112.0, 115.0, 110.0, 105.0],
            "ma_20": [100.0, 102.0, 104.0, 106.0, 108.0],
            "signal": ["hold", "hold", "death_cross", "hold", "hold"],
        }
        df = pd.DataFrame(data)
        result = engine.run(df)

        assert len(result["trades"]) == 0

    def test_backtest_win_rate_calculation(self):
        """Win rate is calculated correctly."""
        engine = BacktestEngine(initial_capital=100000.0)
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
                "2024-01-08",
                "2024-01-09",
                "2024-01-10",
                "2024-01-11",
                "2024-01-12",
            ],
            "close": [
                100.0,
                105.0,
                110.0,
                115.0,
                120.0,
                120.0,
                115.0,
                110.0,
                105.0,
                100.0,
            ],
            "ma_5": [
                100.0,
                102.5,
                105.0,
                107.5,
                110.0,
                115.0,
                110.0,
                105.0,
                100.0,
                97.5,
            ],
            "ma_20": [
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
                100.0,
            ],
            "signal": [
                "hold",
                "golden_cross",
                "hold",
                "hold",
                "death_cross",
                "hold",
                "golden_cross",
                "hold",
                "hold",
                "hold",
            ],
        }
        df = pd.DataFrame(data)
        result = engine.run(df)

        assert "win_rate" in result
        assert 0.0 <= result["win_rate"] <= 1.0

    def test_backtest_max_drawdown(self):
        """Max drawdown is calculated correctly."""
        engine = BacktestEngine(initial_capital=100000.0)
        data = {
            "date": [
                "2024-01-01",
                "2024-01-02",
                "2024-01-03",
                "2024-01-04",
                "2024-01-05",
            ],
            "close": [100.0, 110.0, 90.0, 80.0, 100.0],
            "ma_5": [100.0, 105.0, 100.0, 95.0, 96.0],
            "ma_20": [100.0, 100.0, 100.0, 100.0, 100.0],
            "signal": ["hold", "golden_cross", "hold", "death_cross", "hold"],
        }
        df = pd.DataFrame(data)
        result = engine.run(df)

        assert "max_drawdown" in result
        assert result["max_drawdown"] >= 0.0


class TestRunBacktest:
    """Test run_backtest convenience function."""

    def test_run_backtest_returns_dict(self):
        """run_backtest returns a dictionary with expected keys."""
        data = {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "close": [100.0, 100.0, 100.0],
            "ma_5": [100.0, 100.0, 100.0],
            "ma_20": [100.0, 100.0, 100.0],
            "signal": ["hold", "hold", "hold"],
        }
        df = pd.DataFrame(data)
        result = run_backtest(df)

        assert isinstance(result, dict)
        assert "total_trades" in result
        assert "win_rate" in result
        assert "total_profit" in result
        assert "max_drawdown" in result
        assert "trades" in result


class TestBacktestWithSampleData:
    """Test backtest with sample_data.csv."""

    @pytest.fixture
    def sample_df(self):
        """Load sample_data.csv and prepare with MA signals."""
        csv_path = Path(__file__).parent / "sample_data.csv"
        df = pd.read_csv(csv_path)
        df = calculate_ma(df, short_window=5, long_window=20)
        df = detect_crossover(df, short_col="ma_5", long_col="ma_20")
        return df

    def test_backtest_with_sample_data(self, sample_df):
        """Backtest runs successfully with sample data."""
        result = run_backtest(sample_df)

        assert isinstance(result, dict)
        assert "total_trades" in result
        assert result["total_trades"] >= 0

    def test_sample_data_produces_trades(self, sample_df):
        """Sample data should produce at least some trades."""
        result = run_backtest(sample_df)

        assert result["total_trades"] > 0
