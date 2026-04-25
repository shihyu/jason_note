//! 這個模組包含了模型訓練的核心邏輯。
//!
//! 它提供了兩種主要的訓練函式：
//! 1. `run_foundational_training`：一個完全手動實作的訓練迴圈，旨在展示
//!    `candle-core` 的底層運作原理，包含手動批次處理、梯度計算與權重更新。
//! 2. `run_training_with_batcher`：使用 `candle_datasets::Batcher` 的標準作法，
//!    這是更推薦的、更簡潔且功能更完整的訓練方式。

use anyhow::Result;
use candle_core::{D, DType, Device, Tensor};
use candle_nn::{
    VarMap, loss,
    optim::{AdamW, Optimizer},
};

use crate::data;

// --- Trait 定義區 ---

/// 代表一個可訓練模型的通用 Trait。
///
/// 任何實作了這個 Trait 的結構體，都必須提供一個 `forward` 方法，
/// 用於定義資料如何從輸入流向輸出。
pub trait Model {
    fn forward(&self, xs: &Tensor) -> Result<Tensor>;
}

// --- 核心訓練函式區 ---

/// 執行訓練：完全使用 `candle-core` 進行手動實作。
///
/// 在這趟旅程中，我們會先刻意繞開所有高階工具，只用最底層的
/// `candle-core` 所提供的 `Tensor`，在 MNIST 資料集上從零到有地
/// 完成一次基本的類神經網路訓練。這個函式是為了教學與展示目的。
pub fn run_foundational_training<M: Model>(
    model: &M,
    varmap: &VarMap,
    device: &Device,
    dataset: &data::MnistDataset,
) -> Result<()> {
    println!("\n> 開始訓練：使用 `candle-core` 手動實作...");

    // --- 訓練超參數 ---
    let num_epochs = 10;
    let learning_rate = 0.01;
    let batch_size = 64;

    // --- 資料預處理 ---
    // 為了進行手動批次切割，我們先將所有訓練資料一次性地載入目標運算設備。
    let train_images = dataset.train_images.to_device(device)?;
    // 將標籤轉換為 U32 型別，這是分類任務中計算損失時常用的格式。
    let train_labels = dataset
        .train_labels
        .to_dtype(DType::U32)?
        .to_device(device)?;

    // --- 批次處理的準備工作 ---
    let num_train_samples = train_images.dim(0)?;
    // 計算總共需要多少個批次才能完整迭代一次資料集。
    // 這裡使用整數除法的技巧來處理不能整除的情況（向上取整）。
    let num_batches = (num_train_samples + batch_size - 1) / batch_size;

    // --- 訓練迴圈 ---
    for epoch in 1..=num_epochs {
        let mut total_epoch_loss = 0.0;

        // 手動迭代索引，並使用 `narrow` 方法從大張量中切割出批次。
        for batch_idx in 0..num_batches {
            let start_idx = batch_idx * batch_size;
            // 確保最後一個批次不會超出邊界。
            let current_batch_size = (num_train_samples - start_idx).min(batch_size);

            let batch_images = train_images.narrow(0, start_idx, current_batch_size)?;
            let batch_labels = train_labels.narrow(0, start_idx, current_batch_size)?;

            // --- 1. 前向傳播 (Forward Pass) ---
            let logits = model.forward(&batch_images)?;

            // --- 2. 計算損失值 (Loss Calculation) ---
            let log_probabilities = crate::ops::log_softmax(&logits, D::Minus1)
                .map_err(|e| anyhow::anyhow!("計算 log_softmax 失敗: {}", e))?;
            let training_loss = crate::ops::nll_loss(&log_probabilities, &batch_labels)
                .map_err(|e| anyhow::anyhow!("計算 NLL 損失失敗: {}", e))?;
            total_epoch_loss += training_loss
                .to_scalar::<f32>()
                .map_err(|e| anyhow::anyhow!("轉換損失為純量失敗: {}", e))?;

            // --- 3. 反向傳播 (Backward Pass) ---
            let grads = training_loss
                .backward()
                .map_err(|e| anyhow::anyhow!("計算梯度失敗: {}", e))?;

            // --- 4. 手動更新權重 (Manual Weight Update) ---
            // 遍歷 VarMap 中所有的可訓練變數 (權重和偏差)。
            for var in varmap.all_vars().iter() {
                // 檢查當前變數是否有對應的梯度。
                if let Some(grad) = grads.get(var) {
                    // 梯度下降法： new_weight = old_weight - learning_rate * gradient
                    let new_value = (var.as_tensor() - (grad * learning_rate)?)
                        .map_err(|e| anyhow::anyhow!("計算新權重失敗: {}", e))?;
                    var.set(&new_value)
                        .map_err(|e| anyhow::anyhow!("設定新權重失敗: {}", e))?;
                }
            }
        }

        let avg_loss = total_epoch_loss / num_batches as f32;
        println!(
            "Epoch [{:2}/{}] | 平均損失: {:.5}",
            epoch, num_epochs, avg_loss
        );
    }

    // --- 評估模型 ---
    // 將所有測試資料一次性載入設備進行評估。
    let test_images = dataset.test_images.to_device(device)?;
    let test_labels = dataset
        .test_labels
        .to_dtype(DType::U32)?
        .to_device(device)?;

    // 進行一次完整的前向傳播，得到所有測試樣本的預測 logits。
    let logits = model.forward(&test_images)?;
    // 找出每個樣本中，logit 值最大的那個索引，作為模型的預測類別。
    let predicted_classes = logits.argmax(D::Minus1)?;
    // 比較預測類別與真實標籤，計算正確預測的總數。
    let correct_predictions = predicted_classes
        .eq(&test_labels)?
        .to_dtype(DType::U32)?
        .sum_all()?
        .to_scalar::<u32>()?;
    let num_test_samples = dataset.test_images.dim(0)?;
    let accuracy = correct_predictions as f32 / num_test_samples as f32 * 100.0;
    println!(
        "\n最終測試準確率: {:.2}% ({}/{} 正確)",
        accuracy, correct_predictions, num_test_samples
    );

    Ok(())
}

