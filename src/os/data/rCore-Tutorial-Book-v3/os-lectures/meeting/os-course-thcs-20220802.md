---
marp: true
theme: default
paginate: true
_paginate: false
header: ''
footer: ''
backgroundColor: white
style: @import url('https://unpkg.com/tailwindcss@^2/dist/utilities.min.css');

---

<!-- theme: gaia -->
<!-- _class: lead -->

# 操作系統課程建設的分析與實踐探索


<br>

陳渝 向勇  李國良 任炬

<br>

2022年8月2日

<br>

人才培養與核心課程建設研討會  

---
### 報告內容
- 背景介紹
   - 歷史
   - 當前基本情況  
- 課程建設
   - 目標+策略
   - 基本思路
   - 具體實施
---
### 背景介紹
清華大學相關院系的操作系統課程

![w:800](./figs/os-course-in-tsinghua.png)


---
### 背景介紹 -- 歷史

**鐵打的課程，流水的老師**

時間 | 任課老師 | 教材 | 實驗 
---------|----------|--------- |----------
 1997前 | 史美林 張堯學 伍尚廣 | 計算機操作系統 |  /
 1998 | 向勇 | 無固定教材 |  Nachos MIPS
 2008~2017 | 向勇 陳渝 | 無固定教材 |  uCore x86
 2018~至今 | 向勇 陳渝 李國良 | 無固定教材 |  uCore/rCore RISC-V



---
### 背景介紹 -- 歷史

**鐵打的課程，流水的老師**


- 任課老師：李國良(2021)、任炬(2023)
- 相關課程：
   - 大四本科：操作系統專題訓練（2008年開始）  
   - 研究生：高級操作系統（2009開始）
   - MOOC：學堂在線（2015年開始）

---
### 背景介紹 -- 當前基本情況
<div class="grid grid-cols-2 gap-4">
<div>

基本情況
- 特徵：計算機專業課 必修
- 時間：春季/秋季（48學時）
- 學分：3學分
- 教師：向勇 陳渝 李國良 任炬
- 學生：大三（部分大一/二/四）
- 有實驗內容（不算課時）
- 無指定教材/有參考教材

</div>
<div>

課程目標
- 掌握OS的基本原理和設計思路
- 掌握OS機制的實現技術
- 理解計算機軟硬件系統


先修課
- 程序設計+編程語言
- 數據結構+算法
- 計算機組成原理+編譯原理


</div>
</div>

---
### 背景介紹 -- 當前基本情況
學生反饋
- 太難，量太大，不會編程
- 覺得時間投入太大
- 部分同學為了學分而學
- 趣味性不足，缺少及時反饋
- 碰到問題難以及時獲得幫助
- 就業並不看好
 

![bg right 60%](./figs/study-os.png)

