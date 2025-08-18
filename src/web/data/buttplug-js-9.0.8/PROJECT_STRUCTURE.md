# ERICA Controller 專案結構

## 必要檔案清單

```
buttplug-js/
├── Makefile                 # 建構和執行腳本
├── README_ERICA.md         # 使用說明文件
├── CLAUDE.md               # Claude Code 開發指南
├── PROJECT_STRUCTURE.md   # 本文件
│
├── js/                     # JavaScript 客戶端庫
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── dist/              # 編譯後的 JS 檔案
│   │   ├── main/
│   │   └── web/
│   │       └── buttplug.mjs
│   └── src/               # 原始碼 (保留供參考)
│       ├── client/
│       ├── core/
│       └── utils/
│
└── wasm/
    ├── dist/              # WASM 編譯檔案
    │   ├── buttplug-wasm.mjs
    │   ├── buttplug_wasm-C70Ovw8k.js
    │   └── index.d.ts
    │
    └── example/           # Web 應用程式
        ├── erica.html     # 主控制頁面
        ├── vite.config.js # Vite 配置
        ├── env-shim.js    # WASM 環境設定
        ├── package.json
        ├── package-lock.json
        └── public/
            └── wasm/
                └── buttplug_wasm_bg.wasm  # WASM 二進位檔案
```

## 執行指令

```bash
# 安裝依賴
make install

# 啟動伺服器
make run

# 清理檔案
make clean

# 顯示幫助
make help
```

## 訪問網址

http://localhost:7777/erica.html

## 核心檔案說明

- **erica.html**: ERICA 設備控制介面
- **buttplug-wasm.mjs**: WASM 客戶端連接器
- **buttplug.mjs**: JavaScript 客戶端庫
- **buttplug_wasm_bg.wasm**: WebAssembly 二進位檔案
- **env-shim.js**: WASM 執行環境配置

## 已移除的檔案

- 所有測試檔案 (test-*.html, *-test.*)
- Rust 原始碼 (不需要重新編譯)
- 重複的配置檔案
- IDE 專用檔案 (.vscode, .github)
- 建構暫存檔案 (target/, .vite/)
- 說明文件的重複版本