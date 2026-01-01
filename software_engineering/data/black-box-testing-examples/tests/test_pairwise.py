"""
組合測試（Pairwise Testing）

測試方法：成對組合測試
適用對象：多輸入參數交互作用
核心理念：用最少的測試案例，覆蓋所有兩兩參數組合
"""

import pytest
from src.pairwise.browser_compatibility import BrowserCompatibilityTester
from src.pairwise.pict_generator import PairwiseGenerator


class TestPairwiseGenerator:
    """測試 Pairwise 組合生成器"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.generator = PairwiseGenerator()

    def test_simple_pairwise_generation(self):
        """測試：簡單的兩參數組合生成"""
        parameters = {
            'OS': ['Windows', 'Mac', 'Linux'],
            'Browser': ['Chrome', 'Firefox']
        }

        pairs = self.generator.generate(parameters)

        # 驗證有生成結果
        assert len(pairs) > 0

        # 驗證每個組合都包含所有參數
        for pair in pairs:
            assert 'OS' in pair
            assert 'Browser' in pair

    def test_complex_pairwise_generation(self):
        """測試：複雜的多參數組合生成"""
        parameters = {
            'OS': ['Windows', 'Mac', 'Linux'],
            'Browser': ['Chrome', 'Firefox', 'Safari'],
            'Language': ['zh-TW', 'en-US']
        }

        pairs = self.generator.generate(parameters)

        # 驗證組合數量遠小於全組合
        total_combinations = 3 * 3 * 2  # 18
        assert len(pairs) < total_combinations

        # 驗證每個組合的結構
        for pair in pairs:
            assert len(pair) == 3
            assert pair['OS'] in parameters['OS']
            assert pair['Browser'] in parameters['Browser']
            assert pair['Language'] in parameters['Language']

    def test_pairwise_coverage(self):
        """測試：驗證 Pairwise 覆蓋率"""
        parameters = {
            'Color': ['Red', 'Green', 'Blue'],
            'Size': ['Small', 'Large']
        }

        pairs = self.generator.generate(parameters)
        coverage = self.generator.calculate_coverage(pairs, parameters)

        # Pairwise 應該達到 100% 的兩兩組合覆蓋率
        assert coverage['pairwise_coverage'] == 100.0

    def test_large_combination_reduction(self):
        """測試：大型組合的縮減效果"""
        # 模擬課程筆記的範例：5×7×2×3×2 = 420 種組合
        parameters = {
            'OS': ['Windows 10', 'Windows 11', 'macOS', 'Ubuntu', 'Fedora'],
            'Browser': ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave', 'Vivaldi'],
            'Language': ['zh-TW', 'en-US'],
            'Resolution': ['1920x1080', '2560x1440', '3840x2160'],
            'Network': ['Fast', 'Slow']
        }

        pairs = self.generator.generate(parameters)

        total_combinations = 5 * 7 * 2 * 3 * 2  # 420
        reduction_ratio = len(pairs) / total_combinations

        # 驗證組合數大幅縮減（應該小於 20%）
        assert len(pairs) < total_combinations
        assert reduction_ratio < 0.2

        # 輸出統計資訊
        print(f"\n組合縮減效果：")
        print(f"  全組合數：{total_combinations}")
        print(f"  Pairwise 組合數：{len(pairs)}")
        print(f"  縮減比例：{reduction_ratio:.2%}")
        print(f"  節省測試數：{total_combinations - len(pairs)}")


class TestBrowserCompatibilityTester:
    """測試瀏覽器相容性測試器"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.tester = BrowserCompatibilityTester()

    def test_generate_test_cases(self):
        """測試：生成瀏覽器相容性測試案例"""
        test_cases = self.tester.generate_test_cases()

        # 驗證有生成測試案例
        assert len(test_cases) > 0

        # 驗證每個測試案例的結構
        for case in test_cases:
            assert 'OS' in case
            assert 'Browser' in case
            assert 'Language' in case
            assert 'Resolution' in case
            assert 'Network' in case

    def test_run_compatibility_test(self):
        """測試：執行單一相容性測試"""
        test_case = {
            'OS': 'Windows 10',
            'Browser': 'Chrome',
            'Language': 'zh-TW',
            'Resolution': '1920x1080',
            'Network': 'Fast'
        }

        result = self.tester.run_test(test_case)

        # 驗證測試結果結構
        assert 'test_case' in result
        assert 'status' in result
        assert 'passed' in result
        assert result['status'] in ['pass', 'fail', 'skip']

    def test_run_all_tests(self):
        """測試：執行所有相容性測試"""
        results = self.tester.run_all_tests()

        # 驗證有測試結果
        assert len(results) > 0

        # 驗證統計資訊
        stats = self.tester.get_statistics(results)
        assert 'total' in stats
        assert 'passed' in stats
        assert 'failed' in stats
        assert 'pass_rate' in stats

        # 驗證數字合理性
        assert stats['total'] == stats['passed'] + stats['failed']
        assert 0 <= stats['pass_rate'] <= 100

    def test_filter_failing_combinations(self):
        """測試：篩選失敗的組合"""
        results = self.tester.run_all_tests()
        failing = self.tester.filter_failing_tests(results)

        # 驗證篩選結果
        assert isinstance(failing, list)

        # 所有失敗的測試都應該被篩選出來
        for result in failing:
            assert result['passed'] is False

    def test_known_incompatible_combination(self):
        """測試：已知不相容的組合"""
        # Safari 只在 macOS 上可用
        test_case = {
            'OS': 'Windows 10',
            'Browser': 'Safari',
            'Language': 'zh-TW',
            'Resolution': '1920x1080',
            'Network': 'Fast'
        }

        result = self.tester.run_test(test_case)

        # 驗證這個不相容的組合會被標記為失敗或跳過
        assert result['status'] in ['fail', 'skip']
        if result['status'] == 'skip':
            assert 'incompatible' in result.get('reason', '').lower()

    def test_coverage_report(self):
        """測試：生成覆蓋率報告"""
        test_cases = self.tester.generate_test_cases()
        report = self.tester.generate_coverage_report(test_cases)

        # 驗證報告結構
        assert 'total_cases' in report
        assert 'parameters_covered' in report
        assert 'pairwise_coverage' in report

        # 輸出報告
        print(f"\n覆蓋率報告：")
        print(f"  測試案例數：{report['total_cases']}")
        print(f"  參數覆蓋：{report['parameters_covered']}")
        print(f"  Pairwise 覆蓋率：{report['pairwise_coverage']:.2f}%")
