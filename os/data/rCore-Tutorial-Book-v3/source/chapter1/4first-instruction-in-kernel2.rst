內核第一條指令（實踐篇）
===========================================================================================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
------------------------------------

承接上一節，本節我們將實踐在 Qemu 上執行內核的第一條指令。首先我們編寫內核第一條指令並嵌入到我們的內核項目中，接著指定內核的內存佈局使得我們的內核可以正確對接到 Qemu 中。由於 Qemu 的文件加載功能過於簡單，它不支持完整的可執行文件，因此我們從內核可執行文件中剝離多餘的元數據得到內核鏡像並提供給 Qemu 。最後，我們使用 GDB 來跟蹤 Qemu 的整個啟動流程並驗證內核的第一條指令被正確執行。

提示：在進入本節之前請參考 :doc:`/chapter0/5setup-devel-env` 安裝配置 Rust 相關軟件包、Qemu軟件和 GDB 調試工具等。

編寫內核第一條指令
-------------------------------------

首先，我們需要編寫進入內核後的第一條指令，這樣更方便我們驗證我們的內核鏡像是否正確對接到 Qemu 上。

.. code-block::
   :linenos:

    # os/src/entry.asm
        .section .text.entry
        .globl _start
    _start:
        li x1, 100

實際的指令位於第 5 行，也即 ``li x1, 100`` 。 ``li`` 是 Load Immediate 的縮寫，也即將一個立即數加載到某個寄存器，因此這條指令可以看做將寄存器 ``x1`` 賦值為 ``100`` 。第 4 行我們聲明瞭一個符號 ``_start`` ，該符號指向緊跟在符號後面的內容——也就是位於第 5 行的指令，因此符號 ``_start`` 的地址即為第 5 行的指令所在的地址。第 3 行我們告知編譯器 ``_start`` 是一個全局符號，因此可以被其他目標文件使用。第 2 行表明我們希望將第 2 行後面的內容全部放到一個名為 ``.text.entry`` 的段中。一般情況下，所有的代碼都被放到一個名為 ``.text`` 的代碼段中，這裡我們將其命名為 ``.text.entry`` 從而區別於其他 ``.text`` 的目的在於我們想要確保該段被放置在相比任何其他代碼段更低的地址上。這樣，作為內核的入口點，這段指令才能被最先執行。

接著，我們在 ``main.rs`` 中嵌入這段彙編代碼，這樣 Rust 編譯器才能夠注意到它，不然編譯器會認為它是一個與項目無關的文件：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 8

    // os/src/main.rs
    #![no_std]
    #![no_main]

    mod lang_items;

    use core::arch::global_asm;
    global_asm!(include_str!("entry.asm"));

第 8 行，我們通過 ``include_str!`` 宏將同目錄下的彙編代碼 ``entry.asm`` 轉化為字符串並通過 ``global_asm!`` 宏嵌入到代碼中。

.. chyyuu 可以看到，在經歷了長時間的迭代之後， ``global_asm!`` 宏已被加入到 Rust 核心庫 core 中。

調整內核的內存佈局
-------------------------------------

.. _term-linker-script:

由於鏈接器默認的內存佈局並不能符合我們的要求，為了實現與 Qemu 正確對接，我們可以通過 **鏈接腳本** (Linker Script) 調整鏈接器的行為，使得最終生成的可執行文件的內存佈局符合Qemu的預期，即內核第一條指令的地址應該位於 `0x80200000` 。我們修改 Cargo 的配置文件來使用我們自己的鏈接腳本 ``os/src/linker.ld`` 而非使用默認的內存佈局：

.. code-block::
   :linenos:
   :emphasize-lines: 5,6,7,8

    // os/.cargo/config
    [build]
    target = "riscv64gc-unknown-none-elf"

    [target.riscv64gc-unknown-none-elf]
    rustflags = [
        "-Clink-arg=-Tsrc/linker.ld", "-Cforce-frame-pointers=yes"
    ]

鏈接腳本 ``os/src/linker.ld`` 如下：

