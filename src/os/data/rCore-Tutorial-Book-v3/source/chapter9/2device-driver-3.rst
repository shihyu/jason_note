virtio_blk塊設備驅動程序
=========================================

本節導讀
-----------------------------------------

本節主要介紹了與操作系統無關的基本virtio_blk設備驅動程序的設計與實現，以及如何在操作系統中封裝virtio_blk設備驅動程序，實現基於中斷機制的I/O操作，提升計算機系統的整體性能。



virtio-blk驅動程序
------------------------------------------

virtio-blk設備是一種virtio存儲設備，在QEMU模擬的RISC-V 64計算機中，以MMIO和中斷等方式方式來與驅動程序進行交互。這裡我們以Rust語言為例，給出virtio-blk設備驅動程序的設計與實現。主要包括如下內容：

- virtio-blk設備的關鍵數據結構
- 初始化virtio-blk設備
- 操作系統對接virtio-blk設備初始化
- virtio-blk設備的I/O操作
- 操作系統對接virtio-blk設備I/O操作

virtio-blk設備的關鍵數據結構
------------------------------------------

這裡我們首先需要定義virtio-blk設備的結構：

.. code-block:: Rust
   :linenos:

   // virtio-drivers/src/blk.rs
   pub struct VirtIOBlk<'a, H: Hal> {
      header: &'static mut VirtIOHeader,
      queue: VirtQueue<'a, H>,
      capacity: usize,
   }


``header`` 成員對應的 ``VirtIOHeader`` 數據結構是virtio設備的共有屬性，包括版本號、設備id、設備特徵等信息，其內存佈局和成員變量的含義與上一節描述 :ref:`virt-mmio設備的寄存器內存佈局 <term-virtio-mmio-regs>` 是一致的。而 ``VirtQueue`` 數據結構與上一節描述的 :ref:`virtqueue <term-virtqueue>` 在表達的含義上基本一致的。

.. _term-virtqueue-struct:

.. code-block:: Rust
   :linenos:

   #[repr(C)]
   pub struct VirtQueue<'a, H: Hal> {
      dma: DMA<H>, // DMA guard
      desc: &'a mut [Descriptor], // 描述符表
      avail: &'a mut AvailRing, // 可用環 Available ring
      used: &'a mut UsedRing, // 已用環 Used ring
      queue_idx: u32, //虛擬隊列索引值
      queue_size: u16, // 虛擬隊列長度
      num_used: u16, // 已經使用的隊列項目數
      free_head: u16, // 空閒隊列項目頭的索引值
      avail_idx: u16, //可用環的索引值
      last_used_idx: u16, //上次已用環的索引值
   }

其中成員變量 ``free_head`` 指空閒描述符鏈表頭，初始時所有描述符通過 ``next`` 指針依次相連形成空閒鏈表，成員變量 ``last_used_idx`` 是指設備上次已取的已用環元素位置。成員變量 ``avail_idx`` 是可用環的索引值。

.. _term-virtio-hal:

這裡出現的 ``Hal`` trait是 `virtio_drivers` 庫中定義的一個trait，用於抽象出與具體操作系統相關的操作，主要與內存分配和虛實地址轉換相關。這裡我們只給出trait的定義，對應操作系統的具體實現在後續的章節中會給出。


.. code-block:: Rust
   :linenos:

   pub trait Hal {
      /// Allocates the given number of contiguous physical pages of DMA memory for virtio use.
      fn dma_alloc(pages: usize) -> PhysAddr;
      /// Deallocates the given contiguous physical DMA memory pages.
      fn dma_dealloc(paddr: PhysAddr, pages: usize) -> i32;
      /// Converts a physical address used for virtio to a virtual address which the program can
      /// access.
      fn phys_to_virt(paddr: PhysAddr) -> VirtAddr;
      /// Converts a virtual address which the program can access to the corresponding physical
      /// address to use for virtio.
      fn virt_to_phys(vaddr: VirtAddr) -> PhysAddr;
   }



初始化virtio-blk設備
------------------------------------------
   
.. 在 ``virtio-drivers`` crate的 ``examples\riscv\src\main.rs`` 文件中的 ``virtio_probe`` 函數識別出virtio-blk設備後，會調用 ``virtio_blk(header)`` 來完成對virtio-blk設備的初始化過程。其實具體的初始化過程與virtio規範中描述的一般virtio設備的初始化過程大致一樣，步驟（實際實現可以簡化）如下：
   
