"""測試 YOLO 檢測器"""

import numpy as np
import pytest
from pathlib import Path

from src.detector import Detector, Detection


class TestDetector:
    """測試 Detector 類別"""

    @pytest.fixture
    def model_path(self) -> str:
        """模型路徑"""
        return "data/models/best.pt"

    @pytest.fixture
    def detector(self, model_path: str) -> Detector:
        """創建檢測器實例"""
        model_file = Path(model_path)
        if not model_file.exists():
            pytest.skip(f"模型文件不存在: {model_path}")

        return Detector(model_path=model_path, conf_threshold=0.05)

    def test_model_loading(self, detector: Detector) -> None:
        """測試模型載入"""
        assert detector.model is not None, "模型應該成功載入"

    def test_detect_returns_list(self, detector: Detector, tmp_path: Path) -> None:
        """測試 detect 返回 Detection 列表"""
        # 創建假圖片
        img_path = tmp_path / "test.jpg"
        img = np.ones((640, 640, 3), dtype=np.uint8) * 255
        import cv2

        cv2.imwrite(str(img_path), img)

        # 執行檢測
        detections = detector.detect(str(img_path))

        # 驗證返回類型
        assert isinstance(detections, list), "應該返回列表"
        assert all(isinstance(d, Detection) for d in detections), "所有元素應該是 Detection"

    def test_detection_attributes(self, detector: Detector, tmp_path: Path) -> None:
        """測試 Detection 物件屬性"""
        # 創建假圖片
        img_path = tmp_path / "test.jpg"
        img = np.ones((640, 640, 3), dtype=np.uint8) * 255
        import cv2

        cv2.imwrite(str(img_path), img)

        detections = detector.detect(str(img_path))

        for detection in detections:
            assert hasattr(detection, "bbox"), "應該有 bbox 屬性"
            assert hasattr(detection, "confidence"), "應該有 confidence 屬性"
            assert hasattr(detection, "class_id"), "應該有 class_id 屬性"
            assert isinstance(detection.bbox, tuple), "bbox 應該是 tuple"
            assert len(detection.bbox) == 4, "bbox 應該有 4 個元素"
