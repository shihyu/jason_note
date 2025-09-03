# record_replay.gdb - GDB 記錄/重播功能範例

# 開始程式
start

# 開啟記錄功能
record

# 設置斷點
break calculate
break add
break multiply

# 繼續執行
continue

# 程式結束後的反向執行範例
# 反向執行到上一個斷點
reverse-continue

# 查看執行歷史
info record

# 反向單步執行
reverse-step

# 反向執行下一行
reverse-next

# 再次正向執行
continue

# 停止記錄
record stop

quit