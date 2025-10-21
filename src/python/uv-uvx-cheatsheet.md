# UV 和 UVX 指令完整指南：Python 開發者的速度工具

這份完整的速查表將最常用的 `uv` 指令按照工作流程分類，讓開發過程中可以快速查閱。

## 專案建立

使用 `uv init` 初始化專案，支援三種模板：

- **基本專案**：`uv init` 建立標準結構，包含 `.gitignore`、`.python-version`、`main.py`、`pyproject.toml` 和 `README.md`
- **應用程式模板**：`uv init --app myapp` 產生 `src/myapp/` 目錄，包含 `__main__.py` 入口點
- **函式庫模板**：`uv init --lib mylib` 建立可發布的套件結構

指定 Python 版本：`uv init --python 3.12` 在 `pyproject.toml` 中設定版本需求。

## Script 操作

建立符合 PEP 723 規範的獨立腳本，內嵌依賴宣告：

- `uv init --script myscript.py` 產生帶有依賴宣告區塊的腳本
- `uv run myscript.py` 在隔離的虛擬環境中執行
- `uv run --with click myscript.py` 暫時性加入依賴套件
- `uv add --script myscript.py click` 永久加入依賴到腳本

## 依賴管理

**新增/移除套件**：

- `uv add requests httpx` 安裝多個套件
- `uv add --dev pytest ruff` 加入開發用依賴
- `uv remove requests` 移除套件

**檢視關係**：

- `uv tree` 顯示依賴層級結構
- `uv lock --upgrade` 更新所有套件至最新相容版本

**批次操作**：

- `uv add -r requirements.txt` 從舊式 requirements 檔案匯入

## Python 版本管理

- `uv python list` 顯示已安裝的版本
- `uv python install 3.13` 下載並管理版本
- `uv python pin 3.12` 透過 `.python-version` 鎖定專案到特定版本
- `uv python upgrade` 更新所有已管理的版本

## 全域工具

安裝並管理全域工具：

- `uv tool install ruff` 安裝為隔離工具
- `uv tool install ipython --with matplotlib` 包含額外依賴
- `uv tool list` 顯示已安裝的工具
- `uv tool upgrade --all` 更新所有工具

## 快速執行 (uvx)

使用 `uvx` 執行工具而不需安裝（`uv tool run` 的簡寫）：

- `uvx ruff check .` 執行程式碼檢查
- `uvx pytest` 執行測試
- `uvx --from jupyter-core jupyter notebook` 啟動 Jupyter
- `uvx cookiecutter gh:audreyr/cookiecutter-pypackage` 從模板建立專案

## 建置與發布

- `uv build` 在 `dist/` 目錄產生 `.tar.gz` 和 `.whl` 檔案
- `uv publish` 上傳至 PyPI 或套件索引

## 核心特色

「uv 是由 Astral 團隊使用 Rust 開發的極速 Python 套件與專案管理工具」，速度比傳統工具（如 pip 和 virtualenv）快 10-100 倍。它整合了套件安裝、虛擬環境管理和 Python 版本控制於一體。

## uv vs Anaconda：為什麼選擇 uv？

對大多數 Python 開發場景來說，**有了 uv 就可以不需要 Anaconda**！

### ✅ uv 可以取代 Anaconda 的功能

1. **套件管理** - uv 可以安裝所有 PyPI 上的套件
2. **Python 版本管理** - `uv python install 3.x`
3. **虛擬環境** - `uv venv` 或專案自動管理
4. **速度** - 比 conda 快 10-100 倍
5. **輕量** - 不會占用大量硬碟空間

### 📊 何時仍可能需要 Anaconda

只有在少數特殊情況下：

1. **特定的 conda 專屬套件** - 某些科學計算套件只有 conda 版本
2. **非 Python 依賴** - conda 可以管理 C/C++ 庫等系統級依賴
3. **遺留專案** - 團隊已經深度使用 conda 生態系統
4. **特殊編譯版本** - 某些預編譯的二進位套件（但現在 PyPI 上也越來越完整）

### 實際建議

**對一般開發者（推薦 uv）**：
```bash
# 安裝 uv（非常輕量）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 建立專案
uv init myproject
cd myproject

# 安裝常用數據科學套件
uv add pandas numpy matplotlib scikit-learn
```

**數據科學工作（也可用 uv）**：
```bash
# 這些套件在 PyPI 上都有，uv 可以安裝
uv add pandas numpy scipy matplotlib seaborn jupyter
uv add scikit-learn tensorflow pytorch
```

### 總結

- 🎯 **90% 的情況**：uv 就夠了，更快、更輕、更現代
- 📦 **特殊需求**：才需要考慮 Anaconda/Miniconda
- 💡 **建議**：新專案優先使用 uv，遇到問題再考慮 conda

**個人推薦：直接用 uv，它是 Python 工具鏈的未來趨勢！**

---

## 常見使用情境

### 建立新專案
```bash
# 基本專案
uv init my-project
cd my-project

# 應用程式
uv init --app my-app

# 函式庫
uv init --lib my-lib
```

### 管理依賴
```bash
# 安裝套件
uv add requests pandas numpy

# 安裝開發工具
uv add --dev pytest black ruff

# 從 requirements.txt 匯入
uv add -r requirements.txt

# 查看依賴樹
uv tree
```

### Python 版本管理
```bash
# 列出可用版本
uv python list

# 安裝特定版本
uv python install 3.13
uv python install 3.12

# 鎖定專案版本
uv python pin 3.12
```

### 執行腳本和工具
```bash
# 執行專案
uv run python main.py

# 執行腳本
uv run myscript.py

# 快速執行工具（不安裝）
uvx ruff check .
uvx pytest
uvx black .
```

### 全域工具管理
```bash
# 安裝全域工具
uv tool install ruff
uv tool install black
uv tool install ipython --with matplotlib

# 列出已安裝工具
uv tool list

# 更新所有工具
uv tool upgrade --all
```

## 參考資料

- 原文：[uv & uvx 指令完全教學速查表 - The Will Will Web](https://blog.miniasp.com/post/2025/10/20/uv-uvx-cheatsheet)
- [uv 官方文件](https://docs.astral.sh/uv/)
- [PEP 723 - Inline script metadata](https://peps.python.org/pep-0723/)
