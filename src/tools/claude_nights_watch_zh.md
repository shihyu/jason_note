# ClaudeNightsWatch - 自主任務執行系統

基於 Claude CLI 的智能自主任務執行系統，可監控使用時間窗口並自動執行預定義任務。

## 🌟 核心功能

- **自主執行** - 無需手動干預自動執行任務
- **任務流程** - 使用簡單的 markdown 文件定義任務
- **安全規則** - 透過 rules.md 配置安全約束
- **智能定時** - 使用 ccusage 獲得準確的時間監控
- **預定開始** - 可配置特定時間開始執行
- **全面記錄** - 追蹤所有活動和執行歷史

## 📋 前置要求

### 必需組件
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code/quickstart) - 已安裝並配置

### 可選組件  
- [ccusage](https://www.npmjs.com/package/ccusage) - 提供精確時間監控
  ```bash
  npm install -g ccusage
  ```

## 🚀 快速開始

### 1. 安裝設置
```bash
# 克隆存儲庫
git clone https://github.com/aniketkarne/ClaudeNightsWatch.git
cd ClaudeNightsWatch

# 使腳本可執行
chmod +x *.sh

# 運行互動式設置
./setup-nights-watch.sh
```

### 2. 創建配置文件

**task.md - 任務定義**
```markdown
# 日常開發任務
1. 對所有源文件運行 linting
2. 更新依賴項到最新版本
3. 運行測試套件
4. 生成覆蓋率報告
5. 創建變更摘要
```

**rules.md - 安全規則**
```markdown
# 安全規則
- 在不備份的情況下永不刪除文件
- 只在項目目錄內工作
- 始終為變更創建 feature 分支
- 永不提交敏感信息
```

## 🎮 基本使用

### 啟動系統
```bash
# 立即啟動
./claude-nights-watch-manager.sh start

# 指定時間啟動
./claude-nights-watch-manager.sh start --at "09:00"
./claude-nights-watch-manager.sh start --at "2025-01-28 14:30"
```

### 管理命令
```bash
# 停止守護程序
./claude-nights-watch-manager.sh stop

# 檢查狀態
./claude-nights-watch-manager.sh status

# 重啟守護程序
./claude-nights-watch-manager.sh restart

# 查看任務和規則
./claude-nights-watch-manager.sh task
```

### 日誌管理
```bash
# 查看日誌
./claude-nights-watch-manager.sh logs

# 實時跟隨日誌
./claude-nights-watch-manager.sh logs -f

# 互動式日誌查看器
./view-logs.sh
```

## ⚙️ 系統架構

### 工作原理
1. **監控階段** - 持續監控 Claude 使用時間窗口
2. **定時階段** - 接近 5 小時限制時準備執行
3. **任務準備** - 讀取並組合 rules.md 和 task.md
4. **自主執行** - 使用 `claude --dangerously-skip-permissions` 執行
5. **記錄階段** - 完整記錄所有活動

### 時間檢測機制
| 情況 | 檢測方式 |
|------|----------|
| **有 ccusage** | API 獲得準確剩餘時間 |
| **沒有 ccusage** | 基於時間戳的檢查 |

### 自適應檢查間隔
| 剩餘時間 | 檢查頻率 |
|----------|----------|
| > 30 分鐘 | 每 10 分鐘 |
| 5-30 分鐘 | 每 2 分鐘 |
| < 5 分鐘 | 每 30 秒 |

## 🔄 多工任務管理

### Claude 多會話能力
- ✅ **技術上可行** - 一個帳號可同時多個 CLI 會話
- ⚠️ **共享配額** - 所有會話共用 5 小時使用限制
- 🎯 **建議策略** - 智慧規劃勝過暴力並行

### 多工執行策略

#### 策略一：多目錄管理（推薦）
```bash
~/claude-tasks/
├── project-a/          # 專案 A 獨立環境
│   ├── task.md
│   ├── rules.md
│   └── claude-nights-watch-*
├── project-b/          # 專案 B 獨立環境
│   ├── task.md
│   ├── rules.md
│   └── claude-nights-watch-*
└── project-c/          # 專案 C 獨立環境
    ├── task.md
    ├── rules.md
    └── claude-nights-watch-*
```

#### 策略二：時間分段執行
```bash
# 早上執行專案 A
./claude-nights-watch-manager.sh start --at "09:00"

# 中午執行專案 B
./claude-nights-watch-manager.sh start --at "13:00"

# 下午執行專案 C
./claude-nights-watch-manager.sh start --at "17:00"
```

#### 策略三：tmux 並行監控
```bash
# 創建 tmux 會話
tmux new-session -d -s claude-tasks

# 建立多個視窗
tmux new-window -t claude-tasks:1 -n 'project-a'
tmux new-window -t claude-tasks:2 -n 'project-b'
tmux new-window -t claude-tasks:3 -n 'project-c'

# 在各視窗啟動任務
tmux send-keys -t claude-tasks:1 'cd ~/claude-tasks/project-a && ./claude-nights-watch-manager.sh start' Enter
tmux send-keys -t claude-tasks:2 'cd ~/claude-tasks/project-b && ./claude-nights-watch-manager.sh start' Enter
tmux send-keys -t claude-tasks:3 'cd ~/claude-tasks/project-c && ./claude-nights-watch-manager.sh start' Enter
```

### 方案選擇建議

#### Pro 用戶（$20/月）
- 🎯 **時間分段執行**
- 🎯 **任務整合到單一 task.md**
- 🎯 **重點單一專案深度工作**

#### Max 5x 用戶（$100/月）
- 🎯 **2-3 個並行會話**
- 🎯 **tmux 分割管理**
- 🎯 **監控配額使用**

#### Max 20x 用戶（$200/月）
- 🎯 **真正多專案並行**
- 🎯 **5+ 個同時會話**
- 🎯 **適合大型團隊**

## ⚠️ 安全注意事項

### 重要提醒
> 此工具使用 `--dangerously-skip-permissions` 標誌，將不經確認執行任務

### 安全建議
- ✅ 在設置前手動測試所有任務
- ✅ 使用完整的 rules.md 防止破壞性操作
- ✅ 從簡單任務開始，逐步增加複雜性
- ✅ 定期監控日誌確保正確執行
- ✅ 保留重要數據備份
- ✅ 在隔離環境中運行

### 推薦安全規則
- 🔒 限制文件系統訪問到項目目錄
- 🚫 禁止刪除命令
- 🛡️ 防止系統修改
- 🌐 限制網路訪問
- 📊 設置資源限制

## 🐛 疑難排解

### 檢查清單
1. **Claude CLI 安裝** - `which claude`
2. **配置文件存在** - 驗證 task.md 存在
3. **查看日誌** - `./claude-nights-watch-manager.sh logs`
4. **使用量檢查** - `ccusage blocks`
5. **時間設置** - 檢查預定開始時間
6. **文件內容** - 確保 task.md 不為空
7. **精確監控** - 安裝 ccusage 提高準確性
8. **系統時間** - 檢查時間是否正確

## 📁 項目結構

```
claude-nights-watch/
├── claude-nights-watch-daemon.sh      # 核心守護程序
├── claude-nights-watch-manager.sh     # 管理界面
├── setup-nights-watch.sh              # 設置腳本
├── view-logs.sh                        # 日誌查看器
├── logs/                               # 日誌存儲
├── examples/                           # 示例文件
│   ├── task.example.md
│   └── rules.example.md
└── test/                              # 測試腳本
    ├── test-simple.sh
    ├── test-task-simple.md
    └── test-rules-simple.md
```

## 🧪 測試與驗證

```bash
# 進入測試目錄
cd test

# 運行簡單測試
./test-simple.sh

# 測試即時執行
./test-immediate-execution.sh
```

## 🤝 貢獻指南

1. Fork 存儲庫
2. 創建 feature 分支
3. 遵循現有代碼風格
4. 優先考慮安全性
5. 更新相關文檔
6. 提供使用示例
7. 確保測試通過
8. 提交 Pull Request

## 📄 授權資訊

- **授權** - MIT License
- **創建者** - [Aniket Karne](https://github.com/aniketkarne)
- **基於** - [CCAutoRenew](https://github.com/aniketkarne/CCAutoRenew) 專案

---

**記住**：強大的自動化伴隨重大責任。啟用自主執行前，請務必仔細檢查任務和規則！🚨
