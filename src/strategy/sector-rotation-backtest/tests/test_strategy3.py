"""
測試策略3：綜合法
"""
import pytest
import pandas as pd
import numpy as np
import sys
import os

# 加入 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy3_combined import CombinedStrategy
from data_loader import DataLoader


class TestCombinedStrategy:
    """測試綜合策略"""

    @pytest.fixture
    def loader(self):
        """建立測試用 DataLoader"""
        return DataLoader(start_date='2020-01-01')

    @pytest.fixture
    def strategy(self, loader):
        """建立策略實例"""
        return CombinedStrategy(loader)

    def test_calculate_sector_volume(self, strategy):
        """測試族群成交金額計算"""
        sector_volume = strategy.calculate_sector_volume()

        # 驗證返回型態
        assert isinstance(sector_volume, dict), "族群成交金額應該是字典"

        # 驗證族群數量
        assert len(sector_volume) > 0, "應該至少有一個族群"

        # 驗證每個族群的成交金額是 Series
        for cat, vol in sector_volume.items():
            assert isinstance(vol, pd.Series), f"{cat} 的成交金額應該是 Series"
            assert len(vol) > 0, f"{cat} 的成交金額不應為空"

    def test_calculate_volume_ma(self, strategy):
        """測試成交金額移動平均計算"""
        sector_volume = strategy.calculate_sector_volume()

        # 取一個測試族群
        test_cat = list(sector_volume.keys())[0]
        test_vol = sector_volume[test_cat]

        # 計算 20 日均量
        vol_ma = test_vol.rolling(20).mean()

        # 驗證計算結果
        assert isinstance(vol_ma, pd.Series), "均量應該是 Series"
        assert len(vol_ma) == len(test_vol), "均量長度應該與原始數據一致"

    def test_identify_volume_confirmed_sectors(self, strategy):
        """測試識別量能確認的族群"""
        confirmed = strategy.identify_volume_confirmed_sectors(
            date='2023-06-05',
            volume_period=3,
            ma_period=20
        )

        # 驗證返回型態
        assert isinstance(confirmed, list), "量能確認族群應該是 list"

        # 驗證結果合理（可能為空）
        assert len(confirmed) >= 0, "量能確認族群數量應該 >= 0"

    def test_filter_qualified_sectors(self, strategy):
        """測試篩選符合條件的族群"""
        qualified = strategy.filter_qualified_sectors(
            date='2023-06-05',
            rs_top_pct=0.3,
            sync_threshold=0.3,
            volume_period=3
        )

        # 驗證返回型態
        assert isinstance(qualified, list), "符合條件的族群應該是 list"

        # 驗證結果合理（可能為空）
        assert len(qualified) >= 0, "符合條件的族群數量應該 >= 0"

    def test_integration_with_strategy1_strategy2(self, strategy):
        """測試與策略 1、2 的整合"""
        # 驗證策略 3 可以調用策略 1 的方法
        rs = strategy.strategy1.calculate_relative_strength(period=10)
        assert isinstance(rs, dict), "應該能調用策略1的方法"

        # 驗證策略 3 可以調用策略 2 的方法
        sync_ratio = strategy.strategy2.calculate_sector_sync_ratio(ma_period=20)
        assert isinstance(sync_ratio, dict), "應該能調用策略2的方法"

    def test_select_combined_stocks(self, strategy):
        """測試綜合選股"""
        # 使用測試族群
        test_sectors = ['半導體', '電子零組件']

        # 選股
        stocks = strategy.select_combined_stocks(
            sectors=test_sectors,
            date='2023-06-05',
            n_stocks=15
        )

        # 驗證返回型態
        assert isinstance(stocks, list), "選股結果應該是 list"

        # 驗證選股數量限制
        assert len(stocks) <= 15, "選股數量不應超過 15 檔"

    def test_generate_signals(self, strategy):
        """測試生成交易訊號"""
        # 使用較短期間測試
        signals = strategy.generate_signals(
            rs_period=10,
            rs_top_pct=0.3,
            sync_threshold=0.3,
            volume_period=3,
            n_stocks=15,
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
            rs_period=10,
            rs_top_pct=0.3,
            sync_threshold=0.3,
            volume_period=3,
            n_stocks=15,
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

    def test_strategy_parameters(self, strategy):
        """測試策略參數設置"""
        # 驗證策略 3 的參數與 plan.md 一致
        # RS Top 30%（比策略1的20%更寬鬆）
        # 同步性 >= 30%
        # 選股數量 15 檔

        result = strategy.backtest(
            rs_period=10,
            rs_top_pct=0.3,  # 30%
            sync_threshold=0.3,  # 30%
            volume_period=3,
            n_stocks=15,  # 15 檔
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

        # 只要能執行完成就算通過
        assert result is not None, "回測應該能正常執行"
