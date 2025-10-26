#!/usr/bin/env python3
"""
正確的 sherpa-onnx TTS 使用範例
需要先下載模型文件
"""

import sherpa_onnx
from pathlib import Path


def text_to_speech_correct(
    text: str,
    output_file: str = "output.wav",
    model_dir: str = "vits-piper-en_US-lessac-medium",
    speed: float = 1.0,
):
    """
    使用正確的 API 將文字轉換為語音

    Args:
        text: 要轉換的文字
        output_file: 輸出的音頻檔案路徑
        model_dir: 模型目錄路徑
        speed: 語速 (1.0 為正常速度)
    """
    model_path = Path(model_dir)

    print("正在配置模型...")

    # 正確的配置方式
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
    from pathlib import Path

    # 測試輸出目錄（指向 src/validation/tests/）
    test_dir = Path(__file__).parent.parent / "validation" / "tests"
    test_dir.mkdir(exist_ok=True)

    # 模型目錄（從 src/examples/ 向上兩層到專案根目錄）
    model_dir = str(Path(__file__).parent.parent.parent / "vits-piper-en_US-lessac-medium")

    # 範例 1: 簡單的問候語
    text_to_speech_correct(
        text="Hello! This is sherpa o n n x speaking.",
        output_file=str(test_dir / "correct_hello.wav"),
        model_dir=model_dir,
    )

    # 範例 2: 更長的文字，調整語速
    text_to_speech_correct(
        text="Welcome to the world of offline text to speech synthesis. This is a demonstration of sherpa o n n x capabilities.",
        output_file=str(test_dir / "correct_welcome.wav"),
        model_dir=model_dir,
        speed=0.9,
    )

    print("\n所有語音檔案已生成完成!")
