---
name: skill-creator-advanced
description: 當使用者要建立、改版、評估或發布可重複使用的 skill 時使用，例如命名、切 scope、補 output contract、設計 evals、檢查 registry readiness。若只是一次性 prompt、單純潤稿一段說明、或只需要實作單一 tool/function schema，則不要用；成功輸出應是可安裝、可測、邊界清楚的 skill 資產。
version: 2026.3.21
homepage: https://github.com/AllanYiin/skills/tree/main/skills/skill-creator-advanced
license: MIT
metadata: {"author":"Allan Yiin","language":"zh-TW","category":"ops","short-description":"Skill 建立、評估、benchmark 與打包迭代流程","openclaw":{"emoji":"🛠️"}}
---

# Skill Creator Advanced

此 skill 的目標是把「做 skill」變成可重複執行的工程流程，而不是一次性的 prompt 雜談。

它同時提供：
- 可操作的流程：從組合定位、命名、metadata、驗證、evals、benchmark、打包到迭代
- 可重用的腳本：初始化、格式檢查、驗證、測試計畫產生、workspace 準備、benchmark 彙整、regression gate 檢查、打包
- 可拆分的參考文件：把長內容放到 references/，維持 progressive disclosure
- 輕量 review viewer：把 with-skill / baseline 結果整理成可檢閱的 HTML

## 快速開始（你只要做一個新 skill）

1) 先從現有對話、repo、範例任務整理 2-3 個 use cases，不夠再補問。
2) 先確認它是否真的是「一個主要工作」；若同時包含研究、分析、寫作、發信、排版等多種交付物，先拆 skill 或定義 handoff。
3) 為每個 use case 寫 trigger 語句、必要輸入、成功輸出與 done looks like。
4) 建立 skill 資料夾：

```bash
python scripts/init_skill_advanced.py <skill-name> --path <output-dir>
```

5) 先決定這個 skill 是 `router`、`executor`、`ops` 還是 `utility`，再補完 `SKILL.md` 的決策邊界、`output contract`、`default follow-through policy`、few-shot 與 metadata surface。
6) 若 skill 會包工具、MCP 或 function calling，先檢查 tool/function 名稱、參數描述、enum 與 active tool set 是否足夠清楚。
7) 做格式、相容性與引用檢查：

```bash
python scripts/format_check.py <path/to/skill>
python scripts/quick_validate.py <path/to/skill>
python scripts/audit_openclaw_frontmatter.py
python scripts/audit_skill_references.py
```

8) 規劃真實測試案例，必要時產生測試計畫：

```bash
python scripts/generate_test_plan.py <path/to/skill> --out references/test_plan.md
```

9) 準備 eval workspace，讓 with-skill / baseline 能沿用固定目錄結構：

```bash
python scripts/prepare_eval_workspace.py <path/to/skill>
```

10) 打包成 `.skill`：

```bash
python scripts/package_skill.py <path/to/skill> <output-dir>
```

11) 若要優化 description 的觸發品質，另外準備 trigger eval set，再跑：

```bash
python scripts/run_eval.py --eval-set <path/to/trigger-evals.json> --skill-path <path/to/skill> --model <model-id>
python scripts/run_loop.py --eval-set <path/to/trigger-evals.json> --skill-path <path/to/skill> --model <model-id> --apply-best
```

## 操作方式

當使用者要建立或改版 skill 時，請用下列順序推進；可以跳步，但要明確說明原因。

1) Phase -1：Portfolio & competition
- 先做 portfolio architecture audit：判斷它是 `router`、`executor`、`ops` 還是 `utility`，不要在命名之前跳過 archetype。
- 先問清楚這個 skill 的 primary job 是什麼；一個 skill 預設只負責一件主要工作，避免同時承擔多種不相干的交付物。
- 列出上游與下游 handoff skill，確認它不會和既有 repo 自己打架。
- 再做 competitive positioning audit：列出 repo 內最相近的 3 個技能與 repo 外最相近的公開技能，說清楚它為什麼不會被取代。
- 若只是一次性流程、明顯被現有 skill 覆蓋，或其實應拆成多個 skill，直接指出不值得新增或應先重切 scope。

