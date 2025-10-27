#!/usr/bin/env python3
"""下載測試圖片

從 Unsplash Source API 下載測試圖片
"""

import requests
from pathlib import Path
import time
from utils import setup_logger

logger = setup_logger(__name__)


CATEGORIES = {
    'people': ['portrait', 'person', 'face', 'woman', 'man'],
    'animals': ['dog', 'cat', 'bird', 'wildlife', 'pet'],
    'landscape': ['mountain', 'beach', 'forest', 'sunset', 'nature'],
    'objects': ['car', 'food', 'building', 'phone', 'computer']
}


def download_image(url: str, save_path: Path) -> bool:
    """下載單張圖片"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(save_path, 'wb') as f:
            f.write(response.content)

        return True

    except Exception as e:
        logger.error(f"下載失敗: {e}")
        return False


def download_test_images(output_dir: str = 'tests/fixtures/database'):
    """下載測試圖片"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info("開始下載測試圖片...")
    logger.info(f"儲存位置: {output_path}")

    total_downloaded = 0

    for category, keywords in CATEGORIES.items():
        logger.info(f"\n下載 {category} 類別圖片...")

        for i, keyword in enumerate(keywords, 1):
            filename = f"{category}_{i:02d}_{keyword}.jpg"
            save_path = output_path / filename

            if save_path.exists():
                logger.info(f"  ✓ {filename} (已存在)")
                total_downloaded += 1
                continue

            # Unsplash Source API
            url = f"https://source.unsplash.com/800x600/?{keyword}"

            logger.info(f"  下載 {filename}...")

            if download_image(url, save_path):
                logger.info(f"  ✓ {filename}")
                total_downloaded += 1
            else:
                logger.warning(f"  ✗ {filename} 下載失敗")

            # 避免請求過快
            time.sleep(1)

    logger.info(f"\n下載完成！共 {total_downloaded} 張圖片")
    return total_downloaded


if __name__ == '__main__':
    download_test_images()