.. 1. （可忽略）通過將0寫入狀態寄存器來複位器件；
.. 2. 將狀態寄存器的ACKNOWLEDGE狀態位置1；
.. 3. 將狀態寄存器的DRIVER狀態位置1；
.. 4. 從host_features寄存器讀取設備功能；
.. 5. 協商功能集並將接受的內容寫入guest_features寄存器；
.. 6. 將狀態寄存器的FEATURES_OK狀態位置1；
.. 7. （可忽略）重新讀取狀態寄存器，以確認設備已接受協商的功能；
.. 8. 執行特定於設備的設置：讀取設備配置空間，建立虛擬隊列；
.. 9. 將狀態寄存器的DRIVER_OK狀態位置1，使得該設備處於活躍可用狀態。
   

virtio-blk設備的初始化過程與virtio規範中描述的一般virtio設備的初始化過程大致一樣，對其實現的初步分析在 :ref:`virtio-blk初始化代碼 <term-virtio-blk-init>` 中。在設備初始化過程中讀取了virtio-blk設備的配置空間的設備信息：

.. code-block:: Rust
   :linenos:

   capacity: Volatile<u64> = 32  //32個扇區，即16KB
   blk_size: Volatile<u32> = 512 //扇區大小為512字節

為何能看到扇區大小為 ``512`` 字節欸，容量為 ``16KB`` 大小的virtio-blk設備？這當然是我們讓Qemu模擬器建立的一個虛擬硬盤。下面的命令可以看到虛擬硬盤創建和識別過程：

.. code-block:: shell
   :linenos:

   # 在virtio-drivers倉庫的example/riscv目錄下執行如下命令
   make run 
   # 可以看到與虛擬硬盤創建相關的具體命令
   ## 通過 dd 工具創建了扇區大小為 ``512`` 字節欸，容量為 ``16KB`` 大小的硬盤鏡像（disk img）
   dd if=/dev/zero of=target/riscv64imac-unknown-none-elf/release/img bs=512 count=32
      記錄了32+0 的讀入
      記錄了32+0 的寫出
      16384字節（16 kB，16 KiB）已複製，0.000439258 s，37.3 MB/s
   ## 通過 qemu-system-riscv64 命令啟動 Qemu 模擬器，創建 virtio-blk 設備   
   qemu-system-riscv64 \
        -drive file=target/riscv64imac-unknown-none-elf/release/img,if=none,format=raw,id=x0 \
        -device virtio-blk-device,drive=x0 ...
   ## 可以看到設備驅動查找到的virtio-blk設備色信息
   ...
   [ INFO] Detected virtio MMIO device with vendor id 0x554D4551, device type Block, version Modern
   [ INFO] device features: SEG_MAX | GEOMETRY | BLK_SIZE | FLUSH | TOPOLOGY | CONFIG_WCE | DISCARD | WRITE_ZEROES | RING_INDIRECT_DESC | RING_EVENT_IDX | VERSION_1
   [ INFO] config: 0x10008100
   [ INFO] found a block device of size 16KB
   ...

virtio-blk設備驅動程序瞭解了virtio-blk設備的扇區個數，扇區大小和總體容量後，還需調用 `` VirtQueue::new`` 成員函數來創建虛擬隊列 ``VirtQueue`` 數據結構的實例，這樣才能進行後續的磁盤讀寫操作。這個函數主要完成的事情是分配虛擬隊列的內存空間，並進行初始化：

- 設定 ``queue_size`` （即虛擬隊列的描述符條目數）為16；
- 計算滿足 ``queue_size`` 的描述符表 ``desc`` ，可用環 ``avail`` 和已用環 ``used`` 所需的物理空間的大小 -- ``size`` ；
- 基於上面計算的 ``size`` 分配物理空間； //VirtQueue.new()
- ``VirtIOHeader.queue_set`` 函數把虛擬隊列的相關信息（內存地址等）寫到virtio-blk設備的MMIO寄存器中；
- 初始化VirtQueue實例中各個成員變量（主要是 ``dma`` ， ``desc`` ，``avail`` ，``used`` ）的值。

做完這一步後，virtio-blk設備和設備驅動之間的虛擬隊列接口就打通了，可以進行I/O數據讀寫了。下面簡單代碼完成了對虛擬硬盤的讀寫操作和讀寫正確性檢查：


