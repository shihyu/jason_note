練習參考答案
=====================================================

.. toctree::
      :hidden:
      :maxdepth: 4

課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 擴展easy-fs文件系統功能，擴大單個文件的大小，支持三級間接inode。

在修改之前，先看看原始inode的結構：

.. code:: rust

    /// The max number of direct inodes
    const INODE_DIRECT_COUNT: usize = 28;

    #[repr(C)]
    pub struct DiskInode {
        pub size: u32,
        pub direct: [u32; INODE_DIRECT_COUNT],
        pub indirect1: u32,
        pub indirect2: u32,
        type_: DiskInodeType,
    }

    #[derive(PartialEq)]
    pub enum DiskInodeType {
        File,
        Directory,
    }

一個 ``DiskInode`` 在磁盤上佔據128字節的空間。我們考慮加入 ``indirect3`` 字段並縮減 ``INODE_DIRECT_COUNT`` 為27以保持 ``DiskInode`` 的大小不變。此時直接索引可索引13.5KiB的內容，一級間接索引和二級間接索引仍然能索引64KiB和8MiB的內容，而三級間接索引能索引128 * 8MiB = 1GiB的內容。當文件大小大於13.5KiB + 64KiB + 8MiB時，需要用到三級間接索引。

下面的改動都集中在 ``easy-fs/src/layout.rs`` 中。首先修改 ``DiskInode`` 和相關的常量定義。

.. code-block:: rust
    :emphasize-lines: 6

    pub struct DiskInode {
        pub size: u32,
        pub direct: [u32; INODE_DIRECT_COUNT],
        pub indirect1: u32,
        pub indirect2: u32,
        pub indirect3: u32,
        type_: DiskInodeType,
    }

在計算給定文件大小對應的塊總數時，需要新增對三級間接索引的處理。三級間接索引的存在使得二級間接索引所需的塊數不再計入所有的剩餘數據塊。

.. code-block:: rust
    :emphasize-lines: 14

    pub fn total_blocks(size: u32) -> u32 {
        let data_blocks = Self::_data_blocks(size) as usize;
        let mut total = data_blocks as usize;
        // indirect1
        if data_blocks > INODE_DIRECT_COUNT {
            total += 1;
        }
        // indirect2
        if data_blocks > INDIRECT1_BOUND {
            total += 1;
            // sub indirect1
            let level2_extra =
                (data_blocks - INDIRECT1_BOUND + INODE_INDIRECT1_COUNT - 1) / INODE_INDIRECT1_COUNT;
            total += level2_extra.min(INODE_INDIRECT1_COUNT);
        }
        // indirect3
        if data_blocks > INDIRECT2_BOUND {
            let remaining = data_blocks - INDIRECT2_BOUND;
            let level2_extra = (remaining + INODE_INDIRECT2_COUNT - 1) / INODE_INDIRECT2_COUNT;
            let level3_extra = (remaining + INODE_INDIRECT1_COUNT - 1) / INODE_INDIRECT1_COUNT;
            total += 1 + level2_extra + level3_extra;
        }
        total as u32
    }

``DiskInode`` 的 ``get_block_id`` 方法中遇到三級間接索引要額外讀取三次塊緩存。

.. code:: rust

    pub fn get_block_id(&self, inner_id: u32, block_device: &Arc<dyn BlockDevice>) -> u32 {
        let inner_id = inner_id as usize;
        if inner_id < INODE_DIRECT_COUNT {
            // ...
        } else if inner_id < INDIRECT1_BOUND {
            // ...
        } else if inner_id < INDIRECT2_BOUND {
            // ...
        } else { // 對三級間接索引的處理
            let last = inner_id - INDIRECT2_BOUND;
            let indirect1 = get_block_cache(self.indirect3 as usize, Arc::clone(block_device))
                .lock()
                .read(0, |indirect3: &IndirectBlock| {
                    indirect3[last / INODE_INDIRECT2_COUNT]
                });
            let indirect2 = get_block_cache(indirect1 as usize, Arc::clone(block_device))
                .lock()
                .read(0, |indirect2: &IndirectBlock| {
                    indirect2[(last % INODE_INDIRECT2_COUNT) / INODE_INDIRECT1_COUNT]
                });
            get_block_cache(indirect2 as usize, Arc::clone(block_device))
                .lock()
                .read(0, |indirect1: &IndirectBlock| {
                    indirect1[(last % INODE_INDIRECT2_COUNT) % INODE_INDIRECT1_COUNT]
                })
        }
    }

方法 ``increase_size`` 的實現本身比較繁瑣，如果按照原有的一級和二級間接索引的方式實現對三級間接索引的處理，代碼會比較醜陋。實際上多重間接索引是樹結構，變量 ``current_blocks`` 和 ``total_blocks`` 對應著當前樹的葉子數量和目標葉子數量，我們可以用遞歸函數來實現樹的生長。先實現以下的輔助方法：

