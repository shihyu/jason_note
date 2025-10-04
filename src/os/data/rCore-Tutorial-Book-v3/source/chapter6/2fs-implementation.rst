簡易文件系統 easy-fs
=======================================

本節導讀
---------------------------------------

本節我們介紹一個簡易文件系統的實現 -- easy-fs。作為一個文件系統而言，它的磁盤佈局（為了敘述方便，我們用磁盤來指代一系列持久存儲設備）體現在磁盤上各扇區的內容上，而它解析磁盤佈局得到的邏輯目錄樹結構則是通過內存上的數據結構來訪問的，這意味著它要同時涉及到對磁盤和對內存的訪問。它們的訪問方式是不同的，對於內存直接通過一條指令即可直接讀寫內存相應的位置，而磁盤的話需要用軟件的方式向磁盤發出請求來間接進行讀寫。因此，我們也要特別注意哪些數據結構是存儲在磁盤上，哪些數據結構是存儲在內存中的，這樣在實現的時候才不會引起混亂。

松耦合模塊化設計思路
---------------------------------------

大家可以看到，本章的內核功能越來越多，代碼量也越來越大（但僅僅是Linux代碼量的萬分之一左右）。為了減少同學學習內核的分析理解成本，我們需要讓內核的各個部分之間儘量松耦合，所以easy-fs 被從內核中分離出來，它的實現分成兩個不同的 crate ：

- ``easy-fs`` 為簡易文件系統的核心部分，它是一個庫形式 crate，實現一種簡單的文件系統磁盤佈局；
- ``easy-fs-fuse`` 是一個能在開發環境（如 Ubuntu）中運行的應用程序，它可以對 ``easy-fs`` 進行測試，或者將為我們內核開發的應用打包為一個 easy-fs 格式的文件系統鏡像。

這樣，整個easy-fs文件系統的設計開發可以按照應用程序庫的開發過程來完成。而且在開發完畢後，可直接放到內核中，形成有文件系統支持的新內核。


能做到這一點，是由於我們在easy-fs設計上，採用了松耦合模塊化設計思路。easy-fs與底層設備驅動之間通過抽象接口 ``BlockDevice`` 來連接，避免了與設備驅動的綁定。easy-fs通過Rust提供的alloc crate來隔離了操作系統內核的內存管理，避免了直接調用內存管理的內核函數。在底層驅動上，採用的是輪詢的方式訪問 ``virtio_blk`` 虛擬磁盤設備，從而避免了訪問外設中斷的相關內核函數。easy-fs在設計中避免了直接訪問進程相關的數據和函數，從而隔離了操作系統內核的進程管理。

同時，easy-fs本身也劃分成不同的層次，形成層次化和模塊化的設計架構。``easy-fs`` crate 自下而上大致可以分成五個不同的層次：

1. 磁盤塊設備接口層：定義了以塊大小為單位對磁盤塊設備進行讀寫的trait接口
2. 塊緩存層：在內存中緩存磁盤塊的數據，避免頻繁讀寫磁盤
3. 磁盤數據結構層：磁盤上的超級塊、位圖、索引節點、數據塊、目錄項等核心數據結構和相關處理
4. 磁盤塊管理器層：合併了上述核心數據結構和磁盤佈局所形成的磁盤文件系統數據結構，以及基於這些結構的創建/打開文件系統的相關處理和磁盤塊的分配和回收處理
5. 索引節點層：管理索引節點（即文件控制塊）數據結構，並實現文件創建/文件打開/文件讀寫等成員函數來向上支持文件操作相關的系統調用

大家也許覺得有五層架構的文件系統是一個很複雜的軟件。其實，相對於面向Qemu模擬器的操作系統內核源碼所佔的2400行左右代碼，它只有900行左右的代碼，佔總代碼量的27%。且由於其代碼邏輯其實是一種自下而上的線性思維，屬於傳統的常規編程。相對於異常/中斷/系統調用的特權級切換，進程管理中的進程上下文切換，內存管理中的頁表地址映射等涉及異常控制流和硬件訪問的非常規編程，文件系統的設計實現其實更容易理解。

塊設備接口層
---------------------------------------

定義設備驅動需要實現的塊讀寫接口 ``BlockDevice`` trait的塊設備接口層代碼在 ``block_dev.rs`` 中。

在 ``easy-fs`` 庫的最底層聲明瞭一個塊設備的抽象接口 ``BlockDevice`` ：

.. code-block:: rust

    // easy-fs/src/block_dev.rs

    pub trait BlockDevice : Send + Sync + Any {
        fn read_block(&self, block_id: usize, buf: &mut [u8]);
        fn write_block(&self, block_id: usize, buf: &[u8]);
    }

它需要實現兩個抽象方法：

- ``read_block`` 將編號為 ``block_id`` 的塊從磁盤讀入內存中的緩衝區 ``buf`` ；
- ``write_block`` 將內存中的緩衝區 ``buf`` 中的數據寫入磁盤編號為 ``block_id`` 的塊。

在 ``easy-fs`` 中並沒有一個實現了 ``BlockDevice`` Trait 的具體類型。因為塊設備僅支持以塊為單位進行隨機讀寫，所以需要由具體的塊設備驅動來實現這兩個方法，實際上這是需要由文件系統的使用者（比如操作系統內核或直接測試 ``easy-fs`` 文件系統的 ``easy-fs-fuse`` 應用程序）提供並接入到 ``easy-fs`` 庫的。 ``easy-fs`` 庫的塊緩存層會調用這兩個方法，進行塊緩存的管理。這也體現了 ``easy-fs`` 的泛用性：它可以訪問實現了 ``BlockDevice`` Trait 的塊設備驅動程序。

.. note::

    **塊與扇區**

    實際上，塊和扇區是兩個不同的概念。 **扇區** (Sector) 是塊設備隨機讀寫的數據單位，通常每個扇區為 512 字節。而塊是文件系統存儲文件時的數據單位，每個塊的大小等同於一個或多個扇區。之前提到過 Linux 的Ext4文件系統的單個塊大小默認為 4096 字節。在我們的 easy-fs 實現中一個塊和一個扇區同為 512 字節，因此在後面的講解中我們不再區分扇區和塊的概念。

塊緩存層
---------------------------------------

實現磁盤塊緩存功能的塊緩存層的代碼在 ``block_cache.rs`` 中。

由於操作系統頻繁讀寫速度緩慢的磁盤塊會極大降低系統性能，因此常見的手段是先通過 ``read_block`` 將一個塊上的數據從磁盤讀到內存中的一個緩衝區中，這個緩衝區中的內容是可以直接讀寫的，那麼後續對這個數據塊的大部分訪問就可以在內存中完成了。如果緩衝區中的內容被修改了，那麼後續還需要通過 ``write_block`` 將緩衝區中的內容寫回到磁盤塊中。

事實上，無論站在代碼實現魯棒性還是性能的角度，將這些緩衝區合理的管理起來都是很有必要的。一種完全不進行任何管理的模式可能是：每當要對一個磁盤塊進行讀寫的時候，都通過 ``read_block`` 將塊數據讀取到一個 *臨時* 創建的緩衝區，並在進行一些操作之後（可選地）將緩衝區的內容寫回到磁盤塊。從性能上考慮，我們需要儘可能降低實際塊讀寫（即 ``read/write_block`` ）的次數，因為每一次調用它們都會產生大量開銷。要做到這一點，關鍵就在於對塊讀寫操作進行 **合併** 。例如，如果一個塊已經被讀到緩衝區中了，那麼我們就沒有必要再讀一遍，直接用已有的緩衝區就行了；同時，對於緩衝區中的同一個塊的多次修改沒有必要每次都寫回磁盤，只需等所有的修改都結束之後統一寫回磁盤即可。

當磁盤上的數據結構比較複雜的時候，很難通過應用來合理地規劃塊讀取/寫入的時機。這不僅可能涉及到複雜的參數傳遞，稍有不慎還有可能引入同步性問題(目前可以暫時忽略)：即一個塊緩衝區修改後的內容在後續的同一個塊讀操作中不可見，這很致命但又難以調試。

因此，我們的做法是將緩衝區統一管理起來。當我們要讀寫一個塊的時候，首先就是去全局管理器中查看這個塊是否已被緩存到內存緩衝區中。如果是這樣，則在一段連續時間內對於一個塊進行的所有操作均是在同一個固定的緩衝區中進行的，這解決了同步性問題。此外，通過 ``read/write_block`` 進行塊實際讀寫的時機完全交給塊緩存層的全局管理器處理，上層子系統無需操心。全局管理器會盡可能將更多的塊操作合併起來，並在必要的時機發起真正的塊實際讀寫。

塊緩存
+++++++++++++++++++++++++++++++++++++++++

塊緩存 ``BlockCache`` 的定義如下：

.. code-block:: rust

    // easy-fs/src/lib.rs

    pub const BLOCK_SZ: usize = 512;

    // easy-fs/src/block_cache.rs

    pub struct BlockCache {
        cache: [u8; BLOCK_SZ],
        block_id: usize,
        block_device: Arc<dyn BlockDevice>,
        modified: bool,
    }

其中：

- ``cache`` 是一個 512 字節的數組，表示位於內存中的緩衝區；
- ``block_id`` 記錄了這個塊緩存來自於磁盤中的塊的編號；
- ``block_device`` 是一個底層塊設備的引用，可通過它進行塊讀寫；
- ``modified`` 記錄這個塊從磁盤載入內存緩存之後，它有沒有被修改過。

當我們創建一個 ``BlockCache`` 的時候，這將觸發一次 ``read_block`` 將一個塊上的數據從磁盤讀到緩衝區 ``cache`` ：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    impl BlockCache {
        /// Load a new BlockCache from disk.
        pub fn new(
            block_id: usize, 
            block_device: Arc<dyn BlockDevice>
        ) -> Self {
            let mut cache = [0u8; BLOCK_SZ];
            block_device.read_block(block_id, &mut cache);
            Self {
                cache,
                block_id,
                block_device,
                modified: false,
            }
        }
    }

一旦磁盤塊已經存在於內存緩存中，CPU 就可以直接訪問磁盤塊數據了：

