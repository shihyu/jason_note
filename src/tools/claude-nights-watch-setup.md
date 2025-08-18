# ClaudeNightsWatch 完整設定指南

## 概述
ClaudeNightsWatch 是一個自動化守護程序，會在 Claude CLI 使用時間窗口結束前自動執行預定義的任務。

## 設定步驟

### 步驟 1：執行互動式設定腳本

執行設定腳本：
```bash
./setup-nights-watch.sh
```

此腳本會：
1. **檢查必要條件**
   - 確認 Claude CLI 已安裝
   - 檢查 ccusage（可選，用於精確時間追蹤）

2. **引導設定流程**
   - 提示建立任務檔案
   - 設定安全規則
   - 配置守護程序選項

### 步驟 2：建立任務檔案 (task.md)

**範例任務檔案：**
```markdown
# 自動化開發任務

## 目標：
1. 執行程式碼品質檢查
2. 更新專案文件
3. 執行測試套件

## 具體任務：
- 在 src/ 目錄執行 linting
- 修正發現的問題
- 執行所有單元測試
- 產生測試覆蓋率報告
- 更新 CHANGELOG.md
```

### 步驟 3：建立安全規則 (rules.md)

**預設安全規則包含：**
- **禁止破壞性命令**：不執行 `rm -rf`、不刪除系統檔案
- **保護敏感資料**：不暴露密碼、API keys
- **限制工作範圍**：只在專案目錄內工作
- **Git 安全**：不強制推送到主分支、建立功能分支
- **最佳實踐**：測試變更、備份資料、記錄修改

### 步驟 4：啟動守護程序

**立即啟動：**
```bash
./claude-nights-watch-manager.sh start
```

**排程啟動：**
```bash
# 今天 09:00 啟動
./claude-nights-watch-manager.sh start --at "09:00"

# 特定日期時間啟動
./claude-nights-watch-manager.sh start --at "2025-01-28 14:30"
```

### 步驟 5：驗證運作狀態

**檢查系統狀態：**
```bash
# 檢查守護程序狀態
./claude-nights-watch-manager.sh status

# 查看執行日誌
./claude-nights-watch-manager.sh logs

# 互動式日誌檢視器
./view-logs.sh

# 查看當前任務設定
./claude-nights-watch-manager.sh task
```

## 運作原理

### 核心機制
1. **監控時間**：持續監控 Claude 使用時間窗口
2. **自動觸發**：在 5 小時限制前 2 分鐘準備執行
3. **執行任務**：結合 rules.md + task.md，使用 `claude --dangerously-skip-permissions` 自動執行
4. **完整記錄**：所有活動記錄在 `logs/` 目錄

### 時間檢查邏輯
- **有 ccusage**：從 API 取得準確剩餘時間
- **無 ccusage**：使用時間戳記檢查
- **自適應檢查間隔**：
  - 剩餘 30+ 分鐘：每 10 分鐘檢查
  - 剩餘 5-30 分鐘：每 2 分鐘檢查
  - 剩餘 <5 分鐘：每 30 秒檢查

## 任務完成狀態

- ✅ 檢查並執行 setup-nights-watch.sh 互動式設定
- ✅ 建立 task.md 任務檔案
- ✅ 建立 rules.md 安全規則檔案
- ✅ 啟動守護程序
- ✅ 驗證設定是否正常運作

## ⚠️ 重要安全提醒

此工具會**自動執行任務且無需確認**，務必：

1. **事前測試**：先手動測試所有任務
2. **完整規則**：設定詳細的安全規則
3. **定期監控**：檢查執行日誌
4. **資料備份**：備份重要資料

## 常用管理命令

```bash
# 停止守護程序
./claude-nights-watch-manager.sh stop

# 重新啟動
./claude-nights-watch-manager.sh restart

# 更新任務
./claude-nights-watch-manager.sh update-task

# 清理日誌
./claude-nights-watch-manager.sh clean-logs
```

---

**設定完成！** ClaudeNightsWatch 現在會在適當時機自動執行您的任務。