.. code:: rust

    /// Helper to build tree recursively
    /// extend number of leaves from `src_leaf` to `dst_leaf`
    fn build_tree(
        &self,
        blocks: &mut alloc::vec::IntoIter<u32>,
        block_id: u32,
        mut cur_leaf: usize,
        src_leaf: usize,
        dst_leaf: usize,
        cur_depth: usize,
        dst_depth: usize,
        block_device: &Arc<dyn BlockDevice>,
    ) -> usize {
        if cur_depth == dst_depth {
            return cur_leaf + 1;
        }
        get_block_cache(block_id as usize, Arc::clone(block_device))
            .lock()
            .modify(0, |indirect_block: &mut IndirectBlock| {
                let mut i = 0;
                while i < INODE_INDIRECT1_COUNT && cur_leaf < dst_leaf {
                    if cur_leaf >= src_leaf {
                        indirect_block[i] = blocks.next().unwrap();
                    }
                    cur_leaf = self.build_tree(
                        blocks,
                        indirect_block[i],
                        cur_leaf,
                        src_leaf,
                        dst_leaf,
                        cur_depth + 1,
                        dst_depth,
                        block_device,
                    );
                    i += 1;
                }
            });
        cur_leaf
    }

然後修改方法 ``increase_size``。不要忘記在填充二級間接索引時維護 ``current_blocks`` 的變化，並限制目標索引 ``(a1, b1)`` 的範圍。

