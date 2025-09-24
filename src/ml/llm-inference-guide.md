# LLM 推理框架完整指南 - RTX 3060 優化版

## 一、llama.cpp 與其他框架比較

### llama.cpp 主要特點

#### 優勢
- **極致的效率優化**：純 C/C++ 實現，無需 Python 依賴
- **低記憶體需求**：支援 4-bit、5-bit、8-bit 量化
- **跨平台支援**：Windows、Linux、macOS、Android、iOS
- **CPU 優化**：特別適合在沒有 GPU 的環境運行
- **輕量級**：編譯後的執行檔很小，部署簡單

#### 限制
- 主要針對 Llama 系列模型優化
- 功能相對單一，專注於推理

### 與其他主流框架比較

#### 1. vLLM
- **優勢**：PagedAttention 技術、高吞吐量、生產環境優化
- **劣勢**：需要 GPU、Python 依賴較重
- **適用場景**：大規模服務部署、需要高並發的 API 服務

#### 2. TensorRT-LLM (NVIDIA)
- **優勢**：NVIDIA GPU 上效能最佳、支援多 GPU 並行
- **劣勢**：僅限 NVIDIA GPU、設置複雜
- **適用場景**：企業級部署、需要極致 GPU 性能

#### 3. Ollama
- **優勢**：使用體驗極佳、一鍵安裝、內建模型管理
- **劣勢**：效能不如專門優化的框架
- **適用場景**：個人使用、快速原型開發

#### 4. Text Generation Inference (HuggingFace)
- **優勢**：與 HuggingFace 生態整合、支援多種模型
- **劣勢**：資源消耗較大
- **適用場景**：研究環境、需要靈活切換模型

#### 5. ExLlamaV2
- **優勢**：極致的量化優化、GPTQ 支援優秀
- **劣勢**：僅支援 Llama 架構、需要 GPU
- **適用場景**：消費級 GPU 運行大模型

#### 6. MLC-LLM
- **優勢**：跨平台（包括瀏覽器 WebGPU）、編譯優化
- **劣勢**：設置較複雜、社群相對較小
- **適用場景**：邊緣設備、瀏覽器部署

### 效能對比（13B 模型參考數據）
- **llama.cpp (CPU)**：15-30 tokens/秒
- **vLLM (GPU)**：100-200 tokens/秒  
- **TensorRT-LLM**：150-300 tokens/秒
- **Ollama**：20-100 tokens/秒（依硬體而定）
- **ExLlamaV2**：80-150 tokens/秒

### 選擇建議

**選擇 llama.cpp** 如果您：
- 沒有 GPU 或只有消費級顯卡
- 需要在邊緣設備或嵌入式系統運行
- 重視低資源消耗和部署簡單性
- 主要使用 Llama 系列模型

**選擇其他框架** 如果您：
- 有專業 GPU 且需要最高效能 → TensorRT-LLM
- 需要高並發 API 服務 → vLLM
- 想要最簡單的使用體驗 → Ollama
- 需要支援多種模型架構 → HuggingFace TGI

---

## 二、超越 llama.cpp 的選項

### CPU 環境下的競爭者

#### 1. llamafile (Mozilla)
- **優勢**：基於 llama.cpp 但更進一步優化
- **特色**：單一執行檔包含模型和推理引擎
- **效能**：與 llama.cpp 相當或略優
- **便利性**：勝過 llama.cpp

#### 2. candle (Rust)
- **優勢**：Rust 實現，記憶體安全性更好
- **效能**：某些情況下與 llama.cpp 相當
- **生態系統**：Rust 生態整合更好
- **成熟度**：仍在快速發展

#### 3. Intel Neural Compressor / OpenVINO
- **優勢**：在 Intel CPU 上可能有 20-40% 效能提升
- **限制**：主要針對 Intel 硬體優化
- **使用場景**：Intel 平台專屬優化

### CPU 效能比較（Llama2-13B 4-bit）
```
llama.cpp:           25-30 tokens/秒
llamafile:           25-32 tokens/秒  
candle:              20-28 tokens/秒
OpenVINO (Intel):    35-40 tokens/秒 (Intel CPU)
ONNX Runtime:        22-28 tokens/秒
```

### 特殊硬體平台的最佳選擇

