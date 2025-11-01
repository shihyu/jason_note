#!/usr/bin/env python3
"""
Convert MobileCLIP-S2 PyTorch model to ONNX format.

This script extracts the image encoder from MobileCLIP and converts it to ONNX.
"""

import sys
import os

# Add parent directory to path to import mobileclip
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../ml-mobileclip'))

import torch
import mobileclip
from mobileclip.modules.common.mobileone import reparameterize_model
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


def convert_to_onnx(image_encoder, output_path, input_size=256):
    """Convert image encoder to ONNX format."""
    print(f"\nConverting to ONNX format...")
    print(f"Input size: {input_size}x{input_size}")
    print(f"Output path: {output_path}")

    # Create dummy input (batch_size=1, channels=3, height=256, width=256)
    dummy_input = torch.randn(1, 3, input_size, input_size, dtype=torch.float32)

    # Test forward pass
    print("\nTesting forward pass with dummy input...")
    with torch.no_grad():
        output = image_encoder(dummy_input)
    print(f"Output shape: {output.shape}")
    print(f"Output dtype: {output.dtype}")

    # Export to ONNX
    print("\nExporting to ONNX...")
    torch.onnx.export(
        image_encoder,                    # Model to export
        dummy_input,                      # Model input (or a tuple for multiple inputs)
        output_path,                      # Where to save the model
        export_params=True,               # Store the trained parameter weights
        opset_version=17,                 # ONNX opset version (17 for better compatibility)
        do_constant_folding=True,         # Optimize constant folding
        input_names=['input'],            # Input name
        output_names=['output'],          # Output name
        dynamic_axes={                    # Dynamic axes for variable batch size
            'input': {0: 'batch_size'},
            'output': {0: 'batch_size'}
        }
    )

    print(f"✅ ONNX model saved to {output_path}")

    # Verify ONNX model
    print("\nVerifying ONNX model...")
    import onnx
    onnx_model = onnx.load(output_path)
    onnx.checker.check_model(onnx_model)
    print("✅ ONNX model verification passed")

    return output_path


def test_onnx_inference(onnx_path, input_size=256):
    """Test ONNX model inference using onnxruntime."""
    print(f"\nTesting ONNX inference...")

    import onnxruntime as ort

    # Create ONNX Runtime session
    session = ort.InferenceSession(onnx_path)

    # Get input/output names
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    print(f"Input name: {input_name}")
    print(f"Output name: {output_name}")

    # Create dummy input
    dummy_input = np.random.randn(1, 3, input_size, input_size).astype(np.float32)

    # Run inference
    outputs = session.run([output_name], {input_name: dummy_input})

    print(f"✅ ONNX inference successful!")
    print(f"Output shape: {outputs[0].shape}")
    print(f"Output dtype: {outputs[0].dtype}")

    return outputs[0]


def main():
    """Main conversion pipeline."""
    print("=" * 60)
    print("MobileCLIP-S2 PyTorch → ONNX Converter")
    print("=" * 60)

    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(script_dir, '../../ml-mobileclip/checkpoints/mobileclip_s2.pt')
    output_dir = os.path.join(script_dir, '../flutter_app/assets/models')
    onnx_path = os.path.join(output_dir, 'mobileclip_s2.onnx')

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Load MobileCLIP model
    model, preprocess = load_mobileclip_model(model_path)

    # Step 2: Extract image encoder
    image_encoder = extract_image_encoder(model)

    # Step 3: Convert to ONNX
    convert_to_onnx(image_encoder, onnx_path, input_size=256)

    # Step 4: Test ONNX inference
    test_onnx_inference(onnx_path, input_size=256)

    print("\n" + "=" * 60)
    print("✅ Conversion completed successfully!")
    print(f"ONNX model saved to: {onnx_path}")
    print("=" * 60)

    # Print model info
    import onnx
    model = onnx.load(onnx_path)
    file_size = os.path.getsize(onnx_path) / (1024 * 1024)  # MB
    print(f"\nModel info:")
    print(f"  File size: {file_size:.2f} MB")
    print(f"  Input shape: {model.graph.input[0].type.tensor_type.shape}")
    print(f"  Output shape: {model.graph.output[0].type.tensor_type.shape}")


if __name__ == '__main__':
    main()
