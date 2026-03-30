#!/usr/bin/env python3
"""
Transformer 股價預測器 — 場景 A：用 Transformer 預測股價

使用 Transformer Encoder 學習歷史股價特徵序列，預測未來 N 天的報酬率。
資料來源：yfinance（免費）

架構：
    輸入 (batch, seq_len=60, features=6)
    → Input Projection → Positional Encoding
    → Transformer Encoder (2 layers, 4 heads)
    → 取最後一天隱藏狀態 → Output Head → 預測報酬率
"""

import argparse
import os
import sys
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

# ============================================================
# 1. 資料下載與特徵工程
# ============================================================

def download_stock_data(ticker="TSM", start="2015-01-01", end=None):
    """用 yfinance 下載股票 OHLCV 資料"""
    import yfinance as yf

    if end is None:
        end = datetime.now().strftime("%Y-%m-%d")
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"無法下載 {ticker} 的資料，請檢查代號或網路連線")

    # yfinance 可能回傳 MultiIndex columns，統一處理
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df


def compute_features(df):
    """
    從 OHLCV 計算 6 個特徵：
    1. 日報酬率
    2. 5 日報酬率
    3. 20 日波動率
    4. 收盤價 / 20MA 比值
    5. 成交量變化率
    6. 高低價振幅 (High-Low range / Close)
    """
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    features = pd.DataFrame(index=df.index)
    features["returns_1d"] = close.pct_change(1)
    features["returns_5d"] = close.pct_change(5)
    features["volatility_20d"] = features["returns_1d"].rolling(20).std()
    features["ma_ratio"] = close / close.rolling(20).mean()
    features["volume_change"] = volume.pct_change(5)
    features["hl_range"] = (high - low) / close

    return features


def rolling_zscore(features, window=252):
    """滾動 Z-score 標準化（避免前瞻偏差）"""
    mean = features.rolling(window, min_periods=60).mean()
    std = features.rolling(window, min_periods=60).std()
    std = std.replace(0, 1)  # 避免除以 0
    return ((features - mean) / std).dropna()


def build_dataset(df, lookback=60, horizon=5):
    """
    建立滑動窗口資料集

    Args:
        df: 原始 OHLCV DataFrame
        lookback: 回看天數（Transformer 序列長度）
        horizon: 預測未來幾天的報酬率

    Returns:
        X: (samples, lookback, n_features) 特徵張量
        y: (samples,) 未來 horizon 天的報酬率（用於訓練）
        dates: 每個樣本對應的日期
        daily_ret: (samples,) 次日報酬率（用於回測 P&L）
    """
    features = compute_features(df)
    features_norm = rolling_zscore(features)

    close = df["Close"]
    future_ret = close.pct_change(horizon).shift(-horizon)  # 訓練標籤
    next_day_ret = close.pct_change(1).shift(-1)            # 回測用次日報酬

    # 對齊索引
    common_idx = features_norm.index.intersection(future_ret.dropna().index)
    common_idx = common_idx.intersection(next_day_ret.dropna().index)
    features_norm = features_norm.loc[common_idx]
    future_ret = future_ret.loc[common_idx]
    next_day_ret = next_day_ret.loc[common_idx]

    X_list, y_list, daily_list, date_list = [], [], [], []
    values = features_norm.values
    ret_values = future_ret.values
    daily_values = next_day_ret.values

    for i in range(lookback, len(values)):
        if np.isnan(ret_values[i]) or np.isnan(daily_values[i]):
            continue
        window = values[i - lookback : i]
        if np.any(np.isnan(window)):
            continue
        X_list.append(window)
        y_list.append(ret_values[i])
        daily_list.append(daily_values[i])
        date_list.append(common_idx[i])

    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.float32)
    daily_ret = np.array(daily_list, dtype=np.float32)
    return X, y, date_list, daily_ret


# ============================================================
# 2. Transformer 模型
# ============================================================

