#!/usr/bin/env python3
"""
Transformer 股價預測器 — 單元測試

測試內容：
1. 模型結構與輸出維度
2. 特徵工程正確性
3. 資料集建立（滑動窗口）
4. 訓練流程（小規模煙霧測試）
5. 回測邏輯
"""

import sys
import os
import unittest

import numpy as np
import pandas as pd
import torch

# 加入專案路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import (
    StockTransformer,
    compute_features,
    rolling_zscore,
    build_dataset,
    train_model,
    backtest,
)


class TestStockTransformer(unittest.TestCase):
    """測試 Transformer 模型結構"""

    def test_output_shape(self):
        """模型輸出 shape 應為 (batch,)"""
        model = StockTransformer(d_feature=6, d_model=32, nhead=4, num_layers=1)
        x = torch.randn(8, 60, 6)  # batch=8, seq=60, feat=6
        out = model(x)
        self.assertEqual(out.shape, (8,))

    def test_single_sample(self):
        """單一樣本也能正常推論"""
        model = StockTransformer(d_feature=6)
        x = torch.randn(1, 60, 6)
        out = model(x)
        self.assertEqual(out.shape, (1,))

    def test_different_seq_len(self):
        """不同序列長度都能處理"""
        model = StockTransformer(d_feature=6, max_seq_len=200)
        for seq_len in [30, 60, 120]:
            x = torch.randn(4, seq_len, 6)
            out = model(x)
            self.assertEqual(out.shape, (4,), f"seq_len={seq_len} failed")

    def test_different_feature_dims(self):
        """不同特徵維度都能處理"""
        for d_feat in [3, 6, 10]:
            model = StockTransformer(d_feature=d_feat)
            x = torch.randn(4, 60, d_feat)
            out = model(x)
            self.assertEqual(out.shape, (4,), f"d_feature={d_feat} failed")

    def test_gradient_flow(self):
        """梯度可以正常反向傳播"""
        model = StockTransformer(d_feature=6)
        x = torch.randn(4, 60, 6)
        target = torch.randn(4)
        loss = torch.nn.MSELoss()(model(x), target)
        loss.backward()
        for name, param in model.named_parameters():
            if param.requires_grad:
                self.assertIsNotNone(param.grad, f"{name} has no gradient")


class TestFeatureEngineering(unittest.TestCase):
    """測試特徵工程"""

    def _make_fake_ohlcv(self, n=300):
        """產生假的 OHLCV 資料"""
        np.random.seed(42)
        dates = pd.bdate_range("2020-01-01", periods=n)
        close = 100 + np.cumsum(np.random.randn(n) * 0.5)
        high = close + np.abs(np.random.randn(n))
        low = close - np.abs(np.random.randn(n))
        volume = np.random.randint(1000000, 5000000, n).astype(float)
        return pd.DataFrame(
            {"Open": close * 0.99, "High": high, "Low": low, "Close": close, "Volume": volume},
            index=dates,
        )

    def test_compute_features_columns(self):
        """特徵工程應產出 6 個欄位"""
        df = self._make_fake_ohlcv()
        features = compute_features(df)
        expected_cols = ["returns_1d", "returns_5d", "volatility_20d", "ma_ratio", "volume_change", "hl_range"]
        self.assertEqual(list(features.columns), expected_cols)

    def test_compute_features_no_future_leak(self):
        """特徵不應包含未來資訊（所有特徵都用 pct_change / rolling，天然向後看）"""
        df = self._make_fake_ohlcv(500)
        features = compute_features(df)
        # 取前 100 天計算的特徵，不應受第 101 天之後的資料影響
        features_100 = compute_features(df.iloc[:100])
        features_full = compute_features(df)
        # 前 100 天的特徵應完全一致
        common = features_100.dropna().index.intersection(features_full.dropna().index)
        if len(common) > 0:
            pd.testing.assert_frame_equal(
                features_100.loc[common],
                features_full.loc[common],
                check_names=False,
            )

    def test_rolling_zscore(self):
        """Z-score 後的數值應大致在合理範圍"""
        df = self._make_fake_ohlcv(500)
        features = compute_features(df)
        normed = rolling_zscore(features, window=252)
        # 大部分值應在 [-5, 5] 之間
        within_range = ((normed > -5) & (normed < 5)).mean().mean()
        self.assertGreater(within_range, 0.95)

    def test_build_dataset_shape(self):
        """build_dataset 輸出 shape 正確"""
        df = self._make_fake_ohlcv(500)
        X, y, dates, daily_ret = build_dataset(df, lookback=30, horizon=5)
        self.assertEqual(len(X.shape), 3)
        self.assertEqual(X.shape[1], 30)  # lookback
        self.assertEqual(X.shape[2], 6)   # n_features
        self.assertEqual(len(y), len(X))
        self.assertEqual(len(dates), len(X))
        self.assertEqual(len(daily_ret), len(X))

    def test_build_dataset_no_nan(self):
        """資料集不應包含 NaN"""
        df = self._make_fake_ohlcv(500)
        X, y, _, _ = build_dataset(df, lookback=30, horizon=5)
        self.assertFalse(np.any(np.isnan(X)))
        self.assertFalse(np.any(np.isnan(y)))


