"""
會員折扣計算器 - 決策表測試範例

決策表：
條件：
1. 會員等級：金卡/銀卡
2. 購買金額：≥1000/<1000
3. 使用優惠券：是/否

總組合數：2^3 = 8 種情境

決策規則：
| 規則 | 會員等級 | 金額≥1000 | 有優惠券 | 折扣率 |
|------|---------|-----------|---------|--------|
| 1    | 金卡    | 是        | 是      | 25%    |
| 2    | 金卡    | 是        | 否      | 20%    |
| 3    | 金卡    | 否        | 是      | 15%    |
| 4    | 金卡    | 否        | 否      | 10%    |
| 5    | 銀卡    | 是        | 是      | 15%    |
| 6    | 銀卡    | 是        | 否      | 10%    |
| 7    | 銀卡    | 否        | 是      | 10%    |
| 8    | 銀卡    | 否        | 否      | 5%     |
"""


class MembershipDiscountCalculator:
    """會員折扣計算器"""

    def __init__(self):
        """初始化計算器"""
        # 定義決策表
        self.decision_table = [
            # 規則 1：金卡 + 高金額 + 有券
            {
                'conditions': {
                    'member_level': 'gold',
                    'high_amount': True,
                    'has_coupon': True
                },
                'discount_rate': 0.25
            },
            # 規則 2：金卡 + 高金額 + 無券
            {
                'conditions': {
                    'member_level': 'gold',
                    'high_amount': True,
                    'has_coupon': False
                },
                'discount_rate': 0.20
            },
            # 規則 3：金卡 + 低金額 + 有券
            {
                'conditions': {
                    'member_level': 'gold',
                    'high_amount': False,
                    'has_coupon': True
                },
                'discount_rate': 0.15
            },
            # 規則 4：金卡 + 低金額 + 無券
            {
                'conditions': {
                    'member_level': 'gold',
                    'high_amount': False,
                    'has_coupon': False
                },
                'discount_rate': 0.10
            },
            # 規則 5：銀卡 + 高金額 + 有券
            {
                'conditions': {
                    'member_level': 'silver',
                    'high_amount': True,
                    'has_coupon': True
                },
                'discount_rate': 0.15
            },
            # 規則 6：銀卡 + 高金額 + 無券
            {
                'conditions': {
                    'member_level': 'silver',
                    'high_amount': True,
                    'has_coupon': False
                },
                'discount_rate': 0.10
            },
            # 規則 7：銀卡 + 低金額 + 有券
            {
                'conditions': {
                    'member_level': 'silver',
                    'high_amount': False,
                    'has_coupon': True
                },
                'discount_rate': 0.10
            },
            # 規則 8：銀卡 + 低金額 + 無券
            {
                'conditions': {
                    'member_level': 'silver',
                    'high_amount': False,
                    'has_coupon': False
                },
                'discount_rate': 0.05
            }
        ]

    def calculate(self, member_level, amount, has_coupon):
        """
        計算折扣

        Args:
            member_level: 會員等級（'gold', 'silver', 'none'）
            amount: 購買金額
            has_coupon: 是否使用優惠券

        Returns:
            dict: 包含折扣率和最終金額的字典
        """
        # 非會員無折扣
        if member_level == 'none':
            return {
                'discount_rate': 0.0,
                'final_amount': amount
            }

        # 判斷是否為高金額
        high_amount = amount >= 1000

        # 查找匹配的規則
        discount_rate = 0.0
        for rule in self.decision_table:
            conditions = rule['conditions']
            if (conditions['member_level'] == member_level and
                conditions['high_amount'] == high_amount and
                conditions['has_coupon'] == has_coupon):
                discount_rate = rule['discount_rate']
                break

        # 計算最終金額
        discount_amount = amount * discount_rate
        final_amount = amount - discount_amount

        return {
            'discount_rate': discount_rate,
            'discount_amount': discount_amount,
            'final_amount': final_amount
        }

    def get_decision_table(self):
        """
        獲取決策表

        Returns:
            list: 決策表規則列表
        """
        return self.decision_table
