"""
測試策略邏輯
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from strategy import PairsTradingStrategy, StrategyParams, Trade, Position


def create_test_data():
    """建立測試數據"""
    symbols = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT"]
    timestamps = [datetime(2023, 1, 1, 0, i) for i in range(10)]

    rows = []
    for ts in timestamps:
        base_price = 100
        for i, sym in enumerate(symbols):
            volatility = (i + 1) * 0.001
            open_p = base_price + np.random.randn() * 5
            high_p = open_p + abs(np.random.randn()) * 10 * volatility
            low_p = open_p - abs(np.random.randn()) * 10 * volatility
            close_p = open_p + np.random.randn() * 5

            rows.append(
                {
                    "symbol": sym,
                    "open_time": ts,
                    "open": open_p,
                    "high": high_p,
                    "low": low_p,
                    "close": close_p,
                    "volume": 1000,
                }
            )

    return pd.DataFrame(rows)


class TestPairsTradingStrategy:
    def test_strategy_init(self):
        params = StrategyParams(entry_amp=0.005, top_n=5)
        strategy = PairsTradingStrategy(params)

        assert strategy.params.entry_amp == 0.005
        assert strategy.params.top_n == 5
        assert len(strategy.positions) == 0
        assert len(strategy.trades) == 0

    def test_calculate_amplitude(self):
        strategy = PairsTradingStrategy()
        df = pd.DataFrame(
            {
                "high": [105, 110, 103],
                "low": [100, 100, 100],
                "close": [102, 105, 101],
                "open": [101, 103, 100],
                "symbol": ["A", "B", "C"],
                "open_time": [datetime.now()] * 3,
            }
        )

        amp = strategy.calculate_amplitude(df)
        assert amp.iloc[0] == pytest.approx(0.05, rel=0.01)
        assert amp.iloc[1] == pytest.approx(0.10, rel=0.01)
        assert amp.iloc[2] == pytest.approx(0.03, rel=0.01)

    def test_rank_by_amplitude(self):
        strategy = PairsTradingStrategy()
        df = pd.DataFrame(
            {
                "high": [105, 110, 103],
                "low": [100, 100, 100],
                "close": [102, 105, 101],
                "open": [101, 103, 100],
                "symbol": ["A", "B", "C"],
                "open_time": [datetime.now()] * 3,
            }
        )

        ranked = strategy.rank_by_amplitude(df)
        assert "amplitude" in ranked.columns
        assert "rank" in ranked.columns

        assert ranked[ranked["symbol"] == "B"]["rank"].iloc[0] == 1
        assert ranked[ranked["symbol"] == "A"]["rank"].iloc[0] == 2
        assert ranked[ranked["symbol"] == "C"]["rank"].iloc[0] == 3

    def test_check_exit_exit_amp(self):
        params = StrategyParams(
            entry_amp=0.01, exit_amp_ratio=0.33, stop_loss_ratio=2.0, max_hold=5
        )
        strategy = PairsTradingStrategy(params)

        pos = Position(
            symbol="BTCUSDT",
            side="long",
            entry_time=datetime.now(),
            entry_price=100,
            entry_amp=0.01,
            bar_count=0,
        )

        row = pd.Series({"amplitude": 0.003})
        should_exit, reason = strategy.check_exit(row, pos)
        assert should_exit
        assert reason == "exit_amp"

    def test_check_exit_stop_loss(self):
        params = StrategyParams(
            entry_amp=0.01, exit_amp_ratio=0.33, stop_loss_ratio=2.0, max_hold=5
        )
        strategy = PairsTradingStrategy(params)

        pos = Position(
            symbol="BTCUSDT",
            side="long",
            entry_time=datetime.now(),
            entry_price=100,
            entry_amp=0.01,
            bar_count=0,
        )

        row = pd.Series({"amplitude": 0.025})
        should_exit, reason = strategy.check_exit(row, pos)
        assert should_exit
        assert reason == "stop_loss"

    def test_check_exit_max_hold(self):
        params = StrategyParams(
            entry_amp=0.01, exit_amp_ratio=0.33, stop_loss_ratio=2.0, max_hold=3
        )
        strategy = PairsTradingStrategy(params)

        pos = Position(
            symbol="BTCUSDT",
            side="long",
            entry_time=datetime.now(),
            entry_price=100,
            entry_amp=0.01,
            bar_count=3,
        )

        row = pd.Series({"amplitude": 0.005})
        should_exit, reason = strategy.check_exit(row, pos)
        assert should_exit
        assert reason == "max_hold"

    def test_run_no_trades(self):
        params = StrategyParams(entry_amp=1.0)
        strategy = PairsTradingStrategy(params)
        df = create_test_data()

        trades = strategy.run(df)
        assert isinstance(trades, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
