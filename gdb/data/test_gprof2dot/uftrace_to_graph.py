#!/usr/bin/env python3
# uftrace_to_graph.py - 將 uftrace 輸出轉換為視覺化圖表

import re
import json
import os
from graphviz import Digraph

def parse_uftrace_replay(filename='uftrace_trace.txt'):
    """解析 uftrace replay 輸出"""
    traces = []
    call_stack = []
    time_pattern = r'\[([\d.]+)\s*us\]'

    if not os.path.exists(filename):
        print(f"Error: {filename} not found")
        return traces

    with open(filename, 'r') as f:
        for line in f:
            # 解析時間戳記
            time_match = re.search(time_pattern, line)
            timestamp = time_match.group(1) if time_match else None

            # 解析函數進入
            enter_match = re.search(r'\|\s*([\w:]+)\(\)', line)
            if enter_match and '{' in line:
                func = enter_match.group(1)
                indent = line.count(' ') - len(line.lstrip())

                traces.append({
                    'type': 'enter',
                    'func': func,
                    'depth': len(call_stack),
                    'time': timestamp
                })
                call_stack.append(func)

            # 解析函數退出
            elif '}' in line:
                if call_stack:
                    func = call_stack.pop()
                    # 提取執行時間
                    time_match = re.search(r'([\d.]+)\s*us', line)
                    exec_time = time_match.group(1) if time_match else None

                    traces.append({
                        'type': 'exit',
                        'func': func,
                        'depth': len(call_stack),
                        'exec_time': exec_time
                    })

    return traces

def create_uftrace_graph(traces, output='uftrace_flow'):
    """建立 uftrace 流程圖"""
    if not traces:
        print("No traces to visualize")
        return

    dot = Digraph(comment='uftrace Program Flow')
    dot.attr(rankdir='TB')
    dot.attr('graph', splines='ortho')

    # 記錄函數呼叫關係
    edges = set()
    call_stack = []
    node_counter = {}
    exec_times = {}

    for trace in traces:
        func = trace['func']

        if trace['type'] == 'enter':
            # 為每個函數呼叫建立唯一節點
            if func not in node_counter:
                node_counter[func] = 0
            node_counter[func] += 1

            node_id = f"{func}_{node_counter[func]}"

            # 設定節點樣式
            if func == 'main':
                color = 'lightgreen'
            elif 'fibonacci' in func:
                color = 'lightcoral'
            elif 'Calculator' in func or 'add' in func or 'multiply' in func:
                color = 'lightyellow'
            else:
                color = 'lightblue'

            # 節點標籤
            label = func
            if trace.get('time'):
                label += f"\\n@{trace['time']}us"

            dot.node(node_id, label, shape='box',
                    style='rounded,filled', fillcolor=color)

            # 建立邊
            if call_stack:
                parent = call_stack[-1]
                edge = (parent, node_id)
                if edge not in edges:
                    dot.edge(parent, node_id)
                    edges.add(edge)

            call_stack.append(node_id)
            exec_times[node_id] = None

        elif trace['type'] == 'exit' and call_stack:
            node_id = call_stack.pop()
            if trace.get('exec_time'):
                exec_times[node_id] = trace['exec_time']

    # 輸出圖表
    try:
        dot.render(output, format='svg', cleanup=True)
        dot.render(output, format='png', cleanup=True)
        print(f"Generated {output}.svg and {output}.png")
    except Exception as e:
        print(f"Error generating graph: {e}")
        print("Make sure graphviz is installed: sudo apt install graphviz")

    return exec_times

def create_summary_graph(filename='uftrace_trace.txt', output='uftrace_summary'):
    """建立函數呼叫統計圖"""
    if not os.path.exists(filename):
        print(f"Skipping summary graph: {filename} not found")
        return

    dot = Digraph(comment='Function Call Summary')
    dot.attr(rankdir='LR')

    # 統計函數呼叫次數和時間
    call_count = {}
    call_relations = {}
    exec_times = {}

    with open(filename, 'r') as f:
        current_caller = None
        for line in f:
            match = re.search(r'\|\s*([\w:]+)\(\)', line)
            if match:
                func = match.group(1)
                call_count[func] = call_count.get(func, 0) + 1

                # 提取執行時間
                time_match = re.search(r'([\d.]+)\s*us', line)
                if time_match and '}' in line:
                    time = float(time_match.group(1))
                    if func not in exec_times:
                        exec_times[func] = []
                    exec_times[func].append(time)

                if current_caller and current_caller != func:
                    key = (current_caller, func)
                    call_relations[key] = call_relations.get(key, 0) + 1

                if '{' in line:
                    current_caller = func

    # 建立節點（顯示呼叫次數和平均時間）
    for func, count in call_count.items():
        label = f"{func}\\n(called {count}x)"
        if func in exec_times and exec_times[func]:
            avg_time = sum(exec_times[func]) / len(exec_times[func])
            label += f"\\navg: {avg_time:.2f}us"

        dot.node(func, label, shape='box', style='filled',
                fillcolor='lightblue')

    # 建立邊（顯示呼叫關係）
    for (caller, callee), count in call_relations.items():
        label = f"{count}x" if count > 1 else ""
        dot.edge(caller, callee, label=label)

    try:
        dot.render(output, format='svg', cleanup=True)
        print(f"Generated {output}.svg")
    except Exception as e:
        print(f"Error generating summary graph: {e}")

def main():
    print("=== uftrace Trace to Graph Converter ===\n")

    # 解析並產生流程圖
    traces = parse_uftrace_replay()

    if traces:
        exec_times = create_uftrace_graph(traces)
        create_summary_graph()

        # 打印執行時間統計
        print("\nExecution Time Statistics:")
        func_times = {}
        for trace in traces:
            if trace['type'] == 'exit' and trace.get('exec_time'):
                func = trace['func']
                if func not in func_times:
                    func_times[func] = []
                func_times[func].append(float(trace['exec_time']))

        if func_times:
            print("\nTop 10 functions by total time:")
            sorted_funcs = []
            for func, times in func_times.items():
                avg = sum(times) / len(times)
                total = sum(times)
                sorted_funcs.append((func, avg, total, len(times)))

            for func, avg, total, calls in sorted(sorted_funcs, key=lambda x: x[2], reverse=True)[:10]:
                print(f"  {func}: avg={avg:.2f}us, total={total:.2f}us, calls={calls}")
        else:
            print("  No timing data available")
    else:
        print("No traces found in uftrace_trace.txt")
        print("Please run './uftrace_trace.sh <program>' first")

if __name__ == "__main__":
    main()