.. code:: rust

    /// Increase the size of current disk inode
    pub fn increase_size(
        &mut self,
        new_size: u32,
        new_blocks: Vec<u32>,
        block_device: &Arc<dyn BlockDevice>,
    ) {
        // ...
        // alloc indirect2
        // ...
        // fill indirect2 from (a0, b0) -> (a1, b1)
        // 不要忘記限制 (a1, b1) 的範圍
        // ...
        // alloc indirect3
        if total_blocks > INODE_INDIRECT2_COUNT as u32 {
            if current_blocks == INODE_INDIRECT2_COUNT as u32 {
                self.indirect3 = new_blocks.next().unwrap();
            }
            current_blocks -= INODE_INDIRECT2_COUNT as u32;
            total_blocks -= INODE_INDIRECT2_COUNT as u32;
        } else {
            return;
        }
        // fill indirect3
        self.build_tree(
            &mut new_blocks,
            self.indirect3,
            0,
            current_blocks as usize,
            total_blocks as usize,
            0,
            3,
            block_device,
        );

對方法 ``clear_size`` 的修改與 ``increase_size`` 類似。先實現輔助方法 ``collect_tree_blocks``：

.. code:: rust

    /// Helper to recycle blocks recursively
    fn collect_tree_blocks(
        &self,
        collected: &mut Vec<u32>,
        block_id: u32,
        mut cur_leaf: usize,
        max_leaf: usize,
        cur_depth: usize,
        dst_depth: usize,
        block_device: &Arc<dyn BlockDevice>,
    ) -> usize {
        if cur_depth == dst_depth {
            return cur_leaf + 1;
        }
        get_block_cache(block_id as usize, Arc::clone(block_device))
            .lock()
            .read(0, |indirect_block: &IndirectBlock| {
                let mut i = 0;
                while i < INODE_INDIRECT1_COUNT && cur_leaf < max_leaf {
                    collected.push(indirect_block[i]);
                    cur_leaf = self.collect_tree_blocks(
                        collected,
                        indirect_block[i],
                        cur_leaf,
                        max_leaf,
                        cur_depth + 1,
                        dst_depth,
                        block_device,
                    );
                    i += 1;
                }
            });
        cur_leaf
    }

然後修改方法 ``clear_size``。

.. code:: rust

    /// Clear size to zero and return blocks that should be deallocated.
    /// We will clear the block contents to zero later.
    pub fn clear_size(&mut self, block_device: &Arc<dyn BlockDevice>) -> Vec<u32> {
        // ...
        // indirect2 block
        // ...
        // indirect2
        // 不要忘記限制 (a1, b1) 的範圍
        self.indirect2 = 0;
        // indirect3 block
        assert!(data_blocks <= INODE_INDIRECT3_COUNT);
        if data_blocks > INODE_INDIRECT2_COUNT {
            v.push(self.indirect3);
            data_blocks -= INODE_INDIRECT2_COUNT;
        } else {
            return v;
        }
        // indirect3
        self.collect_tree_blocks(&mut v, self.indirect3, 0, data_blocks, 0, 3, block_device);
        self.indirect3 = 0;
        v
    }

接下來你可以在 ``easy-fs-fuse/src/main.rs`` 中測試easy-fs文件系統的修改，比如讀寫大小超過10MiB的文件。

2. `*` 擴展內核功能，支持stat系統調用，能顯示文件的inode元數據信息。

你將在本章的編程實驗中實現這個功能。

3. `**` 擴展內核功能，支持mmap系統調用，支持對文件的映射，實現基於內存讀寫方式的文件讀寫功能。

.. note:: 這裡只是給出了一種參考實現。mmap本身行為比較複雜，使用你認為合理的方式實現即可。

在第四章的編程實驗中你應該已經實現了mmap的匿名映射功能，這裡我們要實現文件映射。
`mmap <https://man7.org/linux/man-pages/man2/mmap.2.html>`_ 的原型如下：

.. code:: c

    void *mmap(void *addr, size_t length, int prot, int flags,
                    int fd, off_t offset);

其中 ``addr`` 是一個虛擬地址的hint，在映射文件時我們不關心具體的虛擬地址（相當於傳入 ``NULL`` ），這裡我們的系統調用忽略這個參數。 ``prot`` 和 ``flags`` 指定了一些屬性，為簡單起見我們也不要這兩個參數，映射的虛擬內存的屬性直接繼承自文件的讀寫屬性。我們最終保留 ``length`` 、 ``fd`` 和 ``offset`` 三個參數。

考慮最簡單的一種實現方式：mmap調用時隨便選擇一段虛擬地址空間，將它映射到一些隨機的物理頁面上，之後再把文件的對應部分全部讀到內存裡。如果這段映射是可寫的，那麼內核還要在合適的時機（比如調用msync、munmap、進程退出時）把內存裡的東西回寫到文件。

這樣做的問題是被映射的文件可能很大，將映射的區域全部讀入內存可能很慢，而且用戶未必會訪問所有的頁面。這裡可以應用按需分頁的惰性加載策略：先不實際建立虛擬內存到物理內存的映射，當用戶訪問映射的區域時會觸發缺頁異常，我們在處理異常時分配實際的物理頁面並將文件讀入內存。

按照上述方式已經可以實現文件映射了，但讓我們來考慮較為微妙的情況。比如以下的Linux C程序：

.. code:: c

    #include <unistd.h>
    #include <fcntl.h>
    #include <sys/mman.h>
    #include <stdio.h>

    int main()
    {
        char str[] = {"asdbasdq3423423\n"};
        int fd = open("2.txt", O_RDWR | O_CREAT | O_TRUNC, 0664);
        if (fd < 0) {
            printf("open failed\n");
            return -1;
        }

        if (write(fd, str, sizeof(str)) < 0) {
            printf("write failed\n");
            return -1;
        }

        char *p1 = mmap(NULL, sizeof(str), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        char *p2 = mmap(NULL, sizeof(str), PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
        printf("p1 = %p, p2 = %p\n", p1, p2);
        close(fd);
        
        p1[1] = '1';
        p2[2] = '2';
        p2[0] = '2';
        p1[0] = '1';
        printf("content1: %s", p1);
        printf("content2: %s", p2);
        return 0;
    }

一個可能的輸出結果如下：

.. code::

    p1 = 0x7f955a3cf000, p2 = 0x7f955a3a2000
    content1: 112basdq3423423
    content2: 112basdq3423423

可以看到文件的同一段區域被映射到了兩個不同的虛擬地址，對這兩段虛擬內存的修改全部生效（衝突的修改也是最後的可見），修改後再讀出來的內容也相同。這樣的結果是符合直覺的，因為底層的文件只有一個（也與 ``MAP_SHARED`` 有關，由於設置 ``MAP_PRIVATE`` 標誌不會將修改真正寫入文件，我們參考 ``MAP_SHARED`` 的行為）。如果按照上面說的方式將兩個虛擬內存區域映射到不同的物理頁面，那麼對兩個區域的修改無法同時生效，我們也無法確定應該將哪個頁面回寫到文件。這個例子啟示我們， **如果文件映射包含文件的相同部分，那麼相應的虛擬頁面應該映射到相同的物理頁** 。

不幸的是，現有的 ``MapArea`` 類型只含 ``Identical`` 和 ``Framed`` ，不支持不同的虛擬頁面共享物理頁，所以我們需要手動管理一些資源。下面的 ``FileMapping`` 結構描述了一個文件的若干段映射：

.. code:: rust

    pub struct FileMapping {
        file: Arc<Inode>,
        ranges: Vec<MapRange>,
        frames: Vec<FrameTracker>,
        dirty_parts: BTreeSet<usize>, // file segments that need writing back
        map: BTreeMap<usize, PhysPageNum>, // file offset -> ppn
    }

其中 ``file`` 代表被映射的文件，你可能會好奇它的類型為什麼不是一個文件描述符編號或者 ``Arc<dyn File>`` 。首先mmap之後使用的文件描述符可以立即被關閉而不會對文件映射造成任何影響，所以不適合只存放fd編號；其次mmap通常要求映射的文件是常規文件 （例：映射stdin和stdout毫無意義），這裡用 ``Inode`` 來提醒我們這點。 ``ranges`` 裡面存放了若干 ``MapRange`` ，每個都用於描述一段映射區域。 ``frames`` 用於管理實際分配的物理頁幀。 ``dirty_parts`` 記錄了需要回寫的髒頁，注意它實際上用文件內的偏移來表示。 ``map`` 維護文件內偏移到物理頁號的映射。需要注意的是這裡記錄髒頁的方式比較簡單，而且也完全沒有考慮在進程間共享物理頁，你可以使用引用計數等手段進行擴展。

.. code:: rust

    #[derive(Clone)]
    struct MapRange {
        start: VirtAddr,
        len: usize,    // length in bytes
        offset: usize, // offset in file
        perm: MapPermission,
    }

``MapRange`` 描述了一段映射區域。 ``start`` 是該區域的起始虛擬地址， ``offset`` 為其在文件中的偏移， ``perm`` 記錄了該區域的屬性。

前面提到過，我們的mmap忽略掉作為hint的 ``addr`` 參數，那這裡的虛擬地址填什麼呢？一般來說64位架構具有大到用不完的虛擬地址空間，用一個簡單的線性分配器隨便分配虛擬地址即可。

.. code:: rust

    /// Base virtual address for mmap
    pub const MMAP_AREA_BASE: usize = 0x0000_0001_0000_0000; // 隨便選的基址，挑塊沒人用的

    /// A naive linear virtual address space allocator
    pub struct VirtualAddressAllocator {
        cur_va: VirtAddr,
    }

    impl VirtualAddressAllocator {
        /// Create a new allocator with given base virtual address
        pub fn new(base: usize) -> Self {
            Self {
                cur_va: base.into(),
            }
        }

        /// Allocate a virtual address area
        pub fn alloc(&mut self, len: usize) -> VirtAddr {
            let start = self.cur_va;
            let end: VirtAddr = (self.cur_va.0 + len).into();
            self.cur_va = end.ceil().into();
            start
        }

        // 不必釋放
    }

然後把 ``VirtualAddressAllocator`` 和 ``FileMapping`` 放進 ``TaskControlBlockInner`` 裡。為簡單起見，fork時不考慮這兩個字段的複製和映射的共享。

.. code-block:: rust
    :caption: ``os/src/task/task.rs``
    :emphasize-lines: 11,12

    pub struct TaskControlBlockInner {
        pub trap_cx_ppn: PhysPageNum,
        pub base_size: usize,
        pub task_cx: TaskContext,
        pub task_status: TaskStatus,
        pub memory_set: MemorySet,
        pub parent: Option<Weak<TaskControlBlock>>,
        pub children: Vec<Arc<TaskControlBlock>>,
        pub exit_code: i32,
        pub fd_table: Vec<Option<Arc<dyn File + Send + Sync>>>,
        pub mmap_va_allocator: VirtualAddressAllocator,
        pub file_mappings: Vec<FileMapping>,
    }

下面來添加mmap系統調用：

.. code:: rust

    /// This is a simplified version of mmap which only supports file-backed mapping
    pub fn sys_mmap(fd: usize, len: usize, offset: usize) -> isize {
        if len == 0 {
            // invalid length
            return -1;
        }
        if (offset & (PAGE_SIZE - 1)) != 0 {
            // offset must be page size aligned
            return -1;
        }

        let task = current_task().unwrap();
        let mut tcb = task.inner_exclusive_access();
        if fd >= tcb.fd_table.len() {
            return -1;
        }
        if tcb.fd_table[fd].is_none() {
            return -1;
        }

        let fp = tcb.fd_table[fd].as_ref().unwrap();
        let opt_inode = fp.as_any().downcast_ref::<OSInode>();
        if opt_inode.is_none() {
            // must be a regular file
            return -1;
        }

        let inode = opt_inode.unwrap();
        let perm = parse_permission(inode);
        let file = inode.clone_inner_inode();
        if offset >= file.get_size() {
            // file offset exceeds size limit
            return -1;
        }

        let start = tcb.mmap_va_allocator.alloc(len);
        let mappings = &mut tcb.file_mappings;
        if let Some(m) = find_file_mapping(mappings, &file) {
            m.push(start, len, offset, perm);
        } else {
            let mut m = FileMapping::new_empty(file);
            m.push(start, len, offset, perm);
            mappings.push(m);
        }
        start.0 as isize
    }

這裡面有不少無聊的參數檢查和輔助函數，就不詳細介紹了。總之這個系統調用實際做的事情只有維護對應的 ``FileMapping`` 結構，實際的工作被推遲到缺頁異常處理例程中。

.. code-block:: rust
    :caption: ``os/src/trap/mod.rs``
    :emphasize-lines: 17

    #[no_mangle]
    /// handle an interrupt, exception, or system call from user space
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::UserEnvCall) => {
                // ...
            }
            Trap::Exception(Exception::StoreFault)
            | Trap::Exception(Exception::StorePageFault)
            | Trap::Exception(Exception::InstructionFault)
            | Trap::Exception(Exception::InstructionPageFault)
            | Trap::Exception(Exception::LoadFault)
            | Trap::Exception(Exception::LoadPageFault) => {
                if !handle_page_fault(stval) {
                    println!(
                        "[kernel] {:?} in application, bad addr = {:#x}, bad instruction = {:#x}, kernel killed it.",
                        scause.cause(),
                        stval,
                        current_trap_cx().sepc,
                    );
                    // page fault exit code
                    exit_current_and_run_next(-2);
                }
            }
            Trap::Exception(Exception::IllegalInstruction) => {
                // ...
            }
            Trap::Interrupt(Interrupt::SupervisorTimer) => {
                // ...
            }
            _ => {
                panic!(
                    "Unsupported trap {:?}, stval = {:#x}!",
                    scause.cause(),
                    stval
                );
            }
        }
        trap_return();
    }

