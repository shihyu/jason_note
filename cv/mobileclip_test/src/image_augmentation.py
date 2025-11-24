#!/usr/bin/env python3
"""圖像增強模組 - 旋轉、亮度、模糊、裁切、縮放"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple


class ImageAugmenter:
    """圖像增強類別"""

    @staticmethod
    def rotate(image: Image.Image, angle: float) -> Image.Image:
        """
        旋轉圖片

        Args:
            image: PIL Image
            angle: 旋轉角度 (度)

        Returns:
            旋轉後的圖片
        """
        return image.rotate(angle, expand=True, fillcolor=(255, 255, 255))

    @staticmethod
    def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
        """
        調整亮度

        Args:
            image: PIL Image
            factor: 亮度係數 (1.0 = 原始, >1.0 = 變亮, <1.0 = 變暗)

        Returns:
            調整後的圖片
        """
        # 轉換為 numpy array
        img_array = np.array(image).astype(np.float32)

        # 調整亮度
        img_array = np.clip(img_array * factor, 0, 255).astype(np.uint8)

        return Image.fromarray(img_array)

    @staticmethod
    def blur(image: Image.Image, kernel_size: int = 5) -> Image.Image:
        """
        高斯模糊

        Args:
            image: PIL Image
            kernel_size: 核心大小 (必須為奇數)

        Returns:
            模糊後的圖片
        """
        # 確保 kernel_size 為奇數
        if kernel_size % 2 == 0:
            kernel_size += 1

        # 轉換為 OpenCV 格式
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 高斯模糊
        blurred = cv2.GaussianBlur(img_cv, (kernel_size, kernel_size), 0)

        # 轉換回 PIL
        blurred_rgb = cv2.cvtColor(blurred, cv2.COLOR_BGR2RGB)
        return Image.fromarray(blurred_rgb)

    @staticmethod
    def center_crop(image: Image.Image, crop_ratio: float) -> Image.Image:
        """
        中心裁切

        Args:
            image: PIL Image
            crop_ratio: 裁切比例 (0.0-1.0)

        Returns:
            裁切後的圖片
        """
        width, height = image.size

        # 計算裁切區域
        new_width = int(width * crop_ratio)
        new_height = int(height * crop_ratio)

        left = (width - new_width) // 2
        top = (height - new_height) // 2
        right = left + new_width
        bottom = top + new_height

        return image.crop((left, top, right, bottom))

    @staticmethod
    def resize(image: Image.Image, scale: float) -> Image.Image:
        """
        縮放圖片

        Args:
            image: PIL Image
            scale: 縮放比例 (1.0 = 原始大小)

        Returns:
            縮放後的圖片
        """
        width, height = image.size
        new_width = int(width * scale)
        new_height = int(height * scale)

        return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

    @staticmethod
    def combined(image: Image.Image,
                 rotate_angle: float = 0,
                 brightness_factor: float = 1.0,
                 scale: float = 1.0) -> Image.Image:
        """
        組合多種變化

        Args:
            image: PIL Image
            rotate_angle: 旋轉角度
            brightness_factor: 亮度係數
            scale: 縮放比例

        Returns:
            處理後的圖片
        """
        result = image

        if rotate_angle != 0:
            result = ImageAugmenter.rotate(result, rotate_angle)

        if brightness_factor != 1.0:
            result = ImageAugmenter.adjust_brightness(result, brightness_factor)

        if scale != 1.0:
            result = ImageAugmenter.resize(result, scale)

        return result


# 預定義的變化配置
AUGMENTATION_PRESETS = {
    # 旋轉
    'rotate_15': {'rotate_angle': 15},
    'rotate_30': {'rotate_angle': 30},
    'rotate_45': {'rotate_angle': 45},
    'rotate_90': {'rotate_angle': 90},

    # 亮度
    'brightness_+30': {'brightness_factor': 1.3},
    'brightness_+50': {'brightness_factor': 1.5},
    'brightness_-30': {'brightness_factor': 0.7},
    'brightness_-50': {'brightness_factor': 0.5},

    # 模糊
    'blur_3': {'kernel_size': 3},
    'blur_5': {'kernel_size': 5},
    'blur_7': {'kernel_size': 7},

    # 裁切
    'crop_70': {'crop_ratio': 0.7},
    'crop_80': {'crop_ratio': 0.8},
    'crop_90': {'crop_ratio': 0.9},

    # 縮放
    'scale_50': {'scale': 0.5},
    'scale_75': {'scale': 0.75},
    'scale_125': {'scale': 1.25},
    'scale_150': {'scale': 1.5},

    # 組合
    'combined_1': {'rotate_angle': 15, 'brightness_factor': 1.2, 'scale': 0.9},
    'combined_2': {'rotate_angle': 30, 'brightness_factor': 0.8, 'scale': 1.1},
}
