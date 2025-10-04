管理 SV39 多級頁表
========================================================


本節導讀
--------------------------


上一節更多的是站在硬件的角度來分析SV39多級頁表的硬件機制，本節我們主要講解基於 SV39 多級頁表機制的操作系統內存管理。這還需進一步管理計算機系統中當前已經使用的或空閒的物理頁幀，這樣操作系統才能給應用程序動態分配或回收物理地址空間。有了有效的物理內存空間的管理，操作系統就能夠在物理內存空間中建立多級頁表（頁表佔用物理內存），為應用程序和操作系統自身建立虛實地址映射關係，從而實現虛擬內存空間，即給應用“看到”的地址空間。


.. _term-manage-phys-frame:

物理頁幀管理
-----------------------------------

從前面的介紹可以看出物理頁幀的重要性：它既可以用來實際存放應用/內核的數據/代碼，也能夠用來存儲應用/內核的多級頁表。當Bootloader把操作系統內核加載到物理內存中後，物理內存上已經有一部分用於放置內核的代碼和數據。我們需要將剩下的空閒內存以單個物理頁幀為單位管理起來，當需要存放應用數據或擴展應用的多級頁表時分配空閒的物理頁幀，並在應用出錯或退出的時候回收應用佔有的所有物理頁幀。

可用物理頁的分配與回收
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

首先，我們需要知道物理內存的哪一部分是可用的。在 ``os/src/linker.ld`` 中，我們用符號 ``ekernel`` 指明瞭內核數據的終止物理地址，在它之後的物理內存都是可用的。而在 ``config`` 子模塊中：

.. code-block:: rust

    // os/src/config.rs

    pub const MEMORY_END: usize = 0x80800000;

我們硬編碼整塊物理內存的終止物理地址為 ``0x80800000`` 。 而 :ref:`之前 <term-physical-memory>` 提到過物理內存的起始物理地址為 ``0x80000000`` ，這意味著我們將可用內存大小設置為 :math:`8\text{MiB}` 。實際上在 Qemu 模擬器上可以通過設置使用更大的物理內存，但這裡我們希望它和真實硬件 K210 的配置保持一致，因此設置為僅使用 :math:`8\text{MiB}` 。我們用一個左閉右開的物理頁號區間來表示可用的物理內存，則：

- 區間的左端點應該是 ``ekernel`` 的物理地址以上取整方式轉化成的物理頁號；
- 區間的右端點應該是 ``MEMORY_END`` 以下取整方式轉化成的物理頁號。

這個區間將被傳給我們後面實現的物理頁幀管理器用於初始化。

我們聲明一個 ``FrameAllocator`` Trait 來描述一個物理頁幀管理器需要提供哪些功能：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    trait FrameAllocator {
        fn new() -> Self;
        fn alloc(&mut self) -> Option<PhysPageNum>;
        fn dealloc(&mut self, ppn: PhysPageNum);
    }

即創建一個物理頁幀管理器的實例，以及以物理頁號為單位進行物理頁幀的分配和回收。

我們實現一種最簡單的棧式物理頁幀管理策略 ``StackFrameAllocator`` ：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    pub struct StackFrameAllocator {
        current: usize,  //空閒內存的起始物理頁號
        end: usize,      //空閒內存的結束物理頁號
        recycled: Vec<usize>,
    }

其中各字段的含義是：物理頁號區間 [ ``current`` , ``end`` ) 此前均 *從未* 被分配出去過，而向量 ``recycled`` 以後入先出的方式保存了被回收的物理頁號（注：我們已經自然的將內核堆用起來了）。

初始化非常簡單。在通過 ``FrameAllocator`` 的 ``new`` 方法創建實例的時候，只需將區間兩端均設為 :math:`0` ，然後創建一個新的向量；而在它真正被使用起來之前，需要調用 ``init`` 方法將自身的 :math:`[\text{current},\text{end})` 初始化為可用物理頁號區間：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    impl FrameAllocator for StackFrameAllocator {
        fn new() -> Self {
            Self {
                current: 0,
                end: 0,
                recycled: Vec::new(),
            }
        }
    }

    impl StackFrameAllocator {
        pub fn init(&mut self, l: PhysPageNum, r: PhysPageNum) {
            self.current = l.0;
            self.end = r.0;
        }
    }

