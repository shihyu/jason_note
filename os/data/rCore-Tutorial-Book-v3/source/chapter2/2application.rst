實現應用程序
===========================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
-------------------------------

本節主要講解如何設計實現被批處理系統逐個加載並運行的應用程序。這有個前提，即應用程序假定在用戶態（U 特權級模式）下運行。實際上，如果應用程序的代碼都符合用戶態特權級的約束，那它完全可以正常在用戶態中運行；但如果應用程序執行特權指令或非法操作（如執行非法指令，訪問一個非法的地址等），那會產生異常，並導致程序退出。保證應用程序的代碼在用戶態能正常運行是將要實現的批處理系統的關鍵任務之一。應用程序的設計實現要點是：

- 應用程序的內存佈局
- 應用程序發出的系統調用

從某種程度上講，這裡設計的應用程序與第一章中的最小用戶態執行環境有很多相同的地方。即設計一個應用程序和基本的支持功能庫，這樣應用程序在用戶態通過操作系統提供的服務完成自身的任務。

應用程序設計
-----------------------------

應用程序、用戶庫（包括入口函數、初始化函數、I/O 函數和系統調用接口等多個 rs 文件組成）放在項目根目錄的 ``user`` 目錄下，它和第一章的裸機應用不同之處主要在項目的目錄文件結構和內存佈局上：

