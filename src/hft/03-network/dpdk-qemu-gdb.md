# DPDK + QEMU + GDB 調試環境指南

## 環境配置

### 1. 編譯 DPDK

```bash
# 配置編譯（啟用調試符號）
meson setup build --buildtype=debug

# 編譯
ninja -C build -j$(nproc)
```

### 2. 編譯測試程序

```bash
gcc -o build/test_dpdk test_dpdk.c \
    -I./build/include \
    -I./lib/eal/include \
    -I./lib/eal/x86/include \
    -I./lib/eal/linux/include \
    -I./lib/eal/common \
    -I./lib/ethdev \
    -I./lib/net \
    -I./lib/mbuf \
    -I./lib/mempool \
    -I./lib/ring \
    -I./lib/meter \
    -I./lib/metrics \
    -I./lib/telemetry \
    -I./lib/kvargs \
    -I./lib/log \
    -I./config \
    -I./build \
    -L./build/lib \
    -Wl,--whole-archive \
    -lrte_eal -lrte_ethdev -lrte_mbuf -lrte_mempool \
    -lrte_ring -lrte_net -lrte_meter -lrte_telemetry \
    -lrte_kvargs -lrte_log \
    -Wl,--no-whole-archive \
    -lpthread -ldl -lnuma \
    -g -O0 -march=native
```

## 使用方法

### 方法 1: 本地 GDB 調試（推薦）

```bash
# 運行調試腳本
chmod +x run_dpdk_gdb.sh
./run_dpdk_gdb.sh

# 在 GDB 中運行
(gdb) run -l 0 -n 1 --no-pci --no-huge --no-shconf
```

### 方法 2: QEMU + GDB 遠程調試

#### Terminal 1 - 啟動 QEMU
```bash
chmod +x run_qemu_dpdk.sh
./run_qemu_dpdk.sh
```

#### Terminal 2 - GDB 連接
```bash
gdb build/test_dpdk

# 連接到 QEMU
(gdb) target remote :1234

# 設置斷點
(gdb) break main
(gdb) break rte_eal_init
(gdb) break port_init
(gdb) break lcore_main

# 繼續執行
(gdb) continue
```

## GDB 常用命令

### 基本調試命令
```gdb
# 斷點管理
break <function>     # 設置斷點
info breakpoints     # 查看所有斷點
delete <n>          # 刪除斷點 n
disable <n>         # 暫時禁用斷點 n
enable <n>          # 啟用斷點 n

# 執行控制
run <args>          # 運行程序
continue            # 繼續執行
step               # 單步進入函數
next               # 單步跳過函數
finish             # 執行完當前函數

# 查看信息
print <variable>    # 查看變量值
info locals        # 查看局部變量
backtrace          # 查看調用棧
frame <n>          # 切換到棧幀 n
list               # 顯示源代碼

# 內存查看
x/10x $rsp         # 查看棧指針處的內存
x/s <address>      # 查看字符串
```

### DPDK 特定調試點

```gdb
# 主要函數斷點
break main
break rte_eal_init          # EAL 初始化
break rte_pktmbuf_pool_create # 內存池創建
break rte_eth_dev_configure   # 端口配置
break rte_eth_dev_start       # 端口啟動
break rte_eth_rx_burst        # 接收數據包
break rte_eth_tx_burst        # 發送數據包
```

## 文件說明

### 核心文件
- `test_dpdk.c` - DPDK 測試程序源碼
- `build/test_dpdk` - 編譯後的可執行文件

### 腳本文件
- `run_dpdk_gdb.sh` - 本地 GDB 調試腳本
- `run_qemu_dpdk.sh` - QEMU 環境啟動腳本

## 環境要求

### 系統需求
- Ubuntu 20.04 或更高版本
- 至少 4GB RAM（QEMU 運行需要）
- 支持虛擬化的 CPU

### 軟體需求
```bash
# 必要軟體
- GCC 編譯器
- Meson/Ninja 構建系統
- QEMU 虛擬機
- GDB 調試器

# DPDK 依賴
- libnuma-dev
- libpcap-dev
- python3-pyelftools
```

### 系統配置
```bash
# 設置 Hugepages（可選）
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 加載內核模組（可選）
sudo modprobe vfio-pci
```

## 故障排除

### 問題 1: 找不到共享庫
```bash
# 解決方法：設置庫路徑
export LD_LIBRARY_PATH=/home/shihyu/github/dpdk/build/lib:$LD_LIBRARY_PATH
```

### 問題 2: 權限錯誤
```bash
# 解決方法：使用 sudo 運行
sudo ./run_dpdk_gdb.sh
```

### 問題 3: QEMU 無法啟動
```bash
# 檢查 TAP 介面
ip link show tap0

# 手動創建 TAP 介面
sudo ip link add dev tap0 type tap
sudo ip link set dev tap0 up
```

### 問題 4: GDB 無法連接到 QEMU
```bash
# 確認 QEMU 正在監聽
netstat -an | grep 1234

# 使用正確的連接命令
(gdb) target remote :1234
```

## 清理環境

```bash
# 清理編譯
cd build && ninja clean && cd ..

# 刪除 TAP 介面
sudo ip link del tap0

# 釋放 Hugepages
echo 0 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
```

## 參考資訊

- DPDK 官方文檔: https://doc.dpdk.org/
- GDB 文檔: https://www.gnu.org/software/gdb/documentation/
- QEMU 文檔: https://www.qemu.org/documentation/
