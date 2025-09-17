# GDB 自動化除錯完整指南

## 第一部分：GDB 命令行參數指南

### 快速參考

#### 基本用法
```bash
gdb [選項] [程式檔案] [核心檔案或進程ID]
```

## 四種執行腳本的方法

### 方法 1：使用 `-x` 參數
```bash
gdb -x script.gdb ./program
```

**範例：**
```bash
# 創建腳本檔案 debug.gdb
echo "break main
run
continue" > debug.gdb

# 執行
gdb -x debug.gdb ./myapp
```

### 方法 2：使用 `--command` 參數
```bash
gdb --command=script.gdb ./program
```

**範例：**
```bash
# 與方法 1 相同效果
gdb --command=debug.gdb ./myapp
```

### 方法 3：使用 `-ex` 執行命令
```bash
gdb ./program -ex "source script.gdb"
```

**範例：**
```bash
# 執行多個命令
gdb ./myapp \
  -ex "break main" \
  -ex "break func1" \
  -ex "run arg1 arg2" \
  -ex "continue"

# 載入腳本並執行
gdb ./myapp -ex "source debug.gdb" -ex "run"
```

### 方法 4：批次模式 `-batch`
```bash
gdb -batch -x script.gdb ./program
```

**範例：**
```bash
# 創建自動化測試腳本 test.gdb
cat > test.gdb << 'EOF'
break main
run
print variable1
backtrace
quit
EOF

# 批次執行（執行完自動退出）
gdb -batch -x test.gdb ./myapp > test_output.txt
```

## 方法對比

| 特性 | `-x` / `--command` | `-ex` | `-batch` |
|------|-------------------|--------|----------|
| **互動模式** | ✓ | ✓ | ✗ |
| **執行後停留** | ✓ | ✓ | ✗ |
| **多命令支援** | 腳本內 | 多個 -ex | 腳本內 |
| **自動化** | ✗ | ✗ | ✓ |
| **顯示提示符** | ✓ | ✓ | ✗ |

## 實用範例

### 1. Rust 程式除錯
```bash
# 創建 Rust 除錯腳本
cat > rust_debug.gdb << 'EOF'
set print pretty on
set print array on
break panic_impl
break rust_panic
run
EOF

# 執行
gdb -x rust_debug.gdb ./target/debug/myapp
```

### 2. 自動化測試
```bash
# 批次測試，輸出到檔案
gdb -batch -x test_suite.gdb ./app 2>&1 | tee test_results.log

# CI/CD 中使用
gdb -batch -ex "run" -ex "bt" -ex "quit" ./app core.dump
```

### 3. 快速除錯會話
```bash
# 設定斷點並執行
gdb ./app -ex "b main" -ex "r" -ex "n" -ex "p argc"

# 附加到執行中的進程
gdb -p 1234 -ex "bt" -ex "info threads"
```

### 4. 載入多個設定
```bash
# 載入符號和設定
gdb ./app \
  -ex "set sysroot /path/to/sysroot" \
  -ex "set solib-search-path /path/to/libs" \
  -ex "source ~/.gdbinit.local" \
  -ex "run"
```

## 其他實用參數

| 參數 | 說明 | 範例 |
|------|------|------|
| `-q` / `--quiet` | 安靜模式（不顯示版權信息） | `gdb -q ./app` |
| `-p PID` | 附加到進程 | `gdb -p 1234` |
| `-c core` | 載入核心轉儲 | `gdb ./app -c core.dump` |
| `-d dir` | 新增原始碼目錄 | `gdb -d /src/path ./app` |
| `--args` | 傳遞參數給程式 | `gdb --args ./app arg1 arg2` |
| `-tui` | 啟用文字介面 | `gdb -tui ./app` |

## 建議使用場景

- **互動除錯**：使用方法 1 (`-x`) 或方法 3 (`-ex`)
- **自動化測試**：使用方法 4 (`-batch`)
- **快速命令**：使用方法 3 (`-ex`)
- **複雜腳本**：使用方法 1 (`-x`) 配合腳本檔案

---

## 第二部分：GDB -ex 自動化實戰

### 核心概念
`gdb -ex` 的核心優勢是**自動化**和**腳本化**！最實用的技巧包括：

### 🚀 最常用的組合

