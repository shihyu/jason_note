import math

import pandas as pd

from backtest_runner import BacktestRunner
from cost_model import TaiwanStockCostModel


def test_runner_shifts_signal_to_next_bar_and_applies_cost():
    index = pd.date_range("2024-01-05", periods=4, freq="W-FRI")
    prices = pd.DataFrame(
        {
            "AAA": [100.0, 110.0, 121.0, 121.0],
        },
        index=index,
    )
    positions = pd.DataFrame(
        {
            "AAA": [1.0, 1.0, 0.0, 0.0],
        },
        index=index,
    )

    runner = BacktestRunner(cost_model=TaiwanStockCostModel(discount=0.3))
    result = runner.run(positions=positions, prices=prices)

    first_active_date = index[1]
    expected_buy_cost_ratio = 42.75 / 100000

    assert result["positions"].loc[index[0], "AAA"] == 0.0
    assert result["positions"].loc[first_active_date, "AAA"] == 1.0
    assert math.isclose(
        result["strategy_returns"].loc[first_active_date],
        0.10 - expected_buy_cost_ratio,
        rel_tol=1e-9,
    )
    assert "cagr" in result["metrics"]
    assert "max_drawdown" in result["metrics"]
