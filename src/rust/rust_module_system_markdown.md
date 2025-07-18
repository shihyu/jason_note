# Rust 模組系統完整指南

## 概述

Rust 沒有像 C/C++ 那樣的 `.h` 標頭檔，但有更強大的模組系統。本指南將詳細介紹 Rust 的模組系統，包括模組組織、路徑引用和最佳實踐。

## C/C++ vs Rust 對比

| C/C++ | Rust | 說明 |
|-------|------|------|
| `.h` 標頭檔 | `.rs` 模組檔 | 都用來組織程式碼 |
| `#include` | `mod` + `use` | 引入其他檔案的內容 |
| `#ifndef` 防重複 | 自動防重複 | Rust 自動處理重複引入 |
| 前置宣告 | `pub` 關鍵字 | 控制可見性 |
| 預處理器 | `cfg` 屬性 | 條件編譯 |

## 專案結構範例

```
my_project/
├── Cargo.toml
└── src/
    ├── main.rs       # 程式入口點（crate root）
    ├── lib.rs        # 函式庫入口點
    ├── animals.rs    # 動物模組
    ├── swimming.rs   # 游泳相關模組
    └── animals/      # 子模組目錄
        ├── mod.rs    # 模組入口
        ├── fish.rs   # 魚類定義
        └── bird.rs   # 鳥類定義
```

## 路徑引用系統

### `crate` 關鍵字

`crate` 是 Rust 中的特殊關鍵字，代表**當前專案的根目錄**，類似於檔案系統中的絕對路徑。

#### 路徑引用方式

| 引用方式 | 語法 | 說明 | 類比 |
|----------|------|------|------|
| 絕對路徑 | `crate::` | 從專案根目錄開始 | 「從大樓1樓開始」 |
| 相對路徑 | `super::` | 上一層模組 | 「上一層樓」 |
| 當前模組 | `self::` | 同一模組內 | 「同一層樓」 |
| 直接引用 | 無前綴 | 同層級模組 | 「同一區域」 |

### 引用範例

```rust
// 絕對路徑（推薦）
use crate::swimming::CanSwim;
use crate::animals::Fish;
use crate::utils::helper::some_function;

// 相對路徑
use self::local_module::LocalStruct;    // 當前模組內
use super::parent_module::ParentStruct; // 父模組中

// 直接引用
use swimming::CanSwim;  // 同層級模組
```

## 完整程式碼範例

### main.rs (crate root)
```rust
// 聲明模組
mod animals;          // 對應 animals.rs 檔案
mod swimming;         // 對應 swimming.rs 檔案

// 使用模組中的項目
use animals::{Fish, Bird};
use swimming::CanSwim;

fn main() {
    let fish = Fish::new("小丑魚".to_string(), "小丑魚".to_string());
    let bird = Bird::new("企鵝".to_string(), "國王企鵝".to_string());
    
    fish.swim();
    bird.swim();
}
```

### swimming.rs
```rust
// 定義游泳相關的 trait

pub trait CanSwim {
    fn swim(&self);
}

pub trait CanDive {
    fn dive(&self, depth: f32);
}

// 提供預設實作
pub trait Aquatic {
    fn enter_water(&self) {
        println!("進入水中...");
    }
    
    fn exit_water(&self) {
        println!("離開水中...");
    }
}
```

### animals.rs
```rust
// 動物結構體定義

// 使用絕對路徑引用（推薦）
use crate::swimming::CanSwim;

pub struct Fish {
    pub name: String,
    pub species: String,
    pub fin_count: u8,
    pub max_depth: f32,
}

pub struct Bird {
    pub name: String,
    pub species: String,
    pub wing_span: f32,
    pub can_fly: bool,
}

impl Fish {
    pub fn new(name: String, species: String) -> Self {
        Fish {
            name,
            species,
            fin_count: 6,
            max_depth: 30.0,
        }
    }
}

impl Bird {
    pub fn new(name: String, species: String) -> Self {
        Bird {
            name,
            species,
            wing_span: 85.0,
            can_fly: false,
        }
    }
}

// 實作 trait
impl CanSwim for Fish {
    fn swim(&self) {
        println!("{}（{}）用 {} 片鰭游泳！最深可潛到 {} 公尺", 
                self.name, self.species, self.fin_count, self.max_depth);
    }
}

impl CanSwim for Bird {
    fn swim(&self) {
        if self.can_fly {
            println!("{}（{}）翼展 {} 公分，在水面划水游泳！", 
                    self.name, self.species, self.wing_span);
        } else {
            println!("{}（{}）是不會飛的鳥類，用腳划水游泳！", 
                    self.name, self.species);
        }
    }
}
```

## 子模組結構

### animals/mod.rs
```rust
// 子模組的入口點
pub mod fish;
pub mod bird;

// 重新導出供外部使用
pub use fish::Fish;
pub use bird::Bird;
```

