#!/usr/bin/env python3
"""
文字轉語音工具
支援命令行輸入或互動式使用
"""

import argparse
import sherpa_onnx
from pathlib import Path


# 專案根目錄（從 src/sherpa_onnx/ 向上兩層）
PROJECT_ROOT = Path(__file__).parent.parent.parent


def text_to_speech(
    text: str,
    output_file: str = "output.wav",
    speed: float = 1.0,
    model_dir: Path = None,
):
    """
    將文字轉換為語音檔案

    Args:
        text: 要轉換的文字
        output_file: 輸出檔案名稱
        speed: 語速 (0.5-2.0，1.0 為正常速度)
        model_dir: 模型目錄路徑
    """
    if model_dir is None:
        model_dir = PROJECT_ROOT / "vits-piper-en_US-lessac-medium"

    if not model_dir.exists():
        print(f"❌ 錯誤：找不到模型目錄 {model_dir}")
        print("\n請先下載模型：")
        print("wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-medium.tar.bz2")
        print("tar -xjf vits-piper-en_US-lessac-medium.tar.bz2")
        return False

    print("正在配置模型...")

    # 配置 TTS 模型
    tts_config = sherpa_onnx.OfflineTtsConfig(
        model=sherpa_onnx.OfflineTtsModelConfig(
            vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                model=str(model_dir / "en_US-lessac-medium.onnx"),
                lexicon="",
                data_dir=str(model_dir / "espeak-ng-data"),
                tokens=str(model_dir / "tokens.txt"),
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
        print("❌ 配置驗證失敗！請檢查模型路徑")
        return False

    print("正在載入模型...")
    tts = sherpa_onnx.OfflineTts(tts_config)

    print(f"正在生成語音...")
    print(f"文字內容: {text}")

    # 生成語音
    audio = tts.generate(text, sid=0, speed=speed)

    # 儲存為 WAV 檔案
    sherpa_onnx.write_wave(output_file, audio.samples, audio.sample_rate)

    print(f"\n✓ 語音已生成成功！")
    print(f"  檔案: {output_file}")
    print(f"  採樣率: {audio.sample_rate} Hz")
    print(f"  長度: {len(audio.samples)/audio.sample_rate:.2f} 秒")
    print(f"  檔案大小: {len(audio.samples) * 2 / 1024:.2f} KB")

    return True


def interactive_mode():
    """互動式模式"""
    print("=" * 60)
    print("文字轉語音工具 - 互動模式")
    print("=" * 60)

    # 輸入文字
    print("\n請輸入要轉換的文字：")
    text = input("> ").strip()

    if not text:
        print("❌ 錯誤：文字不能為空")
        return

    # 輸入檔案名稱
    print("\n請輸入輸出檔案名稱 (預設: output.wav)：")
    output_file = input("> ").strip()
    if not output_file:
        output_file = "output.wav"

    # 確保副檔名為 .wav
    if not output_file.endswith(".wav"):
        output_file += ".wav"

    # 輸入語速
    print("\n請輸入語速 (0.5-2.0，預設: 1.0)：")
    speed_input = input("> ").strip()
    try:
        speed = float(speed_input) if speed_input else 1.0
        if speed < 0.5 or speed > 2.0:
            print("⚠️ 語速超出範圍，使用預設值 1.0")
            speed = 1.0
    except ValueError:
        print("⚠️ 無效的語速，使用預設值 1.0")
        speed = 1.0

    # 執行轉換
    print("\n" + "=" * 60)
    text_to_speech(text, output_file, speed)


def main():
    parser = argparse.ArgumentParser(
        description="文字轉語音工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 互動模式
  python text_to_speech.py

  # 命令行模式
  python text_to_speech.py -t "你好世界" -o hello.wav

  # 調整語速
  python text_to_speech.py -t "快速朗讀" -o fast.wav -s 1.5

  # 從檔案讀取文字
  python text_to_speech.py -f input.txt -o output.wav
        """,
    )

    parser.add_argument(
        "-t", "--text",
        type=str,
        help="要轉換的文字內容"
    )

    parser.add_argument(
        "-f", "--file",
        type=str,
        help="從檔案讀取文字內容"
    )

    parser.add_argument(
        "-o", "--output",
        type=str,
        default="output.wav",
        help="輸出檔案名稱 (預設: output.wav)"
    )

    parser.add_argument(
        "-s", "--speed",
        type=float,
        default=1.0,
        help="語速 (0.5-2.0，預設: 1.0)"
    )

    args = parser.parse_args()

    # 決定文字來源
    text = None

    if args.file:
        # 從檔案讀取
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                text = f.read().strip()
            print(f"✓ 從檔案讀取文字: {args.file}")
        except FileNotFoundError:
            print(f"❌ 錯誤：找不到檔案 {args.file}")
            return
        except Exception as e:
            print(f"❌ 讀取檔案時發生錯誤: {e}")
            return

    elif args.text:
        # 從命令行參數讀取
        text = args.text

    else:
        # 沒有提供參數，進入互動模式
        interactive_mode()
        return

    # 驗證語速範圍
    if args.speed < 0.5 or args.speed > 2.0:
        print("⚠️ 警告：語速應在 0.5-2.0 之間，使用預設值 1.0")
        args.speed = 1.0

    # 確保輸出檔名有 .wav 副檔名
    if not args.output.endswith(".wav"):
        args.output += ".wav"

    # 執行轉換
    print("=" * 60)
    text_to_speech(text, args.output, args.speed)


if __name__ == "__main__":
    main()