我們在這裡嘗試處理缺頁異常，如果 ``handle_page_fault`` 返回 ``true`` 表明異常已經被處理，否則內核仍然會殺死當前進程。

.. code-block:: rust
    :linenos:

    /// Try to handle page fault caused by demand paging
    /// Returns whether this page fault is fixed
    pub fn handle_page_fault(fault_addr: usize) -> bool {
        let fault_va: VirtAddr = fault_addr.into();
        let fault_vpn = fault_va.floor();
        let task = current_task().unwrap();
        let mut tcb = task.inner_exclusive_access();

        if let Some(pte) = tcb.memory_set.translate(fault_vpn) {
            if pte.is_valid() {
                return false; // fault va already mapped, we cannot handle this
            }
        }

        match tcb.file_mappings.iter_mut().find(|m| m.contains(fault_va)) {
            Some(mapping) => {
                let file = Arc::clone(&mapping.file);
                // fix vm mapping
                let (ppn, range, shared) = mapping.map(fault_va).unwrap();
                tcb.memory_set.map(fault_vpn, ppn, range.perm);

                if !shared {
                    // load file content
                    let file_size = file.get_size();
                    let file_offset = range.file_offset(fault_vpn);
                    assert!(file_offset < file_size);

                    // let va_offset = range.va_offset(fault_vpn);
                    // let va_len = range.len - va_offset;
                    // Note: we do not limit `read_len` with `va_len`
                    // consider two overlapping areas with different lengths

                    let read_len = PAGE_SIZE.min(file_size - file_offset);
                    file.read_at(file_offset, &mut ppn.get_bytes_array()[..read_len]);
                }
                true
            }
            None => false,
        }
    }

