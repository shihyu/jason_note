# TSE Receiver 優化詳解與程式碼對照分析

## 1. 執行摘要

本文件詳細說明將 TSE 報價接收程式從參考實作 (`tse_receiver.c`) 升級為低延遲基準測試版本 (`tse_receiver_benchmark.c`) 的關鍵技術細節。透過程式碼層級的優化與系統層級的調優，我們成功將 **P99 延遲從 14.32 ms 降低至 5.33 ms**，改善幅度達 **62.8%**。

---

## 2. 程式碼層級優化 (Code-Level Optimizations)

### 2.1 引入 Non-blocking I/O (Busy Polling)

傳統的 Blocking I/O 會導致進程進入睡眠狀態，等待數據到達時再由 kernel 喚醒，這個過程包含上下文切換 (Context Switch) 開銷。我們改用 Non-blocking 模式配合 Busy Polling 來消除此開銷。

**優化前 (`tse_receiver.c`)**:
```c
// 傳統阻塞式接收
// 進程會在這裡掛起 (Sleep)，直到有數據到達
int nbytes = recvfrom(sockfd, buf, BUF_SIZE, 0, (struct sockaddr*)&src_addr, &addrlen);
```

**優化後 (`tse_receiver_benchmark.c`)**:
```c
// 1. 設定 Socket 為 Non-blocking
if (g_config.use_nonblocking) {
    int flags = fcntl(sockfd, F_GETFL, 0);
    fcntl(sockfd, F_SETFL, flags | O_NONBLOCK);
}

// ... 在接收迴圈中 ...

// 2. 使用 MSG_DONTWAIT (雙重保險)
int nbytes = recvfrom(sockfd, buf, BUF_SIZE,
                      g_config.use_nonblocking ? MSG_DONTWAIT : 0,
                      (struct sockaddr*)&src_addr, &addrlen);

if (nbytes < 0) {
    if (errno == EAGAIN || errno == EWOULDBLOCK) {
        // 3. Busy Polling: 沒數據不睡覺，立刻重試
        // 雖然吃滿 100% CPU，但反應最快
        continue;
    }
    // ... 錯誤處理 ...
}
```

### 2.2 CPU 親和性綁定 (CPU Affinity)

為了避免作業系統將進程在不同 CPU 核心間遷移 (Migration)，導致 L1/L2 Cache 失效，我們強制將程式綁定在特定核心。

**優化前**:
*   無此代碼。作業系統排程器自由決定程式跑在哪個核。

**優化後**:
```c
// 設定 CPU Affinity
int SetCPUAffinity(int cpu_id)
{
    cpu_set_t cpuset;
    CPU_ZERO(&cpuset);
    CPU_SET(cpu_id, &cpuset);

    if (sched_setaffinity(0, sizeof(cpuset), &cpuset) == -1) {
        perror("設置 CPU affinity 失敗");
        return -1;
    }
    return 0;
}

// 在 main() 中呼叫
if (g_config.cpu_affinity >= 0) {
    SetCPUAffinity(g_config.cpu_affinity);
}
```

### 2.3 即時排程策略 (Real-time Scheduling)

將進程提升為即時優先級，避免被其他背景程式搶佔 CPU 時間片。

**優化後**:
```c
int SetRealtimeScheduling(void)
{
    struct sched_param param;
    param.sched_priority = 80; // 高優先級

    // 使用 FIFO 策略：除非自己讓出 CPU 或被更高優先級搶佔，否則一直執行
    if (sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
        perror("設置即時排程失敗");
        return -1;
    }
    return 0;
}
```

### 2.4 統計與延遲測量 (Latency Measurement)

為了精確量化優化效果，我們將原本的 `PrintQuote` (單純印出) 替換為高效能的記憶體內統計。

**優化前**:
```c
// 每次接收都 printf，I/O 操作極慢，嚴重拖累接收效能
PrintQuote(&quote);
```

**優化後**:
```c
// 1. 僅寫入記憶體陣列，極快
AddLatencySample(q->CalibratedLatencyMicros);

// 2. 僅在收集完畢或每隔 N 筆才做一次 I/O 輸出
if (g_stats.count % STAT_INTERVAL == 0) {
    PrintStatistics();
}
```

---

## 3. 系統層級優化 (System-Level Optimizations)

程式碼寫得再好，如果作業系統配置不當，效果也會大打折扣。以下是配合程式碼的關鍵系統設定。

### 3.1 中斷親和性 (IRQ Affinity)

這是本次優化**最關鍵**的一步。原本網卡中斷 (IRQ) 分散在 CPU3，而程式跑在 CPU2，導致跨核通訊 (Cache Coherency) 延遲。

*   **操作**: 將網卡的所有 IRQ 隊列綁定到 **CPU1**。
*   **指令**:
    ```bash
    echo 1 > /proc/irq/62/smp_affinity_list
    # ... 對所有相關 IRQ 重複此操作 ...
    ```
*   **配合程式**: 使用 `-c 1` 參數將程式也綁定到 **CPU1**。
    ```bash
    taskset -c 1 ./tse_receiver_benchmark ...
    ```
*   **結果**: 數據從網卡 -> Driver -> 用戶空間程式，全程在同一顆 CPU 的 L1/L2 Cache 中流動，零拷貝、零跨核。

### 3.2 禁用中斷合併 (Disable Interrupt Coalescing)

網卡預設會累積幾個封包或等待幾微秒才發一次中斷，以節省 CPU。這對吞吐量有利，但對延遲是災難。

*   **操作**: `ethtool -C ens224 rx-usecs 0`
*   **效果**: 每個封包到達，網卡立刻發中斷，程式立刻收到。

### 3.3 擴大 Socket 緩衝區

防止微秒級的流量突波導致丟包。

*   **系統層**: `ethtool -G ens224 rx 4096` (網卡硬體環)
*   **程式層**:
    ```c
    int rcvbuf = 8 * 1024 * 1024;  // 8 MB
    setsockopt(sockfd, SOL_SOCKET, SO_RCVBUF, &rcvbuf, sizeof(rcvbuf));
    ```

---

## 4. 優化前後效能對比表

| 指標 | 優化前 (Baseline) | 優化後 (Optimized) | 改善說明 |
| :--- | :--- | :--- | :--- |
| **P99 延遲** | 14.32 ms | **5.33 ms** | **減少 63%**，主要歸功於 IRQ/CPU 綁定消除跨核開銷。 |
| **P999 延遲** | 15.90 ms | **6.01 ms** | **尾端延遲大幅收斂**，系統抖動極小。 |
| **< 1μs 封包比例** | 31.0% | **83.8%** | 絕大多數封包都能即時處理，不再堆積。 |
| **CPU 使用率** | 低 (Sleeping) | **100% (如果是 Non-blocking)** | 用 CPU 資源換取極致低延遲 (Busy Polling 代價)。 |

## 5. 結論

透過將程式邏輯 (Non-blocking, Affinity) 與系統特性 (IRQ, Ethtool) 緊密結合，我們成功打造了一個 kernel-based 的低延遲接收方案。目前的瓶頸已轉移至 Linux Kernel 本身的網路堆疊 (Network Stack)，若需進一步突破 (如 < 1ms)，則需考慮 DPDK 等 Kernel Bypass 技術。
