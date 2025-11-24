#!/usr/bin/env python3
"""MobileCLIP 以圖找圖完整演示

測試不同變化對搜尋準確度的影響:
- 旋轉 (15°, 30°, 45°, 90°)
- 亮度調整 (±30%, ±50%)
- 模糊 (kernel 3, 5, 7)
- 裁切 (70%, 80%, 90%)
- 縮放 (50%, 75%, 125%, 150%)
- 組合變化

比較三個模型 (S0, S1, S2) 的:
- 準確度
- 速度
"""

import sys
sys.path.insert(0, 'src')

from pathlib import Path
from PIL import Image
import time
import numpy as np

from image_search import MobileCLIPSearchEngine
from image_augmentation import ImageAugmenter
from utils import setup_logger, format_time

logger = setup_logger(__name__)


def test_model(model_name: str, test_images: list, augmentations: dict):
    """測試單個模型"""
    logger.info(f"\n{'='*60}")
    logger.info(f"測試 {model_name}")
    logger.info(f"{'='*60}")

    # 建立搜尋引擎
    engine = MobileCLIPSearchEngine(model_name=model_name)

    # 建立索引
    logger.info("\n1. 建立圖片索引...")
    index_info = engine.build_index('tests/fixtures/database')
    logger.info(f"   索引: {index_info['num_images']} 張圖片")
    logger.info(f"   特徵維度: {index_info['feature_dim']}")
    logger.info(f"   建立時間: {format_time(index_info['time'])}")
    logger.info(f"   平均速度: {index_info['avg_time_per_image']*1000:.2f}ms/張")

    # 測試各種變化
    logger.info(f"\n2. 測試圖片搜尋 (使用 {len(test_images)} 張測試圖)")

    results = {}

    for aug_name, aug_config in augmentations.items():
        logger.info(f"\n   測試: {aug_name}")

        correct = 0
        total_time = 0

        for img_path in test_images:
            # 載入原圖
            original = Image.open(img_path).convert('RGB')

            # 套用變化
            if not aug_config:
                # 原始圖片
                query = original
            elif 'kernel_size' in aug_config:
                query = ImageAugmenter.blur(original, aug_config['kernel_size'])
            elif 'crop_ratio' in aug_config:
                query = ImageAugmenter.center_crop(original, aug_config['crop_ratio'])
            elif 'scale' in aug_config and len(aug_config) == 1:
                query = ImageAugmenter.resize(original, aug_config['scale'])
            elif 'rotate_angle' in aug_config and len(aug_config) == 1:
                query = ImageAugmenter.rotate(original, aug_config['rotate_angle'])
            elif 'brightness_factor' in aug_config and len(aug_config) == 1:
                query = ImageAugmenter.adjust_brightness(original, aug_config['brightness_factor'])
            else:
                # 組合變化
                query = ImageAugmenter.combined(original, **aug_config)

            # 搜尋
            start = time.time()
            search_results = engine.search(query, top_k=1)
            elapsed = time.time() - start
            total_time += elapsed

            # 檢查是否正確
            top1_path = search_results[0][0]
            if Path(top1_path).name == Path(img_path).name:
                correct += 1

        accuracy = (correct / len(test_images)) * 100
        avg_time = (total_time / len(test_images)) * 1000

        results[aug_name] = {
            'accuracy': accuracy,
            'avg_time_ms': avg_time
        }

        logger.info(f"      準確度: {accuracy:.1f}% ({correct}/{len(test_images)})")
        logger.info(f"      平均搜尋時間: {avg_time:.2f}ms")

    return results


def main():
    """主程式"""
    logger.info("="*60)
    logger.info("MobileCLIP 以圖找圖完整測試")
    logger.info("="*60)

    # 選擇測試圖片 (每個類別選1張)
    test_images = [
        'tests/fixtures/database/people_01.jpg',
        'tests/fixtures/database/animals_01.jpg',
        'tests/fixtures/database/landscape_01.jpg',
        'tests/fixtures/database/objects_01.jpg',
    ]

    logger.info(f"\n測試圖片: {len(test_images)} 張")
    for img in test_images:
        logger.info(f"  - {Path(img).name}")

    # 定義測試的變化
    augmentations = {
        '原始圖片': {},
        '旋轉15度': {'rotate_angle': 15},
        '旋轉30度': {'rotate_angle': 30},
        '旋轉45度': {'rotate_angle': 45},
        '亮度+30%': {'brightness_factor': 1.3},
        '亮度-30%': {'brightness_factor': 0.7},
        '模糊(k=3)': {'kernel_size': 3},
        '模糊(k=5)': {'kernel_size': 5},
        '裁切80%': {'crop_ratio': 0.8},
        '縮放75%': {'scale': 0.75},
        '縮放125%': {'scale': 1.25},
        '組合變化': {'rotate_angle': 15, 'brightness_factor': 1.2, 'scale': 0.9},
    }

    # 測試三個模型
    all_results = {}
    models = ['mobileclip_s0', 'mobileclip_s1', 'mobileclip_s2']

    for model_name in models:
        results = test_model(model_name, test_images, augmentations)
        all_results[model_name] = results

    # 總結報告
    logger.info("\n" + "="*60)
    logger.info("測試總結")
    logger.info("="*60)

    logger.info("\n準確度比較 (%):")
    logger.info(f"{'變化類型':<15} {'S0':>8} {'S1':>8} {'S2':>8}")
    logger.info("-" * 45)

    for aug_name in augmentations.keys():
        s0_acc = all_results['mobileclip_s0'][aug_name]['accuracy']
        s1_acc = all_results['mobileclip_s1'][aug_name]['accuracy']
        s2_acc = all_results['mobileclip_s2'][aug_name]['accuracy']

        logger.info(f"{aug_name:<15} {s0_acc:>7.1f}% {s1_acc:>7.1f}% {s2_acc:>7.1f}%")

    logger.info("\n平均搜尋時間 (ms):")
    logger.info(f"{'變化類型':<15} {'S0':>8} {'S1':>8} {'S2':>8}")
    logger.info("-" * 45)

    for aug_name in augmentations.keys():
        s0_time = all_results['mobileclip_s0'][aug_name]['avg_time_ms']
        s1_time = all_results['mobileclip_s1'][aug_name]['avg_time_ms']
        s2_time = all_results['mobileclip_s2'][aug_name]['avg_time_ms']

        logger.info(f"{aug_name:<15} {s0_time:>7.2f} {s1_time:>7.2f} {s2_time:>7.2f}")

    logger.info("\n" + "="*60)
    logger.info("✓ 測試完成！")
    logger.info("="*60)


if __name__ == '__main__':
    main()
