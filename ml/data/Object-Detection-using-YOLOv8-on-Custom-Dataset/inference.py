#!/usr/bin/env python3
"""
YOLOv8 Guitar Detection Inference Script

This script runs inference on the validation dataset and saves predictions.
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO


def main():
    """Run inference on validation dataset"""

    # Configuration
    MODEL_PATH = "runs/detect/guitar_train/weights/best.pt"
    SOURCE_DIR = "Dataset/Guitar_dataset/val/images"
    OUTPUT_DIR = "tests/inference_results"
    IMG_SIZE = 640
    CONFIDENCE = 0.6

    print("=" * 60)
    print("YOLOv8 Guitar Detection Inference")
    print("=" * 60)

    # Check if model exists
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        print(f"ERROR: Trained model not found at {MODEL_PATH}")
        print("Please run training first: make train")
        sys.exit(1)

    # Check if source directory exists
    source_dir = Path(SOURCE_DIR)
    if not source_dir.exists():
        print(f"ERROR: Source directory not found at {SOURCE_DIR}")
        sys.exit(1)

    # Count images
    images = list(source_dir.glob("*.jpg")) + list(source_dir.glob("*.JPG"))
    print(f"\nSource: {SOURCE_DIR}")
    print(f"Images to process: {len(images)}")

    if len(images) == 0:
        print("ERROR: No images found in source directory")
        sys.exit(1)

    # Create output directory
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)

    # Configuration
    print(f"\nInference Configuration:")
    print(f"  Model: {MODEL_PATH}")
    print(f"  Image Size: {IMG_SIZE}x{IMG_SIZE}")
    print(f"  Confidence Threshold: {CONFIDENCE}")
    print(f"  Output: {OUTPUT_DIR}")

    # Load model
    print(f"\nLoading model...")
    model = YOLO(MODEL_PATH)

    # Run inference
    print(f"\nRunning inference...")
    print("=" * 60)

    try:
        results = model.predict(
            source=SOURCE_DIR,
            imgsz=IMG_SIZE,
            conf=CONFIDENCE,
            save=True,
            project=str(output_path.parent),
            name=output_path.name,
            exist_ok=True,
            verbose=True,
        )

        print("=" * 60)
        print("Inference completed!")
        print("=" * 60)

        # Count detections
        total_detections = 0
        images_with_detections = 0

        for result in results:
            num_boxes = len(result.boxes)
            total_detections += num_boxes
            if num_boxes > 0:
                images_with_detections += 1

        print(f"\nInference Summary:")
        print(f"  Total images processed: {len(results)}")
        print(f"  Images with detections: {images_with_detections}")
        print(f"  Total detections: {total_detections}")
        print(f"  Average detections per image: {total_detections/len(results):.2f}")

        print(f"\nPrediction images saved to:")
        print(f"  {output_path}")

        # Print some sample detection details
        print(f"\nSample Detections:")
        for i, result in enumerate(results[:5]):  # Show first 5
            img_name = Path(result.path).name
            num_boxes = len(result.boxes)
            if num_boxes > 0:
                confidences = [float(box.conf) for box in result.boxes]
                avg_conf = sum(confidences) / len(confidences)
                print(f"  {img_name}: {num_boxes} guitar(s), avg confidence: {avg_conf:.3f}")
            else:
                print(f"  {img_name}: No detections")

        return 0

    except Exception as e:
        print("=" * 60)
        print(f"ERROR: Inference failed with exception:")
        print(f"  {str(e)}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
