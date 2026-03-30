# Plan: cf-binance-ws (Completed)

## 任務目標
建立一個基於 Cloudflare Pages 的專案，實作從 Binance WebSocket API 獲取 BTC/USDT 即時報價，並動態更新至網頁上。

## 專案結構組織
- 專案名稱：`cf-binance-ws`
- 資料夾結構：
  - `cf-binance-ws/`
    - `public/`: 靜態網頁資源
      - `index.html`: 主頁面
      - `app.js`: WebSocket 邏輯與 DOM 更新
      - `style.css`: 樣式表
    - `functions/`: (預留) Cloudflare Pages Functions
    - `tests/`: 測試腳本與環境
    - `Makefile`: 標準化建置工具
    - `package.json`: 專案依賴與腳本
    - `wrangler.toml`: Cloudflare Pages 設定

## 預期產出
1. 即時顯示 BTC/USDT 價格、漲跌幅、成交量等資訊的網頁。
2. 自動連線與斷線重連機制的 JavaScript 實作。
3. 符合規範的 Makefile。
4. 完整的測試環境。

## Makefile 規範

### 必備目標
- `make` (無參數)：顯示可用目標和使用範例
- `make build`：安裝依賴 (npm install)
- `make run`：執行本地預覽 (port 8888)
- `make test`：執行測試
- `make deploy`：部署到 Cloudflare Pages
- `make clean`：清理臨時檔案

### 特殊處理
- 預設 Port: 8888
- `run` 目標會自動清理 port 8888。

## build/debug/test 指令
- Build: `npm install`
- Debug: `npx wrangler pages dev public --port 8888`
- Test: `npm test`
- Deploy: `npx wrangler pages deploy public`

## 驗收標準
1. 網頁開啟後能正確連線至 Binance WS (`wss://stream.binance.com:9443/ws/btcusdt@trade`)。
2. 頁面上的價格欄位會隨著 WS 訊息即時更新（不需重新整理）。
3. 價格上漲時顯示綠色，下跌時顯示紅色（視覺反饋）。
4. 包含錯誤處理與斷線自動重連機制。
5. Makefile 所有目標運作正常。

## 子任務拆解
1. [x] 初始化專案結構與 `package.json`。
2. [x] 撰寫 `Makefile`。
3. [x] 實作 `public/index.html` 基本架構。
4. [x] 實作 `public/app.js` WebSocket 連線邏輯。
5. [x] 撰寫測試腳本驗證 WS 連線與資料解析。
6. [x] 完善樣式與視覺反饋。
7. [x] 部署至 Cloudflare Pages 並驗證成功。
