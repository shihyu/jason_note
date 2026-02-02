"""
策略3：綜合法

選股邏輯：
結合策略 1 和策略 2 的條件：
1. 族群相對強弱排名 Top 30%（放寬篩選）
2. 族群同步性 ≥ 30%
3. 族群 3 日平均成交金額 > 前 20 日均值（量能確認）
4. 個股條件：補漲股技術條件（同策略2）

權重分配：
- 等權重持有通過條件的前 15 檔股票
"""
import pandas as pd
import numpy as np
from finlab import data
from data_loader import DataLoader
from strategy1_relative_strength import RelativeStrengthStrategy
from strategy2_synchronization import SynchronizationStrategy
from backtest_utils import BacktestEngine


class CombinedStrategy:
    """綜合策略（結合策略1和策略2）"""

    def __init__(self, loader: DataLoader):
        """
        初始化策略

        Args:
            loader: DataLoader 實例
        """
        self.loader = loader
        # 整合策略 1 和策略 2
        self.strategy1 = RelativeStrengthStrategy(loader)
        self.strategy2 = SynchronizationStrategy(loader)

    def calculate_sector_volume(self):
        """
        計算各族群的成交金額

        Returns:
            dict: {族群名稱: Series(日期, 成交金額)}
        """
        categories = self.loader.get_categories()
        sector_volumes = {}

        for cat in categories:
            with data.universe(category=[cat]):
                try:
                    sector_close = data.get('price:收盤價')
                    sector_volume = data.get('price:成交股數')

                    # 過濾起始日期
                    sector_close = sector_close[sector_close.index >= self.loader.start_date]
                    sector_volume = sector_volume[sector_volume.index >= self.loader.start_date]

                    # 計算成交金額 = 收盤價 * 成交股數
                    # 對每個股票計算，然後加總
                    sector_amount = (sector_close * sector_volume).sum(axis=1)

                    sector_volumes[cat] = sector_amount

                except Exception as e:
                    print(f"警告：{cat} 族群成交金額計算失敗 - {e}")
                    continue

        return sector_volumes

    def identify_volume_confirmed_sectors(self, date, volume_period=3, ma_period=20):
        """
        識別量能確認的族群（近 N 日平均成交金額 > 前 M 日均值）

        Args:
            date: 指定日期
            volume_period: 近期平均週期（預設 3 日）
            ma_period: 均量週期（預設 20 日）

        Returns:
            list: 量能確認的族群名稱
        """
        sector_volumes = self.calculate_sector_volume()
        confirmed = []

        for cat, vol_series in sector_volumes.items():
            try:
                # 確保日期存在
                if date not in vol_series.index:
                    valid_dates = vol_series.index[vol_series.index <= date]
                    if len(valid_dates) == 0:
                        continue
                    date = valid_dates[-1]

                # 計算近 N 日平均成交金額
                recent_vol = vol_series.loc[:date].tail(volume_period).mean()

                # 計算前 M 日均量
                vol_ma = vol_series.rolling(ma_period).mean()

                if date in vol_ma.index:
                    vol_ma_value = vol_ma.loc[date]

                    # 量能確認：近期平均 > 均量
                    if pd.notna(recent_vol) and pd.notna(vol_ma_value) and recent_vol > vol_ma_value:
                        confirmed.append(cat)

            except (KeyError, IndexError):
                continue

        return confirmed

    def filter_qualified_sectors(self, date, rs_period=10, rs_top_pct=0.3,
                                 sync_threshold=0.3, volume_period=3):
        """
        篩選符合所有條件的族群

        Args:
            date: 指定日期
            rs_period: RS 計算週期
            rs_top_pct: RS 排名百分比（預設 0.3 = Top 30%）
            sync_threshold: 同步性閾值（預設 0.3 = 30%）
            volume_period: 量能平均週期（預設 3 日）

        Returns:
            list: 符合所有條件的族群名稱
        """
        # 條件 1：相對強弱 Top 30%
        rs = self.strategy1.calculate_relative_strength(period=rs_period)
        ranked_rs = self.strategy1.rank_sectors_by_rs(rs, date=date)
        top_rs_sectors = self.strategy1.select_top_sectors(ranked_rs, top_pct=rs_top_pct)

        # 條件 2：同步性 >= 30%
        sync_ratios = self.strategy2.calculate_sector_sync_ratio(ma_period=20)
        activated_sectors = self.strategy2.identify_activated_sectors(
            sync_ratios, date=date, threshold=sync_threshold
        )

        # 條件 3：量能確認
        volume_confirmed = self.identify_volume_confirmed_sectors(
            date=date, volume_period=volume_period, ma_period=20
        )

        # 取交集（所有條件都滿足的族群）
        qualified = list(set(top_rs_sectors) & set(activated_sectors) & set(volume_confirmed))

        return qualified

    def select_combined_stocks(self, sectors, date, n_stocks=15):
        """
        從符合條件的族群中選擇補漲股

        Args:
            sectors: 符合條件的族群列表
            date: 選股日期
            n_stocks: 選股數量

        Returns:
            list: 選中的股票代碼
        """
        # 使用策略 2 的補漲股邏輯
        stocks = self.strategy2.identify_catchup_stocks(
            sectors=sectors,
            date=date,
            ma_period=20,
            n_stocks=n_stocks
        )

        return stocks

    def generate_signals(self, rs_period=10, rs_top_pct=0.3, sync_threshold=0.3,
                        volume_period=3, n_stocks=15, start_date=None, end_date=None):
        """
        生成月度交易訊號

        Args:
            rs_period: RS 計算週期
            rs_top_pct: RS 排名百分比
            sync_threshold: 同步性閾值
            volume_period: 量能平均週期
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            DataFrame: 交易訊號（index=日期, columns=股票代碼, value=1持有/0不持有）
        """
        # 取得所有可能的交易日
        close = self.loader.get_close_price()
        all_dates = close.index

        if start_date:
            all_dates = all_dates[all_dates >= pd.to_datetime(start_date)]
        if end_date:
            all_dates = all_dates[all_dates <= pd.to_datetime(end_date)]

        # 生成月初日期（每月第一個交易日）
        dates_series = pd.Series(all_dates, index=all_dates)
        rebalance_dates = dates_series.resample('MS').first().dropna()

        # 生成訊號
        signals_list = []

        for rb_date in rebalance_dates:
            # 篩選符合條件的族群
            qualified = self.filter_qualified_sectors(
                date=rb_date,
                rs_period=rs_period,
                rs_top_pct=rs_top_pct,
                sync_threshold=sync_threshold,
                volume_period=volume_period
            )

            # 從符合條件的族群中選股
            if len(qualified) > 0:
                stocks = self.select_combined_stocks(qualified, rb_date, n_stocks)
            else:
                stocks = []

            # 記錄訊號
            signals_list.append({
                'date': rb_date,
                'stocks': stocks
            })

        # 轉換為 DataFrame
        if len(signals_list) == 0:
            return pd.DataFrame()

        # 建立完整訊號矩陣
        all_stocks = list(set([s for sig in signals_list for s in sig['stocks']]))

        if len(all_stocks) == 0:
            return pd.DataFrame()

        signals = pd.DataFrame(0, index=all_dates, columns=all_stocks)

        # 填充訊號
        for sig in signals_list:
            rb_date = sig['date']
            stocks = sig['stocks']

            if len(stocks) == 0:
                continue

            # 從 rebalance 日期開始持有，直到下一個 rebalance 日期
            next_dates = rebalance_dates[rebalance_dates > rb_date]
            if len(next_dates) > 0:
                end = next_dates.iloc[0]
            else:
                end = all_dates[-1]

            # 設定持有訊號
            mask = (signals.index >= rb_date) & (signals.index < end)
            signals.loc[mask, stocks] = 1

        signals.index.name = 'date'

        return signals

    def backtest(self, rs_period=10, rs_top_pct=0.3, sync_threshold=0.3,
                volume_period=3, n_stocks=15, start_date=None, end_date=None):
        """
        執行回測（修正版：避免 Look-ahead Bias + 扣除交易成本）

        Args:
            rs_period: RS 計算週期
            rs_top_pct: RS 排名百分比
            sync_threshold: 同步性閾值
            volume_period: 量能平均週期
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            dict: 回測結果
        """
        # 生成訊號
        signals = self.generate_signals(
            rs_period, rs_top_pct, sync_threshold, volume_period, n_stocks,
            start_date, end_date
        )

        # 載入收盤價
        close = self.loader.get_close_price()

        # 使用修正後的回測引擎
        engine = BacktestEngine()
        result = engine.backtest_with_cost(signals, close, verbose=False)

        return result
