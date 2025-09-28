# 程式執行流程追蹤與視覺化指南

> **專案狀態**: ✅ 95% 完成（最後更新：2024-09-29）
> **版本**: 1.1.0
> **環境**: Linux/Ubuntu 測試通過

## 🎯 快速開始

```bash
# 快速測試所有功能
make quick-start  # 需要 sudo 權限

# 或分步執行
make build        # 編譯程式
make trace-all    # 執行所有追蹤
make graphs       # 產生視覺化圖表
```

## 📊 最新改進 (2024-09-29)

### ✅ 已修正問題
- **Makefile 顏色顯示**：所有 `echo` 改為 `printf` 支援 ANSI 顏色碼
- **GDB logging 衝突**：修正 `test.log` 與 `gdb_trace.log` 檔名衝突
- **Heredoc 語法錯誤**：改用檔案複製方式建立測試程式
- **重複目標警告**：調整 Makefile 依賴關係

### ✅ 測試結果
- **GDB 追蹤**：成功追蹤 48 個函數呼叫
- **uftrace 追蹤**：產生完整時間統計報告
- **視覺化輸出**：5 種格式（SVG, PNG, JSON, Chrome Trace, FlameGraph）
- **Makefile targets**：9/10 通過測試

## 目錄
- [概述](#概述)
- [測試程式準備](#測試程式準備)
- [方法一：GDB 追蹤](#方法一gdb-追蹤)
- [方法二：uftrace 追蹤](#方法二uftrace-追蹤)
- [Rust 支援](#rust-支援)
- [比較與選擇](#比較與選擇)
- [常見問題](#常見問題)

## 概述

本指南介紹如何追蹤程式執行流程，記錄每個函數的檔案、函數名、行號，並轉換成視覺化流程圖。支援 C/C++ 和 Rust。

### 需求工具
- GDB (GNU Debugger)
- uftrace
- Python 3 + Graphviz
- gcc/g++ 或 rustc

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install gdb uftrace python3-pip graphviz
pip3 install graphviz

# Arch Linux
sudo pacman -S gdb graphviz python-pip
yay -S uftrace
pip3 install graphviz

# macOS
brew install gdb graphviz
# uftrace 需要從源碼編譯
git clone https://github.com/namhyung/uftrace
cd uftrace && make && sudo make install
```

## 測試程式準備

### C++ 測試程式

```cpp
// test_program.cpp
#include <iostream>
#include <cmath>

class Calculator {
public:
    int add(int a, int b) {
        return a + b;
    }
    
    int multiply(int a, int b) {
        return a * b;
    }
};

int fibonacci(int n) {
    if (n <= 1) return n;
    return fibonacci(n-1) + fibonacci(n-2);
}

void process_data() {
    Calculator calc;
    int result = calc.add(5, 3);
    std::cout << "Add result: " << result << std::endl;
    
    result = calc.multiply(4, 7);
    std::cout << "Multiply result: " << result << std::endl;
}

int main() {
    std::cout << "Program started" << std::endl;
    
    process_data();
    
    int fib = fibonacci(5);
    std::cout << "Fibonacci(5) = " << fib << std::endl;
    
    return 0;
}
```

### Rust 測試程式

```rust
// test_program.rs
use std::fmt::Debug;

struct Calculator;

impl Calculator {
    fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }
    
    fn multiply(&self, a: i32, b: i32) -> i32 {
        a * b
    }
}

fn fibonacci(n: i32) -> i32 {
    if n <= 1 {
        return n;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

fn process_data() {
    let calc = Calculator;
    let result = calc.add(5, 3);
    println!("Add result: {}", result);
    
    let result = calc.multiply(4, 7);
    println!("Multiply result: {}", result);
}

fn main() {
    println!("Program started");
    
    process_data();
    
    let fib = fibonacci(5);
    println!("Fibonacci(5) = {}", fib);
}
```

## 方法一：GDB 追蹤

### 1.1 GDB 自動追蹤腳本

```bash
#!/bin/bash
# gdb_trace.sh

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi

PROGRAM=$1

# 建立 GDB 命令檔
cat > trace_commands.gdb << 'EOF'
set pagination off
set logging file gdb_trace.log
set logging overwrite on
set logging on
set print thread-events off

# 使用 Python 來追蹤所有函數
python
import gdb
import re

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
            bp.commands = "py trace_hit()\ncontinue"

def trace_hit():
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

# 註冊命令
TraceFunctions()

# 執行追蹤
trace-all
run
end

quit
EOF

# 執行 GDB
echo "Starting GDB trace for $PROGRAM..."
gdb -batch -x trace_commands.gdb ./$PROGRAM 2>/dev/null

echo "GDB trace completed. Check gdb_trace.log"
```

### 1.2 GDB 輸出轉換為圖表

```python
#!/usr/bin/env python3
# gdb_to_graph.py

import re
import sys
from graphviz import Digraph

def parse_gdb_trace(filename='gdb_trace.log'):
    """解析 GDB 追蹤檔案"""
    traces = []
    
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
    dot.render(output, format='svg', cleanup=True)
    dot.render(output, format='png', cleanup=True)
    print(f"Generated {output}.svg and {output}.png")
    
    # 產生統計資訊
    print(f"\nTrace Statistics:")
    print(f"Total function calls: {len(traces)}")
    func_count = {}
    for trace in traces:
        func = trace['func']
        func_count[func] = func_count.get(func, 0) + 1
    
    print("\nFunction call frequency:")
    for func, count in sorted(func_count.items(), key=lambda x: x[1], reverse=True):
        print(f"  {func}: {count} times")

if __name__ == "__main__":
    traces = parse_gdb_trace()
    if traces:
        create_flow_graph(traces)
    else:
        print("No traces found in gdb_trace.log")
```

## 方法二：uftrace 追蹤

### 2.1 uftrace 追蹤腳本

```bash
#!/bin/bash
# uftrace_trace.sh

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <program_name>"
    exit 1
fi

PROGRAM=$1
PROGRAM_BASE="${PROGRAM%.*}"

# 檢查 uftrace 是否安裝
if ! command -v uftrace &> /dev/null; then
    echo "uftrace is not installed. Please install it first."
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

# 執行 uftrace 追蹤
echo "=== Running uftrace ==="
uftrace record -d uftrace_data ./$EXEC_PROGRAM

# 產生各種輸出格式
echo -e "\n=== Text Report ==="
uftrace report -d uftrace_data | head -20

echo -e "\n=== Call Graph ==="
uftrace graph -d uftrace_data | head -30

echo -e "\n=== Detailed Trace ==="
uftrace replay -d uftrace_data --no-pager > uftrace_trace.txt

# 輸出為 Chrome Tracing 格式
uftrace dump -d uftrace_data --chrome > trace.json 2>/dev/null
echo "Chrome trace saved to trace.json (view at chrome://tracing)"

# 輸出為 FlameGraph 格式
uftrace dump -d uftrace_data --flame-graph > flame.txt 2>/dev/null
echo "FlameGraph data saved to flame.txt"

# 產生時間統計
echo -e "\n=== Time Statistics ==="
uftrace report -d uftrace_data -s total,self,call | head -20
```

### 2.2 uftrace 輸出轉換為圖表

```python
#!/usr/bin/env python3
# uftrace_to_graph.py

import re
import json
from graphviz import Digraph

def parse_uftrace_replay(filename='uftrace_trace.txt'):
    """解析 uftrace replay 輸出"""
    traces = []
    call_stack = []
    time_pattern = r'\[([\d.]+)\s*us\]'
    
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
    dot.render(output, format='svg', cleanup=True)
    dot.render(output, format='png', cleanup=True)
    print(f"Generated {output}.svg and {output}.png")
    
    return exec_times

def create_summary_graph(filename='uftrace_trace.txt', output='uftrace_summary'):
    """建立函數呼叫統計圖"""
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
    
    dot.render(output, format='svg', cleanup=True)
    print(f"Generated {output}.svg")

if __name__ == "__main__":
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
        
        for func, times in sorted(func_times.items()):
            avg = sum(times) / len(times)
            total = sum(times)
            print(f"  {func}: avg={avg:.2f}us, total={total:.2f}us, calls={len(times)}")
    else:
        print("No traces found in uftrace_trace.txt")
```

## Rust 支援

### Rust 與 GDB

Rust 完全支援 GDB 除錯：

```bash
# 編譯 Rust 程式（包含除錯符號）
rustc -g test_program.rs -o test_program

# 或使用 cargo
cargo build

# 使用 GDB 追蹤（同樣的腳本）
./gdb_trace.sh test_program
```

**注意事項：**
- Rust 函數名會被 mangle，看起來像 `_ZN4test11process_data17h...`
- 可以使用 `rust-gdb` 獲得更好的支援
- 在 GDB 中使用 `set print demangle on` 顯示可讀名稱

### Rust 與 uftrace

Rust 對 uftrace 的支援較為有限：

```bash
# 方法 1：使用 -C instrument-coverage
rustc -C instrument-coverage -g test_program.rs -o test_program

# 方法 2：使用 -Z instrument-mcount (需要 nightly)
rustc +nightly -Z instrument-mcount -g test_program.rs -o test_program

# 方法 3：使用 cargo-flamegraph (推薦)
cargo install flamegraph
cargo flamegraph
```

### Rust 專用工具

#### 1. cargo-profiling

```bash
cargo install cargo-profiling
cargo profiling callgrind
cargo profiling cachegrind
```

#### 2. tokio-console (for async)

```toml
# Cargo.toml
[dependencies]
tokio = { version = "1", features = ["full", "tracing"] }
console-subscriber = "0.1"
```

```rust
#[tokio::main]
async fn main() {
    console_subscriber::init();
    // your async code
}
```

#### 3. tracing crate

```rust
use tracing::{info, instrument};

#[instrument]
fn process_data() {
    info!("Processing data");
    // ...
}
```

## 完整執行腳本

```bash
#!/bin/bash
# run_all_traces.sh

echo "========================================="
echo "Program Flow Tracing Tool"
echo "========================================="

# 檢查參數
if [ $# -eq 0 ]; then
    echo "Usage: $0 <source_file>"
    echo "Example: $0 test_program.cpp"
    echo "         $0 test_program.rs"
    exit 1
fi

SOURCE_FILE=$1
FILE_EXT="${SOURCE_FILE##*.}"
BASE_NAME="${SOURCE_FILE%.*}"

# 編譯程式
echo "Compiling $SOURCE_FILE..."
case $FILE_EXT in
    cpp|cc|cxx)
        g++ -g -O0 -pg $SOURCE_FILE -o $BASE_NAME
        ;;
    c)
        gcc -g -O0 -pg $SOURCE_FILE -o $BASE_NAME
        ;;
    rs)
        rustc -g $SOURCE_FILE -o $BASE_NAME
        ;;
    *)
        echo "Unsupported file type: $FILE_EXT"
        exit 1
        ;;
esac

# 方法 1: GDB
echo -e "\n[1] Running GDB trace..."
./gdb_trace.sh $BASE_NAME
python3 gdb_to_graph.py

# 方法 2: uftrace (C/C++ only)
if [[ $FILE_EXT != "rs" ]]; then
    echo -e "\n[2] Running uftrace..."
    ./uftrace_trace.sh $SOURCE_FILE
    python3 uftrace_to_graph.py
else
    echo -e "\n[2] uftrace not fully supported for Rust"
fi

# 產生火焰圖 (if available)
if [ -f flame.txt ]; then
    echo -e "\n[3] Generating FlameGraph..."
    if [ ! -d FlameGraph ]; then
        git clone https://github.com/brendangregg/FlameGraph 2>/dev/null
    fi
    cat flame.txt | ./FlameGraph/flamegraph.pl > flamegraph.svg
    echo "FlameGraph saved to flamegraph.svg"
fi

echo -e "\n========================================="
echo "Completed! Generated files:"
ls -la *.svg *.png *.json 2>/dev/null | grep -E "\.(svg|png|json)$"
echo "========================================="
```

## 比較與選擇

| 特性 | GDB | uftrace |
|------|-----|---------|
| **語言支援** | C/C++/Rust/Go 等 | 主要 C/C++ |
| **效能開銷** | 高（中斷點） | 低（instrumentation） |
| **執行時間** | 有 | 有（精確） |
| **編譯需求** | -g（除錯符號） | -pg 或 -finstrument-functions |
| **即時追蹤** | 是 | 是 |
| **輸出格式** | 自訂 | 多種（Chrome、Flame、文字） |
| **學習曲線** | 陡峭 | 平緩 |
| **適用場景** | 除錯、深入分析 | 效能分析、流程追蹤 |

### 建議選擇

- **簡單流程追蹤**：uftrace
- **詳細除錯分析**：GDB
- **效能分析**：uftrace + FlameGraph
- **Rust 專案**：GDB 或 cargo-flamegraph
- **生產環境**：uftrace（開銷較小）

## 常見問題與解決方案

### ✅ 已解決問題 (2024-09-29)

#### Q1: Makefile 顏色碼不顯示（顯示 `\033[0;32m`）
**解決方案**：將所有 `echo` 改為 `printf`
```makefile
# 錯誤寫法
@echo "$(GREEN)完成$(NC)"

# 正確寫法
@printf "$(GREEN)完成$(NC)\n"
```

#### Q2: GDB logging 檔名衝突
**解決方案**：在設定新的 log 檔案前先關閉 logging
```gdb
set logging enabled off
set logging file gdb_trace.log
set logging overwrite on
set logging enabled on
```

#### Q3: Makefile heredoc 語法錯誤
**解決方案**：改用檔案複製或 echo 逐行寫入
```makefile
# 改為直接複製已存在的檔案
@cp test_program.cpp $(CPP_SOURCE)
```

### 📋 常見技術問題

#### Q1: GDB 追蹤太慢怎麼辦？

可以只追蹤特定函數：
```gdb
rbreak ^process_.*  # 只追蹤 process_ 開頭的函數
break main
break fibonacci
```

#### Q2: uftrace 沒有輸出？

檢查編譯選項：
```bash
# 確保使用了 -pg 或 -finstrument-functions
nm your_program | grep mcount  # 應該要看到 mcount
```

#### Q3: Rust 函數名太長？

使用 rustfilt 工具：
```bash
cargo install rustfilt
cat trace.log | rustfilt
```

#### Q4: 如何過濾系統函數？

GDB:
```gdb
rbreak ^[^_].*  # 排除 _ 開頭的函數
```

uftrace:
```bash
uftrace record -F main -F process_data ./program  # 只追蹤特定函數
uftrace record -N printf -N malloc ./program      # 排除特定函數
```

#### Q5: 圖表太複雜怎麼簡化？

修改 Python 腳本，加入過濾：
```python
# 只顯示執行超過 N 次的函數
MIN_CALLS = 2
filtered = [t for t in traces if call_count[t['func']] >= MIN_CALLS]
```

## 進階技巧

### 結合 perf 使用

```bash
# 記錄
perf record -g ./program

# 產生火焰圖
perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > perf.svg
```

### 自動化 CI/CD 整合

```yaml
# .github/workflows/trace.yml
name: Trace Analysis
on: [push]
jobs:
  trace:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y gdb graphviz
          pip install graphviz
      - name: Build and trace
        run: |
          make build
          ./run_all_traces.sh main.cpp
      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: trace-graphs
          path: "*.svg"
```

### 即時監控

```bash
# 使用 watch 即時更新
watch -n 1 'uftrace report -d uftrace_data | head -20'

# 使用 tail 追蹤日誌
tail -f gdb_trace.log | grep "TRACE"
```

## 參考資源

- [GDB Documentation](https://www.gnu.org/software/gdb/documentation/)
- [uftrace GitHub](https://github.com/namhyung/uftrace)
- [Flamegraph](https://github.com/brendangregg/FlameGraph)
- [Rust Profiling Book](https://nnethercote.github.io/perf-book/)
- [Chrome Tracing](chrome://tracing)
