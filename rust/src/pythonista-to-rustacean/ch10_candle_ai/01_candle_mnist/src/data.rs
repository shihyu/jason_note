//! 這個模組負責處理所有與 MNIST 資料集相關的載入、解碼與批次化邏輯。
//!
//! 主要的進入點是 `MnistDataset::new()`，它會從 Hugging Face Hub 下載資料，
//! 並利用 Rayon 進行高效率的並行解碼。接著，可以直接從 MnistDataset 物件
//! 透過 `.train_iter()` 或 `.test_iter()` 方法取得用於訓練的批次迭代器。

use anyhow::{Result, anyhow};
use candle_core::{DType, Device, Error as CandleError, Tensor};
use candle_datasets::{
    Batcher,
    hub::{FileReader, from_hub},
};
use hf_hub::api::sync::Api;
use parquet::file::reader::SerializedFileReader;
use rayon::prelude::*;
use std::fs::File;

// --- 常數定義區 ---
// 將魔法數字定義為具名常數，增加可讀性與可維護性。
const MNIST_REPO: &str = "ylecun/mnist";
const TRAIN_SAMPLES: i64 = 60_000;
const TEST_SAMPLES: i64 = 10_000;
const IMAGE_DIM: usize = 28 * 28;
const LABEL_COL: &str = "label";
const IMAGE_COL: &str = "image";

// --- 結構體定義區 ---
/// 負責存放從 Hub 下載並解碼後的完整 MNIST 資料集。
///
/// 這個結構體代表了最純粹的資料集，本身不包含批次化或迭代邏輯，
/// 僅僅是將所有圖片與標籤以 Tensor 的形式保存在記憶體中。
/// 同時也扮演著「迭代器工廠」的角色。
#[derive(Debug)]
pub struct MnistDataset {
    pub train_images: Tensor,
    pub train_labels: Tensor,
    pub test_images: Tensor,
    pub test_labels: Tensor,
}

impl MnistDataset {
    /// 創建一個新的 `MnistDataset` 物件。
    ///
    /// 這個函式會負責從 Hugging Face Hub 下載資料、進行並行化解碼，並將結果轉換為 Tensor。
    pub fn new() -> Result<Self> {
        // 初始化 Hugging Face Hub API，準備下載檔案。
        let api = Api::new()?;
        let mut mnist_files = from_hub(&api, MNIST_REPO.to_string())?;

        // 透過 Parquet 檔案的 metadata 來找出訓練集與測試集。
        // 這裡我們用檔案的總行數來辨識，因為 MNIST 的樣本數是固定的。
        let train_file = mnist_files
            .iter()
            .position(|file| file.metadata().file_metadata().num_rows() == TRAIN_SAMPLES)
            // `.position()` 會找到符合條件的索引，`.map()` 則利用該索引
            // 從 Vec 中移除項目並回傳，這種寫法可以避免後續再次遍歷。
            .map(|pos| mnist_files.remove(pos));

        let test_file = mnist_files
            .iter()
            .position(|file| file.metadata().file_metadata().num_rows() == TEST_SAMPLES)
            .map(|pos| mnist_files.remove(pos));

        // 確保兩個檔案都成功找到，才繼續進行解碼。
        if let (Some(train), Some(test)) = (train_file, test_file) {
            println!("> 正在進行解碼與轉換...");
            // 找到檔案後，就交由我們的小幫手函式 `load_parquet` 進行實際的解碼與轉換。
            let (train_images, train_labels) = load_parquet(train)?;
            let (test_images, test_labels) = load_parquet(test)?;

            Ok(Self {
                train_images,
                train_labels,
                test_images,
                test_labels,
            })
        } else {
            Err(anyhow!("無法在資料集中找到必要的訓練或測試檔案！"))
        }
    }

    /// 創建並回傳一個用於訓練資料的批次迭代器。
    ///
    /// 這個方法使用 `&self` (共享借用)，所以不會消耗 MnistDataset。
    /// 每次呼叫此方法都會得到一個全新的迭代器。
    pub fn train_iter(
        &self,
        batch_size: usize,
    ) -> Result<impl Iterator<Item = Result<(Tensor, Tensor), CandleError>>> {
        // Tensor 的 clone() 操作成本極低，它只複製了指向底層資料的指標 (Arc)，
        // 並增加引用計數，而不會複製整個 Tensor 的資料。
        let train_images = self.train_images.clone();
        let train_labels = self.train_labels.clone();
        let train_len = self.train_images.dim(0)?;

        // 建立一個惰性迭代器，逐一從完整的資料張量中提取出 (樣本, 標籤) 的元組。
        let train_iter = (0..train_len).map(move |i| {
            // 由於索引 `i` 的範圍是 `0..train_len`，此操作在邏輯上是絕對安全的。
            // 使用 .expect() 可以讓我們在保持程式碼簡潔的同時，記錄下這個重要的不變性假設。
            let sample = train_images.get(i).expect("索引應該在範圍內");
            let label = train_labels.get(i).expect("索引應該在範圍內");
            (sample, label)
        });

        // 使用 Batcher::new2 將 (樣本, 標籤) 元組的迭代器，轉換為批次化的迭代器。
        // `new2` 會自動處理將單一樣本堆疊 (stack) 成批次張量的邏輯。
        let train_dl = Batcher::new2(train_iter).batch_size(batch_size);

        Ok(train_dl)
    }

