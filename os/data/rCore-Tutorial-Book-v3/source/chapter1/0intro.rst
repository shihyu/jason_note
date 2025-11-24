引言
=====================

本章導讀
--------------------------

.. chyyuu
  這是註釋：我覺得需要給出執行環境（EE），Task，...等的描述。
  並且有一個圖，展示這些概念的關係。
  
本章展現了操作系統的一個基本目標：讓應用與硬件隔離，簡化了應用訪問硬件的難度和複雜性。這也是遠古操作系統雛形和現代的一些簡單嵌入式操作系統的主要功能。具有這樣功能的操作系統形態就是一個函數庫，可以被應用訪問，並通過函數庫的函數來訪問硬件。

大多數程序員的第一行代碼都從 ``Hello, world!`` 開始，當我們滿懷著好奇心在編輯器內鍵入僅僅數個字節，再經過幾行命令編譯（靠的是編譯器）、運行（靠的是操作系統），終於在黑洞洞的終端窗口中看到期望中的結果的時候，一扇通往編程世界的大門已經打開。在本章第一節 :doc:`1app-ee-platform` 中，可以看到用Rust語言編寫的非常簡單的“Hello, world”應用程序是如何被進一步拆解和分析的。

不過我們能夠隱約意識到編程工作能夠如此方便簡潔並不是理所當然的，實際上有著多層硬件和軟件工具和支撐環境隱藏在它背後，才讓我們不必付出那麼多努力就能夠創造出功能強大的應用程序。生成應用程序二進制執行代碼所依賴的是以 **編譯器** 為主的 **開發環境** ；運行應用程序執行碼所依賴的是以 **操作系統** 為主的 **執行環境** 。

本章主要是講解如何設計和實現建立在裸機上的執行環境，並讓應用程序能夠在這樣的執行環境中運行。從而讓同學能夠對應用程序和它所依賴的執行環境有一個全面和深入的理解。

本章的目標仍然只是讓應用程序輸出 ``Hello, world!`` 字符串，但這一次，我們將離開舒適區，基於一個幾乎空無一物的硬件平臺從零開始搭建我們自己的軟件高樓大廈，而不是僅僅通過一行語句就完成任務。所以，在接下來的內容中，我們將描述如何讓 ``Hello, world!`` 應用程序逐步脫離對編譯器、運行時庫和操作系統的現有複雜依賴，最終以最小的依賴需求能在裸機上運行。這時，我們也可把這個能在裸機上運行的 ``Hello, world!`` 應用程序所依賴的軟件庫稱為一種支持輸出字符串的非常初級的寒武紀“三葉蟲”操作系統 -- LibOS。LibOS其實就是一個給應用提供各種服務（比如輸出字符串）的庫，方便了單一應用程序在裸機上的開發與運行。輸出字符串的功能好比是三葉蟲的眼睛功能，有了它，我們就有了對軟件的最基本的動態分析與調試功能，即通過在代碼中的不同位置插入特定內容的輸出語句來實現對應用程序和操作系統運行狀態的分析與調試。


