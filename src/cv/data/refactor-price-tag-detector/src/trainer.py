"""YOLO 模型訓練器"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import torch

# Monkey patch for PyTorch weights_only issue
_original_load = torch.load


def _patched_load(*args, **kwargs):
    if "weights_only" not in kwargs:
        kwargs["weights_only"] = False
    return _original_load(*args, **kwargs)


torch.load = _patched_load

from ultralytics import YOLO


@dataclass
class TrainingConfig:
    """訓練配置

    Attributes:
        data_yaml: 資料集配置文件路徑
        epochs: 訓練輪數
        batch_size: 批次大小
        img_size: 圖片大小
        base_model: 基礎模型（預設 'yolov8n.pt'）
        project: 輸出專案目錄
        name: 訓練名稱
        patience: 早停耐心值
    """

    data_yaml: str
    epochs: int = 50
    batch_size: int = 8
    img_size: int = 640
    base_model: str = "yolov8n.pt"
    project: str = "runs/train"
    name: str = "price_tag_detector"
    patience: int = 50


@dataclass
class ValidationMetrics:
    """驗證指標

    Attributes:
        map50: mAP@0.5
        map50_95: mAP@0.5:0.95
        precision: 精確度
        recall: 召回率
    """

    map50: float
    map50_95: float
    precision: float
    recall: float


class Trainer:
    """YOLO 模型訓練器

    使用 Ultralytics YOLO 進行模型訓練

    Attributes:
        config: 訓練配置
        model: YOLO 模型實例
    """

    def __init__(self, config: TrainingConfig) -> None:
        """初始化訓練器

        Args:
            config: 訓練配置

        Raises:
            FileNotFoundError: 如果資料集配置文件不存在
        """
        self.config = config

        if not Path(config.data_yaml).exists():
            raise FileNotFoundError(f"資料集配置文件不存在: {config.data_yaml}")

        # 載入基礎模型
        self.model = YOLO(config.base_model)

    def train(self) -> str:
        """訓練模型

        Returns:
            最佳模型路徑
        """
        print(f"\n{'='*60}")
        print("開始訓練 YOLO 模型")
        print(f"{'='*60}")
        print(f"配置：")
        print(f"  - 資料集: {self.config.data_yaml}")
        print(f"  - Epochs: {self.config.epochs}")
        print(f"  - Batch size: {self.config.batch_size}")
        print(f"  - Image size: {self.config.img_size}")
        print(f"  - 基礎模型: {self.config.base_model}")
        print(f"{'='*60}\n")

        # 訓練模型
        results = self.model.train(
            data=self.config.data_yaml,
            epochs=self.config.epochs,
            batch=self.config.batch_size,
            imgsz=self.config.img_size,
            project=self.config.project,
            name=self.config.name,
            patience=self.config.patience,
            save=True,
            plots=True,
            verbose=True,
            exist_ok=True,
        )

        # 獲取最佳模型路徑
        best_model_path = Path(self.config.project) / self.config.name / "weights" / "best.pt"

        print(f"\n{'='*60}")
        print("訓練完成！")
        print(f"{'='*60}")
        print(f"最佳模型: {best_model_path}")
        print(f"{'='*60}\n")

        return str(best_model_path)

    def validate(self) -> ValidationMetrics:
        """驗證模型

        Returns:
            驗證指標
        """
        print("\n驗證模型...")

        metrics = self.model.val(data=self.config.data_yaml)

        print(f"\n{'='*60}")
        print("驗證結果：")
        print(f"{'='*60}")
        print(f"mAP50:         {metrics.box.map50:.4f} ({metrics.box.map50*100:.2f}%)")
        print(f"mAP50-95:      {metrics.box.map:.4f} ({metrics.box.map*100:.2f}%)")
        print(f"Precision:     {metrics.box.mp:.4f} ({metrics.box.mp*100:.2f}%)")
        print(f"Recall:        {metrics.box.mr:.4f} ({metrics.box.mr*100:.2f}%)")
        print(f"{'='*60}\n")

        return ValidationMetrics(
            map50=float(metrics.box.map50),
            map50_95=float(metrics.box.map),
            precision=float(metrics.box.mp),
            recall=float(metrics.box.mr),
        )
