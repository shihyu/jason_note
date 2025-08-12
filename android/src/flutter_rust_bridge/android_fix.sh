#!/bin/bash

echo "🔧 修復 Android 動態函式庫部署問題"
echo "=================================="

# 檢查 Android 設備連接
if ! adb devices | grep -q "device$"; then
    echo "❌ 沒有檢測到 Android 設備"
    echo "請確保："
    echo "1. Android 設備已連接並啟用 USB 調試"
    echo "2. adb devices 顯示設備"
    exit 1
fi

echo "✅ 檢測到 Android 設備"

# 建置 Rust 函式庫
echo "📦 建置 Rust 函式庫..."
cargo build --release

# 確認函式庫存在
if [ ! -f "target/release/librust_flutter_bridge.so" ]; then
    echo "❌ Rust 函式庫建置失敗"
    exit 1
fi

echo "✅ Rust 函式庫建置成功"

# 建立 Android JNI 目錄結構
echo "📁 建立 Android JNI 目錄結構..."
mkdir -p flutter_app/android/app/src/main/jniLibs/arm64-v8a
mkdir -p flutter_app/android/app/src/main/jniLibs/armeabi-v7a
mkdir -p flutter_app/android/app/src/main/jniLibs/x86_64

# 複製函式庫到所有架構目錄（暫時使用 x86_64 版本）
echo "📦 複製函式庫到 Android JNI 目錄..."
cp target/release/librust_flutter_bridge.so flutter_app/android/app/src/main/jniLibs/x86_64/
cp target/release/librust_flutter_bridge.so flutter_app/android/app/src/main/jniLibs/arm64-v8a/
cp target/release/librust_flutter_bridge.so flutter_app/android/app/src/main/jniLibs/armeabi-v7a/

echo "✅ 函式庫複製完成"

# 檢查設備架構
echo "🔍 檢查設備架構..."
DEVICE_ARCH=$(adb shell getprop ro.product.cpu.abi)
echo "設備架構: $DEVICE_ARCH"

# 推送函式庫到設備的 /data/local/tmp（測試用）
echo "📤 推送函式庫到設備進行測試..."
adb push target/release/librust_flutter_bridge.so /data/local/tmp/
echo "✅ 函式庫推送完成"

echo ""
echo "🎯 修復措施說明："
echo "1. ✅ 已將函式庫複製到所有 Android JNI 目錄"
echo "2. ✅ 已推送函式庫到設備 /data/local/tmp 進行測試"
echo "3. 🔄 現在需要重新建置和安裝 Flutter 應用程式"
echo ""

echo "下一步操作："
echo "cd flutter_app"
echo "flutter clean"
echo "flutter pub get" 
echo "flutter run --debug"