# WebAssembly (WASM) 完整知識指南

## 目錄
- [基本概念](#基本概念)
- [Rust 編譯 WASM 語法](#rust-編譯-wasm-語法)
- [程式碼相容性](#程式碼相容性)
- [常見誤解與最佳實踐](#常見誤解與最佳實踐)

---

## 基本概念

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

### 並非所有程式碼都能轉成 WASM

**主要限制**：
1. **系統呼叫和平台 API**
2. **檔案系統操作**
3. **多執行緒（部分支援）**
4. **內嵌組合語言**
5. **動態連結**

---

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

### 編譯命令

```bash
# 安裝目標平台
rustup target add wasm32-unknown-unknown

# 基本編譯
cargo build --target wasm32-unknown-unknown --release

# 使用 wasm-pack (推薦)
cargo install wasm-pack

# 編譯成不同目標
wasm-pack build --target web        # 瀏覽器 ES6 模組
wasm-pack build --target bundler    # 打包工具 (webpack等)
wasm-pack build --target nodejs     # Node.js
wasm-pack build --target no-modules # 全域變數
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

---

## 程式碼相容性

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

#### 4. 平台特定程式碼
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

#### 4. 遊戲邏輯
```rust
use wasm_bindgen::prelude::*;

// ✅ 遊戲狀態
#[wasm_bindgen]
pub struct GameState {
    player_x: f32,
    player_y: f32,
    score: u32,
}

#[wasm_bindgen]
impl GameState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> GameState {
        GameState {
            player_x: 0.0,
            player_y: 0.0,
            score: 0,
        }
    }
    
    #[wasm_bindgen]
    pub fn update(&mut self, delta_time: f32) {
        // 更新遊戲邏輯
        self.player_x += 50.0 * delta_time;
    }
    
    #[wasm_bindgen]
    pub fn check_collision(&self, x: f32, y: f32) -> bool {
        let distance = ((self.player_x - x).powi(2) + (self.player_y - y).powi(2)).sqrt();
        distance < 20.0
    }
}
```

#### 5. 加密和壓縮
```rust
use wasm_bindgen::prelude::*;

// ✅ 簡單加密
#[wasm_bindgen]
pub fn caesar_cipher(text: &str, shift: u8) -> String {
    text.chars()
        .map(|c| {
            if c.is_ascii_alphabetic() {
                let base = if c.is_ascii_lowercase() { b'a' } else { b'A' };
                let shifted = (c as u8 - base + shift) % 26 + base;
                shifted as char
            } else {
                c
            }
        })
        .collect()
}

// ✅ 壓縮演算法
#[wasm_bindgen]
pub fn run_length_encode(data: &[u8]) -> Vec<u8> {
    let mut result = Vec::new();
    if data.is_empty() {
        return result;
    }
    
    let mut current = data[0];
    let mut count = 1u8;
    
    for &byte in &data[1..] {
        if byte == current && count < 255 {
            count += 1;
        } else {
            result.push(count);
            result.push(current);
            current = byte;
            count = 1;
        }
    }
    
    result.push(count);
    result.push(current);
    result
}
```

### 相容性總結表

| **可以編譯成 WASM** | **無法編譯成 WASM** |
|-------------------|-------------------|
| 純計算邏輯 | 系統呼叫 |
| 資料結構操作 | 檔案 I/O |
| 演算法實作 | 網路 Socket |
| 字串/陣列處理 | 多執行緒 |
| 數學運算 | 平台特定 API |
| 遊戲邏輯 | 環境變數存取 |
| 圖像/音訊處理 | 行程管理 |
| 加密/壓縮 | 硬體直接存取 |

---

## 常見誤解與最佳實踐

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

#### 6. 多執行緒支援
```rust
// ❌ 誤解：WASM 不支援多執行緒
// ✅ 實際：支援，但有限制

// 需要特殊編譯設定
// RUSTFLAGS='-C target-feature=+atomics,+bulk-memory,+mutable-globals'

use wasm_bindgen::prelude::*;
use std::sync::Arc;
use std::sync::atomic::{AtomicI32, Ordering};

#[wasm_bindgen]
pub struct SharedCounter {
    counter: Arc<AtomicI32>,
}

// 但需要 SharedArrayBuffer 支援（安全限制）
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

---

## 實際案例：Buttplug 專案

### 依賴版本衝突解決

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

### Buttplug WASM 編譯
```bash
# 正確的編譯命令
wasm-pack build --target web --no-default-features --features "wasm,client,serialize-json"
```

---

## 總結

**核心原則**：
1. WASM 適合純計算、不依賴系統資源的程式碼
2. `#[wasm_bindgen]` 控制匯出，不控制編譯
3. WASM 和 JavaScript 是協作關係，不是替代關係
4. 記憶體管理需要特別注意
5. 效能優勢主要體現在密集計算場景

**最佳實踐**：
- 使用 `wasm-pack` 而非 `cargo` 直接編譯
- 明確管理記憶體生命週期
- 適當的錯誤處理和邊界檢查
- 針對目標平台優化編譯設定

WebAssembly 是強大的工具，但了解其限制和適用場景同樣重要。它不是銀彈，而是現代 Web 開發工具箱中的一個重要組件。
