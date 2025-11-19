# 實驗 4：多核、多進程、調度與IPC

在本實驗中，ChCore將支持在多核處理器上啟動（第一部分）；實現多核調度器以調度執行多個線程（第二部分）；實現第一個用戶態系統服務：進程管理器並支持`spawn`系統調用以啟動新的進程（第三部分）；最後實現內核信號量（第四部分）。

## 第一部分：多核支持

在本實驗第一部分中，ChCore將進入多核的世界。為了讓ChCore支持多核，我們需要考慮如下問題：

- 如何啟動多核，讓每個核心執行初始化代碼並開始執行用戶代碼？
- 如何區分不同核心在內核中保存的數據結構（比如狀態，配置，內核對象等）？
- 如何保證內核中對象併發正確性，確保不會由於多個核心同時訪問內核對象導致競爭條件？

在啟動多核之前，我們先介紹ChCore如何解決第二個問題。ChCore對於內核中需要每個CPU核心單獨存一份的內核對象，都根據核心數量創建了多份（即利用一個數組來保存）。ChCore支持的核心數量為`PLAT_CPU_NUM`（該宏定義在 `kernel/common/machine.h` 中，其代表可用CPU核心的數量，根據具體平臺而異）。 比如，實驗使用的樹莓派3平臺擁有4個核心，因此該宏定義的值為4。ChCore會CPU核心的核心ID作為數組的索引，在數組中取出對應的CPU核心本地的數據。為了方便確定當前執行該代碼的CPU核心ID，我們在 `kernel/arch/aarch64/machine/smp.c`中提供了`smp_get_cpu_id`函數。該函數通過訪問系統寄存器`tpidr_el1`來獲取調用它的CPU核心的ID，該ID可用作訪問上述數組的索引。

### 啟動多核

在實驗1中我們已經介紹，在QEMU模擬的樹莓派中，所有CPU核心在開機時會被同時啟動。在引導時這些核心會被分為兩種類型。一個指定的CPU核心會引導整個操作系統和初始化自身，被稱為**主CPU**（primary CPU）。其他的CPU核心只初始化自身即可，被稱為**其他CPU**（backup CPU）。CPU核心僅在系統引導時有所區分，在其他階段，每個CPU核心都是被相同對待的。

> 思考題 1：閱讀彙編代碼`kernel/arch/aarch64/boot/raspi3/init/start.S`。說明ChCore是如何選定主CPU，並阻塞其他其他CPU的執行的。

在樹莓派真機中，還需要主CPU手動指定每一個CPU核心的的啟動地址。這些CPU核心會讀取固定地址的上填寫的啟動地址，並跳轉到該地址啟動。在`kernel/arch/aarch64/boot/raspi3/init/init_c.c`中，我們提供了`wakeup_other_cores`函數用於實現該功能，並讓所有的CPU核心同在QEMU一樣開始執行`_start`函數。

與之前的實驗一樣，主CPU在第一次返回用戶態之前會在`kernel/arch/aarch64/main.c`中執行`main`函數，進行操作系統的初始化任務。在本小節中，ChCore將執行`enable_smp_cores`函數激活各個其他CPU。

> 思考題 2：閱讀彙編代碼`kernel/arch/aarch64/boot/raspi3/init/start.S, init_c.c`以及`kernel/arch/aarch64/main.c`，解釋用於阻塞其他CPU核心的`secondary_boot_flag`是物理地址還是虛擬地址？是如何傳入函數`enable_smp_cores`中，又該如何賦值的（考慮虛擬地址/物理地址）？

> 練習題 3：完善主CPU激活各個其他CPU的函數：`enable_smp_cores`和`kernel/arch/aarch64/main.c`中的`secondary_start`。請注意測試代碼會要求各個其他CPU按序被依次激活。在完成該部分之後，應看到如下輸出：
>
> ```
> [INFO] CPU 0 is active
> [INFO] CPU 1 is active
> [INFO] CPU 2 is active
> [INFO] CPU 3 is active
> [INFO] All 4 CPUs are active
> ```
>
> 完成該練習後應能夠通過`Boot multicore`測試，並獲得對應的5分。注意，這裡由於實驗後續步驟還未完成，其他核心會有對應的報錯輸出，導致評分腳本*可能暫時無法正確給分*。請先自行判斷輸出中是否包含有以上內容。隨著後續實驗進行，評分腳本將能夠正確判斷。

### 大內核鎖

