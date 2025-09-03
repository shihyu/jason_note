#!/bin/bash

echo "🔍 BitoPro Logcat Monitor"
echo "========================="
echo "監控 BitoPro 標籤的日誌輸出..."
echo "按 Ctrl+C 停止監控"
echo ""

# 清除之前的日誌
adb logcat -c

# 監控 BitoPro 標籤
echo "[$(date '+%Y-%m-%d %H:%M:%S')] 開始監控 BitoPro 日誌..."
adb logcat -s BitoPro:V -v time | while read line
do
    echo "[$(date '+%H:%M:%S')] $line"
done