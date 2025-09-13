#!/bin/bash

echo "=== Rust HFT 效能分析 (使用 Guider) ==="
echo ""

# 編譯程式
echo "編譯 Rust HFT 程式中..."
cargo build --release
echo ""

# 執行並監控
echo "1. 執行程式並監控 CPU 和記憶體..."
./target/release/hft_rust_example 10 &
PID=$!
sleep 1

# 取得基本資訊
echo "程序 PID: $PID"
ps -p $PID -o pid,ppid,cmd,rss,vsz,%cpu,%mem
echo ""

# 監控 CPU 使用率
echo "2. CPU 使用率監控..."
timeout 5 top -b -p $PID -d 1 | grep $PID | head -5
echo ""

# 檢查記憶體使用
echo "3. 記憶體分析..."
cat /proc/$PID/status | grep -E "VmSize|VmRSS|VmHWM|Threads"
echo ""

# 監控執行緒活動
echo "4. 執行緒活動..."
ls -la /proc/$PID/task/ 2>/dev/null | wc -l
echo "執行緒數量: $(ls /proc/$PID/task/ 2>/dev/null | wc -l)"
echo ""

# 等待程式完成
wait $PID

echo "分析完成！"