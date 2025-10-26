"""
語音轉文字 (Automatic Speech Recognition, ASR) 模組

使用 sherpa-onnx 提供離線 ASR 功能
模型: zipformer-bilingual-zh-en (中英雙語)
"""

import wave
import numpy as np
from pathlib import Path
from typing import Dict, Optional
from sherpa_onnx import OnlineRecognizer
from .utils import download_asr_model, ASR_MODELS, download_audio


class SpeechRecognizer:
    """語音轉文字類別"""

    def __init__(self, model_name: str = 'zipformer-bilingual-zh-en'):
        """
        初始化 ASR 引擎

        Args:
            model_name: 預訓練模型名稱，預設使用中英雙語模型

        第一次執行會下載模型（約 200MB），後續執行會使用緩存
        """
        self.model_name = model_name
        self.recognizer = None
        self._load_model()

    def _load_model(self):
        """載入預訓練模型"""
        try:
            print(f"正在載入 ASR 模型: {self.model_name}")
            print("（首次執行需要下載模型，請稍候...）")

            # 下載模型
            model_dir = download_asr_model(self.model_name)
            model_info = ASR_MODELS[self.model_name]

            # 創建識別器（使用 from_transducer 工廠方法）
            self.recognizer = OnlineRecognizer.from_transducer(
                encoder=str(model_dir / model_info['encoder']),
                decoder=str(model_dir / model_info['decoder']),
                joiner=str(model_dir / model_info['joiner']),
                tokens=str(model_dir / model_info['tokens']),
                num_threads=2,
                sample_rate=16000,
                feature_dim=80,
                enable_endpoint_detection=True,
                decoding_method="greedy_search"
            )

            print("✓ 模型載入完成")

        except Exception as e:
            raise RuntimeError(f"模型載入失敗: {e}")

    def recognize(self, audio_path: str) -> Dict:
        """
        識別語音檔案

        Args:
            audio_path: 音頻檔案路徑（WAV 格式）

        Returns:
            字典包含:
                - text: 識別出的文字
                - file_path: 音頻檔案路徑

        Raises:
            FileNotFoundError: 檔案不存在
            RuntimeError: 識別失敗
        """
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"音頻檔案不存在: {audio_path}")

        try:
            print(f"正在識別音頻: {audio_path}")

            # 讀取 WAV 檔案
            with wave.open(str(audio_path), 'rb') as wf:
                sample_rate = wf.getframerate()
                num_channels = wf.getnchannels()
                audio_data = wf.readframes(wf.getnframes())

            # 轉換為 float32 格式
            samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0

            # 處理雙聲道：轉為單聲道
            if num_channels == 2:
                samples = samples.reshape(-1, 2).mean(axis=1)

            # 創建識別流
            stream = self.recognizer.create_stream()

            # 輸入音頻數據
            stream.accept_waveform(sample_rate, samples)

            # 執行識別
            while self.recognizer.is_ready(stream):
                self.recognizer.decode_stream(stream)

            # 取得識別結果
            result_text = self.recognizer.get_result(stream)

            print(f"✓ 識別完成: {result_text[:100] if len(result_text) > 100 else result_text}")

            return {
                "text": result_text,
                "file_path": str(audio_path)
            }

        except Exception as e:
            raise RuntimeError(f"語音識別失敗: {e}")

    def recognize_from_url(self, url: str) -> Dict:
        """
        從網路 URL 下載音頻並識別

        Args:
            url: 音頻檔案 URL

        Returns:
            字典包含:
                - text: 識別出的文字
                - url: 原始 URL
                - file_path: 下載的檔案路徑

        Raises:
            RuntimeError: 下載或識別失敗
        """
        try:
            print(f"正在從 URL 下載音頻: {url}")

            # 下載音頻
            audio_path = download_audio(url)

            # 識別
            result = self.recognize(str(audio_path))

            # 添加 URL 資訊
            result["url"] = url

            return result

        except Exception as e:
            raise RuntimeError(f"從 URL 識別失敗: {e}")


# 便利函數
def recognize_speech(audio_path: str, model_name: str = 'zipformer-bilingual-zh-en') -> Dict:
    """
    便利函數：快速語音識別

    Args:
        audio_path: 音頻檔案路徑
        model_name: 模型名稱

    Returns:
        識別結果字典

    Example:
        >>> result = recognize_speech("audio.wav")
        >>> print(result["text"])
        Hello world
    """
    asr = SpeechRecognizer(model_name=model_name)
    return asr.recognize(audio_path)


def recognize_from_url(url: str, model_name: str = 'zipformer-bilingual-zh-en') -> Dict:
    """
    便利函數：從 URL 識別語音

    Args:
        url: 音頻檔案 URL
        model_name: 模型名稱

    Returns:
        識別結果字典

    Example:
        >>> result = recognize_from_url("https://example.com/audio.wav")
        >>> print(result["text"])
        Hello world
    """
    asr = SpeechRecognizer(model_name=model_name)
    return asr.recognize_from_url(url)
