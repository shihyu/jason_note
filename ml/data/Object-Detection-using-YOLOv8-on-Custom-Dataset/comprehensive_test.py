#!/usr/bin/env python3
"""
Comprehensive Test Script for YOLOv8 Guitar Detection

This script performs a complete validation to ensure the newly trained model
performs similarly to the original Notebook baseline.

Tests include:
1. Metrics comparison (Precision, Recall, mAP50, mAP50-95)
2. Per-image prediction comparison
3. Statistical analysis of detection quality
"""

import os
import sys
import json
from pathlib import Path
import cv2
import numpy as np
from ultralytics import YOLO


def load_baseline_metrics(baseline_file="tests/baseline_metrics.json"):
    """Load baseline metrics from JSON file"""
    if Path(baseline_file).exists():
        with open(baseline_file, 'r') as f:
            return json.load(f)
    return None


def test_model_metrics(model_path, data_config):
    """Test model and return validation metrics"""
    print(f"\nTesting model: {model_path}")

    if not Path(model_path).exists():
        print(f"ERROR: Model not found at {model_path}")
        return None

    model = YOLO(model_path)

    print("Running validation...")
    results = model.val(
        data=data_config,
        batch=16,
        imgsz=640,
        verbose=False,
    )

    metrics_box = results.box
    metrics = {
        "precision": float(metrics_box.mp),
        "recall": float(metrics_box.mr),
        "mAP50": float(metrics_box.map50),
        "mAP50-95": float(metrics_box.map),
    }

    return metrics


def test_predictions_consistency(model_path, test_images_dir, conf_threshold=0.6):
    """
    Test prediction consistency by running inference on test images
    and analyzing the detection quality
    """
    print(f"\nTesting prediction consistency on validation images...")

    model = YOLO(model_path)

    test_images = list(Path(test_images_dir).glob("*.jpg")) + \
                  list(Path(test_images_dir).glob("*.JPG"))

    if len(test_images) == 0:
        print(f"ERROR: No test images found in {test_images_dir}")
        return None

    print(f"Found {len(test_images)} test images")

    results = model.predict(
        source=test_images_dir,
        imgsz=640,
        conf=conf_threshold,
        verbose=False,
    )

    stats = {
        "total_images": len(results),
        "images_with_detections": 0,
        "total_detections": 0,
        "avg_confidence": 0.0,
        "min_confidence": 1.0,
        "max_confidence": 0.0,
        "detections_per_image": [],
    }

    all_confidences = []

    for result in results:
        num_boxes = len(result.boxes)
        stats["total_detections"] += num_boxes
        stats["detections_per_image"].append(num_boxes)

        if num_boxes > 0:
            stats["images_with_detections"] += 1

            for box in result.boxes:
                conf = float(box.conf)
                all_confidences.append(conf)
                stats["min_confidence"] = min(stats["min_confidence"], conf)
                stats["max_confidence"] = max(stats["max_confidence"], conf)

    if all_confidences:
        stats["avg_confidence"] = float(np.mean(all_confidences))
        stats["std_confidence"] = float(np.std(all_confidences))

    stats["avg_detections_per_image"] = stats["total_detections"] / stats["total_images"]

    return stats


def compare_metrics(current, baseline, tolerance=0.05):
    """Compare current metrics with baseline and determine pass/fail"""

    if baseline is None:
        return {
            "status": "no_baseline",
            "message": "No baseline metrics for comparison"
        }

    metrics_to_check = ["precision", "recall", "mAP50", "mAP50-95"]
    results = {}
    all_passed = True

    for metric in metrics_to_check:
        if metric not in current or metric not in baseline:
            continue

        current_val = current[metric]
        baseline_val = baseline[metric]
        diff = current_val - baseline_val
        diff_pct = (diff / baseline_val) * 100 if baseline_val > 0 else 0

        lower_bound = baseline_val * (1 - tolerance)
        passed = current_val >= lower_bound
        all_passed = all_passed and passed

        results[metric] = {
            "current": round(current_val, 4),
            "baseline": round(baseline_val, 4),
            "diff": round(diff, 4),
            "diff_pct": round(diff_pct, 2),
            "lower_bound": round(lower_bound, 4),
            "passed": passed
        }

    return {
        "status": "passed" if all_passed else "failed",
        "all_passed": all_passed,
        "tolerance": tolerance,
        "metrics": results
    }


