<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Claude Code 使用心得與技巧完整指南

您的 Claude Code 使用心得非常實用！讓我為您整理一份更完整的 Claude Code 使用指南，結合您的經驗和全球開發者社群的最佳實踐。

***

## 📝 CLAUDE.md 優化實戰

### 您的精簡理念是對的

官方初始化產生的 CLAUDE.md 確實冗長，建議精簡至：

```markdown
# 核心指令
請務必測試。
指定修改檔案：編輯 src/components/Button.tsx
使用專案既有架構模式
錯誤必須印 log 才處理
避免 over-engineering

# 工作流程
- 先討論方案再寫程式
- 每次修改後執行測試
- 提交前檢查 linting
```


### 更進階的 CLAUDE.md 技巧

- **分層管理**：在不同目錄放置不同的 CLAUDE.md
    - 專案根目錄：全域規則
    - 各子模組：特定規則
- **動態更新**：使用 `#` 鍵讓 Claude 自動更新 CLAUDE.md

***

## 💰 Token 節省攻略

### 模型切換策略

```bash
/model haiku    # 基礎操作（成本僅 Opus 的 5.3%）
/model sonnet   # 中等複雜任務
/model opus     # 複雜架構設計
```

**智能切換建議：**
- 讀檔案、簡單修改 → Haiku
- 程式邏輯、重構 → Sonnet 
- 架構設計、複雜 debug → Opus

### 上下文管理精髓

```bash
/clear          # 每完成一個任務就清空
/compact        # 保留重要資訊的壓縮
/cost           # 隨時監控使用量
/resume         # 從歷史恢復（省去重複輸入）
```

### 省 Token 的指令技巧

**精簡指令模式：**
```bash
# 壞習慣：冗長描述
請幫我分析這個檔案的程式碼結構，然後告訴我有什麼問題...

# 好習慣：直接指令
分析 src/utils.js 找出效能問題
```

**批次操作：**
```bash
# 一次處理多個任務
修正 src/*.ts 的型別錯誤 + 執行測試 + 更新文件
```

**使用檔案路徑：**
```bash
# 直接指定不用讓 Claude 搜尋
編輯 src/components/Button.tsx line 45-60
```

### 快取利用技巧

**重複使用相同文件結構：**
- Claude 會快取讀過的檔案
- 重新開啟專案時先讀取主要檔案
- 使用 `@filename` 快速引用

**記憶管理：**
```bash
# 建立專案記憶快照
/remember 專案架構使用 React + TypeScript + Vite

# 引用記憶避免重複說明
使用已記住的架構新增登入功能
```

### ccusage 監控神器

```bash
npm install -g ccusage
ccusage daily               # 查看每日用量
ccusage blocks --live       # 實時監控
ccusage summary            # 週/月度報告
ccusage alerts             # 設定用量警告
```


***

## 🔧 效率提升技巧

### Plan Mode 工作流程

```bash
think hard 如何重構這個模組？
ultrathink 設計這個功能的最佳架構
```


### 多工處理技巧

```bash
# 創建獨立工作樹（吳恩達課程推薦）
git worktree add ../project-feature-a feature-a
# 在不同工作樹同時運行多個 Claude Code
```

**課程實戰技巧：**
- 每個功能分支使用獨立工作樹
- 並行開發不同模組避免衝突
- 使用不同的 CLAUDE.md 管理各工作樹


### 權限管理優化

```bash
claude --dangerously-skip-permissions
alias claude='claude --dangerously-skip-permissions'
```


***

## 🚀 高級工作流程

### 測試驅動開發（TDD）

在 CLAUDE.md 中強制執行 TDD：

```markdown
MUST: 先寫測試再寫程式碼
MUST: 每次修改後執行完整測試
MUST: 所有測試必須通過才能提交
```


### 自動化指令

```bash
# .claude/commands/refactor.md
重構指定檔案：
1. 分析現有程式碼結構
2. 識別改進機會
3. 保持 API 相容性
4. 執行完整測試
```


***

## ⚡ 超級省 Token 密技

### 使用簡潔符號

```bash
# 標準指令
check src/api.js for bugs

# 符號簡化  
chk src/api.js bugs

# 極簡模式
fix: api.js:42 TypeError
```

