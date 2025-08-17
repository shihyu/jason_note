# Buttplug Server WASM Example

這是一個示範如何在網頁中使用 Buttplug Server WebAssembly 模組的例子。

## 特色

- 🚀 完整的 WASM 載入和初始化流程
- 🧪 基本功能測試
- 📋 導出函數和類別列表
- 🎨 現代化的使用者介面
- 📝 詳細的日誌輸出

## 快速開始

### 方法 1: 使用 Python HTTP Server

```bash
# 在專案根目錄執行
python3 -m http.server 8080
```

然後在瀏覽器中開啟: http://localhost:8080/web_example/

### 方法 2: 使用 Node.js serve

```bash
cd web_example
npm install
npm run serve
```

### 方法 3: 使用任何其他 HTTP 伺服器

確保伺服器支援 ES modules 和 WASM 檔案的正確 MIME 類型。

## 檔案結構

```
web_example/
├── index.html          # 主要的測試頁面
├── package.json        # npm 配置
├── README.md          # 這個檔案
└── pkg/               # WASM 模組檔案
    ├── buttplug_server.js
    ├── buttplug_server_bg.wasm
    ├── buttplug_server_bg.js
    ├── buttplug_server.d.ts
    └── package.json
```

## 使用步驟

1. 在瀏覽器中開啟測試頁面
2. 點擊 "載入 WASM 模組" 按鈕
3. 等待模組載入完成
4. 點擊 "測試基本功能" 驗證模組可用性
5. 點擊 "顯示導出函數" 查看可用的 API

## 技術細節

### WASM 模組載入

```javascript
// 動態載入 WASM 模組
const wasmModule = await import('./pkg/buttplug_server.js');

// 初始化 WASM
await wasmModule.default();
```

### 錯誤處理

頁面包含完整的錯誤處理機制：
- 模組載入失敗
- 初始化錯誤
- 功能測試失敗

### 瀏覽器相容性

- ✅ Chrome 61+
- ✅ Firefox 60+
- ✅ Safari 11+
- ✅ Edge 16+

需要支援：
- ES6 Modules
- WebAssembly
- Async/Await

## 疑難排解

### CORS 錯誤
確保使用 HTTP 伺服器而不是直接開啟 HTML 檔案。

### WASM 載入失敗
檢查：
1. 檔案路徑是否正確
2. WASM 檔案是否存在
3. 伺服器是否正確設定 WASM MIME 類型

### 模組初始化失敗
檢查瀏覽器控制台中的詳細錯誤訊息。

## 進一步開發

這個例子提供了基礎框架，你可以：

1. 添加具體的 Buttplug 功能測試
2. 整合到現有的 web 應用
3. 添加設備連接和控制功能
4. 實作更複雜的 UI 互動

## 相關連結

- [Buttplug 官方網站](https://buttplug.io)
- [WebAssembly 官方文件](https://webassembly.org)
- [wasm-pack 文件](https://rustwasm.github.io/wasm-pack/)