#!/bin/bash
# gdb_trace.sh - GDB 自動追蹤腳本

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi

PROGRAM=$1

# 檢查程式是否存在
if [ ! -f "$PROGRAM" ]; then
    echo "Error: Program '$PROGRAM' not found"
    exit 1
fi

# 建立 GDB 命令檔
cat > trace_commands.gdb << 'EOF'
set pagination off
set logging enabled off
set logging file gdb_trace.log
set logging overwrite on
set logging enabled on
set print thread-events off

# 使用 Python 來追蹤所有函數
python
import gdb
import re

# 全域函數定義
def trace_hit():
    try:
        frame = gdb.newest_frame()
        sal = frame.find_sal()

        func_name = frame.name() or "??"
        if sal and sal.symtab:
            filename = sal.symtab.filename.split('/')[-1]
            line = sal.line
        else:
            filename = "??"
            line = 0

        # 打印追蹤訊息
        print(f"TRACE|{func_name}|{filename}|{line}")

        # 也可以打印呼叫堆疊深度
        depth = 0
        f = frame
        while f:
            depth += 1
            f = f.older()
        print(f"DEPTH|{depth}")
    except Exception as e:
        pass

class TraceFunctions(gdb.Command):
    def __init__(self):
        super(TraceFunctions, self).__init__("trace-all", gdb.COMMAND_USER)
        self.call_depth = 0
        self.trace_data = []

    def invoke(self, arg, from_tty):
        # 對所有函數設定中斷點
        gdb.execute("rbreak .*")

        # 設定中斷點的行為
        for bp in gdb.breakpoints():
            bp.silent = True
            # 使用更相容的方式設定命令
            gdb.execute(f"commands {bp.number}\nsilent\npy trace_hit()\ncontinue\nend")

# 註冊命令
TraceFunctions()

# 執行追蹤
gdb.execute("trace-all")
gdb.execute("run")
end

quit
EOF

# 執行 GDB
echo "Starting GDB trace for $PROGRAM..."
gdb -batch -x trace_commands.gdb ./$PROGRAM 2>/dev/null

# 清理臨時檔案
rm -f trace_commands.gdb

echo "GDB trace completed. Check gdb_trace.log"