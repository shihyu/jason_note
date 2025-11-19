# 讀書心得: 操作系統原型 - xv6 分析與實踐

## 概述

本文基於《操作系統原型 - xv6 分析與實踐》一書的學習筆記。

xv6 是 MIT 開發的一個教學操作系統，是 Unix Version 6 的重新實現，設計用於在 x86 多處理器系統上運行，使用 ANSI C 語言編寫。

---

## 第 0 章：本文閱讀指南

推薦兩種閱讀路徑：

### 實踐派
1. 從第 1 章開始安裝並進行實際操作
2. 通過動手實驗理解操作系統的工作原理
3. 在實踐中逐漸深化理論理解

### 理論先行派
1. 先從附錄 A & B 開始，理解核心原理
2. 了解 x86 硬體基礎和 xv6 啟動流程
3. 再進行實驗和驗證

---

## 第 1 章：xv6 安裝與配置

### 什麼是 xv6？

- **重新實現**：Unix Version 6（v6）的現代化實現
- **教學目的**：設計用於操作系統課程教學
- **硬體平台**：x86 單處理器或多處理器系統
- **開發語言**：ANSI C 和 x86 彙編語言
- **許可證**：MIT License

### 安裝步驟

```bash
# 1. 下載 xv6 源代碼
wget https://github.com/mit-pdos/xv6-public/archive/refs/tags/xv6-rev9.tar.gz

# 2. 解壓文件
tar -xvf xv6-rev9.tar.gz

# 3. 進入目錄
cd xv6-public-xv6-rev9

# 4. 編譯內核
make

# 5. 在 QEMU 中運行（非圖形界面）
make qemu-nox
```

### 退出命令

- **QEMU (nox mode)**：按 `Ctrl+A` 再按 `X` 退出
- **GDB 調試器**：按 `Ctrl+D` 退出

### 依賴環境

確保已安裝：
- GCC 編譯工具
- Make 構建工具
- QEMU 虛擬機
- GDB 調試器（可選）

---

## 第 2 章：xv6 實驗

### 2.1 實驗 1-0：修改啟動信息

**目標**：自定義 xv6 的啟動消息

**步驟**：
1. 定位 `main.c` 文件中的 `mpmain()` 函數
2. 修改啟動時輸出的問候信息
3. 重新編譯並在 QEMU 中運行驗證

**代碼位置**：`main.c` - `mpmain()` 函數

### 2.2 實驗 1-1：添加用戶應用程序

**目標**：創建並編譯一個用戶態應用程序

**步驟**：
1. 在 xv6 根目錄創建 `my-app.c`
2. 在 `Makefile` 中添加 `_my-app` 到 `UPROGS` 列表
3. 運行 `make` 編譯
4. 在 xv6 shell 中運行應用程序

**示例代碼**：
```c
#include "types.h"
#include "stat.h"
#include "user.h"
#include "fcntl.h"

int
main(int argc, char *argv[])
{
    printf(1, "Hello from my-app!\n");
    exit();
}
```

### 2.3 實驗 1-2：添加系統調用

**目標**：實現一個新的系統調用（如 `getcpuid()`）

**涉及文件修改**：

#### 1. `syscall.h` - 定義系統調用號
```c
#define SYS_getcpuid  24
```

#### 2. `user.h` - 聲明用戶函數
```c
int getcpuid(void);
```

#### 3. `usys.S` - 用戶態系統調用入口
使用 `SYSCALL` 宏生成系統調用代碼：
```asm
SYSCALL(getcpuid)
```

#### 4. `syscall.c` - 註冊系統調用
```c
extern int sys_getcpuid(void);

// 在 syscalls[] 數組中添加
[SYS_getcpuid] sys_getcpuid,
```

#### 5. `sysproc.c` - 實現系統調用
```c
int
sys_getcpuid(void)
{
    return cpuid();
}
```

#### 6. `defs.h` - 導出函數聲明
```c
int     cpuid(void);
```

#### 7. `proc.c` - 實現核心功能
```c
int
cpuid(void)
{
    return 0;  // 簡單實現
}
```

**驗證步驟**：
1. 創建用戶應用調用 `getcpuid()`
2. 編譯並運行
3. 使用 GDB 追蹤系統調用流程

---

## 第 3 章：核心概念

### 3.1 文件描述符

xv6 中的標準文件描述符：

| 文件描述符 | 名稱 | 用途 |
|-----------|------|------|
| 0 | stdin | 標準輸入 |
| 1 | stdout | 標準輸出 |
| 2 | stderr | 標準錯誤輸出 |

### 3.2 引導過程（Bootstrap Sequence）

