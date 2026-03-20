from __future__ import annotations

import argparse

from backtest_runner import BacktestRunner
from config import StrategyConfig
from cost_model import TaiwanStockCostModel
from data_loader import DataLoader
from regime import MarketRegimeClassifier
from signal_builder import SignalBuilder


def build_parser():
    parser = argparse.ArgumentParser(description="FinLab 牛熊多空回測")
    parser.add_argument("--start-date", default=StrategyConfig.start_date)
    parser.add_argument("--end-date", default=StrategyConfig.end_date)
    parser.add_argument("--debug", action="store_true")
    return parser


def run_backtest(start_date: str, end_date: str | None, debug: bool = False):
    config = StrategyConfig(start_date=start_date, end_date=end_date)
    loader = DataLoader(start_date=config.start_date, end_date=config.end_date)
    weekly_close, weekly_volume, weekly_benchmark = loader.load_weekly_data()

    classifier = MarketRegimeClassifier(ma_window=config.ma_window, flat_tolerance=config.flat_tolerance)
    regimes = classifier.classify(weekly_benchmark)

    builder = SignalBuilder(
        ma_window=config.ma_window,
        breakout_window=config.breakout_window,
        volume_window=config.volume_window,
        relative_strength_window=config.relative_strength_window,
        top_n=config.top_n,
        require_52_week_high=config.require_52_week_high,
    )
    target_weights = builder.build_target_weights(
        close=weekly_close,
        volume=weekly_volume,
        benchmark=weekly_benchmark,
        regimes=regimes,
    )

    runner = BacktestRunner(
        cost_model=TaiwanStockCostModel(
            commission_rate=config.commission_rate,
            tax_rate=config.tax_rate,
            discount=config.discount,
        ),
        initial_capital=config.initial_capital,
    )
    result = runner.run(positions=target_weights, prices=weekly_close)

    print("FinLab 牛熊多空回測")
    print(f"區間: {config.start_date} ~ {config.end_date or '最新'}")
    print(f"最終報酬: {result['metrics']['total_return'] * 100:.2f}%")
    print(f"CAGR: {result['metrics']['cagr'] * 100:.2f}%")
    print(f"Sharpe: {result['metrics']['sharpe']:.2f}")
    print(f"Max Drawdown: {result['metrics']['max_drawdown'] * 100:.2f}%")
    print(f"交易次數: {result['metrics']['total_trades']}")
    print(f"總成本占比: {result['metrics']['total_cost_ratio'] * 100:.2f}%")

    if debug:
        print(f"牛市週數: {(regimes == 'bull').sum()}")
        print(f"持股週數: {(target_weights.sum(axis=1) > 0).sum()}")

    return result


if __name__ == "__main__":
    args = build_parser().parse_args()
    run_backtest(start_date=args.start_date, end_date=args.end_date, debug=args.debug)
