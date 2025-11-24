#!/bin/bash

set -e  # 遇到錯誤立即停止

echo "========================================"
echo "  完整編譯和測試流程"
echo "========================================"
echo ""

# 1. 清理並建立 build 目錄
echo "[1/5] 建立 build 目錄..."
cd ..
rm -rf build
mkdir build
cd build

# 2. 執行 cmake (Debug 模式)
echo ""
echo "[2/5] 執行 cmake (Debug 模式)..."
cmake -DCMAKE_BUILD_TYPE=Debug ..
echo "CMAKE_BUILD_TYPE=Debug"

# 3. 編譯
echo ""
echo "[3/5] 編譯專案..."
make -j8 2>&1 | tail -20

# 4. 回到 test_gdb 目錄並編譯測試程式
echo ""
echo "[4/5] 編譯測試程式..."
cd ../test_gdb
make clean
make

# 5. 執行 gdb 測試
echo ""
echo "[5/5] 執行 gdb 測試..."
echo ""
./test_final.sh

echo ""
echo "========================================"
echo "  測試完成!"
echo "========================================"
