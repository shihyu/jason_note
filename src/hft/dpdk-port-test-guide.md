# DPDK 20 雙埠收發測試完整指南 - Ubuntu

## 目錄
1. [環境需求](#環境需求)
2. [DPDK 安裝](#dpdk-安裝)
3. [系統配置](#系統配置)
4. [測試程式實作](#測試程式實作)
5. [執行測試](#執行測試)
6. [效能監控](#效能監控)
7. [常見問題](#常見問題)

---

## 環境需求

### 硬體需求
- **CPU**: 支援 SSE4.2 的 x86_64 處理器（建議 4 核心以上）
- **記憶體**: 最少 4GB（建議 8GB 以上）
- **網卡**: 
  - 2 個 DPDK 支援的網路埠（可以是雙埠網卡或兩張單埠網卡）
  - 支援的網卡：Intel 82599/X520/X710/E810, Mellanox ConnectX-3/4/5/6
  - 虛擬環境：virtio-net, vmxnet3

### 軟體需求
- **Ubuntu**: 20.04 LTS 或 22.04 LTS
- **核心**: 4.15 以上
- **編譯器**: GCC 7.5+ 或 Clang 6.0+

### 檢查系統
```bash
# 檢查 CPU 支援
grep -m1 sse4_2 /proc/cpuinfo

# 檢查網卡
lspci | grep -i ethernet

# 檢查核心版本
uname -r
```

---

## DPDK 安裝

### 方法一：從套件管理器安裝（簡單但版本較舊）
```bash
# Ubuntu 20.04/22.04
sudo apt update
sudo apt install dpdk dpdk-dev dpdk-doc libdpdk-dev
```

### 方法二：從原始碼編譯（推薦，最新版本）

#### 1. 安裝依賴
```bash
sudo apt update
sudo apt install -y build-essential libnuma-dev python3-pip \
    python3-pyelftools python3-setuptools meson ninja-build \
    pkg-config libarchive-dev libelf-dev libpcap-dev

# Python 依賴
pip3 install meson ninja pyelftools
```

#### 2. 下載 DPDK 20.11 LTS
```bash
cd /tmp
wget https://fast.dpdk.org/rel/dpdk-20.11.9.tar.xz
tar xf dpdk-20.11.9.tar.xz
cd dpdk-stable-20.11.9
```

#### 3. 編譯安裝
```bash
# 設定編譯選項
meson build
cd build

# 配置選項（可選）
meson configure -Dexamples=all
meson configure -Ddisable_drivers=regex/octeontx2

# 編譯
ninja

# 安裝
sudo ninja install
sudo ldconfig

# 驗證安裝
pkg-config --modversion libdpdk
```

---

## 系統配置

### 1. 設定大頁記憶體（Hugepages）
```bash
# 檢查當前設定
grep -i huge /proc/meminfo

# 設定 2MB 大頁（推薦用於測試）
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 或設定 1GB 大頁（更好的效能）
echo 4 | sudo tee /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# 掛載 hugetlbfs
sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge

# 永久設定（加入 /etc/fstab）
echo "nodev /mnt/huge hugetlbfs defaults 0 0" | sudo tee -antml /etc/fstab

# 永久設定大頁數量（/etc/sysctl.conf）
echo "vm.nr_hugepages = 1024" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

### 2. 載入核心模組
```bash
# 載入 UIO 模組
sudo modprobe uio
sudo modprobe uio_pci_generic

# 或使用 VFIO（更安全，推薦）
sudo modprobe vfio-pci
sudo chmod a+x /dev/vfio
sudo chmod 0666 /dev/vfio/*

# 自動載入（永久）
echo "uio" | sudo tee -a /etc/modules
echo "uio_pci_generic" | sudo tee -a /etc/modules
# 或
echo "vfio-pci" | sudo tee -a /etc/modules
```

### 3. 綁定網卡到 DPDK

```bash
# 查看網卡狀態
sudo dpdk-devbind.py --status

# 範例輸出：
# Network devices using kernel driver
# ====================================
# 0000:02:00.0 '82599ES 10-Gigabit' if=eth0 drv=ixgbe unused=vfio-pci
# 0000:02:00.1 '82599ES 10-Gigabit' if=eth1 drv=ixgbe unused=vfio-pci

# 綁定網卡（請替換為您的 PCI 地址）
sudo ifconfig eth0 down
sudo ifconfig eth1 down

# 使用 vfio-pci（推薦）
sudo dpdk-devbind.py -b vfio-pci 0000:02:00.0 0000:02:00.1

# 或使用 uio_pci_generic
sudo dpdk-devbind.py -b uio_pci_generic 0000:02:00.0 0000:02:00.1

# 確認綁定
sudo dpdk-devbind.py --status
```

### 4. 設定 CPU 隔離（可選但推薦）
```bash
# 編輯 /etc/default/grub
# 加入 isolcpus=2,3,4,5 到 GRUB_CMDLINE_LINUX_DEFAULT
sudo nano /etc/default/grub

# 更新 grub
sudo update-grub
sudo reboot
```

---

## 測試程式實作

### 1. 基本轉發測試程式 (l2fwd_test.c)

```c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <errno.h>
#include <signal.h>

#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_cycles.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>
#include <rte_ether.h>
#include <rte_ip.h>
#include <rte_udp.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

static volatile bool force_quit = false;

/* 統計資訊 */
struct port_statistics {
    uint64_t tx;
    uint64_t rx;
    uint64_t dropped;
} __rte_cache_aligned;

static struct port_statistics port_stats[2];

/* 乙太網埠配置 */
static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .max_rx_pkt_len = RTE_ETHER_MAX_LEN,
    },
};

/* 初始化埠 */
static inline int
port_init(uint16_t port, struct rte_mempool *mbuf_pool)
{
    struct rte_eth_conf port_conf = port_conf_default;
    const uint16_t rx_rings = 1, tx_rings = 1;
    uint16_t nb_rxd = RX_RING_SIZE;
    uint16_t nb_txd = TX_RING_SIZE;
    int retval;
    struct rte_eth_dev_info dev_info;
    struct rte_eth_txconf txconf;

    if (!rte_eth_dev_is_valid_port(port))
        return -1;

    /* 獲取設備資訊 */
    retval = rte_eth_dev_info_get(port, &dev_info);
    if (retval != 0) {
        printf("Error during getting device (port %u) info: %s\n",
                port, strerror(-retval));
        return retval;
    }

    if (dev_info.tx_offload_capa & DEV_TX_OFFLOAD_MBUF_FAST_FREE)
        port_conf.txmode.offloads |= DEV_TX_OFFLOAD_MBUF_FAST_FREE;

    /* 配置設備 */
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0)
        return retval;

    retval = rte_eth_dev_adjust_nb_rx_tx_desc(port, &nb_rxd, &nb_txd);
    if (retval != 0)
        return retval;

    /* 配置 RX 佇列 */
    for (uint16_t q = 0; q < rx_rings; q++) {
        retval = rte_eth_rx_queue_setup(port, q, nb_rxd,
                rte_eth_dev_socket_id(port), NULL, mbuf_pool);
        if (retval < 0)
            return retval;
    }

    txconf = dev_info.default_txconf;
    txconf.offloads = port_conf.txmode.offloads;

    /* 配置 TX 佇列 */
    for (uint16_t q = 0; q < tx_rings; q++) {
        retval = rte_eth_tx_queue_setup(port, q, nb_txd,
                rte_eth_dev_socket_id(port), &txconf);
        if (retval < 0)
            return retval;
    }

    /* 啟動設備 */
    retval = rte_eth_dev_start(port);
    if (retval < 0)
        return retval;

    /* 顯示埠 MAC 地址 */
    struct rte_ether_addr addr;
    retval = rte_eth_macaddr_get(port, &addr);
    if (retval != 0)
        return retval;

    printf("Port %u MAC: %02" PRIx8 ":%02" PRIx8 ":%02" PRIx8
           ":%02" PRIx8 ":%02" PRIx8 ":%02" PRIx8 "\n",
            port,
            addr.addr_bytes[0], addr.addr_bytes[1],
            addr.addr_bytes[2], addr.addr_bytes[3],
            addr.addr_bytes[4], addr.addr_bytes[5]);

    /* 啟用混雜模式 */
    retval = rte_eth_promiscuous_enable(port);
    if (retval != 0)
        return retval;

    return 0;
}

/* 主要處理迴圈 */
static void
l2fwd_main_loop(void)
{
    struct rte_mbuf *pkts_burst[BURST_SIZE];
    uint16_t port;
    uint16_t nb_rx, nb_tx;

    printf("\nCore %u forwarding packets. [Ctrl+C to quit]\n",
            rte_lcore_id());

    /* 主迴圈 */
    while (!force_quit) {
        /* 從埠 0 接收，轉發到埠 1 */
        nb_rx = rte_eth_rx_burst(0, 0, pkts_burst, BURST_SIZE);
        if (nb_rx > 0) {
            port_stats[0].rx += nb_rx;
            
            nb_tx = rte_eth_tx_burst(1, 0, pkts_burst, nb_rx);
            port_stats[1].tx += nb_tx;
            
            /* 釋放未傳送的封包 */
            if (unlikely(nb_tx < nb_rx)) {
                port_stats[1].dropped += (nb_rx - nb_tx);
                for (uint16_t buf = nb_tx; buf < nb_rx; buf++)
                    rte_pktmbuf_free(pkts_burst[buf]);
            }
        }

        /* 從埠 1 接收，轉發到埠 0 */
        nb_rx = rte_eth_rx_burst(1, 0, pkts_burst, BURST_SIZE);
        if (nb_rx > 0) {
            port_stats[1].rx += nb_rx;
            
            nb_tx = rte_eth_tx_burst(0, 0, pkts_burst, nb_rx);
            port_stats[0].tx += nb_tx;
            
            /* 釋放未傳送的封包 */
            if (unlikely(nb_tx < nb_rx)) {
                port_stats[0].dropped += (nb_rx - nb_tx);
                for (uint16_t buf = nb_tx; buf < nb_rx; buf++)
                    rte_pktmbuf_free(pkts_burst[buf]);
            }
        }
    }
}

/* 顯示統計資訊 */
static void
print_stats(void)
{
    uint64_t total_packets_dropped, total_packets_tx, total_packets_rx;
    
    total_packets_dropped = port_stats[0].dropped + port_stats[1].dropped;
    total_packets_tx = port_stats[0].tx + port_stats[1].tx;
    total_packets_rx = port_stats[0].rx + port_stats[1].rx;

    printf("\n====== Port Statistics ======\n");
    printf("Port 0: RX: %"PRIu64" TX: %"PRIu64" Dropped: %"PRIu64"\n",
            port_stats[0].rx, port_stats[0].tx, port_stats[0].dropped);
    printf("Port 1: RX: %"PRIu64" TX: %"PRIu64" Dropped: %"PRIu64"\n",
            port_stats[1].rx, port_stats[1].tx, port_stats[1].dropped);
    printf("Total: RX: %"PRIu64" TX: %"PRIu64" Dropped: %"PRIu64"\n",
            total_packets_rx, total_packets_tx, total_packets_dropped);
    printf("============================\n");
}

/* 信號處理 */
static void
signal_handler(int signum)
{
    if (signum == SIGINT || signum == SIGTERM) {
        printf("\n\nSignal %d received, preparing to exit...\n", signum);
        force_quit = true;
    }
}

int
main(int argc, char *argv[])
{
    struct rte_mempool *mbuf_pool;
    uint16_t portid;
    int ret;

    /* 初始化 EAL */
    ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");

    argc -= ret;
    argv += ret;

    /* 檢查是否有兩個埠可用 */
    if (rte_eth_dev_count_avail() < 2)
        rte_exit(EXIT_FAILURE, "Error: need at least 2 ports\n");

    /* 建立 mbuf 池 */
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE,
        rte_socket_id());

    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    /* 初始化所有埠 */
    RTE_ETH_FOREACH_DEV(portid) {
        if (portid >= 2)
            break;
        if (port_init(portid, mbuf_pool) != 0)
            rte_exit(EXIT_FAILURE, "Cannot init port %"PRIu16 "\n", portid);
    }

    /* 註冊信號處理 */
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    /* 執行主迴圈 */
    l2fwd_main_loop();

    /* 顯示最終統計 */
    print_stats();

    /* 清理 */
    RTE_ETH_FOREACH_DEV(portid) {
        if (portid >= 2)
            break;
        printf("Closing port %"PRIu16"...\n", portid);
        rte_eth_dev_stop(portid);
        rte_eth_dev_close(portid);
    }

    printf("Bye...\n");

    return 0;
}
```

### 2. Makefile

```makefile
# SPDX-License-Identifier: BSD-3-Clause

# binary name
APP = l2fwd_test

# all source are stored in SRCS-y
SRCS-y := l2fwd_test.c

# Build using pkg-config variables if possible
ifeq ($(shell pkg-config --exists libdpdk && echo 0),0)

all: shared
.PHONY: shared static
shared: build/$(APP)-shared
	ln -sf $(APP)-shared build/$(APP)
static: build/$(APP)-static
	ln -sf $(APP)-static build/$(APP)

PKGCONF ?= pkg-config

PC_FILE := $(shell $(PKGCONF) --path libdpdk 2>/dev/null)
CFLAGS += -O3 $(shell $(PKGCONF) --cflags libdpdk)
LDFLAGS_SHARED = $(shell $(PKGCONF) --libs libdpdk)
LDFLAGS_STATIC = $(shell $(PKGCONF) --static --libs libdpdk)

build/$(APP)-shared: $(SRCS-y) Makefile $(PC_FILE) | build
	$(CC) $(CFLAGS) $(SRCS-y) -o $@ $(LDFLAGS) $(LDFLAGS_SHARED)

build/$(APP)-static: $(SRCS-y) Makefile $(PC_FILE) | build
	$(CC) $(CFLAGS) $(SRCS-y) -o $@ $(LDFLAGS) $(LDFLAGS_STATIC)

build:
	@mkdir -p $@

.PHONY: clean
clean:
	rm -f build/$(APP) build/$(APP)-static build/$(APP)-shared
	test -d build && rmdir -p build || true

else # Build using legacy build system

ifeq ($(RTE_SDK),)
$(error "Please define RTE_SDK environment variable")
endif

# Default target, detect a build directory, by looking for a path with a .config
RTE_TARGET ?= $(notdir $(abspath $(dir $(firstword $(wildcard $(RTE_SDK)/*/.config)))))

include $(RTE_SDK)/mk/rte.vars.mk

CFLAGS += -O3
CFLAGS += $(WERROR_FLAGS)

include $(RTE_SDK)/mk/rte.extapp.mk
endif
```

### 3. 進階測試程式（含封包產生器）

```c
/* packet_generator.c - 封包產生與測試 */
#include <rte_cycles.h>

/* 產生測試封包 */
static struct rte_mbuf *
create_test_packet(struct rte_mempool *pool, uint16_t pkt_size)
{
    struct rte_mbuf *pkt;
    struct rte_ether_hdr *eth_hdr;
    struct rte_ipv4_hdr *ip_hdr;
    struct rte_udp_hdr *udp_hdr;
    uint8_t *payload;
    
    pkt = rte_pktmbuf_alloc(pool);
    if (pkt == NULL)
        return NULL;
    
    /* 乙太網標頭 */
    eth_hdr = rte_pktmbuf_mtod(pkt, struct rte_ether_hdr *);
    rte_eth_random_addr(eth_hdr->s_addr.addr_bytes);
    rte_eth_random_addr(eth_hdr->d_addr.addr_bytes);
    eth_hdr->ether_type = rte_cpu_to_be_16(RTE_ETHER_TYPE_IPV4);
    
    /* IP 標頭 */
    ip_hdr = (struct rte_ipv4_hdr *)(eth_hdr + 1);
    memset(ip_hdr, 0, sizeof(*ip_hdr));
    ip_hdr->version_ihl = 0x45;
    ip_hdr->type_of_service = 0;
    ip_hdr->total_length = rte_cpu_to_be_16(pkt_size - sizeof(*eth_hdr));
    ip_hdr->packet_id = 0;
    ip_hdr->fragment_offset = 0;
    ip_hdr->time_to_live = 64;
    ip_hdr->next_proto_id = IPPROTO_UDP;
    ip_hdr->src_addr = rte_cpu_to_be_32(0x0A000001); // 10.0.0.1
    ip_hdr->dst_addr = rte_cpu_to_be_32(0x0A000002); // 10.0.0.2
    
    /* UDP 標頭 */
    udp_hdr = (struct rte_udp_hdr *)(ip_hdr + 1);
    udp_hdr->src_port = rte_cpu_to_be_16(1234);
    udp_hdr->dst_port = rte_cpu_to_be_16(5678);
    udp_hdr->dgram_len = rte_cpu_to_be_16(pkt_size - sizeof(*eth_hdr) - sizeof(*ip_hdr));
    
    /* 填充資料 */
    payload = (uint8_t *)(udp_hdr + 1);
    for (int i = 0; i < pkt_size - sizeof(*eth_hdr) - sizeof(*ip_hdr) - sizeof(*udp_hdr); i++) {
        payload[i] = i & 0xFF;
    }
    
    pkt->data_len = pkt_size;
    pkt->pkt_len = pkt_size;
    
    return pkt;
}

/* 效能測試函數 */
static void
run_performance_test(uint16_t port_id, struct rte_mempool *pool)
{
    struct rte_mbuf *pkts[BURST_SIZE];
    uint64_t start_cycles, end_cycles;
    uint64_t total_packets = 0;
    double duration;
    
    printf("\nStarting performance test on port %u...\n", port_id);
    
    /* 準備測試封包 */
    for (int i = 0; i < BURST_SIZE; i++) {
        pkts[i] = create_test_packet(pool, 64); // 64 位元組封包
        if (pkts[i] == NULL) {
            printf("Failed to create packet %d\n", i);
            return;
        }
    }
    
    /* 開始測試 */
    start_cycles = rte_get_timer_cycles();
    
    /* 傳送 1 百萬個封包 */
    for (int i = 0; i < 1000000 / BURST_SIZE; i++) {
        uint16_t nb_tx = rte_eth_tx_burst(port_id, 0, pkts, BURST_SIZE);
        total_packets += nb_tx;
        
        /* 重新分配未傳送的封包 */
        for (uint16_t j = nb_tx; j < BURST_SIZE; j++) {
            rte_pktmbuf_free(pkts[j]);
            pkts[j] = create_test_packet(pool, 64);
        }
    }
    
    end_cycles = rte_get_timer_cycles();
    
    /* 計算結果 */
    duration = (double)(end_cycles - start_cycles) / rte_get_timer_hz();
    printf("Sent %lu packets in %.2f seconds\n", total_packets, duration);
    printf("Rate: %.2f Mpps\n", total_packets / duration / 1000000);
    printf("Throughput: %.2f Gbps\n", total_packets * 64 * 8 / duration / 1000000000);
    
    /* 清理 */
    for (int i = 0; i < BURST_SIZE; i++) {
        if (pkts[i] != NULL)
            rte_pktmbuf_free(pkts[i]);
    }
}
```

---

## 執行測試

### 1. 編譯程式
```bash
# 使用 pkg-config
make

# 或指定 DPDK 路徑
make RTE_SDK=/usr/local/share/dpdk RTE_TARGET=x86_64-native-linux-gcc
```

### 2. 執行基本轉發測試
```bash
# 基本執行
sudo ./build/l2fwd_test

# 指定核心和記憶體
sudo ./build/l2fwd_test -l 0-3 -n 4

# 使用特定核心進行轉發
sudo ./build/l2fwd_test -l 0,2 -n 4 -- -p 0x3

# 啟用除錯訊息
sudo ./build/l2fwd_test --log-level=8
```

### 3. 使用 testpmd（DPDK 內建測試工具）
```bash
# 基本轉發模式
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --portmask=0x3 --nb-cores=2

# 在 testpmd 提示符下
testpmd> set fwd mac  # MAC 轉發模式
testpmd> start

# 其他轉發模式
testpmd> set fwd io      # I/O 模式
testpmd> set fwd rxonly  # 只接收
testpmd> set fwd txonly  # 只傳送
testpmd> set fwd csum    # Checksum 轉發

# 顯示統計
testpmd> show port stats all
testpmd> show fwd stats all

# 停止測試
testpmd> stop
testpmd> quit
```

### 4. 產生測試流量

#### 使用 pktgen-dpdk
```bash
# 安裝 pktgen
git clone https://github.com/pktgen/Pktgen-DPDK.git
cd Pktgen-DPDK
make

# 執行 pktgen
sudo ./app/x86_64-native-linux-gcc/pktgen -l 0-3 -n 4 -- \
    -P -m "[1:2].0, [3:4].1"

# pktgen 命令
Pktgen> set 0 count 1000000
Pktgen> set 0 size 64
Pktgen> set 0 rate 100
Pktgen> start 0
```

#### 使用 MoonGen（高精度流量產生器）
```bash
# 安裝 MoonGen
git clone https://github.com/emmericp/MoonGen
cd MoonGen
./build.sh

# 執行測試
sudo ./moongen examples/l2-load-latency.lua 0 1
```

---

## 效能監控

### 1. 即時監控腳本
```bash
#!/bin/bash
# dpdk_monitor.sh

while true; do
    clear
    echo "===== DPDK Port Statistics ====="
    
    # 顯示埠資訊
    for port in 0 1; do
        echo "Port $port:"
        cat /sys/class/net/dpdk_port_$port/statistics/rx_packets 2>/dev/null || echo "N/A"
        cat /sys/class/net/dpdk_port_$port/statistics/tx_packets 2>/dev/null || echo "N/A"
    done
    
    # CPU 使用率
    echo -e "\n===== CPU Usage ====="
    mpstat -P ALL 1 1 | tail -n +4
    
    # 記憶體使用
    echo -e "\n===== Memory Usage ====="
    free -h | grep -E "Mem|Huge"
    
    # 中斷統計
    echo -e "\n===== Interrupts ====="
    grep -E "eth|dpdk" /proc/interrupts | head -5
    
    sleep 2
done
```

### 2. 效能分析
```bash
# 使用 perf 分析
sudo perf record -g ./build/l2fwd_test
sudo perf report

# 檢查 CPU 快取未命中
sudo perf stat -e cache-misses,cache-references ./build/l2fwd_test

# 追蹤系統呼叫
sudo strace -c ./build/l2fwd_test
```

### 3. 調優建議
```bash
# CPU 頻率調節
sudo cpupower frequency-set -g performance

# 關閉 CPU C-states
sudo cpupower idle-set -d 2
sudo cpupower idle-set -d 3

# NUMA 優化
numactl --cpunodebind=0 --membind=0 ./build/l2fwd_test

# 網卡中斷親和性
sudo sh -c 'echo 2 > /proc/irq/24/smp_affinity'
```

---

## 常見問題

### Q1: 找不到網卡
```bash
# 檢查網卡是否支援
dpdk-devbind.py --status-dev net

# 確認驅動載入
lsmod | grep -E "vfio|uio"

# 重新綁定
sudo dpdk-devbind.py -u 0000:02:00.0
sudo dpdk-devbind.py -b vfio-pci 0000:02:00.0
```

### Q2: 大頁記憶體不足
```bash
# 增加大頁數量
echo 2048 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 檢查分配
grep -i huge /proc/meminfo

# 清理舊的大頁
sudo rm -f /mnt/huge/*
```

### Q3: 權限問題
```bash
# 使用 vfio 需要設定權限
sudo chmod a+x /dev/vfio
sudo chmod 0666 /dev/vfio/*

# 或加入 vfio 群組
sudo usermod -a -G vfio $USER
```

### Q4: 虛擬機測試

#### KVM/QEMU 設定
```xml
<!-- 虛擬機 XML 配置 -->
<interface type='hostdev'>
  <source>
    <address type='pci' domain='0x0000' bus='0x02' slot='0x00' function='0x0'/>
  </source>
  <model type='virtio'/>
</interface>
```

#### VirtualBox 設定
```bash
# 啟用虛擬化
VBoxManage modifyvm "VM_NAME" --hwvirtex on --nestedpaging on

# 設定網卡類型
VBoxManage modifyvm "VM_NAME" --nictype1 virtio
VBoxManage modifyvm "VM_NAME" --nictype2 virtio
```

### Q5: 效能不佳

1. **檢查 CPU 親和性**
```bash
taskset -pc $(pidof l2fwd_test)
```

2. **檢查 NUMA 節點**
```bash
numactl --hardware
lstopo
```

3. **檢查網卡設定**
```bash
ethtool -g eth0  # Ring buffer 大小
ethtool -c eth0  # Coalescing 設定
ethtool -k eth0  # Offload 功能
```

---

## 進階配置

### 多佇列支援
```c
/* 修改程式支援多佇列 */
#define NB_RX_QUEUE 4
#define NB_TX_QUEUE 4

/* RSS 配置 */
struct rte_eth_conf port_conf = {
    .rxmode = {
        .mq_mode = ETH_MQ_RX_RSS,
    },
    .rx_adv_conf = {
        .rss_conf = {
            .rss_key = NULL,
            .rss_hf = ETH_RSS_IP | ETH_RSS_UDP | ETH_RSS_TCP,
        },
    },
};
```

### 使用 rte_flow 進行封包分類
```c
/* 建立 flow rule */
struct rte_flow_attr attr = {
    .ingress = 1,
};

struct rte_flow_item pattern[] = {
    {
        .type = RTE_FLOW_ITEM_TYPE_ETH,
    },
    {
        .type = RTE_FLOW_ITEM_TYPE_IPV4,
    },
    {
        .type = RTE_FLOW_ITEM_TYPE_END,
    },
};

struct rte_flow_action action[] = {
    {
        .type = RTE_FLOW_ACTION_TYPE_QUEUE,
        .conf = &(struct rte_flow_action_queue){
            .index = 0,
        },
    },
    {
        .type = RTE_FLOW_ACTION_TYPE_END,
    },
};
```

---

## 總結

這份指南涵蓋了在 Ubuntu 上使用 DPDK 20 測試雙埠收發的完整流程：

1. **環境準備**：安裝 DPDK、配置系統
2. **程式開發**：基本轉發程式、效能測試
3. **執行測試**：使用自定義程式或 testpmd
4. **效能監控**：即時監控、效能分析
5. **問題排查**：常見問題解決方案

**關鍵要點**：
- Ubuntu 完全支援 DPDK 測試
- 虛擬機也可以測試（使用 virtio-net）
- 適當的系統配置對效能至關重要
- 使用 testpmd 可快速驗證功能

根據您的硬體和需求，可以進一步調整配置以獲得最佳效能。