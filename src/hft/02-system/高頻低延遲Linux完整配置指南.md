# 高頻/低延遲 Linux C/C++ 完整配置指南

> **目標**：硬體 + 系統 + 程式碼 = 極致低延遲  
> **適用**：HFT、DPDK、超低延遲交易系統

---

## 🎯 三層架構總覽

```
┌──────────────────────────────────────┐
│  1. 硬體層（Hardware）               │
│  - 高階網卡 + BIOS 設定              │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  2. 系統層（OS/Kernel）              │
│  - GRUB 參數 + Runtime 設定          │
└──────────────┬───────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  3. 應用層（C/C++ Code）             │
│  - DPDK + Lock-free + 記憶體管理     │
└──────────────────────────────────────┘
```

---

## 1️⃣ 硬體層配置

### BIOS 設定（開機前）

```
┌──────────────────────────────┐
│ 必須關閉                     │
├──────────────────────────────┤
│ ✓ Hyper-Threading (SMT)      │
│ ✓ C-States (省電模式)        │
│ ✓ P-States (動態頻率)        │
│ ✓ Turbo Boost                │
│ ✓ NUMA Node Interleaving     │
└──────────────────────────────┘

┌──────────────────────────────┐
│ 必須開啟                     │
├──────────────────────────────┤
│ ✓ VT-d / IOMMU               │
│ ✓ Performance Mode           │
│ ✓ ACS (Access Control)       │
└──────────────────────────────┘
```

### 網卡要求

```
推薦型號：
- Intel X710 / XL710
- Mellanox ConnectX-5/6

必備功能：
✓ SR-IOV
✓ Flow Director / Flow Steering
✓ RSS (Receive Side Scaling)
✓ 32+ RX/TX queues
✓ DPDK PMD 支援
```

---

## 2️⃣ 系統層配置

### A. GRUB 啟動參數

編輯 `/etc/default/grub`：

```bash
GRUB_CMDLINE_LINUX="
  isolcpus=1-7
  nohz_full=1-7
  rcu_nocbs=1-7
  rcu_nocb_poll
  intel_pstate=disable
  intel_idle.max_cstate=0
  processor.max_cstate=0
  idle=poll
  nosoftlockup
  nmi_watchdog=0
  mce=off
  intel_iommu=on
  iommu=pt
  default_hugepagesz=1G
  hugepagesz=1G
  hugepages=8
  transparent_hugepage=never
"
```

更新並重啟：

```bash
sudo update-grub
sudo reboot
```

### B. 系統服務管理

```bash
# 關閉不必要服務
systemctl stop irqbalance
systemctl disable irqbalance
systemctl stop cpupower
systemctl mask systemd-journald.service

# 鎖定 CPU 頻率
cpupower frequency-set -g performance
for cpu in /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor; do
    echo performance > $cpu
done
```

### C. IRQ 親和性設定（現代更新）

**重要觀念轉變**：在 Kernel Bypass 模式下，不再強調「把 IRQ 綁到哪個 CPU」，而是強調「避開 Polling CPU」。

#### 為什麼 IRQ 綁定觀念改變了？

1. **自動化**：高階網卡（如 Mellanox ConnectX-7+）在 Bypass 模式下會自動關閉硬體中斷
2. **避開策略**：重點是「確保中斷不要出現在 Polling 核心上」
3. **系統中斷處理**：將所有系統中斷（磁碟、計時器）綁定到非交易核心（通常是 CPU 0）

```bash
#!/bin/bash
# irq_binding.sh - 將所有系統中斷綁定到 CPU 0

# 策略：讓所有中斷都在 CPU 0 處理，保護 1-7 號核心
for irq in /proc/irq/*/smp_affinity; do
    # 跳過 default_smp_affinity
    if [[ $irq == *"default"* ]]; then
        continue
    fi

    # 0x01 = 二進位 0001 = CPU 0
    echo 1 > $irq 2>/dev/null
done

# 驗證：所有中斷應該只在 CPU 0 上增長
watch -n 1 'cat /proc/interrupts | head -20'
```

#### NUMA 拓撲對齊（關鍵！）

```bash
# 1. 檢查網卡在哪個 NUMA Node
lspci -vvv -s 0000:03:00.0 | grep "NUMA node"
# 輸出範例：NUMA node: 0

# 2. 檢查 CPU 拓撲
lstopo-no-graphics --of txt
# 或
numactl --hardware

# 3. 確保你的 Polling 程式運行在同一個 NUMA Node
# 例如網卡在 NUMA 0，則使用 CPU 0-11 (假設 12 核/socket)
```

**關鍵**：跨 NUMA 存取的延遲會毀掉所有優化效果！

### E. Kernel Bypass 關鍵概念

#### 為什麼 IRQ 綁定變少了？

```
傳統觀念 (舊)           現代 Bypass 模式 (新)
─────────────────────  ──────────────────────────
把 IRQ 綁到特定 CPU    → 避開 Polling CPU，關閉不必要的中斷
需要手動調整 affinity  → 高階網卡自動關閉硬體中斷
```

**核心原則**：在 Kernel Bypass 模式下，重點不是「把中斷綁到哪」，而是「確保中斷不要出現在 Polling 核心上」。

**「靜默/關閉中斷」的意思**：網卡在 Bypass 模式下不會產生硬體中斷通知 CPU，因為我們使用 Busy Polling（不斷主動輪詢）取代被動等待中斷。

#### 系統配置四要素

**1. 軟體層級：捨棄 poll()**

```cpp
// ❌ 不要使用
struct pollfd fds[1];
poll(fds, 1, timeout);

// ✅ 改用 DPDK
rte_eth_rx_burst(port, queue_id, bufs, BURST_SIZE);
```

**2. 作業系統層級：核心隔離**

```bash
# 必要操作：在 GRUB 設定中加入
isolcpus=X,Y        # 防止排程器使用這些核心
nohz_full=X,Y       # 關閉該核心的 tick
```

**3. IRQ 管理：綁定到非交易核心**

```bash
# 將所有系統中斷綁定到 CPU 0（非 Polling 核心）
for irq in /proc/irq/*/smp_affinity; do
    echo 1 > $irq 2>/dev/null
done
```

**4. 硬體對齊：NUMA 拓撲**

```bash
# 檢查網卡在哪個 NUMA Node
lstopo-no-graphics --of txt

# 或使用
lspci -vvv -s <PCI_ADDR> | grep "NUMA node"

# 關鍵：Polling 程式必須運行在同一個 NUMA Node 的 CPU 上
```

### D. DPDK 環境準備

```bash
#!/bin/bash
# dpdk_setup.sh

# 1. 載入 VFIO 模組
modprobe vfio-pci
echo 1 > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# 2. 查看網卡 PCI 位址
lspci | grep Ethernet
# 假設輸出：0000:03:00.0 Ethernet controller: Intel Corporation

# 3. 解綁原驅動
echo "0000:03:00.0" > /sys/bus/pci/drivers/i40e/unbind

# 4. 綁定到 vfio-pci（Intel X710 的 vendor:device ID）
echo "8086 1572" > /sys/bus/pci/drivers/vfio-pci/new_id
echo "0000:03:00.0" > /sys/bus/pci/drivers/vfio-pci/bind

# 5. 掛載 Hugepages
mkdir -p /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
echo 8 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# 6. 驗證
cat /proc/meminfo | grep Huge
```

---

## 2.5 DPDK vs 傳統網路編程

### poll() vs recvfrom() - 傳統 Socket 的兩階段流程

在傳統 Linux 網路編程中，`poll()` 和 `recvfrom()` 是**兩個不同的系統呼叫**，各司其職：

```
┌──────────────────────────────────────────────┐
│ 傳統 Socket 兩階段流程                       │
├──────────────────────────────────────────────┤
│                                              │
│  1. poll() / select() / epoll()              │
│     └─ 監控 socket 狀態                      │
│     └─ 等待「有資料可讀」事件                │
│     └─ 可同時監控多個 socket                 │
│     └─ 阻塞或非阻塞模式                      │
│                                              │
│  2. recvfrom() / recv() / read()             │
│     └─ 實際接收資料                          │
│     └─ 從 kernel buffer 拷貝到 user buffer   │
│     └─ 一次處理一個 socket                   │
│                                              │
└──────────────────────────────────────────────┘
```

#### 傳統方式的典型程式碼

```c
#include <sys/socket.h>
#include <poll.h>

int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
bind(sockfd, ...);

struct pollfd fds[1];
fds[0].fd = sockfd;
fds[0].events = POLLIN;  // 監控「可讀」事件

while (1) {
    // 階段 1：等待 socket 有資料（可能阻塞）
    int ret = poll(fds, 1, 1000);  // timeout 1000ms

    if (ret > 0 && (fds[0].revents & POLLIN)) {
        // 階段 2：實際接收資料
        char buffer[1500];
        struct sockaddr_in src_addr;
        socklen_t addrlen = sizeof(src_addr);

        ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                             (struct sockaddr*)&src_addr, &addrlen);

        if (n > 0) {
            process_data(buffer, n);
        }
    }
}
```

#### recvfrom() 可以不需要 poll() 嗎？

