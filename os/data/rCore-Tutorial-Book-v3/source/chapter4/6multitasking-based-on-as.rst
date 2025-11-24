基於地址空間的分時多任務
==============================================================


本節導讀
--------------------------




本節我們介紹如何基於地址空間抽象而不是對於物理內存的直接訪問來實現支持地址空間隔離的分時多任務系統 -- “頭甲龍” [#tutus]_ 操作系統 。這樣，我們的應用編寫會更加方便，應用與操作系統內核的空間隔離性增強了，應用程序和操作系統自身的安全性也得到了加強。為此，需要對現有的操作系統進行如下的功能擴展：

- 創建內核頁表，使能分頁機制，建立內核的虛擬地址空間；
- 擴展Trap上下文，在保存與恢復Trap上下文的過程中切換頁表（即切換虛擬地址空間）；
- 建立用於內核地址空間與應用地址空間相互切換所需的跳板空間；
- 擴展任務控制塊包括虛擬內存相關信息，並在加載執行創建基於某應用的任務時，建立應用的虛擬地址空間；
- 改進Trap處理過程和sys_write等系統調用的實現以支持分離的應用地址空間和內核地址空間。

在擴展了上述功能後，應用與應用之間，應用與操作系統內核之間通過硬件分頁機制實現了內存空間隔離，且應用和內核之間還是能有效地進行相互訪問，而且應用程序的編寫也會更加簡單通用。


建立並開啟基於分頁模式的虛擬地址空間
--------------------------------------------

當 SBI 實現（本項目中基於 RustSBI）初始化完成後， CPU 將跳轉到內核入口點並在 S 特權級上執行，此時還並沒有開啟分頁模式，內核的每次訪存是直接的物理內存訪問。而在開啟分頁模式之後，內核代碼在訪存時只能看到內核地址空間，此時每次訪存需要通過 MMU 的地址轉換。這兩種模式之間的過渡在內核初始化期間完成。

創建內核地址空間
^^^^^^^^^^^^^^^^^^^^^^^^


我們創建內核地址空間的全局實例：

.. code-block:: rust

    // os/src/mm/memory_set.rs

    lazy_static! {
        pub static ref KERNEL_SPACE: Arc<UPSafeCell<MemorySet>> = Arc::new(unsafe {
            UPSafeCell::new(MemorySet::new_kernel()
        )});
    }

從之前對於 ``lazy_static!`` 宏的介紹可知， ``KERNEL_SPACE`` 在運行期間它第一次被用到時才會實際進行初始化，而它所
佔據的空間則是編譯期被放在全局數據段中。這裡使用 ``Arc<UPSafeCell<T>>`` 組合是因為我們既需要 ``Arc<T>`` 提供的共享
引用，也需要 ``UPSafeCell<T>`` 提供的內部可變引用訪問。

在 ``rust_main`` 函數中，我們首先調用 ``mm::init`` 進行內存管理子系統的初始化：

.. code-block:: rust

    // os/src/mm/mod.rs

    pub use memory_set::KERNEL_SPACE;

    pub fn init() {
        heap_allocator::init_heap();
        frame_allocator::init_frame_allocator();
        KERNEL_SPACE.exclusive_access().activate();
    }

可以看到，我們最先進行了全局動態內存分配器的初始化，因為接下來馬上就要用到 Rust 的堆數據結構。接下來我們初始化物理頁幀管理器（內含堆數據結構 ``Vec<T>`` ）使能可用物理頁幀的分配和回收能力。最後我們創建內核地址空間並讓 CPU 開啟分頁模式， MMU 在地址轉換的時候使用內核的多級頁表，這一切均在一行之內做到：

- 首先，我們引用 ``KERNEL_SPACE`` ，這是它第一次被使用，就在此時它會被初始化，調用 ``MemorySet::new_kernel`` 創建一個內核地址空間並使用 ``Arc<UPSafeCell<T>>`` 包裹起來；
- 接著使用 ``.exclusive_access()`` 獲取一個可變引用 ``&mut MemorySet`` 。需要注意的是這裡發生了兩次隱式類型轉換：

  1.  我們知道 ``exclusive_access`` 是 ``UPSafeCell<T>`` 的方法而不是 ``Arc<T>`` 的方法，由於 ``Arc<T>`` 實現了 ``Deref`` Trait ，當 ``exclusive_access`` 需要一個 ``&UPSafeCell<T>`` 類型的參數的時候，編譯器會自動將傳入的 ``Arc<UPSafeCell<T>>`` 轉換為 ``&UPSafeCell<T>`` 這樣就實現了類型匹配；
  2.  事實上 ``UPSafeCell<T>::exclusive_access`` 返回的是一個 ``RefMut<'_, T>`` ，這同樣是 RAII 的思想，當這個類型生命週期結束後互斥鎖就會被釋放。而該類型實現了 ``DerefMut`` Trait，因此當一個函數接受類型為 ``&mut T`` 的參數卻被傳入一個類型為 ``&mut RefMut<'_, T>`` 的參數的時候，編譯器會自動進行類型轉換使參數匹配。
- 最後，我們調用 ``MemorySet::activate`` ：

    .. code-block:: rust 
        :linenos:

        // os/src/mm/page_table.rs

        pub fn token(&self) -> usize {
            8usize << 60 | self.root_ppn.0
        }

        // os/src/mm/memory_set.rs

        impl MemorySet {
            pub fn activate(&self) {
                let satp = self.page_table.token();
                unsafe {
                    satp::write(satp);
                    asm!("sfence.vma");
                }
            }
        }

  ``PageTable::token`` 會按照 :ref:`satp CSR 格式要求 <satp-layout>` 構造一個無符號 64 位無符號整數，使得其分頁模式為 SV39 ，且將當前多級頁表的根節點所在的物理頁號填充進去。在 ``activate`` 中，我們將這個值寫入當前 CPU 的 satp CSR ，從這一刻開始 SV39 分頁模式就被啟用了，而且 MMU 會使用內核地址空間的多級頁表進行地址轉換。

  我們必須注意切換 satp CSR 是否是一個 *平滑* 的過渡：其含義是指，切換 satp 的指令及其下一條指令這兩條相鄰的指令的虛擬地址是相鄰的（由於切換 satp 的指令並不是一條跳轉指令， pc 只是簡單的自增當前指令的字長），而它們所在的物理地址一般情況下也是相鄰的，但是它們所經過的地址轉換流程卻是不同的——切換 satp 導致 MMU 查的多級頁表是不同的。這就要求前後兩個地址空間在切換 satp 的指令 *附近* 的映射滿足某種意義上的連續性。

  幸運的是，我們做到了這一點。這條寫入 satp 的指令及其下一條指令都在內核內存佈局的代碼段中，在切換之後是一個恆等映射，而在切換之前是視為物理地址直接取指，也可以將其看成一個恆等映射。這完全符合我們的期待：即使切換了地址空間，指令仍應該能夠被連續的執行。

注意到在 ``activate`` 的最後，我們插入了一條彙編指令 ``sfence.vma`` ，它又起到什麼作用呢？

讓我們再來回顧一下多級頁表：它相比線性表雖然大量節約了內存佔用，但是卻需要 MMU 進行更多的隱式訪存。如果是一個線性表， MMU 僅需單次訪存就能找到頁表項並完成地址轉換，而多級頁表（以 SV39 為例，不考慮大頁）最順利的情況下也需要三次訪存。這些額外的訪存和真正訪問數據的那些訪存在空間上並不相鄰，加大了多級緩存的壓力，一旦緩存缺失將帶來巨大的性能懲罰。如果採用多級頁表實現，這個問題會變得更為嚴重，使得地址空間抽象的性能開銷過大。

.. _term-tlb:

為了解決性能問題，一種常見的做法是在 CPU 中利用部分硬件資源額外加入一個 **快表** (TLB, Translation Lookaside Buffer) ， 它維護了部分虛擬頁號到頁表項的鍵值對。當 MMU 進行地址轉換的時候，首先會到快表中看看是否匹配，如果匹配的話直接取出頁表項完成地址轉換而無需訪存；否則再去查頁表並將鍵值對保存在快表中。一旦我們修改 satp 就會切換地址空間，快表中的鍵值對就會失效（因為快表保存著老地址空間的映射關係，切換到新地址空間後，老的映射關係就沒用了）。為了確保 MMU 的地址轉換能夠及時與 satp 的修改同步，我們需要立即使用 ``sfence.vma`` 指令將快表清空，這樣 MMU 就不會看到快表中已經過期的鍵值對了。

.. note::

    **sfence.vma 是一個屏障(Barrier)**

    對於一種含有快表的 RISC-V CPU 實現來說，我們可以認為 ``sfence.vma`` 的作用就是清空快表。事實上它在特權級規範中被定義為一種含義更加豐富的內存屏障，具體來說： ``sfence.vma`` 可以使得所有發生在它後面的地址轉換都能夠看到所有排在它前面的寫入操作。在不同的硬件配置上這條指令要做的具體事務是有差異的。這條指令還可以被精細配置來減少同步開銷，詳情請參考 RISC-V 特權級規範。


檢查內核地址空間的多級頁表設置
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

調用 ``mm::init`` 之後我們就使能了內核動態內存分配、物理頁幀管理，還啟用了分頁模式進入了內核地址空間。之後我們可以通過 ``mm::remap_test`` 來檢查內核地址空間的多級頁表是否被正確設置：

.. code-block:: rust

    // os/src/mm/memory_set.rs

    pub fn remap_test() {
        let mut kernel_space = KERNEL_SPACE.exclusive_access();
        let mid_text: VirtAddr = ((stext as usize + etext as usize) / 2).into();
        let mid_rodata: VirtAddr = ((srodata as usize + erodata as usize) / 2).into();
        let mid_data: VirtAddr = ((sdata as usize + edata as usize) / 2).into();
        assert_eq!(
            kernel_space.page_table.translate(mid_text.floor()).unwrap().writable(),
            false
        );
        assert_eq!(
            kernel_space.page_table.translate(mid_rodata.floor()).unwrap().writable(),
            false,
        );
        assert_eq!(
            kernel_space.page_table.translate(mid_data.floor()).unwrap().executable(),
            false,
        );
        println!("remap_test passed!");
    }

在上述函數的實現中，分別通過手動查內核多級頁表的方式驗證代碼段和只讀數據段不允許被寫入，同時不允許從數據段上取指執行。

.. _term-trampoline:

跳板機制的實現
------------------------------------

上一小節我們看到無論是內核還是應用的地址空間，最高的虛擬頁面都是一個跳板。同時應用地址空間的次高虛擬頁面還被設置為用來存放應用的 Trap 上下文。那麼跳板究竟起什麼作用呢？為何不直接把 Trap 上下文仍放到應用的內核棧中呢？

回憶曾在第二章介紹過的 :ref:`Trap 上下文保存與恢復 <trap-context-save-restore>` 。當一個應用 Trap 到內核時，``sscratch`` 已指向該應用的內核棧棧頂，我們用一條指令即可從用戶棧切換到內核棧，然後直接將 Trap 上下文壓入內核棧棧頂。當 Trap 處理完畢返回用戶態的時候，將 Trap 上下文中的內容恢復到寄存器上，最後將保存著應用用戶棧頂的 ``sscratch`` 與 sp 進行交換，也就從內核棧切換回了用戶棧。在這個過程中， ``sscratch`` 起到了非常關鍵的作用，它使得我們可以在不破壞任何通用寄存器的情況下，完成用戶棧與內核棧的切換，以及位於內核棧頂的 Trap 上下文的保存與恢復。

然而，一旦使能了分頁機制，一切就並沒有這麼簡單了，我們必須在這個過程中同時完成地址空間的切換。具體來說，當 ``__alltraps`` 保存 Trap 上下文的時候，我們必須通過修改 satp 從應用地址空間切換到內核地址空間，因為 trap handler 只有在內核地址空間中才能訪問；同理，在 ``__restore`` 恢復 Trap 上下文的時候，我們也必須從內核地址空間切換回應用地址空間，因為應用的代碼和數據只能在它自己的地址空間中才能訪問，應用是看不到內核地址空間的。這樣就要求地址空間的切換不能影響指令的連續執行，即要求應用和內核地址空間在切換地址空間指令附近是平滑的。

.. _term-meltdown:

.. note::

    **內核與應用地址空間的隔離**

    目前我們的設計思路 A 是：對內核建立唯一的內核地址空間存放內核的代碼、數據，同時對於每個應用維護一個它們自己的用戶地址空間，因此在 Trap 的時候就需要進行地址空間切換，而在任務切換的時候無需進行（因為這個過程全程在內核內完成）。

    另外的一種設計思路 B 是：讓每個應用都有一個包含應用和內核的地址空間，並將其中的邏輯段分為內核和用戶兩部分，分別映射到內核/用戶的數據和代碼，且分別在 CPU 處於 S/U 特權級時訪問。此設計中並不存在一個單獨的內核地址空間。

    設計方式 B 的優點在於： Trap 的時候無需切換地址空間，而在任務切換的時候才需要切換地址空間。相對而言，設計方式B比設計方式A更容易實現，在應用高頻進行系統調用的時候，採用設計方式B能夠避免頻繁地址空間切換的開銷，這通常源於快表或 cache 的失效問題。但是設計方式B也有缺點：即內核的邏輯段需要在每個應用的地址空間內都映射一次，這會帶來一些無法忽略的內存佔用開銷，並顯著限制了嵌入式平臺（如我們所採用的 K210 ）的任務併發數。此外，設計方式 B 無法防禦針對處理器電路設計缺陷的側信道攻擊（如 `熔斷 (Meltdown) 漏洞 <https://cacm.acm.org/magazines/2020/6/245161-meltdown/fulltext>`_ ），使得惡意應用能夠以某種方式間接“看到”內核地址空間中的數據，使得用戶隱私數據有可能被洩露。將內核與地址空間隔離便是修復此漏洞的一種方法。

    經過權衡，在本教程中我們參考 MIT 的教學 OS `xv6 <https://github.com/mit-pdos/xv6-riscv>`_ ，採用內核和應用地址空間隔離的設計。

我們為何將應用的 Trap 上下文放到應用地址空間的次高頁面而不是內核地址空間中的內核棧中呢？原因在於，在保存 Trap 上下文到內核棧中之前，我們必須完成兩項工作：1）必須先切換到內核地址空間，這就需要將內核地址空間的 token 寫入 satp 寄存器；2）之後還需要保存應用的內核棧棧頂的位置，這樣才能以它為基址保存 Trap 上下文。這兩步需要用寄存器作為臨時週轉，然而我們無法在不破壞任何一個通用寄存器的情況下做到這一點。因為事實上我們需要用到內核的兩條信息：內核地址空間的 token ，以及應用的內核棧棧頂的位置，RISC-V卻只提供一個 ``sscratch`` 寄存器可用來進行週轉。所以，我們不得不將 Trap 上下文保存在應用地址空間的一個虛擬頁面中，而不是切換到內核地址空間去保存。


擴展Trap 上下文
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

為了方便實現，我們在 Trap 上下文中包含更多內容（和我們關於上下文的定義有些不同，它們在初始化之後便只會被讀取而不會被寫入，並不是每次都需要保存/恢復）：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 8,9,10

    // os/src/trap/context.rs

    #[repr(C)]
    pub struct TrapContext {
        pub x: [usize; 32],
        pub sstatus: Sstatus,
        pub sepc: usize,
        pub kernel_satp: usize,
        pub kernel_sp: usize,
        pub trap_handler: usize,
    }

在多出的三個字段中：

- ``kernel_satp`` 表示內核地址空間的 token ，即內核頁表的起始物理地址；
- ``kernel_sp`` 表示當前應用在內核地址空間中的內核棧棧頂的虛擬地址；
- ``trap_handler`` 表示內核中 trap handler 入口點的虛擬地址。

它們在應用初始化的時候由內核寫入應用地址空間中的 TrapContext 的相應位置，此後就不再被修改。



切換地址空間
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

讓我們來看一下現在的 ``__alltraps`` 和 ``__restore`` 各是如何在保存和恢復 Trap 上下文的同時也切換地址空間的：

.. code-block:: riscv
    :linenos:

    # os/src/trap/trap.S

        .section .text.trampoline
        .globl __alltraps
        .globl __restore
        .align 2
    __alltraps:
        csrrw sp, sscratch, sp
        # now sp->*TrapContext in user space, sscratch->user stack
        # save other general purpose registers
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
        # we can use t0/t1/t2 freely, because they have been saved in TrapContext
        csrr t0, sstatus
        csrr t1, sepc
        sd t0, 32*8(sp)
        sd t1, 33*8(sp)
        # read user stack from sscratch and save it in TrapContext
        csrr t2, sscratch
        sd t2, 2*8(sp)
        # load kernel_satp into t0
        ld t0, 34*8(sp)
        # load trap_handler into t1
        ld t1, 36*8(sp)
        # move to kernel_sp
        ld sp, 35*8(sp)
        # switch to kernel space
        csrw satp, t0
        sfence.vma
        # jump to trap_handler
        jr t1

    __restore:
        # a0: *TrapContext in user space(Constant); a1: user space token
        # switch to user space
        csrw satp, a1
        sfence.vma
        csrw sscratch, a0
        mv sp, a0
        # now sp points to TrapContext in user space, start restoring based on it
        # restore sstatus/sepc
        ld t0, 32*8(sp)
        ld t1, 33*8(sp)
        csrw sstatus, t0
        csrw sepc, t1
        # restore general purpose registers except x0/sp/tp
        ld x1, 1*8(sp)
        ld x3, 3*8(sp)
        .set n, 5
        .rept 27
            LOAD_GP %n
            .set n, n+1
        .endr
        # back to user stack
        ld sp, 2*8(sp)
        sret

- 當應用 Trap 進入內核的時候，硬件會設置一些 CSR 並在 S 特權級下跳轉到 ``__alltraps`` 保存 Trap 上下文。此時 sp 寄存器仍指向用戶棧，但 ``sscratch`` 則被設置為指向應用地址空間中存放 Trap 上下文的位置（實際在次高頁面）。隨後，就像之前一樣，我們 ``csrrw`` 交換 sp 和 ``sscratch`` ，並基於指向 Trap 上下文位置的 sp 開始保存通用寄存器和一些 CSR ，這個過程在第 28 行結束。到這裡，我們就全程在應用地址空間中完成了保存 Trap 上下文的工作。
  
- 接下來該考慮切換到內核地址空間並跳轉到 trap handler 了。

  - 第 30 行將內核地址空間的 token 載入到 t0 寄存器中；
  - 第 32 行將 trap handler 入口點的虛擬地址載入到 t1 寄存器中；
  - 第 34 行直接將 sp 修改為應用內核棧頂的地址；

  注：這三條信息均是內核在初始化該應用的時候就已經設置好的。

  - 第 36~37 行將 satp 修改為內核地址空間的 token 並使用 ``sfence.vma`` 刷新快表，這就切換到了內核地址空間；
  - 第 39 行 最後通過 ``jr`` 指令跳轉到 t1 寄存器所保存的trap handler 入口點的地址。

  注：這裡我們不能像之前的章節那樣直接 ``call trap_handler`` ，原因稍後解釋。

- 當內核將 Trap 處理完畢準備返回用戶態的時候會 *調用* ``__restore`` （符合RISC-V函數調用規範），它有兩個參數：第一個是 Trap 上下文在應用地址空間中的位置，這個對於所有的應用來說都是相同的，在 a0 寄存器中傳遞；第二個則是即將回到的應用的地址空間的 token ，在 a1 寄存器中傳遞。

  - 第 44~45 行先切換回應用地址空間（注：Trap 上下文是保存在應用地址空間中）；
  - 第 46 行將傳入的 Trap 上下文位置保存在 ``sscratch`` 寄存器中，這樣 ``__alltraps`` 中才能基於它將 Trap 上下文保存到正確的位置；
  - 第 47 行將 sp 修改為 Trap 上下文的位置，後面基於它恢復各通用寄存器和 CSR；
  - 第 64 行最後通過 ``sret`` 指令返回用戶態。


建立跳板頁面
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


接下來還需要考慮切換地址空間前後指令能否仍能連續執行。可以看到我們將 ``trap.S`` 中的整段彙編代碼放置在 ``.text.trampoline`` 段，並在調整內存佈局的時候將它對齊到代碼段的一個頁面中：

.. code-block:: diff
    :linenos:

    # os/src/linker.ld

        stext = .;
        .text : {
            *(.text.entry)
    +        . = ALIGN(4K);
    +        strampoline = .;
    +        *(.text.trampoline);
    +        . = ALIGN(4K);
            *(.text .text.*)
        }

這樣，這段彙編代碼放在一個物理頁幀中，且 ``__alltraps`` 恰好位於這個物理頁幀的開頭，其物理地址被外部符號 ``strampoline`` 標記。在開啟分頁模式之後，內核和應用代碼都只能看到各自的虛擬地址空間，而在它們的視角中，這段彙編代碼都被放在它們各自地址空間的最高虛擬頁面上，由於這段彙編代碼在執行的時候涉及到地址空間切換，故而被稱為跳板頁面。

在產生trap前後的一小段時間內會有一個比較 **極端** 的情況，即剛產生trap時，CPU已經進入了內核態（即Supervisor Mode），但此時執行代碼和訪問數據還是在應用程序所處的用戶態虛擬地址空間中，而不是我們通常理解的內核虛擬地址空間。在這段特殊的時間內，CPU指令為什麼能夠被連續執行呢？這裡需要注意：無論是內核還是應用的地址空間，跳板的虛擬頁均位於同樣位置，且它們也將會映射到同一個實際存放這段彙編代碼的物理頁幀。也就是說，在執行 ``__alltraps`` 或 ``__restore`` 函數進行地址空間切換的時候，應用的用戶態虛擬地址空間和操作系統內核的內核態虛擬地址空間對切換地址空間的指令所在頁的映射方式均是相同的，這就說明了這段切換地址空間的指令控制流仍是可以連續執行的。

現在可以說明我們在創建用戶/內核地址空間中用到的 ``map_trampoline`` 是如何實現的了：

.. code-block:: rust
    :linenos:

    // os/src/config.rs

    pub const TRAMPOLINE: usize = usize::MAX - PAGE_SIZE + 1;

    // os/src/mm/memory_set.rs

    impl MemorySet {
        /// Mention that trampoline is not collected by areas.
        fn map_trampoline(&mut self) {
            self.page_table.map(
                VirtAddr::from(TRAMPOLINE).into(),
                PhysAddr::from(strampoline as usize).into(),
                PTEFlags::R | PTEFlags::X,
            );
        }
    }

這裡我們為了實現方便並沒有新增邏輯段 ``MemoryArea`` 而是直接在多級頁表中插入一個從地址空間的最高虛擬頁面映射到跳板彙編代碼所在的物理頁幀的鍵值對，訪問權限與代碼段相同，即 ``RX`` （可讀可執行）。

最後可以解釋為何我們在 ``__alltraps`` 中需要藉助寄存器 ``jr`` 而不能直接 ``call trap_handler`` 了。因為在內存佈局中，這條 ``.text.trampoline`` 段中的跳轉指令和 ``trap_handler`` 都在代碼段之內，彙編器（Assembler）和鏈接器（Linker）會根據 ``linker-qemu/k210.ld`` 的地址佈局描述，設定跳轉指令的地址，並計算二者地址偏移量，讓跳轉指令的實際效果為當前 pc 自增這個偏移量。但實際上由於我們設計的緣故，這條跳轉指令在被執行的時候，它的虛擬地址被操作系統內核設置在地址空間中的最高頁面之內，所以加上這個偏移量並不能正確的得到 ``trap_handler`` 的入口地址。

**問題的本質可以概括為：跳轉指令實際被執行時的虛擬地址和在編譯器/彙編器/鏈接器進行後端代碼生成和鏈接形成最終機器碼時設置此指令的地址是不同的。** 

加載和執行應用程序
------------------------------------

擴展任務控制塊
^^^^^^^^^^^^^^^^^^^^^^^^^^^

為了讓應用在運行時有一個安全隔離且符合編譯器給應用設定的地址空間佈局的虛擬地址空間，操作系統需要對任務進行更多的管理，所以任務控制塊相比第三章也包含了更多內容：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 6,7,8

    // os/src/task/task.rs

    pub struct TaskControlBlock {
        pub task_cx: TaskContext,
        pub task_status: TaskStatus,
        pub memory_set: MemorySet,
        pub trap_cx_ppn: PhysPageNum,
        pub base_size: usize,
    }

除了應用的地址空間 ``memory_set`` 之外，還有位於應用地址空間次高頁的 Trap 上下文被實際存放在物理頁幀的物理頁號 ``trap_cx_ppn`` ，它能夠方便我們對於 Trap 上下文進行訪問。此外， ``base_size`` 統計了應用數據的大小，也就是在應用地址空間中從 :math:`\text{0x0}` 開始到用戶棧結束一共包含多少字節。它後續還應該包含用於應用動態內存分配的堆空間的大小，但目前暫不支持。



更新對任務控制塊的管理
^^^^^^^^^^^^^^^^^^^^^^^^^^^

下面是任務控制塊的創建：

.. code-block:: rust
    :linenos:

    // os/src/config.rs

    /// Return (bottom, top) of a kernel stack in kernel space.
    pub fn kernel_stack_position(app_id: usize) -> (usize, usize) {
        let top = TRAMPOLINE - app_id * (KERNEL_STACK_SIZE + PAGE_SIZE);
        let bottom = top - KERNEL_STACK_SIZE;
        (bottom, top)
    }

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn new(elf_data: &[u8], app_id: usize) -> Self {
            // memory_set with elf program headers/trampoline/trap context/user stack
            let (memory_set, user_sp, entry_point) = MemorySet::from_elf(elf_data);
            let trap_cx_ppn = memory_set
                .translate(VirtAddr::from(TRAP_CONTEXT).into())
                .unwrap()
                .ppn();
            let task_status = TaskStatus::Ready;
            // map a kernel-stack in kernel space
            let (kernel_stack_bottom, kernel_stack_top) = kernel_stack_position(app_id);
            KERNEL_SPACE
                .exclusive_access()
                .insert_framed_area(
                    kernel_stack_bottom.into(),
                    kernel_stack_top.into(),
                    MapPermission::R | MapPermission::W,
                );
            let task_control_block = Self {
                task_status,
                task_cx: TaskContext::goto_trap_return(kernel_stack_top),
                memory_set,
                trap_cx_ppn,
                base_size: user_sp,
            };
            // prepare TrapContext in user space
            let trap_cx = task_control_block.get_trap_cx();
            *trap_cx = TrapContext::app_init_context(
                entry_point,
                user_sp,
                KERNEL_SPACE.exclusive_access().token(),
                kernel_stack_top,
                trap_handler as usize,
            );
            task_control_block
        }
    }

