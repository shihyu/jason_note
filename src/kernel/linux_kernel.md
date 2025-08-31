# Linux Kernel 深度解析

## 簡介

Linux Kernel 是整個 Linux 作業系統的核心，負責管理系統資源、硬體設備、進程調度等底層操作。它是由 Linus Torvalds 於 1991 年創建的開源項目，現已成為世界上最廣泛使用的作業系統核心之一。

### 核心架構層次

```
┌─────────────────────────────────────┐
│         使用者空間 (User Space)        │
├─────────────────────────────────────┤
│         系統呼叫介面 (System Call)      │
├─────────────────────────────────────┤
│    ┌──────────┬──────────┬──────┐   │
│    │  VFS     │  進程管理  │ IPC  │   │
│    ├──────────┼──────────┼──────┤   │
│    │  網路協議 │  記憶體管理 │ 檔案 │   │
│    ├──────────┴──────────┴──────┤   │
│    │        裝置驅動程式          │   │
│    └──────────────────────────────┘   │
├─────────────────────────────────────┤
│         硬體抽象層 (HAL)              │
└─────────────────────────────────────┘
```

## 核心子系統

### 1. 進程管理 (Process Management)
- **調度器 (Scheduler)**: CFS (Completely Fair Scheduler)
- **進程狀態**: Running, Waiting, Stopped, Zombie
- **上下文切換**: 保存和恢復 CPU 狀態
- **進程通訊**: Signal, Pipe, Socket, Shared Memory

### 2. 記憶體管理 (Memory Management)
- **虛擬記憶體**: 分頁機制、位址空間
- **記憶體分配器**: SLAB, SLUB, SLOB
- **頁面置換演算法**: LRU, Clock
- **記憶體映射**: mmap(), munmap()

### 3. 檔案系統 (File System)
- **VFS (Virtual File System)**: 統一的檔案系統介面
- **支援的檔案系統**: ext4, Btrfs, XFS, ZFS
- **塊設備層**: I/O 調度器 (CFQ, Deadline, NOOP)
- **頁緩存**: Page Cache 機制

### 4. 網路子系統 (Networking)
- **協議棧**: TCP/IP, UDP, ICMP
- **Netfilter**: 防火牆框架
- **Socket 層**: BSD Socket API
- **網路設備驅動**: 網卡驅動介面

### 5. 裝置驅動 (Device Drivers)
- **字符設備**: 按字節訪問 (如終端、串口)
- **塊設備**: 按塊訪問 (如硬碟、SSD)
- **網路設備**: 網路介面卡
- **Platform 設備**: 嵌入式系統設備

## 開發工具

### 編譯工具
```bash
# 安裝編譯工具鏈
sudo apt-get install build-essential libncurses-dev bison flex libssl-dev libelf-dev

# 配置核心
make menuconfig    # 圖形化配置
make defconfig     # 預設配置
make oldconfig     # 基於舊配置

# 編譯核心
make -j$(nproc)    # 多核心編譯
make modules       # 編譯模組
make modules_install  # 安裝模組
make install       # 安裝核心
```

### 調試工具

#### 1. **printk**
```c
// 核心日誌等級
#define KERN_EMERG   "<0>"  // 系統無法使用
#define KERN_ALERT   "<1>"  // 必須立即採取行動
#define KERN_CRIT    "<2>"  // 危急情況
#define KERN_ERR     "<3>"  // 錯誤情況
#define KERN_WARNING "<4>"  // 警告情況
#define KERN_NOTICE  "<5>"  // 正常但重要
#define KERN_INFO    "<6>"  // 資訊
#define KERN_DEBUG   "<7>"  // 調試資訊

printk(KERN_INFO "Module loaded\n");
```

#### 2. **KGDB**
```bash
# 在 kernel config 中啟用
CONFIG_KGDB=y
CONFIG_KGDB_SERIAL_CONSOLE=y

# 啟動參數
kgdboc=ttyS0,115200 kgdbwait
```

#### 3. **SystemTap**
```bash
# 安裝
sudo apt-get install systemtap systemtap-runtime

# 範例腳本
stap -e 'probe kernel.function("sys_open") { printf("open called\n") }'
```

