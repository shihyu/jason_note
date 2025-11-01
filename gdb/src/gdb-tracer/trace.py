#!/usr/bin/env python3
# trace.py - GDB Python 腳本，用於自動追蹤程式流程

import gdb
import datetime

# 全域變數，用於追蹤縮排層級
indent_level = 0
trace_file = None

class FunctionTracer(gdb.Breakpoint):
    """在函式入口設置斷點並記錄"""

    def __init__(self, function_name):
        super().__init__(function_name)
        self.function_name = function_name

    def stop(self):
        global indent_level, trace_file

        # 獲取當前 frame 資訊
        frame = gdb.selected_frame()

        # 取得函式參數
        args = []
        try:
            block = frame.block()
            for symbol in block:
                if symbol.is_argument:
                    value = frame.read_var(symbol)
                    args.append(f"{symbol.name}={value}")
        except:
            args = ["<unable to read args>"]

        # 格式化輸出
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        indent = "  " * indent_level
        message = f"[{timestamp}] {indent}→ {self.function_name}({', '.join(args)})"

        # 輸出到終端和檔案
        print(message)
        if trace_file:
            trace_file.write(message + "\n")
            trace_file.flush()

        # 增加縮排層級
        indent_level += 1

        # 設置函式返回斷點
        try:
            FunctionExitTracer(frame, self.function_name)
        except:
            pass

        # 不停止執行
        return False

class FunctionExitTracer(gdb.FinishBreakpoint):
    """在函式返回時記錄"""

    def __init__(self, frame, function_name=None):
        try:
            super().__init__(frame)
            self.function_name = function_name or frame.name()
        except Exception as e:
            # FinishBreakpoint 可能在某些情況下失敗
            pass

    def stop(self):
        global indent_level, trace_file

        # 減少縮排層級
        indent_level = max(0, indent_level - 1)

        # 取得返回值
        try:
            return_value = self.return_value
        except:
            return_value = "<unknown>"

        # 格式化輸出
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        indent = "  " * indent_level
        message = f"[{timestamp}] {indent}← {self.function_name} returned: {return_value}"

        # 輸出到終端和檔案
        print(message)
        if trace_file:
            trace_file.write(message + "\n")
            trace_file.flush()

        # 不停止執行
        return False

    def out_of_scope(self):
        # 處理超出範圍的情況
        global indent_level
        indent_level = max(0, indent_level - 1)
        return False

class VariableWatcher:
    """監視變數變化"""

    def __init__(self, variable_name):
        # 使用 GDB 的 watch 命令
        try:
            gdb.execute(f"watch {variable_name}")
            self.variable_name = variable_name
            print(f"✓ Watching variable: {variable_name}")
        except Exception as e:
            print(f"✗ Could not watch variable {variable_name}: {e}")
        
    def log_change(self, old_value, new_value):
        global trace_file

        frame = gdb.selected_frame()

        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        message = f"[{timestamp}] Variable '{self.variable_name}' changed: {old_value} → {new_value} in {frame.name()}"

        print(message)
        if trace_file:
            trace_file.write(message + "\n")
            trace_file.flush()

# GDB 命令類別
class TraceCommand(gdb.Command):
    """開始追蹤程式執行"""
    
    def __init__(self):
        super().__init__("trace-start", gdb.COMMAND_USER)
        
    def invoke(self, arg, from_tty):
        global trace_file
        
        # 開啟記錄檔案
        trace_file = open("trace_log.txt", "w")
        trace_file.write(f"=== Trace started at {datetime.datetime.now()} ===\n")
        
        # 清除舊的斷點
        try:
            gdb.execute("delete breakpoints")
        except:
            pass

        # 重置縮排層級
        global indent_level
        indent_level = 0

        # 從參數解析要追蹤的函式，如果沒有就使用預設值
        if arg:
            functions = arg.split()
        else:
            # 嘗試自動找出所有函式
            functions = ["main", "calculate", "add", "multiply"]

        for func in functions:
            try:
                FunctionTracer(func)
                print(f"✓ Tracing function: {func}")
            except Exception as e:
                print(f"✗ Could not trace: {func} - {e}")
        
        print("\nTracing started. Output will be saved to trace_log.txt")
        print("Use 'continue' to run the program\n")