/// 使用 `Batcher` 迭代器進行訓練。
///
/// 這是 Candle 中更典型且推薦的作法。`Batcher` 會自動處理批次的生成、
/// 資料的隨機打亂 (shuffling) 以及記憶體管理，讓訓練迴圈更簡潔。
pub fn run_training_with_batcher<M: candle_nn::Module>(
    model: &M,
    varmap: &VarMap,
    device: &Device,
    dataset: &data::MnistDataset,
) -> Result<()> {
    println!("\n> 開始訓練：使用 Batcher 迭代器...");

    // --- 訓練設定 ---
    // 使用 AdamW 優化器，這是 Adam 的一個改良版本，常用於現代深度學習。
    let mut optimizer = AdamW::new_lr(varmap.all_vars(), 1e-3)?;
    let num_epochs = 10;
    let batch_size = 64;

    let num_test_samples = dataset.test_images.dim(0)?;

    // --- 訓練迴圈 ---
    for epoch in 1..=num_epochs {
        let mut total_epoch_loss = 0.0;
        let mut batch_count = 0;

        // 在每個 Epoch 開始時，都從資料集工廠方法 `train_iter` 取得一個新的訓練迭代器。
        // 這確保了如果 Batcher 內部有隨機化邏輯，每個 Epoch 的資料順序都不同。
        for batch in dataset.train_iter(batch_size)? {
            // 從迭代器中解構出 (圖片, 標籤) 的元組。
            let (batch_images, batch_labels) = batch?;

            // 將當前批次的資料移動到指定的運算設備 (例如 Metal GPU)。
            let batch_images = batch_images.to_device(device)?;
            let batch_labels = batch_labels.to_dtype(DType::U32)?.to_device(device)?;

            // --- 前向、計算損失、反向傳播 ---
            let logits = model.forward(&batch_images)?;
            // 使用 candle_nn 提供的 `cross_entropy`，它內部整合了 log_softmax 和 nll_loss，
            // 不僅使用上更方便，通常也經過數值穩定性優化。
            let loss = loss::cross_entropy(&logits, &batch_labels)?;
            // 優化器的 `backward_step` 會自動計算梯度並更新與優化器綁定的所有變數。
            optimizer.backward_step(&loss)?;

            total_epoch_loss += loss.to_scalar::<f32>()?;
            batch_count += 1;
        }

        let avg_loss = total_epoch_loss / batch_count as f32;
        println!(
            "Epoch [{:2}/{}] | 平均損失: {:.5}",
            epoch, num_epochs, avg_loss
        );
    }

    // --- 評估模型 ---
    let mut total_correct_predictions = 0;
    // 為測試資料也建立一個迭代器，以批次方式進行評估，可節省記憶體。
    for batch in dataset.test_iter(batch_size)? {
        let (test_images, test_labels) = batch?;
        let test_images = test_images.to_device(device)?;
        let test_labels = test_labels.to_dtype(DType::U32)?.to_device(device)?;

        // 進行預測並計算批次內的正確數量。
        let predicted_logits = model.forward(&test_images)?;
        let predicted_classes = predicted_logits.argmax(D::Minus1)?;
        let correct_in_batch = predicted_classes
            .eq(&test_labels)?
            .to_dtype(DType::U32)?
            .sum_all()?
            .to_scalar::<u32>()?;
        total_correct_predictions += correct_in_batch;
    }

    // 計算並輸出最終準確率。
    let final_accuracy = total_correct_predictions as f32 / num_test_samples as f32;
    println!(
        "\n最終測試準確率: {:.2}% ({}/{} 正確)",
        final_accuracy * 100.0,
        total_correct_predictions,
        num_test_samples
    );

    Ok(())
}