從現在開始，內核代碼已經可以運行在多核上了。為了確保代碼不會由於併發執行而引起錯誤，ChCore應首先解決併發問題。在本小節中，ChCore將使用最簡單的併發控制方法，即通過一把**大內核鎖**保證不會有多個核心同時訪問內核的數據（即互斥訪問）。具體而言，CPU核心在進入內核態執行內核代碼之前，它應該首先獲得大內核鎖。同理，CPU核心應當在退出內核態之前釋放大內核鎖。大內核鎖的獲取與釋放，保證了同時只存在一個CPU核心執行內核代碼、訪問內核數據，因此不會產生競爭。在文件`kernel/arch/aarch64/sync/ticket.c`中，我們提供了一個簡單的排號鎖，用以充當大內核鎖。

ChCore中大內核鎖共有三個接口進行封裝：初始化大內核鎖的`kernel_lock_init`，上鎖與放鎖操作`lock_kernel`與`unlock_kernel`。在本實驗中，為了在CPU核心進入內核態時拿鎖、離開內核態時放鎖，應該在以下5個位置調用上述接口進行**加鎖操作**：

1. `kernel/arch/aarch64/main.c`中的`main`：主CPU在初始化完成之後且其他CPU返回用戶態之前獲取大內核鎖。
2. `kernel/arch/aarch64/main.c`中的`secondary_start`：其他CPU在初始化完成之後且返回用戶態之前獲取大內核鎖。
3. `kernel/arch/aarch64/irq/irq_entry.S`中的`el0_syscall`：在跳轉到`syscall_table`中相應的`syscall`條目之前獲取大內核鎖（該部分彙編代碼已實現完成）。
4. `kernel/arch/aarch64/irq/irq_entry.c`中的`handle_entry_c`：在該異常處理函數的第一行獲取大內核鎖。因為在內核態下也可能會發生異常，所以如果異常是在內核中捕獲的，則不應獲取大內核鎖。
5. `kernel/arch/aarch64/irq/irq_entry.c`中的`handle_irq`：在中斷處理函數的第一行獲取大內核鎖。與`handle_entry_c`類似，如果是內核異常，則不應獲取該鎖。

