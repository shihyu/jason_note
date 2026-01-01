"""
邊界值分析測試

測試方法：等價類劃分 + 邊界值分析
適用對象：單一輸入參數
核心理念：用最少的測試案例，抓出邊界條件錯誤
"""

import pytest
from src.boundary_value.age_validator import AgeValidator
from src.boundary_value.amount_validator import AmountValidator


class TestAgeValidator:
    """測試年齡驗證器（範圍：0-120）"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.validator = AgeValidator()

    # 左邊界測試
    def test_age_below_minimum(self):
        """測試：低於最小值（-1）- 應該無效"""
        assert self.validator.validate(-1) is False

    def test_age_at_minimum(self):
        """測試：最小有效值（0）- 應該有效"""
        assert self.validator.validate(0) is True

    def test_age_above_minimum(self):
        """測試：最小有效值+1（1）- 應該有效"""
        assert self.validator.validate(1) is True

    # 右邊界測試
    def test_age_below_maximum(self):
        """測試：最大有效值-1（119）- 應該有效"""
        assert self.validator.validate(119) is True

    def test_age_at_maximum(self):
        """測試：最大有效值（120）- 應該有效"""
        assert self.validator.validate(120) is True

    def test_age_above_maximum(self):
        """測試：超過最大值（121）- 應該無效"""
        assert self.validator.validate(121) is False

    # 中間正常值測試
    def test_age_normal_value(self):
        """測試：中間正常值（30）- 應該有效"""
        assert self.validator.validate(30) is True

    # 異常輸入測試
    def test_age_negative_large(self):
        """測試：大負數（-100）- 應該無效"""
        assert self.validator.validate(-100) is False

    def test_age_very_large(self):
        """測試：非常大的數（1000）- 應該無效"""
        assert self.validator.validate(1000) is False

    # 錯誤訊息測試
    def test_age_error_message_too_low(self):
        """測試：低於最小值時的錯誤訊息"""
        result = self.validator.validate_with_message(-1)
        assert result['valid'] is False
        assert '年齡不能小於' in result['message']

    def test_age_error_message_too_high(self):
        """測試：超過最大值時的錯誤訊息"""
        result = self.validator.validate_with_message(121)
        assert result['valid'] is False
        assert '年齡不能大於' in result['message']

    def test_age_success_message(self):
        """測試：有效值的成功訊息"""
        result = self.validator.validate_with_message(30)
        assert result['valid'] is True
        assert result['message'] == '年齡驗證通過'


class TestAmountValidator:
    """測試金額驗證器（範圍：0-1000）"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.validator = AmountValidator()

    # 左邊界測試
    def test_amount_below_minimum(self):
        """測試：低於最小值（-1）- 應該無效"""
        assert self.validator.validate(-1) is False

    def test_amount_at_minimum(self):
        """測試：最小有效值（0）- 應該有效"""
        assert self.validator.validate(0) is True

    def test_amount_above_minimum(self):
        """測試：最小有效值+1（1）- 應該有效"""
        assert self.validator.validate(1) is True

    # 右邊界測試
    def test_amount_below_maximum(self):
        """測試：最大有效值-1（999）- 應該有效"""
        assert self.validator.validate(999) is True

    def test_amount_at_maximum(self):
        """測試：最大有效值（1000）- 應該有效"""
        assert self.validator.validate(1000) is True

    def test_amount_above_maximum(self):
        """測試：超過最大值（1001）- 應該無效"""
        assert self.validator.validate(1001) is False

    # 小數測試
    def test_amount_decimal_valid(self):
        """測試：有效小數（99.99）- 應該有效"""
        assert self.validator.validate(99.99) is True

    def test_amount_decimal_invalid(self):
        """測試：無效小數（1000.01）- 應該無效"""
        assert self.validator.validate(1000.01) is False

    # 異常輸入測試
    def test_amount_negative(self):
        """測試：負數金額（-50）- 應該無效"""
        assert self.validator.validate(-50) is False

    def test_amount_very_large(self):
        """測試：非常大的數（999999）- 應該無效"""
        assert self.validator.validate(999999) is False

    # 精度測試
    def test_amount_precision(self):
        """測試：小數精度（99.999）- 應該四捨五入到兩位"""
        result = self.validator.validate_with_precision(99.999)
        assert result['valid'] is True
        assert result['rounded_amount'] == 100.00

    def test_amount_precision_boundary(self):
        """測試：邊界精度（1000.004）- 四捨五入後應該有效"""
        result = self.validator.validate_with_precision(1000.004)
        assert result['valid'] is True
        assert result['rounded_amount'] == 1000.00

    def test_amount_precision_over_boundary(self):
        """測試：邊界精度（1000.006）- 四捨五入後應該無效"""
        result = self.validator.validate_with_precision(1000.006)
        assert result['valid'] is False  # 因為四捨五入後會變成 1000.01
        assert result['rounded_amount'] == 1000.01
