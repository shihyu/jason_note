"""快速測試腳本 - 在第一個影片的影格上測試模型"""
import os
import glob
from ultralytics import YOLO

def main():
    # 模型路徑
    model_path = "runs/detect/runs/train/price_tag_detector/weights/best.pt"

    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Please run 'make train' first.")
        return

    # 載入模型
    print("Loading model...")
    model = YOLO(model_path)

    # 獲取第一個影片的影格目錄
    images_root = "data/images"
    if not os.path.exists(images_root):
        print(f"Error: {images_root} not found. Run 'make run' first.")
        return

    video_dirs = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    if not video_dirs:
        print(f"Error: No image directories found in {images_root}")
        return

    # 使用第一個影片目錄
    test_dir = os.path.join(images_root, video_dirs[0])
    image_files = glob.glob(os.path.join(test_dir, "*.jpg"))[:5]  # 只測試前 5 張

    if not image_files:
        print(f"Error: No images found in {test_dir}")
        return

    print(f"\n{'='*60}")
    print(f"Quick Test - Testing on {len(image_files)} images from {video_dirs[0]}")
    print(f"{'='*60}\n")

    output_dir = "data/test_results"
    os.makedirs(output_dir, exist_ok=True)

    total_detections = 0

    # 測試每張圖片
    for img_path in image_files:
        img_name = os.path.basename(img_path)
        print(f"Testing: {img_name}")

        # 執行推理
        results = model.predict(
            source=img_path,
            conf=0.25,
            save=True,
            project=output_dir,
            name='quick_test',
            exist_ok=True
        )

        # 顯示結果
        boxes = results[0].boxes
        print(f"  Detected {len(boxes)} objects:")

        for box in boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            print(f"    - {class_name}: {confidence:.2%}")

        total_detections += len(boxes)
        print()

    print(f"{'='*60}")
    print(f"Summary:")
    print(f"  Total images tested: {len(image_files)}")
    print(f"  Total detections: {total_detections}")
    print(f"  Average per image: {total_detections/len(image_files):.2f}")
    print(f"  Results saved to: {output_dir}/quick_test/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