- 第 15 行，解析傳入的 ELF 格式數據構造應用的地址空間 ``memory_set`` 並獲得其他信息；
- 第 16 行，從地址空間 ``memory_set`` 中查多級頁表找到應用地址空間中的 Trap 上下文實際被放在哪個物理頁幀；
- 第 22 行，根據傳入的應用 ID ``app_id`` 調用在 ``config`` 子模塊中定義的 ``kernel_stack_position`` 找到
  應用的內核棧預計放在內核地址空間 ``KERNEL_SPACE`` 中的哪個位置，並通過 ``insert_framed_area`` 實際將這個邏輯段
  加入到內核地址空間中；

.. _trap-return-intro:

- 第 30~32 行，在應用的內核棧頂壓入一個跳轉到 ``trap_return`` 而不是 ``__restore`` 的任務上下文，這主要是為了能夠支持對該應用的啟動並順利切換到用戶地址空間執行。在構造方式上，只是將 ra 寄存器的值設置為 ``trap_return`` 的地址。 ``trap_return`` 是後面要介紹的新版的 Trap 處理的一部分。

  這裡對裸指針解引用成立的原因在於：當前已經進入了內核地址空間，而要操作的內核棧也是在內核地址空間中的；
- 第 33~36 行，用上面的信息來創建並返回任務控制塊實例 ``task_control_block``；
- 第 38 行，查找該應用的 Trap 上下文的內核虛地址。由於應用的 Trap 上下文是在應用地址空間而不是在內核地址空間中，我們只能手動查頁表找到 Trap 上下文實際被放在的物理頁幀，然後通過之前介紹的 :ref:`在內核地址空間讀寫特定物理頁幀的能力 <access-frame-in-kernel-as>` 獲得在用戶空間的 Trap 上下文的可變引用用於初始化：

  .. code-block:: rust

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn get_trap_cx(&self) -> &'static mut TrapContext {
            self.trap_cx_ppn.get_mut()
        }
    }
  
  此處需要說明的是，返回 ``'static`` 的可變引用和之前一樣可以看成一個繞過 unsafe 的裸指針；而 ``PhysPageNum::get_mut`` 是一個泛型函數，由於我們已經聲明瞭總體返回 ``TrapContext`` 的可變引用，則Rust編譯器會給 ``get_mut`` 泛型函數針對具體類型 ``TrapContext`` 的情況生成一個特定版本的 ``get_mut`` 函數實現。在 ``get_trap_cx`` 函數中則會靜態調用 ``get_mut`` 泛型函數的特定版本實現。
