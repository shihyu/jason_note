# WebAssembly 編譯與載入完整流程

## 📋 目錄結構與檔案作用

```
wasm-demo/
├── .cargo/
│   └── config                    # Cargo 編譯設定（設定預設編譯目標）
│
├── src/
│   └── lib.rs                    # Rust 源碼（WASM 模組的業務邏輯）
│
├── Cargo.toml                    # Rust 專案配置（依賴、編譯類型）
├── build.js                      # 建置腳本（執行 Rust 編譯 + wasm-bindgen）
├── index.js                      # JavaScript 入口（載入並執行 WASM 模組）
├── webpack.config.js             # Webpack 打包配置（產生最終的 bundle）
├── package.json                  # Node.js 專案配置（建置指令定義）
└── Makefile                      # Make 自動化腳本（統一的建置介面）
```

---

## 🔄 完整編譯流程圖

```
┌─────────────────────────────────────────────────────────────────┐
│ 階段 1：開發者執行建置指令                                            │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        make build
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 階段 2：Makefile 調用 npm                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                   npm run build (package.json)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 階段 3：Node.js 執行建置腳本                                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                      node build.js
                              ↓
        ┌────────────────────┴────────────────────┐
        ↓                                         ↓
┌──────────────────┐                    ┌──────────────────┐
│ 步驟 3.1         │                    │ 步驟 3.2         │
│ cargo build      │                    │ wasm-bindgen     │
│ --release        │──產生 .wasm──────→│                  │
└──────────────────┘                    └──────────────────┘
        ↓                                         ↓
        │                                         │
        │  讀取 .cargo/config                     │
        │  發現 target = "wasm32-unknown-unknown" │
        │                                         │
        │  [Rust 編譯器 LLVM]                     │
        │         ↓                               │
        │  產生 WASM 二進位檔                      │
        │         ↓                               │
        │  target/wasm32-unknown-unknown/         │
        │    release/wasm_demo.wasm               │
        └────────────┬────────────────────────────┘
                     ↓
        [wasm-bindgen 產生 JavaScript 綁定]
                     ↓
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
wasm_demo.js  wasm_demo_bg.wasm  wasm_demo.d.ts
(JS綁定)      (優化後WASM)       (TypeScript類型)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 階段 4：Webpack 打包                                              │
└─────────────────────────────────────────────────────────────────┘
                     ↓
              webpack serve
                     ↓
    [讀取 webpack.config.js]
         entry: './index.js'
                     ↓
    [處理 index.js 中的 import]
         import('./wasm_demo')
                     ↓
    [Webpack 自動處理 WASM 模組]
    experiments: { asyncWebAssembly: true }
                     ↓
         產生 dist/ 目錄
                     ↓
    ┌────────────────┼────────────────┐
    ↓                ↓                ↓
dist/           dist/            dist/
index.html      bundle.js        *.wasm
(自動產生)      (打包後的JS)     (WASM模組)
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 階段 5：開發伺服器運行                                              │
└─────────────────────────────────────────────────────────────────┘
                     ↓
         http://localhost:8080
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│ 階段 6：瀏覽器載入與執行                                            │
└─────────────────────────────────────────────────────────────────┘
                     ↓
         [瀏覽器請求 index.html]
                     ↓
         [載入 bundle.js]
                     ↓
         [執行 index.js 中的程式碼]
                     ↓
    const wasm = import('./wasm_demo')
                     ↓
         [非同步載入 WASM 模組]
                     ↓
    [瀏覽器下載 .wasm 檔案]
                     ↓
    [WebAssembly.instantiate()]
                     ↓
    [WASM 模組初始化完成]
                     ↓
         wasm.then(m => m.main())
                     ↓
    [執行 Rust 編譯的 main 函數]
                     ↓
    [操作 DOM: 建立 <p> 元素]
                     ↓
    [顯示 "Hello from Rust"]
                     ↓
              ✅ 完成！
```

---

## 📄 各檔案詳細解析

### 1️⃣ `.cargo/config`
```toml
[build]
target = "wasm32-unknown-unknown"
```

**作用：**
- 設定 Cargo 的預設編譯目標
- 讓 `cargo build` 自動編譯成 WebAssembly
- 不需要每次手動加 `--target wasm32-unknown-unknown`