class StopTraceCommand(gdb.Command):
    """停止追蹤"""

    def __init__(self):
        super().__init__("trace-stop", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        global trace_file, indent_level

        # 刪除所有斷點
        try:
            gdb.execute("delete breakpoints")
        except:
            pass

        # 重置縮排層級
        indent_level = 0

        # 關閉檔案
        if trace_file:
            trace_file.write(f"=== Trace ended at {datetime.datetime.now()} ===\n")
            trace_file.close()
            trace_file = None

        print("Tracing stopped")

class AutoTraceCommand(gdb.Command):
    """自動追蹤所有函式"""

    def __init__(self):
        super().__init__("auto-trace", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        global trace_file, indent_level

        # 開啟記錄檔案
        trace_file = open("trace_log.txt", "w")
        trace_file.write(f"=== Auto-trace started at {datetime.datetime.now()} ===\n")

        # 清除舊的斷點
        try:
            gdb.execute("delete breakpoints")
        except:
            pass

        # 重置縮排層級
        indent_level = 0

        # 取得所有函式符號
        try:
            # 收集所有函式
            functions = set()

            # 方法1: 從符號表取得函式
            try:
                # 取得當前二進位檔案
                objfile = gdb.current_progspace().filename

                # 使用 info functions 取得函式列表，但只針對當前檔案
                result = gdb.execute("info functions", to_string=True)

                # 解析每一行
                in_file_section = False
                for line in result.split('\n'):
                    # 檢查是否在檔案段落內
                    if 'File ' in line and '.c:' in line:
                        in_file_section = True
                        continue
                    elif line.startswith('File ') or line.startswith('Non-debugging'):
                        in_file_section = False
                        continue

                    # 在正確的段落內尋找函式
                    if in_file_section and line.strip():
                        # 嘗試提取函式名
                        # 格式通常是: "行號: 返回類型 函式名(參數);"
                        if ':' in line:
                            parts = line.split(':', 1)
                            if len(parts) > 1:
                                func_def = parts[1].strip()
                                # 找函式名 - 通常在括號前
                                if '(' in func_def:
                                    # 取得括號前的部分
                                    before_paren = func_def.split('(')[0]
                                    # 取最後一個單詞作為函式名
                                    words = before_paren.split()
                                    if words:
                                        func_name = words[-1].strip('*')
                                        if func_name and not func_name.startswith('_'):
                                            functions.add(func_name)
            except:
                pass

            # 方法2: 如果方法1失敗，使用備用列表或讓使用者指定
            if not functions:
                # 嘗試從當前程式的符號取得
                for sym in gdb.execute("info functions ^[a-z]", to_string=True).split('\n'):
                    if '(' in sym and ':' in sym:
                        try:
                            # 提取函式名
                            parts = sym.split(':')[1].strip()
                            if '(' in parts:
                                name = parts.split('(')[0].strip().split()[-1]
                                if name and not name.startswith('_'):
                                    functions.add(name)
                        except:
                            pass

            # 如果還是沒有，使用預設函式
            if not functions:
                print("Could not auto-discover functions. Using default list...")
                functions = ["main", "calculate", "add", "multiply"]

            # 設置斷點
            traced_count = 0
            for func in functions:
                try:
                    FunctionTracer(func)
                    print(f"✓ Auto-tracing function: {func}")
                    traced_count += 1
                except:
                    pass

            print(f"\nAuto-trace started. Tracing {traced_count} functions.")
            print("Output will be saved to trace_log.txt")
            print("Use 'continue' to run the program\n")

        except Exception as e:
            print(f"Error during auto-trace: {e}")

class WatchCommand(gdb.Command):
    """監視變數變化"""

    def __init__(self):
        super().__init__("trace-watch", gdb.COMMAND_USER)

    def invoke(self, arg, from_tty):
        if not arg:
            print("Usage: trace-watch <variable_name>")
            return

        VariableWatcher(arg)

# 註冊命令
TraceCommand()
StopTraceCommand()
AutoTraceCommand()
WatchCommand()

print("""
╔════════════════════════════════════════════╗
║         GDB Function Tracer Loaded         ║
╠════════════════════════════════════════════╣
║ Commands:                                  ║
║   trace-start [funcs] : Trace functions    ║
║   auto-trace         : Trace all functions ║
║   trace-watch <var>  : Watch variable      ║
║   trace-stop         : Stop tracing        ║
╚════════════════════════════════════════════╝
""")
