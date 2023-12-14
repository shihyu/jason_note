## RISC-V Linux kernel debug 环境搭建

https://blog.csdn.net/m0_43422086/article/details/125276723

# 一、目的

搭建qemu-gdb risc-v64 linux kernel的调试环境。

# 二、准备工作

​    Build Ninja 和riscv-toolchain

​    首先安装必要的库(这是编译riscv toolchain必须安装的库文件)

```bash
sudo apt update 
sudo apt upgrade 
sudo apt install git \ 
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
1234567891011121314151617181920212223242526
```

## ①Build Ninja

```bash
git clone https://github.com/ninja-build/ninja.git
cd ninja
cmake -Bbuild-cmake
cmake --build build-cmake
12345
```

然后在.bashrc中添加ninja/build-cmake目录

编辑.bashrc如下：

```bash
export PATH=$PATH:/home/kali/Desktop/riscv-debug/ninja/build-cmake
12
```

## ②Build riscv-gnu-compiler toolchain and debug gdb

```bash
wget https://static.dev.sifive.com/dev-tools/freedom-tools/v2020.12/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
tar -xzvf riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14.tar.gz
mv riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14  riscv64-unknown-elf-toolchain
1234
```

接着编辑~/.bashrc,加入下面的环境变量：

```bash
export PATH=$PATH:/home/kali/Desktop/riscv-debug/riscv64-unknown-elf-toolchain/bin
12
```

## ③命令行安装gcc-riscv64-linux-gnu-

```bash
sudo apt install binutils-riscv64-linux-gnu $ sudo apt install gcc-riscv64-linux-gnu
12
```

# 三、Build Qemu

```bash
git clone https://gitlab.com/qemu-project/qemu.git
cd qemu
git submodule init
git submodule update --recursive
./configure
make
1234567
```

# 四、Build opensbi

```bash
git clone https://github.com/riscv-software-src/opensbi.git
cd opensbi/
make CROSS_COMPILE=riscv64-linux-gnu- PLATFORM=generic
1234
```

# 五、Build Busybox

```bash
wget https://busybox.net/downloads/busybox-1.35.0.tar.bz2
tar -jxvf busybox-1.35.0.tar.bz2
cd busybox-1.35.0/
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- menuconfig
vim .config 
1234567
```

在.config中添加这句：

```bash
CONFIG_STATIC=y
12
```

添加完成

```bash
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- install
cd _install 
mkdir proc sys dev etc etc/init.d
touch etc/init.d/rcS
vim etc/init.d/rcS
1234567
```

后保存回到busybox-1.35.0目录

在rcS中添加以下内容：

```bash
#!bin/sh 
mount -t proc none /proc 
mount -t sysfs none /sys 
/sbin/mdev -s
12345
```

添加后保存

接着执行下面两条指令，这两条指令需要root权限：

```bash
sudo mknod dev/console c 5 1 
sudo mknod dev/ram b 1 0
123
```

给rcS文件设置可执行属性：

```bash
chmod 777 etc/init.d/rcS
find -print0 | cpio -0oH newc | gzip -9 > ../rootfs.img 
123
```

到此busybox操作完成。

# 六、Build Linux Kernel

```bash
wget https://mirrors.edge.kernel.org/pub/linux/kernel/v5.x/linux-5.9.tar.xz
tar -xvf linux-5.9.tar.xz
cd linux-5.9.tar.xz 
1234
```

在内核Makefile的KBUILD_CFLAGS上添加-g选项，然后再执行下面命令：

```bash
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- defconfig 
make ARCH=riscv CROSS_COMPILE=riscv64-linux-gnu- -j $(nproc)
123
```

以上步骤完成后使用gdb调试qemu启动linux kernel，qemu命令行如下：

```bash
qemu-system-riscv64 \
        -nographic -machine virt \
        -bios  /home/kali/Desktop/riscv-debug/opensbi/build/platform/generic/firmware/fw_dynamic.bin \
        -kernel /home/kali/Desktop/riscv-debug/linux-5.9/arch/riscv/boot/Image \
        -initrd /home/kali/Desktop/riscv-debug/busybox-1.35.0/rootfs.img  \
        -append "root=/dev/ram rdinit=/sbin/init" \
        -S \
        -s
123456789
```

开启另一个终端，进入刚刚的linux kernel 目录（该目录下有vmlinux文件），使用下面命令启动gdb：

```bash
riscv64-unknown-elf-gdb vmlinux -ex 'target remote localhost:1234'
```