.. code-block::
    :linenos:
    :emphasize-lines: 12

    OUTPUT_ARCH(riscv)
    ENTRY(_start)
    BASE_ADDRESS = 0x80200000;

    SECTIONS
    {
        . = BASE_ADDRESS;
        skernel = .;

        stext = .;
        .text : {
            *(.text.entry)
            *(.text .text.*)
        }

        . = ALIGN(4K);
        etext = .;
        srodata = .;
        .rodata : {
            *(.rodata .rodata.*)
            *(.srodata .srodata.*)
        }

        . = ALIGN(4K);
        erodata = .;
        sdata = .;
        .data : {
            *(.data .data.*)
            *(.sdata .sdata.*)
        }

        . = ALIGN(4K);
        edata = .;
        .bss : {
            *(.bss.stack)
            sbss = .;
            *(.bss .bss.*)
            *(.sbss .sbss.*)
        }

        . = ALIGN(4K);
        ebss = .;
        ekernel = .;

        /DISCARD/ : {
            *(.eh_frame)
        }
    }

第 1 行我們設置了目標平臺為 riscv ；第 2 行我們設置了整個程序的入口點為之前定義的全局符號 ``_start``；

第 3 行定義了一個常量 ``BASE_ADDRESS`` 為 ``0x80200000`` ，也就是我們之前提到內核的初始化代碼被放置的地址；

從第 5 行開始體現了鏈接過程中對輸入的目標文件的段的合併。其中 ``.`` 表示當前地址，也就是鏈接器會從它指向的位置開始往下放置從輸入的目標文件中收集來的段。我們可以對 ``.`` 進行賦值來調整接下來的段放在哪裡，也可以創建一些全局符號賦值為 ``.`` 從而記錄這一時刻的位置。我們還能夠看到這樣的格式：

.. code-block::

    .rodata : {
        *(.rodata)
    }

冒號前面表示最終生成的可執行文件的一個段的名字，花括號內按照放置順序描述將所有輸入目標文件的哪些段放在這個段中，每一行格式為 ``<ObjectFile>(SectionName)``，表示目標文件 ``ObjectFile`` 的名為 ``SectionName`` 的段需要被放進去。我們也可以使用通配符來書寫 ``<ObjectFile>`` 和 ``<SectionName>`` 分別表示可能的輸入目標文件和段名。因此，最終的合併結果是，在最終可執行文件中各個常見的段 ``.text, .rodata .data, .bss`` 從低地址到高地址按順序放置，每個段裡面都包括了所有輸入目標文件的同名段，且每個段都有兩個全局符號給出了它的開始和結束地址（比如 ``.text`` 段的開始和結束地址分別是 ``stext`` 和 ``etext`` ）。

第 12 行我們將包含內核第一條指令的 ``.text.entry`` 段放在最終的 ``.text`` 段的最開頭，同時注意到在最終內存佈局中代碼段 ``.text`` 又是先於任何其他段的。因為所有的段都從 ``BASE_ADDRESS`` 也即 ``0x80200000`` 開始放置，這就能夠保證內核的第一條指令正好放在 ``0x80200000`` 從而能夠正確對接到 Qemu 上。

此後我們便可以生成內核可執行文件，切換到 ``os`` 目錄下並進行以下操作：

.. code-block:: console

    $ cargo build --release
    Finished release [optimized] target(s) in 0.10s
    $ file target/riscv64gc-unknown-none-elf/release/os
    target/riscv64gc-unknown-none-elf/release/os: ELF 64-bit LSB executable, UCB RISC-V, version 1 (SYSV), statically linked, not stripped

我們以 ``release`` 模式生成了內核可執行文件，它的位置在 ``os/target/riscv64gc.../release/os`` 。接著我們通過 ``file`` 工具查看它的屬性，可以看到它是一個運行在 64 位 RISC-V 架構計算機上的可執行文件，它是靜態鏈接得到的。

