.. _term-trap-handle:

實現特權級的切換
===========================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
-------------------------------

由於處理器具有硬件級的特權級機制，應用程序在用戶態特權級運行時，是無法直接通過函數調用訪問處於內核態特權級的批處理操作系統內核中的函數。但應用程序又需要得到操作系統提供的服務，所以應用程序與操作系統需要通過某種合作機制完成特權級之間的切換，使得用戶態應用程序可以得到內核態操作系統函數的服務。本節將講解在 RISC-V 64 處理器提供的 U/S 特權級下，批處理操作系統和應用程序如何相互配合，完成特權級切換的。

RISC-V特權級切換
---------------------------------------

特權級切換的起因
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
我們知道，批處理操作系統被設計為運行在內核態特權級（RISC-V 的 S 模式），這是作為 SEE（Supervisor Execution Environment）的 RustSBI 所保證的。而應用程序被設計為運行在用戶態特權級（RISC-V 的 U 模式），被操作系統為核心的執行環境監管起來。在本章中，這個應用程序的執行環境即是由“鄧式魚” 批處理操作系統提供的 AEE（Application Execution Environment) 。批處理操作系統為了建立好應用程序的執行環境，需要在執行應用程序之前進行一些初始化工作，並監控應用程序的執行，具體體現在：

- 當啟動應用程序的時候，需要初始化應用程序的用戶態上下文，並能切換到用戶態執行應用程序； 
- 當應用程序發起系統調用（即發出 Trap）之後，需要到批處理操作系統中進行處理；
- 當應用程序執行出錯的時候，需要到批處理操作系統中殺死該應用並加載運行下一個應用； 
- 當應用程序執行結束的時候，需要到批處理操作系統中加載運行下一個應用（實際上也是通過系統調用 ``sys_exit`` 來實現的）。

這些處理都涉及到特權級切換，因此需要應用程序、操作系統和硬件一起協同，完成特權級切換機制。


特權級切換相關的控制狀態寄存器
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

當從一般意義上討論 RISC-V 架構的 Trap 機制時，通常需要注意兩點：

- 在觸發 Trap 之前 CPU 運行在哪個特權級；
- CPU 需要切換到哪個特權級來處理該 Trap ，並在處理完成之後返回原特權級。
  
但本章中我們僅考慮如下流程：當 CPU 在用戶態特權級（ RISC-V 的 U 模式）運行應用程序，執行到 Trap，切換到內核態特權級（ RISC-V的S 模式），批處理操作系統的對應代碼響應 Trap，並執行系統調用服務，處理完畢後，從內核態返回到用戶態應用程序繼續執行後續指令。

.. _term-s-mod-csr:

在 RISC-V 架構中，關於 Trap 有一條重要的規則：在 Trap 前的特權級不會高於 Trap 後的特權級。因此如果觸發 Trap 之後切換到 S 特權級（下稱 Trap 到 S），說明 Trap 發生之前 CPU 只能運行在 S/U 特權級。但無論如何，只要是 Trap 到 S 特權級，操作系統就會使用 S 特權級中與 Trap 相關的 **控制狀態寄存器** (CSR, Control and Status Register) 來輔助 Trap 處理。我們在編寫運行在 S 特權級的批處理操作系統中的 Trap 處理相關代碼的時候，就需要使用如下所示的 S 模式的 CSR 寄存器。

.. list-table:: 進入 S 特權級 Trap 的相關 CSR
   :header-rows: 1
   :align: center
   :widths: 30 100

   * - CSR 名
     - 該 CSR 與 Trap 相關的功能
   * - sstatus
     - ``SPP`` 等字段給出 Trap 發生之前 CPU 處在哪個特權級（S/U）等信息
   * - sepc
     - 當 Trap 是一個異常的時候，記錄 Trap 發生之前執行的最後一條指令的地址
   * - scause
     - 描述 Trap 的原因
   * - stval
     - 給出 Trap 附加信息
   * - stvec
     - 控制 Trap 處理代碼的入口地址

.. note::

   **S模式下最重要的 sstatus 寄存器**

   注意 ``sstatus`` 是 S 特權級最重要的 CSR，可以從多個方面控制 S 特權級的 CPU 行為和執行狀態。
   
.. chy   
   我們在這裡先給出它在 Trap 處理過程中的作用。

特權級切換
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

當執行一條 Trap 類指令（如 ``ecall`` 時），CPU 發現觸發了一個異常並需要進行特殊處理，這涉及到 :ref:`執行環境切換 <term-ee-switch>` 。具體而言，用戶態執行環境中的應用程序通過 ``ecall`` 指令向內核態執行環境中的操作系統請求某項服務功能，那麼處理器和操作系統會完成到內核態執行環境的切換，並在操作系統完成服務後，再次切換回用戶態執行環境，然後應用程序會緊接著 ``ecall`` 指令的後一條指令位置處繼續執行，參考 :ref:`圖示 <environment-call-flow>` 。

.. chy ？？？: 這條觸發 Trap 的指令和進入 Trap 之前執行的最後一條指令不一定是同一條。