> 練習題 4：本練習分為以下幾個步驟：
>
> 1. 請熟悉排號鎖的基本算法，並在`kernel/arch/aarch64/sync/ticket.c`中完成`unlock`和`is_locked`的代碼。
> 2. 在`kernel/arch/aarch64/sync/ticket.c`中實現`kernel_lock_init`、`lock_kernel`和`unlock_kernel`。
> 3. 在適當的位置調用`lock_kernel`。
> 4. 判斷什麼時候需要放鎖，添加`unlock_kernel`。（注意：由於這裡需要自行判斷，沒有在需要添加的代碼周圍插入TODO註釋）
>
> 至此，ChCore已經可以通過使用大內核鎖來處理可能的併發問題。本練習的前2項可以通過提供的內核鎖測試檢查是否正確，後2項內容則需後續完成調度後再核對（ChCore應能正常運行用戶態程序）。
>
> 完成本練習後應能夠通過`Mutex test`測試，並獲得對應的5分。
>
> **注意：本部分測試需要打開`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`ON`。**
>
> ```
> CHCORE_KERNEL_TEST:BOOL=ON
> ```

> 思考題 5：在`el0_syscall`調用`lock_kernel`時，在棧上保存了寄存器的值。這是為了避免調用`lock_kernel`時修改這些寄存器。在`unlock_kernel`時，是否需要將寄存器的值保存到棧中，試分析其原因。

在課本中，我們還介紹了由於嵌套中斷可能會導致死鎖，其必須使用可重入鎖來解決。為簡單起見，ChCore實驗不考慮可重入鎖。在內核中，我們關閉了中斷。
這一功能是在硬件的幫助下實現的。
當異常觸發時，中斷即被禁用。
當彙編代碼`eret`被調用時，中斷則會被重新啟用。
因此，在整個實驗的實現過程中，可以無需考慮時鐘中斷打斷內核代碼執行的情況，而僅需要其對用戶態進程的影響。

## 第二部分：調度

截止目前，ChCore已經可以啟動多核，但仍然無法對多個線程進行調度。本部分將首先實現協作式調度，從而允許當前在CPU核心上運行的線程**主動退出或主動放棄CPU**時，CPU核心能夠切換到另一個線程繼續執行。其後，我們將支持搶佔式調度，使得內核可以在一定時間片後重新獲得對CPU核心的控制，而無需當前運行線程的配合。最後，我們將擴展調度器，允許線程被調度到所有CPU核心上。

### 協作式調度

在本部分將實現一個基本的調度器，該程序調度在同一CPU核心上運行的線程。所有相關的數據結構都可以在`kernel/include/sched/sched.h`中找到，這裡簡要介紹其涉及的數據結構：

- `current_threads`是一個數組，分別指向每個CPU核心上運行的線程。而`current_thread`則利用`smp_get_cpu_id`獲取當前運行核心的id，從而找到當前核心上運行的線程。

- `sched_ops`則是用於抽象ChCore中調度器的一系列操作。它存儲指向不同調度操作的函數指針，以支持不同的調度策略。

    - `sche_init`：初始化調度器。
    - `sched`：進行一次調度。即將正在運行的線程放回就緒隊列，然後在就緒隊列中選擇下一個需要執行的線程返回。
    - `sched_enqueue`：將新線程添加到調度器的就緒隊列中。
    - `sched_dequeue`：從調度器的就緒隊列中取出一個線程。
    - `sched_top`：用於debug打印當前所有核心上的運行線程以及等待線程的函數。

- `cur_sched_ops`則是一個`sched_ops`的實例，其在`sched_init`的時候初始化。ChCore用在 `kernel/include/sched/sched.h` 中定義的靜態函數封裝對`cur_sched_ops`的調用。

#### Round Robin（時間片輪轉）調度策略

我們將在`kernel/sched/policy_rr.c`中實現名為`rr`的調度策略，以實現時間片輪轉方式調度線程。回顧一下時間片輪轉調度：其將維護一個FIFO（先入先出）的線程就緒隊列，所有可以執行的線程均放在該就緒隊列中。調度器將每次將當前正在執行的線程放回到就緒隊列中，並從該就緒隊列中按照先入先出的順序取一個就緒的線程執行。

具體而言，在ChCore的實現中，每個CPU核心都有自己線程就緒隊列（`rr_ready_queue_meta`），該列表存儲CPU核心的就緒線程。一個線程只能出現在一個CPU核心的就緒隊列中。當調用`sched_enqueue`時，rr策略會指向`rr_sched_enqueue`。該函數會將傳入的線程放入合適的核心的線程就緒隊列中，並將線程的狀態設置為`TS_READY`。

同樣，當CPU核心調用`sched_dequeue`時，rr策略會指向`rr_sched_dequeue`。該操作將從核心自己的就緒隊列中取出給定線程，並將線程狀態設置為`TS_INTER`，代表了線程的中間狀態。在本部分還未支持設置CPU的親和度，因此只要求將當前的線程加入到當前的核心的等待隊列中。此外，還應該更新該線程的`thread_ctx->cpuid`代表其當前所屬的CPU核心。

一旦CPU核心要發起調度，它只需要調用`rr_sched`。該函數將首先檢查當前是否正在運行某個線程。如果是，它將調用`rr_sched_enqueue`將線程添加回就緒隊列。然後，它調用`rr_sched_choose_thread`按照上述的時間片輪轉的策略來選擇要調度的線程。當CPU核心沒有要調度的線程時，它不應在內核態忙等，否則它持有的大內核鎖將鎖住整個內核。所以，ChCore為每個CPU核心創建一個空閒線程（即`idle_threads`）。空閒線程將不斷的執行一個空循環，其實現在`kernel/arch/aarch64/sched/idle.S`。`rr_sched_choose_thread`首先檢查CPU核心的就緒隊列是否為空。如果是，`rr_sched_choose_thread`將返回CPU核心自己的空閒線程。如果就緒隊列中有其他的線程，它將選擇就緒隊列的隊首並調用`rr_sched_dequeue`使該隊首出隊，然後返回該隊首線程。在ChCore中，`idle_threads`不應出現在就緒隊列中。因此，`rr_sched_enqueue`和`rr_sched_dequeue`都應空閒線程進行特殊處理。

當線程退出時（即`thread_exit_state`被設置為`TE_EXITING`時），其也會調用`rr_sched`來調度到其他線程執行。因此，當判斷到當前的線程正在退出時，`rr_sched`需要更新線程的狀態`state`為`TS_EXIT`以及其退出狀態`thread_exit_state`為`TE_EXITED`。此外，該線程也不應加入到等待隊列中。

> 思考題 6：為何`idle_threads`不會加入到等待隊列中？請分析其原因？

`rr_sched_init`用於初始化調度器。它只能在內核初始化流程中被調用一次。由主CPU負責初始化`rr_ready_queue_meta`和`idle_threads`中的所有條目。

> 練習題 7：完善`kernel/sched/policy_rr.c`中的調度功能，包括`rr_sched_enqueue`，`rr_sched_dequeue`，`rr_sched_choose_thread`與`rr_sched`，需要填寫的代碼使用`LAB 4 TODO BEGIN`標出。在完成該部分後應能看到如下輸出，並通過`cooperative`測試獲得5分。
>
> ```
> [INFO] Pass tst_sched_cooperative!
> ```
>
> **注意：本部分測試需要打開`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`ON`。**
>
> ```
> CHCORE_KERNEL_TEST:BOOL=ON
> ```

> 思考題 8：如果異常是從內核態捕獲的，CPU核心不會在`kernel/arch/aarch64/irq/irq_entry.c`的`handle_irq`中獲得大內核鎖。但是，有一種特殊情況，即如果空閒線程（以內核態運行）中捕獲了錯誤，則CPU核心還應該獲取大內核鎖。否則，內核可能會被永遠阻塞。請思考一下原因。

