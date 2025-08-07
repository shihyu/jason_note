# Slack Socket Mode 完整設定指南

## 🎯 目標
使用 Python 監控 Slack 頻道訊息

## 📋 前置作業

### 1. 建立 Slack App

1. 前往 [Slack API 網站](https://api.slack.com/apps)
2. 點擊 **"Create New App"**
3. 選擇建立方式：
   - **From scratch**: 從零開始建立（需手動設定）
   - **From an app manifest**: 使用預設檔案（推薦快速設定）

#### 如果選擇 From an app manifest，使用以下設定：

```yaml
display_information:
  name: Message Monitor
description:
  Simple message monitoring bot
features:
  bot_user:
    display_name: Monitor Bot
oauth_config:
  scopes:
    bot:
      - channels:history
      - channels:read
      - chat:write
settings:
  event_subscriptions:
    bot_events:
      - message.channels
  interactivity:
    is_enabled: false
  org_deploy_enabled: false
  socket_mode_enabled: true
  token_rotation_enabled: false
```

### 2. 設定權限 (如果選擇 From scratch)

1. 左側選單 → **"OAuth & Permissions"**
2. 在 **"Bot Token Scopes"** 添加：
   - `channels:history` - 讀取頻道歷史
   - `channels:read` - 讀取頻道資訊
   - `chat:write` - 發送訊息
3. 點擊 **"Install to Workspace"**
4. 授權後取得 **Bot User OAuth Token** (xoxb-開頭)

### 3. 啟用 Socket Mode

1. 左側選單 → **"Socket Mode"**
2. 開啟 **"Enable Socket Mode"**
3. 建立 App-Level Token：
   - 輸入 Token 名稱
   - 勾選 `connections:write` scope
   - 點擊 **"Generate"**
4. 取得 **App-Level Token** (xapp-開頭)

### 4. 設定事件訂閱 (如果選擇 From scratch)

1. 左側選單 → **"Event Subscriptions"**
2. 開啟 **"Enable Events"**
3. 在 **"Subscribe to bot events"** 添加：
   - `message.channels` - 頻道訊息事件

## 🔧 Python 程式設定

### 1. 安裝必要套件

```bash
pip install slack-bolt
```

### 2. 基本監控程式碼

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

# 替換成你的 tokens
SLACK_BOT_TOKEN = "xoxb-你的-bot-token"
SLACK_APP_TOKEN = "xapp-你的-app-token"

# 初始化 Slack App
app = App(token=SLACK_BOT_TOKEN)

# 監聽所有頻道訊息
@app.message("")
def handle_message(message, say):
    user = message.get('user', '未知使用者')
    text = message.get('text', '')
    channel = message.get('channel', '')
    
    print(f"頻道: {channel}")
    print(f"使用者: {user}")
    print(f"訊息: {text}")
    print("-" * 50)

# 啟動應用程式
if __name__ == "__main__":
    print("🚀 開始監控 Slack 頻道訊息...")
    print("按 Ctrl+C 停止程式")
    
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
```

### 3. 除錯版本程式碼

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging

# 啟用詳細日誌
logging.basicConfig(level=logging.DEBUG)

# 你的 tokens
SLACK_BOT_TOKEN = "xoxb-你的-bot-token"
SLACK_APP_TOKEN = "xapp-你的-app-token"

# 初始化 Slack App
app = App(token=SLACK_BOT_TOKEN)

# 監聽所有事件來除錯
@app.event("message")
def handle_message_event(event, say, logger):
    logger.info(f"收到事件: {event}")
    
    # 避免處理 bot 自己的訊息
    if event.get('bot_id') or event.get('subtype'):
        print(f"⏭️  忽略 bot 訊息或特殊訊息: {event.get('subtype', 'bot_message')}")
        return
    
    user = event.get('user', '未知使用者')
    text = event.get('text', '')
    channel = event.get('channel', '')
    
    print(f"✅ 收到訊息！")
    print(f"頻道: {channel}")
    print(f"使用者: {user}")
    print(f"訊息: {text}")
    print(f"時間戳: {event.get('ts', '')}")
    print("-" * 50)

# 監聽連接狀態
@app.event("hello")
def handle_hello(event, logger):
    logger.info("Socket Mode 連接成功！")
    print("🎉 成功連接到 Slack！")

# 監聽錯誤
@app.error
def custom_error_handler(error, body, logger):
    logger.exception(f"錯誤: {error}")
    print(f"❌ 發生錯誤: {error}")

# 測試連接
def test_connection():
    try:
        response = app.client.api_test()
        if response["ok"]:
            print("✅ API 連接正常")
        else:
            print("❌ API 連接失敗")
    except Exception as e:
        print(f"❌ API 測試失敗: {e}")

if __name__ == "__main__":
    print("🚀 開始監控 Slack 頻道訊息...")
    print("🔧 除錯模式啟用")
    
    # 測試連接
    test_connection()
    
    # 啟動 Socket Mode
    try:
        handler = SocketModeHandler(app, SLACK_APP_TOKEN)
        print("⚡ Socket Mode Handler 啟動中...")
        handler.start()
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
```

## 🏃‍♂️ 執行和測試

### 1. 取得必要的 Tokens

#### Bot Token 位置：
- 路徑：**OAuth & Permissions** → **"OAuth Tokens for Your Workspace"**
- 格式：`xoxb-` 開頭
- 用途：API 呼叫

#### App Token 位置：
- 路徑：**Socket Mode** → **App-Level Tokens**
- 格式：`xapp-` 開頭
- 用途：Socket Mode 連接

### 2. 邀請 Bot 到頻道

**重要：Bot 必須被邀請到頻道才能監控！**

在目標頻道中輸入：
```
/invite @你的bot名稱
```

或透過頻道設定手動加入 Bot。

### 3. 執行程式

```bash
python your_script.py
```

### 4. 測試驗證

1. 確認看到 "🎉 成功連接到 Slack！"
2. 在已邀請 Bot 的頻道發送訊息
3. 觀察終端機是否有輸出

## 🔍 監控範圍說明

### ✅ 會監控到的訊息：
- **公開頻道**中的訊息（Bot 已加入）
- **私人頻道**中的訊息（Bot 已被邀請）
- **直接提及 Bot** 的訊息

### ❌ 不會監控到的訊息：
- **私人訊息**（除非直接傳給 Bot）
- Bot **未加入**的頻道
- Bot **沒有權限**的頻道

## 🎛️ 進階設定

### 監控特定頻道

```python
TARGET_CHANNEL = "C1234567890"  # 替換成你的頻道 ID

@app.message("")
def handle_message(message, say):
    channel = message.get('channel', '')
    
    if channel == TARGET_CHANNEL:
        # 只處理特定頻道的訊息
        user = message.get('user', '未知使用者')
        text = message.get('text', '')
        print(f"✅ 目標頻道訊息！")
        print(f"頻道: {channel}")
        print(f"使用者: {user}")
        print(f"訊息: {text}")
```

### 取得頻道 ID

1. 在 Slack 中右鍵點擊頻道名稱
2. 選擇「複製連結」
3. 連結中的 `/C123456789/` 就是頻道 ID

### 環境變數設定（推薦）

建立 `.env` 檔案：
```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token-here
SLACK_APP_TOKEN=xapp-your-app-token-here
```

安裝套件：
```bash
pip install python-dotenv
```

程式碼修改：
```python
import os
from dotenv import load_dotenv

load_dotenv()

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
```

## 🚨 常見問題排除

### 1. 程式執行但收不到訊息

- ✅ 確認 Bot 已被邀請到頻道
- ✅ 檢查 OAuth Scopes 權限
- ✅ 確認 Event Subscriptions 設定正確
- ✅ 檢查 Socket Mode 已啟用

### 2. 連接失敗

- ✅ 確認 Tokens 正確
- ✅ 檢查網路連接
- ✅ 確認 App 已安裝到工作區

### 3. 檢查 Bot 是否在頻道中

在頻道輸入：
```
/who
```
應該會看到 Bot 在成員列表中。

## 📝 注意事項

- Socket Mode 適合開發和測試
- 生產環境建議使用 HTTP 模式
- 妥善保管 Tokens，不要提交到版本控制
- Bot 需要適當的權限才能監控訊息
- 避免在程式中處理 Bot 自己發送的訊息
