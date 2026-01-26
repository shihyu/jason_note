"""
測試回測執行器
"""
import pytest
import pandas as pd
import os
import sys

# 加入 src 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backtest_runner import BacktestRunner


class TestBacktestRunner:
    """測試回測執行器"""

    @pytest.fixture
    def runner(self):
        """建立測試用 BacktestRunner"""
        return BacktestRunner(
            start_date='2023-01-01',
            end_date='2023-12-31'
        )

    def test_run_all_strategies(self, runner):
        """測試執行所有策略"""
        results = runner.run_all_strategies()

        # 驗證返回三個策略的結果
        assert isinstance(results, dict), "結果應該是字典"
        assert len(results) == 3, "應該有三個策略的結果"

        # 驗證包含三個策略
        assert 'strategy1' in results, "應包含策略1"
        assert 'strategy2' in results, "應包含策略2"
        assert 'strategy3' in results, "應包含策略3"

        # 驗證每個策略的結果結構
        for strategy_name, result in results.items():
            assert isinstance(result, dict), f"{strategy_name} 的結果應該是字典"

            # 驗證包含關鍵指標
            required_keys = ['cagr', 'sharpe', 'max_drawdown', 'win_rate', 'total_trades']
            for key in required_keys:
                assert key in result, f"{strategy_name} 應包含 {key}"

    def test_generate_comparison_table(self, runner):
        """測試生成對比表格"""
        # 先執行回測
        results = runner.run_all_strategies()

        # 生成對比表格
        comparison = runner.generate_comparison_table(results)

        # 驗證對比表格格式
        assert isinstance(comparison, pd.DataFrame), "對比表格應該是 DataFrame"

        # 驗證包含三個策略
        assert len(comparison) == 3, "應該有三列（三個策略）"

        # 驗證包含關鍵欄位
        required_columns = ['年化報酬', 'Sharpe', '最大回撤', '勝率', '總交易次數']
        for col in required_columns:
            assert col in comparison.columns, f"應包含欄位 {col}"

    def test_format_percentage(self, runner):
        """測試百分比格式化"""
        # 測試正常百分比
        assert runner.format_percentage(0.123) == "12.30%"
        assert runner.format_percentage(-0.456) == "-45.60%"

        # 測試 None 值
        assert runner.format_percentage(None) == "N/A"

        # 測試極小值
        assert runner.format_percentage(0.001) == "0.10%"

    def test_generate_strategy_report(self, runner):
        """測試生成策略報告"""
        # 執行一個策略
        results = runner.run_all_strategies()
        result1 = results['strategy1']

        # 生成報告
        report = runner.generate_strategy_report(
            strategy_name="策略1：相對強弱法",
            result=result1
        )

        # 驗證報告是字串
        assert isinstance(report, str), "報告應該是字串"

        # 驗證報告包含關鍵資訊
        assert "策略1：相對強弱法" in report, "報告應包含策略名稱"
        assert "年化報酬率" in report, "報告應包含年化報酬率"
        assert "Sharpe Ratio" in report, "報告應包含 Sharpe Ratio"
        assert "最大回撤" in report, "報告應包含最大回撤"
        assert "勝率" in report, "報告應包含勝率"

    def test_save_results(self, runner, tmp_path):
        """測試儲存結果到檔案"""
        # 執行回測
        results = runner.run_all_strategies()

        # 修改輸出目錄到臨時路徑
        runner.output_dir = str(tmp_path)

        # 儲存結果
        runner.save_results(results)

        # 驗證檔案存在
        assert (tmp_path / "strategy1_report.txt").exists(), "應產生策略1報告"
        assert (tmp_path / "strategy2_report.txt").exists(), "應產生策略2報告"
        assert (tmp_path / "strategy3_report.txt").exists(), "應產生策略3報告"
        assert (tmp_path / "comparison.csv").exists(), "應產生對比表格"

        # 驗證報告內容
        report1_content = (tmp_path / "strategy1_report.txt").read_text(encoding='utf-8')
        assert len(report1_content) > 0, "報告內容不應為空"
        assert "策略1" in report1_content, "報告應包含策略名稱"

        # 驗證 CSV 內容
        comparison_df = pd.read_csv(tmp_path / "comparison.csv", index_col=0)
        assert len(comparison_df) == 3, "對比表格應該有三列"

    def test_find_best_strategy(self, runner):
        """測試找出最優策略"""
        # 執行回測
        results = runner.run_all_strategies()
        comparison = runner.generate_comparison_table(results)

        # 找出最優策略
        best = runner.find_best_strategy(comparison)

        # 驗證返回字串
        assert isinstance(best, str), "最優策略應該是字串"

        # 驗證是三個策略之一
        assert best in ['策略1相對強弱', '策略2同步性', '策略3綜合法'], \
            f"最優策略應該是三個策略之一，實際為 {best}"
