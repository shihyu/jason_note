# 高頻交易系統：作業系統效能調校實踐

## 背景介紹

高頻量化交易（HFT）是一場發生在奈秒(Nanosecond, ns)尺度上的戰爭。當傳統交易系統還在以毫秒(Millisecond, ms)為單位衡量效能時，HFT系統必須在微秒(Microsecond, μs)乃至奈秒(ns)級別進行競爭。這意味著任何微小的作業系統開銷或硬體資源爭用，都可能導致關鍵訂單流處理延遲，從而錯失最佳成交價或在訂單佇列中落後。

### 核心挑戰

核心挑戰在於馴服作業系統和硬體平台，消除其引入的非確定性和額外延遲：

- **作業系統排程不確定性**：預設的完全公平排程(CFS)策略可能導致低延遲關鍵行程被背景任務（如日誌、監控）或核心執行緒（如 ksoftirqd, kworker）搶占，引入不可預測的微秒級甚至毫秒級停頓。

- **硬體資源爭用**：超執行緒(Hyper-Threading, HT)使得邏輯核心共享實體執行單元，兄弟執行緒的計算密集型任務（如使用AVX指令）會阻塞交易執行緒；多個核心爭用共享的末級快取(L3 Cache)，導致快取行失效和更高的記憶體存取延遲。

- **NUMA架構影響**：在非統一記憶體存取(NUMA)架構的多路伺服器上，跨節點(Remote Node)存取記憶體的延遲可能比本地節點(Local Node)高出50%甚至更多。

- **傳統I/O瓶頸**：核心網路協定堆疊處理網路封包需要多次上下文切換、資料拷貝和協定解析，單次處理耗時輕鬆超過10μs，成為延遲大戶。

### 最佳化目標

透過本文闡述的作業系統深度調校實踐，目標是將關鍵路徑的延遲波動（Jitter）從預設環境下的±50μs壓縮到±1μs以內，並將平均延遲穩定地控制在20μs以下，為策略執行提供高度確定性的微秒級回應能力。這是實現穩定獲利的基礎設施保障。

## 核心隔離：消除資源競爭

### 1. 實體核獨占（CPU Pinning）

#### 為什麼需要

現代CPU的超執行緒技術(HT)將一個實體核模擬為兩個邏輯核，它們共享核心的執行單元（如ALU、FPU）和L1/L2快取。在高頻交易場景下，這帶來兩個致命問題：

1. 若綁定到同一實體核上的兄弟執行緒（如日誌執行緒、監控執行緒）執行了計算密集型操作，尤其是使用AVX等寬指令集時，會完全占用共享的浮點單元，導致交易執行緒被阻塞
2. 兄弟執行緒對L1/L2快取的存取會污染或驅逐交易執行緒的熱點資料，增加快取未命中(Cache Miss)率

**實測資料表明**，在高負載、低延遲敏感場景下，停用超執行緒可使關鍵交易執行緒的執行延遲降低高達22%（基於Intel Xeon Scalable處理器測試），更重要的是大幅降低了延遲波動（Jitter）。

#### 權衡取捨

停用超執行緒會降低系統的整體吞吐量(Throughput)。因此，合理的策略是**隔離關鍵路徑**：將交易策略引擎、網路處理執行緒等低延遲敏感任務**獨占綁定到實體核心**（使用邏輯核ID的偶數或奇數部分），而將日誌記錄、監控上報、資料持久化等非即時性任務部署在啟用超執行緒的核心上。

#### 設定方法

```bash
# 檢視實體核拓撲（實體核ID連續）
lscpu -p | grep -v '#' | awk -F, '{print $1,$3}' | sort -t, -k2n

# 綁定策略行程到實體核8-15（跳過超執行緒核）
taskset -c 8-15 ./strategy_engine
```

#### C++實作（sched_setaffinity）

```cpp
cpu_set_t cpuset;
CPU_ZERO(&cpuset);
for(int i=8; i<=15; i++) CPU_SET(i, &cpuset);
sched_setaffinity(0, sizeof(cpuset), &cpuset);
```