- ``handle_page_fault`` 的9~13行先檢查觸發異常的虛擬內存頁是否已經映射到物理頁面，如果是則說明此異常並非源自惰性按需分頁（比如寫入只讀頁），這個問題不歸我們管，直接返回 ``false``。
- 接下來的第15行檢查出錯的虛擬地址是否在映射區域內，如果是我們才上手來處理。

在實際的修復過程中：
- 第19行先調用 ``FileMapping`` 的 ``map`` 方法建立目標虛擬地址到物理頁面的映射；
- 第20行將新的映射關係添加到頁表；
- 第22~35行處理文件讀入。注意實際的文件讀取只發生在物理頁面的引用計數從0變為1的時候，存在共享的情況下再讀取文件可能會覆蓋掉用戶對內存的修改。

``FileMapping`` 的 ``map`` 方法實現如下：

.. code-block:: rust
    :linenos:

    impl FileMapping {
        /// Create mapping for given virtual address
        fn map(&mut self, va: VirtAddr) -> Option<(PhysPageNum, MapRange, bool)> {
            // Note: currently virtual address ranges never intersect
            let vpn = va.floor();
            for range in &self.ranges {
                if !range.contains(va) {
                    continue;
                }
                let offset = range.file_offset(vpn);
                let (ppn, shared) = match self.map.get(&offset) {
                    Some(&ppn) => (ppn, true),
                    None => {
                        let frame = frame_alloc().unwrap();
                        let ppn = frame.ppn;
                        self.frames.push(frame);
                        self.map.insert(offset, ppn);
                        (ppn, false)
                    }
                };
                if range.perm.contains(MapPermission::W) {
                    self.dirty_parts.insert(offset);
                }
                return Some((ppn, range.clone(), shared));
            }
            None
        }
    }

- 第6~9行先找到包含目標虛擬地址的映射區域；
- 第10行計算虛擬地址對應的文件內偏移；
- 第11~20行先查詢此文件偏移是否對應已分配的物理頁，如果沒有則分配一個物理頁幀並記錄映射關係；
- 第21~23行檢查此映射區域是否有寫入權限，如果有則將對應的物理頁面標記為髒頁。這個處理實際上比較粗糙，有些沒有被真正寫入的頁面也被視為髒頁，導致最後會有多餘的文件回寫。你也可以考慮不維護髒頁信息，而是通過檢查頁表項中由硬件維護的 Dirty 位來確定哪些是真正的髒頁。

修復後用戶進程重新執行觸發缺頁異常的指令，此時物理頁裡存放了文件的內容，這樣用戶就實現了以讀取內存的方式來讀取文件。最後來處理被修改的髒頁的同步，給 ``FileMapping`` 添加 ``sync`` 方法：