.. code-block:: rust
   :linenos:

   // virtio-drivers/examples/riscv/src/main.rs
   fn virtio_blk(header: &'static mut VirtIOHeader) { {
      // 創建blk結構
      let mut blk = VirtIOBlk::<HalImpl, T>::new(header).expect("failed to create blk driver");
      // 讀寫緩衝區
      let mut input = vec![0xffu8; 512];
      let mut output = vec![0; 512];
      ...
      // 把input數組內容寫入virtio-blk設備
      blk.write_block(i, &input).expect("failed to write");
      // 從virtio-blk設備讀取內容到output數組
      blk.read_block(i, &mut output).expect("failed to read");
      // 檢查virtio-blk設備讀寫的正確性
      assert_eq!(input, output);
   ...

操作系統對接virtio-blk設備初始化過程
--------------------------------------------------------------

但virtio_derivers 模塊還沒有與操作系統內核進行對接。我們還需在操作系統中封裝virtio-blk設備，讓操作系統內核能夠識別並使用virtio-blk設備。首先分析一下操作系統需要建立的表示virtio_blk設備的全局變量 ``BLOCK_DEVICE`` ：


.. code-block:: Rust
   :linenos:

   // os/src/drivers/block/virtio_blk.rs
   pub struct VirtIOBlock {
      virtio_blk: UPIntrFreeCell<VirtIOBlk<'static, VirtioHal>>,
      condvars: BTreeMap<u16, Condvar>,
   }
   // os/easy-fs/src/block_dev.rs
   pub trait BlockDevice: Send + Sync + Any {
      fn read_block(&self, block_id: usize, buf: &mut [u8]);
      fn write_block(&self, block_id: usize, buf: &[u8]);
      fn handle_irq(&self);
   }
   // os/src/boards/qemu.rs
   pub type BlockDeviceImpl = crate::drivers::block::VirtIOBlock;
   // os/src/drivers/block/mod.rs
   lazy_static! {
      pub static ref BLOCK_DEVICE: Arc<dyn BlockDevice> = Arc::new(BlockDeviceImpl::new());
   }


從上面的代碼可以看到，操作系統中表示virtio_blk設備的全局變量 ``BLOCK_DEVICE`` 的類型是 ``VirtIOBlock`` ,封裝了來自virtio_derivers 模塊的 ``VirtIOBlk`` 類型。這樣，操作系統內核就可以通過 ``BLOCK_DEVICE`` 全局變量來訪問virtio_blk設備了。而  ``VirtIOBlock`` 中的 ``condvars: BTreeMap<u16, Condvar>`` 條件變量結構，是用於進程在等待 I/O讀或寫操作完全前，通過條件變量讓進程處於掛起狀態。當virtio_blk設備完成I/O操作後，會通過中斷喚醒等待的進程。而操作系統對virtio_blk設備的初始化除了封裝 ``VirtIOBlk`` 類型並調用 ``VirtIOBlk::<VirtioHal>::new()`` 外，還需要初始化 ``condvars`` 條件變量結構，而每個條件變量對應著一個虛擬隊列條目的編號，這意味著每次I/O請求都綁定了一個條件變量，讓發出請求的線程/進程可以被掛起。


.. code-block:: Rust
   :linenos:

   impl VirtIOBlock {
      pub fn new() -> Self {
         let virtio_blk = unsafe {
               UPIntrFreeCell::new(
                  VirtIOBlk::<VirtioHal>::new(&mut *(VIRTIO0 as *mut VirtIOHeader)).unwrap(),
               )
         };
         let mut condvars = BTreeMap::new();
         let channels = virtio_blk.exclusive_access().virt_queue_size();
         for i in 0..channels {
               let condvar = Condvar::new();
               condvars.insert(i, condvar);
         }
         Self {
               virtio_blk,
               condvars,
         }
      }
   }

在上述初始化代碼中，我們先看到 ``VIRTIO0`` ，這是 Qemu模擬的virtio_blk設備中I/O寄存器的物理內存地址， ``VirtIOBlk`` 需要這個地址來對 ``VirtIOHeader`` 數據結構所表示的virtio-blk I/O控制寄存器進行讀寫操作，從而完成對某個具體的virtio-blk設備的初始化過程。而且我們還看到了 ``VirtioHal`` 結構，它實現virtio-drivers 模塊定義 ``Hal`` trait約定的方法 ，提供DMA內存分配和虛實地址映射操作，從而讓virtio-drivers 模塊中 ``VirtIOBlk`` 類型能夠得到操作系統的服務。

.. code-block:: Rust
   :linenos:

   // os/src/drivers/bus/virtio.rs
   impl Hal for VirtioHal {
      fn dma_alloc(pages: usize) -> usize {
         //分配頁幀 page-frames
         }
         let pa: PhysAddr = ppn_base.into();
         pa.0
      }

      fn dma_dealloc(pa: usize, pages: usize) -> i32 {
         //釋放頁幀 page-frames
         0
      }

      fn phys_to_virt(addr: usize) -> usize {
         addr
      }

      fn virt_to_phys(vaddr: usize) -> usize {
         //把虛地址轉為物理地址
      }
   }


