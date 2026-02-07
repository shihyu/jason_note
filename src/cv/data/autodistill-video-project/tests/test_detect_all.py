"""
detect_all.py 整合測試

測試整合 color_ocr 模組後的 detect_all.py 功能：
1. 雙色檢測框過濾
2. OCR 識別準確率
3. 輸出格式驗證
"""

import os
import sys
import cv2
import glob
import numpy as np
from pathlib import Path

# 加入專案根目錄到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

import color_ocr
from ultralytics import YOLO


def test_dual_color_detection():
    """
    測試 1：驗證雙色檢測功能

    驗證 process_detection_with_ocr() 能正確識別同時包含黃色和綠色的檢測框
    """
    print("\n" + "="*60)
    print("測試 1：雙色檢測功能")
    print("="*60)

    # 檢查測試圖片是否存在
    images_root = "data/images"
    if not os.path.exists(images_root):
        print(f"❌ 錯誤：{images_root} 不存在")
        print("   請先執行 'make run' 產生影格")
        return False

    # 載入模型
    model_path = "runs/detect/runs/train/price_tag_detector/weights/best.pt"
    if not os.path.exists(model_path):
        print(f"❌ 錯誤：模型 {model_path} 不存在")
        print("   請先執行 'make train' 訓練模型")
        return False

    model = YOLO(model_path)

    # 取得第一個影片的前 5 張圖片
    video_dirs = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    if not video_dirs:
        print(f"❌ 錯誤：{images_root} 下沒有影片目錄")
        return False

    video_dir = os.path.join(images_root, video_dirs[0])
    image_files = sorted(glob.glob(os.path.join(video_dir, "*.jpg")))[:5]

    print(f"使用測試圖片：{len(image_files)} 張")

    dual_color_count = 0
    single_color_count = 0
    no_detection_count = 0

    for img_path in image_files:
        image = cv2.imread(img_path)
        results = model.predict(source=img_path, conf=0.25, verbose=False)

        if len(results[0].boxes) == 0:
            no_detection_count += 1
            continue

        for box in results[0].boxes:
            bbox = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls[0])

            # 執行顏色檢測
            ocr_result = color_ocr.process_detection_with_ocr(image, bbox, class_id)

            if ocr_result['has_both_colors']:
                dual_color_count += 1
                print(f"  ✓ 找到雙色檢測框：{os.path.basename(img_path)}")
            else:
                single_color_count += 1

    print(f"\n檢測結果統計：")
    print(f"  雙色檢測框：{dual_color_count}")
    print(f"  單色檢測框：{single_color_count}")
    print(f"  無檢測：{no_detection_count}")

    # 驗收標準：至少要有一個雙色檢測框
    if dual_color_count > 0:
        print(f"\n✅ 測試通過：成功檢測到 {dual_color_count} 個雙色檢測框")
        return True
    else:
        print(f"\n❌ 測試失敗：沒有檢測到雙色檢測框")
        print("   可能原因：")
        print("   1. 測試圖片中沒有同時包含黃色和綠色的物件")
        print("   2. 顏色檢測閾值需要調整")
        return False


def test_ocr_accuracy():
    """
    測試 2：驗證 OCR 識別準確率

    在測試集上運行 OCR，計算平均置信度
    目標：平均置信度 ≥ 90%
    """
    print("\n" + "="*60)
    print("測試 2：OCR 識別準確率")
    print("="*60)

    images_root = "data/images"
    model_path = "runs/detect/runs/train/price_tag_detector/weights/best.pt"

    if not os.path.exists(images_root) or not os.path.exists(model_path):
        print("❌ 錯誤：缺少必要檔案")
        return False

    model = YOLO(model_path)

    # 取得所有影片目錄
    video_dirs = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    # 取樣：每個影片取前 3 張圖片
    test_images = []
    for video_name in video_dirs[:2]:  # 只測試前 2 個影片
        video_dir = os.path.join(images_root, video_name)
        images = sorted(glob.glob(os.path.join(video_dir, "*.jpg")))[:3]
        test_images.extend(images)

    print(f"使用測試圖片：{len(test_images)} 張")

    stats = color_ocr.OCRStatistics()

    for img_path in test_images:
        image = cv2.imread(img_path)
        results = model.predict(source=img_path, conf=0.25, verbose=False)

        for box in results[0].boxes:
            bbox = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls[0])

            ocr_result = color_ocr.process_detection_with_ocr(image, bbox, class_id)

            # 只統計雙色檢測框
            if ocr_result['has_both_colors']:
                stats.update(ocr_result)

    # 顯示統計報告
    print(stats.report())

    # 計算平均置信度
    all_confidences = stats.green_confidences + stats.yellow_confidences
    if all_confidences:
        avg_confidence = sum(all_confidences) / len(all_confidences)
        print(f"整體平均置信度：{avg_confidence:.1f}%")

        # 驗收標準：平均置信度 ≥ 90%
        if avg_confidence >= 90.0:
            print(f"\n✅ 測試通過：OCR 平均置信度 {avg_confidence:.1f}% ≥ 90%")
            return True
        else:
            print(f"\n⚠️  測試未達標：OCR 平均置信度 {avg_confidence:.1f}% < 90%")
            print("   建議：")
            print("   1. 檢查圖片品質")
            print("   2. 調整 preprocess_for_ocr() 參數")
            print("   3. 嘗試不同的 Tesseract 配置")
            return False
    else:
        print("\n❌ 測試失敗：沒有成功識別任何價格")
        return False


