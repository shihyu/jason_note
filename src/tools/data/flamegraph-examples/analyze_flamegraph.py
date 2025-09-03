#!/usr/bin/env python3
"""
analyze_flamegraph.py - 分析火焰圖數據，找出延遲熱點
"""

import sys
import os
from collections import defaultdict
import argparse

def analyze_flamegraph_data(folded_file):
    """
    解析 folded 格式的火焰圖數據
    格式: stack;frame1;frame2;frame3 count
    """
    if not os.path.exists(folded_file):
        print(f"Error: File {folded_file} not found")
        return None
    
    hotspots = defaultdict(int)
    stack_samples = defaultdict(int)
    total_samples = 0
    
    try:
        with open(folded_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                    
                # 分離堆疊和計數
                parts = line.rsplit(' ', 1)
                if len(parts) != 2:
                    continue
                    
                stack, count = parts
                try:
                    count = int(count)
                except ValueError:
                    continue
                    
                total_samples += count
                stack_samples[stack] = count
                
                # 提取每個函數的採樣數
                frames = stack.split(';')
                for func in frames:
                    func = func.strip()
                    if func:
                        hotspots[func] += count
    
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
    if total_samples == 0:
        print("No samples found in the file")
        return None
    
    return {
        'hotspots': hotspots,
        'stack_samples': stack_samples,
        'total_samples': total_samples
    }

def print_top_hotspots(data, top_n=20):
    """打印最熱的函數"""
    if not data:
        return
    
    hotspots = data['hotspots']
    total_samples = data['total_samples']
    
    # 計算百分比並排序
    sorted_hotspots = sorted(
        [(func, count, count/total_samples*100) 
         for func, count in hotspots.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"\nTop {min(top_n, len(sorted_hotspots))} CPU Hotspots:")
    print("="*80)
    print(f"{'Percentage':<12} {'Samples':<12} {'Function'}")
    print("-"*80)
    
    for i, (func, count, percentage) in enumerate(sorted_hotspots[:top_n]):
        # 截斷過長的函數名
        if len(func) > 50:
            func = func[:47] + "..."
        print(f"{percentage:10.2f}% {count:11,d}  {func}")
    
    print("-"*80)
    print(f"Total samples: {total_samples:,d}")

def print_stack_analysis(data, pattern=None):
    """分析特定模式的調用棧"""
    if not data:
        return
    
    stack_samples = data['stack_samples']
    total_samples = data['total_samples']
    
    matching_stacks = []
    
    for stack, count in stack_samples.items():
        if pattern and pattern not in stack:
            continue
        matching_stacks.append((stack, count, count/total_samples*100))
    
    # 排序並顯示
    matching_stacks.sort(key=lambda x: x[1], reverse=True)
    
    if pattern:
        print(f"\nStacks containing '{pattern}':")
    else:
        print("\nTop 10 Call Stacks:")
    print("="*80)
    
    for i, (stack, count, percentage) in enumerate(matching_stacks[:10]):
        frames = stack.split(';')
        print(f"\nStack #{i+1} - {percentage:.2f}% ({count:,d} samples)")
        print("-"*40)
        
        # 顯示調用棧（限制深度）
        max_depth = min(len(frames), 10)
        for j, frame in enumerate(frames[-max_depth:]):
            indent = "  " * j
            if len(frame) > 60:
                frame = frame[:57] + "..."
            print(f"{indent}└─ {frame}")

def compare_profiles(baseline_file, current_file):
    """比較兩個性能剖析結果"""
    print("\n" + "="*80)
    print("Performance Comparison")
    print("="*80)
    
    baseline = analyze_flamegraph_data(baseline_file)
    current = analyze_flamegraph_data(current_file)
    
    if not baseline or not current:
        print("Error: Cannot compare profiles")
        return
    
    baseline_hotspots = baseline['hotspots']
    current_hotspots = current['hotspots']
    baseline_total = baseline['total_samples']
    current_total = current['total_samples']
    
    # 找出所有函數
    all_functions = set(baseline_hotspots.keys()) | set(current_hotspots.keys())
    
    changes = []
    for func in all_functions:
        baseline_pct = baseline_hotspots.get(func, 0) / baseline_total * 100
        current_pct = current_hotspots.get(func, 0) / current_total * 100
        diff = current_pct - baseline_pct
        
        if abs(diff) > 0.1:  # 只顯示變化超過 0.1% 的
            changes.append((func, baseline_pct, current_pct, diff))
    
    # 排序：先改進，後退步
    changes.sort(key=lambda x: x[3])
    
    # 顯示改進
    improvements = [c for c in changes if c[3] < 0]
    if improvements:
        print("\n✓ Performance Improvements:")
        print("-"*80)
        print(f"{'Function':<50} {'Baseline':<12} {'Current':<12} {'Change'}")
        print("-"*80)
        for func, baseline_pct, current_pct, diff in improvements[:10]:
            if len(func) > 47:
                func = func[:44] + "..."
            print(f"{func:<50} {baseline_pct:>10.2f}% {current_pct:>10.2f}% {diff:>+10.2f}%")
    
    # 顯示退步
    regressions = [c for c in changes if c[3] > 0]
    if regressions:
        print("\n✗ Performance Regressions:")
        print("-"*80)
        print(f"{'Function':<50} {'Baseline':<12} {'Current':<12} {'Change'}")
        print("-"*80)
        for func, baseline_pct, current_pct, diff in regressions[-10:]:
            if len(func) > 47:
                func = func[:44] + "..."
            print(f"{func:<50} {baseline_pct:>10.2f}% {current_pct:>10.2f}% {diff:>+10.2f}%")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze flamegraph folded data to find performance hotspots'
    )
    parser.add_argument(
        'folded_file',
        help='Path to the folded flamegraph data file'
    )
    parser.add_argument(
        '-n', '--top',
        type=int,
        default=20,
        help='Number of top hotspots to display (default: 20)'
    )
    parser.add_argument(
        '-s', '--stack',
        help='Search for stacks containing specific pattern'
    )
    parser.add_argument(
        '-c', '--compare',
        help='Compare with another profile (baseline)'
    )
    
    args = parser.parse_args()
    
    # 基本分析
    data = analyze_flamegraph_data(args.folded_file)
    if data:
        print_top_hotspots(data, args.top)
        
        # 堆疊分析
        if args.stack:
            print_stack_analysis(data, args.stack)
        
        # 比較分析
        if args.compare:
            compare_profiles(args.compare, args.folded_file)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())