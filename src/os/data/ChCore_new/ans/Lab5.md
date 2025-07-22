# Lab5

> 思考題 1: 文件的數據塊使用基數樹的形式組織有什麼好處? 除此之外還有其他的數據塊存儲方式嗎?

- 用基數樹的形式組織的好處
  - 減小了inode的大小，inode存儲所佔用的空間更少

- 其他的數據塊存儲方式
  1. Unix V6文件系統：在inode中存儲所有direct block和indirect block的block_id
  2. Ext4：使用了區段樹的方法，保存起始塊地址以及長度



> 練習題 2：實現位於`userland/servers/tmpfs/tmpfs.c`的`tfs_mknod`和`tfs_namex`。

- `tfs_mknod`
  1. 根據`mkdir`的值去判斷創建文件/目錄的inode
  2. 創建對應的dentry
- `tfs_namex`
  1. 用`/`分割name的各個部分
  2. 調用`tfs_lookup`來尋找dentry
  3. 更新相關變量



> 練習題 3：實現位於`userland/servers/tmpfs/tmpfs.c`的`tfs_file_read`和`tfs_file_write`。提示：由於數據塊的大小為PAGE_SIZE，因此讀寫可能會牽涉到多個頁面。讀取不能超過文件大小，而寫入可能會增加文件大小（也可能需要創建新的數據塊）。

- `tfs_file_read`
  1. 首先判斷要讀取的位置`cur_off+size`是否大於inode的size，若是則更新最大讀取size
  2. 在每一個data block中讀取數據
- `tfs_file_write`
  1. 讀取每一個data block中的數據
  2. 若`cur_off - offset`的值大於inode的size，則更新inode的size



> 練習題 4：實現位於`userland/servers/tmpfs/tmpfs.c`的`tfs_load_image`函數。需要通過之前實現的tmpfs函數進行目錄和文件的創建，以及數據的讀寫。

1. 將`dirat`設置為`tmpfs_root`，調用`tfs_namex`來定位文件
2. 調用`tfs_lookup`來獲取對應文件的dentry（若不存在則創建對應文件）
3. 調用`tfs_file_write`將對應的數據寫入文件
4. 重複上述過程



> 練習題 5：利用`userland/servers/tmpfs/tmpfs.c`中已經實現的函數，完成在`userland/servers/tmpfs/tmpfs_ops.c`中的`fs_creat`、`tmpfs_unlink`和`tmpfs_mkdir`函數，從而使`tmpfs_*`函數可以被`fs_server_dispatch`調用以提供系統服務。對應關係可以參照`userland/servers/tmpfs/tmpfs_ops.c`中`server_ops`的設置以及`userland/fs_base/fs_wrapper.c`的`fs_server_dispatch`函數。

- `fs_creat`

  調用`tfs_namex`以及`tfs_creat`

- `tmpfs_unlink`

  調用`tfs_namex`以及`tfs_remove`

- `tmpfs_mkdir`

  調用`tfs_namex`以及`tfs_mkdir`



> 練習題 6：補全`libchcore/src/libc/fs.c`與`libchcore/include/libc/FILE.h`文件，以實現`fopen`, `fwrite`, `fread`, `fclose`, `fscanf`, `fprintf`五個函數，函數用法應與libc中一致。

- `fopen`
  1. 填充`fs_request`和`ipc_msg`
  2. 調用`ipc_call`發送相應`FS_REQ_OPEN`類型的`ipc_msg`
  3. 判斷返回值
     1. 和`fr`的`new_fd`值相同：不做處理
     2. 若`fr`的`new_fd`值不同：
        1. 模式為"w"：發送`FS_REQ_OPEN`類型的`ipc_msg`來創建文件，然後再進行操作2
        2. 否則報錯
  4. 設置FILE，返回
- `fwrite`
  1. 填充`fs_request`和`ipc_msg`
  2. 調用`ipc_call`發送相應`FS_REQ_WRITE`類型的`ipc_msg`
  3. 返回寫入的字節數
