.. _term-remove-std:

移除標準庫依賴
==========================

.. toctree::
   :hidden:
   :maxdepth: 5

本節導讀
-------------------------------

.. 為了很好地理解一個簡單應用所需的執行環境服務如何體現，本節將嘗試開始構造一個小的執行環境。這個執行環境可以看成是一個函數庫級的操作系統雛形，可建立在 Linux 之上，也可直接建立在裸機之上，我們稱為“三葉蟲”操作系統。作為第一步，本節將嘗試移除之前的 ``Hello world!`` 程序對於 Rust std 標準庫的依賴，使得它能夠編譯到裸機平臺 RV64GC 或 Linux-RV64 上。

本章的目標是構建一個內核最小執行環境使得它能在 RV64GC （即實現了IMAFDC規範的 RISC-V 64位CPU）裸機上運行，在功能上它則像上一節最簡單的 Rust 應用程序一樣能夠打印 ``Hello, world!`` ，這將會為我們的後續章節提供很多調試上的方便，我們將其稱為“三葉蟲”操作系統。本節我們來進行第一個步驟：即對上一節最簡單的 Rust 應用程序進行改造使得它能夠被編譯到 RV64GC 裸機平臺上，為此我們需要移除它對於 Rust std標準庫的依賴，因為 Rust std標準庫自己就需要操作系統內核的支持。這樣我們需要添加能夠支持應用的裸機級別的庫操作系統（LibOS）。 

