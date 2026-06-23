# Hermes Agent 安裝 + GLM 5.2 設定指南

## 環境需求

- Linux (Debian/Ubuntu 或任何發行版)
- `git`, `curl`, `xz-utils`
- Z.AI / 智譜 API Key

```bash
sudo apt install git curl xz-utils -y
```

---

## 1. 安裝 Hermes Agent

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

安裝完成後重新載入 shell：

```bash
source ~/.bashrc   # 或 source ~/.zshrc
```

驗證安裝：

```bash
hermes doctor
```

---

## 2. 設定 GLM 5.2 Provider

### 2.1 取得 API Key

到 [Z.AI Console](https://api.z.ai/) 取得 API Key。

### 2.2 寫入 API Key

```bash
hermes config set GLM_API_KEY "sk-your-z-ai-api-key"
```

這會自動寫入 `~/.hermes/.env`，Hermes 會從此讀取密鑰。

### 2.3 設定 Provider 與 Model

**方式一：互動式精靈（推薦）**

```bash
hermes model
```

選擇 `z.ai / GLM` → 選 `glm-5.2`。

**方式二：直接編輯 config**

編輯 `~/.hermes/config.yaml`：

```yaml
model:
  provider: "zai"
  default: "glm-5.2"
```

**方式三：Custom Provider（OpenAI 相容代理 / 第三方 endpoint）**

適用場景：使用 cmkey.cn、openrouter、或其他 OpenAI-compatible 代理。

`~/.hermes/.env`：

```bash
GLM_API_KEY=sk-your-actual-api-key
```

`~/.hermes/config.yaml`：

```yaml
model:
  default: glm-5.2
  provider: custom:glm

custom_providers:
  - name: glm
    base_url: https://cmkey.cn/v1
    key_env: GLM_API_KEY
    api_mode: chat_completions
```

> `api_mode: chat_completions` 表示使用 OpenAI `/v1/chat/completions` 格式。Hermes 支援 `chat_completions` 和 `anthropic_messages` 兩種模式。

---

## 3. Z.AI API Endpoint 參考

| Endpoint | Base URL | 用途 |
|---|---|---|
| Coding Plan（全球） | `https://api.z.ai/api/coding/paas/v4` | GLM-5.2 coding 場景 |
| 通用 API（全球） | `https://api.z.ai/api/paas/v4` | 標準對話 |
| 中國通用 | `https://open.bigmodel.cn/api/paas/v4` | 中國用戶 |
| OpenAI 相容 | `https://api.z.ai/api/openai/v1` | OpenAI SDK 相容 |
| Anthropic 相容 | `https://api.z.ai/api/anthropic` | Claude Code 相容 |
| cmkey.cn（代理） | `https://cmkey.cn/v1` | OpenAI 相容代理 |

---

## 4. 切換模型

**互動式切換：**
```bash
hermes model
```

**聊天中即時切換：**
```
/model glm-4.7 --provider zai
```

**永久設定（編輯 `~/.hermes/config.yaml`）：**
```yaml
model:
  provider: "zai"
  default: "glm-5.2"
```

---

## 5. 驗證測試

### 5.1 基本對話測試

```bash
hermes chat -q "Hello! What model are you running on? Reply with just the model name." --provider custom:glm --model glm-5.2
```

預期看到回覆為 `GLM-5.2` 或類似內容。

### 5.2 檢查設定

```bash
grep -E '^model\.|^custom_providers' ~/.hermes/config.yaml
```

預期輸出：
```
model:
  default: glm-5.2
  provider: custom:glm

custom_providers:
  - name: glm
    base_url: https://cmkey.cn/v1
    key_env: GLM_API_KEY
    api_mode: chat_completions
```

### 5.3 診斷檢查

```bash
hermes doctor
```

會檢查所有相依套件與 provider 連線狀態。

### 5.4 工具呼叫測試

```bash
hermes chat -q "列出目前目錄的檔案" --provider custom:glm --model glm-5.2
```

如果 agent 自動執行了 `ls` 並回傳結果，代表整個 agent loop（provider + tools）正常運作。

### 5.5 除錯模式

```bash
hermes chat --provider custom:glm --model glm-5.2 --verbose
```

查看 log：
```bash
tail -f ~/.hermes/logs/agent.log
tail -f ~/.hermes/logs/errors.log
```

---

## 6. 完整最小設定檔

`~/.hermes/config.yaml`：

```yaml
model:
  default: glm-5.2
  provider: custom:glm

custom_providers:
  - name: glm
    base_url: https://cmkey.cn/v1
    key_env: GLM_API_KEY
    api_mode: chat_completions

terminal:
  backend: local
```

`~/.hermes/.env`：

```bash
GLM_API_KEY=sk-your-actual-api-key
```

---

## 7. 常用指令速查

| 指令 | 說明 |
|---|---|
| `hermes chat` | 開始對話 |
| `hermes chat -q "..."` | 單次提問 |
| `hermes model` | 互動式切換模型 |
| `hermes doctor` | 系統診斷 |
| `hermes config show` | 查看完整設定 |
| `hermes config set KEY VALUE` | 設定 config 值 |
| `/model glm-5.2 --provider custom:glm` | 對話中切換模型 |
| `hermes dashboard` | 開啟 Web 儀表板（`http://127.0.0.1:9119`） |

---

## 8. 疑難排解

| 問題 | 解法 |
|---|---|
| `hermes: command not found` | `source ~/.bashrc` 或重開終端機 |
| Provider 沒出現在選單 | 先 `hermes config set GLM_API_KEY sk-...` 再 `hermes model` |
| API 呼叫失敗 | Z.AI 會自動探測 endpoint，查看 `~/.hermes/logs/agent.log` |
| `glm-5.2` 不在模型清單 | 試 `glm-5.1` 或 `/model custom:glm:glm-5.2` 強制指定 |
| Context window 太小 | GLM-5.2 支援 1M tokens，config 加 `context_length: 1000000` |
| cmkey.cn 連線失敗 | 確認 `GLM_API_KEY` 有效，檢查 `~/.hermes/logs/agent.log` |
