# BPF 特性的內核配置

## 與 BPF 相關的內核配置

| 功能 | 內核配置 | 描述 |
|:----|:----------|:-----|
| **基礎** | CONFIG_BPF_SYSCALL | 啟用 bpf() 系統調用 |
|  | CONFIG_BPF_JIT | BPF 程序通常由 BPF 解釋器處理。此選項允許內核在加載程序時生成本地代碼。這將顯著加速 BPF 程序的處理 |
|  | CONFIG_HAVE_BPF_JIT | 啟用 BPF 即時編譯器 |
|  | CONFIG_HAVE_EBPF_JIT | 擴展 BPF JIT (eBPF) |
|  | CONFIG_HAVE_CBPF_JIT | 經典 BPF JIT (cBPF) |
|  | CONFIG_MODULES | 啟用可加載內核模塊的構建 |
|  | CONFIG_BPF | BPF VM 解釋器 |
|  | CONFIG_BPF_EVENTS | 允許用戶將 BPF 程序附加到 kprobe、uprobe 和 tracepoint 事件上 |
|  | CONFIG_PERF_EVENTS | 內核性能事件和計數器 |
|  | CONFIG_HAVE_PERF_EVENTS | 啟用性能事件 |
|  | CONFIG_PROFILING | 啟用分析器使用的擴展分析支持機制 |
| **BTF** | CONFIG_DEBUG_INFO_BTF | 從 DWARF 調試信息生成去重的 BTF 類型信息 |
| | CONFIG_PAHOLE_HAS_SPLIT_BTF | 為每個選定的內核模塊生成 BTF |
| | CONFIG_DEBUG_INFO_BTF_MODULES | 為內核模塊生成緊湊的分割 BTF 類型信息 |
| **安全** | CONFIG_BPF_JIT_ALWAYS_ON | 啟用 BPF JIT 並刪除 BPF 解釋器以避免猜測執行 |
| | CONFIG_BPF_UNPRIV_DEFAULT_OFF | 通過設置默認禁用非特權 BPF |
| **Cgroup** | CONFIG_CGROUP_BPF | 支持將 BPF 程序附加到 cgroup 上 |
| **網絡** | CONFIG_BPFILTER | 基於 BPF 的數據包過濾框架 (BPFILTER) |
| | CONFIG_BPFILTER_UMH | 使用內嵌的用戶模式助手構建 bpfilter 內核模塊 |
| | CONFIG_NET_CLS_BPF | 基於可編程 BPF (JIT'ed) 過濾器進行數據包分類的基於 BPF 的分類器的替代方法 || | CONFIG_NET_ACT_BPF | 在數據包上執行BPF代碼。BPF代碼將決定是否丟棄數據包 |
| | CONFIG_BPF_STREAM_PARSER | 啟用此功能，允許使用BPF_MAP_TYPE_SOCKMAP與TCP流解析器配合使用 |
| | CONFIG_LWTUNNEL_BPF | 在路由查找入站和出站數據包後，允許作為下一跳操作運行BPF程序 |
| | CONFIG_NETFILTER_XT_MATCH_BPF | BPF匹配將對每個數據包應用Linux套接字過濾器，並接受過濾器返回非零值的數據包 |
| | CONFIG_IPV6_SEG6_BPF | 為支持BPF seg6local掛鉤，添加IPv6 Segement Routing助手 [參考](https://github.com/torvalds/linux/commit/fe94cc290f535709d3c5ebd1e472dfd0aec7ee7) |
| **kprobes** | CONFIG_KPROBE_EVENTS | 允許用戶通過ftrace接口動態添加跟蹤事件（類似於tracepoints） |
|  | CONFIG_KPROBES | 啟用基於kprobes的動態事件 |
|  | CONFIG_HAVE_KPROBES | 檢查是否啟用了kprobes |
|  | CONFIG_HAVE_REGS_AND_STACK_ACCESS_API | 如果架構支持從pt_regs訪問寄存器和堆棧條目所需的API，則應該選擇此符號。例如，基於kprobes的事件跟蹤器需要此API |
|  | CONFIG_KPROBES_ON_FTRACE | 如果架構支持將pt_regs完全傳遞給函數跟蹤，則在函數跟蹤器上有kprobes |
| **kprobe multi** | CONFIG_FPROBE | 啟用fprobe以一次性在多個函數上附加探測點 |
| **kprobe override** | CONFIG_BPF_KPROBE_OVERRIDE | 啟用BPF程序覆蓋kprobed函數 |
| **uprobes** | CONFIG_UPROBE_EVENTS | 啟用基於uprobes的動態事件 |
|  | CONFIG_ARCH_SUPPORTS_UPROBES | 架構特定的uprobes支持 |
|  | CONFIG_UPROBES | Uprobes是kprobes的用戶空間對應項：它們允許儀器應用程序（如'perf probe'）在用戶空間二進制文件和庫中建立非侵入性探測點，並在用戶空間應用程序觸發探測點時執行處理函數。 ||  | CONFIG_MMU | 基於MMU的虛擬化尋址空間支持，通過分頁內存管理 |
| **Tracepoints** | CONFIG_TRACEPOINTS | 啟用在內核中插入Tracepoints並與問題函數連接 |
|  | CONFIG_HAVE_SYSCALL_TRACEPOINTS | 啟用系統調用進入/退出跟蹤 |
| **Raw Tracepoints** | Same as Tracepoints | |
| **LSM** | CONFIG_BPF_LSM | 使用BPF程序對安全鉤子進行儀器化，實現動態MAC和審計策略 |
| **LIRC** | CONFIG_BPF_LIRC_MODE2 | 允許將BPF程序附加到lirc設備 |