.. note::

   **庫操作系統（Library OS，LibOS）**

   LibOS 以函數庫的形式存在，為應用程序提供操作系統的基本功能。它最早來源於 MIT PDOS研究小組在1996年左右的Exokernel（外核）操作系統結構研究。Frans Kaashoek 教授的博士生Dawson Engler 提出了一種與以往操作系統架構大相徑庭的 Exokernel（外核）架構設計 [#exokernel]_ ，即把傳統的單體內核分為兩部分，一部分以庫操作系統的形式（即 LibOS）與應用程序緊耦合以實現傳統的操作系統抽象，並進行面向應用的裁剪與優化；另外一部分（即外核）僅專注在最基本的安全複用物理硬件的機制上，來給 LibOS 提供基本的硬件訪問服務。這樣的設計思路可以針對應用程序的特徵定製 LibOS ，達到高性能的目標。

   這種操作系統架構的設計思路比較超前，對原型系統的測試顯示了很好的性能提升。但最終沒有被工業界採用，其中一個重要的原因是針對特定應用定製一個LibOS的工作量大，難以重複使用。人力成本因素導致了它不太被工業界認可。


移除 ``println!`` 宏
----------------------------------

``println!`` 宏所在的 Rust 標準庫 std 需要通過系統調用獲得操作系統的服務，而如果要構建運行在裸機上的操作系統，就不能再依賴標準庫了。所以我們第一步要嘗試移除 ``println!`` 宏及其所在的標準庫。

由於後續實驗需要 ``rustc`` 編譯器缺省生成RISC-V 64的目標代碼，所以我們首先要給  ``rustc`` 添加一個target : ``riscv64gc-unknown-none-elf`` 。這可通過如下命令來完成：

.. code-block:: bash

   $ rustup target add riscv64gc-unknown-none-elf


然後在 ``os`` 目錄下新建 ``.cargo`` 目錄，並在這個目錄下創建 ``config`` 文件，並在裡面輸入如下內容：

.. code-block:: toml

   # os/.cargo/config
   [build]
   target = "riscv64gc-unknown-none-elf"

.. _term-cross-compile:

這會對於 Cargo 工具在 os 目錄下的行為進行調整：現在默認會使用 riscv64gc 作為目標平臺而不是原先的默認 x86_64-unknown-linux-gnu。事實上，這是一種編譯器運行的開發平臺（x86_64）與可執行文件運行的目標平臺（riscv-64）不同的情況。我們把這種情況稱為 **交叉編譯** (Cross Compile)。


.. note::

   **本地編譯與交叉編譯** 

   下面指的 **平臺** 主要由CPU硬件和操作系統這兩個要素組成。

   本地編譯，即在當前開發平臺下編譯出來的程序，也只是放到這個平臺下運行。如在 Linux x86-64 平臺上編寫代碼並編譯成可在 Linux x86-64 同樣平臺上執行的程序。
   
   交叉編譯，是一個與本地編譯相對應的概念，即在一種平臺上編譯出在另一種平臺上運行的程序。程序編譯的環境與程序運行的環境不一樣。如我們後續會講到，在Linux x86-64 開發平臺上，編寫代碼並編譯成可在 rCore Tutorial（這是我們要編寫的操作系統內核）和 riscv64gc（這是CPU硬件）構成的目標平臺上執行的程序。
   


當然，這只是使得我們之後在 ``cargo build`` 的時候不必再加上 ``--target`` 參數的一個小 trick。如果我們現在執行 ``cargo build`` ，還是會和上一小節一樣出現找不到標準庫 std 的錯誤。於是我們需要在著手移除標準庫的過程中一步一步地解決這些錯誤。

我們在 ``main.rs`` 的開頭加上一行 ``#![no_std]`` 來告訴 Rust 編譯器不使用 Rust 標準庫 std 轉而使用核心庫 core（core庫不需要操作系統的支持）。編譯器報出如下錯誤：

.. error::

   .. code-block:: console

      $ cargo build
         Compiling os v0.1.0 (/home/shinbokuow/workspace/v3/rCore-Tutorial-v3/os)
      error: cannot find macro `println` in this scope
      --> src/main.rs:4:5
        |
      4 |     println!("Hello, world!");
        |     ^^^^^^^

我們之前提到過， ``println!`` 宏是由標準庫 std 提供的，且會使用到一個名為 write 的系統調用。現在我們的代碼功能還不足以自己實現一個 ``println!`` 宏。由於程序使用了系統調用，但不能在核心庫 core 中找到它，所以我們目前先通過將 ``println!`` 宏註釋掉的簡單粗暴方式，來暫時繞過這個問題。

.. chyyuu note::
   **Rust Tips: Rust std 庫和 core 庫**
   * Rust 的標準庫--std，為絕大多數的 Rust 應用程序開發提供基礎支持、跨硬件和操作系統平臺支持，是應用範圍最廣、地位最重要的庫，但需要有底層操作系統的支持。
   * Rust 的核心庫--core，可以理解為是經過大幅精簡的標準庫，它被應用在標準庫不能覆蓋到的某些特定領域，如裸機(bare metal) 環境下，用於操作系統和嵌入式系統的開發，它不需要底層操作系統的支持。


提供panic_handler功能應對致命錯誤
--------------------------------------------------------

我們重新編譯簡單的os程序，之前的 `println` 宏缺失的錯誤消失了，但又出現瞭如下新的編譯錯誤：

.. error::

   .. code-block:: console

      $ cargo build
         Compiling os v0.1.0 (/home/shinbokuow/workspace/v3/rCore-Tutorial-v3/os)
      error: `#[panic_handler]` function required, but not found

在使用 Rust 編寫應用程序的時候，我們常常在遇到了一些無法恢復的致命錯誤（panic），導致程序無法繼續向下運行。這時手動或自動調用 ``panic!`` 宏來打印出錯的位置，讓軟件能夠意識到它的存在，並進行一些後續處理。 ``panic!`` 宏最典型的應用場景包括斷言宏 ``assert!`` 失敗或者對 ``Option::None/Result::Err`` 進行 ``unwrap`` 操作。所以Rust編譯器在編譯程序時，從安全性考慮，需要有 ``panic!`` 宏的具體實現。

.. chyyuu  rust-lang/rust/library/std/src/panic.rs  `pub macro panic_2015/2021 {`

.. chyyuu  rust-lang/rust/library/core/src/macros/modrs `macro_rules! panic {`

在標準庫 std 中提供了關於 ``panic!`` 宏的具體實現，其大致功能是打印出錯位置和原因並殺死當前應用。但本章要實現的操作系統不能使用還需依賴操作系統的標準庫std，而更底層的核心庫 core 中只有一個 ``panic!`` 宏的空殼，並沒有提供 ``panic!`` 宏的精簡實現。因此我們需要自己先實現一個簡陋的 panic 處理函數，這樣才能讓“三葉蟲”操作系統 -- LibOS的編譯通過。

.. note::

   **#[panic_handler]**

   ``#[panic_handler]`` 是一種編譯指導屬性，用於標記核心庫core中的 ``panic!`` 宏要對接的函數（該函數實現對致命錯誤的具體處理）。該編譯指導屬性所標記的函數需要具有 ``fn(&PanicInfo) -> !`` 函數簽名，函數可通過 ``PanicInfo`` 數據結構獲取致命錯誤的相關信息。這樣Rust編譯器就可以把核心庫core中的 ``panic!`` 宏定義與 ``#[panic_handler]`` 指向的panic函數實現合併在一起，使得no_std程序具有類似std庫的應對致命錯誤的功能。

.. chyyuu https://doc.rust-lang.org/beta/unstable-book/language-features/lang-items.html

.. chyyuu  note::

..    **Rust Tips：語義項（lang_items）**

..    為了滿足編譯器和運行時庫的靈活性，Rust 編譯器內部的某些功能並不僅僅硬編碼在語言內部來實現，而是以一種可插入的形式在庫中提供，而且可以定製。標準庫或第三方庫只需要通過某種方式（在方法前面加上一個標記，稱為`語義項`標記)，如 ``#[panic_handler]`` 、 ``#[]`` 、 ``#[]`` 、 ``#[]`` 等，即可告訴編譯器它實現了編譯器內部的哪些功能，編譯器就會採用庫提供的方法來替換它內部對應的功能。

