# WASM + Rust 實戰

> Rust 編譯至 WebAssembly 完整實戰指南。

## 🦀 Rust + WASM 開發

### 實戰教學
- [WebAssembly + Rust 實戰教學](data/rust-webassembly-complete-guide.md)

核心內容：
- 環境設置
- wasm-pack 工具鏈
- Rust 編譯至 WASM
- JavaScript 整合
- 實戰專案開發

## 🔌 Buttplug 專案實戰

### 開發流程
- [Buttplug WASM 開發流程](buttplug_wasm_flow.md)

核心內容：
- 專案架構設計
- Rust 核心邏輯
- WASM 封裝
- Web Bluetooth API 整合

### 函數呼叫
- [Buttplug 函數呼叫詳細整理](buttplug_function_calls.md)

核心內容：
- API 設計
- 跨語言呼叫
- 錯誤處理
- 生命週期管理

## 🛠️ wasm_bindgen 工具鏈

### 綁定工具
- [wasm_bindgen 作用整理](wasm_bindgen_guide.md)

核心內容：
- wasm_bindgen 原理
- JavaScript 類型轉換
- 異步函數支援
- 自定義類型綁定

### 分析工具
- [wasm-objdump 分析指南：深入 WASM 檔案與 Buttplug 依賴解析](wasm_dependency_analysis.md)
- [wasm-objdump 完整使用指南](wasm-objdump-guide.md)

核心內容：
- WASM 二進制分析
- 依賴關係解析
- 符號表檢查
- 程式碼大小優化

## 💡 Rust + WASM 實踐

### 基本設置
```toml
[package]
name = "wasm-example"
version = "0.1.0"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"
```

### 導出函數
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen]
pub struct Calculator {
    value: i32,
}

#[wasm_bindgen]
impl Calculator {
    #[wasm_bindgen(constructor)]
    pub fn new() -> Calculator {
        Calculator { value: 0 }
    }

    pub fn add(&mut self, n: i32) {
        self.value += n;
    }

    pub fn get(&self) -> i32 {
        self.value
    }
}
```

### JavaScript 使用
```javascript
import init, { add, Calculator } from './pkg/wasm_example.js';

async function run() {
  await init();

  // 呼叫函數
  console.log(add(5, 3)); // 8

  // 使用類
  const calc = new Calculator();
  calc.add(10);
  console.log(calc.get()); // 10
}
```

## 🔧 wasm-pack 工具

### 建置專案
```bash
# 建置 WASM
wasm-pack build --target web

# 建置並優化
wasm-pack build --release --target web

# 發布到 npm
wasm-pack publish
```

### 檢查產物
```bash
# 查看 WASM 模組資訊
wasm-objdump -h pkg/wasm_example_bg.wasm

# 查看匯出函數
wasm-objdump -x pkg/wasm_example_bg.wasm | grep export

# 分析檔案大小
ls -lh pkg/wasm_example_bg.wasm
```

**最後更新**: 2025-12-01
