# bcc 教程

本教程介紹如何使用[bcc](https://github.com/iovisor/bcc)工具快速解決性能、故障排除和網絡問題。如果你想開發新的bcc工具，請參考[tutorial_bcc_python_developer.md](tutorial_bcc_python_developer.md)教程。

本教程假設bcc已經安裝好，並且你可以成功運行像execsnoop這樣的工具。參見[INSTALL.md](https://github.com/iovisor/bcc/blob/master/INSTALL.md)。這些功能是在Linux 4.x系列中增加的。

## 可觀察性

一些快速的收穫。

### 0. 使用bcc之前

在使用bcc之前，你應該從Linux基礎知識開始。可以參考[Linux Performance Analysis in 60,000 Milliseconds](https://www.brendangregg.com/Articles/Netflix_Linux_Perf_Analysis_60s.pdf)文章，其中介紹了以下命令：

1. uptime
1. dmesg | tail
1. vmstat 1
1. mpstat -P ALL 1
1. pidstat 1
1. iostat -xz 1
1. free -m
1. sar -n DEV 1
1. sar -n TCP,ETCP 1
1. top

### 1. 性能分析

這是一個用於性能調查的通用檢查清單，首先有一個列表，然後詳細描述：

1. execsnoop
1. opensnoop
1. ext4slower（或btrfs\*，xfs\*，zfs\*）
1. biolatency
1. biosnoop
1. cachestat
1. tcpconnect
1. tcpaccept
1. tcpretrans
1. runqlat
1. profile

這些工具可能已經安裝在你的系統的/usr/share/bcc/tools目錄下，或者你可以從bcc github倉庫的/tools目錄中運行它們，這些工具使用.py擴展名。瀏覽50多個可用的工具，獲得更多的分析選項。

#### 1.1 execsnoop

```sh
# ./execsnoop
PCOMM            PID    RET ARGS
supervise        9660     0 ./run
supervise        9661     0 ./run
mkdir            9662     0 /bin/mkdir -p ./main
run              9663     0 ./run
[...]
```

execsnoop對於每個新進程打印一行輸出。檢查短生命週期的進程。這些進程可能會消耗CPU資源，但不會在大多數週期性運行的進程監控工具中顯示出來。它通過跟蹤`exec()`來工作，而不是`fork()`，所以它可以捕獲許多類型的新進程，但不是所有類型（例如，它不會看到啟動工作進程的應用程序，該應用程序沒有`exec()`其他任何內容）。

更多[例子](https://github.com/iovisor/bcc/tree/master/tools/execsnoop_example.txt)。

#### 1.2. opensnoop

```sh
# ./opensnoop
PID    COMM               FD ERR PATH
1565   redis-server        5   0 /proc/1565/stat
1565   redis-server        5   0 /proc/1565/stat
1565   redis-server        5   0 /proc/1565/stat
1603   snmpd               9   0 /proc/net/dev
1603   snmpd              11   0 /proc/net/if_inet6
1603   snmpd              -1   2 /sys/class/net/eth0/device/vendor
1603   snmpd              11   0 /proc/sys/net/ipv4/neigh/eth0/retrans_time_ms
1603   snmpd              11   0 /proc/sys/net/ipv6/neigh/eth0/retrans_time_ms
1603   snmpd              11   0 /proc/sys/net/ipv6/conf/eth0/forwarding
[...]
```

opensnoop每次open() syscall執行時打印一行輸出，包括詳細信息。

打開的文件可以告訴你很多關於應用程序的工作方式的信息：它們的數據文件、配置文件和日誌文件。有時候應用程序可能會表現不正常，當它們不斷嘗試讀取不存在的文件時則會表現得很差。opensnoop能夠快速幫助你查看。

更多[例子](https://github.com/iovisor/bcc/tree/master/tools/opensnoop_example.txt)。

#### 1.3. ext4slower（或btrfs\*，xfs\*，zfs\*）

```sh
# ./ext4slower
追蹤超過10毫秒的ext4操作
時間     進程           進程ID    T 字節數   偏移KB   延遲(ms) 文件名
06:35:01 cron           16464  R 1249    0          16.05 common-auth
06:35:01 cron           16463  R 1249    0          16.04 common-auth
06:35:01 cron           16465  R 1249    0          16.03 common-auth
06:35:01 cron           16465  R 4096    0          10.62 login.defs
06:35:01 cron           16464  R 4096    0          10.61 login.defs
```

ext4slower跟蹤ext4文件系統，並計時常見操作，然後只打印超過閾值的操作。這對於識別或證明一種性能問題非常方便：通過文件系統單獨顯示較慢的磁盤 I/O。磁盤以異步方式處理 I/O，很難將該層的延遲與應用程序所經歷的延遲關聯起來。在內核堆棧中更高層的追蹤，即在 VFS -> 文件系統接口中，會更接近應用程序遭受的延遲。使用此工具來判斷文件系統的延遲是否超過了給定的閾值。

在 bcc 中存在其他文件系統的類似工具：btrfsslower、xfsslower 和 zfsslower。還有一個名為 fileslower 的工具，它在 VFS 層工作並跟蹤所有內容（儘管會有更高的開銷）。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/ext4slower_example.txt)。

#### 1.4. biolatency

```sh
# ./biolatency
跟蹤塊設備的 I/O... 按 Ctrl-C 結束。
^C
     微秒             : 數量      分佈
       0 -> 1        : 0        |                                      |
       2 -> 3        : 0        |                                      |
       4 -> 7        : 0        |                                      |
       8 -> 15       : 0        |                                      |
      16 -> 31       : 0        |                                      |
      32 -> 63       : 0        |                                      |
      64 -> 127      : 1        |                                      |
     128 -> 255      : 12       |********                              |
     256 -> 511      : 15       |**********                            |
     512 -> 1023     : 43       |*******************************       |
    1024 -> 2047     : 52       |**************************************|
    2048 -> 4095     : 47       |**********************************    |
    4096 -> 8191     : 52       |**************************************|
    8192 -> 16383    : 36       |**************************            |
   16384 -> 32767    : 15       |**********                            |。32768 -> 65535    : 2        |*                                     |
   65536 -> 131071   : 2        |*                                     |
```

biolatency跟蹤磁盤I/O延遲（從設備執行到完成的時間），當工具結束（Ctrl-C，或給定的間隔）時，它會打印延遲的直方圖摘要。

這對於瞭解超出iostat等工具提供的平均時間的磁盤I/O延遲非常有用。在分佈的末尾將可見I/O延遲的異常值，以及多種模式的分佈。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/biolatency_example.txt)。

#### 1.5. biosnoop

```sh
# ./biosnoop
TIME(s)        COMM           PID    DISK    T  SECTOR    BYTES   LAT(ms)
0.000004001    supervise      1950   xvda1   W  13092560  4096       0.74
0.000178002    supervise      1950   xvda1   W  13092432  4096       0.61
0.001469001    supervise      1956   xvda1   W  13092440  4096       1.24
0.001588002    supervise      1956   xvda1   W  13115128  4096       1.09
1.022346001    supervise      1950   xvda1   W  13115272  4096       0.98
1.022568002    supervise      1950   xvda1   W  13188496  4096       0.93
[...]
```

biosnoop為每個磁盤I/O打印一行輸出，其中包括延遲（從設備執行到完成的時間）等詳細信息。

這讓您可以更詳細地研究磁盤I/O，並尋找按時間排序的模式（例如，讀取在寫入後排隊）。請注意，如果您的系統以高速率執行磁盤I/O，則輸出將冗長。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/biosnoop_example.txt)。

#### 1.6. cachestat

```sh
# ./cachestat
    HITS   MISSES  DIRTIES  READ_HIT% WRITE_HIT%   BUFFERS_MB  CACHED_MB
    1074       44       13      94.9%       2.9%            1        223
    2195      170        8      92.5%       6.8%            1        143
     182       53       56      53.6%       1.3%            1        143
   62480    40960    20480      40.6%      19.8%            1        223"。
格式：僅返回翻譯後的內容，不包括原始文本。```
7        2        5      22.2%      22.2%            1        223
     348        0        0     100.0%       0.0%            1        223
[...]
```

cachestat 每秒（或每個自定義時間間隔）打印一行摘要，顯示文件系統緩存的統計信息。

可以用它來識別低緩存命中率和高缺失率，這是性能調優的線索之一。

更多 [示例](https://github.com/iovisor/bcc/tree/master/tools/cachestat_example.txt)。

#### 1.7. tcpconnect

```sh
# ./tcpconnect
PID    COMM         IP SADDR            DADDR            DPORT
1479   telnet       4  127.0.0.1        127.0.0.1        23
1469   curl         4  10.201.219.236   54.245.105.25    80
1469   curl         4  10.201.219.236   54.67.101.145    80
1991   telnet       6  ::1              ::1              23
2015   ssh          6  fe80::2000:bff:fe82:3ac fe80::2000:bff:fe82:3ac 22
[...]
```

tcpconnect 每個活動的 TCP 連接（例如通過 connect()）打印一行輸出，包括源地址和目標地址的詳細信息。

尋找可能指向應用程序配置問題或入侵者的意外連接。

更多 [示例](https://github.com/iovisor/bcc/tree/master/tools/tcpconnect_example.txt)。

#### 1.8. tcpaccept

```sh
# ./tcpaccept
PID    COMM         IP RADDR            LADDR            LPORT
907    sshd         4  192.168.56.1     192.168.56.102   22
907    sshd         4  127.0.0.1        127.0.0.1        22
5389   perl         6  1234:ab12:2040:5020:2299:0:5:0 1234:ab12:2040:5020:2299:0:5:0 7001
[...]
```

tcpaccept 每個被動的 TCP 連接（例如通過 accept()）打印一行輸出，包括源地址和目標地址的詳細信息。

尋找可能指向應用程序配置問題或入侵者的意外連接。

更多 [示例](https://github.com/iovisor/bcc/tree/master/tools/tcpaccept_example.txt)。

#### 1.9. tcpretrans

```sh
# ./tcpretrans".
```時間 PID IP LADDR:LPORT T> RADDR:RPORT 狀態
01:55:05 0 4 10.153.223.157:22 R> 69.53.245.40:34619 已建立
01:55:05 0 4 10.153.223.157:22 R> 69.53.245.40:34619 已建立
01:55:17 0 4 10.153.223.157:22 R> 69.53.245.40:22957 已建立
[...]
```

tcpretrans為每個TCP重傳數據包打印一行輸出，其中包括源地址、目的地址以及TCP連接的內核狀態。

TCP重傳會導致延遲和吞吐量問題。對於已建立的重傳，可以查找與網絡有關的模式。對於SYN_SENT，可能指向目標內核CPU飽和和內核數據包丟失。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/tcpretrans_example.txt)。

#### 1.10. runqlat

```sh
# ./runqlat
跟蹤運行隊列延遲... 按Ctrl-C結束。
^C
     微秒數               : 計數     分佈
         0 -> 1          : 233      |***********                             |
         2 -> 3          : 742      |************************************    |
         4 -> 7          : 203      |**********                              |
         8 -> 15         : 173      |********                                |
        16 -> 31         : 24       |*                                       |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 30       |*                                       |
       128 -> 255        : 6        |                                        |
       256 -> 511        : 3        |                                        |
       512 -> 1023       : 5        |                                        |
      1024 -> 2047       : 27       |*                                       |
      2048 -> 4095       : 30       |*                                       |
      4096 -> 8191       : 20       |                                        |
      8192 -> 16383      : 29       |*                                       |".16384 -> 32767      : 809      |****************************************|
32768 -> 65535      : 64       |***                                     |
```

這可以幫助量化在CPU飽和期間等待獲取CPU的時間損失。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/runqlat_example.txt)。

