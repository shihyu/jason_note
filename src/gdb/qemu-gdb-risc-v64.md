## RISC-V Linux kernel debug 環境搭建

https://blog.csdn.net/m0_43422086/article/details/125276723

# 一、目的

搭建qemu-gdb risc-v64 linux kernel的調試環境。

# 二、準備工作

​    Build Ninja 和riscv-toolchain

​    首先安裝必要的庫(這是編譯riscv toolchain必須安裝的庫文件)

```bash
sudo apt update 
sudo apt upgrade 
sudo apt install \
    git \
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


mkdir qemu-gdb-risc-v64 && qemu-gdb-risc-v64
```

## ①Build Ninja

```bash
git clone https://github.com/ninja-build/ninja.git
cd ninja
cmake -Bbuild-cmake
cmake --build build-cmake
```

然後在.bashrc中添加ninja/build-cmake目錄

編輯.bashrc如下：

```bash
export PATH=$PATH:/home/kali/Desktop/riscv-debug/ninja/build-cmake
```

## ②Build riscv-gnu-compiler toolchain and debug gdb

```bash
wget https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
tar -xzvf riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
mv riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14  riscv64-unknown-elf-toolchain
```

接著編輯~/.bashrc,加入下面的環境變量：

```bash
export PATH=$PATH:/home/kali/Desktop/riscv-debug/riscv64-unknown-elf-toolchain/bin
```

## ③命令行安裝gcc-riscv64-linux-gnu-

```bash
sudo apt install binutils-riscv64-linux-gnu 
sudo apt install gcc-riscv64-linux-gnu
```

OR

自己下載工具鏈原始碼進行編譯容易配錯選項，我們使用編譯好的工具鏈即可。
網址：https://toolchains.bootlin.com
這個網站提供了一些已經編譯好的工具鏈，我們從中下載即可。
arch選擇riscv64-lp64d，libc選擇glibc，然後點選下載。
stable是穩定版，bleeding-edge是最新的，可根據需要選擇，這裡我們選擇bleeding-edge。

```bash
export PATH=xxxxxxxxxxxxxxxxxxxx/toolchain/riscv64-lp64d--glibc--bleeding-edge-2022.08-1/bin:$PATH
```


# 三、Build Qemu

```bash
git clone https://gitlab.com/qemu-project/qemu.git
cd qemu
git submodule init
git submodule update --recursive
mkdir build && cd build
../configure --prefix=/home/shihyu/.mybin/qemu
make



linux-user/ioctls.h:188:1: error: ‘SNDCTL_DSP_MAPINBUF’ undeclared here (not in a function)
linux-user/ioctls.h:189:1: error: ‘SNDCTL_DSP_MAPOUTBUF’ undeclared here (not in a function)
linux-user/ioctls.h:244:1: error: ‘SOUND_MIXER_ACCESS’ undeclared here (not in a function)


Replace this line :
#include <linux/soundcard.h>
by :
#include <linux/soundcard.h.oss3>
in the linux-user/syscall.c file.
```

# 四、Build opensbi

```bash
git clone https://github.com/riscv-software-src/opensbi.git
cd opensbi/
make CROSS_COMPILE=riscv64-linux-gnu- PLATFORM=generic
```

# 五、Build Busybox

```bash
wget https://busybox.net/downloads/busybox-1.35.0.tar.bz2
tar -jxvf busybox-1.35.0.tar.bz2
cd busybox-1.35.0/
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- menuconfig
vim .config 
```

在.config中添加這句：

```bash
CONFIG_STATIC=y
```

添加完成

```bash
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- install
cd _install 
mkdir proc sys dev etc etc/init.d
touch etc/init.d/rcS
vim etc/init.d/rcS
```

後保存回到busybox-1.35.0目錄

在rcS中添加以下內容：

```bash
#!bin/sh 
mount -t proc none /proc 
mount -t sysfs none /sys 
/sbin/mdev -s
```

添加後保存

接著執行下面兩條指令，這兩條指令需要root權限：

```bash
sudo mknod dev/console c 5 1 
sudo mknod dev/ram b 1 0
```

給rcS文件設置可執行屬性：

```bash
chmod 777 etc/init.d/rcS
find -print0 | cpio -0oH newc | gzip -9 > ../rootfs.img 
```

到此busybox操作完成。

# 六、Build Linux Kernel

```bash
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.9.tar.xz
tar -xvf linux-5.9.tar.xz
cd linux-5.9
```

在內核Makefile的KBUILD_CFLAGS上添加-g選項，然後再執行下面命令：

```bash
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig 
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
```

以上步驟完成後使用gdb調試qemu啟動linux kernel，qemu命令行如下：

```bash
qemu-system-riscv64 \
        -nographic -machine virt \
        -bios  opensbi/build/platform/generic/firmware/fw_dynamic.bin \
        -kernel linux-5.9/arch/riscv/boot/Image \
        -initrd busybox-1.35.0/rootfs.img  \
        -append "root=/dev/ram rdinit=/sbin/init nokaslr" \
        -S \
        -s
```
nokaslr 的核心參數是停用隨機分配 kernel 運作位址的功能

開啟另一個終端，進入剛剛的linux kernel 目錄（該目錄下有vmlinux文件），使用下面命令啟動gdb：

```bash
riscv64-unknown-elf-gdb vmlinux -ex 'target remote localhost:1234'
```

```sh
(gdb) b start_kernel 
Breakpoint 1 at 0xffffffe00000272e
(gdb) continue
Continuing.
Breakpoint 1, 0xffffffe00000272e in start_kernel ()
```