在本小節中，ChCore還處於協作式調度。顧名思義，協作式調度需要線程主動放棄CPU。為了實現該功能，我們提供了`sys_yield`這一個新的syscall。該syscall可以主動放棄當前CPU核心，並調用上述的`sched`接口完成調度器的調度工作。

> 練習題 9：在`kernel/sched/sched.c`中實現系統調用`sys_yield()`，使用戶態程序可以啟動線程調度。此外，ChCore還添加了一個新的系統調用`sys_get_cpu_id`，其將返回當前線程運行的CPU的核心id。請在`kernel/syscall/syscall.c`文件中實現該函數。
>
> 運行用戶態程序`yield_single.bin`應能看到以下輸出：
>
> ```
> Hello from ChCore userland!
> Hello, I am thread 0
> Hello, I am thread 1
> Iteration 1, thread 0, cpu 0
> Iteration 1, thread 1, cpu 0
> Iteration 2, thread 0, cpu 0
> Iteration 2, thread 1, cpu 0
> Iteration 3, thread 0, cpu 0
> Iteration 3, thread 1, cpu 0
> Iteration 4, thread 0, cpu 0
> ...
> ```
>
> **提示：成功運行該用戶態程序同時需要上一小節在正確的地方添加加鎖與放鎖條件。如果無法正確運行，可以進一步檢查大內核鎖相關代碼是否實現正確。**
>
> **注意：本部分測試需要關閉`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`OFF`。並將對應的啟動程序設置為`yield_single.bin`**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=yield_single.bin
> CHCORE_KERNEL_TEST:BOOL=OFF
> ```
>
> 評分腳本將在後續練習檢查該部分正確性。

### 搶佔式調度

使用剛剛實現的協作式調度器，ChCore能夠在單個CPU核心內部調度線程。然而，若用戶線程不想放棄對CPU核心的佔據，內核便只能讓用戶線程繼續執行，而無法強制用戶線程中止。 因此，在這一部分中，本實驗將實現搶先式調度，以幫助內核定期重新獲得對CPU核心的控制權。

#### 時鐘中斷與搶佔

請嘗試運行`yield_spin.bin`程序。該用戶程序的主線程將創建一個“自旋線程”，該線程在獲得CPU核心的控制權後便會執行無限循環，進而導致無論是該程序的主線程還是ChCore內核都無法重新獲得CPU核心的控制權。 就保護系統免受用戶程序中的錯誤或惡意代碼影響而言，這一情況顯然並不理想，任何用戶應用線程均可以如該“自旋線程”一樣，通過進入無限循環來永久“霸佔”整個CPU核心。

#### 處理時鐘中斷

為了處理“自旋線程”的問題，允許ChCore內核強行中斷一個正在運行的線程並奪回對CPU核心的控制權，我們必須擴展ChCore以支持來自時鐘硬件的外部硬件中斷。

> 練習題 10：定時器中斷初始化的相關代碼已包含在本實驗的初始代碼中（`timer_init`）。請在主CPU以及其他CPU的初始化流程中加入對該函數的調用。此時，`yield_spin.bin`應可以正常工作：主線程應能在一定時間後重新獲得對CPU核心的控制並正常終止。
>
> 在完成功能後，運行用戶態程序`yield_spin.bin`應能看到以下輸出：
>
> ```
> Hello, I am thread 1
> Successfully regain the control!
> ```
>
> **注意：本部分測試需要關閉`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`OFF`。並將對應的啟動程序設置為`yield_spin.bin`**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=yield_spin.bin
> CHCORE_KERNEL_TEST:BOOL=OFF
> ```
>
> 評分腳本將在後續練習檢查該部分正確性。

#### 調度預算（Budget）

在實際的操作系統中，如果每次時鐘中斷都會觸發調度，會導致調度時間間隔過短、增加調度開銷。對於每個線程，我們在`kernel/include/sched/sched.h`中維護了一個**調度上下文**`sched_cont`。`sched_cont`中存在一個成員`budget`，其表示該線程被調度時的“預算”。當每一次處理時鐘中斷時，將當前線程的預算減少一。在之前的調度策略實現`sched`中，調度器應只能在某個線程預算等於零時才能調度該線程。通過給每個線程合適的“預算”，就可以避免過於頻繁的調度。此外，我們已經提供了一個函數原型`rr_sched_refill_budget`，其應在當前線程預算用完之後被使用，並且給當前線程重新填滿默認的預算`DEFAULT_BUDGET`。

