"""
文字轉語音 (Text-to-Speech, TTS) 模組

使用 sherpa-onnx 提供離線 TTS 功能
模型: vits-piper-en_US-lessac-medium (英文)
"""

import wave
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from sherpa_onnx import (
    OfflineTts,
    OfflineTtsConfig,
    OfflineTtsModelConfig,
    OfflineTtsVitsModelConfig
)
from .utils import download_tts_model, TTS_MODELS


class TextToSpeech:
    """文字轉語音類別"""

    def __init__(self, model_name: str = 'vits-piper-en_US-lessac-medium'):
        """
        初始化 TTS 引擎

        Args:
            model_name: 預訓練模型名稱，預設使用英文模型

        第一次執行會下載模型（約 100MB），後續執行會使用緩存
        """
        self.model_name = model_name
        self.tts_engine = None
        self._load_model()

    def _load_model(self):
        """載入預訓練模型"""
        try:
            print(f"正在載入 TTS 模型: {self.model_name}")
            print("（首次執行需要下載模型，請稍候...）")

            # 下載模型
            model_dir = download_tts_model(self.model_name)
            model_info = TTS_MODELS[self.model_name]

            # 設定 VITS 模型配置
            vits_config = OfflineTtsVitsModelConfig(
                model=str(model_dir / model_info['model_file']),
                lexicon="",
                tokens=str(model_dir / model_info['tokens']),
                data_dir=str(model_dir / model_info['data_dir']),
                dict_dir=""
            )

            # 設定模型配置
            model_config = OfflineTtsModelConfig(
                vits=vits_config,
                num_threads=2,
                debug=False,
                provider="cpu"
            )

            # 設定 TTS 配置
            tts_config = OfflineTtsConfig(
                model=model_config,
                rule_fsts="",
                max_num_sentences=1
            )

            # 創建 TTS 引擎
            self.tts_engine = OfflineTts(tts_config)

            print("✓ 模型載入完成")

        except Exception as e:
            raise RuntimeError(f"模型載入失敗: {e}")

    def generate(
        self,
        text: str,
        output_path: str,
        speed: float = 1.0,
        sid: int = 0
    ) -> Dict:
        """
        生成語音檔案

        Args:
            text: 要轉換的文字內容
            output_path: 輸出 WAV 檔案路徑
            speed: 語速倍率（1.0 為正常速度，<1.0 較慢，>1.0 較快）
            sid: 說話人 ID（某些模型支援多個說話人）

        Returns:
            字典包含:
                - file_path: 生成的檔案路徑
                - sample_rate: 採樣率 (Hz)
                - duration: 音頻長度（秒）
                - text: 原始文字

        Raises:
            ValueError: 文字為空
            RuntimeError: 生成失敗
        """
        # 驗證輸入
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # 生成語音
            print(f"正在生成語音: {text[:50]}...")
            audio = self.tts_engine.generate(
                text,
                sid=sid,
                speed=speed
            )

            # 取得音頻資訊
            sample_rate = audio.sample_rate
            samples = audio.samples

            # 轉換為 numpy array（如果還不是）
            if not isinstance(samples, np.ndarray):
                samples = np.array(samples, dtype=np.float32)

            # 轉換為 int16 格式
            samples_int16 = self._convert_to_int16(samples)

            # 寫入 WAV 檔案
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with wave.open(str(output_path), 'w') as wf:
                wf.setnchannels(1)  # 單聲道
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(sample_rate)
                wf.writeframes(samples_int16.tobytes())

            # 計算音頻長度
            duration = len(samples) / sample_rate

            print(f"✓ 語音生成完成: {output_path}")
            print(f"  - 採樣率: {sample_rate} Hz")
            print(f"  - 長度: {duration:.2f} 秒")

            return {
                "file_path": str(output_path),
                "sample_rate": sample_rate,
                "duration": duration,
                "text": text
            }

        except Exception as e:
            raise RuntimeError(f"語音生成失敗: {e}")

    @staticmethod
    def _convert_to_int16(samples: np.ndarray) -> np.ndarray:
        """
        將浮點數音頻樣本轉換為 16-bit 整數格式

        Args:
            samples: 浮點數音頻樣本 (範圍 -1.0 到 1.0)

        Returns:
            16-bit 整數音頻樣本
        """
        # 將浮點數 [-1.0, 1.0] 縮放到 [-32768, 32767]
        samples_int16 = (samples * 32767).astype(np.int16)
        return samples_int16


# 便利函數
def text_to_speech(
    text: str,
    output_path: str,
    speed: float = 1.0,
    model_name: str = 'vits-piper-en_US-lessac-medium'
) -> Dict:
    """
    便利函數：快速文字轉語音

    Args:
        text: 要轉換的文字
        output_path: 輸出檔案路徑
        speed: 語速倍率
        model_name: 模型名稱

    Returns:
        生成結果字典

    Example:
        >>> result = text_to_speech("Hello world", "output.wav")
        >>> print(result["file_path"])
        output.wav
    """
    tts = TextToSpeech(model_name=model_name)
    return tts.generate(text, output_path, speed=speed)