.. note::

    **思考： 0x80200000 可否改為其他地址？**

    首先需要區分絕對地址和相對地址。在對編譯器進行某些設置的情況下，在訪問變量或函數時，可以通過它們所在地址與當前某個寄存器（如 PC）的相對地址而非它們位於的絕對地址來訪問這些變量或函數。比如，在一個起始地址（即上面提到的 ``BASE_ADDRESS`` ）固定為 ``0x80200000`` 的內存佈局中，某個函數入口位於 ``0x80201111`` 處，那麼我們可以使用其絕對地址 ``0x80201111`` 來訪問它。但是，如果一條位於 ``0x80200111`` 指令會調用該函數，那麼這條指令也不一定要用到絕對地址 ``0x80201111`` ，而是用函數入口地址相對於當前指令地址 ``0x80200111`` 的相對地址 ``0x1000`` （計算方式為函數入口地址與當前指令地址之差值）來找到並調用該函數。

    如果一個程序全程都使用相對地址而不依賴任何絕對地址，那麼只要保持好各段之間的相對位置不發生變化，將程序整體加載到內存中的任意位置程序均可正常運行。在這種情況下， ``BASE_ADDRESS`` 可以為任意值，我們可以將程序在內存中隨意平移。這種程序被稱為 **位置無關可執行文件（PIE，Position-independent Executable）** 。相對的，如果程序依賴絕對地址，那麼它一定有一個確定的內存佈局，而且該程序必須被加載到與其內存佈局一致的位置才能正常運行。由於我們的內核並不是位置無關的，所以我們必須將內存佈局的起始地址設置為 ``0x80200000`` ，與之匹配我們也必須將內核加載到這一地址。

.. note::

    **靜態鏈接與動態鏈接**

    靜態鏈接是指程序在編譯時就將所有用到的函數庫的目標文件鏈接到可執行文件中，這樣會導致可執行文件容量較大，佔用硬盤空間；而動態鏈接是指程序在編譯時僅在可執行文件中記錄用到哪些函數庫和在這些函數庫中用到了哪些符號，在操作系統執行該程序準備將可執行文件加載到內存時，操作系統會檢查這些被記錄的信息，將用到的函數庫的代碼和數據和程序一併加載到內存，並進行一些重定位工作，即對裝入內存的目標程序中的指令或數據的內存地址進行修改，確保程序運行時能正確找到相關函數或數據。使用動態鏈接可以顯著縮減可執行文件的容量，並使得程序不必在函數庫更新後重新鏈接依然可用。

    根據以往的經驗， Qemu 模擬的計算機不支持在加載時動態鏈接，因此我們的內核採用靜態鏈接進行編譯。



手動加載內核可執行文件
--------------------------------------------------

上面得到的內核可執行文件完全符合我們對於內存佈局的要求，但是我們不能將其直接提交給 Qemu ，因為它除了實際會被用到的代碼和數據段之外還有一些多餘的元數據，這些元數據無法被 Qemu 在加載文件時利用，且會使代碼和數據段被加載到錯誤的位置。如下圖所示：

.. figure:: load-into-qemu.png
   :align: center

   丟棄元數據前後的內核可執行文件被加載到 Qemu 上的情形

圖中，紅色的區域表示內核可執行文件中的元數據，深藍色的區域表示各個段（包括代碼段和數據段），而淺藍色區域則表示內核被執行的第一條指令，它位於深藍色區域的開頭。圖示的上半部分中，我們直接將內核可執行文件 ``os`` 提交給 Qemu ，而 Qemu 會將整個可執行文件不加處理的加載到 Qemu 內存的 ``0x80200000`` 處，由於內核可執行文件的開頭是一段元數據，這會導致 Qemu 內存 ``0x80200000`` 處無法找到內核第一條指令，也就意味著 RustSBI 無法正常將計算機控制權轉交給內核。相反，圖示的下半部分中，將元數據丟棄得到的內核鏡像 ``os.bin`` 被加載到 Qemu 之後，則可以在 ``0x80200000`` 處正確找到內核第一條指令。如果想要深入瞭解這些元數據的內容，可以參考 :doc:`/appendix-b/index` 。

.. _content-binary-from-elf:

使用如下命令可以丟棄內核可執行文件中的元數據得到內核鏡像：

.. code-block:: console

	$ rust-objcopy --strip-all target/riscv64gc-unknown-none-elf/release/os -O binary target/riscv64gc-unknown-none-elf/release/os.bin

