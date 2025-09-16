#!/bin/bash

# DPDK + GDB 調試腳本（最簡潔版本）

DPDK_LIB_PATH="/home/shihyu/github/dpdk/build/lib"

echo "========================================="
echo "       DPDK + GDB Debug Environment"
echo "========================================="
echo ""
echo "Library Path: $DPDK_LIB_PATH"
echo ""
echo "Starting GDB with DPDK program..."
echo "-----------------------------------------"

# 啟動 GDB 並自動設置環境和斷點
sudo LD_LIBRARY_PATH=$DPDK_LIB_PATH gdb \
    -ex "set environment LD_LIBRARY_PATH=$DPDK_LIB_PATH" \
    -ex "break main" \
    -ex "break rte_eal_init" \
    -ex "break port_init" \
    -ex "break lcore_main" \
    -ex "echo \n" \
    -ex "echo Breakpoints set: main, rte_eal_init, port_init, lcore_main\n" \
    -ex "echo Run with: run -l 0 -n 1 --no-pci --no-huge --no-shconf\n" \
    -ex "echo \n" \
    build/test_dpdk