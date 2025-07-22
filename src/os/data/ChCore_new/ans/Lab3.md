# Lab3

> 思考題 1: 內核從完成必要的初始化到用戶態程序的過程是怎麼樣的？嘗試描述一下調用關係。

1. 內核在完成必要的初始化之後，先調用`arch_interrupt_init`函數進行異常向量表的初始化
2. 然後調用`create_root_thread`創建第一個用戶態程序。在`create_root_thread`中：
   1. 內核先調用`create_root_cap_group`創建內核對象(kernel object)——進程的抽象`cap_group`
   2. 之後再調用`__create_root_thread`在`cap_group`中創建root thread
   3. 最後通過`obj_put`和`switch_to_thread`函數設置新創建的root thread，將`current_thread`設置為root thread
3. 最後回到main函數中，調用`eret_to_thread(switch_context())`進行context switch，真正切換到剛剛創建的root上運行



> 練習題 2: 在 `kernel/object/cap_group.c` 中完善 `cap_group_init`、`sys_create_cap_group`、`create_root_cap_group` 函數。在完成填寫之後，你可以通過 Cap create pretest 測試點。

- `cap_group_init`函數是初始化cap_group的函數，需要依次初始化slot_table, thread_list, thread_cnt以及pid（根據傳入的參數決定）
- `sys_create_cap_group`是用戶創建cap_group的函數，在需要我們填寫的部分中：
  1. 調用`obj_alloc`創建`new_cap_group`對象，同時調用`cap_group_init`來初始化cap_group
  2. 調用`obj_alloc`創建`vmspace`對象
- `create_root_cap_group`是用戶創建第一個進程所使用的函數，在我們需要填寫的部分中：
  1. 調用`obj_alloc`創建`new_cap_group`對象
  2. 調用`cap_group_init`來初始化`cap_group`，同時調用`cap_alloc`來更新`cap_group`的`slot_table`，將`cap_group`自身加入到其中
  3. 調用`obj_alloc`創建`vmspace`對象
  4. 設置`vmspace->pcid`為`ROOT_PCID`，同時調用`vmspace_init`來初始化`vmspace`，再調用`cap_alloc`來更新`cap_group`的`slot_table`，將`vmspace`加入到其中



> 練習題 3: 在 `kernel/object/thread.c` 中完成 `load_binary` 函數，將用戶程序 ELF 加載到剛剛創建的進程地址空間中。

由於Chcore系統中尚無文件系統，所有用戶程序鏡像以ELF二進制的形式直接嵌入到內核鏡像中，所以相當於我們可以直接從內存中訪問ELF文件，觀察`load_binary`函數的參數，我們不難發現`bin`就是ELF文件開頭的位置，我們進行如下操作：

1. 從program headers中獲取flags（調用`PFLAGS2VMRFLAGS`將其轉化為vmr_flags_t類型）

2. 算出`seg_map_sz`，需要以頁為粒度去映射，因此需要調用`ROUND_UP`和`ROUND_DOWN`

   ```c++
   seg_map_sz = ROUND_UP(p_vaddr + seg_sz, PAGE_SIZE) - ROUND_DOWN(p_vaddr, PAGE_SIZE);
   ```

3. 為每個ELF section創建一個對應的pmo，調用`create_pmo`

4. 將ELF文件中對應的section拷貝到剛剛創建的pmo的內存中(調用`memcpy`)

5. 調用`vmspace_map_range`添加內存映射，以頁為粒度



> 練習題 4: 按照前文所述的表格填寫 `kernel/arch/aarch64/irq/irq_entry.S` 中的異常向量表，並且增加對應的函數跳轉操作。

1. 異常向量表調用宏定義函數`exception_entry`+`label`來實現，對照前文的表格填入
2. 函數跳轉即為`bl <handler>`，`irq_el1h`, `irq_el1t`, `fiq_el1t`, `fiq_el1h`, `error_el1t`, `error_el1h`, `sync_el1t`, `sync_el1h`調用`unexpected_handler`，`sync_el1h`調用`handle_entry_c`



> 練習題 5: 填寫 `kernel/arch/aarch64/irq/pgfault.c` 中的 `do_page_fault`，需要將缺頁異常轉發給 `handle_trans_fault` 函數。

- 直接調用`ret = handle_trans_fault(current_thread->vmspace, fault_addr)`即可



> 練習題 6: 填寫 `kernel/mm/pgfault_handler.c` 中的 `handle_trans_fault`，實現 `PMO_SHM` 和 `PMO_ANONYM` 的按需物理頁分配。

1. 首先調用`get_page_from_pmo`獲取缺頁異常的page的物理地址
2. 檢查pmo中當前的fault地址對應的物理頁是否存在
   1. 若未分配(`pa == 0`)，則通過`get_pages`分配一個物理頁，然後用`commit_page_pmo`將頁記錄在pmo中，用`map_range_in_pgtbl`增加頁表映射
   2. 若已分配，則調用`map_range_in_pgtbl`修改頁表映射



> 練習題 7: 按照前文所述的表格填寫 `kernel/arch/aarch64/irq/irq_entry.S` 中的 `exception_enter` 與 `exception_exit`，實現上下文保存的功能。

- `exception_enter`中用`stp`將`x0`~`x29`寄存器依次保存，然後在獲取系統寄存器之後，將這些系統寄存器中的值與`x30`一起保存，最後更新`sp`的值
- `exception_exit`同理，先將系統寄存器中的值從內存中通過`ldp`加載出來存入系統寄存器，然後再依次使用`stp`將`x0`~`x29`從內存中加載出來恢復，最後更新`sp`的值



> 思考題 8： ChCore中的系統調用是通過使用匯編代碼直接跳轉到`syscall_table`中的 相應條目來處理的。請閱讀`kernel/arch/aarch64/irq/irq_entry.S`中的代碼，並簡要描述ChCore是如何將系統調用從異常向量分派到系統調用表中對應條目的。

1. 在user態進行系統調用時，代碼下陷到kernel態觸發同步異常，處理器在異常向量表中找到對應的異常處理程序代碼`sync_el0_64`
2. 進入到`sync_el0_64`後，首先調用`exception_enter`進行上下文保存，進行一些比較之後調用`el0_syscall`
3. `el0_syscall`先到syscall_table中查詢對應的syscall entry，也即對應的異常handler函數，然後通過`blr`調用這個函數
4. 最後調用`exception_exit`恢復上下文，退出syscall



> 練習題 9: 填寫 `kernel/syscall/syscall.c` 中的 `sys_putc`、`sys_getc`，`kernel/object/thread.c` 中的 `sys_thread_exit`，`libchcore/include/chcore/internal/raw_syscall.h` 中的 `__chcore_sys_putc`、`__chcore_sys_getc`、`__chcore_sys_thread_exit`，以實現 `putc`、`getc`、`thread_exit` 三個系統調用。

1. `sys_thread_exit`：將`current_thread`的`thread_exit_state`設置為`TE_EXITED`，然後調用`thread_deinit`來銷燬當前的thread
2. `sys_putc`：調用`uart_send`
3. `sys_getc`：調用`uart_recv`
4. `__chcore_sys_putc`：調用`__chcore_syscall1`，傳入系統調用編號和`ch`
5. `__chcore_sys_getc`：調用`__chcore_sys_call0`，傳入系統調用編號
6. `__chcore_sys_thread_exit`：調用`__chcore_syscall0`，傳入系統調用編號