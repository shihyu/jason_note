引言
=========================================

本章導讀
-----------------------------------------

.. 
   在第六章中，我們為進程引入了文件的抽象，使得進程能夠通過一個統一的接口來讀寫內核管理的多種不同的 I/O 資源。作為例子，我們實現了匿名管道，並通過它進行了簡單的父子進程間的單向通信，但這些其實不是文件這一抽象概念最初建立時要達到的功能。

文件最早來自於計算機用戶需要把數據持久保存在 **持久存儲設備** 上的需求。由於放在內存中的數據在計算機關機或掉電後就會消失，所以應用程序要把內存中需要保存的數據放到 持久存儲設備的數據塊（比如磁盤的扇區等）中存起來。隨著操作系統功能的增強，在操作系統的管理下，應用程序不用理解持久存儲設備的硬件細節，而只需對 **文件** 這種持久存儲數據的抽象進行讀寫就可以了，由操作系統中的文件系統和存儲設備驅動程序一起來完成繁瑣的持久存儲設備的管理與讀寫。所以本章要完成的操作系統的第一個核心目標是： **讓應用能夠方便地把數據持久保存起來** 。

大家不要被 **持久存儲設備** 這個詞給嚇住了，這就是指計算機遠古時代的卡片、紙帶、磁芯、磁鼓、汞延遲線存儲器等，以及到現在還在用的磁帶、磁盤、硬盤、光盤、閃存、固態硬盤 (SSD, Solid-State Drive)等存儲設備。我們可以把這些設備叫做 **外存** 。在本章之前，我們僅使用一種存儲，就是內存（或稱 RAM），內存是一種易失性存儲。相比內存，外存的讀寫速度較慢，容量較大。但內存掉電後信息會丟失，而外存在掉電之後並不會丟失數據。因此，將需要持久保存的數據從內存寫入到外存，或是從外存讀入到內存是應用的一種重要需求。


.. note::

   文件系統在UNIX操作系統有著特殊的地位，根據史料《UNIX: A History and a Memoir》記載，1969年，Ken Thompson（UNIX的作者）在貝爾實驗室比較閒，寫了PDP-7計算機的磁盤調度算法來提高磁盤的吞吐量。為了測試這個算法，他本來想寫一個批量讀寫數據的測試程序。但寫著寫著，他在某一時刻發現，這個測試程序再擴展一下，就是一個文件，再擴展一下，就是一個操作系統了。他的直覺告訴他，他離實現一個操作系統僅有 **三週之遙** 。一週：寫代碼編輯器；一週：寫彙編器；一週寫shell程序，在寫這些程序的同時，需要添加操作系統的功能（如 exec等系統調用）以支持這些應用。結果三週後，為測試磁盤調度算法性能的UNIX雛形誕生了。


.. chyyuu 可以介紹文件系統 ???

   https://en.wikipedia.org/wiki/Data_storage
   https://en.wikipedia.org/wiki/Computer_data_storage
   https://en.wikipedia.org/wiki/Williams_tube
   https://en.wikipedia.org/wiki/Delay-line_memory
   https://en.wikipedia.org/wiki/Drum_memory
   https://en.wikipedia.org/wiki/Magnetic-core_memory
   https://www.ironmountain.com/resources/general-articles/t/the-history-of-magnetic-tape-and-computing-a-65-year-old-marriage-continues-to-evolve
   https://en.wikipedia.org/wiki/File_system
   https://en.wikipedia.org/wiki/Multics
   https://www.multicians.org/fjcc4.html  R. C. Daley, P. G. Neumann, A General Purpose File System for Secondary Storage (AFIPS, 1965) describes the file system, including the access control and backup mechanisms
   https://www.multicians.org/fjcc3.html V. A. Vyssotsky, F. J. Corbató, R. M. Graham, Structure of the Multics Supervisor (AFIPS 1965) describes the basic internal structure of the Multics kernel.
   http://www.multicians.org/fjcc1.html F. J. Corbató, V. A. Vyssotsky, Introduction and Overview of the Multics System (AFIPS 1965) is a good introduction to the system. 
   http://cs-exhibitions.uni-klu.ac.at/index.php?id=216 Multics、UNIX 和 FS
   https://en.wikipedia.org/wiki/Unix_filesystem
   book UNIX: A History and a Memoir ，  Brian Kernighan， 2019

