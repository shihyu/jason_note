# Claude Code Skills 與 Skill Creator：打造你的專屬 AI 工具包

用 Claude Code 一段時間後，很容易碰到同一類問題：每次都要重新解釋專案背景、提交規範、框架慣例，或團隊自己的流程。這些知識如果只留在對話裡，就得不斷重講。

`Skills` 的用途，就是把這些可重複使用的知識、規則與操作流程封裝成一個可攜式工具包。搭配 `Skill Creator`，你可以更系統化地建立、測試與優化這些 Skill。

---

## 什麼是 Skills？

Skills 是一種可攜式的指令包，本質上是一個資料夾，裡面放了 Claude 需要知道的知識、腳本與資源。當你啟動某個 Skill，Claude 就會自動載入對應指令，不需要每次重新說明。

官方的 [anthropics/skills](https://github.com/anthropics/skills) 倉庫提供了幾個現成範例：

- **pdf / docx / xlsx / pptx**：讀取與分析各種文件格式
- **webapp-testing**：用 Playwright 測試本地網頁應用程式
- **algorithmic-art**：用 p5.js 生成演算法藝術
- **brand-guidelines**：套用品牌設計規範
- **mcp-builder**：快速建立 MCP 工具

這些只是起點；更有價值的地方，在於你可以依照自己的工作流打造專屬 Skill。

---

## Skills 的結構

每個 Skill 至少要有一個 `SKILL.md`，常見目錄結構如下：

```text
my-skill/
├── SKILL.md          # 必要，Skill 的核心定義
├── scripts/          # 可選，Python / Bash / JS 腳本（確定性任務）
├── references/       # 可選，補充文件，供 Claude 按需參考
└── assets/           # 可選，輸出用的靜態資源（模板、字體、圖片等）
```

這三個子目錄的定位不同：

- `scripts/`：Claude 會執行的程式碼，例如格式轉換、資料處理、驗證腳本
- `references/`：補充文件，Claude 需要時才讀進 context
- `assets/`：輸出會用到的靜態資源，例如 PowerPoint 模板、字體、Logo、圖片

---

## `SKILL.md` 的格式

`SKILL.md` 通常由 YAML frontmatter 加上 Markdown 內文構成：

```markdown
---
name: my-skill
description: This skill should be used when the user asks to "do X", "handle Y", or mentions Z-related topic. Describe what this skill does and when to trigger it.
---
# 詳細的操作指令
...
```

常見欄位如下：

| 欄位 | 必填 | 說明 |
| --- | --- | --- |
| `name` | ✓ | 小寫字母、數字、連字號，最長 64 字，且需與資料夾同名 |
| `description` | ✓ | 說明 Skill 做什麼、何時觸發，最長 1024 字 |
| `license` | - | 授權聲明 |
| `compatibility` | - | 環境需求，例如套件或網路條件 |
| `allowed-tools` | - | 預先核准的工具清單（實驗性） |

有兩個寫法慣例值得注意：

- `description` 建議使用第三人稱，例如 `This skill should be used when...`
- `SKILL.md` 內文建議使用祈使句，直接寫操作指令，而不是用第二人稱解說

---

## 三層載入機制

Skills 採用漸進式載入，避免每次都把所有內容塞進 context。

**第一層：常駐資訊**

只有 `name` 與 `description` 會長駐於 context 中，Claude 會用它們判斷是否應該啟動這個 Skill。

**第二層：啟動時載入**

當 Claude 判斷任務需要某個 Skill，才會載入 `SKILL.md` 內文。這份文件建議控制在 500 行內，大約 1,500 到 2,000 words 是相對理想的範圍。

**第三層：按需載入**

像 `scripts/`、`references/`、`assets/` 這些資源，只有在真的需要時才會讀取。這讓你可以安裝很多個 Skill，同時維持 token 使用量可控。

---

## 一個真實的 Skill 範例

`xlsx` Skill 的 `description` 是很好的範本，因為它把觸發情境定義得非常具體：

```yaml
---
name: xlsx
description: "Use this skill any time a spreadsheet file is the primary input or output.
  This means any task where the user wants to: open, read, edit, or fix an existing
  .xlsx, .xlsm, .csv, or .tsv file (e.g., adding columns, computing formulas, formatting,
  charting, cleaning messy data); create a new spreadsheet from scratch or from other
  data sources; or convert between tabular file formats. Trigger especially when the
  user references a spreadsheet file by name or path — even casually (like \"the xlsx
  in my downloads\") — and wants something done to it or produced from it. Do NOT trigger
  when the primary deliverable is a Word document, HTML report, standalone Python script,
  database pipeline, or Google Sheets API integration, even if tabular data is involved."
license: Proprietary. LICENSE.txt has complete terms
---
```

這個範例有兩個重點：

- 它把會觸發的情境列得非常細
- 它也清楚說明哪些情況**不要觸發**

這樣才能降低誤觸發，也避免搶到不屬於自己的任務。

---

## 安裝現有的 Skills

官方 Skills 可以透過 plugin 市集安裝：

```bash
/plugin marketplace add anthropics/skills
```

安裝後，直接自然地描述需求即可，例如：

```text
幫我分析這份 contract.pdf 裡的付款條款
把 sales_report.xlsx 的季度資料加上一欄 profit margin
```

Claude 會自動判斷是否該啟動對應 Skill。

---

## 用 Skill Creator 打造自己的 Skill

官方提供了 [Skill Creator](https://claude.com/plugins/skill-creator) plugin，專門用來建立、測試與優化 Skill。它本身也是一個 Skill，安裝後只要說明你想建立或改善哪一種 Skill，就能自動進入流程。

整體開發流程通常長這樣：

1. 定義需求
2. 撰寫 `SKILL.md` 草稿
3. 建立測試案例
4. 執行評估
5. 檢查輸出
6. 根據結果調整，再重跑

Skill Creator 會先詢問幾個關鍵問題，例如：

- 這個 Skill 要做什麼？
- 什麼情況下應該觸發？
- 預期輸出格式是什麼？
- 有沒有需要注意的邊界情況？

接著，它會協助產生 `SKILL.md` 草稿，並建立 2 到 3 個測試案例，通常存成 `evals/evals.json`：

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "使用者的實際需求",
      "expected_output": "期望的輸出描述",
      "files": []
    }
  ]
}
```

### 測試怎麼跑

Skill Creator 會對每個測試案例同時跑兩個版本：

- 一個有 Skill
- 一個沒有 Skill

如果是在改善既有 Skill，也會把舊版本當成 baseline 一起比較。這些版本會平行執行，之後再用 eval viewer 檢查結果。

除了執行測試，Skill Creator 還會先擬定量化評估用的 `assertions`，例如：

- 輸出是否包含欄位 `X`
- 是否實際使用了腳本 `Y`
- 是否產生預期格式的結果

最後會由專門的評分代理依據這些條件自動檢查。

### 三個幕後子代理

Skill Creator 內建三個專用子代理，各自負責不同工作：

- **Grader**：根據 `assertions` 檢查執行紀錄與輸出，判定是否通過，並附上證據
- **Comparator**：用盲測方式比較兩份輸出，從正確性、完整性、準確性、組織、格式與易用性等面向給分
- **Analyzer**：在比較完成後解盲，回頭分析兩個版本的 `SKILL.md` 與執行紀錄，說明贏家為什麼贏、輸家缺在哪裡

### Description 優化

Skill Creator 還提供專門優化 `description` 的流程，主要用來降低 undertrigger，也就是「該觸發卻沒觸發」的情況。

典型做法是：

1. 先產生 20 個觸發評估查詢
2. 其中約 8 到 10 個應該觸發，8 到 10 個不應該觸發
3. 用 60% 查詢做訓練，40% 做測試
4. 每個查詢跑三次，取平均觸發率
5. 讓 Claude 提出新的 `description`
6. 重複評估，最多迭代五輪

最後用測試集表現最好的版本作為新 `description`，避免對訓練樣本過度擬合。

### 觸發機制的一個微妙點

有一個現象值得注意：Claude 並不是遇到所有匹配條件都會查 Skill。若任務過於簡單，例如「讀一下這個 PDF」，Claude 可能直接自己處理，而不啟動任何 Skill。

因此，若你要評估某個 Skill 是否容易被正確觸發，測試案例不能設計得太淺。越接近真實、多步驟、具專業背景的任務，越能反映 `description` 的品質。

---

## 寫好 `description` 是關鍵

實際測下來，很多 Skill 的問題不是亂觸發，而是沒有被觸發。要改善這件事，`description` 必須寫得更主動、更具體。

假設你想做一個 dashboard 生成 Skill：

太模糊的寫法：

```yaml
description: 建立資料視覺化介面。
```

比較好的寫法：

```yaml
description: This skill should be used when the user asks to build a dashboard or data visualization interface. Use this skill whenever the user mentions dashboards, internal metrics, data display, or wants to visualize any kind of company data, even if they don't explicitly say "dashboard".
```

除了描述會觸發的情境，也應該明確列出**不觸發的邊界**。當多個 Skill 的領域有重疊時，這點尤其重要。

---

## 實作時踩過的坑

### 1. `name` 和資料夾名稱要完全一致

`SKILL.md` 裡的 `name` 欄位必須與資料夾名稱相同，否則 Skill 無法正確載入。

### 2. `SKILL.md` 要主動指向子目錄資源

Claude 不會自動掃描 `references/` 或 `scripts/` 裡有哪些東西，你需要在 `SKILL.md` 內明確寫出路徑，例如：

```markdown
## 延伸資源
需要更詳細的規則時，參考：
- **`references/formatting-guide.md`**：格式規範細節
- **`scripts/validate.py`**：格式驗證腳本
```

如果沒寫，這些補充資源很可能根本不會被使用。

### 3. `SKILL.md` 內文不要塞太多

由於 `SKILL.md` 在 Skill 啟動時會整份讀入 context，建議把大量邊界條件、補充說明、詳細範例移到 `references/`，讓主文件維持精簡。

### 4. `description` 不要超過 1024 字元

`description` 需要完整，但不用塞入整個操作流程。重點放在：

- 這個 Skill 做什麼
- 什麼情況下該觸發
- 哪些情況不該觸發

---

## 自己從零寫一個 Skill

如果不使用 Skill Creator，從零開始寫一個最簡單的 Skill 其實不複雜。以下用 commit message 規範 Skill 做示範。

先建立資料夾，名稱要與 Skill 的 `name` 一致：

```bash
mkdir -p ~/.claude/skills/commit-helper
```

放在 `~/.claude/skills/` 下的是個人全域 Skill，在任何專案都能使用。若只想在特定專案生效，也可以放在專案根目錄的 `.claude/skills/` 下，並直接納入版本控制。

有個容易忽略的點是：若全域與專案內存在同名 Skill，**全域 Skill 的優先級較高**。這代表你專案裡的同名版本可能不會生效。

接著建立 `SKILL.md`：

```markdown
---
name: commit-helper
description: This skill should be used when the user wants to write a commit message,
  asks "how should I commit this", or is about to run git commit. Guides writing
  conventional commit messages following the Conventional Commits specification.
