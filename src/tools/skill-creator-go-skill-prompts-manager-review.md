# skill-creator Go Skill 指揮稿（Manager Review 版）

這份文件是站在「主管審稿」視角寫的。
重點不是叫對方開始做，而是要求它交出可審、可驗、可退件的成果。

這份比 `boss` 版更嚴。
差別在於：
- 不是只要求執行，還要求交付品質
- 不是只要求跑驗證，還要求說明驗證結果
- 不是只要求補 evals，還要求 benchmark 有可讀結論
- 不達標就直接退回，不接受空泛回報

## 使用方式

直接貼下面任一段 prompt 給 Codex。

如果你只想先壓一句總命令，先用這句：

```text
照 /home/shihyu/skill-creator-go-skill-prompts-manager-review.md 執行。這是交付審查，不是討論題；交付不完整就直接視為未完成。
```

## 通用審稿總指令

每次交辦前，先把這段貼上：

```text
這次不是要你提供建議，是要你交付可審核成果。
不要只給分析、計畫、選項、草稿或方向。
直接建立檔案、補內容、跑驗證、整理結果。
先交最小可用版本，再補到可以過審。
缺資料先合理假設，不要因為細節不完整就停工。
quick_validate.py 必須跑。
能補 evals 就補。
能跑 benchmark 就跑。
如果過程失敗，先修再回報，不要把失敗過程當成成果。
最後回報時只接受：
- 產物路徑
- 驗證結果
- benchmark 結果
- 風險與待補項
任何只有方向沒有產物的回覆，一律視為未完成。
```

## 審稿標準

以下任何一項沒做到，都視為退件：

1. 沒有實際建立 skill folder
2. 沒有實際寫好 `SKILL.md`
3. 沒有產生 `agents/openai.yaml`
4. 沒有跑 `quick_validate.py`
5. 回報時沒有明確路徑
6. 只描述打算怎麼做，沒有實際修改檔案
7. 補了 evals 但沒說 benchmark 結果
8. description 寫得太空泛，無法判斷 trigger 情境
9. `references/` 或 `scripts/` 建了一堆沒用的垃圾內容
10. 建了 README、CHANGELOG、QUICK_REFERENCE 之類非必要文件

## 交付格式要求

交付時必須用這種格式回報：

```text
交付物：
- <skill 路徑>
- <重要檔案路徑>

驗證：
- quick_validate.py：pass / fail
- 如果 fail，修了什麼

評估：
- 是否補 evals：yes / no
- 是否跑 benchmark：yes / no
- skill 相對 baseline 的差異

風險：
- 還有哪些地方值得下一輪改進
```

如果沒有這種交付格式，直接要求它重報。

## 指令 1：Go API skill 交付任務

```text
用 skill-creator 幫我做一個 Go API skill。這是交付任務，不是討論；沒做完就不要回來。

交付要求如下：

1. 基本資訊
- skill 名稱：go-api-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- 處理 Go backend / HTTP API 的建立與重構
- 必須涵蓋 router、handler、middleware、request validation、response shaping、problem details、service/repository 邊界、auth、timeout、context 傳遞

3. 觸發情境
- 建立 Go API endpoint
- 重構 Go backend / microservice
- 修 handler / middleware / validation / response format
- 整理 service / repository 分層
- 修 auth / timeout / error handling / API consistency
- 使用者提到 chi、gin、echo、net/http、REST API、problem details、repository pattern 時要容易命中

4. 強制產出
- skill folder
- SKILL.md
- agents/openai.yaml
- 必要的 references/
- 只有在值得重用時才建立 scripts/

5. 文件要求
- SKILL.md frontmatter 只保留 name 和 description
- description 要能明確覆蓋這個 skill 做什麼、哪些情境要觸發
- body 要偏實戰與工程執行，不要寫成教材
- framework-specific 細節拆到 references，不要把 SKILL.md 塞滿
- 不要建立 README、CHANGELOG、QUICK_REFERENCE 等非必要檔案

6. 驗證要求
- 做完立刻跑 quick_validate.py
- 驗證失敗就修到過

7. 回報要求
- 用可審稿格式回報
- 如果你沒有實際建立檔案與跑驗證，就不要回報完成
```

## 指令 2：Go core skill 交付任務

```text
用 skill-creator 幫我做一個 Go core skill。不要交 Go 教學稿，交可以讓 Codex 真正執行工程決策的 skill。

交付要求如下：

1. 基本資訊
- skill 名稱：go-core-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- idiomatic Go
- package 設計
- cmd/internal/pkg 結構
- consumer-side interface
- dependency injection
- error handling
- context 傳遞
- goroutine/channel 協調
- 效能敏感邏輯

3. 觸發情境
- 寫 Go 程式
- 重構 Go 專案
- 整理 package 結構
- 修 interface 邊界
- 修 concurrency / context / error handling / performance 問題

4. 強制產出
- skill folder
- SKILL.md
- agents/openai.yaml
- 必要的 references/
- 視情況建立 scripts/

5. 驗證要求
- quick_validate.py 跑到過

6. 回報要求
- 用可審稿格式回報
- 說清楚 description 如何提高觸發率
- 說清楚 references 如何支撐真實重構工作
```

