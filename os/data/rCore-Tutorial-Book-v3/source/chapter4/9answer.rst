練習參考答案
============================================

課後練習
-------------------------------

編程題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1. `**` 使用sbrk，mmap,munmap,mprotect內存相關係統調用的linux應用程序。

   可以編寫使用sbrk系統調用的應用程序，具體代碼如下：

.. code-block:: c

   //user/src/ch4_sbrk.c
   int main()
   {
            printf("Test sbrk start.\n");
            uint64 PAGE_SIZE = 0x1000;
            uint64 origin_brk = sbrk(0);
            printf("origin break point = %p\n", origin_brk);
            uint64 brk = sbrk(PAGE_SIZE);
            if(brk != origin_brk){
                    return -1;
            }
            brk = sbrk(0);
            printf("one page allocated, break point = %p\n", brk);
            printf("try write to allocated page\n");
            char *new_page = (char *)origin_brk;
            for(uint64 i = 0;i < PAGE_SIZE;i ++) {
                    new_page[i] = 1;
            }
            printf("write ok\n");
            sbrk(PAGE_SIZE * 10);
            brk = sbrk(0);
            printf("10 page allocated, break point = %p\n", brk);
            sbrk(PAGE_SIZE * -11);
            brk = sbrk(0);
            printf("11 page DEALLOCATED, break point = %p\n", brk);
            printf("try DEALLOCATED more one page, should be failed.\n");
            uint64 ret = sbrk(PAGE_SIZE * -1);
            if(ret != -1){
                    printf("Test sbrk failed!\n");
                    return -1;
            }
            printf("Test sbrk almost OK!\n");
            printf("now write to deallocated page, should cause page fault.\n");
            for(uint64 i = 0;i < PAGE_SIZE;i ++){
                    new_page[i] = 2;
            }
            return 0;
    }

使用mmap、unmap系統調用的應用代碼可參考測例中的ch4_mmap0.c、ch4_unmap0.c等代碼。

2. `***` 修改本章操作系統內核，實現任務和操作系統內核共用同一張頁表的單頁表機制。

   要實現任務和操作系統內核通用一張頁表，需要了解清楚內核地址空間和任務地址空間的佈局，然後為每個任務在內核地址空間中單獨分配一定的地址空間。

   在描述任務的struct proc中添加新的成員“kpgtbl”、“trapframe_base”，前者用戶保存內核頁表，後者用於保存任務的TRAPFRAME虛地址。並增加獲取內核頁表的函數“get_kernel_pagetable()”。

.. code-block:: c

   //os/proc.h
   struct proc {
        enum procstate state; // Process state
        int pid; // Process ID
        pagetable_t pagetable; // User page table
        uint64 ustack;
        uint64 kstack; // Virtual address of kernel stack
        struct trapframe *trapframe; // data page for trampoline.S
        struct context context; // swtch() here to run process
        uint64 max_page;
        uint64 program_brk;
        uint64 heap_bottom;
        pagetable_t kpgtbl; // 增加kpgtbl，用於保存內核頁表
        uint64 trapframe_base; // 增加trapframe，用於保存任務自己的trapframe
   }
   //os/vm.c
   //增加get_kernel_pagetable函數，返回內核頁表
   pagetable_t get_kernel_pagetable(){
        return kernel_pagetable;
   }

讓任務使用內核頁表，在內核地址空間中為每個任務分配一定的地址空間，在bin_loader()函數中修改任務的內存佈局。