// src/training.rs (續)

#[cfg(test)]
mod tests {
    use super::*;
    use crate::{models, ops};
    use candle_core::{DType, Device, Tensor};
    use candle_nn::{Module, Optimizer, SGD, VarBuilder, VarMap};
    use std::collections::HashMap;

    // --- 黃金標準 ---
    // 在重構過程中，這個函式會逐步演進，始終代表「已被驗證的最新版本」。
    // 初始狀態是「全手刻」。
    fn run_one_step_original(
        // [重構] 2. 使用 candle_nn::{Linear, Module} 重構：從手刻結構到慣用模式
        // model: &models::linear_manual::MnistClassifier,
        model: &models::linear_nn::MnistClassifier,
        varmap: &VarMap,
        images: &Tensor,
        labels: &Tensor,
        lr: f64,
    ) -> Result<(f32, Tensor)> {
        let logits = model.forward(images)?;
        // [重構] 1. 使用 candle_nn::loss::cross_entropy 重構：從手動計算到框架優化
        // let log_probs = ops::log_softmax(&logits, D::Minus1)?;
        // let loss = ops::nll_loss(&log_probs, labels)?;
        let loss = candle_nn::loss::cross_entropy(&logits, labels)?;
        let loss_val = loss.to_scalar::<f32>()?;

        let grads = loss.backward()?;
        // 為了方便比較，我們只關注第一個隱藏層的權重更新
        // 以執行緒安全的方式，從 VarMap 中按名稱取得 "hidden.weight" 變數的複本以供後續使用。
        let weight_var = varmap
            .data()
            .lock()
            .unwrap()
            .get("hidden.weight")
            .unwrap()
            .clone();
        let weight_grad = grads.get(&weight_var).unwrap();

        let scaled_grad = (weight_grad * lr)?;
        let updated_weight = weight_var.as_tensor().sub(&scaled_grad)?;

        Ok((loss_val, updated_weight))
    }

