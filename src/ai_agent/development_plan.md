# AutoContent Loop 開發計畫 (Replication Kit)

這份文件是為了讓開發者朋友快速理解並復刻「AutoContent Loop (AI 分身系統)」所撰寫。

## 1. 專案核心概念

**"Put a UI on CLI"**

這個專案的核心不是重寫 AI 邏輯，而是為強大的 command-line 工具（這裡是 Gemini CLI）加上一個「手機遙控介面」（Telegram Bot）。

- **Backend**: 一台隨時開著的 Mac/Linux 電腦，跑 Python 腳本。
- **Core AI**: 使用 `gemini` CLI 工具（負責 Research, RAG, Content Generation）。
- **Frontend**: Telegram App（透過 Bot API 溝通）。

## 2. 技術棧 (Tech Stack)

| Component | Choice | Reason |
| :--- | :--- | :--- |
| **Language** | **Python 3.11+** | 豐富的 AI 生態系，原生支援 `asyncio` 和 `subprocess`。 |
| **Interface** | **python-telegram-bot** | 強大的 Async Telegram Client，支援 Inline keyboard (按鈕) 和狀態管理。 |
| **Core AI** | **Gemini CLI** | (關鍵) 不直接 Call API，而是用 `subprocess` 呼叫 CLI 工具，讓 CLI 處理複雜的 Tool Use / Memory。 |
| **Knowledge** | **NotebookLM** | 透過 Gemini CLI 的 MCP (Model Context Protocol) 整合 NotebookLM 進行 RAG。 |
| **Config** | **YAML** | 簡單易讀的 `config.yaml` 管理 Token 和 Prompts。 |

---

## 3. 系統架構 (Architecture)

```mermaid
graph TD
    User((User)) -- Telegram --> TGBot[Telegram Bot (Python)]
    
    subgraph "Local Machine (Mac/Linux)"
        TGBot -- 1. Receive Cmd --> Controller[Controller Logic]
        Controller -- 2. subprocess.run() --> CLI[Gemini CLI]
        
        CLI -- 3. Tool Use --> Tools[Tools (Browser/Files)]
        CLI -- 4. RAG --> NLM[NotebookLM]
        
        CLI -- 5. Stdout --> Controller
    end
    
    Controller -- 6. Reply Text/File --> User
```

**關鍵實作細節：**

1.  **Shell Wrapper**: Bot 不直接對接 OpenAI/Gemini API，而是「假裝自己是使用者」去敲 Terminal 指令。
2.  **Non-blocking**: 使用 `asyncio.get_event_loop().run_in_executor` 將耗時的 CLI 指令放到 Thread 跑，避免卡住 Telegram 訊息接收。
3.  **State Management**: 用一個簡單的 `dict` 紀錄每個 User 目前在 Pipeline 的哪個階段 (e.g. `WAITING_RESEARCH`, `WAITING_MELD`)。

---

## 4. 核心工作流 (The Pipeline)

專案目標是實現「內容生產流水線」，由以下四個階段組成：

### Phase 1: Research (吸納)
- **Input**: User 輸入關鍵字 (e.g., `/research 2026 AI 趨勢`)
- **Action**: Bot 呼叫 Gemini CLI 執行 Deep Research (自動搜尋、爬蟲)。
- **Output**: 建立一個 NotebookLM 筆記本，並回傳「摘要」與「Notebook ID」。

### Phase 2: Meld (觀點融合)
- **Input**: User 針對該主題輸入觀點 (e.g., `/meld 我覺得 AI 會讓人類更懶惰`)
- **Action**: Bot 將觀點丟給 AI，AI 扮演「挑戰者」角色，反問並激發更多思考。
- **Goal**: 讓 User 的個人風格 (Style) 與客觀資訊 (Research) 融合。

### Phase 3: Script (轉化)
- **Input**: 確認觀點後，User 下達 `/script`。
- **Action**: AI 根據 Research + Meld 的紀錄，生成 YouTube/Podcast 腳本。
- **Style**: 必須套用 User 的 Persona（專業顧問、親切口吻）。

### Phase 4: Distribute (分發)
- **Input**: User 選擇分發格式 (Video/Social Post)。
- **Action**:
    - **Video**: 呼叫 NotebookLM 生成 Audio/Video Overview。
    - **Social**: 根據腳本改寫成 FB/LinkedIn 貼文。

---

## 5. 開發步驟 (Step-by-Step)

### Step 1: 環境建置
1. 申請 Telegram Bot Token (@BotFather)。
2. 安裝依賴：`pip install python-telegram-bot pyyaml`。
3. 確認 `gemini` CLI 可以在 Terminal 正常運作。

### Step 2: 打造 Shell Wrapper
寫一個 Python function 用來執行 CLI 指令並抓取輸出：

```python
import subprocess

def call_gemini_cli(prompt):
    # 這裡的關鍵是用 subprocess 呼叫
    result = subprocess.run(
        ["gemini", "--no-stream", prompt], 
        capture_output=True, 
        text=True
    )
    return result.stdout
```

### Step 3: 接上 Telegram Bot
1. 建立 `Application` 與 `CommandHandler`。
2. 在 `/start` 或 `/research` 指令中，使用 `run_in_executor` 呼叫上面的 Wrapper。

```python
async def research_command(update, context):
    topic = " ".join(context.args)
    await update.message.reply_text("🔍 研究中，請稍候...")
    
    # 這是關鍵！不要讓 Bot 卡住
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, call_gemini_cli, f"Research: {topic}")
    
    await update.message.reply_text(result)
```

### Step 4: 狀態機與按鈕 (Interactive)
1. 使用 `InlineKeyboardMarkup` 製作按鈕 (e.g. `[生成腳本]`, `[再想一下]`)。
2. 實作 `CallbackQueryHandler` 處理按鈕點擊，推動 Pipeline 前進。

---

## 6. 給開發者的備忘錄 (Tips)

- **Timeout**: Deep Research 可能跑 3-5 分鐘，Telegram Bot 預設 timeout 可能太短，記得在 `subprocess.run` 和 HTTP client 把 timeout 拉長。
- **Privacy**: `gemini` CLI 會紀錄對話歷史，如果是多用戶共用，記得要處理 Session 隔離（或加上 `--session` 參數）。
- **Error Handling**: CLI 會有各種非預期輸出 (ANSI codes, Loading bars)，記得寫 Regex 清理 `stdout` 再傳回 Telegram。

祝開發順利！🚀
