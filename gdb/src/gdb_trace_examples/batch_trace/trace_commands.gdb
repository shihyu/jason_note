# trace_commands.gdb - 批次執行 GDB 追蹤
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