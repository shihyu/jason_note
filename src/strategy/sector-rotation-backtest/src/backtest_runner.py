"""
回測執行器

執行三個策略的完整回測並生成報告
"""
import pandas as pd
import os
from data_loader import DataLoader
from strategy1_relative_strength import RelativeStrengthStrategy
from strategy2_synchronization import SynchronizationStrategy
from strategy3_combined import CombinedStrategy


class BacktestRunner:
    """回測執行器"""

    def __init__(self, start_date='2020-01-01', end_date=None, output_dir='results'):
        """
        初始化回測執行器

        Args:
            start_date: 回測起始日期
            end_date: 回測結束日期（None = 最新日期）
            output_dir: 結果輸出目錄
        """
        self.start_date = start_date
        self.end_date = end_date
        self.output_dir = output_dir

        # 初始化數據載入器
        self.loader = DataLoader(start_date=start_date)

        # 初始化三個策略
        self.strategy1 = RelativeStrengthStrategy(self.loader)
        self.strategy2 = SynchronizationStrategy(self.loader)
        self.strategy3 = CombinedStrategy(self.loader)

    def run_all_strategies(self):
        """
        執行所有策略的回測

        Returns:
            dict: {策略名稱: 回測結果}
        """
        print("=" * 60)
        print("開始執行台股族群輪動策略回測")
        print("=" * 60)
        print(f"回測區間：{self.start_date} ~ {self.end_date or '最新'}")
        print()

        results = {}

        # 策略 1：相對強弱法
        print("執行策略 1：族群相對強弱法...")
        results['strategy1'] = self.strategy1.backtest(
            period=10,
            top_pct=0.2,
            n_stocks=10,
            start_date=self.start_date,
            end_date=self.end_date
        )
        print(f"  ✓ 完成（CAGR: {self.format_percentage(results['strategy1']['cagr'])}）")

        # 策略 2：同步性法
        print("執行策略 2：族群同步性法...")
        results['strategy2'] = self.strategy2.backtest(
            ma_period=20,
            sync_threshold=0.3,
            n_stocks=15,
            start_date=self.start_date,
            end_date=self.end_date
        )
        print(f"  ✓ 完成（CAGR: {self.format_percentage(results['strategy2']['cagr'])}）")

        # 策略 3：綜合法
        print("執行策略 3：綜合法...")
        results['strategy3'] = self.strategy3.backtest(
            rs_period=10,
            rs_top_pct=0.3,
            sync_threshold=0.3,
            volume_period=3,
            n_stocks=15,
            start_date=self.start_date,
            end_date=self.end_date
        )
        print(f"  ✓ 完成（CAGR: {self.format_percentage(results['strategy3']['cagr'])}）")

        print()
        return results

    def format_percentage(self, value):
        """
        格式化百分比

        Args:
            value: 數值（0.123 = 12.3%）

        Returns:
            str: 格式化後的字串
        """
        if value is None:
            return "N/A"
        return f"{value * 100:.2f}%"

    def generate_strategy_report(self, strategy_name, result):
        """
        生成單一策略的報告

        Args:
            strategy_name: 策略名稱
            result: 回測結果

        Returns:
            str: 報告內容
        """
        report = []
        report.append("=" * 60)
        report.append(f"{strategy_name}")
        report.append("=" * 60)
        report.append("")

        # 績效指標
        report.append("績效指標")
        report.append("-" * 60)
        report.append(f"年化報酬率（CAGR）        : {self.format_percentage(result['cagr'])}")
        report.append(f"Sharpe Ratio             : {result['sharpe']:.2f}" if result['sharpe'] is not None else "Sharpe Ratio             : N/A")
        report.append(f"最大回撤（Max Drawdown）  : {self.format_percentage(result['max_drawdown'])}")
        report.append(f"勝率（Win Rate）          : {self.format_percentage(result['win_rate'])}")
        report.append(f"總交易次數                : {result['total_trades']}")
        report.append("")

        # 計算平均持股數
        if 'strategy_returns' in result:
            avg_holdings = result.get('avg_holdings', 'N/A')
            report.append(f"月均持股檔數              : {avg_holdings}")
            report.append("")

        # 累積報酬曲線摘要
        if 'cum_returns' in result and result['cum_returns'] is not None:
            cum_returns = result['cum_returns']
            report.append("累積報酬曲線摘要")
            report.append("-" * 60)
            report.append(f"起始日期                  : {cum_returns.index[0].strftime('%Y-%m-%d')}")
            report.append(f"結束日期                  : {cum_returns.index[-1].strftime('%Y-%m-%d')}")
            report.append(f"最終累積報酬              : {self.format_percentage(cum_returns.iloc[-1] - 1)}")
            report.append("")

        return "\n".join(report)

    def generate_comparison_table(self, results):
        """
        生成三個策略的對比表格

        Args:
            results: run_all_strategies 的返回值

        Returns:
            DataFrame: 對比表格
        """
        comparison_data = {
            '策略名稱': [
                '策略1相對強弱',
                '策略2同步性',
                '策略3綜合法'
            ],
            '年化報酬': [
                self.format_percentage(results['strategy1']['cagr']),
                self.format_percentage(results['strategy2']['cagr']),
                self.format_percentage(results['strategy3']['cagr'])
            ],
            'Sharpe': [
                f"{results['strategy1']['sharpe']:.2f}" if results['strategy1']['sharpe'] is not None else "N/A",
                f"{results['strategy2']['sharpe']:.2f}" if results['strategy2']['sharpe'] is not None else "N/A",
                f"{results['strategy3']['sharpe']:.2f}" if results['strategy3']['sharpe'] is not None else "N/A"
            ],
            '最大回撤': [
                self.format_percentage(results['strategy1']['max_drawdown']),
                self.format_percentage(results['strategy2']['max_drawdown']),
                self.format_percentage(results['strategy3']['max_drawdown'])
            ],
            '勝率': [
                self.format_percentage(results['strategy1']['win_rate']),
                self.format_percentage(results['strategy2']['win_rate']),
                self.format_percentage(results['strategy3']['win_rate'])
            ],
            '總交易次數': [
                results['strategy1']['total_trades'],
                results['strategy2']['total_trades'],
                results['strategy3']['total_trades']
            ]
        }

        df = pd.DataFrame(comparison_data)
        df.set_index('策略名稱', inplace=True)

        return df

    def find_best_strategy(self, comparison_df):
        """
        找出最優策略（基於 Sharpe Ratio）

        Args:
            comparison_df: 對比表格

        Returns:
            str: 最優策略名稱
        """
        # 將 Sharpe 欄位轉換為數值
        sharpe_values = []
        for idx, row in comparison_df.iterrows():
            sharpe_str = row['Sharpe']
            if sharpe_str == 'N/A':
                sharpe_values.append(-999)  # 給一個很小的值
            else:
                sharpe_values.append(float(sharpe_str))

        # 找出最大 Sharpe 的策略
        best_idx = sharpe_values.index(max(sharpe_values))
        best_strategy = comparison_df.index[best_idx]

        return best_strategy

    def save_results(self, results):
        """
        儲存回測結果到檔案

        Args:
            results: run_all_strategies 的返回值
        """
        # 建立輸出目錄
        os.makedirs(self.output_dir, exist_ok=True)

        # 儲存三個策略的報告
        reports = {
            'strategy1_report.txt': self.generate_strategy_report(
                "策略1：族群相對強弱法", results['strategy1']
            ),
            'strategy2_report.txt': self.generate_strategy_report(
                "策略2：族群同步性法", results['strategy2']
            ),
            'strategy3_report.txt': self.generate_strategy_report(
                "策略3：綜合法", results['strategy3']
            )
        }

        for filename, content in reports.items():
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ 已儲存：{filepath}")

        # 儲存對比表格
        comparison = self.generate_comparison_table(results)
        comparison_path = os.path.join(self.output_dir, 'comparison.csv')
        comparison.to_csv(comparison_path, encoding='utf-8-sig')  # 使用 utf-8-sig 以支援 Excel 開啟
        print(f"  ✓ 已儲存：{comparison_path}")

        # 顯示對比表格
        print()
        print("=" * 60)
        print("三策略績效對比")
        print("=" * 60)
        print(comparison.to_string())
        print()

        # 顯示最優策略
        best = self.find_best_strategy(comparison)
        print(f"🏆 最優策略（基於 Sharpe Ratio）：{best}")
        print()

    def run(self):
        """執行完整回測流程"""
        # 執行回測
        results = self.run_all_strategies()

        # 儲存結果
        print("儲存結果...")
        self.save_results(results)

        print("=" * 60)
        print("回測完成！")
        print("=" * 60)


def main():
    """主函數"""
    # 建立回測執行器（使用 plan.md 的預設參數）
    runner = BacktestRunner(
        start_date='2020-01-01',
        end_date=None  # 使用最新日期
    )

    # 執行回測
    runner.run()


if __name__ == '__main__':
    main()
