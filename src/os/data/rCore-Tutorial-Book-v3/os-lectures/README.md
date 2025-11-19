# 操作系統課程，2022春季，清華大學計算機系

## 老師與助教

### 主講教師：
  - 陳渝
  - 李國良
### 助教
  - 張譯仁 鈕澤平 饒淙元 尤予陽 徐奧淳 王瑞康
  - 馬思源 彭浩洋 田凱夫 曹雋誠 安之達 許善樸
## 上課時間/地點
- 星期一 上午第二大節 09:50-12:15 (1-16周) 
- 地點
   - 五教 5305  李國良
   - 五教 5205  陳渝
## 課程資源
### 課程大綱
- [課程&實驗大綱](os-course-outline.md)
### 課程幻燈片
* [Github倉庫](https://github.com/LearningOS/os-lectures/)
* [Gitee備份倉庫](https://gitee.com/learning-os/os-lectures/)
* [課程幻燈片在線閱讀](https://learningos.github.io/os-lectures/)
* pdf 版會在課前發佈到網絡學堂
### 課程參考書

* OS：[Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP)
* Computer System：[深入瞭解計算機系統](https://hansimov.gitbook.io/csapp)
* RISC-V CPU：[RISC-V Reader中文版](http://riscvbook.com/chinese/RISC-V-Reader-Chinese-v2p1.pdf)
* OS實踐：[rCore Tutorial Book v3](https://rcore-os.github.io/rCore-Tutorial-Book-v3)
    * 配套代碼和API文檔
        * [Github倉庫](https://github.com/rcore-os/rCore-Tutorial-v3)
        * [Gitee備份倉庫](https://gitee.com/learning-os/rCore-Tutorial-v3)
        * [各章OS的API 在線文檔](https://learningos.github.io/rCore-Tutorial-v3/)
        * [可顯示內核動態執行信息的內核分支](https://github.com/rcore-os/rCore-Tutorial-v3/tree/ch9-log)
### 課程答疑

* [QA倉庫](https://git.tsinghua.edu.cn/os-lab/q-and-a/)
* [助教的實驗講解視頻](https://cloud.tsinghua.edu.cn/d/ce9eced17e89471c8c30/)
### 課後習題

[rCore Tutorial Book v3](https://rcore-os.github.io/rCore-Tutorial-Book-v3)中各章後面的“練習”小節中的“課後練習”和“練習參考答案”小節

###	往年考題

在網絡學堂的“課程文件”中的“往年考試題”欄中。

### rCore實驗

#### 實驗指導書

包含每次實驗必做的編程和問答作業，以及相對rCore Tutorial Book-v3較為精簡的指導

* [rCore-Tutorial-Guide文檔源碼](https://github.com/LearningOS/rCore-Tutorial-Guide-2022S)
*  [rCore-Tutorial-Guide文檔在線閱讀](https://learningos.github.io/rCore-Tutorial-Guide-2022S/)
* [lab1(ch3) OS框架API在線文檔](https://learningos.github.io/rCore-Tutorial-Code-2022S/ch3/os/index.html)
* [lab2(ch4) OS框架API在線文檔](https://learningos.github.io/rCore-Tutorial-Code-2022S/ch4/os/index.html)
#### 代碼框架

* [Github倉庫](https://github.com/LearningOS/rCore-Tutorial-Code-2022S)
* [git.tsinghua倉庫](https://git.tsinghua.edu.cn/os-lab/public/rcore-tutorial-code-2022s)
#### 用戶態測例

* [Github倉庫](https://github.com/LearningOS/rCore-Tutorial-Test-2022S)
* [git.tsinghua倉庫](https://git.tsinghua.edu.cn/os-lab/public/rcore-tutorial-test-2022s)
### uCore實驗

#### 實驗指導書

* [Github倉庫](https://github.com/LearningOS/uCore-Tutorial-Guide-2022S)
* [uCore-Tutorial-Guide文檔在線閱讀](https://learningos.github.io/uCore-Tutorial-Guide-2022S/)
#### 代碼框架

* [Github倉庫](https://github.com/LearningOS/uCore-Tutorial-Code-2022S)
* [git.tsinghua倉庫](https://git.tsinghua.edu.cn/os-lab/public/ucore-tutorial-code-2022s)
#### 用戶態測例

* [Github倉庫](https://github.com/LearningOS/uCore-Tutorial-Test-2022S)
* [git.tsinghua倉庫](https://git.tsinghua.edu.cn/os-lab/public/ucore-tutorial-test-2022s)
## 其它內容

 1. [幻燈片模板](style-marp.md)
 2. [RISC-V與X86 CPU硬件特徵的對比介紹](rv-x86-hardware-info-video.md)
 3. 如何生成PDF slides
      - [ubuntu 用 markdown + vscode + marp 編寫 slides 並輸出為 pdf](https://www.cnblogs.com/luyi07/p/14736322.html)

        ```
        marp --pdf --allow-local-files lec[1-9]*/*.md
        ```