2) Phase 0：Task extraction
- 先看對話歷史、現有檔案、既有流程，再決定要不要追問。
- 用使用者熟悉的術語溝通；如果對方不熟技術名詞，不要把 jargon 當前提。

3) Phase 1：Use cases & boundaries
- 先拿到 2-3 個具體 use cases。
- 每個 use case 至少要有：trigger 語句、必要輸入、主要步驟、輸出、done looks like。
- 先定義 neighboring skills、negative triggers 與 handoff 規則，避免公開後互搶 query。
- 若 2-3 個 use cases 的輸入、步驟、輸出差異過大，優先拆 skill，而不是用一份超寬 description 硬包。
- 若規則來自事故復盤或踩坑心得，先抽出它依賴的條件：實體載體、受眾、工具鏈、輸入成熟度與失敗模式；不要把單次經驗直接寫成無條件真理。

4) Phase 2：Naming / description / metadata surface
- 先做 discoverability-first naming audit：檢查 slug 長度、slash command 長度、description 長度、trigger phrase、boundary 與內部名詞比例。
- `name` 優先服務 discoverability，不要把內部實作細節放進主名稱。
- `description` 要寫成 decision boundary，不要寫成能力介紹；固定回答：做什麼、何時用、何時不用、成功輸出是什麼。
- `description` 優先放真實 trigger phrases、場景、檔案類型與 deliverable 名稱；不要把 marketing 式優點當主要內容。
- `metadata`、`homepage`、`license`、OpenClaw 欄位與安裝敘事要一致，不能 repo 內部通過但公開頁面失真。

5) Phase 3：SKILL.md architecture
- 決定哪些內容要放 `scripts/`、`references/`、`assets/`。
- 核心流程留在 `SKILL.md`，細節與變體移到 `references/`。
- 優先寫會改變行為的指令，不要解釋模型本來就知道的常識。
- 步驟預設用祈使句撰寫，並明寫每一步的 input、action、output 與驗證點；不要只寫空泛原則。
- 內文優先分成語意區塊，例如 `<role>`、`<decision_boundary>`、`<workflow>`、`<output_contract>`、`<tool_rules>`、`<default_follow_through_policy>`、`<examples>`。
- `output contract` 要明訂段落順序、欄位、格式、長度、是否允許自由加段，以及「什麼算完成」。
- 當輸出品質依賴格式或風格時，把模板與 worked examples / few-shot 放進 skill 或 references，不要全部塞進 system prompt。
- `default follow-through policy` 要明寫：哪些低風險動作可直接做、哪些有外部副作用的行為必須先問、哪些情況要停止並回報。
- 把 postmortem 萃取出的規則寫成「條件 -> 預設動作 -> 例外 -> 驗證點」；凡是依賴投影環境、列印需求、既有 API 或狀態機的規則，都要把觸發條件寫明。

6) Phase 4：Compatibility / trust / install audit
- 先跑 `format_check.py` 與 `quick_validate.py` 修掉結構問題。
- 再跑 `audit_openclaw_frontmatter.py` 與 `audit_skill_references.py`，確認 frontmatter surface 與單獨打包後的本地路徑都可用。
- 抽查安裝、憑證、環境變數、持久化與權限敘事是否一致，避免公開頁的 trust signal 掉分。
- 把 `SKILL.md`、`scripts/`、`references/` 中提到的 binary、env、config path、install path、secret、persistence 行為都抽出來比對。
- 若 skill 依賴 tools / MCP / function calling，額外檢查 function 名稱、參數描述、enum、required 欄位與 active tool set；tool schema 本身也是 routing signal，不只是技術介面。