#### 1.11. 分析

```sh
# ./profile
以每秒49次的頻率對所有線程進行採樣，包括用戶和內核棧...按Ctrl-C結束。
^C
    00007f31d76c3251 [未知]
    47a2c1e752bf47f7 [未知]
    -                sign-file (8877)
        1

    ffffffff813d0af8 __clear_user
    ffffffff813d5277 iov_iter_zero
    ffffffff814ec5f2 read_iter_zero
    ffffffff8120be9d __vfs_read
    ffffffff8120c385 vfs_read
    ffffffff8120d786 sys_read
    ffffffff817cc076 entry_SYSCALL_64_fastpath
    00007fc5652ad9b0 read
    -                dd (25036)
        4

    0000000000400542 func_a
    0000000000400598 main
    00007f12a133e830 __libc_start_main
    083e258d4c544155 [未知]
    -                func_ab (13549)
        5

[...]

    ffffffff8105eb66 native_safe_halt
    ffffffff8103659e default_idle
    ffffffff81036d1f arch_cpu_idle
    ffffffff810bba5a default_idle_call
    ffffffff810bbd07 cpu_startup_entry
    ffffffff8104df55 start_secondary
    -                swapper/1 (0)
        75
```

profile是一個CPU分析工具，它在定時間隔內採樣堆棧跟蹤，並打印唯一堆棧跟蹤的摘要及其出現次數。

