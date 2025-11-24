進程管理機制的設計實現
============================================

本節導讀
--------------------------------------------

有了上節的數據結構和相關基本方法的介紹後，我們還需完成進程管理關鍵功能的實現，從而構造出一個完整的白堊紀“傷齒龍”操作系統。本節將從如下四個方面介紹如何基於上一節設計的內核數據結構來實現進程管理：

- 創建初始進程：創建第一個用戶態進程 ``initproc``；
- 進程調度機制：當進程主動調用 ``sys_yield`` 交出 CPU 使用權或者內核把本輪分配的時間片用盡的進程換出且換入下一個進程；
- 進程生成機制：介紹進程相關的兩個重要系統調用 ``sys_fork/sys_exec`` 的實現；
- 進程資源回收機制：當進程調用 ``sys_exit`` 正常退出或者出錯被內核終止之後如何保存其退出碼，其父進程通過 ``sys_waitpid`` 系統調用收集該進程的信息並回收其資源。
- 字符輸入機制：為了支持shell程序-user_shell獲得字符輸入，介紹 ``sys_read`` 系統調用的實現；

初始進程的創建
--------------------------------------------

內核初始化完畢之後即會調用 ``task`` 子模塊提供的 ``add_initproc`` 函數來將初始進程 ``initproc`` 加入任務管理器，但在這之前我們需要初始化初始進程的進程控制塊 ``INITPROC`` ，這個過程基於 ``lazy_static`` 在運行時完成。

.. code-block:: rust

    // os/src/task/mod.rs

    use crate::loader::get_app_data_by_name;
    use manager::add_task;

    lazy_static! {
        pub static ref INITPROC: Arc<TaskControlBlock> = Arc::new(
            TaskControlBlock::new(get_app_data_by_name("initproc").unwrap())
        );
    }

    pub fn add_initproc() {
        add_task(INITPROC.clone());
    }

我們調用 ``TaskControlBlock::new`` 來創建一個進程控制塊，它需要傳入 ELF 可執行文件的數據切片作為參數，這可以通過加載器 ``loader`` 子模塊提供的 ``get_app_data_by_name`` 接口查找 ``initproc`` 的 ELF 執行文件數據來獲得。在初始化 ``INITPROC`` 之後，就可以在 ``add_initproc`` 中調用 ``task`` 的任務管理器 ``manager`` 子模塊提供的 ``add_task`` 接口，將其加入到任務管理器。

接下來介紹 ``TaskControlBlock::new`` 是如何實現的：

.. code-block:: rust
    :linenos:

    // os/src/task/task.rs

    use super::{PidHandle, pid_alloc, KernelStack};
    use super::TaskContext;
    use crate::config::TRAP_CONTEXT;
    use crate::trap::TrapContext;

    // impl TaskControlBlock
    pub fn new(elf_data: &[u8]) -> Self {
        // memory_set with elf program headers/trampoline/trap context/user stack
        let (memory_set, user_sp, entry_point) = MemorySet::from_elf(elf_data);
        let trap_cx_ppn = memory_set
            .translate(VirtAddr::from(TRAP_CONTEXT).into())
            .unwrap()
            .ppn();
        // alloc a pid and a kernel stack in kernel space
        let pid_handle = pid_alloc();
        let kernel_stack = KernelStack::new(&pid_handle);
        let kernel_stack_top = kernel_stack.get_top();
        // push a task context which goes to trap_return to the top of kernel stack
        let task_control_block = Self {
            pid: pid_handle,
            kernel_stack,
            inner: unsafe { UPSafeCell::new(TaskControlBlockInner {
                trap_cx_ppn,
                base_size: user_sp,
                task_cx: TaskContext::goto_trap_return(kernel_stack_top),
                task_status: TaskStatus::Ready,
                memory_set,
                parent: None,
                children: Vec::new(),
                exit_code: 0,
            })},
        };
        // prepare TrapContext in user space
        let trap_cx = task_control_block.inner_exclusive_access().get_trap_cx();
        *trap_cx = TrapContext::app_init_context(
            entry_point,
            user_sp,
            KERNEL_SPACE.exclusive_access().token(),
            kernel_stack_top,
            trap_handler as usize,
        );
        task_control_block
    }

