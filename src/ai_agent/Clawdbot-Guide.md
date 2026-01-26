# Clawdbot 完整使用指南

## 目錄
1. [概念介紹](#概念介紹)
2. [核心功能](#核心功能)
3. [使用方法](#使用方法)
4. [常用指令](#常用指令)
5. [成本估算](#成本估算)
6. [安全警告](#安全警告)
7. [常見 Q&A](#常見qa)

---

## 概念介紹

### 什麼是 Clawdbot？

Clawdbot 是一款**開源的個人 AI 助手**，其核心理念是將 AI 能力下沈到用戶自己的設備上，而非依賴遠端雲端服務。

**核心特色**：
- 本地優先的架構（Local-first）
- 支援多通訊平台整合（WhatsApp、Telegram、Discord、Slack 等）
- 具有真正的行動能力（可操控電腦）
- 擁有複雜的記憶系統
- 完全開源免費

### 核心架構

```
你的通訊軟體 (WhatsApp/Telegram/等)
        ↓
   通訊平台伺服器
        ↓
你的電腦上的 Gateway（本地網關）
        ↓
Claude / ChatGPT / Gemini（本地運行）
        ↓
回覆訊息 + 執行任務
```

**重點**：所有 AI 運算都在你的電腦上進行，資料不上傳到任何第三方伺服器。

---

## 核心功能

### 1. 記憶與理解能力

Clawdbot 擁有真正的長期記憶機制，不同於 ChatGPT 每次都要重新提供背景。它會：

- 自動生成 Markdown 日記形式的「記憶檔案」，記錄每天的所有互動
- 記住你的偏好、習慣和過去的對話
- 甚至記得你兩週前隨口提過的一件小事，隨著時間推移越來越懂你

### 2. 主動出擊能力

與傳統 AI 被動等待不同，Clawdbot 會主動找你：

- **晨間簡報**：起床時自動發送當日行程、緊急郵件、待辦事項摘要
- **股票監控**：你關注的股票下跌時主動警報
- **天氣提醒**：明天天氣不好時提前通知
- **郵件提醒**：收到緊急郵件時立即通知

### 3. 真正的行動能力

Clawdbot 不只回答問題，它能直接操控你的電腦：

- **瀏覽器自動化**：自動登入網站、點擊、填表、截圖
- **Shell 命令執行**：運行程式、修改設定、安裝軟體
- **檔案系統操作**：讀寫檔案、整理資料夾
- **設備控制**：相機拍照、螢幕錄製（如有手機節點連接）

---

## 具體應用場景

| 功能類型 | 具體例子 | 備註 |
|---------|--------|------|
| **郵件管理** | 「取消訂閱所有新聞郵件」→ AI 自動登入並執行 | 完全自動化 |
| **行程管理** | 晨間自動發送今日行程、會議、待辦事項 | 每日自動觸發 |
| **研究助手** | 「找東京飯店附近 5 家最好的餐廳」→ 搜尋、比價、列清單 | 全在聊天完成 |
| **價格監控** | 「監控 Amazon 商品價格，降價時通知我」→ 每小時自動檢查並發截圖 | 24/7 運行 |
| **健康追蹤** | 「連接我的 WHOOP 帳戶」→ 每日自動獲取健康報告 | 5 分鐘設定 |
| **任務自動化** | 「每週五下午 5 點發送本週工作總結」 | 永久自動化 |
| **內容創作** | 「寫冥想詞、配音樂、每天早上自動發」→ 完全自動化 | 100% 無人介入 |
| **網站開發** | 使用者躺床上看 Netflix 時，傳一則訊息就能完成網站重建 | 真實案例 |
| **API 整合** | 連接 GitHub、Google Drive、Google Calendar、Todoist 等 | 無需手動配置 |
| **定時任務** | Cron 排程、Webhooks、Gmail Pub/Sub 觸發 | 完全自動化 |

---

## 使用方法：30 分鐘快速上手

### 第一步：選擇運行環境（5 分鐘）

#### 選項 A：使用免費 AWS 伺服器（推薦入門）

- 申請 AWS 免費方案，獲得 100 美元抵用金
- 啟動 EC2 實例（Ubuntu 系統）
- 完全免費運行 Clawdbot

#### 選項 B：本地電腦運行

- 直接在 macOS、Linux、Windows（WSL2）上安裝
- 設備需求：1GB 記憶體以上

#### 選項 C：便宜的 VPS

- 如 Hetzner 的 5 美元/月伺服器
- 官方推薦方案

### 第二步：安裝 Clawdbot（3 分鐘）

在終端機執行一行指令即可：

```bash
curl -fsSL https://clawd.bot/install.sh | bash
```

安裝完成後會自動跳出設定精靈。

### 第三步：選擇 AI 模型與通訊方式（10 分鐘）

設定精靈會引導你選擇：

#### 1. 選擇 AI 模型

- **Claude（Anthropic）** - 官方推薦，長上下文記憶能力強，抗提示詞注入
- **ChatGPT（OpenAI）** - 可選，根據個人偏好
- **Gemini（Google）** - 可選

#### 2. 獲取 API Token

系統會要求你：
- 在自己電腦執行指令生成 Token，或
- 在瀏覽器登入 LLM 帳號

**OpenAI 例子**：
1. 訪問 `platform.openai.com/api-keys`
2. 點擊「Create new secret key」
3. 複製 Token 貼回設定精靈

#### 3. 選擇通訊平台

支援的平台：
- Telegram（最推薦，設定最簡單）
- WhatsApp
- Discord
- Slack
- Signal
- Microsoft Teams
- Google Chat
- iMessage（macOS 限定）
- **未來**：LINE（待開發）

### 第四步：連接通訊軟體（5 分鐘，以 Telegram 為例）

#### Telegram 連接步驟

1. 打開 Telegram，搜尋 `@botfather`
2. 發送指令 `/newbot`
3. BotFather 給你一串 Token，複製它
4. 貼回 Clawdbot 設定精靈
5. 回到 Telegram，機器人會詢問設定身份：
   - 你該叫我什麼名字？
   - 你該叫我什麼？
   - 我的存在目的是什麼？
   - 你在哪個時區？
6. 完成！機器人已上線

#### 其他平台連接

**WhatsApp**：
```bash
clawdbot channels login
```
然後掃描二維碼連結設備

**Discord/Slack**：
- 設定相應的 Bot Token

### 第五步：可選 - 啟用高級功能（額外 5 分鐘）

#### 開啟聯網搜尋

```
Set up Brave search with this API key: [你的 Key]
```

在 `brave.com/search/api` 申請免費 API Key

#### 連接外部服務

- GitHub
- Google Drive
- Google Calendar
- Todoist
- WHOOP 運動手環
- 等等

---

## OAuth 配置完整指南

### 概述

Clawdbot 支援三種主流 AI 模型，全部使用 OAuth 認證（更安全，無需手動管理 API Key）：

| AI Model | Provider | 認證方式 | 有效期 |
|----------|----------|----------|--------|
| **Claude Opus 4.5** | Anthropic | OAuth | ~5 小時 |
| **Gemini 3 Pro** | Google | OAuth | ~1 小時 |
| **Codex** | OpenAI | OAuth | ~10 天 |

### 1. 啟用 OAuth Plugins

```bash
# 啟用 Gemini OAuth plugin
clawdbot plugins enable google-gemini-cli-auth

# 重啟 gateway 套用變更
clawdbot gateway restart
```

### 2. 執行 OAuth 登入

#### Claude OAuth
```bash
clawdbot models auth login --provider anthropic
```
- 會開啟瀏覽器
- 登入你的 Anthropic 帳號
- 授權完成後自動儲存 token

#### Gemini OAuth
```bash
clawdbot models auth login --provider google-gemini-cli
```
- 會開啟瀏覽器
- 登入 Google 帳號
- 授權 Gemini CLI 存取權限

#### Codex (OpenAI) OAuth
```bash
clawdbot models auth login --provider openai-codex
```
- 會開啟瀏覽器
- 登入 ChatGPT 帳號（需要 Plus 訂閱）
- 授權完成後自動儲存

### 3. 檢查認證狀態

```bash
# 查看所有 model 的認證狀態
clawdbot models status

# 查看 OAuth token 有效期
clawdbot models status | grep -A 10 "OAuth/token status"
```

**範例輸出：**
```
OAuth/token status
- anthropic usage: 5h 45% left ⏱2h 16m
  - anthropic:claude-cli expiring expires in 52m (claude-cli)
- google-gemini-cli usage: Pro 100% left · Flash 100% left
  - google-gemini-cli:jason@example.com expiring expires in 54m
- openai-codex usage: 5h 100% left ⏱5h · Day 100% left ⏱Feb 2
  - openai-codex:codex-cli ok expires in 10d (codex-cli)
```

### 4. 設定預設 Model

```bash
# 查看可用的 models
clawdbot models list

# 設定預設 model（選擇一個）
clawdbot models set anthropic/claude-opus-4-5           # Claude
clawdbot models set google-gemini-cli/gemini-3-pro-preview  # Gemini
clawdbot models set openai-codex/gpt-4o                 # Codex

# 查看當前設定
clawdbot models status | grep "Default"
```

### 5. 測試三種 Model

#### ⚠️ 重要：agent 指令需要指定 session

使用 `clawdbot agent` 指令時，**必須**加上以下其中一個參數：
- `--session-id <id>` - 指定 session ID（最簡單，適合測試）
- `--to <E.164>` - 指定電話號碼（例如：+886912345678）
- `--agent <id>` - 指定 agent ID

#### 方式 1：使用 clawdbot agent 指令測試

```bash
# ✅ 測試 Claude Opus 4.5（推薦，最穩定）
clawdbot models set anthropic/claude-opus-4-5
clawdbot agent --session-id test-claude --message "你好，請用繁體中文自我介紹" --json

# ⚠️ 測試 Gemini 3 Pro（可能遇到容量不足 429 錯誤）
clawdbot models set google-gemini-cli/gemini-3-pro-preview
clawdbot agent --session-id test-gemini --message "你好，請用繁體中文自我介紹" --json

# ❌ 測試 Codex（目前 model 不可用）
# clawdbot models set openai-codex/gpt-4o
# clawdbot agent --session-id test-codex --message "你好，請用繁體中文自我介紹" --json
# 註：OpenAI Codex 可能需要特殊配置或 model ID 不正確
```

#### 方式 2：在通訊軟體中測試（推薦）

發送訊息到你的 Telegram/WhatsApp bot：
```
你好，請自我介紹一下
```

通訊軟體中的測試會自動使用預設 model，無需指定 session-id。切換 model 後再測試以比較回應風格。

#### 測試結果預期

**Claude Opus 4.5** 回應範例：
```json
{
  "status": "ok",
  "result": {
    "payloads": [{
      "text": "你好！我是 Claude，由 Anthropic 公司開發的 AI 助手..."
    }],
    "meta": {
      "agentMeta": {
        "provider": "anthropic",
        "model": "claude-opus-4-5",
        "usage": {
          "input": 10,
          "output": 472
        }
      }
    }
  }
}
```

**Gemini 3 Pro** 可能的錯誤：
```
Cloud Code Assist API error (429): No capacity available for model gemini-3-pro-preview on the server
```
→ 這是 Google 伺服器容量不足，稍後再試或使用其他 model

**Codex** 可能的錯誤：
```
Error: Unknown model: openai-codex/gpt-4o
```
→ 檢查 model 名稱是否正確，或查看 `clawdbot models list` 確認可用的 models

### 6. Token 更新管理

#### 自動更新（推薦）
OAuth tokens 會在接近過期時自動更新（如果有 refresh token）。

#### 手動更新
如果 token 過期，重新執行登入即可：
```bash
clawdbot models auth login --provider anthropic
clawdbot models auth login --provider google-gemini-cli
clawdbot models auth login --provider openai-codex
```

### 7. 移除舊的 API Keys（可選）

如果之前用 API Key 方式設定，現在改用 OAuth，可以清理環境變數：

```bash
# 檢查哪裡設定了 API Keys
grep -r "ANTHROPIC_API_KEY\|GEMINI_API_KEY\|OPENAI_API_KEY" \
  ~/.bashrc ~/.zshrc ~/.profile ~/.bash_profile 2>/dev/null

# 編輯對應檔案移除這些環境變數
vim ~/.bashrc  # 或其他檔案

# 重新載入環境
source ~/.bashrc
```

### 8. 疑難排解

#### 問題：OAuth 登入失敗
```bash
# 檢查 gateway 是否運行
clawdbot gateway status

# 重啟 gateway
clawdbot gateway restart

# 檢查是否有錯誤
clawdbot logs --tail 50
```

#### 問題：Token 過期
```bash
# 重新登入即可
clawdbot models auth login --provider <provider-name>
```

#### 問題：找不到認證檔案
```bash
# 檢查認證檔案位置
ls -la ~/.clawdbot/agents/main/agent/auth-profiles.json

# 查看檔案內容（確認 token 存在）
cat ~/.clawdbot/agents/main/agent/auth-profiles.json | jq '.profiles | keys'
```

#### 問題：agent 指令要求 session-id
```
Error: Pass --to <E.164>, --session-id, or --agent to choose a session
```

**解決方案**：agent 指令必須指定 session，使用以下任一參數：

```bash
# 方法 1：使用 session-id（最簡單，適合測試）
clawdbot agent --session-id test --message "你好" --json

# 方法 2：使用電話號碼（E.164 格式）
clawdbot agent --to +886912345678 --message "你好" --json

# 方法 3：指定 agent ID
clawdbot agent --agent main --message "你好" --json
```

#### 問題：Model 不可用 (Unknown model)
```
Error: Unknown model: openai-codex/gpt-4o
```

**解決方案**：

```bash
# 1. 檢查可用的 models
clawdbot models list | grep -v "missing"

# 2. 檢查 OAuth 認證狀態
clawdbot models status

# 3. 使用確認可用的 model
clawdbot models set anthropic/claude-opus-4-5  # 推薦
```

#### 問題：Gemini 容量不足 (429 Error)
```
Cloud Code Assist API error (429): No capacity available for model gemini-3-pro-preview
```

**解決方案**：
- Google 伺服器暫時容量不足
- 稍後再試（通常幾分鐘到幾小時後恢復）
- 或切換到其他 model（Claude 或 Codex）

---

## 遠端控制電腦的原理

### 運作流程

1. 你用通訊軟體（WhatsApp/Telegram/等）發送命令
2. 通訊平台伺服器將訊息轉發到你電腦上的 Clawdbot Gateway
3. Gateway 將命令傳給 Claude/ChatGPT 等 AI 模型
4. AI 執行實際操作：
   - 控制瀏覽器（自動化點擊、填表、登入）
   - 執行 Shell 命令（運行程式、修改檔案）
   - 存取檔案系統（讀寫資料夾）
5. 完成後，結果（文字、截圖、檔案等）透過通訊軟體回傳給你

### LINE 整合（未來支援）

雖然目前 LINE 還未整合，但一旦支援，流程將是：

```
你的 LINE 應用
    ↓
LINE 伺服器
    ↓
你的電腦 Gateway
    ↓
Claude/ChatGPT
    ↓
回覆 + 執行任務
```

---

## 常用指令

### 通訊軟體中的指令

在任何通訊軟體（Telegram/WhatsApp/Discord 等）中可使用：

| 指令 | 功能 |
|-----|------|
| `/status` | 查看會話狀態（模型、token 數、費用） |
| `/new` 或 `/reset` | 重設對話 |
| `/compact` | 壓縮會話記憶 |
| `/think <等級>` | 設定 AI 思考深度（off/minimal/low/medium/high/xhigh） |
| `/verbose on\|off` | 開關詳細模式 |
| `/usage off\|tokens\|full` | 設定費用顯示 |

### CLI 命令行指令

#### Gateway 管理

```bash
# 啟動 gateway
clawdbot gateway

# 強制啟動（自動 kill 佔用的 port）
clawdbot gateway --force

# 指定 port
clawdbot gateway --port 18789

# 查看 gateway 狀態
clawdbot gateway status

# 重啟 gateway
clawdbot gateway restart

# 停止 gateway
clawdbot gateway stop

# 查看即時 logs
clawdbot logs --tail 50

# 持續監看 logs
clawdbot logs --follow
```

#### Model 管理

```bash
# 列出所有可用 models
clawdbot models list

# 查看 model 認證狀態
clawdbot models status

# 設定預設 model
clawdbot models set anthropic/claude-opus-4-5

# OAuth 登入
clawdbot models auth login --provider anthropic
clawdbot models auth login --provider google-gemini-cli
clawdbot models auth login --provider openai-codex

# 查看認證 profiles
clawdbot models auth order
```

#### Agent 管理

```bash
# 列出所有 agents
clawdbot agents list

# 添加新 agent
clawdbot agents add

# 刪除 agent
clawdbot agents delete <agent-id>

# 發送訊息給 agent
clawdbot agent --message "你好" --json

# 指定 agent 處理
clawdbot agent --agent ops --message "產生報告"

# 指定 session
clawdbot agent --to +886912345678 --message "查詢狀態"

# 直接傳送回覆到通訊軟體
clawdbot agent --message "總結今天的工作" --deliver

# 本地執行（不透過 Gateway）
clawdbot agent --local --message "分析程式碼"
```

#### 通訊頻道管理

```bash
# 查看頻道狀態
clawdbot channels status

# 登入頻道（例如 WhatsApp）
clawdbot channels login

# 查看 sessions
clawdbot sessions

# 發送訊息
clawdbot message send --target +886912345678 --message "Hi" --json
```

#### Plugin 管理

```bash
# 列出所有 plugins
clawdbot plugins list

# 查看 plugin 詳情
clawdbot plugins info <plugin-id>

# 啟用 plugin
clawdbot plugins enable <plugin-id>

# 停用 plugin
clawdbot plugins disable <plugin-id>

# 安裝 plugin
clawdbot plugins install <path-or-npm-spec>

# 更新 plugins
clawdbot plugins update
```

#### 系統診斷

```bash
# 健康檢查
clawdbot doctor

# 系統健康狀態
clawdbot health

# 查看頻道和 session 狀態
clawdbot status

# 配置管理
clawdbot config get <path>
clawdbot config set <path> <value>
clawdbot config unset <path>
```

#### 其他工具

```bash
# 開啟控制面板
clawdbot dashboard

# 查看 cron 排程
clawdbot cron

# 記憶體搜尋
clawdbot memory

# 瀏覽器管理
clawdbot browser

# 沙箱工具
clawdbot sandbox

# 更新 CLI
clawdbot update

# 重設配置
clawdbot reset

# 完全移除
clawdbot uninstall
```

#### 快速檢查指令組合

```bash
# 全面狀態檢查
clawdbot gateway status && \
clawdbot models status && \
clawdbot channels status && \
clawdbot agents list

# 重啟並檢查
clawdbot gateway restart && \
sleep 3 && \
clawdbot health

# 查看最近錯誤
clawdbot logs --tail 100 | grep -i error
```

#### 測試連線

```bash
# ✅ 測試 Claude（最穩定）
clawdbot models set anthropic/claude-opus-4-5
clawdbot agent --session-id test-claude --message "測試 Claude 連線" --json | jq '.result.payloads[0].text'

# ⚠️ 測試 Gemini（可能遇到容量不足）
clawdbot models set google-gemini-cli/gemini-3-pro-preview
clawdbot agent --session-id test-gemini --message "測試 Gemini 連線" --json | jq '.result.payloads[0].text'

# ❌ 測試 Codex（目前不可用，需要檢查 model 配置）
# clawdbot models set openai-codex/gpt-4o
# clawdbot agent --session-id test-codex --message "測試 Codex 連線" --json | jq '.result.payloads[0].text'

# 簡化測試（不使用 jq，查看完整 JSON）
clawdbot agent --session-id test --message "Hello" --json
```

### 實際使用例子

```
你：「查查看今天有沒有重要郵件」
機器人：「你有 3 封郵件：1 件來自老闆，2 件來自客戶，我已幫你分類。」

你：「監控 Amazon 上 iPhone 15 的價格，降到 $700 以下就通知我」
機器人：「✓ 已設定監控，每小時檢查一次。」
[6 小時後]
機器人：「✓ 價格降到 $699！[截圖]」

你：「幫我在 Excel 帳本裡找過去一年最貴的一筆支出」
機器人：「找到了！2025 年 3 月買的 MacBook Pro，花費 $3,200。我也列出了前 10 大支出。」
```

---

## 成本估算

### 月度成本分析

| 項目 | 成本 |
|-----|------|
| 軟體 | 免費（開源） |
| 伺服器 | $0-50/月（AWS 免費 1 年，或 $5 VPS） |
| AI 模型費用 | $3-100/月（Claude Pro $20，或按 API 用量計費） |
| **總計** | **$3-150/月** |

**成本對比**：
- 傳統人類助理：月薪 $2,000+
- Clawdbot：$20-30/月
- **節省**：90% 以上

### 如何控制成本

1. **設定硬上限**：在 OpenAI 的「Billing」設定中設定上限金額（如 $20），超過後機器人自動停止

2. **選擇便宜模型**：
   - Claude API：按 token 計費，便宜
   - OpenAI：也很便宜，個人用途通常 $3-10/月

3. **使用 AWS 免費層**：第一年完全免費

---

## 安全警告 ⚠️

### 絕對不要在以下電腦上安裝 Clawdbot

- **有加密貨幣錢包或私鑰的設備**
- **存有重要財務資訊的機器**
- **有高度安全敏感性的工作電腦**

### 為什麼這麼危險？

1. Clawdbot 需要 Shell 存取與完整檔案系統讀寫權限（相當於開啟一個巨大後門）
2. 一旦 AI 被提示詞注入攻擊或誤判，可能執行危險操作
3. 有可能不小心安裝病毒或刪除重要檔案
4. 歷史例子：有人不小心讓 AI 刪除了他的整個資料庫

### 安全防護措施

#### DM 配對模式
- 陌生人先收到配對碼確認
- 確認前機器人不執行任何指令

#### 白名單控制
- 設定 `allowFrom` 限制互動用戶
- 只允許特定 LINE/Telegram 帳號

#### 沙箱隔離
- 群組中的非主會話在 Docker 沙盒運行
- 防止誤操作影響系統

#### 診斷工具
```bash
clawdbot doctor
```
執行此命令檢查潛在安全風險

### 最佳實踐

1. **用獨立電腦運行**：
   - 買一台 Mac mini（$600）或便宜 VPS（$5/月）
   - 不要在主電腦安裝

2. **定期審查**：
   - 定期檢查機器人執行了什麼操作
   - 保持 Clawdbot 軟體更新

3. **限制權限**：
   - 不要給 Clawdbot 存取銀行帳戶、加密錢包等敏感設備
   - 只在非關鍵系統上運行

4. **啟用所有防護**：
   - 啟用 DM 配對模式
   - 設定白名單
   - 啟用沙箱隔離

---

## 常見 Q&A

### Q：我不懂技術，能安裝嗎？

**A**：可以。Clawdbot 只需要複製貼上命令，按照引導精靈走。不會編碼也沒關係，遇到問題可以問 ChatGPT。目前網路上已有大量教學影片。

### Q：如果聊太多會不會破產？

**A**：可以設定硬上限。在 OpenAI 的「Billing」設定中設定上限金額（如 $20），超過後機器人自動停止，不會刷爆信用卡。

### Q：機器人壞掉了怎麼辦？

**A**：99% 的問題重啟即可。重新登入伺服器，執行：

```bash
NODE_OPTIONS="--max-old-space-size=2048" clawdbot gateway --force
```

### Q：我有 ChatGPT Plus ($20/月)，為什麼還要付 API 費用？

**A**：這是兩個不同的錢包：
- ChatGPT Plus：網頁吃到飽，$20/月
- API：機器人計量付費，個人用途通常只需 $3-10/月

兩者互不影響，可以都訂，或只訂其中一個。

### Q：線上時數有限制嗎？

**A**：沒有。Clawdbot 在雲端伺服器上 24/7 自動運行，即使你關電腦也不影響。

### Q：我可以同時連接多個通訊軟體嗎？

**A**：完全可以。你可以同時在 WhatsApp、Telegram、Discord、Slack 中都連接同一個 Clawdbot，所有會話共享同一份記憶。

### Q：Clawdbot 會記得我多久以前的事？

**A**：理論上永久記得。Clawdbot 會自動生成 Markdown 日記，記錄每天的所有互動。你可以隨時查詢幾個月前的對話。

### Q：如果我換了 AI 模型（從 Claude 改成 ChatGPT），會不會丟失記憶？

**A**：不會。Clawdbot 的記憶系統獨立於 LLM，所以換模型不影響記憶。

### Q：GitHub 上有多少開發者在維護這個專案？

**A**：截至 2026 年 1 月，Clawdbot 已達約 24,600 顆星，擁有超過 280 位貢獻者，是非常活躍的開源專案。

---

## 下一步行動

### 立即開始（5 分鐘）

1. 選擇運行環境（AWS / 本地 / VPS）
2. 執行安裝指令
3. 連接 Telegram
4. 發送第一條訊息給機器人

### 深度配置（30 分鐘）

1. 連接多個通訊軟體（WhatsApp、Discord 等）
2. 設定聯網搜尋
3. 連接外部服務（Google Calendar、GitHub 等）
4. 設定定時任務

### 進階應用（1-2 小時）

1. 設定自動化工作流（如晨間簡報）
2. 建立自訂指令
3. 整合特殊業務流程
4. 與團隊共享使用

---

## 資源連結

- **GitHub**：https://github.com/clawdbot/clawdbot
- **官網**：https://clawd.bot
- **文件**：https://docs.clawd.bot
- **社群**：GitHub Discussions、Discord

---

## 總結

**Clawdbot = ChatGPT + Siri + 自動化機器 + 完整記憶**

- **ChatGPT 的能力**：可以思考、分析、寫作
- **Siri 的形態**：整合進你的日常通訊軟體，隨時召喚
- **自動化機器**：真的能控制電腦執行任務
- **完整記憶**：記得所有細節，越用越懂你

用 30 分鐘、花費每月 $20-30，你就能擁有一個真正的 **AI 超級秘書**。

---

## 快速參考卡

### 每日檢查指令
```bash
# 查看系統狀態
clawdbot gateway status
clawdbot models status
clawdbot health

# 查看 OAuth 有效期
clawdbot models status | grep "expires in"

# 查看最近 logs
clawdbot logs --tail 20
```

### OAuth 更新（Token 過期時）
```bash
# Claude
clawdbot models auth login --provider anthropic

# Gemini
clawdbot models auth login --provider google-gemini-cli

# Codex
clawdbot models auth login --provider openai-codex
```

### 切換 Model
```bash
# 切換到 Claude
clawdbot models set anthropic/claude-opus-4-5

# 切換到 Gemini
clawdbot models set google-gemini-cli/gemini-3-pro-preview

# 切換到 Codex
clawdbot models set openai-codex/gpt-4o
```

### 重啟 Gateway（遇到問題時）
```bash
# 標準重啟
clawdbot gateway restart

# 強制重啟（清理舊 process）
clawdbot gateway stop
sleep 2
clawdbot gateway --force
```

### 測試 AI 回應
```bash
# 快速測試（使用當前預設 model，必須指定 session-id）
clawdbot agent --session-id test --message "測試連線" --json

# 測試特定 model
clawdbot agent --session-id test-claude --message "你是什麼 AI?" --json

# 測試並傳送到通訊軟體（需要先設定通訊頻道）
clawdbot agent --session-id test --message "測試訊息" --deliver --reply-channel telegram
```

### 記憶檔案位置
```bash
# Agent 記憶體目錄
~/.clawdbot/agents/main/agent/

# 認證檔案
~/.clawdbot/agents/main/agent/auth-profiles.json

# 配置檔案
~/.clawdbot/clawdbot.json

# Logs 目錄
/tmp/clawdbot/
```

### 故障排除 Checklist

1. **Gateway 無法啟動**
   ```bash
   clawdbot gateway status
   clawdbot doctor
   lsof -i :18789  # 檢查 port 是否被佔用
   ```

2. **OAuth 過期**
   ```bash
   clawdbot models status | grep "expiring"
   clawdbot models auth login --provider <provider>
   ```

3. **Agent 無回應**
   ```bash
   clawdbot health
   clawdbot logs --tail 50
   clawdbot gateway restart
   ```

4. **通訊頻道離線**
   ```bash
   clawdbot channels status
   clawdbot channels login
   ```

### 效能優化
```bash
# 檢查記憶體使用
ps aux | grep clawdbot

# 設定記憶體限制
NODE_OPTIONS="--max-old-space-size=2048" clawdbot gateway --force

# 清理舊 sessions
clawdbot sessions | grep -i inactive
```

### 備份重要資料
```bash
# 備份配置和認證
tar -czf clawdbot-backup-$(date +%Y%m%d).tar.gz \
  ~/.clawdbot/clawdbot.json \
  ~/.clawdbot/agents/main/agent/auth-profiles.json

# 還原備份
tar -xzf clawdbot-backup-YYYYMMDD.tar.gz -C ~/
```

---

## 進階技巧

### 1. 多 Agent 配置

不同的 agent 可以用不同的 model：

```bash
# 添加專用 agent
clawdbot agents add

# 為不同 agent 設定不同的 workspace
# 編輯 ~/.clawdbot/clawdbot.json
{
  "agents": {
    "main": { "model": "anthropic/claude-opus-4-5" },
    "research": { "model": "google-gemini-cli/gemini-3-pro-preview" },
    "coding": { "model": "openai-codex/gpt-4o" }
  }
}
```

### 2. 設定 Fallback Models

當主 model 失敗時自動切換：

```bash
# 設定 fallback 順序
clawdbot models fallbacks add anthropic/claude-opus-4-5
clawdbot models fallbacks add google-gemini-cli/gemini-3-pro-preview
clawdbot models fallbacks add openai-codex/gpt-4o

# 查看 fallback 設定
clawdbot models status | grep Fallbacks
```

### 3. 定時 Token 更新

建立 cron job 自動更新 OAuth tokens：

```bash
# 編輯 crontab
crontab -e

# 每 4 小時更新 Claude token
0 */4 * * * clawdbot models auth login --provider anthropic 2>&1 | logger -t clawdbot-auth

# 每小時更新 Gemini token
0 * * * * clawdbot models auth login --provider google-gemini-cli 2>&1 | logger -t clawdbot-auth
```

### 4. 監控腳本

建立簡單的監控腳本：

```bash
#!/bin/bash
# ~/monitor-clawdbot.sh

echo "=== Clawdbot 狀態檢查 ==="
echo "時間: $(date)"
echo ""

# Gateway 狀態
echo "Gateway:"
clawdbot gateway status | grep "Runtime"

# Model 認證
echo -e "\nModel OAuth 狀態:"
clawdbot models status | grep -A 3 "OAuth/token status"

# 錯誤檢查
echo -e "\n最近錯誤:"
clawdbot logs --tail 100 | grep -i error | tail -5

echo "======================"
```

使用：
```bash
chmod +x ~/monitor-clawdbot.sh
~/monitor-clawdbot.sh
```

---

## 社群資源

### 官方資源
- **GitHub**: https://github.com/clawdbot/clawdbot
- **官網**: https://clawd.bot
- **文件**: https://docs.clawd.bot
- **Discord**: https://discord.gg/clawdbot

### 學習資源
- YouTube 教學影片搜尋: "Clawdbot tutorial"
- Reddit: r/clawdbot
- Twitter/X: #clawdbot

### 疑難排解
- GitHub Issues: 報告 bug 和功能請求
- Discord #support: 即時支援
- Stack Overflow: [clawdbot] tag

---

*文件更新日期：2026 年 1 月 26 日*
*版本：2.0 - 新增 OAuth 完整指南和 CLI 指令參考*