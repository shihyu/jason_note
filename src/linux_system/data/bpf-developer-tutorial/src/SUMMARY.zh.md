# eBPF 開發實踐教程：基於 CO-RE，通過小工具快速上手 eBPF 開發

這是一個基於 `CO-RE`（一次編譯，到處運行）的 eBPF 的開發教程，提供了從入門到進階的 eBPF 開發實踐，包括基本概念、代碼實例、實際應用等內容。和 BCC 不同的是，我們使用 libbpf、Cilium、libbpf-rs、eunomia-bpf 等框架進行開發，包含 C、Go、Rust 等語言的示例。

本教程不會進行復雜的概念講解和場景介紹，主要希望提供一些 eBPF 小工具的案例（**非常短小，從二十行代碼開始入門！**），來幫助 eBPF 應用的開發者快速上手 eBPF 的開發方法和技巧。教程內容可以在目錄中找到，每個目錄都是一個獨立的 eBPF 工具案例。

教程關注於可觀測性、網絡、安全等等方面的 eBPF 示例。完整的代碼和教程可以在 [https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) GitHub 開源倉庫中找到。**如果您認為本教程對您有所幫助，也請給我們一個 star 鼓勵一下！**

# 入門示例

這一部分包含簡單的 eBPF 程序示例和介紹。主要利用 `eunomia-bpf` 框架簡化開發，介紹 eBPF 的基本用法和開發流程。

- [lesson 0-introduce](0-introduce/README.zh.md) eBPF 示例教程 0：核心概念與工具簡介
- [lesson 1-helloworld](1-helloworld/README.zh.md) eBPF 入門開發實踐教程一：Hello World，基本框架和開發流程
- [lesson 2-kprobe-unlink](2-kprobe-unlink/README.zh.md) eBPF 入門開發實踐教程二：在 eBPF 中使用 kprobe 監測捕獲 unlink 系統調用
- [lesson 3-fentry-unlink](3-fentry-unlink/README.zh.md) eBPF 入門開發實踐教程三：在 eBPF 中使用 fentry 監測捕獲 unlink 系統調用
- [lesson 4-opensnoop](4-opensnoop/README.zh.md) eBPF 入門開發實踐教程四：在 eBPF 中捕獲進程打開文件的系統調用集合，使用全局變量過濾進程 pid
- [lesson 5-uprobe-bashreadline](5-uprobe-bashreadline/README.zh.md) eBPF 入門開發實踐教程五：在 eBPF 中使用  uprobe 捕獲 bash 的 readline 函數調用
- [lesson 6-sigsnoop](6-sigsnoop/README.zh.md) eBPF 入門開發實踐教程六：捕獲進程發送信號的系統調用集合，使用 hash map 保存狀態
- [lesson 7-execsnoop](7-execsnoop/README.zh.md) eBPF 入門實踐教程七：捕獲進程執行事件，通過 perf event array 向用戶態打印輸出
- [lesson 8-exitsnoop](8-exitsnoop/README.zh.md) eBPF 入門開發實踐教程八：在 eBPF 中使用 exitsnoop 監控進程退出事件，使用 ring buffer 向用戶態打印輸出
- [lesson 9-runqlat](9-runqlat/README.zh.md) eBPF 入門開發實踐教程九：捕獲進程調度延遲，以直方圖方式記錄
- [lesson 10-hardirqs](10-hardirqs/README.zh.md) eBPF 入門開發實踐教程十：在 eBPF 中使用 hardirqs 或 softirqs 捕獲中斷事件

# 高級文檔和示例

我們開始構建完整的 eBPF 項目，主要基於 `libbpf`，並將其與各種應用場景結合起來，以便實際使用。

