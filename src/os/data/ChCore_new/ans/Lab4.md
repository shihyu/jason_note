# Lab4

> 思考題 1：閱讀彙編代碼`kernel/arch/aarch64/boot/raspi3/init/start.S`。說明ChCore是如何選定主CPU，並阻塞其他其他CPU的執行的。

1. 首先ChCore先從`mpidr_el1`中取出各個CPU的`cpu_id`
2. 選定`cpu_id`為0的CPU為主CPU，跳到`primary`中執行
3. 其它的CPU不進行跳轉，進入到`wait_until_smp_enabled`中循環，直到對應的`secondary_boot_flag`被設置為0（由主CPU設置）



> 思考題 2：閱讀彙編代碼`kernel/arch/aarch64/boot/raspi3/init/start.S, init_c.c`以及`kernel/arch/aarch64/main.c`，解釋用於阻塞其他CPU核心的`secondary_boot_flag`是物理地址還是虛擬地址？是如何傳入函數`enable_smp_cores`中，又該如何賦值的（考慮虛擬地址/物理地址）？

1. `secondary_boot_flag`在其它CPU中是物理地址，因為此時其它CPU中的MMU還處於關閉的狀態，虛擬地址與物理地址的轉換尚未打開；在主CPU中是虛擬地址，因為主CPU打開了MMU，虛擬地址與物理地址的轉換已經開啟
2. `secondary_boot_flag`的傳遞過程如下：
   1. 主CPU運行`init_c`函數時會調用`start_kernel`函數，會把`secondary_boot_flag`傳入到`start_kernel`中
   2. 主CPU運行`start_kernel`函數時會調用`main`函數，會把`secondary_boot_flag`傳入到`main`函數中
   3. 最後`main`函數將`secondary_boot_flag`傳入到`enable_smp_cores`中
3. `secondary_boot_flag`在`enable_smp_cores`中被賦值
   1. 首先`secondary_boot_flag`在剛剛傳入`enable_smp_cores`中時是物理地址，調用`phys_to_virt`來將其轉化為虛擬地址，因為主CPU打開了MMU，虛擬地址與物理地址的轉換已經開啟
   2. `secondary_boot_flag`是一個數組，數組下標對應於`cpu_id`，會根據CPU的核數來依次對其進行賦值



> 練習題 3：完善主CPU激活各個其他CPU的函數：`enable_smp_cores`和`kernel/arch/aarch64/main.c`中的`secondary_start`。

- `enable_smp_cores`函數

  1. 需要將其它CPU從`wait_until_smp_enabled`的循環中釋放出來，將它們各自的對應的`secondary_boot_flag`值改為非0值

     ```
     secondary_boot_flag[i] = 1;
     ```

  2. 等待各個CPU的初始化進程完成

     ```
     while (cpu_status[i] != cpu_run);
     ```

- `secondary_start`函數

  1. 設置cpu_status

     ```
     cpu_status[cpuid] = cpu_run;
     ```



> 練習題 4：本練習分為以下幾個步驟：
>
> 1. 請熟悉排號鎖的基本算法，並在`kernel/arch/aarch64/sync/ticket.c`中完成`unlock`和`is_locked`的代碼。
> 2. 在`kernel/arch/aarch64/sync/ticket.c`中實現`kernel_lock_init`、`lock_kernel`和`unlock_kernel`。
> 3. 在適當的位置調用`lock_kernel`。
> 4. 判斷什麼時候需要放鎖，添加`unlock_kernel`。（注意：由於這裡需要自行判斷，沒有在需要添加的代碼周圍插入TODO註釋）

1. `unlock`操作需要將`lock->owner`的值加1，`is_locked`的判斷依據是`lock->owner`和`lock->next`是否相等
2. 這三個函數分別調用`lock_init`，`lock`，`unlock`即可
3. 在五個函數有`TODO`註釋標記的地方添加對`lock_kernel`的調用

4. 在以下位置釋放鎖：
   1. `sync_el0_64`中調用完`handle_entry_c`之後
   2. `el0_syscall`中從syscall返回之後
   3. `__eret_to_thread`中即將退出時



> 思考題 5：在`el0_syscall`調用`lock_kernel`時，在棧上保存了寄存器的值。這是為了避免調用`lock_kernel`時修改這些寄存器。在`unlock_kernel`時，是否需要將寄存器的值保存到棧中，試分析其原因。

- 在`unlock_kernel`時，不需要將寄存器的值保存到棧中，因為`unlock_kernel`幾乎不涉及對寄存器的修改，只是改變了`lock->owner`這一在內存中的值



> 思考題 6：為何`idle_threads`不會加入到等待隊列中？請分析其原因？