    /// 創建並回傳一個用於測試資料的批次迭代器。
    pub fn test_iter(
        &self,
        batch_size: usize,
    ) -> Result<impl Iterator<Item = Result<(Tensor, Tensor), CandleError>>> {
        let test_images = self.test_images.clone();
        let test_labels = self.test_labels.clone();
        let test_len = self.test_images.dim(0)?;

        let test_iter = (0..test_len).map(move |i| {
            let sample = test_images.get(i).expect("索引應該在範圍內");
            let label = test_labels.get(i).expect("索引應該在範圍內");
            (sample, label)
        });

        let test_dl = Batcher::new2(test_iter).batch_size(batch_size);
        Ok(test_dl)
    }
}

// --- 內部輔助函式區 ---

/// 從 Parquet 檔案中載入 MNIST 圖片與標籤，並利用 Rayon 進行並行化解碼。
///
/// 由於圖片解碼是 CPU 密集的任務，透過並行化可以大幅縮短資料載入的時間。
fn load_parquet(parquet: SerializedFileReader<File>) -> Result<(Tensor, Tensor)> {
    let num_rows = parquet.metadata().file_metadata().num_rows() as usize;

    // 為了讓 Rayon 的並行迭代器能順利運作，我們得先將所有 row 讀進記憶體。
    let rows: Vec<_> = parquet.into_iter().collect::<Result<_, _>>()?;

    // 使用 Rayon 將解碼任務分散到多個 CPU 核心上並行處理。
    let results: Vec<(Vec<u8>, u8)> = rows
        .into_par_iter()
        .map(|row| -> Result<(Vec<u8>, u8)> {
            // 在每個執行緒中，從 Parquet 的 row 物件安全地提取出 `image` 和 `label` 欄位。
            // 透過欄位名稱進行匹配，可以避免因未來格式變更、欄位順序調換而導致的錯誤。
            let mut image_bytes: Option<&[u8]> = None;
            let mut label_val: Option<i64> = None;

            for (name, field) in row.get_column_iter() {
                match name.as_str() {
                    LABEL_COL => {
                        if let parquet::record::Field::Long(label) = field {
                            label_val = Some(*label);
                        }
                    }
                    IMAGE_COL => {
                        if let parquet::record::Field::Group(sub_row) = field {
                            if let Some((_, parquet::record::Field::Bytes(bytes))) =
                                sub_row.get_column_iter().next()
                            {
                                image_bytes = Some(bytes.data());
                            }
                        }
                    }
                    _ => {}
                }
            }

            if let (Some(bytes), Some(label)) = (image_bytes, label_val) {
                // 從記憶體中的二進位緩衝區解碼 PNG 影像。
                // 這一步是主要的 CPU 運算瓶頸，也是最適合並行化的地方。
                let decoded_image = image::load_from_memory(bytes)?;
                let luma8_image = decoded_image.to_luma8();
                Ok((luma8_image.into_raw(), label as u8))
            } else {
                Err(anyhow!("在 Parquet 的其中一列中找不到 image 或 label 欄位"))
            }
        })
        // 將所有並行任務的 `Result` 收集起來。若任一任務失敗，此處會提早回傳錯誤。
        .collect::<Result<Vec<_>>>()?;

    // 建立兩個緩衝區 (buffer)，用來彙整所有並行任務的處理結果。
    // 透過 `with_capacity` 預先分配足夠的記憶體，可以避免後續 `push` 或 `extend` 時，
    // 因容量不足而需要重新分配記憶體所帶來的效能開銷。
    let mut image_buffer = Vec::with_capacity(num_rows * IMAGE_DIM);
    let mut label_buffer = Vec::with_capacity(num_rows);

    // 迭代處理結果，將各個圖片的像素資料串接起來，形成一個扁平化的緩衝區。
    for (image_vec, label) in results {
        image_buffer.extend_from_slice(&image_vec);
        label_buffer.push(label);
    }

    // 最後，將整理好的緩衝區轉換為 Candle Tensor。
    let images = (
        // 1. 從 Vec<u8> 創建 Tensor，並設定其維度為 [樣本數, 圖片大小]。
        Tensor::from_vec(image_buffer, (num_rows, IMAGE_DIM), &Device::Cpu)?
            // 2. 將像素資料的型別從 u8 轉換為 F32，這是神經網路計算常用的格式。
            .to_dtype(DType::F32)?
            // 3. 進行標準化，將像素值從 [0, 255] 縮放到 [0.0, 1.0] 的範圍。
            / 255.0
    )?;
    let labels = Tensor::from_vec(label_buffer, (num_rows,), &Device::Cpu)?;

    Ok((images, labels))
}
