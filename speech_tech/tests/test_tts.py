"""
文字轉語音 (TTS) 模組測試
"""

import pytest
from pathlib import Path
import wave
import numpy as np


@pytest.mark.slow
def test_generate_speech_basic(fixtures_dir):
    """測試基本的文字轉語音功能"""
    from sherpa_onnx_demo.tts import TextToSpeech

    tts = TextToSpeech()
    text = "Hello! This is a test."
    output_file = fixtures_dir / "temp_test_basic.wav"

    result = tts.generate(text, output_path=str(output_file))

    # 驗證返回值
    assert result is not None
    assert "file_path" in result
    assert "sample_rate" in result
    assert "duration" in result

    # 驗證檔案存在
    assert Path(result["file_path"]).exists()

    # 驗證音頻格式
    with wave.open(result["file_path"], "rb") as wf:
        assert wf.getnchannels() == 1  # 單聲道
        assert wf.getsampwidth() == 2  # 16-bit
        assert wf.getframerate() == result["sample_rate"]  # 採樣率一致


@pytest.mark.slow
def test_generate_speech_with_speed(fixtures_dir):
    """測試調整語速功能"""
    from sherpa_onnx_demo.tts import TextToSpeech

    tts = TextToSpeech()
    text = "Speed test."

    # 測試不同語速
    output_normal = fixtures_dir / "temp_test_speed_normal.wav"
    output_fast = fixtures_dir / "temp_test_speed_fast.wav"

    result_normal = tts.generate(text, output_path=str(output_normal), speed=1.0)
    result_fast = tts.generate(text, output_path=str(output_fast), speed=1.5)

    # 驗證兩個檔案都存在
    assert Path(result_normal["file_path"]).exists()
    assert Path(result_fast["file_path"]).exists()

    # 快速語音應該比正常語音短
    assert result_fast["duration"] < result_normal["duration"]


@pytest.mark.slow
def test_generate_speech_empty_text(fixtures_dir):
    """測試空白文字處理"""
    from sherpa_onnx_demo.tts import TextToSpeech

    tts = TextToSpeech()
    output_file = fixtures_dir / "temp_test_empty.wav"

    with pytest.raises(ValueError, match="Text cannot be empty"):
        tts.generate("", output_path=str(output_file))


@pytest.mark.slow
def test_generate_speech_long_text(fixtures_dir):
    """測試較長文字處理"""
    from sherpa_onnx_demo.tts import TextToSpeech

    tts = TextToSpeech()
    text = "This is a longer text for testing. " * 10
    output_file = fixtures_dir / "temp_test_long.wav"

    result = tts.generate(text, output_path=str(output_file))

    assert result is not None
    assert Path(result["file_path"]).exists()
    # 長文字應該產生較長的音頻
    assert result["duration"] > 5.0  # 至少 5 秒


@pytest.mark.slow
def test_model_initialization():
    """測試模型初始化"""
    from sherpa_onnx_demo.tts import TextToSpeech

    # 測試預設初始化
    tts = TextToSpeech()
    assert tts is not None

    # 測試模型已載入
    assert tts.tts_engine is not None


def test_audio_format_conversion(fixtures_dir):
    """測試音頻格式轉換工具"""
    from sherpa_onnx_demo.tts import TextToSpeech

    # 建立測試用的音頻數據
    sample_rate = 22050
    duration = 1.0  # 1 秒
    samples = np.random.randn(int(sample_rate * duration)).astype(np.float32)

    # 測試轉換為 int16
    tts = TextToSpeech()
    samples_int16 = tts._convert_to_int16(samples)

    assert samples_int16.dtype == np.int16
    assert len(samples_int16) == len(samples)
    assert samples_int16.min() >= -32768
    assert samples_int16.max() <= 32767