```bash
# 1. 快速崩潰分析（最實用！）
gdb -batch -ex "run" -ex "bt" -ex "quit" ./program

# 2. 一行命令除錯
gdb -ex "b main" -ex "r" -ex "n" -ex "n" -ex "p result" ./demo

# 3. 自動生成報告
gdb -batch -ex "info functions" -ex "info variables" ./program > symbols.txt

# 4. CI/CD 整合測試
gdb -batch -ex "run < test.txt" -ex "quit" ./program || exit 1
```

### 💡 進階技巧

```bash
# 監控執行中的程式
gdb -batch -ex "attach $(pidof server)" -ex "bt" -ex "detach"

# 批量分析 core dumps
for core in *.core; do
    gdb -batch -ex "bt" ./program $core
done

# 效能分析
gdb -ex "b calculate" -ex "commands" -ex "silent" -ex "set \$count++" -ex "c" -ex "end" -ex "r" -ex "p \$count" ./demo
```

最大的好處是可以將 GDB 整合到各種自動化工作流程中，不需要人工互動！

---

## 📁 完整範例專案

### 1. 測試程式 (test_program.c)

```c
// test_program.c - 包含各種測試場景的範例程式
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>

// 全域變數用於測試
int global_counter = 0;
char global_buffer[256];

// 函式1: 可能造成 segfault
void dangerous_function(char *input) {
    char buffer[10];
    strcpy(buffer, input);  // 潛在的 buffer overflow
    printf("Buffer: %s\n", buffer);
}

// 函式2: 遞迴函式
int factorial(int n) {
    global_counter++;
    if (n <= 1) return 1;
    return n * factorial(n - 1);
}

// 函式3: 記憶體洩漏
void memory_leak() {
    for (int i = 0; i < 10; i++) {
        char *leak = malloc(1024);
        sprintf(leak, "Leak #%d", i);
        // 故意不 free
    }
}

// 函式4: 無限迴圈
void infinite_loop() {
    int i = 0;
    while (1) {
        i++;
        if (i % 1000000 == 0) {
            printf("Still running... %d\n", i);
        }
    }
}

// 函式5: 正常計算
int calculate(int a, int b, char op) {
    switch(op) {
        case '+': return a + b;
        case '-': return a - b;
        case '*': return a * b;
        case '/': return b != 0 ? a / b : 0;
        default: return 0;
    }
}

int main(int argc, char *argv[]) {
    printf("Test Program Started (PID: %d)\n", getpid());
    
    if (argc < 2) {
        printf("Usage: %s <test_number>\n", argv[0]);
        printf("Tests:\n");
        printf("  1 - Normal execution\n");
        printf("  2 - Segmentation fault\n");
        printf("  3 - Memory leak\n");
        printf("  4 - Infinite loop\n");
        printf("  5 - Factorial calculation\n");
        return 1;
    }
    
    int test = atoi(argv[1]);
    
    switch(test) {
        case 1:
            printf("Normal execution test\n");
            printf("5 + 3 = %d\n", calculate(5, 3, '+'));
            printf("5 * 3 = %d\n", calculate(5, 3, '*'));
            break;
            
        case 2:
            printf("Triggering segfault...\n");
            dangerous_function("This string is way too long for the buffer!");
            break;
            
        case 3:
            printf("Creating memory leaks...\n");
            memory_leak();
            printf("Memory leaked successfully\n");
            break;
            
        case 4:
            printf("Starting infinite loop...\n");
            infinite_loop();
            break;
            
        case 5:
            printf("Calculating factorial...\n");
            int result = factorial(10);
            printf("10! = %d\n", result);
            printf("Function called %d times\n", global_counter);
            break;
            
        default:
            printf("Invalid test number\n");
            return 1;
    }
    
    printf("Test completed\n");
    return 0;
}
```

### 2. 自動化除錯腳本 (auto_debug.sh)

