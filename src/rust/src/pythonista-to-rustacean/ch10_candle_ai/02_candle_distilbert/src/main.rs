//!
//! # DistilBERT 推論範例：遮罩語言模型與句子嵌入
//!
//! 展示如何使用 Hugging Face Candle 框架載入 DistilBERT 模型，執行兩種經典任務：
//! 1. **遮罩語言模型 (Masked LM)**：預測句子中被 `[MASK]` 遮住的詞元
//! 2. **句子嵌入 (Sentence Embedding)**：將句子轉換為稠密向量表徵
//!
//! ## 架構圖
//!
//! ```text
//! ┌─────────────────────────────────────────────────────────────────────────┐
//! │                        DistilBERT 推論流程                              │
//! │                                                                         │
//! │   Hugging Face Hub                                                     │
//! │   distilbert-base-uncased                                              │
//! │          │                                                              │
//! │          ▼                                                              │
//! │   ┌──────────────────────┐    ┌──────────────────────┐               │
//! │   │  Config (config.json) │    │ Tokenizer (tokenizer.json)│          │
//! │   └──────────────────────┘    └──────────────────────┘               │
//! │          │                              │                              │
//! │          └──────────────┬──────────────┘                              │
//! │                         ▼                                               │
//! │              ┌──────────────────────┐                                  │
//! │              │  VarBuilder (mmap)  │                                  │
//! │              │  model.safetensors   │                                  │
//! │              └──────────────────────┘                                  │
//! │                         │                                               │
//! │                         ▼                                               │
//! │   ┌──────────────────────────────────────────────────────────┐         │
//! │   │  兩種推論模式                                              │         │
//! │   │                                                           │         │
//! │   │  ┌───────────────────┐   ┌───────────────────────────┐ │         │
//! │   │  │ DistilBertModel    │   │ DistilBertForMaskedLM    │ │         │
//! │   │  │ → 句子嵌入向量      │   │ → [MASK] 詞元預測       │ │         │
//! │   │  └───────────────────┘   └───────────────────────────┘ │         │
//! │   └──────────────────────────────────────────────────────────┘         │
//! └─────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (Transformers) 写法                              | Rust (Candle) 写法                    |
//! |-------------------|-----------------------------------------------------|---------------------------------------|
//! | 模型下載         | `AutoModel.from_pretrained("distilbert-base-uncased")` | `VarBuilder::from_mmaped_safetensors()` |
//! | 分詞器載入       | `AutoTokenizer.from_pretrained(...)`                   | `Tokenizer::from_file(...)`           |
//! | 設定檔讀取       | `AutoConfig.from_pretrained(...)`                    | `serde_json::from_str::<DistilBertConfig>(...)` |
//! | 遮罩預測         | `model.fill_mask_pipeline(...)`                       | `DistilBertForMaskedLM::forward()` + `softmax` + `top-k` |
//! | 句子嵌入         | `model(**inputs).last_hidden_state`                  | `DistilBertModel::forward()` → sequence_output |
//!
//! ## 關鍵技法
//!
//! - `VarBuilder::from_mmaped_safetensors`：記憶體映射式權重載入，無需複製資料
//! - `Tokenizer::encode`：將文字轉為 token IDs，包含特殊詞元處理
//! - `attention_mask.unsqueeze(1)?.unsqueeze(2)?`：2D → 4D 廣播擴展
//! - `candle_nn::ops::softmax`：在 Rust 中重現 `torch.nn.functional.softmax`
//! - `.i((0, mask_pos))`：使用 Candle 的索引語法取出特定位置的 logits
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch10_candle_ai/02_candle_distilbert
//! cargo run --release
//! ```
//!
use anyhow::{Error as E, Result, anyhow};
use candle_core::{Device, IndexOp, Tensor};
use candle_nn::VarBuilder;
use hf_hub::{Repo, RepoType, api::sync::Api};
use tokenizers::Tokenizer;

use candle_distilbert::{DistilBertConfig, DistilBertForMaskedLM, DistilBertModel};

/// 範例一：句子嵌入 (Sentence Embeddings)
///
/// 這個函式展示如何使用基礎的 DistilBertModel 將一個句子轉換成一系列的向量表徵 (embeddings)。
/// 這些 embeddings 可以用於下游任務，例如語意相似度比較、文本分類等。
fn run_sentence_embedding_example(
    device: &Device,
    vb: &VarBuilder,
    config: &DistilBertConfig,
    tokenizer: &Tokenizer,
) -> Result<()> {
    println!("--- 範例 1: 句子嵌入 (Sentence Embeddings) ---");
    let prompt = "Here is a test sentence";
    println!("輸入句子: \"{}\"\n", prompt);

    // 載入基礎模型 (不含特定任務的頭部)
    let model = DistilBertModel::load(vb.clone(), config)?;

    // 對輸入進行分詞
    let tokens = tokenizer.encode(prompt, true).map_err(E::msg)?;
    let token_ids = tokens.get_ids();

    // 先建立 1D Tensor，再用 unsqueeze(0) 增加 batch 維度
    let input_ids = Tensor::new(token_ids, device)?.unsqueeze(0)?;
    let attention_mask = input_ids.ones_like()?;

    // 執行推論，得到最後一層的隱藏狀態 (即 embeddings)
    let embeddings = model.forward(&input_ids, &attention_mask)?;

    println!("輸出 embeddings:");
    println!("{}", embeddings);
    println!(
        "\nTensor 維度 (Batch, 序列長度, 隱藏層維度): {:?}",
        embeddings.shape()
    );
    Ok(())
}

