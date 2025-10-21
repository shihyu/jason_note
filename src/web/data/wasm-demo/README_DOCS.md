# WebAssembly 專案文檔導覽

## 📚 文檔索引

本專案包含三份完整的技術文檔，適合不同需求的讀者：

---

### 1️⃣ [WASM_WORKFLOW.md](./WASM_WORKFLOW.md) - 完整流程詳解

**適合對象：** 想深入理解整個編譯與載入流程的開發者

**內容包含：**
- ✅ 完整的 6 階段編譯流程圖
- ✅ 8 個關鍵檔案的詳細解析（每個檔案的作用、為什麼需要、缺少會怎樣）
- ✅ 核心技術點深度解析（wasm-bindgen、cdylib、Webpack WASM 支援）
- ✅ 15 步驟的瀏覽器運行時序
- ✅ 常見問題排查與解決方案
- ✅ 生產環境優化建議

**適用場景：**
- 第一次接觸 WASM 專案
- 需要理解每個配置檔案的作用
- 遇到編譯或載入問題需要除錯
- 想知道背後的技術原理

---

### 2️⃣ [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) - 快速參考手冊

**適合對象：** 已經熟悉基本概念，需要快速查閱的開發者

**內容包含：**
- ✅ 一圖看懂完整流程（簡化版流程圖）
- ✅ 檔案角色速查表
- ✅ 三大關鍵配置速覽
- ✅ 常用指令清單
- ✅ Rust ↔ JavaScript 互動範例
- ✅ 快速除錯指南
- ✅ 效能優化清單

**適用場景：**
- 忘記某個配置要怎麼寫
- 需要快速查詢建置指令
- 記不起某個檔案的作用
- 要複製參考程式碼範例

---

### 3️⃣ [ARCHITECTURE.md](./ARCHITECTURE.md) - 系統架構圖

**適合對象：** 想從架構層面理解整個系統的開發者

**內容包含：**
- ✅ 完整的系統架構圖（從開發者介面到瀏覽器執行）
- ✅ 配置檔案依賴關係圖
- ✅ 編譯時與運行時的資料流向
- ✅ 記憶體模型與型別轉換機制
- ✅ 建置工具鏈架構
- ✅ 部署架構與最佳化
- ✅ 除錯工具鏈
- ✅ 效能考量與擴展架構

**適用場景：**
- 需要向團隊解釋專案架構
- 規劃新功能的實作方式
- 優化建置流程或部署策略
- 理解 WASM 與 JavaScript 的互動機制

---

## 🎯 快速開始

### 我該看哪一份？

```
┌─────────────────────────────────────────────────┐
│ 我是完全新手，第一次接觸 WASM                    │
└──────────────────────┬──────────────────────────┘
                       ↓
              📖 先看 WASM_WORKFLOW.md
              （從頭到尾詳細讀一遍）
                       ↓
              📖 再看 ARCHITECTURE.md
              （理解整體架構）
                       ↓
              📋 最後看 QUICK_REFERENCE.md
              （做為日常參考）

┌─────────────────────────────────────────────────┐
│ 我有 WASM 經驗，想快速上手這個專案               │
└──────────────────────┬──────────────────────────┘
                       ↓
              📋 直接看 QUICK_REFERENCE.md
              （快速掌握核心配置）
                       ↓
              📖 有問題再查 WASM_WORKFLOW.md
              （深入了解細節）

┌─────────────────────────────────────────────────┐
│ 我要向團隊講解或設計新架構                       │
└──────────────────────┬──────────────────────────┘
                       ↓
              🏗️ 重點看 ARCHITECTURE.md
              （系統架構與設計決策）
```

---

## 📖 閱讀路徑建議

### 路徑 A：從零開始學習

```
Day 1: 基礎概念
  → 閱讀 WASM_WORKFLOW.md 的「檔案作用」章節
  → 執行 make build 和 make run
  → 觀察產生的檔案

Day 2: 深入流程
  → 閱讀 WASM_WORKFLOW.md 的「完整編譯流程圖」
  → 理解每個階段的轉換過程
  → 手動執行 build.js 中的指令

Day 3: 架構理解
  → 閱讀 ARCHITECTURE.md
  → 理解系統架構與資料流
  → 嘗試修改 src/lib.rs

Day 4: 實戰除錯
  → 故意製造錯誤（如移除 #[wasm_bindgen]）
  → 使用 QUICK_REFERENCE.md 的除錯指南
  → 解決問題並理解錯誤原因
```

### 路徑 B：快速上手

```
30分鐘快速導覽
  → 閱讀 QUICK_REFERENCE.md（10分鐘）
  → 執行 make install && make build（5分鐘）
  → 執行 make run 並觀察結果（5分鐘）
  → 修改 src/lib.rs 並重新編譯（10分鐘）
```

### 路徑 C：問題導向

```
遇到問題時
  1. 先查 QUICK_REFERENCE.md 的「快速除錯」章節
  2. 如果沒解決，查 WASM_WORKFLOW.md 的「常見問題排查」
  3. 如果還沒解決，查 ARCHITECTURE.md 理解底層機制
  4. 最後手動執行建置指令，觀察錯誤訊息
```

---