- 第 39~45 行，調用 ``TrapContext::app_init_context`` 函數，通過應用的 Trap 上下文的可變引用來對其進行初始化。具體初始化過程如下所示：

  .. code-block:: rust
      :linenos:
      :emphasize-lines: 8,9,10,18,19,20

      // os/src/trap/context.rs

      impl TrapContext {
          pub fn set_sp(&mut self, sp: usize) { self.x[2] = sp; }
          pub fn app_init_context(
              entry: usize,
              sp: usize,
              kernel_satp: usize,
              kernel_sp: usize,
              trap_handler: usize,
          ) -> Self {
              let mut sstatus = sstatus::read();
              sstatus.set_spp(SPP::User);
              let mut cx = Self {
                  x: [0; 32],
                  sstatus,
                  sepc: entry,
                  kernel_satp,
                  kernel_sp,
                  trap_handler,
              };
              cx.set_sp(sp);
              cx
          }
      }

  和之前實現相比， ``TrapContext::app_init_context`` 需要補充上讓應用在 ``__alltraps`` 能夠順利進入到內核地址空間並跳轉到 trap handler 入口點的相關信息。

在內核初始化的時候，需要將所有的應用加載到全局應用管理器中：

.. code-block:: rust
    :linenos:

    // os/src/task/mod.rs

    struct TaskManagerInner {
        tasks: Vec<TaskControlBlock>,
        current_task: usize,
    }

    lazy_static! {
        pub static ref TASK_MANAGER: TaskManager = {
            println!("init TASK_MANAGER");
            let num_app = get_num_app();
            println!("num_app = {}", num_app);
            let mut tasks: Vec<TaskControlBlock> = Vec::new();
            for i in 0..num_app {
                tasks.push(TaskControlBlock::new(
                    get_app_data(i),
                    i,
                ));
            }
            TaskManager {
                num_app,
                inner: RefCell::new(TaskManagerInner {
                    tasks,
                    current_task: 0,
                }),
            }
        };
    }