### 2. 中斷重定向

#### 為什麼需要

網路介面卡(NIC)產生的中斷(IRQ)預設通常由CPU 0處理。如果在關鍵交易執行緒執行的CPU核心上處理網路中斷，會產生嚴重的負面影響：

1. **中斷處理程式搶占使用者態交易執行緒**，強制進行上下文切換
2. **中斷處理程式存取記憶體會污染該核心的L1d快取**，導致交易執行緒的熱點資料被驅逐

單次中斷事件就可能增加~300ns的額外記憶體存取延遲。透過將網卡中斷重定向到專用的非隔離核心，可以顯著降低關鍵交易核心的延遲波動。

#### 設定方法

```bash
# 將eth0中斷綁定到CPU16-23
IRQ=$(awk -F: '/eth0/{print $1}' /proc/interrupts)
echo "fff000" > /proc/irq/$IRQ/smp_affinity  # 遮罩對應CPU16-23
```

### 3. 核心排程隔離

#### 為什麼需要

即使進行了CPU綁定，預設情況下，核心執行緒（如負責軟中斷處理的ksoftirqd，處理工作佇列的kworker）仍然可能被排程到綁定的核心上執行，搶占使用者態交易執行緒。

- `isolcpus`參數將指定的CPU核心從核心通用排程器中隔離出來，**阻止大部分核心執行緒和普通使用者行程在其上執行**
- `nohz_full`參數可以在這些核心上啟用自適應無時鐘模式，**顯著減少或完全消除時鐘中斷**
- `rcu_nocbs`參數將**RCU回呼任務卸載到其他非隔離核心執行**

#### 設定方法

```bash
# 修改GRUB設定
grub_cmdline="isolcpus=8-15 nohz_full=8-15 rcu_nocbs=8-15"

# 生效設定
grub2-mkconfig -o /boot/grub2/grub.cfg
```

## NUMA記憶體最佳化：攻克跨節點延遲

### 1. 記憶體本地化綁定

#### 為什麼需要

在多路伺服器(NUMA架構)中，記憶體控制器分布在不同的實體CPU插槽(Node)上。CPU存取其本地節點的記憶體(**Local Access**)速度最快，而存取其他節點(**Remote Access**)的記憶體需要透過CPU間的互連，延遲顯著增加（通常高出50%-100%甚至更多）。

透過將策略行程及其使用的記憶體嚴格綁定在同一個NUMA節點上，可以消除跨節點存取，將記憶體延遲降低多達50%，並大幅降低延遲波動。

#### 設定方法

```bash
# 啟動時綁定記憶體節點
numactl --cpunodebind=0 --membind=0 ./strategy
```

#### 程式碼控制

```cpp
#include <numa.h>
numa_set_localalloc();  // 優先本地分配
void* mem = numa_alloc_local(1024*1024); // 1MB本地記憶體
```

## 缺頁中斷最佳化：鎖定、預取與大頁

記憶體存取延遲的另一個主要敵人是**缺頁中斷(Page Fault)**和**TLB未命中(TLB Miss)**。本部分最佳化旨在**將記憶體存取相關的開銷移至初始化階段**，並**鎖定關鍵資源**。

### 1. 記憶體鎖定（強制實體記憶體駐留）

#### 為什麼需要

預設情況下，作業系統會根據記憶體壓力將行程不常用的記憶體頁換出到磁碟。執行時觸發的換入會造成毫秒級的不可預測停頓。

`mlock`系統呼叫將指定的虛擬記憶體範圍**鎖定在實體記憶體(RAM)中**，確保其不會被換出。此外，它還具有兩個關鍵優勢：

1. **防止頁快取回寫干擾**：鎖定的匿名頁不會被標記為髒頁
2. **確定性提升**：結合NUMA綁定，確保所需記憶體始終駐留在本地節點的實體記憶體中