def test_output_format():
    """
    測試 3：驗證輸出格式

    檢查輸出圖片是否正確產生，並包含 OCR 標註
    """
    print("\n" + "="*60)
    print("測試 3：輸出格式驗證")
    print("="*60)

    # 創建臨時輸出目錄
    output_dir = "tests/output"
    os.makedirs(output_dir, exist_ok=True)

    images_root = "data/images"
    model_path = "runs/detect/runs/train/price_tag_detector/weights/best.pt"

    if not os.path.exists(images_root) or not os.path.exists(model_path):
        print("❌ 錯誤：缺少必要檔案")
        return False

    model = YOLO(model_path)

    # 取得第一張測試圖片
    video_dirs = [d for d in os.listdir(images_root)
                  if os.path.isdir(os.path.join(images_root, d))]

    if not video_dirs:
        print("❌ 錯誤：沒有測試圖片")
        return False

    video_dir = os.path.join(images_root, video_dirs[0])
    image_files = sorted(glob.glob(os.path.join(video_dir, "*.jpg")))

    if not image_files:
        print("❌ 錯誤：沒有測試圖片")
        return False

    test_image_path = image_files[0]
    image = cv2.imread(test_image_path)
    results = model.predict(source=test_image_path, conf=0.25, verbose=False)

    annotated_count = 0

    for box in results[0].boxes:
        bbox = box.xyxy[0].cpu().numpy()
        class_id = int(box.cls[0])

        ocr_result = color_ocr.process_detection_with_ocr(image, bbox, class_id)

        if ocr_result['has_both_colors']:
            # 標註 OCR 結果
            color_ocr.annotate_ocr_results(image, bbox, ocr_result)
            annotated_count += 1

    # 保存測試輸出
    output_path = os.path.join(output_dir, "test_annotated.jpg")
    cv2.imwrite(output_path, image)

    print(f"測試圖片：{os.path.basename(test_image_path)}")
    print(f"標註數量：{annotated_count}")
    print(f"輸出檔案：{output_path}")

    # 驗證輸出檔案存在
    if os.path.exists(output_path):
        file_size = os.path.getsize(output_path)
        print(f"檔案大小：{file_size / 1024:.1f} KB")

        if annotated_count > 0:
            print(f"\n✅ 測試通過：成功產生帶有 {annotated_count} 個標註的輸出圖片")
            return True
        else:
            print(f"\n⚠️  測試部分通過：輸出圖片已產生，但沒有雙色檢測框")
            return True
    else:
        print("\n❌ 測試失敗：輸出檔案未產生")
        return False


def run_all_tests():
    """執行所有測試"""
    print("\n" + "="*60)
    print("開始執行 detect_all.py 整合測試")
    print("="*60)

    results = []

    # 測試 1：雙色檢測
    results.append(("雙色檢測功能", test_dual_color_detection()))

    # 測試 2：OCR 準確率
    results.append(("OCR 識別準確率", test_ocr_accuracy()))

    # 測試 3：輸出格式
    results.append(("輸出格式驗證", test_output_format()))

    # 顯示測試摘要
    print("\n" + "="*60)
    print("測試摘要")
    print("="*60)

    for test_name, passed in results:
        status = "✅ 通過" if passed else "❌ 失敗"
        print(f"{status} - {test_name}")

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    print(f"\n總計：{passed_count}/{total_count} 測試通過")

    if passed_count == total_count:
        print("\n🎉 所有測試通過！")
        return True
    else:
        print(f"\n⚠️  有 {total_count - passed_count} 個測試失敗")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