可以看到，在 ``TaskManagerInner`` 中我們使用向量 ``Vec`` 來保存任務控制塊。在全局任務管理器 ``TASK_MANAGER`` 初始化的時候，只需使用 ``loader`` 子模塊提供的 ``get_num_app`` 和 ``get_app_data`` 分別獲取鏈接到內核的應用數量和每個應用的 ELF 文件格式的數據，然後依次給每個應用創建任務控制塊並加入到向量中即可。將 ``current_task`` 設置為 0 ，表示內核將從第 0 個應用開始執行。

回過頭來介紹一下應用構建器 ``os/build.rs`` 的改動：

- 首先，我們在 ``.incbin`` 中不再插入清除全部符號的應用二進制鏡像 ``*.bin`` ，而是將應用的 ELF 執行文件直接鏈接進來；
- 其次，在鏈接每個 ELF 執行文件之前我們都加入一行 ``.align 3`` 來確保它們對齊到 8 字節，這是由於如果不這樣做， ``xmas-elf`` crate 可能會在解析 ELF 的時候進行不對齊的內存讀寫，例如使用 ``ld`` 指令從內存的一個沒有對齊到 8 字節的地址加載一個 64 位的值到一個通用寄存器。而在 k210 平臺上，由於其硬件限制，這種情況會觸發一個內存讀寫不對齊的異常，導致解析無法正常完成。

