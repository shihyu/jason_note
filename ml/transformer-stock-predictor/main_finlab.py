#!/usr/bin/env python3
"""
Transformer 股價預測器 — 場景 A（FinLab 版）

使用 FinLab 取得台股資料，Transformer 預測未來報酬率，
再將預測結果轉為 FinLab position DataFrame，用 finlab.backtest.sim() 回測。

流程：
    FinLab 資料層 → 特徵工程 → Transformer 訓練（多股票共用模型）
    → 預測所有股票的未來報酬 → 選前 N 名 → finlab.backtest.sim()

架構：
    輸入 (batch, seq_len=60, features=6)
    → Input Projection → Positional Encoding
    → Transformer Encoder (2 layers, 4 heads)
    → 取最後一天隱藏狀態 → Output Head → 預測報酬率
"""

import argparse
import os
import warnings
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset

warnings.filterwarnings("ignore", category=FutureWarning)

# ============================================================
# 1. FinLab 資料層
# ============================================================

def login_finlab():
    """登入 FinLab（使用已儲存的憑證，首次需瀏覽器登入）"""
    import finlab
    finlab.login()


def load_finlab_data():
    """
    用 FinLab 取得台股資料

    Returns:
        adj_close: 還原除權息收盤價 (日期 × 股票代號)
        adj_open:  還原除權息開盤價
        adj_high:  還原除權息最高價
        adj_low:   還原除權息最低價
        volume:    成交股數
        close:     原始收盤價（用於 sim 回測）
    """
    from finlab import data

    print("  載入 FinLab 資料...")
    adj_close = data.get("etl:adj_close")
    adj_open = data.get("etl:adj_open")
    adj_high = data.get("etl:adj_high")
    adj_low = data.get("etl:adj_low")
    volume = data.get("price:成交股數")
    close = data.get("price:收盤價")

    print(f"  資料期間：{adj_close.index[0].strftime('%Y-%m-%d')} ~ {adj_close.index[-1].strftime('%Y-%m-%d')}")
    print(f"  股票數量：{adj_close.shape[1]}")
    return adj_close, adj_open, adj_high, adj_low, volume, close


def filter_liquid_stocks(adj_close, volume, close, min_price=10, min_volume_pct=70, recent_days=60):
    """
    篩選流動性足夠的股票（避免小型股雜訊太大）

    條件：
    1. 近 recent_days 天平均成交量排名前 min_volume_pct%
    2. 股價 > min_price
    3. 股票代號為 4 碼純數字（排除 ETF、權證等）
    """
    # 4 碼純數字股票
    valid_ids = [c for c in adj_close.columns if len(str(c)) == 4 and str(c).isdigit()]
    adj_close = adj_close[valid_ids]
    volume = volume.reindex(columns=valid_ids)
    close = close.reindex(columns=valid_ids)

    # 近期有交易
    recent_close = adj_close.iloc[-recent_days:]
    active = recent_close.notna().sum() > recent_days * 0.8
    active_ids = active[active].index.tolist()

    # 均量排名
    avg_vol = volume[active_ids].iloc[-recent_days:].mean()
    threshold = avg_vol.quantile(1 - min_volume_pct / 100)
    liquid_ids = avg_vol[avg_vol >= threshold].index.tolist()

    # 股價門檻
    last_price = close[liquid_ids].iloc[-1]
    final_ids = last_price[last_price >= min_price].dropna().index.tolist()

    print(f"  篩選後股票數：{len(final_ids)}（流動性 top {min_volume_pct}%, 股價 > {min_price}）")
    return final_ids


# ============================================================
# 2. 特徵工程
# ============================================================

