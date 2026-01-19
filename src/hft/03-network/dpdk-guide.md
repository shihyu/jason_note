# DPDK 網卡完整指南

## 目錄
- [什麼是 DPDK 網卡](#什麼是-dpdk-網卡)
- [DPDK 網卡的特點](#dpdk-網卡的特點)
- [一般上網能否走 DPDK](#一般上網能否走-dpdk)
- [實際部署方式](#實際部署方式)
- [常見誤解](#常見誤解)
- [重要補充](#重要補充)
- [實際建議](#實際建議)

---

## 什麼是 DPDK 網卡

DPDK (Data Plane Development Kit) 支援的網卡和一般網卡在架構上有顯著差異。DPDK 是一套使用者空間的高性能封包處理框架。

### 常見支援 DPDK 的網卡品牌
- Intel (82599、X710 系列)
- Mellanox
- Broadcom
- 其他企業級網卡

---

## DPDK 網卡的特點

### 核心特性

1. **繞過核心 (Kernel Bypass)**
   - DPDK 應用程式直接在使用者空間操作網卡
   - 繞過 Linux 核心的網路堆疊
   - 減少上下文切換和系統呼叫

2. **輪詢模式 (Poll Mode Driver, PMD)**
   - 使用持續輪詢取代中斷驅動
   - CPU 會被「吃滿」到 100%，即使沒有流量
   - 換取更低的延遲和更高的吞吐量

3. **零拷貝 (Zero Copy)**
   - 減少資料在記憶體間的複製次數
   - 直接從網卡 DMA 到應用程式記憶體

4. **CPU 綁定 (CPU Affinity)**
   - 將特定 CPU 核心專門用於封包處理
   - 避免核心間的快取同步開銷

### 主要應用場景

- 路由器/交換機
- 防火牆/負載均衡器
- 5G 核心網
- 高頻交易系統
- NFV (Network Function Virtualization)
- DPI (Deep Packet Inspection)

---

## 一般上網能否走 DPDK

### 答案：技術上可行但實際上不適合

#### 為什麼不適合一般上網？

1. **需要專用應用程式**
   - DPDK 繞過了 Linux 核心網路堆疊
   - 一般的瀏覽器、應用程式無法直接使用 DPDK 網卡
   - 需要用 DPDK API 重新開發應用

2. **資源消耗大**
   - 需要獨佔 CPU 核心持續輪詢
   - 對於一般上網來說太浪費資源
   - 一個 DPDK 應用可能佔用 4-8 個核心

3. **使用場景不同**
   - 一般上網：延遲要求不高，頻寬需求適中
   - DPDK：需要處理數百萬 pps (packets per second)

---

## 實際部署方式

### 雙網卡配置（推薦做法）

如果一台機器需要同時做一般上網和高性能封包處理：

#### 網卡 1：一般網卡
- 走 Linux 核心網路堆疊
- **用途：**
  - SSH 遠端管理
  - 系統更新
  - 監控和日誌
  - 一般網路存取

#### 網卡 2：DPDK 網卡
- 走 DPDK 使用者空間
- 綁定到 DPDK 驅動 (如 `vfio-pci` 或 `uio_pci_generic`)
- **用途：**
  - 專門處理高速封包
  - 在高頻交易中處理市場數據、下單等
  - 高吞吐量的封包轉發

### 高頻交易的典型架構

```
[交易所] ←→ [DPDK 網卡] ←→ [DPDK 應用程式 (市場數據/下單)]
                              
[管理網路] ←→ [一般網卡] ←→ [系統管理/監控/SSH]
```

### 為什麼需要分開？

1. **隔離風險**
   - DPDK 網卡綁定後，系統就看不到它
   - 如果只有一張網卡，可能連 SSH 都連不進去

2. **管理方便**
   - 保留一張網卡用於管理
   - 不影響 DPDK 應用的性能

3. **網路分離**
   - 交易網路和管理網路實體隔離
   - 提高安全性

---

## 常見誤解

### 誤解 1：DPDK 網卡 = 特殊硬體

**錯誤認知：** 需要購買特殊的「DPDK 網卡」硬體

**實際情況：**
- 大多數企業級網卡都支援 DPDK
- 關鍵在於**驅動程式和軟體配置**
- 同一張網卡可以在「一般模式」和「DPDK 模式」之間切換
- 透過綁定/解綁驅動來切換模式

### 誤解 2：綁定後網卡「消失」了

**實際情況：**
- 一旦網卡綁定到 DPDK 驅動 (如 `vfio-pci`)
- `ifconfig` 或 `ip addr` 就看不到它
- 系統層面完全失去對該網卡的控制
- 必須用 `dpdk-devbind.py` 工具來管理綁定/解綁

**示例：**
```bash
# 查看網卡狀態
dpdk-devbind.py --status

# 綁定網卡到 DPDK
dpdk-devbind.py --bind=vfio-pci 0000:03:00.0

# 解綁回核心驅動
dpdk-devbind.py --bind=ixgbe 0000:03:00.0
```

### 誤解 3：CPU 被「吃滿」是異常

**實際情況：**
- DPDK 的 PMD 會讓 CPU 核心使用率達到 100%
- **即使沒有流量也是 100%**
- 這是**正常現象**，因為它持續輪詢網卡
- 需要預留專用 CPU 核心，不能跟一般應用競爭

### 誤解 4：DPDK 一定比核心網路堆疊快

**實際情況：**
- 對於低流量場景 (<10 Gbps)，一般核心網路堆疊可能更省資源
- DPDK 的優勢在於**高封包率**和**低延遲**
- 如果只是頻寬需求，不一定需要 DPDK
- 需要根據實際場景評估

---

## 重要補充

### 1. Huge Pages 記憶體需求

DPDK 需要使用 Huge Pages 來提高記憶體存取效率。

```bash
# 配置 2MB 的 Huge Pages (1024 個)
echo 1024 > /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages

# 或配置 1GB 的 Huge Pages
echo 4 > /sys/kernel/mm/hugepages/hugepages-1048576kB/nr_hugepages

# 掛載 hugetlbfs
mkdir /mnt/huge
mount -t hugetlbfs nodev /mnt/huge
```

**注意事項：**
- 必須事先分配，不能動態取用
- 通常需要幾 GB 的 Huge Pages
- 系統其他程式無法使用這些記憶體
- 重開機後需要重新配置

### 2. NUMA 架構考量

在多 CPU 插槽的伺服器上：

- 網卡、CPU、記憶體最好在**同一個 NUMA 節點**
- 跨 NUMA 存取會有顯著的性能損失
- 需要配置 CPU affinity 和記憶體分配策略

```bash
# 查看 NUMA 拓撲
numactl --hardware

# 查看網卡所在的 NUMA 節點
cat /sys/class/net/eth0/device/numa_node
```

### 3. 不支援所有協定特性

**限制：**
- DPDK 需要自己實現網路堆疊
- TCP/IP、TLS 等都需要用 DPDK 相容的函式庫
- 不像核心網路堆疊那樣功能完整

**解決方案：**
- 使用第三方網路堆疊：mTCP, f-stack, TLDK
- 或只處理特定協定（如 UDP、Raw Ethernet）

### 4. SR-IOV 虛擬化場景

**功能：**
- 一張實體網卡可以虛擬成多個 VF (Virtual Function)
- 每個 VM 可以獨立使用 DPDK
- 實現接近原生性能的虛擬化網路

**要求：**
- 硬體支援 SR-IOV
- BIOS 需要啟用 VT-d / AMD-Vi
- 配置更複雜

```bash
# 啟用 SR-IOV，創建 4 個 VF
echo 4 > /sys/class/net/eth0/device/sriov_numvfs
```

### 5. 成本考量

**資源成本：**
- **CPU 核心專用：** 一個 DPDK 應用可能佔用 4-8 個核心
- **記憶體佔用：** Huge Pages 可能佔用數 GB
- **網卡成本：** 高性能網卡價格較高

**人力成本：**
- 需要專業知識，學習曲線陡峭
- 不像一般 socket 程式設計簡單
- 維護和除錯需要專門技能

### 6. 除錯困難

**挑戰：**
- 無法用 `tcpdump`、`wireshark` 直接抓包
- 需要在應用層實現封包捕獲
- 系統工具 (`netstat`, `ss`) 看不到連線狀態
- 需要自己實現監控和診斷工具

**解決方案：**
- 使用 DPDK 的 `pdump` 函式庫
- 實現自訂的統計和監控
- 使用 DPDK Telemetry API

### 7. 核心網路功能缺失

**DPDK 不支援或需要自己實現：**
- iptables / netfilter
- 路由表自動更新
- ARP 自動處理
- ICMP (ping)
- 大部分的 socket 選項

### 8. 驅動和核心版本相依性

**注意：**
- DPDK 版本與 Linux 核心版本有相依性
- 升級系統可能影響 DPDK 應用
- 需要仔細規劃升級策略

### 9. 中斷 Coalescing 和輪詢的權衡

**考量因素：**
- 輪詢模式：低延遲，高 CPU 使用率
- 中斷模式：省 CPU，延遲較高
- 有些場景可以使用混合模式

### 10. 不適合所有網路應用

**DPDK 適合：**
- 高封包率 (>1M pps)
- 低延遲要求 (<10 μs)
- 封包處理邏輯相對簡單

**DPDK 不適合：**
- 複雜的應用層協定處理
- 需要完整 TCP/IP 堆疊特性
- 低流量、低頻率的應用

---

## 實際建議

### 對於高頻交易場景

#### 1. 一定要量測
- **先確認瓶頸：** 是否真的遇到核心網路堆疊瓶頸
- **基準測試：** 測量當前系統的延遲和吞吐量
- **成本效益分析：** DPDK 的收益是否值得投入成本

#### 2. 漸進式部署
- **先優化核心網路堆疊：**
  - 調整 IRQ affinity
  - 啟用 RSS (Receive Side Scaling)
  - 使用 SO_BUSY_POLL
  - 調整核心參數

- **考慮其他方案：**
  - Kernel bypass 的其他方案 (如 Solarflare's OpenOnload)
  - XDP (eXpress Data Path)
  - AF_XDP sockets

- **最後才考慮 DPDK**

#### 3. 團隊技能
- 確保團隊有能力維護 DPDK 應用
- 投資培訓和知識轉移
- 建立完善的文件和運維流程

#### 4. 測試環境
- 建立與生產環境相同的測試環境
- 充分測試各種場景
- 準備回退方案

#### 5. 監控和告警
- 實現完善的監控系統
- 監控封包丟失、延遲、吞吐量
- 設定合理的告警閾值

### 架構設計建議

1. **保留管理網路**
   - 至少保留一張網卡用於管理
   - 使用 out-of-band 管理網路

2. **高可用性**
   - 考慮使用主備或負載均衡
   - 實現快速故障轉移

3. **可觀測性**
   - 實現詳細的日誌記錄
   - 提供性能指標輸出
   - 整合到現有監控系統

4. **安全性**
   - DPDK 應用也需要考慮安全
   - 實現必要的存取控制
   - 定期安全審計

---

## 總結

### DPDK 的優勢
- 極低延遲 (微秒級)
- 極高吞吐量 (數千萬 pps)
- 完全控制封包處理流程

### DPDK 的代價
- 高 CPU 使用率
- 開發和維護複雜度高
- 需要專業知識
- 調試困難

### 何時使用 DPDK
- 高頻交易
- 電信級網路設備
- 需要極致性能的場景

### 何時不用 DPDK
- 一般 web 應用
- 低頻率網路通訊
- 資源受限的環境

---

## 參考資源

- [DPDK 官方網站](https://www.dpdk.org/)
- [DPDK 官方文件](https://doc.dpdk.org/)
- [DPDK Getting Started Guide](https://doc.dpdk.org/guides/linux_gsg/index.html)
- [Intel DPDK 教學](https://www.intel.com/content/www/us/en/developer/topic-technology/open/data-plane-development-kit/overview.html)

---

**文件版本：** 1.0  
**最後更新：** 2026-01-19
