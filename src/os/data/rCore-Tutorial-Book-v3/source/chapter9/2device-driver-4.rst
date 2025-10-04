virtio_gpu設備驅動程序
=========================================

本節導讀
-----------------------------------------

本節主要介紹了與操作系統無關的基本virtio_gpu設備驅動程序的設計與實現，以及如何在操作系統中封裝virtio_gpu設備驅動程序，實現對豐富多彩的GUI app的支持。




virtio-gpu驅動程序
------------------------------------------

讓操作系統能夠顯示圖形是一個有趣的目標。這可以通過在QEMU或帶顯示屏的開發板上寫顯示驅動程序來完成。這裡我們主要介紹如何驅動基於QEMU的virtio-gpu虛擬顯示設備。大家不用擔心這個驅動實現很困難，其實它主要完成的事情就是對顯示內存進行寫操作而已。我們看到的圖形顯示屏幕其實是由一個一個的像素點來組成的，顯示驅動程序的主要目標就是把每個像素點用內存單元來表示，並把代表所有這些像素點的內存區域（也稱顯示內存，顯存， frame buffer）“通知”顯示I/O控制器（也稱圖形適配器，graphics adapter），然後顯示I/O控制器會根據內存內容渲染到圖形顯示屏上。這裡我們以Rust語言為例，給出virtio-gpu設備驅動程序的設計與實現。主要包括如下內容：

- virtio-gpu設備的關鍵數據結構
- 初始化virtio-gpu設備
- 操作系統對接virtio-gpu設備初始化
- virtio-gpu設備的I/O操作
- 操作系統對接virtio-gpu設備I/O操作


virtio-gpu設備的關鍵數據結構
------------------------------------------

.. code-block:: Rust
   :linenos:
   
   // virtio-drivers/src/gpu.rs
    pub struct VirtIOGpu<'a, H: Hal> {
        header: &'static mut VirtIOHeader,
        /// 顯示區域的分辨率
        rect: Rect,
        /// 顯示內存frame buffer
        frame_buffer_dma: Option<DMA<H>>,
        /// 光標圖像內存cursor image buffer.
        cursor_buffer_dma: Option<DMA<H>>,
        /// Queue for sending control commands.
        control_queue: VirtQueue<'a, H>,
        /// Queue for sending cursor commands.
        cursor_queue: VirtQueue<'a, H>,
        /// Queue buffer
        queue_buf_dma: DMA<H>,
        /// Send buffer for queue.
        queue_buf_send: &'a mut [u8],
        /// Recv buffer for queue.
        queue_buf_recv: &'a mut [u8],
    }

``header`` 成員對應的 ``VirtIOHeader`` 數據結構是virtio設備的共有屬性，包括版本號、設備id、設備特徵等信息，其內存佈局和成員變量的含義與本章前述的 :ref:`virt-mmio設備的寄存器內存佈局 <term-virtio-mmio-regs>` 是一致的。而 :ref:`VirtQueue數據結構的內存佈局<term-virtqueue-struct>` 和 :ref:`virtqueue的含義 <term-virtqueue>` 與本章前述內容一致。與 :ref:`具體操作系統相關的服務函數接口Hal<term-virtio-hal>` 在上一節已經介紹過，這裡不再贅述。

顯示內存區域 ``frame_buffer_dma`` 是一塊要由操作系統或運行時分配的顯示內存，當把表示像素點的值就寫入這個區域後，virtio-gpu設備會在Qemu虛擬的顯示器上顯示出圖形。光標圖像內存區域 ``cursor_buffer_dma`` 用於存放光標圖像的數據，當光標圖像數據更新後，virtio-gpu設備會在Qemu虛擬的顯示器上顯示出光標圖像。這兩塊區域與  ``queue_buf_dma`` 區域都是用於與I/O設備進行數據傳輸的 :ref:`DMA內存<term-dma-tech>`，都由操作系統進行分配等管理。所以在 ``virtio_drivers`` 中建立了對應的 ``DMA`` 結構，用於操作系統管理這些DMA內存。