**為什麼需要：**
- 確保團隊成員編譯設定一致
- 簡化建置指令

---

### 2️⃣ `Cargo.toml`
```toml
[package]
name = "wasm-demo"
version = "0.1.0"
edition = "2018"

[lib]
crate-type = ["cdylib"]          # ← 關鍵：產生動態函式庫而非執行檔

[dependencies]
wasm-bindgen = "0.2.75"          # ← Rust ↔ JavaScript 橋接

[dependencies.web-sys]
version = "0.3.52"
features = ["Window", "Document", "Node", "HtmlElement", "Element"]
                                 # ← 提供瀏覽器 API 的 Rust 綁定
```

**作用：**
- **`crate-type = ["cdylib"]`**：告訴 Rust 編譯器產生 C 相容的動態函式庫（可被 JavaScript 呼叫）
- **`wasm-bindgen`**：處理 Rust 與 JavaScript 之間的型別轉換和函數綁定
- **`web-sys`**：提供瀏覽器 API（如 `document`, `window`）的 Rust 包裝

**如果沒有 `cdylib`：**
```toml
# 這樣會產生執行檔，無法被 JavaScript 載入
[[bin]]
name = "wasm-demo"
```

---

### 3️⃣ `src/lib.rs`
```rust
extern crate wasm_bindgen;
extern crate web_sys;

use wasm_bindgen::prelude::*;

#[wasm_bindgen]                    // ← 標記：此函數可被 JavaScript 呼叫
pub fn main() -> Result<(), JsValue> {
    let window = web_sys::window().unwrap();
    let document = window.document().unwrap();
    let body = document.body().unwrap();

    // 建立 <p> 元素
    let el = document.create_element("p")?;
    el.set_inner_html("Hello from Rust");

    // 加入到 <body>
    AsRef::<web_sys::Node>::as_ref(&body)
        .append_child(el.as_ref())?;
    Ok(())
}
```

**作用：**
- 定義可被 JavaScript 呼叫的 Rust 函數
- **`#[wasm_bindgen]`**：巨集標記，告訴 wasm-bindgen 為此函數產生 JavaScript 綁定
- **`web_sys` API**：在 Rust 中操作 DOM

**編譯後產生：**
- JavaScript 可以呼叫 `wasm.main()`
- 在瀏覽器中建立 DOM 元素

---

### 4️⃣ `build.js`
```javascript
const s = require('shelljs')

s.cd(__dirname)
s.exec('cargo build --release')      // 步驟 1：編譯 Rust → WASM
s.exec(
  'wasm-bindgen target/wasm32-unknown-unknown/release/wasm_demo.wasm --out-dir .'
)                                    // 步驟 2：產生 JavaScript 綁定
```

**執行流程：**

**步驟 1：`cargo build --release`**
- 讀取 `.cargo/config`，發現 `target = "wasm32-unknown-unknown"`
- 編譯 `src/lib.rs` 成 WebAssembly
- 產生：`target/wasm32-unknown-unknown/release/wasm_demo.wasm`

**步驟 2：`wasm-bindgen`**
- 讀取編譯好的 `.wasm` 檔案
- 分析 `#[wasm_bindgen]` 標記的函數
- 產生 JavaScript 綁定程式碼：

```
wasm_demo.js          ← JavaScript 綁定（可 import 的模組）
wasm_demo_bg.wasm     ← 優化後的 WASM 二進位檔
wasm_demo.d.ts        ← TypeScript 型別定義
wasm_demo_bg.wasm.d.ts
```

**wasm-bindgen 產生的 `wasm_demo.js` 範例：**
```javascript
// 自動產生的程式碼
export function main() {
    return wasm.main();  // 呼叫 WASM 中的 main 函數
}

async function load(module, imports) {
    // 載入 WASM 模組的邏輯
    const bytes = await module.arrayBuffer();
    const result = await WebAssembly.instantiate(bytes, imports);
    return result.instance;
}
```

---

### 🔗 `.cargo/config` 與 `build.js` 的關係與優先權

**問題：兩者都有指定 WASM 編譯目標,以哪個為主？**

**答案：`.cargo/config` 為主要配置來源**