.. code-block:: rust
    :linenos:

    // easy-fs/src/block_cache.rs

    impl BlockCache {
        fn addr_of_offset(&self, offset: usize) -> usize {
            &self.cache[offset] as *const _ as usize
        }

        pub fn get_ref<T>(&self, offset: usize) -> &T where T: Sized {
            let type_size = core::mem::size_of::<T>();
            assert!(offset + type_size <= BLOCK_SZ);
            let addr = self.addr_of_offset(offset);
            unsafe { &*(addr as *const T) } 
        }

        pub fn get_mut<T>(&mut self, offset: usize) -> &mut T where T: Sized {
            let type_size = core::mem::size_of::<T>();
            assert!(offset + type_size <= BLOCK_SZ);
            self.modified = true;
            let addr = self.addr_of_offset(offset);
            unsafe { &mut *(addr as *mut T) }
        }
    }

- ``addr_of_offset`` 可以得到一個 ``BlockCache`` 內部的緩衝區中指定偏移量 ``offset`` 的字節地址；
- ``get_ref`` 是一個泛型方法，它可以獲取緩衝區中的位於偏移量 ``offset`` 的一個類型為 ``T`` 的磁盤上數據結構的不可變引用。該泛型方法的 Trait Bound 限制類型 ``T`` 必須是一個編譯時已知大小的類型，我們通過 ``core::mem::size_of::<T>()`` 在編譯時獲取類型 ``T`` 的大小，並確認該數據結構被整個包含在磁盤塊及其緩衝區之內。這裡編譯器會自動進行生命週期標註，約束返回的引用的生命週期不超過 ``BlockCache`` 自身，在使用的時候我們會保證這一點。
- ``get_mut`` 與 ``get_ref`` 的不同之處在於， ``get_mut`` 會獲取磁盤上數據結構的可變引用，由此可以對數據結構進行修改。由於這些數據結構目前位於內存中的緩衝區中，我們需要將 ``BlockCache`` 的 ``modified`` 標記為 true 表示該緩衝區已經被修改，之後需要將數據寫回磁盤塊才能真正將修改同步到磁盤。

``BlockCache`` 的設計也體現了 RAII 思想， 它管理著一個緩衝區的生命週期。當 ``BlockCache`` 的生命週期結束之後緩衝區也會被從內存中回收，這個時候 ``modified`` 標記將會決定數據是否需要寫回磁盤：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    impl BlockCache {
        pub fn sync(&mut self) {
            if self.modified {
                self.modified = false;
                self.block_device.write_block(self.block_id, &self.cache);
            }
        }
    }

    impl Drop for BlockCache {
        fn drop(&mut self) {
            self.sync()
        }
    }

在 ``BlockCache`` 被 ``drop`` 的時候，它會首先調用 ``sync`` 方法，如果自身確實被修改過的話才會將緩衝區的內容寫回磁盤。事實上， ``sync`` 並不是只有在 ``drop`` 的時候才會被調用。在 Linux 中，通常有一個後臺進程負責定期將內存中緩衝區的內容寫回磁盤。另外有一個 ``sys_fsync`` 系統調用可以讓應用主動通知內核將一個文件的修改同步回磁盤。由於我們的實現比較簡單， ``sync`` 僅會在 ``BlockCache`` 被 ``drop`` 時才會被調用。

我們可以將 ``get_ref/get_mut`` 進一步封裝為更為易用的形式：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    impl BlockCache {
        pub fn read<T, V>(&self, offset: usize, f: impl FnOnce(&T) -> V) -> V {
            f(self.get_ref(offset))
        }

        pub fn modify<T, V>(&mut self, offset:usize, f: impl FnOnce(&mut T) -> V) -> V {
            f(self.get_mut(offset))
        }
    }

它們的含義是：在 ``BlockCache`` 緩衝區偏移量為 ``offset`` 的位置獲取一個類型為 ``T`` 的磁盤上數據結構的不可變/可變引用（分別對應 ``read/modify`` ），並讓它執行傳入的閉包 ``f`` 中所定義的操作。注意 ``read/modify`` 的返回值是和傳入閉包的返回值相同的，因此相當於 ``read/modify`` 構成了傳入閉包 ``f`` 的一層執行環境，讓它能夠綁定到一個緩衝區上執行。

這裡我們傳入閉包的類型為 ``FnOnce`` ，這是因為閉包裡面的變量被捕獲的方式涵蓋了不可變引用/可變引用/和 move 三種可能性，故而我們需要選取範圍最廣的 ``FnOnce`` 。參數中的 ``impl`` 關鍵字體現了一種類似泛型的靜態分發功能。

我們很快將展示 ``read/modify`` 接口如何在後續的開發中提供便利。

塊緩存全局管理器
+++++++++++++++++++++++++++++++++++++++++

為了避免在塊緩存上浪費過多內存，我們希望內存中同時只能駐留有限個磁盤塊的緩衝區：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    const BLOCK_CACHE_SIZE: usize = 16;

塊緩存全局管理器的功能是：當我們要對一個磁盤塊進行讀寫時，首先看它是否已經被載入到內存緩存中了，如果已經被載入的話則直接返回，否則需要先讀取磁盤塊的數據到內存緩存中。此時，如果內存中駐留的磁盤塊緩衝區的數量已滿，則需要遵循某種緩存替換算法將某個塊的緩存從內存中移除，再將剛剛讀到的塊數據加入到內存緩存中。我們這裡使用一種類 FIFO 的簡單緩存替換算法，因此在管理器中只需維護一個隊列：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    use alloc::collections::VecDeque;

    pub struct BlockCacheManager {
        queue: VecDeque<(usize, Arc<Mutex<BlockCache>>)>,
    }

    impl BlockCacheManager {
        pub fn new() -> Self {
            Self { queue: VecDeque::new() }
        }
    }

隊列 ``queue`` 中管理的是塊編號和塊緩存的二元組。塊編號的類型為 ``usize`` ，而塊緩存的類型則是一個 ``Arc<Mutex<BlockCache>>`` 。這是一個此前頻頻提及到的 Rust 中的經典組合，它可以同時提供共享引用和互斥訪問。這裡的共享引用意義在於塊緩存既需要在管理器 ``BlockCacheManager`` 保留一個引用，還需要以引用的形式返回給塊緩存的請求者讓它可以對塊緩存進行訪問。而互斥訪問在單核上的意義在於提供內部可變性通過編譯，在多核環境下則可以幫助我們避免可能的併發衝突。事實上，一般情況下我們需要在更上層提供保護措施避免兩個線程同時對一個塊緩存進行讀寫，因此這裡只是比較謹慎的留下一層保險。


.. warning::

    Rust Pattern卡片： ``Arc<Mutex<?>>`` 

    先看下Arc和Mutex的正確配合可以達到支持多線程安全讀寫數據對象。如果需要多線程共享所有權的數據對象，則只用Arc即可。如果需要修改 ``T`` 類型中某些成員變量 ``member`` ，那直接採用 ``Arc<Mutex<T>>`` ，並在修改的時候通過  ``obj.lock().unwrap().member = xxx`` 的方式是可行的，但這種編程模式的同步互斥的粒度太大，可能對互斥性能的影響比較大。為了減少互斥性能開銷，其實只需要在 ``T`` 類型中的需要被修改的成員變量上加 ``Mutex<_>`` 即可。如果成員變量也是一個數據結構，還包含更深層次的成員變量，那應該繼續下推到最終需要修改的成員變量上去添加 ``Mutex`` 。
    

``get_block_cache`` 方法嘗試從塊緩存管理器中獲取一個編號為 ``block_id`` 的塊的塊緩存，如果找不到，會從磁盤讀取到內存中，還有可能會發生緩存替換：

.. code-block:: rust
    :linenos:

    // easy-fs/src/block_cache.rs

    impl BlockCacheManager {
        pub fn get_block_cache(
            &mut self,
            block_id: usize,
            block_device: Arc<dyn BlockDevice>,
        ) -> Arc<Mutex<BlockCache>> {
            if let Some(pair) = self.queue
                .iter()
                .find(|pair| pair.0 == block_id) {
                    Arc::clone(&pair.1)
            } else {
                // substitute
                if self.queue.len() == BLOCK_CACHE_SIZE {
                    // from front to tail
                    if let Some((idx, _)) = self.queue
                        .iter()
                        .enumerate()
                        .find(|(_, pair)| Arc::strong_count(&pair.1) == 1) {
                        self.queue.drain(idx..=idx);
                    } else {
                        panic!("Run out of BlockCache!");
                    }
                }
                // load block into mem and push back
                let block_cache = Arc::new(Mutex::new(
                    BlockCache::new(block_id, Arc::clone(&block_device))
                ));
                self.queue.push_back((block_id, Arc::clone(&block_cache)));
                block_cache
            }
        }
    }

- 第 9 行會遍歷整個隊列試圖找到一個編號相同的塊緩存，如果找到了，會將塊緩存管理器中保存的塊緩存的引用複製一份並返回；
- 第 13 行對應找不到的情況，此時必須將塊從磁盤讀入內存中的緩衝區。在實際讀取之前，需要判斷管理器保存的塊緩存數量是否已經達到了上限。如果達到了上限（第 15 行）才需要執行緩存替換算法，丟掉某個塊緩存並空出一個空位。這裡使用一種類 FIFO 算法：每加入一個塊緩存時要從隊尾加入；要替換時則從隊頭彈出。但此時隊頭對應的塊緩存可能仍在使用：判斷的標誌是其強引用計數 :math:`\geq 2` ，即除了塊緩存管理器保留的一份副本之外，在外面還有若干份副本正在使用。因此，我們的做法是從隊頭遍歷到隊尾找到第一個強引用計數恰好為 1 的塊緩存並將其替換出去。
  
  那麼是否有可能出現隊列已滿且其中所有的塊緩存都正在使用的情形呢？事實上，只要我們的上限 ``BLOCK_CACHE_SIZE`` 設置的足夠大，超過所有應用同時訪問的塊總數上限，那麼這種情況永遠不會發生。但是，如果我們的上限設置不足，內核將 panic （基於簡單內核設計的思路）。
- 第 27 行開始我們創建一個新的塊緩存（會觸發 ``read_block`` 進行塊讀取）並加入到隊尾，最後返回給請求者。

