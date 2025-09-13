#!/bin/bash

echo "=== HFT 效能比較 (使用 Guider 分析) ==="
echo ""

# 設定工作目錄 (使用相對路徑)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORK_DIR="$SCRIPT_DIR"
cd $WORK_DIR

# 測試 C++ 版本
echo "測試 C++ HFT 實作..."
echo "================================="

# Build C++ version
cd $WORK_DIR/hft_cpp_example
make clean && make
cd $WORK_DIR

# Start guider top in background for system monitoring
echo 'f0409' | sudo -S python3 $WORK_DIR/guider_tool/guider.py top -o cpp_top.out -I 1 2>/dev/null &
GUIDER_PID=$!
sleep 2

# Run C++ HFT
$WORK_DIR/hft_cpp_example/hft_trading 10 > cpp_output.txt 2>&1

# Stop guider (check if process exists before killing)
if ps -p $GUIDER_PID > /dev/null 2>&1; then
    echo 'f0409' | sudo -S kill -INT $GUIDER_PID 2>/dev/null
fi
sleep 2

echo ""
echo "測試 Rust HFT 實作..."
echo "=================================="

# 編譯 Rust 版本
cd $WORK_DIR/hft_rust_example
cargo build --release
cd $WORK_DIR

# Use the correct Rust binary name
RUST_BIN="$WORK_DIR/hft_rust_example/target/release/hft_rust_example"

# Start guider top in background for system monitoring
echo 'f0409' | sudo -S python3 $WORK_DIR/guider_tool/guider.py top -o rust_top.out -I 1 2>/dev/null &
GUIDER_PID=$!
sleep 2

# Run Rust HFT
$RUST_BIN 10 > rust_output.txt 2>&1

# Stop guider (check if process exists before killing)
if ps -p $GUIDER_PID > /dev/null 2>&1; then
    echo 'f0409' | sudo -S kill -INT $GUIDER_PID 2>/dev/null
fi
sleep 2

echo ""
echo "=== 測試結果 ==="
echo ""
echo "C++ 輸出:"
tail -5 cpp_output.txt
echo ""
echo "Rust 輸出:"
tail -5 rust_output.txt

echo ""
echo "Guider 分析結果已儲存至 cpp_top.out 和 rust_top.out"
echo "所有輸出檔案位於: $WORK_DIR"