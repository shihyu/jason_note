import pandas as pd


class MarketRegimeClassifier:
    def __init__(self, ma_window=30, flat_tolerance=0.01):
        self.ma_window = ma_window
        self.flat_tolerance = flat_tolerance

    def classify(self, benchmark_close: pd.Series) -> pd.Series:
        benchmark_close = benchmark_close.astype(float)
        moving_average = benchmark_close.rolling(self.ma_window, min_periods=self.ma_window).mean()
        slope = moving_average.diff()
        short_term_slope = benchmark_close.diff(4) / 4

        regime = pd.Series("base", index=benchmark_close.index, dtype="object")

        bull_mask = (
            (benchmark_close > moving_average)
            & (slope > self.flat_tolerance)
            & (short_term_slope > self.flat_tolerance * 2)
        )
        bear_mask = (benchmark_close < moving_average) & (slope < -self.flat_tolerance)
        top_mask = (benchmark_close > moving_average) & ~bull_mask
        base_mask = (benchmark_close <= moving_average) & ~bear_mask

        regime.loc[bull_mask] = "bull"
        regime.loc[bear_mask] = "bear"
        regime.loc[top_mask] = "top"
        regime.loc[base_mask] = "base"
        regime.loc[moving_average.isna()] = "base"
        return regime