### 預設模板指令

**在 CLAUDE.md 中定義縮寫：**
```markdown
# 快捷指令
- `rf` = 重構檔案保持 API 不變
- `tdd` = 先寫測試再實作
- `perf` = 效能分析和優化
- `docs` = 更新 README 和註解
```

### 多檔案操作技巧

```bash
# 一次處理相關檔案
同時修改 Button.tsx + Button.test.tsx + Button.stories.tsx

# 使用 glob 模式
更新所有 components/**/*.tsx 的 props 介面
```

### 上下文切割策略

**功能拆分：**
- 每個功能一個 session
- 完成後立即 `/clear`
- 用 `/resume` 連接相關 session

**檔案分組：**
- 前端 session：只處理 UI 相關
- 後端 session：只處理 API/DB
- 測試 session：專門寫測試

### 快速除錯模式

```bash
# 直接貼錯誤訊息
TypeError: Cannot read property 'map' of undefined at line 42

# 不用多說，Claude 會自動定位和修復
```

### 利用 Git 歷史

```bash
# 讓 Claude 從 commit 學習
基於最近 3 個 commits 的模式修改登入功能
```

***

## 📊 成本效益分析

| 使用類型 | 日均成本 | 備註 |
| :-- | :-- | :-- |
| 中型專案 | \$20–50 | 常規開發 |
| 大型專案 | \$100–200 | 重度使用 |
| Max Plan | \$200/月 | 無限用量 |

- **輸入幾乎免費**：大量上下文成本極低
- **輸出計價**：實際產出越多花費越高
- **快取機制**：重複內容可節省約 90% 成本

***

## 📚 吳恩達 x Anthropic 官方免費課程

### 課程概況

**課程名稱**：Claude Code: A Highly Agentic Coding Assistant  
**合作方**：DeepLearning.AI（吳恩達創辦）x Anthropic  
**講師**：Elie Schoppik（Anthropic 技術教育主管）  
**時長**：1小時50分鐘（共10個課程單元）  
**費用**：完全免費  
**課程連結**：https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/

### 📖 完整教學大綱

**學習目標**
- 使用 Claude Code 探索、開發、測試、重構和除錯程式碼庫
- 透過 MCP 伺服器擴展 Claude Code 功能
- 在三個實務專案中應用最佳實踐

**核心技能培養**
- 理解 Claude Code 的架構設計
- 建立 CLAUDE.md 專案文檔管理
- 使用 escape/clear 指令管理上下文
- 利用 git worktrees 進行並行開發
- GitHub 整合和 Issues 管理
- MCP 伺服器連接（Figma、Playwright）

### 🎯 三大實戰專案

**專案一：RAG 聊天機器人**
- 探索前後端架構設計
- 新增功能模組
- 撰寫完整測試套件
- 程式碼重構優化

**專案二：電商數據分析**
- Jupyter notebook 重構
- 轉換為互動式儀表板
- 數據視覺化優化

**專案三：Web 應用開發**
- 基於 Figma 設計稿建立 Web 界面
- 使用 Playwright 進行 UI 設計改進
- 響應式界面開發

### 🎓 吳恩達的 AI 民主化願景

> "AI 教育應該是大眾化、通識化，而不是只屬於少數精英"

這門課程體現了吳恩達的核心理念：
- **普及化學習**：讓任何人都能掌握 AI 工具
- **實務導向**：專注於真實工作場景應用
- **全球培育**：已培育超過 700 萬名 AI 人才

### 🚀 課程亮點特色

**高度自主性**
- Claude Code 能以最少人工輸入自主規劃、執行、改進程式碼
- 跨會話記憶和協作能力
- 通過 hooks 調用外部工具

**企業級應用**
- 真實專案案例研究
- 團隊協作工作流程
- 生產環境最佳實踐

**前瞻技術整合**
- MCP（Model Context Protocol）伺服器
- GitHub Issues 自動化
- Figma 設計稿直接轉程式碼

***

## 🛠 進階整合技巧

### IDE 協同作業

- 與 Cursor 無縫整合
- 支援 VS Code、JetBrains 系列


### MCP 工具擴展

```bash
npm install context7 browsermcp puppeteer
```