- ``user/src/bin/*.rs`` ：各個應用程序
- ``user/src/*.rs`` ：用戶庫（包括入口函數、初始化函數、I/O 函數和系統調用接口等）
- ``user/src/linker.ld`` ：應用程序的內存佈局說明。

項目結構
^^^^^^^^^^^^^^^^^^^^^^

.. 似乎並不是這樣？

    用戶庫看起來很複雜，它預留了直到 ch7 內核才能實現的系統調用接口，console 模塊還實現了輸出緩存區。它們不是為本章準備的，你只需關注本節提到的部分即可。

我們看到 ``user/src`` 目錄下面多出了一個 ``bin`` 目錄。``bin`` 裡面有多個文件，目前裡面至少有三個程序（一個文件是一個應用程序），分別是：

- ``hello_world`` ：在屏幕上打印一行 ``Hello world from user mode program!``
- ``store_fault`` ：訪問一個非法的物理地址，測試批處理系統是否會被該錯誤影響
- ``power`` ：不斷在計算操作和打印字符串操作之間進行特權級切換

批處理系統會按照文件名開頭的數字編號從小到大的順序加載並運行它們。

每個應用程序的實現都在對應的單個文件中。打開其中一個文件，會看到裡面只有一個 ``main`` 函數和若干相關的函數所形成的整個應用程序邏輯。

我們還能夠看到代碼中嘗試引入了外部庫：

.. code-block:: rust

    #[macro_use]
    extern crate user_lib;

這個外部庫其實就是 ``user`` 目錄下的 ``lib.rs`` 以及它引用的若干子模塊中。至於這個外部庫為何叫 ``user_lib`` 而不叫 ``lib.rs`` 所在的目錄的名字 ``user`` ，是因為在 ``user/Cargo.toml`` 中我們對於庫的名字進行了設置： ``name =  "user_lib"`` 。它作為 ``bin`` 目錄下的源程序所依賴的用戶庫，等價於其他編程語言提供的標準庫。

在 ``lib.rs`` 中我們定義了用戶庫的入口點 ``_start`` ：

.. code-block:: rust
    :linenos:

    #[no_mangle]
    #[link_section = ".text.entry"]
    pub extern "C" fn _start() -> ! {
        clear_bss();
        exit(main());
        panic!("unreachable after sys_exit!");
    }

第 2 行使用 Rust 的宏將 ``_start`` 這段代碼編譯後的彙編代碼中放在一個名為 ``.text.entry`` 的代碼段中，方便我們在後續鏈接的時候調整它的位置使得它能夠作為用戶庫的入口。

從第 4 行開始，進入用戶庫入口之後，首先和第一章一樣，手動清空需要零初始化的 ``.bss`` 段（很遺憾到目前為止底層的批處理系統還沒有這個能力，所以我們只能在用戶庫中完成）；然後調用 ``main`` 函數得到一個類型為 ``i32`` 的返回值，最後調用用戶庫提供的 ``exit`` 接口退出應用程序，並將 ``main`` 函數的返回值告知批處理系統。

我們還在 ``lib.rs`` 中看到了另一個 ``main`` ：

.. code-block:: rust
    :linenos:

    #[linkage = "weak"]
    #[no_mangle]
    fn main() -> i32 {
        panic!("Cannot find main!");
    }

第 1 行，我們使用 Rust 的宏將其函數符號 ``main`` 標誌為弱鏈接。這樣在最後鏈接的時候，雖然在 ``lib.rs`` 和 ``bin`` 目錄下的某個應用程序都有 ``main`` 符號，但由於 ``lib.rs`` 中的 ``main`` 符號是弱鏈接，鏈接器會使用 ``bin`` 目錄下的應用主邏輯作為 ``main`` 。這裡我們主要是進行某種程度上的保護，如果在 ``bin`` 目錄下找不到任何 ``main`` ，那麼編譯也能夠通過，但會在運行時報錯。

為了支持上述這些鏈接操作，我們需要在 ``lib.rs`` 的開頭加入：

.. code-block:: rust

    #![feature(linkage)]


.. _term-app-mem-layout:

內存佈局
^^^^^^^^^^^^^^^^^^^^^^

在 ``user/.cargo/config`` 中，我們和第一章一樣設置鏈接時使用鏈接腳本 ``user/src/linker.ld`` 。在其中我們做的重要的事情是：

- 將程序的起始物理地址調整為 ``0x80400000`` ，三個應用程序都會被加載到這個物理地址上運行；
- 將 ``_start`` 所在的 ``.text.entry`` 放在整個程序的開頭，也就是說批處理系統只要在加載之後跳轉到 ``0x80400000`` 就已經進入了
  用戶庫的入口點，並會在初始化之後跳轉到應用程序主邏輯；
- 提供了最終生成可執行文件的 ``.bss`` 段的起始和終止地址，方便 ``clear_bss`` 函數使用。

其餘的部分和第一章基本相同。

.. _term-call-syscall:

系統調用
^^^^^^^^^^^^^^^^^^^^^^

在子模塊 ``syscall`` 中，應用程序通過 ``ecall`` 調用批處理系統提供的接口，由於應用程序運行在用戶態（即 U 模式）， ``ecall`` 指令會觸發 名為 *Environment call from U-mode* 的異常，並 Trap 進入 S 模式執行批處理系統針對這個異常特別提供的服務代碼。由於這個接口處於 S 模式的批處理系統和 U 模式的應用程序之間，從上一節我們可以知道，這個接口可以被稱為 ABI 或者系統調用。現在我們不關心底層的批處理系統如何提供應用程序所需的功能，只是站在應用程序的角度去使用即可。

在本章中，應用程序和批處理系統之間按照 API 的結構，約定如下兩個系統調用：

.. code-block:: rust
    :caption: 第二章新增系統調用

    /// 功能：將內存中緩衝區中的數據寫入文件。
    /// 參數：`fd` 表示待寫入文件的文件描述符；
    ///      `buf` 表示內存中緩衝區的起始地址；
    ///      `len` 表示內存中緩衝區的長度。
    /// 返回值：返回成功寫入的長度。
    /// syscall ID：64               
    fn sys_write(fd: usize, buf: *const u8, len: usize) -> isize;

    /// 功能：退出應用程序並將返回值告知批處理系統。
    /// 參數：`exit_code` 表示應用程序的返回值。
    /// 返回值：該系統調用不應該返回。
    /// syscall ID：93
    fn sys_exit(exit_code: usize) -> !;

我們知道系統調用實際上是彙編指令級的二進制接口，因此這裡給出的只是使用 Rust 語言描述的 API 版本。在實際調用的時候，我們需要按照 RISC-V 調用規範（即ABI格式）在合適的寄存器中放置系統調用的參數，然後執行 ``ecall`` 指令觸發 Trap。在 Trap 回到 U 模式的應用程序代碼之後，會從 ``ecall`` 的下一條指令繼續執行，同時我們能夠按照調用規範在合適的寄存器中讀取返回值。

.. note::

   **RISC-V 寄存器編號和別名**

   RISC-V 寄存器編號從 ``0~31`` ，表示為 ``x0~x31`` 。 其中：

   -  ``x10~x17`` : 對應  ``a0~a7`` 
   -  ``x1`` ：對應 ``ra`` 

在 RISC-V 調用規範中，和函數調用的 ABI 情形類似，約定寄存器 ``a0~a6`` 保存系統調用的參數， ``a0`` 保存系統調用的返回值。有些許不同的是寄存器 ``a7`` 用來傳遞 syscall ID，這是因為所有的 syscall 都是通過 ``ecall`` 指令觸發的，除了各輸入參數之外我們還額外需要一個寄存器來保存要請求哪個系統調用。由於這超出了 Rust 語言的表達能力，我們需要在代碼中使用內嵌彙編來完成參數/返回值綁定和 ``ecall`` 指令的插入：

.. code-block:: rust
    :linenos:

    // user/src/syscall.rs
    use core::arch::asm;
    fn syscall(id: usize, args: [usize; 3]) -> isize {
        let mut ret: isize;
        unsafe {
            asm!(
                "ecall",
                inlateout("x10") args[0] => ret,
                in("x11") args[1],
                in("x12") args[2],
                in("x17") id
            );
        }
        ret
    }

第 3 行，我們將所有的系統調用都封裝成 ``syscall`` 函數，可以看到它支持傳入 syscall ID 和 3 個參數。

``syscall`` 中使用從第 5 行開始的 ``asm!`` 宏嵌入 ``ecall`` 指令來觸發系統調用。在第一章中，我們曾經使用 ``global_asm!`` 宏來嵌入全局彙編代碼，而這裡的 ``asm!`` 宏可以將彙編代碼嵌入到局部的函數上下文中。相比 ``global_asm!`` ， ``asm!`` 宏可以獲取上下文中的變量信息並允許嵌入的彙編代碼對這些變量進行操作。由於編譯器的能力不足以判定插入彙編代碼這個行為的安全性，所以我們需要將其包裹在 unsafe 塊中自己來對它負責。

從 RISC-V 調用規範來看，就像函數有著輸入參數和返回值一樣， ``ecall`` 指令同樣有著輸入和輸出寄存器： ``a0~a2`` 和 ``a7`` 作為輸入寄存器分別表示系統調用參數和系統調用 ID ，而當系統調用返回後， ``a0`` 作為輸出寄存器保存系統調用的返回值。在函數上下文中，輸入參數數組 ``args`` 和變量 ``id`` 保存系統調用參數和系統調用 ID ，而變量 ``ret`` 保存系統調用返回值，它也是函數 ``syscall`` 的輸出/返回值。這些輸入/輸出變量可以和 ``ecall`` 指令的輸入/輸出寄存器一一對應。如果完全由我們自己編寫彙編代碼，那麼如何將變量綁定到寄存器則成了一個難題：比如，在 ``ecall`` 指令被執行之前，我們需要將寄存器 ``a7`` 的值設置為變量 ``id`` 的值，那麼我們首先需要知道目前變量 ``id`` 的值保存在哪裡，它可能在棧上也有可能在某個寄存器中。

作為程序員我們並不知道這些只有編譯器才知道的信息，因此我們只能在編譯器的幫助下完成變量到寄存器的綁定。現在來看 ``asm!`` 宏的格式：首先在第 6 行是我們要插入的彙編代碼段本身，這裡我們只插入一行 ``ecall`` 指令，不過它可以支持同時插入多條指令。從第 7 行開始我們在編譯器的幫助下將輸入/輸出變量綁定到寄存器。比如第 8 行的 ``in("x11") args[1]`` 則表示將輸入參數 ``args[1]`` 綁定到 ``ecall`` 的輸入寄存器 ``x11`` 即 ``a1`` 中，編譯器自動插入相關指令並保證在 ``ecall`` 指令被執行之前寄存器 ``a1`` 的值與 ``args[1]`` 相同。以同樣的方式我們可以將輸入參數 ``args[2]`` 和 ``id`` 分別綁定到輸入寄存器 ``a2`` 和 ``a7`` 中。這裡比較特殊的是 ``a0`` 寄存器，它同時作為輸入和輸出，因此我們將 ``in`` 改成 ``inlateout`` ，並在行末的變量部分使用 ``{in_var} => {out_var}`` 的格式，其中 ``{in_var}`` 和 ``{out_var}`` 分別表示上下文中的輸入變量和輸出變量。

有些時候不必將變量綁定到固定的寄存器，此時 ``asm!`` 宏可以自動完成寄存器分配。某些彙編代碼段還會帶來一些編譯器無法預知的副作用，這種情況下需要在 ``asm!`` 中通過 ``options`` 告知編譯器這些可能的副作用，這樣可以幫助編譯器在避免出錯更加高效分配寄存器。事實上， ``asm!`` 宏遠比我們這裡介紹的更加強大易用，詳情參考 Rust 相關 RFC 文檔 [#rust-asm-macro-rfc]_ 。

上面這一段彙編代碼的含義和內容與 :ref:`第一章中的 RustSBI 輸出到屏幕的 SBI 調用匯編代碼 <term-llvm-sbicall>` 涉及的彙編指令一樣，但傳遞參數的寄存器的含義是不同的。有興趣的同學可以回顧第一章的 ``console.rs`` 和 ``sbi.rs`` 。

於是 ``sys_write`` 和 ``sys_exit`` 只需將 ``syscall`` 進行包裝：

.. code-block:: rust
    :linenos:

    // user/src/syscall.rs

    const SYSCALL_WRITE: usize = 64;
    const SYSCALL_EXIT: usize = 93;

    pub fn sys_write(fd: usize, buffer: &[u8]) -> isize {
        syscall(SYSCALL_WRITE, [fd, buffer.as_ptr() as usize, buffer.len()])
    }

    pub fn sys_exit(xstate: i32) -> isize {
        syscall(SYSCALL_EXIT, [xstate as usize, 0, 0])
    }

.. _term-fat-pointer:

注意 ``sys_write`` 使用一個 ``&[u8]`` 切片類型來描述緩衝區，這是一個 **胖指針** (Fat Pointer)，裡面既包含緩衝區的起始地址，還
包含緩衝區的長度。我們可以分別通過 ``as_ptr`` 和 ``len`` 方法取出它們並獨立地作為實際的系統調用參數。

我們將上述兩個系統調用在用戶庫 ``user_lib`` 中進一步封裝，從而更加接近在 Linux 等平臺的實際系統調用接口：

.. code-block:: rust
    :linenos:

    // user/src/lib.rs
    use syscall::*;

    pub fn write(fd: usize, buf: &[u8]) -> isize { sys_write(fd, buf) }
    pub fn exit(exit_code: i32) -> isize { sys_exit(exit_code) }

我們把 ``console`` 子模塊中 ``Stdout::write_str`` 改成基於 ``write`` 的實現，且傳入的 ``fd`` 參數設置為 1，它代表標準輸出，
也就是輸出到屏幕。目前我們不需要考慮其他的 ``fd`` 選取情況。這樣，應用程序的 ``println!`` 宏藉助系統調用變得可用了。
參考下面的代碼片段：

.. code-block:: rust
    :linenos:

    // user/src/console.rs
    const STDOUT: usize = 1;

    impl Write for Stdout {
        fn write_str(&mut self, s: &str) -> fmt::Result {
            write(STDOUT, s.as_bytes());
            Ok(())
        }
    }

``exit`` 接口則在用戶庫中的 ``_start`` 內使用，當應用程序主邏輯 ``main`` 返回之後，使用它退出應用程序並將返回值告知
底層的批處理系統。



編譯生成應用程序二進制碼
-------------------------------

這裡簡要介紹一下應用程序的自動構建。只需要在 ``user`` 目錄下 ``make build`` 即可：

1. 對於 ``src/bin`` 下的每個應用程序，在 ``target/riscv64gc-unknown-none-elf/release`` 目錄下生成一個同名的 ELF 可執行文件；
2. 使用 objcopy 二進制工具將上一步中生成的 ELF 文件刪除所有 ELF header 和符號得到 ``.bin`` 後綴的純二進制鏡像文件。它們將被鏈接進內核並由內核在合適的時機加載到內存。

實現操作系統前執行應用程序
----------------------------------- 

我們還沒有實現操作系統，能提前執行或測試應用程序嗎？可以！這是因為我們除了一個能模擬一臺 RISC-V 64 計算機的全系統模擬器 ``qemu-system-riscv64`` 外，還有一個直接支持運行 RISC-V 64 用戶程序的半系統模擬器 ``qemu-riscv64`` 。不過需要注意的是，如果想讓用戶態應用程序在 ``qemu-riscv64`` 模擬器（實際上是一個 RISC-V 架構下的 Linux 操作系統）上和在我們自己寫的 OS 上執行效果一樣，需要做到二者的系統調用的接口是一樣的（包括系統調用編號，參數約定的具體的寄存器和棧等）。

.. note::

    **Qemu 的用戶態模擬和系統級模擬**

    Qemu 有兩種運行模式：用戶態模擬（User mode）和系統級模擬（System mode）。在 RISC-V 架構中，用戶態模擬可使用 ``qemu-riscv64`` 模擬器，它可以模擬一臺預裝了 Linux 操作系統的 RISC-V 計算機。但是一般情況下我們並不通過輸入命令來與之交互（就像我們正常使用 Linux 操作系統一樣），它僅支持載入並執行單個可執行文件。具體來說，它可以解析基於 RISC-V 的應用級 ELF 可執行文件，加載到內存並跳轉到入口點開始執行。在翻譯並執行指令時，如果碰到是系統調用相關的彙編指令，它會把不同處理器（如 RISC-V）的 Linux 系統調用轉換為本機處理器（如 x86-64）上的 Linux 系統調用，這樣就可以讓本機 Linux 完成系統調用，並返回結果（再轉換成 RISC-V 能識別的數據）給這些應用。相對的，我們使用 ``qemu-system-riscv64`` 模擬器來系統級模擬一臺 RISC-V 64 裸機，它包含處理器、內存及其他外部設備，支持運行完整的操作系統。

.. _term-csr-instr-app:

假定我們已經完成了編譯並生成了 ELF 可執行文件格式的應用程序，我們就可以來試試。首先看看應用程序執行 :ref:`RV64 的 S 模式特權指令 <term-csr-instr>` 會出現什麼情況，對應的應用程序可以在 ``user/src/bin`` 目錄下找到。

.. code-block:: rust

    // user/src/bin/03priv_inst.rs
    use core::arch::asm;
    #[no_mangle]
    fn main() -> i32 {
        println!("Try to execute privileged instruction in U Mode");
        println!("Kernel should kill this application!");
        unsafe {
            asm!("sret");
        }
        0
    }

    // user/src/bin/04priv_csr.rs
    use riscv::register::sstatus::{self, SPP};
    #[no_mangle]
    fn main() -> i32 {
        println!("Try to access privileged CSR in U Mode");
        println!("Kernel should kill this application!");
        unsafe {
            sstatus::set_spp(SPP::User);
        }
        0
    }

在上述代碼中，兩個應用都會打印提示信息，隨後應用 ``03priv_inst`` 會嘗試在用戶態執行內核態的特權指令 ``sret`` ，而應用 ``04priv_csr`` 則會試圖在用戶態修改內核態 CSR ``sstatus`` 。

接下來，我們嘗試在用戶態模擬器 ``qemu-riscv64`` 執行這兩個應用：

.. code-block:: console

    $ cd user
    $ make build
    $ cd target/riscv64gc-unknown-none-elf/release/
    # 確認待執行的應用為 ELF 格式
    $ file 03priv_inst
    03priv_inst: ELF 64-bit LSB executable, UCB RISC-V, version 1 (SYSV), statically linked, not stripped
    # 執行特權指令出錯
    $ qemu-riscv64 ./03priv_inst
    Try to execute privileged instruction in U Mode
    Kernel should kill this application!
    Illegal instruction (core dumped)
    # 執行訪問特權級 CSR 的指令出錯
    $ qemu-riscv64 ./04priv_csr
    Try to access privileged CSR in U Mode
    Kernel should kill this application!
    Illegal instruction (core dumped)

看來RV64的特權級機制確實有用。那對於一般的用戶態應用程序，在 ``qemu-riscv64`` 模擬器下能正確執行嗎？

.. code-block:: console

    $ cd user/target/riscv64gc-unknown-none-elf/release/
    $ qemu-riscv64 ./00hello_world
    Hello, world!
    # 正確顯示了字符串   
    $ qemu-riscv64 ./01store_fault
    Into Test store_fault, we will insert an invalid store operation...
    Kernel should kill this application!
    Segmentation fault (core dumped)
    # 故意訪問了一個非法地址，導致應用和 qemu-riscv64 被 Linux 內核殺死
    $ qemu-riscv64 ./02power
    3^10000=Segmentation fault (core dumped)
    # 由於 Qemu 和 Rust 編譯器版本不匹配，無法正常運行

可以看到，除了 ``02power`` 之外，其餘兩個應用程序都能夠執行並順利結束。這是由於它們在運行時得到了操作系統 Linux for RISC-V 64 的支持。而 ``02power`` 的例子也說明我們應用的兼容性比較受限，當應用用到較多特性時很可能就不再兼容 Qemu 了。我們期望在下一節開始實現的泥盆紀“鄧式魚”操作系統也能夠正確加載和執行這些應用程序。

.. [#rust-asm-macro-rfc] https://doc.rust-lang.org/reference/inline-assembly.html
