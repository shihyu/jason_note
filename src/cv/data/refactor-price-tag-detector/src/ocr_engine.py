"""改進的 OCR 引擎 - 針對價格標籤優化"""
import cv2
import numpy as np
import pytesseract
from dataclasses import dataclass
from typing import List
import re


@dataclass
class OCRResult:
    """OCR 識別結果

    Attributes:
        text: 識別的文字
        confidence: 置信度分數
        raw_output: 原始輸出
        method: 使用的識別方法
    """
    text: str
    confidence: float
    raw_output: dict | None = None
    method: str = "default"


class PriceTagOCR:
    """針對價格標籤優化的 OCR 引擎

    專門處理遊戲中的價格標籤，包含：
    - $125/s
    - $40K
    - $1.5M
    等格式
    """

    def __init__(self):
        """初始化 OCR 引擎"""
        # Tesseract 配置
        self.configs = {
            'default': '--psm 7 --oem 3',  # 單行文字
            'digits': '--psm 7 --oem 3 -c tessedit_char_whitelist=0123456789$.,/KMTBs',
            'single': '--psm 8 --oem 3 -c tessedit_char_whitelist=0123456789$.,/KMTBs',
            'sparse': '--psm 11 --oem 3 -c tessedit_char_whitelist=0123456789$.,/KMTBs',
        }

    def preprocess_yellow_region(self, image: np.ndarray) -> List[np.ndarray]:
        """預處理黃色區域（黑色文字在黃色背景）

        Args:
            image: 輸入圖片

        Returns:
            預處理後的圖片列表（多種策略）
        """
        processed = []

        # 轉換到灰度
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 獲取圖片尺寸
        height, width = gray.shape[:2]

        # 根據大小調整 CLAHE 參數
        if width < 30 or height < 30:
            # 極小區域：更激進的參數
            clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        # 策略 1: CLAHE + 反色 + 自適應二值化
        enhanced = clahe.apply(gray)
        # 反色（黃底黑字 -> 白底黑字）
        inverted = 255 - enhanced
        binary = cv2.adaptiveThreshold(
            inverted, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        processed.append(binary)

        # 策略 2: 簡單反色 + Otsu
        inverted2 = 255 - gray
        _, binary2 = cv2.threshold(inverted2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary2)

        # 策略 3: 增強對比度
        enhanced2 = cv2.convertScaleAbs(gray, alpha=2.0, beta=-100)
        inverted3 = 255 - enhanced2
        _, binary3 = cv2.threshold(inverted3, 127, 255, cv2.THRESH_BINARY)
        processed.append(binary3)

        # 策略 4: 極小區域專用 - 極度放大 + 銳化
        if width < 30 or height < 30:
            # 先放大 4 倍
            enlarged = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            # 反色
            enlarged_inv = 255 - enlarged
            # 銳化
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enlarged_inv, -1, kernel_sharpen)
            # 對比度增強
            enhanced3 = cv2.convertScaleAbs(sharpened, alpha=2.0, beta=-50)
            # 自適應二值化
            binary4 = cv2.adaptiveThreshold(
                enhanced3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            # 縮回到 2 倍大小（保持一致性）
            binary4 = cv2.resize(binary4, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            processed.append(binary4)

        # 對所有結果進行去噪和動態放大
        final = []
        # 根據原始大小決定放大倍數
        if width < 30 or height < 30:
            scale = 4  # 極小區域放大 4 倍
        elif width < 50 or height < 50:
            scale = 3  # 小區域放大 3 倍
        else:
            scale = 2  # 正常區域放大 2 倍

        for img in processed:
            # 去噪
            denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
            # 形態學操作
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            # 動態放大圖片
            upscaled = cv2.resize(cleaned, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            final.append(upscaled)

        return final

    def preprocess_green_region(self, image: np.ndarray) -> List[np.ndarray]:
        """預處理綠色區域（白色文字在綠色背景）

        Args:
            image: 輸入圖片

        Returns:
            預處理後的圖片列表
        """
        processed = []

        # 轉換到灰度
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()

        # 獲取圖片尺寸
        height, width = gray.shape[:2]

        # 根據大小調整 CLAHE 參數
        if width < 30 or height < 30:
            # 極小區域：更激進的參數
            clahe = cv2.createCLAHE(clipLimit=5.0, tileGridSize=(4, 4))
        else:
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))

        # 策略 1: CLAHE + 自適應二值化
        enhanced = clahe.apply(gray)
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        processed.append(binary)

        # 策略 2: Otsu 二值化
        _, binary2 = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        processed.append(binary2)

        # 策略 3: 增強亮度後二值化
        enhanced2 = cv2.convertScaleAbs(gray, alpha=1.5, beta=50)
        _, binary3 = cv2.threshold(enhanced2, 127, 255, cv2.THRESH_BINARY)
        processed.append(binary3)

        # 策略 4: 極小區域專用 - 極度放大 + 銳化
        if width < 30 or height < 30:
            # 先放大 4 倍
            enlarged = cv2.resize(gray, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
            # 銳化
            kernel_sharpen = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(enlarged, -1, kernel_sharpen)
            # 對比度增強
            enhanced3 = cv2.convertScaleAbs(sharpened, alpha=2.0, beta=-50)
            # 自適應二值化
            binary4 = cv2.adaptiveThreshold(
                enhanced3, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY, 11, 2
            )
            # 縮回到 2 倍大小（保持一致性）
            binary4 = cv2.resize(binary4, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
            processed.append(binary4)

        # 清理和動態放大
        final = []
        # 根據原始大小決定放大倍數
        if width < 30 or height < 30:
            scale = 4  # 極小區域放大 4 倍
        elif width < 50 or height < 50:
            scale = 3  # 小區域放大 3 倍
        else:
            scale = 2  # 正常區域放大 2 倍

        for img in processed:
            denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
            kernel = np.ones((2, 2), np.uint8)
            cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            upscaled = cv2.resize(cleaned, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            final.append(upscaled)

        return final

    def recognize_with_multiple_strategies(
        self,
        images: List[np.ndarray],
        color: str
    ) -> OCRResult:
        """使用多種策略識別文字

        Args:
            images: 預處理後的圖片列表
            color: 顏色類型 ('yellow' 或 'green')

        Returns:
            最佳識別結果
        """
        all_results = []

        for img_idx, img in enumerate(images):
            for config_name, config in self.configs.items():
                try:
                    # OCR 識別
                    text = pytesseract.image_to_string(img, config=config).strip()

                    # 獲取詳細資訊
                    data = pytesseract.image_to_data(
                        img, config=config, output_type=pytesseract.Output.DICT
                    )

                    # 計算平均置信度
                    confidences = [c for c in data['conf'] if c != -1]
                    avg_conf = np.mean(confidences) if confidences else 0

                    # 清理文字
                    cleaned = self.clean_text(text)

                    if cleaned:
                        all_results.append({
                            'text': cleaned,
                            'confidence': avg_conf,
                            'method': f"{color}_{img_idx}_{config_name}",
                            'raw': text
                        })
                except Exception as e:
                    continue

        if not all_results:
            return OCRResult(text="", confidence=0.0, method="none")

        # 選擇最佳結果
        best = self.select_best_result(all_results)

        return OCRResult(
            text=best['text'],
            confidence=best['confidence'],
            method=best['method'],
            raw_output={'raw': best['raw']}
        )

    def clean_text(self, text: str) -> str:
        """清理和標準化識別的文字

        Args:
            text: 原始文字

        Returns:
            清理後的文字
        """
        if not text:
            return ""

        # 移除空白
        cleaned = text.strip()

        # 替換常見錯誤
        replacements = {
            'S': '$',  # S 可能被誤認為 $
            'l': '1',  # l 可能被誤認為 1
            'O': '0',  # O 可能被誤認為 0
            'o': '0',  # o 可能被誤認為 0
            '|': '1',  # | 可能被誤認為 1
            'I': '1',  # I 可能被誤認為 1
        }

        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        # 只保留價格相關字符
        cleaned = re.sub(r'[^0-9$.,/KMTBs]', '', cleaned)

        # 確保 $ 在開頭
        if '$' in cleaned and not cleaned.startswith('$'):
            cleaned = '$' + cleaned.replace('$', '')

        return cleaned

    def select_best_result(self, results: List[dict]) -> dict:
        """選擇最佳識別結果

        Args:
            results: 所有識別結果

        Returns:
            最佳結果
        """
        # 過濾無效結果
        valid = [r for r in results if self.is_valid_price(r['text'])]

        if not valid:
            # 如果沒有有效結果，返回置信度最高的
            return max(results, key=lambda x: x['confidence'])

        # 評分：結合置信度和有效性
        for r in valid:
            score = r['confidence']

            # 加分項
            if r['text'].startswith('$'):
                score += 10
            if any(c in r['text'] for c in ['K', 'M', 'T', 'B']):
                score += 5
            if '/' in r['text']:
                score += 5

            r['score'] = score

        # 返回得分最高的
        return max(valid, key=lambda x: x['score'])

    def is_valid_price(self, text: str) -> bool:
        """驗證是否為有效的價格格式

        Args:
            text: 文字

        Returns:
            是否有效
        """
        if not text or len(text) < 2:
            return False

        # 必須包含數字
        if not any(c.isdigit() for c in text):
            return False

        # 檢查價格格式
        patterns = [
            r'\$\d+',           # $123
            r'\$\d+\.\d+',      # $1.5
            r'\$\d+[KMTBkmtb]', # $40K
            r'\$\d+/s',         # $125/s
            r'\$\d+\.\d+[KMTBkmtb]', # $1.5M
        ]

        for pattern in patterns:
            if re.search(pattern, text):
                return True

        return False

    def recognize_yellow(self, image: np.ndarray) -> OCRResult:
        """識別黃色區域文字

        Args:
            image: ROI 圖片

        Returns:
            識別結果
        """
        preprocessed = self.preprocess_yellow_region(image)
        return self.recognize_with_multiple_strategies(preprocessed, 'yellow')

    def recognize_green(self, image: np.ndarray) -> OCRResult:
        """識別綠色區域文字

        Args:
            image: ROI 圖片

        Returns:
            識別結果
        """
        preprocessed = self.preprocess_green_region(image)
        return self.recognize_with_multiple_strategies(preprocessed, 'green')

    def recognize(self, image: np.ndarray, color_hint: str = None) -> OCRResult:
        """識別文字（通用接口）

        Args:
            image: ROI 圖片
            color_hint: 顏色提示 ('yellow' 或 'green')

        Returns:
            識別結果
        """
        if color_hint == 'yellow':
            return self.recognize_yellow(image)
        elif color_hint == 'green':
            return self.recognize_green(image)
        else:
            # 嘗試兩種方式，取最佳結果
            yellow_result = self.recognize_yellow(image)
            green_result = self.recognize_green(image)

            if yellow_result.confidence > green_result.confidence:
                return yellow_result
            else:
                return green_result