接下來需要創建 ``BlockCacheManager`` 的全局實例：

.. code-block:: rust

    // easy-fs/src/block_cache.rs

    lazy_static! {
        pub static ref BLOCK_CACHE_MANAGER: Mutex<BlockCacheManager> = Mutex::new(
            BlockCacheManager::new()
        );
    }

    pub fn get_block_cache(
        block_id: usize,
        block_device: Arc<dyn BlockDevice>
    ) -> Arc<Mutex<BlockCache>> {
        BLOCK_CACHE_MANAGER.lock().get_block_cache(block_id, block_device)
    }

這樣對於其他模塊而言，就可以直接通過 ``get_block_cache`` 方法來請求塊緩存了。這裡需要指出的是，它返回的是一個 ``Arc<Mutex<BlockCache>>`` ，調用者需要通過 ``.lock()`` 獲取裡層互斥鎖 ``Mutex`` 才能對最裡面的 ``BlockCache`` 進行操作，比如通過 ``read/modify`` 訪問緩衝區裡面的磁盤數據結構。

磁盤佈局及磁盤上數據結構
---------------------------------------

磁盤數據結構層的代碼在 ``layout.rs`` 和 ``bitmap.rs`` 中。

對於一個文件系統而言，最重要的功能是如何將一個邏輯上的文件目錄樹結構映射到磁盤上，決定磁盤上的每個塊應該存儲文件相關的哪些數據。為了更容易進行管理和更新，我們需要將磁盤上的數據組織為若干種不同的磁盤上數據結構，併合理安排它們在磁盤中的位置。

easy-fs 磁盤佈局概述
+++++++++++++++++++++++++++++++++++++++

在 easy-fs 磁盤佈局中，按照塊編號從小到大順序地分成 5 個不同屬性的連續區域：

- 最開始的區域的長度為一個塊，其內容是 easy-fs **超級塊** (Super Block)。超級塊內以魔數的形式提供了文件系統合法性檢查功能，同時還可以定位其他連續區域的位置。
- 第二個區域是一個索引節點位圖，長度為若干個塊。它記錄了後面的索引節點區域中有哪些索引節點已經被分配出去使用了，而哪些還尚未被分配出去。
- 第三個區域是索引節點區域，長度為若干個塊。其中的每個塊都存儲了若干個索引節點。
- 第四個區域是一個數據塊位圖，長度為若干個塊。它記錄了後面的數據塊區域中有哪些數據塊已經被分配出去使用了，而哪些還尚未被分配出去。
- 最後的區域則是數據塊區域，顧名思義，其中的每一個已經分配出去的塊保存了文件或目錄中的具體數據內容。

easy-fs 的磁盤佈局如下圖所示：

.. image:: 文件系統佈局.png

**索引節點** (Inode, Index Node) 是文件系統中的一種重要數據結構。邏輯目錄樹結構中的每個文件和目錄都對應一個 inode ，我們前面提到的文件系統實現中，文件/目錄的底層編號實際上就是指 inode 編號。在 inode 中不僅包含了我們通過 ``stat`` 工具能夠看到的文件/目錄的元數據（大小/訪問權限/類型等信息），還包含實際保存對應文件/目錄數據的數據塊（位於最後的數據塊區域中）的索引信息，從而能夠找到文件/目錄的數據被保存在磁盤的哪些塊中。從索引方式上看，同時支持直接索引和間接索引。

每個區域中均存儲著不同的磁盤數據結構， ``easy-fs`` 文件系統能夠對磁盤中的數據進行解釋並將其結構化。下面我們分別對它們進行介紹。

easy-fs 超級塊
+++++++++++++++++++++++++++++++++++++++

超級塊 ``SuperBlock`` 的內容如下：

.. code-block:: rust

    // easy-fs/src/layout.rs

    #[repr(C)]
    pub struct SuperBlock {
        magic: u32,
        pub total_blocks: u32,
        pub inode_bitmap_blocks: u32,
        pub inode_area_blocks: u32,
        pub data_bitmap_blocks: u32,
        pub data_area_blocks: u32,
    }

其中， ``magic`` 是一個用於文件系統合法性驗證的魔數， ``total_block`` 給出文件系統的總塊數。注意這並不等同於所在磁盤的總塊數，因為文件系統很可能並沒有佔據整個磁盤。後面的四個字段則分別給出 easy-fs 佈局中後四個連續區域的長度各為多少個塊。

下面是它實現的方法：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl SuperBlock {
        pub fn initialize(
            &mut self,
            total_blocks: u32,
            inode_bitmap_blocks: u32,
            inode_area_blocks: u32,
            data_bitmap_blocks: u32,
            data_area_blocks: u32,
        ) {
            *self = Self {
                magic: EFS_MAGIC,
                total_blocks,
                inode_bitmap_blocks,
                inode_area_blocks,
                data_bitmap_blocks,
                data_area_blocks,
            }
        }
        pub fn is_valid(&self) -> bool {
            self.magic == EFS_MAGIC
        }
    }

- ``initialize`` 可以在創建一個 easy-fs 的時候對超級塊進行初始化，注意各個區域的塊數是以參數的形式傳入進來的，它們的劃分是更上層的磁盤塊管理器需要完成的工作。
- ``is_valid`` 則可以通過魔數判斷超級塊所在的文件系統是否合法。

``SuperBlock`` 是一個磁盤上數據結構，它就存放在磁盤上編號為 0 的塊的起始處。

位圖
+++++++++++++++++++++++++++++++++++++++

在 easy-fs 佈局中存在兩類不同的位圖，分別對索引節點和數據塊進行管理。每個位圖都由若干個塊組成，每個塊大小為 512 bytes，即 4096 bits。每個 bit 都代表一個索引節點/數據塊的分配狀態， 0 意味著未分配，而 1 則意味著已經分配出去。位圖所要做的事情是通過基於 bit 為單位的分配（尋找一個為 0 的bit位並設置為 1）和回收（將bit位清零）來進行索引節點/數據塊的分配和回收。

.. code-block:: rust

    // easy-fs/src/bitmap.rs

    pub struct Bitmap {
        start_block_id: usize,
        blocks: usize,
    }

    impl Bitmap {
        pub fn new(start_block_id: usize, blocks: usize) -> Self {
            Self {
                start_block_id,
                blocks,
            }
        }
    }

位圖 ``Bitmap`` 中僅保存了它所在區域的起始塊編號以及區域的長度為多少個塊。通過 ``new`` 方法可以新建一個位圖。注意 ``Bitmap`` 自身是駐留在內存中的，但是它能夠表示索引節點/數據塊區域中的那些磁盤塊的分配情況。磁盤塊上位圖區域的數據則是要以磁盤數據結構 ``BitmapBlock`` 的格式進行操作：

.. code-block:: rust

    // easy-fs/src/bitmap.rs

    type BitmapBlock = [u64; 64];

``BitmapBlock`` 是一個磁盤數據結構，它將位圖區域中的一個磁盤塊解釋為長度為 64 的一個 ``u64`` 數組， 每個 ``u64`` 打包了一組 64 bits，於是整個數組包含 :math:`64\times 64=4096` bits，且可以以組為單位進行操作。

首先來看 ``Bitmap`` 如何分配一個bit：

.. code-block:: rust
    :linenos:

    // easy-fs/src/bitmap.rs
    
    const BLOCK_BITS: usize = BLOCK_SZ * 8;
    
    impl Bitmap {
        pub fn alloc(&self, block_device: &Arc<dyn BlockDevice>) -> Option<usize> {
            for block_id in 0..self.blocks {
                let pos = get_block_cache(
                    block_id + self.start_block_id as usize,
                    Arc::clone(block_device),
                )
                .lock()
                .modify(0, |bitmap_block: &mut BitmapBlock| {
                    if let Some((bits64_pos, inner_pos)) = bitmap_block
                        .iter()
                        .enumerate()
                        .find(|(_, bits64)| **bits64 != u64::MAX)
                        .map(|(bits64_pos, bits64)| {
                            (bits64_pos, bits64.trailing_ones() as usize)
                        }) {
                        // modify cache
                        bitmap_block[bits64_pos] |= 1u64 << inner_pos;
                        Some(block_id * BLOCK_BITS + bits64_pos * 64 + inner_pos as usize)
                    } else {
                        None
                    }
                });
                if pos.is_some() {
                    return pos;
                }
            }
            None
        }
    }

其主要思路是遍歷區域中的每個塊，再在每個塊中以bit組（每組 64 bits）為單位進行遍歷，找到一個尚未被全部分配出去的組，最後在裡面分配一個bit。它將會返回分配的bit所在的位置，等同於索引節點/數據塊的編號。如果所有bit均已經被分配出去了，則返回 ``None`` 。

第 7 行枚舉區域中的每個塊（編號為 ``block_id`` ），在循環內部我們需要讀寫這個塊，在塊內嘗試找到一個空閒的bit並置 1 。一旦涉及到塊的讀寫，就需要用到塊緩存層提供的接口：

- 第 8 行我們調用 ``get_block_cache`` 獲取塊緩存，注意我們傳入的塊編號是區域起始塊編號 ``start_block_id`` 加上區域內的塊編號 ``block_id`` 得到的塊設備上的塊編號。
- 第 12 行我們通過 ``.lock()`` 獲取塊緩存的互斥鎖從而可以對塊緩存進行訪問。
- 第 13 行我們使用到了 ``BlockCache::modify`` 接口。它傳入的偏移量 ``offset`` 為 0，這是因為整個塊上只有一個 ``BitmapBlock`` ，它的大小恰好為 512 字節。因此我們需要從塊的開頭開始才能訪問到完整的 ``BitmapBlock`` 。同時，傳給它的閉包需要顯式聲明參數類型為 ``&mut BitmapBlock`` ，不然的話， ``BlockCache`` 的泛型方法 ``modify/get_mut`` 無法得知應該用哪個類型來解析塊上的數據。在聲明之後，編譯器才能在這裡將兩個方法中的泛型 ``T`` 實例化為具體類型 ``BitmapBlock`` 。
  
  總結一下，這裡 ``modify`` 的含義就是：從緩衝區偏移量為 0 的位置開始將一段連續的數據（數據的長度隨具體類型而定）解析為一個 ``BitmapBlock`` 並要對該數據結構進行修改。在閉包內部，我們可以使用這個 ``BitmapBlock`` 的可變引用 ``bitmap_block`` 對它進行訪問。 ``read/get_ref`` 的用法完全相同，後面將不再贅述。