7) Phase 5：Trigger & overlap evals
- Triggering tests：應觸發、近義改寫、near-miss、不應觸發。
- Multilingual tests：至少考慮 `zh`、`en`、`mixed`、縮寫/俗稱。
- Skill overlap tests：列出容易混淆的鄰近 skill 與 negative triggers。
- 額外測同義改寫、錯誤競品、跨語言、縮寫、檔案型態詞與上下游 handoff。
- 測試用語要接近真實使用者會講的話，不要只測教科書式 prompt。
- 若 skill 內有「預設採用某種設計/工具路線」的規則，必測例外情境，例如高亮 LED 導致暗色可行、只有列印 handout、或工具不足必須停止；避免把預設值誤用成硬編碼。
- 最後輸出 `hit@1`、`hit@3`、`false positive` 與 neighbor confusion matrix。

8) Phase 6：Functional benchmark / ROI
- Functional tests：Given/When/Then，至少含 happy path、edge case、failure mode。
- 把核准過的測試 prompt 寫進 `assets/evals/evals.json`。
- 先建立 `<skill-name>-workspace/iteration-N/`，每個 eval 各自有 `with_skill/` 與 baseline 目錄。
- 若環境支援 subagents 或平行 workers，應在同一輪啟動 with-skill 與 baseline/old-skill；不支援時可序列執行，但保留相同目錄結構。
- 若 workflow 很長或包含不同性質的工作，優先拆成多回合或多階段：先分析缺口，再蒐集資料，再產出草稿，最後做 QA / 格式化；不要把所有要求壓成單一巨型 prompt。
- Performance comparison：和 baseline 比較輪次、tool calls、失敗率、結果品質。
- ROI comparison：確認提升是否值得額外的 token、時間與維護成本。
- 執行後用 `scripts/aggregate_benchmark.py` 彙整 benchmark，再用 `scripts/generate_review.py` 產生 review viewer。
- 用 `scripts/check_regression_gates.py` 檢查是否達到發版門檻。

9) Phase 7：Publish surface / registry readiness
- 用 `package_skill.py` 產生 `.skill`。
- 做 publish surface audit：檢查 README、GitHub About、topics、homepage、license、release notes、registry 說明是否一致。
- 分享時，README、安裝說明、release notes 應放在 skill folder 外。

10) Phase 8：Post-publish telemetry loop
- Under-trigger：補真實 trigger phrases、專有名詞、檔案類型。
- Over-trigger：加入 negative triggers、縮小範圍、移除模糊字眼。
- 執行不穩：補 validation、把脆弱步驟搬到 scripts。
- 內容過大：縮短 SKILL.md，把細節下放到 references。
- 迭代時優先收集具體失敗案例、使用率訊號與使用者回饋，不要只憑感覺改 wording。

完整細節見：
- `references/authoring-patterns.md`
- `references/lifecycle.md`
- `references/testing-playbook.md`
- `references/description-optimization.md`
- `references/eval-workflow.md`
- `references/eval-schemas.md`
- `references/multilingual-trigger-strategy.md`
- `references/skill-boundary-management.md`
- `references/regression-gates.md`
- `references/skill-roi-model.md`
- `references/distribution-playbook.md`
- `references/output-patterns.md`
- `references/workflows.md`
- `references/patterns-troubleshooting.md`

## 核心規則（請強制遵守）

1) **先把 description 寫對**
- 這是 skill 是否會被載入的主要因素。
- description 內要包含真實 trigger phrases、工作情境、必要時的檔案類型。
- description 至少要交代何時用、何時不用、成功輸出長什麼樣；不要只寫能力介紹。
- description 預設控制在 1-3 句，避免把完整產品說明塞進常駐 metadata surface。
- 優先讓明顯 query 穩定命中，再處理邊角案例；不要為了少數怪句子把 description 寫得過寬。