class StockTransformer(nn.Module):
    """
    用 Transformer Encoder 預測股價報酬率

    資料流：
        (batch, seq_len, d_feature)
        → Linear(d_feature, d_model)         # 特徵投影
        → + Positional Encoding              # 注入時間順序
        → TransformerEncoder × num_layers    # Self-Attention
        → 取最後一天的隱藏狀態                  # 濃縮整段資訊
        → Linear(d_model, 32) → ReLU → Linear(32, 1)  # 預測報酬
    """

    def __init__(self, d_feature=6, d_model=64, nhead=4, num_layers=2, dropout=0.1, max_seq_len=200):
        super().__init__()
        self.input_proj = nn.Linear(d_feature, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, max_seq_len, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=128,
            dropout=dropout,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)

        self.output_head = nn.Sequential(
            nn.Linear(d_model, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
        )

    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_feature)
        Returns:
            (batch,) 預測報酬率
        """
        x = self.input_proj(x)  # (batch, seq_len, d_model)
        seq_len = x.size(1)
        x = x + self.pos_encoding[:, :seq_len, :]
        x = self.transformer(x)
        x = x[:, -1, :]  # 取最後一天的隱藏狀態
        return self.output_head(x).squeeze(-1)


# ============================================================
# 3. 訓練
# ============================================================

def train_model(X_train, y_train, X_val, y_val, d_feature=6, epochs=100, batch_size=64, lr=1e-3, patience=10, verbose=True):
    """
    訓練 Transformer 模型（含 Early Stopping）

    Returns:
        model: 訓練好的模型
        train_losses: 每個 epoch 的訓練 loss
        val_losses: 每個 epoch 的驗證 loss
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    model = StockTransformer(d_feature=d_feature).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr, weight_decay=1e-5)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)
    loss_fn = nn.MSELoss()

    train_ds = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    X_val_t = torch.FloatTensor(X_val).to(device)
    y_val_t = torch.FloatTensor(y_val).to(device)

    train_losses, val_losses = [], []
    best_val_loss = float("inf")
    best_state = None
    wait = 0

    for epoch in range(epochs):
        # 訓練
        model.train()
        epoch_loss = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            loss = loss_fn(pred, yb)
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_loss += loss.item() * len(xb)
        train_loss = epoch_loss / len(X_train)
        train_losses.append(train_loss)

        # 驗證
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_t)
            val_loss = loss_fn(val_pred, y_val_t).item()
        val_losses.append(val_loss)
        scheduler.step(val_loss)

        # Early Stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            wait = 0
        else:
            wait += 1
            if wait >= patience:
                if verbose:
                    print(f"  Early stopping at epoch {epoch + 1}")
                break

        if verbose and (epoch + 1) % 10 == 0:
            print(f"  Epoch {epoch + 1:3d} | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")

    if best_state is not None:
        model.load_state_dict(best_state)
    model.eval()
    return model, train_losses, val_losses


# ============================================================
# 4. 回測
# ============================================================

def backtest(predictions, actuals, dates, daily_rets=None, threshold=0.0):
    """
    簡易回測：預測報酬 > threshold 則做多，否則空手

    Args:
        predictions: 模型預測的 horizon 天報酬率（用於方向判斷）
        actuals: 實際 horizon 天報酬率（用於方向準確率統計）
        dates: 日期列表
        daily_rets: 次日報酬率（用於 P&L 計算）。若為 None 則用 actuals。
        threshold: 進場閾值

    Returns:
        dict: 績效指標
        pd.DataFrame: 每日詳細回測結果
    """
    pnl_rets = daily_rets if daily_rets is not None else actuals
    df = pd.DataFrame({"date": dates, "pred": predictions, "actual": actuals, "daily_ret": pnl_rets})
    df = df.set_index("date")

    # 策略：預測為正則做多，否則空手
    df["signal"] = (df["pred"] > threshold).astype(float)
    df["strategy_ret"] = df["signal"] * df["daily_ret"]
    df["buy_hold_ret"] = df["daily_ret"]

    # 累積報酬
    df["strategy_cumret"] = (1 + df["strategy_ret"]).cumprod()
    df["buyhold_cumret"] = (1 + df["buy_hold_ret"]).cumprod()

    # 績效指標
    n_days = len(df)
    n_years = n_days / 252

    # 策略
    total_ret = df["strategy_cumret"].iloc[-1] - 1
    cagr = (1 + total_ret) ** (1 / max(n_years, 0.01)) - 1
    daily_rets = df["strategy_ret"]
    sharpe = daily_rets.mean() / max(daily_rets.std(), 1e-8) * np.sqrt(252)
    cum = df["strategy_cumret"]
    drawdown = cum / cum.cummax() - 1
    max_dd = drawdown.min()

    # Buy & Hold
    bh_total = df["buyhold_cumret"].iloc[-1] - 1
    bh_cagr = (1 + bh_total) ** (1 / max(n_years, 0.01)) - 1

    # 勝率
    trades = df[df["signal"] == 1]
    win_rate = (trades["actual"] > 0).mean() if len(trades) > 0 else 0

    # 方向準確率
    direction_acc = ((df["pred"] > 0) == (df["actual"] > 0)).mean()

    metrics = {
        "total_return": total_ret,
        "cagr": cagr,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
        "win_rate": win_rate,
        "direction_accuracy": direction_acc,
        "num_trades": int(df["signal"].sum()),
        "total_days": n_days,
        "buyhold_return": bh_total,
        "buyhold_cagr": bh_cagr,
    }
    return metrics, df


