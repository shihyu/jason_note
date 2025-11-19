---
marp: true
theme: default
paginate: true
_paginate: false
header: ''
footer: ''
backgroundColor: white
---

<!-- theme: gaia -->
<!-- _class: lead -->

# 第七講 進程管理與單處理器調度
### 第四節 實踐：支持進程的操作系統

Process OS(POS)

<br>
<br>

向勇 陳渝 李國良 

2022年秋季

---

**提綱**

### 1. 實驗目標和步驟
- 實驗目標
- 實踐步驟
2. 代碼結構
3. 應用程序設計
4. 內核程序設計

![bg right:57% 100%](figs/process-os-detail.png)

---

#### 以往目標

提高性能、簡化開發、加強安全
- Address Space OS
    - APP不用考慮運行時的起始執行地址，隔離APP訪問的地址空間
- multiprog & time-sharing
    - 讓APP有效共享CPU，提高系統總體性能和效率
- BatchOS: 讓APP與OS隔離，加強系統安全，提高執行效率
- LibOS: 讓APP與HW隔離，簡化應用訪問硬件的難度和複雜性

---

#### 實驗目標

增強進程管理和資源管理、提高性能、簡化開發、加強安全

- 整合之前的特權級、地址空間、任務，形成進程
- 進程成為資源的擁有者
- 擴展進程動態特徵，能夠在應用層面發出如下系統調用請求：
   - 動態創建子進程
   - 動態構造新進程
   - 子進程退出/父進程等待子進程退出

---

#### 實驗要求

- 理解進程概念
- 理解進程的動態管理機制的設計與實現
- 初步認識進程調度
- 掌握shell應用的編寫與使用
- 會寫支持進程的操作系統

<!-- 智商最高的白堊紀“傷齒龍” 操作系統 troodon -->

![bg right 80%](figs/troodon.png)



---

#### 總體思路

![bg right:76% 90%](figs/process-os-detail.png)


---

#### 總體思路

![bg right:76% 85%](figs/process-os-key-structures.png)

---

#### 總體思路

- 編譯：應用程序和內核獨立編譯，合併為一個鏡像
- 編譯：不同應用程序可採用統一的起始地址
- 構造：系統調用服務，**進程的管理與初始化**
- 構造：建立基於頁表機制的虛存空間
- 運行：特權級切換，進程與OS相互切換
- 運行：切換地址空間，跨地址空間訪問數據


---
#### 歷史背景
- 1965：描述未來的 MULTICS 操作系統
  - MIT 的 Fernando J. Corbató 教授牽頭
  - 參與單位：MIT, GE(通用電氣公司), AT&T Bell Labs
  - 提出了**進程的動態管理思想**，啟發和造就了UNIX
- 1971：Thompson shell 
  - 由Ken Thompson寫的第一個**UNIX Shell**
  - 按照極簡主義設計，語法非常簡單，是一個簡單的命令行解釋器
  - 它的許多特徵影響了以後的操作系統命令行界面的發展
---

#### 實踐步驟
```
git clone https://github.com/rcore-os/rCore-Tutorial-v3.git
cd rCore-Tutorial-v3
git checkout ch5
cd os
make run
```

---
#### 實踐步驟
```
[RustSBI output]
...
yield
**************/
Rust user shell
>>
```
操作系統啟動``shell``後，用戶可以在``shell``中通過敲入應用名字來執行應用。


---

#### 軟件架構

- 管理進程
    - 創建
    - 回收
    - fork
    - exec
  
![bg right:74% 90%](figs/process-os-detail.png)

---

**提綱**

1. 實驗目標和步驟
### 2. 代碼結構
3. 應用程序設計
4. 內核程序設計

![bg right:65% 100%](figs/process-os-detail.png)

---

#### 改進OS
```
├── os
    ├── build.rs(修改：基於應用名的應用構建器)
    └── src
         ├── loader.rs(修改：基於應用名的應用加載器)
         ├── main.rs(修改)
         ├── mm(修改：為了支持本章的系統調用對此模塊做若干增強)
```

---

#### 改進OS
```
├── os
    └── src
         ├── syscall
             ├──fs.rs(修改：新增 sys_read)
             ├── mod.rs(修改：新的系統調用的分發處理)
             └── process.rs（修改：新增 sys_getpid/fork/exec/waitpid）
         ├── task
             ├── manager.rs(新增：任務管理器，為上一章任務管理器功能的一部分)
             ├── mod.rs(修改：調整原來的接口實現以支持進程)
             ├── pid.rs(新增：進程標識符和內核棧的 Rust 抽象)
             ├── processor.rs(新增：處理器管理結構 ``Processor`` ，為上一章任務管理器功能的一部分)
             └── task.rs(修改：支持進程管理機制的任務控制塊)
         └── trap
              ├── mod.rs(修改：對於系統調用的實現進行修改以支持進程系統調用)
```


---

**提綱**

1. 實驗目標和步驟
2. 代碼結構
### 3. 應用程序設計
4. 內核程序設計

