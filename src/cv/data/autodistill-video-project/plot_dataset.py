import os
import cv2
import supervision as sv
import glob
from pathlib import Path

def plot_dataset(dataset_dir: str, output_dir: str, dataset_name: str):
    """
    為單一資料集產生標記預覽圖
    """
    print(f"\nProcessing dataset: {dataset_name}")

    box_annotator = sv.BoxAnnotator()
    label_annotator = sv.LabelAnnotator()

    total_images = 0

    # 處理 train 和 valid 兩個 split
    for split in ["train", "valid"]:
        images_path = os.path.join(dataset_dir, split, "images")
        annotations_path = os.path.join(dataset_dir, split, "labels")
        data_yaml_path = os.path.join(dataset_dir, "data.yaml")

        if not os.path.exists(images_path):
            continue

        print(f"  Processing {split} split...")

        # 使用 supervision 載入資料集
        dataset = sv.DetectionDataset.from_yolo(
            images_directory_path=images_path,
            annotations_directory_path=annotations_path,
            data_yaml_path=data_yaml_path
        )

        # 為每張圖片產生標記圖
        for image_path, _, detections in dataset:
            image_name = os.path.basename(image_path)
            image = cv2.imread(image_path)

            labels = [
                f"{dataset.classes[class_id]}"
                for class_id in detections.class_id
            ]

            annotated_frame = box_annotator.annotate(
                scene=image.copy(),
                detections=detections
            )
            annotated_frame = label_annotator.annotate(
                scene=annotated_frame,
                detections=detections,
                labels=labels
            )

            # 儲存到可視化目錄（包含資料集名稱和 split）
            output_file = os.path.join(output_dir, f"{dataset_name}_{split}_{image_name}")
            cv2.imwrite(output_file, annotated_frame)
            total_images += 1

    print(f"  ✓ Generated {total_images} labeled images")

def main():
    DATASETS_ROOT = "data/datasets"
    OUTPUT_DIR = "data/visualizations"

    if not os.path.exists(DATASETS_ROOT):
        print(f"Error: Datasets directory {DATASETS_ROOT} not found. Run 'make run' first.")
        return

    # 掃描所有影片資料集
    dataset_dirs = [d for d in os.listdir(DATASETS_ROOT)
                   if os.path.isdir(os.path.join(DATASETS_ROOT, d))]

    if not dataset_dirs:
        print(f"Error: No datasets found in {DATASETS_ROOT}")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Found {len(dataset_dirs)} dataset(s) to visualize:")
    for dataset_name in dataset_dirs:
        print(f"  - {dataset_name}")

    # 處理每個資料集
    for dataset_name in dataset_dirs:
        dataset_path = os.path.join(DATASETS_ROOT, dataset_name)
        try:
            plot_dataset(dataset_path, OUTPUT_DIR, dataset_name)
        except Exception as e:
            print(f"Error processing {dataset_name}: {e}")
            continue

    print(f"\n{'='*60}")
    print(f"All visualizations saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