virtio-blk設備的I/O操作
--------------------------------------------------------------

操作系統的virtio-blk驅動的主要功能是給操作系統中的文件系統內核模塊提供讀寫磁盤塊的服務，並在對進程管理有一定的影響，但不用直接給應用程序提供服務。在操作系統與virtio-drivers crate中virtio-blk裸機驅動對接的過程中，需要注意的關鍵問題是操作系統的virtio-blk驅動如何封裝virtio-blk裸機驅動的基本功能，完成如下服務：

1. 讀磁盤塊，掛起發起請求的進程/線程;
2. 寫磁盤塊，掛起發起請求的進程/線程；
3. 對virtio-blk設備發出的中斷進行處理，喚醒相關等待的進程/線程。

virtio-blk驅動程序發起的I/O請求包含操作類型(讀或寫)、起始扇區(塊設備的最小訪問單位的一個扇區的長度512字節)、內存地址、訪問長度；請求處理完成後返回的I/O響應僅包含結果狀態(成功或失敗，讀操作請求的讀出扇區內容)。系統產生的一個I/O請求在內存中的數據結構分為三個部分：Header（請求頭部，包含操作類型和起始扇區）；Data（數據區，包含地址和長度）；Status（結果狀態），這些信息分別放在三個buffer，所以需要三個描述符。

virtio-blk設備使用 ``VirtQueue`` 數據結構來表示虛擬隊列進行數據傳輸，此數據結構主要由三段連續內存組成：描述符表 ``Descriptor[]`` 、環形隊列結構的 ``AvailRing`` 和 ``UsedRing``  。驅動程序和virtio-blk設備都能訪問到此數據結構。

描述符表由固定長度(16字節)的描述符Descriptor組成，其個數等於環形隊列長度，其中每個Descriptor的結構為：

.. code-block:: Rust
   :linenos:

   struct Descriptor {
      addr: Volatile<u64>,
      len: Volatile<u32>,
      flags: Volatile<DescFlags>,
      next: Volatile<u16>,
   }

包含四個域：addr代表某段內存的起始地址，長度為8個字節；len代表某段內存的長度，本身佔用4個字節(因此代表的內存段最大為4GB)；flags代表內存段讀寫屬性等，長度為2個字節；next代表下一個內存段對應的Descpriptor在描述符表中的索引，因此通過next字段可以將一個請求對應的多個內存段連接成鏈表。

可用環 ``AvailRing`` 的結構為：

.. code-block:: Rust
   :linenos:

   struct AvailRing {
      flags: Volatile<u16>,
      /// A driver MUST NOT decrement the idx.
      idx: Volatile<u16>,
      ring: [Volatile<u16>; 32], // actual size: queue_size
      used_event: Volatile<u16>, // unused
   }

可用環由頭部的 ``flags`` 和 ``idx`` 域及 ``ring`` 數組組成： ``flags`` 與通知機制相關； ``idx`` 代表最新放入IO請求的編號，從零開始單調遞增，將其對隊列長度取餘即可得該I/O請求在可用環數組中的索引；可用環數組元素用來存放I/O請求佔用的首個描述符在描述符表中的索引，數組長度等於可用環的長度(不開啟event_idx特性)。

已用環 ``UsedRing`` 的結構為：

.. code-block:: Rust
   :linenos:

   struct UsedRing {
      flags: Volatile<u16>,
      idx: Volatile<u16>,
      ring: [UsedElem; 32],       // actual size: queue_size
      avail_event: Volatile<u16>, // unused
   }


已用環由頭部的 ``flags`` 和 ``idx`` 域及 ``ring`` 數組組成： ``flags`` 與通知機制相關； ``idx`` 代表最新放入I/O響應的編號，從零開始單調遞增，將其對隊列長度取餘即可得該I/O響應在已用環數組中的索引；已用環數組元素主要用來存放I/O響應占用的首個描述符在描述符表中的索引， 數組長度等於已用環的長度(不開啟event_idx特性)。


針對用戶進程發出的I/O請求，經過系統調用，文件系統等一系列處理後，最終會形成對virtio-blk驅動程序的調用。對於寫操作，具體實現如下：