.. code-block:: c

   //os/loader.c
   //修改任務的地址空間
   pagetable_t bin_loader(uint64 start, uint64 end, struct proc *p, int num)
   {
        //pagetable_t pg = uvmcreate(); //任務不創建自己的頁表
        pagetable_t pg = get_kernel_pagetable(); //獲取內核頁表
        uint64 trapframe = TRAPFRAME - (num + 1)* PAGE_SIZE; // 為每個任務依次指定TRAPFRAME
        if (mappages(pg, trapframe, PGSIZE, (uint64)p->trapframe,
                     PTE_R | PTE_W) < 0) {
                panic("mappages fail");
        }
        if (!PGALIGNED(start)) {
                panic("user program not aligned, start = %p", start);
        }
        if (!PGALIGNED(end)) {
                // Fix in ch5
                warnf("Some kernel data maybe mapped to user, start = %p, end = %p",
                      start, end);
        }
        end = PGROUNDUP(end);
        uint64 length = end - start;
        uint64 base_address = BASE_ADDRESS + (num * (p->max_page + 100)) * PAGE_SIZE; //設置任務的起始地址，併為任務保留100個頁用做堆內存
        if (mappages(pg, base_address, length, start,
                     PTE_U | PTE_R | PTE_W | PTE_X) != 0) {
                panic("mappages fail");
        }
        p->pagetable = pg;
        uint64 ustack_bottom_vaddr = base_address + length + PAGE_SIZE;
        if (USTACK_SIZE != PAGE_SIZE) {
                // Fix in ch5
                panic("Unsupported");
        }
        mappages(pg, ustack_bottom_vaddr, USTACK_SIZE, (uint64)kalloc(),
                 PTE_U | PTE_R | PTE_W | PTE_X);
        p->ustack = ustack_bottom_vaddr;
        p->trapframe->epc = base_address;
        p->trapframe->sp = p->ustack + USTACK_SIZE;
        p->max_page = PGROUNDUP(p->ustack + USTACK_SIZE - 1) / PAGE_SIZE;
        p->program_brk = p->ustack + USTACK_SIZE;
        p->heap_bottom = p->ustack + USTACK_SIZE;
        p->trapframe_base = trapframe; //任務保存自己的TRAPFRAME
        return pg;
   }
   
在內核返回任務中使用任務自己的TRAPFRAME。

.. code-block:: c

   //os/trap.c
   void usertrapret()
   {
        set_usertrap();
        struct trapframe *trapframe = curr_proc()->trapframe;
        trapframe->kernel_satp = r_satp(); // kernel page table
        trapframe->kernel_sp =
                curr_proc()->kstack + KSTACK_SIZE; // process's kernel stack
        trapframe->kernel_trap = (uint64)usertrap;
        trapframe->kernel_hartid = r_tp(); // unuesd
        w_sepc(trapframe->epc);
        // set up the registers that trampoline.S's sret will use
        // to get to user space.
        // set S Previous Privilege mode to User.
        uint64 x = r_sstatus();
        x &= ~SSTATUS_SPP; // clear SPP to 0 for user mode
        x |= SSTATUS_SPIE; // enable interrupts in user mode
        w_sstatus(x);
        // tell trampoline.S the user page table to switch to.
        uint64 satp = MAKE_SATP(curr_proc()->pagetable);
        uint64 fn = TRAMPOLINE + (userret - trampoline);
        tracef("return to user @ %p", trapframe->epc);
        ((void (*)(uint64, uint64))fn)(curr_proc()->trapframe_base, satp); //使用任務自己的TRAPFRAME
        //((void (*)(uint64, uint64))fn)(TRAPFRAME, satp);
   }

3. `***` 擴展內核，支持基於缺頁異常機制，具有Lazy 策略的按需分頁機制。


   在頁面懶分配（Lazy allocation of pages）技術中，內存分配並不會立即發生，而是在需要使用內存時才分配，這樣可以節省系統的資源並提高程序的性能。

   實現頁面懶分配的思路是：當調用sbrk時不分配實際的頁面，而是僅僅增大堆的大小，當實際訪問頁面時，就會觸發缺頁異常，此時再申請一個頁面並映射到頁表中，這時再次執行觸發缺頁異常的代碼就可以正常讀寫內存了。

   註釋掉growproc()函數，增加堆的size，但不實際分配內存：

.. code-block:: c

   //os/syscall.c
   uint64 sys_sbrk(int n)
   {
        uint64 addr;
        struct proc *p = curr_proc();
        addr = p->program_brk;
        int heap_size = addr + n - p->heap_bottom; 
        if(heap_size < 0){
                errorf("out of heap_bottom\n");
                return -1;
        }
        else{
                p->program_brk += n; //增加堆的size，但不實際分配內存
                if(n < 0){
                        printf("uvmdealloc\n");
                        uvmdealloc(p->pagetable, addr, addr + n); //如果減少內存則調用內存釋放函數
                }
        }
        //if(growproc(n) < 0) //註釋掉growproc()函數，不實際分配內存
        //        return -1;
        return addr;
   }

因為沒有給虛擬地址實際分配內存，所以當對相應的虛擬地址的內存進行讀寫的時候會觸發缺頁錯誤，這時再實際分配內存：