2) **先從上下文學會，再提最少的問題**
- 先讀對話、檔案與現有 skill。
- 只有在高風險假設會害結果偏掉時，才追問使用者。

3) **把脆弱步驟移到 scripts**
- 只要是重複、易出錯、或需要 deterministic 的檢查/轉換，就寫成腳本。

4) **避免 context 膨脹**
- `SKILL.md` 放流程與導航。
- 細節放 `references/`，必要時再讀。

5) **測試要真實，不要只測漂亮案例**
- 用接近實際對話的 prompt。
- 比較 baseline，確認 skill 真的有幫助，而不是只是多了一堆指令。

6) **with-skill 與 baseline 要用同一批 evals 比**
- 盡量同一輪啟動，避免時間與上下文條件差太多。
- 若是改版既有 skill，baseline 應是舊版 skill snapshot，而不是「完全不用 skill」。

7) **先處理 skill 邊界，再處理 wording**
- 若多個 skill 搶同一類 query，先做 overlap matrix 與 in-scope / out-of-scope。
- 不要只靠把 description 寫得更長來硬解衝突。

8) **公開相容性與信任訊號不能最後才補**
- frontmatter、homepage、license、安裝路徑、權限與憑證敘事必須在公開前就對齊。
- repo README、registry 描述與 skill metadata 若互相矛盾，應先停下來修正再發佈。

9) **ROI 不成立的 skill 不值得硬留**
- 若提升太小、成本太高、維護太重，要直接考慮縮 scope、拆 skill，或退回一般 prompt。

10) **不要在 skill folder 放 README.md**
- README 是給人看的，應放在 repo root 或其他 skill folder 外的位置。

11) **把事故心得寫成有條件的規則，不要寫成審美偏好**
- 規則至少要交代：什麼情境觸發、預設怎麼做、何時可以例外、怎麼驗證。
- 尤其是投影、列印、螢幕尺寸、既有模板、工具 API、狀態流這類會改變結果的環境因素，必須明寫，不能只留一句「通常比較好」。

12) **系統設計模式優先於臨時繞路**
- 若問題根因涉及工具鏈、狀態管理或既有 API，skill 應優先要求順應框架，而不是鼓勵直接改中間檔或臨時腳本硬繞。
- 需要繞路時，必須同時寫出風險、停止條件與回退方式。

## 內文品質與路由補強

1) **一個 skill 只做一件主要工作**
- 若 use cases 的輸入、工具、驗收產物明顯分裂，應拆 skill 或建立 handoff，而不是把 description 寫得越來越寬。

2) **步驟用祈使句，且每步要有 I/O**
- 每一步至少回答：要讀什麼、要做什麼、要輸出什麼、怎麼驗證。

3) **把 output contract 寫死**
- 指定段落順序、欄位、格式、長度、允許/禁止的自由度；若必須只輸出 JSON、Markdown、SQL 或固定欄位，直接明寫。

4) **few-shot / worked examples 要跟 skill 走**
- 對摘要、報告、轉換、分類、格式化這類任務，應把高品質範例放進 `SKILL.md` 或 `references/`，只在 skill 真正載入時使用。

5) **語意區塊要分清楚**
- 規則預設分成角色、路由、流程、格式、工具政策、主動執行政策與範例，不要把所有要求揉成一段說明文。

6) **主動執行邊界要明文化**
- 低風險、可逆、無外部副作用的動作可以直接做；刪除、付款、寄信、寫正式環境、對外發布等高風險行為，必須先取得明確同意。

7) **tool schema 也是 prompt**
- skill 若包工具，名稱、參數描述、enum 與 required 欄位都會直接影響 routing 與填參正確率；工具集太多時，應優先縮小 active tool set。

8) **長流程預設拆成多回合**
- 將分析、蒐集、起草、QA 拆開通常比單次巨型 prompt 更穩，尤其在多工具或高不確定任務。

