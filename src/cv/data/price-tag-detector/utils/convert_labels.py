"""轉換手動標註（LabelMe JSON）為 YOLO 格式並分割資料集"""
import json
import shutil
from pathlib import Path
import cv2


def convert_labelme_to_yolo(json_path, img_width, img_height):
    """將 LabelMe JSON 轉換為 YOLO 格式

    Args:
        json_path: JSON 標註文件路徑
        img_width: 圖片寬度
        img_height: 圖片高度

    Returns:
        YOLO 格式標籤列表
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    yolo_labels = []
    for shape in data.get('shapes', []):
        if shape['shape_type'] != 'rectangle':
            continue

        label = shape['label']
        # label "1" -> class 0
        class_id = int(label) - 1 if label.isdigit() else 0

        points = shape['points']
        x1, y1 = points[0]
        x2, y2 = points[1]

        # 計算中心點和寬高（歸一化）
        x_center = ((x1 + x2) / 2) / img_width
        y_center = ((y1 + y2) / 2) / img_height
        width = abs(x2 - x1) / img_width
        height = abs(y2 - y1) / img_height

        yolo_labels.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}")

    return yolo_labels


def main():
    """主函數：轉換標註並分割資料集"""
    manual_dir = Path("data/manual_labels")
    output_dir = Path("data/dataset")

    # 創建輸出目錄
    for split in ['train', 'valid']:
        (output_dir / split / 'images').mkdir(parents=True, exist_ok=True)
        (output_dir / split / 'labels').mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("轉換手動標註 LabelMe → YOLO")
    print("=" * 60)

    # 收集所有有標註的圖片
    all_samples = []

    for video_dir in sorted(manual_dir.iterdir()):
        if not video_dir.is_dir():
            continue

        video_name = video_dir.name
        print(f"\n處理 {video_name}...")

        for json_file in sorted(video_dir.glob("*.json")):
            # 對應的圖片在 data/images/video_name/ 目錄
            img_name = json_file.stem + '.jpg'
            img_file = Path(f"data/images/{video_name}/{img_name}")

            if not img_file.exists():
                print(f"  ⚠️  找不到圖片: {img_file}")
                continue

            # 讀取圖片尺寸
            img = cv2.imread(str(img_file))
            if img is None:
                print(f"  ⚠️  無法讀取: {img_file}")
                continue

            img_height, img_width = img.shape[:2]

            # 轉換標註
            yolo_labels = convert_labelme_to_yolo(json_file, img_width, img_height)

            if not yolo_labels:
                continue

            all_samples.append({
                'video': video_name,
                'img_file': img_file,
                'img_name': img_name,
                'labels': yolo_labels,
                'label_count': len(yolo_labels)
            })

            print(f"  ✓ {img_name}: {len(yolo_labels)} 個標記")

    # 分割資料集 (80% train, 20% valid)
    import random
    random.seed(42)
    random.shuffle(all_samples)

    split_idx = int(len(all_samples) * 0.8)
    train_samples = all_samples[:split_idx]
    valid_samples = all_samples[split_idx:]

    print(f"\n{'=' * 60}")
    print(f"資料集分割")
    print(f"{'=' * 60}")
    print(f"訓練集: {len(train_samples)} 張")
    print(f"驗證集: {len(valid_samples)} 張")

    # 保存訓練集
    print(f"\n保存訓練集...")
    for sample in train_samples:
        new_img_name = f"{sample['video']}_{sample['img_name']}"
        new_lbl_name = f"{sample['video']}_{sample['img_name'].replace('.jpg', '.txt')}"

        shutil.copy(sample['img_file'], output_dir / 'train' / 'images' / new_img_name)

        with open(output_dir / 'train' / 'labels' / new_lbl_name, 'w') as f:
            f.write('\n'.join(sample['labels']))

    # 保存驗證集
    print(f"保存驗證集...")
    for sample in valid_samples:
        new_img_name = f"{sample['video']}_{sample['img_name']}"
        new_lbl_name = f"{sample['video']}_{sample['img_name'].replace('.jpg', '.txt')}"

        shutil.copy(sample['img_file'], output_dir / 'valid' / 'images' / new_img_name)

        with open(output_dir / 'valid' / 'labels' / new_lbl_name, 'w') as f:
            f.write('\n'.join(sample['labels']))

    # 創建 data.yaml
    yaml_content = f"""path: {output_dir.absolute()}
train: train/images
val: valid/images

nc: 1
names: ['price_tag']
"""

    with open(output_dir / "data.yaml", 'w') as f:
        f.write(yaml_content)

    print(f"\n{'=' * 60}")
    print(f"轉換完成！")
    print(f"{'=' * 60}")
    print(f"總共轉換: {len(all_samples)} 張圖片")
    print(f"  訓練集: {len(train_samples)} 張")
    print(f"  驗證集: {len(valid_samples)} 張")
    print(f"輸出位置: {output_dir}")
    print(f"✓ 已創建 data.yaml")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
