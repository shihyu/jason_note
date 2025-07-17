# GDB函數調用軌跡分析與流程圖生成完整指南

> 本指南介紹如何使用 GDB 記錄程式執行過程中的函數調用軌跡，並將其轉換為視覺化流程圖，適用於程式分析、調試和文檔製作。

## 方法一：使用 GDB 腳本記錄函數調用

### 1. 創建 GDB 追蹤腳本

```bash
# trace_functions.gdb
set logging file function_trace.txt
set logging on

# 設置在每個函數入口處的斷點
define trace_function
    if $argc == 1
        break $arg0
        commands
            silent
            printf "ENTER: %s at %s:%d\n", $arg0, __FILE__, __LINE__
            bt 1
            continue
        end
    end
end

# 設置在函數退出處的斷點
define trace_return
    if $argc == 1
        break $arg0
        commands
            silent
            printf "EXIT: %s\n", $arg0
            continue
        end
    end
end

# 追蹤特定函數
trace_function main.main
trace_function your_target_function

# 開始執行
run
```

### 2. 使用腳本運行

```bash
gdb -x trace_functions.gdb ./your_program
```

## 方法二：使用 GDB Python 腳本自動化

### 1. Python 腳本記錄調用軌跡

```python
# function_tracer.py
import gdb
import json
from datetime import datetime

class FunctionTracer:
    def __init__(self):
        self.call_stack = []
        self.function_calls = []
        self.depth = 0
    
    def trace_function_entry(self, function_name):
        timestamp = datetime.now().isoformat()
        call_info = {
            'type': 'enter',
            'function': function_name,
            'depth': self.depth,
            'timestamp': timestamp,
            'stack': list(self.call_stack)
        }
        self.function_calls.append(call_info)
        self.call_stack.append(function_name)
        self.depth += 1
        print(f"{'  ' * (self.depth-1)}→ {function_name}")
    
    def trace_function_exit(self, function_name):
        timestamp = datetime.now().isoformat()
        if self.call_stack and self.call_stack[-1] == function_name:
            self.call_stack.pop()
            self.depth -= 1
        
        call_info = {
            'type': 'exit',
            'function': function_name,
            'depth': self.depth,
            'timestamp': timestamp
        }
        self.function_calls.append(call_info)
        print(f"{'  ' * self.depth}← {function_name}")
    
    def save_trace(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.function_calls, f, indent=2)

# 創建全局追蹤器
tracer = FunctionTracer()

class FunctionBreakpoint(gdb.Breakpoint):
    def __init__(self, function_name, is_entry=True):
        super().__init__(function_name)
        self.function_name = function_name
        self.is_entry = is_entry
    
    def stop(self):
        if self.is_entry:
            tracer.trace_function_entry(self.function_name)
        else:
            tracer.trace_function_exit(self.function_name)
        return False  # 不停止執行

# 設置要追蹤的函數
functions_to_trace = [
    'main.main',
    'your_target_function',
    'another_function'
]

for func in functions_to_trace:
    FunctionBreakpoint(func, True)

# 執行完畢後保存
def save_and_exit():
    tracer.save_trace('function_trace.json')
    print("Trace saved to function_trace.json")

# 註冊退出處理
gdb.events.exited.connect(save_and_exit)
```

### 2. 使用 Python 腳本

```bash
gdb -x function_tracer.py ./your_program
```

## 方法三：使用外部工具 + GDB

### 1. 使用 `ltrace` 和 `strace` 結合

```bash
# 記錄函數調用
ltrace -f -o function_calls.txt ./your_program

# 或者使用 strace 記錄系統調用
strace -f -o system_calls.txt ./your_program
```

### 2. 使用 `perf` 記錄調用圖

```bash
# 記錄調用圖
perf record -g ./your_program
perf report --stdio > call_graph.txt

# 生成調用圖
perf script | python /usr/share/perf-core/scripts/python/flamegraph.py > flamegraph.svg
```

## 方法四：轉換成流程圖

### 1. Python 腳本轉換 JSON 為 Mermaid

```python
# json_to_mermaid.py
import json
import sys

def generate_mermaid_flowchart(trace_file):
    with open(trace_file, 'r') as f:
        calls = json.load(f)
    
    mermaid = ["graph TD"]
    
    # 提取函數調用關係
    call_stack = []
    edges = set()
    
    for call in calls:
        if call['type'] == 'enter':
            if call_stack:
                parent = call_stack[-1]
                child = call['function']
                edges.add((parent, child))
            call_stack.append(call['function'])
        elif call['type'] == 'exit' and call_stack:
            call_stack.pop()
    
    # 生成節點
    functions = set()
    for parent, child in edges:
        functions.add(parent)
        functions.add(child)
    
    # 清理函數名作為節點 ID
    def clean_name(name):
        return name.replace('.', '_').replace(':', '_')
    
    # 添加節點定義
    for func in functions:
        clean_func = clean_name(func)
        mermaid.append(f"    {clean_func}[\"{func}\"]")
    
    # 添加邊
    for parent, child in edges:
        clean_parent = clean_name(parent)
        clean_child = clean_name(child)
        mermaid.append(f"    {clean_parent} --> {clean_child}")
    
    return '\n'.join(mermaid)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_to_mermaid.py function_trace.json")
        sys.exit(1)
    
    mermaid_code = generate_mermaid_flowchart(sys.argv[1])
    
    with open('function_flowchart.mmd', 'w') as f:
        f.write(mermaid_code)
    
    print("Mermaid flowchart saved to function_flowchart.mmd")
    print("\nMermaid code:")
    print(mermaid_code)
```