.. code-block:: c

   //os/loader.c
   void usertrap()
   {
        set_kerneltrap();
        struct trapframe *trapframe = curr_proc()->trapframe;
        tracef("trap from user epc = %p", trapframe->epc);
        if ((r_sstatus() & SSTATUS_SPP) != 0)
                panic("usertrap: not from user mode");
        uint64 cause = r_scause();
        if (cause & (1ULL << 63)) {
                cause &= ~(1ULL << 63);
                switch (cause) {
                case SupervisorTimer:
                        tracef("time interrupt!");
                        set_next_timer();
                        yield();
                        break;
                default:
                        unknown_trap();
                        break;
                }
        } else {
                switch (cause) {
                case UserEnvCall:
                        trapframe->epc += 4;
                        syscall();
                        break;
                case StorePageFault: // 讀缺頁錯誤
                case LoadPageFault:  // 寫缺頁錯誤
                        {
                                uint64 addr = r_stval(); // 獲取發生缺頁錯誤的地址
                                if(lazy_alloc(addr) < 0){ // 調用頁面懶分配函數
                                        errorf("lazy_aolloc() failed!\n");
                                        exit(-2);
                                }
                                break;
                        }
                case StoreMisaligned:
                case InstructionMisaligned:
                case InstructionPageFault:
                case LoadMisaligned:
                        errorf("%d in application, bad addr = %p, bad instruction = %p, "
                               "core dumped.",
                               cause, r_stval(), trapframe->epc);
                        exit(-2);
                        break;
                case IllegalInstruction:
                        errorf("IllegalInstruction in application, core dumped.");
                        exit(-3);
                        break;
                default:
                        unknown_trap();
                        break;
                }
        }
        usertrapret();
   }
   
實現頁面懶分配函數，首先判斷地址是否在堆的範圍內，然後分配實際的內存，最後在頁面中建立映射：

.. code-block:: c

   //os/trap.c
   int lazy_alloc(uint64 addr){
        struct proc *p = curr_proc();
        // 通過兩個if判斷髮生缺頁錯誤的地址是否在堆的範圍內，不在則返回
        if (addr >= p->program_brk) { 
                errorf("lazy_alloc: access invalid address");
                return -1;
        }
        if (addr < p->heap_bottom) {
                errorf("lazy_alloc: access address below stack");
                return -2;
        }
        uint64 va = PGROUNDDOWN(addr);
        char* mem = kalloc(); // 調用kalloc()實際分配頁面
        if (mem == 0) {
                errorf("lazy_alloc: kalloc failed");
                return -3;
        }
        memset(mem, 0, PGSIZE);
        if(mappages(p->pagetable, va, PGSIZE, (uint64)mem, PTE_W|PTE_X|PTE_R|PTE_U) != 0){ // 將新分配的頁面和虛擬地址在頁表中建立映射
                kfree(mem);
                return -4;
        }
        return 0;
   }

4. `***` 擴展內核，支持基於缺頁異常的COW機制。（初始時，兩個任務共享一個只讀物理頁。當一個任務執行寫操作後，兩個任務擁有各自的可寫物理頁）

   COW（Copy on Write）是指當需要在內存中創建一個新的副本時，COW技術會推遲複製操作，直到數據被修改為止。從而減少不必要的內存拷貝，提升性能。

   實現COW的思路是：在創建內存副本時，在內存中創建一個指向原始數據的指針或引用，而不是創建原始數據的完整副本。如果原始數據沒有被修改，新副本將繼續共享原始數據的指針或引用，以節省內存。當某個程序試圖修改數據時，COW技術會在新副本中複製原始數據，使得每個程序都有自己的獨立副本，從而避免數據之間的干擾。

   增加一個當做計數器的數據結構用於記錄每個物理頁面被多少變量引用，當頁面初始被分配時計數器設置為1，其後如果產生副本則計數器加1。當頁面被釋放的時候則計數器減1，如果計數器不為0，說明還有其他引用在使用該頁面，此時不執行實際的釋放操作，最後計數器變為0時才真正釋放頁面：