- 閉包的主體位於第 14~26 行。它嘗試在 ``bitmap_block`` 中找到一個空閒的bit並返回其位置，如果不存在的話則返回 ``None`` 。它的思路是，遍歷每 64 bits構成的組（一個 ``u64`` ），如果它並沒有達到 ``u64::MAX`` （即 :math:`2^{64}-1` ），則通過 ``u64::trailing_ones`` 找到最低的一個 0 並置為 1 。如果能夠找到的話，bit組的編號將保存在變量 ``bits64_pos`` 中，而分配的bit在組內的位置將保存在變量 ``inner_pos`` 中。在返回分配的bit編號的時候，它的計算方式是 ``block_id*BLOCK_BITS+bits64_pos*64+inner_pos`` 。注意閉包中的 ``block_id`` 並不在閉包的參數列表中，因此它是從外部環境（即自增 ``block_id`` 的循環）中捕獲到的。

我們一旦在某個塊中找到一個空閒的bit併成功分配，就不再考慮後續的塊。第 28 行體現了提前返回的思路。

.. warning::

    **Rust 語法卡片：閉包**

    閉包是持有外部環境變量的函數。所謂外部環境, 就是指創建閉包時所在的詞法作用域。Rust中定義的閉包，按照對外部環境變量的使用方式（借用、複製、轉移所有權），分為三個類型: Fn、FnMut、FnOnce。Fn類型的閉包會在閉包內部以共享借用的方式使用環境變量；FnMut類型的閉包會在閉包內部以獨佔借用的方式使用環境變量；而FnOnce類型的閉包會在閉包內部以所有者的身份使用環境變量。由此可見，根據閉包內使用環境變量的方式，即可判斷創建出來的閉包的類型。


接下來看 ``Bitmap`` 如何回收一個bit：

.. code-block:: rust

    // easy-fs/src/bitmap.rs

    /// Return (block_pos, bits64_pos, inner_pos)
    fn decomposition(mut bit: usize) -> (usize, usize, usize) {
        let block_pos = bit / BLOCK_BITS;
        bit = bit % BLOCK_BITS;
        (block_pos, bit / 64, bit % 64)
    }

    impl Bitmap {
        pub fn dealloc(&self, block_device: &Arc<dyn BlockDevice>, bit: usize) {
            let (block_pos, bits64_pos, inner_pos) = decomposition(bit);
            get_block_cache(
                block_pos + self.start_block_id,
                Arc::clone(block_device)
            ).lock().modify(0, |bitmap_block: &mut BitmapBlock| {
                assert!(bitmap_block[bits64_pos] & (1u64 << inner_pos) > 0);
                bitmap_block[bits64_pos] -= 1u64 << inner_pos;
            });
        }
    }

``dealloc`` 方法首先調用 ``decomposition`` 函數將bit編號 ``bit`` 分解為區域中的塊編號 ``block_pos`` 、塊內的組編號 ``bits64_pos`` 以及組內編號 ``inner_pos`` 的三元組，這樣就能精確定位待回收的bit，隨後將其清零即可。

磁盤上索引節點
+++++++++++++++++++++++++++++++++++++++

在磁盤上的索引節點區域，每個塊上都保存著若干個索引節點 ``DiskInode`` ：

.. code-block:: rust

    // easy-fs/src/layout.rs

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

每個文件/目錄在磁盤上均以一個 ``DiskInode`` 的形式存儲。其中包含文件/目錄的元數據： ``size`` 表示文件/目錄內容的字節數， ``type_`` 表示索引節點的類型 ``DiskInodeType`` ，目前僅支持文件 ``File`` 和目錄 ``Directory`` 兩種類型。其餘的 ``direct/indirect1/indirect2`` 都是存儲文件內容/目錄內容的數據塊的索引，這也是索引節點名字的由來。

為了儘可能節約空間，在進行索引的時候，塊的編號用一個 ``u32`` 存儲。索引方式分成直接索引和間接索引兩種：

- 當文件很小的時候，只需用到直接索引， ``direct`` 數組中最多可以指向 ``INODE_DIRECT_COUNT`` 個數據塊，當取值為 28 的時候，通過直接索引可以找到 14KiB 的內容。
- 當文件比較大的時候，不僅直接索引的 ``direct`` 數組裝滿，還需要用到一級間接索引 ``indirect1`` 。它指向一個一級索引塊，這個塊也位於磁盤佈局的數據塊區域中。這個一級索引塊中的每個 ``u32`` 都用來指向數據塊區域中一個保存該文件內容的數據塊，因此，最多能夠索引 :math:`\frac{512}{4}=128` 個數據塊，對應 64KiB 的內容。
- 當文件大小超過直接索引和一級索引支持的容量上限 78KiB 的時候，就需要用到二級間接索引 ``indirect2`` 。它指向一個位於數據塊區域中的二級索引塊。二級索引塊中的每個 ``u32`` 指向一個不同的一級索引塊，這些一級索引塊也位於數據塊區域中。因此，通過二級間接索引最多能夠索引 :math:`128\times 64\text{KiB}=8\text{MiB}` 的內容。

為了充分利用空間，我們將 ``DiskInode`` 的大小設置為 128 字節，每個塊正好能夠容納 4 個 ``DiskInode`` 。在後續需要支持更多類型的元數據的時候，可以適當縮減直接索引 ``direct`` 的塊數，並將節約出來的空間用來存放其他元數據，仍可保證 ``DiskInode`` 的總大小為 128 字節。

通過 ``initialize`` 方法可以初始化一個 ``DiskInode`` 為一個文件或目錄：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DiskInode {
        /// indirect1 and indirect2 block are allocated only when they are needed.
        pub fn initialize(&mut self, type_: DiskInodeType) {
            self.size = 0;
            self.direct.iter_mut().for_each(|v| *v = 0);
            self.indirect1 = 0;
            self.indirect2 = 0;
            self.type_ = type_;
        }
    }

需要注意的是， ``indirect1/2`` 均被初始化為 0 。因為最開始文件內容的大小為 0 字節，並不會用到一級/二級索引。為了節約空間，內核會按需分配一級/二級索引塊。此外，直接索引 ``direct`` 也被清零。

``is_file`` 和 ``is_dir`` 兩個方法可以用來確認 ``DiskInode`` 的類型為文件還是目錄：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DiskInode {
        pub fn is_dir(&self) -> bool {
            self.type_ == DiskInodeType::Directory
        }
        pub fn is_file(&self) -> bool {
            self.type_ == DiskInodeType::File
        }
    }

``get_block_id`` 方法體現了 ``DiskInode`` 最重要的數據塊索引功能，它可以從索引中查到它自身用於保存文件內容的第 ``block_id`` 個數據塊的塊編號，這樣後續才能對這個數據塊進行訪問：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 10,12,18

    // easy-fs/src/layout.rs

    const INODE_INDIRECT1_COUNT: usize = BLOCK_SZ / 4;
    const INDIRECT1_BOUND: usize = DIRECT_BOUND + INODE_INDIRECT1_COUNT;
    type IndirectBlock = [u32; BLOCK_SZ / 4];

    impl DiskInode {
        pub fn get_block_id(&self, inner_id: u32, block_device: &Arc<dyn BlockDevice>) -> u32 {
            let inner_id = inner_id as usize;
            if inner_id < INODE_DIRECT_COUNT {
                self.direct[inner_id]
            } else if inner_id < INDIRECT1_BOUND {
                get_block_cache(self.indirect1 as usize, Arc::clone(block_device))
                    .lock()
                    .read(0, |indirect_block: &IndirectBlock| {
                        indirect_block[inner_id - INODE_DIRECT_COUNT]
                    })
            } else {
                let last = inner_id - INDIRECT1_BOUND;
                let indirect1 = get_block_cache(
                    self.indirect2 as usize,
                    Arc::clone(block_device)
                )
                .lock()
                .read(0, |indirect2: &IndirectBlock| {
                    indirect2[last / INODE_INDIRECT1_COUNT]
                });
                get_block_cache(
                    indirect1 as usize,
                    Arc::clone(block_device)
                )
                .lock()
                .read(0, |indirect1: &IndirectBlock| {
                    indirect1[last % INODE_INDIRECT1_COUNT]
                })
            }
        }
    }

這裡需要說明的是：

- 第 10/12/18 行分別利用直接索引/一級索引和二級索引，具體選用哪種索引方式取決於 ``block_id`` 所在的區間。
- 在對一個索引塊進行操作的時候，我們將其解析為磁盤數據結構 ``IndirectBlock`` ，實質上就是一個 ``u32`` 數組，每個都指向一個下一級索引塊或者數據塊。
- 對於二級索引的情況，需要先查二級索引塊找到掛在它下面的一級索引塊，再通過一級索引塊找到數據塊。

在對文件/目錄初始化之後，它的 ``size`` 均為 0 ，此時並不會索引到任何數據塊。它需要通過 ``increase_size`` 方法逐步擴充容量。在擴充的時候，自然需要一些新的數據塊來作為索引塊或是保存內容的數據塊。我們需要先編寫一些輔助方法來確定在容量擴充的時候額外需要多少塊：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DiskInode {
        /// Return block number correspond to size.
        pub fn data_blocks(&self) -> u32 {
            Self::_data_blocks(self.size)
        }
        fn _data_blocks(size: u32) -> u32 {
            (size + BLOCK_SZ as u32 - 1) / BLOCK_SZ as u32
        }
        /// Return number of blocks needed include indirect1/2.
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
                total += (data_blocks - INDIRECT1_BOUND + INODE_INDIRECT1_COUNT - 1) / INODE_INDIRECT1_COUNT;
            }
            total as u32
        }
        pub fn blocks_num_needed(&self, new_size: u32) -> u32 {
            assert!(new_size >= self.size);
            Self::total_blocks(new_size) - Self::total_blocks(self.size)
        }
    }

