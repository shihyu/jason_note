練習參考答案
=====================================================

.. toctree::
   :hidden:
   :maxdepth: 4


課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. `*` 實現一個linux應用程序A，顯示當前目錄下的文件名。（用C或Rust編程）

   參考實現：

   .. code-block:: c

      #include <dirent.h>
      #include <stdio.h>

      int main() {
          DIR *dir = opendir(".");

          struct dirent *entry;

          while ((entry = readdir(dir))) {
              printf("%s\n", entry->d_name);
          }

          return 0;
      }

   可能的輸出：

   .. code-block:: console

      $ ./ls
      .
      ..
      .git
      .dockerignore
      Dockerfile
      LICENSE
      Makefile
      [...]


2. `***` 實現一個linux應用程序B，能打印出調用棧鏈信息。（用C或Rust編程）

    以使用 GCC 編譯的 C 語言程序為例，使用編譯參數 ``-fno-omit-frame-pointer`` 的情況下，會保存棧幀指針 ``fp`` 。

    ``fp`` 指向的棧位置的負偏移量處保存了兩個值：

    * ``-8(fp)`` 是保存的 ``ra``
    * ``-16(fp)`` 是保存的上一個 ``fp``

    .. TODO：這個規範在哪裡？

    因此我們可以像鏈表一樣，從當前的 ``fp`` 寄存器的值開始，每次找到上一個 ``fp`` ，逐幀恢復我們的調用棧：

    .. code-block:: c

       #include <inttypes.h>
       #include <stdint.h>
       #include <stdio.h>

       // Compile with -fno-omit-frame-pointer
       void print_stack_trace_fp_chain() {
           printf("=== Stack trace from fp chain ===\n");

           uintptr_t *fp;
           asm("mv %0, fp" : "=r"(fp) : : );

           // When should this stop?
           while (fp) {
               printf("Return address: 0x%016" PRIxPTR "\n", fp[-1]);
               printf("Old stack pointer: 0x%016" PRIxPTR "\n", fp[-2]);
               printf("\n");

               fp = (uintptr_t *) fp[-2];
           }
           printf("=== End ===\n\n");
       }

    但是這裡會遇到一個問題，因為我們的標準庫並沒有保存棧幀指針，所以找到調用棧到標準的庫時候會打破我們對棧幀格式的假設，出現異常。

    我們也可以不做關於棧幀保存方式的假設，而是明確讓編譯器告訴我們每個指令處的調用棧如何恢復。在編譯的時候加入 ``-funwind-tables`` 會開啟這個功能，將調用棧恢復的信息存入可執行文件中。

    有一個叫做 `libunwind <https://www.nongnu.org/libunwind>`_ 的庫可以幫我們讀取這些信息生成調用棧信息，而且它可以正確發現某些棧幀不知道怎麼恢復，避免異常退出。

    正確安裝 libunwind 之後，我們也可以用這樣的方式生成調用棧信息：

    .. code-block:: c

       #include <inttypes.h>
       #include <stdint.h>
       #include <stdio.h>

       #define UNW_LOCAL_ONLY
       #include <libunwind.h>

       // Compile with -funwind-tables -lunwind
       void print_stack_trace_libunwind() {
           printf("=== Stack trace from libunwind ===\n");

           unw_cursor_t cursor; unw_context_t uc;
           unw_word_t pc, sp;

           unw_getcontext(&uc);
           unw_init_local(&cursor, &uc);

           while (unw_step(&cursor) > 0) {
               unw_get_reg(&cursor, UNW_REG_IP, &pc);
               unw_get_reg(&cursor, UNW_REG_SP, &sp);

               printf("Program counter: 0x%016" PRIxPTR "\n", (uintptr_t) pc);
               printf("Stack pointer: 0x%016" PRIxPTR "\n", (uintptr_t) sp);
               printf("\n");
           }
           printf("=== End ===\n\n");
       }


3. `**` 實現一個基於rcore/ucore tutorial的應用程序C，用sleep系統調用睡眠5秒（in rcore/ucore tutorial v3: Branch ch1）

注： 嘗試用GDB等調試工具和輸出字符串的等方式來調試上述程序，能設置斷點，單步執行和顯示變量，理解彙編代碼和源程序之間的對應關係。


問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 應用程序在執行過程中，會佔用哪些計算機資源？

    佔用 CPU 計算資源（CPU 流水線，緩存等），內存（內存不夠還會佔用外存）等

2. `*` 請用相關工具軟件分析並給出應用程序A的代碼段/數據段/堆/棧的地址空間範圍。

    簡便起見，我們靜態編譯該程序生成可執行文件。使用 ``readelf`` 工具查看地址空間：

    .. 
        Section Headers:
        [Nr] Name              Type             Address           Offset
            Size              EntSize          Flags  Link  Info  Align
        ...
        [ 7] .text             PROGBITS         00000000004011c0  000011c0
            0000000000095018  0000000000000000  AX       0     0     64
        ... 
        [10] .rodata           PROGBITS         0000000000498000  00098000
            000000000001cadc  0000000000000000   A       0     0     32
        ...    
        [21] .data             PROGBITS         00000000004c50e0  000c40e0
            00000000000019e8  0000000000000000  WA       0     0     32
        ...    
        [25] .bss              NOBITS           00000000004c72a0  000c6290
            0000000000005980  0000000000000000  WA       0     0     32

    數據段（.data）和代碼段（.text）的起止地址可以從輸出信息中看出。

    應用程序的堆棧是由內核為其動態分配的，需要在運行時查看。將 A 程序置於後臺執行，通過查看 ``/proc/[pid]/maps`` 得到堆棧空間的分佈：

    .. 
        01bc9000-01beb000 rw-p 00000000 00:00 0                                  [heap]
        7ffff8e60000-7ffff8e82000 rw-p 00000000 00:00 0                          [stack]
        
