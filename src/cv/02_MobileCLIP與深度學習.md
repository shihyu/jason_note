# MobileCLIP 與深度學習

> CLIP 模型、MobileCLIP 部署與電腦視覺套件。

## 🎯 MobileCLIP 完整指南

### 學習與使用
- [MobileCLIP 完整學習指南](MobileCLIP_完整指南.md)
- [MobileCLIP 完整使用指南](mobileclip-complete-guide.md)
- [MobileCLIP 與深度學習框架的關係](mobileclip-frameworks-comparison.md)

核心特點：
- 輕量化 CLIP 模型
- 適合移動設備部署
- 多模態（圖像+文字）
- 零樣本分類能力

## 📱 Mobile 部署

### Android 部署
- [MobileCLIP Android 完整部署指南](MobileCLIP_Android_部署指南.md)

部署流程：
1. 模型轉換（ONNX/TFLite）
2. Android 整合
3. 性能優化
4. 實際應用案例

## 🛠️ 電腦視覺工具

### Supervision 套件
- [Supervision 電腦視覺套件完整指南](supervision.md)

功能特點：
- 物件偵測後處理
- 物件追蹤
- 標註工具
- 視覺化工具

## 💡 CLIP 技術詳解

### CLIP 原理
1. **對比學習**
   - 圖像-文字配對
   - 大規模預訓練
   - 零樣本遷移學習

2. **架構設計**
   - Image Encoder (Vision Transformer)
   - Text Encoder (Transformer)
   - 對比損失函數

### MobileCLIP 優化
1. **模型壓縮**
   - 知識蒸餾
   - 網路架構搜索（NAS）
   - 量化技術

2. **性能優化**
   - 減少參數量
   - 降低計算複雜度
   - 保持準確度

## 🚀 實戰應用

### 零樣本分類
```python
# 圖像分類（無需訓練）
texts = ['a photo of a cat', 'a photo of a dog']
predictions = model.predict(image, texts)
```

### 圖像檢索
```python
# 以文搜圖
query = "red car on the street"
results = search_images(query, image_database)
```

### 物件偵測增強
```python
# 結合 YOLO + CLIP
detections = yolo(image)
for det in detections:
    label = clip.classify(det.crop, class_names)
```

## 🔧 Supervision 實用功能

### 物件追蹤
- ByteTrack
- DeepSORT
- 多目標追蹤

### 視覺化
- Bounding Box
- Mask
- Trajectory
- Heatmap

**最後更新**: 2025-12-01
