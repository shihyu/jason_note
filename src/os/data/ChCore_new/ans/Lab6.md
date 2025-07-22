# Lab6

> 思考題 1：請自行查閱資料，並閱讀`userland/servers/sd`中的代碼，回答以下問題:
>
> - circle中還提供了SDHost的代碼。SD卡，EMMC和SDHost三者之間的關係是怎麼樣的？
> - 請**詳細**描述Chcore是如何與SD卡進行交互的？即Chcore發出的指令是如何輸送到SD卡上，又是如何得到SD卡的響應的。(提示: IO設備常使用MMIO的方式映射到內存空間當中)
> - 請簡要介紹一下SD卡驅動的初始化流程。
> - 在驅動代碼的初始化當中，設置時鐘頻率的意義是什麼？為什麼需要調用`TimeoutWait`進行等待?

- SD卡、EMMC和SDHost三者之間的關係是怎麼樣的？

  SD卡是存儲介質；EMMC是SD卡內部的管理器，相當於驅動，負責數據的讀取、寫入、擦除等操作；SD Host是主機設備中的控制器，與EMMC交互，負責主機與SD卡之間的數據傳輸和交互

- Chcore是如何與SD卡進行交互的？

  1. Chcore首先初始化SD卡驅動，將SD卡設備映射到內存上，註冊IPC server進程提供服務
  2. Chcore向SD卡存儲服務進程發送IPC指令
  3. SD存儲服務進程在收到指令後判斷屬於read還是write指令，通過mmio對SD卡進行操作
  4. 調用`ipc_return`向Chcore返回結果

- SD卡驅動的初始化流程

  1. 將EMMC設備映射到內存中
  2. 初始化SD卡的配置，打開SD卡的電源
  3. 重置SD卡中的信息

- 在驅動代碼的初始化當中，設置時鐘頻率的意義是什麼？為什麼需要調用`TimeoutWait`進行等待?

  - 設置時鐘頻率的意義是什麼？

    時鐘頻率確定了數據傳輸的速率，通過設置合適的時鐘頻率可以確保主機設備和外部設備（如存儲設備或外設）之間的數據傳輸同步

  - 為什麼需要調用`TimeoutWait`進行等待？

    因為對外部設備寄存器的修改需要較長的時間，調用`TimeoutWait`進行等待可以更好地確定外部設備寄存器按照逾期情況被設置



> 練習 1：完成`userland/servers/sd`中的代碼，實現SD卡驅動。驅動程序需實現為用戶態系統服務，應用程序與驅動通過 IPC 通信。需要實現 `sdcard_readblock` 與 `sdcard_writeblock` 接口，通過 Logical Block Address(LBA) 作為參數訪問 SD 卡的塊。

- `emmc.c`中的代碼：參照circle中對emmc的實現，刪去LED燈以及其它的無關操作

- `sdcard_readblock`與`sdcard_writeblock`：

  根據參數`lba`調用`Seek`函數以設置emmc中的offset參數，然後各自調用`sd_Read`/`sd_Write`



> 練習 2：實現naive_fs。
>
> 你需要在 userland/apps/lab6/naive_fs/file_ops.[ch] 中按下述規範實現接口：
>
> - naive_fs_access，判斷參數文件名對應的文件是否存在，不存在返回-1，存在返回0；
> - naive_fs_creat，創建一個空文件，如果文件已經存在則返回-1，創建成功返回0；
> - naive_fs_unlink，刪除一個已有文件，如果文件不存在則返回-1，刪除成功返回0；
> - naive_fs_pread，根據偏移量和大小讀取文件內容，特殊情況的處理請參考 pread 接口的 Linux Manual Page；
> - naive_fs_pwrite，根據偏移量和大小寫入文件內容，特殊情況的處理請參考 pwrite 接口的 Linux Manual Page。

