#!/usr/bin/env python3
"""
YOLOv8 Guitar Detection Visualization and Comparison Script

This script generates a comprehensive HTML report comparing:
- Training curves (loss, metrics)
- Confusion matrices
- Prediction results vs ground truth
- Metric comparison table
"""

import os
import sys
import json
import base64
from pathlib import Path
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from datetime import datetime


def load_metrics(filepath):
    """Load metrics from JSON file"""
    if Path(filepath).exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    return None


def image_to_base64(image_path):
    """Convert image file to base64 string for HTML embedding"""
    if not Path(image_path).exists():
        return None
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def generate_html_report(
    baseline_metrics,
    current_metrics,
    train_dir,
    inference_dir,
    output_file="tests/comparison_report.html"
):
    """Generate comprehensive HTML comparison report"""

    html_content = f"""
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YOLOv8 Guitar Detection - Training Comparison Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #34495e;
            margin-top: 40px;
            border-left: 4px solid #3498db;
            padding-left: 15px;
        }}
        .timestamp {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        .metrics-table th {{
            background-color: #3498db;
            color: white;
            padding: 12px;
            text-align: left;
        }}
        .metrics-table td {{
            padding: 10px;
            border-bottom: 1px solid #ecf0f1;
        }}
        .metrics-table tr:hover {{
            background-color: #f8f9fa;
        }}
        .pass {{
            color: #27ae60;
            font-weight: bold;
        }}
        .fail {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .image-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .image-card img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .image-caption {{
            padding: 10px;
            background-color: #f8f9fa;
            font-size: 0.9em;
            color: #495057;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
        .success {{
            background-color: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 20px 0;
        }}
        .info {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🎸 YOLOv8 Guitar Detection - Training Comparison Report</h1>
        <div class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
"""

    # Metrics Comparison Section
    html_content += """
        <h2>📊 Metrics Comparison</h2>
"""

    if baseline_metrics and current_metrics:
        # Calculate differences
        metrics_list = ["precision", "recall", "mAP50", "mAP50-95"]
        tolerance = 0.05

        all_passed = True
        table_rows = ""

        for metric in metrics_list:
            if metric in baseline_metrics and metric in current_metrics:
                baseline_val = baseline_metrics[metric]
                current_val = current_metrics[metric]
                diff = current_val - baseline_val
                diff_pct = (diff / baseline_val) * 100 if baseline_val > 0 else 0
                lower_bound = baseline_val * (1 - tolerance)
                passed = current_val >= lower_bound

                if not passed:
                    all_passed = False

                status_class = "pass" if passed else "fail"
                status_text = "✓ PASS" if passed else "✗ FAIL"

                table_rows += f"""
                <tr>
                    <td><strong>{metric}</strong></td>
                    <td>{current_val:.4f}</td>
                    <td>{baseline_val:.4f}</td>
                    <td>{diff:+.4f}</td>
                    <td>{diff_pct:+.2f}%</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
"""

        overall_class = "success" if all_passed else "warning"
        overall_text = "✓ All metrics passed!" if all_passed else "⚠ Some metrics below threshold"

        html_content += f"""
        <div class="{overall_class}">
            <strong>{overall_text}</strong> (Tolerance: ±{tolerance*100}%)
        </div>

        <table class="metrics-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Current</th>
                    <th>Baseline</th>
                    <th>Difference</th>
                    <th>Difference %</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {table_rows}
            </tbody>
        </table>
"""
    else:
        html_content += """
        <div class="info">
            No baseline metrics available for comparison. Current metrics will serve as baseline.
        </div>
"""

    # Training Curves Section
    html_content += """
        <h2>📈 Training Results</h2>
"""

    # Check for training result images
    results_img = Path(train_dir) / "results.png"
    confusion_matrix_img = Path(train_dir) / "confusion_matrix_normalized.png"
    pr_curve_img = Path(train_dir) / "PR_curve.png"

    if results_img.exists():
        results_b64 = image_to_base64(results_img)
        html_content += f"""
        <div class="image-card">
            <img src="data:image/png;base64,{results_b64}" alt="Training Results">
            <div class="image-caption">Training curves showing loss and metrics over epochs</div>
        </div>
"""

    # Confusion Matrix Section
    html_content += """
        <h2>🎯 Confusion Matrix & PR Curve</h2>
        <div class="image-grid">
"""

    if confusion_matrix_img.exists():
        cm_b64 = image_to_base64(confusion_matrix_img)
        html_content += f"""
            <div class="image-card">
                <img src="data:image/png;base64,{cm_b64}" alt="Confusion Matrix">
                <div class="image-caption">Normalized confusion matrix</div>
            </div>
"""

    if pr_curve_img.exists():
        pr_b64 = image_to_base64(pr_curve_img)
        html_content += f"""
            <div class="image-card">
                <img src="data:image/png;base64,{pr_b64}" alt="PR Curve">
                <div class="image-caption">Precision-Recall curve</div>
            </div>
"""

    html_content += """
        </div>
"""

    # Inference Results Section
    html_content += """
        <h2>🔍 Inference Results (Sample Predictions)</h2>
        <div class="image-grid">
"""

    # Find inference result images
    inference_path = Path(inference_dir)
    if inference_path.exists():
        image_files = sorted(list(inference_path.glob("*.jpg")) + list(inference_path.glob("*.JPG")))
        # Show up to 12 images
        for img_path in image_files[:12]:
            img_b64 = image_to_base64(img_path)
            if img_b64:
                html_content += f"""
            <div class="image-card">
                <img src="data:image/png;base64,{img_b64}" alt="{img_path.name}">
                <div class="image-caption">{img_path.name}</div>
            </div>
"""

    html_content += """
        </div>
"""

    # Footer
    html_content += """
        <hr style="margin-top: 40px; border: none; border-top: 1px solid #ddd;">
        <div style="text-align: center; color: #7f8c8d; margin-top: 20px;">
            Generated by YOLOv8 Guitar Detection Training Pipeline
        </div>
    </div>
</body>
</html>
"""

    # Write HTML file
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    return output_path