# ============================================================
# 5. 視覺化
# ============================================================

def plot_results(df_backtest, train_losses, val_losses, metrics, output_dir="."):
    """產出視覺化圖表"""
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))

    # (1) 訓練曲線
    ax = axes[0, 0]
    ax.plot(train_losses, label="Train Loss")
    ax.plot(val_losses, label="Val Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.set_title("Training & Validation Loss")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # (2) 預測 vs 實際散佈圖
    ax = axes[0, 1]
    ax.scatter(df_backtest["actual"], df_backtest["pred"], alpha=0.3, s=10)
    lims = [
        min(df_backtest["actual"].min(), df_backtest["pred"].min()),
        max(df_backtest["actual"].max(), df_backtest["pred"].max()),
    ]
    ax.plot(lims, lims, "r--", alpha=0.5)
    ax.set_xlabel("Actual Return")
    ax.set_ylabel("Predicted Return")
    ax.set_title(f"Pred vs Actual (Direction Acc: {metrics['direction_accuracy']:.1%})")
    ax.grid(True, alpha=0.3)

    # (3) 累積報酬曲線
    ax = axes[1, 0]
    ax.plot(df_backtest.index, df_backtest["strategy_cumret"], label="Transformer Strategy", linewidth=1.5)
    ax.plot(df_backtest.index, df_backtest["buyhold_cumret"], label="Buy & Hold", linewidth=1.5, alpha=0.7)
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Return")
    ax.set_title("Backtest: Cumulative Returns")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    # (4) Drawdown
    ax = axes[1, 1]
    cum = df_backtest["strategy_cumret"]
    dd = cum / cum.cummax() - 1
    ax.fill_between(df_backtest.index, dd, 0, alpha=0.4, color="red")
    ax.set_xlabel("Date")
    ax.set_ylabel("Drawdown")
    ax.set_title(f"Strategy Drawdown (Max: {metrics['max_drawdown']:.1%})")
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=30)

    plt.tight_layout()
    path = os.path.join(output_dir, "backtest_results.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n  圖表已儲存至 {path}")


