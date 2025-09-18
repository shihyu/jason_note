# Linux MCP 服務器完整設置指南

## 專案結構
```
~/mcp-servers/
└── my-first-server/
    ├── server.py           # MCP 服務器主程式
    ├── requirements.txt    # Python 依賴
    └── venv/              # Python 虛擬環境
```

## 步驟 1：創建專案資料夾

```bash
# 創建 MCP 服務器目錄
mkdir -p ~/mcp-servers/my-first-server
cd ~/mcp-servers/my-first-server
```

## 步驟 2：創建 server.py

```bash
nano ~/mcp-servers/my-first-server/server.py
```

內容：
```python
#!/usr/bin/env python3
"""Linux MCP 服務器"""

from mcp.server import Server
import mcp.server.stdio
import mcp.types as types
from datetime import datetime
import os
import subprocess

# 創建服務器實例
server = Server("linux-tools")

# 定義可用的工具
@server.list_tools()
async def list_tools():
    """列出所有可用的工具"""
    return [
        types.Tool(
            name="get_system_info",
            description="獲取 Linux 系統資訊",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="list_directory",
            description="列出目錄內容",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "目錄路徑",
                        "default": "."
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="execute_command",
            description="執行簡單的 Linux 命令",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "要執行的命令（安全命令）"
                    }
                },
                "required": ["command"]
            }
        )
    ]

# 處理工具調用
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """執行具體的工具功能"""
    
    if name == "get_system_info":
        # 獲取系統資訊
        info = []
        try:
            # 系統版本
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines[:3]:
                    info.append(line.strip())
            
            # 核心版本
            kernel = subprocess.check_output(['uname', '-r'], text=True).strip()
            info.append(f"Kernel: {kernel}")
            
            # 當前時間
            info.append(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
        except Exception as e:
            info.append(f"Error: {str(e)}")
        
        return [types.TextContent(
            type="text",
            text="\n".join(info)
        )]
    
    elif name == "list_directory":
        path = arguments.get("path", ".")
        path = os.path.expanduser(path)  # 處理 ~ 符號
        
        try:
            items = os.listdir(path)
            result = f"目錄 {path} 的內容：\n"
            for item in sorted(items):
                full_path = os.path.join(path, item)
                if os.path.isdir(full_path):
                    result += f"📁 {item}/\n"
                else:
                    result += f"📄 {item}\n"
        except Exception as e:
            result = f"錯誤：{str(e)}"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    
    elif name == "execute_command":
        command = arguments.get("command")
        
        # 安全命令白名單
        safe_commands = ["date", "pwd", "whoami", "hostname", "uptime", "df", "free"]
        cmd_parts = command.split()
        
        if cmd_parts[0] not in safe_commands:
            return [types.TextContent(
                type="text",
                text=f"命令 '{cmd_parts[0]}' 不在安全命令清單中"
            )]
        
        try:
            result = subprocess.check_output(command, shell=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            result = "命令執行超時"
        except Exception as e:
            result = f"執行錯誤：{str(e)}"
        
        return [types.TextContent(
            type="text",
            text=result
        )]
    
    else:
        raise ValueError(f"未知的工具: {name}")

# 主程式
async def main():
    """啟動 MCP 服務器"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.get_capabilities()
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## 步驟 3：設置執行權限

```bash
chmod +x ~/mcp-servers/my-first-server/server.py
```

## 步驟 4：創建 requirements.txt

```bash
echo "mcp>=0.1.0" > ~/mcp-servers/my-first-server/requirements.txt
```

## 步驟 5：設置 Python 虛擬環境

```bash
# 進入專案目錄
cd ~/mcp-servers/my-first-server

# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate

# 升級 pip
pip install --upgrade pip

# 安裝 MCP
pip install mcp
```

## 步驟 6：配置 Claude Desktop

### 配置檔位置
```bash
~/.config/Claude/claude_desktop_config.json
```

完整路徑（假設用戶名為 username）：
```bash
/home/username/.config/Claude/claude_desktop_config.json
```

### 創建配置目錄（如果不存在）
```bash
mkdir -p ~/.config/Claude
```

### 編輯配置檔
```bash
nano ~/.config/Claude/claude_desktop_config.json
```

### 配置檔內容（使用虛擬環境）

```json
{
  "mcpServers": {
    "linux-tools": {
      "command": "/home/username/mcp-servers/my-first-server/venv/bin/python",
      "args": ["/home/username/mcp-servers/my-first-server/server.py"],
      "env": {}
    }
  }
}
```

### 動態獲取用戶路徑的配置

如果想要更通用的配置，可以使用環境變數：

```json
{
  "mcpServers": {
    "linux-tools": {
      "command": "bash",
      "args": ["-c", "source ~/mcp-servers/my-first-server/venv/bin/activate && python ~/mcp-servers/my-first-server/server.py"],
      "env": {}
    }
  }
}
```

## 步驟 7：驗證設置

```bash
# 檢查 Python 路徑
which python3