我們可以使用 ``stat`` 工具來比較內核可執行文件和內核鏡像的大小：

.. code-block:: console

	$ stat target/riscv64gc-unknown-none-elf/release/os
	File: target/riscv64gc-unknown-none-elf/release/os
	Size: 1016      	Blocks: 8          IO Block: 4096   regular file
	...
	$ stat target/riscv64gc-unknown-none-elf/release/os.bin
	File: target/riscv64gc-unknown-none-elf/release/os.bin
	Size: 4         	Blocks: 8          IO Block: 4096   regular file
	...

可以看到，內核鏡像的大小僅有 4 字節，這是因為它裡面僅包含我們在 ``entry.asm`` 中編寫的一條指令。一般情況下 RISC-V 架構的一條指令位寬即為 4 字節。而內核可執行文件由於包含了兩部分元數據，其大小達到了 1016 字節。這些元數據能夠幫助我們更加靈活地加載並使用可執行文件，比如在加載時完成一些重定位工作或者動態鏈接。不過由於 Qemu 的加載功能過於簡單，我們只能將這些元數據丟棄再交給 Qemu 。從某種意義上可以理解為我們手動幫助 Qemu 完成了可執行文件的加載。

.. note::

    **新版 Qemu 支持直接加載 ELF**

    經過我們的實驗，至少在 Qemu 7.0.0 版本後，我們可以直接將內核可執行文件 ``os`` 提交給 Qemu 而不必進行任何元數據的裁剪工作，這種情況下我們的內核也能正常運行。其具體做法為：將 Qemu 的參數替換為 ``-device loader,file=path/to/os`` 。但是，我們仍推薦大家瞭解並在代碼框架和文檔中保留這一流程，原因在於這種做法更加通用，對環境和工具的依賴程度更低。

基於 GDB 驗證啟動流程
--------------------------------------------------

在 ``os`` 目錄下通過以下命令啟動 Qemu 並加載 RustSBI 和內核鏡像：

.. code-block:: console
    :linenos:

    $ qemu-system-riscv64 \
        -machine virt \
        -nographic \
        -bios ../bootloader/rustsbi-qemu.bin \
        -device loader,file=target/riscv64gc-unknown-none-elf/release/os.bin,addr=0x80200000 \
        -s -S

``-s`` 可以使 Qemu 監聽本地 TCP 端口 1234 等待 GDB 客戶端連接，而 ``-S`` 可以使 Qemu 在收到 GDB 的請求後再開始運行。因此，Qemu 暫時沒有任何輸出。注意，如果不想通過 GDB 對於 Qemu 進行調試而是直接運行 Qemu 的話，則要刪掉最後一行的 ``-s -S`` 。

打開另一個終端，啟動一個 GDB 客戶端連接到 Qemu ：

.. code-block:: console

    $ riscv64-unknown-elf-gdb \
        -ex 'file target/riscv64gc-unknown-none-elf/release/os' \
        -ex 'set arch riscv:rv64' \
        -ex 'target remote localhost:1234'
    [GDB output]
    0x0000000000001000 in ?? ()

可以看到，正如我們在上一節提到的那樣，Qemu 啟動後 PC 被初始化為 ``0x1000`` 。我們可以檢查一下 Qemu 的啟動固件的內容：

.. code-block:: console

    $ (gdb) x/10i $pc
    => 0x1000:	auipc	t0,0x0
    0x1004:	addi	a1,t0,32 
    0x1008:	csrr	a0,mhartid
    0x100c:	ld	t0,24(t0)
    0x1010:	jr	t0
    0x1014:	unimp
    0x1016:	unimp
    0x1018:	unimp
    0x101a:	0x8000
    0x101c:	unimp

