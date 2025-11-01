#!/usr/bin/env python3
"""
Pytest tests for MobileCLIP ONNX model.

Tests:
1. ONNX model file exists and is valid
2. ONNX model inference works
3. Output shape and values are correct
"""

import pytest
import os
import numpy as np
import onnxruntime as ort
import onnx


# Test configuration
ONNX_MODEL_PATH = '../flutter_app/assets/models/mobileclip_s2.onnx'
INPUT_SIZE = 256
FEATURE_DIM = 512


@pytest.fixture(scope='module')
def onnx_session():
    """Load ONNX model (shared across tests)."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    onnx_path = os.path.join(script_dir, ONNX_MODEL_PATH)

    session = ort.InferenceSession(onnx_path)
    return session


@pytest.fixture
def dummy_input():
    """Create dummy input for testing."""
    return np.random.randn(1, 3, INPUT_SIZE, INPUT_SIZE).astype(np.float32)


class TestONNXModel:
    """Test suite for ONNX model."""

    def test_onnx_file_exists(self):
        """Test that ONNX model file exists."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        onnx_path = os.path.join(script_dir, ONNX_MODEL_PATH)

        assert os.path.exists(onnx_path), f"ONNX model not found: {onnx_path}"

        # Check file size (should be > 1MB)
        file_size = os.path.getsize(onnx_path) / (1024 * 1024)
        assert file_size > 1.0, f"ONNX model too small: {file_size:.2f} MB"

    def test_onnx_model_valid(self):
        """Test that ONNX model is valid."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        onnx_path = os.path.join(script_dir, ONNX_MODEL_PATH)

        # Load and check model
        model = onnx.load(onnx_path)
        onnx.checker.check_model(model)

        # Check input/output shapes
        input_shape = [dim.dim_value if dim.dim_value > 0 else -1
                      for dim in model.graph.input[0].type.tensor_type.shape.dim]
        output_shape = [dim.dim_value if dim.dim_value > 0 else -1
                       for dim in model.graph.output[0].type.tensor_type.shape.dim]

        assert input_shape[1:] == [3, INPUT_SIZE, INPUT_SIZE], \
            f"Unexpected input shape: {input_shape}"
        assert output_shape[-1] == FEATURE_DIM, \
            f"Unexpected output dimension: {output_shape}"

    def test_onnx_inference(self, onnx_session, dummy_input):
        """Test ONNX model inference."""
        input_name = onnx_session.get_inputs()[0].name
        output_name = onnx_session.get_outputs()[0].name

        # Run inference
        outputs = onnx_session.run([output_name], {input_name: dummy_input})
        features = outputs[0]

        # Check output shape
        assert features.shape == (1, FEATURE_DIM), \
            f"Unexpected output shape: {features.shape}"

        # Check output is not all zeros
        assert not np.allclose(features, 0), "Output is all zeros"

        # Check output is finite
        assert np.all(np.isfinite(features)), "Output contains NaN or Inf"



class TestModelBehavior:
    """Test ONNX model behavior."""

    def test_output_deterministic(self, onnx_session, dummy_input):
        """Test that ONNX model output is deterministic."""
        input_name = onnx_session.get_inputs()[0].name
        output_name = onnx_session.get_outputs()[0].name

        # Run inference twice
        output1 = onnx_session.run([output_name], {input_name: dummy_input})[0]
        output2 = onnx_session.run([output_name], {input_name: dummy_input})[0]

        # Outputs should be identical
        assert np.allclose(output1, output2, atol=1e-8), \
            "Model output is not deterministic"

    def test_output_normalized(self, onnx_session, dummy_input):
        """Test that output can be normalized properly."""
        input_name = onnx_session.get_inputs()[0].name
        output_name = onnx_session.get_outputs()[0].name

        features = onnx_session.run([output_name], {input_name: dummy_input})[0]

        # Normalize
        norm = np.linalg.norm(features, axis=-1, keepdims=True)
        normalized = features / norm

        # Check normalized output
        assert np.allclose(np.linalg.norm(normalized, axis=-1), 1.0, atol=1e-6), \
            "Normalized output norm is not 1.0"


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v'])
