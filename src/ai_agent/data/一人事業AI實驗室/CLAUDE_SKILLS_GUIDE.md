# 在 Google Antigravity 中實現 Claude Skills 漸進式披露

> **版本**: 1.0  
> **適用對象**: 使用 Google Antigravity IDE 的開發者

---

## 為什麼需要這個？

### 問題：上下文過長導致 AI 幻覺

Google Antigravity 的 `.agent/rules/` 目錄中的所有 Markdown 文件會**全部載入**到 AI 的上下文中。當規則文件累積過多（例如 10+ 個文件、50KB+、~15,000 tokens），AI 會：

- 🔴 產生「幻覺」（Hallucination）
- 🔴 遺忘或混淆指令
- 🔴 無法專注於當前任務
- 🔴 回應變慢、成本增加

### 解決方案：Claude Skills 漸進式披露

Claude Skills 是 Anthropic 提出的結構化指令架構，核心概念是**按需載入**：

```
┌──────────────────────────────────────────────────────────┐
│ Level 1: 元數據層 (~30-50 tokens)                        │
│          → 僅載入 name + description                     │
│          → 始終在上下文中                                │
├──────────────────────────────────────────────────────────┤
│ Level 2: 指令層 (數百~數千 tokens)                       │
│          → 任務匹配時才載入 SKILL.md                     │
├──────────────────────────────────────────────────────────┤
│ Level 3: 資源層 (視需要)                                 │
│          → 執行具體步驟時才讀取 reference 文件           │
└──────────────────────────────────────────────────────────┘
```

---

## 實作步驟

### Step 1: 建立 Skills 目錄結構

在專案根目錄建立 `.agent/skills/` 目錄：

```bash
# 基本結構
mkdir -p .agent/skills/{domain}/{topic}/reference

# 範例：前端框架 + 後端框架 + 專案規範
mkdir -p .agent/skills/frontend/{components,routing,state}/reference
mkdir -p .agent/skills/backend/{api,database,auth}/reference
mkdir -p .agent/skills/project-sop/reference
```

### Step 2: 建立根索引 SKILL.md

每個 domain 需要一個根索引，作為 **Level 1 元數據層**：

```markdown
## <!-- .agent/skills/frontend/SKILL.md -->

name: frontend-skills
description: >
前端開發技能集合。包含 Components、Routing、State Management
等主題。當用戶詢問前端相關問題時觸發。
tags: [frontend, react, ui]

---

# Frontend Skills

| Skill                               | 說明         | 觸發關鍵字              |
| :---------------------------------- | :----------- | :---------------------- |
| [components](./components/SKILL.md) | 組件開發規範 | component, 組件         |
| [routing](./routing/SKILL.md)       | 路由設計     | route, 路由, navigation |
| [state](./state/SKILL.md)           | 狀態管理     | state, store, redux     |
```

### Step 3: 建立主題 SKILL.md

每個主題的 SKILL.md 是 **Level 2 指令層**。**關鍵是精簡**：

```markdown
## <!-- .agent/skills/frontend/components/SKILL.md -->

name: frontend-components
description: >
前端組件開發規範。當用戶詢問 "component"、"組件"、
"reusable"、"props" 時觸發此 Skill。
tags: [frontend, components, react]
allowed-tools: [view_file, grep_search, replace_file_content]

---

# 組件開發規範

## 核心原則

1. 單一職責：每個組件只做一件事
2. Props 優先：避免內部狀態
3. 組合優於繼承

## 命名規範

| 類型     | 命名              | 範例           |
| :------- | :---------------- | :------------- |
| 頁面組件 | PascalCase + Page | `HomePage.tsx` |
| UI 組件  | PascalCase        | `Button.tsx`   |
| Hook     | use + 動詞        | `useAuth.ts`   |

## 詳細參考

如需完整範例，請參閱：
→ [reference/patterns.md](./reference/patterns.md)
→ [reference/testing.md](./reference/testing.md)
```

**撰寫原則**：

- SKILL.md 應保持在 **100 行以內**
- 僅包含最常用的 20% 內容
- 將進階內容移至 `reference/` 目錄

### Step 4: 建立 Reference 文件

將詳細文檔放入 `reference/` 目錄，這是 **Level 3 資源層**：

```
.agent/skills/frontend/components/
├── SKILL.md              # ~80 行，Quick Reference
└── reference/
    ├── patterns.md       # 完整設計模式
    ├── testing.md        # 測試指南
    └── examples.md       # 程式碼範例
```

AI 只有在 SKILL.md 中明確引用時，才會讀取 reference 文件。

### Step 5: 遷移現有 Rules

將 `.agent/rules/` 中的大文件遷移至 Skills：

