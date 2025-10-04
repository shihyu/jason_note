基於文件的標準輸入/輸出
===========================================

本節導讀
-------------------------------------------

本節我們介紹為何要把標準輸入/輸出用文件來進行抽象，以及如何以文件和文件描述符概念來重新定義標準輸入/輸出，並在進程中把各種文件描述符組織到文件描述符表中，同時將進程對於標準輸入輸出的訪問修改為基於文件抽象的接口實現。這主要是為下一節支持進程間信息傳遞的管道實現打下基礎。由於管道是基於文件抽象接口來實現的，所以我們將首先對 **一切皆是文件** 的設計思路進行介紹。

一切皆是文件
-------------------------------------------

.. chyyuu 可以簡單介紹一下文件的起源???

在UNIX操作系統之前，大多數的操作系統提供了各種複雜且不規則的設計實現來處理各種I/O設備（也可稱為I/O資源），如鍵盤、顯示器、以磁盤為代表的存儲介質、以串口為代表的通信設備等，使得應用程序開發繁瑣且很難統一表示和處理I/O設備。隨著UNIX的誕生，一個簡潔優雅的I/O設備抽象出現了，這就是 **文件** 。在 UNIX 操作系統中，”**一切皆文件**“ (Everything is a file) 是一種重要的設計思想，這種設計思想繼承於 Multics 操作系統的 **通用性** 文件的設計理念，並進行了進一步的簡化。在本章中，應用程序訪問的 **文件** (File) 就是一系列的字節組合。操作系統管理文件，但操作系統不關心文件內容，只關心如何對文件按字節流進行讀寫的機制，這就意味著任何程序可以讀寫任何文件（即字節流），對文件具體內容的解析是應用程序的任務，操作系統對此不做任何干涉。例如，一個Rust編譯器可以讀取一個C語言源程序並進行編譯，操作系統並不會阻止這樣的事情發生。


有了文件這樣的抽象後，操作系統內核就可把能讀寫的I/O資源按文件來進行管理，並把文件分配給進程，讓進程以統一的文件訪問接口與I/O 資源進行交互。在目前和後續可能涉及到的I/O硬件設備中，大致可以分成以下幾種：

- **鍵盤設備** 是程序獲得字符輸入的一種設備，也可抽象為一種只讀性質的文件，可以從這個文件中讀出一系列的字節序列；
- **屏幕設備** 是展示程序的字符輸出結果的一種字符顯示設備，可抽象為一種只寫性質的文件，可以向這個文件中寫入一系列的字節序列，在顯示屏上可以直接呈現出來；
- **串口設備** 是獲得字符輸入和展示程序的字符輸出結果的一種字符通信設備，可抽象為一種可讀寫性質的文件，可以向這個文件中寫入一系列的字節序列傳給程序，也可把程序要顯示的字符傳輸出去；還可以把這個串口設備拆分成兩個文件，一個用於獲取輸入字符的只讀文件和一個傳出輸出字符的只寫文件。


在QEMU模擬的RISC-V計算機和K210物理硬件上存在虛擬/物理串口設備，開發者可通過QEMU的串口命令行界面或特定串口通信工具軟件來對虛擬/物理串口設備進行輸入/輸出操作。由於RustSBI直接管理了串口設備，並給操作系統提供了基於串口收發字符的兩個SBI接口，從而使得操作系統可以很簡單地通過這兩個SBI接口，完成輸出或輸入字符串的工作。

.. ！！！下面的內容移到了chapter6: section3
.. 文件的抽象接口 ``File trait`` 
.. -------------------------------------------

.. 文件被操作系統來進行管理，並提供給應用程序使用。雖然文件可代表很多種不同類型的I/O 資源，但是在進程看來，所有文件的訪問都可以通過一個很簡潔的統一抽象接口 ``File`` 來進行：

.. .. code-block:: rust

..     // os/src/fs/mod.rs

..     pub trait File : Send + Sync {
..         fn read(&self, buf: UserBuffer) -> usize;
..         fn write(&self, buf: UserBuffer) -> usize;
..     }

.. 這個接口在內存和I/O資源之間建立了數據交換的通道。其中 ``UserBuffer`` 是我們在 ``mm`` 子模塊中定義的應用地址空間中的一段緩衝區（即內存）的抽象。它的具體實現在本質上其實只是一個 ``&[u8]`` ，位於應用地址空間中，內核無法直接通過用戶地址空間的虛擬地址來訪問，因此需要進行封裝。然而，在理解抽象接口 ``File`` 的各方法時，我們仍可以將 ``UserBuffer`` 看成一個 ``&[u8]`` 切片，它是一個同時給出了緩衝區起始地址和長度的胖指針。