.. chy？？？ 下面的內容合併到第零章的os 抽象一節中， 執行環境切換, context等
    _term-execution-of-thread:
    回顧第一章的 :ref:`函數調用與棧 <function-call-and-stack>` ，我們知道在一個固定的 CPU 上，只要有一個棧作為存儲空間，我們就能以多種
    普通控制流（順序、分支、循環結構和多層嵌套函數調用）組合的方式，來一行一行的執行源代碼（以編程語言級的視角），也是一條一條的執行彙編指令
    （以彙編語言級的視角）。只考慮普通控制流，那麼從某條指令開始記錄，該 CPU 可用的所有資源，包括自帶的所有通用寄存器（包括虛擬的描述當前執行
    指令地址的寄存器 pc ）和當前特權級可用的 CSR 以及位於內存中的一塊棧空間，它們會隨著指令的執行而逐漸發生變化。這種侷限在普通控制流（相對於 :ref:`異常控制流 <term-ecf>` 而言）之內的
    連續指令執行和與之同步的對相關資源的改變我們用一個新名詞 **執行流** (Execution Flow) 來命名。執行流的狀態是一個由它衍生出來的
    概念，表示截止到某條指令執行完畢所有相關資源（包括寄存器、棧）的狀態集合，它完整描述了自記錄起始之後該執行流的指令執行歷史。
    .. note::
    實際上 CPU 還有其他資源可用：
    - 內存除了與執行流綁定的棧之外的其他存儲空間，比如程序中的數據段；
    - 外圍 I/O 設備。
    它們也會在執行期間動態發生變化。但它們可能由多條執行流共享，難以清晰的從中單獨區分出某一條執行流的狀態變化。因此在執行流概念中，
    我們不將其納入考慮。

.. chy？？？ 內容與第一段有重複
    讓我們通過從 U 特權級 Trap 到 S 特權級的切換過程（這是一個特例，實際上在 Trap 的前後，特權級也可以不變）來分析一下在 Trap 前後發生了哪些事情。首先假設CPU 正處在 U 特權級跑著應用程序的代碼。在執行完某一條指令之後， CPU 發現一個
    中斷/異常被觸發，於是必須將應用執行流暫停，先 Trap 到更高的 S 特權級去執行批處理操作系統提供的相應服務代碼，等待執行
    完了之後再回過頭來恢復到並繼續執行應用程序的執行流。
.. chy？？？  內容與第一段有重複
    我們可以將 CPU 在 S 特權級執行的那一段指令序列也看成一個控制流，因為它全程只是以普通控制流的模式在 S 特權級執行。這個控制流的意義就在於
    處理 Trap ，我們可以將其稱之為 **Trap 專用** 控制流，它在 Trap 觸發的時候開始，並於 Trap 處理完畢之後結束。於是我們可以從執行環境切換和控制流的角度來看待 
    操作系統對Trap 的整個處理過程： CPU 從用戶態執行環境中的應用程序的普通控制流轉到內核態執行環境中的 Trap 執行流，然後再切換回去繼續運行應用程序。站在應用程序的角度， 由操作系統和CPU協同完成的Trap 機制對它是完全透明的，無論應用程序在它的哪一條指令執行結束後進入 Trap ，它總是相信在 Trap 結束之後 CPU 能夠在與被打斷的時候"相同"的執行環境中繼續正確的運行應用程序的指令。
.. chy？？？ 
    .. note::
.. chy？？？  內容與第一段有重複
        這裡所說的相同並不是絕對相同，但是其變化是完全能夠被應用程序預知到的。比如應用程序通過 ``ecall`` 指令請求底層高特權級軟件的功能，
        由調用規範它知道 Trap 之後 ``a0~a1`` 兩個寄存器會被用來保存返回值，所以會發生變化。這個信息是應用程序明確知曉的，但某種程度上
        確實也體現了執行流的變化。

應用程序被切換回來之後需要從發出系統調用請求的執行位置恢復應用程序上下文並繼續執行，這需要在切換前後維持應用程序的上下文保持不變。應用程序的上下文包括通用寄存器和棧兩個主要部分。由於 CPU 在不同特權級下共享一套通用寄存器，所以在運行操作系統的 Trap 處理過程中，操作系統也會用到這些寄存器，這會改變應用程序的上下文。因此，與函數調用需要保存函數調用上下文/活動記錄一樣，在執行操作系統的 Trap 處理過程（會修改通用寄存器）之前，我們需要在某個地方（某內存塊或內核的棧）保存這些寄存器並在 Trap 處理結束後恢復這些寄存器。

除了通用寄存器之外還有一些可能在處理 Trap 過程中會被修改的 CSR，比如 CPU 所在的特權級。我們要保證它們的變化在我們的預期之內。比如，對於特權級轉換而言，應該是 Trap 之前在 U 特權級，處理 Trap 的時候在 S 特權級，返回之後又需要回到 U 特權級。而對於棧問題則相對簡單，只要兩個應用程序執行過程中用來記錄執行歷史的棧所對應的內存區域不相交，就不會產生令我們頭痛的覆蓋問題或數據破壞問題，也就無需進行保存/恢復。

