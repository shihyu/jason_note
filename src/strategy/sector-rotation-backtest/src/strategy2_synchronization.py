"""
策略2：族群同步性法

選股邏輯：
1. 計算每個族群內「站上 20MA 的股票比例」
2. 當比例 ≥ 30% 時，判定族群啟動
3. 在啟動族群中選擇「尚未創高但 RS 剛翻正」的補漲股
4. 補漲股定義：
   - 價格未創 20 日新高
   - 近 5 日報酬 > 大盤同期報酬（RS 翻正）
   - 價格位於季線（60MA）～半年線（120MA）之間
   - 成交量 > 20 日均量
"""
import pandas as pd
import numpy as np
from finlab import data
from data_loader import DataLoader
from backtest_utils import BacktestEngine


class SynchronizationStrategy:
    """族群同步性策略"""

    def __init__(self, loader: DataLoader):
        """
        初始化策略

        Args:
            loader: DataLoader 實例
        """
        self.loader = loader

    def calculate_ma(self, close, period=20):
        """
        計算移動平均線

        Args:
            close: 收盤價 DataFrame
            period: 週期（天數）

        Returns:
            DataFrame: 移動平均線
        """
        return close.rolling(period).mean()

    def calculate_sector_sync_ratio(self, ma_period=20):
        """
        計算各族群的同步性比例（站上 MA 的股票比例）

        Args:
            ma_period: 移動平均線週期

        Returns:
            dict: {族群名稱: Series(日期, 同步性比例)}
        """
        categories = self.loader.get_categories()
        sync_ratios = {}

        for cat in categories:
            with data.universe(category=[cat]):
                try:
                    sector_close = data.get('price:收盤價')

                    # 過濾起始日期
                    sector_close = sector_close[sector_close.index >= self.loader.start_date]

                    # 計算 MA
                    ma = self.calculate_ma(sector_close, period=ma_period)

                    # 計算站上 MA 的股票比例
                    above_ma = (sector_close > ma)
                    sync_ratio = above_ma.mean(axis=1)  # 橫向平均（每日的比例）

                    sync_ratios[cat] = sync_ratio

                except Exception as e:
                    print(f"警告：{cat} 族群同步性計算失敗 - {e}")
                    continue

        return sync_ratios

    def identify_activated_sectors(self, sync_ratios, date, threshold=0.3):
        """
        識別啟動的族群（同步性 >= 閾值）

        Args:
            sync_ratios: calculate_sector_sync_ratio 的返回值
            date: 指定日期
            threshold: 同步性閾值（預設 0.3 = 30%）

        Returns:
            list: 啟動的族群名稱
        """
        activated = []

        for cat, ratio_series in sync_ratios.items():
            try:
                # 取得該日期的同步性比例
                if date in ratio_series.index:
                    ratio = ratio_series.loc[date]
                else:
                    # 找最接近的日期
                    valid_dates = ratio_series.index[ratio_series.index <= date]
                    if len(valid_dates) == 0:
                        continue
                    ratio = ratio_series.loc[valid_dates[-1]]

                # 判斷是否啟動
                if pd.notna(ratio) and ratio >= threshold:
                    activated.append(cat)

            except (KeyError, IndexError):
                continue

        return activated

    def calculate_stock_rs(self, period=5):
        """
        計算個股相對強度（個股報酬 - 大盤報酬）

        Args:
            period: 計算週期（天數）

        Returns:
            DataFrame: 個股 RS（index=日期, columns=股票代碼）
        """
        close = self.loader.get_close_price()
        benchmark = self.loader.get_benchmark_return()

        # 計算個股報酬
        stock_returns = close.pct_change(period, fill_method=None)

        # 計算大盤報酬
        benchmark_ret = benchmark.pct_change(period)

        # 計算相對強度
        rs = stock_returns.sub(benchmark_ret, axis=0)

        return rs

    def identify_catchup_stocks(self, sectors, date, ma_period=20, n_stocks=15):
        """
        從指定族群中識別補漲股

        Args:
            sectors: 族群名稱列表
            date: 選股日期
            ma_period: 移動平均線週期
            n_stocks: 選股數量

        Returns:
            list: 補漲股代碼列表
        """
        close = self.loader.get_close_price()
        volume = self.loader.get_volume()

        # 確保日期存在
        if date not in close.index:
            valid_dates = close.index[close.index <= date]
            if len(valid_dates) == 0:
                return []
            date = valid_dates[-1]

        # 計算技術指標
        ma20 = self.calculate_ma(close, period=20)
        ma60 = self.calculate_ma(close, period=60)
        ma120 = self.calculate_ma(close, period=120)
        high20 = close.rolling(20).max()
        vol_ma20 = volume.rolling(20).mean()

        # 計算個股 RS
        stock_rs = self.calculate_stock_rs(period=5)

        # 收集所有族群的股票
        all_stocks = []

        for cat in sectors:
            with data.universe(category=[cat]):
                try:
                    sector_close = data.get('price:收盤價')
                    stock_list = sector_close.columns.tolist()
                    all_stocks.extend(stock_list)
                except:
                    continue

        # 去重
        all_stocks = list(set(all_stocks))

        # 篩選補漲股
        catchup_stocks = []

        for stock in all_stocks:
            if stock not in close.columns:
                continue

            try:
                # 取得該股票的數據
                stock_close = close.loc[date, stock]
                stock_high20 = high20.loc[date, stock] if stock in high20.columns else np.nan
                stock_ma60 = ma60.loc[date, stock] if stock in ma60.columns else np.nan
                stock_ma120 = ma120.loc[date, stock] if stock in ma120.columns else np.nan
                stock_volume = volume.loc[date, stock] if stock in volume.columns else np.nan
                stock_vol_ma20 = vol_ma20.loc[date, stock] if stock in vol_ma20.columns else np.nan
                stock_rs_value = stock_rs.loc[date, stock] if stock in stock_rs.columns else np.nan

                # 條件 1：未創 20 日新高
                cond1 = pd.notna(stock_high20) and stock_close < stock_high20

                # 條件 2：RS 翻正（近 5 日報酬 > 大盤）
                cond2 = pd.notna(stock_rs_value) and stock_rs_value > 0

                # 條件 3：價格位於季線～半年線之間
                cond3 = (pd.notna(stock_ma60) and pd.notna(stock_ma120) and
                        stock_close > stock_ma60 and stock_close < stock_ma120)

                # 條件 4：成交量 > 20 日均量
                cond4 = pd.notna(stock_vol_ma20) and stock_volume > stock_vol_ma20

                # 全部條件滿足
                if cond1 and cond2 and cond3 and cond4:
                    catchup_stocks.append(stock)

            except (KeyError, IndexError):
                continue

        # 限制數量
        return catchup_stocks[:n_stocks]

    def generate_signals(self, ma_period=20, sync_threshold=0.3, n_stocks=15,
                        start_date=None, end_date=None):
        """
        生成月度交易訊號

        Args:
            ma_period: 移動平均線週期
            sync_threshold: 同步性閾值
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            DataFrame: 交易訊號（index=日期, columns=股票代碼, value=1持有/0不持有）
        """
        # 計算族群同步性
        sync_ratios = self.calculate_sector_sync_ratio(ma_period)

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
            # 識別啟動族群
            activated = self.identify_activated_sectors(sync_ratios, rb_date, sync_threshold)

            # 識別補漲股
            if len(activated) > 0:
                stocks = self.identify_catchup_stocks(activated, rb_date, ma_period, n_stocks)
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

    def backtest(self, ma_period=20, sync_threshold=0.3, n_stocks=15,
                start_date=None, end_date=None):
        """
        執行回測（修正版：避免 Look-ahead Bias + 扣除交易成本）

        Args:
            ma_period: 移動平均線週期
            sync_threshold: 同步性閾值
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            dict: 回測結果
        """
        # 生成訊號
        signals = self.generate_signals(ma_period, sync_threshold, n_stocks, start_date, end_date)

        # 載入收盤價
        close = self.loader.get_close_price()

        # 使用修正後的回測引擎
        engine = BacktestEngine()
        result = engine.backtest_with_cost(signals, close, verbose=False)

        return result