系統啟動時的執行順序：

```
1. BIOS 加載啟動塊 (bootblock)
   ↓
2. bootblock (512 bytes) 被加載到內存地址 0x7c00
   ↓
3. bootasm.S 切換 CPU 模式
   - 從實模式 → 32 位保護模式
   ↓
4. bootmain.c 從磁盤讀取內核 ELF 映像
   - 從磁盤扇區 1 開始讀取
   - 加載到內存
   ↓
5. entry.S 啟用分頁機制
   - 設置頁表
   - 開啟虛擬內存
   ↓
6. main.c 初始化內核子系統
   - 初始化 CPU、內存、中斷等
```

### 3.3 啟動加載器詳解

#### 啟動塊特性
- **大小**：精確 512 字節（一個磁盤扇區）
- **位置**：磁盤第一個扇區（LBA 0）
- **加載地址**：0x7c00（BIOS 約定）
- **類型**：機器碼（二進制可執行）

#### 內核加載
- **起始扇區**：扇區 1
- **加載方式**：使用 BIOS INT 0x13 中斷
- **映像格式**：ELF 格式

#### 內存佈局演變

**實模式（Real Mode）**
```
0x00000000 +--------+
           | BIOS   |
0x000F0000 +--------+
           | ...    |
0x00007C00 +--------+ ← 啟動塊加載位置
           | ...    |
0x00000000 +--------+
```

**保護模式初期（Protected Mode Init）**
```
0x00100000 +--------+ ← 內核開始位置（1MB）
           | Kernel |
           |        |
0x00080000 +--------+ ← 啟動代碼區
           |        |
0x00000000 +--------+
```

### 3.4 全局描述符表（GDT）

GDT 為保護模式設置段描述符，配置包括：

#### 段結構
```
+--------+--------+--------+--------+
| 段基址 | 段限制 | 訪問權限 | 其他 |
+--------+--------+--------+--------+
```

#### 預定義段
1. **NULL 段**（段選擇子 0x00）
   - 防止錯誤使用

2. **代碼段**（段選擇子 0x08）
   - **類型**：可執行、可讀
   - **特權級**：Ring 0（內核）
   - **粒度**：4KB 頁面

3. **數據段**（段選擇子 0x10）
   - **類型**：可寫
   - **特權級**：Ring 0（內核）
   - **粒度**：4KB 頁面

#### GDT 初始化代碼位置
- **文件**：`bootasm.S`
- **作用**：切換到保護模式前設置

### 3.5 x86 處理器工作模式

![x86 Operating Modes Comparison](images/x86-operating-modes.jpg)

| 模式 | 位寬 | 尋址範圍 | 保護機制 | 用途 |
|------|------|---------|---------|------|
| 實模式 | 16 位 | 1MB | 無 | BIOS、DOS |
| 保護模式 | 32 位 | 4GB | 段、分頁 | xv6 內核 |
| 長模式（64位） | 64 位 | 16EB | 分頁 | 現代 OS |

### 3.6 段描述符格式

![Segment Descriptor Format Diagram](images/segment-descriptor-format.gif)

**段描述符包含**：
- **基地址 (Base Address)**：段在線性地址空間中的起始地址
- **段限制 (Limit)**：段的大小
  - 以字節為單位（粒度 = 1）
  - 或以 4KB 頁為單位（粒度 = 4KB）
- **訪問權限 (Type/S/DPL/P)**：
  - Type：段類型（代碼或數據）
  - S：描述符類型（系統或非系統）
  - DPL：特權級別（0-3）
  - P：段存在位

---

## 第 4 章：引導程序詳解

### 4.1 bootasm.S - 彙編啟動代碼

**主要責任**：
1. 禁用中斷和清除寄存器
2. 初始化 GDT（全局描述符表）
3. 從實模式切換到 32 位保護模式
4. 跳轉到 bootmain.c 的 C 代碼

**關鍵步驟**：

```asm
# 1. 禁用中斷
cli

# 2. 清除全局描述符表
lgdt gdtdesc

# 3. 啟用保護模式位
mov %cr0, %eax
orl $CR0_PE, %eax
mov %eax, %cr0

# 4. 長跳轉到 32 位代碼段
ljmp $SEG_KCODE, $start32
```

### 4.2 bootmain.c - C 語言啟動代碼

**功能**：
1. 從磁盤讀取內核 ELF 映像
2. 將每個程序段加載到指定的物理內存地址
3. 跳轉到內核入口點