特權級切換的具體過程一部分由硬件直接完成，另一部分則需要由操作系統來實現。

.. _trap-hw-mechanism:

特權級切換的硬件控制機制
-------------------------------------

當 CPU 執行完一條指令（如 ``ecall`` ）並準備從用戶特權級 陷入（ ``Trap`` ）到 S 特權級的時候，硬件會自動完成如下這些事情：

- ``sstatus`` 的 ``SPP`` 字段會被修改為 CPU 當前的特權級（U/S）。
- ``sepc`` 會被修改為被中斷或觸發異常的指令的地址。如 CPU 執行 ``ecall`` 指令會觸發異常，則 ``sepc`` 會被設置為 ``ecall`` 指令的地址。
- ``scause/stval`` 分別會被修改成這次 Trap 的原因以及相關的附加信息。
- CPU 會跳轉到 ``stvec`` 所設置的 Trap 處理入口地址，並將當前特權級設置為 S ，然後從Trap 處理入口地址處開始執行。

.. note::

   **stvec 相關細節**

   在 RV64 中， ``stvec`` 是一個 64 位的 CSR，在中斷使能的情況下，保存了中斷處理的入口地址。它有兩個字段：

   - MODE 位於 [1:0]，長度為 2 bits；
   - BASE 位於 [63:2]，長度為 62 bits。

   當 MODE 字段為 0 的時候， ``stvec`` 被設置為 Direct 模式，此時進入 S 模式的 Trap 無論原因如何，處理 Trap 的入口地址都是 ``BASE<<2`` ， CPU 會跳轉到這個地方進行異常處理。本書中我們只會將 ``stvec`` 設置為 Direct 模式。而 ``stvec`` 還可以被設置為 Vectored 模式，有興趣的同學可以自行參考 RISC-V 指令集特權級規範。

而當 CPU 完成 Trap 處理準備返回的時候，需要通過一條 S 特權級的特權指令 ``sret`` 來完成，這一條指令具體完成以下功能：

- CPU 會將當前的特權級按照 ``sstatus`` 的 ``SPP`` 字段設置為 U 或者 S ；
- CPU 會跳轉到 ``sepc`` 寄存器指向的那條指令，然後繼續執行。

這些基本上都是硬件不得不完成的事情，還有一些剩下的收尾工作可以都交給軟件，讓操作系統能有更大的靈活性。

用戶棧與內核棧
--------------------------------

在 Trap 觸發的一瞬間， CPU 就會切換到 S 特權級並跳轉到 ``stvec`` 所指示的位置。但是在正式進入 S 特權級的 Trap 處理之前，上面
提到過我們必須保存原控制流的寄存器狀態，這一般通過內核棧來保存。注意，我們需要用專門為操作系統準備的內核棧，而不是應用程序運行時用到的用戶棧。

.. 
    chy:我們在一個作為用戶棧的特別留出的內存區域上保存應用程序的棧信息，而 Trap 執行流則使用另一個內核棧。

使用兩個不同的棧主要是為了安全性：如果兩個控制流（即應用程序的控制流和內核的控制流）使用同一個棧，在返回之後應用程序就能讀到 Trap 控制流的歷史信息，比如內核一些函數的地址，這樣會帶來安全隱患。於是，我們要做的是，在批處理操作系統中添加一段彙編代碼，實現從用戶棧切換到內核棧，並在內核棧上保存應用程序控制流的寄存器狀態。不過需要注意的是，在沒有啟用虛擬內存的情況下，用戶態代碼依然可以通過物理地址訪問整個內存空間，包括內核棧區域。

我們聲明兩個類型 ``KernelStack`` 和 ``UserStack`` 分別表示內核棧和用戶棧，它們都只是字節數組的簡單包裝：

.. code-block:: rust
    :linenos:

    // os/src/batch.rs

    const USER_STACK_SIZE: usize = 4096 * 2;
    const KERNEL_STACK_SIZE: usize = 4096 * 2;

    #[repr(align(4096))]
    struct KernelStack {
        data: [u8; KERNEL_STACK_SIZE],
    }

    #[repr(align(4096))]
    struct UserStack {
        data: [u8; USER_STACK_SIZE],
    }

    static KERNEL_STACK: KernelStack = KernelStack { data: [0; KERNEL_STACK_SIZE] };
    static USER_STACK: UserStack = UserStack { data: [0; USER_STACK_SIZE] };

常數 ``USER_STACK_SIZE`` 和 ``KERNEL_STACK_SIZE`` 指出用戶棧和內核棧的大小分別為 :math:`8\text{KiB}` 。兩個類型是以全局變量的形式實例化在批處理操作系統的 ``.bss`` 段中的。

我們為兩個類型實現了 ``get_sp`` 方法來獲取棧頂地址。由於在 RISC-V 中棧是向下增長的，我們只需返回包裹的數組的結尾地址，以用戶棧類型 ``UserStack`` 為例：

