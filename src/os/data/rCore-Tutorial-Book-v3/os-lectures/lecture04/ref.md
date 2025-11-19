### 第四講 存儲管理

 * [v1](https://github.com/LearningOS/os-lectures/blob/61f05814711b7dd6a8bfd0b7b4c3cf48025775ba/lecture04/ref.md)
 * [v2](https://github.com/LearningOS/os-lectures/blob/4578d7e2d1a2c4671e4503a611a11f07e41dbbcd/lecture04/ref.md)
 * V3

#### 1. 計算機體系結構和內存層次概述

4.1 計算機體系結構和內存層次：[幻燈片文件](http://os.cs.tsinghua.edu.cn/oscourse/OS2018spring/lecture05?action=AttachFile&do=get&target=20180424-5-1.pptx)、

#### 2. 內存分配概述

4.2 地址空間和地址生成：[幻燈片文件](http://os.cs.tsinghua.edu.cn/oscourse/OS2018spring/lecture05?action=AttachFile&do=get&target=20180424-5-2.pptx)、
4.3 連續內存分配：[幻燈片文件](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture05?action=AttachFile&do=get&target=5-3.pptx)（只用前兩頁）
5.1 非連續內存分配的需求背景：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture06?action=AttachFile&do=get&target=lecture06-1.pptx)

#### 3. 頁式存儲管理與多級頁表

5.3 頁式存儲管理：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture06?action=AttachFile&do=get&target=lecture06-3.pptx)
5.4 頁表概述：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture06?action=AttachFile&do=get&target=lecture06-4.pptx)
5.5 快表和多級頁表：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture06?action=AttachFile&do=get&target=lecture06-5-6.pptx)

#### 4. 虛擬內存

6.4 虛擬存儲概念：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2019spring/lecture08?action=AttachFile&do=get&target=20190320-os-08-05虛擬存儲管理的概念.pptx)
6.5 虛擬頁式存儲管理：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2018spring/lecture08?action=AttachFile&do=get&target=20180514-os-08-06虛擬頁式存儲.pptx) 

#### 5. 文件系統概述

17.1 文件系統和文件：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture21?action=AttachFile&do=get&target=21-1.pptx)
17.2 文件描述符
17.6 文件分配：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2017spring/lecture21?action=AttachFile&do=get&target=20170508-21-4.pptx) 

#### 6. mem-isolation 操作系統

##### RISC-V頁映射機制

5.6 RISC-V頁映射機制：[PDF講義](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture05?action=AttachFile&do=get&target=slide-05-06.pdf)中SV39的頁表
5.7 使能RISC-V頁表：[PDF講義](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture05?action=AttachFile&do=get&target=slide-05-07.pdf)（這裡的描述可能錯的）

