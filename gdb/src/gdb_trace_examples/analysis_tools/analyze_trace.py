#!/usr/bin/env python3
# analyze_trace.py - 分析 GDB 追蹤結果

import re
import sys
from collections import Counter

def analyze_trace_file(filename):
    """分析追蹤檔案"""
    try:
        with open(filename, 'r') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: Cannot find file '{filename}'")
        return
    
    # 統計函式呼叫次數
    functions = re.findall(r'→ (\w+)\(', content)
    
    if functions:
        counter = Counter(functions)
        print("Function call statistics:")
        print("-" * 30)
        for func, count in counter.most_common():
            print(f"  {func}: {count} calls")
        print()
    
    # 分析斷點觸發
    breakpoints = re.findall(r'Breakpoint \d+, (\w+)', content)
    if breakpoints:
        bp_counter = Counter(breakpoints)
        print("Breakpoint hit statistics:")
        print("-" * 30)
        for func, count in bp_counter.most_common():
            print(f"  {func}: {count} times")
        print()
    
    # 計算執行時間（如果有時間戳記）
    times = re.findall(r'\[(\d+:\d+:\d+\.\d+)\]', content)
    if len(times) >= 2:
        print("Execution timeline:")
        print("-" * 30)
        print(f"  Start time: {times[0]}")
        print(f"  End time:   {times[-1]}")
        
        # 簡單計算執行時間差
        start_parts = times[0].split(':')
        end_parts = times[-1].split(':')
        
        start_ms = (int(start_parts[0]) * 3600000 + 
                   int(start_parts[1]) * 60000 + 
                   float(start_parts[2]) * 1000)
        end_ms = (int(end_parts[0]) * 3600000 + 
                 int(end_parts[1]) * 60000 + 
                 float(end_parts[2]) * 1000)
        
        duration_ms = end_ms - start_ms
        print(f"  Duration:   {duration_ms:.3f} ms")
        print()
    
    # 顯示呼叫堆疊深度
    stack_depth = content.count("→")
    if stack_depth > 0:
        print("Call stack analysis:")
        print("-" * 30)
        print(f"  Total function calls: {stack_depth}")
        
        # 找出最深的呼叫層級
        max_depth = 0
        for line in content.split('\n'):
            if '→' in line:
                depth = len(re.findall(r'  ', line))
                max_depth = max(max_depth, depth)
        print(f"  Maximum call depth: {max_depth}")
        print()
    
    # 統計檔案行數
    lines = content.count('\n')
    print("Trace file statistics:")
    print("-" * 30)
    print(f"  Total lines: {lines}")
    print(f"  File size: {len(content)} bytes")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_trace_file(sys.argv[1])
    else:
        # 預設分析 trace_log.txt
        print("Analyzing trace_log.txt (use argument to specify other file)")
        print("=" * 50)
        analyze_trace_file("trace_log.txt")