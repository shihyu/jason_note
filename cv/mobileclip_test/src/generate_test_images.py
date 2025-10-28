#!/usr/bin/env python3
"""生成測試圖片 - 用於測試目的"""

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from pathlib import Path
from utils import setup_logger

logger = setup_logger(__name__)


def generate_test_image(width: int = 800, height: int = 600,
                       color: tuple = (100, 150, 200),
                       text: str = "Test") -> Image.Image:
    """生成測試圖片"""
    # 建立圖片
    image = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(image)

    # 繪製一些圖形
    # 矩形
    draw.rectangle([50, 50, 250, 200], outline='white', width=3)

    # 圓形
    draw.ellipse([300, 100, 500, 300], fill='yellow', outline='red', width=2)

    # 線條
    draw.line([100, 400, 700, 500], fill='green', width=5)

    # 多邊形
    draw.polygon([(600, 100), (700, 200), (650, 300)], fill='purple')

    # 文字
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    text_position = (width // 2 - 100, height // 2)
    draw.text(text_position, text, fill='white', font=font)

    return image


def generate_test_dataset(output_dir: str = 'tests/fixtures/database', num_images: int = 20):
    """生成測試圖片集"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"生成 {num_images} 張測試圖片...")
    logger.info(f"儲存位置: {output_path}")

    categories = {
        'people': [(220, 180, 150), (200, 160, 130), (180, 140, 110), (160, 120, 90), (140, 100, 70)],
        'animals': [(180, 140, 100), (160, 120, 80), (140, 100, 60), (120, 80, 40), (100, 60, 20)],
        'landscape': [(135, 206, 250), (70, 130, 180), (25, 25, 112), (0, 100, 200), (0, 50, 150)],
        'objects': [(220, 20, 60), (178, 34, 34), (139, 0, 0), (100, 0, 0), (80, 0, 0)],
    }

    count = 0
    for category, colors in categories.items():
        for i, color in enumerate(colors, 1):
            filename = f"{category}_{i:02d}.jpg"
            save_path = output_path / filename

            # 生成圖片
            text = f"{category.upper()} {i}"
            image = generate_test_image(color=color, text=text)

            # 儲存
            image.save(save_path, 'JPEG', quality=95)
            logger.info(f"  ✓ {filename}")

            count += 1

    logger.info(f"\n✓ 完成！共生成 {count} 張圖片")
    return count


if __name__ == '__main__':
    generate_test_dataset()
