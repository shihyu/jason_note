# basic_trace.gdb - 基本 GDB 追蹤命令
set logging enabled on
set logging file basic_trace.txt
set trace-commands on

# 設置斷點
break main
break calculate
break add
break multiply

# 設定自動命令（每次停在斷點時執行）
commands 1-4
silent
printf "=== Function: "
where 1
info args
info locals
continue
end

# 執行程式
run

# 程式執行完畢後
set logging enabled off
quit