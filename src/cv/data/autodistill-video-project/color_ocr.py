"""
顏色檢測與 OCR 識別模組

在 YOLO 檢測框內進行顏色分析（綠色/黃色），並使用 pytesseract 識別價格數字。
"""

import cv2
import numpy as np
import pytesseract
from typing import Dict, Tuple, Optional


# HSV 顏色範圍定義
COLOR_RANGES = {
    'green': {
        'lower': np.array([35, 40, 40]),
        'upper': np.array([85, 255, 255])
    },
    'yellow': {
        'lower': np.array([15, 80, 80]),
        'upper': np.array([35, 255, 255])
    }
}


def detect_color_regions(bbox_roi: np.ndarray, color_type: str) -> Tuple[np.ndarray, bool, Optional[np.ndarray]]:
    """
    在 ROI 中檢測特定顏色（綠色或黃色）

    Args:
        bbox_roi: 檢測框內的圖像 ROI (BGR 格式)
        color_type: 'green' 或 'yellow'

    Returns:
        (color_mask, has_color, largest_contour)
        - color_mask: 顏色遮罩
        - has_color: 是否檢測到該顏色
        - largest_contour: 最大輪廓（如果有）
    """
    if color_type not in COLOR_RANGES:
        raise ValueError(f"不支援的顏色類型: {color_type}. 僅支援 'green' 或 'yellow'")

    # 轉換到 HSV 色彩空間
    hsv = cv2.cvtColor(bbox_roi, cv2.COLOR_BGR2HSV)

    # 創建顏色遮罩
    color_range = COLOR_RANGES[color_type]
    mask = cv2.inRange(hsv, color_range['lower'], color_range['upper'])

    # 形態學運算降噪（3x3 kernel）
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 查找輪廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return mask, False, None

    # 找到最大輪廓
    largest_contour = max(contours, key=cv2.contourArea)

    # 判斷是否有效（面積閾值）
    min_area = 100  # 最小面積像素
    has_color = cv2.contourArea(largest_contour) > min_area

    return mask, has_color, largest_contour if has_color else None


def extract_color_region(bbox_roi: np.ndarray, contour: np.ndarray, padding: int = 5) -> Tuple[np.ndarray, Tuple[int, int, int, int]]:
    """
    基於輪廓提取顏色區域的最小外接矩形

    Args:
        bbox_roi: 檢測框內的圖像 ROI
        contour: 顏色區域的輪廓
        padding: 外接矩形的邊界擴展像素

    Returns:
        (region_image, (x, y, w, h))
        - region_image: 裁剪的區域圖像
        - (x, y, w, h): 相對於 ROI 的座標
    """
    x, y, w, h = cv2.boundingRect(contour)

    # 添加 padding（確保不超出邊界）
    roi_h, roi_w = bbox_roi.shape[:2]
    x = max(0, x - padding)
    y = max(0, y - padding)
    w = min(roi_w - x, w + 2 * padding)
    h = min(roi_h - y, h + 2 * padding)

    # 裁剪區域
    region_image = bbox_roi[y:y+h, x:x+w]

    return region_image, (x, y, w, h)


