#!/bin/bash

echo "=== Building C HFT Examples ==="
make clean
make

echo -e "\n=== Running Trading System Benchmark ==="
./hft_trading

echo -e "\n=== Running Advanced Performance Test ==="
./hft_advanced_test

echo -e "\n=== Running C vs C++ Comparison ==="
cd ..
./hft_c_example/compare_benchmark

# Optional: Run with performance profiling
if command -v perf &> /dev/null; then
    echo -e "\n=== Performance Analysis (requires sudo) ==="
    echo "Run 'make perf' to analyze with perf"
fi

# Optional: Run with valgrind for memory analysis
if command -v valgrind &> /dev/null; then
    echo -e "\n=== Memory Analysis ==="
    echo "Running valgrind on hft_trading..."
    valgrind --leak-check=full --show-leak-kinds=all ./hft_c_example/hft_trading 2>&1 | grep -A5 "HEAP SUMMARY"
fi