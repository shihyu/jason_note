練習參考答案
=====================================================

.. toctree::
   :hidden:
   :maxdepth: 4


課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. `***` 實現一個裸機應用程序A，能打印調用棧。

   以 rCore tutorial ch2 代碼為例，在編譯選項中我們已經讓編譯器對所有函數調用都保存棧指針（參考 ``os/.cargo/config`` ），因此我們可以直接從 `fp` 寄存器追溯調用棧：

   .. code-block:: rust
      :caption: ``os/src/stack_trace.rs``

      use core::{arch::asm, ptr};

      pub unsafe fn print_stack_trace() -> () {
          let mut fp: *const usize;
          asm!("mv {}, fp", out(reg) fp);

          println!("== Begin stack trace ==");
          while fp != ptr::null() {
              let saved_ra = *fp.sub(1);
              let saved_fp = *fp.sub(2);

              println!("0x{:016x}, fp = 0x{:016x}", saved_ra, saved_fp);

              fp = saved_fp as *const usize;
          }
          println!("== End stack trace ==");
      }

   之後我們將其加入 ``main.rs`` 作為一個子模塊：

   .. code-block:: rust
      :caption: 加入 ``os/src/main.rs``
      :emphasize-lines: 4

      // ...
      mod syscall;
      mod trap;
      mod stack_trace;
      // ...

   作為一個示例，我們可以將打印調用棧的代碼加入 panic handler 中，在每次 panic 的時候打印調用棧：

   .. code-block:: rust
      :caption: ``os/lang_items.rs``
      :emphasize-lines: 3,9

      use crate::sbi::shutdown;
      use core::panic::PanicInfo;
      use crate::stack_trace::print_stack_trace;

      #[panic_handler]
      fn panic(info: &PanicInfo) -> ! {
          // ...

          unsafe { print_stack_trace(); }

          shutdown()
      }

   現在，panic 的時候輸入的信息變成了這樣：

   .. code-block::

      Panicked at src/batch.rs:68 All applications completed!
      == Begin stack trace ==
      0x0000000080200e12, fp = 0x0000000080205cf0
      0x0000000080201bfa, fp = 0x0000000080205dd0
      0x0000000080200308, fp = 0x0000000080205e00
      0x0000000080201228, fp = 0x0000000080205e60
      0x00000000802005b4, fp = 0x0000000080205ef0
      0x0000000080200424, fp = 0x0000000000000000
      == End stack trace ==

   這裡打印的兩個數字，第一個是棧幀上保存的返回地址，第二個是保存的上一個 frame pointer。


2. `**` 擴展內核，實現新系統調用get_taskinfo，能顯示當前task的id和task name；實現一個裸機應用程序B，能訪問get_taskinfo系統調用。
3. `**` 擴展內核，能夠統計多個應用的執行過程中系統調用編號和訪問此係統調用的次數。
4. `**` 擴展內核，能夠統計每個應用執行後的完成時間。
5. `***` 擴展內核，統計執行異常的程序的異常情況（主要是各種特權級涉及的異常），能夠打印異常程序的出錯的地址和指令等信息。
   
   在trap.c中添加相關異常情況的處理：

   .. code-block:: c
      :caption: ``os/trap.c``

      void usertrap()
      {        
         set_kerneltrap();
         struct trapframe *trapframe = curr_proc()->trapframe;

         if ((r_sstatus() & SSTATUS_SPP) != 0)
                  panic("usertrap: not from user mode");

         uint64 cause = r_scause();
         if (cause & (1ULL << 63)) {
                  cause &= ~(1ULL << 63);
                  switch (cause) {
                  case SupervisorTimer:
                        tracef("time interrupt!\n");
                        set_next_timer();
                        yield();
                        break;
                  default:
                        unknown_trap();
                        break;
                  }
         } else {
                  switch (cause) {
                  case UserEnvCall:
                        trapframe->epc += 4;
                        syscall();
                        break;
                  case StoreMisaligned:
                  case StorePageFault:
                  case InstructionMisaligned:
                  case InstructionPageFault:
                  case LoadMisaligned:
                  case LoadPageFault:
                        printf("%d in application, bad addr = %p, bad instruction = %p, "
                                 "core dumped.\n",
                                 cause, r_stval(), trapframe->epc);
                        exit(-2);
                        break;
                  case IllegalInstruction:
                        printf("IllegalInstruction in application, core dumped.\n");
                        exit(-3);
                        break;
                  default:
                        unknown_trap();
                        break;
                  }
         }
         usertrapret();
      }


注：上述編程基於 rcore/ucore tutorial v3: Branch ch2

問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 函數調用與系統調用有何區別？

   * 函數調用用普通的控制流指令，不涉及特權級的切換；系統調用使用專門的指令（如 RISC-V 上的 `ecall`），會切換到內核特權級。
   * 函數調用可以隨意指定調用目標；系統調用只能將控制流切換給調用操作系統內核給定的目標。

