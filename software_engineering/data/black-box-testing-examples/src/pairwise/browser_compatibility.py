"""
瀏覽器相容性測試器 - Pairwise Testing 應用範例

展示如何使用 Pairwise 方法測試瀏覽器相容性
原始組合數：5×7×2×3×2 = 420
Pairwise 組合數：約 30-50（縮減 90% 以上）
"""

from src.pairwise.pict_generator import PairwiseGenerator


class BrowserCompatibilityTester:
    """瀏覽器相容性測試器"""

    def __init__(self):
        """初始化測試器"""
        self.generator = PairwiseGenerator()

        # 定義測試參數（模擬課程筆記的範例）
        self.parameters = {
            'OS': ['Windows 10', 'Windows 11', 'macOS', 'Ubuntu', 'Fedora'],
            'Browser': ['Chrome', 'Firefox', 'Safari', 'Edge', 'Opera', 'Brave', 'Vivaldi'],
            'Language': ['zh-TW', 'en-US'],
            'Resolution': ['1920x1080', '2560x1440', '3840x2160'],
            'Network': ['Fast', 'Slow']
        }

        # 定義已知的不相容組合
        self.incompatible_combinations = [
            {'OS': 'Windows 10', 'Browser': 'Safari'},
            {'OS': 'Windows 11', 'Browser': 'Safari'},
            {'OS': 'Ubuntu', 'Browser': 'Safari'},
            {'OS': 'Fedora', 'Browser': 'Safari'},
        ]

    def generate_test_cases(self):
        """
        生成 Pairwise 測試案例

        Returns:
            list: 測試案例列表
        """
        return self.generator.generate(self.parameters)

    def is_compatible(self, test_case):
        """
        檢查測試組合是否相容

        Args:
            test_case: 測試案例字典

        Returns:
            tuple: (is_compatible, reason)
        """
        # 檢查已知的不相容組合
        for incompatible in self.incompatible_combinations:
            match = all(
                test_case.get(key) == value
                for key, value in incompatible.items()
            )
            if match:
                return False, f"Incompatible: {incompatible}"

        return True, ""

    def run_test(self, test_case):
        """
        執行單一測試案例

        Args:
            test_case: 測試案例字典

        Returns:
            dict: 測試結果
        """
        # 檢查相容性
        is_compatible, reason = self.is_compatible(test_case)

        if not is_compatible:
            return {
                'test_case': test_case,
                'status': 'skip',
                'passed': False,
                'reason': reason
            }

        # 模擬測試執行（實際應用中會進行真實測試）
        # 這裡簡化為檢查一些基本規則
        passed = self._simulate_test(test_case)

        return {
            'test_case': test_case,
            'status': 'pass' if passed else 'fail',
            'passed': passed,
            'reason': '' if passed else 'Test failed'
        }

    def _simulate_test(self, test_case):
        """
        模擬測試執行

        Args:
            test_case: 測試案例

        Returns:
            bool: 測試是否通過
        """
        # 模擬一些測試規則
        # 實際應用中這裡會執行真實的瀏覽器測試

        # 規則 1：慢速網路 + 高解析度可能會有問題
        if test_case['Network'] == 'Slow' and test_case['Resolution'] == '3840x2160':
            return False

        # 規則 2：某些瀏覽器在某些語言下可能有問題
        if test_case['Browser'] == 'Vivaldi' and test_case['Language'] == 'zh-TW':
            return False

        # 其他情況視為通過
        return True

    def run_all_tests(self):
        """
        執行所有測試案例

        Returns:
            list: 所有測試結果
        """
        test_cases = self.generate_test_cases()
        results = []

        for test_case in test_cases:
            result = self.run_test(test_case)
            results.append(result)

        return results

    def get_statistics(self, results):
        """
        獲取測試統計資訊

        Args:
            results: 測試結果列表

        Returns:
            dict: 統計資訊
        """
        total = len(results)
        passed = sum(1 for r in results if r['passed'])
        failed = sum(1 for r in results if not r['passed'])
        pass_rate = (passed / total * 100) if total > 0 else 0

        return {
            'total': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': pass_rate
        }

    def filter_failing_tests(self, results):
        """
        篩選失敗的測試

        Args:
            results: 測試結果列表

        Returns:
            list: 失敗的測試結果
        """
        return [r for r in results if not r['passed']]

    def generate_coverage_report(self, test_cases):
        """
        生成覆蓋率報告

        Args:
            test_cases: 測試案例列表

        Returns:
            dict: 覆蓋率報告
        """
        coverage = self.generator.calculate_coverage(test_cases, self.parameters)
        stats = self.generator.get_statistics(self.parameters, test_cases)

        return {
            'total_cases': len(test_cases),
            'parameters_covered': list(self.parameters.keys()),
            'pairwise_coverage': coverage['pairwise_coverage'],
            'total_combinations': stats['total_combinations'],
            'reduction_ratio': stats['reduction_ratio'],
            'saved_tests': stats['saved_tests']
        }