#### 設定方法

```bash
# 增大記憶體鎖定配額 (預設64KB)
sysctl vm.lock_limit_kb=1048576  # 1GB
echo "vm.lock_limit_kb=1048576" >> /etc/sysctl.conf

# 停用交換空間
swapoff -a
```

#### 程式碼實作

```cpp
#include <sys/mman.h>
#include <iostream>
#include <cstring>

// 分配並鎖定記憶體
void* allocateLockedMemory(size_t size) {
    // 分配對齊的記憶體（POSIX標準）
    void* mem;
    if (posix_memalign(&mem, sysconf(_SC_PAGESIZE), size) != 0) {
        return nullptr;
    }

    // 嘗試實體記憶體鎖定 
    if (mlock(mem, size) == -1) {
        free(mem);  // 鎖定失敗則釋放記憶體
        return nullptr;
    }

    return mem;
}

int main() {
    const size_t memSize = 1024 * 1024; // 1MB
    void* lockedMem = allocateLockedMemory(memSize);
    
    if (!lockedMem) {
        std::cerr << "Failed to allocate locked memory! ";
        std::cerr << "(Tip: Requires root or CAP_IPC_LOCK)\n";
        return 1;
    }

    // 使用記憶體...
    int* data = static_cast<int*>(lockedMem);
    data[0] = 0x12345678;

    // 保持常駐（程式執行時記憶體不會換出）
    while(true) {
        // 實際應用中應有退出邏輯
        sleep(1);
    }
    
    // 程式退出時自動解鎖
    munlock(lockedMem, memSize);
    free(lockedMem);
    return 0;
}
```

### 2. 記憶體預取（Prefetching）

#### 為什麼需要

記憶體鎖定保證了實體記憶體駐留，但在行程啟動或記憶體剛分配時，虛擬位址到實體位址的映射可能尚未建立。預取的核心思想是：在策略初始化階段、交易開始前，主動地、一次性地存取所有未來需要使用的鎖定記憶體區域，人為觸發並處理完所有潛在的缺頁中斷。

#### 程式碼實作

```cpp
#include <sys/mman.h>
#include <iostream>
#include <cstring>

int main() {
    const size_t memSize = 1024 * 1024; // 1MB
    void* lockedMem = allocateLockedMemory(memSize);
    
    if (!lockedMem) {
        std::cerr << "Failed to allocate locked memory!\n";
        return 1;
    }

    // 手動觸發缺頁中斷
    memset(lockedMem, 0, memSize);

    // 保持常駐
    while(true) {
        // 預取資料到L1
        __builtin_prefetch(lockedMem, 0, 3);
        sleep(1);
    }

    munlock(lockedMem, memSize);
    free(lockedMem);
    return 0;
}
```

### 3. 大頁記憶體（HugePage）

#### 為什麼需要

預設記憶體頁大小為4KB。當行程需要存取大量記憶體時，頻繁的TLB未命中會觸發頁表遍歷，增加存取延遲。

**大頁(HugePage)**（通常為2MB或1GB）透過增大單個頁的大小，使得一個TLB條目可以覆蓋更大的實體位址範圍，從而**顯著減少TLB Misses的機率**。

#### 使用建議

- **與記憶體鎖定協同**：避免大頁被換出
- **停用透明大頁(THP)**：THP的合併操作可能在執行時發生，引入不可預測的效能抖動

#### 設定方法

```bash
# 檢視目前大頁狀態
grep Huge /proc/meminfo

# 預留 1024 個 2MB 大頁（永久生效）
sudo vim /etc/sysctl.conf
vm.nr_hugepages = 1024

# 關閉透明大頁（THP）
# 臨時關閉
sudo sh -c 'echo never > /sys/kernel/mm/transparent_hugepage/enabled'

# 永久關閉（編輯 GRUB 設定）
sudo vim /etc/default/grub
transparent_hugepage=never

# 更新並重新啟動
sudo update-grub
sudo reboot
```