2. `**` 為了方便操作系統處理，Ｍ態軟件會將 S 態異常/中斷委託給 S 態軟件，請指出有哪些寄存器記錄了委託信息，rustsbi 委託了哪些異常/中斷？（也可以直接給出寄存器的值）

   * 兩個寄存器記錄了委託信息： ``mideleg`` （中斷委託）和 ``medeleg`` （異常委託）

   * 參考 RustSBI 輸出

     .. code-block::

        [rustsbi] mideleg: ssoft, stimer, sext (0x222)
        [rustsbi] medeleg: ima, ia, bkpt, la, sa, uecall, ipage, lpage, spage (0xb1ab)

     可知委託了中斷：

     * ``ssoft`` : S-mode 軟件中斷
     * ``stimer`` : S-mode 時鐘中斷
     * ``sext`` : S-mode 外部中斷

     委託了異常：

     * ``ima`` : 指令未對齊
     * ``ia`` : 取指訪問異常
     * ``bkpt`` : 斷點
     * ``la`` : 讀異常
     * ``sa`` : 寫異常
     * ``uecall`` : U-mode 系統調用
     * ``ipage`` : 取指 page fault
     * ``lpage`` : 讀 page fault
     * ``spage`` : 寫 page fault

3. `**` 如果操作系統以應用程序庫的形式存在，應用程序可以通過哪些方式破壞操作系統？

   如果操作系統以應用程序庫的形式存在，那麼編譯器在鏈接OS庫時會把應用程序跟OS庫鏈接成一個可執行文件，兩者處於同一地址空間，這也是LibOS（Unikernel）架構，此時存在如下幾個破壞操作系統的方式：
   
   * 緩衝區溢出：應用程序可以覆蓋寫其合法內存邊界之外的部分，這可能會危及 OS；
   * 整數溢出：當對整數值的運算產生的值超出整數數據類型可以表示的範圍時，就會發生整數溢出， 這可能會導致OS出現意外行為和安全漏洞。 例如，如果允許應用程序分配大量內存，攻擊者可能會在內存分配例程中觸發整數溢出，從而可能導致緩衝區溢出或其他安全漏洞；
   * 系統調用攔截：應用程序可能會攔截或重定向系統調用，從而可能損害OS的行為。例如，攻擊者可能會攔截讀取敏感文件的系統調用並將其重定向到他們選擇的文件，從而可能危及 unikernel 的安全性。
   * 資源耗盡：應用程序可能會消耗內存或網絡帶寬等資源，可能導致拒絕服務或其他安全漏洞。

4. `**` 編譯器/操作系統/處理器如何合作，可採用哪些方法來保護操作系統不受應用程序的破壞？

   硬件操作系統運行在一個硬件保護的安全執行環境中，不受到應用程序的破壞；應用程序運行在另外一個無法破壞操作系統的受限執行環境中。
   現代CPU提供了很多硬件機制來保護操作系統免受惡意應用程序的破壞，包括如下幾個：

   * 特權級模式：處理器能夠設置不同安全等級的執行環境，即用戶態執行環境和內核態特權級的執行環境。處理器在執行指令前會進行特權級安全檢查，如果在用戶態執行環境中執行內核態特權級指令，會產生異常阻止當前非法指令的執行。
   * TEE（可信執行環境）：CPU的TEE能夠構建一個可信的執行環境，用於抵禦惡意軟件或攻擊，能夠確保處理敏感數據的應用程序（例如移動銀行和支付應用程序）的安全。 
   * ASLR（地址空間佈局隨機化）：ASLR 是CPU的一種隨機化進程地址空間佈局的安全功能，其能夠隨機生成進程地址空間，例如棧、共享庫等關鍵部分的起始地址，使攻擊者預測特定數據或代碼的位置。
5. `**` RISC-V處理器的S態特權指令有哪些，其大致含義是什麼，有啥作用？

   RISC-V處理器的S態特權指令有兩類：指令本身屬於高特權級的指令，如 sret 指令（表示從 S 模式返回到 U 模式）。指令訪問了S模式特權級下才能訪問的寄存器或內存，如表示S模式系統狀態的 控制狀態寄存器 sstatus 等。如下所示：

   * sret：從 S 模式返回 U 模式。如可以讓位於S模式的驅動程序返回U模式。
   * wfi：讓CPU在空閒時進入等待狀態，以降低CPU功耗。
   * sfence.vma：刷新 TLB 緩存，在U模式下執行會嘗試非法指令異常。
   * 訪問 S 模式 CSR 的指令：通過訪問spce/stvec/scause/sscartch/stval/sstatus/satp等CSR來改變系統狀態。

6. `**` RISC-V處理器在用戶態執行特權指令後的硬件層面的處理過程是什麼？

   CPU 執行完一條指令（如 ecall ）並準備從用戶特權級 陷入（ Trap ）到 S 特權級的時候，硬件會自動完成如下這些事情：

   * sstatus 的 SPP 字段會被修改為 CPU 當前的特權級（U/S）。
   * sepc 會被修改為 Trap 處理完成後默認會執行的下一條指令的地址。
   * scause/stval 分別會被修改成這次 Trap 的原因以及相關的附加信息。
   * cpu 會跳轉到 stvec 所設置的 Trap 處理入口地址，並將當前特權級設置為 S ，然後從Trap 處理入口地址處開始執行。

   CPU 完成 Trap 處理準備返回的時候，需要通過一條 S 特權級的特權指令 sret 來完成，這一條指令具體完成以下功能：
   * CPU 會將當前的特權級按照 sstatus 的 SPP 字段設置為 U 或者 S ；
   * CPU 會跳轉到 sepc 寄存器指向的那條指令，然後繼續執行。