def compute_stock_features(adj_close, adj_high, adj_low, volume, stock_id):
    """
    計算單一股票的 6 個特徵

    1. 日報酬率
    2. 5 日報酬率
    3. 20 日波動率
    4. 收盤價 / 20MA 比值
    5. 成交量變化率
    6. 高低價振幅
    """
    c = adj_close[stock_id]
    h = adj_high[stock_id]
    lo = adj_low[stock_id]
    v = volume[stock_id]

    features = pd.DataFrame(index=c.index)
    features["returns_1d"] = c.pct_change(1)
    features["returns_5d"] = c.pct_change(5)
    features["volatility_20d"] = features["returns_1d"].rolling(20).std()
    features["ma_ratio"] = c / c.rolling(20).mean()
    features["volume_change"] = v.pct_change(5)
    features["hl_range"] = (h - lo) / c

    return features


def rolling_zscore(features, window=252):
    """滾動 Z-score 標準化（避免前瞻偏差）"""
    mean = features.rolling(window, min_periods=60).mean()
    std = features.rolling(window, min_periods=60).std()
    std = std.replace(0, 1)
    return ((features - mean) / std).dropna()


def build_multi_stock_dataset(adj_close, adj_high, adj_low, volume, stock_ids,
                               lookback=60, horizon=5, max_stocks=None):
    """
    為多檔股票建立合併的訓練資料集

    Returns:
        X: (total_samples, lookback, 6) 特徵張量
        y: (total_samples,) 未來 horizon 天報酬率
        meta: list of (date, stock_id) 對應每個樣本
    """
    if max_stocks and len(stock_ids) > max_stocks:
        stock_ids = stock_ids[:max_stocks]

    X_all, y_all, meta_all = [], [], []
    skipped = 0

    for sid in stock_ids:
        try:
            features = compute_stock_features(adj_close, adj_high, adj_low, volume, sid)
            features_norm = rolling_zscore(features)
            if len(features_norm) < lookback + horizon + 10:
                skipped += 1
                continue

            close_s = adj_close[sid]
            future_ret = close_s.pct_change(horizon).shift(-horizon)

            common_idx = features_norm.index.intersection(future_ret.dropna().index)
            features_norm = features_norm.loc[common_idx]
            future_ret = future_ret.loc[common_idx]

            values = features_norm.values
            ret_values = future_ret.values

            for i in range(lookback, len(values)):
                if np.isnan(ret_values[i]):
                    continue
                window = values[i - lookback : i]
                if np.any(np.isnan(window)):
                    continue
                X_all.append(window)
                y_all.append(ret_values[i])
                meta_all.append((common_idx[i], sid))
        except Exception:
            skipped += 1
            continue

    if skipped > 0:
        print(f"  跳過 {skipped} 檔股票（資料不足）")

    X = np.array(X_all, dtype=np.float32)
    y = np.array(y_all, dtype=np.float32)
    return X, y, meta_all


# ============================================================
# 3. Transformer 模型（同 main.py）
# ============================================================