.. code-block:: rust
    :linenos:

    impl UserStack {
        fn get_sp(&self) -> usize {
            self.data.as_ptr() as usize + USER_STACK_SIZE
        }
    }

於是換棧是非常簡單的，只需將 ``sp`` 寄存器的值修改為 ``get_sp`` 的返回值即可。

.. _term-trap-context:

接下來是Trap上下文（即數據結構 ``TrapContext`` ），類似前面提到的函數調用上下文，即在 Trap 發生時需要保存的物理資源內容，並將其一起放在一個名為 ``TrapContext`` 的類型中，定義如下：

.. code-block:: rust
    :linenos:

    // os/src/trap/context.rs

    #[repr(C)]
    pub struct TrapContext {
        pub x: [usize; 32],
        pub sstatus: Sstatus,
        pub sepc: usize,
    }

可以看到裡面包含所有的通用寄存器 ``x0~x31`` ，還有 ``sstatus`` 和 ``sepc`` 。那麼為什麼需要保存它們呢？

- 對於通用寄存器而言，兩條控制流（應用程序控制流和內核控制流）運行在不同的特權級，所屬的軟件也可能由不同的編程語言編寫，雖然在 Trap 控制流中只是會執行 Trap 處理相關的代碼，但依然可能直接或間接調用很多模塊，因此很難甚至不可能找出哪些寄存器無需保存。既然如此我們就只能全部保存了。但這裡也有一些例外，如 ``x0`` 被硬編碼為 0 ，它自然不會有變化；還有 ``tp(x4)`` 寄存器，除非我們手動出於一些特殊用途使用它，否則一般也不會被用到。雖然它們無需保存，但我們仍然在 ``TrapContext`` 中為它們預留空間，主要是為了後續的實現方便。
- 對於 CSR 而言，我們知道進入 Trap 的時候，硬件會立即覆蓋掉 ``scause/stval/sstatus/sepc`` 的全部或是其中一部分。``scause/stval`` 的情況是：它總是在 Trap 處理的第一時間就被使用或者是在其他地方保存下來了，因此它沒有被修改並造成不良影響的風險。而對於 ``sstatus/sepc`` 而言，它們會在 Trap 處理的全程有意義（在 Trap 控制流最後 ``sret`` 的時候還用到了它們），而且確實會出現 Trap 嵌套的情況使得它們的值被覆蓋掉。所以我們需要將它們也一起保存下來，並在 ``sret`` 之前恢復原樣。


Trap 管理
-------------------------------

特權級切換的核心是對Trap的管理。這主要涉及到如下一些內容：

- 應用程序通過 ``ecall`` 進入到內核狀態時，操作系統保存被打斷的應用程序的 Trap 上下文；
- 操作系統根據Trap相關的CSR寄存器內容，完成系統調用服務的分發與處理；
- 操作系統完成系統調用服務後，需要恢復被打斷的應用程序的Trap 上下文，並通 ``sret`` 讓應用程序繼續執行。

接下來我們具體介紹上述內容。

Trap 上下文的保存與恢復
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

首先是具體實現 Trap 上下文保存和恢復的彙編代碼。

.. _trap-context-save-restore: 


在批處理操作系統初始化的時候，我們需要修改 ``stvec`` 寄存器來指向正確的 Trap 處理入口點。

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    global_asm!(include_str!("trap.S"));

    pub fn init() {
        extern "C" { fn __alltraps(); }
        unsafe {
            stvec::write(__alltraps as usize, TrapMode::Direct);
        }
    }

這裡我們引入了一個外部符號 ``__alltraps`` ，並將 ``stvec`` 設置為 Direct 模式指向它的地址。我們在 ``os/src/trap/trap.S`` 中實現 Trap 上下文保存/恢復的彙編代碼，分別用外部符號 ``__alltraps`` 和 ``__restore`` 標記為函數，並通過 ``global_asm!`` 宏將 ``trap.S`` 這段彙編代碼插入進來。

Trap 處理的總體流程如下：首先通過 ``__alltraps`` 將 Trap 上下文保存在內核棧上，然後跳轉到使用 Rust 編寫的 ``trap_handler`` 函數完成 Trap 分發及處理。當 ``trap_handler`` 返回之後，使用 ``__restore`` 從保存在內核棧上的 Trap 上下文恢復寄存器。最後通過一條 ``sret`` 指令回到應用程序執行。

首先是保存 Trap 上下文的 ``__alltraps`` 的實現：

.. code-block:: riscv
    :linenos:

    # os/src/trap/trap.S

    .macro SAVE_GP n
        sd x\n, \n*8(sp)
    .endm

    .align 2
    __alltraps:
        csrrw sp, sscratch, sp
        # now sp->kernel stack, sscratch->user stack
        # allocate a TrapContext on kernel stack
        addi sp, sp, -34*8
        # save general-purpose registers
        sd x1, 1*8(sp)
        # skip sp(x2), we will save it later
        sd x3, 3*8(sp)
        # skip tp(x4), application does not use it
        # save x5~x31
        .set n, 5
        .rept 27
            SAVE_GP %n
            .set n, n+1
        .endr
        # we can use t0/t1/t2 freely, because they were saved on kernel stack
        csrr t0, sstatus
        csrr t1, sepc
        sd t0, 32*8(sp)
        sd t1, 33*8(sp)
        # read user stack from sscratch and save it on the kernel stack
        csrr t2, sscratch
        sd t2, 2*8(sp)
        # set input argument of trap_handler(cx: &mut TrapContext)
        mv a0, sp
        call trap_handler