- 第 11 行我們解析應用的 ELF 執行文件得到應用地址空間 ``memory_set`` ，用戶棧在應用地址空間中的位置 ``user_sp`` 以及應用的入口點 ``entry_point`` 。
- 第 12 行我們手動查頁表找到位於應用地址空間中新創建的Trap 上下文被實際放在哪個物理頁幀上，用來做後續的初始化。
- 第 16~19 行我們為該進程分配 PID 以及內核棧，並記錄下內核棧在內核地址空間的位置 ``kernel_stack_top`` 。
- 第 20 行我們在該進程的內核棧上壓入初始化的任務上下文，使得第一次任務切換到它的時候可以跳轉到 ``trap_return`` 並進入用戶態開始執行。
- 第 21 行我們整合之前的部分信息創建進程控制塊 ``task_control_block`` 。
- 第 37 行我們初始化位於該進程應用地址空間中的 Trap 上下文，使得第一次進入用戶態的時候時候能正確跳轉到應用入口點並設置好用戶棧，同時也保證在 Trap 的時候用戶態能正確進入內核態。
- 第 44 行將 ``task_control_block`` 返回。

進程調度機制
--------------------------------------------

通過調用 ``task`` 子模塊提供的 ``suspend_current_and_run_next`` 函數可以暫停當前任務並切換到下一個任務，當應用調用 ``sys_yield`` 主動交出使用權、本輪時間片用盡或者由於某些原因內核中的處理無法繼續的時候，就會在內核中調用此函數觸發調度機制並進行任務切換。下面給出了兩種典型的使用情況：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 4,18

    // os/src/syscall/process.rs

    pub fn sys_yield() -> isize {
        suspend_current_and_run_next();
        0
    }

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Interrupt(Interrupt::SupervisorTimer) => {
                set_next_trigger();
                suspend_current_and_run_next();
            }
            ...
        }
        trap_return();
    }

隨著進程概念的引入， ``suspend_current_and_run_next`` 的實現也需要發生變化：

.. code-block:: rust
    :linenos:

    // os/src/task/mod.rs

    use processor::{task_current_task, schedule};
    use manager::add_task;

    pub fn suspend_current_and_run_next() {
        // There must be an application running.
        let task = take_current_task().unwrap();

        // ---- access current TCB exclusively
        let mut task_inner = task.inner_exclusive_access();
        let task_cx_ptr = &mut task_inner.task_cx as *mut TaskContext;
        // Change status to Ready
        task_inner.task_status = TaskStatus::Ready;
        drop(task_inner);
        // ---- stop exclusively accessing current PCB

        // push back to ready queue.
        add_task(task);
        // jump to scheduling cycle
        schedule(task_cx_ptr);
    }

首先通過 ``take_current_task`` 來取出當前正在執行的任務，修改其進程控制塊內的狀態，隨後將這個任務放入任務管理器的隊尾。接著調用 ``schedule`` 函數來觸發調度並切換任務。注意，當僅有一個任務的時候， ``suspend_current_and_run_next`` 的效果是會繼續執行這個任務。

進程的生成機制
--------------------------------------------

在內核中手動生成的進程只有初始進程 ``initproc`` ，餘下所有的進程都是它直接或間接 fork 出來的。當一個子進程被 fork 出來之後，它可以調用 ``exec`` 系統調用來加載並執行另一個可執行文件。因此， ``fork/exec`` 兩個系統調用提供了進程的生成機制。下面我們分別來介紹二者的實現。

fork 系統調用的實現
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

在實現 fork 的時候，最為關鍵且困難的是為子進程創建一個和父進程幾乎完全相同的應用地址空間。我們的實現如下：