---
### 背景介紹 -- 當前基本情況
參考教材
- **Operating Systems: Three Easy Pieces**, Remzi H. Arpaci-Dusseau and Andrea C. Arpaci-Dusseau
- **Operating system concepts**,Abraham Silberschatz, Peter Baer Galvin,Greg Gagne
- **Operating Systems: Internals and Design Principles**,William Stallings,
- [rCore-Tutorial-Book, 清華OS課程教學組](http://rcore-os.cn/rCore-Tutorial-Book-v3/)
---
### 背景介紹 -- 當前基本情況 -- 教學大綱
特點：粗看：**幾十年基本不變**
* 操作系統結構
* 中斷及系統調用
* 內存管理
* 進程管理
* 處理機調度
* 同步互斥
* 文件系統

![bg right 100%](../lec1/figs/ucorearch.png)

---
### 背景介紹 -- 當前基本情況 -- 教學內容
特點：**基本抽象（骨）大致不變，內容與實驗（肉）一直在變化**

**骨** -- 基本抽象：進程、地址空間、文件
**肉** -- 方法技術：調度、頁表、文件系統、同步互斥、指令集、配套實驗設計...

![bg right 100%](./figs/os-labs-choice.png)

---
### 背景介紹 -- 當前基本情況 -- 教學內容
特點：**基本（骨）不變，內容（肉）在變化** -- 骨架子大，沒太多肉
- 1995年前，缺少對實際操作系統的分析
   - 學生感覺像說教類課，把背誦記憶作為主要學習手段
   - 幾乎沒有實踐：只能說

---
### 背景介紹 -- 當前基本情況 -- 教學內容
特點：**基本（骨）不變，內容（肉）在變化** -- 骨頭撐不起肉
- 2000~2007年，增加了對實際操作系統（Windows、Linux、Solaris）的分析
  - 學生感覺是霧裡看花，只可遠觀，不過細品
  - 遠看很漂亮，近看太複雜
  - 有一些實踐：側重用戶態編程或模擬抽象環節下的編程
  - Nachos實驗展示的OS與實際操作系統有間距
  - 前期準備：C、Java


---
### 背景介紹 -- 當前基本情況 -- 教學內容
特點：**基本（骨）不變，內容（肉）在變化** -- 肉太厚
- 2008年，MIT教授Frans Kaashoek來清華訪問，並引入xv6教學操作系統到本科實驗；後簡化實驗，形成uCore教學操作系統。
- 2008~2015，弱化了對實際操作系統的深入分析，增加了對教學操作系統的分析與實踐
  - 能力強的學生可以比較深入地理解一個實際的小操作系統
  - **如果**認真完成課程，投入的時間估計是上課時間的2倍以上
  - 前期準備：x86硬件架構、x86彙編、C語言



<!-- 由於難度大，配套課堂教學沒有跟上，大部分學生雖然覺得好，但實際掌握起來很困難，任課老師得差評 -->

---
### 背景介紹 -- 當前基本情況 -- 教學內容
特點：**基本（骨）不變，內容（肉）在變化** -- 合適的肌肉與脂肪
- 2015年，探索代替x86的指令集: MIPS、ARM、OR1200、RISC-V
- 2017年，選擇RISC-V指令集，並逐步調整uCore實驗和教學內容
- 2018年，增加Rust編程語言，並逐步添加rCore實驗和教學內容
- 2021年，設計遞增式的教學操作系統集，設計配套支撐的教學內容
- 2022年，加強從app-->syscall-->kernel的全系統分析

---
### 課程建設的目標
**基本觀點**：迭代實踐與迭代認識是學好OS的基礎

- 硬件簡單
- 軟件簡潔
- 循序漸進
- 理技結合
- 應用驅動
- 生物進化

![bg right:60% 100%](./figs/build-os-course-goal.png)

---
### 課程建設的策略
讓學生通過OS實踐來深入地理解OS原理
- 支持應用  -- OS功能擴展全來自於應用的需求
- 硬件簡單  -- RISC-V 64 支持OS的最小硬件子集
- 軟件簡潔  -- 選用Rust語言的抽象能力和高安全設計
- 循序漸進  -- 隨著知識點擴展來擴展OS實踐
- 理技結合  -- 原理的知識點與OS實踐內容對應
- 生物進化  -- 實踐逐步形成的多個OS類似生命進化中形成的各種生物
  
---
### 課程建設的基本思路
- 理解式學習：編寫應用，並通過分析應用與OS的執行過程，掌握OS原理
  - 幾行~幾十行的**應用程序**，理解應用需求
  - 十幾個**系統調用**，理解接口
  - OS的系統調用**實現功能**的流程圖，理解OS的設計思路
  - **動態調試**應用程序-->系統調用-->操作系統內核的**全系統執行**過程，從而理解操作系統的全局
  
---
### 課程建設的基本思路
- 構造式學習：深入OS內部實現，參考/基於這些OS，擴展某些相對完整的OS功能
  - 幾行~幾十行的**應用程序**，理解應用需求
  - 十幾個**系統調用**，理解接口
  - OS的系統調用**實現功能**的流程圖，理解OS的設計思路
  - **動態調試**應用程序-->系統調用-->操作系統內核的**全系統執行**過程，從而理解操作系統的全局
  - 參考已有實現，**擴展/實現**操作系統的新功能/性能優化，從而具備操作系統的設計實現能力，並掌握操作系統

---
### 課程建設的具體實施 -- OS設計

- 原理與實踐結合
    - 提供十幾個由簡單到相對複雜功能進化的OS實例
    - 提供OS的詳細設計實現文檔、多種測試用例、自動測試環境
   -  課程上講的OS原理和概念在實踐或實驗中基本上有對應
   -  分析原理和實踐有共同點和差異點
   -  通過原理和實踐來深化對操作系統全局與細節的理解

---
### 課程建設的具體實施 -- OS設計
**設計實現滿足應用APP逐步遞增需求的逐步進化的OS**
操作系統 | 功能      | 系統調用個數 
---------|----------|----------
 LibOS | 讓APP與HW隔離，簡化應用訪問硬件的難度和複雜性 | 0
 BatchOS | 讓APP與OS隔離，加強系統安全，提高執行效率 | 2
multiprogOS | 讓APP共享CPU資源 | 3


---
### 課程建設的具體實施 -- OS設計
**設計實現滿足應用APP逐步遞增需求的逐步進化的OS**
操作系統 | 功能 | 系統調用個數 
---------|----------|----------
TimeSharing OS | 讓APP共享CPU資源 | 4
Address Space OS | 隔離APP訪問的內存地址空間，加強APP間的安全 | 4
Process OS | 支持APP動態創建新進程，增強進程管理和資源管理能力 |9


---
### 課程建設的具體實施
**設計實現滿足應用APP逐步遞增需求的逐步進化的OS**
操作系統 | 功能  | 系統調用個數 
---------|----------|----------
Filesystem OS | 支持APP對數據的持久保存 | 11
IPC OS | 支持多個APP進程間數據交互與事件通知 | 17
TreadOS | 支持線程APP，簡化切換與數據共享  | 18
SyncMutex OS | 在多線程APP中支持對共享資源的同步互斥訪問 | 27


<!-- 1 LibOS: 讓APP與HW隔離，簡化應用訪問硬件的難度和複雜性
    2 BatchOS： 讓APP與OS隔離，加強系統安全，提高執行效率
    3 multiprog&time-sharing OS: 讓APP共享CPU資源
    4 Address Space OS: 隔離APP訪問的內存地址空間，加強APP間的安全
    5 Process OS: 支持APP動態創建新進程，增強進程管理和資源管理能力
    6 Filesystem OS：支持APP對數據的持久保存
    7 IPC OS：支持多個APP進程間數據交互與事件通知 
    8 Tread&Coroutine OS：支持線程和協程APP，簡化切換與數據共享  
    9 SyncMutex OS：在多線程APP中支持對共享資源的同步互斥訪問
    10 Device OS：提高APP的I/O效率，支持基於外設中斷的串口/塊設備 -->


---
### 課程建設的具體實施 -- OS設計 -- 系統調用
**30個系統調用**

- 進程相關： 13個
- 文件相關：5個
- 地址空間相關：2個
- 同步互斥相關：9個

<!-- ---
### 課程建設的具體實施
**30個系統調用**
```rust
const SYSCALL_DUP: usize = 24;
const SYSCALL_OPEN: usize = 56;
const SYSCALL_CLOSE: usize = 57;
const SYSCALL_PIPE: usize = 59;
const SYSCALL_READ: usize = 63;
const SYSCALL_WRITE: usize = 64;
const SYSCALL_EXIT: usize = 93;
const SYSCALL_SLEEP: usize = 101;
const SYSCALL_YIELD: usize = 124;
```
---
### 課程建設的具體實施
**30個系統調用**
```rust
const SYSCALL_KILL: usize = 129;
const SYSCALL_SIGACTION: usize = 134;
const SYSCALL_SIGPROCMASK: usize = 135;
const SYSCALL_SIGRETURN: usize = 139;
const SYSCALL_GET_TIME: usize = 169;
const SYSCALL_GETPID: usize = 172;
const SYSCALL_FORK: usize = 220;
const SYSCALL_EXEC: usize = 221;
const SYSCALL_WAITPID: usize = 260;
```

---
### 課程建設的具體實施
**30個系統調用**
```rust
const SYSCALL_KILL: usize = 129;
const SYSCALL_SIGACTION: usize = 134;
const SYSCALL_SIGPROCMASK: usize = 135;
const SYSCALL_SIGRETURN: usize = 139;
const SYSCALL_GET_TIME: usize = 169;
const SYSCALL_GETPID: usize = 172;
const SYSCALL_FORK: usize = 220;
const SYSCALL_EXEC: usize = 221;
const SYSCALL_WAITPID: usize = 260;
const SYSCALL_THREAD_CREATE: usize = 1000;
const SYSCALL_GETTID: usize = 1001;
const SYSCALL_WAITTID: usize = 1002;
```
---
### 課程建設的具體實施
**設計實現滿足應用APP逐步遞增需求的逐步進化的OS**
```rust
const SYSCALL_MUTEX_CREATE: usize = 1010;
const SYSCALL_MUTEX_LOCK: usize = 1011;
const SYSCALL_MUTEX_UNLOCK: usize = 1012;
const SYSCALL_SEMAPHORE_CREATE: usize = 1020;
const SYSCALL_SEMAPHORE_UP: usize = 1021;
const SYSCALL_SEMAPHORE_DOWN: usize = 1022;
const SYSCALL_CONDVAR_CREATE: usize = 1030;
const SYSCALL_CONDVAR_SIGNAL: usize = 1031;
const SYSCALL_CONDVAR_WAIT: usize = 1032;
``` -->


---
###  課程建設的具體實施 -- 課程資源建設
#### 課程實踐內容 -- rCore Tutorial Book v3
-  [課程實踐參考書](https://learningos.github.io/rCore-Tutorial-Book-v3/)，[課程實踐代碼](https://github.com/rcore-os/rCore-Tutorial-v3)，[課程實踐代碼的API文檔](https://learningos.github.io/rCore-Tutorial-v3/)

#### 課程實驗內容 -- rCore Tutorial Guide 2022 Spring
- [實驗文檔](https://github.com/LearningOS/rCore-Tutorial-Guide-2022S/)  , [API文檔](https://github.com/LearningOS/rCore-Tutorial-Guide-2022S/) , [實驗代碼](https://github.com/LearningOS/rCore-Tutorial-Code-2022S)，[測試用例](https://github.com/LearningOS/rCore-Tutorial-Test-2022S) 

#### 課程參考文檔 --教材/課件
- [課程在線Slides](http://learningos.github.io/os-lectures/)，[Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
- [深入瞭解計算機系統](https://hansimov.gitbook.io/csapp/)，[RISC-V Reader中文版](http://riscvbook.com/chinese/RISC-V-Reader-Chinese-v2p1.pdf)


---
### 課程建設的具體實施 -- 在線學習建設
- 當前還存在一些需要改進的地方
  - 學習內容的逐步遞進
    - 進一步細化知識粒度和銜接 
  - 學習效果的及時反饋
    - 在線IDE
    - 在線評測  
  - 學習問題的及時解答 
    - 在線答疑
    - 鼓勵機制

![bg right:25% 100%](./figs/online-os.png)

---
### 課程建設的具體實施 --  課程設計
- 課程內容
  - 48學時，16次課（13講） 
- 實踐內容
  - 16~32學時，5次實驗
- 擴展講解和訓練
  - 最新技術進展
  - 實驗代替考試
  - 操作系統比賽

![bg right:50% 100%](./figs/build-os-course-goal.png)


---
<!-- theme: gaia -->
<!-- _class: lead -->

# 謝謝！

開源操作系統訓練營

https://github.com/LearningOS/rust-based-os-comp2022

一年三期：春季學期、秋季學期、暑假


---
<!-- theme: gaia -->
<!-- _class: lead -->

# 備份材料
- 十三講的課程內容設計+知識點設計
- 十一個教學OS的實踐設計
- 五個實驗設計

---
#### 第一講 操作系統概述
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 課程概述 & 教學安排](../lec1/p1-intro.html)
- [第二節 什麼是操作系統](../lec1/p2-whatisos.html)
- [第三節 操作系統歷史演化](../lec1/p3-oshistory.html)
- [第四節 操作系統結構](../lec1/p4-osarchitecture.html)
- [第五節 實踐：試試UNIX/Linux](../lec1/p5-tryunix.html)

</div>
<div>

知識點
- 操作系統定義、抽象、特徵
- 操作系統歷史演化
- 操作系統的架構
- 硬件與操作系統的關係與接口
- 應用與操作系統的關係與接口
- 實踐：Linux/rCore/uCore APP

</div>
</div>

---
#### 第二講 實踐與實驗介紹
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 實踐與實驗簡要分析](../lec2/p1-labintro.html)
- [第二節 Compiler與OS](../lec2/p2-compiling.html)
- [第三節 硬件啟動與軟件啟動](../lec2/p3-boot.html)
- [第四節 實踐：裸機程序 -- LibOS](../lec2/p4-lab1.html)

</div>
<div>

知識點
- 函數調用、棧幀與參數
- 編譯器/硬件與OS的共識
- 加電後硬件/軟件啟動過程
- 程序執行過程、Linux應用編程
- RISC-V的SBI
- 開發環境與執行環境、裸機編程
- 實踐：LibOS操作系統
</div>
</div>

---
#### 第三講 基於特權級的隔離與批處理
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 從 OS 角度看計算機系統](../lec3/p1-osviewarch.html)
- [第二節 從 OS 角度看RISC-V](../lec3/p2-osviewrv.html)
- [第三節 實踐：批處理操作系統](../lec3/p3-batchos.html)

</div>
<div>

知識點
- 特權級與特權級切換
- 系統調用、外設中斷、軟件異常
- 系統調用設計與實現、執行過程
- 實踐：批處理操作系統
</div>
<div>

---

#### 第四講 多道程序與分時多任務
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 相關背景與基本概念](../lec4/p1-multiprog.html)
- [第二節 實踐：多道程序與分時多任務操作系統](../lec4/p2-labs.html)

</div>
<div>

知識點
- 上下文、中斷、任務、任務/中斷上下文、任務/中斷上下文切換、任務/中斷上下文切換的時機
- 任務生命週期、任務執行過程
- 協作式調度、搶佔式調度
- 實踐：多道程序操作系統
- 實踐：分時多任務操作系統

</div>
<div>

---

#### 第五講 地址空間-物理內存管理
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 地址空間](../lec5/p1-memintro.html)
- [第二節 內存分配](../lec5/p2-memalloc.html)
- [第三節 實踐：建立地址空間的操作系統](../lec5/p3-labs.html)

