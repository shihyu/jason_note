# Spec-Kit 開發指南

## 📋 目錄
- [什麼是 Spec-Kit](#什麼是-spec-kit)
- [核心概念](#核心概念)
- [安裝方式](#安裝方式)
- [五大核心命令](#五大核心命令)
- [實務開發應用](#實務開發應用)
- [完整開發流程範例](#完整開發流程範例)
- [支援的 AI 助手](#支援的-ai-助手)
- [適用場景](#適用場景)

---

## 什麼是 Spec-Kit

**Spec-Kit** 是 GitHub 開源的工具包，用於實現「**規格驅動開發**」(Spec-Driven Development, SDD)。

### 傳統開發 vs 規格驅動開發

| 傳統開發 | 規格驅動開發 |
|---------|------------|
| 先寫程式碼，文件只是參考 | 規格文件是核心，直接生成程式碼 |
| 邊寫邊想怎麼實作 | 先想清楚要什麼，再決定怎麼做 |
| 憑感覺寫程式 (Vibe Coding) | 結構化、可預測的開發流程 |

---

## 核心概念

### 三大原則
1. **意圖驅動** - 先定義「是什麼」(what) 和「為什麼」(why)
2. **多階段細化** - 不是一次性生成，而是逐步完善
3. **充分利用 AI** - 讓 AI 理解規格並自動生成實現

---

## 安裝方式

### 方法一：持久安裝（推薦）
```bash
# 安裝 CLI 工具
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git

# 初始化專案
specify init <專案名稱>

# 檢查系統環境
specify check

# 升級工具
uv tool install specify-cli --force --from git+https://github.com/github/spec-kit.git
```

### 方法二：直接執行
```bash
# 不安裝直接使用
uvx --from git+https://github.com/github/spec-kit.git specify init <專案名稱>
```

### 初始化選項
```bash
# 指定 AI 助手
specify init my-project --ai claude
specify init my-project --ai copilot
specify init my-project --ai cursor-agent

# 在當前目錄初始化
specify init . --ai claude
specify init --here --ai claude

# 強制覆蓋現有檔案
specify init . --force --ai claude

# 跳過 Git 初始化
specify init my-project --ai gemini --no-git

# 啟用除錯模式
specify init my-project --ai claude --debug
```

---

## 五大核心命令

### 1. `/speckit.constitution` - 建立專案治理原則

**目的**：定義專案的「遊戲規則」

**使用時機**：專案一開始，在寫任何程式碼之前

**範例指令**：
```
/speckit.constitution 建立專注於程式碼品質、測試標準、使用者體驗一致性和效能要求的原則
```

**輸出**：`.specify/memory/constitution.md` 檔案

**實務應用**：
- **App 開發**：支援裝置、最低系統版本、離線功能、效能標準
- **Web 開發**：瀏覽器支援、響應式設計、無障礙要求、SEO 規範
- **一般開發**：程式碼風格、測試覆蓋率、安全性要求、文件規範

---

### 2. `/speckit.specify` - 定義功能需求

**目的**：描述要建構什麼功能

**使用時機**：Constitution 建立後，開始定義具體功能

**重點**：
- ✅ 專注於「要做什麼」和「為什麼」
- ✅ 描述使用者故事和功能需求
- ❌ 不用提技術細節和實作方式

**範例指令**：
```
/speckit.specify 
建立一個相簿管理應用程式。使用者可以：
- 建立多個相簿，依日期分組
- 在主頁面拖放重新排序相簿
- 相簿不能巢狀（不能有子相簿）
- 每個相簿內以磁磚方式預覽照片
- 照片不上傳到雲端，只存在本地
```

**輸出**：`specs/001-feature-name/spec.md` 檔案

**實務應用**：
- **App 開發**：「記帳 App，可記錄收支、分類管理、看報表、匯出資料」
- **Web 開發**：「電商網站，有購物車、結帳、會員系統、訂單追蹤」
- **一般開發**：「API 服務，提供使用者認證、資料 CRUD、檔案上傳」

---

### 3. `/speckit.plan` - 規劃技術實作

**目的**：決定使用什麼技術堆疊和架構

**使用時機**：需求確認後，開始技術規劃

**範例指令**：
```
/speckit.plan
使用 Vite 搭配最少的第三方套件。盡可能使用原生 HTML、CSS 和 JavaScript。
圖片不上傳到任何地方，metadata 存在本地 SQLite 資料庫。
```

**輸出檔案**：
- `plan.md` - 實作計畫
- `data-model.md` - 資料模型
- `contracts/api-spec.json` - API 規格
- `research.md` - 技術研究
- `quickstart.md` - 快速開始指南

**實務應用**：
- **App 開發**：「用 Flutter + Firebase + Provider 狀態管理」
- **Web 開發**：「Next.js + TypeScript + Prisma + PostgreSQL」
- **一般開發**：「Python FastAPI + SQLAlchemy + Redis + Docker」

---

### 4. `/speckit.tasks` - 生成任務清單

**目的**：將實作計畫拆解成可執行的小任務

**使用時機**：Plan 確認後，實作前

**範例指令**：
```
/speckit.tasks
```

**輸出**：`tasks.md` 檔案，包含：
- 按使用者故事組織的任務
- 任務依賴關係和執行順序
- 可平行執行的任務標記 `[P]`
- 每個任務的檔案路徑
- 測試任務（如果需要）

**任務範例**：
```markdown
## Phase 1: 資料層實作
- [ ] 1.1 建立 SQLite 資料庫連線 (`src/db/connection.js`)
- [ ] 1.2 建立 Album 資料模型 (`src/models/Album.js`)
- [ ] 1.3 建立 Photo 資料模型 (`src/models/Photo.js`)
- [P] 1.4 撰寫資料模型測試 (`tests/models.test.js`)

## Phase 2: 業務邏輯
- [ ] 2.1 實作相簿 CRUD 服務 (`src/services/albumService.js`)
- [ ] 2.2 實作照片管理服務 (`src/services/photoService.js`)
```

---

### 5. `/speckit.implement` - 執行實作

**目的**：讓 AI 按照任務清單自動實作

**使用時機**：Tasks 確認後，開始寫程式

**範例指令**：
```
/speckit.implement
```

**執行流程**：
1. ✅ 驗證必要檔案存在（constitution, spec, plan, tasks）
2. ✅ 解析 `tasks.md` 的任務清單
3. ✅ 按正確順序執行任務
4. ✅ 尊重依賴關係和平行執行標記
5. ✅ 遵循 TDD 流程（先寫測試）
6. ✅ 提供進度更新和錯誤處理

**注意事項**：
- AI 會執行本地 CLI 命令（如 `npm`, `dotnet`, `python`）
- 確保已安裝所需的開發工具
- 完成後需手動測試（特別是瀏覽器端功能）

---

## 實務開發應用

### 開發者常用語對照表

| Spec-Kit 命令 | 開發者用語 | 產出文件 |
|--------------|----------|---------|
| `/speckit.constitution` | 開發準則、Team Guidelines | PRD 前置規範 |
| `/speckit.specify` | 產品需求文件 (PRD) | User Stories |
| `/speckit.plan` | 技術設計文件 (Tech Spec) | System Design |
| `/speckit.tasks` | Sprint Planning、任務拆解 | Task Board |
| `/speckit.implement` | Development Sprint | Working Code |

### 額外輔助命令

| 命令 | 用途 |
|-----|------|
| `/speckit.clarify` | 澄清模糊的需求（建議在 plan 前使用）|
| `/speckit.analyze` | 檢查規格一致性（tasks 後、implement 前）|
| `/speckit.checklist` | 生成品質檢查清單 |

---

## 完整開發流程範例

### 範例：記帳 App 開發

#### Step 1: 定規矩
```
/speckit.constitution

我要做的記帳 App 原則：
1. 使用者隱私第一，資料只存本地，絕不上傳雲端
2. 支援 iOS 14+ 和 Android 8+
3. 離線優先，不需網路連線
4. 介面簡潔，3 秒內可完成記帳
5. 所有功能必須有單元測試，覆蓋率 > 80%
```

#### Step 2: 寫需求
```
/speckit.specify

記帳 App 功能需求：

【核心功能】
1. 快速記帳
   - 輸入金額、選擇分類、備註（選填）
   - 預設今天日期，可修改
   - 區分收入/支出

2. 分類管理
   - 預設 10 個常用分類（飲食、交通、娛樂...）
   - 可自訂新增分類、修改顏色圖示

3. 報表查看
   - 月報表：收支總覽、分類圓餅圖
   - 年報表：每月趨勢折線圖
   - 可切換月份/年份

4. 資料匯出
   - 匯出 CSV 格式
   - 可選日期區間
   - 包含所有欄位

【使用者流程】
- 開啟 App → 直接在首頁快速記帳
- 下方 Tab：首頁、列表、報表、設定
```

#### Step 3: 選技術
```
/speckit.plan

技術堆疊：
- 框架：Flutter 3.16+
- 狀態管理：Provider
- 本地儲存：sqflite (SQLite)
- 圖表：fl_chart
- 檔案處理：csv 套件

架構：
- Clean Architecture
- Repository Pattern
- 三層結構：Presentation / Domain / Data
```

#### Step 4: 拆任務
```
/speckit.tasks

（AI 自動生成任務清單，約 30-40 個任務）
```

#### Step 5: 開始實作
```
/speckit.implement

（AI 自動開始寫程式，完成所有功能）
```

---

## 支援的 AI 助手

| AI 助手 | 支援狀態 | 備註 |
|--------|---------|------|
| GitHub Copilot | ✅ 完整支援 | |
| Claude Code | ✅ 完整支援 | |
| Cursor | ✅ 完整支援 | |
| Gemini CLI | ✅ 完整支援 | |
| Windsurf | ✅ 完整支援 | |
| Qwen Code | ✅ 完整支援 | |
| opencode | ✅ 完整支援 | |
| Auggie CLI | ✅ 完整支援 | |
| CodeBuddy CLI | ✅ 完整支援 | |
| Roo Code | ✅ 完整支援 | |
| Amazon Q Developer | ❌ 不支援 | 不支援自訂斜線命令參數 |

---

## 適用場景

### ✅ 適合使用 Spec-Kit 的情境

1. **從零開始的新專案** (Greenfield)
   - 全新產品開發
   - MVP 快速驗證

2. **複雜的業務邏輯**
   - 需要清楚規格文件
   - 多人協作開發

3. **需要品質保證**
   - 完整測試覆蓋
   - 程式碼審查

4. **探索多種方案**
   - 技術選型比較
   - 平行實作不同版本

5. **現有系統改造** (Brownfield)
   - 重構舊系統
   - 技術棧升級

### ⚠️ 不太適合的情境

- 極簡單的腳本（幾十行程式碼）
- 需要大量客製化的 UI 設計
- 實驗性質的 Proof of Concept
- 沒有明確需求的探索性開發

---

## 專案結構範例

```
my-project/
├── .specify/
│   ├── memory/
│   │   └── constitution.md          # 專案治理原則
│   ├── scripts/
│   │   ├── create-new-feature.sh    # 建立新功能腳本
│   │   ├── setup-plan.sh            # 設定計畫腳本
│   │   └── check-prerequisites.sh   # 環境檢查腳本
│   ├── specs/
│   │   └── 001-feature-name/
│   │       ├── spec.md              # 功能規格
│   │       ├── plan.md              # 實作計畫
│   │       ├── tasks.md             # 任務清單
│   │       ├── data-model.md        # 資料模型
│   │       ├── research.md          # 技術研究
│   │       └── contracts/
│   │           └── api-spec.json    # API 規格
│   └── templates/
│       ├── spec-template.md
│       ├── plan-template.md
│       └── tasks-template.md
├── src/                              # 實際程式碼
├── tests/                            # 測試程式碼
└── CLAUDE.md                         # Claude 指令參考
```

---

## 最佳實踐

### 1. Constitution 階段
- ✅ 明確定義技術限制（瀏覽器支援、裝置支援）
- ✅ 設定品質標準（測試覆蓋率、效能指標）
- ✅ 定義開發規範（程式碼風格、命名慣例）

### 2. Specify 階段
- ✅ 使用使用者故事格式
- ✅ 包含驗收標準
- ✅ 描述邊界情況
- ⚠️ 避免提及技術細節

### 3. Plan 階段
- ✅ 研究最新框架版本
- ✅ 考慮技術債務
- ✅ 評估第三方套件
- ⚠️ 避免過度工程化

### 4. Tasks 階段
- ✅ 確保任務可獨立測試
- ✅ 標記可平行執行的任務
- ✅ 包含驗收檢查點

### 5. Implement 階段
- ✅ 安裝所需開發工具
- ✅ 監控執行進度
- ✅ 測試瀏覽器端功能
- ✅ 處理執行時錯誤

---

## 疑難排解

### Git 認證問題（Linux）
```bash
#!/usr/bin/env bash
set -e

echo "下載 Git Credential Manager..."
wget https://github.com/git-ecosystem/git-credential-manager/releases/download/v2.6.1/gcm-linux_amd64.2.6.1.deb

echo "安裝中..."
sudo dpkg -i gcm-linux_amd64.2.6.1.deb

echo "設定 Git..."
git config --global credential.helper manager

echo "清理..."
rm gcm-linux_amd64.2.6.1.deb
```

### 常見問題

**Q: AI 生成的程式碼不符合需求？**
A: 回到 `/speckit.specify` 階段，澄清需求並重新執行

**Q: 技術選型不合適？**
A: 使用 `/speckit.plan` 重新規劃，或先用 `/speckit.clarify` 確認

**Q: 任務拆解太粗？**
A: 要求 AI 更細緻地拆解，或手動編輯 `tasks.md`

**Q: 執行時出現環境錯誤？**
A: 使用 `specify check` 檢查環境，確保工具已安裝

---

## 參考資源

- **官方文檔**：[Spec-Driven Development Methodology](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- **GitHub Repository**：https://github.com/github/spec-kit
- **Issue 回報**：https://github.com/github/spec-kit/issues
- **視頻教學**：[YouTube Overview](https://www.youtube.com/watch?v=a9eR1xsfvHg)

---

## 授權

MIT License - 開源免費使用

---

**最後更新**：2025-10-27
