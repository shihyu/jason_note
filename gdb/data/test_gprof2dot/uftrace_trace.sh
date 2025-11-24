#!/bin/bash
# uftrace_trace.sh - uftrace 追蹤腳本

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi

PROGRAM=$1
PROGRAM_BASE="${PROGRAM%.*}"

# 檢查 uftrace 是否安裝
if ! command -v uftrace &> /dev/null; then
    echo "Warning: uftrace is not installed. Trying alternative methods..."
    echo "Please install uftrace: https://github.com/namhyung/uftrace"
    echo "Or use: sudo apt install uftrace (on Ubuntu/Debian)"
    exit 1
fi

# 對於 C/C++ 程式，需要重新編譯
if [[ $PROGRAM == *.cpp ]] || [[ $PROGRAM == *.c ]]; then
    echo "Recompiling with instrumentation..."
    if [[ $PROGRAM == *.cpp ]]; then
        g++ -pg -g -O0 $PROGRAM -o ${PROGRAM_BASE}_traced
    else
        gcc -pg -g -O0 $PROGRAM -o ${PROGRAM_BASE}_traced
    fi
    EXEC_PROGRAM="${PROGRAM_BASE}_traced"
else
    EXEC_PROGRAM=$PROGRAM
fi

# 檢查編譯後的程式是否存在
if [ ! -f "$EXEC_PROGRAM" ]; then
    echo "Error: Failed to compile or find $EXEC_PROGRAM"
    exit 1
fi

# 執行 uftrace 追蹤
echo "=== Running uftrace ==="
uftrace record -d uftrace_data ./$EXEC_PROGRAM

# 檢查 uftrace 是否成功
if [ $? -ne 0 ]; then
    echo "Error: uftrace recording failed"
    exit 1
fi

# 產生各種輸出格式
echo -e "\n=== Text Report ==="
uftrace report -d uftrace_data | head -20

echo -e "\n=== Call Graph ==="
uftrace graph -d uftrace_data | head -30

echo -e "\n=== Detailed Trace ==="
uftrace replay -d uftrace_data --no-pager > uftrace_trace.txt

# 輸出為 Chrome Tracing 格式
if uftrace dump -d uftrace_data --chrome > trace.json 2>/dev/null; then
    echo "Chrome trace saved to trace.json (view at chrome://tracing)"
else
    echo "Warning: Chrome trace generation failed (may not be supported in this version)"
fi

# 輸出為 FlameGraph 格式
if uftrace dump -d uftrace_data --flame-graph > flame.txt 2>/dev/null; then
    echo "FlameGraph data saved to flame.txt"
else
    echo "Warning: FlameGraph generation failed (may not be supported in this version)"
fi

# 產生時間統計
echo -e "\n=== Time Statistics ==="
uftrace report -d uftrace_data -s total,self,call | head -20

echo -e "\nTrace data saved in uftrace_data/"
echo "Detailed trace saved to uftrace_trace.txt"