</div>
<div>

知識點

- 地址空間、內存管理、連續物理內存分配、非連續物理內存分配
- 物理內存的管理
- 多級頁表的設計與實現
- 訪存異常及其軟硬件協同處理過程
- 實踐：基於地址空間的分時多任務操作系統

</div>
<div>

---
#### 第六講  地址空間-虛擬存儲管理
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節  虛擬存儲的基本概念](../lec6/p1-vmoverview.html)
- [第二節 頁面置換算法 -- 局部頁面置換算法](../lec6/p2-pagereplace-1.html)
- [第三節 頁面置換算法 -- 全局頁面置換算法](../lec6/p2-pagereplace-2.html)

</div>
<div>

知識點
- 局部性原理、虛擬存儲基本概念、Page Fault異常、局部頁面置換算法、全局頁面置換算法、Belady異常
- 按需分頁、Copy On Write、基於頁的內存換入換出機制
- 實踐：支持虛存的分時多任務操作系統


</div>
<div>

---
#### 第七講  進程管理與單處理器調度
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 進程管理](../lec7/p1-process-overview.html)
- [第二節 單處理器調度](../lec7/p2-sched.html)
- [第三節 實時管理與調度](../lec7/p3-realtime.html)
- [第四節 實踐：支持進程的操作系統](../lec7/p4-labs.html)

