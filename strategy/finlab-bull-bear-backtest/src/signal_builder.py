import pandas as pd


class SignalBuilder:
    def __init__(
        self,
        ma_window=30,
        breakout_window=20,
        volume_window=20,
        relative_strength_window=4,
        top_n=10,
        require_52_week_high=False,
    ):
        self.ma_window = ma_window
        self.breakout_window = breakout_window
        self.volume_window = volume_window
        self.relative_strength_window = relative_strength_window
        self.top_n = top_n
        self.require_52_week_high = require_52_week_high

    def select_long_candidates(self, close: pd.DataFrame, volume: pd.DataFrame, benchmark: pd.Series) -> list[str]:
        latest_index = close.index[-1]
        moving_average = close.rolling(self.ma_window, min_periods=self.ma_window).mean().iloc[-1]
        breakout_level = close.shift(1).rolling(self.breakout_window, min_periods=self.breakout_window).max().iloc[-1]
        volume_average = volume.rolling(self.volume_window, min_periods=self.volume_window).mean().iloc[-1]

        stock_returns = close.pct_change(self.relative_strength_window, fill_method=None).iloc[-1]
        benchmark_return = benchmark.pct_change(self.relative_strength_window, fill_method=None).loc[latest_index]
        relative_strength = stock_returns - benchmark_return

        filters = (
            (close.iloc[-1] > moving_average)
            & (close.iloc[-1] > breakout_level)
            & (volume.iloc[-1] > volume_average)
            & (relative_strength > 0)
        )

        if self.require_52_week_high:
            year_high = close.rolling(52, min_periods=52).max().iloc[-1]
            filters &= close.iloc[-1] >= year_high

        selected = relative_strength[filters].sort_values(ascending=False).head(self.top_n)
        return list(selected.index)

    def build_target_weights(
        self,
        close: pd.DataFrame,
        volume: pd.DataFrame,
        benchmark: pd.Series,
        regimes: pd.Series,
    ) -> pd.DataFrame:
        weights = pd.DataFrame(0.0, index=close.index, columns=close.columns)

        for row_number in range(len(close)):
            current_date = close.index[row_number]
            if regimes.loc[current_date] != "bull":
                continue
            if row_number + 1 < max(self.ma_window, self.breakout_window, self.volume_window):
                continue

            sliced_close = close.iloc[: row_number + 1]
            sliced_volume = volume.iloc[: row_number + 1]
            sliced_benchmark = benchmark.iloc[: row_number + 1]
            selected = self.select_long_candidates(sliced_close, sliced_volume, sliced_benchmark)
            if not selected:
                continue

            weight = 1 / len(selected)
            weights.loc[current_date, selected] = weight

        return weights