.. code-block:: rust
    :linenos:

    // os/src/mm/memory_set.rs

    impl MapArea {
        pub fn from_another(another: &MapArea) -> Self {
            Self {
                vpn_range: VPNRange::new(
                    another.vpn_range.get_start(),
                    another.vpn_range.get_end()
                ),
                data_frames: BTreeMap::new(),
                map_type: another.map_type,
                map_perm: another.map_perm,
            }
        }
    }

    impl MemorySet {
        pub fn from_existed_user(user_space: &MemorySet) -> MemorySet {
            let mut memory_set = Self::new_bare();
            // map trampoline
            memory_set.map_trampoline();
            // copy data sections/trap_context/user_stack
            for area in user_space.areas.iter() {
                let new_area = MapArea::from_another(area);
                memory_set.push(new_area, None);
                // copy data from another space
                for vpn in area.vpn_range {
                    let src_ppn = user_space.translate(vpn).unwrap().ppn();
                    let dst_ppn = memory_set.translate(vpn).unwrap().ppn();
                    dst_ppn.get_bytes_array().copy_from_slice(src_ppn.get_bytes_array());
                }
            }
            memory_set
        }
    }

這需要對內存管理子模塊 ``mm`` 做一些拓展：

- 第 4 行的 ``MapArea::from_another`` 可以從一個邏輯段複製得到一個虛擬地址區間、映射方式和權限控制均相同的邏輯段，不同的是由於它還沒有真正被映射到物理頁幀上，所以 ``data_frames`` 字段為空。
- 第 18 行的 ``MemorySet::from_existed_user`` 可以複製一個完全相同的地址空間。首先在第 19 行，我們通過 ``new_bare`` 新創建一個空的地址空間，並在第 21 行通過 ``map_trampoline`` 為這個地址空間映射上跳板頁面，這是因為我們解析 ELF 創建地址空間的時候，並沒有將跳板頁作為一個單獨的邏輯段插入到地址空間的邏輯段向量 ``areas`` 中，所以這裡需要單獨映射上。
  
  剩下的邏輯段都包含在 ``areas`` 中。我們遍歷原地址空間中的所有邏輯段，將複製之後的邏輯段插入新的地址空間，在插入的時候就已經實際分配了物理頁幀了。接著我們遍歷邏輯段中的每個虛擬頁面，對應完成數據複製，這隻需要找出兩個地址空間中的虛擬頁面各被映射到哪個物理頁幀，就可轉化為將數據從物理內存中的一個位置複製到另一個位置，使用 ``copy_from_slice`` 即可輕鬆實現。

接著，我們實現 ``TaskControlBlock::fork`` 來從父進程的進程控制塊創建一份子進程的控制塊：

.. code-block:: rust
    :linenos:

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn fork(self: &Arc<TaskControlBlock>) -> Arc<TaskControlBlock> {
            // ---- access parent PCB exclusively
            let mut parent_inner = self.inner_exclusive_access();
            // copy user space(include trap context)
            let memory_set = MemorySet::from_existed_user(
                &parent_inner.memory_set
            );
            let trap_cx_ppn = memory_set
                .translate(VirtAddr::from(TRAP_CONTEXT).into())
                .unwrap()
                .ppn();
            // alloc a pid and a kernel stack in kernel space
            let pid_handle = pid_alloc();
            let kernel_stack = KernelStack::new(&pid_handle);
            let kernel_stack_top = kernel_stack.get_top();
            let task_control_block = Arc::new(TaskControlBlock {
                pid: pid_handle,
                kernel_stack,
                inner: unsafe { UPSafeCell::new(TaskControlBlockInner {
                    trap_cx_ppn,
                    base_size: parent_inner.base_size,
                    task_cx: TaskContext::goto_trap_return(kernel_stack_top),
                    task_status: TaskStatus::Ready,
                    memory_set,
                    parent: Some(Arc::downgrade(self)),
                    children: Vec::new(),
                    exit_code: 0,
                })},
            });
            // add child
            parent_inner.children.push(task_control_block.clone());
            // modify kernel_sp in trap_cx
            // **** access children PCB exclusively
            let trap_cx = task_control_block.inner_exclusive_access().get_trap_cx();
            trap_cx.kernel_sp = kernel_stack_top;
            // return
            task_control_block
            // ---- stop exclusively accessing parent/children PCB automatically
        }
    }

它基本上和新建進程控制塊的 ``TaskControlBlock::new`` 是相同的，但要注意以下幾點：

