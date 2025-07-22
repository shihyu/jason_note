# Lab1

- 思考題1：閱讀 `_start` 函數的開頭，嘗試說明 ChCore 是如何讓其中一個核首先進入初始化流程，並讓其他核暫停執行的。

  答：各個CPU首先從系統中取出`mpidr_el1`，其中`mpidr_el1`為各個CPU的序列號，經過出處理後，進入一個conditional branch。如果CPU的序列號等於0則跳轉到primary函數執行CPU初始化操作，若CPU的序列號不等於0則調用`b .`停留在原地，直到引入SMP



- 練習題 2：在 `arm64_elX_to_el1` 函數的 `LAB 1 TODO 1` 處填寫一行彙編代碼，獲取 CPU 當前異常級別。

  ```
  mrs x9, CurrentEL
  ```

  通過`mrs`指令將`CurrentEL`寄存器中的值讀入到x9寄存器中，在gdb中打印後輸出為12，是EL3的exception level。



- 練習題 3：在 `arm64_elX_to_el1` 函數的 `LAB 1 TODO 2` 處填寫大約 4 行彙編代碼，設置從 EL3 跳轉到 EL1 所需的 `elr_el3` 和 `spsr_el3` 寄存器值。具體地，我們需要在跳轉到 EL1 時暫時屏蔽所有中斷、並使用內核棧（`sp_el1` 寄存器指定的棧指針）。

  ```
  adr x9, .Ltarget
  msr elr_el3, x9
  mov x9, SPSR_ELX_DAIF | SPSR_ELX_EL1H
  msr spsr_el3, x9
  ```

  > 在這裡我們是在為eret做準備，eret調用後會使用`elr_el3`中的地址作為下一條指令的地址，同時將`spsr_el3`中保存的process state設置新的exception level中的process state

  1. 首先設置`elr_el3`的值。我們選擇將其設置為`.Ltarget`的地址，和EL2共享同一個出口

  2. 然後我們在`spsr_el3`中設置DAIF bits以關閉中斷，設置execution mode以進入el1(內核態)



- 思考題 4：結合此前 ICS 課的知識，並參考 `kernel.img` 的反彙編（通過 `aarch64-linux-gnu-objdump -S` 可獲得），說明為什麼要在進入 C 函數之前設置啟動棧。如果不設置，會發生什麼？

  答：因為C語言會有壓棧操作（參數傳遞、Callee-saved、Caller-saved, ret addr等）。如果不設置棧的話，則C語言壓棧相關的操作便無法正常執行，可能會發生程序崩潰。



- 思考題 5：在實驗 1 中，其實不調用 `clear_bss` 也不影響內核的執行，請思考不清理 `.bss` 段在之後的何種情況下會導致內核無法工作。

  答：在`.bss`段存儲的未被初始化全局變量和靜態變量若未執行`clear_bss`，則在後面使用時的初始值便不是0，這對一些假定全局變量和靜態變量的初始值為0的內核段代碼會是致命的錯誤。



- 練習題 6：在 `kernel/arch/aarch64/boot/raspi3/peripherals/uart.c` 中 `LAB 1 TODO 3` 處實現通過 UART 輸出字符串的邏輯。

  ```c++
  void uart_send_string(char *str)
  {
          /* LAB 1 TODO 3 BEGIN */
          early_uart_init();      // Initialize uart first
          int offset = 0;
          while (str[offset] != '\0') 
                  early_uart_send(str[offset++]);
          /* LAB 1 TODO 3 END */
  }
  ```

  首先調用`early_uart_init()`來初始化uart

  接著我們對字符串`str`中每一個字符調用`early_uart_send`函數，一個一個將字符輸出



- 練習題 7：在 `kernel/arch/aarch64/boot/raspi3/init/tools.S` 中 `LAB 1 TODO 4` 處填寫一行彙編代碼，以啟用 MMU。

  ```
  orr		x8, x8, #SCTLR_EL1_M
  ```

  仿照下方設置的格式，清除用`bic`指令，設置用`orr`指令。設置了`SCTLR_EL1_M`的位之後通過`msr`指令將設置好的位更新到`sctlr_el1`寄存器中