為了方便後續的實現，全局任務管理器還需要提供關於當前應用與地址空間有關的一些信息：

.. code-block:: rust
    :linenos:

    // os/src/task/mod.rs

    impl TaskManager {
        fn get_current_token(&self) -> usize {
            let inner = self.inner.borrow();
            let current = inner.current_task;
            inner.tasks[current].get_user_token()
        }

        fn get_current_trap_cx(&self) -> &mut TrapContext {
            let inner = self.inner.borrow();
            let current = inner.current_task;
            inner.tasks[current].get_trap_cx()
        }
    }

    pub fn current_user_token() -> usize {
        TASK_MANAGER.get_current_token()
    }

    pub fn current_trap_cx() -> &'static mut TrapContext {
        TASK_MANAGER.get_current_trap_cx()
    }

通過 ``current_user_token`` 可以獲得當前正在執行的應用的地址空間的 token 。同時，該應用地址空間中的 Trap 上下文很關鍵，內核需要訪問它來拿到應用進行系統調用的參數並將系統調用返回值寫回，通過 ``current_trap_cx`` 內核可以拿到它訪問這個 Trap 上下文的可變引用並進行讀寫。

改進 Trap 處理的實現
------------------------------------

讓我們來看現在 ``trap_handler`` 的改進實現：

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    fn set_kernel_trap_entry() {
        unsafe {
            stvec::write(trap_from_kernel as usize, TrapMode::Direct);
        }
    }

    #[no_mangle]
    pub fn trap_from_kernel() -> ! {
        panic!("a trap from kernel!");
    }

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let cx = current_trap_cx();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            ...
        }
        trap_return();
    }

