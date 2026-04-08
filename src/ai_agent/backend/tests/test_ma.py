# backend/tests/test_ma.py
import pytest
import pandas as pd
import numpy as np
from backend.indicators.ma import calculate_ma, detect_crossover


def create_test_data():
    dates = pd.date_range("2024-01-01", periods=30, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            "open": [100 + i for i in range(30)],
            "high": [102 + i for i in range(30)],
            "low": [98 + i for i in range(30)],
            "close": [101 + i for i in range(30)],
            "volume": [1000000] * 30,
        }
    )


def test_calculate_ma_short():
    df = create_test_data()
    result = calculate_ma(df, short_window=5, long_window=20)

    assert pd.isna(result["ma_short"].iloc[0])
    assert pd.isna(result["ma_short"].iloc[3])
    assert not pd.isna(result["ma_short"].iloc[4])
    assert result["ma_short"].iloc[4] == pytest.approx(103.0)


def test_calculate_ma_long():
    df = create_test_data()
    result = calculate_ma(df, short_window=5, long_window=20)

    assert pd.isna(result["ma_long"].iloc[0])
    assert pd.isna(result["ma_long"].iloc[18])
    assert not pd.isna(result["ma_long"].iloc[19])


def test_detect_golden_cross():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    closes = [100, 95, 90, 85, 80, 85, 90, 95, 100, 105]
    df = pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000000] * 10,
        }
    )

    result = calculate_ma(df, short_window=3, long_window=5)
    crossovers = detect_crossover(result)

    golden_crosses = [c for c in crossovers if c["type"] == "golden_cross"]
    assert len(golden_crosses) >= 1


def test_detect_death_cross():
    dates = pd.date_range("2024-01-01", periods=10, freq="D")
    closes = [80, 85, 90, 95, 100, 95, 90, 85, 80, 75]
    df = pd.DataFrame(
        {
            "date": dates,
            "open": closes,
            "high": closes,
            "low": closes,
            "close": closes,
            "volume": [1000000] * 10,
        }
    )

    result = calculate_ma(df, short_window=3, long_window=5)
    crossovers = detect_crossover(result)

    death_crosses = [c for c in crossovers if c["type"] == "death_cross"]
    assert len(death_crosses) >= 1