- 第 7 行我們使用 ``.align`` 將 ``__alltraps`` 的地址 4 字節對齊，這是 RISC-V 特權級規範的要求；
- 第 9 行的 ``csrrw`` 原型是 :math:`\text{csrrw rd, csr, rs}` 可以將 CSR 當前的值讀到通用寄存器 :math:`\text{rd}` 中，然後將通用寄存器 :math:`\text{rs}` 的值寫入該 CSR 。因此這裡起到的是交換 sscratch 和 sp 的效果。在這一行之前 sp 指向用戶棧， sscratch 指向內核棧（原因稍後說明），現在 sp 指向內核棧， sscratch 指向用戶棧。
- 第 12 行，我們準備在內核棧上保存 Trap 上下文，於是預先分配 :math:`34\times 8` 字節的棧幀，這裡改動的是 sp ，說明確實是在內核棧上。
- 第 13~24 行，保存 Trap 上下文的通用寄存器 x0~x31，跳過 x0 和 tp(x4)，原因之前已經說明。我們在這裡也不保存 sp(x2)，因為我們要基於它來找到每個寄存器應該被保存到的正確的位置。實際上，在棧幀分配之後，我們可用於保存 Trap 上下文的地址區間為 :math:`[\text{sp},\text{sp}+8\times34)` ，按照  ``TrapContext`` 結構體的內存佈局，基於內核棧的位置（sp所指地址）來從低地址到高地址分別按順序放置 x0~x31這些通用寄存器，最後是 sstatus 和 sepc 。因此通用寄存器 xn 應該被保存在地址區間 :math:`[\text{sp}+8n,\text{sp}+8(n+1))` 。

  為了簡化代碼，x5~x31 這 27 個通用寄存器我們通過類似循環的 ``.rept`` 每次使用 ``SAVE_GP`` 宏來保存，其實質是相同的。注意我們需要在 ``trap.S`` 開頭加上 ``.altmacro`` 才能正常使用 ``.rept`` 命令。
- 第 25~28 行，我們將 CSR sstatus 和 sepc 的值分別讀到寄存器 t0 和 t1 中然後保存到內核棧對應的位置上。指令 :math:`\text{csrr rd, csr}`  的功能就是將 CSR 的值讀到寄存器 :math:`\text{rd}` 中。這裡我們不用擔心 t0 和 t1 被覆蓋，因為它們剛剛已經被保存了。
- 第 30~31 行專門處理 sp 的問題。首先將 sscratch 的值讀到寄存器 t2 並保存到內核棧上，注意： sscratch 的值是進入 Trap 之前的 sp 的值，指向用戶棧。而現在的 sp 則指向內核棧。
- 第 33 行令 :math:`\text{a}_0\leftarrow\text{sp}`，讓寄存器 a0 指向內核棧的棧指針也就是我們剛剛保存的 Trap 上下文的地址，這是由於我們接下來要調用 ``trap_handler`` 進行 Trap 處理，它的第一個參數 ``cx`` 由調用規範要從 a0 中獲取。而 Trap 處理函數 ``trap_handler`` 需要 Trap 上下文的原因在於：它需要知道其中某些寄存器的值，比如在系統調用的時候應用程序傳過來的 syscall ID 和對應參數。我們不能直接使用這些寄存器現在的值，因為它們可能已經被修改了，因此要去內核棧上找已經被保存下來的值。


.. _term-atomic-instruction:

.. note::

    **CSR 相關原子指令**

    RISC-V 中讀寫 CSR 的指令是一類能不會被打斷地完成多個讀寫操作的指令。這種不會被打斷地完成多個操作的指令被稱為 **原子指令** (Atomic Instruction)。這裡的 **原子** 的含義是“不可分割的最小個體”，也就是說指令的多個操作要麼都不完成，要麼全部完成，而不會處於某種中間狀態。

    另外，RISC-V 架構中常規的數據處理和訪存類指令只能操作通用寄存器而不能操作 CSR 。因此，當想要對 CSR 進行操作時，需要先使用讀取 CSR 的指令將 CSR 讀到一個通用寄存器中，而後操作該通用寄存器，最後再使用寫入 CSR 的指令將該通用寄存器的值寫入到 CSR 中。

當 ``trap_handler`` 返回之後會從調用 ``trap_handler`` 的下一條指令開始執行，也就是從棧上的 Trap 上下文恢復的 ``__restore`` ：

.. _code-restore:

