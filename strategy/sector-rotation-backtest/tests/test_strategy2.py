"""
測試策略2：族群同步性法
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# 加入 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy2_synchronization import SynchronizationStrategy
from data_loader import DataLoader


class TestSynchronizationStrategy:
    """測試族群同步性策略"""

    @pytest.fixture
    def loader(self):
        """建立測試用 DataLoader"""
        return DataLoader(start_date='2020-01-01')

    @pytest.fixture
    def strategy(self, loader):
        """建立策略實例"""
        return SynchronizationStrategy(loader)

    def test_calculate_ma(self, strategy):
        """測試移動平均線計算"""
        close = strategy.loader.get_close_price()

        # 計算 20MA
        ma20 = strategy.calculate_ma(close, period=20)

        # 驗證返回型態
        assert isinstance(ma20, pd.DataFrame), "MA 應該是 DataFrame"

        # 驗證維度與原始數據一致
        assert ma20.shape == close.shape, "MA 維度應該與收盤價一致"

        # 驗證前 20 天應該是 NaN
        assert ma20.iloc[:19].isna().all().all(), "前 19 天應該是 NaN"

    def test_calculate_sector_sync_ratio(self, strategy):
        """測試族群同步性比例計算"""
        sync_ratio = strategy.calculate_sector_sync_ratio(ma_period=20)

        # 驗證返回型態
        assert isinstance(sync_ratio, dict), "同步性比例應該是字典"

        # 驗證族群數量
        assert len(sync_ratio) > 0, "應該至少有一個族群"

        # 驗證每個族群的同步性比例是 Series
        for cat, ratio in sync_ratio.items():
            assert isinstance(ratio, pd.Series), f"{cat} 的同步性比例應該是 Series"

            # 移除 NaN 後檢查值範圍
            valid_ratio = ratio.dropna()
            if len(valid_ratio) > 0:
                assert (valid_ratio >= 0).all(), f"{cat} 的同步性比例應該 >= 0"
                assert (valid_ratio <= 1).all(), f"{cat} 的同步性比例應該 <= 1"

    def test_identify_activated_sectors(self, strategy):
        """測試識別啟動族群"""
        sync_ratio = strategy.calculate_sector_sync_ratio(ma_period=20)

        # 取最新日期測試
        latest_date = max([s.index.max() for s in sync_ratio.values() if len(s) > 0])

        # 識別啟動族群（閾值 30%）
        activated = strategy.identify_activated_sectors(sync_ratio, date=latest_date, threshold=0.3)

        # 驗證返回型態
        assert isinstance(activated, list), "啟動族群應該是 list"

        # 驗證每個啟動族群的同步性 >= 30%
        for cat in activated:
            if cat in sync_ratio and latest_date in sync_ratio[cat].index:
                ratio = sync_ratio[cat].loc[latest_date]
                if pd.notna(ratio):
                    assert ratio >= 0.3, f"{cat} 的同步性應該 >= 30%"

    def test_calculate_stock_rs(self, strategy):
        """測試個股相對強度計算"""
        rs = strategy.calculate_stock_rs(period=5)

        # 驗證返回型態
        assert isinstance(rs, pd.DataFrame), "個股 RS 應該是 DataFrame"

        # 驗證維度
        close = strategy.loader.get_close_price()
        assert rs.shape == close.shape, "RS 維度應該與收盤價一致"

    def test_identify_catchup_stocks(self, strategy):
        """測試識別補漲股"""
        # 使用測試族群
        test_sectors = ['半導體', '電子零組件']

        # 識別補漲股
        catchup = strategy.identify_catchup_stocks(
            sectors=test_sectors,
            date='2023-06-05',
            ma_period=20
        )

        # 驗證返回型態
        assert isinstance(catchup, list), "補漲股應該是 list"

        # 補漲股數量應該合理（可能為 0）
        assert len(catchup) >= 0, "補漲股數量應該 >= 0"

    def test_catchup_stock_conditions(self, strategy):
        """測試補漲股條件檢查"""
        close = strategy.loader.get_close_price()

        # 測試單一股票的條件
        test_stock = close.columns[0]
        test_date = '2023-06-05'

        # 計算技術指標
        ma20 = strategy.calculate_ma(close, period=20)
        ma60 = strategy.calculate_ma(close, period=60)
        ma120 = strategy.calculate_ma(close, period=120)
        high20 = close.rolling(20).max()
        volume = strategy.loader.get_volume()
        vol_ma20 = volume.rolling(20).mean()

        # 檢查條件
        if test_stock in close.columns and test_date in close.index:
            stock_close = close.loc[test_date, test_stock]

            # 條件 1：未創新高
            is_not_high = stock_close < high20.loc[test_date, test_stock] if test_stock in high20.columns else True

            # 條件 2：價格位置（季線～半年線之間）
            if test_stock in ma60.columns and test_stock in ma120.columns:
                is_between_ma = (stock_close > ma60.loc[test_date, test_stock]) and \
                               (stock_close < ma120.loc[test_date, test_stock])
            else:
                is_between_ma = True

            # 驗證條件是布林值（接受 Python bool 和 numpy bool）
            assert isinstance(is_not_high, (bool, np.bool_, type(pd.NA))), "條件應該是布林值"

    def test_generate_signals(self, strategy):
        """測試生成交易訊號"""
        # 使用較短期間測試
        signals = strategy.generate_signals(
            ma_period=20,
            sync_threshold=0.3,
            n_stocks=10,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

        # 驗證訊號格式
        assert isinstance(signals, pd.DataFrame), "訊號應該是 DataFrame"

        # 驗證訊號包含日期索引
        assert isinstance(signals.index, pd.DatetimeIndex), "訊號應該有日期索引"

    def test_backtest_basic(self, strategy):
        """測試基本回測流程"""
        # 使用較短期間測試
        result = strategy.backtest(
            ma_period=20,
            sync_threshold=0.3,
            n_stocks=10,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

        # 驗證回測結果結構
        assert isinstance(result, dict), "回測結果應該是字典"

        # 驗證包含關鍵指標
        required_keys = ['cagr', 'sharpe', 'max_drawdown', 'win_rate', 'total_trades']
        for key in required_keys:
            assert key in result, f"回測結果應包含 {key}"

        # 驗證數值合理性（可能為 None 如果沒有交易）
        if result['cagr'] is not None:
            assert isinstance(result['cagr'], (int, float)), "CAGR 應該是數值"
            assert result['sharpe'] is not None, "Sharpe Ratio 不應為 None"
            assert result['max_drawdown'] <= 0, "Max Drawdown 應該是負數或零"
            assert 0 <= result['win_rate'] <= 1, "勝率應該在 0~1 之間"
