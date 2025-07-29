# Supervision 電腦視覺套件完整指南

## 簡介

Supervision 是 Roboflow 開源的 Python 套件，專門用於電腦視覺任務。它提供了豐富的工具來處理物件偵測、追蹤、標註和視覺化等功能。

## 安裝步驟

### 基本安裝
```bash
pip install supervision
```

### 完整功能安裝
```bash
pip install supervision[desktop]  # 包含額外的視覺化工具
```

### 相關依賴
```bash
pip install ultralytics opencv-python numpy
```

## 基本範例

### 1. 物件偵測 + 標註視覺化

```python
import supervision as sv
import cv2
from ultralytics import YOLO

# 載入預訓練的 YOLO 模型
model = YOLO('yolov8n.pt')

# 讀取圖片
image = cv2.imread('your_image.jpg')

# 進行物件偵測
results = model(image)[0]

# 將結果轉換為 supervision 格式
detections = sv.Detections.from_ultralytics(results)

# 創建標註器
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# 準備標籤
labels = [
    f"{results.names[class_id]} {confidence:.2f}"
    for class_id, confidence in zip(detections.class_id, detections.confidence)
]

# 在圖片上標註
annotated_image = box_annotator.annotate(image.copy(), detections)
annotated_image = label_annotator.annotate(annotated_image, detections, labels)

# 顯示結果
cv2.imshow('Detection Result', annotated_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

### 2. 影片物件追蹤

```python
import supervision as sv
import cv2
from ultralytics import YOLO

# 載入模型
model = YOLO('yolov8n.pt')

# 創建追蹤器
tracker = sv.ByteTracker()

# 創建標註器
box_annotator = sv.BoxAnnotator()
label_annotator = sv.LabelAnnotator()

# 開啟影片
cap = cv2.VideoCapture('your_video.mp4')

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 物件偵測
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    
    # 物件追蹤
    detections = tracker.update_with_detections(detections)
    
    # 準備標籤（包含追蹤ID）
    labels = [
        f"#{tracker_id} {results.names[class_id]} {confidence:.2f}"
        for class_id, confidence, tracker_id 
        in zip(detections.class_id, detections.confidence, detections.tracker_id)
    ]
    
    # 標註畫面
    annotated_frame = box_annotator.annotate(frame.copy(), detections)
    annotated_frame = label_annotator.annotate(annotated_frame, detections, labels)
    
    # 顯示結果
    cv2.imshow('Tracking', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

### 3. 進階功能：區域監控

```python
import supervision as sv
import cv2
import numpy as np
from ultralytics import YOLO

# 載入模型
model = YOLO('yolov8n.pt')

# 定義監控區域（多邊形頂點）
polygon = np.array([
    [100, 100],
    [300, 100], 
    [300, 300],
    [100, 300]
])

# 創建監控區域
zone = sv.PolygonZone(polygon=polygon)

# 創建各種標註器
box_annotator = sv.BoxAnnotator()
zone_annotator = sv.PolygonZoneAnnotator(zone=zone)
label_annotator = sv.LabelAnnotator()

# 開啟攝影機或影片
cap = cv2.VideoCapture(0)  # 0 為攝影機，或用影片路徑

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # 物件偵測
    results = model(frame)[0]
    detections = sv.Detections.from_ultralytics(results)
    
    # 只保留特定類別（例如：人）
    detections = detections[detections.class_id == 0]  # 0 = person in COCO
    
    # 檢查物件是否在區域內
    mask = zone.trigger(detections)
    detections_in_zone = detections[mask]
    
    # 標註
    annotated_frame = box_annotator.annotate(frame.copy(), detections_in_zone)
    annotated_frame = zone_annotator.annotate(annotated_frame)
    
    # 顯示區域內物件數量
    zone_text = f"Objects in zone: {len(detections_in_zone)}"
    cv2.putText(annotated_frame, zone_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow('Zone Monitoring', annotated_frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

## 快速開始步驟

### 1. 準備環境
```bash
pip install supervision ultralytics opencv-python
```

### 2. 下載模型
- YOLO 模型會自動下載
- 或使用自己訓練的模型

### 3. 準備素材
- 圖片：`your_image.jpg`
- 影片：`your_video.mp4`
- 或使用攝影機

### 4. 執行範例
- 從簡單的物件偵測開始
- 逐步嘗試追蹤和區域監控

## 核心組件

### 偵測結果處理
- `sv.Detections`: 統一的偵測結果格式
- 支援多種模型框架轉換：
  - `from_ultralytics()`
  - `from_detectron2()`
  - `from_mmdetection()`

### 標註器（Annotators）
- `BoxAnnotator`: 邊界框標註
- `LabelAnnotator`: 文字標籤標註
- `MaskAnnotator`: 分割遮罩標註
- `PolygonZoneAnnotator`: 區域標註

### 追蹤器（Trackers）
- `ByteTracker`: 高效能多物件追蹤
- 支援跨幀物件關聯

### 區域監控
- `PolygonZone`: 多邊形監控區域
- `LineZone`: 線性監控區域
- 支援物件計數和統計

## 主要特色

### 🚀 簡化整合
- 與各種深度學習框架無縫整合
- 統一的 API 介面設計

### 🎨 豐富標註
- 多種視覺化工具
- 可自定義樣式和顏色

### ⚡ 高效能
- 優化的計算效能
- 支援即時處理

### 🛠️ 易於使用
- 直觀的 API 設計
- 豐富的文檔和範例

## 實際應用場景

### 安全監控
- 入侵偵測
- 人員計數
- 異常行為識別

### 交通監控
- 車輛追蹤
- 違規偵測
- 流量統計

### 零售分析
- 顧客行為分析
- 商品識別
- 排隊檢測

### 工業檢測
- 產品品質控制
- 設備狀態監控
- 安全合規檢查

## 進階功能

### 資料集工具
```python
# 資料集統計
dataset = sv.DetectionDataset.from_yolo(...)
dataset.split(train=0.7, val=0.2, test=0.1)
```

### 影片處理
```python
# 影片資訊取得
video_info = sv.VideoInfo.from_video_path("video.mp4")

# 影片寫入
with sv.VideoSink(target_path="output.mp4", video_info=video_info) as sink:
    for frame in sv.get_video_frames_generator(source_path="input.mp4"):
        # 處理frame
        sink.write_frame(annotated_frame)
```

### 統計和分析
```python
# 物件計數
counter = sv.LineZoneAnnotator(line_zone)
count = counter.trigger(detections)
```

## 資源連結

- 📖 [官方文檔](https://supervision.roboflow.com/)
- 🔗 [GitHub 倉庫](https://github.com/roboflow/supervision)
- 📺 [教學影片](https://www.youtube.com/roboflow)
- 💬 [社群討論](https://discuss.roboflow.com/)

## 結語

Supervision 是一個功能強大且易於使用的電腦視覺工具包，無論是初學者還是專業開發者都能快速上手。通過其豐富的功能和直觀的 API，您可以輕鬆構建各種電腦視覺應用。

立即開始您的電腦視覺專案吧！
