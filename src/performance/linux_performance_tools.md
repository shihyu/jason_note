# Linux Kernel 與 User Space 效能分析工具完整指南

## 主線內核內建工具（無需打補丁）

### 1. Ftrace
- **內建於內核**，功能強大的追蹤框架
- 支援函數追蹤、事件追蹤、圖形化追蹤
- 極低開銷，適合生產環境

**使用範例：**
```bash
# 啟用函數追蹤
echo function > /sys/kernel/debug/tracing/current_tracer
echo 1 > /sys/kernel/debug/tracing/tracing_on

# 查看追蹤結果
cat /sys/kernel/debug/tracing/trace
```

**特點：**
- 內核原生支援
- 開銷極低（< 1%）
- 支援多種追蹤器（function, function_graph, irqsoff, preemptoff 等）

---

### 2. perf (perf_events)
- Linux 官方效能分析工具
- CPU profiling、硬體計數器、事件追蹤
- 生成 Flame Graphs 的標準工具

**使用範例：**
```bash
# CPU profiling
perf record -F 99 -a -g -- sleep 30
perf report

# 查看系統調用
perf trace

# 統計事件
perf stat ./my_program

# 查看 CPU 快取未命中
perf stat -e cache-misses,cache-references ./my_program
```

**特點：**
- 支援硬體 PMU (Performance Monitoring Unit)
- 豐富的事件類型（硬體、軟體、tracepoint）
- 可生成火焰圖
- 主流發行版都內建

---

### 3. eBPF / BCC / bpftrace
- 功能最豐富的追蹤框架
- 可編程、安全、高效
- 支援內核和用戶空間追蹤

**使用範例：**
```bash
# 使用 bpftrace 追蹤系統調用延遲
bpftrace -e 'tracepoint:syscalls:sys_enter_read { @start[tid] = nsecs; }
             tracepoint:syscalls:sys_exit_read /@start[tid]/ { 
               @latency = hist(nsecs - @start[tid]); 
               delete(@start[tid]); 
             }'

# 使用 BCC 工具追蹤打開的文件
opensnoop-bpfcc

# 分析 I/O 延遲分佈
biolatency-bpfcc

# 追蹤 TCP 連線
tcpconnect-bpfcc
```

**特點：**
- 在內核中執行自定義程式
- 安全（通過驗證器檢查）
- 豐富的工具生態系統
- 支援即時聚合和過濾

---

### 4. LTTng (Linux Trace Toolkit Next Generation)
- 專注於低開銷的追蹤
- 支援 kernel 和 userspace 追蹤
- 適合實時系統和長時間追蹤

**使用範例：**
```bash
# 創建追蹤會話
lttng create my-session

# 啟用所有內核事件
lttng enable-event -k --all

# 啟用用戶空間事件
lttng enable-event -u --all

# 開始追蹤
lttng start

# 運行你的程式
./my_program

# 停止追蹤
lttng stop

# 查看結果
lttng view

# 銷毀會話
lttng destroy
```

**特點：**
- 極低開銷（接近零影響）
- 適合長時間生產環境追蹤
- 支援多種輸出格式
- 優秀的時間戳精度

---

## 專門化追蹤工具

### 5. SystemTap
- 類似 DTrace 的追蹤語言
- 需要編譯內核模組
- 功能強大但學習曲線較陡

**使用範例：**
```bash
# 追蹤 read 系統調用
stap -e 'probe syscall.read { 
    printf("%s(%d) read %d bytes\n", execname(), pid(), $count) 
}'

# 追蹤內核函數
stap -e 'probe kernel.function("vfs_read") { 
    printf("Reading file: %s\n", kernel_string($file->f_path->dentry->d_name->name)) 
}'
```

**特點：**
- 類似 DTrace 的腳本語言
- 功能極其強大
- 需要內核偵錯符號
- 安全性較 eBPF 低

---

### 6. kprobes / uprobes
- 動態探針機制
- eBPF、perf、SystemTap 的基礎技術
- 可在任意內核/用戶函數插入探針

**類型：**
- **kprobes**: 內核探針
- **uprobes**: 用戶空間探針
- **kretprobes / uretprobes**: 函數返回探針

**使用範例：**
```bash
# 使用 perf 設置 kprobe
perf probe --add 'do_sys_open filename:string'
perf record -e probe:do_sys_open -aR sleep 10
perf script

# 使用 uprobe 追蹤用戶程式
perf probe -x /bin/bash --add readline
perf record -e probe_bash:readline -a
```

---