#### 優先權判斷

**`.cargo/config` (Cargo 配置檔)**
```toml
[build]
target = "wasm32-unknown-unknown"
```

**作用：**
- 設定 Cargo 的**預設編譯目標**為 wasm32
- 這是 **Cargo 的官方配置機制**
- 會自動應用到所有在此專案下執行的 `cargo build` 指令
- 不需要每次手動指定 `--target` 參數

**影響範圍：**
- 專案層級的配置
- 所有團隊成員共享相同設定
- 確保編譯一致性

---

**`build.js` (建構腳本)**
```javascript
s.exec('cargo build --release')
```

**作用：**
- 執行編譯腳本
- 這裡的 `cargo build --release` **會自動繼承** `.cargo/config` 中定義的 target
- **等效於**：`cargo build --release --target wasm32-unknown-unknown`

**依賴關係：**
- `build.js` 依賴 `.cargo/config` 的設定
- 如果沒有 `.cargo/config`，則需要在 `build.js` 中明確指定 `--target`

---

#### 協同工作流程

```
步驟 1: Cargo 讀取配置
    ↓
.cargo/config 定義：
target = "wasm32-unknown-unknown"
    ↓
步驟 2: build.js 執行編譯
    ↓
cargo build --release
    ↓
步驟 3: Cargo 應用配置
    ↓
實際執行：
cargo build --release --target wasm32-unknown-unknown
    ↓
產生 WASM 檔案
```

---

#### 優先權規則

如果兩者設定衝突（例如 build.js 明確指定不同的 target），則以**命令列參數優先**：

```javascript
// build.js 中明確指定 target (會覆蓋 .cargo/config)
s.exec('cargo build --release --target x86_64-unknown-linux-gnu')
```

**優先權順序（高 → 低）：**
1. 命令列參數 (`--target` 明確指定)
2. `.cargo/config` 配置檔
3. Cargo 預設行為

---

#### 最佳實踐

**推薦做法：**
```toml
# .cargo/config - 定義預設 target
[build]
target = "wasm32-unknown-unknown"
```

```javascript
// build.js - 簡潔的腳本，繼承配置
s.exec('cargo build --release')
```

**優點：**
- ✅ 配置集中管理（在 `.cargo/config`）
- ✅ 建置腳本簡潔（不需重複指定參數）
- ✅ 團隊成員設定一致
- ✅ 易於維護

**避免：**
```javascript
// ❌ 不推薦：在 build.js 中重複指定 target
s.exec('cargo build --release --target wasm32-unknown-unknown')
// 這會造成配置分散，難以維護
```

---

#### 修改編譯目標的正確方式

**如果要修改編譯目標，應該優先修改 `.cargo/config`：**

```toml
# .cargo/config
[build]
target = "wasm32-wasi"  # 改成其他 WASM target
```

**而不是修改 build.js：**
```javascript
// ❌ 不建議這樣做
s.exec('cargo build --release --target wasm32-wasi')
```

---

#### 驗證當前配置

```bash
# 查看實際使用的編譯目標
cargo build --release --verbose

# 輸出會顯示：
# Compiling wasm-demo v0.1.0 (/path/to/project)
# Running `rustc ... --target wasm32-unknown-unknown ...`
```

---

### 5️⃣ `index.js`（JavaScript 入口）
```javascript
const wasm = import('./wasm_demo')   // ← 非同步載入 WASM 模組（返回 Promise）

wasm
  .then(m => {
    m.main()                         // ← 執行 Rust 編譯的 main 函數
  })
  .catch(console.error)
```

**執行流程：**

1. **`import('./wasm_demo')`**：
   - ES6 動態 import，非同步載入模組
   - Webpack 會處理這個 import，找到 `wasm_demo.js`
   - `wasm_demo.js` 內部會載入 `wasm_demo_bg.wasm`

2. **`.then(m => m.main())`**：
   - WASM 模組載入完成後
   - 呼叫 Rust 中的 `main()` 函數
   - 執行 DOM 操作（建立 `<p>` 元素）