接下來我們來看核心的物理頁幀分配和回收如何實現：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    impl FrameAllocator for StackFrameAllocator {
        fn alloc(&mut self) -> Option<PhysPageNum> {
            if let Some(ppn) = self.recycled.pop() {
                Some(ppn.into())
            } else {
                if self.current == self.end {
                    None
                } else {
                    self.current += 1;
                    Some((self.current - 1).into())
                }
            }
        }
        fn dealloc(&mut self, ppn: PhysPageNum) {
            let ppn = ppn.0;
            // validity check
            if ppn >= self.current || self.recycled
                .iter()
                .find(|&v| {*v == ppn})
                .is_some() {
                panic!("Frame ppn={:#x} has not been allocated!", ppn);
            }
            // recycle
            self.recycled.push(ppn);
        }
    }

- 在分配 ``alloc`` 的時候，首先會檢查棧 ``recycled`` 內有沒有之前回收的物理頁號，如果有的話直接彈出棧頂並返回；否則的話我們只能從之前從未分配過的物理頁號區間 [ ``current`` , ``end`` ) 上進行分配，我們分配它的左端點 ``current`` ，同時將管理器內部維護的 ``current`` 加 ``1`` 代表 ``current`` 已被分配了。在即將返回的時候，我們使用 ``into`` 方法將 usize 轉換成了物理頁號 ``PhysPageNum`` 。

  注意極端情況下可能出現內存耗盡分配失敗的情況：即 ``recycled`` 為空且  ``current`` == ``end`` 。為了涵蓋這種情況， ``alloc`` 的返回值被 ``Option`` 包裹，我們返回 ``None`` 即可。
- 在回收 ``dealloc`` 的時候，我們需要檢查回收頁面的合法性，然後將其壓入 ``recycled`` 棧中。回收頁面合法有兩個條件：

  - 該頁面之前一定被分配出去過，因此它的物理頁號一定 :math:`<` ``current`` ；
  - 該頁面沒有正處在回收狀態，即它的物理頁號不能在棧 ``recycled`` 中找到。

  我們通過 ``recycled.iter()`` 獲取棧上內容的迭代器，然後通過迭代器的 ``find`` 方法試圖尋找一個與輸入物理頁號相同的元素。其返回值是一個 ``Option`` ，如果找到了就會是一個 ``Option::Some`` ，這種情況說明我們內核其他部分實現有誤，直接報錯退出。

下面我們來創建 ``StackFrameAllocator`` 的全局實例 ``FRAME_ALLOCATOR`` ：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    use crate::sync::UPSafeCell;
    type FrameAllocatorImpl = StackFrameAllocator;
    lazy_static! {
        pub static ref FRAME_ALLOCATOR: UPSafeCell<FrameAllocatorImpl> = unsafe {
            UPSafeCell::new(FrameAllocatorImpl::new())
        };
    }

這裡我們使用 ``UPSafeCell<T>`` 來包裹棧式物理頁幀分配器。每次對該分配器進行操作之前，我們都需要先通過 ``FRAME_ALLOCATOR.exclusive_access()`` 拿到分配器的可變借用。

.. chyyuu
    注意 ``alloc`` 中並沒有提供 ``Mutex<T>`` ，它
    來自於一個我們在 ``no_std`` 的裸機環境下經常使用的名為 ``spin`` 的 crate ，它僅依賴 Rust 核心庫 
    ``core`` 提供一些可跨平臺使用的同步原語，如互斥鎖 ``Mutex<T>`` 和讀寫鎖 ``RwLock<T>`` 等。

.. 現在前面已經講到了

    **Rust Tips：在單核環境下采用 UPSafeCell<T> 而沒有采用 Mutex<T> 的原因**

    在編寫一個多線程的Rust應用時，一般會通過 Mutex<T> 來包裹數據，並對數據訪問進行加鎖互斥保護，加鎖的目的是為了避免數據競爭，使得裡層的共享數據結構同一時間只有一個線程
    在對它進行訪問。然而，目前我們的內核運行在單 CPU 上，且 Trap 進入內核之後並沒有手動打開中斷，這也就
    使得同一時間最多隻有一條 Trap 控制流併發訪問內核的各數據結構，此時應該是並沒有任何數據競爭風險，所以我們基於更簡單的 ``RefCell<T>`` 實現了 ``UPSafeCell<T>`` 來支持對全局變量的安全訪問，支持在不觸及 ``unsafe`` 的情況下實現 ``static mut`` 語義。

    注：這裡引入了一些新概念，比如線程，互斥訪問、數據競爭等。同學可以先不必深究，暫時有一個初步的概念即可，在後續章節會有進一步深入講解。