.. code-block:: Rust
   :linenos:

   //virtio-drivers/src/blk.rs
    pub fn write_block(&mut self, block_id: usize, buf: &[u8]) -> Result {
        assert_eq!(buf.len(), BLK_SIZE);
        let req = BlkReq {
            type_: ReqType::Out,
            reserved: 0,
            sector: block_id as u64,
        };
        let mut resp = BlkResp::default();
        self.queue.add(&[req.as_buf(), buf], &[resp.as_buf_mut()])?;
        self.header.notify(0);
        while !self.queue.can_pop() {
            spin_loop();
        }
        self.queue.pop_used()?;
        match resp.status {
            RespStatus::Ok => Ok(()),
            _ => Err(Error::IoError),
        }
    }

基本流程如下：

1. 一個完整的virtio-blk的I/O寫請求由三部分組成，包括表示I/O寫請求信息的結構 ``BlkReq`` ，要傳輸的數據塊 ``buf``，一個表示設備響應信息的結構 ``BlkResp``  。這三部分需要三個描述符來表示；
2. （驅動程序處理）接著調用 ``VirtQueue.add`` 函數，從描述符表中申請三個空閒描述符，每項指向一個內存塊，填寫上述三部分的信息，並將三個描述符連接成一個描述符鏈表；
3. （驅動程序處理）接著調用 ``VirtQueue.notify`` 函數，寫MMIO模式的 ``queue_notify`` 寄存器，即向 virtio-blk設備發出通知；
4. （設備處理）virtio-blk設備收到通知後，通過比較 ``last_avail`` (初始為0)和 ``AvailRing`` 中的 ``idx`` 判斷是否有新的請求待處理(如果 ``last_vail`` 小於 ``AvailRing`` 中的 ``idx`` ，則表示有新請求)。如果有，則 ``last_avail`` 加1，並以 ``last_avail`` 為索引從描述符表中找到這個I/O請求對應的描述符鏈來獲知完整的請求信息，並完成存儲塊的I/O寫操作；
5. （設備處理）設備完成I/O寫操作後(包括更新包含 ``BlkResp`` 的Descriptor)，將已完成I/O的描述符放入UsedRing對應的ring項中，並更新idx，代表放入一個響應；如果設置了中斷機制，還會產生中斷來通知操作系統響應中斷；
6. （驅動程序處理）驅動程序可用輪詢機制查看設備是否有響應（持續調用  ``VirtQueue.can_pop`` 函數），通過比較內部的 ``VirtQueue.last_used_idx`` 和 ``VirtQueue.used.idx`` 判斷是否有新的響應。如果有，則取出響應(並更新 ``last_used_idx`` )，將完成響應對應的三項Descriptor回收，最後將結果返回給用戶進程。當然，也可通過中斷機制來響應。


I/O讀請求的處理過程與I/O寫請求的處理過程幾乎一樣，僅僅是 ``BlkReq`` 的內容不同，寫操作中的 ``req.type_`` 是 ``ReqType::Out``，而讀操作中的 ``req.type_`` 是 ``ReqType::In`` 。具體可以看看 ``virtio-drivers/src/blk.rs`` 文件中的 ``VirtIOBlk.read_block`` 函數的實現。

這種基於輪詢的I/O訪問方式效率比較差，為此，我們需要實現基於中斷的I/O訪問方式。為此在支持中斷的 ``write_block_nb`` 方法：



.. code-block:: Rust
   :linenos:

   pub unsafe fn write_block_nb(
        &mut self,
        block_id: usize,
        buf: &[u8],
        resp: &mut BlkResp,
    ) -> Result<u16> {
        assert_eq!(buf.len(), BLK_SIZE);
        let req = BlkReq {
            type_: ReqType::Out,
            reserved: 0,
            sector: block_id as u64,
        };
        let token = self.queue.add(&[req.as_buf(), buf], &[resp.as_buf_mut()])?;
        self.header.notify(0);
        Ok(token)
   }

   // Acknowledge interrupt.
   pub fn ack_interrupt(&mut self) -> bool {
        self.header.ack_interrupt()
   }

與不支持中的 ``write_block`` 函數比起來， ``write_block_nb`` 函數更簡單了，在發出I/O請求後，就直接返回了。 ``read_block_nb`` 函數的處理流程與此一致。而響應中斷的 ``ack_interrupt`` 函數只是完成了非常基本的 virtio設備的中斷響應操作。在virtio-drivers中實現的virtio設備驅動是看不到進程、條件變量等操作系統的各種關鍵要素，只有與操作系統內核對接，才能完整實現基於中斷的I/O訪問方式。