.. code-block:: c

   //os/kalloc.c
   uint64 page_ref[ (PHYSTOP - KERNBASE)/PAGE_SIZE] = {0}; // 定義用來記錄頁面引用的計數器，並將其值初始化為0
   // 新增修改頁面計數器的函數
   void page_ref_add(uint64 pa, int n){ // 增加頁面計數
        page_ref[(PGROUNDDOWN(pa)-KERNBASE)/PGSIZE] += n;
   }
   void page_ref_reduce(uint64 pa, int n){ // 減少頁面計數
        page_ref[(PGROUNDDOWN(pa)-KERNBASE)/PGSIZE] -= n;
   }
   uint64 page_ref_get(uint64 pa){ // 返回頁面計數
        return page_ref[(PGROUNDDOWN(pa)-KERNBASE)/PGSIZE];
   }
   void *kalloc()
   {
        struct linklist *l;
        l = kmem.freelist;
        if (l) {
                kmem.freelist = l->next;
                memset((char *)l, 5, PGSIZE); // fill with junk
                page_ref_add((uint64)l, 1); // 在頁面分配的時候設置計數器為1
        }
        return (void *)l;
   }
   void kfree(void *pa)
   {
        struct linklist *l;
        if (((uint64)pa % PGSIZE) != 0 || (char *)pa < ekernel ||
            (uint64)pa >= PHYSTOP)
                panic("kfree");
        if(page_ref_get((uint64)pa) > 1){ // 判斷計數器的值，如果大於1說明還有其他引用，計數器減1後直接返回
                page_ref_reduce((uint64)pa, 1);
                return;
        }
        // Fill with junk to catch dangling refs.
        memset(pa, 1, PGSIZE);
        l = (struct linklist *)pa;
        l->next = kmem.freelist;
        kmem.freelist = l;
   }

修改內存複製函數umcopy()，其實不進行實際的內存複製，只是增加新的引用到需要複製的內存上：

.. code-block:: c

   //os/vm.c
   int uvmcopy(pagetable_t old, pagetable_t new, uint64 max_page)
  {
        pte_t *pte;
        uint64 pa, i;
        uint flags;
        //char *mem;
        for (i = 0; i < max_page * PAGE_SIZE; i += PGSIZE) {
                if ((pte = walk(old, i, 0)) == 0)
                        continue;
                if ((*pte & PTE_V) == 0)
                        continue;
                pa = PTE2PA(*pte);
                flags = PTE_FLAGS(*pte);
                *pte = ((*pte) & (~PTE_W)) | PTE_COW; // 雖然不進行內存頁的複製，但是需要修改內存頁的操作權限，取消頁的寫操作權限，同時增加COW權限
                /*if ((mem = kalloc()) == 0) // 註釋掉分配內存的函數
                        goto err;
                memmove(mem, (char *)pa, PGSIZE);
                if (mappages(new, i, PGSIZE, (uint64)mem, flags) != 0) {*/
                if (mappages(new, i, PGSIZE, (uint64)pa, (flags & (~PTE_W)) | PTE_COW) != 0) { // 讓另一頁表中的虛擬地址指向原來頁表中的物理地址
                        //kfree(mem);
                        goto err;
                }
                page_ref_add(pa, 1);
        }
        return 0;
   err:
        uvmunmap(new, 0, i / PGSIZE, 1);
        return -1;
   }

因為沒有實際地進行內存複製，且取消了頁面的的寫權限，所以當對相應的虛擬地址的內存進行寫操作的時候會觸發缺頁錯誤，這時再調用cowcopy()函數實際分配頁或修改頁的寫權限：

.. code-block:: c

   //os/trap.c
   void usertrap()
   {
        set_kerneltrap();
        struct trapframe *trapframe = curr_proc()->trapframe;
        tracef("trap from user epc = %p", trapframe->epc);
        if ((r_sstatus() & SSTATUS_SPP) != 0)
                panic("usertrap: not from user mode");
        uint64 cause = r_scause();
        if (cause & (1ULL << 63)) {
                cause &= ~(1ULL << 63);
                switch (cause) {
                case SupervisorTimer:
                        tracef("time interrupt!");
                        set_next_timer();
                        yield();
                        break;
                default:
                        unknown_trap();
                        break;
                }
        } else {
                switch (cause) {
                case UserEnvCall:
                        trapframe->epc += 4;
                        syscall();
                        break;
                case StorePageFault:{ // 寫缺頁錯誤
                        uint64 va = r_stval(); //獲取發生缺頁錯誤的虛擬地址
                        if(cowcopy(va) == -1){ // 當發生寫缺頁錯誤的時候，調用COW函數，進行實際的內存複製
                                errorf("Copy on Write Failed!\n");
                                exit(-2);
                        }
                        break;
                }
                case StoreMisaligned:
                case InstructionMisaligned:
                case InstructionPageFault:
                case LoadMisaligned:
                case LoadPageFault:
                        errorf("%d in application, bad addr = %p, bad instruction = %p, "
                               "core dumped.",
                               cause, r_stval(), trapframe->epc);
                        exit(-2);
                        break;
                case IllegalInstruction:
                        errorf("IllegalInstruction in application, core dumped.");
                        exit(-3);
                        break;
                default:
                        unknown_trap();
                        break;
                }
        }
        usertrapret();
   }
   
