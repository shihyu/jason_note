#!/usr/bin/env python3
"""
中文文字轉語音工具
支援中文 TTS 模型
"""

import argparse
import sherpa_onnx
from pathlib import Path


# 專案根目錄（從 src/sherpa_onnx/ 向上兩層）
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 支援的中文模型配置
CHINESE_MODELS = {
    "aishell3": {
        "dir": "vits-zh-aishell3",
        "model": "vits-aishell3.onnx",
        "lexicon": "lexicon.txt",
        "tokens": "tokens.txt",
        "download": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-zh-aishell3.tar.bz2",
        "description": "中文多說話人模型 (66個說話人)",
    },
    "huayan": {
        "dir": "vits-piper-zh_CN-huayan-medium",
        "model": "zh_CN-huayan-medium.onnx",
        "lexicon": "",
        "tokens": "tokens.txt",
        "data_dir": "espeak-ng-data",
        "download": "https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-zh_CN-huayan-medium.tar.bz2",
        "description": "中文單說話人模型 (piper)",
    },
}


def detect_available_model():
    """自動偵測可用的中文模型"""
    for model_name, config in CHINESE_MODELS.items():
        model_dir = PROJECT_ROOT / config["dir"]
        if model_dir.exists():
            return model_name, model_dir
    return None, None


def text_to_speech(
    text: str,
    output_file: str = "output.wav",
    speed: float = 1.0,
    model_name: str = None,
    speaker_id: int = 0,
):
    """
    將中文文字轉換為語音檔案

    Args:
        text: 要轉換的中文文字
        output_file: 輸出檔案名稱
        speed: 語速 (0.5-2.0，1.0 為正常速度)
        model_name: 模型名稱 (aishell3 或 huayan)
        speaker_id: 說話人 ID (僅 aishell3 有效，0-65)
    """

    # 自動選擇模型
    if model_name is None:
        auto_model, model_dir = detect_available_model()
        if auto_model is None:
            print("❌ 錯誤：找不到任何中文 TTS 模型")
            print("\n請下載中文模型：")
            print("\n推薦模型：")
            for name, config in CHINESE_MODELS.items():
                print(f"\n{name}: {config['description']}")
                print(f"  wget {config['download']}")
                print(f"  tar -xjf {config['dir']}.tar.bz2")
            return False
        model_name = auto_model
        print(f"✓ 自動選擇模型: {model_name}")

    # 獲取模型配置
    if model_name not in CHINESE_MODELS:
        print(f"❌ 錯誤：不支援的模型 {model_name}")
        print(f"支援的模型: {', '.join(CHINESE_MODELS.keys())}")
        return False

    config = CHINESE_MODELS[model_name]
    model_dir = PROJECT_ROOT / config["dir"]

    if not model_dir.exists():
        print(f"❌ 錯誤：找不到模型目錄 {model_dir}")
        print(f"\n請下載 {model_name} 模型：")
        print(f"wget {config['download']}")
        print(f"tar -xjf {config['dir']}.tar.bz2")
        return False

    print("正在配置中文 TTS 模型...")
    print(f"模型: {config['description']}")

    # 配置 TTS 模型
    if model_name == "aishell3":
        # aishell3 配置
        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=str(model_dir / config["model"]),
                    lexicon=str(model_dir / config["lexicon"]),
                    tokens=str(model_dir / config["tokens"]),
                ),
                provider="cpu",
                debug=False,
                num_threads=1,
            ),
            rule_fsts="",
            max_num_sentences=1,
        )
    else:
        # piper 類型配置
        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model=str(model_dir / config["model"]),
                    lexicon="",
                    data_dir=str(model_dir / config.get("data_dir", "")),
                    tokens=str(model_dir / config["tokens"]),
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
    if model_name == "aishell3":
        print(f"說話人 ID: {speaker_id}")

    # 生成語音
    audio = tts.generate(text, sid=speaker_id, speed=speed)

    # 儲存為 WAV 檔案
    sherpa_onnx.write_wave(output_file, audio.samples, audio.sample_rate)

    print(f"\n✓ 中文語音已生成成功！")
    print(f"  檔案: {output_file}")
    print(f"  採樣率: {audio.sample_rate} Hz")
    print(f"  長度: {len(audio.samples)/audio.sample_rate:.2f} 秒")
    print(f"  檔案大小: {len(audio.samples) * 2 / 1024:.2f} KB")

    return True


def interactive_mode():
    """互動式模式"""
    print("=" * 60)
    print("中文文字轉語音工具 - 互動模式")
    print("=" * 60)

    # 偵測可用模型
    model_name, model_dir = detect_available_model()
    if model_name is None:
        print("\n❌ 錯誤：找不到任何中文 TTS 模型")
        print("\n請先下載中文模型：")
        for name, config in CHINESE_MODELS.items():
            print(f"\n{name}: {config['description']}")
            print(f"  wget {config['download']}")
            print(f"  tar -xjf {config['dir']}.tar.bz2")
        return

    print(f"\n✓ 使用模型: {CHINESE_MODELS[model_name]['description']}")

    # 輸入文字
    print("\n請輸入要轉換的中文文字：")
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

    # 說話人選擇 (僅 aishell3)
    speaker_id = 0
    if model_name == "aishell3":
        print("\n請輸入說話人 ID (0-65，預設: 0)：")
        speaker_input = input("> ").strip()
        try:
            speaker_id = int(speaker_input) if speaker_input else 0
            if speaker_id < 0 or speaker_id > 65:
                print("⚠️ 說話人 ID 超出範圍，使用預設值 0")
                speaker_id = 0
        except ValueError:
            print("⚠️ 無效的說話人 ID，使用預設值 0")
            speaker_id = 0

    # 執行轉換
    print("\n" + "=" * 60)
    text_to_speech(text, output_file, speed, model_name, speaker_id)


def main():
    parser = argparse.ArgumentParser(
        description="中文文字轉語音工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用範例:
  # 互動模式
  python text_to_speech_cn.py

  # 命令行模式
  python text_to_speech_cn.py -t "你好世界" -o hello.wav

  # 調整語速
  python text_to_speech_cn.py -t "快速朗讀" -o fast.wav -s 1.5

  # 指定說話人 (aishell3 模型)
  python text_to_speech_cn.py -t "不同的聲音" -o voice.wav --speaker 10

  # 從檔案讀取文字
  python text_to_speech_cn.py -f lyrics.txt -o song.wav
        """,
    )

    parser.add_argument(
        "-t", "--text",
        type=str,
        help="要轉換的中文文字內容"
    )

    parser.add_argument(
        "-f", "--file",
        type=str,
        help="從檔案讀取中文文字內容"
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

    parser.add_argument(
        "-m", "--model",
        type=str,
        choices=list(CHINESE_MODELS.keys()),
        help=f"指定模型 ({', '.join(CHINESE_MODELS.keys())})"
    )

    parser.add_argument(
        "--speaker",
        type=int,
        default=0,
        help="說話人 ID (僅 aishell3 有效，0-65，預設: 0)"
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
    text_to_speech(text, args.output, args.speed, args.model, args.speaker)


if __name__ == "__main__":
    main()
