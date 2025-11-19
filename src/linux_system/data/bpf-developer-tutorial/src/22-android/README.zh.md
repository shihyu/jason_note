# 在 Android 上使用 eBPF 程序

> 本文主要記錄了筆者在 Android Studio Emulator 中測試高版本 Android Kernel 對基於 libbpf 的 CO-RE 技術支持程度的探索過程、結果和遇到的問題。
> 測試採用的方式是在 Android Shell 環境下構建 Debian 環境，並基於此嘗試構建 eunomia-bpf 工具鏈、運行其測試用例。

## 背景

截至目前（2023-04），Android 還未對 eBPF 程序的動態加載做出較好的支持，無論是以 bcc 為代表的帶編譯器分發方案，還是基於 btf 和 libbpf 的 CO-RE 方案，都在較大程度上離不開 Linux 環境的支持，無法在 Android 系統上很好地運行[^WeiShu]。

雖然如此，在 Android 平臺上嘗試 eBPF 也已經有了一些成功案例，除谷歌官方提供的修改 `Android.bp` 以將 eBPF 程序隨整個系統一同構建並掛載的方案[^Google]，也有人提出基於 Android 內核構建 Linux 環境進而運行 eBPF 工具鏈的思路，並開發了相關工具。

目前已有的資料，大多基於 adeb/eadb 在 Android 內核基礎上構建 Linux 沙箱，並對 bcc 和 bpftrace 相關工具鏈進行測試，而對 CO-RE 方案的測試工作較少。在 Android 上使用 bcc 工具目前有較多參考資料，如：

+ SeeFlowerX：<https://blog.seeflower.dev/category/eBPF/>
+ evilpan：<https://bbs.kanxue.com/thread-271043.htm>

其主要思路是利用 chroot 在 Android 內核上運行一個 Debian 鏡像，並在其中構建整個 bcc 工具鏈，從而使用 eBPF 工具。如果想要使用 bpftrace，原理也是類似的。

事實上，高版本的 Android 內核已支持 btf 選項，這意味著 eBPF 領域中新興的 CO-RE 技術也應當能夠運用到基於 Android 內核的 Linux 系統中。本文將基於此對 eunomia-bpf 在模擬器環境下進行測試運行。

