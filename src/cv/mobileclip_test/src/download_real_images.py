#!/usr/bin/env python3
"""下載真實圖片進行測試

使用 Pexels API 或其他免費圖片源
"""

import os
import requests
from pathlib import Path
import time
from utils import setup_logger

logger = setup_logger(__name__)


def download_from_picsum(output_dir: str = 'tests/fixtures/real_images', count: int = 20):
    """
    從 Lorem Picsum (免費圖片服務) 下載真實圖片
    https://picsum.photos/
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"從 Lorem Picsum 下載 {count} 張真實圖片...")
    logger.info(f"儲存位置: {output_path}")

    # 使用不同的圖片 ID
    base_ids = list(range(1, 1001, 50))  # 從 1000+ 圖片中挑選

    categories = {
        'people': base_ids[:5],
        'animals': base_ids[5:10],
        'landscape': base_ids[10:15],
        'objects': base_ids[15:20],
    }

    downloaded = 0
    failed = []

    for category, img_ids in categories.items():
        logger.info(f"\n下載 {category} 類別...")

        for i, img_id in enumerate(img_ids, 1):
            filename = f"{category}_{i:02d}.jpg"
            save_path = output_path / filename

            if save_path.exists():
                logger.info(f"  ✓ {filename} (已存在)")
                downloaded += 1
                continue

            # Lorem Picsum API
            url = f"https://picsum.photos/id/{img_id}/800/600.jpg"

            try:
                logger.info(f"  下載 {filename} (ID: {img_id})...")
                response = requests.get(url, timeout=15)
                response.raise_for_status()

                with open(save_path, 'wb') as f:
                    f.write(response.content)

                logger.info(f"  ✓ {filename}")
                downloaded += 1

                # 避免請求過快
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"  ✗ {filename} 下載失敗: {e}")
                failed.append(filename)

    logger.info(f"\n{'='*60}")
    logger.info(f"下載完成！")
    logger.info(f"  成功: {downloaded} 張")
    logger.info(f"  失敗: {len(failed)} 張")
    if failed:
        logger.info(f"  失敗檔案: {', '.join(failed)}")
    logger.info(f"{'='*60}")

    return downloaded


if __name__ == '__main__':
    download_from_picsum()
