# backend/tests/test_backtest.py
import pytest
import pandas as pd
from backend.backtest.engine import BacktestEngine, run_backtest


def create_test_data_with_signals():
    dates = pd.date_range("2024-01-01", periods=25, freq="D")
    closes = [100] * 20 + [105, 110, 115, 120, 125]
    return pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000000] * 25,
        }
    )


def test_backtest_engine_initialization():
    engine = BacktestEngine(initial_cash=1000000)
    assert engine.initial_cash == 1000000
    assert engine.position == 0
    assert len(engine.trades) == 0


def test_backtest_engine_buy_signal():
    engine = BacktestEngine(initial_cash=100000)
    engine.buy("2024-01-01", 100.0, 1000)
    assert engine.position == 1000
    assert engine.cash == 0


def test_backtest_engine_sell_signal():
    engine = BacktestEngine(initial_cash=100000)
    engine.buy("2024-01-01", 100.0, 1000)
    engine.sell("2024-01-10", 110.0, 1000)
    assert engine.position == 0
    assert engine.cash == 100000 + 10000


def test_run_backtest_with_golden_cross():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    closes = [100] * 20 + [105, 110, 115, 120, 125, 120, 115, 110, 105, 100]
    df = pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000000] * 30,
        }
    )

    result = run_backtest(df, short_window=5, long_window=10)

    assert "total_trades" in result
    assert "win_rate" in result
    assert "total_profit" in result
    assert "max_drawdown" in result
    assert "trades" in result
    assert result["total_trades"] >= 1


def test_backtest_result_format():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    closes = [100] * 20 + [105, 110, 115, 120, 125, 120, 115, 110, 105, 100]
    df = pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000000] * 30,
        }
    )

    result = run_backtest(df, short_window=5, long_window=10)

    for trade in result["trades"]:
        assert "entry_date" in trade
        assert "entry_price" in trade
        assert "exit_date" in trade
        assert "exit_price" in trade
        assert "profit" in trade
        assert trade["type"] in ["golden_cross", "death_cross"]