.. ``read`` 指的是從文件（即I/O資源）中讀取數據放到緩衝區中，最多將緩衝區填滿（即讀取緩衝區的長度那麼多字節），並返回實際讀取的字節數；而 ``write`` 指的是將緩衝區中的數據寫入文件，最多將緩衝區中的數據全部寫入，並返回直接寫入的字節數。至於 ``read`` 和 ``write`` 的實現則與文件具體是哪種類型有關，它決定了數據如何被讀取和寫入。

.. 回過頭來再看一下用戶緩衝區的抽象 ``UserBuffer`` ，它的聲明如下：

.. .. code-block:: rust

..     // os/src/mm/page_table.rs

..     pub fn translated_byte_buffer(
..         token: usize,
..         ptr: *const u8,
..         len: usize
..     ) -> Vec<&'static mut [u8]>;

..     pub struct UserBuffer {
..         pub buffers: Vec<&'static mut [u8]>,
..     }

..     impl UserBuffer {
..         pub fn new(buffers: Vec<&'static mut [u8]>) -> Self {
..             Self { buffers }
..         }
..         pub fn len(&self) -> usize {
..             let mut total: usize = 0;
..             for b in self.buffers.iter() {
..                 total += b.len();
..             }
..             total
..         }
..     }

.. 它只是將我們調用 ``translated_byte_buffer`` 獲得的包含多個切片的 ``Vec`` 進一步包裝起來，通過 ``len`` 方法可以得到緩衝區的長度。此外，我們還讓它作為一個迭代器可以逐字節進行讀寫。有興趣的同學可以參考類型 ``UserBufferIterator`` 還有 ``IntoIterator`` 和 ``Iterator`` 兩個 Trait 的使用方法。

標準輸入/輸出對 ``File trait`` 的實現
----------------------------------------------------------------

其實我們在第二章就對應用程序引入了基於 **文件** 的標準輸出接口 ``sys_write`` ，在第五章引入了基於 **文件** 的標準輸入接口 ``sys_read`` ；在第六章引入 **文件系統** ，在進程控制塊中添加了表示打開文件集合的文件描述符表。我們提前把標準輸出設備在文件描述符表中的文件描述符的值規定為 ``1`` ，用 ``Stdout`` 表示；把標準輸入設備在文件描述符表中的文件描述符的值規定為 ``0``，用 ``Stdin`` 表示 。現在，我們可以重構操作系統，為標準輸入和標準輸出實現 ``File`` Trait，使得進程可以按文件接口與I/O外設進行交互：

.. code-block:: rust
    :linenos:

    // os/src/fs/stdio.rs

    pub struct Stdin;

    pub struct Stdout;

    impl File for Stdin {
        fn read(&self, mut user_buf: UserBuffer) -> usize {
            assert_eq!(user_buf.len(), 1);
            // busy loop
            let mut c: usize;
            loop {
                c = console_getchar();
                if c == 0 {
                    suspend_current_and_run_next();
                    continue;
                } else {
                    break;
                }
            }
            let ch = c as u8;
            unsafe { user_buf.buffers[0].as_mut_ptr().write_volatile(ch); }
            1
        }
        fn write(&self, _user_buf: UserBuffer) -> usize {
            panic!("Cannot write to stdin!");
        }
    }

    impl File for Stdout {
        fn read(&self, _user_buf: UserBuffer) -> usize{
            panic!("Cannot read from stdout!");
        }
        fn write(&self, user_buf: UserBuffer) -> usize {
            for buffer in user_buf.buffers.iter() {
                print!("{}", core::str::from_utf8(*buffer).unwrap());
            }
            user_buf.len()
        }
    }

可以看到，標準輸入文件 ``Stdin`` 是隻讀文件，只允許進程通過 ``read`` 從裡面讀入，目前每次僅支持讀入一個字符，其實現與之前的 ``sys_read`` 基本相同，只是需要通過 ``UserBuffer`` 來獲取具體將字節寫入的位置。相反，標準輸出文件 ``Stdout`` 是隻寫文件，只允許進程通過 ``write`` 寫入到裡面，實現方法是遍歷每個切片，將其轉化為字符串通過 ``print!`` 宏來輸出。

.. chyyuu 值得注意的是，如果有多核同時使用 ``print!`` 宏，將會導致兩個不同的輸出交錯到一起造成輸出混亂，後續我們還會對它做一些改進。


對標準輸入/輸出的管理
-------------------------------------------

這樣，應用程序如果要基於文件進行I/O訪問，大致就會涉及如下幾個操作：

