# Claude Code Skills & Plugins 知識指南

## 一、`~/.claude` 目錄結構總覽

```
~/.claude/
├── CLAUDE.md                  # 全域指令（所有專案都生效）
├── settings.json              # Claude Code 設定
├── settings.local.json        # 本機設定（不 commit）
├── config/                    # 額外設定檔
│
├── rules/                     # 全域規則（自動載入）
│   └── code-quality.md        # 例：代碼品質規範
│
├── commands/                  # 自訂 slash 指令
│   ├── cping.md               # /cping → 測試 Codex 連線
│   ├── gping.md               # /gping → 測試 Gemini 連線
│   └── ...
│
├── agents/                    # 自訂 subagent
│   ├── agent-browser/
│   └── ...
│
├── skills/                    # 本機自建 skill（不透過 plugin 安裝）
│   ├── all-plan/
│   └── ...
│
├── plugins/                   # Plugin 管理核心
│   ├── installed_plugins.json # 已安裝套件清單
│   ├── known_marketplaces.json# 已知 marketplace 來源
│   ├── config.json
│   ├── marketplaces/          # 從 GitHub clone 下來的原始碼
│   │   ├── anthropic-agent-skills/
│   │   ├── claude-plugins-official/
│   │   └── thedotmack/
│   └── cache/                 # 安裝後的本機快取（實際執行用）
│       ├── anthropic-agent-skills/
│       ├── claude-plugins-official/
│       └── thedotmack/
│
├── projects/                  # 專案記憶（每個專案的 memory）
├── history.jsonl              # 對話歷史
├── tasks/                     # 任務追蹤
├── todos/                     # 待辦清單
└── telemetry/                 # 遙測資料
```

---

## 二、Plugin vs Skill vs Command 差異

```
┌─────────────────────────────────────────────────────────────┐
│                      Claude Code 擴充機制                    │
├──────────────┬──────────────────┬───────────────────────────┤
│   類型        │   存放位置        │   說明                    │
├──────────────┼──────────────────┼───────────────────────────┤
│ CLAUDE.md    │ ~/.claude/        │ 全域永遠生效的指令         │
│              │ <project>/        │ 專案層級指令               │
├──────────────┼──────────────────┼───────────────────────────┤
│ rules/       │ ~/.claude/rules/  │ 自動載入的額外規則         │
│              │                   │（補充 CLAUDE.md）          │
├──────────────┼──────────────────┼───────────────────────────┤
│ commands/    │ ~/.claude/        │ 自訂 /slash 指令           │
│              │ commands/         │ 用 .md 檔定義              │
├──────────────┼──────────────────┼───────────────────────────┤
│ skills/      │ ~/.claude/skills/ │ 本機自建 skill             │
│              │ （或 plugin 安裝）│ 需要複雜工作流時使用       │
├──────────────┼──────────────────┼───────────────────────────┤
│ plugins      │ ~/.claude/plugins/│ 從 marketplace 安裝的套件  │
│              │ cache/            │ 可包含多個 skill           │
└──────────────┴──────────────────┴───────────────────────────┘
```

---

## 三、Plugin 安裝流程示意

```
GitHub Repo (marketplace)
  anthropics/skills
  anthropics/claude-plugins-official
          │
          │ claude plugin install
          ▼
~/.claude/plugins/marketplaces/    ← 原始碼（參考用）
  anthropic-agent-skills/
  claude-plugins-official/
          │
          │ 安裝時複製到 cache
          ▼
~/.claude/plugins/cache/           ← 實際執行用（快取）
  anthropic-agent-skills/
    example-skills/
      b0cbd3df1533/                ← commit hash（版本鎖定）
        skills/
          pdf/
          docx/
          skill-creator/
          ...
  claude-plugins-official/
    skill-creator/
      b36fd4b75301/
        skills/
          skill-creator/
          │
          ├── SKILL.md             ← skill 核心指令
          ├── scripts/             ← 可執行腳本
          ├── references/          ← 參考文件
          └── assets/              ← 靜態資源
```

---

## 四、Skill 指令格式解析

### 格式：`/<套件名>:<skill名>`

**套件名** 來自 `installed_plugins.json` 的 key，取 `@` 前面的部分：

```
installed_plugins.json key：

  "example-skills @ anthropic-agent-skills"
        ↑                    ↑
      套件名              marketplace名
   （指令用這個）
```

**skill名** 是該套件 `skills/` 資料夾底下的子目錄名稱：

```
~/.claude/plugins/cache/anthropic-agent-skills/
  example-skills/
    b0cbd3df1533/
      skills/
        pdf/            ← skill名 = pdf
        docx/           ← skill名 = docx
        skill-creator/  ← skill名 = skill-creator
        pptx/           ← skill名 = pptx
```

