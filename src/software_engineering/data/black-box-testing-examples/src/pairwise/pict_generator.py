"""
Pairwise 組合生成器

使用 AllPairs 演算法生成成對組合測試案例
核心理念：確保任意兩個參數的所有配對都至少測試過一次
"""

from allpairspy import AllPairs
from itertools import combinations


class PairwiseGenerator:
    """Pairwise 組合生成器"""

    def generate(self, parameters):
        """
        生成 Pairwise 測試組合

        Args:
            parameters: 參數字典，格式如 {'param1': [values...], 'param2': [values...]}

        Returns:
            list: Pairwise 測試組合列表
        """
        if not parameters:
            return []

        # 準備參數名稱和值
        param_names = list(parameters.keys())
        param_values = [parameters[name] for name in param_names]

        # 生成 Pairwise 組合
        pairs = []
        for combination in AllPairs(param_values):
            pair_dict = {
                param_names[i]: combination[i]
                for i in range(len(param_names))
            }
            pairs.append(pair_dict)

        return pairs

    def calculate_coverage(self, test_cases, parameters):
        """
        計算 Pairwise 覆蓋率

        Args:
            test_cases: 測試案例列表
            parameters: 原始參數字典

        Returns:
            dict: 包含覆蓋率統計的字典
        """
        if not test_cases or not parameters:
            return {
                'pairwise_coverage': 0.0,
                'covered_pairs': 0,
                'total_pairs': 0
            }

        # 計算所有可能的兩兩組合
        param_names = list(parameters.keys())
        all_pairs = set()

        for param1, param2 in combinations(param_names, 2):
            for val1 in parameters[param1]:
                for val2 in parameters[param2]:
                    all_pairs.add((param1, val1, param2, val2))

        # 計算測試案例覆蓋的兩兩組合
        covered_pairs = set()
        for test_case in test_cases:
            for param1, param2 in combinations(param_names, 2):
                if param1 in test_case and param2 in test_case:
                    pair = (param1, test_case[param1], param2, test_case[param2])
                    covered_pairs.add(pair)

        # 計算覆蓋率
        total_pairs = len(all_pairs)
        covered = len(covered_pairs)
        coverage = (covered / total_pairs * 100) if total_pairs > 0 else 0

        return {
            'pairwise_coverage': coverage,
            'covered_pairs': covered,
            'total_pairs': total_pairs
        }

    def get_statistics(self, parameters, test_cases):
        """
        獲取統計資訊

        Args:
            parameters: 參數字典
            test_cases: 測試案例列表

        Returns:
            dict: 統計資訊
        """
        # 計算全組合數
        total_combinations = 1
        for values in parameters.values():
            total_combinations *= len(values)

        # 計算覆蓋率
        coverage = self.calculate_coverage(test_cases, parameters)

        return {
            'total_parameters': len(parameters),
            'total_combinations': total_combinations,
            'pairwise_cases': len(test_cases),
            'reduction_ratio': len(test_cases) / total_combinations if total_combinations > 0 else 0,
            'saved_tests': total_combinations - len(test_cases),
            'pairwise_coverage': coverage['pairwise_coverage']
        }
