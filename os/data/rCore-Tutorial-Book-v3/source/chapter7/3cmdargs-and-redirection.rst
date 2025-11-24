命令行參數與標準 I/O 重定向
=================================================

本節導讀
-------------------------------------------------

雖然我們已經支持從文件系統中加載應用，還實現了文件的創建和讀寫，但是目前我們在應用中只能硬編碼要操作的文件，這就使得應用的功能大大受限，shell程序對於文件的交互訪問能力也很弱。為了解決這些問題，我們需要在shell程序和內核中支持命令行參數的解析和傳遞。而且我們可以把應用的命令行參數的擴展，管道以及標準 I/O 重定向功能綜合在一起，來讓兩個甚至多個互不相干的應用也能合作。

命令行參數
-------------------------------------------------

在使用 C/C++ 語言開發 Linux 應用的時候，我們可以使用標準庫提供的 ``argc/argv`` 來獲取命令行參數，它們是直接被作為參數傳給 ``main`` 函數的。下面來看一個打印命令行參數的例子：

.. code-block:: c
    :linenos:

    // a.c

    #include <stdio.h>

    int main(int argc, char* argv[]) {
        printf("argc = %d\n", argc);
        for (int i = 0; i < argc; i++) {
            printf("argv[%d] = %s\n", i, argv[i]);
        }
        return 0;
    }

其中 ``argc`` 表示命令行參數的個數，而 ``argv`` 是一個長度為 ``argc`` 的字符串數組，數組中的每個字符串都是一個命令行參數。我們可以在 Linux 系統上運行這個程序：

.. code-block:: console

    $ gcc a.c -oa -g -Wall
    $ ./a aa bb 11 22 cc
    argc = 6
    argv[0] = ./a
    argv[1] = aa
    argv[2] = bb
    argv[3] = 11
    argv[4] = 22
    argv[5] = cc

為了支持後續的一些功能，我們希望在內核和shell程序上支持這個功能。為了對實現正確性進行測試，在本章中我們編寫了一個名為 ``cmdline_args`` 的應用，它是用 Rust 編寫的，並只能在我們的內核上執行，但是它的功能是和 ``a.c`` 保持一致的。我們可以在我們的內核上運行該應用來看看效果：

.. code-block::

    Rust user shell
    >> cmdline_args aa bb 11 22 cc
    argc = 6
    argv[0] = cmdline_args
    argv[1] = aa
    argv[2] = bb
    argv[3] = 11
    argv[4] = 22
    argv[5] = cc
    Shell: Process 2 exited with code 0
    >> 

可以看到二者的輸出是基本相同的。

但是，要實現這個看似簡單的功能，需要內核和用戶態應用的共同努力。為了支持命令行參數， ``sys_exec`` 的系統調用接口需要發生變化：

.. code-block:: rust
    :linenos:

    // user/src/syscall.rs

    pub fn sys_exec(path: &str, args: &[*const u8]) -> isize;

可以看到，它的參數多出了一個 ``args`` 數組，數組中的每個元素都是一個命令行參數字符串的起始地址。由於我們是以引用的形式傳遞這個數組，實際傳遞給內核的是這個數組的起始地址：

.. code-block:: rust
    :linenos:

    // user/src/syscall.rs

    pub fn sys_exec(path: &str, args: &[*const u8]) -> isize {
        syscall(SYSCALL_EXEC, [path.as_ptr() as usize, args.as_ptr() as usize, 0])
    }

    // user/src/lib.rs

    pub fn exec(path: &str, args: &[*const u8]) -> isize { sys_exec(path, args) }

接下來我們分析一下，一行帶有命令行參數的命令從輸入到它的命令行參數被打印出來中間經歷了哪些過程。

shell程序的命令行參數分割
+++++++++++++++++++++++++++++++++++++++++++++++++

