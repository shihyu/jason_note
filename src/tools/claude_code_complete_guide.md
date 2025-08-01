# Claude Code 完整自動化開發指南

## 目錄
1. [基本概念](#基本概念)
2. [安裝與設置](#安裝與設置)
3. [命令使用方式](#命令使用方式)
4. [自動化模式詳解](#自動化模式詳解)
5. [夜間自動化設置](#夜間自動化設置)
6. [Token 管理與監控](#token-管理與監控)
7. [實用腳本範例](#實用腳本範例)
8. [安全考量與最佳實踐](#安全考量與最佳實踐)
9. [故障排除](#故障排除)

---

## 基本概念

Claude Code 是 Anthropic 的命令行工具，讓開發者可以直接在終端中與 Claude 協作進行編程任務。

### 主要特性
- **完整代碼庫感知**：理解整個項目結構和模式
- **直接文件操作**：編輯文件、執行命令、管理 git 操作
- **自主執行**：可執行複雜的多步驟工作流程
- **上下文保持**：維持項目慣例的長期記憶
- **確定性自動化**：使用 hooks 保證特定動作總是發生

---

## 安裝與設置

### 安裝步驟
```bash
# 通過 npm 安裝
npm install -g @anthropic-ai/claude-code

# 驗證安裝
claude --version

# 設置 API 密鑰
export ANTHROPIC_API_KEY="your-api-key-here"

# 或者初次使用時會提示輸入
claude auth
```

### 環境變數設置
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export ANTHROPIC_API_KEY="your-api-key-here"

# 設置常用別名
alias cc="claude --dangerously-skip-permissions"
alias claude-auto="claude --dangerously-skip-permissions"
```

---

## 命令使用方式

### 基本命令格式
```bash
# 命令名稱是 claude（不是 claude-code）
claude [選項] [提示]

# 查看所有可用選項
claude --help
claude -h
```

### 常用命令選項
```bash
# 互動模式（預設）
claude

# 單次任務模式
claude -p "修復所有 lint 錯誤"

# 跳過權限確認
claude --dangerously-skip-permissions

# JSON 輸出格式
claude -p "分析代碼品質" --output-format json

# 詳細模式（調試用）
claude --verbose

# Headless 模式（CI/CD 用）
claude -p "執行測試" --output-format stream-json
```

---

## 自動化模式詳解

### 1. 預設模式（有權限確認）
```bash
claude
```
**特點：**
- 每個操作都需要確認
- 安全性最高
- 適合精確控制場景
- 會中斷工作流程

### 2. 完全自動化模式
```bash
claude --dangerously-skip-permissions
```
**特點：**
- 繞過所有權限檢查
- 不間斷執行直到完成
- 類似 "yolo 模式"
- 適合夜間自動化

### 3. Auto-Accept 模式
```bash
# 啟動後按 Shift+Tab 切換
claude
# 然後按 Shift+Tab 進入自動接受模式
```
**特點：**
- 部分自動化
- 可隨時切換
- 保持一定控制權

### 4. Print 模式（單次任務）
```bash
claude -p "具體任務描述"
```
**特點：**
- 非互動式
- 適合腳本化
- 執行完就結束

### 5. 任務排隊系統
```bash
# 啟動自動化模式後，可連續輸入多個任務
claude --dangerously-skip-permissions

# 然後輸入一系列任務（Claude 會智能排序執行）
"修復所有 lint 錯誤"
"運行完整測試套件並修復失敗測試"
"重構重複代碼"
"添加缺失的註解和文檔"
"優化性能瓶頸"
```

---

## 夜間自動化設置

### 適合夜間運行的任務類型

#### Bug 修復和建構問題
- 修復編譯錯誤
- 解決依賴衝突
- 修復測試失敗
- 處理 lint 警告
- 解決類型錯誤

#### 代碼品質改善
- 重構重複代碼
- 添加單元測試
- 更新過時文檔
- 優化性能
- 改善錯誤處理

#### 自動化維護
- 更新依賴版本
- 清理無用代碼
- 格式化代碼風格
- 生成 API 文檔
- 整理 git 歷史

### 夜間自動化啟動方式

#### 方式一：直接啟動
```bash
# 睡前執行（在專案目錄中）
cd /path/to/your/project
claude --dangerously-skip-permissions
```

然後輸入任務清單：
```
檢查並修復所有建構錯誤
運行完整測試套件，修復所有失敗的測試
處理所有 ESLint 和 TypeScript 警告
重構重複代碼並提高可讀性
添加缺失的單元測試，確保覆蓋率達到 80%
更新依賴到最新穩定版本
生成或更新 API 文檔
優化數據庫查詢和 API 響應時間
添加錯誤處理和日誌記錄
清理無用的註解和死代碼
```

#### 方式二：單行命令啟動
```bash
claude --dangerously-skip-permissions -p "執行完整的夜間維護：修復所有 bug、運行測試、重構代碼、更新文檔、優化性能"
```

---

## Token 管理與監控

### Token 使用監控工具

#### 安裝監控工具
```bash
# CC Usage - CLI 工具用於管理和分析 Claude Code 使用情況
npm install -g cc-usage

# Claude Code Usage Monitor - 實時終端監控工具
npm install -g claude-code-usage-monitor
```

#### 使用監控工具
```bash
# 查看 token 使用情況
cc-usage dashboard

# 實時監控
claude-code-usage-monitor
```

### 節省 Token 的策略

#### 1. 代碼優化
- 使用簡潔變數名稱（i, j, e, el）
- 避免過長的函數和類名
- 刪除不必要的註解

#### 2. 分階段執行
```bash
# 階段性執行而非一次性大任務
claude -p "階段1：只修復編譯錯誤"
# 完成後
claude -p "階段2：只運行並修復測試"
# 完成後  
claude -p "階段3：只重構重複代碼"
```

#### 3. 使用壓縮指令
```bash
# 當對話接近上下文限制時
/compact
```

### Token 耗盡自動重啟機制

#### 監控腳本
```bash
#!/bin/bash
# token-monitor.sh

PROJECT_PATH="/path/to/your/project"
LOG_FILE="/tmp/claude-auto.log"

check_tokens() {
    # 檢查 token 使用情況（需要配合監控工具）
    remaining=$(cc-usage check-remaining)
    echo "剩餘 tokens: $remaining"
    
    if [ "$remaining" -lt 1000 ]; then
        return 1  # token 不足
    else
        return 0  # token 充足
    fi
}

while true; do
    if check_tokens; then
        echo "$(date): Tokens 充足，啟動 Claude..." | tee -a $LOG_FILE
        cd $PROJECT_PATH
        
        timeout 4h claude --dangerously-skip-permissions -p "
        繼續開發任務：
        1. 檢查並修復任何建構問題
        2. 運行測試並修復失敗項目
        3. 改善代碼品質
        4. 更新文檔
        完成後進入待機模式
        " | tee -a $LOG_FILE
        
    else
        echo "$(date): Token 不足，等待補充..." | tee -a $LOG_FILE
        sleep 3600  # 等待1小時
    fi
    
    sleep 300  # 5分鐘後再檢查
done
```

---

## 實用腳本範例

### 1. 基本夜間自動化腳本
```bash
#!/bin/bash
# basic-auto-dev.sh

PROJECT_PATH="/path/to/your/project"
LOG_FILE="/tmp/claude-dev-$(date +%Y%m%d).log"

echo "$(date): 開始夜間自動化開發" | tee -a $LOG_FILE

cd $PROJECT_PATH

# 啟動完全自動化模式，設置最大6小時執行時間
timeout 6h claude --dangerously-skip-permissions -p "
🌙 夜間自動化開發任務清單：

## 第一優先級（必須完成）
1. 檢查並修復所有編譯錯誤
2. 解決建構失敗問題
3. 修復所有測試失敗

## 第二優先級（代碼品質）  
4. 處理所有 lint 警告和錯誤
5. 修復 TypeScript 類型錯誤
6. 重構重複代碼

## 第三優先級（改善和優化）
7. 添加缺失的單元測試
8. 更新過時的註解和文檔
9. 優化性能瓶頸
10. 清理死代碼和無用導入

## 第四優先級（維護）
11. 更新依賴到最新穩定版本
12. 生成 API 文檔
13. 整理 git 提交歷史

請按優先級順序執行，完成一個階段後報告進度。
如果遇到需要人工決策的問題，請詳細記錄並繼續下一個任務。
" | tee -a $LOG_FILE

exit_code=$?

if [ $exit_code -eq 124 ]; then
    echo "$(date): 6小時超時完成" | tee -a $LOG_FILE
elif [ $exit_code -eq 0 ]; then
    echo "$(date): 所有任務完成" | tee -a $LOG_FILE
else
    echo "$(date): 執行中斷，錯誤代碼: $exit_code" | tee -a $LOG_FILE
fi

echo "$(date): 夜間自動化結束，檢查日誌: $LOG_FILE" | tee -a $LOG_FILE
```

### 2. 循環重啟腳本
```bash
#!/bin/bash
# continuous-auto-dev.sh

PROJECT_PATH="/path/to/your/project"
LOG_FILE="/tmp/claude-continuous.log"
MAX_CYCLES=5  # 最多重啟5次

cd $PROJECT_PATH

for i in $(seq 1 $MAX_CYCLES); do
    echo "$(date): 開始第 $i/$MAX_CYCLES 輪開發循環" | tee -a $LOG_FILE
    
    timeout 2h claude --dangerously-skip-permissions -p "
    開發循環 $i：
    1. 檢查項目狀態
    2. 修復發現的問題  
    3. 改善代碼品質
    4. 如果沒有明顯問題，進行優化工作
    
    報告這輪完成的工作和發現的問題。
    " | tee -a $LOG_FILE
    
    echo "$(date): 第 $i 輪完成，休息5分鐘..." | tee -a $LOG_FILE
    sleep 300
done

echo "$(date): 所有循環完成" | tee -a $LOG_FILE
```

### 3. Cron 定時任務設置
```bash
# 編輯 crontab
crontab -e

# 添加以下任務：

# 每晚10點啟動夜間開發
0 22 * * * cd /path/to/project && /path/to/basic-auto-dev.sh

# 每6小時檢查一次（適合長期項目）
0 */6 * * * cd /path/to/project && claude --dangerously-skip-permissions -p "快速檢查並修復緊急問題" >> /tmp/claude-check.log 2>&1

# 每天早上8點生成開發報告
0 8 * * * cd /path/to/project && claude -p "生成昨夜開發工作摘要報告" > /tmp/daily-report-$(date +\%Y\%m\%d).txt

# 週末進行深度重構（每週六凌晨2點）
0 2 * * 6 cd /path/to/project && timeout 8h claude --dangerously-skip-permissions -p "執行深度代碼重構和架構優化"
```

### 4. 項目特定配置腳本
```bash
#!/bin/bash
# project-specific-setup.sh

PROJECT_PATH="/path/to/your/project"
cd $PROJECT_PATH

# 創建 CLAUDE.md 配置文件
cat > CLAUDE.md << 'EOF'
# 項目開發指南

## 技術棧
- Frontend: React + TypeScript + Tailwind CSS
- Backend: Node.js + Express + PostgreSQL  
- Testing: Jest + React Testing Library
- Build: Vite + ESBuild

## 代碼風格
- 使用 TypeScript 嚴格模式
- 遵循 ESLint + Prettier 規則
- 函數命名使用 camelCase
- 組件命名使用 PascalCase
- 常量使用 UPPER_CASE

## 測試要求
- 每個 API 端點都要有測試
- React 組件需要渲染測試
- 工具函數需要單元測試  
- 總覆蓋率需達到 80% 以上

## 常見任務命令
- 安裝依賴：`npm install`
- 啟動開發：`npm run dev`
- 運行測試：`npm test`
- 代碼檢查：`npm run lint`
- 代碼格式化：`npm run format` 
- 建構項目：`npm run build`
- 類型檢查：`npm run type-check`

## 部署流程
1. 確保所有測試通過
2. 更新版本號
3. 建構生產版本
4. 部署到 staging 環境測試
5. 部署到 production 環境

## 已知問題
- [ ] API 響應時間偶爾較慢
- [ ] 某些組件的 TypeScript 類型定義不完整
- [ ] 測試覆蓋率還未達到目標

## 優化目標
- [ ] 改善 API 性能
- [ ] 完善類型定義
- [ ] 增加測試覆蓋率
- [ ] 重構重複代碼
- [ ] 更新過時文檔
EOF

echo "CLAUDE.md 配置文件已創建"

# 設置 hooks（如果需要）
mkdir -p .claude/hooks

# 創建自動格式化 hook
cat > .claude/hooks/post-edit << 'EOF'
#!/bin/bash
# 文件編輯後自動格式化
if [[ "$CLAUDE_TOOL_OUTPUT" == *.js ]] || [[ "$CLAUDE_TOOL_OUTPUT" == *.ts ]] || [[ "$CLAUDE_TOOL_OUTPUT" == *.tsx ]]; then
    npm run format "$CLAUDE_TOOL_OUTPUT"
fi
EOF

chmod +x .claude/hooks/post-edit

echo "項目配置完成，可以開始使用 Claude Code"
```

---

## 安全考量與最佳實踐

### 安全措施

#### 1. 備份策略
```bash
# 設置自動備份
# 在啟動 Claude 前執行備份
git add . && git commit -m "Pre-Claude backup $(date)"

# 使用專用分支進行 AI 開發
git checkout -b ai-development-$(date +%Y%m%d)
```

#### 2. 容器化隔離（推薦）
```dockerfile
# Dockerfile for safe Claude development
FROM node:18-alpine

WORKDIR /app
COPY . .

# 安裝 Claude Code
RUN npm install -g @anthropic-ai/claude-code

# 限制網路存取（可選）
# RUN apk add --no-cache iptables

CMD ["claude", "--dangerously-skip-permissions"]
```

```bash
# 使用 Docker 運行
docker build -t claude-dev .
docker run -it -v $(pwd):/app claude-dev
```

#### 3. 權限配置替代方案
```json
// ~/.claude.json - 較安全的權限設置
{
  "allowedTools": [
    "Read(*)",
    "Write(*.js,*.ts,*.tsx,*.json,*.md)",
    "Bash(npm *)",
    "Bash(git add *)",
    "Bash(git commit *)",
    "Edit(*)"
  ],
  "deniedTools": [
    "Bash(rm *)",
    "Bash(sudo *)", 
    "Bash(curl *)",
    "Bash(wget *)"
  ]
}
```

### 風險控制

#### 風險評估
- **高風險**：系統文件被誤刪
- **中風險**：重要代碼被錯誤修改
- **低風險**：配置文件被更改

#### 預防措施
```bash
# 1. 定期備份
alias backup-before-claude="git add . && git commit -m 'Backup before Claude $(date)'"

# 2. 監控文件變化
alias show-claude-changes="git diff HEAD~1"

# 3. 快速回滾
alias undo-claude="git reset --hard HEAD~1"
```

---

## 故障排除

### 常見問題與解決方案

#### 1. Token 用完
```bash
# 檢查使用量
claude --version  # 查看配額信息

# 等待重置或升級計劃
# 設置監控腳本自動重試
```

#### 2. 權限問題
```bash
# 檢查權限設置
claude --help | grep permission

# 重新設置權限
/permissions  # 在 Claude 內部使用
```

#### 3. 任務中斷
```bash
# 使用 /compact 壓縮上下文
/compact

# 重新啟動並要求繼續
claude --dangerously-skip-permissions -p "繼續之前未完成的開發任務"
```

#### 4. 性能問題
```bash
# 清理 Claude 緩存
rm -rf ~/.claude/cache/*

# 重新啟動 Claude
```

### 調試技巧

#### 1. 詳細模式
```bash
# 啟用詳細日誌
claude --verbose --dangerously-skip-permissions
```

#### 2. 日誌分析
```bash
# 查看 Claude 日誌
tail -f ~/.claude/logs/claude.log

# 分析錯誤模式
grep "ERROR" ~/.claude/logs/* | head -20
```

#### 3. 逐步調試
```bash
# 分步執行任務
claude -p "只檢查項目狀態，不要修改任何文件"
claude -p "只修復編譯錯誤，一次一個文件"
claude -p "只運行測試，報告結果"
```

---

## 總結

Claude Code 可以實現真正的「睡覺前啟動，早上看結果」的自動化開發工作流程。關鍵要素：

### ✅ 成功要素
1. **正確使用命令**：`claude`（不是 claude-code）
2. **完全自動化**：`--dangerously-skip-permissions`
3. **任務排隊**：一次性輸入多個相關任務
4. **Token 管理**：監控使用量，設置自動重啟
5. **安全備份**：使用 git 和定期備份
6. **腳本化**：使用 shell 腳本或 cron 自動化

### 🚀 最佳實踐
- 在專用分支進行 AI 開發
- 設置 CLAUDE.md 項目配置文件
- 使用容器隔離提高安全性
- 定期監控和調整自動化腳本
- 保持任務具體明確，避免模糊指令

### ⚠️ 注意事項
- `--dangerously-skip-permissions` 有風險，需要適當預防措施
- Token 使用量需要監控，避免超額
- 複雜任務可能需要分階段執行
- 定期檢查和調整自動化策略

這樣的設置特別適合處理重複性維護任務、bug 修復、代碼品質改善和日常開發工作。