![bg right:63% 90%](figs/process-os-detail.png)

---

#### 理解進程

- 應用角度
    - **進程** 是正在執行的應用
  
- OS角度
    -  **進程** 是應用在其地址空間上的一次執行過程
       - 進程擁有資源，操作系統根據進程的執行狀態管理其資源 
![bg right:50% 100%](figs/seg-addr-space.png)

---

#### 進程管理系統調用

```
/// 功能：當前進程 fork 出來一個子進程。
/// 返回值：對於子進程返回 0，對於當前進程則返回子進程的 PID
/// syscall ID：220
pub fn sys_fork() -> isize;
```
```
/// 功能：將當前進程的地址空間清空並加載一個特定的可執行文件，返回用戶態後開始它的執行。
/// 參數：path 給出了要加載的可執行文件的名字；
/// 返回值：如果出錯的話（如找不到名字相符的可執行文件）則返回 -1，否則不應該返回。
/// syscall ID：221
pub fn sys_exec(path: &str) -> isize;
```
<!-- ![bg right:50% 100%](figs/app-as-full.png) -->



---

#### 進程管理系統調用

```
/// 功能：當前進程等待一個子進程變為殭屍進程，回收其全部資源並收集其返回值。
/// 參數：pid 表示要等待的子進程的進程 ID，如果為 -1 的話表示等待任意一個子進程；
/// exit_code 表示保存子進程返回值的地址，如果這個地址為 0 的話表示不必保存。
/// 返回值：如果要等待的子進程不存在則返回 -1；否則如果要等待的子進程均未結束則返回 -2；
/// 否則返回結束的子進程的進程 ID。
/// syscall ID：260
pub fn sys_waitpid(pid: isize, exit_code: *mut i32) -> isize;
```


---

#### 應用``shell``的執行流程
1. 通過``sys_read``獲取字符串（即文件名）
2. 通過``sys_fork``創建子進程
3. 在子進程中通過``sys_exec``創建新應用的進程
4. 在父進程中通過``sys_waitpid``等待子進程結束
5. 跳轉到第一步循環執行

---

**提綱**

1. 實驗目標和步驟
2. 代碼結構
3. 應用程序設計
### 4. 內核程序設計
- 應用的鏈接與加載支持
- 核心數據結構
- 進程管理機制實現

![bg right:57% 90%](figs/process-os-detail.png)

---

#### 應用的鏈接與加載支持

在編譯操作系統的過程中，會生成如下的 link_app.S 文件
```
 3 _num_app:
 4     .quad 15            #應用程序個數
 7 ......
 9 _app_names:             #app0的名字
10     .string "exit"          
12 ......
17 app_0_start:            #app0的開始位置
18     .incbin "../user/target/riscv64gc-unknown-none-elf/release/exit"
19 app_0_end:              #app0的結束位置
```


---

#### 基於應用名的應用加載

在加載器 loader.rs 中，分析 link_app.S 中的內容，並用一個全局可見的 **只讀** 向量 ``APP_NAMES`` 來按照順序將所有應用的名字保存在內存中，為通過 exec 系統調用創建新進程做好了前期準備。


---

**提綱**

1. 實驗目標和步驟
2. 代碼結構
3. 應用程序設計
4. 內核程序設計
- 應用的鏈接與加載支持
### 核心數據結構
- 進程管理機制實現

![bg right:57% 100%](figs/process-os-detail.png)

---

#### 核心數據結構間的關係

![bg right:70% 100%](figs/process-os-key-structures.png)

---

#### 進程控制塊TCB

進程抽象的對應實現是進程控制塊 -- TCB  ``TaskControlBlock``
```rust
pub struct TaskControlBlock {
    // immutable
    pub pid: PidHandle,                      // 進程id
    pub kernel_stack: KernelStack,           // 進程內核棧
    // mutable
    inner: UPSafeCell<TaskControlBlockInner>,//進程內部管理信息
}
```



---

#### 進程控制塊TCB

進程抽象的對應實現是進程控制塊 -- TCB  ``TaskControlBlock``
```rust
pub struct TaskControlBlockInner {
    pub trap_cx_ppn: PhysPageNum,               // 陷入上下文頁的物理頁號
    pub base_size: usize,                       // 進程的用戶棧頂
    pub task_cx: TaskContext,                   // 進程上下文
    pub task_status: TaskStatus,                // 進程執行狀態  
    pub memory_set: MemorySet,                  // 進程地址空間
    pub parent: Option<Weak<TaskControlBlock>>, // 父進程控制塊
    pub children: Vec<Arc<TaskControlBlock>>,   // 子進程任務控制塊組
    pub exit_code: i32,                         // 退出碼
}
```

---

#### 進程管理器``TaskManager``

- 任務管理器自身僅負責管理所有就緒的進程

```rust
pub struct TaskManager {
    ready_queue: VecDeque<Arc<TaskControlBlock>>,  // 就緒態任務控制塊的鏈表
}
```

---

#### 處理器管理結構