#### Apple Silicon (M1/M2/M3)
- **MLX** (Apple 官方)：可能有 30-50% 效能優勢
- 充分利用 Apple 統一記憶體架構

#### Android 手機
- **MNN** (阿里巴巴)：移動端優化更好
- **NCNN** (騰訊)：在某些 Android 設備上更快

### 結論
綜合考慮效能、穩定性、易用性，llama.cpp 仍是 CPU 推理的最佳選擇，但特定硬體平台可能有更優選擇。

---

## 三、RTX 3060 12GB GPU 最佳方案

### 推薦順序

#### 🏆 最推薦：ExLlamaV2
```bash
# 安裝
pip install exllamav2

# 效能預期
# 7B 模型：約 80-120 tokens/秒
# 13B 模型：約 40-60 tokens/秒
```
**優勢**：
- 專為消費級 NVIDIA GPU 優化
- 支援優秀的 GPTQ 量化
- 12GB 可跑到 30B 模型（4-bit）
- 記憶體使用效率極高

#### 🥈 次推薦：Ollama（最簡單）
```bash
# 一行安裝
curl -fsSL https://ollama.ai/install.sh | sh

# 運行模型
ollama run llama3:8b
```
**優勢**：
- 使用超級簡單
- 自動偵測並使用 GPU
- 內建模型管理

#### 🥉 Text Generation WebUI (oobabooga)
```bash
# 圖形化介面，整合多種後端
git clone https://github.com/oobabooga/text-generation-webui
```
**優勢**：
- 支援多種載入方式
- 友善的網頁介面
- 適合測試比較

### RTX 3060 12GB 效能比較

| 框架 | Tokens/秒 | VRAM 使用 | 設置難度 |
|------|-----------|-----------|----------|
| **ExLlamaV2** | 45-60 | ~7GB | 中等 |
| **vLLM** | 40-55 | ~9GB | 較難 |
| **Ollama** | 35-50 | ~8GB | 極簡單 |
| **llama.cpp (CUDA)** | 30-40 | ~7.5GB | 簡單 |
| **Transformers** | 25-35 | ~10GB | 簡單 |

### 可運行的模型大小
- **70B 模型**：2-bit 量化（品質損失較大）
- **30B 模型**：4-bit 量化（品質不錯）
- **13B 模型**：8-bit 量化（品質極佳）
- **7B 模型**：FP16 全精度（最高品質）

### 具體安裝指南

#### ExLlamaV2 安裝（最佳效能）
```python
# 安裝
pip install exllamav2
pip install flash-attn  # 額外加速

# 使用範例
from exllamav2 import ExLlamaV2, ExLlamaV2Config
from exllamav2.generator import ExLlamaV2Generator

# 載入 GPTQ 量化模型
model_dir = "TheBloke/Llama-2-13B-GPTQ"
```

#### Ollama 安裝（最簡單）
```bash
# Windows：下載安裝程式
# Linux/Mac：
curl -fsSL https://ollama.ai/install.sh | sh

# 運行各種模型
ollama run llama3.2:3b      # 3B 模型
ollama run llama3:8b        # 8B 模型  
ollama run qwen2.5:14b      # 14B 模型
```

#### llama.cpp GPU 版本設置
```bash
# 編譯 CUDA 版本
cmake -B build -DLLAMA_CUDA=ON
cmake --build build --config Release

# 運行時指定 GPU 層數
./main -m model.gguf -ngl 35  # 35 層放 GPU
```

---

## 四、理解 Token 與效能

### 什麼是 Token？

Token 是語言模型處理文字的基本單位，介於字母和單字之間：

#### 範例
```
英文："Hello, how are you?" → 6 個 tokens
["Hello", ",", " how", " are", " you", "?"]

中文："你好嗎" → 3-5 個 tokens（依模型而定）
["你", "好", "嗎"] 或 ["你好", "嗎"]
```

#### Token 的一般規律
- **英文**：1 個 token ≈ 0.75 個單字（約 4 個字母）
- **中文**：1 個 token ≈ 0.5-1 個漢字
- **程式碼**：變數名、符號通常各算一個 token

### 不同模型的 Token 標準差異