```bash
#!/bin/bash
# auto_debug.sh - 完整的 GDB 自動化除錯腳本

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 設定變數
PROGRAM="test_program"
SOURCE="test_program.c"
DEBUG_LOG="debug_report_$(date +%Y%m%d_%H%M%S).log"

# 編譯函式
compile_program() {
    echo -e "${BLUE}[*] 編譯程式...${NC}"
    gcc -g -O0 -o $PROGRAM $SOURCE
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] 編譯成功${NC}"
    else
        echo -e "${RED}[✗] 編譯失敗${NC}"
        exit 1
    fi
}

# 測試1: 快速崩潰分析
test_crash_analysis() {
    echo -e "\n${YELLOW}=== 測試1: 快速崩潰分析 ===${NC}"
    
    echo "執行會崩潰的程式..."
    gdb -batch \
        -ex "run 2" \
        -ex "bt" \
        -ex "info registers" \
        -ex "info frame" \
        -ex "quit" \
        ./$PROGRAM 2>&1 | tee crash_analysis.log
    
    if grep -q "Segmentation fault" crash_analysis.log; then
        echo -e "${RED}[!] 偵測到 Segmentation fault${NC}"
        echo "詳細資訊已儲存至 crash_analysis.log"
    fi
}

# 測試2: 函式呼叫計數
test_function_calls() {
    echo -e "\n${YELLOW}=== 測試2: 函式呼叫計數 ===${NC}"
    
    result=$(gdb -batch \
        -ex "break factorial" \
        -ex "commands" \
        -ex "silent" \
        -ex "set \$count = \$count + 1" \
        -ex "continue" \
        -ex "end" \
        -ex "set \$count = 0" \
        -ex "run 5" \
        -ex "printf \"factorial 被呼叫了 %d 次\\n\", \$count" \
        -ex "quit" \
        ./$PROGRAM 2>&1)
    
    echo "$result" | grep "factorial"
}

# 測試3: 記憶體分析
test_memory_analysis() {
    echo -e "\n${YELLOW}=== 測試3: 記憶體分析 ===${NC}"
    
    gdb -batch \
        -ex "break malloc" \
        -ex "commands" \
        -ex "silent" \
        -ex "printf \"malloc called: size=%d\\n\", \$rdi" \
        -ex "backtrace 1" \
        -ex "continue" \
        -ex "end" \
        -ex "run 3" \
        -ex "quit" \
        ./$PROGRAM 2>&1 | grep -E "malloc|memory_leak"
}

# 測試4: 自動化變數監控
test_variable_watch() {
    echo -e "\n${YELLOW}=== 測試4: 變數監控 ===${NC}"
    
    gdb -batch \
        -ex "break main" \
        -ex "run 1" \
        -ex "watch global_counter" \
        -ex "continue" \
        -ex "info watchpoints" \
        -ex "quit" \
        ./$PROGRAM 2>&1 | head -20
}

# 測試5: 產生符號表報告
test_symbol_report() {
    echo -e "\n${YELLOW}=== 測試5: 符號表分析 ===${NC}"
    
    {
        echo "=== 函式列表 ==="
        gdb -batch -ex "info functions" ./$PROGRAM 2>/dev/null | grep -E "^0x"
        
        echo -e "\n=== 全域變數 ==="
        gdb -batch -ex "info variables" ./$PROGRAM 2>/dev/null | grep -E "^0x.*global"
        
        echo -e "\n=== 程式區段 ==="
        gdb -batch -ex "maintenance info sections" ./$PROGRAM 2>/dev/null | grep -E "\.text|\.data|\.bss" | head -5
    } | tee symbols_report.txt
    
    echo -e "${GREEN}[✓] 符號報告已儲存至 symbols_report.txt${NC}"
}

# 測試6: CI/CD 整合測試
test_ci_integration() {
    echo -e "\n${YELLOW}=== 測試6: CI/CD 整合測試 ===${NC}"
    
    # 建立測試輸入
    echo "1" > test_input.txt
    
    # 執行測試並檢查返回值
    echo "執行正常測試..."
    gdb -batch -ex "run 1" -ex "quit" ./$PROGRAM > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] 測試通過${NC}"
    else
        echo -e "${RED}[✗] 測試失敗${NC}"
    fi
    
    # 測試崩潰偵測
    echo "執行崩潰測試..."
    gdb -batch -ex "run 2" -ex "quit" ./$PROGRAM > /dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}[!] 偵測到預期的崩潰${NC}"
    fi
}

# 測試7: 效能分析
test_performance() {
    echo -e "\n${YELLOW}=== 測試7: 效能分析 ===${NC}"
    
    # 計算執行時間
    gdb -batch \
        -ex "break main" \
        -ex "commands" \
        -ex "silent" \
        -ex "set \$start = clock()" \
        -ex "continue" \
        -ex "end" \
        -ex "break exit" \
        -ex "commands" \
        -ex "silent" \
        -ex "set \$end = clock()" \
        -ex "printf \"執行時間: %f 秒\\n\", (\$end - \$start) / 1000000.0" \
        -ex "continue" \
        -ex "end" \
        -ex "run 5" \
        -ex "quit" \
        ./$PROGRAM 2>&1 | grep "執行時間"
}

# 測試8: 批次 Core Dump 分析
test_core_dump() {
    echo -e "\n${YELLOW}=== 測試8: Core Dump 分析 ===${NC}"
    
    # 啟用 core dump
    ulimit -c unlimited
    
    # 觸發崩潰產生 core dump
    ./$PROGRAM 2 2>/dev/null
    
    # 分析 core dump (如果存在)
    if [ -f core ]; then
        echo "分析 core dump..."
        gdb -batch \
            -ex "bt full" \
            -ex "info registers" \
            -ex "info locals" \
            -ex "quit" \
            ./$PROGRAM core | head -30
        rm -f core
    else
        echo "沒有產生 core dump (可能需要調整系統設定)"
    fi
}

# 測試9: 附加到執行中的程序
test_attach_process() {
    echo -e "\n${YELLOW}=== 測試9: 附加到執行中的程序 ===${NC}"
    
    # 啟動一個背景程序
    ./$PROGRAM 4 > /dev/null 2>&1 &
    PID=$!
    
    sleep 1
    
    if kill -0 $PID 2>/dev/null; then
        echo "附加到 PID $PID..."
        sudo gdb -batch \
            -ex "attach $PID" \
            -ex "bt" \
            -ex "info threads" \
            -ex "detach" \
            -ex "quit" 2>&1 | grep -E "Attaching|Thread|infinite_loop"
        
        # 終止程序
        kill $PID 2>/dev/null
    else
        echo "程序已結束"
    fi
}

# 測試10: 產生完整除錯報告
generate_full_report() {
    echo -e "\n${YELLOW}=== 產生完整除錯報告 ===${NC}"
    
    {
        echo "====================================="
        echo "     完整除錯報告"
        echo "     $(date)"
        echo "====================================="
        echo
        
        echo "[程式資訊]"
        file ./$PROGRAM
        echo
        
        echo "[符號表摘要]"
        gdb -batch -ex "info functions" ./$PROGRAM 2>/dev/null | wc -l | xargs echo "函式數量:"
        gdb -batch -ex "info variables" ./$PROGRAM 2>/dev/null | wc -l | xargs echo "變數數量:"
        echo
        
        echo "[反組譯 main 函式 (前10行)]"
        gdb -batch -ex "disassemble main" ./$PROGRAM 2>/dev/null | head -10
        echo
        
        echo "[正常執行輸出]"
        gdb -batch -ex "run 1" -ex "quit" ./$PROGRAM 2>&1 | tail -5
        echo
        
        echo "[記憶體映射]"
        gdb -batch \
            -ex "break main" \
            -ex "run 1" \
            -ex "info proc mappings" \
            -ex "quit" \
            ./$PROGRAM 2>&1 | grep -E "Start|program|stack|heap" | head -10
        
    } | tee $DEBUG_LOG
    
    echo -e "\n${GREEN}[✓] 完整報告已儲存至 $DEBUG_LOG${NC}"
}

# 主選單
show_menu() {
    echo -e "\n${BLUE}╔════════════════════════════════════╗"
    echo -e "║    GDB -ex 自動化除錯示範選單      ║"
    echo -e "╚════════════════════════════════════╝${NC}"
    echo
    echo "1) 執行所有測試"
    echo "2) 快速崩潰分析"
    echo "3) 函式呼叫計數"
    echo "4) 記憶體分析"
    echo "5) 變數監控"
    echo "6) 符號表分析"
    echo "7) CI/CD 整合測試"
    echo "8) 效能分析"
    echo "9) Core Dump 分析"
    echo "10) 附加到執行中程序"
    echo "11) 產生完整報告"
    echo "0) 退出"
    echo
}

# 主程式
main() {
    # 編譯程式
    compile_program
    
    if [ "$1" == "--all" ]; then
        # 執行所有測試
        test_crash_analysis
        test_function_calls
        test_memory_analysis
        test_variable_watch
        test_symbol_report
        test_ci_integration
        test_performance
        test_core_dump
        test_attach_process
        generate_full_report
    else
        # 互動式選單
        while true; do
            show_menu
            read -p "請選擇 (0-11): " choice
            
            case $choice in
                1) 
                    test_crash_analysis
                    test_function_calls
                    test_memory_analysis
                    test_variable_watch
                    test_symbol_report
                    test_ci_integration
                    test_performance
                    test_core_dump
                    test_attach_process
                    generate_full_report
                    ;;
                2) test_crash_analysis ;;
                3) test_function_calls ;;
                4) test_memory_analysis ;;
                5) test_variable_watch ;;
                6) test_symbol_report ;;
                7) test_ci_integration ;;
                8) test_performance ;;
                9) test_core_dump ;;
                10) test_attach_process ;;
                11) generate_full_report ;;
                0) 
                    echo -e "${GREEN}再見！${NC}"
                    exit 0
                    ;;
                *)
                    echo -e "${RED}無效選擇${NC}"
                    ;;
            esac
            
            read -p "按 Enter 繼續..."
        done
    fi
}

# 清理函式
cleanup() {
    echo -e "\n${YELLOW}[*] 清理檔案...${NC}"
    rm -f core test_input.txt
}

# 設定信號處理
trap cleanup EXIT

# 執行主程式
main "$@"
```

