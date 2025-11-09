#!/usr/bin/env python3
"""
YOLOv8 Guitar Detection Validation Script

This script validates the trained model and compares metrics against baseline.
"""

import os
import sys
import json
from pathlib import Path
from ultralytics import YOLO


def load_baseline_metrics(baseline_file="tests/baseline_metrics.json"):
    """Load baseline metrics from JSON file"""
    baseline_path = Path(baseline_file)
    if baseline_path.exists():
        with open(baseline_path, 'r') as f:
            return json.load(f)
    return None


def save_current_metrics(metrics, output_file="tests/current_metrics.json"):
    """Save current validation metrics to JSON file"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)


def compare_metrics(current, baseline, tolerance=0.05):
    """
    Compare current metrics with baseline

    Args:
        current: Current validation metrics
        baseline: Baseline metrics
        tolerance: Acceptable deviation (default 5%)

    Returns:
        dict with comparison results
    """
    if baseline is None:
        return {
            "status": "no_baseline",
            "message": "No baseline metrics found for comparison"
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

        # Calculate acceptable range
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
        "metrics": results
    }


def main():
    """Validate trained model and compare with baseline"""

    # Configuration
    DATA_CONFIG = "guitar_dataset.yaml"
    MODEL_PATH = "runs/detect/guitar_train/weights/best.pt"
    BASELINE_FILE = "tests/baseline_metrics.json"
    TOLERANCE = 0.05  # 5% tolerance

    print("=" * 60)
    print("YOLOv8 Guitar Detection Validation")
    print("=" * 60)

    # Check if model exists
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        print(f"ERROR: Trained model not found at {MODEL_PATH}")
        print("Please run training first: make train")
        sys.exit(1)

    # Check if config exists
    config_path = Path(DATA_CONFIG)
    if not config_path.exists():
        print(f"ERROR: Config file not found at {config_path}")
        sys.exit(1)

    # Load baseline metrics
    baseline = load_baseline_metrics(BASELINE_FILE)
    if baseline:
        print(f"\nBaseline metrics loaded from: {BASELINE_FILE}")
        print(f"  Precision: {baseline.get('precision', 'N/A')}")
        print(f"  Recall: {baseline.get('recall', 'N/A')}")
        print(f"  mAP50: {baseline.get('mAP50', 'N/A')}")
        print(f"  mAP50-95: {baseline.get('mAP50-95', 'N/A')}")
    else:
        print(f"\nNo baseline metrics found.")
        print(f"Current validation will be saved as baseline.")

    # Load model
    print(f"\nLoading model from: {MODEL_PATH}")
    model = YOLO(MODEL_PATH)

    # Run validation
    print(f"\nRunning validation on dataset...")
    print("=" * 60)

    try:
        results = model.val(
            data=DATA_CONFIG,
            batch=16,
            imgsz=640,
            verbose=True,
            device=None,  # Auto-detect GPU/CPU
        )

        print("=" * 60)
        print("Validation completed!")
        print("=" * 60)

        # Extract metrics from results
        # YOLOv8 validation results structure
        metrics_box = results.box
        current_metrics = {
            "precision": float(metrics_box.mp),  # mean precision
            "recall": float(metrics_box.mr),     # mean recall
            "mAP50": float(metrics_box.map50),   # mAP@0.5
            "mAP50-95": float(metrics_box.map),  # mAP@0.5:0.95
        }

        print(f"\nCurrent Validation Metrics:")
        print(f"  Precision: {current_metrics['precision']:.4f}")
        print(f"  Recall: {current_metrics['recall']:.4f}")
        print(f"  mAP50: {current_metrics['mAP50']:.4f}")
        print(f"  mAP50-95: {current_metrics['mAP50-95']:.4f}")

        # Save current metrics
        save_current_metrics(current_metrics)
        print(f"\nCurrent metrics saved to: tests/current_metrics.json")

        # Compare with baseline
        if baseline:
            print("\n" + "=" * 60)
            print("Baseline Comparison")
            print("=" * 60)

            comparison = compare_metrics(current_metrics, baseline, TOLERANCE)

            if comparison["status"] == "no_baseline":
                print(comparison["message"])
            else:
                print(f"\nTolerance: ±{TOLERANCE*100}%")
                print(f"\n{'Metric':<12} {'Current':<10} {'Baseline':<10} {'Diff':<10} {'Diff%':<10} {'Status'}")
                print("-" * 70)

                for metric, data in comparison["metrics"].items():
                    status = "✓ PASS" if data["passed"] else "✗ FAIL"
                    print(f"{metric:<12} {data['current']:<10.4f} {data['baseline']:<10.4f} "
                          f"{data['diff']:<+10.4f} {data['diff_pct']:<+10.2f} {status}")

                print("-" * 70)
                print(f"\nOverall Status: {'✓ PASSED' if comparison['all_passed'] else '✗ FAILED'}")

                if not comparison['all_passed']:
                    print("\nWARNING: Some metrics fell below baseline threshold!")
                    return 1
        else:
            # Save as baseline if none exists
            baseline_path = Path(BASELINE_FILE)
            baseline_path.parent.mkdir(parents=True, exist_ok=True)
            with open(baseline_path, 'w') as f:
                json.dump(current_metrics, f, indent=2)
            print(f"\nBaseline metrics saved to: {BASELINE_FILE}")

        return 0

    except Exception as e:
        print("=" * 60)
        print(f"ERROR: Validation failed with exception:")
        print(f"  {str(e)}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