**實際瀏覽器執行順序：**
```
index.js 執行
    ↓
發現 import('./wasm_demo')
    ↓
載入 wasm_demo.js
    ↓
wasm_demo.js 內部執行：
    fetch('wasm_demo_bg.wasm')
    ↓
    WebAssembly.instantiate(bytes)
    ↓
    返回 WASM 實例
    ↓
Promise 解析成功
    ↓
執行 m.main()
    ↓
Rust 程式碼執行（建立 DOM）
```

---

### 6️⃣ `webpack.config.js`
```javascript
const path = require('path')
const HtmlPlugin = require('html-webpack-plugin')

module.exports = {
  entry: './index.js',               // ← 入口檔案
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'bundle.js',           // ← 打包後的 JavaScript
  },
  plugins: [
    new HtmlPlugin({
      title: 'wasm demo',            // ← 自動產生 HTML
    }),
  ],
  mode: 'development',
  devtool: 'cheap-module-source-map',
  experiments: {
    asyncWebAssembly: true,          // ← 關鍵：啟用 WASM 支援
  },
}
```

**作用：**

1. **`entry: './index.js'`**：
   - Webpack 從 `index.js` 開始分析依賴關係
   - 發現 `import('./wasm_demo')` → 會一併處理 WASM 模組

2. **`experiments: { asyncWebAssembly: true }`**：
   - 啟用 Webpack 5 的實驗性 WASM 支援
   - 自動處理 `.wasm` 檔案的載入
   - 產生非同步載入的程式碼

3. **`HtmlPlugin`**：
   - 自動產生 `dist/index.html`
   - 自動注入 `<script src="bundle.js"></script>`

**產生的 `dist/index.html`：**
```html
<!DOCTYPE html>
<html>
  <head>
    <title>wasm demo</title>
  </head>
  <body>
    <script src="bundle.js"></script>
  </body>
</html>
```

---

### 7️⃣ `package.json`
```json
{
  "scripts": {
    "build": "node build.js",        // make build 會執行這個
    "serve": "webpack serve"         // make run 會執行這個
  }
}
```

**作用：**
- 定義 npm 腳本命令
- `npm run build`：執行 Rust 編譯 + wasm-bindgen
- `npm run serve`：啟動 Webpack 開發伺服器

---

### 8️⃣ `Makefile`
```makefile
build:
	@echo "==> 編譯 Rust + WebAssembly..."
	npm run build                     # → node build.js
	@echo "==> 編譯完成"

run: kill-port
	@echo "==> 啟動開發伺服器於 http://localhost:8080..."
	npm run serve                     # → webpack serve
```

**作用：**
- 提供統一的建置介面
- `make build`：編譯專案
- `make run`：啟動開發伺服器

---

## 🌐 瀏覽器載入與執行流程

### 完整的運行時序：

```
1. 使用者訪問 http://localhost:8080
      ↓
2. 瀏覽器請求 index.html
      ↓
3. 解析 HTML，發現 <script src="bundle.js">
      ↓
4. 下載並執行 bundle.js
      ↓
5. bundle.js 中執行 index.js 的程式碼
      ↓
6. 執行 import('./wasm_demo')
      ↓
7. 瀏覽器請求 wasm_demo.js
      ↓
8. wasm_demo.js 內部發起請求：
      fetch('wasm_demo_bg.wasm')
      ↓
9. 下載 .wasm 二進位檔案
      ↓
10. WebAssembly.instantiate(wasmBytes)
      ↓
11. WASM 模組編譯 + 實例化
      ↓
12. Promise 解析成功，返回模組實例
      ↓
13. 執行 m.main()
      ↓
14. Rust 程式碼執行：
    - 取得 window.document
    - 建立 <p> 元素
    - 設定內容 "Hello from Rust"
    - 加入到 <body>
      ↓
15. 使用者看到頁面顯示 "Hello from Rust"
```

---

## 🔍 關鍵技術點解析

### 1. 為什麼需要 `wasm-bindgen`？

**問題：** WASM 只支援數字類型（i32, i64, f32, f64），無法直接傳遞字串、物件

**解決：**
```rust
// ❌ 原生 WASM 無法這樣寫
#[no_mangle]
pub fn greet(name: String) -> String {  // 字串無法直接在 WASM 邊界傳遞
    format!("Hello, {}", name)
}

// ✅ wasm-bindgen 會處理型別轉換
#[wasm_bindgen]
pub fn greet(name: &str) -> String {    // 自動處理 Rust String ↔ JS String
    format!("Hello, {}", name)
}
```

