多道程序放置與加載
=====================================

本節導讀
--------------------------

本節我們將實現可以把多個應用放置到內存中的二疊紀“鋸齒螈” [#prionosuchus]_ 操作系統，“鋸齒螈”能夠上陸了！能實現二疊紀“鋸齒螈”操作系統的一個重要前提是計算機中物理內存容量增加了，足以容納多個應用程序的內容。在計算機的發展史上，我們也確實看到，隨著集成電路的快速發展，計算機的內存容量也越來越大了。

在本章的引言中我們提到每個應用都需要按照它的編號被分別放置並加載到內存中不同的位置。本節我們就來介紹多應用的內存放置是如何實現的。通過具體實現，可以看到多個應用程序被一次性地加載到內存中，這樣在切換到另外一個應用程序執行會很快，不像前一章介紹的操作系統，還要有清空前一個應用，然後加載當前應用的過程開銷。

但我們也會了解到，每個應用程序需要知道自己運行時在內存中的不同位置，這對應用程序的編寫帶來了一定的麻煩。而且操作系統也要知道每個應用程序運行時的位置，不能任意移動應用程序所在的內存空間，即不能在運行時根據內存空間的動態空閒情況，把應用程序調整到合適的空閒空間中。這是“鋸齒螈” [#prionosuchus]_ 操作系統在動態內存管理上的不足之處。

..
  chyyuu：有一個ascii圖，畫出我們做的OS在本節的部分。

多道程序放置
----------------------------

與第二章相同，所有應用的 ELF 格式執行文件都經過 ``objcopy`` 工具丟掉所有 ELF header 和符號變為二進制鏡像文件，隨後以同樣的格式通過在操作系統內核中嵌入 ``link_user.S`` 文件，在編譯時直接把應用鏈接到內核的數據段中。不同的是，我們對相關模塊進行了調整：在第二章中應用的加載和執行進度控制都交給 ``batch`` 子模塊，而在第三章中我們將應用的加載這部分功能分離出來在 ``loader`` 子模塊中實現，應用的執行和切換功能則交給 ``task`` 子模塊。

注意，我們需要調整每個應用被構建時使用的鏈接腳本 ``linker.ld`` 中的起始地址 ``BASE_ADDRESS`` ，這個地址是應用被內核加載到內存中的起始地址。也就是要做到：應用知道自己會被加載到某個地址運行，而內核也確實能做到將應用加載到它指定的那個地址。這算是應用和內核在某種意義上達成的一種協議。之所以要有這麼苛刻的條件，是因為目前的操作系統內核的能力還是比較弱的，對應用程序通用性的支持也不夠（比如不支持加載應用到內存中的任意地址運行），這也進一步導致了應用程序編程上不夠方便和通用（應用需要指定自己運行的內存地址）。事實上，目前應用程序的編址方式是基於絕對位置的，並沒做到與位置無關，內核也沒有提供相應的地址重定位機制。

.. note::

   對於編址方式，需要再回顧一下編譯原理課講解的後端代碼生成技術，以及計算機組成原理課的指令尋址方式的內容。可以在 `這裡 <https://nju-projectn.github.io/ics-pa-gitbook/ics2020/4.2.html>`_ 找到更多有關
   位置無關和重定位的說明。

由於每個應用被加載到的位置都不同，也就導致它們的鏈接腳本 ``linker.ld`` 中的 ``BASE_ADDRESS`` 都是不同的。實際上，我們不是直接用 ``cargo build`` 構建應用的鏈接腳本，而是寫了一個腳本定製工具 ``build.py`` ，為每個應用定製了各自的鏈接腳本：

.. code-block:: python
   :linenos:

    # user/build.py

    import os

    base_address = 0x80400000
    step = 0x20000
    linker = 'src/linker.ld'

    app_id = 0
    apps = os.listdir('src/bin')
    apps.sort()
    for app in apps:
        app = app[:app.find('.')]
        lines = []
        lines_before = []
        with open(linker, 'r') as f:
            for line in f.readlines():
                lines_before.append(line)
                line = line.replace(hex(base_address), hex(base_address+step*app_id))
                lines.append(line)
        with open(linker, 'w+') as f:
            f.writelines(lines)
        os.system('cargo build --bin %s --release' % app)
        print('[build.py] application %s start with address %s' %(app, hex(base_address+step*app_id)))
        with open(linker, 'w+') as f:
            f.writelines(lines_before)
        app_id = app_id + 1

它的思路很簡單，在遍歷 ``app`` 的大循環裡面只做了這樣幾件事情：

- 第 16~22 行，找到 ``src/linker.ld`` 中的 ``BASE_ADDRESS = 0x80400000;`` 這一行，並將後面的地址替換為和當前應用對應的一個地址；
- 第 23 行，使用 ``cargo build`` 構建當前的應用，注意我們可以使用 ``--bin`` 參數來只構建某一個應用；
- 第 25~26 行，將 ``src/linker.ld`` 還原。


多道程序加載
----------------------------

應用的加載方式也和上一章的有所不同。上一章中講解的加載方法是讓所有應用都共享同一個固定的加載物理地址。也是因為這個原因，內存中同時最多隻能駐留一個應用，當它運行完畢或者出錯退出的時候由操作系統的 ``batch`` 子模塊加載一個新的應用來替換掉它。本章中，所有的應用在內核初始化的時候就一併被加載到內存中。為了避免覆蓋，它們自然需要被加載到不同的物理地址。這是通過調用 ``loader`` 子模塊的 ``load_apps`` 函數實現的：

.. code-block:: rust
   :linenos:

    // os/src/loader.rs

    pub fn load_apps() {
        extern "C" { fn _num_app(); }
        let num_app_ptr = _num_app as usize as *const usize;
        let num_app = get_num_app();
        let app_start = unsafe {
            core::slice::from_raw_parts(num_app_ptr.add(1), num_app + 1)
        };
        // load apps
        for i in 0..num_app {
            let base_i = get_base_i(i);
            // clear region
            (base_i..base_i + APP_SIZE_LIMIT).for_each(|addr| unsafe {
                (addr as *mut u8).write_volatile(0)
            });
            // load app from data section to memory
            let src = unsafe {
                core::slice::from_raw_parts(
                    app_start[i] as *const u8,
                    app_start[i + 1] - app_start[i]
                )
            };
            let dst = unsafe {
                core::slice::from_raw_parts_mut(base_i as *mut u8, src.len())
            };
            dst.copy_from_slice(src);
        }
        unsafe {
            asm!("fence.i");
        }
    }

可以看出，第 :math:`i` 個應用被加載到以物理地址 ``base_i`` 開頭的一段物理內存上，而 ``base_i`` 的計算方式如下：

.. code-block:: rust
   :linenos:

    // os/src/loader.rs

    fn get_base_i(app_id: usize) -> usize {
        APP_BASE_ADDRESS + app_id * APP_SIZE_LIMIT
    }

我們可以在 ``config`` 子模塊中找到這兩個常數。從這一章開始， ``config`` 子模塊用來存放內核中所有的常數。看到 ``APP_BASE_ADDRESS`` 被設置為 ``0x80400000`` ，而 ``APP_SIZE_LIMIT`` 和上一章一樣被設置為 ``0x20000`` ，也就是每個應用二進制鏡像的大小限制。因此，應用的內存佈局就很明朗了——就是從 ``APP_BASE_ADDRESS`` 開始依次為每個應用預留一段空間。這樣，我們就說清楚了多個應用是如何被構建和加載的。


執行應用程序
----------------------------

當多道程序的初始化放置工作完成，或者是某個應用程序運行結束或出錯的時候，我們要調用 run_next_app 函數切換到下一個應用程序。此時 CPU 運行在 S 特權級的操作系統中，而操作系統希望能夠切換到 U 特權級去運行應用程序。這一過程與上章的 :ref:`執行應用程序 <ch2-app-execution>` 一節的描述類似。相對不同的是，操作系統知道每個應用程序預先加載在內存中的位置，這就需要設置應用程序返回的不同 Trap 上下文（Trap 上下文中保存了 放置程序起始地址的 ``epc`` 寄存器內容）：

- 跳轉到應用程序（編號 :math:`i` ）的入口點 :math:`\text{entry}_i` 
- 將使用的棧切換到用戶棧 :math:`\text{stack}_i` 

我們的“鋸齒螈”初級多道程序操作系統就算是實現完畢了。它支持把多個應用的代碼和數據放置到內存中，並能夠依次執行每個應用，提高了應用切換的效率，這就達到了本章對操作系統的初級需求。但“鋸齒螈”操作系統在任務調度的靈活性上還有很大的改進空間，下一節我們將開始改進這方面的問題。

..
  chyyuu：有一個ascii圖，畫出我們做的OS。


.. [#prionosuchus] 鋸齒螈身長可達9米，是迄今出現過的最大的兩棲動物，是二疊紀時期江河湖泊和沼澤中的頂級掠食者。  