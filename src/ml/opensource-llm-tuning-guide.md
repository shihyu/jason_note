# 開源 LLM 調校完整指南

## 📚 目錄
1. [主流開源模型](#主流開源模型)
2. [調校方法詳解](#調校方法詳解)
3. [工具與框架](#工具與框架)
4. [實戰案例](#實戰案例)
5. [最佳實踐](#最佳實踐)

## 主流開源模型

### 🔥 頂級模型系列

#### Meta Llama 系列
- **Llama 3.1** (8B, 70B, 405B)
  - 支援 128K context
  - 多語言能力強
  - 適合：通用對話、程式碼生成、推理任務

#### Mistral 系列
- **Mistral 7B / Mixtral 8x7B**
  - 效能/參數比極高
  - 32K context window
  - 適合：高效推論、邊緣部署

#### Qwen 系列（阿里）
- **Qwen2.5** (0.5B-72B)
  - 中文能力頂尖
  - 支援 128K context
  - 適合：中文應用、多模態任務

#### DeepSeek 系列
- **DeepSeek-V3**
  - MoE 架構，671B 總參數
  - 極強推理能力
  - 適合：數學、程式碼、複雜推理

### 🎯 特化模型

#### 程式碼特化
- **CodeLlama** - Meta 的程式碼模型
- **DeepSeek-Coder** - 程式碼生成專精
- **StarCoder2** - BigCode 專案
- **CodeQwen** - 阿里程式碼模型

#### 數學推理
- **WizardMath** - 數學增強版
- **MetaMath** - 數學推理優化
- **MAmmoTH** - 數學問題解決

#### 角色扮演/創作
- **Yi-34B** - 創意寫作能力強
- **Nous-Hermes** - 指令遵循優秀
- **OpenChat** - 對話優化

## 調校方法詳解

### 1. 提示工程 (Prompt Engineering)

#### 基礎技巧
```python
# System Prompt 設定
system_prompt = """
你是一位專業的技術顧問，擅長解釋複雜概念。
請用簡潔清晰的方式回答，並提供實例。
"""

# Few-shot Learning
few_shot_examples = """
問題：什麼是 API？
答案：API 是程式之間溝通的介面，像餐廳菜單一樣，
讓你知道可以點什麼菜（呼叫什麼功能）。

問題：{user_question}
答案：
"""

# Chain-of-Thought
cot_prompt = """
讓我們一步步思考這個問題：
1. 首先分析問題的核心需求
2. 列出可能的解決方案
3. 評估每個方案的優缺點
4. 給出最佳建議
"""
```

#### 進階技巧
- **Self-Consistency** - 多次生成後投票
- **Tree-of-Thoughts** - 探索多個思考路徑
- **ReAct** - 推理與行動交替
- **Constitutional AI** - 自我批評與改進

### 2. 微調技術 (Fine-tuning)

#### 全參數微調
```bash
# 使用 transformers 進行全參數微調
python train.py \
    --model_name "meta-llama/Llama-3-8b" \
    --dataset "custom_dataset" \
    --learning_rate 2e-5 \
    --num_epochs 3 \
    --batch_size 4
```

#### LoRA (Low-Rank Adaptation)
```python
# LoRA 配置範例
lora_config = LoraConfig(
    r=16,                # rank
    lora_alpha=32,       # scaling
    target_modules=["q_proj", "v_proj"],
    lora_dropout=0.1,
)

# 優點：
# - 只需訓練 0.1-1% 參數
# - 可切換多個 LoRA adapter
# - 訓練速度快 10-100 倍
```

#### QLoRA (Quantized LoRA)
```python
# 4-bit 量化 + LoRA
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
)

# 優點：
# - 記憶體需求降低 75%
# - 單張 3090 可微調 65B 模型
```

### 3. RAG (檢索增強生成)

#### 基礎 RAG 架構
```python
# 1. 文檔切分與向量化
from langchain.text_splitter import RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

# 2. 建立向量資料庫
from chromadb import Client
vectordb = Client()
collection = vectordb.create_collection("knowledge_base")

# 3. 檢索與生成
def rag_query(question):
    # 檢索相關文檔
    docs = collection.query(question, n_results=5)
    # 組合 context
    context = "\n".join(docs)
    # 生成答案
    prompt = f"根據以下資訊回答問題：\n{context}\n問題：{question}"
    return llm.generate(prompt)
```

#### 進階 RAG 技術
- **Hybrid Search** - 結合向量與關鍵字檢索
- **Re-ranking** - 二次排序提升準確度
- **Query Expansion** - 查詢擴展
- **Contextual Compression** - 上下文壓縮

### 4. 推論優化

#### 量化技術
```python
# INT8 量化
model = AutoModelForCausalLM.from_pretrained(
    "model_name",
    load_in_8bit=True,
    device_map="auto"
)

# GPTQ 4-bit 量化
model = AutoGPTQForCausalLM.from_quantized(
    "model_name-gptq-4bit",
    use_safetensors=True,
)

# AWQ 量化
model = AutoAWQForCausalLM.from_quantized(
    "model_name-awq",
    fuse_layers=True,
)
```

#### 推論加速
- **vLLM** - PagedAttention 優化
- **TensorRT-LLM** - NVIDIA GPU 優化
- **llama.cpp** - CPU/Metal 優化
- **ExLlamaV2** - 極致量化推論

## 工具與框架

### 訓練框架
| 框架 | 特點 | 適用場景 |
|------|------|----------|
| **Axolotl** | 配置簡單、支援多種微調方法 | 快速實驗 |
| **LLaMA-Factory** | 中文友好、GUI 介面 | 新手入門 |
| **TRL (Transformers RL)** | HuggingFace 官方、RLHF 支援 | 生產部署 |
| **Unsloth** | 速度快 2-5 倍、記憶體優化 | 資源受限 |
| **LitGPT** | Lightning 生態、模組化設計 | 研究開發 |

### 部署工具
| 工具 | 優勢 | 支援模型 |
|------|------|----------|
| **Ollama** | 一鍵部署、本地運行 | 主流開源模型 |
| **Text Generation Inference** | HuggingFace 官方、生產級 | 所有 HF 模型 |
| **LocalAI** | OpenAI API 相容 | 多種模型 |
| **FastChat** | 多模型支援、WebUI | 主流模型 |

## 實戰案例

### 案例 1：客服機器人
```python
# 步驟 1: 準備客服對話資料
dataset = load_dataset("customer_service_logs")

# 步驟 2: LoRA 微調
model = AutoModelForCausalLM.from_pretrained("Qwen2.5-7B")
peft_model = get_peft_model(model, lora_config)
trainer = SFTTrainer(
    model=peft_model,
    train_dataset=dataset,
    dataset_text_field="conversations",
)

# 步驟 3: 建立產品知識 RAG
product_docs = load_documents("product_manuals/")
vectorstore = FAISS.from_documents(product_docs)

# 步驟 4: 部署整合系統
def customer_service_bot(query):
    # RAG 檢索
    context = vectorstore.similarity_search(query)
    # 生成回應
    response = peft_model.generate(
        prompt=format_prompt(query, context)
    )
    return response
```

### 案例 2：程式碼助手
```python
# 使用 DeepSeek-Coder + 公司程式碼庫
# 1. 收集公司程式碼與文檔
code_dataset = collect_company_code()

# 2. 微調程式碼模型
base_model = "deepseek-coder-6.7b"
fine_tune_on_company_style(base_model, code_dataset)

# 3. 整合 IDE
vscode_extension = create_copilot_extension(fine_tuned_model)
```

### 案例 3：領域專家系統
```python
# 醫療領域為例
# 1. 收集醫學文獻
medical_papers = crawl_pubmed()

# 2. 持續預訓練
continue_pretrain("Llama-3-8B", medical_papers)

# 3. 指令微調
medical_qa = load_dataset("medical_qa")
instruction_tuning(model, medical_qa)

# 4. 加入安全防護
add_safety_guardrails(model, medical_guidelines)
```

## 最佳實踐

### ✅ DO - 建議做法

1. **資料品質優先**
   - 高品質資料 > 大量資料
   - 清理與去重很重要
   - 保持資料多樣性

2. **漸進式優化**
   - 先 Prompt → 再 RAG → 最後微調
   - 從小模型開始測試
   - 建立評估基準

3. **混合方案**
   - RAG + 微調結合使用
   - 多個 LoRA 按需切換
   - 大小模型協作

4. **監控與評估**
   - 建立評估資料集
   - 追蹤關鍵指標
   - A/B 測試驗證

### ❌ DON'T - 避免踩坑

1. **過度微調**
   - 避免 catastrophic forgetting
   - 不要用太小的資料集
   - 保留模型通用能力

2. **忽視成本**
   - 計算訓練 vs 推論成本
   - 考慮維護複雜度
   - 評估 ROI

3. **安全問題**
   - 不要忽視有害輸出
   - 注意隱私資料洩露
   - 建立內容過濾機制

## 資源連結

### 📖 學習資源
- [HuggingFace 課程](https://huggingface.co/course)
- [LLM University by Cohere](https://docs.cohere.com/docs/llmu)
- [Fast.ai Practical Deep Learning](https://course.fast.ai/)

### 🛠️ 實用工具
- [LangChain](https://langchain.com/) - LLM 應用框架
- [LlamaIndex](https://www.llamaindex.ai/) - RAG 專門框架
- [Weights & Biases](https://wandb.ai/) - 實驗追蹤

### 💬 社群資源
- [LocalLLaMA Reddit](https://reddit.com/r/LocalLLaMA)
- [HuggingFace Discord](https://discord.gg/huggingface)
- [LLM 臺灣社群](https://www.facebook.com/groups/llm.tw)

---

## 總結

開源 LLM 的調校是一門藝術也是科學。關鍵在於：
1. **理解需求** - 明確知道要解決什麼問題
2. **選對方法** - 不同場景用不同技術
3. **持續迭代** - 基於資料和回饋不斷改進
4. **平衡取捨** - 在效果、成本、速度間找平衡

記住：最貴的模型不一定最好，最適合的才是最好的！

*最後更新：2025年1月*