使用此工具來了解消耗CPU資源的代碼路徑。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/profile_example.txt)。

### 2. 使用通用工具進行可觀察性

除了上述用於性能調整的工具外，下面是一個bcc通用工具的清單，首先是一個列表，然後詳細說明：

1. trace
1. argdist
1. funccount這些通用工具可能有助於解決您特定問題的可視化。

#### 2.1. 跟蹤

##### 示例 1

假設您想要跟蹤文件所有權更改。有三個系統調用，`chown`、`fchown`和`lchown`，用戶可以使用它們來更改文件所有權。相應的系統調用入口是`SyS_[f|l]chown`。可以使用以下命令打印系統調用參數和調用進程的用戶ID。您可以使用`id`命令查找特定用戶的UID。

```sh
$ trace.py \
  'p::SyS_chown "file = %s, to_uid = %d, to_gid = %d, from_uid = %d", arg1, arg2, arg3, $uid' \
  'p::SyS_fchown "fd = %d, to_uid = %d, to_gid = %d, from_uid = %d", arg1, arg2, arg3, $uid' \
  'p::SyS_lchown "file = %s, to_uid = %d, to_gid = %d, from_uid = %d", arg1, arg2, arg3, $uid'
PID    TID    COMM         FUNC             -
1269255 1269255 python3.6    SyS_lchown       file = /tmp/dotsync-usisgezu/tmp, to_uid = 128203, to_gid = 100, from_uid = 128203
1269441 1269441 zstd         SyS_chown        file = /tmp/dotsync-vic7ygj0/dotsync-package.zst, to_uid = 128203, to_gid = 100, from_uid = 128203
1269255 1269255 python3.6    SyS_lchown       file = /tmp/dotsync-a40zd7ev/tmp, to_uid = 128203, to_gid = 100, from_uid = 128203
1269442 1269442 zstd         SyS_chown        file = /tmp/dotsync-gzp413o_/dotsync-package.zst, to_uid = 128203, to_gid = 100, from_uid = 128203
1269255 1269255 python3.6    SyS_lchown       file = /tmp/dotsync-whx4fivm/tmp/.bash_profile, to_uid = 128203, to_gid = 100, from_uid = 128203
```