def main():
    """Generate visualization comparison report"""

    # Configuration
    BASELINE_FILE = "tests/baseline_metrics.json"
    CURRENT_FILE = "tests/current_metrics.json"
    TRAIN_DIR = "runs/detect/guitar_train"
    INFERENCE_DIR = "tests/inference_results"
    OUTPUT_FILE = "tests/comparison_report.html"

    print("=" * 60)
    print("YOLOv8 Guitar Detection - Visualization Report")
    print("=" * 60)

    # Load metrics
    baseline_metrics = load_metrics(BASELINE_FILE)
    current_metrics = load_metrics(CURRENT_FILE)

    if baseline_metrics:
        print(f"\n✓ Baseline metrics loaded from: {BASELINE_FILE}")
    else:
        print(f"\n⚠ No baseline metrics found at: {BASELINE_FILE}")

    if current_metrics:
        print(f"✓ Current metrics loaded from: {CURRENT_FILE}")
    else:
        print(f"⚠ No current metrics found at: {CURRENT_FILE}")
        print("Please run validation first: make validate")
        sys.exit(1)

    # Check training directory
    train_path = Path(TRAIN_DIR)
    if not train_path.exists():
        print(f"\n⚠ Training directory not found: {TRAIN_DIR}")
        print("Some visualizations may be missing.")
    else:
        print(f"✓ Training directory found: {TRAIN_DIR}")

    # Check inference directory
    inference_path = Path(INFERENCE_DIR)
    if not inference_path.exists():
        print(f"\n⚠ Inference directory not found: {INFERENCE_DIR}")
        print("Inference results will not be included.")
        print("Run inference first: make inference")
    else:
        print(f"✓ Inference directory found: {INFERENCE_DIR}")

    # Generate report
    print(f"\nGenerating HTML report...")

    try:
        output_path = generate_html_report(
            baseline_metrics,
            current_metrics,
            TRAIN_DIR,
            INFERENCE_DIR,
            OUTPUT_FILE
        )

        print("=" * 60)
        print("Report generated successfully!")
        print("=" * 60)
        print(f"\nReport saved to: {output_path}")
        print(f"\nOpen the report with:")
        print(f"  xdg-open {output_path}")
        print(f"  # or")
        print(f"  firefox {output_path}")

        return 0

    except Exception as e:
        print("=" * 60)
        print(f"ERROR: Report generation failed:")
        print(f"  {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
