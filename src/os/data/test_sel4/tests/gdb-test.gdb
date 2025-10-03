# GDB 測試腳本
target remote :1234
source ../../kernel/gdb-macros

# 設定中斷點
break main
break _start

# 顯示中斷點資訊
info breakpoints

# 測試完成
echo \n=== GDB 測試成功 ===\n
echo 符號表已載入\n
echo 中斷點已設定\n
echo \n執行 'continue' 開始除錯\n