##### 示例 2

假設您想要統計基於bpf的性能監控工具中的非自願上下文切換（`nvcsw`），而您不知道正確的方法是什麼。`/proc/<pid>/status`已經告訴您進程的非自願上下文切換（`nonvoluntary_ctxt_switches`）的數量，並且您可以使用`trace.py`進行快速實驗以驗證您的方法。根據內核源代碼，`nvcsw`在文件`linux/kernel/sched/core.c`的`__schedule`函數中計數，並滿足以下條件：

```c
.!(!preempt && prev->state) // 即 preempt || !prev->state
```

`__schedule` 函數被標記為 `notrace` ，評估上述條件的最佳位置似乎在函數 `__schedule` 內部的 `sched/sched_switch` 跟蹤點中，並且在 `linux/include/trace/events/sched.h` 中定義。`trace.py` 已經將 `args` 設置為跟蹤點 `TP_STRUCT__entry` 的指針。函數 `__schedule` 中的上述條件可以表示為

```c
args->prev_state == TASK_STATE_MAX || args->prev_state == 0
```

可以使用以下命令來計算非自願上下文切換（每個進程或每個進程ID），並與 `/proc/<pid>/status` 或 `/proc/<pid>/task/<task_id>/status` 進行比較，以確保正確性，因為在典型情況下，非自願上下文切換並不常見。