組合起來：

```
/example-skills:skill-creator
      ↑               ↑
   套件名          skills/ 底下的資料夾名
(@前面的部分)

一個套件可裝多個 skill，冒號左邊選套件，右邊選 skill
```

### 三個 skill-creator 對照表

```
指令                              套件來源                    版本
─────────────────────────────────────────────────────────────────
/example-skills:skill-creator    anthropic-agent-skills      b0cbd3d  ┐ 完全
/document-skills:skill-creator   anthropic-agent-skills      b0cbd3d  ┘ 相同
/skill-creator:skill-creator     claude-plugins-official     b36fd4b  ← 官方版（較新）
```

### 官方版差異（`/skill-creator:skill-creator`）

- `run_loop.py` 使用 **extended thinking** 優化 skill description
- 少了 Claude.ai / Cowork 環境下更新現有 skill 的說明

---

## 五、Skill 結構解析（SKILL.md 三層載入）

```
┌─────────────────────────────────────────────────┐
│                  Skill 載入順序                   │
├─────────────────────────────────────────────────┤
│  Layer 1: Metadata（永遠在 context）              │
│  ┌──────────────────────────────────────┐        │
│  │ name: skill-creator                  │ ~100字  │
│  │ description: 觸發條件 + 功能描述     │        │
│  └──────────────────────────────────────┘        │
│           ↓ skill 觸發時載入                      │
│  Layer 2: SKILL.md 本體                          │
│  ┌──────────────────────────────────────┐        │
│  │ 詳細指令、工作流程、範例            │ <500行  │
│  └──────────────────────────────────────┘        │
│           ↓ 需要時才載入                          │
│  Layer 3: Bundled Resources                       │
│  ┌──────────────────────────────────────┐        │
│  │ scripts/   → 可執行腳本             │ 無限制  │
│  │ references/→ 參考文件               │        │
│  │ assets/    → 靜態資源               │        │
│  └──────────────────────────────────────┘        │
└─────────────────────────────────────────────────┘
```

---

## 六、skill-creator 工作流程

```
用戶說「我想做一個 XXX skill」
          │
          ▼
    ① 訪談需求
    （用途、觸發時機、輸出格式）
          │
          ▼
    ② 寫 SKILL.md 草稿
          │
          ▼
    ③ 平行跑測試
    ┌─────────────────────────┐
    │  with_skill/   without_skill/  │
    │  （有skill）   （無skill）     │
    └─────────────────────────┘
          │
          ▼
    ④ 開啟 Eval Viewer（瀏覽器）
    ┌─────────────────────────┐
    │ Outputs tab：看輸出、留回饋    │
    │ Benchmark tab：量化評分        │
    └─────────────────────────┘
          │
          ▼
    ⑤ 根據回饋改進 SKILL.md
          │
          ▼
    ⑥ 重複 ③~⑤ 直到滿意
          │
          ▼
    ⑦ 優化 description
    （run_loop.py，官方版用 extended thinking）
          │
          ▼
    ⑧ 打包成 .skill 檔案
    python -m scripts.package_skill <skill-folder>
```

---

## 七、Skill 工作目錄結構（開發期）

```
<工作目錄>/
├── my-skill/                    ← skill 本體
│   ├── SKILL.md
│   ├── scripts/
│   ├── references/
│   └── assets/
│
└── my-skill-workspace/          ← 測試結果（自動建立）
    ├── skill-snapshot/          ← 改版前的備份
    ├── iteration-1/
    │   ├── eval-0-code-review/
    │   │   ├── with_skill/
    │   │   │   ├── outputs/
    │   │   │   ├── timing.json
    │   │   │   └── grading.json
    │   │   ├── without_skill/
    │   │   │   └── outputs/
    │   │   └── eval_metadata.json
    │   ├── benchmark.json
    │   └── benchmark.md
    └── iteration-2/
        └── ...
```

---

## 八、Skill 自動觸發 vs 手動呼叫

### 自動觸發機制

```
Claude 的 context 裡永遠存在所有 skill 的 metadata：
  name + description（~100字）

用戶說話時，Claude 判斷是否查閱某個 skill：

  ✅ 觸發條件：任務複雜、多步驟、description 符合
  ❌ 不觸發：簡單單步任務（即使 description 符合）
```

**關鍵**：「幫我讀這個 PDF」不會觸發 pdf skill，因為 Claude 直接用工具就能做。
「幫我把這份 100 頁 PDF 轉成有章節目錄的 Word 文件」才會觸發。