.. chyyuu
    。所以那麼
    加鎖的原因其實有兩點：

    1. 在不觸及 ``unsafe`` 的情況下實現 ``static mut`` 語義。如果同學還有印象， 
       :ref:`前面章節 <term-interior-mutability>` 我們使用 ``RefCell<T>`` 提供了內部可變性去掉了
       聲明中的 ``mut`` ，然而麻煩的在於 ``static`` ，在 Rust 中一個類型想被實例化為一個全局變量，則
       該類型必須先告知編譯器自己某種意義上是線程安全的，這個過程本身是 ``unsafe`` 的。

       因此我們直接使用 ``Mutex<T>`` ，它既通過 ``lock`` 方法提供了內部可變性，又已經在模塊內部告知了
       編譯器它的線程安全性。這樣 ``unsafe`` 就被隱藏在了 ``spin`` crate 之內，我們無需關心。這種風格
       是 Rust 所推薦的。
    2. 方便後續拓展到真正存在數據競爭風險的多核環境下運行。

    這裡引入了一些新概念，比如什麼是線程，又如何定義線程安全？同學可以先不必深究，暫時有一個初步的概念即可。

在正式分配物理頁幀之前，我們需要將物理頁幀全局管理器 ``FRAME_ALLOCATOR`` 初始化：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    pub fn init_frame_allocator() {
        extern "C" {
            fn ekernel();
        }
        FRAME_ALLOCATOR
            .exclusive_access()
            .init(PhysAddr::from(ekernel as usize).ceil(), PhysAddr::from(MEMORY_END).floor());
    }

這裡我們調用物理地址 ``PhysAddr`` 的 ``floor/ceil`` 方法分別下/上取整獲得可用的物理頁號區間。


分配/回收物理頁幀的接口
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

然後是公開給其他內核模塊調用的分配/回收物理頁幀的接口：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    pub fn frame_alloc() -> Option<FrameTracker> {
        FRAME_ALLOCATOR
            .exclusive_access()
            .alloc()
            .map(|ppn| FrameTracker::new(ppn))
    }

    fn frame_dealloc(ppn: PhysPageNum) {
        FRAME_ALLOCATOR
            .exclusive_access()
            .dealloc(ppn);
    }

可以發現， ``frame_alloc`` 的返回值類型並不是 ``FrameAllocator`` 要求的物理頁號 ``PhysPageNum`` ，而是將其進一步包裝為一個 ``FrameTracker`` 。這裡借用了 RAII 的思想，將一個物理頁幀的生命週期綁定到一個 ``FrameTracker`` 變量上，當一個 ``FrameTracker`` 被創建的時候，我們需要從 ``FRAME_ALLOCATOR`` 中分配一個物理頁幀：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    pub struct FrameTracker {
        pub ppn: PhysPageNum,
    }

    impl FrameTracker {
        pub fn new(ppn: PhysPageNum) -> Self {
            // page cleaning
            let bytes_array = ppn.get_bytes_array();
            for i in bytes_array {
                *i = 0;
            }
            Self { ppn }
        }
    }

我們將分配來的物理頁幀的物理頁號作為參數傳給 ``FrameTracker`` 的 ``new`` 方法來創建一個 ``FrameTracker`` 
實例。由於這個物理頁幀之前可能被分配過並用做其他用途，我們在這裡直接將這個物理頁幀上的所有字節清零。這一過程並不
那麼顯然，我們後面再詳細介紹。

當一個 ``FrameTracker`` 生命週期結束被編譯器回收的時候，我們需要將它控制的物理頁幀回收到 ``FRAME_ALLOCATOR`` 中：

