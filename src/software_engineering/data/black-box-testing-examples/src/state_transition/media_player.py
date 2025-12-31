"""
媒體播放器狀態機 - 狀態轉移測試範例

狀態圖：
[*] --> 停止
停止 --> 播放中: play()
播放中 --> 暫停: pause()
暫停 --> 播放中: play()
播放中 --> 停止: stop()
暫停 --> 停止: stop()

測試覆蓋目標：
- 狀態覆蓋（State Coverage）：每個狀態至少訪問一次
- 轉移覆蓋（Transition Coverage）：每條轉移至少執行一次
- 成對轉移覆蓋（Pair Transition Coverage）：連續的兩個轉移
"""

from transitions import Machine


class MediaPlayer:
    """媒體播放器狀態機"""

    # 定義狀態
    states = ['停止', '播放中', '暫停']

    def __init__(self):
        """初始化播放器"""
        self.current_time = 0
        self.total_time = 300  # 假設總長度 5 分鐘
        self.visited_states = set()
        self.transitions_executed = []

        # 定義狀態轉移
        transitions = [
            {
                'trigger': 'play',
                'source': '停止',
                'dest': '播放中',
                'after': 'on_play'
            },
            {
                'trigger': 'play',
                'source': '暫停',
                'dest': '播放中',
                'after': 'on_play'
            },
            {
                'trigger': 'pause',
                'source': '播放中',
                'dest': '暫停',
                'after': 'on_pause'
            },
            {
                'trigger': 'stop',
                'source': '播放中',
                'dest': '停止',
                'after': 'on_stop'
            },
            {
                'trigger': 'stop',
                'source': '暫停',
                'dest': '停止',
                'after': 'on_stop'
            }
        ]

        # 初始化狀態機
        self.machine = Machine(
            model=self,
            states=MediaPlayer.states,
            transitions=transitions,
            initial='停止',
            after_state_change='track_state'
        )

        # 追蹤初始狀態
        self.visited_states.add('停止')

    def track_state(self):
        """追蹤狀態訪問"""
        self.visited_states.add(self.state)

    def on_play(self):
        """播放事件處理"""
        self.transitions_executed.append(('play', self.state))

    def on_pause(self):
        """暫停事件處理"""
        self.transitions_executed.append(('pause', self.state))

    def on_stop(self):
        """停止事件處理"""
        self.current_time = 0
        self.transitions_executed.append(('stop', self.state))

    def get_state(self):
        """獲取當前狀態"""
        return self.state

    def get_current_time(self):
        """獲取當前播放時間"""
        return self.current_time

    # 重載 play, pause, stop 以處理無效操作
    def play(self):
        """播放"""
        if self.state == '播放中':
            return {
                'success': False,
                'message': '已經在播放中'
            }

        try:
            self.trigger('play')
            return {
                'success': True,
                'message': '開始播放'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'無效操作：{str(e)}'
            }

    def pause(self):
        """暫停"""
        if self.state != '播放中':
            return {
                'success': False,
                'message': '無效操作：只能在播放中時暫停'
            }

        try:
            self.trigger('pause')
            return {
                'success': True,
                'message': '已暫停'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'無效操作：{str(e)}'
            }

    def stop(self):
        """停止"""
        if self.state == '停止':
            return {
                'success': False,
                'message': '已經停止'
            }

        try:
            self.trigger('stop')
            return {
                'success': True,
                'message': '已停止'
            }
        except Exception as e:
            return {
                'success': False,
                'message': f'無效操作：{str(e)}'
            }

    def get_state_coverage(self):
        """獲取狀態覆蓋率"""
        total_states = len(MediaPlayer.states)
        visited = len(self.visited_states)

        return {
            'total_states': total_states,
            'visited_states': visited,
            'coverage_percentage': (visited / total_states * 100) if total_states > 0 else 0
        }

    def get_transition_coverage(self):
        """獲取轉移覆蓋率"""
        # 定義所有可能的轉移
        all_transitions = [
            ('停止', 'play', '播放中'),
            ('播放中', 'pause', '暫停'),
            ('暫停', 'play', '播放中'),
            ('播放中', 'stop', '停止'),
            ('暫停', 'stop', '停止')
        ]

        # 計算已執行的唯一轉移
        executed_unique = set()
        for i in range(len(self.transitions_executed)):
            action, dest = self.transitions_executed[i]
            if i > 0:
                prev_dest = self.transitions_executed[i-1][1]
                executed_unique.add((prev_dest, action, dest))

        total_transitions = len(all_transitions)
        executed_count = len(executed_unique)

        return {
            'total_transitions': total_transitions,
            'executed_transitions': executed_count,
            'transition_coverage': (executed_count / total_transitions * 100) if total_transitions > 0 else 0
        }
