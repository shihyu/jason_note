@echo off
echo 正在設定 n8n 環境變數...
REM 不顯示 Deprecation 警告訊息
set NODE_NO_WARNINGS=1
REM n8n 設定
set N8N_RUNNERS_ENABLED=true
set N8N_COMMUNITY_PACKAGES_ALLOW_TOOL_USAGE=true

echo 正在啟動 n8n...
npx n8n