實現cowcopy()分配函數，首先判斷地址是否在堆的範圍內，然後分配實際的內存，最後在頁面中建立映射：

.. code-block:: c

   //os/vm.c
   int cowcopy(uint64 va){
        va = PGROUNDDOWN(va);
        pagetable_t p = curr_proc()->pagetable;
        pte_t* pte = walk(p, va, 0);
        uint64 pa = PTE2PA(*pte);
        uint flags = PTE_FLAGS(*pte); // 獲取頁面的操作權限
        if(!(flags & PTE_COW)){
                printf("not cow\n");
                return -2; // not cow page
        }
        uint ref = page_ref_get(pa); // 獲取頁面的被引用的次數
        if(ref > 1){ // 若果大於1則說明有多個引用，這時需要重新分配頁面
                // ref > 1, alloc a new page
                char* mem = kalloc();
                if(mem == 0){
                        errorf("kalloc failed!\n");
                        return -1;
                }
                memmove(mem, (char*)pa, PGSIZE); // 複製頁中的內容到新的頁
                if(mappages(p, va, PGSIZE, (uint64)mem, (flags & (~PTE_COW)) | PTE_W) != 0){
                        errorf("mappage failed!\n");
                        kfree(mem);
                        return -1;
                }
                page_ref_reduce(pa, 1);
        }else{
                // ref = 1, use this page directly
                *pte = ((*pte) & (~PTE_COW)) | PTE_W; // 如果沒有其他引用則修改頁面操作權限，使得該頁面可以進行寫操作
        }
        return 0;
   }

5. `***` 擴展內核，實現swap in/out機制，並實現Clock置換算法或二次機會置換算法。
6. `***` 擴展內核，實現自映射機制。

問答題
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. chyyuu   這次的實驗沒有涉及到缺頁有點遺憾，主要是缺頁難以測試，而且更多的是一種優化，不符合這次實驗的核心理念，所以這裡補兩道小題。

1. `*` 在使用高級語言編寫用戶程序的時候，手動用嵌入彙編的方法隨機訪問一個不在當前程序邏輯地址範圍內的地址，比如向該地址讀/寫數據。該用戶程序執行的時候可能會生什麼？ 

   可能會報出缺頁異常.

2. `*` 用戶程序在運行的過程中，看到的地址是邏輯地址還是物理地址？從用戶程序訪問某一個地址，到實際內存中的對應單元被讀/寫，會經過什麼樣的過程，這個過程中操作系統有什麼作用？（站在學過計算機組成原理的角度）

   邏輯地址。這個過程需要經過頁表的轉換，操作系統會負責建立頁表映射。實際程序執行時的具體VA到PA的轉換是在CPU的MMU之中進行的。

3. `*` 覆蓋、交換和虛擬存儲有何異同，虛擬存儲的優勢和挑戰體現在什麼地方？

   它們都是採取層次存儲的思路，將暫時不用的內存放到外存中去，以此來緩解內存不足的問題。

   不同之處：覆蓋是程序級的，需要程序員自行處理。交換則不同，由OS控制交換程序段。虛擬內存也由OS和CPU來負責處理，可以實現內存交換到外存的過程。
   
   虛擬存儲的優勢:1.與段/頁式存儲完美契合，方便非連續內存分配。2.粒度合適，比較靈活。兼顧了覆蓋和交換的好處：可以在較小粒度上置換；自動化程度高，編程簡單，受程序本身影響很小。（覆蓋的粒度受限於程序模塊的大小，對編程技巧要求很高。交換粒度較大，受限於程序所需內存。尤其頁式虛擬存儲，幾乎不受程序影響，一般情況下，只要置換算法合適，表現穩定、高效）3.頁式虛擬存儲還可以同時消除內存外碎片並將內碎片限制在一個頁面大小以內，提高空間利用率。
   
   虛擬存儲的挑戰: 1.依賴於置換算法的性能。2.相比於覆蓋和交換，需要比較高的硬件支持。3.較小的粒度在面臨大規模的置換時會發生多次較小規模置換，降低效率。典型情況是程序第一次執行時的大量page fault，可配合預取技術緩解這一問題。

4. `*` 什麼是局部性原理？為何很多程序具有局部性？局部性原理總是正確的嗎？為何局部性原理為虛擬存儲提供了性能的理論保證？

   局部性分時間局部性和空間局部性（以及分支局部性）。局部性的原理是程序經常對一塊相近的地址進行訪問或者是對一個範圍內的指令進行操作。局部性原理不一定是一直正確的。虛擬存儲以頁為單位，局部性使得數據和指令的訪存侷限在幾頁之中，可以避免頁的頻繁換入換出的開銷，同時也符合TLB和cache的工作機制。

