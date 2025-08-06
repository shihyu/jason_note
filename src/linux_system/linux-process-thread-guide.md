# Linux Process、Thread 與系統概念完整指南

## 1. 空間劃分概念

```
Memory Layout:
┌─────────────────┐ 0xFFFFFFFF
│   Kernel Space  │ (內核空間)
│   - 內核代碼    │
│   - 內核數據    │
│   - 驅動程序    │
├─────────────────┤ 0xC0000000 (典型分界)
│   User Space    │ (用戶空間)
│   - 應用程序    │
│   - 庫文件      │
│   - 用戶數據    │
└─────────────────┘ 0x00000000
```

## 2. 常見混淆概念對比

### 混淆一：PID 的不同含義

```
User Space 視角:
Process A (PID=1234)
├─ Thread 1 
├─ Thread 2
└─ Thread 3

Kernel Space 視角:
task_struct (PID=1234, TGID=1234)  ← Process A 主線程
task_struct (PID=1235, TGID=1234)  ← Thread 1
task_struct (PID=1236, TGID=1234)  ← Thread 2  
task_struct (PID=1237, TGID=1234)  ← Thread 3
```

**關鍵理解**：
- User space 的 "PID" = Kernel 的 "TGID"
- Kernel 的每個 task 都有獨立的 PID

### 混淆二：Process vs Thread 的本質

| 概念 | User Space 視角 | Kernel Space 視角 |
|------|----------------|-------------------|
| Process | 獨立的程序實體 | 一組共享 TGID 的 task |
| Thread | Process 內的執行單元 | 就是 task，與 process 無區別 |
| 創建方式 | `fork()`, `exec()` vs `pthread_create()` | 都是 `clone()`，只是參數不同 |

### 混淆三：資源管理

```c
// User Space 認知
Process A: 有自己的記憶體、檔案等
  Thread 1: 共享 Process A 的資源
  Thread 2: 共享 Process A 的資源

// Kernel Space 實際
task_struct A: 指向一組共享資源
task_struct B: 指向相同的 mm_struct (記憶體)、files_struct (檔案) 等
task_struct C: 指向相同的共享資源
```

## 3. 權限與保護

```
User Space (Ring 3):
- 受限制的指令集
- 無法直接存取硬體
- 透過 system call 請求服務

System Call Interface:
- read(), write(), fork(), clone()
- 從 user mode 切換到 kernel mode

Kernel Space (Ring 0):  
- 完整的指令集權限
- 直接存取硬體
- 管理所有資源
```

## 4. 調度的誤解

**❌ 錯誤認知**：Kernel 調度 process，process 內部調度 thread

**✅ 正確理解**：
```
Linux Scheduler (CFS):
├─ task_struct (原 Process A 主線程)
├─ task_struct (原 Thread 1)  
├─ task_struct (原 Thread 2)
├─ task_struct (原 Process B)
└─ task_struct (原 Thread 3)
```
- Kernel 只看到 task，統一調度
- 不區分來源是 process 還是 thread

## 5. 創建方式的差異

```c
// 創建 process (fork)
clone(SIGCHLD)

// 創建 thread (pthread_create 內部調用)
clone(CLONE_VM | CLONE_FILES | CLONE_FS | CLONE_SIGHAND | CLONE_THREAD, ...)
```

### Clone Flags 說明

| Flag | 意義 |
|------|------|
| `SIGCHLD` | 子進程結束時發送信號給父進程 |
| `CLONE_VM` | 共享虛擬記憶體空間 |
| `CLONE_FILES` | 共享檔案描述符表 |
| `CLONE_FS` | 共享檔案系統資訊 |
| `CLONE_SIGHAND` | 共享信號處理器 |
| `CLONE_THREAD` | 放入同一個 thread group |

## 6. 實際例子對比

```bash
# User Space 命令
ps aux              # 看到 process 列表
ps -eLf            # 看到 thread 列表  
top                # 預設顯示 process

# 對應的 Kernel 視角
cat /proc/*/task/*  # 每個都是 task_struct
ls /proc/*/task/    # 看到所有 task ID
```

## 7. 重要標識符

### User Space 視角
- **PID**: Process ID（實際上是 Kernel 的 TGID）
- **TID**: Thread ID（在某些工具中顯示）

### Kernel Space 視角  
- **PID**: 每個 task_struct 的唯一 ID
- **TGID**: Thread Group ID，同一 process 內所有 thread 共享

```
實際對應關係:
User Space PID = Kernel Space TGID
User Space TID = Kernel Space PID
```

## 8. 核心要點記憶法

1. **統一原則**：Kernel 把一切都當作 task
2. **共享程度**：Process vs Thread 只是資源共享程度不同  
3. **視角差異**：User space 有層次概念，Kernel space 是平面的
4. **PID 混淆**：User 的 PID = Kernel 的 TGID
5. **調度統一**：Kernel 調度器不區分 process/thread

## 9. Thread vs Process 基本概念與常見誤解

### 基本定義對比

| 特性 | Process | Thread |
|------|---------|--------|
| **定義** | 獨立的執行環境 | Process 內的執行單元 |
| **記憶體** | 獨立的地址空間 | 共享 Process 的地址空間 |
| **創建成本** | 高（需複製資源） | 低（共享現有資源） |
| **通信方式** | IPC（管道、信號、共享記憶體） | 直接存取共享變數 |
| **錯誤隔離** | 一個 Process 崩潰不影響其他 | 一個 Thread 崩潰可能影響整個 Process |

### 常見誤解與澄清

#### 誤解一：「Thread 比較快」
```
❌ 錯誤理解：Thread 執行比 Process 快
✅ 正確理解：
- Thread 創建/切換成本較低
- 但執行速度取決於工作負載，不是 Thread/Process 本身
- 單核心上過多 Thread 反而可能因競爭資源而變慢
```

#### 誤解二：「Process 無法共享資料」
```
❌ 錯誤理解：Process 間完全無法共享資料
✅ 正確理解：Process 可透過多種 IPC 機制共享資料
- 共享記憶體 (shared memory)
- 記憶體映射檔案 (mmap)
- 管道 (pipe)、訊息佇列等
```

#### 誤解三：「Thread 一定比 Process 省記憶體」
```
❌ 錯誤理解：Thread 總是比 Process 節省記憶體
✅ 正確理解：
- Thread 共享 code、data、heap 區段
- 但每個 Thread 仍需獨立的 stack 空間
- 大量 Thread 的 stack 總和可能很可觀
```