回憶一下，之前在shell程序 ``user_shell`` 中，一旦接收到一個回車，我們就會將當前行的內容 ``line`` 作為一個名字並試圖去執行同名的應用。但是現在 ``line`` 還可能包含一些命令行參數，只有最開頭的一個才是要執行的應用名。因此我們要做的第一件事情就是將 ``line`` 用空格進行分割：

.. code-block:: rust
    :linenos:

    // user/src/bin/user_shell.rs

    let args: Vec<_> = line.as_str().split(' ').collect();
    let mut args_copy: Vec<String> = args
    .iter()
    .map(|&arg| {
        let mut string = String::new();
        string.push_str(arg);
        string
    })
    .collect();

    args_copy
    .iter_mut()
    .for_each(|string| {
        string.push('\0');
    });

經過分割， ``args`` 中的 ``&str`` 都是 ``line`` 中的一段子區間，它們的結尾並沒有包含 ``\0`` ，因為 ``line`` 是我們輸入得到的，中間本來就沒有 ``\0`` 。由於在向內核傳入字符串的時候，我們只能傳入字符串的起始地址，因此我們必須保證其結尾為 ``\0`` 。從而我們用 ``args_copy`` 將 ``args`` 中的字符串拷貝一份到堆上並在末尾手動加入 ``\0`` 。這樣就可以安心的將 ``args_copy`` 中的字符串傳入內核了。我們用 ``args_addr`` 來收集這些字符串的起始地址：

.. code-block:: rust
    :linenos:

    // user/src/bin/user_shell.rs

    let mut args_addr: Vec<*const u8> = args_copy
    .iter()
    .map(|arg| arg.as_ptr())
    .collect();
    args_addr.push(0 as *const u8);

向量 ``args_addr`` 中的每個元素都代表一個命令行參數字符串的起始地址。由於我們要傳遞給內核的是這個向量的起始地址，為了讓內核能夠獲取到命令行參數的個數，我們需要在 ``args_addr`` 的末尾放入一個 0 ，這樣內核看到它的時候就能知道命令行參數已經獲取完畢了。

在 ``fork`` 出來的子進程裡面我們需要這樣執行應用：

.. code-block:: rust
    :linenos:

    // user/src/bin/user_shell.rs

    // child process
    if exec(args_copy[0].as_str(), args_addr.as_slice()) == -1 {
        println!("Error when executing!");
        return -4;
    }

sys_exec 將命令行參數壓入用戶棧
+++++++++++++++++++++++++++++++++++++++++++++++++

在 ``sys_exec`` 中，首先需要將應用傳進來的命令行參數取出來：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 6-14,19

    // os/src/syscall/process.rs

    pub fn sys_exec(path: *const u8, mut args: *const usize) -> isize {
        let token = current_user_token();
        let path = translated_str(token, path);
        let mut args_vec: Vec<String> = Vec::new();
        loop {
            let arg_str_ptr = *translated_ref(token, args);
            if arg_str_ptr == 0 {
                break;
            }
            args_vec.push(translated_str(token, arg_str_ptr as *const u8));
            unsafe { args = args.add(1); }
        }
        if let Some(app_inode) = open_file(path.as_str(), OpenFlags::RDONLY) {
            let all_data = app_inode.read_all();
            let task = current_task().unwrap();
            let argc = args_vec.len();
            task.exec(all_data.as_slice(), args_vec);
            // return argc because cx.x[10] will be covered with it later
            argc as isize
        } else {
            -1
        }
    }

這裡的 ``args`` 指向命令行參數字符串起始地址數組中的一個位置，每次我們都可以從一個起始地址通過 ``translated_str`` 拿到一個字符串，直到 ``args`` 為 0 就說明沒有更多命令行參數了。在第 19 行調用 ``TaskControlBlock::exec`` 的時候，我們需要將獲取到的 ``args_vec`` 傳入進去並將裡面的字符串壓入到用戶棧上。