5. `**` 一條load指令，最多導致多少次頁訪問異常？嘗試考慮較多情況。

   考慮多級頁表的情況。首先指令和數據讀取都可能缺頁。因此指令會有3次訪存，之後的數據讀取除了頁表頁缺失的3次訪存外，最後一次還可以出現地址不對齊的異常，因此可以有7次異常。若考更加極端的情況，也就是頁表的每一級都是不對齊的地址並且處在兩頁的交界處（straddle），此時一次訪存會觸發2次讀取頁面，如果這兩頁都缺頁的話，會有更多的異常次數。

6. `**` 如果在頁訪問異常中斷服務例程執行時，再次出現頁訪問異常，這時計算機系統（軟件或硬件）會如何處理？這種情況可能出現嗎？

   我們實驗的os在此時不支持內核的異常中斷，因此此時會直接panic掉，並且這種情況在我們的os中這種情況不可能出現。像linux系統，也不會出現嵌套的page fault。

7. `*` 全局和局部置換算法有何不同？分別有哪些算法？

   全局頁面置換算法：可動態調整某任務擁有的物理內存大小；影響其他任務擁有的物理內存大小。例如：工作集置換算法，缺頁率置換算法。

   局部頁面置換算法：每個任務分配固定大小的物理頁，不會動態調整任務擁有的物理頁數量；只考慮單個任務的內存訪問情況，不影響其他任務擁有的物理內存。例如：最優置換算法、FIFO置換算法、LRU置換算法、Clock置換算法。

8. `*` 簡單描述OPT、FIFO、LRU、Clock、LFU的工作過程和特點 (不用寫太多字，簡明扼要即可)

   OPT：選擇一個應用程序在隨後最長時間內不會被訪問的虛擬頁進行換出。性能最佳但無法實現。
   
   FIFO：由操作系統維護一個所有當前在內存中的虛擬頁的鏈表，從交換區最新換入的虛擬頁放在表尾，最久換入的虛擬頁放在表頭。當發生缺頁中斷時，淘汰/換出表頭的虛擬頁並把從交換區新換入的虛擬頁加到表尾。實現簡單，對頁訪問的局部性感知不夠。
   
   LRU：替換的是最近最少使用的虛擬頁。實現相對複雜，但考慮了訪存的局部性，效果接近最優置換算法。
   
   Clock：將所有有效頁放在一個環形循環列表中，指針根據頁表項的使用位（0或1）尋找被替換的頁面。考慮歷史訪問，性能略差於但接近LRU。
   
   LFU：當發生缺頁中斷時，替換訪問次數最少的頁面。只考慮訪問頻率，不考慮程序動態運行。

9.  `**` 綜合考慮置換算法的收益和開銷，綜合評判在哪種程序執行環境下使用何種算法比較合適？

   FIFO算法：在內存較小的系統中，FIFO 算法可能是一個不錯的選擇，因為它的實現簡單，開銷較小，但是會存在 Belady 異常。
   
   LRU算法：在內存容量較大、應用程序具有較強的局部性時，LRU 算法可能是更好的選擇，因為它可以充分利用頁面的訪問局部性，且具有較好的性能。

   Clock算法：當應用程序中存在一些特殊的內存訪問模式時，例如存在循環引用或者訪問模式具有周期性時，Clock 算法可能會比較適用，因為它能夠處理頁面的訪問頻率。

   LFU算法：對於一些需要對內存訪問進行優先級調度的應用程序，例如多媒體應用程序，LFU 算法可能是更好的選擇，因為它可以充分考慮頁面的訪問頻率，對重要性較高的頁面進行保護，但是實現比較複雜。

10. `**` Clock算法僅僅能夠記錄近期是否訪問過這一信息，對於訪問的頻度幾乎沒有記錄，如何改進這一點？

   如果想要改進這一點，可以將Clock算法和計數器結合使用。具體做法是為每個頁面設置一個計數器，記錄頁面在一段時間內的訪問次數，然後在置換頁面時，既考慮頁面最近的訪問時間，也考慮其訪問頻度。當待緩存對象在緩存中時，把其計數器的值加1。同時，指針指向該對象的下一個對象。若不在緩存中時，檢查指針指向對象的計數器。如果是0，則用待緩存對象替換該對象；否則，把計數器的值減1，指針指向下一個對象。如此直到淘汰一個對象為止。由於計數器的值允許大於1，所以指針可能循環多遍才淘汰一個對象。