## 10. 記憶體管理深度解析

### Process 記憶體布局

```
Process A 記憶體空間:
┌─────────────────┐ 高位址
│     Stack       │ ← 各 Thread 獨立
├─────────────────┤
│       ↓         │
│                 │
│   未使用空間    │
│                 │
│       ↑         │ 
├─────────────────┤
│      Heap       │ ← 所有 Thread 共享
├─────────────────┤
│  Uninitialized  │ ← BSS 段
│     Data        │
├─────────────────┤  
│   Initialized   │ ← Data 段 (所有 Thread 共享)
│     Data        │
├─────────────────┤
│      Code       │ ← Text 段 (所有 Thread 共享)
└─────────────────┘ 低位址
```

### Thread 記憶體共享詳解

```c
// 共享區域 (所有 Thread 可存取)
- Code segment (程式碼)
- Data segment (全域變數、靜態變數)  
- Heap (malloc/new 分配的記憶體)
- 開啟的檔案描述符
- 信號處理器

// 私有區域 (各 Thread 獨立)
- Stack (區域變數、函數參數)
- 暫存器狀態
- Program Counter (PC)
- Stack Pointer (SP)
```

### 記憶體相關誤解

#### 誤解一：「Thread 共享所有記憶體」
```
❌ 錯誤：Thread 共享包含 stack 在內的所有記憶體
✅ 正確：Thread 有各自獨立的 stack 空間

實例:
void* thread_func(void* arg) {
    int local_var = 10;  // 各 Thread 獨立，存在各自 stack
    static int static_var = 20;  // 所有 Thread 共享
    return NULL;
}
```

#### 誤解二：「Process fork 會完整複製記憶體」
```
❌ 錯誤：fork() 立即複製所有記憶體內容
✅ 正確：現代系統使用 Copy-on-Write (COW)

機制說明:
1. fork() 後，父子 Process 共享相同的實體記憶體頁面
2. 當任一方嘗試寫入時，才真正複製該頁面
3. 大幅減少 fork() 的記憶體成本
```

#### 誤解三：「Thread Stack 大小固定」
```
❌ 錯誤：每個 Thread 都有固定大小的 stack
✅ 正確：Stack 大小可以設定，且有預設值

Linux 預設值:
- 主 Thread: 8MB (可透過 ulimit 調整)
- 其他 Thread: 2MB (可透過 pthread_attr_setstacksize 調整)

查看方式:
ulimit -s          # 查看 stack 大小限制
cat /proc/PID/maps # 查看記憶體映射
```

### Virtual Memory 與實際記憶體

```
虛擬記憶體視角:
Process A: 0x00000000 - 0xFFFFFFFF (4GB 虛擬空間)
Process B: 0x00000000 - 0xFFFFFFFF (4GB 虛擬空間)

實體記憶體視角:
實際可能只有 8GB RAM，透過 MMU 進行映射
- 相同虛擬位址可能對應不同實體位址
- 相同實體位址可能被多個虛擬位址映射 (shared library)
```

### 記憶體洩漏常見情境

#### Thread 相關記憶體洩漏
```c
// ❌ 常見錯誤
pthread_t threads[1000];
for (int i = 0; i < 1000; i++) {
    pthread_create(&threads[i], NULL, worker, NULL);
    // 忘記 pthread_join 或 pthread_detach
}
// 結果：Thread 資源無法回收

// ✅ 正確做法
pthread_t thread;
pthread_create(&thread, NULL, worker, NULL);
pthread_join(thread, NULL);  // 或 pthread_detach(thread);
```

#### 共享記憶體洩漏
```c
// ❌ 多個 Thread 都去 malloc，但只有一個 free
void* shared_ptr = malloc(1024);  // Thread 1 分配
free(shared_ptr);                 // Thread 2 釋放，其他 Thread 不知道

// ✅ 明確記憶體管理責任
// 使用 reference counting 或明確定義 owner
```

## 11. 實務除錯技巧

### 查看 Process/Thread 狀態
```bash
# 查看 Process 記憶體使用
cat /proc/PID/status | grep -E "(VmSize|VmRSS|Threads)"

# 查看所有 Thread
ps -eLf | grep PROCESS_NAME

# 查看記憶體映射
cat /proc/PID/maps

# 即時監控
htop -H    # 顯示 Thread
```

### GDB 除錯 Thread
```bash
# 查看所有 Thread
(gdb) info threads

# 切換到特定 Thread
(gdb) thread 2

# 查看 Thread 的 stack
(gdb) bt

# 查看共享變數
(gdb) print global_variable
```

## 總結

> **核心概念**: User space 的抽象概念在 kernel space 都被統一成 task 來處理

### 關鍵記憶點

1. **記憶體共享**：Thread 共享 code/data/heap，但各有獨立 stack
2. **成本差異**：Process 創建成本高但隔離性好，Thread 輕量但易互相影響  
3. **除錯觀念**：理解虛擬記憶體 vs 實體記憶體的差異
4. **資源管理**：Thread 資源需要明確管理（join/detach）
5. **COW 機制**：fork 不會立即複製記憶體，而是使用 Copy-on-Write

## 12. Signal 與 Process/Thread 關係

### Signal 常見誤解

#### 誤解一：「Signal 只發給 Process」
```
❌ 錯誤：Signal 只能發送給整個 Process
✅ 正確：Linux 支持發送 Signal 給特定 Thread

發送方式:
kill(pid, SIGTERM);        // 發給整個 Process Group  
pthread_kill(thread_id, SIGTERM);  // 發給特定 Thread
tgkill(tgid, tid, SIGTERM); // Kernel 層面發給特定 Thread
```

#### 誤解二：「多個 Thread 會同時收到 Signal」
```
❌ 錯誤：Signal 發給 Process 時所有 Thread 都會收到
✅ 正確：只有一個 Thread 會處理 Signal

處理規則:
1. 如果有 Thread 明確 blocked 該 Signal → 跳過
2. 如果有 Thread 在等待該 Signal (sigwait) → 優先給它
3. 否則隨機選一個 Thread 處理
```

### Signal Mask 機制
```c
// 各 Thread 有獨立的 Signal Mask
sigset_t set;
sigemptyset(&set);
sigaddset(&set, SIGINT);
pthread_sigmask(SIG_BLOCK, &set, NULL);  // 只影響當前 Thread

// 但 Signal Handler 是所有 Thread 共享的
signal(SIGINT, handler);  // 影響整個 Process
```