> 練習題 11：在`kernel/sched/sched.c`處理時鐘中斷的函數`sched_handle_timer_irq`中添加相應的代碼，以便它可以支持預算機制。更新其他調度函數支持預算機制，不要忘記在`kernel/sched/sched.c`的`sys_yield()`中重置“預算”，確保`sys_yield`在被調用後可以立即調度當前線程。完成本練習後應能夠`tst_sched_preemptive`測試並獲得5分。
>
> ```
> [INFO] Pass tst_sched_preemptive!
> ```
>
> **注意：本部分測試需要打開`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`ON`。**
>
> ```
> CHCORE_KERNEL_TEST:BOOL=ON
> ```

#### 處理器親和性（Affinity）

到目前為止，已經實現了一個基本完整的調度器。但是，ChCore中的Round Robin策略為每個CPU核心維護一個等待隊列，並且無法在CPU核心之間調度線程。

為瞭解決此問題，親和性（Affinity）的概念被引入，親和性使線程可以綁定到特定的CPU核心。在創建線程時，線程的親和性（`thread_ctx->affinity`）被設置為`NO_AFF`。其代表當前核心可以被調度器放在任意核心運行。將沒有親和度設置的線程加入等待隊列時，ChCore將直接加入到當前核心的等待隊列，否則其應該加入到相應核心的隊列。為了設置與獲取線程的的親和性，ChCore提供了兩個系統調用：`sys_set_affinity`與`sys_get_affinity`，其將分別用於設置與獲取線程的`thread_ctx->affinity`。除了設置親和性，調度器也需要支持親和性，從而保證擁有指定親和性的線程只能在指定核心上運行。

> 練習題 12：在`kernel/object/thread.c`中實現`sys_set_affinity`和`sys_get_affinity`。完善`kernel/sched/policy_rr.c`中的調度功能，增加線程的親和性支持（如入隊時檢查親和度等，請自行考慮）。完成後應能看到內核輸出如下內容：
>
> ```
> [INFO] Pass tst_sched_affinity!
> [INFO] Pass tst_sched!
> ```
>
> **注意：本部分測試需要打開`CHCORE_KERNEL_TEST`，即在`.config`文件中如下行選擇`ON`。**
>
> ```
> CHCORE_KERNEL_TEST:BOOL=ON
> ```
>
> 完成本練習後應能夠通過內核`Affinity`與`Sched`測試，獲得10分。並能夠通過用戶態所有的調度測試，包括之前的` Yield single`，`Yield spin`，以及新怎的`Yield multi`，`Yield aff`，與`Yield multi aff`測試。總共獲得25分。
> 提示：這裡如果確認調度部分都完成正確，但是無法正確運行，可以查看之前是否在正確的地方釋放了大內核鎖。

至此，實驗的第二部分已全部完成，請確認通過了所有第二部分的測試。

## 第三部分：進程管理器（Process Manager）

到目前為止，ChCore執行的進程都是由ChCore內核創建的Root thread。但是，更通用的操作系統應允許用戶態程序執行特定二進制文件。當操作系統執行給定的可執行二進制文件時，它應創建一個負責執行文件的新進程。 為此，ChCore提供了`spawn`的接口實現這一功能。

在這一部分中，我們將首先實現ChCore上的第一個用戶態系統服務進程：進程管理器，並且實現他的第一個功能：給定可執行二進制並創建一個新的進程執行該二進制，也即`spawn`。

### 進程管理器

在Linux中，創建新的進程並執行指定的二進制均由內核實現。ChCore作為微內核，儘可能將系統服務都移動到用戶態。這裡我們將實現第一個ChCore的系統服務：進程管理器。ChCore進程管理器負責創建用戶態進程，管理他們之間的關係，以及在進程退出後回收進程。

在實驗中，我們的進程管理器只負責其中一個功能，即創建新的線程。為了能夠讓用戶態的進程能夠使用該服務，我們首先需要支持**進程間通訊**（IPC）。本實驗的第四部分就是構建ChCore的進程間通訊。我們將在後續實驗再展示如何通過進程間通訊處理用戶程序的系統服務請求。

### Spawn功能

Spawn最終要實現功能是用戶給定一個二進制的路徑，其可以創建一個新的進程，執行該二進制，並返回新創建的進程的主線程cap以及進程的pid。由於到目前為止，實驗中還未實現文件系統服務，進程管理器還不能直接從文件系統中讀取二進制。這裡採取與內核創建第一個`Root thread`相似的方法，將本實驗需要執行的二進制一同放到`procm.srv`的二進制中，並使用`extern`符號的方法找到該二進制讀出來。因此本實驗的`spawn`暫時只支持特定二進制的啟動。具體代碼請閱讀`userland/servers/procm/spawn.c`。

為了讓ChCore運行的用戶態程序能夠連接到各系統服務器（例如本節實現的`procm`，以及後面實驗將實現的文件系統/網絡棧等），在`spawn`創建新的進程時，還需要將所有的系統服務器的`cap`均傳給該進程。在配置好該進程的所有參數之後，`spawn`將調用`launch_process`來創建進程。其基本工作流如下：

1. 使用`__chcore_sys_create_cap_group`創建一個子進程。
2. 如果有需要傳輸的初始cap（比如系統服務的cap，用於後續ipc調用系統服務），則傳輸這些cap。
3. 使用`__chcore_sys_create_pmo`來創建一個新的內存對象，用作主線程的棧，大小為`MAIN_THREAD_STACK_SIZE`。
4. 構建初始執行環境並寫入棧頂。
5. 將二進制elf中每個段以及棧映射到相應位置。這裡可以使用`chcore_pmo_map_multi`，其一次性把需要映射的pmo傳入內核映射。除了最基本的`cap`，`addr`和`perm`，這裡還有一個`free_cap`。其代表是否順帶將當前進程的`pmo`的`cap`釋放掉。由於是幫助新進程創建的`cap`，在映射後當前進程的`cap`無需保留，因此應該都將`free_cap`設置為`1`。
6. 創建新進程的主線程。

> 練習題 13：在`userland/servers/procm/launch.c`中填寫`launch_process`函數中缺少的代碼，完成本練習之後應運行`lab4.bin`應能看到有如下輸出：
>
> ```
> Hello from user.bin!
> ```
>
> **注意，本部分實驗將在`lab4.bin`的應用程序中進行。請自行修改`.config`文件，將啟動程序修改為`lab4.bin`。**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=lab4.bin
> ```
> 完成本練習後應能通過`spawn`測試，並獲得相應的5分。