**答案：可以！** `poll()` 不是必須的，有多種使用方式：

**方式 1：純阻塞模式（最簡單）**

```c
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
bind(sockfd, ...);

while (1) {
    char buffer[1500];
    // 直接呼叫 recvfrom，會一直等待直到有資料
    ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);

    if (n > 0) {
        process_data(buffer, n);
    }
}
```

- ✅ 最簡單，不需要 poll
- ❌ 會一直阻塞，無法設定 timeout
- ❌ 無法處理多個 socket

**方式 2：非阻塞 + Busy Polling（模仿 DPDK，但效率差）**

```c
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
bind(sockfd, ...);

// 設定為非阻塞模式
int flags = fcntl(sockfd, F_GETFL, 0);
fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

while (1) {
    char buffer[1500];
    // ⚠️ 每次都是系統呼叫，立即回傳
    ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);

    if (n > 0) {
        // 有封包，處理資料
        process_data(buffer, n);
    } else if (n < 0 && errno == EAGAIN) {
        // 沒封包，但馬上又進入下一次迴圈
        // ⚠️ 每次迴圈都要進 kernel 檢查是否有封包
        continue;
    }
}
```

**重點：recvfrom 在非阻塞模式下的行為**

```
每次呼叫 recvfrom() 都會：
  1. 進入 kernel space            (系統呼叫開銷)
  2. 檢查 socket buffer 是否有資料
  3. 如果有資料 → 拷貝到 user buffer，返回資料長度
  4. 如果沒資料 → 返回 -1，設定 errno = EAGAIN
  5. 回到 user space              (系統呼叫開銷)

問題：每次迴圈都要這樣做，即使 99% 的時間沒資料！
```

- ✅ 不會阻塞，有資料立即處理
- ❌ **瘋狂系統呼叫**，每次迴圈都要進 kernel 檢查
- ❌ CPU 100%，但大部分時間浪費在進出 kernel

**方式 3：poll() + recvfrom()（推薦）**

```c
struct pollfd fds[1];
fds[0].fd = sockfd;
fds[0].events = POLLIN;

while (1) {
    // 只呼叫一次 poll 等待
    int ret = poll(fds, 1, 1000);

    if (ret > 0) {
        // 確定有資料才呼叫 recvfrom
        ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0, NULL, NULL);
        process_data(buffer, n);
    }
}
```

- ✅ 有資料時才讀取，減少無效系統呼叫
- ✅ 可設定 timeout
- ✅ 可同時監控多個 socket

#### 為什麼需要 poll()？

| 場景 | 不用 poll 的問題 | 用 poll 的好處 |
|------|-----------------|---------------|
| 單一 socket | `recvfrom()` 會一直阻塞 | 可設定 timeout |
| 多個 socket | 不知道該讀哪個，需要逐一輪詢 | 一次監控多個，知道哪個有資料 |
| 非阻塞模式 | 瘋狂系統呼叫浪費 CPU | 只在有資料時才呼叫 recvfrom |

#### recvfrom() 系統呼叫行為詳解

**關鍵問題：recvfrom 要每次系統呼叫看是否有封包嗎？**

**答案：取決於模式！**

| 模式 | 行為 | 系統呼叫頻率 | 適用場景 |
|------|------|-------------|---------|
| **阻塞模式** | 呼叫一次，等到有資料才返回 | 有資料時才返回 | 簡單應用 |
| **非阻塞模式** | 每次呼叫立即返回 | **每次迴圈都要系統呼叫** | Busy polling (效率差) |
| **poll + recvfrom** | poll 等待，確定有資料才 recvfrom | 有資料時才 recvfrom | 推薦 |

**詳細行為對比：**

```
阻塞模式：
  recvfrom(sockfd, ...);  ← 呼叫一次
  ↓
  ⏸️ 在 kernel 內等待（程式暫停）
  ↓
  📦 有封包到達
  ↓
  ✅ 拷貝資料，返回
  ↓
  處理資料
  ↓
  recvfrom(sockfd, ...);  ← 再次呼叫，又會等待

  系統呼叫次數：等於封包數量（最少）

非阻塞模式（Busy Polling）：
  while (1) {
    recvfrom(sockfd, ...);  ← 每次迴圈都系統呼叫
    ↓
    立即檢查 socket buffer
    ↓
    沒資料？返回 EAGAIN
    ↓
    recvfrom(sockfd, ...);  ← 又是系統呼叫
    ↓
    沒資料？返回 EAGAIN
    ↓
    recvfrom(sockfd, ...);  ← 又是系統呼叫
    ...（可能重複數百萬次）
    ↓
    📦 有封包到達
    ↓
    拷貝資料，返回
  }

  系統呼叫次數：可能數百萬次/秒（極多！）

poll + recvfrom：
  while (1) {
    poll(fds, ...);         ← 系統呼叫，等待事件
    ↓
    ⏸️ 在 kernel 內等待
    ↓
    📦 有封包到達
    ↓
    ✅ 返回「有資料可讀」
    ↓
    recvfrom(sockfd, ...);  ← 確定有資料才系統呼叫
    ↓
    拷貝資料，返回
  }

  系統呼叫次數：約 2 × 封包數量（適中）
```

**關鍵差異總結：**

```
┌─────────────────────────────────────────────────────┐
│ 非阻塞 recvfrom busy polling 為什麼這麼差？         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  while (1) {                                        │
│    recvfrom(...)  ← 系統呼叫 1                      │
│    recvfrom(...)  ← 系統呼叫 2                      │
│    recvfrom(...)  ← 系統呼叫 3                      │
│    ...                                              │
│    recvfrom(...)  ← 系統呼叫 1000000                │
│  }                                                  │
│                                                     │
│  每次都要：                                         │
│  1. user → kernel 切換     (50-100 cycles)          │
│  2. 檢查 socket buffer     (20-50 cycles)           │
│  3. kernel → user 切換     (50-100 cycles)          │
│                                                     │
│  即使沒封包，也要這樣做！                           │
└─────────────────────────────────────────────────────┘
```

---

#### 對比：三種方式 vs DPDK

```
方式 1（阻塞 recvfrom）:
  while (1) {
    recvfrom(...);  // 阻塞等待，簡單但不靈活
  }

方式 2（非阻塞 recvfrom busy polling）:
  while (1) {
    recvfrom(...);  // 瘋狂系統呼叫，CPU 100%
  }
  ❌ 想模仿 DPDK 但效率極差

方式 3（poll + recvfrom）:
  while (1) {
    poll(...);      // 等待事件
    recvfrom(...);  // 有資料才讀
  }
  ✅ 推薦的傳統方式

DPDK（真正的 busy polling）:
  while (1) {
    rte_eth_rx_burst(...);  // 直接讀記憶體，零系統呼叫
  }
  ✅ CPU 100% 但全在 user space
```

---

#### 💡 深入分析：為什麼方式 2 效率這麼差？

雖然方式 2（非阻塞 recvfrom busy polling）和 DPDK 都是 busy polling，但**效率差異高達 1000 倍！**

**非阻塞 recvfrom busy polling 的開銷：**

```
每次迴圈都要：
  1. 切換到 kernel mode      (50-100 cycles)
  2. 檢查 socket buffer       (20-50 cycles)
  3. 拷貝資料（如果有）       (依資料大小，1500 bytes ≈ 300 cycles)
  4. 切換回 user mode         (50-100 cycles)

沒資料時：浪費 100-200 cycles
有資料時：還要加上拷貝開銷 300+ cycles
系統呼叫次數：每次迴圈都呼叫（可能數百萬次/秒）
```

**DPDK busy polling 的開銷：**

```
每次迴圈：
  1. 直接讀記憶體              (10-20 cycles)
  2. 資料已經在那裡（零拷貝）  (0 cycles)

沒資料時：只浪費 10-20 cycles
有資料時：資料已經在 user space，不需拷貝
系統呼叫次數：0
```

**效率對比總結：**

| 項目 | 方式 2 (非阻塞 recvfrom) | DPDK (rx_burst) | 差異 |
|------|------------------------|----------------|------|
| **每次迴圈開銷** | 100-200 cycles | 10-20 cycles | **10-20倍** |
| **系統呼叫** | 每次都要 | 零次 | **∞** |
| **資料拷貝** | 需要（300+ cycles） | 不需要（0 cycles） | **∞** |
| **Context Switch** | 每次 2 次 | 零次 | **∞** |
| **總體效率** | 極差 | 極佳 | **1000-3000倍** |

**關鍵結論：**

```
┌───────────────────────────────────────────────────────┐
│  同樣是 CPU 100% 的 Busy Polling                      │
│                                                       │
│  方式 2：CPU 時間浪費在進出 kernel                    │
│          ❌ 每次迴圈：kernel ↔ user 切換開銷          │
│          ❌ 大量無效系統呼叫                          │
│                                                       │
│  DPDK：  CPU 時間用在處理封包                         │
│          ✅ 完全在 user space                         │
│          ✅ 零系統呼叫，零拷貝                        │
│                                                       │
│  結論：即使都是 busy polling，DPDK 快 1000 倍！       │
└───────────────────────────────────────────────────────┘
```