#### 4. **ftrace**
```bash
# 啟用 function tracer
echo function > /sys/kernel/debug/tracing/current_tracer

# 查看追蹤結果
cat /sys/kernel/debug/tracing/trace
```

#### 5. **perf**
```bash
# 安裝
sudo apt-get install linux-tools-common linux-tools-generic

# CPU 分析
perf record -a -g ./program
perf report

# 查看系統調用
perf trace

# 統計效能計數器
perf stat ./program
```

### 分析工具

#### 1. **eBPF (Extended Berkeley Packet Filter)**
```python
# 使用 bcc 工具
from bcc import BPF

# BPF 程式
bpf_text = """
int trace_open(struct pt_regs *ctx) {
    bpf_trace_printk("open() called\\n");
    return 0;
}
"""

b = BPF(text=bpf_text)
b.attach_kprobe(event="sys_open", fn_name="trace_open")
```

#### 2. **bpftrace**
```bash
# 追蹤系統調用
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s %s\n", comm, str(args->filename)); }'

# 統計函數執行時間
sudo bpftrace -e 'kprobe:vfs_read { @start[tid] = nsecs; } kretprobe:vfs_read /@start[tid]/ { @ns = hist(nsecs - @start[tid]); delete(@start[tid]); }'
```

#### 3. **LTTng (Linux Trace Toolkit Next Generation)**
```bash
# 創建會話
lttng create my-session

# 啟用核心事件
lttng enable-event -k sched_switch

# 開始追蹤
lttng start

# 停止並查看
lttng stop
lttng view
```

## 核心模組開發

### 基本模組範例
```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>

static int __init hello_init(void)
{
    printk(KERN_INFO "Hello, Kernel!\n");
    return 0;
}

static void __exit hello_exit(void)
{
    printk(KERN_INFO "Goodbye, Kernel!\n");
}

module_init(hello_init);
module_exit(hello_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Your Name");
MODULE_DESCRIPTION("A simple kernel module");
MODULE_VERSION("1.0");
```

### Makefile
```makefile
obj-m += hello.o

all:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) modules

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(PWD) clean
```

### 模組操作
```bash
# 編譯模組
make

# 載入模組
sudo insmod hello.ko

# 查看模組
lsmod | grep hello

# 查看模組資訊
modinfo hello.ko

# 卸載模組
sudo rmmod hello

# 查看核心日誌
dmesg | tail
```

## 重要資料結構

### 1. task_struct (進程描述符)
```c
struct task_struct {
    volatile long state;        // 進程狀態
    void *stack;               // 核心棧
    unsigned int flags;        // 進程標誌
    int prio, static_prio;     // 優先級
    struct mm_struct *mm;      // 記憶體描述符
    struct files_struct *files; // 開啟的檔案
    pid_t pid;                 // 進程 ID
    pid_t tgid;                // 執行緒群組 ID
    // ... 更多欄位
};
```

### 2. file_operations (檔案操作)
```c
struct file_operations {
    struct module *owner;
    loff_t (*llseek) (struct file *, loff_t, int);
    ssize_t (*read) (struct file *, char __user *, size_t, loff_t *);
    ssize_t (*write) (struct file *, const char __user *, size_t, loff_t *);
    int (*open) (struct inode *, struct file *);
    int (*release) (struct inode *, struct file *);
    // ... 更多操作
};
```

## 學習資源