.. code-block:: rust
    :linenos:
    :emphasize-lines: 11-34,45,50,51

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn exec(&self, elf_data: &[u8], args: Vec<String>) {
            // memory_set with elf program headers/trampoline/trap context/user stack
            let (memory_set, mut user_sp, entry_point) = MemorySet::from_elf(elf_data);
            let trap_cx_ppn = memory_set
                .translate(VirtAddr::from(TRAP_CONTEXT).into())
                .unwrap()
                .ppn();
            // push arguments on user stack
            user_sp -= (args.len() + 1) * core::mem::size_of::<usize>();
            let argv_base = user_sp;
            let mut argv: Vec<_> = (0..=args.len())
                .map(|arg| {
                    translated_refmut(
                        memory_set.token(),
                        (argv_base + arg * core::mem::size_of::<usize>()) as *mut usize
                    )
                })
                .collect();
            *argv[args.len()] = 0;
            for i in 0..args.len() {
                user_sp -= args[i].len() + 1;
                *argv[i] = user_sp;
                let mut p = user_sp;
                for c in args[i].as_bytes() {
                    *translated_refmut(memory_set.token(), p as *mut u8) = *c;
                    p += 1;
                }
                *translated_refmut(memory_set.token(), p as *mut u8) = 0;
            }
            // make the user_sp aligned to 8B for k210 platform
            user_sp -= user_sp % core::mem::size_of::<usize>();

            // **** hold current PCB lock
            let mut inner = self.acquire_inner_lock();
            // substitute memory_set
            inner.memory_set = memory_set;
            // update trap_cx ppn
            inner.trap_cx_ppn = trap_cx_ppn;
            // initialize trap_cx
            let mut trap_cx = TrapContext::app_init_context(
                entry_point,
                user_sp,
                KERNEL_SPACE.lock().token(),
                self.kernel_stack.get_top(),
                trap_handler as usize,
            );
            trap_cx.x[10] = args.len();
            trap_cx.x[11] = argv_base;
            *inner.get_trap_cx() = trap_cx;
            // **** release current PCB lock
        }
    }

第 11-34 行所做的主要工作是將命令行參數以某種格式壓入用戶棧。具體的格式可以參考下圖（比如應用傳入了兩個命令行參數 ``aa`` 和 ``bb`` ）：

.. image:: user-stack-cmdargs.png
    :align: center

- 首先需要在用戶棧上分配一個字符串指針數組，也就是藍色區域。數組中的每個元素都指向一個用戶棧更低處的命令行參數字符串的起始地址。在第 12~24 行可以看到，最開始我們只是分配空間，具體的值要等到字符串被放到用戶棧上之後才能確定更新。
- 第 23~32 行，我們逐個將傳入的 ``args`` 中的字符串壓入到用戶棧中，對應於圖中的橙色區域。為了實現方便，我們在用戶棧上預留空間之後逐字節進行復制。注意 ``args`` 中的字符串是通過 ``translated_str`` 從應用地址空間取出的，它的末尾不包含 ``\0`` 。為了應用能知道每個字符串的長度，我們需要手動在末尾加入 ``\0`` 。
- 第 34 行將 ``user_sp`` 以 8 字節對齊，即圖中的綠色區域。這是因為命令行參數的長度不一，很有可能壓入之後 ``user_sp`` 沒有對齊到 8 字節，那麼在 K210 平臺上在訪問用戶棧的時候就會觸發訪存不對齊的異常。在 Qemu 平臺上則並不存在這個問題。

我們還需要對應修改 Trap 上下文。首先是第 45 行，我們的 ``user_sp`` 相比之前已經發生了變化，它上面已經壓入了命令行參數。同時，我們還需要修改 Trap 上下文中的 ``a0/a1`` 寄存器，讓 ``a0`` 表示命令行參數的個數，而 ``a1`` 則表示圖中 ``argv_base`` 即藍色區域的起始地址。這兩個參數在第一次進入對應應用的用戶態的時候會被接收並用於還原命令行參數。

用戶庫從用戶棧上還原命令行參數
+++++++++++++++++++++++++++++++++++++++++++++++++