這就是為什麼 skill description 需要優化——description 要讓 Claude 知道「這是複雜任務，值得查 skill」。

### 手動呼叫

```
直接輸入指令強制觸發，不依賴自動判斷：

/skill-creator:skill-creator  我想做一個 Go skill
     ↑
  強制載入這個 skill
```

---

## 九、`marketplaces/` vs `cache/` 差異

```
~/.claude/plugins/
├── marketplaces/          ← git clone 的完整 repo（最新版）
│   └── anthropic-agent-skills/
│       └── skills/
│           └── skill-creator/   ← 永遠是最新 commit
│
└── cache/                 ← 安裝當下鎖定版本（實際執行用）
    └── anthropic-agent-skills/
        └── example-skills/
            └── b0cbd3df1533/    ← commit hash，版本固定
                └── skills/
                    └── skill-creator/
```

| | marketplaces/ | cache/ |
|---|---|---|
| 內容 | GitHub repo 完整原始碼 | 安裝時複製的快照 |
| 版本 | 跟著 autoUpdate 更新 | 鎖定在安裝當時的 commit |
| 用途 | 參考、瀏覽 | Claude Code 實際執行 |

**重點**：修改 `marketplaces/` 的檔案不會有任何效果，Claude 執行的是 `cache/` 裡的版本。

---

## 十、本機 Skill（`~/.claude/skills/`）

不透過 plugin 安裝，直接放在 `~/.claude/skills/` 的 skill：

```
~/.claude/skills/
└── all-plan/
    └── SKILL.md
```

**呼叫方式**：直接用 skill 名稱，不需要套件前綴

```
/all-plan
```

與 plugin skill 的差異：

```
本機 skill：   /all-plan
                ↑
            直接是 skills/ 底下的資料夾名

Plugin skill： /example-skills:skill-creator
                      ↑               ↑
                   套件名          skill名
```

---

## 十一、Slash 指令高亮問題

Claude Code CLI 的自動補全（高亮）只支援：
- 內建指令（`/help`, `/clear` 等）
- `~/.claude/commands/` 底下的 `.md` 自訂指令
- `~/.claude/skills/` 的本機 skill

**Plugin skill 的 `/<套件名>:<skill名>` 格式目前不支援高亮**，但輸入後執行是有效的。

變通方式：在 `~/.claude/commands/` 建捷徑：

```bash
# 建立有高亮的捷徑指令
cat > ~/.claude/commands/go-dev.md << 'EOF'
使用 skill-creator:skill-creator 幫我進行 Go 開發，包含 code review、效能分析和測試。
EOF
```

這樣 `/go-dev` 就有高亮和自動補全。

---

## 十二、`installed_plugins.json` 解讀

```json
{
  "version": 2,
  "plugins": {
    "example-skills@anthropic-agent-skills": {   // <套件名>@<marketplace>
      "scope": "project",                         // project 或 user
      "projectPath": "/home/shihyu",
      "installPath": "~/.claude/plugins/cache/anthropic-agent-skills/example-skills/b0cbd3df1533",
      "version": "b0cbd3df1533",                  // commit hash
      "installedAt": "2025-11-03T05:45:52.178Z",
      "lastUpdated": "2026-03-10T02:31:04.726Z",
      "gitCommitSha": "c74d647e56e6daa12029b6acb11a821348ad044b"
    }
  }
}
```

**Scope 說明：**
- `"scope": "user"` → 所有專案都可用
- `"scope": "project"` → 只有特定 projectPath 下可用

---

## 十三、常用指令速查

```bash
# 查看已安裝 plugin
cat ~/.claude/plugins/installed_plugins.json | jq '.plugins | keys'

# 查看某套件包含哪些 skill
ls ~/.claude/plugins/cache/anthropic-agent-skills/example-skills/*/skills/

# skill 觸發格式
/<套件名>:<skill名>

# 常用 skill
/example-skills:pdf           # PDF 處理
/example-skills:docx          # Word 文件
/example-skills:pptx          # PowerPoint
/example-skills:xlsx          # Excel
/skill-creator:skill-creator  # 建立/改進 skill（官方版，有 extended thinking）
```

---

## 十四、CLAUDE.md 載入優先順序

```
載入順序（後者可覆蓋前者）：

1. ~/.claude/CLAUDE.md          ← 全域（所有專案）
2. ~/.claude/rules/*.md         ← 全域補充規則
3. <project>/.claude/CLAUDE.md  ← 專案層級
4. <subdir>/.claude/CLAUDE.md   ← 子目錄層級（最高優先）
```

> **重點**：CLAUDE.md 越靠近當前工作目錄，優先權越高。
