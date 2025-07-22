# Lab2

> 思考題 1：請思考多級頁表相比單級頁錶帶來的優勢和劣勢（如果有的話），並計算在 AArch64 頁表中分別以 4KB 粒度和 2MB 粒度映射 0～4GB 地址範圍所需的物理內存大小（或頁表頁數量）。

- 多級頁表的優勢：更加節省內存，不需要為一些未被分配的內存分配內存頁
- 多級頁表的劣勢：相比於單級頁表，查詢頁的地址時多了幾次內存查詢，性能開銷較高
- 4KB粒度映射：4GB / (4KB * 512) = 2048個頁表頁
- 2MB粒度映射：4GB / (2MB * 512) = 4個頁表頁



> 練習題 2：請在 `init_boot_pt` 函數的 `LAB 2 TODO 1` 處配置內核高地址頁表（`boot_ttbr1_l0`、`boot_ttbr1_l1` 和 `boot_ttbr1_l2`），以 2MB 粒度映射。

```c++
/* TTBR1_EL1 0-1G */
        /* LAB 2 TODO 1 BEGIN */
        /* Step 1: set L0 and L1 page table entry */
        vaddr = KERNEL_VADDR;
        boot_ttbr1_l0[GET_L0_INDEX(vaddr)] = ((u64) boot_ttbr1_l1) | IS_TABLE
                                             | IS_VALID | NG;
        boot_ttbr1_l1[GET_L1_INDEX(vaddr)] = ((u64) boot_ttbr1_l2) | IS_TABLE
                                             | IS_VALID | NG;

        /* Step 2: map PHYSMEM_START ~ PERIPHERAL_BASE with 2MB granularity */
        for (; vaddr < KERNEL_VADDR + PERIPHERAL_BASE; vaddr += SIZE_2M) {
                boot_ttbr1_l2[GET_L2_INDEX(vaddr)] =
                        (vaddr - KERNEL_VADDR) /* High mem, va = pa - KERNEL_VADDR */
                        | UXN /* Unprivileged execute never */
                        | ACCESSED /* Set access flag */
                        | NG /* Mark as not global */
                        | DEVICE_MEMORY /* Device memory */
                        | IS_VALID;
        }

        /* Step 2: map PERIPHERAL_BASE ~ PHYSMEM_END with 2MB granularity */
        vaddr = KERNEL_VADDR + PERIPHERAL_BASE;
        for (; vaddr < KERNEL_VADDR + PHYSMEM_END; vaddr += SIZE_2M) {
                boot_ttbr1_l2[GET_L2_INDEX(vaddr)] =
                        (vaddr - KERNEL_VADDR) /* High mem, va = pa - KERNEL_VADDR */
                        | UXN /* Unprivileged execute never */
                        | ACCESSED /* Set access flag */
                        | NG /* Mark as not global */
                        | DEVICE_MEMORY /* Device memory */
                        | IS_VALID;
        }
        
        /* LAB 2 TODO 1 END */
```

1. 首先，高地址從`KERNEL_VADDR`開始，我們需要先設置`TTBR1_EL1`中L0到L1級頁表的映射以及L1級頁表到L2級頁表的映射

   > 其中L1級頁表對應的內存頁的大小為1G，剛好是Physical Memory的大小，所以我們在映射高地址的時候不需要設置L1，只需要設置L2

2. 然後我們將高地址中[`KERNEL_VADDR`, `KERNEL_VADDR` + `PERIPHERAL_BASE`]處的地址映射到物理內存中的[`PHYSMEM_START`, `PERIPHERAL_BASE`]，其中頁的粒度為2M，同時需要設置PTE，如上面的代碼所示

3. 接著我們將高地址中的[`KERNEL_VADDR + PERIPHERAL_BASE`, `KERNEL_VADDR + PHYSMEM_END`]處的地址映射到物理內存中的[`PERIPHERAL_BASE`, `PHYSMEM_END`]，其中頁的粒度為2M，同時需要設置PTE，如上面的代碼所示



> 思考題 3：請思考在 `init_boot_pt` 函數中為什麼還要為低地址配置頁表，並嘗試驗證自己的解釋。

- 因為在開啟MMU後，PC中的值（PC = 開啟MMU的那行代碼的物理地址 + 4）不再被解釋為物理內存中的地址，立刻變成了虛擬地址。如果我們沒有配置低地址頁表，此時就會出現錯誤，跳轉到異常向量表；而我們配置了低地址頁表之後，虛擬地址中的低地址映射到物理地址中數值相等的內存區域，便不會出現錯誤，能順利執行接下來的代碼。

  > 我們在Lab1的實驗中，GDB運行到`el1_mmu_activate`代碼的第266行`msr     sctlr_el1, x8`便會卡住，最終跳轉到異常向量表中，這是由於沒有配置頁表導致的
  >
  > 如果我們在Lab2中能接著執行代碼的話，則說明我們的解釋是正確的

- 結果發現在GDB能在`el1_mmu_activate`中第266行之後繼續執行代碼，則說明我們的解釋是正確的



> 思考題 4：請解釋 `ttbr0_el1` 與 `ttbr1_el1` 是具體如何被配置的，給出代碼位置，並思考頁表基地址配置後為何需要`ISB`指令。

* 我們在`mmu.c`中初始化了一些和頁表相關的全局變量（比如`boot_ttbr0_l0`和`boot_ttbr1_l0`），我們在`tool.S`中將其讀出來讀到x8中，再利用`msr`指令將分別寫入`ttbr0_el1`中以及`ttbr1_el1`中