```sh
$ trace.py -p 1134138 't:sched:sched_switch (args->prev_state == TASK_STATE_MAX || args->prev_state == 0)'
PID    TID    COMM         FUNC
1134138 1134140 contention_test sched_switch
1134138 1134142 contention_test sched_switch
...
$ trace.py -L 1134140 't:sched:sched_switch (args->prev_state == TASK_STATE_MAX || args->prev_state == 0)'
PID    TID    COMM         FUNC
1134138 1134140 contention_test sched_switch
1134138 1134140 contention_test sched_switch
...
```

##### 示例 3

此示例與問題 [1231](https://github.com/iovisor/bcc/issues/1231) 和 [1516](https://github.com/iovisor/bcc/issues/1516) 相關，其中在某些情況下，uprobes 完全無法工作。首先，你可以執行以下 `strace`

```sh
$ strace trace.py 'r:bash:readline "%s", retval'
...
perf_event_open(0x7ffd968212f0, -1, 0, -1, 0x8 /* PERF_FLAG_??? */) = -1 EIO (Input/output error)
...
```

`perf_event_open`系統調用返回`-EIO`。在`/kernel/trace`和`/kernel/events`目錄中查找與`EIO`相關的內核uprobe代碼，函數`uprobe_register`最可疑。讓我們找出是否調用了這個函數，如果調用了，返回值是什麼。在一個終端中使用以下命令打印出`uprobe_register`的返回值：

```sh
trace.py 'r::uprobe_register "ret = %d", retval'
```

在另一個終端中運行相同的bash uretprobe跟蹤示例，您應該得到：

```sh
$ trace.py 'r::uprobe_register "ret = %d", retval'
PID    TID    COMM         FUNC             -
1041401 1041401 python2.7    uprobe_register  ret = -5
```

錯誤代碼`-5`是EIO。這證實了函數`uprobe_register`中的以下代碼是最可疑的罪魁禍首。

```c
 if (!inode->i_mapping->a_ops->readpage && !shmem_mapping(inode->i_mapping))
        return -EIO;
```

`shmem_mapping`函數定義如下：

```c
bool shmem_mapping(struct address_space *mapping)
{
        return mapping->a_ops == &shmem_aops;
}
```

為了確認這個理論，使用以下命令找出`inode->i_mapping->a_ops`的值：

```sh
$ trace.py -I 'linux/fs.h' 'p::uprobe_register(struct inode *inode) "a_ops = %llx", inode->i_mapping->a_ops'
PID    TID    COMM         FUNC             -
814288 814288 python2.7    uprobe_register  a_ops = ffffffff81a2adc0
^C$ grep ffffffff81a2adc0 /proc/kallsyms
ffffffff81a2adc0 R empty_aops
```

內核符號`empty_aops`沒有定義`readpage`，因此上述可疑條件為真。進一步檢查內核源代碼顯示，`overlayfs`沒有提供自己的`a_ops`，而其他一些文件系統（例如ext4）定義了自己的`a_ops`（例如`ext4_da_aops`），並且`ext4_da_aops`定義了`readpage`。因此，uprobe對於ext4正常工作，但在overlayfs上不正常工作。

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/trace_example.txt)。

#### 2.2. argdist"。更多[示例](https://github.com/iovisor/bcc/tree/master/tools/argdist_example.txt)

#### 2.3. funccount

更多[示例](https://github.com/iovisor/bcc/tree/master/tools/funccount_example.txt).

## 網絡

To do.