.. code-block:: rust

    // os/src/mm/frame_allocator.rs

    impl Drop for FrameTracker {
        fn drop(&mut self) {
            frame_dealloc(self.ppn);
        }
    }

這裡我們只需為 ``FrameTracker`` 實現 ``Drop`` Trait 即可。當一個 ``FrameTracker`` 實例被回收的時候，它的 ``drop`` 方法會自動被編譯器調用，通過之前實現的 ``frame_dealloc`` 我們就將它控制的物理頁幀回收以供後續使用了。

.. note::

    **Rust Tips：Drop Trait**

    Rust 中的 ``Drop`` Trait 是它的 RAII 內存管理風格可以被有效實踐的關鍵。之前介紹的多種在堆上分配的 Rust 數據結構便都是通過實現 ``Drop`` Trait 來進行被綁定資源的自動回收的。例如：

    - ``Box<T>`` 的 ``drop`` 方法會回收它控制的分配在堆上的那個變量；
    - ``Rc<T>`` 的 ``drop`` 方法會減少分配在堆上的那個引用計數，一旦變為零則分配在堆上的那個被計數的變量自身也會被回收；
    - ``UPSafeCell<T>`` 的 ``exclusive_access`` 方法會獲取內部數據結構的獨佔借用權並返回一個 ``RefMut<'a, T>`` （實際上來自 ``RefCell<T>`` ），它可以被當做一個 ``&mut T`` 來使用；而 ``RefMut<'a, T>`` 的 ``drop`` 方法會將獨佔借用權交出，從而允許內核內的其他控制流後續對數據結構進行訪問。

    ``FrameTracker`` 的設計也是基於同樣的思想，有了它之後我們就不必手動回收物理頁幀了，這在編譯期就解決了很多潛在的問題。

最後做一個小結：從其他內核模塊的視角看來，物理頁幀分配的接口是調用 ``frame_alloc`` 函數得到一個 ``FrameTracker`` （如果物理內存還有剩餘），它就代表了一個物理頁幀，當它的生命週期結束之後它所控制的物理頁幀將被自動回收。下面是一段演示該接口使用方法的測試程序：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 9

    // os/src/mm/frame_allocator.rs

    #[allow(unused)]
    pub fn frame_allocator_test() {
        let mut v: Vec<FrameTracker> = Vec::new();
        for i in 0..5 {
            let frame = frame_alloc().unwrap();
            println!("{:?}", frame);
            v.push(frame);
        }
        v.clear();
        for i in 0..5 {
            let frame = frame_alloc().unwrap();
            println!("{:?}", frame);
            v.push(frame);
        }
        drop(v);
        println!("frame_allocator_test passed!");
    }

如果我們將第 9 行刪去，則第一輪分配的 5 個物理頁幀都是分配之後在循環末尾就被立即回收，因為循環作用域的臨時變量 ``frame`` 的生命週期在那時結束了。然而，如果我們將它們 move 到一個向量中，它們的生命週期便被延長了——直到第 11 行向量被清空的時候，這些 ``FrameTracker`` 的生命週期才結束，它們控制的 5 個物理頁幀才被回收。這種思想我們立即就會用到。

多級頁表管理
-----------------------------------


頁表基本數據結構與訪問接口
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

我們知道，SV39 多級頁表是以節點為單位進行管理的。每個節點恰好存儲在一個物理頁幀中，它的位置可以用一個物理頁號來表示。

.. code-block:: rust
    :linenos:

    // os/src/mm/page_table.rs

    pub struct PageTable {
        root_ppn: PhysPageNum,
        frames: Vec<FrameTracker>,
    }

    impl PageTable {
        pub fn new() -> Self {
            let frame = frame_alloc().unwrap();
            PageTable {
                root_ppn: frame.ppn,
                frames: vec![frame],
            }
        }
    }

每個應用的地址空間都對應一個不同的多級頁表，這也就意味這不同頁表的起始地址（即頁表根節點的地址）是不一樣的。因此 ``PageTable`` 要保存它根節點的物理頁號 ``root_ppn`` 作為頁表唯一的區分標誌。此外，向量 ``frames`` 以 ``FrameTracker`` 的形式保存了頁表所有的節點（包括根節點）所在的物理頁幀。這與物理頁幀管理模塊的測試程序是一個思路，即將這些 ``FrameTracker`` 的生命週期進一步綁定到 ``PageTable`` 下面。當 ``PageTable`` 生命週期結束後，向量 ``frames`` 裡面的那些 ``FrameTracker`` 也會被回收，也就意味著存放多級頁表節點的那些物理頁幀被回收了。

