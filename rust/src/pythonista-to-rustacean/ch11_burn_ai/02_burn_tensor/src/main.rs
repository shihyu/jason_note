//!
//! # Burn Tensor 操作範例
//!
//! 展示 Burn 框架中 `Tensor` 的各種建立、操作與資料讀取方式。
//! 涵蓋從陣列建立、迭代提取、型別轉換等常見情境。
//!
//! ## 架構圖
//!
//! ```text
//! ┌────────────────────────────────────────────────────────────────────────┐
//! │                    Burn Tensor 建立與操作流程                            │
//! │                                                                        │
//! │   建立方法                                                             │
//! │   ├── from_data([f32; N])        ← 直接從 Rust 陣列                   │
//! │   ├── from_floats([f32; N])      ← 便利包裝 (推薦)                   │
//! │   ├── from_data(&Vec<f32>[..])   ← 從 Vec 切片                       │
//! │   ├── TensorData::from([...])     ← 明確使用 TensorData               │
//! │   ├── ones_like() / zeros_like() ← 從現有 Tensor 複製形狀             │
//! │   └── zeros::<Int>()             ← 建立整數型 Tensor                   │
//! │          │                                                          │
//! │          ▼                                                          │
//! │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐   │
//! │   │   to_data()     │    │  into_data()   │    │  to_vec()      │   │
//! │   │  (保留 Tensor)  │    │  (消耗 Tensor)  │    │ (→ Vec<T>)     │   │
//! │   └─────────────────┘    └─────────────────┘    └─────────────────┘   │
//! └────────────────────────────────────────────────────────────────────────┘
//! ```
//!
//! ## Python vs Rust 對照表
//!
//! | 情境              | Python (PyTorch) 写法                        | Rust (Burn) 写法                              |
//! |-------------------|-------------------------------------------|-----------------------------------------------|
//! | 建立 1D Tensor   | `torch.tensor([1.0, 2.0])`              | `Tensor::<B, 1>::from_floats([1.0, 2.0], &device)` |
//! | 建立 2D Tensor   | `torch.zeros(3, 4)`                      | `Tensor::<B, 2>::zeros([3, 4], &device)`   |
//! | 建立 Int Tensor  | `torch.tensor([1, 2, 3], dtype=torch.long)` | `Tensor::<B, 1, Int>::from_data([1i32, 2, 3], &device)` |
//! | ones/zeros_like | `torch.ones_like(t)` / `torch.zeros_like(t)` | `Tensor::ones_like(&t)` / `Tensor::zeros_like(&t)` |
//! | 取得資料 (不消耗) | `t.numpy()` (仍保留)                     | `t.to_data()` (Tensor 仍可使用)              |
//! | 取得資料 (消耗)   | `t.numpy()` (消耗後不可再用)           | `t.into_data()` (Tensor 不可再用)            |
//! | 轉 Vec           | `t.tolist()`                             | `t.to_data().to_vec::<f32>().unwrap()`     |
//! | as_slice         | 無直接對應                                | `data.as_slice::<f32>()`                   |
//!
//! ## 關鍵技法
//!
//! - `type B = Wgpu`：使用類型別名簡化泛型書寫
//! - `Tensor::<B, 1>::from_floats`：推薦的浮點數組建方式
//! - `to_data()` vs `into_data()`：前者保留 Tensor，後者消耗
//! - `as_slice::<f32>()`：需要先取 TensorData，否則 chain 會造成借用錯誤
//! - `.to_vec::<T>()`：可直接 chain 取得擁有權的 Vec
//! - `into_scalar()`：從 1x1 Tensor 取出純量值
//!
//! ## 使用方式
//!
//! ```bash
//! cd ch11_burn_ai/02_burn_tensor
//! cargo run --release
//! ```
//!
use burn::backend::Wgpu;
use burn::prelude::*;

type B = Wgpu;