這裡 ``x/10i $pc`` 的含義是從當前 PC 值的位置開始，在內存中反彙編 10 條指令。不過可以看到 Qemu 的固件僅包含 5 條指令，從 ``0x1014`` 開始都是數據，當數據為 0 的時候則會被反彙編為 ``unimp`` 指令。 ``0x101a`` 處的數據 ``0x8000`` 是能夠跳轉到 ``0x80000000`` 進入啟動下一階段的關鍵。有興趣的讀者可以自行探究位於 ``0x1000`` 和 ``0x100c`` 兩條指令的含義。總之，在執行位於 ``0x1010`` 的指令之前，寄存器 ``t0`` 的值恰好為 ``0x80000000`` ，隨後通過 ``jr t0`` 便可以跳轉到該地址。我們可以通過單步調試來複盤這個過程：

.. code-block:: console

    $ (gdb) si
    0x0000000000001004 in ?? ()
    $ (gdb) si
    0x0000000000001008 in ?? ()
    $ (gdb) si
    0x000000000000100c in ?? ()
    $ (gdb) si
    0x0000000000001010 in ?? ()
    $ (gdb) p/x $t0
    $1 = 0x80000000
    $ (gdb) si
    0x0000000080000000 in ?? ()

其中， ``si`` 可以讓 Qemu 每次向下執行一條指令，之後屏幕會打印出待執行的下一條指令的地址。 ``p/x $t0`` 以 16 進制打印寄存器 ``t0`` 的值，注意當我們要打印寄存器的時候需要在寄存器的名字前面加上 ``$`` 。可以看到，當位於 ``0x1010`` 的指令執行完畢後，下一條待執行的指令位於 RustSBI 的入口，也即 ``0x80000000`` ，這意味著我們即將把控制權轉交給 RustSBI 。

.. code-block:: console

    $ (gdb) x/10i $pc
    => 0x80000000:	auipc	sp,0x28
    0x80000004:	mv	sp,sp
    0x80000008:	lui	t0,0x4
    0x8000000a:	addi	t1,a0,1
    0x8000000e:	add	sp,sp,t0
    0x80000010:	addi	t1,t1,-1
    0x80000012:	bnez	t1,0x8000000e
    0x80000016:	j	0x8001125a
    0x8000001a:	unimp
    0x8000001c:	addi	sp,sp,-48
    $ (gdb) si
    0x0000000080000004 in ?? ()
    $ (gdb) si
    0x0000000080000008 in ?? ()
    $ (gdb) si
    0x000000008000000a in ?? ()
    $ (gdb) si
    0x000000008000000e in ?? ()

我們可以用同樣的方式反彙編 RustSBI 最初的幾條指令並單步調試。不過由於 RustSBI 超出了本書的範圍，我們這裡並不打算進行深入。接下來我們檢查控制權能否被移交給我們的內核：

.. code-block:: console

    $ (gdb) b *0x80200000
    Breakpoint 1 at 0x80200000
    $ (gdb) c
    Continuing.

    Breakpoint 1, 0x0000000080200000 in ?? ()

我們在內核的入口點，也即地址 ``0x80200000`` 處打一個斷點。需要注意，當需要在一個特定的地址打斷點時，需要在地址前面加上 ``*`` 。接下來通過 ``c`` 命令（Continue 的縮寫）讓 Qemu 向下運行直到遇到一個斷點。可以看到，我們成功停在了 ``0x80200000`` 處。隨後，可以檢查內核第一條指令是否被正確執行：

.. code-block:: console

    $ (gdb) x/5i $pc
    => 0x80200000:	li	ra,100
    0x80200004:	unimp
    0x80200006:	unimp
    0x80200008:	unimp
    0x8020000a:	unimp
    $ (gdb) si
    0x0000000080200004 in ?? ()
    $ (gdb) p/d $x1
    $2 = 100
    $ (gdb) p/x $sp
    $3 = 0x0

可以看到我們在 ``entry.asm`` 中編寫的第一條指令可以在 ``0x80200000`` 處找到。這裡 ``ra`` 是寄存器 ``x1`` 的別名， ``p/d $x1`` 可以以十進制打印寄存器 ``x1`` 的值，它的結果正確。最後，作為下一節的鋪墊，我們可以檢查此時棧指針 ``sp`` 的值，可以發現它目前是 0 。下一節我們將設置好棧空間，使得內核代碼可以正常進行函數調用，隨後將控制權轉交給 Rust 代碼。
