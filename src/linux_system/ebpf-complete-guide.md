# eBPF 完整指南

## 目錄
- [什麼是 eBPF？](#什麼是-ebpf)
- [核心概念](#核心概念)
- [架構組件](#架構組件)
- [開發工具鏈](#開發工具鏈)
- [安全機制](#安全機制)
- [為什麼使用 eBPF？](#為什麼使用-ebpf)

## 什麼是 eBPF？

**eBPF (extended Berkeley Packet Filter)** 是一項革命性的技術，起源於 Linux 核心，它可以在特權上下文中（如作業系統核心）運行沙盒程序。

### 核心特點
- 🔒 **安全執行**：在核心中安全運行沙盒程序
- ⚡ **高效能**：通過 JIT 編譯達到原生程式碼效能  
- 🔧 **可擴展**：無需修改核心原始碼或載入核心模組
- 🎯 **事件驅動**：基於系統事件觸發執行

### eBPF vs BPF
- **BPF**：Berkeley Packet Filter - 原始的封包過濾器
- **eBPF**：extended BPF - 功能已遠超封包過濾
- **cBPF**：classic BPF - 用於區分原始 BPF

> 🐝 **eBee**：eBPF 的官方吉祥物，由 Vadim Shchekoldin 設計

## 核心概念

### 1. 系統架構圖

```mermaid
graph TB
    subgraph "使用者空間"
        APP[應用程式<br/>Python/Go/C++]
        TOOL[開發工具<br/>bcc/bpftrace]
        LIB[eBPF 函式庫]
    end
    
    subgraph "eBPF 子系統"
        LOAD[載入器]
        VERIFY[驗證器<br/>Verifier]
        JIT[JIT 編譯器]
        MAPS[eBPF Maps<br/>資料儲存]
    end
    
    subgraph "Linux 核心"
        HOOK[鉤子點 Hooks]
        PROG[eBPF 程式<br/>執行環境]
        HELPER[Helper 函數]
        SUBSYS[核心子系統]
    end
    
    subgraph "硬體層"
        HW[CPU/記憶體/網卡]
    end
    
    APP --> TOOL
    TOOL --> LIB
    LIB -->|bpf()系統呼叫| LOAD
    LOAD --> VERIFY
    VERIFY -->|安全檢查通過| JIT
    JIT -->|機器碼| PROG
    PROG <--> MAPS
    PROG --> HELPER
    PROG --> HOOK
    HOOK --> SUBSYS
    SUBSYS --> HW
    
    style VERIFY fill:#ff9999
    style JIT fill:#99ff99
    style MAPS fill:#9999ff
```

### 2. 鉤子點 (Hooks)

eBPF 程序可以附加到多種鉤子點：

| 鉤子類型 | 用途 | 觸發時機 |
|---------|------|----------|
| **系統呼叫** | 監控系統呼叫 | 進程呼叫系統 API 時 |
| **Kprobes** | 核心函數探針 | 核心函數執行時 |
| **Uprobes** | 使用者程式探針 | 應用程式函數執行時 |
| **Tracepoints** | 追蹤點 | 預定義的核心事件 |
| **XDP** | 快速封包處理 | 網卡收到封包時 |
| **TC** | 流量控制 | 網路封包進出時 |
| **Perf Events** | 效能事件 | CPU/記憶體事件發生時 |

### 3. eBPF 程式執行流程

```mermaid
graph LR
    subgraph "開發階段"
        CODE[C/Rust 程式碼]
        COMPILE[LLVM/Clang<br/>編譯]
        BYTECODE[eBPF Bytecode]
    end
    
    subgraph "載入階段"
        SYSCALL[bpf() 系統呼叫]
        VERIFIER[驗證器檢查]
        JIT_COMP[JIT 編譯]
    end
    
    subgraph "執行階段"
        ATTACH[附加到鉤子]
        RUN[事件觸發執行]
        MAPS_RW[讀寫 Maps]
        HELPERS[呼叫 Helper]
    end
    
    CODE --> COMPILE
    COMPILE --> BYTECODE
    BYTECODE --> SYSCALL
    SYSCALL --> VERIFIER
    VERIFIER -->|通過| JIT_COMP
    VERIFIER -->|失敗| REJECT[拒絕載入]
    JIT_COMP --> ATTACH
    ATTACH --> RUN
    RUN --> MAPS_RW
    RUN --> HELPERS
    
    style VERIFIER fill:#ffcccc
    style JIT_COMP fill:#ccffcc
```

## 架構組件

### 1. eBPF Maps

Maps 是核心與使用者空間的資料橋樑：

```mermaid
graph TB
    subgraph "使用者空間程式"
        USER[Python/Go/C++ 應用]
    end
    
    subgraph "eBPF Maps 類型"
        HASH[Hash Map<br/>鍵值對儲存]
        ARRAY[Array<br/>固定大小陣列]
        PERF[Perf Event Array<br/>事件傳遞]
        STACK[Stack Trace<br/>堆疊追蹤]
        LRU[LRU Hash<br/>快取儲存]
        PERCPU[Per-CPU Array<br/>CPU 獨立儲存]
    end
    
    subgraph "核心 eBPF 程式"
        KERNEL[eBPF 程式邏輯]
    end
    
    USER <-->|讀寫| HASH
    USER <-->|讀寫| ARRAY
    USER <--|讀取事件| PERF
    
    KERNEL -->|更新| HASH
    KERNEL -->|寫入| ARRAY
    KERNEL -->|提交事件| PERF
    KERNEL -->|記錄| STACK
    KERNEL <--> LRU
    KERNEL <--> PERCPU
    
    style HASH fill:#ffffcc
    style PERF fill:#ccffff
```

### 2. 驗證器 (Verifier)

驗證器確保 eBPF 程式的安全性：

```mermaid
flowchart TD
    START[eBPF Bytecode]
    
    CHECK1{檢查指令數量<br/>< 1M ?}
    CHECK2{模擬所有路徑}
    CHECK3{記憶體訪問<br/>安全？}
    CHECK4{程式會結束？<br/>無無限迴圈}
    CHECK5{Helper 使用<br/>正確？}
    
    PASS[✅ 載入到核心]
    FAIL[❌ 拒絕載入]
    
    START --> CHECK1
    CHECK1 -->|是| CHECK2
    CHECK1 -->|否| FAIL
    CHECK2 -->|通過| CHECK3
    CHECK2 -->|失敗| FAIL
    CHECK3 -->|安全| CHECK4
    CHECK3 -->|不安全| FAIL
    CHECK4 -->|是| CHECK5
    CHECK4 -->|否| FAIL
    CHECK5 -->|正確| PASS
    CHECK5 -->|錯誤| FAIL
    
    style PASS fill:#90EE90
    style FAIL fill:#FFB6C1
```

### 3. JIT 編譯器

將 eBPF bytecode 轉換為機器碼：

```mermaid
graph LR
    subgraph "編譯流程"
        BC[eBPF Bytecode<br/>虛擬指令]
        JIT[JIT 編譯器]
        MC[機器碼<br/>x86/ARM]
    end
    
    subgraph "效能對比"
        INTERP[解釋執行<br/>速度: 1x]
        NATIVE[原生執行<br/>速度: 10x+]
    end
    
    BC --> JIT
    JIT --> MC
    BC -.->|沒有 JIT| INTERP
    MC -->|有 JIT| NATIVE
    
    style NATIVE fill:#90EE90
    style INTERP fill:#FFE4B5
```

### 4. Helper 函數

eBPF 程式通過 Helper 函數與核心互動：

| Helper 類別 | 功能範例 |
|------------|----------|
| **Map 操作** | `bpf_map_lookup_elem()`, `bpf_map_update_elem()` |
| **時間相關** | `bpf_ktime_get_ns()`, `bpf_get_current_time()` |
| **網路操作** | `bpf_redirect()`, `bpf_clone_redirect()` |
| **追蹤相關** | `bpf_probe_read()`, `bpf_get_stack()` |
| **隨機數** | `bpf_get_prandom_u32()` |
| **程序資訊** | `bpf_get_current_pid_tgid()`, `bpf_get_current_comm()` |

## 開發工具鏈

### 工具對比

```mermaid
graph TB
    subgraph "高階工具"
        BPFTRACE[bpftrace<br/>一行指令追蹤]
        BCC[BCC<br/>Python + eBPF]
    end
    
    subgraph "中階框架"
        GO[eBPF Go<br/>Go 語言函式庫]
        RUST[Aya<br/>Rust 框架]
    end
    
    subgraph "底層函式庫"
        LIBBPF[libbpf<br/>C/C++ 函式庫]
    end
    
    subgraph "使用場景"
        TRACE[快速診斷]
        PROTO[原型開發]
        PROD[生產環境]
    end
    
    BPFTRACE --> TRACE
    BCC --> PROTO
    GO --> PROD
    RUST --> PROD
    LIBBPF --> PROD
    
    style BPFTRACE fill:#FFE4B5
    style BCC fill:#E6E6FA
    style LIBBPF fill:#90EE90
```

### 各工具特點

| 工具 | 語言 | 學習曲線 | 部署複雜度 | 適用場景 |
|------|------|----------|------------|----------|
| **bpftrace** | DSL | 簡單 | 低 | 臨時診斷、一行指令 |
| **BCC** | Python/C | 中等 | 中 | 系統工具、原型開發 |
| **libbpf** | C/C++ | 陡峭 | 低 | 生產環境、高效能 |
| **eBPF Go** | Go | 中等 | 低 | Go 應用整合 |
| **Aya** | Rust | 中等 | 低 | Rust 應用、安全性 |

## 安全機制

### 多層安全保障

```mermaid
graph TD
    subgraph "第一層：權限控制"
        PRIV[需要 root 或 CAP_BPF 權限]
    end
    
    subgraph "第二層：驗證器"
        VER[程式安全性驗證<br/>- 無無限迴圈<br/>- 記憶體訪問安全<br/>- 有界限執行]
    end
    
    subgraph "第三層：加固"
        HARD[執行時保護<br/>- 程式唯讀<br/>- Spectre 緩解<br/>- 常數盲化]
    end
    
    subgraph "第四層：隔離"
        ISO[執行環境隔離<br/>- 不能直接訪問記憶體<br/>- 必須使用 Helper<br/>- 受限的上下文]
    end
    
    PRIV --> VER
    VER --> HARD
    HARD --> ISO
    
    style PRIV fill:#FFB6C1
    style VER fill:#FFE4B5
    style HARD fill:#E6E6FA
    style ISO fill:#90EE90
```

## 為什麼使用 eBPF？

### 傳統方式 vs eBPF

```mermaid
graph LR
    subgraph "傳統方式"
        T1[修改核心原始碼]
        T2[等待數年發布]
        T3[編寫核心模組]
        T4[可能造成崩潰]
    end
    
    subgraph "eBPF 方式"
        E1[編寫 eBPF 程式]
        E2[即時載入執行]
        E3[安全沙盒環境]
        E4[動態可程式化]
    end
    
    T1 --> T2
    T3 --> T4
    
    E1 --> E2
    E2 --> E3
    E3 --> E4
    
    style T4 fill:#FFB6C1
    style E4 fill:#90EE90
```

### eBPF 的革命性影響

類似於 JavaScript 對 Web 的影響：

| 層面 | Web (JavaScript) | Linux (eBPF) |
|------|-----------------|--------------|
| **之前** | 靜態 HTML | 固定核心功能 |
| **之後** | 動態 Web 應用 | 可程式化核心 |
| **安全** | 瀏覽器沙盒 | 驗證器 + 隔離 |
| **效能** | JIT 編譯 | JIT 編譯 |
| **部署** | 即時更新 | 動態載入 |

### 主要應用領域

1. **🌐 網路**
   - 高效能負載平衡
   - DDoS 防護
   - 網路監控

2. **🔍 可觀測性**
   - 系統追蹤
   - 效能分析
   - 應用監控

3. **🔒 安全**
   - 容器安全
   - 異常檢測
   - 存取控制

4. **⚡ 效能優化**
   - CPU 分析
   - 記憶體追蹤
   - I/O 優化

## 實際應用案例

### 知名專案

| 專案 | 用途 | 使用技術 |
|------|------|----------|
| **Cilium** | Kubernetes 網路 | Go + libbpf |
| **Falco** | 容器安全 | libbpf |
| **Pixie** | K8s 觀測性 | Go + BCC |
| **Katran** | Facebook 負載平衡 | C++ + libbpf |
| **bpftrace** | 系統追蹤 | C++ |

## 總結

eBPF 是 Linux 核心的**超能力**，它實現了：

✅ **安全性**：多層驗證與隔離機制  
✅ **高效能**：JIT 編譯，核心執行  
✅ **靈活性**：動態載入，無需重啟  
✅ **可觀測**：深入系統各層級  
✅ **創新性**：解耦核心與應用發展

> 💡 **核心理念**：在事情發生的地方直接處理，而不是等資料複製出來後再處理

---

📚 **延伸閱讀**：
- [eBPF.io 官方網站](https://ebpf.io)
- [eBPF & XDP 參考指南](https://docs.cilium.io/en/stable/bpf/)
- [Linux 核心 BPF 文件](https://www.kernel.org/doc/html/latest/bpf/)