**wasm-bindgen 產生的綁定程式碼（簡化版）：**
```javascript
export function greet(name) {
    // 1. 將 JS 字串寫入 WASM 記憶體
    const ptr = passStringToWasm(name);

    // 2. 呼叫 WASM 函數
    const result = wasm.greet(ptr, name.length);

    // 3. 從 WASM 記憶體讀取結果字串
    return getStringFromWasm(result);
}
```

### 2. 為什麼需要 `crate-type = ["cdylib"]`？

**不同的 crate-type 產生不同的輸出：**

| crate-type | 用途 | 輸出 |
|-----------|------|------|
| `bin` | 執行檔 | 作業系統可執行的程式 |
| `lib` / `rlib` | Rust 靜態函式庫 | 只能被其他 Rust 程式使用 |
| `dylib` | Rust 動態函式庫 | 只能被其他 Rust 程式使用 |
| **`cdylib`** | **C 相容動態函式庫** | **可被 C、JavaScript 等其他語言呼叫** |

**範例：**
```toml
# ❌ 如果用 rlib
[lib]
crate-type = ["rlib"]
# → 只能被其他 Rust 專案 import，JavaScript 無法使用

# ✅ 用 cdylib
[lib]
crate-type = ["cdylib"]
# → 產生 C ABI 相容的函式庫，JavaScript 可透過 FFI 呼叫
```

### 3. Webpack 如何處理 WASM？

**傳統方式（手動載入）：**
```javascript
// 需要手動 fetch + instantiate
fetch('module.wasm')
  .then(response => response.arrayBuffer())
  .then(bytes => WebAssembly.instantiate(bytes, imports))
  .then(result => {
      const wasm = result.instance.exports;
      wasm.main();
  });
```

**Webpack 5 方式（自動處理）：**
```javascript
// Webpack 自動處理所有載入邏輯
import('./wasm_demo').then(m => m.main());
```

**Webpack 配置的作用：**
```javascript
experiments: {
    asyncWebAssembly: true,   // 啟用 WASM 支援
}
```

這會讓 Webpack：
- 自動辨識 `.wasm` 檔案
- 產生非同步載入的程式碼
- 處理 WASM 模組的初始化
- 與 JavaScript 模組系統整合

---

## 🎯 完整建置指令解析

```bash
make build
```

**實際執行的命令展開：**

```bash
# 1. Makefile 執行
npm run build

# 2. package.json 中的 build 腳本
node build.js

# 3. build.js 中的第一個命令
cargo build --release

# 4. Cargo 讀取 .cargo/config，實際執行
cargo build --release --target wasm32-unknown-unknown

# 5. 編譯完成，產生
# target/wasm32-unknown-unknown/release/wasm_demo.wasm

# 6. build.js 中的第二個命令
wasm-bindgen target/wasm32-unknown-unknown/release/wasm_demo.wasm --out-dir .

# 7. 產生最終檔案
# wasm_demo.js
# wasm_demo_bg.wasm
# wasm_demo.d.ts
```

```bash
make run
```

**實際執行的命令展開：**

```bash
# 1. 先執行 kill-port（清理佔用的 port 8080）
lsof -ti:8080 | xargs kill -9

# 2. 啟動 Webpack 開發伺服器
npm run serve

# 3. package.json 中的 serve 腳本
webpack serve

# 4. Webpack 執行
# - 讀取 webpack.config.js
# - 從 index.js 開始打包
# - 處理 WASM 模組
# - 產生 dist/ 目錄
# - 啟動 HTTP 伺服器於 http://localhost:8080
```

---

## 📦 產生的檔案說明

### 編譯後的檔案結構：