**ELF 加載流程**：
```c
void
bootmain(void)
{
    struct elfhdr *elf;
    struct proghdr *ph, *eph;
    void (*entry)(void);
    uchar* pa;

    // 從磁盤扇區 1 讀取第一個頁面（4KB）
    readseg((uchar*)0x10000, 4096, 0);
    
    // 查找 ELF 頭
    elf = (struct elfhdr*)0x10000;
    
    // 檢查 ELF 魔數
    if(elf->magic != ELF_MAGIC)
        return;  // 無效 ELF
    
    // 加載每個程序段
    ph = (struct proghdr*)((uchar*)elf + elf->phoff);
    eph = ph + elf->phnum;
    
    for(; ph < eph; ph++){
        pa = (uchar*)ph->paddr;
        readseg(pa, ph->filesz, ph->offset);
        
        // 初始化 BSS 段（未初始化數據）
        if(ph->memsz > ph->filesz)
            stosb(pa + ph->filesz, 0, ph->memsz - ph->filesz);
    }
    
    // 跳轉到內核入口點
    entry = (void(*)(void))(elf->entry);
    entry();
}
```

### 4.3 entry.S - 內核入口

**主要功能**：
1. 設置頁表
2. 啟用分頁
3. 跳轉到 main()

---

## 第 5 章：內存管理

### 5.1 虛擬內存架構

xv6 使用分頁實現虛擬內存：

```
應用程序虛擬地址空間
0xFFFFFFFF +----------+ ← 內核空間
           |          |
           | Kernel   |
           |          |
0x80000000 +----------+ ← 0.5GB - 用戶/內核邊界
           |          |
           | User     | ← 堆和棧
           |          |
0x00000000 +----------+
```

### 5.2 頁表結構

xv6 使用兩級頁表：
- **頁目錄（PD）**：第一級，10 位索引
- **頁表（PT）**：第二級，10 位索引
- **頁內偏移**：12 位

```
虛擬地址：[PD Index(10)|PT Index(10)|Offset(12)]
                ↓            ↓            ↓
          頁目錄表   →    頁表    →   物理頁
```

### 5.3 關鍵數據結構

#### 頁表項 (PTE)
```c
typedef uint pte_t;  // 32-bit 或 64-bit
```

**PTE 格式**：
```
[物理頁號(20)|保留(3)|標誌位(9)]
   ↓                   ↓
 頁幀號             PTE_P(存在)
                   PTE_W(可寫)
                   PTE_U(用戶)
```

#### 核心函數
```c
pte_t *walkpgdir(pde_t *pgdir, const void *va);
int mappages(pde_t *pgdir, void *va, uint size, uint pa, int perm);
void switchuvm(struct proc *p);
```

---

## 第 6 章：進程管理

### 6.1 進程數據結構

#### proc 結構體
```c
struct proc {
    uint sz;                    // 進程內存大小
    pde_t* pgdir;              // 頁目錄
    char *kstack;              // 內核棧底（用於上下文保存）
    enum procstate state;      // 進程狀態
    int pid;                   // 進程 ID
    struct proc *parent;       // 父進程
    struct trapframe *tf;      // 中斷幀（保存用戶寄存器）
    struct context *context;   // 上下文（保存內核寄存器）
    void *chan;                // 睡眠通道（條件變量）
    int killed;                // 進程是否被殺死
    struct file *ofile[NOFILE]; // 打開文件表
    struct inode *cwd;         // 當前工作目錄
    char name[16];             // 進程名稱
};
```

### 6.2 進程狀態

```
UNUSED ──→ EMBRYO ──→ RUNNABLE ──→ RUNNING
             ↑                        ↓
             └──────────────────── SLEEPING
                                     ↓
                                  ZOMBIE
```

- **UNUSED**：未使用槽位
- **EMBRYO**：新建，初始化中
- **RUNNABLE**：就緒，等待調度
- **RUNNING**：正在運行
- **SLEEPING**：等待事件
- **ZOMBIE**：已終止，等待父進程回收

### 6.3 上下文切換

#### context 結構體
```c
struct context {
    uint edi;
    uint esi;
    uint ebx;
    uint ebp;
    uint eip;
};
```

**切換流程**：
```
用戶態代碼
    ↓
[中斷/系統調用]
    ↓
中斷處理程序
    ↓
schedule() 選擇新進程
    ↓
swtch() 保存舊上下文，恢復新上下文
    ↓
新進程代碼繼續
```

---

## 第 7 章：中斷和異常

### 7.1 中斷描述符表（IDT）

類似 GDT，定義中斷和異常處理器：

