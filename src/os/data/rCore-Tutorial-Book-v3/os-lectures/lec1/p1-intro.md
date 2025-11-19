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

## 第一講 操作系統概述
### 第一節 課程概述 & 教學安排

<br>
<br>

向勇 陳渝 李國良 

<br>
<br>

2022年秋季

---

## 課程信息

### 主講教師：
  - 向勇
  - 陳渝

### 助教
  - 閉浩揚、田凱夫、趙方亮、賀鯤鵬

---

## 上課信息

### 上課時間地點
- 星期三 上午第二大節 09:50-12:15 (1-16周) 
- 地點
   - 五教 5101

----

## 預備知識

### 程序設計語言（彙編、C 和 Rust）
 - :( 不是開發應用程序
 - :) 而是開發系統程序

### 數據結構
 - :) 理解基本數據結構即可

---

## 預備知識
### 計算機組成原理
 - :( 劉總/康總的 RISC-V 原理
 - :) Patterson 的 RISC-V 原理

### 編譯原理
 - :) 沒學過影響不大 
 - :( 但還是要了解高級語言 <–>RISC-V 彙編語言


---

#### 課程參考
- [課程幻燈片](https://www.yuque.com/docs/share/4c39608f-3051-4445-96ca-f3c018cb96c7)
- 參考書
  * [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/)
  - [深入瞭解計算機系統](https://hansimov.gitbook.io/csapp/)
  - [RISC-V Reader中文版](http://riscvbook.com/chinese/RISC-V-Reader-Chinese-v2p1.pdf)
#### 課程實踐：rCore Tutorial Book v3
-  [課程實踐參考書](https://learningos.github.io/rCore-Tutorial-Book-v3/)
-  [課程實踐代碼倉庫](https://github.com/rcore-os/rCore-Tutorial-v3)
-  [課程實踐代碼的API文檔](https://github.com/rcore-os/rCore-Tutorial-v3#os-api-docs)

---

### 實驗指導


#### uCore-RV-64

* 基準代碼倉庫（[lab](https://github.com/uCore-RV-64/uCore-RV-64-lab)）
* 文檔倉庫（[doc](https://github.com/uCore-RV-64/uCore-RV-64-doc)）
* 在線文檔[入口](https://ucore-rv-64.github.io/uCore-RV-64-doc/index.html)
* 實驗參考答案倉庫（[answer](https://github.com/uCore-RV-64/uCore-RV-64-answer)）
* 自動測試腳本倉庫（[test](https://github.com/uCore-RV-64/uCore-RV-64-test)）
* codespace開發環境配置腳本倉庫（[config](https://github.com/uCore-RV-64/uCore-RV-64-conf)）

---

### 實驗指導

#### rCore
- [實驗文檔](https://github.com/LearningOS/rCore-Tutorial-Guide-2022S/)
- [API文檔](https://github.com/LearningOS/rCore-Tutorial-Guide-2022S/#os-api-docs-of-rcore-tutorial-code-2022s) , [實驗代碼](https://github.com/LearningOS/rCore-Tutorial-Code-2022S)
- [測試用例](https://github.com/LearningOS/rCore-Tutorial-Test-2022S)

#### uCore和rCore實驗[講解視頻](https://www.yuque.com/docs/share/1b5b9260-8a80-4427-a612-78ec72b37e5f)

---


![bg right 100%](figs/ucorearch.png)


### OS 原理與設計思想

* 操作系統結構
* 中斷及系統調用
* 內存管理
* 進程管理
* 處理機調度
* 同步互斥
* 文件系統
* I/O 子系統


---

## 作業與實驗

### 平時作業
  - 課後練習

### 基礎實驗
  - 面向 RISC-V CPU 用 Rust/C 設計實現操作系統的功能
 
### 課程設計  
  - 大實驗

---
## 基礎實驗
### 實驗一：操作系統的基本支持
### 實驗二：地址空間
### 實驗三：進程管理與調度
### 實驗四：文件系統與進程間通信
### 實驗五：同步互斥


---

## 課程設計（大實驗）

### 各種操作系統相關的功能和擴展

- 多種CPU平臺上的操作系統移植
  * RISC-V、x86-64、MIPS、ARM
- 多種開發板的驅動開發
  * RaspBerry PI、U740、D1等
  * GUI、驅動、文件系統、網絡
- 操作系統內核模塊的完善和改進
  * 內核可加載模塊、微內核
  * 在內核中引入異步編程

--- 

## 成績評定

### 選擇1： 
  - 按時完成實驗一至實驗五：30% 
  - 期中考試 30% + 期末考試 40% ：70%
### 選擇2： 
  - 四周內完成實驗一至實驗五(2022春季實驗)：30% 
  - 課程設計（即大實驗）：70%
    - 注：選擇大實驗的同學如果後續退出課程設計，需參加考試。

--- 

## 調查問卷

[2022年秋季學期操作系統課選課問卷](http://oscourse2019.mikecrm.com/fPozIRL)（訪問密碼：XxW21Ur1CF）

- 為什麼要學這門課？ 
- 你打算如何來學這門課？
- 對自己的課程學習要求是什麼？
- 你願意如實報告是否獨立完成實驗任務？
- 你希望在操作系統課上學到什麼知識和什麼能力？
- 以前的學習情況？