### 3. 進階 Python 整合腳本 (gdb_automation.py)

```python
#!/usr/bin/env python3
# gdb_automation.py - GDB 自動化 Python 腳本

import subprocess
import os
import sys
import json
import time
from datetime import datetime

class GDBAutomation:
    def __init__(self, program):
        self.program = program
        self.results = {}
        
    def run_gdb_command(self, commands, test_args=""):
        """執行 GDB 命令並返回輸出"""
        cmd = ["gdb", "-batch"]
        for command in commands:
            cmd.extend(["-ex", command])
        cmd.append(self.program)
        
        if test_args:
            # 修改 run 命令以包含參數
            for i, c in enumerate(cmd):
                if c.startswith("run"):
                    cmd[i] = f"run {test_args}"
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            return result.stdout
        except subprocess.TimeoutExpired:
            return "Timeout: 程式執行超時"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def analyze_crash(self):
        """分析程式崩潰"""
        print("🔍 分析崩潰...")
        commands = [
            "run 2",
            "bt full",
            "info registers",
            "info frame",
            "quit"
        ]
        output = self.run_gdb_command(commands)
        
        # 解析輸出
        if "Segmentation fault" in output:
            crash_info = {
                "status": "crashed",
                "type": "Segmentation fault",
                "backtrace": self._extract_backtrace(output)
            }
        else:
            crash_info = {"status": "no crash"}
        
        self.results["crash_analysis"] = crash_info
        return crash_info
    
    def count_function_calls(self, function_name):
        """計算函式呼叫次數"""
        print(f"📊 計算 {function_name} 呼叫次數...")
        commands = [
            f"break {function_name}",
            "commands",
            "silent",
            "set $count = $count + 1",
            "continue",
            "end",
            "set $count = 0",
            "run 5",
            'printf "Count: %d\\n", $count',
            "quit"
        ]
        output = self.run_gdb_command(commands)
        
        # 提取計數
        import re
        match = re.search(r"Count: (\d+)", output)
        count = int(match.group(1)) if match else 0
        
        self.results[f"{function_name}_calls"] = count
        return count
    
    def profile_memory(self):
        """記憶體分析"""
        print("💾 分析記憶體使用...")
        commands = [
            "break malloc",
            "commands",
            "silent",
            'printf "malloc: %d bytes\\n", $rdi',
            "continue",
            "end",
            "run 3",
            "quit"
        ]
        output = self.run_gdb_command(commands)
        
        # 統計 malloc 呼叫
        mallocs = re.findall(r"malloc: (\d+) bytes", output)
        total_allocated = sum(int(m) for m in mallocs)
        
        self.results["memory_profile"] = {
            "malloc_calls": len(mallocs),
            "total_allocated": total_allocated
        }
        return self.results["memory_profile"]
    
    def generate_report(self):
        """產生 JSON 格式報告"""
        print("📝 產生報告...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "program": self.program,
            "results": self.results
        }
        
        # 儲存為 JSON
        with open("gdb_report.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # 產生 Markdown 報告
        self._generate_markdown_report()
        
        return report
    
    def _extract_backtrace(self, output):
        """從輸出中提取 backtrace"""
        lines = output.split('\n')
        backtrace = []
        for line in lines:
            if line.startswith('#'):
                backtrace.append(line.strip())
        return backtrace
    
    def _generate_markdown_report(self):
        """產生 Markdown 格式報告"""
        with open("gdb_report.md", "w") as f:
            f.write("# GDB 自動化分析報告\n\n")
            f.write(f"**時間**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**程式**: `{self.program}`\n\n")
            
            if "crash_analysis" in self.results:
                f.write("## 崩潰分析\n\n")
                crash = self.results["crash_analysis"]
                if crash["status"] == "crashed":
                    f.write(f"- **狀態**: ⚠️ {crash['type']}\n")
                    f.write("- **Backtrace**:\n```\n")
                    for bt in crash.get("backtrace", []):
                        f.write(f"{bt}\n")
                    f.write("```\n\n")
                else:
                    f.write("- **狀態**: ✅ 無崩潰\n\n")
            
            if "factorial_calls" in self.results:
                f.write("## 函式呼叫統計\n\n")
                f.write(f"- `factorial()` 被呼叫 **{self.results['factorial_calls']}** 次\n\n")
            
            if "memory_profile" in self.results:
                f.write("## 記憶體分析\n\n")
                mem = self.results["memory_profile"]
                f.write(f"- malloc 呼叫次數: **{mem['malloc_calls']}**\n")
                f.write(f"- 總配置記憶體: **{mem['total_allocated']} bytes**\n\n")

