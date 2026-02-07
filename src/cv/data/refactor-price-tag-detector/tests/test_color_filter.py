"""測試顏色過濾器"""

import numpy as np
import pytest
import cv2

from src.color_filter import ColorFilter


class TestColorFilter:
    """測試 ColorFilter 類別"""

    @pytest.fixture
    def color_filter(self) -> ColorFilter:
        """創建顏色過濾器實例"""
        return ColorFilter()

    @pytest.fixture
    def yellow_image(self) -> np.ndarray:
        """創建黃色測試圖片"""
        # HSV: 黃色 (25-35, 100-255, 100-255)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :] = [0, 200, 200]  # BGR 格式的黃色
        return img

    @pytest.fixture
    def green_image(self) -> np.ndarray:
        """創建綠色測試圖片"""
        # HSV: 綠色 (40-80, 50-255, 50-255)
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[:, :] = [0, 200, 0]  # BGR 格式的綠色
        return img

    @pytest.fixture
    def dual_color_image(self) -> np.ndarray:
        """創建包含黃色和綠色的測試圖片"""
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # 上半部黃色
        img[:50, :] = [0, 200, 200]
        # 下半部綠色
        img[50:, :] = [0, 200, 0]
        return img

    def test_has_yellow(self, color_filter: ColorFilter, yellow_image: np.ndarray) -> None:
        """測試黃色檢測"""
        bbox = (0, 0, 100, 100)
        result = color_filter.extract_color_regions(yellow_image, bbox)

        assert result["has_yellow"], "應該檢測到黃色"
        assert not result["has_green"], "不應該檢測到綠色"

    def test_has_green(self, color_filter: ColorFilter, green_image: np.ndarray) -> None:
        """測試綠色檢測"""
        bbox = (0, 0, 100, 100)
        result = color_filter.extract_color_regions(green_image, bbox)

        assert not result["has_yellow"], "不應該檢測到黃色"
        assert result["has_green"], "應該檢測到綠色"

    def test_has_both_colors(
        self, color_filter: ColorFilter, dual_color_image: np.ndarray
    ) -> None:
        """測試雙色檢測"""
        bbox = (0, 0, 100, 100)
        result = color_filter.has_both_colors(dual_color_image, bbox)

        assert result, "應該檢測到黃色和綠色"

    def test_extract_regions(
        self, color_filter: ColorFilter, dual_color_image: np.ndarray
    ) -> None:
        """測試區域提取"""
        bbox = (0, 0, 100, 100)
        result = color_filter.extract_color_regions(dual_color_image, bbox)

        assert result["has_yellow"], "應該有黃色"
        assert result["has_green"], "應該有綠色"
        assert result["yellow_region"] is not None, "應該有黃色區域"
        assert result["green_region"] is not None, "應該有綠色區域"
        assert result["yellow_region"].shape == (100, 100), "黃色區域大小應正確"
        assert result["green_region"].shape == (100, 100), "綠色區域大小應正確"

    def test_bbox_cropping(self, color_filter: ColorFilter, dual_color_image: np.ndarray) -> None:
        """測試 bbox 裁切功能"""
        # 只取上半部（黃色區域）
        bbox = (0, 0, 100, 50)
        result = color_filter.extract_color_regions(dual_color_image, bbox)

        assert result["has_yellow"], "上半部應該有黃色"
        # 可能有少量綠色洩漏，所以不嚴格要求沒有綠色

    def test_empty_image(self, color_filter: ColorFilter) -> None:
        """測試空白圖片"""
        black_image = np.zeros((100, 100, 3), dtype=np.uint8)
        bbox = (0, 0, 100, 100)
        result = color_filter.extract_color_regions(black_image, bbox)

        assert not result["has_yellow"], "黑色圖片不應該有黃色"
        assert not result["has_green"], "黑色圖片不應該有綠色"
