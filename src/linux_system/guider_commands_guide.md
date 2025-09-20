# Guider 指令參數完整指南

**版本：3.9.9_250517**

## 目錄

1. [簡介](#簡介)
2. [基本用法](#基本用法)
3. [指令分類](#指令分類)
   - [CONTROL - 控制類指令](#control---控制類指令)
   - [LOG - 日誌類指令](#log---日誌類指令)
   - [MONITOR - 監控類指令](#monitor---監控類指令)
   - [NETWORK - 網路類指令](#network---網路類指令)
   - [PROFILE - 效能分析指令](#profile---效能分析指令)
   - [TEST - 測試類指令](#test---測試類指令)
   - [TRACE - 追蹤類指令](#trace---追蹤類指令)
   - [UTIL - 工具類指令](#util---工具類指令)
   - [VISUAL - 視覺化指令](#visual---視覺化指令)
4. [常用指令詳解](#常用指令詳解)
5. [實用範例](#實用範例)
6. [參數說明對照表](#參數說明對照表)

---

## 簡介

Guider 是一個強大的系統效能分析和監控工具，提供了 182 個指令，涵蓋了從進程監控、效能分析到視覺化等多個方面。本指南提供了所有指令的完整參數說明和使用範例。

## 基本用法

```bash
# 基本語法
guider COMMAND [OPTIONS] [--help]

# 查看幫助
guider --help

# 查看特定指令的幫助
guider COMMAND --help

# 範例
guider top --help
```

## 指令分類

### CONTROL - 控制類指令

控制類指令用於管理和控制系統進程、資源限制等。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `cgroup` | Cgroup 管理 | Linux/Android |
| `freeze` | 凍結執行緒 | Linux/Android |
| `hook` | 函數掛鉤 | Linux/Android |
| `kill`/`tkill` | 發送訊號 | Linux/Android/MacOS |
| `limitcpu` | 限制 CPU 使用 | Linux/Android |
| `limitcpuset` | 限制 CPU 核心 | Linux/Android |
| `limitcpuw` | 限制 CPU 權重 | Linux/Android |
| `limitmem` | 限制記憶體 | Linux/Android |
| `limitmemsoft` | 軟性記憶體限制 | Linux/Android |
| `limitpid` | 限制任務數 | Linux/Android |
| `limitread` | 限制讀取 I/O | Linux/Android |
| `limitwrite` | 限制寫入 I/O | Linux/Android |
| `pause` | 暫停執行緒 | Linux/Android |
| `remote` | 遠端指令 | Linux/Android |
| `rlimit` | 資源限制 | Linux/Android |
| `setafnt` | 設定親和性 | Linux/Android |
| `setcpu` | 設定 CPU 核心 | Linux/Android |
| `setsched` | 設定排程優先級 | Linux/Android |

### LOG - 日誌類指令

日誌類指令用於收集和顯示系統各類日誌。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `logand` | Android 系統日誌 | Android |
| `logdlt` | DLT 日誌 | Linux |
| `logjrl` | Journal 日誌 | Linux |
| `logkmsg` | 核心訊息日誌 | Linux/Android |
| `logsys` | Syslog 日誌 | Linux |
| `logtrace` | Ftrace 日誌 | Linux/Android |
| `printand` | 列印 Android 日誌 | Android |
| `printdlt` | 列印 DLT 日誌 | Linux/MacOS/Windows |
| `printjrl` | 列印 Journal 日誌 | Linux |
| `printkmsg` | 列印核心訊息 | Linux/Android |
| `printsyslog` | 列印 Syslog | Linux |
| `printtrace` | 列印 Ftrace | Linux/Android |

### MONITOR - 監控類指令

監控類指令提供即時系統監控功能。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `andtop` | Android 日誌監控 | Android |
| `atop` | 全系統監控 | Linux/Android |
| `attop` | Atrace 監控 | Android |
| `bdtop` | Binder 監控 | Android |
| `bgtop` | 背景任務監控 | Linux/Android/MacOS/Windows |
| `btop` | 函數監控 | Linux/Android |
| `cgtop` | Cgroup 監控 | Linux/Android |
| `contop` | 容器監控 | Linux/Android |
| `ctop` | 臨界值監控 | Linux/Android/MacOS/Windows |
| `dbustop` | D-Bus 監控 | Linux |
| `disktop` | 儲存裝置監控 | Linux/Android/MacOS/Windows |
| `dlttop` | DLT 監控 | Linux/MacOS |
| `fetop` | 檔案事件監控 | Linux/Android |
| `ftop` | 檔案監控 | Linux/Android/MacOS |
| `gfxtop` | 圖形監控 | Android |
| `irqtop` | 中斷監控 | Linux/Android |
| `kstop` | 堆疊監控 | Linux/Android |
| `ktop` | 核心函數監控 | Linux/Android |
| `mdtop` | Android 記憶體監控 | Android |
| `mtop` | 記憶體監控 | Linux/Android |
| `ntop` | 網路監控 | Linux/Android/MacOS/Windows |
| `ptop` | PMU 監控 | Linux/Android |
| `pytop` | Python 監控 | Linux/Android |
| `rtop` | JSON 監控 | Linux/Android/MacOS/Windows |
| `slabtop` | Slab 監控 | Linux/Android |
| `stacktop` | 堆疊監控 | Linux/Android |
| `systop` | 系統呼叫監控 | Linux/Android |
| **`top`** | **進程監控** | Linux/Android/MacOS/Windows |
| `tptop` | Ftrace 監控 | Linux/Android |
| `trtop` | 樹狀監控 | Linux/Android |
| `ttop` | 執行緒監控 | Linux/Android |
| `utop` | 使用者函數監控 | Linux/Android |
| `vtop` | 虛擬記憶體監控 | Linux/Android |
| `wtop` | WSS 監控 | Linux/Android |

### NETWORK - 網路類指令

網路類指令提供網路相關功能。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `cli` | 客戶端 | Linux/Android/MacOS/Windows |
| `event` | 事件處理 | Linux/Android |
| `fserver` | 檔案伺服器 | Linux/Android/MacOS/Windows |
| `hserver` | HTTP 伺服器 | Linux/Android/MacOS/Windows |
| `list` | 列表功能 | Linux/Android/MacOS/Windows |
| `send` | UDP 發送 | Linux/Android/MacOS/Windows |
| `server` | 伺服器 | Linux/Android/MacOS |
| `start` | 啟動訊號 | Linux/Android |

### PROFILE - 效能分析指令

效能分析指令用於記錄和分析系統效能。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `filerec` | 檔案記錄 | Linux/Android |
| `funcrec` | 函數記錄 | Linux/Android |
| `genrec` | 一般系統記錄 | Linux/Android |
| `hprof` | 記憶體分析 | Android |
| `iorec` | I/O 記錄 | Linux/Android |
| `mem` | 頁面記憶體 | Linux/Android |
| **`rec`** | **執行緒事件記錄** | Linux/Android |
| `report` | 生成報告 | Linux/Android/MacOS/Windows |
| `sperf` | 函數效能 | Android |
| `sysrec` | 系統呼叫記錄 | Linux/Android |

### TEST - 測試類指令

測試類指令用於系統效能測試。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `cputest` | CPU 測試 | Linux/Android/MacOS/Windows |
| `helptest` | 幫助測試 | 所有平台 |
| `iotest` | 儲存裝置測試 | Linux/Android/MacOS/Windows |
| `memtest` | 記憶體測試 | Linux/Android/MacOS/Windows |
| `nettest` | 網路測試 | Linux/Android |

### TRACE - 追蹤類指令

追蹤類指令用於追蹤系統行為。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `btrace` | 函數追蹤 | Linux/Android |
| `leaktrace` | 記憶體洩漏追蹤 | Linux/Android |
| `mtrace` | 記憶體追蹤 | Linux/Android |
| `pytrace` | Python 追蹤 | Linux/Android |
| `sigtrace` | 訊號追蹤 | Linux/Android |
| `stat` | PMU 統計 | Linux/Android |
| **`strace`** | **系統呼叫追蹤** | Linux/Android |
| `utrace` | 使用者函數追蹤 | Linux/Android |

### UTIL - 工具類指令

工具類指令提供各種實用工具功能。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `addr2sym` | 位址轉符號 | Linux/Android/MacOS/Windows |
| `andcmd` | Android 指令 | Android |
| `bugrec` | 錯誤記錄 | Android |
| `bugrep` | 錯誤報告 | Android |
| `checkdup` | 檢查重複頁面 | Linux/Android |
| `comp` | 壓縮 | Linux/Android/MacOS/Windows |
| `convlog` | 日誌轉換 | Linux/Android/MacOS/Windows |
| `decomp` | 解壓縮 | Linux/Android/MacOS/Windows |
| `demangle` | 名稱還原 | Linux/Android/MacOS/Windows |
| `dirdiff` | 目錄差異 | Linux/Android/MacOS/Windows |
| `dump` | 記憶體傾印 | Linux/Android |
| `elftree` | ELF 樹狀結構 | Linux/Android/MacOS/Windows |
| `exec` | 執行指令 | Linux/Android/MacOS/Windows |
| `fadvise` | 檔案建議 | Linux/Android |
| `flush` | 清除記憶體 | Linux/Android |
| `getafnt` | 取得親和性 | Linux/Android |
| `getpid` | 取得 PID | Linux/Android |
| `getprop` | 取得屬性 | Android |
| `less` | 分頁器 | Linux/Android/MacOS/Windows |
| `merge` | 合併檔案 | Linux/Android/MacOS/Windows |
| `mkcache` | 建立快取 | Linux/Android/MacOS/Windows |
| `mnttree` | 掛載樹狀結構 | Linux/Android |
| `mount` | 掛載 | Linux/Android |
| `ping` | ICMP ping | Linux/Android/MacOS/Windows |
| `print` | 列印檔案 | Linux/Android/MacOS/Windows |
| `printbind` | 列印綁定函數 | Linux/Android |
| `printboot` | 列印啟動資訊 | Android |
| `printcg` | 列印 Cgroup | Linux/Android |
| `printdbus` | 列印 D-Bus | Linux |
| `printdbusintro` | 列印 D-Bus 介紹 | Linux |
| `printdbusstat` | 列印 D-Bus 狀態 | Linux |
| `printdbussub` | 列印 D-Bus 訂閱 | Linux |
| `printdir` | 列印目錄 | Linux/Android/MacOS/Windows |
| `printenv` | 列印環境變數 | Linux/Android |
| `printext` | 列印 Ext4 | Linux/Android/MacOS/Windows |
| `printinfo` | 列印系統資訊 | Linux/Android |
| `printkconf` | 列印核心設定 | Linux/Android |
| `printns` | 列印命名空間 | Linux/Android |
| `printsdfile` | 列印 Systemd 檔案 | Linux |
| `printsdinfo` | 列印 Systemd 資訊 | Linux |
| `printsdunit` | 列印 Systemd 單元 | Linux |
| `printsig` | 列印訊號 | Linux/Android |
| `printslab` | 列印 Slab | Linux/Android |
| `printvma` | 列印 Vmalloc | Linux/Android |
| **`ps`** | **進程列表** | Linux/Android/MacOS/Windows |
| `pstree` | 進程樹 | Linux/Android/MacOS/Windows |
| `readahead` | 預讀檔案 | Linux/Android |
| `readelf` | 讀取 ELF 檔案 | Linux/Android/MacOS/Windows |
| `req` | URL 請求 | Linux/Android/MacOS/Windows |
| `scrcap` | 螢幕截圖 | Android |
| `scrrec` | 螢幕錄製 | Android |
| `setprop` | 設定屬性 | Android |
| `split` | 分割檔案 | Linux/Android/MacOS/Windows |
| `strings` | 提取文字 | Linux/Android/MacOS/Windows |
| `sym2addr` | 符號轉位址 | Linux/Android/MacOS/Windows |
| `sync` | 同步檔案 | Linux/Android |
| `sysrq` | 系統請求 | Linux/Android |
| `systat` | 系統狀態 | Linux/Android |
| `topdiff` | 差異比較 | Linux/Android/MacOS/Windows |
| `topsum` | 摘要統計 | Linux/Android/MacOS/Windows |
| `umount` | 卸載 | Linux/Android |
| `watch` | 監視檔案 | Linux/Android |
| `watchprop` | 監視屬性 | Android |

### VISUAL - 視覺化指令

視覺化指令用於生成各種圖表和視覺化輸出。

| 指令 | 功能描述 | 支援平台 |
|------|---------|----------|
| `convert` | 轉換文字 | Linux/MacOS/Windows |
| `draw` | 繪製系統圖表 | Linux/MacOS/Windows |
| `drawavg` | 繪製平均值 | Linux/MacOS/Windows |
| `drawbitmap` | 繪製點陣圖 | Linux/MacOS/Windows |
| `drawcpu` | 繪製 CPU 圖表 | Linux/MacOS/Windows |
| `drawcpuavg` | 繪製 CPU 平均值 | Linux/MacOS/Windows |
| `drawdelay` | 繪製延遲圖 | Linux/MacOS/Windows |
| `drawdiff` | 繪製差異圖 | Linux/MacOS/Windows |
| `drawflame` | 繪製火焰圖 | Linux/MacOS/Windows |
| `drawflamediff` | 繪製火焰圖差異 | Linux/MacOS/Windows |
| `drawhist` | 繪製直方圖 | Linux/MacOS/Windows |
| `drawio` | 繪製 I/O 圖表 | Linux/MacOS/Windows |
| `drawleak` | 繪製記憶體洩漏 | Linux/MacOS/Windows |
| `drawmem` | 繪製記憶體圖表 | Linux/MacOS/Windows |
| `drawmemavg` | 繪製記憶體平均值 | Linux/MacOS/Windows |
| `drawpri` | 繪製優先級圖 | Linux/MacOS/Windows |
| `drawreq` | 繪製請求圖 | Linux/MacOS/Windows |
| `drawrss` | 繪製 RSS 圖表 | Linux/MacOS/Windows |
| `drawrssavg` | 繪製 RSS 平均值 | Linux/MacOS/Windows |
| `drawstack` | 繪製堆疊圖 | Linux/MacOS/Windows |
| `drawtime` | 繪製時間軸 | Linux/MacOS/Windows |
| `drawviolin` | 繪製小提琴圖 | Linux/MacOS/Windows |
| `drawvss` | 繪製 VSS 圖表 | Linux/MacOS/Windows |
| `drawvssavg` | 繪製 VSS 平均值 | Linux/MacOS/Windows |

---

## 常用指令詳解

### 1. top - 進程監控

**功能：** 監控系統進程狀態

**基本語法：**
```bash
guider top [OPTIONS]
```

**主要參數：**

| 參數 | 說明 |
|------|------|
| `-e <CHARACTER>` | 啟用選項 |
| `-d <CHARACTER>` | 停用選項 |
| `-o <DIR\|FILE>` | 設定輸出路徑 |
| `-u` | 在背景執行 |
| `-W <SEC>` | 等待輸入（秒） |
| `-f` | 強制執行 |
| `-b <SIZE:KB>` | 設定緩衝區大小 |
| `-T <PROC>` | 設定進程數量 |
| `-j <DIR\|FILE>` | 設定報告路徑 |
| `-S <CHARACTER{:VALUE}>` | 排序鍵（c:cpu/m:mem/p:pid/N:name等） |
| `-P` | 將同一進程的執行緒分組 |
| `-i <SEC>` | 設定間隔時間（秒） |
| `-g <COMM\|TID{:FILE}>` | 設定任務過濾器 |
| `-a` | 顯示所有統計和事件 |

**啟用選項說明（-e）：**
- `a`: 親和性
- `c`: CPU
- `m`: 記憶體
- `n`: 網路
- `d`: 磁碟
- `t`: 執行緒
- `s`: 堆疊
- `b`: 阻塞
- `w`: WSS（工作集大小）
- `p`: 管道
- `i`: IRQ（中斷）
- `o`: OOM 分數
- `H`: 排程資訊

**停用選項說明（-d）：**
- `c`: CPU
- `m`: GPU 記憶體
- `O`: 顏色
- `p`: 列印
- `t`: 截斷

**使用範例：**

```bash
# 監控 CPU 使用率超過 1% 的進程
guider top

# 監控特定 TID 或進程名
guider top -g 1234
guider top -g nginx

# 每 2 秒更新一次
guider top -i 2

# 按記憶體排序
guider top -S m

# 顯示執行緒詳情
guider top -e t

# 在背景執行並輸出到檔案
guider top -u -o /tmp/top_output.txt
```

### 2. rec - 執行緒事件記錄

**功能：** 記錄系統執行緒事件

**基本語法：**
```bash
guider rec [OPTIONS]
```

**收集參數：**

| 參數 | 說明 |
|------|------|
| `-e <CHARACTER>` | 啟用選項 |
| `-d <CHARACTER>` | 停用選項 |
| `-s <DIR\|FILE>` | 儲存追蹤資料 |
| `-f` | 強制執行 |
| `-u` | 在背景執行 |
| `-W <SEC>` | 等待輸入 |
| `-b <SIZE:KB>` | 設定緩衝區大小 |
| `-D` | 追蹤任務依賴關係 |
| `-t <SYSCALL>` | 追蹤系統呼叫 |
| `-K <NAME:FUNC\|ADDR:ARGS>` | 設定核心事件 |
| `-U <NAME:FUNC\|ADDR:FILE\|COMM\|PID:RET>` | 設定使用者事件 |
| `-R <INTERVAL:TIME:TERM>` | 設定重複計數 |

**報告參數：**

| 參數 | 說明 |
|------|------|
| `-a` | 顯示所有統計和事件 |
| `-o <DIR\|FILE>` | 設定輸出路徑 |
| `-S <CHARACTER>` | 排序鍵 |
| `-P` | 將執行緒分組 |
| `-p <TID>` | 顯示搶占資訊 |
| `-O <CORE>` | 設定核心過濾器 |

**使用範例：**

```bash
# 記錄系統事件 10 秒
guider rec -R 0:10:0 -s trace.dat

# 記錄特定進程的事件
guider rec -g nginx -s nginx_trace.dat

# 啟用記憶體和網路追蹤
guider rec -e mn -s system_trace.dat

# 生成報告
guider report trace.dat -o report.txt
```

### 3. strace - 系統呼叫追蹤

**功能：** 追蹤特定執行緒的系統呼叫

**基本語法：**
```bash
guider strace -g <TID|COMM> | <COMMAND> [OPTIONS]
```

**主要參數：**

| 參數 | 說明 |
|------|------|
| `-e <CHARACTER>` | 啟用選項 |
| `-d <CHARACTER>` | 停用選項 |
| `-u` | 在背景執行 |
| `-a` | 顯示所有統計與暫存器 |
| `-g <COMM\|TID{:FILE}>` | 設定任務過濾器 |
| `-t <SYSCALL>` | 設定要追蹤的系統呼叫 |
| `-I <COMMAND>` | 設定指令 |
| `-R <TIME>` | 設定計時器 |
| `-c <EVENT>` | 設定斷點 |
| `-l` | 列印系統呼叫列表 |
| `-o <DIR\|FILE>` | 設定輸出路徑 |

**使用範例：**

```bash
# 追蹤特定進程的系統呼叫
guider strace -g nginx

# 追蹤新執行的指令
guider strace -I "ls -la"

# 只追蹤特定系統呼叫
guider strace -g 1234 -t open,read,write

# 顯示所有統計資訊
guider strace -g httpd -a
```

### 4. cputest - CPU 測試

**功能：** 創建使用 CPU 的任務進行測試

**基本語法：**
```bash
guider cputest <LOAD:NRTASK> [OPTIONS]
```

**參數說明：**
- `LOAD`: CPU 負載百分比
- `NRTASK`: 任務數量

**主要選項：**

| 參數 | 說明 |
|------|------|
| `-R <TIME>` | 設定執行時間（秒） |
| `-Y <VALUES>` | 設定排程策略 |
| `-v` | 詳細輸出 |

**使用範例：**

```bash
# 創建 10 個進程，每個使用 5% CPU
guider cputest 50:10

# 創建總共使用 250% CPU 的進程
guider cputest 250

# 執行 3 秒後自動終止
guider cputest 250 -R 3

# 使用 RR 排程策略，優先級 1
guider cputest 250 -Y r:1

# 自訂進程名稱
guider cputest 250 -q COMM:testprocess
```

### 5. ps - 進程列表

**功能：** 顯示進程列表

**基本語法：**
```bash
guider ps [OPTIONS]
```

**主要參數：**

| 參數 | 說明 |
|------|------|
| `-a` | 顯示所有進程 |
| `-t` | 顯示執行緒 |
| `-o <FORMAT>` | 自訂輸出格式 |
| `-g <COMM\|PID>` | 過濾特定進程 |

**使用範例：**

```bash
# 顯示所有進程
guider ps -a

# 顯示包含執行緒的詳細資訊
guider ps -at

# 過濾特定進程
guider ps -g nginx
```

---

## 實用範例

### 系統效能監控

```bash
# 即時監控系統整體狀態
guider atop

# 監控 CPU 使用率前 10 的進程
guider top -T 10 -S c

# 監控記憶體使用情況
guider mtop

# 監控網路流量
guider ntop

# 監控磁碟 I/O
guider disktop
```

### 效能分析與記錄

```bash
# 記錄系統 30 秒的活動
guider rec -R 0:30:0 -s performance.dat

# 分析記錄並生成報告
guider report performance.dat -o performance_report.txt

# 記錄特定應用的系統呼叫
guider strace -g myapp -o myapp_syscalls.txt

# 追蹤函數呼叫
guider funcrec -g myapp -s function_trace.dat
```

### 問題診斷

```bash
# 檢查記憶體洩漏
guider leaktrace -g myapp

# 追蹤程式崩潰
guider sigtrace -g myapp

# 檢查 CPU 瓶頸
guider top -e c -S c

# 分析 I/O 延遲
guider iorec -s io_trace.dat
```

### 視覺化分析

```bash
# 生成 CPU 使用率圖表
guider drawcpu performance.dat -o cpu_chart.png

# 生成記憶體使用圖表
guider drawmem performance.dat -o mem_chart.png

# 生成火焰圖
guider drawflame function_trace.dat -o flame_graph.svg

# 生成時間軸圖表
guider drawtime system_trace.dat -o timeline.png
```

### 壓力測試

```bash
# CPU 壓力測試（使用 400% CPU，持續 60 秒）
guider cputest 400 -R 60

# 記憶體壓力測試（分配 2GB 記憶體）
guider memtest 2048

# I/O 壓力測試
guider iotest -s 1024 -n 100

# 網路壓力測試
guider nettest -s 1000 -c 10
```

---

## 參數說明對照表

### 通用參數

| 參數 | 說明 | 適用範圍 |
|------|------|----------|
| `--help` | 顯示幫助資訊 | 所有指令 |
| `-v` | 詳細輸出模式 | 大部分指令 |
| `-o <PATH>` | 輸出路徑 | 監控、記錄類指令 |
| `-u` | 背景執行 | 監控、記錄類指令 |
| `-f` | 強制執行 | 控制類指令 |
| `-g <FILTER>` | 任務過濾器 | 監控、追蹤類指令 |
| `-a` | 顯示所有資訊 | 監控、報告類指令 |
| `-i <SEC>` | 間隔時間 | 監控類指令 |
| `-R <TIME>` | 執行時間 | 測試、記錄類指令 |

### 排序鍵對照

| 鍵值 | 排序依據 |
|------|----------|
| `c` | CPU 使用率 |
| `m` | 記憶體使用 |
| `p` | 進程 ID |
| `N` | 進程名稱 |
| `b` | 阻塞次數 |
| `w` | WFC（等待完成） |
| `n` | 新建 |
| `f` | 檔案 |
| `r` | 執行時間 |
| `s` | 交換空間 |
| `e` | 執行時間 |
| `P` | 優先級 |
| `C` | 上下文切換 |
| `o` | OOM 分數 |

### 啟用/停用選項對照

#### 監控類選項

| 選項 | 啟用功能 | 停用功能 |
|------|---------|---------|
| `a` | 親和性 | 可用記憶體 |
| `b` | 阻塞 | 緩衝區 |
| `c` | CPU | CPU |
| `d` | 磁碟 | 反編譯 |
| `e` | 編碼 | 編碼 |
| `m` | 記憶體 | GPU 記憶體 |
| `n` | 網路 | - |
| `t` | 執行緒 | 截斷 |
| `s` | 堆疊 | - |
| `p` | 管道 | 列印 |
| `O` | I/O 排程 | 顏色 |

#### 記錄類選項

| 選項 | 功能描述 |
|------|----------|
| `b` | 阻塞事件 |
| `B` | Binder（Android） |
| `c` | Cgroup |
| `d` | 磁碟 |
| `f` | 檔案系統 |
| `i` | IRQ |
| `k` | KVM |
| `L` | 鎖定 |
| `m` | 記憶體 |
| `M` | 模組 |
| `n` | 網路 |
| `P` | 電源 |
| `w` | 工作佇列 |

---

## 進階使用技巧

### 1. 組合使用多個工具

```bash
# 先記錄，再分析
guider rec -R 0:60:0 -s trace.dat
guider report trace.dat -o report.txt
guider drawcpu trace.dat -o cpu.png

# 監控並記錄
guider top -o top_output.txt &
guider rec -s system_trace.dat
```

### 2. 自動化腳本

```bash
#!/bin/bash
# 效能監控腳本

# 開始記錄
guider rec -u -R 0:300:0 -s performance.dat

# 等待記錄完成
sleep 305

# 生成報告
guider report performance.dat -o report.txt

# 生成圖表
guider drawcpu performance.dat -o cpu.png
guider drawmem performance.dat -o mem.png
guider drawio performance.dat -o io.png

echo "分析完成！"
```

### 3. 遠端監控

```bash
# 在伺服器端啟動
guider server -x 0.0.0.0:8888

# 在客戶端連接
guider cli -X monitor@192.168.1.100:8888
```

### 4. 容器監控

```bash
# 監控 Docker 容器
guider contop

# 監控特定 cgroup
guider cgtop -g /docker/container_id
```

---

## 故障排除

### 常見問題

**1. 權限不足**
```bash
# 需要 root 權限的指令加 sudo
sudo guider rec -s trace.dat
```

**2. 缺少依賴**
```bash
# 安裝必要的套件
pip install guider
```

**3. 核心模組未載入**
```bash
# 檢查並載入必要的核心模組
sudo modprobe ftrace
```

### 效能優化建議

1. **減少監控開銷**
   - 使用 `-i` 增加更新間隔
   - 使用 `-T` 限制監控的進程數
   - 使用 `-g` 只監控特定進程

2. **優化記錄大小**
   - 使用 `-b` 調整緩衝區大小
   - 使用 `-d` 停用不需要的功能
   - 使用 `-R` 限制記錄時間

3. **提高分析效率**
   - 使用過濾器減少資料量
   - 分批處理大型記錄檔
   - 使用適當的排序鍵

---

## 總結

Guider 是一個功能強大且全面的系統分析工具，提供了從基礎監控到進階分析的完整解決方案。透過本指南，您應該能夠：

1. ✅ 理解 Guider 的基本架構和指令分類
2. ✅ 掌握常用指令的參數和用法
3. ✅ 根據不同場景選擇合適的工具
4. ✅ 組合使用多個工具進行深入分析
5. ✅ 解決常見問題並優化使用效能

建議從簡單的監控指令開始，逐步學習更進階的功能。經常查看 `--help` 輸出以獲取最新的參數資訊。

---

**更新日期：** 2024年
**Guider 版本：** 3.9.9_250517
**文件版本：** 1.0