由於應用的 Trap 上下文不在內核地址空間，因此我們調用 ``current_trap_cx`` 來獲取當前應用的 Trap 上下文的可變引用而不是像之前那樣作為參數傳入 ``trap_handler`` 。至於 Trap 處理的過程則沒有發生什麼變化。

注意到，在 ``trap_handler`` 的開頭還調用 ``set_kernel_trap_entry`` 將 ``stvec`` 修改為同模塊下另一個函數 ``trap_from_kernel`` 的地址。這就是說，一旦進入內核後再次觸發到 S態 Trap，則硬件在設置一些 CSR 寄存器之後，會跳過對通用寄存器的保存過程，直接跳轉到 ``trap_from_kernel`` 函數，在這裡直接 ``panic`` 退出。這是因為內核和應用的地址空間分離之後，U態 --> S態 與 S態 --> S態 的 Trap 上下文保存與恢復實現方式/Trap 處理邏輯有很大差別。這裡為了簡單起見，弱化了 S態 --> S態的 Trap 處理過程：直接 ``panic`` 。

在 ``trap_handler`` 完成 Trap 處理之後，我們需要調用 ``trap_return`` 返回用戶態：

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    fn set_user_trap_entry() {
        unsafe {
            stvec::write(TRAMPOLINE as usize, TrapMode::Direct);
        }
    }

    #[no_mangle]
    pub fn trap_return() -> ! {
        set_user_trap_entry();
        let trap_cx_ptr = TRAP_CONTEXT;
        let user_satp = current_user_token();
        extern "C" {
            fn __alltraps();
            fn __restore();
        }
        let restore_va = __restore as usize - __alltraps as usize + TRAMPOLINE;
        unsafe {
            asm!(
                "fence.i",
                "jr {restore_va}",
                restore_va = in(reg) restore_va,
                in("a0") trap_cx_ptr,
                in("a1") user_satp,
                options(noreturn)
            );
        }
        panic!("Unreachable in back_to_user!");
    }