---
# Commit Message 指引
Follow the Conventional Commits format: `type(scope): description`
Types: feat, fix, docs, style, refactor, test, chore
Rules:
- Keep the subject line under 72 characters
- Use present tense ("add feature", not "added feature")
- No period at the end of the subject line
- Reference issue numbers when relevant: `fix(auth): correct token expiry (#123)`
Examples:
Input: 新增使用者登入功能，用 JWT 處理 token
Output: feat(auth): add JWT-based user authentication
Input: 修復購物車數量計算錯誤
Output: fix(cart): correct item quantity calculation
```

這裡可以看出幾個關鍵：

- `name` 必須與資料夾名稱完全一致
- `description` 是 Claude 判斷是否啟動 Skill 的主要依據
- 內文最好直接給規則與 Input/Output 範例，讓行為更穩定

把這些知識封裝成 Skill 之後，你就不需要每次重新描述 commit 規範，也比較容易維持輸出一致性。

---

## Skills 和 `CLAUDE.md` 的差異

乍看之下，`CLAUDE.md` 與 Skills 都像是在告訴 Claude 應該怎麼做事，但用途其實不同。

簡單來說：

- `CLAUDE.md` 是某個專案的說明書
- Skills 是你可重複使用的工具包

| 項目 | `CLAUDE.md` | Skills |
| --- | --- | --- |
| 作用範圍 | 綁定特定專案目錄 | 可攜，能跨專案使用 |
| 觸發方式 | 進入專案時自動載入 | Claude 依需求判斷是否啟動 |
| 適合內容 | 專案專屬規範、架構說明 | 可重複使用的流程與領域知識 |
| 維護方式 | 跟著 repo 版控 | 獨立管理，也可分享給他人 |

例如，某個部落格專案的目錄結構、frontmatter 規範、URL rewrite 邏輯，很適合寫在 `CLAUDE.md`。但像是「寫 conventional commit」、「處理 Excel 檔案」、「套用品牌規範」這種跨專案都能重用的能力，就更適合寫成 Skill。

---

## 團隊開發時怎麼共享 Skills

當個人 Skill 寫得成熟之後，下一步通常就是思考如何讓團隊也能共用。

最直接的方法，是把 Skills 放進專案版本控制：

```text
.claude/skills/
```

這種方式適合與專案高度綁定的 Skill，例如依照該 codebase 命名習慣生成 component，或套用該專案特有流程。

如果 Skill 是整個組織都能重用的通用能力，也可以另外建立一個獨立的 skills repo，再透過 plugin marketplace 發佈：

```bash
/plugin marketplace add your-org/skills
```

另一種方式則是把 Skill 打包成 `.skill` 檔案，方便透過 Slack、Email 或 PR 傳給同事直接安裝。

---

## Skill 什麼時候該拆，什麼時候該合

這通常不是技術問題，而是觸發邏輯設計問題。

適合拆開的情況：

- 兩個任務的觸發時機完全不同
- 放在同一個 Skill 會讓 `description` 越來越難寫
- `SKILL.md` 已經長到接近 500 行

適合合併的情況：

- 兩個任務幾乎總是一起出現
- 它們共享大量背景知識
- 拆開只會增加維護成本

一個實用判斷方式是：**這個 Skill 的觸發場景，能不能用一句話說清楚？** 如果不行，通常表示範圍太大，應考慮拆分。

---

## 總結

Skills 解決的是「重複解釋背景」的問題，把規範、工作流程與領域知識包裝成可重複使用的能力。`Skill Creator` 則讓建立與優化 Skill 的流程變得可測、可比較、可迭代。

如果你有某件事每隔幾天就得重新跟 Claude 解釋一次，那通常就是值得做成 Skill 的候選。從一個簡單資料夾加一份 `SKILL.md` 開始，就已經足夠實用。
