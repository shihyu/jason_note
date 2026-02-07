"""
OCR 診斷工具：分析預處理圖片質量並保存中間結果
"""

import cv2
import numpy as np
from ultralytics import YOLO
import color_ocr
import os

def save_preprocessing_steps(roi_image, color_type, output_dir, prefix):
    """保存預處理的每個步驟"""
    os.makedirs(output_dir, exist_ok=True)

    # 原始圖片
    cv2.imwrite(f"{output_dir}/{prefix}_1_original.jpg", roi_image)

    # 灰階
    if len(roi_image.shape) == 3:
        gray = cv2.cvtColor(roi_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = roi_image
    cv2.imwrite(f"{output_dir}/{prefix}_2_gray.jpg", gray)

    # 放大
    scale_factor = 3
    gray_scaled = cv2.resize(gray, None, fx=scale_factor, fy=scale_factor,
                            interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(f"{output_dir}/{prefix}_3_scaled.jpg", gray_scaled)

    # 去噪 + 二值化
    if color_type == 'green':
        denoised = cv2.bilateralFilter(gray_scaled, 9, 75, 75)
        cv2.imwrite(f"{output_dir}/{prefix}_4_denoised.jpg", denoised)

        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        cv2.imwrite(f"{output_dir}/{prefix}_5_binary_otsu.jpg", binary)
    else:  # yellow
        binary = cv2.adaptiveThreshold(
            gray_scaled, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        cv2.imwrite(f"{output_dir}/{prefix}_5_binary_adaptive.jpg", binary)

    # 反轉檢查
    black_ratio = np.sum(binary == 0) / binary.size
    if black_ratio > 0.5:
        binary = cv2.bitwise_not(binary)
    cv2.imwrite(f"{output_dir}/{prefix}_6_inverted.jpg", binary)

    # 形態學運算
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    cv2.imwrite(f"{output_dir}/{prefix}_7_morphology.jpg", binary)

    # 邊緣擴展
    border_size = 10
    binary = cv2.copyMakeBorder(
        binary, border_size, border_size, border_size, border_size,
        cv2.BORDER_CONSTANT, value=255
    )
    cv2.imwrite(f"{output_dir}/{prefix}_8_final.jpg", binary)

    return binary


def main():
    output_dir = "tests/ocr_diagnosis"
    os.makedirs(output_dir, exist_ok=True)

    # 載入模型
    model = YOLO('runs/detect/runs/train/price_tag_detector/weights/best.pt')

    # 測試圖片
    test_images = [
        'data/images/video1/frame-00001.jpg',
        'data/images/video1/frame-00002.jpg',
        'data/images/video1/frame-00003.jpg',
    ]

    print("=" * 60)
    print("OCR 診斷工具 - 分析預處理質量")
    print("=" * 60)

    for img_idx, img_path in enumerate(test_images):
        print(f"\n處理圖片 {img_idx + 1}: {img_path}")
        image = cv2.imread(img_path)
        results = model.predict(source=img_path, conf=0.25, verbose=False)

        # 只處理前 2 個雙色檢測框
        dual_color_count = 0
        for box_idx, box in enumerate(results[0].boxes):
            if dual_color_count >= 2:
                break

            bbox = box.xyxy[0].cpu().numpy()
            class_id = int(box.cls[0])
            x1, y1, x2, y2 = map(int, bbox)

            # 提取 ROI
            bbox_roi = image[y1:y2, x1:x2]

            # 檢測顏色
            green_mask, has_green, green_contour = color_ocr.detect_color_regions(bbox_roi, 'green')
            yellow_mask, has_yellow, yellow_contour = color_ocr.detect_color_regions(bbox_roi, 'yellow')

            if not (has_green and has_yellow):
                continue

            dual_color_count += 1
            print(f"\n  雙色框 {dual_color_count}:")

            # 綠色區域
            if green_contour is not None:
                green_region, _ = color_ocr.extract_color_region(bbox_roi, green_contour)
                prefix = f"img{img_idx+1}_box{dual_color_count}_green"

                # 保存預處理步驟
                final_binary = save_preprocessing_steps(green_region, 'green', output_dir, prefix)

                # OCR 識別
                green_price, green_conf = color_ocr.recognize_price(green_region, 'green')
                print(f"    綠色: '{green_price}' (置信度: {green_conf:.1f}%)")

            # 黃色區域
            if yellow_contour is not None:
                yellow_region, _ = color_ocr.extract_color_region(bbox_roi, yellow_contour)
                prefix = f"img{img_idx+1}_box{dual_color_count}_yellow"

                # 保存預處理步驟
                final_binary = save_preprocessing_steps(yellow_region, 'yellow', output_dir, prefix)

                # OCR 識別
                yellow_price, yellow_conf = color_ocr.recognize_price(yellow_region, 'yellow')
                print(f"    黃色: '{yellow_price}' (置信度: {yellow_conf:.1f}%)")

    print(f"\n{'='*60}")
    print(f"診斷完成！")
    print(f"預處理圖片已保存到: {output_dir}/")
    print(f"請檢查 *_final.jpg 圖片的質量")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
