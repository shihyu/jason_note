# ERICA Bluetooth Controller

基於 Buttplug.js WASM 的 ERICA 藍牙設備控制器

## 功能特點

- 🔍 自動掃描並連接 ERICA 藍牙設備
- 🎛️ 即時振動強度控制（0-100%）
- 🌊 多種振動模式：脈衝、波浪、隨機
- 📱 支援多設備同時控制
- 🔧 調試日誌即時顯示
- 🎨 美觀的使用者介面

## 快速開始

### 安裝依賴
```bash
make install
```

### 啟動開發伺服器
```bash
make run
```

然後開啟瀏覽器訪問：http://localhost:7777/erica.html

## 使用說明

1. **準備設備**
   - 確保 ERICA 設備已開啟並處於配對模式

2. **連接設備**
   - 點擊「開始掃描」按鈕
   - 從彈出的藍牙設備列表中選擇 ERICA
   - 等待連接成功提示

3. **控制振動**
   - 使用滑桿調整振動強度
   - 點擊模式按鈕切換不同振動模式
   - 點擊停止按鈕停止所有振動

## Makefile 命令

```bash
make          # 建構專案
make run      # 啟動開發伺服器
make clean    # 清理建構檔案
make stop     # 停止伺服器
make help     # 顯示幫助訊息
```

## 檔案結構

```
buttplug-js/
├── Makefile                 # 建構和執行腳本
├── wasm/
│   ├── example/
│   │   ├── erica.html      # 主控制頁面
│   │   ├── vite.config.js  # Vite 配置
│   │   └── env-shim.js     # WASM 環境配置
│   └── dist/               # WASM 編譯檔案
└── js/
    └── dist/               # JavaScript 庫檔案
```

## 瀏覽器支援

- Chrome/Edge (推薦) - 完整支援 Web Bluetooth API
- Firefox - 不支援 Web Bluetooth API
- Safari - 部分支援

## 故障排除

### 無法找到設備
- 確認設備已開啟配對模式
- 確認瀏覽器支援 Web Bluetooth
- 嘗試重新整理頁面

### 振動無反應
- 檢查調試日誌中的錯誤訊息
- 確認設備電量充足
- 嘗試重新連接設備

### 連接中斷
- 檢查設備是否超出藍牙範圍
- 確認設備電量
- 點擊「斷開連接」後重新掃描

## 技術棧

- **Buttplug.js** - 成人玩具控制協議
- **WebAssembly** - 高效能運算
- **Web Bluetooth API** - 藍牙設備通訊
- **Vite** - 開發伺服器和建構工具

## 授權

BSD 3-Clause License