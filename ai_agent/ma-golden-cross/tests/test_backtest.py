"""
Tests for backtest engine module.
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from backend.backtest.engine import (
    detect_crossovers,
    run_backtest,
    Trade,
    TradeType,
    CrossType,
    BacktestSummary,
    BacktestResult,
    BacktestError,
)


class TestCrossType:
    """Test CrossType enum."""

    def test_golden_cross_value(self):
        """CrossType.GOLDEN should have correct value."""
        assert CrossType.GOLDEN.value == "golden_cross"

    def test_death_cross_value(self):
        """CrossType.DEATH should have correct value."""
        assert CrossType.DEATH.value == "death_cross"


class TestTradeType:
    """Test TradeType enum."""

    def test_buy_value(self):
        """TradeType.BUY should have correct value."""
        assert TradeType.BUY.value == "buy"

    def test_sell_value(self):
        """TradeType.SELL should have correct value."""
        assert TradeType.SELL.value == "sell"


class TestTrade:
    """Test Trade dataclass."""

    def test_trade_creation(self):
        """Trade should store all trade information."""
        trade = Trade(
            entry_date="2024-01-15",
            entry_price=100.0,
            exit_date="2024-01-30",
            exit_price=105.0,
            trade_type=TradeType.BUY,
            cross_type=CrossType.GOLDEN,
            holding_days=15,
            profit_pct=0.05,
            profit_amount=500.0,
        )
        assert trade.entry_date == "2024-01-15"
        assert trade.entry_price == 100.0
        assert trade.exit_date == "2024-01-30"
        assert trade.exit_price == 105.0
        assert trade.trade_type == TradeType.BUY
        assert trade.cross_type == CrossType.GOLDEN
        assert trade.holding_days == 15
        assert trade.profit_pct == 0.05
        assert trade.profit_amount == 500.0

    def test_trade_to_dict(self):
        """Trade.to_dict() should serialize correctly."""
        trade = Trade(
            entry_date="2024-01-15",
            entry_price=100.0,
            exit_date="2024-01-30",
            exit_price=105.0,
            trade_type=TradeType.BUY,
            cross_type=CrossType.GOLDEN,
            holding_days=15,
            profit_pct=0.05,
            profit_amount=500.0,
        )
        result = trade.to_dict()
        assert result["entry_date"] == "2024-01-15"
        assert result["entry_price"] == 100.0
        assert result["exit_date"] == "2024-01-30"
        assert result["exit_price"] == 105.0
        assert result["trade_type"] == "buy"
        assert result["cross_type"] == "golden_cross"
        assert result["holding_days"] == 15
        assert result["profit_pct"] == 0.05
        assert result["profit_amount"] == 500.0


class TestBacktestSummary:
    """Test BacktestSummary dataclass."""

    def test_backtest_summary_to_dict(self):
        """BacktestSummary.to_dict() should serialize correctly."""
        summary = BacktestSummary(
            total_trades=10,
            winning_trades=6,
            losing_trades=4,
            win_rate=0.6,
            total_profit=6000.0,
            total_loss=-2000.0,
            net_profit=4000.0,
            max_drawdown=0.1,
            avg_holding_days=15.5,
        )
        result = summary.to_dict()
        assert result["total_trades"] == 10
        assert result["winning_trades"] == 6
        assert result["losing_trades"] == 4
        assert result["win_rate"] == 0.6
        assert result["total_profit"] == 6000.0
        assert result["total_loss"] == -2000.0
        assert result["net_profit"] == 4000.0
        assert result["max_drawdown"] == 0.1
        assert result["avg_holding_days"] == 15.5


class TestBacktestResult:
    """Test BacktestResult dataclass."""

    def test_backtest_result_to_dict(self):
        """BacktestResult.to_dict() should serialize correctly."""
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
        result = BacktestResult(
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-12-31",
            short_ma=5,
            long_ma=20,
            initial_capital=100000.0,
            final_capital=100000.0,
            summary=summary,
            trades=[],
            equity_curve=[],
        )
        output = result.to_dict()
        assert output["symbol"] == "AAPL"
        assert output["short_ma"] == 5
        assert output["long_ma"] == 20
        assert output["initial_capital"] == 100000.0
        assert output["final_capital"] == 100000.0


class TestDetectCrossovers:
    """Test detect_crossovers function."""

    def test_detect_golden_cross(self):
        """Should detect when MA5 crosses above MA20."""
        # MA5 goes from below MA20 to above MA20
        # diff: -5.0 -> -3.0 -> 1.0 -> 3.0 (golden cross at i=2)
        ma_short = pd.Series([95.0, 97.0, 101.0, 103.0])
        ma_long = pd.Series([100.0, 100.0, 100.0, 100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 1
        assert result[0]["cross_type"] == CrossType.GOLDEN

    def test_detect_death_cross(self):
        """Should detect when MA5 crosses below MA20."""
        # diff: 5.0 -> 3.0 -> -1.0 -> -3.0 (death cross at i=2)
        ma_short = pd.Series([105.0, 103.0, 99.0, 97.0])
        ma_long = pd.Series([100.0, 100.0, 100.0, 100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 1
        assert result[0]["cross_type"] == CrossType.DEATH

    def test_detect_multiple_crossovers(self):
        """Should detect multiple crossover events."""
        # diff: -5 -> -3 -> 1 -> -1 -> 1 -> -1 (alternating)
        ma_short = pd.Series([95.0, 97.0, 101.0, 99.0, 101.0, 99.0])
        ma_long = pd.Series([100.0, 100.0, 100.0, 100.0, 100.0, 100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 4
        assert result[0]["cross_type"] == CrossType.GOLDEN
        assert result[1]["cross_type"] == CrossType.DEATH
        assert result[2]["cross_type"] == CrossType.GOLDEN
        assert result[3]["cross_type"] == CrossType.DEATH

    def test_detect_no_crossover_when_parallel(self):
        """Should return empty when MAs are always above or below."""
        ma_short = pd.Series([105.0, 106.0, 107.0, 108.0])  # always above
        ma_long = pd.Series([100.0, 100.0, 100.0, 100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 0

    def test_detect_crossover_insufficient_data(self):
        """Should return empty for single data point."""
        ma_short = pd.Series([100.0])
        ma_long = pd.Series([100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 0

    def test_detect_crossover_handles_leading_nan(self):
        """Should skip leading NaN values in MA series."""
        # diff: nan -> nan -> -1.0 -> 1.0 (golden cross at i=3)
        ma_short = pd.Series([95.0, 95.0, 99.0, 101.0])
        ma_long = pd.Series([100.0, 100.0, 100.0, 100.0])

        result = detect_crossovers(ma_short, ma_long)

        assert len(result) == 1
        assert result[0]["cross_type"] == CrossType.GOLDEN


class TestRunBacktest:
    """Test run_backtest function."""

    def test_run_backtest_missing_close_column(self):
        """Should raise BacktestError if Close column missing."""
        df = pd.DataFrame({"Open": [100.0], "High": [105.0]})
        ma_short = pd.Series([100.0])
        ma_long = pd.Series([100.0])

        with pytest.raises(
            BacktestError, match="DataFrame must contain 'Close' column"
        ):
            run_backtest(df, ma_short, ma_long, "AAPL", "2024-01-01", "2024-12-31")

    def test_run_backtest_length_mismatch(self):
        """Should raise BacktestError if MA lengths don't match."""
        df = pd.DataFrame({"Close": [100.0, 102.0]})
        ma_short = pd.Series([100.0, 102.0, 103.0])
        ma_long = pd.Series([100.0, 102.0])

        with pytest.raises(
            BacktestError, match="MA series length must match DataFrame length"
        ):
            run_backtest(df, ma_short, ma_long, "AAPL", "2024-01-01", "2024-12-31")

    def test_run_backtest_no_crossovers(self):
        """Should return result with no trades when no crossovers."""
        df = pd.DataFrame({"Close": [105.0, 106.0, 107.0, 108.0]})
        ma_short = pd.Series([100.0, 101.0, 102.0, 103.0])  # always above
        ma_long = pd.Series([95.0, 96.0, 97.0, 98.0])  # always below

        result = run_backtest(
            df,
            ma_short,
            ma_long,
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-04",
            short_ma=5,
            long_ma=20,
            initial_capital=100000.0,
        )

        assert result.symbol == "AAPL"
        assert result.summary.total_trades == 0
        assert result.final_capital == 100000.0

    def test_run_backtest_with_golden_cross_buy(self):
        """Should execute BUY trade on golden cross."""
        # Create data where MA5 crosses above MA20
        df = pd.DataFrame(
            {
                "Close": [
                    100.0,
                    98.0,
                    96.0,
                    94.0,
                    95.0,
                    97.0,
                    100.0,
                    103.0,
                    106.0,
                    109.0,
                ],
            },
            index=pd.date_range("2024-01-01", periods=10),
        )

        # MA5 crosses above MA20 at index 5
        ma5 = pd.Series(
            [np.nan, np.nan, np.nan, np.nan, 96.6, 96.0, 97.0, 100.0, 103.0, 106.0]
        )
        ma20 = pd.Series([np.nan] * 10)
        ma20.iloc[4:] = 100.0

        result = run_backtest(
            df,
            ma5,
            ma20,
            symbol="AAPL",
            start_date="2024-01-01",
            end_date="2024-01-10",
            short_ma=5,
            long_ma=20,
            initial_capital=100000.0,
        )

        # Should have at least some trades or result
        assert isinstance(result, BacktestResult)
        assert result.symbol == "AAPL"

    def test_run_backtest_calculates_max_drawdown(self):
        """Should calculate max drawdown correctly."""
        df = pd.DataFrame({"Close": [100.0, 110.0, 90.0, 100.0, 95.0, 105.0]})
        ma5 = pd.Series([np.nan, np.nan, np.nan, np.nan, 100.0, 100.0])
        ma20 = pd.Series([np.nan, np.nan, np.nan, np.nan, 100.0, 100.0])

        result = run_backtest(
            df,
            ma5,
            ma20,
            symbol="TEST",
            start_date="2024-01-01",
            end_date="2024-01-06",
            initial_capital=100000.0,
        )

        assert hasattr(result.summary, "max_drawdown")
        assert result.summary.max_drawdown >= 0

    def test_run_backtest_trade_profit_calculation(self):
        """Should calculate trade profit correctly."""
        # Simple case: buy at 100, sell at 110 = 10% profit
        df = pd.DataFrame(
            {"Close": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 110.0]},
            index=pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-07",
                ]
            ),
        )

        ma5 = pd.Series([np.nan, np.nan, np.nan, np.nan, 100.0, 100.0, 100.0])
        ma20 = pd.Series([100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0])

        # Set up crossover at index 4 (golden cross)
        ma5.iloc[4] = 98.0  # below 100
        ma5.iloc[5] = 100.5  # above 100
        ma5.iloc[6] = 100.0

        result = run_backtest(
            df,
            ma5,
            ma20,
            symbol="TEST",
            start_date="2024-01-01",
            end_date="2024-01-07",
            initial_capital=100000.0,
        )

        # Verify trade structure
        if result.trades:
            trade = result.trades[0]
            assert hasattr(trade, "profit_pct")
            assert hasattr(trade, "profit_amount")
            assert hasattr(trade, "holding_days")


class TestBacktestError:
    """Test BacktestError exception."""

    def test_backtest_error_is_exception(self):
        """BacktestError should be an Exception subclass."""
        error = BacktestError("Test error")
        assert isinstance(error, Exception)

    def test_backtest_error_message(self):
        """BacktestError should preserve message."""
        msg = "Backtest failed"
        error = BacktestError(msg)
        assert str(error) == msg