我們創建一個新的子模塊 ``lang_items.rs`` 實現panic函數，並通過 ``#[panic_handler]`` 屬性通知編譯器用panic函數來對接 ``panic!`` 宏。為了將該子模塊添加到項目中，我們還需要在 ``main.rs`` 的 ``#![no_std]`` 的下方加上 ``mod lang_items;`` ，相關知識可參考 :ref:`Rust 模塊編程 <rust-modular-programming>` ：

.. code-block:: rust
   :linenos:

   // os/src/lang_items.rs
   use core::panic::PanicInfo;

   #[panic_handler]
   fn panic(_info: &PanicInfo) -> ! {
       loop {}
   }

在把 ``panic_handler`` 配置在單獨的文件 ``os/src/lang_items.rs`` 後，需要在os/src/main.rs文件中添加以下內容才能正常編譯整個軟件：

.. code-block:: rust
   :linenos:

   // os/src/main.rs
   #![no_std]
   mod lang_items;
   // ... other code

注意，panic 處理函數的函數簽名需要一個 ``PanicInfo`` 的不可變借用作為輸入參數，它在核心庫中得以保留，這也是我們第一次與核心庫打交道。之後我們會從 ``PanicInfo`` 解析出錯位置並打印出來，然後殺死應用程序。但目前我們什麼都不做只是在原地  ``loop`` 。



移除 main 函數
-----------------------------

我們再次重新編譯簡單的os程序，之前的 `#[panic_handler]` 函數缺失的錯誤消失了，但又出現瞭如下新的編譯錯誤：
.. error::

   .. code-block::

      $ cargo build
         Compiling os v0.1.0 (/home/shinbokuow/workspace/v3/rCore-Tutorial-v3/os)
      error: requires `start` lang_item

編譯器提醒我們缺少一個名為 ``start`` 的語義項。我們回憶一下，之前提到語言標準庫和三方庫作為應用程序的執行環境，需要負責在執行應用程序之前進行一些初始化工作，然後才跳轉到應用程序的入口點（也就是跳轉到我們編寫的 ``main`` 函數）開始執行。事實上 ``start`` 語義項代表了標準庫 std 在執行應用程序之前需要進行的一些初始化工作。由於我們禁用了標準庫，編譯器也就找不到這項功能的實現了。

最簡單的解決方案就是壓根不讓編譯器使用這項功能。我們在 ``main.rs`` 的開頭加入設置 ``#![no_main]`` 告訴編譯器我們沒有一般意義上的 ``main`` 函數，並將原來的 ``main`` 函數刪除。在失去了 ``main`` 函數的情況下，編譯器也就不需要完成所謂的初始化工作了。

