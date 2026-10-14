# WebAssembly 專案架構圖

## 🏗️ 系統架構

```
┌──────────────────────────────────────────────────────────────────┐
│                         開發者介面                               │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐          │
│  │make build│  │make run  │  │make clean│  │make help │          │
│  └─────┬────┘  └─────┬────┘  └─────┬────┘  └──────────┘          │
└────────┼─────────────┼─────────────┼─────────────────────────────┘
         │             │             │
         ↓             ↓             ↓
┌──────────────────────────────────────────────────────────────────┐
│                      Makefile (統一介面)                         │
│                                                                  │
│  install: npm install + cargo install wasm-bindgen-cli           │
│  build:   npm run build                                          │
│  run:     kill-port + npm run serve                              │
│  clean:   rm -rf target/ dist/ node_modules/                     │
└─────────────────────────┬────────────────────────────────────────┘
                          │
         ┌────────────────┴────────────────┐
         ↓                                 ↓
┌──────────────────┐              ┌──────────────────┐
│  npm run build   │              │  npm run serve   │
│  (編譯階段)      │              │   (運行階段)     │
└────────┬─────────┘              └────────┬─────────┘
         ↓                                 ↓
         │                                 │
         │                          ┌─────────────┐
         │                          │   Webpack   │
         │                          │ Dev Server  │
         │                          └─────────────┘
         ↓
┌──────────────────────────────────────────────────────────────────┐
│                       build.js (建置腳本)                        │
│                                                                  │
│  Step 1: cargo build --release                                   │
│          ↓                                                       │
│          讀取 .cargo/config                                      │
│          發現 target = "wasm32-unknown-unknown"                  │
│          編譯 src/lib.rs → WASM                                  │
│                                                                  │
│  Step 2: wasm-bindgen target/.../wasm_demo.wasm --out-dir .      │
│          ↓                                                       │
│          產生 JavaScript 綁定                                    │
└──────────────────────────────────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────────────────────────────────┐
│                      編譯產物 (artifacts)                        │
│                                                                  │
│  target/wasm32-unknown-unknown/release/                          │
│  └── wasm_demo.wasm          [原始 WASM 二進位]                  │
│                                                                  │
│  專案根目錄/                                                     │
│  ├── wasm_demo.js            [JavaScript 綁定]                   │
│  ├── wasm_demo_bg.wasm       [優化後的 WASM]                     │
│  └── wasm_demo.d.ts          [TypeScript 型別定義]               │
└──────────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                   Webpack 打包 (webpack.config.js)              │
│                                                                 │
│  entry: './index.js'                                            │
│      ↓                                                          │
│  發現 import('./wasm_demo')                                     │
│      ↓                                                          │
│  experiments: { asyncWebAssembly: true }                        │
│      ↓                                                          │
│  自動處理 WASM 模組                                             │
│      ↓                                                          │
│  產生 dist/ 輸出                                                │
│      ↓                                                          │
│  dist/                                                          │
│  ├── index.html              [HtmlPlugin 自動產生]              │
│  ├── bundle.js               [打包後的 JavaScript]              │
│  └── *.wasm                  [WASM 模組]                        │
└─────────────────────────────────────────────────────────────────┘
         │
         ↓
┌──────────────────────────────────────────────────────────────────┐
│                瀏覽器運行時 (Browser Runtime)                    │
│                                                                  │
│  http://localhost:8080                                           │
│      ↓                                                           │
│  載入 index.html                                                 │
│      ↓                                                           │
│  <script src="bundle.js">                                        │
│      ↓                                                           │
│  執行 index.js                                                   │
│      ↓                                                           │
│  import('./wasm_demo')                                           │
│      ↓                                                           │
│  非同步載入 WASM 模組                                            │
│      ↓                                                           │
│  WebAssembly.instantiate(wasmBytes)                              │
│      ↓                                                           │
│  WASM 實例化完成                                                 │
│      ↓                                                           │
│  wasm.main()                                                     │
│      ↓                                                           │
│  執行 Rust 程式碼                                                │
│      ↓                                                           │
│  操作 DOM (document.createElement)                               │
│      ↓                                                           │
│  顯示 "Hello from Rust"                                          │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🔧 配置檔案依賴關係

```
.cargo/config ─────────┐
                       ↓
Cargo.toml ──────→ [Rust Compiler] ──→ wasm_demo.wasm
    ↑                                        ↓
    │                                        ↓
src/lib.rs ───────┘               [wasm-bindgen] ──→ wasm_demo.js
                                                  ──→ wasm_demo_bg.wasm
                                                  ──→ wasm_demo.d.ts
                                        ↓
                                        ↓
