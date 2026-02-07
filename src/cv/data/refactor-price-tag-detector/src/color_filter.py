"""顏色過濾器 - 檢測圖片中的黃色和綠色區域"""

from typing import Dict, Optional, Tuple

import cv2
import numpy as np


class ColorFilter:
    """顏色過濾器

    檢測圖片中的黃色和綠色區域，用於過濾價格標籤

    Attributes:
        yellow_lower: 黃色 HSV 範圍下限
        yellow_upper: 黃色 HSV 範圍上限
        green_lower: 綠色 HSV 範圍下限
        green_upper: 綠色 HSV 範圍上限
        min_area_ratio: 最小區域面積佔比（預設 0.01 = 1%）
    """

    def __init__(
        self,
        yellow_range: Optional[Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = None,
        green_range: Optional[Tuple[Tuple[int, int, int], Tuple[int, int, int]]] = None,
        min_area_ratio: float = 0.01,
    ) -> None:
        """初始化顏色過濾器

        Args:
            yellow_range: 黃色 HSV 範圍 ((H_min, S_min, V_min), (H_max, S_max, V_max))
            green_range: 綠色 HSV 範圍 ((H_min, S_min, V_min), (H_max, S_max, V_max))
            min_area_ratio: 最小區域面積佔比，範圍 [0, 1]
        """
        # 黃色範圍 (HSV)
        if yellow_range is None:
            self.yellow_lower = np.array([20, 100, 100])
            self.yellow_upper = np.array([35, 255, 255])
        else:
            self.yellow_lower = np.array(yellow_range[0])
            self.yellow_upper = np.array(yellow_range[1])

        # 綠色範圍 (HSV)
        if green_range is None:
            self.green_lower = np.array([40, 50, 50])
            self.green_upper = np.array([80, 255, 255])
        else:
            self.green_lower = np.array(green_range[0])
            self.green_upper = np.array(green_range[1])

        self.min_area_ratio = min_area_ratio

    def has_both_colors(self, image: np.ndarray, bbox: Tuple[float, ...]) -> bool:
        """檢查 bbox 區域是否同時包含黃色和綠色

        Args:
            image: BGR 格式的圖片
            bbox: 檢測框 (x1, y1, x2, y2)

        Returns:
            True 如果同時包含黃色和綠色，否則 False
        """
        result = self.extract_color_regions(image, bbox)
        return result["has_yellow"] and result["has_green"]

    def extract_color_regions(
        self, image: np.ndarray, bbox: Tuple[float, ...]
    ) -> Dict[str, any]:
        """提取 bbox 區域內的黃色和綠色區域

        Args:
            image: BGR 格式的圖片
            bbox: 檢測框 (x1, y1, x2, y2)

        Returns:
            包含以下欄位的字典：
            - has_yellow: 是否包含黃色
            - has_green: 是否包含綠色
            - yellow_region: 黃色區域遮罩 (或 None)
            - green_region: 綠色區域遮罩 (或 None)
            - yellow_ratio: 黃色區域佔比
            - green_ratio: 綠色區域佔比
        """
        # 裁切 bbox 區域
        x1, y1, x2, y2 = map(int, bbox)
        roi = image[y1:y2, x1:x2]

        if roi.size == 0:
            return self._empty_result()

        # 轉換到 HSV 色彩空間
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 建立顏色遮罩
        yellow_mask = cv2.inRange(hsv, self.yellow_lower, self.yellow_upper)
        green_mask = cv2.inRange(hsv, self.green_lower, self.green_upper)

        # 計算區域佔比
        total_pixels = roi.shape[0] * roi.shape[1]
        yellow_ratio = np.count_nonzero(yellow_mask) / total_pixels
        green_ratio = np.count_nonzero(green_mask) / total_pixels

        # 判斷是否包含顏色
        has_yellow = yellow_ratio >= self.min_area_ratio
        has_green = green_ratio >= self.min_area_ratio

        return {
            "has_yellow": has_yellow,
            "has_green": has_green,
            "yellow_region": yellow_mask if has_yellow else None,
            "green_region": green_mask if has_green else None,
            "yellow_ratio": yellow_ratio,
            "green_ratio": green_ratio,
        }

    def _empty_result(self) -> Dict[str, any]:
        """返回空結果"""
        return {
            "has_yellow": False,
            "has_green": False,
            "yellow_region": None,
            "green_region": None,
            "yellow_ratio": 0.0,
            "green_ratio": 0.0,
        }
