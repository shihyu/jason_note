#!/bin/bash

# 創建TAP介面以供QEMU使用
echo "Setting up TAP interface..."
sudo ip link add dev tap0 type tap
sudo ip link set dev tap0 up
sudo ip addr add 192.168.100.1/24 dev tap0

# 創建QEMU硬碟映像檔（如果不存在）
if [ ! -f dpdk_test.img ]; then
    echo "Creating disk image..."
    qemu-img create -f qcow2 dpdk_test.img 10G
fi

# 啟動QEMU與GDB server
echo "Starting QEMU with GDB server on port 1234..."
echo "Use 'gdb build/test_dpdk' and 'target remote :1234' to connect"

qemu-system-x86_64 \
    -enable-kvm \
    -cpu host \
    -m 4096 \
    -smp 4 \
    -drive file=dpdk_test.img,if=virtio \
    -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
    -device virtio-net-pci,netdev=net0 \
    -netdev tap,id=net1,ifname=tap1,script=no,downscript=no,vhost=on \
    -device virtio-net-pci,netdev=net1 \
    -kernel /boot/vmlinuz-$(uname -r) \
    -append "root=/dev/vda console=ttyS0 hugepages=512" \
    -initrd /boot/initrd.img-$(uname -r) \
    -nographic \
    -gdb tcp::1234 \
    -S  # 暫停執行，等待GDB連接