.. note::

   指明方向的舵手：Multics文件系統

   計算機的第一種存儲方式是圖靈設計的圖靈機中的紙帶。在計算機最早出現的年代，紙質的穿孔卡成為了第一代的數據物理存儲介質。
   隨著各種應用對持久存儲大容量數據的需求，紙帶和穿孔卡很快就被放棄，在計算機發展歷史依次出現了磁帶、磁盤、光盤、閃存等各種各樣的外部存儲器（也稱外存、輔助存儲器、輔存等）。與處理器可直接尋址訪問的主存（也稱內存）相比，處理器不能直接訪問，速度慢1~2個數量級，容量多兩個數量級以上，且便宜。應用軟件訪問這些存儲設備上的數據很繁瑣，效率也低，於是文件系統就登場了。這裡介紹一下順序存儲介質（以磁帶為代表）的文件系統和隨機存儲介質（以磁盤為代表）的文件系統。

   磁帶是一種順序存儲介質，磁帶的歷史早於計算機，它始於 1928 年，當時它被開發用於音頻存儲（就是錄音帶）。在1951 年，磁帶首次用於在UNIVAC I計算機上存儲數據。磁帶的串行順序訪問特徵對通用文件系統的創建和高效管理提出了挑戰，磁帶需要線性運動來纏繞和展開可能很長的介質卷軸。磁帶的這種順序運動可能需要幾秒鐘到幾分鐘才能將讀/寫磁頭從磁帶的一端移動到另一端。磁帶文件系統用於存儲在磁帶上的文件目錄和文件，為提高效率，它通常允許將文件目錄與文件數據分佈在一起，因此不需要耗時且重複的磁帶往返線性運動來寫入新數據。由於磁帶容量很大，保存方便，且很便宜（磁帶的成本比磁盤低一個數量級），所以到現在為止，磁帶文件系統還在被需要存儲大量數據的單位（如數據中心）使用。

   1956 年，IBM發佈了第一款硬盤驅動器，硬盤高速隨機訪問數據的能力使得它成為替代磁帶的合理選擇。在 Multics 之前，大多數操作系統一般提供特殊且複雜的文件系統來存儲信息。這裡的特殊和複雜性主要體現在操作系統對面向不同應用的文件數據格式的直接支持上。與當時的其他文件系統相比，Multics 文件系統不需要支持各種具體的文件數據格式，而是把文件數據看成是一個無格式的字節流，這樣在一定程度上就簡化了文件系統的設計。Multics操作系統的存儲管理主要面向磁盤這種輔助存儲器，文件只是一個字節序列。Multics操作系統第一次引入了層次文件系統的概念，即文件系統中的目錄可以包含其他子目錄，從而在理論和概念上描述了無限大的文件系統，並使得所有用戶能夠訪問私人和共享文件。用戶通過文件名來尋址文件並訪問文件內容，這使得文件系統的基本結構獨立於物理存儲介質。文件系統可以動態加載和卸載，以便於數據存儲備份等操作。可以說，Multics的這些設計理念（提出這些設計理念的論文出現在Multics操作系統完成的四年前）為UNIX和後續操作系統中基於文件的存儲管理指明瞭方向。

   眼中一切皆文件的UNIX文件系統

   而Ken Thompson 在UNIX文件系統的設計和實現方面，採納了Multics文件系統中的很多設計理念。UNIX 文件只是一個字節序列。文件內容的任何結構或組織僅由處理它的程序決定。UNIX文件系統本身並不關心文件的具體內容，這意味著任何程序都可以讀寫任何文件。這樣就避免了操作系統對各種文件內容的解析，極大地簡化了操作系統的設計與實現。同時UNIX提出了“一切皆文件”的設計理念，這使得你幾乎可以想到的各種操作系統組件都可以通過文件系統中的文件來命名。除了文件自身外，設備、管道、甚至網絡、進程、內存空間都可以用文件來表示和訪問。這種命名的一致性簡化了操作系統的概念模型，使操作系統對外的接口組織更簡單、更模塊化。基本的文件訪問操作包括 ``open，read， write， close`` ，表示了訪問一個文件最核心和基礎的操作：打開文件、讀文件內容、寫文件內容和關閉文件。直到今天，原始 UNIX 文件系統中文件訪問操作的語義幾乎沒有變化。


