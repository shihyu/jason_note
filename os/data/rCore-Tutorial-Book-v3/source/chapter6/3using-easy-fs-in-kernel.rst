在內核中接入 easy-fs
===============================================

本節導讀
-----------------------------------------------

上節實現了 ``easy-fs`` 文件系統，並能在用戶態來進行測試，但還沒有放入到內核中來。本節我們介紹如何將 ``easy-fs`` 文件系統接入內核中從而在內核中支持常規文件和目錄。為此，在操作系統內核中需要有對接 ``easy-fs`` 文件系統的各種結構，它們自下而上可以分成這樣幾個層次：

- 塊設備驅動層：針對內核所要運行在的 qemu 或 k210 平臺，我們需要將平臺上的塊設備驅動起來並實現 ``easy-fs`` 所需的 ``BlockDevice`` Trait ，這樣 ``easy-fs`` 才能將該塊設備用作 easy-fs 鏡像的載體。
- ``easy-fs`` 層：我們在上一節已經介紹了 ``easy-fs`` 文件系統內部的層次劃分。這裡是站在內核的角度，只需知道它接受一個塊設備 ``BlockDevice`` ，並可以在上面打開文件系統 ``EasyFileSystem`` ，進而獲取 ``Inode`` 核心數據結構，進行各種文件系統操作即可。
- 內核索引節點層：在內核中需要將 ``easy-fs`` 提供的 ``Inode`` 進一步封裝成 ``OSInode`` ，以表示進程中一個打開的常規文件。由於有很多種不同的打開方式，因此在 ``OSInode`` 中要維護一些額外的信息。
- 文件描述符層：常規文件對應的 ``OSInode`` 是文件的內核內部表示，因此需要為它實現 ``File`` Trait 從而能夠可以將它放入到進程文件描述符表中並通過 ``sys_read/write`` 系統調用進行讀寫。
- 系統調用層：由於引入了常規文件這種文件類型，導致一些系統調用以及相關的內核機制需要進行一定的修改。


文件簡介
-------------------------------------------

應用程序看到並被操作系統管理的 **文件** (File) 就是一系列的字節組合。操作系統不關心文件內容，只關心如何對文件按字節流進行讀寫的機制，這就意味著任何程序可以讀寫任何文件（即字節流），對文件具體內容的解析是應用程序的任務，操作系統對此不做任何干涉。例如，一個Rust編譯器可以讀取一個C語言源程序並進行編譯，操作系統並並不會阻止這樣的事情發生。

有了文件這樣的抽象後，操作系統內核就可把能讀寫並持久存儲的數據按文件來進行管理，並把文件分配給進程，讓進程以很簡潔的統一抽象接口 ``File`` 來讀寫數據：

.. code-block:: rust

    // os/src/fs/mod.rs

    pub trait File : Send + Sync {
        fn read(&self, buf: UserBuffer) -> usize;
        fn write(&self, buf: UserBuffer) -> usize;
    }

這個接口在內存和存儲設備之間建立了數據交換的通道。其中 ``UserBuffer`` 是我們在 ``mm`` 子模塊中定義的應用地址空間中的一段緩衝區（即內存）的抽象。它的具體實現在本質上其實只是一個 ``&[u8]`` ，位於應用地址空間中，內核無法直接通過用戶地址空間的虛擬地址來訪問，因此需要進行封裝。然而，在理解抽象接口 ``File`` 的各方法時，我們仍可以將 ``UserBuffer`` 看成一個 ``&[u8]`` 切片，它是一個同時給出了緩衝區起始地址和長度的胖指針。

``read`` 指的是從文件中讀取數據放到緩衝區中，最多將緩衝區填滿（即讀取緩衝區的長度那麼多字節），並返回實際讀取的字節數；而 ``write`` 指的是將緩衝區中的數據寫入文件，最多將緩衝區中的數據全部寫入，並返回直接寫入的字節數。至於 ``read`` 和 ``write`` 的實現則與文件具體是哪種類型有關，它決定了數據如何被讀取和寫入。

回過頭來再看一下用戶緩衝區的抽象 ``UserBuffer`` ，它的聲明如下：

.. code-block:: rust

    // os/src/mm/page_table.rs

    pub fn translated_byte_buffer(
        token: usize,
        ptr: *const u8,
        len: usize
    ) -> Vec<&'static mut [u8]>;

    pub struct UserBuffer {
        pub buffers: Vec<&'static mut [u8]>,
    }

    impl UserBuffer {
        pub fn new(buffers: Vec<&'static mut [u8]>) -> Self {
            Self { buffers }
        }
        pub fn len(&self) -> usize {
            let mut total: usize = 0;
            for b in self.buffers.iter() {
                total += b.len();
            }
            total
        }
    }