```c
struct gatedesc {
    uint off_15_0;      // 低 16 位偏移
    ushort sel;         // 段選擇子
    uchar args;         // 參數個數
    uchar type;         // 門類型
    ushort off_31_16;   // 高 16 位偏移
};
```

### 7.2 系統調用實現

**流程**：
```
用戶程序
    ↓
[int $T_SYSCALL] (INT 0x80)
    ↓
alltraps() → trapasm.S 匯編入口
    ↓
trap() 中斷處理函數
    ↓
syscall() 分發系統調用
    ↓
sys_xxx() 具體系統調用實現
    ↓
返回用戶程序
```

**系統調用編號存儲位置**：
- **寄存器 eax**：系統調用號
- **其他寄存器**：系統調用參數（edi, esi, edx, ecx, ebx）

### 7.3 常見系統調用

| 系統調用 | 功能 |
|----------|------|
| fork() | 創建新進程 |
| exec() | 執行程序 |
| exit() | 進程退出 |
| wait() | 等待子進程 |
| getpid() | 獲取進程 ID |
| read() | 讀取文件 |
| write() | 寫入文件 |
| open() | 打開文件 |
| close() | 關閉文件 |

---

## 第 8 章：文件系統

### 8.1 文件系統結構

xv6 使用簡化的 Unix 文件系統：

```
+--------+--------+--------+---------+
| Boot   | Super  | Inode  | Data    |
| Block  | Block  | Block  | Blocks  |
+--------+--------+--------+---------+
```

### 8.2 I-node 結構

```c
struct dinode {
    short type;           // 文件類型（文件/目錄）
    short major, minor;   // 設備號
    uint size;           // 文件大小
    uint addrs[NDIRECT+1]; // 直接和間接塊指針
};
```

### 8.3 目錄結構

目錄是特殊的文件，包含目錄項：

```c
struct dirent {
    ushort inum;        // I-node 編號
    char name[DIRSIZ];  // 文件名
};
```

---

## 第 9 章：系統調用詳解

### 9.1 fork() - 進程創建

**作用**：創建當前進程的副本

**返回值**：
- 父進程：子進程 ID
- 子進程：0
- 錯誤：-1

**示例**：
```c
int pid = fork();
if(pid == 0) {
    // 子進程代碼
} else {
    // 父進程代碼
}
```

### 9.2 exec() - 程序執行

**作用**：用新程序替換當前進程

**語法**：
```c
exec(char *path, char *argv[]);
```

**示例**：
```c
char *args[] = {"cat", "file.txt", 0};
exec("/bin/cat", args);
```

### 9.3 exit() - 進程退出

**作用**：終止當前進程

**語法**：
```c
exit(int status);
```

### 9.4 wait() - 等待子進程

**作用**：等待子進程終止

**語法**：
```c
wait(int *status);
```

### 9.5 read() / write() - 文件 I/O

**讀取文件**：
```c
ssize_t read(int fd, void *buf, size_t count);
```

**寫入文件**：
```c
ssize_t write(int fd, const void *buf, size_t count);
```

---

## 附錄 A：源代碼位置參考

### 核心文件

| 文件 | 功能 |
|------|------|
| `bootasm.S` | 啟動彙編代碼（實→保護模式） |
| `bootmain.c` | 啟動 C 代碼（加載內核） |
| `entry.S` | 內核入口（分頁設置） |
| `main.c` | 內核主函數 |
| `proc.c` | 進程管理 |
| `vm.c` | 虛擬內存管理 |
| `trap.c` | 中斷和異常處理 |
| `syscall.c` | 系統調用分發 |
| `sysproc.c` | 進程相關系統調用 |
| `sysfile.c` | 文件相關系統調用 |
| `fs.c` | 文件系統實現 |
| `ide.c` | 磁盤驅動 |

### 用戶程序位置

用戶程序源碼位於 `user/` 目錄：

```
user/
├── shell.c      # xv6 shell
├── cat.c        # cat 命令
├── ls.c         # ls 命令
├── mkdir.c      # mkdir 命令
└── ...
```

---

## 附錄 B：xv6 啟動詳解

### 完整啟動序列