</div>
<div>

知識點
- 進程概念、進程運行狀態、進程的管理、基本調度策略/算法
- 實時任務、實時調度算法、優先級反置問題與解決方法
- 進程控制塊和fork, exec, waitpid, exit系統調用的設計與執行
- 實踐：支持進程的操作系統

</div>
<div>


---
#### 第八講  多處理器調度
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 對稱多處理與多核架構](../lec8/p1-multiprocessor-overview.html)
- [第二節 多處理器調度概述](../lec8/p2-multiprocessor-sched-overview.html)
- [第三節 Linux O(1) 調度](../lec8/p3-linux-O1-sched.html)
- [第四節 Linux CFS（Completely Fair Schduler） 調度](../lec8/p4-linux-cfs-sched.html)
- [第五節 Linux/FreeBSD BFS 調度](../lec8/p5-linux-bfs-sched.html)

</div>
<div>

知識點
- 多核/SMP/NUMA架構的特徵
- 多處理器調度算法
- 負載遷移技術


</div>
<div>

---
#### 第九講  文件系統
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 文件系統概述](../lec9/p1-fsoverview.html)
- [第二節 文件系統的設計與實現](../lec9/p2-fsimplement.html)
- [第三節 支持崩潰一致性的文件系統](../lec9/p3-fsjournal.html)
- [第四節 支持文件的操作系統](../lec9/p4-fs-lab.html)

