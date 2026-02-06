import os
import cv2
import supervision as sv
import glob
from pathlib import Path

def main():
    DATASET_DIR = "data/dataset"
    OUTPUT_DIR = "data/visualizations"
    
    if not os.path.exists(DATASET_DIR):
        print(f"Error: Dataset directory {DATASET_DIR} not found. Run 'make run' first.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 1. 載入 YOLO 格式資料集
    # 我們分別處理 train 和 valid
    for split in ["train", "valid"]:
        images_path = os.path.join(DATASET_DIR, split, "images")
        annotations_path = os.path.join(DATASET_DIR, split, "labels")
        data_yaml_path = os.path.join(DATASET_DIR, "data.yaml")

        if not os.path.exists(images_path):
            continue

        print(f"Processing {split} split...")
        
        # 使用 supervision 載入資料集
        dataset = sv.DetectionDataset.from_yolo(
            images_directory_path=images_path,
            annotations_directory_path=annotations_path,
            data_yaml_path=data_yaml_path
        )

        box_annotator = sv.BoxAnnotator()
        label_annotator = sv.LabelAnnotator()

        # 2. 為每張圖片產生標記圖
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

            # 儲存到可視化目錄
            output_file = os.path.join(OUTPUT_DIR, f"{split}_{image_name}")
            cv2.imwrite(output_file, annotated_frame)
    
    print(f"Successfully generated labeled images in: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
