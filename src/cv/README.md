# 電腦視覺完整指南

> Computer Vision - 從影像處理到深度學習應用。

## 📊 文檔統計

- **核心文檔**: 13 個
- **主題分類**: 3 個領域
- **適用對象**: CV 工程師、影像處理開發者

---

## 🗂️ 主題分類

### 📗 影像處理基礎

#### [01. 影像處理核心概念](01_影像處理核心概念.md)
**頻率域、基礎概念** | 難度: ⭐⭐⭐

核心內容：
- 影像處理易混淆概念
- 頻率域的直覺理解
- 基礎理論與實踐

**適合**: CV 新手、需要鞏固基礎

---

### 📘 深度學習應用

#### [02. MobileCLIP 與深度學習](02_MobileCLIP與深度學習.md)
**CLIP、部署、框架** | 難度: ⭐⭐⭐⭐

核心內容：
- MobileCLIP 完整學習指南
- MobileCLIP 完整使用指南
- MobileCLIP Android 部署
- MobileCLIP 與深度學習框架關係
- Supervision 電腦視覺套件

**適合**: 深度學習開發者、Mobile AI

---

### 📙 實戰應用

#### [03. 實戰應用與技術方案](03_實戰應用與技術方案.md)
**AR、深度感知、串流** | 難度: ⭐⭐⭐⭐

核心內容：
- AR 眼鏡辨別詐騙技術
- AR 眼鏡面相分析技術方案
- 深度感知技術與裝置
- 雙目立體視覺基線選擇
- 串流應用與相關技術

**適合**: 實戰應用開發、AR/VR 開發

---

## 🎯 學習路徑建議

### 新手路徑（2-4週）

**第一階段：基礎概念**
1. [影像處理核心概念](01_影像處理核心概念.md)
   - 理解頻率域
   - 掌握基礎概念
   - 避免常見誤解

**第二階段：工具實踐**
1. 使用 OpenCV 基礎操作
2. 實作簡單影像處理
3. 理解濾波器原理

---

### 進階路徑（1-3個月）

**深度學習應用**
1. [MobileCLIP 與深度學習](02_MobileCLIP與深度學習.md)
   - 學習 CLIP 模型原理
   - MobileCLIP 部署
   - Supervision 套件使用

**實戰項目**
1. [實戰應用與技術方案](03_實戰應用與技術方案.md)
   - AR 應用開發
   - 深度感知系統
   - 串流處理

---

### 專家路徑（持續學習）

**前沿技術**
1. Transformer in Vision
2. NeRF 與 3D 重建
3. 實時視覺系統

**生產級部署**
1. 模型優化與量化
2. 邊緣設備部署
3. 高性能推理

---

## 💡 使用說明

### 學習影像處理基礎
→ [影像處理核心概念](01_影像處理核心概念.md)

### 深度學習模型部署
→ [MobileCLIP 與深度學習](02_MobileCLIP與深度學習.md)

### AR/VR 實戰應用
→ [實戰應用與技術方案](03_實戰應用與技術方案.md)

---

## 🔗 相關資源

### 其他章節
- [機器學習 ML](../ml/) - 深度學習基礎
- [Python 程式設計](../python/) - OpenCV Python
- [C++ 程式設計](../c++/) - OpenCV C++

### 外部資源
- [OpenCV Documentation](https://docs.opencv.org/)
- [PyTorch Vision](https://pytorch.org/vision/stable/index.html)
- [Supervision GitHub](https://github.com/roboflow/supervision)
- [MobileCLIP Paper](https://arxiv.org/abs/2311.17049)

---

## 🚀 快速開始

### OpenCV 基礎

```python
import cv2
import numpy as np

# 讀取圖片
img = cv2.imread('image.jpg')

# 轉換色彩空間
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# 邊緣檢測
edges = cv2.Canny(gray, 100, 200)

# 顯示結果
cv2.imshow('Edges', edges)
cv2.waitKey(0)
```

### MobileCLIP 使用

```python
from PIL import Image
import torch
from mobileclip import get_model, get_tokenizer

# 載入模型
model = get_model('mobileclip_s0')
tokenizer = get_tokenizer()

# 準備圖片和文字
image = Image.open('image.jpg')
texts = ['a cat', 'a dog', 'a bird']

# 推理
with torch.no_grad():
    image_features = model.encode_image(image)
    text_features = model.encode_text(texts)

    # 計算相似度
    similarity = (image_features @ text_features.T).softmax(dim=-1)
    print(similarity)
```

### Supervision 物件追蹤

```python
import supervision as sv
from ultralytics import YOLO

# 載入模型
model = YOLO('yolov8n.pt')

# 追蹤器
tracker = sv.ByteTrack()

# 處理影片
for frame in frames:
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    detections = tracker.update_with_detections(detections)
```

---

**最後更新**: 2025-12-01
**維護狀態**: ✅ 活躍更新
**貢獻**: 歡迎補充與修正
