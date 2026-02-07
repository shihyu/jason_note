"""快速 OCR 測試：在少量圖片上測試並顯示結果"""

import cv2
import os
from ultralytics import YOLO
import color_ocr

def main():
    # 載入模型
    model = YOLO('runs/detect/runs/train/price_tag_detector/weights/best.pt')

    # 測試圖片（只測試前 10 張）
    images_root = "data/images/video1"
    import glob
    image_files = sorted(glob.glob(os.path.join(images_root, "*.jpg")))[:10]

    print("="*60)
    print("快速 OCR 測試（前 10 張圖片）")
    print("="*60)

    stats = color_ocr.OCRStatistics()
    dual_color_count = 0

    for img_path in image_files:
        image = cv2.imread(img_path)
        results = model.predict(source=img_path, conf=0.25, verbose=False)

        for box in results[0].boxes:
            bbox = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls[0])

            ocr_result = color_ocr.process_detection_with_ocr(image, bbox, class_id)

            if ocr_result['has_both_colors']:
                dual_color_count += 1
                stats.update(ocr_result)

                print(f"\n圖片: {os.path.basename(img_path)}")
                print(f"  綠色: '{ocr_result['green_price']}' ({ocr_result['green_confidence']:.0f}%)")
                print(f"  黃色: '{ocr_result['yellow_price']}' ({ocr_result['yellow_confidence']:.0f}%)")

    print("\n" + "="*60)
    print(stats.report())

    # 計算成功率
    green_success_rate = stats.successful_green_ocr / stats.total_detections * 100 if stats.total_detections > 0 else 0
    yellow_success_rate = stats.successful_yellow_ocr / stats.total_detections * 100 if stats.total_detections > 0 else 0

    print(f"\n✅ 成功率統計：")
    print(f"  綠色識別成功率: {green_success_rate:.1f}%")
    print(f"  黃色識別成功率: {yellow_success_rate:.1f}%")

    # 計算平均置信度
    all_confidences = stats.green_confidences + stats.yellow_confidences
    if all_confidences:
        avg_conf = sum(all_confidences) / len(all_confidences)
        print(f"  整體平均置信度: {avg_conf:.1f}%")

        if avg_conf >= 80 and green_success_rate >= 80 and yellow_success_rate >= 80:
            print(f"\n🎉 目標達成！")
        else:
            print(f"\n⚠️  還需要優化")

if __name__ == "__main__":
    main()
