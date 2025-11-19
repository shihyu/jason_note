# Linux Kernel 除錯與追蹤技術完整指南

## 目錄
- [傳統除錯方法](#傳統除錯方法)
- [現代追蹤技術](#現代追蹤技術)
- [eBPF - 革命性技術](#ebpf---革命性技術)
- [動態追蹤工具](#動態追蹤工具)
- [靜態追蹤點](#靜態追蹤點)
- [Kernel 崩潰分析](#kernel-崩潰分析)
- [即時除錯技術](#即時除錯技術)
- [新興技術與工具](#新興技術與工具)

---

## 傳統除錯方法

### printk
最基本但仍然有效的除錯方式

```c
// kernel module 中使用
printk(KERN_INFO "Debug message: value=%d\n", value);
printk(KERN_ERR "Error occurred at %s:%d\n", __FILE__, __LINE__);

// 不同的日誌級別
KERN_EMERG   // 系統無法使用
KERN_ALERT   // 必須立即採取行動
KERN_CRIT    // 臨界條件
KERN_ERR     // 錯誤條件
KERN_WARNING // 警告條件
KERN_NOTICE  // 正常但重要
KERN_INFO    // 資訊
KERN_DEBUG   // 除錯訊息
```

檢視訊息：
```bash
dmesg | tail -f
journalctl -k -f  # systemd 系統
```

### Dynamic Debug (dyndbg)
動態開關除錯訊息

```c
// 在 kernel code 中
pr_debug("Dynamic debug message\n");
dev_dbg(dev, "Device debug message\n");
```

控制：
```bash
# 開啟特定檔案的除錯
echo 'file drivers/usb/core/hub.c +p' > /sys/kernel/debug/dynamic_debug/control

# 開啟特定函數
echo 'func usb_submit_urb +p' > /sys/kernel/debug/dynamic_debug/control

# 開啟特定模組
echo 'module usbcore +p' > /sys/kernel/debug/dynamic_debug/control
```

### KGDB
Kernel 層級的 GDB 除錯

```bash
# 設定 kernel 參數
kgdboc=ttyS0,115200 kgdbwait

# 在另一臺機器上
gdb vmlinux
(gdb) target remote /dev/ttyS0
(gdb) break sys_open
(gdb) continue
```

---

## 現代追蹤技術

### Ftrace
Linux 內建的追蹤框架

```bash
# 掛載 debugfs
mount -t debugfs none /sys/kernel/debug

# 基本使用
cd /sys/kernel/debug/tracing

# 查看可用的 tracer
cat available_tracers

# 設定 function tracer
echo function > current_tracer
echo 1 > tracing_on
cat trace

# 追蹤特定函數
echo do_sys_open > set_ftrace_filter
echo function_graph > current_tracer

# 追蹤函數調用圖
echo function_graph > current_tracer
echo 1 > options/funcgraph-proc
echo 1 > options/funcgraph-duration
```

進階功能：
```bash
# 設定追蹤 buffer 大小
echo 8192 > buffer_size_kb

# 只追蹤特定 CPU
echo 2 > tracing_cpumask

# 追蹤事件
echo 1 > events/sched/sched_switch/enable
echo 1 > events/irq/enable

# 使用 trace marker
echo "Custom marker" > trace_marker
```

### Perf Events
強大的效能分析框架

```bash
# 系統整體分析
perf top
perf stat -a sleep 10

# Kernel 函數分析
perf record -ag
perf report

# 追蹤特定事件
perf record -e sched:sched_switch -a
perf script

# 產生火焰圖
perf record -F 99 -ag -- sleep 60
perf script | flamegraph.pl > kernel.svg

# 追蹤 kernel 函數
perf probe --add='do_sys_open filename:string'
perf record -e probe:do_sys_open -aR
```

---

## eBPF - 革命性技術

### 基礎概念
eBPF (extended Berkeley Packet Filter) 是 Linux kernel 的革命性技術

```python
# 使用 BCC (BPF Compiler Collection)
from bcc import BPF

prog = """
#include <linux/sched.h>

int trace_sys_open(struct pt_regs *ctx) {
    char comm[TASK_COMM_LEN];
    bpf_get_current_comm(&comm, sizeof(comm));
    bpf_trace_printk("Process %s opened a file\\n", comm);
    return 0;
}
"""

b = BPF(text=prog)
b.attach_kprobe(event="do_sys_open", fn_name="trace_sys_open")
b.trace_print()
```

### bpftrace
高階 eBPF 追蹤語言

```bash
# 一行命令追蹤
bpftrace -e 'kprobe:do_sys_open { printf("%s opened a file\n", comm); }'

# 追蹤系統調用延遲
bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @start[tid] = nsecs; }
             tracepoint:raw_syscalls:sys_exit /@start[tid]/ {
               @ns[comm] = hist(nsecs - @start[tid]);
               delete(@start[tid]);
             }'

# 追蹤 kernel 函數執行時間
bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; }
             kretprobe:vfs_read /@start[tid]/ {
               @ns = hist(nsecs - @start[tid]);
               delete(@start[tid]);
             }'
```

複雜腳本範例：
```bash
#!/usr/bin/env bpftrace

BEGIN {
    printf("Tracing kernel mutex locks... Hit Ctrl-C to end.\n");
}

kprobe:mutex_lock {
    @lock_start[tid] = nsecs;
    @lock_stack[tid] = kstack;
}

kretprobe:mutex_lock /@lock_start[tid]/ {
    $duration = nsecs - @lock_start[tid];
    @lock_time = hist($duration);
    if ($duration > 1000000) {  // > 1ms
        printf("Slow mutex: %d us\n", $duration / 1000);
        printf("%s", @lock_stack[tid]);
    }
    delete(@lock_start[tid]);
    delete(@lock_stack[tid]);
}
```

### libbpf
原生 BPF 程式開發

```c
// kernel space program (kern.c)
#include <linux/bpf.h>
#include <bpf/bpf_helpers.h>

struct {
    __uint(type, BPF_MAP_TYPE_HASH);
    __uint(max_entries, 1024);
    __type(key, u32);
    __type(value, u64);
} counts SEC(".maps");

SEC("kprobe/do_sys_open")
int trace_open(struct pt_regs *ctx) {
    u32 pid = bpf_get_current_pid_tgid() >> 32;
    u64 *count;
    
    count = bpf_map_lookup_elem(&counts, &pid);
    if (count) {
        (*count)++;
    } else {
        u64 init_val = 1;
        bpf_map_update_elem(&counts, &pid, &init_val, BPF_ANY);
    }
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
```

---

## 動態追蹤工具

### SystemTap
強大的動態追蹤系統

```bash
# 安裝
sudo apt-get install systemtap systemtap-runtime

# 簡單範例
stap -e 'probe kernel.function("do_sys_open") {
    printf("%s opened %s\n", execname(), kernel_string($filename))
}'

# 複雜腳本
cat > trace_io.stp << 'EOF'
global io_count

probe vfs.read {
    io_count[execname()] <<< bytes_to_read
}

probe timer.s(5) {
    foreach (name in io_count) {
        printf("%s: %d reads, avg %d bytes\n", 
               name, @count(io_count[name]), @avg(io_count[name]))
    }
    delete io_count
}
EOF

sudo stap trace_io.stp
```

### kprobes / kretprobes
動態 kernel 探測點

```c
// kernel module 範例
#include <linux/kprobes.h>

static struct kprobe kp = {
    .symbol_name = "do_sys_open",
};

static int handler_pre(struct kprobe *p, struct pt_regs *regs) {
    printk(KERN_INFO "do_sys_open called\n");
    return 0;
}

static int __init kprobe_init(void) {
    kp.pre_handler = handler_pre;
    register_kprobe(&kp);
    return 0;
}
```

---

## 靜態追蹤點

### Tracepoints
預定義的追蹤點

```bash
# 列出所有 tracepoints
ls /sys/kernel/debug/tracing/events/

# 啟用特定 tracepoint
echo 1 > /sys/kernel/debug/tracing/events/sched/sched_switch/enable

# 查看輸出
cat /sys/kernel/debug/tracing/trace
```

在 kernel module 中使用：
```c
#include <trace/events/sched.h>

static void my_sched_switch_probe(void *data, bool preempt,
                                  struct task_struct *prev,
                                  struct task_struct *next) {
    printk("Switch from %s to %s\n", prev->comm, next->comm);
}

// 註冊
register_trace_sched_switch(my_sched_switch_probe, NULL);
```

### USDT (User Statically-Defined Tracing)
用戶空間靜態追蹤點

```c
#include <sys/sdt.h>

void process_request() {
    DTRACE_PROBE(myapp, request_start);
    // 處理邏輯
    DTRACE_PROBE1(myapp, request_end, latency);
}
```

---

## Kernel 崩潰分析

### kdump/crash
捕獲和分析 kernel crash dump

```bash
# 設定 kdump
sudo apt-get install kdump-tools crash

# 設定 crashkernel
# 在 /etc/default/grub 加入
GRUB_CMDLINE_LINUX_DEFAULT="crashkernel=384M-2G:128M,2G-:256M"

# 分析 crash dump
crash /usr/lib/debug/boot/vmlinux-$(uname -r) /var/crash/*/dump.*

crash> bt           # backtrace
crash> ps           # process list
crash> log          # kernel log
crash> dis -l function_name  # disassemble
```

### KASAN (Kernel Address Sanitizer)
記憶體錯誤檢測

```bash
# Kernel 編譯選項
CONFIG_KASAN=y
CONFIG_KASAN_INLINE=y
CONFIG_TEST_KASAN=m

# 使用
insmod test_kasan.ko
```

### KTSAN (Kernel Thread Sanitizer)
Race condition 檢測

```bash
CONFIG_KTSAN=y
```

---

## 即時除錯技術

### Live Patching (kpatch/kGraft)
無需重啟的 kernel 修補

```bash
# 使用 kpatch
kpatch-build --sourcedir=/usr/src/linux --config=/boot/config-$(uname -r) patch.diff
kpatch load kpatch-module.ko

# 檢查載入的 patches
kpatch list
```

### drgn
可程式化的 kernel 除錯器

```python
# 連接到執行中的 kernel
from drgn import Program
prog = Program()
prog.set_kernel()

# 檢查 kernel 資料結構
for task in for_each_task(prog):
    print(task.comm.string_(), task.pid.value_())

# 檢查特定結構
init_task = prog['init_task']
print(f"Init task state: {init_task.state.value_()}")
```

---

## 新興技術與工具

### BTF (BPF Type Format)
提供 kernel 資料結構資訊

```bash
# 檢查 BTF 支援
ls /sys/kernel/btf/vmlinux

# 使用 bpftool 檢查
bpftool btf dump file /sys/kernel/btf/vmlinux format c
```

### CO-RE (Compile Once - Run Everywhere)
可攜式 BPF 程式

```c
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_core_read.h>

SEC("kprobe/do_sys_open")
int trace_open(struct pt_regs *ctx) {
    struct task_struct *task = (void *)bpf_get_current_task();
    char comm[16];
    bpf_core_read_str(&comm, sizeof(comm), &task->comm);
    bpf_printk("Process %s opened file\n", comm);
    return 0;
}
```

### Retsnoop
失敗路徑分析工具

```bash
# 追蹤錯誤返回
sudo retsnoop -e 'tcp_*' -a ':kernel/net/ipv4/*'

# 追蹤特定錯誤碼
sudo retsnoop -e '*mount*' -c 'ret == -ENOENT'
```

### bpftool
BPF 程式管理工具

```bash
# 列出載入的 BPF 程式
bpftool prog list

# 顯示 BPF map
bpftool map list
bpftool map dump id 1

# 追蹤 BPF 程式執行
bpftool prog trace log
```

---

## 實戰範例

### 追蹤系統調用延遲
```bash
#!/usr/bin/env bpftrace

tracepoint:raw_syscalls:sys_enter {
    @start[tid] = nsecs;
    @syscall[tid] = args->id;
}

tracepoint:raw_syscalls:sys_exit /@start[tid]/ {
    $duration = nsecs - @start[tid];
    @latency[@syscall[tid]] = hist($duration);
    if ($duration > 10000000) {  // > 10ms
        printf("Slow syscall %d: %d ms\n", @syscall[tid], $duration / 1000000);
    }
    delete(@start[tid]);
    delete(@syscall[tid]);
}

END {
    clear(@start);
    clear(@syscall);
}
```

### 記憶體分配追蹤
```python
from bcc import BPF

prog = """
#include <linux/mm.h>

BPF_HASH(allocs, u64, u64);

TRACEPOINT_PROBE(kmem, kmalloc) {
    u64 size = args->bytes_alloc;
    u64 *total = allocs.lookup(&size);
    if (total) {
        (*total)++;
    } else {
        u64 one = 1;
        allocs.update(&size, &one);
    }
    return 0;
}
"""

b = BPF(text=prog)
# 執行並顯示結果
```

### 檔案系統操作監控
```bash
# 使用 opensnoop (BCC 工具)
sudo opensnoop -p 1234  # 特定 PID
sudo opensnoop -n nginx # 特定程式名稱

# 自訂 bpftrace 腳本
bpftrace -e '
kprobe:vfs_open {
    @opens[comm] = count();
}
kprobe:vfs_read {
    @reads[comm] = count();
}
kprobe:vfs_write {
    @writes[comm] = count();
}
interval:s:5 {
    print(@opens);
    print(@reads);
    print(@writes);
    clear(@opens);
    clear(@reads);
    clear(@writes);
}'
```

---

## 最佳實踐建議

### 開發階段
1. 使用 `pr_debug()` 和 dynamic debug
2. 編譯時開啟 `CONFIG_DEBUG_*` 選項
3. 使用 KASAN 檢測記憶體問題

### 測試階段
1. SystemTap 或 bpftrace 進行動態分析
2. Ftrace 追蹤函數調用
3. perf 進行效能分析

### 生產環境
1. eBPF 工具（低開銷）
2. 有限的 tracepoints
3. kdump 準備 crash 分析

### 問題診斷流程
1. **效能問題**: perf → flamegraph → bpftrace
2. **記憶體問題**: KASAN → kmemleak → crash dump
3. **死鎖問題**: lockdep → ftrace → drgn
4. **系統崩潰**: kdump → crash → gdb

---

## 參考資源

- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/)
- [BPF and XDP Reference Guide](https://docs.cilium.io/en/stable/bpf/)
- [Brendan Gregg's BPF Tools](http://www.brendangregg.com/bpf-performance-tools-book.html)
- [bcc Tutorial](https://github.com/iovisor/bcc/blob/master/docs/tutorial.md)
- [Linux Tracing Technologies](https://www.kernel.org/doc/html/latest/trace/index.html)
- [eBPF.io](https://ebpf.io/)
- [LWN.net Kernel Articles](https://lwn.net/Kernel/)