``data_blocks`` 方法可以計算為了容納自身 ``size`` 字節的內容需要多少個數據塊。計算的過程只需用 ``size`` 除以每個塊的大小 ``BLOCK_SZ`` 並向上取整。而 ``total_blocks`` 不僅包含數據塊，還需要統計索引塊。計算的方法也很簡單，先調用 ``data_blocks`` 得到需要多少數據塊，再根據數據塊數目所處的區間統計索引塊即可。 ``blocks_num_needed`` 可以計算將一個 ``DiskInode`` 的 ``size`` 擴容到 ``new_size`` 需要額外多少個數據和索引塊。這隻需要調用兩次 ``total_blocks`` 作差即可。

下面給出 ``increase_size`` 方法的接口：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DiskInode {
        pub fn increase_size(
            &mut self,
            new_size: u32,
            new_blocks: Vec<u32>,
            block_device: &Arc<dyn BlockDevice>,
        );
    }

其中 ``new_size`` 表示容量擴充之後的文件大小； ``new_blocks`` 是一個保存了本次容量擴充所需塊編號的向量，這些塊都是由上層的磁盤塊管理器負責分配的。 ``increase_size`` 的實現有些複雜，在這裡不詳細介紹。大致的思路是按照直接索引、一級索引再到二級索引的順序進行擴充。

有些時候我們還需要清空文件的內容並回收所有數據和索引塊。這是通過 ``clear_size`` 方法來實現的：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DiskInode {
        /// Clear size to zero and return blocks that should be deallocated.
        ///
        /// We will clear the block contents to zero later.
        pub fn clear_size(&mut self, block_device: &Arc<dyn BlockDevice>) -> Vec<u32>;
    }

它會將回收的所有塊的編號保存在一個向量中返回給磁盤塊管理器。它的實現原理和 ``increase_size`` 一樣也分為多個階段，在這裡不展開。

接下來需要考慮通過 ``DiskInode`` 來讀寫它索引的那些數據塊中的數據。這些數據可以被視為一個字節序列，而每次都是選取其中的一段連續區間進行操作，以 ``read_at`` 為例：

.. code-block:: rust
    :linenos:

    // easy-fs/src/layout.rs

    type DataBlock = [u8; BLOCK_SZ];

    impl DiskInode {
        pub fn read_at(
            &self,
            offset: usize,
            buf: &mut [u8],
            block_device: &Arc<dyn BlockDevice>,
        ) -> usize {
            let mut start = offset;
            let end = (offset + buf.len()).min(self.size as usize);
            if start >= end {
                return 0;
            }
            let mut start_block = start / BLOCK_SZ;
            let mut read_size = 0usize;
            loop {
                // calculate end of current block
                let mut end_current_block = (start / BLOCK_SZ + 1) * BLOCK_SZ;
                end_current_block = end_current_block.min(end);
                // read and update read size
                let block_read_size = end_current_block - start;
                let dst = &mut buf[read_size..read_size + block_read_size];
                get_block_cache(
                    self.get_block_id(start_block as u32, block_device) as usize,
                    Arc::clone(block_device),
                )
                .lock()
                .read(0, |data_block: &DataBlock| {
                    let src = &data_block[start % BLOCK_SZ..start % BLOCK_SZ + block_read_size];
                    dst.copy_from_slice(src);
                });
                read_size += block_read_size;
                // move to next block
                if end_current_block == end { break; }
                start_block += 1;
                start = end_current_block;
            }
            read_size
        }
    }

它的含義是：將文件內容從 ``offset`` 字節開始的部分讀到內存中的緩衝區 ``buf`` 中，並返回實際讀到的字節數。如果文件剩下的內容還足夠多，那麼緩衝區會被填滿；否則文件剩下的全部內容都會被讀到緩衝區中。具體實現上有很多細節，但大致的思路是遍歷位於字節區間 ``start,end`` 中間的那些塊，將它們視為一個 ``DataBlock`` （也就是一個字節數組），並將其中的部分內容複製到緩衝區 ``buf`` 中適當的區域。 ``start_block`` 維護著目前是文件內部第多少個數據塊，需要首先調用 ``get_block_id`` 從索引中查到這個數據塊在塊設備中的塊編號，隨後才能傳入 ``get_block_cache`` 中將正確的數據塊緩存到內存中進行訪問。

在第 14 行進行了簡單的邊界條件判斷，如果要讀取的內容超出了文件的範圍，那麼直接返回 0 ，表示讀取不到任何內容。

``write_at`` 的實現思路基本上和 ``read_at`` 完全相同。但不同的是 ``write_at`` 不會出現失敗的情況；只要 Inode 管理的數據塊的大小足夠，傳入的整個緩衝區的數據都必定會被寫入到文件中。當從 ``offset`` 開始的區間超出了文件範圍的時候，就需要調用者在調用 ``write_at`` 之前提前調用 ``increase_size`` ，將文件大小擴充到區間的右端，保證寫入的完整性。

數據塊與目錄項
+++++++++++++++++++++++++++++++++++++++

作為一個文件而言，它的內容在文件系統看來沒有任何既定的格式，都只是一個字節序列。因此每個保存內容的數據塊都只是一個字節數組：

.. code-block:: rust

    // easy-fs/src/layout.rs

    type DataBlock = [u8; BLOCK_SZ];

然而，目錄的內容卻需要遵從一種特殊的格式。在我們的實現中，它可以看成一個目錄項的序列，每個目錄項都是一個二元組，二元組的首個元素是目錄下面的一個文件（或子目錄）的文件名（或目錄名），另一個元素則是文件（或子目錄）所在的索引節點編號。目錄項相當於目錄樹結構上的子樹節點，我們需要通過它來一級一級的找到實際要訪問的文件或目錄。目錄項 ``DirEntry`` 的定義如下：

.. code-block:: rust

    // easy-fs/src/layout.rs

    const NAME_LENGTH_LIMIT: usize = 27;

    #[repr(C)]
    pub struct DirEntry {
        name: [u8; NAME_LENGTH_LIMIT + 1],
        inode_number: u32,
    }

    pub const DIRENT_SZ: usize = 32;

目錄項 ``Dirent`` 最大允許保存長度為 27 的文件/目錄名（數組 ``name`` 中最末的一個字節留給 ``\0`` ），且它自身佔據空間 32 字節，每個數據塊可以存儲 16 個目錄項。我們可以通過 ``empty`` 和 ``new`` 分別生成一個空的目錄項或是一個合法的目錄項：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DirEntry {
        pub fn empty() -> Self {
            Self {
                name: [0u8; NAME_LENGTH_LIMIT + 1],
                inode_number: 0,
            }
        }
        pub fn new(name: &str, inode_number: u32) -> Self {
            let mut bytes = [0u8; NAME_LENGTH_LIMIT + 1];
            &mut bytes[..name.len()].copy_from_slice(name.as_bytes());
            Self {
                name: bytes,
                inode_number,
            }
        }
    }

在從目錄的內容中讀取目錄項或者是將目錄項寫入目錄的時候，我們需要將目錄項轉化為緩衝區（即字節切片）的形式來符合索引節點 ``Inode``  數據結構中的 ``read_at`` 或 ``write_at`` 方法接口的要求：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DirEntry {
        pub fn as_bytes(&self) -> &[u8] {
            unsafe {
                core::slice::from_raw_parts(
                    self as *const _ as usize as *const u8,
                    DIRENT_SZ,
                )
            }
        }
        pub fn as_bytes_mut(&mut self) -> &mut [u8] {
            unsafe {
                core::slice::from_raw_parts_mut(
                    self as *mut _ as usize as *mut u8,
                    DIRENT_SZ,
                )
            }
        }
    }

此外，通過 ``name`` 和 ``inode_number`` 方法可以取出目錄項中的內容：

.. code-block:: rust

    // easy-fs/src/layout.rs

    impl DirEntry {
        pub fn name(&self) -> &str {
            let len = (0usize..).find(|i| self.name[*i] == 0).unwrap();
            core::str::from_utf8(&self.name[..len]).unwrap()
        }
        pub fn inode_number(&self) -> u32 {
            self.inode_number
        }
    }

磁盤塊管理器
---------------------------------------

本層的代碼在 ``efs.rs`` 中。
上面介紹了 easy-fs 的磁盤佈局設計以及數據的組織方式 -- 即各類磁盤數據結構。但是它們都是以比較零散的形式分開介紹的，並沒有體現出磁盤佈局上各個區域是如何劃分的。實現 easy-fs 的整體磁盤佈局，將各段區域及上面的磁盤數據結構整合起來就是簡易文件系統 ``EasyFileSystem`` 的職責。它知道每個佈局區域所在的位置，磁盤塊的分配和回收也需要經過它才能完成，因此某種意義上講它還可以看成一個磁盤塊管理器。

注意從這一層開始，所有的數據結構就都放在內存上了。

.. code-block:: rust

    // easy-fs/src/efs.rs

    pub struct EasyFileSystem {
        pub block_device: Arc<dyn BlockDevice>,
        pub inode_bitmap: Bitmap,
        pub data_bitmap: Bitmap,
        inode_area_start_block: u32,
        data_area_start_block: u32,
    }

``EasyFileSystem`` 包含索引節點和數據塊的兩個位圖 ``inode_bitmap`` 和 ``data_bitmap`` ，還記錄下索引節點區域和數據塊區域起始塊編號方便確定每個索引節點和數據塊在磁盤上的具體位置。我們還要在其中保留塊設備的一個指針 ``block_device`` ，在進行後續操作的時候，該指針會被拷貝並傳遞給下層的數據結構，讓它們也能夠直接訪問塊設備。

通過 ``create`` 方法可以在塊設備上創建並初始化一個 easy-fs 文件系統：