index.js ──────────────────────────────┘
    ↓
    ↓
webpack.config.js ──→ [Webpack] ──→ dist/
    ↑                                ├── index.html
    │                                ├── bundle.js
package.json ────┘                   └── *.wasm
```

---

## 📦 資料流向

### 編譯時（Compile Time）

```
┌──────────────┐
│  src/lib.rs  │  Rust 源碼
└──────┬───────┘
       │
       ↓ [rustc + LLVM]
       │
┌──────────────────────────────┐
│  WASM 二進位                 │  機器碼（WebAssembly 格式）
│  (target/.../wasm_demo.wasm) │
└──────┬───────────────────────┘
       │
       ↓ [wasm-bindgen]
       │
┌──────────────────────────────┐
│  JavaScript 綁定             │  可在 JS 中 import 的模組
│  (wasm_demo.js)              │
└──────┬───────────────────────┘
       │
       ↓ [Webpack]
       │
┌───────────────────────────────┐
│  打包後的 bundle              │  部署檔案
│  (dist/bundle.js)             │
└───────────────────────────────┘
```

### 運行時（Runtime）

```
┌─────────────┐
│  瀏覽器     │
└──────┬──────┘
       │
       ↓ HTTP Request
       │
┌──────────────┐
│ index.html   │ ← Webpack HtmlPlugin 產生
└──────┬───────┘
       │
       ↓ <script src="bundle.js">
       │
┌──────────────┐
│  bundle.js   │ ← 包含 index.js + wasm 綁定
└──────┬───────┘
       │
       ↓ import('./wasm_demo')
       │
┌──────────────────────┐
│  wasm_demo.js        │ ← JavaScript 綁定層
└──────┬───────────────┘
       │
       ↓ fetch('wasm_demo_bg.wasm')
       │
┌──────────────────────┐
│ wasm_demo_bg.wasm    │ ← WASM 二進位模組
└──────┬───────────────┘
       │
       ↓ WebAssembly.instantiate()
       │
┌──────────────────────┐
│  WASM 實例           │ ← 在記憶體中運行的 Rust 程式碼
└──────┬───────────────┘
       │
       ↓ wasm.main()
       │
┌────────────────────────┐
│  執行 Rust 函數        │ ← 操作 DOM、處理業務邏輯
└────────────────────────┘
```

---

## 🎯 記憶體模型

```
┌──────────────────────────────────────────────────────────────┐
│                        瀏覽器記憶體                          │
│                                                              │
│  ┌───────────────┐           ┌───────────────┐               │
│  │  JavaScript   │           │  WebAssembly  │               │
│  │  Heap         │           │  Linear Memory│               │
│  │               │           │               │               │
│  │  ┌─────────┐  │           │  ┌─────────┐  │               │
│  │  │ Objects │  │  ⟷ copy ⟷ │  │  Bytes  │  │               │
│  │  │ Strings │  │           │  │ Numbers │  │               │
│  │  │ Arrays  │  │           │  │  (i32)  │  │               │
│  │  └─────────┘  │           │  └─────────┘  │               │
│  │               │           │               │               │
│  └───────────────┘           └───────────────┘               │
│         ↑                            ↑                       │
│         │                            │                       │
│         └────── wasm-bindgen ────────┘                       │
│              (處理型別轉換與資料複製)                        │
└──────────────────────────────────────────────────────────────┘
```

### 型別轉換範例

```rust
// Rust 端
#[wasm_bindgen]
pub fn process_text(input: &str) -> String {
    input.to_uppercase()
}
```

```javascript
// JavaScript 端
wasm.process_text("hello");  // 背後發生：

// 1. JS String "hello" → UTF-8 bytes → 寫入 WASM Linear Memory
// 2. 呼叫 WASM 函數，傳遞指標 + 長度
// 3. Rust 處理，結果寫入 WASM Linear Memory
// 4. 從 WASM Memory 讀取 → 轉換成 JS String
// 5. 返回 "HELLO"
```

---

## 🔄 建置工具鏈

```
┌──────────────────────────────────────────────────────────────┐
│                    開發工具鏈                                │
└──────────────────────────────────────────────────────────────┘

   Rust 工具鏈                  JavaScript 工具鏈
   ─────────────                ──────────────────

   rustc (編譯器)               node (運行環境)
      ↓                            ↓
   cargo (建置工具)              npm (套件管理)
      ↓                            ↓
   wasm32 target                webpack (打包工具)
      ↓                            ↓
   wasm-bindgen                 webpack-dev-server
   (綁定產生器)                  (開發伺服器)

         │                          │
         └──────────┬───────────────┘
                    ↓
         ┌────────────────────┐
         │   最終輸出 (dist/) │
         │                    │
         │  index.html        │
         │  bundle.js         │
         │  *.wasm            │
         └────────────────────┘
