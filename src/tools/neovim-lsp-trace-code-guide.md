# Neovim 全語言程式碼追蹤 (Trace Code) 全攻略

> 這是一份為你整理好的完整 Markdown 指南，你可以將其存成 `nvim-trace-code.md` 方便日後查閱。這份文件涵蓋了從原理、工具清單到具體配置的所有精華。

在 Linux 環境下，使用 Neovim 進行全專案程式碼追蹤的核心在於 LSP (Language Server Protocol)。它能像 IDE 一樣「理解」你的代碼結構，並建立索引實現精準跳轉。

---

## 1. 各語言追蹤工具總覽表

| 語言 / 框架 | 推薦 LSP Server | 手動產生索引檔？ | 關鍵檔案 (LSP 識別依據) | 備註 |
|---|---|---|---|---|
| C / C++ | clangd | 是 (必要) | compile_commands.json | 需透過 cmake 或 bear 產生 |
| Rust | rust-analyzer | 否 | Cargo.toml | 自動讀取專案與依賴架構 |
| Go | gopls | 否 | go.mod | 自動追蹤全專案與第三方庫 |
| Python | pyright | 否 | .git, requirements.txt | 建議於根目錄指定虛擬環境路徑 |
| Node / Next.js | vtsls | 否 | package.json, tsconfig.json | tsconfig 決定路徑別名解析 |
| Linux Kernel | clangd | 是 (手動) | compile_commands.json | 執行核心內建 gen_compile_commands.py |

---

## 2. 核心原理：為什麼能跨檔案跳轉？

LSP 並非單純的字串搜尋，它會在背景執行以下動作：

1. **建立索引 (Indexing)**：啟動時掃描專案檔案，將函數、變數定義存入記憶體資料庫。
2. **語義分析**：透過 AST (抽象語法樹) 理解代碼邏輯，區分同名的不同函數。
3. **專案判定**：偵測「關鍵檔案」（如 go.mod 或 .git）來鎖定專案根目錄，從而實現全域搜尋。

---

## 3. Neovim 完整配置範例 (Lua)

這份配置使用了 lazy.nvim 管理插件，並透過 mason 自動管理 LSP Server。

```lua
-- 1. 插件安裝 (使用 lazy.nvim)
local plugins = {
  "neovim/nvim-lspconfig",             -- LSP 基礎配置
  "williamboman/mason.nvim",              -- LSP 下載管理器
  "williamboman/mason-lspconfig.nvim",   -- 橋接器
  {
    'nvim-telescope/telescope.nvim',    -- 視覺化搜尋界面
    dependencies = { 'nvim-lua/plenary.nvim' }
  },
}

-- 2. LSP 自動化配置
local mason = require("mason")
local mason_lspconfig = require("mason-lspconfig")
local lspconfig = require("lspconfig")

mason.setup()

-- 定義要管理的 Server
local servers = {
  clangd = {},
  rust_analyzer = {},
  gopls = {},
  pyright = {},
  vtsls = {}
}

mason_lspconfig.setup({ ensure_installed = vim.tbl_keys(servers) })

-- 設定通用快捷鍵 (當 LSP 連線時)
local on_attach = function(_, bufnr)
  local opts = { buffer = bufnr, remap = false }

  -- 跳進去 (Definition)
  vim.keymap.set("n", "gd", vim.lsp.buf.definition, opts)
  -- 看引用 (References) - 使用 Telescope 彈窗顯示
  vim.keymap.set("n", "gr", require('telescope.builtin').lsp_references, opts)
  -- 看實作 (Implementation)
  vim.keymap.set("n", "gi", vim.lsp.buf.implementation, opts)
  -- 顯示文件 (Hover)
  vim.keymap.set("n", "K", vim.lsp.buf.hover, opts)
end

-- 套用至所有 Server
mason_lspconfig.setup_handlers({
  function(server_name)
    lspconfig[server_name].setup({
      on_attach = on_attach,
      settings = servers[server_name],
    })
  end,
})
```

---

## 4. 必備操作快捷鍵

| 功能 | 快捷鍵 | 說明 |
|---|---|---|
| 跳轉定義 | `gd` | 跳轉至函數或變數的定義處 |
| 返回位置 | `Ctrl + o` | 回到「上一個」看過的位置 (最常用) |
| 往前前進 | `Ctrl + i` | 回到「下一個」位置 |
| 查看引用 | `gr` | 列出整個專案哪裡有用到這個符號 |
| 返回標籤 | `Ctrl + t` | 按照標籤棧 (Tag Stack) 回退 |

---

## 5. 針對 C/C++ 的特別提醒 (關鍵步驟)

如果 `gd` 在 C/C++ 無法跨檔案跳轉，請檢查專案根目錄是否有 `compile_commands.json`。

- **CMake 專案**：`cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON .`
- **Makefile 專案**：安裝 bear 工具後執行 `bear -- make`
- **Linux Kernel**：執行 `python3 ./scripts/clang-tools/gen_compile_commands.py`

---

## 下一步建議

你可以先將此配置貼入 `init.lua`，並在 Neovim 執行 `:Mason` 檢查所有 LSP Server 是否已正確安裝。

需要針對特定的 Debug 偵錯工具 (DAP) 做進一步整理嗎？