11. `***` 哪些算法有belady現象？思考belady現象的成因，嘗試給出說明OPT和LRU等為何沒有belady現象。

   FIFO算法、Clock算法。

   頁面調度算法可分為堆棧式和非堆棧式，LRU、LFU、OPT均為堆棧類算法，FIFO、Clock為非堆棧類算法，只有非堆棧類才會出現Belady現象。

12. `*` 什麼是工作集？什麼是常駐集？簡單描述工作集算法的工作過程。

   工作集為一個進程當前正在使用的邏輯頁面集合，可表示為二元函數$W(t, \Delta)$，t 為執行時刻，$\Delta$ 稱為工作集窗口，即一個定長的頁面訪問時間窗口，$W(t, \Delta)$是指在當前時刻 t 前的 $\Delta$ 時間窗口中的所有訪問頁面所組成的集合，$|W(t, \Delta)|$為工作集的大小，即頁面數目。

13. `*` 請列舉 SV39 頁`*` 頁表項的組成，結合課堂內容，描述其中的標誌位有何作用／潛在作用？

   [63:54]為保留項，[53:10]為44位物理頁號，最低的8位[7:0]為標誌位。

   - V(Valid)：僅當位 V 為 1 時，頁表項才是合法的；
   - R(Read)/W(Write)/X(eXecute)：分別控制索引到這個頁表項的對應虛擬頁面是否允許讀/寫/執行；
   - U(User)：控制索引到這個頁表項的對應虛擬頁面是否在 CPU 處於 U 特權級的情況下是否被允許訪問；
   - A(Accessed)：處理器記錄自從頁表項上的這一位被清零之後，頁表項的對應虛擬頁面是否被訪問過；
   - D(Dirty)：處理器記錄自從頁表項上的這一位被清零之後，頁表項的對應虛擬頁面是否被修改過。

14. `**` 請問一個任務處理 10G 連續的內存頁面，需要操作的頁表實際大致佔用多少內存(給出數量級即可)？

大致佔用`10G/512=20M`內存。

15. `**`  缺頁指的是進程訪問頁面時頁面不在頁表中或在頁表中無效的現象，此時 MMU 將會返回一箇中斷，告知操作系統：該進程內存訪問出了問題。然後操作系統可選擇填補頁表並重新執行異常指令或者殺死進程。操作系統基於缺頁異常進行優化的兩個常見策略中，其一是 Lazy 策略，也就是直到內存頁面被訪問才實際進行頁表操作。比如，一個程序被執行時，進程的代碼段理論上需要從磁盤加載到內存。但是 操作系統並不會馬上這樣做，而是會保存 .text 段在磁盤的位置信息，在這些代碼第一次被執行時才完成從磁盤的加載操作。 另一個常見策略是 swap 頁置換策略，也就是內存頁面可能被換到磁盤上了，導致對應頁面失效，操作系統在任務訪問到該頁產生異常時，再把數據從磁盤加載到內存。

    1. 哪些異常可能是缺頁導致的？發生缺頁時，描述與缺頁相關的CSR寄存器的值及其含義。
  
    - 答案： `mcause` 寄存器中會保存發生中斷異常的原因，其中 `Exception Code` 為 `12` 時發生指令缺頁異常，為 `15` 時發生 `store/AMO` 缺頁異常，為 `13` 時發生 `load` 缺頁異常。

    CSR寄存器: 
        
       - `scause`: 中斷/異常發生時， `CSR` 寄存器 `scause` 中會記錄其信息， `Interrupt` 位記錄是中斷還是異常， `Exception Code` 記錄中斷/異常的種類。
       - `sstatus`: 記錄處理器當前狀態，其中 `SPP` 段記錄當前特權等級。
       - `stvec`: 記錄處理 `trap` 的入口地址，現有兩種模式 `Direct` 和 `Vectored` 。
       - `sscratch`: 其中的值是指向hart相關的S態上下文的指針，比如內核棧的指針。
       - `sepc`: `trap` 發生時會將當前指令的下一條指令地址寫入其中，用於 `trap` 處理完成後返回。
       - `stval`: `trap` 發生進入S態時會將異常信息寫入，用於幫助處理 `trap` ，其中會保存導致缺頁異常的虛擬地址。
 
    2. Lazy 策略有哪些好處？請描述大致如何實現Lazy策略？

    - 答案：Lazy策略一定不會比直接加載策略慢，並且可能會提升性能，因為可能會有些頁面被加載後並沒有進行訪問就被釋放或替代了，這樣可以避免很多無用的加載。分配內存時暫時不進行分配，只是將記錄下來，訪問缺頁時會觸發缺頁異常，在`trap handler`中處理相應的異常，在此時將內存加載或分配即可。
  
    3. swap 頁置換策略有哪些好處？此時頁面失效如何表現在頁表項(PTE)上？請描述大致如何實現swap策略？

    - 答案：可以為用戶程序提供比實際物理內存更大的內存空間。頁面失效會將標誌位`V`置為`0`。將置換出的物理頁面保存在磁盤中，在之後訪問再次觸發缺頁異常時將該頁面寫入內存。
  
