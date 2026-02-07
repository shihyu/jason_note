"""測試 OCR 引擎"""

import numpy as np
import pytest
import cv2

from src.ocr_engine import OCREngine, OCRResult


class TestOCREngine:
    """測試 OCREngine 類別"""

    @pytest.fixture
    def ocr_engine(self) -> OCREngine:
        """創建 OCR 引擎實例"""
        return OCREngine()

    @pytest.fixture
    def digit_image(self) -> np.ndarray:
        """創建包含數字的測試圖片"""
        # 創建白色背景
        img = np.ones((100, 200, 3), dtype=np.uint8) * 255

        # 繪製數字 "123"
        cv2.putText(
            img,
            "123",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            (0, 0, 0),
            3,
        )

        return img

    def test_recognize_digits(self, ocr_engine: OCREngine, digit_image: np.ndarray) -> None:
        """測試數字識別"""
        result = ocr_engine.recognize(digit_image)

        # OCR 可能會識別出 "123" 或其他變體
        assert result.text is not None, "應該識別出文字"
        assert len(result.text) > 0, "識別結果不應為空"

        # 檢查是否包含數字
        assert any(c.isdigit() for c in result.text), "應該包含數字"

    def test_confidence_score(self, ocr_engine: OCREngine, digit_image: np.ndarray) -> None:
        """測試置信度分數"""
        result = ocr_engine.recognize(digit_image)

        assert isinstance(result.confidence, float), "置信度應該是浮點數"
        assert 0 <= result.confidence <= 100, "置信度應該在 0-100 範圍內"

    def test_empty_image(self, ocr_engine: OCREngine) -> None:
        """測試空白圖片處理"""
        # 創建純白色圖片（沒有文字）
        white_image = np.ones((100, 100, 3), dtype=np.uint8) * 255

        result = ocr_engine.recognize(white_image)

        # 空白圖片應該返回空文字或低置信度
        assert isinstance(result, OCRResult), "應該返回 OCRResult"
        assert result.confidence >= 0, "置信度應該 ≥ 0"

    def test_grayscale_image(self, ocr_engine: OCREngine) -> None:
        """測試灰階圖片處理"""
        # 創建灰階圖片
        gray_img = np.ones((100, 200), dtype=np.uint8) * 255

        # 繪製數字
        cv2.putText(
            gray_img,
            "456",
            (20, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            2,
            0,
            3,
        )

        result = ocr_engine.recognize(gray_img)

        assert result.text is not None, "應該能處理灰階圖片"

    def test_batch_recognize(self, ocr_engine: OCREngine, digit_image: np.ndarray) -> None:
        """測試批次識別"""
        images = [digit_image, digit_image, digit_image]

        results = ocr_engine.batch_recognize(images)

        assert len(results) == 3, "應該返回 3 個結果"
        assert all(isinstance(r, OCRResult) for r in results), "所有結果應該是 OCRResult"

    def test_preprocess_for_ocr(self, ocr_engine: OCREngine) -> None:
        """測試 OCR 預處理功能"""
        # 創建低對比度圖片
        img = np.ones((100, 200, 3), dtype=np.uint8) * 128

        # 預處理
        processed = ocr_engine.preprocess_for_ocr(img)

        # 驗證輸出是灰階圖片
        assert len(processed.shape) == 2, "預處理後應該是灰階圖片"
        assert processed.dtype == np.uint8, "應該是 uint8 類型"
