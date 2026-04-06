"""
績效分析器

分析回測結果，生成報告
"""

import json
import pandas as pd
from pathlib import Path
from typing import List, Dict
import argparse


def load_results(filepath: str) -> List[Dict]:
    with open(filepath, "r") as f:
        return json.load(f)


def analyze_results(results: List[Dict]) -> pd.DataFrame:
    df = pd.DataFrame(results)
    df["entry_amp_pct"] = df["entry_amp"] * 100

    df = df.sort_values("profit_factor", ascending=False)

    top_100 = df.head(100)

    print("\n" + "=" * 60)
    print("PAIRS TRADING BACKTEST ANALYSIS")
    print("=" * 60)

    print(f"\nTotal configurations tested: {len(df)}")
    print(f"Configurations with PF > 2.0: {len(df[df['profit_factor'] > 2.0])}")
    print(f"Configurations with Sharpe > 1.5: {len(df[df['sharpe_ratio'] > 1.5])}")

    print("\n" + "-" * 60)
    print("TOP 20 BY PROFIT FACTOR")
    print("-" * 60)

    for i, row in top_100.head(20).iterrows():
        print(
            f"PF={row['profit_factor']:.2f} Sharpe={row['sharpe_ratio']:.2f} "
            f"Win={row['win_rate']:.1%} Return={row['total_return']:.1f}% "
            f"DD={row['max_drawdown']:.1%} Trades={row['total_trades']}"
        )
        print(
            f"  Params: entry={row['entry_amp_pct']:.1f}% top={row['top_n']} "
            f"exit_ratio={row['exit_amp_ratio']:.2f} sl_ratio={row['stop_loss_ratio']:.1f} "
            f"max_hold={row['max_hold']}"
        )

    print("\n" + "-" * 60)
    print("BEST BY PROFIT FACTOR")
    print("-" * 60)
    best_pf = df.iloc[0]
    print(f"Profit Factor: {best_pf['profit_factor']:.4f}")
    print(f"Sharpe Ratio: {best_pf['sharpe_ratio']:.4f}")
    print(f"Win Rate: {best_pf['win_rate']:.2%}")
    print(f"Total Return: {best_pf['total_return']:.2f}%")
    print(f"Max Drawdown: {best_pf['max_drawdown']:.2%}")
    print(f"Total Trades: {best_pf['total_trades']}")
    print(f"Parameters:")
    print(f"  entry_amp: {best_pf['entry_amp_pct']:.2f}%")
    print(f"  top_n: {best_pf['top_n']}")
    print(f"  exit_amp_ratio: {best_pf['exit_amp_ratio']:.2f}")
    print(f"  stop_loss_ratio: {best_pf['stop_loss_ratio']:.2f}")
    print(f"  max_hold: {best_pf['max_hold']} minutes")

    print("\n" + "-" * 60)
    print("PARAMETER ANALYSIS")
    print("-" * 60)

    param_impact = {}
    for param in [
        "entry_amp",
        "top_n",
        "exit_amp_ratio",
        "stop_loss_ratio",
        "max_hold",
    ]:
        grouped = (
            df.groupby(param)
            .agg(
                {
                    "profit_factor": "mean",
                    "sharpe_ratio": "mean",
                    "win_rate": "mean",
                    "total_return": "mean",
                    "total_trades": "sum",
                }
            )
            .sort_values("profit_factor", ascending=False)
        )

        print(f"\n{param}:")
        print(grouped.round(3))

        best_val = grouped["profit_factor"].idxmax()
        param_impact[param] = best_val

    print("\n" + "-" * 60)
    print("RECOMMENDED PARAMETERS")
    print("-" * 60)
    for param, val in param_impact.items():
        print(f"  {param}: {val}")

    return df


def main():
    parser = argparse.ArgumentParser(description="分析回測結果")
    parser.add_argument(
        "--input", default="results/backtest_results.json", help="回測結果JSON檔案路徑"
    )
    parser.add_argument("--output", default=None, help="輸出CSV檔案路徑")
    args = parser.parse_args()

    results = load_results(args.input)
    df = analyze_results(results)

    if args.output:
        df.to_csv(args.output, index=False)
        print(f"\nResults exported to {args.output}")


if __name__ == "__main__":
    main()