.. code-block:: rust
    :linenos:

    impl FileMapping {
        /// Write back all dirty pages
        pub fn sync(&self) {
            let file_size = self.file.get_size();
            for &offset in self.dirty_parts.iter() {
                let ppn = self.map.get(&offset).unwrap();
                if offset < file_size {
                    // WARNING: this can still cause garbage written
                    //  to file when sharing physical page
                    let va_len = self
                        .ranges
                        .iter()
                        .map(|r| {
                            if r.offset <= offset && offset < r.offset + r.len {
                                PAGE_SIZE.min(r.offset + r.len - offset)
                            } else {
                                0
                            }
                        })
                        .max()
                        .unwrap();
                    let write_len = va_len.min(file_size - offset);

                    self.file
                        .write_at(offset, &ppn.get_bytes_array()[..write_len]);
                }
            }
        }
    }

這個方法將所有潛在的髒物理頁內容回寫至文件。第10~22行的計算主要為了限制寫入內容的長度，以避免垃圾被意外寫入文件。

剩下的問題是何時調用 ``sync`` 。正常來說munmap、msync是同步點，你可以自行實現這兩個系統調用，這裡我們把它放在進程退出之前：

.. code-block:: rust
    :caption: ``os/src/task/mod.rs``
    :emphasize-lines: 10-13

    /// Exit the current 'Running' task and run the next task in task list.
    pub fn exit_current_and_run_next(exit_code: i32) {
        let task = take_current_task().unwrap();
        // ...
        let mut inner = task.inner_exclusive_access();
        // ...
        inner.children.clear();
        // deallocate user space
        inner.memory_set.recycle_data_pages();
        // write back dirty pages
        for mapping in inner.file_mappings.iter() {
            mapping.sync();
        }
        drop(inner);
        // **** release current PCB
        // drop task manually to maintain rc correctly
        drop(task);
        // ...
    }

這樣我們就實現了基於內存讀寫方式的文件讀寫功能。可以看到mmap不是魔法，內核悄悄幫你完成了實際的文件讀寫。

4. `**` 擴展easy-fs文件系統功能，支持二級目錄結構。可擴展：支持N級目錄結構。

實際上easy-fs現有的代碼支持目錄的存在，只不過整個文件系統只有根目錄一個目錄，我們考慮放寬現有代碼的一些限制。

原本的 ``easy-fs/src/vfs.rs`` 中有一個用於在當前目錄下創建常規文件的 ``create`` 方法，我們給它加個參數幷包裝一下：

.. code-block:: rust
    :caption: ``easy-fs/src/vfs.rs``
    :emphasize-lines: 3,22,51-54,56-59

    impl Inode {
        /// Create inode under current inode by name
        fn create_inode(&self, name: &str, inode_type: DiskInodeType) -> Option<Arc<Inode>> {
            let mut fs = self.fs.lock();
            let op = |root_inode: &DiskInode| {
                // assert it is a directory
                assert!(root_inode.is_dir());
                // has the file been created?
                self.find_inode_id(name, root_inode)
            };
            if self.read_disk_inode(op).is_some() {
                return None;
            }
            // create a new file
            // alloc a inode with an indirect block
            let new_inode_id = fs.alloc_inode();
            // initialize inode
            let (new_inode_block_id, new_inode_block_offset) = fs.get_disk_inode_pos(new_inode_id);
            get_block_cache(new_inode_block_id as usize, Arc::clone(&self.block_device))
                .lock()
                .modify(new_inode_block_offset, |new_inode: &mut DiskInode| {
                    new_inode.initialize(inode_type);
                });
            self.modify_disk_inode(|root_inode| {
                // append file in the dirent
                let file_count = (root_inode.size as usize) / DIRENT_SZ;
                let new_size = (file_count + 1) * DIRENT_SZ;
                // increase size
                self.increase_size(new_size as u32, root_inode, &mut fs);
                // write dirent
                let dirent = DirEntry::new(name, new_inode_id);
                root_inode.write_at(
                    file_count * DIRENT_SZ,
                    dirent.as_bytes(),
                    &self.block_device,
                );
            });

            let (block_id, block_offset) = fs.get_disk_inode_pos(new_inode_id);
            block_cache_sync_all();
            // return inode
            Some(Arc::new(Self::new(
                block_id,
                block_offset,
                self.fs.clone(),
                self.block_device.clone(),
            )))
            // release efs lock automatically by compiler
        }

        /// Create regular file under current inode
        pub fn create(&self, name: &str) -> Option<Arc<Inode>> {
            self.create_inode(name, DiskInodeType::File)
        }

        /// Create directory under current inode
        pub fn create_dir(&self, name: &str) -> Option<Arc<Inode>> {
            self.create_inode(name, DiskInodeType::Directory)
        }
    }

這樣我們就可以在一個目錄底下調用 ``create_dir`` 創建新目錄了（笑）。本質上我們什麼也沒改，我們再改改其它方法裝裝樣子：

