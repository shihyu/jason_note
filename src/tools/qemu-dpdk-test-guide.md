# QEMU 環境 DPDK 雙埠測試完整指南

## 目錄
1. [測試架構概述](#測試架構概述)
2. [Host 主機準備](#host-主機準備)
3. [QEMU 虛擬機配置](#qemu-虛擬機配置)
4. [Guest 虛擬機內 DPDK 設置](#guest-虛擬機內-dpdk-設置)
5. [測試場景](#測試場景)
6. [效能優化](#效能優化)
7. [故障排除](#故障排除)

---

## 測試架構概述

### 可用的測試拓撲

#### 1. 單一 VM 內部環回測試
```
┌─────────────────────────┐
│      QEMU VM            │
│  ┌──────┐    ┌──────┐  │
│  │ Port0│───►│ Port1│  │
│  └──────┘    └──────┘  │
│       DPDK App          │
└─────────────────────────┘
```

#### 2. VM 到 VM 測試
```
┌──────────┐         ┌──────────┐
│  VM1     │         │  VM2     │
│  Port0───┼────────►│  Port0   │
│  Port1◄──┼─────────┤  Port1   │
└──────────┘         └──────────┘
```

#### 3. VM 到 Host 測試（使用 vhost-user）
```
     Host                    VM
┌──────────┐         ┌──────────┐
│ OVS-DPDK │◄────────┤  DPDK    │
│  或      │ vhost-  │   App    │
│ Testpmd  │  user   │          │
└──────────┘         └──────────┘
```

---

## Host 主機準備

### 1. 安裝必要套件
```bash
# Ubuntu 20.04/22.04
sudo apt update
sudo apt install -y qemu-kvm qemu-system-x86 \
    libvirt-daemon-system libvirt-clients bridge-utils \
    cpu-checker hugepages dpdk dpdk-dev openvswitch-switch-dpdk

# 檢查虛擬化支援
kvm-ok
```

### 2. 設定大頁記憶體（Host）
```bash
# 配置 2MB 大頁
echo 4096 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 或配置 1GB 大頁（更好的效能）
echo 8 | sudo tee /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# 掛載 hugetlbfs
sudo mkdir -p /dev/hugepages
sudo mount -t hugetlbfs hugetlbfs /dev/hugepages

# 永久配置
echo "vm.nr_hugepages=4096" | sudo tee -a /etc/sysctl.conf
echo "hugetlbfs /dev/hugepages hugetlbfs defaults 0 0" | sudo tee -a /etc/fstab
```

### 3. 準備網路橋接（選項一：Linux Bridge）
```bash
# 建立兩個 Linux bridge
sudo ip link add br0 type bridge
sudo ip link add br1 type bridge
sudo ip link set br0 up
sudo ip link set br1 up

# 建立 TAP 介面
sudo ip tuntap add dev tap0 mode tap
sudo ip tuntap add dev tap1 mode tap
sudo ip link set tap0 up
sudo ip link set tap1 up

# 加入 bridge
sudo ip link set tap0 master br0
sudo ip link set tap1 master br1
```

### 4. 準備 vhost-user（選項二：高效能）
```bash
# 建立 vhost-user socket 目錄
sudo mkdir -p /tmp/vhost-sockets
sudo chmod 777 /tmp/vhost-sockets

# 使用 OVS-DPDK（可選）
sudo systemctl start openvswitch-switch
sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-init=true
sudo ovs-vsctl --no-wait set Open_vSwitch . other_config:dpdk-socket-mem="1024,1024"

# 建立 OVS bridge
sudo ovs-vsctl add-br br0 -- set bridge br0 datapath_type=netdev
sudo ovs-vsctl add-port br0 vhost-user0 -- set Interface vhost-user0 type=dpdkvhostuser
sudo ovs-vsctl add-port br0 vhost-user1 -- set Interface vhost-user1 type=dpdkvhostuser
```

---

## QEMU 虛擬機配置

### 方案 1：使用 virtio-net（簡單）

```bash
#!/bin/bash
# start_vm_virtio.sh

QEMU=/usr/bin/qemu-system-x86_64
VM_NAME="dpdk-test-vm"
MEM=4096
CORES=4
DISK="ubuntu-20.04.qcow2"

$QEMU \
  -name $VM_NAME \
  -cpu host \
  -enable-kvm \
  -m $MEM \
  -smp $CORES \
  -object memory-backend-file,id=mem,size=${MEM}M,mem-path=/dev/hugepages,share=on \
  -numa node,memdev=mem \
  -drive file=$DISK,if=virtio \
  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
  -device virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01 \
  -netdev tap,id=net1,ifname=tap1,script=no,downscript=no \
  -device virtio-net-pci,netdev=net1,mac=52:54:00:00:00:02 \
  -vnc :1 \
  -monitor telnet::4444,server,nowait
```

### 方案 2：使用 vhost-user（高效能）

```bash
#!/bin/bash
# start_vm_vhost.sh

QEMU=/usr/bin/qemu-system-x86_64
VM_NAME="dpdk-test-vm"
MEM=4096
CORES=4
DISK="ubuntu-20.04.qcow2"

$QEMU \
  -name $VM_NAME \
  -cpu host \
  -enable-kvm \
  -m $MEM \
  -smp $CORES \
  -object memory-backend-file,id=mem,size=${MEM}M,mem-path=/dev/hugepages,share=on \
  -numa node,memdev=mem \
  -drive file=$DISK,if=virtio \
  -chardev socket,id=char0,path=/tmp/vhost-sockets/vhost-user0,server \
  -netdev type=vhost-user,id=net0,chardev=char0,vhostforce \
  -device virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01,csum=off,gso=off,guest_tso4=off,guest_tso6=off,guest_ecn=off \
  -chardev socket,id=char1,path=/tmp/vhost-sockets/vhost-user1,server \
  -netdev type=vhost-user,id=net1,chardev=char1,vhostforce \
  -device virtio-net-pci,netdev=net1,mac=52:54:00:00:00:02,csum=off,gso=off,guest_tso4=off,guest_tso6=off,guest_ecn=off \
  -vnc :1 \
  -monitor telnet::4444,server,nowait
```

### 方案 3：使用 e1000/vmxnet3（相容性好）

```bash
#!/bin/bash
# start_vm_e1000.sh

QEMU=/usr/bin/qemu-system-x86_64
VM_NAME="dpdk-test-vm"

$QEMU \
  -name $VM_NAME \
  -cpu host \
  -enable-kvm \
  -m 4096 \
  -smp 4 \
  -drive file=ubuntu-20.04.qcow2,if=virtio \
  -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
  -device e1000,netdev=net0,mac=52:54:00:00:00:01 \
  -netdev tap,id=net1,ifname=tap1,script=no,downscript=no \
  -device e1000,netdev=net1,mac=52:54:00:00:00:02 \
  -vnc :1
```

### 方案 4：PCI Passthrough（最佳效能）

```bash
#!/bin/bash
# start_vm_passthrough.sh

# 首先在 Host 上解綁網卡
echo "0000:02:00.0" | sudo tee /sys/bus/pci/drivers/ixgbe/unbind
echo "0000:02:00.1" | sudo tee /sys/bus/pci/drivers/ixgbe/unbind

# 綁定到 VFIO
sudo modprobe vfio-pci
echo "8086 10fb" | sudo tee /sys/bus/pci/drivers/vfio-pci/new_id

QEMU=/usr/bin/qemu-system-x86_64

$QEMU \
  -name dpdk-test-vm \
  -cpu host \
  -enable-kvm \
  -m 4096 \
  -smp 4 \
  -mem-prealloc \
  -object memory-backend-file,id=mem,size=4096M,mem-path=/dev/hugepages,share=on \
  -numa node,memdev=mem \
  -drive file=ubuntu-20.04.qcow2,if=virtio \
  -device vfio-pci,host=0000:02:00.0 \
  -device vfio-pci,host=0000:02:00.1 \
  -vnc :1
```

---

## Guest 虛擬機內 DPDK 設置

### 1. 登入虛擬機
```bash
# 透過 VNC 連接
vncviewer localhost:5901

# 或 SSH（如果已配置網路）
ssh user@vm-ip
```

### 2. 在 Guest 內安裝 DPDK
```bash
# 安裝 DPDK
sudo apt update
sudo apt install -y dpdk dpdk-dev build-essential

# 或從源碼編譯
wget https://fast.dpdk.org/rel/dpdk-20.11.9.tar.xz
tar xf dpdk-20.11.9.tar.xz
cd dpdk-stable-20.11.9
meson build
cd build
ninja
sudo ninja install
```

### 3. Guest 內配置
```bash
# 設定大頁記憶體
echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge

# 載入驅動
sudo modprobe uio_pci_generic

# 檢查網卡
lspci | grep -i net
# 應該看到：
# 00:03.0 Ethernet controller: Red Hat, Inc. Virtio network device
# 00:04.0 Ethernet controller: Red Hat, Inc. Virtio network device

# 綁定到 DPDK
sudo dpdk-devbind.py --status
sudo dpdk-devbind.py -b uio_pci_generic 00:03.0 00:04.0
```

---

## 測試場景

### 場景 1：VM 內部環回測試

```bash
# 在 Guest 內執行
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --portmask=0x3 --nb-cores=2

# testpmd 命令
testpmd> set fwd mac
testpmd> start

# 檢查統計
testpmd> show port stats all
```

### 場景 2：VM 到 VM 測試

#### VM1 設置（發送端）
```bash
# 建立封包產生器
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --portmask=0x3 --nb-cores=2
testpmd> set fwd txonly
testpmd> set txpkts 64
testpmd> start
```

#### VM2 設置（接收端）
```bash
# 接收封包
sudo dpdk-testpmd -l 0-3 -n 4 -- -i --portmask=0x3 --nb-cores=2
testpmd> set fwd rxonly
testpmd> start
testpmd> show port stats all
```

### 場景 3：使用自定義測試程式

```c
// simple_forward.c - 簡單的雙埠轉發程式
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_cycles.h>
#include <rte_lcore.h>
#include <rte_mbuf.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

static const struct rte_eth_conf port_conf_default = {
    .rxmode = {
        .max_rx_pkt_len = RTE_ETHER_MAX_LEN,
    },
};

int main(int argc, char *argv[])
{
    struct rte_mempool *mbuf_pool;
    unsigned nb_ports;
    uint16_t portid;

    /* 初始化 EAL */
    int ret = rte_eal_init(argc, argv);
    if (ret < 0)
        rte_exit(EXIT_FAILURE, "EAL initialization failed\n");

    nb_ports = rte_eth_dev_count_avail();
    printf("Number of ports available: %u\n", nb_ports);

    if (nb_ports < 2)
        rte_exit(EXIT_FAILURE, "Need at least 2 ports\n");

    /* 建立 mbuf pool */
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, rte_socket_id());

    if (mbuf_pool == NULL)
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");

    /* 初始化所有埠 */
    for (portid = 0; portid < nb_ports && portid < 2; portid++) {
        /* 配置埠 */
        ret = rte_eth_dev_configure(portid, 1, 1, &port_conf_default);
        if (ret != 0)
            rte_exit(EXIT_FAILURE, "Port %u configuration failed\n", portid);

        /* 設置 RX 佇列 */
        ret = rte_eth_rx_queue_setup(portid, 0, RX_RING_SIZE,
                rte_eth_dev_socket_id(portid), NULL, mbuf_pool);
        if (ret < 0)
            rte_exit(EXIT_FAILURE, "RX queue setup failed\n");

        /* 設置 TX 佇列 */
        ret = rte_eth_tx_queue_setup(portid, 0, TX_RING_SIZE,
                rte_eth_dev_socket_id(portid), NULL);
        if (ret < 0)
            rte_exit(EXIT_FAILURE, "TX queue setup failed\n");

        /* 啟動埠 */
        ret = rte_eth_dev_start(portid);
        if (ret < 0)
            rte_exit(EXIT_FAILURE, "Port %u start failed\n", portid);

        printf("Port %u started successfully\n", portid);
    }

    printf("\nStarting packet forwarding...\n");

    /* 主迴圈 */
    for (;;) {
        struct rte_mbuf *bufs[BURST_SIZE];
        uint16_t nb_rx, nb_tx;

        /* Port 0 -> Port 1 */
        nb_rx = rte_eth_rx_burst(0, 0, bufs, BURST_SIZE);
        if (nb_rx > 0) {
            nb_tx = rte_eth_tx_burst(1, 0, bufs, nb_rx);
            /* 釋放未發送的封包 */
            if (unlikely(nb_tx < nb_rx)) {
                for (uint16_t i = nb_tx; i < nb_rx; i++)
                    rte_pktmbuf_free(bufs[i]);
            }
        }

        /* Port 1 -> Port 0 */
        nb_rx = rte_eth_rx_burst(1, 0, bufs, BURST_SIZE);
        if (nb_rx > 0) {
            nb_tx = rte_eth_tx_burst(0, 0, bufs, nb_rx);
            /* 釋放未發送的封包 */
            if (unlikely(nb_tx < nb_rx)) {
                for (uint16_t i = nb_tx; i < nb_rx; i++)
                    rte_pktmbuf_free(bufs[i]);
            }
        }
    }

    return 0;
}
```

編譯和執行：
```bash
# 編譯
gcc -o simple_forward simple_forward.c \
    $(pkg-config --cflags --libs libdpdk)

# 執行
sudo ./simple_forward -l 0-3 -n 4
```

---

## 效能優化

### 1. QEMU CPU 優化
```bash
# 使用 CPU pinning
taskset -c 0-3 qemu-system-x86_64 ...

# QEMU 命令行加入
-cpu host,+x2apic,+tsc-deadline \
-realtime mlock=on \
-rtc base=localtime,driftfix=slew
```

### 2. Guest 內核優化
```bash
# 關閉不必要的服務
sudo systemctl stop NetworkManager
sudo systemctl stop firewalld

# CPU 頻率設定
sudo cpupower frequency-set -g performance

# 中斷親和性
echo 2 > /proc/irq/24/smp_affinity_list
```

### 3. virtio 優化參數
```bash
# QEMU 啟動參數
-device virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01,\
  csum=off,gso=off,guest_tso4=off,guest_tso6=off,guest_ecn=off,\
  mq=on,vectors=9,packed=on
```

### 4. vhost-user 多佇列
```bash
# Host 端 testpmd
sudo dpdk-testpmd -l 0-3 -n 4 \
  --vdev 'net_vhost0,iface=/tmp/vhost-user0,queues=2' \
  --vdev 'net_vhost1,iface=/tmp/vhost-user1,queues=2' \
  -- -i --nb-cores=2 --rxq=2 --txq=2

# QEMU 參數
-chardev socket,id=char0,path=/tmp/vhost-user0,server \
-netdev type=vhost-user,id=net0,chardev=char0,vhostforce,queues=2 \
-device virtio-net-pci,netdev=net0,mac=52:54:00:00:00:01,mq=on,vectors=6
```

---

## 效能測試結果參考

### 測試環境
- Host: Intel Xeon E5-2680 v4, 64GB RAM
- Guest: 4 vCPUs, 4GB RAM
- DPDK: 20.11 LTS

### 效能數據

| 配置 | 封包大小 | 吞吐量 (Mpps) | 延遲 (μs) |
|------|---------|---------------|-----------|
| virtio-net | 64B | 2.5 | 40-60 |
| virtio-net | 1518B | 0.8 | 30-50 |
| vhost-user | 64B | 8.5 | 15-25 |
| vhost-user | 1518B | 3.2 | 10-20 |
| SR-IOV VF | 64B | 12.0 | 8-12 |
| SR-IOV VF | 1518B | 4.5 | 6-10 |

---

## 故障排除

### 問題 1：虛擬機內看不到網卡
```bash
# 檢查 QEMU 進程
ps aux | grep qemu

# 檢查網卡是否被識別
lspci -v | grep -i ethernet

# 確認驅動載入
lsmod | grep virtio
```

### 問題 2：DPDK 初始化失敗
```bash
# 檢查大頁配置
cat /proc/meminfo | grep Huge

# 檢查 IOMMU
dmesg | grep -i iommu

# 權限問題
sudo chmod 666 /dev/vfio/*
```

### 問題 3：效能不佳
```bash
# Host 端檢查
# CPU 是否超載
htop

# 檢查 KVM 模組
lsmod | grep kvm

# Guest 端檢查
# 確認使用 virtio-net-pci
ethtool -i eth0
```

### 問題 4：vhost-user 連接失敗
```bash
# 檢查 socket 文件
ls -la /tmp/vhost-sockets/

# 檢查 OVS 狀態（如果使用）
sudo ovs-vsctl show

# 權限設定
sudo chmod 777 /tmp/vhost-sockets
```

---

## 進階測試腳本

### 自動化測試腳本
```bash
#!/bin/bash
# auto_test.sh

# 啟動 VM
./start_vm_vhost.sh &
VM_PID=$!
sleep 30

# SSH 到 VM 執行測試
ssh user@192.168.122.100 << 'EOF'
  # 設定 DPDK
  echo 1024 | sudo tee /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages
  sudo modprobe uio_pci_generic
  sudo dpdk-devbind.py -b uio_pci_generic 00:03.0 00:04.0
  
  # 執行測試
  sudo timeout 60 dpdk-testpmd -l 0-3 -n 4 -- \
    -i --portmask=0x3 --nb-cores=2 --forward-mode=mac
EOF

# 收集結果
echo "Test completed"

# 停止 VM
kill $VM_PID
```

### 效能監控腳本
```bash
#!/bin/bash
# monitor.sh

while true; do
    clear
    echo "=== VM Network Performance ==="
    
    # Host 端監控
    echo "Host CPU:"
    mpstat 1 1 | tail -2
    
    # VM 內監控（透過 SSH）
    echo -e "\nVM Statistics:"
    ssh user@vm-ip "cat /proc/net/dev | grep -E 'eth|virtio'"
    
    sleep 2
done
```

---

## 總結

QEMU 提供了多種方式來測試 DPDK 雙埠收發：

### 優缺點比較

| 方式 | 優點 | 缺點 | 適用場景 |
|------|------|------|----------|
| **virtio-net** | 簡單易用、穩定 | 效能一般 | 功能測試、開發 |
| **vhost-user** | 效能好、延遲低 | 配置複雜 | 效能測試 |
| **SR-IOV/直通** | 接近原生效能 | 需要硬體支援 | 生產環境測試 |
| **e1000** | 相容性最好 | 效能最差 | 相容性測試 |

### 建議

1. **開發測試**：使用 virtio-net，簡單快速
2. **效能測試**：使用 vhost-user 或 SR-IOV
3. **自動化測試**：結合 libvirt 管理 VM
4. **大規模測試**：使用容器化 DPDK（Docker）

QEMU 是測試 DPDK 的優秀平臺，特別適合開發和驗證階段！