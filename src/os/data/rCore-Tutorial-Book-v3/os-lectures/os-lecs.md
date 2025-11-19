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

## 第一講 操作系統概述
- [第一節 課程概述 & 教學安排](./lec1/p1-intro.html)
- [第二節 什麼是操作系統](./lec1/p2-whatisos.html)
- [第三節 操作系統歷史演化](./lec1/p3-oshistory.html)
- [第四節 操作系統結構](./lec1/p4-osarchitecture.html)
- [第五節 實踐：試試UNIX/Linux](./lec1/p5-tryunix.html)

---
## 第二講 實踐與實驗介紹

- [第一節 實踐與實驗簡要分析](./lec2/p1-labintro.html)
- [第二節 Compiler與OS](./lec2/p2-compiling.html)
- [第三節 硬件啟動與軟件啟動](./lec2/p3-boot.html)
- [第四節 實踐：裸機程序 -- LibOS](./lec2/p4-lab1.html)

---

## 第三講 基於特權級的隔離與批處理
- [第一節 從 OS 角度看計算機系統](./lec3/p1-osviewarch.html)
- [第二節 從 OS 角度看RISC-V](./lec3/p2-osviewrv.html)
- [第三節 實踐：批處理操作系統](./lec3/p3-batchos.html)

---

## 第四講 多道程序與分時多任務
- [第一節 相關背景與基本概念](./lec4/p1-multiprog.html)
- [第二節 實踐：多道程序與分時多任務操作系統](./lec4/p2-labs.html)

---

## 第五講 地址空間-物理內存管理
- [第一節 地址空間](./lec5/p1-memintro.html)
- [第二節 內存分配](./lec5/p2-memalloc.html)
- [第三節 實踐：建立地址空間的操作系統](./lec5/p3-labs.html)

---
## 第六講  地址空間-虛擬存儲管理
- [第一節  虛擬存儲的基本概念](./lec6/p1-vmoverview.html)
- [第二節 頁面置換算法 -- 局部頁面置換算法](./lec6/p2-pagereplace-1.html)
- [第三節 頁面置換算法 -- 全局頁面置換算法](./lec6/p2-pagereplace-2.html)

---
## 第七講  進程管理與單處理器調度
- [第一節 進程管理](./lec7/p1-process-overview.html)
- [第二節 單處理器調度](./lec7/p2-sched.html)
- [第三節 實時管理與調度](./lec7/p3-realtime.html)
- [第四節 實踐：支持進程的操作系統](./lec7/p4-labs.html)

---
## 第八講  多處理器調度
- [第一節 對稱多處理與多核架構](./lec8/p1-multiprocessor-overview.html)
- [第二節 多處理器調度概述](./lec8/p2-multiprocessor-sched-overview.html)
- [第三節 Linux O(1) 調度](./lec8/p3-linux-O1-sched.html)
- [第四節 Linux CFS（Completely Fair Schduler） 調度](./lec8/p4-linux-cfs-sched.html)
- [第五節 Linux/FreeBSD BFS 調度](./lec8/p5-linux-bfs-sched.html)

---
## 第九講  文件系統
- [第一節 文件系統概述](./lec9/p1-fsoverview.html)
- [第二節 文件系統的設計與實現](./lec9/p2-fsimplement.html)
- [第三節 支持崩潰一致性的文件系統](./lec9/p3-fsjournal.html)
- [第四節 支持文件的操作系統](./lec9/p4-fs-lab.html)

---
## 第十講  進程間通信
- [第一節 進程間通信(IPC)概述](./lec10/p1-ipcoverview.html)
- [第二節 支持IPC的OS](./lec10/p2-ipclabs.html)


---
## 第十一講  線程與協程
- [第一節 線程](./lec11/p1-thread.html)
- [第二節 協程](./lec11/p2-coroutine.html)
- [第三節 支持線程/協程的OS(TCOS)](./lec11/p3-labs.html)

---
## 第十二講 同步互斥
- [第一節 概述](./lec12/p1-syncmutex.html)
- [第二節 信號量](./lec12/p2-semaphore.html)
- [第三節 管程與條件變量](./lec12/p3-monitor-cond.html)
- [第四節 同步互斥實例問題](./lec12/p4-instances.html)
- [第五節 死鎖](./lec12/p5-deadlock.html)
- [第六節 支持同步互斥的OS(SMOS)](./lec12/p6-labs.html)

---
## 第十三講 設備管理
- [第一節 設備接口](./lec13/p1-devinterface.html)
- [第二節 磁盤子系統](./lec13/p2-disk.html)
- [第三節 支持device的OS（DOS）](./lec13/p3-labs.html)

---
### OS課程介紹
- [清華計算機系2022春季OS課程](./course-intro.md)