當我們通過 ``new`` 方法新建一個 ``PageTable`` 的時候，它只需有一個根節點。為此我們需要分配一個物理頁幀 ``FrameTracker`` 並掛在向量 ``frames`` 下，然後更新根節點的物理頁號 ``root_ppn`` 。

多級頁表並不是被創建出來之後就不再變化的，為了 MMU 能夠通過地址轉換正確找到應用地址空間中的數據實際被內核放在內存中位置，操作系統需要動態維護一個虛擬頁號到頁表項的映射，支持插入/刪除鍵值對，其方法簽名如下：

.. code-block:: rust

    // os/src/mm/page_table.rs

    impl PageTable {
        pub fn map(&mut self, vpn: VirtPageNum, ppn: PhysPageNum, flags: PTEFlags);
        pub fn unmap(&mut self, vpn: VirtPageNum);
    }

- 通過 ``map`` 方法來在多級頁表中插入一個鍵值對，注意這裡將物理頁號 ``ppn`` 和頁表項標誌位 ``flags`` 作為不同的參數傳入；
- 通過 ``unmap`` 方法來刪除一個鍵值對，在調用時僅需給出作為索引的虛擬頁號即可。

.. _modify-page-table:

在上述操作的過程中，內核需要能訪問或修改多級頁表節點的內容。即在操作某個多級頁表或管理物理頁幀的時候，操作系統要能夠讀寫與一個給定的物理頁號對應的物理頁幀上的數據。這是因為，在多級頁表的架構中，每個節點都被保存在一個物理頁幀中，一個節點所在物理頁幀的物理頁號其實就是指向該節點的“指針”。

在尚未啟用分頁模式之前，內核和應用的代碼都可以通過物理地址直接訪問內存。而在打開分頁模式之後，運行在 S 特權級的內核與運行在 U 特權級的應用在訪存上都會受到影響，它們的訪存地址會被視為一個當前地址空間（ ``satp`` CSR 給出當前多級頁表根節點的物理頁號）中的一個虛擬地址，需要 MMU 查相應的多級頁表完成地址轉換變為物理地址，即地址空間中虛擬地址指向的數據真正被內核放在的物理內存中的位置，然後才能訪問相應的數據。此時，如果想要訪問一個特定的物理地址 ``pa`` 所指向的內存上的數據，就需要 **構造** 對應的一個虛擬地址 ``va`` ，使得當前地址空間的頁表存在映射 :math:`\text{va}\rightarrow\text{pa}` ，且頁表項中的保護位允許這種訪問方式。於是，在代碼中我們只需訪問地址 ``va`` ，它便會被 MMU 通過地址轉換變成 ``pa`` ，這樣我們就做到了在啟用分頁模式的情況下也能正常訪問內存。

.. _term-identical-mapping:

這就需要提前擴充多級頁表維護的映射，讓每個物理頁幀的物理頁號 ``ppn`` ，均存在一個對應的虛擬頁號 ``vpn`` ，這需要建立一種映射關係。這裡我們採用一種最簡單的 **恆等映射** (Identical Mapping) ，即對於物理內存上的每個物理頁幀，我們都在多級頁表中用一個與其物理頁號相等的虛擬頁號來映射。

.. _term-recursive-mapping:

.. note::

    **其他的映射方式**

    為了達到這一目的還存在其他不同的映射方式，例如比較著名的 **頁表自映射** (Recursive Mapping) 等。有興趣的同學
    可以進一步參考 `BlogOS 中的相關介紹 <https://os.phil-opp.com/paging-implementation/#accessing-page-tables>`_ 。

這裡需要說明的是，在下一節中我們可以看到，應用和內核的地址空間是隔離的。而直接訪問物理頁幀的操作只會在內核中進行，應用無法看到物理頁幀管理器和多級頁表等內核數據結構。因此，上述的恆等映射只需被附加到內核地址空間即可。