3. `*` 請簡要說明應用程序與操作系統的異同之處。

    這個問題相信大家完成了實驗的學習後一定會有更深的理解。

4. `**` 請基於QEMU模擬RISC—V的執行過程和QEMU源代碼，說明RISC-V硬件加電後的幾條指令在哪裡？完成了哪些功能？

   在 QEMU 源碼 [#qemu_bootrom]_ 中可以找到“上電”的時候剛執行的幾條指令，如下：

   .. code-block:: c

      uint32_t reset_vec[10] = {
          0x00000297,                   /* 1:  auipc  t0, %pcrel_hi(fw_dyn) */
          0x02828613,                   /*     addi   a2, t0, %pcrel_lo(1b) */
          0xf1402573,                   /*     csrr   a0, mhartid  */
      #if defined(TARGET_RISCV32)
          0x0202a583,                   /*     lw     a1, 32(t0) */
          0x0182a283,                   /*     lw     t0, 24(t0) */
      #elif defined(TARGET_RISCV64)
          0x0202b583,                   /*     ld     a1, 32(t0) */
          0x0182b283,                   /*     ld     t0, 24(t0) */
      #endif
          0x00028067,                   /*     jr     t0 */
          start_addr,                   /* start: .dword */
          start_addr_hi32,
          fdt_load_addr,                /* fdt_laddr: .dword */
          0x00000000,
                                        /* fw_dyn: */
      };

   完成的工作是：

   - 讀取當前的 Hart ID CSR ``mhartid`` 寫入寄存器 ``a0``
   - （我們還沒有用到：將 FDT (Flatten device tree) 在物理內存中的地址寫入 ``a1``）
   - 跳轉到 ``start_addr`` ，在我們實驗中是 RustSBI 的地址

5. `*` RISC-V中的SBI的含義和功能是啥？

    詳情見 `SBI 官方文檔 <https://github.com/riscv-non-isa/riscv-sbi-doc/blob/master/riscv-sbi.adoc>`_

6. `**` 為了讓應用程序能在計算機上執行，操作系統與編譯器之間需要達成哪些協議？

    編譯器依賴操作系統提供的程序庫，操作系統執行應用程序需要編譯器提供段位置、符號表、依賴庫等信息。 `ELF <https://en.wikipedia.org/wiki/Executable_and_Linkable_Format>`_ 就是比較常見的一種文件格式。

7.  `**` 請簡要說明從QEMU模擬的RISC-V計算機加電開始運行到執行應用程序的第一條指令這個階段的執行過程。

    接第 5 題，跳轉到 RustSBI 後，SBI 會對部分硬件例如串口等進行初始化，然後通過 mret 跳轉到 payload 也就是 kernel 所在的起始地址。kernel 進行一系列的初始化後（內存管理，虛存管理，線程（進程）初始化等），通過 sret 跳轉到應用程序的第一條指令開始執行。

8.  `**` 為何應用程序員編寫應用時不需要建立棧空間和指定地址空間？

    應用程度對內存的訪問需要通過 MMU 的地址翻譯完成，應用程序運行時看到的地址和實際位於內存中的地址是不同的，棧空間和地址空間需要內核進行管理和分配。應用程序的棧指針在 trap return 過程中初始化。此外，應用程序可能需要動態加載某些庫的內容，也需要內核完成映射。

9.  `***` 現代的很多編譯器生成的代碼，默認情況下不再嚴格保存/恢復棧幀指針。在這個情況下，我們只要編譯器提供足夠的信息，也可以完成對調用棧的恢復。（題目剩餘部分省略）

    * 首先，我們當前的 ``pc`` 在 ``flip`` 函數的開頭，這是我們正在運行的函數。返回給調用者處的地址在 ``ra`` 寄存器裡，是 ``0x10742`` 。因為我們還沒有開始操作棧指針，所以調用處的 ``sp`` 與我們相同，都是 ``0x40007f1310`` 。
    * ``0x10742`` 在 ``flap`` 函數內。根據 ``flap`` 函數的開頭可知，這個函數的棧幀大小是 16 個字節，所以調用者處的棧指針應該是 ``sp + 16 = 0x40007f1320``。調用 ``flap`` 的調用者返回地址保存在棧上 ``8(sp)`` ，可以讀出來是 ``0x10750`` ，還在 ``flap`` 函數內。
    * 依次類推，只要能理解已知地址對應的函數代碼，就可以完成恢復操作。

實驗練習
-------------------------------

問答作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. 請學習 gdb 調試工具的使用(這對後續調試很重要)，並通過 gdb 簡單跟蹤從機器加電到跳轉到 0x80200000 的簡單過程。只需要描述重要的跳轉即可，只需要描述在 qemu 上的情況。


.. [#qemu_bootrom] https://github.com/qemu/qemu/blob/0ebf76aae58324b8f7bf6af798696687f5f4c2a9/hw/riscv/boot.c#L300