.. code-block:: rust
    :linenos:

    // easy-fs/src/efs.rs

    impl EasyFileSystem {
        pub fn create(
            block_device: Arc<dyn BlockDevice>,
            total_blocks: u32,
            inode_bitmap_blocks: u32,
        ) -> Arc<Mutex<Self>> {
            // calculate block size of areas & create bitmaps
            let inode_bitmap = Bitmap::new(1, inode_bitmap_blocks as usize);
            let inode_num = inode_bitmap.maximum();
            let inode_area_blocks =
                ((inode_num * core::mem::size_of::<DiskInode>() + BLOCK_SZ - 1) / BLOCK_SZ) as u32;
            let inode_total_blocks = inode_bitmap_blocks + inode_area_blocks;
            let data_total_blocks = total_blocks - 1 - inode_total_blocks;
            let data_bitmap_blocks = (data_total_blocks + 4096) / 4097;
            let data_area_blocks = data_total_blocks - data_bitmap_blocks;
            let data_bitmap = Bitmap::new(
                (1 + inode_bitmap_blocks + inode_area_blocks) as usize,
                data_bitmap_blocks as usize,
            );
            let mut efs = Self {
                block_device: Arc::clone(&block_device),
                inode_bitmap,
                data_bitmap,
                inode_area_start_block: 1 + inode_bitmap_blocks,
                data_area_start_block: 1 + inode_total_blocks + data_bitmap_blocks,
            };
            // clear all blocks
            for i in 0..total_blocks {
                get_block_cache(
                    i as usize, 
                    Arc::clone(&block_device)
                )
                .lock()
                .modify(0, |data_block: &mut DataBlock| {
                    for byte in data_block.iter_mut() { *byte = 0; }
                });
            }
            // initialize SuperBlock
            get_block_cache(0, Arc::clone(&block_device))
            .lock()
            .modify(0, |super_block: &mut SuperBlock| {
                super_block.initialize(
                    total_blocks,
                    inode_bitmap_blocks,
                    inode_area_blocks,
                    data_bitmap_blocks,
                    data_area_blocks,
                );
            });
            // write back immediately
            // create a inode for root node "/"
            assert_eq!(efs.alloc_inode(), 0);
            let (root_inode_block_id, root_inode_offset) = efs.get_disk_inode_pos(0);
            get_block_cache(
                root_inode_block_id as usize,
                Arc::clone(&block_device)
            )
            .lock()
            .modify(root_inode_offset, |disk_inode: &mut DiskInode| {
                disk_inode.initialize(DiskInodeType::Directory);
            });
            Arc::new(Mutex::new(efs))
        }
    }

- 第 10~21 行根據傳入的參數計算每個區域各應該包含多少塊。根據 inode 位圖的大小計算 inode 區域至少需要多少個塊才能夠使得 inode 位圖中的每個bit都能夠有一個實際的 inode 可以對應，這樣就確定了 inode 位圖區域和 inode 區域的大小。剩下的塊都分配給數據塊位圖區域和數據塊區域。我們希望數據塊位圖中的每個bit仍然能夠對應到一個數據塊，但是數據塊位圖又不能過小，不然會造成某些數據塊永遠不會被使用。因此數據塊位圖區域最合理的大小是剩餘的塊數除以 4097 再上取整，因為位圖中的每個塊能夠對應 4096 個數據塊。其餘的塊就都作為數據塊使用。
- 第 22 行創建 ``EasyFileSystem`` 實例 ``efs`` 。
- 第 30 行首先將塊設備的前 ``total_blocks`` 個塊清零，因為 easy-fs 要用到它們，這也是為初始化做準備。
- 第 41 行將位於塊設備編號為 0 塊上的超級塊進行初始化，只需傳入之前計算得到的每個區域的塊數就行了。
- 第 54~63 行創建根目錄 ``/`` 。首先需要調用 ``alloc_inode`` 在 inode 位圖中分配一個 inode ，由於這是第一次分配，它的編號固定是 0 。接下來需要將分配到的 inode 初始化為 easy-fs 中的唯一一個目錄，故需要調用 ``get_disk_inode_pos`` 來根據 inode 編號獲取該 inode 所在的塊的編號以及塊內偏移，之後就可以將它們傳給 ``get_block_cache`` 和 ``modify`` 了。

通過 ``open`` 方法可以從一個已寫入了 easy-fs 鏡像的塊設備上打開我們的 easy-fs ：

.. code-block:: rust

    // easy-fs/src/efs.rs

    impl EasyFileSystem {
        pub fn open(block_device: Arc<dyn BlockDevice>) -> Arc<Mutex<Self>> {
            // read SuperBlock
            get_block_cache(0, Arc::clone(&block_device))
                .lock()
                .read(0, |super_block: &SuperBlock| {
                    assert!(super_block.is_valid(), "Error loading EFS!");
                    let inode_total_blocks =
                        super_block.inode_bitmap_blocks + super_block.inode_area_blocks;
                    let efs = Self {
                        block_device,
                        inode_bitmap: Bitmap::new(
                            1,
                            super_block.inode_bitmap_blocks as usize
                        ),
                        data_bitmap: Bitmap::new(
                            (1 + inode_total_blocks) as usize,
                            super_block.data_bitmap_blocks as usize,
                        ),
                        inode_area_start_block: 1 + super_block.inode_bitmap_blocks,
                        data_area_start_block: 1 + inode_total_blocks + super_block.data_bitmap_blocks,
                    };
                    Arc::new(Mutex::new(efs))
                })        
        }
    }

它只需將塊設備編號為 0 的塊作為超級塊讀取進來，就可以從中知道 easy-fs 的磁盤佈局，由此可以構造 ``efs`` 實例。

``EasyFileSystem`` 知道整個磁盤佈局，即可以從 inode位圖 或數據塊位圖上分配的 bit 編號，來算出各個存儲inode和數據塊的磁盤塊在磁盤上的實際位置。

.. code-block:: rust

    // easy-fs/src/efs.rs

    impl EasyFileSystem {
        pub fn get_disk_inode_pos(&self, inode_id: u32) -> (u32, usize) {
            let inode_size = core::mem::size_of::<DiskInode>();
            let inodes_per_block = (BLOCK_SZ / inode_size) as u32;
            let block_id = self.inode_area_start_block + inode_id / inodes_per_block;
            (block_id, (inode_id % inodes_per_block) as usize * inode_size)
        }

        pub fn get_data_block_id(&self, data_block_id: u32) -> u32 {
            self.data_area_start_block + data_block_id
        }
    }

inode 和數據塊的分配/回收也由 ``EasyFileSystem`` 負責：

.. code-block:: rust

    // easy-fs/src/efs.rs

    impl EasyFileSystem {
        pub fn alloc_inode(&mut self) -> u32 {
            self.inode_bitmap.alloc(&self.block_device).unwrap() as u32
        }

        /// Return a block ID not ID in the data area.
        pub fn alloc_data(&mut self) -> u32 {
            self.data_bitmap.alloc(&self.block_device).unwrap() as u32 + self.data_area_start_block
        }

        pub fn dealloc_data(&mut self, block_id: u32) {
            get_block_cache(
                block_id as usize,
                Arc::clone(&self.block_device)
            )
            .lock()
            .modify(0, |data_block: &mut DataBlock| {
                data_block.iter_mut().for_each(|p| { *p = 0; })
            });
            self.data_bitmap.dealloc(
                &self.block_device,
                (block_id - self.data_area_start_block) as usize
            )
        }
    }

注意：

- ``alloc_data`` 和 ``dealloc_data`` 分配/回收數據塊傳入/返回的參數都表示數據塊在塊設備上的編號，而不是在數據塊位圖中分配的bit編號；
- ``dealloc_inode`` 未實現，因為現在還不支持文件刪除。

索引節點
---------------------------------------

服務於文件相關係統調用的索引節點層的代碼在 ``vfs.rs`` 中。

``EasyFileSystem`` 實現了磁盤佈局並能夠將磁盤塊有效的管理起來。但是對於文件系統的使用者而言，他們往往不關心磁盤佈局是如何實現的，而是更希望能夠直接看到目錄樹結構中邏輯上的文件和目錄。為此需要設計索引節點 ``Inode`` 暴露給文件系統的使用者，讓他們能夠直接對文件和目錄進行操作。 ``Inode`` 和 ``DiskInode`` 的區別從它們的名字中就可以看出： ``DiskInode`` 放在磁盤塊中比較固定的位置，而 ``Inode`` 是放在內存中的記錄文件索引節點信息的數據結構。

.. code-block:: rust

    // easy-fs/src/vfs.rs

    pub struct Inode {
        block_id: usize,
        block_offset: usize,
        fs: Arc<Mutex<EasyFileSystem>>,
        block_device: Arc<dyn BlockDevice>,
    }

``block_id`` 和 ``block_offset`` 記錄該 ``Inode`` 對應的 ``DiskInode`` 保存在磁盤上的具體位置方便我們後續對它進行訪問。 ``fs`` 是指向 ``EasyFileSystem`` 的一個指針，因為對 ``Inode`` 的種種操作實際上都是要通過底層的文件系統來完成。

仿照 ``BlockCache::read/modify`` ，我們可以設計兩個方法來簡化對於 ``Inode`` 對應的磁盤上的 ``DiskInode`` 的訪問流程，而不是每次都需要 ``get_block_cache.lock.read/modify`` ：

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        fn read_disk_inode<V>(&self, f: impl FnOnce(&DiskInode) -> V) -> V {
            get_block_cache(
                self.block_id,
                Arc::clone(&self.block_device)
            ).lock().read(self.block_offset, f)
        }

        fn modify_disk_inode<V>(&self, f: impl FnOnce(&mut DiskInode) -> V) -> V {
            get_block_cache(
                self.block_id,
                Arc::clone(&self.block_device)
            ).lock().modify(self.block_offset, f)
        }
    }

下面分別介紹文件系統的使用者對於文件系統的一些常用操作：

獲取根目錄的 inode
+++++++++++++++++++++++++++++++++++++++

文件系統的使用者在通過 ``EasyFileSystem::open`` 從裝載了 easy-fs 鏡像的塊設備上打開 easy-fs 之後，要做的第一件事情就是獲取根目錄的 ``Inode`` 。因為 ``EasyFileSystem`` 目前僅支持絕對路徑，對於任何文件/目錄的索引都必須從根目錄開始向下逐級進行。等到索引完成之後， ``EasyFileSystem`` 才能對文件/目錄進行操作。事實上 ``EasyFileSystem`` 提供了另一個名為 ``root_inode`` 的方法來獲取根目錄的 ``Inode`` :