- 子進程的地址空間不是通過解析 ELF 文件，而是通過在第 8 行調用 ``MemorySet::from_existed_user`` 複製父進程地址空間得到的；
- 第 24 行，我們讓子進程和父進程的 ``base_size`` ，也即應用數據的大小保持一致；
- 在 fork 的時候需要注意父子進程關係的維護。第 28 行我們將父進程的弱引用計數放到子進程的進程控制塊中，而在第 33 行我們將子進程插入到父進程的孩子向量 ``children`` 中。

我們在子進程內核棧上壓入一個初始化的任務上下文，使得內核一旦通過任務切換到該進程，就會跳轉到 ``trap_return`` 來進入用戶態。而在複製地址空間的時候，子進程的 Trap 上下文也是完全從父進程複製過來的，這可以保證子進程進入用戶態和其父進程回到用戶態的那一瞬間 CPU 的狀態是完全相同的（後面我們會讓它們的返回值不同從而區分兩個進程）。而兩個進程的應用數據由於地址空間複製的原因也是完全相同的，這是 fork 語義要求做到的。

在具體實現 ``sys_fork`` 的時候，我們需要特別注意如何體現父子進程的差異：

.. code-block:: rust
    :linenos: 
    :emphasize-lines: 11,28,33

    // os/src/syscall/process.rs

    pub fn sys_fork() -> isize {
        let current_task = current_task().unwrap();
        let new_task = current_task.fork();
        let new_pid = new_task.pid.0;
        // modify trap context of new_task, because it returns immediately after switching
        let trap_cx = new_task.inner_exclusive_access().get_trap_cx();
        // we do not have to move to next instruction since we have done it before
        // for child process, fork returns 0
        trap_cx.x[10] = 0;  //x[10] is a0 reg
        // add new task to scheduler
        add_task(new_task);
        new_pid as isize
    }

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::UserEnvCall) => {
                // jump to next instruction anyway
                let mut cx = current_trap_cx();
                cx.sepc += 4;
                // get system call return value
                let result = syscall(cx.x[17], [cx.x[10], cx.x[11], cx.x[12]]);
                // cx is changed during sys_exec, so we have to call it again
                cx = current_trap_cx();
                cx.x[10] = result as usize;
            }
        ...
    }    

在調用 ``syscall`` 進行系統調用分發並具體調用 ``sys_fork`` 之前， 第28行，``trap_handler`` 已經將當前進程 Trap 上下文中的 ``sepc`` 向後移動了 4 字節，使得它回到用戶態之後，會從發出系統調用的 ``ecall`` 指令的下一條指令開始執行。之後當我們複製地址空間的時候，子進程地址空間 Trap 上下文的 ``sepc``  也是移動之後的值，我們無需再進行修改。

父子進程回到用戶態的瞬間都處於剛剛從一次系統調用返回的狀態，但二者的返回值不同。第 8~11 行我們將子進程的 Trap 上下文中用來存放系統調用返回值的 a0 寄存器修改為 0 ；第 33 行，而父進程系統調用的返回值會在 ``trap_handler`` 中 ``syscall`` 返回之後再設置為 ``sys_fork`` 的返回值，這裡我們返回子進程的 PID 。這就做到了父進程 ``fork`` 的返回值為子進程的 PID ，而子進程的返回值則為 0 。通過返回值是否為 0 可以區分父子進程。

另外，不要忘記在第 13 行，我們將生成的子進程通過 ``add_task`` 加入到任務管理器中。

exec 系統調用的實現
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``exec`` 系統調用使得一個進程能夠加載一個新應用的 ELF 可執行文件中的代碼和數據替換原有的應用地址空間中的內容，並開始執行。我們先從進程控制塊的層面進行修改：

.. code-block:: rust
    :linenos:

    // os/src/task/task.rs

    impl TaskControlBlock {
        pub fn exec(&self, elf_data: &[u8]) {
            // memory_set with elf program headers/trampoline/trap context/user stack
            let (memory_set, user_sp, entry_point) = MemorySet::from_elf(elf_data);
            let trap_cx_ppn = memory_set
                .translate(VirtAddr::from(TRAP_CONTEXT).into())
                .unwrap()
                .ppn();

            // **** access inner exclusively
            let mut inner = self.inner_exclusive_access();
            // substitute memory_set
            inner.memory_set = memory_set;
            // update trap_cx ppn
            inner.trap_cx_ppn = trap_cx_ppn;
            // initialize trap_cx
            let trap_cx = inner.get_trap_cx();
            *trap_cx = TrapContext::app_init_context(
                entry_point,
                user_sp,
                KERNEL_SPACE.exclusive_access().token(),
                self.kernel_stack.get_top(),
                trap_handler as usize,
            );
            // **** stop exclusively accessing inner automatically
        }
    }