> [eunomia-bpf](https://github.com/eunomia-bpf/eunomia-bpf) 是一個結合了 libbpf 和 WebAssembly 技術的開源項目，旨在簡化 eBPF 程序的編寫、編譯和部署。該項目可被視作 CO-RE 的一種實踐方式，其核心依賴是 libbpf，相信對 eunomia-bpf 的測試工作能夠為其他 CO-RE 方案提供參考。

## 測試環境

+ Android Emulator（Android Studio Flamingo | 2022.2.1）
+ AVD: Pixel 6
+ Android Image: Tiramisu Android 13.0 x86_64（5.15.41-android13-8-00055-g4f5025129fe8-ab8949913）

## 環境搭建[^SeeFlowerX]

1. 從 [eadb 倉庫](https://github.com/tiann/eadb) 的 releases 頁面獲取 `debianfs-amd64-full.tar.gz` 作為 Linux 環境的 rootfs，同時還需要獲取該項目的 `assets` 目錄來構建環境；
2. 從 Android Studio 的 Device Manager 配置並啟動 Android Virtual Device；
3. 通過 Android Studio SDK 的 adb 工具將 `debianfs-amd64-full.tar.gz` 和 `assets` 目錄推送到 AVD 中：
   + `./adb push debianfs-amd64-full.tar.gz /data/local/tmp/deb.tar.gz`
   + `./adb push assets /data/local/tmp/assets`
4. 通過 adb 進入 Android shell 環境並獲取 root 權限：
   + `./adb shell`
   + `su`
5. 在 Android shell 中構建並進入 debian 環境：
   + `mkdir -p /data/eadb`
   + `mv /data/local/tmp/assets/* /data/eadb`
   + `mv /data/local/tmp/deb.tar.gz /data/eadb/deb.tar.gz`
   + `rm -r /data/local/tmp/assets`
   + `chmod +x /data/eadb/device-*`
   + `/data/eadb/device-unpack`
   + `/data/eadb/run /data/eadb/debian`

至此，測試 eBPF 所需的 Linux 環境已經構建完畢。此外，在 Android shell 中（未進入 debian 時）可以通過 `zcat /proc/config.gz` 並配合 `grep` 查看內核編譯選項。

>目前，eadb 打包的 debian 環境存在 libc 版本低，缺少的工具依賴較多等情況；並且由於內核編譯選項不同，一些 eBPF 功能可能也無法使用。

## 工具構建

在 debian 環境中將 eunomia-bpf 倉庫 clone 到本地，具體的構建過程，可以參考倉庫的 [build.md](https://eunomia.dev/eunomia-bpf/setup/build)。在本次測試中，筆者選用了 `ecc` 編譯生成 `package.json` 的方式，該工具的構建和使用方式請參考[倉庫頁面](https://github.com/eunomia-bpf/eunomia-bpf/tree/master/compiler)。

>在構建過程中，可能需要自行安裝包括但不限於 `curl`，`pkg-config`，`libssl-dev` 等工具。

## 結果

有部分 eBPF 程序可以成功在 Android 上運行，但也會有部分應用因為種種原因無法成功被執行。

### 成功案例

#### [bootstrap](https://github.com/eunomia-bpf/eunomia-bpf/tree/master/examples/bpftools/bootstrap)

運行輸出如下：

```console
TIME     PID     PPID    EXIT_CODE  DURATION_NS  COMM    FILENAME  EXIT_EVENT
09:09:19  10217  479     0          0            sh      /system/bin/sh 0
09:09:19  10217  479     0          0            ps      /system/bin/ps 0
09:09:19  10217  479     0          54352100     ps                1
09:09:21  10219  479     0          0            sh      /system/bin/sh 0
09:09:21  10219  479     0          0            ps      /system/bin/ps 0
09:09:21  10219  479     0          44260900     ps                1
```

#### [tcpstates](https://github.com/eunomia-bpf/eunomia-bpf/tree/master/examples/bpftools/tcpstates)

開始監測後在 Linux 環境中通過 `wget` 下載 Web 頁面：

```console
TIME     SADDR   DADDR   SKADDR  TS_US   DELTA_US  PID     OLDSTATE  NEWSTATE  FAMILY  SPORT   DPORT   TASK
09:07:46  0x4007000200005000000000000f02000a 0x5000000000000f02000a8bc53f77 18446635827774444352 3315344998 0 10115 7 2 2 0 80 wget
09:07:46  0x40020002d98e50003d99f8090f02000a 0xd98e50003d99f8090f02000a8bc53f77 18446635827774444352 3315465870 120872 0 2 1 2 55694 80 swapper/0
09:07:46  0x40010002d98e50003d99f8090f02000a 0xd98e50003d99f8090f02000a8bc53f77 18446635827774444352 3315668799 202929 10115 1 4 2 55694 80 wget
09:07:46  0x40040002d98e50003d99f8090f02000a 0xd98e50003d99f8090f02000a8bc53f77 18446635827774444352 3315670037 1237 0 4 5 2 55694 80 swapper/0
09:07:46  0x40050002000050003d99f8090f02000a 0x50003d99f8090f02000a8bc53f77 18446635827774444352 3315670225 188 0 5 7 2 55694 80 swapper/0
09:07:47  0x400200020000bb01565811650f02000a 0xbb01565811650f02000a6aa0d9ac 18446635828348806592 3316433261 0 2546 2 7 2 49970 443 ChromiumNet
09:07:47  0x400200020000bb01db794a690f02000a 0xbb01db794a690f02000aea2afb8e 18446635827774427776 3316535591 0 1469 2 7 2 37386 443 ChromiumNet
```

開始檢測後在 Android Studio 模擬界面打開 Chrome 瀏覽器並訪問百度頁面：

```console
TIME     SADDR   DADDR   SKADDR  TS_US   DELTA_US  PID     OLDSTATE  NEWSTATE  FAMILY  SPORT   DPORT   TASK
07:46:58  0x400700020000bb01000000000f02000a 0xbb01000000000f02000aeb6f2270 18446631020066638144 192874641 0 3305 7 2 2 0 443 NetworkService
07:46:58  0x40020002d28abb01494b6ebe0f02000a 0xd28abb01494b6ebe0f02000aeb6f2270 18446631020066638144 192921938 47297 3305 2 1 2 53898 443 NetworkService
07:46:58  0x400700020000bb01000000000f02000a 0xbb01000000000f02000ae7e7e8b7 18446631020132433920 193111426 0 3305 7 2 2 0 443 NetworkService
07:46:58  0x40020002b4a0bb0179ff85e80f02000a 0xb4a0bb0179ff85e80f02000ae7e7e8b7 18446631020132433920 193124670 13244 3305 2 1 2 46240 443 NetworkService
07:46:58  0x40010002b4a0bb0179ff85e80f02000a 0xb4a0bb0179ff85e80f02000ae7e7e8b7 18446631020132433920 193185397 60727 3305 1 4 2 46240 443 NetworkService
07:46:58  0x40040002b4a0bb0179ff85e80f02000a 0xb4a0bb0179ff85e80f02000ae7e7e8b7 18446631020132433920 193186122 724 3305 4 5 2 46240 443 NetworkService
07:46:58  0x400500020000bb0179ff85e80f02000a 0xbb0179ff85e80f02000ae7e7e8b7 18446631020132433920 193186244 122 3305 5 7 2 46240 443 NetworkService
07:46:59  0x40010002d01ebb01d0c52f5c0f02000a 0xd01ebb01d0c52f5c0f02000a51449c27 18446631020103553856 194110884 0 5130 1 8 2 53278 443 ThreadPoolForeg
07:46:59  0x400800020000bb01d0c52f5c0f02000a 0xbb01d0c52f5c0f02000a51449c27 18446631020103553856 194121000 10116 3305 8 7 2 53278 443 NetworkService
07:46:59  0x400700020000bb01000000000f02000a 0xbb01000000000f02000aeb6f2270 18446631020099513920 194603677 0 3305 7 2 2 0 443 NetworkService
07:46:59  0x40020002d28ebb0182dd92990f02000a 0xd28ebb0182dd92990f02000aeb6f2270 18446631020099513920 194649313 45635 12 2 1 2 53902 443 ksoftirqd/0
07:47:00  0x400700020000bb01000000000f02000a 0xbb01000000000f02000a26f6e878 18446631020132433920 195193350 0 3305 7 2 2 0 443 NetworkService
07:47:00  0x40020002ba32bb01e0e09e3a0f02000a 0xba32bb01e0e09e3a0f02000a26f6e878 18446631020132433920 195206992 13642 0 2 1 2 47666 443 swapper/0
07:47:00  0x400700020000bb01000000000f02000a 0xbb01000000000f02000ae7e7e8b7 18446631020132448128 195233125 0 3305 7 2 2 0 443 NetworkService
07:47:00  0x40020002b4a8bb0136cac8dd0f02000a 0xb4a8bb0136cac8dd0f02000ae7e7e8b7 18446631020132448128 195246569 13444 3305 2 1 2 46248 443 NetworkService
07:47:00  0xf02000affff00000000000000000000 0x1aca06cffff00000000000000000000 18446631019225912320 195383897 0 947 7 2 10 0 80 Thread-11
07:47:00  0x40010002b4a8bb0136cac8dd0f02000a 0xb4a8bb0136cac8dd0f02000ae7e7e8b7 18446631020132448128 195421584 175014 3305 1 4 2 46248 443 NetworkService
07:47:00  0x40040002b4a8bb0136cac8dd0f02000a 0xb4a8bb0136cac8dd0f02000ae7e7e8b7 18446631020132448128 195422361 777 3305 4 5 2 46248 443 NetworkService
07:47:00  0x400500020000bb0136cac8dd0f02000a 0xbb0136cac8dd0f02000ae7e7e8b7 18446631020132448128 195422450 88 3305 5 7 2 46248 443 NetworkService
07:47:01  0x400700020000bb01000000000f02000a 0xbb01000000000f02000aea2afb8e 18446631020099528128 196321556 0 1315 7 2 2 0 443 ChromiumNet
```

### 一些可能的報錯原因

#### [opensnoop](https://github.com/eunomia-bpf/eunomia-bpf/tree/master/examples/bpftools/opensnoop)

例如 opensnoop 工具，可以在 Android 上成功構建，但運行報錯：

```console
libbpf: failed to determine tracepoint 'syscalls/sys_enter_open' perf event ID: No such file or directory
libbpf: prog 'tracepoint__syscalls__sys_enter_open': failed to create tracepoint 'syscalls/sys_enter_open' perf event: No such file or directory
libbpf: prog 'tracepoint__syscalls__sys_enter_open': failed to auto-attach: -2
failed to attach skeleton
Error: BpfError("load and attach ebpf program failed")
```

後經查看發現內核未開啟 `CONFIG_FTRACE_SYSCALLS` 選項，導致無法使用 syscalls 的 tracepoint。

## 總結

在 Android shell 中查看內核編譯選項可以發現  `CONFIG_DEBUG_INFO_BTF` 默認是打開的，在此基礎上 eunomia-bpf 項目提供的 example 已有一些能夠成功運行的案例，例如可以監測 `exec` 族函數的執行和 tcp 連接的狀態。

對於無法運行的一些，原因主要是以下兩個方面：

1. 內核編譯選項未支持相關 eBPF 功能；
2. eadb 打包的 Linux 環境較弱，缺乏必須依賴；

目前在 Android 系統中使用 eBPF 工具基本上仍然需要構建完整的 Linux 運行環境，但 Android 內核本身對 eBPF 的支持已較為全面，本次測試證明較高版本的 Android 內核支持 BTF 調試信息和依賴 CO-RE 的 eBPF 程序的運行。

Android 系統 eBPF 工具的發展需要官方新特性的加入，目前看來通過 Android APP 直接使用 eBPF 工具需要的工作量較大，同時由於 eBPF 工具需要 root 權限，普通 Android 用戶的使用會面臨較多困難。

如果希望學習更多關於 eBPF 的知識和實踐，可以訪問我們的教程代碼倉庫 <https://github.com/eunomia-bpf/bpf-developer-tutorial> 或網站 <https://eunomia.dev/zh/tutorials/> 以獲取更多示例和完整的教程。

## 參考

[^Google]:<https://source.android.google.cn/docs/core/architecture/kernel/bpf>
[^WeiShu]:<https://mp.weixin.qq.com/s/mul4n5D3nXThjxuHV7GpMA>
[^SeeFlowerX]:<https://blog.seeflower.dev/archives/138/>
