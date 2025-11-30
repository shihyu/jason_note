# 高頻交易：網路 I/O 優化與 FPGA 整合深入指南

完整涵蓋：Kernel Bypass、零拷貝、DPDK、RDMA、FPGA 加速、硬體時間戳

---

## 目錄

1. [網路 I/O 優化基礎](#1-網路-io-優化基礎)
2. [Kernel Bypass 技術](#2-kernel-bypass-技術)
3. [零拷貝技術](#3-零拷貝技術)
4. [DPDK (Data Plane Development Kit)](#4-dpdk-data-plane-development-kit)
5. [RDMA (Remote Direct Memory Access)](#5-rdma-remote-direct-memory-access)
6. [AF_XDP (eXpress Data Path)](#6-af_xdp-express-data-path)
7. [硬體時間戳](#7-硬體時間戳)
8. [FPGA 基礎架構](#8-fpga-基礎架構)
9. [FPGA 訂單處理加速](#9-fpga-訂單處理加速)
10. [FPGA 市場資料解析](#10-fpga-市場資料解析)
11. [CPU-FPGA 通訊](#11-cpu-fpga-通訊)
12. [完整 HFT 系統架構](#12-完整-hft-系統架構)
13. [效能基準測試](#13-效能基準測試)
14. [故障排除與監控](#14-故障排除與監控)

---

## 1. 網路 I/O 優化基礎

### 傳統網路堆疊的問題

```
應用程式
    ↓ (系統呼叫)
Kernel Space
    ↓ (複製)
Socket Buffer
    ↓ (協定處理)
TCP/IP Stack
    ↓ (複製)
NIC Driver
    ↓ (DMA)
Network Card
```

**延遲來源：**
- 系統呼叫：~100-500ns
- 記憶體拷貝：2-4 次
- Context Switch：~1-5μs
- 中斷處理：~500ns-2μs
- 協定處理：~1-3μs

### 標準 Socket 優化

```c
#include <sys/socket.h>
#include <netinet/tcp.h>
#include <arpa/inet.h>

int optimize_socket(int sockfd) {
    int flags = 1;
    
    // 1. TCP_NODELAY - 禁用 Nagle 演算法
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_NODELAY, 
                   &flags, sizeof(flags)) < 0) {
        perror("TCP_NODELAY");
        return -1;
    }
    
    // 2. TCP_QUICKACK - 快速 ACK
    if (setsockopt(sockfd, IPPROTO_TCP, TCP_QUICKACK,
                   &flags, sizeof(flags)) < 0) {
        perror("TCP_QUICKACK");
    }
    
    // 3. SO_RCVBUF - 增大接收緩衝區
    int rcvbuf = 4 * 1024 * 1024;  // 4MB
    if (setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF,
                   &rcvbuf, sizeof(rcvbuf)) < 0) {
        perror("SO_RCVBUF");
    }
    
    // 4. SO_SNDBUF - 增大發送緩衝區
    int sndbuf = 4 * 1024 * 1024;  // 4MB
    if (setsockopt(sockfd, SOL_SOCKET, SO_SNDBUF,
                   &sndbuf, sizeof(sndbuf)) < 0) {
        perror("SO_SNDBUF");
    }
    
    // 5. SO_REUSEADDR - 快速重用地址
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR,
                   &flags, sizeof(flags)) < 0) {
        perror("SO_REUSEADDR");
    }
    
    // 6. SO_REUSEPORT - 端口重用（多執行緒）
    if (setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT,
                   &flags, sizeof(flags)) < 0) {
        perror("SO_REUSEPORT");
    }
    
    // 7. SO_INCOMING_CPU - 綁定到特定 CPU
    int cpu = 2;
    if (setsockopt(sockfd, SOL_SOCKET, SO_INCOMING_CPU,
                   &cpu, sizeof(cpu)) < 0) {
        perror("SO_INCOMING_CPU");
    }
    
    // 8. 設定非阻塞模式
    int sock_flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, sock_flags | O_NONBLOCK);
    
    return 0;
}

// 使用範例
int main() {
    int sockfd = socket(AF_INET, SOCK_STREAM, 0);
    optimize_socket(sockfd);
    
    struct sockaddr_in addr = {
        .sin_family = AF_INET,
        .sin_port = htons(12345),
        .sin_addr.s_addr = inet_addr("192.168.1.100")
    };
    
    connect(sockfd, (struct sockaddr*)&addr, sizeof(addr));
    
    // 使用 socket...
    
    return 0;
}
```

### 系統層級網路調校

```bash
#!/bin/bash
# network_tuning.sh

# ============ TCP 參數優化 ============
# 禁用 TCP timestamps（減少開銷）
sudo sysctl -w net.ipv4.tcp_timestamps=0

# 禁用 SACK（簡化處理）
sudo sysctl -w net.ipv4.tcp_sack=0

# 快速回收 TIME_WAIT
sudo sysctl -w net.ipv4.tcp_tw_reuse=1

# 增大 TCP 緩衝區
sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 67108864"
sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 67108864"

# 增大核心緩衝區
sudo sysctl -w net.core.rmem_max=134217728
sudo sysctl -w net.core.wmem_max=134217728

# 增大 backlog
sudo sysctl -w net.core.netdev_max_backlog=250000
sudo sysctl -w net.ipv4.tcp_max_syn_backlog=8192

# ============ 中斷處理 ============
# 查找網卡中斷號
NIC_NAME="eth0"
IRQ=$(cat /proc/interrupts | grep $NIC_NAME | awk '{print $1}' | tr -d ':')

# 綁定到特定 CPU（避免打擾交易核心）
echo 1 | sudo tee /proc/irq/$IRQ/smp_affinity_list

# ============ Ring Buffer 大小 ============
# 增大網卡 ring buffer
sudo ethtool -G eth0 rx 4096 tx 4096

# ============ 啟用硬體卸載 ============
sudo ethtool -K eth0 tso off gso off gro off lro off
sudo ethtool -K eth0 rx-checksumming on tx-checksumming on

# ============ 停用不必要的服務 ============
sudo systemctl stop firewalld
sudo systemctl disable firewalld
```

---

## 2. Kernel Bypass 技術

### 概念

Kernel Bypass 讓應用程式直接存取網卡，完全繞過 kernel 網路堆疊。

**優勢：**
- 延遲降低 10-100 倍
- 零系統呼叫
- 零拷貝
- 零中斷
- CPU 使用率降低

### 架構比較

```
傳統堆疊:
App → syscall → Kernel → NIC Driver → NIC
延遲: ~10-50μs

Kernel Bypass:
App → User Space Driver → NIC (DMA)
延遲: ~0.5-2μs
```

### 常見 Kernel Bypass 方案

| 技術 | 延遲 | 吞吐量 | 複雜度 | 成本 |
|------|------|--------|--------|------|
| DPDK | 0.5-2μs | 高 | 高 | 免費 |
| Solarflare OpenOnload | 0.3-1μs | 高 | 中 | 需授權 |
| Mellanox VMA | 0.5-1.5μs | 高 | 中 | 免費 |
| RDMA | 0.3-1μs | 極高 | 中 | 需特殊硬體 |
| AF_XDP | 1-3μs | 中高 | 低 | 免費 |

---

## 3. 零拷貝技術

### sendfile()

```c
#include <sys/sendfile.h>

// 零拷貝發送檔案
ssize_t send_file_zero_copy(int out_fd, int in_fd, off_t offset, size_t count) {
    return sendfile(out_fd, in_fd, &offset, count);
}

// 使用範例：發送檔案到 socket
int fd = open("market_data.bin", O_RDONLY);
sendfile(sockfd, fd, NULL, file_size);
```

### splice()

```c
#include <fcntl.h>

// pipe 到 socket 零拷貝
ssize_t splice_to_socket(int pipe_fd, int sockfd, size_t len) {
    return splice(pipe_fd, NULL, sockfd, NULL, len, SPLICE_F_MOVE);
}
```

### mmap() + write()

```c
#include <sys/mman.h>

void* map_file(const char *filename, size_t *size) {
    int fd = open(filename, O_RDONLY);
    struct stat sb;
    fstat(fd, &sb);
    *size = sb.st_size;
    
    void *mapped = mmap(NULL, *size, PROT_READ, MAP_PRIVATE, fd, 0);
    close(fd);
    
    return mapped;
}

// 使用 mmap 發送資料
size_t size;
void *data = map_file("data.bin", &size);
write(sockfd, data, size);
munmap(data, size);
```

### MSG_ZEROCOPY (Linux 4.14+)

```c
#include <linux/errqueue.h>

int send_zero_copy(int sockfd, const void *buf, size_t len) {
    // 啟用 MSG_ZEROCOPY
    int val = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_ZEROCOPY, &val, sizeof(val));
    
    // 發送資料
    ssize_t ret = send(sockfd, buf, len, MSG_ZEROCOPY);
    
    // 等待完成通知（可選）
    struct msghdr msg = {0};
    struct cmsghdr *cmsg;
    char control[100];
    
    msg.msg_control = control;
    msg.msg_controllen = sizeof(control);
    
    recvmsg(sockfd, &msg, MSG_ERRQUEUE);
    
    return ret;
}
```

---

## 4. DPDK (Data Plane Development Kit)

### 安裝 DPDK

```bash
#!/bin/bash

# 安裝依賴
sudo apt-get install -y build-essential libnuma-dev python3-pip
pip3 install meson ninja

# 下載 DPDK
wget https://fast.dpdk.org/rel/dpdk-23.11.tar.xz
tar xf dpdk-23.11.tar.xz
cd dpdk-23.11

# 編譯
meson setup build
cd build
ninja
sudo ninja install
sudo ldconfig

# 設定 Huge Pages
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 綁定網卡到 DPDK
sudo modprobe uio_pci_generic
sudo dpdk-devbind.py --bind=uio_pci_generic 0000:01:00.0
```

### DPDK 基本程式

```c
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_cycles.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8192
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

static struct rte_mempool *mbuf_pool = NULL;

// 初始化 DPDK
int dpdk_init(int argc, char *argv[]) {
    int ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
    }
    
    return ret;
}

// 創建記憶體池
void create_mempool(void) {
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL",
        NUM_MBUFS,
        MBUF_CACHE_SIZE,
        0,
        RTE_MBUF_DEFAULT_BUF_SIZE,
        rte_socket_id());
    
    if (mbuf_pool == NULL) {
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");
    }
}

// 初始化網卡
int init_port(uint16_t port) {
    struct rte_eth_conf port_conf = {
        .rxmode = {
            .max_lro_pkt_size = RTE_ETHER_MAX_LEN,
        },
    };
    
    struct rte_eth_dev_info dev_info;
    rte_eth_dev_info_get(port, &dev_info);
    
    // 配置網卡
    int ret = rte_eth_dev_configure(port, 1, 1, &port_conf);
    if (ret < 0) return ret;
    
    // 設定 RX queue
    ret = rte_eth_rx_queue_setup(port, 0, RX_RING_SIZE,
        rte_eth_dev_socket_id(port), NULL, mbuf_pool);
    if (ret < 0) return ret;
    
    // 設定 TX queue
    ret = rte_eth_tx_queue_setup(port, 0, TX_RING_SIZE,
        rte_eth_dev_socket_id(port), NULL);
    if (ret < 0) return ret;
    
    // 啟動網卡
    ret = rte_eth_dev_start(port);
    if (ret < 0) return ret;
    
    // 啟用 promiscuous mode
    rte_eth_promiscuous_enable(port);
    
    return 0;
}

// 接收封包
void receive_packets(uint16_t port) {
    struct rte_mbuf *bufs[BURST_SIZE];
    
    while (1) {
        // 接收一批封包
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        
        if (unlikely(nb_rx == 0)) {
            continue;
        }
        
        // 處理每個封包
        for (uint16_t i = 0; i < nb_rx; i++) {
            struct rte_mbuf *m = bufs[i];
            
            // 取得封包資料
            uint8_t *pkt_data = rte_pktmbuf_mtod(m, uint8_t*);
            uint16_t pkt_len = rte_pktmbuf_pkt_len(m);
            
            // 處理封包
            process_packet(pkt_data, pkt_len);
            
            // 釋放 mbuf
            rte_pktmbuf_free(m);
        }
    }
}

// 發送封包
void send_packet(uint16_t port, const void *data, uint16_t len) {
    struct rte_mbuf *m = rte_pktmbuf_alloc(mbuf_pool);
    
    if (m == NULL) {
        return;
    }
    
    // 複製資料到 mbuf
    uint8_t *pkt_data = rte_pktmbuf_mtod(m, uint8_t*);
    memcpy(pkt_data, data, len);
    m->pkt_len = len;
    m->data_len = len;
    
    // 發送
    uint16_t nb_tx = rte_eth_tx_burst(port, 0, &m, 1);
    
    if (unlikely(nb_tx == 0)) {
        rte_pktmbuf_free(m);
    }
}

// 主函數
int main(int argc, char *argv[]) {
    // 初始化 DPDK
    int ret = dpdk_init(argc, argv);
    argc -= ret;
    argv += ret;
    
    // 創建記憶體池
    create_mempool();
    
    // 初始化網卡 0
    uint16_t port = 0;
    if (init_port(port) != 0) {
        rte_exit(EXIT_FAILURE, "Cannot init port %u\n", port);
    }
    
    printf("DPDK initialized, receiving packets...\n");
    
    // 接收封包
    receive_packets(port);
    
    return 0;
}
```

### DPDK 編譯

```bash
# Makefile for DPDK application
CC = gcc
CFLAGS = -O3 -march=native
CFLAGS += $(shell pkg-config --cflags libdpdk)
LDFLAGS = $(shell pkg-config --libs libdpdk)

dpdk_app: dpdk_app.c
	$(CC) $(CFLAGS) $< -o $@ $(LDFLAGS)

clean:
	rm -f dpdk_app
```

### DPDK 高級特性

```c
// ============ RSS (Receive Side Scaling) ============
struct rte_eth_conf port_conf = {
    .rxmode = {
        .mq_mode = RTE_ETH_MQ_RX_RSS,
    },
    .rx_adv_conf = {
        .rss_conf = {
            .rss_key = NULL,
            .rss_hf = RTE_ETH_RSS_IP | RTE_ETH_RSS_TCP,
        },
    },
};

// ============ 批次處理 ============
void receive_and_process_batch(uint16_t port) {
    struct rte_mbuf *bufs[BURST_SIZE];
    struct rte_mbuf *tx_bufs[BURST_SIZE];
    uint16_t nb_tx = 0;
    
    while (1) {
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        
        // 批次處理
        for (uint16_t i = 0; i < nb_rx; i++) {
            if (process_and_reply(bufs[i], &tx_bufs[nb_tx])) {
                nb_tx++;
            }
            rte_pktmbuf_free(bufs[i]);
        }
        
        // 批次發送
        if (nb_tx > 0) {
            uint16_t sent = rte_eth_tx_burst(port, 0, tx_bufs, nb_tx);
            
            // 釋放未發送的
            for (uint16_t i = sent; i < nb_tx; i++) {
                rte_pktmbuf_free(tx_bufs[i]);
            }
            nb_tx = 0;
        }
    }
}

// ============ 硬體時間戳 ============
void enable_hardware_timestamp(uint16_t port) {
    struct rte_eth_dev_info dev_info;
    rte_eth_dev_info_get(port, &dev_info);
    
    if (dev_info.rx_offload_capa & RTE_ETH_RX_OFFLOAD_TIMESTAMP) {
        struct rte_eth_conf port_conf = {
            .rxmode = {
                .offloads = RTE_ETH_RX_OFFLOAD_TIMESTAMP,
            },
        };
        // 重新配置...
    }
}

uint64_t get_packet_timestamp(struct rte_mbuf *m) {
    return m->timestamp;
}
```

---

## 5. RDMA (Remote Direct Memory Access)

### RDMA 概念

RDMA 允許直接在遠端機器的記憶體中讀寫資料，完全繞過 CPU 和作業系統。

**特點：**
- 延遲：~0.5-1μs
- 零拷貝
- 零 CPU 參與
- 高頻寬

### 支援的硬體

- InfiniBand (Mellanox)
- RoCE (RDMA over Converged Ethernet)
- iWARP

### 安裝 RDMA

```bash
#!/bin/bash

# 安裝 RDMA 核心模組
sudo apt-get install -y rdma-core libibverbs-dev librdmacm-dev

# 載入模組
sudo modprobe ib_uverbs
sudo modprobe rdma_ucm

# 檢查 RDMA 設備
ibv_devices
```

### RDMA 程式範例

```c
#include <infiniband/verbs.h>
#include <rdma/rdma_cma.h>

// ============ 初始化 RDMA ============
struct ibv_context* init_rdma_device(void) {
    struct ibv_device **dev_list;
    struct ibv_context *context;
    
    // 列出所有設備
    dev_list = ibv_get_device_list(NULL);
    if (!dev_list) {
        fprintf(stderr, "Failed to get IB devices list\n");
        return NULL;
    }
    
    // 打開第一個設備
    context = ibv_open_device(dev_list[0]);
    if (!context) {
        fprintf(stderr, "Failed to open device\n");
        return NULL;
    }
    
    ibv_free_device_list(dev_list);
    return context;
}

// ============ 創建 Protection Domain ============
struct ibv_pd* create_protection_domain(struct ibv_context *context) {
    struct ibv_pd *pd = ibv_alloc_pd(context);
    if (!pd) {
        fprintf(stderr, "Failed to allocate PD\n");
        return NULL;
    }
    return pd;
}

// ============ 註冊記憶體區域 ============
struct ibv_mr* register_memory(struct ibv_pd *pd, void *addr, size_t length) {
    struct ibv_mr *mr = ibv_reg_mr(pd, addr, length,
        IBV_ACCESS_LOCAL_WRITE |
        IBV_ACCESS_REMOTE_READ |
        IBV_ACCESS_REMOTE_WRITE);
    
    if (!mr) {
        fprintf(stderr, "Failed to register MR\n");
        return NULL;
    }
    
    return mr;
}

// ============ 創建 Queue Pair ============
struct ibv_qp* create_queue_pair(struct ibv_pd *pd, struct ibv_cq *cq) {
    struct ibv_qp_init_attr qp_init_attr = {
        .send_cq = cq,
        .recv_cq = cq,
        .qp_type = IBV_QPT_RC,  // Reliable Connection
        .cap = {
            .max_send_wr = 128,
            .max_recv_wr = 128,
            .max_send_sge = 1,
            .max_recv_sge = 1,
        },
    };
    
    struct ibv_qp *qp = ibv_create_qp(pd, &qp_init_attr);
    if (!qp) {
        fprintf(stderr, "Failed to create QP\n");
        return NULL;
    }
    
    return qp;
}

// ============ RDMA Write ============
int rdma_write(struct ibv_qp *qp, struct ibv_mr *local_mr,
               void *local_addr, size_t length,
               uint64_t remote_addr, uint32_t rkey) {
    
    struct ibv_sge sge = {
        .addr = (uintptr_t)local_addr,
        .length = length,
        .lkey = local_mr->lkey,
    };
    
    struct ibv_send_wr wr = {
        .wr_id = 0,
        .sg_list = &sge,
        .num_sge = 1,
        .opcode = IBV_WR_RDMA_WRITE,
        .send_flags = IBV_SEND_SIGNALED,
        .wr.rdma = {
            .remote_addr = remote_addr,
            .rkey = rkey,
        },
    };
    
    struct ibv_send_wr *bad_wr;
    int ret = ibv_post_send(qp, &wr, &bad_wr);
    
    return ret;
}

// ============ RDMA Read ============
int rdma_read(struct ibv_qp *qp, struct ibv_mr *local_mr,
              void *local_addr, size_t length,
              uint64_t remote_addr, uint32_t rkey) {
    
    struct ibv_sge sge = {
        .addr = (uintptr_t)local_addr,
        .length = length,
        .lkey = local_mr->lkey,
    };
    
    struct ibv_send_wr wr = {
        .wr_id = 1,
        .sg_list = &sge,
        .num_sge = 1,
        .opcode = IBV_WR_RDMA_READ,
        .send_flags = IBV_SEND_SIGNALED,
        .wr.rdma = {
            .remote_addr = remote_addr,
            .rkey = rkey,
        },
    };
    
    struct ibv_send_wr *bad_wr;
    return ibv_post_send(qp, &wr, &bad_wr);
}

// ============ 等待完成 ============
int wait_for_completion(struct ibv_cq *cq) {
    struct ibv_wc wc;
    int num_completions;
    
    do {
        num_completions = ibv_poll_cq(cq, 1, &wc);
    } while (num_completions == 0);
    
    if (num_completions < 0) {
        fprintf(stderr, "Failed to poll CQ\n");
        return -1;
    }
    
    if (wc.status != IBV_WC_SUCCESS) {
        fprintf(stderr, "Work completion failed: %s\n",
                ibv_wc_status_str(wc.status));
        return -1;
    }
    
    return 0;
}

// ============ 完整範例 ============
int main(void) {
    // 1. 初始化設備
    struct ibv_context *context = init_rdma_device();
    
    // 2. 創建 Protection Domain
    struct ibv_pd *pd = create_protection_domain(context);
    
    // 3. 創建 Completion Queue
    struct ibv_cq *cq = ibv_create_cq(context, 128, NULL, NULL, 0);
    
    // 4. 分配並註冊記憶體
    size_t buffer_size = 4096;
    void *buffer = malloc(buffer_size);
    struct ibv_mr *mr = register_memory(pd, buffer, buffer_size);
    
    // 5. 創建 Queue Pair
    struct ibv_qp *qp = create_queue_pair(pd, cq);
    
    // 6. 連接到遠端（省略連接邏輯）
    // ...
    
    // 7. RDMA Write
    uint64_t remote_addr = 0x1000000;  // 遠端地址
    uint32_t rkey = 0x12345678;         // 遠端 key
    
    strcpy(buffer, "Hello RDMA!");
    rdma_write(qp, mr, buffer, strlen(buffer) + 1, remote_addr, rkey);
    
    // 8. 等待完成
    wait_for_completion(cq);
    
    printf("RDMA write completed\n");
    
    // 清理
    ibv_destroy_qp(qp);
    ibv_destroy_cq(cq);
    ibv_dereg_mr(mr);
    ibv_dealloc_pd(pd);
    ibv_close_device(context);
    free(buffer);
    
    return 0;
}
```

### RDMA 用於 HFT

```c
// ============ 市場資料接收 ============
typedef struct {
    uint64_t timestamp;
    uint32_t symbol_id;
    double price;
    uint32_t quantity;
} __attribute__((packed)) MarketDataMsg;

// 共享記憶體區域（RDMA 映射）
#define MAX_SYMBOLS 10000
MarketDataMsg *market_data_buffer;

void setup_market_data_rdma(struct ibv_pd *pd) {
    size_t size = MAX_SYMBOLS * sizeof(MarketDataMsg);
    market_data_buffer = aligned_alloc(4096, size);
    
    struct ibv_mr *mr = register_memory(pd, market_data_buffer, size);
    
    // 將 mr->rkey 發送給遠端
    printf("Remote Key: 0x%x\n", mr->rkey);
    printf("Address: 0x%lx\n", (uint64_t)market_data_buffer);
}

// 本地讀取（零延遲）
MarketDataMsg read_market_data(uint32_t symbol_id) {
    return market_data_buffer[symbol_id];
}
```

---

## 6. AF_XDP (eXpress Data Path)

### AF_XDP 概念

AF_XDP 是 Linux kernel 提供的高效能 socket，結合 eBPF 和 XDP (eXpress Data Path)。

**特點：**
- 延遲：~1-3μs
- 較 DPDK 簡單
- 不需要專用驅動
- 可與 kernel 網路堆疊共存

### 安裝依賴

```bash
sudo apt-get install -y libbpf-dev libelf-dev
```

### AF_XDP 程式範例

```c
#include <linux/if_xdp.h>
#include <bpf/xsk.h>
#include <bpf/libbpf.h>

#define BATCH_SIZE 64
#define UMEM_SIZE 4096
#define FRAME_SIZE 2048
#define NUM_FRAMES (UMEM_SIZE / FRAME_SIZE)

struct xsk_socket_info {
    struct xsk_ring_cons rx;
    struct xsk_ring_prod tx;
    struct xsk_umem *umem;
    struct xsk_socket *xsk;
    void *umem_area;
    uint64_t umem_frame_addr[NUM_FRAMES];
    uint32_t umem_frame_free;
};

// ============ 初始化 UMEM ============
int init_umem(struct xsk_socket_info *xsk_info) {
    // 分配 UMEM
    xsk_info->umem_area = aligned_alloc(getpagesize(), UMEM_SIZE);
    if (!xsk_info->umem_area) {
        return -1;
    }
    
    // 配置 UMEM
    struct xsk_umem_config cfg = {
        .fill_size = NUM_FRAMES * 2,
        .comp_size = NUM_FRAMES,
        .frame_size = FRAME_SIZE,
        .frame_headroom = 0,
        .flags = 0,
    };
    
    int ret = xsk_umem__create(&xsk_info->umem,
                               xsk_info->umem_area,
                               UMEM_SIZE,
                               &xsk_info->rx,
                               &xsk_info->tx,
                               &cfg);
    
    if (ret) {
        free(xsk_info->umem_area);
        return ret;
    }
    
    // 初始化 frame pool
    for (int i = 0; i < NUM_FRAMES; i++) {
        xsk_info->umem_frame_addr[i] = i * FRAME_SIZE;
    }
    xsk_info->umem_frame_free = NUM_FRAMES;
    
    return 0;
}

// ============ 創建 XSK Socket ============
int create_xsk_socket(struct xsk_socket_info *xsk_info,
                      const char *ifname, int queue_id) {
    
    struct xsk_socket_config cfg = {
        .rx_size = NUM_FRAMES,
        .tx_size = NUM_FRAMES,
        .libbpf_flags = 0,
        .xdp_flags = XDP_FLAGS_UPDATE_IF_NOEXIST,
        .bind_flags = XDP_ZEROCOPY,
    };
    
    int ret = xsk_socket__create(&xsk_info->xsk,
                                 ifname,
                                 queue_id,
                                 xsk_info->umem,
                                 &xsk_info->rx,
                                 &xsk_info->tx,
                                 &cfg);
    
    return ret;
}

// ============ 接收封包 ============
void receive_packets_xdp(struct xsk_socket_info *xsk) {
    struct xsk_ring_cons *rx = &xsk->rx;
    uint32_t idx_rx = 0;
    uint32_t idx_fq = 0;
    
    while (1) {
        // 接收
        unsigned int rcvd = xsk_ring_cons__peek(rx, BATCH_SIZE, &idx_rx);
        
        if (rcvd == 0) {
            continue;
        }
        
        // 處理每個封包
        for (unsigned int i = 0; i < rcvd; i++) {
            const struct xdp_desc *desc = xsk_ring_cons__rx_desc(rx, idx_rx++);
            
            void *pkt = xsk_umem__get_data(xsk->umem_area, desc->addr);
            uint32_t len = desc->len;
            
            // 處理封包
            process_packet(pkt, len);
        }
        
        // 釋放接收的 frames
        xsk_ring_cons__release(rx, rcvd);
        
        // 補充 fill ring
        unsigned int stock = xsk_prod_nb_free(&xsk->umem->fq, xsk->umem_frame_free);
        if (stock > 0) {
            xsk_ring_prod__reserve(&xsk->umem->fq, stock, &idx_fq);
            
            for (unsigned int i = 0; i < stock; i++) {
                *xsk_ring_prod__fill_addr(&xsk->umem->fq, idx_fq++) =
                    xsk->umem_frame_addr[--xsk->umem_frame_free];
            }
            
            xsk_ring_prod__submit(&xsk->umem->fq, stock);
        }
    }
}

// ============ 發送封包 ============
int send_packet_xdp(struct xsk_socket_info *xsk,
                    const void *data, size_t len) {
    struct xsk_ring_prod *tx = &xsk->tx;
    uint32_t idx;
    
    if (xsk_ring_prod__reserve(tx, 1, &idx) != 1) {
        return -1;
    }
    
    // 分配 frame
    if (xsk->umem_frame_free == 0) {
        return -1;
    }
    
    uint64_t addr = xsk->umem_frame_addr[--xsk->umem_frame_free];
    
    // 複製資料
    void *pkt = xsk_umem__get_data(xsk->umem_area, addr);
    memcpy(pkt, data, len);
    
    // 設定描述符
    struct xdp_desc *desc = xsk_ring_prod__tx_desc(tx, idx);
    desc->addr = addr;
    desc->len = len;
    
    xsk_ring_prod__submit(tx, 1);
    
    // 等待完成
    xsk->outstanding_tx++;
    
    return 0;
}

// ============ 主函數 ============
int main(void) {
    struct xsk_socket_info xsk_info = {0};
    
    // 初始化 UMEM
    if (init_umem(&xsk_info) != 0) {
        fprintf(stderr, "Failed to init UMEM\n");
        return 1;
    }
    
    // 創建 socket
    if (create_xsk_socket(&xsk_info, "eth0", 0) != 0) {
        fprintf(stderr, "Failed to create XSK socket\n");
        return 1;
    }
    
    printf("AF_XDP socket created, receiving packets...\n");
    
    // 接收封包
    receive_packets_xdp(&xsk_info);
    
    return 0;
}
```

---

## 7. 硬體時間戳

### 概念

硬體時間戳由網卡在封包到達/發送時直接打上時間戳，精度遠高於軟體時間戳。

**精度：**
- 軟體時間戳：~100ns-1μs
- 硬體時間戳：~10-50ns

### PTP (Precision Time Protocol)

```bash
# 安裝 linuxptp
sudo apt-get install -y linuxptp

# 啟動 PTP daemon
sudo ptp4l -i eth0 -m -S

# 同步系統時鐘
sudo phc2sys -s eth0 -m
```

### 啟用硬體時間戳

```c
#include <linux/net_tstamp.h>
#include <linux/sockios.h>
#include <sys/ioctl.h>

int enable_hardware_timestamp(int sockfd, const char *ifname) {
    struct ifreq ifr;
    struct hwtstamp_config hwconfig;
    
    memset(&ifr, 0, sizeof(ifr));
    memset(&hwconfig, 0, sizeof(hwconfig));
    
    strncpy(ifr.ifr_name, ifname, IFNAMSIZ - 1);
    
    // 配置硬體時間戳
    hwconfig.tx_type = HWTSTAMP_TX_ON;
    hwconfig.rx_filter = HWTSTAMP_FILTER_ALL;
    
    ifr.ifr_data = (char*)&hwconfig;
    
    if (ioctl(sockfd, SIOCSHWTSTAMP, &ifr) < 0) {
        perror("SIOCSHWTSTAMP");
        return -1;
    }
    
    // 啟用 SO_TIMESTAMP
    int val = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_TIMESTAMPNS, &val, sizeof(val)) < 0) {
        perror("SO_TIMESTAMPNS");
        return -1;
    }
    
    return 0;
}

// ============ 讀取時間戳 ============
uint64_t receive_with_timestamp(int sockfd, void *buf, size_t len) {
    struct msghdr msg = {0};
    struct iovec iov[1];
    char control[512];
    
    iov[0].iov_base = buf;
    iov[0].iov_len = len;
    
    msg.msg_iov = iov;
    msg.msg_iovlen = 1;
    msg.msg_control = control;
    msg.msg_controllen = sizeof(control);
    
    ssize_t n = recvmsg(sockfd, &msg, 0);
    if (n < 0) {
        return 0;
    }
    
    // 解析時間戳
    struct cmsghdr *cmsg;
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && cmsg->cmsg_type == SO_TIMESTAMPNS) {
            struct timespec *ts = (struct timespec*)CMSG_DATA(cmsg);
            return ts->tv_sec * 1000000000ULL + ts->tv_nsec;
        }
    }
    
    return 0;
}
```

### 發送時間戳

```c
uint64_t send_with_timestamp(int sockfd, const void *buf, size_t len) {
    // 發送封包
    ssize_t sent = send(sockfd, buf, len, 0);
    if (sent < 0) {
        return 0;
    }
    
    // 讀取發送時間戳
    struct msghdr msg = {0};
    char control[512];
    
    msg.msg_control = control;
    msg.msg_controllen = sizeof(control);
    
    if (recvmsg(sockfd, &msg, MSG_ERRQUEUE) < 0) {
        return 0;
    }
    
    struct cmsghdr *cmsg;
    for (cmsg = CMSG_FIRSTHDR(&msg); cmsg != NULL; cmsg = CMSG_NXTHDR(&msg, cmsg)) {
        if (cmsg->cmsg_level == SOL_SOCKET && 
            cmsg->cmsg_type == SO_TIMESTAMPING) {
            struct timespec *ts = (struct timespec*)CMSG_DATA(cmsg);
            return ts[2].tv_sec * 1000000000ULL + ts[2].tv_nsec;
        }
    }
    
    return 0;
}
```

---

## 8. FPGA 基礎架構

### FPGA 優勢

**vs CPU：**
- 延遲：10-100 倍更低
- 決定性：無分支預測、無 cache miss
- 平行處理：天生並行
- 功耗：更低

**vs ASIC：**
- 可重新編程
- 開發週期短
- 成本較低

### HFT 中的 FPGA 應用

1. **網路處理**
   - 封包解析
   - 協定處理（TCP/UDP/FIX）
   - 時間戳

2. **訂單處理**
   - 訂單驗證
   - 風險檢查
   - 訂單路由

3. **市場資料處理**
   - Feed handler
   - 資料正規化
   - 訂單簿維護

4. **策略執行**
   - 價格計算
   - 信號生成
   - 套利檢測

### 常見 FPGA 平台

| 廠商 | 產品 | 特點 |
|------|------|------|
| Xilinx | Alveo U280 | 高效能，PCIe 4.0 |
| Intel | Stratix 10 | 高密度，HBM2 |
| Achronix | Speedster7t | 超高頻寬 |

### FPGA 開發流程

```
設計 (VHDL/Verilog/HLS)
    ↓
綜合 (Synthesis)
    ↓
實作 (Implementation)
    ↓
位元流生成 (Bitstream)
    ↓
下載到 FPGA
```

---

## 9. FPGA 訂單處理加速

### Verilog 範例：訂單解析器

```verilog
// order_parser.v - FIX 協定訂單解析器

module order_parser (
    input wire clk,
    input wire rst_n,
    
    // 輸入 FIX 訊息
    input wire [7:0] fix_data,
    input wire fix_valid,
    
    // 輸出解析後的訂單
    output reg [63:0] order_id,
    output reg [31:0] price,
    output reg [31:0] quantity,
    output reg is_buy,
    output reg order_valid
);

// 狀態機
localparam IDLE = 3'd0;
localparam READ_TAG = 3'd1;
localparam READ_VALUE = 3'd2;
localparam DONE = 3'd3;

reg [2:0] state;
reg [7:0] current_tag;
reg [31:0] current_value;
reg [7:0] value_index;

// FIX 標籤定義
localparam TAG_ORDER_ID = 8'd37;   // ClOrdID
localparam TAG_PRICE = 8'd44;      // Price
localparam TAG_QUANTITY = 8'd38;   // OrderQty
localparam TAG_SIDE = 8'd54;       // Side

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        state <= IDLE;
        order_valid <= 1'b0;
        current_tag <= 8'd0;
        current_value <= 32'd0;
        value_index <= 8'd0;
    end else begin
        case (state)
            IDLE: begin
                order_valid <= 1'b0;
                if (fix_valid && fix_data == 8'h01) begin // SOH
                    state <= READ_TAG;
                end
            end
            
            READ_TAG: begin
                if (fix_valid) begin
                    if (fix_data == 8'h3D) begin // '='
                        state <= READ_VALUE;
                        value_index <= 8'd0;
                        current_value <= 32'd0;
                    end else if (fix_data >= 8'h30 && fix_data <= 8'h39) begin
                        // 數字 '0'-'9'
                        current_tag <= current_tag * 10 + (fix_data - 8'h30);
                    end
                end
            end
            
            READ_VALUE: begin
                if (fix_valid) begin
                    if (fix_data == 8'h01) begin // SOH (分隔符)
                        // 儲存值
                        case (current_tag)
                            TAG_ORDER_ID: order_id <= {32'd0, current_value};
                            TAG_PRICE: price <= current_value;
                            TAG_QUANTITY: quantity <= current_value;
                            TAG_SIDE: is_buy <= (current_value == 32'd1);
                        endcase
                        
                        current_tag <= 8'd0;
                        state <= READ_TAG;
                    end else if (fix_data >= 8'h30 && fix_data <= 8'h39) begin
                        current_value <= current_value * 10 + (fix_data - 8'h30);
                    end else if (fix_data == 8'h10) begin // End of message
                        state <= DONE;
                    end
                end
            end
            
            DONE: begin
                order_valid <= 1'b1;
                state <= IDLE;
            end
        endcase
    end
end

endmodule
```

### 訂單驗證器

```verilog
// order_validator.v - 訂單驗證邏輯

module order_validator (
    input wire clk,
    input wire rst_n,
    
    // 輸入訂單
    input wire [63:0] order_id,
    input wire [31:0] price,
    input wire [31:0] quantity,
    input wire is_buy,
    input wire order_valid_in,
    
    // 限制參數
    input wire [31:0] max_quantity,
    input wire [31:0] min_price,
    input wire [31:0] max_price,
    
    // 輸出
    output reg order_valid_out,
    output reg [2:0] error_code
);

localparam ERR_NONE = 3'd0;
localparam ERR_QUANTITY = 3'd1;
localparam ERR_PRICE_LOW = 3'd2;
localparam ERR_PRICE_HIGH = 3'd3;

always @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
        order_valid_out <= 1'b0;
        error_code <= ERR_NONE;
    end else if (order_valid_in) begin
        // 驗證數量
        if (quantity > max_quantity || quantity == 0) begin
            order_valid_out <= 1'b0;
            error_code <= ERR_QUANTITY;
        end
        // 驗證價格
        else if (price < min_price) begin
            order_valid_out <= 1'b0;
            error_code <= ERR_PRICE_LOW;
        end
        else if (price > max_price) begin
            order_valid_out <= 1'b0;
            error_code <= ERR_PRICE_HIGH;
        end
        // 通過驗證
        else begin
            order_valid_out <= 1'b1;
            error_code <= ERR_NONE;
        end
    end else begin
        order_valid_out <= 1'b0;
    end
end

endmodule
```

### 高層次綜合 (HLS) 範例

使用 Vitis HLS (C/C++ 轉 FPGA)：

```cpp
// order_processor.cpp - 使用 HLS

#include <ap_int.h>
#include <hls_stream.h>

// 訂單結構
struct Order {
    ap_uint<64> order_id;
    ap_uint<32> price;
    ap_uint<32> quantity;
    ap_uint<1> is_buy;
};

// 管線化的訂單處理
void process_order(hls::stream<Order> &input,
                   hls::stream<Order> &output,
                   ap_uint<32> max_quantity,
                   ap_uint<32> min_price,
                   ap_uint<32> max_price) {
    
    #pragma HLS INTERFACE axis port=input
    #pragma HLS INTERFACE axis port=output
    #pragma HLS INTERFACE s_axilite port=max_quantity
    #pragma HLS INTERFACE s_axilite port=min_price
    #pragma HLS INTERFACE s_axilite port=max_price
    #pragma HLS INTERFACE s_axilite port=return
    
    #pragma HLS PIPELINE II=1
    
    while (true) {
        Order order = input.read();
        
        // 驗證
        bool valid = true;
        
        if (order.quantity > max_quantity || order.quantity == 0) {
            valid = false;
        }
        
        if (order.price < min_price || order.price > max_price) {
            valid = false;
        }
        
        if (valid) {
            output.write(order);
        }
    }
}

// 批次處理範例
void batch_process_orders(Order orders[1024],
                          Order valid_orders[1024],
                          int *num_valid,
                          ap_uint<32> max_quantity) {
    
    #pragma HLS INTERFACE m_axi port=orders offset=slave bundle=gmem0
    #pragma HLS INTERFACE m_axi port=valid_orders offset=slave bundle=gmem1
    #pragma HLS INTERFACE s_axilite port=num_valid
    #pragma HLS INTERFACE s_axilite port=max_quantity
    #pragma HLS INTERFACE s_axilite port=return
    
    int count = 0;
    
    PROCESS_LOOP: for (int i = 0; i < 1024; i++) {
        #pragma HLS PIPELINE II=1
        
        Order order = orders[i];
        
        if (order.quantity <= max_quantity && order.quantity > 0) {
            valid_orders[count++] = order;
        }
    }
    
    *num_valid = count;
}
```

---

## 10. FPGA 市場資料解析

### Feed Handler (VHDL)

```vhdl
-- market_data_parser.vhd

library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

entity market_data_parser is
    Port (
        clk : in STD_LOGIC;
        rst_n : in STD_LOGIC;
        
        -- 輸入資料流
        data_in : in STD_LOGIC_VECTOR(7 downto 0);
        data_valid : in STD_LOGIC;
        
        -- 輸出市場資料
        symbol_id : out STD_LOGIC_VECTOR(31 downto 0);
        price : out STD_LOGIC_VECTOR(31 downto 0);
        quantity : out STD_LOGIC_VECTOR(31 downto 0);
        timestamp : out STD_LOGIC_VECTOR(63 downto 0);
        data_out_valid : out STD_LOGIC
    );
end market_data_parser;

architecture Behavioral of market_data_parser is
    
    type state_type is (IDLE, HEADER, SYMBOL, PRICE, QUANTITY, TIMESTAMP, DONE);
    signal state : state_type := IDLE;
    
    signal temp_symbol : unsigned(31 downto 0) := (others => '0');
    signal temp_price : unsigned(31 downto 0) := (others => '0');
    signal temp_quantity : unsigned(31 downto 0) := (others => '0');
    signal temp_timestamp : unsigned(63 downto 0) := (others => '0');
    
    signal byte_count : integer := 0;
    
begin

process(clk, rst_n)
begin
    if rst_n = '0' then
        state <= IDLE;
        data_out_valid <= '0';
        byte_count <= 0;
        
    elsif rising_edge(clk) then
        case state is
            when IDLE =>
                data_out_valid <= '0';
                if data_valid = '1' and data_in = x"FF" then -- Magic byte
                    state <= HEADER;
                    byte_count <= 0;
                end if;
                
            when HEADER =>
                if data_valid = '1' then
                    if data_in = x"01" then -- Market data message
                        state <= SYMBOL;
                        byte_count <= 0;
                    end if;
                end if;
                
            when SYMBOL =>
                if data_valid = '1' then
                    temp_symbol <= shift_left(temp_symbol, 8) or unsigned(data_in);
                    byte_count <= byte_count + 1;
                    if byte_count = 3 then
                        state <= PRICE;
                        byte_count <= 0;
                    end if;
                end if;
                
            when PRICE =>
                if data_valid = '1' then
                    temp_price <= shift_left(temp_price, 8) or unsigned(data_in);
                    byte_count <= byte_count + 1;
                    if byte_count = 3 then
                        state <= QUANTITY;
                        byte_count <= 0;
                    end if;
                end if;
                
            when QUANTITY =>
                if data_valid = '1' then
                    temp_quantity <= shift_left(temp_quantity, 8) or unsigned(data_in);
                    byte_count <= byte_count + 1;
                    if byte_count = 3 then
                        state <= TIMESTAMP;
                        byte_count <= 0;
                    end if;
                end if;
                
            when TIMESTAMP =>
                if data_valid = '1' then
                    temp_timestamp <= shift_left(temp_timestamp, 8) or unsigned(data_in);
                    byte_count <= byte_count + 1;
                    if byte_count = 7 then
                        state <= DONE;
                    end if;
                end if;
                
            when DONE =>
                symbol_id <= std_logic_vector(temp_symbol);
                price <= std_logic_vector(temp_price);
                quantity <= std_logic_vector(temp_quantity);
                timestamp <= std_logic_vector(temp_timestamp);
                data_out_valid <= '1';
                state <= IDLE;
                
        end case;
    end if;
end process;

end Behavioral;
```

### 訂單簿維護 (HLS)

```cpp
// orderbook_fpga.cpp

#include <ap_int.h>

#define MAX_PRICE_LEVELS 1000

struct PriceLevel {
    ap_uint<32> price;
    ap_uint<32> total_quantity;
    ap_uint<16> num_orders;
};

// 在 FPGA 中維護訂單簿
void update_orderbook(
    ap_uint<32> price,
    ap_uint<32> quantity,
    ap_uint<1> is_buy,
    ap_uint<1> is_add,
    PriceLevel bid_levels[MAX_PRICE_LEVELS],
    PriceLevel ask_levels[MAX_PRICE_LEVELS],
    ap_uint<32> *best_bid,
    ap_uint<32> *best_ask
) {
    #pragma HLS INTERFACE m_axi port=bid_levels offset=slave bundle=gmem0
    #pragma HLS INTERFACE m_axi port=ask_levels offset=slave bundle=gmem1
    #pragma HLS INTERFACE s_axilite port=price
    #pragma HLS INTERFACE s_axilite port=quantity
    #pragma HLS INTERFACE s_axilite port=is_buy
    #pragma HLS INTERFACE s_axilite port=is_add
    #pragma HLS INTERFACE s_axilite port=best_bid
    #pragma HLS INTERFACE s_axilite port=best_ask
    #pragma HLS INTERFACE s_axilite port=return
    
    PriceLevel *levels = is_buy ? bid_levels : ask_levels;
    
    // 尋找價格等級
    FIND_LEVEL: for (int i = 0; i < MAX_PRICE_LEVELS; i++) {
        #pragma HLS PIPELINE II=1
        
        if (levels[i].price == price) {
            // 找到對應價格
            if (is_add) {
                levels[i].total_quantity += quantity;
                levels[i].num_orders += 1;
            } else {
                levels[i].total_quantity -= quantity;
                levels[i].num_orders -= 1;
            }
            break;
        }
        else if (levels[i].price == 0) {
            // 新價格等級
            if (is_add) {
                levels[i].price = price;
                levels[i].total_quantity = quantity;
                levels[i].num_orders = 1;
            }
            break;
        }
    }
    
    // 更新最佳買賣價
    ap_uint<32> best = 0;
    UPDATE_BEST: for (int i = 0; i < MAX_PRICE_LEVELS; i++) {
        #pragma HLS PIPELINE II=1
        
        if (levels[i].price != 0 && levels[i].total_quantity > 0) {
            if (is_buy) {
                if (levels[i].price > best) best = levels[i].price;
            } else {
                if (best == 0 || levels[i].price < best) best = levels[i].price;
            }
        }
    }
    
    if (is_buy) {
        *best_bid = best;
    } else {
        *best_ask = best;
    }
}
```

---

## 11. CPU-FPGA 通訊

### PCIe DMA

```c
// fpga_pcie.h - CPU 端 PCIe 驅動

#include <stdint.h>

// ============ FPGA 記憶體映射 ============
#define FPGA_BAR0_SIZE (64 * 1024 * 1024)  // 64MB

typedef struct {
    int fd;
    void *bar0;
    size_t bar0_size;
} FPGADevice;

// 打開 FPGA 設備
FPGADevice* fpga_open(const char *device_path) {
    FPGADevice *dev = malloc(sizeof(FPGADevice));
    
    dev->fd = open(device_path, O_RDWR | O_SYNC);
    if (dev->fd < 0) {
        free(dev);
        return NULL;
    }
    
    // mmap BAR0
    dev->bar0_size = FPGA_BAR0_SIZE;
    dev->bar0 = mmap(NULL, dev->bar0_size,
                     PROT_READ | PROT_WRITE,
                     MAP_SHARED,
                     dev->fd, 0);
    
    if (dev->bar0 == MAP_FAILED) {
        close(dev->fd);
        free(dev);
        return NULL;
    }
    
    return dev;
}

// 寫入暫存器
void fpga_write_reg(FPGADevice *dev, uint32_t offset, uint32_t value) {
    volatile uint32_t *reg = (uint32_t*)((uint8_t*)dev->bar0 + offset);
    *reg = value;
    __sync_synchronize();  // Memory barrier
}

// 讀取暫存器
uint32_t fpga_read_reg(FPGADevice *dev, uint32_t offset) {
    volatile uint32_t *reg = (uint32_t*)((uint8_t*)dev->bar0 + offset);
    __sync_synchronize();
    return *reg;
}

// DMA 傳輸
int fpga_dma_transfer(FPGADevice *dev,
                      void *cpu_buffer,
                      uint64_t fpga_addr,
                      size_t size,
                      int direction) {
    // 設定 DMA 控制暫存器
    fpga_write_reg(dev, 0x00, (uint32_t)fpga_addr);          // FPGA 地址
    fpga_write_reg(dev, 0x04, (uint32_t)((uint64_t)cpu_buffer)); // CPU 地址
    fpga_write_reg(dev, 0x08, size);                         // 大小
    fpga_write_reg(dev, 0x0C, direction);                    // 方向 (0=讀, 1=寫)
    fpga_write_reg(dev, 0x10, 1);                            // 啟動
    
    // 等待完成
    while (fpga_read_reg(dev, 0x14) == 0) {
        __builtin_ia32_pause();
    }
    
    return 0;
}

// ============ 高層次 API ============
typedef struct {
    uint64_t order_id;
    uint32_t price;
    uint32_t quantity;
    uint8_t is_buy;
} __attribute__((packed)) Order;

// 發送訂單到 FPGA
void fpga_send_order(FPGADevice *dev, const Order *order) {
    // 方法 1: 直接寫入共享記憶體
    Order *fpga_order = (Order*)((uint8_t*)dev->bar0 + 0x1000);
    *fpga_order = *order;
    
    // 觸發處理
    fpga_write_reg(dev, 0x100, 1);
    
    // 方法 2: 使用 DMA
    // fpga_dma_transfer(dev, (void*)order, 0x1000, sizeof(Order), 1);
}

// 從 FPGA 讀取結果
int fpga_read_result(FPGADevice *dev, Order *result) {
    // 檢查是否有結果
    if (fpga_read_reg(dev, 0x104) == 0) {
        return 0;  // 無結果
    }
    
    // 讀取結果
    Order *fpga_result = (Order*)((uint8_t*)dev->bar0 + 0x2000);
    *result = *fpga_result;
    
    // 清除標誌
    fpga_write_reg(dev, 0x104, 0);
    
    return 1;
}
```

### 環形緩衝區通訊

```c
// ============ 無鎖環形緩衝區 (CPU-FPGA) ============
typedef struct {
    Order *data;
    volatile uint32_t *write_ptr;  // FPGA 寫入
    volatile uint32_t *read_ptr;   // CPU 讀取
    uint32_t capacity;
    uint32_t mask;
} FPGARingBuffer;

FPGARingBuffer* create_fpga_ringbuffer(FPGADevice *dev,
                                       uint32_t offset,
                                       uint32_t capacity) {
    FPGARingBuffer *rb = malloc(sizeof(FPGARingBuffer));
    
    rb->capacity = capacity;
    rb->mask = capacity - 1;
    
    // 映射到 FPGA 記憶體
    rb->data = (Order*)((uint8_t*)dev->bar0 + offset);
    rb->write_ptr = (uint32_t*)((uint8_t*)dev->bar0 + offset + capacity * sizeof(Order));
    rb->read_ptr = (uint32_t*)((uint8_t*)dev->bar0 + offset + capacity * sizeof(Order) + 4);
    
    *rb->write_ptr = 0;
    *rb->read_ptr = 0;
    
    return rb;
}

// CPU 端讀取（FPGA 寫入的資料）
int fpga_rb_pop(FPGARingBuffer *rb, Order *order) {
    uint32_t read = *rb->read_ptr;
    uint32_t write = *rb->write_ptr;
    
    if (read == write) {
        return 0;  // Empty
    }
    
    *order = rb->data[read & rb->mask];
    
    __sync_synchronize();
    *rb->read_ptr = read + 1;
    
    return 1;
}

// FPGA 端寫入範例 (Verilog)
/*
reg [31:0] write_ptr;
reg [31:0] read_ptr;

always @(posedge clk) begin
    if (new_order_valid) begin
        // 寫入資料
        mem[write_ptr & MASK] <= new_order;
        write_ptr <= write_ptr + 1;
    end
end
*/
```

---

## 12. 完整 HFT 系統架構

### 架構圖

```
┌─────────────────────────────────────────────────────────┐
│                      網路層                             │
├─────────────────────────────────────────────────────────┤
│  NIC (Mellanox/Solarflare)                             │
│  - DPDK/RDMA/AF_XDP                                    │
│  - 硬體時間戳                                           │
│  - RSS/Flow Director                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│                    FPGA 層                              │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐ │
│  │ Feed Handler │  │ Order Parser  │  │  Validator   │ │
│  │  (1-wire)    │  │   (FIX/FAST)  │  │  (Risk Check)│ │
│  └──────┬───────┘  └───────┬───────┘  └──────┬───────┘ │
│         │                   │                 │         │
│  ┌──────▼──────────────────▼─────────────────▼───────┐ │
│  │           訂單簿 & 策略引擎 (FPGA)                 │ │
│  │  - Tick-to-Trade < 500ns                          │ │
│  └───────────────────────┬───────────────────────────┘ │
└──────────────────────────┼─────────────────────────────┘
                           │ PCIe DMA
┌──────────────────────────▼─────────────────────────────┐
│                     CPU 層                              │
├─────────────────────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────────┐  ┌──────────────────┐ │
│  │ 複雜策略   │  │  風險管理   │  │    監控/日誌     │ │
│  │ (ML/統計)  │  │  (Position)  │  │                  │ │
│  └────────────┘  └─────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 混合系統實作

```c
// hybrid_trading_system.c

#include "fpga_pcie.h"
#include <pthread.h>
#include <rte_eal.h>
#include <rte_ethdev.h>

// ============ 全局資料結構 ============
typedef struct {
    FPGADevice *fpga;
    uint16_t dpdk_port;
    FPGARingBuffer *order_rb;
    FPGARingBuffer *market_data_rb;
} TradingSystem;

// ============ DPDK 接收執行緒 ============
void* dpdk_rx_thread(void *arg) {
    TradingSystem *sys = (TradingSystem*)arg;
    struct rte_mbuf *bufs[32];
    
    // 綁定到 CPU 2
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(2, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    
    printf("DPDK RX thread started\n");
    
    while (1) {
        uint16_t nb_rx = rte_eth_rx_burst(sys->dpdk_port, 0, bufs, 32);
        
        for (uint16_t i = 0; i < nb_rx; i++) {
            uint8_t *pkt = rte_pktmbuf_mtod(bufs[i], uint8_t*);
            uint16_t len = rte_pktmbuf_pkt_len(bufs[i]);
            
            // 發送到 FPGA 處理
            fpga_dma_transfer(sys->fpga, pkt, 0x10000, len, 1);
            
            rte_pktmbuf_free(bufs[i]);
        }
    }
    
    return NULL;
}

// ============ FPGA 結果處理執行緒 ============
void* fpga_result_thread(void *arg) {
    TradingSystem *sys = (TradingSystem*)arg;
    Order order;
    
    // 綁定到 CPU 3
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(3, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    
    printf("FPGA result thread started\n");
    
    while (1) {
        if (fpga_rb_pop(sys->order_rb, &order)) {
            // FPGA 已處理的訂單
            printf("Order from FPGA: ID=%lu, Price=%u, Qty=%u\n",
                   order.order_id, order.price, order.quantity);
            
            // 發送到交易所
            send_to_exchange(&order);
        } else {
            __builtin_ia32_pause();
        }
    }
    
    return NULL;
}

// ============ 市場資料處理執行緒 ============
void* market_data_thread(void *arg) {
    TradingSystem *sys = (TradingSystem*)arg;
    
    typedef struct {
        uint32_t symbol_id;
        uint32_t price;
        uint32_t quantity;
        uint64_t timestamp;
    } MarketData;
    
    MarketData md;
    
    // 綁定到 CPU 4
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(4, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpuset), &cpuset);
    
    printf("Market data thread started\n");
    
    while (1) {
        // 從 FPGA 讀取市場資料
        if (fpga_rb_pop(sys->market_data_rb, (Order*)&md)) {
            // 更新本地訂單簿
            update_local_orderbook(&md);
            
            // 觸發策略
            check_trading_signals(&md);
        } else {
            __builtin_ia32_pause();
        }
    }
    
    return NULL;
}

// ============ 主函數 ============
int main(int argc, char *argv[]) {
    TradingSystem sys = {0};
    
    // 1. 初始化 DPDK
    int ret = rte_eal_init(argc, argv);
    argc -= ret;
    argv += ret;
    
    // 2. 初始化 DPDK 網卡
    sys.dpdk_port = 0;
    init_dpdk_port(sys.dpdk_port);
    
    // 3. 打開 FPGA
    sys.fpga = fpga_open("/dev/xdma0_user");
    if (!sys.fpga) {
        fprintf(stderr, "Failed to open FPGA\n");
        return 1;
    }
    
    // 4. 創建環形緩衝區
    sys.order_rb = create_fpga_ringbuffer(sys.fpga, 0x100000, 4096);
    sys.market_data_rb = create_fpga_ringbuffer(sys.fpga, 0x200000, 4096);
    
    // 5. 啟動執行緒
    pthread_t dpdk_rx_tid, fpga_result_tid, market_data_tid;
    
    pthread_create(&dpdk_rx_tid, NULL, dpdk_rx_thread, &sys);
    pthread_create(&fpga_result_tid, NULL, fpga_result_thread, &sys);
    pthread_create(&market_data_tid, NULL, market_data_thread, &sys);
    
    printf("Trading system started\n");
    
    // 等待
    pthread_join(dpdk_rx_tid, NULL);
    pthread_join(fpga_result_tid, NULL);
    pthread_join(market_data_tid, NULL);
    
    return 0;
}
```

---

## 13. 效能基準測試

### 延遲測試

```c
// latency_test.c

#include <time.h>
#include <stdlib.h>

#define SAMPLES 1000000

typedef struct {
    uint64_t receive_time;
    uint64_t fpga_process_time;
    uint64_t send_time;
} LatencyRecord;

uint64_t get_ns(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000000000ULL + ts.tv_nsec;
}

void measure_latency(TradingSystem *sys) {
    LatencyRecord *records = malloc(SAMPLES * sizeof(LatencyRecord));
    
    for (int i = 0; i < SAMPLES; i++) {
        // 接收封包
        uint64_t t0 = get_ns();
        
        // 發送到 FPGA
        fpga_send_order(sys->fpga, &test_order);
        
        // FPGA 處理
        Order result;
        while (!fpga_read_result(sys->fpga, &result)) {
            __builtin_ia32_pause();
        }
        uint64_t t1 = get_ns();
        
        // 發送到交易所
        send_to_exchange(&result);
        uint64_t t2 = get_ns();
        
        records[i].receive_time = t0;
        records[i].fpga_process_time = t1 - t0;
        records[i].send_time = t2 - t1;
    }
    
    // 統計
    qsort(records, SAMPLES, sizeof(LatencyRecord), compare_latency);
    
    printf("========== Latency Statistics ==========\n");
    printf("FPGA Processing:\n");
    printf("  Min:   %lu ns\n", records[0].fpga_process_time);
    printf("  P50:   %lu ns\n", records[SAMPLES/2].fpga_process_time);
    printf("  P99:   %lu ns\n", records[SAMPLES*99/100].fpga_process_time);
    printf("  P99.9: %lu ns\n", records[SAMPLES*999/1000].fpga_process_time);
    printf("  Max:   %lu ns\n", records[SAMPLES-1].fpga_process_time);
    
    free(records);
}
```

### 吞吐量測試

```c
void measure_throughput(TradingSystem *sys) {
    const int DURATION_SEC = 10;
    uint64_t count = 0;
    
    time_t start = time(NULL);
    
    while (time(NULL) - start < DURATION_SEC) {
        Order order = generate_test_order();
        fpga_send_order(sys->fpga, &order);
        count++;
    }
    
    double rate = count / (double)DURATION_SEC;
    printf("Throughput: %.2f orders/sec\n", rate);
}
```

---

## 14. 故障排除與監控

### 監控系統

```c
// monitoring.c

typedef struct {
    atomic_uint_fast64_t packets_received;
    atomic_uint_fast64_t packets_sent;
    atomic_uint_fast64_t fpga_errors;
    atomic_uint_fast64_t orders_processed;
    atomic_uint_fast64_t latency_violations;
} SystemStats;

SystemStats g_stats = {0};

void* monitoring_thread(void *arg) {
    TradingSystem *sys = (TradingSystem*)arg;
    
    while (1) {
        sleep(1);
        
        uint64_t rx = atomic_load(&g_stats.packets_received);
        uint64_t tx = atomic_load(&g_stats.packets_sent);
        uint64_t errors = atomic_load(&g_stats.fpga_errors);
        uint64_t orders = atomic_load(&g_stats.orders_processed);
        
        printf("[Monitor] RX: %lu, TX: %lu, Orders: %lu, Errors: %lu\n",
               rx, tx, orders, errors);
        
        // 檢查 FPGA 狀態
        uint32_t fpga_status = fpga_read_reg(sys->fpga, 0x200);
        if (fpga_status & 0x80000000) {
            fprintf(stderr, "FPGA ERROR: 0x%x\n", fpga_status);
            atomic_fetch_add(&g_stats.fpga_errors, 1);
        }
        
        // 重置計數器
        atomic_store(&g_stats.packets_received, 0);
        atomic_store(&g_stats.packets_sent, 0);
        atomic_store(&g_stats.orders_processed, 0);
    }
    
    return NULL;
}
```

### 日誌系統

```c
// 高效能日誌（環形緩衝區）
#define LOG_BUFFER_SIZE (1024 * 1024)

typedef struct {
    uint64_t timestamp;
    uint32_t event_type;
    uint64_t order_id;
    uint32_t data;
} LogEntry;

typedef struct {
    LogEntry *buffer;
    atomic_uint_fast64_t write_pos;
    uint64_t mask;
} LogBuffer;

LogBuffer* create_log_buffer(void) {
    LogBuffer *lb = malloc(sizeof(LogBuffer));
    lb->buffer = aligned_alloc(4096, LOG_BUFFER_SIZE * sizeof(LogEntry));
    lb->mask = LOG_BUFFER_SIZE - 1;
    atomic_init(&lb->write_pos, 0);
    return lb;
}

void log_event(LogBuffer *lb, uint32_t event_type, uint64_t order_id, uint32_t data) {
    uint64_t pos = atomic_fetch_add(&lb->write_pos, 1);
    LogEntry *entry = &lb->buffer[pos & lb->mask];
    
    entry->timestamp = get_ns();
    entry->event_type = event_type;
    entry->order_id = order_id;
    entry->data = data;
}
```

---

## 總結

### 延遲對比

| 方案 | 延遲 | 複雜度 | 成本 |
|------|------|--------|------|
| 標準 Socket | 10-50μs | 低 | 低 |
| 優化 Socket | 5-20μs | 低 | 低 |
| AF_XDP | 1-3μs | 中 | 低 |
| DPDK | 0.5-2μs | 高 | 中 |
| RDMA | 0.3-1μs | 中 | 高 |
| FPGA | 0.1-0.5μs | 極高 | 極高 |

### 建議架構

**入門級（<10μs）：**
- 優化的 Socket + 系統調校
- AF_XDP

**進階級（<5μs）：**
- DPDK
- 硬體時間戳

**專業級（<1μs）：**
- RDMA + DPDK
- 部分 FPGA 加速

**頂級（<500ns）：**
- 全 FPGA 解決方案
- Kernel Bypass + FPGA

---

## 參考資源

- DPDK 官方文件: https://doc.dpdk.org
- RDMA Programming: https://www.rdmamojo.com
- Xilinx Vitis HLS: https://www.xilinx.com/products/design-tools/vitis.html
- Linux XDP: https://www.kernel.org/doc/html/latest/networking/af_xdp.html
