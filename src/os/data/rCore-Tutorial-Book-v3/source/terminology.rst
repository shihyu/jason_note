術語中英文對照表
=========================

.. toctree::
   :hidden:
   :maxdepth: 4

第一章：RV64 裸機應用
----------------------------------

.. list-table:: 
   :align: center
   :header-rows: 1
   :widths: 40 60 30

   * - 中文
     - 英文
     - 出現章節
   * - 執行環境
     - Execution Environment
     - :ref:`應用程序運行環境與平臺支持 <term-execution-environment>`
   * - 系統調用
     - System Call
     - :ref:`應用程序運行環境與平臺支持 <term-system-call>`
   * - 指令集體系結構
     - ISA, Instruction Set Architecture
     - :ref:`應用程序運行環境與平臺支持 <term-isa>`
   * - 抽象
     - Abstraction
     - :ref:`應用程序運行環境與平臺支持 <term-abstraction>`
   * - 平臺
     - Platform
     - :ref:`應用程序運行環境與平臺支持 <term-platform>`
   * - 目標三元組
     - Target Triplet
     - :ref:`應用程序運行環境與平臺支持 <term-target-triplet>`
   * - 裸機平臺
     - Bare-Metal
     - :ref:`應用程序運行環境與平臺支持 <term-bare-metal>`
   * - 交叉編譯
     - Cross Compile
     - :ref:`移除標準庫依賴 <term-cross-compile>`
   * - 物理地址
     - Physical Address
     - :ref:`內核第一條指令（原理篇） <term-physical-address>`
   * - 物理內存
     - Physical Memory
     - :ref:`內核第一條指令（原理篇） <term-physical-memory>`
   * - 引導加載程序
     - Bootloader
     - :ref:`內核第一條指令（原理篇） <term-bootloader>`
   * - 控制流
     - Control Flow
     - :ref:`為內核支持函數調用 <term-control-flow>`
   * - 函數調用
     - Function Call
     - :ref:`為內核支持函數調用 <term-function-call>`
   * - 源寄存器
     - Source Register
     - :ref:`為內核支持函數調用 <term-source-register>`
   * - 立即數
     - Immediate
     - :ref:`為內核支持函數調用 <term-immediate>`
   * - 目標寄存器
     - Destination Register
     - :ref:`為內核支持函數調用 <term-destination-register>`
   * - 偽指令
     - Pseudo Instruction
     - :ref:`為內核支持函數調用 <term-pseudo-instruction>`
   * - 上下文
     - Context
     - :ref:`為內核支持函數調用 <term-context>`
   * - 活動記錄
     - Activation Record
     - :ref:`為內核支持函數調用<term-activation-record>`
   * - 保存/恢復
     - Save/Restore
     - :ref:`為內核支持函數調用 <term-save-restore>`
   * - 被調用者保存
     - Callee-Saved
     - :ref:`為內核支持函數調用 <term-callee-saved>`
   * - 調用者保存
     - Caller-Saved
     - :ref:`為內核支持函數調用 <term-caller-saved>`
   * - 開場白
     - Prologue
     - :ref:`為內核支持函數調用 <term-prologue>`
   * - 收場白
     - Epilogue
     - :ref:`為內核支持函數調用 <term-epilogue>`
   * - 調用規範
     - Calling Convention
     - :ref:`為內核支持函數調用 <term-calling-convention>`
   * - 棧/棧指針/棧幀
     - Stack/Stack Pointer/Stackframe
     - :ref:`為內核支持函數調用 <term-stack>`
   * - 後入先出
     - LIFO, Last In First Out
     - :ref:`為內核支持函數調用 <term-lifo>`
   * - 段
     - Section
     - :ref:`為內核支持函數調用 <term-section>`
   * - 內存佈局
     - Memory Layout
     - :ref:`為內核支持函數調用 <term-memory-layout>`
   * - 堆
     - Heap
     - :ref:`為內核支持函數調用 <term-heap>`
   * - 編譯器
     - Compiler
     - :ref:`為內核支持函數調用 <term-compiler>`
   * - 彙編器
     - Assembler
     - :ref:`為內核支持函數調用 <term-assembler>`
   * - 鏈接器
     - Linker
     - :ref:`為內核支持函數調用 <term-linker>`
   * - 目標文件
     - Object File
     - :ref:`為內核支持函數調用 <term-object-file>`
   * - 鏈接腳本
     - Linker Script
     - :ref:`為內核支持函數調用 <term-linker-script>`
   * - 可執行和鏈接格式
     - ELF, Executable and Linkable Format
     - :ref:`手動加載、運行應用程序 <term-elf>`
   * - 元數據
     - Metadata
     - :ref:`手動加載、運行應用程序 <term-metadata>`
   * - 魔數
     - Magic
     - :ref:`手動加載、運行應用程序 <term-magic>`
   * - 裸指針
     - Raw Pointer
     - :ref:`手動加載、運行應用程序 <term-raw-pointer>`
   * - 解引用
     - Dereference
     - :ref:`手動加載、運行應用程序 <term-dereference>`