def preprocess_for_ocr(roi_image: np.ndarray, color_type: str = 'green') -> np.ndarray:
    """
    OCR 預處理流程（顏色通道分離優化版）

    核心策略：
    - 綠色：灰階 + 二值化 + 連通組件
    - 黃色：HSV 顏色分離 + 反轉亮度通道（提高對比度）

    Args:
        roi_image: 輸入的 ROI 圖像
        color_type: 'green' 或 'yellow'

    Returns:
        處理後的二值化反色圖像
    """
    # 放大圖像（提高解析度）
    scale_factor = 8 if color_type == 'green' else 8  # 黃色也用 8 倍
    roi_scaled = cv2.resize(roi_image, None, fx=scale_factor, fy=scale_factor,
                           interpolation=cv2.INTER_CUBIC)

    if color_type == 'yellow':
        # === 黃色特殊處理：使用 HSV 顏色分離 ===

        # 1. 轉換到 HSV 色彩空間
        hsv = cv2.cvtColor(roi_scaled, cv2.COLOR_BGR2HSV)

        # 2. 提取 V 通道（亮度），並反轉
        # 黃色文字通常較暗，黃色背景較亮，反轉後文字變亮
        v_channel = hsv[:, :, 2]
        v_inverted = cv2.bitwise_not(v_channel)

        # 3. 增強對比度（CLAHE）
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(v_inverted)

        # 4. Otsu 二值化
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 5. 去除小雜訊
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)

        # 6. 連通組件過濾
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        binary_filtered = np.zeros_like(binary)

        min_area = 25
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                binary_filtered[labels == i] = 255

        result = binary_filtered

    else:
        # === 綠色處理：增強版預處理（提升置信度）===

        # 1. 灰階轉換
        if len(roi_scaled.shape) == 3:
            gray = cv2.cvtColor(roi_scaled, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi_scaled

        # 2. 自適應閾值（處理光照不均）
        # 直接使用，不額外處理（已證明效果最好）
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # 5. 輕微去噪（非常小的kernel，避免破壞文字）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)

        # 6. 連通組件過濾（降低 min_area 門檻，避免誤刪文字）
        num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binary, connectivity=8)
        binary_filtered = np.zeros_like(binary)

        min_area = 10  # 降低到 10（之前是 20）
        for i in range(1, num_labels):
            area = stats[i, cv2.CC_STAT_AREA]
            if area >= min_area:
                binary_filtered[labels == i] = 255

        # 7. 反色處理（白色文字黑色背景）
        white_ratio = np.sum(binary_filtered == 255) / binary_filtered.size
        if white_ratio < 0.5:
            result = cv2.bitwise_not(binary_filtered)
        else:
            result = binary_filtered

    # 邊緣擴展
    border_size = 15
    result = cv2.copyMakeBorder(
        result, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=0
    )

    return result


def recognize_price(region_image: np.ndarray, color_type: str = 'green') -> Tuple[str, float]:
    """
    使用 pytesseract 識別價格（基於格式規則的優化版）

    格式規則：
    - 綠色: $數字/M、$數字/K、$數字/T
    - 黃色: $數字/S

    Args:
        region_image: 顏色區域圖像
        color_type: 'green' 或 'yellow'（影響預處理策略和格式驗證）

    Returns:
        (price_text, confidence)
        - price_text: 識別的價格文字（清理並驗證格式後）
        - confidence: 置信度 (0-100)
    """
    import re

    # 預處理（根據顏色類型選擇策略）
    processed = preprocess_for_ocr(region_image, color_type)

    # 根據顏色類型定義字符白名單和格式規則
    if color_type == 'green':
        # 綠色：$數字K、$數字M、$數字T、$數字、$1.2K（沒有斜線）
        whitelist = '0123456789$MKT.'
        # 正則表達式：
        # 1. $數字K/M/T（例如 $1K, $2M, $3T）
        # 2. $數字.數字K/M/T（例如 $1.2K）
        # 3. $數字（例如 $5）
        patterns = [
            re.compile(r'\$?(\d+(?:\.\d+)?)([KMT])', re.IGNORECASE),  # $1K, $1.2M
            re.compile(r'\$?(\d+(?:\.\d+)?)', re.IGNORECASE)  # $5
        ]
    else:  # yellow
        # 黃色：$數字/s（有斜線）
        whitelist = '0123456789$/sS.'
        # 正則表達式：$數字/s
        patterns = [
            re.compile(r'\$?(\d+(?:\.\d+)?)[/\\][sS]', re.IGNORECASE)  # $9/s
        ]

    # Tesseract 配置
    custom_config = f'--psm 7 --oem 1 -c tessedit_char_whitelist={whitelist}'

    best_result = ("", 0.0)
    all_attempts = []

    try:
        # 嘗試多種 PSM 模式
        psm_modes = [7, 8, 6]  # 單行、單詞、單塊

        for psm in psm_modes:
            config = f'--psm {psm} --oem 1 -c tessedit_char_whitelist={whitelist}'

            # 方法 1: image_to_data
            data = pytesseract.image_to_data(
                processed, config=config, output_type=pytesseract.Output.DICT
            )

            text_parts = []
            confidences = []

            for i, conf in enumerate(data['conf']):
                if int(conf) > 0:
                    text = data['text'][i].strip()
                    if text:
                        text_parts.append(text)
                        confidences.append(int(conf))

            if text_parts:
                raw_text = ''.join(text_parts)
                avg_conf = sum(confidences) / len(confidences) if confidences else 0
                all_attempts.append((raw_text, avg_conf))

            # 方法 2: image_to_string
            raw_text = pytesseract.image_to_string(processed, config=config).strip()
            raw_text = ''.join(raw_text.split())  # 移除空格和換行
            if raw_text:
                all_attempts.append((raw_text, 55.0))

        # 後處理所有嘗試結果
        for raw_text, conf in all_attempts:
            if not raw_text:
                continue

            try:
                # 清理常見識別錯誤
                cleaned = raw_text.upper()
                cleaned = cleaned.replace('I', '1').replace('L', '1').replace('O', '0')
                cleaned = cleaned.replace('|', '1').replace('!', '1')
                cleaned = cleaned.replace(';', '').replace(':', '')

                # 移除末尾多餘的點（但保留價格中的小數點）
                if cleaned.endswith('.'):
                    cleaned = cleaned.rstrip('.')

                # 嘗試匹配所有格式模式
                for pattern in patterns:
                    match = pattern.search(cleaned)
                    if match:
                        try:
                            if color_type == 'green':
                                # 綠色可能有兩種格式
                                if len(match.groups()) >= 2:
                                    # $數字K/M/T 格式
                                    number = match.group(1)
                                    unit = match.group(2).upper()
                                    formatted = f"${number}{unit}"  # 沒有斜線！
                                    adjusted_conf = min(conf + 25, 95.0)
                                else:
                                    # $數字 格式（沒有單位）
                                    number = match.group(1)
                                    formatted = f"${number}"
                                    adjusted_conf = min(conf + 20, 90.0)

                                if adjusted_conf > best_result[1]:
                                    best_result = (formatted, adjusted_conf)
                                    break  # 找到匹配就退出

                            elif color_type == 'yellow':
                                # 黃色：$數字/s 格式
                                number = match.group(1)
                                formatted = f"${number}/s"  # 小寫 s
                                adjusted_conf = min(conf + 25, 95.0)

                                if adjusted_conf > best_result[1]:
                                    best_result = (formatted, adjusted_conf)
                                    break

                        except (IndexError, AttributeError):
                            pass

            except Exception:
                pass

        # 如果沒有找到匹配，返回最高置信度的原始結果
        if not best_result[0] and all_attempts:
            best_attempt = max(all_attempts, key=lambda x: x[1])
            # 嘗試基本清理
            cleaned = best_attempt[0].upper()
            cleaned = cleaned.replace('I', '1').replace('L', '1').replace('O', '0')

            # 確保有 $ 符號
            if not cleaned.startswith('$'):
                cleaned = '$' + cleaned

            best_result = (cleaned, best_attempt[1])

        return best_result

    except Exception as e:
        print(f"OCR 識別錯誤: {e}")
        return "", 0.0


