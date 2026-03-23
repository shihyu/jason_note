# Skill Authoring Patterns

這份文件聚焦在「單一 skill 內文要怎麼寫才容易被正確路由、穩定執行、可長期維護」，補的是 lifecycle 之外的作者手法。

## 1) 先把 description 寫成 decision boundary

`description` 不是產品介紹，也不是能力炫耀。它是模型判斷「這個 skill 現在該不該載入」的邊界。

最低要求：
- 做什麼
- 何時用
- 何時不用
- 成功輸出是什麼

壞寫法：
- 這個 skill 可以幫你高品質完成各種報告與分析任務

較好的寫法：
- 在使用者要把提供的材料整理成管理層決策摘要時使用；若只是原文抽取、翻譯或自由腦暴則不要用。成功輸出是有固定段落、可直接拿去決策的 brief。

## 2) 一個 skill 只做一件主要工作

如果一個 skill 同時包：
- 蒐集資料
- 深度分析
- 正式寫作
- 排版成簡報
- 寄信或發布

通常就太寬了。判斷方式不是看「主題是否相同」，而是看：
- 輸入型態是否相同
- 核心步驟是否相同
- 驗收輸出是否相同
- 是否需要不同工具集

若差異很大，優先：
- 拆成多個 skill
- 或保留單一 primary job，再寫 handoff 規則

## 3) 步驟用祈使句，且每步要交代 I/O

不要只寫：
- 保持專業
- 做完整分析
- 注意使用者需求

請改寫成可執行步驟：
- 先讀取輸入材料與既有對話。
- 萃取 3-5 個可驗證主張。
- 刪除沒有證據支撐的結論。
- 依指定模板輸出。

每一步至少回答：
- Input：要讀什麼
- Action：要做什麼
- Output：要產出什麼
- Validation：怎麼知道這一步過關

## 4) 規則要分語意區塊

建議把長規則分成下列區塊，而不是全部塞在一段 prose 裡：

- `<role>`：角色與視角
- `<decision_boundary>`：何時用 / 不用 / 成功輸出
- `<workflow>`：步驟、分支、handoff
- `<output_contract>`：固定格式與完成定義
- `<tool_rules>`：何時用哪個工具、哪些工具不能亂用
- `<default_follow_through_policy>`：是否主動執行、何時先問
- `<examples>`：few-shot / worked examples
- `<model_notes>`：模型差異與 reasoning 策略

範例骨架：

```md
<role>
Act as a senior analyst writing for operations leaders.
</role>

<decision_boundary>
Use when:
- The user needs a structured incident review with evidence.
Do not use when:
- The user only wants raw log extraction or free-form brainstorming.
Inputs:
- incident timeline, logs, key questions
Successful output:
- a report with root cause, impact, mitigations, next steps
</decision_boundary>

<workflow>
Step 0: Read the provided timeline and logs.
- Input: notes, logs, prior discussion
- Output: key facts and missing evidence list

Step 1: Build the causal chain.
- Input: verified facts
- Output: root cause candidates with confidence labels
</workflow>

<output_contract>
Return exactly these sections in order:
1. Incident summary
2. Root cause
3. Evidence
4. Mitigations
5. Follow-up actions
</output_contract>
```

## 5) 把 output contract 寫死

當輸出格式很重要時，不要只寫「請條理清楚」。請直接定義：
- 段落順序
- 欄位名稱
- 格式類型（JSON / Markdown / SQL / CSV）
- 長度限制
- 可否加額外段落
- 缺資料時的回應方式

原則：
- 格式越嚴格，contract 越要明確
- 要求越鬆，越要說明可以自由調整到什麼程度

## 6) 範例與 few-shot 要跟 skill 走

當品質仰賴風格、結構或判準時，請把 worked examples 放進 skill，而不是全部塞到全域 prompt。

適合放 few-shot 的任務：
- 摘要
- 報告
- 文案改寫
- 分類標註
- 結構化轉換

寫法建議：
- 至少提供 1 個「理想輸出」範例
- 若容易踩坑，再補 1 個「常見失敗 vs 修正版」對照
- 範例應該接近真實任務，不要過度教科書化

## 7) 把「是否主動執行」寫成政策

不要讓模型自己猜要不要直接動手。

`<default_follow_through_policy>` 至少要定義三類：
- 直接做：低風險、可逆、無外部副作用
- 先問：會發送、刪除、寫正式環境、付款、對外發布
- 停止並回報：缺關鍵前置條件、狀態不一致、風險過高

若 skill 會調用工具，也要寫：
- 哪些工具是讀取型，可直接用
- 哪些工具是寫入型，需要明確同意
- 哪些結果必須先展示 diff / preview

## 8) tool schema 本身也是 routing signal

如果 skill 會包 function calling、MCP、API wrapper，請同時檢查：
- function 名稱是否一眼可懂
- 參數描述是否具體
- enum 是否把合法值寫死
- required 欄位是否完整
- active tool set 是否能縮到最小

常見壞味道：
- `run_task`, `execute`, `process_data` 這種過度泛化的名稱
- 參數只寫 `string`，沒有格式與例子
- 合法值有限卻不用 enum
- 一次暴露過多相似工具，導致模型選錯

## 9) 依模型類型調整寫法

不是每種模型都該用同一種 instruction density。

GPT 類模型通常更需要：
- 明確步驟
- 清楚動詞
- 具體格式限制

Reasoning 類模型通常更需要：
- 清楚目標
- 強約束
- 明確 output contract
- 適度的 reasoning effort

但不要把 reasoning 模型的每一步中間推理都寫死，否則常會浪費能力。

## 10) 長流程優先拆成多回合

若流程同時包含分析、查證、起草、格式化，優先拆成：
1. 分析任務與缺口
2. 蒐集資料或工具執行
3. 產生草稿
4. 做 QA 與格式化

更細的多回合設計見 `references/workflows.md`。

## 快速檢查表

- description 是否真的寫了「何時不用」
- 這個 skill 是否只有一個 primary job
- 每一步是否都有 input / output / validation
- 是否存在明確 `output contract`
- 是否提供 few-shot 或 worked example
- 是否寫了主動執行政策
- 若包工具，schema 是否具體且工具集夠小
- 若跨模型使用，是否有 model notes