- `fread`
  1. 填充`fs_request`和`ipc_msg`
  2. 調用`ipc_call`發送相應`FS_REQ_READ`類型的`ipc_msg`
  3. 返回讀取的字節數
- `fclose`
  1. 填充`fs_request`和`ipc_msg`
  2. 調用`ipc_call`發送相應`FS_REQ_CLOSE`類型的`ipc_msg`
- `fscanf`
  1. 首先調用`fread`來讀取文件中的內容
  2. 分`%s`,`%d`還有其他狀況分別進行處理:
     1. `%s`：以字符串形式讀出
     2. `%d`：以數字類型讀出
     3. 其它：更新cursor位置
- `fprintf`
  1. 分`%s`,`%d`還有其他狀況分別進行處理:
     1. `%s`：以字符串形式寫入
     2. `%d`：以數字類型寫入
     3. 其它：將原本的字符寫入並更新cursor位置
  2. 最後調用`fwrite`寫入文件



> 練習題 7：實現在`userland/servers/shell/main.c`中定義的`getch`，該函數會每次從標準輸入中獲取字符，並實現在`userland/servers/shell/shell.c`中的`readline`，該函數會將按下回車鍵之前的輸入內容存入內存緩衝區。代碼中可以使用在`libchcore/include/libc/stdio.h`中的定義的I/O函數。

- `getch`

  調用`__chcore_sys_getc`

- `readline`

  判斷字符類型：

  1. 若為`\t`，調用`do_complement`進行補全，並打印
  2. 若為`\n`，退出循環停止讀入，返回
  3. 其它情況則正常讀入



> 練習題 8：根據在`userland/servers/shell/shell.c`中實現好的`bultin_cmd`函數，完成shell中內置命令對應的`do_*`函數，需要支持的命令包括：`ls [dir]`、`echo [string]`、`cat [filename]`和`top`。

- `print_file_content`
  1. 調用`fopen`打開對應的文件
  2. 調用`fread`讀取文件內容
  3. 依次打印讀出來的內容
- `fs_scan`
  1. 調用`fopen`打開相應的目錄
  2. 仿照`demo_gendents`的方式進行scan並打印
- `do_echo`
  1. 首先跳過"echo"
  2. 再跳過空白字符
  3. 打印後續內容



> 練習題 9：實現在`userland/servers/shell/shell.c`中定義的`run_cmd`，以通過輸入文件名來運行可執行文件，同時補全`do_complement`函數並修改`readline`函數，以支持按tab鍵自動補全根目錄（`/`）下的文件名。

- `run_cmd`

  調用`chcore_procm_spawn`，傳入`fs_server_cap`

- `do_complement`

  1. 打開根目錄，調用`getdents`讀取根目錄下的dentry
  2. 根據`complement_time`來遍歷，選中相應的文件名



> 練習題 10：FSM需要兩種不同的文件系統才能體現其特點，本實驗提供了一個fakefs用於模擬部分文件系統的接口，測試代碼會默認將tmpfs掛載到路徑`/`，並將fakefs掛載在到路徑`/fakefs`。本練習需要實現`userland/server/fsm/main.c`中空缺的部分，使得用戶程序將文件系統請求發送給FSM後，FSM根據訪問路徑向對應文件系統發起請求，並將結果返回給用戶程序。實現過程中可以使用`userland/server/fsm`目錄下已經實現的函數。

將參數中的`ipc_msg`拷貝至FSM專有的`ipc_msg`中去，再根據`mpinfo`調用`ipc_call`

同時需要進行一定的特殊處理:

1. `FS_REQ_OPEN`需要在獲取fd後調用`fsm_set_mount_info_withfd`進行fd相關設置
2. `FS_REQ_READ`需要在完成`ipc_call`之後將讀取的文件內容拷貝到參數`ipc_msg`中
3. `FS_REQ_GETDENT64`需要在完成`ipc_call`之後將讀取的dentry信息拷貝回參數`ipc_msg`中

