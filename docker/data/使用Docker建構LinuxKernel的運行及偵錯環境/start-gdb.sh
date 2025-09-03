#!/bin/bash

echo 'add-auto-load-safe-path /workspace/linux-5.12.14/scripts/gdb/vmlinux-gdb.py' > /root/.gdbinit # 讓 gdb 能夠順利載入核心的偵錯指令碼，如果在下一節編譯 Linux Kernel 時下載的是另一版本的 Linux Kernel 程式碼，請修改這裡的版本號
cd /workspace/obj/linux/
gdb vmlinux -ex "target remote :1234" # 啟動 gdb 遠端偵錯核心
