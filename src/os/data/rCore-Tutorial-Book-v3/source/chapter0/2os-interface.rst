操作系統的系統調用接口
================================================

.. toctree::
   :hidden:
   :maxdepth: 5

API與ABI
--------------------

站在使用操作系統的角度會比較容易對操作系統內核的功能產生初步的認識。操作系統內核是一個提供各種服務的軟件，其服務對象是應用程序，而用戶（這裡可以理解為一般使用計算機的人）是通過應用程序的服務間接獲得操作系統的服務的，因此操作系統內核藏在一般用戶看不到的地方。但應用程序需要訪問操作系統獲得操作系統的服務，這就需要通過操作系統的接口才能完成。操作系統與運行在用戶態軟件之間的接口形式就是上一節提到的應用程序二進制接口 (ABI, Application Binary Interface)。

操作系統不能只提供面向單一編程語言的函數庫的編程接口 (API, Application Programming Interface) ，它的接口需要考慮對基於各種編程語言的應用支持，以及訪問安全等因素，使得應用軟件不能像訪問函數庫一樣的直接訪問操作系統內部函數，更不能直接讀寫操作系統內部的地址空間。為此，操作系統設計了一套安全可靠的二進制接口，我們稱為系統調用接口 (System Call Interface)。系統調用接口通常面向應用程序提供了 API 的描述，但在具體實現上，還需要提供 ABI 的接口描述規範。

在現代處理器的安全支持（特權級隔離，內存空間隔離等）下，應用程序就不能直接以函數調用的方式訪問操作系統的函數，以及直接讀寫操作系統的數據變量。不同類型的應用程序可以通過符合操作系統規定的系統調用接口，發出系統調用請求，來獲得操作系統的服務。操作系統提供完服務後，返回應用程序繼續執行。


.. note::

   **API 與 ABI 的區別**
   
   應用程序二進制接口 ABI 是不同二進制代碼片段的連接紐帶。ABI 定義了二進制機器代碼級別的規則，主要包括基本數據類型、通用寄存器的使用、參數的傳遞規則、以及堆棧的使用等等。ABI 與處理器和內存地址等硬件架構相關，是用來約束鏈接器 (Linker) 和彙編器 (Assembler) 的。在同一處理器下，基於不同高級語言編寫的應用程序、庫和操作系統，如果遵循同樣的 ABI 定義，那麼它們就能正確鏈接和執行。

   應用程序編程接口 API 是不同源代碼片段的連接紐帶。API 定義了一個源碼級（如 C 語言）函數的參數，參數的類型，函數的返回值等。因此 API 是用來約束編譯器 (Compiler) 的：一個 API 是給編譯器的一些指令，它規定了源代碼可以做以及不可以做哪些事。API 與編程語言相關，如 libc 是基於 C 語言編寫的標準庫，那麼基於 C 的應用程序就可以通過編譯器建立與 libc 的聯繫，並能在運行中正確訪問 libc 中的函數。

.. chyyuu 應該給具體的例子，說明 API, ABI的區別。學生提問"一直想不出來ABI是怎麼被用戶空間程序調用的"

系統調用接口與功能
------------------------------

對於通用的應用程序，一般需要關注如下問題，並希望得到操作系統的支持：

- 一個運行的程序如何能輸出字符信息？如何能獲得輸入字符信息？
- 一個運行的程序可以要求更多（或更少）的內存空間嗎？
- 一個運行的程序如何持久地存儲用戶數據？
- 一個運行的程序如何與連接到計算機的設備通信並通過它們與物理世界通信？
- 多個運行的程序如何同步互斥地對共享資源進行訪問？
- 一個運行的程序可以創建另一個程序的實例嗎？需要等待另外一個程序執行完成嗎？一個運行的程序能暫停或恢復另一個正在運行的程序嗎？

操作系統主要通過基於 ABI 的系統調用接口來給應用程序提供上述服務，以支持應用程序的各種需求。對於實際操作系統而言，有多少操作系統，就有多少種不同類型的系統調用接口。通用操作系統為支持各種應用的服務需求，需要有相對多的系統調用服務接口，比如目前 Linux 有超過三百個的系統調用接口。下面列出了一些相對比較重要的操作系統接口或抽象，以及它們的大致功能：

* 進程（即程序運行過程）管理：複製創建進程 fork 、退出進程 exit 、執行進程 exec 等。
* 線程管理：線程（即程序的一個執行流）的創建、執行、調度切換等。
* 線程同步互斥的併發控制：互斥鎖 mutex 、信號量 semaphore 、管程 monitor 、條件變量 condition variable 等。
* 進程間通信：管道 pipe 、信號 signal 、事件 event 等。
* 虛存管理：內存空間映射 mmap 、改變數據段地址空間大小 sbrk 、共享內存 shm 等。
* 文件 I/O 操作：對存儲設備中的文件進行讀 read 、寫 write 、打開 open 、關閉 close 等操作。
* 外設 I/O 操作：外設包括鍵盤、顯示器、串口、磁盤、時鐘 ... ，主要採用文件 I/O 操作接口。

.. note::

   上述表述在某種程度上說明了操作系統對計算機硬件重要組成的抽象和虛擬化，這樣會有助於應用程序開發。應用程序員只需訪問統一的抽象概念（如文件、進程等），就可以使用各種複雜的計算機物理資源（處理器、內存、外設等）：

   * 文件 (File) 是外設的一種抽象和虛擬化。特別對於存儲外設而言，文件是持久存儲的抽象。
   * 地址空間 (Address Space) 是對內存的抽象和虛擬化。
   * 進程 (Process) 是對計算機資源的抽象和虛擬化。而其中最核心的部分是對 CPU 的抽象與虛擬化。



