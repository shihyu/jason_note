#!/usr/bin/env python3
# gdb_to_graph.py - 將 GDB 追蹤轉換為視覺化圖表

import re
import sys
import os
from graphviz import Digraph

def parse_gdb_trace(filename='gdb_trace.log'):
    """解析 GDB 追蹤檔案"""
    traces = []

    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return traces

    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('TRACE|'):
                parts = line.strip().split('|')
                if len(parts) >= 4:
                    func = parts[1]
                    file = parts[2]
                    line_no = parts[3]
                    traces.append({
                        'func': func,
                        'file': file,
                        'line': line_no
                    })

    return traces

def create_flow_graph(traces, output='gdb_flow'):
    """建立流程圖"""
    if not traces:
        print("No traces to visualize")
        return

    dot = Digraph(comment='GDB Program Flow')
    dot.attr(rankdir='TB')
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')

    # 建立節點
    for i, trace in enumerate(traces):
        node_id = str(i)
        label = f"{trace['func']}\\n{trace['file']}:{trace['line']}"

        # 特殊顏色標記
        if trace['func'] == 'main':
            dot.node(node_id, label, fillcolor='lightgreen')
        elif 'Calculator' in trace['func']:
            dot.node(node_id, label, fillcolor='lightyellow')
        elif 'fibonacci' in trace['func']:
            dot.node(node_id, label, fillcolor='lightcoral')
        else:
            dot.node(node_id, label)

        # 建立邊
        if i > 0:
            dot.edge(str(i-1), node_id)

    # 輸出
    try:
        dot.render(output, format='svg', cleanup=True)
        dot.render(output, format='png', cleanup=True)
        print(f"Generated {output}.svg and {output}.png")
    except Exception as e:
        print(f"Error generating graph: {e}")
        print("Make sure graphviz is installed: sudo apt install graphviz")

    # 產生統計資訊
    print(f"\nTrace Statistics:")
    print(f"Total function calls: {len(traces)}")
    func_count = {}
    for trace in traces:
        func = trace['func']
        func_count[func] = func_count.get(func, 0) + 1

    print("\nFunction call frequency:")
    for func, count in sorted(func_count.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {func}: {count} times")

def create_simplified_graph(traces, output='gdb_flow_simple', min_calls=2):
    """建立簡化版流程圖（過濾低頻函數）"""
    if not traces:
        return

    # 統計函數呼叫次數
    func_count = {}
    for trace in traces:
        func = trace['func']
        func_count[func] = func_count.get(func, 0) + 1

    # 過濾
    filtered_traces = [t for t in traces if func_count[t['func']] >= min_calls]

    if filtered_traces:
        print(f"\nCreating simplified graph (min calls: {min_calls})...")
        create_flow_graph(filtered_traces, output)

def main():
    print("=== GDB Trace to Graph Converter ===\n")

    # 解析追蹤檔案
    traces = parse_gdb_trace()

    if traces:
        # 產生完整流程圖
        create_flow_graph(traces, 'gdb_flow')

        # 產生簡化流程圖
        if len(traces) > 100:
            create_simplified_graph(traces, 'gdb_flow_simple', min_calls=5)
    else:
        print("No traces found in gdb_trace.log")
        print("Please run './gdb_trace.sh <program>' first")

if __name__ == "__main__":
    main()