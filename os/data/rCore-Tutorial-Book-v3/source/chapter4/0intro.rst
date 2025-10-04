引言
==============================

本章導讀
-------------------------------

..
  chyyuu：有一個ascii圖，畫出我們做的OS。


物理內存是操作系統需要管理的一個重要資源，讓運行在一臺機器上的多個應用程序不用“爭搶”，都能隨時得到想要的任意多的內存，是操作系統的想要達到的理想目標。提高系統物理內存的動態使用效率，通過隔離應用的物理內存空間保證應用間的安全性，把“有限”物理內存變成“無限”虛擬內存，是操作系統的一系列重要的目標，本章展現了操作系統為實現“理想”而要擴展的一系列功能：

- 通過動態內存分配，提高了應用程序對內存的動態使用效率
- 通過頁表的虛實內存映射機制，簡化了編譯器對應用的地址空間設置
- 通過頁表的虛實內存映射機制，加強了應用之間，應用與內核之間的內存隔離，增強了系統安全
- 通過頁表的虛實內存映射機制，可以實現空分複用（提出，但沒有實現）

本章將進一步設計與實現具有上述大部分功能的侏羅紀“頭甲龍” [#tutus]_ 操作系統，讓應用開發更加簡單，應用程序更加通用，且讓應用和操作系統都有強大的地址空間隔離的安全保護。

.. _term-illusion:
.. _term-time-division-multiplexing:
.. _term-transparent:

上一章，我們分別實現了多道程序和分時多任務系統，它們的核心機制都是任務切換。由於多道程序和分時多任務系統的設計初衷不同，它們在任務切換的時機和策略也不同。有趣的一點是，任務切換機制對於應用是完全 **透明** (Transparent) 的，應用可以不對內核實現該機制的策略做任何假定（除非要進行某些針對性優化），甚至可以完全不知道這機制的存在。

在大多數應用（也就是應用開發者）的視角中，它們會獨佔一整個 CPU 和特定（連續或不連續）的內存空間。當然，通過上一章的學習，我們知道在現代操作系統中，出於公平性的考慮，我們極少會讓獨佔 CPU 這種情況發生。所以應用自認為的獨佔 CPU 只是內核想讓應用看到的一種 **幻象** (Illusion) ，而 CPU 計算資源被 **時分複用** (TDM, Time-Division Multiplexing) 的實質被內核通過恰當的抽象隱藏了起來，對應用不可見。

與之相對，我們目前還沒有對內存管理功能進行進一步拓展，僅僅是把程序放到某處的物理內存中。在內存訪問方面，所有的應用都直接通過物理地址訪問物理內存，這使得應用開發者需要了解繁瑣的物理地址空間佈局，訪問內存也很不方便。在上一章中，出於任務切換的需要，所有的應用都在初始化階段被加載到內存中並同時駐留下去直到它們全部運行結束。而且，所有的應用都直接通過物理地址訪問物理內存。這會帶來以下問題：

- 首先，內核提供給應用的內存訪問接口不夠透明，也不好用。由於應用直接訪問物理內存，這需要它在構建的時候就清楚所運行計算機的物理內存空間佈局，還需規劃自己需要被加載到哪個地址運行。為了避免衝突可能還需要應用的開發者們對此進行協商，這顯然是一件在今天看來不夠通用且極端麻煩的事情。
- 其次，內核並沒有對應用的訪存行為進行任何保護措施，每個應用都有計算機系統中整個物理內存的讀寫權力。即使應用被限制在 U 特權級下運行，它還是能夠造成很多麻煩：比如它可以讀寫其他應用的數據來竊取信息或者破壞其它應用的正常運行；甚至它還可以修改內核的代碼段來替換掉原本的 ``trap_handler`` 函數，來挾持內核執行惡意代碼。總之，這造成系統既不安全、也不穩定。
- 再次，目前應用的內存使用空間在其運行前已經限定死了，內核不能靈活地給應用程序提供的運行時動態可用內存空間。比如一個應用結束後，這個應用所佔的空間就被釋放了，但這塊空間無法動態地給其它還在運行的應用使用。

因此，為了簡化應用開發，防止應用胡作非為，本章將更好地管理物理內存，並提供給應用一個抽象出來的更加透明易用、也更加安全的訪存接口，這就是基於分頁機制的虛擬內存。站在應用程序運行的角度看，就是存在一個從“0”地址開始的非常大的可讀/可寫/可執行的地址空間（Address Space），而站在操作系統的角度看，每個應用被侷限在分配給它的物理內存空間中運行，無法讀寫其它應用和操作系統所在的內存空間。

實現地址空間的第一步就是實現分頁機制，建立好虛擬內存和物理內存的頁映射關係。此過程需要硬件支持，硬件細節與具體CPU相關，涉及地址映射機制等，相對比較複雜。總體而言，我們需要思考如下問題：

- 硬件中物理內存的範圍是什麼？
- 哪些物理內存空間需要建立頁映射關係？
- 如何建立頁表使能分頁機制？
- 如何確保 OS 能夠在分頁機制使能前後的不同時間段中都能正常尋址和執行代碼？
- 頁目錄表（一級）的起始地址設置在哪裡？
- 二級/三級等頁表的起始地址設置在哪裡，需要多大空間？
- 如何設置頁目錄表項/頁表項的內容？
- 如果要讓每個任務有自己的地址空間，那每個任務是否要有自己的頁表？
- 代表應用程序的任務和操作系統需要有各自的頁表嗎？
- 在有了頁表之後，任務和操作系統之間應該如何傳遞數據？

如果能解決上述問題，我們就能設計實現具有超強防護能力的侏羅紀“頭甲龍”操作系統。並可更好地理解地址空間，虛擬地址等操作系統的抽象概念與操作系統的虛存具體實現之間的聯繫。

.. chyyuu：在哪裡講解虛存的設計與實現？？？

.. chyyuu : virtual mem, paging history

   The Atlas Supervisor was the program which managed the allocation of processing resources of Manchester University's Atlas Computer so that the machine was able to act on many tasks and user programs concurrently.

   Its various functions included running the Atlas computer's virtual memory (Atlas Supervisor paper, section 3, Store Organisation) and is ‘considered by many to be the first recognisable modern operating system’.[1] Brinch Hansen described it as "the most significant breakthrough in the history of operating systems."[2]

   Lavington, Simon (1980), Early British Computers, Manchester University Press, ISBN 0-7190-0803-4
   Brinch Hansen, Per (2000), Classic Operating Systems: From Batch Processing to Distributed Systems, Springer-Verlag

   https://en.wikipedia.org/wiki/Virtual_memory
   https://en.wikipedia.org/wiki/Atlas_Supervisor
   https://history-computer.com/the-history-of-atlas-computer/
   https://ethw.org/A_Brief_History_of_Early_British_Computers
   http://www.chilton-computing.org.uk/acl/technology/atlas/p019.htm The Atlas Supervisor paper (T Kilburn, R B Payne, D J Howarth, 1962)
   http://curation.cs.manchester.ac.uk/Atlas50/atlas50.cs.manchester.ac.uk/ Memories of the Ferranti Atlas computer
   https://www.essex.ac.uk/people/lavin12900/simon-lavington 參與atlas ，目前關注 cs history
   http://www.computinghistory.org.uk/det/3638/Simon-Lavington/
   https://blog.csdn.net/mightySheldor/article/details/44732029 中文 The Atlas Supervisor
   http://www.whereis.xyz/2019/tech/199/ 虛擬內存技術的前世今生
   
.. note::
   
   **提供巨大虛擬內存空間的 Atlas Supervisor 操作系統**

   兩級存儲系統在 1940 年就已經存在。1950-1960 年期間，計算機的主存（今天稱為 RAM）通常是容量小的磁芯，而輔助存儲器通常是容量大的磁鼓。處理器只能對主存尋址來讀寫數據或執行代碼。1960 年前後，位於計算機內存中的應用程序數量和單個程序的體積都在迅速增加，物理內存的容量跟不上應用對內存的需求。應用程序員的一個主要工作是在程序中編寫在主存和輔助存儲之間移動數據的代碼，來擴大應用程序訪問的數據量。計算機專家開始考慮能否讓計算機自動地移動數據來減輕程序員的編程負擔？

   虛擬內存（Virtual memory）技術概念首次由德國的柏林工業大學（Technische Universität Berlin）博士生 Fritz-Rudolf Güntsch 提出。在他的博士論文中設想了一臺計算機，其內存地址空間大小為 :math:`10^5` 個字，可精確映射到作為二級存儲的磁鼓（大小也為 :math:`10^5` 個字）上，應用程序讀寫的數據的實際位置由硬件和監控器（即操作系統）來管理和控制，並在物理主存（RAM）和輔存（二級存儲）之間按需搬移數據。即主存中只放置應用程序最近訪問的數據，而應用程序最近不訪問的數據會搬移到輔存中，在應用程序需要時再搬回內存中。這個搬移過程對應用程序是透明的。

   虛擬內存的設想在 1959 年變成了現實。英國曼徹斯特大學的 Tom Kilburn 教授領導的團隊於 1959 年展示了他們設計的 Atlas 計算機和 Atlas Supervisor 操作系統，開創了在今天仍然普遍使用的操作系統技術：分頁（paging）技術和虛擬內存（virtual memory，當時稱為 one-level storage system）。他們的核心思想中的根本性創新是區分了“地址（address）”和“內存位置（memory location）”，並因此創造了三項發明：

   1. 地址轉換：硬件自動將處理器生成的每個地址轉換為其當前內存位置。
   2. 按需分頁（demand paging）：由硬件地址轉換觸發缺頁中斷後，由操作系統將缺失的數據頁移動到主存儲器中，並形成正確的地址轉換映射。
   3. 頁面置換算法：檢查最無用（least useful）的頁，並將其移回二級存儲中，這樣可以讓經常訪問的數據駐留在主存中。

   計算機科學家對 Atlas Supervisor 操作系統給予高度的評價。Brinch Hansen 認為它是操作系統史上最重大的突破。Simon Lavington 認為它是第一個可識別的現代操作系統。

實踐體驗
-----------------------

本章的應用和上一章相同，只不過由於內核提供給應用的訪存接口被替換，應用的構建方式發生了變化，這方面在下面會深入介紹。
因此應用運行起來的效果與上一章是一致的。

獲取本章代碼：

.. code-block:: console

   $ git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
   $ cd rCore-Tutorial-v3
   $ git checkout ch4

在 qemu 模擬器上運行本章代碼：

.. code-block:: console

   $ cd os
   $ make run

如果順利的話，我們將看到和上一章相同的運行結果（以 K210 平臺為例）：

.. code-block::

   [RustSBI output]
   [kernel] back to world!
   remap_test passed!
   init TASK_MANAGER
   num_app = 4
   power_3 [10000/300000power_5 [10000/210000]
   power_5 [20000/210000]
   power_5 [30000/210000]
   
   ...
   
   (mod 998244353)
   Test power_7 OK!
   [kernel] Application exited with code 0
   power_3 [290000/300000]
   power_3 [300000/300000]
   3^300000 = 612461288(mod 998244353)
   Test power_3 OK!
   [kernel] Application exited with code 0
   Test sleep OK!
   [kernel] Application exited with code 0
   [kernel] Panicked at src/task/mod.rs:112 All applications completed!
   [rustsbi] reset triggered! todo: shutdown all harts on k210; program halt. Type: 0, reason: 0

本章代碼樹
-----------------------------------------------------

頭甲龍操作系統 - Address Space OS的總體結構如下圖所示：

.. image:: ../../os-lectures/lec5/figs/addr-space-os-detail.png
   :align: center
   :scale: 30 %
   :name: addr-space-os-detail
   :alt: 頭甲龍操作系統 - Address Space OS總體結構

通過上圖，大致可以看出頭甲龍操作系統 - Address Space OS為了提高操作系統和應用程序執行的安全性，增強了內存管理能力，提供了地址空間隔離機制，給APP的內存地址空間劃界，不能越界訪問OS和其他APP。在具體實現上，擴展了 `TaskManager` 的管理範圍，每個 `Task` 的上下文 `Task Context` 還包括該任務的地址空間，在切換任務時，也要切換任務的地址空間。新增的內存管理模塊主要包括與內核中動態內存分配相關的頁幀分配、堆分配，以及表示應用地址空間的 `Apps MemSets` 類型和內核自身地址空間的 `Kernel MemSet`類型。 `MemSet` 類型所包含的頁表 `PageTable` 建立了虛實地址映射關係，而另外一個 `MemArea` 表示任務的合法空間範圍。

位於 ``ch4`` 分支上的頭甲龍操作系統 - Address Space OS的源代碼如下所示：

.. code-block::
    :linenos:
    :emphasize-lines: 59

    ./os/src
    Rust        25 Files    1415 Lines
    Assembly     3 Files      88 Lines

    ├── bootloader
    │   ├── rustsbi-k210.bin
    │   └── rustsbi-qemu.bin
    ├── LICENSE
    ├── os
    │   ├── build.rs
    │   ├── Cargo.lock
    │   ├── Cargo.toml
    │   ├── Makefile
    │   └── src
    │       ├── config.rs(修改：新增一些內存管理的相關配置)
    │       ├── console.rs
    │       ├── entry.asm
    │       ├── lang_items.rs
    │       ├── link_app.S
    │       ├── linker-k210.ld(修改：將跳板頁引入內存佈局)
    │       ├── linker-qemu.ld(修改：將跳板頁引入內存佈局)
    │       ├── loader.rs(修改：僅保留獲取應用數量和數據的功能)
    │       ├── main.rs(修改)
    │       ├── mm(新增：內存管理的 mm 子模塊)
    │       │   ├── address.rs(物理/虛擬 地址/頁號的 Rust 抽象)
    │       │   ├── frame_allocator.rs(物理頁幀分配器)
    │       │   ├── heap_allocator.rs(內核動態內存分配器)
    │       │   ├── memory_set.rs(引入地址空間 MemorySet 及邏輯段 MemoryArea 等)
    │       │   ├── mod.rs(定義了 mm 模塊初始化方法 init)
    │       │   └── page_table.rs(多級頁表抽象 PageTable 以及其他內容)
    │       ├── sbi.rs
    │       ├── sync
    │       │   ├── mod.rs
    │       │   └── up.rs
    │       ├── syscall
    │       │   ├── fs.rs(修改：基於地址空間的 sys_write 實現)
    │       │   ├── mod.rs
    │       │   └── process.rs
    │       ├── task
    │       │   ├── context.rs(修改：構造一個跳轉到不同位置的初始任務上下文)
    │       │   ├── mod.rs(修改，詳見文檔)
    │       │   ├── switch.rs
    │       │   ├── switch.S
    │       │   └── task.rs(修改，詳見文檔)
    │       ├── timer.rs
    │       └── trap
    │           ├── context.rs(修改：在 Trap 上下文中加入了更多內容)
    │           ├── mod.rs(修改：基於地址空間修改了 Trap 機制，詳見文檔)
    │           └── trap.S(修改：基於地址空間修改了 Trap 上下文保存與恢復彙編代碼)
    ├── README.md
    ├── rust-toolchain
    ├── tools
    │   ├── kflash.py
    │   ├── LICENSE
    │   ├── package.json
    │   ├── README.rst
    │   └── setup.py
    └── user
        ├── build.py(移除)
        ├── Cargo.toml
        ├── Makefile
        └── src
            ├── bin
            │   ├── 00power_3.rs
            │   ├── 01power_5.rs
            │   ├── 02power_7.rs
            │   └── 03sleep.rs
            ├── console.rs
            ├── lang_items.rs
            ├── lib.rs
            ├── linker.ld(修改：將所有應用放在各自地址空間中固定的位置)
            └── syscall.rs



本章代碼導讀
-----------------------------------------------------

本章涉及的代碼量相對多了起來，也許同學們不知如何從哪裡看起或從哪裡開始嘗試實驗。這裡簡要介紹一下“頭甲龍”操作系統的大致開發過程。

我們先從簡單的地方入手，那當然就是先改進應用程序了。具體而言，主要就是把 ``linker.ld`` 中應用程序的起始地址都改為 ``0x10000`` ，這是假定我們操作系統能夠通過分頁機制把不同應用的相同虛地址映射到不同的物理地址中。這樣我們寫應用就不用考慮應用的物理地址佈局的問題，能夠以一種更加統一的方式編寫應用程序，可以忽略掉一些不必要的細節。

為了能夠在內核中動態分配內存，我們的第二步需要在內核增加連續內存分配的功能，具體實現主要集中在 ``os/src/mm/heap_allocator.rs`` 中。完成這一步後，我們就可以在內核中用到Rust的堆數據結構了，如 ``Vec`` 、 ``Box`` 等，這樣內核編程就更加靈活了。

操作系統如果要建立頁表（構建虛實地址映射關係），首先要能管理整個系統的物理內存，這就需要知道整個計算機系統的物理內存空間的範圍，物理內存中哪些區域是空閒可用的，哪些區域放置內核/應用的代碼和數據。操作系統內核能夠以物理頁幀為單位分配和回收物理內存，具體實現主要集中在 ``os/src/mm/frame_allocator.rs`` 中；也能在虛擬內存中以各種粒度大小來動態分配內存資源，具體實現主要集中在 ``os/src/mm/heap_allocator.rs`` 中。

頁表中的頁表項的索引其實是虛擬地址中的虛擬頁號，頁表項的重要內容是物理地址的物理頁幀號。為了能夠靈活地在虛擬地址、物理地址、虛擬頁號、物理頁號之間進行各種轉換，在 ``os/src/mm/address.rs`` 中實現了各種轉換函數。

完成上述工作後，基本上就做好了建立頁表的前期準備。我們就可以開始建立頁表，這主要涉及到頁表項的數據結構表示，以及多級頁表的起始物理頁幀位置和整個所佔用的物理頁幀的記錄。具體實現主要集中在 ``os/src/mm/page_table.rs`` 中。

一旦使能分頁機制，CPU 訪問到的地址都是虛擬地址了，那麼內核中也將基於虛地址進行虛存訪問。所以在給應用添加虛擬地址空間前，內核自己也會建立一個頁表，把整塊物理內存通過簡單的恆等映射（即虛擬地址映射到對等的物理地址）映射到內核虛擬地址空間中。後續的應用在執行前，也需要操作系統幫助它建立一個虛擬地址空間。這意味著第三章的初級 ``task`` 將進化到第四章的擁有獨立頁表的 ``task`` 。虛擬地址空間需要有一個數據結構管理起來，這就是 ``MemorySet`` ，即地址空間這個抽象概念所對應的具象體現。在一個虛擬地址空間中，有代碼段，數據段等不同屬性且不一定連續的子空間，它們通過一個重要的數據結構 ``MapArea`` 來表示和管理。圍繞 ``MemorySet`` 等一系列的數據結構和相關操作的實現，主要集中在 ``os/src/mm/memory_set.rs`` 中。比如內核的頁表和虛擬空間的建立在如下代碼中：

.. code-block:: rust
    :linenos:

    // os/src/mm/memory_set.rs

    lazy_static! {
      pub static ref KERNEL_SPACE: Arc<Mutex<MemorySet>> = Arc::new(Mutex::new(
         MemorySet::new_kernel()
      ));
    }

完成到這裡，我們就可以使能分頁機制了。且我們應該有更加方便的機制來給支持應用運行。在本章之前，都是把應用程序的所有元數據丟棄從而轉換成二進制格式來執行，這其實把編譯器生成的 ELF 執行文件中大量有用的信息給去掉了，比如代碼段、數據段的各種屬性，程序的入口地址等。既然有了給應用運行提供虛擬地址空間的能力，我們就可以利用 ELF 執行文件中的各種信息來靈活構建應用運行所需要的虛擬地址空間。在 ``os/src/loader.rs`` 中可以看到如何獲取一個應用的 ELF 執行文件數據，而在 ``os/src/mm/memory_set`` 中的 ``MemorySet::from_elf`` 可以看到如何通過解析 ELF 來創建一個應用地址空間。

為此，操作系統需要擴展任務控制塊 ``TaskControlBlock`` 的管理範圍，使得操作系統能管理擁有獨立頁表和單一虛擬地址空間的應用程序的運行。相關主要的改動集中在  ``os/src/task/task.rs`` 中。

由於代表應用程序運行的任務和管理應用的操作系統各自有獨立的頁表和虛擬地址空間，所以在操作系統的設計實現上需要考慮兩個挑戰。第一個挑戰是 **頁表切換** 。由於系統調用、中斷或異常導致的應用程序和操作系統之間的上下文切換不像以前那麼簡單了，因為在這些處理過程中需要切換頁表，相關改進可參看  ``os/src/trap/trap.S`` 。還有就是需要對來自用戶態和內核態的異常/中斷分別進行處理，相關改進可參看  ``os/src/trap/mod.rs`` 和  :ref:`跳板的實現 <term-trampoline>` 中的講解。

第二個挑戰是 **查頁表以訪問不同地址空間的數據** 。在內核地址空間中執行的內核代碼常常需要讀寫應用的地址空間中的數據，這無法簡單的通過一次訪存來解決，而是需要手動查用戶態應用的地址空間的頁表，知道用戶態應用的虛地址對應的物理地址後，轉換成對應的內核態的虛地址，才能訪問應用地址空間中的數據。如果訪問應用地址空間中的數據跨了多個頁，還需要注意處理地址的邊界條件。具體可以參考 ``os/src/syscall/fs.rs``、 ``os/src/mm/page_table.rs`` 中的 ``translated_byte_buffer`` 函數的實現。

實現到這，本章的“頭甲龍”操作系統應該就可以給應用程序運行提供一個方便且安全的虛擬地址空間了。

.. [#tutus] 頭甲龍最早出現在1.8億年以前的侏羅紀中期，是身披重甲的食素恐龍，尾巴末端的尾錘，是防身武器。