- [lesson 11-bootstrap](11-bootstrap/README.zh.md) eBPF 入門開發實踐教程十一：在 eBPF 中使用 libbpf 開發用戶態程序並跟蹤 exec() 和 exit() 系統調用
- [lesson 12-profile](12-profile/README.zh.md) eBPF 入門實踐教程十二：使用 eBPF 程序 profile 進行性能分析
- [lesson 13-tcpconnlat](13-tcpconnlat/README.zh.md) eBPF入門開發實踐教程十三：統計 TCP 連接延時，並使用 libbpf 在用戶態處理數據
- [lesson 14-tcpstates](14-tcpstates/README.zh.md) eBPF入門實踐教程十四：記錄 TCP 連接狀態與 TCP RTT
- [lesson 15-javagc](15-javagc/README.zh.md) eBPF 入門實踐教程十五：使用 USDT 捕獲用戶態 Java GC 事件耗時
- [lesson 16-memleak](16-memleak/README.zh.md) eBPF 入門實踐教程十六：編寫 eBPF 程序 Memleak 監控內存洩漏
- [lesson 17-biopattern](17-biopattern/README.zh.md) eBPF 入門實踐教程十七：編寫 eBPF 程序統計隨機/順序磁盤 I/O
- [lesson 18-further-reading](18-further-reading/README.zh.md) 更多的參考資料：論文、項目等等
- [lesson 19-lsm-connect](19-lsm-connect/README.zh.md) eBPF 入門實踐教程：使用 LSM 進行安全檢測防禦
- [lesson 20-tc](20-tc/README.zh.md) eBPF 入門實踐教程二十：使用 eBPF 進行 tc 流量控制
- [lesson 21-xdp](21-xdp/README.zh.md) eBPF 入門實踐教程二十一： 使用 XDP 進行可編程數據包處理

# 深入主題

這一部分涵蓋了與 eBPF 相關的高級主題，包括在 Android 上使用 eBPF 程序、利用 eBPF 程序進行的潛在攻擊和防禦以及複雜的追蹤。結合用戶模式和內核模式的 eBPF 可以帶來強大的能力（也可能帶來安全風險）。

Android:

- [lesson 22-android](22-android/README.zh.md) 在 Android 上使用 eBPF 程序
網絡:

- [lesson 23-http](23-http/README.zh.md) 通過 eBPF socket filter 或 syscall trace 追蹤 HTTP 請求等七層協議 - eBPF 實踐教程
- [lesson 29-sockops](29-sockops/README.zh.md) eBPF 開發實踐：使用 sockops 加速網絡請求轉發
- [lesson 41-xdp-tcpdump](41-xdp-tcpdump/README.zh.md) eBPF 示例教程：使用 XDP 捕獲 TCP 信息
- [lesson 42-xdp-loadbalancer](42-xdp-loadbalancer/README.zh.md) eBPF 開發者教程： 簡單的 XDP 負載均衡器
安全:

- [lesson 24-hide](24-hide/README.zh.md) eBPF 開發實踐：使用 eBPF 隱藏進程或文件信息
- [lesson 25-signal](25-signal/README.zh.md) eBPF 入門實踐教程：用 bpf_send_signal 發送信號終止惡意進程
- [lesson 26-sudo](26-sudo/README.zh.md) 使用 eBPF 添加 sudo 用戶
- [lesson 27-replace](27-replace/README.zh.md) 使用 eBPF 替換任意程序讀取或寫入的文本
- [lesson 28-detach](28-detach/README.zh.md) 在應用程序退出後運行 eBPF 程序：eBPF 程序的生命週期
- [lesson 34-syscall](34-syscall/README.zh.md) eBPF 開發實踐：使用 eBPF 修改系統調用參數
調度器:

- [lesson 44-scx-simple](44-scx-simple/README.zh.md) eBPF 教程：BPF 調度器入門
- [lesson 45-scx-nest](45-scx-nest/README.zh.md) eBPF 示例教程：實現 `scx_nest` 調度器

GPU:

- [lesson 47-cuda-events](47-cuda-events/README.zh.md) 使用 eBPF 追蹤 CUDA 操作

其他:

- [lesson 35-user-ringbuf](35-user-ringbuf/README.zh.md) eBPF開發實踐：使用 user ring buffer 向內核異步發送信息
- [lesson 36-userspace-ebpf](36-userspace-ebpf/README.zh.md) 用戶空間 eBPF 運行時：深度解析與應用實踐
- [lesson 38-btf-uprobe](38-btf-uprobe/README.zh.md) 藉助 eBPF 和 BTF，讓用戶態也能一次編譯、到處運行
- [lesson 43-kfuncs](43-kfuncs/README.zh.md) 超越 eBPF 的極限：在內核模塊中定義自定義 kfunc

持續更新中...

# bcc 和 bpftrace 教程與文檔

- [BPF Features by Linux Kernel Version](bcc-documents/kernel-versions.md)
- [Kernel Configuration for BPF Features](bcc-documents/kernel_config.md)
- [bcc Reference Guide](bcc-documents/reference_guide.md)
- [Special Filtering](bcc-documents/special_filtering.md)
- [bcc Tutorial](bcc-documents/tutorial.md)
- [bcc Python Developer Tutorial](bcc-documents/tutorial_bcc_python_developer.md)
- [bpftrace Tutorial](bpftrace-tutorial/README.md)
