#!/bin/bash

echo "======================================"
echo "開始完整測試流程"
echo "======================================"

# 清理並編譯
echo ""
echo ">>> Step 1: 清理舊檔案"
make clean

echo ""
echo ">>> Step 2: 編譯專案"
make all

echo ""
echo ">>> Step 3: 執行程式測試"
make test

echo ""
echo ">>> Step 4: 檢查連結資訊"
make inspect

echo ""
echo "======================================"
echo "測試完成!"
echo "======================================"