**吳恩達課程重點 MCP 伺服器：**
- **Figma MCP**：直接從設計稿生成程式碼
- **Playwright MCP**：自動化 UI 測試和改進
- **GitHub MCP**：Issues 管理和自動化

**實戰應用場景：**
```bash
# Figma 設計稿轉程式碼
使用 Figma MCP 將設計稿轉換為 React 元件

# 自動化測試
通過 Playwright MCP 建立完整的 E2E 測試
```


### Git 整合工作流程

- 自動分析 commit 歷史
- 整合 GitHub Issues
- 生成週報摘要
- 自動化 PR 審查

***

## 💡 社群最佳實踐

### 新手建議

1. 從 Codebase Q\&A 開始
2. 逐步導入程式碼編輯功能
3. 善用內建工具（bash、測試等）
4. 建立專案特定的工具清單

### 團隊協作

- 共享 CLAUDE.md 設定檔
- 建立統一的提示詞模板
- 制定一致的程式碼風格規範
- 撰寫專案專屬最佳實踐文件

### 超省錢使用模式

**學生/個人開發者**
- 95% 使用 Haiku 模式
- 只有卡關才切換 Sonnet
- 善用 `/compact` 和 `/clear`
- 月花費控制在 \$10 以下

**小團隊策略**
- 一人主導 Claude Code 操作
- 其他人提供需求和驗收
- 共享一個付費帳號降低成本
- 建立內部知識庫減少重複查詢

**企業級使用**
- 採用 Max Plan 無限制方案
- 建立企業級 CLAUDE.md 模板
- 整合 CI/CD 自動化流程
- 定期檢討和優化使用模式

***

## 🎯 實戰建議

**適合**

- 大型程式碼重構
- 新功能快速原型
- Bug 調查與修復
- 程式碼審查與優化
- 自動化腳本開發

**不適合**

- 極度複雜的演算法設計
- 需大量人工判斷的 UI/UX
- 高度安全敏感的程式碼

***

> "每次都要糾正 AI 的就放進 CLAUDE.md" —— 迭代優化，是發揮 Claude Code 最大價值的關鍵。

***

## 🏆 終極省 Token 檢查清單

### 開始前檢查
- [ ] 選對模型（90% 任務用 Haiku）
- [ ] 清空上次的 context（`/clear`）
- [ ] 準備好檔案路徑和行數
- [ ] 寫好精簡的指令

### 進行中優化
- [ ] 避免讓 Claude 解釋或總結
- [ ] 用符號和縮寫替代長句
- [ ] 批次處理相關任務
- [ ] 直接貼錯誤訊息不要描述

### 完成後清理
- [ ] 立即 `/clear` 釋放 context
- [ ] 更新 CLAUDE.md 避免重複
- [ ] 檢查 `/cost` 確認花費
- [ ] 記錄高效的指令模式

### 月度回顧
- [ ] 分析 `ccusage` 報告
- [ ] 調整模型使用比例
- [ ] 優化 CLAUDE.md 模板
- [ ] 分享團隊最佳實踐

***

**記住：輸入便宜、輸出昂貴。讓 Claude 少說話、多做事！** 💪

***

## 📖 延伸學習資源

### 官方推薦課程
- 🎓 **吳恩達 x Anthropic 免費課程**  
  https://www.deeplearning.ai/short-courses/claude-code-a-highly-agentic-coding-assistant/
  
- 📚 **Claude Code 官方文件**  
  https://docs.anthropic.com/en/docs/claude-code
  
- 🛠 **MCP 伺服器生態系統**  
  https://github.com/anthropic/mcp-servers

### 社群資源
- 💬 **DeepLearning.AI 社群討論**  
  課程相關問題解答和經驗分享
  
- 🔧 **GitHub Claude Code 整合範例**  
  實際專案應用案例和最佳實踐

### 持續學習建議
1. 完成吳恩達免費課程（1小時50分鐘）
2. 實際應用三大專案模式到自己的工作
3. 參與 DeepLearning.AI 社群討論
4. 定期關注 Anthropic 和 Claude Code 更新

> "AI 的未來在於讓每個人都能成為更好的開發者" —— Andrew Ng