def main():
    """Run comprehensive validation tests"""

    # Configuration
    MODEL_PATH = "runs/detect/guitar_train/weights/best.pt"
    DATA_CONFIG = "guitar_dataset.yaml"
    TEST_IMAGES = "Dataset/Guitar_dataset/val/images"
    BASELINE_FILE = "tests/baseline_metrics.json"
    OUTPUT_FILE = "tests/validation_report.json"
    TOLERANCE = 0.05  # 5% tolerance

    print("=" * 70)
    print("YOLOv8 Guitar Detection - Comprehensive Validation Test")
    print("=" * 70)

    # Check if model exists
    if not Path(MODEL_PATH).exists():
        print(f"\nERROR: Trained model not found at {MODEL_PATH}")
        print("Please complete training first: make train")
        sys.exit(1)

    print(f"\n✓ Model found: {MODEL_PATH}")

    # Load baseline
    baseline = load_baseline_metrics(BASELINE_FILE)
    if baseline:
        print(f"✓ Baseline loaded from: {BASELINE_FILE}")
        print(f"\n  Baseline Metrics:")
        print(f"    Precision: {baseline.get('precision', 'N/A')}")
        print(f"    Recall: {baseline.get('recall', 'N/A')}")
        print(f"    mAP50: {baseline.get('mAP50', 'N/A')}")
        print(f"    mAP50-95: {baseline.get('mAP50-95', 'N/A')}")
    else:
        print(f"⚠ No baseline metrics found")

    # Test 1: Validation Metrics
    print("\n" + "=" * 70)
    print("TEST 1: Validation Metrics")
    print("=" * 70)

    current_metrics = test_model_metrics(MODEL_PATH, DATA_CONFIG)

    if current_metrics:
        print(f"\n  Current Metrics:")
        print(f"    Precision: {current_metrics['precision']:.4f}")
        print(f"    Recall: {current_metrics['recall']:.4f}")
        print(f"    mAP50: {current_metrics['mAP50']:.4f}")
        print(f"    mAP50-95: {current_metrics['mAP50-95']:.4f}")

        # Compare with baseline
        if baseline:
            print(f"\n  Comparison with Baseline (tolerance: ±{TOLERANCE*100}%):")
            comparison = compare_metrics(current_metrics, baseline, TOLERANCE)

            print(f"\n  {'Metric':<12} {'Current':<10} {'Baseline':<10} {'Diff':<10} {'Diff%':<10} {'Status'}")
            print("  " + "-" * 68)

            for metric, data in comparison["metrics"].items():
                status = "✓ PASS" if data["passed"] else "✗ FAIL"
                print(f"  {metric:<12} {data['current']:<10.4f} {data['baseline']:<10.4f} "
                      f"{data['diff']:<+10.4f} {data['diff_pct']:<+10.2f} {status}")

            print("  " + "-" * 68)
            if comparison["all_passed"]:
                print(f"\n  ✓ TEST 1 PASSED: All metrics within acceptable range")
            else:
                print(f"\n  ✗ TEST 1 FAILED: Some metrics below threshold")
    else:
        print("  ✗ TEST 1 FAILED: Could not get metrics")
        sys.exit(1)

    # Test 2: Prediction Consistency
    print("\n" + "=" * 70)
    print("TEST 2: Prediction Consistency")
    print("=" * 70)

    pred_stats = test_predictions_consistency(MODEL_PATH, TEST_IMAGES)

    if pred_stats:
        print(f"\n  Prediction Statistics:")
        print(f"    Total images: {pred_stats['total_images']}")
        print(f"    Images with detections: {pred_stats['images_with_detections']}")
        print(f"    Total detections: {pred_stats['total_detections']}")
        print(f"    Avg detections per image: {pred_stats['avg_detections_per_image']:.2f}")
        print(f"    Avg confidence: {pred_stats['avg_confidence']:.3f}")
        print(f"    Confidence range: [{pred_stats['min_confidence']:.3f}, {pred_stats['max_confidence']:.3f}]")

        # Sanity checks
        checks_passed = True
        print(f"\n  Sanity Checks:")

        # Check 1: Should detect guitars in most images (at least 80%)
        detection_rate = pred_stats['images_with_detections'] / pred_stats['total_images']
        if detection_rate >= 0.8:
            print(f"    ✓ Detection rate: {detection_rate*100:.1f}% (>= 80%)")
        else:
            print(f"    ✗ Detection rate: {detection_rate*100:.1f}% (< 80%)")
            checks_passed = False

        # Check 2: Average confidence should be reasonable (>= 0.5)
        if pred_stats['avg_confidence'] >= 0.5:
            print(f"    ✓ Average confidence: {pred_stats['avg_confidence']:.3f} (>= 0.5)")
        else:
            print(f"    ✗ Average confidence: {pred_stats['avg_confidence']:.3f} (< 0.5)")
            checks_passed = False

        # Check 3: Should not have too many detections per image (< 5 on average)
        if pred_stats['avg_detections_per_image'] <= 5.0:
            print(f"    ✓ Avg detections/image: {pred_stats['avg_detections_per_image']:.2f} (<= 5.0)")
        else:
            print(f"    ⚠ Avg detections/image: {pred_stats['avg_detections_per_image']:.2f} (> 5.0, possible false positives)")

        if checks_passed:
            print(f"\n  ✓ TEST 2 PASSED: Predictions are consistent")
        else:
            print(f"\n  ⚠ TEST 2 WARNING: Some checks did not pass")
    else:
        print("  ✗ TEST 2 FAILED: Could not test predictions")

    # Generate Report
    report = {
        "model_path": MODEL_PATH,
        "test_date": str(Path(MODEL_PATH).stat().st_mtime),
        "baseline_metrics": baseline,
        "current_metrics": current_metrics,
        "comparison": comparison if baseline else None,
        "prediction_stats": pred_stats,
        "overall_status": "PASSED" if (comparison.get("all_passed", False) and checks_passed) else "FAILED"
    }

    # Save report
    output_path = Path(OUTPUT_FILE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(report, f, indent=2)

    print("\n" + "=" * 70)
    print("FINAL RESULT")
    print("=" * 70)

    if report["overall_status"] == "PASSED":
        print("\n  ✓✓✓ ALL TESTS PASSED ✓✓✓")
        print(f"\n  The newly trained model performs within ±{TOLERANCE*100}% of the baseline.")
        print("  The model is validated and ready for use!")
    else:
        print("\n  ✗✗✗ SOME TESTS FAILED ✗✗✗")
        print("\n  Please review the results above.")

    print(f"\n  Detailed report saved to: {OUTPUT_FILE}")
    print("=" * 70)

    return 0 if report["overall_status"] == "PASSED" else 1


if __name__ == "__main__":
    sys.exit(main())