#### 程式碼實作

```cpp
#include <sys/mman.h>
#include <iostream>
#include <cstring>

void* allocateHuge(size_t size) {
    int flags = MAP_PRIVATE | MAP_ANON | MAP_HUGETLB;
    int prot = PROT_READ | PROT_WRITE;
    void* ptr = mmap(nullptr, size, prot, flags, -1, 0);
    return ptr == MAP_FAILED ? nullptr : ptr;
}

int main() {
    const size_t memSize = 2 * 1024 * 1024; // 2MB
    void* lockMem = allocateHuge(memSize);
 
    // 鎖定記憶體
    if (-1 == mlock(lockMem, memSize)) {
        munmap(lockMem, memSize);
        return 1;
    }

    // 手動觸發缺頁中斷
    memset(lockMem, 0, memSize);

    // 保持常駐
    while(true) {
        sleep(1);
    }

    munlock(lockMem, memSize);
    munmap(lockMem, memSize);
    return 0;
}
```

### 4. 資料分片設計

#### 為什麼需要

複雜的交易策略可能同時處理多種證券或大量歷史資料。資料分片的核心思想是根據資料的存取頻率、重要性以及策略邏輯，將不同類型的資料結構分配到最合適的實體記憶體區域。

#### 設定方法

```bash
# 檢視NUMA節點分布
numactl --hardware

# 為Node0分配1024個2MB大頁
echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages

# 為Node1分配512個1GB大頁（若支援）
echo 512 > /sys/devices/system/node/node1/hugepages/hugepages-1048576kB/nr_hugepages
```

#### 程式碼實作

```cpp
#include <numa.h>
#include <numaif.h>
#include <sys/mman.h>

void* alloc_hugepage_on_node(int node, size_t size) {
    struct bitmask *nm = numa_allocate_nodemask();
    numa_bitmask_setbit(nm, node);  // 指定目標節點
    
    // NUMA感知的大頁分配
    void* ptr = mmap(NULL, size, PROT_READ|PROT_WRITE,
                     MAP_PRIVATE|MAP_ANONYMOUS|MAP_HUGETLB,
                     -1, 0);
    mbind(ptr, size, MPOL_BIND, nm->maskp, nm->size + 1, 0);
    
    numa_free_nodemask(nm);
    return ptr;
}
```

## 快取最佳化：釋放硬體算力

### 1. 快取隔離

#### 為什麼需要

在現代多核CPU中，所有核心共享末級快取（通常是L3 Cache）。當多個核心同時頻繁存取L3快取時，會發生**快取爭用(Cache Contention)**。

Intel的快取分配技術(CAT)允許將L3快取劃分為多個容量可設定的區域，並將特定的CPU核心或行程綁定到某個區域。這樣可以為關鍵的低延遲交易執行緒劃分出一塊受保護的「專屬快取空間」。

#### 設定方法

```bash
# 1. 安裝pqos工具
sudo apt update
sudo apt install intel-cmt-cat  # 安裝 Intel RDT 工具包

# 2. 驗證硬體支援
grep -E 'cat_l3' /proc/cpuinfo
pqos -d

# 3. 設定快取隔離策略
pqos -s  # 檢視預設設定

# 建立 COS (Class of Service) 定義
sudo pqos -e 'llc:1=0xff0'    # COS1：分配中間8位快取
sudo pqos -e 'llc:2=0x00f'    # COS2：分配最低4位快取

# 4. 綁定COS
sudo pqos -a 'llc:1=1234'     # 將PID 1234綁定到COS1
sudo pqos -a 'llc:2=5678'     # 將PID 5678綁定到COS2

# 5. 即時監控快取使用
pqos -m all:1                 # 整體監控(每秒重新整理)
pqos -m llc:1 -t 10           # 監控COS1的LLC占用
```

### 2. 資料結構對齊

#### 為什麼需要

CPU快取是以快取行(Cache Line, 通常64位元組)為單位管理的。**偽共享(False Sharing)**發生在多個執行緒頻繁讀寫位於同一個快取行內的不同變數。