在應用第一次進入用戶態的時候，我們放在 Trap 上下文 a0/a1 兩個寄存器中的內容可以被用戶庫中的入口函數以參數的形式接收：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 10-24

    // user/src/lib.rs

    #[no_mangle]
    #[link_section = ".text.entry"]
    pub extern "C" fn _start(argc: usize, argv: usize) -> ! {
        unsafe {
            HEAP.lock()
                .init(HEAP_SPACE.as_ptr() as usize, USER_HEAP_SIZE);
        }
        let mut v: Vec<&'static str> = Vec::new();
        for i in 0..argc {
            let str_start = unsafe {
                ((argv + i * core::mem::size_of::<usize>()) as *const usize).read_volatile()
            };
            let len = (0usize..).find(|i| unsafe {
                ((str_start + *i) as *const u8).read_volatile() == 0
            }).unwrap();
            v.push(
                core::str::from_utf8(unsafe {
                    core::slice::from_raw_parts(str_start as *const u8, len)
                }).unwrap()
            );
        }
        exit(main(argc, v.as_slice()));
    }

可以看到，在入口 ``_start`` 中我們就接收到了命令行參數個數 ``argc`` 和字符串數組的起始地址 ``argv`` 。但是這個起始地址不太好用，我們希望能夠將其轉化為編寫應用的時候看到的 ``&[&str]`` 的形式。轉化的主體在第 10~23 行，就是分別取出 ``argc`` 個字符串的起始地址（基於字符串數組的 base 地址 ``argv`` ），從它向後找到第一個 ``\0`` 就可以得到一個完整的 ``&str`` 格式的命令行參數字符串並加入到向量 ``v`` 中。最後通過 ``v.as_slice`` 就得到了我們在 ``main`` 主函數中看到的 ``&[&str]`` 。

通過命令行工具 cat 輸出文件內容
+++++++++++++++++++++++++++++++++++++++++++++++++

有了之前的命令行參數支持，我們就可以編寫命令行工具 ``cat`` 來輸出指定文件的內容了。它的使用方法如下：

.. code-block::

    >> filetest_simple
    file_test passed!
    Shell: Process 2 exited with code 0
    >> cat filea
    Hello, world!
    Shell: Process 2 exited with code 0
    >> 

``filetest_simple`` 會將 ``Hello, world!`` 輸出到文件 ``filea`` 中。之後我們就可以通過 ``cat filea`` 來打印文件 ``filea`` 中的內容。

``cat`` 本身也是一個應用，且很容易實現：

.. code-block:: rust
    :linenos:

    // user/src/bin/cat.rs

    #![no_std]
    #![no_main]

    #[macro_use]
    extern crate user_lib;
    extern crate alloc;

    use user_lib::{
        open,
        OpenFlags,
        close,
        read,
    };
    use alloc::string::String;

    #[no_mangle]
    pub fn main(argc: usize, argv: &[&str]) -> i32 {
        assert!(argc == 2);
        let fd = open(argv[1], OpenFlags::RDONLY);
        if fd == -1 {
            panic!("Error occurred when opening file");
        }
        let fd = fd as usize;
        let mut buf = [0u8; 16];
        let mut s = String::new();
        loop {
            let size = read(fd, &mut buf) as usize;
            if size == 0 { break; }
            s.push_str(core::str::from_utf8(&buf[..size]).unwrap());
        }
        println!("{}", s);
        close(fd);
        0
    }


標準輸入輸出重定向
-------------------------------------------------

為了進一步增強shell程序使用文件系統時的靈活性，我們需要新增標準輸入輸出重定向功能。這個功能在我們使用 Linux 內核的時候很常用，我們在自己的內核中舉個例子：

.. code-block::

    >> yield > fileb
    Shell: Process 2 exited with code 0
    >> cat fileb
    Hello, I am process 2.
    Back in process 2, iteration 0.
    Back in process 2, iteration 1.
    Back in process 2, iteration 2.
    Back in process 2, iteration 3.
    Back in process 2, iteration 4.
    yield pass.

    Shell: Process 2 exited with code 0
    >> 