本章我們將實現一個簡單的文件系統 -- easyfs，能夠對 **持久存儲設備** (Persistent Storage) 這種 I/O 資源進行管理。對於應用程序訪問持久存儲設備的需求，內核需要新增兩種文件：常規文件和目錄文件，它們均以文件系統所維護的 **磁盤文件** 形式被組織並保存在持久存儲設備上。這樣，就形成了具有強大UNIX操作系統基本功能的 “霸王龍” [#rex]_ 操作系統。

.. image:: filesystem-general.png
   :align: center
   :scale: 60 %
   :name: File System
   :alt: 文件系統示意圖

.. 
   同時，由於我們進一步完善了對 **文件** 這一抽象概念的實現，我們可以更容易建立 ” **一切皆文件** “ (Everything is a file) 的UNIX的重要設計哲學。所以本章要完成的操作系統的第二個核心目標是： **以文件抽象來統一描述進程間通信，基於I/O重定向和程序運行參數，實現獨立應用之間的靈活組合** 。這需要擴展與應用程序執行相關的 ``exec`` 系統調用，加入對程序運行參數的支持，並進一步改進了對shell程序自身的實現，加入對重定向符號 ``>`` 、 ``<`` 的識別和處理。這樣我們也可以像UNIX中的shell程序一樣，基於文件機制實現靈活的I/O重定位和管道操作，更加靈活地把應用程序組合在一起實現複雜功能。這樣，就形成了具有強大UNIX操作系統基本功能的 “霸王龍” [#rex]_ 操作系統。

實踐體驗
-----------------------------------------

獲取本章代碼：

.. code-block:: console

   $ git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
   $ cd rCore-Tutorial-v3
   $ git checkout ch6

在 qemu 模擬器上運行本章代碼：

.. code-block:: console

   $ cd os
   $ make run  # 編譯後，最終執行如下命令模擬rv64 virt計算機運行：
   ......
   $ qemu-system-riscv64 \
   -machine virt \
   -nographic \
   -bios ../bootloader/rustsbi-qemu.bin \
   -device loader,file=target/riscv64gc-unknown-none-elf/release/os.bin,addr=0x80200000 \
   -drive file=../user/target/riscv64gc-unknown-none-elf/release/fs.img,if=none,format=raw,id=x0 \
        -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0


在執行 ``qemu-system-riscv64`` 的參數中，``../user/target/riscv64gc-unknown-none-elf/release/fs.img`` 是包含應用程序集合的文件系統鏡像，這個鏡像是放在虛擬硬盤塊設備 ``virtio-blk-device`` （在下一章會進一步介紹這種存儲設備）中的。

內核初始化完成之後就會進入shell程序，在這裡我們運行一下本章的測例 ``filetest_simple`` ：

.. code-block::

    >> filetest_simple
    file_test passed!
    Shell: Process 2 exited with code 0
    >> 

它會將 ``Hello, world!`` 輸出到另一個文件 ``filea`` ，並讀取裡面的內容確認輸出正確。我們也可以通過命令行工具 ``cat_filea`` 來更直觀的查看 ``filea`` 中的內容：

.. code-block::

   >> cat_filea
   Hello, world!
   Shell: Process 2 exited with code 0
   >> 

本章代碼樹
-----------------------------------------


霸王龍操作系統 -- FilesystemOS的總體結構如下圖所示：

.. image:: ../../os-lectures/lec9/figs/fsos-fsdisk.png
   :align: center
   :scale: 30 %
   :name: filesystem-os-detail
   :alt: 霸王龍操作系統 - Address Space OS總體結構

通過上圖，大致可以看出霸王龍操作系統 -- FilesystemOS增加了對文件系統的支持，並對應用程序提供了文件訪問相關的系統調用服務。在進程管理上，進一步擴展資源管理的範圍，把打開的文件相關信息放到 `fd table` 數據結構中，納入進程的管轄中，並以此為基礎，提供 sys_open、sys_close、sys_read、sys_write 與訪問文件相關的系統調用服務。在設備管理層面，增加了塊設備驅動 --  `BlockDrv` ，通過訪問塊設備數據來讀寫文件系統與文件的各種數據。文件系統 -- EasyFS 成為 FilesystemOS的核心內核模塊，完成文件與存儲塊之間的數據/地址映射關係，通過塊設備驅動 BlockDrv 進行基於存儲塊的讀寫。其核心數據結構包括： Superblock（表示整個文件系統結構）、inode bitmap（表示存放inode磁盤塊空閒情況的位圖）、data bitmap（表示存放文件數據磁盤塊空閒情況的位圖）、inode blks（存放文件元數據的磁盤塊）和data blks（存放文件數據的磁盤塊）。EasyFS中的塊緩存管理器 ``BlockManager`` 在內存中管理有限個 ``BlockCache`` 磁盤塊緩存，並通過Blk Interface(與塊設備驅動對接的讀寫操作接口）與BlockDrv 塊設備驅動程序進行互操作。 

位於 ``ch6`` 分支上的霸王龍操作系統 - FilesystemOS的源代碼如下所示：

.. code-block::
   :linenos:
   :emphasize-lines: 50

   ./os/src
   Rust        32 Files    2893 Lines
   Assembly     3 Files      88 Lines
   ./easyfs/src
   Rust         7 Files     908 Lines
   ├── bootloader
   │   └── rustsbi-qemu.bin
   ├── Dockerfile
   ├── easy-fs(新增：從內核中獨立出來的一個簡單的文件系統 EasyFileSystem 的實現)
   │   ├── Cargo.toml
   │   └── src
   │       ├── bitmap.rs(位圖抽象)
   │       ├── block_cache.rs(塊緩存層，將塊設備中的部分塊緩存在內存中)
   │       ├── block_dev.rs(聲明塊設備抽象接口 BlockDevice，需要庫的使用者提供其實現)
   │       ├── efs.rs(實現整個 EasyFileSystem 的磁盤佈局)
   │       ├── layout.rs(一些保存在磁盤上的數據結構的內存佈局)
   │       ├── lib.rs
   │       └── vfs.rs(提供虛擬文件系統的核心抽象，即索引節點 Inode)
   ├── easy-fs-fuse(新增：將當前 OS 上的應用可執行文件按照 easy-fs 的格式進行打包)
   │   ├── Cargo.toml
   │   └── src
   │       └── main.rs
   ├── LICENSE
   ├── Makefile
   ├── os
   │   ├── build.rs
   │   ├── Cargo.toml(修改：新增 Qemu 和 K210 兩個平臺的塊設備驅動依賴 crate)
   │   ├── Makefile(修改：新增文件系統的構建流程)
   │   └── src
   │       ├── config.rs(修改：新增訪問塊設備所需的一些 MMIO 配置)
   │       ├── console.rs
   │       ├── drivers(修改：新增 Qemu 和 K210 兩個平臺的塊設備驅動)
   │       │   ├── block
   │       │   │   ├── mod.rs(將不同平臺上的塊設備全局實例化為 BLOCK_DEVICE 提供給其他模塊使用)
   │       │   │   ├── sdcard.rs(K210 平臺上的 microSD 塊設備, Qemu不會用)
   │       │   │   └── virtio_blk.rs(Qemu 平臺的 virtio-blk 塊設備)
   │       │   └── mod.rs
   │       ├── entry.asm
   │       ├── fs(修改：在文件系統中新增常規文件的支持)
   │       │   ├── inode.rs(新增：將 easy-fs 提供的 Inode 抽象封裝為內核看到的 OSInode
   │       │   │            並實現 fs 子模塊的 File Trait)
   │       │   ├── mod.rs
   │       │   ├── pipe.rs
   │       │   └── stdio.rs
   │       ├── lang_items.rs
   │       ├── link_app.S
   │       ├── linker-qemu.ld
   │       ├── loader.rs(移除：應用加載器 loader 子模塊，本章開始從文件系統中加載應用)
   │       ├── main.rs
   │       ├── mm
   │       │   ├── address.rs
   │       │   ├── frame_allocator.rs
   │       │   ├── heap_allocator.rs
   │       │   ├── memory_set.rs(修改：在創建地址空間的時候插入 MMIO 虛擬頁面)
   │       │   ├── mod.rs
   │       │   └── page_table.rs(新增：應用地址空間的緩衝區抽象 UserBuffer 及其迭代器實現)
   │       ├── sbi.rs
   │       ├── syscall
   │       │   ├── fs.rs(修改：新增 sys_open)
   │       │   ├── mod.rs
   │       │   └── process.rs(修改：sys_exec 改為從文件系統中加載 ELF，並支持命令行參數)
   │       ├── task
   │       │   ├── context.rs
   │       │   ├── manager.rs
   │       │   ├── mod.rs(修改初始進程 INITPROC 的初始化)
   │       │   ├── pid.rs
   │       │   ├── processor.rs
   │       │   ├── switch.rs
   │       │   ├── switch.S
   │       │   └── task.rs
   │       ├── timer.rs
   │       └── trap
   │           ├── context.rs
   │           ├── mod.rs
   │           └── trap.S
   ├── README.md
   ├── rust-toolchain
   └── user
      ├── Cargo.lock
      ├── Cargo.toml
      ├── Makefile
      └── src
         ├── bin
         │   ├── cat_filea.rs(新增：顯示文件filea的內容)
         │   ├── cmdline_args.rs(新增)
         │   ├── exit.rs
         │   ├── fantastic_text.rs
         │   ├── filetest_simple.rs(新增：創建文件filea並讀取它的內容 )
         │   ├── forktest2.rs
         │   ├── forktest.rs
         │   ├── forktest_simple.rs
         │   ├── forktree.rs
         │   ├── hello_world.rs
         │   ├── initproc.rs
         │   ├── matrix.rs
         │   ├── pipe_large_test.rs
         │   ├── pipetest.rs
         │   ├── run_pipe_test.rs
         │   ├── sleep.rs
         │   ├── sleep_simple.rs
         │   ├── stack_overflow.rs
         │   ├── user_shell.rs
         │   ├── usertests.rs
         │   └── yield.rs
         ├── console.rs
         ├── lang_items.rs
         ├── lib.rs(修改：支持命令行參數解析)
         ├── linker.ld
         └── syscall.rs(修改：新增 sys_open)


本章代碼導讀
-----------------------------------------------------          

本章涉及的代碼量相對較多，且與進程執行相關的管理還有直接的關係。其實我們是參考經典的UNIX基於索引結構的文件系統，設計了一個簡化的有一級目錄並支持 ``open，read， write， close`` ，即創建/打開/讀寫/關閉文件一系列操作的文件系統。這裡簡要介紹一下在內核中添加文件系統的大致開發過程。

**第一步：是能夠寫出與文件訪問相關的應用**

這裡是參考了Linux的創建/打開/讀寫/關閉文件的系統調用接口，力圖實現一個 :ref:`簡化版的文件系統模型 <fs-simplification>` 。在用戶態我們只需要遵從相關係統調用的接口約定，在用戶庫裡完成對應的封裝即可。這一過程我們在前面的章節中已經重複過多次，同學應當對其比較熟悉。其中最為關鍵的是系統調用可以參考 :ref:`sys_open 語義介紹 <sys-open>` ，此外我們還給出了 :ref:`測例代碼解讀 <filetest-simple>` 。

**第二步：就是要實現 easyfs 文件系統**

由於 Rust 語言的特點，我們可以在用戶態實現 easyfs 文件系統，並在用戶態完成文件系統功能的基本測試並基本驗證其實現正確性之後，就可以放心的將該模塊嵌入到操作系統內核中。當然，有了文件系統的具體實現，還需要對上一章的操作系統內核進行擴展，實現與 easyfs 文件系統對接的接口，這樣才可以讓操作系統擁有一個簡單可用的文件系統。這樣內核就可以支持具有文件讀寫功能的複雜應用。當內核進一步支持應用的命令行參數後，就可以進一步提升應用程序的靈活性，讓應用的開發和調試變得更為輕鬆。

easyfs 文件系統的整體架構自下而上可分為五層：

1. 磁盤塊設備接口層：讀寫磁盤塊設備的trait接口
2. 塊緩存層：位於內存的磁盤塊數據緩存
3. 磁盤數據結構層：表示磁盤文件系統的數據結構
4. 磁盤塊管理器層：實現對磁盤文件系統的管理
5. 索引節點層：實現文件創建/文件打開/文件讀寫等操作

它的最底層就是對塊設備的訪問操作接口。在 ``easy-fs/src/block_dev.rs`` 中，可以看到 ``BlockDevice`` trait ，它代表了一個抽象塊設備的接口，該 trait 僅需求兩個函數 ``read_block`` 和 ``write_block`` ，分別代表將數據從塊設備讀到內存緩衝區中，或者將數據從內存緩衝區寫回到塊設備中，數據需要以塊為單位進行讀寫。easy-fs 庫的使用者（如操作系統內核）需要實現塊設備驅動程序，並實現 ``BlockDevice`` trait 以提供給 easy-fs 庫使用，這樣 easy-fs 庫就與一個具體的執行環境對接起來了。至於為什麼塊設備層位於 easy-fs 的最底層，那是因為文件系統僅僅是在塊設備上存儲的稍微複雜一點的數據。無論對文件系統的操作如何複雜，從塊設備的角度看，這些操作終究可以被分解成若干次基本的塊讀寫操作。

儘管在操作系統的最底層（即塊設備驅動程序）已經有了對塊設備的讀寫能力，但從編程方便/正確性和讀寫性能的角度來看，僅有塊讀寫這麼基礎的底層接口是不足以實現高效的文件系統。比如，某應用將一個塊的內容讀到內存緩衝區，對緩衝區進行修改，並尚未寫回塊設備時，如果另外一個應用再次將該塊的內容讀到另一個緩衝區，而不是使用已有的緩衝區，這將會造成數據不一致問題。此外還有可能增加很多不必要的塊讀寫次數，大幅降低文件系統的性能。因此，通過程序自動而非程序員手動地對塊緩衝區進行統一管理也就很必要了，該機制被我們抽象為 easy-fs 自底向上的第二層，即塊緩存層。在 ``easy-fs/src/block_cache.rs`` 中， ``BlockCache`` 代表一個被我們管理起來的塊緩衝區，它包含塊數據內容以及塊的編號等信息。當它被創建的時候，將觸發一次 ``read_block`` 將數據從塊設備讀到它的緩衝區中。接下來只要它駐留在內存中，便可保證對於同一個塊的所有操作都會直接在它的緩衝區中進行而無需額外的 ``read_block`` 。塊緩存管理器 ``BlockManager`` 在內存中管理有限個 ``BlockCache`` 並實現了類似 FIFO 的緩存替換算法，當一個塊緩存被換出的時候視情況可能調用 ``write_block`` 將緩衝區數據寫回塊設備。總之，塊緩存層對上提供 ``get_block_cache`` 接口來屏蔽掉相關細節，從而可以向上層子模塊提供透明讀寫數據塊的服務。

有了塊緩存，我們就可以在內存中方便地處理easyfs文件系統在磁盤上的各種數據了，這就是第三層文件系統的磁盤數據結構。easyfs文件系統中的所有需要持久保存的數據都會放到磁盤上，這包括了管理這個文件系統的 **超級塊 (Super Block)**，管理空閒磁盤塊的 **索引節點位圖區** 和  **數據塊位圖區** ，以及管理文件的 **索引節點區** 和 放置文件數據的 **數據塊區** 組成。

easyfs文件系統中管理這些磁盤數據的控制邏輯主要集中在 **磁盤塊管理器** 中，這是文件系統的第四層。對於文件系統管理而言，其核心是 ``EasyFileSystem`` 數據結構及其關鍵成員函數：
 
 - EasyFileSystem.create：創建文件系統
 - EasyFileSystem.open：打開文件系統
 - EasyFileSystem.alloc_inode：分配inode （dealloc_inode未實現，所以還不能刪除文件）
 - EasyFileSystem.alloc_data：分配數據塊
 - EasyFileSystem.dealloc_data：回收數據塊

對於單個文件的管理和讀寫的控制邏輯主要是 **索引節點（文件控制塊）** 來完成，這是文件系統的第五層，其核心是 ``Inode`` 數據結構及其關鍵成員函數：

 - Inode.new：在磁盤上的文件系統中創建一個inode
 - Inode.find：根據文件名查找對應的磁盤上的inode
 - Inode.create：在根目錄下創建一個文件
 - Inode.read_at：根據inode找到文件數據所在的磁盤數據塊，並讀到內存中
 - Inode.write_at：根據inode找到文件數據所在的磁盤數據塊，把內存中數據寫入到磁盤數據塊中

上述五層就構成了easyfs文件系統的整個內容。我們可以把easyfs文件系統看成是一個庫，被應用程序調用。而 ``easy-fs-fuse`` 這個應用就通過調用easyfs文件系統庫中各種函數，並作用在用Linux上的文件模擬的一個虛擬塊設備，就可以在這個虛擬塊設備上進行各種文件操作和文件系統操作，從而創建一個easyfs文件系統。

**第三步：把easyfs文件系統加入內核中**

這還需要做兩件事情，第一件是在Qemu模擬的 ``virtio`` 塊設備上實現塊設備驅動程序 ``os/src/drivers/block/virtio_blk.rs`` 。由於我們可以直接使用 ``virtio-drivers`` crate中的塊設備驅動，所以只要提供這個塊設備驅動所需要的內存申請與釋放以及虛實地址轉換的4個函數就可以了。而我們之前操作系統中的虛存管理實現中，已經有這些函數，這使得塊設備驅動程序很簡單，且具體實現細節都被 ``virtio-drivers`` crate封裝好了。當然，我們也可把easfys文件系統燒寫到K210開發板的存儲卡中。

第二件事情是把文件訪問相關的系統調用與easyfs文件系統連接起來。在easfs文件系統中是沒有進程的概念的。而進程是程序運行過程中訪問資源的管理實體，而之前的進程沒有管理文件這種資源。
為此我們需要擴展進程的管理範圍，把文件也納入到進程的管理之中。
由於我們希望多個進程都能訪問文件，這意味著文件有著共享的天然屬性，這樣自然就有了 ``open/close/read/write`` 這樣的系統調用，便於進程通過互斥或共享方式訪問文件。

內核中的進程看到的文件應該是一個便於訪問的Inode，這就要對 ``easy-fs`` crate 提供的 ``Inode`` 結構進一步封裝，形成 ``OSInode`` 結構，以表示進程中一個打開的常規文件。文件的抽象 Trait ``File`` 聲明在 ``os/src/fs/mod.rs`` 中，它提供了 ``read/write`` 兩個接口，可以將數據寫入應用緩衝區抽象 ``UserBuffer`` ，或者從應用緩衝區讀取數據。應用緩衝區抽象類型 ``UserBuffer`` 來自 ``os/src/mm/page_table.rs`` 中，它將 ``translated_byte_buffer`` 得到的 ``Vec<&'static mut [u8]>`` 進一步包裝，不僅保留了原有的分段讀寫能力，還可以將其轉化為一個迭代器逐字節進行讀寫。

而進程為了進一步管理多個文件，需要擴展文件描述符表。這樣進程通過系統調用打開一個文件後，會將文件加入到自身的文件描述符表中，並進一步通過文件描述符（也就是某個特定文件在自身文件描述符表中的下標）來讀寫該文件（ 即 ``OSInode`` 結構）。

在具體實現上，在進程控制塊 ``TaskControlBlock`` 中需要加入文件描述符表字段 ``fd_table`` ，可以看到它是一個向量，裡面保存了若干實現了 ``File`` Trait 的文件，由於採用Rust的 ``Trait Object`` 動態分發，文件的類型可能各不相同。 ``os/src/syscall/fs.rs`` 的 ``sys_read/write`` 兩個讀寫文件的系統調用需要訪問當前進程的文件描述符表，用應用傳入內核的文件描述符來索引對應的已打開文件，並調用 ``File`` Trait 的 ``read/write`` 接口； ``sys_close`` 這可以關閉一個文件。調用 ``TaskControlBlock`` 的 ``alloc_fd`` 方法可以在文件描述符表中分配一個文件描述符。進程控制塊的其他操作也需要考慮到新增的文件描述符表字段的影響，如 ``TaskControlBlock::new`` 的時候需要對 ``fd_table`` 進行初始化， ``TaskControlBlock::fork`` 中則需要將父進程的 ``fd_table`` 複製一份給子進程。

對於應用程序而言，它理解的磁盤數據是常規的文件和目錄，不是 ``OSInode`` 這樣相對複雜的結構。其實常規文件對應的 OSInode 是操作系統內核中的文件控制塊數據結構的實例，它實現了 File Trait 定義的函數接口。這些 OSInode 實例會放入到進程文件描述符表中，並通過 sys_read/write 系統調用來完成讀寫文件的服務。這樣就建立了文件與 ``OSInode`` 的對應關係，通過上面描述的三個開發步驟將形成包含文件系統的操作系統內核，可給應用提供基於文件的系統調用服務。

.. [#rex] 霸王龍是最廣為人知的恐龍，生存於約6850萬年到6500萬年的白堊紀最末期， 位於白堊紀晚期的食物鏈頂端。
