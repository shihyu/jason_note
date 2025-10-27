#!/usr/bin/env python3
"""使用真實圖片測試 MobileCLIP 以圖找圖功能

比較真實圖片與合成圖片的測試結果
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


def test_with_images(image_dir: str, test_name: str = "測試"):
    """使用指定圖片目錄進行測試"""

    logger.info(f"\n{'='*60}")
    logger.info(f"{test_name}")
    logger.info(f"圖片目錄: {image_dir}")
    logger.info(f"{'='*60}")

    # 測試圖片
    test_images = [
        f'{image_dir}/people_01.jpg',
        f'{image_dir}/animals_01.jpg',
        f'{image_dir}/landscape_01.jpg',
        f'{image_dir}/objects_01.jpg',
    ]

    # 測試變化
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

    # 測試 S0 模型
    logger.info("\n使用 MobileCLIP-S0 模型...")
    engine = MobileCLIPSearchEngine(model_name='mobileclip_s0')

    # 建立索引
    index_info = engine.build_index(image_dir)
    logger.info(f"索引: {index_info['num_images']} 張圖片")
    logger.info(f"建立時間: {format_time(index_info['time'])}")

    # 測試各種變化
    logger.info(f"\n測試圖片搜尋...")
    results = {}

    for aug_name, aug_config in augmentations.items():
        correct = 0
        total_time = 0

        for img_path in test_images:
            # 載入原圖
            original = Image.open(img_path).convert('RGB')

            # 套用變化
            if not aug_config:
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
            'avg_time_ms': avg_time,
            'correct': correct,
            'total': len(test_images)
        }

    return results


def main():
    """主程式"""
    logger.info("="*60)
    logger.info("真實圖片 vs 合成圖片測試比較")
    logger.info("="*60)

    # 測試合成圖片
    logger.info("\n【測試 1】合成圖片 (簡單幾何圖形)")
    synthetic_results = test_with_images(
        'tests/fixtures/database',
        "合成圖片測試"
    )

    # 測試真實圖片
    logger.info("\n【測試 2】真實圖片 (更接近真實場景)")
    real_results = test_with_images(
        'tests/fixtures/real_images',
        "真實圖片測試"
    )

    # 比較結果
    logger.info("\n" + "="*60)
    logger.info("測試結果比較")
    logger.info("="*60)

    logger.info("\n準確度比較 (%):")
    logger.info(f"{'變化類型':<15} {'合成圖片':>10} {'真實圖片':>10} {'差異':>10}")
    logger.info("-" * 50)

    total_synthetic = 0
    total_real = 0
    count = 0

    for aug_name in synthetic_results.keys():
        syn_acc = synthetic_results[aug_name]['accuracy']
        real_acc = real_results[aug_name]['accuracy']
        diff = real_acc - syn_acc

        total_synthetic += syn_acc
        total_real += real_acc
        count += 1

        diff_str = f"{diff:+.1f}%"
        logger.info(f"{aug_name:<15} {syn_acc:>9.1f}% {real_acc:>9.1f}% {diff_str:>10}")

    logger.info("-" * 50)
    avg_syn = total_synthetic / count
    avg_real = total_real / count
    avg_diff = avg_real - avg_syn

    logger.info(f"{'平均':<15} {avg_syn:>9.1f}% {avg_real:>9.1f}% {avg_diff:+.1f}%")

    logger.info("\n搜尋速度比較 (ms):")
    logger.info(f"{'變化類型':<15} {'合成圖片':>10} {'真實圖片':>10} {'差異':>10}")
    logger.info("-" * 50)

    total_syn_time = 0
    total_real_time = 0

    for aug_name in synthetic_results.keys():
        syn_time = synthetic_results[aug_name]['avg_time_ms']
        real_time = real_results[aug_name]['avg_time_ms']
        diff = real_time - syn_time

        total_syn_time += syn_time
        total_real_time += real_time

        diff_str = f"{diff:+.2f}ms"
        logger.info(f"{aug_name:<15} {syn_time:>9.2f} {real_time:>9.2f} {diff_str:>10}")

    logger.info("-" * 50)
    avg_syn_time = total_syn_time / count
    avg_real_time = total_real_time / count
    avg_time_diff = avg_real_time - avg_syn_time

    logger.info(f"{'平均':<15} {avg_syn_time:>9.2f} {avg_real_time:>9.2f} {avg_time_diff:+.2f}ms")

    # 總結
    logger.info("\n" + "="*60)
    logger.info("測試結論")
    logger.info("="*60)

    if avg_real >= 90:
        logger.info("✅ 真實圖片準確度優異 (>90%)")
    elif avg_real >= 80:
        logger.info("⚠️  真實圖片準確度良好 (80-90%)")
    else:
        logger.info("❌ 真實圖片準確度需改進 (<80%)")

    logger.info(f"\n真實圖片平均準確度: {avg_real:.1f}%")
    logger.info(f"合成圖片平均準確度: {avg_syn:.1f}%")
    logger.info(f"差異: {avg_diff:+.1f}%")

    if abs(avg_diff) < 5:
        logger.info("→ 兩者表現相近")
    elif avg_diff > 0:
        logger.info("→ 真實圖片表現更好")
    else:
        logger.info("→ 合成圖片表現更好")

    logger.info("\n" + "="*60)
    logger.info("✓ 測試完成！")
    logger.info("="*60)


if __name__ == '__main__':
    main()
