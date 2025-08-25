#!/usr/bin/env python3
# trace.py - GDB Python 追蹤腳本

import gdb
import datetime
import sys

class FunctionTracer:
    def __init__(self):
        self.call_stack = []
        self.log_file = None
        self.indent_level = 0
        
    def start(self):
        """開始追蹤"""
        self.log_file = open("trace_log.txt", "w")
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_file.write(f"=== Trace started at {timestamp} ===\n")
        
        # 設置斷點
        gdb.execute("break main")
        gdb.execute("break calculate")
        gdb.execute("break add")
        gdb.execute("break multiply")
        
        # 註冊事件處理器
        gdb.events.stop.connect(self.on_stop)
        
    def stop(self):
        """停止追蹤"""
        if self.log_file:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.log_file.write(f"=== Trace ended at {timestamp} ===\n")
            self.log_file.close()
            self.log_file = None
        gdb.events.stop.disconnect(self.on_stop)
        
    def on_stop(self, event):
        """斷點停止事件處理"""
        if not isinstance(event, gdb.BreakpointEvent):
            return
            
        frame = gdb.selected_frame()
        func_name = frame.name()
        
        # 獲取時間戳記
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # 獲取參數
        args = []
        try:
            block = frame.block()
            for symbol in block:
                if symbol.is_argument:
                    value = frame.read_var(symbol)
                    args.append(f"{symbol.name}={value}")
        except:
            pass
            
        # 寫入日誌
        indent = "  " * self.indent_level
        args_str = ", ".join(args) if args else ""
        self.log_file.write(f"[{timestamp}] {indent}→ {func_name}({args_str})\n")
        self.log_file.flush()
        
        # 調整縮排
        if func_name in ["calculate", "add", "multiply"]:
            self.indent_level += 1
            
        # 繼續執行
        gdb.execute("continue")

# 建立追蹤器實例
tracer = FunctionTracer()

# 定義 GDB 命令
class TraceStartCommand(gdb.Command):
    """開始函式追蹤"""
    def __init__(self):
        super(TraceStartCommand, self).__init__("trace-start", gdb.COMMAND_USER)
        
    def invoke(self, arg, from_tty):
        tracer.start()
        print("Function tracing started")

class TraceStopCommand(gdb.Command):
    """停止函式追蹤"""
    def __init__(self):
        super(TraceStopCommand, self).__init__("trace-stop", gdb.COMMAND_USER)
        
    def invoke(self, arg, from_tty):
        tracer.stop()
        print("Function tracing stopped")

# 註冊命令
TraceStartCommand()
TraceStopCommand()

print("Trace commands loaded. Use 'trace-start' to begin and 'trace-stop' to end.")