內核中訪問物理頁幀的方法
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _access-frame-in-kernel-as:


於是，我們來看看在內核中應如何訪問一個特定的物理頁幀：

.. code-block:: rust

    // os/src/mm/address.rs

    impl PhysPageNum {
        pub fn get_pte_array(&self) -> &'static mut [PageTableEntry] {
            let pa: PhysAddr = self.clone().into();
            unsafe {
                core::slice::from_raw_parts_mut(pa.0 as *mut PageTableEntry, 512)
            }
        }
        pub fn get_bytes_array(&self) -> &'static mut [u8] {
            let pa: PhysAddr = self.clone().into();
            unsafe {
                core::slice::from_raw_parts_mut(pa.0 as *mut u8, 4096)
            }
        }
        pub fn get_mut<T>(&self) -> &'static mut T {
            let pa: PhysAddr = self.clone().into();
            unsafe {
                (pa.0 as *mut T).as_mut().unwrap()
            }
        }
    }

我們構造可變引用來直接訪問一個物理頁號 ``PhysPageNum`` 對應的物理頁幀，不同的引用類型對應於物理頁幀上的一種不同的內存佈局，如 ``get_pte_array`` 返回的是一個頁表項定長數組的可變引用，代表多級頁表中的一個節點；而 ``get_bytes_array`` 返回的是一個字節數組的可變引用，可以以字節為粒度對物理頁幀上的數據進行訪問，前面進行數據清零就用到了這個方法； ``get_mut`` 是個泛型函數，可以獲取一個恰好放在一個物理頁幀開頭的類型為 ``T`` 的數據的可變引用。

在實現方面，都是先把物理頁號轉為物理地址 ``PhysAddr`` ，然後再轉成 usize 形式的物理地址。接著，我們直接將它轉為裸指針用來訪問物理地址指向的物理內存。在分頁機制開啟前，這樣做自然成立；而開啟之後，雖然裸指針被視為一個虛擬地址，但是上面已經提到，基於恆等映射，虛擬地址會映射到一個相同的物理地址，因此在也是成立的。注意，我們在返回值類型上附加了靜態生命週期泛型 ``'static`` ，這是為了繞過 Rust 編譯器的借用檢查，實質上可以將返回的類型也看成一個裸指針，因為它也只是標識數據存放的位置以及類型。但與裸指針不同的是，無需通過 ``unsafe`` 的解引用訪問它指向的數據，而是可以像一個正常的可變引用一樣直接訪問。

.. note::
    
    **unsafe 真的就是“不安全”嗎？**

    下面是筆者關於 unsafe 一點較為深入的討論，不感興趣的同學可以跳過。

    當我們在 Rust 中使用 unsafe 的時候，並不僅僅是為了繞過編譯器檢查，更是為了告知編譯器和其他看到這段代碼的程序員：“ **我保證這樣做是安全的** ” 。儘管，嚴格的 Rust 編譯器暫時還不能確信這一點。從規範 Rust 代碼編寫的角度，我們需要儘可能繞過 unsafe ，因為如果 Rust 編譯器或者一些已有的接口就可以提供安全性，我們當然傾向於利用它們讓我們實現的功能仍然是安全的，可以避免一些無謂的心智負擔；反之，就只能使用 unsafe ，同時最好說明如何保證這項功能是安全的。

    這裡簡要從內存安全的角度來分析一下 ``PhysPageNum`` 的 ``get_*`` 系列方法的實現中 ``unsafe`` 的使用。首先需要指出的是，當需要訪問一個物理頁幀的時候，我們需要從它被綁定到的 ``FrameTracker`` 中獲得其物理頁號 ``PhysPageNum`` 隨後再調用 ``get_*`` 系列方法才能訪問物理頁幀。因此， ``PhysPageNum`` 介於 ``FrameTracker`` 和物理頁幀之間，也可以看做擁有部分物理頁幀的所有權。由於 ``get_*`` 返回的是引用，我們可以嘗試檢查引用引發的常見問題：第一個問題是 use-after-free 的問題，即是否存在 ``get_*`` 返回的引用存在期間被引用的物理頁幀已被回收的情形；第二個問題則是注意到 ``get_*`` 返回的是可變引用，那麼就需要考慮對物理頁幀的訪問讀寫衝突的問題。

    為了解決這些問題，我們在編寫代碼的時候需要額外當心。對於每一段 unsafe 代碼，我們都需要認真考慮它會對其他無論是 unsafe 還是 safe 的代碼造成的潛在影響。比如為了避免第一個問題，我們需要保證當完成物理頁幀訪問之後便立即回收掉 ``get_*`` 返回的引用，至少使它不能超出 ``FrameTracker`` 的生命週期；考慮第二個問題，目前每個 ``FrameTracker`` 僅會出現一次（在它所屬的進程中），因此它只會出現在一個上下文中，也就不會產生衝突。但是當內核態打開（允許）中斷時，或內核支持在單進程中存在多個線程時，情況也許又會發生變化。

    當編譯器不能介入的時候，我們很難完美的解決這些問題。因此重新設計數據結構和接口，特別是考慮數據的所有權關係，將建模進行轉換，使得 Rust 有能力檢查我們的設計會是一種更明智的選擇。這也可以說明為什麼要儘量避免使用 unsafe 。事實上，我們目前 ``PhysPageNum::get_*`` 接口並非一個好的設計，如果同學有興趣可以試著對設計進行改良，讓 Rust 編譯器幫助我們解決上述與引用相關的問題。
    
