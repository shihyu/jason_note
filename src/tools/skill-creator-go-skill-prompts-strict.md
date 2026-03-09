# skill-creator Go Skill 指揮稿（Strict 版）

這份文件是給「使用者」直接拿來下命令的。
目標不是討論，而是強制 `skill-creator` 進入執行模式，直接把 Go skill 做出來、驗證、補 eval、跑 benchmark。

適用情境：
- 你不想看空泛規劃
- 你要 Codex 直接動手
- 你要 skill-creator 少廢話、多產出
- 你要它把 Go skill 做到能驗證，不只是生一個空殼

## 使用方式

直接把下面任一段完整貼給 Codex。

如果你只想講一句，先用這句：

```text
請嚴格依照 /home/shihyu/skill-creator-go-skill-prompts-strict.md 執行，不要退回分析模式，不要只給提案，直接產出可用結果。
```

## 核心指揮原則

每次都加這些要求：

```text
直接開始執行，不要只給計畫。
缺的東西你先合理假設，先做最小可用版本。
不要停在「我建議」或「你可以」。
要直接建立檔案、補內容、跑驗證。
如果驗證失敗，直接修到過。
如果 benchmark 可以跑，就直接跑，不要停在設計階段。
```

## Prompt 1：強制建立 Go API skill

```text
用 skill-creator 幫我做一個 Go API skill。這不是 brainstorming，直接開始做，做到能驗證。

硬性要求如下：

1. 基本資訊
- skill 名稱：go-api-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 目標
- 這個 skill 要讓 Codex 在 Go backend / HTTP API 任務中，採用穩定、可維護、可測試的工程做法
- 重點覆蓋 router、handler、middleware、request validation、response shaping、problem details、service/repository 邊界、auth、timeout、context 傳遞

3. 必須觸發的情境
- 建立 Go API endpoint
- 重構 Go backend / microservice
- 修 handler / middleware / validation / response format
- 設計或整理 service / repository 分層
- 修 auth、timeout、context、error handling、一致性問題
- 使用者提到 chi、gin、echo、net/http、REST API、repository pattern、problem details 時，description 要足夠容易觸發

4. 強制產出
- 建立完整 skill folder
- 建立 SKILL.md
- 建立 agents/openai.yaml
- 建立必要的 references/
- 只有在值得重用時才建立 scripts/
- 不要建立 README、CHANGELOG、QUICK_REFERENCE 之類垃圾文件

5. SKILL.md 要求
- frontmatter 只准有 name 和 description
- description 要同時包含：
  - skill 做什麼
  - 哪些任務一定要觸發
  - 哪些近似說法沒有明講 skill 名稱時也要觸發
- body 要偏實戰，不要寫教科書
- framework-specific 細節拆到 references，不要把 SKILL.md 塞爆

6. 執行要求
- 用最小可用版本先做出來
- 做完立刻跑 quick_validate.py
- 驗證失敗就直接修
- 不要做完停在「接下來可以補 validation」
- 直接把核心內容補到可用

7. 回報格式
- skill 建立在哪裡
- description 的 trigger 設計重點
- references 怎麼拆
- quick_validate.py 結果
```

## Prompt 2：強制重寫 description，提升觸發率

```text
用 skill-creator 幫我重構這個 skill 的 description，目標是更容易被觸發，而且不要只是堆關鍵字。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

執行要求：

1. 直接修改 SKILL.md frontmatter 的 description
2. 不要只提建議，直接改檔
3. description 必須清楚覆蓋：
- Go API
- router / handler / middleware
- request validation
- response shaping / problem details
- service / repository 分層
- auth / timeout / microservice refactor
- API consistency / error handling / testability

4. description 要做到：
- 有明確任務描述
- 有具體 trigger 情境
- 有一些近似表述也能命中
- 不要變成 keyword dump

5. 完成後：
- 跑 quick_validate.py
- 告訴我這次改動如何提升 trigger coverage
- 簡短指出舊版最弱的地方
```

## Prompt 3：強制補 evals 並跑 benchmark

```text
用 skill-creator 幫我補 evals，然後直接跑一次 benchmark。不要停在設計階段。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

硬性要求：

1. 建立 3 個 realistic eval prompts，至少包含：
- 新增 Go API endpoint
- 重構 handler/service/repository
- 修 validation、timeout、error response consistency

2. 把 evals 寫入：
- evals/evals.json

3. 每個 eval 都補 assertions
- assertion 要客觀、可判定
- 名稱要有辨識度
- 不要只寫模糊描述

4. 直接執行 with-skill 和 baseline 比較
- 如果這是新 skill，baseline 用 without_skill
- workspace 請按 iteration 結構放好

5. 產出：
- benchmark.json
- benchmark.md
- review viewer

6. 完成後直接給我：
- skill 與 baseline 的差異
- 哪些 assertions 沒鑑別力
- 哪些 eval 容易高變異
- 下一輪最值得改的點
```

## Prompt 4：一步到位，從零做到 benchmark

