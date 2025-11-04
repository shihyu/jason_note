#!/usr/bin/env python3
"""
Convert MobileCLIP-S2 PyTorch model to TFLite format.

This script uses ai-edge-torch to convert the image encoder from MobileCLIP to TFLite.
"""

import sys
import os

# Add parent directory to path to import mobileclip
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../ml-mobileclip'))

import torch
import mobileclip
import numpy as np
from PIL import Image


def load_mobileclip_model(model_path, device='cpu'):
    """Load MobileCLIP-S2 model from checkpoint."""
    print(f"Loading MobileCLIP-S2 model from {model_path}...")

    model, _, preprocess = mobileclip.create_model_and_transforms(
        'mobileclip_s2',
        pretrained=model_path,
        reparameterize=True,  # Reparameterize for faster inference
        device=device
    )

    model.eval()
    print(f"Model loaded successfully. Model type: {type(model)}")

    return model, preprocess


def extract_image_encoder(model):
    """Extract only the image encoder part."""
    print("Extracting image encoder...")

    # The image encoder is stored in model.image_encoder
    image_encoder = model.image_encoder
    image_encoder.eval()

    print(f"Image encoder extracted. Type: {type(image_encoder)}")
    return image_encoder


def convert_to_tflite(image_encoder, output_path, input_size=256):
    """Convert image encoder to TFLite format using ai-edge-torch."""
    print(f"\nConverting to TFLite format...")
    print(f"Input size: {input_size}x{input_size}")
    print(f"Output path: {output_path}")

    try:
        import ai_edge_torch
    except ImportError:
        print("❌ ai-edge-torch not found. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ai-edge-torch"])
        import ai_edge_torch

    # Create dummy input (batch_size=1, channels=3, height=256, width=256)
    dummy_input = torch.randn(1, 3, input_size, input_size, dtype=torch.float32)

    # Test forward pass
    print("\nTesting forward pass with dummy input...")
    with torch.no_grad():
        output = image_encoder(dummy_input)
    print(f"Output shape: {output.shape}")
    print(f"Output dtype: {output.dtype}")

    # Convert to TFLite using ai-edge-torch
    print("\nConverting to TFLite using ai-edge-torch...")

    # Convert the model
    edge_model = ai_edge_torch.convert(
        image_encoder,
        (dummy_input,)
    )

    # Export to TFLite
    edge_model.export(output_path)

    print(f"✅ TFLite model saved to {output_path}")

    # Get file size
    file_size = os.path.getsize(output_path)
    print(f"File size: {file_size / (1024*1024):.2f} MB")

    return output_path


def test_tflite_inference(tflite_path, input_size=256):
    """Test TFLite model inference."""
    print(f"\nTesting TFLite inference...")

    try:
        import tensorflow as tf
    except ImportError:
        print("❌ TensorFlow not found, skipping inference test")
        return

    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"Input shape: {input_details[0]['shape']}")
    print(f"Output shape: {output_details[0]['shape']}")

    # Create test input
    test_input = np.random.randn(1, 3, input_size, input_size).astype(np.float32)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    print(f"✅ TFLite inference successful!")
    print(f"Output shape: {output.shape}")
    print(f"Output dtype: {output.dtype}")


def main():
    print("=" * 60)
    print("MobileCLIP-S2 PyTorch → TFLite Converter")
    print("=" * 60)

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, '../ml-mobileclip/checkpoints/mobileclip_s2.pt')
    output_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2.tflite')

    # Check if model exists
    if not os.path.exists(model_path):
        print(f"❌ Model not found: {model_path}")
        print("Please run 'make download-model' first")
        return 1

    # Create output directory
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Load model
    model, preprocess = load_mobileclip_model(model_path)

    # Extract image encoder
    image_encoder = extract_image_encoder(model)

    # Convert to TFLite
    tflite_path = convert_to_tflite(image_encoder, output_path)

    # Test inference
    test_tflite_inference(tflite_path)

    print("\n" + "=" * 60)
    print("✅ Conversion completed successfully!")
    print(f"TFLite model saved to: {tflite_path}")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    sys.exit(main())