16. `**` 為了防範側信道攻擊，本章的操作系統使用了雙頁表。但是傳統的操作系統設計一般採用單頁表，也就是說，任務和操作系統內核共用同一張頁表，只不過內核對應的地址只允許在內核態訪問。(備註：這裡的單/雙的說法僅為自創的通俗說法，並無這個名詞概念，詳情見 `KPTI <https://en.wikipedia.org/wiki/Kernel_page-table_isolation>`_ )

    1. 單頁表情況下，如何控制用戶態無法訪問內核頁面？
  
    - 答案：將內核頁面的 pte 的`U`標誌位設置為0。
 
    2. 相對於雙頁表，單頁表有何優勢？
 
    - 答案：在內核和用戶態之間轉換時不需要更換頁表，也就不需要跳板，可以像之前一樣直接切換上下文。
 
    3. 請描述：在單頁表和雙頁表模式下，分別在哪個時機，如何切換頁表？
 
    - 答案：雙頁表實現下用戶程序和內核轉換時、用戶程序轉換時都需要更換頁表，而對於單頁表操作系統，不同用戶線程切換時需要更換頁表。

實驗練習
-------------------------------

實驗練習包括實踐作業和問答作業兩部分。

實踐作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

重寫 sys_get_time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

引入虛存機制後，原來內核的 sys_get_time 函數實現就無效了。請你重寫這個函數，恢復其正常功能。

mmap 和 munmap 匿名映射
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`mmap <https://man7.org/linux/man-pages/man2/mmap.2.html>`_ 在 Linux 中主要用於在內存中映射文件，本次實驗簡化它的功能，僅用於申請內存。

請實現 mmap 和 munmap 系統調用，mmap 定義如下：


.. code-block:: rust

    fn sys_mmap(start: usize, len: usize, prot: usize) -> isize

- syscall ID：222
- 申請長度為 len 字節的物理內存（不要求實際物理內存位置，可以隨便找一塊），將其映射到 start 開始的虛存，內存頁屬性為 prot
- 參數：
    - start 需要映射的虛存起始地址，要求按頁對齊
    - len 映射字節長度，可以為 0
    - prot：第 0 位表示是否可讀，第 1 位表示是否可寫，第 2 位表示是否可執行。其他位無效且必須為 0
- 返回值：執行成功則返回 0，錯誤返回 -1
- 說明：
    - 為了簡單，目標虛存區間要求按頁對齊，len 可直接按頁向上取整，不考慮分配失敗時的頁回收。
- 可能的錯誤：
    - start 沒有按頁大小對齊
    - prot & !0x7 != 0 (prot 其餘位必須為0)
    - prot & 0x7 = 0 (這樣的內存無意義)
    - [start, start + len) 中存在已經被映射的頁
    - 物理內存不足

munmap 定義如下：

.. code-block:: rust

    fn sys_munmap(start: usize, len: usize) -> isize

- syscall ID：215
- 取消到 [start, start + len) 虛存的映射
- 參數和返回值請參考 mmap
- 說明：
    - 為了簡單，參數錯誤時不考慮內存的恢復和回收。
- 可能的錯誤：
    - [start, start + len) 中存在未被映射的虛存。


TIPS：注意 prot 參數的語義，它與內核定義的 MapPermission 有明顯不同！

實驗要求
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- 實現分支：ch4-lab
- 實驗目錄要求不變
- 通過所有測例

  在 os 目錄下 ``make run TEST=1`` 測試 sys_get_time， ``make run TEST=2`` 測試 map 和 unmap。

challenge: 支持多核。

問答作業
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

無

實驗練習的提交報告要求
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* 簡單總結本次實驗與上個實驗相比你增加的東西。（控制在5行以內，不要貼代碼）
* 完成問答問題。
* (optional) 你對本次實驗設計及難度的看法。
   