7. `**` 操作系統在完成用戶態<-->內核態雙向切換中的一般處理過程是什麼？
   
   當 CPU 在用戶態特權級（ RISC-V 的 U 模式）運行應用程序，執行到 Trap，切換到內核態特權級（ RISC-V的S 模式），批處理操作系統的對應代碼響應 Trap，並執行系統調用服務，處理完畢後，從內核態返回到用戶態應用程序繼續執行後續指令。

8. `**` 程序陷入內核的原因有中斷、異常和陷入（系統調用），請問 riscv64 支持哪些中斷 / 異常？如何判斷進入內核是由於中斷還是異常？描述陷入內核時的幾個重要寄存器及其值。

   * 具體支持的異常和中斷，參見 RISC-V 特權集規範 *The RISC-V Instruction Set Manual Volume II: Privileged Architecture* 。其它很多問題在這裡也有答案。
   * `scause` 的最高位，為 1 表示中斷，為 0 表示異常
   * 重要的寄存器：

     * `scause` ：發生了具體哪個異常或中斷
     * `sstatus` ：其中的一些控制為標誌發生異常時的處理器狀態，如 `sstatus.SPP` 表示發生異常時處理器在哪個特權級。
     * `sepc` ：發生異常或中斷的時候，將要執行但未成功執行的指令地址
     * `stval` ：值與具體異常相關，可能是發生異常的地址，指令等

9. `*` 在哪些情況下會出現特權級切換：用戶態-->內核態，以及內核態-->用戶態？

   * 用戶態–>內核態：應用程序發起系統調用；應用程序執行出錯，需要到批處理操作系統中殺死該應用並加載運行下一個應用；應用程序執行結束，需要到批處理操作系統中加載運行下一個應用。
   * 內核態–>用戶態：啟動應用程序需要初始化應用程序的用戶態上下文時；應用程序發起的系統調用執行完畢返回應用程序時。

10. `**` Trap上下文的含義是啥？在本章的操作系統中，Trap上下文的具體內容是啥？如果不進行Trap上下文的保存於恢復，會出現什麼情況？

   Trap上下文的主要有兩部分含義：

   * 在觸發 Trap 之前 CPU 運行在哪個特權級；
   * CPU 需要切換到哪個特權級來處理該 Trap ，並在處理完成之後返回原特權級。在本章的實際操作系統中，Trap上下文的具體內容主要包括通用寄存器和棧兩部分。如果不進行Trap的上下文保存與恢復，CPU就無法在處理完成之後，返回原特權級。


實驗練習
-------------------------------

問答作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. 正確進入 U 態後，程序的特徵還應有：使用 S 態特權指令，訪問 S 態寄存器後會報錯。請自行測試這些內容 (運行 Rust 三個 bad 測例 ) ，描述程序出錯行為，註明你使用的 sbi 及其版本。

2. 請結合用例理解 `trap.S <https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch2/os/src/trap/trap.S>`_ 中兩個函數 ``__alltraps`` 和 ``__restore`` 的作用，並回答如下幾個問題:

   1. L40：剛進入 ``__restore`` 時，``a0`` 代表了什麼值。請指出 ``__restore`` 的兩種使用情景。

   2. L46-L51：這幾行彙編代碼特殊處理了哪些寄存器？這些寄存器的的值對於進入用戶態有何意義？請分別解釋。

      .. code-block:: riscv

         ld t0, 32*8(sp)
         ld t1, 33*8(sp)
         ld t2, 2*8(sp)
         csrw sstatus, t0
         csrw sepc, t1
         csrw sscratch, t2

   3. L53-L59：為何跳過了 ``x2`` 和 ``x4``？

      .. code-block:: riscv

         ld x1, 1*8(sp)
         ld x3, 3*8(sp)
         .set n, 5
         .rept 27
            LOAD_GP %n
            .set n, n+1
         .endr

   4. L63：該指令之後，``sp`` 和 ``sscratch`` 中的值分別有什麼意義？

      .. code-block:: riscv

         csrrw sp, sscratch, sp

   5. ``__restore``：中發生狀態切換在哪一條指令？為何該指令執行之後會進入用戶態？

   6. L13：該指令之後，``sp`` 和 ``sscratch`` 中的值分別有什麼意義？

      .. code-block:: riscv

         csrrw sp, sscratch, sp

   7. 從 U 態進入 S 態是哪一條指令發生的？



3. 對於任何中斷，``__alltraps`` 中都需要保存所有寄存器嗎？你有沒有想到一些加速 ``__alltraps`` 的方法？簡單描述你的想法。