- 打開（open）：進程只有打開文件，操作系統才能返回一個可進行讀寫的文件描述符給進程，進程才能基於這個值來進行對應文件的讀寫；
- 關閉（close）：進程基於文件描述符關閉文件後，就不能再對文件進行讀寫操作了，這樣可以在一定程度上保證對文件的合法訪問；
- 讀（read）：進程可以基於文件描述符來讀文件內容到相應內存中；
- 寫（write）：進程可以基於文件描述符來把相應內存內容寫到文件中；


在本節中，還不會涉及創建文件。當一個進程被創建的時候，內核會默認為其打開三個缺省就存在的文件：

- 文件描述符為 0 的標準輸入
- 文件描述符為 1 的標準輸出
- 文件描述符為 2 的標準錯誤輸出

在我們的實現中並不區分標準輸出和標準錯誤輸出，而是會將文件描述符 1 和 2 均對應到標準輸出。實際上，在本章中，標準輸出文件就是串口輸出，標準輸入文件就是串口輸入。

這裡隱含著有關文件描述符的一條重要的規則：即進程打開一個文件的時候，內核總是會將文件分配到該進程文件描述符表中 **最小的** 空閒位置。比如，當一個進程被創建以後立即打開一個文件，則內核總是會返回文件描述符 3 （0~2號文件描述符已被缺省打開了）。當我們關閉一個打開的文件之後，它對應的文件描述符將會變得空閒並在後面可以被分配出去。


創建標準輸入/輸出文件
+++++++++++++++++++++++++++++++++++++++++++++++++


當新建一個進程的時候，我們需要按照先前的說明為進程打開標準輸入文件和標準輸出文件：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 18-25

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn new(elf_data: &[u8]) -> Self {
            ...
            let task_control_block = Self {
                pid: pid_handle,
                kernel_stack,
                inner: Mutex::new(TaskControlBlockInner {
                    trap_cx_ppn,
                    base_size: user_sp,
                    task_cx_ptr: task_cx_ptr as usize,
                    task_status: TaskStatus::Ready,
                    memory_set,
                    parent: None,
                    children: Vec::new(),
                    exit_code: 0,
                    fd_table: vec![
                        // 0 -> stdin
                        Some(Arc::new(Stdin)),
                        // 1 -> stdout
                        Some(Arc::new(Stdout)),
                        // 2 -> stderr
                        Some(Arc::new(Stdout)),
                    ],
                }),
            };
            ...
        }
    }


繼承標準輸入/輸出文件
+++++++++++++++++++++++++++++++++++++++++++++++++

此外，在 fork 的時候，子進程需要完全繼承父進程的文件描述符表來和父進程共享所有文件：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 8-16,29

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn fork(self: &Arc<TaskControlBlock>) -> Arc<TaskControlBlock> {
            ...
            // push a goto_trap_return task_cx on the top of kernel stack
            let task_cx_ptr = kernel_stack.push_on_top(TaskContext::goto_trap_return());
            // copy fd table
            let mut new_fd_table: Vec<Option<Arc<dyn File + Send + Sync>>> = Vec::new();
            for fd in parent_inner.fd_table.iter() {
                if let Some(file) = fd {
                    new_fd_table.push(Some(file.clone()));
                } else {
                    new_fd_table.push(None);
                }
            }
            let task_control_block = Arc::new(TaskControlBlock {
                pid: pid_handle,
                kernel_stack,
                inner: Mutex::new(TaskControlBlockInner {
                    trap_cx_ppn,
                    base_size: parent_inner.base_size,
                    task_cx_ptr: task_cx_ptr as usize,
                    task_status: TaskStatus::Ready,
                    memory_set,
                    parent: Some(Arc::downgrade(self)),
                    children: Vec::new(),
                    exit_code: 0,
                    fd_table: new_fd_table,
                }),
            });
            // add child
            ...
        }
    }

這樣，即使我們僅手動為初始進程 ``initproc`` 打開了標準輸入輸出，所有進程也都可以訪問它們。

讀寫標準輸入/輸出文件
---------------------------------------------------

由於有基於文件抽象接口和文件描述符表，之前實現的文件讀寫系統調用 ``sys_read/write`` 可以直接用於標準輸入/輸出文件，很好地達到了代碼重用的目標。
這樣，操作系統通過文件描述符在當前進程的文件描述符表中找到某個文件，無需關心文件具體的類型，只要知道它一定實現了 ``File`` Trait 的 ``read/write`` 方法即可。Trait 對象提供的運行時多態能力會在運行的時候幫助我們定位到符合實際類型的 ``read/write`` 方法，完成不同類型文件各自的讀寫。