它在解析傳入的 ELF 格式數據之後只做了兩件事情：

- 首先是從 ELF 文件生成一個全新的地址空間並直接替換進來（第 15 行），這將導致原有的地址空間生命週期結束，裡面包含的全部物理頁幀都會被回收；
- 然後是修改新的地址空間中的 Trap 上下文，將解析得到的應用入口點、用戶棧位置以及一些內核的信息進行初始化，這樣才能正常實現 Trap 機制。

這裡無需對任務上下文進行處理，因為這個進程本身已經在執行了，而只有被暫停的應用才需要在內核棧上保留一個任務上下文。

有了 ``exec`` 函數後， ``sys_exec`` 就很容易實現了：

.. code-block:: rust
    :linenos:

    // os/src/mm/page_table.rs

    pub fn translated_str(token: usize, ptr: *const u8) -> String {
        let page_table = PageTable::from_token(token);
        let mut string = String::new();
        let mut va = ptr as usize;
        loop {
            let ch: u8 = *(page_table.translate_va(VirtAddr::from(va)).unwrap().get_mut());
            if ch == 0 {
                break;
            } else {
                string.push(ch as char);
                va += 1;
            }
        }
        string
    }

    // os/src/syscall/process.rs

    pub fn sys_exec(path: *const u8) -> isize {
        let token = current_user_token();
        let path = translated_str(token, path);
        if let Some(data) = get_app_data_by_name(path.as_str()) {
            let task = current_task().unwrap();
            task.exec(data);
            0
        } else {
            -1
        }
    }

應用在 ``sys_exec`` 系統調用中傳遞給內核的只有一個要執行的應用名字符串在當前應用地址空間中的起始地址，如果想在內核中具體獲得字符串的話就需要手動查頁表。第 3 行的 ``translated_str`` 便可以從內核地址空間之外的某個應用的用戶態地址空間中拿到一個字符串，其原理就是針對應用的字符串中字符的用戶態虛擬地址，查頁表，找到對應的內核虛擬地址，逐字節地構造字符串，直到發現一個 ``\0`` 為止（第7~15行）。

..  chyyuu 這樣找字符串，是否有安全隱患？？？

回到 ``sys_exec`` 的實現，它調用 ``translated_str`` 找到要執行的應用名並試圖在應用加載器提供的 ``get_app_data_by_name`` 接口中找到對應的 ELF 格式的數據。如果找到，就調用 ``TaskControlBlock::exec`` 替換掉地址空間並返回 0。這個返回值其實並沒有意義，因為我們在替換地址空間的時候本來就對 Trap 上下文重新進行了初始化。如果沒有找到，就不做任何事情並返回 -1。在shell程序-user_shell中我們也正是通過這個返回值來判斷要執行的應用是否存在。

系統調用後重新獲取 Trap 上下文
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

過去的 ``trap_handler`` 實現是這樣處理系統調用的：

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let cx = current_trap_cx();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::UserEnvCall) => {
                cx.sepc += 4;
                cx.x[10] = syscall(cx.x[17], [cx.x[10], cx.x[11], cx.x[12]]) as usize;
            }
            ...
        }
        trap_return();
    }

這裡的 ``cx`` 是當前應用的 Trap 上下文的可變引用，我們需要通過查頁表找到它具體被放在哪個物理頁幀上，並構造相同的虛擬地址來在內核中訪問它。對於系統調用 ``sys_exec`` 來說，一旦調用它之後，我們會發現 ``trap_handler`` 原來上下文中的 ``cx`` 失效了——因為它是用來訪問之前地址空間中 Trap 上下文被保存在的那個物理頁幀的，而現在它已經被回收掉了。因此，為了能夠處理類似的這種情況，我們在 ``syscall`` 分發函數返回之後需要重新獲取 ``cx`` ，目前的實現如下：