.. code-block:: rust
    :caption: ``easy-fs/src/vfs.rs``
    :emphasize-lines: 7-9,28,41

    impl Inode {
        /// List inodes under current inode
        pub fn ls(&self) -> Vec<String> {
            let _fs = self.fs.lock();
            self.read_disk_inode(|disk_inode| {
                let mut v: Vec<String> = Vec::new();
                if disk_inode.is_file() {
                    return v;
                }

                let file_count = (disk_inode.size as usize) / DIRENT_SZ;
                for i in 0..file_count {
                    let mut dirent = DirEntry::empty();
                    assert_eq!(
                        disk_inode.read_at(i * DIRENT_SZ, dirent.as_bytes_mut(), &self.block_device,),
                        DIRENT_SZ,
                    );
                    v.push(String::from(dirent.name()));
                }
                v
            })
        }

        /// Write data to current inode
        pub fn write_at(&self, offset: usize, buf: &[u8]) -> usize {
            let mut fs = self.fs.lock();
            let size = self.modify_disk_inode(|disk_inode| {
                assert!(disk_inode.is_file());

                self.increase_size((offset + buf.len()) as u32, disk_inode, &mut fs);
                disk_inode.write_at(offset, buf, &self.block_device)
            });
            block_cache_sync_all();
            size
        }

        /// Clear the data in current inode
        pub fn clear(&self) {
            let mut fs = self.fs.lock();
            self.modify_disk_inode(|disk_inode| {
                assert!(disk_inode.is_file());

                let size = disk_inode.size;
                let data_blocks_dealloc = disk_inode.clear_size(&self.block_device);
                assert!(data_blocks_dealloc.len() == DiskInode::total_blocks(size) as usize);
                for data_block in data_blocks_dealloc.into_iter() {
                    fs.dealloc_data(data_block);
                }
            });
            block_cache_sync_all();
        }
    }

對一個普通文件的inode調用 ``ls`` 方法毫無意義，但為了保持接口不變，我們返回一個空 ``Vec``。隨意地清空或寫入目錄文件都會損壞目錄結構，這裡直接在 ``write_at`` 和 ``clear`` 方法中斷言，你也可以改成其它的錯誤處理方式。

接下來是實際一點的修改（有，但不多）：我們讓 ``find`` 方法支持簡單的相對路徑（不含“.”和“..”）。

.. code-block:: rust
    :caption: ``easy-fs/src/vfs.rs``

    impl Inode {
        /// Find inode under current inode by **path**
        pub fn find(&self, path: &str) -> Option<Arc<Inode>> {
            let fs = self.fs.lock();
            let mut block_id = self.block_id as u32;
            let mut block_offset = self.block_offset;
            for name in path.split('/').filter(|s| !s.is_empty()) {
                let inode_id = get_block_cache(block_id as usize, self.block_device.clone())
                    .lock()
                    .read(block_offset, |disk_inode: &DiskInode| {
                        if disk_inode.is_file() {
                            return None;
                        }
                        self.find_inode_id(name, disk_inode)
                    });
                if inode_id.is_none() {
                    return None;
                }
                (block_id, block_offset) = fs.get_disk_inode_pos(inode_id.unwrap());
            }
            Some(Arc::new(Self::new(
                block_id,
                block_offset,
                self.fs.clone(),
                self.block_device.clone(),
            )))
        }
    }

最後在 ``easy-fs-fuse/src/main.rs`` 裡試試我們添加的新特性：

.. code-block:: rust
    :caption: ``easy-fs-fuse/src/main.rs``

    fn read_string(file: &Arc<Inode>) -> String {
        let mut read_buffer = [0u8; 512];
        let mut offset = 0usize;
        let mut read_str = String::new();
        loop {
            let len = file.read_at(offset, &mut read_buffer);
            if len == 0 {
                break;
            }
            offset += len;
            read_str.push_str(core::str::from_utf8(&read_buffer[..len]).unwrap());
        }
        read_str
    }

    fn tree(inode: &Arc<Inode>, name: &str, depth: usize) {
        for _ in 0..depth {
            print!("  ");
        }
        println!("{}", name);
        for name in inode.ls() {
            let child = inode.find(&name).unwrap();
            tree(&child, &name, depth + 1);
        }
    }

    #[test]
    fn efs_dir_test() -> std::io::Result<()> {
        let block_file = Arc::new(BlockFile(Mutex::new({
            let f = OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .open("target/fs.img")?;
            f.set_len(8192 * 512).unwrap();
            f
        })));
        EasyFileSystem::create(block_file.clone(), 4096, 1);
        let efs = EasyFileSystem::open(block_file.clone());
        let root = Arc::new(EasyFileSystem::root_inode(&efs));
        root.create("f1");
        root.create("f2");

        let d1 = root.create_dir("d1").unwrap();

        let f3 = d1.create("f3").unwrap();
        let d2 = d1.create_dir("d2").unwrap();

        let f4 = d2.create("f4").unwrap();
        tree(&root, "/", 0);

        let f3_content = "3333333";
        let f4_content = "4444444444444444444";
        f3.write_at(0, f3_content.as_bytes());
        f4.write_at(0, f4_content.as_bytes());

        assert_eq!(read_string(&d1.find("f3").unwrap()), f3_content);
        assert_eq!(read_string(&root.find("/d1/f3").unwrap()), f3_content);
        assert_eq!(read_string(&d2.find("f4").unwrap()), f4_content);
        assert_eq!(read_string(&d1.find("d2/f4").unwrap()), f4_content);
        assert_eq!(read_string(&root.find("/d1/d2/f4").unwrap()), f4_content);
        assert!(f3.find("whatever").is_none());
        Ok(())
    }