處理器管理結構 ``Processor`` 描述CPU 執行狀態
```rust
pub struct Processor {
    current: Option<Arc<TaskControlBlock>>, // 在當前處理器上正在執行的任務
    idle_task_cx: TaskContext,              // 空閒任務
}
```
- 負責從任務管理器 `TaskManager` 中分出去的維護 CPU 狀態的職責
- 維護在一個處理器上正在執行的任務，可以查看它的信息或是對它進行替換
- `Processor` 有一個 idle 控制流，功能是嘗試從任務管理器中選出一個任務來在當前 CPU 核上執行，有自己的CPU啟動內核棧上



---

**提綱**

1. 實驗目標和步驟
2. 代碼結構
3. 應用程序設計
4. 內核程序設計
- 應用的鏈接與加載支持
- 核心數據結構
### 進程管理機制實現

![bg right:55% 100%](figs/process-os-detail.png)

---

#### 進程管理機制實現概述

1. 創建初始進程：創建第一個用戶態進程 `initproc`
2. 進程生成機制：介紹進程相關的系統調用 `sys_fork`/`sys_exec` 
3. 進程調度機制：進程主動/被動切換
4. 進程資源回收機制：調用` sys_exit` 退出或進程終止後保存其退出碼
5. 進程資源回收機制：父進程通過 `sys_waitpid` 收集該進程的信息並回收其資源
6. 字符輸入機制：通過`sys_read` 系統調用獲得字符輸入


---

#### 創建初始進程

```rust
lazy_static! {
    pub static ref INITPROC: Arc<TaskControlBlock> = Arc::new(
        TaskControlBlock::new(get_app_data_by_name("initproc").unwrap()));
}
pub fn add_initproc() {
    add_task(INITPROC.clone());
}
```
- `TaskControlBlock::new` 會解析`initproc`的ELF執行文件格式，並建立應用的地址空間、內核棧等，形成一個就緒的進程控制塊
- `add_task`會把進程控制塊加入就緒隊列中



---

#### 創建新進程`fork()`

複製父進程內容並構造新的進程控制塊

```rust
pub fn fork(self: &Arc<TaskControlBlock>) -> Arc<TaskControlBlock> {...}
```
-  建立新頁表，複製父進程地址空間的內容
-  創建新的陷入上下文
-  創建新的應用內核棧
-  創建任務上下文
-  建立父子關係
-  設置`0`為`fork`返回碼

---

#### 加載新應用`exec()`

用新應用的 ELF 可執行文件中的代碼和數據替換原有的應用地址空間中的內容

```rust
pub fn exec(&self, elf_data: &[u8]) {...}
```
- 回收已有應用地址空間，基於ELF 文件的全新的地址空間直接替換已有應用地址空間
- 修改進程控制塊的 Trap 上下文，將解析得到的應用入口點、用戶棧位置以及一些內核的信息進行初始化


---

#### 進程調度機制

暫停當前任務並切換到下一個任務

- 時機
   - `sys_yield`系統調用時
   - 進程的時間片用完時
- 操作
   - 執行`suspend_current_and_run_next` 函數
      - 取出當前正在執行的任務，修改其狀態，放入就緒隊列隊尾
      - 接著調用 schedule 函數來觸發調度並切換任務

---

#### 進程資源回收機制

進程退出`exit_current_and_run_next` 
- 當前進程控制塊從``PROCESSOR``中取出，修改其為殭屍進程
- 退出碼 `exit_code `寫入進程控制塊中
- 把所有子進程掛到`initproc`的子進程集合中
- 釋放應用地址空間
- 接著調用 schedule 函數來觸發調度並切換任務


---

#### 進程資源回收機制

等待子進程退出`sys_waitpid`

- 不存在進程 ID 為 pid（pid==-1 或 > 0）的子進程時，返回 -1
- 存在進程 ID 為 pid 的殭屍子進程時，正常回收子進程，返回子進程pid，更新退出碼參數為 exit_code 
- 子進程還沒退出時，返回 -2，用戶庫看到是 -2 後，就進一步調用 sys_yield 系統調用，讓父進程進入等待狀態
- 返回前，釋放子進程的進程控制塊

---

#### 字符輸入機制

```rust
pub fn sys_read(fd: usize, buf: *const u8, len: usize) -> isize {
   c=sbi::console_getchar(); ...}
  
```
- 目前僅支持每次只能讀入一個字符
- 調用 sbi 子模塊提供的從鍵盤獲取輸入的接口 `console_getchar` 

---
#### 支持進程的操作系統POS
- 進程概念與進程實現的關係
- 進程管理機制
- 基本調度機制
- 能寫傷齒龍OS
![bg right 70%](figs/troodon.png)

---

### 小結

**提綱**

1. 實驗目標和步驟
2. 代碼結構
3. 應用程序設計
4. 內核程序設計
- 應用的鏈接與加載支持
- 核心數據結構
- 進程管理機制實現

![bg right:57% 100%](figs/process-os-detail.png)