操作系統對接virtio-blk設備I/O處理
--------------------------------------------------------------

操作系統中的文件系統模塊與操作系統中的塊設備驅動程序 ``VirtIOBlock`` 直接交互，而操作系統中的塊設備驅動程序 ``VirtIOBlock`` 封裝了virtio-drivers中實現的virtio_blk設備驅動。在文件系統的介紹中，我們並沒有深入分析virtio_blk設備。這裡我們將介紹操作系統對接virtio_blk設備驅動並完成基於中斷機制的I/O處理過程。

接下來需要擴展文件系統對塊設備驅動的I/O訪問要求，這體現在  ``BlockDevice`` trait的新定義中增加了 ``handle_irq`` 方法，而操作系統的virtio_blk設備驅動程序中的 ``VirtIOBlock`` 實現了這個方法，並且實現了既支持輪詢方式，也支持中斷方式的塊讀寫操作。

.. code-block:: Rust
   :linenos:

   // easy-fs/src/block_dev.rs
   pub trait BlockDevice: Send + Sync + Any {
      fn read_block(&self, block_id: usize, buf: &mut [u8]);
      fn write_block(&self, block_id: usize, buf: &[u8]);
      // 更新的部分：增加對塊設備中斷的處理
      fn handle_irq(&self);
   }
   // os/src/drivers/block/virtio_blk.rs
   impl BlockDevice for VirtIOBlock {
      fn handle_irq(&self) {
         self.virtio_blk.exclusive_session(|blk| {
               while let Ok(token) = blk.pop_used() {
                     // 喚醒等待該塊設備I/O完成的線程/進程
                  self.condvars.get(&token).unwrap().signal();
               }
         });
      }

      fn read_block(&self, block_id: usize, buf: &mut [u8]) {
         // 獲取輪詢或中斷的配置標記
         let nb = *DEV_NON_BLOCKING_ACCESS.exclusive_access();
         if nb { // 如果是中斷方式
               let mut resp = BlkResp::default();
               let task_cx_ptr = self.virtio_blk.exclusive_session(|blk| { 
                  // 基於中斷方式的塊讀請求
                  let token = unsafe { blk.read_block_nb(block_id, buf, &mut resp).unwrap() };
                  // 將當前線程/進程加入條件變量的等待隊列
                  self.condvars.get(&token).unwrap().wait_no_sched()
               });
               // 切換線程/進程
               schedule(task_cx_ptr);
               assert_eq!(
                  resp.status(),
                  RespStatus::Ok,
                  "Error when reading VirtIOBlk"
               );
         } else { // 如果是輪詢方式，則進行輪詢式的塊讀請求
               self.virtio_blk
                  .exclusive_access()
                  .read_block(block_id, buf)
                  .expect("Error when reading VirtIOBlk");
         }
      }

``write_block`` 寫操作與 ``read_block`` 讀操作的處理過程一致，這裡不再贅述。

然後需要對操作系統整體的中斷處理過程進行調整，以支持對基於中斷方式的塊讀寫操作：

.. code-block:: Rust
   :linenos:

   // os/src/trap/mode.rs
   //在用戶態接收到外設中斷
   pub fn trap_handler() -> ! {
      ...
      crate::board::irq_handler();
   //在內核態接收到外設中斷
   pub fn trap_from_kernel(_trap_cx: &TrapContext) {
      ...
      crate::board::irq_handler();
   // os/src/boards/qemu.rs
   pub fn irq_handler() {
      let mut plic = unsafe { PLIC::new(VIRT_PLIC) };
      // 獲得外設中斷號
      let intr_src_id = plic.claim(0, IntrTargetPriority::Supervisor);
      match intr_src_id {
         ...
         //處理virtio_blk設備產生的中斷
         8 => BLOCK_DEVICE.handle_irq(),
      }
      // 完成中斷響應
      plic.complete(0, IntrTargetPriority::Supervisor, intr_src_id);
   }


``BLOCK_DEVICE.handle_irq()`` 執行的就是  ``VirtIOBlock`` 實現的中斷處理方法 ``handle_irq()`` ，從而讓等待在塊讀寫的進程/線程得以繼續執行。

有了基於中斷方式的塊讀寫操作後，當某個線程/進程由於塊讀寫操作無法繼續執行時，操作系統可以切換到其它處於就緒態的線程/進程執行，從而讓計算機系統的整體執行效率得到提升。