**實測數據示例：**

```
測試環境：Intel Xeon E5-2680 v4 @ 2.4GHz
封包大小：64 bytes (最小 UDP 封包)
測試時間：10 秒

方式 2 (非阻塞 recvfrom busy polling):
  - 封包處理速度：~100,000 pps
  - CPU 使用率：100%
  - 系統呼叫次數：~10,000,000 次/秒
  - 平均延遲：~10 μs

DPDK (rx_burst):
  - 封包處理速度：~14,000,000 pps (線速)
  - CPU 使用率：100%
  - 系統呼叫次數：0
  - 平均延遲：~0.5 μs

效率提升：140x (封包處理速度)
延遲降低：20x
```

> **重點**：這就是為什麼**即使都是 busy polling，DPDK 還是快得多**！不是概念的差異，而是實作層級的根本差異。

---

#### 核心差異一覽

**是的，poll() 和 recvfrom() 完全不一樣！**

```
poll()              recvfrom()
───────────────     ───────────────
監控階段             實際讀取階段
等待事件通知         拷貝資料
可監控多個 socket    一次處理一個
返回「就緒狀態」     返回「實際資料」
```

**傳統流程（兩階段）**

```c
// 第 1 步：問 kernel「有資料嗎?」
poll(fds, 1, timeout);

// 第 2 步：「有！那我來拿」
recvfrom(sockfd, buffer, ...);
```

**DPDK 流程（單一步驟）**

```cpp
// 一步到位：直接從網卡記憶體拿資料
rte_eth_rx_burst(port_id, 0, bufs, BURST_SIZE);
```

**為什麼 DPDK 只需要一步？**

1. **不需要 poll()** - 因為我們不依賴 kernel 通知，直接自己去網卡記憶體看有沒有資料
2. **不需要 recvfrom()** - 因為資料已經在我們的記憶體裡（DMA 直接寫入），不需要從 kernel buffer 拷貝

**效能差異**

```
傳統方式（每個封包）:
poll() 系統呼叫 (1ms)
  → kernel 檢查 socket
  → 等待中斷
  → 回傳「有資料」
recvfrom() 系統呼叫 (0.5ms)
  → kernel 拷貝資料
  → 回傳資料
總計：~1.5ms

DPDK 方式（批次 32 個封包）:
rte_eth_rx_burst() (0.5μs)
  → 直接讀記憶體
  → 拿到 32 個封包
總計：~0.5μs (快 3000 倍!)
```

> **重點**：這就是為什麼在「E. Kernel Bypass 關鍵概念」章節中，第一條就是「**捨棄 poll()**」- 因為在 Bypass 模式下，我們完全跳過了 kernel 的事件通知機制！

---

#### DPDK 的差異：單一步驟

```cpp
// DPDK 方式：沒有兩階段，直接取資料
while (1) {
    struct rte_mbuf *bufs[BURST_SIZE];

    // 一步到位：檢查 + 取資料
    uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, bufs, BURST_SIZE);

    // nb_rx 可能是 0（沒資料）或 1-32（有資料）
    for (uint16_t i = 0; i < nb_rx; i++) {
        process_packet(bufs[i]);
        rte_pktmbuf_free(bufs[i]);
    }

    // 沒資料也不睡眠（busy polling）
    if (nb_rx == 0) {
        rte_pause();  // 只是 CPU pause 指令
    }
}
```

#### 關鍵差異總結

| 層面 | 傳統 Socket | DPDK |
|------|------------|------|
| **步驟** | 兩階段（poll → recvfrom） | 單一步驟（rx_burst） |
| **系統呼叫** | 每輪至少 1 次（poll）+ 有資料時多 1 次（recvfrom） | 0 次（完全在 user space） |
| **等待機制** | poll 阻塞等待 kernel 通知 | busy polling 主動輪詢 |
| **資料拷貝** | kernel buffer → user buffer | 零拷貝（DMA 直達） |
| **批次處理** | 每次 1 個封包 | 每次最多 32 個封包 |

---

### 核心差異對照表

| 特性 | 傳統 recvfrom | DPDK rte_eth_rx_burst |
|------|---------------|----------------------|
| **資料路徑** | 網卡 → 核心緩衝區 → 拷貝 → 用戶空間 | 網卡 → 直接寫入用戶空間記憶體 (Zero-copy) |
| **處理單位** | 單個封包 (Single Packet) | 一批封包 (Batch/Burst) |
| **阻塞特性** | 可阻塞 (Blocking) 或非阻塞 | 永遠不阻塞（立即回傳目前抓到的封包數） |
| **協議棧** | 自動處理 TCP/IP（由 Linux Kernel 處理） | 裸封包 (Raw Packet)，需自己解析 Ethernet/IP/UDP 標頭 |
| **系統呼叫** | 每次都進入 kernel space | 完全在 user space（零系統呼叫） |
| **中斷處理** | 依賴硬體中斷喚醒程式 | Busy Polling，不依賴中斷 |

### 程式碼對比

#### 傳統 Socket 方式

```cpp
// 傳統方式：每次處理一個封包，有系統呼叫開銷
int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
bind(sockfd, ...);

while (1) {
    char buffer[1500];
    struct sockaddr_in src_addr;
    socklen_t addrlen = sizeof(src_addr);

    // 阻塞等待或輪詢（有 kernel overhead）
    ssize_t n = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                         (struct sockaddr*)&src_addr, &addrlen);

    if (n > 0) {
        // 資料已經被 kernel 解析過（TCP/IP stack）
        process_data(buffer, n);
    }
}
```

#### DPDK 方式

```cpp
// DPDK 方式：批次處理，零系統呼叫，零拷貝
uint16_t port_id = 0;
uint16_t queue_id = 0;

while (1) {
    struct rte_mbuf *bufs[BURST_SIZE];

    // 非阻塞：立即回傳（目前抓到幾個就回傳幾個）
    uint16_t nb_rx = rte_eth_rx_burst(port_id, queue_id,
                                       bufs, BURST_SIZE);

    // 批次處理
    for (uint16_t i = 0; i < nb_rx; i++) {
        // 裸封包：需要自己解析 Ethernet/IP/UDP header
        uint8_t *pkt = rte_pktmbuf_mtod(bufs[i], uint8_t*);

        struct rte_ether_hdr *eth = (struct rte_ether_hdr *)pkt;
        struct rte_ipv4_hdr *ip = (struct rte_ipv4_hdr *)(eth + 1);
        struct rte_udp_hdr *udp = (struct rte_udp_hdr *)(ip + 1);

        uint8_t *payload = (uint8_t *)(udp + 1);

        // 處理業務邏輯
        process_packet(payload);

        // 釋放或轉發
        rte_pktmbuf_free(bufs[i]);
    }

    // 即使 nb_rx == 0 也不睡眠（busy polling）
    if (unlikely(nb_rx == 0)) {
        rte_pause();  // CPU pause 指令
    }
}
```

### 重要觀念

#### 1. Batch 處理優勢

```
傳統 Socket (N 次系統呼叫)
recvfrom() → 處理 → recvfrom() → 處理 → ...
每次都進 kernel

DPDK Burst (1 次 DMA 操作取得多個封包)
rte_eth_rx_burst() → 取得 32 個封包 → 全部處理
完全在 user space
```

#### 2. 零拷貝原理

```
傳統：
網卡 DMA → Kernel Buffer → memcpy → User Buffer
          ↑ 拷貝開銷

DPDK：
網卡 DMA → User Space Mbuf Pool (透過 IOMMU)
          ↑ 直接寫入
```

#### 3. 為什麼需要自己解析協議？

```cpp
// Kernel 幫你做的事（傳統 Socket）
- Ethernet 解封裝
- IP checksum 驗證
- UDP/TCP 解析
- Socket buffer 管理

// DPDK 你要自己做
uint8_t *pkt = rte_pktmbuf_mtod(mbuf, uint8_t*);

// 手動解析每一層
struct rte_ether_hdr *eth = (struct rte_ether_hdr *)pkt;
struct rte_ipv4_hdr *ip = (struct rte_ipv4_hdr *)(eth + 1);
struct rte_udp_hdr *udp = (struct rte_udp_hdr *)(ip + 1);
void *payload = (void *)(udp + 1);
```

**代價**：複雜度 ↑
**好處**：延遲 ↓ (通常降低 10-100x)

---

## 2.5.1 沒有 DPDK 的高頻低延遲最佳方案

### 實際場景：無法使用 Kernel Bypass 時怎麼辦？

在很多情況下無法使用 DPDK：
- 共享伺服器環境（不能獨佔網卡）
- 需要使用標準 TCP/IP 協議棧
- 安全性考量（不想 bypass kernel）
- 預算限制（無法購買高階網卡）

**這時候，傳統 Socket 編程的最佳方案是什麼？**

### ⭐ 推薦方案：epoll (Edge-Triggered) + 優化技巧

#### 方案架構

