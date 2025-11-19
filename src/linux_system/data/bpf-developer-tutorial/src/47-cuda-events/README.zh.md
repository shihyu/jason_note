# eBPF 與機器學習可觀測：追蹤 CUDA GPU 操作

你是否曾經想知道CUDA應用程序在運行時底層發生了什麼？GPU操作由於發生在具有獨立內存空間的設備上，因此調試和性能分析變得極為困難。在本教程中，我們將構建一個強大的基於eBPF的追蹤工具，讓你實時查看CUDA API調用。

## CUDA和GPU追蹤簡介

CUDA（Compute Unified Device Architecture，計算統一設備架構）是NVIDIA的並行計算平臺和編程模型，使開發者能夠利用NVIDIA GPU進行通用計算。當你運行CUDA應用程序時，後臺會發生以下步驟：

1. 主機（CPU）在設備（GPU）上分配內存
2. 數據從主機內存傳輸到設備內存
3. GPU內核（函數）被啟動以處理數據
4. 結果從設備傳回主機
5. 設備內存被釋放

每個操作都涉及CUDA API調用，如`cudaMalloc`、`cudaMemcpy`和`cudaLaunchKernel`。追蹤這些調用可以提供寶貴的調試和性能優化信息，但這並不簡單。GPU操作是異步的，傳統調試工具通常無法訪問GPU內部。

這時eBPF就派上用場了！通過使用uprobes，我們可以在用戶空間CUDA運行庫（`libcudart.so`）中攔截CUDA API調用，在它們到達GPU之前。這使我們能夠了解：

- 內存分配大小和模式
- 數據傳輸方向和大小
- 內核啟動參數
- 錯誤代碼和失敗原因
- 操作的時間信息

