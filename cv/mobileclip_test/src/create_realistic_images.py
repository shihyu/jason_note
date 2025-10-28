#!/usr/bin/env python3
"""生成更真實的測試圖片 - 使用 numpy 生成接近真實的圖像"""

from PIL import Image, ImageDraw, ImageFilter
import numpy as np
from pathlib import Path
from utils import setup_logger
import random

logger = setup_logger(__name__)


def create_gradient_image(width=800, height=600, colors=None):
    """創建漸層圖片"""
    if colors is None:
        colors = [(random.randint(50, 200), random.randint(50, 200), random.randint(50, 200)),
                  (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))]

    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        ratio = y / height
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def add_noise(image, amount=0.1):
    """添加雜訊"""
    img_array = np.array(image).astype(np.float32)
    noise = np.random.normal(0, amount * 255, img_array.shape)
    noisy = np.clip(img_array + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(noisy)


def create_realistic_people_image(index):
    """模擬人物圖片 - 使用膚色和形狀"""
    # 膚色範圍
    skin_tones = [
        (255, 220, 177),  # 淺膚色
        (241, 194, 125),  # 中等膚色
        (224, 172, 105),  # 棕色膚色
        (198, 134, 66),   # 深膚色
    ]

    bg_color = random.choice([(240, 240, 245), (230, 230, 235), (220, 220, 225)])
    img = Image.new('RGB', (800, 600), bg_color)
    draw = ImageDraw.Draw(img)

    # 繪製橢圓形（模擬人臉）
    face_color = skin_tones[index % len(skin_tones)]
    face_pos = (300, 150, 500, 400)
    draw.ellipse(face_pos, fill=face_color)

    # 眼睛
    draw.ellipse((350, 250, 380, 270), fill=(50, 50, 50))
    draw.ellipse((420, 250, 450, 270), fill=(50, 50, 50))

    # 嘴巴
    draw.arc((360, 300, 440, 350), 0, 180, fill=(150, 50, 50), width=3)

    # 添加雜訊使其更真實
    img = add_noise(img, 0.02)
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    return img


def create_realistic_animal_image(index):
    """模擬動物圖片"""
    # 動物顏色
    animal_colors = [
        (180, 140, 100),  # 棕色
        (220, 220, 220),  # 白色
        (100, 100, 100),  # 灰色
        (200, 150, 100),  # 淺棕色
    ]

    bg_color = random.choice([(180, 220, 180), (200, 230, 200), (160, 200, 160)])
    img = Image.new('RGB', (800, 600), bg_color)
    draw = ImageDraw.Draw(img)

    # 身體
    body_color = animal_colors[index % len(animal_colors)]
    draw.ellipse((200, 250, 600, 500), fill=body_color)

    # 頭部
    draw.ellipse((450, 150, 650, 350), fill=body_color)

    # 耳朵
    draw.ellipse((450, 100, 520, 180), fill=body_color)
    draw.ellipse((580, 100, 650, 180), fill=body_color)

    # 眼睛
    draw.ellipse((490, 200, 520, 230), fill=(0, 0, 0))
    draw.ellipse((580, 200, 610, 230), fill=(0, 0, 0))

    # 鼻子
    draw.polygon([(545, 260), (530, 280), (560, 280)], fill=(50, 50, 50))

    img = add_noise(img, 0.02)
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    return img


def create_realistic_landscape_image(index):
    """模擬風景圖片"""
    # 天空到地面的漸層
    sky_colors = [
        ((135, 206, 250), (100, 180, 220)),  # 藍天
        ((255, 200, 150), (200, 150, 100)),  # 日落
        ((100, 150, 200), (70, 120, 170)),   # 陰天
    ]

    colors = sky_colors[index % len(sky_colors)]
    img = create_gradient_image(800, 600, colors)
    draw = ImageDraw.Draw(img)

    # 地平線
    horizon_y = 400
    ground_color = (100, 150, 80)
    draw.rectangle([(0, horizon_y), (800, 600)], fill=ground_color)

    # 山脈輪廓
    points = [(0, horizon_y)]
    for x in range(0, 800, 50):
        y_offset = random.randint(-100, -20)
        points.append((x, horizon_y + y_offset))
    points.append((800, horizon_y))
    draw.polygon(points, fill=(70, 100, 60))

    # 太陽或月亮
    sun_x = 650 + index * 20
    sun_y = 150
    draw.ellipse((sun_x-40, sun_y-40, sun_x+40, sun_y+40), fill=(255, 255, 200))

    img = add_noise(img, 0.015)
    img = img.filter(ImageFilter.GaussianBlur(radius=0.5))

    return img


def create_realistic_object_image(index):
    """模擬物品圖片"""
    object_colors = [
        (200, 50, 50),   # 紅色物品
        (50, 50, 200),   # 藍色物品
        (50, 200, 50),   # 綠色物品
        (200, 200, 50),  # 黃色物品
    ]

    bg_color = (240, 240, 240)
    img = Image.new('RGB', (800, 600), bg_color)
    draw = ImageDraw.Draw(img)

    # 物品主體（立方體或圓柱體）
    obj_color = object_colors[index % len(object_colors)]

    if index % 2 == 0:
        # 立方體
        draw.rectangle((200, 200, 600, 500), fill=obj_color)
        # 陰影
        shadow_color = tuple(int(c * 0.7) for c in obj_color)
        draw.polygon([(600, 200), (700, 150), (700, 450), (600, 500)], fill=shadow_color)
    else:
        # 圓柱體
        draw.ellipse((250, 180, 550, 240), fill=obj_color)
        draw.rectangle((250, 210, 550, 500), fill=obj_color)
        draw.ellipse((250, 470, 550, 530), fill=tuple(int(c * 0.8) for c in obj_color))

    img = add_noise(img, 0.02)
    img = img.filter(ImageFilter.SMOOTH)

    return img


def generate_realistic_dataset(output_dir='tests/fixtures/real_images'):
    """生成更真實的圖片數據集"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    logger.info("生成更真實的測試圖片...")
    logger.info(f"儲存位置: {output_path}")

    generators = {
        'people': create_realistic_people_image,
        'animals': create_realistic_animal_image,
        'landscape': create_realistic_landscape_image,
        'objects': create_realistic_object_image,
    }

    count = 0
    for category, generator_func in generators.items():
        logger.info(f"\n生成 {category} 類別...")

        for i in range(5):
            filename = f"{category}_{i+1:02d}.jpg"
            save_path = output_path / filename

            # 生成圖片
            img = generator_func(i)

            # 儲存
            img.save(save_path, 'JPEG', quality=95)
            logger.info(f"  ✓ {filename}")
            count += 1

    logger.info(f"\n✓ 完成！共生成 {count} 張更真實的圖片")
    return count


if __name__ == '__main__':
    generate_realistic_dataset()