.. code-block:: riscv
    :linenos:

    # os/src/trap/trap.S

    .macro LOAD_GP n
        ld x\n, \n*8(sp)
    .endm

    __restore:
        # case1: start running app by __restore
        # case2: back to U after handling trap
        mv sp, a0
        # now sp->kernel stack(after allocated), sscratch->user stack
        # restore sstatus/sepc
        ld t0, 32*8(sp)
        ld t1, 33*8(sp)
        ld t2, 2*8(sp)
        csrw sstatus, t0
        csrw sepc, t1
        csrw sscratch, t2
        # restore general-purpuse registers except sp/tp
        ld x1, 1*8(sp)
        ld x3, 3*8(sp)
        .set n, 5
        .rept 27
            LOAD_GP %n
            .set n, n+1
        .endr
        # release TrapContext on kernel stack
        addi sp, sp, 34*8
        # now sp->kernel stack, sscratch->user stack
        csrrw sp, sscratch, sp
        sret

- 第 10 行比較奇怪我們暫且不管，假設它從未發生，那麼 sp 仍然指向內核棧的棧頂。
- 第 13~26 行負責從內核棧頂的 Trap 上下文恢復通用寄存器和 CSR 。注意我們要先恢復 CSR 再恢復通用寄存器，這樣我們使用的三個臨時寄存器才能被正確恢復。
- 在第 28 行之前，sp 指向保存了 Trap 上下文之後的內核棧棧頂， sscratch 指向用戶棧棧頂。我們在第 28 行在內核棧上回收 Trap 上下文所佔用的內存，迴歸進入 Trap 之前的內核棧棧頂。第 30 行，再次交換 sscratch 和 sp，現在 sp 重新指向用戶棧棧頂，sscratch 也依然保存進入 Trap 之前的狀態並指向內核棧棧頂。
- 在應用程序控制流狀態被還原之後，第 31 行我們使用 ``sret`` 指令回到 U 特權級繼續運行應用程序控制流。

.. note::

    **sscratch CSR 的用途**

    在特權級切換的時候，我們需要將 Trap 上下文保存在內核棧上，因此需要一個寄存器暫存內核棧地址，並以它作為基地址指針來依次保存 Trap 上下文的內容。但是所有的通用寄存器都不能夠用作基地址指針，因為它們都需要被保存，如果覆蓋掉它們，就會影響後續應用控制流的執行。

    事實上我們缺少了一個重要的中轉寄存器，而 ``sscratch`` CSR 正是為此而生。從上面的彙編代碼中可以看出，在保存 Trap 上下文的時候，它起到了兩個作用：首先是保存了內核棧的地址，其次它可作為一箇中轉站讓 ``sp`` （目前指向的用戶棧的地址）的值可以暫時保存在 ``sscratch`` 。這樣僅需一條 ``csrrw  sp, sscratch, sp`` 指令（交換對 ``sp`` 和 ``sscratch`` 兩個寄存器內容）就完成了從用戶棧到內核棧的切換，這是一種極其精巧的實現。

Trap 分發與處理
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Trap 在使用 Rust 實現的 ``trap_handler`` 函數中完成分發和處理：

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler(cx: &mut TrapContext) -> &mut TrapContext {
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::UserEnvCall) => {
                cx.sepc += 4;
                cx.x[10] = syscall(cx.x[17], [cx.x[10], cx.x[11], cx.x[12]]) as usize;
            }
            Trap::Exception(Exception::StoreFault) |
            Trap::Exception(Exception::StorePageFault) => {
                println!("[kernel] PageFault in application, kernel killed it.");
                run_next_app();
            }
            Trap::Exception(Exception::IllegalInstruction) => {
                println!("[kernel] IllegalInstruction in application, kernel killed it.");
                run_next_app();
            }
            _ => {
                panic!("Unsupported trap {:?}, stval = {:#x}!", scause.cause(), stval);
            }
        }
        cx
    }

- 第 4 行聲明返回值為 ``&mut TrapContext`` 並在第 25 行實際將傳入的Trap 上下文 ``cx`` 原樣返回，因此在 ``__restore`` 的時候 ``a0`` 寄存器在調用 ``trap_handler`` 前後並沒有發生變化，仍然指向分配 Trap 上下文之後的內核棧棧頂，和此時 ``sp`` 的值相同，這裡的 :math:`\text{sp}\leftarrow\text{a}_0` 並不會有問題；
- 第 7 行根據 ``scause`` 寄存器所保存的 Trap 的原因進行分發處理。這裡我們無需手動操作這些 CSR ，而是使用 Rust 的 riscv 庫來更加方便的做這些事情。要引入 riscv 庫，我們需要：

  .. code-block:: toml

      # os/Cargo.toml
      
      [dependencies]
      riscv = { git = "https://github.com/rcore-os/riscv", features = ["inline-asm"] }  
    