#### 實例："我愛人工智慧"
```
GPT 系列：    5 tokens ["我", "愛", "人", "工", "智慧"]
LLaMA 系列：   6-7 tokens（對中文切分更細）
ChatGLM：     3-4 tokens ["我", "愛", "人工智慧"]
Qwen：       4 tokens（中文優化更好）
```

### 模型大小與速度關係

#### 7B 模型：80-120 tokens/秒
- 70 億參數
- 每個 token 需要經過 70 億次計算
- VRAM 佔用：約 4-6GB（4-bit 量化）

#### 13B 模型：40-60 tokens/秒
- 130 億參數（幾乎是 7B 的兩倍）
- 計算量加倍，速度約減半
- VRAM 佔用：約 7-9GB（4-bit 量化）

### Tokens/秒的實際體感

```
10 tokens/秒：  明顯卡頓，像打字機
30 tokens/秒：  流暢，像正常閱讀速度  
60 tokens/秒：  很快，像快速瀏覽
100+ tokens/秒： 極快，幾乎即時
```

#### 實際輸出速度
- **中文輸出**：30 tokens/秒 ≈ 每秒 15-30 個字
- **英文輸出**：30 tokens/秒 ≈ 每秒 20-25 個單字
- **一般對話**：30-40 tokens/秒 就很流暢了

### Token 計算工具

```python
# 使用 tiktoken（OpenAI）
import tiktoken
enc = tiktoken.get_encoding("cl100k_base")
tokens = enc.encode("Hello, world!")
print(f"Token 數：{len(tokens)}")  # 輸出：3

# 使用 transformers（HuggingFace）
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b")
tokens = tokenizer.encode("Hello, world!")
print(f"Token 數：{len(tokens)}")
```

### 為什麼要關心 Token？

1. **API 計費基準**
   - GPT-4：約 $0.03/1K tokens
   - Claude：約 $0.025/1K tokens

2. **上下文長度限制**
   - GPT-4：128K tokens 限制
   - Llama-2：4K tokens 限制
   - Claude：200K tokens 限制

3. **效能評估標準**
   - 同樣 30 tokens/秒，中文可能比英文慢

### RTX 3060 實際使用體驗

#### 7B 模型 @ 100 tokens/秒
- 英文：每秒約 75 個單字（極快）
- 中文：每秒約 50-100 個字（很快）
- 適合：即時對話、程式碼生成

#### 13B 模型 @ 50 tokens/秒
- 英文：每秒約 35-40 個單字（流暢）
- 中文：每秒約 25-50 個字（流暢）
- 適合：深度對話、專業寫作

---

## 五、實用建議總結

### 快速開始指南

1. **新手入門**：先試 **Ollama**，5 分鐘就能跑起來
2. **追求效能**：用 **ExLlamaV2**，充分發揮 3060 實力
3. **需要介面**：用 **Text Generation WebUI**
4. **已熟悉 llama.cpp**：編譯 CUDA 版本繼續使用

### 模型選擇建議

- **日常對話**：7B 模型足夠，速度快
- **專業任務**：13B 模型，品質更好
- **中文使用**：優先選擇 Qwen、ChatGLM（tokenizer 對中文更友善）

### 效能測試方法

```bash
# 大多數工具會顯示 tokens/秒
llama.cpp: 會顯示 "tok/s"
ollama: 運行時顯示速度統計
exllama: 提供詳細的效能指標
```

### RTX 3060 12GB 最佳實踐

1. 使用 4-bit 量化以支援更大模型
2. 優先選擇 GPU 優化框架（ExLlamaV2、vLLM）
3. 合理配置 VRAM 使用，預留 1-2GB 給系統
4. 定期更新驅動程式和 CUDA 版本

---

## 附錄：常用資源連結

### 模型下載
- [HuggingFace](https://huggingface.co/models)
- [TheBloke GPTQ Models](https://huggingface.co/TheBloke)
- [Ollama Model Library](https://ollama.ai/library)

### 框架官方文檔
- [llama.cpp](https://github.com/ggerganov/llama.cpp)
- [ExLlamaV2](https://github.com/turboderp/exllamav2)
- [vLLM](https://docs.vllm.ai/)
- [Ollama](https://ollama.ai/)

### 社群資源
- [LocalLLaMA Reddit](https://reddit.com/r/LocalLLaMA)
- [LLM 效能排行榜](https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard)

---

*最後更新：2025年1月*