.. code-block:: rust

    // easy-fs/src/efs.rs

    impl EasyFileSystem {
        pub fn root_inode(efs: &Arc<Mutex<Self>>) -> Inode {
            let block_device = Arc::clone(&efs.lock().block_device);
            // acquire efs lock temporarily
            let (block_id, block_offset) = efs.lock().get_disk_inode_pos(0);
            // release efs lock
            Inode::new(
                block_id,
                block_offset,
                Arc::clone(efs),
                block_device,
            )
        }
    }

    // easy-fs/src/vfs.rs

    impl Inode {
        /// We should not acquire efs lock here.
        pub fn new(
            block_id: u32,
            block_offset: usize,
            fs: Arc<Mutex<EasyFileSystem>>,
            block_device: Arc<dyn BlockDevice>,
        ) -> Self {
            Self {
                block_id: block_id as usize,
                block_offset,
                fs,
                block_device,
            }
        }
    }

對於 ``root_inode`` 的初始化，是在調用 ``Inode::new`` 時將傳入的 ``inode_id`` 設置為 0 ，因為根目錄對應於文件系統中第一個分配的 inode ，因此它的 ``inode_id`` 總會是 0 。不會在調用 ``Inode::new`` 過程中嘗試獲取整個 ``EasyFileSystem`` 的鎖來查詢 inode 在塊設備中的位置，而是在調用它之前預先查詢並作為參數傳過去。

文件索引
+++++++++++++++++++++++++++++++++++++++

:ref:`前面 <fs-simplification>` 提到過，為了儘可能簡化文件系統設計， ``EasyFileSystem`` 是一個扁平化的文件系統，即在目錄樹上僅有一個目錄——那就是作為根節點的根目錄。所有的文件都在根目錄下面。於是，我們不必實現目錄索引。文件索引的查找比較簡單，僅需在根目錄的目錄項中根據文件名找到文件的 inode 編號即可。由於沒有子目錄的存在，這個過程只會進行一次。

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        pub fn find(&self, name: &str) -> Option<Arc<Inode>> {
            let fs = self.fs.lock();
            self.read_disk_inode(|disk_inode| {
                self.find_inode_id(name, disk_inode)
                .map(|inode_id| {
                    let (block_id, block_offset) = fs.get_disk_inode_pos(inode_id);
                    Arc::new(Self::new(
                        block_id,
                        block_offset,
                        self.fs.clone(),
                        self.block_device.clone(),
                    ))
                })
            })
        }

        fn find_inode_id(
            &self,
            name: &str,
            disk_inode: &DiskInode,
        ) -> Option<u32> {
            // assert it is a directory
            assert!(disk_inode.is_dir());
            let file_count = (disk_inode.size as usize) / DIRENT_SZ;
            let mut dirent = DirEntry::empty();
            for i in 0..file_count {
                assert_eq!(
                    disk_inode.read_at(
                        DIRENT_SZ * i,
                        dirent.as_bytes_mut(),
                        &self.block_device,
                    ),
                    DIRENT_SZ,
                );
                if dirent.name() == name {
                    return Some(dirent.inode_number() as u32);
                }
            }
            None
        }
    }

``find`` 方法只會被根目錄 ``Inode`` 調用，文件系統中其他文件的 ``Inode`` 不會調用這個方法。它首先調用 ``find_inode_id`` 方法，嘗試從根目錄的 ``DiskInode`` 上找到要索引的文件名對應的 inode 編號。這就需要將根目錄內容中的所有目錄項都讀到內存進行逐個比對。如果能夠找到，則 ``find`` 方法會根據查到 inode 編號，對應生成一個 ``Inode`` 用於後續對文件的訪問。

這裡需要注意，包括 ``find`` 在內，所有暴露給文件系統的使用者的文件系統操作（還包括接下來將要介紹的幾種），全程均需持有 ``EasyFileSystem`` 的互斥鎖（相對而言，文件系統內部的操作，如之前的 ``Inode::new`` 或是上面的 ``find_inode_id`` ，都是假定在已持有 efs 鎖的情況下才被調用的，因此它們不應嘗試獲取鎖）。這能夠保證在多核情況下，同時最多隻能有一個核在進行文件系統相關操作。這樣也許會帶來一些不必要的性能損失，但我們目前暫時先這樣做。如果我們在這裡加鎖的話，其實就能夠保證塊緩存的互斥訪問了。

文件列舉
+++++++++++++++++++++++++++++++++++++++

``ls`` 方法可以收集根目錄下的所有文件的文件名並以向量的形式返回，這個方法只有根目錄的 ``Inode`` 才會調用：

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        pub fn ls(&self) -> Vec<String> {
            let _fs = self.fs.lock();
            self.read_disk_inode(|disk_inode| {
                let file_count = (disk_inode.size as usize) / DIRENT_SZ;
                let mut v: Vec<String> = Vec::new();
                for i in 0..file_count {
                    let mut dirent = DirEntry::empty();
                    assert_eq!(
                        disk_inode.read_at(
                            i * DIRENT_SZ,
                            dirent.as_bytes_mut(),
                            &self.block_device,
                        ),
                        DIRENT_SZ,
                    );
                    v.push(String::from(dirent.name()));
                }
                v
            })
        }
    }

.. note::

    **Rust 語法卡片： _ 在匹配中的使用方法**

    可以看到在 ``ls`` 操作中，我們雖然獲取了 efs 鎖，但是這裡並不會直接訪問 ``EasyFileSystem`` 實例，其目的僅僅是鎖住該實例避免其他核在同時間的訪問造成併發衝突。因此，我們將其綁定到以 ``_`` 開頭的變量 ``_fs`` 中，這樣即使我們在其作用域中並沒有使用它，編譯器也不會報警告。然而，我們不能將其綁定到變量 ``_`` 上。因為從匹配規則可以知道這意味著該操作會被編譯器丟棄，從而無法達到獲取鎖的效果。

文件創建
+++++++++++++++++++++++++++++++++++++++

``create`` 方法可以在根目錄下創建一個文件，該方法只有根目錄的 ``Inode`` 會調用：

.. code-block:: rust
    :linenos:

    // easy-fs/src/vfs.rs

    impl Inode {
        pub fn create(&self, name: &str) -> Option<Arc<Inode>> {
            let mut fs = self.fs.lock();
            if self.modify_disk_inode(|root_inode| {
                // assert it is a directory
                assert!(root_inode.is_dir());
                // has the file been created?
                self.find_inode_id(name, root_inode)
            }).is_some() {
                return None;
            }
            // create a new file
            // alloc a inode with an indirect block
            let new_inode_id = fs.alloc_inode();
            // initialize inode
            let (new_inode_block_id, new_inode_block_offset) 
                = fs.get_disk_inode_pos(new_inode_id);
            get_block_cache(
                new_inode_block_id as usize,
                Arc::clone(&self.block_device)
            ).lock().modify(new_inode_block_offset, |new_inode: &mut DiskInode| {
                new_inode.initialize(DiskInodeType::File);
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
            // return inode
            Some(Arc::new(Self::new(
                block_id,
                block_offset,
                self.fs.clone(),
                self.block_device.clone(),
            )))
            // release efs lock automatically by compiler
        }
    }

- 第 6~13 行，檢查文件是否已經在根目錄下，如果找到的話返回 ``None`` ；
- 第 14~25 行，為待創建文件分配一個新的 inode 並進行初始化；
- 第 26~39 行，將待創建文件的目錄項插入到根目錄的內容中，使得之後可以索引到。

文件清空
+++++++++++++++++++++++++++++++++++++++

在以某些標誌位打開文件（例如帶有 *CREATE* 標誌打開一個已經存在的文件）的時候，需要首先將文件清空。在索引到文件的 ``Inode`` 之後，可以調用 ``clear`` 方法：

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        pub fn clear(&self) {
            let mut fs = self.fs.lock();
            self.modify_disk_inode(|disk_inode| {
                let size = disk_inode.size;
                let data_blocks_dealloc = disk_inode.clear_size(&self.block_device);
                assert!(data_blocks_dealloc.len() == DiskInode::total_blocks(size) as usize);
                for data_block in data_blocks_dealloc.into_iter() {
                    fs.dealloc_data(data_block);
                }
            });
        }
    }

這會將該文件佔據的索引塊和數據塊回收。

文件讀寫
+++++++++++++++++++++++++++++++++++++++

從根目錄索引到一個文件之後，可以對它進行讀寫。注意：和 ``DiskInode`` 一樣，這裡的讀寫作用在字節序列的一段區間上：

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        pub fn read_at(&self, offset: usize, buf: &mut [u8]) -> usize {
            let _fs = self.fs.lock();
            self.read_disk_inode(|disk_inode| {
                disk_inode.read_at(offset, buf, &self.block_device)
            })
        }

        pub fn write_at(&self, offset: usize, buf: &[u8]) -> usize {
            let mut fs = self.fs.lock();
            self.modify_disk_inode(|disk_inode| {
                self.increase_size((offset + buf.len()) as u32, disk_inode, &mut fs);
                disk_inode.write_at(offset, buf, &self.block_device)
            })
        }
    }

具體實現比較簡單，需要注意在執行 ``DiskInode::write_at`` 之前先調用 ``increase_size`` 對自身進行擴容：

.. code-block:: rust

    // easy-fs/src/vfs.rs

    impl Inode {
        fn increase_size(
            &self,
            new_size: u32,
            disk_inode: &mut DiskInode,
            fs: &mut MutexGuard<EasyFileSystem>,
        ) {
            if new_size < disk_inode.size {
                return;
            }
            let blocks_needed = disk_inode.blocks_num_needed(new_size);
            let mut v: Vec<u32> = Vec::new();
            for _ in 0..blocks_needed {
                v.push(fs.alloc_data());
            }
            disk_inode.increase_size(new_size, v, &self.block_device);
        }
    }

這裡會從 ``EasyFileSystem`` 中分配一些用於擴容的數據塊並傳給 ``DiskInode::increase_size`` 。

在用戶態測試 easy-fs 的功能
----------------------------------------------