- 第 8~11 行，發現觸發 Trap 的原因是來自 U 特權級的 Environment Call，也就是系統調用。這裡我們首先修改保存在內核棧上的 Trap 上下文裡面 sepc，讓其增加 4。這是因為我們知道這是一個由 ``ecall`` 指令觸發的系統調用，在進入 Trap 的時候，硬件會將 sepc 設置為這條 ``ecall`` 指令所在的地址（因為它是進入 Trap 之前最後一條執行的指令）。而在 Trap 返回之後，我們希望應用程序控制流從 ``ecall`` 的下一條指令開始執行。因此我們只需修改 Trap 上下文裡面的 sepc，讓它增加 ``ecall`` 指令的碼長，也即 4 字節。這樣在 ``__restore`` 的時候 sepc 在恢復之後就會指向 ``ecall`` 的下一條指令，並在 ``sret`` 之後從那裡開始執行。

  用來保存系統調用返回值的 a0 寄存器也會同樣發生變化。我們從 Trap 上下文取出作為 syscall ID 的 a7 和系統調用的三個參數 a0~a2 傳給 ``syscall`` 函數並獲取返回值。 ``syscall`` 函數是在 ``syscall`` 子模塊中實現的。 這段代碼是處理正常系統調用的控制邏輯。
- 第 12~20 行，分別處理應用程序出現訪存錯誤和非法指令錯誤的情形。此時需要打印錯誤信息並調用 ``run_next_app`` 直接切換並運行下一個應用程序。
- 第 21 行開始，當遇到目前還不支持的 Trap 類型的時候，“鄧式魚” 批處理操作系統整個 panic 報錯退出。



實現系統調用功能
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

對於系統調用而言， ``syscall`` 函數並不會實際處理系統調用，而只是根據 syscall ID 分發到具體的處理函數：

.. code-block:: rust
    :linenos:

    // os/src/syscall/mod.rs

    pub fn syscall(syscall_id: usize, args: [usize; 3]) -> isize {
        match syscall_id {
            SYSCALL_WRITE => sys_write(args[0], args[1] as *const u8, args[2]),
            SYSCALL_EXIT => sys_exit(args[0] as i32),
            _ => panic!("Unsupported syscall_id: {}", syscall_id),
        }
    }

這裡我們會將傳進來的參數 ``args`` 轉化成能夠被具體的系統調用處理函數接受的類型。它們的實現都非常簡單：

.. code-block:: rust
    :linenos:

    // os/src/syscall/fs.rs

    const FD_STDOUT: usize = 1;

    pub fn sys_write(fd: usize, buf: *const u8, len: usize) -> isize {
        match fd {
            FD_STDOUT => {
                let slice = unsafe { core::slice::from_raw_parts(buf, len) };
                let str = core::str::from_utf8(slice).unwrap();
                print!("{}", str);
                len as isize
            },
            _ => {
                panic!("Unsupported fd in sys_write!");
            }
        }
    }

    // os/src/syscall/process.rs

    pub fn sys_exit(xstate: i32) -> ! {
        println!("[kernel] Application exited with code {}", xstate);
        run_next_app()
    }

- ``sys_write`` 我們將傳入的位於應用程序內的緩衝區的開始地址和長度轉化為一個字符串 ``&str`` ，然後使用批處理操作系統已經實現的 ``print!`` 宏打印出來。注意這裡我們並沒有檢查傳入參數的安全性，即使會在出錯嚴重的時候 panic，還是會存在安全隱患。這裡我們出於實現方便暫且不做修補。
- ``sys_exit`` 打印退出的應用程序的返回值並同樣調用 ``run_next_app`` 切換到下一個應用程序。

.. _ch2-app-execution:

執行應用程序
-------------------------------------

當批處理操作系統初始化完成，或者是某個應用程序運行結束或出錯的時候，我們要調用 ``run_next_app`` 函數切換到下一個應用程序。此時 CPU 運行在 S 特權級，而它希望能夠切換到 U 特權級。在 RISC-V 架構中，唯一一種能夠使得 CPU 特權級下降的方法就是執行 Trap 返回的特權指令，如 ``sret`` 、``mret`` 等。事實上，在從操作系統內核返回到運行應用程序之前，要完成如下這些工作：


- 構造應用程序開始執行所需的 Trap 上下文；
- 通過 ``__restore`` 函數，從剛構造的 Trap 上下文中，恢復應用程序執行的部分寄存器；
- 設置 ``sepc`` CSR的內容為應用程序入口點 ``0x80400000``；
- 切換 ``scratch`` 和 ``sp`` 寄存器，設置 ``sp`` 指向應用程序用戶棧；
- 執行 ``sret`` 從 S 特權級切換到 U 特權級。


它們可以通過複用 ``__restore`` 的代碼來更容易的實現上述工作。我們只需要在內核棧上壓入一個為啟動應用程序而特殊構造的 Trap 上下文，再通過 ``__restore`` 函數，就能讓這些寄存器到達啟動應用程序所需要的上下文狀態。

.. code-block:: rust
    :linenos:

    // os/src/trap/context.rs

    impl TrapContext {
        pub fn set_sp(&mut self, sp: usize) { self.x[2] = sp; }
        pub fn app_init_context(entry: usize, sp: usize) -> Self {
            let mut sstatus = sstatus::read();
            sstatus.set_spp(SPP::User);
            let mut cx = Self {
                x: [0; 32],
                sstatus,
                sepc: entry,
            };
            cx.set_sp(sp);
            cx
        }
    }

