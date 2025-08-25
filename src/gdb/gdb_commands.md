# GDB 程式流程追蹤 - 完整使用指南

## 1. 編譯程式
```bash
# 編譯時加入 -g 參數以包含除錯資訊
gcc -g -o demo demo.c
```

## 2. 方法一：使用基本 GDB 命令追蹤

### 啟動 GDB 並設定記錄
```bash
# 啟動 GDB
gdb ./demo

# 在 GDB 中設定記錄
(gdb) set logging enabled on
(gdb) set logging file basic_trace.txt
(gdb) set trace-commands on

# 設置斷點
(gdb) break main
(gdb) break calculate
(gdb) break add
(gdb) break multiply

# 設定自動命令（每次停在斷點時執行）
(gdb) commands 1-4
> silent
> printf "=== Function: "
> where 1
> info args
> info locals
> continue
> end

# 執行程式
(gdb) run

# 程式執行完畢後
(gdb) set logging enabled off
(gdb) quit
```

## 3. 方法二：使用 Python 腳本自動追蹤

### 啟動 GDB 並載入腳本
```bash
# 啟動 GDB
gdb ./demo

# 載入 Python 追蹤腳本
(gdb) source trace.py

# 開始追蹤
(gdb) trace-start

# 執行程式
(gdb) run

# 停止追蹤
(gdb) trace-stop

# 退出
(gdb) quit
```

## 4. 方法三：使用 GDB 記錄/重播功能

```bash
# 啟動 GDB
gdb ./demo

# 開始程式
(gdb) start

# 開啟記錄功能
(gdb) record

# 繼續執行
(gdb) continue

# 程式結束後，可以反向執行
(gdb) reverse-continue    # 反向執行到上一個斷點
(gdb) reverse-step        # 反向單步執行
(gdb) reverse-next        # 反向執行下一行

# 查看執行歷史
(gdb) info record

# 停止記錄
(gdb) record stop
```

## 5. 方法四：一行命令批次執行

### 建立 GDB 命令檔案 (trace_commands.gdb)
```gdb
# trace_commands.gdb
set logging enabled on
set logging file auto_trace.txt
set trace-commands on

# 設置斷點
break main
break calculate  
break add
break multiply

# 設定斷點命令
commands 1-4
silent
backtrace 1
info args
continue
end

# 執行程式
run

# 結束
set logging enabled off
quit
```

### 執行批次命令
```bash
gdb -x trace_commands.gdb ./demo
```

## 6. 檢視追蹤結果

### 基本追蹤輸出範例 (basic_trace.txt)
```
Breakpoint 1, main () at demo.c:20
#0  main () at demo.c:20
No arguments.
a = 0
b = 0

Breakpoint 3, add (a=5, b=3) at demo.c:4
#0  add (a=5, b=3) at demo.c:4
a = 5
b = 3
```

### Python 腳本追蹤輸出範例 (trace_log.txt)
```
=== Trace started at 2024-01-20 10:15:30 ===
[10:15:30.123] → main()
[10:15:30.124]   → calculate(x=5, y=3)
[10:15:30.125]     → add(a=5, b=3)
[10:15:30.126]     ← add returned: 8
[10:15:30.127]     → multiply(a=5, b=3)
[10:15:30.128]     ← multiply returned: 15
[10:15:30.129]     → add(a=8, b=15)
[10:15:30.130]     ← add returned: 23
[10:15:30.131]   ← calculate returned: 23
[10:15:30.132] ← main returned: 0
=== Trace ended at 2024-01-20 10:15:30 ===
```

## 7. 進階技巧

### 追蹤特定變數變化
```bash
(gdb) watch result
(gdb) commands
> printf "result changed to %d\n", result
> backtrace 2
> continue
> end
```

### 條件斷點
```bash
(gdb) break add if a > 10
(gdb) condition 1 a > 10
```

### 追蹤系統呼叫
```bash
(gdb) catch syscall
(gdb) commands
> info registers
> continue
> end
```

### 產生呼叫圖
```bash
# 使用 gprof 配合 GDB
gcc -pg -g -o demo demo.c
./demo
gprof demo gmon.out > call_graph.txt
```

## 8. 分析追蹤結果的小工具

### 簡單的 Python 分析腳本
```python
#!/usr/bin/env python3
# analyze_trace.py

import re
from collections import Counter

with open('trace_log.txt', 'r') as f:
    content = f.read()
    
# 統計函式呼叫次數
functions = re.findall(r'→ (\w+)\(', content)
counter = Counter(functions)

print("Function call statistics:")
for func, count in counter.most_common():
    print(f"  {func}: {count} calls")

# 計算執行時間（如果有時間戳記）
times = re.findall(r'\[(\d+:\d+:\d+\.\d+)\]', content)
if len(times) >= 2:
    # 簡單計算總執行時間
    print(f"\nTotal execution time: {times[0]} to {times[-1]}")
```

## 注意事項

1. **效能影響**：追蹤會顯著降低程式執行速度
2. **檔案大小**：長時間執行的程式可能產生很大的追蹤檔案
3. **多執行緒**：需要額外設定來正確追蹤多執行緒程式
4. **最佳化**：編譯時避免使用 -O2 或 -O3，否則可能無法正確追蹤

## 常用 GDB 追蹤命令速查

| 命令 | 說明 |
|------|------|
| `record` | 開始記錄執行 |
| `record stop` | 停止記錄 |
| `reverse-step` | 反向單步執行 |
| `reverse-continue` | 反向執行到斷點 |
| `set logging on` | 開啟日誌記錄 |
| `backtrace` / `bt` | 顯示呼叫堆疊 |
| `info args` | 顯示函式參數 |
| `info locals` | 顯示區域變數 |
| `watch` | 監視變數變化 |
| `commands` | 設定斷點自動執行命令 |