.. chyyuu note
   
    在練習一節前面，是否有一個歷史故事???
    目前發現，英國的OS（也可稱之為雛形）出現的可能更早
    Timeline of operating systems https://en.wikipedia.org/wiki/Timeline_of_operating_systems#cite_note-1
    1950 https://h2g2.com/edited_entry/A1000729  LEO I 'Lyons Electronic Office'[1] was the commercial development of EDSAC computing platform, supported by British firm J. Lyons and Co.    
    https://en.wikipedia.org/wiki/EDSAC  
    https://en.wikipedia.org/wiki/LEO_(computer)  
    https://www.theregister.com/2021/11/30/leo_70/  
    https://www.sciencemuseum.org.uk/objects-and-stories/meet-leo-worlds-first-business-computer 
    https://warwick.ac.uk/services/library/mrc/archives_online/digital/leo/story
    https://www.kzwp.com/lyons1/leo.htm 介紹了leo i 計算工資遠快於人工,隨著時間的推移，英國的計算機制造逐漸消失。
    https://en.wikipedia.org/wiki/Wheeler_Jump 
    https://en.wikipedia.org/wiki/EDSAC
    https://people.cs.clemson.edu/~mark/edsac.html 模擬器， 提到了操作系統
    The EDSAC (electronic delay storage automatic calculator) performed its first calculation at Cambridge University, England, in May 1949. EDSAC contained 3,000 vacuum tubes and used mercury delay lines for memory. Programs were input using paper tape and output results were passed to a teleprinter. Additionally, EDSAC is credited as using one of the first assemblers called "Initial Orders," which allowed it to be programmed symbolically instead of using machine code. [http://www.maxmon.com/1946ad.htm]

    The operating system or "initial orders" consisted of 31 instructions which were hard-wired on uniselectors, a mechanical read-only memory. These instructions assembled programs in symbolic form from paper tape into the main memory and set them running. The second release of the initial orders was installed in August 1949. This occupied the full 41 words of read-only memory and included facilities for relocation or "coordination" to facilitate the use of subroutines (an important invention by D.J. Wheeler). [http://www.cl.cam.ac.uk/UoCCL/misc/EDSAC99/statistics.html]

    The EDSAC programming system was based on a set of "initial orders" and a subroutine library. The initial orders combined in a rudimentary fashion the functions performed by a bootstrap loader and an assembler in later computer systems. The initial orders existed in three versions. The first version, Initial Orders 1, was devised by David Wheeler, then a research student, in 1949. The initial orders resided in locations 0 to 30, and loaded a program tape into locations 31 upwards. The program was punched directly onto tape in a symbolic form using mnemonic operation codes and decimal addresses, foreshadowing in a remarkable way much later assembly systems. ... In September 1949 the first form of the initial orders was replaced by a new version. Again written by Wheeler, Initial Orders 2 was a tour de force of programming that combined a surprisingly sophisticated assembler and relocating loader in just 41 instructions. The initial orders read in a master routine (main program) in symbolic form, converted it to binary and placed it in the main memory; this could be followed by any number of subroutines, which would be relocated and packed end-to-end so that there were none of the memory allocation problems associated with less sophisticated early attempts to organise a subroutine library. [http://www.inf.fu-berlin.de/~widiger/ICHC/papers/campbell.html]   

.. note::
   

   **最早的操作系統雛形是計算工資單的程序庫**

   操作系統需要給程序員提供支持：高效便捷地開發應用和執行應用。遠古時期的計算機硬件昂貴笨重，能力弱，單靠硬件還不能高效地執行應用，能夠減少程序員的開發成本就已經很不錯了。

   程序庫一般由一些子程序（函數）組成。通過調用程序庫中的子程序，應用程序可以更加方便的實現其應用功能。但在早期的軟件開發中，還缺少便捷有效的子程序調用機制。

   根據維基百科的操作系統時間線 [#OSTIMELINE]_ 上的記錄，1949-1951 年，英國 J. Lyons and Co. 公司（一家包括連鎖餐廳和食品製造的大型集團公司）開創性地引入並使用劍橋大學的 EDSAC 計算機，聯合設計實現了 LEO I 'Lyons Electronic Office' 軟硬件系統，利用計算機的高速度(按當時的標準)來高效地計算薪資，以及組織蛋糕和其他易腐爛的商品的分配等。這樣計算機就成為了一個高效的專用事務處理系統。但軟件開發還是一個很困難的事情，需要減少軟件編程人員的開發負擔。而通過函數庫來重用軟件功能並簡化應用的編程是當時自然的想法。但在軟件編程中，由於硬件的侷限性（缺少索引寄存器、保存函數返回地址的寄存器、棧寄存器、硬件棧等），早期的程序員不得不使用在程序中修改自身代碼的方式來訪問數組或調用函數。從現在的視角看來，這樣具有自修改能力的程序是一種黑科技。

   參與 EDSAC 項目的 David Wheeler 發明了子程序的概念 --  **Wheeler Jump** 。Wheeler 的方法是在子程序的最後一行添加 **“jump to this address”** 指令，並在指令後跟一個內存空間，這個內存空間通常被設置為 0，在子程序被調用後，這個內存空間的值會被修改為返回地址。當調用子程序時，調用者（Caller）的地址將被放置在累加寄存器中，然後代碼將跳轉到子程序的入口。子程序的第一條指令將根據累加寄存器中的值計算返回地址，通常是調用指令的下一條指令所在的內存位置，然後將計算出的返回地址寫入先前預留的內存空間中。當子程序繼續執行，自然會到達子程序的末尾，即 **“jump to this address”** 指令處，這條指令讀取位於它之後的內存單元，獲得返回地址，就可以正常返回了。

   在有了便捷有效的子程序概念和子程序調用機制後，軟件開發人員在 EDSAC 計算機開發了大量的子程序庫，其中就包括了檢查計算機系統，加載應用軟件，寫數據到持久性存儲設備中，打印數據等硬件系統相關功能的系統子程序庫。這樣程序員就可以方便開發應用程序來使用計算機了。這也是為何維基百科的的操作系統時間線 [#OSTIMELINE]_ 一文中，把 LEO I 'Lyons Electronic Office' 軟件系統（其實就是硬件系統相關的子程序庫）定位為最早（1951 年）的操作系統的起因。這樣的計算機系統只支持一個應用的運行，可以稱為專用計算機系統。1951 年 9 月 5 日，計算機首次執行了一個名為 Bakeries Valuations 的應用程序，並在後續承擔計算工資單這一必須按時執行的任務，因為必須向員工按時支付週薪。計算員工薪酬的任務需要一位經驗豐富的文員 8 分鐘內完成，而  LEO I 在 1.5 秒內完成了這項工作，快了 320 倍，這在當時英國社會上引起了轟動。


   即使到了現在，以子程序庫形式存在的簡單嵌入式操作系統大量存在，運行在很多基於微控制單元（Microcontroller Unit，簡稱 MCU）的單片機中，並支持簡單應用甚至是單一應用，在智能儀表、玩具、遊戲機、小家電等領域廣泛存在。



實踐體驗
---------------------------

本章設計實現了一個支持顯示字符串應用的簡單操作系統--“三葉蟲”操作系統 -- LibOS，它的形態就是一個函數庫，給應用程序提供了顯示字符串的函數。

獲取本章代碼：

.. code-block:: console

   $ git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
   $ cd rCore-Tutorial-v3
   $ git checkout ch1

在 Qemu 模擬器上運行本章代碼，看看一個小應用程序是如何在Qemu模擬的計算機上運行的：

.. code-block:: console

   $ cd os
   $ LOG=TRACE make run

``LOG=TRACE`` 是指定 LOG 的級別為 ``TRACE``，可以查看重要程度不低於 TRACE 的輸出日誌。目前 TRACE 的重要程度最低，因此這樣能夠看到全部日誌。

如果順利的話，以 Qemu 平臺為例，將輸出：

.. code-block::

    [RustSBI output]
    [rustsbi] RustSBI version 0.3.1, adapting to RISC-V SBI v1.0.0
    .______       __    __      _______.___________.  _______..______   __
    |   _  \     |  |  |  |    /       |           | /       ||   _  \ |  |
    |  |_)  |    |  |  |  |   |   (----`---|  |----`|   (----`|  |_)  ||  |
    |      /     |  |  |  |    \   \       |  |      \   \    |   _  < |  |
    |  |\  \----.|  `--'  |.----)   |      |  |  .----)   |   |  |_)  ||  |
    | _| `._____| \______/ |_______/       |__|  |_______/    |______/ |__|
    [rustsbi] Implementation     : RustSBI-QEMU Version 0.2.0-alpha.2
    [rustsbi] Platform Name      : riscv-virtio,qemu
    [rustsbi] Platform SMP       : 1
    [rustsbi] Platform Memory    : 0x80000000..0x88000000
    [rustsbi] Boot HART          : 0
    [rustsbi] Device Tree Region : 0x87000000..0x87000ef2
    [rustsbi] Firmware Address   : 0x80000000
    [rustsbi] Supervisor Address : 0x80200000
    [rustsbi] pmp01: 0x00000000..0x80000000 (-wr)
    [rustsbi] pmp02: 0x80000000..0x80200000 (---)
    [rustsbi] pmp03: 0x80200000..0x88000000 (xwr)
    [rustsbi] pmp04: 0x88000000..0x00000000 (-wr)
    [kernel] Hello, world!
    [TRACE] [kernel] .text [0x80200000, 0x80203000)
    [DEBUG] [kernel] .rodata [0x80203000, 0x80205000)
    [ INFO] [kernel] .data [0x80205000, 0x80206000)
    [ WARN] [kernel] boot_stack top=bottom=0x80216000, lower_bound=0x80206000
    [ERROR] [kernel] .bss [0x80216000, 0x80217000)


``Hello, world!`` 前後有一些額外的動態運行信息，最後是一系列 kernel 的輸出日誌。

本章代碼樹
------------------------------------------------

三葉蟲LibOS操作系統的總體結構如下圖所示：

.. image:: ../../os-lectures/lec2/figs/lib-os-detail.png
   :align: center
   :scale: 30 %
   :name: lib-os-detail
   :alt: LibOS總體結構

通過上圖，大致可以看出Qemu把包含app和三葉蟲LibOS的image鏡像加載到內存中，RustSBI（bootloader）完成基本的硬件初始化後，跳轉到三葉蟲LibOS起始位置，三葉蟲LibOS首先進行app執行前的初始化工作，即建立棧空間和清零bss段，然後跳轉到app去執行。app在執行過程中，會通過函數調用的方式得到三葉蟲LibOS提供的OS服務，如輸出字符串等，避免了app與硬件直接交互的繁瑣過程。

注: 圖中的S-Mode和M-Mode是RISC-V 處理器架構中的兩種特權級別。S-Mode 指的是 Supervisor 模式，是操作系統使用的特權級別，可執行特權指令等。M-Mode是 Machine模式，其特權級別比S-Mode還高，可以訪問RISC-V處理器中的所有系統資源。關於特權級的進一步描述可以看第二章的  :doc:`../chapter2/1rv-privilege` 中的詳細說明。

位於 ``ch1`` 分支上的三葉蟲LibOS操作系統的源代碼如下所示：

.. code-block::

   ./os/src
   Rust        4 Files   119 Lines
   Assembly    1 Files    11 Lines

   ├── bootloader(內核依賴的運行在 M 特權級的 SBI 實現，本項目中我們使用 RustSBI) 
   │   └── rustsbi-qemu.bin(可運行在 qemu 虛擬機上的預編譯二進制版本)
   ├── LICENSE
   ├── os(我們的內核實現放在 os 目錄下)
   │   ├── Cargo.toml(內核實現的一些配置文件)
   │   ├── Makefile
   │   └── src(所有內核的源代碼放在 os/src 目錄下)
   │       ├── console.rs(將打印字符的 SBI 接口進一步封裝實現更加強大的格式化輸出)
   │       ├── entry.asm(設置內核執行環境的的一段彙編代碼)
   │       ├── lang_items.rs(需要我們提供給 Rust 編譯器的一些語義項，目前包含內核 panic 時的處理邏輯)
   │       ├── linker-qemu.ld(控制內核內存佈局的鏈接腳本以使內核運行在 qemu 虛擬機上)
   │       ├── main.rs(內核主函數)
   │       └── sbi.rs(調用底層 SBI 實現提供的 SBI 接口)
   ├── README.md
   └── rust-toolchain(控制整個項目的工具鏈版本)

.. note::
   
    :doc:`../appendix-c/index` 中可以找到關於 RustSBI 的更多信息。


本章代碼導讀
-----------------------------------------------------

LibOS操作系統雖然是軟件，但它不是運行在通用操作系統（如Linux）上的一般應用軟件，而是運行在裸機執行環境中的系統軟件。如果採用通常的應用編程方法和編譯手段，無法開發出這樣的操作系統。其中一個重要的原因是：編譯器（Rust 編譯器和 C 編譯器等）編譯出的應用軟件在缺省情況下是要鏈接標準庫，而標準庫是依賴於操作系統（如 Linux、Windows 等）的，但LibOS操作系統不依賴其他操作系統。所以，本章主要是讓同學能夠脫離常規應用軟件開發的思路，理解如何開發沒有操作系統支持的操作系統內核。

為了做到這一步，首先需要寫出不需要標準庫的軟件並通過編譯。為此，先把一般應用所需要的標準庫的組件給去掉，這會導致編譯失敗。然後再逐步添加不需要操作系統的極少的運行時支持代碼，讓編譯器能夠正常編譯出不需要標準庫的正常程序。但此時的程序沒有顯示輸出，更沒有輸入等，但可以正常通過編譯，這樣就打下 **可正常編譯OS** 的前期開發基礎。具體可看 :ref:`移除標準庫依賴 <term-remove-std>` 一節的內容。

LibOS內核主要在 Qemu 模擬器上運行，它可以模擬一臺 64 位 RISC-V 計算機。為了讓LibOS內核能夠正確對接到 Qemu 模擬器上，需要了解 Qemu 模擬器的啟動流程，還需要一些程序內存佈局和編譯流程（特別是鏈接）相關知識，這樣才能將LibOS內核加載到正確的內存位置上，並使得它能夠在 Qemu 上正常運行。為了確認內核被加載到正確的內存位置，我們會在LibOS內核中手寫一條彙編指令，並使用 GDB 工具監控 Qemu 的執行流程確認這條指令被正確執行。具體可以參考 :doc:`/chapter1/3first-instruction-in-kernel1` 和 :doc:`/chapter1/4first-instruction-in-kernel2` 兩節。

我們想用 Rust 語言來實現內核的大多數功能，因此我們需要進一步將控制權從第一條指令轉交給 Rust 入口函數。在 Rust 代碼中，函數調用是不可或缺的基本控制流，為了使得函數調用能夠正常進行，我們在跳轉到 Rust 入口函數前還需要進行棧的初始化工作。為此我們詳細介紹了函數調用和棧的相關背景知識，具體內容可參考 :doc:`/chapter1/5support-func-call` 一節。最終，我們調用軟件棧中相比內核更低一層的軟件——也即 RustSBI 提供的服務來實現格式化輸出和遇到致命錯誤時的關機功能，形成了LibOS的核心功能，詳情參考 :doc:`/chapter1/6print-and-shutdown-based-on-sbi` 一節。至此，應用程序可以直接調用LibOS提供的字符串輸出函數或關機函數，達到讓應用與硬件隔離的操作系統目標。


.. 操作系統代碼無法像應用軟件那樣，可以有方便的調試（Debug）功能。這是因為應用之所以能夠被調試，也是由於操作系統提供了方便的調試相關的系統調用。而我們不得不再次認識到，需要運行在沒有操作系統的裸機環境中，當然沒法採用依賴操作系統的傳統調試方法了。所以，我們只能採用 ``print`` 這種原始且有效的調試方法。這樣，第二步就是讓脫離了標準庫的軟件有輸出，這樣，我們就能看到程序的運行情況了。為了簡單起見，我們可以先在用戶態嘗試構建沒有標準庫的支持顯示輸出的最小運行時執行環境，比較特別的地方在於如何寫內嵌彙編調用更為底層的輸出接口來實現這一功能。具體可看 :ref:`構建用戶態執行環境 <term-print-userminienv>` 一節的內容。

.. 接下來就是嘗試構建可在裸機上支持顯示的最小運行時執行環境。相對於用戶態執行環境，同學需要能夠做更多的事情，比如如何關機，如何配置軟件運行所在的物理內存空間，特別是棧空間，如何清除 ``bss`` 段，如何通過 ``RustSBI`` 的 ``SBI_CONSOLE_PUTCHAR`` 接口簡潔地實現信息輸出。這裡比較特別的地方是需要了解 ``linker.ld`` 文件中對 OS 的代碼和數據所在地址空間佈局的描述，以及基於 RISC-V 64 的彙編代碼 ``entry.asm`` 如何進行棧的設置和初始化，以及如何跳轉到 Rust 語言編寫的 ``rust_main`` 主函數中，並開始內核最小運行時執行環境的運行。具體可看 :ref:`構建裸機執行環境 <term-print-kernelminienv>` 一節的內容。


.. [#OSTIMELINE] https://en.wikipedia.org/wiki/Timeline_of_operating_systems 
