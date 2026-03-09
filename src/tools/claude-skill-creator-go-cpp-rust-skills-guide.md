# Claude Skill Creator 打造 Go、C++、Rust Skill 指南

如果你想替 Go、C++ 或 Rust 開發流程做一個真正有用的 Claude Skill，最有效的做法不是把一堆程式碼直接丟給 `skill-creator`，而是先定義清楚這個 Skill 要處理哪一種固定工作，再用幾個真實專案反覆測試與迭代。

`skill-creator` 比較像是幫你設計 Skill 的顧問，不是拿來硬塞訓練資料的工具。這個觀念如果一開始就抓對，後面做出來的 Skill 才會穩定、可重用，也比較容易維護。

## 核心觀念

- Skills 本質上是有結構的 `SKILL.md`，可以再搭配 `scripts/`、`assets/` 或 `references/`，用來定義何時啟用、啟用後怎麼工作。
- `skill-creator` 則是用來互動式建立或修改其他 Skill 的工具，它會協助你整理 frontmatter、`description`、主體流程，以及測試案例。
- 真正有價值的部分，不是讓它自動產生一份空殼，而是把你自己在 Go、C++、Rust 專案裡重視的 review 標準、debug 流程與效能觀察方法寫進去。

參考資料：

- [Claude Skills Cases: skill-creator](https://www.claudeskills.org/docs/skills-cases/skill-creator)
- [Anthropic skills/skill-creator/SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)
- [The Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf)

## 網路上有哪些 skill-creator 教學

如果你想先看別人怎麼用，現在已經有幾篇蠻實用的教學可參考：

- [Anthropic 官方 `skill-creator` SKILL.md](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md)：完整描述 Skill 建立流程，從理解範例、規劃 `scripts/` 與 `references/`，到初始化、編輯、封裝與迭代。
- [Claude 官方說明：用對話建立 Skill](https://support.claude.com/en/articles/12599426-how-to-create-a-skill-with-claude-through-conversation)：示範如何直接透過對話讓 Claude 背後呼叫 `skill-creator`。
- [SmartScope 完整教學](https://smartscope.blog/en/ai-development/skills/skill-creator-complete-guide/)：整理了從零開始、把既有對話轉成 Skill，以及改善 `SKILL.md`、`scripts/`、`references/` 的流程。
- [中文教學：用官方內建技能包創建者一鍵生成](https://vocus.cc/article/69a3c09dfd897800015798c4)：偏實作導向，適合快速了解實際操作畫面與步驟。
- [Reddit 討論串](https://www.reddit.com/r/ClaudeAI/comments/1onjxs9/how_to_set_up_claude_skills_in_15_minutes_for/)：有簡短設定與啟用流程。
- [YouTube 示範影片](https://www.youtube.com/watch?v=rihf3-mpNG4)：可直接看完整操作 demo。

## 推薦流程

這套流程對 Go、C++、Rust 都一樣，只是你在描述裡換成對應語言與工作重點。

1. **先開啟 `skill-creator`**

   在 Claude 的設定裡打開 Skills 功能，再啟用 `skill-creator`。

2. **先定義單一、明確的 workflow**

   例如：

   - 針對 Go 專案做 code review，重點放在 goroutine leak、`context.Context`、error handling。
   - 針對 C++ 專案做效能與安全性檢查，重點放在記憶體管理、未定義行為與 move semantics。
   - 針對 Rust 專案做 idiomatic review，重點放在所有權、錯誤處理、trait 設計與 async 最佳實踐。
   - 讀取 Go 的 `pprof` 報告與相關原始碼，提出效能優化建議。
   - 根據錯誤訊息、panic stack 與局部檔案內容，協助推導 root cause。

   一個 Skill 最好只處理一種清楚的工作流，不要做成萬能大雜燴。

3. **開新對話，下第一句指令**

   例如：

   > 我要做一個 Skill，讓你幫我 review Golang 專案的併發與錯誤處理，請用 `skill-creator` 幫我設計。

   或：

   > 幫我做一個 Skill，專門做 Rust code review。

   Claude 會自動啟動 `skill-creator`，開始互動式詢問需求。

4. **準備 3 到 5 個具體使用情境**

   每個情境都要包含：

   - 輸入長什麼樣子
   - 你期待的輸出輪廓
   - 你最在意它一定要做到的判斷

   這一步本質上是在先做規格，再做 Skill。

5. **回答 `skill-creator` 的問題**

   一般會被問到：

   - 這個 Skill 主要要做什麼
   - 會用在什麼情境
   - 使用者通常會貼什麼輸入
   - 需不需要 `scripts/` 幫忙執行工具
   - 是否需要 `references/` 存放範本、文件或檢查清單

6. **用 `skill-creator` 產生第一版骨架**

   你可以直接這樣描述：

   > 請用 `skill-creator` 幫我建立一個叫 `go-repo-reviewer` 的 Skill，專門對 Go 專案做 code review，重點關注 goroutine、channel、`context`、error wrapping 與併發安全。以下是我的典型使用情境……

   接著讓它補齊：

   - `name`
   - `description`
   - 觸發關鍵字
   - 主要工作步驟
   - 測試案例

7. **手動補上語言領域真正需要的 know-how**

   這一步通常才是成敗關鍵。你應該把這類規則直接寫進 `SKILL.md`：

   Go：

   - 是否可能產生 goroutine leak
   - 是否正確傳遞 `context.Context`
   - 是否使用 `%w` 包裝 error
   - library code 是否濫用 `panic`
   - 是否存在 data race 或 channel 關閉順序問題
   - 是否有 `time.After`、ticker、timer 之類的資源洩漏風險

   C++：

   - 是否濫用裸指標或手動記憶體管理
   - 是否存在未定義行為風險
   - 是否該用 move 卻發生不必要 copy
   - 是否適合加入 `clang-tidy`、sanitizer、benchmark 腳本

   Rust：

   - 是否遵循 idiomatic ownership 與 borrowing 寫法
   - 是否使用合適的 error handling 慣例
   - trait、模組切分與 async 流程是否合理
   - 是否需要把 `cargo clippy`、`cargo test`、`cargo fmt --check` 放進 `scripts/`

8. **用真實專案反覆測試與修正**

   最好的做法不是看它能不能「大概回答」，而是用實際 repo 驗證：

   - 它有沒有抓到你預期的問題
   - 它會不會忽略你最在意的風險
   - 它的輸出格式是否真的能直接拿來 review 或 debug

9. **啟用 Skill，回到實戰任務繼續迭代**

   把新 Skill 放進對應的 Skills 目錄後，直接對真實專案使用。失敗案例越具體，你下一輪修正就越準。

## GitHub 專案怎麼用最有價值

比較好的做法，不是把很多 GitHub 專案內容直接塞進 Skill 本體，而是把它們當成測試樣本。這個原則對 Go、C++、Rust 都成立。

- 挑幾個規模不大但結構完整的專案，當作測試 corpus。
- 準備兩種類型的專案：
  - 有明顯 code smell 或併發問題的專案。
  - 風格成熟、可當作正面參考的專案。
- 把這些專案當成 Skill 的驗證資料，而不是 `SKILL.md` 的正文內容。
- 對每個測試 repo 先定義成功條件，例如「至少指出 3 個特定並發問題」或「要能判斷這段 code 缺少 context cancel」。

這種用法的重點是可驗證，而不是只求輸出看起來像專家。

## 適合系統語言開發者的 Skill 類型

如果你平常就在做系統、效能、除錯或 API 開發，下面這幾種 Skill 會特別實用。

### Go 效能分析 Skill

- 輸入：`pprof`、`fgprof`、trace 結果，加上部分原始碼。
- 任務：找出 hotspot、allocation 問題、不必要的 goroutine、lock contention。
- 建議在 `SKILL.md` 寫明固定流程，例如先看 top N 熱點，再對照 call graph 與原始碼。

### Go Debug Skill

- 輸入：錯誤訊息、panic stack、race report、相關檔案。
- 任務：列出可能 root cause、優先排序、提供最小重現方向。

### Go Code Review Skill

- 輸入：單一檔案、diff，或整個 repo 的摘要。
- 任務：固定檢查 package 切分、命名、錯誤處理、`context` 傳遞、併發安全與可維護性。

### C++ 效能與安全性檢查 Skill

- 輸入：單一 `.cpp`/`.hpp`、diff，或整個模組摘要。
- 任務：檢查裸指標、記憶體管理、未定義行為風險、copy 與 move、過度動態配置。
- 可以搭配 `clang-tidy`、`clang++ -fsanitize=address,undefined` 等工具腳本。

### Rust Idiomatic Coding Skill

- 輸入：Rust 程式碼片段、crate 結構，或功能需求描述。
- 任務：檢查所有權、借用、error handling、trait 設計、模組劃分與 async 最佳實踐。
- 可以搭配 `cargo clippy`、`cargo test`、`cargo fmt --check`。

## 可直接拿去用的提示詞範例

### Go：併發與錯誤處理 review

> 使用 `skill-creator` 幫我建立一個新的 Claude Skill。  
> Skill 名稱暫定：`go-repo-reviewer`。  
>  
> 功能：  
> - 專門對 Golang 專案做 code review。  
> - 重點檢查：goroutine / channel 使用是否可能 leak、是否有正確使用 `context`、error wrapping 是否使用 `%w`、是否在 library code 使用 `panic`、是否存在 data race 風險。  
> - 可以讀取使用者提供的 Go 檔案內容，或整個專案目錄的摘要。  
>  
> 典型使用情境：  
> 1. 使用者請我 review 一段 Go code，找出 goroutine leak 與錯誤處理問題。  
> 2. 使用者要我針對 `./cmd/server/main.go` 做完整 review，列出前 10 個最嚴重問題。  
>  
> 請你：  
> - 設計合適的 `name`、`description` 與觸發關鍵字。  
> - 在主體內容裡寫出詳細的 review 步驟與 checklist。  
> - 提供幾個後續可用來實測的案例。

### C++：效能與 unsafe pattern 檢查

> 幫我用 `skill-creator` 建一個 C++ 效能與安全性檢查的 Skill。  
> 要點：  
> - 檢查裸指標使用、記憶體管理、未定義行為風險、copy vs move、過度動態配置。  
> - 可以搭配 `clang-tidy` 或 `clang++ -fsanitize` 等 scripts，請把這些命令寫進 `scripts/`。  
> - 希望生成的 `SKILL.md` 裡有詳細步驟：先做靜態檢查，再根據 warning 排序優先級。  

### Rust：idiomatic coding 與 crate 最佳實踐

> 用 `skill-creator` 幫我建立一個 Rust coding Skill。  
> 需求：  
> - 指導寫 idiomatic Rust，涵蓋所有權、借用、error handling、模組結構、trait 設計、async / tokio best practices。  
> - 使用者會貼 Rust code，或描述要實作的功能。  
> - 請在 `SKILL.md` 裡列出詳細 checklist，並參考 tokio、serde、axum 的常見最佳實踐。  

## Frontmatter 技術規格（官方限制）

這部分很多教學沒有提到，但直接影響 Skill 能不能被正常載入。

### `name` 欄位規則

- 最多 **64 個字元**
- 只能用小寫字母、數字、連字符（`-`）
- 不能包含 XML 標籤
- 不能包含保留字：`anthropic`、`claude`

命名風格建議用動名詞形式（gerund），這樣一眼就能看出 Skill 的作用：

```yaml
name: reviewing-go-concurrency    # 動名詞，清楚
name: go-code-reviewer             # 名詞片語，可接受
name: helper                       # 太模糊，避免
name: claude-tools                 # 含保留字，禁止
```

### `description` 欄位規則

- 最多 **1024 個字元**
- 不能為空
- 不能包含 XML 標籤
- **必須用第三人稱撰寫**（這是官方明確要求）

```yaml
# 正確：第三人稱
description: Reviews Go source code for goroutine leaks, context propagation, and error wrapping. Use when analyzing Go concurrency or reviewing goroutine/channel usage.

# 錯誤：第一人稱
description: I can help you review Go code for goroutine issues.

# 錯誤：第二人稱
description: You can use this to review Go code.
```

---

## Undertrigger 問題與 Description 寫法

Claude 天生有**少觸發（undertrigger）**的傾向——明明應該用 Skill 的場合，它卻沒有觸發。這是因為 Skill 的選取完全依賴 LLM 推理，沒有任何演算法關鍵字比對，description 太模糊就會造成 false negative。

### 對策：在 description 裡加入明確的觸發語言

官方建議讓 description 稍微「強硬一點」（pushy），直接寫出觸發條件：

```yaml
# 弱觸發（容易被跳過）
description: Helps with Go code quality.

# 強觸發（明確觸發條件）
description: Reviews Go source code for goroutine leaks, context propagation errors, and improper error wrapping. USE WHEN user asks to review, audit, or check Go code, or mentions goroutine, channel, context, or concurrency.
```

### 觸發優化數據

根據實測，加入明確觸發語言可以把 Skill 啟用率從 20% 提升到 50%，再加上具體範例後可達 90%。

### `when_to_use` 欄位（實驗性）

codebase 裡存在一個未正式文件化的 `when_to_use` 字段，它的內容會被附加到 description 後面：

```yaml
---
name: go-code-reviewer
description: Reviews Go source code for concurrency and error handling issues.
when_to_use: When user wants to review, debug, or audit Go code quality.
---
```

效果等同於把觸發條件寫進 description，但因為這個欄位可能已被棄用，**建議直接把觸發條件寫進 description** 比較保險。

---

## `disable-model-invocation`（手動觸發模式）

這個 frontmatter 欄位很少被提到，但對某些 Skill 非常重要。

```yaml
---
name: deploy-production
description: Deploys the application to production environment.
disable-model-invocation: true
---
```

設為 `true` 後，這個 Skill **不會出現**在 Claude 的自動選擇清單裡，只能透過明確的斜線指令觸發，例如 `/deploy-production`。

適合使用的場景：

- 有副作用的操作（部署、推送、傳送訊息）
- 需要明確確認才能執行的流程（`/commit`、`/send-slack`）
- 需要控制執行時機的互動式流程

對於 Go/C++/Rust 的情境：

```yaml
# 自動觸發（適合 review、分析類）
disable-model-invocation: false   # 預設值，可省略

# 手動觸發（適合執行 cargo publish、go generate、cmake build 之類有副作用的動作）
disable-model-invocation: true
```

---

## Progressive Disclosure：檔案架構設計

### SKILL.md 的大小限制

SKILL.md 本體建議**不超過 500 行**。超過時要把內容拆到獨立的參考檔案。

啟動時 Claude 只會預先載入 `name` 和 `description`；SKILL.md 本體只在 Skill 被選中時才讀取；其他參考檔案只在需要時才讀取。這表示即使你放了很大的參考文件，在用到它之前不會消耗 context token。

### 推薦的目錄結構

```text
go-repo-reviewer/
├── SKILL.md              # 主體，500 行以內，作為導覽索引
├── concurrency.md        # goroutine、channel 詳細 checklist
├── error-handling.md     # error wrapping 規則與範例
├── performance.md        # pprof 解讀流程
└── scripts/
    ├── check_race.sh     # go race detector 腳本
    └── run_vet.sh        # go vet 腳本
```

### 只做一層參考，不要巢狀

```markdown
# 正確：SKILL.md 直接連到所有參考檔
**Concurrency**: See [concurrency.md](concurrency.md)
**Error handling**: See [error-handling.md](error-handling.md)

# 錯誤：巢狀兩層，Claude 可能只讀到一半
# SKILL.md → advanced.md → details.md   ← 這樣不要做
```

### 超過 100 行的參考檔要加目錄

```markdown
# Go Concurrency Checklist

## 目錄
- Goroutine lifecycle
- Channel patterns
- Context propagation
- Race condition detection

## Goroutine lifecycle
...
```

---

## MCP 工具名稱格式

如果 Skill 要呼叫 MCP 工具，必須用完整格式 `ServerName:tool_name`，否則當有多個 MCP server 時 Claude 可能找不到工具：

```markdown
# 正確
Use GitHub:create_issue to file the bug report.
Use BigQuery:bigquery_schema to check the table structure.

# 錯誤（找不到工具）
Use create_issue to file the bug report.
```

---

## Evaluation-Driven 開發流程

官方建議**先寫測試案例再寫 Skill**，這和 TDD 邏輯一樣。

1. 不用 Skill，直接讓 Claude 做任務，記錄哪裡失敗
2. 根據失敗點設計 3 個以上具體測試情境
3. 建立基準（沒有 Skill 時的表現）
4. 寫剛好夠通過測試的最小 SKILL.md
5. 測試 → 觀察 Claude 的實際行為 → 迭代

測試情境格式範例：

```json
{
  "skills": ["go-code-reviewer"],
  "query": "Review this Go file for goroutine leak risks",
  "files": ["examples/worker_pool.go"],
  "expected_behavior": [
    "Identifies missing WaitGroup synchronization",
    "Points out goroutine leak in error path",
    "Suggests context.Done() handling"
  ]
}
```

建立「Claude A 設計 Skill」、「Claude B 測試 Skill」的雙角色迭代模式效果最好：Claude A 理解 Skill 格式，幫你設計；Claude B 拿真實任務測試，暴露缺漏。

---

## Scripts 的使用原則

### 執行 vs. 讀取的差異

```markdown
# 執行腳本（不消耗 context，只有 output 計 token）
Run `python scripts/check_goroutine.py` to analyze goroutine usage.

# 讀取為參考（會把腳本內容載入 context）
See `scripts/check_goroutine.py` for the analysis algorithm.
```

大多數情況用執行，只有在需要讓 Claude 理解演算法邏輯時才用讀取。

### Rust/Go/C++ 適合放進 scripts/ 的工具

```text
go-reviewer/scripts/
├── run_vet.sh          # go vet ./...
├── run_race.sh         # go test -race ./...
├── check_fmt.sh        # gofmt -l .

cpp-reviewer/scripts/
├── run_clang_tidy.sh   # clang-tidy with config
├── run_asan.sh         # -fsanitize=address,undefined

rust-reviewer/scripts/
├── run_clippy.sh       # cargo clippy -- -D warnings
├── run_fmt_check.sh    # cargo fmt --check
├── run_tests.sh        # cargo test
```

---

## Skill 發布前的完整 Checklist

```
### 基本品質
- [ ] description 用第三人稱
- [ ] description 包含「USE WHEN」或明確觸發條件
- [ ] name 只有小寫字母、數字、連字符，不含保留字
- [ ] SKILL.md 本體不超過 500 行
- [ ] 參考檔案只有一層深度（不巢狀）
- [ ] 較長的參考檔案（>100 行）有目錄

### 系統語言特定
- [ ] 語言核心規則明確寫入（goroutine leak / UB / borrow checker 等）
- [ ] scripts/ 裡有對應的靜態分析工具腳本
- [ ] 有真實程式碼範例作為測試 corpus

### 進階
- [ ] 有副作用的 Skill 設了 disable-model-invocation: true
- [ ] MCP 工具呼叫使用完整格式 ServerName:tool_name
- [ ] 至少有 3 個 evaluation 情境並跑過測試
- [ ] 在多個 Claude 版本（Haiku/Sonnet/Opus）驗證過
```

---

## 結論

如果你的目標是做出真正能落地的 Go、C++、Rust Skill，最重要的不是讓 `skill-creator` 幫你一次生出完整答案，而是先把 workflow 定義清楚，再用真實專案持續驗證。

換句話說，`skill-creator` 最適合拿來快速建立骨架與迭代方向；而真正讓 Skill 變得有用的，是你補進去的語言實戰規則、失敗案例與驗證標準。

技術細節上，記住幾個最容易被忽略的點：description 要用第三人稱並加入「USE WHEN」觸發語言、有副作用的 Skill 要加 `disable-model-invocation: true`、SKILL.md 不超過 500 行並用一層深度的 progressive disclosure、以及先寫 evaluation 再寫 Skill 內容。