def main():
    # 編譯測試程式
    print("🔨 編譯程式...")
    os.system("gcc -g -O0 -o test_program test_program.c")
    
    # 建立自動化物件
    gdb = GDBAutomation("test_program")
    
    # 執行各項測試
    gdb.analyze_crash()
    gdb.count_function_calls("factorial")
    gdb.profile_memory()
    
    # 產生報告
    report = gdb.generate_report()
    
    print("\n✅ 分析完成！")
    print(f"📊 結果摘要:")
    print(json.dumps(report["results"], indent=2))
    print(f"\n📁 報告已儲存至:")
    print("  - gdb_report.json")
    print("  - gdb_report.md")

if __name__ == "__main__":
    main()
```

### 4. Makefile 整合

```makefile
# Makefile - 整合 GDB 自動化到建構流程

CC = gcc
CFLAGS = -g -O0 -Wall
PROGRAM = test_program
SOURCE = test_program.c

.PHONY: all clean test debug analyze

all: $(PROGRAM)

$(PROGRAM): $(SOURCE)
	$(CC) $(CFLAGS) -o $@ $<

# 執行所有測試
test: $(PROGRAM)
	@echo "Running automated tests..."
	@gdb -batch -ex "run 1" -ex "quit" ./$(PROGRAM) > /dev/null && echo "✓ Test 1: Normal execution"
	@gdb -batch -ex "run 5" -ex "quit" ./$(PROGRAM) > /dev/null && echo "✓ Test 5: Factorial"
	@echo "All tests passed!"

