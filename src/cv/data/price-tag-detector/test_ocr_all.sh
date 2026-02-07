#!/bin/bash
# 測試改進的 OCR 在所有影片上的效果

cd /home/shihyu/price-tag-detector

echo "======================================================================"
echo "測試改進的 OCR 引擎"
echo "======================================================================"
echo ""

# Video3 (最小，先測試)
echo "=== Video3 (19 張圖片) ==="
uv run python cli/detect_v2.py \
    --input data/images/video3 \
    --output data/detections_v2/video3 \
    2>&1 | grep -A 20 "檢測完成"
echo ""

# Video2 (中等大小)
echo "=== Video2 (205 張圖片) ==="
uv run python cli/detect_v2.py \
    --input data/images/video2 \
    --output data/detections_v2/video2 \
    2>&1 | grep -A 20 "檢測完成"
echo ""

# Video1 (最大)
echo "=== Video1 (437 張圖片) ==="
uv run python cli/detect_v2.py \
    --input data/images/video1 \
    --output data/detections_v2/video1 \
    2>&1 | grep -A 20 "檢測完成"
echo ""

echo "======================================================================"
echo "所有測試完成！"
echo "======================================================================"
echo ""
echo "檢測結果保存在:"
echo "  - data/detections_v2/video1/"
echo "  - data/detections_v2/video2/"
echo "  - data/detections_v2/video3/"
echo ""
echo "可以隨機查看幾張檢測結果確認效果"