它只是將我們調用 ``translated_byte_buffer`` 獲得的包含多個切片的 ``Vec`` 進一步包裝起來，通過 ``len`` 方法可以得到緩衝區的長度。此外，我們還讓它作為一個迭代器可以逐字節進行讀寫。有興趣的同學可以參考類型 ``UserBufferIterator`` 還有 ``IntoIterator`` 和 ``Iterator`` 兩個 Trait 的使用方法。



塊設備驅動層
-----------------------------------------------

在 ``drivers`` 子模塊中的 ``block/mod.rs`` 中，我們可以找到內核訪問的塊設備實例 ``BLOCK_DEVICE`` ：

.. code-block:: rust

    // os/drivers/block/mod.rs

    #[cfg(feature = "board_qemu")]
    type BlockDeviceImpl = virtio_blk::VirtIOBlock;

    #[cfg(feature = "board_k210")]
    type BlockDeviceImpl = sdcard::SDCardWrapper;

    lazy_static! {
        pub static ref BLOCK_DEVICE: Arc<dyn BlockDevice> = Arc::new(BlockDeviceImpl::new());
    }

qemu 和 k210 平臺上的塊設備是不同的。在 qemu 上，我們使用 ``VirtIOBlock`` 訪問 VirtIO 塊設備；而在 k210 上，我們使用 ``SDCardWrapper`` 來訪問插入 k210 開發板上真實的 microSD 卡，它們都實現了 ``easy-fs`` 要求的 ``BlockDevice`` Trait 。通過 ``#[cfg(feature)]`` 可以在編譯的時候根據編譯參數調整 ``BlockDeviceImpl`` 具體為哪個塊設備，之後將它全局實例化為 ``BLOCK_DEVICE`` ，使得內核的其他模塊可以訪問。

Qemu 模擬器平臺
+++++++++++++++++++++++++++++++++++++++++++++++

在啟動 Qemu 模擬器的時候，我們可以配置參數來添加一塊 VirtIO 塊設備：

.. code-block:: makefile
    :linenos:
    :emphasize-lines: 12-13

    # os/Makefile

    FS_IMG := ../user/target/$(TARGET)/$(MODE)/fs.img

    run-inner: build
    ifeq ($(BOARD),qemu)
        @qemu-system-riscv64 \
            -machine virt \
            -nographic \
            -bios $(BOOTLOADER) \
            -device loader,file=$(KERNEL_BIN),addr=$(KERNEL_ENTRY_PA) \
            -drive file=$(FS_IMG),if=none,format=raw,id=x0 \
            -device virtio-blk-device,drive=x0,bus=virtio-mmio-bus.0

- 第 12 行，我們為虛擬機添加一塊虛擬硬盤，內容為我們之前通過 ``easy-fs-fuse`` 工具打包的包含應用 ELF 的 easy-fs 鏡像，並命名為 ``x0`` 。
- 第 13 行，我們將硬盤 ``x0`` 作為一個 VirtIO 總線中的一個塊設備接入到虛擬機系統中。 ``virtio-mmio-bus.0`` 表示 VirtIO 總線通過 MMIO 進行控制，且該塊設備在總線中的編號為 0 。

**內存映射 I/O** (MMIO, Memory-Mapped I/O) 指的是外設的設備寄存器可以通過特定的物理內存地址來訪問，每個外設的設備寄存器都分佈在沒有交集的一個或數個物理地址區間中，不同外設的設備寄存器所佔的物理地址空間也不會產生交集，且這些外設物理地址區間也不會和RAM的物理內存所在的區間存在交集（注：在後續的外設相關章節有更深入的講解）。從Qemu for RISC-V 64 平臺的 `源碼 <https://github.com/qemu/qemu/blob/f1dd640896ee2b50cb34328f2568aad324702954/hw/riscv/virt.c#L83>`_ 中可以找到 VirtIO 外設總線的 MMIO 物理地址區間為從 0x10001000 開頭的 4KiB 。為了能夠在內核中訪問 VirtIO 外設總線，我們就必須在內核地址空間中對特定內存區域提前進行映射：

.. code-block:: rust

    // os/src/config.rs

    #[cfg(feature = "board_qemu")]
    pub const MMIO: &[(usize, usize)] = &[
        (0x10001000, 0x1000),
    ];

如上面一段代碼所示，在 ``config`` 子模塊中我們硬編碼 Qemu 上的 VirtIO 總線的 MMIO 地址區間（起始地址，長度）。在創建內核地址空間的時候需要建立頁表映射：