    // --- 待測版本 ---
    // 這個函式是我們的「實驗場」，用於測試下一步的重構。
    // 初始狀態與原始版本完全相同。
    fn run_one_step_refactored(
        // [重構] 2. 使用 candle_nn::{Linear, Module} 重構：從手刻結構到慣用模式
        // model: &models::linear_manual::MnistClassifier,
        model: &models::linear_nn::MnistClassifier,
        varmap: &VarMap,
        images: &Tensor,
        labels: &Tensor,
        lr: f64,
    ) -> Result<(f32, Tensor)> {
        let logits = model.forward(images)?;
        // [重構] 1. 使用 candle_nn::loss::cross_entropy 重構：從手動計算到框架優化
        // let log_probs = ops::log_softmax(&logits, D::Minus1)?;
        // let loss = ops::nll_loss(&log_probs, labels)?;
        let loss = candle_nn::loss::cross_entropy(&logits, labels)?;
        let loss_val = loss.to_scalar::<f32>()?;

        // [重構] 3. 使用 candle_nn::optim 重構：從手動更新到自動化優化
        // let grads = loss.backward()?;
        // let weight_var = varmap
        //     .data()
        //     .lock()
        //     .unwrap()
        //     .get("hidden.weight")
        //     .unwrap()
        //     .clone();
        // let weight_grad = grads.get(&weight_var).unwrap();

        // let scaled_grad = (weight_grad * lr)?;
        // let updated_weight = weight_var.as_tensor().sub(&scaled_grad)?;
        // 建立優化器
        let mut optimizer = SGD::new(varmap.all_vars(), lr)?;
        // 使用 optimizer.backward_step() 取代 loss.backward() 與手動更新的邏輯
        optimizer.backward_step(&loss)?;

        // 為了驗證，我們在更新後，重新從 varmap 取出權重
        let updated_weight = varmap
            .data()
            .lock()
            .unwrap()
            .get("hidden.weight")
            .unwrap()
            .as_tensor()
            .copy()?;

        Ok((loss_val, updated_weight))
    }

    // --- 主測試函式 ---
    #[test]
    fn test_incremental_refactoring() -> Result<()> {
        let device = Device::Cpu;
        let lr = 0.01;
        let dummy_images = Tensor::randn(0f32, 1f32, (4, 784), &device)?;
        let dummy_labels = Tensor::from_slice(&[1u32, 5, 4, 9], (4,), &device)?;

        // 建立共享的 VarMap 與 VarBuilder
        let varmap = VarMap::new();
        let vb = VarBuilder::from_varmap(&varmap, DType::F32, &device);

        // 使用同一個 VarBuilder 建立模型，確保它們共享同一組 Var
        // [重構] 2. 使用 candle_nn::{Linear, Module} 重構：從手刻結構到慣用模式
        // let model_orig = models::linear_manual::MnistClassifier::new(vb.clone())?;
        let model_orig = models::linear_nn::MnistClassifier::new(vb.clone())?;
        // [重構] 2. 使用 candle_nn::{Linear, Module} 重構：從手刻結構到慣用模式
        // let model_refactored = models::linear_manual::MnistClassifier::new(vb.clone())?;
        let model_refactored = models::linear_nn::MnistClassifier::new(vb.clone())?;

        // --- 儲存與還原狀態 ---
        // 1. 儲存：在任何計算發生前，複製一份所有參數的初始狀態
        // 建立 VarMap 中所有權重的深層複本快照，用於在測試中還原模型的初始狀態。
        let initial_vars: HashMap<String, Tensor> = varmap
            .data()
            .lock()
            .unwrap()
            .iter()
            .map(|(name, var)| (name.clone(), var.as_tensor().copy().unwrap()))
            .collect();

        // 執行「黃金標準」版本
        let (loss_orig, weight_orig) =
            run_one_step_original(&model_orig, &varmap, &dummy_images, &dummy_labels, lr)?;

        // 2. 還原：在執行下一個版本前，將所有參數還原到初始狀態
        for (name, initial_tensor) in &initial_vars {
            varmap
                .data()
                .lock()
                .unwrap()
                .get(name)
                .unwrap()
                .set(initial_tensor)?;
        }

        // 執行「待測」版本
        let (loss_refactored, weight_refactored) =
            run_one_step_refactored(&model_refactored, &varmap, &dummy_images, &dummy_labels, lr)?;

        println!("Original Loss:   {:.6}", loss_orig);
        println!("Refactored Loss: {:.6}", loss_refactored);

        // --- 最終裁決 ---
        // 關於浮點數的精度:
        // 手動實現與框架優化版本在計算路徑上可能存在微小差異，因此使用 1e-5 作為務實的容忍度標準。
        let tolerance = 1e-5;
        assert!(
            (loss_orig - loss_refactored).abs() < tolerance,
            "Loss values are inconsistent!"
        );
        let weight_diff = weight_orig
            .sub(&weight_refactored)?
            .abs()?
            .sum_all()?
            .to_scalar::<f32>()?;
        assert!(weight_diff < tolerance, "Updated weights are inconsistent!");

        Ok(())
    }
}
