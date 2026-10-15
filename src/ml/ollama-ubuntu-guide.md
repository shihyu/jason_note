# Ollama 在 Ubuntu 24.04 完整使用指南

## 目錄
- [快速開始](#快速開始)
- [安裝](#安裝)
- [基本操作](#基本操作)
- [簡單範例](#簡單範例)
- [常用模型推薦](#常用模型推薦)
- [實用技巧](#實用技巧)
- [Web UI 設定](#web-ui-設定)
- [故障排除](#故障排除)
- [進階設定](#進階設定)
- [API 參考](#api-參考)

## 快速開始

```bash
# 一鍵安裝
curl -fsSL https://ollama.com/install.sh | sh

# 執行第一個模型
ollama run tinyllama

# 輸入問題開始對話
>>> 你好，請自我介紹
```

## 安裝

### 系統需求
- Ubuntu 24.04 LTS
- 最少 4GB RAM（建議 8GB 以上）
- 10GB 可用硬碟空間
- (選用) NVIDIA GPU with CUDA 11.8+

### 安裝方法

#### 方法 1：官方腳本（推薦）
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

#### 方法 2：手動安裝
```bash
# 下載二進位檔案
wget https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64

# 賦予執行權限
chmod +x ollama-linux-amd64

# 移動到系統路徑
sudo mv ollama-linux-amd64 /usr/local/bin/ollama

# 建立服務檔案
sudo useradd -r -s /bin/false -m -d /usr/share/ollama ollama
```

### 驗證安裝
```bash
# 檢查版本
ollama --version

# 檢查服務狀態
sudo systemctl status ollama
```

## 基本操作

### 服務管理
```bash
# 檢查服務狀態
sudo systemctl status ollama

# 啟動服務
sudo systemctl start ollama

# 停止服務
sudo systemctl stop ollama

# 重啟服務
sudo systemctl restart ollama

# 設定開機自動啟動
sudo systemctl enable ollama

# 檢視服務日誌
journalctl -u ollama -f
```

### 模型管理
```bash
# 下載並執行模型
ollama run llama3.2:3b

# 只下載模型不執行
ollama pull llama3.2:3b

# 列出已安裝的模型
ollama list

# 顯示模型資訊
ollama show llama3.2:3b

# 刪除模型
ollama rm llama3.2:3b

# 複製模型（用於自訂）
ollama cp llama3.2:3b my-custom-model
```

## 簡單範例

### 範例 1：命令列對話
```bash
# 互動式對話
ollama run llama3.2:3b

>>> 解釋什麼是容器技術？
>>> 用 Python 寫一個快速排序
>>> /bye
```

### 範例 2：一次性問答
```bash
# 單次問答（不進入互動模式）
echo "什麼是 RESTful API？" | ollama run llama3.2:3b

# 或使用參數方式
ollama run llama3.2:3b "列出 5 個 Git 常用指令"
```

### 範例 3：使用 cURL 呼叫 API
```bash
# 基本 API 呼叫
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "解釋什麼是微服務架構",
  "stream": false
}'

# 串流回應
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2:3b",
  "prompt": "寫一個 Python Flask 範例",
  "stream": true
}'
```

### 範例 4：Python 整合腳本
```python
#!/usr/bin/env python3
"""
Ollama Python 整合範例
安裝: pip install requests
"""

import requests
import json

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, prompt, model="llama3.2:3b", stream=False):
        """生成回應"""
        url = f"{self.base_url}/api/generate"
        data = {
            "model": model,
            "prompt": prompt,
            "stream": stream
        }
        
        if not stream:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                return response.json()['response']
        else:
            response = requests.post(url, json=data, stream=True)
            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line)
                    yield chunk['response']
    
    def chat(self, messages, model="llama3.2:3b"):
        """聊天介面"""
        url = f"{self.base_url}/api/chat"
        data = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        response = requests.post(url, json=data)
        if response.status_code == 200:
            return response.json()['message']['content']
    
    def list_models(self):
        """列出可用模型"""
        url = f"{self.base_url}/api/tags"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()['models']

# 使用範例
if __name__ == "__main__":
    client = OllamaClient()
    
    # 簡單生成
    print("=== 簡單生成 ===")
    result = client.generate("用 Python 寫一個費氏數列")
    print(result)
    
    # 串流生成
    print("\n=== 串流生成 ===")
    for chunk in client.generate("解釋 Docker 的優點", stream=True):
        print(chunk, end='', flush=True)
    print()
    
    # 聊天模式
    print("\n=== 聊天模式 ===")
    messages = [
        {"role": "user", "content": "你是誰？"},
        {"role": "assistant", "content": "我是一個 AI 助手。"},
        {"role": "user", "content": "你能做什麼？"}
    ]
    response = client.chat(messages)
    print(response)
    
    # 列出模型
    print("\n=== 可用模型 ===")
    models = client.list_models()
    for model in models:
        print(f"- {model['name']} ({model['size']/1e9:.1f}GB)")
```

### 範例 5：Bash 聊天機器人腳本
```bash
#!/bin/bash
# 儲存為 ollama-chat.sh
# 使用: chmod +x ollama-chat.sh && ./ollama-chat.sh

# 設定
MODEL="${1:-llama3.2:3b}"
HISTORY_FILE="$HOME/.ollama_chat_history"

# 顏色設定
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 函數：顯示標題
show_header() {
    clear
    echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║       Ollama 聊天機器人 v1.0           ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
    echo -e "${YELLOW}模型: $MODEL${NC}"
    echo -e "${GREEN}指令: /help, /clear, /model, /save, /quit${NC}"
    echo ""
}

# 函數：處理命令
handle_command() {
    case $1 in
        /help)
            echo -e "${GREEN}可用指令：${NC}"
            echo "  /help   - 顯示幫助"
            echo "  /clear  - 清除螢幕"
            echo "  /model  - 切換模型"
            echo "  /save   - 儲存對話"
            echo "  /quit   - 離開程式"
            ;;
        /clear)
            show_header
            ;;
        /model)
            echo -e "${YELLOW}可用模型：${NC}"
            ollama list
            read -p "輸入模型名稱: " new_model
            if [ ! -z "$new_model" ]; then
                MODEL=$new_model
                echo -e "${GREEN}已切換到 $MODEL${NC}"
            fi
            ;;
        /save)
            echo "$conversation" > "$HISTORY_FILE"
            echo -e "${GREEN}對話已儲存到 $HISTORY_FILE${NC}"
            ;;
        /quit|/exit|/bye)
            echo -e "${BLUE}再見！${NC}"
            exit 0
            ;;
        *)
            return 1
            ;;
    esac
    return 0
}

# 主程式
show_header
conversation=""

while true; do
    # 讀取使用者輸入
    echo -ne "${GREEN}👤 你: ${NC}"
    read -r input
    
    # 檢查是否為命令
    if [[ $input == /* ]]; then
        handle_command "$input"
        continue
    fi
    
    # 新增到對話記錄
    conversation="$conversation\n👤: $input"
    
    # 取得 AI 回應
    echo -ne "${BLUE}🤖 AI: ${NC}"
    response=$(echo "$input" | ollama run $MODEL 2>/dev/null)
    echo "$response"
    
    # 新增到對話記錄
    conversation="$conversation\n🤖: $response"
    echo ""
done
```

### 範例 6：Node.js 整合
```javascript
// ollama-client.js
// 安裝: npm install axios

const axios = require('axios');

class OllamaClient {
    constructor(baseURL = 'http://localhost:11434') {
        this.baseURL = baseURL;
    }

    async generate(prompt, model = 'llama3.2:3b') {
        try {
            const response = await axios.post(`${this.baseURL}/api/generate`, {
                model: model,
                prompt: prompt,
                stream: false
            });
            return response.data.response;
        } catch (error) {
            console.error('Error:', error.message);
            return null;
        }
    }

    async *generateStream(prompt, model = 'llama3.2:3b') {
        try {
            const response = await axios.post(`${this.baseURL}/api/generate`, {
                model: model,
                prompt: prompt,
                stream: true
            }, {
                responseType: 'stream'
            });

            for await (const chunk of response.data) {
                const lines = chunk.toString().split('\n').filter(Boolean);
                for (const line of lines) {
                    const data = JSON.parse(line);
                    yield data.response;
                }
            }
        } catch (error) {
            console.error('Error:', error.message);
        }
    }
}

// 使用範例
async function main() {
    const client = new OllamaClient();
    
    // 一般生成
    console.log('=== 一般生成 ===');
    const response = await client.generate('什麼是 Node.js？');
    console.log(response);
    
    // 串流生成
    console.log('\n=== 串流生成 ===');
    for await (const chunk of client.generateStream('列出 JavaScript 的特點')) {
        process.stdout.write(chunk);
    }
    console.log();
}

main();
```

## 常用模型推薦

### 🎯 輕量級模型 (RAM < 4GB)

| 模型名稱 | 參數大小 | 記憶體需求 | 特點 | 安裝指令 |
|---------|---------|-----------|------|---------|
| TinyLlama | 1.1B | ~2GB | 超快速回應 | `ollama run tinyllama` |
| Phi-3 Mini | 3.8B | ~3GB | 微軟出品，效能佳 | `ollama run phi3:mini` |
| Qwen 0.5B | 0.5B | ~1GB | 中文支援良好 | `ollama run qwen:0.5b` |
| Gemma 2B | 2B | ~2.5GB | Google 模型 | `ollama run gemma:2b` |

### 💪 中型模型 (RAM 8-16GB)

| 模型名稱 | 參數大小 | 記憶體需求 | 特點 | 安裝指令 |
|---------|---------|-----------|------|---------|
| Llama 3.2 | 3B | ~5GB | Meta 最新，平衡選擇 | `ollama run llama3.2:3b` |
| Mistral | 7B | ~8GB | 法國團隊，品質優秀 | `ollama run mistral` |
| Gemma 2 | 9B | ~10GB | Google 大型模型 | `ollama run gemma2:9b` |
| Vicuna | 7B | ~8GB | 對話能力強 | `ollama run vicuna` |

### 👨‍💻 程式碼專用模型

| 模型名稱 | 參數大小 | 記憶體需求 | 特點 | 安裝指令 |
|---------|---------|-----------|------|---------|
| CodeLlama | 7B | ~8GB | Meta 程式碼模型 | `ollama run codellama` |
| DeepSeek Coder | 1.3B | ~2GB | 輕量級程式碼 | `ollama run deepseek-coder:1.3b` |
| Starcoder2 | 3B | ~4GB | 多語言程式碼 | `ollama run starcoder2:3b` |
| CodeGemma | 7B | ~8GB | Google 程式碼模型 | `ollama run codegemma` |

### 🌏 中文優化模型

| 模型名稱 | 參數大小 | 記憶體需求 | 特點 | 安裝指令 |
|---------|---------|-----------|------|---------|
| Qwen | 1.8B | ~3GB | 阿里通義千問 | `ollama run qwen` |
| Yi | 6B | ~7GB | 零一萬物 | `ollama run yi` |
| ChatGLM3 | 6B | ~7GB | 清華智譜 | `ollama run chatglm3` |

## 實用技巧

### 效能優化

#### 1. GPU 加速設定
```bash
# 檢查 GPU 支援
nvidia-smi

# 設定使用特定 GPU
export CUDA_VISIBLE_DEVICES=0

# 使用多個 GPU
export CUDA_VISIBLE_DEVICES=0,1
```

#### 2. 記憶體優化
```bash
# 使用量子化版本（降低記憶體使用）
ollama run llama3.2:3b-q4_0  # 4-bit 量子化
ollama run llama3.2:3b-q5_0  # 5-bit 量子化
ollama run llama3.2:3b-q8_0  # 8-bit 量子化

# 限制上下文長度
ollama run llama3.2:3b --num-ctx 2048
```

#### 3. CPU 優化
```bash
# 設定並行數
export OLLAMA_NUM_PARALLEL=2

# 設定執行緒數
export OLLAMA_NUM_THREAD=4
```

### 批次處理

#### 批次問答腳本
```bash
#!/bin/bash
# batch-query.sh

# 問題列表檔案
QUESTIONS_FILE="questions.txt"
OUTPUT_FILE="answers.md"
MODEL="llama3.2:3b"

# 清空輸出檔案
> "$OUTPUT_FILE"

# 逐行讀取問題並處理
while IFS= read -r question; do
    echo "處理: $question"
    echo "## $question" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    answer=$(echo "$question" | ollama run $MODEL)
    echo "$answer" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    echo "---" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done < "$QUESTIONS_FILE"

echo "完成！結果已儲存到 $OUTPUT_FILE"
```

### 整合到 VS Code

#### 1. 安裝 Continue 擴充套件
```bash
# 在 VS Code 中
# 1. 開啟延伸模組 (Ctrl+Shift+X)
# 2. 搜尋 "Continue"
# 3. 安裝
```

#### 2. 設定 Continue
```json
{
  "models": [
    {
      "title": "Ollama",
      "provider": "ollama",
      "model": "codellama:7b",
      "apiBase": "http://localhost:11434"
    }
  ]
}
```

### 建立別名快捷

```bash
# 加入到 ~/.bashrc 或 ~/.zshrc

# 快速啟動對話
alias chat='ollama run llama3.2:3b'

# 程式碼助手
alias code-ai='ollama run codellama:7b'

# 快速翻譯
translate() {
    echo "Translate to Chinese: $1" | ollama run llama3.2:3b
}

# 程式碼解釋
explain() {
    echo "Explain this code: $(cat $1)" | ollama run codellama:7b
}

# 快速摘要
summarize() {
    echo "Summarize: $(cat $1)" | ollama run llama3.2:3b
}
```

## Web UI 設定

### 選項 1：Open WebUI（推薦）

#### Docker 安裝
```bash
# 拉取並執行
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -e OLLAMA_BASE_URL=http://host.docker.internal:11434 \
  --name open-webui \
  --restart always \
  ghcr.io/open-webui/open-webui:main

# 檢查狀態
docker ps | grep open-webui

# 檢視日誌
docker logs -f open-webui
```

#### Docker Compose 安裝
```yaml
# docker-compose.yml
version: '3.8'

services:
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open-webui:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://host.docker.internal:11434
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: always

volumes:
  open-webui:
```

```bash
# 啟動
docker-compose up -d

# 訪問 http://localhost:3000
```

### 選項 2：Ollama UI

```bash
# 克隆專案
git clone https://github.com/ollama-ui/ollama-ui
cd ollama-ui

# 安裝依賴
npm install

# 建立環境設定
cp .env.example .env
echo "OLLAMA_HOST=http://localhost:11434" >> .env

# 啟動開發伺服器
npm run dev

# 建置生產版本
npm run build
npm start
```

### 選項 3：簡單 HTML 介面

```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ollama Chat</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .container {
            width: 90%;
            max-width: 800px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #4a5568;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-box {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f7fafc;
        }
        .message {
            margin: 10px 0;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user-message {
            background: #4299e1;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .ai-message {
            background: #e2e8f0;
            color: #2d3748;
        }
        .input-area {
            display: flex;
            padding: 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
        }
        #messageInput {
            flex: 1;
            padding: 10px 15px;
            border: 2px solid #e2e8f0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        #messageInput:focus {
            border-color: #4299e1;
        }
        #sendButton {
            margin-left: 10px;
            padding: 10px 30px;
            background: #4299e1;
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: background 0.3s;
        }
        #sendButton:hover {
            background: #3182ce;
        }
        #sendButton:disabled {
            background: #a0aec0;
            cursor: not-allowed;
        }
        .model-selector {
            padding: 10px 20px;
            background: #edf2f7;
        }
        select {
            padding: 5px 10px;
            border-radius: 5px;
            border: 1px solid #cbd5e0;
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #4299e1;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Ollama Chat</h1>
        </div>
        
        <div class="model-selector">
            <label for="modelSelect">模型：</label>
            <select id="modelSelect">
                <option value="llama3.2:3b">Llama 3.2 (3B)</option>
                <option value="tinyllama">TinyLlama</option>
                <option value="codellama:7b">CodeLlama</option>
                <option value="mistral">Mistral</option>
            </select>
        </div>
        
        <div class="chat-box" id="chatBox"></div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="輸入訊息..." />
            <button id="sendButton">發送</button>
        </div>
    </div>

    <script>
        const chatBox = document.getElementById('chatBox');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const modelSelect = document.getElementById('modelSelect');
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            // 顯示使用者訊息
            addMessage(message, 'user');
            messageInput.value = '';
            
            // 禁用輸入
            sendButton.disabled = true;
            messageInput.disabled = true;
            
            // 顯示載入中
            const loadingId = 'loading-' + Date.now();
            addMessage('<div class="loading"></div>', 'ai', loadingId);
            
            try {
                const response = await fetch('http://localhost:11434/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        model: modelSelect.value,
                        prompt: message,
                        stream: false
                    })
                });
                
                const data = await response.json();
                
                // 移除載入動畫
                document.getElementById(loadingId).remove();
                
                // 顯示 AI 回應
                addMessage(data.response, 'ai');
                
            } catch (error) {
                document.getElementById(loadingId).remove();
                addMessage('錯誤：無法連接到 Ollama 服務', 'ai');
            }
            
            // 重新啟用輸入
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
        }
        
        function addMessage(content, sender, id = null) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            if (id) messageDiv.id = id;
            messageDiv.innerHTML = content;
            chatBox.appendChild(messageDiv);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        // 初始訊息
        addMessage('你好！我是 Ollama AI 助手，有什麼可以幫助你的嗎？', 'ai');
    </script>
</body>
</html>
```

## 故障排除

### 常見問題與解決方案

#### 1. 服務無法啟動
```bash
# 檢查錯誤日誌
journalctl -u ollama -n 50

# 常見原因：埠號被佔用
sudo lsof -i :11434

# 解決方案：更改埠號
OLLAMA_HOST=0.0.0.0:8080 ollama serve
```

#### 2. GPU 不被識別
```bash
# 檢查 NVIDIA 驅動
nvidia-smi

# 安裝 CUDA 工具包
sudo apt update
sudo apt install nvidia-cuda-toolkit

# 檢查 CUDA 版本
nvcc --version

# 重啟 Ollama
sudo systemctl restart ollama
```

#### 3. 記憶體不足錯誤
```bash
# 解決方案 1：使用更小的模型
ollama run tinyllama

# 解決方案 2：使用量子化版本
ollama run llama3.2:3b-q4_0

# 解決方案 3：限制上下文長度
ollama run llama3.2:3b --num-ctx 1024

# 解決方案 4：清理未使用的模型
ollama list
ollama rm unused-model
```

#### 4. 模型下載失敗
```bash
# 檢查網路連線
ping ollama.com

# 使用代理
export HTTP_PROXY=http://proxy:port
export HTTPS_PROXY=http://proxy:port

# 重試下載
ollama pull llama3.2:3b

# 手動下載模型檔案
wget https://ollama.com/library/llama3.2/blobs/sha256:xxxxx
```

#### 5. API 連線被拒絕
```bash
# 檢查服務狀態
sudo systemctl status ollama

# 允許外部連線
OLLAMA_HOST=0.0.0.0:11434 ollama serve

# 防火牆設定
sudo ufw allow 11434/tcp
```

### 效能調優

#### 系統層級優化
```bash
# 增加檔案描述符限制
ulimit -n 65536

# 調整 swap 使用
sudo sysctl vm.swappiness=10

# 設定 CPU 調控器
sudo cpupower frequency-set -g performance
```

#### Ollama 特定優化
```bash
# 環境變數設定
export OLLAMA_NUM_PARALLEL=4     # 並行請求數
export OLLAMA_NUM_GPU=1          # GPU 數量
export OLLAMA_MAX_LOADED_MODELS=2 # 最大載入模型數
export OLLAMA_KEEP_ALIVE=5m      # 模型保持載入時間
```

## 進階設定

### 自訂模型 (Modelfile)

#### 基本 Modelfile
```dockerfile
# Modelfile
FROM llama3.2:3b

# 設定參數
PARAMETER temperature 0.8
PARAMETER top_k 40
PARAMETER top_p 0.9
PARAMETER repeat_penalty 1.1
PARAMETER num_ctx 4096

# 設定系統提示
SYSTEM """
你是一個專業的技術顧問，專門協助解決程式設計和系統架構問題。
請用繁體中文回答，並提供詳細的解釋和範例。
"""

# 設定訊息模板
TEMPLATE """
{{ if .System }}System: {{ .System }}{{ end }}
{{ if .Prompt }}User: {{ .Prompt }}{{ end }}
Assistant: {{ .Response }}
"""
```

#### 建立和使用自訂模型
```bash
# 建立模型
ollama create my-assistant -f ./Modelfile

# 使用自訂模型
ollama run my-assistant

# 分享模型
ollama push username/my-assistant
```

#### 進階 Modelfile 範例
```dockerfile
# 程式碼助手模型
FROM codellama:7b

PARAMETER temperature 0.3  # 降低隨機性
PARAMETER num_predict 2000 # 最大生成長度

SYSTEM """
You are an expert programmer. Follow these rules:
1. Always provide working code examples
2. Include comments explaining complex parts
3. Consider edge cases and error handling
4. Suggest best practices and optimizations
5. Use the most appropriate programming patterns
"""

# 加入範例對話
MESSAGE user "Write a function to reverse a string"
MESSAGE assistant """Here's a function to reverse a string in Python:

```python
def reverse_string(s):
    \"\"\"
    Reverse a string using Python's slicing feature.
    
    Args:
        s (str): The string to reverse
    
    Returns:
        str: The reversed string
    \"\"\"
    return s[::-1]

# Example usage
print(reverse_string("hello"))  # Output: "olleh"
```
"""
```

### 多模型管理

#### 模型切換腳本
```python
#!/usr/bin/env python3
"""
Ollama 模型管理器
"""

import subprocess
import json
import sys

class ModelManager:
    def __init__(self):
        self.models = self.get_installed_models()
    
    def get_installed_models(self):
        """取得已安裝的模型列表"""
        try:
            result = subprocess.run(
                ['ollama', 'list'], 
                capture_output=True, 
                text=True
            )
            # 解析輸出
            lines = result.stdout.strip().split('\n')[1:]  # 跳過標題
            models = []
            for line in lines:
                if line:
                    parts = line.split()
                    models.append({
                        'name': parts[0],
                        'size': parts[1] if len(parts) > 1 else 'N/A'
                    })
            return models
        except Exception as e:
            print(f"錯誤: {e}")
            return []
    
    def list_models(self):
        """列出所有模型"""
        print("\n已安裝的模型:")
        print("-" * 40)
        for i, model in enumerate(self.models, 1):
            print(f"{i}. {model['name']} ({model['size']})")
    
    def run_model(self, model_name):
        """執行指定模型"""
        print(f"\n啟動模型: {model_name}")
        subprocess.run(['ollama', 'run', model_name])
    
    def pull_model(self, model_name):
        """下載新模型"""
        print(f"\n下載模型: {model_name}")
        subprocess.run(['ollama', 'pull', model_name])
    
    def delete_model(self, model_name):
        """刪除模型"""
        confirm = input(f"確定要刪除 {model_name}? (y/n): ")
        if confirm.lower() == 'y':
            subprocess.run(['ollama', 'rm', model_name])
            print(f"已刪除 {model_name}")

def main():
    manager = ModelManager()
    
    while True:
        print("\n" + "="*40)
        print("Ollama 模型管理器")
        print("="*40)
        print("1. 列出模型")
        print("2. 執行模型")
        print("3. 下載新模型")
        print("4. 刪除模型")
        print("5. 離開")
        
        choice = input("\n選擇操作 (1-5): ")
        
        if choice == '1':
            manager.list_models()
        
        elif choice == '2':
            manager.list_models()
            model_idx = input("\n選擇模型編號: ")
            try:
                idx = int(model_idx) - 1
                if 0 <= idx < len(manager.models):
                    manager.run_model(manager.models[idx]['name'])
            except (ValueError, IndexError):
                print("無效的選擇")
        
        elif choice == '3':
            model_name = input("輸入模型名稱 (如 llama3.2:3b): ")
            manager.pull_model(model_name)
            manager.models = manager.get_installed_models()
        
        elif choice == '4':
            manager.list_models()
            model_idx = input("\n選擇要刪除的模型編號: ")
            try:
                idx = int(model_idx) - 1
                if 0 <= idx < len(manager.models):
                    manager.delete_model(manager.models[idx]['name'])
                    manager.models = manager.get_installed_models()
            except (ValueError, IndexError):
                print("無效的選擇")
        
        elif choice == '5':
            print("再見！")
            break
        
        else:
            print("無效的選擇")

if __name__ == "__main__":
    main()
```

## API 參考

### 核心 API 端點

#### 1. 生成文字 `/api/generate`
```bash
# 請求
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "prompt": "Why is the sky blue?",
    "stream": false,
    "options": {
      "temperature": 0.7,
      "top_p": 0.9,
      "top_k": 40
    }
  }'

# 回應
{
  "model": "llama3.2:3b",
  "created_at": "2024-01-01T00:00:00.000Z",
  "response": "The sky appears blue because...",
  "done": true,
  "context": [1, 2, 3],
  "total_duration": 5000000000,
  "load_duration": 1000000000,
  "prompt_eval_duration": 1000000000,
  "eval_duration": 3000000000,
  "eval_count": 100
}
```

#### 2. 聊天介面 `/api/chat`
```bash
# 請求
curl -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "system", "content": "You are a helpful assistant."},
      {"role": "user", "content": "Hello!"},
      {"role": "assistant", "content": "Hi! How can I help you?"},
      {"role": "user", "content": "Tell me a joke"}
    ],
    "stream": false
  }'
```

#### 3. 模型管理

##### 列出模型 `/api/tags`
```bash
curl http://localhost:11434/api/tags

# 回應
{
  "models": [
    {
      "name": "llama3.2:3b",
      "modified_at": "2024-01-01T00:00:00.000Z",
      "size": 3825819519,
      "digest": "sha256:xxx"
    }
  ]
}
```

##### 顯示模型資訊 `/api/show`
```bash
curl -X POST http://localhost:11434/api/show \
  -d '{"name": "llama3.2:3b"}'
```

##### 複製模型 `/api/copy`
```bash
curl -X POST http://localhost:11434/api/copy \
  -d '{
    "source": "llama3.2:3b",
    "destination": "my-model"
  }'
```

##### 刪除模型 `/api/delete`
```bash
curl -X DELETE http://localhost:11434/api/delete \
  -d '{"name": "llama3.2:3b"}'
```

##### 拉取模型 `/api/pull`
```bash
curl -X POST http://localhost:11434/api/pull \
  -d '{"name": "llama3.2:3b"}'
```

##### 推送模型 `/api/push`
```bash
curl -X POST http://localhost:11434/api/push \
  -d '{"name": "username/my-model"}'
```

#### 4. 嵌入向量 `/api/embeddings`
```bash
curl -X POST http://localhost:11434/api/embeddings \
  -d '{
    "model": "llama3.2:3b",
    "prompt": "Hello world"
  }'

# 回應
{
  "embedding": [0.1, 0.2, 0.3, ...]
}
```

### 參數說明

#### 生成參數 (options)
| 參數 | 類型 | 預設值 | 說明 |
|-----|------|--------|------|
| temperature | float | 0.8 | 控制隨機性 (0-2) |
| top_k | int | 40 | 限制詞彙選擇數量 |
| top_p | float | 0.9 | 累積機率閾值 |
| repeat_penalty | float | 1.1 | 重複懲罰 |
| seed | int | 0 | 隨機種子 |
| num_predict | int | 128 | 最大生成長度 |
| num_ctx | int | 2048 | 上下文視窗大小 |
| stop | []string | [] | 停止序列 |

### SDK 整合

#### Python (ollama-python)
```bash
pip install ollama
```

```python
import ollama

# 生成
response = ollama.generate(model='llama3.2:3b', prompt='Why is the sky blue?')
print(response['response'])

# 聊天
messages = [
    {'role': 'user', 'content': 'Why is the sky blue?'}
]
response = ollama.chat(model='llama3.2:3b', messages=messages)
print(response['message']['content'])

# 串流
for chunk in ollama.generate(model='llama3.2:3b', prompt='Tell me a story', stream=True):
    print(chunk['response'], end='', flush=True)
```

#### JavaScript/TypeScript
```bash
npm install ollama
```

```javascript
import ollama from 'ollama'

// 生成
const response = await ollama.generate({
  model: 'llama3.2:3b',
  prompt: 'Why is the sky blue?'
})
console.log(response.response)

// 聊天
const message = await ollama.chat({
  model: 'llama3.2:3b',
  messages: [{ role: 'user', content: 'Why is the sky blue?' }],
})
console.log(message.message.content)

// 串流
const stream = await ollama.generate({
  model: 'llama3.2:3b',
  prompt: 'Tell me a story',
  stream: true,
})
for await (const chunk of stream) {
  process.stdout.write(chunk.response)
}
```

## 最佳實踐

### 1. 安全性設定
```bash
# 限制本地存取
OLLAMA_HOST=127.0.0.1:11434 ollama serve

# 使用 nginx 反向代理
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location /api/ {
        proxy_pass http://localhost:11434/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 監控和日誌
```bash
# 即時監控
watch -n 1 'nvidia-smi; echo ""; ollama list'

# 日誌分析
journalctl -u ollama --since "1 hour ago" | grep ERROR

# 效能監控腳本
#!/bin/bash
while true; do
    echo "$(date): $(ollama list | wc -l) models loaded"
    nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader
    sleep 5
done
```

### 3. 備份和還原
```bash
# 備份模型
tar -czf ollama-models-backup.tar.gz ~/.ollama/models

# 還原模型
tar -xzf ollama-models-backup.tar.gz -C ~/

# 備份設定
cp -r ~/.ollama ollama-config-backup
```

## 資源連結

### 官方資源
- [Ollama 官方網站](https://ollama.com)
- [Ollama GitHub](https://github.com/ollama/ollama)
- [模型庫](https://ollama.com/library)
- [API 文件](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Modelfile 文件](https://github.com/ollama/ollama/blob/main/docs/modelfile.md)

### 社群資源
- [Ollama Discord](https://discord.gg/ollama)
- [Reddit r/LocalLLaMA](https://www.reddit.com/r/LocalLLaMA/)
- [Hugging Face Models](https://huggingface.co/models)

### 相關工具
- [Open WebUI](https://github.com/open-webui/open-webui)
- [Continue (VS Code)](https://continue.dev/)
- [LangChain](https://langchain.com/)
- [LlamaIndex](https://www.llamaindex.ai/)

### 學習資源
- [Ollama 教學影片](https://www.youtube.com/results?search_query=ollama+tutorial)
- [LLM 課程](https://www.deeplearning.ai/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 更新日誌

- **2024.01**: 初始版本
- **2024.02**: 新增 Web UI 設定
- **2024.03**: 新增進階設定和 API 參考
- **2024.04**: 新增故障排除和最佳實踐

---

💡 **小提示**: 
- 開始使用時先嘗試較小的模型（如 TinyLlama）
- 定期更新 Ollama 以獲得最新功能和效能改進
- 加入社群獲得支援和分享經驗

📝 **授權**: MIT License

🤝 **貢獻**: 歡迎提交 Issue 和 Pull Request！