## 13. File Descriptor 與 Process/Thread

### 檔案描述符共享機制

#### Fork 後的 FD 行為
```c
int fd = open("test.txt", O_RDONLY);
pid_t pid = fork();

if (pid == 0) {
    // 子 Process
    read(fd, buffer, 100);  // ✅ 可以使用，與父 Process 共享
    close(fd);              // ❌ 會影響父 Process！
} else {
    // 父 Process  
    read(fd, buffer, 100);  // 可能讀到子 Process 讀過的位置
}
```

**關鍵概念**: Fork 後 FD 共享同一個 file table entry
- 檔案位置指標 (file offset) 是共享的
- 一方 close() 會減少 reference count
- 只有所有引用都 close() 後才真正關閉檔案

#### Thread 間的 FD 共享
```c
// Thread 間完全共享 FD table
int fd = open("test.txt", O_RDONLY);

void* thread1(void* arg) {
    lseek(fd, 100, SEEK_SET);  // 設定檔案位置
    return NULL;
}

void* thread2(void* arg) {
    char buffer[10];
    read(fd, buffer, 10);  // 會從位置 100 開始讀！
    return NULL;
}
```

### 常見 FD 管理錯誤

#### 錯誤一：多 Thread 同時操作同一 FD
```c
// ❌ 危險：多個 Thread 同時寫入同一檔案
void* writer_thread(void* arg) {
    write(shared_fd, data, size);  // 可能與其他 Thread 的寫入交錯
}

// ✅ 安全：使用 mutex 保護
pthread_mutex_t fd_mutex = PTHREAD_MUTEX_INITIALIZER;
void* safe_writer_thread(void* arg) {
    pthread_mutex_lock(&fd_mutex);
    write(shared_fd, data, size);
    pthread_mutex_unlock(&fd_mutex);
}
```

#### 錯誤二：忘記設定 FD_CLOEXEC
```c
// ❌ 子 Process 會繼承不必要的 FD
int fd = open("config.txt", O_RDONLY);
execve("/usr/bin/program", argv, envp);  // program 也能存取 config.txt

// ✅ 使用 FD_CLOEXEC
int fd = open("config.txt", O_RDONLY);  
fcntl(fd, F_SETFD, FD_CLOEXEC);  // exec 時自動關閉
```

## 14. 同步機制常見誤解

### Mutex vs Spinlock vs Semaphore

| 機制 | 使用時機 | CPU 行為 | 適用場景 |
|------|---------|----------|----------|
| **Mutex** | 長時間等待 | Thread 讓出 CPU | I/O 操作、長運算 |
| **Spinlock** | 短時間等待 | 持續檢查，不讓出 CPU | 保護共享計數器 |  
| **Semaphore** | 資源計數 | 可設定資源數量 | 連線池、記憶體池 |

### 常見同步錯誤

#### 錯誤一：誤用 Spinlock
```c
// ❌ 錯誤：在可能長時間等待的場景使用 Spinlock
spinlock_t lock;
spin_lock(&lock);
sleep(1);  // 持有 lock 時睡眠 → CPU 空轉
spin_unlock(&lock);

// ✅ 正確：使用 Mutex
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_mutex_lock(&mutex);
sleep(1);
pthread_mutex_unlock(&mutex);
```

#### 錯誤二：死鎖 (Deadlock)
```c
// ❌ 典型死鎖場景
Thread 1: lock(A) → lock(B)
Thread 2: lock(B) → lock(A)

// ✅ 解決方案：統一加鎖順序
void safe_function() {
    // 總是先鎖 A 再鎖 B
    pthread_mutex_lock(&mutex_A);
    pthread_mutex_lock(&mutex_B);
    // 做事情
    pthread_mutex_unlock(&mutex_B);
    pthread_mutex_unlock(&mutex_A);
}
```

## 15. Context Switch 開銷誤解

### 真實的 Context Switch 成本

```
Process Context Switch:
1. 保存暫存器狀態 (~50 cycles)
2. 切換記憶體映射表 (~100-500 cycles) ← 昂貴
3. TLB flush (~1000+ cycles) ← 非常昂貴  
4. Cache miss penalty (~數千 cycles) ← 最昂貴

Thread Context Switch (同一 Process):
1. 保存暫存器狀態 (~50 cycles)
2. 切換 Stack pointer (~10 cycles)
3. 不需切換記憶體映射 ← 省下大量成本
```

#### 誤解：「Thread Switch 沒有成本」
```
❌ 錯誤：Thread 間切換完全沒有開銷
✅ 正確：有開銷，但比 Process Switch 小很多

實際測量:
Process Switch: ~1-10 microseconds  
Thread Switch: ~0.1-1 microseconds
Function Call: ~1-10 nanoseconds
```

## 16. 系統限制與配置

### 重要的系統限制

```bash
# Thread 相關限制
cat /proc/sys/kernel/threads-max     # 系統最大 Thread 數
ulimit -u                           # 每個使用者最大 Process 數
cat /proc/sys/kernel/pid_max        # 最大 PID 值

# 記憶體相關限制  
ulimit -s                           # Stack 大小限制
ulimit -v                           # 虛擬記憶體限制
cat /proc/sys/vm/max_map_count      # 記憶體映射數量限制

# 檔案相關限制
ulimit -n                           # 每個 Process 最大 FD 數
cat /proc/sys/fs/file-max           # 系統最大檔案數
```

### 常見的「無法創建 Thread」錯誤

```c
// 錯誤排查步驟
int ret = pthread_create(&thread, NULL, worker, NULL);
if (ret != 0) {
    switch(ret) {
        case EAGAIN:  // 超過系統限制
            printf("系統資源不足或達到 Thread 數量限制\n");
            break;
        case ENOMEM:  // 記憶體不足
            printf("無法分配記憶體給新 Thread\n");  
            break;
        case EPERM:   // 權限不足
            printf("沒有權限創建 Thread\n");
            break;
    }
}
```

## 17. 效能監控與分析

### 實用監控命令

```bash
# 即時監控 Process/Thread
htop -H                    # 顯示 Thread
top -H -p PID             # 監控特定 Process 的 Thread

# 分析 Context Switch
vmstat 1                  # cs 欄位顯示 context switch 次數
pidstat -w 1              # 每個 Process 的 context switch

# 記憶體分析
pmap PID                  # Process 記憶體映射
cat /proc/PID/smaps       # 詳細記憶體使用

# CPU 使用分析
perf top                  # 即時 CPU hotspot
perf stat -p PID          # Process 效能統計
```

