import pandas as pd

from regime import MarketRegimeClassifier


def test_classify_bull_when_close_above_rising_ma():
    index = pd.date_range("2024-01-05", periods=35, freq="W-FRI")
    benchmark = pd.Series(range(100, 135), index=index, dtype=float)

    classifier = MarketRegimeClassifier(ma_window=30, flat_tolerance=0.01)
    regime = classifier.classify(benchmark)

    assert regime.iloc[-1] == "bull"


def test_classify_bear_when_close_below_falling_ma():
    index = pd.date_range("2024-01-05", periods=35, freq="W-FRI")
    benchmark = pd.Series(range(135, 100, -1), index=index, dtype=float)

    classifier = MarketRegimeClassifier(ma_window=30, flat_tolerance=0.01)
    regime = classifier.classify(benchmark)

    assert regime.iloc[-1] == "bear"


def test_classify_top_when_price_above_ma_but_slope_weakens():
    index = pd.date_range("2024-01-05", periods=35, freq="W-FRI")
    values = [100 + i for i in range(30)] + [129.1, 129.15, 129.2, 129.25, 129.3]
    benchmark = pd.Series(values, index=index, dtype=float)

    classifier = MarketRegimeClassifier(ma_window=30, flat_tolerance=0.05)
    regime = classifier.classify(benchmark)

    assert regime.iloc[-1] == "top"
