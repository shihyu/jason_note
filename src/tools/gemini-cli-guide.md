# Gemini CLI 在 Ubuntu 的安裝與 Bypass 使用說明

## 1. 安裝 Gemini CLI

### 前置需求

-   Node.js v18+
-   npm
-   Google 帳號 (OAuth)

### 安裝步驟

``` bash
# 安裝 Node.js via nvm
curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
source ~/.nvm/nvm.sh
nvm install 22
nvm use 22

# 安裝 gemini-cli
sudo npm install -g @google/gemini-cli

# 驗證
gemini --version
```

第一次執行會要求登入 Google 帳號並建立 `~/.gemini/settings.json`。

------------------------------------------------------------------------

## 2. Bypass / 自動化功能

### 2.1 --allowed-tools

允許特定工具自動執行而不需要手動確認：

``` bash
gemini --allowed-tools "ShellTool(git status),ShellTool(pwd)"
```

### 2.2 --approval-mode / --yolo

統一自動批准所有工具（高風險，不建議長期使用）：

``` bash
gemini --yolo
```

### 2.3 trust

在 config 中設定 `trust: true`，將繞過所有工具確認。僅限受信任環境。

### 2.4 API Key 直接登入

將 `GEMINI_API_KEY` 放入環境變數或 `.env`，可繞過 OAuth 登入。

------------------------------------------------------------------------

## 3. 安全風險與研究

-   Tracebit 研究指出若 bypass
    工具檢查，惡意命令可偽裝為合法工具並被執行。
-   有 Issue 提到 `.env` API key 會讓 CLI 自動跳過 onboarding。
-   Google 已在新版修正部分弱點，建議隨時更新。

------------------------------------------------------------------------

## 4. 安全建議

1.  **避免在不信任的資料夾執行 gemini-cli**。
2.  **盡量在 Docker / sandbox 環境使用**。
3.  **精確白名單**：只允許必要工具，避免廣泛 pattern。
4.  **避免將長期 API key 放在專案目錄**。
5.  **保持 gemini-cli 為最新版**。

------------------------------------------------------------------------

## 5. 範例設定檔

`~/.gemini/config.json`

``` json
{
  "approvalMode": "manual",
  "trust": false,
  "allowedTools": [
    "ShellTool(pwd)",
    "ShellTool(git status)"
  ]
}
```

------------------------------------------------------------------------

## 6. Docker 執行範例

``` dockerfile
FROM node:22-slim

RUN npm install -g @google/gemini-cli

WORKDIR /workspace
CMD ["gemini"]
```

------------------------------------------------------------------------

## 📌 結論

Gemini CLI 在 Ubuntu 安裝簡單，但 bypass
功能需謹慎使用。建議只在受信任、隔離的環境中使用
`--allowed-tools`，並避免使用 `--yolo` 或 `trust: true`。
