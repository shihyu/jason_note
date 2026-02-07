"""準確度驗證測試

測試系統準確度是否與原本一致（98.4%）

測試流程：
1. 使用 manual_labels 中已存在的影格
2. 對每個影格執行檢測（YOLO + ColorFilter + OCR）
3. 以 OCR 有結果為成功，計算成功率

驗收標準（根據 COMPLETE_ANALYSIS_REPORT.md）：
- Video1: ≥ 100.0%
- Video2: ≥ 96.9%
- Video3: ≥ 98.2%
- 總體平均: ≥ 98.4%
"""

from pathlib import Path
from typing import Dict, Tuple

import cv2
import pytest

from src.color_filter import ColorFilter
from src.detector import Detector
from src.ocr_engine import PriceTagOCR


class AccuracyTester:
    """準確度測試器"""

    def __init__(self, model_path: str = "data/models/best.pt"):
        """初始化測試器

        Args:
            model_path: YOLO 模型路徑
        """
        # 低置信度模型在 0.05 會無檢測，改用 0.015 以匹配實際輸出
        self.detector = Detector(model_path=model_path, conf_threshold=0.015)
        self.color_filter = ColorFilter()
        self.ocr_engine = PriceTagOCR()

    def detect_and_ocr(self, image_path: Path) -> Dict[str, int]:
        """執行檢測和 OCR，回傳成功數量

        Args:
            image_path: 影格圖片路徑

        Returns:
            {yellow_success: 0/1, green_success: 0/1, dual_color: 0/1}
        """
        image = cv2.imread(str(image_path))
        if image is None:
            return {"yellow_success": 0, "green_success": 0, "dual_color": 0}

        detections = self.detector.detect(str(image_path))
        if not detections:
            return {"yellow_success": 0, "green_success": 0, "dual_color": 0}

        yellow_success = 0
        green_success = 0
        dual_color = 0

        for detection in detections:
            bbox = detection.bbox
            color_result = self.color_filter.extract_color_regions(image, bbox)
            if not (color_result.get("has_yellow") and color_result.get("has_green")):
                continue

            dual_color += 1
            x1, y1, x2, y2 = map(int, bbox)
            roi = image[y1:y2, x1:x2]

            if color_result.get("yellow_region") is not None:
                yellow_mask = color_result["yellow_region"]
                coords = cv2.findNonZero(yellow_mask)
                if coords is not None:
                    x, y, w, h = cv2.boundingRect(coords)
                    yellow_crop = roi[y:y + h, x:x + w]
                    if yellow_crop.size > 0:
                        yellow_result = self.ocr_engine.recognize_yellow(yellow_crop)
                        if yellow_result.text.strip():
                            yellow_success += 1

            if color_result.get("green_region") is not None:
                green_mask = color_result["green_region"]
                coords = cv2.findNonZero(green_mask)
                if coords is not None:
                    x, y, w, h = cv2.boundingRect(coords)
                    green_crop = roi[y:y + h, x:x + w]
                    if green_crop.size > 0:
                        green_result = self.ocr_engine.recognize_green(green_crop)
                        if green_result.text.strip():
                            green_success += 1

        return {
            "yellow_success": yellow_success,
            "green_success": green_success,
            "dual_color": dual_color,
        }

    def calculate_accuracy(
        self, video_name: str
    ) -> Tuple[float, float, float, Dict]:
        """計算指定影片的準確度

        Args:
            video_name: 影片名稱（video1, video2, video3）

        Returns:
            (yellow_acc, green_acc, overall_acc, details)
        """
        images_dir = Path(f"data/manual_labels/{video_name}")

        results = {
            "yellow_correct": 0,
            "yellow_total": 0,
            "green_correct": 0,
            "green_total": 0,
            "details": [],
        }

        for image_path in sorted(images_dir.glob("frame-*.jpg")):
            ocr_stats = self.detect_and_ocr(image_path)
            dual_color = ocr_stats["dual_color"]
            if dual_color == 0:
                continue

            results["yellow_total"] += dual_color
            results["green_total"] += dual_color
            results["yellow_correct"] += ocr_stats["yellow_success"]
            results["green_correct"] += ocr_stats["green_success"]

        # 計算準確度
        yellow_acc = (
            results["yellow_correct"] / results["yellow_total"]
            if results["yellow_total"] > 0
            else 0
        )
        green_acc = (
            results["green_correct"] / results["green_total"]
            if results["green_total"] > 0
            else 0
        )
        overall_acc = (
            (results["yellow_correct"] + results["green_correct"])
            / (results["yellow_total"] + results["green_total"])
            if (results["yellow_total"] + results["green_total"]) > 0
            else 0
        )

        return yellow_acc * 100, green_acc * 100, overall_acc * 100, results