# 除錯模式
debug: $(PROGRAM)
	gdb -ex "break main" -ex "run 1" ./$(PROGRAM)

# 快速崩潰分析
crash: $(PROGRAM)
	@echo "Analyzing crash..."
	@gdb -batch -ex "run 2" -ex "bt" -ex "quit" ./$(PROGRAM) | grep -A5 "Segmentation"

# 符號分析
symbols: $(PROGRAM)
	@echo "Extracting symbols..."
	@gdb -batch -ex "info functions" ./$(PROGRAM) > symbols.txt
	@echo "Symbols saved to symbols.txt"

# 效能分析
profile: $(PROGRAM)
	@echo "Profiling function calls..."
	@gdb -batch \
		-ex "break factorial" \
		-ex "commands" \
		-ex "silent" \
		-ex "set \$$count++" \
		-ex "continue" \
		-ex "end" \
		-ex "set \$$count = 0" \
		-ex "run 5" \
		-ex 'printf "factorial called %d times\n", \$$count' \
		-ex "quit" \
		./$(PROGRAM)

# 記憶體檢查
memcheck: $(PROGRAM)
	@echo "Checking memory..."
	@gdb -batch \
		-ex "break malloc" \
		-ex "commands" \
		-ex "silent" \
		-ex 'printf "malloc: %d bytes\n", \$$rdi' \
		-ex "continue" \
		-ex "end" \
		-ex "run 3" \
		-ex "quit" \
		./$(PROGRAM) | grep malloc | wc -l | xargs echo "Total malloc calls:"