- 第 11 行，在 ``trap_return`` 的開始處就調用 ``set_user_trap_entry`` ，來讓應用 Trap 到 S 的時候可以跳轉到 ``__alltraps`` 。注：我們把 ``stvec`` 設置為內核和應用地址空間共享的跳板頁面的起始地址 ``TRAMPOLINE`` 而不是編譯器在鏈接時看到的 ``__alltraps`` 的地址。這是因為啟用分頁模式之後，內核只能通過跳板頁面上的虛擬地址來實際取得 ``__alltraps`` 和 ``__restore`` 的彙編代碼。
- 第 12~13 行，準備好 ``__restore`` 需要兩個參數：分別是 Trap 上下文在應用地址空間中的虛擬地址和要繼續執行的應用地址空間的 token 。
  
  最後我們需要跳轉到 ``__restore`` ，以執行：切換到應用地址空間、從 Trap 上下文中恢復通用寄存器、 ``sret`` 繼續執行應用。它的關鍵在於如何找到 ``__restore`` 在內核/應用地址空間中共同的虛擬地址。

- 第 18 行，展示了計算 ``__restore`` 虛地址的過程：由於 ``__alltraps`` 是對齊到地址空間跳板頁面的起始地址 ``TRAMPOLINE`` 上的， 則 ``__restore`` 的虛擬地址只需在 ``TRAMPOLINE`` 基礎上加上 ``__restore`` 相對於 ``__alltraps`` 的偏移量即可。這裡 ``__alltraps`` 和 ``__restore`` 都是指編譯器在鏈接時看到的內核內存佈局中的地址。


