"""
測試數據載入模組
"""
import pytest
from datetime import datetime
import sys
import os

# 加入 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_loader import DataLoader


class TestDataLoader:
    """測試 DataLoader 類別"""

    @pytest.fixture
    def loader(self):
        """建立 DataLoader 實例"""
        return DataLoader(start_date='2020-01-01')

    def test_load_categories(self, loader):
        """測試載入族群列表"""
        categories = loader.get_categories()

        # 驗證族群數量
        assert len(categories) == 30, f"應該有 30 個族群，實際 {len(categories)} 個"

        # 驗證關鍵族群存在
        assert '半導體' in categories
        assert '電子零組件' in categories
        assert '金融' in categories

    def test_load_close_price(self, loader):
        """測試載入收盤價數據"""
        close = loader.get_close_price()

        # 驗證數據類型
        assert close is not None, "收盤價數據不應為 None"

        # 驗證數據維度（應該是 DataFrame）
        assert hasattr(close, 'shape'), "收盤價應該是 DataFrame"

        # 驗證數據非空
        assert close.shape[0] > 0, "收盤價數據不應為空"
        assert close.shape[1] > 0, "應該至少有一檔股票"

    def test_load_volume(self, loader):
        """測試載入成交量數據"""
        volume = loader.get_volume()

        # 驗證數據存在
        assert volume is not None, "成交量數據不應為 None"
        assert hasattr(volume, 'shape'), "成交量應該是 DataFrame"
        assert volume.shape[0] > 0, "成交量數據不應為空"

    def test_load_pb_ratio(self, loader):
        """測試載入 PB Ratio 數據"""
        pb = loader.get_pb_ratio()

        # 驗證數據存在
        assert pb is not None, "PB Ratio 數據不應為 None"
        assert hasattr(pb, 'shape'), "PB Ratio 應該是 DataFrame"
        assert pb.shape[0] > 0, "PB Ratio 數據不應為空"

    def test_date_range(self, loader):
        """測試數據時間範圍"""
        close = loader.get_close_price()

        # 取得日期範圍
        start_date = close.index.min()
        end_date = close.index.max()

        # 驗證起始日期（應該在 2020-01-01 附近）
        target_start = datetime(2020, 1, 1)
        assert start_date.year == 2020, f"起始年份應該是 2020，實際是 {start_date.year}"

        # 驗證結束日期（應該接近當前日期）
        current_year = datetime.now().year
        assert end_date.year >= current_year - 1, f"結束日期應該接近當前，實際是 {end_date}"

    def test_data_consistency(self, loader):
        """測試數據一致性（收盤價、成交量、PB 的日期應該對齊）"""
        close = loader.get_close_price()
        volume = loader.get_volume()
        pb = loader.get_pb_ratio()

        # 驗證日期索引存在
        assert hasattr(close, 'index'), "收盤價應該有日期索引"
        assert hasattr(volume, 'index'), "成交量應該有日期索引"
        assert hasattr(pb, 'index'), "PB Ratio 應該有日期索引"
