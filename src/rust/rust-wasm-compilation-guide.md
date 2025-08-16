# Rust WASM 編譯流程詳解

基於你的 `buttplug_wasm` 專案，以下是完整的編譯邏輯說明：

## 1. 依賴解析階段

### Cargo.toml 的角色
```toml
[dependencies]
buttplug = { version = "7.1.13", default-features = false, features = ["wasm"] }
js-sys = "0.3.68"
wasm-bindgen = { version = "0.2.91", features = ["serde-serialize"] }
tokio = { version = "1.36.0", features = ["sync", "macros", "io-util"] }
# ... 其他依賴
```

- **直接依賴**：你在 `Cargo.toml` 中明確指定的套件
- **版本約束**：指定可接受的版本範圍
- **特性選擇**：控制編譯哪些功能模組

### Cargo.lock 的角色
```toml
[[package]]
name = "buttplug"
version = "7.1.13"
dependencies = [
 "aes",
 "async-stream", 
 "tokio",
 # ... 完整的間接依賴清單
]
```

- **版本鎖定**：確保每次編譯使用完全相同的版本
- **間接依賴**：記錄所有依賴的依賴關係
- **編譯一致性**：不同環境下產生相同的編譯結果

## 2. 依賴樹建構

```mermaid
graph TD
    A[buttplug_wasm] --> B[buttplug 7.1.13]
    A --> C[wasm-bindgen 0.2.91]
    A --> D[tokio 1.36.0]
    B --> E[async-trait 0.1.77]
    B --> F[serde 1.0.197]
    C --> G[js-sys 0.3.68]
    D --> H[futures 0.3.30]
    # ... 更多間接依賴
```

## 3. 源碼下載與快取

- **下載位置**：`~/.cargo/registry/src/`
- **快取機制**：避免重複下載相同版本
- **完整性檢查**：驗證下載的源碼完整性

## 4. 編譯配置分析

### crate-type 設定
```toml
[lib]
crate-type = ["cdylib", "rlib"]
```
- **cdylib**：編譯成動態函式庫，用於生成 WASM
- **rlib**：Rust 原生函式庫格式，供其他 Rust 專案使用

### 特性標誌影響
```toml
buttplug = { default-features = false, features = ["wasm"] }
```
- **條件編譯**：只編譯 WASM 環境需要的程式碼
- **減少體積**：排除不需要的功能模組

## 5. 統一編譯階段

### 編譯目標
```bash
wasm-pack build --release --target web
```

**編譯流程**：
```
所有 Rust 源碼 (主專案 + 所有依賴)
    ↓
rustc (with wasm32-unknown-unknown target)
    ↓ 
LLVM 最佳化
    ↓
單一 WASM 二進制檔案
```

### 跨函式庫最佳化
- **Link Time Optimization (LTO)**：跨套件的函式內聯
- **死代碼消除**：移除未使用的函式和類型
- **常數摺疊**：編譯時計算常數表達式

## 6. WASM 特定最佳化

### --release 模式優化
- **程式碼最佳化**：`-O3` 等級優化
- **體積最佳化**：`wee_alloc` 記憶體分配器
- **除錯資訊移除**：減小最終檔案大小

### --target web 配置
```javascript
// 生成適合瀏覽器的 ES6 模組
import init, { buttplug_create_embedded_wasm_server } from './pkg/buttplug_wasm.js';
```

## 7. 輸出產物

### 主要檔案
```
pkg/
├── buttplug_wasm.wasm          # 主 WASM 二進制檔案 (~500KB-2MB)
├── buttplug_wasm.js            # JavaScript 綁定
├── buttplug_wasm_bg.wasm       # 背景 WASM 模組
├── buttplug_wasm_bg.js         # 背景 JS 綁定
├── package.json                # NPM 套件設定
└── buttplug_wasm.d.ts          # TypeScript 型別定義
```

### 檔案關係
- **WASM 檔案**：包含所有 Rust 程式碼的編譯結果
- **JS 綁定**：提供 JavaScript 可調用的介面
- **型別定義**：支援 TypeScript 開發

## 8. 執行時載入

```javascript
// 瀏覽器中載入和初始化
import init, { buttplug_create_embedded_wasm_server } from './pkg/buttplug_wasm.js';

async function main() {
    await init(); // 載入 WASM 模組
    const server = buttplug_create_embedded_wasm_server(callback);
}
```

## 9. 編譯時間考量

- **初次編譯**：需要編譯所有依賴 (5-15 分鐘)
- **增量編譯**：只重新編譯修改的部分 (30 秒 - 2 分鐘)
- **快取利用**：Cargo 會快取已編譯的依賴

這個編譯流程確保了最終的 WASM 檔案包含所有必要的功能，同時保持最佳的效能和最小的檔案大小。
