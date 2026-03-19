from __future__ import annotations

import pandas as pd


class DataLoader:
    def __init__(self, start_date="2020-01-01", end_date=None):
        self.start_date = pd.Timestamp(start_date)
        self.end_date = pd.Timestamp(end_date) if end_date else None

    def load_weekly_data(self) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
        try:
            from finlab import data
        except ImportError as exc:
            raise RuntimeError("缺少 finlab 套件，無法載入回測資料。") from exc

        close = data.get("price:收盤價")
        volume = data.get("price:成交股數")
        benchmark = data.get("benchmark_return:發行量加權股價報酬指數")

        if isinstance(benchmark, pd.DataFrame):
            benchmark = benchmark.iloc[:, 0]

        close = self._filter_dates(close)
        volume = self._filter_dates(volume)
        benchmark = self._filter_dates(benchmark)

        weekly_close = close.resample("W-FRI").last().dropna(how="all")
        weekly_volume = volume.resample("W-FRI").sum().reindex(weekly_close.index)
        weekly_benchmark = benchmark.resample("W-FRI").last().reindex(weekly_close.index)
        return weekly_close, weekly_volume, weekly_benchmark

    def _filter_dates(self, frame):
        filtered = frame[frame.index >= self.start_date]
        if self.end_date is not None:
            filtered = filtered[filtered.index <= self.end_date]
        return filtered
