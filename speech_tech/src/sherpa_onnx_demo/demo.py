#!/usr/bin/env python3
"""
sherpa-onnx 語音處理示範程式

展示功能：
1. 文字轉語音 (TTS)
2. 語音轉文字 (ASR)
3. 完整循環：文字 → 語音 → 文字
"""

import sys
from pathlib import Path

# 添加 src 到 Python 路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from sherpa_onnx_demo.tts import TextToSpeech
from sherpa_onnx_demo.asr import SpeechRecognizer


def print_header(title: str):
    """列印標題"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_tts():
    """示範文字轉語音"""
    print_header("示範 1: 文字轉語音 (TTS)")

    # 初始化 TTS
    print("\n[步驟 1] 初始化 TTS 引擎...")
    tts = TextToSpeech()

    # 測試文字
    text = "Hello! This is a demonstration of sherpa-onnx text to speech system."
    print(f"\n[步驟 2] 輸入文字:\n  {text}")

    # 生成語音
    output_file = Path("outputs/demo_tts.wav")
    print(f"\n[步驟 3] 生成語音...")
    result = tts.generate(text, output_path=str(output_file))

    print(f"\n✓ 成功！語音已儲存到: {result['file_path']}")
    print(f"  - 採樣率: {result['sample_rate']} Hz")
    print(f"  - 長度: {result['duration']:.2f} 秒")

    return result['file_path']


def demo_asr(audio_file: str = None):
    """示範語音轉文字"""
    print_header("示範 2: 語音轉文字 (ASR)")

    # 初始化 ASR
    print("\n[步驟 1] 初始化 ASR 引擎...")
    asr = SpeechRecognizer()

    if not audio_file:
        audio_file = "outputs/demo_tts.wav"

    # 識別語音
    print(f"\n[步驟 2] 識別音頻: {audio_file}")
    result = asr.recognize(audio_file)

    print(f"\n✓ 識別完成！")
    print(f"  識別結果: {result['text']}")

    return result['text']


def demo_full_cycle():
    """示範完整循環：文字 → 語音 → 文字"""
    print_header("示範 3: 完整循環 (TTS → ASR)")

    # 原始文字
    original_text = "This is a full cycle demonstration. Text to speech, then speech to text."
    print(f"\n[原始文字]\n  {original_text}")

    # 文字轉語音
    print("\n[步驟 1] 文字 → 語音...")
    tts = TextToSpeech()
    output_file = Path("outputs/demo_cycle.wav")
    tts_result = tts.generate(original_text, output_path=str(output_file))

    # 語音轉文字
    print(f"\n[步驟 2] 語音 → 文字...")
    asr = SpeechRecognizer()
    asr_result = asr.recognize(tts_result['file_path'])

    # 比較結果
    print(f"\n[比較結果]")
    print(f"  原始文字: {original_text}")
    print(f"  識別文字: {asr_result['text']}")

    # 計算相似度（簡單比較）
    original_words = set(original_text.lower().split())
    recognized_words = set(asr_result['text'].lower().split())
    if original_words:
        similarity = len(original_words & recognized_words) / len(original_words) * 100
        print(f"  相似度: {similarity:.1f}%")

    return asr_result['text']


def interactive_mode():
    """互動模式"""
    print_header("互動模式")
    print("\n選擇功能:")
    print("  1. 文字轉語音 (TTS)")
    print("  2. 語音轉文字 (ASR)")
    print("  3. 完整循環 (TTS → ASR)")
    print("  4. 全部執行")
    print("  0. 退出")

    choice = input("\n請選擇 (0-4): ").strip()

    if choice == "1":
        demo_tts()
    elif choice == "2":
        audio_file = input("請輸入音頻檔案路徑 (按 Enter 使用預設): ").strip()
        demo_asr(audio_file if audio_file else None)
    elif choice == "3":
        demo_full_cycle()
    elif choice == "4":
        demo_tts()
        demo_asr()
        demo_full_cycle()
    elif choice == "0":
        print("退出程式")
        return
    else:
        print("無效選擇")


def main():
    """主程式"""
    print("\n" + "=" * 60)
    print("  sherpa-onnx 語音處理示範程式")
    print("  功能: TTS (文字轉語音) + ASR (語音轉文字)")
    print("=" * 60)

    # 確保輸出目錄存在
    Path("outputs").mkdir(exist_ok=True)

    # 檢查命令列參數
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "tts":
            demo_tts()
        elif cmd == "asr":
            audio_file = sys.argv[2] if len(sys.argv) > 2 else None
            demo_asr(audio_file)
        elif cmd == "cycle":
            demo_full_cycle()
        elif cmd == "all":
            demo_tts()
            demo_asr()
            demo_full_cycle()
        else:
            print(f"未知指令: {cmd}")
            print("使用方式: python demo.py [tts|asr|cycle|all]")
    else:
        # 互動模式
        interactive_mode()

    print("\n" + "=" * 60)
    print("  示範完成！")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