# 完整分析
analyze: $(PROGRAM)
	@bash auto_debug.sh --all

# Python 分析
pyanalyze: $(PROGRAM)
	@python3 gdb_automation.py

# CI/CD 整合
ci-test: $(PROGRAM)
	@echo "Running CI tests..."
	@for test in 1 5; do \
		if gdb -batch -ex "run $$test" -ex "quit" ./$(PROGRAM) > /dev/null 2>&1; then \
			echo "✓ Test $$test passed"; \
		else \
			echo "✗ Test $$test failed"; \
			exit 1; \
		fi \
	done
	@echo "CI tests completed successfully!"

# 清理
clean:
	rm -f $(PROGRAM) *.log *.txt *.json *.md core

# 說明
help:
	@echo "Available targets:"
	@echo "  make all      - Build the program"
	@echo "  make test     - Run automated tests"
	@echo "  make debug    - Start interactive debugging"
	@echo "  make crash    - Analyze crash"
	@echo "  make symbols  - Extract symbols"
	@echo "  make profile  - Profile function calls"
	@echo "  make memcheck - Check memory usage"
	@echo "  make analyze  - Run full analysis"
	@echo "  make pyanalyze- Run Python analysis"
	@echo "  make ci-test  - Run CI/CD tests"
	@echo "  make clean    - Clean build files"
```

### 5. Docker 整合 (Dockerfile)

```dockerfile
# Dockerfile - 容器化 GDB 自動化環境

FROM ubuntu:22.04

# 安裝必要套件
RUN apt-get update && apt-get install -y \
    build-essential \
    gdb \
    python3 \
    python3-pip \
    make \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 複製檔案
COPY test_program.c .
COPY auto_debug.sh .
COPY gdb_automation.py .
COPY Makefile .

# 設定執行權限
RUN chmod +x auto_debug.sh

# 編譯程式
RUN make all

# 預設命令
CMD ["bash", "auto_debug.sh"]
```

### 6. GitHub Actions CI/CD (.github/workflows/gdb-test.yml)

```yaml
name: GDB Automated Testing

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Install dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y gdb build-essential
    
    - name: Compile program
      run: make all
    
    - name: Run automated tests
      run: |
        # 正常執行測試
        gdb -batch -ex "run 1" -ex "quit" ./test_program
        
        # 函式呼叫測試
        gdb -batch -ex "run 5" -ex "quit" ./test_program
    
    - name: Check for crashes
      run: |
        # 這個應該會失敗（預期行為）
        if gdb -batch -ex "run 2" -ex "quit" ./test_program 2>&1 | grep -q "Segmentation"; then
          echo "Expected crash detected"
        else
          echo "Unexpected: no crash detected"
          exit 1
        fi
    
    - name: Generate analysis report
      run: |
        make analyze
        
    - name: Upload reports
      uses: actions/upload-artifact@v2
      with:
        name: gdb-reports
        path: |
          *.log
          *.txt
          *.json
          *.md
```

## 使用說明

### 快速開始

1. **儲存所有檔案到同一目錄**

2. **執行互動式選單**：
```bash
chmod +x auto_debug.sh
./auto_debug.sh
```

3. **執行所有測試**：
```bash
./auto_debug.sh --all
```

4. **使用 Makefile**：
```bash
make all        # 編譯
make test       # 測試
make analyze    # 完整分析
make clean      # 清理
```

5. **使用 Python 腳本**：
```bash
python3 gdb_automation.py
```

6. **Docker 執行**：
```bash
docker build -t gdb-auto .
docker run -it gdb-auto
```

## 輸出範例

執行後會產生多個報告檔案：

- `debug_report_YYYYMMDD_HHMMSS.log` - 完整除錯報告
- `crash_analysis.log` - 崩潰分析
- `symbols_report.txt` - 符號表報告
- `gdb_report.json` - JSON 格式報告
- `gdb_report.md` - Markdown 格式報告

## 最佳實踐

1. **使用 `-batch` 提高效率**
2. **善用 `-ex` 串接命令**
3. **結合 Shell 腳本自動化**
4. **整合到 CI/CD 流程**
5. **產生結構化報告便於分析**

這個完整範例展示了 `gdb -ex` 在實際專案中的強大應用！