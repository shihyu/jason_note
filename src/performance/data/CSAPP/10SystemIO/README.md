<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [第十章：系統級I/O](#%E7%AC%AC%E5%8D%81%E7%AB%A0%E7%B3%BB%E7%BB%9F%E7%BA%A7io)
  - [10.1 Unix I/O](#101-unix-io)
  - [10.2 文件](#102-%E6%96%87%E4%BB%B6)
  - [10.3 打開和關閉文件](#103-%E6%89%93%E5%BC%80%E5%92%8C%E5%85%B3%E9%97%AD%E6%96%87%E4%BB%B6)
  - [10.4 讀和寫文件](#104-%E8%AF%BB%E5%92%8C%E5%86%99%E6%96%87%E4%BB%B6)
  - [10.5 用RIO包健壯地讀寫](#105-%E7%94%A8rio%E5%8C%85%E5%81%A5%E5%A3%AE%E5%9C%B0%E8%AF%BB%E5%86%99)
  - [10.6 讀取文件元數據](#106-%E8%AF%BB%E5%8F%96%E6%96%87%E4%BB%B6%E5%85%83%E6%95%B0%E6%8D%AE)
  - [10.7 讀取目錄內容](#107-%E8%AF%BB%E5%8F%96%E7%9B%AE%E5%BD%95%E5%86%85%E5%AE%B9)
  - [10.8 共享文件](#108-%E5%85%B1%E4%BA%AB%E6%96%87%E4%BB%B6)
  - [10.9 I/O重定向](#109-io%E9%87%8D%E5%AE%9A%E5%90%91)
  - [10.10 標準I/O](#1010-%E6%A0%87%E5%87%86io)
  - [10.11 綜合：我該使用哪些I/O函數？](#1011-%E7%BB%BC%E5%90%88%E6%88%91%E8%AF%A5%E4%BD%BF%E7%94%A8%E5%93%AA%E4%BA%9Bio%E5%87%BD%E6%95%B0)
  - [資料補充](#%E8%B5%84%E6%96%99%E8%A1%A5%E5%85%85)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

# 第十章：系統級I/O

輸入輸出（IO）是在主存和外部設備（磁盤驅動器、終端、網絡）之間複製數據的過程。
- 輸入操作是從IO設備到主存，輸出操作是從主存到IO設備。
- 所有運行時系統都提供執行IO的較高級別的工具，例如ANSI C提供標準IO庫，包含printf、scanf這樣的帶緩衝IO函數，C++語言IO庫提供`<< >>`運算符用於輸入輸出。
- 在Linux系統中，可以通過內核提供的系統級Unix IO函數實現這些教高級別的輸出輸出功能的。
- 某些時候，無法選擇或者高層IO接口不是一個好選擇，除了使用底層IO接口別無選擇。比如網絡編程中、需要獲取文件元數據等場景。

## 10.1 Unix I/O

一個Linux文件就是一個某長度字節的序列，所有的IO設備都被模型化為**文件**，而所有的輸入輸出都被當做對相應文件的讀和寫來執行。
- 這種將設備優雅地映射為文件的方式，允許Linux內核引出一個簡單的、低級的應用接口，稱之為Unix I/O。使得所有輸入輸出能夠以統一方式來執行：
- 打開文件：應用程序通過要求內核打開相應文件，來宣告它想要訪問一個I/O設備。內核返回一個小的非負整數，叫做描述符，後續對文件的所有操作都基於文件描述符。內核記錄著打開文件的所有信息，應用程序只需要記住這個描述符。
- Linux Shell創建的每個進程開始時都有三個打開的文件，標準輸入、標準輸出、標準錯誤輸出，文件描述符分別為0、1、2，使用常量`STDIN_FILENO STDOUT_FILENO STDERR_FILENO`來表示。
- 改變文件當前位置：對於每個打開文件，內核維護著一個當前位置k，初始為0，這個值是從文件開頭開始的字節偏移量。通過`seek`操作可以改變當前位置。
- 讀寫文件：讀操作就是從文件複製n字節到內存，從當前文件位置k開始增加到k+n，如果k+n大於文件大小，就會觸發EOF（End-Of-File）條件，應用程序能夠檢測這個條件，文件尾並沒有明確的EOF符號。類似地，寫操作就是從內存複製n字節到文件，從當前文件k開始，然後更新k。
- 關閉文件：當應用完成對文件的訪問之後，它會通知內核關閉這個文件，作為響應，內核會釋放打開時創建的數據結構，並將文件描述符恢復到可用的描述符池中。無論一個進程因為何種原因終止，內核都會自動關閉它打開的文件，並釋放它們的內存資源。

## 10.2 文件

每個Linux文件都有一個類型：
- 普通文件：包含任意數據，可能是文本文件或者二進制文件，對內核沒有差別，只在應用程序處理中存在差別。文件文件是一個文本行序列，每一個文本行以`\n`即LF作為結尾。
- 目錄（directory）：包含一組鏈接（link）的文件，其中每個鏈接都將一個文件名映射到一個文件，這個文件也可能是目錄。其中至少包含兩個文件，`. ..`映射到當前目錄和上一級目錄。
- 套接字（socket）：是和另一個進程進行跨進程通信的文件。
- 其他文件類型：命名管道、符號鏈接、字符和塊設備。

Linux將所有文件組織成一個目錄層次的樹形結構（directory hierarchy），根目錄是`/`。

作為上下文的一部分，每個進程都有一個當前工作目錄（current working directory），來確定其目錄層次結構中的當前位置，可以用`cd`命令修改shell中的當前工作目錄。
- 目錄層次中的位置用路徑名（pathname）來指定。
- 路徑名是一個字符串，可以是絕對路徑或者相對路徑。

## 10.3 打開和關閉文件

打開文件：
```C
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
int open(const char *pathname, int flags);
int open(const char *pathname, int flags, mode_t mode);
int creat(const char *pathname, mode_t mode);
int openat(int dirfd, const char *pathname, int flags);
int openat(int dirfd, const char *pathname, int flags, mode_t mode);
```
- `flags`訪問模式：
    - 讀寫權限：`O_RDONLY O_WRONLY R_RDWR`表示只讀、只寫、可讀可寫。
    - 可以或上更多掩碼：`O_CREAT O_TRUNC O_APPEND`表示創建、截斷、添加到末尾。
- `mode`參數給定新文件的訪問權限：
    - 作為上下文一部分，每個進程有一個`umask`，可以通過調用`umask`函數設置：
    ```C
    #include <sys/types.h>
    #include <sys/stat.h>
    mode_t umask(mode_t mask);
    ```
    - `open creat`創建新文件時，文件權限位被設置為`mode & ~umask`。
    - 掩碼或者訪問權限位：
    - `S_IRUSR S_IWUSR S_IXUSR`：擁有者可以讀、寫、執行。
    - `S_IRGRP S_IWGRP S_IXGRP`：擁有者同組可以讀、寫、執行。
    - `S_IROTH S_IWOTH S_IXOTH`：其他人可以讀、寫、執行。

關閉文件：
```C
#include <unistd.h>
int close(int fd);
```

## 10.4 讀和寫文件

讀寫文件：
```C
#include <unistd.h>
ssize_t read(int fd, void *buf, size_t count);
ssize_t write(int fd, const void *buf, size_t count);
```
- `read`從文件中讀取至多`count`字節到內存位置`buf`，返回實際讀取的數量，`-1`表示錯誤，可能為0（如果直接遇到EOF）。
- `write`從`buf`中寫入`count`字節到文件`fd`當前文件位置。

更改當前位置：
```C
#include <sys/types.h>
#include <unistd.h>
off_t lseek(int fd, off_t offset, int whence);
```

`sszie_t size_t`區別：
- 前者有符號，可以表示負數，後者無符號，通常用來表示長度、大小。

不足值：
- `read write`某些時候傳送的字節比應用程序要求的少。
- 讀磁盤文件除了`EOF`不會有，寫磁盤文件也不會有。
- 從標準輸入讀取，一行緩衝一次，返回一行的內容。
- 讀寫網絡套接字，可能因為緩衝和延遲導致`read write`實際讀寫數量不足。
- 管道調用`read write`也可能不足。
- 這些不是錯誤，而是程序行為，不應該僅依賴傳入的字節數來保證，而應該檢查返回值，適當重新調用。

## 10.5 用RIO包健壯地讀寫

可以使用`read write`實現會自動處理不足值的健壯IO函數，通過循環檢查返回值在不足或者被中斷時自動重新調用，直到所有字節傳輸完成再返回。實現略。

## 10.6 讀取文件元數據

應用程序能夠調用`stat fstat`函數，檢索關於文件的信息：
```C
#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
int stat(const char *pathname, struct stat *statbuf);
int fstat(int fd, struct stat *statbuf);
int lstat(const char *pathname, struct stat *statbuf);
#include <fcntl.h>           /* Definition of AT_* constants */
#include <sys/stat.h>
int fstatat(int dirfd, const char *pathname, struct stat *statbuf,
            int flags);
```
- `struct stat`數據結構文件的元數據：
```C
struct stat {
    dev_t     st_dev;         /* ID of device containing file */
    ino_t     st_ino;         /* Inode number */
    mode_t    st_mode;        /* File type and mode */
    nlink_t   st_nlink;       /* Number of hard links */
    uid_t     st_uid;         /* User ID of owner */
    gid_t     st_gid;         /* Group ID of owner */
    dev_t     st_rdev;        /* Device ID (if special file) */
    off_t     st_size;        /* Total size, in bytes */
    blksize_t st_blksize;     /* Block size for filesystem I/O */
    blkcnt_t  st_blocks;      /* Number of 512B blocks allocated */

    /* Since Linux 2.6, the kernel supports nanosecond
       precision for the following timestamp fields.
       For the details before Linux 2.6, see NOTES. */

    struct timespec st_atim;  /* Time of last access */
    struct timespec st_mtim;  /* Time of last modification */
    struct timespec st_ctim;  /* Time of last status change */

#define st_atime st_atim.tv_sec      /* Backward compatibility */
#define st_mtime st_mtim.tv_sec
#define st_ctime st_ctim.tv_sec
};
```
- `st_mode`編碼了文件訪問許可位和文件類型，`sys/stat.h`中定義了一些宏函數來確定`st_mode`中的文件類型：
    - `S_ISREG(m) S_ISDIR(m) S_ISSOCK(m)`表示是普通文件、目錄文件、套接字。

## 10.7 讀取目錄內容

- 打開目錄，得到一個指向目錄流`DIR`的指針。
```C
#include <sys/types.h>
#include <dirent.h>
DIR *opendir(const char *name);
DIR *fdopendir(int fd);
```
- 讀取目錄：每次調用返回指向目錄流中下一目錄項的指針，如果沒有更多目錄項則返回NULL。
```C
#include <dirent.h>
struct dirent *readdir(DIR *dirp);

struct dirent {
    ino_t          d_ino;       /* Inode number */
    off_t          d_off;       /* Not an offset; see below */
    unsigned short d_reclen;    /* Length of this record */
    unsigned char  d_type;      /* Type of file; not supported
                                   by all filesystem types */
    char           d_name[256]; /* Null-terminated filename */
};
```
- `dirent`中只有`d_ino d_name`是標準的，前者是文件名，後者是文件位置。
- 出錯會返回NULL，並設置errno。區分錯誤和流結束的方式只有檢查errno前後是否修改過。
- 關閉目錄：
```C
#include <sys/types.h>
#include <dirent.h>
int closedir(DIR *dirp);
```
- 關閉流並釋放其所有資源。

## 10.8 共享文件

Linux有許多方式可以用來共享文件，需要弄清楚內核如何表示打開文件才能才能理解文件共享，內核用三個相關的數據結構來表示打開文件：
- **描述符表**（descriptor table）：每個進程都有獨立的描述符表，表項使用文件描述符索引。每個打開的文件描述符表項指向文件表中的一個表項。
- **文件表**：打開文件的集合由一張文件表來表示，所有進程共享這張表。每個文件表表項包括當前文件位置、引用計數、指向v-node表中對應表項的指針。關閉一個描述符會遞減引用計數，知道引用計數為零，內核才會刪除這個表項。
- **v-node表**：所有進程共享，每個表項包含`stat`結構中的大多數信息，包括`st_mode st_size`成員。

文件共享：
- 可以通過多次調用`open`打開同一個文件來共享文件，此時得到的多個描述符不同，他們指向的文件表項也不同，文件表項中保存的文件位置也不同。不過最終指向的v-node表項是相同的。
- 父子進程則不同，子進程擁有父進程文件描述符表的副本，父子進程共享相同的文件表項，因此共享表項中相同的文件位置，但是不共享描述符表。

## 10.9 I/O重定向

Linux Shell提供I/O重定向操作符，允許用戶將磁盤文件和標準輸入輸出練習起來，比如：
```shell
ls > foo.txt
```
- 使shell執行`ls`文件，並且將標準輸出文件重定向到磁盤文件`foo.txt`。
- 那麼IO重定向是如何工作的呢，一個典型手段是使用`dup`函數：
```C
#include <unistd.h>
int dup(int oldfd);
int dup2(int oldfd, int newfd);
#define _GNU_SOURCE             /* See feature_test_macros(7) */
#include <fcntl.h>              /* Obtain O_* constant definitions */
#include <unistd.h>
int dup3(int oldfd, int newfd, int flags);
```
- `dup`返回一個新的複製的文件描述符，`dup2`則是將就`oldfd`複製到`newfd`，如果`newfd`已經打開，那麼會被靜默關閉。
- 複製描述符的意思就是複製對應的描述符表項，複製得到的和原文件描述符表項將指向同一個文件表項，共享同一個文件位置，共享同一個文件表項中的引用計數。
- 出錯返回-1，成功將返回新的文件描述符。
- 例子：使用`dup(5, STDIN_FILENO)`即可將標準輸入重定位到描述符5對應文件，那麼此時從標準輸入讀取內容時就會從改文件讀取。

## 10.10 標準I/O

C語言定義了一組高級輸入輸出函數，稱為標準I/O庫，這個庫提供了：
- 打開關閉文件：`fopen fclose`。
- 按字節讀寫文件：`fread fwrite`。
- 讀寫字符串函數：`fgets fputs`。
- 以及複雜的格式化函數：`fscanf fprintf`。
- 這些函數有些有標準輸入輸出版本，對應於使用標準輸出輸出流`stdin stdout stderr`。
- 標準輸入輸出流類型是`struct FILE`，是對文件描述符和流緩衝區的抽象。

## 10.11 綜合：我該使用哪些I/O函數？

無論是自己實現的可靠的IO函數，還是C標準庫提供的跨平臺IO函數，在Unix平臺都是基於底層Unix IO系統調用的。
- 在用戶程序中，可以使用任意一者進行IO。
- 那麼如何選擇呢，基本指導原則是：
    - 只有有可能就使用標準IO，標準IO已經處理了緩衝區、格式化等問題，並且還跨平臺。
    - 不要使用格式化IO函數來讀取二進制文件，標準接口都是讀取文本文件的。應該自己編寫Unix IO的包裝來做這件事情（如果要跨平臺，那麼最好先定義一套跨平臺接口，而不是直接用Unix IO）。
    - 用於網絡IO時，最好自己實現一套接口（雖然使用Unix IO也是可行的，但最好在此基礎上實現一套更健壯的IO函數），不能使用標準輸入輸出。

## 資料補充

- APUE，TLPL。