</div>
<div>

知識點
- 文件系統基本概念：文件/目錄/文件描述符/目錄項, 軟/硬鏈接
- 文件/文件系統設計與實現
- open/close/read/write系統調用的設計與執行
- 鏈式/索引文件結構設計、空閒磁盤塊空間管理、緩衝區管理
- 實踐：支持文件的FS操作系統

</div>
<div>

---
#### 第十講  進程間通信
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 進程間通信(IPC)概述](../lec10/p1-ipcoverview.html)
- [第二節 支持IPC的OS](../lec10/p2-ipclabs.html)


</div>
<div>

知識點
- 無名/有名管道、消息隊列、共享內存、信號的應用編程與設計實現
- 支持管道與信號的IPC操作系統


</div>
<div>

---
#### 第十一講  線程與協程
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 線程](../lec11/p1-thread.html)
- [第二節 協程](../lec11/p2-coroutine.html)
- [第三節 支持線程/協程的OS(TCOS)](../lec11/p3-labs.html)

</div>
<div>

知識點
- 線程、協程的起因與特徵
- 用戶態管理的線程設計與實現
- 內核態管理的線程設計與實現
- 實踐：支持線程的操作系統

</div>
<div>

---
#### 第十二講 同步互斥
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 概述](../lec12/p1-syncmutex.html)
- [第二節 信號量](../lec12/p2-semaphore.html)
- [第三節 管程與條件變量](../lec12/p3-monitor-cond.html)
- [第四節 同步互斥實例問題](../lec12/p4-instances.html)
- [第五節 死鎖](../lec12/p5-deadlock.html)
- [第六節 支持同步互斥的OS(SMOS)](../lec12/p6-labs.html)

