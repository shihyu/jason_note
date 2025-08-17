# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案概述

這是一個 Buttplug WASM 專案，將 Rust 實作的 Buttplug 協議編譯為 WebAssembly，以在瀏覽器中實現硬體設備控制功能。專案支援 WebBluetooth API，可直接在瀏覽器中掃描、配對和控制藍牙設備。

## 核心架構

專案採用三層架構：

1. **JavaScript/TypeScript 層** (`src/index.ts`): 提供瀏覽器 API 介面
2. **WASM 綁定層** (`rust/src/lib.rs`): Rust 與 JavaScript 間的 FFI 橋接
3. **Rust 核心層** (`rust/src/webbluetooth/`): 實現 Buttplug 協議和 WebBluetooth 通訊

### 關鍵組件

- `ButtplugWasmClientConnector`: TypeScript 連接器，處理 WASM 模組載入和訊息傳遞
- `WebBluetoothCommunicationManager`: Rust 實作的 WebBluetooth 設備管理器
- WASM 綁定函數：`buttplug_create_embedded_wasm_server()`, `buttplug_client_send_json_message()`

## 常用開發指令

### 建構相關
```bash
# 完整建構流程 (推薦)
make build

# 僅編譯 WASM
make wasm-only

# 僅編譯 WASM (直接使用 wasm-pack)
cd rust && wasm-pack build --release --target web

# 編譯 TypeScript
npm run build:web
```

### 開發服務器
```bash
# 啟動開發服務器
make dev

# 快速啟動 (不重新建構)
make quick-dev

# 直接使用 vite
cd example && npx vite --host 0.0.0.0 --port 3000
```

### 依賴安裝
```bash
# 安裝所有依賴
make install

# 手動安裝
npm install
cd example && npm install
```

### 清理
```bash
# 清理所有建構檔案
make clean

# 重新建構
make rebuild
```

## 檔案結構重點

```
wasm/
├── src/index.ts              # TypeScript 連接器主檔案
├── rust/
│   ├── src/lib.rs           # WASM 綁定和 FFI 函數
│   ├── src/webbluetooth/    # WebBluetooth 實作
│   └── pkg/                 # wasm-pack 編譯輸出
├── example/                 # 範例應用程式
└── Makefile                 # 建構腳本 (中文註解)
```

## 開發流程

1. **WASM 編譯**: 修改 Rust 代碼後需重新編譯 WASM
2. **檔案複製**: WASM 檔案需複製到 `example/public/wasm/` 供瀏覽器載入
3. **路徑配置**: WASM 模組透過 `/wasm/buttplug_wasm_bg.wasm` 路徑載入

## 重要技術細節

### WASM 模組載入
- 使用動態 import 載入 WASM 模組
- 需手動初始化 WASM 實例
- 路徑配置在 `src/index.ts:22`

### 訊息傳遞機制
- JavaScript ↔ WASM 使用回調函數進行非同步通訊
- 所有訊息都經過 JSON 序列化/反序列化
- 使用 `Uint8Array` 傳遞二進位資料

### WebBluetooth 整合
- Rust 代碼直接調用瀏覽器 WebBluetooth API
- 支援設備掃描、配對和通訊
- 需要 HTTPS 環境才能使用 WebBluetooth

## 測試和除錯

- 使用 `example/` 目錄中的測試頁面
- 啟用日誌: `ButtplugWasmClientConnector.activateLogging("debug")`
- 瀏覽器開發者工具中檢查 WASM 載入狀態

## 必要工具

- `wasm-pack`: Rust 到 WASM 編譯工具
- Node.js 和 npm: JavaScript 依賴管理
- 支援 WebBluetooth 的瀏覽器 (Chrome, Edge 等)