> 採用經典的Unix inode設計方式，第0塊block存儲bitmap，第1塊block存儲根目錄下的dentry信息，第2-63塊block存儲inode信息，第64塊block之後存儲數據塊信息

- `naive_fs_access`

  1. 調用`sd_bread`讀取根目錄下的dentry信息
  2. 在dentry中匹配，如果有相應name的dentry則返回0，若無則返回-1

  

- `naive_fs_creat`

  1. 調用`naive_fs_access`檢測文件是否已經存在，若是則立即返回-1
  2. 調用`sd_bread`讀取根目錄下的dentry信息以及bitmap信息
  3. 在bitmap中找到一個空的inode，分配給即將創建的文件
  4. 將新的dentry(“filename-inode_num”對)寫入到根目錄下
  5. 調用`sd_bwrite`將相關數據結構的更新寫回sd卡

  

- `naive_fs_unlink`

  1. 調用`naive_fs_access`檢測文件是否存在，若不存在則返回-1
  2. 調用`sd_bread`讀取根目錄下的dentry信息以及bitmap信息
  3. 刪去相應的dentry，清空inode和數據塊，將bitmap中相應的位標為0
  4. 調用`sd_bwrite`將相關數據結構的更新寫回sd卡

  

- `naive_fs_pread`

  1. 調用`naive_fs_access`檢測文件是否存在，若不存在則返回-1
  2. 調用`sd_bread`讀取根目錄下的dentry信息
  3. 在dentry中根據name進行匹配，獲取相應的inode_num
  4. 根據相應的inode_num獲取inode信息，進一步獲取數據塊的信息
  5. 根據offset以及size確定訪問的數據塊，拷貝相關數據到buffer中，並返回

  

- `naive_fs_pwrite`

  1. 調用`naive_fs_access`檢測文件是否存在，若不存在則返回-1
  2. 調用`sd_bread`讀取根目錄下的dentry信息以及bitmap信息
  3. 在dentry中根據name進行匹配，獲取相應的inode_num
  4. 根據相應的inode_num獲取inode信息，進一步獲取數據塊的信息
  5. 根據offset以及size確定訪問的數據塊，如果沒有則分配新的數據塊，更新bitmap
  6. 將數據拷貝到數據塊中
  7. 調用`sd_bwrite`將相關數據結構的更新寫回sd卡，並返回



> 思考題2：查閱資料瞭解 SD 卡是如何進行分區，又是如何識別分區對應的文件系統的？嘗試設計方案為 ChCore 提供多分區的 SD 卡驅動支持，設計其解析與掛載流程。本題的設計部分請在實驗報告中詳細描述，如果有代碼實現，可以編寫對應的測試程序放入倉庫中提交。

- SD卡如何進行分區：

  1. 創建分區表：在SD卡上創建一個分區表，例如MBR，它記錄了每個分區的起始位置、大小和文件系統類型等信息
  2. 分區創建：在分區表中定義一個或多個分區
  3. 格式化：格式化每個分區，創建文件系統的結構和元數據，以準備文件系統，

  

- SD卡如何識別對應的文件系統：

  1. 讀取分區表：讀取SD卡上的分區表，獲取每個分區的信息，包括分區的起始位置和大小
  2. 根據路由識別掛載點：根據相應的路徑在分區表中檢索掛載點，找到相應的分區
  3. 識別文件系統：讀取分區的文件系統元數據，識別分區對應的文件系統類型



- Chcore多分區的SD卡驅動支持
  - 解析流程：
    1. 根據對應的路由進行前綴匹配，找到相應的分區
    2. 讀取相應分區的信息，加載相應數據結構到內存中
    3. 裁剪路由，通過相應的驅動調用相應分區文件系統的操作
  - 掛載流程：
    1. 在分區表中創建分區，分配存儲空間，記錄分區起始位置和大小
    2. 將分區掛載到文件系統樹中的一個掛載點，將路徑信息寫入分區表中
    3. 格式化分區，創建相應文件系統的結構和元數據