</div>
<div>

知識點
- 軟件實現的互斥、基於中斷的互斥、基於原子指令的互斥
- 忙等方式與休眠方式的同步互斥
- 信號量的設計與實現
- 管程與條件變量的設計與實現
- 死鎖必要條件、死鎖安全、銀行家算法、死鎖檢測算法等
- 實踐：支持同步互斥的操作系統

</div>
<div>

---
#### 第十三講 設備管理
<div class="grid grid-cols-2 gap-4">
<div>

- [第一節 設備接口](../lec13/p1-devinterface.html)
- [第二節 磁盤子系統](../lec13/p2-disk.html)
- [第三節 第三節 支持device的OS（DOS）](../lec13/p3-Labs.html)


</div>
<div>

知識點
- I/O設備分類、I/O傳輸方式、I/O設備抽象
- I/O執行模型
- 串口驅動、塊設備驅動
- 內核態響應中斷
- 實踐：支持外設中斷的操作系統

</div>
<div>

---
### 實踐 1: UNIX/Linux APP 

  - "系統調用"
  - 例子，用C語言，來自UNIX（例如Linux、macOS、FreeBSD）

            fd = open("out", 1);
            write(fd, "hello\n", 6);
            pid = fork()
- 能理解和編寫包含操作系統進程/文件等相關的簡單命令行Linux程序

---
### 實踐 2: 裸機程序：LibOS             
  - 軟硬件啟動，棧的建立、函數調用，SBI調用
![w:600](../lec2/figs/os-as-lib.png)
- 理解RISC-V的特權模式，理解SBI訪問，編寫裸機程序


---
### 實踐 3: Batch OS  
  - 特權級: U-Mode, S-Mode
  - 特權級切換
  - 陷入上下文
  - 編譯多應用+OS的鏡像
  - 加載並執行應用

![bg right 100%](../lec3/figs/batch-os-detail.png)


---
### 實踐 4-1: MultiProg OS  
   - 任務的概念
   - 任務的設計實現
   - 協作/搶佔式調度
   -  任務上下文 
   -  陷入上下文
   - 切換任務
   - 切換特權級
![bg right:60% 100%](../lec4/figs/more-task-multiprog-os-detail.png) 

--- 
### 實踐 4-2: TimeSharing OS  
   - 中斷
   - 中斷響應
   - 協作/搶佔式調度
   -  陷入上下文
   -  任務上下文 
   - 切換任務
   - 切換特權級
![bg right:60% 100%](../lec4/figs/time-task-multiprog-os-detail.png) 


---
### 實踐 5： AddrSpace OS   
App/OS內存佈局
- .text: 數據段
- .data：可修改的全局數據。
- 未初始化數據段 .bss
- 堆 （heap）向高地址增長
- 棧 （stack）向低地址增長
![bg right 120%](../lec2/figs/memlayout.png)

---
### 實踐 5： AddrSpace OS  
- 地址空間
- 物理地址
- 頁表
-  陷入上下文
-  任務上下文 
-  中斷響應

![bg right:60% 100%](../lec5/figs/addr-space-os-detail.png) 



