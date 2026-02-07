"""YOLO 檢測器"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import cv2
import numpy as np

# 修正 PyTorch 2.10 的 weights_only 預設值問題
# 必須在導入 ultralytics 之前設定
os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = '0'

import torch

# Monkey patch torch.load 以支援舊版模型
_original_torch_load = torch.load

def _patched_torch_load(*args, **kwargs):
    kwargs.setdefault('weights_only', False)
    return _original_torch_load(*args, **kwargs)

torch.load = _patched_torch_load

from ultralytics import YOLO


@dataclass
class Detection:
    """檢測結果

    Attributes:
        bbox: 邊界框 (x1, y1, x2, y2)
        confidence: 置信度分數
        class_id: 類別 ID
        class_name: 類別名稱
    """

    bbox: tuple[float, float, float, float]
    confidence: float
    class_id: int
    class_name: str


class Detector:
    """YOLO 物體檢測器

    使用訓練好的 YOLO 模型進行價格標籤檢測

    Attributes:
        model_path: YOLO 模型路徑
        conf_threshold: 置信度閾值
        model: YOLO 模型實例
    """

    def __init__(self, model_path: str, conf_threshold: float = 0.05) -> None:
        """初始化檢測器

        Args:
            model_path: YOLO 模型文件路徑
            conf_threshold: 置信度閾值（預設 0.05）

        Raises:
            FileNotFoundError: 如果模型文件不存在
        """
        self.model_path = Path(model_path)
        self.conf_threshold = conf_threshold

        if not self.model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 載入模型
        self.model = YOLO(str(self.model_path))

    def detect(self, image_path: str) -> List[Detection]:
        """檢測單張圖片

        Args:
            image_path: 圖片文件路徑

        Returns:
            Detection 列表
        """
        # 執行 YOLO 推理
        results = self.model.predict(
            source=image_path, conf=self.conf_threshold, verbose=False
        )

        # 轉換為 Detection 物件
        detections = []

        for result in results:
            boxes = result.boxes

            for box in boxes:
                bbox = tuple(box.xyxy[0].cpu().numpy().tolist())
                confidence = float(box.conf[0].cpu().numpy())
                class_id = int(box.cls[0].cpu().numpy())
                class_name = result.names[class_id]

                detection = Detection(
                    bbox=bbox,
                    confidence=confidence,
                    class_id=class_id,
                    class_name=class_name,
                )

                detections.append(detection)

        return detections

    def detect_batch(self, image_paths: List[str]) -> Dict[str, List[Detection]]:
        """批次檢測多張圖片

        Args:
            image_paths: 圖片文件路徑列表

        Returns:
            {image_path: [Detection, ...]} 字典
        """
        results = {}

        for img_path in image_paths:
            results[img_path] = self.detect(img_path)

        return results
