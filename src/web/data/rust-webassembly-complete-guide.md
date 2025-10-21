# WebAssembly + Rust 實戰教學

這是一個使用 Rust 編譯成 WebAssembly 並在瀏覽器中運行的完整範例專案。本文將介紹如何使用 `wasm-bindgen` 讓 Rust 程式碼與 JavaScript 互動，並操作 DOM。

## 目錄

- [專案結構](#專案結構)
- [環境需求](#環境需求)
- [安裝步驟](#安裝步驟)
- [快速開始](#快速開始)
- [核心技術解析](#核心技術解析)
- [程式碼說明](#程式碼說明)
- [編譯流程](#編譯流程)
- [開發伺服器](#開發伺服器)
- [cargo install vs cargo add](#cargo-install-vs-cargo-add)
- [常見問題](#常見問題)

## 專案結構

```
wasm-demo/
├── src/
│   └── lib.rs              # Rust 原始碼
├── .cargo/
│   └── config              # Cargo 編譯設定
├── Cargo.toml              # Rust 專案設定
├── package.json            # Node.js 專案設定
├── build.js                # 編譯腳本
├── index.js                # JavaScript 入口
├── webpack.config.js       # Webpack 設定
├── Makefile               # 方便的指令集合
├── wasm_demo.js           # 生成的 JS 綁定（編譯後產生）
├── wasm_demo_bg.js        # 生成的 JS 綁定實作（編譯後產生）
└── wasm_demo_bg.wasm      # 編譯好的 WebAssembly（編譯後產生）
```

## 環境需求

- **Rust** 工具鏈（rustup + cargo）
- **Node.js** 和 npm/yarn
- **wasm-bindgen-cli** 工具

## 安裝步驟

### 1. 安裝 Rust

如果尚未安裝 Rust，請執行：

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

### 2. 添加 WebAssembly 編譯目標

```bash
rustup target add wasm32-unknown-unknown
```

### 3. 安裝專案依賴

使用 Makefile 一鍵安裝所有依賴：

```bash
make install
```

這會自動：
- 安裝 Node.js 依賴（webpack、webpack-dev-server 等）
- 安裝 `wasm-bindgen-cli`（如果尚未安裝）

或手動安裝：

```bash
# 安裝 Node.js 依賴
npm install

# 安裝 wasm-bindgen-cli
cargo install wasm-bindgen-cli
```

## 快速開始

### 方式一：使用 Makefile（推薦）

```bash
# 查看所有可用指令
make help

# 編譯專案
make build

# 啟動開發伺服器（自動處理 port 衝突）
make run

# 清理生成檔案
make clean
```

### 方式二：使用 npm scripts

```bash
# 編譯
npm run build

# 啟動開發伺服器
npm run serve
```

### 訪問應用

開發伺服器啟動後，瀏覽器訪問：
```
http://localhost:8080
```

你將看到網頁上顯示 "Hello from Rust"，這段文字是由 Rust 程式碼透過 WebAssembly 在瀏覽器中動態產生的。

## 核心技術解析

### 1. wasm-bindgen

`wasm-bindgen` 是 Rust 與 JavaScript 之間的橋樑，負責：

- **類型轉換**：在 Rust 和 JavaScript 之間自動轉換資料型別
- **函數綁定**：讓 JavaScript 可以呼叫 Rust 函數
- **DOM 操作**：透過 `web-sys` crate 讓 Rust 可以操作瀏覽器 DOM

### 2. web-sys

`web-sys` 提供了 Web API 的 Rust 綁定，包括：
- `Window`、`Document`
- `Element`、`Node`、`HtmlElement`
- 以及其他瀏覽器 API

### 3. 編譯目標

`.cargo/config` 設定了預設的編譯目標：

```toml
[build]
target = "wasm32-unknown-unknown"
```

這告訴 Cargo 編譯成 WebAssembly 格式。

## 程式碼說明

### Rust 程式碼（src/lib.rs）

```rust
extern crate wasm_bindgen;
extern crate web_sys;

use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub fn main() -> Result<(), JsValue> {
    // 獲取 window 物件
    let window = web_sys::window().unwrap();

    // 獲取 document 物件
    let document = window.document().unwrap();

    // 獲取 body 元素
    let body = document.body().unwrap();

    // 建立一個新的 <p> 元素
    let el = document.create_element("p")?;

    // 設定元素的內容
    el.set_inner_html("Hello from Rust");

    // 將元素附加到 body
    AsRef::<web_sys::Node>::as_ref(&body).append_child(el.as_ref())?;

    Ok(())
}
```

**關鍵點說明：**

1. **`#[wasm_bindgen]` 宏**：標記這個函數應該被導出給 JavaScript 使用
2. **`JsValue`**：JavaScript 值的 Rust 表示，用於錯誤處理
3. **DOM 操作**：
   - `window()` → 獲取瀏覽器視窗物件
   - `document()` → 獲取文檔物件
   - `create_element()` → 建立新的 HTML 元素
   - `append_child()` → 將元素加入到 DOM 樹
4. **型別轉換**：使用 `AsRef` trait 將 `HtmlElement` 轉換為 `Node` 類型

### JavaScript 入口（index.js）

```javascript
const wasm = import('./wasm_demo')

wasm
  .then(m => {
    m.main()  // 呼叫 Rust 導出的 main 函數
  })
  .catch(console.error)
```

這段程式碼：
1. 動態 import WebAssembly 模組
2. 模組載入完成後呼叫 Rust 的 `main` 函數
3. 處理可能發生的錯誤

### 編譯腳本（build.js）

```javascript
const s = require('shelljs')

s.cd(__dirname)
// 編譯 Rust 成 WebAssembly
s.exec('cargo build --release')

// 使用 wasm-bindgen 產生 JavaScript 綁定
s.exec(
  'wasm-bindgen target/wasm32-unknown-unknown/release/wasm_demo.wasm --out-dir .'
)
```

**編譯流程：**
1. **Cargo 編譯**：將 Rust 程式碼編譯成 `.wasm` 檔案
2. **wasm-bindgen 處理**：生成 JavaScript 綁定程式碼（`wasm_demo.js` 和 `wasm_demo_bg.js`）

### Webpack 設定（webpack.config.js）

```javascript
const path = require('path')
const HtmlPlugin = require('html-webpack-plugin')

module.exports = {
  entry: './index.js',
  output: {
    path: path.join(__dirname, 'dist'),
    filename: 'bundle.js',
  },
  plugins: [
    new HtmlPlugin({
      title: 'wasm demo',
    }),
  ],
  mode: 'development',
  devtool: 'cheap-module-source-map',
  experiments: {
    asyncWebAssembly: true,  // 啟用 WebAssembly 支援
  },
}
```

**關鍵設定：**
- `experiments.asyncWebAssembly: true`：啟用 Webpack 5 的 WebAssembly 支援
- `HtmlPlugin`：自動產生 HTML 檔案

## 編譯流程

完整的編譯流程如下：

```
src/lib.rs (Rust 源碼)
    ↓
[cargo build --release]
    ↓
target/wasm32-unknown-unknown/release/wasm_demo.wasm
    ↓
[wasm-bindgen]
    ↓
wasm_demo.js + wasm_demo_bg.js + wasm_demo_bg.wasm
    ↓
[webpack]
    ↓
dist/bundle.js + dist/index.html
```

### 生成的檔案說明

編譯後會產生以下檔案：

1. **wasm_demo_bg.wasm** (29KB)：編譯好的 WebAssembly 二進位檔案
2. **wasm_demo.js** (179 bytes)：ES6 模組入口，負責初始化
3. **wasm_demo_bg.js** (4.3KB)：JavaScript 綁定實作，包含：
   - 記憶體管理函數
   - 類型轉換邏輯
   - Web API 綁定（`__wbg_*` 函數）
   - 導出的 `main()` 函數
4. **wasm_demo.d.ts** 和 **wasm_demo_bg.wasm.d.ts**：TypeScript 型別定義

## 開發伺服器

### 使用 Makefile

```bash
# 啟動開發伺服器（預設 port 8080）
make run

# 或
make serve

# 指定不同的 port
PORT=3000 make run
```

Makefile 會自動：
1. 檢查並終止佔用 port 的進程
2. 啟動 webpack-dev-server
3. 開啟熱重載功能

### 手動啟動

```bash
npm run serve
```

開發伺服器提供：
- 熱重載（Hot Reload）
- Source Map 支援
- 自動產生 HTML

## cargo install vs cargo add

在開發 WebAssembly 專案時，新手常常會混淆 `cargo install` 和 `cargo add` 的用途。以下詳細說明兩者的區別。

### 📦 `cargo install wasm-bindgen-cli`

#### 這是什麼？
- **命令行工具（CLI Tool）**
- 全局安裝到您的系統

#### 做什麼用？
```bash
# 安裝後可以在終端使用 wasm-bindgen 命令
$ wasm-bindgen --help

# 用來處理編譯後的 WASM 檔案
$ wasm-bindgen target/wasm32-unknown-unknown/release/my_project.wasm \
  --out-dir ./pkg \
  --target web
```

#### 安裝位置
```
~/.cargo/bin/wasm-bindgen  ← 全局工具
```

---

### 📚 `cargo add wasm-bindgen web-sys`

#### 這是什麼？
- **專案依賴庫（Library Dependencies）**
- 添加到當前專案的 `Cargo.toml`

#### 做什麼用？
```rust
// 在 Rust 代碼中使用這些庫
use wasm_bindgen::prelude::*;
use web_sys::console;

#[wasm_bindgen]
pub fn greet(name: &str) {
    console::log_1(&format!("Hello, {}!", name).into());
}
```

#### 安裝位置
```
your-project/
├── Cargo.toml  ← 添加依賴到這裡
└── src/
    └── lib.rs  ← 代碼中使用這些庫
```

---

### 🎯 清楚的對比

| 項目 | `cargo install` | `cargo add` |
|------|-----------------|-------------|
| **類型** | 命令行工具 | 程式庫 |
| **作用範圍** | 全局（整個系統） | 單一專案 |
| **安裝次數** | 一次（全局） | 每個專案都需要 |
| **用途** | 編譯/處理 WASM | 在代碼中使用 |
| **使用方式** | 在終端執行命令 | 在 Rust 代碼中 import |

---

### 📋 完整的 WASM 開發流程

```bash
# 1️⃣ 安裝全局工具（只需一次）
cargo install wasm-bindgen-cli
cargo install wasm-pack  # 建議也裝這個

# 2️⃣ 創建新專案
cargo new my-wasm-project --lib
cd my-wasm-project

# 3️⃣ 添加專案依賴
cargo add wasm-bindgen
cargo add web-sys --features console,Window

# 4️⃣ 寫代碼
# 編輯 src/lib.rs

# 5️⃣ 編譯
wasm-pack build --target web

# 6️⃣ 使用 wasm-bindgen 工具處理（通常 wasm-pack 會自動做）
```

---

### 💡 簡單記憶法

- **`install`** = 裝**工具**（像裝 VS Code）
- **`add`** = 加**材料**（像 npm install 套件）

```
工具 (CLI)         材料 (Library)
    │                  │
    ├─ 處理 WASM       ├─ 寫 Rust 代碼時用
    ├─ 全局安裝        ├─ 每個專案都要加
    └─ 一次性          └─ 在代碼中 use
```

### 🔍 本專案中的使用情況

在本專案 (`wasm-demo`) 中：

**全局工具（已安裝）：**
```bash
wasm-bindgen-cli  # 用於生成 JavaScript 綁定
```

**專案依賴（Cargo.toml）：**
```toml
[dependencies]
wasm-bindgen = "0.2.75"  # 在 Rust 代碼中使用

[dependencies.web-sys]
version = "0.3.52"        # 在 Rust 代碼中使用
features = ["Window", "Document", "Node", "HtmlElement", "Element"]
```

**工作流程：**
1. 使用 `wasm-bindgen` **庫**在 Rust 代碼中標記要導出的函數
2. `cargo build` 編譯成 `.wasm` 檔案
3. 使用 `wasm-bindgen` **工具**處理 `.wasm` 檔案，生成 JavaScript 綁定

## 常見問題

### 1. 編譯錯誤：找不到 wasm-bindgen

**錯誤訊息：**
```
error: failed to run custom build command for `wasm-bindgen`
```

**解決方式：**
```bash
cargo install wasm-bindgen-cli
# 或
make install
```

### 2. Port 被佔用

**錯誤訊息：**
```
Error: listen EADDRINUSE: address already in use :::8080
```

**解決方式：**
```bash
# 使用 Makefile 自動處理
make run

# 或手動 kill port
make kill-port
```

### 3. Webpack 不支援 WebAssembly

**錯誤訊息：**
```
Module parse failed: magic header not detected
```

**解決方式：**
確保 `webpack.config.js` 包含：
```javascript
experiments: {
  asyncWebAssembly: true,
}
```

### 4. 找不到 wasm 檔案

**確認步驟：**
```bash
# 檢查是否已編譯
ls -lh wasm_demo_bg.wasm

# 重新編譯
make build
```

### 5. .cargo/config 棄用警告

**警告訊息：**
```
warning: `.cargo/config` is deprecated in favor of `config.toml`
```

**解決方式：**
```bash
cd .cargo
mv config config.toml
```

## Cargo.toml 說明

```toml
[package]
name = "wasm-demo"
version = "0.1.0"
authors = ["DanSnow <dododavid006@gmail.com>"]
edition = "2018"

[lib]
crate-type = ["cdylib"]  # 編譯成動態連結庫（WebAssembly 需要）

[dependencies]
wasm-bindgen = "0.2.75"

[dependencies.web-sys]
version = "0.3.52"
# 需要哪些 Web API 就加入對應的 feature
features = ["Window", "Document", "Node", "HtmlElement", "Element"]
```

**關鍵設定：**
- `crate-type = ["cdylib"]`：編譯成 C 動態連結庫格式，這是 WebAssembly 所需的
- `web-sys` features：按需啟用 Web API，減少編譯產物大小

## package.json 說明

```json
{
  "name": "wasm-demo",
  "version": "1.0.0",
  "main": "index.js",
  "license": "MIT",
  "scripts": {
    "build": "node build.js",
    "serve": "webpack serve"
  },
  "devDependencies": {
    "html-webpack-plugin": "^5.5.0",
    "shelljs": "^0.8.5",
    "webpack": "^5.66.0",
    "webpack-cli": "^4.9.1",
    "webpack-dev-server": "^4.7.3"
  },
  "packageManager": "yarn@3.1.1"
}
```

## Makefile 指令總覽

```bash
make help       # 顯示所有可用指令
make install    # 安裝所有依賴
make build      # 編譯 Rust + WebAssembly
make run        # 啟動開發伺服器（自動處理 port）
make serve      # 同 run
make kill-port  # 終止佔用 port 的進程
make clean      # 清理所有生成檔案
make rebuild    # 完整重建（clean + install + build）
```

## 進階應用

### 添加更多 Web API

如需使用更多 Web API（例如 `console.log`），在 `Cargo.toml` 添加對應的 feature：

```toml
[dependencies.web-sys]
version = "0.3.52"
features = [
  "Window",
  "Document",
  "Node",
  "HtmlElement",
  "Element",
  "Console",  # 新增
]
```

然後在 Rust 程式碼中使用：

```rust
use web_sys::console;

#[wasm_bindgen]
pub fn main() -> Result<(), JsValue> {
    console::log_1(&"Hello from Rust console!".into());
    // ... 其他程式碼
    Ok(())
}
```

### 從 JavaScript 傳遞參數到 Rust

Rust 程式碼：

```rust
#[wasm_bindgen]
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

JavaScript 程式碼：

```javascript
import('./wasm_demo').then(wasm => {
  const greeting = wasm.greet("World");
  console.log(greeting); // "Hello, World!"
});
```

## 效能考量

1. **編譯優化**：使用 `--release` 模式編譯可大幅減少檔案大小並提升效能
2. **Web API feature 精簡**：只啟用需要的 feature，避免不必要的程式碼
3. **記憶體管理**：注意 Rust 和 JavaScript 之間的記憶體傳遞

## 參考資源

- [wasm-bindgen 官方文檔](https://rustwasm.github.io/wasm-bindgen/)
- [web-sys API 文檔](https://rustwasm.github.io/wasm-bindgen/api/web_sys/)
- [Rust WebAssembly 書籍](https://rustwasm.github.io/book/)
- [MDN WebAssembly 指南](https://developer.mozilla.org/zh-TW/docs/WebAssembly)

## 授權

MIT License

## 作者

原作者：DanSnow (dododavid006@gmail.com)

---

**祝你使用 Rust + WebAssembly 開發順利！**