### 效能分析工具鏈

```bash
# 系統呼叫追蹤
strace -f -p PID          # 追蹤 Process 及其子 Process/Thread
ltrace -f -p PID          # 追蹤函式庫呼叫

# Thread 同步分析  
helgrind ./program        # Valgrind 工具，檢測競爭條件
drd ./program             # 另一個同步檢測工具
```

## 18. 實戰最佳實踐

### Process vs Thread 選擇指南

```
選擇 Process 當：
✅ 需要強隔離性（一個崩潰不影響其他）
✅ 需要不同權限等級
✅ 需要分散到不同機器（微服務架構）
✅ CPU 密集型工作且可平行處理

選擇 Thread 當：
✅ 需要頻繁共享大量資料
✅ I/O 密集型工作（如網路服務）
✅ 需要細粒度的併發控制
✅ 記憶體使用需要優化
```

### 避免常見陷阱

```c
// 1. Thread 安全的單例模式
class Singleton {
private:
    static std::once_flag flag;
    static Singleton* instance;
public:
    static Singleton* getInstance() {
        std::call_once(flag, []() {
            instance = new Singleton();
        });
        return instance;
    }
};

// 2. 正確的 Thread 終止
volatile bool should_exit = false;
void* worker_thread(void* arg) {
    while (!should_exit) {
        // 做工作
        if (should_exit) break;  // 檢查退出條件
    }
    return NULL;
}

// 3. 記憶體屏障的重要性
// 在某些架構上，需要明確的記憶體屏障
__sync_synchronize();  // GCC builtin
// 或使用 C11 atomic 操作
```

## 19. 記憶體管理與 OOM (Out of Memory) 殺手機制

### 記憶體回收機制詳解

#### 虛擬記憶體與實體記憶體的關係
```
虛擬記憶體分配:
Process A 要求 1GB → Linux 立即同意 (虛擬分配)
Process B 要求 2GB → Linux 立即同意 (虛擬分配)  
Process C 要求 4GB → Linux 立即同意 (虛擬分配)

實體記憶體分配:
只有在實際存取時才分配實體記憶體頁面
這就是「延遲分配」(Lazy Allocation) 或「按需分頁」(Demand Paging)
```

#### 記憶體回收的層次
```
記憶體壓力響應機制:
1. Page Cache 回收    ← 最溫和，釋放檔案快取
2. Swap 機制啟動      ← 將記憶體頁面寫入交換空間
3. 主動回收機制       ← kswapd 背景進程啟動
4. 直接回收          ← 分配記憶體時同步回收
5. OOM Killer 啟動   ← 最後手段，殺死進程
```

### OOM 殺手 (OOM Killer) 工作原理

#### OOM Killer 觸發條件
```
觸發場景:
1. 實體記憶體 + Swap 空間都耗盡
2. 特定記憶體域 (memory zone) 耗盡
3. 記憶體碎片化嚴重，無法分配大塊連續記憶體
4. cgroup 記憶體限制達到上限

常見誤解:
❌ 錯誤：「記憶體用完就會 OOM」
✅ 正確：「無法分配必要的記憶體才會 OOM」
```

#### OOM Score 計算機制
```bash
# 查看進程的 OOM Score
cat /proc/PID/oom_score      # 當前分數 (0-1000)
cat /proc/PID/oom_score_adj  # 調整值 (-1000 到 1000)

# OOM Score 計算因子
影響因子              權重說明
記憶體使用量          使用越多分數越高
CPU 時間             運行時間短的進程分數較高  
Nice 值              Nice 值高的進程分數較高
是否為 Root 進程      Root 進程分數會降低
子進程數量           有很多子進程的分數較高
```

#### OOM Killer 選擇邏輯 (白話解釋)
```
OOM Killer 的心理活動:
1. "誰用了最多記憶體？" → 記憶體大戶優先考慮
2. "誰剛啟動不久？" → 新進程比老進程更容易被選中
3. "誰不重要？" → Nice 值高的進程更容易被選中
4. "誰是 Root？" → Root 進程有一定保護
5. "殺掉誰能釋放最多記憶體？" → 效益最大化

簡化公式:
OOM Score = (記憶體使用百分比 × 10) + oom_score_adj + 其他修正
```

### 記憶體洩漏 vs OOM 的區別

#### 記憶體洩漏 (Memory Leak)
```c
// 典型的記憶體洩漏
void leaky_function() {
    for (int i = 0; i < 1000; i++) {
        char *ptr = malloc(1024 * 1024);  // 分配 1MB
        // 忘記 free(ptr); ← 記憶體洩漏
        
        // 即使離開函數，記憶體仍被佔用
        // 虛擬記憶體和實體記憶體都無法回收
    }
}

洩漏特徵:
- 程式仍在運行但記憶體使用持續增長
- 重啟程式後記憶體使用恢復正常
- 影響整個系統的記憶體可用性
```

#### 記憶體溢出 (OOM)
```c
// 瞬間大量分配導致 OOM
void oom_function() {
    // 嘗試分配 8GB 記憶體
    char *huge_buffer = malloc(8L * 1024 * 1024 * 1024);
    
    if (huge_buffer == NULL) {
        printf("分配失敗，可能觸發 OOM\n");
    } else {
        // 如果分配成功但系統記憶體不足
        // 在實際使用時可能觸發 OOM Killer
        memset(huge_buffer, 0, 8L * 1024 * 1024 * 1024);
    }
}
```

### OOM 預防與處理策略

#### 預防措施
```bash
# 1. 監控記憶體使用
free -h                    # 查看系統記憶體狀況
cat /proc/meminfo          # 詳細記憶體資訊
vmstat 1                   # 即時記憶體統計

# 2. 設定記憶體限制
ulimit -v 2097152          # 限制虛擬記憶體為 2GB
echo 1000000 > /proc/sys/vm/max_map_count  # 限制記憶體映射數

# 3. 調整 Swap 策略
echo 10 > /proc/sys/vm/swappiness  # 降低 swap 使用傾向 (0-100)
echo 1 > /proc/sys/vm/overcommit_memory  # 嚴格記憶體檢查
```

