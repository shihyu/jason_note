"""
販賣機狀態機 - 狀態轉移測試範例

狀態圖：
[*] --> 待機
待機 --> 投幣中: 投幣
投幣中 --> 選擇商品: 金額足夠
投幣中 --> 投幣中: 繼續投幣
選擇商品 --> 出貨中: 選擇商品
出貨中 --> 找零: 出貨完成
找零 --> 待機: 找零完成
投幣中 --> 退幣: 取消
退幣 --> 待機: 退幣完成

測試覆蓋目標：
- 轉移覆蓋（Transition Coverage）：每條轉移至少執行一次
- 成對轉移覆蓋（Pair Transition Coverage）：連續的兩個轉移
"""

from transitions import Machine


class VendingMachine:
    """販賣機狀態機"""

    # 定義狀態
    states = ['待機', '投幣中', '選擇商品', '出貨中', '找零', '退幣']

    def __init__(self):
        """初始化販賣機"""
        self.balance = 0
        self.selected_product = None
        self.product_prices = {
            '可樂': 30,
            '雪碧': 30,
            '咖啡': 40,
            '茶': 25
        }

        # 定義狀態轉移
        transitions = [
            {'trigger': 'insert_coin', 'source': '待機', 'dest': '投幣中', 'before': 'add_balance'},
            {'trigger': 'insert_coin', 'source': '投幣中', 'dest': '投幣中', 'before': 'add_balance'},
            {'trigger': 'confirm_amount', 'source': '投幣中', 'dest': '選擇商品'},
            {'trigger': 'select_product', 'source': '選擇商品', 'dest': '出貨中', 'before': 'set_product',
             'conditions': 'has_sufficient_balance'},
            {'trigger': 'dispense', 'source': '出貨中', 'dest': '找零'},
            {'trigger': 'return_change', 'source': '找零', 'dest': '待機', 'before': 'reset_balance'},
            {'trigger': 'cancel', 'source': '投幣中', 'dest': '退幣'},
            {'trigger': 'complete_refund', 'source': '退幣', 'dest': '待機', 'before': 'reset_balance'}
        ]

        # 初始化狀態機
        self.machine = Machine(
            model=self,
            states=VendingMachine.states,
            transitions=transitions,
            initial='待機'
        )

        self._coin_amount = 0

    def add_balance(self, amount):
        """增加餘額"""
        self._coin_amount = amount
        self.balance += amount

    def has_sufficient_balance(self, product_name):
        """檢查餘額是否足夠"""
        if product_name not in self.product_prices:
            return False
        return self.balance >= self.product_prices[product_name]

    def set_product(self, product_name):
        """設定選擇的商品"""
        self.selected_product = product_name

    def reset_balance(self):
        """重置餘額"""
        change = self.balance
        self.balance = 0
        self._coin_amount = 0
        self.selected_product = None
        return change

    def get_state(self):
        """獲取當前狀態"""
        return self.state

    def get_balance(self):
        """獲取當前餘額"""
        return self.balance

    # 重載 select_product 以處理失敗情況
    def select_product(self, product_name):
        """選擇商品"""
        if self.state != '選擇商品':
            return {
                'success': False,
                'message': '請先投幣並確認金額'
            }

        if product_name not in self.product_prices:
            return {
                'success': False,
                'message': '商品不存在'
            }

        if not self.has_sufficient_balance(product_name):
            return {
                'success': False,
                'message': f'餘額不足，需要 {self.product_prices[product_name]}，目前餘額 {self.balance}'
            }

        # 觸發狀態轉移
        self.trigger('select_product', product_name)

        return {
            'success': True,
            'message': f'已選擇 {product_name}'
        }

    def return_change(self):
        """找零並返回金額"""
        if self.selected_product:
            price = self.product_prices[self.selected_product]
            change = self.balance - price
            self.trigger('return_change')
            return change
        return self.reset_balance()

    def complete_refund(self):
        """完成退幣"""
        refund = self.balance
        self.trigger('complete_refund')
        return refund