## 第四部分：進程間通訊

在本部分，我們將實現ChCore的進程間通訊，從而允許跨地址空間的兩個進程可以使用IPC進行信息交換。

### ChCore進程間通訊概覽

![](./assets/IPC-overview.png)

ChCore的IPC接口不是傳統的`send/recv`接口。其更像客戶端/服務器模型，其中IPC請求接收者是服務器，而IPC請求發送者是客戶端。如圖所示，為了處理IPC，服務器（接收者）需要先註冊回調函數`ipc_dispatcher`。當客戶端（發送者）需要發送IPC請求的時候，其將使用`sys_ipc_call`切換到一個服務器專屬的線程並執行該回調函數處理該請求。而在該請求處理結束之後，將會調用`sys_ipc_return`回到調用IPC的客戶端（發送者）線程。

該服務器專屬的IPC處理線程為每一個IPC連接專屬，且屬於一種特殊的線程類型`TYPE_SHADOW`。不同於正常的用戶態線程`TYPE_USER`，這種類型的線程不再擁有**調度上下文**（Scheduling Context），也即不會主動被調度器調度到。其在客戶端註冊IPC連接的時候被創建，且只有在執行IPC的時候方能被調度到。為了實現該功能，該處理線程將在調用IPC的時候**繼承**IPC客戶端線程的調度上下文（即budget），從而能被調度器正確地調度。

### ChCore IPC具體流程

為了實現ChCore IPC的功能，首先需要在Client與Server端創建起一個一對一的IPC Connection。該Connection保存了IPC Server中處理IPC請求的線程（即圖中IPC handler Thread）、Client與Server的共享內存（用於存放IPC通訊的內容）。同一時刻，一個Connection只能有一個Client接入，並使用該Connection切換到Server的處理流程。ChCore提供了一系列機制，用於創建Connection以及創建每個Connection對應的Server處理線程。下面將以具體的IPC註冊到調用的流程，詳細介紹ChCore的IPC機制：

1. IPC服務器調用`ipc_register_server`（`libchcore/src/ipc/ipc.c`中）來註冊自己為IPC的服務器端。其主要包含以下內容：

   1. 構造IPC服務所需要的參數`ipc_vm_config`，其包括：

      - `stack_base_addr`：IPC服務線程的棧基地址
      - `stack_size`：服務線程棧的大小
      - `buf_base_addr`：IPC用於傳輸數據的共享內存基地址
      - `buf_size`：IPC共享內存大小

      ChCore的IPC支持同時多個不同的IPC客戶端連接服務器。處理這些Client的服務器線程明顯不能夠使用同一個棧以及共享內存。因此ChCore會賦予每一個不同的連接不同的`conn_idx`，並以此為索引來尋找對應的棧與共享內存。

   2. 調用ChCore提供的的系統調用：`sys_register_server`。該系統調用需要傳入三個參數，分別是用於處理IPC的例程`server_handler`（圖中對應`ipc_dispatcher`），支持連接的客戶端最大數量以及剛才構造的IPC服務器參數。服務例程`server_handler`接受兩個參數`ipc_msg`以及`pid`。其中`pid`為發起IPC的客戶端的PID，其用於區分不同的進程。

      ChCore內核中將使用`copy_from_user`從用戶態拷入的IPC服務器參數，並且構造一個bitmap用於記錄空閒的`conn_idx`（即`conn_bmp`）。