[實現 SV39 多級頁表機制（上）](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/3sv39-implementation-1.html#sv39)：在RV64架構下的虛擬地址與物理地址的訪問屬性（可讀，可寫，可執行等），組成結構（頁號，幀好，偏移量等），訪問的空間範圍等；

##### 邏輯地址和物理地址

[地址格式與組成](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/3sv39-implementation-1.html#id3)：

* 在 64 位架構上虛擬地址長度應該是 64 位
* SV39 分頁模式規定 64 位虛擬地址的 [63:39]這 25 位必須和第 38 位相同
* MMU 取出後 39 位，再嘗試將其轉化為 56 位的物理地址

![sv39-va-pa](/Users/xyong/github/os-lectures/lecture04/figs/sv39-va-pa.png)

[地址類型定義](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/address.rs#L5)：`struct PhysAddr`、`struct VirtAddr`、`struct PhysPageNum`、`struct VirtPageNum`

![address-5](/Users/xyong/github/os-lectures/lecture04/figs/address-5.png)

[地址和頁號的相互轉換](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/address.rs#L88)：

![address-88](/Users/xyong/github/os-lectures/lecture04/figs/address-88.png)

##### 頁表項

![sv39-pte](/Users/xyong/github/os-lectures/lecture04/figs/sv39-pte.png)

[頁表項的數據結構抽象與類型定義](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/3sv39-implementation-1.html#id5)

[PageTableEntry](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L21)

 `PageTableEntry` 的工具[函數](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L45)

![page_table-45](/Users/xyong/github/os-lectures/lecture04/figs/page_table-45.png)

##### 頁表

[多級頁表實現](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/4sv39-implementation-2.html#id5)

`PageTable`[數據結構](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L56)

![page_table-56](/Users/xyong/github/os-lectures/lecture04/figs/page_table-56.png)

[PageTable](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L114)



##### 地址轉換過程

[多級頁表原理](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/3sv39-implementation-1.html#id6)

SV39 地址轉換的全過程

![sv39-full](/Users/xyong/github/os-lectures/lecture04/figs/sv39-full.png)

SV39 中的 R/W/X 組合的含義

![pte-rwx](/Users/xyong/github/os-lectures/lecture04/figs/pte-rwx.png)



##### 地址映射建立和撤消

[建立和拆除虛實地址映射關係](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/4sv39-implementation-2.html#id8)：

* 在多級頁表中找到一個虛擬地址對應的頁表項
* 修改頁表項的內容以建立虛實地址映射關係
* 頁表中間的頁表項可能未創建：手動分配物理頁存放該頁表項

[map](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L114)、[unmap](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/page_table.rs#L120)：

![page_table-114](/Users/xyong/github/os-lectures/lecture04/figs/page_table-114.png)



##### 物理頁管理

[實現 SV39 多級頁表機制（下）](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/4sv39-implementation-2.html#sv39)：物理內存管理、多級頁表、地址轉換；

[物理頁幀管理](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/4sv39-implementation-2.html#id2)：

* 聲明一個 `FrameAllocator` Trait 描述物理頁幀管理器的功能
* 實現一種簡單的棧式物理頁幀管理策略 `StackFrameAllocator` 

[FrameAllocator](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/frame_allocator.rs#L35)

![frame_allocator-L35](/Users/xyong/github/os-lectures/lecture04/figs/frame_allocator-L35.png)

棧式物理頁幀管理策略

* 分配 `alloc` 時，檢查棧 `recycled` 內有沒有之前回收的物理頁號；
  * 如果有的話直接彈出棧頂並返回；
  * 否則，從之前從未分配過的物理頁號區間的左端點 `current`分配。
* 回收 `dealloc` 時，檢查回收頁面的合法性，然後將其壓入 `recycled` 棧中。



##### 地址空間

[邏輯段](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/5kernel-app-spaces.html#id4)：指地址區間中的一段屬性相同的連續虛擬地址區間，以相同方式映射到物理頁幀。

[MapArea](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/memory_set.rs#L193)

![memory_set-L193](/Users/xyong/github/os-lectures/lecture04/figs/memory_set-L193.png)

[地址空間](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/5kernel-app-spaces.html#id5)：包含一個多級頁表 `page_table` 和一個邏輯段 `MapArea` 的向量 `areas` 。

[struct MemorySet](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/memory_set.rs#L38)

![memory_set-L38](/Users/xyong/github/os-lectures/lecture04/figs/memory_set-L38.png)

注：[Resource Acquisition is Initialisation (RAII) Explained](https://www.tomdalling.com/blog/software-design/resource-acquisition-is-initialisation-raii-explained/)

##### 內核地址空間

[內核地址空間](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/5kernel-app-spaces.html#id6)

[內核地址空間高256GiB佈局](https://rcore-os.github.io/rCore-Tutorial-Book-v3/_images/kernel-as-high.png)

![kernel-as-high](/Users/xyong/github/os-lectures/lecture04/figs/kernel-as-high.png)

[內核地址空間低256GiB佈局](https://rcore-os.github.io/rCore-Tutorial-Book-v3/_images/kernel-as-low.png)：四個邏輯段 `.text/.rodata/.data/.bss` 被恆等映射到物理內存；

![kernel-as-low](/Users/xyong/github/os-lectures/lecture04/figs/kernel-as-low.png)





[new_kernel](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/memory_set.rs#L78)

保護頁面 (Guard Page)

##### 用戶地址空間 

[應用地址空間](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/5kernel-app-spaces.html#id7)：藉助地址空間的抽象，可以讓所有應用程序都使用同樣的起始地址；

[應用地址空間的佈局](https://rcore-os.github.io/rCore-Tutorial-Book-v3/_images/app-as-full.png)

![app-as-full](/Users/xyong/github/os-lectures/lecture04/figs/app-as-full.png)

[from_elf](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/memory_set.rs#L126)

##### 內核地址空間初始化

[建立並開啟基於分頁模式的虛擬地址空間](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/6multitasking-based-on-as.html#id1)

* CPU 將跳轉到內核入口點並在 S 特權級上執行，此時並沒有開啟分頁模式；

[內核地址空間初始化](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch4/os/src/mm/mod.rs#L15)

![mod-L15](/Users/xyong/github/os-lectures/lecture04/figs/mod-L15.png)

##### 使能分頁機制

[SV39 分頁模式啟用]()：S特權級的MMU使能；

* 切換 satp CSR 必須是平滑，即切換 satp 的指令及其下一條指令的虛擬地址是相鄰的；
* 內核內存佈局的代碼段在切換之後採用恆等映射，切換前的物理地址直接訪問可視為恆等映射。

##### 用戶態與內核態間的地址空間切換

[跳板的實現](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter4/6multitasking-based-on-as.html#id6)

需求：

1. 使能了分頁機制後，必須用戶態與內核態切換中同時完成地址空間的切換。
2. 通過修改 satp 在應用地址空間和內核地址空間間切換。
3. 應用和內核地址空間在切換地址空間指令附近是平滑的。

實現：

* 內核與用戶進程各有自己的地址空間，共享同一個Trampoline（ `__alltraps` 的代碼）和TrapContext（ `__alltraps` 的數據）；Trampoline可在用戶地址空間和內核態時訪問。
* 當應用 Trap 進入內核時，硬件會設置一些 CSR 並在 S 特權級下跳轉到 `__alltraps` 保存 Trap 上下文。

map_trampoline建立跳板區域的虛實映射關係：

1. 用戶態是不能訪問的；
2. 中斷時，中斷進入時硬件保存現場並不直接訪問這個區域的內存，而是放在寄存器中；
3. 這個區域只在內核態且是用戶地址空間時訪問；
4. 這兩個頁表的設置是一樣的，可以保證它只在內核態可以訪問；
5. 中斷服務例程的地址在鏈接時得到；



#### 7. File-System 操作系統

##### 文件接口

[文件](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter6/1file-descriptor.html#id3)：所有輸入輸出都被視為文件操作(Everything is a file)
統一的 `File`抽象[接口](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch6/os/src/fs/mod.rs#L5)

![mod-L5](/Users/xyong/github/os-lectures/lecture04/figs/mod-L5.png)

用戶緩衝區的抽象 `UserBuffer`：[struct UserBuffer](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch6/os/src/mm/page_table.rs#L199)

![page_table-L199](/Users/xyong/github/os-lectures/lecture04/figs/page_table-L199.png)

##### 標準輸入和輸出文件實現

[標準輸入和標準輸出](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter6/1file-descriptor.html#id3)

標準輸入：[stdin](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch6/os/src/fs/stdio.rs#L10)

![stdio-L10](/Users/xyong/github/os-lectures/lecture04/figs/stdio-L10.png)

標準輸出：[stdout](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch6/os/src/fs/stdio.rs#L33)

![stdio-L33](/Users/xyong/github/os-lectures/lecture04/figs/stdio-L33.png)

##### 文件描述符

[文件描述符與文件描述符表](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter6/1file-descriptor.html#id5) ：進程控制塊中的文件描述符表、進程的標準輸入輸出

![task-L20](/Users/xyong/github/os-lectures/lecture04/figs/task-L20.png)

[進程控制塊中的文件描述符表](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch6/os/src/task/task.rs#L20)：在進程創建時，缺省打開標準輸入和輸出；

##### 文件相關的系統調用

[文件讀寫系統調用](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter6/1file-descriptor.html#id6)：基於文件抽象接口和文件描述符表，可以讓文件讀寫系統調用 `sys_read/write` 變得更加通用；

![fs-L5](/Users/xyong/github/os-lectures/lecture04/figs/fs-L5.png)