.. code-block:: rust
    :linenos:

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::UserEnvCall) => {
                // jump to next instruction anyway
                let mut cx = current_trap_cx();
                cx.sepc += 4;
                // get system call return value
                let result = syscall(cx.x[17], [cx.x[10], cx.x[11], cx.x[12]]);
                // cx is changed during sys_exec, so we have to call it again
                cx = current_trap_cx();
                cx.x[10] = result as usize;
            }
            ...
        }
        trap_return();
    }


shell程序 user_shell 的輸入機制
--------------------------------------------

為了實現shell程序 ``user_shell`` 的輸入機制，我們需要實現 ``sys_read`` 系統調用使得應用能夠取得用戶的鍵盤輸入。

.. code-block:: rust
    :linenos:
    
    // os/src/syscall/fs.rs

    use crate::sbi::console_getchar;

    const FD_STDIN: usize = 0;

    pub fn sys_read(fd: usize, buf: *const u8, len: usize) -> isize {
        match fd {
            FD_STDIN => {
                assert_eq!(len, 1, "Only support len = 1 in sys_read!");
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
                let mut buffers = translated_byte_buffer(current_user_token(), buf, len);
                unsafe { buffers[0].as_mut_ptr().write_volatile(ch); }
                1
            }
            _ => {
                panic!("Unsupported fd in sys_read!");
            }
        }
    }

目前我們僅支持從標準輸入 ``FD_STDIN`` 即文件描述符 0 讀入，且單次讀入的長度限制為 1，即每次只能讀入一個字符。我們調用 ``sbi`` 子模塊提供的從鍵盤獲取輸入的接口 ``console_getchar`` ，如果返回 0 則說明還沒有輸入，我們調用 ``suspend_current_and_run_next`` 暫時切換到其他進程，等下次切換回來的時候再看看是否有輸入了。獲取到輸入之後，我們退出循環並手動查頁表將輸入的字符正確的寫入到應用地址空間。

注：我們這裡還沒有涉及 **文件** 的概念，在後續章節中有具體的介紹。

進程資源回收機制
--------------------------------------------

進程的退出
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. _process-exit:

當應用調用 ``sys_exit`` 系統調用主動退出或者出錯由內核終止之後，會在內核中調用 ``exit_current_and_run_next`` 函數退出當前進程並切換到下一個進程。使用方法如下：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 4,29,34

    // os/src/syscall/process.rs

    pub fn sys_exit(exit_code: i32) -> ! {
        exit_current_and_run_next(exit_code);
        panic!("Unreachable in sys_exit!");
    }

    // os/src/trap/mod.rs

    #[no_mangle]
    pub fn trap_handler() -> ! {
        set_kernel_trap_entry();
        let scause = scause::read();
        let stval = stval::read();
        match scause.cause() {
            Trap::Exception(Exception::StoreFault) |
            Trap::Exception(Exception::StorePageFault) |
            Trap::Exception(Exception::InstructionFault) |
            Trap::Exception(Exception::InstructionPageFault) |
            Trap::Exception(Exception::LoadFault) |
            Trap::Exception(Exception::LoadPageFault) => {
                println!(
                    "[kernel] {:?} in application, bad addr = {:#x}, bad instruction = {:#x}, core dumped.",
                    scause.cause(),
                    stval,
                    current_trap_cx().sepc,
                );
                // page fault exit code
                exit_current_and_run_next(-2);
            }
            Trap::Exception(Exception::IllegalInstruction) => {
                println!("[kernel] IllegalInstruction in application, core dumped.");
                // illegal instruction exit code
                exit_current_and_run_next(-3);
            }
            ...
        }
        trap_return();
    }

相比前面的章節， ``exit_current_and_run_next`` 帶有一個退出碼作為參數。當在 ``sys_exit`` 正常退出的時候，退出碼由應用傳到內核中；而出錯退出的情況（如第 29 行的訪存錯誤或第 34 行的非法指令異常）則是由內核指定一個特定的退出碼。這個退出碼會在 ``exit_current_and_run_next`` 寫入當前進程的進程控制塊中：