def process_detection_with_ocr(image: np.ndarray, bbox: np.ndarray, class_id: int) -> Dict:
    """
    主處理函數：整合顏色檢測和 OCR 識別

    Args:
        image: 原始圖像
        bbox: YOLO 檢測框 [x1, y1, x2, y2]
        class_id: YOLO 類別 ID

    Returns:
        字典包含：
        {
            'has_both_colors': bool,
            'has_green': bool,
            'has_yellow': bool,
            'green_price': str,
            'green_confidence': float,
            'yellow_price': str,
            'yellow_confidence': float,
            'bbox': np.ndarray
        }
    """
    x1, y1, x2, y2 = map(int, bbox)

    # 提取檢測框 ROI
    bbox_roi = image[y1:y2, x1:x2]

    # 初始化結果
    result = {
        'has_both_colors': False,
        'has_green': False,
        'has_yellow': False,
        'green_price': '',
        'green_confidence': 0.0,
        'yellow_price': '',
        'yellow_confidence': 0.0,
        'bbox': bbox
    }

    # 檢測綠色區域
    green_mask, has_green, green_contour = detect_color_regions(bbox_roi, 'green')
    result['has_green'] = has_green

    if has_green:
        green_region, _ = extract_color_region(bbox_roi, green_contour)
        green_price, green_conf = recognize_price(green_region, color_type='green')
        result['green_price'] = green_price
        result['green_confidence'] = green_conf

    # 檢測黃色區域
    yellow_mask, has_yellow, yellow_contour = detect_color_regions(bbox_roi, 'yellow')
    result['has_yellow'] = has_yellow

    if has_yellow:
        yellow_region, _ = extract_color_region(bbox_roi, yellow_contour)
        yellow_price, yellow_conf = recognize_price(yellow_region, color_type='yellow')
        result['yellow_price'] = yellow_price
        result['yellow_confidence'] = yellow_conf

    # 判斷是否同時包含綠色和黃色
    result['has_both_colors'] = has_green and has_yellow

    return result


