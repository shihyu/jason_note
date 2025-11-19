# bcc Python 開發者教程

本教程介紹使用 Python 接口開發 [bcc](https://github.com/iovisor/bcc) 工具和程序。分為兩個部分：可觀測性和網絡。代碼片段取自 bcc 的各個程序，請查閱其文件以瞭解許可證情況。

還請參閱 bcc 開發者的[參考指南](reference_guide.md)，以及針對工具的用戶的教程：[教程](tutorial.md)。還有適用於 bcc 的 lua 接口。

## 可觀測性

這個可觀測性教程包含17個課程和46個要學習的枚舉事項。

### 第1課. 你好，世界

首先運行 [examples/hello_world.py](https://github.com/iovisor/bcc/tree/master/examples/hello_world.py)，同時在另一個會話中運行一些命令（例如，“ls”）。它應該會為新進程打印“Hello, World!”。如果沒有打印，請先修復bcc：請參閱 [INSTALL.md](https://github.com/iovisor/bcc/blob/master/INSTALL.md)。

```sh
# ./examples/hello_world.py
            bash-13364 [002] d... 24573433.052937: : Hello, World!
            bash-13364 [003] d... 24573436.642808: : Hello, World!
[...]
```

以下是 hello_world.py 的代碼示例：

```Python
from bcc import BPF
BPF(text='int kprobe__sys_clone(void *ctx) { bpf_trace_printk("Hello, World!\\n"); return 0; }').trace_print()
```

從中可以學到六件事情：

1. ```text='...'```：這定義了內聯的 BPF 程序。該程序是用 C 編寫的。

1. ```kprobe__sys_clone()```：這是通過 kprobes 動態跟蹤內核的一種快捷方式。如果 C 函數以 ```kprobe__``` 開頭，其餘部分將被視為要定位的內核函數名稱，本例中為 ```sys_clone()```。

1. ```void *ctx```：ctx 是參數，但由於我們在此處未使用它們，所以我們將其轉換為 ```void*``` 類型。
1. ```bpf_trace_printk()```: 用於將 printf() 打印到通用 trace_pipe (/sys/kernel/debug/tracing/trace_pipe) 的簡單內核工具。 這對於一些快速示例是可以的，但有一些限制：最多隻有 3 個參數，只能有一個 %s，並且 trace_pipe 是全局共享的，所以併發程序會有衝突的輸出。更好的接口是通過 BPF_PERF_OUTPUT() 實現的，稍後會介紹。

1. ```return 0;```: 必要的規範性代碼（如果想知道原因，請參見 [#139](https://github.com/iovisor/bcc/issues/139)）。

1. ```.trace_print()```: 一個讀取 trace_pipe 並打印輸出的 bcc 程序。

### 第二課 sys_sync()

編寫一個跟蹤 sys_sync() 內核函數的程序。運行時打印 "sys_sync() called"。在跟蹤時，在另一個會話中運行 ```sync``` 進行測試。hello_world.py 程序中包含了這一切所需的內容。

通過在程序剛啟動時打印 "Tracing sys_sync()... Ctrl-C to end." 來改進它。提示：它只是 Python 代碼。

### 第三課 hello_fields.py

該程序位於 [examples/tracing/hello_fields.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/hello_fields.py)。樣本輸出（在另一個會話中運行命令）：

```sh
# examples/tracing/hello_fields.py
時間(s)            進程名             進程 ID    消息
24585001.174885999 sshd             1432   你好，世界！
24585001.195710000 sshd             15780  你好，世界！
24585001.991976000 systemd-udevd    484    你好，世界！
24585002.276147000 bash             15787  你好，世界！
```

代碼：

```Python
from bcc import BPF

# 定義 BPF 程序
prog = """
int hello(void *ctx) {
    bpf_trace_printk("你好，世界！\\n");
    return 0;
}
"""

# 加載 BPF 程序
b = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("clone"), fn_name="hello")

# 頭部
print("%-18s %-16s %-6s %s" % ("時間(s)", "進程名", "進程 ID", "消息"))

# 格式化輸出
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    print("%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
```

這與hello_world.py類似，並通過sys_clone()再次跟蹤新進程，但是還有一些要學習的內容：

1. `prog =`：這次我們將C程序聲明為變量，然後引用它。如果您想根據命令行參數添加一些字符串替換，這將非常有用。

1. `hello()`：現在我們只是聲明瞭一個C函數，而不是使用`kprobe__`的快捷方式。我們稍後會引用它。在BPF程序中聲明的所有C函數都希望在探測器上執行，因此它們都需要以`pt_reg* ctx`作為第一個參數。如果您需要定義一些不會在探測器上執行的輔助函數，則需要將其定義為`static inline`，以便由編譯器內聯。有時您還需要為其添加`_always_inline`函數屬性。

1. `b.attach_kprobe(event=b.get_syscall_fnname("clone"), fn_name="hello")`：為內核clone系統調用函數創建一個kprobe，該函數將執行我們定義的hello()函數。您可以多次調用attach_kprobe()，並將您的C函數附加到多個內核函數上。

1. `b.trace_fields()`：從trace_pipe中返回一組固定的字段。與trace_print()類似，它對於編寫腳本很方便，但是對於實際的工具化需求，我們應該切換到BPF_PERF_OUTPUT()。

### Lesson 4. sync_timing.py

還記得以前系統管理員在緩慢的控制檯上輸入`sync`三次然後才重啟嗎？後來有人認為`sync;sync;sync`很聰明，將它們都寫在一行上運行，儘管這違背了最初的目的！然後，sync變成了同步操作，所以更加愚蠢。無論如何。

以下示例計算了`do_sync`函數被調用的速度，並且如果它在一秒鐘之內被調用，則輸出信息。`sync;sync;sync`將為第2個和第3個sync打印輸出：

```sh
# examples/tracing/sync_timing.py
追蹤快速sync... 按Ctrl-C結束"。
```

在時間0.00秒時：檢測到多個同步，上次發生在95毫秒前
在時間0.10秒時：檢測到多個同步，上次發生在96毫秒前

此程序是[examples/tracing/sync_timing.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/sync_timing.py)：

```Python
from __future__ import print_function
from bcc import BPF

# 加載BPF程序
b = BPF(text="""
#include <uapi/linux/ptrace.h>

BPF_HASH(last);

int do_trace(struct pt_regs *ctx) {
    u64 ts, *tsp, delta, key = 0;

    // 嘗試讀取存儲的時間戳
    tsp = last.lookup(&key);
    if (tsp != NULL) {
        delta = bpf_ktime_get_ns() - *tsp;
        if (delta < 1000000000) {
            // 時間小於1秒則輸出
            bpf_trace_printk("%d\\n", delta / 1000000);
        }
        last.delete(&key);
    }

    // 更新存儲的時間戳
    ts = bpf_ktime_get_ns();
    last.update(&key, &ts);
    return 0;
}
""")

b.attach_kprobe(event=b.get_syscall_fnname("sync"), fn_name="do_trace")
print("跟蹤快速同步... 按Ctrl-C結束")

# 格式化輸出
start = 0
while 1:
    (task, pid, cpu, flags, ts, ms) = b.trace_fields()
    if start == 0:
        start = ts
    ts = ts - start
    print("在時間%.2f秒處：檢測到多個同步，上次發生在%s毫秒前" % (ts, ms))
```

學習內容：

1. ```bpf_ktime_get_ns()```: 返回時間，單位為納秒。
1. ```BPF_HASH(last)```: 創建一個BPF映射對象，類型為哈希（關聯數組），名為"last"。我們沒有指定其他參數，因此默認的鍵和值類型為u64。
1. ```key = 0```: 我們只會在哈希中存儲一個鍵值對，其中鍵被硬編碼為零。
1. ```last.lookup(&key)```: 在哈希中查找鍵，並如果存在則返回其值的指針，否則返回NULL。我們將鍵作為指針的地址傳遞給該函數。
1. ```if (tsp != NULL) {```: 驗證器要求在將從映射查找得到的指針值解引用使用之前，必須先檢查其是否為null。1. ```last.delete(&key)```: 從哈希表中刪除key。目前需要這樣做是因為[`.update()`中存在一個內核錯誤](https://git.kernel.org/cgit/linux/kernel/git/davem/net.git/commit/?id=a6ed3ea65d9868fdf9eff84e6fe4f666b8d14b02)（在4.8.10中已經修復）。
1. ```last.update(&key, &ts)```: 將第二個參數的值與key關聯起來，覆蓋之前的任何值。這會記錄時間戳。

### 第5課. sync_count.py

修改sync_timing.py程序（前一課）以存儲所有內核同步系統調用（包括快速和慢速）的計數，並將其與輸出一起打印出來。可以通過向現有哈希表添加一個新的鍵索引來在BPF程序中記錄此計數。

### 第6課. disksnoop.py

瀏覽[examples/tracing/disksnoop.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/disksnoop.py)程序以瞭解新內容。以下是一些示例輸出：

```sh
# disksnoop.py
時間(s)            T  字節     延遲(ms)
16458043.436012    W  4096        3.13
16458043.437326    W  4096        4.44
16458044.126545    R  4096       42.82
16458044.129872    R  4096        3.24
[...]
```

以及代碼片段：

```Python
[...]
REQ_WRITE = 1  # 來自include/linux/blk_types.h

# 加載BPF程序
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blk-mq.h>

BPF_HASH(start, struct request *);

void trace_start(struct pt_regs *ctx, struct request *req) {
 // 使用請求指針存儲開始時間戳
 u64 ts = bpf_ktime_get_ns();

 start.update(&req, &ts);
}

void trace_completion(struct pt_regs *ctx, struct request *req) {
 u64 *tsp, delta;

 tsp = start.lookup(&req);
 if (tsp != 0) {
  delta = bpf_ktime_get_ns() - *tsp;
  bpf_trace_printk("%d %x %d\\n", req->__data_len,
      req->cmd_flags, delta / 1000);
  start.delete(&req);
 }
}
""")
if BPF.get_kprobe_functions(b'blk_start_request'):
        b.attach_kprobe(event="blk_start_request", fn_name="trace_start")
b.attach_kprobe(event="blk_mq_start_request", fn_name="trace_start")
if BPF.get_kprobe_functions(b'__blk_account_io_done'):
    b.attach_kprobe(event="__blk_account_io_done", fn_name="trace_completion") else: b.attach_kprobe(event="blk_account_io_done", fn_name="trace_completion") 
    [...]
```

學習內容：

1. ```REQ_WRITE```: 我們在Python程序中定義了一個內核常量，因為我們後面會在Python程序中使用它。如果我們在BPF程序中使用REQ_WRITE，它應該可以正常工作（無需定義），只需使用適當的```#includes```。
2. ```trace_start(struct pt_regs *ctx, struct request*req)```: 這個函數將在後面附加到kprobe上。kprobe函數的參數是```struct pt_regs *ctx```，用於寄存器和BPF上下文，然後是函數的實際參數。我們將把它附加到blk_start_request()上，其中第一個參數是```struct request*```。
3. ```start.update(&req, &ts)```: 我們使用請求結構的指針作為哈希中的鍵。這在跟蹤中很常見。結構體指針是非常好的鍵，因為它們是唯一的：兩個結構體不能具有相同的指針地址。（只需小心何時釋放和重用指針。）所以我們實際上是給描述磁盤I/O的請求結構體打上我們自己的時間戳，以便我們可以計時。存儲時間戳常用的兩個鍵是結構體指針和線程ID（用於記錄函數入口到返回的時間）。
4. ```req->__data_len```: 我們在解引用```struct request```的成員。請參閱內核源代碼中對其定義的部分以獲得有關哪些成員可用的信息。bcc實際上會將這些表達式重寫為一系列```bpf_probe_read_kernel()```調用。有時bcc無法處理複雜的解引用，此時您需要直接調用```bpf_probe_read_kernel()```。

這是一個非常有趣的程序，如果您能理解所有的代碼，您就會理解很多重要的基礎知識。我們仍然在使用```bpf_trace_printk()```的技巧，我們下一步要解決這個問題。

### Lesson 7. hello_perf_output.py

讓我們最終停止使用bpf_trace_printk()，並使用適當的BPF_PERF_OUTPUT()接口。這也意味著我們將停止獲取免費的trace_field()成員，如PID和時間戳，並且需要直接獲取它們。在另一個會話中運行命令時的示例輸出

```sh
# hello_perf_output.py
TIME(s)            COMM             PID    MESSAGE
0.000000000        bash             22986  你好，perf_output！
0.021080275        systemd-udevd    484    你好，perf_output！
0.021359520        systemd-udevd    484    你好，perf_output！
0.021590610        systemd-udevd    484    你好，perf_output！
[...]
```

代碼位於[examples/tracing/hello_perf_output.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/hello_perf_output.py)：

```Python
from bcc import BPF

// 定義BPF程序
prog = """
#include <linux/sched.h>

// 在C中定義輸出數據結構
struct data_t {
    u32 pid;
    u64 ts;
    char comm[TASK_COMM_LEN];
};
BPF_PERF_OUTPUT(events);

int hello(struct pt_regs *ctx) {
    struct data_t data = {};

    data.pid = bpf_get_current_pid_tgid();
    data.ts = bpf_ktime_get_ns();
    bpf_get_current_comm(&data.comm, sizeof(data.comm));

    events.perf_submit(ctx, &data, sizeof(data));

    return 0;
}
"""

// 加載BPF程序
b = BPF(text=prog)
b.attach_kprobe(event=b.get_syscall_fnname("clone"), fn_name="hello")

//標題
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "MESSAGE"))

//處理事件
start = 0
def print_event(cpu, data, size):
    global start
    event = b["events"].event(data)
    if start == 0:
            start = event.ts
    time_s = (float(event.ts - start)) / 1000000000
    print("%-18.9f %-16s %-6d %s" % (time_s, event.comm, event.pid, "你好，perf_output！"))

//循環並回調print_event
b["events"].open_perf_buffer(print_event)
while 1:
    b.perf_buffer_poll()
```

學習的內容：

1. ```struct data_t```: 這定義了一個C結構體，我們將用它來從內核傳遞數據到用戶空間。1. `BPF_PERF_OUTPUT(events)`: 這裡給我們的輸出通道命名為"events"。
1. `struct data_t data = {};`: 創建一個空的`data_t`結構體，我們將在之後填充它。
1. `bpf_get_current_pid_tgid()`: 返回低32位的進程ID（內核視圖中的PID，用戶空間中通常被表示為線程ID），以及高32位的線程組ID（用戶空間通常認為是PID）。通過直接將其設置為`u32`，我們丟棄了高32位。應該顯示PID還是TGID？對於多線程應用程序，TGID將是相同的，所以如果你想要區分它們，你需要PID。這也是對最終用戶期望的一個問題。
1. `bpf_get_current_comm()`: 將當前進程的名稱填充到第一個參數的地址中。
1. `events.perf_submit()`: 通過perf環形緩衝區將事件提交給用戶空間以供讀取。
1. `def print_event()`: 定義一個Python函數來處理從`events`流中讀取的事件。
1. `b["events"].event(data)`: 現在將事件作為一個Python對象獲取，該對象是根據C聲明自動生成的。
1. `b["events"].open_perf_buffer(print_event)`: 將Python的`print_event`函數與`events`流關聯起來。
1. `while 1: b.perf_buffer_poll()`: 阻塞等待事件。

### 第八課。 sync_perf_output.py

重寫之前的課程中的sync_timing.py，使用```BPF_PERF_OUTPUT```。

### 第九課。 bitehist.py

以下工具記錄了磁盤I/O大小的直方圖。樣本輸出：

```sh
# bitehist.py
跟蹤中... 按Ctrl-C結束。
^C
     kbytes          : count     distribution
       0 -> 1        : 3        |                                      |
       2 -> 3        : 0        |                                      |
       4 -> 7        : 211      |**********                            |
       8 -> 15       : 0        |                                      |
      16 -> 31       : 0        |                                      |".32 -> 63       : 0        |                                      |
      64 -> 127      : 1        |                                      |
     128 -> 255      : 800      |**************************************|
```

代碼在[examples/tracing/bitehist.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/bitehist.py):

```Python
from __future__ import print_function
from bcc import BPF
from time import sleep

# 加載BPF程序
b = BPF(text="""
#include <uapi/linux/ptrace.h>
#include <linux/blkdev.h>

BPF_HISTOGRAM(dist);

int kprobe__blk_account_io_done(struct pt_regs *ctx, struct request *req)
{
 dist.increment(bpf_log2l(req->__data_len / 1024));
 return 0;
}
""")

# 頭部
print("跟蹤中... 按Ctrl-C結束.")

# 跟蹤直到按下Ctrl-C
try:
 sleep(99999999)
except KeyboardInterrupt:
 print()

# 輸出
b["dist"].print_log2_hist("kbytes")
```

之前課程的總結：

- ```kprobe__```: 這個前綴意味著其餘部分將被視為一個將使用kprobe進行插樁的內核函數名。
- ```struct pt_regs *ctx, struct request*req```: kprobe的參數。```ctx``` 是寄存器和BPF上下文，```req``` 是被插樁函數 ```blk_account_io_done()``` 的第一個參數。
- ```req->__data_len```: 解引用該成員。

新知識：

1. ```BPF_HISTOGRAM(dist)```: 定義了一個名為 "dist" 的BPF映射對象，它是一個直方圖。
1. ```dist.increment()```: 默認情況下，將第一個參數提供的直方圖桶索引加1。也可以作為第二個參數傳遞自定義的增量。
1. ```bpf_log2l()```: 返回所提供值的對數值。這將成為我們直方圖的索引，這樣我們構建了一個以2為底的冪直方圖。
1. ```b["dist"].print_log2_hist("kbytes")```: 以2為底的冪形式打印 "dist" 直方圖，列標題為 "kbytes"。這樣只有桶計數從內核傳輸到用戶空間，因此效率高。

### Lesson 10. disklatency.py”。#### Lesson 11. vfsreadlat.py

這個例子分為獨立的Python和C文件。示例輸出：

```sh
# vfsreadlat.py 1
跟蹤中... 按Ctrl-C停止。
     微秒               : 數量     分佈
         0 -> 1          : 0        |                                        |
         2 -> 3          : 2        |***********                             |
         4 -> 7          : 7        |****************************************|
         8 -> 15         : 4        |**********************                  |

     微秒               : 數量     分佈
         0 -> 1          : 29       |****************************************|
         2 -> 3          : 28       |**************************************  |
         4 -> 7          : 4        |*****                                   |
         8 -> 15         : 8        |***********                             |
        16 -> 31         : 0        |                                        |
        32 -> 63         : 0        |                                        |
        64 -> 127        : 0        |                                        |
       128 -> 255        : 0        |                                        |
       256 -> 511        : 2        |**                                      |
       512 -> 1023       : 0        |                                        |
      1024 -> 2047       : 0        |                                        |
      2048 -> 4095       : 0        |                                        |
      4096 -> 8191       : 4        |*****                                   |
      8192 -> 16383      : 6        |********                                |
     16384 -> 32767      : 9        |************                            |```.32768 -> 65535      : 6        |********                                |
     65536 -> 131071     : 2        |**                                      |

     usecs               : count     distribution
         0 -> 1          : 11       |****************************************|
         2 -> 3          : 2        |*******                                 |
         4 -> 7          : 10       |************************************    |
         8 -> 15         : 8        |*****************************           |
        16 -> 31         : 1        |***                                     |
        32 -> 63         : 2        |*******                                 |
[...]
```

瀏覽 [examples/tracing/vfsreadlat.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/vfsreadlat.py) 和 [examples/tracing/vfsreadlat.c](https://github.com/iovisor/bcc/tree/master/examples/tracing/vfsreadlat.c) 中的代碼。

學習的內容:

1. `b = BPF(src_file = "vfsreadlat.c")`: 從單獨的源代碼文件中讀取 BPF C 程序。
2. `b.attach_kretprobe(event="vfs_read", fn_name="do_return")`: 將 BPF C 函數 `do_return()` 鏈接到內核函數 `vfs_read()` 的返回值上。這是一個 kretprobe：用於檢測函數返回值，而不是函數的入口。
3. `b["dist"].clear()`: 清除直方圖。

### Lesson 12. urandomread.py

當運行 `dd if=/dev/urandom of=/dev/null bs=8k count=5` 時進行跟蹤：

```sh
# urandomread.py
TIME(s)            COMM             PID    GOTBITS
24652832.956994001 smtp             24690  384
24652837.726500999 dd               24692  65536
24652837.727111001 dd               24692  65536
24652837.727703001 dd               24692  65536
24652837.728294998 dd               24692  65536
24652837.728888001 dd               24692  65536
```

哈！我意外地捕捉到了 smtp。代碼在 [examples/tracing/urandomread.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/urandomread.py) 中：

```Python
from __future__ import print_function".```python
from bcc import BPF

# 加載BPF程序
b = BPF(text="""
TRACEPOINT_PROBE(random, urandom_read) {
    // args is from /sys/kernel/debug/tracing/events/random/urandom_read/format
    bpf_trace_printk("%d\\n", args->got_bits);
    return 0;
}
""")

# header
print("%-18s %-16s %-6s %s" % ("TIME(s)", "COMM", "PID", "GOTBITS"))

# format output
while 1:
    try:
        (task, pid, cpu, flags, ts, msg) = b.trace_fields()
    except ValueError:
        continue
    print("%-18.9f %-16s %-6d %s" % (ts, task, pid, msg))
```

要學到的東西：

1. ```TRACEPOINT_PROBE(random, urandom_read)```: 對內核跟蹤點 ```random:urandom_read``` 進行注入。這些具有穩定的API，因此在可能的情況下建議使用它們來代替kprobe。您可以運行 ```perf list``` 來獲取跟蹤點列表。至少需要 Linux 版本 4.7 來將 BPF 程序附加到跟蹤點上。
2. ```args->got_bits```: ```args``` 是自動填充的跟蹤點參數結構。上面的註釋指出了可以查看這個結構的位置。例如：

```sh
# cat /sys/kernel/debug/tracing/events/random/urandom_read/format
name: urandom_read
ID: 972
format:
 field:unsigned short common_type; offset:0; size:2; signed:0;
 field:unsigned char common_flags; offset:2; size:1; signed:0;
 field:unsigned char common_preempt_count; offset:3; size:1; signed:0;
 field:int common_pid; offset:4; size:4; signed:1;

 field:int got_bits; offset:8; size:4; signed:1;
 field:int pool_left; offset:12; size:4; signed:1;
 field:int input_left; offset:16; size:4; signed:1;

print fmt: "got_bits %d nonblocking_pool_entropy_left %d input_entropy_left %d", REC->got_bits, REC->pool_left, REC->input_left
```

在這種情況下，我們正在打印 ```got_bits``` 成員。

### 第13課. disksnoop.py已修復

將上一課的 disksnoop.py 修改為使用 ```block:block_rq_issue``` 和 ```block:block_rq_complete``` 跟蹤點。

### 第14課. strlen_count.py.

這個程序對用戶級函數進行插樁，其中包括 ```strlen()``` 庫函數，並對其字符串參數進行頻率統計。例如輸出

```sh
# strlen_count.py
跟蹤 strlen()... 按 Ctrl-C 結束。
^C     數量 字符串
         1 " "
         1 "/bin/ls"
         1 "."
         1 "cpudist.py.1"
         1 ".bashrc"
         1 "ls --color=auto"
         1 "key_t"
[...]
        10 "a7:~# "
        10 "/root"
        12 "LC_ALL"
        12 "en_US.UTF-8"
        13 "en_US.UTF-8"
        20 "~"
        70 "#%^,~:-=?+/}"
       340 "\x01\x1b]0;root@bgregg-test: ~\x07\x02root@bgregg-test:~# "
```

這些是在跟蹤時由此庫函數處理的各種字符串以及它們的頻率計數。例如，"LC_ALL" 被調用了12次。

代碼在 [examples/tracing/strlen_count.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/strlen_count.py) 中：

```Python
from __future__ import print_function
from bcc import BPF
from time import sleep

# 載入 BPF 程序
b = BPF(text="""
#include <uapi/linux/ptrace.h>

struct key_t {
    char c[80];
};
BPF_HASH(counts, struct key_t);

int count(struct pt_regs *ctx) {
    if (!PT_REGS_PARM1(ctx))
        return 0;

    struct key_t key = {};
    u64 zero = 0, *val;

    bpf_probe_read_user(&key.c, sizeof(key.c), (void *)PT_REGS_PARM1(ctx));
    // 也可以使用 `counts.increment(key)`
    val = counts.lookup_or_try_init(&key, &zero);
    if (val) {
      (*val)++;
    }
    return 0;
};
""")
b.attach_uprobe(name="c", sym="strlen", fn_name="count")

# 頭部
print("跟蹤 strlen()... 按 Ctrl-C 結束。")

# 睡眠直到按下 Ctrl-C
try:
    sleep(99999999)
except KeyboardInterrupt:
    pass

# 打印輸出
print("%10s %s" % ("數量", "字符串"))
counts = b.get_table("counts")
for k, v in sorted(counts.items(), key=lambda counts: counts[1].value):
    print("%10d \"%s\"" % (v.value, k.c.encode('string-escape')))
```

要學習的內容：1. ```PT_REGS_PARM1(ctx)```: 這個參數會獲取傳遞給 ```strlen()``` 的第一個參數，也就是字符串。

1. ```b.attach_uprobe(name="c", sym="strlen", fn_name="count")```: 附加到庫 "c"（如果這是主程序，則使用其路徑名），對用戶級函數 ```strlen()``` 進行插裝，並在執行時調用我們的 C 函數 ```count()```。

### 第15課。nodejs_http_server.py

本程序會對用戶靜態定義的跟蹤 (USDT) 探測點進行插裝，這是內核跟蹤點的用戶級版本。示例輸出：

```sh
# nodejs_http_server.py 24728
TIME(s)            COMM             PID    ARGS
24653324.561322998 node             24728  path:/index.html
24653335.343401998 node             24728  path:/images/welcome.png
24653340.510164998 node             24728  path:/images/favicon.png
```

來自 [examples/tracing/nodejs_http_server.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/nodejs_http_server.py) 的相關代碼：

```Python
from __future__ import print_function
from bcc import BPF, USDT
import sys

if len(sys.argv) < 2:
    print("USAGE: nodejs_http_server PID")
    exit()
pid = sys.argv[1]
debug = 0

# load BPF program
bpf_text = """
#include <uapi/linux/ptrace.h>
int do_trace(struct pt_regs *ctx) {
    uint64_t addr;
    char path[128]={0};
    bpf_usdt_readarg(6, ctx, &addr);
    bpf_probe_read_user(&path, sizeof(path), (void *)addr);
    bpf_trace_printk("path:%s\\n", path);
    return 0;
};
"""

# enable USDT probe from given PID
u = USDT(pid=int(pid))
u.enable_probe(probe="http__server__request", fn_name="do_trace")
if debug:
    print(u.get_text())
    print(bpf_text)

# initialize BPF
b = BPF(text=bpf_text, usdt_contexts=[u])
```

學習內容：

1. ```bpf_usdt_readarg(6, ctx, &addr)```: 從 USDT 探測點中讀取參數 6 的地址到 ```addr```。
1. ```bpf_probe_read_user(&path, sizeof(path), (void *)addr)```: 現在字符串 ```addr``` 指向我們的 ```path``` 變量。
1. ```u = USDT(pid=int(pid))```: 為給定的 PID 初始化 USDT 跟蹤。1. ```u.enable_probe(probe="http__server__request", fn_name="do_trace")```: 將我們的 ```do_trace()``` BPF C 函數附加到 Node.js 的 ```http__server__request``` USDT 探針。
1. ```b = BPF(text=bpf_text, usdt_contexts=[u])```: 需要將我們的 USDT 對象 ```u``` 傳遞給 BPF 對象的創建。

### 第16課. task_switch.c

這是一個早期的教程，作為額外的課程包含其中。用它來複習和加深你已經學到的內容。

這是一個比 Hello World 更復雜的示例程序。該程序將在內核中每次任務切換時被調用，並在一個 BPF 映射中記錄新舊進程的 pid。

下面的 C 程序引入了一個新的概念：prev 參數。BCC 前端會特殊處理這個參數，從而使得對這個變量的訪問從由 kprobe 基礎設施傳遞的保存上下文中進行讀取。從位置1開始的參數的原型應該與被 kprobed 的內核函數的原型匹配。如果這樣做，程序就可以無縫訪問函數參數。

```c
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct key_t {
    u32 prev_pid;
    u32 curr_pid;
};

BPF_HASH(stats, struct key_t, u64, 1024);
int count_sched(struct pt_regs *ctx, struct task_struct *prev) {
    struct key_t key = {};
    u64 zero = 0, *val;

    key.curr_pid = bpf_get_current_pid_tgid();
    key.prev_pid = prev->pid;

    // could also use `stats.increment(key);`
    val = stats.lookup_or_try_init(&key, &zero);
    if (val) {
      (*val)++;
    }
    return 0;
}
```

用戶空間組件加載上面顯示的文件，並將其附加到 `finish_task_switch` 內核函數上。
BPF 對象的 `[]` 運算符允許訪問程序中的每個 BPF_HASH，允許對內核中的值進行通行訪問。可以像使用任何其他 python dict 對象一樣使用該對象：讀取、更新和刪除操作都是允許的。

```python
from bcc import BPF
from time import sleep

b = BPF(src_file="task_switch.c")".```markdown
```Chinese
b.attach_kprobe(event="finish_task_switch", fn_name="count_sched")

# 生成多個調度事件
for i in range(0, 100): sleep(0.01)

for k, v in b["stats"].items():
    print("task_switch[%5d->%5d]=%u" % (k.prev_pid, k.curr_pid, v.value))
```

這些程序可以在文件 [examples/tracing/task_switch.c](https://github.com/iovisor/bcc/tree/master/examples/tracing/task_switch.c) 和 [examples/tracing/task_switch.py](https://github.com/iovisor/bcc/tree/master/examples/tracing/task_switch.py) 中找到。

### 第17課. 進一步研究

要進行進一步研究，請參閱 Sasha Goldshtein 的 [linux-tracing-workshop](https://github.com/goldshtn/linux-tracing-workshop)，其中包含了額外的實驗。bcc/tools 中還有許多工具可供研究。

如果您希望為 bcc 貢獻工具，請閱讀 [CONTRIBUTING-SCRIPTS.md](https://github.com/iovisor/bcc/tree/master/CONTRIBUTING-SCRIPTS.md)。在主要的 [README.md](https://github.com/iovisor/bcc/tree/master/README.md) 的底部，您還會找到與我們聯繫的方法。祝您好運，祝您成功追蹤！

## 網絡

TODO