### 官方文件
- [Linux Kernel Documentation](https://www.kernel.org/doc/html/latest/)
- [Kernel Newbies](https://kernelnewbies.org/)
- [Linux Kernel Mailing List (LKML)](https://lkml.org/)

### 書籍推薦
1. **《Linux Kernel Development》** - Robert Love
2. **《Understanding the Linux Kernel》** - Daniel P. Bovet & Marco Cesati
3. **《Linux Device Drivers》** - Jonathan Corbet, Alessandro Rubini
4. **《Professional Linux Kernel Architecture》** - Wolfgang Mauerer
5. **《The Linux Programming Interface》** - Michael Kerrisk

### 線上課程
- [Linux Kernel Programming (Coursera)](https://www.coursera.org/learn/linux-kernel-programming)
- [Linux Kernel Internals (edX)](https://www.edx.org/course/linux-kernel)
- [Eudyptula Challenge](http://eudyptula-challenge.org/) - Kernel 開發挑戰

### 實用網站
- [LWN.net](https://lwn.net/) - Linux 週報
- [Phoronix](https://www.phoronix.com/) - Linux 硬體和效能新聞
- [Linux Inside](https://0xax.gitbooks.io/linux-insides/) - 深入理解 Linux 核心
- [The Linux Kernel Module Programming Guide](https://sysprog21.github.io/lkmpg/)

### 原始碼瀏覽
- [Elixir Cross Referencer](https://elixir.bootlin.com/linux/latest/source)
- [Linux Kernel GitHub Mirror](https://github.com/torvalds/linux)
- [Kernel.org Git](https://git.kernel.org/)

## 實戰專案

### 入門級
1. **Hello World 模組**: 基本的核心模組
2. **字符設備驅動**: 實現簡單的字符設備
3. **/proc 檔案系統**: 創建 /proc 條目
4. **sysfs 介面**: 實現 sysfs 屬性

### 進階級
1. **塊設備驅動**: RAM disk 實現
2. **網路驅動**: 虛擬網路設備
3. **檔案系統**: 簡單的檔案系統實現
4. **調度器修改**: 自定義調度策略

### 專家級
1. **即時核心修改**: RT-PREEMPT 補丁
2. **安全模組**: LSM (Linux Security Module)
3. **虛擬化**: KVM 模組開發
4. **效能優化**: 核心效能調優

## 常用命令速查

```bash
# 核心版本
uname -r

# 核心參數
sysctl -a                  # 查看所有參數
sysctl kernel.version      # 查看特定參數
echo 1 > /proc/sys/net/ipv4/ip_forward  # 修改參數

# 模組管理
lsmod                      # 列出載入的模組
modprobe module_name       # 載入模組及依賴
modprobe -r module_name    # 卸載模組
depmod                     # 生成模組依賴

# 核心日誌
dmesg                      # 查看核心環緩衝區
journalctl -k              # 查看核心日誌 (systemd)
cat /proc/kmsg             # 即時核心訊息

# 系統資訊
cat /proc/cpuinfo          # CPU 資訊
cat /proc/meminfo          # 記憶體資訊
cat /proc/interrupts       # 中斷資訊
cat /proc/modules          # 載入的模組
cat /proc/version          # 核心版本

# 效能監控
vmstat 1                   # 虛擬記憶體統計
iostat -x 1                # I/O 統計
mpstat -P ALL 1            # CPU 統計
sar -n DEV 1               # 網路統計
```

## 核心開發最佳實踐

### 1. 編碼規範
- 遵循 [Linux Kernel Coding Style](https://www.kernel.org/doc/html/latest/process/coding-style.html)
- 使用 checkpatch.pl 檢查程式碼
- 保持函數簡短，一個函數一個功能

### 2. 記憶體管理
- 正確使用 kmalloc/kfree
- 避免記憶體洩漏
- 使用適當的 GFP 標誌
- 注意原子上下文限制

### 3. 並發控制
- 正確使用鎖機制 (spinlock, mutex, semaphore)
- 避免死鎖
- 使用 RCU 進行讀優化
- 注意中斷上下文

### 4. 錯誤處理
- 檢查所有返回值
- 使用 goto 進行錯誤清理
- 提供有意義的錯誤訊息
- 正確釋放資源

### 5. 測試和調試
- 使用 KASAN 檢測記憶體錯誤
- 啟用 DEBUG 選項
- 進行壓力測試
- 使用 sparse 進行靜態分析

## 結語

Linux Kernel 是一個龐大而複雜的系統，掌握它需要時間和實踐。建議從簡單的模組開始，逐步深入到更複雜的子系統。記住，核心開發需要謹慎，因為錯誤可能導致系統崩潰。始終在虛擬機或測試環境中進行開發和測試。
