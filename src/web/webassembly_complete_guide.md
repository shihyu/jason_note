# WebAssembly (WASM) 完整開發指南

## 目錄
- [基本概念](#基本概念)
- [工具鏈關係](#工具鏈關係)
- [Rust 編譯 WASM 語法](#rust-編譯-wasm-語法)
- [程式碼相容性](#程式碼相容性)
- [編譯範例](#編譯範例)
- [效能對比](#效能對比)
- [常見誤解](#常見誤解)
- [最佳實踐](#最佳實踐)
- [實際案例](#實際案例)

## 基本概念

### WebAssembly 是什麼？
WebAssembly (WASM) 是一種低階的類似組語的語言，具有緊湊的二進制格式，為其他語言提供一個編譯目標，使它們能夠在 Web 上運行，同時提供接近原生的效能。

### 核心特性
- **安全性**：運行在沙盒環境中
- **效能**：接近原生代碼的執行速度
- **可移植性**：跨平臺執行
- **語言無關**：支援多種編程語言
- **Web 標準**：W3C 標準，所有主流瀏覽器支持

### WASM 不是程式語言轉換

**重要區別**：
- **.so 檔案 → WASM**：❌ 不可能
- **原始碼 → WASM**：✅ 可行

```bash
# ❌ 無法直接轉換已編譯的二進制檔案
# .so 檔案是 x86-64 機器碼，WASM 是虛擬指令集

# ✅ 必須從原始碼重新編譯
emcc your_code.c -o output.wasm -s WASM=1
```

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

## Rust 編譯 WASM 語法

### 基本設定

#### Cargo.toml 配置
```toml
[package]
name = "my-wasm-project"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib"]  # 編譯成動態庫

[dependencies]
wasm-bindgen = "0.2"
```

### 函數匯出語法

#### 使用 wasm-bindgen (推薦)
```rust
use wasm_bindgen::prelude::*;

// 匯出基本函數
#[wasm_bindgen]
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// 匯出字串處理函數
#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}

// 匯出結構體
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
    
    #[wasm_bindgen]
    pub fn add(&mut self, x: i32) {
        self.value += x;
    }
    
    #[wasm_bindgen(getter)]
    pub fn value(&self) -> i32 {
        self.value
    }
}
```

#### JavaScript 互操作
```rust
use wasm_bindgen::prelude::*;

// JavaScript 導入
#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = console)]
    fn log(s: &str);
    
    #[wasm_bindgen(js_namespace = Math)]
    fn random() -> f64;
}

// 定義 console.log 巨集
macro_rules! console_log {
    ($($t:tt)*) => (log(&format_args!($($t)*).to_string()))
}

#[wasm_bindgen]
pub fn use_js_functions() {
    console_log!("Random number: {}", random());
}
```

### 重要概念澄清

#### `#[wasm_bindgen]` 的作用
```rust
// ✅ 所有程式碼都會編譯成 WASM
fn internal_function() -> i32 {
    42  // 這個函數也會編譯成 WASM，但不會匯出給 JavaScript
}

#[wasm_bindgen]
pub fn exported_function() -> i32 {
    internal_function()  // 這個函數會匯出給 JavaScript 使用
}
```

**關鍵點**：
- `#[wasm_bindgen]` **不決定**是否編譯成 WASM
- 它只決定是否**匯出**給 JavaScript 使用
- 整個 Rust 專案都會編譯成 WASM

## 程式碼相容性

### 並非所有程式碼都能轉成 WASM

**主要限制**：
1. **系統呼叫和平臺 API**
2. **檔案系統操作**
3. **多執行緒（部分支援）**
4. **內嵌組合語言**
5. **動態連結**

### ❌ 無法編譯成 WASM 的程式碼

#### 1. 系統呼叫和檔案 I/O
```rust
use std::fs;
use std::process::Command;

// ❌ 檔案系統操作
fn read_file() -> String {
    fs::read_to_string("config.txt").unwrap()  // 無法編譯
}

// ❌ 執行系統命令
fn run_command() {
    Command::new("ls").output().unwrap();  // 無法編譯
}

// ❌ 環境變數
fn get_env() {
    std::env::var("HOME").unwrap();  // 無法編譯
}
```

#### 2. 多執行緒
```rust
use std::thread;
use std::sync::Mutex;

// ❌ 標準執行緒
fn spawn_thread() {
    thread::spawn(|| {
        println!("Hello from thread!");
    });
}

// ❌ 同步原語
static COUNTER: Mutex<i32> = Mutex::new(0);  // 無法編譯
```

#### 3. 網路和 Socket
```rust
use std::net::{TcpListener, TcpStream, UdpSocket};

// ❌ TCP Socket
fn tcp_server() {
    let listener = TcpListener::bind("127.0.0.1:8080").unwrap();  // 無法編譯
}

// ❌ UDP Socket
fn udp_socket() {
    let socket = UdpSocket::bind("127.0.0.1:0").unwrap();  // 無法編譯
}
```

#### 4. 平臺特定程式碼
```rust
// ❌ 內嵌組合語言
#[cfg(target_arch = "x86_64")]
fn assembly_code() {
    unsafe {
        asm!("mov rax, 42");  // 無法編譯
    }
}

// ❌ Windows API
#[cfg(windows)]
extern "system" {
    fn GetCurrentProcessId() -> u32;  // 無法編譯
}
```

### ✅ 可以編譯成 WASM 的程式碼

#### 1. 純計算邏輯
```rust
use wasm_bindgen::prelude::*;

// ✅ 數學計算
#[wasm_bindgen]
pub fn fibonacci(n: u32) -> u64 {
    match n {
        0 => 0,
        1 => 1,
        _ => fibonacci(n - 1) + fibonacci(n - 2),
    }
}

// ✅ 字串處理
#[wasm_bindgen]
pub fn reverse_string(s: &str) -> String {
    s.chars().rev().collect()
}

// ✅ 陣列操作
#[wasm_bindgen]
pub fn sum_array(numbers: &[i32]) -> i32 {
    numbers.iter().sum()
}
```

#### 2. 資料結構和演算法
```rust
use wasm_bindgen::prelude::*;

// ✅ 排序演算法
#[wasm_bindgen]
pub fn quick_sort(mut arr: Vec<i32>) -> Vec<i32> {
    if arr.len() <= 1 {
        return arr;
    }
    
    let pivot = arr.len() / 2;
    let pivot_value = arr[pivot];
    arr.remove(pivot);
    
    let less: Vec<i32> = arr.iter().filter(|&&x| x < pivot_value).cloned().collect();
    let greater: Vec<i32> = arr.iter().filter(|&&x| x >= pivot_value).cloned().collect();
    
    let mut result = quick_sort(less);
    result.push(pivot_value);
    result.extend(quick_sort(greater));
    result
}
```

#### 3. 圖像和音訊處理
```rust
use wasm_bindgen::prelude::*;

// ✅ 圖像濾鏡
#[wasm_bindgen]
pub fn apply_grayscale(pixels: &mut [u8]) {
    for chunk in pixels.chunks_exact_mut(4) {
        let r = chunk[0] as f32;
        let g = chunk[1] as f32;
        let b = chunk[2] as f32;
        
        let gray = (0.299 * r + 0.587 * g + 0.114 * b) as u8;
        
        chunk[0] = gray;
        chunk[1] = gray;
        chunk[2] = gray;
        // chunk[3] 是 alpha，保持不變
    }
}

// ✅ 音訊處理
#[wasm_bindgen]
pub fn apply_echo(samples: &mut [f32], delay_samples: usize, decay: f32) {
    for i in delay_samples..samples.len() {
        samples[i] += samples[i - delay_samples] * decay;
    }
}
```

### 相容性總結表

| **可以編譯成 WASM** | **無法編譯成 WASM** |
|-------------------|-------------------|
| 純計算邏輯 | 系統呼叫 |
| 資料結構操作 | 檔案 I/O |
| 演算法實作 | 網路 Socket |
| 字串/陣列處理 | 多執行緒 |
| 數學運算 | 平臺特定 API |
| 遊戲邏輯 | 環境變數存取 |
| 圖像/音訊處理 | 行程管理 |
| 加密/壓縮 | 硬體直接存取 |

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
# 安裝目標平臺
rustup target add wasm32-unknown-unknown

# 初始化項目
cargo generate --git https://github.com/rustwasm/wasm-pack-template
cd my-wasm-project

# 基本編譯
cargo build --target wasm32-unknown-unknown --release

# 使用 wasm-pack (推薦)
cargo install wasm-pack

# 開發版本編譯
wasm-pack build --dev

# 生產版本編譯
wasm-pack build --release

# 指定特定特性
wasm-pack build --no-default-features --features "web-feature"

# 針對不同目標
wasm-pack build --target web --out-dir pkg-web
wasm-pack build --target nodejs --out-dir pkg-node
wasm-pack build --target bundler    # 打包工具 (webpack等)
wasm-pack build --target no-modules # 全域變數
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

### 🧠 概念誤解

#### 1. 「WASM 會取代 JavaScript」
```javascript
// ❌ 誤解：WASM 要完全取代 JS
// ✅ 實際：WASM 和 JS 協作

// JavaScript 負責 DOM 操作
document.getElementById('canvas').addEventListener('click', (e) => {
    // WASM 負責密集計算
    const result = wasm.heavy_computation(e.clientX, e.clientY);
    // JS 負責更新 UI
    updateDisplay(result);
});
```

#### 2. 語言支援誤解
```markdown
✅ 容易編譯：Rust, C/C++, AssemblyScript
⚠️ 需要工具：Go, Python (via Pyodide)
❌ 困難/不支援：Java, C#（部分支援）, PHP, Ruby
```

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

### 🔧 技術誤解

#### 3. 記憶體管理混淆
```rust
use wasm_bindgen::prelude::*;

// ❌ 誤解：JS 會自動回收 Rust 記憶體
#[wasm_bindgen]
pub fn create_data() -> *mut u8 {
    let data = vec![0u8; 1000];
    let ptr = data.as_mut_ptr();
    std::mem::forget(data);  // 記憶體洩漏！
    ptr
}

// ✅ 正確：明確管理記憶體
#[wasm_bindgen]
pub struct DataBuffer {
    data: Vec<u8>,
}

#[wasm_bindgen]
impl DataBuffer {
    #[wasm_bindgen(constructor)]
    pub fn new(size: usize) -> DataBuffer {
        DataBuffer {
            data: vec![0; size],
        }
    }
    
    // 明確的清理方法
    #[wasm_bindgen]
    pub fn free(self) {
        // Rust 的 Drop trait 會自動清理
    }
}
```

#### 4. 效能期望不實際
```rust
// ❌ 誤解：WASM 總是比 JS 快
#[wasm_bindgen]
pub fn simple_addition(a: i32, b: i32) -> i32 {
    a + b  // 對簡單操作，JS 可能更快（JIT 優化）
}

// ✅ WASM 適合：密集計算
#[wasm_bindgen]
pub fn matrix_multiplication(a: &[f64], b: &[f64], size: usize) -> Vec<f64> {
    // 大量計算，WASM 顯著更快
    let mut result = vec![0.0; size * size];
    for i in 0..size {
        for j in 0..size {
            for k in 0..size {
                result[i * size + j] += a[i * size + k] * b[k * size + j];
            }
        }
    }
    result
}
```

### 🌐 瀏覽器兼容性

#### 5. 支援性檢查
```javascript
// ✅ 檢查支援性
if (typeof WebAssembly === 'object') {
    // 基本 WASM 支援
    import('./pkg/my_wasm.js').then(wasm => {
        // 使用 WASM
    });
} else {
    // 降級到 JS 實作
    console.log('WASM not supported, using JS fallback');
}

// ⚠️ 新功能需要特別檢查
if (WebAssembly.instantiateStreaming) {
    // 支援串流編譯
} else {
    // 使用傳統方式
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

// 日誌輸出
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

### 🔒 安全性

#### 9. 沙盒安全性
```rust
// ⚠️ WASM 沙盒有限制，但不是萬能的
#[wasm_bindgen]
pub fn potential_issue(size: usize) -> Vec<u8> {
    // 惡意輸入可能造成記憶體耗盡
    if size > 1_000_000_000 {
        panic!("Size too large!");  // 但這不會防止所有攻擊
    }
    vec![0; size]
}

// ✅ 更好的防護
#[wasm_bindgen]
pub fn safe_allocation(size: usize) -> Option<Vec<u8>> {
    const MAX_SIZE: usize = 10_000_000;  // 10MB 限制
    if size > MAX_SIZE {
        return None;
    }
    Some(vec![0; size])
}
```

### 🎯 最佳實踐

#### 10. 開發工作流程
```bash
# ❌ 直接用 cargo 編譯 WASM
cargo build --target wasm32-unknown-unknown

# ✅ 使用專門工具
wasm-pack build --target web
wasm-pack build --target bundler
wasm-pack build --target nodejs

# 🔧 進階優化
wasm-opt -Oz output.wasm -o optimized.wasm  # 進一步壓縮
```

#### 11. 除錯方法
```javascript
// ❌ 誤解：WASM 難以除錯
// ✅ 實際：有多種除錯方式

// 1. 在 Rust 中添加日誌
use web_sys::console;
console::log_1(&"Debug message".into());

// 2. 使用瀏覽器開發者工具的 WASM 支援
// 3. 使用 wasm-pack 的除錯模式
// wasm-pack build --dev
```

### 📦 部署和載入

#### 7. bundler 整合
```javascript
// ❌ 錯誤的載入方式
import wasmModule from './my_module.wasm';  // 不會工作

// ✅ 正確的方式
import init, { my_function } from './pkg/my_module.js';

async function run() {
    await init();  // 必須先初始化
    const result = my_function(42);
}
```

#### 8. 檔案大小優化
```rust
// ✅ 優化建議
// 1. 使用 wee_alloc 替代預設分配器
extern crate wee_alloc;
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

// 2. 在 Cargo.toml 中啟用 LTO 和大小優化
// [profile.release]
// lto = true
// opt-level = "s"  // 優化大小
// codegen-units = 1
```

### 🚀 未來發展

#### 12. WASM 的發展方向
```markdown
✅ 實際趨勢：
- 垃圾收集支援（WasmGC）
- SIMD 指令支援
- 異常處理改進
- WASI（系統介面標準化）

❌ 常見誤解：
- "WASM 會完全取代 JavaScript"
- "所有網站都會用 WASM"
- "WASM 只適用於網頁"
```

## 實際案例

### Buttplug 專案

#### 依賴版本衝突解決

當遇到 `getrandom` 版本衝突時：

```bash
# 檢查依賴樹
cargo tree | grep getrandom

# 強制統一版本
[patch.crates-io]
getrandom = { version = "0.2.16", features = ["js"] }

# 清理並重建
cargo clean
wasm-pack build --target web --no-default-features --features "wasm"
```

#### Buttplug WASM 編譯
```bash
# 正確的編譯命令
wasm-pack build --target web --no-default-features --features "wasm,client,serialize-json"
```

## 總結

**核心原則**：
1. **正確選擇使用場景**：CPU 密集型任務
2. **合理的架構設計**：JS 處理 I/O，WASM 處理運算
3. **適當的優化策略**：編譯優化、記憶體管理
4. **跨平臺考量**：Web 用 WASM，Native App 用原生庫
5. WASM 適合純計算、不依賴系統資源的程式碼
6. `#[wasm_bindgen]` 控制匯出，不控制編譯
7. WASM 和 JavaScript 是協作關係，不是替代關係
8. 記憶體管理需要特別注意
9. 效能優勢主要體現在密集計算場景

**最佳實踐**：
- 使用 `wasm-pack` 而非 `cargo` 直接編譯
- 明確管理記憶體生命週期
- 適當的錯誤處理和邊界檢查
- 針對目標平臺優化編譯設定

記住：技術選型沒有銀彈，要根據具體需求和環境做出最佳選擇。WebAssembly 是強大的工具，但瞭解其限制和適用場景同樣重要。它不是銀彈，而是現代 Web 開發工具箱中的一個重要組件。