第二章：批處理系統
-------------------------

.. list-table:: 
   :align: center
   :header-rows: 1
   :widths: 40 60 30

   * - 中文
     - 英文
     - 出現章節
   * - 批處理系統
     - Batch System
     - :ref:`引言 <term-batch-system>`
   * - 特權級
     - Privilege
     - :ref:`引言 <term-privilege>`
   * - 監督模式執行環境
     - SEE, Supervisor Execution Environment
     - :ref:`RISC-V 特權級架構 <term-see>`
   * - 異常控制流
     - ECF, Exception Control Flow
     - :ref:`RISC-V 特權級架構 <term-ecf>`
   * - 陷入
     - Trap
     - :ref:`RISC-V 特權級架構 <term-trap>`
   * - 異常
     - Exception
     - :ref:`RISC-V 特權級架構 <term-exception>`
   * - 執行環境調用
     - Environment Call
     - :ref:`RISC-V 特權級架構 <term-environment-call>`
   * - 監督模式二進制接口
     - SBI, Supervisor Binary Interface
     - :ref:`RISC-V 特權級架構 <term-sbi>`
   * - 應用程序二進制接口
     - ABI, Application Binary Interface
     - :ref:`RISC-V 特權級架構 <term-abi>`
   * - 控制狀態寄存器
     - CSR, Control and Status Register
     - :ref:`RISC-V 特權級架構 <term-csr>`
   * - 胖指針
     - Fat Pointer
     - :ref:`實現應用程序 <term-fat-pointer>`
   * - 內部可變性
     - Interior Mutability
     - :ref:`實現應用程序 <term-interior-mutability>`
   * - 指令緩存
     - i-cache, Instruction Cache
     - :ref:`實現批處理系統 <term-icache>`
   * - 數據緩存
     - d-cache, Data Cache
     - :ref:`實現批處理系統 <term-dcache>`
   * - 原子指令
     - Atomic Instruction
     - :ref:`處理 Trap <term-atomic-instruction>`
   
第三章：多道程序與分時多任務
----------------------------------------------------------------------------

.. list-table:: 
   :align: center
   :header-rows: 1
   :widths: 40 60 30

   * - 中文
     - 英文
     - 出現章節
   * - 多道程序
     - Multiprogramming
     - :ref:`引言 <term-multiprogramming>`   
   * - 分時多任務系統
     - Time-Sharing Multitasking
     - :ref:`引言 <term-time-sharing-multitasking>`
   * - 任務上下文
     - Task Context
     - :ref:`任務切換 <term-task-context>`
   * - 輸入/輸出
     - I/O, Input/Output
     - :ref:`多道程序與協作式調度 <term-input-output>`
   * - 任務控制塊
     - Task Control Block
     - :ref:`多道程序與協作式調度 <term-task-control-block>`
   * - 吞吐量
     - Throughput
     - :ref:`分時多任務系統與搶佔式調度 <term-throughput>`
   * - 後臺應用
     - Background Application
     - :ref:`分時多任務系統與搶佔式調度 <term-background-application>`
   * - 交互式應用
     - Interactive Application
     - :ref:`分時多任務系統與搶佔式調度 <term-interactive-application>`
   * - 協作式調度
     - Cooperative Scheduling
     - :ref:`分時多任務系統與搶佔式調度 <term-cooperative-scheduling>`
   * - 時間片
     - Time Slice
     - :ref:`分時多任務系統與搶佔式調度 <term-time-slice>`
   * - 公平性
     - Fairness
     - :ref:`分時多任務系統與搶佔式調度 <term-fairness>`
   * - 時間片輪轉算法
     - RR, Round-Robin
     - :ref:`分時多任務系統與搶佔式調度 <term-round-robin>`
   * - 中斷
     - Interrupt
     - :ref:`分時多任務系統與搶佔式調度 <term-interrupt>`
   * - 同步
     - Synchronous
     - :ref:`分時多任務系統與搶佔式調度 <term-sync>`
   * - 異步
     - Asynchronous
     - :ref:`分時多任務系統與搶佔式調度 <term-async>`
   * - 並行
     - Parallel
     - :ref:`分時多任務系統與搶佔式調度 <term-parallel>`
   * - 軟件中斷
     - Software Interrupt
     - :ref:`分時多任務系統與搶佔式調度 <term-software-interrupt>`
   * - 時鐘中斷
     - Timer Interrupt
     - :ref:`分時多任務系統與搶佔式調度 <term-timer-interrupt>`
   * - 外部中斷
     - External Interrupt
     - :ref:`分時多任務系統與搶佔式調度 <term-external-interrupt>`
   * - 嵌套中斷
     - Nested Interrupt
     - :ref:`分時多任務系統與搶佔式調度 <term-nested-interrupt>`
   * - 輪詢
     - Busy Loop
     - :ref:`分時多任務系統與搶佔式調度 <term-busy-loop>`
     
