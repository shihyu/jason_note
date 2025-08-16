# wasm_bindgen 作用整理

## 概述

`wasm_bindgen` 是 Rust 生態系統中用於簡化 WebAssembly 和 JavaScript 互操作的工具，它**不決定代碼是否編譯成 WASM**，而是負責**生成綁定代碼**讓兩種語言能夠互相調用。

## 主要作用

### 1. 🔗 JavaScript 函數綁定到 Rust

允許 Rust 代碼調用 JavaScript 函數和 Web API。

```rust
#[wasm_bindgen]
extern "C" {
    // 綁定 console.log
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
    
    // 綁定 alert
    fn alert(s: &str);
    
    // 綁定自定義 JavaScript 函數
    #[wasm_bindgen(js_namespace = myModule)]
    fn custom_function(x: i32) -> i32;
}
```

### 2. 🚀 Rust 函數導出到 JavaScript

讓 JavaScript 能夠調用 Rust 函數。

```rust
#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

### 3. 📦 結構體和類型綁定

支持複雜數據類型的雙向傳遞。

```rust
#[wasm_bindgen]
pub struct Person {
    name: String,
    age: u32,
}

#[wasm_bindgen]
impl Person {
    #[wasm_bindgen(constructor)]
    pub fn new(name: String, age: u32) -> Person {
        Person { name, age }
    }
    
    #[wasm_bindgen(getter)]
    pub fn name(&self) -> String {
        self.name.clone()
    }
}
```

### 4. 🌐 Web API 綁定

直接使用瀏覽器 API。

```rust
#[wasm_bindgen]
extern "C" {
    type Document;
    type Element;
    
    #[wasm_bindgen(js_namespace = document)]
    fn getElementById(id: &str) -> Element;
}
```

## 編譯行為對比

### ✅ 有 `#[wasm_bindgen]` 標記

```rust
#[wasm_bindgen]
pub fn public_function() -> i32 {
    42
}
```

- ✅ 編譯到 WASM 中
- ✅ **暴露給 JavaScript 調用**
- ✅ 生成 JavaScript 綁定代碼
- ✅ 包含在 TypeScript 定義中

### 🔒 沒有 `#[wasm_bindgen]` 標記

```rust
fn internal_helper() -> i32 {  // 沒有 #[wasm_bindgen]
    123
}

pub fn another_internal() -> String {  // 即使是 pub，沒有標記也不暴露
    "internal".to_string()
}
```

- ✅ **仍然會被編譯成 WASM**
- ❌ **不會暴露給 JavaScript**
- ❌ JavaScript 無法直接調用
- ✅ **只能在 Rust 內部使用**
- ✅ 可以被其他 Rust 函數調用

### 📝 混合使用示例

```rust
// 內部輔助函數 - 不暴露給 JS
fn calculate_internal(x: i32, y: i32) -> i32 {
    x * x + y * y
}

// 暴露給 JS 的公共 API
#[wasm_bindgen]
pub fn calculate_distance(x: i32, y: i32) -> f64 {
    let sum = calculate_internal(x, y);  // 調用內部函數
    (sum as f64).sqrt()
}
```

在這個例子中：
- `calculate_internal` 編譯到 WASM 但 JS 訪問不到
- `calculate_distance` 可以從 JS 調用，內部使用 `calculate_internal`

## 生成的產物

`wasm_bindgen` 會生成以下文件：

- **`.wasm`** - 實際的 WebAssembly 二進制文件
- **`_bg.js`** - JavaScript 膠水代碼
- **`.d.ts`** - TypeScript 類型定義
- **`.js`** - ES6 模塊包裝器

## 重要概念澄清

### ✅ 正確理解
- **所有 Rust 代碼都會編譯成 WASM**
- `#[wasm_bindgen]` 標記需要 JS 互操作的部分
- 沒有標記的函數仍在 WASM 中，但 JS 無法訪問
- 生成必要的綁定代碼和類型定義

### ❌ 常見誤解
- ~~`#[wasm_bindgen]` 決定是否編譯成 WASM~~
- ~~沒標記的函數不會被編譯~~
- ~~只有標記的代碼才在最終的 WASM 中~~

## 使用場景

| 場景 | 是否需要 `#[wasm_bindgen]` | 編譯結果 | JS 可訪問 |
|------|---------------------------|---------|-----------|
| 內部 Rust 函數 | ❌ | ✅ 編譯到 WASM | ❌ |
| 導出給 JS 的函數 | ✅ | ✅ 編譯到 WASM | ✅ |
| 調用 JS/Web API | ✅ | ✅ 編譯到 WASM | N/A |
| 結構體暴露給 JS | ✅ | ✅ 編譯到 WASM | ✅ |
| 純 Rust 邏輯處理 | ❌ | ✅ 編譯到 WASM | ❌ |

## 配置選項

```rust
// 命名空間綁定
#[wasm_bindgen(js_namespace = console)]

// 自定義 JS 名稱
#[wasm_bindgen(js_name = customName)]

// 構造函數
#[wasm_bindgen(constructor)]

// getter/setter
#[wasm_bindgen(getter, setter)]

// 靜態方法
#[wasm_bindgen(static_method_of = ClassName)]
```

## 總結

`wasm_bindgen` 是 Rust WebAssembly 開發的核心工具，主要負責：
- 🔄 **雙向綁定** - Rust ↔ JavaScript
- 📝 **代碼生成** - 自動生成膠水代碼  
- 🎯 **類型安全** - 提供 TypeScript 定義
- 🌐 **Web 整合** - 簡化瀏覽器 API 使用
- 🔒 **訪問控制** - 決定哪些函數暴露給 JavaScript

**關鍵要點**：所有 Rust 代碼都會編譯成 WASM，`#[wasm_bindgen]` 只是決定 JavaScript 能否訪問這些函數。