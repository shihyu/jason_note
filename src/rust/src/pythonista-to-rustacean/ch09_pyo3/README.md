# 第 9 章：PyO3 範例執行指南
本章節所有範例皆使用 **`uv`** 進行 Python 環境管理與執行。請依據各範例資料夾內的結構，選擇對應的執行方式：
## 🚀 快速判斷執行方式
進入範例資料夾後，請觀察檔案結構：
### 1. 資料夾內有 `tests/` 目錄 📂
代表此範例包含完整的測試套件，請使用 `pytest` 執行：
```Bash
$ uv run pytest
````
### 2. 資料夾內有 `test_xxx.py` 檔案 📄
代表此範例依賴單一 Python 腳本進行驗證，請直接執行該腳本：
```Bash
$ uv run test_xxx.py
```
_(或者是 `uv run python test_xxx.py`)_
### 3. 上述兩者皆無 🐍
代表這是一個互動式範例，請進入 Python REPL 環境，依照書中教學手動 `import` 模組實驗：
```Bash
$ uv run python
```
_(進入 Python 互動介面後，即可輸入 Rust 編譯好的模組名稱)_
## ⚡ 關於效能測試 (Benchmark)
部分範例涉及 Rust 與 Python 原生程式碼的效能比較。
若您需要執行 Benchmark，請參考書中該小節的具體提示與指令。