``easy-fs`` 架構設計的一個優點在於它可以在Rust應用開發環境（Windows/macOS/Ubuntu）中，按照應用程序庫的開發方式來進行測試，不必過早的放到內核中測試運行。眾所周知，內核運行在裸機環境上，對其進行調試很困難。而面向應用的開發環境對於調試的支持更為完善，從基於命令行的 GDB 到 IDE 提供的圖形化調試界面都能給文件系統的開發帶來很大幫助。另外一點是，由於 ``easy-fs`` 需要放到在裸機上運行的內核中，使得 ``easy-fs`` 只能使用 ``no_std`` 模式，不能在 ``easy-fs`` 中調用標準庫 ``std`` 。但是在把 ``easy-fs`` 作為一個應用的庫運行的時候，可以暫時讓使用它的應用程序調用標準庫 ``std`` ，這也會在開發調試上帶來一些方便。

``easy-fs`` 的測試放在另一個名為 ``easy-fs-fuse`` 的應用程序中，不同於 ``easy-fs`` ，它是一個可以調用標準庫  ``std`` 的應用程序 ，能夠在Rust應用開發環境上運行並很容易調試。

在Rust應用開發環境中模擬塊設備
+++++++++++++++++++++++++++++++++++++++++++

從文件系統的使用者角度來看，它僅需要提供一個實現了 ``BlockDevice`` Trait 的塊設備用來裝載文件系統，之後就可以使用 ``Inode`` 來方便地進行文件系統操作了。但是在開發環境上，我們如何來提供這樣一個塊設備呢？答案是用 Linux （當然也可以是Windows/MacOS等其它通用操作系統）上的一個文件模擬一個塊設備。

.. code-block:: rust

    // easy-fs-fuse/src/main.rs

    use std::fs::File;
    use easy-fs::BlockDevice;

    const BLOCK_SZ: usize = 512;

    struct BlockFile(Mutex<File>);

    impl BlockDevice for BlockFile {
        fn read_block(&self, block_id: usize, buf: &mut [u8]) {
            let mut file = self.0.lock().unwrap();
            file.seek(SeekFrom::Start((block_id * BLOCK_SZ) as u64))
                .expect("Error when seeking!");
            assert_eq!(file.read(buf).unwrap(), BLOCK_SZ, "Not a complete block!");
        }

        fn write_block(&self, block_id: usize, buf: &[u8]) {
            let mut file = self.0.lock().unwrap();
            file.seek(SeekFrom::Start((block_id * BLOCK_SZ) as u64))
                .expect("Error when seeking!");
            assert_eq!(file.write(buf).unwrap(), BLOCK_SZ, "Not a complete block!");
        }
    }

``std::file::File`` 由 Rust 標準庫 std 提供，可以訪問 Linux 上的一個文件。我們將它包裝成 ``BlockFile`` 類型來模擬一塊磁盤，為它實現 ``BlockDevice`` 接口。注意 ``File`` 本身僅通過 ``read/write`` 接口是不能實現隨機讀寫的，在訪問一個特定的塊的時候，我們必須先 ``seek`` 到這個塊的開頭位置。

測試主函數為 ``easy-fs-fuse/src/main.rs`` 中的 ``efs_test`` 函數中，我們只需在 ``easy-fs-fuse`` 目錄下 ``cargo test`` 即可執行該測試：

.. code-block::

    running 1 test
    test efs_test ... ok

    test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out; finished in 1.27s

看到上面的內容就說明測試通過了。

``efs_test`` 展示了 ``easy-fs`` 庫的使用方法，大致分成以下幾個步驟：

打開塊設備
+++++++++++++++++++++++++++++++++++++++

.. code-block:: rust

    let block_file = Arc::new(BlockFile(Mutex::new({
        let f = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .open("target/fs.img")?;
        f.set_len(8192 * 512).unwrap();
        f
    })));
    EasyFileSystem::create(
        block_file.clone(),
        4096,
        1,
    );

第一步我們需要打開虛擬塊設備。這裡我們在 Linux 上創建文件 ``easy-fs-fuse/target/fs.img`` 來新建一個虛擬塊設備，並將它的容量設置為 8192 個塊即 4MiB 。在創建的時候需要將它的訪問權限設置為可讀可寫。

由於我們在進行測試，需要初始化測試環境，因此在虛擬塊設備 ``block_file`` 上初始化 easy-fs 文件系統，這會將 ``block_file`` 用於放置 easy-fs 鏡像的前 4096 個塊上的數據覆蓋，然後變成僅有一個根目錄的初始文件系統。如果塊設備上已經放置了一個合法的 easy-fs 鏡像，則我們不必這樣做。

從塊設備上打開文件系統
+++++++++++++++++++++++++++++++++++++++

.. code-block:: rust

    let efs = EasyFileSystem::open(block_file.clone());

這是通常進行的第二個步驟。

獲取根目錄的 Inode
+++++++++++++++++++++++++++++++++++++++

.. code-block:: rust

    let root_inode = EasyFileSystem::root_inode(&efs);

這是通常進行的第三個步驟。

進行各種文件操作
+++++++++++++++++++++++++++++++++++++++

拿到根目錄 ``root_inode`` 之後，可以通過它進行各種文件操作，目前支持以下幾種：

- 通過 ``create`` 創建文件。
- 通過 ``ls`` 列舉根目錄下的文件。
- 通過 ``find`` 根據文件名索引文件。

當通過索引獲取根目錄下的一個文件的 inode 之後則可以進行如下操作：

- 通過 ``clear`` 將文件內容清空。
- 通過 ``read/write_at`` 讀寫文件，注意我們需要將讀寫在文件中開始的位置 ``offset`` 作為一個參數傳遞進去。

測試方法在這裡不詳細介紹，大概是每次清空文件 ``filea`` 的內容，向其中寫入一個不同長度的隨機數字字符串，然後再全部讀取出來，驗證和寫入的內容一致。其中有一個細節是：用來生成隨機字符串的 ``rand`` crate 並不支持 ``no_std`` ，因此只有在用戶態我們才能更容易進行測試。

將應用打包為 easy-fs 鏡像
---------------------------------------

在第六章中我們需要將所有的應用都鏈接到內核中，隨後在應用管理器中通過應用名進行索引來找到應用的 ELF 數據。這樣做有一個缺點，就是會造成內核體積過度膨脹。在 k210 平臺上可以很明顯的感覺到從第五章開始隨著應用數量的增加，向開發板上燒寫內核鏡像的耗時顯著增長。同時這也會浪費內存資源，因為未被執行的應用也佔據了內存空間。在實現了 easy-fs 文件系統之後，終於可以將這些應用打包到 easy-fs 鏡像中放到磁盤中，當我們要執行應用的時候只需從文件系統中取出ELF 執行文件格式的應用 並加載到內存中執行即可，這樣就避免了前面章節的存儲開銷等問題。

``easy-fs-fuse`` 的主體 ``easy-fs-pack`` 函數就實現了這個功能：

.. code-block:: rust
    :linenos:

    // easy-fs-fuse/src/main.rs

    use clap::{Arg, App};

    fn easy_fs_pack() -> std::io::Result<()> {
        let matches = App::new("EasyFileSystem packer")
            .arg(Arg::with_name("source")
                .short("s")
                .long("source")
                .takes_value(true)
                .help("Executable source dir(with backslash)")
            )
            .arg(Arg::with_name("target")
                .short("t")
                .long("target")
                .takes_value(true)
                .help("Executable target dir(with backslash)")    
            )
            .get_matches();
        let src_path = matches.value_of("source").unwrap();
        let target_path = matches.value_of("target").unwrap();
        println!("src_path = {}\ntarget_path = {}", src_path, target_path);
        let block_file = Arc::new(BlockFile(Mutex::new({
            let f = OpenOptions::new()
                .read(true)
                .write(true)
                .create(true)
                .open(format!("{}{}", target_path, "fs.img"))?;
            f.set_len(8192 * 512).unwrap();
            f
        })));
        // 4MiB, at most 4095 files
        let efs = EasyFileSystem::create(
            block_file.clone(),
            8192,
            1,
        );
        let root_inode = Arc::new(EasyFileSystem::root_inode(&efs));
        let apps: Vec<_> = read_dir(src_path)
            .unwrap()
            .into_iter()
            .map(|dir_entry| {
                let mut name_with_ext = dir_entry.unwrap().file_name().into_string().unwrap();
                name_with_ext.drain(name_with_ext.find('.').unwrap()..name_with_ext.len());
                name_with_ext
            })
            .collect();
        for app in apps {
            // load app data from host file system
            let mut host_file = File::open(format!("{}{}", target_path, app)).unwrap();
            let mut all_data: Vec<u8> = Vec::new();
            host_file.read_to_end(&mut all_data).unwrap();
            // create a file in easy-fs
            let inode = root_inode.create(app.as_str()).unwrap();
            // write data to easy-fs
            inode.write_at(0, all_data.as_slice());
        }
        // list apps
        for app in root_inode.ls() {
            println!("{}", app);
        }
        Ok(())
    }

- 為了實現 ``easy-fs-fuse`` 和 ``os/user`` 的解耦，第 6~21 行使用 ``clap`` crate 進行命令行參數解析，需要通過 ``-s`` 和 ``-t`` 分別指定應用的源代碼目錄和保存應用 ELF 的目錄，而不是在 ``easy-fs-fuse`` 中硬編碼。如果解析成功的話它們會分別被保存在變量 ``src_path`` 和 ``target_path`` 中。
- 第 23~38 行依次完成：創建 4MiB 的 easy-fs 鏡像文件、進行 easy-fs 初始化、獲取根目錄 inode 。
- 第 39 行獲取源碼目錄中的每個應用的源代碼文件並去掉後綴名，收集到向量 ``apps`` 中。
- 第 48 行開始，枚舉 ``apps`` 中的每個應用，從放置應用執行程序的目錄中找到對應應用的 ELF 文件（這是一個 Linux 上的文件），並將數據讀入內存。接著需要在 easy-fs 中創建一個同名文件並將 ELF 數據寫入到這個文件中。這個過程相當於將 Linux 上的文件系統中的一個文件複製到我們的 easy-fs 中。

儘管沒有進行任何同步寫回磁盤的操作，我們也不用擔心塊緩存中的修改沒有寫回磁盤。因為在 ``easy-fs-fuse`` 這個應用正常退出的過程中，塊緩存因生命週期結束會被回收，屆時如果塊緩存的 ``modified`` 標誌為 true ，就會將其修改寫回磁盤。
