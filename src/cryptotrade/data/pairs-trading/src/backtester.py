"""
配對交易回測器 - 極簡向量化版
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import List
from dataclasses import dataclass
from itertools import product
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from strategy import StrategyParams


@dataclass
class Result:
    params: StrategyParams
    total_trades: int
    win_rate: float
    profit_factor: float
    sharpe: float
    max_dd: float
    total_return: float


class FastBacktester:
    def __init__(self, data_dir=Path("data/raw")):
        self.data_dir = data_dir
        self.commission = 0.0005
        self.slippage = 0.0002

    def load_data(self, symbols: List[str]) -> pd.DataFrame:
        dfs = []
        for sym in symbols:
            f = self.data_dir / f"{sym}.parquet"
            if f.exists():
                df = pd.read_parquet(f)
                df["symbol"] = sym
                dfs.append(df)
        if not dfs:
            raise ValueError("No data")
        df = pd.concat(dfs, ignore_index=True)
        df = df.sort_values(["open_time", "symbol"]).reset_index(drop=True)

        df["amp"] = (df["high"] - df["low"]) / df["low"]
        df["ret"] = df.groupby("symbol")["close"].pct_change()
        df["rank"] = df.groupby("open_time")["amp"].rank(
            ascending=False, method="first"
        )
        return df

    def run(self, df: pd.DataFrame, p: StrategyParams) -> Result:
        n = len(df)
        exit_amp = p.entry_amp * p.exit_amp_ratio
        stop_amp = p.entry_amp * p.stop_loss_ratio

        long_cond = (df["rank"] == 1) & (df["amp"] >= p.entry_amp)
        short_cond = (df["rank"].isin([3, 4, 5])) & (df["amp"] >= p.entry_amp)

        long_pos = long_cond.shift(1).fillna(False).astype(int)
        short_pos = short_cond.shift(1).fillna(False).astype(int)

        amp_shock = (df["amp"] < exit_amp) | (df["amp"] > stop_amp)
        long_exit = (long_pos == 1) & amp_shock
        short_exit = (short_pos == 1) & amp_shock

        trade_mask = (long_pos == 1) | (short_pos == 1)
        exit_mask = long_exit | short_exit

        long_ret = long_pos * df["ret"]
        short_ret = -short_pos * df["ret"]
        raw_ret = long_ret + short_ret - self.commission - self.slippage

        trade_ret = raw_ret[trade_mask]

        if len(trade_ret) == 0:
            return Result(p, 0, 0.0, 0.0, 0.0, 0.0, 0.0)

        wins = trade_ret[trade_ret > 0]
        losses = trade_ret[trade_ret < 0]
        win_rate = len(wins) / len(trade_ret) if len(trade_ret) > 0 else 0
        pf = (
            abs(wins.sum() / losses.sum())
            if len(losses) > 0 and losses.sum() != 0
            else float("inf")
        )

        equity = (1 + trade_ret).cumprod()
        running_max = equity.cummax()
        dd = (equity - running_max) / running_max
        max_dd = dd.min() * 100

        total_return = (equity.iloc[-1] - 1) * 100 if len(equity) > 0 else 0
        sharpe = (
            trade_ret.mean() / trade_ret.std() * np.sqrt(252 * 1440)
            if trade_ret.std() > 0
            else 0
        )

        return Result(p, len(trade_ret), win_rate, pf, sharpe, max_dd, total_return)

    def grid_search(self, df: pd.DataFrame, param_grid: dict) -> List[Result]:
        combos = [
            StrategyParams(**dict(zip(param_grid.keys(), values)))
            for values in product(*param_grid.values())
        ]
        print(f"Total: {len(combos)}")
        results = []
        for i, p in enumerate(combos):
            if (i + 1) % 20 == 0:
                print(f"Progress: {i + 1}/{len(combos)}")
            results.append(self.run(df, p))
        results.sort(key=lambda x: x.profit_factor, reverse=True)
        return results

    def save(self, results: List[Result], filepath: str):
        out = []
        for r in results:
            out.append(
                {
                    "entry_amp": r.params.entry_amp,
                    "top_n": r.params.top_n,
                    "exit_amp_ratio": r.params.exit_amp_ratio,
                    "stop_loss_ratio": r.params.stop_loss_ratio,
                    "max_hold": r.params.max_hold,
                    "total_trades": r.total_trades,
                    "win_rate": r.win_rate,
                    "profit_factor": r.profit_factor,
                    "sharpe": r.sharpe,
                    "max_dd": r.max_dd,
                    "total_return": r.total_return,
                }
            )
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(out, f, indent=2)
        print(f"Saved to {filepath}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2024-01-01")
    parser.add_argument("--end", default="2025-04-07")
    parser.add_argument("--output", default="results/backtest_results.json")
    args = parser.parse_args()

    bt = FastBacktester()
    symbols = [f.stem for f in bt.data_dir.glob("*.parquet")]
    if not symbols:
        print("No data!")
        return

    print(f"Loading {len(symbols)} symbols...")
    df = bt.load_data(symbols)
    df = df[(df["open_time"] >= args.start) & (df["open_time"] < args.end)]
    print(
        f"Rows: {len(df):,}, Range: {df['open_time'].min()} ~ {df['open_time'].max()}"
    )

    grid = {
        "entry_amp": [0.003, 0.005, 0.007, 0.01],
        "top_n": [5],
        "exit_amp_ratio": [0.3, 0.33, 0.4],
        "stop_loss_ratio": [1.5, 2.0, 2.5],
        "max_hold": [5],
    }

    results = bt.grid_search(df, grid)

    print("\n=== TOP 10 ===")
    for i, r in enumerate(results[:10]):
        print(
            f"{i + 1}. PF={r.profit_factor:.2f} Sharpe={r.sharpe:.2f} Win={r.win_rate:.1%} "
            f"Return={r.total_return:.1f}% DD={r.max_dd:.1f}% Trades={r.total_trades} "
            f"Entry={r.params.entry_amp * 100:.1f}% ExitRatio={r.params.exit_amp_ratio:.2f}"
        )

    bt.save(results, args.output)


if __name__ == "__main__":
    main()
