# Linux 效能檢測工具完整指南

## 目錄
- [CPU 與 Context Switch 監控](#cpu-與-context-switch-監控)
- [記憶體監控](#記憶體監控)
- [I/O 與磁碟監控](#io-與磁碟監控)
- [網路監控](#網路監控)
- [進程監控](#進程監控)
- [系統追蹤工具](#系統追蹤工具)
- [效能分析框架](#效能分析框架)
- [容器監控](#容器監控)
- [GPU 監控](#gpu-監控)
- [電源與溫度監控](#電源與溫度監控)
- [核心監控](#核心監控)
- [應用層監控](#應用層監控)
- [綜合監控套件](#綜合監控套件)
- [效能測試與基準工具](#效能測試與基準工具)
- [實用診斷腳本](#實用診斷腳本)

---

## CPU 與 Context Switch 監控

### vmstat - 虛擬記憶體統計
```bash
# 每秒更新，顯示 5 次
vmstat 1 5

# 顯示活躍和非活躍記憶體
vmstat -a 1 5

# 顯示 slab 快取資訊
vmstat -m

# 顯示磁碟統計
vmstat -d

# 重要欄位說明：
# r: 執行佇列中的進程數
# b: 阻塞的進程數
# cs: 每秒 context switches
# in: 每秒中斷數
# us: 用戶空間 CPU 使用率
# sy: 系統空間 CPU 使用率
```

### pidstat - 進程統計
```bash
# Context switch 監控
pidstat -w 1 5

# CPU 使用率
pidstat -u 1 5

# I/O 統計
pidstat -d 1 5

# 記憶體統計
pidstat -r 1 5

# 特定進程的所有統計
pidstat -p 1234 -urd 1

# 監控線程
pidstat -t -p 1234 1
```

### mpstat - 多處理器統計
```bash
# 所有 CPU 統計
mpstat -P ALL 1 5

# 特定 CPU
mpstat -P 0,1 1 5

# 顯示中斷統計
mpstat -I ALL 1 5
```

### turbostat - CPU 頻率和電源狀態
```bash
# 顯示 CPU 頻率、C-state、溫度
sudo turbostat

# 間隔 1 秒
sudo turbostat --interval 1

# 簡化輸出
sudo turbostat --quiet
```

### cpupower - CPU 電源管理
```bash
# 顯示 CPU 頻率資訊
cpupower frequency-info

# 監控 CPU 頻率
cpupower monitor

# 設定效能模式
sudo cpupower frequency-set -g performance
```

### numastat - NUMA 統計
```bash
# NUMA 記憶體統計
numastat

# 特定進程 NUMA 統計
numastat -p 1234

# 詳細模式
numastat -v
```

---

## 記憶體監控

### free - 記憶體使用
```bash
# 人類可讀格式
free -h

# 顯示總計
free -t

# 持續監控
watch -n 1 free -h

# 寬格式輸出
free -w
```

### smem - 記憶體報告工具
```bash
# 按 RSS 排序
smem -s rss -r

# 按比例排序
smem -s pss -r

# 顯示總計
smem -t

# 產生圖表
smem --pie name -s pss
```

### slabtop - Slab 快取監控
```bash
# 即時 slab 快取監控
sudo slabtop

# 排序選項
# a: 活躍對象數
# b: 每個 slab 的對象數
# c: 快取大小
```

### pmap - 進程記憶體映射
```bash
# 基本映射
pmap 1234

# 擴展格式
pmap -x 1234

# 顯示裝置格式
pmap -d 1234

# 完整詳細資訊
pmap -XX 1234
```

### vmtouch - 檔案系統快取控制
```bash
# 檢查檔案在快取中的狀態
vmtouch /path/to/file

# 將檔案載入快取
vmtouch -t /path/to/file

# 從快取移除
vmtouch -e /path/to/file
```

### pcstat - 頁面快取統計
```bash
# 檢查檔案的頁面快取狀態
pcstat /var/log/syslog

# 多個檔案
pcstat -json *.log
```

---

## I/O 與磁碟監控

### iostat - I/O 統計
```bash
# 擴展統計
iostat -x 1

# 只顯示裝置
iostat -d 1

# 顯示分區統計
iostat -p ALL 1

# NFS 統計
iostat -n 1

# 人類可讀格式
iostat -h 1
```

### iotop - I/O 使用率監控
```bash
# 基本監控
sudo iotop

# 只顯示有 I/O 的進程
sudo iotop -o

# 累積模式
sudo iotop -a

# 批次模式
sudo iotop -b -n 5 -d 1
```

### biosnoop - 區塊 I/O 追蹤
```bash
# 追蹤區塊 I/O (需要 bcc-tools)
sudo biosnoop

# 包含時間戳
sudo biosnoop -t
```

### blktrace - 區塊層追蹤
```bash
# 開始追蹤
sudo blktrace -d /dev/sda -o trace

# 停止並分析
sudo blkparse trace.* | less

# 產生報告
sudo btt -i trace.* -o report
```

### ioping - I/O 延遲測試
```bash
# 測試目錄 I/O 延遲
ioping -c 10 .

# 測試裝置
sudo ioping -c 10 /dev/sda

# 順序讀取測試
ioping -RL /dev/sda
```

### hdparm - 硬碟參數設定
```bash
# 測試讀取速度
sudo hdparm -t /dev/sda

# 測試快取讀取速度
sudo hdparm -T /dev/sda

# 顯示硬碟資訊
sudo hdparm -I /dev/sda
```

### fatrace - 檔案存取追蹤
```bash
# 監控所有檔案存取
sudo fatrace

# 特定掛載點
sudo fatrace /home

# 包含時間戳
sudo fatrace -t
```

---

## 網路監控

### ss - Socket 統計
```bash
# TCP 連線
ss -tan

# 監聽 ports
ss -tln

# 顯示進程
ss -tulpn

# 顯示計時器資訊
ss -o

# 顯示記憶體使用
ss -m

# 統計摘要
ss -s
```

### netstat - 網路統計
```bash
# 所有連線
netstat -a

# 路由表
netstat -r

# 介面統計
netstat -i

# 持續監控
netstat -c

# 群組成員
netstat -g
```

### iftop - 即時流量監控
```bash
# 基本監控
sudo iftop

# 指定介面
sudo iftop -i eth0

# 不解析 DNS
sudo iftop -n

# 顯示 port
sudo iftop -P
```

### nethogs - 按進程分組的網路流量
```bash
# 基本監控
sudo nethogs

# 指定介面
sudo nethogs eth0

# 追蹤模式
sudo nethogs -t
```

### tcpdump - 封包擷取
```bash
# 基本擷取
sudo tcpdump -i any

# 寫入檔案
sudo tcpdump -w capture.pcap

# 讀取檔案
sudo tcpdump -r capture.pcap

# 詳細輸出
sudo tcpdump -vvv

# 過濾器範例
sudo tcpdump 'tcp port 80'
sudo tcpdump 'host 192.168.1.1'
```

### nload - 網路負載監控
```bash
# 基本監控
nload

# 指定介面
nload eth0

# 設定更新間隔
nload -t 500
```

### bmon - 頻寬監控
```bash
# 互動式介面
bmon

# 指定介面
bmon -p eth0

# HTML 輸出
bmon -o html:path=/tmp/bmon.html
```

### vnstat - 網路流量統計
```bash
# 顯示統計
vnstat

# 即時監控
vnstat -l

# 每日統計
vnstat -d

# 每月統計
vnstat -m
```

### iptraf-ng - IP 流量監控
```bash
# 互動式介面
sudo iptraf-ng

# 監控所有介面
sudo iptraf-ng -i all

# 產生日誌
sudo iptraf-ng -L logfile
```

### nicstat - 網路介面統計
```bash
# 基本統計
nicstat 1

# 擴展統計
nicstat -x 1

# TCP 統計
nicstat -t 1
```

---

## 進程監控

### ps - 進程狀態
```bash
# 標準格式
ps aux

# 樹狀顯示
ps auxf
pstree -p

# 自訂欄位
ps -eo pid,tid,class,rtprio,ni,pri,psr,pcpu,pmem,comm

# 按記憶體排序
ps aux --sort=-rss

# 顯示線程
ps -eLf

# 顯示安全性內容
ps auxZ
```

### top/htop - 即時監控
```bash
# top 進階用法
top -H           # 顯示線程
top -c           # 顯示完整命令
top -p 1234,5678 # 監控特定 PID

# htop (更友善)
htop
htop -u username # 特定用戶
htop -p 1234     # 特定進程
```

### atop - 進階系統監控
```bash
# 即時監控
atop

# 記錄模式 (每 10 秒)
atop -w /var/log/atop.log 10

# 讀取記錄
atop -r /var/log/atop.log

# 特定時間
atop -r /var/log/atop.log -b 10:00
```

### glances - 跨平臺監控
```bash
# 基本監控
glances

# Web 模式
glances -w

# 匯出到 CSV
glances --export csv --export-csv-file /tmp/glances.csv

# 客戶端/伺服器模式
glances -s  # 伺服器
glances -c hostname  # 客戶端
```

### lsof - 開啟檔案列表
```bash
# 特定進程
lsof -p 1234

# 特定用戶
lsof -u username

# 網路連線
lsof -i
lsof -i :80
lsof -i TCP

# 特定檔案
lsof /var/log/syslog

# 特定目錄
lsof +D /var/log/
```

### fuser - 檔案使用者
```bash
# 查看誰在使用檔案
fuser /var/log/syslog

# 查看誰在使用 port
fuser -n tcp 80

# 終止使用檔案的進程
fuser -k /path/to/file
```

### pgrep/pkill - 進程搜尋/終止
```bash
# 搜尋進程
pgrep -l nginx
pgrep -u username

# 終止進程
pkill nginx
pkill -u username

# 傳送訊號
pkill -USR1 nginx
```

---

## 系統追蹤工具

### strace - 系統呼叫追蹤
```bash
# 追蹤進程
strace -p 1234

# 追蹤並統計
strace -c -p 1234

# 追蹤特定系統呼叫
strace -e open,read,write ls

# 追蹤網路相關
strace -e trace=network nc

# 輸出到檔案
strace -o output.txt ls

# 時間戳
strace -t ls
strace -tt ls  # 微秒
```

### ltrace - 函式庫呼叫追蹤
```bash
# 追蹤函式庫呼叫
ltrace ls

# 追蹤特定函式
ltrace -e malloc+free ls

# 統計模式
ltrace -c ls

# 追蹤系統呼叫
ltrace -S ls
```

### ftrace - 核心函式追蹤
```bash
# 啟用追蹤
echo function > /sys/kernel/debug/tracing/current_tracer

# 開始追蹤
echo 1 > /sys/kernel/debug/tracing/tracing_on

# 讀取追蹤
cat /sys/kernel/debug/tracing/trace

# 追蹤特定函式
echo do_fork > /sys/kernel/debug/tracing/set_ftrace_filter
```

### SystemTap - 動態追蹤
```bash
# 簡單範例
sudo stap -e 'probe kernel.function("do_fork") { printf("Fork!\n") }'

# Context switch 追蹤
sudo stap -e 'probe scheduler.ctxswitch { 
    printf("%s(%d) -> %s(%d)\n", 
           prev_task_name, prev_tid, 
           next_task_name, next_tid) 
}'

# 系統呼叫計數
sudo stap -e 'global syscalls; 
              probe syscall.* { syscalls[name]++ } 
              probe end { foreach(s in syscalls-) 
                          printf("%s: %d\n", s, syscalls[s]) }'
```

### eBPF/bpftrace - 進階追蹤
```bash
# Context switch 計數
sudo bpftrace -e 'tracepoint:sched:sched_switch { @[comm] = count(); }'

# 系統呼叫延遲
sudo bpftrace -e 'tracepoint:raw_syscalls:sys_enter { @start[tid] = nsecs; }
                   tracepoint:raw_syscalls:sys_exit /@start[tid]/ { 
                       @ns = hist(nsecs - @start[tid]); delete(@start[tid]); }'

# TCP 連線追蹤
sudo bpftrace -e 'tracepoint:tcp:tcp_destroy_sock { printf("%s\n", comm); }'

# 檔案開啟追蹤
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_open { printf("%s: %s\n", comm, str(args->filename)); }'
```

### BCC Tools - eBPF 工具集
```bash
# execsnoop - 追蹤新進程
sudo execsnoop

# opensnoop - 追蹤檔案開啟
sudo opensnoop

# tcpconnect - TCP 連線追蹤
sudo tcpconnect

# tcpaccept - TCP 接受追蹤
sudo tcpaccept

# biolatency - 區塊 I/O 延遲
sudo biolatency

# cachestat - 快取統計
sudo cachestat

# runqlat - CPU 執行佇列延遲
sudo runqlat

# profile - CPU 剖析
sudo profile
```

---

## 效能分析框架

### perf - Linux 效能分析
```bash
# 系統整體統計
sudo perf stat -a sleep 5

# 特定事件統計
sudo perf stat -e cycles,instructions,cache-misses ls

# Context switch 統計
sudo perf stat -e context-switches,cpu-migrations sleep 5

# 記錄效能資料
sudo perf record -a sleep 5
sudo perf report

# 即時監控
sudo perf top

# 火焰圖資料收集
sudo perf record -F 99 -a -g sleep 30
sudo perf script > out.perf

# 鎖定分析
sudo perf lock record sleep 5
sudo perf lock report

# 排程延遲分析
sudo perf sched record sleep 5
sudo perf sched latency

# 追蹤點列表
sudo perf list
```

### Flamegraph - 火焰圖
```bash
# 安裝
git clone https://github.com/brendangregg/FlameGraph

# 產生火焰圖
sudo perf record -F 99 -a -g sleep 30
sudo perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl > flame.svg

# Java 火焰圖
sudo perf record -F 99 -a -g -p `pgrep java` sleep 30
sudo perf script | ./FlameGraph/stackcollapse-perf.pl | ./FlameGraph/flamegraph.pl --color=java > java_flame.svg
```

### Intel VTune - Intel CPU 分析
```bash
# 收集資料
vtune -collect hotspots ./application

# 硬體事件
vtune -collect advanced-hotspots ./application

# 記憶體存取分析
vtune -collect memory-access ./application
```

### AMD uProf - AMD CPU 分析
```bash
# CPU 剖析
AMDuProfCLI collect --config tbp ./application

# 功耗分析
AMDuProfCLI collect --config power ./application
```

---

## 容器監控

### docker stats - Docker 統計
```bash
# 所有容器統計
docker stats

# 特定容器
docker stats container_name

# 不持續更新
docker stats --no-stream

# 格式化輸出
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

### ctop - 容器 top
```bash
# 互動式監控
ctop

# 只顯示執行中的容器
ctop -a
```

### cAdvisor - 容器顧問
```bash
# 執行 cAdvisor
docker run -d \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --publish=8080:8080 \
  --name=cadvisor \
  google/cadvisor:latest
```

### kubectl top - Kubernetes 監控
```bash
# Pod 資源使用
kubectl top pods

# Node 資源使用
kubectl top nodes

# 特定 namespace
kubectl top pods -n namespace
```

---

## GPU 監控

### nvidia-smi - NVIDIA GPU 監控
```bash
# 基本資訊
nvidia-smi

# 持續監控
nvidia-smi -l 1

# 查詢特定資訊
nvidia-smi --query-gpu=name,temperature.gpu,utilization.gpu,utilization.memory --format=csv

# 進程資訊
nvidia-smi pmon
```

### nvtop - NVIDIA GPU top
```bash
# 互動式監控
nvtop

# 指定 GPU
nvtop -g 0
```

### radeontop - AMD GPU 監控
```bash
# 基本監控
radeontop

# 指定 GPU
radeontop -b 1
```

### intel_gpu_top - Intel GPU 監控
```bash
# 需要 root 權限
sudo intel_gpu_top
```

---

## 電源與溫度監控

### powertop - 電源消耗分析
```bash
# 互動式模式
sudo powertop

# 產生 HTML 報告
sudo powertop --html=report.html

# 自動調整
sudo powertop --auto-tune
```

### sensors - 硬體感測器監控
```bash
# 顯示所有感測器
sensors

# 持續監控
watch -n 1 sensors

# JSON 輸出
sensors -j
```

### s-tui - 終端 UI 壓力測試和監控
```bash
# 基本監控
s-tui

# 包含壓力測試
s-tui -s
```

### i7z - Intel Core CPU 監控
```bash
# 即時監控
sudo i7z

# 日誌模式
sudo i7z -l
```

---

## 核心監控

### dmesg - 核心訊息
```bash
# 顯示核心訊息
dmesg

# 持續監控
dmesg -w

# 人類可讀時間戳
dmesg -T

# 只顯示錯誤
dmesg -l err

# 清除緩衝區
sudo dmesg -C
```

### sysctl - 核心參數
```bash
# 顯示所有參數
sysctl -a

# 特定參數
sysctl kernel.threads-max

# 設定參數
sudo sysctl -w kernel.threads-max=100000

# 從檔案載入
sudo sysctl -p /etc/sysctl.conf
```

### /proc 和 /sys 檔案系統
```bash
# CPU 資訊
cat /proc/cpuinfo

# 記憶體資訊
cat /proc/meminfo

# 系統負載
cat /proc/loadavg

# 中斷統計
cat /proc/interrupts

# Context switch 統計
cat /proc/stat | grep ctxt

# 特定進程資訊
cat /proc/[PID]/status
cat /proc/[PID]/stat
cat /proc/[PID]/io

# 網路統計
cat /proc/net/dev
cat /proc/net/tcp
```

### kmon - 核心模組監控
```bash
# 互動式核心活動監控
sudo kmon
```

---

## 應用層監控

### jstat - Java 統計
```bash
# GC 統計
jstat -gc PID 1000

# 類別載入統計
jstat -class PID

# JIT 編譯統計
jstat -compiler PID
```

### mysqltuner - MySQL 調校
```bash
# 分析 MySQL
mysqltuner.pl

# 遠端伺服器
mysqltuner.pl --host targethost --user admin --pass password
```

### pgbadger - PostgreSQL 日誌分析
```bash
# 分析日誌
pgbadger /var/log/postgresql/postgresql.log

# 產生 HTML 報告
pgbadger -o report.html postgresql.log
```

### apachetop - Apache 即時監控
```bash
# 監控存取日誌
apachetop /var/log/apache2/access.log

# 指定更新間隔
apachetop -d 1 /var/log/apache2/access.log
```

### ngxtop - Nginx 即時監控
```bash
# 基本監控
ngxtop

# 特定日誌
ngxtop -l /var/log/nginx/access.log

# 按狀態碼分組
ngxtop -g status
```

---

## 綜合監控套件

### sar - 系統活動報告
```bash
# CPU 使用率
sar -u 1 5

# 記憶體使用
sar -r 1 5

# I/O 統計
sar -b 1 5

# 網路統計
sar -n DEV 1 5

# Context switch
sar -w 1 5

# 執行佇列
sar -q 1 5

# 歷史資料
sar -f /var/log/sysstat/sa01
```

### dstat - 系統資源統計
```bash
# 預設輸出
dstat

# 完整輸出
dstat -a

# 包含 top CPU 和 I/O 進程
dstat -a --top-cpu --top-io

# 自訂輸出
dstat -tcmdrn

# Context switch 和中斷
dstat --sys

# 輸出到 CSV
dstat --output dstat.csv
```

### collectl - 系統收集工具
```bash
# 基本監控
collectl

# 詳細模式
collectl -scdmnst

# 記錄模式
collectl -f /var/log/collectl

# 播放記錄
collectl -p /var/log/collectl
```

### nmon - 系統監控
```bash
# 互動式模式
nmon

# 資料收集模式
nmon -f -s 10 -c 60

# 分析器
nmon_analyser nmon_output.nmon
```

### sysstat 套件
```bash
# 安裝完整套件
sudo apt-get install sysstat

# 包含工具：
# - sar
# - iostat
# - mpstat
# - pidstat
# - sadf (資料格式轉換)
```

---

## 效能測試與基準工具

### stress/stress-ng - 系統壓力測試
```bash
# CPU 壓力
stress --cpu 4 --timeout 60s

# 記憶體壓力
stress --vm 2 --vm-bytes 1G --timeout 60s

# I/O 壓力
stress --io 4 --timeout 60s

# stress-ng 進階功能
stress-ng --cpu 4 --cpu-method matrixprod --metrics --timeout 60s

# 所有壓力測試
stress-ng --all 1 --timeout 60s
```

### sysbench - 系統基準測試
```bash
# CPU 測試
sysbench cpu --threads=4 run

# 記憶體測試
sysbench memory --memory-total-size=10G run

# 檔案 I/O 測試
sysbench fileio --file-test-mode=seqwr prepare
sysbench fileio --file-test-mode=seqwr run
sysbench fileio cleanup

# MySQL 測試
sysbench oltp_read_write --mysql-host=localhost --mysql-user=root prepare
sysbench oltp_read_write --mysql-host=localhost --mysql-user=root run
```

### fio - 彈性 I/O 測試
```bash
# 順序讀取測試
fio --name=seqread --rw=read --size=1G --numjobs=1

# 隨機寫入測試
fio --name=randwrite --rw=randwrite --size=1G --numjobs=4

# 混合讀寫測試
fio --name=randrw --rw=randrw --size=1G --rwmixread=70
```

### iperf3 - 網路效能測試
```bash
# 伺服器模式
iperf3 -s

# 客戶端測試
iperf3 -c server_ip

# UDP 測試
iperf3 -c server_ip -u

# 反向測試
iperf3 -c server_ip -R
```

### phoronix-test-suite - 綜合測試套件
```bash
# 列出可用測試
phoronix-test-suite list-available-tests

# 執行測試
phoronix-test-suite run pts/compress-7zip

# 批次測試
phoronix-test-suite batch-benchmark pts/cpu
```

### unixbench - Unix 基準測試
```bash
# 執行完整測試
./Run

# 特定測試
./Run dhry2 whetstone
```

---

## 實用診斷腳本

### 快速系統健康檢查
```bash
#!/bin/bash
# system_health.sh

echo "===== System Health Check ====="
echo ""
echo "=== CPU Usage ==="
mpstat 1 2 | tail -n 1

echo ""
echo "=== Memory Usage ==="
free -h

echo ""
echo "=== Disk Usage ==="
df -h | grep -E '^/dev/'

echo ""
echo "=== Load Average ==="
uptime

echo ""
echo "=== Context Switches ==="
vmstat 1 2 | tail -n 1 | awk '{print "CS/sec: "$12}'

echo ""
echo "=== Top 5 CPU Processes ==="
ps aux --sort=-%cpu | head -6

echo ""
echo "=== Top 5 Memory Processes ==="
ps aux --sort=-%mem | head -6
```

### Context Switch 監控腳本
```bash
#!/bin/bash
# context_switch_monitor.sh

INTERVAL=1
COUNT=10

echo "Monitoring context switches for $COUNT seconds..."
echo "Time          | Total CS | CS/sec | Vol CS | Invol CS"
echo "--------------------------------------------------------"

PREV_CS=$(cat /proc/stat | grep ctxt | awk '{print $2}')
PREV_TIME=$(date +%s)

for i in $(seq 1 $COUNT); do
    sleep $INTERVAL
    
    CURR_CS=$(cat /proc/stat | grep ctxt | awk '{print $2}')
    CURR_TIME=$(date +%s)
    
    CS_DIFF=$((CURR_CS - PREV_CS))
    TIME_DIFF=$((CURR_TIME - PREV_TIME))
    CS_PER_SEC=$((CS_DIFF / TIME_DIFF))
    
    # Get voluntary and involuntary context switches for init process (PID 1)
    VOL_CS=$(cat /proc/1/status | grep voluntary_ctxt | awk '{print $2}')
    INVOL_CS=$(cat /proc/1/status | grep nonvoluntary_ctxt | awk '{print $2}')
    
    echo "$(date +%T) | $CURR_CS | $CS_PER_SEC | $VOL_CS | $INVOL_CS"
    
    PREV_CS=$CURR_CS
    PREV_TIME=$CURR_TIME
done
```

### 效能瓶頸診斷腳本
```bash
#!/bin/bash
# bottleneck_finder.sh

echo "===== Performance Bottleneck Analysis ====="
echo ""

# CPU Check
echo "=== CPU Analysis ==="
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
echo "CPU Usage: $CPU_USAGE%"

if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "⚠️  High CPU usage detected!"
    echo "Top CPU consumers:"
    ps aux --sort=-%cpu | head -4
fi

echo ""

# Memory Check
echo "=== Memory Analysis ==="
MEM_USAGE=$(free | grep Mem | awk '{print ($3/$2) * 100.0}')
echo "Memory Usage: ${MEM_USAGE}%"

if (( $(echo "$MEM_USAGE > 90" | bc -l) )); then
    echo "⚠️  High memory usage detected!"
    echo "Top memory consumers:"
    ps aux --sort=-%mem | head -4
fi

echo ""

# I/O Check
echo "=== I/O Analysis ==="
iostat -x 1 2 | grep -A1 avg-cpu | tail -n 1

IOWAIT=$(iostat -x 1 2 | grep -A1 avg-cpu | tail -n 1 | awk '{print $4}')
if (( $(echo "$IOWAIT > 30" | bc -l) )); then
    echo "⚠️  High I/O wait detected!"
    echo "Processes with high I/O:"
    iotop -b -n 1 | head -10
fi

echo ""

# Network Check
echo "=== Network Analysis ==="
for INTERFACE in $(ls /sys/class/net/ | grep -v lo); do
    RX=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
    TX=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)
    sleep 1
    RX2=$(cat /sys/class/net/$INTERFACE/statistics/rx_bytes)
    TX2=$(cat /sys/class/net/$INTERFACE/statistics/tx_bytes)
    
    RX_RATE=$((($RX2 - $RX) / 1024))
    TX_RATE=$((($TX2 - $TX) / 1024))
    
    echo "$INTERFACE: RX: ${RX_RATE}KB/s TX: ${TX_RATE}KB/s"
done
```

### 進程追蹤腳本
```bash
#!/bin/bash
# process_tracker.sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 <process_name or PID>"
    exit 1
fi

PROCESS=$1

# Check if input is PID or process name
if [[ $PROCESS =~ ^[0-9]+$ ]]; then
    PID=$PROCESS
else
    PID=$(pgrep -f $PROCESS | head -1)
    if [ -z "$PID" ]; then
        echo "Process not found!"
        exit 1
    fi
fi

echo "Tracking PID: $PID"
echo "======================================"

while true; do
    if ! kill -0 $PID 2>/dev/null; then
        echo "Process terminated!"
        break
    fi
    
    clear
    echo "=== Process Information for PID $PID ==="
    echo "Time: $(date +%T)"
    echo ""
    
    # Basic info
    ps -p $PID -o pid,ppid,user,%cpu,%mem,vsz,rss,comm
    
    echo ""
    echo "=== Resource Usage ==="
    cat /proc/$PID/status | grep -E "VmSize|VmRSS|Threads|voluntary_ctxt|nonvoluntary_ctxt"
    
    echo ""
    echo "=== I/O Statistics ==="
    cat /proc/$PID/io 2>/dev/null || echo "I/O stats not available"
    
    echo ""
    echo "=== Open Files ==="
    lsof -p $PID 2>/dev/null | wc -l | xargs echo "Total open files:"
    
    echo ""
    echo "=== Network Connections ==="
    ss -tunap | grep "pid=$PID" | wc -l | xargs echo "Total connections:"
    
    sleep 2
done
```

### 系統報告產生器
```bash
#!/bin/bash
# system_report.sh

REPORT_FILE="system_report_$(date +%Y%m%d_%H%M%S).txt"

{
    echo "System Performance Report"
    echo "Generated: $(date)"
    echo "Hostname: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo ""
    
    echo "===== Hardware Information ====="
    echo "CPU: $(lscpu | grep 'Model name' | cut -d':' -f2 | xargs)"
    echo "Cores: $(nproc)"
    echo "Memory: $(free -h | grep Mem | awk '{print $2}')"
    echo ""
    
    echo "===== Resource Usage ====="
    echo "--- CPU ---"
    mpstat | tail -2
    echo ""
    
    echo "--- Memory ---"
    free -h
    echo ""
    
    echo "--- Disk ---"
    df -h
    echo ""
    
    echo "===== Top Processes ====="
    echo "--- By CPU ---"
    ps aux --sort=-%cpu | head -10
    echo ""
    
    echo "--- By Memory ---"
    ps aux --sort=-%mem | head -10
    echo ""
    
    echo "===== Network Statistics ====="
    ss -s
    echo ""
    
    echo "===== System Load ====="
    uptime
    echo ""
    sar -q | tail -5
    echo ""
    
    echo "===== Recent System Messages ====="
    dmesg | tail -20
    
} > "$REPORT_FILE"

echo "Report saved to: $REPORT_FILE"
```

---

## 快速參考命令組合

### 找出最消耗資源的進程
```bash
# CPU 消耗最高的進程
ps aux --sort=-%cpu | head -10

# 記憶體消耗最高的進程
ps aux --sort=-%mem | head -10

# I/O 消耗最高的進程
iotop -b -n 1 | head -10

# 網路流量最高的進程
nethogs -t -c 2
```

### Context Switch 分析
```bash
# 系統總 context switch
vmstat 1 5 | awk '{print $12}'

# 每個 CPU 的 context switch
mpstat -P ALL 1 5

# 進程的 context switch
pidstat -w 1 5

# 高 context switch 進程
pidstat -w 1 1 | sort -k4 -rn | head
```

### 即時監控儀錶板
```bash
# 使用 tmux 分割畫面
tmux new-session \; \
  split-window -h \; \
  split-window -v \; \
  split-window -v \; \
  send-keys 'htop' C-m \; \
  select-pane -t 0 \; \
  send-keys 'iostat -x 1' C-m \; \
  select-pane -t 2 \; \
  send-keys 'iftop' C-m \; \
  select-pane -t 3 \; \
  send-keys 'vmstat 1' C-m
```

### 效能基準測試套件
```bash
# 快速 CPU 測試
sysbench cpu --threads=$(nproc) --time=10 run

# 快速記憶體測試
sysbench memory --memory-total-size=1G run

# 快速磁碟測試
dd if=/dev/zero of=testfile bs=1G count=1 oflag=direct

# 快速網路測試
iperf3 -c iperf.he.net -t 10
```

---

## 工具安裝指南

### Ubuntu/Debian
```bash
# 基礎工具
sudo apt-get update
sudo apt-get install -y sysstat htop iotop iftop nethogs dstat

# 進階工具
sudo apt-get install -y perf-tools-unstable linux-tools-common linux-tools-generic
sudo apt-get install -y bpfcc-tools systemtap

# 效能測試工具
sudo apt-get install -y stress-ng sysbench fio iperf3
```

### RHEL/CentOS/Fedora
```bash
# 基礎工具
sudo yum install -y sysstat htop iotop iftop nethogs dstat

# 進階工具
sudo yum install -y perf systemtap bcc-tools

# 效能測試工具
sudo yum install -y stress-ng sysbench fio iperf3
```

### Arch Linux
```bash
# 基礎工具
sudo pacman -S sysstat htop iotop iftop nethogs dstat

# 進階工具
sudo pacman -S perf bpf bcc-tools

# 效能測試工具
sudo pacman -S stress-ng sysbench fio iperf3
```

---

## 最佳實踐建議

1. **建立基準線**: 在系統正常運作時收集效能數據作為基準
2. **定期監控**: 設定自動化監控和警報系統
3. **多工具驗證**: 使用多個工具交叉驗證問題
4. **保存歷史數據**: 使用 sar、atop 等工具保存歷史數據供分析
5. **關注趨勢**: 不只看絕對值，更要關注變化趨勢
6. **瞭解工作負載**: 不同應用有不同的效能特徵
7. **測試環境**: 在測試環境先驗證效能優化措施
8. **文件記錄**: 記錄所有效能問題和解決方案

---

## 參考資源

- [Brendan Gregg's Performance Tools](http://www.brendangregg.com/linuxperf.html)
- [Linux Performance Documentation](https://www.kernel.org/doc/html/latest/admin-guide/perf/)
- [BPF Performance Tools Book](http://www.brendangregg.com/bpf-performance-tools-book.html)
- [Systems Performance Book](http://www.brendangregg.com/systems-performance-2nd-edition-book.html)
- [Linux System Programming](https://www.oreilly.com/library/view/linux-system-programming/9781449339531/)