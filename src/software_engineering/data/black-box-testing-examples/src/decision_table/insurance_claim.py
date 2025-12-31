"""
保險理賠處理器 - 決策表測試範例

決策表：
條件：
1. 保單有效：是/否
2. 在理賠期限內：是/否
3. 提供完整文件：是/否
4. 金額在保額內：是/否

總組合數：2^4 = 16 種情境

核准規則：
- 所有條件都滿足 → 核准全額
- 任一條件不滿足 → 拒絕或部分核准
"""


class InsuranceClaimProcessor:
    """保險理賠處理器"""

    def __init__(self, max_coverage=50000):
        """
        初始化處理器

        Args:
            max_coverage: 最大保額（預設 50000）
        """
        self.max_coverage = max_coverage

    def process_claim(self, policy_valid, within_period, complete_documents,
                      within_coverage, claim_amount, allow_partial=False):
        """
        處理理賠申請

        Args:
            policy_valid: 保單是否有效
            within_period: 是否在理賠期限內
            complete_documents: 文件是否完整
            within_coverage: 金額是否在保額內
            claim_amount: 理賠金額
            allow_partial: 是否允許部分核准

        Returns:
            dict: 理賠結果
        """
        reasons = []

        # 檢查所有條件
        if not policy_valid:
            reasons.append('保單無效')

        if not within_period:
            reasons.append('超過理賠期限')

        if not complete_documents:
            reasons.append('文件不完整')

        if not within_coverage:
            reasons.append('超過保額')

        # 決策邏輯
        # 情況 1：所有條件都滿足
        if policy_valid and within_period and complete_documents and within_coverage:
            return {
                'approved': True,
                'payout_amount': claim_amount,
                'reason': '核准全額理賠'
            }

        # 情況 2：允許部分核准（前三個條件滿足，但超過保額）
        if allow_partial and policy_valid and within_period and complete_documents and not within_coverage:
            return {
                'approved': True,
                'payout_amount': self.max_coverage,
                'reason': f'部分核准：理賠金額調整為保額上限 {self.max_coverage}'
            }

        # 情況 3：拒絕理賠
        return {
            'approved': False,
            'payout_amount': 0,
            'reason': '；'.join(reasons)
        }

    def get_decision_table_coverage(self):
        """
        獲取決策表覆蓋率資訊

        Returns:
            dict: 覆蓋率資訊
        """
        # 4 個布林條件，總共 2^4 = 16 種組合
        total_combinations = 2 ** 4

        return {
            'total_combinations': total_combinations,
            'covered_combinations': total_combinations,
            'coverage_percentage': 100.0
        }

    def validate_claim_amount(self, claim_amount):
        """
        驗證理賠金額

        Args:
            claim_amount: 理賠金額

        Returns:
            dict: 驗證結果
        """
        if claim_amount <= 0:
            return {
                'valid': False,
                'within_coverage': False,
                'reason': '理賠金額必須大於 0'
            }

        if claim_amount > self.max_coverage:
            return {
                'valid': True,
                'within_coverage': False,
                'reason': f'理賠金額超過保額上限 {self.max_coverage}'
            }

        return {
            'valid': True,
            'within_coverage': True,
            'reason': '金額在保額範圍內'
        }

    def generate_decision_table_report(self):
        """
        生成決策表報告

        Returns:
            str: 決策表報告
        """
        report = []
        report.append("保險理賠決策表")
        report.append("=" * 60)
        report.append("")
        report.append("條件：")
        report.append("1. 保單有效（True/False）")
        report.append("2. 在理賠期限內（True/False）")
        report.append("3. 提供完整文件（True/False）")
        report.append("4. 金額在保額內（True/False）")
        report.append("")
        report.append("決策規則：")
        report.append("- 全部滿足 → 核准全額")
        report.append("- 前三項滿足但超過保額 → 可部分核准（需啟用）")
        report.append("- 其他情況 → 拒絕")
        report.append("")
        report.append(f"保額上限：{self.max_coverage}")
        report.append(f"總組合數：{2**4} 種")

        return "\n".join(report)
