# 高頻交易系統完整指南
## HFT OS 調校 + 開源項目 + 台灣市場實踐

---

## 目錄
1. [HFT 系統 OS 調校核心](#hft-系統-os-調校核心)
2. [GitHub 開源項目推薦](#github-開源項目推薦)
3. [台灣市場具體實踐：解封包 & 收報價](#台灣市場具體實踐解封包--收報價)
4. [效能測試工具](#效能測試工具)
5. [術語速查表](#術語速查表)

---

## HFT 系統 OS 調校核心

### 背景
高頻量化交易（HFT）是奈秒級戰爭。要從毫秒精度（傳統）降到微秒精度（HFT），必須馴服：
- 作業系統排程不確定性
- 硬體資源爭用（超執行緒、快取、NUMA）
- 傳統 I/O 瓶頸

**目標**：將關鍵路徑延遲從 ±50μs 壓縮到 ±1μs，平均延遲 <20μs。

### 1. 核心隔離：消除資源競爭

#### 1.1 停用超執行緒 & CPU Pinning

**為什麼**：
- 超執行緒（HT）將實體核模擬為 2 個邏輯核，共享執行單元和 L1/L2 快取
- 兄弟執行緒的 AVX 計算會完全佔用浮點單元，導致交易線程被阻塞
- 快取汙染：兄弟線程的資料會驅逐你的熱點數據

**實測結果**：停用 HT 可降低延遲 22%，更重要的是大幅降低 Jitter。

**設定方法**：
```bash
# 檢視實體核拓撲
lscpu -p | grep -v '#' | awk -F, '{print $1,$3}' | sort -t, -k2n

# 綁定策略進程到實體核 8-15（跳過 HT 核）
taskset -c 8-15 ./strategy_engine
```

**C++ 實作**：
```cpp
#include <sched.h>
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
for(int i=8; i<=15; i++) CPU_SET(i, &cpuset);
sched_setaffinity(0, sizeof(cpuset), &cpuset);
```

#### 1.2 中斷重定向

**為什麼**：
- 網卡中斷預設由 CPU 0 處理
- 中斷搶佔交易線程，造成上下文切換
- 中斷程序存取記憶體會汙染 L1d 快取
- 單次中斷可增加 ~300ns 延遲

**設定方法**：
```bash
# 將 eth0 中斷綁定到 CPU 16-23
IRQ=$(awk -F: '/eth0/{print $1}' /proc/interrupts | head -1)
echo "fff000" > /proc/irq/$IRQ/smp_affinity
```

#### 1.3 核心排程隔離

**為什麼**：
- 即使 CPU 綁定，核心線程（ksoftirqd、kworker）仍可能搶佔
- 時鐘中斷每 ms 檢查一次有無其他任務要執行
- RCU 回調可能在關鍵線程上執行

**設定方法**（編輯 GRUB）：
```bash
# /etc/default/grub
grub_cmdline="isolcpus=8-15 nohz_full=8-15 rcu_nocbs=8-15"

# 應用設定
sudo grub2-mkconfig -o /boot/grub2/grub.cfg
```

| 參數 | 功能 |
|------|------|
| `isolcpus=8-15` | 隔離這些核心，核心調度器不會在其上運行普通進程 |
| `nohz_full=8-15` | 關閉時鐘中斷，讓這些核心安靜執行（無週期性中斷） |
| `rcu_nocbs=8-15` | RCU 回調卸載到其他非隔離核心 |

---

### 2. NUMA 記憶體最佳化

#### 2.1 記憶體本地化綁定

**為什麼**：
- NUMA 系統中，本地節點存取速度最快
- 遠端節點存取延遲高 50-100%
- 跨節點延遲不確定性很大

**設定方法**：
```bash
# 啟動時綁定到 Node 0
numactl --cpunodebind=0 --membind=0 ./strategy

# 檢視 NUMA 拓撲
numactl --hardware
```

**程式碼控制**：
```cpp
#include <numa.h>
numa_set_localalloc();          // 優先本地分配
void* mem = numa_alloc_local(1024*1024);  // 分配本地記憶體
```

#### 2.2 記憶體鎖定（mlock）

**為什麼**：
- 預設 OS 會根據記憶體壓力換頁到磁碟
- 執行時換入導致毫秒級不可預測停頓
- `mlock` 保證記憶體永不被換出

**設定方法**：
```bash
# 增大記憶體鎖定配額（預設 64KB）
sudo sysctl vm.lock_limit_kb=1048576  # 設為 1GB
echo "vm.lock_limit_kb=1048576" >> /etc/sysctl.conf

# 停用交換空間
sudo swapoff -a
```

**程式碼實作**：
```cpp
#include <sys/mman.h>

void* allocateLockedMemory(size_t size) {
    void* mem;
    if (posix_memalign(&mem, sysconf(_SC_PAGESIZE), size) != 0) {
        return nullptr;
    }
    
    if (mlock(mem, size) == -1) {
        free(mem);
        return nullptr;
    }
    
    return mem;
}
```

#### 2.3 大頁記憶體（HugePage）

**為什麼**：
- 預設頁大小 4KB，TLB 未命中頻繁
- 大頁（2MB/1GB）使 TLB 條目覆蓋更大記憶體範圍
- 減少頁表遍歷開銷

**設定方法**：
```bash
# 預留 1024 個 2MB 大頁
sudo vim /etc/sysctl.conf
vm.nr_hugepages = 1024

# 關閉透明大頁（THP）避免不確定性
sudo sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'

# 編輯 GRUB 永久關閉 THP
# /etc/default/grub
transparent_hugepage=never
```

**程式碼實作**：
```cpp
#include <sys/mman.h>

void* allocateHuge(size_t size) {
    int flags = MAP_PRIVATE | MAP_ANON | MAP_HUGETLB;
    int prot = PROT_READ | PROT_WRITE;
    void* ptr = mmap(nullptr, size, prot, flags, -1, 0);
    
    if (ptr != MAP_FAILED) {
        mlock(ptr, size);  // 再加鎖
    }
    
    return ptr == MAP_FAILED ? nullptr : ptr;
}
```

#### 2.4 記憶體預取

**為什麼**：
- 鎖定保證實體駐留，但虛擬到實體映射可能未建立
- 預取在初始化階段主動觸發所有缺頁中斷

**程式碼實作**：
```cpp
// 手動觸發缺頁中斷
memset(lockedMem, 0, memSize);

// 預取到 L1 快取
__builtin_prefetch(lockedMem, 0, 3);
```

---

### 3. 快取最佳化

#### 3.1 快取隔離（Intel CAT）

**為什麼**：
- 所有核心共享 L3 快取
- 其他核心的存取會驅逐你的快取行
- CAT 可劃分 L3 為多個獨立區域

**設定方法**：
```bash
# 安裝 Intel RDT 工具
sudo apt install intel-cmt-cat

# 驗證硬體支援
grep -E 'cat_l3' /proc/cpuinfo
pqos -d

# 設定快取隔離
sudo pqos -e 'llc:1=0xff0'   # COS1 分配中間 8 位快取
sudo pqos -a 'llc:1=1234'    # 綁定 PID 1234 到 COS1

# 監控
pqos -m all:1
```

#### 3.2 資料結構對齊（消除偽共享）

**為什麼**：
- 快取行 64 位元組，多線程存取同一快取行內的不同變數導致效能崩潰
- 對齊至快取行可消除偽共享

**程式碼實作**：
```cpp
struct __attribute__((aligned(64))) MarketData {
    std::atomic<uint64_t> timestamp;
    double bid_price;
    int64_t bid_qty;
    // 剩餘空間自動填充至 64 位元組
};

// 驗證對齊
static_assert(sizeof(MarketData) % 64 == 0, "Alignment failed");
```

#### 3.3 SIMD 指令加速

**為什麼**：
- 一條指令處理多個資料（e.g., AVX-512 處理 8 個浮點數同時）
- 對高頻策略的大量計算提速

**程式碼範例**：
```cpp
#include <immintrin.h>

// 計算 8 支股票的價差（AVX-512）
__m512 calculate_spread(const float* bid, const float* ask) {
    __m512 bid_v = _mm512_loadu_ps(bid);
    __m512 ask_v = _mm512_loadu_ps(ask);
    return _mm512_sub_ps(ask_v, bid_v);
}
```

---

### 4. 調校優先級策略

| 優先級 | 技術方向 | 核心價值 | 關鍵手段 |
|--------|---------|----------|----------|
| 1 | **核心隔離** | 消除 OS 排程和硬體中斷不確定性 | isolcpus、中斷重定向、CPU Pinning |
| 2 | **NUMA 記憶體** | 解決跨節點延遲翻倍 | numactl 綁核、hugepage、mlock |
| 3 | **快取控制** | 避免共享快取爭用 | CAT 隔離、資料對齐、SIMD |

---

## GitHub 開源項目推薦

### 1. 低延遲撮合引擎（C/C++）

#### 1.1 RapidTrader
- **Repo**: `jmsadair/RapidTrader`
- **語言**: C++17
- **特點**: 低延遲撮合、lock-free 資料結構
- **應用**: 直接綁定到隔離核心執行

#### 1.2 SubMicroTrading
- **Repo**: `gsitgithub/SubMicroTrading`
- **語言**: C++
- **特點**: Ultra-low latency algo trading framework，component-based 架構
- **應用**: 線程拆分設計已為 CPU pin 做好準備

#### 1.3 其他 HFT 撮合系統
- GitHub topic: `hft-trading` (C++ 為主)
- GitHub topic: `kernel-bypass` (kernel bypass 技術集合)

### 2. NUMA / HugePage / 記憶體調校（C + Rust）

#### 2.1 HugePageDemo (Rust)
- **Repo**: `evanj/hugepagedemo`
- **內容**: 
  - `mmap() + MAP_HUGETLB / MAP_HUGE_1GB` 配置
  - 4K vs 2M vs 1G 頁大小的 latency/throughput benchmark
  - 實測數據對比
- **應用**: 直接借鑒記憶體分配和 benchmark 方法

#### 2.2 HFT 伺服器設定
- **Repo**: `twanas/hft-server-settings`
- **內容**:
  - `isolcpus` / `nohz_full` / `rcu_nocbs` 設定
  - hugepages 配置腳本
  - `numactl` 綁定示例
- **應用**: OS 層調校 check list

#### 2.3 Low Latency System 學習倉庫
- **Repo**: `ashavijit/Lowlatencysystem`
- **內容**: Kernel bypass、NUMA、快取調校的學習資源集合
- **應用**: 當作你的「實作清單」延伸

### 3. Kernel Bypass / DPDK / 網路加速（C/C++）

#### 3.1 PcapPlusPlus
- **Repo**: `pcapplusplus/pcapplusplus`
- **語言**: C++ (封裝 DPDK C 接口)
- **特點**: 
  - Kernel bypass（DPDK 驅動）收發封包
  - Zero-copy 技術
  - Polling mode driver
- **應用**: 如果想先用 C++ 庫玩 DPDK 再下探純 C API

#### 3.2 DPDK 相關專案集合
- GitHub topic: `dpdk` (眾多 C 專案)
- 包括:
  - L2/L3 forwarding samples
  - 高性能代理
  - 負載均衡器
- **關鍵特性都有**: CPU pin、hugepage、NUMA aware memory pool、輪詢隊列

#### 3.3 Rust + DPDK Wrapper
- `dpdk-rs`、`capsule` 等 Rust DPDK wrapper
- 從 `dpdk` topic 和 `kernel-bypass` topic 中尋找
- 展示如何：
  - 在 Rust 端封裝 unsafe DPDK C API
  - 保證 zero-copy + lock-free
  - Cache line 對齐

### 4. 技術文章 / 調查報告

#### 4.1 Hardware Low Latency Techniques
- **來源**: `zhanghaowx.github.io/Blog-Escape/low-latency-techniques`
- **內容**: Tickless kernel、CPU isolation、Hyper-threading、NUMA pinning
- **應用**: Cross-check 你的理解

#### 4.2 2025 A 股低延遲技術調研
- **來源**: `heth.ink/AShareLowLatency/`
- **內容**: 市場行情解析、延遲測試、工具推薦
- **應用**: 對標台灣市場的技術路線

---

## 台灣市場具體實踐：解封包 & 收報價

### 背景：主機共置（Co-Location）

台灣交易所（TWSE）與期貨交易所（TAIFEX）都提供主機共置服務，讓券商在交易所機房內部署伺服器，直接接收 multicast 行情。

### 1. 行情協議概覽

| 交易所 | 協議 | 傳輸 | 內容 |
|--------|------|------|------|
| **TWSE** (股票) | 自定義電文 | Multicast UDP + TCP | 逐筆成交、最佳5檔、成交統計 |
| **TAIFEX** (期貨) | TMP (Taifex Message Protocol) | Multicast UDP + TCP | 期貨逐筆、選擇權、指數 |

**官方文件**:
- 臺灣證券交易所資訊傳輸作業手冊（定義所有電文格式）
- 臺灣期貨交易所資訊傳輸作業手冊

### 2. 解封包流程

```
交易所 Multicast (224.x.x.x:port)
   ↓
券商 NIC 接收
   ↓
DPDK 或 kernel bypass 驅動
   ↓
用戶態應用（策略引擎）
   ↓
解析 TWSE 電文格式
   ↓
更新本地 orderbook / tick data
   ↓
觸發交易信號
```

### 3. C++ 解封包實作框架

```cpp
#include <rte_eal.h>
#include <rte_ethdev.h>
#include <stdint.h>

// 訊息類型定義（根據 TWSE 文件）
enum TWSEMessageType {
    TWSE_MSG_TRADE = 1,      // 成交訊息
    TWSE_MSG_QUOTE = 2,      // 報價（最佳5檔）
    TWSE_MSG_STAT = 3,       // 統計資訊
};

struct OrderBook {
    double bid[5], ask[5];          // 買賣5檔價格
    int64_t bid_qty[5], ask_qty[5]; // 對應量
    uint64_t timestamp;             // 奈秒級時戳
};

// 解析最佳5檔報價
void parse_quote_message(const uint8_t* payload, OrderBook& book) {
    // 根據 TWSE 電文格式，位元組偏移位置
    // payload[0] = 訊息類型
    // payload[1:2] = 代碼長度
    // payload[3:8] = 股票代碼
    // payload[9:16] = 最佳買價 (8 bytes, big endian)
    // payload[17:24] = 最佳賣價
    // ...依此類推
    
    uint64_t bid_price = be64toh(*(uint64_t*)(payload + 9));
    uint64_t ask_price = be64toh(*(uint64_t*)(payload + 17));
    
    book.bid[0] = bid_price / 10000.0;  // 假設 4 位小數
    book.ask[0] = ask_price / 10000.0;
}

// HFT 主迴圈
void hft_engine() {
    OrderBook book;
    
    // 初始化 DPDK EAL
    rte_eal_init(0, nullptr);
    
    uint16_t port_id = 0;
    rte_eth_dev_start(port_id);
    
    while(trading_active) {
        // 從網卡接收 multicast 行情（32 個封包批次）
        struct rte_mbuf* pkts[32];
        uint16_t nb_rx = rte_eth_rx_burst(port_id, 0, pkts, 32);
        
        for(uint16_t i = 0; i < nb_rx; i++) {
            struct rte_mbuf* pkt = pkts[i];
            
            // 去掉 L2/L3/L4 header（MAC/IP/UDP），指向 TWSE 電文
            uint8_t* payload = rte_pktmbuf_mtod_offset(pkt, uint8_t*,
                              sizeof(struct ether_hdr) +
                              sizeof(struct ipv4_hdr) +
                              sizeof(struct udp_hdr));
            
            // 路由：根據訊息類型分發
            uint8_t msg_type = payload[0];
            
            if (msg_type == TWSE_MSG_QUOTE) {
                parse_quote_message(payload, book);
            } else if (msg_type == TWSE_MSG_TRADE) {
                parse_trade_message(payload, book);
            }
            
            // 記錄時戳（CPU 時鐘，奈秒級精度）
            book.timestamp = rdtsc();
            
            // 檢查交易信號
            if (should_buy(book)) {
                // 執行買單邏輯
                send_buy_order(book.ask[0], 100);
            }
            
            // 釋放 mbuf
            rte_pktmbuf_free(pkt);
        }
    }
}
```

### 4. 「報價」是什麼

#### Level 1：最佳報價（5 檔）
- **內容**: 最佳買/賣 5 檔及其成交量
- **更新頻率**: 逐筆撮合後立即推送（~1-10ms）
- **來源**: TWSE 官方 multicast

#### Level 2：完整 Orderbook
- **內容**: 所有掛單快照
- **台灣市場**: 尚未完全開放 Level 2（不同於美國 NASDAQ）
- **商業方案**: 部分券商提供 Level 2 API

#### Level 3：逐筆成交（Tick Data）
- **內容**: 每一筆成交的時間、價格、量
- **更新頻率**: 微秒到毫秒級
- **來源**: TWSE multicast

### 5. 實戰路徑

#### 短期（1-2 個月）：用券商 API
```
1. 選擇支持低延遲 API 的券商
   - 群益、元大、永豐 等
   
2. 接入 tick data stream
   - 通常是 TCP push 或 gRPC
   
3. 自寫 C++ 解析層
   - tick → orderbook → 交易信號
```

#### 中期（2-4 個月）：Co-Location + 自寫解析
```
1. 申請 TWSE co-location
   - 成本: NT$10-50k/月 + 建置費
   - 等待: 1-2 個月核准
   
2. 部署自己的伺服器在 co-location 機房
   
3. 訂閱 TWSE multicast 行情
   - IP: 224.x.x.x (TWSE 告知)
   - Port: 特定 UDP port
   
4. 用 DPDK 或 kernel bypass 收封包
   
5. 按 TWSE 電文手冊解析
```

#### 長期（4-6 個月）：極致優化
```
1. DPDK + Solarflare NIC
   - 進一步降低延遲到 μs 級
   
2. 應用 OS 調校全套
   - CPU pin / NUMA / hugepage / isolcpus
   
3. 考慮 FPGA 加速（預算允許）
   - 在網卡端做初步解析
```

---

## 效能測試工具

### 1. 延遲測試

#### cyclictest（實時延遲測試）
```bash
sudo apt-get install rt-tests

# 測試系統延遲抖動
sudo cyclictest -p 99 -t 1 -n -i 1000 -l 100000 -h 1000 -q
```

#### 自製延遲測試程式
```cpp
#include <chrono>
#include <vector>
#include <algorithm>

void measure_latency() {
    const int iterations = 1000000;
    std::vector<long> latencies;
    
    for(int i = 0; i < iterations; i++) {
        auto start = std::chrono::high_resolution_clock::now();
        // 你的交易邏輯
        auto end = std::chrono::high_resolution_clock::now();
        
        auto latency = std::chrono::duration_cast<std::chrono::nanoseconds>
                      (end - start).count();
        latencies.push_back(latency);
    }
    
    std::sort(latencies.begin(), latencies.end());
    
    std::cout << "P50: " << latencies[iterations * 0.50] << "ns\n";
    std::cout << "P99: " << latencies[iterations * 0.99] << "ns\n";
    std::cout << "P99.9: " << latencies[iterations * 0.999] << "ns\n";
}
```

### 2. CPU 和中斷監控

#### perf（系統效能分析）
```bash
sudo apt-get install linux-tools-generic

# 監控 CPU 事件
sudo perf stat -C 8-15 ./strategy_engine

# 快取命中率
sudo perf stat -e cache-references,cache-misses ./strategy_engine

# 上下文切換
sudo perf stat -e context-switches,cpu-migrations ./strategy_engine
```

#### 監控中斷
```bash
# 即時監控中斷分佈
watch -n 1 'cat /proc/interrupts | grep eth0'

# 檢查 CPU 親和性
for i in /proc/irq/*/smp_affinity; do 
    echo "$i: $(cat $i)"
done
```

### 3. NUMA 和記憶體測試

#### numactl 測試
```bash
# 檢視 NUMA 拓撲
numactl --hardware

# 本地節點測試
numactl --cpunodebind=0 --membind=0 ./memory_test

# 遠端節點測試
numactl --cpunodebind=0 --membind=1 ./memory_test
```

### 4. 快取效能測試

#### pqos（快取隔離監控）
```bash
sudo apt install intel-cmt-cat

# 監控 L3 快取使用
sudo pqos -m llc:1

# 測試隔離效果前後
sudo pqos -m all:1 -t 10
```

### 5. 網路延遲測試

#### sockperf（Socket 效能測試）
```bash
# Server 端
./sockperf server -i 192.168.1.100 -p 12345

# Client 測試
./sockperf ping-pong -i 192.168.1.100 -p 12345 -t 60
```

### 6. 整合測試腳本

```bash
#!/bin/bash
# performance_test.sh

echo "=== HFT System Performance Test ==="

echo "1. System Configuration:"
echo "CPU Isolation: $(cat /proc/cmdline | grep isolcpus)"
echo "Huge Pages: $(grep HugePages_Total /proc/meminfo)"

echo -e "\n2. CPU Latency Test:"
sudo cyclictest -p 99 -t 1 -n -i 1000 -l 10000 -h 100 -q | tail -n 10

echo -e "\n3. Memory Latency:"
sudo numactl --hardware | grep "node distances"

echo -e "\n4. Cache Performance:"
sudo perf stat -e cache-references,cache-misses sleep 1 2>&1 | grep cache

echo -e "\n5. Network Latency:"
ping -c 100 -i 0.001 localhost | tail -n 3

echo -e "\n=== Test Complete ==="
```

### 7. 效能基準對比

| 指標 | 優化前 | 優化後 | 測試工具 |
|------|--------|--------|----------|
| CPU 延遲抖動 | ±50μs | ±1μs | cyclictest |
| 平均延遲 | 100μs | <20μs | 自製測試程式 |
| 快取命中率 | 85% | >98% | perf stat |
| NUMA 遠端存取 | +50% | 0% | numactl |
| 網路 RTT | 50μs | <10μs | sockperf |
| 上下文切換 | >1000/s | <100/s | perf stat |

---

## 術語速查表

| 術語 | 全稱 | 白話解釋 |
|------|------|----------|
| HFT | High-Frequency Trading | 高頻交易 |
| CFS | Completely Fair Scheduler | Linux 公平排程器 |
| IRQ | Interrupt Request | 中斷請求 |
| NUMA | Non-Uniform Memory Access | 非統一記憶體存取 |
| TLB | Translation Lookaside Buffer | 地址轉換緩衝 |
| Cache Line | - | 快取最小單位（通常 64 bytes） |
| False Sharing | - | 偽共享，多線程對同一快取行競爭 |
| Page Fault | - | 缺頁中斷 |
| Jitter | - | 延遲不穩定程度 |
| SIMD | Single Instruction Multiple Data | 單指令多資料 |
| DPDK | Data Plane Development Kit | 數據平面開發套件 |
| CAT | Cache Allocation Technology | Intel 快取分配技術 |
| HugePages | - | 大頁記憶體（2MB/1GB） |
| Co-Location | - | 主機共置，伺服器放在交易所機房 |
| Kernel Bypass | - | 繞過核心直接處理網路 |
| Multicast | - | 多播，同時發送給多個接收方 |
| AVX | Advanced Vector Extensions | Intel SIMD 擴充指令集 |

---

## 下一步：核心旁路技術實踐

儘管系統層最佳化已將延遲壓至微秒級，**網路 I/O 仍是最堅固的效能壁壘**。

傳統核心網路協議堆疊的瓶頸：
- 協議堆疊處理耗時 >10μs
- 多次資料拷貝
- 不確定的 TCP 重傳

**解決方案**：核心旁路技術（DPDK、XDP、Solarflare）

- **消除核心開銷**：避免上下文切換
- **零拷貝**：NIC DMA 直接到用戶空間
- **輪詢驅動**：替代中斷，降低延遲
- **線速處理**：達到網卡硬體極限

預期效果：端到端延遲進一步降至 **<1μs**，實現真正的奈秒級交易系統。

---

## 快速參考：調校檢查表

- [ ] 禁用超執行緒或分離關鍵核心
- [ ] 設定 `isolcpus` / `nohz_full` / `rcu_nocbs`
- [ ] CPU pinning：綁定策略進程到實體核
- [ ] 中斷重定向：網卡中斷指向非隔離核心
- [ ] NUMA 綁定：核心和記憶體綁到同一節點
- [ ] 記憶體鎖定：`mlock` + `madvise`
- [ ] 大頁配置：預留 hugepages，停用 THP
- [ ] 記憶體預取：初始化時觸發所有缺頁中斷
- [ ] 快取隔離：用 CAT 劃分 L3 區域
- [ ] 資料對齐：消除偽共享（64 bytes 對齐）
- [ ] SIMD 優化：用 AVX/AVX-512 向量化計算
- [ ] 性能測試：用 cyclictest / perf / numactl 驗證

---

*本文基於高頻交易系統 OS 調校最佳實踐、GitHub 開源項目調研、以及台灣市場具體實踐整理。*
