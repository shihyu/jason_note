# 已有教學素材收集

* [v1](https://github.com/LearningOS/os-lectures/blob/57187673ab9e28379108a50808c53d26ea88f2b2/lecture03/ref.md)
* [v2](https://github.com/LearningOS/os-lectures/blob/8dc5af59fb5f79fef2d9ee26915863648a3da9af/lecture03/ref.md)
* v3

## 第3講 進程與調度
### 參考

實驗文檔-[第二章實現批處理系統](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter2/3batch-system.html#id1)

[第三章多道程序與分時多任務](https://rcore-os.github.io/rCore-Tutorial-Book-v3/chapter3/index.html)

### 3.1 進程概念

進程的概念（9.1 進程的概念[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture09)、[幻燈片]()）
進程控制塊（9.2 進程控制塊：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2018spring/lecture11?action=AttachFile&do=get&target=20180402-11-2-進程控制塊.pptx)）
進程狀態（9.3 進程狀態：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture11?action=AttachFile&do=get&target=11-3-進程狀態.pptx)）
三狀態進程模型（9.4 三狀態進程模型：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture11?action=AttachFile&do=get&target=11-4-三狀態進程模型.pptx)）

### 3.2 進程調度

處理機調度概念（11.1 處理機調度概念[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture11)、[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture15?action=AttachFile&do=get&target=15-1.pptx)）

協作式調度與搶佔式調度
 * 協作式調度：主動釋放處理器
 * 搶佔式調度：通過時鐘中斷來強制打斷一個程序的執行

先來先服務調度算法（11.3 先來先服務：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture15?action=AttachFile&do=get&target=15-3.pptx)）
時間片輪轉調度算法（11.4 時間片輪轉：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture15?action=AttachFile&do=get&target=15-4.pptx)）

### 3.3 進程切換與管理（switch/fork/exec/wait/exit）

進程切換（12.1 進程切換：[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture10)、[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture12?action=AttachFile&do=get&target=12-1.pptx)）：

* 不同類型的上下文與切換：函數調用與返回；系統調用和返回；進程切換；
* 切換位置的要求：調用方；用戶進程的可選位置；用戶態的任意位置，內核的指定位置；

進程創建（12.2 進程創建：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture12?action=AttachFile&do=get&target=12-2.pptx)）
進程退出（12.4 進程等待與退出：[PPT講義](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture12?action=AttachFile&do=get&target=12-4.pptx)）

### 3.4 同步互斥與進程間通信

進程同步（13.1 背景[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture13)、[幻燈片](os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture17?action=AttachFile&do=get&target=17-1%E8%83%8C%E6%99%AF.pptx)）

信號量的基本概念（14.1 信號量[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture14)、[幻燈片](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture14?action=AttachFile&do=view&target=20200402-18-1.pptx)）

進程通信（16.1 進程通信概念[wiki](https://os.cs.tsinghua.edu.cn/oscourse/OS2020spring/lecture16)、[幻燈片](os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture20?action=AttachFile&do=get&target=20-5.pptx)）
管道（16.2 信號和管道[幻燈片](http://os.cs.tsinghua.edu.cn/oscourse/OS2015/lecture20?action=AttachFile&do=get&target=20-6.pptx)）

### 3.5 教學實驗：分時多任務系統

#### 系統調用：中斷上下文保存與恢復

`TrapContext` [結構體](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/trap/context.rs#L4)

`__alltraps` 的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/trap/trap.S#L12)

上下文恢復的 `__restore` 的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/trap/trap.S#L40)

#### 任務切換：任務上下文(Task Context)

![task_context](/Users/xyong/github/os-lectures/lecture03/figs/task_context.png)

 `TaskContext` [數據結構](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/task/context.rs#L2)

#### 進程切換過程

![switch](/Users/xyong/github/os-lectures/lecture03/figs/switch.png)

`__switch` 的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/task/switch.S#L10)

#### 進程切換的實現

如何進入用戶態第一次執行應用程序？

 `run_next_app` [函數](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch2/os/src/batch.rs#L116)

 `app_init_context` [函數](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch2/os/src/trap/context.rs#L12)

#### 多道批處理系統中的程序加載

 `load_apps` [函數](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/loader.rs#L55)

#### 進程管理：任務運行狀態

簡單的進程控制塊數據結構和三狀態進程模型

![fsm-coop](/Users/xyong/github/os-lectures/lecture03/figs/fsm-coop.png)

```TaskStatus```[數據結構](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/task/task.rs#L13)

#### 進程管理：任務控制塊

**任務控制塊** (Task Control Block)：```TaskControlBlock``` [數據結構](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3-coop/os/src/task/task.rs#L1)

#### 協作式調度：主動讓出CPU

主動調用`sys_yield` 來交出 CPU 使用權。

![multiprogramming](/Users/xyong/github/os-lectures/lecture03/figs/multiprogramming.png)

#### sys_yield 和 sys_exit

 `sys_yield` [系統調用](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/user/src/syscall.rs#L27)

```sys_yield```的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/syscall/process.rs#L13)

```sys_exit```的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/syscall/process.rs#L7)

#### 第一次進入用戶態

多進程下的第一次進入用戶態；

 `init_app_cx` 的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/loader.rs#L82)

 `task::run_first_task` 的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/task/mod.rs#L48)

```task::run_next_task```的[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/task/mod.rs#L82)

#### 搶佔式調度

`timer` [模塊](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/timer.rs#L12)

`suspend_current_and_run_next` 的[引用](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/trap/mod.rs#L53)和[實現](https://github.com/rcore-os/rCore-Tutorial-v3/blob/ch3/os/src/task/mod.rs#L119)