9) **依模型類型調整寫法**
- GPT 類模型通常更吃明確步驟與精準指令；reasoning 類模型則更適合給清楚目標、強約束與 `output contract`，不要把中間推理寫死。

## 寫作與設計準則

- 用使用者懂的語言描述，不要預設對方知道你的內部名詞。
- 指令優先用明確動詞開頭，例如「先檢查」「若失敗就停止並回報」。
- 若步驟不是純線性流程，請明寫 decision tree、handoff 或多回合拆分點。
- 重要步驟要標註 input / output；沒有 I/O 的規則通常不夠可執行。
- 當某一步驟的理由能防止錯誤時，把理由寫出來；否則保持精簡。
- 技能不該偷偷改任務。若 workflow 需要做取捨，應明示取捨原則。
- 若某個任務其實不該做成 skill，要直接指出原因，而不是硬湊內容。
- 若規則依賴觀看距離、投影設備、列印需求或工具能力，直接把前提寫在規則裡，不要期待模型自己補完。

## 你可以用的腳本

- `scripts/init_skill_advanced.py`：建立帶測試/發布欄位的 SKILL.md 骨架。
- `scripts/format_check.py`：格式與結構檢查器（含 `--fix`）。
- `scripts/quick_validate.py`：最小合規驗證。
- `scripts/audit_openclaw_frontmatter.py`：檢查 OpenClaw frontmatter surface，例如單行 JSON `metadata`。
- `scripts/audit_skill_references.py`：檢查 `SKILL.md` 中引用的本地路徑在單獨打包後仍然存在。
- `scripts/check_skill_name_surface.py`：檢查 slug、slash command、description surface 與命名衝突風險。
- `scripts/audit_skill_overlap.py`：建立 overlap matrix，找出 repo 內互搶 query 的鄰近 skill。
- `scripts/audit_repo_discovery.py`：檢查 README、About、topics、代表 skills 與安裝入口是否一致。
- `scripts/generate_catalog.py`：輸出 repo 級 `catalog/skills.yaml`，整理 archetype、category、triggers 與 negative boundaries。
- `scripts/generate_test_plan.py`：產生測試計畫模板。
- `scripts/prepare_eval_workspace.py`：從 `assets/evals/evals.json` 建立 iteration workspace。
- `scripts/aggregate_benchmark.py`：彙整 with-skill / baseline run 結果，輸出 `benchmark.json` 與 `benchmark.md`。
- `scripts/check_regression_gates.py`：依 benchmark 與門檻設定判斷是否可發版。
- `scripts/run_eval.py`：跑 description trigger eval，輸出 query-level 與 run-level 診斷結果。
- `scripts/improve_description.py`：依 trigger eval 失敗型態重寫 description，保留 transcript。
- `scripts/run_loop.py`：把 eval 與 description 改寫串成多輪迭代，可選擇直接套用最佳 description。
- `scripts/generate_report.py`：產生 description optimization 的 HTML 報告。
- `scripts/utils.py`：共用的 `SKILL.md` / JSON 讀寫輔助。
- `scripts/package_skill.py`：驗證後打包成 `.skill`。

## 你可以用的 viewer / eval 結構

- `assets/evals/evals.json`：保存真實測試 prompt、預期輸出與 expectations。
- `assets/evals/regression_gates.json`：保存 benchmark 的發版門檻設定。
- `scripts/generate_review.py`：把 workspace 結果輸出成 review HTML。
- `<skill-name>-workspace/iteration-N/`：保存每輪 with-skill / baseline 的輸出、grading 與 benchmark。

## 常見交付物

交付給使用者時，通常包含：
- skill folder（`SKILL.md` + `scripts/` + `references/` + `assets/`）
- `assets/evals/evals.json`
- `<skill-name>-workspace/iteration-N/` 的 benchmark 與 review 輸出
- `.skill` 打包檔
- 放在 skill folder 外的 README、示例、release notes、安裝說明