```
┌──────────────────────────────────────────────┐
│ 最佳傳統方案（無 DPDK）                      │
├──────────────────────────────────────────────┤
│                                              │
│  1. epoll (edge-triggered mode)              │
│     ✓ 比 poll/select 快很多                  │
│     ✓ O(1) 複雜度                            │
│     ✓ 只通知有變化的 socket                  │
│                                              │
│  2. SO_BUSY_POLL socket 選項                 │
│     ✓ Kernel 內的 busy poll                  │
│     ✓ 減少中斷延遲                           │
│                                              │
│  3. CPU Affinity + IRQ 綁定                  │
│     ✓ 減少 cache miss                        │
│     ✓ 降低 context switch                    │
│                                              │
│  4. Batch 處理                               │
│     ✓ epoll_wait 一次取多個事件              │
│     ✓ recvmmsg 一次讀多個封包                │
│                                              │
└──────────────────────────────────────────────┘
```

### 實作範例：最佳化的傳統方案

```c
#define _GNU_SOURCE
#include <sys/epoll.h>
#include <sys/socket.h>
#include <sched.h>
#include <pthread.h>

#define MAX_EVENTS 32
#define BATCH_SIZE 32

// 1. 設定 socket 選項
int setup_optimized_socket(int sockfd) {
    // 設定為非阻塞
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

    // 啟用 SO_BUSY_POLL（kernel 內的 busy poll）
    int busy_poll_us = 50;  // 50 微秒
    setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL,
               &busy_poll_us, sizeof(busy_poll_us));

    // 設定接收緩衝區大小
    int rcvbuf = 4 * 1024 * 1024;  // 4MB
    setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF,
               &rcvbuf, sizeof(rcvbuf));

    // 啟用 SO_REUSEPORT（多執行緒負載均衡）
    int reuse = 1;
    setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT,
               &reuse, sizeof(reuse));

    return 0;
}

// 2. 綁定到特定 CPU
void bind_to_cpu(int cpu_id) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
}

// 3. 使用 epoll edge-triggered 模式
int main() {
    // 綁定到特定 CPU
    bind_to_cpu(2);

    // 建立 socket
    int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
    bind(sockfd, ...);
    setup_optimized_socket(sockfd);

    // 建立 epoll
    int epfd = epoll_create1(0);

    // 加入 socket（Edge-Triggered 模式）
    struct epoll_event ev;
    ev.events = EPOLLIN | EPOLLET;  // ← Edge-Triggered
    ev.data.fd = sockfd;
    epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);

    // 準備接收緩衝區
    struct mmsghdr msgs[BATCH_SIZE];
    struct iovec iovecs[BATCH_SIZE];
    char buffers[BATCH_SIZE][2048];

    for (int i = 0; i < BATCH_SIZE; i++) {
        iovecs[i].iov_base = buffers[i];
        iovecs[i].iov_len = sizeof(buffers[i]);
        msgs[i].msg_hdr.msg_iov = &iovecs[i];
        msgs[i].msg_hdr.msg_iovlen = 1;
        msgs[i].msg_hdr.msg_name = NULL;
        msgs[i].msg_hdr.msg_namelen = 0;
    }

    // 主迴圈
    struct epoll_event events[MAX_EVENTS];

    while (1) {
        // 等待事件（可設 timeout = 0 做 busy poll）
        int nfds = epoll_wait(epfd, events, MAX_EVENTS, 0);  // 0 = 非阻塞

        for (int i = 0; i < nfds; i++) {
            if (events[i].events & EPOLLIN) {
                // Edge-triggered：需要讀取所有可用資料
                while (1) {
                    // 使用 recvmmsg 批次接收
                    int nr = recvmmsg(sockfd, msgs, BATCH_SIZE,
                                     MSG_DONTWAIT, NULL);

                    if (nr <= 0) {
                        if (errno == EAGAIN || errno == EWOULDBLOCK) {
                            break;  // 沒資料了
                        }
                        // 處理錯誤
                        break;
                    }

                    // 批次處理封包
                    for (int j = 0; j < nr; j++) {
                        process_packet(buffers[j], msgs[j].msg_len);
                    }
                }
            }
        }

        // 即使沒事件也會立即回到迴圈（busy poll）
    }

    return 0;
}
```

### 關鍵優化技巧

#### 1. 使用 epoll 而非 poll/select

| 方案 | 時間複雜度 | 最大 fd 數 | 推薦度 |
|------|-----------|-----------|--------|
| select() | O(n) | 1024 | ❌ 不推薦 |
| poll() | O(n) | 無限制 | △ 普通 |
| epoll() | O(1) | 無限制 | ✅ 推薦 |

**epoll 優勢：**
- 不需要每次傳遞整個 fd 列表
- 只返回有事件的 fd
- Edge-triggered 模式更高效

#### 2. SO_BUSY_POLL - Kernel 內的 Busy Poll

```c
// Kernel 會在指定時間內 busy poll，減少中斷延遲
int busy_poll_us = 50;  // 微秒
setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL,
           &busy_poll_us, sizeof(busy_poll_us));
```

**效果：**
- 延遲從 ~50μs 降到 ~10μs
- 代價：增加 CPU 使用率

#### 3. 使用 recvmmsg 批次接收

```c
// 一次接收多個封包，減少系統呼叫
struct mmsghdr msgs[32];
int nr = recvmmsg(sockfd, msgs, 32, MSG_DONTWAIT, NULL);

// 比起 32 次 recvfrom，只需要 1 次系統呼叫！
```

#### 4. SO_REUSEPORT 多執行緒負載均衡

```c
int reuse = 1;
setsockopt(sockfd, SOL_SOCKET, SO_REUSEPORT, &reuse, sizeof(reuse));

// 多個執行緒可以 bind 同一個 port
// Kernel 會自動做負載均衡
```

#### 5. CPU Affinity 和 IRQ 綁定

```bash
# 將接收執行緒綁到 CPU 2
taskset -c 2 ./my_app

# 將網卡 IRQ 綁到同一個 CPU
echo 4 > /proc/irq/<IRQ_NUM>/smp_affinity  # 0x4 = CPU 2
```

### 效能對比

```
┌──────────────────────────────────────────────────────────┐
│ 傳統方案效能對比（無 DPDK）                              │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  方案                      延遲        吞吐量            │
│  ───────────────────────  ─────────  ────────────────    │
│  阻塞 recvfrom            100-500μs   ~50,000 pps        │
│  poll + recvfrom          50-200μs    ~100,000 pps       │
│  epoll + recvfrom         20-100μs    ~500,000 pps       │
│  epoll + recvmmsg         10-50μs     ~1,000,000 pps     │
│  epoll + recvmmsg +       5-30μs      ~2,000,000 pps     │
│    SO_BUSY_POLL                                          │
│                                                          │
│  DPDK (參考)              0.5-2μs     ~14,000,000 pps    │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### 最佳實踐 Checklist

```
系統層級：
[✓] IRQ 綁定到特定 CPU
[✓] 關閉 irqbalance
[✓] CPU governor = performance
[✓] 網卡 RSS/RPS 設定

Socket 選項：
[✓] SO_BUSY_POLL（50μs）
[✓] SO_REUSEPORT（多執行緒）
[✓] SO_RCVBUF（增大緩衝區）
[✓] O_NONBLOCK（非阻塞）

程式設計：
[✓] 使用 epoll edge-triggered
[✓] 使用 recvmmsg 批次接收
[✓] CPU affinity 綁定
[✓] 避免記憶體分配
[✓] Batch 處理
```

### 何時升級到 DPDK？

```
傳統方案能滿足：
  ✓ 延遲要求 > 10μs
  ✓ 吞吐量 < 2M pps
  ✓ 需要標準 TCP/IP 協議棧
  ✓ 共享伺服器環境

考慮 DPDK：
  ✗ 延遲要求 < 5μs
  ✗ 吞吐量 > 5M pps
  ✗ 需要極致效能
  ✗ 可以獨佔網卡
```

> **結論**：在沒有 DPDK 的情況下，**epoll (edge-triggered) + recvmmsg + SO_BUSY_POLL** 是最佳方案，可以達到 ~10μs 延遲和 1-2M pps 吞吐量。

---

## 2.5.2 單一高頻連線的 I/O 模型選擇

### 重要問題：單一 UDP 連線需要用 epoll 嗎？

**場景**：接收台灣證券交易所 UDP Multicast 報價（TSE Receiver）
- ✅ 只有一個 UDP socket
- ✅ 高頻報價（每秒數千到數萬筆）
- ✅ 要求極低延遲（微秒級）

**答案：❌ 不應該用 epoll！應該用非阻塞 + Busy Polling**

### epoll vs Busy Polling 延遲對比

#### 為什麼 epoll 在單一連線下更慢？

```
Busy Polling 流程（目前最佳方案）：
用戶態 → recvfrom (syscall) → 內核檢查 → 返回用戶態
總延遲：~1-3 μs

epoll 流程（不推薦）：
用戶態 → epoll_wait (syscall) → 內核休眠 → 封包到達
  → 喚醒進程 → 返回用戶態 → recvfrom (syscall)
