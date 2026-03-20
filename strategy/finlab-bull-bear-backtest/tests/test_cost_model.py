import math

from cost_model import TaiwanStockCostModel


def test_buy_cost_uses_discounted_commission_only():
    model = TaiwanStockCostModel(commission_rate=0.001425, tax_rate=0.003, discount=0.3)

    cost = model.calculate_trade_cost(notional=100000, side="buy")

    assert math.isclose(cost, 42.75, rel_tol=1e-9)


def test_sell_cost_includes_commission_and_tax():
    model = TaiwanStockCostModel(commission_rate=0.001425, tax_rate=0.003, discount=0.3)

    cost = model.calculate_trade_cost(notional=100000, side="sell")

    assert math.isclose(cost, 342.75, rel_tol=1e-9)
