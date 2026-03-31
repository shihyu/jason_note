#!/usr/bin/env python3
"""
Transformer 股價預測器（FinLab 版）— 單元測試

測試內容：
1. FinLab 資料載入
2. 股票篩選邏輯
3. 多股票資料集建立
4. 預測 → position 轉換
5. 整合煙霧測試（FinLab sim）
"""

import os
import sys
import unittest
import warnings

import numpy as np
import pandas as pd
import torch

warnings.filterwarnings("ignore", category=FutureWarning)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main_finlab import (
    StockTransformer,
    build_multi_stock_dataset,
    build_position,
    compute_stock_features,
    filter_liquid_stocks,
    rolling_zscore,
    train_model,
)


def _make_fake_multi_stock_data(n_days=500, n_stocks=20):
    """產生假的多股票 OHLCV 資料，模擬 FinLab DataFrame 格式"""
    np.random.seed(42)
    dates = pd.bdate_range("2020-01-01", periods=n_days)
    stock_ids = [f"{i:04d}" for i in range(2300, 2300 + n_stocks)]

    close_data = {}
    high_data = {}
    low_data = {}
    volume_data = {}

    for sid in stock_ids:
        price = 100 + np.cumsum(np.random.randn(n_days) * 0.5)
        price = np.maximum(price, 5)  # 確保價格為正
        close_data[sid] = price
        high_data[sid] = price + np.abs(np.random.randn(n_days))
        low_data[sid] = price - np.abs(np.random.randn(n_days))
        volume_data[sid] = np.random.randint(500000, 5000000, n_days).astype(float)

    adj_close = pd.DataFrame(close_data, index=dates)
    adj_high = pd.DataFrame(high_data, index=dates)
    adj_low = pd.DataFrame(low_data, index=dates)
    volume = pd.DataFrame(volume_data, index=dates)
    close = adj_close.copy()

    return adj_close, adj_high, adj_low, volume, close, stock_ids


class TestFilterLiquidStocks(unittest.TestCase):
    """測試股票篩選"""

    def test_basic_filter(self):
        """篩選後股票數應小於等於原始數量"""
        adj_close, _, _, volume, close, stock_ids = _make_fake_multi_stock_data()
        filtered = filter_liquid_stocks(adj_close, volume, close, min_price=10, min_volume_pct=70)
        self.assertGreater(len(filtered), 0)
        self.assertLessEqual(len(filtered), len(stock_ids))

    def test_high_price_filter(self):
        """極高的價格門檻應大幅減少股票數"""
        adj_close, _, _, volume, close, _ = _make_fake_multi_stock_data()
        filtered_low = filter_liquid_stocks(adj_close, volume, close, min_price=10)
        filtered_high = filter_liquid_stocks(adj_close, volume, close, min_price=200)
        self.assertGreaterEqual(len(filtered_low), len(filtered_high))


class TestComputeStockFeatures(unittest.TestCase):
    """測試特徵工程"""

    def test_feature_columns(self):
        """應產出 6 個特徵欄位"""
        adj_close, adj_high, adj_low, volume, _, stock_ids = _make_fake_multi_stock_data()
        features = compute_stock_features(adj_close, adj_high, adj_low, volume, stock_ids[0])
        expected = ["returns_1d", "returns_5d", "volatility_20d", "ma_ratio", "volume_change", "hl_range"]
        self.assertEqual(list(features.columns), expected)

    def test_no_future_leak(self):
        """前 200 天的特徵不應受後面資料影響"""
        adj_close, adj_high, adj_low, volume, _, stock_ids = _make_fake_multi_stock_data(n_days=500)
        sid = stock_ids[0]
        f_200 = compute_stock_features(
            adj_close.iloc[:200], adj_high.iloc[:200], adj_low.iloc[:200], volume.iloc[:200], sid
        )
        f_all = compute_stock_features(adj_close, adj_high, adj_low, volume, sid)
        common = f_200.dropna().index.intersection(f_all.dropna().index)
        if len(common) > 0:
            pd.testing.assert_frame_equal(f_200.loc[common], f_all.loc[common])


