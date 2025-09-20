# Guider 指令參數完整指南

**版本：3.9.9_250918**
**測試日期：2025-09-20**
**測試環境：Ubuntu Linux 6.14.0**

## 目錄

1. [簡介](#簡介)
2. [基本用法](#基本用法)
3. [全域參數說明](#全域參數說明)
4. [指令分類](#指令分類)
   - [CONTROL - 控制類指令](#control---控制類指令)
   - [LOG - 日誌類指令](#log---日誌類指令)
   - [MONITOR - 監控類指令](#monitor---監控類指令)
   - [NETWORK - 網路類指令](#network---網路類指令)
   - [PROFILE - 效能分析指令](#profile---效能分析指令)
   - [TEST - 測試類指令](#test---測試類指令)
   - [TRACE - 追蹤類指令](#trace---追蹤類指令)
   - [UTIL - 工具類指令](#util---工具類指令)
   - [VISUAL - 視覺化指令](#visual---視覺化指令)
5. [常用指令詳解](#常用指令詳解)
6. [實用範例](#實用範例)

---

## 簡介

Guider 是一個強大的系統效能分析和監控工具，提供了 183 個指令，涵蓋了從進程監控、效能分析到視覺化等多個方面。本指南提供了所有指令的完整參數說明和使用範例。

## 基本用法

```bash
# 基本語法（安裝後）
guider COMMAND [OPTIONS] [--help]

# 直接執行（未安裝）
python3 guider/guider.py COMMAND [OPTIONS] [--help]

# 查看幫助
guider --help

# 查看特定指令的幫助
guider COMMAND --help

# 範例
guider top --help
```

## 全域參數說明

以下是 Guider 中常用的全域參數，大多數指令都支援這些參數：

| 參數 | 說明 | 範例 |
|------|------|------|
| `-e <CHARACTER>` | 啟用選項 | `-e a` 啟用 affinity |
| `-d <CHARACTER>` | 停用選項 | `-d c` 停用 CPU |
| `-o <DIR\|FILE>` | 設定輸出路徑 | `-o /tmp/output.out` |
| `-u` | 在背景執行 | `top -u` |
| `-W <SEC>` | 等待輸入 | `-W 5` 等待5秒 |
| `-f` | 強制執行 | `top -f` |
| `-b <SIZE:KB>` | 設定緩衝區大小 | `-b 1024` |
| `-T <PROC>` | 設定進程數量 | `-T 100` |
| `-j <DIR\|FILE>` | 設定報告路徑 | `-j /tmp/report` |
| `-w <TIME:FILE{:VALUE}>` | 設定額外命令 | `-w 10:cmd` |
| `-x <IP:PORT>` | 設定本地地址 | `-x 127.0.0.1:5555` |
| `-X <REQ@IP:PORT>` | 設定請求地址 | `-X req@127.0.0.1:5555` |
| `-N <REQ@IP:PORT>` | 設定報告地址 | `-N req@127.0.0.1:5555` |
| `-S <CHARACTER{:VALUE}>` | 按關鍵字排序 | `-S c:10` CPU > 10% |
| `-P` | 群組同進程的線程 | `top -P` |
| `-I <CMD\|FILE>` | 設定輸入命令或文件 | `-I ./a.out` |
| `-m <ROWS:COLS:SYSTEM>` | 設定終端大小 | `-m 40:80:linux` |
| `-a` | 顯示所有統計和事件 | `top -a` |
| `-g <COMM\|TID{:FILE}>` | 設定任務過濾器 | `-g 1234` or `-g chrome` |
| `-i <SEC>` | 設定間隔 | `-i 2` 每2秒 |
| `-R <INTERVAL:TIME:TERM>` | 設定重複計數 | `-R 1:10:auto` |
| `-C <PATH>` | 設定配置文件 | `-C /etc/guider.conf` |
| `-c <CMD>` | 設定熱鍵命令 | `-c "ls -la"` |
| `-Q` | 以流式打印所有行 | `top -Q` |
| `-q <NAME{:VALUE}>` | 設定環境變量 | `-q CMDLINE` |
| `-J` | 以 JSON 格式打印 | `top -J` |
| `-L <PATH>` | 設定日誌文件 | `-L /tmp/guider.log` |
| `-l <TYPE>` | 設定日誌類型 | `-l a` Android |
| `-E <DIR>` | 設定緩存目錄 | `-E /tmp/cache` |
| `-H <LEVEL>` | 設定函數深度級別 | `-H 5` |
| `-G <KEYWORD>` | 設定忽略列表 | `-G kernel` |
| `-k <COMM\|TID:SIG{:CONT}>` | 設定信號 | `-k 1234:9` |
| `-z <COMM\|TID:MASK{:CONT}>` | 設定 CPU 親和性 | `-z 1234:0x3` |
| `-Y <VALUES>` | 設定調度 | `-Y SCHED_FIFO:99` |
| `-v` | 詳細模式 | `top -v` |

## 指令分類

### CONTROL - 控制類指令

控制類指令用於管理和控制系統進程、資源限制等。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `cgroup` | Cgroup 管理 | Linux/Android | `guider cgroup <PID>` |
| `freeze` | 凍結線程 | Linux/Android | `guider freeze <TID>` |
| `hook` | 函數掛鉤 | Linux/Android | `guider hook <FUNCTION>` |
| `kill`/`tkill` | 發送信號 | Linux/Android/MacOS | `guider kill <PID> <SIG>` |
| `limitcpu` | 限制 CPU 使用 | Linux/Android | `guider limitcpu <PID> <PERCENT>` |
| `limitcpuset` | 限制 CPU 核心 | Linux/Android | `guider limitcpuset <PID> <CORES>` |
| `limitcpuw` | 限制 CPU 權重 | Linux/Android | `guider limitcpuw <PID> <WEIGHT>` |
| `limitmem` | 限制記憶體 | Linux/Android | `guider limitmem <PID> <MB>` |
| `limitmemsoft` | 軟限制記憶體 | Linux/Android | `guider limitmemsoft <PID> <MB>` |
| `limitpid` | 限制進程數 | Linux/Android | `guider limitpid <PID> <COUNT>` |
| `limitread` | 限制讀取 I/O | Linux/Android | `guider limitread <PID> <MB/S>` |
| `limitwrite` | 限制寫入 I/O | Linux/Android | `guider limitwrite <PID> <MB/S>` |
| `pause` | 暫停線程 | Linux/Android | `guider pause <TID>` |
| `remote` | 遠端命令 | Linux/Android | `guider remote <CMD>` |
| `rlimit` | 資源限制 | Linux/Android | `guider rlimit <PID>` |
| `setafnt` | 設定 CPU 親和性 | Linux/Android | `guider setafnt <PID> <MASK>` |
| `setcpu` | 設定 CPU 核心 | Linux/Android | `guider setcpu <PID> <CORE>` |
| `setsched` | 設定優先級 | Linux/Android | `guider setsched <PID> <PRIO>` |

### LOG - 日誌類指令

日誌類指令用於收集和分析各種系統日誌。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `logand` | Android 系統日誌 | Android | `guider logand` |
| `logdlt` | DLT 日誌 | Linux | `guider logdlt` |
| `logjrl` | Journal 日誌 | Linux | `guider logjrl` |
| `logkmsg` | Kernel 訊息 | Linux/Android | `guider logkmsg` |
| `logsys` | Syslog 日誌 | Linux | `guider logsys` |
| `logtrace` | Ftrace 日誌 | Linux/Android | `guider logtrace` |
| `printand` | 打印 Android 日誌 | Android | `guider printand` |
| `printdlt` | 打印 DLT 日誌 | Linux/MacOS/Windows | `guider printdlt` |
| `printjrl` | 打印 Journal 日誌 | Linux | `guider printjrl` |
| `printkmsg` | 打印 Kernel 訊息 | Linux/Android | `guider printkmsg` |
| `printsyslog` | 打印 Syslog | Linux | `guider printsyslog` |
| `printtrace` | 打印 Ftrace | Linux/Android | `guider printtrace` |

### MONITOR - 監控類指令

監控類指令提供即時系統監控功能。

| 指令 | 功能 | 平台支援 | 基本用法 | 常用參數 |
|------|------|----------|----------|----------|
| `andtop` | Android 日誌監控 | Android | `guider andtop` | `-a` 顯示所有 |
| `atop` | 全面系統監控 | Linux/Android | `guider atop` | `-a` 顯示所有 |
| `attop` | Atrace 監控 | Android | `guider attop` | `-a` 顯示所有 |
| `bdtop` | Binder 監控 | Android | `guider bdtop` | `-a` 顯示所有 |
| `bgtop` | 背景任務監控 | Linux/Android/MacOS/Windows | `guider bgtop` | `-a` 顯示所有 |
| `btop` | 函數監控 | Linux/Android | `guider btop` | `-g <FUNC>` 過濾函數 |
| `cgtop` | Cgroup 監控 | Linux/Android | `guider cgtop` | `-a` 顯示所有 |
| `contop` | 容器監控 | Linux/Android | `guider contop` | `-a` 顯示所有 |
| `ctop` | 閾值監控 | Linux/Android/MacOS/Windows | `guider ctop` | `-S c:10` CPU > 10% |
| `dbustop` | D-Bus 監控 | Linux | `guider dbustop` | `-a` 顯示所有 |
| `disktop` | 儲存監控 | Linux/Android/MacOS/Windows | `guider disktop` | `-a` 顯示所有 |
| `dlttop` | DLT 監控 | Linux/MacOS | `guider dlttop` | `-a` 顯示所有 |
| `fetop` | 文件事件監控 | Linux/Android | `guider fetop` | `-g <FILE>` 過濾文件 |
| `ftop` | 文件 I/O 監控 | Linux/Android/MacOS | `guider ftop` | `-a` 顯示所有 |
| `gfxtop` | 圖形監控 | Android | `guider gfxtop` | `-a` 顯示所有 |
| `irqtop` | IRQ 監控 | Linux/Android | `guider irqtop` | `-a` 顯示所有 |
| `kstop` | 內核堆疊監控 | Linux/Android | `guider kstop` | `-a` 顯示所有 |
| `ktop` | 內核函數監控 | Linux/Android | `guider ktop` | `-g <FUNC>` 過濾函數 |
| `mdtop` | 記憶體詳細監控 | Android | `guider mdtop` | `-a` 顯示所有 |
| `mtop` | 記憶體監控 | Linux/Android | `guider mtop` | `-a` 顯示所有 |
| `ntop` | 網路監控 | Linux/Android/MacOS/Windows | `guider ntop` | `-a` 顯示所有 |
| `ptop` | PMU 效能監控 | Linux/Android | `guider ptop` | `-a` 顯示所有 |
| `pytop` | Python 監控 | Linux/Android | `guider pytop` | `-g <SCRIPT>` 過濾腳本 |
| `rtop` | JSON 格式監控 | Linux/Android/MacOS/Windows | `guider rtop` | `-J` JSON 輸出 |
| `slabtop` | Slab 記憶體監控 | Linux/Android | `guider slabtop` | `-a` 顯示所有 |
| `stacktop` | 堆疊監控 | Linux/Android | `guider stacktop` | `-a` 顯示所有 |
| `systop` | 系統調用監控 | Linux/Android | `guider systop` | `-a` 顯示所有 |
| `top` | 進程監控 | Linux/Android/MacOS/Windows | `guider top` | `-a` 顯示所有<br>`-e T` 顯示總計<br>`-S c:1` CPU > 1% |
| `tptop` | Ftrace 監控 | Linux/Android | `guider tptop` | `-a` 顯示所有 |
| `trtop` | 樹狀進程監控 | Linux/Android | `guider trtop` | `-a` 顯示所有 |
| `ttop` | 線程監控 | Linux/Android | `guider ttop` | `-a` 顯示所有 |
| `utop` | 使用者函數監控 | Linux/Android | `guider utop` | `-g <FUNC>` 過濾函數 |
| `vtop` | 虛擬記憶體監控 | Linux/Android | `guider vtop` | `-a` 顯示所有 |
| `wtop` | WSS 記憶體監控 | Linux/Android | `guider wtop` | `-a` 顯示所有 |

### NETWORK - 網路類指令

網路類指令提供網路相關功能。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `cli` | 客戶端 | Linux/Android/MacOS/Windows | `guider cli <IP:PORT>` |
| `event` | 事件管理 | Linux/Android | `guider event` |
| `fserver` | 文件服務器 | Linux/Android/MacOS/Windows | `guider fserver <PORT>` |
| `hserver` | HTTP 服務器 | Linux/Android/MacOS/Windows | `guider hserver <PORT>` |
| `list` | 列表 | Linux/Android/MacOS/Windows | `guider list` |
| `send` | UDP 發送 | Linux/Android/MacOS/Windows | `guider send <IP:PORT> <MSG>` |
| `server` | 服務器 | Linux/Android/MacOS | `guider server <PORT>` |
| `start` | 開始信號 | Linux/Android | `guider start` |

### PROFILE - 效能分析指令

效能分析指令用於記錄和分析系統效能。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `filerec` | 文件操作記錄 | Linux/Android | `guider filerec -R 10` |
| `funcrec` | 函數調用記錄 | Linux/Android | `guider funcrec -R 10` |
| `genrec` | 通用系統記錄 | Linux/Android | `guider genrec -R 10` |
| `hprof` | 記憶體分析 | Android | `guider hprof <PID>` |
| `iorec` | I/O 操作記錄 | Linux/Android | `guider iorec -R 10` |
| `mem` | 分頁記憶體分析 | Linux/Android | `guider mem <PID>` |
| `rec` | 線程記錄 | Linux/Android | `guider rec -R 10` |
| `report` | 生成報告 | Linux/Android/MacOS/Windows | `guider report <FILE>` |
| `sperf` | 函數效能分析 | Android | `guider sperf` |
| `sysrec` | 系統調用記錄 | Linux/Android | `guider sysrec -R 10` |

### TEST - 測試類指令

測試類指令提供系統壓力測試功能。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `cputest` | CPU 壓力測試 | Linux/Android/MacOS/Windows | `guider cputest <THREADS>` |
| `helptest` | 幫助測試 | ALL | `guider helptest` |
| `iotest` | 儲存 I/O 測試 | Linux/Android/MacOS/Windows | `guider iotest <SIZE>` |
| `memtest` | 記憶體壓力測試 | Linux/Android/MacOS/Windows | `guider memtest <SIZE>` |
| `nettest` | 網路測試 | Linux/Android | `guider nettest <IP>` |

### TRACE - 追蹤類指令

追蹤類指令提供系統追蹤功能。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `btrace` | 函數追蹤 | Linux/Android | `guider btrace <FUNCTION>` |
| `leaktrace` | 洩漏追蹤 | Linux/Android | `guider leaktrace <PID>` |
| `mtrace` | 記憶體追蹤 | Linux/Android | `guider mtrace <PID>` |
| `pytrace` | Python 追蹤 | Linux/Android | `guider pytrace <SCRIPT>` |
| `sigtrace` | 信號追蹤 | Linux/Android | `guider sigtrace <PID>` |
| `stat` | PMU 統計 | Linux/Android | `guider stat <PID>` |
| `strace` | 系統調用追蹤 | Linux/Android | `guider strace <PID>` |
| `utrace` | 使用者函數追蹤 | Linux/Android | `guider utrace <FUNCTION>` |

### UTIL - 工具類指令

工具類指令提供各種實用功能。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `addr2sym` | 地址轉符號 | Linux/Android/MacOS/Windows | `guider addr2sym <ADDR>` |
| `andcmd` | Android 命令 | Android | `guider andcmd <CMD>` |
| `bugrec` | Bug 報告記錄 | Android | `guider bugrec` |
| `bugrep` | Bug 報告 | Android | `guider bugrep` |
| `checkdup` | 檢查重複頁面 | Linux/Android | `guider checkdup` |
| `comp` | 壓縮 | Linux/Android/MacOS/Windows | `guider comp <FILE>` |
| `convlog` | 日誌轉換 | Linux/Android/MacOS/Windows | `guider convlog <FILE>` |
| `decomp` | 解壓縮 | Linux/Android/MacOS/Windows | `guider decomp <FILE>` |
| `demangle` | C++ 符號還原 | Linux/Android/MacOS/Windows | `guider demangle <SYMBOL>` |
| `dirdiff` | 目錄差異 | Linux/Android/MacOS/Windows | `guider dirdiff <DIR1> <DIR2>` |
| `dump` | 記憶體轉儲 | Linux/Android | `guider dump <PID> <ADDR>` |
| `dumpstack` | 堆疊轉儲 | Linux/Android | `guider dumpstack <PID>` |
| `elftree` | ELF 依賴樹 | Linux/Android/MacOS/Windows | `guider elftree <FILE>` |
| `exec` | 執行命令 | Linux/Android/MacOS/Windows | `guider exec <CMD>` |
| `fadvise` | 文件建議 | Linux/Android | `guider fadvise <FILE>` |
| `flush` | 清除記憶體 | Linux/Android | `guider flush` |
| `getafnt` | 獲取親和性 | Linux/Android | `guider getafnt <PID>` |
| `getpid` | 獲取 PID | Linux/Android | `guider getpid <NAME>` |
| `getprop` | 獲取屬性 | Android | `guider getprop <PROP>` |
| `less` | 分頁器 | Linux/Android/MacOS/Windows | `guider less <FILE>` |
| `merge` | 合併文件 | Linux/Android/MacOS/Windows | `guider merge <FILE1> <FILE2>` |
| `mkcache` | 建立緩存 | Linux/Android/MacOS/Windows | `guider mkcache <DIR>` |
| `mnttree` | 掛載樹 | Linux/Android | `guider mnttree` |
| `mount` | 掛載 | Linux/Android | `guider mount <DEV> <PATH>` |
| `ping` | ICMP 測試 | Linux/Android/MacOS/Windows | `guider ping <IP>` |
| `print` | 打印文件 | Linux/Android/MacOS/Windows | `guider print <FILE>` |
| `printbind` | 打印綁定 | Linux/Android | `guider printbind` |
| `printboot` | 打印啟動信息 | Android | `guider printboot` |
| `printcg` | 打印 Cgroup | Linux/Android | `guider printcg` |
| `printdbus` | 打印 D-Bus | Linux | `guider printdbus` |
| `printdbusintro` | 打印 D-Bus 內省 | Linux | `guider printdbusintro` |
| `printdbusstat` | 打印 D-Bus 統計 | Linux | `guider printdbusstat` |
| `printdbussub` | 打印 D-Bus 訂閱 | Linux | `guider printdbussub` |
| `printdir` | 打印目錄 | Linux/Android/MacOS/Windows | `guider printdir <DIR>` |
| `printenv` | 打印環境變量 | Linux/Android | `guider printenv` |
| `printext` | 打印 Ext4 信息 | Linux/Android/MacOS/Windows | `guider printext <DEV>` |
| `printinfo` | 打印系統信息 | Linux/Android | `guider printinfo` |
| `printkconf` | 打印內核配置 | Linux/Android | `guider printkconf` |
| `printns` | 打印命名空間 | Linux/Android | `guider printns` |
| `printsdfile` | 打印 Systemd 文件 | Linux | `guider printsdfile` |
| `printsdinfo` | 打印 Systemd 信息 | Linux | `guider printsdinfo` |
| `printsdunit` | 打印 Systemd 單元 | Linux | `guider printsdunit` |
| `printsig` | 打印信號 | Linux/Android | `guider printsig` |
| `printslab` | 打印 Slab | Linux/Android | `guider printslab` |
| `printvma` | 打印 Vmalloc | Linux/Android | `guider printvma` |
| `ps` | 進程列表 | Linux/Android/MacOS/Windows | `guider ps` |
| `pstree` | 進程樹 | Linux/Android/MacOS/Windows | `guider pstree` |
| `readahead` | 預讀 | Linux/Android | `guider readahead <FILE>` |
| `readelf` | 讀取 ELF | Linux/Android/MacOS/Windows | `guider readelf <FILE>` |
| `req` | URL 請求 | Linux/Android/MacOS/Windows | `guider req <URL>` |
| `scrcap` | 螢幕截圖 | Android | `guider scrcap` |
| `scrrec` | 螢幕錄製 | Android | `guider scrrec` |
| `setprop` | 設定屬性 | Android | `guider setprop <PROP> <VALUE>` |
| `split` | 分割文件 | Linux/Android/MacOS/Windows | `guider split <FILE> <SIZE>` |
| `strings` | 提取文本 | Linux/Android/MacOS/Windows | `guider strings <FILE>` |
| `sym2addr` | 符號轉地址 | Linux/Android/MacOS/Windows | `guider sym2addr <SYMBOL>` |
| `sync` | 同步文件 | Linux/Android | `guider sync` |
| `sysrq` | SysRq 命令 | Linux/Android | `guider sysrq <KEY>` |
| `systat` | 系統狀態 | Linux/Android | `guider systat` |
| `topdiff` | Top 差異 | Linux/Android/MacOS/Windows | `guider topdiff <FILE1> <FILE2>` |
| `topsum` | Top 總結 | Linux/Android/MacOS/Windows | `guider topsum <FILE>` |
| `umount` | 卸載 | Linux/Android | `guider umount <PATH>` |
| `watch` | 監視文件 | Linux/Android | `guider watch <FILE>` |
| `watchprop` | 監視屬性 | Android | `guider watchprop <PROP>` |

### VISUAL - 視覺化指令

視覺化指令將數據轉換為圖表。

| 指令 | 功能 | 平台支援 | 基本用法 |
|------|------|----------|----------|
| `convert` | 文本轉換 | Linux/MacOS/Windows | `guider convert <FILE>` |
| `draw` | 繪製系統圖表 | Linux/MacOS/Windows | `guider draw <FILE>` |
| `drawavg` | 繪製平均值圖表 | Linux/MacOS/Windows | `guider drawavg <FILE>` |
| `drawbitmap` | 繪製位圖 | Linux/MacOS/Windows | `guider drawbitmap <FILE>` |
| `drawcpu` | 繪製 CPU 圖表 | Linux/MacOS/Windows | `guider drawcpu <FILE>` |
| `drawcpuavg` | 繪製 CPU 平均圖表 | Linux/MacOS/Windows | `guider drawcpuavg <FILE>` |
| `drawdelay` | 繪製延遲圖表 | Linux/MacOS/Windows | `guider drawdelay <FILE>` |
| `drawdiff` | 繪製差異圖表 | Linux/MacOS/Windows | `guider drawdiff <FILE1> <FILE2>` |
| `drawflame` | 繪製火焰圖 | Linux/MacOS/Windows | `guider drawflame <FILE>` |
| `drawflamediff` | 繪製差異火焰圖 | Linux/MacOS/Windows | `guider drawflamediff <FILE1> <FILE2>` |
| `drawhist` | 繪製直方圖 | Linux/MacOS/Windows | `guider drawhist <FILE>` |
| `drawio` | 繪製 I/O 圖表 | Linux/MacOS/Windows | `guider drawio <FILE>` |
| `drawleak` | 繪製洩漏圖表 | Linux/MacOS/Windows | `guider drawleak <FILE>` |
| `drawmem` | 繪製記憶體圖表 | Linux/MacOS/Windows | `guider drawmem <FILE>` |
| `drawmemavg` | 繪製記憶體平均圖表 | Linux/MacOS/Windows | `guider drawmemavg <FILE>` |
| `drawpri` | 繪製優先級圖表 | Linux/MacOS/Windows | `guider drawpri <FILE>` |
| `drawreq` | 繪製請求圖表 | Linux/MacOS/Windows | `guider drawreq <FILE>` |
| `drawrss` | 繪製 RSS 圖表 | Linux/MacOS/Windows | `guider drawrss <FILE>` |
| `drawrssavg` | 繪製 RSS 平均圖表 | Linux/MacOS/Windows | `guider drawrssavg <FILE>` |
| `drawstack` | 繪製堆疊圖表 | Linux/MacOS/Windows | `guider drawstack <FILE>` |
| `drawtime` | 繪製時間軸圖表 | Linux/MacOS/Windows | `guider drawtime <FILE>` |
| `drawviolin` | 繪製小提琴圖 | Linux/MacOS/Windows | `guider drawviolin <FILE>` |
| `drawvss` | 繪製 VSS 圖表 | Linux/MacOS/Windows | `guider drawvss <FILE>` |
| `drawvssavg` | 繪製 VSS 平均圖表 | Linux/MacOS/Windows | `guider drawvssavg <FILE>` |

## 常用指令詳解

### top 指令詳解

`top` 是最常用的系統監控指令，提供豐富的參數選項：

#### 啟用選項 (-e)
```bash
# 啟用 affinity 顯示
guider top -e a

# 啟用多個選項
guider top -e "aTmn"
```

可用選項：
- `a`: affinity (CPU 親和性)
- `A`: secAttr (安全屬性)
- `b`: block (阻塞統計)
- `B`: bar (條形圖)
- `c`: cpu (CPU 統計)
- `C`: compress (壓縮)
- `d`: disk (磁碟統計)
- `D`: DWARF (調試信息)
- `e`: encode (編碼)
- `E`: exec (執行)
- `f`: float (浮點數顯示)
- `F`: wfc (等待文件完成)
- `G`: cgroup (Cgroup 信息)
- `h`: sigHandler (信號處理器)
- `H`: sched (調度信息)
- `i`: irq (中斷統計)
- `I`: elastic (彈性搜索)
- `k`: peak (峰值)
- `K`: cgroupRoot (Cgroup 根)
- `l`: threshold (閾值)
- `L`: cmdline (命令行)
- `m`: mem (記憶體統計)
- `M`: min (最小統計)
- `n`: net (網路統計)
- `N`: namespace (命名空間)
- `o`: oomScore (OOM 分數)
- `O`: iosched (I/O 調度器)
- `p`: pipe (管道)
- `P`: perf (性能計數器)
- `q`: quit (自動退出)
- `Q`: group (群組信息)
- `r`: report (報告)
- `R`: reportFile (報告文件)
- `s`: stack (堆疊)
- `S`: pss (PSS 記憶體)
- `t`: thread (線程)
- `T`: total (總計)
- `u`: uss (USS 記憶體)
- `U`: unit (單位)
- `w`: wss (WSS 記憶體)
- `W`: wchan (等待通道)
- `x`: fixTarget (固定目標)
- `X`: exe (執行檔路徑)
- `Y`: delay (延遲)

#### 停用選項 (-d)
```bash
# 停用 CPU 統計
guider top -d c

# 停用多個選項
guider top -d "cmn"
```

#### 排序選項 (-S)
```bash
# 按 CPU 使用率排序
guider top -S c

# 按記憶體排序，顯示大於 500MB 的進程
guider top -S m:500

# 按記憶體排序，顯示小於 10MB 的進程（升序）
guider top -S "m:<10" -q ORDERASC
```

排序鍵：
- `c`: CPU 使用率
- `m`: 記憶體 (RSS)
- `p`: PID
- `N`: 進程名稱
- `b`: 阻塞時間
- `w`: wfc (等待文件完成)
- `n`: 新進程
- `f`: 文件數
- `r`: 運行時間
- `s`: swap
- `e`: 執行時間
- `P`: 優先級
- `C`: 上下文切換
- `o`: OOM 分數

#### 環境變量選項 (-q)
```bash
# 顯示命令行
guider top -q CMDLINE

# 設定 OOM 調整值
guider top -q OOMADJ:-1000

# 只顯示 Android 應用
guider top -q ANDAPP

# 顯示系統百分比
guider top -q SYSPER

# KB 為單位顯示
guider top -q KBUNIT

# 顯示 Cgroup 信息
guider top -q PRINTCG

# 顯示 Cgroup 信息（指定類型）
guider top -q PRINTCG:"cpu+cpuacct+memory+blkio"

# 快速初始化
guider top -q FASTINIT

# 不轉換大小單位
guider top -q NOCONVSIZE

# 不轉換時間單位
guider top -q NOCONVTIME

# 不格式化數字
guider top -q NOCONVNUM
```

### 記錄與重播

```bash
# 記錄 3 秒並輸出到文件
# 注意：輸出文件名會自動添加時長後綴
guider top -R 1:3:auto -o /tmp/test.out
# 實際輸出文件：/tmp/test.out_00:00:03

# 記錄 10 秒
guider top -R 1:10:auto -o /tmp/guider.out
# 實際輸出文件：/tmp/guider.out_00:00:10

# 生成視覺化圖表（注意使用完整文件名）
guider draw /tmp/test.out_00:00:03
# 輸出：/tmp/test_graph.svg

# 生成 CPU 圖表
guider drawcpu /tmp/test.out_00:00:03
# 輸出：/tmp/test_graph.svg

# 生成記憶體圖表
guider drawmem /tmp/test.out_00:00:03
# 輸出：/tmp/test_graph.svg
```

### 過濾選項

```bash
# 監控特定 PID
guider top -g 1234

# 監控特定進程名
guider top -g chrome

# 使用萬用字元
guider top -g "chrome*"
guider top -g "*worker"

# 排除特定進程
guider top -g "^test"

# 用戶過濾
guider top -q USERFILTER:"root*"
```

### 條件控制

```bash
# 等待用戶輸入後開始
guider top -a -W

# 等待 5 秒後開始
guider top -a -W 5s

# 從系統啟動 100 秒後開始
guider top -a -q STARTCONDTIME:100

# 當特定任務創建時開始
guider top -a -q STARTCONDTASK:"yes|test*"

# 當文件存在時開始
guider top -a -q STARTCONDFILE:"/tmp/start"

# 當文件不存在時開始
guider top -a -q STARTCONDNOFILE:"/tmp/stop"

# CPU 使用率大於 10% 時開始
guider top -a -q STARTCONDCPUMORE:10 -R

# 特定進程結束時退出
guider top -a -q EXITCONDTERM:"a.out"

# 新進程啟動時退出
guider top -a -q EXITCONDNEW:"test"

# 運行到指定時間退出
guider top -a -q EXITCONDTIME:100
```

### JSON 輸出

```bash
# JSON 格式輸出
guider top -J

# 完整 JSON 統計
guider top -J -q ALLJSONSTAT

# 過濾 JSON 欄位
guider top -J -q JSONFILTER:"*mem", JSONFILTER:"*cpu"
```

## 實用範例

### 系統監控範例

```bash
# 1. 監控所有進程，顯示完整統計
guider top -a

# 2. 監控 CPU 使用率超過 1% 的進程
guider top -S c:1

# 3. 監控記憶體使用超過 500MB 的進程
guider top -S m:500

# 4. 監控特定進程並記錄 30 秒
guider top -g chrome -R 1:30:auto -o /tmp/chrome.out
# 實際輸出文件：/tmp/chrome.out_00:00:30

# 5. 顯示進程樹狀結構
guider pstree

# 6. 顯示進程列表
guider ps

# 7. 監控文件 I/O 操作（需要 root）
sudo guider ftop -a

# 8. 監控網路連接
guider ntop -a

# 9. 監控系統調用（需要 root）
sudo guider systop -a

# 10. 顯示進程的命令行參數
guider top -e L

# 11. 顯示線程級別的詳細信息
guider ttop -a

# 12. 按執行時間排序進程
guider top -S e

# 13. 顯示進程的 CPU 親和性
guider top -e a

# 14. 顯示記憶體詳細信息（包含 PSS）
guider top -e S

# 15. 監控阻塞的進程
guider top -e b -S b:100
```

### 效能分析範例

```bash
# 1. 記錄系統效能 60 秒（需要 root）
sudo guider rec -R 1:60:auto -o /tmp/rec.out
# 實際輸出文件：/tmp/rec.out_00:01:00

# 2. 使用 top 記錄（不需要 root）
guider top -a -R 1:60:auto -o /tmp/top.out
# 實際輸出文件：/tmp/top.out_00:01:00

# 3. 生成視覺化圖表
guider draw /tmp/top.out_00:01:00
# 輸出：/tmp/top_graph.svg

# 4. 生成 CPU 使用圖表
guider drawcpu /tmp/top.out_00:01:00
# 輸出：/tmp/top_graph.svg

# 5. 生成記憶體使用圖表
guider drawmem /tmp/top.out_00:01:00
# 輸出：/tmp/top_graph.svg

# 6. 生成火焰圖（需要函數追蹤數據）
sudo guider funcrec -R 1:10:auto -o /tmp/func.out
guider drawflame /tmp/func.out_00:00:10
```

### 故障診斷範例

```bash
# 1. 追蹤記憶體洩漏
guider leaktrace <PID>

# 2. 追蹤系統調用
guider strace <PID>

# 3. 追蹤信號
guider sigtrace <PID>

# 4. 轉儲進程堆疊
guider dumpstack <PID>

# 5. 查看進程的 CPU 親和性
guider getafnt <PID>

# 6. 查看系統信息
guider printinfo

# 7. 查看內核配置
guider printkconf

# 8. 查看 Slab 記憶體
guider printslab
```

### 壓力測試範例

```bash
# 1. CPU 壓力測試（4 線程）
guider cputest 4

# 2. 記憶體壓力測試（1GB）
guider memtest 1024

# 3. I/O 壓力測試（100MB）
guider iotest 100

# 4. 網路測試
guider nettest 127.0.0.1
```

### 進階用法範例

```bash
# 1. 監控並在 CPU 超過 80% 時自動記錄
guider top -a -q STARTCONDCPUMORE:80 -R 60 -o

# 2. 監控特定目錄的文件變化
guider top -a -q MONDIR:"/tmp/test"

# 3. 監控並顯示 GPU 記憶體
guider top -a -q GPUMEM

# 4. 監控並顯示 GPU 溫度
guider top -a -q GPUTEMP

# 5. 監控容器資源使用
guider contop -a

# 6. 監控 D-Bus 活動
guider dbustop -a

# 7. 以條形圖顯示 CPU 使用
guider top -a -e B

# 8. 監控並在程序結束時執行命令
guider top -a -q EXITCMD:"ls -lha"

# 9. 結合多個條件
guider top -a -q STARTCONDCPUMORE:10, STARTCONDMEMMORE:1000 -R

# 10. 流式輸出（適合管道處理）
guider top -a -q TASKSTREAM -Q -S c:1
```

### 視覺化範例

```bash
# 1. 記錄數據（實際文件名會包含時長）
guider top -R 1:60:auto -o /tmp/data.out
# 實際輸出文件：/tmp/data.out_00:01:00

# 2. 生成系統總覽圖表
guider draw /tmp/data.out_00:01:00
# 輸出：/tmp/data_graph.svg

# 3. 生成 CPU 使用趨勢圖
guider drawcpu /tmp/data.out_00:01:00
# 輸出：/tmp/data_graph.svg（會覆蓋之前的圖表）

# 4. 生成記憶體使用趨勢圖
guider drawmem /tmp/data.out_00:01:00
# 輸出：/tmp/data_graph.svg（會覆蓋之前的圖表）

# 5. 生成火焰圖（需要函數追蹤數據）
sudo guider funcrec -R 1:10:auto -o /tmp/func.out
guider drawflame /tmp/func.out_00:00:10

# 6. 生成直方圖
guider drawhist /tmp/data.out_00:01:00

# 7. 生成小提琴圖
guider drawviolin /tmp/data.out_00:01:00

# 8. 比較兩個數據文件
guider drawdiff /tmp/data1.out_00:01:00 /tmp/data2.out_00:01:00

# 9. 生成平均值圖表
guider drawavg /tmp/data.out_00:01:00

# 10. 生成時間軸圖表
guider drawtime /tmp/data.out_00:01:00
```

## 注意事項

1. **權限要求**：某些指令需要 root 權限才能完全運行，例如 `ftop`、`strace`、`rec`、`funcrec` 等。
2. **輸出文件命名**：
   - 使用 `-o` 參數記錄時，實際輸出文件名會自動添加時長後綴
   - 例如：`-o /tmp/test.out` 實際輸出為 `/tmp/test.out_00:00:03`
   - 視覺化時需要使用完整的文件名（包含時長後綴）
3. **視覺化輸出**：
   - 默認輸出為 SVG 格式，文件名為 `<basename>_graph.svg`
   - 多次運行會自動備份舊文件為 `_old.svg`
4. **平台相容性**：不同平台支援的指令不同，請參考指令分類中的平台支援欄位。
5. **資源消耗**：持續監控會消耗系統資源，建議根據需要調整監控間隔和範圍。
6. **視覺化要求**：視覺化功能需要安裝 matplotlib 和 numpy：
   ```bash
   pip install -r guider/requirements.txt
   ```

## 進階參數詳解

### 時間與間隔控制
```bash
# -i: 設定間隔（秒）
guider top -i 2           # 每 2 秒更新
guider top -i 0.5         # 每 0.5 秒更新

# -R: 設定重複計數 (INTERVAL:TIME:TERM)
guider top -R 1:10:auto   # 每 1 秒，總共 10 秒，自動結束
guider top -R 2:60:manual # 每 2 秒，總共 60 秒，手動結束

# -W: 等待輸入或時間
guider top -W             # 等待用戶按鍵開始
guider top -W 5           # 等待 5 秒開始
guider top -W 5s          # 等待 5 秒開始（明確單位）
```

### 輸出與日誌控制
```bash
# -o: 設定輸出路徑（檔案會自動添加時長後綴）
guider top -o /tmp/test.out        # 輸出到 /tmp/test.out_HH:MM:SS
guider top -o .                    # 輸出到當前目錄
guider top -o /var/log/guider/     # 輸出到指定目錄

# -L: 設定日誌文件
guider top -L /tmp/guider.log      # 記錄日誌到指定文件

# -l: 設定日誌類型
guider top -l a                    # Android 日誌
guider top -l d                    # DLT 日誌
guider top -l k                    # KMSG 日誌
guider top -l j                    # Journal 日誌
guider top -l s                    # Syslog 日誌
```

### 效能與資源控制
```bash
# -b: 設定緩衝區大小
guider top -b 1024                 # 1024 KB 緩衝區
guider top -b 50m                  # 50 MB 緩衝區
guider top -b 1g                   # 1 GB 緩衝區

# -T: 設定進程數量限制
guider top -T 100                  # 最多顯示 100 個進程
guider top -T 50                   # 最多顯示 50 個進程
```

### 網路與遠端控制
```bash
# -x: 設定本地地址
guider top -x 127.0.0.1:5555       # 綁定本地地址和端口

# -X: 設定請求地址
guider top -X req@192.168.1.100:5555

# -N: 設定報告地址
guider top -N report@192.168.1.100:5555
```

## 常見問題

### Q1: 如何在背景執行監控？
```bash
guider top -u -R 1:3600:auto -o /tmp/monitor.out
# 實際輸出文件：/tmp/monitor.out_01:00:00
```

### Q2: 如何監控特定用戶的所有進程？
```bash
guider top -q USERFILTER:"username*"
```

### Q3: 如何生成定期報告？
```bash
# 使用 cron 定期執行
0 * * * * guider top -R 1:300:auto -o /var/log/guider/hourly.out
# 實際輸出文件：/var/log/guider/hourly.out_00:05:00
```

### Q4: 如何監控 Docker 容器？
```bash
guider contop -a
```

### Q5: 如何追蹤特定函數的調用？
```bash
# 需要 root 權限
sudo guider btrace <function_name>
```

### Q6: 如何查看所有可用的環境變量選項？
```bash
# 使用 --help 查看完整列表
guider top --help | grep -A 100 "set environment"
```

### Q7: 如何同時監控多個條件？
```bash
# CPU 和記憶體同時超過閾值
guider top -a -q STARTCONDCPUMORE:80, STARTCONDMEMMORE:1000 -R

# 多個過濾條件
guider top -g "chrome*" -S c:5 -q USERFILTER:"user*"
```

### Q8: 如何自定義輸出格式？
```bash
# JSON 格式
guider top -J

# 流式輸出
guider top -Q

# 不轉換單位
guider top -q NOCONVSIZE, NOCONVTIME, NOCONVNUM
```

## 完整參數快速參考

### 監控類命令通用參數
| 參數 | 功能描述 | 範例 |
|------|----------|------|
| `-a` | 顯示所有統計和事件 | `guider top -a` |
| `-e <CHAR>` | 啟用選項 | `guider top -e aBcT` |
| `-d <CHAR>` | 停用選項 | `guider top -d cmt` |
| `-g <FILTER>` | 過濾任務 | `guider top -g chrome` |
| `-S <KEY:VAL>` | 排序 | `guider top -S c:5` |
| `-i <SEC>` | 間隔 | `guider top -i 2` |
| `-o <PATH>` | 輸出路徑 | `guider top -o /tmp/out` |
| `-R <I:T:M>` | 記錄 | `guider top -R 1:60:auto` |
| `-J` | JSON 輸出 | `guider top -J` |
| `-Q` | 流式輸出 | `guider top -Q` |
| `-q <VAR>` | 環境變量 | `guider top -q CMDLINE` |
| `-W <TIME>` | 等待 | `guider top -W 5s` |
| `-u` | 背景執行 | `guider top -u` |
| `-v` | 詳細模式 | `guider top -v` |
| `-P` | 群組線程 | `guider top -P` |
| `-T <NUM>` | 進程數限制 | `guider top -T 50` |
| `-b <SIZE>` | 緩衝區大小 | `guider top -b 50m` |
| `-L <PATH>` | 日誌文件 | `guider top -L /tmp/log` |
| `-l <TYPE>` | 日誌類型 | `guider top -l dks` |
| `-c <CMD>` | 熱鍵命令 | `guider top -c "ls -la"` |
| `-C <PATH>` | 配置文件 | `guider top -C /etc/guider.conf` |
| `-f` | 強制執行 | `guider top -f` |
| `-m <R:C:S>` | 終端大小 | `guider top -m 40:80:linux` |

### 啟用選項 (-e) 詳細說明
| 字元 | 功能 | 描述 |
|------|------|------|
| `a` | affinity | CPU 親和性 |
| `A` | secAttr | 安全屬性 |
| `b` | block | 阻塞統計 |
| `B` | bar | 條形圖顯示 |
| `c` | cpu | CPU 統計 |
| `C` | compress | 壓縮 |
| `d` | disk | 磁碟統計 |
| `D` | DWARF | 調試信息 |
| `e` | encode | 編碼 |
| `E` | exec | 執行 |
| `f` | float | 浮點數顯示 |
| `F` | wfc | 等待文件完成 |
| `G` | cgroup | Cgroup 信息 |
| `h` | sigHandler | 信號處理器 |
| `H` | sched | 調度信息 |
| `i` | irq | 中斷統計 |
| `I` | elastic | 彈性搜索 |
| `k` | peak | 峰值統計 |
| `K` | cgroupRoot | Cgroup 根 |
| `l` | threshold | 閾值 |
| `L` | cmdline | 命令行 |
| `m` | mem | 記憶體統計 |
| `M` | min | 最小統計 |
| `n` | net | 網路統計 |
| `N` | namespace | 命名空間 |
| `o` | oomScore | OOM 分數 |
| `O` | iosched | I/O 調度器 |
| `p` | pipe | 管道 |
| `P` | perf | 性能計數器 |
| `q` | quit | 自動退出 |
| `Q` | group | 群組信息 |
| `r` | report | 報告 |
| `R` | reportFile | 報告文件 |
| `s` | stack | 堆疊 |
| `S` | pss | PSS 記憶體 |
| `t` | thread | 線程 |
| `T` | total | 總計 |
| `u` | uss | USS 記憶體 |
| `U` | unit | 單位 |
| `w` | wss | WSS 記憶體 |
| `W` | wchan | 等待通道 |
| `x` | fixTarget | 固定目標 |
| `X` | exe | 執行檔路徑 |
| `Y` | delay | 延遲 |

## 更多資源

- 官方文檔：查看項目 README.md
- 配置文件：編輯 guider.conf 進行自定義配置
- 問題回報：https://github.com/iipeace/guider/issues
- 源碼倉庫：https://github.com/iipeace/guider

---

*本指南基於 Guider 3.9.9_250918 版本編寫，測試於 Ubuntu Linux 6.14.0，不同版本和平台可能有所差異。*