至此，我們成功移除了標準庫的依賴，並完成了構建裸機平臺上的“三葉蟲”操作系統的第一步工作--通過編譯器檢查並生成執行碼。

.. code-block:: console

   $ cargo build
      Compiling os v0.1.0 (/home/shinbokuow/workspace/v3/rCore-Tutorial-v3/os)
       Finished dev [unoptimized + debuginfo] target(s) in 0.06s

目前的主要代碼包括 ``main.rs`` 和 ``lang_items.rs`` ，大致內容如下：

.. code-block:: rust
   :linenos:

   // os/src/main.rs
   #![no_main]
   #![no_std]
   mod lang_items;
   // ... other code


   // os/src/lang_items.rs
   use core::panic::PanicInfo;

   #[panic_handler]
   fn panic(_info: &PanicInfo) -> ! {
       loop {}
   }

本小節我們固然脫離了標準庫，通過了編譯器的檢驗，但也是傷筋動骨，將原有的很多功能弱化甚至直接刪除，看起來距離在 RV64GC 平臺上打印 ``Hello world!`` 相去甚遠了（我們甚至連 ``println!`` 和 ``main`` 函數都刪除了）。不要著急，接下來我們會以自己的方式來重塑這些基本功能，並最終完成我們的目標。

.. _rust-modular-programming:

.. note::

   **Rust Tips：Rust 模塊化編程**

   將一個軟件工程項目劃分為多個子模塊分別進行實現是一種被廣泛應用的編程技巧，它有助於促進複用代碼，並顯著提升代碼的可讀性和可維護性。因此，眾多編程語言均對模塊化編程提供了支持，Rust 語言也不例外。

   每個通過 Cargo 工具創建的 Rust 項目均是一個模塊，取決於 Rust 項目類型的不同，模塊的根所在的位置也不同。當使用 ``--bin`` 創建一個可執行的 Rust 項目時，模塊的根是 ``src/main.rs`` 文件；而當使用 ``--lib`` 創建一個 Rust 庫項目時，模塊的根是 ``src/lib.rs`` 文件。在模塊的根文件中，我們需要聲明所有可能會用到的子模塊。如果不聲明的話，即使子模塊對應的文件存在，Rust 編譯器也不會用到它們。如上面的代碼片段中，我們就在根文件 ``src/main.rs`` 中通過 ``mod lang_items;`` 聲明瞭子模塊 ``lang_items`` ，該子模塊實現在文件 ``src/lang_item.rs`` 中，我們將項目中所有的語義項放在該模塊中。

   當一個子模塊比較複雜的時候，它往往不會被放在一個獨立的文件中，而是放在一個 ``src`` 目錄下與子模塊同名的子目錄之下，在後面的章節中我們常會用到這種方法。例如第二章代碼（參見代碼倉庫的 ``ch2`` 分支）中的 ``syscall`` 子模塊就放在 ``src/syscall`` 目錄下。對於這樣的子模塊，其所在目錄下的 ``mod.rs`` 為該模塊的根，其中可以進而聲明它的子模塊。同樣，這些子模塊既可以放在一個文件中，也可以放在一個目錄下。

   每個模塊可能會對其他模塊公開一些變量、類型或函數，而該模塊的其他內容則是對其他模塊不可見的，也即其他模塊不允許引用或訪問這些內容。在模塊內，僅有被顯式聲明為 ``pub`` 的內容才會對其他模塊公開。Rust 類內部聲明的屬性域和方法也可以對其他類公開或是不對其他類公開，這取決於它們是否被聲明為 ``pub`` 。我們在 C++/Java 語言中能夠找到相同功能的關鍵字：即 ``public/private`` 。提供上述可見性機制的原因在於讓其他類/模塊能夠訪問當前類/模塊公開提供的內容而無需關心它們是如何實現的，它們實際上也無法看到這些具體實現，因為這些具體實現並未向它們公開。編譯器會對可見性進行檢查，例如，當一個類/模塊試圖訪問其他類/模塊未公開的方法時，將無法通過編譯。

   我們可以使用絕對路徑或相對路徑來引用其他模塊或當前模塊的內容。參考上面的 ``use core::panic::PanicInfo;`` ，類似 C++ ，我們將模塊的名字按照層級由淺到深排列，並在相鄰層級之間使用分隔符 ``::`` 進行分隔。路徑的最後一級（如 ``PanicInfo``）則表示我們具體要引用或訪問的內容，可能是變量、類型或者方法名。當通過絕對路徑進行引用時，路徑最開頭可能是項目依賴的一個外部庫的名字，或者是 ``crate`` 表示項目自身的根模塊。在後面的章節中，我們會多次用到它們。