class TestBuildMultiStockDataset(unittest.TestCase):
    """測試多股票資料集建立"""

    def test_shape(self):
        """輸出 shape 正確"""
        adj_close, adj_high, adj_low, volume, _, stock_ids = _make_fake_multi_stock_data()
        X, y, meta = build_multi_stock_dataset(
            adj_close, adj_high, adj_low, volume, stock_ids,
            lookback=30, horizon=5, max_stocks=5,
        )
        self.assertEqual(len(X.shape), 3)
        self.assertEqual(X.shape[1], 30)
        self.assertEqual(X.shape[2], 6)
        self.assertEqual(len(y), len(X))
        self.assertEqual(len(meta), len(X))
        self.assertGreater(len(X), 0)

    def test_no_nan(self):
        """不應有 NaN"""
        adj_close, adj_high, adj_low, volume, _, stock_ids = _make_fake_multi_stock_data()
        X, y, _ = build_multi_stock_dataset(
            adj_close, adj_high, adj_low, volume, stock_ids,
            lookback=30, horizon=5, max_stocks=5,
        )
        self.assertFalse(np.any(np.isnan(X)))
        self.assertFalse(np.any(np.isnan(y)))

    def test_meta_has_stock_and_date(self):
        """meta 應包含 (date, stock_id) tuple"""
        adj_close, adj_high, adj_low, volume, _, stock_ids = _make_fake_multi_stock_data()
        _, _, meta = build_multi_stock_dataset(
            adj_close, adj_high, adj_low, volume, stock_ids,
            lookback=30, horizon=5, max_stocks=3,
        )
        for date, sid in meta[:5]:
            self.assertIsInstance(date, pd.Timestamp)
            self.assertIn(sid, stock_ids)


class TestBuildPosition(unittest.TestCase):
    """測試 position DataFrame 建立"""

    def test_position_shape(self):
        """position 應為 bool DataFrame"""
        adj_close, _, _, _, _, stock_ids = _make_fake_multi_stock_data(n_days=100)
        # 模擬預測分數
        pred_dates = adj_close.index[60:]
        pred_df = pd.DataFrame(
            np.random.randn(len(pred_dates), len(stock_ids)),
            index=pred_dates, columns=stock_ids,
        )
        position = build_position(pred_df, adj_close, top_n=3, resample_freq="W")
        self.assertEqual(position.dtypes.unique().tolist(), [np.dtype("bool")])

    def test_top_n_constraint(self):
        """每個時間點持股數應 <= top_n"""
        adj_close, _, _, _, _, stock_ids = _make_fake_multi_stock_data(n_days=200)
        pred_dates = adj_close.index[60:]
        pred_df = pd.DataFrame(
            np.random.randn(len(pred_dates), len(stock_ids)),
            index=pred_dates, columns=stock_ids,
        )
        top_n = 5
        position = build_position(pred_df, adj_close, top_n=top_n, resample_freq="W")
        daily_count = position.sum(axis=1)
        # 允許部分日期為 0（資料不足的週期）
        nonzero = daily_count[daily_count > 0]
        if len(nonzero) > 0:
            self.assertLessEqual(nonzero.max(), top_n)


class TestTrainingSmoke(unittest.TestCase):
    """訓練煙霧測試"""

    def test_training_reduces_loss(self):
        """訓練應降低 loss"""
        np.random.seed(42)
        torch.manual_seed(42)
        n = 200
        X = np.random.randn(n, 30, 6).astype(np.float32)
        y = np.random.randn(n).astype(np.float32) * 0.01
        split = int(n * 0.7)
        model, tl, vl = train_model(
            X[:split], y[:split], X[split:], y[split:],
            d_feature=6, epochs=30, batch_size=32, lr=1e-3, patience=20, verbose=False,
        )
        self.assertLess(tl[-1], tl[0])
        self.assertFalse(model.training)


class TestFinlabIntegration(unittest.TestCase):
    """FinLab 整合測試（需要 finlab 已登入且有快取資料）"""

    @classmethod
    def setUpClass(cls):
        """嘗試載入 finlab 資料，若失敗則跳過"""
        try:
            import finlab
            finlab.login()
            from finlab import data
            cls.adj_close = data.get("etl:adj_close")
            cls.has_finlab = cls.adj_close is not None and len(cls.adj_close) > 0
        except Exception:
            cls.has_finlab = False

    def test_finlab_data_loaded(self):
        """FinLab 資料應可載入"""
        if not self.has_finlab:
            self.skipTest("FinLab 資料不可用")
        self.assertGreater(len(self.adj_close), 100)
        self.assertGreater(len(self.adj_close.columns), 100)

    def test_finlab_data_no_all_nan_columns(self):
        """應有足夠的非全 NaN 欄位"""
        if not self.has_finlab:
            self.skipTest("FinLab 資料不可用")
        non_null_cols = self.adj_close.dropna(axis=1, how="all").shape[1]
        self.assertGreater(non_null_cols, 500)


if __name__ == "__main__":
    unittest.main(verbosity=2)
