# 2020-12-20 更新

* 說明了子進程機制；
* 在基礎系統調用中，補充了 open/close/pipe 的相關說明；
* 將 kill 移動到拓展系統調用；
# 實現細節約定

* 以下 int/i32 均指有符號 32 位整數。（然而出於實現方便可以進行一些調整，比如將所有的返回值都調整為 64 位有符號整數 long long/i64）
# 子進程機制

當一個進程通過 exit 系統調用或者由於出錯退出之後，它應當被標記為處於殭屍（Zombie）狀態，此時可以儘可能多的回收資源，但不是全部。需要等待它的父進程在 waitpid 系統調用中 wait 到這個子進程的時候，該子進程的資源（包括進程控制塊 PCB）才被全部回收。

一個進程 fork 出來的進程會成為它的子進程，一般來說它需要負責通過 waitpid 系統調用來回收子進程的資源。然而，如果一個進程在子進程還在運行的時候退出，它的所有子進程需要被轉移到進程 initproc 下面。

在內核初始化之後，需要加載唯一的用戶進程 initproc，參考實現如下：

```rust
#[no_mangle]
fn main() -> i32 {
    if fork() == 0 {
        exec("user_shell\0");
    } else {
        loop {
            let mut exit_code: i32 = 0;
            let pid = wait(&mut exit_code);
            if pid == -1 {
                yield_();
                continue;
            }
            println!(
                "[initproc] Released a zombie process, pid={}, exit_code={}",
                pid,
                exit_code,
            );
        }
    }
    0
}
```
可以看到它 fork 了一個子進程並運行用戶終端 user_shell。它自身則是不斷循環 wait，來回收那些被轉移到它下面的子進程的資源。
# 基礎系統調用接口

## open

syscall ID：56

功能：打開一個文件，並返回可以訪問它的文件描述符。

C 接口：int open(char* path, unsigned int flags);

Rust 接口：fn open(path: *const u8, flags: u32);

參數：**fd**描述要打開的文件的文件名（簡單起見，文件系統不需要支持目錄，所有的文件都放在根目錄 / 下），**flags**描述打開文件的標誌，具體含義見備註。

返回值：如果出現了錯誤則返回 -1，否則返回可以訪問給定文件的文件描述符。

可能的錯誤：文件不存在。

備註：在分配文件描述符的時候，總是會選取所有可能的文件描述符中編號最小的一個。參考 xv6，打開文件的 flags 支持以下幾種：

* 如果 flags 為 0，則表示以只讀模式*RDONLY*打開；
* 如果 flags 第 0 位被設置（0x001），表示以只寫模式*WRONLY*打開；
* 如果 flags 第 1 位被設置（0x002），表示既可讀又可寫*RDWR*；
* 如果 flags 第 9 位被設置（0x200），表示允許創建文件*CREATE*，在找不到該文件的時候應創建文件；如果該文件已經存在則應該將該文件的大小歸零；
* 如果 flags 第 10 位被設置（0x400），則在打開文件的時候應該將該文件的大小歸零，也即*TRUNC*。
## close

syscall ID：57

功能：關閉一個文件。

C 接口：int close(int fd);

Rust 接口：fn close(fd: i32) -> i32;

參數：**fd**描述一個文件，可能是索引節點/管道/串口。

返回值：如果出現了錯誤則返回 -1，否則返回 0。

可能的錯誤：傳入的文件描述符 fd 並未被打開。

## pipe

syscall ID：59

功能：建立一個管道，用於當前進程及其子進程之間的通信。

C 接口：int pipe(int pipefd[2]);

Rust 接口：fn pipe(pipefd: &mut [i32]) -> i32;

參數：**pipefd**描述一個大小為 2 的 fd 數組，前一項為管道輸入端的 fd，後一項為管道輸出端的 fd。

返回值：如果出現了錯誤則返回 -1，否則返回 0。

可能的錯誤：傳入的地址 pipefd 不合法；

備註：在分配文件描述符的時候，總是會選取所有可能的文件描述符中編號最小的一個。

## read

syscall ID：63

功能：從文件中讀取一段內容到內存中的緩衝區。

C 接口：int read(int fd, char *buf, int len);

Rust 接口： fn read(fd: i32, buf: *mut u8, len: i32) -> i32;

參數：**fd**描述當前進程需要訪問的文件，**buf**表示保存文件中讀到的數據的緩衝區的地址，**len**表示最大的讀取字節數。

返回值：如果出現了錯誤則返回 -1，否則返回實際讀到的字節數。

可能的錯誤：傳入的**fd**不合法；

備註：該 syscall 的實現可能是阻塞的。

## write

syscall ID：64

功能：從內存中的緩衝區寫入一段內容到文件。

C 接口：int write(int fd, char *buf, int len);

Rust 接口：fn write(fd: i32, buf: *mut u8, len: i32) -> i32;

參數：**fd**描述當前進程需要訪問的文件，**buf**表示保存即將寫入文件的數據的緩衝區的地址，**len**表示最大的寫入字節數。

返回值：如果出現了錯誤則返回 -1，否則返回實際寫入的字節數。

可能的錯誤：傳入的**fd**不合法；