如果你覺得這個練習不夠過癮，可以試試下面的任務：

- 讓easy-fs支持包含“.”和“..”的相對路徑。你可以在目錄文件裡存放父目錄的inode。
- 在內核裡給進程加上當前路徑信息，然後實現chdir和getcwd。當然，也可以順便補上openat和mkdir。
- 在easy-fs中實現rename和mv的功能。在目錄文件中刪掉一些目錄項也許要實現 ``decrease_size`` 或者類似刪除的東西，但也可以考慮用刪除標記這種常見的手段讓一個目錄項變得“不存在”。

問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `*` 文件系統的功能是什麼？

   將數據以文件的形式持久化保存在存儲設備上。

2. `**` 目前的文件系統只有單級目錄，假設想要支持多級文件目錄，請描述你設想的實現方式，描述合理即可。

   允許在目錄項中存在目錄（原本只能存在普通文件）即可。

3. `**` 軟鏈接和硬鏈接是幹什麼的？有什麼區別？當刪除一個軟鏈接或硬鏈接時分別會發生什麼？

   軟硬鏈接的作用都是給一個文件以"別名"，使得不同的多個路徑可以指向同一個文件。當刪除軟鏈接時候，對文件沒有任何影響，當刪除硬鏈接時，文件的引用計數會被減一，若引用計數為0，則該文件所佔據的磁盤空間將會被回收。

4. `***` 在有了多級目錄之後，我們就也可以為一個目錄增加硬鏈接了。在這種情況下，文件樹中是否可能出現環路(軟硬鏈接都可以，鼓勵多嘗試)？你認為應該如何解決？請在你喜歡的系統上實現一個環路，描述你的實現方式以及系統提示、實際測試結果。

   是可以出現環路的，一種可能的解決方式是在訪問文件的時候檢查自己遍歷的路徑中是否有重複的inode，並在發現環路時返回錯誤。

5. `*` 目錄是一類特殊的文件，存放的是什麼內容？用戶可以自己修改目錄內容嗎？

   存放的是目錄中的文件列表以及他們對應的inode，通常而言用戶不能自己修改目錄的內容，但是可以通過操作目錄（如mv裡面的文件）的方式間接修改。

6. `**` 在實際操作系統中，如Linux，為什麼會存在大量的文件系統類型？

   因為不同的文件系統有著不同的特性，比如對於特定種類的存儲設備的優化，或是快照和多設備管理等高級特性，適用於不同的使用場景。

7. `**` 可以把文件控制塊放到目錄項中嗎？這樣做有什麼優缺點？

   可以，是對於小目錄可以減少一次磁盤訪問，提升性能，但是對大目錄而言會使得在目錄中查找文件的性能降低。

8. `**` 為什麼要同時維護進程的打開文件表和操作系統的打開文件表？這兩個打開文件表有什麼區別和聯繫？

   多個進程可能會同時打開同一個文件，操作系統級的打開文件表可以加快後續的打開操作，但同時由於每個進程打開文件時使用的訪問模式或是偏移量不同，所以還需要進程的打開文件表另外記錄。

9. `**` 文件分配的三種方式是如何組織文件數據塊的？各有什麼特徵（存儲、文件讀寫、可靠性）？

   連續分配：實現簡單、存取速度快，但是難以動態增加文件大小，長期使用後會產生大量無法使用（過小而無法放入大文件）碎片空間。

   鏈接分配：可以處理文件大小的動態增長，也不會出現碎片，但是隻能按順序訪問文件中的塊，同時一旦有一個塊損壞，後面的其他塊也無法讀取，可靠性差。

   索引分配：可以隨機訪問文件中的偏移量，但是對於大文件需要實現多級索引，實現較為複雜。

10. `**` 如果一個程序打開了一個文件，寫入了一些數據，但是沒有及時關閉，可能會有什麼後果？如果打開文件後，又進一步發出了讀文件的系統調用，操作系統中各個組件是如何相互協作完成整個讀文件的系統調用的？

   (若也沒有flush的話）假如此時操作系統崩潰，尚處於內存緩衝區中未寫入磁盤的數據將會丟失，同時也會佔用文件描述符，造成資源的浪費。首先是系統調用處理的部分，將這一請求轉發給文件系統子系統，文件系統子系統再將其轉發給塊設備子系統，最後再由塊設備子系統轉發給實際的磁盤驅動程序讀取數據，最終返回給程序。

11. `***` 文件系統是一個操作系統必要的組件嗎？是否可以將文件系統放到用戶態？這樣做有什麼好處？操作系統需要提供哪些基本支持？

    不是，如在本章之前的rCore就沒有文件系統。可以，如在Linux下就有FUSE這樣的框架可以實現這一點。這樣可以使得文件系統的實現更為靈活，開發與調試更為簡便。操作系統需要提供一個註冊用戶態文件系統實現的機制，以及將收到的文件系統相關係統調用轉發給註冊的用戶態進程的支持。

