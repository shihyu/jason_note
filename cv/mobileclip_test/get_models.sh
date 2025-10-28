#!/usr/bin/env bash
# 只下載 S0, S1, S2 模型

mkdir -p checkpoints

echo "下載 MobileCLIP 模型..."
echo "========================================"

# S0
if [ ! -f "checkpoints/mobileclip_s0.pt" ]; then
    echo "下載 MobileCLIP-S0..."
    wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s0.pt -P checkpoints
else
    echo "✓ S0 已存在"
fi

# S1
if [ ! -f "checkpoints/mobileclip_s1.pt" ]; then
    echo "下載 MobileCLIP-S1..."
    wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s1.pt -P checkpoints
else
    echo "✓ S1 已存在"
fi

# S2
if [ ! -f "checkpoints/mobileclip_s2.pt" ]; then
    echo "下載 MobileCLIP-S2..."
    wget https://docs-assets.developer.apple.com/ml-research/datasets/mobileclip/mobileclip_s2.pt -P checkpoints
else
    echo "✓ S2 已存在"
fi

echo "========================================"
echo "模型下載完成！"
ls -lh checkpoints/