分析被移除標準庫的程序
-----------------------------

對於上面這個被移除標準庫的應用程序，通過了Rust編譯器的檢查和編譯，形成了二進制代碼。但這個二進制代碼的內容是什麼，它能否在RISC-V 64計算機上正常執行呢？為了分析這個二進制可執行程序，首先需要安裝 cargo-binutils 工具集：

.. code-block:: console

   $ cargo install cargo-binutils
   $ rustup component add llvm-tools-preview

這樣我們可以通過各種工具來分析目前的程序：

.. code-block:: console

   # 文件格式
   $ file target/riscv64gc-unknown-none-elf/debug/os
   target/riscv64gc-unknown-none-elf/debug/os: ELF 64-bit LSB executable, UCB RISC-V, ......

   # 文件頭信息
   $ rust-readobj -h target/riscv64gc-unknown-none-elf/debug/os
      File: target/riscv64gc-unknown-none-elf/debug/os
      Format: elf64-littleriscv
      Arch: riscv64
      AddressSize: 64bit
      ......
      Type: Executable (0x2)
      Machine: EM_RISCV (0xF3)
      Version: 1
      Entry: 0x0
      ......
      }

   # 反彙編導出彙編程序
   $ rust-objdump -S target/riscv64gc-unknown-none-elf/debug/os
      target/riscv64gc-unknown-none-elf/debug/os:	file format elf64-littleriscv

通過 ``file`` 工具對二進制程序 ``os`` 的分析可以看到它好像是一個合法的 RISC-V 64 可執行程序，但通過 ``rust-readobj`` 工具進一步分析，發現它的入口地址 Entry 是 ``0`` ，從 C/C++ 等語言中得來的經驗告訴我們， ``0`` 一般表示 NULL 或空指針，因此等於 ``0`` 的入口地址看上去無法對應到任何指令。再通過 ``rust-objdump`` 工具把它反彙編，可以看到沒有生成彙編代碼。所以，我們可以斷定，這個二進制程序雖然合法，但它是一個空程序。產生該現象的原因是：目前我們的程序（參考上面的源代碼）沒有進行任何有意義的工作，由於我們移除了 ``main`` 函數並將項目設置為 ``#![no_main]`` ，它甚至沒有一個傳統意義上的入口點（即程序首條被執行的指令所在的位置），因此 Rust 編譯器會生成一個空程序。

在下面幾節，我們將建立有支持顯示字符串的最小執行環境。

.. note::

   **在 x86_64 平臺上移除標準庫依賴**

   有興趣的同學可以將目標平臺換回之前默認的 ``x86_64-unknown-linux-gnu`` 並重複本小節所做的事情，比較兩個平臺從 ISA 到操作系統的差異。可以參考 `BlogOS 的相關內容 <https://os.phil-opp.com/freestanding-rust-binary/>`_ [#blogos]_ 。

.. note:: 

   本節內容部分參考自 `BlogOS 的相關章節 <https://os.phil-opp.com/freestanding-rust-binary/>`_ 。


.. [#exokernel] D. R. Engler, M. F. Kaashoek, and J. O'Toole. 1995. Exokernel: an operating system architecture for application-level resource management. In Proceedings of the fifteenth ACM symposium on Operating systems principles (SOSP '95). Association for Computing Machinery, New York, NY, USA, 251–266. 
.. [#blogos] https://os.phil-opp.com/freestanding-rust-binary/