# 檢查虛擬環境 Python
ls -la ~/mcp-servers/my-first-server/venv/bin/python

# 測試服務器（手動）
cd ~/mcp-servers/my-first-server
source venv/bin/activate
python server.py
# Ctrl+C 結束測試
```

## 步驟 8：重啟 Claude Desktop

```bash
# 如果 Claude 正在運行，先關閉
pkill -f claude

# 重新啟動 Claude Desktop
# (根據你的安裝方式啟動 Claude)
```

## 完整路徑速查表

假設用戶名是 `john`：

```bash
# 專案根目錄
/home/john/mcp-servers/my-first-server/

# 服務器腳本
/home/john/mcp-servers/my-first-server/server.py

# Python 虛擬環境執行檔
/home/john/mcp-servers/my-first-server/venv/bin/python

# Claude 配置檔
/home/john/.config/Claude/claude_desktop_config.json
```

## 多個服務器配置範例

```json
{
  "mcpServers": {
    "linux-tools": {
      "command": "/home/john/mcp-servers/my-first-server/venv/bin/python",
      "args": ["/home/john/mcp-servers/my-first-server/server.py"]
    },
    "web-scraper": {
      "command": "/home/john/mcp-servers/web-scraper/venv/bin/python",
      "args": ["/home/john/mcp-servers/web-scraper/server.py"]
    },
    "database-tool": {
      "command": "/usr/bin/node",
      "args": ["/home/john/mcp-servers/database/index.js"]
    }
  }
}
```

## 除錯技巧

### 1. 查看 Claude 日誌
```bash
# Claude 日誌位置
tail -f ~/.config/Claude/logs/*.log
```

### 2. 測試 MCP 服務器
```bash
# 直接執行測試
cd ~/mcp-servers/my-first-server
source venv/bin/activate
python -c "import mcp; print('MCP 安裝成功')"
```

### 3. 檢查程序是否運行
```bash
# 查看 MCP 相關程序
ps aux | grep -E "mcp|claude"
```

### 4. 權限檢查
```bash
# 確保所有檔案有正確權限
ls -la ~/mcp-servers/my-first-server/
ls -la ~/.config/Claude/
```

## 常見問題解決

### 問題 1：找不到 MCP 模組
```bash
# 確保在虛擬環境中安裝
cd ~/mcp-servers/my-first-server
source venv/bin/activate
pip install mcp
```

### 問題 2：配置檔不生效
```bash
# 檢查 JSON 格式
python3 -m json.tool ~/.config/Claude/claude_desktop_config.json
```

### 問題 3：Python 版本問題
```bash
# 檢查 Python 版本（需要 3.8+）
python3 --version

# 如果版本太舊，安裝新版
sudo apt update
sudo apt install python3.10 python3.10-venv
```

## 快速安裝腳本

創建一個快速安裝腳本 `setup-mcp.sh`：

```bash
#!/bin/bash

# 設置變數
MCP_DIR="$HOME/mcp-servers/my-first-server"
CONFIG_DIR="$HOME/.config/Claude"

# 創建目錄
mkdir -p "$MCP_DIR"
mkdir -p "$CONFIG_DIR"

# 創建虛擬環境並安裝
cd "$MCP_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mcp

# 創建配置檔
cat > "$CONFIG_DIR/claude_desktop_config.json" << EOF
{
  "mcpServers": {
    "linux-tools": {
      "command": "$MCP_DIR/venv/bin/python",
      "args": ["$MCP_DIR/server.py"],
      "env": {}
    }
  }
}
EOF

echo "✅ MCP 服務器設置完成！"
echo "📁 服務器位置：$MCP_DIR"
echo "📄 配置檔位置：$CONFIG_DIR/claude_desktop_config.json"
echo "🔄 請重啟 Claude Desktop"
```

執行安裝腳本：
```bash
chmod +x setup-mcp.sh
./setup-mcp.sh
```

這樣就完成了 Linux 上的 MCP 服務器設置！