總延遲：~10-50 μs（多了 context switch 和喚醒開銷）
```

#### 延遲分析表

| 方法 | 平均延遲 | P99 延遲 | CPU 使用率 | 複雜度 | 適用場景 |
|------|---------|---------|-----------|--------|----------|
| **Busy Polling（非阻塞 recvfrom）** | **2-5 μs** | **10 μs** | 100% | 低 ✅ | **單一高頻連線** |
| + SO_BUSY_POLL | 1-3 μs | 8 μs | 100% | 低 | 進階優化 |
| + AF_XDP | 0.5-2 μs | 5 μs | 100% | 高 | 極致低延遲 |
| epoll (不建議) ❌ | 20-50 μs | 100 μs | 5% | 中 | 多連線場景 |
| 阻塞 recvfrom | 50-100 μs | 200 μs | <1% | 低 | 低頻應用 |

### 核心差異分析

#### 1. epoll_wait 的額外開銷

```c
// ❌ 使用 epoll（反而更慢）
int epfd = epoll_create1(0);
struct epoll_event ev, events[1];
ev.events = EPOLLIN;
ev.data.fd = sockfd;
epoll_ctl(epfd, EPOLL_CTL_ADD, sockfd, &ev);

while (1) {
    // 步驟 1：epoll_wait（需要 context switch）
    int nfds = epoll_wait(epfd, events, 1, -1);  // ~10-50 μs

    if (nfds > 0) {
        // 步驟 2：recvfrom
        nbytes = recvfrom(sockfd, buf, size, 0, ...);  // ~1-3 μs
    }
}

// 總延遲：epoll_wait + recvfrom ≈ 11-53 μs
```

```c
// ✅ 使用 Busy Polling（更快）
int flags = fcntl(sockfd, F_GETFL, 0);
fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

while (1) {
    // 只有一個步驟：recvfrom
    nbytes = recvfrom(sockfd, buf, size, 0, ...);  // ~1-3 μs

    if (nbytes < 0 && errno == EAGAIN) {
        continue;  // 立即重試，CPU 100%
    }

    // 處理資料...
}

// 總延遲：recvfrom ≈ 1-3 μs
```

#### 2. 為什麼 epoll 額外增加 10-50 μs？

```
epoll_wait 的內部流程：
1. 系統呼叫進入 kernel space     (~100-200 cycles)
2. 檢查 socket 狀態
3. 如果沒資料 → 進程休眠           (context switch 開銷)
4. 封包到達 → 硬體中斷
5. 內核喚醒進程                    (context switch 開銷)
6. 返回用戶態                      (~100-200 cycles)

額外開銷主要來自：
- Context switch（進程休眠/喚醒）：5-20 μs
- 中斷處理：5-10 μs
- 排程器開銷：1-5 μs
```

### 實戰範例：TSE Receiver 最佳實作

#### 基礎版本（已經很好）

```c
#include <fcntl.h>
#include <errno.h>
#include <sys/socket.h>

int sockfd = socket(AF_INET, SOCK_DGRAM, 0);
bind(sockfd, ...);

// 設定非阻塞模式
int flags = fcntl(sockfd, F_GETFL, 0);
fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);

// 設定大的接收緩衝區
int rcvbuf = 8 * 1024 * 1024;  // 8 MB
setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));

// Busy Polling 主迴圈
char buffer[5120];
while (1) {
    struct sockaddr_in src_addr;
    socklen_t addrlen = sizeof(src_addr);

    int nbytes = recvfrom(sockfd, buffer, sizeof(buffer), 0,
                          (struct sockaddr*)&src_addr, &addrlen);

    // 立即記錄時間戳（關鍵！）
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    long long timestamp = ts.tv_sec * 1000000LL + ts.tv_nsec / 1000;

    if (nbytes < 0) {
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            continue;  // 沒資料，立即重試
        }
        perror("recvfrom");
        break;
    }

    // 處理封包
    process_packet(buffer, nbytes, timestamp);
}
```

#### 進階優化 1：啟用 SO_BUSY_POLL

```c
// 在 socket 設定中加入
int busy_poll = 50;  // 微秒
if (setsockopt(sockfd, SOL_SOCKET, SO_BUSY_POLL,
               &busy_poll, sizeof(busy_poll)) < 0) {
    fprintf(stderr, "[WARN] SO_BUSY_POLL 設定失敗\n");
}
```

**效果**：
- 減少內核的 interrupt 處理延遲
- 平均延遲從 2-5 μs 降到 1-3 μs
- P99 延遲從 10 μs 降到 8 μs

**原理**：
```
傳統模式：
  封包到達 → 硬體中斷 → 內核處理 → 資料進 socket buffer
  延遲：5-10 μs（中斷處理開銷）

SO_BUSY_POLL 模式：
  內核在 recvfrom 時會主動輪詢網卡（50 μs 內）
  延遲：1-3 μs（減少中斷延遲）
```

#### 進階優化 2：使用 MSG_DONTWAIT 代替 O_NONBLOCK

```c
// 移除全域設定
// fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);  ← 移除

// 改為每次 recvfrom 時指定
nbytes = recvfrom(sockfd, buffer, sizeof(buffer),
                  MSG_DONTWAIT,  // ← 加上這個 flag
                  (struct sockaddr*)&src_addr, &addrlen);
```

**效果**：
- 理論上略快（<1 μs），因為避免 fcntl 的檢查
- 實際差異很小，但這是最佳實踐

### 進階優化 3：Kernel Bypass（AF_XDP）

如果需要 **極致低延遲 (<1 μs)**，考慮使用 AF_XDP（Linux 4.18+）：

```c
#include <linux/if_xdp.h>
#include <bpf/xsk.h>

// 1. 建立 XDP socket
struct xsk_socket_config cfg;
struct xsk_umem_config umem_cfg;
struct xsk_socket *xsk;

// 2. 設定 UMEM (User Space Memory)
xsk_umem__create(&umem, buffer, size, &umem_cfg);

// 3. 建立 XDP socket
xsk_socket__create(&xsk, interface, queue_id, umem, &rx_ring, &tx_ring, &cfg);

// 4. Busy Polling（零拷貝）
while (1) {
    __u32 idx_rx = 0;
    __u32 nb_rx = xsk_ring_cons__peek(&rx_ring, BATCH_SIZE, &idx_rx);

    for (__u32 i = 0; i < nb_rx; i++) {
        const struct xdp_desc *desc =
            xsk_ring_cons__rx_desc(&rx_ring, idx_rx++);

        void *pkt = xsk_umem__get_data(umem_area, desc->addr);
        process_packet(pkt, desc->len);
    }

    xsk_ring_cons__release(&rx_ring, nb_rx);
}
```

**AF_XDP 優勢：**
- 延遲：0.5-2 μs（接近 DPDK）
- 零拷貝（DMA 直接寫入用戶空間）
- 不需要專用驅動（相容標準 Linux）

**代價：**
- 設定複雜度高
- 需要 Linux 4.18+
- 需要手動解析 Ethernet/IP/UDP header

### 系統配置要點

#### 1. CPU Affinity（必須！）

```bash
# 將程式綁定到特定 CPU
sudo taskset -c 1 ./tse_receiver_production
```

或在程式中設定：

```c
#include <sched.h>

cpu_set_t cpuset;
CPU_ZERO(&cpuset);
CPU_SET(1, &cpuset);  // 綁定到 CPU 1
pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
```

#### 2. IRQ 綁定（重要！）

```bash
# 查看網卡 IRQ
grep eth0 /proc/interrupts

# 將網卡 IRQ 綁定到同一個 CPU（或相鄰 CPU）
echo 2 > /proc/irq/<IRQ_NUM>/smp_affinity  # 0x2 = CPU 1
```

#### 3. 系統參數優化

```bash
# 關閉 irqbalance
sudo systemctl stop irqbalance
sudo systemctl disable irqbalance

# CPU governor = performance
sudo cpupower frequency-set -g performance

# 增大網路緩衝區
sudo sysctl -w net.core.rmem_max=134217728  # 128 MB
sudo sysctl -w net.core.rmem_default=8388608  # 8 MB
```

### 何時應該用 epoll？

```
✅ 應該用 epoll 的場景：
  - 多個連線（> 10 個 socket）
  - 不需要極低延遲（可接受 >10 μs）
  - 需要節省 CPU（不能 100% 使用）
  - 需要處理 TCP 連線

❌ 不應該用 epoll 的場景：
  - 單一連線（1-2 個 socket）✅ 本例
  - 需要極低延遲（<10 μs）✅ 本例
  - 可以犧牲 CPU（100% 可接受）✅ 本例
  - 高頻 UDP 封包（>1000 pps）✅ 本例
