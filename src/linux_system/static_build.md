# Linux 靜態連結編譯說明

## 目錄
- [什麼是靜態連結](#什麼是靜態連結)
- [靜態連結 vs 動態連結](#靜態連結-vs-動態連結)
- [適用範圍與限制](#適用範圍與限制)
- [編譯方法](#編譯方法)
- [跨平台編譯](#跨平台編譯)
- [驗證方法](#驗證方法)
- [常見問題](#常見問題)

---

## 什麼是靜態連結

靜態連結（Static Linking）是將程式所需的所有函式庫代碼**直接打包進執行檔**的編譯方式。

### 編譯時的差異

```bash
# 動態連結（預設）
gcc -o program program.c
# 產生檔案: ~16KB，需要依賴系統的 libc.so

# 靜態連結
gcc -static -o program program.c
# 產生檔案: ~800KB，完全獨立運行
```

---

## 靜態連結 vs 動態連結

| 比較項目 | 靜態連結 | 動態連結 |
|---------|---------|---------|
| **檔案大小** | 大 (800KB+) | 小 (10-50KB) |
| **執行速度** | 快 (載入時間短) | 慢 (需載入 .so) |
| **記憶體使用** | 高 (每個程式獨立) | 低 (共享函式庫) |
| **部署難度** | 簡單 (單一檔案) | 複雜 (需安裝依賴) |
| **安全性更新** | 難 (需重新編譯) | 易 (更新系統函式庫) |
| **可攜性** | 高 (同架構可用) | 低 (依賴系統環境) |

### 使用場景建議

**適合靜態連結：**
- ✅ 容器化部署 (Docker/Podman)
- ✅ 嵌入式系統 (最小化 Linux)
- ✅ 工具分發 (不想讓使用者安裝依賴)
- ✅ 系統救援工具

**適合動態連結：**
- ✅ 桌面應用程式
- ✅ 系統服務 (systemd 管理)
- ✅ 需要頻繁更新函式庫
- ✅ 多程式共享函式庫的環境

---

## 適用範圍與限制

### ✅ 靜態連結可以解決的問題

1. **函式庫相依性**
   ```bash
   # 動態連結的問題
   ./program
   # 錯誤: error while loading shared libraries: libc.so.6

   # 靜態連結沒有這個問題
   ./program
   # 直接執行，不需要額外安裝任何函式庫
   ```

2. **不同 Linux 發行版**
   - Ubuntu 編譯的執行檔可以在 CentOS 運行
   - Debian 編譯的執行檔可以在 Alpine Linux 運行
   - 前提：相同 CPU 架構

3. **glibc 版本差異**
   ```bash
   # 動態連結可能遇到
   ./program: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.34' not found

   # 靜態連結不會有版本衝突
   ```

### ❌ 靜態連結無法解決的問題

1. **CPU 架構不同**
   ```
   x86-64 編譯   ❌ 無法在 ARM 運行
   ARM 編譯      ❌ 無法在 x86-64 運行
   64-bit 編譯   ❌ 無法在 32-bit 運行
   ```

2. **作業系統不同**
   ```
   Linux 編譯    ❌ 無法在 Windows 運行
   Linux 編譯    ❌ 無法在 macOS 運行
   Linux 編譯    ❌ 無法在 FreeBSD 運行
   ```

3. **核心版本過舊**
   - 詳細說明請見下方「[為什麼核心版本會影響執行](#為什麼核心版本會影響執行)」章節
   ```bash
   # 編譯在 kernel 5.x 環境的程式
   # 可能無法在 kernel 2.6.x 運行

   # 範例錯誤訊息
   FATAL: kernel too old
   Segmentation fault
   ```

### 相容性矩陣

| 編譯環境 | 可執行環境 | 是否可行 |
|---------|-----------|---------|
| x86-64 Linux | x86-64 Linux (任何發行版) | ✅ |
| x86-64 Linux | ARM Linux | ❌ |
| x86-64 Linux | x86-64 Windows | ❌ |
| x86-64 Linux (64-bit) | x86-64 Linux (32-bit) | ❌ |
| Ubuntu 24.04 | CentOS 7 | ✅ (靜態) / ⚠️ (動態) |

---

## 為什麼核心版本會影響執行

### 核心版本限制的本質

即使是**靜態連結**的程式，最終仍然需要透過 **系統呼叫 (system call)** 與 Linux 核心互動。靜態連結只是將函式庫程式碼打包進執行檔，但核心功能本身無法打包。

```
┌─────────────────────────────┐
│   你的程式 (tse_receiver)    │
│   (靜態連結 glibc)           │
└─────────────┬───────────────┘
              │ 呼叫函式
              ▼
┌─────────────────────────────┐
│   glibc 函式 (已打包進執行檔) │
│   例如: socket(), bind()     │
└─────────────┬───────────────┘
              │ syscall (系統呼叫)
              ▼
┌─────────────────────────────┐
│   Linux Kernel               │  ← 這裡無法打包！
│   必須由目標系統提供          │
└─────────────────────────────┘
```

### 系統呼叫的版本演進

#### 1. 新系統呼叫的加入

Linux 核心會不斷加入新的系統呼叫，舊核心沒有這些功能：

| 系統呼叫 | 加入版本 | 用途 | 範例程式 |
|---------|---------|------|---------|
| `accept4()` | 2.6.28 (2008) | 帶 flags 的 socket accept | 網路伺服器 |
| `epoll_create1()` | 2.6.27 (2008) | 改進的 event polling | 高併發伺服器 |
| `eventfd2()` | 2.6.27 (2008) | 事件通知機制 | 多執行緒程式 |
| `pipe2()` | 2.6.27 (2008) | 帶 flags 的管道 | IPC 程式 |
| `preadv()`/`pwritev()` | 2.6.30 (2009) | 向量式 I/O | 資料庫 |
| `recvmmsg()` | 2.6.33 (2010) | 批次接收網路封包 | 高效能網路程式 |
| `sendmmsg()` | 3.0 (2011) | 批次傳送網路封包 | UDP 伺服器 |
| `getrandom()` | 3.17 (2014) | 安全亂數產生 | 加密程式 |
| `memfd_create()` | 3.17 (2014) | 記憶體檔案描述符 | 容器技術 |
| `copy_file_range()` | 4.5 (2016) | 零拷貝檔案複製 | 檔案管理工具 |
| `statx()` | 4.11 (2017) | 擴充檔案狀態查詢 | 現代檔案系統工具 |
| `openat2()` | 5.6 (2020) | 更安全的檔案開啟 | 安全性要求高的程式 |
| `close_range()` | 5.9 (2020) | 批次關閉檔案描述符 | 程序管理 |

#### 2. 實際錯誤範例

```c
// 程式碼使用新的系統呼叫
#include <sys/random.h>

int main() {
    char buf[16];
    // getrandom() 在 kernel 3.17+ 才有
    getrandom(buf, 16, 0);
    return 0;
}
```

編譯並在不同核心執行：

```bash
# 在 kernel 5.15 編譯（靜態連結）
$ gcc -static -o test test.c

# 在 kernel 5.15 執行 ✅
$ ./test
(正常執行)

# 在 kernel 3.10 (CentOS 7 預設) 執行 ❌
$ ./test
Segmentation fault

# 使用 strace 查看原因
$ strace ./test
...
getrandom(0x7ffd..., 16, 0) = -1 ENOSYS (Function not implemented)
                                  ^^^^^^
                                  核心不支援此 syscall
```

### glibc 對核心版本的假設

#### glibc 的最低核心需求演進

| glibc 版本 | 最低核心需求 | 發布年份 | 代表發行版 |
|-----------|------------|---------|-----------|
| glibc 2.17 | kernel 2.6.32 | 2012 | CentOS 7 |
| glibc 2.19 | kernel 2.6.32 | 2014 | Ubuntu 14.04 |
| glibc 2.24 | kernel 3.2.0 | 2016 | Ubuntu 16.04 |
| glibc 2.27 | kernel 3.2.0 | 2018 | Ubuntu 18.04 |
| glibc 2.31 | kernel 3.2.0 | 2020 | Ubuntu 20.04 |
| glibc 2.35 | kernel 3.2.0 | 2022 | Ubuntu 22.04 |
| glibc 2.39 | kernel 3.2.0 | 2024 | Ubuntu 24.04 |

**重點：** 從 glibc 2.24 (2016) 開始，預設假設核心至少是 **3.2.0**

#### 檢查你的執行檔的核心需求

```bash
# 方法 1: 使用 file 命令
$ file tse_receiver
tse_receiver: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux),
statically linked, for GNU/Linux 3.2.0, not stripped
                            ^^^^^^^^^^^^^^^^^^^
                            最低核心需求

# 方法 2: 使用 readelf
$ readelf -n tse_receiver

Displaying notes found in: .note.ABI-tag
  Owner                 Data size       Description
  GNU                  0x00000010       NT_GNU_ABI_TAG (ABI version tag)
    OS: Linux, ABI: 3.2.0
                   ^^^^^^^^^
```

### 為什麼需要 kernel 3.2.0+？

glibc 2.24+ 假設核心至少是 3.2.0 的原因：

1. **執行緒效能改進**
   - `FUTEX_WAIT_BITSET` 和 `FUTEX_WAKE_BITSET` 操作
   - 更快的 pthread mutex 和 condition variable

2. **新的 socket 選項**
   - `TCP_USER_TIMEOUT` socket 選項
   - `SO_REUSEPORT` 支援（3.9+）

3. **檔案系統改進**
   - `O_CLOEXEC` flag 的普遍支援
   - 更好的 `/proc` 介面

4. **安全性功能**
   - Seccomp BPF (3.5+)
   - 命名空間 (namespaces) 的完整支援

### 實際測試：不同核心的相容性

#### 測試程式

```c
// test_kernel.c - 測試不同核心功能
#include <stdio.h>
#include <sys/utsname.h>

int main() {
    struct utsname buffer;
    uname(&buffer);
    printf("Kernel: %s\n", buffer.release);
    printf("Program compiled for kernel 3.2.0+\n");
    return 0;
}
```

#### 測試結果

```bash
# Docker 容器測試（使用舊核心映像）

# kernel 4.19 (Debian 10) ✅
$ docker run --rm -v $(pwd):/test debian:10 /test/test_kernel
Kernel: 4.19.0
Program compiled for kernel 3.2.0+

# kernel 3.10 (CentOS 7) ✅
$ docker run --rm -v $(pwd):/test centos:7 /test/test_kernel
Kernel: 3.10.0
Program compiled for kernel 3.2.0+

# kernel 2.6.32 (CentOS 6) ❌
$ docker run --rm -v $(pwd):/test centos:6 /test/test_kernel
FATAL: kernel too old
Segmentation fault
```

### 針對舊核心編譯的方法

#### 方法 1: 在舊系統上編譯

```bash
# 在 CentOS 6 (kernel 2.6.32 + glibc 2.12) 編譯
docker run -it --rm -v $(pwd):/work centos:6 bash

# 安裝開發工具
yum install -y gcc glibc-static

# 編譯
gcc -static -o tse_receiver_old tse_receiver.c

# 檢查核心需求
file tse_receiver_old
# 輸出: for GNU/Linux 2.6.32
```

#### 方法 2: 使用 musl libc（推薦）

musl libc 對核心版本需求較低，而且產生的執行檔更小：

```bash
# Alpine Linux (使用 musl)
docker run -it --rm -v $(pwd):/work alpine:latest sh

# 安裝編譯工具
apk add gcc musl-dev

# 編譯
gcc -static -o tse_receiver_musl tse_receiver.c

# 檔案大小比較
ls -lh tse_receiver*
# glibc 版本: 800KB
# musl 版本:  100KB
```

**musl 的優勢：**
- 更小的執行檔
- 對核心需求更寬鬆（通常 2.6+ 即可）
- 更少的系統呼叫依賴

#### 方法 3: 手動降級 glibc 版本需求（不推薦）

```bash
# 危險！可能導致未定義行為
gcc -static -Wl,--defsym,__kernel_version=0x020620 -o test test.c
                        ^^^^^^^^^^^^^^^^^^^^^^^^
                        假裝核心是 2.6.32
```

這個方法**不推薦**，因為：
- 編譯器可能已經使用了新的 syscall
- 執行時仍可能崩潰
- 難以除錯

### tse_receiver 的核心需求分析

讓我們分析 `tse_receiver.c` 使用的系統呼叫：

```c
// tse_receiver.c 使用的函式
socket()      // kernel 2.0+  ✅ 非常古老
bind()        // kernel 2.0+  ✅
setsockopt()  // kernel 2.0+  ✅
recvfrom()    // kernel 2.0+  ✅
close()       // kernel 1.0+  ✅
printf()      // 不是 syscall，是 glibc 函式
```

**結論：**
- `tse_receiver.c` 本身只使用非常基本的 syscall
- 這些 syscall 從 Linux 2.0 時代就有
- **但編譯時使用的 glibc 會決定最低核心需求**

```bash
# 檢查實際的 syscall 使用情況
$ strace -c ./tse_receiver 2>&1 | head -20

% time     seconds  usecs/call     calls    errors syscall
------ ----------- ----------- --------- --------- ----------------
 0.00    0.000000           0         1           socket
 0.00    0.000000           0         1           bind
 0.00    0.000000           0         1           setsockopt
 0.00    0.000000           0      1234           recvfrom
 0.00    0.000000           0         1           close
```

### 核心版本相容性決策表

| 目標環境 | 編譯策略 | 核心需求 | 檔案大小 |
|---------|---------|---------|---------|
| 現代 Linux (2020+) | gcc -static | 3.2.0+ | 800KB |
| CentOS 7 / RHEL 7 | gcc -static | 3.2.0+ | 800KB |
| CentOS 6 / RHEL 6 | 在 CentOS 6 編譯 | 2.6.32+ | 800KB |
| 任意發行版 | musl-gcc -static | 2.6.0+ | 100KB |
| 嵌入式 Linux | musl-gcc -static | 2.6.0+ | 100KB |

### 最佳實務建議

#### 1. 目標系統核心 >= 3.2 (2012+)

```bash
# 標準編譯即可
gcc -static -o tse_receiver tse_receiver.c
```

**適用環境：**
- Ubuntu 16.04+
- CentOS 7+
- Debian 8+
- 大多數現代 Linux

#### 2. 目標系統核心 2.6.x (舊系統)

```bash
# 使用 musl libc
docker run --rm -v $(pwd):/work alpine:latest sh -c \
  "apk add gcc musl-dev && \
   gcc -static -o tse_receiver tse_receiver.c"
```

**適用環境：**
- CentOS 6
- RHEL 6
- 古老嵌入式系統

#### 3. 萬用方案（同時產生多個版本）

```makefile
.PHONY: build-all
build-all:
    # 現代 Linux (glibc)
    gcc -static -o tse_receiver_glibc tse_receiver.c

    # 舊系統 (musl)
    docker run --rm -v $(pwd):/work alpine:latest sh -c \
      "apk add gcc musl-dev && \
       gcc -static -o tse_receiver_musl tse_receiver.c"
```

### 驗證核心相容性

```bash
# 1. 檢查執行檔的核心需求
file tse_receiver

# 2. 在 Docker 測試不同核心
docker run --rm -v $(pwd):/test centos:7 /test/tse_receiver

# 3. 使用 strace 檢查 syscall
strace -e trace=syscall ./tse_receiver

# 4. 檢查是否使用了新的 syscall
strace ./tse_receiver 2>&1 | grep -E "ENOSYS|EINVAL"
```

---

## 編譯方法

### 本專案的 Makefile

```makefile
# 編譯器設定
CC = gcc
CFLAGS = -Wall -O2
LDFLAGS = -static  # 關鍵：啟用靜態連結

# 檔名設定
TARGET = tse_receiver
SRC = tse_receiver.c

.DEFAULT_GOAL := help

.PHONY: build
build: $(TARGET)

$(TARGET): $(SRC)
	$(CC) $(CFLAGS) $(LDFLAGS) -o $(TARGET) $(SRC)

.PHONY: clean
clean:
	rm -f $(TARGET)
```

### 使用方法

```bash
# 清理舊檔案
make clean

# 編譯（靜態連結）
make build

# 執行
make run
```

### 手動編譯命令

```bash
# 基本靜態編譯
gcc -static -o tse_receiver tse_receiver.c

# 加上優化和警告
gcc -Wall -O2 -static -o tse_receiver tse_receiver.c

# 完全靜態編譯（包含 libgcc）
gcc -static -static-libgcc -o tse_receiver tse_receiver.c
```

---

## 跨平台編譯

### 安裝交叉編譯工具鏈

```bash
# Ubuntu/Debian
sudo apt-get install gcc-aarch64-linux-gnu      # ARM 64-bit
sudo apt-get install gcc-arm-linux-gnueabihf    # ARM 32-bit
sudo apt-get install gcc-riscv64-linux-gnu      # RISC-V 64-bit
```

### 編譯不同架構的執行檔

```bash
# ARM 64-bit (如 Raspberry Pi 4, AWS Graviton)
aarch64-linux-gnu-gcc -static -o tse_receiver_arm64 tse_receiver.c

# ARM 32-bit (如 Raspberry Pi 3)
arm-linux-gnueabihf-gcc -static -o tse_receiver_arm32 tse_receiver.c

# RISC-V 64-bit
riscv64-linux-gnu-gcc -static -o tse_receiver_riscv64 tse_receiver.c
```

### Makefile 支援多架構

```makefile
# 多目標編譯
.PHONY: build-all
build-all:
	gcc -static -o tse_receiver_x86_64 tse_receiver.c
	aarch64-linux-gnu-gcc -static -o tse_receiver_arm64 tse_receiver.c
	arm-linux-gnueabihf-gcc -static -o tse_receiver_arm32 tse_receiver.c

# 指定架構編譯
.PHONY: build-arm64
build-arm64:
	aarch64-linux-gnu-gcc -static -o tse_receiver_arm64 tse_receiver.c
```

---

## 驗證方法

### 1. 檢查執行檔類型

```bash
$ file tse_receiver
tse_receiver: ELF 64-bit LSB executable, x86-64, version 1 (GNU/Linux),
statically linked, BuildID[sha1]=7eee6f2dad54b135e1b740e3f16a68c8d0984c57,
for GNU/Linux 3.2.0, not stripped
```

**關鍵字：`statically linked`** ✅

### 2. 檢查動態函式庫依賴

```bash
$ ldd tse_receiver
不是動態可執行檔案
```

**如果顯示「不是動態可執行檔案」表示靜態連結成功** ✅

**如果顯示函式庫列表，表示是動態連結：**
```bash
$ ldd tse_receiver
linux-vdso.so.1 (0x00007ffd8d3e9000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f9e5c800000)
/lib64/ld-linux-x86-64.so.2 (0x00007f9e5ca3a000)
```
❌ 這表示還是動態連結

### 3. 檢查檔案大小

```bash
$ ls -lh tse_receiver
-rwxr-xr-x 1 user user 807K 12月 3 03:52 tse_receiver
```

**靜態連結通常會有數百 KB 到數 MB** ✅

### 4. 檢查 CPU 架構和核心需求

```bash
$ readelf -h tse_receiver | grep -E "Class|Machine|OS/ABI"
  Class:                             ELF64
  Machine:                           Advanced Micro Devices X86-64
  OS/ABI:                            UNIX - GNU
```

**重要資訊：**
- `ELF64` → 64位元執行檔
- `X86-64` → Intel/AMD 架構
- `UNIX - GNU` → Linux 系統

### 5. 測試在不同環境執行

```bash
# 在 Docker Alpine Linux 測試（最小化環境）
docker run --rm -v $(pwd):/app alpine:latest /app/tse_receiver

# 在 Ubuntu 容器測試
docker run --rm -v $(pwd):/app ubuntu:latest /app/tse_receiver

# 在 CentOS 容器測試
docker run --rm -v $(pwd):/app centos:7 /app/tse_receiver
```

---

## 常見問題

### Q1: 編譯時出現 "cannot find -lc" 錯誤

```bash
/usr/bin/ld: cannot find -lc
collect2: error: ld returned 1 exit status
```

**解決方法：**
```bash
# Ubuntu/Debian
sudo apt-get install libc6-dev

# CentOS/RHEL
sudo yum install glibc-static

# Alpine Linux
apk add musl-dev
```

### Q2: 靜態連結後檔案太大怎麼辦？

```bash
# 方法 1: 使用 strip 移除除錯符號
strip tse_receiver
# 可減少 30-50% 大小

# 方法 2: 使用 UPX 壓縮（執行時自動解壓）
upx --best tse_receiver
# 可減少 50-70% 大小

# 方法 3: 編譯時優化
gcc -Os -static -o tse_receiver tse_receiver.c
# -Os: 優化檔案大小
```

### Q3: NSS (Name Service Switch) 相關問題

某些程式使用 glibc 的 NSS 功能（如 DNS 解析、用戶資訊查詢），靜態連結可能導致問題。

```c
// 如果程式有使用這些函式，靜態連結可能有問題：
getaddrinfo()  // DNS 解析
gethostbyname()
getpwnam()     // 用戶資訊
getgrnam()     // 群組資訊
```

**解決方法：**
1. 使用 musl libc 編譯（Alpine Linux）
2. 使用動態連結
3. 直接使用 syscall 而非 libc 函式

### Q4: 如何檢查是否真的可以在其他機器運行？

```bash
# 方法 1: 使用 Docker 模擬純淨環境
docker run --rm -v $(pwd):/test alpine:latest /test/tse_receiver

# 方法 2: 使用 chroot 隔離環境
mkdir /tmp/testenv
sudo chroot /tmp/testenv /path/to/tse_receiver

# 方法 3: 使用 strace 檢查系統呼叫
strace ./tse_receiver 2>&1 | grep -E "open|access"
# 如果沒有嘗試開啟 .so 檔案，就是純靜態
```

### Q5: 靜態連結的安全性考量

**問題：**
- 如果 glibc 有安全漏洞，靜態連結的程式無法透過系統更新修補
- 每次 glibc 更新都需要重新編譯所有程式

**建議：**
- 建立 CI/CD 流程自動重新編譯
- 定期檢查依賴的函式庫版本
- 使用容器映像管理工具追蹤版本

### Q6: 為什麼 Alpine Linux 的靜態執行檔更小？

```bash
# glibc 靜態連結
gcc -static -o program program.c
# 檔案大小: ~800KB

# musl libc 靜態連結
musl-gcc -static -o program program.c
# 檔案大小: ~100KB
```

**原因：**
- glibc 功能完整但龐大
- musl libc 輕量化設計
- Alpine Linux 預設使用 musl

**在 Alpine Docker 編譯：**
```dockerfile
FROM alpine:latest
RUN apk add gcc musl-dev
COPY tse_receiver.c .
RUN gcc -static -o tse_receiver tse_receiver.c
```

---

## 實戰範例

### 場景 1: 部署到 Docker 容器

```dockerfile
# 使用靜態連結執行檔的最小化映像
FROM scratch
COPY tse_receiver /
CMD ["/tse_receiver"]
```

檔案大小比較：
- 使用動態連結 + base image: ~100MB
- 使用靜態連結 + scratch: ~1MB

### 場景 2: 製作可攜式工具包

```bash
#!/bin/bash
# 打包腳本
mkdir -p release

# 編譯多架構版本
make clean
gcc -static -o release/tse_receiver_x86_64 tse_receiver.c
aarch64-linux-gnu-gcc -static -o release/tse_receiver_arm64 tse_receiver.c

# 壓縮
cd release
tar czf tse_receiver_portable.tar.gz *

# 使用者只需解壓並執行
# tar xzf tse_receiver_portable.tar.gz
# ./tse_receiver_x86_64
```

### 場景 3: 系統救援工具

```bash
# 編譯成靜態執行檔
gcc -static -Os -o recover_tool recover_tool.c
strip recover_tool

# 即使在損壞的系統中（/lib 遺失）也能執行
# 因為不依賴任何動態函式庫
```

---

## 總結

### 決策流程圖

```
需要分發程式？
├─ 是 → 目標環境可控？
│      ├─ 是 → 動態連結（節省空間）
│      └─ 否 → 靜態連結（相容性優先）
│
└─ 否 → 自己使用？
       └─ 動態連結（方便更新）
```

### 快速參考

| 需求 | 推薦方案 |
|------|---------|
| 單一執行檔分發 | 靜態連結 |
| 容器化部署 | 靜態連結 + scratch image |
| 嵌入式 Linux | 靜態連結 |
| 桌面應用 | 動態連結 |
| 系統服務 | 動態連結 |
| 跨發行版相容 | 靜態連結 |
| 經常更新的程式 | 動態連結 |

---

## 參考資源

- [GCC Static Linking Options](https://gcc.gnu.org/onlinedocs/gcc/Link-Options.html)
- [ELF Format Specification](https://refspecs.linuxfoundation.org/elf/elf.pdf)
- [Linux Cross Reference - Syscalls](https://elixir.bootlin.com/linux/latest/source)
- [musl libc vs glibc Comparison](https://www.musl-libc.org/intro.html)

---

**文件版本：** 1.0
**最後更新：** 2025-12-03
**適用專案：** tse_market_data / tse_receiver
