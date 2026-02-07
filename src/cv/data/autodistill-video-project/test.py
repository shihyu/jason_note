import os
import sys
import glob
import cv2
from ultralytics import YOLO
from pathlib import Path

def test_on_images(model_path: str, images_dir: str, output_dir: str = "data/test_results"):
    """
    在圖片上測試模型
    """
    print(f"\n{'='*60}")
    print(f"Testing model on images")
    print(f"{'='*60}")
    print(f"Model: {model_path}")
    print(f"Images: {images_dir}")
    print(f"{'='*60}\n")

    # 載入模型
    model = YOLO(model_path)

    # 獲取所有圖片
    image_files = []
    for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp']:
        image_files.extend(glob.glob(os.path.join(images_dir, ext)))

    if not image_files:
        print(f"Error: No images found in {images_dir}")
        return

    print(f"Found {len(image_files)} images")

    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)

    # 對每張圖片進行推理
    for img_path in image_files:
        print(f"Processing: {os.path.basename(img_path)}")

        # 執行推理
        results = model.predict(
            source=img_path,
            conf=0.25,  # 信心度閾值
            save=True,  # 保存結果
            project=output_dir,
            name='',
            exist_ok=True
        )

        # 顯示檢測結果
        for result in results:
            boxes = result.boxes
            print(f"  Detected {len(boxes)} objects:")
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = model.names[class_id]
                print(f"    - {class_name}: {confidence:.2%}")

    print(f"\n✓ Results saved to: {output_dir}")

def test_on_video(model_path: str, video_path: str, output_dir: str = "data/test_results"):
    """
    在影片上測試模型
    """
    print(f"\n{'='*60}")
    print(f"Testing model on video")
    print(f"{'='*60}")
    print(f"Model: {model_path}")
    print(f"Video: {video_path}")
    print(f"{'='*60}\n")

    # 載入模型
    model = YOLO(model_path)

    # 創建輸出目錄
    os.makedirs(output_dir, exist_ok=True)

    # 設定輸出影片路徑
    video_name = os.path.basename(video_path)
    output_video = os.path.join(output_dir, f"detected_{video_name}")

    # 開啟影片
    cap = cv2.VideoCapture(video_path)

    # 獲取影片資訊
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    print(f"Video info: {width}x{height} @ {fps}fps, {total_frames} frames")

    # 創建輸出影片
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

    frame_idx = 0
    total_detections = 0

    print("Processing video...")
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 執行推理
        results = model.predict(
            source=frame,
            conf=0.25,
            verbose=False  # 不顯示每幀的詳細信息
        )

        # 統計檢測數量
        total_detections += len(results[0].boxes)

        # 繪製結果
        annotated_frame = results[0].plot()

        # 寫入輸出影片
        out.write(annotated_frame)

        frame_idx += 1
        if frame_idx % 30 == 0:  # 每 30 幀顯示一次進度
            progress = (frame_idx / total_frames) * 100
            print(f"  Progress: {progress:.1f}% ({frame_idx}/{total_frames} frames)")

    # 釋放資源
    cap.release()
    out.release()

    avg_detections = total_detections / total_frames if total_frames > 0 else 0
    print(f"\n✓ Processed {total_frames} frames")
    print(f"✓ Total detections: {total_detections}")
    print(f"✓ Average detections per frame: {avg_detections:.2f}")
    print(f"✓ Output saved to: {output_video}")