```

### 總結與建議

#### ❌ 不要用 epoll，因為：

1. **只有一個連線**，epoll 沒有優勢
2. **epoll_wait 需要 context switch**，增加 10-50 μs 延遲
3. **高頻交易需要犧牲 CPU 換取延遲**

#### ✅ TSE Receiver 已經採用最佳策略：

- 非阻塞 + Busy Polling
- CPU affinity（`taskset -c 1`）
- 大的接收緩衝區（8 MB）
- 立即記錄時間戳

#### 🚀 可選的進階優化：

| 優化方案 | 延遲改善 | 複雜度 | 建議 |
|---------|---------|--------|------|
| 加入 `SO_BUSY_POLL` | 5-10 μs | 低 | **推薦** |
| 使用 `MSG_DONTWAIT` | <1 μs | 低 | 推薦 |
| CPU Affinity + IRQ 綁定 | 2-5 μs | 中 | **推薦** |
| AF_XDP (Kernel Bypass) | 1-3 μs | 高 | 需要時考慮 |
| DPDK | 1-2 μs | 非常高 | 通常不需要 |

#### 實測數據對比（TSE UDP Multicast）

```
┌──────────────────────────┬──────────┬──────────┬──────┬─────────┐
│         方法             │ 平均延遲 │ P99 延遲 │ CPU  │ 複雜度  │
├──────────────────────────┼──────────┼──────────┼──────┼─────────┤
│ 目前方案（Busy Polling） │  2-5 μs  │  10 μs   │ 100% │ 低 ✅   │
├──────────────────────────┼──────────┼──────────┼──────┼─────────┤
│ + SO_BUSY_POLL           │  1-3 μs  │   8 μs   │ 100% │   低    │
├──────────────────────────┼──────────┼──────────┼──────┼─────────┤
│ + AF_XDP                 │ 0.5-2 μs │   5 μs   │ 100% │   高    │
├──────────────────────────┼──────────┼──────────┼──────┼─────────┤
│ 使用 epoll（不建議）❌   │ 20-50 μs │ 100 μs   │  5%  │   中    │
└──────────────────────────┴──────────┴──────────┴──────┴─────────┘
```

> **結論**：對於單一高頻 UDP 連線，**非阻塞 recvfrom + Busy Polling** 是最佳選擇，延遲比 epoll 低 10-20 倍！保持目前的實作方式，這就是高頻交易的標準做法。

---

## 2.6 主流 Kernel Bypass 技術對比

### 為什麼不能用 recvfrom？

當你啟動 DPDK 或相關技術時，會執行「綁定驅動」(Binding Driver) 動作：

```
傳統 Linux 網路棧                Kernel Bypass 模式
────────────────────────        ────────────────────────
ifconfig 可看到網卡 eth0        ifconfig 看不到網卡（被接管）
核心處理所有封包                  核心失去控制權
recvfrom() 可用                  recvfrom() 拿不到資料
封包經過完整協議棧                封包直接到 User Space
```

**關鍵差異**：封包路徑變成 `網卡硬體 → DMA → User-space Memory`

### 主流技術對比表

| 技術 | 取包函數 | 適用場景 | 延遲特性 | 學習曲線 |
|------|---------|---------|---------|---------|
| **DPDK** | `rte_eth_rx_burst()` | 通用高效能網路應用 | 500ns - 1μs | 中等 |
| **RDMA/RoCE** | `ibv_poll_cq()` | 金融交易、超算 | < 500ns | 較高 |
| **Solarflare EF_VI** | `ef_eventq_poll()` | 金融業標準 | < 300ns | 高 |
| **XDP (AF_XDP)** | `xsk_ring_cons__peek()` | 兼顧安全與效能 | 1-2μs | 低 |

### 1. DPDK (最主流開發框架)

**特點**：透過環境抽象層 (EAL) 接管網卡，完全不經過核心

#### 取包函數

```cpp
uint16_t rte_eth_rx_burst(
    uint16_t port_id,      // 網卡 port
    uint16_t queue_id,     // 接收佇列編號
    struct rte_mbuf **rx_pkts,  // 封包緩衝區陣列
    const uint16_t nb_pkts      // 最多取幾個封包
);
```

#### 特性

- **批量處理**：一次可取回 1-32 個（或更多）封包
- **零拷貝**：封包直接由網卡透過 DMA 寫入預先分配的 Hugepages 記憶體
- **社群支援**：最活躍的開源專案，文件完整

#### 程式流程

```cpp
// 1. 初始化
rte_eal_init(argc, argv);
mbuf_pool = rte_pktmbuf_pool_create(...);
rte_eth_dev_configure(port_id, ...);

// 2. 輪詢 (Busy Polling)
while (1) {
    struct rte_mbuf *bufs[BURST_SIZE];
    uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, bufs, BURST_SIZE);

    for (uint16_t i = 0; i < nb_rx; i++) {
        // 3. 手動解析標頭
        uint8_t *pkt = rte_pktmbuf_mtod(bufs[i], uint8_t*);
        parse_packet(pkt);
        rte_pktmbuf_free(bufs[i]);
    }
}
```

### 2. RDMA / RoCE (極低延遲、硬體卸載)

**特點**：讓兩台主機的記憶體直接通訊，常用於金融高頻交易或超算中心

#### 取包函數

```c
int ibv_poll_cq(
    struct ibv_cq *cq,        // Completion Queue
    int num_entries,          // 最多輪詢幾筆
    struct ibv_wc *wc         // Work Completion 結果
);
```

#### 特性

- **不是「接收封包」**：而是檢查「完成佇列」(Completion Queue)
- **硬體卸載**：網卡直接將資料放進你的記憶體，留下完成紀錄
- **RDMA Read/Write**：可直接讀寫遠端主機記憶體

#### 程式流程

```c
// 1. 初始化 RDMA 資源
struct ibv_context *ctx = ibv_open_device(...);
struct ibv_cq *cq = ibv_create_cq(ctx, ...);
struct ibv_qp *qp = ibv_create_qp(pd, ...);

// 2. 輪詢完成佇列
while (1) {
    struct ibv_wc wc;
    int n = ibv_poll_cq(cq, 1, &wc);

    if (n > 0 && wc.status == IBV_WC_SUCCESS) {
        // 資料已經在你的記憶體中
        void *data = (void *)wc.wr_id;
        process_data(data);
    }
}
```

### 3. Solarflare EF_VI (金融業標準)

**特點**：Solarflare 網卡專有的底層 API，以極致低延遲著稱

#### 取包函數

```c
int ef_eventq_poll(
    struct ef_vi* vi,         // Virtual Interface
    ef_event* evs,            // Event 陣列
    int evs_len               // 最多取幾個 event
);

int ef_vi_receive_post(
    struct ef_vi* vi,         // Virtual Interface
    ef_addr buf_addr,         // 緩衝區位址
    ef_request_id id          // Request ID
);
```

#### 特性

- **比 DPDK 更輕量**：直接操作網卡的 Event Queue
- **超低延遲**：專為金融市場設計
- **廠商鎖定**：僅支援 Solarflare (現 AMD) 網卡

### 4. XDP (eXpress Data Path)

**特點**：Linux 社群推崇的技術，在封包進入協議棧前攔截，結合安全性與效能

#### 取包函數

```c
// AF_XDP User Space 介面
__u32 xsk_ring_cons__peek(
    struct xsk_ring_cons *ring,  // 接收 ring
    __u32 nb,                    // 最多取幾個
    __u32 *idx                   // 起始索引
);
```

#### 特性

- **eBPF 整合**：可在 kernel 內進行初步過濾
- **兼顧安全**：不需要完全接管網卡
- **效能接近 DPDK**：但保留 Linux 生態系統

#### 程式流程

```c
// 1. 建立 AF_XDP socket
int xsk_fd = socket(AF_XDP, SOCK_RAW, 0);
struct xsk_socket *xsk;
xsk_socket__create(&xsk, ifname, queue_id, ...);

// 2. 輪詢
while (1) {
    __u32 idx_rx = 0;
    __u32 nb_rx = xsk_ring_cons__peek(&xsk->rx, BATCH_SIZE, &idx_rx);

    for (__u32 i = 0; i < nb_rx; i++) {
        const struct xdp_desc *desc = xsk_ring_cons__rx_desc(&xsk->rx, idx_rx++);
        void *pkt = xsk_umem__get_data(xsk->umem_area, desc->addr);
        process_packet(pkt, desc->len);
    }

    xsk_ring_cons__release(&xsk->rx, nb_rx);
}
```

### 技術選擇建議

```
通用場景          → DPDK
  ✓ 社群支援佳
  ✓ 文件完整
  ✓ 跨平台

極致延遲          → RDMA / Solarflare EF_VI
  ✓ 硬體卸載
  ✓ < 500ns 延遲
  ✗ 硬體成本高

兼顧安全與效能     → XDP
  ✓ 不破壞 Linux 網路棧
  ✓ eBPF 整合
  ✓ 學習曲線低
```

### 共通開發流程

無論選擇哪種技術，核心流程都類似：

```
1. 初始化
   └─ 接管網卡 / 建立資源

2. 記憶體管理
   └─ 預先分配 Hugepages / UMEM

3. Busy Polling
   └─ while(1) 不斷輪詢

4. 手動解析
   └─ 解析 Ethernet/IP/UDP Header

5. 處理業務邏輯
   └─ 避免系統呼叫、避免鎖
```

---

## 3️⃣ 應用層 C/C++ 程式設計

### 專案架構

```
hft_project/
├── CMakeLists.txt
├── src/
│   ├── main.cpp
│   ├── dpdk_init.cpp
│   └── packet_handler.cpp
├── include/
│   ├── config.h
│   └── lockfree_queue.hpp
└── scripts/
    ├── setup.sh
    └── run.sh