- 代碼的位置在`tool.S`文件的第246~250行

  ```c
  /* Write ttbr with phys addr of the translation table */
  	adrp    x8, boot_ttbr0_l0
  	msr     ttbr0_el1, x8
  	adrp    x8, boot_ttbr1_l0
  	msr     ttbr1_el1, x8
  	isb
  ```

- `isb`指令的作用是**指令同步隔離指令**，在該指令執行完成之前，後面的指令不會得到執行。在頁表基地址配置後需要`ISB`是因為這些彙編指令並不是完全順序執行的，若在配置好頁表基地址之前執行了開啟MMU的代碼，則程序會出現錯誤，所以我們需要`isb`指令來確保指令執行的順序



> 練習題 5：完成 `kernel/mm/buddy.c` 中的 `split_page`、`buddy_get_pages`、`merge_page` 和 `buddy_free_pages` 函數中的 `LAB 2 TODO 2` 部分，其中 `buddy_get_pages` 用於分配指定階大小的連續物理頁，`buddy_free_pages` 用於釋放已分配的連續物理頁。

1. `split_page`的主體是一個while循環，當`page->order == order`時循環結束返回，在其它情況時將這個page一分為二並且更新兩個page的order，維護free_lists等數據結構
2. `buddy_get_pages`的主體也是一個while循環，需要在free_lists裡面從order開始逐級向上尋找空閒的page，找到之後調用`split_page`進行分割，更新相關數據結構後返回分割後的頁
3. `merge_page`的主體是一個while循環，首先獲取page的buddy，如果這個buddy為NULL，或已經被分配，或與page的order不匹配，或者page的order>=BUDDY_MAX_ORDER-1，則無法合併，直接返回當前的page；否則，則進行合併操作，更新page的order，並維護相關的數據結構，進入下一次循環
4. `buddy_free_pages`首先將目標page的allocated位設置為0，再調用`merge_page`去嘗試將這個page與它的buddy進行合併，最後再維護相關的數據結構



> 練習題 6：完成 `kernel/arch/aarch64/mm/page_table.c` 中的 `get_next_ptp`、 `query_in_pgtbl`、`map_range_in_pgtbl`、`unmap_range_in_pgtbl` 函數中的 `LAB 2 TODO 3` 部分，後三個函數分別實現頁表查詢、映射、取消映射操作，其中映射和取消映射以 4KB 頁為粒度。

1. `query_in_pgtbl`的主體是一個while循環，調用`get_next_ptp`尋找下一個page table page，根據返回值的情況進行處理：
   1. 若返回值大小為`-ENOMAPPING`，則返回`-ENOMAPPING`（va is not mapped)
   2. 若level值為3或者返回值大小為`BLOCK_PTP`，則說明對應的pte指向的是一個物理頁，根據level值確定offset和對應的物理頁基地址，返回0
   3. 若返回值大小為`NORMAL_PTP`，則將`cur_ptp`更新為`next_ptp`，增加`level`值
2. `get_next_ptp`中待完成部分的邏輯是，通過`get_pages`得出下一個ptp，並且將其對應地址PAGE_SIZE大小內的空間置0，設置`is_valid`和`is_table`位為1，`next_table_addr`為物理地址右移12位的地址
3. `map_range_in_pgtbl`主體是一個for循環，以4KB為粒度增加cursor，調用`get_next_ptp`到L3頁表，獲取對應的entry，並設置`l3_page`的`is_page`為1，`is_valid`為1，`pfn`為物理地址右移12位的地址
4. `unmap_range_in_pgtbl`主體是一個for循環，以4KB為粒度增加cursor，調用`get_next_ptp`到L3頁表，獲取對應的entry，將`l3_page`的`is_valid`位置為0



> 練習題 7：完成 `kernel/arch/aarch64/mm/page_table.c` 中的 `map_range_in_pgtbl_huge` 和 `unmap_range_in_pgtbl_huge` 函數中的 `LAB 2 TODO 4` 部分，實現大頁（2MB、1GB 頁）支持

1. `map_range_in_pgtbl_huge`主體為三個while語句，第一個語句處理1GB頁的映射，第二個語句處理2MB頁的映射，第三個語句處理4KB頁的映射（調用`map_range_in_pgtbl`），邏輯大致都與之前實現的`map_range_in_pgtbl`類似
2. `unmap_range_in_pgtbl_huge`主體為三個while語句，第一個語句處理1GB頁的unmap，第二個語句處理2MB頁的unmap，第三個語句處理4KB頁的unmap（調用`unmap_range_in_pgtbl`），邏輯大致都與之前實現的`unmap_range_in_pgtbl`類似



> 思考題 8：閱讀 Arm Architecture Reference Manual，思考要在操作系統中支持寫時拷貝（Copy-on-Write，CoW）[^cow]需要配置頁表描述符的哪個/哪些字段，並在發生缺頁異常（實際上是 permission fault）時如何處理。

- 需要配置頁表描述符的`AP`屬性，將PTE中的AP設置成僅允許讀取(read-only)
- 在缺頁異常時，我們在buddy system中再分配一塊內存，同時將對應的PTE中的地址更新成該新分配的內存塊的地址，同時將`AP`字段設置成允許讀寫(read/write)



> 思考題 9：為了簡單起見，在 ChCore 實驗中沒有為內核頁表使用細粒度的映射，而是直接沿用了啟動時的粗粒度頁表，請思考這樣做有什麼問題。

- ChCore中大部分的文件大小沒有2MB，這意味著會在分配的內存頁中，會有大量的internel fragment，內存的利用率較低



> 挑戰題 10：使用前面實現的 `page_table.c` 中的函數，在內核啟動後重新配置內核頁表，進行細粒度的映射。