### animals/fish.rs
```rust
use crate::swimming::CanSwim;

pub struct Fish {
    pub name: String,
    pub species: String,
}

impl Fish {
    pub fn new(name: String, species: String) -> Self {
        Fish { name, species }
    }
}

impl CanSwim for Fish {
    fn swim(&self) {
        println!("{}（{}）游泳中...", self.name, self.species);
    }
}
```

## 外部依賴管理

### Cargo.toml
```toml
[dependencies]
serde = { version = "1.0", features = ["derive"] }
tokio = { version = "1.0", features = ["full"] }
clap = { version = "4.0", features = ["derive"] }
```

### 使用外部 crate
```rust
// 外部依賴
use serde::{Serialize, Deserialize};
use std::collections::HashMap;

// 內部模組
use crate::animals::Fish;
use crate::swimming::CanSwim;

#[derive(Serialize, Deserialize, Debug)]
pub struct Animal {
    name: String,
    species: String,
}
```

## 條件編譯

### 功能開關
```rust
// 在 Cargo.toml 中定義 features
// [features]
// advanced = []

#[cfg(feature = "advanced")]
mod advanced_swimming {
    pub trait AdvancedSwimming {
        fn underwater_breathing(&self);
        fn deep_dive(&self, depth: f32);
    }
}

#[cfg(feature = "advanced")]
pub use advanced_swimming::AdvancedSwimming;
```

### 除錯/發佈模式
```rust
#[cfg(debug_assertions)]
fn debug_info() {
    println!("這是 debug 模式 - 啟用額外檢查");
}

#[cfg(not(debug_assertions))]
fn debug_info() {
    // release 模式下什麼都不做
}

// 平台特定編譯
#[cfg(target_os = "windows")]
fn platform_specific() {
    println!("Windows 平台");
}

#[cfg(target_os = "linux")]
fn platform_specific() {
    println!("Linux 平台");
}
```

## 複雜模組結構範例

```rust
// 深層模組中的引用
// src/ocean/creatures/fish.rs

use crate::swimming::CanSwim;              // 絕對路徑到根模組
use crate::ocean::environment::Water;      // 絕對路徑到其他模組
use super::super::habitat::DeepSea;        // 相對路徑到祖父模組
use super::mammal::Whale;                  // 相對路徑到兄弟模組

pub struct DeepSeaFish {
    name: String,
    depth: f32,
}

impl DeepSeaFish {
    pub fn new(name: String, depth: f32) -> Self {
        DeepSeaFish { name, depth }
    }
}
```

## 最佳實踐

### 1. 使用絕對路徑
```rust
// ✅ 推薦：清晰明確
use crate::swimming::CanSwim;
use crate::animals::Fish;

// ❌ 不推薦：容易混淆
use super::super::swimming::CanSwim;
```

### 2. 合理的可見性控制
```rust
// 公開給外部使用
pub struct Fish {
    pub name: String,        // 公開欄位
    species: String,         // 私有欄位
}

impl Fish {
    pub fn new(name: String, species: String) -> Self {  // 公開方法
        Fish { name, species }
    }
    
    fn internal_method(&self) {  // 私有方法
        // 內部邏輯
    }
}
```

### 3. 重新導出（Re-export）
```rust
// 在 lib.rs 中重新導出常用項目
pub use animals::{Fish, Bird};
pub use swimming::CanSwim;

// 這樣外部使用者可以直接：
// use my_crate::{Fish, CanSwim};
```

### 4. 模組組織原則
- 每個模組負責單一功能
- 相關功能放在同一模組
- 使用子模組組織複雜結構
- 合理使用 `pub` 控制可見性

## 為什麼選擇 `crate::`？

### 優勢

1. **清晰明確** - 一看就知道是從專案根開始
2. **避免混淆** - 區分內部模組和外部依賴
3. **重構友好** - 移動檔案時不需要修改路徑
4. **一致性** - 在任何模組中都使用相同的引用方式

### 範例對比

```rust
// 外部 crate vs 內部 crate
use serde::Serialize;           // 外部依賴
use std::collections::HashMap;  // 標準庫
use crate::animals::Fish;       // 你的專案內部模組
```

## 總結

Rust 的模組系統相比 C/C++ 的標頭檔有以下優勢：

- **自動防重複引入** - 不需要 `#ifndef` 護衛
- **更清晰的可見性** - `pub` 明確標示公開項目
- **依賴管理** - Cargo 自動處理依賴關係
- **編譯時檢查** - 模組錯誤在編譯時就會發現
- **更好的組織** - 模組系統更直觀和安全

**推薦做法：** 在跨模組引用時優先使用 `crate::`，這樣程式碼更清晰、更好維護！