.. code-block:: rust

    // os/src/mm/memory_set.rs

    use crate::config::MMIO;

    impl MemorySet {
        /// Without kernel stacks.
        pub fn new_kernel() -> Self {
            ...
            println!("mapping memory-mapped registers");
            for pair in MMIO {
                memory_set.push(MapArea::new(
                    (*pair).0.into(),
                    ((*pair).0 + (*pair).1).into(),
                    MapType::Identical,
                    MapPermission::R | MapPermission::W,
                ), None);
            }
            memory_set
        }
    }

這裡我們進行的是透明的恆等映射，從而讓內核可以兼容於直接訪問物理地址的設備驅動庫。

由於設備驅動的開發過程比較瑣碎，我們這裡直接使用已有的 `virtio-drivers <https://github.com/rcore-os/virtio-drivers>`_ crate ，它已經支持 VirtIO 總線架構下的塊設備、網絡設備、GPU 等設備。注：關於VirtIO 相關驅動的內容，在後續的外設相關章節有更深入的講解。

.. code-block:: rust

    // os/src/drivers/block/virtio_blk.rs

    use virtio_drivers::{VirtIOBlk, VirtIOHeader};
    const VIRTIO0: usize = 0x10001000;

    pub struct VirtIOBlock(Mutex<VirtIOBlk<'static>>);

    impl VirtIOBlock {
        pub fn new() -> Self {
            Self(Mutex::new(VirtIOBlk::new(
                unsafe { &mut *(VIRTIO0 as *mut VirtIOHeader) }
            ).unwrap()))
        }
    }

    impl BlockDevice for VirtIOBlock {
        fn read_block(&self, block_id: usize, buf: &mut [u8]) {
            self.0.lock().read_block(block_id, buf).expect("Error when reading VirtIOBlk");
        }
        fn write_block(&self, block_id: usize, buf: &[u8]) {
            self.0.lock().write_block(block_id, buf).expect("Error when writing VirtIOBlk");
        }
    }

上面的代碼中，我們將 ``virtio-drivers`` crate 提供的 VirtIO 塊設備抽象 ``VirtIOBlk`` 包裝為我們自己的 ``VirtIOBlock`` ，實質上只是加上了一層互斥鎖，生成一個新的類型來實現 ``easy-fs`` 需要的 ``BlockDevice`` Trait 。注意在 ``VirtIOBlk::new`` 的時候需要傳入一個 ``&mut VirtIOHeader`` 的參數， ``VirtIOHeader`` 實際上就代表以 MMIO 方式訪問 VirtIO 設備所需的一組設備寄存器。因此我們從 ``qemu-system-riscv64`` 平臺上的 Virtio MMIO 區間左端 ``VIRTIO0`` 開始轉化為一個 ``&mut VirtIOHeader`` 就可以在該平臺上訪問這些設備寄存器了。

很容易為 ``VirtIOBlock`` 實現 ``BlockDevice`` Trait ，因為它內部來自 ``virtio-drivers`` crate 的 ``VirtIOBlk`` 類型已經實現了 ``read/write_block`` 方法，我們進行轉發即可。

VirtIO 設備需要佔用部分內存作為一個公共區域從而更好的和 CPU 進行合作。這就像 MMU 需要在內存中保存多級頁表才能和 CPU 共同實現分頁機制一樣。在 VirtIO 架構下，需要在公共區域中放置一種叫做 VirtQueue 的環形隊列，CPU 可以向此環形隊列中向 VirtIO 設備提交請求，也可以從隊列中取得請求的結果，詳情可以參考 `virtio 文檔 <https://docs.oasis-open.org/virtio/virtio/v1.1/csprd01/virtio-v1.1-csprd01.pdf>`_ 。對於 VirtQueue 的使用涉及到物理內存的分配和回收，但這並不在 VirtIO 驅動 ``virtio-drivers`` 的職責範圍之內，因此它聲明瞭數個相關的接口，需要庫的使用者自己來實現：

.. code-block:: rust
    
    // https://github.com/rcore-os/virtio-drivers/blob/master/src/hal.rs#L57

    extern "C" {
        fn virtio_dma_alloc(pages: usize) -> PhysAddr;
        fn virtio_dma_dealloc(paddr: PhysAddr, pages: usize) -> i32;
        fn virtio_phys_to_virt(paddr: PhysAddr) -> VirtAddr;
        fn virtio_virt_to_phys(vaddr: VirtAddr) -> PhysAddr;
    }

由於我們已經實現了基於分頁內存管理的地址空間，實現這些功能自然不在話下：

.. code-block:: rust

    // os/src/drivers/block/virtio_blk.rs

    lazy_static! {
        static ref QUEUE_FRAMES: Mutex<Vec<FrameTracker>> = Mutex::new(Vec::new());
    }

    #[no_mangle]
    pub extern "C" fn virtio_dma_alloc(pages: usize) -> PhysAddr {
        let mut ppn_base = PhysPageNum(0);
        for i in 0..pages {
            let frame = frame_alloc().unwrap();
            if i == 0 { ppn_base = frame.ppn; }
            assert_eq!(frame.ppn.0, ppn_base.0 + i);
            QUEUE_FRAMES.lock().push(frame);
        }
        ppn_base.into()
    }

    #[no_mangle]
    pub extern "C" fn virtio_dma_dealloc(pa: PhysAddr, pages: usize) -> i32 {
        let mut ppn_base: PhysPageNum = pa.into();
        for _ in 0..pages {
            frame_dealloc(ppn_base);
            ppn_base.step();
        }
        0
    }

    #[no_mangle]
    pub extern "C" fn virtio_phys_to_virt(paddr: PhysAddr) -> VirtAddr {
        VirtAddr(paddr.0)
    }

    #[no_mangle]
    pub extern "C" fn virtio_virt_to_phys(vaddr: VirtAddr) -> PhysAddr {
        PageTable::from_token(kernel_token()).translate_va(vaddr).unwrap()
    }

這裡有一些細節需要注意：

- ``virtio_dma_alloc/dealloc`` 需要分配/回收數個 *連續* 的物理頁幀，而我們的 ``frame_alloc`` 是逐個分配，嚴格來說並不保證分配的連續性。幸運的是，這個過程只會發生在內核初始化階段，因此能夠保證連續性。
- 在 ``virtio_dma_alloc`` 中通過 ``frame_alloc`` 得到的那些物理頁幀 ``FrameTracker`` 都會被保存在全局的向量 ``QUEUE_FRAMES`` 以延長它們的生命週期，避免提前被回收。


K210 真實硬件平臺
+++++++++++++++++++++++++++++++++++++++++++++++

在 K210 開發板上，我們可以插入 microSD 卡並將其作為塊設備。相比 VirtIO 塊設備來說，想要將 microSD 驅動起來是一件比較困難的事情。microSD 自身的通信規範比較複雜，且還需考慮在 K210 中microSD掛在 **串行外設接口** (SPI, Serial Peripheral Interface) 總線上的情況。此外還需要正確設置 GPIO 的管腳映射並調整各鎖相環的頻率。實際上，在一塊小小的芯片中除了 K210 CPU 之外，還集成了很多不同種類的外設和控制模塊，它們內在的關聯比較緊密，不能像 VirtIO 設備那樣容易地從系統中獨立出來。

好在目前 Rust 嵌入式的生態正高速發展，針對 K210 平臺也有比較成熟的封裝了各類外設接口的庫可以用來開發上層應用。但是其功能往往分散為多個 crate ，在使用的時候需要開發者根據需求自行進行組裝。這屬於 Rust 的特點之一，和 C 語言提供一個一站式的板級開發包風格有很大的不同。在開發的時候，筆者就從社區中選擇了一些 crate 並進行了微量修改最終變成 ``k210-hal/k210-pac/k210-soc`` 三個能夠運行在 S 特權級（它們的原身僅支持運行在 M 特權級）的 crate ，它們可以更加便捷的實現 microSD 的驅動。關於 microSD 的驅動 ``SDCardWrapper`` 的實現，有興趣的同學可以參考 ``os/src/drivers/block/sdcard.rs`` 。

.. note::

    **感謝相關 crate 的原身**

    - `k210-hal <https://github.com/riscv-rust/k210-hal>`_
    - `k210-pac <https://github.com/riscv-rust/k210-pac>`_
    - `k210-sdk-stuff <https://github.com/laanwj/k210-sdk-stuff>`_

要在 K210 上啟用 microSD ，執行的時候無需任何改動，只需在 ``make run`` 之前將 microSD 插入 PC 再通過 ``make sdcard`` 將 easy-fs 鏡像燒寫進去即可。而後，將 microSD 插入 K210 開發板，連接到 PC 再 ``make run`` 。

在對 microSD 進行操作的時候，會涉及到 K210 內置的各種外設，正所謂”牽一髮而動全身“。因此 K210 平臺上的 MMIO 包含很多區間：

.. code-block:: rust

    // os/src/config.rs

    #[cfg(feature = "board_k210")]
    pub const MMIO: &[(usize, usize)] = &[
        // we don't need clint in S priv when running
        // we only need claim/complete for target0 after initializing
        (0x0C00_0000, 0x3000),      /* PLIC      */
        (0x0C20_0000, 0x1000),      /* PLIC      */
        (0x3800_0000, 0x1000),      /* UARTHS    */
        (0x3800_1000, 0x1000),      /* GPIOHS    */
        (0x5020_0000, 0x1000),      /* GPIO      */
        (0x5024_0000, 0x1000),      /* SPI_SLAVE */
        (0x502B_0000, 0x1000),      /* FPIOA     */
        (0x502D_0000, 0x1000),      /* TIMER0    */
        (0x502E_0000, 0x1000),      /* TIMER1    */
        (0x502F_0000, 0x1000),      /* TIMER2    */
        (0x5044_0000, 0x1000),      /* SYSCTL    */
        (0x5200_0000, 0x1000),      /* SPI0      */
        (0x5300_0000, 0x1000),      /* SPI1      */
        (0x5400_0000, 0x1000),      /* SPI2      */
    ];

內核索引節點層
-----------------------------------------------

在本章的第一小節我們介紹過，站在用戶的角度看來，在一個進程中可以使用多種不同的標誌來打開一個文件，這會影響到打開的這個文件可以用何種方式被訪問。此外，在連續調用 ``sys_read/write`` 讀寫一個文件的時候，我們知道進程中也存在著一個文件讀寫的當前偏移量，它也隨著文件讀寫的進行而被不斷更新。這些用戶視角中的文件系統抽象特徵需要內核來實現，與進程有很大的關係，而 ``easy-fs`` 文件系統不必涉及這些與進程結合緊密的屬性。因此，我們需要將 ``easy-fs`` 提供的 ``Inode`` 加上上述信息，進一步封裝為 OS 中的索引節點 ``OSInode`` ：

.. code-block:: rust

    // os/src/fs/inode.rs

    pub struct OSInode {
        readable: bool,
        writable: bool,
        inner: Mutex<OSInodeInner>,
    }

    pub struct OSInodeInner {
        offset: usize,
        inode: Arc<Inode>,
    }

    impl OSInode {
        pub fn new(
            readable: bool,
            writable: bool,
            inode: Arc<Inode>,
        ) -> Self {
            Self {
                readable,
                writable,
                inner: Mutex::new(OSInodeInner {
                    offset: 0,
                    inode,
                }),
            }
        }
    }

``OSInode`` 就表示進程中一個被打開的常規文件或目錄。 ``readable/writable`` 分別表明該文件是否允許通過 ``sys_read/write`` 進行讀寫。至於在 ``sys_read/write`` 期間被維護偏移量 ``offset`` 和它在 ``easy-fs`` 中的 ``Inode`` 則加上一把互斥鎖丟到 ``OSInodeInner`` 中。這在提供內部可變性的同時，也可以簡單應對多個進程同時讀寫一個文件的情況。


文件描述符層
-----------------------------------------------


.. chyyuu 可以解釋一下文件描述符的起因???

一個進程可以訪問的多個文件，所以在操作系統中需要有一個管理進程訪問的多個文件的結構，這就是 **文件描述符表** (File Descriptor Table) ，其中的每個 **文件描述符** (File Descriptor) 代表了一個特定讀寫屬性的I/O資源。

為簡化操作系統設計實現，可以讓每個進程都帶有一個線性的 **文件描述符表** ，記錄該進程請求內核打開並讀寫的那些文件集合。而 **文件描述符** (File Descriptor) 則是一個非負整數，表示文件描述符表中一個打開的 **文件描述符** 所處的位置（可理解為數組下標）。進程通過文件描述符，可以在自身的文件描述符表中找到對應的文件記錄信息，從而也就找到了對應的文件，並對文件進行讀寫。當打開（ ``open`` ）或創建（ ``create`` ） 一個文件的時候，一般情況下內核會返回給應用剛剛打開或創建的文件對應的文件描述符；而當應用想關閉（ ``close`` ）一個文件的時候，也需要向內核提供對應的文件描述符，以完成對應文件相關資源的回收操作。


因為 ``OSInode`` 也是一種要放到進程文件描述符表中文件，並可通過 ``sys_read/write`` 系統調用進行讀寫操作，因此我們也需要為它實現 ``File`` Trait ：

.. code-block:: rust

    // os/src/fs/inode.rs

    impl File for OSInode {
        fn readable(&self) -> bool { self.readable }
        fn writable(&self) -> bool { self.writable }
        fn read(&self, mut buf: UserBuffer) -> usize {
            let mut inner = self.inner.lock();
            let mut total_read_size = 0usize;
            for slice in buf.buffers.iter_mut() {
                let read_size = inner.inode.read_at(inner.offset, *slice);
                if read_size == 0 {
                    break;
                }
                inner.offset += read_size;
                total_read_size += read_size;
            }
            total_read_size
        }
        fn write(&self, buf: UserBuffer) -> usize {
            let mut inner = self.inner.lock();
            let mut total_write_size = 0usize;
            for slice in buf.buffers.iter() {
                let write_size = inner.inode.write_at(inner.offset, *slice);
                assert_eq!(write_size, slice.len());
                inner.offset += write_size;
                total_write_size += write_size;
            }
            total_write_size
        }
    }

本章我們為 ``File`` Trait 新增了 ``readable/writable`` 兩個抽象接口從而在 ``sys_read/sys_write`` 的時候進行簡單的訪問權限檢查。 ``read/write`` 的實現也比較簡單，只需遍歷 ``UserBuffer`` 中的每個緩衝區片段，調用 ``Inode`` 寫好的 ``read/write_at`` 接口就好了。注意 ``read/write_at`` 的起始位置是在 ``OSInode`` 中維護的 ``offset`` ，這個 ``offset`` 也隨著遍歷的進行被持續更新。在 ``read/write`` 的全程需要獲取 ``OSInode`` 的互斥鎖，保證兩個進程無法同時訪問同個文件。

文件描述符表
-----------------------------------------------

為了支持進程對文件的管理，我們需要在進程控制塊中加入文件描述符表的相應字段：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 12

    // os/src/task/task.rs

    pub struct TaskControlBlockInner {
        pub trap_cx_ppn: PhysPageNum,
        pub base_size: usize,
        pub task_cx_ptr: usize,
        pub task_status: TaskStatus,
        pub memory_set: MemorySet,
        pub parent: Option<Weak<TaskControlBlock>>,
        pub children: Vec<Arc<TaskControlBlock>>,
        pub exit_code: i32,
        pub fd_table: Vec<Option<Arc<dyn File + Send + Sync>>>,
    }

可以看到 ``fd_table`` 的類型包含多層嵌套，我們從外到裡分別說明：

- ``Vec`` 的動態長度特性使得我們無需設置一個固定的文件描述符數量上限，我們可以更加靈活的使用內存，而不必操心內存管理問題；
- ``Option`` 使得我們可以區分一個文件描述符當前是否空閒，當它是 ``None`` 的時候是空閒的，而 ``Some`` 則代表它已被佔用；
- ``Arc`` 首先提供了共享引用能力。後面我們會提到，可能會有多個進程共享同一個文件對它進行讀寫。此外被它包裹的內容會被放到內核堆而不是棧上，於是它便不需要在編譯期有著確定的大小；
- ``dyn`` 關鍵字表明 ``Arc`` 裡面的類型實現了 ``File/Send/Sync`` 三個 Trait ，但是編譯期無法知道它具體是哪個類型（可能是任何實現了 ``File`` Trait 的類型如 ``Stdin/Stdout`` ，故而它所佔的空間大小自然也無法確定），需要等到運行時才能知道它的具體類型，對於一些抽象方法的調用也是在那個時候才能找到該類型實現的方法並跳轉過去。

.. note::

    **Rust 語法卡片：Rust 中的多態**

    在編程語言中， **多態** (Polymorphism) 指的是在同一段代碼中可以隱含多種不同類型的特徵。在 Rust 中主要通過泛型和 Trait 來實現多態。
    
    泛型是一種 **編譯期多態** (Static Polymorphism)，在編譯一個泛型函數的時候，編譯器會對於所有可能用到的類型進行實例化並對應生成一個版本的彙編代碼，在編譯期就能知道選取哪個版本並確定函數地址，這可能會導致生成的二進制文件體積較大；而 Trait 對象（也即上面提到的 ``dyn`` 語法）是一種 **運行時多態** (Dynamic Polymorphism)，需要在運行時查一種類似於 C++ 中的 **虛表** (Virtual Table) 才能找到實際類型對於抽象接口實現的函數地址並進行調用，這樣會帶來一定的運行時開銷，但是更省空間且靈活。


應用訪問文件的內核機制實現
-----------------------------------------------

應用程序在訪問文件之前，首先需要完成對文件系統的初始化和加載。這可以通過操作系統來完成，也可以讓應用程序發出文件系統相關的系統調用（如 ``mount`` 等）來完成。我們這裡的選擇是讓操作系統直接完成。

應用程序如果要基於文件進行I/O訪問，大致就會涉及如下一些系統調用：

- 打開文件 -- sys_open：進程只有打開文件，操作系統才能返回一個可進行讀寫的文件描述符給進程，進程才能基於這個值來進行對應文件的讀寫。
- 關閉文件 -- sys_close：進程基於文件描述符關閉文件後，就不能再對文件進行讀寫操作了，這樣可以在一定程度上保證對文件的合法訪問。
- 讀文件 -- sys_read：進程可以基於文件描述符來讀文件內容到相應內存中。
- 寫文件 -- sys_write：進程可以基於文件描述符來把相應內存內容寫到文件中。


文件系統初始化
+++++++++++++++++++++++++++++++++++++++++++++++

在上一小節我們介紹過，為了使用 ``easy-fs`` 提供的抽象和服務，我們需要進行一些初始化操作才能成功將 ``easy-fs`` 接入到我們的內核中。按照前面總結的步驟：

1. 打開塊設備。從本節前面可以看出，我們已經打開並可以訪問裝載有 easy-fs 文件系統鏡像的塊設備 ``BLOCK_DEVICE`` ；
2. 從塊設備 ``BLOCK_DEVICE`` 上打開文件系統；
3. 從文件系統中獲取根目錄的 inode 。

2-3 步我們在這裡完成：

.. code-block:: rust

    // os/src/fs/inode.rs

    lazy_static! {
        pub static ref ROOT_INODE: Arc<Inode> = {
            let efs = EasyFileSystem::open(BLOCK_DEVICE.clone());
            Arc::new(EasyFileSystem::root_inode(&efs))
        };
    }

這之後就可以使用根目錄的 inode ``ROOT_INODE`` ，在內核中進行各種  ``easy-fs`` 的相關操作了。例如，在文件系統初始化完畢之後，在內核主函數 ``rust_main`` 中調用 ``list_apps`` 函數來列舉文件系統中可用的應用的文件名：

.. code-block:: rust

    // os/src/fs/inode.rs

    pub fn list_apps() {
        println!("/**** APPS ****");
        for app in ROOT_INODE.ls() {
            println!("{}", app);
        }
        println!("**************/")
    }


打開與關閉文件
+++++++++++++++++++++++++++++++++++++++++++++++

我們需要在內核中也定義一份打開文件的標誌 ``OpenFlags`` ：

.. code-block:: rust

    // os/src/fs/inode.rs

    bitflags! {
        pub struct OpenFlags: u32 {
            const RDONLY = 0;
            const WRONLY = 1 << 0;
            const RDWR = 1 << 1;
            const CREATE = 1 << 9;
            const TRUNC = 1 << 10;
        }
    }

    impl OpenFlags {
        /// Do not check validity for simplicity
        /// Return (readable, writable)
        pub fn read_write(&self) -> (bool, bool) {
            if self.is_empty() {
                (true, false)
            } else if self.contains(Self::WRONLY) {
                (false, true)
            } else {
                (true, true)
            }
        }
    }

它的 ``read_write`` 方法可以根據標誌的情況返回要打開的文件是否允許讀寫。簡單起見，這裡假設標誌自身一定合法。

接著，我們實現 ``open_file`` 內核函數，可根據文件名打開一個根目錄下的文件：

.. code-block:: rust

    // os/src/fs/inode.rs

    pub fn open_file(name: &str, flags: OpenFlags) -> Option<Arc<OSInode>> {
        let (readable, writable) = flags.read_write();
        if flags.contains(OpenFlags::CREATE) {
            if let Some(inode) = ROOT_INODE.find(name) {
                // clear size
                inode.clear();
                Some(Arc::new(OSInode::new(
                    readable,
                    writable,
                    inode,
                )))
            } else {
                // create file
                ROOT_INODE.create(name)
                    .map(|inode| {
                        Arc::new(OSInode::new(
                            readable,
                            writable,
                            inode,
                        ))
                    })
            }
        } else {
            ROOT_INODE.find(name)
                .map(|inode| {
                    if flags.contains(OpenFlags::TRUNC) {
                        inode.clear();
                    }
                    Arc::new(OSInode::new(
                        readable,
                        writable,
                        inode
                    ))
                })
        }
    }

這裡主要是實現了 ``OpenFlags`` 各標誌位的語義。例如只有 ``flags`` 參數包含 `CREATE` 標誌位才允許創建文件；而如果文件已經存在，則清空文件的內容。另外我們將從 ``OpenFlags`` 解析得到的讀寫相關權限傳入 ``OSInode`` 的創建過程中。

在其基礎上， ``sys_open`` 也就很容易實現了：

.. code-block:: rust

    // os/src/syscall/fs.rs

    pub fn sys_open(path: *const u8, flags: u32) -> isize {
        let task = current_task().unwrap();
        let token = current_user_token();
        let path = translated_str(token, path);
        if let Some(inode) = open_file(
            path.as_str(),
            OpenFlags::from_bits(flags).unwrap()
        ) {
            let mut inner = task.inner_exclusive_access();
            let fd = inner.alloc_fd();
            inner.fd_table[fd] = Some(inode);
            fd as isize
        } else {
            -1
        }
    }


關閉文件的系統調用 ``sys_close`` 實現非常簡單，我們只需將進程控制塊中的文件描述符表對應的一項改為 ``None`` 代表它已經空閒即可，同時這也會導致內層的引用計數類型 ``Arc`` 被銷燬，會減少一個文件的引用計數，當引用計數減少到 0 之後文件所佔用的資源就會被自動回收。

.. code-block:: rust

    // os/src/syscall/fs.rs

    pub fn sys_close(fd: usize) -> isize {
        let task = current_task().unwrap();
        let mut inner = task.inner_exclusive_access();
        if fd >= inner.fd_table.len() {
            return -1;
        }
        if inner.fd_table[fd].is_none() {
            return -1;
        }
        inner.fd_table[fd].take();
        0
    }


基於文件來加載並執行應用
+++++++++++++++++++++++++++++++++++++++++++++++

在有了文件系統支持之後，我們在 ``sys_exec`` 所需的應用的 ELF 文件格式的數據就不再需要通過應用加載器從內核的數據段獲取，而是從文件系統中獲取，這樣內核與應用的代碼/數據就解耦了：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 6-9

    // os/src/syscall/process.rs

    pub fn sys_exec(path: *const u8) -> isize {
        let token = current_user_token();
        let path = translated_str(token, path);
        if let Some(app_inode) = open_file(path.as_str(), OpenFlags::RDONLY) {
            let all_data = app_inode.read_all();
            let task = current_task().unwrap();
            task.exec(all_data.as_slice());
            0
        } else {
            -1
        }
    }

注意上面代碼片段中的高亮部分。當執行獲取應用的 ELF 數據的操作時，首先調用 ``open_file`` 函數，以只讀的方式在內核中打開應用文件並獲取它對應的 ``OSInode`` 。接下來可以通過 ``OSInode::read_all`` 將該文件的數據全部讀到一個向量 ``all_data`` 中：

.. code-block:: rust

    // os/src/fs/inode.rs

    impl OSInode {
        pub fn read_all(&self) -> Vec<u8> {
            let mut inner = self.inner.lock();
            let mut buffer = [0u8; 512];
            let mut v: Vec<u8> = Vec::new();
            loop {
                let len = inner.inode.read_at(inner.offset, &mut buffer);
                if len == 0 {
                    break;
                }
                inner.offset += len;
                v.extend_from_slice(&buffer[..len]);
            }
            v
        }
    }

之後，就可以從向量 ``all_data`` 中拿到應用中的 ELF 數據，當解析完畢並創建完應用地址空間後該向量將會被回收。

同樣的，我們在內核中創建初始進程 ``initproc`` 也需要替換為基於文件系統的實現：

.. code-block:: rust

    // os/src/task/mod.rs

    lazy_static! {
        pub static ref INITPROC: Arc<TaskControlBlock> = Arc::new({
            let inode = open_file("initproc", OpenFlags::RDONLY).unwrap();
            let v = inode.read_all();
            TaskControlBlock::new(v.as_slice())
        });
    }


讀寫文件
+++++++++++++++++++++++++++++++++++++++++++++++

基於文件抽象接口和文件描述符表，我們可以按照無結構的字節流來處理基本的文件讀寫，這樣可以讓文件讀寫系統調用 ``sys_read/write`` 變得更加具有普適性，為後續支持把管道等抽象為文件打下了基礎：

.. code-block:: rust

    // os/src/syscall/fs.rs

    pub fn sys_write(fd: usize, buf: *const u8, len: usize) -> isize {
        let token = current_user_token();
        let task = current_task().unwrap();
        let inner = task.inner_exclusive_access();
        if fd >= inner.fd_table.len() {
            return -1;
        }
        if let Some(file) = &inner.fd_table[fd] {
            let file = file.clone();
            // release current task TCB manually to avoid multi-borrow
            drop(inner);
            file.write(
                UserBuffer::new(translated_byte_buffer(token, buf, len))
            ) as isize
        } else {
            -1
        }
    }

    pub fn sys_read(fd: usize, buf: *const u8, len: usize) -> isize {
        let token = current_user_token();
        let task = current_task().unwrap();
        let inner = task.inner_exclusive_access();
        if fd >= inner.fd_table.len() {
            return -1;
        }
        if let Some(file) = &inner.fd_table[fd] {
            let file = file.clone();
            // release current task TCB manually to avoid multi-borrow
            drop(inner);
            file.read(
                UserBuffer::new(translated_byte_buffer(token, buf, len))
            ) as isize
        } else {
            -1
        }
    }

操作系統都是通過文件描述符在當前進程的文件描述符表中找到某個文件，無需關心文件具體的類型，只要知道它一定實現了 ``File`` Trait 的 ``read/write`` 方法即可。Trait 對象提供的運行時多態能力會在運行的時候幫助我們定位到符合實際類型的 ``read/write`` 方法。
