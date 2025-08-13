# Claude Nights Watch - 自主任務執行系統

一個基於Claude CLI的自主任務執行系統，會監控你的使用時間窗口並自動執行預定義的任務。

## 🌟 功能特色

- 🤖 **自主執行**：無需手動干預自動執行任務
- 📋 **任務流程**：在簡單的markdown文件中定義任務
- 🛡️ **安全規則**：在rules.md中配置安全約束
- ⏰ **智能定時**：使用ccusage獲得準確的時間或退回到基於時間的檢查
- 📅 **預定開始**：可以配置在特定時間開始
- 📊 **全面記錄**：追蹤所有活動和執行
- 🔄 **基於經驗證代碼**：建立在可靠的claude-auto-renew守護程序之上

## 📋 前置要求

- 已安裝並配置 [Claude CLI](https://docs.anthropic.com/en/docs/claude-code/quickstart)
- (可選) 安裝 [ccusage](https://www.npmjs.com/package/ccusage) 獲得準確時間：
  ```bash
  npm install -g ccusage
  ```

## 🚀 安裝步驟

### 1. 克隆存儲庫
```bash
git clone https://github.com/aniketkarne/ClaudeNightsWatch.git
cd ClaudeNightsWatch
```

### 2. 使腳本可執行
```bash
chmod +x *.sh
```

### 3. 運行互動式設置
```bash
./setup-nights-watch.sh
```

## 📝 配置文件

### 創建任務文件 (task.md)
```markdown
# 日常開發任務
1. 對所有源文件運行linting
2. 將依賴項更新到最新版本
3. 運行測試套件
4. 生成覆蓋率報告
5. 創建變更摘要
```

### 創建安全規則 (rules.md)
```markdown
# 安全規則
- 在不備份的情況下永不刪除文件
- 只在項目目錄內工作
- 始終為變更創建feature分支
- 永不提交敏感信息
```

## 🎮 使用方法

### 基本命令

#### 啟動守護程序
```bash
# 立即啟動
./claude-nights-watch-manager.sh start

# 在指定時間啟動
./claude-nights-watch-manager.sh start --at "09:00"
./claude-nights-watch-manager.sh start --at "2025-01-28 14:30"
```

#### 管理守護程序
```bash
# 停止守護程序
./claude-nights-watch-manager.sh stop

# 檢查狀態
./claude-nights-watch-manager.sh status

# 重啟守護程序
./claude-nights-watch-manager.sh restart
```

#### 查看日誌
```bash
# 查看日誌
./claude-nights-watch-manager.sh logs

# 實時跟隨日誌
./claude-nights-watch-manager.sh logs -f

# 使用互動式日誌查看器
./view-logs.sh
```

#### 其他命令
```bash
# 查看當前任務和規則
./claude-nights-watch-manager.sh task
```

## ⚙️ 工作原理

1. **監控階段**：守護程序持續監控你的Claude使用時間窗口
2. **定時階段**：接近5小時限制（2分鐘內）時準備執行
3. **任務準備**：讀取 `rules.md` 和 `task.md`，將它們組合成單個提示
4. **自主執行**：使用 `claude --dangerously-skip-permissions` 執行任務
5. **記錄階段**：所有活動記錄到 `logs/claude-nights-watch-daemon.log`

### 時間檢測機制

| 情況 | 檢測方式 |
|------|----------|
| **有 ccusage** | 從API獲得準確的剩餘時間 |
| **沒有 ccusage** | 退回到基於時間戳的檢查 |

### 自適應檢查間隔

| 剩餘時間 | 檢查頻率 |
|----------|----------|
| > 30分鐘 | 每10分鐘檢查一次 |
| 5-30分鐘 | 每2分鐘檢查一次 |
| < 5分鐘 | 每30秒檢查一次 |

## ⚠️ 安全注意事項

> **重要提醒**：此工具使用 `--dangerously-skip-permissions` 標誌運行Claude，意味著它將不經確認執行任務。

### 安全建議

- ✅ 在設置自主執行前始終手動測試任務
- ✅ 使用全面的rules.md防止破壞性操作
- ✅ 從簡單、安全的任務開始，逐漸增加複雜性
- ✅ 定期監控日誌確保正確執行
- ✅ 保留重要數據的備份
- ✅ 盡可能在隔離環境中運行

### 推薦安全規則

- 🔒 限制文件系統訪問到項目目錄
- 🚫 禁止刪除命令
- 🛡️ 防止系統修改
- 🌐 限制網路訪問
- 📊 設置資源限制

## 🐛 疑難排解

### 常見問題檢查清單

1. **檢查Claude CLI是否已安裝**
   ```bash
   which claude
   ```

2. **驗證task.md存在於工作目錄中**

3. **檢查日誌**
   ```bash
   ./claude-nights-watch-manager.sh logs
   ```

4. **驗證你有剩餘的Claude使用量**
   ```bash
   ccusage blocks
   ```

5. **檢查是否已過預定開始時間**

6. **確保task.md不為空**

7. **為了更好的準確性安裝ccusage**
   ```bash
   npm install -g ccusage
   ```

8. **檢查系統時間是否正確**

9. **驗證 `.claude-last-activity` 時間戳**

## 📁 項目結構

```
claude-nights-watch/
├── claude-nights-watch-daemon.sh     # 核心守護程序
├── claude-nights-watch-manager.sh    # 守護程序管理界面
├── setup-nights-watch.sh             # 互動式設置腳本
├── view-logs.sh                       # 互動式日誌查看器
├── README.md                          # 說明文件
├── LICENSE                            # MIT授權
├── CONTRIBUTING.md                    # 貢獻指南
├── CHANGELOG.md                       # 版本歷史
├── SUMMARY.md                         # 項目摘要
├── .gitignore                         # Git忽略文件
├── .github/                           # GitHub模板
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── pull_request_template.md
├── logs/                              # 所有日誌存儲位置（首次運行時創建）
├── examples/                          # 示例文件
│   ├── task.example.md               # 示例任務文件
│   └── rules.example.md              # 示例規則文件
└── test/                             # 測試腳本和文件
    ├── README.md                     # 測試說明
    ├── test-immediate-execution.sh   # 直接任務執行測試
    ├── test-simple.sh               # 簡單功能測試
    ├── test-task-simple.md          # 簡單測試任務
    └── test-rules-simple.md         # 簡單測試規則
```

## 📊 日誌管理

所有日誌都存儲在 `logs/` 目錄中，每個日誌包含：

- 🕐 **時間戳**：每個操作都有時間戳
- 📝 **完整提示**：發送給Claude的完整提示（規則 + 任務）
- 💬 **完整回應**：Claude輸出的所有內容
- ✅ **狀態訊息**：成功/失敗指示器

### 互動式日誌查看器功能

```bash
./view-logs.sh
```

- 瀏覽所有日誌文件
- 查看完整日誌或最後50行
- 過濾只看發送給Claude的提示
- 過濾只看Claude的回應
- 搜索錯誤
- 實時跟隨日誌

## 🧪 測試

測試腳本位於 `test/` 目錄：

```bash
cd test
./test-simple.sh  # 運行簡單測試
```

詳細測試說明請參閱 `test/README.md`。

## 🤝 貢獻

歡迎貢獻！請按照以下步驟：

1. Fork GitHub上的存儲庫
2. 在本地克隆你的fork
3. 創建feature分支 (`git checkout -b feature/amazing-feature`)
4. 按照我們的指南進行更改
5. 使用測試套件徹底測試
6. 提交更改 (`git commit -m 'Add amazing feature'`)
7. 推送到你的fork (`git push origin feature/amazing-feature`)
8. 在GitHub上創建Pull Request

請確保：
- 代碼遵循現有風格
- 優先考慮安全性
- 更新文檔
- 提供示例
- 測試通過

詳細指南請參閱 [CONTRIBUTING.md](https://github.com/aniketkarne/ClaudeNightsWatch/blob/main/CONTRIBUTING.md)。

## 📄 授權

此專案採用MIT授權 - 詳情請參閱 [LICENSE](https://github.com/aniketkarne/ClaudeNightsWatch/blob/main/LICENSE) 文件。

## 👥 致謝

- **創建者**：[Aniket Karne](https://github.com/aniketkarne)
- **基於**：優秀的 [CCAutoRenew](https://github.com/aniketkarne/CCAutoRenew) 專案
- **感謝**：Claude CLI團隊提供的優秀工具

---

**記住**：強大的自動化伴隨著重大責任。在啟用自主執行之前，請務必仔細檢查你的任務和規則！🚨