"""OCR 引擎 - 文字識別"""

from dataclasses import dataclass
from typing import List

import cv2
import numpy as np
import pytesseract


@dataclass
class OCRResult:
    """OCR 識別結果

    Attributes:
        text: 識別出的文字
        confidence: 置信度分數 (0-100)
        raw_output: pytesseract 原始輸出（可選）
    """

    text: str
    confidence: float
    raw_output: dict | None = None


class OCREngine:
    """OCR 文字識別引擎

    使用 Tesseract OCR 進行文字識別

    Attributes:
        lang: 識別語言（預設 'eng'）
        config: Tesseract 配置參數
    """

    def __init__(self, lang: str = "eng", config: str | None = None) -> None:
        """初始化 OCR 引擎

        Args:
            lang: 識別語言代碼（例如：'eng', 'chi_tra'）
            config: Tesseract 配置參數字串
        """
        self.lang = lang

        # 預設配置：只識別數字和一些符號
        if config is None:
            self.config = "--psm 6 -c tessedit_char_whitelist=0123456789.$,"
        else:
            self.config = config

    def recognize(self, image: np.ndarray) -> OCRResult:
        """識別圖片中的文字

        Args:
            image: 輸入圖片（可以是 BGR 或灰階）

        Returns:
            OCRResult: 識別結果
        """
        # 預處理圖片
        processed = self.preprocess_for_ocr(image)

        # 執行 OCR
        try:
            # 獲取詳細輸出
            data = pytesseract.image_to_data(
                processed, lang=self.lang, config=self.config, output_type=pytesseract.Output.DICT
            )

            # 提取文字和置信度
            text = self._extract_text(data)
            confidence = self._calculate_confidence(data)

            return OCRResult(text=text, confidence=confidence, raw_output=data)

        except Exception as e:
            # OCR 失敗時返回空結果
            return OCRResult(text="", confidence=0.0, raw_output=None)

    def batch_recognize(self, images: List[np.ndarray]) -> List[OCRResult]:
        """批次識別多張圖片

        Args:
            images: 圖片列表

        Returns:
            識別結果列表
        """
        return [self.recognize(img) for img in images]

    def preprocess_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """OCR 預處理

        提高 OCR 準確率的圖片預處理步驟：
        1. 轉換為灰階
        2. 二值化
        3. 降噪
        4. 形態學運算

        Args:
            image: 輸入圖片

        Returns:
            預處理後的圖片
        """
        # 如果已經是灰階，跳過轉換
        if len(image.shape) == 2:
            gray = image
        else:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 調整對比度（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # 二值化（Otsu's method）
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 降噪
        denoised = cv2.medianBlur(binary, 3)

        # 形態學閉運算（連接斷開的文字）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        closed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)

        return closed

    def _extract_text(self, data: dict) -> str:
        """從 pytesseract 輸出中提取文字

        Args:
            data: pytesseract.image_to_data 的輸出

        Returns:
            識別出的文字（去除空白）
        """
        texts = []

        for i, conf in enumerate(data["conf"]):
            # 只保留置信度 > 0 的文字
            if int(conf) > 0:
                text = data["text"][i].strip()
                if text:
                    texts.append(text)

        return " ".join(texts)

    def _calculate_confidence(self, data: dict) -> float:
        """計算平均置信度

        Args:
            data: pytesseract.image_to_data 的輸出

        Returns:
            平均置信度 (0-100)
        """
        confidences = [int(c) for c in data["conf"] if int(c) > 0]

        if not confidences:
            return 0.0

        return sum(confidences) / len(confidences)