2. IPC客戶端調用`ipc_register_client`（`libchcore/src/ipc/ipc.c`中）來與給定服務器建立連接（connection）。其主要包含以下內容：

   1. 構建IPC客戶端的參數`ipc_vm_config`，其只需要以下兩個值：

      - `buf_base_addr`：當前客戶端的連接的IPC共享內存的基地址
      - `buf_size`：IPC共享內存的大小。

      同樣，這裡需要注意給不同的客戶端不同的`client_id`，確保不會用到同一塊的共享內存。

   2. 調用`sys_register_client`系統調用註冊連接。其會創建專屬於該連接的IPC處理線程，並且配置好IPC的共享內存。由於調用該接口時，服務器可能還未準備好（即執行`register_server`），因此可能會註冊失敗，此時返回`-EIPCRETRY`。這裡使用一個重試循環將其包裹。具體而言，該系統調用將執行以下步驟：

      1. 創建一個新的連接`connection`。
      2. 查詢bitmap分配一個新的`conn_idx`。
      3. 以此為index尋找合適的服務器配置（即棧與共享內存）。
      4. 創建對應的pmo，然後映射到對應的地址空間中。
      5. 將`connection`的`cap`賦予客戶端與服務器。

3. IPC客戶端調用`ipc_call`完成一次IPC通訊。

   在使用`ipc_call`之前，IPC客戶端需要使用`ipc_create_msg`來創建IPC信息（填metadata），然後使用`ipc_set_msg_data`以及`ipc_set_msg_cap`來設置需要傳輸的數據或cap。其本質就是在之前的共享內存中找到相應位置，然後把需要傳輸的數據拷貝過去。`ipc_set_msg_data`還會傳入一個`offset`參數，用於表示需要設置的數據在`ipc`數據中的偏移量。

   而`ipc_call`則直接調用系統調用`sys_ipc_call`。該系統調用將遷移到之前註冊的handler線程。具體而言，`sys_ipc_call`需要完成以下步驟。

   1. 判斷是否要傳遞cap。如果要傳遞，則需要使用`cap_copy`傳遞給server並設置好對應的`cap`。
   2. 調用`thread_migrate_to_server`配置好handler thread的上下文並切換到該shadow thread執行。此外，由於當前的客戶端線程需要等待IPC服務器線程處理完畢，因此需要更新其狀態為`TS_WAITING`，且不要加入等待隊列。

   `ipc_call`默認傳輸兩個參數給IPC服務器的處理線程，包括調用`ipc_call`時傳入的參數以及該線程所屬進程的`pid`。

4. IPC服務器的處理線程在處理完IPC請求之後使用`sys_ipc_return`系統調用返回。該系統調用也包含兩個參數，一個是返回值，另一個是server傳回的cap數量。與發送類似，如果有cap需要傳遞，則需要使用cap_copy傳回client並更新對應的cap。最後調用`thread_migrate_to_client`回到客戶端。