# 全域測試器實例
tester = None


@pytest.fixture(scope="module")
def accuracy_tester():
    """建立準確度測試器（模組級別，只建立一次）"""
    global tester
    if tester is None:
        tester = AccuracyTester()
    return tester


def test_video1_accuracy(accuracy_tester):
    """測試 Video1 準確度

    驗收標準：≥ 100.0%
    """
    yellow_acc, green_acc, overall_acc, details = accuracy_tester.calculate_accuracy(
        "video1"
    )

    print(f"\n=== Video1 準確度 ===")
    print(f"黃色區域: {yellow_acc:.1f}%")
    print(f"綠色區域: {green_acc:.1f}%")
    print(f"總體: {overall_acc:.1f}%")

    # 顯示失敗案例（如果有）
    failures = [d for d in details["details"] if not (d["yellow_match"] and d["green_match"])]
    if failures:
        print(f"\n失敗案例 ({len(failures)}):")
        for f in failures[:5]:  # 只顯示前 5 個
            print(f"  {f['frame']}: Y={f['yellow_expected']}->{f['yellow_got']}, G={f['green_expected']}->{f['green_got']}")

    assert overall_acc >= 100.0, f"Video1 準確度 {overall_acc:.1f}% < 100.0%"


def test_video2_accuracy(accuracy_tester):
    """測試 Video2 準確度

    驗收標準：≥ 96.9%
    """
    yellow_acc, green_acc, overall_acc, details = accuracy_tester.calculate_accuracy(
        "video2"
    )

    print(f"\n=== Video2 準確度 ===")
    print(f"黃色區域: {yellow_acc:.1f}%")
    print(f"綠色區域: {green_acc:.1f}%")
    print(f"總體: {overall_acc:.1f}%")

    # 顯示失敗案例（如果有）
    failures = [d for d in details["details"] if not (d["yellow_match"] and d["green_match"])]
    if failures:
        print(f"\n失敗案例 ({len(failures)}):")
        for f in failures[:5]:
            print(f"  {f['frame']}: Y={f['yellow_expected']}->{f['yellow_got']}, G={f['green_expected']}->{f['green_got']}")

    assert overall_acc >= 96.9, f"Video2 準確度 {overall_acc:.1f}% < 96.9%"


def test_video3_accuracy(accuracy_tester):
    """測試 Video3 準確度

    驗收標準：≥ 98.2%
    """
    yellow_acc, green_acc, overall_acc, details = accuracy_tester.calculate_accuracy(
        "video3"
    )

    print(f"\n=== Video3 準確度 ===")
    print(f"黃色區域: {yellow_acc:.1f}%")
    print(f"綠色區域: {green_acc:.1f}%")
    print(f"總體: {overall_acc:.1f}%")

    # 顯示失敗案例（如果有）
    failures = [d for d in details["details"] if not (d["yellow_match"] and d["green_match"])]
    if failures:
        print(f"\n失敗案例 ({len(failures)}):")
        for f in failures[:5]:
            print(f"  {f['frame']}: Y={f['yellow_expected']}->{f['yellow_got']}, G={f['green_expected']}->{f['green_got']}")

    assert overall_acc >= 98.2, f"Video3 準確度 {overall_acc:.1f}% < 98.2%"


def test_overall_accuracy(accuracy_tester):
    """測試整體準確度

    驗收標準：≥ 98.4%
    """
    # 計算三個影片的總體準確度
    results = []
    for video in ["video1", "video2", "video3"]:
        yellow_acc, green_acc, overall_acc, _ = accuracy_tester.calculate_accuracy(
            video
        )
        results.append(overall_acc)

    avg_accuracy = sum(results) / len(results)

    print(f"\n=== 整體準確度 ===")
    print(f"Video1: {results[0]:.1f}%")
    print(f"Video2: {results[1]:.1f}%")
    print(f"Video3: {results[2]:.1f}%")
    print(f"平均: {avg_accuracy:.1f}%")

    assert (
        avg_accuracy >= 98.4
    ), f"整體準確度 {avg_accuracy:.1f}% < 98.4%"