.. code-block:: Rust
   :linenos:
   
   // virtio-drivers/src/gpu.rs
    pub struct DMA<H: Hal> {
        paddr: usize,  // DMA內存起始物理地址
        pages: usize,  // DMA內存所佔物理頁數量
        ...
    }
    impl<H: Hal> DMA<H> {
        pub fn new(pages: usize) -> Result<Self> {
            //操作系統分配 pages*頁大小的DMA內存
            let paddr = H::dma_alloc(pages);
            ...
        }
        // DMA內存的物理地址
        pub fn paddr(&self) -> usize {
            self.paddr
        }
        // DMA內存的虛擬地址
        pub fn vaddr(&self) -> usize {
            H::phys_to_virt(self.paddr)
        }
        // DMA內存的物理頁幀號
        pub fn pfn(&self) -> u32 {
            (self.paddr >> 12) as u32
        }
        // 把DMA內存轉為便於Rust處理的可變一維數組切片
        pub unsafe fn as_buf(&self) -> &'static mut [u8] {
            core::slice::from_raw_parts_mut(self.vaddr() as _, PAGE_SIZE * self.pages as usize)
        ...
    impl<H: Hal> Drop for DMA<H> {
        // 操作系統釋放DMA內存
        fn drop(&mut self) {
            let err = H::dma_dealloc(self.paddr as usize, self.pages as usize);
            ...


virtio-gpu驅動程序與virtio-gpu設備之間通過兩個 virtqueue 來進行交互訪問，``control_queue`` 用於驅動程序發送顯示相關控制命令（如設置顯示內存的起始地址等）給virtio-gpu設備， ``cursor_queue`` 用於驅動程序給給virtio-gpu設備發送顯示鼠標更新的相關控制命令。 ``queue_buf_dma`` 是存放控制命令和返回結果的內存， ``queue_buf_send`` 和 ``queue_buf_recv`` 是 ``queue_buf_dma`` DMA內存的可變一維數組切片形式，分別用於虛擬隊列的接收與發送。

初始化virtio-gpu設備
------------------------------------------

在 ``virtio-drivers`` crate的 ``examples/riscv/src/main.rs`` 文件中的 ``virtio_probe`` 函數識別出virtio-gpu設備後，會調用 ``virtio_gpu(header)`` 函數來完成對virtio-gpu設備的初始化過程。virtio-gpu設備初始化的工作主要是查詢顯示設備的信息（如分辨率等），並將該信息用於初始顯示掃描（scanout）設置。下面的命令可以看到虛擬GPU的創建和識別過程：

.. code-block:: shell
   :linenos:

   # 在virtio-drivers倉庫的example/riscv目錄下執行如下命令
   make run 
   ## 通過 qemu-system-riscv64 命令啟動 Qemu 模擬器，創建 virtio-gpu 設備   
   qemu-system-riscv64 \
        -device virtio-gpu-device ...
   ## 可以看到設備驅動查找到的virtio-gpu設備色信息
   ...
   [ INFO] Detected virtio MMIO device with vendor id 0x554D4551, device type GPU, version Modern
   [ INFO] Device features EDID | RING_INDIRECT_DESC | RING_EVENT_IDX | VERSION_1
   [ INFO] events_read: 0x0, num_scanouts: 0x1
   [ INFO] GPU resolution is 1280x800
   [ INFO] => RespDisplayInfo { header: CtrlHeader { hdr_type: OkDisplayInfo, flags: 0, fence_id: 0, ctx_id: 0, _padding: 0 }, rect: Rect { x: 0, y: 0, width: 1280, height: 800 }, enabled: 1, flags: 0 }


並看到Qemu輸出的圖形顯示：

.. image:: virtio-test-example2.png
    :align: center
    :scale: 30 %
    :name: virtio-test-example2

接下來我們看看virtio-gpu設備初始化的具體過程如：

.. code-block:: Rust
   :linenos:

    // virtio-drivers/examples/riscv/src/main.rs
    fn virtio_gpu(header: &'static mut VirtIOHeader) {
        let mut gpu = VirtIOGpu::<HalImpl>::new(header).expect("failed to create gpu driver");
        let (width, height) = gpu.resolution().expect("failed to get resolution");
        info!("GPU resolution is {}x{}", width, height);
        let fb = gpu.setup_framebuffer().expect("failed to get fb");
        ...

在 ``virtio_gpu`` 函數調用創建了 ``VirtIOGpu::<HalImpl>::new(header)`` 函數，獲得關於virtio-gpu設備的重要信息：顯示分辨率 ``1280x800`` ；而且會建立virtio虛擬隊列，並基於這些信息來創建表示virtio-gpu的 ``gpu`` 結構。然後會進一步調用 ``gpu.setup_framebuffer()`` 函數來建立和配置顯示內存緩衝區，打通設備驅動與virtio-gpu設備間的顯示數據傳輸通道。

.. _term-virtio-driver-gpu-new:

``VirtIOGpu::<HalImpl>::new(header)`` 函數主要完成了virtio-gpu設備的初始化工作：

.. code-block:: Rust
   :linenos:

   // virtio-drivers/src/gpu.rs
   impl VirtIOGpu<'_, H> {
   pub fn new(header: &'static mut VirtIOHeader) -> Result<Self> {
        header.begin_init(|features| {
            let features = Features::from_bits_truncate(features);
            let supported_features = Features::empty();
            (features & supported_features).bits()
        });

        // read configuration space
        let config = unsafe { &mut *(header.config_space() as *mut Config) };

        let control_queue = VirtQueue::new(header, QUEUE_TRANSMIT, 2)?;
        let cursor_queue = VirtQueue::new(header, QUEUE_CURSOR, 2)?;

        let queue_buf_dma = DMA::new(2)?;
        let queue_buf_send = unsafe { &mut queue_buf_dma.as_buf()[..PAGE_SIZE] };
        let queue_buf_recv = unsafe { &mut queue_buf_dma.as_buf()[PAGE_SIZE..] };

        header.finish_init();

        Ok(VirtIOGpu {
            header,
            frame_buffer_dma: None,
            rect: Rect::default(),
            control_queue,
            cursor_queue,
            queue_buf_dma,
            queue_buf_send,
            queue_buf_recv,
        })
    }

首先是 ``header.begin_init`` 函數完成了對virtio設備的共性初始化的常規步驟的前六步；第七步在這裡被忽略；第八步讀取virtio-gpu設備的配置空間（config space）信息；緊接著是創建兩個虛擬隊列：控制命令隊列、光標管理隊列。併為控制命令隊列分配兩個 page （8KB）的內存空間用於放置虛擬隊列中的控制命令和返回結果；最後的第九步，調用 ``header.finish_init`` 函數，將virtio-gpu設備設置為活躍可用狀態。

雖然virtio-gpu初始化完畢，但它目前還不能進行顯示。為了能夠進行正常的顯示，我們還需建立顯存區域 frame buffer，並綁定在virtio-gpu設備上。這主要是通過 ``VirtIOGpu.setup_framebuffer`` 函數來完成的。

.. _term-virtio-driver-gpu-setupfb:

.. code-block:: Rust
   :linenos:

   // virtio-drivers/src/gpu.rs
   pub fn setup_framebuffer(&mut self) -> Result<&mut [u8]> {
        // get display info
        let display_info: RespDisplayInfo =
            self.request(CtrlHeader::with_type(Command::GetDisplayInfo))?;
        display_info.header.check_type(Command::OkDisplayInfo)?;
        self.rect = display_info.rect;

        // create resource 2d
        let rsp: CtrlHeader = self.request(ResourceCreate2D {
            header: CtrlHeader::with_type(Command::ResourceCreate2d),
            resource_id: RESOURCE_ID,
            format: Format::B8G8R8A8UNORM,
            width: display_info.rect.width,
            height: display_info.rect.height,
        })?;
        rsp.check_type(Command::OkNodata)?;

        // alloc continuous pages for the frame buffer
        let size = display_info.rect.width * display_info.rect.height * 4;
        let frame_buffer_dma = DMA::new(pages(size as usize))?;

        // resource_attach_backing
        let rsp: CtrlHeader = self.request(ResourceAttachBacking {
            header: CtrlHeader::with_type(Command::ResourceAttachBacking),
            resource_id: RESOURCE_ID,
            nr_entries: 1,
            addr: frame_buffer_dma.paddr() as u64,
            length: size,
            padding: 0,
        })?;
        rsp.check_type(Command::OkNodata)?;

        // map frame buffer to screen
        let rsp: CtrlHeader = self.request(SetScanout {
            header: CtrlHeader::with_type(Command::SetScanout),
            rect: display_info.rect,
            scanout_id: 0,
            resource_id: RESOURCE_ID,
        })?;
        rsp.check_type(Command::OkNodata)?;

        let buf = unsafe { frame_buffer_dma.as_buf() };
        self.frame_buffer_dma = Some(frame_buffer_dma);
        Ok(buf)
    }


上面的函數主要完成的工作有如下幾個步驟，其實就是驅動程序給virtio-gpu設備發控制命令，建立好顯存區域：

1. 發出 ``GetDisplayInfo`` 命令，獲得virtio-gpu設備的顯示分辨率;
2. 發出 ``ResourceCreate2D`` 命令，讓設備以分辨率大小（ ``width *height`` ），像素信息（ ``Red/Green/Blue/Alpha`` 各佔1字節大小，即一個像素佔4字節），來配置設備顯示資源；
3. 分配 ``width *height * 4`` 字節的連續物理內存空間作為顯存， 發出 ``ResourceAttachBacking`` 命令，讓設備把顯存附加到設備顯示資源上；
4. 發出 ``SetScanout`` 命令，把設備顯示資源鏈接到顯示掃描輸出上，這樣才能讓顯存的像素信息顯示出來；

到這一步，才算是把virtio-gpu設備初始化完成了。做完這一步後，virtio-gpu設備和設備驅動之間的虛擬隊列接口就打通了，顯示緩衝區也建立好了，就可以進行顯存數據讀寫了。

virtio-gpu設備的I/O操作
------------------------------------------

對初始化好的virtio-gpu設備進行圖形顯示其實很簡單，主要就是兩個步驟：

1. 把要顯示的像素數據寫入到顯存中；
2. 發出刷新命令，讓virtio-gpu在Qemu模擬的顯示區上顯示圖形。

下面簡單代碼完成了對虛擬GPU的圖形顯示：

.. code-block:: Rust
   :linenos:

   // virtio-drivers/src/gpu.rs
   fn virtio_gpu(header: &'static mut VirtIOHeader) {
        ...
        //把像素數據寫入顯存
        for y in 0..height {    //height=800
            for x in 0..width { //width=1280
                let idx = (y * width + x) * 4;
                fb[idx] = x as u8;
                fb[idx + 1] = y as u8;
                fb[idx + 2] = (x + y) as u8;
            }
        }
        // 發出刷新命令
        gpu.flush().expect("failed to flush");

這裡需要注意的是對virtio-gpu進行刷新操作比較耗時，所以我們儘量先把顯示的圖形像素值都寫入顯存中，再發出刷新命令，減少刷新命令的執行次數。


操作系統對接virtio-gpu設備初始化
------------------------------------------

雖然virtio-gpu設備驅動程序已經完成了，但是還需要操作系統對接virtio-gpu設備，才能真正的把virtio-gpu設備驅動程序和操作系統對接起來。這裡以侏羅獵龍操作系統 --Device OS 為例，來介紹virtio-gpu設備在操作系統中的初始化過程。其初始化過程主要包括：

1. 調用virtio-drivers/gpu.rs中提供 ``VirtIOGpu::new()`` 方法，初始化virtio_gpu設備；
2. 建立顯存緩衝區的可變一維數組引用，便於後續寫顯存來顯示圖形；
3. 建立顯示窗口中的光標圖形；
4. 設定表示virtio_gpu設備的全局變量。



先看看操作系統需要建立的表示virtio_gpu設備的全局變量 ``GPU_DEVICE`` ：

.. code-block:: Rust
   :linenos:

    // os/src/drivers/gpu/mod.rs
    pub trait GpuDevice: Send + Sync + Any {
        fn update_cursor(&self); //更新光標，目前暫時沒用
        fn get_framebuffer(&self) -> &mut [u8];
        fn flush(&self);
    }
    pub struct VirtIOGpuWrapper {
        gpu: UPIntrFreeCell<VirtIOGpu<'static, VirtioHal>>,
        fb: &'static [u8],
    }
    lazy_static::lazy_static!(
        pub static ref GPU_DEVICE: Arc<dyn GpuDevice> = Arc::new(VirtIOGpuWrapper::new());
    );


從上面的代碼可以看到，操作系統中表示表示virtio_gpu設備的全局變量 ``GPU_DEVICE`` 的類型是 ``VirtIOGpuWrapper`` ,封裝了來自virtio_derivers 模塊的 ``VirtIOGpu`` 類型，以及一維字節數組引用表示的顯存緩衝區 ``fb`` 。這樣，操作系統內核就可以通過 ``GPU_DEVICE`` 全局變量來訪問gpu_blk設備了。而操作系統對virtio_blk設備的初始化就是調用 ``VirtIOGpuWrapper::<VirtioHal>::new()`` 。


當用戶態應用程序要進行圖形顯示時，至少需要得到操作系統的兩個基本圖形顯示服務。一個是得到顯存在用戶態可訪問的的內存地址，這樣應用程序可以在用戶態把表示圖形的像素值寫入顯存中；第二個是給virtio-gpu設備發出 ``flush`` 刷新指令，這樣virtio-gpu設備能夠更新顯示器中的圖形顯示內容。

為此，操作系統在 ``VirtIOGpuWrapper`` 結構類型中需要實現 ``GpuDevice`` trait，該 trait需要實現兩個函數來支持應用程序所需要的基本顯示服務：

.. code-block:: Rust
   :linenos:

    impl GpuDevice for VirtIOGpuWrapper {
        // 通知virtio-gpu設備更新圖形顯示內容
        fn flush(&self) {
            self.gpu.exclusive_access().flush().unwrap();
        }
        // 得到顯存的基於內核態虛地址的一維字節數組引用
        fn get_framebuffer(&self) -> &mut [u8] {
            unsafe {
                let ptr = self.fb.as_ptr() as *const _ as *mut u8;
                core::slice::from_raw_parts_mut(ptr, self.fb.len())
            }
        }
    ...

接下來，看一下操作系統對virtio-gpu設備的初始化過程：

.. code-block:: Rust
   :linenos:

    // os/src/drivers/gpu/mod.rs
    impl VirtIOGpuWrapper {
        pub fn new() -> Self {
            unsafe {
                // 1. 執行virtio-drivers的gpu.rs中virto-gpu基本初始化
                let mut virtio =
                    VirtIOGpu::<VirtioHal>::new(&mut *(VIRTIO7 as *mut VirtIOHeader)).unwrap();
                // 2. 設置virtio-gpu設備的顯存，初始化顯存的一維字節數組引用    
                let fbuffer = virtio.setup_framebuffer().unwrap();
                let len = fbuffer.len();
                let ptr = fbuffer.as_mut_ptr();
                let fb = core::slice::from_raw_parts_mut(ptr, len);
                // 3. 初始化光標圖像的像素值
                let bmp = Bmp::<Rgb888>::from_slice(BMP_DATA).unwrap();
                let raw = bmp.as_raw();
                let mut b = Vec::new();
                for i in raw.image_data().chunks(3) {
                    let mut v = i.to_vec();
                    b.append(&mut v);
                    if i == [255, 255, 255] {
                        b.push(0x0)
                    } else {
                        b.push(0xff)
                    }
                }
                // 4. 設置virtio-gpu設備的光標圖像
                virtio.setup_cursor(b.as_slice(), 50, 50, 50, 50).unwrap();
                // 5. 返回VirtIOGpuWrapper結構類型
                Self {
                    gpu: UPIntrFreeCell::new(virtio),
                    fb,
                }
        ...

在上述初始化過程中，我們先看到 ``VIRTIO7`` ，這是 Qemu模擬的virtio_gpu設備中I/O寄存器的物理內存地址， ``VirtIOGpu`` 需要這個地址來對 ``VirtIOHeader`` 數據結構所表示的virtio-gpu I/O控制寄存器進行讀寫操作，從而完成對某個具體的virtio-gpu設備的初始化過程。整個初始化過程的步驟如下：

1. 執行virtio-drivers的gpu.rs中virto-gpu基本初始化
2. 設置virtio-gpu設備的顯存，初始化顯存的一維字節數組引用
3. （可選）初始化光標圖像的像素值
4. （可選）設置virtio-gpu設備的光標圖像
5. 返回VirtIOGpuWrapper結構類型

上述步驟的第一步  :ref:`"virto-gpu基本初始化"<term-virtio-driver-gpu-new>` 和第二步 :ref:`設置顯存<term-virtio-driver-gpu-setupfb>` 是核心內容，都由 virtio-drivers中與具體操作系統無關的virtio-gpu裸機驅動實現，極大降低本章從操作系統的代碼複雜性。至此，我們已經完成了操作系統對 virtio-gpu設備的初始化過程，接下來，我們看一下操作系統對virtio-gpu設備的I/O處理過程。

操作系統對接virtio-gpu設備I/O處理
------------------------------------------

操作系統的virtio-gpu驅動的主要功能是給操作系統提供支持，讓運行在用戶態應用能夠顯示圖形。為此，應用程序需要知道可讀寫的顯存在哪裡，並能把更新的像素值寫入顯存。另外還需要能夠通知virtio-gpu設備更新顯示內容。可以看出，這主要與操作系統的進程管理和虛存管理有直接的關係。

在操作系統與virtio-drivers crate中virtio-gpu裸機驅動對接的過程中，需要注意的關鍵問題是操作系統的virtio-gpu驅動如何封裝virtio-blk裸機驅動的基本功能，完成如下服務：

1. 根據virtio-gpu裸機驅動提供的顯存信息，建立應用程序訪問的用戶態顯存地址空間；
2. 實現系統調用，把用戶態顯存地址空間的基址和範圍發給應用程序；
3. 實現系統調用，把更新顯存的命令發給virtio-gpu設備。

這裡我們還是做了一些簡化，即應用程序預先知道了virtio-blk的顯示分辨率為 ``1280x800`` ，採用的是R/G/B/Alpha 像素顯示，即一個像素點佔用4個字節。這樣整個顯存大小為 ``1280x800x4=4096000`` 字節，即大約4000KB，近4MB。

我們先看看圖形應用程序所需要的兩個系統調用：

.. code-block:: Rust
   :linenos:

    // os/src/syscall/mod.rs
    const SYSCALL_FRAMEBUFFER: usize = 2000;
    const SYSCALL_FRAMEBUFFER_FLUSH: usize = 2001;
    // os/src/syscall/gui.rs
    // 顯存的用戶態起始虛擬地址
    const FB_VADDR: usize = 0x10000000;
    pub fn sys_framebuffer() -> isize {
        // 獲得顯存的起始物理頁幀和結束物理頁幀
        let gpu = GPU_DEVICE.clone();
        let fb = gpu.get_framebuffer();
        let len = fb.len();
        let fb_ppn = PhysAddr::from(fb.as_ptr() as usize).floor();
        let fb_end_ppn = PhysAddr::from(fb.as_ptr() as usize + len).ceil();
        // 獲取當前進程的地址空間結構 mem_set
        let current_process = current_process();
        let mut inner = current_process.inner_exclusive_access();
        let mem_set = &mut inner.memory_set;
        // 把顯存的物理頁幀映射到起始地址為FB_VADDR的用戶態虛擬地址空間
        mem_set.push_noalloc(
            MapArea::new(
                (FB_VADDR as usize).into(),
                (FB_VADDR + len as usize).into(),
                MapType::Framed,
                MapPermission::R | MapPermission::W | MapPermission::U,
            ),
            PPNRange::new(fb_ppn, fb_end_ppn),
        );
        // 返回起始地址為FB_VADDR
        FB_VADDR as isize
    }
    // 要求virtio-gpu設備刷新圖形顯示
    pub fn sys_framebuffer_flush() -> isize {
        let gpu = GPU_DEVICE.clone();
        gpu.flush();
        0
    }

有了這兩個系統調用，就可以很容易建立圖形應用程序了。下面這個應用程序，可以在Qemu模擬的屏幕上顯示一個彩色的矩形。

.. code-block:: Rust
   :linenos:

   // user/src/bin/gui_simple.rs
   pub const VIRTGPU_XRES: usize = 1280; // 顯示分辨率的寬度
   pub const VIRTGPU_YRES: usize = 800;  // 顯示分辨率的高度
   pub fn main() -> i32 {
        // 訪問sys_framebuffer系統調用，獲得顯存基址
        let fb_ptr =framebuffer() as *mut u8;
        // 把顯存轉換為一維字節數組
        let fb= unsafe {core::slice::from_raw_parts_mut(fb_ptr as *mut u8, VIRTGPU_XRES*VIRTGPU_YRES*4 as usize)};
        // 更新顯存的像素值
        for y in 0..800 {
            for x in 0..1280 {
                let idx = (y * 1280 + x) * 4;
                fb[idx] = x as u8;
                fb[idx + 1] = y as u8;
                fb[idx + 2] = (x + y) as u8;
            }
        }
        // 訪問sys_framebuffer_flush系統調用，要求virtio-gpu設備刷新圖形顯示
        framebuffer_flush();
        0
   }


到目前為止，看到的操作系統支持工作還是比較簡單的，但其實我們還沒分析如何給應用程序提供顯存虛擬地址空間的。以前章節的操作系統支持應用程序的 :ref:`用戶態地址空間<term-vm-app-addr-space>` ，都是在創建應用程序對應進程的初始化過程中建立，涉及不少工作，具體包括：

- 分配空閒 :ref:`物理頁幀<term-manage-phys-frame>`
- 建立 :ref:`進程地址空間(Address Space)<term-vm-memory-set>` 中的 :ref:`邏輯段（MemArea）<term-vm-map-area>` 
- 建立映射物理頁幀和虛擬頁的 :ref:`頁表<term-create-pagetable>` 

目前這些工作不能直接支持建立用戶態顯存地址空間。主要原因在於，用戶態顯存的物理頁幀分配和物理虛地址頁表映射，都是由virtio-gpu裸機設備驅動程序在設備初始化時完成。在圖形應用進程的創建過程中，不需要再分配顯存的物理頁幀了，只需建立顯存的用戶態虛擬地址空間。

為了支持操作系統把用戶態顯存地址空間的基址發給應用程序，需要對操作系統的虛擬內存管理進行一定的擴展， 即實現 ``sys_framebuffer`` 系統調用中訪問的 ``mem_set.push_noalloc`` 新函數和其它相關函數。


.. code-block:: Rust
   :linenos:

   // os/src/mm/memory_set.rs
   impl MemorySet {
     pub fn push_noalloc(&mut self, mut map_area: MapArea, ppn_range: PPNRange) {
        map_area.map_noalloc(&mut self.page_table, ppn_range);
        self.areas.push(map_area);
     }      
   impl MapArea {
     pub fn map_noalloc(&mut self, page_table: &mut PageTable,ppn_range:PPNRange) {
        for (vpn,ppn) in core::iter::zip(self.vpn_range,ppn_range) {
            self.data_frames.insert(vpn, FrameTracker::new_noalloc(ppn));
            let pte_flags = PTEFlags::from_bits(self.map_perm.bits).unwrap();
            page_table.map(vpn, ppn, pte_flags);
        }
     }
   // os/src/mm/frame_allocator.rs 
   pub struct FrameTracker {
     pub ppn: PhysPageNum,
     pub nodrop: bool,
   }
   impl FrameTracker {
     pub fn new_nowrite(ppn: PhysPageNum) -> Self {
        Self { ppn, nodrop: true }
     }
   impl Drop for FrameTracker {
        fn drop(&mut self) {
            if self.nodrop {
                return;
            }
            frame_dealloc(self.ppn);
        }
   }


這樣，就可以實現把某一塊已分配的物理頁幀映射到進程的用戶態虛擬地址空間，並且在進程退出是否地址空間的物理頁幀時，不會把顯存的物理頁幀給釋放掉。


圖形化應用程序設計
----------------------------------------

現在操作系統有了顯示的彩色圖形顯示功能，也有通過串口接收輸入的功能，我們就可以設計更加豐富多彩的應用了。這裡簡單介紹一個 ``貪吃蛇`` 圖形小遊戲的設計。

.. note:: 
    
   "貪吃蛇"遊戲簡介

   遊戲中的元素主要有蛇和食物組成，蛇的身體是由若干個格子組成的，初始化時蛇的身體只有一格，吃了食物後會增長。食物也是一個格子，代表食物的格子位置隨機產生。遊戲的主要運行邏輯是，蛇可以移動，通過用戶輸入的字母 ``asdw`` 的控制蛇的上下左右移動的方向。用戶通過移動貪吃蛇，並與食物格子位置重合，來增加蛇的身體長度。用戶輸入回車鍵時，遊戲結束。

為了簡化設計，我們移植了 ``embedded-graphics`` 嵌入式圖形庫 [#EMBEDGRAPH]_ 到侏羅獵龍操作系統中，並修改了一個基於此圖形庫的Linux圖形應用 -- embedded-snake-rs [#SNAKEGAME]_ ，讓它在侏羅獵龍操作系統中能夠運行。


移植 ``embedded-graphics`` 嵌入式圖形庫
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``embedded-graphics`` 嵌入式圖形庫給出了很詳細的移植說明， 主要是實現 ``embedded_graphics_core::draw_target::DrawTarget`` trait中的函數接口 ``fn draw_iter<I>(&mut self, pixels: I)`` 。為此需要為圖形應用建立一個能夠表示顯存、像素點特徵和顯示區域的數據結構 ``Display`` 和創建函數 ``new()`` ：


.. code-block:: Rust
    :linenos:

    pub struct Display {
        pub size: Size,
        pub point: Point,
        pub fb: &'static mut [u8],
    }
    impl Display {
        pub fn new(size: Size, point: Point) -> Self {
            let fb_ptr = framebuffer() as *mut u8;
            println!(
                "Hello world from user mode program! 0x{:X} , len {}",
                fb_ptr as usize, VIRTGPU_LEN
            );
            let fb =
                unsafe { core::slice::from_raw_parts_mut(fb_ptr as *mut u8, VIRTGPU_LEN as usize) };
            Self { size, point, fb }
        }
    }

在這個 ``Display`` 結構的基礎上，我們就可以實現 ``DrawTarget`` trait 要求的函數：

.. code-block:: Rust
    :linenos:

    impl OriginDimensions for Display {
        fn size(&self) -> Size {
            self.size
        }
    }

    impl DrawTarget for Display {
        type Color = Rgb888;
        type Error = core::convert::Infallible;

        fn draw_iter<I>(&mut self, pixels: I) -> Result<(), Self::Error>
        where
            I: IntoIterator<Item = embedded_graphics::Pixel<Self::Color>>,
        {
            pixels.into_iter().for_each(|px| {
                let idx = ((self.point.y + px.0.y) * VIRTGPU_XRES as i32 + self.point.x + px.0.x)
                    as usize
                    * 4;
                if idx + 2 >= self.fb.len() {
                    return;
                }
                self.fb[idx] = px.1.b();
                self.fb[idx + 1] = px.1.g();
                self.fb[idx + 2] = px.1.r();
            });
            framebuffer_flush();
            Ok(())
        }
    }


上述的 ``draw_iter()`` 函數實現了對一個由像素元素組成的顯示區域的繪製迭代器，將迭代器中的像素元素繪製到 ``Display`` 結構中的顯存中，並調用 ``framebuffer_flush()`` 函數將顯存中的內容刷新到屏幕上。這樣， ``embedded-graphics`` 嵌入式圖形庫在侏羅獵龍操作系統的移植任務就完成了。


實現貪吃蛇遊戲圖形應用
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``embedded-snake-rs`` 的具體實現大約有200多行代碼，提供了一系列的數據結構，主要的數據結構（包含相關方法實現）包括：

- ``ScaledDisplay`` ：封裝了 ``Dislpay`` 並支持顯示大小可縮放的方塊
- ``Food`` ：會在隨機位置產生並定期消失的"食物"方塊
- ``Snake`` : "貪吃蛇"方塊，長度由一系列的方塊組成，可以通過鍵盤控制方向，碰到食物會增長
- ``SnakeGame`` ：食物和貪吃蛇的遊戲顯示配置和遊戲狀態

有了上述事先準備的數據結構，我們就可以實現貪吃蛇遊戲的主體邏輯了。


.. code-block:: Rust
    :linenos:

    pub fn main() -> i32 {
        // 創建具有virtio-gpu設備顯示內存虛地址的Display結構
        let mut disp = Display::new(Size::new(1280, 800), Point::new(0, 0));
        // 初始化遊戲顯示元素的配置：紅色的蛇、黃色的食物，方格大小為20個像素點
        let mut game = SnakeGame::<20, Rgb888>::new(1280, 800, 20, 20, Rgb888::RED, Rgb888::YELLOW, 50);
        // 清屏
        let _ = disp.clear(Rgb888::BLACK).unwrap();
        // 啟動遊戲循環
        loop {
            if key_pressed() {
                let c = getchar();
                match c {
                    LF => break,
                    CR => break,
                    // 調整蛇行進方向
                    b'w' => game.set_direction(Direction::Up),
                    b's' => game.set_direction(Direction::Down),
                    b'a' => game.set_direction(Direction::Left),
                    b'd' => game.set_direction(Direction::Right),
                    _ => (),
                }
            }
            //繪製遊戲界面
            let _ = disp.clear(Rgb888::BLACK).unwrap();
            game.draw(&mut disp);
            //暫停一小會
            sleep(10);
        }
        0
    }

這裡看到，為了判斷通過串口輸入的用戶是否按鍵，我們擴展了一個系統調用 ``sys_key_pressed`` ：

.. code-block:: Rust
    :linenos:

    // os/src/syscall/input.rs
    pub fn sys_key_pressed()  -> isize {
        let res =!UART.read_buffer_is_empty();
        if res {
            1
        } else {
            0
        }    
    }


這樣，我們結合串口和 ``virtio-gpu`` 兩種外設，並充分利用已有的Rust庫，設計實現了一個 ``貪吃蛇`` 小遊戲（如下圖所示）。至此，基於侏羅獵龍操作系統的圖形應用開發任務就完成了。

.. image:: ../../os-lectures/lec13/figs/gui-snake.png
   :align: center
   :scale: 30 %
   :name: gui-snake

.. [#EMBEDGRAPH] https://github.com/embedded-graphics/embedded-graphics
.. [#SNAKEGAME] https://github.com/libesz/embedded-snake-rs