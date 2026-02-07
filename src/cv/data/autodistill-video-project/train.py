import os
import torch
from ultralytics import YOLO
import glob

# 設置環境變數以允許載入舊版 YOLOv8 權重（PyTorch 2.6+ 需要）
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['TORCH_LOAD_WEIGHTS_ONLY'] = '0'

def merge_datasets(datasets_root: str = "data/datasets", output_dir: str = "data/merged_dataset"):
    """
    合併所有影片資料集成一個統一的訓練集
    """
    import shutil
    import yaml

    print("Merging datasets...")

    # 獲取所有資料集
    dataset_dirs = [d for d in os.listdir(datasets_root)
                   if os.path.isdir(os.path.join(datasets_root, d))]

    if not dataset_dirs:
        print(f"Error: No datasets found in {datasets_root}")
        return None

    print(f"Found {len(dataset_dirs)} dataset(s): {', '.join(dataset_dirs)}")

    # 創建合併的資料集目錄
    os.makedirs(os.path.join(output_dir, "train", "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "train", "labels"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "valid", "images"), exist_ok=True)
    os.makedirs(os.path.join(output_dir, "valid", "labels"), exist_ok=True)

    # 讀取第一個資料集的 data.yaml 來獲取類別信息
    first_dataset = os.path.join(datasets_root, dataset_dirs[0])
    with open(os.path.join(first_dataset, "data.yaml"), 'r') as f:
        data_yaml = yaml.safe_load(f)

    # 合併所有資料集
    total_train_images = 0
    total_valid_images = 0

    for dataset_name in dataset_dirs:
        dataset_path = os.path.join(datasets_root, dataset_name)

        # 複製 train 資料
        for split in ["train", "valid"]:
            src_images = os.path.join(dataset_path, split, "images")
            src_labels = os.path.join(dataset_path, split, "labels")
            dst_images = os.path.join(output_dir, split, "images")
            dst_labels = os.path.join(output_dir, split, "labels")

            if not os.path.exists(src_images):
                continue

            # 複製圖片
            for img_file in glob.glob(os.path.join(src_images, "*.jpg")):
                img_name = f"{dataset_name}_{os.path.basename(img_file)}"
                shutil.copy(img_file, os.path.join(dst_images, img_name))

                if split == "train":
                    total_train_images += 1
                else:
                    total_valid_images += 1

            # 複製標籤
            for label_file in glob.glob(os.path.join(src_labels, "*.txt")):
                label_name = f"{dataset_name}_{os.path.basename(label_file)}"
                shutil.copy(label_file, os.path.join(dst_labels, label_name))

    # 創建合併後的 data.yaml
    merged_yaml = {
        'names': data_yaml['names'],
        'nc': data_yaml['nc'],
        'train': os.path.abspath(os.path.join(output_dir, "train", "images")),
        'val': os.path.abspath(os.path.join(output_dir, "valid", "images"))
    }

    yaml_path = os.path.join(output_dir, "data.yaml")
    with open(yaml_path, 'w') as f:
        yaml.dump(merged_yaml, f, default_flow_style=False)

    print(f"✓ Merged dataset created:")
    print(f"  - Train images: {total_train_images}")
    print(f"  - Valid images: {total_valid_images}")
    print(f"  - Classes: {data_yaml['names']}")
    print(f"  - Config: {yaml_path}")

    return yaml_path

def train_model(data_yaml: str, epochs: int = 50, imgsz: int = 640, batch: int = 16):
    """
    訓練 YOLOv8 模型
    """
    print(f"\n{'='*60}")
    print("Starting YOLOv8 Training")
    print(f"{'='*60}")
    print(f"Configuration:")
    print(f"  - Epochs: {epochs}")
    print(f"  - Image size: {imgsz}")
    print(f"  - Batch size: {batch}")
    print(f"  - Data config: {data_yaml}")
    print(f"{'='*60}\n")

    # 載入 YOLOv8 nano 模型（輕量快速）
    model = YOLO('yolov8n.pt')

    # 訓練模型
    results = model.train(
        data=data_yaml,
        epochs=epochs,
        imgsz=imgsz,
        batch=batch,
        project='runs/train',
        name='price_tag_detector',
        patience=10,  # 早停耐心值
        save=True,
        plots=True,
        verbose=True
    )

    print(f"\n{'='*60}")
    print("Training completed!")
    print(f"{'='*60}")

    return model, results

def validate_model(model, data_yaml: str):
    """
    驗證模型準確度
    """
    print(f"\n{'='*60}")
    print("Validating Model")
    print(f"{'='*60}\n")

    # 在驗證集上評估
    metrics = model.val(data=data_yaml)

    print(f"\n{'='*60}")
    print("Validation Results:")
    print(f"{'='*60}")
    print(f"mAP50 (IoU=0.5):     {metrics.box.map50:.4f}")
    print(f"mAP50-95 (IoU=0.5:0.95): {metrics.box.map:.4f}")
    print(f"Precision:            {metrics.box.mp:.4f}")
    print(f"Recall:               {metrics.box.mr:.4f}")
    print(f"{'='*60}\n")

    return metrics

def main():
    # 1. 合併資料集
    data_yaml = merge_datasets()

    if data_yaml is None:
        print("Error: Failed to merge datasets")
        return

    # 2. 訓練模型
    model, results = train_model(
        data_yaml=data_yaml,
        epochs=50,      # 可調整
        imgsz=640,      # 圖片大小
        batch=16        # batch size（根據 GPU 記憶體調整）
    )

    # 3. 驗證模型
    metrics = validate_model(model, data_yaml)

    # 4. 顯示最佳模型路徑
    best_model_path = "runs/train/price_tag_detector/weights/best.pt"
    print(f"Best model saved to: {best_model_path}")
    print(f"\nTo use the model for inference:")
    print(f"  from ultralytics import YOLO")
    print(f"  model = YOLO('{best_model_path}')")
    print(f"  results = model.predict('path/to/image.jpg')")

if __name__ == "__main__":
    main()