## 🔑 核心概念速覽

無論讀哪一份文檔，都要理解這三個核心：

### 1. 編譯目標設定
```toml
# .cargo/config
[build]
target = "wasm32-unknown-unknown"
```
→ 讓 Rust 編譯成 WebAssembly 而非執行檔

### 2. 函式庫類型
```toml
# Cargo.toml
[lib]
crate-type = ["cdylib"]
```
→ 產生可被 JavaScript 呼叫的動態函式庫

### 3. WASM 支援
```javascript
// webpack.config.js
experiments: {
  asyncWebAssembly: true,
}
```
→ Webpack 自動處理 WASM 模組載入

---

## 🛠️ 實用工具清單

### 建置與執行
```bash
make install      # 安裝所有依賴
make build        # 編譯 Rust → WASM
make run          # 啟動開發伺服器
make clean        # 清理所有產生的檔案
make rebuild      # 完整重建
```

### 除錯技巧
```bash
# 檢查 WASM 檔案是否產生
ls -la *.wasm

# 檢查編譯目標
rustc --print target-list | grep wasm

# 檢查 wasm-bindgen 是否安裝
wasm-bindgen --version

# 手動執行建置步驟（用於除錯）
cargo build --release --target wasm32-unknown-unknown
wasm-bindgen target/wasm32-unknown-unknown/release/wasm_demo.wasm --out-dir .
```

### 瀏覽器除錯
```
開啟 DevTools (F12)
  → Network Tab: 確認 .wasm 檔案載入成功
  → Console Tab: 查看 JavaScript 錯誤或 console.log
  → Sources Tab: 查看 Source Maps（如果啟用）
```

---

## 📊 文檔對照表

| 問題 | 查閱文檔 | 章節 |
|------|---------|------|
| 什麼是 wasm-bindgen？ | WASM_WORKFLOW.md | 「關鍵技術點解析」 |
| 為什麼要用 cdylib？ | WASM_WORKFLOW.md | 「Cargo.toml 詳解」 |
| 如何優化 WASM 大小？ | QUICK_REFERENCE.md | 「檔案大小優化」 |
| 編譯流程是什麼？ | WASM_WORKFLOW.md | 「完整編譯流程圖」 |
| 如何除錯載入失敗？ | QUICK_REFERENCE.md | 「快速除錯」 |
| 系統架構是什麼？ | ARCHITECTURE.md | 「系統架構」 |
| Rust 如何呼叫 JS？ | ARCHITECTURE.md | 「記憶體模型」 |
| 如何部署到生產環境？ | ARCHITECTURE.md | 「部署架構」 |
| make build 做了什麼？ | WASM_WORKFLOW.md | 「完整建置指令解析」 |
| 瀏覽器如何載入 WASM？ | WASM_WORKFLOW.md | 「瀏覽器載入與執行流程」 |

---

## 🎓 進階主題

看完基礎文檔後，可以探索：

### 進階優化
- Tree Shaking（移除未使用的程式碼）
- Code Splitting（拆分 WASM 模組）
- 使用 wasm-opt 壓縮 WASM
- 啟用 SIMD 指令集

### 複雜互動
- 傳遞複雜資料結構（Vec、HashMap）
- 使用 Closure 從 Rust 呼叫 JavaScript
- 非同步 Rust 函數（async/await）
- Web Worker 中執行 WASM

### 生產部署
- CI/CD 整合
- CDN 部署策略
- 快取策略
- 效能監控

---

## 📞 如何貢獻與回饋

如果發現文檔中的錯誤或有改進建議：

1. **文字錯誤**：直接修改對應的 .md 檔案
2. **內容不清楚**：在 Issues 中提出問題
3. **想要新增章節**：提出 PR 或開 Issue 討論
4. **實作範例**：可以在 examples/ 目錄新增示範程式碼

---

## 🌟 相關資源

### 官方文檔
- [Rust and WebAssembly Book](https://rustwasm.github.io/docs/book/)
- [wasm-bindgen Guide](https://rustwasm.github.io/wasm-bindgen/)
- [WebAssembly MDN](https://developer.mozilla.org/en-US/docs/WebAssembly)

### 工具文檔
- [Cargo Book](https://doc.rust-lang.org/cargo/)
- [Webpack WASM](https://webpack.js.org/configuration/experiments/)
- [web-sys 文檔](https://rustwasm.github.io/wasm-bindgen/api/web_sys/)

### 社群資源
- [Rust WASM Working Group](https://github.com/rustwasm)
- [Awesome WASM](https://github.com/mbasso/awesome-wasm)

---

## ✅ 學習檢查清單

完成以下項目代表你已經掌握基礎：

- [ ] 理解 `.cargo/config` 的作用
- [ ] 知道 `cdylib` 與 `bin` 的差異
- [ ] 能解釋 wasm-bindgen 的用途
- [ ] 成功執行 `make build` 並理解產生的檔案
- [ ] 成功修改 `src/lib.rs` 並看到變化
- [ ] 理解瀏覽器載入 WASM 的流程
- [ ] 能夠除錯常見的編譯錯誤
- [ ] 知道如何優化 WASM 檔案大小

---

**祝學習順利！🚀**
