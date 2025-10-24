# sherpa-onnx 完整指南

## 目錄
- [什麼是 sherpa-onnx](#什麼是-sherpa-onnx)
- [主要功能](#主要功能)
- [支援平台](#支援平台)
- [WebAssembly 應用](#webassembly-應用)
- [Python 快速驗證](#python-快速驗證)
- [完整測試腳本](#完整測試腳本)
- [常見問題](#常見問題)
- [更多資源](#更多資源)

---

## 什麼是 sherpa-onnx

**sherpa-onnx** 是一個開源的語音處理工具庫，使用 ONNX Runtime 和 Next-gen Kaldi 框架開發。

### 核心特色
- ✅ **完全離線運行**：不需要網路連線
- ✅ **跨平台支援**：支援 Windows、Linux、macOS、Android、iOS、嵌入式系統
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

## 支援平台

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

#### 4. 跨平台相容
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
   - 教育平台

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

## 方案一：最簡單的 TTS 測試（推薦）

只需 **5 行程式碼**！

### 程式碼：`simple_tts_test.py`

```python
#!/usr/bin/env python3
"""最簡單的 sherpa-onnx TTS 測試"""

from sherpa_onnx import OfflineTts

print("正在載入模型（第一次會下載，請稍候）...")
tts = OfflineTts.from_pretrained(model='vits-piper-en_US-lessac-medium')

print("正在生成語音...")
audio = tts.generate("Hello! This is sherpa o n n x speaking.", speed=1.0)

audio.save("hello.wav")
print("✓ 完成！語音已儲存到 hello.wav")
```

### 執行

```bash
python simple_tts_test.py
```

### 預期結果

- 第一次執行：下載模型（約 100-200 MB），需要 2-5 分鐘
- 生成 `hello.wav` 檔案
- 用任何播放器播放該檔案，應該能聽到英文語音

---

## 方案二：語音識別測試

### 程式碼：`simple_asr_test.py`

```python
#!/usr/bin/env python3
"""簡單的語音識別測試"""

from sherpa_onnx import OnlineRecognizer
import wave
import numpy as np

print("正在載入模型（支援中英文）...")
recognizer = OnlineRecognizer.from_pretrained(
    'csukuangfj/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20'
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

### 程式碼：`test_sherpa_onnx.py`

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
        from sherpa_onnx import OfflineTts
        
        tts = OfflineTts.from_pretrained(
            model='vits-piper-en_US-lessac-medium',
            rule_fsts='',
            max_num_sentences=1
        )
        
        text = "Hello! This is a test of sherpa-onnx text to speech."
        print(f"正在生成語音: {text}")
        
        audio = tts.generate(text, speed=1.0, speaker_id=0)
        
        output_file = "output_tts.wav"
        sample_rate = audio.sample_rate
        samples = audio.samples
        samples_int16 = (samples * 32767).astype(np.int16)
        
        with wave.open(output_file, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples_int16.tobytes())
        
        print(f"✓ 成功生成語音檔案: {output_file}")
        print(f"  採樣率: {sample_rate} Hz")
        print(f"  長度: {len(samples)/sample_rate:.2f} 秒")
        
        return output_file
        
    except Exception as e:
        print(f"✗ TTS 測試失敗: {e}")
        return None


def test_asr(audio_file=None):
    """測試語音識別"""
    print("\n=== 測試語音識別（ASR）===")
    
    try:
        from sherpa_onnx import OnlineRecognizer
        
        recognizer = OnlineRecognizer.from_pretrained(
            model='csukuangfj/sherpa-onnx-streaming-zipformer-bilingual-zh-en-2023-02-20'
        )
        
        if audio_file and os.path.exists(audio_file):
            print(f"正在識別音頻: {audio_file}")
            
            with wave.open(audio_file, 'rb') as wf:
                sample_rate = wf.getframerate()
                num_channels = wf.getnchannels()
                audio_data = wf.readframes(wf.getnframes())
                samples = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                
                if num_channels == 2:
                    samples = samples.reshape(-1, 2).mean(axis=1)
            
            stream = recognizer.create_stream()
            stream.accept_waveform(sample_rate, samples)
            
            while recognizer.is_ready(stream):
                recognizer.decode_stream(stream)
            
            result = recognizer.get_result(stream)
            print(f"✓ 識別結果: {result}")
        else:
            print("ℹ 未提供音頻檔案，跳過 ASR 測試")
        
    except Exception as e:
        print(f"✗ ASR 測試失敗: {e}")


def main():
    print("=" * 60)
    print("sherpa-onnx Python 完整測試")
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
    
    # 測試 ASR
    if tts_output:
        test_asr(tts_output)
    
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

## 快速開始總結

### 1. 安裝
```bash
pip install sherpa-onnx numpy
```

### 2. 最簡單測試（TTS）
```bash
python simple_tts_test.py
```

### 3. 完整測試
```bash
python test_sherpa_onnx.py
```

### 4. 線上體驗（無需安裝）
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
- ✅ 跨平台應用開發

---

**最後更新**: 2025-10-24  
**文檔版本**: 1.0  
**sherpa-onnx 版本**: 1.12.14+

如有問題或建議，歡迎到 GitHub 提出 Issue 或參與討論！