class StockTransformer(nn.Module):
    """Transformer Encoder 預測股價報酬率"""

    def __init__(self, d_feature=6, d_model=64, nhead=4, num_layers=2, dropout=0.1, max_seq_len=200):
        super().__init__()
        self.input_proj = nn.Linear(d_feature, d_model)
        self.pos_encoding = nn.Parameter(torch.randn(1, max_seq_len, d_model) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model, nhead=nhead,
            dim_feedforward=128, dropout=dropout, batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_head = nn.Sequential(
            nn.Linear(d_model, 32), nn.ReLU(), nn.Dropout(dropout), nn.Linear(32, 1),
        )

    def forward(self, x):
        x = self.input_proj(x)
        x = x + self.pos_encoding[:, :x.size(1), :]
        x = self.transformer(x)
        x = x[:, -1, :]
        return self.output_head(x).squeeze(-1)


# ============================================================
# 4. 訓練
# ============================================================

def train_model(X_train, y_train, X_val, y_val, d_feature=6,
                epochs=100, batch_size=64, lr=1e-3, patience=10, verbose=True):
    """訓練 Transformer 模型（含 Early Stopping）"""
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

        model.eval()
        with torch.no_grad():
            val_pred = model(X_val_t)
            val_loss = loss_fn(val_pred, y_val_t).item()
        val_losses.append(val_loss)
        scheduler.step(val_loss)

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
# 5. 預測 → FinLab position → sim() 回測
# ============================================================

def predict_all_stocks(model, adj_close, adj_high, adj_low, volume,
                        stock_ids, lookback=60, predict_dates=None, batch_size=256):
    """
    對所有股票的每個交易日做預測，回傳預測分數 DataFrame

    使用批次推論加速：每檔股票一次收集所有窗口，批次預測。

    Returns:
        pred_df: DataFrame (日期 × 股票代號)，值 = 預測報酬率
    """
    device = next(model.parameters()).device
    model.eval()

    # 收集每個 (date, stock_id) 的預測值
    results = {}  # {sid: {date: pred}}
    total_preds = 0
    n_stocks = len(stock_ids)

    for idx, sid in enumerate(stock_ids):
        if (idx + 1) % 50 == 0 or idx == n_stocks - 1:
            print(f"    預測進度：{idx + 1}/{n_stocks} 檔股票...", end="\r")
        try:
            features = compute_stock_features(adj_close, adj_high, adj_low, volume, sid)
            features_norm = rolling_zscore(features)
            if len(features_norm) < lookback + 1:
                continue

            if predict_dates is not None:
                valid_dates = features_norm.index.intersection(predict_dates)
            else:
                valid_dates = features_norm.index[lookback:]

            # 批次收集所有窗口
            windows = []
            window_dates = []
            values = features_norm.values
            index = features_norm.index

            for dt in valid_dates:
                loc = index.get_loc(dt)
                if loc < lookback:
                    continue
                window = values[loc - lookback : loc]
                if np.any(np.isnan(window)):
                    continue
                windows.append(window)
                window_dates.append(dt)

            if not windows:
                continue

            # 批次推論
            X = np.array(windows, dtype=np.float32)
            sid_preds = {}
            with torch.no_grad():
                for start in range(0, len(X), batch_size):
                    xb = torch.FloatTensor(X[start:start + batch_size]).to(device)
                    preds = model(xb).cpu().numpy()
                    for j, p in enumerate(preds):
                        sid_preds[window_dates[start + j]] = float(p)

            results[sid] = sid_preds
            total_preds += len(sid_preds)
        except Exception:
            continue

    print()  # 換行
    pred_df = pd.DataFrame(results).sort_index()
    pred_df.index = pd.DatetimeIndex(pred_df.index)
    print(f"  預測完成：{total_preds} 個 (日期, 股票) 配對")
    return pred_df


def build_position(pred_df, adj_close, top_n=10, resample_freq="W"):
    """
    將預測分數轉換為 FinLab position DataFrame

    策略：每個 resample 週期結束時，選預測報酬最高的 top_n 檔股票

    Args:
        pred_df: 預測分數 DataFrame
        adj_close: 還原收盤價（用來對齊 index/columns）
        top_n: 每期選幾檔
        resample_freq: 換股頻率 ("W"=週, "M"=月)

    Returns:
        position: FinLab 格式的 bool DataFrame
    """
    # 對齊到 adj_close 的日期和股票
    common_dates = pred_df.index.intersection(adj_close.index)
    common_stocks = pred_df.columns.intersection(adj_close.columns)
    pred_aligned = pred_df.loc[common_dates, common_stocks]

    # 按 resample 頻率取最後一天的預測
    pred_resampled = pred_aligned.resample(resample_freq).last()

    # 建立 position DataFrame（與 adj_close 同型）
    position = pd.DataFrame(False, index=adj_close.index, columns=adj_close.columns)

    for dt in pred_resampled.index:
        scores = pred_resampled.loc[dt].dropna()
        if len(scores) < top_n:
            continue
        top_stocks = scores.nlargest(top_n).index
        # 找到此日期之後、下一期之前的所有交易日，設為 True
        mask = position.index >= dt
        next_dates = pred_resampled.index[pred_resampled.index > dt]
        if len(next_dates) > 0:
            mask = mask & (position.index < next_dates[0])
        position.loc[mask, top_stocks] = True

    # 裁切到預測範圍
    position = position.loc[common_dates[0]:]
    # 確保至少有一些 True
    n_true = position.sum().sum()
    print(f"  Position 建立完成：{n_true} 個持倉日×股票")
    return position


def run_finlab_backtest(position, top_n=10, resample_freq="W"):
    """用 finlab.backtest.sim() 執行回測"""
    from finlab.backtest import sim

    print(f"\n  執行 FinLab 回測 (resample={resample_freq}, top_n={top_n})...")
    report = sim(
        position,
        resample=resample_freq,
        position_limit=1.0 / top_n,   # 等權重
        fee_ratio=1.425 / 1000,        # 手續費 0.1425%
        stop_loss=0.08,                 # 停損 8%
        trade_at_price="open",          # 隔日開盤價成交
        upload=False,
    )
    return report


# ============================================================
# 6. 視覺化
# ============================================================

def plot_training(train_losses, val_losses, output_dir="."):
    """繪製訓練曲線"""
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(train_losses, label="Train Loss")
    ax.plot(val_losses, label="Val Loss")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MSE Loss")
    ax.set_title("Training & Validation Loss")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    path = os.path.join(output_dir, "training_loss.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  訓練曲線已儲存至 {path}")


# ============================================================
# 7. 主程式
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Transformer 股價預測器（FinLab 版）")
    parser.add_argument("--lookback", type=int, default=60, help="回看天數 (預設: 60)")
    parser.add_argument("--horizon", type=int, default=5, help="預測天數 (預設: 5)")
    parser.add_argument("--epochs", type=int, default=100, help="最大訓練 epoch (預設: 100)")
    parser.add_argument("--batch-size", type=int, default=64, help="Batch size (預設: 64)")
    parser.add_argument("--lr", type=float, default=1e-3, help="學習率 (預設: 1e-3)")
    parser.add_argument("--top-n", type=int, default=10, help="每期選幾檔 (預設: 10)")
    parser.add_argument("--max-stocks", type=int, default=100, help="訓練用最大股票數 (預設: 100)")
    parser.add_argument("--resample", default="W", choices=["W", "M"], help="換股頻率 W=週/M=月 (預設: W)")
    parser.add_argument("--train-ratio", type=float, default=0.7, help="訓練集比例 (預設: 0.7)")
    parser.add_argument("--val-ratio", type=float, default=0.15, help="驗證集比例 (預設: 0.15)")
    parser.add_argument("--no-plot", action="store_true", help="不產出圖表")
    args = parser.parse_args()

    output_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("  Transformer 股價預測器 — 場景 A（FinLab 版）")
    print("=" * 60)

    # Step 1: 載入 FinLab 資料
    print("\n[1/6] 載入 FinLab 台股資料...")
    login_finlab()
    adj_close, adj_open, adj_high, adj_low, volume, close = load_finlab_data()

    # Step 2: 篩選股票
    print("\n[2/6] 篩選流動性足夠的股票...")
    stock_ids = filter_liquid_stocks(adj_close, volume, close, min_price=10, min_volume_pct=70)

    # Step 3: 建立多股票訓練集
    print(f"\n[3/6] 建立訓練集 (lookback={args.lookback}, horizon={args.horizon}, max_stocks={args.max_stocks})...")
    X, y, meta = build_multi_stock_dataset(
        adj_close, adj_high, adj_low, volume, stock_ids,
        lookback=args.lookback, horizon=args.horizon, max_stocks=args.max_stocks,
    )
    n_features = X.shape[2]
    print(f"  資料集大小：X={X.shape}, y={y.shape}")
    print(f"  特徵數：{n_features}")

    # 用時間切割
    dates_arr = np.array([m[0] for m in meta])
    sorted_idx = np.argsort(dates_arr)
    X, y, meta = X[sorted_idx], y[sorted_idx], [meta[i] for i in sorted_idx]
    dates_arr = dates_arr[sorted_idx]

    n = len(X)
    train_end = int(n * args.train_ratio)
    val_end = int(n * (args.train_ratio + args.val_ratio))

    X_train, y_train = X[:train_end], y[:train_end]
    X_val, y_val = X[train_end:val_end], y[train_end:val_end]

    train_date_range = f"{dates_arr[0].strftime('%Y-%m-%d')} ~ {dates_arr[train_end-1].strftime('%Y-%m-%d')}"
    val_date_range = f"{dates_arr[train_end].strftime('%Y-%m-%d')} ~ {dates_arr[val_end-1].strftime('%Y-%m-%d')}"
    test_date_range = f"{dates_arr[val_end].strftime('%Y-%m-%d')} ~ {dates_arr[-1].strftime('%Y-%m-%d')}"

    print(f"\n  時間序列切割：")
    print(f"    訓練集：{len(X_train):,} 筆 ({train_date_range})")
    print(f"    驗證集：{len(X_val):,} 筆 ({val_date_range})")
    print(f"    測試期：{test_date_range}")

    # Step 4: 訓練
    print(f"\n[4/6] 訓練 Transformer (epochs={args.epochs}, batch_size={args.batch_size})...")
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
    print(f"  最佳 Val Loss:   {min(val_losses):.6f}")

    # Step 5: 對測試期所有股票做預測
    test_start = pd.Timestamp(dates_arr[val_end])
    predict_dates = adj_close.index[adj_close.index >= test_start]

    print(f"\n[5/6] 測試期預測 ({test_start.strftime('%Y-%m-%d')} ~)...")
    pred_df = predict_all_stocks(
        model, adj_close, adj_high, adj_low, volume,
        stock_ids, lookback=args.lookback, predict_dates=predict_dates,
    )

    # 建立 position
    position = build_position(pred_df, adj_close, top_n=args.top_n, resample_freq=args.resample)

    # Step 6: FinLab 回測
    print(f"\n[6/6] FinLab 回測...")
    report = run_finlab_backtest(position, top_n=args.top_n, resample_freq=args.resample)
    stats = report.get_stats()

    print("\n" + "=" * 60)
    print("  FinLab 回測績效報告")
    print("=" * 60)
    print(f"  換股頻率：{'週' if args.resample == 'W' else '月'}")
    print(f"  持股數量：{args.top_n}")
    print(f"  ---")
    for key in ["daily_mean", "daily_sharpe", "daily_sortino", "max_drawdown",
                 "winning_ratio", "profit_factor", "trading_count"]:
        if key in stats:
            val = stats[key]
            if key == "max_drawdown":
                print(f"  {key}: {val * 100:.2f}%")
            elif key == "winning_ratio":
                print(f"  {key}: {val * 100:.1f}%")
            elif key == "trading_count":
                print(f"  {key}: {val:.0f}")
            else:
                print(f"  {key}: {val:.4f}")
    print("=" * 60)

    # 圖表
    if not args.no_plot:
        plot_training(train_losses, val_losses, output_dir=output_dir)
        try:
            fig = report.display()
            if fig is not None:
                report_path = os.path.join(output_dir, "finlab_backtest.png")
                fig.savefig(report_path, dpi=150, bbox_inches="tight")
                plt.close(fig)
                print(f"  FinLab 回測圖已儲存至 {report_path}")
        except Exception as e:
            print(f"  FinLab 圖表產出失敗（不影響結果）: {e}")

    return stats, report


if __name__ == "__main__":
    main()
