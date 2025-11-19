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

### 第五節 實踐：試試UNIX/Linux

<br>
<br>

向勇 陳渝 李國良 

<br>
<br>

2022年秋季

---
## UNIX/Linux在哪裡？

- Linux 
   - Ubuntu、Fedora、SuSE、openEuler 
   - 麒麟  統信  
- Windows with WSL (Windows Subsystem of Linux)
- MacOS with UNIX shell 
---
## 為什麼是Linux？
- 開放源碼，有很好的文檔，設計簡潔，使用廣泛
- 如果你瞭解Linux的內部情況，學習ucore/rcore會有幫助。

---
## Try Linux

- shell
   - bash, fish, zsh, starship ...

- program
   - ls, rm，gcc，gdb, vim ...

---
## Linux內核通常提供哪些服務？

  * 進程（一個正在運行的程序）
  * 內存分配
  * 文件內容
  * 文件名、目錄
  * 訪問控制（安全）
  * 許多其他的：用戶、IPC、網絡、時間、終端


---
## Linux內核提供的應用程序/內核接口？

  * "系統調用"
  * 例子，用C語言，來自UNIX（例如Linux、macOS、FreeBSD）。

            fd = open("out", 1);
            write(fd, "hello\n", 6);
            pid = fork()

 *  這些看起來像函數調用，但它們並不是
 *  核心的系統調用數量並不多（20個左右）

---
## Linux內核提供的應用程序/內核接口？

| 系統調用名 | 含義 |
| ------------------------ | ---- |
| ``int fork()``           |  創建一個進程，返回子進程的PID。    |
| ``int exit(int status)`` | 終止當前進程；報告狀態給執行wait()系統調用的父進程。沒有返回。     |
| ``int wait(int *status)``    |  等待子進程退出；退出狀態為 ``*status`` ；返回子進程的PID。    |
| ``int kill (int pid)``           |   終止進程號為PID的進程。返回0表示成功，或-1表示錯誤。    |
| ``int getpid()``             |   返回當前進程的PID。   |

---
## Linux內核提供的應用程序/內核接口？

| 系統調用名 | 含義 |
| ------------------------ | ---- |
| ``int sleep(int n)``                         | 暫停n個時鐘週期。     |
| ``int exec(char *file，char *argv[])``   |  用參數加載文件並執行；僅當出錯時返回。    |
|   ``char *sbrk(int n)``   |  將進程內存增加n個字節。返回新內存的開始地址。    |
|   ``int open(char *file，int flags)``   |  打開文件；標誌flag表示文件操作的讀/寫屬性；返回一個fd(文件描述符)。    |
|   ``int write(int fd，char *buf，int n)``   |  從buf向文件描述符fd寫入n個字節；返回n。    |

---
## Linux內核提供的應用程序/內核接口？

| 系統調用名 | 含義 |
| ------------------------ | ---- |
|  ``int read(int fd，char *buf，int n)``   |    將n個字節讀入buf；返回讀取的數字；如果文件結束，則為0。   |
|  ``int close(int fd)``   |  釋放打開的描述符為fd的文件。    |
|  ``int dup(int fd)``  |  返回一個新的文件描述符，引用與文件描述符相同的文件。    |
|  ``int pipe(int p[])``   |  創建一個管道，將讀/寫文件描述符放在p[0]和p[1]中。    |
|  ``int chdir(char *dir)``     | 更改當前目錄。|

---
## Linux內核提供的應用程序/內核接口？

| 系統調用名 | 含義 |
| ------------------------ | ---- |
|  ``int mkdir(char *dir) ``     |  創建一個新目錄。    |
| ``int mknod(char *file, int, int)``  |  創建一個設備文件。    |
|  ``int fstat(int fd, struct stat *st)``    | 將文件fd的元信息放入 ``*st``     |
|   ``int stat(char *file, struct stat *st)``   | 將文件 ``*file`` 的元信息放入 ``*st``     |
| ``int link(char *file1，char *file2)``    |   為文件file1創建另一個名稱(file2)。    |
| ``int unlink(char *file)``    |   刪除文件。    |


---
## 分析UNIX/Linux類應用

[分析一些非常簡單的小程序](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/)

