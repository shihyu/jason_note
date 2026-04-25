//! DistilBERT 模型的整合測試套件。
//!
//! 這個檔案包含了對 DistilBERT 模型各個核心組件的單元測試，以及對
//! 完整模型的端對端整合測試。
//!
//! 所有測試的「預期值」(expected values) 均來自 Hugging Face `transformers`
//! 函式庫的參考實作，以確保我們的 Candle 版本在數值上與之對齊。

// ==================================================================
//  第 1 部分：所有必要的 `use` 陳述
// ==================================================================
use anyhow::Result;
use approx::assert_abs_diff_eq;
use candle_core::{DType, Device, Module, Tensor};
use candle_nn::VarBuilder;
use hf_hub::{Repo, RepoType, api::sync::Api};

use candle_distilbert::distilbert::{
    DistilBertForMaskedLM, DistilBertModel, attention::DistilBertSelfAttention,
    config::DistilBertConfig, embeddings, layer, nn,
};

// ==================================================================
//  第 2 部分：測試輔助函式
// ==================================================================

/// 從 Hugging Face Hub 下載模型權重和設定檔。
///
/// 此函式會處理與 Hub 的所有互動，並直接回傳可用於模型實例化的
/// `VarBuilder` 和 `DistilBertConfig`。
fn get_vb_and_config(model_name: &str) -> Result<(VarBuilder<'static>, DistilBertConfig)> {
    let device = Device::Cpu;
    let api = Api::new()?;
    let repo = api.repo(Repo::with_revision(
        model_name.to_string(),
        RepoType::Model,
        "main".to_string(),
    ));

    let config_filename = repo.get("config.json")?;
    let weights_filename = repo.get("model.safetensors")?;

    // 直接讀取並解析為我們主要的 DistilBertConfig
    let config_str = std::fs::read_to_string(config_filename)?;
    let config: DistilBertConfig = serde_json::from_str(&config_str)?;

    let vb =
        unsafe { VarBuilder::from_mmaped_safetensors(&[weights_filename], DType::F32, &device)? };

    Ok((vb, config))
}

/// 將浮點數四捨五入到指定的小數位。
fn round_to_decimal_places(f: f32, places: u32) -> f32 {
    let multiplier = 10f32.powi(places as i32);
    (f * multiplier).round() / multiplier
}

/// 從一個 3D 張量中提取一個 2D 切片並四捨五入，以便進行比較。
fn slice_and_round(tensor: &Tensor, shape: (usize, usize)) -> Result<Vec<Vec<f32>>> {
    let tensor = tensor.squeeze(0)?;
    let tensor_vec = tensor.to_vec2::<f32>()?;
    let sliced_vec = tensor_vec
        .iter()
        .take(shape.0)
        .map(|nested_vec| {
            nested_vec
                .iter()
                .take(shape.1)
                .map(|&x| round_to_decimal_places(x, 4))
                .collect()
        })
        .collect();
    Ok(sliced_vec)
}

/// 建立一個 2D 注意力遮罩，並將其擴展為 Transformer 注意力層所需的 4D 形狀。
///
/// # Arguments
/// * `b_size`: usize - 批次大小 (batch size)。
/// * `seq_len`: usize - 序列長度 (sequence length)。
/// * `device`: &Device - 張量所在的設備。
///
/// # Returns
/// 一個 `U8` 型別、形狀為 `(b_size, 1, 1, seq_len)` 的張量。
fn create_extended_attention_mask(
    b_size: usize,
    seq_len: usize,
    device: &Device,
) -> Result<Tensor> {
    let attention_mask = Tensor::ones((b_size, seq_len), DType::U8, device)?;
    let extended_mask = attention_mask.unsqueeze(1)?.unsqueeze(2)?;
    Ok(extended_mask)
}

// ==================================================================
//  第 3 部分：測試函式
// ==================================================================

#[test]
/// 1. 基礎部件測試：驗證 `Embeddings` 層的輸出。
fn test_embeddings() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let vb_embeddings = vb.pp("distilbert.embeddings");
    let embeddings = embeddings::Embeddings::load(vb_embeddings, &config)?;

    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let output = embeddings.forward(&input_ids)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![0.3469, -0.1626, -0.2333],
        vec![-0.7254, 0.6949, 0.0031],
        vec![-0.8898, -0.2188, -0.4554],
    ];

    // 淺層部件，誤差極小，使用較嚴格的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 1e-4
    );
    Ok(())
}

