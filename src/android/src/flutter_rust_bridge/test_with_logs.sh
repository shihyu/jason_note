#!/bin/bash

echo "🚀 BitoPro Rust-Flutter 測試與日誌監控"
echo "====================================="
echo ""

# 檢查是否有 Android 設備連接
if ! adb devices | grep -q device; then
    echo "❌ 沒有檢測到 Android 設備"
    echo "請確保："
    echo "1. Android 設備已連接並啟用 USB 調試"
    echo "2. adb devices 顯示設備"
    exit 1
fi

echo "✅ 檢測到 Android 設備"

# 建置專案
echo "📦 建置專案..."
make build

# 清除之前的日誌
echo "🧹 清除舊日誌..."
adb logcat -c

# 建立臨時文件來控制進程
TEMP_DIR=$(mktemp -d)
LOGCAT_PID_FILE="$TEMP_DIR/logcat.pid"

# 清理函數
cleanup() {
    echo ""
    echo "🛑 停止監控..."
    if [ -f "$LOGCAT_PID_FILE" ]; then
        LOGCAT_PID=$(cat "$LOGCAT_PID_FILE")
        kill "$LOGCAT_PID" 2>/dev/null
        rm -f "$LOGCAT_PID_FILE"
    fi
    rm -rf "$TEMP_DIR"
    echo "✅ 清理完成"
}

# 設置信號處理
trap cleanup EXIT INT TERM

# 在背景執行 logcat 監控
echo "🔍 開始監控 BitoPro 日誌..."
(
    adb logcat -s BitoPro:V -v time | while read line; do
        echo "[LOG] $line"
    done
) &
echo $! > "$LOGCAT_PID_FILE"

echo "📱 啟動 Flutter 應用程式..."
echo "請在手機上測試各個按鈕，日誌會即時顯示在下方："
echo "----------------------------------------"

# 啟動 Flutter 應用程式
cd flutter_app
flutter run --debug

# Flutter 應用程式退出後會自動清理