.. code-block:: rust
    :linenos:

    // os/src/mm/memory_set.rs

    impl MemorySet {
        pub fn recycle_data_pages(&mut self) {
            self.areas.clear();
        }
    }

    // os/src/task/mod.rs

    pub fn exit_current_and_run_next(exit_code: i32) {
        // take from Processor
        let task = take_current_task().unwrap();
        // **** access current TCB exclusively
        let mut inner = task.inner_exclusive_access();
        // Change status to Zombie
        inner.task_status = TaskStatus::Zombie;
        // Record exit code
        inner.exit_code = exit_code;
        // do not move to its parent but under initproc

        // ++++++ access initproc TCB exclusively
        {
            let mut initproc_inner = INITPROC.inner_exclusive_access();
            for child in inner.children.iter() {
                child.inner_exclusive_access().parent = Some(Arc::downgrade(&INITPROC));
                initproc_inner.children.push(child.clone());
            }
        }
        // ++++++ stop exclusively accessing parent PCB

        inner.children.clear();
        // deallocate user space
        inner.memory_set.recycle_data_pages();
        drop(inner);
        // **** stop exclusively accessing current PCB
        // drop task manually to maintain rc correctly
        drop(task);
        // we do not have to save task context
        let mut _unused = TaskContext::zero_init();
        schedule(&mut _unused as *mut _);
    }

- 第 13 行我們調用 ``take_current_task`` 來將當前進程控制塊從處理器監控 ``PROCESSOR`` 中取出而不是得到一份拷貝，這是為了正確維護進程控制塊的引用計數；
- 第 17 行我們將進程控制塊中的狀態修改為 ``TaskStatus::Zombie`` 即殭屍進程，這樣它後續才能被父進程在 ``waitpid`` 系統調用的時候回收；
- 第 19 行我們將傳入的退出碼 ``exit_code`` 寫入進程控制塊中，後續父進程在 ``waitpid`` 的時候可以收集；
- 第 24~26 行所做的事情是將當前進程的所有子進程掛在初始進程 ``initproc`` 下面，其做法是遍歷每個子進程，修改其父進程為初始進程，並加入初始進程的孩子向量中。第 32 行將當前進程的孩子向量清空。
- 第 34 行對於當前進程佔用的資源進行早期回收。在第 4 行可以看出， ``MemorySet::recycle_data_pages`` 只是將地址空間中的邏輯段列表 ``areas`` 清空（即執行 ``Vec``  向量清空），這將導致應用地址空間被回收（即進程的數據和代碼對應的物理頁幀都被回收），但用來存放頁表的那些物理頁幀此時還不會被回收（會由父進程最後回收子進程剩餘的佔用資源）。
- 最後在第 41 行我們調用 ``schedule`` 觸發調度及任務切換，由於我們再也不會回到該進程的執行過程中，因此無需關心任務上下文的保存。

父進程回收子進程資源
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

父進程通過 ``sys_waitpid`` 系統調用來回收子進程的資源並收集它的一些信息：

.. code-block:: rust
    :linenos:
    :emphasize-lines: 15,35,37,46,47

    // os/src/syscall/process.rs

    /// If there is not a child process whose pid is same as given, return -1.
    /// Else if there is a child process but it is still running, return -2.
    pub fn sys_waitpid(pid: isize, exit_code_ptr: *mut i32) -> isize {
        let task = current_task().unwrap();
        // find a child process

        // ---- access current TCB exclusively
        let mut inner = task.inner_exclusive_access();
        if inner.children
            .iter()
            .find(|p| {pid == -1 || pid as usize == p.getpid()})
            .is_none() {
            return -1;
            // ---- stop exclusively accessing current PCB
        }
        let pair = inner.children
            .iter()
            .enumerate()
            .find(|(_, p)| {
                // ++++ temporarily access child PCB exclusively
                p.inner_exclusive_access().is_zombie() && (pid == -1 || pid as usize == p.getpid())
                // ++++ stop exclusively accessing child PCB
            });
        if let Some((idx, _)) = pair {
            let child = inner.children.remove(idx);
            // confirm that child will be deallocated after removing from children list
            assert_eq!(Arc::strong_count(&child), 1);
            let found_pid = child.getpid();
            // ++++ temporarily access child TCB exclusively
            let exit_code = child.inner_exclusive_access().exit_code;
            // ++++ stop exclusively accessing child PCB
            *translated_refmut(inner.memory_set.token(), exit_code_ptr) = exit_code;
            found_pid as isize
        } else {
            -2
        }
        // ---- stop exclusively accessing current PCB automatically
    }

    // user/src/lib.rs

    pub fn wait(exit_code: &mut i32) -> isize {
        loop {
            match sys_waitpid(-1, exit_code as *mut _) {
                -2 => { yield_(); }
                // -1 or a real pid
                exit_pid => return exit_pid,
            }
        }
    }

