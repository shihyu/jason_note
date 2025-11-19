# AI 模型訓練完整指南：從零開始到實戰

## 目錄
1. [開源模型選擇](#開源模型選擇)
2. [訓練方法：LoRA 技術](#訓練方法lora-技術)
3. [數據收集策略](#數據收集策略)
4. [硬體需求與解決方案](#硬體需求與解決方案)
5. [為什麼選擇 NVIDIA GPU](#為什麼選擇-nvidia-gpu)
6. [CPU vs GPU 原理解析](#cpu-vs-gpu-原理解析)
7. [實戰程式碼範例](#實戰程式碼範例)

---

## 開源模型選擇

### 基礎語言模型
- **Llama 3.1/3.2** (Meta): 效能優異，有 8B、70B 等版本
- **Mistral/Mixtral**: 輕量但效果好，適合財務分析
- **Qwen 2.5** (阿里): 中文支援佳，適閤中文財報
- **Yi-1.5** (零一萬物): 中英雙語能力強
- **Phi-2** (Microsoft): 2.7B 參數，適合初學者
- **TinyLlama**: 1.1B 參數，訓練快速

### 財務專用模型
- **FinGPT**: 專門為金融領域設計的開源模型
- **BloombergGPT** (部分開源): 金融領域預訓練
- **FinBERT**: 較小但專注於金融情感分析

### 模型選擇建議
| 模型規模 | 參數量 | VRAM需求 | 適用場景 |
|---------|--------|----------|----------|
| 小型 | < 3B | 4-8GB | 學習測試、特定任務 |
| 中型 | 3-13B | 8-24GB | 通用助手、商業應用 |
| 大型 | 13-70B | 24-80GB | 複雜推理、專業應用 |

---

## 訓練方法：LoRA 技術

### 什麼是 LoRA？
LoRA (Low-Rank Adaptation) 是一種**通用的微調技術**，不綁定特定模型：
- 在原始模型旁邊添加小的可訓練參數
- 凍結原始模型權重，只訓練新增的部分
- 大幅減少需要訓練的參數量（通常只需 1-10%）

### LoRA 的優勢
1. **省資源**: 只需訓練 1-10% 參數
2. **可疊加**: 可以訓練多個 LoRA 用於不同任務
3. **易分享**: LoRA 檔案小（幾十MB），方便分享
4. **可切換**: 同一個基礎模型可以載入不同 LoRA

### LoRA 配置範例
```python
from peft import LoraConfig, get_peft_model

# 通用 LoRA 配置
lora_config = LoraConfig(
    r=16,  # LoRA rank（可調整：4, 8, 16, 32, 64）
    lora_alpha=32,  # 縮放參數
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM",
)

# 應用到任何模型
model = get_peft_model(model, lora_config)
```

---

## 數據收集策略

### 推薦訓練領域（按難易度）

#### 1. 程式碼助手 ⭐⭐⭐⭐⭐
**最容易收集數據，實用性極高**
- CodeAlpaca: 20K 程式指令數據
- CodeSearchNet: 2M+ 函數和文檔
- The Stack: 3TB 開源程式碼
- GitHub 公開專案

#### 2. 客服/FAQ 機器人 ⭐⭐⭐⭐⭐
**公開數據多，商業價值高**
- Amazon 產品 QA: 100萬+ QA對
- SQuAD: 問答數據集
- 各公司公開的 FAQ 頁面

#### 3. 文章摘要生成器 ⭐⭐⭐⭐
**新聞網站多，數據豐富**
- CNN/DailyMail: 30萬+ 新聞摘要
- XSum: BBC 新聞摘要
- 中文：THUCNews、新浪新聞

#### 4. 財報分析數據源
```python
# SEC EDGAR (美股)
import sec_edgar_downloader
downloader = sec_edgar_downloader.Downloader()
downloader.get("10-K", "AAPL")

# 財經 API
import yfinance as yf
ticker = yf.Ticker("TSLA")
financials = ticker.financials

# 臺灣公開資訊觀測站
# https://mops.twse.com.tw/
```

### 數據格式範例
```json
{
  "instruction": "分析這份財報的營收成長",
  "input": "公司2023年營收...",
  "output": "根據財報顯示..."
}
```

---

## 硬體需求與解決方案

### 硬體配置建議

#### 最低配置
- GPU: RTX 3090 (24GB VRAM)
- 可訓練 7B 參數模型（使用 LoRA）

#### 建議配置
- GPU: A100 40GB 或 RTX 4090
- 可訓練 13B-30B 模型

### 沒有顯卡的解決方案

#### 1. Google Colab（最推薦）
| 方案 | 價格 | GPU | 適用場景 |
|------|------|-----|----------|
| 免費版 | $0 | T4 (15GB) | 學習測試 |
| Pro | $10/月 | V100/A100 | 常常訓練 |
| Pro+ | $50/月 | A100 48小時不斷 | 專業使用 |

#### 2. 雲端租用
- Vast.ai: $0.2-0.5/hr (RTX 3090)
- RunPod: $0.3-0.7/hr
- Lambda Labs: $0.5-1.5/hr

#### 3. CPU 訓練策略（AMD 8745HS）
```python
# CPU 優化設定
import torch
torch.set_num_threads(16)  # 使用所有線程

# 使用量化技術
from transformers import BitsAndBytesConfig
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
)

# 使用超小模型
models = {
    "microsoft/phi-1_5": "1.3B",
    "TinyLlama/TinyLlama-1.1B": "1.1B",
    "facebook/opt-350m": "350M",
}
```

### 訓練時間對比
| 硬體 | 模型規模 | 1000筆資料訓練時間 |
|------|---------|-------------------|
| CPU (8745HS) | 350M | 5-8 小時 |
| CPU (8745HS) | 2.7B + LoRA | 10-15 小時 |
| GPU (RTX 3090) | 7B + LoRA | 30 分鐘 |
| GPU (A100) | 13B | 45 分鐘 |

---

## 為什麼選擇 NVIDIA GPU

### NVIDIA 壟斷的原因

#### 1. 生態系統優勢
- **CUDA**: 2007年發布，領先 AMD ROCm 9年
- **軟體支援**: 所有 AI 框架原生支援
- **開發工具**: 完整的除錯、優化工具鏈

#### 2. 硬體優勢
- **Tensor Cores**: 專門的 AI 運算單元
- **記憶體頻寬**: H100 達 3.35 TB/s
- **NVLink**: GPU 間高速通訊

### NVIDIA vs AMD 對比

| 項目 | NVIDIA | AMD |
|------|--------|-----|
| 軟體生態 | ⭐⭐⭐⭐⭐ 成熟完整 | ⭐⭐ 發展中 |
| 安裝難度 | ⭐⭐⭐⭐⭐ 簡單 | ⭐ 複雜 |
| 框架支援 | ⭐⭐⭐⭐⭐ 全面 | ⭐⭐ 有限 |
| 性能表現 | ⭐⭐⭐⭐⭐ 最佳 | ⭐⭐⭐ 可用 |
| 性價比 | ⭐⭐⭐ 較貴 | ⭐⭐⭐⭐ 便宜 |

### 實際差異
```bash
# NVIDIA 安裝（簡單）
pip install torch torchvision torchaudio

# AMD 安裝（複雜）
# 1. 確認 GPU 支援
# 2. 安裝特定 Linux 版本
# 3. 安裝 ROCm
# 4. 安裝特殊版本 PyTorch
pip install torch --index-url https://download.pytorch.org/whl/rocm5.7
```

---

## CPU vs GPU 原理解析

### 架構差異

#### CPU：高級餐廳主廚
- **核心數**: 8-16 個強大核心
- **特點**: 複雜邏輯、依序處理
- **適合**: 通用計算、邏輯判斷

#### GPU：流水線工廠
- **核心數**: 數千個簡單核心
- **特點**: 並行處理、同時運算
- **適合**: 大量重複計算

### AI 訓練的本質：矩陣運算

```python
# 神經網路 = 大量矩陣乘法
def neural_network_layer(input_data, weights, bias):
    output = np.dot(input_data, weights) + bias  # 核心運算
    return output

# 實際規模
input_data = (1024, 768)   # 批次資料
weights = (768, 2048)       # 權重矩陣
# 需要：1024 × 768 × 2048 = 16億次運算！
```

### 性能對比

| 運算類型 | CPU (8核) | GPU (RTX 4090) | 速度差異 |
|---------|-----------|----------------|----------|
| 串行邏輯 | ⭐⭐⭐⭐⭐ | ⭐ | CPU 勝 |
| 矩陣運算 | ⭐ | ⭐⭐⭐⭐⭐ | GPU 快 100x |
| AI 訓練 | 50 小時 | 30 分鐘 | GPU 快 100x |

### 為什麼 GPU 快？
1. **並行計算**: 16,384 個 CUDA 核心 vs 8 個 CPU 核心
2. **記憶體頻寬**: 1008 GB/s vs 90 GB/s
3. **專用硬體**: Tensor Cores 專為 AI 設計

### GPU 適合 AI 訓練的核心原因

1. **大規模並行** - 數千個核心同時工作
2. **矩陣運算優化** - AI 的本質就是矩陣運算
3. **高記憶體頻寬** - 快速移動大量資料
4. **專用硬體** - Tensor Cores 專為 AI 設計
5. **能源效率** - 同樣運算量，GPU 更省電

**簡單比喻：**
- **CPU = 8個博士**（很聰明，但人少）
- **GPU = 10000個小學生**（簡單，但人超多）
- **AI訓練 = 大量簡單重複運算**（適合10000個小學生一起做）

這就是為什麼訓練 AI 一定要用 GPU 的原因！

---

## 實戰程式碼範例

### 完整訓練流程（Colab 版）

```python
# 1. 環境設置
!pip install transformers datasets accelerate peft bitsandbytes

# 2. 載入模型和配置 LoRA
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
import torch

# 選擇基礎模型
model_name = "microsoft/phi-2"
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype=torch.float16,
    device_map="cuda"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 配置 LoRA
peft_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["Wqkv", "out_proj", "fc1", "fc2"],
    lora_dropout=0.1,
)

model = get_peft_model(model, peft_config)
print(f"可訓練參數: {model.num_parameters(only_trainable=True):,}")

# 3. 準備數據
from datasets import load_dataset

# 財報分析數據格式
def prepare_dataset(examples):
    inputs = [f"分析任務：{inst}\n財報內容：{inp}\n" 
              for inst, inp in zip(examples["instruction"], examples["input"])]
    model_inputs = tokenizer(inputs, max_length=2048, truncation=True)
    labels = tokenizer(examples["output"], max_length=2048, truncation=True)
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

dataset = load_dataset("your_dataset")
dataset = dataset.map(prepare_dataset, batched=True)

# 4. 訓練
from transformers import TrainingArguments, Trainer

training_args = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    warmup_steps=100,
    logging_steps=10,
    save_strategy="epoch",
    fp16=True,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
    tokenizer=tokenizer,
)

trainer.train()

# 5. 保存和測試
model.save_pretrained("./my-finance-lora")

# 測試
prompt = "請分析這家公司2023年第四季的獲利能力..."
inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_length=500)
response = tokenizer.decode(outputs[0])
print(response)
```

### 本地部署（載入訓練好的模型）

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 載入基礎模型
base_model = AutoModelForCausalLM.from_pretrained(
    "microsoft/phi-2",
    device_map="cpu",  # 本地 CPU 使用
    torch_dtype=torch.float32
)

# 載入 LoRA 權重
model = PeftModel.from_pretrained(
    base_model,
    "./my-finance-lora"
)

# 使用模型
def analyze_financial_report(report_text):
    prompt = f"分析以下財報：\n{report_text}\n分析結果："
    inputs = tokenizer(prompt, return_tensors="pt")
    outputs = model.generate(**inputs, max_length=500)
    return tokenizer.decode(outputs[0])
```

---

## 學習路線圖

### Week 1-2: 基礎學習
- 瞭解 Transformer 架構
- 熟悉 Hugging Face 生態系統
- 在 Colab 跑通第一個模型

### Week 3-4: 數據準備
- 收集領域數據
- 學習數據清理和格式化
- 建立訓練數據集

### Week 5-6: 模型訓練
- 理解 LoRA 原理
- 調整超參數
- 訓練第一個客製化模型

### Week 7-8: 優化部署
- 模型量化和優化
- 部署到生產環境
- 性能測試和改進

---

## 重要提醒

1. **先從小模型開始**：Phi-2、TinyLlama 適合初學者
2. **善用免費資源**：Google Colab、Kaggle Notebooks
3. **LoRA 是關鍵**：大幅降低訓練成本
4. **數據品質 > 數量**：高品質數據比大量數據重要
5. **迭代改進**：先跑通流程，再逐步優化

---

## 資源連結

### 模型下載
- [Hugging Face Models](https://huggingface.co/models)
- [ModelScope (中文模型)](https://modelscope.cn/)

### 數據集
- [Hugging Face Datasets](https://huggingface.co/datasets)
- [Kaggle Datasets](https://www.kaggle.com/datasets)

### 學習資源
- [Hugging Face Course](https://huggingface.co/course)
- [Fast.ai Course](https://www.fast.ai/)
- [Andrej Karpathy's Videos](https://www.youtube.com/@AndrejKarpathy)

### 社群
- [r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
- [Hugging Face Forums](https://discuss.huggingface.co/)

---

## 總結

訓練 AI 模型不再是大公司的專利。透過：
- 開源模型（Llama、Qwen、Phi）
- LoRA 微調技術
- 免費 GPU 資源（Colab）
- 良好的數據策略

任何人都可以訓練出專屬的 AI 模型。關鍵是**從小開始、逐步成長、持續學習**。

祝你的 AI 訓練之旅順利！🚀