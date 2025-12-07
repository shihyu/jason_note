# ⚡ uv：Python 極速全能管理工具指南

## 1. 什麼是 uv？

**uv** 是一個由 Rust 編寫的 Python 套件與專案管理器。它的目標是統一 Python 破碎的工具鏈，成為「Python 界的 Cargo」。

* **開發商**：Astral (也是知名 linter 工具 `Ruff` 的開發者)。
* **核心特色**：**極致的速度**（比 pip 快 10-100 倍）、**一站式管理**（取代 pip, poetry, pyenv, virtualenv, pipx）。
* **定位**：不僅僅是 pip 的替代品，更是現代化 Python 專案工作流的標準。

---

## 2. 工具比較：為什麼要換？

uv 的最大優勢在於將多個工具的功能整合進一個單一的執行檔中，且效能大幅提升。

| 功能 | **uv** | pip | Poetry | pip-tools | pyenv | pipx |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **安裝速度** | 🚀 **極快 (Rust)** | 🐢 慢 | 🐢 慢 | - | - | - |
| **依賴解析** | 🚀 **極快** | 🐢 慢 | 🐢 慢 | 😐 普通 | - | - |
| **虛擬環境管理** | ✅ **內建** | ❌ (需 venv) | ✅ | ❌ | ❌ | ❌ |
| **Python 版本管理** | ✅ **內建** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **執行 CLI 工具** | ✅ (`uvx`) | ❌ | ❌ | ❌ | ❌ | ✅ |
| **專案鎖定檔** | ✅ (`uv.lock`) | ❌ | ✅ (`poetry.lock`) | ✅ | - | - |

> **一句話總結**：使用 `uv`，你通常不再需要安裝 Python (它幫你裝)、不再需要手動建立 venv、也不再需要 Poetry 或 pipx。

---

## 3. 安裝 uv

### macOS / Linux
官方推薦使用安裝腳本：
```bash
curl -LsSf [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
````

### Windows

使用 PowerShell：

```powershell
powershell -ExecutionPolicy ByPass -c "irm [https://astral.sh/uv/install.ps1](https://astral.sh/uv/install.ps1) | iex"
```

### 使用 pip 安裝 (不推薦，但可行)

如果你已經有 Python 環境，也可以用 pip 安裝（但這樣 uv 就變成了依賴於該 Python 的套件）：

```bash
pip install uv
```

-----

## 4\. 常用指令速查表 (Cheatsheet)

uv 有兩種使用模式：**「專案管理模式 (Project)」** 與 **「pip 兼容模式 (Pip Interface)」**。目前官方推薦使用專案管理模式。

### 📦 模式一：現代化專案管理 (類似 Poetry/npm)

這是 `uv` 最強大的用法，自動處理虛擬環境與鎖定檔。

| 動作 | 指令 | 說明 |
| :--- | :--- | :--- |
| **初始化專案** | `uv init <專案名>` | 建立新資料夾與 `pyproject.toml` |
| **加入套件** | `uv add flask` | 安裝套件並更新設定檔與 lock 檔 |
| **加入開發套件** | `uv add --dev pytest` | 僅加入開發環境依賴 |
| **移除套件** | `uv remove flask` | 移除套件 |
| **執行腳本** | `uv run main.py` | **最常用！** 自動在虛擬環境中執行 |
| **同步環境** | `uv sync` | 根據 lock 檔安裝所有依賴 (類似 `npm install`) |
| **檢視依賴樹** | `uv tree` | 顯示依賴關係樹狀圖 |

### 🐍 Python 版本管理 (取代 pyenv)

| 動作 | 指令 | 說明 |
| :--- | :--- | :--- |
| **安裝 Python** | `uv python install 3.12` | 下載並安裝指定版本的 Python |
| **列出版本** | `uv python list` | 列出已安裝或可用的 Python 版本 |
| **指定專案版本** | `uv pin 3.11` | 強制目前專案使用 Python 3.11 |

### 🛠️ 工具執行 (取代 pipx)

不想安裝套件到專案，只想暫時執行某個工具（如 ruff, black, httpie）？

| 動作 | 指令 | 說明 |
| :--- | :--- | :--- |
| **執行工具** | `uvx ruff check .` | 下載並執行 ruff (用完即丟，不汙染環境) |
| **安裝工具** | `uv tool install black` | 將工具安裝到全域環境 |

### 🐢 模式二：Pip 兼容模式 (Legacy)

如果你不想改變現有的工作流，只想把它當作更快的 pip 使用。

| 動作 | 指令 | 對應 pip 指令 |
| :--- | :--- | :--- |
| **建立 venv** | `uv venv` | `python -m venv .venv` |
| **安裝套件** | `uv pip install requests` | `pip install requests` |
| **安裝列表** | `uv pip install -r requirements.txt` | `pip install -r ...` |
| **匯出列表** | `uv pip freeze > requirements.txt` | `pip freeze > ...` |

-----

## 5\. 常見問答 (FAQ)

### Q1: `uv run` 是做什麼的？

這是 `uv` 最方便的指令。當你執行 `uv run app.py` 時，它會：

1.  檢查是否有虛擬環境，沒有就建立一個。
2.  檢查依賴是否安裝，沒有就安裝。
3.  使用該虛擬環境執行 `app.py`。
    你不再需要手動 `source .venv/bin/activate`！

### Q2: 全域快取 (Global Cache) 是什麼？

`uv` 會將下載過的套件存在硬碟的一個中心位置。如果你有 10 個專案都用了 `numpy`，`uv` 只需要下載一次，且硬碟佔用量極低（透過 Hard link 技術）。

### Q3: 如何升級 uv 本身？

```bash
uv self update
```

## 6\. 從 Poetry 遷移到 uv

如果你原本使用 `pyproject.toml` (Poetry)，遷移非常簡單：

1.  刪除 `poetry.lock`
2.  在專案目錄執行：
    ```bash
    uv init
    uv add <你的主要套件>
    ```
    *(或者直接讓 uv 讀取既有的 pyproject.toml 格式並轉換)*