---
### 實踐 5： AddrSpace OS  
- 應用地址空間
- 內核地址空間
- 切換任務
- 切換特權級
- 切換頁表
  


![bg right:65% 100%](../lec5/figs/trampoline.png)


---
### 實踐 6：Process OS  
  - Process
    - Trap
    - Task
    - Address Space
    - state
    - relations
    - exit code
![bg right:65% 100%](../lec7/figs/process-os-detail.png) 

---
### 實踐 6：Process OS  
  - fork
  - exec
  - exit
  - wait

![bg right:70% 100%](../lec7/figs/fork-exec.png) 

---
### 實踐 6：Process OS   
   - PCB 
![bg right:70% 100%](../lec7/figs/process-os-key-structures.png)

---
### 實踐 7: Filesystem OS  
- 文件系統層次結構
- 塊設備驅動
- 塊緩衝區
- EasyFS
- Virtual FS
- 進程的文件描述符表
- 文件相關係統調用
![bg right:60% 100%](../lec9/figs/fs-intro.png)


---
### 實踐 7: Filesystem OS  
- 文件系統在操作系統中的位置
![bg right:70% 100%](../lec9/figs/filesystem-os-detail.png)

---
### 實踐 7: Filesystem OS  
- 進程的文件描述符表
- 文件相關係統調用
![bg right:70% 100%](../lec9/figs/process-os-key-structures-file.png)



---
### 實踐 8: IPC OS
支持進程間通信和異步消息機制
- 管道（PIPE）
- 信號（Signal）
![bg right:70% 100%](../lec10/figs/ipc-os-detail-2.png)


---
### 實踐 8: IPC OS
對進程控制塊的擴展
- 管道也是一種文件
- 支持I/O重定向
![bg right:60% 100%](../lec10/figs/process-os-key-structures-file-ipc.png)



---
### 實踐 9: Thread OS
- 用戶態管理的用戶態運行的線程
- 內核態管理的用戶態運行的線程
![bg right:65% 100%](../lec11/figs/thread-coroutine-os-detail.png)


---
### 實踐 9: Thread OS
- 協程結構
- 線程結構
- 進程結構

![bg right:60% 100%](../lec11/figs/task-abstracts.png)


---
### 實踐 10: SyncMutex OS
對進程控制塊擴展，支持線程同步互斥訪問共享變量
- Mutex
- Semphore
- Condvar
![bg right:70% 100%](../lec12/figs/syncmutex-os-detail.png)


---
### 實踐 10: SyncMutex OS
對進程控制塊擴展，支持線程同步互斥訪問共享變量
- Mutex
- Semphore
- Condvar

![bg right:70% 100%](../lec12/figs/syncmutex-os-key-structures.png)



---
### 實踐 11: Device OS
支持塊設備/串口等外設
- 內核態中斷響應
- DMA
- 輪詢
- 設備<-->內存間數據傳輸
- 同步互斥保護


![bg right:60% 100%](../lec13/figs/os-io-lifetime.png)


---
### 實驗 1 ：獲取任務信息

- 預先學習完成 實踐 1--4

#### 內容

我們的系統已經能夠支持多個任務分時輪流運行，我們希望引入一個新的系統調用 sys_task_info 以獲取當前任務的信息


---
### 實驗 2 ：完成mmap和munmap系統調用功能

- 預先學習完成 實踐 1--5

#### 內容

- 引入虛存機制後，原來內核的 sys_get_time 和 sys_task_info 函數實現就無效了。請你重寫這個函數，恢復其正常功能。
- mmap 在 Linux 中主要用於在內存中映射文件， 本次實驗簡化它的功能，僅用於申請內存。請實現 mmap 和 munmap 系統調用


---
### 實驗 3 ：完成spawn系統調用功能

- 預先學習完成 實踐 1--6
- 
#### 內容

實現一個完全 DIY 的系統調用 spawn，用以創建一個新進程。


---
### 實驗 4 ：實現文件的硬鏈接功能

- 預先學習完成 實踐 1--7

#### 內容

硬鏈接要求兩個不同的目錄項指向同一個文件，在我們的文件系統中也就是兩個不同名稱目錄項指向同一個磁盤塊。要求實現三個系統調用 sys_linkat、sys_unlinkat、sys_stat 。

---
### 實驗 5 ：實現文件的硬鏈接功能

- 預先學習完成 實踐 1--10

內容

完成對基於信號量/條件變量的同步互斥多線程程序的死鎖檢測
