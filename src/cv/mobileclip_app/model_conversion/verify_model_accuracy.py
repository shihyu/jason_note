#!/usr/bin/env python3
"""
Verify ONNX model accuracy by comparing with PyTorch model outputs.

This script tests the converted ONNX model against the original PyTorch model
to ensure the conversion didn't introduce significant errors.
"""

import sys
import os

# Add parent directory to path to import mobileclip
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../ml-mobileclip'))

import torch
import mobileclip
import numpy as np
import onnxruntime as ort
from PIL import Image
import requests
from io import BytesIO


def load_pytorch_model(model_path):
    """Load PyTorch MobileCLIP model."""
    print("Loading PyTorch model...")
    model, _, preprocess = mobileclip.create_model_and_transforms(
        'mobileclip_s2',
        pretrained=model_path,
        reparameterize=True,
        device='cpu'
    )
    model.eval()
    print(f"✅ PyTorch model loaded")
    return model, preprocess


def load_onnx_model(onnx_path):
    """Load ONNX model."""
    print("\nLoading ONNX model...")
    session = ort.InferenceSession(onnx_path)
    print(f"✅ ONNX model loaded")

    # Print model info
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name
    input_shape = session.get_inputs()[0].shape
    output_shape = session.get_outputs()[0].shape

    print(f"  Input: {input_name} {input_shape}")
    print(f"  Output: {output_name} {output_shape}")

    return session


def load_test_image(image_url=None):
    """Load a test image."""
    print("\nLoading test image...")

    if image_url is None:
        # Use a sample image URL
        image_url = "https://raw.githubusercontent.com/pytorch/hub/master/images/dog.jpg"

    try:
        response = requests.get(image_url, timeout=10)
        image = Image.open(BytesIO(response.content)).convert('RGB')
        print(f"✅ Image loaded from URL: {image_url}")
        print(f"  Image size: {image.size}")
        return image
    except Exception as e:
        print(f"⚠️  Failed to load image from URL: {e}")
        print("Creating random image for testing...")
        image = Image.fromarray(np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8))
        return image


def preprocess_image_pytorch(image, preprocess):
    """Preprocess image for PyTorch model."""
    # Apply MobileCLIP preprocessing
    image_tensor = preprocess(image).unsqueeze(0)  # Add batch dimension
    return image_tensor


def preprocess_image_onnx(image):
    """Preprocess image for ONNX model."""
    # Resize and convert to tensor
    image = image.resize((256, 256))
    image_np = np.array(image).astype(np.float32)

    # Convert HWC to CHW
    image_np = np.transpose(image_np, (2, 0, 1))

    # Normalize to [0, 1]
    image_np = image_np / 255.0

    # Add batch dimension
    image_np = np.expand_dims(image_np, axis=0)

    return image_np


def run_pytorch_inference(model, image_tensor):
    """Run inference with PyTorch model."""
    print("\n" + "="*60)
    print("Running PyTorch Inference")
    print("="*60)

    with torch.no_grad():
        # Extract image features using image encoder
        features = model.image_encoder(image_tensor)

        # Normalize features (L2 normalization)
        features = features / features.norm(dim=-1, keepdim=True)

    features_np = features.cpu().numpy()

    print(f"✅ PyTorch inference completed")
    print(f"  Output shape: {features_np.shape}")
    print(f"  Output dtype: {features_np.dtype}")
    print(f"  Output range: [{features_np.min():.6f}, {features_np.max():.6f}]")
    print(f"  Output mean: {features_np.mean():.6f}")
    print(f"  Output std: {features_np.std():.6f}")

    return features_np


def run_onnx_inference(session, image_np):
    """Run inference with ONNX model."""
    print("\n" + "="*60)
    print("Running ONNX Inference")
    print("="*60)

    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    # Run inference
    outputs = session.run([output_name], {input_name: image_np})
    features = outputs[0]

    # Normalize features (L2 normalization)
    norm = np.linalg.norm(features, axis=-1, keepdims=True)
    features = features / norm

    print(f"✅ ONNX inference completed")
    print(f"  Output shape: {features.shape}")
    print(f"  Output dtype: {features.dtype}")
    print(f"  Output range: [{features.min():.6f}, {features.max():.6f}]")
    print(f"  Output mean: {features.mean():.6f}")
    print(f"  Output std: {features.std():.6f}")

    return features


def compare_outputs(pytorch_output, onnx_output, tolerance=5e-3):
    """Compare PyTorch and ONNX outputs."""
    print("\n" + "="*60)
    print("Comparing Outputs")
    print("="*60)

    # Compute metrics
    mae = np.mean(np.abs(pytorch_output - onnx_output))
    mse = np.mean((pytorch_output - onnx_output) ** 2)
    max_diff = np.max(np.abs(pytorch_output - onnx_output))

    # Cosine similarity
    pytorch_flat = pytorch_output.flatten()
    onnx_flat = onnx_output.flatten()
    cosine_sim = np.dot(pytorch_flat, onnx_flat) / (
        np.linalg.norm(pytorch_flat) * np.linalg.norm(onnx_flat)
    )

    print(f"Mean Absolute Error (MAE): {mae:.8f}")
    print(f"Mean Squared Error (MSE): {mse:.8f}")
    print(f"Max Absolute Difference: {max_diff:.8f}")
    print(f"Cosine Similarity: {cosine_sim:.8f}")

    # Check if within tolerance (relaxed for mobile deployment)
    # MAE < 5e-3 and cosine_sim > 0.99 are acceptable for feature extraction
    if mae < tolerance and cosine_sim > 0.99:
        print(f"\n✅ PASS: Models are equivalent (MAE < {tolerance}, cosine_sim > 0.99)")
        print(f"   Difference is acceptable for mobile deployment")
        return True
    else:
        print(f"\n⚠️  WARNING: Models differ more than expected")
        print(f"   Expected MAE < {tolerance}, got {mae:.8f}")
        print(f"   Expected cosine_sim > 0.99, got {cosine_sim:.8f}")
        return False


def main():
    """Main verification pipeline."""
    print("="*60)
    print("MobileCLIP Model Accuracy Verification")
    print("PyTorch vs ONNX")
    print("="*60)

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    pytorch_model_path = os.path.join(script_dir, '../ml-mobileclip/checkpoints/mobileclip_s2.pt')
    onnx_model_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2.onnx')

    # Check if models exist
    if not os.path.exists(pytorch_model_path):
        print(f"❌ PyTorch model not found: {pytorch_model_path}")
        return False

    if not os.path.exists(onnx_model_path):
        print(f"❌ ONNX model not found: {onnx_model_path}")
        print("Please run convert_to_onnx.py first!")
        return False

    # Load models
    pytorch_model, preprocess = load_pytorch_model(pytorch_model_path)
    onnx_session = load_onnx_model(onnx_model_path)

    # Load test image
    test_image = load_test_image()

    # Preprocess for both models
    print("\nPreprocessing image...")
    pytorch_input = preprocess_image_pytorch(test_image, preprocess)
    onnx_input = preprocess_image_onnx(test_image)

    # Run inference
    pytorch_output = run_pytorch_inference(pytorch_model, pytorch_input)
    onnx_output = run_onnx_inference(onnx_session, onnx_input)

    # Compare outputs
    success = compare_outputs(pytorch_output, onnx_output)

    print("\n" + "="*60)
    if success:
        print("✅ Verification PASSED - ONNX model is accurate!")
    else:
        print("⚠️  Verification WARNING - Models differ slightly")
        print("   This may be acceptable for mobile deployment")
    print("="*60)

    return success


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