## 指令 3：Go testing skill 交付任務

```text
用 skill-creator 幫我做一個 Go testing skill，而且要做到可驗證。不要只交一個說明文件。

交付要求如下：

1. 基本資訊
- skill 名稱：go-testing-builder
- skill 路徑：/home/shihyu/.codex/skills

2. 任務範圍
- unit test
- table-driven tests
- subtests
- HTTP handler tests
- integration tests
- race detection
- benchmark
- fuzz
- coverage

3. 觸發情境
- 補測試
- 修 failing tests
- 補 benchmark / fuzz / race check
- 測 API / handler 行為

4. 強制產出
- skill folder
- SKILL.md
- agents/openai.yaml
- references/
- 值得重用才建立 scripts/

5. 驗證要求
- quick_validate.py 要過
- 補 3 個 realistic evals
- 跑一次 benchmark

6. 回報要求
- 用可審稿格式回報
- 額外說明 eval 設計理由與 benchmark 結論
```

## 指令 4：description 重寫審查

```text
用 skill-creator 幫我重寫這個 skill 的 description，目標是提高觸發率。不要只提建議，直接改檔，改完給我可審核結果。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

要求如下：

1. 直接修改 SKILL.md frontmatter 的 description
2. 新 description 必須明確覆蓋：
- Go API
- router / handler / middleware
- request validation
- response shaping / problem details
- service / repository 分層
- auth / timeout
- backend / microservice refactor
- API consistency / error handling / testability

3. description 必須做到：
- 清楚說明 skill 做什麼
- 清楚列出該觸發的任務
- 使用者沒講 skill 名稱時，仍可透過任務語義命中
- 不要變成 keyword dump

4. 驗證要求
- 跑 quick_validate.py

5. 回報要求
- 用可審稿格式回報
- 額外說明舊版 description 的弱點
- 說明這次如何補足 trigger coverage
```

## 指令 5：evals 與 benchmark 審查

```text
用 skill-creator 幫我補 evals，然後跑 benchmark。不要停在設計階段；我要的是結果，不是意圖。

skill 路徑：
- /home/shihyu/.codex/skills/go-api-builder

要求如下：

1. 設計 3 個 realistic eval prompts，至少包含：
- 新增 Go API endpoint
- 重構 handler/service/repository
- 修 validation、timeout、error response consistency

2. 把 evals 寫入：
- evals/evals.json

3. 每個 eval 都要補 assertions
- assertion 要客觀、可驗證
- 名稱要清楚
- 不要模糊

4. 執行 with-skill 與 baseline 比較
- 新 skill baseline 用 without_skill
- workspace 要按 iteration 結構整理

5. 產出：
- benchmark.json
- benchmark.md
- review viewer

6. 回報要求
- 用可審稿格式回報
- 額外說明：
  - 哪些地方 skill 贏 baseline
  - 哪些 assertions 沒有鑑別力
  - 哪些 eval 容易高變異
  - 下一輪最值得改的地方
```

## 指令 6：一步到位，做到可審查

```text
用 skill-creator 幫我從零做一個 Go API skill，並一路做到 benchmark。這是完整交付任務，不接受半成品。

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

6. 品質標準：
- SKILL.md 精簡但可執行
- description 要有足夠 trigger coverage
- references 要合理拆分
- 不要產生多餘文件

7. 回報要求：
- 用可審稿格式回報
- 若任何一項沒完成，明確列未完成項，不要包裝成完成
```

## 主管常用補刀句

如果對方還是想拖回分析模式，直接補這些：

```text
我不要方案，我要交付物。
沒有檔案路徑、沒有驗證結果、沒有 benchmark 結論，就不要回報完成。
如果你只是描述你準備怎麼做，這份回覆會直接退件。
先做出最小可用結果，再談下一步，不要反過來。
```

## 極短版

最短可用的一段：

```text
用 skill-creator 幫我做一個 Go API skill，放在 /home/shihyu/.codex/skills。這是交付審查，不是討論。直接建立 skill folder、寫 SKILL.md、產生 agents/openai.yaml、補 references、跑 quick_validate.py，並補 3 個 realistic evals 跑一次 benchmark。description 必須清楚覆蓋 Go API、handler、middleware、validation、response shaping、problem details、service/repository、auth、timeout、microservice refactor 等觸發情境。最後用可審稿格式回報；沒有產物、沒有驗證、沒有 benchmark，就視為未完成。
```

## 退件條款

碰到以下回覆，直接退件：

1. 「我建議先...」
2. 「以下是我的計畫...」
3. 「你可以考慮...」
4. 「我還沒建立檔案，但...」
5. 「我先幫你設計 prompt，之後再實作」
6. 沒有 skill 路徑
7. 沒有 quick_validate.py 結果
8. 沒有 benchmark 結果卻說已完成評估

## 最後一句

如果你懶得挑版本，直接貼這句：

```text
照 /home/shihyu/skill-creator-go-skill-prompts-manager-review.md 執行。這是交付審查，不是討論題。直接做出來，沒有產物、沒有驗證、沒有 benchmark，就不要回報完成。
```