.. _term-create-pagetable:

建立和拆除虛實地址映射關係
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

接下來介紹建立和拆除虛實地址映射關係的 ``map`` 和 ``unmap`` 方法是如何實現的。它們都依賴於一個很重要的過程，即在多級頁表中找到一個虛擬地址對應的頁表項。找到之後，只要修改頁表項的內容即可完成鍵值對的插入和刪除。在尋找頁表項的時候，可能出現頁表的中間級節點還未被創建的情況，這個時候我們需要手動分配一個物理頁幀來存放這個節點，並將這個節點接入到當前的多級頁表的某級中。


.. code-block:: rust
    :linenos:

    // os/src/mm/address.rs

    impl VirtPageNum {
        pub fn indexes(&self) -> [usize; 3] {
            let mut vpn = self.0;
            let mut idx = [0usize; 3];
            for i in (0..3).rev() {
                idx[i] = vpn & 511;
                vpn >>= 9;
            }
            idx
        }
    }

    // os/src/mm/page_table.rs

    impl PageTable {
        fn find_pte_create(&mut self, vpn: VirtPageNum) -> Option<&mut PageTableEntry> {
            let idxs = vpn.indexes();
            let mut ppn = self.root_ppn;
            let mut result: Option<&mut PageTableEntry> = None;
            for i in 0..3 {
                let pte = &mut ppn.get_pte_array()[idxs[i]];
                if i == 2 {
                    result = Some(pte);
                    break;
                }
                if !pte.is_valid() {
                    let frame = frame_alloc().unwrap();
                    *pte = PageTableEntry::new(frame.ppn, PTEFlags::V);
                    self.frames.push(frame);
                }
                ppn = pte.ppn();
            }
            result
        }
        fn find_pte(&self, vpn: VirtPageNum) -> Option<&mut PageTableEntry> {
            let idxs = vpn.indexes();
            let mut ppn = self.root_ppn;
            let mut result: Option<&mut PageTableEntry> = None;
            for i in 0..3 {
                let pte = &mut ppn.get_pte_array()[idxs[i]];
                if i == 2 {
                    result = Some(pte);
                    break;
                }
                if !pte.is_valid() {
                    return None;
                }
                ppn = pte.ppn();
            }
            result
        }
    }

- ``VirtPageNum`` 的 ``indexes`` 可以取出虛擬頁號的三級頁索引，並按照從高到低的順序返回。注意它裡面包裹的 usize 可能有 :math:`27` 位，也有可能有 :math:`64-12=52` 位，但這裡我們是用來在多級頁表上進行遍歷，因此只取出低 :math:`27` 位。
- ``PageTable::find_pte_create`` 在多級頁表找到一個虛擬頁號對應的頁表項的可變引用。如果在遍歷的過程中發現有節點尚未創建則會新建一個節點。

  變量 ``ppn`` 表示當前節點的物理頁號，最開始指向多級頁表的根節點。隨後每次循環通過 ``get_pte_array`` 將取出當前節點的頁表項數組，並根據當前級頁索引找到對應的頁表項。如果當前節點是一個葉節點，那麼直接返回這個頁表項的可變引用；否則嘗試向下走。走不下去的話就新建一個節點，更新作為下級節點指針的頁表項，並將新分配的物理頁幀移動到向量 ``frames`` 中方便後續的自動回收。注意在更新頁表項的時候，不僅要更新物理頁號，還要將標誌位 V 置 1，不然硬件在查多級頁表的時候，會認為這個頁表項不合法，從而觸發 Page Fault 而不能向下走。
