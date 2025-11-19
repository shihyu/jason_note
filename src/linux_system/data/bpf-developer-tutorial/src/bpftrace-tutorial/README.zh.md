# bpftrace一行教程

該教程通過12個簡單小節幫助你瞭解bpftrace的使用。每一小節都是一行的命令，你可以嘗試運行並立刻看到運行效果。該教程系列用來介紹bpftrace的概念。關於bpftrace的完整參考，見[bpftrace手冊](https://github.com/iovisor/bpftrace/blob/master/man/adoc/bpftrace.adoc)。

該教程貢獻者是Brendan Gregg, Netflix (2018), 基於他的FreeBSD DTrace教程系列[DTrace Tutorial](https://wiki.freebsd.org/DTrace/Tutorial)。

# 1. 列出所有探針

```
bpftrace -l 'tracepoint:syscalls:sys_enter_*'
```

"bpftrace -l" 列出所有探針，並且可以添加搜索項。

- 探針是用於捕獲事件數據的檢測點。
- 搜索詞支持通配符，如`*`和`?`。
- "bpftrace -l" 也可以通過管道傳遞給grep，進行完整的正則表達式搜索。

# 2. Hello World

```
# bpftrace -e 'BEGIN { printf("hello world\n"); }'
Attaching 1 probe...
hello world
^C
```

打印歡迎消息。運行後, 按Ctrl-C結束。

- `BEGIN`是一個特殊的探針，在程序開始時觸發探針執行(類似awk的BEGIN)。你可以使用它設置變量和打印消息頭。
- 探針可以關聯動作，把動作放到{}中。這個例子中，探針被觸發時會調用printf()。

# 3. 文件打開

```
# bpftrace -e 'tracepoint:syscalls:sys_enter_openat { printf("%s %s\n", comm, str(args.filename)); }'
Attaching 1 probe...
snmp-pass /proc/cpuinfo
snmp-pass /proc/stat
snmpd /proc/net/dev
snmpd /proc/net/if_inet6
^C
```

這裡我們在文件打開的時候打印進程名和文件名。

- 該命令以`tracepoint:syscalls:sys_enter_openat`開始: 這是tracepoint探針類型(內核靜態跟蹤)，當進入`openat()`系統調用時執行該探針。相比kprobes探針(內核動態跟蹤，在第6節介紹)，我們更加喜歡用tracepoints探針，因為tracepoints有穩定的應用程序編程接口。注意：現代linux系統(glibc >= 2.26)，`open`總是調用`openat`系統調用。
- `comm`是內建變量，代表當前進程的名字。其它類似的變量還有pid和tid，分別表示進程標識和線程標識。
- `args`是一個包含所有tracepoint參數的結構。這個結構是由bpftrace根據tracepoint信息自動生成的。這個結構的成員可以通過命令`bpftrace -vl tracepoint:syscalls:sys_enter_openat`找到。
- `args.filename`用來獲取args的成員變量`filename`的值。
- `str()`用來把字符串指針轉換成字符串。

# 4. 進程級系統調用計數

```
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @[comm] = count(); }'
Attaching 1 probe...
^C

@[bpftrace]: 6
@[systemd]: 24
@[snmp-pass]: 96
@[sshd]: 125
```

按Ctrl-C後打印進程的系統調用計數。

- @: 表示一種特殊的變量類型，稱為map，可以以不同的方式來存儲和描述數據。你可以在@後添加可選的變量名(如@num)，用來增加可讀性或者區分不同的map。
- [] 可選的中括號允許設置map的關鍵字，比較像關聯數組。
- count(): 這是一個map函數 - 記錄被調用次數。因為調用次數根據comm保存在map裡，輸出結果是進程執行系統調用的次數統計。

Maps會在bpftrace結束(如按Ctrl-C)時自動打印出來。

# 5. read()返回值分佈統計

```
# bpftrace -e 'tracepoint:syscalls:sys_exit_read /pid == 18644/ { @bytes = hist(args.ret); }'
Attaching 1 probe...
^C

@bytes:
[0, 1]                12 |@@@@@@@@@@@@@@@@@@@@                                |
[2, 4)                18 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                     |
[4, 8)                 0 |                                                    |
[8, 16)                0 |                                                    |
[16, 32)               0 |                                                    |
[32, 64)              30 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[64, 128)             19 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                    |
[128, 256)             1 |@
```

這裡統計進程號為18644的進程執行內核函數sys_read()的返回值，並打印出直方圖。
- /.../: 這裡設置一個過濾條件(條件判斷)，滿足該過濾條件時才執行{}裡面的動作。在這個例子中意思是隻追蹤進程號為18644的進程。過濾條件表達式也支持布爾運算，如("&&", "||")。
- ret: 表示函數的返回值。對於sys_read()，它可能是-1(錯誤)或者成功讀取的字節數。
- @: 類似於上節的map，但是這裡沒有key，即[]。該map的名稱"bytes"會出現在輸出中。
- hist(): 一個map函數，用來描述直方圖的參數。輸出行以2次方的間隔開始，如`[128, 256)`表示值大於等於128且小於256。後面跟著位於該區間的參數個數統計，最後是ascii碼錶示的直方圖。該圖可以用來研究它的模式分佈。
- 其它的map函數還有lhist(線性直方圖)，count()，sum()，avg()，min()和max()。

# 6. 內核動態跟蹤read()返回的字節數

```
# bpftrace -e 'kretprobe:vfs_read { @bytes = lhist(retval, 0, 2000, 200); }'
Attaching 1 probe...
^C

@bytes:
(...,0]                0 |                                                    |
[0, 200)              66 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[200, 400)             2 |@                                                   |
[400, 600)             3 |@@                                                  |
[600, 800)             0 |                                                    |
[800, 1000)            5 |@@@                                                 |
[1000, 1200)           0 |                                                    |
[1200, 1400)           0 |                                                    |
[1400, 1600)           0 |                                                    |
[1600, 1800)           0 |                                                    |
[1800, 2000)           0 |                                                    |
[2000,...)            39 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@                      |
```

使用內核動態跟蹤技術顯示read()返回字節數的直方圖。

- `kretprobe:vfs_read`: 這是kretprobe類型(動態跟蹤內核函數返回值)的探針，跟蹤`vfs_read`內核函數。此外還有kprobe類型的探針(在下一節介紹)用於跟蹤內核函數的調用。它們是功能強大的探針類型，讓我們可以跟蹤成千上萬的內核函數。然而它們是"不穩定"的探針類型:由於它們可以跟蹤任意內核函數，對於不同的內核版本，kprobe和kretprobe不一定能夠正常工作。因為內核函數名，參數，返回值和作用等可能會變化。此外，由於它們用來跟蹤底層內核的，你需要瀏覽內核源代碼，理解這些探針的參數和返回值的意義。
- lhist(): 線性直方圖函數:參數分別是value，最小值，最大值，步進值。第一個參數(`retval`)表示系統調用sys_read()返回值:即成功讀取的字節數。

# 7. read()調用的時間

```
# bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; } kretprobe:vfs_read /@start[tid]/ { @ns[comm] = hist(nsecs - @start[tid]); delete(@start[tid]); }'
Attaching 2 probes...

[...]
@ns[snmp-pass]:
[0, 1]                 0 |                                                    |
[2, 4)                 0 |                                                    |
[4, 8)                 0 |                                                    |
[8, 16)                0 |                                                    |
[16, 32)               0 |                                                    |
[32, 64)               0 |                                                    |
[64, 128)              0 |                                                    |
[128, 256)             0 |                                                    |
[256, 512)            27 |@@@@@@@@@                                           |
[512, 1k)            125 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@       |
[1k, 2k)              22 |@@@@@@@                                             |
[2k, 4k)               1 |                                                    |
[4k, 8k)              10 |@@@                                                 |
[8k, 16k)              1 |                                                    |
[16k, 32k)             3 |@                                                   |
[32k, 64k)           144 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[64k, 128k)            7 |@@                                                  |
[128k, 256k)          28 |@@@@@@@@@@                                          |
[256k, 512k)           2 |                                                    |
[512k, 1M)             3 |@                                                   |
[1M, 2M)               1 |                                                    |
```

根據進程名，以直方圖的形式顯示read()調用花費的時間，時間單位為納秒。

- @start[tid]: 使用線程ID作為key。某一時刻，可能有許許多多的read調用正在進行，我們希望為每個調用記錄一個起始時間戳。這要如何做到呢？我們可以為每個read調用建立一個唯一的標識符，並用它作為key進行統計。由於內核線程一次只能執行一個系統調用，我們可以使用線程ID作為上述標識符。
- nsecs: 自系統啟動到現在的納秒數。這是一個高精度時間戳，可以用來對事件計時。
- /@start[tid]/: 該過濾條件檢查起始時間戳是否被記錄。程序可能在某次read調用中途被啟動，如果沒有這個過濾條件，這個調用的時間會被統計為now-zero，而不是now-start。
- delete(@start[tid]): 釋放變量。

# 8. 統計進程級別的事件

```
# bpftrace -e 'tracepoint:sched:sched* { @[probe] = count(); } interval:s:5 { exit(); }'
Attaching 25 probes...
@[tracepoint:sched:sched_wakeup_new]: 1
@[tracepoint:sched:sched_process_fork]: 1
@[tracepoint:sched:sched_process_exec]: 1
@[tracepoint:sched:sched_process_exit]: 1
@[tracepoint:sched:sched_process_free]: 2
@[tracepoint:sched:sched_process_wait]: 7
@[tracepoint:sched:sched_wake_idle_without_ipi]: 53
@[tracepoint:sched:sched_stat_runtime]: 212
@[tracepoint:sched:sched_wakeup]: 253
@[tracepoint:sched:sched_waking]: 253
@[tracepoint:sched:sched_switch]: 510
```

這裡統計5秒內進程級的事件並打印。

- sched: `sched`探針可以探測調度器的高級事件和進程事件如fork, exec和上下文切換。
- probe: 探針的完整名稱。
- interval:s:5: 這是一個每5秒在每個CPU上觸發一次的探針，它用來創建腳本級別的間隔或超時時間。
- exit(): 退出bpftrace。

# 9. 分析內核實時函數棧

```
# bpftrace -e 'profile:hz:99 { @[kstack] = count(); }'
Attaching 1 probe...
^C

[...]
@[
filemap_map_pages+181
__handle_mm_fault+2905
handle_mm_fault+250
__do_page_fault+599
async_page_fault+69
]: 12
[...]
@[
cpuidle_enter_state+164
do_idle+390
cpu_startup_entry+111
start_secondary+423
secondary_startup_64+165
]: 22122
```

以99赫茲的頻率分析內核調用棧並打印次數統計。

- profile:hz:99: 這裡所有cpu都以99赫茲的頻率採樣分析內核棧。為什麼是99而不是100或者1000？我們想要抓取足夠詳細的內核執行時內核棧信息，但是頻率太大影響性能。100赫茲足夠了，但是我們不想用正好100赫茲，這樣採樣頻率可能與其他定時事件步調一致，所以99赫茲是一個理想的選擇。
- kstack: 返回內核調用棧。這裡作為map的關鍵字，可以跟蹤次數。這些輸出信息可以使用火焰圖可視化。此外`ustack`用來分析用戶級堆棧。

# 10. 調度器跟蹤

```
# bpftrace -e 'tracepoint:sched:sched_switch { @[kstack] = count(); }'
^C
[...]

@[
__schedule+697
__schedule+697
schedule+50
schedule_timeout+365
xfsaild+274
kthread+248
ret_from_fork+53
]: 73
@[
__schedule+697
__schedule+697
schedule_idle+40
do_idle+356
cpu_startup_entry+111
start_secondary+423
secondary_startup_64+165
]: 305
```

這裡統計進程上下文切換次數。以上輸出被截斷，只輸出了最後兩個結果。

- sched: 跟蹤調度類別的調度器事件:sched_switch, sched_wakeup, sched_migrate_task等。
- sched_switch: 當線程釋放cpu資源，當前不運行時觸發。這裡可能的阻塞事件:如等待I/O，定時器，分頁/交換，鎖等。
- kstack: 內核堆棧跟蹤，打印調用棧。
- sched_switch在線程切換的時候觸發，打印的調用棧是被切換出cpu的那個線程。像你使用其他探針一樣，注意這裡的上下文，例如comm, pid, kstack等等，並不一定反映了探針的目標的狀態。

# 11. 塊級I/O跟蹤

```
# bpftrace -e 'tracepoint:block:block_rq_issue { @ = hist(args.bytes); }'
Attaching 1 probe...
^C

@:
[0, 1]                 1 |@@                                                  |
[2, 4)                 0 |                                                    |
[4, 8)                 0 |                                                    |
[8, 16)                0 |                                                    |
[16, 32)               0 |                                                    |
[32, 64)               0 |                                                    |
[64, 128)              0 |                                                    |
[128, 256)             0 |                                                    |
[256, 512)             0 |                                                    |
[512, 1K)              0 |                                                    |
[1K, 2K)               0 |                                                    |
[2K, 4K)               0 |                                                    |
[4K, 8K)              24 |@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@|
[8K, 16K)              2 |@@@@                                                |
[16K, 32K)             6 |@@@@@@@@@@@@@                                       |
[32K, 64K)             5 |@@@@@@@@@@                                          |
[64K, 128K)            0 |                                                    |
[128K, 256K)           1 |@@                                                  |

```

以上是塊I/O請求字節數的直方圖。

- tracepoint:block: 塊類別的跟蹤點跟蹤塊級I/O事件。
- block_rq_issue: 當I/O提交到塊設備時觸發。
- args.bytes: 跟蹤點block_rq_issue的參數成員bytes，表示提交I/O請求的字節數。

該探針的上下文是非常重要的: 它在I/O請求被提交給塊設備時觸發。這通常發生在進程上下文，此時通過內核的comm可以得到進程名；也可能發生在內核上下文，(如readahead)，此時不能顯示預期的進程號和進程名信息。

# 12. 內核結構跟蹤

```
# cat path.bt
#ifndef BPFTRACE_HAVE_BTF
#include <linux/path.h>
#include <linux/dcache.h>
#endif

kprobe:vfs_open
{
	printf("open path: %s\n", str(((struct path *)arg0)->dentry->d_name.name));
}

# bpftrace path.bt
Attaching 1 probe...
open path: dev
open path: if_inet6
open path: retrans_time_ms
[...]
```


這裡使用內核動態跟蹤技術跟蹤vfs_read()函數，該函數的(struct path *)作為第一個參數。

- kprobe: 如前面所述，這是內核動態跟蹤kprobe探針類型，跟蹤內核函數的調用(kretprobe探針類型跟蹤內核函數返回值)。
- `arg0` 是一個內建變量，表示探針的第一個參數，其含義由探針類型決定。對於`kprobe`類型探針，它表示函數的第一個參數。其它參數使用arg1,...,argN訪問。
- `((struct path *)arg0)->dentry->d_name.name`: 這裡`arg0`作為`struct path *`並引用dentry。
- #include: 在沒有BTF (BPF Type Format) 的情況下,包含必要的path和dentry類型聲明的頭文件。

bpftrace對內核結構跟蹤的支持和bcc是一樣的，允許使用內核頭文件。這意味著大多數結構是可用的，但是並不是所有的，有時需要手動增加某些結構的聲明。例如這個例子，見[dcsnoop tool](https://github.com/iovisor/bpftrace/blob/master/docs/../tools/dcsnoop.bt)，包含struct nameidata的聲明。倘若內核有提供BTF數據，則所有結構都可用。

現在，你已經理解了bpftrace的大部分功能，你可以開始使用和編寫強大的一行命令。查閱[參考手冊](https://github.com/iovisor/bpftrace/blob/master/docs/reference_guide.md)更多的功能。

> 原文地址：https://github.com/iovisor/bpftrace/blob/master/docs