第四章：地址空間
-------------------------------------------

.. list-table:: 
   :align: center
   :header-rows: 1
   :widths: 40 60 30

   * - 中文
     - 英文
     - 出現章節
   * - 幻象
     - Illusion
     - :ref:`引言 <term-illusion>`
   * - 時分複用
     - TDM, Time-Division Multiplexing
     - :ref:`引言 <term-time-division-multiplexing>`
   * - 地址空間
     - Address Space
     - :ref:`地址空間 <term-address-space>`
   * - 虛擬地址
     - Virtual Address
     - :ref:`地址空間 <term-virtual-address>`
   * - 內存管理單元
     - MMU, Memory Management Unit
     - :ref:`地址空間 <term-mmu>`
   * - 地址轉換
     - Address Translation
     - :ref:`地址空間 <term-address-translation>`
   * - 插槽
     - Slot
     - :ref:`地址空間 <term-slot>`
   * - 位圖
     - Bitmap
     - :ref:`地址空間 <term-bitmap>`
   * - 內碎片
     - Internal Fragment
     - :ref:`地址空間 <term-internal-fragment>`
   * - 外碎片
     - External Fragment
     - :ref:`地址空間 <term-external-fragment>`
   * - 頁面
     - Page
     - :ref:`地址空間 <term-page>`
   * - 虛擬頁號
     - VPN, Virtual Page Number
     - :ref:`地址空間 <term-virtual-page-number>`
   * - 物理頁號
     - PPN, Physical Page Number
     - :ref:`地址空間 <term-physical-page-number>`
   * - 頁表
     - Page Table
     - :ref:`地址空間 <term-page-table>`
   * - 靜態分配
     - Static Allocation
     - :ref:`Rust 中的動態內存分配 <term-static-allocation>`
   * - 動態分配
     - Dynamic Allocation
     - :ref:`Rust 中的動態內存分配 <term-dynamic-allocation>`
   * - 智能指針
     - Smart Pointer
     - :ref:`Rust 中的動態內存分配 <term-smart-pointer>`
   * - 集合
     - Collection
     - :ref:`Rust 中的動態內存分配 <term-collection>`
   * - 容器
     - Container
     - :ref:`Rust 中的動態內存分配 <term-container>`
   * - 借用檢查
     - Borrow Check
     - :ref:`Rust 中的動態內存分配 <term-borrow-check>`
   * - 引用計數
     - Reference Counting
     - :ref:`Rust 中的動態內存分配 <term-reference-counting>`
   * - 垃圾回收
     - GC, Garbage Collection
     - :ref:`Rust 中的動態內存分配 <term-garbage-collection>`
   * - 資源獲取即初始化
     - RAII, Resource Acquisition Is Initialization
     - :ref:`Rust 中的動態內存分配 <term-raii>`
   * - 頁內偏移
     - Page Offset
     - :ref:`實現 SV39 多級頁表機制（上） <term-page-offset>`
   * - 類型轉換
     - Type Conversion
     - :ref:`實現 SV39 多級頁表機制（上） <term-type-conversion>`
   * - 字典樹
     - Trie
     - :ref:`實現 SV39 多級頁表機制（上） <term-trie>`
   * - 多級頁表
     - Multi-Level Page Table
     - :ref:`實現 SV39 多級頁表機制（上） <term-multi-level-page-table>`
   * - 頁索引
     - Page Index
     - :ref:`實現 SV39 多級頁表機制（上） <term-page-index>`
   * - 大頁
     - Huge Page
     - :ref:`實現 SV39 多級頁表機制（上） <term-huge-page>`
   * - 恆等映射
     - Identical Mapping
     - :ref:`實現 SV39 多級頁表機制（下） <term-identical-mapping>`
   * - 頁表自映射
     - Recursive Mapping
     - :ref:`實現 SV39 多級頁表機制（下） <term-recursive-mapping>`
   * - 跳板
     - Trampoline
     - :ref:`內核與應用的地址空間 <term-trampoline>`
   * - 隔離
     - Isolation
     - :ref:`內核與應用的地址空間 <term-isolation>`
   * - 保護頁面
     - Guard Page
     - :ref:`內核與應用的地址空間 <term-guard-page>`
   * - 快表
     - Translation Lookaside Buffer
     - :ref:`基於地址空間的分時多任務 <term-tlb>`
   * - 熔斷
     - Meltdown
     - :ref:`基於地址空間的分時多任務 <term-meltdown>`
    
  
    