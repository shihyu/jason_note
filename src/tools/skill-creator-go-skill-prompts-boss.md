# skill-creator Go Skill 指揮稿（老闆下命令版）

這份文件是給使用者直接拿來下命令的。
語氣設計成「交辦任務」而不是「討論需求」。
重點只有一個：叫 `skill-creator` 直接把 Go skill 做出來，不准停在分析、提案、空談。

## 使用方式

直接把下面任一段貼給 Codex。

如果只想先丟一句話，就先用這句：

```text
照 /home/shihyu/skill-creator-go-skill-prompts-boss.md 執行。不要跟我討論流程，直接做完。
```

## 通用總指令

每次都先補這段：

```text
這是執行任務，不是討論題。
不要只給我分析、建議、規劃或選項。
直接開始做，先交最小可用版本，再補完整。
缺資料就先做合理假設，不要卡住。
該建檔就建檔，該改檔就改檔，該驗證就驗證。
quick_validate.py 要跑。
能補 evals 就補。
能跑 benchmark 就直接跑。
如果失敗就直接修，不要把錯誤原樣丟回來當結果。
最後只回報產物、路徑、驗證、benchmark 與待補強項。
```

## 指令 1：做一個 Go API skill

```text
用 skill-creator 幫我做一個 Go API skill，現在就做，不要停在分析。

交付要求如下：

1. 基本資訊
- skill 名稱：go-api-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- 這個 skill 要處理 Go backend / HTTP API 開發與重構
- 內容必須涵蓋 router、handler、middleware、request validation、response shaping、problem details、service/repository 邊界、auth、timeout、context 傳遞

3. 觸發情境
- 建立 Go API endpoint
- 重構 Go backend / microservice
- 修 handler / middleware / validation / response format
- 整理 service / repository 分層
- 修 auth / timeout / error handling / API consistency
- 使用者提到 chi、gin、echo、net/http、REST API、problem details、repository pattern 時，要容易命中

4. 必須交付
- skill folder
- SKILL.md
- agents/openai.yaml
- 必要的 references/
- 需要時才建立 scripts/

5. 文件要求
- SKILL.md frontmatter 只保留 name 與 description
- description 要明確寫出做什麼、什麼情境該觸發
- body 要能拿來執行，不要寫成空泛教學文
- variant / framework-specific 細節拆到 references，不要全部塞進 SKILL.md
- 不要建立 README、CHANGELOG、QUICK_REFERENCE 這些多餘檔案

6. 驗證要求
- 做完立刻跑 quick_validate.py
- 失敗就修到過

7. 回報要求
- 告訴我 skill 建在哪裡
- 告訴我 description 為什麼這樣寫
- 告訴我 references 怎麼拆
- 告訴我驗證結果
```

## 指令 2：做一個 Go core skill

```text
用 skill-creator 幫我做一個 Go core skill。不要把它寫成 Go 入門教材，要寫成能指揮 Codex 幹活的 skill。

交付要求如下：

1. 基本資訊
- skill 名稱：go-core-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- 聚焦 idiomatic Go、package 設計、cmd/internal/pkg 結構、consumer-side interface、dependency injection、error handling、context 傳遞、goroutine/channel 協調、效能敏感邏輯

3. 觸發情境
- 寫 Go 程式
- 重構 Go 專案
- 整理 package 結構
- 修 interface 邊界
- 修 concurrency / context / error handling / performance 問題

4. 必須交付
- skill folder
- SKILL.md
- agents/openai.yaml
- 必要的 references/
- 視情況建立 scripts/

5. 驗證要求
- quick_validate.py 要跑到過

6. 回報要求
- skill 路徑
- description 的 trigger 設計
- references 的拆分理由
```

## 指令 3：做一個 Go testing skill

```text
用 skill-creator 幫我做一個 Go testing skill，直接做到可驗證，不要只交說明文件。

交付要求如下：

1. 基本資訊
- skill 名稱：go-testing-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- 涵蓋 unit test、table-driven tests、subtests、HTTP handler tests、integration tests、race detection、benchmark、fuzz、coverage

3. 觸發情境
- 使用者要求補測試
- 使用者要求修 failing tests
- 使用者要求補 benchmark / fuzz / race check
- 使用者要求測 API / handler 行為

4. 必須交付
- skill folder
- SKILL.md
- agents/openai.yaml
- references/
- 如果值得重用再建 scripts/

5. 驗證要求
- 跑 quick_validate.py
- 補 3 個 realistic evals
- 跑一次 benchmark

6. 回報要求
- skill 路徑
- eval 設計理由
- benchmark 結果
```

