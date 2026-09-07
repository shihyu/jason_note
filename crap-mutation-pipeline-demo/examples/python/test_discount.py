import pytest

from discount import calculate_discount


def test_member_gets_20_percent_off():
    assert calculate_discount(100, True) == 80


def test_non_member_pays_full_price():
    assert calculate_discount(100, False) == 100


def test_negative_price_raises():
    with pytest.raises(ValueError):
        calculate_discount(-1, True)


def test_zero_price_boundary_does_not_raise():
    # 邊界值：price == 0 不應該被當成負數擋下來
    assert calculate_discount(0, False) == 0