### 7. trace-cmd
- Ftrace 的命令行前端工具
- 更易用的 ftrace 介面
- 簡化了 ftrace 的使用

**使用範例：**
```bash
# 記錄函數圖追蹤
trace-cmd record -p function_graph ls

# 顯示追蹤結果
trace-cmd report

# 追蹤特定函數
trace-cmd record -p function -l do_sys_open sleep 5

# 記錄事件
trace-cmd record -e sched_switch -e sched_wakeup
```

**特點：**
- 比直接使用 ftrace 更簡單
- 支援追蹤記錄和回放
- 可配合 kernelshark 視覺化

---

## 視覺化和分析工具

### 8. Flame Graphs (火焰圖)
- Brendan Gregg 開發的可視化工具
- 配合 perf、eBPF 使用
- 多種類型：CPU、Off-CPU、Memory

**生成方式：**
```bash
# CPU 火焰圖
perf record -F 99 -a -g -- sleep 30
perf script | ./stackcollapse-perf.pl | ./flamegraph.pl > cpu.svg

# Off-CPU 火焰圖（使用 eBPF）
offcputime-bpfcc -df 30 > out.stacks
./flamegraph.pl --color=io --title="Off-CPU Time" < out.stacks > offcpu.svg
```

**類型：**
- **CPU Flame Graphs**: 顯示 CPU 時間消耗
- **Off-CPU Flame Graphs**: 顯示阻塞時間
- **Memory Flame Graphs**: 顯示記憶體分配
- **Differential Flame Graphs**: 比較兩次追蹤的差異

---

### 9. Intel VTune / AMD uProf
- 廠商專屬的 PMU 工具
- 深度硬體分析
- 支援高級 CPU 性能計數器

**特點：**
- Intel VTune: Intel CPU 專用
- AMD uProf: AMD CPU 專用
- 提供 GUI 介面
- 深入的微架構分析

---

### 10. kernelshark
- Ftrace/trace-cmd 的 GUI 視覺化工具
- 時間線視圖，易於理解
- 支援事件過濾和搜索

**使用方式：**
```bash
# 記錄追蹤
trace-cmd record -e all

# 使用 kernelshark 視覺化
kernelshark trace.dat
```

**特點：**
- 圖形化時間線
- 支援多個 CPU 同時顯示
- 事件過濾和搜索功能

---

## 綜合性能分析工具集

### 11. perf-tools
- Brendan Gregg 開發的腳本集合
- 基於 ftrace 和 perf
- 超過 30 個實用工具

**常用工具：**
```bash
# 統計函數調用次數
funccount 'vfs_*'

# 追蹤文件系統同步操作
funccount 'ext4_sync_*'

# 追蹤進程執行
execsnoop

# 追蹤 I/O 操作
iosnoop

# 追蹤記憶體頁錯誤
funcgraph do_page_fault
```

**專案地址：** https://github.com/brendangregg/perf-tools

---

### 12. bcc-tools (eBPF 工具集)
- 超過 70+ 個現成的追蹤工具
- 基於 eBPF/BCC 框架
- 涵蓋網路、磁碟、CPU、記憶體等

**常用工具：**
```bash
# 追蹤打開的文件
opensnoop-bpfcc

# 分析 I/O 延遲分佈
biolatency-bpfcc

# 追蹤 TCP 連線
tcpconnect-bpfcc

# 追蹤 TCP 生命週期
tcplife-bpfcc

# CPU 採樣分析
profile-bpfcc -F 99 -a -g

# 追蹤 malloc/free
memleak-bpfcc

# 分析硬碟 I/O 模式
biotop-bpfcc

# 追蹤網路封包丟失
tcpdrop-bpfcc
```

**專案地址：** https://github.com/iovisor/bcc

---

## KUTrace
- 需要內核補丁
- 極低開銷（< 1%）
- 微秒級全系統時間線追蹤

**特點：**
- 專注於調度和內核-用戶態切換
- 完整的時間線視圖
- 適合分析系統級性能問題

---

## 工具選擇指南

| 使用場景 | 推薦工具 | 開銷 | 易用性 |
|---------|---------|------|--------|
| **快速 CPU profiling** | perf + Flame Graphs | 低 | 高 |
| **通用追蹤和監控** | eBPF/BCC | 極低 | 中 |
| **極低開銷追蹤** | LTTng, Ftrace | 極低 | 中 |
| **開發調試** | perf, trace-cmd | 低 | 高 |
| **生產環境** | eBPF, perf, LTTng | 極低 | 中-高 |
| **深度內核分析** | SystemTap, Ftrace | 低-中 | 低 |
| **微秒級全系統追蹤** | KUTrace | 極低 | 低 |
| **網路分析** | bcc-tools (tcplife, tcptop) | 極低 | 高 |
| **I/O 分析** | bcc-tools (biolatency, biotop) | 極低 | 高 |
| **記憶體分析** | perf, bcc-tools (memleak) | 低 | 中 |