#[test]
/// 2. 核心部件測試：驗證 `DistilBertSelfAttention` 層的輸出。
fn test_distilbert_self_attention() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;

    let vb_embeddings = vb.pp("distilbert.embeddings");
    let embeddings = embeddings::Embeddings::load(vb_embeddings, &config)?;
    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let embedding_output = embeddings.forward(&input_ids)?;

    let vb_attention = vb.pp("distilbert.transformer.layer.0.attention");
    let attention = DistilBertSelfAttention::load(vb_attention, &config)?;

    let extended_mask = create_extended_attention_mask(1, 4, &Device::Cpu)?;

    let output = attention.forward(&embedding_output, &extended_mask)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![0.1337, -0.0473, 0.4447],
        vec![0.0907, 0.1984, 0.4197],
        vec![-0.1002, 0.1296, 0.722],
    ];

    // Attention 層的計算誤差也很小，同樣使用較嚴格的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 1e-4
    );
    Ok(())
}

#[test]
/// 3. 核心部件測試：驗證 `FFN` 層的輸出。
fn test_ffn() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let distilbert_config: DistilBertConfig = config.into();

    // --- 準備 FFN 的輸入 (即 Attention Add & Norm 之後的輸出) ---
    let vb_embeddings = vb.pp("distilbert.embeddings");
    let embeddings = embeddings::Embeddings::load(vb_embeddings, &distilbert_config)?;
    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let embedding_output = embeddings.forward(&input_ids)?;

    let vb_attention = vb.pp("distilbert.transformer.layer.0.attention");
    let attention = DistilBertSelfAttention::load(vb_attention, &distilbert_config)?;
    let extended_mask = create_extended_attention_mask(1, 4, &Device::Cpu)?;
    let attention_output = attention.forward(&embedding_output, &extended_mask)?;

    let vb_sa_norm = vb.pp("distilbert.transformer.layer.0.sa_layer_norm");
    let sa_layer_norm = nn::layer_norm(distilbert_config.dim, 1e-12, vb_sa_norm)?;
    let ffn_input = sa_layer_norm.forward(&(attention_output + embedding_output)?)?;

    // --- 載入 FFN 並驗證其輸出 ---
    let vb_ffn = vb.pp("distilbert.transformer.layer.0.ffn");
    let ffn = layer::FFN::load(vb_ffn, &distilbert_config)?;
    let output = ffn.forward(&ffn_input)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![-0.6896, 0.0653, -0.0333],
        vec![-0.403, 0.1215, 0.4211],
        vec![-0.9056, -0.4509, -0.2738],
    ];

    // FFN 計算量大，浮點數誤差開始累積，因此使用較寬鬆的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 2e-3
    );
    Ok(())
}

#[test]
/// 4. 整合測試：驗證單個 `TransformerBlock` 的完整輸出。
fn test_transformer_block() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;

    let vb_embeddings = vb.pp("distilbert.embeddings");
    let embeddings = embeddings::Embeddings::load(vb_embeddings, &config.clone().into())?;
    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let embedding_output = embeddings.forward(&input_ids)?;

    let vb_block = vb.pp("distilbert.transformer.layer.0");
    let block = layer::TransformerBlock::load(vb_block, &config.into())?;

    let extended_mask = create_extended_attention_mask(1, 4, &Device::Cpu)?;

    let output = block.forward(&embedding_output, &extended_mask)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![0.0209, -0.038, 0.0625],
        vec![-0.452, 0.4705, 0.2942],
        vec![-0.8209, -0.2522, -0.0862],
    ];

    // 作為一個較大的整合測試，同樣採用較寬鬆的公差以應對誤差累積。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 2e-3
    );
    Ok(())
}