/// 範例二：遮罩詞元預測 (Masked Token Prediction)
///
/// 這個函式展示如何使用 DistilBertForMaskedLM 來預測句子中被 "[MASK]" 符號遮蓋住的詞元。
/// 這是 BERT 系列模型在預訓練階段的核心任務之一。
fn run_masked_lm_example(
    device: &Device,
    vb: &VarBuilder,
    config: &DistilBertConfig,
    tokenizer: &Tokenizer,
) -> Result<()> {
    println!("--- 範例 2: 遮罩詞元預測 (Masked Token Prediction) ---");
    let prompt = "The capital of Taiwan is [MASK].";

    let top_k = 5;
    println!("輸入句子: \"{}\"\n", prompt);

    // 載入 DistilBertForMaskedLM 模型，這個版本包含了預測詞元的「頭部」。
    let model = DistilBertForMaskedLM::load(vb.clone(), config)?;

    // 從分詞器的詞彙表中，找出 "[MASK]" 這個特殊 token 的專屬數字 ID。
    let mask_token_id = tokenizer
        .token_to_id("[MASK]")
        .ok_or_else(|| anyhow!("token '[MASK]' not found in vocabulary"))?;

    // 將輸入的句子轉換成模型可以理解的數字序列 (token IDs)。
    let tokens = tokenizer.encode(prompt, true).map_err(E::msg)?;
    let token_ids = tokens.get_ids();

    // 在數字序列中，找到 [MASK] token ID 所在的位置 (索引)。
    let mask_pos = token_ids
        .iter()
        .position(|&id| id == mask_token_id)
        .ok_or_else(|| anyhow!("[MASK] token not found in the prompt"))?;

    // 將 token ID 序列轉換成 Candle 的 Tensor 格式。
    // 先建立一維 Tensor，再使用 `unsqueeze(0)` 增加一個批次維度 (batch dimension)。
    let input_ids = Tensor::new(token_ids, device)?.unsqueeze(0)?;
    // 建立一個簡單的 attention_mask，告訴模型要注意序列中的所有 token。
    let attention_mask = input_ids.ones_like()?;

    // 執行模型的前向傳播 (Inference)，得到預測結果。
    // `logits` 的維度會是 [batch_size, 序列長度, 詞彙表大小]。
    let logits = model.forward(&input_ids, &attention_mask)?;

    // 從巨大的 logits 結果中，只取出我們關心的 [MASK] 位置上的預測分數。
    // 結果 `logits` 維度會是 [詞彙表大小]。
    let logits = logits.i((0, mask_pos))?;

    // 使用 softmax 函式，將模型輸出的原始分數 (logits) 轉換成機率分佈。
    // 所有詞的機率加總會等於 1。
    let prs = candle_nn::ops::softmax(&logits, 0)?;

    // --- 找出機率最高的前 K 個 Token ---
    // 1. 為了方便處理，將 Candle Tensor 轉換成標準的 Rust Vec<f32>。
    let prs_vec = prs.to_vec1::<f32>()?;
    // 2. 建立一個包含 (機率, 索引) 的 Vec，這樣排序時才能同時保留機率和 token ID。
    let mut indexed_prs: Vec<(f32, u32)> = prs_vec
        .iter()
        .enumerate()
        .map(|(index, &prob)| (prob, index as u32))
        .collect();
    // 3. 根據機率值由高到低進行排序。
    indexed_prs.sort_by(|a, b| b.0.partial_cmp(&a.0).unwrap_or(std::cmp::Ordering::Equal));

    println!("預測 '{}' 位置最可能的 {} 個詞:", "[MASK]", top_k);
    // 從排序好的結果中，取出前 k 名。
    for (i, (prob, token_id)) in indexed_prs.iter().take(top_k).enumerate() {
        // 將 token ID 轉換回人類可讀的文字。jK:w
        let token = tokenizer.id_to_token(*token_id).unwrap_or_default();
        println!("{:>3}: {:<15} (機率: {:5.2}%)", i + 1, token, prob * 100.0);
    }
    Ok(())
}

fn main() -> Result<()> {
    let device = Device::Cpu;

    // --- 1. 一次性通用設定：載入模型資源 ---
    // 我們使用 distilbert-base-uncased，這是一個通用的預訓練模型，
    // 適用於以上兩種任務。
    println!("正在從 Hugging Face Hub 載入模型資源...\n");
    let model_id = "distilbert-base-uncased".to_string();
    let revision = "main".to_string();
    let repo = Repo::with_revision(model_id, RepoType::Model, revision);
    let api = Api::new()?;
    let api = api.repo(repo);

    let config_filename = api.get("config.json")?;
    let tokenizer_filename = api.get("tokenizer.json")?;
    let weights_filename = api.get("model.safetensors")?;

    let config: DistilBertConfig =
        serde_json::from_str(&std::fs::read_to_string(config_filename)?)?;
    let tokenizer = Tokenizer::from_file(tokenizer_filename).map_err(E::msg)?;
    let vb = unsafe {
        VarBuilder::from_mmaped_safetensors(&[weights_filename], candle_core::DType::F32, &device)?
    };
    println!("模型資源載入完成。\n");

    println!("============================================================");
    println!("      展示 DistilBERT 模型的兩種主要用途");
    println!("============================================================\n");

    // --- 2. 執行範例一 ---
    run_sentence_embedding_example(&device, &vb, &config, &tokenizer)?;

    println!("\n{}\n", "-".repeat(60));

    // --- 3. 執行範例二 ---
    run_masked_lm_example(&device, &vb, &config, &tokenizer)?;

    Ok(())
}