```

---

## 🚀 部署架構

### 開發環境

```
開發者機器
├── make run
├── Webpack Dev Server (port 8080)
├── Hot Reload
└── Source Maps
```

### 生產環境

```
┌──────────────┐
│  CDN / 靜態  │
│  檔案伺服器  │
└──────┬───────┘
       │
       ↓ 部署 dist/ 內容
       │
┌──────────────┐
│  使用者瀏覽器│
└──────────────┘

檔案清單：
- index.html        (主頁面)
- bundle.js         (應用邏輯 + WASM 載入器)
- *.wasm           (WebAssembly 模組)
```

**最佳化建議：**
1. 啟用 gzip/brotli 壓縮
2. 設定 Cache-Control headers
3. 使用 `webpack --mode production`
4. 使用 `wasm-opt` 優化 WASM 大小

---

## 🔍 除錯架構

```
┌──────────────────────────────────────────────────────────────┐
│                      除錯工具鏈                              │
└──────────────────────────────────────────────────────────────┘

Rust 側                           JavaScript 側
─────────                         ─────────────

cargo test                        npm run serve
   ↓                                 ↓
單元測試                          瀏覽器 DevTools
   ↓                                 ↓
println! / dbg!                   console.log
   ↓                                 ↓
Rust 除錯器                        Source Maps
                                     ↓
                                  Network Tab
                                  (檢查 WASM 載入)
                                     ↓
                                  Console Tab
                                  (JavaScript 錯誤)
```

### Source Map 支援

```javascript
// webpack.config.js
devtool: 'cheap-module-source-map',
```

這允許：
- 在瀏覽器 DevTools 中看到原始 Rust 源碼（有限支援）
- JavaScript 錯誤可追溯到 `index.js` 源碼
- 更好的除錯體驗

---

## 📊 效能考量

### 冷啟動流程

```
首次載入
    ↓
下載 HTML (< 1KB)
    ↓
下載 bundle.js (~ 幾十 KB)
    ↓
下載 .wasm (取決於程式大小)
    ↓
編譯 WASM (JIT/AOT)
    ↓
實例化模組
    ↓
執行應用程式碼
```

**優化策略：**
1. **Code Splitting**：將 WASM 模組分離成獨立 chunk
2. **延遲載入**：使用 `import()` 動態載入
3. **壓縮**：啟用 gzip (通常可減少 70% 大小)
4. **快取**：設定長期快取 headers

### 運行時效能

```
Rust (WASM)                    JavaScript
────────────                   ──────────
✅ 數值運算快                   ❌ 數值運算慢
✅ 記憶體效率高                 ❌ GC 開銷
✅ 型別安全                     ⚠️ 動態型別
❌ 無法直接操作 DOM             ✅ 原生 DOM 操作
❌ 與 JS 互動有開銷              ✅ 無跨境開銷
```

**最佳實踐：**
- 計算密集任務 → Rust/WASM
- DOM 操作 → JavaScript
- 最小化跨邊界呼叫次數

---

## 🎓 擴展架構

### 多模組架構

```
src/
├── lib.rs              (主入口)
├── math.rs            (數學運算模組)
│   └── pub fn calculate()
├── image.rs           (圖片處理模組)
│   └── pub fn process_image()
└── utils.rs           (工具函數)
    └── pub fn helper()
```

```rust
// lib.rs
mod math;
mod image;
mod utils;

#[wasm_bindgen]
pub fn main() {
    math::calculate();
    image::process_image();
}
```

### Worker 架構（進階）

```
┌─────────────┐
│  Main Thread│
└──────┬──────┘
       │
       ↓ postMessage
       │
┌──────────────┐
│  Web Worker  │  ← 在這裡執行 WASM
│  + WASM      │    (不阻塞主執行緒)
└──────┬───────┘
       │
       ↓ postMessage
       │
┌──────────────┐
│  Main Thread │  ← 接收結果，更新 UI
└──────────────┘
```

---

## 📝 總結

這個架構展示了：

1. **編譯鏈**：Rust → WASM → JS 綁定 → Webpack 打包
2. **運行時**：瀏覽器載入 → WASM 實例化 → 執行
3. **資料流**：JS ↔ wasm-bindgen ↔ WASM Memory
4. **工具鏈**：Cargo + npm + Webpack 的整合

**核心優勢：**
- ✅ 高效能計算（接近原生速度）
- ✅ 型別安全（Rust 編譯器保證）
- ✅ 與 JavaScript 生態系統無縫整合
- ✅ 可在瀏覽器中運行系統級語言