#### 程式層面的防護
```c
// 1. 檢查記憶體分配結果
void* safe_malloc(size_t size) {
    void* ptr = malloc(size);
    if (ptr == NULL) {
        fprintf(stderr, "記憶體分配失敗，請求大小: %zu bytes\n", size);
        // 可以選擇退出或釋放其他資源後重試
        exit(EXIT_FAILURE);
    }
    return ptr;
}

// 2. 使用 mmap 代替大量 malloc
void* large_allocation(size_t size) {
    void* ptr = mmap(NULL, size, PROT_READ | PROT_WRITE,
                     MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (ptr == MAP_FAILED) {
        return NULL;
    }
    return ptr;
}

// 3. 設定進程記憶體限制
#include <sys/resource.h>
void set_memory_limit(size_t limit_mb) {
    struct rlimit limit;
    limit.rlim_cur = limit_mb * 1024 * 1024;  // 當前限制
    limit.rlim_max = limit_mb * 1024 * 1024;  // 最大限制
    
    if (setrlimit(RLIMIT_AS, &limit) != 0) {
        perror("設定記憶體限制失敗");
    }
}
```

### OOM Killer 日誌分析

#### 典型 OOM 日誌解讀
```
[12345.678901] Out of memory: Kill process 1234 (myprogram) score 800 or sacrifice child
[12345.678902] Killed process 1234 (myprogram) total-vm:2097152kB, anon-rss:1048576kB, file-rss:0kB, shmem-rss:0kB

解讀:
- Kill process 1234: 被殺的進程 PID
- score 800: OOM Score (最高1000)
- total-vm: 總虛擬記憶體
- anon-rss: 匿名常駐記憶體 (heap, stack)
- file-rss: 檔案映射記憶體
- shmem-rss: 共享記憶體
```

#### OOM 事件監控
```bash
# 1. 查看 OOM Killer 歷史
dmesg | grep -i "killed process"
journalctl --since "1 hour ago" | grep -i oom

# 2. 實時監控記憶體壓力
cat /proc/pressure/memory      # PSI (Pressure Stall Information)
watch -n 1 'free -h && echo "--- Top Memory Users ---" && ps aux --sort=-%mem | head -10'

# 3. 設定 OOM 通知
echo "/usr/local/bin/oom_notify.sh" > /proc/sys/vm/panic_on_oom
```

### 容器環境下的 OOM 特殊情況

#### Docker/Kubernetes 中的 OOM
```bash
# 容器記憶體限制
docker run -m 512m myapp        # 限制容器記憶體為 512MB

# 當容器超過記憶體限制:
# 1. 容器內的進程會被 OOM Killer 殺死
# 2. 容器可能會重啟 (依 restart policy)
# 3. 不會影響宿主機上的其他容器

# 查看容器 OOM 事件
docker stats                   # 即時資源使用
kubectl top pods              # K8s Pod 資源使用
kubectl describe pod POD_NAME  # 查看 OOM 事件詳情
```

### 記憶體除錯工具

#### Valgrind 記憶體檢查
```bash
# 檢查記憶體洩漏
valgrind --leak-check=full --show-leak-kinds=all ./myprogram

# 檢查記憶體錯誤
valgrind --tool=memcheck ./myprogram

# 分析記憶體使用模式
valgrind --tool=massif ./myprogram
ms_print massif.out.PID
```

#### 系統層面記憶體分析
```bash
# 分析系統記憶體使用
cat /proc/buddyinfo           # 記憶體碎片資訊
cat /proc/pagetypeinfo        # 頁面類型統計
cat /proc/zoneinfo           # 記憶體區域資訊

# 分析進程記憶體映射
pmap -X PID                  # 詳細記憶體映射
cat /proc/PID/smaps          # 最詳細的記憶體使用資訊
```

## 20. 圖解複雜記憶體布局與進程關係

### 完整的記憶體分層視圖

```
                           系統記憶體全景圖
┌─────────────────────────────────────────────────────────────────┐
│                        實體記憶體 (RAM)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────────┐ │
│  │ Page 1  │ │ Page 2  │ │ Page 3  │ │         ...            │ │
│  │  4KB    │ │  4KB    │ │  4KB    │ │                        │ │
│  └─────────┘ └─────────┘ └─────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                ↑
                      記憶體管理單元 (MMU)
                                ↕
┌─────────────────────────────────────────────────────────────────┐
│                     虛擬記憶體空間映射                          │
│                                                                │
│ Process A 虛擬空間            Process B 虛擬空間               │
│ ┌─────────────────┐           ┌─────────────────┐              │
│ │ 0xFFFF0000     │           │ 0xFFFF0000     │              │
│ │    Stack       │ ────┐     │    Stack       │ ────┐        │
│ │ 0xC0000000     │     │     │ 0xC0000000     │     │        │
│ │      ↓         │     │     │      ↓         │     │        │
│ │                │     │     │                │     │        │
│ │      ↑         │     │     │      ↑         │     │        │
│ │ 0x08000000     │     │     │ 0x08000000     │     │        │
│ │    Heap        │ ────┼──── │    Heap        │ ────┼──→ 不同實體頁面
│ │ 0x00401000     │     │     │ 0x00401000     │     │        │
│ │    Data        │ ────┼──── │    Data        │ ────┘        │
│ │ 0x00400000     │     │     │ 0x00400000     │              │
│ │    Code        │ ────┴──── │    Code        │ ────→ 共享相同實體頁面
│ │ 0x00000000     │           │ 0x00000000     │              │
│ └─────────────────┘           └─────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

### Thread 記憶體布局詳細圖解

```
                   單一 Process 內多 Thread 記憶體分布:

┌─────────────────────────────────────────────────────────────────┐ 0xFFFFFFFF
│                        Kernel Space                            │
│                       (所有進程共用)                           │
├─────────────────────────────────────────────────────────────────┤ 0xC0000000
│                       User Space                               │
│                                                                │
│ Thread 1 Stack      Thread 2 Stack      Thread 3 Stack        │ 高位址
│ ┌─────────────┐     ┌─────────────┐     ┌─────────────┐        │
│ │ 局部變數    │     │ 局部變數    │     │ 局部變數    │        │
│ │ 函數呼叫    │     │ 函數呼叫    │     │ 函數呼叫    │        │
│ │ 回傳位址    │     │ 回傳位址    │     │ 回傳位址    │        │
│ └─────────────┘     └─────────────┘     └─────────────┘        │
│        │                   │                   │               │
│        ↓                   ↓                   ↓               │
│                                                                │
│                      未使用記憶體區域                          │
│                                                                │
│        ↑                                                       │
│        │                                                       │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                      Heap 區域                             │ │
│ │                (所有 Thread 共享)                          │ │
│ │     malloc()、new、全域變數、動態分配的資料               │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                      Data 段                               │ │
│ │                (所有 Thread 共享)                          │ │
│ │           全域變數、靜態變數、常數                          │ │
│ └─────────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────────┐ │
│ │                      Code 段                               │ │ 低位址
│ │                (所有 Thread 共享)                          │ │
│ │                   程式執行碼                               │ │
│ └─────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘ 0x00000000
```

### Fork vs Thread Creation 視覺化對比

#### Fork() 創建 Process
```
                          Fork() 過程

