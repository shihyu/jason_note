#!/usr/bin/env python3
"""
Simple ONNX to TFLite converter using tf2onnx in reverse.

Actually, we'll use a simpler approach: use onnx-tf to convert ONNX to TensorFlow SavedModel,
then use TFLite converter to convert SavedModel to TFLite.
"""

import sys
import os
import numpy as np

def convert_onnx_to_tflite(onnx_path, tflite_path):
    """Convert ONNX model to TFLite using onnx-tf and TFLite converter."""

    print(f"Converting {onnx_path} to {tflite_path}...")

    # Try onnx-tensorflow package
    try:
        import onnx
        from onnx_tf.backend import prepare
    except ImportError:
        print("Installing onnx-tf...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "onnx-tf"])
        import onnx
        from onnx_tf.backend import prepare

    # Load ONNX model
    print("Loading ONNX model...")
    onnx_model = onnx.load(onnx_path)

    # Check model (skip opset compatibility check for IR version mismatch)
    try:
        onnx.checker.check_model(onnx_model, skip_opset_compatibility_check=True)
        print(f"✅ ONNX model loaded. IR version: {onnx_model.ir_version}")
    except Exception as e:
        print(f"⚠️  Model check warning: {e}")
        print(f"Proceeding with conversion anyway...")

    # Convert to TensorFlow
    print("Converting ONNX to TensorFlow...")
    tf_rep = prepare(onnx_model)

    # Export to SavedModel
    saved_model_path = os.path.dirname(tflite_path) + "/saved_model"
    print(f"Exporting to SavedModel: {saved_model_path}")
    tf_rep.export_graph(saved_model_path)

    # Convert SavedModel to TFLite
    print("Converting SavedModel to TFLite...")
    import tensorflow as tf

    converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
    converter.optimizations = [tf.lite.Optimize.DEFAULT]
    tflite_model = converter.convert()

    # Save TFLite model
    with open(tflite_path, 'wb') as f:
        f.write(tflite_model)

    print(f"✅ TFLite model saved to {tflite_path}")
    file_size = os.path.getsize(tflite_path)
    print(f"File size: {file_size / (1024*1024):.2f} MB")

    # Clean up SavedModel
    import shutil
    shutil.rmtree(saved_model_path)
    print(f"Cleaned up temporary SavedModel")

    return tflite_path


def test_tflite(tflite_path):
    """Test TFLite model."""
    print(f"\nTesting TFLite model...")

    import tensorflow as tf

    # Load TFLite model
    interpreter = tf.lite.Interpreter(model_path=tflite_path)
    interpreter.allocate_tensors()

    # Get input and output details
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    print(f"Input shape: {input_details[0]['shape']}")
    print(f"Input dtype: {input_details[0]['dtype']}")
    print(f"Output shape: {output_details[0]['shape']}")
    print(f"Output dtype: {output_details[0]['dtype']}")

    # Create test input
    input_shape = input_details[0]['shape']
    test_input = np.random.randn(*input_shape).astype(np.float32)

    # Run inference
    interpreter.set_tensor(input_details[0]['index'], test_input)
    interpreter.invoke()
    output = interpreter.get_tensor(output_details[0]['index'])

    print(f"✅ TFLite inference successful!")
    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.4f}, {output.max():.4f}]")


def main():
    # Paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    onnx_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2.onnx')
    tflite_path = os.path.join(script_dir, '../flutter_app/assets/models/mobileclip_s2.tflite')

    # Check if ONNX model exists
    if not os.path.exists(onnx_path):
        print(f"❌ ONNX model not found: {onnx_path}")
        return 1

    # Convert
    convert_onnx_to_tflite(onnx_path, tflite_path)

    # Test
    test_tflite(tflite_path)

    print("\n✅ Conversion completed successfully!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
