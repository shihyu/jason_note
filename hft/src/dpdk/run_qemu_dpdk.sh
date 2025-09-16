#!/bin/bash

# QEMU + DPDK + GDB 環境設置腳本（最簡潔版本）

echo "========================================="
echo "    QEMU + DPDK + GDB Test Environment"
echo "========================================="
echo ""

# 1. 設置 TAP 網路介面
setup_network() {
    echo "[1] Setting up TAP network interface..."
    sudo ip link add dev tap0 type tap 2>/dev/null || echo "    TAP0 already exists"
    sudo ip link set dev tap0 up
    sudo ip addr add 192.168.100.1/24 dev tap0 2>/dev/null || echo "    IP already assigned"
    echo "    ✓ Network configured"
}

# 2. 準備測試程序
prepare_test() {
    echo ""
    echo "[2] Preparing test program..."

    # 創建簡單的 initramfs
    mkdir -p /tmp/dpdk_test/bin
    cp build/test_dpdk /tmp/dpdk_test/

    # 創建 init 腳本
    cat > /tmp/dpdk_test/init << 'EOF'
#!/bin/sh
echo "DPDK Test Environment in QEMU"
export LD_LIBRARY_PATH=/lib
/test_dpdk -l 0 -n 1 --no-pci --no-huge --no-shconf
/bin/sh
EOF
    chmod +x /tmp/dpdk_test/init

    # 複製必要的庫文件
    mkdir -p /tmp/dpdk_test/lib
    cp build/lib/*.so* /tmp/dpdk_test/lib/

    # 打包 initramfs
    (cd /tmp/dpdk_test && find . | cpio -o -H newc | gzip > /tmp/dpdk_initrd.gz)
    echo "    ✓ Test program prepared"
}

# 3. 啟動 QEMU
start_qemu() {
    echo ""
    echo "[3] Starting QEMU with GDB server..."
    echo ""
    echo "╔══════════════════════════════════════════════════════════╗"
    echo "║  QEMU is starting with GDB server on port 1234          ║"
    echo "║                                                          ║"
    echo "║  In another terminal, connect with:                     ║"
    echo "║  $ gdb build/test_dpdk                                  ║"
    echo "║  (gdb) target remote :1234                              ║"
    echo "║  (gdb) continue                                         ║"
    echo "╚══════════════════════════════════════════════════════════╝"
    echo ""

    # 使用簡單的 QEMU 配置（不需要完整系統）
    qemu-system-x86_64 \
        -m 512 \
        -smp 2 \
        -netdev tap,id=net0,ifname=tap0,script=no,downscript=no \
        -device virtio-net-pci,netdev=net0,mac=52:54:00:12:34:56 \
        -kernel /boot/vmlinuz-$(uname -r) \
        -initrd /tmp/dpdk_initrd.gz \
        -append "console=ttyS0 init=/init quiet" \
        -nographic \
        -gdb tcp::1234 \
        -S  # 暫停等待 GDB 連接
}

# 4. 清理函數
cleanup() {
    echo ""
    echo "Cleaning up..."
    sudo ip link del tap0 2>/dev/null
    rm -rf /tmp/dpdk_test /tmp/dpdk_initrd.gz
    echo "Done"
}

# 捕獲退出信號
trap cleanup EXIT

# 執行主流程
setup_network
prepare_test
start_qemu