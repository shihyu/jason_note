#!/usr/bin/env python3
"""
簡單的 sherpa-onnx 文字轉語音範例
將文字轉換為語音檔案

注意：需要先下載模型文件
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-medium.tar.bz2
tar -xjf vits-piper-en_US-lessac-medium.tar.bz2
"""

import sherpa_onnx
from pathlib import Path

# 計算專案根目錄路徑（從 src/examples/ 向上兩層）
PROJECT_ROOT = Path(__file__).parent.parent.parent


def text_to_speech(
    text: str,
    output_file: str = "output.wav",
    model_dir: str = None,
    speed: float = 1.0,
):
    """
    將文字轉換為語音檔案

    Args:
        text: 要轉換的文字
        output_file: 輸出的音頻檔案路徑
        model_dir: 模型目錄路徑（如果為 None，則使用專案根目錄的模型）
        speed: 語速 (1.0 為正常速度, > 1.0 更快, < 1.0 更慢)
    """
    # 如果未指定模型目錄，使用專案根目錄的模型
    if model_dir is None:
        model_path = PROJECT_ROOT / "vits-piper-en_US-lessac-medium"
    else:
        model_path = Path(model_dir)

    print("正在配置模型...")

    # 配置 TTS 模型
    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=str(model_path / "en_US-lessac-medium.onnx"),
                lexicon="",
                data_dir=str(model_path / "espeak-ng-data"),
                tokens=str(model_path / "tokens.txt"),
            ),
            provider="cpu",
            debug=False,
            num_threads=1,
        ),
        rule_fsts="",
        max_num_sentences=1,
    )

    # 驗證配置
    if not tts_config.validate():
        raise ValueError("配置驗證失敗！請檢查模型路徑")

    print("正在載入模型...")
    tts = sherpa_onnx.OfflineTts(tts_config)

    print(f"正在生成語音: {text}")

    # 生成語音
    audio = tts.generate(text, sid=0, speed=speed)

    # 儲存為 WAV 檔案
    sherpa_onnx.write_wave(output_file, audio.samples, audio.sample_rate)

    print(f"✓ 完成！語音已儲存到 {output_file}")
    print(f"  採樣率: {audio.sample_rate} Hz")
    print(f"  長度: {len(audio.samples)/audio.sample_rate:.2f} 秒")


if __name__ == "__main__":
    # 範例 1: 簡單的問候語
    text_to_speech(
        text="Hello! This is sherpa o n n x speaking. 游刃有餘",
        output_file="hello.wav"
    )

    # 範例 2: 更長的文字，調整語速
    text_to_speech(
        text="Welcome to the world of offline text to speech synthesis. This is a demonstration of sherpa o n n x capabilities.",
        output_file="welcome.wav",
        speed=0.9  # 稍微慢一點
    )

    print("\n所有語音檔案已生成完成!")
