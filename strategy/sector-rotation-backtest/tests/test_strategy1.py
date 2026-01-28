"""
測試策略1：族群相對強弱法
"""
import pytest
import pandas as pd
import sys
import os

# 加入 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from strategy1_relative_strength import RelativeStrengthStrategy
from data_loader import DataLoader


class TestRelativeStrengthStrategy:
    """測試族群相對強弱策略"""

    @pytest.fixture
    def loader(self):
        """建立測試用 DataLoader"""
        return DataLoader(start_date='2020-01-01')

    @pytest.fixture
    def strategy(self, loader):
        """建立策略實例"""
        return RelativeStrengthStrategy(loader)

    def test_calculate_sector_returns(self, strategy):
        """測試族群報酬計算"""
        sector_returns = strategy.calculate_sector_returns(period=10)

        # 驗證返回型態
        assert isinstance(sector_returns, dict), "族群報酬應該是字典"

        # 驗證族群數量
        assert len(sector_returns) > 0, "應該至少有一個族群"

        # 驗證每個族群的報酬是 Series
        for cat, returns in sector_returns.items():
            assert isinstance(returns, pd.Series), f"{cat} 的報酬應該是 Series"
            assert len(returns) > 0, f"{cat} 的報酬不應為空"

    def test_calculate_relative_strength(self, strategy):
        """測試相對強度計算"""
        rs = strategy.calculate_relative_strength(period=10)

        # 驗證返回型態
        assert isinstance(rs, dict), "相對強度應該是字典"

        # 驗證族群數量
        assert len(rs) > 0, "應該至少有一個族群的 RS"

        # 驗證 RS 值範圍（應該是百分比變化，通常在 -50% ~ +50% 之間）
        for cat, rs_series in rs.items():
            assert isinstance(rs_series, pd.Series), f"{cat} 的 RS 應該是 Series"

            # 移除 NaN 後檢查
            valid_rs = rs_series.dropna()
            if len(valid_rs) > 0:
                # RS 是報酬差，理論上不應該出現極端值
                assert valid_rs.abs().max() < 2.0, f"{cat} 的 RS 值異常（超過 200%）"

    def test_rank_sectors_by_rs(self, strategy):
        """測試族群 RS 排名"""
        # 使用某個特定日期測試
        rs = strategy.calculate_relative_strength(period=10)

        # 取最新一個交易日的 RS 排名
        ranked = strategy.rank_sectors_by_rs(rs)

        # 驗證排名結果
        assert isinstance(ranked, pd.Series), "排名應該是 Series"
        assert len(ranked) > 0, "排名不應為空"

        # 驗證排名順序（應該由大到小）
        values = ranked.values
        for i in range(len(values) - 1):
            if not pd.isna(values[i]) and not pd.isna(values[i+1]):
                assert values[i] >= values[i+1], "RS 排名應該由大到小"

    def test_select_top_sectors(self, strategy):
        """測試選擇 Top 20% 族群"""
        rs = strategy.calculate_relative_strength(period=10)
        ranked = strategy.rank_sectors_by_rs(rs)

        # 選擇 Top 20%
        top_sectors = strategy.select_top_sectors(ranked, top_pct=0.2)

        # 驗證選擇結果
        assert isinstance(top_sectors, list), "Top 族群應該是 list"
        assert len(top_sectors) > 0, "應該至少選出一個族群"

        # 驗證數量符合 Top 20%（30 個族群的 20% = 6 個）
        expected_count = int(len(strategy.loader.get_categories()) * 0.2)
        assert len(top_sectors) <= expected_count + 1, f"Top 20% 應該約 {expected_count} 個族群"

    def test_select_stocks_from_sectors(self, strategy):
        """測試從指定族群選擇低 PB 股票"""
        # 使用測試族群列表
        test_sectors = ['半導體', '電子零組件']

        # 選擇股票
        selected = strategy.select_stocks_from_sectors(
            sectors=test_sectors,
            date='2023-01-05',  # 使用一個確定的日期
            n_stocks=10
        )

        # 驗證選擇結果
        assert isinstance(selected, list), "選股結果應該是 list"

        # 可能會少於 10 檔（如果族群內股票數不足）
        assert len(selected) <= 10, "選股數量不應超過 10 檔"

    def test_generate_signals(self, strategy):
        """測試生成交易訊號（月度 rebalance）"""
        # 使用較短期間測試
        signals = strategy.generate_signals(
            period=10,
            top_pct=0.2,
            n_stocks=10,
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

        # 驗證訊號格式
        assert isinstance(signals, pd.DataFrame), "訊號應該是 DataFrame"

        # 驗證訊號包含日期索引
        assert signals.index.name == 'date' or isinstance(signals.index, pd.DatetimeIndex), \
            "訊號應該有日期索引"

        # 驗證訊號非空（2023 年應該至少有幾次 rebalance）
        assert len(signals) > 0, "2023 年應該有交易訊號"

    def test_backtest_basic(self, strategy):
        """測試基本回測流程"""
        # 使用較短期間測試（避免測試時間過長）
        result = strategy.backtest(
            period=10,
            top_pct=0.2,
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

        # 驗證數值合理性
        assert result['cagr'] is not None, "CAGR 不應為 None"
        assert result['sharpe'] is not None, "Sharpe Ratio 不應為 None"
        assert result['max_drawdown'] <= 0, "Max Drawdown 應該是負數或零"
        assert 0 <= result['win_rate'] <= 1, "勝率應該在 0~1 之間"