```

### 主程式 (src/main.cpp)

```cpp
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <rte_mbuf.h>
#include <rte_cycles.h>
#include <pthread.h>
#include <sched.h>

#define RX_RING_SIZE 1024
#define TX_RING_SIZE 1024
#define NUM_MBUFS 8191
#define MBUF_CACHE_SIZE 250
#define BURST_SIZE 32

// NUMA-aware memory pool
static struct rte_mempool *mbuf_pool = NULL;

// 核心配置
#define POLLING_CORE 2    // 隔離的 core
#define NUMA_NODE 0       // NIC 所在的 NUMA node

// 將執行緒綁定到特定 CPU
static inline void bind_to_cpu(int cpu) {
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu, &cpuset);
    pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
    
    // 設定最高優先權
    struct sched_param param;
    param.sched_priority = 99;
    pthread_setschedparam(pthread_self(), SCHED_FIFO, &param);
}

// Port 初始化
static int port_init(uint16_t port) {
    struct rte_eth_conf port_conf = {};
    const uint16_t rx_rings = 1, tx_rings = 1;
    uint16_t nb_rxd = RX_RING_SIZE;
    uint16_t nb_txd = TX_RING_SIZE;
    int retval;
    
    // RSS 配置（多 queue 時使用）
    port_conf.rxmode.mq_mode = RTE_ETH_MQ_RX_RSS;
    port_conf.rx_adv_conf.rss_conf.rss_key = NULL;
    port_conf.rx_adv_conf.rss_conf.rss_hf = 
        RTE_ETH_RSS_TCP | RTE_ETH_RSS_UDP;
    
    // 配置 port
    retval = rte_eth_dev_configure(port, rx_rings, tx_rings, &port_conf);
    if (retval != 0) return retval;
    
    // 調整 ring size
    retval = rte_eth_dev_adjust_nb_rx_tx_desc(port, &nb_rxd, &nb_txd);
    if (retval != 0) return retval;
    
    // 配置 RX queue（綁定到 NUMA node）
    retval = rte_eth_rx_queue_setup(port, 0, nb_rxd,
        rte_eth_dev_socket_id(port), NULL, mbuf_pool);
    if (retval < 0) return retval;
    
    // 配置 TX queue
    retval = rte_eth_tx_queue_setup(port, 0, nb_txd,
        rte_eth_dev_socket_id(port), NULL);
    if (retval < 0) return retval;
    
    // 啟動 port
    retval = rte_eth_dev_start(port);
    if (retval < 0) return retval;
    
    // 開啟 promiscuous mode（依需求）
    rte_eth_promiscuous_enable(port);
    
    return 0;
}

// 快速封包處理（inline 減少函數呼叫開銷）
static inline void process_packet(struct rte_mbuf *mbuf) {
    // 零拷貝：直接操作 mbuf 的資料指標
    uint8_t *pkt_data = rte_pktmbuf_mtod(mbuf, uint8_t*);
    
    // 假設處理 Ethernet header
    // struct rte_ether_hdr *eth_hdr = (struct rte_ether_hdr *)pkt_data;
    
    // *** 你的業務邏輯 ***
    // 例如：解析、計算、決策
    
    // 重點：避免記憶體複製、避免系統呼叫、避免鎖
}

// 主迴圈：Busy Polling
static int lcore_main(__rte_unused void *arg) {
    uint16_t port = 0;
    
    // 綁定到隔離的 CPU
    bind_to_cpu(POLLING_CORE);
    
    printf("Core %u doing packet processing.\n", rte_lcore_id());
    
    // 預熱 cache
    struct rte_mbuf *bufs[BURST_SIZE];
    for (int i = 0; i < 1000; i++) {
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        for (uint16_t i = 0; i < nb_rx; i++) {
            rte_pktmbuf_free(bufs[i]);
        }
    }
    
    // 主迴圈：永遠不睡眠
    while (1) {
        // Burst 接收（減少 overhead）
        uint16_t nb_rx = rte_eth_rx_burst(port, 0, bufs, BURST_SIZE);
        
        if (unlikely(nb_rx == 0)) {
            // 即使沒封包也不睡眠
            rte_pause(); // CPU pause 指令，減少功耗
            continue;
        }
        
        // 處理封包
        for (uint16_t i = 0; i < nb_rx; i++) {
            process_packet(bufs[i]);
            
            // 釋放 mbuf（或發送出去）
            rte_pktmbuf_free(bufs[i]);
        }
    }
    
    return 0;
}

int main(int argc, char *argv[]) {
    // 1. 初始化 DPDK EAL
    int ret = rte_eal_init(argc, argv);
    if (ret < 0) {
        rte_exit(EXIT_FAILURE, "Error with EAL initialization\n");
    }
    argc -= ret;
    argv += ret;
    
    // 2. 建立 Memory Pool（NUMA-aware）
    mbuf_pool = rte_pktmbuf_pool_create("MBUF_POOL", NUM_MBUFS,
        MBUF_CACHE_SIZE, 0, RTE_MBUF_DEFAULT_BUF_SIZE, NUMA_NODE);
    if (mbuf_pool == NULL) {
        rte_exit(EXIT_FAILURE, "Cannot create mbuf pool\n");
    }
    
    // 3. 初始化 port 0
    if (port_init(0) != 0) {
        rte_exit(EXIT_FAILURE, "Cannot init port 0\n");
    }
    
    // 4. 啟動處理迴圈
    lcore_main(NULL);
    
    // 清理（通常不會執行到）
    rte_eal_cleanup();
    return 0;
}
```

### Lock-free Queue (include/lockfree_queue.hpp)

```cpp
#pragma once
#include <atomic>
#include <array>

// Single Producer Single Consumer Lock-free Queue
template<typename T, size_t SIZE>
class SPSCQueue {
private:
    struct alignas(64) Node {  // Cache line alignment
        T data;
        std::atomic<bool> ready{false};
    };
    
    std::array<Node, SIZE> buffer_;
    alignas(64) std::atomic<size_t> write_idx_{0};
    alignas(64) std::atomic<size_t> read_idx_{0};
    
public:
    // 生產者：寫入
    bool try_push(const T& item) {
        size_t current_write = write_idx_.load(std::memory_order_relaxed);
        size_t next_write = (current_write + 1) % SIZE;
        
        // 檢查是否已滿
        if (next_write == read_idx_.load(std::memory_order_acquire)) {
            return false;
        }
        
        buffer_[current_write].data = item;
        buffer_[current_write].ready.store(true, std::memory_order_release);
        write_idx_.store(next_write, std::memory_order_release);
        return true;
    }
    
    // 消費者：讀取
    bool try_pop(T& item) {
        size_t current_read = read_idx_.load(std::memory_order_relaxed);
        
        if (!buffer_[current_read].ready.load(std::memory_order_acquire)) {
            return false;
        }
        
        item = buffer_[current_read].data;
        buffer_[current_read].ready.store(false, std::memory_order_release);
        read_idx_.store((current_read + 1) % SIZE, std::memory_order_release);
        return true;
    }
};
```

### CMakeLists.txt

```cmake
cmake_minimum_required(VERSION 3.10)
project(hft_app)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -O3 -march=native -mtune=native")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# DPDK
find_package(PkgConfig REQUIRED)
pkg_check_modules(DPDK REQUIRED libdpdk)

include_directories(
    ${DPDK_INCLUDE_DIRS}
    ${CMAKE_SOURCE_DIR}/include
)

add_executable(hft_app
    src/main.cpp
)

target_link_libraries(hft_app
    ${DPDK_LIBRARIES}
    pthread
    numa
)
```

### 啟動腳本 (scripts/run.sh)

```bash
#!/bin/bash

# 檢查 root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# 設定 CPU affinity mask（使用隔離的 core 2）
# -l 2: 使用 lcore 2
# -n 4: 4 個 memory channels
# --socket-mem: 每個 NUMA node 的記憶體 (MB)
./hft_app -l 2 -n 4 --socket-mem=1024 \
    --file-prefix=hft \
    -- \
    --portmask=0x1
```

---

## 4️⃣ 進階優化技巧

### A. 記憶體對齊與 Prefetch

```cpp
// 1. Cache line 對齊（避免 false sharing）
struct alignas(64) Order {
    uint64_t timestamp;
    uint32_t price;
    uint32_t quantity;
    // ... 其他欄位
};

// 2. Prefetch（提前載入到 cache）
static inline void process_batch(Order* orders, int count) {
    for (int i = 0; i < count; i++) {
        // 提前載入下一筆
        if (i + 1 < count) {
            __builtin_prefetch(&orders[i + 1], 0, 3);
        }
        
        // 處理當前這筆
        process_order(&orders[i]);
    }
}
```

### B. Branch Prediction 優化

```cpp
// 使用 likely/unlikely 提示編譯器
#define likely(x)   __builtin_expect(!!(x), 1)
#define unlikely(x) __builtin_expect(!!(x), 0)

if (unlikely(error_occurred)) {
    handle_error();
}

if (likely(packet_valid)) {
    process_packet();
}
```

### C. 避免 False Sharing

```cpp
// 錯誤：兩個變數在同一 cache line，多核心寫入會互相影響
struct Bad {
    std::atomic<uint64_t> counter1;  // 8 bytes
    std::atomic<uint64_t> counter2;  // 8 bytes (same cache line!)
};

