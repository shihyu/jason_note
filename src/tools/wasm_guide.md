# WebAssembly (WASM) 完整開發指南

## 目錄
- [基本概念](#基本概念)
- [工具鏈關係](#工具鏈關係)
- [編譯範例](#編譯範例)
- [效能對比](#效能對比)
- [常見誤解](#常見誤解)
- [最佳實踐](#最佳實踐)

## 基本概念

### WebAssembly 是什麼？
WebAssembly (WASM) 是一種低階的類似組語的語言，具有緊湊的二進制格式，為其他語言提供一個編譯目標，使它們能夠在 Web 上運行，同時提供接近原生的效能。

### 核心特性
- **安全性**：運行在沙盒環境中
- **效能**：接近原生代碼的執行速度
- **可移植性**：跨平台執行
- **語言無關**：支援多種編程語言
- **Web 標準**：W3C 標準，所有主流瀏覽器支持

### 記憶體模型
```javascript
// WASM 使用線性記憶體模型
const memory = new WebAssembly.Memory({
    initial: 10,  // 10 頁 (640KB)
    maximum: 100  // 最大 100 頁 (6.4MB)
});

// 每頁 = 64KB
// 記憶體是連續的，類似 C 的 malloc
```

### 類型系統
WASM 支援四種基本數值類型：
- `i32`: 32位整數
- `i64`: 64位整數  
- `f32`: 32位浮點數
- `f64`: 64位浮點數

## 工具鏈關係

### 基本關係圖
```
Source Code (Rust/C/C++)
        ↓
    Cargo.toml (配置)
        ↓
    cargo build (編譯)
        ↓
    wasm-pack (包裝)
        ↓
    WebAssembly + JS綁定
```

### Cargo 與 Cargo.toml
**Cargo** 是 Rust 的包管理工具和構建系統
**Cargo.toml** 是項目配置文件，定義：

```toml
[package]
name = "my-wasm-project"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]  # 生成動態庫供 WASM 使用

[dependencies]
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }

[dependencies.web-sys]
version = "0.3"
features = [
  "console",
  "Document",
  "Element",
  "HtmlElement",
  "Window",
]

[features]
default = ["console_error_panic_hook"]
console_error_panic_hook = ["console_error_panic_hook/dep"]
```

### wasm-pack 的作用
wasm-pack 是 cargo 的高層包裝，執行以下步驟：

1. **編譯 WASM**：`cargo build --target wasm32-unknown-unknown`
2. **生成綁定**：使用 wasm-bindgen 創建 JS/TS 接口
3. **優化**：使用 wasm-opt 優化二進制文件
4. **打包**：生成 npm 可用的包結構

### 參數說明

#### wasm-pack build 參數
```bash
# 開發模式（未優化，保留調試信息）
wasm-pack build --dev

# 禁用默認特性
wasm-pack build --no-default-features

# 指定目標
wasm-pack build --target web           # 適用於 ES6 模組
wasm-pack build --target nodejs       # 適用於 Node.js
wasm-pack build --target bundler      # 適用於 Webpack 等

# 輸出目錄
wasm-pack build --out-dir pkg

# 範圍（用於 npm 發布）
wasm-pack build --scope mycompany
```

## 編譯範例

### 1. 基本 Rust + WASM 設定

**Cargo.toml**:
```toml
[package]
name = "hello-wasm"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]

[dependencies]
wasm-bindgen = "0.2"

[dependencies.web-sys]
version = "0.3"
features = [
  "console",
]

[features]
default = ["console_error_panic_hook"]

[dependencies.console_error_panic_hook]
version = "0.1.6"
optional = true
```

**src/lib.rs**:
```rust
mod utils;

use wasm_bindgen::prelude::*;

// 導入 `console.log` 函數
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
}

// 定義一個宏來方便調用 `console.log`
macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

#[wasm_bindgen]
pub fn greet(name: &str) {
    console_log!("Hello, {}!", name);
}

#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 複雜運算示例
#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u32 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

// 處理數組
#[wasm_bindgen]
pub fn sum_array(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}
```

### 2. 編譯命令

```bash
# 初始化項目
cargo generate --git https://github.com/rustwasm/wasm-pack-template
cd my-wasm-project

# 開發版本編譯
wasm-pack build --dev

# 生產版本編譯
wasm-pack build --release

# 指定特定特性
wasm-pack build --no-default-features --features "web-feature"

# 針對不同目標
wasm-pack build --target web --out-dir pkg-web
wasm-pack build --target nodejs --out-dir pkg-node
```

### 3. JavaScript 使用

**在 Web 中使用**:
```javascript
import init, { greet, add, fibonacci } from './pkg/hello_wasm.js';

async function run() {
    // 初始化 WASM 模組
    await init();
    
    // 調用函數
    greet('World');
    console.log('2 + 3 =', add(2, 3));
    console.log('fibonacci(10) =', fibonacci(10));
}

run();
```

**在 Node.js 中使用**:
```javascript
const wasm = require('./pkg-node/hello_wasm.js');

// Node.js 版本通常是同步初始化
console.log('2 + 3 =', wasm.add(2, 3));
```

### 4. 高級範例：圖像處理

**Cargo.toml**:
```toml
[dependencies]
wasm-bindgen = "0.2"
js-sys = "0.3"
image = { version = "0.24", default-features = false, features = ["png", "jpeg"] }

[dependencies.web-sys]
version = "0.3"
features = [
  "console",
  "ImageData",
  "CanvasRenderingContext2d",
]
```

**src/lib.rs**:
```rust
use wasm_bindgen::prelude::*;
use wasm_bindgen::Clamped;
use web_sys::{CanvasRenderingContext2d, ImageData};

#[wasm_bindgen]
pub struct ImageProcessor {
    width: u32,
    height: u32,
    data: Vec<u8>,
}

#[wasm_bindgen]
impl ImageProcessor {
    #[wasm_bindgen(constructor)]
    pub fn new(width: u32, height: u32) -> ImageProcessor {
        ImageProcessor {
            width,
            height,
            data: vec![0; (width * height * 4) as usize],
        }
    }

    #[wasm_bindgen]
    pub fn apply_grayscale(&mut self) {
        for pixel in self.data.chunks_exact_mut(4) {
            let gray = (0.299 * pixel[0] as f64 
                      + 0.587 * pixel[1] as f64 
                      + 0.114 * pixel[2] as f64) as u8;
            pixel[0] = gray;
            pixel[1] = gray;
            pixel[2] = gray;
            // Alpha 通道保持不變
        }
    }

    #[wasm_bindgen]
    pub fn get_image_data(&self, ctx: &CanvasRenderingContext2d) -> Result<ImageData, JsValue> {
        ImageData::new_with_u8_clamped_array_and_sh(
            Clamped(&self.data),
            self.width,
            self.height,
        )
    }
}
```

## 效能對比

### Web 環境效能比較

| 技術 | 適用場景 | 效能 | 限制 |
|------|----------|------|------|
| **純 JavaScript** | DOM 操作、輕量運算 | 基準 | V8 優化限制 |
| **WebAssembly** | CPU 密集運算 | 2-10x 更快 | 調用邊界開銷 |
| **.so 庫** | ❌ 不支援 | N/A | 瀏覽器沙盒限制 |

### 手機環境效能比較

#### React Native / Hybrid Apps
```javascript
// .so 庫調用 (Android)
import { NativeModules } from 'react-native';
const { MyNativeModule } = NativeModules;

// ⭐ 效能最佳 - 直接 JNI 調用
MyNativeModule.computeHeavyTask(data)
    .then(result => console.log(result));

// WASM 調用
import wasmModule from './my_module.wasm';
// ⚠️ 需要額外的 runtime，效能較差
```

#### 原生 App
```java
// Android - 直接 JNI 調用
static {
    System.loadLibrary("mynative");
}
public native int computeTask(int[] data);
```

```swift
// iOS - 直接調用 C/C++ Framework
import MyNativeFramework
let result = MyNativeFramework.computeTask(data)
```

### 效能測試結果

| 環境 | .so 庫 | WASM | 效能比較 |
|------|--------|------|----------|
| **Web 瀏覽器** | ❌ | ✅ 良好 | WASM 唯一選擇 |
| **React Native** | ⭐ 極佳 | ⚠️ 受限 | .so 快 3-5x |
| **Android 原生** | ⭐ 極佳 | ❌ | .so 最優 |
| **iOS 原生** | ⭐ 極佳 | ❌ | Native 最優 |
| **Node.js** | ⭐ 極佳 | ✅ 良好 | .so 快 1.5-3x |

## 常見誤解

### ❌ 誤解 1：WASM 總是比 JavaScript 快
```javascript
// 錯誤：頻繁的小運算調用
for (let i = 0; i < 1000; i++) {
    wasmAdd(i, i + 1); // 每次調用都有邊界開銷
}

// 正確：批量處理
const results = wasmBatchAdd(array1, array2);
```

**解釋**：JS ↔ WASM 調用有開銷，小運算可能比純 JS 慢。

### ❌ 誤解 2：手機瀏覽器支援 .so 調用
```javascript
// 完全錯誤 - 手機瀏覽器仍是沙盒環境
loadLibrary('./native.so'); // ❌ 不可能
```

### ❌ 誤解 3：WASM 檔案大小不重要
```rust
// 錯誤：包含大量無用依賴
[dependencies]
tokio = "1.0"        // 異步 runtime，WASM 中無用
reqwest = "0.11"     // HTTP 客戶端，用 fetch API 即可
serde_json = "1.0"   // 如果只需簡單序列化

// 正確：最小化依賴
[dependencies]
wasm-bindgen = "0.2"
serde = { version = "1.0", features = ["derive"] }
```

### ❌ 誤解 4：所有運算都適合 WASM
```javascript
// 錯誤：DOM 操作用 WASM
wasm.updateElement(id, value); // 反而更慢

// 正確：分工合作
const processed = wasm.processData(rawData); // CPU 密集用 WASM
document.getElementById(id).value = processed; // DOM 操作用 JS
```

### ❌ 誤解 5：WASM 可以直接操作 DOM
```rust
// 錯誤理解 - WASM 無法直接訪問 DOM
// 需要通過 web-sys 綁定
use web_sys::{console, Document, Element, HtmlElement, Window};

#[wasm_bindgen]
pub fn update_dom(id: &str, text: &str) {
    let window = web_sys::window().unwrap();
    let document = window.document().unwrap();
    let element = document.get_element_by_id(id).unwrap();
    element.set_text_content(Some(text));
}
```

## 最佳實踐

### 1. 選擇合適的場景
**✅ 適合 WASM：**
- 數學密集運算（加密、圖像處理、物理模擬）
- 數據處理（排序、過濾、統計）
- 遊戲邏輯
- 音訊/視訊處理

**❌ 不適合 WASM：**
- DOM 操作
- 網絡請求
- 簡單的業務邏輯
- 頻繁的小運算

### 2. 優化編譯
```bash
# 生產環境優化
wasm-pack build --release --target web

# 進一步優化
wasm-opt -Oz -o optimized.wasm original.wasm

# 壓縮
gzip optimized.wasm
```

### 3. 記憶體管理
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct LargeData {
    data: Vec<f64>,
}

#[wasm_bindgen]
impl LargeData {
    #[wasm_bindgen(constructor)]
    pub fn new(size: usize) -> LargeData {
        LargeData {
            data: vec![0.0; size],
        }
    }
    
    // 提供明確的清理方法
    #[wasm_bindgen]
    pub fn free(self) {
        // Rust 會自動清理
        drop(self);
    }
}
```

### 4. 錯誤處理
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn safe_divide(a: f64, b: f64) -> Result<f64, JsValue> {
    if b == 0.0 {
        Err(JsValue::from_str("Division by zero"))
    } else {
        Ok(a / b)
    }
}
```

### 5. 調試技巧
```rust
// 開發環境啟用 panic hook
#[cfg(feature = "console_error_panic_hook")]
console_error_panic_hook::set_once();

// 日志輸出
web_sys::console::log_1(&format!("Debug: {}", value).into());
```

### 6. 性能監控
```javascript
// 測量 WASM 載入時間
console.time('WASM Load');
await init();
console.timeEnd('WASM Load');

// 測量函數執行時間
console.time('WASM Execution');
const result = wasmFunction(data);
console.timeEnd('WASM Execution');
```

## 總結

WebAssembly 是 Web 平台上實現高效能運算的重要技術，但需要：

1. **正確選擇使用場景**：CPU 密集型任務
2. **合理的架構設計**：JS 處理 I/O，WASM 處理運算
3. **適當的優化策略**：編譯優化、記憶體管理
4. **跨平台考量**：Web 用 WASM，Native App 用原生庫

記住：技術選型沒有銀彈，要根據具體需求和環境做出最佳選擇。