備註：該 syscall 的實現可能是阻塞的。

## exit

syscall ID：93

功能：退出當前進程。

C 接口：int exit(int status);

Rust 接口：fn exit(status: i32) -> i32;

參數：**status**描述當前進程的返回值，並應當由其父進程捕獲到。

返回值：正常情況下應不會返回。請在調用 exit 之後加入 panic 語句來確保這一點。

可能的錯誤：觸發了調用 exit 之後的 panic；

## sleep

syscall ID：101

功能：將當前進程休眠一段時間。

C 接口：int sleep(int n);

Rust 接口：fn sleep(n: i32) -> i32;

參數：**n**描述將當前進程休眠多少個時間單位，採用哪種時間單位待定，可選項：時間片個數/毫秒數/ CPU 時鐘週期數，請幫忙確定。暫定為毫秒數。

返回值：總是返回 0。

可能的錯誤：無。

備註：該 syscall 的實現可能是阻塞的。

## yield

syscall ID：124

功能：主動交出當前進程的 CPU 使用權，從而使得 CPU 可以執行其他進程。

C 接口：int yield();

Rust 接口：fn yield() -> i32;

參數：無參數。

返回值：總是返回 0。

可能的錯誤：無。

## gettime

syscall ID：169

功能：獲取當前時間。

C 接口：int gettime(unsigned long long* time);

Rust 接口：fn gettime(time: *mut u64) -> i32;

參數：將當前時間保存在地址**time**處。時間的單位待定，可選為毫秒數/ CPU 時鐘週期數，請幫忙確定。暫定為毫秒數。

返回值：總是返回 0。

可能的錯誤：無。

## getpid

syscall ID：172

功能：獲取當前進程的進程 ID。

C 接口：int getpid();

Rust 接口：fn getpid() -> i32;

參數：無參數。

返回值：返回當前進程的進程 ID。

可能的錯誤：無。

## fork

syscall ID：220

功能：生成一個子進程，其地址空間與當前進程（也稱父進程）完全相同，且和父進程一樣，回到用戶態之後都是從系統調用的下一條指令開始執行。

C 接口：int fork();

Rust 接口：fn fork() -> i32;

參數：無參數。

返回值：如果出現了錯誤則返回 -1；否則對於父進程，返回子進程的進程 ID；對於子進程則返回 0。

可能的錯誤：生成子進程的過程中會分配新的物理頁框，如果物理頁框不足則應該撤銷所有操作，放棄生成子進程並返回錯誤；

## exec

syscall ID：221

功能：替換當前進程的地址空間為一個程序，且返回用戶態之後從該程序的入口點開始執行。還需要初始化當前進程的運行棧支持帶有參數。

C 接口：int exec(char *file, char *argv[]);

Rust 接口：fn exec(file: *const u8, argv: *const *const u8);

參數：**file**表示將要替換到的程序的文件名，**argv**表示新程序的執行參數。

返回值：如果出現了錯誤則返回 -1；否則不應該返回。

可能的錯誤：**file**不存在；需要分配物理頁框而物理頁框不足，此時應該撤銷所有操作並返回錯誤。

## waitpid

syscall ID：260

功能：當前進程等待一個子進程結束，並獲取其返回值。

C 接口：int waitpid(int pid, int *status);

Rust 接口： fn waitpid(pid: i32, status: *mut i32) -> i32;

參數：**pid**表示要等待結束的子進程的進程 ID，如果為 0 的話表示等待任意一個子進程結束；**status**表示保存子進程返回值的地址，如果這個地址為 0 的話表示不必保存。

返回值：如果出現了錯誤則返回 -1；否則返回結束的子進程的進程 ID。

可能的錯誤：如果在調用時找不到符合要求的子進程（當前進程沒有子進程或者 pid!= 0 而當前進程沒有 pid 相符的子進程）則返回錯誤；傳入的地址 status 不為 0 但是不合法；

備註：該 syscall 的實現可能是阻塞的。

# 拓展系統調用接口

## kill

syscall ID：129

功能：殺死一個進程。

C 接口：int kill(int pid);

Rust 接口：fn kill(pid: i32) -> i32;

參數：**pid**表示要殺死的進程的進程 ID。

返回值：如果殺死當前進程的話則不返回。如果出現了錯誤則返回 -1，否則返回 0。

可能的錯誤：嘗試殺死初始用戶進程 initproc；不存在對應 pid 的進程；

備註：在 kill 一個目前正處於阻塞狀態的進程的時候情況比較複雜，隨著其處於的阻塞狀態的不同，需要討論更加明確的語義，請幫忙一同確定。

# 參考內容

[xv6 實驗指導書]([https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf](https://pdos.csail.mit.edu/6.828/2020/xv6/book-riscv-rev1.pdf))

[之前總結的用戶程序支持文檔]([https://github.com/wyfcyx/osnotes/blob/master/book/v3/%E7%94%A8%E6%88%B7%E7%A8%8B%E5%BA%8F%E6%94%AF%E6%8C%81.md](https://github.com/wyfcyx/osnotes/blob/master/book/v3/%E7%94%A8%E6%88%B7%E7%A8%8B%E5%BA%8F%E6%94%AF%E6%8C%81.md))


