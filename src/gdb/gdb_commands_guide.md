# GDB Commands 和腳本語法完整指南

## 目錄
- [Commands 基本語法](#commands-基本語法)
- [常用 Commands 範例](#常用-commands-範例)
- [條件控制語法](#條件控制語法)
- [循環控制語法](#循環控制語法)
- [自定義函數 (define)](#自定義函數-define)
- [GDB 腳本檔案](#gdb-腳本檔案)
- [進階應用範例](#進階應用範例)

## Commands 基本語法

### 1. 基本結構

```gdb
(gdb) commands [斷點編號]
Type commands for breakpoint(s) N, one per line.
End with a line saying just "end".
> 命令1
> 命令2
> 命令3
> end
```

### 2. 語法規則

- `commands` 後可接斷點編號，若省略則套用到最近設定的斷點
- 每個命令佔一行
- 必須以 `end` 結束命令序列
- 支援所有 GDB 命令和自定義函數

## Continue 指令的重要性

### 為什麼需要 continue？

在 `commands` 區塊中，`continue` 指令決定了程式是否會在斷點處停止：

- **沒有 continue**：程式執行完 commands 後會停在斷點處，等待手動輸入
- **有 continue**：程式執行完 commands 後自動繼續執行

### Continue 的執行流程比較

#### 1. 沒有 continue（會停止）
```gdb
(gdb) break main
(gdb) commands 1
> printf "Hit breakpoint\n"
> print x
> end  # 沒有 continue，程式會停在這裡
```
結果：需要手動輸入 `continue` 或 `next` 才能繼續

#### 2. 有 continue（自動繼續）
```gdb
(gdb) break main  
(gdb) commands 1
> printf "Hit breakpoint\n"
> print x
> continue  # 自動繼續執行，不會停下來
> end
```
結果：程式自動繼續執行，適合記錄和監控

### Continue 的位置策略

#### 在結尾（最常見）
```gdb
(gdb) commands
> print x
> print y
> continue  # 執行完所有命令後繼續
> end
```

#### 在條件中（選擇性繼續）
```gdb
(gdb) commands
> if (x == 0)
>   continue  # 滿足條件時直接繼續，跳過後面的命令
> end
> # x != 0 時才會執行以下命令
> print "x is not zero"
> print x
> # 這裡故意不加 continue，會停下來
> end
```

#### 混合使用（智能停止）
```gdb
(gdb) commands
> silent
> printf "Function called with: %d\n", param
> if (param > 0 && param < 100)
>   # 正常範圍，繼續執行
>   continue
> end
> # 異常值，停下來調試
> printf "Abnormal parameter: %d\n", param
> backtrace
> # 不加 continue，需要手動檢查
> end
```

## 常用 Commands 範例

### 1. 基本輸出和繼續執行

```gdb
(gdb) break main
Breakpoint 1 at 0x1150: file test.cpp, line 10.

(gdb) commands 1
> printf "Program started at main()\n"
> print argc
> print argv[0]
> continue  # 記錄後自動繼續
> end
```

### 2. 記錄變數值（不中斷執行）

```gdb
(gdb) break loop_function
Breakpoint 2 at 0x1234: file test.cpp, line 25.

(gdb) commands 2
> silent  # 抑制預設訊息
> printf "i = %d, sum = %d\n", i, sum
> continue  # 必須加 continue，否則迴圈會卡住
> end
```

### 3. 調試模式（需要停止檢查）

```gdb
(gdb) break error_handler
Breakpoint 3 at 0x1300: file test.cpp, line 40.

(gdb) commands 3
> echo === Error Occurred ===\n
> print error_code
> print error_message
> backtrace
> info locals
> # 故意不加 continue，需要手動檢查錯誤
> end
```

### 4. 性能分析（高頻斷點必須用 continue）

```gdb
(gdb) break frequently_called_function
Breakpoint 4 at 0x1400: file test.cpp, line 55.

(gdb) commands 4
> silent
> set $call_count = $call_count + 1
> if ($call_count % 10000 == 0)
>   printf "Function called %d times\n", $call_count
> end
> continue  # 高頻函數必須自動繼續，否則程式無法正常運行
> end
```

### 5. 條件式停止（智能調試）

```gdb
(gdb) break process_data
Breakpoint 5 at 0x1500: file test.cpp, line 70.

(gdb) commands 5
> silent
> if (data_size < 1000)
>   # 小數據，不需要調試
>   continue
> end
> # 大數據，需要檢查
> printf "Processing large data: size=%d\n", data_size
> print data_ptr
> info locals
> # 不加 continue，讓開發者決定如何處理
> end
```

**註：`silent` 可以抑制斷點觸發的預設訊息**

### 3. 條件式輸出

```gdb
(gdb) break process_data
Breakpoint 3 at 0x1300: file test.cpp, line 40.

(gdb) commands 3
> silent
> if (value > 100)
>   printf "Warning: value = %d exceeds limit!\n", value
>   backtrace
> end
> continue  # 記錄後繼續執行
> end
```

### 4. 收集資料到檔案（背景記錄）

```gdb
(gdb) break calculate
Breakpoint 4 at 0x1400: file test.cpp, line 55.

(gdb) commands 4
> silent
> set logging file debug.log
> set logging on
> printf "Time: %d, Result: %f\n", timestamp, result
> set logging off
> continue  # 記錄後自動繼續，不中斷程式
> end
```

### 5. 複雜的調試序列（需要停止）

```gdb
(gdb) break error_handler
Breakpoint 5 at 0x1500: file test.cpp, line 70.

(gdb) commands 5
> echo === Error occurred ===\n
> backtrace full
> info locals
> info args
> up
> info locals
> down
> if (error_code == -1)
>   print *error_struct
>   x/10x error_buffer
> end
> # 注意：這裡沒有 continue，因為錯誤需要手動檢查
> end
```

## 條件控制語法

### 1. if-else 結構

```gdb
(gdb) commands 6
> if (ptr != 0)
>   print *ptr
>   printf "Pointer value: 0x%x\n", ptr
> else
>   echo Pointer is NULL\n
> end
> continue
> end
```

### 2. 巢狀條件

```gdb
(gdb) commands 7
> if (status == 1)
>   echo Status: Running\n
>   if (counter > 10)
>     echo Counter overflow!\n
>     set counter = 0
>   end
> else
>   if (status == 0)
>     echo Status: Stopped\n
>   else
>     echo Status: Unknown\n
>   end
> end
> continue
> end
```

### 3. 多重條件檢查

```gdb
(gdb) commands 8
> silent
> set $flag = 0
> if (x > 0 && y > 0)
>   set $flag = 1
>   echo First quadrant\n
> end
> if (x < 0 && y > 0)
>   set $flag = 2
>   echo Second quadrant\n
> end
> if ($flag == 0)
>   echo Origin or axis\n
> end
> continue
> end
```

## 循環控制語法

### 1. while 循環

```gdb
(gdb) commands 9
> set $i = 0
> while ($i < 10)
>   printf "array[%d] = %d\n", $i, array[$i]
>   set $i = $i + 1
> end
> continue
> end
```

### 2. 遍歷鏈表

```gdb
(gdb) commands 10
> set $node = head
> set $count = 0
> while ($node != 0)
>   printf "Node %d: value = %d\n", $count, $node->value
>   set $node = $node->next
>   set $count = $count + 1
>   if ($count > 100)
>     echo Warning: Possible infinite loop!\n
>     loop_break
>   end
> end
> printf "Total nodes: %d\n", $count
> continue
> end
```

### 3. 記憶體掃描

```gdb
(gdb) commands 11
> set $addr = buffer
> set $end = buffer + size
> while ($addr < $end)
>   if (*(char*)$addr == 0)
>     printf "Found null at 0x%x\n", $addr
>     loop_break
>   end
>   set $addr = $addr + 1
> end
> continue
> end
```

## 自定義函數 (define)

### 1. 基本函數定義

```gdb
(gdb) define print_array
Type commands for definition of "print_array".
End with a line saying just "end".
> set $i = 0
> while ($i < $arg1)
>   printf "array[%d] = %d\n", $i, array[$i]
>   set $i = $i + 1
> end
> end

# 使用方式
(gdb) print_array 5
```

### 2. 帶參數的函數

```gdb
(gdb) define examine_pointer
> if ($arg0 != 0)
>   printf "Pointer: 0x%x\n", $arg0
>   printf "Value: %d\n", *$arg0
>   x/4x $arg0
> else
>   echo Null pointer!\n
> end
> end

# 使用方式
(gdb) examine_pointer ptr
```

### 3. 複雜的調試函數

```gdb
(gdb) define debug_struct
> echo === Structure Debug Info ===\n
> print $arg0
> print *$arg0
> printf "Size: %d bytes\n", sizeof(*$arg0)
> if ($arg0->next != 0)
>   echo Has next element\n
>   print $arg0->next
> end
> if ($argc > 1)
>   if ($arg1 == 1)
>     echo Detailed mode\n
>     x/20x $arg0
>   end
> end
> end

# 使用方式
(gdb) debug_struct my_struct
(gdb) debug_struct my_struct 1  # 詳細模式
```

### 4. 遞迴函數

```gdb
(gdb) define print_tree
> if ($arg0 != 0)
>   printf "Node value: %d\n", $arg0->value
>   if ($arg0->left != 0)
>     echo Left: 
>     print_tree $arg0->left
>   end
>   if ($arg0->right != 0)
>     echo Right: 
>     print_tree $arg0->right
>   end
> end
> end
```

## GDB 腳本檔案

### 1. 基本腳本結構

**debug_script.gdb:**
```gdb
# GDB 調試腳本
# 使用方式: gdb -x debug_script.gdb ./program

# 設定環境
set pagination off
set logging file debug.log
set logging on

# 定義輔助函數
define print_status
  echo === Program Status ===\n
  info registers
  info frame
  backtrace 3
end

# 設定斷點
break main
commands
  silent
  echo Program started\n
  continue
end

break error_function
commands
  echo Error detected!\n
  print_status
  print error_code
  continue
end

# 設定 watchpoint
watch global_counter
commands
  silent
  printf "Counter changed to: %d\n", global_counter
  continue
end

# 執行程式
run

# 程式結束後的清理
echo Program finished\n
set logging off
quit
```

### 2. 批次處理腳本

**batch_debug.gdb:**
```gdb
# 批次處理多個核心轉儲檔案
set pagination off
set confirm off

define analyze_core
  echo ========================================\n
  printf "Analyzing: %s\n", $arg0
  echo ========================================\n
  
  core $arg0
  
  echo === Backtrace ===\n
  backtrace
  
  echo === Registers ===\n
  info registers
  
  echo === Local Variables ===\n
  info locals
  
  echo === Memory Map ===\n
  info proc mappings
  
  echo \n\n
end

# 分析多個 core 檔案
analyze_core core.1234
analyze_core core.5678
analyze_core core.9012

quit
```

### 3. 自動化測試腳本

**auto_test.gdb:**
```gdb
# 自動化測試腳本
set pagination off
set breakpoint pending on

# 測試計數器
set $test_passed = 0
set $test_failed = 0

# 定義測試函數
define test_function
  printf "Testing: %s\n", $arg0
  
  # 設定斷點並執行
  tbreak $arg0
  continue
  
  # 檢查結果
  if ($arg1 == $return_value)
    printf "  PASSED: return value = %d\n", $return_value
    set $test_passed = $test_passed + 1
  else
    printf "  FAILED: expected %d, got %d\n", $arg1, $return_value
    set $test_failed = $test_failed + 1
  end
end

# 開始測試
run

# 執行測試案例
test_function add_numbers 30
test_function subtract_numbers 10
test_function multiply_numbers 200

# 顯示測試結果
echo =============================\n
printf "Tests Passed: %d\n", $test_passed
printf "Tests Failed: %d\n", $test_failed
echo =============================\n

quit
```

## 進階應用範例

### 1. 效能分析腳本

```gdb
# 效能分析
define profile_function
  set $start_time = clock()
  finish
  set $end_time = clock()
  printf "Execution time: %f seconds\n", ($end_time - $start_time) / 1000000.0
end

(gdb) break slow_function
(gdb) commands
> profile_function
> continue
> end
```

### 2. 記憶體洩漏偵測

```gdb
# 記憶體配置追蹤
set $malloc_count = 0
set $free_count = 0

break malloc
commands
  silent
  set $malloc_count = $malloc_count + 1
  printf "malloc #%d: size=%d\n", $malloc_count, $rdi
  backtrace 2
  continue
end

break free
commands
  silent
  set $free_count = $free_count + 1
  printf "free #%d: ptr=0x%x\n", $free_count, $rdi
  continue
end

define memory_report
  printf "Allocations: %d\n", $malloc_count
  printf "Deallocations: %d\n", $free_count
  printf "Potential leaks: %d\n", $malloc_count - $free_count
end
```

### 3. 多執行緒調試

```gdb
# 執行緒監控
define thread_info
  echo === Thread Information ===\n
  info threads
  thread apply all backtrace 2
end

define switch_and_examine
  thread $arg0
  echo Current thread:\n
  backtrace
  info locals
end

# 設定執行緒相關斷點
break critical_section
commands
  silent
  printf "Thread %d entered critical section\n", $_thread
  if ($_thread != 1)
    echo Warning: Non-main thread in critical section!\n
    thread_info
  end
  continue
end
```

### 4. 狀態機調試

```gdb
# 狀態機追蹤
set $state_history = {}
set $state_count = 0

define track_state
  set $state_history[$state_count] = current_state
  set $state_count = $state_count + 1
  
  if (current_state == STATE_ERROR)
    echo ERROR STATE REACHED!\n
    print_state_history
    backtrace full
  end
end

define print_state_history
  echo === State History ===\n
  set $i = 0
  while ($i < $state_count)
    printf "Step %d: State %d\n", $i, $state_history[$i]
    set $i = $i + 1
  end
end

break state_machine_update
commands
  silent
  track_state
  continue
end
```

### 5. 自動錯誤恢復

```gdb
# 錯誤處理和恢復
define handle_segfault
  echo Segmentation fault detected!\n
  backtrace
  
  # 嘗試恢復
  if ($pc == dangerous_function)
    echo Skipping dangerous function\n
    finish
    set $rax = 0  # 設定返回值
    continue
  else
    echo Unable to recover\n
  end
end

catch signal SIGSEGV
commands
  handle_segfault
end
```

## 實用技巧和最佳實踐

### 1. 變數使用技巧

```gdb
# GDB 便利變數
(gdb) set $counter = 0
(gdb) commands 12
> set $counter = $counter + 1
> if ($counter % 100 == 0)
>   printf "Hit count: %d\n", $counter
> end
> continue
> end

# 使用暫存器
(gdb) commands 13
> if ($rax == 0)
>   echo Function returned NULL\n
> end
> continue
> end
```

### 2. 輸出格式化

```gdb
# 各種輸出格式
(gdb) commands 14
> # 十六進制
> printf "Hex: 0x%x\n", value
> # 十進制
> printf "Dec: %d\n", value
> # 字串
> printf "String: %s\n", string_ptr
> # 浮點數
> printf "Float: %.2f\n", float_value
> # 字元
> printf "Char: %c\n", char_value
> # 指標
> printf "Pointer: %p\n", ptr
> continue
> end
```

### 3. 條件斷點優化

```gdb
# 使用 commands 代替條件斷點以提高效能
(gdb) break hot_function
(gdb) commands
> silent
> if (counter != target_value)
>   continue
> end
> # 只在條件滿足時執行以下命令
> echo Target reached!\n
> print counter
> backtrace
> end
```

### 4. 錯誤處理

```gdb
# 安全的指標存取
(gdb) commands 15
> if (ptr != 0)
>   if (ptr >= 0x1000 && ptr < 0x7fffffffffff)
>     print *ptr
>   else
>     printf "Invalid pointer: 0x%x\n", ptr
>   end
> else
>   echo Null pointer\n
> end
> continue
> end
```

### 5. 日誌記錄

```gdb
# 完整的日誌系統
define log_init
  set logging file $arg0
  set logging overwrite on
  set logging on
  printf "=== Debug session started at %s ===\n", $_gdb_timestamp
end

define log_message
  printf "[%s] %s\n", $_gdb_timestamp, $arg0
end

define log_close
  printf "=== Debug session ended at %s ===\n", $_gdb_timestamp
  set logging off
end

# 使用方式
(gdb) log_init "debug_session.log"
(gdb) commands 16
> log_message "Breakpoint hit"
> continue
> end
(gdb) log_close
```

## 實用應用場景範例

### 場景 1：記錄型斷點（需要 continue）
用於收集資訊但不想中斷程式執行：

```gdb
# 統計函數呼叫頻率
(gdb) break hot_function
(gdb) commands
> silent
> set $counter = $counter + 1
> if ($counter % 1000 == 0)
>   printf "Called %d times\n", $counter
> end
> continue  # 必須要 continue，否則程式會卡住
> end

# 追蹤記憶體配置
(gdb) break malloc
(gdb) commands
> silent
> printf "malloc: size=%d, caller=%p\n", $rdi, *(void**)$rsp
> continue  # 自動繼續，不中斷程式
> end
```

### 場景 2：調試型斷點（不要 continue）
需要停下來檢查和分析：

```gdb
# 錯誤處理 - 需要手動檢查
(gdb) break error_handler
(gdb) commands
> echo === ERROR DETECTED ===\n
> print error_code
> print error_message
> backtrace
> info locals
> # 故意不加 continue，需要人工介入
> end

# 關鍵函數 - 需要逐步調試
(gdb) break critical_function
(gdb) commands
> echo Entering critical section\n
> print input_param
> info registers
> # 不加 continue，需要單步執行檢查
> end
```

### 場景 3：混合型斷點（選擇性 continue）
根據條件決定是否停止：

```gdb
# 只在異常情況下停止
(gdb) break validate_data
(gdb) commands
> silent
> if (data_valid == 1)
>   # 資料正常，繼續執行
>   continue
> end
> # 資料異常，停下來調試
> printf "Invalid data detected!\n"
> print data_valid
> print data_buffer
> backtrace
> # 異常時不加 continue，需要檢查
> end

# 效能監控 - 只在慢速時停止
(gdb) break function_end
(gdb) commands
> silent
> set $duration = $end_time - $start_time
> printf "Duration: %d ms\n", $duration
> if ($duration < 100)
>   # 效能正常，繼續
>   continue
> end
> # 效能異常，停下來分析
> echo Performance issue detected!\n
> print $duration
> info locals
> # 不加 continue，需要分析原因
> end
```

### 場景 4：自動化測試（都需要 continue）
完全自動化執行：

```gdb
# 自動化回歸測試
(gdb) break test_function
(gdb) commands
> silent
> # 檢查測試結果
> if ($return_value == expected_value)
>   set $test_passed = $test_passed + 1
>   printf "Test PASSED: %s\n", test_name
> else
>   set $test_failed = $test_failed + 1
>   printf "Test FAILED: %s (expected %d, got %d)\n", \
>          test_name, expected_value, $return_value
> end
> continue  # 自動執行下一個測試
> end
```

## 常見問題和解決方案

### Q1: commands 中的變數作用域？

GDB 變數（`$var`）是全域的，可在所有 commands 間共享。C/C++ 變數則依據當前 frame。

### Q2: 如何中斷無限循環？

使用 `loop_break` 指令：
```gdb
while (condition)
  # commands
  if (exit_condition)
    loop_break
  end
end
```

### Q3: 如何在 commands 中呼叫 shell 命令？

```gdb
(gdb) commands 17
> shell date >> debug.log
> shell echo "Breakpoint hit" >> debug.log
> continue
> end
```

### Q4: 如何讓 commands 不輸出訊息？

使用 `silent` 指令：
```gdb
(gdb) commands 18
> silent
> # 你的命令
> continue
> end
```

### Q5: 如何在 commands 中設定新斷點？

```gdb
(gdb) commands 19
> if (error_detected)
>   break error_handler
> end
> continue
> end
```

## Continue 使用決策指南

### 快速判斷規則

| 情況 | 是否加 continue | 原因 |
|-----|----------------|------|
| 記錄日誌 | ✅ 是 | 不應中斷程式執行 |
| 統計計數 | ✅ 是 | 需要持續收集資料 |
| 效能分析 | ✅ 是 | 不能影響程式效能 |
| 錯誤處理 | ❌ 否 | 需要手動檢查和處理 |
| 調試關鍵邏輯 | ❌ 否 | 需要逐步執行 |
| 條件監控 | 🔄 視情況 | 正常時繼續，異常時停止 |
| 自動化測試 | ✅ 是 | 需要自動完成所有測試 |
| 死鎖檢測 | ❌ 否 | 需要立即分析 |

### Continue 的最佳實踐

```gdb
# ✅ 好的做法：高頻斷點使用 continue
(gdb) break malloc
(gdb) commands
> silent
> set $malloc_count = $malloc_count + 1
> continue  # 避免程式卡住
> end

# ❌ 錯誤做法：錯誤處理使用 continue
(gdb) break segfault_handler
(gdb) commands
> print error_info
> continue  # 錯誤！應該停下來調試
> end

# ✅ 好的做法：智能判斷
(gdb) break process_request
(gdb) commands
> silent
> if (status == SUCCESS)
>   continue  # 成功案例自動繼續
> end
> # 失敗案例停下來分析
> print status
> print error_reason
> end
```

## 總結

GDB 的 commands 和腳本功能提供了強大的自動化調試能力：

1. **基本 commands** - 自動執行命令序列
2. **條件和循環** - 實現複雜的邏輯控制
3. **自定義函數** - 創建可重用的調試工具
4. **腳本檔案** - 批次處理和自動化測試
5. **進階應用** - 效能分析、記憶體追蹤、多執行緒調試

透過熟練掌握這些功能，可以大幅提升調試效率，實現自動化測試和問題診斷。記住 `end` 關鍵字是結束命令序列的必要標記。