### 2. 轉換為 Graphviz DOT 格式

```python
# json_to_dot.py
import json
import sys

def generate_dot_graph(trace_file):
    with open(trace_file, 'r') as f:
        calls = json.load(f)
    
    dot = ['digraph FunctionCalls {']
    dot.append('    rankdir=TD;')
    dot.append('    node [shape=box];')
    
    call_stack = []
    edges = set()
    
    for call in calls:
        if call['type'] == 'enter':
            if call_stack:
                parent = call_stack[-1]
                child = call['function']
                edges.add((parent, child))
            call_stack.append(call['function'])
        elif call['type'] == 'exit' and call_stack:
            call_stack.pop()
    
    # 添加邊
    for parent, child in edges:
        dot.append(f'    "{parent}" -> "{child}";')
    
    dot.append('}')
    return '\n'.join(dot)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python json_to_dot.py function_trace.json")
        sys.exit(1)
    
    dot_code = generate_dot_graph(sys.argv[1])
    
    with open('function_graph.dot', 'w') as f:
        f.write(dot_code)
    
    print("DOT graph saved to function_graph.dot")
    print("Generate PNG with: dot -Tpng function_graph.dot -o function_graph.png")
```

## 方法五：使用 Valgrind Callgrind

### 1. 生成調用圖

```bash
# 使用 Valgrind 生成調用圖
valgrind --tool=callgrind ./your_program

# 查看調用圖
callgrind_annotate callgrind.out.*

# 生成可視化調用圖
gprof2dot -f callgrind callgrind.out.* | dot -Tpng -o callgraph.png
```

## 完整工作流程

### 1. 記錄函數調用

```bash
# 1. 編譯程式（保留 debug symbol）
go build -gcflags="-N -l" -o myprogram main.go

# 2. 使用 GDB Python 腳本記錄
gdb -x function_tracer.py ./myprogram

# 3. 或者使用簡單的 ltrace
ltrace -f -o calls.txt ./myprogram
```

### 2. 轉換為流程圖

```bash
# 轉換 JSON 為 Mermaid
python json_to_mermaid.py function_trace.json

# 或轉換為 DOT 格式
python json_to_dot.py function_trace.json
dot -Tpng function_graph.dot -o flowchart.png
```

### 3. 在線可視化

- **Mermaid**：貼到 [mermaid.live](https://mermaid.live)
- **Graphviz**：使用 [Graphviz Online](https://dreampuf.github.io/GraphvizOnline/)

## 實用腳本：一鍵生成流程圖

```bash
#!/bin/bash
# generate_flowchart.sh

PROGRAM=$1
if [ -z "$PROGRAM" ]; then
    echo "Usage: $0 <program_path>"
    exit 1
fi

echo "🔍 分析程式: $PROGRAM"

# 1. 檢查 debug symbol
if ! file "$PROGRAM" | grep -q "not stripped"; then
    echo "❌ 程式沒有 debug symbol，請重新編譯"
    exit 1
fi

# 2. 使用 ltrace 記錄函數調用
echo "📊 記錄函數調用..."
timeout 30 ltrace -f -o function_calls.txt "$PROGRAM" 2>/dev/null

# 3. 解析並生成 DOT 格式
echo "🎨 生成流程圖..."
python3 -c "
import re
calls = []
with open('function_calls.txt', 'r') as f:
    for line in f:
        match = re.search(r'(\w+)\(', line)
        if match:
            calls.append(match.group(1))

# 生成簡單的調用關係
with open('flowchart.dot', 'w') as f:
    f.write('digraph G {\\n')
    f.write('  rankdir=TD;\\n')
    for i in range(len(calls)-1):
        f.write(f'  \"{calls[i]}\" -> \"{calls[i+1]}\";\\n')
    f.write('}\\n')
"

# 4. 生成 PNG
if command -v dot >/dev/null; then
    dot -Tpng flowchart.dot -o flowchart.png
    echo "✅ 流程圖已生成: flowchart.png"
else
    echo "✅ DOT 檔案已生成: flowchart.dot"
    echo "📝 安裝 graphviz 後執行: dot -Tpng flowchart.dot -o flowchart.png"
fi
```

## 總結

雖然 GDB 本身不能直接生成流程圖，但可以透過：
1. **記錄函數調用軌跡** (GDB 腳本/Python/ltrace)
2. **解析調用關係** (Python 腳本)
3. **轉換為圖形格式** (Mermaid/Graphviz/D3.js)

這樣的組合可以有效地將程式執行流程可視化！
