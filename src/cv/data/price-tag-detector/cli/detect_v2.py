"""改進的檢測命令列工具 - 使用優化的 OCR"""
import argparse
import sys
from pathlib import Path

import cv2
from tqdm import tqdm

# 添加專案根目錄到 Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.detector import Detector
from src.color_filter import ColorFilter
from src.ocr_engine_v2 import PriceTagOCR


class ImprovedDetectionPipeline:
    """改進的檢測流水線 - 使用優化的 OCR"""

    def __init__(self, model_path: str, conf_threshold: float = 0.05):
        """初始化檢測流水線

        Args:
            model_path: YOLO 模型路徑
            conf_threshold: 置信度閾值
        """
        self.detector = Detector(model_path, conf_threshold)
        self.color_filter = ColorFilter()
        self.ocr_engine = PriceTagOCR()

        # 統計資訊
        self.stats = {
            "total_images": 0,
            "total_detections": 0,
            "dual_color_detections": 0,
            "yellow_ocr_success": 0,
            "green_ocr_success": 0,
            "yellow_total_confidence": 0.0,
            "green_total_confidence": 0.0,
        }

    def process_image(self, image_path: str, output_path: str) -> int:
        """處理單張圖片

        Args:
            image_path: 輸入圖片路徑
            output_path: 輸出圖片路徑

        Returns:
            雙色檢測框數量
        """
        # 讀取圖片
        image = cv2.imread(image_path)
        if image is None:
            print(f"❌ 無法讀取圖片: {image_path}")
            return 0

        # YOLO 檢測
        detections = self.detector.detect(image_path)
        self.stats["total_detections"] += len(detections)

        # 處理每個檢測框
        dual_color_count = 0

        for detection in detections:
            # 顏色過濾
            color_result = self.color_filter.extract_color_regions(image, detection.bbox)

            # 只處理雙色檢測框
            if not (color_result["has_yellow"] and color_result["has_green"]):
                continue

            dual_color_count += 1
            x1, y1, x2, y2 = map(int, detection.bbox)
            roi = image[y1:y2, x1:x2]

            # 分別識別黃色和綠色區域
            yellow_text = ""
            green_text = ""
            yellow_conf = 0.0
            green_conf = 0.0

            # 黃色區域 OCR
            if color_result["yellow_region"] is not None:
                yellow_mask = color_result["yellow_region"]
                # 創建黃色區域的 ROI
                yellow_roi = cv2.bitwise_and(roi, roi, mask=yellow_mask)

                # 找到黃色區域的邊界
                coords = cv2.findNonZero(yellow_mask)
                if coords is not None:
                    yx, yy, yw, yh = cv2.boundingRect(coords)
                    yellow_crop = yellow_roi[yy:yy+yh, yx:yx+yw]

                    if yellow_crop.size > 0:
                        yellow_result = self.ocr_engine.recognize_yellow(yellow_crop)
                        yellow_text = yellow_result.text
                        yellow_conf = yellow_result.confidence

                        if yellow_text:
                            self.stats["yellow_ocr_success"] += 1
                            self.stats["yellow_total_confidence"] += yellow_conf

            # 綠色區域 OCR
            if color_result["green_region"] is not None:
                green_mask = color_result["green_region"]
                green_roi = cv2.bitwise_and(roi, roi, mask=green_mask)

                # 找到綠色區域的邊界
                coords = cv2.findNonZero(green_mask)
                if coords is not None:
                    gx, gy, gw, gh = cv2.boundingRect(coords)
                    green_crop = green_roi[gy:gy+gh, gx:gx+gw]

                    if green_crop.size > 0:
                        green_result = self.ocr_engine.recognize_green(green_crop)
                        green_text = green_result.text
                        green_conf = green_result.confidence

                        if green_text:
                            self.stats["green_ocr_success"] += 1
                            self.stats["green_total_confidence"] += green_conf

            # 標註圖片
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 顯示 OCR 結果
            if yellow_text or green_text:
                # 使用中文字體（如果有識別結果）
                label_parts = []
                if yellow_text:
                    label_parts.append(f"Y:{yellow_text}({yellow_conf:.0f}%)")
                if green_text:
                    label_parts.append(f"G:{green_text}({green_conf:.0f}%)")

                label = " ".join(label_parts)

                # 添加背景讓文字更清楚
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.5
                thickness = 1
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, font, font_scale, thickness
                )

                # 繪製背景
                cv2.rectangle(
                    image,
                    (x1, y1 - text_height - baseline - 5),
                    (x1 + text_width, y1),
                    (0, 255, 0),
                    -1
                )

                # 繪製文字
                cv2.putText(
                    image,
                    label,
                    (x1, y1 - baseline - 2),
                    font,
                    font_scale,
                    (0, 0, 0),
                    thickness,
                )

        # 保存標註後的圖片
        cv2.imwrite(output_path, image)

        self.stats["total_images"] += 1
        self.stats["dual_color_detections"] += dual_color_count

        return dual_color_count

    def process_directory(self, input_dir: str, output_dir: str) -> None:
        """處理目錄中的所有圖片

        Args:
            input_dir: 輸入目錄
            output_dir: 輸出目錄
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 獲取所有圖片
        image_files = list(input_path.glob("*.jpg")) + list(input_path.glob("*.png"))

        if not image_files:
            print(f"❌ 在 {input_dir} 中沒有找到圖片")
            return

        print(f"\n{'='*60}")
        print(f"處理 {len(image_files)} 張圖片")
        print(f"輸入: {input_dir}")
        print(f"輸出: {output_dir}")
        print(f"{'='*60}\n")

        # 處理每張圖片
        for img_file in tqdm(image_files, desc="檢測進度"):
            output_file = output_path / img_file.name
            self.process_image(str(img_file), str(output_file))

        # 顯示統計資訊
        self.print_stats()

    def print_stats(self) -> None:
        """顯示統計資訊"""
        print(f"\n{'='*60}")
        print("檢測完成！")
        print(f"{'='*60}")
        print(f"總圖片數:         {self.stats['total_images']}")
        print(f"總檢測框數:       {self.stats['total_detections']}")
        print(f"雙色檢測框數:     {self.stats['dual_color_detections']}")

        print(f"\nOCR 識別結果:")
        print(f"  黃色區域:")
        print(f"    成功數: {self.stats['yellow_ocr_success']}")
        if self.stats['yellow_ocr_success'] > 0:
            avg_conf = self.stats['yellow_total_confidence'] / self.stats['yellow_ocr_success']
            print(f"    平均信心度: {avg_conf:.1f}%")
            success_rate = self.stats['yellow_ocr_success'] / self.stats['dual_color_detections'] * 100
            print(f"    成功率: {success_rate:.1f}%")

        print(f"  綠色區域:")
        print(f"    成功數: {self.stats['green_ocr_success']}")
        if self.stats['green_ocr_success'] > 0:
            avg_conf = self.stats['green_total_confidence'] / self.stats['green_ocr_success']
            print(f"    平均信心度: {avg_conf:.1f}%")
            success_rate = self.stats['green_ocr_success'] / self.stats['dual_color_detections'] * 100
            print(f"    成功率: {success_rate:.1f}%")

        total_ocr_success = self.stats['yellow_ocr_success'] + self.stats['green_ocr_success']
        if self.stats['dual_color_detections'] > 0:
            overall_rate = total_ocr_success / (self.stats['dual_color_detections'] * 2) * 100
            print(f"\n總體 OCR 成功率: {overall_rate:.1f}%")

        print(f"{'='*60}\n")


def main() -> None:
    """檢測命令主函數"""
    parser = argparse.ArgumentParser(description="價格標籤檢測（改進的 OCR）")

    parser.add_argument(
        "--model",
        type=str,
        default="data/models/best.pt",
        help="YOLO 模型路徑",
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/images",
        help="輸入目錄或圖片路徑",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/detections_v2",
        help="輸出目錄",
    )
    parser.add_argument(
        "--conf",
        type=float,
        default=0.05,
        help="置信度閾值（預設 0.05）",
    )

    args = parser.parse_args()

    # 檢查模型是否存在
    if not Path(args.model).exists():
        print(f"❌ 錯誤：模型文件不存在: {args.model}")
        print(f"\n請先訓練模型：")
        print(f"  make train")
        sys.exit(1)

    # 創建檢測流水線
    pipeline = ImprovedDetectionPipeline(args.model, args.conf)

    # 處理輸入
    input_path = Path(args.input)

    if input_path.is_file():
        # 單張圖片
        output_file = Path(args.output) / input_path.name
        output_file.parent.mkdir(parents=True, exist_ok=True)
        pipeline.process_image(str(input_path), str(output_file))
        pipeline.print_stats()
    elif input_path.is_dir():
        # 目錄
        pipeline.process_directory(str(input_path), args.output)
    else:
        print(f"❌ 錯誤：輸入路徑不存在: {args.input}")
        sys.exit(1)


if __name__ == "__main__":
    main()