#### 進程相關

fork.c  exec.c  forkexec.c ...
#### 文件系統相關
list.c  open.c echo.c  copy.c  ... 
#### 進程間通信相關
 pipe1.c  pipe2.c  redirect.c ...

---
## 分析UNIX/Linux類應用
 例如：[copy.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/copy.c)，將輸入複製到輸出
從輸入中讀取字節，將其寫入輸出中

        $ copy

  copy.c是用C語言編寫的
    
  read()和write()是系統調用
  read()/write()第一個參數是"文件描述符"(fd)
  傳遞給內核，告訴它要讀/寫哪個 "打開的文件"。

---
## 分析UNIX/Linux類應用

必須先前已經打開過的一個FD（描述符）連接到一個文件/設備/socket
一個進程可以打開許多文件，有許多描述符
UNIX慣例：FD： 0是 "標準輸入"，1是 "標準輸出"


read()第二個參數是一個指針，指向要讀入的一些內存。

read()第三個參數是要讀取的最大字節數

注：read()可以少讀，但不能多讀


---
## 分析UNIX/Linux類應用

返回值：實際讀取的字節數，或者-1表示錯誤
注意：copy.c並不關心數據的格式。
UNIX的I/O是8位字節
解釋是特定於應用的，例如數據庫記錄、C源碼等
文件描述符從何而來？


---
## 分析UNIX/Linux類應用

例如：[open.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/open.c)，創建一個文件

    $ open
    $ cat output.txt

open() 創建一個文件，返回一個文件描述符（或-1表示錯誤）。
FD是一個小整數，FD索引到一個由內核維護的每進程表中

不同的進程有不同的FD命名空間。例如，FD 1對不同的進程意味不同

進一步細節可以參考UNIX手冊，例如 "man 2 open"。 
man 1是shell命令如ls；man 2是系統調用如open；man 3是函數說明

---
## 分析UNIX/Linux類應用

當程序調用open()這樣的系統調用時會發生什麼？

- 看起來像一個函數調用，但它實際上是一個特殊的指令
- 硬件保存了一些用戶寄存器
- 硬件提高權限級別
- 硬件跳轉到內核中一個已知的 "入口點"
- 現在在內核中運行C代碼


---
## 分析UNIX/Linux類應用

當程序調用open()這樣的系統調用時會發生什麼？

- 內核調用系統調用實現
- open() 在文件系統中查找名字
- 它可能會等待磁盤的到來
- 更新內核數據結構（緩存，FD表）
- 恢復用戶寄存器
- 降低權限級別
- 跳回程序中的調用點，繼續運行
- 我們將在後面的課程中看到更多的細節

---
## 分析UNIX/Linux類應用

在向UNIX的命令行界面（shell）輸入信息。
shell打印出"$"的提示。
shell讓你運行UNIX的命令行工具
對系統管理、處理文件、開發和編寫腳本很有用

    $ ls
    $ ls > out
    $ grep x < out

---
## 分析UNIX/Linux類應用

但通過shell來支持分時共享多任務執行是UNIX設計之初的重點。
可以通過shell行使許多系統調用。

shell為你輸入的每個命令創建一個新的進程，例如，對於

    $ echo hello



---


## 分析UNIX/Linux類應用
fork()系統調用創建一個新的進程

    $ fork

內核創建一個調用進程的副本
- 指令、數據、寄存器、文件描述符、當前目錄
- "父 "和 "子 "進程

---


## 分析UNIX/Linux類應用

唯一的區別：fork()在父進程中返回一個pid，在子進程中返回0。
pid（進程ID）是一個整數，內核給每個進程一個不同的pid

因此，[fork.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/fork.c)的 "fork()返回 "在**兩個**進程中都會執行
"if(pid == 0) "實現對父子進程的區分

---
## 分析UNIX/Linux類應用

我們怎樣才能在這個進程中運行一個新程序呢？  

例如：[exec.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/exec.c)，用一個可執行文件代替調用進程。
shell是如何運行一個程序的，例如

    $ echo a b c

一個程序被儲存在一個文件中：指令和初始內存，由編譯器和鏈接器創建
所以有一個叫echo的文件，包含對 `exec` 系統調用的操作命令