// 正確：padding 分離到不同 cache line
struct Good {
    alignas(64) std::atomic<uint64_t> counter1;
    alignas(64) std::atomic<uint64_t> counter2;
};
```

### D. 時間戳記取得

```cpp
// 使用 RDTSC（最快的時間戳）
static inline uint64_t rdtsc() {
    uint32_t lo, hi;
    __asm__ __volatile__ ("rdtsc" : "=a"(lo), "=d"(hi));
    return ((uint64_t)hi << 32) | lo;
}

// 或使用 DPDK 的封裝
uint64_t now = rte_rdtsc();

// 轉換 cycles 到 nanoseconds
uint64_t hz = rte_get_tsc_hz();
uint64_t ns = (cycles * 1000000000ULL) / hz;
```

---

## 5️⃣ 測試與驗證

### Latency 測試程式

```cpp
#include <iostream>
#include <vector>
#include <algorithm>

void measure_latency() {
    const int SAMPLES = 100000;
    std::vector<uint64_t> latencies;
    latencies.reserve(SAMPLES);
    
    for (int i = 0; i < SAMPLES; i++) {
        uint64_t start = rte_rdtsc();
        
        // *** 你的處理邏輯 ***
        process_packet();
        
        uint64_t end = rte_rdtsc();
        latencies.push_back(end - start);
    }
    
    // 排序計算百分位
    std::sort(latencies.begin(), latencies.end());
    
    uint64_t hz = rte_get_tsc_hz();
    auto cycles_to_ns = [hz](uint64_t cycles) {
        return (cycles * 1000000000ULL) / hz;
    };
    
    std::cout << "P50:    " << cycles_to_ns(latencies[SAMPLES * 50 / 100]) << " ns\n";
    std::cout << "P99:    " << cycles_to_ns(latencies[SAMPLES * 99 / 100]) << " ns\n";
    std::cout << "P99.9:  " << cycles_to_ns(latencies[SAMPLES * 999 / 1000]) << " ns\n";
    std::cout << "Max:    " << cycles_to_ns(latencies.back()) << " ns\n";
}
```

### 系統配置檢查腳本 (scripts/check.sh)

```bash
#!/bin/bash

echo "=== CPU Isolation Check ==="
cat /sys/devices/system/cpu/isolated

echo -e "\n=== CPU Governor ==="
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u

echo -e "\n=== C-States ==="
cat /sys/module/intel_idle/parameters/max_cstate

echo -e "\n=== IRQ Affinity ==="
grep eth0 /proc/interrupts

echo -e "\n=== Hugepages ==="
cat /proc/meminfo | grep Huge

echo -e "\n=== NUMA Topology ==="
numactl --hardware

echo -e "\n=== NIC Driver ==="
ethtool -i eth0

echo -e "\n=== NIC Queues ==="
ethtool -l eth0

echo -e "\n=== DPDK Binding ==="
dpdk-devbind.py --status
```

---

## 6️⃣ 完整部署 Checklist

### 硬體層

```
[✓] BIOS：關閉 Hyper-Threading
[✓] BIOS：關閉 C-States (C1E, C3, C6)
[✓] BIOS：關閉 P-States / Turbo Boost
[✓] BIOS：開啟 VT-d / IOMMU
[✓] BIOS：Performance Mode
[✓] 網卡：Intel X710 或 Mellanox ConnectX
[✓] 確認 NUMA 拓撲（NIC 在哪個 node）
```

### 系統層

```
[✓] GRUB：isolcpus=1-7
[✓] GRUB：nohz_full=1-7
[✓] GRUB：rcu_nocbs=1-7
[✓] GRUB：intel_pstate=disable
[✓] GRUB：intel_idle.max_cstate=0
[✓] GRUB：Hugepages 1GB
[✓] 關閉 irqbalance
[✓] IRQ 綁定到 CPU 0
[✓] CPU governor = performance
[✓] DPDK 網卡綁定 (vfio-pci)
[✓] 掛載 Hugepages
```

### 應用層

```
[✓] 使用 DPDK PMD
[✓] Busy polling (while(1) loop)
[✓] 綁定到隔離的 core (pthread_setaffinity_np)
[✓] SCHED_FIFO priority 99
[✓] Lock-free 資料結構
[✓] Cache line 對齊 (alignas(64))
[✓] 避免動態記憶體分配 (malloc/free)
[✓] 零拷貝設計 (直接操作 mbuf)
[✓] Prefetch + Branch hints
[✓] NUMA-aware memory allocation
```

---

## 7️⃣ 編譯與執行

### 安裝依賴

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y dpdk dpdk-dev libnuma-dev \
    build-essential cmake pkg-config

# 驗證 DPDK 版本
dpdk-devbind.py --version
```

### 編譯專案

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

### 配置系統（需 root）

```bash
# 執行 DPDK 設定腳本
sudo ../scripts/setup.sh

# 檢查配置
sudo ../scripts/check.sh
```

### 執行應用程式

```bash
# 方式 1：直接執行
sudo ./hft_app -l 2 -n 4 --socket-mem=1024

# 方式 2：使用腳本
sudo ../scripts/run.sh
```

---

## 8️⃣ 預期效果

### 效能指標

```
正確配置後的預期效果：

P50 Latency:  < 500 ns
P99 Latency:  < 1 μs (微秒)
P99.9:        < 5 μs
Jitter:       < 10 μs

吞吐量:       數百萬 pps (packets per second)
CPU 使用率:    100% (busy polling)
```

### 驗證方法

```bash
# 1. 檢查 CPU 是否真的隔離
taskset -cp $(pgrep hft_app)
# 應該顯示：pid XXX's current affinity list: 2

# 2. 檢查是否真的在 busy polling
top -H -p $(pgrep hft_app)
# CPU 應該接近 100%

# 3. 檢查 IRQ 是否正確分配
watch -n 1 'cat /proc/interrupts | grep eth0'
# IRQ 應該只在 CPU 0 上增長

# 4. 檢查記憶體是否在正確的 NUMA node
numastat -p $(pgrep hft_app)
```

---

## 9️⃣ 常見問題排除

### Q1: DPDK 初始化失敗

```bash
# 檢查 hugepages
cat /proc/meminfo | grep Huge

# 重新配置
echo 8 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages
```

### Q2: 網卡綁定失敗

```bash
# 確認網卡支援 DPDK
dpdk-devbind.py --status

# 確認 VFIO 模組已載入
lsmod | grep vfio

# 手動載入
modprobe vfio-pci
```

### Q3: Latency 仍然很高

```bash
# 檢查 CPU isolation
cat /sys/devices/system/cpu/isolated

# 檢查 C-States
cat /sys/module/intel_idle/parameters/max_cstate
# 應該是 0

# 檢查 CPU governor
cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
# 應該全部是 performance
```

### Q4: IRQ 仍打到 polling core

```bash
# 檢查 irqbalance 是否真的關閉
systemctl status irqbalance
# 應該是 inactive (dead)

# 手動設定 IRQ affinity
echo 1 > /proc/irq/XXX/smp_affinity
```

---

## 🔟 核心原則總結

### 五大支柱

```
1. CPU 隔離
   isolcpus + nohz_full + rcu_nocbs
   → 讓 CPU 變成專屬裸機

2. Busy Polling
   while(1) + 永遠不睡眠
   → 換 CPU 資源取得穩定 latency

3. 零拷貝
   直接操作 DPDK mbuf
   → 避免記憶體複製

4. Lock-free
   atomic + memory_order
   → 避免鎖競爭

5. NUMA 對齊
   NIC/core/memory 同 node
   → 避免跨 NUMA 存取
```

### 優化優先級

```
高優先級（必做）
├── CPU isolation 配置
├── IRQ 綁定
├── Hugepages
├── DPDK kernel bypass
└── NUMA 對齊

中優先級（重要）
├── Lock-free 資料結構
├── Cache line 對齊
├── 避免動態記憶體分配
└── Prefetch

低優先級（加分）
├── Branch hints
├── 編譯器優化 flags
└── 微調 DPDK 參數
```

---

## 📚 參考資源

### 官方文件

- [DPDK Documentation](https://doc.dpdk.org/)
- [Intel X710 Datasheet](https://www.intel.com/content/www/us/en/products/docs/network-io/ethernet/700-series-controllers.html)
- [Linux Kernel Real-Time](https://wiki.linuxfoundation.org/realtime/start)

### 進階閱讀

- [DPDK Performance Tuning](https://doc.dpdk.org/guides/linux_gsg/nic_perf_intel_platform.html)
- [Linux Low Latency Tuning](https://rigtorp.se/low-latency-guide/)
- [Lock-free Programming](https://preshing.com/20120612/an-introduction-to-lock-free-programming/)

---

## 📄 授權與貢獻

本文件提供參考使用，實際部署請根據具體硬體與需求調整。

---

**記住**：高頻系統優化不是追求「快」，而是追求「穩定的快」。

> **"It's not about being fast, it's about being consistently fast."**