```
1. 計算機上電
   ↓
2. BIOS 執行 POST（自檢）
   ↓
3. BIOS 尋找可引導設備
   ↓
4. 加載 MBR（主引導記錄） → bootblock
   物理地址：0x7c00
   ↓
5. bootasm.S 執行
   - CPU 模式：實模式
   - 任務：
     * 禁用中斷（CLI）
     * 加載 GDT
     * 啟用保護模式（設置 CR0 的 PE 位）
     * 長跳轉到 32 位代碼段
   ↓
6. bootmain.c 執行
   - CPU 模式：保護模式（32 位）
   - 任務：
     * 初始化磁盤驅動
     * 加載 ELF 格式的內核映像
     * 解析 ELF 頭和程序段
     * 將每個段複製到指定物理地址
     * 跳轉到內核入口點
   ↓
7. entry.S 執行
   - 任務：
     * 設置臨時頁表
     * 啟用分頁（設置 CR0 的 PG 位）
     * 虛擬地址映射已生效
     * 跳轉到 main()
   ↓
8. main.c 執行（內核初始化）
   - CPU 模式：保護模式 + 分頁
   - 任務：
     * 初始化 CPU
     * 初始化內存管理
     * 初始化中斷和異常處理（IDT）
     * 初始化進程系統
     * 啟動首個用戶進程（init）
   ↓
9. init 進程啟動
   - 創建 shell 進程
   - 等待用戶命令
```

### 啟動時的內存映射

**bootblock 加載時**（實模式）：
```
0x00000000 +----------+ 
           | IVT      | (中斷向量表)
0x00007C00 +----------+ ← bootblock 加載位置
           |bootblock |
0x00007E00 +----------+
           | 空閒     |
0x00100000 +----------+ ← 內核加載位置
```

**內核運行時**（保護模式 + 分頁）：
```
虛擬地址           物理地址
0xFFFFFFFF    
          +----------+
          | 內核棧   |
0xFE000000 +----------+
          | 內核代碼 |
          | 和數據   |
0x80000000 +----------+
          | 頁表     |
0x00000000 +----------+
```

---

## 關鍵知識點

### 1. 模式轉換
- **實模式 → 保護模式**：bootasm.S
- **分頁啟用**：entry.S

### 2. 地址轉換
- **物理地址**：硬體實際使用的地址
- **線性地址**：保護模式下的地址（GDT 轉換）
- **虛擬地址**：分頁後的地址（頁表轉換）

### 3. 特權級別
- **Ring 0**：內核態（無限制）
- **Ring 3**：用戶態（受限）
- 系統調用通過中斷實現特權提升

### 4. 進程隔離
- 每個進程有獨立的虛擬地址空間
- 通過頁表實現
- 防止進程間互相干擾

---

## 實驗建議

### 初級實驗
1. ✅ 修改啟動消息
2. ✅ 添加簡單用戶程序
3. ✅ 實現簡單系統調用

### 中級實驗
1. 修改進程調度算法
2. 實現新的系統調用（如 `getcpuid()`）
3. 追蹤進程創建流程

### 高級實驗
1. 實現分層分頁
2. 添加信號機制
3. 優化內存管理
4. 實現管道機制

---

## 常見問題解答

### Q1: xv6 為什麼使用分段？
**A**：雖然 xv6 主要依賴分頁，但仍使用分段：
- 滿足 x86 硬體要求（必須有 GDT）
- 實現用戶態/內核態分離
- 提供額外的訪問控制層

### Q2: 為什麼要有 bootblock？
**A**：
- BIOS 期望在 0x7c00 找到可引導代碼
- 大小限制為 512 字節（一個扇區）
- 用於完成初始化工作並加載主內核

### Q3: xv6 如何限制進程訪問？
**A**：
- **分段**：用戶態進程只能訪問用戶段
- **分頁**：頁表中的 PTE_U 位控制用戶訪問
- **系統調用**：用戶操作必須通過內核

### Q4: 如何調試 xv6？
**A**：
```bash
# 終端 1：運行 QEMU
make qemu-gdb

# 終端 2：運行 GDB
gdb kernel
(gdb) target remote localhost:26000
(gdb) break main
(gdb) continue
```

---

## 參考資源

### 官方資源
- [xv6 公開倉庫](https://github.com/mit-pdos/xv6-public)
- [xv6 論文](https://pdos.csail.mit.edu/6.828/2018/xv6/book-rev11.pdf)
- [MIT 6.828 課程](https://pdos.csail.mit.edu/6.828/)

### 推薦閱讀
- **Lions' Commentary on UNIX 6th Edition**
- **The Design and Implementation of the 9th Edition Unix Operating System** (Pike, Ritchie)
- **Operating System Concepts** (Silberschatz, Galvin, Gagne)

### 相關圖表
- x86 架構手冊（Intel Software Developer's Manual）
- 分頁機制詳解
- GDT 和 IDT 格式規範

---

## 更新歷史

- **2023-02-27**：初版完成
- **2024-11-19**：更新補充並添加圖表

---

**筆記作者**：基於《操作系統原型 - xv6 分析與實踐》一書
**最後更新**：2024 年 11 月 19 日