``sys_waitpid`` 是一個立即返回的系統調用，它的返回值語義是：如果當前的進程不存在一個進程 ID 為 pid（pid==-1 或 pid > 0）的子進程，則返回 -1；如果存在一個進程 ID 為 pid 的殭屍子進程，則正常回收並返回子進程的 pid，並更新系統調用的退出碼參數為 ``exit_code``  。這裡還有一個 -2 的返回值，它的含義是子進程還沒退出，通知用戶庫 ``user_lib`` （是實際發出系統調用的地方），這樣用戶庫看到是 -2 後，就進一步調用 ``sys_yield`` 系統調用（第46行），讓當前父進程進入等待狀態。

注：在編寫應用的開發者看來， 位於用戶庫 ``user_lib`` 中的 ``wait/waitpid`` 兩個輔助函數都必定能夠返回一個有意義的結果，要麼是 -1，要麼是一個正數 PID ，是不存在 -2 這種通過等待即可消除的中間結果的。讓調用 ``wait/waitpid`` 兩個輔助函數的進程等待正是在用戶庫 ``user_lib`` 中完成。

第 11~17 行判斷 ``sys_waitpid`` 是否會返回 -1 ，這取決於當前進程是否有一個符合要求的子進程。當傳入的 ``pid`` 為 -1 的時候，任何一個子進程都算是符合要求；但 ``pid`` 不為 -1 的時候，則只有 PID 恰好與 ``pid`` 相同的子進程才算符合條件。我們簡單通過迭代器即可完成判斷。

第 18~26 行判斷符合要求的子進程中是否有殭屍進程，如果有的話還需要同時找出它在當前進程控制塊子進程向量中的下標。如果找不到的話直接返回 ``-2`` ，否則進入第 27~35 行的處理：

- 第 27 行我們將子進程從向量中移除並置於當前上下文中；
- 第 29 行確認這是對於該子進程控制塊的唯一一次強引用，即它不會出現在某個進程的子進程向量中，更不會出現在處理器監控器或者任務管理器中。當它所在的代碼塊結束，這次引用變量的生命週期結束，將導致該子進程進程控制塊的引用計數變為 0 ，徹底回收掉它佔用的所有資源，包括：內核棧和它的 PID 還有它的應用地址空間存放頁表的那些物理頁幀等等。

剩下主要是將收集的子進程信息返回。

- 第 30 行得到子進程的 PID 並會在最終返回；
- 第 32 行得到了子進程的退出碼；
- 第 34 行寫入到當前進程的應用地址空間中。由於應用傳遞給內核的僅僅是一個指向應用地址空間中保存子進程返回值的內存區域的指針，我們還需要在 ``translated_refmut`` 中手動查頁表找到應該寫入到物理內存中的哪個位置，這樣才能把子進程的退出碼 ``exit_code`` 返回給父進程。其實現可以在 ``os/src/mm/page_table.rs`` 中找到，比較簡單，在這裡不再贅述。


到這裡，“傷齒龍”操作系統就算完成了。它在啟動後，會加載執行用戶態的shell程序，並可以通過shell程序提供的命令行交互界面，讓使用者敲入要執行的應用程序名字，就可以創建一個子進程來執行這個應用程序，實現了靈活的人機交互和進程管理的動態靈活性。

.. chyyuu 可以加入一節，描述os的執行過程？？？