> 練習題 14：在`libchcore/src/ipc/ipc.c`與`kernel/ipc/connection.c`中實現了大多數IPC相關的代碼，請根據註釋完成其餘代碼。運行`lab4.bin`之後應能看到如下輸出：
>
> ```
> Hello from ChCore Process Manager!
> Hello from user.bin!
> Hello from ipc_client.bin!
> IPC test: connect to server 2
> IPC no data test .... Passed!
> IPC transfer data test .... Passed!
> IPC transfer cap test .... Passed!
> IPC transfer large data test .... Passed!
> 20 threads concurrent IPC test .... Passed!
> ```
>
> **注意，本部分實驗將在`lab4.bin`的應用程序中進行。請自行修改`.config`文件，將啟動程序修改為`lab4.bin`。**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=lab4.bin
> ```
>
> 完成本練習後應能夠通過所有ipc測試，包括`ipc no data`、`ipc data`、`ipc cap`、`ipc large data`、`ipc multiple`，並獲得25分。

## 第五部分：內核信號量

本實驗的最後一部分將實現一套線程等待（掛起）/喚醒機制。線程掛起需要調度器合作，因此操作系統內核需要提供新的原語輔助線程完成掛起，並在合適的時機喚醒該線程。因此，我們在ChCore內核中提供了一套信號量的機制，用於為上層應用提供掛起/喚醒的能力。

### 信號量回顧

信號量的本質是一個資源計數器，其提供兩個原語：`wait_sem`與`signal_sem`。`wait_sem`將消耗資源並將資源計數器減少；而`signal_sem`則代表生產資源，其將使資源計數器增加。如果當前計數器為0則代表沒有資源可供消耗，此時如果有線程調用`wait_sem`操作系統應當掛起當前線程，直到有其他的線程調用了`signal_sem`。

### 內核中實現信號量

為了能夠允許用戶態的應用程序使用操作系統內核中的信號量，我們需要提供三個新的系統調用，分別對應信號量的創建、wait操作與signal操作。

- `sys_create_sem()`：要求內核創建一個新的信號量，其返回該信號量的`cap`。
- `sys_wait_sem(int sem_cap, int is_block)`：等待在某一個信號量上，需要傳入等待的信號量的`cap`，並設定是否阻塞。如果`is_block`是1，則代表如果信號量不可用則掛起當前線程並等待。否則代表如果信號量無可用的資源時返回`-EAGAIN`。
- `sys_signal_sem(int sem_cap)`：喚醒等待在某一信號量上的線程。

在書中，我們介紹瞭如何使用條件變量實現信號量。而條件變量中最重要也是需要操作系統輔助實現的一部分是保證**原子的放鎖與阻塞（掛起）**。同樣的，如果我們需要在操作系統內核中實現信號量，其中最重要的一環是保證在檢查發現沒有可用的資源（即`sem->count == 0`）後並在真正掛起當前線程之前，不會有其他的線程調用`signal_sem`。也即保證檢查計數器到掛起兩個操作的原子性。不過，ChCore採用了大內核鎖。這代表所有的wait操作與signal操作都是互斥的，因此也保證了上述情況不會發生。

> 練習題 15：ChCore在`kernel/semaphore/semaphore.h`中定義了內核信號量的結構體，並在`kernel/semaphore/semaphore.c`中提供了創建信號量`init_sem`與信號量對應syscall的處理函數。請補齊`wait_sem`操作與`signal_sem`操作。
>
> 在完成後運行`test_sem.bin`應能看到如下輸出：
>
> ```
> Hello thread 2! Before delay!
> Hello thread 2! Before signal!
> Thread 2 return
> Hello thread 1! wait sem 6 return
> Thread 1 return
> ```
>
> **提示:**
> - 線程結構體中提供了`sem_queue_node`可以用於將該線程加入到`sem`的等待隊列
> - 使用之前調度器實現的接口可以實現掛起線程的功能。
>
> **注意，本部分實驗將在`test_sem.bin`的應用程序中進行。請自行修改`.config`文件，將啟動程序修改為`test_sem.bin`。**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=test_sem.bin
> ```
>
> 完成本練習應能通過`sem`測試，並獲得相應的5分。

### 生產者消費者

使用內核信號量可以用於實現生產者消費者問題，我們也將通過這個實驗檢測你內核信號量實現的正確與否。為了輔助實現生產者消費者問題，我們提供了線程安全的緩衝區`buf.c/h`。為了保證多生產者多消費者對緩衝操作的正確性，我們實現了`buffer_add_safe`與`buffer_remove_safe`，其用到了在用戶態的自旋鎖`spin.c/h`。除此之外，我們提供了用於生產者生產新的信息的方法`produce_new`，以及用於消費者消費新信息的方法`consume_msg`。

> 練習題 16：在`userland/apps/lab4/prodcons_impl.c`中實現`producer`和`consumer`。
>
>完成後運行`prodcons.bin`應能看到如下輸出：
>
>```
>Progress:0%==10%==20%==30%==40%==50%==60%==70%==80%==90%==100%
>Producer/Consumer Test Finish!
>```
>
>**注意，本部分實驗將在`prodcons.bin`的應用程序中進行。請自行修改`.config`文件，將啟動程序修改為`prodcons.bin`。**
>
>```
>CHCORE_ROOT_PROGRAM:STRING=prodcons.bin
>```
>
>完成本練習應能通過`prodcons`測試，並獲得相應的5分。

### 阻塞互斥鎖

本實驗的最後將使用**內核信號量**可以用於實現**用戶態**阻塞互斥鎖。阻塞互斥鎖在互斥鎖不空閒時會將當前線程掛起，當互斥鎖可用時再由鎖持有者喚醒。

> 練習題 17：請使用內核信號量實現阻塞互斥鎖，在`userland/apps/lab4/mutex.c`中填上`lock`與`unlock`的代碼。注意，這裡不能使用提供的`spinlock`。
>
> 完成後運行`test_mutex.bin`應能看到如下輸出：
>
> ```
> Begin Mutex Test!
> Global Count 1600
> test_mutex passed!
> ```
>
>
> **注意，本部分實驗將在`test_mutex.bin`的應用程序中進行。請自行修改`.config`文件，將啟動程序修改為`test_mutex.bin`。**
>
> ```
> CHCORE_ROOT_PROGRAM:STRING=test_mutex.bin
> ```
>
> 完成本練習應能通過`mutex`測試，並獲得相應的5分。
