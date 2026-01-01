"""
金額驗證器 - 邊界值分析範例

規格要求：金額範圍 0-1000
測試重點：
  - 左邊界：-1, 0, 1
  - 右邊界：999, 1000, 1001
  - 小數支援：99.99, 1000.01
  - 精度處理：四捨五入到兩位小數
"""


class AmountValidator:
    """金額驗證器"""

    def __init__(self, min_amount=0, max_amount=1000):
        """
        初始化驗證器

        Args:
            min_amount: 最小金額（預設 0）
            max_amount: 最大金額（預設 1000）
        """
        self.min_amount = min_amount
        self.max_amount = max_amount

    def validate(self, amount):
        """
        驗證金額是否在有效範圍內

        Args:
            amount: 要驗證的金額

        Returns:
            bool: True 表示有效，False 表示無效
        """
        if not isinstance(amount, (int, float)):
            return False

        return self.min_amount <= amount <= self.max_amount

    def validate_with_message(self, amount):
        """
        驗證金額並返回詳細訊息

        Args:
            amount: 要驗證的金額

        Returns:
            dict: 包含 'valid' 和 'message' 的字典
        """
        if not isinstance(amount, (int, float)):
            return {
                'valid': False,
                'message': '金額必須是數字'
            }

        if amount < self.min_amount:
            return {
                'valid': False,
                'message': f'金額不能小於 {self.min_amount}'
            }

        if amount > self.max_amount:
            return {
                'valid': False,
                'message': f'金額不能大於 {self.max_amount}'
            }

        return {
            'valid': True,
            'message': '金額驗證通過'
        }

    def validate_with_precision(self, amount):
        """
        驗證金額並處理精度（四捨五入到兩位小數）

        Args:
            amount: 要驗證的金額

        Returns:
            dict: 包含 'valid', 'rounded_amount', 'message' 的字典
        """
        if not isinstance(amount, (int, float)):
            return {
                'valid': False,
                'rounded_amount': 0,
                'message': '金額必須是數字'
            }

        # 四捨五入到兩位小數
        rounded = round(amount, 2)

        if rounded < self.min_amount:
            return {
                'valid': False,
                'rounded_amount': rounded,
                'message': f'金額不能小於 {self.min_amount}'
            }

        if rounded > self.max_amount:
            return {
                'valid': False,
                'rounded_amount': rounded,
                'message': f'金額不能大於 {self.max_amount}'
            }

        return {
            'valid': True,
            'rounded_amount': rounded,
            'message': '金額驗證通過'
        }
