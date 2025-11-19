# sherpa-onnx 完整指南

## 目錄
- [什麼是 sherpa-onnx](#什麼是-sherpa-onnx)
- [主要功能](#主要功能)
- [支援平臺](#支援平臺)
- [WebAssembly 應用](#webassembly-應用)
- [Python 快速驗證](#python-快速驗證)
- [完整測試腳本](#完整測試腳本)
- [中文 TTS 工具](#中文-tts-工具) ⭐
- [常見問題](#常見問題)
- [更多資源](#更多資源)

---

## 什麼是 sherpa-onnx

**sherpa-onnx** 是一個開源的語音處理工具庫，使用 ONNX Runtime 和 Next-gen Kaldi 框架開發。

### 核心特色
- ✅ **完全離線運行**：不需要網路連線
- ✅ **跨平臺支援**：支援 Windows、Linux、macOS、Android、iOS、嵌入式系統
- ✅ **多語言支援**：中文、英文、日文、韓文、粵語、俄語等
- ✅ **多種編程語言**：支援 12 種編程語言（Python、C++、Java、JavaScript、Swift 等）
- ✅ **高性能**：使用 ONNX Runtime 優化，執行效率高

---

## 主要功能

### 1. 語音轉文字（Speech-to-Text, ASR）
- 即時語音識別
- 支援串流（streaming）和批次（batch）處理
- 多語言模型可選

### 2. 文字轉語音（Text-to-Speech, TTS）
- 自然流暢的語音合成
- 可調整語速、音調
- 多種說話人（speaker）選擇

### 3. 說話人分離（Speaker Diarization）
- 識別「誰在何時說話」
- 適用於會議記錄、訪談分析

### 4. 語音活動檢測（VAD）
- 自動偵測語音片段
- 過濾靜音和噪音

### 5. 語音增強（Speech Enhancement）
- 改善語音品質
- 降噪處理

### 6. 聲源分離（Source Separation）
- 分離混合音頻中的不同聲音來源

---

## 支援平臺

### 作業系統
- Windows
- Linux
- macOS
- Android
- iOS
- HarmonyOS

### 嵌入式系統
- Raspberry Pi
- RISC-V
- RK3588
- Jetson (NVIDIA)

### 編程語言
Python、C++、Java、JavaScript、TypeScript、C#、Go、Swift、Kotlin、Dart、Rust、C

---

## WebAssembly 應用

### 什麼是 WebAssembly 版本？

sherpa-onnx 的 WebAssembly 版本讓語音處理功能可以**直接在網頁瀏覽器中執行**，無需後端伺服器。

### 主要優勢

#### 1. 完全在瀏覽器運行
- 使用 Emscripten 編譯器將 C++ 程式碼編譯成 WebAssembly
- 接近原生應用的性能表現
- 無需安裝額外軟體

#### 2. 隱私保護
- 所有處理都在客戶端完成
- 語音資料不會傳送到伺服器
- 適合處理敏感資訊

#### 3. 離線運作
- 模型載入後可完全離線使用
- 不受網路狀況影響

#### 4. 跨平臺相容
- 只需現代瀏覽器即可執行
- 支援桌面和行動裝置

### WebAssembly 應用場景

1. **網頁語音識別**
   - 線上會議字幕
   - 語音筆記工具
   - 客服系統

2. **網頁文字轉語音**
   - 電子書朗讀
   - 學習輔助工具
   - 無障礙功能

3. **語音互動網頁**
   - 語音助手
   - 語音遊戲
   - 教育平臺

4. **隱私敏感應用**
   - 醫療記錄語音輸入
   - 法律文件聽寫
   - 私人日記語音記錄

### 線上體驗（Hugging Face Spaces）

你可以直接在瀏覽器中試用：

- **英文語音識別**: https://huggingface.co/spaces/k2-fsa/web-assembly-asr-sherpa-onnx-en
- **中英雙語識別**: https://huggingface.co/spaces/k2-fsa/web-assembly-asr-sherpa-onnx-zh-en
- **中文、粵語、英文**: https://huggingface.co/spaces/k2-fsa/web-assembly-asr-sherpa-onnx-zh-cantonese-en-paraformer
- **英文文字轉語音**: https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en

---

## Python 快速驗證

### 前置準備

**無需麥克風！** 我們使用音頻檔案來測試。

### 安裝

```bash
pip install sherpa-onnx numpy
```

---

## 方案一：使用 VITS 模型的 TTS 測試（推薦）

### 步驟 1: 下載模型

sherpa-onnx 需要手動下載模型文件（不會自動下載）。

```bash
# 下載 VITS 模型
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-en_US-lessac-medium.tar.bz2

# 解壓縮
tar -xjf vits-piper-en_US-lessac-medium.tar.bz2
```

### 步驟 2: 程式碼：`src/sherpa_onnx/simple_tts_example.py`

```python
#!/usr/bin/env python3
"""sherpa-onnx TTS 測試範例"""

import sherpa_onnx

print("正在配置模型...")

# 配置 TTS 模型
tts_config = sherpa_onnx.OfflineTtsConfig(
    model=sherpa_onnx.OfflineTtsModelConfig(
        vits=sherpa_onnx.OfflineTtsVitsModelConfig(
            model="vits-piper-en_US-lessac-medium/en_US-lessac-medium.onnx",
            lexicon="",
            data_dir="vits-piper-en_US-lessac-medium/espeak-ng-data",
            tokens="vits-piper-en_US-lessac-medium/tokens.txt",
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

print("正在生成語音...")
audio = tts.generate("Hello! This is sherpa o n n x speaking.", sid=0, speed=1.0)

# 儲存為 WAV 檔案
sherpa_onnx.write_wave("hello.wav", audio.samples, audio.sample_rate)

print("✓ 完成！語音已儲存到 hello.wav")
print(f"  採樣率: {audio.sample_rate} Hz")
print(f"  長度: {len(audio.samples)/audio.sample_rate:.2f} 秒")
```

### 執行

```bash
python src/sherpa_onnx/simple_tts_example.py
```

### 預期結果

- 生成 `hello.wav` 檔案（約 2-3 秒的語音）
- 採樣率：22050 Hz
- 用任何播放器播放該檔案，應該能聽到英文語音

---

## 方案二：語音識別測試

**注意**：ASR（語音識別）需要額外下載和配置模型，不支持自動下載。

詳細的 ASR 配置請參考官方文檔：https://k2-fsa.github.io/sherpa/onnx/pretrained_models/index.html

### 簡化範例：使用 from_transducer

```python
#!/usr/bin/env python3
"""簡單的語音識別測試（需要先下載模型）"""

from sherpa_onnx import OnlineRecognizer
import wave
import numpy as np

# 注意：這個範例假設你已經下載了對應的模型文件
# 下載說明：https://k2-fsa.github.io/sherpa/onnx/pretrained_models/online-transducer/index.html

print("正在載入模型...")
recognizer = OnlineRecognizer.from_transducer(
    encoder="模型路徑/encoder.onnx",
    decoder="模型路徑/decoder.onnx",
    joiner="模型路徑/joiner.onnx",
    tokens="模型路徑/tokens.txt",
)

# 讀取音頻檔案（需要準備一個 WAV 檔案）
audio_file = "test.wav"  # 替換成你的音頻檔案

print(f"正在讀取音頻: {audio_file}")
with wave.open(audio_file, 'rb') as wf:
    sample_rate = wf.getframerate()
    audio_data = wf.readframes(wf.getnframes())
    samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
    
    # 如果是雙聲道，轉為單聲道
    if wf.getnchannels() == 2:
        samples = samples.reshape(-1, 2).mean(axis=1)

print("正在識別...")
stream = recognizer.create_stream()
stream.accept_waveform(sample_rate, samples)

while recognizer.is_ready(stream):
    recognizer.decode_stream(stream)

result = recognizer.get_result(stream)
print(f"✓ 識別結果: {result}")
```

### 測試音頻下載

如果沒有自己的音頻檔案：

```bash
# 中文測試音頻
wget https://github.com/k2-fsa/sherpa-onnx/raw/master/sherpa-onnx/python/tests/test_data/zh.wav

# 英文測試音頻
wget https://github.com/k2-fsa/sherpa-onnx/raw/master/sherpa-onnx/python/tests/test_data/en.wav
```

---

## 完整測試腳本

### 程式碼：`src/sherpa_onnx/test_tts_validation.py`

```python
#!/usr/bin/env python3
"""
sherpa-onnx 完整測試腳本
測試 TTS 和 ASR 功能
"""

import os
import sys
import wave
import numpy as np

def test_tts():
    """測試文字轉語音"""
    print("\n=== 測試文字轉語音（TTS）===")

    try:
        import sherpa_onnx

        # 配置 TTS 模型
        tts_config = sherpa_onnx.OfflineTtsConfig(
            model=sherpa_onnx.OfflineTtsModelConfig(
                vits=sherpa_onnx.OfflineTtsVitsModelConfig(
                    model="vits-piper-en_US-lessac-medium/en_US-lessac-medium.onnx",
                    lexicon="",
                    data_dir="vits-piper-en_US-lessac-medium/espeak-ng-data",
                    tokens="vits-piper-en_US-lessac-medium/tokens.txt",
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

        tts = sherpa_onnx.OfflineTts(tts_config)

        text = "Hello! This is a test of sherpa-onnx text to speech."
        print(f"正在生成語音: {text}")

        audio = tts.generate(text, sid=0, speed=1.0)

        output_file = "output_tts.wav"
        sherpa_onnx.write_wave(output_file, audio.samples, audio.sample_rate)

        print(f"✓ 成功生成語音檔案: {output_file}")
        print(f"  採樣率: {audio.sample_rate} Hz")
        print(f"  長度: {len(audio.samples)/audio.sample_rate:.2f} 秒")

        return output_file

    except Exception as e:
        print(f"✗ TTS 測試失敗: {e}")
        return None


def test_audio_file_info(audio_file):
    """顯示音頻檔案資訊"""
    print("\n=== 音頻檔案資訊 ===")

    try:
        if not os.path.exists(audio_file):
            print(f"✗ 檔案不存在: {audio_file}")
            return

        file_size = os.path.getsize(audio_file)
        print(f"檔案: {audio_file}")
        print(f"大小: {file_size / 1024:.2f} KB")

        with wave.open(audio_file, 'rb') as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            duration = n_frames / framerate

            print(f"採樣率: {framerate} Hz")
            print(f"聲道數: {channels}")
            print(f"位元深度: {sample_width * 8} bit")
            print(f"長度: {duration:.2f} 秒")

        print("✓ 音頻檔案驗證通過")

    except Exception as e:
        print(f"✗ 讀取音頻檔案失敗: {e}")


def main():
    print("=" * 60)
    print("sherpa-onnx TTS 測試")
    print("=" * 60)

    try:
        import sherpa_onnx
        print(f"✓ sherpa-onnx 已安裝 (版本: {sherpa_onnx.__version__})")
    except ImportError:
        print("✗ sherpa-onnx 未安裝")
        print("\n請執行: pip install sherpa-onnx")
        sys.exit(1)

    # 測試 TTS
    tts_output = test_tts()

    # 顯示音頻檔案資訊
    if tts_output:
        test_audio_file_info(tts_output)

    print("\n" + "=" * 60)
    print("測試完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
```

---

## 常見問題

### Q1: 第一次執行很慢？
**A:** 是的，第一次需要下載模型檔案（100-300 MB），之後就會很快。

### Q2: 模型下載到哪裡？
**A:** 預設位置：
- Linux/macOS: `~/.cache/sherpa-onnx/` 或 `~/.local/share/sherpa-onnx/`
- Windows: `C:\Users\用戶名\.cache\sherpa-onnx\`

### Q3: 可以完全離線使用嗎？
**A:** 可以！模型下載後就完全不需要網路連線。

### Q4: 支援哪些語言？
**A:** 
- 中文（普通話、粵語、各種方言）
- 英文
- 日文
- 韓文
- 俄文
- 西班牙文
- 德文
- 法文
- 等多種語言

### Q5: 音頻格式有什麼要求？
**A:** 最佳格式：
- 採樣率：16 kHz
- 位元深度：16-bit PCM
- 聲道：單聲道（mono）
- 格式：WAV

但系統會自動處理其他格式的轉換。

### Q6: 需要 GPU 嗎？
**A:** 不需要！CPU 就能跑，但如果有 GPU 會更快。支援 CUDA、NNAPI、CoreML 等加速。

### Q7: 可以用在商業項目嗎？
**A:** 請查看具體模型的授權。sherpa-onnx 本身是 Apache 2.0 授權，但不同的預訓練模型可能有不同的授權條款。

### Q8: 識別準確率如何？
**A:** 取決於：
- 選用的模型
- 音頻品質
- 語言/口音
- 背景噪音

一般來說，清晰的錄音可以達到 90%+ 的準確率。

### Q9: 可以自訂模型嗎？
**A:** 可以！你可以：
- 使用自己訓練的模型
- Fine-tune 現有模型
- 轉換其他框架的模型為 ONNX 格式

### Q10: 如何選擇模型？
**A:** 考慮因素：
- **語言**：選擇支援目標語言的模型
- **大小**：小模型執行快但準確率較低
- **用途**：串流（streaming）vs 批次（batch）
- **裝置**：嵌入式系統選擇小模型

---

## 實際應用案例

### 1. 智能音箱
- 小愛音箱自定義喚醒詞
- 離線語音控制

### 2. 語音助手
- Windows/Linux 桌面語音助手
- 類 Jarvis 系統

### 3. 會議記錄
- 自動語音轉文字
- 說話人識別

### 4. 教育應用
- 語言學習工具
- 發音評測
- 聽力練習

### 5. 無障礙輔助
- 視障者閱讀輔助
- 聽障者語音轉字幕
- 智能眼鏡應用

### 6. 遊戲應用
- 語音聊天轉文字
- 遊戲內語音指令

### 7. IoT 設備
- ESP32 語音控制
- Raspberry Pi 智能裝置
- 機器人語音互動

### 8. 醫療應用
- 病歷語音輸入
- 醫療記錄轉錄

---

## 更多資源

### 官方資源
- **GitHub**: https://github.com/k2-fsa/sherpa-onnx
- **文檔**: https://k2-fsa.github.io/sherpa/
- **發布版本**: https://github.com/k2-fsa/sherpa-onnx/releases

### 預訓練模型
- **ASR 模型**: https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models
- **TTS 模型**: https://github.com/k2-fsa/sherpa-onnx/releases/tag/tts-models
- **模型庫**: https://huggingface.co/csukuangfj

### 範例程式碼
- **Python 範例**: https://github.com/k2-fsa/sherpa-onnx/tree/master/python-api-examples
- **Android 範例**: https://github.com/k2-fsa/sherpa-onnx/tree/master/android
- **iOS 範例**: https://github.com/k2-fsa/sherpa-onnx/tree/master/ios
- **WebAssembly 範例**: https://github.com/k2-fsa/sherpa-onnx/tree/master/wasm

### 社群
- **討論區**: https://github.com/k2-fsa/sherpa-onnx/discussions
- **問題回報**: https://github.com/k2-fsa/sherpa-onnx/issues

### 相關項目
- **Next-gen Kaldi**: https://github.com/k2-fsa
- **Icefall**: https://github.com/k2-fsa/icefall
- **ONNX Runtime**: https://onnxruntime.ai/

---

## 中文 TTS 工具

### 簡介

專案提供了易用的中文文字轉語音工具，支援自動模型偵測和多種使用方式。

### 下載中文模型

```bash
# 推薦：中文單說話人模型 (huayan)
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-zh_CN-huayan-medium.tar.bz2
tar -xjf vits-piper-zh_CN-huayan-medium.tar.bz2

# 或：中文多說話人模型 (aishell3，支援 66 個不同聲音)
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-zh-aishell3.tar.bz2
tar -xjf vits-zh-aishell3.tar.bz2
```

### 使用方式

#### 方法 1: 命令行模式（推薦）

```bash
# 基本使用
python src/sherpa_onnx/text_to_speech_cn.py -t "你好世界" -o hello.wav

# 調整語速
python src/sherpa_onnx/text_to_speech_cn.py -t "快速朗讀" -o fast.wav -s 1.5

# 慢速朗讀
python src/sherpa_onnx/text_to_speech_cn.py -t "慢速朗讀" -o slow.wav -s 0.8
```

#### 方法 2: 從檔案讀取

```bash
# 將歌詞或長文本存入檔案
echo "本來應該從從容容遊刃有餘" > lyrics.txt

# 轉換為語音
python src/sherpa_onnx/text_to_speech_cn.py -f lyrics.txt -o song.wav
```

#### 方法 3: 互動模式

```bash
# 啟動互動式介面
python src/sherpa_onnx/text_to_speech_cn.py

# 按提示輸入：
# 1. 文字內容
# 2. 輸出檔案名稱
# 3. 語速設定
# 4. 說話人選擇（僅 aishell3 模型）
```

#### 方法 4: 多說話人模型（aishell3）

```bash
# 使用不同的說話人 (0-65)
python src/sherpa_onnx/text_to_speech_cn.py -t "測試不同聲音" -o voice1.wav --speaker 0
python src/sherpa_onnx/text_to_speech_cn.py -t "測試不同聲音" -o voice2.wav --speaker 10
python src/sherpa_onnx/text_to_speech_cn.py -t "測試不同聲音" -o voice3.wav --speaker 30
```

### 完整參數說明

```bash
python src/sherpa_onnx/text_to_speech_cn.py --help

參數:
  -t, --text TEXT        要轉換的中文文字內容
  -f, --file FILE        從檔案讀取中文文字內容
  -o, --output FILE      輸出檔案名稱 (預設: output.wav)
  -s, --speed SPEED      語速 (0.5-2.0，預設: 1.0)
  -m, --model MODEL      指定模型 (aishell3 或 huayan)
  --speaker ID           說話人 ID (僅 aishell3 有效，0-65，預設: 0)
```

### 功能特色

- ✅ **自動模型偵測**：無需手動指定，自動找到可用的中文模型
- ✅ **多種輸入方式**：命令行、檔案、互動式
- ✅ **語速調整**：支援 0.5-2.0 倍速調整
- ✅ **多說話人**：aishell3 模型支援 66 種不同聲音
- ✅ **完全離線**：無需網路連線
- ✅ **高品質**：清晰自然的中文發音

### 工具檔案位置

```
src/sherpa_onnx/
├── text_to_speech_cn.py        # 中文 TTS 工具 ⭐
├── text_to_speech.py           # 英文 TTS 工具
├── simple_tts_example.py       # 簡單範例
├── correct_tts_example.py      # 正確 API 範例
└── test_tts_validation.py      # 完整測試腳本
```

---

## 快速開始總結

### 1. 安裝
```bash
pip install sherpa-onnx numpy
```

### 2. 最簡單測試（TTS）
```bash
python src/sherpa_onnx/simple_tts_example.py
```

### 3. 中文 TTS 工具（推薦）⭐
```bash
# 先下載中文模型
wget https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/vits-piper-zh_CN-huayan-medium.tar.bz2
tar -xjf vits-piper-zh_CN-huayan-medium.tar.bz2

# 使用中文 TTS
python src/sherpa_onnx/text_to_speech_cn.py -t "你好世界" -o hello.wav
```

### 4. 完整測試
```bash
python src/sherpa_onnx/test_tts_validation.py
```

### 5. 線上體驗（無需安裝）
訪問 Hugging Face Spaces 直接在瀏覽器中試用。

---

## 結語

sherpa-onnx 是一個功能強大、易於使用、完全離線的語音處理工具庫。無論你是：
- 想要為應用添加語音功能的開發者
- 需要離線語音處理的項目
- 研究語音技術的學生
- 想要打造智能助手的愛好者

sherpa-onnx 都是一個很好的選擇！

**特別適合**：
- ✅ 注重隱私的應用
- ✅ 需要離線運行的場景
- ✅ 嵌入式和 IoT 設備
- ✅ 跨平臺應用開發

---

**最後更新**: 2025-10-24  
**文檔版本**: 1.0  
**sherpa-onnx 版本**: 1.12.14+

如有問題或建議，歡迎到 GitHub 提出 Issue 或參與討論！