---

## 現代最佳實踐組合

### 日常開發和監控
```
eBPF/BCC tools → 快速問題定位
perf + Flame Graphs → CPU 性能分析
trace-cmd/Ftrace → 詳細事件追蹤
```

### 生產環境
```
LTTng → 長期低開銷追蹤
eBPF → 即時監控和告警
perf → 週期性性能採樣
```

### 深度性能調優
```
perf → 硬體計數器分析
eBPF → 自定義追蹤邏輯
SystemTap → 複雜場景腳本
Intel VTune/AMD uProf → 微架構分析
```

---

## 快速上手建議

### 1. 初學者起步
```bash
# 安裝基本工具
sudo apt install linux-tools-common linux-tools-generic bpfcc-tools

# 簡單 CPU 分析
perf top

# 查看系統調用
perf trace -p $(pidof my_program)

# 使用現成的 BCC 工具
opensnoop-bpfcc
```

### 2. 進階使用
```bash
# CPU 火焰圖
perf record -F 99 -a -g -- sleep 30
perf script | stackcollapse-perf.pl | flamegraph.pl > flame.svg

# 自定義 eBPF 追蹤
bpftrace -e 'kprobe:do_sys_open { printf("%s opened %s\n", comm, str(arg1)); }'

# Ftrace 函數圖
trace-cmd record -p function_graph -F my_program
trace-cmd report
```

### 3. 生產環境監控
```bash
# 低開銷 CPU 採樣
perf record -F 49 -a -g -- sleep 60

# 實時 I/O 監控
biolatency-bpfcc 1

# TCP 連線追蹤
tcplife-bpfcc
```

---

## 工具對比總結

### 功能豐富度排名
1. **eBPF/BCC** - 最全面，支援幾乎所有追蹤場景
2. **SystemTap** - 功能強大，但需要內核開發知識
3. **perf** - 專注性能分析，硬體支援好
4. **LTTng** - 專注低開銷長期追蹤
5. **Ftrace** - 內核內建，功能實用
6. **KUTrace** - 專精微秒級全系統追蹤

### 易用性排名
1. **bcc-tools** - 開箱即用的工具集
2. **perf top/record** - 簡單直觀
3. **trace-cmd** - 簡化 ftrace 使用
4. **Ftrace** - 需要了解 sysfs 介面
5. **eBPF/bpftrace** - 需要學習語法
6. **SystemTap** - 學習曲線陡峭
7. **KUTrace** - 需要打補丁，門檻高

### 開銷排名（從低到高）
1. **LTTng** - 接近零開銷
2. **Ftrace** - 極低開銷（< 1%）
3. **eBPF** - 低開銷（內核聚合）
4. **perf** - 低開銷（採樣方式）
5. **KUTrace** - 低開銷（< 1%）
6. **SystemTap** - 中等開銷

---

## 參考資源

### 官方文檔
- [Linux Kernel Tracing](https://www.kernel.org/doc/html/latest/trace/)
- [perf Wiki](https://perf.wiki.kernel.org/)
- [eBPF Documentation](https://ebpf.io/)
- [BCC Tutorial](https://github.com/iovisor/bcc/blob/master/docs/tutorial.md)

### 推薦書籍
- **Systems Performance: Enterprise and the Cloud** (Brendan Gregg)
- **BPF Performance Tools** (Brendan Gregg)
- **Linux Kernel Development** (Robert Love)

### 線上資源
- [Brendan Gregg's Blog](https://www.brendangregg.com/)
- [Linux Performance](https://www.brendangregg.com/linuxperf.html)
- [eBPF Tracing Tools](https://www.brendangregg.com/ebpf.html)

---

## 總結

Linux 提供了豐富的效能分析工具，從內核內建的 Ftrace 到強大的 eBPF 框架，每個工具都有其適用場景。對於大多數使用者：

- **日常使用**：perf + bcc-tools
- **深度分析**：eBPF/bpftrace + Flame Graphs
- **生產環境**：LTTng 或低頻率的 perf 採樣

不需要像 KUTrace 那樣打內核補丁，就能獲得優秀的追蹤和分析能力。選擇合適的工具組合，可以高效地定位和解決性能問題。