透過將高頻並行存取的關鍵資料結構按快取行大小(64位元組)進行記憶體對齊，確保它們獨占一個或多個完整的快取行，可以徹底消除偽共享帶來的效能損耗。

#### 程式碼實作

```cpp
struct __attribute__((aligned(64))) MarketData {
    std::atomic<uint64_t> timestamp;
    char payload[32];
};

// 驗證對齊
static_assert(offsetof(MarketData, timestamp) % 64 == 0, "未對齊");
```

### 3. SIMD指令加速

#### 為什麼需要

高頻交易策略常常需要對大量資料進行相同的算術或邏輯運算。單指令多資料流(SIMD)指令允許一條指令同時處理多個資料元素。

#### 程式碼範例

```cpp
__m512 parse_bid_ask(const float* data) {
    __m512 bid = _mm512_load_ps(data);
    __m512 ask = _mm512_load_ps(data + 16);
    return _mm512_sub_ps(ask, bid);  // 計算價差
}
```

## 調校優先級策略

最佳化措施的實施應遵循優先級原則，優先解決影響最大、最基礎的非確定性問題：

| 優先級 | 技術方向 | 核心價值 | 關鍵手段範例 |
|--------|----------|----------|--------------|
| 1 | **核心隔離** | 消除作業系統排程與硬體中斷帶來的不確定性，為奈秒級精度奠定基礎 | isolcpus隔離核、中斷重定向、CPU Pinning |
| 2 | **NUMA記憶體最佳化** | 解決跨節點記憶體存取延遲翻倍問題，將記憶體存取約束在本地NUMA節點 | numactl綁核綁存、大頁記憶體(HugePage)、記憶體鎖定(mlock) |
| 3 | **快取控制** | 避免共享快取爭用導致的微秒級抖動，提升計算確定性 | CAT快取隔離、資料結構對齊消除偽共享、SIMD指令向量化 |

## 關鍵結論

在追求奈秒級競爭優勢的高頻交易領域，作業系統的預設行為往往是延遲不確定性的主要來源。透過本文詳述的系統性調校實踐：

- 從核心隔離消除排程干擾
- 到NUMA綁定最佳化記憶體位置
- 再到記憶體鎖定/預取/大頁消除缺頁停頓
- 最後透過快取隔離和資料結構最佳化減少核心間干擾

我們能夠將關鍵交易路徑的延遲**穩定地壓縮到20微秒(μs)以內**，並將其波動範圍(**Jitter**)控制在**±1微秒(μs)**的狹窄區間。這種**高度確定的微秒級回應能力**是策略穩定獲利的基礎設施保障。

## 下一征程：核心旁路(Kernel Bypass)

儘管系統層最佳化已將延遲壓縮至微秒級，**網路I/O處理仍然是最後的、也是最堅固的效能壁壘**。傳統核心網路協定堆疊在處理高速網路封包時存在固有瓶頸：

- **協定堆疊處理耗時 >10μs**：封包需要穿越複雜的協定層
- **多次資料拷貝**：資料從網卡DMA區域拷貝到核心Socket Buffer，再從核心拷貝到使用者空間
- **TCP重傳引入不確定性**：核心的擁塞控制和重傳機制可能引入非預期的延遲

為了將端到端延遲進一步推向亞微秒級甚至奈秒級，必須繞過核心協定堆疊。下篇《核心旁路技術實踐》將深入探討如何利用**DPDK(Data Plane Development Kit)**、**Solarflare**等技術，將使用者態應用直接與網卡硬體對接，實現零拷貝(Zero-Copy)、輪詢模式驅動(Polling Mode Driver)和使用者態協定堆疊，將網路處理延遲降低一個數量級（通常降至1μs以下），突破核心瓶頸，實現真正的奈秒級交易系統。

---

*原文連結：https://zhuanlan.zhihu.com/p/1936428978639467459*