```bash
# 1. 對於適中的文件，直接複製
cp .agent/rules/api-guide.md .agent/skills/backend/api/SKILL.md

# 2. 對於大文件 (500+ 行)，拆分：
#    - 建立精簡版 SKILL.md (~80 行)
#    - 完整版移至 reference/

# 3. 刪除舊的 rules 文件
rm .agent/rules/api-guide.md
```

### Step 6: 保留核心 Rules

`.agent/rules/` 中應只保留 **1-2 個核心文件**：

```markdown
## <!-- .agent/rules/core.md -->

## trigger: always_on

# 專案核心規則

1. 使用 TypeScript
2. 遵循 ESLint 規範
3. 提交前執行測試

詳細規範請見 `.agent/skills/`
```

---

## YAML Frontmatter 規範

每個 SKILL.md **必須**包含 YAML Frontmatter：

```yaml
---
name: skill-name # 必填：唯一識別碼 (小寫 + 連字號)
description: > # 必填：描述 + 觸發條件
  說明此 Skill 做什麼，以及何時應該被觸發。
  務必包含觸發關鍵字讓 AI 能語義匹配。
tags: [tag1, tag2] # 選填：分類標籤
allowed-tools: [tool1, tool2] # 選填：限制可用工具
---
```

### Description 撰寫技巧

❌ **錯誤**：

```yaml
description: API 開發指南
```

✅ **正確**：

```yaml
description: >
  後端 API 開發指南。當用戶詢問 "API"、"endpoint"、
  "REST"、"route"、"controller" 時觸發此 Skill。
```

---

## 最終目錄結構

```
.agent/
├── rules/                    # ← 精簡！只保留 1-2 個核心規則
│   └── core.md               #    (~100 tokens)
│
├── skills/                   # ← 新增！按需載入
│   ├── frontend/
│   │   ├── SKILL.md          # Level 1 索引
│   │   ├── components/
│   │   │   ├── SKILL.md      # Level 2 指令 (~80 行)
│   │   │   └── reference/    # Level 3 資源
│   │   │       └── patterns.md
│   │   └── routing/
│   │       └── SKILL.md
│   │
│   ├── backend/
│   │   ├── SKILL.md
│   │   └── api/
│   │       └── SKILL.md
│   │
│   └── project-sop/
│       ├── SKILL.md
│       └── reference/
│           └── workflow.md
│
└── workflows/                # ← 保持不變
    └── deploy.md
```

---

## 效益對比

| 指標           | 傳統 Rules            | Skills 架構         |
| :------------- | :-------------------- | :------------------ |
| **上下文載入** | 全部 (~15-20K tokens) | 按需 (~1-3K tokens) |
| **Token 節省** | -                     | **85-95%**          |
| **AI 專注度**  | 低（資訊過載）        | 高（聚焦任務）      |
| **幻覺風險**   | 高                    | 低                  |
| **可維護性**   | 難（大文件）          | 易（模組化）        |
| **擴展性**     | 差（難以新增）        | 佳（獨立 Skill）    |

---

## 常見問題

### Q: Antigravity 會自動讀取 Skills 嗎？

**A**: 是的！Antigravity 會掃描 `.agent/` 目錄。當問題與 SKILL.md 的 `description` 語義匹配時，會自動載入。

### Q: 現有 Workflows 還能用嗎？

**A**: 可以！`.agent/workflows/` 保持不變，仍透過 `/command` 觸發。

### Q: 精簡 SKILL.md 時應保留什麼？

**A**: 使用 **80/20 法則**：

- ✅ 保留最常用的 20% 內容
- ✅ 保留 Quick Reference 表格
- ❌ 移除進階用例、邊緣情況
- ❌ 移除長程式碼範例

### Q: 如何驗證 Skills 生效？

**A**:

1. 開啟新對話
2. 問一個與 Skill 相關的問題
3. 觀察 AI 是否引用 SKILL.md 內容
4. 或直接問：「你載入了哪些 Skills？」

---

## 快速開始 Checklist

- [ ] 建立 `.agent/skills/` 目錄
- [ ] 選擇最大的 2-3 個 rules 文件遷移
- [ ] 為每個 domain 建立根索引 SKILL.md
- [ ] 將大文件拆分為 SKILL.md + reference/
- [ ] 刪除已遷移的舊 rules
- [ ] 保留 1-2 個核心 rules
- [ ] 測試 AI 是否正確載入 Skills

---

## 結論

透過 Claude Skills 漸進式披露機制：

✅ 大幅減少上下文佔用 (節省 85-95%)  
✅ 提高 AI 專注度與準確性  
✅ 降低幻覺風險  
✅ 建立可維護的模組化規則庫

**立即開始**：建立你的第一個 Skill！

---

_靈感來源：[Claude Skills 官方文檔](https://claude.com) | [Anthropic 漸進式披露設計](https://docs.anthropic.com)_