.. image:: run-app.png
   :align: center
   :name: run-app

有了這些系統調用接口，簡單的應用程序就不用考慮底層硬件細節，可以在操作系統的服務支持和管理下簡潔地完成其應用功能了。在現階段，也許大家對進程、文件、地址空間等抽象概念還不瞭解，在接下來的章節會對這些概念有進一步的介紹。值得注意的是，我們設計的各種操作系統總共只用到三十個左右系統調用功能接口（如下表所示），就可以支持應用需要的上述功能。而且這些調用與最初的 UNIX 的系統調用接口類似，幾乎沒有變化。儘管UNIX 的系統調用最早是在 1970 年左右設計和實現的，但這些調用中的大多數仍然在今天的系統中廣泛使用。

..  chyyuu 在線組織表格 https://tableconvert.com/restructuredtext-generator 再用 format current (ctrl-alt-T C)格式化



====  ====================  =============  ===============================
編號   系統調用              所在章節        功能描述
====  ====================  =============  ===============================
1     sys_exit                 2           結束執行
2     sys_write                2/6         (2)輸出字符串/(6)寫文件
3     sys_yield                3           暫時放棄執行
4     sys_get_time             3           獲取當前時間
5     sys_getpid               5           獲取進程id
6     sys_fork                 5           創建子進程
7     sys_exec                 5           執行新程序
8     sys_waitpid              5           等待子進程結束
9     sys_read                 5/6         (5)讀取字符串/(6)讀文件
10    sys_open                 6           打開/創建文件
11    sys_close                6           關閉文件
12    sys_dup                  7           複製文件描述符
13    sys_pipe                 7           創建管道
14    sys_kill                 7           發送信號給某進程
15    sys_sigaction            7           設立信號處理例程
16    sys_sigprocmask          7           設置要阻止的信號
17    sys_sigreturn            7           從信號處理例程返回
18    sys_sleep                8           進程休眠一段時間
19    sys_thread_create        8           創建線程
20    sys_gettid               8           獲取線程id
21    sys_waittid              8           等待線程結束
22    sys_mutex_create         8           創建鎖
23    sys_mutex_lock           8           獲取鎖
24    sys_mutex_unlock         8           釋放鎖
25    sys_semaphore_create     8           創建信號量
26    sys_semaphore_up         8           減少信號量的計數
27    sys_semaphore_down       8           增加信號量的計數
28    sys_condvar_create       8           創建條件變量
29    sys_condvar_signal       8           喚醒阻塞在條件變量上的線程
30    sys_condvar_wait         8           阻塞與此條件變量關聯的當前線程
====  ====================  =============  ===============================


系統調用接口舉例
---------------------------------------------------

.. chyyuu 可以有兩個例子，體現API和ABI
   #![feature(asm)]
   let cmd = 0xd1;
   unsafe {
      asm!("out 0x64, eax", in("eax") cmd);
   }

   use std::io::{self, Write};

   fn main() -> io::Result<()> {
   io::stdout().write_all(b"hello world")?;

   Ok(())
   }

 
我們以rCore-Tutorial中的例子，一個應用程序顯示一個字符串，來看看系統調用的具體內容。應用程序的代碼如下：

.. code-block:: rust
   :linenos:

   // user/src/bin/hello_world.rs
   ...
   pub fn main() -> i32 {
      println!("Hello world from user mode program!");
      0
   }    

這個程序的功能就是顯示一行字符串（重點看第4行的代碼）。注意，這裡的 `println!` 一個宏。而進一步跟蹤源代碼 （位於  `user/src/console.rs` ），可以看到 `println!` 會進一步展開為 `write` 函數：

.. code-block:: rust
   :linenos:

   // user/src/console.rs
   ...
   impl Write for Stdout {
      fn write_str(&mut self, s: &str) -> fmt::Result {
         write(STDOUT, s.as_bytes());
         Ok(())
      }
   }

這個write函數就是對系統調用 `sys_write` 的封裝：


.. code-block:: rust
   :linenos:

   // user/src/lib.rs
   ...
   pub fn write(fd: usize, buf: &[u8]) -> isize {
    sys_write(fd, buf)
   }

   // user/src/syscall.rs
   ...
   pub fn sys_write(fd: usize, buffer: &[u8]) -> isize {
      syscall(SYSCALL_WRITE, [fd, buffer.as_ptr() as usize, buffer.len()])
   }


`sys_write` 用戶庫函數封裝了 `sys_write`  系統調用的API接口，這個系統調用API的參數和返回值的含義如下：

- `SYSCALL_WRITE` 表示 `sys_write` 的系統調用號
- `fd` 表示待寫入文件的文件描述符；
- `buf` 表示內存中緩衝區的起始地址；
- `len` 表示內存中緩衝區的長度；
- 返回值：返回成功寫入的長度或錯誤值

而 `sys_write`  系統調用的ABI接口描述了具體用哪些寄存器來保存參數和返回值：

.. code-block:: rust
   :linenos:

   // user/src/syscall.rs
   ...
   fn syscall(id: usize, args: [usize; 3]) -> isize {
      let mut ret: isize;
      unsafe {
         asm!(
               "ecall",
               inlateout("x10") args[0] => ret,
               in("x11") args[1],
               in("x12") args[2],
               in("x17") id
         );
      }
      ret
   }

這裡我們看到，API中的各個參數和返回值分別被RISC-V通用寄存器 `x17` （即存放系統調用號）、 `x10` （存放 `fd` ，也保存返回值） 、 `x11` （存放 `buf` ）和 `x12` （存放 `len` ）保存。