通過 ``>`` 我們可以將應用 ``yield`` 的輸出重定向到文件 ``fileb`` 中。我們也可以注意到在屏幕上暫時看不到 ``yield`` 的輸出了。在應用 ``yield`` 退出之後，我們可以使用 ``cat`` 工具來查看文件 ``fileb`` 的內容，可以看到裡面的確是 ``yield`` 的輸出。同理，通過 ``<`` 則可以將一個應用的輸入重定向到某個指定文件而不是從鍵盤輸入。

注意重定向功能對於應用來說是透明的。在應用中除非明確指出了數據要從指定的文件輸入或者輸出到指定的文件，否則數據默認都是輸入自進程文件描述表位置 0 （即 ``fd=0`` ）處的標準輸入，並輸出到進程文件描述符表位置 1 （即  ``fd=1`` ）處的標準輸出。這是由於內核在執行 ``sys_exec`` 系統調用創建基於新應用的進程時，會直接把文件描述符表位置 0 放置標準輸入文件，位置 1 放置標準輸出文件，位置 2 放置標準錯誤輸出文件。標準輸入/輸出文件其實是把設備當成文件，標準輸入文件就是串口的輸入或鍵盤，而標準輸出文件就是串口的輸出或顯示器。

因此，在應用執行之前，我們就要對應用進程的文件描述符表進行某種替換。以輸出為例，我們需要提前打開文件並用這個文件來替換掉應用文件描述符表位置 1 處的標準輸出文件，這就完成了所謂的重定向。在重定向之後，應用認為自己輸出到  ``fd=1`` 的標準輸出文件，但實際上是輸出到我們指定的文件中。我們能夠做到這一點還是得益於文件的抽象，因為在進程看來無論是標準輸出還是常規文件都是一種文件，可以通過同樣的接口來讀寫。

為了實現重定向功能，我們需要引入一個新的系統調用 ``sys_dup`` ：

.. code-block:: rust
    :linenos:

    // user/src/syscall.rs

    /// 功能：將進程中一個已經打開的文件複製一份並分配到一個新的文件描述符中。
    /// 參數：fd 表示進程中一個已經打開的文件的文件描述符。
    /// 返回值：如果出現了錯誤則返回 -1，否則能夠訪問已打開文件的新文件描述符。
    /// 可能的錯誤原因是：傳入的 fd 並不對應一個合法的已打開文件。
    /// syscall ID：24
    pub fn sys_dup(fd: usize) -> isize;

這個系統調用的實現非常簡單：

.. code-block:: rust
    :linenos:

    // os/src/syscall/fs.rs

    pub fn sys_dup(fd: usize) -> isize {
        let task = current_task().unwrap();
        let mut inner = task.acquire_inner_lock();
        if fd >= inner.fd_table.len() {
            return -1;
        }
        if inner.fd_table[fd].is_none() {
            return -1;
        }
        let new_fd = inner.alloc_fd();
        inner.fd_table[new_fd] = Some(Arc::clone(inner.fd_table[fd].as_ref().unwrap()));
        new_fd as isize
    }

在 ``sys_dup`` 函數中，首先檢查傳入 ``fd`` 的合法性。然後在文件描述符表中分配一個新的文件描述符，並保存 ``fd`` 指向的已打開文件的一份拷貝即可。

那麼我們應該在什麼時候進行替換，又應該如何利用 ``sys_dup`` 進行替換呢？

答案是在shell程序 ``user_shell`` 中進行處理。在分割命令行參數的時候，我們要檢查是否存在通過 ``<`` 或 ``>`` 進行輸入輸出重定向的情況，如果存在的話則需要將它們從命令行參數中移除，並記錄匹配到的輸入文件名或輸出文件名到字符串 ``input`` 或 ``output`` 中。注意，為了實現方便，我們這裡假設輸入shell程序的命令一定合法：即 ``<`` 或 ``>`` 最多隻會出現一次，且後面總是會有一個參數作為重定向到的文件。