class TestTraining(unittest.TestCase):
    """測試訓練流程（煙霧測試）"""

    def test_training_reduces_loss(self):
        """訓練應能降低 loss"""
        np.random.seed(42)
        torch.manual_seed(42)
        n_samples = 200
        X = np.random.randn(n_samples, 30, 6).astype(np.float32)
        y = np.random.randn(n_samples).astype(np.float32) * 0.01

        split = int(n_samples * 0.7)
        model, train_losses, val_losses = train_model(
            X[:split], y[:split],
            X[split:], y[split:],
            d_feature=6, epochs=30, batch_size=32, lr=1e-3, patience=20, verbose=False,
        )
        # 最後的 train loss 應小於初始 train loss
        self.assertLess(train_losses[-1], train_losses[0])

    def test_model_returns_eval_mode(self):
        """訓練後模型應處於 eval 模式"""
        X = np.random.randn(100, 30, 6).astype(np.float32)
        y = np.random.randn(100).astype(np.float32) * 0.01
        model, _, _ = train_model(X[:70], y[:70], X[70:], y[70:], d_feature=6, epochs=5, verbose=False)
        self.assertFalse(model.training)


class TestBacktest(unittest.TestCase):
    """測試回測邏輯"""

    def test_perfect_prediction(self):
        """完美預測應有正報酬"""
        n = 100
        dates = pd.bdate_range("2023-01-01", periods=n)
        actuals = np.random.randn(n) * 0.02
        predictions = actuals.copy()  # 完美預測

        metrics, df = backtest(predictions, actuals, dates)
        self.assertGreater(metrics["direction_accuracy"], 0.99)
        self.assertGreater(metrics["total_return"], 0)

    def test_zero_prediction(self):
        """全零預測（永不進場）應有零報酬"""
        n = 100
        dates = pd.bdate_range("2023-01-01", periods=n)
        actuals = np.random.randn(n) * 0.02
        predictions = np.zeros(n)

        metrics, df = backtest(predictions, actuals, dates, threshold=0.0)
        self.assertEqual(metrics["num_trades"], 0)
        self.assertAlmostEqual(metrics["total_return"], 0.0, places=5)

    def test_always_long(self):
        """全部做多的策略報酬應等於 Buy & Hold"""
        n = 100
        dates = pd.bdate_range("2023-01-01", periods=n)
        np.random.seed(42)
        actuals = np.random.randn(n) * 0.02
        predictions = np.ones(n)  # 永遠預測為正

        metrics, df = backtest(predictions, actuals, dates)
        self.assertEqual(metrics["num_trades"], n)
        self.assertAlmostEqual(
            metrics["total_return"], metrics["buyhold_return"], places=5
        )

    def test_metrics_keys(self):
        """回測結果應包含所有必要指標"""
        n = 50
        dates = pd.bdate_range("2023-01-01", periods=n)
        metrics, _ = backtest(np.random.randn(n), np.random.randn(n) * 0.02, dates)
        required_keys = [
            "total_return", "cagr", "sharpe", "max_drawdown",
            "win_rate", "direction_accuracy", "num_trades", "total_days",
            "buyhold_return", "buyhold_cagr",
        ]
        for key in required_keys:
            self.assertIn(key, metrics, f"Missing key: {key}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
