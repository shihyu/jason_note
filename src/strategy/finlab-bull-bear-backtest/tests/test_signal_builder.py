import pandas as pd

from signal_builder import SignalBuilder


def test_select_top_10_relative_strength_breakout_stocks():
    index = pd.date_range("2024-01-05", periods=35, freq="W-FRI")
    stock_ids = [f"S{i:02d}" for i in range(12)]

    close = pd.DataFrame(index=index, columns=stock_ids, dtype=float)
    volume = pd.DataFrame(index=index, columns=stock_ids, dtype=float)

    for idx, stock_id in enumerate(stock_ids):
        base = 100 + idx
        series = [base + step * (idx + 1) * 0.3 for step in range(35)]
        close[stock_id] = series
        volume[stock_id] = [1000 + step * (idx + 1) * 10 for step in range(35)]

    benchmark = pd.Series([100 + step * 0.2 for step in range(35)], index=index, dtype=float)

    builder = SignalBuilder(
        ma_window=30,
        breakout_window=20,
        volume_window=20,
        relative_strength_window=4,
        top_n=10,
        require_52_week_high=False,
    )
    selected = builder.select_long_candidates(close, volume, benchmark)

    assert len(selected) == 10
    assert selected[0] == "S11"
    assert selected[-1] == "S02"
