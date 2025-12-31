"""
年齡驗證器 - 邊界值分析範例

規格要求：年齡範圍 0-120
測試重點：
  - 左邊界：-1, 0, 1
  - 右邊界：119, 120, 121
  - 中間值：30
  - 異常值：-100, 1000
"""


class AgeValidator:
    """年齡驗證器"""

    def __init__(self, min_age=0, max_age=120):
        """
        初始化驗證器

        Args:
            min_age: 最小年齡（預設 0）
            max_age: 最大年齡（預設 120）
        """
        self.min_age = min_age
        self.max_age = max_age

    def validate(self, age):
        """
        驗證年齡是否在有效範圍內

        Args:
            age: 要驗證的年齡

        Returns:
            bool: True 表示有效，False 表示無效
        """
        if not isinstance(age, (int, float)):
            return False

        return self.min_age <= age <= self.max_age

    def validate_with_message(self, age):
        """
        驗證年齡並返回詳細訊息

        Args:
            age: 要驗證的年齡

        Returns:
            dict: 包含 'valid' 和 'message' 的字典
        """
        if not isinstance(age, (int, float)):
            return {
                'valid': False,
                'message': '年齡必須是數字'
            }

        if age < self.min_age:
            return {
                'valid': False,
                'message': f'年齡不能小於 {self.min_age}'
            }

        if age > self.max_age:
            return {
                'valid': False,
                'message': f'年齡不能大於 {self.max_age}'
            }

        return {
            'valid': True,
            'message': '年齡驗證通過'
        }
