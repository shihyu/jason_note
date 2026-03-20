class TaiwanStockCostModel:
    def __init__(self, commission_rate=0.001425, tax_rate=0.003, discount=0.3):
        self.commission_rate = commission_rate
        self.tax_rate = tax_rate
        self.discount = discount

    @property
    def buy_rate(self):
        return self.commission_rate * self.discount

    @property
    def sell_rate(self):
        return self.commission_rate * self.discount + self.tax_rate

    def calculate_trade_cost(self, notional, side):
        if side == "buy":
            return notional * self.buy_rate
        if side == "sell":
            return notional * self.sell_rate
        raise ValueError(f"unsupported side: {side}")

    def calculate_weight_cost(self, weight_change, side):
        if side == "buy":
            return weight_change * self.buy_rate
        if side == "sell":
            return abs(weight_change) * self.sell_rate
        raise ValueError(f"unsupported side: {side}")