本教程主要關注CPU側的CUDA API調用，對於細粒度的GPU操作追蹤，你可以參考[eGPU](https://dl.acm.org/doi/10.1145/3723851.3726984)論文和[bpftime](https://github.com/eunomia-bpf/bpftime)項目。

## eBPF技術背景與GPU追蹤的挑戰

eBPF（Extended Berkeley Packet Filter）最初是為網絡數據包過濾而設計的，但現在已經發展成為一個強大的內核編程框架，使開發人員能夠在內核空間運行用戶定義的程序，而無需修改內核源代碼或加載內核模塊。eBPF的安全性通過靜態分析和運行時驗證器來保證，這使得它能夠在生產環境中安全地運行。

傳統的系統追蹤方法往往存在顯著的性能開銷和功能限制。例如，使用strace等工具追蹤系統調用會導致每個被追蹤的系統調用產生數倍的性能損失，因為它需要在內核空間和用戶空間之間頻繁切換。相比之下，eBPF程序直接在內核空間執行，可以就地處理事件，只在必要時才將彙總或過濾後的數據傳遞給用戶空間，從而大大減少了上下文切換的開銷。

GPU追蹤面臨著獨特的挑戰。現代GPU是高度並行的處理器，包含數千個小型計算核心，這些核心可以同時執行數萬個線程。GPU具有自己的內存層次結構，包括全局內存、共享內存、常數內存和紋理內存，這些內存的訪問模式對性能有著巨大影響。更復雜的是，GPU操作通常是異步的，這意味著當CPU啟動一個GPU操作後，它可以繼續執行其他任務，而無需等待GPU操作完成。另外，CUDA編程模型的異步特性使得調試變得特別困難。當一個內核函數在GPU上執行時，CPU無法直接觀察到GPU的內部狀態。錯誤可能在GPU上發生，但直到後續的同步操作（如cudaDeviceSynchronize或cudaStreamSynchronize）時才被檢測到，這使得錯誤源的定位變得困難。此外，GPU內存錯誤（如數組越界訪問）可能導致靜默的數據損壞，而不是立即的程序崩潰，這進一步增加了調試的複雜性。

## 我們追蹤的關鍵CUDA函數

我們的追蹤工具監控幾個關鍵CUDA函數，這些函數代表GPU計算中的主要操作。瞭解這些函數有助於解釋追蹤結果並診斷CUDA應用程序中的問題：

### 內存管理

- **`cudaMalloc`**：在GPU設備上分配內存。通過追蹤這個函數，我們可以看到請求了多少內存、何時請求以及是否成功。內存分配失敗是CUDA應用程序中常見的問題來源。
  ```c
  cudaError_t cudaMalloc(void** devPtr, size_t size);
  ```

- **`cudaFree`**：釋放先前在GPU上分配的內存。追蹤這個函數有助於識別內存洩漏（分配的內存從未被釋放）和雙重釋放錯誤。
  ```c
  cudaError_t cudaFree(void* devPtr);
  ```

### 數據傳輸

- **`cudaMemcpy`**：在主機（CPU）和設備（GPU）內存之間，或在設備內存的不同位置之間複製數據。方向參數（`kind`）告訴我們數據是流向GPU、來自GPU還是在GPU內部移動。
  ```c
  cudaError_t cudaMemcpy(void* dst, const void* src, size_t count, cudaMemcpyKind kind);
  ```
  
  `kind`參數可以是：
  - `cudaMemcpyHostToDevice` (1)：從CPU複製到GPU
  - `cudaMemcpyDeviceToHost` (2)：從GPU複製到CPU
  - `cudaMemcpyDeviceToDevice` (3)：在GPU內存內複製

### 內核執行

- **`cudaLaunchKernel`**：啟動GPU內核（函數）在設備上運行。這是真正的並行計算發生的地方。追蹤這個函數顯示內核何時啟動以及是否成功。
  ```c
  cudaError_t cudaLaunchKernel(const void* func, dim3 gridDim, dim3 blockDim, 
                              void** args, size_t sharedMem, cudaStream_t stream);
  ```

### 流和同步

CUDA使用流來管理併發和異步操作：

- **`cudaStreamCreate`**：創建一個新的流，用於按順序執行操作，但可能與其他流併發。
  ```c
  cudaError_t cudaStreamCreate(cudaStream_t* pStream);
  ```

- **`cudaStreamSynchronize`**：等待流中的所有操作完成。這是一個關鍵的同步點，可以揭示性能瓶頸。
  ```c
  cudaError_t cudaStreamSynchronize(cudaStream_t stream);
  ```

### 事件

CUDA事件用於計時和同步：

- **`cudaEventCreate`**：創建一個事件對象，用於計時操作。
  ```c
  cudaError_t cudaEventCreate(cudaEvent_t* event);
  ```

- **`cudaEventRecord`**：在流中記錄一個事件，可用於計時或同步。
  ```c
  cudaError_t cudaEventRecord(cudaEvent_t event, cudaStream_t stream);
  ```

- **`cudaEventSynchronize`**：等待事件完成，這是另一個同步點。
  ```c
  cudaError_t cudaEventSynchronize(cudaEvent_t event);
  ```

### 設備管理

- **`cudaGetDevice`**：獲取當前使用的設備。
  ```c
  cudaError_t cudaGetDevice(int* device);
  ```

- **`cudaSetDevice`**：設置用於GPU執行的設備。
  ```c
  cudaError_t cudaSetDevice(int device);
  ```

通過追蹤這些函數，我們可以全面瞭解GPU操作的生命週期，從設備選擇和內存分配到數據傳輸、內核執行和同步。這使我們能夠識別瓶頸、診斷錯誤並瞭解CUDA應用程序的行為。

## 架構概述

我們的CUDA事件追蹤器由三個主要組件組成：

1. **頭文件（`cuda_events.h`）**：定義內核空間和用戶空間之間通信的數據結構
2. **eBPF程序（`cuda_events.bpf.c`）**：使用uprobes實現對CUDA函數的內核側鉤子
3. **用戶空間應用程序（`cuda_events.c`）**：加載eBPF程序，處理事件並向用戶顯示

該工具使用eBPF uprobes附加到CUDA運行庫中的CUDA API函數。當調用CUDA函數時，eBPF程序捕獲參數和結果，並通過環形緩衝區將它們發送到用戶空間。

## 關鍵數據結構

我們追蹤器的核心數據結構是在`cuda_events.h`中定義的`struct event`：

```c
struct event {
    /* Common fields */
    int pid;                  /* Process ID */
    char comm[TASK_COMM_LEN]; /* Process name */
    enum cuda_event_type type;/* Type of CUDA event */
    
    /* Event-specific data (union to save space) */
    union {
        struct { size_t size; } mem;                 /* For malloc/memcpy */
        struct { void *ptr; } free_data;             /* For free */
        struct { size_t size; int kind; } memcpy_data; /* For memcpy */
        struct { void *func; } launch;               /* For kernel launch */
        struct { int device; } device;               /* For device operations */
        struct { void *handle; } handle;             /* For stream/event operations */
    };
    
    bool is_return;           /* True if this is from a return probe */
    int ret_val;              /* Return value (for return probes) */
    char details[MAX_DETAILS_LEN]; /* Additional details as string */
};
```

這個結構設計用於高效捕獲不同類型的CUDA操作信息。`union`是一種巧妙的節省空間技術，因為每個事件一次只需要一種類型的數據。例如，內存分配事件需要存儲大小，而釋放事件需要存儲指針。

`cuda_event_type`枚舉幫助我們對不同的CUDA操作進行分類：

```c
enum cuda_event_type {
    CUDA_EVENT_MALLOC = 0,
    CUDA_EVENT_FREE,
    CUDA_EVENT_MEMCPY,
    CUDA_EVENT_LAUNCH_KERNEL,
    CUDA_EVENT_STREAM_CREATE,
    CUDA_EVENT_STREAM_SYNC,
    CUDA_EVENT_GET_DEVICE,
    CUDA_EVENT_SET_DEVICE,
    CUDA_EVENT_EVENT_CREATE,
    CUDA_EVENT_EVENT_RECORD,
    CUDA_EVENT_EVENT_SYNC
};
```

這個枚舉涵蓋了我們要追蹤的主要CUDA操作，從內存管理到內核啟動和同步。

## eBPF程序實現

讓我們深入瞭解鉤入CUDA函數的eBPF程序（`cuda_events.bpf.c`）。完整代碼可在倉庫中找到，以下是關鍵部分：

首先，我們創建一個環形緩衝區與用戶空間通信：

```c
struct {
    __uint(type, BPF_MAP_TYPE_RINGBUF);
    __uint(max_entries, 256 * 1024);
} rb SEC(".maps");
```

環形緩衝區是我們追蹤器的關鍵組件。它充當一個高性能隊列，eBPF程序可以在其中提交事件，用戶空間應用程序可以檢索它們。我們設置了256KB的大小來處理事件突發而不丟失數據。

對於每種CUDA操作，我們實現了一個輔助函數來收集相關數據。讓我們看看`submit_malloc_event`函數為例：

```c
static inline int submit_malloc_event(size_t size, bool is_return, int ret_val) {
    struct event *e = bpf_ringbuf_reserve(&rb, sizeof(*e), 0);
    if (!e) return 0;
    
    /* Fill common fields */
    e->pid = bpf_get_current_pid_tgid() >> 32;
    bpf_get_current_comm(&e->comm, sizeof(e->comm));
    e->type = CUDA_EVENT_MALLOC;
    e->is_return = is_return;
    
    /* Fill event-specific data */
    if (is_return) {
        e->ret_val = ret_val;
    } else {
        e->mem.size = size;
    }
    
    bpf_ringbuf_submit(e, 0);
    return 0;
}
```

這個函數首先在環形緩衝區中為我們的事件保留空間。然後它填充進程ID和名稱等常見字段。對於malloc事件，我們存儲請求的大小（在函數入口）或返回值（在函數退出時）。最後，我們將事件提交到環形緩衝區。

實際的探針使用SEC註釋附加到CUDA函數。對於cudaMalloc，我們有：

```c
SEC("uprobe")
int BPF_KPROBE(cuda_malloc_enter, void **ptr, size_t size) {
    return submit_malloc_event(size, false, 0);
}

SEC("uretprobe")
int BPF_KRETPROBE(cuda_malloc_exit, int ret) {
    return submit_malloc_event(0, true, ret);
}
```

第一個函數在進入`cudaMalloc`時調用，捕獲請求的大小。第二個在`cudaMalloc`返回時調用，捕獲錯誤代碼。這個模式對我們要追蹤的每個CUDA函數都會重複。

一個有趣的例子是`cudaMemcpy`，它在主機和設備之間傳輸數據：

```c
SEC("uprobe")
int BPF_KPROBE(cuda_memcpy_enter, void *dst, const void *src, size_t size, int kind) {
    return submit_memcpy_event(size, kind, false, 0);
}
```

在這裡，我們不僅捕獲了大小，還捕獲了"kind"參數，它指示傳輸的方向（主機到設備、設備到主機或設備到設備）。這為我們提供了關於數據移動模式的寶貴信息。

## 用戶空間應用程序詳情

用戶空間應用程序（`cuda_events.c`）負責加載eBPF程序，處理來自環形緩衝區的事件，並以用戶友好的格式顯示它們。

首先，程序解析命令行參數以配置其行為：

```c
static struct env {
    bool verbose;
    bool print_timestamp;
    char *cuda_library_path;
    bool include_returns;
    int target_pid;
} env = {
    .print_timestamp = true,
    .include_returns = true,
    .cuda_library_path = NULL,
    .target_pid = -1,
};
```

這個結構存儲配置選項，如是否打印時間戳或包含返回探針。默認值提供了一個合理的起點。

程序使用`libbpf`加載並附加eBPF程序到CUDA函數：

```c
int attach_cuda_func(struct cuda_events_bpf *skel, const char *lib_path, 
                    const char *func_name, struct bpf_program *prog_entry,
                    struct bpf_program *prog_exit) {
    /* Attach entry uprobe */
    if (prog_entry) {
        uprobe_opts.func_name = func_name;
        struct bpf_link *link = bpf_program__attach_uprobe_opts(prog_entry, 
                                env.target_pid, lib_path, 0, &uprobe_opts);
        /* Error handling... */
    }
    
    /* Attach exit uprobe */
    if (prog_exit) {
        /* Similar for return probe... */
    }
}
```

這個函數接受一個函數名（如"cudaMalloc"）和相應的入口和退出eBPF程序。然後它將這些程序作為uprobes附加到指定的庫。

最重要的函數之一是`handle_event`，它處理來自環形緩衝區的事件：

```c
static int handle_event(void *ctx, void *data, size_t data_sz) {
    const struct event *e = data;
    struct tm *tm;
    char ts[32];
    char details[MAX_DETAILS_LEN];
    time_t t;

    /* Skip return probes if requested */
    if (e->is_return && !env.include_returns)
        return 0;

    time(&t);
    tm = localtime(&t);
    strftime(ts, sizeof(ts), "%H:%M:%S", tm);

    get_event_details(e, details, sizeof(details));

    if (env.print_timestamp) {
        printf("%-8s ", ts);
    }

    printf("%-16s %-7d %-20s %8s %s\n", 
           e->comm, e->pid, 
           event_type_str(e->type),
           e->is_return ? "[EXIT]" : "[ENTER]",
           details);

    return 0;
}
```

此函數格式化並顯示事件信息，包括時間戳、進程詳情、事件類型以及特定參數或返回值。

`get_event_details`函數將原始事件數據轉換為人類可讀的形式：

```c
static void get_event_details(const struct event *e, char *details, size_t len) {
    switch (e->type) {
    case CUDA_EVENT_MALLOC:
        if (!e->is_return)
            snprintf(details, len, "size=%zu bytes", e->mem.size);
        else
            snprintf(details, len, "returned=%s", cuda_error_str(e->ret_val));
        break;
    
    /* Similar cases for other event types... */
    }
}
```

這個函數對每種事件類型都有不同的處理方式。例如，malloc事件在入口顯示請求的大小，在退出時顯示錯誤代碼。

主事件循環非常簡單：

```c
while (!exiting) {
    err = ring_buffer__poll(rb, 100 /* timeout, ms */);
    /* Error handling... */
}
```

這會輪詢環形緩衝區的事件，對每個事件調用`handle_event`。100ms超時確保程序對信號（如Ctrl+C）保持響應。

## CUDA錯誤處理和報告

我們追蹤器的一個重要方面是將CUDA錯誤代碼轉換為人類可讀的消息。CUDA有100多種不同的錯誤代碼，從簡單的"內存不足"到複雜的"不支持的PTX版本"。

我們的工具包括一個全面的`cuda_error_str`函數，將這些數字代碼映射到字符串描述：

```c
static const char *cuda_error_str(int error) {
    switch (error) {
    case 0:  return "Success";
    case 1:  return "InvalidValue";
    case 2:  return "OutOfMemory";
    /* Many more error codes... */
    default: return "Unknown";
    }
}
```

這使輸出對調試更有用。不是看到"錯誤2"，而是看到"OutOfMemory"，這立即告訴你出了什麼問題。

## 編譯和執行

使用提供的Makefile構建追蹤器非常簡單：

```bash
# 構建追蹤器和示例
make
```

這將創建兩個二進制文件：
- `cuda_events`：基於eBPF的CUDA追蹤工具
- `basic02`：一個簡單的CUDA示例應用程序

構建系統足夠智能，可以使用`nvidia-smi`檢測你的GPU架構，並使用適當的標誌編譯CUDA代碼。

運行追蹤器同樣簡單：

```bash
# 啟動追蹤工具
sudo ./cuda_events -p ./basic02

# 在另一個終端運行CUDA示例
./basic02
```

你還可以通過PID追蹤特定進程：

```bash
# 運行CUDA示例
./basic02 &
PID=$!

# 使用PID過濾啟動追蹤工具
sudo ./cuda_events -p ./basic02 -d $PID
```

示例輸出顯示了每個CUDA操作的詳細信息：

```
Using CUDA library: ./basic02
TIME     PROCESS          PID     EVENT                 TYPE    DETAILS
17:35:41 basic02          12345   cudaMalloc          [ENTER]  size=4000 bytes
17:35:41 basic02          12345   cudaMalloc           [EXIT]  returned=Success
17:35:41 basic02          12345   cudaMalloc          [ENTER]  size=4000 bytes
17:35:41 basic02          12345   cudaMalloc           [EXIT]  returned=Success
17:35:41 basic02          12345   cudaMemcpy          [ENTER]  size=4000 bytes, kind=1
17:35:41 basic02          12345   cudaMemcpy           [EXIT]  returned=Success
17:35:41 basic02          12345   cudaLaunchKernel    [ENTER]  func=0x7f1234567890
17:35:41 basic02          12345   cudaLaunchKernel     [EXIT]  returned=Success
17:35:41 basic02          12345   cudaMemcpy          [ENTER]  size=4000 bytes, kind=2
17:35:41 basic02          12345   cudaMemcpy           [EXIT]  returned=Success
17:35:41 basic02          12345   cudaFree            [ENTER]  ptr=0x7f1234568000
17:35:41 basic02          12345   cudaFree             [EXIT]  returned=Success
17:35:41 basic02          12345   cudaFree            [ENTER]  ptr=0x7f1234569000
17:35:41 basic02          12345   cudaFree             [EXIT]  returned=Success
```

這個輸出顯示了CUDA應用程序的典型流程：
1. 在設備上分配內存
2. 從主機複製數據到設備（kind=1）
3. 啟動內核處理數據
4. 從設備複製結果回主機（kind=2）
5. 釋放設備內存

## 基準測試

我們還提供了一個基準測試工具來測試追蹤器的性能和CUDA API調用的延遲。

```bash
make
sudo ./cuda_events -p ./bench
./bench
```

當沒有追蹤時，結果如下：

```
Data size: 1048576 bytes (1024 KB)
Iterations: 10000

Summary (average time per operation):
-----------------------------------
cudaMalloc:           113.14 µs
cudaMemcpyH2D:        365.85 µs
cudaLaunchKernel:       7.82 µs
cudaMemcpyD2H:        393.55 µs
cudaFree:               0.00 µs
```

當附加追蹤器時，結果如下：

```
Data size: 1048576 bytes (1024 KB)
Iterations: 10000

Summary (average time per operation):
-----------------------------------
cudaMalloc:           119.81 µs
cudaMemcpyH2D:        367.16 µs
cudaLaunchKernel:       8.77 µs
cudaMemcpyD2H:        383.66 µs
cudaFree:               0.00 µs
```

追蹤器為每個CUDA API調用增加了約2微秒的開銷，這對大多數情況來說是可以忽略不計的。為了進一步減少開銷，你可以嘗試使用[bpftime](https://github.com/eunomia-bpf/bpftime)用戶空間運行時來優化eBPF程序。

## 命令行選項

`cuda_events`工具支持以下選項：

- `-v`：啟用詳細調試輸出
- `-t`：不打印時間戳
- `-r`：不顯示函數返回（只顯示函數入口）
- `-p PATH`：指定CUDA運行庫或應用程序的路徑
- `-d PID`：僅追蹤指定的進程ID

## 下一步

一旦你熟悉了這個基本的CUDA追蹤工具，你可以擴展它來：

1. 添加對更多CUDA API函數的支持
2. 添加時間信息以分析性能瓶頸
3. 實現相關操作之間的關聯（例如，匹配malloc和free）
4. 創建CUDA操作的可視化，便於分析
5. 添加對其他GPU框架（如OpenCL或ROCm）的支持

更多關於CUDA追蹤工具的細節，請查看我們的教程倉庫：[https://github.com/eunomia-bpf/basic-cuda-tutorial](https://github.com/eunomia-bpf/basic-cuda-tutorial)

這個教程的代碼在[https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/47-cuda-events](https://github.com/eunomia-bpf/bpf-developer-tutorial/tree/main/src/47-cuda-events)

## 參考資料

- CUDA編程指南：[https://docs.nvidia.com/cuda/cuda-c-programming-guide/](https://docs.nvidia.com/cuda/cuda-c-programming-guide/)
- NVIDIA CUDA運行時API：[https://docs.nvidia.com/cuda/cuda-runtime-api/](https://docs.nvidia.com/cuda/cuda-runtime-api/)
- libbpf文檔：[https://libbpf.readthedocs.io/](https://libbpf.readthedocs.io/)
- Linux uprobes文檔：[https://www.kernel.org/doc/Documentation/trace/uprobetracer.txt](https://www.kernel.org/doc/Documentation/trace/uprobetracer.txt)

如果你想深入瞭解eBPF，請查看我們的教程倉庫：[https://github.com/eunomia-bpf/bpf-developer-tutorial](https://github.com/eunomia-bpf/bpf-developer-tutorial) 或訪問我們的網站：[https://eunomia.dev/tutorials/](https://eunomia.dev/tutorials/)。
