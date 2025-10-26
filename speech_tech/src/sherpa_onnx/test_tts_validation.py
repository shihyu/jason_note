#!/usr/bin/env python3
"""
sherpa-onnx TTS 測試驗證腳本
測試 md 文件中的程式碼範例和 simple_tts_example.py
"""

import os
import sys
import wave
import traceback
from pathlib import Path

# 確保可以 import 上層目錄的模組
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunner:
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        # 測試輸出目錄改為 src/validation/tests/
        self.test_dir = Path(__file__).parent.parent / "validation" / "tests"
        # 確保測試目錄存在
        self.test_dir.mkdir(exist_ok=True)

    def print_header(self, text):
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60)

    def print_test(self, name):
        print(f"\n→ 測試: {name}")

    def print_success(self, message):
        print(f"  ✓ {message}")
        self.tests_passed += 1

    def print_failure(self, message):
        print(f"  ✗ {message}")
        self.tests_failed += 1

    def print_info(self, message):
        print(f"  ℹ {message}")

    def verify_audio_file(self, filepath, min_duration=0.5):
        """驗證音頻檔案"""
        try:
            # 確保 filepath 是字串
            filepath = str(filepath)

            if not os.path.exists(filepath):
                self.print_failure(f"檔案不存在: {filepath}")
                return False

            file_size = os.path.getsize(filepath)
            if file_size == 0:
                self.print_failure(f"檔案大小為 0: {filepath}")
                return False

            # 讀取 WAV 檔案資訊
            with wave.open(filepath, 'rb') as wf:
                channels = wf.getnchannels()
                sample_width = wf.getsampwidth()
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                duration = n_frames / framerate

                self.print_info(f"檔案: {filepath}")
                self.print_info(f"  大小: {file_size / 1024:.2f} KB")
                self.print_info(f"  採樣率: {framerate} Hz")
                self.print_info(f"  聲道數: {channels}")
                self.print_info(f"  位元深度: {sample_width * 8} bit")
                self.print_info(f"  長度: {duration:.2f} 秒")

                if duration < min_duration:
                    self.print_failure(f"音頻長度過短: {duration:.2f} < {min_duration}")
                    return False

                self.print_success(f"音頻檔案驗證通過: {filepath}")
                return True

        except Exception as e:
            self.print_failure(f"驗證音頻檔案失敗: {e}")
            return False

    def test_environment(self):
        """測試 1: 環境檢查"""
        self.print_header("測試 1: 環境檢查")

        # 檢查 sherpa-onnx
        self.print_test("檢查 sherpa-onnx 是否已安裝")
        try:
            import sherpa_onnx
            self.print_success(f"sherpa-onnx 已安裝 (版本: {sherpa_onnx.__version__})")
        except ImportError:
            self.print_failure("sherpa-onnx 未安裝")
            return False

        # 檢查 numpy
        self.print_test("檢查 numpy 是否已安裝")
        try:
            import numpy
            self.print_success(f"numpy 已安裝 (版本: {numpy.__version__})")
        except ImportError:
            self.print_failure("numpy 未安裝")
            return False

        return True

    def test_md_simple_tts(self):
        """測試 2: md 文件中的「最簡單的 TTS 測試」"""
        self.print_header("測試 2: md 文件中的程式碼範例")

        self.print_test("執行 md 文件中的 simple_tts_test.py 程式碼")

        try:
            import sherpa_onnx
            from pathlib import Path

            model_dir = Path(__file__).parent.parent.parent / "vits-piper-en_US-lessac-medium"

            print("  正在配置模型...")

            # 配置 TTS 模型（與修正後的 md 文件一致）
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

            if not tts_config.validate():
                raise ValueError("配置驗證失敗")

            print("  正在載入模型...")
            tts = sherpa_onnx.OfflineTts(tts_config)

            print("  正在生成語音...")
            audio = tts.generate("Hello! This is sherpa o n n x speaking.", sid=0, speed=1.0)

            output_file = self.test_dir / "hello_md.wav"
            sherpa_onnx.write_wave(str(output_file), audio.samples, audio.sample_rate)

            self.print_success("成功執行 md 程式碼範例")

            # 驗證生成的音頻檔案
            self.print_test("驗證生成的音頻檔案")
            return self.verify_audio_file(output_file)

        except Exception as e:
            self.print_failure(f"執行失敗: {e}")
            traceback.print_exc()
            return False

    def test_simple_tts_example(self):
        """測試 3: simple_tts_example.py"""
        self.print_header("測試 3: simple_tts_example.py")

        self.print_test("執行 simple_tts_example.py")

        try:
            from simple_tts_example import text_to_speech

            model_dir = str(Path(__file__).parent.parent.parent / "vits-piper-en_US-lessac-medium")

            # 測試範例 1
            output_file1 = self.test_dir / "hello.wav"
            text_to_speech(
                text="Hello! This is sherpa o n n x speaking.",
                output_file=str(output_file1),
                model_dir=model_dir
            )

            if not self.verify_audio_file(output_file1):
                return False

            # 測試範例 2
            output_file2 = self.test_dir / "welcome.wav"
            text_to_speech(
                text="Welcome to the world of offline text to speech synthesis.",
                output_file=str(output_file2),
                model_dir=model_dir,
                speed=0.9
            )

            if not self.verify_audio_file(output_file2):
                return False

            self.print_success("simple_tts_example.py 執行成功")
            return True

        except Exception as e:
            self.print_failure(f"執行失敗: {e}")
            traceback.print_exc()
            return False

    def test_api_correctness(self):
        """測試 4: API 使用正確性"""
        self.print_header("測試 4: API 使用正確性")

        self.print_test("檢查 OfflineTts API")

        try:
            import sherpa_onnx

            model_dir = Path(__file__).parent.parent.parent / "vits-piper-en_US-lessac-medium"

            # 檢查配置類是否存在
            if not hasattr(sherpa_onnx, 'OfflineTtsConfig'):
                self.print_failure("sherpa_onnx 沒有 OfflineTtsConfig 類")
                return False
            self.print_success("OfflineTtsConfig 類存在")

            if not hasattr(sherpa_onnx, 'OfflineTtsModelConfig'):
                self.print_failure("sherpa_onnx 沒有 OfflineTtsModelConfig 類")
                return False
            self.print_success("OfflineTtsModelConfig 類存在")

            if not hasattr(sherpa_onnx, 'OfflineTtsVitsModelConfig'):
                self.print_failure("sherpa_onnx 沒有 OfflineTtsVitsModelConfig 類")
                return False
            self.print_success("OfflineTtsVitsModelConfig 類存在")

            # 測試基本功能
            tts_config = sherpa_onnx.OfflineTtsConfig(
                model=sherpa_onnx.OfflineTtsModelConfig(
                    vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                        model=str(model_dir / "en_US-lessac-medium.onnx"),
                        lexicon="",
                        data_dir=str(model_dir / "espeak-ng-data"),
                        tokens=str(model_dir / "tokens.txt"),
                    ),
                    provider="cpu",
                    num_threads=1,
                ),
            )

            tts = sherpa_onnx.OfflineTts(tts_config)

            # 檢查 generate 方法
            if not hasattr(tts, 'generate'):
                self.print_failure("OfflineTts 沒有 generate 方法")
                return False
            self.print_success("OfflineTts.generate 方法存在")

            # 測試 generate
            audio = tts.generate("Test", sid=0, speed=1.0)

            # 檢查返回的 audio 物件
            if not hasattr(audio, 'sample_rate'):
                self.print_failure("audio 物件沒有 sample_rate 屬性")
                return False
            self.print_success("audio.sample_rate 屬性存在")

            if not hasattr(audio, 'samples'):
                self.print_failure("audio 物件沒有 samples 屬性")
                return False
            self.print_success("audio.samples 屬性存在")

            # 檢查 write_wave 函數
            if not hasattr(sherpa_onnx, 'write_wave'):
                self.print_failure("sherpa_onnx 沒有 write_wave 函數")
                return False
            self.print_success("sherpa_onnx.write_wave 函數存在")

            # 測試儲存
            test_file = self.test_dir / "api_test.wav"
            sherpa_onnx.write_wave(str(test_file), audio.samples, audio.sample_rate)

            if self.verify_audio_file(test_file):
                self.print_success("API 使用正確")
                return True
            else:
                return False

        except Exception as e:
            self.print_failure(f"API 測試失敗: {e}")
            traceback.print_exc()
            return False

    def run_all_tests(self):
        """執行所有測試"""
        self.print_header("sherpa-onnx TTS 測試驗證")

        # 執行測試
        self.test_environment()
        self.test_md_simple_tts()
        self.test_simple_tts_example()
        self.test_api_correctness()

        # 顯示總結
        self.print_header("測試總結")
        print(f"\n總測試數: {self.tests_passed + self.tests_failed}")
        print(f"通過: {self.tests_passed}")
        print(f"失敗: {self.tests_failed}")

        if self.tests_failed == 0:
            print("\n🎉 所有測試都通過了！")
            return True
        else:
            print(f"\n⚠️  有 {self.tests_failed} 個測試失敗")
            return False


def main():
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