def annotate_ocr_results(image: np.ndarray, bbox: np.ndarray, ocr_result: Dict) -> None:
    """
    在圖像上標註 OCR 結果

    Args:
        image: 要標註的圖像（會直接修改）
        bbox: 檢測框座標 [x1, y1, x2, y2]
        ocr_result: process_detection_with_ocr 返回的結果字典
    """
    x1, y1, x2, y2 = map(int, bbox)

    # 字體設置
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.6
    thickness = 2

    # 綠色價格標註（檢測框上方）
    if ocr_result['green_price']:
        price_str = ocr_result['green_price']
        # 避免雙重美元符號
        if not price_str.startswith('$'):
            price_str = f"${price_str}"
        green_text = f"G: {price_str} ({ocr_result['green_confidence']:.0f}%)"

        # 計算文字大小
        (text_w, text_h), baseline = cv2.getTextSize(green_text, font, font_scale, thickness)

        # 繪製黑色背景矩形
        bg_y1 = max(0, y1 - text_h - baseline - 10)
        bg_y2 = y1 - 5
        cv2.rectangle(image, (x1, bg_y1), (x1 + text_w + 10, bg_y2), (0, 0, 0), -1)

        # 繪製綠色文字
        cv2.putText(
            image, green_text, (x1 + 5, y1 - 10),
            font, font_scale, (0, 255, 0), thickness
        )

    # 黃色價格標註（檢測框下方）
    if ocr_result['yellow_price']:
        price_str = ocr_result['yellow_price']
        # 避免雙重美元符號
        if not price_str.startswith('$'):
            price_str = f"${price_str}"
        yellow_text = f"Y: {price_str} ({ocr_result['yellow_confidence']:.0f}%)"

        # 計算文字大小
        (text_w, text_h), baseline = cv2.getTextSize(yellow_text, font, font_scale, thickness)

        # 繪製黑色背景矩形
        bg_y1 = y2 + 5
        bg_y2 = y2 + text_h + baseline + 10
        cv2.rectangle(image, (x1, bg_y1), (x1 + text_w + 10, bg_y2), (0, 0, 0), -1)

        # 繪製黃色文字
        cv2.putText(
            image, yellow_text, (x1 + 5, y2 + text_h + 10),
            font, font_scale, (0, 255, 255), thickness
        )


class OCRStatistics:
    """OCR 識別統計追蹤"""

    def __init__(self):
        self.total_detections = 0
        self.dual_color_detections = 0
        self.successful_green_ocr = 0
        self.successful_yellow_ocr = 0
        self.green_confidences = []
        self.yellow_confidences = []

    def update(self, ocr_result: Dict):
        """更新統計資訊"""
        self.total_detections += 1

        if ocr_result['has_both_colors']:
            self.dual_color_detections += 1

        if ocr_result['green_price']:
            self.successful_green_ocr += 1
            self.green_confidences.append(ocr_result['green_confidence'])

        if ocr_result['yellow_price']:
            self.successful_yellow_ocr += 1
            self.yellow_confidences.append(ocr_result['yellow_confidence'])

    def report(self) -> str:
        """生成統計報告"""
        avg_green_conf = sum(self.green_confidences) / len(self.green_confidences) if self.green_confidences else 0
        avg_yellow_conf = sum(self.yellow_confidences) / len(self.yellow_confidences) if self.yellow_confidences else 0

        report = f"""
╔════════════════════════════════════════════════════════════════╗
║                     OCR 識別統計報告                           ║
╚════════════════════════════════════════════════════════════════╝
  總檢測數:              {self.total_detections}
  雙色檢測數:            {self.dual_color_detections} ({self.dual_color_detections/self.total_detections*100:.1f}%)

  綠色價格識別成功:      {self.successful_green_ocr} ({self.successful_green_ocr/self.total_detections*100:.1f}%)
  綠色平均置信度:        {avg_green_conf:.1f}%

  黃色價格識別成功:      {self.successful_yellow_ocr} ({self.successful_yellow_ocr/self.total_detections*100:.1f}%)
  黃色平均置信度:        {avg_yellow_conf:.1f}%
╚════════════════════════════════════════════════════════════════╝
"""
        return report
