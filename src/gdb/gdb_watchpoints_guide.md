# GDB Watchpoints 和 Catchpoints 完整指南

## 目錄
- [概述](#概述)
- [指令總覽](#指令總覽)
- [範例程式](#範例程式)
- [Watchpoints 詳細範例](#watchpoints-詳細範例)
- [Catchpoints 詳細範例](#catchpoints-詳細範例)
- [進階技巧](#進階技巧)
- [常見問題](#常見問題)

## 概述

GDB 提供了強大的監控機制，讓開發者能夠在特定條件下暫停程式執行：
- **Watchpoints**: 監控變數或記憶體位置的存取
- **Catchpoints**: 捕捉系統事件和例外

## 指令總覽

### Watchpoint 相關指令

| 指令 | 功能 | 語法範例 |
|------|------|----------|
| `watch` | 當值被修改時中斷 | `watch variable` |
| `rwatch` | 當值被讀取時中斷 | `rwatch variable` |
| `awatch` | 當值被讀取或修改時中斷 | `awatch variable` |
| `info watchpoints` | 顯示所有 watchpoint | `info watchpoints` |

### Catchpoint 相關指令

| 指令 | 功能 | 語法範例 |
|------|------|----------|
| `catch throw` | 捕捉 C++ 例外拋出 | `catch throw` |
| `catch catch` | 捕捉 C++ 例外被接住 | `catch catch` |
| `catch exec` | 捕捉 exec 系統呼叫 | `catch exec` |
| `catch fork` | 捕捉 fork 系統呼叫 | `catch fork` |
| `catch syscall` | 捕捉特定系統呼叫 | `catch syscall open` |
| `catch signal` | 捕捉信號 | `catch signal SIGINT` |
| `catch load` | 捕捉動態函式庫載入 | `catch load` |
| `catch unload` | 捕捉動態函式庫卸載 | `catch unload` |

### 其他相關指令

| 指令 | 功能 | 語法範例 |
|------|------|----------|
| `break` / `b` | 設定一般斷點 | `break main.c:10` |
| `tbreak` | 設定暫時斷點 | `tbreak function_name` |
| `condition` | 為斷點添加條件 | `condition 1 x > 5` |
| `commands` | 設定斷點觸發時的命令 | `commands 1` |
| `delete` | 刪除斷點 | `delete 1` |
| `disable` | 停用斷點 | `disable 2` |
| `enable` | 啟用斷點 | `enable 2` |
| `info breakpoints` | 顯示所有斷點 | `info breakpoints` |

## 範例程式

```cpp
#include <iostream>
#include <stdexcept>
#include <cstring>

// 全域變數用於 watch 示範
int global_counter = 0;
char buffer[100];

// 類別用於示範例外處理
class Calculator {
private:
    int result;
    
public:
    Calculator() : result(0) {}
    
    int divide(int a, int b) {
        if (b == 0) {
            throw std::runtime_error("Division by zero!");
        }
        result = a / b;
        return result;
    }
    
    int getResult() const {
        return result;
    }
    
    void setResult(int val) {
        result = val;
    }
};

// 函數用於修改全域變數
void modify_counter() {
    global_counter++;  // 寫入操作
    std::cout << "Counter modified to: " << global_counter << std::endl;
}

void read_counter() {
    int temp = global_counter;  // 讀取操作
    std::cout << "Counter read, value is: " << temp << std::endl;
}

void access_counter() {
    global_counter *= 2;  // 讀取並寫入
    std::cout << "Counter accessed and doubled: " << global_counter << std::endl;
}

int main() {
    std::cout << "=== GDB Watch and Catch Demo ===" << std::endl;
    
    // Part 1: Watchpoint 示範
    std::cout << "\n--- Part 1: Watchpoint Demo ---" << std::endl;
    
    global_counter = 10;
    std::cout << "Initial counter: " << global_counter << std::endl;
    
    modify_counter();  // 會觸發 watch
    read_counter();    // 會觸發 rwatch
    access_counter();  // 會觸發 awatch
    
    // 字串操作
    strcpy(buffer, "Hello");
    std::cout << "Buffer: " << buffer << std::endl;
    strcat(buffer, " World");
    std::cout << "Buffer after concat: " << buffer << std::endl;
    
    // Part 2: Catch 示範 - 例外處理
    std::cout << "\n--- Part 2: Exception Catch Demo ---" << std::endl;
    
    Calculator calc;
    
    try {
        std::cout << "10 / 2 = " << calc.divide(10, 2) << std::endl;
        std::cout << "20 / 5 = " << calc.divide(20, 5) << std::endl;
        std::cout << "Attempting 15 / 0..." << std::endl;
        std::cout << "15 / 0 = " << calc.divide(15, 0) << std::endl;  // 會拋出例外
    }
    catch (const std::runtime_error& e) {
        std::cout << "Caught exception: " << e.what() << std::endl;
    }
    
    // Part 3: 動態記憶體配置 (可用於 catch syscall)
    std::cout << "\n--- Part 3: Dynamic Memory ---" << std::endl;
    
    int* arr = new int[5];
    for (int i = 0; i < 5; i++) {
        arr[i] = i * 10;
        std::cout << "arr[" << i << "] = " << arr[i] << std::endl;
    }
    delete[] arr;
    
    std::cout << "\nProgram completed!" << std::endl;
    return 0;
}
```

### 編譯指令
```bash
# 使用 -g 編譯以包含除錯資訊
g++ -g -o test test.cpp
```

## Watchpoints 詳細範例

### 1. Watch - 監控變數寫入

```bash
$ gdb ./test
(gdb) break main
Breakpoint 1 at 0x1234: file test.cpp, line 49.

(gdb) run
Starting program: ./test
Breakpoint 1, main () at test.cpp:49

# 設定 watch - 當 global_counter 被修改時中斷
(gdb) watch global_counter
Hardware watchpoint 2: global_counter

(gdb) continue
Continuing.
=== GDB Watch and Catch Demo ===

--- Part 1: Watchpoint Demo ---

Hardware watchpoint 2: global_counter

Old value = 0
New value = 10
main () at test.cpp:54
54	    std::cout << "Initial counter: " << global_counter << std::endl;

(gdb) continue
Continuing.
Initial counter: 10

Hardware watchpoint 2: global_counter

Old value = 10
New value = 11
modify_counter () at test.cpp:35
35	    std::cout << "Counter modified to: " << global_counter << std::endl;
```

### 2. RWatch - 監控變數讀取

```bash
# 重新開始並設定 rwatch
(gdb) delete  # 刪除所有斷點
Delete all breakpoints? (y or n) y

(gdb) break main
Breakpoint 1 at 0x1234: file test.cpp, line 49.

(gdb) run
Starting program: ./test
Breakpoint 1, main () at test.cpp:49

# 前進到適當位置
(gdb) next
(gdb) next

# 設定 rwatch - 當 global_counter 被讀取時中斷
(gdb) rwatch global_counter
Hardware read watchpoint 3: global_counter

(gdb) continue
Continuing.

Hardware read watchpoint 3: global_counter

Value = 11
read_counter () at test.cpp:39
39	    int temp = global_counter;  // 讀取操作

(gdb) backtrace
#0  read_counter () at test.cpp:39
#1  0x0000123456 in main () at test.cpp:57

(gdb) print global_counter
$1 = 11
```

### 3. AWatch - 監控變數讀取或寫入

```bash
# 設定 awatch - 當 global_counter 被讀取或寫入時都中斷
(gdb) delete
Delete all breakpoints? (y or n) y

(gdb) break main
Breakpoint 1 at 0x1234: file test.cpp, line 49.

(gdb) run
Starting program: ./test
Breakpoint 1, main () at test.cpp:49

(gdb) awatch global_counter
Hardware access (read/write) watchpoint 4: global_counter

(gdb) continue
Continuing.

Hardware access (read/write) watchpoint 4: global_counter

Value = 0
main () at test.cpp:53
53	    global_counter = 10;

(gdb) continue
Continuing.

Hardware access (read/write) watchpoint 4: global_counter

Old value = 0
New value = 10
main () at test.cpp:54

# 會在每次讀取或寫入時都中斷
```

### 4. 監控陣列元素

```bash
# 監控特定陣列元素
(gdb) watch buffer[5]
Hardware watchpoint 5: buffer[5]

# 監控整個陣列的前 10 個元素
(gdb) watch *buffer@10
Hardware watchpoint 6: *buffer@10

# 監控特定記憶體位址
(gdb) print &global_counter
$2 = (int *) 0x555555558040

(gdb) watch *(int*)0x555555558040
Hardware watchpoint 7: *(int*)0x555555558040
```

## Catchpoints 詳細範例

### 1. Catch Throw - 捕捉例外拋出

```bash
(gdb) delete
Delete all breakpoints? (y or n) y

# 設定捕捉例外拋出
(gdb) catch throw
Catchpoint 1 (throw)

(gdb) run
Starting program: ./test

# 執行到例外拋出處
=== GDB Watch and Catch Demo ===
--- Part 1: Watchpoint Demo ---
...
--- Part 2: Exception Catch Demo ---
10 / 2 = 5
20 / 5 = 4
Attempting 15 / 0...

Catchpoint 1 (exception thrown), 0x00007ffff7abc123 in __cxa_throw ()
   from /usr/lib/x86_64-linux-gnu/libstdc++.so.6

(gdb) backtrace
#0  __cxa_throw () from /usr/lib/x86_64-linux-gnu/libstdc++.so.6
#1  0x0000555555555234 in Calculator::divide (this=0x7fffffffe3d0, a=15, b=0) 
    at test.cpp:19
#2  0x0000555555555456 in main () at test.cpp:77

# 檢查拋出例外的位置
(gdb) frame 1
#1  0x0000555555555234 in Calculator::divide (this=0x7fffffffe3d0, a=15, b=0) 
    at test.cpp:19
19	            throw std::runtime_error("Division by zero!");

(gdb) print a
$3 = 15
(gdb) print b
$4 = 0
```

### 2. Catch Catch - 捕捉例外被接住

```bash
# 同時設定捕捉例外拋出和接住
(gdb) catch throw
Catchpoint 1 (throw)

(gdb) catch catch
Catchpoint 2 (catch)

(gdb) run
Starting program: ./test

# 第一次中斷：例外被拋出
Catchpoint 1 (exception thrown), ...

(gdb) continue
Continuing.

# 第二次中斷：例外被接住
Catchpoint 2 (exception caught), 0x00007ffff7abc456 in __cxa_begin_catch ()
   from /usr/lib/x86_64-linux-gnu/libstdc++.so.6

(gdb) backtrace
#0  __cxa_begin_catch () from /usr/lib/x86_64-linux-gnu/libstdc++.so.6
#1  0x0000555555555678 in main () at test.cpp:79

(gdb) frame 1
#1  0x0000555555555678 in main () at test.cpp:79
79	    catch (const std::runtime_error& e) {

(gdb) continue
Continuing.
Caught exception: Division by zero!
```

### 3. Catch Syscall - 捕捉系統呼叫

```bash
# 捕捉記憶體相關系統呼叫
(gdb) catch syscall mmap
Catchpoint 3 (syscall 'mmap' [9])

(gdb) catch syscall munmap
Catchpoint 4 (syscall 'munmap' [11])

# 捕捉所有系統呼叫
(gdb) catch syscall
Catchpoint 5 (any syscall)

# 捕捉特定系統呼叫群組
(gdb) catch syscall open close read write
Catchpoint 6 (syscalls 'open' [2] 'close' [3] 'read' [0] 'write' [1])

(gdb) run
Starting program: ./test

# 當呼叫 new (內部使用 mmap) 時
Catchpoint 3 (call to syscall mmap), 0x00007ffff7abc789 in mmap64 ()
   from /lib/x86_64-linux-gnu/libc.so.6

(gdb) backtrace
#0  mmap64 () from /lib/x86_64-linux-gnu/libc.so.6
#1  0x00007ffff7def123 in operator new[] () 
    from /usr/lib/x86_64-linux-gnu/libstdc++.so.6
#2  0x0000555555555890 in main () at test.cpp:87
```

### 4. Catch Fork - 捕捉程序建立

```bash
# 捕捉 fork 系統呼叫
(gdb) catch fork
Catchpoint 7 (fork)

(gdb) catch vfork
Catchpoint 8 (vfork)

(gdb) catch exec
Catchpoint 9 (exec)

# 當程式 fork 時會中斷
(gdb) run
Starting program: ./test_fork

Catchpoint 7 (forked process 12345), 0x00007ffff7abc123 in fork ()
   from /lib/x86_64-linux-gnu/libc.so.6

(gdb) info inferiors
  Num  Description       Executable        
* 1    process 12344     /home/user/test_fork
  2    process 12345     /home/user/test_fork

# 可以切換到子程序
(gdb) inferior 2
[Switching to inferior 2 [process 12345]]
```

## 進階技巧

### 1. 組合使用多個監控點

```bash
# 同時設定多個監控點
(gdb) watch global_counter
Hardware watchpoint 1: global_counter

(gdb) catch throw
Catchpoint 2 (throw)

(gdb) break Calculator::divide if b==0
Breakpoint 3 at 0x555555555234: file test.cpp, line 17.

# 為斷點 3 添加自動執行命令
(gdb) commands 3
Type commands for breakpoint(s) 3, one per line.
End with a line saying just "end".
> printf "Warning: Dividing by zero!\n"
> backtrace 2
> continue
> end
```

### 2. 條件式 Watchpoint

```bash
# 只在特定條件下觸發 watchpoint
(gdb) watch global_counter if global_counter > 10
Hardware watchpoint 4: global_counter

# 監控表達式
(gdb) watch (global_counter + 5) * 2
Hardware watchpoint 5: (global_counter + 5) * 2
```

### 3. 管理監控點

```bash
# 顯示所有斷點和監控點
(gdb) info breakpoints
Num     Type           Disp Enb Address            What
1       hw watchpoint  keep y                      global_counter
2       catchpoint     keep y                      exception throw
3       breakpoint     keep y   0x0000555555555234 in Calculator::divide(int, int) 
                                                   at test.cpp:17
        stop only if b==0

# 顯示只有 watchpoints
(gdb) info watchpoints
Num     Type           Disp Enb Address    What
1       hw watchpoint  keep y              global_counter

# 停用特定監控點
(gdb) disable 1

# 啟用特定監控點
(gdb) enable 1

# 刪除特定監控點
(gdb) delete 2

# 刪除所有監控點
(gdb) delete
Delete all breakpoints? (y or n) y
```

### 4. 記憶體監控技巧

```bash
# 監控結構體成員
(gdb) watch calc.result

# 監控指標指向的值
(gdb) watch *ptr

# 監控特定大小的記憶體區域
(gdb) watch -l *(char *)buffer@10

# 使用硬體斷點
(gdb) hbreak *0x555555555234

# 監控記憶體範圍
(gdb) watch $rsp
(gdb) watch *(int *)($rsp + 8)
```

## 常見問題

### Q1: 為什麼 watchpoint 顯示 "Hardware watchpoint"？

GDB 優先使用硬體 watchpoint（由 CPU 支援），因為效能較好。如果硬體資源不足，會使用軟體 watchpoint。

### Q2: 可以設定多少個 watchpoint？

硬體 watchpoint 數量受 CPU 限制（通常為 4 個）。軟體 watchpoint 沒有數量限制，但會顯著降低執行速度。

### Q3: 如何監控動態配置的記憶體？

```bash
# 先執行到 new/malloc 之後
(gdb) print arr
$1 = (int *) 0x555555559eb0

# 然後設定 watchpoint
(gdb) watch *arr
(gdb) watch arr[3]
```

### Q4: Watchpoint 和 Breakpoint 的差異？

- **Breakpoint**: 在特定程式碼位置中斷
- **Watchpoint**: 在資料變化時中斷，不限定程式碼位置

### Q5: 如何調試多執行緒程式的 watchpoint？

```bash
# 設定所有執行緒都會觸發
(gdb) watch global_var

# 只在特定執行緒觸發
(gdb) watch global_var thread 2

# 顯示執行緒資訊
(gdb) info threads
```

### Q6: Catchpoint 支援哪些事件？

- C++ 例外：`throw`, `catch`, `rethrow`
- 系統呼叫：`syscall`, `fork`, `vfork`, `exec`
- 動態載入：`load`, `unload`
- 信號：`signal`
- Ada 例外：`exception`, `handlers`, `assert`

## 實用範例腳本

### 自動化調試腳本

```bash
# debug_script.gdb
# 使用方式: gdb -x debug_script.gdb ./test

# 設定初始斷點
break main

# 執行程式
run

# 設定監控點
watch global_counter
catch throw

# 設定條件斷點
break Calculator::divide if b==0
commands
  printf "Division by zero detected!\n"
  printf "a = %d, b = %d\n", a, b
  backtrace
  continue
end

# 繼續執行
continue
```

執行腳本：
```bash
gdb -x debug_script.gdb ./test
```

## 總結

GDB 的 watchpoint 和 catchpoint 功能提供了強大的調試能力：

1. **Watchpoint** 適合追蹤資料問題
   - `watch`: 追蹤意外的資料修改
   - `rwatch`: 找出誰在讀取資料
   - `awatch`: 完整監控資料存取

2. **Catchpoint** 適合追蹤系統事件
   - 例外處理調試
   - 系統呼叫分析
   - 程序管理追蹤

3. **最佳實踐**
   - 優先使用硬體 watchpoint
   - 適當組合不同類型的監控點
   - 使用腳本自動化重複的調試任務
   - 善用條件和命令增強監控點功能

透過熟練掌握這些工具，可以大幅提升調試效率，快速定位並解決程式問題。