為 ``TrapContext`` 實現 ``app_init_context`` 方法，修改其中的 sepc 寄存器為應用程序入口點 ``entry``， sp 寄存器為我們設定的一個棧指針，並將 sstatus 寄存器的 ``SPP`` 字段設置為 User 。

在 ``run_next_app`` 函數中我們能夠看到：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 14,15,16,17,18

    // os/src/batch.rs

    pub fn run_next_app() -> ! {
        let mut app_manager = APP_MANAGER.exclusive_access();
        let current_app = app_manager.get_current_app();
        unsafe {
            app_manager.load_app(current_app);
        }
        app_manager.move_to_next_app();
        drop(app_manager);
        // before this we have to drop local variables related to resources manually
        // and release the resources
        extern "C" { fn __restore(cx_addr: usize); }
        unsafe {
            __restore(KERNEL_STACK.push_context(
                TrapContext::app_init_context(APP_BASE_ADDRESS, USER_STACK.get_sp())
            ) as *const _ as usize);
        }
        panic!("Unreachable in batch::run_current_app!");
    }

在高亮行所做的事情是在內核棧上壓入一個 Trap 上下文，其 ``sepc`` 是應用程序入口地址 ``0x80400000`` ，其 ``sp`` 寄存器指向用戶棧，其 ``sstatus`` 的 ``SPP`` 字段被設置為 User 。``push_context`` 的返回值是內核棧壓入 Trap 上下文之後的棧頂，它會被作為 ``__restore`` 的參數（回看 :ref:`__restore 代碼 <code-restore>` ，這時我們可以理解為何 ``__restore`` 函數的起始部分會完成 :math:`\text{sp}\leftarrow\text{a}_0` ），這使得在 ``__restore`` 函數中 ``sp`` 仍然可以指向內核棧的棧頂。這之後，就和執行一次普通的 ``__restore`` 函數調用一樣了。

.. note::

    有興趣的同學可以思考： sscratch 是何時被設置為內核棧頂的？



.. 
   馬老師發生甚麼事了？
   --
   這裡要說明目前只考慮從 U Trap 到 S ，而實際上 Trap 的要素就有：Trap 之前在哪個特權級，Trap 在哪個特權級處理。這個對於中斷和異常
   都是如此，只不過中斷可能跟特權級的關係稍微更緊密一點。畢竟中斷的類型都是跟特權級掛鉤的。但是對於 Trap 而言有一點是共同的，也就是觸發 
   Trap 不會導致優先級下降。從中斷/異常的代理就可以看出從定義上就不允許代理到更低的優先級。而且代理只能逐級代理，目前我們能操作的只有從 
   M 代理到 S，其他代理都基本只出現在指令集拓展或者硬件還不支持。中斷的情況是，如果是屬於某個特權級的中斷，不能在更低的優先級處理。事實上
   這個中斷只可能在 CPU 處於不會更高的優先級上收到（否則會被屏蔽），而 Trap 之後優先級不會下降（Trap 代理機制決定），這樣就自洽了。
   --
   之前提到異常是說需要執行環境功能的原因與某條指令的執行有關。而 Trap 的定義更加廣泛一些，就是在執行某條指令之後發現需要執行環境的功能，
   如果是中斷的話 Trap 回來之後默認直接執行下一條指令，如果是異常的話硬件會將 sepc 設置為 Trap 發生之前最後執行的那條指令，而異常發生
   的原因不一定和這條指令的執行有關。應該指出的是，在大多數情況下都是和最後這條指令的執行有關。但在緩存的作用下也會出現那種特別極端的情況。
   --
   然後是 Trap 到 S，就有 S 模式的一些相關 CSR，以及從 U Trap 到 S，硬件會做哪些事情（包括觸發異常的一瞬間，以及處理完成調用 sret 
   之後）。然後指出從用戶的視角來看，如果是 ecall 的話， Trap 回來之後應該從 ecall 的下一條指令開始執行，且執行現場不能發生變化。
   所以就需要將應用執行環境保存在內核棧上（還需要換棧！）。棧存在的原因可能是 Trap handler 是一條新的運行在 S 特權級的執行流，所以
   這個可以理解成跨特權級的執行流切換，確實就複雜一點，要保存的內容也相對多一點。而下一章多任務的任務切換是全程發生在 S 特權級的執行流
   切換，所以會簡單一點，保存的通用寄存器大概率更少（少在調用者保存寄存器），從各種意義上都很像函數調用。從不同特權級的角度來解釋換棧
   是出於安全性，應用不應該看到 Trap 執行流的棧，這樣做完之後，雖然理論上可以訪問，但應用不知道內核棧的位置應該也有點麻煩。
   --
   然後是 rust_trap 的處理，尤其是奇妙的參數傳遞，內部處理邏輯倒是非常簡單。
   --
   最後是如何利用 __restore 初始化應用的執行環境，包括如何設置入口點、用戶棧以及保證在 U 特權級執行。