原始 Process A                      新 Process B
┌─────────────────┐   fork()   ┌─────────────────┐
│   Stack A       │    ──→     │   Stack B       │ ← 完整複製
├─────────────────┤            ├─────────────────┤
│   Heap A        │    ──→     │   Heap B        │ ← Copy-on-Write
├─────────────────┤            ├─────────────────┤
│   Data A        │    ──→     │   Data B        │ ← Copy-on-Write
├─────────────────┤            ├─────────────────┤
│   Code A        │    ──→     │   Code B        │ ← 共享只讀
└─────────────────┘            └─────────────────┘

特點:
- 每個 Process 有獨立的虛擬記憶體空間
- 初始時透過 COW 共享實體記憶體
- 寫入時才真正複製頁面
- PID 不同，PPID 指向父進程
```

#### pthread_create() 創建 Thread
```
                       pthread_create() 過程

原始狀態                           新增 Thread 後
┌─────────────────┐                 ┌─────────────────┐
│   Main Stack    │                 │   Main Stack    │ ← 原有
├─────────────────┤   create thread   ├─────────────────┤
│                 │      ──→       │   Thread Stack  │ ← 新增
│   Shared Heap   │                 │   Shared Heap   │ ← 共享
├─────────────────┤                 ├─────────────────┤
│   Shared Data   │                 │   Shared Data   │ ← 共享
├─────────────────┤                 ├─────────────────┤
│   Shared Code   │                 │   Shared Code   │ ← 共享
└─────────────────┘                 └─────────────────┘

特點:
- 共享相同的虛擬記憶體空間
- 只有 Stack 是獨立的
- 相同的 TGID，不同的 PID (kernel 視角)
- 共享檔案描述符、信號處理器等
```

### Context Switch 視覺化

#### Process Context Switch (昂貴)
```
Process A 執行中                切換過程                 Process B 執行中

┌─────────────────┐                儲存 A 狀態:        ┌─────────────────┐
│ CPU Registers   │                ├ 暫存器           │ CPU Registers   │
│ PC: 0x401234    │     ───→       ├ PC 指標          │ PC: 0x501234    │
│ SP: 0xBFFF1000  │                ├ Stack 指標       │ SP: 0xBFFF2000  │
└─────────────────┘                └ 其他狀態         └─────────────────┘

┌─────────────────┐                切換記憶體映射:     ┌─────────────────┐
│ Page Table A    │                ├ 更新 MMU         │ Page Table B    │
│ 虛擬→實體對應   │     ───→       ├ 清空 TLB        │ 虛擬→實體對應   │
│                 │                └ 重建快取         │                 │
└─────────────────┘                                  └─────────────────┘

成本: ~1-10 微秒 (包含 Cache Miss)
```

#### Thread Context Switch (便宜)
```
Thread 1 執行中               切換過程                Thread 2 執行中

┌─────────────────┐                儲存 Thread 1:      ┌─────────────────┐
│ CPU Registers   │                ├ 暫存器           │ CPU Registers   │
│ PC: 0x401234    │     ───→       ├ PC 指標          │ PC: 0x401456    │
│ SP: 0xBFFF1000  │                └ Stack 指標       │ SP: 0xBFFF2000  │
└─────────────────┘                                  └─────────────────┘

┌─────────────────┐                記憶體映射不變:     ┌─────────────────┐
│ 相同 Page Table │                ├ MMU 不變         │ 相同 Page Table │
│ 虛擬→實體對應   │     ───→       ├ TLB 有效        │ 虛擬→實體對應   │
│                 │                └ Cache 部分有效   │                 │
└─────────────────┘                                  └─────────────────┘

成本: ~0.1-1 微秒 (大部分快取仍有效)
```

### 記憶體分配策略圖解

#### 虛擬記憶體分配 vs 實體記憶體分配
```
                    程式請求: malloc(1GB)

                虛擬記憶體配置 (立即):
┌───────────────────────────────────────────────────┐
│ 虛擬位址空間: 0x40000000 - 0x80000000 (1GB)       │
│ 狀態: 已分配但未映射到實體記憶體                   │
│ 成本: 幾乎為零                                     │
└───────────────────────────────────────────────────┘
                          ↓
                      實際存取時
                          ↓
                實體記憶體配置 (按需):
┌───────────────────────────────────────────────────┐
│ 第 1 次存取 0x40000000:                           │
│ └→ 分配實體頁面 Page #1234                        │
│ 第 2 次存取 0x40001000:                           │
│ └→ 分配實體頁面 Page #1235                        │
│ 只有真正使用的部分才佔用實體記憶體                 │
└───────────────────────────────────────────────────┘
```

### OOM Killer 選擇流程圖

```
                      記憶體不足警報
                            │
                            ↓
                ┌─────────────────────────┐
                │    啟動記憶體回收        │
                │  - 清理 Page Cache      │
                │  - 啟動 Swap           │
                │  - 壓縮記憶體           │
                └─────────────┬───────────┘
                            │
                     回收成功? ────→ [Yes] ────→ 繼續運行
                            │
                         [No]
                            │
                            ↓
                ┌─────────────────────────┐
                │     啟動 OOM Killer     │
                │                        │
                │  掃描所有進程:          │
                │  ├─ 計算 OOM Score     │
                │  ├─ 排除受保護進程      │
                │  └─ 選擇最高分進程      │
                └─────────────┬───────────┘
                            │
                            ↓
                ┌─────────────────────────┐
                │  殺死選中的進程         │
                │                        │
                │  記錄日誌:              │
                │  "Killed process 1234   │
                │   (myapp) score 856"    │
                └─────────────┬───────────┘
                            │
                            ↓
                 記憶體壓力緩解 ────→ 系統恢復正常
```

### Signal 在 Multi-Thread 中的傳遞

```
           Signal 發送到 Process                Thread 處理機制