# ============================================================
# 6. 主程式
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Transformer 股價預測器")
    parser.add_argument("--ticker", default="TSM", help="股票代號 (預設: TSM)")
    parser.add_argument("--start", default="2015-01-01", help="資料起始日 (預設: 2015-01-01)")
    parser.add_argument("--lookback", type=int, default=60, help="回看天數 (預設: 60)")
    parser.add_argument("--horizon", type=int, default=5, help="預測天數 (預設: 5)")
    parser.add_argument("--epochs", type=int, default=100, help="最大訓練 epoch (預設: 100)")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size (預設: 64)")
    parser.add_argument("--lr", type=float, default=1e-3, help="學習率 (預設: 1e-3)")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="訓練集比例 (預設: 0.7)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="驗證集比例 (預設: 0.15)")
    parser.add_argument("--no-plot", action="store_true", help="不產出圖表")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  Transformer 股價預測器 — 場景 A")
    print("=" * 60)

    # Step 1: 下載資料
    print(f"\n[1/5] 下載 {args.ticker} 資料 ({args.start} ~ 今天)...")
    df = download_stock_data(args.ticker, start=args.start)
    print(f"  下載完成：{len(df)} 筆日資料")
    print(f"  日期範圍：{df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")

    # Step 2: 建立資料集
    print(f"\n[2/5] 特徵工程 (lookback={args.lookback}, horizon={args.horizon})...")
    X, y, dates, daily_ret = build_dataset(df, lookback=args.lookback, horizon=args.horizon)
    n_features = X.shape[2]
    print(f"  資料集大小：X={X.shape}, y={y.shape}")
    print(f"  特徵數：{n_features}")

    # Step 3: 時間序列切割（訓練/驗證/測試）
    n = len(X)
    train_end = int(n * args.train_ratio)
    val_end = int(n * (args.train_ratio + args.val_ratio))

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]
    X_test, y_test = X[val_end:], y[val_end:]
    daily_ret_test = daily_ret[val_end:]
    dates_test = dates[val_end:]

    print(f"\n  時間序列切割（不可隨機切！）：")
    print(f"    訓練集：{len(X_train)} 筆 ({dates[0].strftime('%Y-%m-%d')} ~ {dates[train_end-1].strftime('%Y-%m-%d')})")
    print(f"    驗證集：{len(X_val)} 筆 ({dates[train_end].strftime('%Y-%m-%d')} ~ {dates[val_end-1].strftime('%Y-%m-%d')})")
    print(f"    測試集：{len(X_test)} 筆 ({dates[val_end].strftime('%Y-%m-%d')} ~ {dates[-1].strftime('%Y-%m-%d')})")

    # Step 4: 訓練
    print(f"\n[3/5] 訓練 Transformer (epochs={args.epochs}, batch_size={args.batch_size})...")
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"  Device: {device}")

    model, train_losses, val_losses = train_model(
        X_train, y_train, X_val, y_val,
        d_feature=n_features,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        patience=15,
    )
    print(f"  最終 Train Loss: {train_losses[-1]:.6f}")
    print(f"  最終 Val Loss:   {val_losses[-1]:.6f}")

    # Step 5: 測試集預測
    print(f"\n[4/5] 測試集預測...")
    model.eval()
    with torch.no_grad():
        X_test_t = torch.FloatTensor(X_test).to(next(model.parameters()).device)
        predictions = model(X_test_t).cpu().numpy()

    # 相關係數
    corr = np.corrcoef(predictions, y_test)[0, 1]
    print(f"  預測 vs 實際相關係數: {corr:.4f}")

    # Step 6: 回測
    print(f"\n[5/5] 回測...")
    metrics, df_bt = backtest(predictions, y_test, dates_test, daily_rets=daily_ret_test)

    print("\n" + "=" * 60)
    print("  回測績效報告")
    print("=" * 60)
    print(f"  測試期間：{dates_test[0].strftime('%Y-%m-%d')} ~ {dates_test[-1].strftime('%Y-%m-%d')}")
    print(f"  總交易日：{metrics['total_days']}")
    print(f"  做多天數：{metrics['num_trades']}")
    print(f"  方向準確率：{metrics['direction_accuracy']:.1%}")
    print(f"  勝率（做多日）：{metrics['win_rate']:.1%}")
    print(f"  ---")
    print(f"  策略總報酬：{metrics['total_return']:.2%}")
    print(f"  策略 CAGR：  {metrics['cagr']:.2%}")
    print(f"  策略 Sharpe：{metrics['sharpe']:.3f}")
    print(f"  最大回撤：  {metrics['max_drawdown']:.2%}")
    print(f"  ---")
    print(f"  Buy&Hold 總報酬：{metrics['buyhold_return']:.2%}")
    print(f"  Buy&Hold CAGR：  {metrics['buyhold_cagr']:.2%}")
    print("=" * 60)

    # 圖表
    if not args.no_plot:
        plot_results(df_bt, train_losses, val_losses, metrics, output_dir=output_dir)

    return metrics


if __name__ == "__main__":
    main()