- 因為如果`idle_threads`加入到了等待隊列中，則意味著`idle_threads`也會被調度到。然而`idle_threads`並沒有什麼實際意義，只是一個循環空轉，調度到`idle_threads`是對CPU資源的一種浪費。因此為了節約計算資源提高性能，`idle_threads`不會加入到等待隊列中



> 練習題 7：完善`kernel/sched/policy_rr.c`中的調度功能，包括`rr_sched_enqueue`，`rr_sched_dequeue`，`rr_sched_choose_thread`與`rr_sched`，需要填寫的代碼使用`LAB 4 TODO BEGIN`標出。

- `rr_sched_enqueue`函數
  1. 首先對參數進行一些判斷，做錯誤處理
     1. `thread`或者`thread_ctx`為NULL
     2. 已經入隊的thread不能重複入隊（state不能是`TS_READY`）
     3. IDLE線程不能入隊
  2. 設置當前thread的狀態，包括state和cpuid
  3. 將其加入到等待隊列中，更新隊列長度

- `rr_sched_dequeue`函數
  1. 首先對參數進行一些判斷，做錯誤處理
     1. `thread`或者`thread_ctx`為NULL
     2. 出隊的對象不能是IDLE線程
     3. 出隊的對象不能是不在隊列中的線程（state一定是`TS_READY`）
  2. 設置當前thread的狀態，包括state和cpuid
  3. 將其出隊，更新隊列長度

- `rr_sched_choose_thread`函數
  1. 如果等待隊列的長度為0，返回IDLE線程
  2. 否則返回隊列中第一個線程，將其出隊

- `rr_sched`函數
  1. 進行條件判斷
     1. 如果`current_thread`為NULL或者其`thread_ctx`為NULL，不做任何處理
     2. 如果`current_thread`的`thread_exit_state`為`TE_EXITING`，則將`state`設置為`TS_EXIT`，將`thread_exit_state`設置為`TE_EXITED`
     3. 如果`current_thread`的`state`不是`TS_WAITING`，則將`current_thread`入隊
  2. 調用`switch_to_thread`換線程



> 思考題 8：如果異常是從內核態捕獲的，CPU核心不會在`kernel/arch/aarch64/irq/irq_entry.c`的`handle_irq`中獲得大內核鎖。但是，有一種特殊情況，即如果空閒線程（以內核態運行）中捕獲了錯誤，則CPU核心還應該獲取大內核鎖。否則，內核可能會被永遠阻塞。請思考一下原因。

- 因為在同一時刻可能有多個CPU在運行空閒線程（以內核態運行），如果不獲取大內核鎖則有可能出現多個錯誤處理函數在不同CPU上同時運行內核代碼的情況，相應的共享數據結構可能會被錯誤修改而產生代碼運行故障，因此可能會出現內核永遠被阻塞的問題。
- 也可能是因為如果空閒線程觸發了調度函數，在返回用戶態線程的過程中需要放一次鎖，如空閒線程在這之前沒有拿到鎖的話會出現錯誤



> 練習題 9：在`kernel/sched/sched.c`中實現系統調用`sys_yield()`，使用戶態程序可以啟動線程調度。此外，ChCore還添加了一個新的系統調用`sys_get_cpu_id`，其將返回當前線程運行的CPU的核心id。請在`kernel/syscall/syscall.c`文件中實現該函數。

- `sys_yield()`函數
  1. 重置當前線程的預算，確保可以立刻調度當前線程
  2. 調用`sched`函數
  3. 調用`eret_to_thread`函數切換線程

- `sys_get_cpu_id()`函數

  為`cpuid`賦值`cpuid = smp_get_cpu_id();`



> 練習題 10：定時器中斷初始化的相關代碼已包含在本實驗的初始代碼中（`timer_init`）。請在主CPU以及其他CPU的初始化流程中加入對該函數的調用。此時，`yield_spin.bin`應可以正常工作：主線程應能在一定時間後重新獲得對CPU核心的控制並正常終止。

- 在主CPU初始化的`main`函數中

  在`arch_interrupt_init()`調用下方調用`timer_init()`，打開時鐘中斷

- 在其它CPU初始化的`secondary_start`函數中

  在`lock_kernel()`前調用`timer_init()`，打開時鐘中斷



> 練習題 11：在`kernel/sched/sched.c`處理時鐘中斷的函數`sched_handle_timer_irq`中添加相應的代碼，以便它可以支持預算機制。更新其他調度函數支持預算機制，不要忘記在`kernel/sched/sched.c`的`sys_yield()`中重置“預算”，確保`sys_yield`在被調用後可以立即調度當前線程。完成本練習後應能夠`tst_sched_preemptive`測試並獲得5分。

- `sched_handle_timer_irq`函數

  在`current_thread`、`current_thread->thread_ctx`不為NULL，且`budget`不等於0的時候，將budget減去1

- 其它調度函數預算機制的更新

  在`rr_sched`函數中，在當前進程的`budget`不等於0且`affinity`與當前CPU的cpuid匹配時，不改變當前運行的線程

