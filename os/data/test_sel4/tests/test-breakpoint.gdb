# 測試中斷點功能
target remote :1234
source ../kernel/gdb-macros

# 設定中斷點
break main
info breakpoints

# 繼續執行，應該在 main 處中斷
continue

# 顯示當前位置
where
list

# 顯示暫存器
info registers rip rsp rbp

echo \n=== 中斷點測試成功 ===\n
echo 已在 main 函數處中斷\n
