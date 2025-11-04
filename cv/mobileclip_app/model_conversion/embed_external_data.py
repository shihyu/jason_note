#!/usr/bin/env python3
"""
Convert ONNX model with external data to embedded data format.

This script loads an ONNX model that uses external data file and
re-saves it with all data embedded in the .onnx file.
"""

import onnx
from onnx.external_data_helper import convert_model_to_external_data, convert_model_from_external_data
import os

def embed_external_data(input_onnx_path, output_onnx_path):
    """Convert ONNX model from external data to embedded data."""
    print(f"Loading ONNX model from {input_onnx_path}...")

    # Load model with external data
    model = onnx.load(input_onnx_path)

    print(f"Model IR version: {model.ir_version}")
    print(f"Model opset version: {model.opset_import[0].version}")
    print(f"Total initializers: {len(model.graph.initializer)}")

    # Check external data
    external_count = sum(1 for init in model.graph.initializer if len(init.external_data) > 0)
    print(f"Initializers with external data: {external_count}/{len(model.graph.initializer)}")

    # Convert from external data to embedded
    print("\nConverting to embedded data format...")
    onnx.save_model(
        model,
        output_onnx_path,
        save_as_external_data=False,  # Embed all data in the .onnx file
    )

    # Verify the conversion
    print("\nVerifying converted model...")
    model_embedded = onnx.load(output_onnx_path)
    external_count_after = sum(1 for init in model_embedded.graph.initializer if len(init.external_data) > 0)

    # Get file size
    file_size_mb = os.path.getsize(output_onnx_path) / (1024 * 1024)

    print(f"✅ Conversion complete!")
    print(f"   Output file: {output_onnx_path}")
    print(f"   File size: {file_size_mb:.2f} MB")
    print(f"   External data references: {external_count_after}")

    if external_count_after == 0:
        print("✅ All data successfully embedded!")
    else:
        print(f"⚠️  Warning: Still {external_count_after} external data references")

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2.onnx')
    output_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2_embedded.onnx')

    embed_external_data(input_path, output_path)
