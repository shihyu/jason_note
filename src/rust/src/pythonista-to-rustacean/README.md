# 從 Pythonista 到 Rustacean：資料從業者的第一本 Rust 指南 🦀🐍
歡迎來到《從 Pythonista 到 Rustacean》的官方範例程式碼倉庫！
這裡收錄了書中所有的範例程式碼，讓您能依照章節順序，從 Rust 的基礎語法，一路實作到高效能的 Python 擴充套件與 AI 模型訓練。
## 📂 資料夾結構
為了方便檢索，所有範例皆依照書中章節編號進行分類：
### PART I：Rust 基礎與核心概念
* **`ch01_basics`**：Rust 的基本功與工具鏈 (Cargo)
* **`ch02_types_and_traits`**：Rust 風格的物件導向 (Struct, Enum, Trait)
* **`ch03_ownership`**：無 GC 的記憶體安全：所有權系統
* **`ch04_closures_iterators`**：優雅的資料處理：閉包與迭代器
* **`ch05_error_handling`**：穩健的程式碼 (Result & Panic)
* **`ch06_modules_testing`**：模組化與測試
* **`ch07_lifetimes`**：參考的有效期限 (Lifetimes)
* **`ch08_concurrency`**：無懼的並行 (Threads, Sync)
### PART II：資料工程、PyO3 與 AI 實戰
* **`ch09_pyo3`**：打造高效能 Python 擴充套件 (搭配 `uv` 管理)
* **`ch10_candle_ai`**：Hugging Face Candle 極速推論
* **`ch11_burn_ai`**：Burn 深度學習框架實戰
* **`ch12_profiling`**：效能分析工具箱
---
## 🛠️ 環境準備
要順利執行本倉庫的程式碼，請確保您的環境已安裝以下工具：
1.  **Rust (Cargo)**: 請透過 [rustup.rs](https://rustup.rs/) 安裝最新穩定版。
2.  **Python & uv** (針對 Ch9 及 AI 章節): 本書範例使用 **[uv](https://github.com/astral-sh/uv)** 進行 Python 虛擬環境與套件管理。
### 快速檢查環境
```Bash
$cargo --version
$ uv --version
````
---
## 🚀 如何執行範例

### 一般 Rust 專案 (Ch1 - Ch8, Ch10 - Ch12)
進入對應的範例資料夾，使用 Cargo 執行：
```Bash
cd ch01_basics/01_rust_intro
cargo run
# 若為效能敏感的範例 (如 AI 訓練)，請加上 --release
cargo run --release
```
### PyO3 專案 (Ch9)
第九章涉及 Python 與 Rust 的互動，建議使用 `uv` 來驅動測試與執行：
```Bash
cd ch09_pyo3/01_my_first_pyo3
# 執行測試
uv run pytest
# 或執行 Python 腳本
uv run python test_example.py
```
---
## 🐛 勘誤與回饋 (Issues & Errata)
雖然我們在寫作與校稿過程中盡力確保正確性，但程式世界變化快速，難免會有疏漏。
如果您在閱讀過程中發現：
- 程式碼無法執行
- 書中內容有誤 (Typos 或觀念修正)
- 有更好的實作建議
**非常歡迎您直接在 GitHub 開啟 [Issue](https://github.com/xavierforge/pythonista-to-rustacean/issues) 回報！** 您的回饋將幫助所有讀者獲得更好的學習體驗。
---
Happy Coding! 願 Rust 的借用檢查器永遠對你微笑 :)