外部信號                                 ┌─────────────────┐
(如: kill -TERM 1234)                   │   Thread 1      │
         │                              │ Signal Mask:    │
         │                              │ SIGTERM: 未阻擋 │ ← 可能被選中
         ↓                              └─────────────────┘
┌─────────────────┐                                │
│  Process 1234   │                                │
│  (TGID=1234)    │                     ┌─────────────────┐
│                 │                     │   Thread 2      │
│  內核決定由誰   │ ──────────→     │ Signal Mask:    │
│  處理此信號     │                     │ SIGTERM: 阻擋   │ ← 跳過
└─────────────────┘                     └─────────────────┘
                                              │
                                    ┌─────────────────┐
                                    │   Thread 3      │
                                    │ Signal Mask:    │
                                    │ SIGTERM: 未阻擋 │ ← 可能被選中
                                    │ 但在 sigwait()  │ ← 優先選中
                                    └─────────────────┘

選擇規則:
1. 跳過阻擋該信號的 Thread
2. 優先選擇正在 sigwait() 等待的 Thread  
3. 隨機選擇一個未阻擋的 Thread
4. 只有一個 Thread 會收到信號
```

### File Descriptor 在 Fork 和 Thread 中的行為

#### Fork 後的 FD 共享
```
                Fork 前:                            Fork 後:

          Parent Process                 Parent Process    Child Process
         ┌─────────────────┐         ┌─────────────────┐ ┌─────────────────┐
         │ fd=3            │ ─────→  │ fd=3            │ │ fd=3            │
         │ ↓              │         │ ↓              │ │ ↓              │
         └─────────────────┘         └─────────────────┘ └─────────────────┘
                 │                           │             │
                 ↓                           ↓             ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                      File Table Entry                                      │
│  - file position: 1024                                                    │
│  - access mode: O_RDONLY                                                   │
│  - reference count: 2 ←── 兩個進程都指向同一個                           │
└─────────────────────────────────────────────────────────────────────────────┘

影響:
- 共享檔案位置指標 (file offset)
- 一方 read() 會影響另一方的讀取位置
- 一方 close() 只減少 reference count
```

#### Thread 間的 FD 完全共享
```
              Single Process with Multiple Threads:

   Thread 1              Thread 2              Thread 3
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ fd=3            │    │ fd=3            │    │ fd=3            │
│ fd=4            │ ───│ fd=4            │ ───│ fd=4            │
│ fd=5            │    │ fd=5            │    │ fd=5            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
       │                       │                       │
       └───────────────────┼───────────────────┘
                              │
                              ↓
                ┌───────────────────────────────────────┐
                │          共享 FD Table             │
                │  fd=3 → File A                    │
                │  fd=4 → Socket B                  │  
                │  fd=5 → Pipe C                    │
                └───────────────────────────────────────┘

特點:
- 所有 Thread 看到相同的 FD table
- 任一 Thread 的 close() 都會關閉檔案
- 需要同步機制避免競爭條件
```

## 21. Linux 調度器 (CFS) 工作原理白話解釋

### 什麼是 CFS (Completely Fair Scheduler)

CFS 是 Linux 2.6.23 之後的預設調度器，它的設計哲學很簡單：**每個任務都應該得到公平的 CPU 時間**。

#### CFS 的核心概念
```
傳統調度器的問題:
- 時間片固定 (如 100ms)
- 優先級複雜難理解
- 互動性和公平性難以平衡

CFS 的解決方案:
- 使用「虛擬執行時間」(vruntime) 概念
- 總是執行 vruntime 最小的任務
- 動態調整，沒有固定時間片
```

### CFS 的虛擬時間機制 (白話解釋)

#### 虛擬時間就像是「欠債記帳」
```
想像一個公平的咖啡廳:
- 每個客人都應該得到同等的服務時間
- 如果某個客人等太久，下次就優先服務他
- 如果某個客人剛被服務過，就讓其他人先來

CFS 的 vruntime 就是這個「等待債務」:
┌─────────────────┐
│ Task A: 100ms   │ ← vruntime 最小，下一個執行
├─────────────────┤
│ Task B: 150ms   │
├─────────────────┤  
│ Task C: 200ms   │ ← 剛執行過，vruntime 最大
└─────────────────┘
```

#### vruntime 計算方式
```c
// 簡化的 vruntime 計算
void update_vruntime(struct task_struct *task, u64 runtime) {
    u64 weighted_runtime = runtime;
    
    // Nice 值影響權重
    if (task->nice > 0) {
        weighted_runtime *= 1.25;  // Nice 值高，虛擬時間走得快
    } else if (task->nice < 0) {
        weighted_runtime *= 0.8;   // Nice 值低，虛擬時間走得慢
    }
    
    task->vruntime += weighted_runtime;
}

白話解釋:
- Nice 值高的任務：「虛擬時間走得快」→ 更快輪到下一個
- Nice 值低的任務：「虛擬時間走得慢」→ 可以執行更久
- 這樣 Nice 值低的任務自然得到更多 CPU 時間
```

### 調度決策的完整流程

#### CFS 調度器的心理活動
```
調度器的思考過程:

1. "目前正在跑誰？"
   → 檢查當前任務的 vruntime

2. "他跑夠久了嗎？"  
   → 如果 vruntime 超過左邊鄰居太多 → 需要切換
   → 如果還在合理範圍內 → 繼續執行

3. "下一個該輪誰？"
   → 從紅黑樹最左邊拿出 vruntime 最小的任務

4. "切換成本值得嗎？"
   → 如果切換成本 > 收益，可能延後切換
   
5. "處理完畢，更新紀錄"
   → 更新執行時間、vruntime、統計資料
```

#### 紅黑樹調度視覺化
```
                     CFS 紅黑樹 (按 vruntime 排序)
                     
                       Task C (150ms)
                      /              \
             Task A            Task E (300ms)  
            (100ms)           /              \
               \        Task D           Task F
            Task B     (200ms)          (400ms)
           (120ms)        \
                       Task G
                      (250ms)

調度規則:
1. 永遠選擇最左邊的節點 (vruntime 最小)
2. 任務執行後 vruntime 增加，位置右移
3. 樹自動保持平衡，查找時間 O(log n)
4. 插入新任務時會放在適當位置
```

### 不同工作負載下的 CFS 行為

#### CPU 密集型任務
```
場景: 3 個計算任務同時運行

初始狀態:
Task A: vruntime=0, nice=0
Task B: vruntime=0, nice=0  
Task C: vruntime=0, nice=0