```
wasm-demo/
├── target/
│   └── wasm32-unknown-unknown/
│       └── release/
│           └── wasm_demo.wasm        # Rust 編譯的原始 WASM
│
├── wasm_demo.js                      # wasm-bindgen 產生的 JS 綁定
├── wasm_demo_bg.wasm                 # wasm-bindgen 優化後的 WASM
├── wasm_demo.d.ts                    # TypeScript 型別定義
├── wasm_demo_bg.wasm.d.ts
│
└── dist/                             # Webpack 打包後的輸出
    ├── index.html                    # 自動產生的 HTML
    ├── bundle.js                     # 打包後的 JavaScript
    └── *.wasm                        # Webpack 複製的 WASM 檔案
```

### 各檔案的差異：

| 檔案 | 產生工具 | 用途 |
|------|---------|------|
| `target/.../wasm_demo.wasm` | Rust 編譯器 | 原始編譯輸出，含完整符號資訊 |
| `wasm_demo_bg.wasm` | wasm-bindgen | 優化後版本，移除不必要的符號 |
| `wasm_demo.js` | wasm-bindgen | JavaScript 綁定，處理型別轉換 |
| `dist/*.wasm` | Webpack | 最終部署版本，複製自 wasm_demo_bg.wasm |

---

## 🚀 最佳化與部署

### 生產環境建置：

```bash
# 1. 使用 release 模式編譯（已經在用）
cargo build --release

# 2. 優化 WASM 大小（可選）
wasm-opt -Oz -o output.wasm input.wasm

# 3. Webpack 生產模式
# 修改 webpack.config.js
mode: 'production',

# 4. 打包
webpack --mode production
```

### WASM 檔案大小優化：

```toml
# Cargo.toml 加入
[profile.release]
opt-level = "z"          # 優化大小
lto = true               # Link Time Optimization
codegen-units = 1        # 減少程式碼分割
strip = true             # 移除符號資訊
```

---

## 🐛 常見問題排查

### 1. WASM 無法載入

**症狀：** 瀏覽器報錯 `Failed to fetch wasm`

**檢查：**
```bash
# 確認檔案存在
ls -la wasm_demo_bg.wasm

# 檢查 Webpack 配置
# webpack.config.js 必須有：
experiments: {
    asyncWebAssembly: true,
}
```

### 2. 函數無法呼叫

**症狀：** `m.main is not a function`

**檢查：**
```rust
// src/lib.rs 必須有 #[wasm_bindgen] 標記
#[wasm_bindgen]  // ← 必須加這個
pub fn main() -> Result<(), JsValue> {
    // ...
}
```

### 3. 編譯目標錯誤

**症狀：** 產生了 ELF 執行檔而非 WASM

**檢查：**
```bash
# 確認 .cargo/config 存在且正確
cat .cargo/config
# 應顯示：
# [build]
# target = "wasm32-unknown-unknown"

# 或手動指定目標
cargo build --release --target wasm32-unknown-unknown
```

---

## 📚 延伸學習

### WASM 與 JavaScript 的記憶體共享

```rust
#[wasm_bindgen]
pub fn process_large_data(data: &[u8]) -> Vec<u8> {
    // WASM 和 JS 共享記憶體（Linear Memory）
    // wasm-bindgen 自動處理資料複製
    data.iter().map(|&x| x * 2).collect()
}
```

**實際運作：**
1. JavaScript 傳遞陣列
2. wasm-bindgen 將 JS Array 複製到 WASM 線性記憶體
3. Rust 處理資料
4. 結果複製回 JavaScript

### 多個 WASM 模組

```javascript
// 同時載入多個 WASM 模組
Promise.all([
    import('./wasm_demo'),
    import('./another_wasm_module'),
]).then(([demo, another]) => {
    demo.main();
    another.process();
});
```

---

## ✅ 總結

**編譯鏈：**
```
Rust 源碼 → Cargo 編譯 → WASM 二進位 → wasm-bindgen 綁定
→ Webpack 打包 → 瀏覽器載入 → 執行
```

**關鍵配置：**
1. `.cargo/config` → 設定編譯目標
2. `Cargo.toml` → `cdylib` + `wasm-bindgen`
3. `webpack.config.js` → `asyncWebAssembly: true`
4. `#[wasm_bindgen]` → 標記可匯出的函數

**執行流程：**
1. `make build` → 編譯 Rust + 產生綁定
2. `make run` → 啟動開發伺服器
3. 瀏覽器載入 HTML → 執行 bundle.js → 載入 WASM → 執行 Rust 程式碼
