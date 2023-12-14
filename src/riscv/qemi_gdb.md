## 1 實驗目標

使用GDB在QEMU模擬器中調試運行基於64位RISCV架構的Linux內核。

## 2 實驗簡介

本次實驗將幫助我們更好地瞭解如何使用交叉編譯工具鏈編譯Linux內核源代碼，並將編譯所得到的基於RISCV指令集架構的Linux內核運行在QEMU模擬器上。本次實驗還將幫助我們更好地瞭解掌握如何利用GDB和QEMU聯合調試內核運行。

```
關鍵詞: Qemu, Kernel, Linux, OS, RISC-V, Cross Compiler Toolchain, GDB
```

## 3 實驗環境

### 3.1 實驗平臺

- Linux 發行版: [Ubuntu 20.04 LTS](http://mirrors.zju.edu.cn/ubuntu-releases/releases/20.04.2.0/ubuntu-20.04.2.0-desktop-amd64.iso)

```
$ lsb_release -a # 查看當前實驗平臺系統發行版的具體版本號 
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 20.04.2 LTS
Release:	20.04
Codename:	focal
```

- 請選擇如下合適的方式運行Linux實驗操作系統
  - 物理機/虛擬機(Virtual Box, Vmware…)
  - Windows Subsystem for Linux(WSL)
  - Docker鏡像運行

### 3.2 實驗所需的工具/源代碼

- [QEMU 6.0.0](https://download.qemu.org/qemu-6.0.0.tar.xz)
- [Linux Kernel 5.10.42(LTS)](https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.10.42.tar.gz)
- [RISC‑V Compiler Toolchain](http://riscv-gnu-toolchain: riscv-gnu-toolchain 是一個用來支持 RISC-V 為後端的C和C++交叉編譯工具鏈, 包含通用的ELF/Newlib和更復雜的Linux-ELF/glibc兩種 (gitee.com))

## 4 背景知識

### 4.1 RISC-V：自由和開放的RISC指令集架構

- [RISC-V歷史](https://riscv.org/about/history/)
- [RISC-V介紹](https://riscv.org/wp-content/uploads/2021/05/RISC-V-Introduction.pptx)

```
RISC-V ISA發端於深厚的學術研究，將免費且可擴展的軟硬件架構自由度提升至新的水平，為未來50年的計算設計與創新鋪平了道路。
```

### 4.2 QEMU：一款開源且通用的模擬器和虛擬機

- [QEMU介紹](https://wiki.qemu.org/Main_Page)
- [QEMU用戶手冊](https://qemu-project.gitlab.io/qemu/system/index.html)

#### 4.2.1 什麼是QEMU

QEMU最開始是由法國程序員Fabrice Bellard開發的模擬器。QEMU能夠完成用戶程序模擬和系統虛擬化模擬。用戶程序模擬指的是QEMU能夠將為一個平臺編譯的二進制文件運行在另一個不同的平臺，如一個ARM指令集的二進制程序，通過QEMU的TCG（Tiny Code Generator）引擎的處理之後，ARM指令被轉化為TCG中間代碼，然後再轉化為目標平臺（比如Intel x86）的代碼。系統虛擬化模擬指的是QEMU能夠模擬一個完整的系統虛擬機，該虛擬機有自己的虛擬CPU，芯片組，虛擬內存以及各種虛擬外部設備，能夠為虛擬機中運行的操作系統和應用軟件呈現出與物理計算機完全一致的硬件視圖。

#### 4.2.2 如何使用 QEMU（常見參數介紹）

以以下命令為例，我們簡單介紹QEMU的參數所代表的含義

```
$ qemu-system-riscv64 -nographic -machine virt -kernel build/linux/arch/riscv/boot/Image  \
 -device virtio-blk-device,drive=hd0 -append "root=/dev/vda ro console=ttyS0"   \
 -bios default -drive file=rootfs.ext4,format=raw,id=hd0 \
 -netdev user,id=net0 -device virtio-net-device,netdev=net0 -S -s
```

**-nographic**: 不使用圖形窗口，使用命令行
**-machine**: 指定要emulate的機器，可以通過命令`qemu-system-riscv64 -machine help`查看可選擇的機器選項
**-kernel**: 指定內核image
**-append cmdline**: 使用cmdline作為內核的命令行
**-device**: 指定要模擬的設備，可以通過命令`qemu-system-riscv64 -device help`查看可選擇的設備，通過命令`qemu-system-riscv64 -device <具體的設備>,help`查看某個設備的命令選項
**-drive, file=<file_name>**: 使用’file’作為文件系統
**-netdev user,id=str**: 指定user mode的虛擬網卡, 指定ID為str
**-S**: 啟動時暫停CPU執行(使用’c’啟動執行)
**-s**: -gdb tcp::1234 的簡寫
**-bios default**: 使用默認的OpenSBI firmware作為bootloader

更多參數信息可以參考[這裡](https://www.qemu.org/docs/master/system/index.html)

### 4.3 Linux 內核

Linux is a clone of the operating system Unix, written from scratch by Linus Torvalds with assistance from a loosely-knit team of hackers across the Net. It aims towards POSIX and [Single UNIX Specification](http://www.unix.org/) compliance.

It has all the features you would expect in a modern fully-fledged Unix, including true multitasking, virtual memory, shared libraries, demand loading, shared copy-on-write executables, proper memory management, and multistack networking including IPv4 and IPv6.

Although originally developed first for 32-bit x86-based PCs (386 or higher), today Linux also runs on a multitude of other processor architectures, in both 32- and 64-bit variants.

#### 4.3.1 Linux 使用基礎

在Linux環境下，人們通常使用命令行接口來完成與計算機的交互。終端（Terminal）是用於處理該過程的一個應用程序，通過終端你可以運行各種程序以及在自己的計算機上處理文件。在類Unix的操作系統上，終端可以為你完成一切你所需要的操作。
下面我們僅對實驗中涉及的一些概念進行介紹，你可以通過下面的鏈接來對命令行的使用進行學習：

1. [The Missing Semester of Your CS Education](https://missing-semester-cn.github.io/2020/shell-tools) [>>Video<<](https://www.bilibili.com/video/BV1x7411H7wa?p=2)
2. [GNU/Linux Command-Line Tools Summary](https://tldp.org/LDP/GNU-Linux-Tools-Summary/html/index.html)
3. [Basics of UNIX](https://github.com/berkeley-scf/tutorial-unix-basics)

#### 4.3.2 Linux 環境變量

當我們在終端輸入命令時，終端會找到對應的程序來運行。我們可以通過`which`命令來做一些小的實驗：

```
$ which gcc
/usr/bin/gcc
$ ls -l /usr/bin/gcc
lrwxrwxrwx 1 root root 5 5月  21  2019 /usr/bin/gcc -> gcc-7
```

可以看到，當我們在輸入`gcc`命令時，終端實際執行的程序是`/usr/bin/gcc`。實際上，終端在執行命令時，會從`PATH`環境變量所包含的地址中查找對應的程序來執行。我們可以將`PATH`變量打印出來來檢查一下其是否包含`/usr/bin`。

```
$ echo $PATH
/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin:/home/phantom/.local/bin
```

在後面的實驗中，如果你想直接訪問`riscv64-unknown-linux-gnu-gcc`、`qemu-system-riscv64`等程序，那麼你需要把他們所在的目錄添加到目錄中。

```
$ export PATH=$PATH:/opt/riscv/bin
```

### 4.4 交叉編譯工具鏈

compiler is a kind of computer software that compiles a high-level language (such as C) into machine instructions that can be executed by the target CPU platform.

#### 4.4.1 編譯器的類別

這裡首先介紹如下三種概念名詞：

- ***\*The build system: The machine which generates the compiler binaries.\****
- ***\*The host system: The system which runs the compiler binaries.\****
- ***\*The target system: The system which runs the application code compiled by the compiler binari\****

根據上述不同平臺之間的異同，編譯器可以分為如下幾種類型：

- **native compiler**: A compiler where **target** is the same system as **host**.
- **cross compiler**: A compiler where **target** is not the same system as **host**.

其中**交叉編譯工具鏈（Cross Compiler）**是我們在本系列實驗中所採用的主要編譯工具。交叉編譯指的是在一個平臺上編譯可以在另一個平臺運行的程序，例如在x86機器上編譯可以在arm平臺運行的程序，交叉編譯需要交叉編譯工具鏈的支持。

在後續實驗中我們令：

```
build = X86_64 linux
host =  X86_64 linux
target = RISC-V64 
```

#### 4.4.2 GNU GCC

GCC stands for GNU Compiler Collection

GCC is an integrated distribution of compilers for several major programming languages. These languages currently include C, C++,Objective-C, Objective-C++, Fortran, Ada, D, Go, and BRIG (HSAIL)

> [GCC 11.1 Manual](https://gcc.gnu.org/onlinedocs/gcc-11.1.0/gcc/) 
>
> Using the GNU Compiler Collection For gcc version 11.1.0
> [Richard M. Stallman](https://stallman.org/) and the [GCC Developer Community](https://gcc.gnu.org/)

#### 4.4.2 GNU Binutils

The GNU Binutils are a collection of binary tools. The main ones are:

- **ld** – the GNU linker.
- **as** – the GNU assembler.

But they also include:

- **addr2line** – Converts addresses into filenames and line numbers.
- **ar** – A utility for creating, modifying and extracting from archives.
- **c++filt** – Filter to demangle encoded C++ symbols.
- **dlltool** – Creates files for building and using DLLs.
- **gold** – A new, faster, ELF only linker, still in beta test.
- **gprof** – Displays profiling information.
- **nlmconv** – Converts object code into an NLM.
- **nm** – Lists symbols from object files.
- **objcopy** – Copies and translates object files.
- **objdump** – Displays information from object files.
- **ranlib** – Generates an index to the contents of an archive.
- **readelf** – Displays information from any ELF format object file.
- **size** – Lists the section sizes of an object or archive file.
- **strings** – Lists printable strings from files.
- **strip** – Discards symbols.
- **windmc** – A Windows compatible message compiler.
- **windres** – A compiler for Windows resource files.

Most of these programs use **BFD**, the Binary File Descriptor library, to do low-level manipulation. Many of them also use the **opcodes** library to assemble and disassemble machine instructions.

> [GNU Binutils](https://www.gnu.org/software/binutils/)
>
> [**GNU** Operating System](https://www.gnu.org/)
> Supported by the [Free Software Foundation](https://www.gnu.org/software/binutils/#mission-statement)

### 4.5 GDB 使用基礎

#### 4.5.1 什麼是 GDB

GNU調試器（英語：GNU Debugger，縮寫：gdb）是一個由GNU開源組織發佈的、UNIX/LINUX操作系統下的、基於命令行的、功能強大的程序調試工具。藉助調試器，我們能夠查看另一個程序在執行時實際在做什麼（比如訪問哪些內存、寄存器），在其他程序崩潰的時候可以比較快速地瞭解導致程序崩潰的原因。
被調試的程序可以是和gdb在同一臺機器上（本地調試，or native debug），也可以是不同機器上（遠程調試， or remote debug）。

總的來說，gdb可以有以下4個功能

- 啟動程序，並指定可能影響其行為的所有內容
- 使程序在指定條件下停止
- 檢查程序停止時發生了什麼
- 更改程序中的內容，以便糾正一個bug的影響

#### 4.5.2 GDB 基本命令介紹

(gdb) start：單步執行，運行程序，停在第一執行語句
(gdb) next：單步調試（逐過程，函數直接執行）,簡寫n
(gdb) run：重新開始運行文件（run-text：加載文本文件，run-bin：加載二進制文件），簡寫r
(gdb) backtrace：查看函數的調用的棧幀和層級關係，簡寫bt
(gdb) break 設置斷點。比如斷在具體的函數就break func；斷在某一行break filename:num
(gdb) finish：結束當前函數，返回到函數調用點
(gdb) frame：切換函數的棧幀，簡寫f
(gdb) print：打印值及地址，簡寫p
(gdb) info：查看函數內部局部變量的數值，簡寫i；查看寄存器的值i register xxx
(gdb) display：追蹤查看具體變量值

更多命令可以參考[100個gdb小技巧](https://wizardforcel.gitbooks.io/100-gdb-tips/content/)

#### 4.5.3 GDB 插件使用（不做要求）

單純使用gdb比較繁瑣不是很方便，我們可以使用gdb插件讓調試過程更有效率。推薦各位同學使用gef，由於當前工具鏈還不支持 `python3`，請使用舊版本的[gef-legacy](https://github.com/hugsy/gef-legacy)。
該倉庫中已經取消的原有的安裝腳本，同學們可以把 `gef.py` 腳本拷貝下來，直接在 `.gdbinit` 中引導，感興趣的同學可以參考這篇[文章（內網訪問)](http://zju.phvntom.tech/markdown/md2html.php?id=md/gef.md)。

###  4.6 LINUX 內核編譯基礎

#### 4.6.1 內核配置

內核配置是用於配置是否啟用內核的各項特性，內核會提供一個名為 `defconfig`(即default configuration) 的默認配置，該配置文件位於各個架構目錄的 `configs` 文件夾下，例如對於RISC-V而言，其默認配置文件為 `arch/riscv/configs/defconfig`。使用 `make ARCH=riscv defconfig` 命令可以在內核根目錄下生成一個名為 `.config` 的文件，包含了內核完整的配置，內核在編譯時會根據 `.config` 進行編譯。配置之間存在相互的依賴關係，直接修改defconfig文件或者 `.config` 有時候並不能達到想要的效果。因此如果需要修改配置一般採用 `make ARCH=riscv menuconfig` 的方式對內核進行配置。

#### 4.6.2 常見參數

**ARCH** 指定架構，可選的值包括arch目錄下的文件夾名，如x86,arm,arm64等，不同於arm和arm64，32位和64位的RISC-V共用 `arch/riscv` 目錄，通過使用不同的config可以編譯32位或64位的內核。

**CROSS_COMPILE** 指定使用的交叉編譯工具鏈，例如指定 `CROSS_COMPILE=aarch64-linux-gnu-`，則編譯時會採用 `aarch64-linux-gnu-gcc` 作為編譯器，編譯可以在arm64平臺上運行的kernel。

**CC** 指定編譯器，通常指定該變量是為了使用clang編譯而不是用gcc編譯，Linux內核在逐步提供對clang編譯的支持，arm64和x86已經能夠很好的使用clang進行編譯。

#### 4.6.3 常用編譯選項

```
$ make defconfig	        ### 使用當前平臺的默認配置，在x86機器上會使用x86的默認配置
$ make -j$(nproc)	        ### 編譯當前平臺的內核，-j$(nproc)為以機器硬件線程數進行多線程編譯

$ make ARCH=riscv defconfig	### 使用RISC-V平臺的默認配置
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j$(nproc)     ### 編譯RISC-V平臺內核

$ make clean	                ### 清除所有編譯好的object文件
$ make mrproper	                ### 清除編譯的配置文件，中間文件和結果文件

$ make init/main.o	        ### 編譯當前平臺的單個object文件init/main.o（會同時編譯依賴的文件）
```

## 5 實驗步驟

通常情況下，`$` 提示符表示當前運行的用戶為普通用戶，`#` 代表當前運行的用戶為特權用戶。
但注意，在下文的示例中，以 `###` 開頭的行代表註釋，`$` 開頭的行代表在你的宿主機/虛擬機上運行的命令，`#` 開頭的行代表在 `docker` 中運行的命令，`(gdb)` 開頭的行代表在 `gdb` 中運行的命令。
**在執行每一條命令前，請你對將要進行的操作進行思考，給出的命令不需要全部執行，並且不是所有的命令都可以無條件執行，請不要直接複製粘貼命令去執行。**

### 5.1 實驗環境設置

#### 5.1.1 下載安裝必要的工具和庫

```
$ sudo apt update
$ sudo apt upgrade
$ sudo apt install git \
        autoconf \
        automake \
        autotools-dev \
        ninja-build \
        build-essential \
        libmpc-dev \
        libmpfr-dev \
        libgmp-dev \
        libglib2.0-dev \
        libpixman-1-dev \
        libncurses5-dev \
        libtool \
        libexpat-dev \
        zlib1g-dev \
        curl \
        gawk \
        bison \
        flex \
        texinfo \
        gperf \
        patchutils \
        bc 
```

#### 5.1.2 下載和安裝必要的工具鏈以及源代碼包

##### 5.1.2.1 編譯安裝 QEMU 5.0.0

```
$ mkdir riscv_oslab
$ cd ~/riscv64_oslab  ### 進入實驗工作目錄，然後在線獲取QEMU 5.0.0版本的源代碼安裝包到當前目錄下
$ wget https://download.qemu.org/qemu-5.0.0.tar.xz 
$ tar -xvJf qemu-5.0.0.tar.xz ### 解壓縮源代碼包到qemu-5.0.0文件夾中
$ cd qemu-5.0.0 ### 進入該目錄
$ ./configure --static --target-list=riscv64-softmmu,riscv64-linux-user ### 編譯前配置好QEMU，病設置目標處理器架構為"64位的RISC-V"
$ make -j16 ### 編譯，可用nproc查看可用的線程數
$ make install ### 安裝QEMU到默認位置
```

此處編譯qemu的時候，目標選擇了 riscv64-softmmu 和 riscv64-linux-user，兩者具體的區別為：

To put it simply, xxx-softmmu will compile **qemu-system-xxx**, which is an emulated machine for xxx architecture (System Emulation). When it resets, the starting point will be the reset vector of that architecture. While xxx-linux-user, compiles **qemu-xxx**, which allows you to run user application in xxx architecture (User-mode Emulation). Which will seek the user applications’ main function, and start execution from there.

安裝完畢後如果執行如下命令後能夠查看到qemu的具體版本，則說明安裝成功

```
$ qemu-system-riscv64 --version
QEMU emulator version 5.0.0
Copyright (c) 2003-2021 Fabrice Bellard and the QEMU Project developers
```

##### 5.1.2.2 下載或編譯安裝 RISC‑V GCC Toolchain

**途徑**1（推薦）：下載預編譯版本的 riscv-gnu-toolchain

- 下載newlibc版本的riscv-gnu-toolchain，地址：https://www.sifive.com/software

這裡可選擇下載：GNU Embedded Toolchain — v2020.12.8 Ubuntu版本的 Prebuilt RISC‑V GCC Toolchain（帶有gdb調試工具）在此您也可以選擇運行在其它系統環境下的riscv-gnu-toolchain.

```
$ cd ~/riscv64_oslab
$ wget https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
$ tar -xzvf riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz ###解壓
$ mv riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14 \
     riscv64-unknown-elf-toolchain ### 重命名文件夾
$ 編輯~/.bashrc 在文件末尾添加如下環境變量設置語句
export PATH=~/riscv_oslab/riscv64-unknown-elf-toolchain/bin:$PATH
$ source ~/.bashrc
$ riscv64-unknown-elf-gcc --version ### 查看gcc版本
riscv64-unknown-elf-gcc (SiFive GCC-Metal 10.2.0-2020.12.8) 10.2.0
Copyright (C) 2020 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

- 安裝 glibc 版本的 riscv-gnu-toolchain

```
$ sudo apt install binutils-riscv64-linux-gnu
$ sudo apt install gcc-riscv64-linux-gnu
$ riscv64-linux-gnu-gcc --version ### 查看gcc版本
riscv64-linux-gnu-gcc (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0
Copyright (C) 2019 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```

**途徑2**：從源代碼編譯獲得

首先下載 riscv-gnu-toolchain倉庫

```
$ git clone --recursive https://github.com/riscv/riscv-gnu-toolchain
```

注意：採用上述Git clone的方式來獲得riscv-gnu-toolchain可能需要6.65GB的空間

編譯安裝步驟：

```
./configure --prefix=/opt/riscv
make
```

##### 5.1.2.3 使用上述交叉編譯工具鏈編譯Linux 5.10.42版本的內核

```
$ cd ~/riscv64_oslab
$ wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.10.42.tar.gz
$ tar -xzvf linux-5.10.42.tar.gz
$ cd linux-5.10.42
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
  ...
  GEN     .version
  CHK     include/generated/compile.h
  LD      vmlinux.o
  MODPOST vmlinux.symvers
  MODINFO modules.builtin.modinfo
  GEN     modules.builtin
  LD      .tmp_vmlinux.kallsyms1
  KSYMS   .tmp_vmlinux.kallsyms1.S
  AS      .tmp_vmlinux.kallsyms1.S
  LD      .tmp_vmlinux.kallsyms2
  KSYMS   .tmp_vmlinux.kallsyms2.S
  AS      .tmp_vmlinux.kallsyms2.S
  LD      vmlinux
  SYSMAP  System.map
  MODPOST modules-only.symvers
  GEN     Module.symvers
  OBJCOPY arch/riscv/boot/Image
  CC [M]  fs/efivarfs/efivarfs.mod.o
  GZIP    arch/riscv/boot/Image.gz
  LD [M]  fs/efivarfs/efivarfs.ko
  Kernel: arch/riscv/boot/Image.gz is ready
```

##### 5.1.2.4 使用上述交叉編譯工具鏈編譯Busybox

```
$ cd ~/riscv64_oslab
$ wget https://busybox.net/downloads/busybox-1.33.1.tar.bz2
$ tar  -jxvf  busybox-1.33.1.tar.bz2 
$ cd busybox-1.33.1
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- menuconfig ### 這裡打開後可以選擇直接exit，並保存到配置文件.config中
$ 打開.config文件並編輯添加 
  CONFIG_STATIC=y
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
$ make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- install
$ cd _install
$ mkdir proc sys dev etc etc/init.d
$ ls ### 查看目錄結構
bin  dev  etc  linuxrc  proc  sbin  sys  usr
$ touch etc/init.d/rcS 並編輯文件內容為如下： ### We will now create a bash script in order to mount some devices automatically after the boot.
$ sudo mknod dev/console c 5 1
$ sudo mknod dev/ram b 1 0
#!bin/sh
mount -t proc none /proc
mount -t sysfs none /sys
/sbin/mdev -s
$ chmod +x etc/init.d/rcS # Now change the file’s mode as executable.
$ find -print0 | cpio -0oH newc | gzip -9 > ../rootfs.img
$ cd ..
```

##### 5.1.2.5 使用qemu 運行我們的linux kernel

從上述的實驗步驟中我們分別獲得了

```
~/riscv_oslab/busybox-1.33.1/rootfs.img
~/riscv_oslab/linux-5.10.42/arch/riscv/boot/Image
```

下面我們在QEMU中模擬運行我們地Linux內核：

執行如下命令行:

```
$ qemu-system-riscv64 \
        -nographic -machine virt \
        -kernel ~/riscv_oslab/linux-5.10.42/arch/riscv/boot/Image \
        -initrd ~/riscv_oslab/busybox-1.33.1/rootfs.img  \
        -append "root=/dev/ram rdinit=/sbin/init"
```

可以看到整個Linux Kernel地啟動流程：

```
OpenSBI v0.9
   ____                    _____ ____ _____
  / __ \                  / ____|  _ \_   _|
 | |  | |_ __   ___ _ __ | (___ | |_) || |
 | |  | | '_ \ / _ \ '_ \ \___ \|  _ < | |
 | |__| | |_) |  __/ | | |____) | |_) || |_
  \____/| .__/ \___|_| |_|_____/|____/_____|
        | |
        |_|

Platform Name             : riscv-virtio,qemu
Platform Features         : timer,mfdeleg
Platform HART Count       : 1
Firmware Base             : 0x80000000
Firmware Size             : 100 KB
Runtime SBI Version       : 0.2

Domain0 Name              : root
Domain0 Boot HART         : 0
Domain0 HARTs             : 0*
Domain0 Region00          : 0x0000000080000000-0x000000008001ffff ()
Domain0 Region01          : 0x0000000000000000-0xffffffffffffffff (R,W,X)
Domain0 Next Address      : 0x0000000080200000
Domain0 Next Arg1         : 0x0000000087000000
Domain0 Next Mode         : S-mode
Domain0 SysReset          : yes

Boot HART ID              : 0
Boot HART Domain          : root
Boot HART ISA             : rv64imafdcsu
Boot HART Features        : scounteren,mcounteren,time
Boot HART PMP Count       : 16
Boot HART PMP Granularity : 4
Boot HART PMP Address Bits: 54
Boot HART MHPM Count      : 0
Boot HART MHPM Count      : 0
Boot HART MIDELEG         : 0x0000000000000222
Boot HART MEDELEG         : 0x000000000000b109
[    0.000000] Linux version 5.10.42 (nn@ubuntu) (riscv64-linux-gnu-gcc (Ubuntu 9.3.0-17ubuntu1~20.04) 9.3.0, GNU ld (GNU Binutils for Ubuntu) 2.34) #1 SMP Sat Jun 26 22:53:26 PDT 2021
[    0.000000] OF: fdt: Ignoring memory range 0x80000000 - 0x80200000
[    0.000000] efi: UEFI not found.
[    0.000000] Initial ramdisk at: 0x(____ptrval____) (1146880 bytes)
[    0.000000] Zone ranges:
[    0.000000]   DMA32    [mem 0x0000000080200000-0x0000000087ffffff]
[    0.000000]   Normal   empty
[    0.000000] Movable zone start for each node
[    0.000000] Early memory node ranges
[    0.000000]   node   0: [mem 0x0000000080200000-0x0000000087ffffff]
[    0.000000] Initmem setup node 0 [mem 0x0000000080200000-0x0000000087ffffff]
[    0.000000] software IO TLB: Cannot allocate buffer
[    0.000000] SBI specification v0.2 detected
[    0.000000] SBI implementation ID=0x1 Version=0x9
[    0.000000] SBI v0.2 TIME extension detected
[    0.000000] SBI v0.2 IPI extension detected
[    0.000000] SBI v0.2 RFENCE extension detected
[    0.000000] SBI v0.2 HSM extension detected
[    0.000000] riscv: ISA extensions acdfimsu
[    0.000000] riscv: ELF capabilities acdfim
[    0.000000] percpu: Embedded 17 pages/cpu s32360 r8192 d29080 u69632
[    0.000000] Built 1 zonelists, mobility grouping on.  Total pages: 31815
[    0.000000] Kernel command line: root=/dev/ram rdinit=/sbin/init
[    0.000000] Dentry cache hash table entries: 16384 (order: 5, 131072 bytes, linear)
[    0.000000] Inode-cache hash table entries: 8192 (order: 4, 65536 bytes, linear)
[    0.000000] Sorting __ex_table...
[    0.000000] mem auto-init: stack:off, heap alloc:off, heap free:off
[    0.000000] Memory: 108180K/129024K available (6954K kernel code, 4125K rwdata, 4096K rodata, 223K init, 342K bss, 20844K reserved, 0K cma-reserved)
[    0.000000] Virtual kernel memory layout:
[    0.000000]       fixmap : 0xffffffcefee00000 - 0xffffffceff000000   (2048 kB)
[    0.000000]       pci io : 0xffffffceff000000 - 0xffffffcf00000000   (  16 MB)
[    0.000000]      vmemmap : 0xffffffcf00000000 - 0xffffffcfffffffff   (4095 MB)
[    0.000000]      vmalloc : 0xffffffd000000000 - 0xffffffdfffffffff   (65535 MB)
[    0.000000]       lowmem : 0xffffffe000000000 - 0xffffffe007e00000   ( 126 MB)
[    0.000000] SLUB: HWalign=64, Order=0-3, MinObjects=0, CPUs=1, Nodes=1
[    0.000000] rcu: Hierarchical RCU implementation.
[    0.000000] rcu: 	RCU restricting CPUs from NR_CPUS=8 to nr_cpu_ids=1.
[    0.000000] rcu: 	RCU debug extended QS entry/exit.
[    0.000000] 	Tracing variant of Tasks RCU enabled.
[    0.000000] rcu: RCU calculated value of scheduler-enlistment delay is 25 jiffies.
[    0.000000] rcu: Adjusting geometry for rcu_fanout_leaf=16, nr_cpu_ids=1
[    0.000000] NR_IRQS: 64, nr_irqs: 64, preallocated irqs: 0
[    0.000000] riscv-intc: 64 local interrupts mapped
[    0.000000] plic: plic@c000000: mapped 53 interrupts with 1 handlers for 2 contexts.
[    0.000000] random: get_random_bytes called from start_kernel+0x312/0x484 with crng_init=0
[    0.000000] riscv_timer_init_dt: Registering clocksource cpuid [0] hartid [0]
[    0.000000] clocksource: riscv_clocksource: mask: 0xffffffffffffffff max_cycles: 0x24e6a1710, max_idle_ns: 440795202120 ns
[    0.000155] sched_clock: 64 bits at 10MHz, resolution 100ns, wraps every 4398046511100ns
[    0.003256] Console: colour dummy device 80x25
[    0.004684] printk: console [tty0] enabled
[    0.008705] Calibrating delay loop (skipped), value calculated using timer frequency.. 20.00 BogoMIPS (lpj=40000)
[    0.008862] pid_max: default: 32768 minimum: 301
[    0.009925] Mount-cache hash table entries: 512 (order: 0, 4096 bytes, linear)
[    0.009977] Mountpoint-cache hash table entries: 512 (order: 0, 4096 bytes, linear)
[    0.031354] rcu: Hierarchical SRCU implementation.
[    0.033066] EFI services will not be available.
[    0.034680] smp: Bringing up secondary CPUs ...
[    0.034774] smp: Brought up 1 node, 1 CPU
[    0.042458] devtmpfs: initialized
[    0.047904] clocksource: jiffies: mask: 0xffffffff max_cycles: 0xffffffff, max_idle_ns: 7645041785100000 ns
[    0.048157] futex hash table entries: 256 (order: 2, 16384 bytes, linear)
[    0.052753] NET: Registered protocol family 16
[    0.096960] vgaarb: loaded
[    0.097897] SCSI subsystem initialized
[    0.099470] usbcore: registered new interface driver usbfs
[    0.099708] usbcore: registered new interface driver hub
[    0.099841] usbcore: registered new device driver usb
[    0.109735] clocksource: Switched to clocksource riscv_clocksource
[    0.121388] NET: Registered protocol family 2
[    0.122636] IP idents hash table entries: 2048 (order: 2, 16384 bytes, linear)
[    0.125264] tcp_listen_portaddr_hash hash table entries: 128 (order: 0, 5120 bytes, linear)
[    0.125384] TCP established hash table entries: 1024 (order: 1, 8192 bytes, linear)
[    0.125566] TCP bind hash table entries: 1024 (order: 3, 32768 bytes, linear)
[    0.125704] TCP: Hash tables configured (established 1024 bind 1024)
[    0.126589] UDP hash table entries: 256 (order: 2, 24576 bytes, linear)
[    0.126838] UDP-Lite hash table entries: 256 (order: 2, 24576 bytes, linear)
[    0.127964] NET: Registered protocol family 1
[    0.130578] RPC: Registered named UNIX socket transport module.
[    0.130640] RPC: Registered udp transport module.
[    0.130666] RPC: Registered tcp transport module.
[    0.130690] RPC: Registered tcp NFSv4.1 backchannel transport module.
[    0.130796] PCI: CLS 0 bytes, default 64
[    0.132983] Unpacking initramfs...
[    0.184451] Freeing initrd memory: 1116K
[    0.186811] workingset: timestamp_bits=62 max_order=15 bucket_order=0
[    0.196540] NFS: Registering the id_resolver key type
[    0.197258] Key type id_resolver registered
[    0.197309] Key type id_legacy registered
[    0.197590] nfs4filelayout_init: NFSv4 File Layout Driver Registering...
[    0.197681] nfs4flexfilelayout_init: NFSv4 Flexfile Layout Driver Registering...
[    0.198313] 9p: Installing v9fs 9p2000 file system support
[    0.199295] NET: Registered protocol family 38
[    0.199533] Block layer SCSI generic (bsg) driver version 0.4 loaded (major 251)
[    0.199661] io scheduler mq-deadline registered
[    0.199745] io scheduler kyber registered
[    0.206411] pci-host-generic 30000000.pci: host bridge /soc/pci@30000000 ranges:
[    0.207040] pci-host-generic 30000000.pci:       IO 0x0003000000..0x000300ffff -> 0x0000000000
[    0.207407] pci-host-generic 30000000.pci:      MEM 0x0040000000..0x007fffffff -> 0x0040000000
[    0.207473] pci-host-generic 30000000.pci:      MEM 0x0400000000..0x07ffffffff -> 0x0400000000
[    0.209120] pci-host-generic 30000000.pci: ECAM at [mem 0x30000000-0x3fffffff] for [bus 00-ff]
[    0.209814] pci-host-generic 30000000.pci: PCI host bridge to bus 0000:00
[    0.210081] pci_bus 0000:00: root bus resource [bus 00-ff]
[    0.210175] pci_bus 0000:00: root bus resource [io  0x0000-0xffff]
[    0.210203] pci_bus 0000:00: root bus resource [mem 0x40000000-0x7fffffff]
[    0.210228] pci_bus 0000:00: root bus resource [mem 0x400000000-0x7ffffffff]
[    0.211207] pci 0000:00:00.0: [1b36:0008] type 00 class 0x060000
[    0.257315] Serial: 8250/16550 driver, 4 ports, IRQ sharing disabled
[    0.263577] 10000000.uart: ttyS0 at MMIO 0x10000000 (irq = 2, base_baud = 230400) is a 16550A
[    0.293271] printk: console [ttyS0] enabled
[    0.298044] [drm] radeon kernel modesetting enabled.
[    0.311076] loop: module loaded
[    0.313675] libphy: Fixed MDIO Bus: probed
[    0.314711] e1000e: Intel(R) PRO/1000 Network Driver
[    0.314950] e1000e: Copyright(c) 1999 - 2015 Intel Corporation.
[    0.315481] ehci_hcd: USB 2.0 'Enhanced' Host Controller (EHCI) Driver
[    0.315834] ehci-pci: EHCI PCI platform driver
[    0.316191] ehci-platform: EHCI generic platform driver
[    0.316510] ohci_hcd: USB 1.1 'Open' Host Controller (OHCI) Driver
[    0.316869] ohci-pci: OHCI PCI platform driver
[    0.317290] ohci-platform: OHCI generic platform driver
[    0.318730] usbcore: registered new interface driver uas
[    0.319250] usbcore: registered new interface driver usb-storage
[    0.320182] mousedev: PS/2 mouse device common for all mice
[    0.323094] goldfish_rtc 101000.rtc: registered as rtc0
[    0.323986] goldfish_rtc 101000.rtc: setting system clock to 2021-06-27T06:45:02 UTC (1624776302)
[    0.326296] syscon-poweroff soc:poweroff: pm_power_off already claimed (____ptrval____) sbi_shutdown
[    0.326805] syscon-poweroff: probe of soc:poweroff failed with error -16
[    0.327990] usbcore: registered new interface driver usbhid
[    0.328373] usbhid: USB HID core driver
[    0.330278] NET: Registered protocol family 10
[    0.337351] Segment Routing with IPv6
[    0.338095] sit: IPv6, IPv4 and MPLS over IPv4 tunneling driver
[    0.340452] NET: Registered protocol family 17
[    0.341736] 9pnet: Installing 9P2000 support
[    0.342188] Key type dns_resolver registered
[    0.342886] debug_vm_pgtable: [debug_vm_pgtable         ]: Validating architecture page table helpers
[    0.378742] Freeing unused kernel memory: 220K
[    0.381020] Run /sbin/init as init process

Please press Enter to activate this console. 
```

由於以安裝了Busy Box並製作了rootfs，因此可以運行較多的常用命令，示例如下：

```
/ # ls
bin      etc      proc     sbin     usr
dev      linuxrc  root     sys
/ # pwd
/ # cd bin
/bin # ls
arch           dumpkmap       kill           netstat        setarch
ash            echo           link           nice           setpriv
base32         ed             linux32        nuke           setserial
base64         egrep          linux64        pidof          sh
busybox        false          ln             ping           sleep
cat            fatattr        login          ping6          stat
chattr         fdflush        ls             pipe_progress  stty
chgrp          fgrep          lsattr         printenv       su
chmod          fsync          lzop           ps             sync
chown          getopt         makemime       pwd            tar
conspy         grep           mkdir          reformime      touch
cp             gunzip         mknod          resume         true
cpio           gzip           mktemp         rev            umount
cttyhack       hostname       more           rm             uname
date           hush           mount          rmdir          usleep
dd             ionice         mountpoint     rpm            vi
df             iostat         mpstat         run-parts      watch
dmesg          ipcalc         mt             scriptreplay   zcat
dnsdomainname  kbd_mode       mv             sed
/bin # 
退出QEMU模擬器的方法為：
使用ctrl+a(macOS下為control+a)，鬆開後再按下x鍵即可退出qemu
```

## Debug with GDB

接下來使用GDB來調試運行在QEMU中地Linux Kernel：

在之前運行QEMU啟動Linux Kernel的命令行之後追加如下兩個參數 **-s -S**

```
$ qemu-system-riscv64 \
        -nographic -machine virt \
        -kernel ~/riscv_oslab/linux-5.10.42/arch/riscv/boot/Image \
        -initrd ~/riscv_oslab/busybox-1.33.1/rootfs.img  \
        -append "root=/dev/ram rdinit=/sbin/init" \
        -s -S
```

然後打開另一個終端，使用 riscv64-unknown-elf-gdb 進行內核的調試工作:

查看gdb的版本號：

```
$ riscv64-unknown-elf-gdb --version
GNU gdb (SiFive GDB-Metal 10.1.0-2020.12.7) 10.1
$ riscv64-unknown-elf-gdb ~/riscv_oslab/linux-5.10.42/vmlinux
```

若gdb提示如下信息：

```
Reading symbols from .../vmlinux…
(No debugging symbols found in .../vmlinux)
```

需要重新編譯內核,需要在內核Makefile的KBUILD_CFLAGS上添加**-g**選項，然後繼續運行上述命令行啟動gdb開始調試

在gdb中添加斷點,如在start_kernel處添加斷點後,輸⼊continue,則qemu會在初始化kernel的過程中停止,如下所示:

```
(gdb) remote target localhost:1234 ### 連接本地Qemu調試端口
(gdb) b start_kernel 
Breakpoint 1 at 0xffffffe00000272e
(gdb) continue
Continuing.
Breakpoint 1, 0xffffffe00000272e in start_kernel ()
```