執行過程:
Time 0-10ms: Task A 執行 → vruntime=10
Time 10-20ms: Task B 執行 → vruntime=10  
Time 20-30ms: Task C 執行 → vruntime=10
Time 30-40ms: Task A 執行 → vruntime=20
...

結果: 每個任務輪流得到 ~33.3% CPU 時間 (完全公平)
```

#### I/O 密集型 vs CPU 密集型混合
```
場景: I/O 任務 vs CPU 任務

Task A (I/O 密集):
- 執行 2ms → sleep 等待磁碟 → vruntime=2
- 醒來時發現自己 vruntime 最小 → 立即執行
- 再執行 2ms → 又去等待 → vruntime=4

Task B (CPU 密集):  
- 一直想執行，但經常因為 vruntime 較大而等待
- 得到執行機會時會跑較久 (因為沒有其他事要做)

結果: I/O 任務得到優秀的響應性，CPU 任務仍能得到公平時間
```

### CFS 的智能調整機制

#### 睡眠補償 (Sleep Credit)
```c
// 任務從睡眠中醒來時的處理
void wake_up_task(struct task_struct *task) {
    u64 sleep_time = current_time - task->sleep_start;
    u64 min_vruntime = get_min_vruntime();
    
    // 如果睡眠太久，調整 vruntime 避免「餓死」其他任務
    if (task->vruntime < min_vruntime - MAX_SLEEP_CREDIT) {
        task->vruntime = min_vruntime - MAX_SLEEP_CREDIT;
    }
    
    // 但也不讓它完全追上，保持一點優先性
    if (task->vruntime > min_vruntime) {
        task->vruntime = min_vruntime;
    }
}

白話解釋:
- 睡眠的任務不會累積「無限的優先權」
- 醒來時會有一點優先性，但不會壟斷 CPU
- 平衡互動性和公平性
```

#### 負載平衡 (Load Balancing)
```
多核心環境下的 CFS:

CPU 0: [Task A=100ms] [Task B=150ms]  ← 較輕負載
CPU 1: [Task C=80ms] [Task D=90ms] [Task E=120ms] [Task F=200ms] ← 重負載

CFS 的負載平衡:
1. 定期檢查各 CPU 的負載差異
2. 如果差異過大，觸發任務遷移
3. 選擇合適的任務 (通常是 vruntime 較大的)
4. 遷移時調整 vruntime 以適應目標 CPU

遷移後:
CPU 0: [Task A=100ms] [Task B=150ms] [Task F=200ms] ← 平衡後
CPU 1: [Task C=80ms] [Task D=90ms] [Task E=120ms]   ← 平衡後
```

### 常見的 CFS 誤解

#### 誤解一：「Nice 值是優先級」
```
❌ 錯誤理解: Nice -20 的任務有 20 倍優先權
✅ 正確理解: Nice 值影響權重，進而影響時間分配

實際效果:
Nice 0 vs Nice 19: 約 1.5:1 的時間比例 (不是 19:1)
Nice -20 vs Nice 0: 約 9:1 的時間比例 (不是 20:1)

權重計算:
Nice -10: weight = 9548
Nice 0:   weight = 1024  
Nice 10:  weight = 110
Nice 19:  weight = 15
```

#### 誤解二：「時間片固定」
```
❌ 錯誤理解: CFS 有固定的時間片 (如 10ms)
✅ 正確理解: CFS 動態調整，沒有固定時間片

實際行為:
- 高負載時: 時間片可能只有 1-2ms
- 低負載時: 時間片可能達到 20-100ms  
- 根據系統負載和任務數量自動調整
- 目標延遲 (target latency) 動態變化
```

#### 誤解三：「實時任務優先級」
```
❌ 錯誤理解: CFS 處理所有任務包括實時任務
✅ 正確理解: 實時任務使用不同的調度器

Linux 調度器層次:
1. RT 調度器 (SCHED_FIFO, SCHED_RR) - 最高優先級
2. Deadline 調度器 (SCHED_DEADLINE) - 截止期限保證
3. CFS 調度器 (SCHED_NORMAL) - 一般任務
4. Idle 調度器 (SCHED_IDLE) - 空閒任務

只有沒有實時任務時，CFS 才開始工作
```

### CFS 性能調優參數

#### 重要的 sysctl 參數
```bash
# 查看 CFS 參數
sysctl kernel.sched_migration_cost    # 遷移成本閾值
sysctl kernel.sched_min_granularity   # 最小運行時間
sysctl kernel.sched_latency           # 目標延遲
sysctl kernel.sched_wakeup_granularity # 喚醒粒度

# 調整範例
echo 500000 > /proc/sys/kernel/sched_latency        # 減少延遲
echo 100000 > /proc/sys/kernel/sched_min_granularity # 減少最小粒度

效果:
- 較小的延遲：更好的互動性，但更多切換開銷
- 較大的延遲：較少切換開銷，但較差的響應性
```

#### 任務優先級調整工具
```bash
# 調整執行中程式的 Nice 值
renice -10 -p PID              # 提高優先級 (需要權限)
renice 19 -p PID               # 降低優先級

# 啟動時設定 Nice 值  
nice -n -10 ./important_task   # 高優先級啟動
nice -n 19 ./background_task   # 低優先級啟動

# 使用 chrt 調整調度策略
chrt -f 50 ./realtime_task     # 設為實時任務 (FIFO)
chrt -r 50 ./realtime_task     # 設為實時任務 (RR)
chrt -o 0 ./normal_task        # 設為一般任務 (CFS)
```

### CFS 除錯與監控

#### 查看調度統計
```bash
# 查看系統負載
uptime                         # 平均負載
cat /proc/loadavg             # 詳細負載資訊

# 查看調度統計
cat /proc/sched_debug         # 詳細調度資訊
cat /proc/PID/sched           # 特定任務調度資訊

# 即時監控
htop                          # 互動式監控
top -H                        # 顯示線程資訊
pidstat -t 1                  # 每秒統計
```

#### perf 工具分析調度
```bash
# 記錄調度事件
perf record -e sched:sched_switch -a sleep 10
perf report                    # 分析調度模式

# 即時監控調度
perf top -e sched:sched_switch # 即時調度切換監控
perf sched record -- sleep 10  # 記錄調度活動
perf sched latency             # 分析調度延遲
```

記住這個關鍵差異，就能理解為什麼很多系統行為看起來與直覺不符 - 因為我們習慣用 user space 的概念思考，但實際執行是在 kernel space 的邏輯下進行的。