#[test]
/// 5. 端對端測試：驗證完整的 `DistilBertModel` (主幹) 的輸出。
fn test_distilbert_model_backbone() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let model = DistilBertModel::load(vb.pp("distilbert"), &config)?;

    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let attention_mask = Tensor::ones_like(&input_ids)?;
    let output = model.forward(&input_ids, &attention_mask)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![-0.2099, -0.1589, 0.2063],
        vec![-0.4446, -0.3966, 0.2451],
        vec![-0.5053, -0.5484, 0.0862],
    ];

    // 經過全部 6 層 Transformer，誤差累積最大，使用最寬鬆的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 3e-3
    );
    Ok(())
}

#[test]
/// 6. 端對端測試：驗證 `DistilBertForMaskedLM` 的最終 logits 輸出。
fn test_distilbert_for_masked_lm_full() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let model = DistilBertForMaskedLM::load(vb, &config)?;

    let input_ids = Tensor::new(&[[101u32, 2023, 2003, 102]], &Device::Cpu)?;
    let attention_mask = Tensor::ones_like(&input_ids)?;
    let output = model.forward(&input_ids, &attention_mask)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![-5.8788, -5.8295, -5.8591],
        vec![-10.147, -10.1183, -10.138],
        vec![-9.8976, -9.7942, -9.8487],
    ];
    // 這是最深層的測試，同樣使用最寬鬆的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 6e-3
    );
    Ok(())
}

#[test]
/// 7. 整合測試：驗證模型在使用 attention_mask 處理 padding 時的行為。
///
/// 這個測試確保模型能正確忽略序列中的 padding token (ID 為 0)，
/// 這是 Transformer 模型處理不同長度序列的關鍵功能。
fn test_distilbert_model_with_padding() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let model = DistilBertModel::load(vb.pp("distilbert"), &config)?;

    // 輸入："[CLS] hello world [SEP] [PAD]"
    let input_ids = Tensor::new(&[[101u32, 7592, 2088, 102, 0]], &Device::Cpu)?;
    // Attention mask 在 [PAD] token 的位置為 0
    let attention_mask = Tensor::new(&[[1u32, 1, 1, 1, 0]], &Device::Cpu)?;
    let output = model.forward(&input_ids, &attention_mask)?;

    let output_sliced = slice_and_round(&output, (3, 3))?;
    let expected_output = vec![
        vec![-0.1698, -0.1662, 0.0256],
        vec![-0.4213, 0.1761, 0.4999],
        vec![-0.2182, -0.2248, 0.4035],
    ];

    // 完整的模型主幹測試，使用較寬鬆的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 4e-3
    );
    Ok(())
}

#[test]
/// 8. 整合測試：驗證模型是否能正確處理批次化輸入 (batch_size > 1)。
///
/// 這個測試確保模型的張量操作在處理多個輸入序列時依然保持正確，
/// 這是模型在實際應用中進行高效推論的基礎。
fn test_distilbert_model_with_batching() -> Result<()> {
    let (vb, config) = get_vb_and_config("distilbert-base-uncased")?;
    let model = DistilBertModel::load(vb.pp("distilbert"), &config)?;

    // 輸入批次, shape: (2, 4)
    // 句子 1: "[CLS] this is a [SEP]"
    // 句子 2: "[CLS] what is it [SEP]"
    let input_ids = Tensor::new(
        &[[101u32, 2023, 2003, 102], [101, 2054, 2024, 102]],
        &Device::Cpu,
    )?;
    let attention_mask = Tensor::ones_like(&input_ids)?;
    let output = model.forward(&input_ids, &attention_mask)?;

    // 從批次輸出 (2, 4, 768) 中，取出第二個元素 (1, 4, 768) 進行驗證
    let second_item_output = output.narrow(0, 1, 1)?;

    let output_sliced = slice_and_round(&second_item_output, (3, 3))?;
    let expected_output = vec![
        vec![-0.1129, -0.019, 0.1227],
        vec![0.1029, -0.1496, -0.179],
        vec![0.0354, -0.4155, 0.2457],
    ];

    // 驗證批次處理的正確性，同樣使用較寬鬆的公差。
    assert_abs_diff_eq!(
        output_sliced
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        expected_output
            .iter()
            .flatten()
            .collect::<Vec<_>>()
            .as_slice(),
        epsilon = 3e-3
    );
    Ok(())
}