def test_on_dataset(model_path: str, data_yaml: str):
    """
    在資料集上測試模型（使用驗證集）
    """
    print(f"\n{'='*60}")
    print(f"Testing model on dataset")
    print(f"{'='*60}")
    print(f"Model: {model_path}")
    print(f"Data: {data_yaml}")
    print(f"{'='*60}\n")

    # 載入模型
    model = YOLO(model_path)

    # 在驗證集上評估
    metrics = model.val(data=data_yaml)

    print(f"\n{'='*60}")
    print("Dataset Validation Results:")
    print(f"{'='*60}")
    print(f"mAP50 (IoU=0.5):         {metrics.box.map50:.4f} ({metrics.box.map50*100:.2f}%)")
    print(f"mAP50-95 (IoU=0.5:0.95): {metrics.box.map:.4f} ({metrics.box.map*100:.2f}%)")
    print(f"Precision:                {metrics.box.mp:.4f} ({metrics.box.mp*100:.2f}%)")
    print(f"Recall:                   {metrics.box.mr:.4f} ({metrics.box.mr*100:.2f}%)")
    print(f"{'='*60}\n")

def main():
    # 預設模型路徑
    default_model = "runs/detect/runs/train/price_tag_detector/weights/best.pt"

    # 檢查模型是否存在
    if not os.path.exists(default_model):
        print(f"Error: Model not found at {default_model}")
        print("Please run 'make train' first to train the model.")
        return

    print(f"\n{'='*60}")
    print("YOLOv8 Model Testing Tool")
    print(f"{'='*60}\n")
    print("Choose test mode:")
    print("  1. Test on sample images (from data/images/)")
    print("  2. Test on video (from data/videos/)")
    print("  3. Test on validation dataset")
    print("  4. Test on custom image/video path")
    print()

    choice = input("Enter choice (1-4) [default: 1]: ").strip() or "1"

    if choice == "1":
        # 測試影格圖片
        images_dir = "data/images"

        # 列出可用的影片目錄
        if os.path.exists(images_dir):
            video_dirs = [d for d in os.listdir(images_dir)
                         if os.path.isdir(os.path.join(images_dir, d))]

            if video_dirs:
                print(f"\nAvailable image sets:")
                for i, vdir in enumerate(video_dirs, 1):
                    print(f"  {i}. {vdir}")

                vid_choice = input(f"\nSelect image set (1-{len(video_dirs)}) [default: 1]: ").strip() or "1"
                vid_idx = int(vid_choice) - 1

                if 0 <= vid_idx < len(video_dirs):
                    test_dir = os.path.join(images_dir, video_dirs[vid_idx])
                    test_on_images(default_model, test_dir)
                else:
                    print("Invalid choice")
            else:
                print(f"Error: No image directories found in {images_dir}")
        else:
            print(f"Error: {images_dir} not found. Run 'make run' first.")

    elif choice == "2":
        # 測試影片
        videos_dir = "data/videos"

        if os.path.exists(videos_dir):
            video_files = glob.glob(os.path.join(videos_dir, "*.mp4"))

            if video_files:
                print(f"\nAvailable videos:")
                for i, vfile in enumerate(video_files, 1):
                    print(f"  {i}. {os.path.basename(vfile)}")

                vid_choice = input(f"\nSelect video (1-{len(video_files)}) [default: 1]: ").strip() or "1"
                vid_idx = int(vid_choice) - 1

                if 0 <= vid_idx < len(video_files):
                    test_on_video(default_model, video_files[vid_idx])
                else:
                    print("Invalid choice")
            else:
                print(f"Error: No videos found in {videos_dir}")
        else:
            print(f"Error: {videos_dir} not found")

    elif choice == "3":
        # 測試資料集
        data_yaml = "data/merged_dataset/data.yaml"

        if os.path.exists(data_yaml):
            test_on_dataset(default_model, data_yaml)
        else:
            print(f"Error: {data_yaml} not found. Run 'make train' first.")

    elif choice == "4":
        # 自訂路徑
        path = input("\nEnter image/video path: ").strip()

        if not os.path.exists(path):
            print(f"Error: {path} not found")
            return

        if os.path.isdir(path):
            test_on_images(default_model, path)
        elif path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            test_on_video(default_model, path)
        elif path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            # 單張圖片
            test_dir = os.path.dirname(path)
            test_on_images(default_model, test_dir if test_dir else ".")
        else:
            print("Error: Unsupported file format")

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()