---
## 分析UNIX/Linux類應用

exec()用一個可執行文件取代當前進程
- 丟棄指令和數據存儲器
- 從文件中加載指令和內存
- 保留了文件描述符

---
## 分析UNIX/Linux類應用

exec(filename, argument-array)
argument-array保存命令行參數；exec傳遞給main()

    cat user/echo.c

echo.c顯示了一個程序如何看待它的命令行參數

---
## 分析UNIX/Linux類應用

例如：[forkexec.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/forkexec.c)，fork()一個新進程，exec()一個程序。

      $ forkexec

forkexec.c包含了一個常見的UNIX習慣用語。
- fork() 一個子進程
- exec() 子進程中的一條命令
- 父進程等待子進程完成


---
## 分析UNIX/Linux類應用

shell對你輸入的每個命令都進行fork/exec/wait操作。
在wait()之後，shell會打印出下一個提示信息
在後臺運行 -- `&` -- , shell會跳過wait()


---
## 分析UNIX/Linux類應用

exit(status) --> wait(&status)

status約定：0 = 成功，1 = 命令遇到了一個錯誤
注意：fork()會複製，但exec()會丟棄複製的內存。
這可能看起來很浪費
你可以通過 "寫時複製 "技術透明地消除複製


---
## 分析UNIX/Linux類應用

例子：[redirect.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/redirect.c)，重定向一個命令的輸出
shell對此做了什麼？

    $ echo hello > out
 
答案：fork，改變子進程的FD1，執行echo

    $ redirect
    $ cat output.txt

---
## 分析UNIX/Linux類應用

注意：open()總是選擇最低的未使用的FD；選擇1是由於close(1)。
fork、FD和exec很好地互動，以實現I/O重定向
獨立的fork-then-exec給子進程一個機會在exec之前改變FD。
FDs提供了指示作用
命令只需使用FDs 0和1，不需要知道它們的位置
exec保留了sh設置的FDs
因此：只有sh需要知道I/O重定向，而不是每個程序



---
## 分析UNIX/Linux類應用

一些值得思考的問題：
- 為什麼是這些I/O和進程的抽象？為什麼不是其他的東西？
- 為什麼要提供一個文件系統？為什麼不讓程序以他們自己的方式使用磁盤？
- 為什麼是FDs？為什麼不向write()傳遞一個文件名？
- 為什麼文件是字節流，而不是磁盤塊或格式化記錄？
- 為什麼不把fork()和exec()結合起來？

UNIX的設計很好用，但我們會看到其他的設計

---
## 分析UNIX/Linux類應用

例子：[pipe1.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/pipe1.c)，通過一個管道進行通信
shell是如何實現的

    $ ls | grep x
    $ pipe1

一個FD可以指一個 "管道"，也可以指一個文件。
pipe()系統調用創建了兩個FD
- 從第一個FD中讀取
- 寫入第二個FD
  

---
## 分析UNIX/Linux類應用

內核為每個管道維護一個緩衝區
- write()添加到緩衝區中
- read()等待，直到有數據出現

---
## 分析UNIX/Linux類應用

例子：[pipe2.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/pipe2.c)，在進程間通信。
管道與fork()結合得很好，可以實現ls | grep x。
shell創建一個管道。
然後分叉（兩次）。
然後將ls的FD1連接到管道的寫FD。
和grep的FD 0連接到管道上。

   $ pipe2 -- 一個簡化版本

管道是一個獨立的抽象概念，但與 fork() 結合得很好


---
## 分析UNIX/Linux類應用


* 例子：[list.c](https://pdos.csail.mit.edu/6.828/2021/lec/l-overview/list.c)，列出一個目錄中的文件
ls是如何獲得一個目錄中的文件列表的？
你可以打開一個目錄並讀取它 -> 文件名
"... "是一個進程的當前目錄的假名
更多細節見ls.c

---
## 分析UNIX/Linux類應用

小結

  * 我們已經研究了UNIX的I/O、文件系統和進程的抽象
  * 這些接口很簡單，只有整數和I/O緩衝區
  * 這些抽象結合得很好，例如，I/O重定向