- `sys_yield`

  1. 重置當前線程的預算，確保可以立刻調度當前線程
  2. 調用`sched`函數
  3. 調用`eret_to_thread`函數切換線程



> 練習題 12：在`kernel/object/thread.c`中實現`sys_set_affinity`和`sys_get_affinity`。完善`kernel/sched/policy_rr.c`中的調度功能，增加線程的親和性支持（如入隊時檢查親和度等，請自行考慮）。

- `sys_set_affinity`函數以及`sys_get_affinity`函數

  簡單返回或設置`affinity`即可

- `rr_sched_enqueue`函數

  1. 首先檢查`aff`是否valid，否則返回`-EINVAL`
  2. 在`aff == NO_AFF`時將thread加入本CPU的等待隊列，否則加入到`aff`所對應的CPU中



> 練習題 13：在`userland/servers/procm/launch.c`中填寫`launch_process`函數中缺少的代碼。

1. 利用`__chcore_sys_create_pmo`函數創建pmo，返回`main_stack_cap`

2. `stack_top`的值為`MAIN_THREAD_STACK_BASE + MAIN_THREAD_STACK_SIZE`

   `offset`的值為`MAIN_THREAD_STACK_SIZE - PAGE_SIZE`(因為最上方的一個page存儲了一些數據)

3. 填充參數`pmo_map_requests[0]`，對應於內核棧的物理內存對象

4. `arg.stack`的值為`stack_top - PAGE_SIZE`



> 練習題 14：在`libchcore/src/ipc/ipc.c`與`kernel/ipc/connection.c`中實現了大多數IPC相關的代碼，請根據註釋完成其餘代碼。

- `create_connection`

  1. 根據傳入參數給定的`stack_base_addr`和`conn_idx`來唯一確定`server_stack_base`
  2. 同上方法確定`server_buf_base`，`client_buf_base`使用傳入參數即可
  3. 利用`vmspace_map_range`函數將共享內存分別映射到client和server的虛擬地址空間

- `thread_migrate_to_server`

  1. 服務線程的stack地址為`conn->server_stack_top`
  2. 服務線程的ip為`callback`
  3. 分別將arg和pid作為參數傳入服務線程

- `thread_migrate_to_client`

  將client線程的返回值設置為`ret_value`

- `ipc_send_cap`

  調用`cap_copy`將cap複製到server中，同時更新cap_buf

- `sys_ipc_return`

  將client線程的state設置為`TS_INTER`，budget設置為`DEFAULT_BUDGET`

- `sys_ipc_call`

  1. 若`cap_num`大於0，則調用`ipc_send_cap`傳遞參數
  2. arg是server中`ipc_msg`的地址，需要將client中`ipc_msg`的地址減去offset後傳入

- `ipc_register_server`

  設置server中stack的大小和基地址，以及共享內存buffer的大小和基地址

- `ipc_register_client`

  設置client中共享內存buffer的大小和基地址

- `ipc_set_msg_data`

  將數據拷貝到ipc_msg中，需要注意的是data的起始地址是`ipc_msg + ipc_msg->data_offset`



> 練習題 15：ChCore在`kernel/semaphore/semaphore.h`中定義了內核信號量的結構體，並在`kernel/semaphore/semaphore.c`中提供了創建信號量`init_sem`與信號量對應syscall的處理函數。請補齊`wait_sem`操作與`signal_sem`操作。

- `wait_sem`
  1. 當資源數大於0時，直接減1即可
  2. 當資源數等於0且選擇了非阻塞時，返回`-EAGAIN`
  3. 當資源數等於0且選擇了阻塞時，將線程的狀態設置為`TS_WAITING`，將其放入等待隊列中，同時設置線程的返回值，同時增加sem的reference數量
- `signal_sem`
  1. 當沒有等待線程時，增加sem->sem_count即可
  2. 當有等待線程時，不增加sem->sem_count，激活隊列中第一個等待線程，將其放入調度的等待隊列中



> 練習題 16：在`userland/apps/lab4/prodcons_impl.c`中實現`producer`和`consumer`。

- `producer`

  等待`empty_slot`的資源，完成producing任務後給`filled_slot`發信號

- `consumer`

  等待`filled_slot`的資源，完成consuming任務後給`empty_slot`發信號



> 練習題 17：請使用內核信號量實現阻塞互斥鎖，在`userland/apps/lab4/mutex.c`中填上`lock`與`unlock`的代碼。注意，這裡不能使用提供的`spinlock`。

- `lock_init`

  使用系統調用`__chcore_sys_create_sem`來初始化鎖，同時調用`__chcore_sys_signal_sem`將最初的資源數設置為1

- `lock`

  調用`__chcore_sys_wait_sem`

- `unlock`

  調用`__chcore_sys_signal_sem`