- ``PageTable::find_pte`` 與 ``find_pte_create`` 的不同在於當找不到合法葉子節點的時候不會新建葉子節點而是直接返回 ``None`` 即查找失敗。因此，它不會嘗試對頁表本身進行修改，但是注意它返回的參數類型是頁表項的可變引用，也即它允許我們修改頁表項。從 ``find_pte`` 的實現還可以看出，即使找到的頁表項不合法，還是會將其返回回去而不是返回 ``None`` 。這說明在目前的實現中，頁表和頁表項是相對解耦合的。

於是， ``map/unmap`` 就非常容易實現了：

.. code-block:: rust

    // os/src/mm/page_table.rs

    impl PageTable {
        pub fn map(&mut self, vpn: VirtPageNum, ppn: PhysPageNum, flags: PTEFlags) {
            let pte = self.find_pte_create(vpn).unwrap();
            assert!(!pte.is_valid(), "vpn {:?} is mapped before mapping", vpn);
            *pte = PageTableEntry::new(ppn, flags | PTEFlags::V);
        }
        pub fn unmap(&mut self, vpn: VirtPageNum) {
            let pte = self.find_pte(vpn).unwrap();
            assert!(pte.is_valid(), "vpn {:?} is invalid before unmapping", vpn);
            *pte = PageTableEntry::empty();
        }
    }

只需根據虛擬頁號找到頁表項，然後修改或者直接清空其內容即可。

.. warning::

    目前的實現方式並不打算對物理頁幀耗盡的情形做任何處理而是直接 ``panic`` 退出。因此在前面的代碼中能夠看到很多 ``unwrap`` ，這種使用方式並不為 Rust 所推薦，只是由於簡單起見暫且這樣做。

為了方便後面的實現，我們還需要 ``PageTable`` 提供一種類似 MMU 操作的手動查頁表的方法：

.. code-block:: rust
    :linenos:

    // os/src/mm/page_table.rs

    impl PageTable {
        /// Temporarily used to get arguments from user space.
        pub fn from_token(satp: usize) -> Self {
            Self {
                root_ppn: PhysPageNum::from(satp & ((1usize << 44) - 1)),
                frames: Vec::new(),
            }
        }
        pub fn translate(&self, vpn: VirtPageNum) -> Option<PageTableEntry> {
            self.find_pte(vpn)
                .map(|pte| {pte.clone()})
        }
    }

- 第 5 行的 ``from_token`` 可以臨時創建一個專用來手動查頁表的 ``PageTable`` ，它僅有一個從傳入的 ``satp`` token 中得到的多級頁表根節點的物理頁號，它的 ``frames`` 字段為空，也即不實際控制任何資源；
- 第 11 行的 ``translate`` 調用 ``find_pte`` 來實現，如果能夠找到頁表項，那麼它會將頁表項拷貝一份並返回，否則就返回一個 ``None`` 。

之後，當遇到需要查一個特定頁表（非當前正處在的地址空間的頁表時），便可先通過 ``PageTable::from_token`` 新建一個頁表，再調用它的 ``translate`` 方法查頁表。

小結一下，上一節和本節講解了如何基於 RISC-V64 的 SV39 分頁機制建立多級頁表，並實現基於虛存地址空間的內存使用環境。這樣，一旦啟用分頁機制，操作系統和應用都只能在虛擬地址空間中訪問數據了，只是操作系統可以通過頁表機制來限制應用訪問的實際物理內存範圍。這就要在後續小節中，進一步看看操作系統內核和應用程序是如何在虛擬地址空間中進行代碼和數據訪問的。