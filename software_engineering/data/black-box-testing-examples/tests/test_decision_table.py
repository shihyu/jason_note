"""
決策表測試

測試方法：決策表測試（Decision Table Testing）
適用對象：複雜的商業規則
核心理念：確保所有條件組合都被測試，涵蓋 2^n 個邏輯情境
"""

import pytest
from src.decision_table.membership_discount import MembershipDiscountCalculator
from src.decision_table.insurance_claim import InsuranceClaimProcessor


class TestMembershipDiscountCalculator:
    """測試會員折扣計算器"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.calculator = MembershipDiscountCalculator()

    # 決策表：2^3 = 8 種組合
    # 條件 1：會員等級（金卡/銀卡）
    # 條件 2：購買金額（≥1000/<1000）
    # 條件 3：使用優惠券（是/否）

    def test_gold_member_high_amount_with_coupon(self):
        """測試：金卡 + 金額≥1000 + 有優惠券"""
        result = self.calculator.calculate(
            member_level='gold',
            amount=1500,
            has_coupon=True
        )
        assert result['discount_rate'] == 0.25  # 25% 折扣
        assert result['final_amount'] == 1125

    def test_gold_member_high_amount_no_coupon(self):
        """測試：金卡 + 金額≥1000 + 無優惠券"""
        result = self.calculator.calculate(
            member_level='gold',
            amount=1500,
            has_coupon=False
        )
        assert result['discount_rate'] == 0.20  # 20% 折扣
        assert result['final_amount'] == 1200

    def test_gold_member_low_amount_with_coupon(self):
        """測試：金卡 + 金額<1000 + 有優惠券"""
        result = self.calculator.calculate(
            member_level='gold',
            amount=500,
            has_coupon=True
        )
        assert result['discount_rate'] == 0.15  # 15% 折扣
        assert result['final_amount'] == 425

    def test_gold_member_low_amount_no_coupon(self):
        """測試：金卡 + 金額<1000 + 無優惠券"""
        result = self.calculator.calculate(
            member_level='gold',
            amount=500,
            has_coupon=False
        )
        assert result['discount_rate'] == 0.10  # 10% 折扣
        assert result['final_amount'] == 450

    def test_silver_member_high_amount_with_coupon(self):
        """測試：銀卡 + 金額≥1000 + 有優惠券"""
        result = self.calculator.calculate(
            member_level='silver',
            amount=1500,
            has_coupon=True
        )
        assert result['discount_rate'] == 0.15  # 15% 折扣
        assert result['final_amount'] == 1275

    def test_silver_member_high_amount_no_coupon(self):
        """測試：銀卡 + 金額≥1000 + 無優惠券"""
        result = self.calculator.calculate(
            member_level='silver',
            amount=1500,
            has_coupon=False
        )
        assert result['discount_rate'] == 0.10  # 10% 折扣
        assert result['final_amount'] == 1350

    def test_silver_member_low_amount_with_coupon(self):
        """測試：銀卡 + 金額<1000 + 有優惠券"""
        result = self.calculator.calculate(
            member_level='silver',
            amount=500,
            has_coupon=True
        )
        assert result['discount_rate'] == 0.10  # 10% 折扣
        assert result['final_amount'] == 450

    def test_silver_member_low_amount_no_coupon(self):
        """測試：銀卡 + 金額<1000 + 無優惠券"""
        result = self.calculator.calculate(
            member_level='silver',
            amount=500,
            has_coupon=False
        )
        assert result['discount_rate'] == 0.05  # 5% 折扣
        assert result['final_amount'] == 475

    def test_non_member(self):
        """測試：非會員"""
        result = self.calculator.calculate(
            member_level='none',
            amount=1500,
            has_coupon=True
        )
        assert result['discount_rate'] == 0.0  # 無折扣
        assert result['final_amount'] == 1500

    def test_decision_table_completeness(self):
        """測試：決策表完整性檢查"""
        table = self.calculator.get_decision_table()
        # 應該有 8 個規則（2^3）
        assert len(table) == 8


class TestInsuranceClaimProcessor:
    """測試保險理賠處理器"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.processor = InsuranceClaimProcessor()

    # 決策表：2^4 = 16 種組合
    # 條件 1：保單有效（是/否）
    # 條件 2：在理賠期限內（是/否）
    # 條件 3：提供完整文件（是/否）
    # 條件 4：金額在保額內（是/否）

    def test_all_conditions_met(self):
        """測試：所有條件都滿足"""
        result = self.processor.process_claim(
            policy_valid=True,
            within_period=True,
            complete_documents=True,
            within_coverage=True,
            claim_amount=10000
        )
        assert result['approved'] is True
        assert result['payout_amount'] == 10000

    def test_policy_invalid(self):
        """測試：保單無效"""
        result = self.processor.process_claim(
            policy_valid=False,
            within_period=True,
            complete_documents=True,
            within_coverage=True,
            claim_amount=10000
        )
        assert result['approved'] is False
        assert '保單無效' in result['reason']

    def test_outside_period(self):
        """測試：超過理賠期限"""
        result = self.processor.process_claim(
            policy_valid=True,
            within_period=False,
            complete_documents=True,
            within_coverage=True,
            claim_amount=10000
        )
        assert result['approved'] is False
        assert '超過理賠期限' in result['reason']

    def test_incomplete_documents(self):
        """測試：文件不完整"""
        result = self.processor.process_claim(
            policy_valid=True,
            within_period=True,
            complete_documents=False,
            within_coverage=True,
            claim_amount=10000
        )
        assert result['approved'] is False
        assert '文件不完整' in result['reason']

    def test_exceeds_coverage(self):
        """測試：超過保額"""
        result = self.processor.process_claim(
            policy_valid=True,
            within_period=True,
            complete_documents=True,
            within_coverage=False,
            claim_amount=100000
        )
        assert result['approved'] is False
        assert '超過保額' in result['reason']

    def test_partial_approval_scenario(self):
        """測試：部分核准情境"""
        # 當文件完整但金額略微超過時，可能部分核准
        result = self.processor.process_claim(
            policy_valid=True,
            within_period=True,
            complete_documents=True,
            within_coverage=False,
            claim_amount=55000,  # 略超過 50000 的保額
            allow_partial=True
        )
        # 應該部分核准到保額上限
        assert result['approved'] is True
        assert result['payout_amount'] == 50000
        assert '部分核准' in result['reason']

    def test_multiple_failures(self):
        """測試：多個條件失敗"""
        result = self.processor.process_claim(
            policy_valid=False,
            within_period=False,
            complete_documents=False,
            within_coverage=False,
            claim_amount=100000
        )
        assert result['approved'] is False
        # 應該列出所有失敗原因
        assert '保單無效' in result['reason']

    def test_decision_table_coverage(self):
        """測試：決策表覆蓋率"""
        coverage = self.processor.get_decision_table_coverage()
        # 應該覆蓋所有 16 種組合
        assert coverage['total_combinations'] == 16
        assert coverage['covered_combinations'] >= 16