## 指令 4：重寫 description，提高觸發率

```text
用 skill-creator 幫我重寫這個 skill 的 description，目標是提高觸發率。不要只提建議，直接改檔。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

要求如下：

1. 直接修改 SKILL.md frontmatter 的 description
2. 新 description 必須清楚覆蓋：
- Go API
- router / handler / middleware
- request validation
- response shaping / problem details
- service / repository 分層
- auth / timeout
- backend / microservice refactor
- API consistency / error handling / testability

3. description 要同時做到：
- 明確說出 skill 做什麼
- 明確列出哪些情境該觸發
- 即使使用者沒講 skill 名稱，也能靠任務語義命中
- 不要寫成雜亂關鍵字堆砌

4. 做完後：
- 跑 quick_validate.py
- 告訴我新舊 description 差異
- 告訴我這次怎麼補 trigger coverage
```

## 指令 5：補 evals，跑 benchmark

```text
用 skill-creator 幫我補 evals，然後跑 benchmark。不要只停在設計檔案。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

要求如下：

1. 設計 3 個 realistic eval prompts，至少包含：
- 新增 Go API endpoint
- 重構 handler/service/repository
- 修 validation、timeout、error response consistency

2. 把 evals 寫進：
- evals/evals.json

3. 每個 eval 都要補 assertions
- assertion 要客觀、可驗證
- 名稱要清楚
- 不要模糊

4. 直接跑 with-skill 與 baseline 比較
- 新 skill baseline 用 without_skill
- workspace 請按 iteration 結構整理

5. 產出：
- benchmark.json
- benchmark.md
- review viewer

6. 最後回報：
- 哪些地方 skill 明顯贏 baseline
- 哪些 assertions 沒有鑑別力
- 哪些 eval 可能有高變異
- 下一輪最值得改的點
```

## 指令 6：一步做到位

```text
用 skill-creator 幫我從零做一個 Go API skill，並一路做到 benchmark。不要停在分析，不要只交骨架。

任務如下：

1. skill 名稱：go-api-builder
2. skill 路徑：/home/shihyu/.codex/skills
3. skill 目標：
- 讓 Codex 處理 Go backend / API 任務時，採用固定且工程化的做法
- 涵蓋 router、handler、middleware、validation、problem details、service/repository、auth、timeout、context、testing

4. 必須觸發的任務：
- 建 API endpoint
- 重構 backend
- 修 validation / middleware / response format
- 改 service boundary / repository
- 修 auth / timeout / error handling / consistency

5. 必須完成的工作：
- 建 skill folder
- 寫 SKILL.md
- 產生 agents/openai.yaml
- 補 references/
- 必要時建立 scripts/
- 跑 quick_validate.py
- 建 evals/evals.json
- 補 assertions
- 跑 with-skill vs baseline benchmark
- 產生 review viewer

6. 品質要求：
- SKILL.md 精簡但能用
- description 要有足夠 trigger coverage
- references 要合理拆分
- 不要產生多餘文件

7. 最後交付：
- skill 路徑
- 驗證結果
- benchmark 結果
- 下一輪建議
```

## 極短版命令

懶得挑就直接丟這段：

```text
用 skill-creator 幫我做一個 Go API skill，放在 /home/shihyu/.codex/skills。直接開始做，不要只給計畫。建立 skill folder、寫 SKILL.md、產生 agents/openai.yaml、補 references、跑 quick_validate.py，並補 3 個 realistic evals 跑一次 benchmark。description 要清楚覆蓋 Go API、handler、middleware、validation、response shaping、problem details、service/repository、auth、timeout、microservice refactor 等觸發情境。做完直接回報產物與結果。
```

## 壓最後一層的補刀句

如果對方還是想講流程，補這句：

```text
我現在不是要你教我怎麼做，我是要你把東西做出來。直接改檔、補檔、驗證、跑 benchmark，最後回報結果。
```

## 最低限度也要講清楚的四件事

如果你不想失敗，至少別漏這四個：

1. `skill 名稱`
2. `skill 路徑`
3. `觸發情境`
4. `要不要跑 quick_validate / evals / benchmark`

最差也要這樣下：

```text
用 skill-creator 幫我做一個 Go API skill，放在 /home/shihyu/.codex/skills。直接建立 skill folder、寫 SKILL.md、產生 agents/openai.yaml、補 references、跑 quick_validate.py、補 evals/evals.json、跑 benchmark。不要停在分析。
```