- 第 20-27 行，首先需要使用 ``fence.i`` 指令清空指令緩存 i-cache 。這是因為，在內核中進行的一些操作可能導致一些原先存放某個應用代碼的物理頁幀如今用來存放數據或者是其他應用的代碼，i-cache 中可能還保存著該物理頁幀的錯誤快照。因此我們直接將整個 i-cache 清空避免錯誤。接著使用 ``jr`` 指令完成了跳轉到 ``__restore`` 的任務。  

當每個應用第一次獲得 CPU 使用權即將進入用戶態執行的時候，它的內核棧頂放置著我們在 :ref:`內核加載應用的時候 <trap-return-intro>` 構造的一個任務上下文：

.. code-block:: rust

    // os/src/task/context.rs

    impl TaskContext {
        pub fn goto_trap_return() -> Self {
            Self {
                ra: trap_return as usize,
                s: [0; 12],
            }
        }
    }

在 ``__switch`` 切換到該應用的任務上下文的時候，內核將會跳轉到 ``trap_return`` 並返回用戶態開始該應用的啟動執行。

改進 sys_write 的實現
------------------------------------

類似Trap處理的改進，由於內核和應用地址空間的隔離， ``sys_write`` 不再能夠直接訪問位於應用空間中的數據，而需要手動查頁表才能知道那些數據被放置在哪些物理頁幀上並進行訪問。

為此，頁表模塊 ``page_table`` 提供了將應用地址空間中一個緩衝區轉化為在內核空間中能夠直接訪問的形式的輔助函數：

.. code-block:: rust
    :linenos:

    // os/src/mm/page_table.rs

    pub fn translated_byte_buffer(
        token: usize,
        ptr: *const u8,
        len: usize
    ) -> Vec<&'static [u8]> {
        let page_table = PageTable::from_token(token);
        let mut start = ptr as usize;
        let end = start + len;
        let mut v = Vec::new();
        while start < end {
            let start_va = VirtAddr::from(start);
            let mut vpn = start_va.floor();
            let ppn = page_table
                .translate(vpn)
                .unwrap()
                .ppn();
            vpn.step();
            let mut end_va: VirtAddr = vpn.into();
            end_va = end_va.min(VirtAddr::from(end));
            if end_va.page_offset() == 0 {
                v.push(&mut ppn.get_bytes_array()[start_va.page_offset()..]);
            } else {
                v.push(&mut ppn.get_bytes_array()[start_va.page_offset()..end_va.page_offset()]);
            }
            start = end_va.into();
        }
        v
    }

參數中的 ``token`` 是某個應用地址空間的 token ， ``ptr`` 和 ``len`` 則分別表示該地址空間中的一段緩衝區的起始地址和長度(注：這個緩衝區的應用虛擬地址範圍是連續的)。 ``translated_byte_buffer`` 會以向量的形式返回一組可以在內核空間中直接訪問的字節數組切片（注：這個緩衝區的內核虛擬地址範圍有可能是不連續的），具體實現在這裡不再贅述。

進而我們可以完成對 ``sys_write`` 系統調用的改造：

.. code-block:: rust

    // os/src/syscall/fs.rs

    pub fn sys_write(fd: usize, buf: *const u8, len: usize) -> isize {
        match fd {
            FD_STDOUT => {
                let buffers = translated_byte_buffer(current_user_token(), buf, len);
                for buffer in buffers {
                    print!("{}", core::str::from_utf8(buffer).unwrap());
                }
                len as isize
            },
            _ => {
                panic!("Unsupported fd in sys_write!");
            }
        }
    }

上述函數嘗試將按應用的虛地址指向的緩衝區轉換為一組按內核虛地址指向的字節數組切片構成的向量，然後把每個字節數組切片轉化為字符串``&str`` 然後輸出即可。



小結
-------------------------------------

這一章內容很多，講解了 **地址空間** 這一抽象概念是如何在一個具體的“頭甲龍”操作系統中實現的。這裡面的核心內容是如何建立基於頁表機制的虛擬地址空間。為此，操作系統需要知道並管理整個系統中的物理內存；需要建立虛擬地址到物理地址映射關係的頁表；並基於頁表給操作系統自身和每個應用提供一個虛擬地址空間；並需要對管理應用的任務控制塊進行擴展，確保能對應用的地址空間進行管理；由於應用和內核的地址空間是隔離的，需要有一個跳板來幫助完成應用與內核之間的切換執行；並導致了對異常、中斷、系統調用的相應更改。這一系列的改進，最終的效果是編寫應用更加簡單了，且應用的執行或錯誤不會影響到內核和其他應用的正常工作。為了得到這些好處，我們需要比較費勁地進化我們的操作系統。如果同學結合閱讀代碼，編譯並運行應用+內核，讀懂了上面的文檔，那完成本章的實驗就有了一個堅實的基礎。

如果同學能想明白如何插入/刪除頁表；如何在 ``trap_handler`` 下處理 ``LoadPageFault`` ；以及 ``sys_get_time`` 在使能頁機制下如何實現，那就會發現下一節的實驗練習也許 **就和lab1一樣** 。

.. [#tutus] 頭甲龍最早出現在1.8億年以前的侏羅紀中期，是身披重甲的食素恐龍，尾巴末端的尾錘，是防身武器。
