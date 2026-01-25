"""
策略1：族群相對強弱法

選股邏輯：
1. 計算所有族群近 5/10/20 日報酬
2. 扣除加權指數同期報酬（相對強度 RS）
3. 選擇 RS 排名 Top 20% 的族群
4. 在這些族群中選擇價值最低（PB Ratio）的 10 檔股票
"""
import pandas as pd
import numpy as np
from finlab import data
from data_loader import DataLoader
from backtest_utils import BacktestEngine


class RelativeStrengthStrategy:
    """族群相對強弱策略"""

    def __init__(self, loader: DataLoader):
        """
        初始化策略

        Args:
            loader: DataLoader 實例
        """
        self.loader = loader

    def calculate_sector_returns(self, period=10):
        """
        計算各族群的報酬率

        Args:
            period: 計算週期（天數）

        Returns:
            dict: {族群名稱: Series(日期, 報酬率)}
        """
        close = self.loader.get_close_price()
        categories = self.loader.get_categories()

        sector_returns = {}

        for cat in categories:
            # 使用 category filter 取得該族群股票
            with data.universe(category=[cat]):
                try:
                    sector_close = data.get('price:收盤價')

                    # 過濾起始日期
                    sector_close = sector_close[sector_close.index >= self.loader.start_date]

                    # 計算族群平均價格
                    sector_avg = sector_close.mean(axis=1)

                    # 計算報酬率
                    sector_returns[cat] = sector_avg.pct_change(period)

                except Exception as e:
                    # 某些族群可能沒有數據，跳過
                    print(f"警告：{cat} 族群數據載入失敗 - {e}")
                    continue

        return sector_returns

    def calculate_relative_strength(self, period=10):
        """
        計算相對強度（族群報酬 - 大盤報酬）

        Args:
            period: 計算週期（天數）

        Returns:
            dict: {族群名稱: Series(日期, RS)}
        """
        # 計算族群報酬
        sector_returns = self.calculate_sector_returns(period)

        # 計算大盤報酬
        benchmark = self.loader.get_benchmark_return()
        benchmark_ret = benchmark.pct_change(period)

        # 計算相對強度
        rs = {}
        for cat, returns in sector_returns.items():
            # 對齊日期索引
            aligned_returns = returns.reindex(benchmark_ret.index)
            rs[cat] = aligned_returns - benchmark_ret

        return rs

    def rank_sectors_by_rs(self, rs_dict, date=None):
        """
        對族群的 RS 進行排名

        Args:
            rs_dict: calculate_relative_strength 的返回值
            date: 指定日期（None = 最新日期）

        Returns:
            Series: 族群 RS 排名（由大到小）
        """
        if date is None:
            # 使用最新日期
            date = max([s.index.max() for s in rs_dict.values() if len(s) > 0])

        # 取得各族群在指定日期的 RS 值
        rs_values = {}
        for cat, rs_series in rs_dict.items():
            try:
                # 使用 .loc 直接取值，避免 in 判斷的問題
                value = rs_series.loc[date]
                # 如果是 Series，取第一個值
                if isinstance(value, pd.Series):
                    value = value.iloc[0]
                rs_values[cat] = value
            except (KeyError, IndexError):
                # 該日期無數據，跳過
                continue

        # 轉換為 Series 並排序
        ranked = pd.Series(rs_values).sort_values(ascending=False)

        return ranked

    def select_top_sectors(self, ranked_rs, top_pct=0.2):
        """
        選擇 RS 排名前 X% 的族群

        Args:
            ranked_rs: rank_sectors_by_rs 的返回值
            top_pct: 選擇比例（0.2 = Top 20%）

        Returns:
            list: 選中的族群名稱
        """
        n_select = max(1, int(len(ranked_rs) * top_pct))

        # 移除 NaN
        valid_ranked = ranked_rs.dropna()

        # 選擇前 N 個
        top_sectors = valid_ranked.head(n_select).index.tolist()

        return top_sectors

    def select_stocks_from_sectors(self, sectors, date, n_stocks=10):
        """
        從指定族群中選擇 PB Ratio 最低的股票

        Args:
            sectors: 族群名稱列表
            date: 選股日期
            n_stocks: 選股數量

        Returns:
            list: 選中的股票代碼
        """
        pb = self.loader.get_pb_ratio()

        # 確保日期存在
        if date not in pb.index:
            # 找最接近的日期
            valid_dates = pb.index[pb.index <= date]
            if len(valid_dates) == 0:
                return []
            date = valid_dates[-1]

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

        # 只保留在 PB 數據中存在的股票
        available_stocks = [s for s in all_stocks if s in pb.columns]

        if len(available_stocks) == 0:
            return []

        # 取得這些股票的 PB Ratio
        pb_values = pb.loc[date, available_stocks]

        # 移除 NaN 和無效值（PB <= 0）
        pb_values = pb_values[pb_values > 0]

        # 排序並選擇最低 PB 的股票
        selected = pb_values.sort_values().head(n_stocks).index.tolist()

        return selected

    def generate_signals(self, period=10, top_pct=0.2, n_stocks=10,
                        start_date=None, end_date=None):
        """
        生成月度交易訊號

        Args:
            period: RS 計算週期
            top_pct: 族群選擇比例
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            DataFrame: 交易訊號（index=日期, columns=股票代碼, value=1持有/0不持有）
        """
        # 計算 RS
        rs = self.calculate_relative_strength(period)

        # 取得所有可能的交易日
        close = self.loader.get_close_price()
        all_dates = close.index

        if start_date:
            all_dates = all_dates[all_dates >= pd.to_datetime(start_date)]
        if end_date:
            all_dates = all_dates[all_dates <= pd.to_datetime(end_date)]

        # 生成月初日期（每月第一個交易日）
        # 將 Index 轉換為 Series，設定正確的 index
        dates_series = pd.Series(all_dates, index=all_dates)
        rebalance_dates = dates_series.resample('MS').first().dropna()

        # 生成訊號
        signals_list = []

        for rb_date in rebalance_dates:
            # 選擇 Top 族群
            ranked = self.rank_sectors_by_rs(rs, date=rb_date)
            top_sectors = self.select_top_sectors(ranked, top_pct)

            # 選股
            stocks = self.select_stocks_from_sectors(top_sectors, rb_date, n_stocks)

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
        signals = pd.DataFrame(0, index=all_dates, columns=all_stocks)

        # 填充訊號
        for sig in signals_list:
            rb_date = sig['date']
            stocks = sig['stocks']

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

    def backtest(self, period=10, top_pct=0.2, n_stocks=10,
                start_date=None, end_date=None):
        """
        執行回測（修正版：避免 Look-ahead Bias + 扣除交易成本）

        Args:
            period: RS 計算週期
            top_pct: 族群選擇比例
            n_stocks: 選股數量
            start_date: 回測起始日期
            end_date: 回測結束日期

        Returns:
            dict: 回測結果
        """
        # 生成訊號
        signals = self.generate_signals(period, top_pct, n_stocks, start_date, end_date)

        # 載入收盤價
        close = self.loader.get_close_price()

        # 使用修正後的回測引擎
        engine = BacktestEngine()
        result = engine.backtest_with_cost(signals, close, verbose=False)

        return result
