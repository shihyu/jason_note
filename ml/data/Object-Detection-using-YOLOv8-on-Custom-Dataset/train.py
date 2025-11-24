#!/usr/bin/env python3
"""
YOLOv8 Guitar Detection Training Script

This script trains a YOLOv8 model on the custom guitar dataset.
Based on the original Jupyter notebook training configuration.
"""

import os
import sys
from pathlib import Path
from ultralytics import YOLO


def main():
    """Train YOLOv8 model on guitar dataset"""

    # Configuration (can be overridden by environment variable)
    MODEL = "yolov8n.pt"
    DATA_CONFIG = "guitar_dataset.yaml"
    EPOCHS = int(os.environ.get("EPOCHS", "300"))  # Allow override via env var
    BATCH_SIZE = 16
    IMG_SIZE = 640
    PROJECT_NAME = "runs/detect"
    TRAIN_NAME = "guitar_train"

    print("=" * 60)
    print("YOLOv8 Guitar Detection Training")
    print("=" * 60)

    # Verify dataset exists
    dataset_path = Path("Dataset/Guitar_dataset")
    if not dataset_path.exists():
        print(f"ERROR: Dataset not found at {dataset_path}")
        sys.exit(1)

    # Verify config file exists
    config_path = Path(DATA_CONFIG)
    if not config_path.exists():
        print(f"ERROR: Config file not found at {config_path}")
        sys.exit(1)

    # Check training and validation images
    train_images = list((dataset_path / "train" / "images").glob("*.jpg")) + \
                   list((dataset_path / "train" / "images").glob("*.JPG"))
    val_images = list((dataset_path / "val" / "images").glob("*.jpg")) + \
                 list((dataset_path / "val" / "images").glob("*.JPG"))

    print(f"\nDataset Info:")
    print(f"  Training images: {len(train_images)}")
    print(f"  Validation images: {len(val_images)}")

    if len(train_images) == 0 or len(val_images) == 0:
        print("ERROR: No images found in dataset")
        sys.exit(1)

    # Training parameters
    print(f"\nTraining Configuration:")
    print(f"  Model: {MODEL}")
    print(f"  Epochs: {EPOCHS}")
    print(f"  Batch Size: {BATCH_SIZE}")
    print(f"  Image Size: {IMG_SIZE}x{IMG_SIZE}")
    print(f"  Augmentation: Enabled")
    print(f"  Output: {PROJECT_NAME}/{TRAIN_NAME}")

    # Initialize model
    print(f"\nInitializing YOLOv8 model...")
    model = YOLO(MODEL)

    # Train the model
    print(f"\nStarting training...")
    print("=" * 60)

    try:
        results = model.train(
            data=DATA_CONFIG,
            epochs=EPOCHS,
            batch=BATCH_SIZE,
            imgsz=IMG_SIZE,
            augment=True,
            project=PROJECT_NAME,
            name=TRAIN_NAME,
            exist_ok=True,  # Allow overwriting existing run
            verbose=True,
            device=None,  # Auto-detect GPU/CPU
        )

        print("=" * 60)
        print("Training completed successfully!")
        print("=" * 60)

        # Print output locations
        output_dir = Path(PROJECT_NAME) / TRAIN_NAME
        print(f"\nModel weights saved to:")
        print(f"  Best: {output_dir / 'weights' / 'best.pt'}")
        print(f"  Last: {output_dir / 'weights' / 'last.pt'}")
        print(f"\nTraining results saved to:")
        print(f"  {output_dir}")

        return 0

    except Exception as e:
        print("=" * 60)
        print(f"ERROR: Training failed with exception:")
        print(f"  {str(e)}")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
