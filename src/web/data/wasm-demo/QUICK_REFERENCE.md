# WASM 快速參考

## 🔥 一圖看懂完整流程

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  開發階段：編譯 Rust → WASM                             ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  src/lib.rs                          Rust 源碼（業務邏輯）
      ↓
  [.cargo/config]                     設定編譯目標 = wasm32
      ↓
  cargo build --release               編譯成 WASM 二進位
      ↓
  wasm_demo.wasm                      原始編譯輸出（含符號）
      ↓
  wasm-bindgen                        產生 JS ↔ Rust 綁定
      ↓
  ┌─────────────────┬──────────────────┐
  wasm_demo.js      wasm_demo_bg.wasm  wasm_demo.d.ts
  (JS 綁定)         (優化後 WASM)      (TypeScript 型別)

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  打包階段：Webpack 處理                                 ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  index.js                            載入 WASM 模組
      ↓
  webpack serve                       打包 + 啟動伺服器
      ↓
  dist/
  ├── index.html                      自動產生 HTML
  ├── bundle.js                       打包後的 JS
  └── *.wasm                          WASM 模組

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  運行階段：瀏覽器執行                                   ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

  http://localhost:8080               訪問網頁
      ↓
  載入 index.html
      ↓
  執行 bundle.js
      ↓
  import('./wasm_demo')               非同步載入 WASM
      ↓
  WebAssembly.instantiate()           WASM 模組初始化
      ↓
  wasm.main()                         執行 Rust 函數
      ↓
  操作 DOM                            在頁面顯示 "Hello from Rust"
```

---

## 📁 檔案角色速查表

| 檔案 | 類型 | 作用 | 關鍵設定 |
|------|------|------|---------|
| **src/lib.rs** | Rust | WASM 模組源碼 | `#[wasm_bindgen]` 標記 |
| **Cargo.toml** | 配置 | Rust 專案設定 | `crate-type = ["cdylib"]` |
| **.cargo/config** | 配置 | 編譯目標設定 | `target = "wasm32-unknown-unknown"` |
| **build.js** | 腳本 | 建置自動化 | `cargo build` + `wasm-bindgen` |
| **index.js** | JS | 應用入口 | `import('./wasm_demo').then(...)` |
| **webpack.config.js** | 配置 | 打包設定 | `asyncWebAssembly: true` |
| **package.json** | 配置 | npm 腳本 | `"build": "node build.js"` |
| **Makefile** | 腳本 | 統一介面 | `make build`, `make run` |

---

## ⚙️ 三大關鍵配置

### 1️⃣ 讓 Rust 編譯成 WASM
```toml
# .cargo/config
[build]
target = "wasm32-unknown-unknown"
```

### 2️⃣ 產生可被 JS 呼叫的函式庫
```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]
```

### 3️⃣ Webpack 支援 WASM
```javascript
// webpack.config.js
experiments: {
  asyncWebAssembly: true,
}
```

---

## 🚀 常用指令

```bash
# 安裝依賴
make install

# 編譯 WASM
make build

# 啟動開發伺服器
make run

# 清理檔案
make clean

# 完整重建
make rebuild
```

---

## 🔍 Rust 與 JavaScript 互動

### Rust 端（src/lib.rs）
```rust
use wasm_bindgen::prelude::*;

#[wasm_bindgen]                    // ← 標記：可被 JS 呼叫
pub fn greet(name: &str) -> String {
    format!("Hello, {}!", name)
}
```

### JavaScript 端（index.js）
```javascript
import('./wasm_demo').then(wasm => {
    const message = wasm.greet("World");
    console.log(message);  // "Hello, World!"
});
```

---

## 🐛 快速除錯

### 問題：編譯出執行檔而非 WASM
```bash
# 檢查
cat .cargo/config
cat Cargo.toml  # 確認有 crate-type = ["cdylib"]
```

### 問題：WASM 無法載入
```bash
# 確認檔案存在
ls -la wasm_demo_bg.wasm

# 檢查 Webpack 配置
grep asyncWebAssembly webpack.config.js
```

### 問題：函數無法呼叫
```rust
// src/lib.rs 檢查是否有標記
#[wasm_bindgen]  // ← 必須要有
pub fn your_function() { }
```

---

## 📊 檔案大小優化

### Cargo.toml
```toml
[profile.release]
opt-level = "z"        # 優化大小
lto = true             # Link Time Optimization
codegen-units = 1      # 減少程式碼分割
strip = true           # 移除符號資訊
```

### 使用 wasm-opt
```bash
# 安裝
cargo install wasm-opt

# 優化
wasm-opt -Oz -o optimized.wasm input.wasm
```

---

## 🎓 學習路徑

### Level 1：基礎概念
- ✅ 理解 WASM 是什麼
- ✅ 知道為什麼需要 wasm-bindgen
- ✅ 會執行 `make build` 和 `make run`

### Level 2：配置理解
- ✅ 理解 `.cargo/config` 的作用
- ✅ 知道 `cdylib` 與 `bin` 的差異
- ✅ 會修改 Webpack 配置

### Level 3：進階應用
- ✅ Rust 與 JS 的複雜型別傳遞
- ✅ 多個 WASM 模組協作
- ✅ 效能優化與除錯

---

## 🔗 相關資源

- [Rust WASM Book](https://rustwasm.github.io/docs/book/)
- [wasm-bindgen 文檔](https://rustwasm.github.io/wasm-bindgen/)
- [WebAssembly MDN](https://developer.mozilla.org/en-US/docs/WebAssembly)
- [Webpack WASM](https://webpack.js.org/configuration/experiments/#experimentsasyncwebassembly)