fn main() {
    let device: <B as Backend>::Device = Default::default();

    // === 各種建立 Tensor 的方法 ===
    // 1. 從陣列直接建立 (Rust 陣列 [f32; 3])
    // 透過 From trait 自動轉換為 TensorData
    let thrust = Tensor::<B, 1>::from_data([100.0, 200.0, 300.0], &device);
    // 直接 println! 張量，會顯示完整的資訊
    println!("推力 (Thrust): {}", thrust);
    // 2. 使用 from_floats (推薦用於 f32)
    // 這是 `from_data` 的一個便利包裝
    let velocity = Tensor::<B, 1>::from_floats([0.0, 5.0, 10.0], &device);
    // 3. 從 Vec 切片建立
    let temps_vec = vec![20.0, 25.0, 30.0, 35.0];
    // 傳入 &temps_vec[..] (一個 &[f32] 切片)
    let temperature = Tensor::<B, 1>::from_data(&temps_vec[..], &device);
    // 4. 明確使用 TensorData::from (最標準的作法)
    let altitude_data = TensorData::from([0.0, 1000.0, 2000.0]);
    let altitude = Tensor::<B, 1>::from_data(altitude_data, &device);
    // 5. 建立 2D tensor
    let matrix = Tensor::<B, 2>::from_data([[1.0, 2.0], [3.0, 4.0]], &device);
    // 6. 建立 Int 型態 tensor
    // 注意結尾的 <B, 1, Int>
    let sensor_ids = Tensor::<B, 1, Int>::from_data([1i32, 2, 3, 4], &device);
    // 7. ones_like 和 zeros_like
    // 建立一個與 'thrust' 形狀/型別/後端皆相同，但值為 1 的張量
    let ones = Tensor::<B, 1>::ones_like(&thrust);
    // 建立一個與 'matrix' 形狀/型別/後端皆相同，但值為 0 的張量
    let zeros = Tensor::<B, 2>::zeros_like(&matrix);

    // === 取得資料：to_data() vs into_data() ===
    // to_data()：保留 tensor
    let thrust_data = thrust.to_data();
    let thrust_dims = thrust.dims(); // tensor 仍可使用
    // into_data()：消耗 tensor
    let velocity_clone = velocity.clone();
    let velocity_data = velocity_clone.into_data();
    // velocity_clone 已無法使用

    // === 正確使用 as_slice ===
    // 正確：先儲存 TensorData
    let data = temperature.to_data();
    let slice = data.as_slice::<f32>().unwrap();
    println!("溫度資料: {:?}", slice);

    // 錯誤：chain 操作會造成借用錯誤
    // let slice = temperature.to_data().as_slice::<f32>().unwrap();

    // === 使用 to_vec 取得擁有權 ===
    // 可以安全地 chain
    let vec = altitude.to_data().to_vec::<f32>().unwrap();
    println!("高度資料 Vec: {:?}", vec);

    // === 處理不同資料型別 ===
    let int_data = sensor_ids.to_data();
    // 正確型別
    match int_data.as_slice::<i32>() {
        Ok(slice) => println!("感測器 ID: {:?}", slice),
        Err(e) => println!("轉換錯誤: {:?}", e),
    }

    // 錯誤型別示範
    match int_data.as_slice::<f32>() {
        Ok(_) => println!("不會執行"),
        Err(e) => println!("預期的型別錯誤: {:?}", e),
    }

    // === 使用迭代器 ===

    let matrix_data = matrix.to_data();
    println!("\n矩陣元素:");
    for value in matrix_data.iter::<f32>() {
        print!("{} ", value);
    }

    // === 檢查 shape 和 dtype ===
    println!("\n\n資料資訊:");
    println!("矩陣形狀: {:?}", matrix_data.shape); // [2, 2]
    println!("資料型別: {:?}", matrix_data.dtype); // F32

    // === 實用操作 ===

    // 取得純量值
    let sum = thrust.clone().sum();
    let sum_value = sum.into_scalar();
    println!("\n推力總和: {}", sum_value);
    // as_mut_slice 修改資料（需要 mut）
    let mut mutable_tensor = Tensor::<Wgpu, 1>::from_floats([1.0, 2.0, 3.0], &device);
    let mut mutable_data = mutable_tensor.to_data();
    if let Ok(slice) = mutable_data.as_mut_slice::<f32>() {
        slice[0] = 999.0;
        println!("修改後第一個元素: {}", slice[0]);
    }
}