```text
用 skill-creator 幫我從零做一個 Go skill，並且一路做到 benchmark。不要只停在分析或建骨架。

任務定義：

1. skill 類型
- 類型：Go API skill
- 名稱：go-api-builder
- 路徑：/home/shihyu/.codex/skills

2. skill 目標
- 讓 Codex 處理 Go backend / API 任務時，有一套固定且工程化的做法
- 重點涵蓋 router、handler、middleware、validation、problem details、service/repository、auth、timeout、context、testing

3. 必須觸發的任務
- 建 API endpoint
- 重構 backend
- 修 validation / middleware / response format
- 改 service boundary / repository
- 修 auth / timeout / error handling / consistency

4. 必須產出的內容
- 完整 skill folder
- SKILL.md
- agents/openai.yaml
- 必要的 references/
- 必要時建立 scripts/
- evals/evals.json

5. 執行要求
- 先做最小可用版本，不要拖
- 接著跑 quick_validate.py
- 再補 evals 和 assertions
- 再跑 with-skill vs baseline benchmark
- 再產生 review viewer
- 中途不要停在「下一步建議」

6. 品質要求
- SKILL.md 精簡但夠用
- description 要有 trigger coverage，不要太保守
- references 要按主題拆分，不要亂堆
- scripts 只有在重複邏輯明顯時才加
- 不要產生多餘文件

7. 最後回報
- skill 路徑
- 驗證結果
- benchmark 結果
- 哪些地方還需要第二輪迭代
```

## Prompt 5：做 Go core skill，別做成空泛教學稿

```text
用 skill-creator 幫我做一個 Go core skill。不要寫成 Go 教學筆記，要寫成 Codex 可執行的 skill。

需求如下：

1. 基本資訊
- skill 名稱：go-core-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 目標
- 聚焦 idiomatic Go、package 設計、cmd/internal/pkg 結構、consumer-side interface、dependency injection、error handling、context 傳遞、goroutine/channel 協調、效能敏感邏輯

3. 觸發情境
- 寫 Go 程式
- 重構 Go 專案
- 整理 package 結構
- 修 interface 邊界
- 修 context / concurrency / error handling / performance 問題

4. 執行要求
- 直接建立 skill folder、SKILL.md、agents/openai.yaml
- 規劃 references/
- quick_validate.py 跑到通過
- 不要產生多餘文件
- SKILL.md 要偏工程決策，不要變成初學者教材

5. 回報
- 告訴我 description 如何確保 Go 任務容易命中
- 告訴我 references 如何支撐真正重構工作
```

## Prompt 6：做 Go testing skill，要求可驗證

```text
用 skill-creator 幫我做一個 Go testing skill，而且要做到可驗證，不要只生成說明文字。

需求如下：

1. 基本資訊
- skill 名稱：go-testing-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 目標
- 讓 Codex 在 Go 專案裡優先採用穩定的測試策略
- 涵蓋 unit test、table-driven tests、subtests、HTTP handler tests、integration tests、race detection、benchmark、fuzz、coverage

3. 觸發情境
- 使用者要求補測試
- 使用者要求修 failing tests
- 使用者要求加 benchmark / fuzz / race check
- 使用者要求測 HTTP handler 或 API 行為

4. 強制工作
- 建 skill
- 寫好 description
- 補 references
- 跑 quick_validate.py
- 設計 3 個 evals
- 跑 benchmark

5. 輸出
- skill 路徑
- eval 設計理由
- benchmark 結論
```

## 超短兇版

你懶得選時，直接貼這段：

```text
用 skill-creator 幫我做一個 Go API skill，放在 /home/shihyu/.codex/skills。不要只給計畫，直接建立 skill folder、寫 SKILL.md、產生 agents/openai.yaml、規劃 references、跑 quick_validate.py，並補 3 個 realistic evals 跑一次 benchmark。description 必須清楚覆蓋 Go API、handler、middleware、validation、response shaping、problem details、service/repository、auth、timeout、microservice refactor 等觸發情境。缺細節你先合理假設，先做最小可用版本，驗證失敗就直接修，不要停在分析。
```

## 補刀句

如果你覺得對方還是太保守，每次再補這句：

```text
不要把時間花在幫我解釋 skill-creator 流程，我要的是實際產物。直接改檔、補檔、驗證、跑結果。
```

## 最後原則

如果你真的要它做出東西，不要只說：

```text
用 skill-creator 幫我做一個 Go skill
```

這句太弱。

至少補上這四個：

1. `skill 名稱`
2. `skill 路徑`
3. `觸發情境`
4. `要不要跑 quick_validate / evals / benchmark`

最穩的寫法就是：

```text
用 skill-creator 幫我做一個 Go API skill，放在 /home/shihyu/.codex/skills。直接開始做，建立完整 skill folder、寫 SKILL.md、產生 agents/openai.yaml、補 references、跑 quick_validate.py、補 evals/evals.json、跑 benchmark。不要只停在分析。
```