.. code-block:: rust
    :linenos:

    // user/src/bin/user_shell.rs

    // redirect input
    let mut input = String::new();
    if let Some((idx, _)) = args_copy
    .iter()
    .enumerate()
    .find(|(_, arg)| arg.as_str() == "<\0") {
        input = args_copy[idx + 1].clone();
        args_copy.drain(idx..=idx + 1);
    }

    // redirect output
    let mut output = String::new();
    if let Some((idx, _)) = args_copy
    .iter()
    .enumerate()
    .find(|(_, arg)| arg.as_str() == ">\0") {
        output = args_copy[idx + 1].clone();
        args_copy.drain(idx..=idx + 1);
    }

打開文件和替換的過程則發生在 ``fork`` 之後的子進程分支中：

.. code-block:: rust
    :linenos:

    // user/src/bin/user_shell.rs

    let pid = fork();
    if pid == 0 {
        // input redirection
        if !input.is_empty() {
            let input_fd = open(input.as_str(), OpenFlags::RDONLY);
            if input_fd == -1 {
                println!("Error when opening file {}", input);
                return -4;
            }
            let input_fd = input_fd as usize;
            close(0);
            assert_eq!(dup(input_fd), 0);
            close(input_fd);
        }
        // output redirection
        if !output.is_empty() {
            let output_fd = open(
                output.as_str(),
                OpenFlags::CREATE | OpenFlags::WRONLY
            );
            if output_fd == -1 {
                println!("Error when opening file {}", output);
                return -4;
            }
            let output_fd = output_fd as usize;
            close(1);
            assert_eq!(dup(output_fd), 1);
            close(output_fd);
        }
        // child process
        if exec(args_copy[0].as_str(), args_addr.as_slice()) == -1 {
            println!("Error when executing!");
            return -4;
        }
        unreachable!();
    } else {
        let mut exit_code: i32 = 0;
        let exit_pid = waitpid(pid as usize, &mut exit_code);
        assert_eq!(pid, exit_pid);
        println!("Shell: Process {} exited with code {}", pid, exit_code);
    }

- 輸入重定向發生在第 6~16 行。我們嘗試打開輸入文件 ``input`` 到 ``input_fd`` 中。之後，首先通過 ``close`` 關閉標準輸入所在的文件描述符 0 。之後通過 ``dup`` 來分配一個新的文件描述符來訪問 ``input_fd`` 對應的輸入文件。這裡用到了文件描述符分配的重要性質：即必定分配可用描述符中編號最小的一個。由於我們剛剛關閉了描述符 0 ，那麼在 ``dup`` 的時候一定會將它分配出去，於是現在應用進程的文件描述符 0 就對應到輸入文件了。最後，因為應用進程的後續執行不會用到輸入文件原來的描述符 ``input_fd`` ，所以就將其關掉。
- 輸出重定向則發生在 18~31 行。它的原理和輸入重定向幾乎完全一致，只是通過 ``open`` 打開文件的標誌不太相同。

實現到這裡，就可以通過 ``exec`` 來執行應用了。

小結
-------------------------------------------------

雖然 ``fork/exec/waitpid`` 三個經典的系統調用自它們於古老的 UNIX 時代誕生以來已經過去了太長時間，從某種程度上來講已經不太適合新的內核環境了。人們也已經提出了若干種替代品並已經在進行實踐，比如POSIX標準中的 ``posix_spawn`` 或者 Linux 上的 ``clone`` 系統調用。但是它們迄今為止仍然存在就證明在它們的設計中還能夠找到可取之處。從本節介紹的重定向就可以看出它們的靈活性以及強大的功能性：我們能夠進行重定向恰恰是因為創建新應用進程分為 ``fork`` 和 ``exec`` 兩個系統調用，那麼在這兩個系統調用之間我們就能夠進行一些類似重定向的處理。在實現的過程中，我們還用到了 ``fork`` 出來的子進程會和父進程共享文件描述符表的性質。
