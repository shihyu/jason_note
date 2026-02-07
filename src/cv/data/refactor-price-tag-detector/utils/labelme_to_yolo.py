#!/usr/bin/env python3
"""將 labelme 標註轉換為 YOLO 格式

從 manual_labels/（labelme JSON）轉換為 dataset/（YOLO txt）
用於訓練 YOLO 模型。

使用方式：
    python utils/labelme_to_yolo.py --input data/manual_labels --output data/dataset
"""

import argparse
import json
import shutil
from pathlib import Path
from typing import List, Tuple


def labelme_to_yolo_bbox(
    points: List[List[float]], img_width: int, img_height: int
) -> Tuple[float, float, float, float]:
    """將 labelme 矩形座標轉換為 YOLO 格式

    Args:
        points: labelme 矩形的兩個點 [[x1, y1], [x2, y2]]
        img_width: 圖片寬度
        img_height: 圖片高度

    Returns:
        (x_center, y_center, width, height) 相對於圖片大小的比例（0-1）
    """
    x1, y1 = points[0]
    x2, y2 = points[1]

    # 計算中心點和寬高
    x_center = (x1 + x2) / 2
    y_center = (y1 + y2) / 2
    width = abs(x2 - x1)
    height = abs(y2 - y1)

    # 轉換為相對座標（0-1）
    x_center_norm = x_center / img_width
    y_center_norm = y_center / img_height
    width_norm = width / img_width
    height_norm = height / img_height

    return x_center_norm, y_center_norm, width_norm, height_norm


def convert_labelme_to_yolo(
    json_path: Path, output_dir: Path, class_id: int = 0
) -> bool:
    """轉換單個 labelme JSON 檔案為 YOLO txt 格式

    Args:
        json_path: labelme JSON 檔案路徑
        output_dir: 輸出目錄
        class_id: YOLO 類別 ID（預設 0 = price_tag）

    Returns:
        是否成功轉換
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        img_width = data.get('imageWidth')
        img_height = data.get('imageHeight')
        shapes = data.get('shapes', [])

        if not img_width or not img_height:
            print(f"⚠️  跳過 {json_path.name}: 缺少圖片尺寸資訊")
            return False

        if not shapes:
            print(f"⚠️  跳過 {json_path.name}: 沒有標註")
            return False

        # 建立 YOLO txt 檔案
        txt_path = output_dir / f"{json_path.stem}.txt"

        with open(txt_path, 'w', encoding='utf-8') as f:
            for shape in shapes:
                if shape['shape_type'] != 'rectangle':
                    continue

                points = shape['points']
                if len(points) != 2:
                    continue

                # 轉換為 YOLO 格式
                x_center, y_center, width, height = labelme_to_yolo_bbox(
                    points, img_width, img_height
                )

                # 寫入 YOLO 格式：<class_id> <x_center> <y_center> <width> <height>
                f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

        return True

    except Exception as e:
        print(f"✗ 轉換失敗 {json_path.name}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='將 labelme 標註轉換為 YOLO 格式')
    parser.add_argument(
        '--input',
        type=str,
        default='data/manual_labels',
        help='輸入目錄（manual_labels）'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='data/dataset',
        help='輸出目錄（dataset）'
    )
    parser.add_argument(
        '--train-ratio',
        type=float,
        default=0.8,
        help='訓練集比例（預設 0.8 = 80%）'
    )

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    train_ratio = args.train_ratio

    if not input_dir.exists():
        print(f"✗ 錯誤：輸入目錄不存在: {input_dir}")
        return 1

    print("=" * 60)
    print("labelme → YOLO 轉換工具")
    print("=" * 60)
    print(f"輸入: {input_dir}")
    print(f"輸出: {output_dir}")
    print(f"訓練集比例: {train_ratio * 100:.0f}%")
    print()

    # 建立輸出目錄
    train_images_dir = output_dir / "train" / "images"
    train_labels_dir = output_dir / "train" / "labels"
    valid_images_dir = output_dir / "valid" / "images"
    valid_labels_dir = output_dir / "valid" / "labels"

    for dir_path in [train_images_dir, train_labels_dir, valid_images_dir, valid_labels_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)

    # 收集所有影片目錄
    video_dirs = [d for d in input_dir.iterdir() if d.is_dir()]

    if not video_dirs:
        print(f"✗ 錯誤：找不到影片目錄在 {input_dir}")
        return 1

    print(f"找到 {len(video_dirs)} 個影片目錄")
    print()

    total_converted = 0
    total_train = 0
    total_valid = 0

    # 處理每個影片目錄
    for video_dir in sorted(video_dirs):
        print(f"處理 {video_dir.name}...")

        # 找到所有 JSON 檔案
        json_files = sorted(video_dir.glob("*.json"))

        if not json_files:
            print(f"  ⚠️  沒有找到 JSON 檔案")
            continue

        # 分割訓練集和驗證集
        split_idx = int(len(json_files) * train_ratio)
        train_files = json_files[:split_idx]
        valid_files = json_files[split_idx:]

        # 轉換訓練集
        for json_file in train_files:
            # 複製圖片
            img_file = json_file.with_suffix('.jpg')
            if img_file.exists():
                shutil.copy(img_file, train_images_dir / img_file.name)

                # 轉換標註
                if convert_labelme_to_yolo(json_file, train_labels_dir):
                    total_converted += 1
                    total_train += 1

        # 轉換驗證集
        for json_file in valid_files:
            # 複製圖片
            img_file = json_file.with_suffix('.jpg')
            if img_file.exists():
                shutil.copy(img_file, valid_images_dir / img_file.name)

                # 轉換標註
                if convert_labelme_to_yolo(json_file, valid_labels_dir):
                    total_converted += 1
                    total_valid += 1

        print(f"  ✓ 轉換 {len(train_files)} 個訓練樣本，{len(valid_files)} 個驗證樣本")

    # 建立 data.yaml
    data_yaml = output_dir / "data.yaml"
    data_yaml_content = f"""path: {output_dir.absolute()}
train: train/images
val: valid/images

nc: 1
names: ['price_tag']
"""

    with open(data_yaml, 'w', encoding='utf-8') as f:
        f.write(data_yaml_content)

    print()
    print("=" * 60)
    print("✓ 轉換完成！")
    print("=" * 60)
    print(f"總共轉換: {total_converted} 個檔案")
    print(f"  - 訓練集: {total_train} 個")
    print(f"  - 驗證集: {total_valid} 個")
    print()
    print(f"輸出目錄: {output_dir}")
    print(f"配置檔案: {data_yaml}")
    print()
    print("下一步：訓練模型")
    print(f"  uv run python src/trainer.py --data {data_yaml} --epochs 100")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    exit(main())
