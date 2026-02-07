"""使用訓練好的模型檢測所有影格並產生標記圖片（整合 OCR 功能）"""
import os
import glob
import cv2
from ultralytics import YOLO
from tqdm import tqdm
import color_ocr

def main():
    # 模型路徑
    model_path = "runs/detect/runs/train/price_tag_detector2/weights/best.pt"

    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        print("Please run 'make train' first.")
        return

    # 影格目錄
    images_root = "data/images"

    if not os.path.exists(images_root):
        print(f"Error: {images_root} not found. Run 'make run' first.")
        return

    # 載入模型
    print("Loading model...")
    model = YOLO(model_path)

    # 獲取所有影片目錄
    video_dirs = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    if not video_dirs:
        print(f"Error: No video directories found in {images_root}")
        return

    print(f"\n{'='*60}")
    print(f"檢測所有影格 - 使用訓練好的 YOLOv8 模型")
    print(f"{'='*60}")
    print(f"找到 {len(video_dirs)} 個影片目錄")
    print(f"模型: {model_path}")
    print(f"{'='*60}\n")

    output_root = "data/detections"
    os.makedirs(output_root, exist_ok=True)

    total_images = 0
    total_detections = 0

    # 初始化 OCR 統計
    ocr_stats = color_ocr.OCRStatistics()

    # 處理每個影片的影格
    for video_name in video_dirs:
        video_dir = os.path.join(images_root, video_name)
        output_dir = os.path.join(output_root, video_name)

        # 獲取所有圖片
        image_files = sorted(glob.glob(os.path.join(video_dir, "*.jpg")))

        if not image_files:
            print(f"Warning: No images found in {video_dir}")
            continue

        print(f"\n處理 {video_name}: {len(image_files)} 張圖片")

        os.makedirs(output_dir, exist_ok=True)

        # 使用 tqdm 顯示進度條
        for img_path in tqdm(image_files, desc=f"  檢測 + OCR"):
            # 讀取圖片
            image = cv2.imread(img_path)

            # 執行 YOLO 推理
            results = model.predict(
                source=img_path,
                conf=0.25,
                verbose=False
            )

            # 處理每個檢測框
            dual_color_count = 0
            for box in results[0].boxes:
                bbox = box.xyxy[0].cpu().numpy()
                class_id = int(box.cls[0])

                # 【整合】執行顏色檢測 + OCR
                ocr_result = color_ocr.process_detection_with_ocr(image, bbox, class_id)

                # 【過濾】只處理雙色檢測框
                if not ocr_result['has_both_colors']:
                    continue

                dual_color_count += 1

                # 【標註】在圖片上標註 OCR 結果
                color_ocr.annotate_ocr_results(image, bbox, ocr_result)

                # 【統計】更新 OCR 統計資訊
                ocr_stats.update(ocr_result)

            # 保存標註後的圖片
            output_path = os.path.join(output_dir, os.path.basename(img_path))
            cv2.imwrite(output_path, image)

            # 統計檢測數量
            total_detections += dual_color_count
            total_images += 1

        print(f"  ✓ 完成 {video_name}")
        print(f"  ✓ 輸出目錄: {output_dir}")

    # 顯示摘要
    print(f"\n{'='*60}")
    print("檢測完成！")
    print(f"{'='*60}")
    print(f"總圖片數: {total_images}")
    print(f"雙色檢測框總數: {total_detections}")
    print(f"平均每張圖: {total_detections/total_images:.2f}" if total_images > 0 else "N/A")
    print(f"\n所有檢測結果已保存到: {output_root}/")
    print(f"{'='*60}")

    # 顯示 OCR 統計報告
    print(ocr_stats.report())

if __name__ == "__main__":
    main()
