"""
狀態轉移測試

測試方法：狀態轉移測試（State Transition Testing）
適用對象：具有先後順序或狀態切換的系統
核心理念：確保所有狀態轉移都被測試，覆蓋所有轉移路徑
"""

import pytest
from src.state_transition.vending_machine import VendingMachine
from src.state_transition.media_player import MediaPlayer


class TestVendingMachine:
    """測試販賣機狀態機"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.machine = VendingMachine()

    def test_initial_state(self):
        """測試：初始狀態應為待機"""
        assert self.machine.get_state() == '待機'

    def test_transition_idle_to_accepting_coins(self):
        """測試：待機 → 投幣中"""
        self.machine.insert_coin(10)
        assert self.machine.get_state() == '投幣中'
        assert self.machine.get_balance() == 10

    def test_transition_accepting_to_selecting(self):
        """測試：投幣中 → 選擇商品"""
        self.machine.insert_coin(50)
        self.machine.confirm_amount()
        assert self.machine.get_state() == '選擇商品'

    def test_transition_selecting_to_dispensing(self):
        """測試：選擇商品 → 出貨中"""
        self.machine.insert_coin(50)
        self.machine.confirm_amount()
        result = self.machine.select_product('可樂')
        assert result['success'] is True
        assert self.machine.get_state() == '出貨中'

    def test_transition_dispensing_to_change(self):
        """測試：出貨中 → 找零"""
        self.machine.insert_coin(100)
        self.machine.confirm_amount()
        self.machine.select_product('可樂')  # 價格 30
        self.machine.dispense()
        assert self.machine.get_state() == '找零'

    def test_transition_change_to_idle(self):
        """測試：找零 → 待機"""
        self.machine.insert_coin(100)
        self.machine.confirm_amount()
        self.machine.select_product('可樂')
        self.machine.dispense()
        change = self.machine.return_change()
        assert change == 70  # 100 - 30
        assert self.machine.get_state() == '待機'

    def test_transition_cancel_to_refund(self):
        """測試：投幣中 → 退幣（取消）"""
        self.machine.insert_coin(50)
        self.machine.cancel()
        assert self.machine.get_state() == '退幣'

    def test_transition_refund_to_idle(self):
        """測試：退幣 → 待機"""
        self.machine.insert_coin(50)
        self.machine.cancel()
        refund = self.machine.complete_refund()
        assert refund == 50
        assert self.machine.get_state() == '待機'

    def test_full_purchase_flow(self):
        """測試：完整購買流程"""
        # 待機 → 投幣中
        self.machine.insert_coin(50)
        assert self.machine.get_state() == '投幣中'

        # 投幣中 → 選擇商品
        self.machine.confirm_amount()
        assert self.machine.get_state() == '選擇商品'

        # 選擇商品 → 出貨中
        self.machine.select_product('可樂')
        assert self.machine.get_state() == '出貨中'

        # 出貨中 → 找零
        self.machine.dispense()
        assert self.machine.get_state() == '找零'

        # 找零 → 待機
        change = self.machine.return_change()
        assert self.machine.get_state() == '待機'
        assert change == 20

    def test_insufficient_balance(self):
        """測試：餘額不足無法選商品"""
        self.machine.insert_coin(10)
        self.machine.confirm_amount()
        result = self.machine.select_product('可樂')  # 需要 30
        assert result['success'] is False
        assert '餘額不足' in result['message']

    def test_continue_inserting_coins(self):
        """測試：投幣中 → 繼續投幣（停留在投幣中）"""
        self.machine.insert_coin(10)
        assert self.machine.get_state() == '投幣中'
        self.machine.insert_coin(10)
        assert self.machine.get_state() == '投幣中'
        assert self.machine.get_balance() == 20


class TestMediaPlayer:
    """測試媒體播放器狀態機"""

    def setup_method(self):
        """每個測試方法前執行"""
        self.player = MediaPlayer()

    def test_initial_state(self):
        """測試：初始狀態應為停止"""
        assert self.player.get_state() == '停止'

    def test_transition_stopped_to_playing(self):
        """測試：停止 → 播放"""
        self.player.play()
        assert self.player.get_state() == '播放中'

    def test_transition_playing_to_paused(self):
        """測試：播放中 → 暫停"""
        self.player.play()
        self.player.pause()
        assert self.player.get_state() == '暫停'

    def test_transition_paused_to_playing(self):
        """測試：暫停 → 播放"""
        self.player.play()
        self.player.pause()
        self.player.play()
        assert self.player.get_state() == '播放中'

    def test_transition_playing_to_stopped(self):
        """測試：播放中 → 停止"""
        self.player.play()
        self.player.stop()
        assert self.player.get_state() == '停止'

    def test_transition_paused_to_stopped(self):
        """測試：暫停 → 停止"""
        self.player.play()
        self.player.pause()
        self.player.stop()
        assert self.player.get_state() == '停止'

    def test_full_playback_cycle(self):
        """測試：完整播放循環"""
        # 停止 → 播放
        self.player.play()
        assert self.player.get_state() == '播放中'

        # 播放 → 暫停
        self.player.pause()
        assert self.player.get_state() == '暫停'

        # 暫停 → 播放
        self.player.play()
        assert self.player.get_state() == '播放中'

        # 播放 → 停止
        self.player.stop()
        assert self.player.get_state() == '停止'

    def test_invalid_transition_pause_when_stopped(self):
        """測試：無效轉移 - 停止狀態下暫停"""
        result = self.player.pause()
        assert result['success'] is False
        assert '無效操作' in result['message']
        assert self.player.get_state() == '停止'

    def test_invalid_transition_stop_when_stopped(self):
        """測試：無效轉移 - 重複停止"""
        self.player.play()
        self.player.stop()
        result = self.player.stop()
        assert result['success'] is False
        assert self.player.get_state() == '停止'

    def test_state_coverage(self):
        """測試：狀態覆蓋率"""
        coverage = self.player.get_state_coverage()
        # 應該有 3 個狀態：停止、播放中、暫停
        assert coverage['total_states'] == 3

    def test_transition_coverage(self):
        """測試：轉移覆蓋率"""
        # 執行所有可能的轉移
        # 1. 停止 → 播放
        self.player.play()
        # 2. 播放 → 暫停
        self.player.pause()
        # 3. 暫停 → 播放
        self.player.play()
        # 4. 播放 → 停止
        self.player.stop()
        # 5. 停止 → 播放 → 暫停 → 停止（覆蓋「暫停 → 停止」）
        self.player.play()
        self.player.pause()
        self.player.stop()

        coverage = self.player.get_transition_coverage()
        # 應該覆蓋所有有效的轉移（5 個）
        assert coverage['transition_coverage'] >= 80.0
